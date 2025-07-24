import asyncio
import json
import os
from datetime import datetime, timedelta

from prefect import flow, task
from prefect.artifacts import create_link_artifact,  create_progress_artifact, update_progress_artifact

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.content_filter_strategy import BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from pydantic import BaseModel
from pydantic_core import from_json
from typing import List, Optional


class CrawlerTaskConfig(BaseModel):
    task_name: str
    config_path: Optional[str] = None
    urls: List[str]
    output_dir: str


def load_crawler_log_file(logfile_path: str):
    with open(os.path.join(logfile_path), "r+") as logfile:
        log_content = logfile.read()
        if log_content == "":
            logs = {}
        else:
            logs = json.loads(log_content)
        logfile.close()

    return logs


def update_crawl_task_config_to_log_file(logfile_path: str, config_file_path: str):
    print(f"Updating '{config_file_path}' crawl time into logfile.")

    logs = load_crawler_log_file(logfile_path=logfile_path)
    logs[config_file_path] = str(datetime.now())

    with open(os.path.join(logfile_path), "w") as logfile:
        logfile.write(json.dumps(logs, indent=2))
        logfile.close()


@task(log_prints=True, name="Get crawler task config")
def get_crawler_task_configs(config_dir: str, logfile_path: str) -> List[str]:
    logs = load_crawler_log_file(logfile_path)

    print("Loaded logs:", logs)

    task_configs = []
    config_paths = [f for f in os.listdir(
        config_dir) if f.endswith(".json")]
    for config_file in config_paths:
        config_file_path = os.path.join(config_dir, config_file)

        if config_file_path in logs:
            print(f"Crawler task '{config_file}' found in log.")
            last_crawled = datetime.fromisoformat(logs[config_file_path])
            now = datetime.now()
            if now - last_crawled < timedelta(days=1):
                print(
                    f"Skipping '{config_file}'. Reason: last crawled in less than 1 day.")
                continue
        else:
            print(
                f"Crawler task '{config_file}' not found in log, added into task queue.")

        with open(config_file_path, "r") as file:
            task_config = CrawlerTaskConfig.model_validate(
                from_json(file.read(), allow_partial=True))
            task_config.config_path = config_file_path
        task_configs.append(task_config)

    print(f"Loaded {len(task_configs)}/{len(config_paths)} task configs.")
    return task_configs


@task(log_prints=True, name="Start crawler")
async def crawl(task_config: CrawlerTaskConfig,
                logfile_path: str,
                browser_cfg: BrowserConfig = None):

    instruction = """
Extract the main article content from this web page.
Only include text that is directly related to the main title of the article:
    - The main title
    - The main content
    - The image URLs related main content.
Do not include navigation menus, advertisements, sidebars, related articles, comments, or footer content.
Retain the content original language.
Return valid JSON.
""".strip()

    if task_config.task_name:
        instruction = f"This page is mainly about '{task_config.task_name}'.\n" + instruction
        instruction.strip()

    bm25_filter = BM25ContentFilter(
        user_query=task_config.task_name,
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

    from datetime import datetime
    now = datetime.now().strftime("%Y%m%d")
    file_name = f"{task_config.task_name.replace(" ", "-")}__{now}.md"
    image_metadata_file_name = f"{task_config.task_name.replace(" ", "-")}__{now}.json"
    output_file_path = os.path.join(task_config.output_dir, file_name)
    image_metadata_file_path = os.path.join(
        task_config.output_dir, image_metadata_file_name)

    images = []

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        progress_artifact_id = create_progress_artifact(
            progress=0.0,
            description="Indicates the progress of crawling data from the URLs.")
        for i, url in enumerate(task_config.urls):
            result = await crawler.arun(
                url=url,
                config=config,
            )

            images.append({
                url: result.media.get("images", [])
            })

            with open(output_file_path, "a+") as file:
                file.write(url)
                file.write(result.markdown.fit_markdown)
                file.write("\n\n")
                print(
                    f"Wrote content from '{url}' to '{output_file_path}': {len(result.markdown.fit_markdown)} characters")
            update_progress_artifact(
                artifact_id=progress_artifact_id, progress=i/len(task_config.urls) * 100)

        with open(image_metadata_file_path, "w+") as file:
            file.write(json.dumps(images, indent=2, ensure_ascii=True))
            print(
                f"Wrote {len(images)} images metadata for {task_config.task_name}.")

    update_crawl_task_config_to_log_file(
        logfile_path, task_config.config_path)

    create_link_artifact(
        key="crawl-result",
        link=output_file_path,
        description=f"Crawl result of '{task_config.task_name}' task",
    )


@flow(log_prints=True)
async def main(config_dir: str, logfile_path: str):
    task_configs = get_crawler_task_configs(config_dir, logfile_path)

    browser_cfg = BrowserConfig(headless=True)
    progress_artifact_id = create_progress_artifact(
        progress=0.0,
        description="Indicates the progress of running crawler tasks.")
    for i, task_config in enumerate(task_configs):
        await crawl(task_config=task_config, browser_cfg=browser_cfg, logfile_path=logfile_path)
        update_progress_artifact(
            artifact_id=progress_artifact_id, progress=i/len(task_configs) * 100)

if __name__ == "__main__":
    asyncio.run(main(
        config_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/crawler_task/configs/",
        logfile_path="/Users/quanbm/Dev/sides/localgaid_notebooks/crawler_task/logs/logs.json"))
