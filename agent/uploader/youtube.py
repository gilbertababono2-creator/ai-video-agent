"""YouTube Shorts upload module."""

import os
from pathlib import Path
from typing import Optional, Dict
from agent.logger import setup_logger
from agent.config import YOUTUBE_SCOPES, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET

logger = setup_logger(__name__)


class YouTubeUploader:
    """Upload videos to YouTube Shorts using Official Data API v3."""
    
    def __init__(self):
        """
        Initialize YouTube uploader.
        
        Requires YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET environment variables.
        """
        self.scopes = YOUTUBE_SCOPES
        self.youtube = None
        logger.info("YouTubeUploader initialized")
    
    def authenticate(self) -> None:
        """
        Authenticate with YouTube using OAuth2.
        
        This creates a local browser session for user authorization.
        """
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            import pickle
            
            creds = None
            token_file = "youtube_token.pickle"
            
            # Check if we have a cached token
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
                logger.info("Loaded cached YouTube credentials")
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    logger.info("Refreshed YouTube credentials")
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'youtube_credentials.json',
                        self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                    logger.info("Obtained new YouTube credentials")
                
                # Save credentials for future use
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            from googleapiclient.discovery import build
            self.youtube = build('youtube', 'v3', credentials=creds)
            logger.info("YouTube authentication successful")
        
        except FileNotFoundError:
            logger.error("youtube_credentials.json not found")
            logger.error("Follow README setup instructions to obtain OAuth credentials")
            raise
        except Exception as e:
            logger.error(f"YouTube authentication failed: {str(e)}")
            raise
    
    def upload(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: Optional[list] = None,
        made_for_kids: bool = False,
    ) -> Dict[str, str]:
        """
        Upload video to YouTube Shorts.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags/hashtags
            made_for_kids: Mark video as made for kids
        
        Returns:
            Dictionary with video_id and upload status
        """
        if not self.youtube:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            logger.info(f"Uploading to YouTube Shorts: {title}")
            
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '24',  # Shorts category
                },
                'status': {
                    'privacyStatus': 'public',
                    'madeForKids': made_for_kids,
                },
            }
            
            from googleapiclient.http import MediaFileUpload
            
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True,
            )
            
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media,
            )
            
            response = request.execute()
            video_id = response['id']
            
            logger.info(f"Video uploaded successfully. Video ID: {video_id}")
            return {
                'status': 'success',
                'video_id': video_id,
                'url': f'https://www.youtube.com/shorts/{video_id}',
            }
        
        except Exception as e:
            logger.error(f"Upload to YouTube failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
            }
