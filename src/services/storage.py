"""Google Cloud Storage service for video file management"""

import logging
from pathlib import Path
from google.cloud import storage

logger = logging.getLogger(__name__)


class StorageService:
    """Handles video file uploads and downloads from Google Cloud Storage"""
    
    def __init__(self, project_id: str, bucket_name: str):
        """Initialize GCS client
        
        Args:
            project_id: GCP project ID
            bucket_name: GCS bucket name for video storage
        """
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.client = storage.Client(project=project_id)
        
        logger.info(f"Initialized StorageService for bucket: {bucket_name}")
    
    def upload_video(self, local_path: str) -> str:
        """Upload local video file to GCS bucket
        
        Args:
            local_path: Local path to video file
            
        Returns:
            GCS URI of uploaded file (gs://bucket/filename)
        """
        bucket = self.client.bucket(self.bucket_name)
        
        # Create bucket if it doesn't exist
        if not bucket.exists():
            logger.info(f"Creating GCS bucket: {self.bucket_name}")
            bucket.create(location="us-central1")
            logger.info(f"Bucket {self.bucket_name} created successfully")
        
        filename = Path(local_path).name
        blob = bucket.blob(filename)
        
        logger.info(f"Uploading {local_path} to gs://{self.bucket_name}/{filename}")
        blob.upload_from_filename(local_path)
        
        gcs_uri = f"gs://{self.bucket_name}/{filename}"
        logger.info(f"Upload complete: {gcs_uri}")
        
        return gcs_uri
    
    def download_video(self, gcs_uri: str, local_path: str) -> None:
        """Download video from GCS to local file
        
        Args:
            gcs_uri: GCS URI (gs://bucket/filename)
            local_path: Local path to save file
        """
        if gcs_uri.startswith("gs://"):
            bucket_name = gcs_uri.split("/")[2]
            blob_path = "/".join(gcs_uri.split("/")[3:])
            
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            
            logger.info(f"Downloading {gcs_uri} to {local_path}")
            blob.download_to_filename(local_path)
            logger.info(f"Download complete: {local_path}")
        else:
            raise ValueError(f"Invalid GCS URI: {gcs_uri}")

