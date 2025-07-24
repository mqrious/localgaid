import asyncio
import os
import shutil
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from agents import Agent, Runner, ModelProvider, Model, OpenAIChatCompletionsModel, \
    RunConfig, ModelSettings, set_tracing_disabled, ItemHelpers
from agents.mcp import MCPServer, MCPServerStdio
from openai.types.responses import ResponseTextDeltaEvent

set_tracing_disabled(disabled=True)

load_dotenv()

print(os.environ.get("AOAI_API_VERSION"))
print(os.environ.get("AOAI_ENDPOINT"))
print(os.environ.get("AZURE_OPENAI_API_KEY"))

client = AsyncAzureOpenAI(
    api_version=os.environ.get("AOAI_API_VERSION"),
    azure_endpoint=os.environ.get("AOAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.environ.get("AOAI_DEPLOYMENT")
)

model_name = "lg-gpt-4o-mini"


class AzureOpenAIModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=client)


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to read the filesystem and answer questions based on those files.",
        mcp_servers=[mcp_server],
    )

    # List the files it can read
    message = "Please remove all the index number at the beginning of each file name."
    print(f"Running: {message}")

    run_config = RunConfig(model_provider=AzureOpenAIModelProvider(),
                           model_settings=ModelSettings(
                               temperature=0.8, max_tokens=1000),
                           )

    result = await Runner.run(starting_agent=agent, input=message,
                              run_config=run_config)
    print(result.final_output)

    # STREAMING
    # result = Runner.run_streamed(starting_agent=agent,
    #                              input=message,
    #                              run_config=run_config)

    # async for event in result.stream_events():
    #     print(event.type)
    # # We'll ignore the raw responses event deltas
    # if event.type == "raw_response_event":
    #     continue
    # # When the agent updates, print that
    # elif event.type == "agent_updated_stream_event":
    #     print(f"Agent updated: {event.new_agent.name}")
    #     continue
    # # When items are generated, print them
    # elif event.type == "run_item_stream_event":
    #     if event.item.type == "tool_call_item":
    #         print("-- Tool was called")
    #     elif event.item.type == "tool_call_output_item":
    #         print(f"-- Tool output: {event.item.output}")
    #     elif event.item.type == "message_output_item":
    #         print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
    #     else:
    #         pass  # Ignore other event types

    print("=== Run complete ===")


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "data")
    print(samples_dir)

    async with MCPServerStdio(
            name="Filesystem Server, via npx",
            params={
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    samples_dir],
            },
    ) as server:
        await run(server)


if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError(
            "npx is not installed. Please install it with `npm install -g npx`.")

    asyncio.run(main())

# Các model có thể sử dụng: llama3.2:3b
# Các model sử dụng không tốt: qwen3:0.6b
