import io
import os
import tempfile
import warnings

import torch
import whisper
from azure.storage.blob import BlobServiceClient
from promptflow.core import tool


class FileNotFoundException(Exception):
    """Custom exception for file not found."""

    def __init__(self, message: str):
        super().__init__(message)


def download_audio_from_blob(
    account_name: str, account_key: str, container_name: str, file_name: str
) -> bytes:
    """
    Downloads an audio file from Azure Blob Storage.

    Args:
        account_name (str): Azure Storage account name.
        account_key (str): Azure Storage account key.
        container_name (str): Name of the blob container.
        file_name (str): Name of the audio file in the container.

    Returns:
        bytes: The binary content of the audio file.
    """
    try:
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={account_name};"
            f"AccountKey={account_key};"
            f"EndpointSuffix=core.windows.net"
        )
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=file_name
        )

        return blob_client.download_blob().readall()

    except Exception as e:
        raise FileNotFoundException(
            f"Audio file '{file_name}' not found in container '{container_name}'."
        ) from e


@tool
def load_and_transcribe_audio(file_name: str, container_name: str) -> str:
    """
    Downloads an audio file from Azure Blob Storage, transcribes it using OpenAI Whisper (local),
    and returns the transcription text.

    Args:
        file_name (str): Name of the audio file in Azure Blob Storage.
        container_name (str): Name of the container where the audio file is stored.

    Returns:
        str: Transcribed text from the audio.
    """
    # Suppress known warning about FP16 not being supported on CPU
    warnings.filterwarnings(
        "ignore", message="FP16 is not supported on CPU; using FP32 instead"
    )

    # Load credentials
    account_name = os.getenv("BLOB_STORAGE_ACCOUNT_NAME")
    account_key = os.getenv("BLOB_STORAGE_ACCOUNT_KEY")

    if not account_name or not account_key:
        raise ValueError(
            "Missing Azure Blob Storage credentials in environment variables."
        )

    try:
        # Download audio bytes from blob
        audio_data = download_audio_from_blob(
            account_name, account_key, container_name, file_name
        )

        # Save to temporary file (Whisper requires a file path)
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as temp_audio:
            temp_audio.write(audio_data)
            temp_audio.flush()

            # Check for GPU availability
            device = "cuda" if torch.cuda.is_available() else "cpu"

            # Load Whisper model on appropriate device
            model_name = os.getenv("WHISPER_MODEL", "base")
            model = whisper.load_model(model_name, device=device)

            # Transcribe audio
            result = model.transcribe(temp_audio.name)

        return result["text"]

    except FileNotFoundException as fnfe:
        print(f"[ERROR] File Not Found: {fnfe}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error during transcription: {e}")
        raise
