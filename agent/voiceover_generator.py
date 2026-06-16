"""
Voiceover generator using ElevenLabs API.
"""

import os
from typing import List, Optional
from elevenlabs.client import ElevenLabs
from agent.config import ELEVENLABS_API_KEY, TEMP_DIR
from agent.logger import setup_logger

logger = setup_logger(__name__, "voiceover_generator.log")


class VoiceoverGenerator:
    """Generate high-quality voiceovers using ElevenLabs."""

    def __init__(self, api_key: str = ELEVENLABS_API_KEY):
        """
        Initialize with ElevenLabs API key.

        Args:
            api_key: ElevenLabs API key
        """
        if not api_key:
            logger.warning("ELEVENLABS_API_KEY not found in environment")
        self.api_key = api_key
        self.client = ElevenLabs(api_key=api_key)

    def generate_voiceover(self, text: str, voice_name: str = "Adam", output_filename: Optional[str] = None) -> str:
        """
        Generate a voiceover for the given text.

        Args:
            text: Text to convert to speech
            voice_name: Name of the voice to use
            output_filename: Optional custom filename

        Returns:
            Path to the generated audio file
        """
        logger.info(f"Generating voiceover for text (length: {len(text)}) using voice: {voice_name}")

        if not output_filename:
            output_filename = f"voiceover_{hash(text) % 10000}.mp3"

        output_path = TEMP_DIR / output_filename

        try:
            audio_generator = self.client.generate(
                text=text,
                voice=voice_name,
                model="eleven_monolingual_v1"
            )

            # audio_generator is an iterator of bytes
            with open(output_path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)

            logger.info(f"Voiceover saved to: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating voiceover: {str(e)}")
            raise

    def generate_scene_voiceovers(self, scenes: List[dict]) -> List[str]:
        """
        Generate voiceovers for a list of scenes.

        Args:
            scenes: List of scene dicts with 'text' key

        Returns:
            List of paths to generated audio files
        """
        audio_paths = []
        for i, scene in enumerate(scenes):
            text = scene.get("text", "")
            if text:
                filename = f"scene_{i}_voiceover.mp3"
                path = self.generate_voiceover(text, output_filename=filename)
                audio_paths.append(path)
            else:
                logger.warning(f"Scene {i} has no text for voiceover")
        return audio_paths
