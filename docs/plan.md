# Project Implementation Plan

## Phase 1: Infrastructure & Core Setup
- [x] Initial Project Setup (Directory structure, virtualenv)
- [x] Base Dependencies (`requirements.txt`)
- [x] Environment Configuration (`.env.example`)
- [x] LLM Factory Implementation (`src/providers/llm_factory.py`)
- [x] Create missing directories (`audio/`, `output/`, `logs/`)
- [x] Set up logging configuration

## Phase 2: Audio Ingestion Module
- [x] Implement `src/ingestion/audio_downloader.py`
  - [x] YouTube download logic (pytube)
  - [x] Direct URL handling
  - [x] File validation (size/duration)
  - [x] MP3 conversion/storage (Using Pytube default, saved as .mp3)
- [x] **Test**: Unit tests for audio downloader

## Phase 3: Transcription Service
- [x] Implement `src/transcription/transcriber.py`
  - [x] AssemblyAI client integration
  - [x] Transcription job submission (using `transcribe()` blocking call)
  - [x] Configured Universal model, Speaker Diarization, Punctuation
  - [x] Output saving (Raw Text + JSON with timestamps/utterances)
- [x] **Test**: Unit tests for transcription service

## Phase 4: Content Generation Engine
- [x] Implement `src/generation/content_generator.py`
  - [x] Prompt construction (System & User prompts)
  - [x] LLM Client integration (using Factory, supports Gemini/OpenAI/Groq)
  - [x] JSON schema validation
  - [x] Error handling & Retries (Basic exception handling implemented)
- [x] **Test**: Unit tests for content generator

## Phase 5: PDF Design & Generation
- [x] Implement `src/design/pdf_designer.py`
  - [x] `fpdf2` class setup
  - [x] Font loading (using standard fonts for now to ensure compatibility)
  - [x] Color extraction logic (Pillow) with Black/White fallback
  - [x] Page layout design (Cover, Days 1-6)
  - [x] PDF export logic
- [x] **Test**: Unit tests for PDF designer

## Phase 6: CLI & Orchestration
- [ ] Implement `src/main.py` (Orchestrator)
  - [ ] Argument parsing (URL, Series Title, etc.)
  - [ ] Linking pipeline steps (Download -> Transcribe -> Generate -> PDF)
  - [ ] Progress reporting
- [ ] **Test**: Integration tests

## Phase 7: Final Polish
- [ ] Refine prompts based on output quality
- [ ] Optimize PDF layout
