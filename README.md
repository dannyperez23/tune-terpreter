# Tune-Terpreter
    
A web application that helps you understand the meaning behind a song's lyrics.

## Overview

Tune-Terpreter is an AI-powered web application that fetches song lyrics and provides a detailed interpretation, designed to help users understand songs they like but find lyrically complex. The user inputs a song-artist search query. Then, Tune-Terpreter fetches the song's lyrics using the Genius API and feeds the lyrics to an OpenAI LLM to break down and analyze the song's various sections. The song lyrics and the AI-generated analysis are then presented together to the user.

## Features

Core features:
-   Fetches song lyrics using Genius API
-   Prompts AI-generated response from OpenAI LLM
-   Interprets and analyzes song lyrics section by section
-   Provides summary of song

User Experience:
-   Responsive design (works on mobile and desktop)
-   Persisting light and dark themes that toggle and match the user's OS
-   Error handling with appropriate user-facing error messages
-   Loading state for better UX

Security:
-   Rate limiting to prevent abuse

## Tech Stack

Backend: Python, Flask, OpenAI API, Genius API
Frontend: HTML, JavaScript, Tailwind CSS
Testing: pytest, pytest-mock

## Architecture

Tune-Terpreter follows a standard client-server architecture with a Flask backend, JavaScript frontend, and integration with two external APIs (Genius & OpenAI).

Request flow:

1.  User interacts with the UI (inputs song title and artist name to search)
2.  JavaScript sends a request to the Flask API (POST /search endpoint)
3.  Flask validates the request, then calls fetch_lyrics which queries the Genius API
4.  Genius API returns the lyrics data
5.  Flask then calls interpret_lyrics, which sends the lyrics data along with a prompt to OpenAI's GPT LLM
6.  The OpenAI LLM returns a response containing an analysis of the lyrics
7.  Flask returns the song lyrics & AI-generated response as a JSON response
8.  JavaScript updates the DOM to reflect the new state

Component Responsibility:

-   Frontend (script.js): Handles user input, API requests, UI
-   Backend (app.py): Handles http requests, API requests, validates input, returns appropriate status codes
-   Error handling: Custom exceptions map to specific http status codes

Key design decision:

-   Custom exception handling: (SongNotFoundError, LyricsNotFoundError, GeniusServiceError, OpenAIServiceError): Custom exception classes propagate from data-fetch functions and map to http status codes.
-   Separation of concerns: Dedicated functions make calls to single external APIs. The LLM prompt is contained in an external .txt file.
-   Responsive UI update: Frontend updates with loading and error states to give the user visual feedback
-   Security: Rate-limiting via Flask-limiter restricts API calls to 10 requests per minute and 100 per day, while restricting further to 5 requests per minute at the /search route

## Setup

Prerequisites:

Python 3.10+
Node.js 18.0+

Steps:

1.  Clone the GitHub repository:

```bash
git clone https://github.com/dannyperez23/tune-terpreter.git
cd tune-terpreter
```

2. Create and activate virtual environment:

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
npm install
```

4. Create .env file with required variables (example provided):

```
# Default OpenAI LLM is gpt-4o-mini. Optional to use different OpenAI LLM
OPENAI_API_KEY=your_openai_key
GENIUS_ACCESS_TOKEN=your_genius_access_token
OPENAI_LLM_MODEL=gpt-4o-mini
```

5. Run build script (for TailwindCSS):

```bash
npm run build
```

6. Run the app:

```bash
flask run
```

## Testing

The project includes a testing suite using pytest and pytest-mock.
A formal [test plan] documenting the testing strategy, scope, test cases, test environment, entry & exit criteria, and risks & assumptions is available in the `docs/` directory

Run the tests with:

```bash
pytest
```

The test suite contains 22 test cases across three files:

-   `tests/test_lyrics.py` - unit tests for `fetch_lyrics`
-   `tests/test_interpretation.py` - unit tests for `interpret_lyrics`
-   `tests/test_app.py` - integration tests for the `/search` route

Testing approach:

-   External APIs are mocked to avoid network dependencies and reduce costs for LLM usage
-   Custom exceptions are verified using `pytest.raises`
-   Error logging is verified using `caplog`
-   Edge cases tested include: empty strings, API errors, missing fields, rate limit, timeout, and authentication error responses
-   Rate limiting is verified using a dedicated client fixture and test case in `tests/test_app.py`

## Security Considerations

-   API key management: All API keys are stored in a local `.env` file and excluded from version control via `.gitignore`
-   Rate limiting: Flask-Limiter caps requests at 5 per minute in the `/search` route to reduce costs
-   LLM Billing Cap: OpenAI billing is capped at $10/month in the OpenAI dashboard along with rate limiting to prevent abuse.
-   Error handling: No stack traces or internal details are revealed to the user.
-   Input validation: Both frontend and backend ensure search requests are valid before making API requests.
-   Debug Mode: Debug mode is disabled by default to protect against remote code execution.

## Future Improvements

-   End-to-end testing: Add browser-based testing, Selenium, to verify the complete user experience beyond unit and integration testing.
-   Prompt refinement: Continue tuning the LLM prompt to generate better quality interpretations across diverse music genres and lyrics complexity.
-   Lyrics & response caching: Give users access to previous lyrics & interpretation pairs within the same session to reduce API and LLM usage.
-   Improved error handling: implement handlers for Genius authentication, rate limit, and timeout errors.

## License

This project is under the MIT License. See the [LICENSE](LICENSE) file for details.