import pytest
from unittest.mock import MagicMock, patch
from agent.visual_generator import VisualGenerator

@patch('agent.visual_generator.OpenAI')
@patch('agent.visual_generator.requests.get')
def test_generate_image(mock_requests_get, mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.data[0].url = "http://fakeurl.com/image.png"
    mock_client.images.generate.return_value = mock_response

    mock_req_response = MagicMock()
    mock_req_response.content = b"fake image data"
    mock_requests_get.return_value = mock_req_response

    # Mock open
    with patch("builtins.open", MagicMock()):
        generator = VisualGenerator(api_key="fake_key")
        path = generator.generate_image("test prompt", "test.png")

    assert "test.png" in path
    mock_client.images.generate.assert_called_once()
