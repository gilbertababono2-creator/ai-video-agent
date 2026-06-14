import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
DOWNLOAD_DIR = PROJECT_ROOT / "downloads"
TEMP_DIR = PROJECT_ROOT / "temp"

# Create directories if they don't exist
for directory in [OUTPUT_DIR, DOWNLOAD_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# YouTube OAuth
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# TikTok
TIKTOK_COOKIES_PATH = os.getenv("TIKTOK_COOKIES_PATH", str(TEMP_DIR / "tiktok_cookies.json"))

# Facebook
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_API_VERSION = "v18.0"

# Video Settings
VIDEO_RESOLUTION = (1080, 1920)  # 9:16 aspect ratio
VIDEO_FPS = 30
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "128k"
VIDEO_BITRATE = "5000k"

# YouTube Shorts constraints
YOUTUBE_SHORTS_MAX_DURATION = 60  # seconds
YOUTUBE_SHORTS_MIN_DURATION = 15  # seconds

# TikTok constraints
TIKTOK_MAX_DURATION = 600  # seconds (10 minutes)
TIKTOK_MIN_DURATION = 3  # seconds

# Facebook Reels constraints
FACEBOOK_REELS_MAX_DURATION = 90  # seconds
FACEBOOK_REELS_MIN_DURATION = 3  # seconds

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
