"""Configuration settings for Video Reasoning System"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Settings:
    """Application settings loaded from environment variables"""
    
    # GCP Configuration
    project_id: str
    region: str
    bucket_name: str
    credentials_path: str
    
    # Gemini Configuration
    gemini_api_key: str
    gemini_model: str
    
    # Vector Search Configuration (Optional)
    vector_search_endpoint_id: Optional[str] = None
    vector_search_deployed_index_id: Optional[str] = None
    
    @classmethod
    def from_env(cls, project_id: Optional[str] = None, region: Optional[str] = None) -> 'Settings':
        """Load settings from environment variables
        
        Args:
            project_id: Override GOOGLE_CLOUD_PROJECT env var
            region: Override GCP_REGION env var
            
        Returns:
            Settings instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        project = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project:
            raise ValueError("GOOGLE_CLOUD_PROJECT must be set in environment or passed as argument")
        
        bucket = os.getenv('GCS_BUCKET_NAME')
        if not bucket:
            raise ValueError("GCS_BUCKET_NAME must be set in environment")
        
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY must be set in environment")
        
        credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not credentials:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS must be set in environment")
        
        return cls(
            project_id=project,
            region=region or os.getenv('GCP_REGION', 'us-central1'),
            bucket_name=bucket,
            credentials_path=credentials,
            gemini_api_key=gemini_key,
            gemini_model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
            vector_search_endpoint_id=os.getenv('VECTOR_SEARCH_INDEX_ENDPOINT_ID'),
            vector_search_deployed_index_id=os.getenv('VECTOR_SEARCH_DEPLOYED_INDEX_ID')
        )
    
    def validate(self) -> None:
        """Validate that all required settings are present"""
        required_fields = [
            'project_id', 'region', 'bucket_name', 
            'credentials_path', 'gemini_api_key', 'gemini_model'
        ]
        
        for field in required_fields:
            value = getattr(self, field)
            if not value:
                raise ValueError(f"Required setting '{field}' is missing")

