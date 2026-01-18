import os
from dotenv import load_dotenv

load_dotenv()

def get_llm_client():
    provider = os.getenv('LLM_PROVIDER', 'gemini')
    api_key = os.getenv('LLM_API_KEY')
    model = os.getenv('LLM_MODEL')

    if provider == 'gemini':
        from google import genai
        client = genai.Client(api_key=api_key)
        return client, provider
        
    elif provider == 'openai':
        import openai
        client = openai.OpenAI(api_key=api_key)
        return client, provider
        
    elif provider == 'openrouter':
        import openai
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        return client, provider
        
    elif provider == 'groq':
        from groq import Groq
        client = Groq(api_key=api_key)
        return client, provider
        
    else:
        raise ValueError(f"Unsupported provider: {provider}")

