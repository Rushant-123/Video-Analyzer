# Video-Analyzer

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Vertex%20AI-4285F4?style=flat&logo=googlecloud&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Gemini](https://img.shields.io/badge/Gemini-2.5-8E75B2?style=flat&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Gradio](https://img.shields.io/badge/Gradio-Web%20UI-FF7C00?style=flat&logo=gradio&logoColor=white)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Transform first-person video into searchable, queryable knowledge using multimodal AI.**

Video-Analyzer processes smart glasses and wearable camera footage through Google Cloud's AI stack, enabling natural language queries like *"What did I promise?"* or *"Who did I meet at the gym?"*

## Demo

https://github.com/user-attachments/assets/4bd4b985-ce9a-4786-966e-cc735e7c8a30

*AI-powered analysis of smart glasses footage with natural language queries*

## Architecture

```
Video Input --> GCS Upload --> Shot Detection --> Multimodal Embeddings --> Vector Search
                                                                                  |
                                                                                  v
                              Gemini Analysis <-- Segment Retrieval <-- Text Query
```

### Pipeline Flow

| Stage | Service | Technology |
|-------|---------|------------|
| **1. Upload** | `StorageService` | Google Cloud Storage |
| **2. Segment** | `SegmentationService` | Video Intelligence API |
| **3. Embed** | `EmbeddingService` | Multimodal Embeddings (1408-D) |
| **4. Index** | `VectorSearchService` | Vertex Vector Search / Pinecone |
| **5. Analyze** | `AnalysisService` | Gemini 2.5 |

### How It Works

1. **Video Segmentation** - Video Intelligence API detects shot boundaries automatically
2. **Semantic Embeddings** - Each segment becomes a 1408-dimensional vector capturing visual and audio content
3. **Vector Storage** - Embeddings indexed for sub-second similarity search
4. **Query Processing** - Natural language queries converted to embeddings and matched against video segments
5. **AI Analysis** - Gemini analyzes retrieved segments and extracts structured insights

## Setup

### Prerequisites

- Python 3.9+
- Google Cloud account with billing enabled
- `gcloud` CLI (optional but recommended)

### Installation

```bash
git clone https://github.com/Rushant-123/Video-Analyzer.git
cd Video-Analyzer
pip install -r requirements.txt
cp .env.example .env
```

### GCP Configuration

#### Option A: Using gcloud CLI

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com \
                       storage.googleapis.com \
                       videointelligence.googleapis.com

# Create service account
gcloud iam service-accounts create video-analyzer-sa \
  --display-name="Video Analyzer Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:video-analyzer-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:video-analyzer-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Generate key file
gcloud iam service-accounts keys create credentials.json \
  --iam-account=video-analyzer-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

#### Option B: Google Cloud Console

1. Create project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable APIs: Vertex AI, Cloud Storage, Video Intelligence
3. Create service account with Storage Admin + Vertex AI User roles
4. Download JSON key file

### Environment Variables

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
GCS_BUCKET_NAME=your-bucket-name
GEMINI_API_KEY=your-gemini-api-key

# Optional
GCP_REGION=us-central1
GEMINI_MODEL=gemini-2.5-flash
VECTOR_SEARCH_INDEX_ENDPOINT_ID=your-endpoint-id
VECTOR_SEARCH_DEPLOYED_INDEX_ID=your-index-id
```

Get your Gemini API key at [makersuite.google.com](https://makersuite.google.com/app/apikey)

## Usage

### Web Interface

```bash
python app.py
```

Open `http://localhost:7860` and:
1. Upload a video file
2. Enter your question
3. Click **Analyze Video**

### Command Line

```bash
# Basic usage
python main.py --video-path ./video.mp4 --query "What promises were made?"

# With GCS video
python main.py --video-path gs://bucket/video.mp4 --query "Who did I meet?"

# Custom parameters
python main.py --video-path ./video.mp4 \
               --query "Describe the conversation" \
               --top-k 5 \
               --project-id my-project \
               --region us-west1
```

### Programmatic

```python
from src.config import Settings
from src.pipeline import VideoReasoningPipeline

settings = Settings.from_env()
pipeline = VideoReasoningPipeline(settings)

gcs_uri = pipeline.process_video("meeting.mp4")
results = pipeline.query_and_analyze("What action items were discussed?", top_k=3)
```

## Project Structure

```
Video-Analyzer/
├── src/
│   ├── config/settings.py      # Environment configuration
│   ├── services/
│   │   ├── storage.py          # GCS operations
│   │   ├── segmentation.py     # Video Intelligence API
│   │   ├── embeddings.py       # Multimodal embeddings
│   │   ├── vector_search.py    # Vector similarity search
│   │   └── analysis.py         # Gemini analysis
│   ├── utils/formatter.py      # Output formatting
│   └── pipeline.py             # Orchestration layer
├── app.py                      # Gradio web interface
├── main.py                     # CLI entry point
└── requirements.txt
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Video Processing | Google Cloud Video Intelligence API |
| Embeddings | Vertex AI Multimodal Embeddings (`multimodalembedding@001`) |
| Vector Search | Vertex Vector Search / Pinecone |
| Analysis | Gemini 2.5 Pro/Flash |
| Web UI | Gradio |
| Storage | Google Cloud Storage |

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with Google Cloud Vertex AI
