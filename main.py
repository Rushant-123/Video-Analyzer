#!/usr/bin/env python3
"""
Video Reasoning System - Main Entry Point

This script processes smart-glasses videos through:
1. Video Intelligence API for shot segmentation
2. Multimodal Embeddings for semantic representation
3. Vector Search for efficient retrieval
4. Gemini for multimodal reasoning

Usage:
    python main.py --video-path /path/to/video.mp4 --query "what did I promise?"
"""

import argparse
import logging
import sys

from src.config import Settings
from src.pipeline import VideoReasoningPipeline
from src.utils import OutputFormatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for video reasoning system"""
    parser = argparse.ArgumentParser(
        description="Video Reasoning System - Process and analyze video recordings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process local video
  python main.py --video-path ./video.mp4 --query "what did I promise?"
  
  # Process GCS video
  python main.py --video-path gs://bucket/video.mp4 --query "who did I meet?"
  
  # Override project and region
  python main.py --video-path ./video.mp4 --query "..." --project-id my-project --region us-west1
        """
    )
    
    parser.add_argument(
        "--video-path",
        required=True,
        help="Local path to video file or GCS URI (gs://bucket/video.mp4)"
    )
    parser.add_argument(
        "--query",
        required=True,
        help="Natural language query about the video content"
    )
    parser.add_argument(
        "--project-id",
        help="GCP project ID (overrides GOOGLE_CLOUD_PROJECT env var)"
    )
    parser.add_argument(
        "--region",
        help="GCP region (overrides GCP_REGION env var, default: us-central1)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of top segments to retrieve and analyze (default: 3)"
    )
    
    args = parser.parse_args()
    
    try:
        # Load settings from environment
        logger.info("Loading configuration...")
        settings = Settings.from_env(args.project_id, args.region)
        settings.validate()
        
        # Initialize pipeline
        logger.info("Initializing video reasoning pipeline...")
        pipeline = VideoReasoningPipeline(settings)
        
        # Process video (segment and embed)
        logger.info(f"Processing video: {args.video_path}")
        gcs_uri = pipeline.process_video(args.video_path)
        
        # Query and analyze
        logger.info(f"Querying with: '{args.query}'")
        analyses = pipeline.query_and_analyze(args.query, args.top_k)
        
        # Format and display results
        OutputFormatter.format_results(analyses)
        
        logger.info("Video reasoning complete!")
        return 0
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file or environment variables")
        return 1
    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

