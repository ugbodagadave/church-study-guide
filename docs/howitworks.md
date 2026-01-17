# How It Works (Technical Architecture)

This document provides a technical overview of the Church Study Guide Generator, detailing its architecture, modules, and data flow.

## Architecture Overview

The system follows a sequential pipeline architecture:
`Ingestion -> Transcription -> Content Generation -> PDF Design`

It uses a **Factory Pattern** for LLM provider abstraction, allowing seamless switching between Gemini, OpenAI, and Groq without changing core logic.

## Directory Structure

```
Church Study Guide/
├── src/
│   ├── ingestion/         # Audio downloading logic
│   ├── transcription/     # Speech-to-text integration
│   ├── generation/        # LLM prompts & generation logic
│   ├── design/            # PDF generation & layout
│   ├── providers/         # LLM Factory & Clients
│   ├── utils/             # Helpers (Logger, etc.)
│   └── main.py            # CLI Orchestrator
├── assets/                # Fonts & Images
├── docs/                  # Documentation
├── output/                # Generated PDFs
└── tests/                 # Unit tests
```

## Module Breakdown

### 1. Orchestrator (`src/main.py`)
- **Role**: Entry point. Parses CLI arguments and coordinates the data flow between modules.
- **Key Logic**:
    - Validates inputs (URL vs File).
    - Sets the active LLM provider via environment variables.
    - Handles top-level error catching and logging.

### 2. Audio Ingestion (`src/ingestion/audio_downloader.py`)
- **Library**: `pytube`
- **Functionality**:
    - Downloads audio streams from YouTube videos.
    - Converts streams to MP3 format.
    - **Validation**: Checks for file size limits (<500MB) to prevent API timeouts.

### 3. Transcription (`src/transcription/transcriber.py`)
- **Service**: AssemblyAI API
- **Model**: Universal Speech Model (Best-in-class accuracy).
- **Process**:
    - Uploads local audio file to AssemblyAI.
    - Initiates transcription with Speaker Diarization enabled.
    - Polls the API until status is `completed`.
- **Output**: Raw text + Structured JSON (with timestamps/speakers).

### 4. Content Generation (`src/generation/content_generator.py`)
- **Role**: The "Theological Brain".
- **Pattern**: Uses `LLMFactory` (`src/providers/llm_factory.py`) to instantiate the requested provider (Gemini/OpenAI/Groq).
- **Prompt Engineering**:
    - **System Prompt**: Defines the persona as a "Theological Content Curator".
    - **JSON Enforcement**: Uses strict JSON schema enforcement (via `response_mime_type="application/json"` or provider equivalents) to ensure the output is machine-readable.
- **Output**: A JSON object containing:
    - Series Title
    - Memory Verse
    - 6 Days of content (Scripture, Reflection, Questions, Prayer).

### 5. PDF Design (`src/design/pdf_designer.py`)
- **Library**: `fpdf2`
- **Key Features**:
    - **Inheritance**: Subclasses `FPDF` to create custom Header/Footer methods.
    - **Dynamic Branding**: Uses `Pillow` (PIL) to analyze the provided logo (`--logo`).
        - Extracts the dominant color (Primary) and a secondary color (Accent).
        - Falls back to Black/Grey if no logo is provided or extraction fails.
    - **Typography**: Loads **Montserrat** fonts dynamically from `assets/fonts/`.
    - **Layout**: Programmatic placement of text blocks, rectangles, and images using `x, y` coordinates.

## Data Flow

1.  **Input**: User provides `https://youtube.com/...`
2.  **Audio**: Saved as `audio/video_title.mp3`
3.  **Transcript**: `transcriber.transcribe("audio/video_title.mp3")` -> returns `str` (text).
4.  **JSON Content**: `content_generator.generate_content(text)` -> returns `dict`.
5.  **PDF**: `pdf_designer.create_pdf(dict, "output/guide.pdf")` -> writes file to disk.

## Key Dependencies

- `assemblyai`: Transcription API client.
- `google-generativeai` / `openai` / `groq`: LLM SDKs.
- `fpdf2`: PDF generation.
- `Pillow`: Image processing (color extraction).
- `python-dotenv`: Environment variable management.
