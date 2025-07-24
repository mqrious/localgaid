import openai
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

client = openai.AzureOpenAI(
    api_version=os.environ.get("AOAI_API_VERSION"),
    azure_endpoint=os.environ.get("AOAI_ENDPOINT"),
)


def get_completion(messages: List[dict], temparature: float = 0.8):
    completion = client.beta.chat.completions.parse(
        temperature=temparature,
        model="lg-gpt-4o-mini",
        messages=messages
    )
    return completion
