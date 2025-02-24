import asyncio
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict

from unmeshed.sdk.apis.workers.worker import Worker
from unmeshed.sdk.configs.client_config import ClientConfig
from unmeshed.sdk.decorators.worker_function import worker_function
from unmeshed.sdk.common.api_call_type import ApiCallType
from unmeshed.sdk.common.process_data import ProcessData
from unmeshed.sdk.common.process_request_data import ProcessRequestData
from unmeshed.sdk.common.process_search_request import ProcessSearchRequest
from unmeshed.sdk.unmeshed_client import UnmeshedClient
from unmeshed.sdk.utils.worker_scanner import logger


@dataclass
class SampleResponse:
    success: bool = False
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self) # type: ignore


@worker_function(name="worker3_alt", max_in_progress=500)
def task_hello_world1(input_dict: dict) -> dict:
    # print(f"Received input: {input_dict}")
    output_dict = {
        "message": "Hello, world!",
        "input_received": input_dict
    }
    return output_dict

def sample_function(input_dict: dict) -> dict:
    output_dict = {
        "message": "Hello, world! sample_function",
        "input_received": input_dict
    }
    return output_dict

async def sample_async_function(input_dict: dict) -> dict:
    output_dict = {
        "message": "Hello, world! sample_async_function",
        "input_received": input_dict
    }
    return output_dict


async def task_hello_world2(input_dict: dict) -> dict:
    output_dict = {
        "message": "Hello, world! task_hello_world2",
        "input_received": input_dict
    }
    return output_dict


def waiting_function(input_dict: dict) -> dict:
    time.sleep(0.2)
    output_dict = {
        "message": "Hello, world! waiting_function",
        "input_received": input_dict
    }
    return output_dict


async def async_waiting_function(input_dict: dict) -> dict:
    await asyncio.sleep(0.5)
    output_dict = {
        "message": "Hello, world! async waiting_function",
        "input_received": input_dict
    }
    return output_dict


@worker_function(name="list_no_test", max_in_progress=100, namespace="testns3", worker_queue_names=["res_list", "res_list2"])
def list_no_test(inp: dict) -> list:
    # Define a complex list with nested arrays and objects
    lst = [
        "23232",
        {
            "val": len(inp),
            "id": "1",
            "name": "Item 1",
            "tags": ["tag1", "tag2"],
            "details": {
                "description": "This is a description for item 1",
                "attributes": [100, 200, 300]
            }
        },
        {
            "id": "2",
            "name": "Item 2",
            "tags": ["tag3", "tag4"],
            "details": {
                "description": "This is a description for item 2",
                "attributes": [400, 500, 600]
            }
        },
        {
            "id": "3",
            "name": "Item 3",
            "tags": ["tag5", "tag6"],
            "details": {
                "description": "This is a description for item 3",
                "attributes": [700, 800, 900]
            }
        }
    ]
    return lst

@worker_function(name="sample_annotated_worker", max_in_progress=100, namespace="default", worker_queue_names=["sample_annotated_worker_name1", "sample_annotated_worker_name2"])
def sample_annotated_worker(response: SampleResponse) -> SampleResponse:
    print(f"Processing response: {response.to_dict()}")
    return SampleResponse(
        success=True,
        message="Sample Annotated Worker",
        data={
            "original_response": response.to_dict(),
            "worker_note": "Processed by sample_annotated_worker"
        }
    )

@worker_function(name="task_second_worker", max_in_progress=100, namespace="testns3", worker_queue_names=["task_second_worker"])
def task_second_worker(response: SampleResponse) -> SampleResponse:
    print(f"Processing response: {response.to_dict()}")
    return SampleResponse(
        success=True,
        message="Second worker processed",
        data={
            "original_response": response.to_dict(),
            "worker_note": "Processed by secondary worker"
        }
    )


class NotestWorkerCallable:
    def __init__(self):
        pass

    @worker_function(name="class_worker", max_in_progress=5, namespace="testns3")
    def class_worker(self, worker_input: dict) -> dict:
        print("Input received is " + str(worker_input))
        return {
            "a": "bcd"
        }


class CustomError(RuntimeError):
    def __init__(self, message, error_code, error_data):
        super().__init__(message)
        self.error_code = error_code
        self.error_data = error_data


# noinspection PyUnusedLocal
def exception_step(input_dict: dict) -> dict:
    """Raises a custom exception with sample error details"""
    raise CustomError(
        "Intentional exception from exception_step",
        error_code="CUSTOM_ERROR_123",
        error_data={"step": 2, "status": "failed"}
    )


def main():
    client_config = ClientConfig()
    client_config.set_base_url(os.getenv("UNMESHED_URL"))
    port = os.getenv("UNMESHED_PORT")
    client_config.set_client_id(os.getenv("UNMESHED_CLIENT_ID"))
    client_config.set_auth_token(os.getenv("UNMESHED_AUTH_TOKEN"))
    if port:
        client_config.set_port(int(port))
    client_config.set_initial_delay_millis(50)
    client_config.set_step_timeout_millis(3600000)
    client_config.set_work_request_batch_size(200)
    client_config.set_response_submit_batch_size(1000)
    client_config.set_max_threads_count(10)
    client_config.set_poll_interval_millis(10)

    client = UnmeshedClient(client_config)

    worker1: Worker = Worker(task_hello_world2, "worker3")
    worker1.max_in_progress = 3000
    client.register_worker(worker1)

    worker2: Worker = Worker(task_hello_world2, "worker4")
    worker2.max_in_progress = 1000
    client.register_worker(worker2)

    worker3: Worker = Worker(async_waiting_function, "waiting_worker")
    worker3.max_in_progress = 10000
    client.register_worker(worker3)

    client.register_worker(
        Worker(execution_method=exception_step, name="exception_step", namespace="testns3", max_in_progress=100))

    current_directory_full_path = os.getcwd()
    client.register_decorated_workers(current_directory_full_path)
    client.start()

    process_request: ProcessRequestData = ProcessRequestData("default", "test_process", 1, "req001", "corr001", {
        "test1": "value",
        "test2": 100,
        "test3": 100.0,
    })
    process_data1: ProcessData = client.run_process_sync(process_request)
    logger.info(
        f"Sync execution of process request %s returned %s",
        process_request,
        process_data1.to_json()
    )

    process_data2: ProcessData = client.run_process_async(process_request)
    logger.info(
        f"Async execution of process request %s returned %s",
        process_request,
        process_data2.to_json()
    )

    process_data1_retrieved1: ProcessData = client.get_process_data(process_data1.processId)
    logger.info(
        f"Retrieving process %s returned %s",
        process_data1.processId,
        process_data1_retrieved1.to_json()
    )

    logger.info("Since the flag to include steps was false the steps was not returned: %s", len(process_data1_retrieved1.stepRecords))


    process_data1_retrieved2: ProcessData = client.get_process_data(process_data1.processId, include_steps=True)
    logger.info(
        f"Retrieving process %s returned %s",
        process_data1.processId,
        process_data1_retrieved2.to_json()
    )

    logger.info("Since the flag to include steps was true the steps was returned: %s", len(process_data1_retrieved2.stepRecords))

    step_data1 = client.get_step_data(process_data1_retrieved2.steps[0].get("id"))
    logger.info(
        f"Retrieving step data %s returned %s",
        step_data1.processId,
        step_data1.to_json()
    )

    process_search_request: ProcessSearchRequest = ProcessSearchRequest()
    process_search_request.names = ["test_process"]
    process_search_request.limit = 20
    process_search_request.namespace = "default"
    processes_search_results_data: list['ProcessData'] = client.search_process_executions(process_search_request)
    logger.info(
        f"Search returned %s", len(processes_search_results_data)
    )

    rerun_process_data = client.rerun(process_id=process_data1.processId, version=1)
    logger.info(
        f"Rerun of process %s returned %s",
        process_data1.processId,
        rerun_process_data.to_json()
    )

    action_response = client.bulk_terminate(process_ids=[process_data1.processId, 1, 2])
    logger.info(
        f"Bulk terminate of 3 process %s returned %s",
        process_data1.processId,
        action_response.details
    )

    action_response = client.bulk_resume(process_ids=[process_data1.processId, 1, 2])
    logger.info(
        f"Bulk resume of 3 process %s returned %s",
        process_data1.processId,
        action_response.details
    )

    action_response = client.bulk_reviewed(process_ids=[process_data1.processId, 1, 2])
    logger.info(
        f"Bulk review of 3 process %s returned %s",
        process_data1.processId,
        action_response.details
    )

    response = client.invoke_api_mapping_get(endpoint="test_process_endpoint", correlation_id="correl_id--1", _id="req_id--1", api_call_type=ApiCallType.SYNC)
    logger.info(
        f"API mapped endpoint invocation using GET returned %s", response
    )

    response = client.invoke_api_mapping_post(endpoint="test_process_endpoint", correlation_id="correl_id--1", _id="req_id--1", api_call_type=ApiCallType.SYNC, _input={"test": "value"})
    logger.info(
        f"API mapped endpoint invocation using POST returned %s", response
    )


if __name__ == "__main__":
    main()
