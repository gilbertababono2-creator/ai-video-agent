"""Video generation module for creating faceless videos."""

import os
from pathlib import Path
from typing import Optional, List
from agent.logger import setup_logger
from agent.config import (
    OUTPUT_DIR,
    TEMP_DIR,
    VIDEO_RESOLUTION,
    VIDEO_FPS,
    VIDEO_CODEC,
    AUDIO_CODEC,
)

logger = setup_logger(__name__)


class VideoGenerator:
    """Generate videos with FFmpeg and MoviePy."""
    
    def __init__(
        self,
        resolution: tuple = VIDEO_RESOLUTION,
        fps: int = VIDEO_FPS,
        codec: str = VIDEO_CODEC,
    ):
        """
        Initialize video generator.
        
        Args:
            resolution: Video resolution (width, height) - default 1080x1920 (9:16)
            fps: Frames per second
            codec: Video codec to use
        """
        self.resolution = resolution
        self.fps = fps
        self.codec = codec
        logger.info(f"VideoGenerator initialized: {resolution} @ {fps}fps")
    
    def create_from_images(
        self,
        images: List[str],
        duration_per_image: float = 2.0,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Create a video from a list of images.
        
        Args:
            images: List of image file paths
            duration_per_image: Duration each image is shown (seconds)
            output_path: Output video file path
        
        Returns:
            Path to generated video
        """
        try:
            from moviepy.editor import ImageClip, concatenate_videoclips
            
            if not output_path:
                output_path = OUTPUT_DIR / "generated_video.mp4"
            else:
                output_path = Path(output_path)
            
            logger.info(f"Creating video from {len(images)} images...")
            
            clips = []
            for image in images:
                if not Path(image).exists():
                    logger.warning(f"Image not found: {image}")
                    continue
                
                clip = ImageClip(image).set_duration(duration_per_image)
                clip = clip.resize(height=self.resolution[1])
                clips.append(clip)
            
            if not clips:
                raise ValueError("No valid images provided")
            
            video = concatenate_videoclips(clips)
            video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec=self.codec,
                audio=False,
                verbose=False,
            )
            
            logger.info(f"Video created successfully: {output_path}")
            return str(output_path)
        
        except ImportError:
            logger.error("moviepy not installed. Install with: pip install moviepy")
            raise
        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            raise
    
    def add_text_overlay(
        self,
        video_path: str,
        text: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Add text overlay to video.
        
        Args:
            video_path: Path to input video
            text: Text to overlay
            output_path: Output video file path
        
        Returns:
            Path to video with text overlay
        """
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            
            if not output_path:
                output_path = OUTPUT_DIR / "video_with_text.mp4"
            else:
                output_path = Path(output_path)
            
            logger.info(f"Adding text overlay to {video_path}...")
            
            video = VideoFileClip(video_path)
            txt_clip = TextClip(text, fontsize=50, color='white', font='Arial')
            txt_clip = txt_clip.set_duration(video.duration)
            txt_clip = txt_clip.set_position('center')
            
            final_video = CompositeVideoClip([video, txt_clip])
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec=self.codec,
                verbose=False,
            )
            
            logger.info(f"Text overlay added: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error adding text overlay: {str(e)}")
            raise
    
    def add_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Add audio track to video.
        
        Args:
            video_path: Path to input video
            audio_path: Path to audio file
            output_path: Output video file path
        
        Returns:
            Path to video with audio
        """
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
            
            if not output_path:
                output_path = OUTPUT_DIR / "video_with_audio.mp4"
            else:
                output_path = Path(output_path)
            
            logger.info(f"Adding audio to {video_path}...")
            
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            final_video = video.set_audio(audio)
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec=self.codec,
                audio_codec=AUDIO_CODEC,
                verbose=False,
            )
            
            logger.info(f"Audio added: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error adding audio: {str(e)}")
            raise
    
    def resize_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Resize video to target resolution (9:16 for Shorts/Reels).
        
        Args:
            video_path: Path to input video
            output_path: Output video file path
        
        Returns:
            Path to resized video
        """
        try:
            from moviepy.editor import VideoFileClip
            
            if not output_path:
                output_path = OUTPUT_DIR / "video_resized.mp4"
            else:
                output_path = Path(output_path)
            
            logger.info(f"Resizing video to {self.resolution}...")
            
            video = VideoFileClip(video_path)
            video_resized = video.resize(height=self.resolution[1])
            
            video_resized.write_videofile(
                str(output_path),
                fps=self.fps,
                codec=self.codec,
                verbose=False,
            )
            
            logger.info(f"Video resized: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error resizing video: {str(e)}")
            raise
