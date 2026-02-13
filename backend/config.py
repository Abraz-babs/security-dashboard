"""CITADEL KEBBI - Configuration Module"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# ──── API Keys ────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

COPERNICUS_CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID", "")
COPERNICUS_CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET", "")

NASA_FIRMS_KEY = os.getenv("NASA_FIRMS_KEY", "")

N2YO_API_KEY = os.getenv("N2YO_API_KEY", "")

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

# ──── App Settings ────
APP_NAME = os.getenv("APP_NAME", "CITADEL KEBBI")
APP_VERSION = os.getenv("APP_VERSION", "2.1.0")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ──── Kebbi State Constants ────
KEBBI_CENTER = {"lat": 12.4539, "lon": 4.1975}
KEBBI_BBOX = {"min_lat": 10.8, "max_lat": 13.3, "min_lon": 3.5, "max_lon": 5.9}

# All 21 LGAs with accurate coordinates (centroids)
KEBBI_LGAS = [
    {"name": "Aleiro",        "lat": 12.2833, "lon": 4.5167, "risk": "medium"},
    {"name": "Arewa Dandi",   "lat": 12.0167, "lon": 4.3000, "risk": "low"},
    {"name": "Argungu",       "lat": 12.7500, "lon": 4.5167, "risk": "medium"},
    {"name": "Augie",         "lat": 12.8667, "lon": 4.0667, "risk": "high"},
    {"name": "Bagudo",        "lat": 11.9500, "lon": 4.2333, "risk": "medium"},
    {"name": "Birnin Kebbi",  "lat": 12.4539, "lon": 4.1975, "risk": "low"},
    {"name": "Bunza",         "lat": 12.4833, "lon": 4.0333, "risk": "medium"},
    {"name": "Dandi",         "lat": 11.6333, "lon": 3.9500, "risk": "high"},
    {"name": "Fakai",         "lat": 11.3833, "lon": 3.8833, "risk": "critical"},
    {"name": "Gwandu",        "lat": 12.5000, "lon": 4.4667, "risk": "medium"},
    {"name": "Jega",          "lat": 12.2167, "lon": 4.3833, "risk": "low"},
    {"name": "Kalgo",         "lat": 12.3167, "lon": 4.2000, "risk": "low"},
    {"name": "Koko/Besse",    "lat": 11.4167, "lon": 4.1333, "risk": "high"},
    {"name": "Maiyama",       "lat": 12.0333, "lon": 4.5667, "risk": "medium"},
    {"name": "Ngaski",        "lat": 11.6500, "lon": 4.2000, "risk": "high"},
    {"name": "Sakaba",        "lat": 11.2167, "lon": 3.9833, "risk": "critical"},
    {"name": "Shanga",        "lat": 11.2000, "lon": 3.6333, "risk": "high"},
    {"name": "Suru",          "lat": 11.8000, "lon": 4.1500, "risk": "medium"},
    {"name": "Wasagu/Danko",  "lat": 11.0667, "lon": 3.8167, "risk": "critical"},
    {"name": "Yauri",         "lat": 10.8333, "lon": 4.7667, "risk": "high"},
    {"name": "Zuru",          "lat": 11.4333, "lon": 5.2333, "risk": "critical"},
]

RISK_LEVELS = {
    "critical": {"color": "#ff0040", "weight": 4, "label": "CRITICAL"},
    "high":     {"color": "#ff6600", "weight": 3, "label": "HIGH"},
    "medium":   {"color": "#f0ff00", "weight": 2, "label": "MEDIUM"},
    "low":      {"color": "#00ff80", "weight": 1, "label": "LOW"},
}
