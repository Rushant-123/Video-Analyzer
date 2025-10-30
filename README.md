# Video-Analyzer

A Python script that processes smart-glasses videos using GCP Vertex AI to enable natural language queries about video content.

## Features

- **Video Segmentation**: Uses Google Cloud Video Intelligence API to segment videos into shots
- **Multimodal Embeddings**: Embeds video segments using Vertex AI's `multimodalembedding@001` model
- **Vector Search**: Stores embeddings in Vertex Vector Search for efficient retrieval
- **Natural Language Queries**: Query videos using natural language (e.g., "who did I meet at the gym?")
- **AI Analysis**: Uses Gemini 2.5 Pro to analyze retrieved video segments for insights

## Demo

🎬 **Try Video-Analyzer with our demo video!**

### Video Preview

<video width="100%" controls>
  <source src="Video-Analyzer.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

*Demo video showcasing Video-Analyzer in action*

> **Note**: If the video doesn't play above, you can [download it directly](Video-Analyzer.mp4) or view it in your local clone.

### Demo Video Download

A sample demo video is available in the repository: [`Video-Analyzer.mp4`](Video-Analyzer.mp4) (24MB)

This demonstrates the full video analysis pipeline including:
- Video segmentation into meaningful shots
- Semantic search capabilities
- AI-powered content analysis
- Real-time query processing

**Note**: The demo video showcases the system analyzing smart-glasses footage and answering natural language questions about the content.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your actual credentials
   # Make sure .env is in .gitignore!
   ```

3. **Required Environment Variables**:
   ```bash
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_APPLICATION_CREDENTIALS=./path-to-service-account.json
   GCS_BUCKET_NAME=your-bucket-name
   GEMINI_API_KEY=your-gemini-api-key
   VECTOR_SEARCH_INDEX_ENDPOINT_ID=your-endpoint-id  # Optional
   VECTOR_SEARCH_DEPLOYED_INDEX_ID=your-index-name   # Optional
   GCP_REGION=us-central1                            # Optional
   GEMINI_MODEL=gemini-2.5-flash                     # Optional
   ```

4. **GCP Setup Requirements**:

### 🔧 **Complete GCP Setup Guide**

#### **Step 1: Create GCP Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., `video-reasoning-project`)
4. Note the **Project ID** (not name) - this is your `GOOGLE_CLOUD_PROJECT`

#### **Step 2: Enable Required APIs**
1. Go to "APIs & Services" → "Library"
2. Enable these APIs:
   - **Vertex AI API**
   - **Cloud Storage API**
   - **Cloud Video Intelligence API**

#### **Step 3: Create Service Account**
1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name: `video-reasoning-sa`
4. Grant these roles:
   - **Storage Admin** (for GCS access)
   - **Vertex AI User** (for AI models)
   - **Service Usage Consumer** (for API access)
5. Create a key:
   - Click the service account → "Keys" → "Add Key" → "JSON"
   - Download the JSON file
   - Place it in your project directory
   - This file path is your `GOOGLE_APPLICATION_CREDENTIALS`

#### **Step 4: Create GCS Bucket**
1. Go to "Cloud Storage" → "Buckets"
2. Click "Create Bucket"
3. Name: `your-unique-bucket-name` (must be globally unique)
4. Region: `us-central1` (or your preferred region)
5. This bucket name is your `GCS_BUCKET_NAME`

#### **Step 5: Get Gemini API Key**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the API key
4. This is your `GEMINI_API_KEY`

#### **Step 6: Enable Billing (Important!)**
1. Go to "Billing" in GCP Console
2. Enable billing for your project
3. **Note**: GCP requires billing to be enabled for most AI services

### 💡 **Quick Setup Commands**

If you have `gcloud` CLI installed:

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable videointelligence.googleapis.com

# Create service account
gcloud iam service-accounts create video-reasoning-sa \
  --description="Video Reasoning Service Account" \
  --display-name="Video Reasoning SA"

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:video-reasoning-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:video-reasoning-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Create key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=video-reasoning-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## Project Structure

```
Video Reasoning/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Configuration management
│   ├── services/
│   │   ├── __init__.py
│   │   ├── storage.py           # GCS operations
│   │   ├── segmentation.py      # Video Intelligence API
│   │   ├── embeddings.py        # Multimodal embeddings
│   │   ├── vector_search.py     # Vector Search
│   │   └── analysis.py          # Gemini analysis
│   ├── utils/
│   │   ├── __init__.py
│   │   └── formatter.py         # Output formatting
│   └── pipeline.py              # Main pipeline orchestrator
├── app.py                        # Streamlit web UI
├── main.py                       # CLI entry point
├── requirements.txt
├── .env                         # Your credentials (not in git)
└── README.md
```

## Usage

### 🌐 Web Interface (Recommended)

The easiest way to use Video-Analyzer is through the web interface:

```bash
# Install Gradio (compatible with Python 3.9.7+)
pip install gradio

# Run the web app
python app.py
```

Then open your browser to `http://localhost:7860` and:
1. 📤 Upload a video file
2. 🔍 Ask a question about the video
3. 🚀 Click "Analyze Video" to get AI-powered insights

### 💻 Command Line Interface

For programmatic use or automation:

```bash
# Simple usage (reads from .env)
python main.py \
  --video-path ./video.mp4 \
  --query "what did I promise?"

# Or override with command line args
python main.py \
  --video-path ./video.mp4 \
  --query "what did I promise?" \
  --project-id your-project-id \
  --region us-central1
```

### Query Options

- `--video-path`: Local video file path or GCS URI (`gs://bucket/video.mp4`)
- `--query`: Natural language question about the video content
- `--project-id`: GCP project ID (overrides `GOOGLE_CLOUD_PROJECT` env var)
- `--region`: GCP region (overrides `GCP_REGION` env var)
- `--top-k`: Number of segments to retrieve and analyze (default: 10)

## Output

The script outputs:
1. **Colorized Console Summary**: Top 3 analyzed segments with key insights
2. **Full JSON Results**: Complete analysis for all retrieved segments

### Sample Output Format
```json
{
  "clip_start": 45.2,
  "clip_end": 78.9,
  "summary": "Meeting with John at the gym entrance",
  "promises": ["Call him tomorrow about the project"],
  "body_language": "Confident handshake, direct eye contact",
  "confidence_score": 0.85,
  "actions": ["Handshake", "Pointing at equipment"]
}
```

## Cost and Rate Limits

**Approximate costs** (based on GCP pricing as of 2024):

- **Video Intelligence API**: ~$0.10-0.20 per minute of video
- **Multimodal Embeddings**: ~$0.0002 per embedding (1408 dimensions)
- **Vector Search**: ~$0.10 per 1000 queries + storage costs
- **Gemini 2.5 Pro**: ~$0.001-0.002 per query

**Rate Limits**:
- Video Intelligence: 100 videos/hour
- Multimodal Embeddings: 1000 requests/minute
- Vector Search: Varies by index configuration
- Gemini: 60 requests/minute

## Architecture

1. **Input Processing**: Upload local videos to GCS or use direct GCS URIs
2. **Segmentation**: Video Intelligence API detects shot boundaries
3. **Embedding**: Each segment gets a 1408-D multimodal embedding
4. **Storage**: Embeddings stored in Vector Search with metadata
5. **Query**: Text queries embedded and matched against video segments
6. **Analysis**: Top segments analyzed by Gemini for structured insights

## Security Notes

- Store service account keys securely
- Use environment variables for sensitive configuration
- GCS bucket should have appropriate access controls
- Consider VPC Service Controls for production deployments
# Video-Analyzer
