import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContentSettings
import mimetypes

load_dotenv(override=True)

class AzureStorageClient:
    """
    Azure Blob Storage Client with Safe Fallback for Local/Dev.
    """
    def __init__(self) -> None:
        # FORCE MOCK: User confirmed Azure deletion
        print("FORCING MOCK STORAGE: Azure Resources Deleted.")
        self.blob_service_client = None
        return

    def upload_file(self, file_or_bytes, filename: str, tenant_id: str) -> str:
        """
        Uploads to Azure if configured, else returns a Mock URL.
        """
        if not self.blob_service_client:
            print(f"MOCK: Uploading {filename} for tenant {tenant_id}")
            return f"https://mock-storage.local/{tenant_id}/{filename}"

        # Generate blob name (folder structure: tenant_id/filename)
        blob_name = f"{tenant_id}/{filename}"
        blob_client = self.container_client.get_blob_client(blob_name)

        # Detect content type
        content_type = "application/octet-stream"
        if isinstance(file_or_bytes, str):
            content_type, _ = mimetypes.guess_type(file_or_bytes)
        
        if not content_type:
            content_type = "application/octet-stream"

        try:
            settings = ContentSettings(content_type=content_type)
            if isinstance(file_or_bytes, (bytes, bytearray)):
                blob_client.upload_blob(file_or_bytes, overwrite=True, content_settings=settings)
            elif isinstance(file_or_bytes, str) and os.path.isfile(file_or_bytes):
                with open(file_or_bytes, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True, content_settings=settings)
            else:
                raise ValueError("file_or_bytes must be bytes or valid file path.")
            
            return blob_client.url
        except Exception as e:
            print(f"Upload failed: {e}")
            raise e

# For backward compatibility with existing code that might import FirebaseStorageClient
# we alias it, though calls should eventually start using AzureStorageClient
FirebaseStorageClient = AzureStorageClient
