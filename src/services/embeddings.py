"""Vertex AI Multimodal Embedding service"""

import logging
from typing import List
from vertexai.vision_models import MultiModalEmbeddingModel, Video, VideoSegmentConfig

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Handles video segment embedding using Vertex AI Multimodal Embeddings"""
    
    def __init__(self):
        """Initialize Multimodal Embedding model"""
        self.model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
        logger.info("Initialized EmbeddingService with multimodalembedding@001")
    
    def embed_video_segment(self, gcs_uri: str, start_sec: float, end_sec: float) -> List[float]:
        """Generate embedding for a video segment
        
        Args:
            gcs_uri: GCS URI of video file
            start_sec: Start time in seconds
            end_sec: End time in seconds
            
        Returns:
            1408-dimensional embedding vector
        """
        logger.info(f"Creating VideoSegmentConfig: start={int(start_sec)}, end={int(end_sec)}")
        
        video = Video(gcs_uri=gcs_uri)
        
        start_int = int(start_sec)
        end_int = int(end_sec)
        
        if end_int <= start_int:
            end_int = start_int + 1
        
        video_segment_config = VideoSegmentConfig(
            start_offset_sec=start_int,
            end_offset_sec=end_int
        )
        
        embeddings = self.model.get_embeddings(
            video=video,
            video_segment_config=video_segment_config
        )
        
        if not embeddings:
            raise ValueError("No embedding generated for video clip")
        
        # Extract embedding from response
        if hasattr(embeddings, 'video_embeddings') and embeddings.video_embeddings:
            video_embedding = embeddings.video_embeddings[0]
            if hasattr(video_embedding, 'embedding'):
                embedding = video_embedding.embedding
            elif hasattr(video_embedding, 'values'):
                embedding = video_embedding.values
            else:
                try:
                    embedding = list(video_embedding)
                except:
                    logger.error(f"Could not extract embedding from video_embedding: {video_embedding}")
                    raise ValueError("Unknown video embedding structure")
        else:
            logger.warning("No video_embeddings found, using text_embedding fallback")
            embedding = embeddings.text_embedding
        
        if not embedding:
            raise ValueError("Empty embedding returned")
        
        logger.info(f"Generated {len(embedding)}-dimensional embedding")
        return embedding

