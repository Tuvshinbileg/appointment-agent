"""
Configuration settings for the Appointment Booking System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv()

# Database settings
# SQLite (default): sqlite:///./bookings.db
# PostgreSQL: postgresql://user:password@localhost:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bookings.db")

# Legacy JSON path (kept for backward compatibility)
BOOKINGS_DB_PATH = os.getenv("BOOKINGS_DB_PATH", str(BASE_DIR / "bookings.json"))

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_RELOAD = os.getenv("API_RELOAD", "False").lower() == "true"

# LLM settings
# Provider options: "openai", "gemini", "ollama" (not recommended)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)  # For custom OpenAI-compatible endpoints

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # or gemini-1.5-pro

# Legacy Ollama (local only - not recommended for production)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Business hours
BUSINESS_START_HOUR = int(os.getenv("BUSINESS_START_HOUR", 9))
BUSINESS_END_HOUR = int(os.getenv("BUSINESS_END_HOUR", 18))

# Service definitions with default durations (in minutes)
SERVICES = {
    "үс засалт": 60,
    "шүдний үзлэг": 45,
    "массаж": 90,
    "маникюр": 45,
    "педикюр": 60,
    "косметик": 120,
    "эмчилгээ": 60,
    "сэтгэл зүйч": 60,
}

# CORS settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Application metadata
APP_TITLE = "Appointment Booking Chat Agent"
APP_DESCRIPTION = "AI-powered booking system with Mongolian language support"
APP_VERSION = "1.0.0"
