import pytest
from unittest.mock import MagicMock, patch
from agent.voiceover_generator import VoiceoverGenerator

@patch('agent.voiceover_generator.ElevenLabs')
def test_generate_voiceover(mock_elevenlabs):
    mock_client = MagicMock()
    mock_elevenlabs.return_value = mock_client
    mock_client.generate.return_value = b"fake audio data"

    generator = VoiceoverGenerator(api_key="fake_key")
    # Need to mock open since we are calling save in VoiceoverGenerator
    with patch("builtins.open", MagicMock()):
        path = generator.generate_voiceover("test text", output_filename="test.mp3")

    assert "test.mp3" in path
    mock_client.generate.assert_called_once()

@patch('agent.voiceover_generator.VoiceoverGenerator.generate_voiceover')
def test_generate_scene_voiceovers(mock_gen_vo):
    mock_gen_vo.return_value = "/tmp/scene.mp3"

    generator = VoiceoverGenerator(api_key="fake_key")
    scenes = [{"text": "Scene 1"}, {"text": "Scene 2"}]
    paths = generator.generate_scene_voiceovers(scenes)

    assert len(paths) == 2
    assert paths[0] == "/tmp/scene.mp3"
