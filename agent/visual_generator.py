"""
Visual generator using OpenAI DALL-E 3 to create images for scenes.
"""

import os
import requests
from typing import List, Dict
from openai import OpenAI
from agent.config import OPENAI_API_KEY, TEMP_DIR
from agent.logger import setup_logger

logger = setup_logger(__name__, "visual_generator.log")


class VisualGenerator:
    """Generate AI visuals for video scenes."""

    def __init__(self, api_key: str = OPENAI_API_KEY):
        """
        Initialize with OpenAI API key.

        Args:
            api_key: OpenAI API key
        """
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=api_key)

    def generate_image(self, prompt: str, output_filename: str) -> str:
        """
        Generate an image using DALL-E 3.

        Args:
            prompt: Text prompt for image generation
            output_filename: Filename to save the image

        Returns:
            Path to the saved image
        """
        logger.info(f"Generating image for prompt: {prompt[:50]}...")

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # Vertical aspect ratio for 9:16
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            output_path = TEMP_DIR / output_filename

            # Download image
            img_data = requests.get(image_url).content
            with open(output_path, 'wb') as f:
                f.write(img_data)

            logger.info(f"Image saved to: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise

    def generate_scene_visuals(self, scenes: List[dict]) -> List[str]:
        """
        Generate images for a list of scenes.

        Args:
            scenes: List of scene dicts with 'visual_prompt' key

        Returns:
            List of paths to generated images
        """
        image_paths = []
        for i, scene in enumerate(scenes):
            visual_prompt = scene.get("visual_prompt", "")
            if visual_prompt:
                filename = f"scene_{i}_visual.png"
                path = self.generate_image(visual_prompt, filename)
                image_paths.append(path)
            else:
                logger.warning(f"Scene {i} has no visual prompt")
        return image_paths
