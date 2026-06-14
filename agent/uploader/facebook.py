"""Facebook Reels upload module."""

import requests
from typing import Optional, Dict
from agent.logger import setup_logger
from agent.config import (
    FACEBOOK_PAGE_ACCESS_TOKEN,
    FACEBOOK_PAGE_ID,
    FACEBOOK_API_VERSION,
)

logger = setup_logger(__name__)


class FacebookUploader:
    """Upload videos to Facebook Reels using Official Graph API."""
    
    def __init__(
        self,
        page_access_token: str = FACEBOOK_PAGE_ACCESS_TOKEN,
        page_id: str = FACEBOOK_PAGE_ID,
        api_version: str = FACEBOOK_API_VERSION,
    ):
        """
        Initialize Facebook uploader.
        
        Args:
            page_access_token: Facebook Page Access Token
            page_id: Facebook Page ID
            api_version: Facebook Graph API version
        """
        if not page_access_token or not page_id:
            raise ValueError(
                "FACEBOOK_PAGE_ACCESS_TOKEN and FACEBOOK_PAGE_ID required"
            )
        
        self.page_access_token = page_access_token
        self.page_id = page_id
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"
        logger.info(f"FacebookUploader initialized for page: {page_id}")
    
    def upload(
        self,
        video_path: str,
        title: str,
        description: str = "",
        hashtags: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Upload video to Facebook Reels.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            hashtags: Hashtags to include
        
        Returns:
            Dictionary with upload status and video info
        """
        try:
            from pathlib import Path
            
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            logger.info(f"Uploading to Facebook Reels: {title}")
            
            # Prepare full description with hashtags
            full_description = description
            if hashtags:
                full_description = f"{description} {hashtags}".strip()
            
            # Upload video using resumable upload
            upload_url = f"{self.base_url}/{self.page_id}/video_reels"
            
            with open(video_path, 'rb') as video_file:
                files = {'upload_file': video_file}
                data = {
                    'access_token': self.page_access_token,
                    'title': title,
                    'description': full_description,
                }
                
                response = requests.post(upload_url, files=files, data=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                video_id = result.get('id')
                logger.info(f"Video uploaded to Facebook Reels. ID: {video_id}")
                return {
                    'status': 'success',
                    'video_id': video_id,
                    'url': f'https://www.facebook.com/watch/?v={video_id}',
                }
            else:
                error_msg = response.text
                logger.error(f"Facebook upload failed: {error_msg}")
                return {
                    'status': 'failed',
                    'error': error_msg,
                }
        
        except Exception as e:
            logger.error(f"Upload to Facebook failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
            }
