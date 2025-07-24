import os
import io
import time
from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel
from pydantic_core import from_json

from prefect import runtime, flow, task, Flow
from prefect.client.schemas.objects import FlowRun
from prefect.states import State
from prefect_aws import AwsCredentials, S3Bucket

from supabase_block import SupabaseCredentials
from supabase import create_client, Client

from common_types import PlaceDataGold, AudioGuide


@task(log_prints=True, name="Load place data (gold) task")
def load_place_data(place_data_path: str) -> PlaceDataGold:
    with open(place_data_path, "r") as file:
        place_data = PlaceDataGold.model_validate(
            from_json(file.read(), allow_partial=True)
        )
    print("Loaded place data (gold):", place_data)
    return place_data


@task(log_prints=True, name="Upsert to database table task")
def upsert_to_database_table_task(place_data: PlaceDataGold,
                                  database_block_name: str = "supabase-localgaid-dev"):
    credentials = SupabaseCredentials.load(database_block_name)

    supabase: Client = create_client(
        supabase_url=credentials.url, supabase_key=credentials.key.get_secret_value())

    supabase.rpc(
        "upsert_place", {
            "p_name": place_data.name,
            "p_tags": [],
            "p_latitude": place_data.latitude,
            "p_longitude": place_data.longitude,
            "p_images": place_data.images
        }).execute()

    place = (
        supabase.table("places")
        .select("id")
        .eq("name", place_data.name)
        .single()
        .execute()
    )
    print(
        f"Upserted place '{place_data.name}'(ID={place.data["id"]}) into 'places' table.")

    audio_guides = [ag.model_dump() for ag in place_data.audio_guides]

    print("Audio guides to be upsert:")
    print(audio_guides)

    supabase.rpc("update_audio_guides",
                 {
                     "p_place_id": place.data["id"],
                     "audio_guides": audio_guides
                 }).execute()
    print(
        f"Updated {len(audio_guides)} audio guides for '{place_data.name}'(ID={place.data["id"]}) into 'audio_guides' table.")
    return


@task(log_prints=True, name="Put objects to storage task")
def put_objects_to_storage_task(audio_guides: List[AudioGuide], bucket_name: str,
                                folder_name: str,
                                aws_credentials_block_name: str = "localgaid-aws-credentials") -> List[AudioGuide]:
    uploaded_audio_guides: List[AudioGuide] = []

    aws_credentials = AwsCredentials.load(aws_credentials_block_name)
    s3_bucket = S3Bucket(
        bucket_name=bucket_name,
        credentials=aws_credentials
    )

    for ag in audio_guides:
        s3_audio_path = s3_bucket.upload_from_path(from_path=ag.audio_url,
                                                   to_path=os.path.join(folder_name, ag.audio_url.rsplit("/", 1)[1]))
        s3_subtitle_path = s3_bucket.upload_from_path(from_path=ag.subtitle_url,
                                                      to_path=os.path.join(folder_name, ag.subtitle_url.rsplit("/", 1)[1]))

        uploaded_audio_guides.append(
            AudioGuide(
                title=ag.title,
                full_subtitle=ag.full_subtitle,
                duration_seconds=ag.duration_seconds,
                audio_url=s3_audio_path,
                subtitle_url=s3_subtitle_path
            )
        )
        print(f"Uploaded audio to {s3_audio_path}")
        print(f"Uploaded subititle to {s3_subtitle_path}")
    return uploaded_audio_guides


@flow(log_prints=True, name="Update production database flow")
def update_production_database_flow(place_data_path: str,
                                    bucket_name: str = "localgaid-dev",
                                    parent_folder_name: str = "audio-guides",
                                    database_block_name: str = "supabase-localgaid-dev",
                                    aws_credentials_block_name: str = "localgaid-aws-credentials"):
    run_id = str(
        runtime.flow_run.root_flow_run_id) if runtime.flow_run.root_flow_run_id is not None else str(runtime.flow_run.id)

    place_data = load_place_data(place_data_path=place_data_path)

    uploaded_audio_guides = put_objects_to_storage_task(audio_guides=place_data.audio_guides,
                                                        bucket_name=bucket_name,
                                                        folder_name=f"{parent_folder_name}/{run_id}",
                                                        aws_credentials_block_name=aws_credentials_block_name)

    place_data.audio_guides = uploaded_audio_guides

    upsert_to_database_table_task(place_data=place_data,
                                  database_block_name=database_block_name)


if __name__ == "__main__":
    update_production_database_flow(
        place_data_path="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/data_gold/f759a403-1df2-4387-bf8e-da67a85c7a89/Dinh Ông Nam Hải.json",
        bucket_name="localgaid-dev",
        parent_folder_name="audio-guides",
        database_block_name="supabase-localgaid-dev",
        aws_credentials_block_name="localgaid-aws-credentials"
    )
