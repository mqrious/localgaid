import os
import io
import edge_tts
import time

from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel
from pydantic_core import from_json

from prefect import runtime, flow, task, Flow
from prefect.client.schemas.objects import FlowRun
from prefect.states import State
from prefect.artifacts import create_link_artifact

from common_types import PlaceDataSilver, PlaceDataGold, AudioRunResult, AudioGuide


class AudioScriptSection(BaseModel):
    number: int
    title: str
    content: str


@task(log_prints=True, name="Load place data (silver) task")
def load_place_data(place_data_path: str) -> PlaceDataSilver:
    with open(place_data_path, "r") as file:
        place_data = PlaceDataSilver.model_validate(
            from_json(file.read(), allow_partial=True)
        )
    print("Loaded place data (silver):", place_data)
    return place_data


@task(log_prints=True, name="Pre-process script task")
def preprocess_script(script: str) -> List[AudioScriptSection]:
    text_sections = [s for s in script.split("#") if s.strip() != ""]
    sections = []
    for i, section in enumerate(text_sections):
        title = section.split("\n", 1)[0].strip()
        content = section.split("\n", 1)[1].strip()
        sections.append(AudioScriptSection(
            number=i+1, title=title, content=content))
    print(f"Preprocessed script, got {len(sections)} sections:", sections)
    return sections


@task(log_prints=True, name="Generate audio task")
def generate_audio_files_and_subtitles(sections: List[AudioScriptSection]) -> dict:
    audio_data = {}

    for section in sections:
        number = f"{section.number:02d}"
        title = section.title.replace(" ", "-")
        text = section.content
        voice = "vi-VN-NamMinhNeural"

        print(
            f"Generating audio for section {number} ({title}) with '{voice}' voice.")

        file_name = f"{number}_{title}"

        communicate = edge_tts.Communicate(text, voice)
        submaker = edge_tts.SubMaker()

        audio_file = io.BytesIO()

        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

        audio_data[file_name] = {
            "title": section.title,
            "full_subtitle": text,
            "file": audio_file,
            "subtitle": submaker.get_srt(),
        }
        time.sleep(5)

    return audio_data


@task(log_prints=True, name="Compose and save result task")
def compose_place_data_and_save_result(place_data_silver: PlaceDataSilver, audio_data: dict,
                                       output_dir: str, run_id: str):
    output_run_dir = os.path.join(output_dir, run_id)
    os.makedirs(output_run_dir, exist_ok=True)

    audio_guides = []

    for audio_file_name, data in audio_data.items():
        audio_file_path = os.path.join(
            output_run_dir, audio_file_name + ".mp3")
        subtitle_file_path = os.path.join(
            output_run_dir, audio_file_name + ".srt")

        with open(audio_file_path, "wb+") as file:
            file.write(data["file"].getvalue())
        print(f"Created audio file at '{audio_file_path}'")
        with open(subtitle_file_path, "w+") as file:
            file.write(data["subtitle"])
        print(f"Created subtitle file at '{subtitle_file_path}'")

        from mutagen.mp3 import MP3
        duration_seconds = int(MP3(audio_file_path).info.length)

        audio_guides.append(AudioGuide(
            title=data["title"],
            full_subtitle=data["full_subtitle"],
            audio_url=audio_file_path,
            duration_seconds=duration_seconds,
            subtitle_url=subtitle_file_path,
        ))

    place_data = PlaceDataGold(
        **place_data_silver.model_dump(),
        audio_guides=audio_guides,
    )

    output_file_path = os.path.join(output_run_dir, f"{place_data.name}.json")
    with open(output_file_path, "w+") as file:
        file.write(place_data.model_dump_json(indent=2))

    print("Run result (PlaceDataGold):")
    print(place_data.model_dump_json(indent=2))
    print(f"Saved to {output_file_path}")

    create_link_artifact(
        key="s03-generate-audio-guides-output",
        link=output_file_path,
        description="Step 3 output"
    )

    return output_file_path


@flow(log_prints=True, name="Generate narration audio flow")
def generate_audio_guides_flow(place_data_path: str, output_dir: str,
                               #    run_result_dir: str = None
                               ):
    run_id = str(
        runtime.flow_run.root_flow_run_id) if runtime.flow_run.root_flow_run_id is not None else str(runtime.flow_run.id)

    place_data = load_place_data(place_data_path)

    sections = preprocess_script(place_data.script)

    audio_data = generate_audio_files_and_subtitles(sections)

    output_file_path = compose_place_data_and_save_result(place_data_silver=place_data,
                                                          audio_data=audio_data,
                                                          output_dir=output_dir,
                                                          run_id=run_id)

    return output_file_path

    # return output_file_path, place_data.model_dump_json(), run_result_dir


# @generate_audio_guides_flow.on_completion
# def handle_on_completion(flw: Flow, run: FlowRun, state: State):
#     end_time = str(datetime.now(timezone.utc))

#     output_file_path, place_data, run_result_dir = run.state.data.result

#     run_id = str(
#         runtime.flow_run.root_flow_run_id) if runtime.flow_run.root_flow_run_id is not None else str(runtime.flow_run.id)

#     cr_result = AudioRunResult(
#         id=run_id,
#         status=run.state.name,
#         start_time=str(run.start_time),
#         end_time=end_time,
#         input_place_data=place_data,
#         output=output_file_path
#     )

#     out_dir = os.path.join(run_result_dir, run_id)
#     os.makedirs(out_dir, exist_ok=True)

#     result_file_path = os.path.join(
#         out_dir, f"audio_{run.start_time.strftime("%Y%m%d_%H%M%S")}__{run_id}.json")
#     with open(result_file_path, "w+") as file:
#         file.write(cr_result.model_dump_json(indent=2))


if __name__ == "__main__":
    generate_audio_guides_flow(
        place_data_path="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/data_silver/d87e4ee6-c5ff-41af-b351-c7f3b14577cb/Bạch Dinh.json",
        output_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/data_gold",
        # run_result_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/run_data/run_results",
    )
