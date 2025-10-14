import os

from unmeshed.sdk.apis.steps.steps_client import StepClient
from unmeshed.sdk.common.process_definition import ProcessDefinition
from unmeshed.sdk.common.step_definition import StepDefinition
from unmeshed.sdk.common.unmeshed_constants import ProcessType, StepType
from unmeshed.sdk.configs.client_config import ClientConfig
from unmeshed.sdk.unmeshed_client import UnmeshedClient
from unmeshed.sdk.utils.worker_scanner import logger


def main():
    os.environ["DISABLE_SUBMIT_CLIENT"] = "true"
    client_config = ClientConfig()
    client_config.set_client_id(os.getenv("UNEMSHED_CLIENT_ID"))
    client_config.set_auth_token(os.getenv("UNMESHED_AUTH_TOKEN"))
    client_config.set_port(8080)
    client_config.set_base_url(os.getenv("UNMESHED_SERVER_URL"))
    client_config.set_initial_delay_millis(50)
    client_config.set_step_timeout_millis(3600000)
    client_config.set_work_request_batch_size(200)
    client_config.set_response_submit_batch_size(1000)
    client_config.set_max_threads_count(10)
    client_config.set_poll_interval_millis(10)

    client = UnmeshedClient(client_config)

    ### Get Default Template for Step Type
    noop1_step = StepClient.get_default_step_definition_template(stepType=StepType.NOOP, namespace="default")

    noop2_step = StepDefinition(
        name="noop2",
        ref="noop2",
        description="Test noop 2",
        type=StepType.NOOP,
        input= {"key1": "val1"}
    )

    noop3_step = StepDefinition(
        name="noop3",
        ref="noop3",
        description="Test noop 3",
        type=StepType.NOOP,
        input={"key1": "val1"}
    )

    process_definition = ProcessDefinition(
        name="test-process",
        version=1,
        namespace="default",
        description="Testing Process",
        type=ProcessType.API_ORCHESTRATION,
        steps=[noop1_step, noop2_step]
    )

    pd_created : ProcessDefinition = client.create_new_process_definition(process_definition)
    logger.info(
        f"Created process definition :%s",
        pd_created
    )

    process_definition = ProcessDefinition(
        name="test-process",
        version=2,
        namespace="default",
        description="Testing Process",
        type=ProcessType.API_ORCHESTRATION,
        steps=[noop1_step, noop2_step, noop3_step]
    )
    new_version_added : ProcessDefinition = client.update_process_definition(process_definition)
    logger.info(
        f"Updated process definition :%s",
        new_version_added
    )


    latest_or_specific_pd: ProcessDefinition = client.get_process_definition_latest_or_version(
        namespace="default", name="test-process", version=None)
    logger.info(
        f"Latest test-process definition :%s",
        latest_or_specific_pd
    )

    versions = client.get_process_definition_versions(namespace="default", name="test-process")
    logger.info(
        f"Fetched Process definition versions :%s",
        versions
    )


    all_process_definitions: list[ProcessDefinition] = client.get_all_process_definitions()
    logger.info(
        f"Fetched All Process definitions :%s",
        all_process_definitions
    )

    # Filter only test-process definitions
    test_process_definitions = [
        pd for pd in all_process_definitions
        if pd.name == "test-process" and pd.namespace == "default"
    ]

    logger.info(
        f"Filtered test-process definitions: %s",
        test_process_definitions
    )

    if test_process_definitions:
        deleted_process_definitions_response = client.delete_process_definitions(
            process_definitions=test_process_definitions,
            version_only=False
        )
        logger.info(
            f"Deleted process definitions response: %s",
            deleted_process_definitions_response
        )
    else:
        logger.info("No test-process definitions found to delete")


if __name__ == "__main__":
    main()