"""
Core video generation engine for creating vertical 9:16 faceless videos.

Handles:
- Image/video composition
- Transitions and effects
- Text overlays and subtitles
- Audio mixing
- Final rendering to MP4 (1080x1920)
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
from moviepy import (
    ImageClip, VideoFileClip, ColorClip, TextClip,
    CompositeVideoClip, concatenate_videoclips, CompositeAudioClip,
    AudioClip, AudioFileClip, vfx, concatenate_audioclips
)
from PIL import Image, ImageDraw, ImageFont

from agent.logger import setup_logger
from agent.config import (
    OUTPUT_DIR, TEMP_DIR, VIDEO_RESOLUTION, VIDEO_FPS,
    VIDEO_CODEC, AUDIO_CODEC, AUDIO_BITRATE, VIDEO_BITRATE
)

logger = setup_logger(__name__, "video_generator.log")


class VideoGenerator:
    """Generate vertical 9:16 videos with AI visuals, text, and audio."""
    
    def __init__(self):
        """Initialize video generator with default settings."""
        self.width, self.height = VIDEO_RESOLUTION  # 1080x1920 (9:16)
        self.fps = VIDEO_FPS
        self.output_dir = OUTPUT_DIR
        self.temp_dir = TEMP_DIR
        
        logger.info(f"Video Generator initialized: {self.width}x{self.height} @ {self.fps}fps")
    
    def create_from_images(
        self,
        image_paths: List[str],
        duration_per_image: float = 3.0,
        transition: str = "fade",
        transition_duration: float = 0.5,
    ) -> str:
        """
        Create a video from a list of images.
        
        Args:
            image_paths: List of paths to image files
            duration_per_image: How long each image displays (seconds)
            transition: Type of transition ('fade', 'slide', 'zoom', 'none')
            transition_duration: Duration of transition effect (seconds)
        
        Returns:
            Path to output video file
        
        Raises:
            ValueError: If image_paths is empty or files don't exist
        """
        if not image_paths:
            raise ValueError("image_paths cannot be empty")
        
        # Verify all images exist
        for img_path in image_paths:
            if not Path(img_path).exists():
                raise FileNotFoundError(f"Image not found: {img_path}")
        
        logger.info(f"Creating video from {len(image_paths)} images")
        logger.info(f"Transition: {transition}, Duration: {duration_per_image}s per image")
        
        try:
            # Create clips for each image, resized to 9:16
            clips = []
            for i, img_path in enumerate(image_paths):
                logger.debug(f"Processing image {i+1}/{len(image_paths)}: {img_path}")
                
                # Resize image to 9:16 aspect ratio
                img_clip = self._load_and_resize_image(
                    img_path,
                    duration=duration_per_image
                )
                clips.append(img_clip)
            
            # Apply transitions between clips
            if transition != "none":
                clips = self._apply_transitions(clips, transition, transition_duration)
            
            # Concatenate clips
            final_clip = concatenate_videoclips(clips, method="chain")
            
            # Output path
            output_path = self.output_dir / f"video_from_images_{len(image_paths)}_images.mp4"
            
            # Render video
            self._render_video(final_clip, str(output_path))
            
            logger.info(f"Video created successfully: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error creating video from images: {str(e)}")
            raise
    
    def create_from_videos(
        self,
        video_paths: List[str],
        duration: float = 30.0,
        transition: str = "fade",
        transition_duration: float = 0.5,
    ) -> str:
        """
        Create a video by concatenating/clipping multiple videos.
        
        Args:
            video_paths: List of paths to video files
            duration: Total target duration (seconds) - videos will be cropped/sped up
            transition: Type of transition between clips
            transition_duration: Duration of transition effect
        
        Returns:
            Path to output video file
        """
        if not video_paths:
            raise ValueError("video_paths cannot be empty")
        
        logger.info(f"Creating video from {len(video_paths)} video files")
        logger.info(f"Target duration: {duration}s, Transition: {transition}")
        
        try:
            clips = []
            duration_per_clip = (duration - (len(video_paths) - 1) * transition_duration) / len(video_paths)
            
            for i, video_path in enumerate(video_paths):
                logger.debug(f"Processing video {i+1}/{len(video_paths)}: {video_path}")
                
                video_clip = self._load_and_resize_video(
                    video_path,
                    duration=duration_per_clip
                )
                clips.append(video_clip)
            
            # Apply transitions
            if transition != "none":
                clips = self._apply_transitions(clips, transition, transition_duration)
            
            # Concatenate
            final_clip = concatenate_videoclips(clips, method="chain")
            
            # Ensure target duration
            if final_clip.duration > duration:
                final_clip = final_clip.with_effects([vfx.MultiplySpeed(final_clip.duration / duration)])
            
            output_path = self.output_dir / f"video_from_videos_{len(video_paths)}_clips.mp4"
            self._render_video(final_clip, str(output_path))
            
            logger.info(f"Video created successfully: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error creating video from videos: {str(e)}")
            raise
    
    def add_text_overlay(
        self,
        video_path: str,
        text: str,
        fontsize: int = 80,
        color: str = "white",
        position: str = "center",
        start_time: float = 0,
        end_time: Optional[float] = None,
        background_color: Optional[str] = None,
        background_opacity: float = 0.7,
    ) -> str:
        """
        Add text overlay to video.
        
        Args:
            video_path: Path to input video
            text: Text to overlay
            fontsize: Font size in pixels
            color: Text color (hex or name)
            position: Position - 'top', 'center', 'bottom'
            start_time: When to start showing text (seconds)
            end_time: When to stop showing text (seconds)
            background_color: Optional background color behind text
            background_opacity: Opacity of background (0-1)
        
        Returns:
            Path to output video with text overlay
        """
        logger.info(f"Adding text overlay to video: {video_path}")
        logger.debug(f"Text: '{text}', Position: {position}")
        
        try:
            video = VideoFileClip(video_path)
            
            if end_time is None:
                end_time = video.duration
            
            # Create text clip
            txt_clip = TextClip(
                text,
                font_size=fontsize,
                color=color,
                method="caption",
                size=(self.width - 100, None),
                text_align="center",
                font="Arial-Bold"
            )
            txt_clip = txt_clip.with_duration(end_time - start_time)
            txt_clip = txt_clip.with_start(start_time)
            
            # Position text
            if position == "top":
                txt_clip = txt_clip.with_position(("center", 100))
            elif position == "center":
                txt_clip = txt_clip.with_position(("center", "center"))
            elif position == "bottom":
                txt_clip = txt_clip.with_position(("center", self.height - 200))
            
            # Optional background
            if background_color:
                bg_h = int(txt_clip.h + 40)
                # Calculate y position for background
                if position == "top":
                    bg_y = 100 + (txt_clip.h / 2) - (bg_h / 2)
                elif position == "center":
                    bg_y = (self.height / 2) - (bg_h / 2)
                elif position == "bottom":
                    bg_y = (self.height - 200) + (txt_clip.h / 2) - (bg_h / 2)
                else:
                    bg_y = (self.height / 2) - (bg_h / 2)

                bg_clip = ColorClip(
                    size=(self.width, bg_h),
                    color=self._parse_color(background_color)
                ).with_duration(end_time - start_time).with_start(start_time).with_position((0, bg_y)).with_opacity(background_opacity)
                
                # Composite with background
                composite = CompositeVideoClip([video, bg_clip, txt_clip])
            else:
                # Just add text
                composite = CompositeVideoClip([video, txt_clip])
            
            # Output
            output_path = self.output_dir / f"video_with_text_{Path(video_path).stem}.mp4"
            self._render_video(composite, str(output_path))
            
            logger.info(f"Text overlay added: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error adding text overlay: {str(e)}")
            raise
    
    def add_subtitles(
        self,
        video_path: str,
        subtitles: List[dict],
        fontsize: int = 40,
        color: str = "white",
        background_color: str = "black",
    ) -> str:
        """
        Add subtitles to video.
        
        Args:
            video_path: Path to input video
            subtitles: List of dicts with 'start', 'end', 'text' keys
                Example: [{"start": 0, "end": 2, "text": "Hello"}, ...]
            fontsize: Font size in pixels
            color: Subtitle text color
            background_color: Subtitle background color
        
        Returns:
            Path to output video with subtitles
        """
        logger.info(f"Adding {len(subtitles)} subtitles to video")
        
        try:
            video = VideoFileClip(video_path)
            subtitle_clips = []
            
            for i, sub in enumerate(subtitles):
                txt_clip = TextClip(
                    sub["text"],
                    font_size=fontsize,
                    color=color,
                    method="caption",
                    size=(self.width - 100, None),
                    text_align="center",
                    font="Arial"
                )
                txt_clip = txt_clip.with_duration(sub["end"] - sub["start"])
                txt_clip = txt_clip.with_start(sub["start"])
                txt_clip = txt_clip.with_position(("center", self.height - 150))
                
                # Background for readability
                bg_h = int(txt_clip.h + 20)
                bg_y = (self.height - 150) + (txt_clip.h / 2) - (bg_h / 2)
                bg_clip = ColorClip(
                    size=(self.width, bg_h),
                    color=self._parse_color(background_color)
                ).with_duration(sub["end"] - sub["start"]).with_start(sub["start"]).with_position((0, bg_y)).with_opacity(0.8)
                
                subtitle_clips.append(bg_clip)
                subtitle_clips.append(txt_clip)
            
            # Composite video with all subtitles
            all_clips = [video] + subtitle_clips
            composite = CompositeVideoClip(all_clips)
            
            # Output
            output_path = self.output_dir / f"video_with_subtitles_{Path(video_path).stem}.mp4"
            self._render_video(composite, str(output_path))
            
            logger.info(f"Subtitles added: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error adding subtitles: {str(e)}")
            raise
    
    def add_audio(
        self,
        video_path: str,
        audio_path: str,
        mix_with_original: bool = False,
        volume: float = 1.0,
    ) -> str:
        """
        Add or replace audio in video.
        
        Args:
            video_path: Path to input video
            audio_path: Path to audio file (mp3, wav, aac)
            mix_with_original: Whether to mix with original audio (True) or replace (False)
            volume: Audio volume multiplier (0-1)
        
        Returns:
            Path to output video with new audio
        """
        logger.info(f"Adding audio to video: {audio_path}")
        logger.debug(f"Mix original: {mix_with_original}, Volume: {volume}")
        
        try:
            video = VideoFileClip(video_path)
            new_audio = AudioFileClip(audio_path)
            
            # Trim or loop audio to match video duration
            if new_audio.duration > video.duration:
                new_audio = new_audio.subclipped(0, video.duration)
            elif new_audio.duration < video.duration:
                # Loop audio if too short
                repeats = int(video.duration / new_audio.duration) + 1
                audio_clips = [new_audio] * repeats
                new_audio = concatenate_audioclips(audio_clips).subclipped(0, video.duration)
            
            # Apply volume
            new_audio = new_audio.with_volume_scaled(volume)
            
            if mix_with_original and video.audio is not None:
                # Mix original and new audio
                composite_audio = CompositeAudioClip([video.audio, new_audio])
                video = video.with_audio(composite_audio)
            else:
                # Replace audio
                video = video.with_audio(new_audio)
            
            # Output
            output_path = self.output_dir / f"video_with_audio_{Path(video_path).stem}.mp4"
            self._render_video(video, str(output_path))
            
            logger.info(f"Audio added: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error adding audio: {str(e)}")
            raise
    
    def resize_to_vertical(self, video_path: str, fill_color: str = "black") -> str:
        """
        Resize video to 9:16 vertical format, adding letterboxing if needed.
        
        Args:
            video_path: Path to input video
            fill_color: Color to fill (hex or name)
        
        Returns:
            Path to resized video
        """
        logger.info(f"Resizing video to vertical 9:16: {video_path}")
        
        try:
            video = VideoFileClip(video_path)
            
            # Calculate new dimensions
            aspect_ratio = video.w / video.h
            target_ratio = self.width / self.height  # 9:16
            
            if aspect_ratio > target_ratio:
                # Video is too wide, add top/bottom bars
                new_height = int(video.w / target_ratio)
                padding = (new_height - video.h) // 2
                
                color = self._parse_color(fill_color)
                canvas = ColorClip(
                    size=(video.w, new_height),
                    color=color
                ).with_duration(video.duration)
                video = CompositeVideoClip([canvas, video.with_position(("center", padding))])
            else:
                # Video is too tall, add left/right bars
                new_width = int(video.h * target_ratio)
                padding = (new_width - video.w) // 2
                
                color = self._parse_color(fill_color)
                canvas = ColorClip(
                    size=(new_width, video.h),
                    color=color
                ).with_duration(video.duration)
                video = CompositeVideoClip([canvas, video.with_position((padding, "center"))])
            
            # Final resize to exactly 1080x1920
            video = video.resized(new_size=(self.width, self.height))
            
            output_path = self.output_dir / f"video_vertical_{Path(video_path).stem}.mp4"
            self._render_video(video, str(output_path))
            
            logger.info(f"Video resized to vertical: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error resizing to vertical: {str(e)}")
            raise
    
    # ==================== Private Helper Methods ====================
    
    def _load_and_resize_image(
        self,
        image_path: str,
        duration: float
    ) -> ImageClip:
        """Load image and resize to 9:16, with letterboxing if needed."""
        img = Image.open(image_path)
        img_aspect = img.width / img.height
        target_aspect = self.width / self.height
        
        # Resize image to fit 9:16
        if img_aspect > target_aspect:
            # Image is too wide
            new_height = self.height
            new_width = int(new_height * img_aspect)
        else:
            # Image is too tall
            new_width = self.width
            new_height = int(new_width / img_aspect)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create canvas with letterboxing
        canvas = Image.new("RGB", (self.width, self.height), color="black")
        offset_x = (self.width - new_width) // 2
        offset_y = (self.height - new_height) // 2
        canvas.paste(img, (offset_x, offset_y))
        
        # Save resized image to temp
        temp_path = self.temp_dir / f"resized_{Path(image_path).stem}.png"
        canvas.save(temp_path)
        
        # Create clip
        clip = ImageClip(str(temp_path))
        clip = clip.with_duration(duration)
        
        return clip
    
    def _load_and_resize_video(
        self,
        video_path: str,
        duration: float
    ) -> VideoFileClip:
        """Load video, resize to 9:16, and adjust duration."""
        video = VideoFileClip(video_path)
        
        # Crop center area to 9:16
        aspect = video.w / video.h
        target_aspect = self.width / self.height
        
        if aspect > target_aspect:
            # Video is too wide, crop sides
            new_width = int(video.h * target_aspect)
            x_offset = (video.w - new_width) // 2
            video = video.cropped(x1=x_offset, x2=x_offset + new_width)
        else:
            # Video is too tall, crop top/bottom
            new_height = int(video.w / target_aspect)
            y_offset = (video.h - new_height) // 2
            video = video.cropped(y1=y_offset, y2=y_offset + new_height)
        
        # Resize to exact dimensions
        video = video.resized(new_size=(self.width, self.height))
        
        # Adjust duration
        if video.duration > duration:
            video = video.with_effects([vfx.MultiplySpeed(video.duration / duration)])
        elif video.duration < duration:
            video = video.with_effects([vfx.MultiplySpeed(video.duration / duration)])
        
        return video.with_duration(duration)
    
    def _apply_transitions(
        self,
        clips: List,
        transition_type: str,
        duration: float
    ) -> List:
        """Apply transitions between clips."""
        if transition_type == "fade":
            from moviepy.video.fx.crossfadedecompose import crossfadedecompose
            clips = concatenate_videoclips(clips, method="chain")
            # Note: crossfade requires proper setup; fallback to chain
        # For now, chain concatenation (can be enhanced with fx)
        return clips
    
    def _render_video(self, clip, output_path: str):
        """Render video clip to MP4 file."""
        logger.info(f"Rendering video: {output_path}")
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write video file
        clip.write_videofile(
            output_path,
            fps=self.fps,
            codec=VIDEO_CODEC,
            audio_codec=AUDIO_CODEC,
            verbose=False,
            logger=None
        )
        
        logger.info(f"Video rendered successfully")
    
    def _parse_color(self, color: str) -> Tuple[int, int, int]:
        """Parse color string to RGB tuple."""
        color_map = {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "gray": (128, 128, 128),
        }
        
        if color.lower() in color_map:
            return color_map[color.lower()]
        
        # Parse hex color
        if color.startswith("#"):
            color = color.lstrip("#")
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        return (0, 0, 0)  # Default to black
