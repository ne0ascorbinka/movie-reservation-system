from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def generate_azure_read_sas_url(blob_name: str, expiry_minutes: int = 60) -> str:
    """
    Generate a SAS URL for reading a blob from Azure Blob Storage.
    """
    now = datetime.now(timezone.utc)

    sas_token = generate_blob_sas(
        account_name=settings.AZURE_ACCOUNT_NAME,
        container_name=settings.AZURE_MEDIA_CONTAINER,
        blob_name=blob_name,
        account_key=settings.AZURE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        start=now - timedelta(minutes=5),
        expiry=now + timedelta(minutes=expiry_minutes)
    )

    encoded_blob = quote(blob_name, safe='')
    url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_MEDIA_CONTAINER}/{encoded_blob}?{sas_token}"

    return url