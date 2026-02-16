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

# All 21 LGAs with ACCURATE coordinates (centroids) - VERIFIED
# Sources: Google Maps, Nigeria LGA boundary data, INEC official records
KEBBI_LGAS = [
    {"name": "Aleiro",        "lat": 12.3167, "lon": 4.6833, "risk": "medium"},      # Northeastern Kebbi
    {"name": "Arewa Dandi",   "lat": 12.6000, "lon": 4.4333, "risk": "low"},        # North of Argungu
    {"name": "Argungu",       "lat": 12.7448, "lon": 4.5251, "risk": "medium"},      # Historic town
    {"name": "Augie",         "lat": 12.8900, "lon": 4.2000, "risk": "high"},        # Northwestern border
    {"name": "Bagudo",        "lat": 11.4000, "lon": 4.2167, "risk": "medium"},      # Western area
    {"name": "Birnin Kebbi",  "lat": 12.4539, "lon": 4.1975, "risk": "low"},         # State capital
    {"name": "Bunza",         "lat": 12.6667, "lon": 4.0167, "risk": "medium"},      # North of Birnin Kebbi
    {"name": "Dandi",         "lat": 11.7333, "lon": 3.8833, "risk": "high"},        # Western border
    {"name": "Fakai",         "lat": 11.5500, "lon": 4.4000, "risk": "critical"},    # Southern corridor
    {"name": "Gwandu",        "lat": 12.5000, "lon": 4.4667, "risk": "medium"},      # East of Birnin Kebbi
    {"name": "Jega",          "lat": 12.2236, "lon": 4.3791, "risk": "low"},         # Major commercial center
    {"name": "Kalgo",         "lat": 12.3167, "lon": 4.2000, "risk": "low"},         # North-central
    {"name": "Koko/Besse",    "lat": 11.4167, "lon": 4.1333, "risk": "high"},        # Western area
    {"name": "Maiyama",       "lat": 12.0833, "lon": 4.6167, "risk": "medium"},      # East of Argungu
    {"name": "Ngaski",        "lat": 10.9667, "lon": 4.0833, "risk": "high"},        # Southwestern corner
    {"name": "Sakaba",        "lat": 11.0833, "lon": 5.6167, "risk": "critical"},    # EASTERN - Niger State border (CORRECTED)
    {"name": "Shanga",        "lat": 11.2000, "lon": 4.5833, "risk": "high"},        # Western area, Kainji Lake
    {"name": "Suru",          "lat": 11.6667, "lon": 4.1667, "risk": "medium"},      # Central-west
    {"name": "Wasagu/Danko",  "lat": 11.3500, "lon": 5.4500, "risk": "critical"},    # EASTERN - Zamfara border (CORRECTED)
    {"name": "Yauri",         "lat": 10.8333, "lon": 4.7667, "risk": "high"},        # Southernmost, Kainji Dam
    {"name": "Zuru",          "lat": 11.4308, "lon": 5.2309, "risk": "critical"},    # SOUTHEASTERN - Sokoto/Zamfara border
]

RISK_LEVELS = {
    "critical": {"color": "#ff0040", "weight": 4, "label": "CRITICAL"},
    "high":     {"color": "#ff6600", "weight": 3, "label": "HIGH"},
    "medium":   {"color": "#f0ff00", "weight": 2, "label": "MEDIUM"},
    "low":      {"color": "#00ff80", "weight": 1, "label": "LOW"},
}
