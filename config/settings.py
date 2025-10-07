# config/settings.py - Application configuration and environment settings

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_SERVER", "localhost"),
    "database": os.getenv("DB_NAME", "fitbridge"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": int(os.getenv("DB_PORT", 5432))
}

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Application settings
APP_TITLE = "FitBridge Chatbot API"
APP_DESCRIPTION = "AI-powered gym search and fitness assistant for Vietnam"
APP_VERSION = "1.0.0"

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000"
]

# Default search parameters
DEFAULT_SEARCH_RADIUS_KM = 5
MAX_SEARCH_RADIUS_KM = 20

# Conversation settings
MAX_CONVERSATION_HISTORY = 10