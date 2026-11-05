"""Read configuration without printing credentials."""
import os
from pathlib import Path
from dotenv import load_dotenv


def get_settings():
    load_dotenv(Path(__file__).with_name(".env"))
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    key = os.getenv("SUPABASE_SECRET_KEY", "").strip()
    if not url.startswith("https://") or "YOUR_PROJECT" in url:
        raise ValueError("Set your project HTTPS URL in .env (not the dashboard URL).")
    if not key.startswith("sb_secret_"):
        raise ValueError("Set SUPABASE_SECRET_KEY to your own project's sb_secret_ key.")
    return url, key



