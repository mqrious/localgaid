import os
import json
from urllib.parse import urlparse
from prefect import flow, task


filter_keywords = ["Xanh SM", "Google Maps", "Xem thêm"]
max_desc_length = 20000


@task(log_prints=True)
def load_image_metadata(input_dir: str):
    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    print(f"Loaded {len(files)} metadata files.")
    return files


@task(log_prints=True)
def clean_up_images(metadata_file_path: str, output_dir: str):
    with open(metadata_file_path, "r") as file:
        data = json.loads(file.read())

    subfolder = metadata_file_path.rsplit(
        "/", 1)[1].rsplit(".", 1)[0]
    
    file_name = "images.json"

    cleaned_image_urls = []

    for origin in data:
        for url, images in origin.items():
            o = urlparse(url)
            hostname = f"{o.scheme}://{o.netloc}"
            for image in images:
                # Check the image desc
                image_desc = image["desc"]
                if len(image_desc) > max_desc_length:
                    continue
                if any(keyword in image_desc for keyword in filter_keywords):
                    continue

                # Check the image width: only take width=null
                if image["width"] != None:
                    continue

                # Clean the image src
                image_src = image["src"]
                if image_src.startswith("/"):
                    source = hostname + image_src
                else:
                    source = image_src
                cleaned_image_urls.append(source)

    output_file_path = os.path.join(output_dir, subfolder, file_name)
    with open(output_file_path, "w+") as file:
        file.write(json.dumps(cleaned_image_urls, indent=2))


@flow(log_prints=True)
def main(input_dir: str, output_dir):
    metadata_files = load_image_metadata(input_dir)

    for mf in metadata_files:
        mf_path = os.path.join(input_dir, mf)
        clean_up_images(mf_path, output_dir)


if __name__ == "__main__":
    main(
        input_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/data/bronze",
        output_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/data/gold"
    )
