"""
AI Video Agent - Generate and upload faceless videos to multiple platforms.

Supported platforms:
- YouTube Shorts
- TikTok
- Facebook Reels
"""

__version__ = "0.1.0"
__author__ = "Gilbert Ababono"

from agent.video_generator import VideoGenerator
from agent.uploader import YouTubeUploader, TikTokUploader, FacebookUploader

__all__ = [
    "VideoGenerator",
    "YouTubeUploader",
    "TikTokUploader",
    "FacebookUploader",
]
