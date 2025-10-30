"""Gemini AI analysis service"""

import logging
import time
import os
import tempfile
from typing import Dict
import google.generativeai as genai

logger = logging.getLogger(__name__)


class AnalysisService:
    """Handles video analysis using Gemini AI"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize Gemini client
        
        Args:
            api_key: Gemini API key
            model_name: Gemini model to use
        """
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model_name)
        self.model_name = model_name
        
        logger.info(f"Initialized AnalysisService with {model_name}")
    
    def analyze_segment(
        self, 
        segment: Dict,
        storage_service
    ) -> Dict:
        """Analyze video segment with Gemini
        
        Args:
            segment: Segment dictionary with timing and video URI
            storage_service: StorageService instance for downloading video
            
        Returns:
            Analysis results with structured insights
        """
        logger.info(f"Analyzing segment {segment['id']}")
        
        temp_file_path = None
        try:
            # Download video from GCS to temporary local file
            gcs_uri = segment["video_uri"]
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            temp_file_path = temp_file.name
            temp_file.close()
            
            logger.info("Downloading video from GCS for Gemini analysis...")
            storage_service.download_video(gcs_uri, temp_file_path)
            
            # Upload to Gemini
            logger.info("Uploading video to Gemini API...")
            video_file = genai.upload_file(temp_file_path)
            logger.info(f"Video uploaded: {video_file.name}")
            
            # Wait for the file to be processed and become ACTIVE
            logger.info("Waiting for video to be processed by Gemini...")
            max_wait = 60  # Maximum 60 seconds
            wait_time = 0
            while video_file.state.name == "PROCESSING" and wait_time < max_wait:
                time.sleep(2)
                wait_time += 2
                video_file = genai.get_file(video_file.name)
                logger.info(f"File state: {video_file.state.name} (waited {wait_time}s)")
            
            if video_file.state.name != "ACTIVE":
                raise Exception(f"Video file did not become ACTIVE after {wait_time}s. State: {video_file.state.name}")
            
            logger.info("Video is now ACTIVE and ready for analysis")
            
            # Create the analysis prompt with time information
            prompt_text = f"""Analyze this video segment from {segment['start_time']:.1f} to {segment['end_time']:.1f} seconds.

Answer: what's being demonstrated? List:
- Key features shown
- Promises or commitments made
- Actions performed
- Brief body-language assessment of the presenter

Be specific and detailed about what you observe in this time segment."""
            
            # Call Gemini with video and text
            logger.info("Generating content analysis...")
            response = self.client.generate_content([
                video_file,
                prompt_text
            ])
            
            analysis_text = response.text
            
            # Parse the response
            analysis = self._parse_response(analysis_text)
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            analysis = {
                "summary": f"Analysis failed: {str(e)}",
                "promises": [],
                "body_language": "Analysis failed",
                "confidence_score": 0.5,
                "actions": []
            }
        
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.info("Cleaned up temporary video file")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file: {e}")
        
        # Add timing information
        analysis.update({
            "clip_start": segment["start_time"],
            "clip_end": segment["end_time"]
        })
        
        logger.info(f"Gemini analysis complete for segment {segment['id']}")
        return analysis
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini response into structured format
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Structured analysis dictionary
        """
        # Simple parsing - use full response as summary
        return {
            "summary": response_text,
            "promises": [],
            "body_language": "",
            "confidence_score": 0.8,
            "actions": []
        }

