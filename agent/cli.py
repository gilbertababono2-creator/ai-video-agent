"""Command-line interface for AI Video Agent."""

import click
import os
from pathlib import Path
from typing import List, Optional

from moviepy import AudioFileClip, VideoFileClip, concatenate_videoclips, concatenate_audioclips

from agent.logger import setup_logger
from agent.video_generator import VideoGenerator
from agent.script_generator import ScriptGenerator
from agent.voiceover_generator import VoiceoverGenerator
from agent.visual_generator import VisualGenerator
from agent.media_downloader import MediaDownloader
from agent.uploader.youtube import YouTubeUploader
from agent.uploader.tiktok import TikTokUploader
from agent.uploader.facebook import FacebookUploader
from agent.config import TEMP_DIR

logger = setup_logger(__name__)


@click.group()
def cli():
    """AI Video Agent - Generate and upload faceless videos."""
    pass


@cli.command()
@click.option(
    '--prompt',
    required=True,
    help='Text prompt describing the video content',
)
@click.option(
    '--urls',
    multiple=True,
    help='Source video/image URLs to download and process',
)
@click.option(
    '--duration',
    type=int,
    default=45,
    help='Video duration in seconds (default: 45)',
)
@click.option(
    '--output',
    type=click.Path(),
    help='Output video file path',
)
@click.option(
    '--youtube-title',
    help='YouTube Shorts title',
)
@click.option(
    '--youtube-description',
    help='YouTube Shorts description',
)
@click.option(
    '--tiktok-caption',
    help='TikTok caption',
)
@click.option(
    '--facebook-description',
    help='Facebook Reels description',
)
@click.option(
    '--hashtags',
    help='Hashtags for all platforms',
)
@click.option(
    '--upload-youtube',
    is_flag=True,
    help='Upload to YouTube Shorts',
)
@click.option(
    '--upload-tiktok',
    is_flag=True,
    help='Upload to TikTok',
)
@click.option(
    '--upload-facebook',
    is_flag=True,
    help='Upload to Facebook Reels',
)
def generate_and_upload(
    prompt,
    urls,
    duration,
    output,
    youtube_title,
    youtube_description,
    tiktok_caption,
    facebook_description,
    hashtags,
    upload_youtube,
    upload_tiktok,
    upload_facebook,
):
    """
    Generate a faceless video and optionally upload to multiple platforms.
    """
    try:
        logger.info(f"Starting video generation pipeline: {prompt}")

        # 1. Download sources if provided
        downloader = MediaDownloader()
        downloaded_files = []
        if urls:
            logger.info(f"Downloading sources from {len(urls)} URLs")
            for url in urls:
                try:
                    file_path = downloader.download_video(url)
                    downloaded_files.append(file_path)
                except Exception as e:
                    logger.warning(f"Failed to download from {url}: {e}")

        # 2. Generate script
        script_gen = ScriptGenerator()
        script = script_gen.generate_script(prompt, duration)

        # 3. Generate voiceovers
        voice_gen = VoiceoverGenerator()
        voiceover_paths = voice_gen.generate_scene_voiceovers(script['scenes'])

        # 4. Generate visuals if supplement needed
        visual_gen = VisualGenerator()
        image_paths = visual_gen.generate_scene_visuals(script['scenes'])

        # 5. Create video base
        video_gen = VideoGenerator()
        
        # Integrate downloaded videos
        clips = []
        if downloaded_files:
            logger.info(f"Processing {len(downloaded_files)} downloaded files")
            for file in downloaded_files:
                if file.lower().endswith(('.mp4', '.mov', '.avi')):
                    try:
                        clip = VideoFileClip(file)
                        # Resize and crop to 9:16 vertical
                        clip = clip.resized(height=video_gen.height)
                        # Manual centering
                        x_center = clip.w / 2
                        y_center = clip.h / 2
                        clip = clip.cropped(width=video_gen.width, height=video_gen.height, x_center=x_center, y_center=y_center)
                        clips.append(clip)
                    except Exception as e:
                        logger.error(f"Error processing video file {file}: {e}")
                elif file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_paths.insert(0, file) # Add to the beginning

        # Final video assembly
        if not clips and not image_paths:
             raise ValueError("No images generated and no image/video sources provided")

        if image_paths:
            # Generate video from images as fallback or base
            duration_per_image = duration / len(image_paths) if image_paths else 0
            img_video_path = video_gen.create_from_images(image_paths, duration_per_image=duration_per_image)
            clips.append(VideoFileClip(img_video_path))

        final_video_clip = concatenate_videoclips(clips, method="compose")
        video_path = str(Path(TEMP_DIR) / "assembled_video.mp4")
        final_video_clip.write_videofile(video_path, fps=video_gen.fps, logger=None)
        
        # 6. Add audio (concatenate all voiceovers)
        if voiceover_paths:
            logger.info(f"Concatenating {len(voiceover_paths)} voiceovers")
            audio_clips = []
            for p in voiceover_paths:
                try:
                    audio_clips.append(AudioFileClip(p))
                except Exception as e:
                    logger.error(f"Error loading audio file {p}: {e}")

            if audio_clips:
                final_audio = concatenate_audioclips(audio_clips)
                combined_audio_path = str(TEMP_DIR / "combined_voiceover.mp3")
                final_audio.write_audiofile(combined_audio_path, logger=None)
                video_path = video_gen.add_audio(video_path, combined_audio_path)

        # 7. Add subtitles (using script text)
        subtitles = []
        current_time = 0
        num_scenes = len(script['scenes'])
        if num_scenes > 0:
            for i, scene in enumerate(script['scenes']):
                scene_duration = scene.get('duration', duration/num_scenes)
                subtitles.append({
                    'start': current_time,
                    'end': current_time + scene_duration,
                    'text': scene.get('text', '')
                })
                current_time += scene_duration

            video_path = video_gen.add_subtitles(video_path, subtitles)
        
        logger.info(f"Final video generated: {video_path}")
        click.echo(f"Video generated: {video_path}")

        # 8. Upload to platforms
        if upload_youtube:
            logger.info("Uploading to YouTube Shorts")
            yt_uploader = YouTubeUploader()
            yt_uploader.authenticate()
            yt_uploader.upload_video(
                video_path=video_path,
                title=youtube_title or script.get('title', 'AI Video'),
                description=youtube_description or script.get('description', ''),
                tags=script.get('tags', []) + (hashtags.split() if hashtags else [])
            )
            click.echo("Uploaded to YouTube Shorts")

        if upload_tiktok:
            logger.info("Uploading to TikTok")
            tt_uploader = TikTokUploader()
            tt_uploader.initialize()
            tt_uploader.upload(
                video_path=video_path,
                caption=tiktok_caption or script.get('title', 'AI Video'),
                hashtags=hashtags
            )
            click.echo("Uploaded to TikTok")

        if upload_facebook:
            logger.info("Uploading to Facebook Reels")
            fb_uploader = FacebookUploader()
            fb_uploader.upload(
                video_path=video_path,
                title=youtube_title or script.get('title', 'AI Video'),
                description=facebook_description or script.get('description', ''),
                hashtags=hashtags
            )
            click.echo("Uploaded to Facebook Reels")

    except Exception as e:
        logger.error(f"Error in pipeline: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
def demo():
    """Run a demo to test the video generation pipeline."""
    try:
        logger.info("Running demo...")
        generator = VideoGenerator()
        click.echo("Demo mode - Video generation capabilities:")
        click.echo("✓ Create videos from images")
        click.echo("✓ Add text overlays")
        click.echo("✓ Add audio tracks")
        click.echo("✓ Resize to 9:16 format")
        click.echo("\nFull pipeline integrated! Run 'generate-and-upload' to test.")
    
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
