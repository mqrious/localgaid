import os
import openai
from prefect import flow, task
from prefect.artifacts import create_link_artifact,  create_progress_artifact, update_progress_artifact
from typing import List


@task(log_prints=True)
def get_content_files(content_dir: str) -> List[str]:
    content_files = [f for f in os.listdir(content_dir) if f.endswith(".md")]

    print(f"Found {len(content_files)} files ready for narration.")
    return content_files


@task(log_prints=True)
def make_narration(prompt: str, result_file_path: str):
    client = openai.AzureOpenAI(
        api_version=os.environ.get("AOAI_API_VERSION"),
        azure_endpoint=os.environ.get("AOAI_ENDPOINT"),
    )
    completion = client.beta.chat.completions.parse(
        temperature=0.5,
        model=os.environ.get("AOAI_MODEL"),
        messages=[{"role": "user", "content": prompt}]
    )
    result = completion.choices[0].message.content

    with open(result_file_path, "w+") as f:
        f.write(result)
        print(f"Generated narration: {result_file_path}.")

    create_link_artifact(
        link=result_file_path,
        key="narration-script-result",
        description=result_file_path.rsplit("/")[1]
    )


@flow(log_prints=True)
def main(prompt_template_path: str, content_dir: str, output_dir: str):

    from jinja2 import Template
    prompt_content = open(prompt_template_path, "r").read()
    template = Template(prompt_content)

    content_files = get_content_files(content_dir=content_dir)

    progress_artifact_id = create_progress_artifact(
        progress=0.0,
        description="Indicates the progress of running narration tasks.")

    for i, confile in enumerate(content_files):
        content = open(os.path.join(content_dir, confile), "r").read()
        prompt = template.render(content=content)
        new_file_name = f"narration__{confile}"
        result_file_path = os.path.join(output_dir, new_file_name)

        make_narration(prompt, result_file_path)

        update_progress_artifact(artifact_id=progress_artifact_id,
                                 progress=i/len(content_files) * 100)


if __name__ == "__main__":
    main(
        prompt_template_path="/Users/quanbm/Dev/sides/localgaid_notebooks/prompts/narration_2.jinja",
        content_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/data/bronze",
        output_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/data/silver",
    )
