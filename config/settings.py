"""Configuration settings for the LinkedIn AI Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Ollama Configuration (Local LLM)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")  # Change to your preferred model

# LinkedIn Configuration
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_ID = os.getenv("LINKEDIN_PERSON_ID")
LINKEDIN_API_BASE_URL = "https://api.linkedin.com/v2"

# Agent Configuration
POSTING_TIME = os.getenv("POSTING_TIME", "10:00")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
TOTAL_DAYS = 90

# File paths
CURRICULUM_FILE = DATA_DIR / "curriculum.json"
HISTORY_FILE = DATA_DIR / "posted_history.json"
STATE_FILE = DATA_DIR / "agent_state.json"

# Content settings
MAX_POST_LENGTH = 3000  # LinkedIn character limit
MIN_POST_LENGTH = 500
HASHTAG_COUNT = 5
