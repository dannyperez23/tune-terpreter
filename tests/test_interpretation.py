import logging
import pytest
from app import interpret_lyrics, OpenAIServiceError
import openai

def test_interpret_lyrics_success(mocker):
    """Test successful lyrics interpretation"""
    #Mock the OpenAI response structure
    mock_response = mocker.Mock()
    mock_response.choices = [mocker.Mock()]
    mock_response.choices[0].message.content = "This is an interpretation"

    #Mock the OpenAI client
    mock_client = mocker.Mock()
    mock_client.chat.completions.create.return_value = mock_response

    mocker.patch('openai.OpenAI', return_value=mock_client)

    result = interpret_lyrics("Test Lyrics here")

    assert result == "This is an interpretation"
    #Verify OpenAI was called with correct parameters
    mock_client.chat.completions.create.assert_called_once()

def test_interpret_lyrics_rate_limit_error(mocker, caplog):
    mock_client = mocker.Mock()
    mock_client.chat.completions.create.side_effect = openai.RateLimitError(
        "Rate limit exceeded",
        response=mocker.Mock(),
        body=None
    )

    mocker.patch('openai.OpenAI', return_value=mock_client)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(OpenAIServiceError):
            interpret_lyrics("Test lyrics")

    assert "OpenAI rate limit exceeded" in caplog.text

def test_interpret_lyrics_auth_error(mocker, caplog):
    mock_client = mocker.Mock()
    mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
        "Invalid API key",
        response=mocker.Mock(),
        body=None
    )

    mocker.patch('openai.OpenAI', return_value=mock_client)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(OpenAIServiceError):
            interpret_lyrics("Test lyrics")

    assert "OpenAI authentication failed" in caplog.text

def test_interpret_lyrics_generic_error(mocker, caplog):
    """Test handling of generic errors"""
    mock_client = mocker.Mock()
    mock_client.chat.completions.create.side_effect = Exception("Unknown error")

    mocker.patch('openai.OpenAI', return_value=mock_client)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(OpenAIServiceError):
            interpret_lyrics("Test lyrics")

    assert "An unexpected error occurred" in caplog.text
