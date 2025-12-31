import base64
import json
import os
import tempfile
import uuid
import time

from unmeshed.sdk.common.delete_file_request import DeleteFileRequest
from unmeshed.sdk.common.download_file_base64_response import DownloadFileBase64Response
from unmeshed.sdk.common.download_file_request import DownloadFileRequest
from unmeshed.sdk.common.list_files_request import ListFilesRequest
from unmeshed.sdk.common.list_files_response import ListFilesResponse
from unmeshed.sdk.common.upload_file_response import UploadFileResponse
from unmeshed.sdk.configs.client_config import ClientConfig
from unmeshed.sdk.unmeshed_client import UnmeshedClient, logger

def get_client() -> UnmeshedClient:
    client_config = ClientConfig()
    client_config.set_base_url(os.getenv("UNMESHED_ENGINE_URL"))
    port = os.getenv("UNMESHED_PORT")
    client_config.set_client_id(os.getenv("UNMESHED_CLIENT_ID"))
    client_config.set_auth_token(os.getenv("UNMESHED_AUTH_TOKEN"))
    if port:
        client_config.set_port(int(port))
    client_config.set_enable_results_submission(False) ## Disable Polling
    return UnmeshedClient(client_config)

def view_files_tests(client : UnmeshedClient) -> None:
    list_files_request = ListFilesRequest(path="/") ## this should be any valid folder path
    list_files_response : ListFilesResponse = client.view_files(list_files_request)
    logger.info("Listing files and folder at / path : %s", list_files_response.to_json())


def upload_file(client: UnmeshedClient) -> None:
    sample_upload_name = f"sample_upload_{uuid.uuid4().hex}.json"
    sample_payload = {"message": "hello world", "timestamp": time.time()}
    tmp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            json.dump(sample_payload, tmp_file)
            tmp_file_path = tmp_file.name

        # Read and print the file contents
        with open(tmp_file_path, 'r') as f:
            file_contents = f.read()
            logger.info("Temporary file contents:\n%s", file_contents)

        # Upload the file
        upload_file_response: UploadFileResponse = client.upload_file(
            file_path=tmp_file_path,
            folder_path="/test-pysdk/folder1",
            custom_file_name=sample_upload_name
        )
        logger.info("Upload file response: %s", upload_file_response.to_json())
    except Exception as exc:
        logger.exception("Some exception occurred while uploading the file %s", exc)
    finally:
        if tmp_file_path and os.path.isfile(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except OSError:
                logger.warning("Failed to delete temp file %s", tmp_file_path)

def download_file(client : UnmeshedClient) -> None:
    file_name_to_download = f"sample_upload_{uuid.uuid4().hex}.json"
    download_file_request = DownloadFileRequest(path=f"/{file_name_to_download}") ## Must be valid file path
    download_bytes: bytes = client.download_file(download_file_request=download_file_request, http_read_timeout= 120)
    try:
        downloaded_payload = json.loads(download_bytes.decode("utf-8"))
        logger.info("Downloaded file: %s", downloaded_payload)
    except Exception as download_exc:
        logger.error("Failed to parse downloaded file: %s", download_exc)


def download_file_as_base64(client : UnmeshedClient) -> None:
    file_name_to_download = f"sample_upload_{uuid.uuid4().hex}.json"
    download_base64_response: DownloadFileBase64Response = client.download_file_base64(
        DownloadFileRequest(path=f"/app/files/{file_name_to_download}") ## Must be valid file path and must starts with /app/file/<file_or_folder-path>
    )
    if download_base64_response.contentBase64:
        decoded = json.loads(base64.b64decode(download_base64_response.contentBase64).decode("utf-8"))
        logger.info("Downloaded file base64: %s", decoded)


def delete_file_or_folder(client):
    file_name_to_delete = f"sample_upload_{uuid.uuid4().hex}.json"
    delete_response = client.delete_file(
        delete_file_request=DeleteFileRequest(path=f"/{file_name_to_delete}") ## This should be a valid file or folder path
    )
    logger.info("Delete response: %s", delete_response.to_json())

def main():
    client = get_client()

    upload_file(client)
    view_files_tests(client)
    download_file(client)
    download_file_as_base64(client)
    delete_file_or_folder(client)

if __name__ == "__main__":
    main()
