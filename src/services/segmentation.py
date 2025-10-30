"""Video Intelligence API service for video segmentation"""

import logging
from typing import List, Dict
from google.cloud import videointelligence_v1 as videointelligence

logger = logging.getLogger(__name__)


class SegmentationService:
    """Handles video segmentation using Google Cloud Video Intelligence API"""
    
    def __init__(self):
        """Initialize Video Intelligence client"""
        self.client = videointelligence.VideoIntelligenceServiceClient()
        logger.info("Initialized SegmentationService")
    
    def segment_video(self, gcs_uri: str) -> List[Dict]:
        """Detect shot changes in video using Video Intelligence API
        
        Args:
            gcs_uri: GCS URI of video file
            
        Returns:
            List of segment dictionaries with start and end times
        """
        logger.info("Starting video segmentation with Video Intelligence API")
        
        features = [videointelligence.Feature.SHOT_CHANGE_DETECTION]
        operation = self.client.annotate_video(
            request={"features": features, "input_uri": gcs_uri}
        )
        
        logger.info("Waiting for video annotation to complete...")
        result = operation.result(timeout=300)
        
        segments = []
        for i, shot in enumerate(result.annotation_results[0].shot_annotations):
            start_time = shot.start_time_offset.seconds + shot.start_time_offset.microseconds / 1e6
            end_time = shot.end_time_offset.seconds + shot.end_time_offset.microseconds / 1e6
            
            # Ensure minimum segment duration (at least 1 second for embedding)
            duration = end_time - start_time
            if duration < 1.0:
                end_time = start_time + 1.0
            
            segment = {
                "start": start_time,
                "end": end_time
            }
            logger.info(f"Segment {i+1}: start={start_time:.1f}s, end={end_time:.1f}s, duration={end_time-start_time:.1f}s")
            segments.append(segment)
        
        logger.info(f"Found {len(segments)} shot segments")
        return segments

