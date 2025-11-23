# AI Coding Agent Instructions

## Project Overview
This is a **FastAPI** application that fetches and caches YouTube video transcripts. It uses **SQLite** for storage and `youtube-transcript-api` for fetching data. The project uses **uv** for dependency management and is containerized with Docker.

## Architecture & Core Components
- **Entry Point**: `main.py` defines the FastAPI app, dependency injection, and API endpoints.
- **Database**: `database.py` handles `aiosqlite` connections and schema management.
  - **Pattern**: Uses async context managers (`async with`) for all DB interactions.
  - **Schema**: Simple tables (`transcripts`, `api_tokens`) created on startup (`lifespan`).
- **Business Logic**: `utils.py` contains logic for:
  - Extracting video IDs from various YouTube URL formats.
  - Fetching transcripts using `youtube_transcript_api`.
  - **Important**: Blocking calls (like `YouTubeTranscriptApi.list`) must be wrapped in `run_in_threadpool` to avoid blocking the async event loop.
- **Authentication**: Bearer token auth implemented via `HTTPBearer` and a database lookup (`verify_token`).

## Development Workflow
- **Dependency Management**: Uses `uv`.
  - Install dependencies: `uv sync`
  - Add dependency: `uv add <package>`
- **Running Locally**:
  - `uv run uvicorn main:app --reload`
  - Or directly: `python main.py`
- **Testing**:
  - Run tests: `uv run pytest`
  - Tests use a temporary SQLite file (`test_transcripts.db`) and mock external API calls.
- **Docker**:
  - Build & Run: `docker-compose up --build`
  - **Note**: The container runs as a non-root user (`appuser`). The database is persisted in the `/data` volume.

## Coding Conventions & Patterns
- **Async/Await**: Use `async def` for all route handlers and DB operations.
- **Blocking Code**: NEVER call blocking I/O directly in async functions. Use `fastapi.concurrency.run_in_threadpool`.
  - *Example*: `await run_in_threadpool(utils.fetch_youtube_transcript, video_id)`
- **Type Hinting**: Strictly use Python type hints and Pydantic models (`TranscriptRequest`).
- **Error Handling**: Use `HTTPException` with appropriate status codes (400, 401, 404, 500).
- **Configuration**: Environment variables (e.g., `DB_PATH`) are used for configuration, with sensible defaults.

## Key Files
- `main.py`: API routes and app configuration.
- `database.py`: Database access layer.
- `utils.py`: YouTube integration logic.
- `pyproject.toml`: Project metadata and dependencies (managed by `uv`).
- `Dockerfile`: Multi-stage build using `uv` for fast, cached builds.
