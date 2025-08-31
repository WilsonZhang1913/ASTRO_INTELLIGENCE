import os
from pathlib import Path

# Load environment variables from a local .env if present (for local dev)
def _load_env_best_effort() -> None:
    """Load env vars from a .env file using python-dotenv if available,
    otherwise perform a minimal manual parse. Looks in repo root and CWD.
    """
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [repo_root / ".env", Path.cwd() / ".env"]

    # Try python-dotenv first if available
    try:
        from dotenv import load_dotenv  # type: ignore
        # First, call without args to let it search upwards from CWD
        load_dotenv()
        # Then explicitly load known locations to be safe
        for p in candidates:
            load_dotenv(p, override=False)
        return
    except Exception:
        pass

    # Fallback: minimal manual parser
    for p in candidates:
        try:
            if p.exists():
                for line in p.read_text().splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key, val)
        except Exception:
            # Ignore parsing errors silently; real env still applies
            continue

_load_env_best_effort()

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
