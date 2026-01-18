# Church Study Guide Generator

**Automated Sermon-to-Discipleship Tool**

This tool automatically converts church sermon audio (from YouTube or local files) into professionally designed, printable PDF discipleship guides. It uses AI to transcribe the audio, extract key theological themes, and generate a 6-day devotional study guide.

## Features

- **Audio Ingestion**: Downloads audio directly from YouTube (using `yt-dlp`) or accepts local audio files.
- **AI Transcription**: Uses AssemblyAI for high-accuracy speech-to-text conversion.
- **Content Generation**: Generates a 6-day devotional plan using advanced LLMs (Gemini, OpenAI, or Groq).
- **Reliable Scripture**: Integrates with Bible-API.com to fetch accurate scripture texts (KJV, WEB, etc.) instead of relying on AI hallucination.
- **Professional Design**: Creates print-ready PDFs with custom branding (church logo), colors, and typography (Montserrat).

## Setup

1.  **Prerequisites**:
    - Python 3.10 or higher.
    - An AssemblyAI API Key.
    - An LLM API Key (Google Gemini, OpenAI, or Groq).

2.  **Installation**:
    ```bash
    # Clone the repository
    git clone <repository-url>
    cd "Church Study Guide"

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    Create a `.env` file in the root directory and add your API keys:
    ```env
    ASSEMBLYAI_API_KEY=your_assemblyai_key
    GOOGLE_API_KEY=your_gemini_key
    # OPENAI_API_KEY=your_openai_key  # Optional
    # GROQ_API_KEY=your_groq_key      # Optional
    # OPENROUTER_API_KEY=...          # Optional
    ```

## Usage

Run the tool via the command line interface (CLI).

### 1. Process a YouTube Video
```bash
python src/main.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --series "The Book of Romans" --preacher "Pastor John Doe" --provider gemini
```

### 2. Process a Local Audio File
```bash
python src/main.py --file "path/to/sermon.mp3" --logo "assets/logo.png" --series "Sunday Service" --preacher "Pastor Jane Doe"
```

### CLI Arguments
| Argument | Description | Default |
| :--- | :--- | :--- |
| `--url` | YouTube URL to download audio from. | None |
| `--file` | Path to a local audio file (MP3/WAV). | None |
| `--provider` | AI Provider to use (`gemini`, `openai`, `groq`). | `gemini` |
| `--series` | Title of the sermon series for the PDF header. | "Sermon Series" |
| `--preacher` | Name of the preacher for the cover page. | "" |
| `--bible-version` | Bible version for scriptures (`kjv`, `web`, `rvr`, etc.). | `kjv` |
| `--logo` | Path to a church logo image (PNG/JPG) for branding. | None |

## Output

The generated PDF study guide will be saved in the `output/` directory:
`output/The_Book_of_Romans.pdf`

## Customization

- **Fonts**: The tool uses the **Montserrat** font family. Ensure font files are in `assets/fonts/`.
- **Branding**: The PDF uses a static premium palette (Navy primary, Rose accent). You can still provide a logo via `--logo` to display on the cover, but colors are not derived from the logo.
