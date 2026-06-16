import pytest
from unittest.mock import MagicMock, patch
from agent.script_generator import ScriptGenerator

@patch('agent.script_generator.OpenAI')
def test_generate_script(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"title": "Test Video", "description": "Test Desc", "tags": ["test"], "scenes": [{"text": "Scene 1", "visual_prompt": "Prompt 1", "duration": 5}]}'
    mock_client.chat.completions.create.return_value = mock_response

    generator = ScriptGenerator(api_key="fake_key")
    script = generator.generate_script("test prompt", duration=5)

    assert script['title'] == "Test Video"
    assert len(script['scenes']) == 1
    assert script['scenes'][0]['text'] == "Scene 1"
