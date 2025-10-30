# Video Reasoning System - Architecture

## Overview

The Video Reasoning System is now structured as a modular, maintainable codebase with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│                    (Entry Point)                            │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    src/pipeline.py                          │
│                (Pipeline Orchestrator)                      │
│  - Coordinates all services                                 │
│  - Manages workflow                                         │
└────────────────────────────┬────────────────────────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
┌──────────────────┐  ┌──────────────┐  ┌────────────────┐
│  src/config/     │  │ src/services/│  │  src/utils/    │
│  settings.py     │  │              │  │  formatter.py  │
│                  │  │ - storage    │  │                │
│ - Configuration  │  │ - segment    │  │ - Output       │
│ - Environment    │  │ - embeddings │  │ - Formatting   │
│   variables      │  │ - search     │  │                │
│                  │  │ - analysis   │  │                │
└──────────────────┘  └──────────────┘  └────────────────┘
```

## Module Breakdown

### 1. **Configuration Layer** (`src/config/`)

**Purpose**: Centralized configuration management

- **`settings.py`**: 
  - Loads environment variables
  - Validates configuration
  - Provides type-safe settings access
  - Supports overrides via command-line args

### 2. **Service Layer** (`src/services/`)

**Purpose**: Individual service implementations

- **`storage.py`** - `StorageService`:
  - Upload videos to GCS
  - Download videos from GCS
  - Bucket management

- **`segmentation.py`** - `SegmentationService`:
  - Video Intelligence API integration
  - Shot detection
  - Segment extraction

- **`embeddings.py`** - `EmbeddingService`:
  - Multimodal embedding generation
  - 1408D vector creation
  - Video segment processing

- **`vector_search.py`** - `VectorSearchService`:
  - Vector storage (simulated)
  - Similarity search
  - Query processing

- **`analysis.py`** - `AnalysisService`:
  - Gemini AI integration
  - Video analysis
  - Insight extraction

### 3. **Orchestration Layer** (`src/pipeline.py`)

**Purpose**: Coordinate service interactions

- **`VideoReasoningPipeline`**:
  - Initializes all services
  - Manages workflow
  - Handles video processing
  - Coordinates query and analysis

### 4. **Utility Layer** (`src/utils/`)

**Purpose**: Helper functions and formatters

- **`formatter.py`** - `OutputFormatter`:
  - Console output formatting
  - JSON serialization
  - Result presentation

### 5. **Entry Point** (`main.py`)

**Purpose**: Command-line interface

- Argument parsing
- Error handling
- Logging configuration
- Main execution flow

## Benefits of Modular Architecture

### ✅ **Maintainability**
- Each module has a single responsibility
- Easy to locate and fix bugs
- Clear code organization

### ✅ **Testability**
- Each service can be tested independently
- Mock dependencies easily
- Unit test individual components

### ✅ **Scalability**
- Add new services without touching existing code
- Replace implementations (e.g., swap storage providers)
- Extend functionality cleanly

### ✅ **Reusability**
- Import services in other projects
- Use components independently
- Build on existing modules

### ✅ **Readability**
- Clear separation of concerns
- Self-documenting structure
- Easy onboarding for new developers

## Usage Comparison

### Old (Monolithic):
```bash
python video_reasoning_prototype.py --video-path video.mp4 --query "..." --project-id ...
```

### New (Modular):
```bash
python main.py --video-path video.mp4 --query "..."
```

## Migration Guide

### From Old to New:

1. **Environment Setup** - Same `.env` file
2. **Command** - Use `main.py` instead of `video_reasoning_prototype.py`
3. **Arguments** - Same arguments, cleaner interface
4. **Output** - Same formatted results

### Programmatic Usage:

```python
from src.config import Settings
from src.pipeline import VideoReasoningPipeline

# Load settings
settings = Settings.from_env()

# Create pipeline
pipeline = VideoReasoningPipeline(settings)

# Process video
gcs_uri = pipeline.process_video("video.mp4")

# Query and analyze
results = pipeline.query_and_analyze("what happened?", top_k=3)
```

## Future Enhancements

### Potential Improvements:

1. **Database Integration**: Store results in database
2. **Caching Layer**: Cache embeddings and analyses
3. **Async Processing**: Use async/await for parallel operations
4. **API Server**: Wrap pipeline in FastAPI or Flask
5. **Monitoring**: Add metrics and observability
6. **Testing Suite**: Add unit and integration tests
7. **CI/CD Pipeline**: Automated testing and deployment

## File Structure

```
Video Reasoning/
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── storage.py
│   │   ├── segmentation.py
│   │   ├── embeddings.py
│   │   ├── vector_search.py
│   │   └── analysis.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── formatter.py
│   └── pipeline.py
├── main.py                           # New entry point
├── video_reasoning_prototype.py      # Legacy (can be removed)
├── test_gemini.py                   # Test script
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── ARCHITECTURE.md                   # This file
```

## Best Practices Implemented

1. **Type Hints**: All functions have type annotations
2. **Docstrings**: Comprehensive documentation
3. **Logging**: Structured logging throughout
4. **Error Handling**: Graceful error handling
5. **Configuration**: Environment-based config
6. **Security**: Credentials in .env, not in code
7. **Modularity**: Clear separation of concerns
8. **Pythonic**: Following PEP 8 and Python conventions

