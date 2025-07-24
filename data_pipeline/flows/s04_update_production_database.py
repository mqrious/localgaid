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

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

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
                                  aws_credentials_block_name: str = "localgaid-aws-credentials",
                                  places_table_name: str = "localgaid-places",
                                  audio_guides_table_name: str = "localgaid-audio-guides"):
    # Load AWS credentials
    aws_credentials = AwsCredentials.load(aws_credentials_block_name)
    
    # Create DynamoDB resource
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=aws_credentials.aws_access_key_id,
        aws_secret_access_key=aws_credentials.aws_secret_access_key.get_secret_value(),
        region_name=aws_credentials.region_name or 'us-east-1'
    )
    
    places_table = dynamodb.Table(places_table_name)
    audio_guides_table = dynamodb.Table(audio_guides_table_name)
    
    # Generate a unique place ID based on name (you might want to use UUID instead)
    import hashlib
    place_id = hashlib.md5(place_data.name.encode()).hexdigest()
    
    # Upsert place data
    place_item = {
        'id': place_id,
        'name': place_data.name,
        'latitude': place_data.latitude,
        'longitude': place_data.longitude,
        'images': place_data.images,
        'tags': [],
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    try:
        places_table.put_item(Item=place_item)
        print(f"Upserted place '{place_data.name}' (ID={place_id}) into '{places_table_name}' table.")
    except ClientError as e:
        print(f"Error upserting place: {e}")
        raise
    
    # Prepare audio guides data
    audio_guides = [ag.model_dump() for ag in place_data.audio_guides]
    print("Audio guides to be upserted:")
    print(audio_guides)
    
    # Delete existing audio guides for this place
    try:
        # Query existing audio guides for this place
        response = audio_guides_table.query(
            IndexName='place-id-index',  # Assuming you have a GSI on place_id
            KeyConditionExpression=Key('place_id').eq(place_id)
        )
        
        # Delete existing audio guides
        for item in response['Items']:
            audio_guides_table.delete_item(
                Key={'id': item['id']}
            )
    except ClientError as e:
        print(f"Note: Could not delete existing audio guides (table might be new): {e}")
    
    # Insert new audio guides
    for i, ag in enumerate(audio_guides):
        audio_guide_id = f"{place_id}_{i}"
        audio_guide_item = {
            'id': audio_guide_id,
            'place_id': place_id,
            'title': ag['title'],
            'full_subtitle': ag['full_subtitle'],
            'audio_url': ag['audio_url'],
            'duration_seconds': ag['duration_seconds'],
            'subtitle_url': ag['subtitle_url'],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            audio_guides_table.put_item(Item=audio_guide_item)
        except ClientError as e:
            print(f"Error inserting audio guide {audio_guide_id}: {e}")
            raise
    
    print(f"Updated {len(audio_guides)} audio guides for '{place_data.name}' (ID={place_id}) into '{audio_guides_table_name}' table.")
    return place_id


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
                                    places_table_name: str = "localgaid-places",
                                    audio_guides_table_name: str = "localgaid-audio-guides",
                                    aws_credentials_block_name: str = "localgaid-aws-credentials"):
    run_id = str(
        runtime.flow_run.root_flow_run_id) if runtime.flow_run.root_flow_run_id is not None else str(runtime.flow_run.id)

    place_data = load_place_data(place_data_path=place_data_path)

    uploaded_audio_guides = put_objects_to_storage_task(audio_guides=place_data.audio_guides,
                                                        bucket_name=bucket_name,
                                                        folder_name=f"{parent_folder_name}/{run_id}",
                                                        aws_credentials_block_name=aws_credentials_block_name)

    place_data.audio_guides = uploaded_audio_guides

    place_id = upsert_to_database_table_task(place_data=place_data,
                                             aws_credentials_block_name=aws_credentials_block_name,
                                             places_table_name=places_table_name,
                                             audio_guides_table_name=audio_guides_table_name)
    
    print(f"Successfully processed place with ID: {place_id}")


if __name__ == "__main__":
    update_production_database_flow(
        place_data_path="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/data_gold/f759a403-1df2-4387-bf8e-da67a85c7a89/Dinh Ông Nam Hải.json",
        bucket_name="localgaid-dev",
        parent_folder_name="audio-guides",
        places_table_name="localgaid-places",
        audio_guides_table_name="localgaid-audio-guides",
        aws_credentials_block_name="localgaid-aws-credentials"
    )
