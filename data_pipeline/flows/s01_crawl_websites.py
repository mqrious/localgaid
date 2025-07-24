import asyncio
import os
from datetime import datetime, timezone
from urllib.parse import urlparse
from pydantic_core import from_json
from typing import List, Tuple

from prefect import runtime, flow, task, Flow
from prefect.artifacts import create_progress_artifact, update_progress_artifact, create_link_artifact
from prefect.client.schemas.objects import FlowRun
from prefect.states import State

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from common_types import PlaceConfig, PlaceDataBronze, CrawlRunResult


@task(log_prints=True, name="Load page config task")
def load_place_config(config_file_path: str) -> PlaceConfig:
    with open(config_file_path, "r") as file:
        place_config = PlaceConfig.model_validate(
            from_json(file.read(), allow_partial=True))

    print("Loaded place configs:", place_config)
    return place_config


@task(log_prints=True, name="Crawl task")
async def crawl(place_config: PlaceConfig,
                browser_cfg: BrowserConfig = None) -> Tuple[str, List[dict]]:

    bm25_filter = BM25ContentFilter(
        user_query=place_config.name,
        bm25_threshold=1.2,
    )

    md_generator = DefaultMarkdownGenerator(
        content_filter=bm25_filter,
        content_source="raw_html",
        options={
            "ignore_images": False
        })

    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_for="body",
        markdown_generator=md_generator,
        css_selector="body",
        excluded_selector="script, style",
        exclude_external_images=True,
        image_score_threshold=3,
        exclude_external_links=True,
        exclude_social_media_links=True,
    )

    if not browser_cfg:
        browser_cfg = BrowserConfig(headless=True)

    page_content = ""
    images = []

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        progress_artifact_id = create_progress_artifact(
            progress=0.0,
            description="Indicates the progress of crawling data from the URLs.")
        for i, url in enumerate(place_config.urls):
            result = await crawler.arun(
                url=url,
                config=config,
            )

            images.append({
                url: result.media.get("images", [])
            })

            page_content += f"""{url}
{result.markdown.fit_markdown}
\n\n
"""
            print(
                f"Crawled from '{url}': {len(result.markdown.fit_markdown)} characters")

            update_progress_artifact(
                artifact_id=progress_artifact_id, progress=i/len(place_config.urls) * 100)

    return page_content, images


@task(log_prints=True, name="Extract place location task")
def extract_place_location(page_config: PlaceConfig) -> Tuple[float, float]:
    parts = page_config.location.split(",")
    latitude = float(parts[0].strip())
    longitude = float(parts[1].strip())
    return latitude, longitude


@task(log_prints=True, name="Clean up images task")
def clean_up_images(image_dict: List[dict]) -> List[str]:
    max_desc_length = 10000

    cleaned_image_urls = []

    for origin in image_dict:
        for url, images in origin.items():
            o = urlparse(url)
            hostname = f"{o.scheme}://{o.netloc}"
            for image in images:
                # Check the image desc
                image_desc = image["desc"]
                if len(image_desc) > max_desc_length:
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
    return cleaned_image_urls


@task(log_prints=True, name="Compose and save result task")
def compose_place_data_and_save_result(name: str, page_content: str, images: List[str],
                                       latitude: float, longitude: float,
                                       output_dir: str, run_id: str = None) -> str:
    output_run_dir = os.path.join(output_dir, run_id)
    os.makedirs(output_run_dir, exist_ok=True)

    place_data = PlaceDataBronze(
        name=name,
        latitude=latitude,
        longitude=longitude,
        content=page_content,
        images=images,
    )

    output_file_path = os.path.join(output_run_dir, f"{name}.json")
    with open(output_file_path, "w+") as file:
        file.write(place_data.model_dump_json(indent=2))

    print("Run result (PlaceDataBronze):")
    print(place_data.model_dump_json(indent=2))
    print(f"Saved to {output_file_path}")

    create_link_artifact(
        key="s01-crawl-websites-output",
        link=output_file_path,
        description="Step 1 output"
    )

    return output_file_path


@flow(log_prints=True, name="Crawl flow")
async def crawl_flow(config_file_path: str, output_dir: str,
                     #  run_result_dir: str = None
                     ) -> Tuple[str, str, str, str]:
    browser_cfg = BrowserConfig(headless=True)

    run_id = str(
        runtime.flow_run.root_flow_run_id) if runtime.flow_run.root_flow_run_id is not None else str(runtime.flow_run.id)

    place_config = load_place_config(config_file_path=config_file_path)

    page_content, image_dict = await crawl(place_config=place_config, browser_cfg=browser_cfg)
    images = clean_up_images(image_dict=image_dict)
    latitude, longitude = extract_place_location(place_config)

    output_file_path = compose_place_data_and_save_result(
        name=place_config.name,
        page_content=page_content,
        images=images,
        latitude=latitude,
        longitude=longitude,
        output_dir=output_dir,
        run_id=run_id,
    )

    return output_file_path

    # return output_file_path, config_file_path, place_config.model_dump_json(), run_result_dir


# @crawl_flow.on_completion
# def handle_on_completion(flw: Flow, run: FlowRun, state: State):
#     end_time = str(datetime.now(timezone.utc))

#     output_file_path, config_file_path, place_config, run_result_dir = run.state.data.result

#     run_id = str(
#         runtime.flow_run.root_flow_run_id) if runtime.flow_run.root_flow_run_id is not None else str(runtime.flow_run.id)

#     cr_result = CrawlRunResult(
#         id=run_id,
#         input=config_file_path,
#         config=place_config,
#         status=run.state.name,
#         start_time=str(run.start_time),
#         end_time=end_time,
#         output=output_file_path
#     )

#     out_dir = os.path.join(run_result_dir, run_id)
#     os.makedirs(out_dir, exist_ok=True)

#     result_file_path = os.path.join(
#         out_dir, f"crawl_{run.start_time.strftime("%Y%m%d_%H%M%S")}__{run_id}.json")
#     with open(result_file_path, "w+") as file:
#         file.write(cr_result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(
        crawl_flow(
            config_file_path="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/place_configs/vungtau_bachdinh.json",
            output_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/data_bronze",
            # run_result_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/run_results",
        )
    )
