#!/usr/bin/env python3
"""
Video-Analyzer Web UI
A Streamlit-based web interface for video analysis using GCP Vertex AI
"""

import streamlit as st
import tempfile
import os
import time
from pathlib import Path

# Import our video reasoning pipeline
from src.config import Settings
from src.pipeline import VideoReasoningPipeline


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Video-Analyzer",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    .result-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<h1 class="main-header">🎬 Video-Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload a video and ask questions about its content using AI</p>', unsafe_allow_html=True)

    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("""
        **Video-Analyzer** uses Google's AI to understand video content:

        🔍 **Video Segmentation** - Automatically detects shots
        🧠 **AI Embeddings** - Creates semantic representations
        🎯 **Smart Search** - Finds relevant video segments
        🤖 **Gemini Analysis** - Provides detailed insights
        """)

        st.header("🔧 Tech Stack")
        st.write("""
        - **Google Cloud Vertex AI**
        - **Gemini 2.5 Flash**
        - **Video Intelligence API**
        - **Multimodal Embeddings**
        """)

        st.header("⚡ Features")
        st.write("""
        ✅ Natural language queries
        ✅ Body language analysis
        ✅ Promise detection
        ✅ Action recognition
        ✅ Timestamped results
        """)

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Upload Video")

        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a video file (MP4, AVI, MOV)",
            type=["mp4", "avi", "mov", "mkv"],
            help="Upload a short video (under 5 minutes for best results)"
        )

        # Query input
        query = st.text_input(
            "🔍 Ask a question about the video:",
            placeholder="e.g., 'What is being demonstrated?', 'What promises were made?', 'Describe the presenter's body language'",
            help="Ask natural language questions about the video content"
        )

        # Process button
        process_button = st.button(
            "🚀 Analyze Video",
            type="primary",
            use_container_width=True,
            disabled=not (uploaded_file and query)
        )

    with col2:
        st.subheader("📊 Analysis Results")

        # Results display area
        results_placeholder = st.empty()

        # Show sample results if no analysis has been run
        if 'analysis_results' not in st.session_state:
            with results_placeholder.container():
                st.info("💡 Upload a video and ask a question to see AI-powered analysis!")

                # Sample result preview
                st.markdown("""
                **Example Output:**
                - **Clip 1 (0:10-0:25)**: Demonstrates the landing page of AVEA THE AI VILLAGE
                - **Key Features**: Pixel art style, interactive buttons, user registration
                - **Promises**: AI characters that evolve, safe digital space
                - **Body Language**: Engaged and enthusiastic presenter
                """)

    # Processing logic
    if process_button and uploaded_file and query:
        # Clear previous results
        results_placeholder.empty()

        with results_placeholder.container():
            with st.spinner("🔄 Initializing AI pipeline..."):
                try:
                    # Load settings
                    settings = Settings.from_env()
                    settings.validate()

                    # Initialize pipeline
                    pipeline = VideoReasoningPipeline(settings)
                    st.success("✅ AI pipeline ready!")

                except Exception as e:
                    st.error(f"❌ Failed to initialize pipeline: {e}")
                    st.error("Please check your .env file and GCP credentials")
                    return

            # Save uploaded file temporarily
            with st.spinner("📁 Processing video upload..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    video_path = tmp_file.name

            try:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Process video (segment and embed)
                status_text.text("🎬 Processing video: segmenting and generating embeddings...")
                progress_bar.progress(25)

                gcs_uri = pipeline.process_video(video_path)
                progress_bar.progress(50)

                # Step 2: Query and analyze
                status_text.text("🤖 Analyzing video content with AI...")
                progress_bar.progress(75)

                analyses = pipeline.query_and_analyze(query, top_k=3)
                progress_bar.progress(100)

                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()

                # Display results
                st.success("🎉 Analysis complete!")

                for i, analysis in enumerate(analyses, 1):
                    with st.container():
                        st.markdown(f"""
                        <div class="result-card">
                            <h4>🎬 Clip {i}: {analysis['clip_start']:.1f}s - {analysis['clip_end']:.1f}s</h4>
                            <p><strong>📝 Summary:</strong> {analysis['summary']}</p>
                            <p><strong>🎯 Confidence:</strong> {analysis.get('confidence_score', 0.0):.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                # JSON download button
                import json
                json_data = json.dumps(analyses, indent=2)
                st.download_button(
                    label="📥 Download Full Results (JSON)",
                    data=json_data,
                    file_name="video_analysis_results.json",
                    mime="application/json"
                )

            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                st.error("This might be due to GCP service limits or network issues. Try again or check your credentials.")

            finally:
                # Clean up temporary file
                if os.path.exists(video_path):
                    os.unlink(video_path)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Google Cloud Vertex AI & Streamlit</p>
        <p><a href="https://github.com/Rushant-123/Video-Analyzer" target="_blank">View on GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
