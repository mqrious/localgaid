import os
import openai

from prefect import runtime, flow, task, Flow
from prefect.client.schemas.objects import FlowRun
from prefect.states import State
from prefect.artifacts import create_markdown_artifact, create_link_artifact

from datetime import datetime, timezone
from typing import List
from jinja2 import Template
from pydantic_core import from_json

from common_types import PlaceDataBronze, PlaceDataSilver, ScriptRunResult


@task(log_prints=True, name="Load prompt template task")
def load_prompt_template(prompt_template_path: str) -> Template:
    prompt_content = open(prompt_template_path, "r").read()
    template = Template(prompt_content)
    return template


@task(log_prints=True, name="Load place data (bronze) task")
def load_place_data(place_data_path: str) -> PlaceDataBronze:
    with open(place_data_path, "r") as file:
        place_data = PlaceDataBronze.model_validate(
            from_json(file.read(), allow_partial=True)
        )
    print("Loaded place data (bronze):", place_data)
    return place_data


@task(log_prints=True, name="Generate script task")
def generate_script(prompt: str) -> str:
    client = openai.AzureOpenAI(
        api_version=os.environ.get("AOAI_API_VERSION"),
        azure_endpoint=os.environ.get("AOAI_ENDPOINT"),
    )
    completion = client.beta.chat.completions.parse(
        temperature=0.2,
        model=os.environ.get("AOAI_MODEL"),
        messages=[{"role": "user", "content": prompt}]
    )
    result = completion.choices[0].message.content

    print(f"Generated audio script: {result}.")
    return result


@task(log_prints=True, name="Compose and save result task")
def compose_place_data_and_save_result(place_data_bronze: PlaceDataBronze, script: str,
                                       output_dir: str, run_id: str = None):
    output_run_dir = os.path.join(output_dir, run_id)
    os.makedirs(output_run_dir, exist_ok=True)

    place_data = PlaceDataSilver(
        **place_data_bronze.model_dump(),
        script=script
    )

    output_file_path = os.path.join(output_run_dir, f"{place_data.name}.json")
    with open(output_file_path, "w+") as file:
        file.write(place_data.model_dump_json(indent=2))

    create_markdown_artifact(
        key="audio-guide-script",
        markdown=place_data.script,
        description=place_data.name,
    )

    print("Run result (PlaceDataSilver):")
    print(place_data.model_dump_json(indent=2))
    print(f"Saved to {output_file_path}")

    create_link_artifact(
        key="s02-make-audio-script-output",
        link=output_file_path,
        description="Step 2 output"
    )

    return output_file_path


@flow(log_prints=True, name="Make audio script flow")
def make_audio_script_flow(prompt_template_path: str, place_data_path: str, output_dir: str,
                           #    run_result_dir: str = None
                           ):
    run_id = str(
        runtime.flow_run.root_flow_run_id) if runtime.flow_run.root_flow_run_id is not None else str(runtime.flow_run.id)

    place_data_bronze = load_place_data(place_data_path)
    template = load_prompt_template(prompt_template_path)
    prompt = template.render(content=place_data_bronze.content)
    script = generate_script(prompt)

    output_file_path = compose_place_data_and_save_result(place_data_bronze=place_data_bronze,
                                                          script=script,
                                                          output_dir=output_dir,
                                                          run_id=run_id)

    return output_file_path
    # return output_file_path, prompt_template_path, prompt, place_data_bronze.model_dump_json(), run_result_dir


# @make_audio_script_flow.on_completion
# def handle_on_completion(flw: Flow, run: FlowRun, state: State):
#     end_time = str(datetime.now(timezone.utc))

#     output_file_path, prompt_template_path, prompt, place_data_bronze, run_result_dir = run.state.data.result

#     run_id = str(
#         runtime.flow_run.root_flow_run_id) if runtime.flow_run.root_flow_run_id is not None else str(runtime.flow_run.id)

#     cr_result = ScriptRunResult(
#         id=run_id,
#         input_prompt_path=prompt_template_path,
#         input_prompt=prompt,
#         input_place_data=place_data_bronze,
#         status=run.state.name,
#         start_time=str(run.start_time),
#         end_time=end_time,
#         output=output_file_path
#     )

#     out_dir = os.path.join(run_result_dir, run_id)
#     os.makedirs(out_dir, exist_ok=True)

#     result_file_path = os.path.join(
#         out_dir, f"script_{run.start_time.strftime("%Y%m%d_%H%M%S")}__{run_id}.json")
#     with open(result_file_path, "w+") as file:
#         file.write(cr_result.model_dump_json(indent=2))


if __name__ == "__main__":
    make_audio_script_flow(
        prompt_template_path="/Users/quanbm/Dev/sides/localgaid_notebooks/prompts/narration_2.jinja",
        place_data_path="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/data_bronze/8c0c7045-03ce-43a2-91b5-9bdc8695cf2f/Bạch Dinh.json",
        output_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/data_silver",
        # run_result_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/run_results",
    )
