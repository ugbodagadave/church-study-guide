# Church Sermon to Discipleship Guide Converter - Requirements

## Project Overview
A tool that automatically converts church sermon audio into professionally designed discipleship materials. The system transcribes audio/video, generates structured devotional content using configurable LLMs, and produces print-ready PDF study guides.

## Core Dependencies
- **Audio Transcription**: AssemblyAI (Universal Speech Model)
- **Configuration**: python-dotenv
- **PDF Generation**: fpdf2
- **Video Extraction**: pytube
- **Image Processing**: Pillow (for color extraction)
- **LLM Providers**:
  - google-generativeai (Gemini)
  - openai (OpenAI/OpenRouter)
  - groq (Groq Cloud)

## Functional Requirements

### 1. Audio Ingestion
- **Source Support**: 
  - YouTube URLs
  - Facebook Video URLs
  - Direct MP3 links
- **Output**: MP3 files stored in `/audio/{church_name}_{sermon_title}.mp3`
- **Validation**:
  - File size < 500MB
  - Duration: 15-90 minutes (flexible for longer)

### 2. Transcription Pipeline
- **Provider**: AssemblyAI (`speech_models=["universal"]`)
- **Features**:
  - Speaker diarization
  - Punctuation & paragraph segmentation
  - Automatic language detection
- **Outputs**:
  - Raw transcript text file
  - Structured JSON with timestamps

### 3. Content Generation
- **Input**: Raw transcript
- **LLM Abstraction**: Factory pattern supporting Gemini, OpenAI, OpenRouter, Groq
- **Prompt Engineering**:
  - Role: Theological content curator
  - Output: 5-day devotional guide
  - Requirements:
    - Scripture verse (related)
    - 250-word reflection
    - 2 application questions
    - Prayer
    - Connection to sermon series
    - Tone: Warm, encouraging, actionable
- **Structured Output (JSON)**:
  ```json
  {
    "series_title": "string",
    "memory_verse": "string",
    "days": [
      {
        "day": 1,
        "title": "string",
        "scripture": "string",
        "reflection": "string (250 words)",
        "questions": ["string", "string"],
        "prayer": "string"
      }
    ],
    "key_quotes": ["string", "string", "string"]
  }
  ```
- **Validation**: Ensure 6 days generated (Cover + 5 days?), or 5 days + Cover info. (User specified "5-day devotional guide" but "6 days are generated" in validation - clarifying: likely 5 devotional days + 1 overview/intro day or just 5 days content). *Correction based on user input: "Ensure 6 days are generated"* - will adhere to generating 6 entries or 5 days + overview.

### 4. PDF Design
- **Tool**: fpdf2
- **Specs**:
  - Page Size: A4
  - Length: 6-7 pages
  - Typography: Montserrat (11pt body, 14pt headers)
  - Branding: Auto-extracted colors from church logo
- **Sections**:
  - Cover
  - Memory Verse
  - 6 Daily Sections (Title, Scripture, Reflection, Questions, Prayer)
- **Output**: 
  - Print-ready PDF
  - Compressed PDF (<5MB)

## System Architecture
- **Language**: Python
- **Configuration**: Environment variables (.env)
- **Directory Structure**:
  - `src/`: Source code
  - `audio/`: Temporary audio storage
  - `docs/`: Documentation
  - `output/`: Generated PDFs
