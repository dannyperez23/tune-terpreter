import os
import re
import logging
import openai
import lyricsgenius
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler('app.log')
                    ])

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Flask Limiter
limiter = Limiter (
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per minute"],
    storage_uri="memory://"
)

# Validate and set API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not GENIUS_ACCESS_TOKEN:
    raise ValueError("GENIUS_ACCESS_TOKEN not found in environment variables")

openai.api_key = OPENAI_API_KEY
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)

# Load LLM and Prompt variables
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
LLM_PROMPT_FILE = os.path.join(os.path.dirname(__file__), 'interpretation_prompt.txt')
try:
    with open(LLM_PROMPT_FILE, 'r', encoding='utf-8') as f:
        LLM_PROMPT = f.read()
except FileNotFoundError:
    raise RuntimeError(f"Prompt file not found at {LLM_PROMPT_FILE}")

# Custom Exception Handlers
class SongNotFoundError(Exception):
    pass

class LyricsNotFoundError(Exception):
    pass

class GeniusServiceError(Exception):
    pass

class OpenAIServiceError(Exception):
    pass

# Function to fetch lyrics from Genius API
def fetch_lyrics(song_title, artist_name):
    try:
        logger.info(f"Requesting {song_title}, {artist_name} from Genius")
        if not song_title:
            logger.error("Empty string passed as song title")
            raise SongNotFoundError(f"Empty song title")
        if not artist_name:
            logger.error("Empty string passed as artist name")
            raise SongNotFoundError(f"Empty artist name")
        
        song = genius.search_song(song_title, artist_name)

        if song and song.lyrics:
            logger.info(f"{song_title}, {artist_name} successfully found")
            return song.lyrics
        elif song and not song.lyrics:
            logger.warning(f"{song_title}, {artist_name} found but lyrics unavailable")
            raise LyricsNotFoundError(f"Lyrics unavailable for {song_title}, {artist_name}")
        else:
            logger.warning(f"{song_title}, {artist_name} not found on Genius")
            raise SongNotFoundError(f"{song_title}, {artist_name} not found")
    except (SongNotFoundError, LyricsNotFoundError):
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred, {e}")
        raise GeniusServiceError(str(e))
    

# Function to interpret lyrics using OpenAI API
def interpret_lyrics(lyrics):
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=OPENAI_LLM_MODEL,
            messages=[
                {"role": "system", "content": LLM_PROMPT},
                {"role": "user", "content": f"Interpret these song lyrics:\n\n{lyrics}"}
            ]
        )
        
        formatted_response = strip_markdown(response.choices[0].message.content)
        return formatted_response
    except openai.RateLimitError:
        logger.error("OpenAI rate limit exceeded")
        raise OpenAIServiceError("Rate limit exceeded")
    except openai.AuthenticationError:
        logger.error("OpenAI authentication failed")
        raise OpenAIServiceError("Authentication failed")
    except openai.APITimeoutError:
        logger.error("OpenAI request timed out")
        raise OpenAIServiceError("Timeout error")
    except Exception as e:
        logger.error(f"An unexpected error occurred, {e}")
        raise OpenAIServiceError(str(e))

# Function to clean up markdown formatting from LLM
def strip_markdown(response):
    response = re.sub(r'\*\*(.+?)\*\*', r'\1', response)            # **bold**
    response = re.sub(r'\*(.+?)\*', r'\1', response)                # *italic*
    response = re.sub(r'__(.+?)__', r'\1', response)                # __bold__
    response = re.sub(r'_(.+?)_', r'\1', response)                  # _italic_
    response = re.sub(r'^#+ ', '', response, flags=re.MULTILINE)    # headers
    return response

# Render the home page
@app.route('/')
def home():
    return render_template('index.html')

# Handle song search requests
@app.route('/search', methods=['POST'])
@limiter.limit('5 per minute')
def search():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data provided.'}), 400
    
    song = data.get('song')
    artist = data.get('artist')

    if not song:
        return jsonify({'error': 'Query incomplete. Missing song title.'}), 400
    if not artist:
        return jsonify({'error': 'Query incomplete. Missing artist name.'}), 400
    
    try:
        lyrics = fetch_lyrics(song, artist)
    except SongNotFoundError:
        return jsonify({'error': 'Song not found'}), 404
    except LyricsNotFoundError:
        return jsonify({'error': 'Lyrics not available for song'}), 404
    except GeniusServiceError:
        return jsonify({'error': 'Genius service unavailable'}), 502
    
    try:
        summary = interpret_lyrics(lyrics)
    except OpenAIServiceError:
        return jsonify({'error': 'Failed to generate interpretation'}), 502
        
    
    return jsonify({
        'lyrics': lyrics,
        'summary': summary
    })

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Too many requests. Please wait a moment before trying again.'}), 429

if __name__ == '__main__':
    # WARNING: Debug mode should be disabled in production
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(debug=debug_mode)