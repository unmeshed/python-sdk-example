# Unmeshed Python SDK - Example

This README is a clone of the Unmeshed Python SDK project - and it has the details of how to use the SDK and more.


# Unmeshed Python SDK


This README will guide you on how to set up Unmeshed credentials, run workers, and get started with the Unmeshed platform. Read more about Unmeshed on [unmeshed.io](https://unmeshed.io/).

## About Unmeshed

Unmeshed is a ⚡ fast, low-latency orchestration platform that enables you to build 🛠️, run 🏃, and scale 📈 API and microservices orchestration, scheduled jobs ⏰, and more with ease. Learn more on our [🌍 main website](https://unmeshed.io) or explore the [📖 documentation overview](https://unmeshed.io/docs/concepts/overview).

Unmeshed is built by the ex-founders of Netflix Conductor. This next-gen platform is blazing fast and supports a wider range of use cases.

---

## Installing the Unmeshed SDK

To use Unmeshed in your Python project, install the SDK using pip:

```bash
pip install unmeshed-sdk
```

---

## Setting Up Unmeshed Credentials

To use the Unmeshed SDK in your Python application, initialize the `UnmeshedClient` with your credentials:

```python
from unmeshed.sdk.configs.client_config import ClientConfig
from unmeshed.sdk.unmeshed_client import UnmeshedClient

def main():
    client_config = ClientConfig()
    client_config.set_client_id("your-client-id")  # Replace with your API 🆔 client ID
    client_config.set_auth_token("your-auth-token")  # Replace with your API 🔒 auth token
    client_config.set_port(8080)  # Replace with your Unmeshed API port 🚪
    client_config.set_base_url("http://localhost")  # Replace with your Unmeshed API endpoint 🌐
    client_config.set_initial_delay_millis(50)
    client_config.set_step_timeout_millis(3600000)
    client_config.set_work_request_batch_size(200)
    client_config.set_response_submit_batch_size(1000)
    client_config.set_max_threads_count(10)
    client_config.set_poll_interval_millis(10)

    client = UnmeshedClient(client_config)
```

---

## Running a Worker using Regular Functions

A worker in Unmeshed is simply a Python function that gets mapped to a step in a process execution. When a step with a matching name is reached in a process execution, the corresponding worker function is invoked with the step’s input.

### Step 1: Define Worker Functions

We support both synchronous and asynchronous worker functions:

```python
def sample_function(input_dict: dict) -> dict:
    return {
        "message": "Hello, world! sample_function",
        "input_received": input_dict
    }

import asyncio

async def sample_async_function(input_dict: dict) -> dict:
    return {
        "message": "Hello, world! sample_async_function",
        "input_received": input_dict
    }
```

### Step 2: Register the Worker

Workers are registered using `client.register_worker()`. The `name` parameter is the correlation between the process step and the function, meaning when a step with this name is reached during process execution, the function is invoked with the step's input.

```python
from unmeshed.sdk.apis.workers.worker import Worker

client.register_worker(
    Worker(execution_method=sample_async_function, name="sample_async_function", namespace="default", max_in_progress=100)
)

client.register_worker(
    Worker(execution_method=sample_function, name="sample_function", namespace="default", max_in_progress=100)
)
```

This ensures that when a step named `sample_function` or `sample_async_function` is executed in a process, the respective function is called.

### Step 3: Start Your Application

Once registered, workers automatically listen for incoming tasks. To start the worker listening, use the following command:

```python
client.start()
```

Run your Python application, and Unmeshed will take care of the execution flow.

---

## Running Workers with Annotation

Unmeshed also supports registering worker functions using annotations. This provides a more declarative way to define workers.

```python
from unmeshed.sdk.decorators.worker_function import worker_function

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
```

### Using `worker_queue_names`

The `worker_queue_names` parameter allows a single worker function to be associated with multiple worker queue names. If this parameter is provided, it will take precedence over the `name` parameter, meaning that the worker function will be invoked for any of the specified queue names.

This feature applies to both regular function-based workers and annotation-based workers, allowing flexible mapping of process steps to worker functions.

---

## APIs Supported in the SDK

### Running a Process Synchronously

You can run a process synchronously using the `run_process_sync` method:

```python
from unmeshed.sdk.common.process_data import ProcessData
from unmeshed.sdk.common.process_request_data import ProcessRequestData

process_request = ProcessRequestData(
    namespace="default",
    name="test_process",
    version=1,
    requestId="req001",
    correlationId="corr001",
    input={
        "test1": "value",
        "test2": 100,
        "test3": 100.0,
    }
)

process_data = client.run_process_sync(process_request)
```

This API executes a process synchronously and returns the result immediately after execution.

---

### Running a Process Asynchronously

You can run a process asynchronously using the `run_process_async` method:

```python
process_data2 = client.run_process_async(process_request)
logger.info(
    f"Async execution of process request %s returned %s",
    process_request,
    process_data2.to_json()
)
```

Unlike the synchronous version, this API triggers the process execution but does not wait for it to complete. This is useful for triggering long-running workflows where an immediate response is not required.

---

### Process Request Data Structure

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class ProcessRequestData(JSONSerializable):
    namespace: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    version: Optional[int] = field(default=None)
    requestId: Optional[str] = field(default=None)
    correlationId: Optional[str] = field(default=None)
    input: Optional[Dict[str, Any]] = field(default=None)
```

#### Explanation of Inputs:
- **namespace**: The namespace under which the process is defined.
- **name**: The name of the process to be executed.
- **version**: The version of the process definition to use.
- **requestId**: A unique identifier for the process request.
- **correlationId**: A unique identifier used to correlate related process executions.
- **input**: A dictionary containing key-value pairs representing input parameters for the process.

These APIs allow executing workflows either synchronously (waiting for completion) or asynchronously (triggering without waiting).


## Unmeshed Python SDK

This README will guide you through the usage of the Unmeshed Python SDK, including how to execute processes, retrieve process data, and integrate with the Unmeshed orchestration platform.

## APIs Supported in the SDK

### Running a Process Synchronously

You can run a process synchronously using the `run_process_sync` method:

```python
from unmeshed.sdk.common.process_data import ProcessData
from unmeshed.sdk.common.process_request_data import ProcessRequestData

process_request = ProcessRequestData(
    namespace="default",
    name="test_process",
    version=1,
    requestId="req001",
    correlationId="corr001",
    input={
        "test1": "value",
        "test2": 100,
        "test3": 100.0,
    }
)

process_data = client.run_process_sync(process_request)
```

This API executes a process synchronously and returns the result immediately after execution.

---

### Running a Process Asynchronously

You can run a process asynchronously using the `run_process_async` method:

```python
process_data2 = client.run_process_async(process_request)
logger.info(
    f"Async execution of process request %s returned %s",
    process_request,
    process_data2.to_json()
)
```

Unlike the synchronous version, this API triggers the process execution but does not wait for it to complete. This is useful for triggering long-running workflows where an immediate response is not required.

---

### Retrieving a Previously Executed Process

You can retrieve the details of a previously executed process using the `get_process_data` method:

```python
process_data_retrieved1 = client.get_process_data(process_data.processId)
logger.info(
    f"Retrieving process %s returned %s",
    process_data.processId,
    process_data_retrieved1.to_json()
)

# Since the flag to include steps was false, steps were not returned
logger.info("Since the flag to include steps was false, the steps were not returned: %s", len(process_data_retrieved1.stepRecords))

process_data_retrieved2 = client.get_process_data(process_data.processId, include_steps=True)
logger.info(
    f"Retrieving process %s with steps returned %s",
    process_data.processId,
    process_data_retrieved2.to_json()
)
```

By default, the retrieved process data does not include step details. If step details are required, set `include_steps=True` when calling `get_process_data`.

---

### Process Request Data Structure

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class ProcessRequestData(JSONSerializable):
    namespace: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    version: Optional[int] = field(default=None)
    requestId: Optional[str] = field(default=None)
    correlationId: Optional[str] = field(default=None)
    input: Optional[Dict[str, Any]] = field(default=None)
```

#### Explanation of Inputs:
- **namespace**: The namespace under which the process is defined.
- **name**: The name of the process to be executed.
- **version**: The version of the process definition to use.
- **requestId**: A unique identifier for the process request.
- **correlationId**: A unique identifier used to correlate related process executions.
- **input**: A dictionary containing key-value pairs representing input parameters for the process.

These APIs allow executing workflows either synchronously (waiting for completion), asynchronously (triggering without waiting), or retrieving process execution details.


### Retrieving a Previously Executed Process

You can retrieve the details of a previously executed process using the `get_process_data` method:

```python
process_data_retrieved1 = client.get_process_data(process_data.processId)
logger.info(
    f"Retrieving process %s returned %s",
    process_data.processId,
    process_data_retrieved1.to_json()
)

# Since the flag to include steps was false, steps were not returned
logger.info("Since the flag to include steps was false, the steps were not returned: %s", len(process_data_retrieved1.stepRecords))

process_data_retrieved2 = client.get_process_data(process_data.processId, include_steps=True)
logger.info(
    f"Retrieving process %s with steps returned %s",
    process_data.processId,
    process_data_retrieved2.to_json()
)


logger.info("Since the flag to include steps was true the steps was returned: %s", len(process_data1_retrieved2.stepRecords))
```

By default, the retrieved process data does not include step details. If step details are required, set `include_steps=True` when calling `get_process_data`.



### Retrieving Step Data

You can retrieve details of a specific step within a previously executed process using the get_step_data method:

```python
step_data1 = client.get_step_data(process_data_retrieved2.steps[0].get("id"))
logger.info(
    f"Retrieving step data %s returned %s",
    step_data1.processId,
    step_data1.to_json()
)
```

This API allows fetching details of a specific step in a process execution, which can be useful for debugging or tracking execution flow.


### Searching for Process Executions

You can search for processes using the `search_process_executions` method:

```python
process_search_request = ProcessSearchRequest()
process_search_request.names = ["test_process"]
process_search_request.limit = 20
process_search_request.namespace = "default"

processes_search_results_data = client.search_process_executions(process_search_request)
logger.info(
    f"Search returned %s", len(processes_search_results_data)
)
```

This API allows searching for processes based on various filters such as names, namespace, process types, statuses, and trigger types.

### Process Search Request Structure

```python
from dataclasses import dataclass, field
from typing import Optional, List
import time

@dataclass
class ProcessSearchRequest(JSONSerializable):
    startTimeEpoch: int = field(default_factory=lambda: int(time.time() * 1000) - (60 * 1000 * 60 * 24))
    endTimeEpoch: Optional[int] = field(default=None)
    namespace: Optional[str] = field(default=None)
    processTypes: Optional[List[ProcessType]] = field(default=None)
    triggerTypes: Optional[List[ProcessTriggerType]] = field(default=None)
    names: Optional[List[str]] = field(default=None)
    processIds: Optional[List[int]] = field(default=None)
    correlationIds: Optional[List[str]] = field(default=None)
    requestIds: Optional[List[str]] = field(default=None)
    statuses: Optional[List[ProcessStatus]] = field(default=None)
    limit: int = 10
    offset: int = 0
```

### Explanation of Search Parameters:
- **startTimeEpoch**: Start time in milliseconds (defaults to 24 hours ago).
- **endTimeEpoch**: Optional end time in milliseconds.
- **namespace**: The namespace to filter processes.
- **processTypes**: Optional list of process types to filter.
- **triggerTypes**: Optional list of trigger types to filter.
- **names**: List of process names to search for.
- **processIds**: List of specific process IDs.
- **correlationIds**: List of correlation IDs to match.
- **requestIds**: List of request IDs to match.
- **statuses**: List of process statuses to filter.
- **limit**: The number of results to return (default is 10).
- **offset**: The starting point for paginated results.

This API provides flexible options for retrieving processes based on various search criteria.




### Rerunning a Process

You can rerun a previously executed process using the `rerun` method:

```python
rerun_process_data = client.rerun(process_id=process_data1.processId, version=1)
logger.info(
    f"Rerun of process %s returned %s",
    process_data1.processId,
    rerun_process_data.to_json()
)
```

This API allows rerunning a completed or failed process with the specified version.

---

### Bulk Termination of Processes

You can terminate multiple processes in bulk using the `bulk_terminate` method:

```python
action_response = client.bulk_terminate(process_ids=[process_data1.processId, 1, 2])
logger.info(
    f"Bulk terminate of 3 processes %s returned %s",
    process_data1.processId,
    action_response.details
)
```

This API is useful for stopping multiple running processes at once. In this example we are requesting termination of process_data1.processId, 1 and 2.

---

### Bulk Resumption of Processes

You can resume multiple failed or stopped processes using the `bulk_resume` method:

```python
action_response = client.bulk_resume(process_ids=[process_data1.processId, 1, 2])
logger.info(
    f"Bulk resume of 3 processes %s returned %s",
    process_data1.processId,
    action_response.details
)
```

This API is helpful when recovering multiple processes that were previously in a failed state or terminated state.

---

### Bulk Marking Processes as Reviewed

You can mark multiple processes as reviewed using the `bulk_reviewed` method:

```python
action_response = client.bulk_reviewed(process_ids=[process_data1.processId, 1, 2])
logger.info(
    f"Bulk review of 3 processes %s returned %s",
    process_data1.processId,
    action_response.details
)
```

This API is useful for marking failed or terminated processes as reviewed.

---

### Invoking API Mappings

You can invoke an API mapping using either a GET or POST request.

#### GET API Mapping Invocation

```python
response = client.invoke_api_mapping_get(endpoint="test_process_endpoint", correlation_id="correl_id--1", _id="req_id--1", api_call_type=ApiCallType.SYNC)
logger.info(
    f"API mapped endpoint invocation using GET returned %s", response
)
```

This API calls a mapped endpoint using GET and returns the response.

#### POST API Mapping Invocation

```python
response = client.invoke_api_mapping_post(endpoint="test_process_endpoint", correlation_id="correl_id--1", _id="req_id--1", api_call_type=ApiCallType.SYNC, _input={"test": "value"})
logger.info(
    f"API mapped endpoint invocation using POST returned %s", response
)
```

This API calls a mapped endpoint using POST with input payload and returns the response.

---

# Scaling Worker

If you are running a large workload using the **Unmeshed SDK**, it’s important to understand how it handles concurrency and in-progress tasks:

> **Available tasks** = **Max In Progress** – **Currently In Progress**

Where:
- **Currently In Progress** refers to tasks that have already been polled but not yet submitted back to the server with a final result.

---

## Why is my **Max In Progress** setting not having the desired effect?

1. **Check if your work is asynchronous**  
   - If your code is **asynchronous** but contains blocking operations, it will limit concurrency.  
   - If your code is **synchronous**, the SDK can only handle concurrent tasks up to the number of threads available in its thread pool.

2. **Thread Pool Limits**  
   - The polled work is submitted to the SDK’s internal thread pool (controlled by `max_threads_count`).  
   - If this thread pool is fully occupied, additional work remains in a memory queue until threads become available.  
   - To achieve a higher concurrency, either **increase your thread pool** or **use non-blocking asynchronous methods**.

3. **For Long-Running or I/O-Heavy Work**  
   - If you have a very large `max_in_progress` but still see limited concurrency, likely the thread pool or blocking code is the bottleneck.  
   - Asynchronous approaches can better utilize CPU resources for I/O-heavy tasks.

4. **Short-Running Processes**  
   - If your tasks finish quickly, you may not need a large thread pool. Increasing `max_in_progress` may be sufficient.  

---

## Additional Tuning Options

- **`response_submit_batch_size`**  
  The number of completed tasks submitted in a batch back to the server.

- **`poll_interval_millis`**  
  The gap (in milliseconds) between poll requests. A single poll request is made for all registered workers, so keeping this value low is generally safe.  

By adjusting these parameters—along with ensuring your code is either effectively asynchronous or has an appropriately sized thread pool—you can achieve higher scalability and throughput with the Unmeshed SDK.

> **Tip**: You can always run multiple worker instances to scale up even further.

By adjusting these parameters—along with ensuring your code is either effectively asynchronous or has an appropriately sized thread pool—you can achieve higher scalability and throughput with the Unmeshed SDK.


Visit us at [Unmeshed](https://unmeshed.io/)
