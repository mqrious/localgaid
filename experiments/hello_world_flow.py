import json

from prefect import flow, Flow
from prefect.client.schemas.objects import TaskRun, FlowRun
from prefect.states import State


@flow(log_prints=True)
def main(name: str):
    return f"Hello {name}!", name

@main.on_completion
def on_main_completion(flw: Flow, run: FlowRun, state: State):
    print(flw)
    # print(run.model_dump_json())
    # print(run.state.data.result)

    result, arg = run.state.data.result
    print(result)
    print(arg)

if __name__ == "__main__":
    main("Bob")