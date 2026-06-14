"""
YouTube Shorts uploader using OAuth2 and YouTube Data API v3.

Handles:
- OAuth2 authentication and token refresh
- Video upload with resumable upload support
- Metadata management (title, description, tags, privacy)
- Playlist management
- Upload progress tracking
"""

import os
import pickle
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from agent.logger import setup_logger
from agent.config import (
    OUTPUT_DIR, TEMP_DIR,
    YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_SCOPES
)

logger = setup_logger(__name__, "youtube_uploader.log")

# YouTube API constants
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


class YouTubeUploader:
    """Upload videos to YouTube Shorts using the official Data API."""
    
    def __init__(self, credentials_file: str = "youtube_credentials.json"):
        """
        Initialize YouTube uploader.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
        """
        self.credentials_file = credentials_file
        self.token_file = "youtube_token.pickle"
        self.credentials = None
        self.youtube_service = None
        
        logger.info("YouTube Uploader initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API using OAuth2.
        
        Returns:
            True if authentication successful
        
        Raises:
            FileNotFoundError: If credentials file not found
        """
        logger.info("Authenticating with YouTube API...")
        
        try:
            # Try to load existing token
            if Path(self.token_file).exists():
                logger.debug("Loading existing token")
                with open(self.token_file, "rb") as token:
                    self.credentials = pickle.load(token)
            
            # Refresh or create new credentials
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                logger.debug("Refreshing expired token")
                self.credentials.refresh(Request())
            elif not self.credentials or not self.credentials.valid:
                logger.debug("Creating new credentials")
                self._get_new_credentials()
            
            # Save token for next time
            with open(self.token_file, "wb") as token:
                pickle.dump(self.credentials, token)
            
            # Build YouTube service
            self.youtube_service = build(
                YOUTUBE_API_SERVICE_NAME,
                YOUTUBE_API_VERSION,
                credentials=self.credentials
            )
            
            logger.info("Authentication successful")
            return True
        
        except FileNotFoundError:
            logger.error(f"Credentials file not found: {self.credentials_file}")
            raise FileNotFoundError(
                f"Please download OAuth2 credentials from Google Cloud Console "
                f"and save as {self.credentials_file}"
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        category_id: str = "24",  # 24 = Entertainment (YouTube Shorts category)
        privacy_status: str = "private",  # private, unlisted, public
        thumbnail_path: Optional[str] = None,
        playlist_id: Optional[str] = None,
    ) -> Dict:
        """
        Upload a video to YouTube Shorts.
        
        Args:
            video_path: Path to video file (MP4)
            title: Video title (max 100 characters)
            description: Video description (max 5000 characters)
            tags: List of tags/keywords
            category_id: YouTube category ID (24=Entertainment, 22=People & Blogs, etc.)
            privacy_status: 'private', 'unlisted', or 'public'
            thumbnail_path: Optional path to custom thumbnail
            playlist_id: Optional playlist ID to add video to
        
        Returns:
            Dictionary with upload result including video ID and URL
        
        Raises:
            FileNotFoundError: If video file not found
            RuntimeError: If upload fails
        """
        logger.info(f"Uploading video to YouTube Shorts: {title}")
        
        if not self.youtube_service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        try:
            # Validate dimensions
            file_size = Path(video_path).stat().st_size
            max_size = 128 * 1024 * 1024  # 128MB limit for Shorts
            if file_size > max_size:
                logger.warning(f"Video size {file_size / 1024 / 1024:.1f}MB may exceed limits")
            
            # Prepare video metadata
            body = {
                "snippet": {
                    "title": title[:100],  # YouTube limit
                    "description": description[:5000],  # YouTube limit
                    "tags": tags or [],
                    "categoryId": category_id,
                    "defaultLanguage": "en",
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False,
                    "madeForKids": False,
                }
            }
            
            logger.debug(f"Video metadata: {json.dumps(body, indent=2)}")
            
            # Upload video file
            logger.info(f"Starting file upload: {video_path}")
            media = MediaFileUpload(
                video_path,
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024 * 1024  # 1MB chunks
            )
            
            # Create insert request
            insert_request = self.youtube_service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            # Execute upload with progress tracking
            response = self._execute_upload(insert_request)
            
            video_id = response["id"]
            logger.info(f"Video uploaded successfully. ID: {video_id}")
            
            # Set thumbnail if provided
            if thumbnail_path and Path(thumbnail_path).exists():
                try:
                    self._set_thumbnail(video_id, thumbnail_path)
                except Exception as e:
                    logger.warning(f"Failed to set thumbnail: {str(e)}")
            
            # Add to playlist if specified
            if playlist_id:
                try:
                    self._add_to_playlist(video_id, playlist_id)
                except Exception as e:
                    logger.warning(f"Failed to add to playlist: {str(e)}")
            
            # Build result
            result = {
                "success": True,
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "shorts_url": f"https://www.youtube.com/shorts/{video_id}",
                "upload_time": datetime.now().isoformat(),
                "title": title,
                "privacy_status": privacy_status,
            }
            
            logger.info(f"Upload result: {json.dumps(result, indent=2)}")
            return result
        
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise RuntimeError(f"Failed to upload video: {str(e)}")
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise
    
    def update_video(
        self,
        video_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        privacy_status: Optional[str] = None,
    ) -> bool:
        """
        Update video metadata after upload.
        
        Args:
            video_id: YouTube video ID
            title: New title
            description: New description
            tags: New tags
            privacy_status: New privacy status
        
        Returns:
            True if update successful
        """
        logger.info(f"Updating video metadata: {video_id}")
        
        if not self.youtube_service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            # Get current video
            request = self.youtube_service.videos().list(
                part="snippet,status",
                id=video_id
            )
            response = request.execute()
            
            if not response["items"]:
                raise ValueError(f"Video not found: {video_id}")
            
            video = response["items"][0]
            
            # Update fields
            if title:
                video["snippet"]["title"] = title[:100]
            if description:
                video["snippet"]["description"] = description[:5000]
            if tags is not None:
                video["snippet"]["tags"] = tags
            if privacy_status:
                video["status"]["privacyStatus"] = privacy_status
            
            # Execute update
            update_request = self.youtube_service.videos().update(
                part="snippet,status",
                body=video
            )
            update_request.execute()
            
            logger.info(f"Video updated: {video_id}")
            return True
        
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise
    
    def get_video_info(self, video_id: str) -> Dict:
        """
        Get information about a video.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Video information dictionary
        """
        logger.info(f"Getting video info: {video_id}")
        
        if not self.youtube_service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            request = self.youtube_service.videos().list(
                part="snippet,status,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response["items"]:
                raise ValueError(f"Video not found: {video_id}")
            
            video = response["items"][0]
            
            info = {
                "id": video_id,
                "title": video["snippet"]["title"],
                "description": video["snippet"]["description"],
                "channel_id": video["snippet"]["channelId"],
                "published_at": video["snippet"]["publishedAt"],
                "status": video["status"]["privacyStatus"],
                "view_count": int(video["statistics"].get("viewCount", 0)),
                "like_count": int(video["statistics"].get("likeCount", 0)),
                "comment_count": int(video["statistics"].get("commentCount", 0)),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "shorts_url": f"https://www.youtube.com/shorts/{video_id}",
            }
            
            logger.info(f"Video info: {json.dumps(info, indent=2)}")
            return info
        
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise
    
    def get_channel_info(self) -> Dict:
        """
        Get authenticated user's channel information.
        
        Returns:
            Channel info dictionary
        """
        logger.info("Getting channel info")
        
        if not self.youtube_service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            request = self.youtube_service.channels().list(
                part="snippet,statistics",
                mine=True
            )
            response = request.execute()
            
            if not response["items"]:
                raise ValueError("No channel found for authenticated user")
            
            channel = response["items"][0]
            
            info = {
                "channel_id": channel["id"],
                "title": channel["snippet"]["title"],
                "description": channel["snippet"]["description"],
                "url": f"https://www.youtube.com/channel/{channel['id']}",
                "subscriber_count": int(channel["statistics"].get("subscriberCount", 0)),
                "view_count": int(channel["statistics"].get("viewCount", 0)),
                "video_count": int(channel["statistics"].get("videoCount", 0)),
            }
            
            logger.info(f"Channel info: {json.dumps(info, indent=2)}")
            return info
        
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise
    
    # ==================== Private Helper Methods ====================
    
    def _get_new_credentials(self):
        """Create new OAuth2 credentials."""
        if not Path(self.credentials_file).exists():
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_file}\n"
                f"Please download it from Google Cloud Console and place it in the project root."
            )
        
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file,
            scopes=YOUTUBE_SCOPES
        )
        
        logger.info("Opening browser for OAuth2 authorization...")
        self.credentials = flow.run_local_server(port=8080)
    
    def _execute_upload(self, insert_request):
        """Execute resumable upload with progress tracking."""
        response = None
        attempt = 0
        max_retries = 3
        
        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.debug(f"Upload progress: {progress}%")
            except HttpError as e:
                attempt += 1
                if e.resp.status in [500, 502, 503, 504] and attempt < max_retries:
                    logger.warning(f"Server error, retrying... (attempt {attempt}/{max_retries})")
                    continue
                else:
                    raise
        
        return response
    
    def _set_thumbnail(self, video_id: str, thumbnail_path: str):
        """Set custom thumbnail for video."""
        logger.info(f"Setting thumbnail: {thumbnail_path}")
        
        try:
            self.youtube_service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
            
            logger.info(f"Thumbnail set for video: {video_id}")
        except Exception as e:
            logger.warning(f"Failed to set thumbnail: {str(e)}")
            raise
    
    def _add_to_playlist(self, video_id: str, playlist_id: str):
        """Add video to playlist."""
        logger.info(f"Adding video to playlist: {playlist_id}")
        
        try:
            self.youtube_service.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()
            
            logger.info(f"Video added to playlist: {playlist_id}")
        except Exception as e:
            logger.warning(f"Failed to add to playlist: {str(e)}")
            raise
