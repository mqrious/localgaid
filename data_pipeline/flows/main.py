import asyncio

from datetime import datetime

from prefect import runtime, flow, get_client
from prefect.flow_runs import pause_flow_run
from prefect.input import RunInput

from data_pipeline.flows.s01_crawl_websites import crawl_flow
from data_pipeline.flows.s02_make_audio_script import make_audio_script_flow
from data_pipeline.flows.s03_generate_audio_guides import generate_audio_guides_flow
from data_pipeline.flows.s04_update_production_database import update_production_database_flow


@flow(log_prints=True, name="audiogaid flow")
async def main(config_file_path: str,
               make_audio_script_prompt_path: str,
               bronze_output_dir: str,
               silver_output_dir: str,
               gold_output_dir: str,
               #    run_result_dir: str,
               bucket_name: str,
               parent_folder_name: str,
               database_block_name: str,
               aws_credentials_block_name: str,
               ):

    async with get_client() as client:
        name = config_file_path.rsplit("/", 1)[1].rsplit(".")[0]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        await client.update_flow_run(flow_run_id=runtime.flow_run.id, name=f"{name}_{ts}")

    s01_output_file_path = await crawl_flow(
        config_file_path=config_file_path,
        output_dir=bronze_output_dir,
        # run_result_dir=run_result_dir,
    )

    s02_output_file_path = make_audio_script_flow(
        prompt_template_path=make_audio_script_prompt_path,
        place_data_path=s01_output_file_path,
        output_dir=silver_output_dir,
        # run_result_dir=run_result_dir,
    )

    print("Generate the audio guide files? (Y/n): ")
    s02_confirmation = await pause_flow_run(wait_for_input=str)
    if s02_confirmation.lower() != "y":
        return

    s03_output_file_path = generate_audio_guides_flow(
        place_data_path=s02_output_file_path,
        output_dir=gold_output_dir,
        # run_result_dir=run_result_dir,
    )

    print("Update the production database? (Y/n): ")
    s03_confirmation = await pause_flow_run(wait_for_input=str)
    if s03_confirmation.lower() != "y":
        return

    update_production_database_flow(
        place_data_path=s03_output_file_path,
        bucket_name=bucket_name,
        parent_folder_name=parent_folder_name,
        database_block_name=database_block_name,
        aws_credentials_block_name=aws_credentials_block_name,
    )


if __name__ == "__main__":
    # TODO: check the directories before serving the deployment
    parameters = {
        "config_file_path": "",
        "bronze_output_dir": "/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/data_bronze",
        "silver_output_dir": "/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/data_silver",
        "gold_output_dir": "/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/data_gold",
        # "run_result_dir": "/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/run_results",
        "make_audio_script_prompt_path": "/Users/quanbm/Dev/sides/localgaid_notebooks/prompts/narration_2.jinja",
        "bucket_name": "localgaid-dev",
        "parent_folder_name": "audio-guides",
        "database_block_name": "supabase-localgaid-dev",
        "aws_credentials_block_name": "localgaid-aws-credentials"
    }

    parameters["config_file_path"] = "/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/place_configs/vungtau_dinhongnamhai.json"

    # asyncio.run(
    #     main(**parameters)
    # )

    main.serve(name="localgaid-data-pipeline-deployment",
               tags=["dev"],
               parameters=parameters,
               version="1.4")
