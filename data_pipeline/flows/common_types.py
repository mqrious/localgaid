from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# PAGE DATA


class PlaceConfig(BaseModel):
    name: str
    location: str
    urls: List[str]


class PlaceDataBronze(BaseModel):
    name: str
    latitude: float
    longitude: float
    content: str
    images: List[str]


class PlaceDataSilver(PlaceDataBronze):
    script: str


class AudioGuide(BaseModel):
    title: str
    full_subtitle: str
    audio_url: str
    duration_seconds: int
    subtitle_url: str


class PlaceDataGold(PlaceDataSilver):
    audio_guides: List[AudioGuide]

    # Pydantic config type
    model_config = ConfigDict(arbitrary_types_allowed=True)

# RUN RESULTS


class BaseRunResult(BaseModel):
    id: str
    status: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]


class CrawlRunResult(BaseRunResult):
    input: str
    config: str
    output: Optional[str] = None
    urls_crawled: Optional[int] = None
    images_crawled: Optional[int] = None


class ScriptRunResult(BaseRunResult):
    input_prompt_path: str
    input_prompt: str
    input_place_data: str
    output: Optional[str] = None


class AudioRunResult(BaseRunResult):
    input_place_data: str
    output: Optional[str] = None
