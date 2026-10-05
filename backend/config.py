import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
).rstrip("/")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:7b"
)

SEMANTIC_SCHOLAR_API_KEY = os.getenv(
    "SEMANTIC_SCHOLAR_API_KEY",
    ""
)

WEB_SEARCH_API_KEY = os.getenv(
    "WEB_SEARCH_API_KEY",
    ""
)

DATABASE_PATH = BASE_DIR / "data" / "research.db"

FRONTEND_DIR = BASE_DIR / "frontend"

MAX_WEB_RESULTS = 6
MAX_ARXIV_RESULTS = 6
MAX_SEMANTIC_RESULTS = 6

SOURCE_READ_TIMEOUT = 30
OLLAMA_TIMEOUT = 180