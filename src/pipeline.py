"""Main video reasoning pipeline orchestrator"""

import logging
from typing import List, Dict
from pathlib import Path

from google.cloud import aiplatform

from .config import Settings
from .services import (
    StorageService,
    SegmentationService,
    EmbeddingService,
    VectorSearchService,
    AnalysisService
)

logger = logging.getLogger(__name__)


class VideoReasoningPipeline:
    """Main pipeline for processing smart-glasses videos through GCP Vertex AI"""
    
    def __init__(self, settings: Settings):
        """Initialize pipeline with all services
        
        Args:
            settings: Configuration settings
        """
        self.settings = settings
        
        # Initialize Vertex AI
        aiplatform.init(project=settings.project_id, location=settings.region)
        
        # Initialize services
        self.storage = StorageService(settings.project_id, settings.bucket_name)
        self.segmentation = SegmentationService()
        self.embeddings = EmbeddingService()
        self.vector_search = VectorSearchService(
            settings.project_id,
            settings.region,
            settings.vector_search_endpoint_id,
            settings.vector_search_deployed_index_id
        )
        self.analysis = AnalysisService(
            settings.gemini_api_key,
            settings.gemini_model
        )
        
        logger.info("Initialized VideoReasoningPipeline")
        logger.info(f"Using project: {settings.project_id}, region: {settings.region}, bucket: {settings.bucket_name}")
    
    def process_video(self, video_path: str) -> str:
        """Process video: upload, segment, and embed
        
        Args:
            video_path: Local path or GCS URI
            
        Returns:
            GCS URI of video
        """
        logger.info("Starting video processing pipeline")
        
        # Upload video if local path
        if video_path.startswith("gs://"):
            gcs_uri = video_path
        else:
            gcs_uri = self.storage.upload_video(video_path)
        
        # Segment video
        segments = self.segmentation.segment_video(gcs_uri)
        
        # Generate embeddings for all segments
        logger.info("Generating embeddings for all segments...")
        vectors = []
        for i, segment in enumerate(segments):
            logger.info(f"Processing segment {i+1}/{len(segments)}")
            embedding = self.embeddings.embed_video_segment(
                gcs_uri,
                segment["start"],
                segment["end"]
            )
            vector = {
                "id": f"segment_{i}",
                "embedding": embedding,
                "metadata": {
                    "start_time": segment["start"],
                    "end_time": segment["end"],
                    "video_uri": gcs_uri
                }
            }
            vectors.append(vector)
        
        # Store embeddings in Vector Search
        self.vector_search.upsert_embeddings(vectors)
        
        logger.info("Video processing pipeline complete")
        return gcs_uri
    
    def query_and_analyze(self, query: str, top_k: int = 10) -> List[Dict]:
        """Query video and analyze retrieved segments
        
        Args:
            query: Natural language query
            top_k: Number of segments to retrieve
            
        Returns:
            List of analysis results
        """
        logger.info(f"Starting query analysis: '{query}'")
        
        # Query Vector Search
        segments = self.vector_search.query_similar(
            query,
            self.settings.bucket_name,
            top_k
        )
        
        # Analyze each segment with Gemini
        analyses = []
        for i, segment in enumerate(segments, 1):
            logger.info(f"Analyzing segment {i}/{len(segments)}")
            
            # Add rate limiting to avoid overwhelming the API
            import time
            if i > 1:
                time.sleep(1)
            
            analysis = self.analysis.analyze_segment(segment, self.storage)
            analyses.append(analysis)
        
        logger.info("Query analysis complete")
        return analyses

