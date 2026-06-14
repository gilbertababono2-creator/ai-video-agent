"""Command-line interface for AI Video Agent."""

import click
from pathlib import Path
from agent.logger import setup_logger
from agent.video_generator import VideoGenerator

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
    
    Example:
        python -m agent.cli generate-and-upload \\
            --prompt "Create a motivational video about AI" \\
            --urls "https://example.com/video.mp4" \\
            --duration 45 \\
            --youtube-title "Top 5 AI Tools 2026 🔥" \\
            --upload-youtube
    """
    try:
        logger.info(f"Starting video generation: {prompt}")
        logger.info(f"Duration: {duration}s")
        
        # TODO: Implement full pipeline
        # 1. Download sources
        # 2. Generate script with AI
        # 3. Generate visuals
        # 4. Create video
        # 5. Upload to platforms
        
        click.echo("Video generation pipeline - Under construction")
        click.echo(f"Prompt: {prompt}")
        click.echo(f"Duration: {duration}s")
        
        if upload_youtube:
            click.echo("YouTube upload enabled")
        if upload_tiktok:
            click.echo("TikTok upload enabled")
        if upload_facebook:
            click.echo("Facebook upload enabled")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
def demo():
    """Run a demo to test the video generation pipeline."""
    try:
        logger.info("Running demo...")
        
        # Initialize video generator
        generator = VideoGenerator()
        
        click.echo("Demo mode - Video generation capabilities:")
        click.echo("✓ Create videos from images")
        click.echo("✓ Add text overlays")
        click.echo("✓ Add audio tracks")
        click.echo("✓ Resize to 9:16 format")
        click.echo("\nFull pipeline coming soon!")
    
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
