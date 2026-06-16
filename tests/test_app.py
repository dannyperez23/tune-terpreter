
from app import SongNotFoundError, LyricsNotFoundError, GeniusServiceError, OpenAIServiceError


def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_search_success(client, mocker):
    #Mock the Genius API call
    mock_fetch_lyrics = mocker.patch('app.fetch_lyrics')
    mock_fetch_lyrics.return_value = "Sample lyrics here\nLine 2\nLine3"

    #Mock the OpenAI APi call
    mock_interpreter = mocker.patch('app.interpret_lyrics')
    mock_interpreter.return_value = "Sample interpretation"

    #Make request to /search endpoint
    response = client.post('/search', json={'song': 'Test Song', 'artist': 'Test Artist'})
    
    #Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert 'lyrics' in data
    assert 'summary' in data
    assert data['lyrics'] == "Sample lyrics here\nLine 2\nLine3"
    assert data['summary'] == "Sample interpretation"


def test_search_missing_song(client):
    """Test search with missing song parameter"""
    #Make request to /search endpoint
    response = client.post('/search', json={'artist': 'Test Artist'})

    #Assertions
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_search_empty_song_string(client):
    """Test search with an empty string passed as a song title"""
    response = client.post('/search', json={'song': '', 'artist': 'Test Artist'})

    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_search_missing_artist(client):
    """Test search with missing artist parameter"""
    #Make request to /search endpoint
    response = client.post('/search', json={'song': 'Test Song'})

    #Assertions
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_search_empty_artist_string(client):
    """Test search with an empty string passed as an artist name"""
    response = client.post('/search', json={'song': 'Test Song', 'artist': ''})

    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_search_song_not_found(client, mocker):
    """Test song not found search"""
    #Mock the Genius API call
    mock_fetch_lyrics = mocker.patch('app.fetch_lyrics')
    mock_fetch_lyrics.side_effect = SongNotFoundError("Song not found")

    #Make request to /search endpoint
    response = client.post('/search', json={'song': 'Nonexistent Song', 'artist': 'Nonexistent Artist'})

    #Assertions
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_search_lyrics_not_found(client, mocker):
    mock_fetch_lyrics = mocker.patch('app.fetch_lyrics')
    mock_fetch_lyrics.side_effect = LyricsNotFoundError("Lyrics not available for song")

    response = client.post('/search', json={'song': 'Test Song', 'artist': 'Test Artist'})

    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_search_genius_service_error(client, mocker):
    mock_fetch_lyrics = mocker.patch('app.fetch_lyrics')
    mock_fetch_lyrics.side_effect = GeniusServiceError("Genius service unavailable")

    response = client.post('/search', json={'song': 'Test Song', 'artist': 'Test Artist'})

    assert response.status_code == 502
    data = response.get_json()
    assert 'error' in data

def test_search_openai_service_error(client, mocker):
    mock_fetch_lyrics = mocker.patch('app.fetch_lyrics')
    mock_fetch_lyrics.return_value = "Sample lyrics"

    mock_interpret_lyrics = mocker.patch('app.interpret_lyrics')
    mock_interpret_lyrics.side_effect = OpenAIServiceError("OpenAI service unavailable")

    response = client.post('/search', json={'song': 'Test Song', 'artist': 'Test Artist'})

    assert response.status_code == 502
    data = response.get_json()
    assert 'error' in data

def test_search_limiting_error(client_limiting_enabled, mocker):
    mock_fetch_lyrics = mocker.patch('app.fetch_lyrics')
    mock_fetch_lyrics.return_value = "Sample lyrics"

    mock_interpreter = mocker.patch('app.interpret_lyrics')
    mock_interpreter.return_value = "Sample interpretation"

    for i in range(6):
        response = client_limiting_enabled.post('/search', json={'song': 'Test Song', 'artist': 'Test Artist'})

    assert response.status_code == 429
    data = response.get_json()
    assert 'error' in data


    