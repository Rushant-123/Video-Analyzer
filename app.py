#!/usr/bin/env python3
"""
Video-Analyzer Web UI
A Gradio-based web interface for video analysis using GCP Vertex AI
"""

import gradio as gr
import tempfile
import os
import json
from typing import List, Dict

# Import our video reasoning pipeline
from src.config import Settings
from src.pipeline import VideoReasoningPipeline


def analyze_video(video_file, query: str) -> str:
    """
    Process video and return analysis results

    Args:
        video_file: Uploaded video file
        query: User's question about the video

    Returns:
        Formatted analysis results as HTML string
    """
    if not video_file or not query:
        return "<div style='color: red; padding: 10px;'>Please upload a video and enter a question.</div>"

    try:
        # Load settings
        settings = Settings.from_env()
        settings.validate()

        # Initialize pipeline
        pipeline = VideoReasoningPipeline(settings)

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            # Gradio gives us the file path directly
            import shutil
            shutil.copy2(video_file, tmp_file.name)
            video_path = tmp_file.name

        try:
            # Process video (segment and embed)
            yield "<div style='color: blue; padding: 10px;'>🎬 Processing video: segmenting and generating embeddings...</div>"

            gcs_uri = pipeline.process_video(video_path)

            # Query and analyze
            yield "<div style='color: blue; padding: 10px;'>🤖 Analyzing video content with AI...</div>"

            analyses = pipeline.query_and_analyze(query, top_k=3)

            # Format results as HTML
            result_html = "<div style='font-family: Arial, sans-serif;'>"
            result_html += "<h2 style='color: #1f77b4;'>🎉 Analysis Complete!</h2>"

            for i, analysis in enumerate(analyses, 1):
                result_html += f"""
                <div style='background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 10px; border-left: 5px solid #1f77b4;'>
                    <h4 style='color: #1f77b4; margin-top: 0;'>🎬 Clip {i}: {analysis['clip_start']:.1f}s - {analysis['clip_end']:.1f}s</h4>
                    <p><strong>📝 Summary:</strong> {analysis['summary']}</p>
                    <p><strong>🎯 Confidence:</strong> {analysis.get('confidence_score', 0.0):.2f}</p>
                </div>
                """

            result_html += "<h3>📊 Full Results (JSON):</h3>"
            result_html += f"<pre style='background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;'>{json.dumps(analyses, indent=2)}</pre>"
            result_html += "</div>"

            yield result_html

        finally:
            # Clean up temporary file
            if os.path.exists(video_path):
                os.unlink(video_path)

    except Exception as e:
        error_msg = f"""
        <div style='color: red; padding: 10px; background-color: #ffebee; border-radius: 5px;'>
            <h3>❌ Analysis Failed</h3>
            <p>{str(e)}</p>
            <p>This might be due to GCP service limits or network issues. Please check your credentials and try again.</p>
        </div>
        """
        yield error_msg


def create_interface():
    """Create the Gradio interface"""

    # Custom CSS for better styling
    css = """
    .gradio-container {
        max-width: 1200px;
        margin: auto;
    }
    .title {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    """

    # Create the interface
    with gr.Blocks(title="Video-Analyzer", theme=gr.themes.Soft(), css=css) as interface:

        # Header
        gr.HTML("""
        <div class="title">🎬 Video-Analyzer</div>
        <div class="subtitle">Upload a video and ask questions about its content using AI</div>
        """)

        # Sidebar with information
        with gr.Accordion("ℹ️ About Video-Analyzer", open=False):
            gr.Markdown("""
            **Video-Analyzer** uses Google's AI to understand video content:

            🔍 **Video Segmentation** - Automatically detects shots
            🧠 **AI Embeddings** - Creates semantic representations
            🎯 **Smart Search** - Finds relevant video segments
            🤖 **Gemini Analysis** - Provides detailed insights

            ### Tech Stack
            - **Google Cloud Vertex AI**
            - **Gemini 2.5 Flash**
            - **Video Intelligence API**
            - **Multimodal Embeddings**

            ### Features
            ✅ Natural language queries
            ✅ Body language analysis
            ✅ Promise detection
            ✅ Action recognition
            ✅ Timestamped results
            """)

        # Main interface
        with gr.Row():
            # Input column
            with gr.Column(scale=1):
                gr.HTML("<h3>📤 Upload & Configure</h3>")

                video_input = gr.File(
                    label="Choose a video file",
                    file_types=[".mp4", ".avi", ".mov", ".mkv"],
                    elem_classes="file-input"
                )

                query_input = gr.Textbox(
                    label="🔍 Ask a question about the video",
                    placeholder="e.g., 'What is being demonstrated?', 'What promises were made?', 'Describe the presenter's body language'",
                    lines=2
                )

                analyze_btn = gr.Button(
                    "🚀 Analyze Video",
                    variant="primary",
                    size="lg"
                )

            # Output column
            with gr.Column(scale=1):
                gr.HTML("<h3>📊 Analysis Results</h3>")

                output_display = gr.HTML(
                    value="<div style='text-align: center; color: #666; padding: 20px;'>💡 Upload a video and ask a question to see AI-powered analysis!</div>"
                )

        # Sample results preview
        with gr.Accordion("📋 Example Output", open=False):
            gr.Markdown("""
            **Example Analysis Results:**
            - **Clip 1 (0:10-0:25)**: Demonstrates the landing page of AVEA THE AI VILLAGE
            - **Key Features**: Pixel art style, interactive buttons, user registration
            - **Promises**: AI characters that evolve, safe digital space
            - **Body Language**: Engaged and enthusiastic presenter
            """)

        # Connect the function
        analyze_btn.click(
            fn=analyze_video,
            inputs=[video_input, query_input],
            outputs=output_display
        )

        # Footer
        gr.HTML("""
        <hr style='margin: 20px 0;'>
        <div style='text-align: center; color: #666;'>
            <p>Built with ❤️ using Google Cloud Vertex AI & Gradio</p>
            <p><a href="https://github.com/Rushant-123/Video-Analyzer" target="_blank" style='color: #1f77b4;'>View on GitHub</a></p>
        </div>
        """)

    return interface


def main():
    """Launch the Gradio interface"""
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False  # Set to True for public sharing
    )


if __name__ == "__main__":
    main()
