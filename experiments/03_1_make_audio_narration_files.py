import os
import edge_tts
import time
from prefect import flow, task
from typing import List, Tuple
from pydantic import BaseModel
from prefect.artifacts import create_link_artifact,  create_progress_artifact, update_progress_artifact


class AudioNarrationItem(BaseModel):
    number: int
    title: str
    content: str


@task(log_prints=True, name="Get narration script files")
def get_narration_script_files(narration_script_dir: str) -> List[str]:
    files = [f for f in os.listdir(narration_script_dir) if f.endswith(".md")]
    print(f"Loaded {len(files)} scripts file ready to generate audios.")
    return files


@task(log_prints=True, name="Pre-process script")
def preprocess_script(script_file_path: str) -> Tuple[List[AudioNarrationItem], str]:
    script_file_name = script_file_path.rsplit("/", 1)[1].rsplit(".", 1)[0]
    text = open(script_file_path, "r").read()

    sections = [s for s in text.split("#") if s.strip() != ""]

    items = []

    for i, section in enumerate(sections):
        title = section.split("\n", 1)[0].strip()
        content = section.split("\n", 1)[1].strip()
        items.append(AudioNarrationItem(
            number=i+1, title=title, content=content))
    return items, script_file_name


@task(log_prints=True, name="Generate audio")
def generate_audio(audio_narration_item: AudioNarrationItem, script_file_name: str, output_dir: str):
    number = f"{audio_narration_item.number:02d}"
    title = audio_narration_item.title.replace(" ", "-")
    text = audio_narration_item.content
    voice = "vi-VN-NamMinhNeural"

    outfolder = script_file_name.split("__", 1)[1]
    final_output_dir = os.path.join(output_dir, outfolder, "audio_guides")

    os.makedirs(final_output_dir, exist_ok=True)

    outaudio_name = os.path.join(final_output_dir, f"{number}_{title}.mp3")
    outsrt_name = os.path.join(final_output_dir, f"{number}_{title}.srt")

    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()

    with open(outaudio_name, "wb") as file:
        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    with open(outsrt_name, "w", encoding="utf-8") as file:
        file.write(submaker.get_srt())

    print(f"Generated '{outaudio_name}' with subtitles '{outsrt_name}'.")

    time.sleep(5)


@flow(log_prints=True, name="Generate narration audio flow")
def main(narration_script_dir: str, output_dir: str):
    script_files = get_narration_script_files(narration_script_dir)

    progress_artifact_id = create_progress_artifact(
        progress=0.0,
        description="Indicates the progress of generating narrtion audios.")

    for i, script_file in enumerate(script_files):
        audio_narration_items, script_file_name = preprocess_script(
            script_file_path=os.path.join(narration_script_dir, script_file))

        for item in audio_narration_items:
            generate_audio(item, script_file_name, output_dir)

        print(f"Finished generating narration audios for '{script_file}'")

        update_progress_artifact(artifact_id=progress_artifact_id,
                                 progress=i/len(script_files) * 100)


if __name__ == "__main__":
    main(
        narration_script_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/data/silver",
        output_dir="/Users/quanbm/Dev/sides/localgaid_notebooks/data/gold",
    )
