"""TikTok upload module."""

from typing import Optional, Dict
from agent.logger import setup_logger
from agent.config import TIKTOK_COOKIES_PATH

logger = setup_logger(__name__)


class TikTokUploader:
    """Upload videos to TikTok using tiktok-uploader library."""
    
    def __init__(self, cookies_path: str = TIKTOK_COOKIES_PATH):
        """
        Initialize TikTok uploader.
        
        Args:
            cookies_path: Path to TikTok cookies.json file
        """
        self.cookies_path = cookies_path
        self.uploader = None
        logger.info(f"TikTokUploader initialized with cookies from: {cookies_path}")
    
    def initialize(self) -> None:
        """
        Initialize TikTok uploader with cookies.
        
        Requires cookies.json file. See README for how to export TikTok cookies.
        """
        try:
            from TikTokApi import TikTokApi
            import json
            
            with open(self.cookies_path, 'r') as f:
                cookies = json.load(f)
            
            self.uploader = TikTokApi(cookies=cookies)
            logger.info("TikTok uploader initialized successfully")
        
        except FileNotFoundError:
            logger.error(f"Cookies file not found: {self.cookies_path}")
            logger.error("Export TikTok cookies and save to cookies.json")
            raise
        except Exception as e:
            logger.error(f"TikTok initialization failed: {str(e)}")
            raise
    
    def upload(
        self,
        video_path: str,
        caption: str,
        hashtags: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Upload video to TikTok.
        
        Args:
            video_path: Path to video file
            caption: Video caption
            hashtags: Hashtags to include in caption
        
        Returns:
            Dictionary with upload status and video info
        """
        if not self.uploader:
            raise RuntimeError("Not initialized. Call initialize() first.")
        
        try:
            from pathlib import Path
            
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            full_caption = caption
            if hashtags:
                full_caption = f"{caption} {hashtags}"
            
            logger.info(f"Uploading to TikTok: {caption[:50]}...")
            
            # NOTE: Actual upload implementation depends on tiktok-uploader version
            # This is a placeholder for the API
            response = self.uploader.upload_video(
                video_path=video_path,
                caption=full_caption,
                video_cover=None,
                allow_duet=True,
                allow_stitch=True,
                privacy='public',
            )
            
            logger.info("Video uploaded to TikTok successfully")
            return {
                'status': 'success',
                'response': response,
            }
        
        except Exception as e:
            logger.error(f"Upload to TikTok failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
            }
