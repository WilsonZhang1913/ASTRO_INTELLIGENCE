import os

# OpenRouter base URL and API key are loaded from environment.
# NEVER commit real API keys.
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Ranked list of free chatbot models (best first)
CHATBOT_MODELS = [
    "deepseek/deepseek-chat-v3.1:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
]

if not API_KEY:
    # Fail fast with a clear error message so it's obvious in logs.
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set. Configure it as an environment variable."
    )
