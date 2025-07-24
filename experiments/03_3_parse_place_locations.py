import os
import json
from prefect import flow, task


@task(log_prints=True)
def get_place_location_config_files(config_dir: str):
    config_files = [f for f in os.listdir(config_dir) if f.endswith(".json")]
    print(f"Loaded {len(config_files)} config files.")
    return config_files

@task(log_prints=True)
def create_location_data_file(config_file_path: str, output_dir: str):
    with open(config_file_path, "r") as f:
        data = json.loads(f.read())

    title = data["task_name"].replace(" ", "-")

