from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

AI_LOCAL_TIMEOUT = float(os.getenv("AI_LOCAL_TIMEOUT", "90"))
AI_ONLINE_TIMEOUT = float(os.getenv("AI_ONLINE_TIMEOUT", "30"))
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1200"))

AI_ALLOW_ONLINE = os.getenv("AI_ALLOW_ONLINE", "true").lower() == "true"
