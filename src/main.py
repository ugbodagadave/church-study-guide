import os
import assemblyai as aai
from dotenv import load_dotenv
from providers.llm_factory import get_llm_client

load_dotenv()

# Configuration
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
aai.settings.api_key = ASSEMBLYAI_API_KEY

# Initialize LLM (can swap provider anytime via .env)
llm_client, provider_type = get_llm_client()

print(f"✓ AssemblyAI configured")
print(f"✓ LLM Provider: {provider_type} ({os.getenv('LLM_MODEL')})")
print(f"✓ Ready to process sermons")

# TODO: Implement:
# 1. download_audio(url) -> MP3 file
# 2. transcribe_audio(file_path) -> text (AssemblyAI)
# 3. generate_devotional(transcript) -> structured content (LLM)
# 4. design_pdf(devotional_content) -> PDF file (fpdf2)

