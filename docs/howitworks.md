# How It Works (Technical Architecture)

This document provides a technical overview of the Church Study Guide Generator, detailing its architecture, modules, and data flow.

## Architecture Overview

The system follows a sequential pipeline architecture:
`Ingestion -> Transcription -> Content Generation (+ Scripture Retrieval) -> PDF Design`

It uses a **Factory Pattern** for LLM provider abstraction, allowing seamless switching between Gemini, OpenAI, and Groq without changing core logic.

## Directory Structure

```
Church Study Guide/
├── src/
│   ├── ingestion/         # Audio downloading logic (yt-dlp)
│   ├── transcription/     # Speech-to-text integration (AssemblyAI)
│   ├── generation/        # LLM prompts & generation logic
│   ├── design/            # PDF generation & layout
│   ├── providers/         # LLM Factory & Clients
│   ├── utils/             # Helpers (Logger, BibleFetcher, etc.)
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
- **Library**: `yt-dlp`
- **Functionality**:
    - Downloads audio streams from YouTube videos.
    - Extracts metadata (title, duration).
    - **Validation**: Checks for valid YouTube URLs.

### 3. Transcription (`src/transcription/transcriber.py`)
- **Service**: AssemblyAI API
- **Class**: `TranscriptionService`
- **Model**: Universal Speech Model (Best-in-class accuracy).
- **Process**:
    - Uploads local audio file to AssemblyAI.
    - Initiates transcription (Speaker Diarization disabled for cleaner output).
    - Polls the API until status is `completed`.
- **Output**: Raw text + Simplified JSON (Clean text stream without metadata clutter).

### 4. Content Generation (`src/generation/content_generator.py`)
- **Role**: The "Theological Brain".
- **Pattern**: Uses `LLMFactory` (`src/providers/llm_factory.py`) to instantiate the requested provider (Gemini/OpenAI/Groq).
- **Technology**: Migrated to `google-genai` Unified SDK for future-proof Gemini integration.
- **Prompt Engineering**:
    - **System Prompt**: Defines the persona as a "Theological Content Curator".
    - **JSON Enforcement**: Uses strict JSON schema enforcement to ensure machine-readable output.
    - **Style**: Enforces "Mind Muscle" transformation, 350-word reflections, and single application questions.
- **Output**: A JSON object containing:
    - Series Title & Memory Verse Reference
    - 6 Days of content (Scripture Reference, Reflection, Question, Prayer).

### 5. Scripture Retrieval (`src/utils/bible_fetcher.py`)
- **API**: bible-api.com
- **Role**: Fetches actual scripture text to prevent LLM hallucinations.
- **Functionality**:
    - Takes references (e.g., "John 3:16") and version (e.g., "KJV").
    - Retrieves text and removes formatting/line breaks for smooth reading flow.
    - Enriches the JSON content before PDF generation.

### 6. PDF Design (`src/design/pdf_designer.py`)
- **Library**: `fpdf2`
- **Key Features**:
    - **Dynamic Layout**: Automatically calculates text height for prayers and reflections to prevent overflow.
    - **Dynamic Branding**: Uses `Pillow` (PIL) to analyze the provided logo (`--logo`).
        - Extracts the dominant color (Primary) and a secondary color (Accent).
    - **Typography**: Loads **Montserrat** fonts dynamically.
    - **Cover Page**: Features bold Preacher Name, Series Title, and Memory Verse.

## Data Flow

1.  **Input**: User provides `https://youtube.com/...` + Preacher Name + Series.
2.  **Audio**: Downloaded via `yt-dlp` to `audio/video_title.webm` (or similar).
3.  **Transcript**: `transcriber.transcribe_audio(...)` -> returns `str` (text).
4.  **JSON Content**: `content_generator.generate_content(text)` -> calls LLM.
5.  **Enrichment**: `content_generator` calls `BibleFetcher` to fill in `scripture` and `memory_verse` texts.
6.  **PDF**: `pdf_designer.create_pdf(dict, "output/guide.pdf")` -> writes file to disk.

## Key Dependencies

- `assemblyai`: Transcription API client.
- `google-genai` / `openai` / `groq`: LLM SDKs (Migrated from `google-generativeai`).
- `yt-dlp`: YouTube audio download.
- `fpdf2`: PDF generation.
- `Pillow`: Image processing (color extraction).
- `requests`: For Bible API calls.
- `python-dotenv`: Environment variable management.
