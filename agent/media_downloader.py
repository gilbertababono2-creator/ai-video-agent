"""
Media downloader for fetching videos and images from various sources.

Handles:
- YouTube video/shorts downloading
- TikTok video downloading
- Generic video/image URL downloads
- Clip extraction and frame extraction
- Source validation and error handling
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from urllib.parse import urlparse
import json
import time

from agent.logger import setup_logger
from agent.config import DOWNLOAD_DIR, TEMP_DIR

logger = setup_logger(__name__, "media_downloader.log")


class MediaDownloader:
    """Download and process media from various sources."""
    
    def __init__(self):
        """Initialize media downloader."""
        self.download_dir = DOWNLOAD_DIR
        self.temp_dir = TEMP_DIR
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        logger.info(f"Media Downloader initialized")
        self._verify_dependencies()
    
    def _verify_dependencies(self):
        """Verify required dependencies are installed."""
        try:
            import yt_dlp
            logger.debug("yt-dlp available")
        except ImportError:
            logger.warning("yt-dlp not installed. Install with: pip install yt-dlp")
        
        # Check ffmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            logger.debug("FFmpeg available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("FFmpeg not found. Install with: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
    
    def download_video(
        self,
        url: str,
        output_format: str = "mp4",
        max_duration: Optional[int] = None,
    ) -> str:
        """
        Download a video from URL (YouTube, TikTok, or generic).
        
        Args:
            url: Video URL
            output_format: Output format (mp4, webm, etc.)
            max_duration: Maximum duration in seconds (for trimming)
        
        Returns:
            Path to downloaded video file
        
        Raises:
            ValueError: If URL is invalid
            RuntimeError: If download fails
        """
        logger.info(f"Downloading video from: {url}")
        
        if not self._validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        try:
            # Determine source type
            source_type = self._get_source_type(url)
            logger.debug(f"Detected source type: {source_type}")
            
            # Download based on source
            if source_type == "youtube":
                return self._download_youtube(url, output_format, max_duration)
            elif source_type == "tiktok":
                return self._download_tiktok(url, output_format, max_duration)
            else:
                return self._download_generic(url, output_format, max_duration)
        
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise
    
    def download_images(
        self,
        urls: List[str],
        output_format: str = "png",
    ) -> List[str]:
        """
        Download multiple images from URLs.
        
        Args:
            urls: List of image URLs
            output_format: Output format (png, jpg, etc.)
        
        Returns:
            List of paths to downloaded images
        """
        logger.info(f"Downloading {len(urls)} images")
        
        downloaded_paths = []
        for i, url in enumerate(urls):
            try:
                logger.debug(f"Downloading image {i+1}/{len(urls)}: {url}")
                path = self._download_image(url, output_format)
                downloaded_paths.append(path)
            except Exception as e:
                logger.warning(f"Failed to download image {url}: {str(e)}")
                continue
        
        logger.info(f"Downloaded {len(downloaded_paths)}/{len(urls)} images")
        return downloaded_paths
    
    def extract_clip(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_format: str = "mp4",
    ) -> str:
        """
        Extract a clip from a video file.
        
        Args:
            video_path: Path to input video
            start_time: Start time in seconds
            end_time: End time in seconds
            output_format: Output format
        
        Returns:
            Path to extracted clip
        """
        logger.info(f"Extracting clip from {start_time}s to {end_time}s")
        
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        try:
            duration = end_time - start_time
            output_filename = f"clip_{start_time}_{end_time}.{output_format}"
            output_path = self.temp_dir / output_filename
            
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-ss", str(start_time),
                "-t", str(duration),
                "-c", "copy",  # Copy without re-encoding for speed
                "-y",  # Overwrite output
                str(output_path)
            ]
            
            logger.debug(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=True, check=True)
            
            logger.info(f"Clip extracted: {output_path}")
            return str(output_path)
        
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to extract clip: {str(e)}")
    
    def extract_frames(
        self,
        video_path: str,
        frame_rate: float = 1.0,
        start_time: float = 0,
        end_time: Optional[float] = None,
        output_format: str = "jpg",
    ) -> List[str]:
        """
        Extract frames from a video as images.
        
        Args:
            video_path: Path to input video
            frame_rate: Frames per second to extract
            start_time: Start time in seconds
            end_time: End time in seconds (None = entire video)
            output_format: Image format (jpg, png, etc.)
        
        Returns:
            List of paths to extracted frame images
        """
        logger.info(f"Extracting frames from {video_path} at {frame_rate} fps")
        
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        try:
            # Create frames directory
            frames_dir = self.temp_dir / "frames"
            frames_dir.mkdir(exist_ok=True)
            
            # Build ffmpeg command
            output_pattern = frames_dir / f"frame_%04d.{output_format}"
            
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-ss", str(start_time),
            ]
            
            if end_time:
                duration = end_time - start_time
                cmd.extend(["-t", str(duration)])
            
            cmd.extend([
                "-vf", f"fps={frame_rate}",
                "-y",  # Overwrite
                str(output_pattern)
            ])
            
            logger.debug(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=True, check=True)
            
            # List extracted frames
            frame_files = sorted(frames_dir.glob(f"frame_*.{output_format}"))
            logger.info(f"Extracted {len(frame_files)} frames")
            
            return [str(f) for f in frame_files]
        
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to extract frames: {str(e)}")
    
    def get_video_metadata(self, video_path: str) -> Dict:
        """
        Get metadata from a video file (duration, resolution, etc.).
        
        Args:
            video_path: Path to video file
        
        Returns:
            Dictionary with video metadata
        """
        logger.info(f"Getting video metadata: {video_path}")
        
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        try:
            import yt_dlp
            
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, check=True, text=True)
            metadata = json.loads(result.stdout)
            
            # Extract key information
            video_stream = next((s for s in metadata.get("streams", []) if s["codec_type"] == "video"), None)
            audio_stream = next((s for s in metadata.get("streams", []) if s["codec_type"] == "audio"), None)
            
            info = {
                "duration": float(metadata["format"].get("duration", 0)),
                "size": int(metadata["format"].get("size", 0)),
                "bit_rate": metadata["format"].get("bit_rate", "unknown"),
            }
            
            if video_stream:
                info.update({
                    "width": video_stream.get("width"),
                    "height": video_stream.get("height"),
                    "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                    "codec": video_stream.get("codec_name"),
                })
            
            if audio_stream:
                info["audio_codec"] = audio_stream.get("codec_name")
                info["sample_rate"] = audio_stream.get("sample_rate")
            
            logger.info(f"Metadata: {info}")
            return info
        
        except subprocess.CalledProcessError as e:
            logger.error(f"ffprobe error: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to get metadata: {str(e)}")
        except ImportError:
            logger.warning("ffprobe not available. Install FFmpeg with libav-tools.")
            raise
    
    # ==================== Private Helper Methods ====================
    
    def _validate_url(self, url: str) -> bool:
        """Validate if URL is properly formatted."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _get_source_type(self, url: str) -> str:
        """Detect source type from URL."""
        url_lower = url.lower()
        
        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "youtube"
        elif "tiktok.com" in url_lower:
            return "tiktok"
        elif "instagram.com" in url_lower or "instagr.am" in url_lower:
            return "instagram"
        else:
            return "generic"
    
    def _download_youtube(
        self,
        url: str,
        output_format: str = "mp4",
        max_duration: Optional[int] = None,
    ) -> str:
        """Download video from YouTube using yt-dlp."""
        try:
            import yt_dlp
        except ImportError:
            raise RuntimeError("yt-dlp not installed. Install with: pip install yt-dlp")
        
        logger.info(f"Downloading YouTube video: {url}")
        
        output_filename = f"youtube_%(title)s.%(ext)s"
        output_path = self.download_dir / output_filename
        
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": str(output_path),
            "quiet": True,
            "no_warnings": True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                logger.info(f"Downloaded: {downloaded_file}")
                
                # Trim if needed
                if max_duration and info.get("duration", 0) > max_duration:
                    return self.extract_clip(downloaded_file, 0, max_duration)
                
                return downloaded_file
        
        except Exception as e:
            logger.error(f"YouTube download error: {str(e)}")
            raise RuntimeError(f"Failed to download YouTube video: {str(e)}")
    
    def _download_tiktok(
        self,
        url: str,
        output_format: str = "mp4",
        max_duration: Optional[int] = None,
    ) -> str:
        """Download video from TikTok using yt-dlp."""
        try:
            import yt_dlp
        except ImportError:
            raise RuntimeError("yt-dlp not installed. Install with: pip install yt-dlp")
        
        logger.info(f"Downloading TikTok video: {url}")
        
        output_filename = f"tiktok_%(title)s.%(ext)s"
        output_path = self.download_dir / output_filename
        
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": str(output_path),
            "quiet": True,
            "no_warnings": True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                logger.info(f"Downloaded: {downloaded_file}")
                
                # Trim if needed
                if max_duration and info.get("duration", 0) > max_duration:
                    return self.extract_clip(downloaded_file, 0, max_duration)
                
                return downloaded_file
        
        except Exception as e:
            logger.error(f"TikTok download error: {str(e)}")
            raise RuntimeError(f"Failed to download TikTok video: {str(e)}")
    
    def _download_generic(
        self,
        url: str,
        output_format: str = "mp4",
        max_duration: Optional[int] = None,
    ) -> str:
        """Download video from generic URL using yt-dlp."""
        try:
            import yt_dlp
        except ImportError:
            raise RuntimeError("yt-dlp not installed. Install with: pip install yt-dlp")
        
        logger.info(f"Downloading generic video: {url}")
        
        output_filename = f"video_%(title)s.%(ext)s"
        output_path = self.download_dir / output_filename
        
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": str(output_path),
            "quiet": True,
            "no_warnings": True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                logger.info(f"Downloaded: {downloaded_file}")
                
                # Trim if needed
                if max_duration and info.get("duration", 0) > max_duration:
                    return self.extract_clip(downloaded_file, 0, max_duration)
                
                return downloaded_file
        
        except Exception as e:
            logger.error(f"Generic download error: {str(e)}")
            raise RuntimeError(f"Failed to download video: {str(e)}")
    
    def _download_image(self, url: str, output_format: str = "png") -> str:
        """Download a single image from URL."""
        try:
            import requests
            from PIL import Image
            from io import BytesIO
        except ImportError:
            raise RuntimeError("Required libraries not installed. Install with: pip install requests pillow")
        
        logger.debug(f"Downloading image: {url}")
        
        try:
            # Download image
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Open and save with PIL
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = bg
            
            # Save
            filename = f"image_{int(time.time() * 1000)}.{output_format}"
            output_path = self.download_dir / filename
            img.save(output_path, output_format.upper())
            
            logger.debug(f"Image saved: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Image download error: {str(e)}")
            raise
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        logger.info("Cleaning up temporary files")
        
        try:
            import shutil
            
            frames_dir = self.temp_dir / "frames"
            if frames_dir.exists():
                shutil.rmtree(frames_dir)
                logger.info("Removed frames directory")
            
            # Remove temp files older than 1 hour
            import time
            current_time = time.time()
            hour_ago = current_time - 3600
            
            for file in self.temp_dir.glob("*"):
                if file.is_file() and file.stat().st_mtime < hour_ago:
                    file.unlink()
                    logger.debug(f"Removed old temp file: {file}")
        
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")
