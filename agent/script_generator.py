"""
Script generator using OpenAI to create video scripts.
"""

import json
from typing import List, Dict, Optional
from openai import OpenAI
from agent.config import OPENAI_API_KEY
from agent.logger import setup_logger

logger = setup_logger(__name__, "script_generator.log")


class ScriptGenerator:
    """Generate video scripts using AI."""

    def __init__(self, api_key: str = OPENAI_API_KEY):
        """
        Initialize with OpenAI API key.

        Args:
            api_key: OpenAI API key
        """
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=api_key)

    def generate_script(self, prompt: str, duration: int = 45) -> Dict:
        """
        Generate a video script based on a prompt.

        Args:
            prompt: User prompt describing the video
            duration: Target duration in seconds

        Returns:
            Dict containing title, description, tags, and scenes

        Returns a dict with:
        - title: Video title
        - description: Video description
        - tags: List of tags
        - scenes: List of dicts with 'text' (narration), 'visual_prompt', and 'duration'
        """
        logger.info(f"Generating script for prompt: {prompt} (duration: {duration}s)")

        system_prompt = (
            "You are an expert video script writer for YouTube Shorts, TikTok, and Reels. "
            "Create an engaging script based on the user's prompt. "
            f"The video should be approximately {duration} seconds long. "
            "Return the script in JSON format with the following structure: "
            "{\n"
            "  \"title\": \"Engaging Title\",\n"
            "  \"description\": \"Informative description\",\n"
            "  \"tags\": [\"tag1\", \"tag2\"],\n"
            "  \"scenes\": [\n"
            "    {\"text\": \"Narration text for scene 1\", \"visual_prompt\": \"Detailed description for AI image generation\", \"duration\": 5},\n"
            "    ...\n"
            "  ]\n"
            "}\n"
            "Ensure the total duration of scenes matches the requested duration."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            script = json.loads(content)
            logger.info(f"Script generated successfully with {len(script.get('scenes', []))} scenes")
            return script

        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise
