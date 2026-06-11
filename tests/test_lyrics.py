import logging
import pytest
from app import fetch_lyrics, SongNotFoundError, LyricsNotFoundError, GeniusServiceError

def test_fetch_lyrics_success(mocker):
    #Create a mock song object
    mock_song = mocker.Mock()
    mock_song.lyrics = "These are the lyrics\nLine 2\nLine 3"

    #Mock the genius.search_song method
    mock_genius = mocker.patch('app.genius.search_song')
    mock_genius.return_value = mock_song

    result = fetch_lyrics("Test Song", "Test Artist")

    #Verify the function was called correctly
    mock_genius.assert_called_once_with("Test Song", "Test Artist")
    assert result == "These are the lyrics\nLine 2\nLine 3"

def test_fetch_lyrics_empty_song_string(caplog):
    with caplog.at_level(logging.ERROR):
        with pytest.raises(SongNotFoundError):
            fetch_lyrics("", "Test Artist")

    assert "Empty string passed as song title" in caplog.text

def test_fetch_lyrics_empty_artist_string(caplog):
    with caplog.at_level(logging.ERROR):
        with pytest.raises(SongNotFoundError):
            fetch_lyrics("Test Song", "")
    
    assert "Empty string passed as artist name" in caplog.text

def test_fetch_lyrics_unavailable_lyrics(mocker, caplog):
    mock_song = mocker.Mock()
    mock_song.lyrics = ""

    mock_genius = mocker.patch('app.genius.search_song')
    mock_genius.return_value = mock_song

    with caplog.at_level(logging.WARNING):
        with pytest.raises(LyricsNotFoundError):
            fetch_lyrics("Test Song", "Test Artist")
    
    assert "lyrics unavailable" in caplog.text

def test_fetch_lyrics_song_not_found(mocker, caplog):
    # Mock the genius.search_song method
    mock_genius = mocker.patch('app.genius.search_song')
    mock_genius.return_value = None #Song not found

    with caplog.at_level(logging.WARNING):
        with pytest.raises(SongNotFoundError):
            fetch_lyrics("Test Song", "Test Artist")

    #Verify the function was called and did not return a song
    assert "not found on Genius" in caplog.text

def test_fetch_lyrics_generic_error(mocker, caplog):
    #Mock the genius.search_song raising an API Error Exception
    mock_genius = mocker.patch('app.genius.search_song')
    mock_genius.side_effect = Exception("API Error")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(GeniusServiceError):
            fetch_lyrics("Test Song", "Test Artist")

    assert "An unexpected error occurred" in caplog.text