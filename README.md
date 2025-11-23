# yt-transcript

A lightweight FastAPI service that fetches and caches YouTube video transcripts.

## Features

- **Fetch Transcripts**: Retrieves English transcripts for YouTube videos.
- **Caching**: Caches transcripts in a SQLite database to reduce external API calls.
- **Authentication**: Secure access via Bearer tokens.
- **Containerized**: Ready to run with Docker.

## Installation & Running

### Using Docker (Recommended)

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

### Local Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1.  **Install dependencies:**
    ```bash
    uv sync
    ```

2.  **Run the server:**
    ```bash
    uv run uvicorn main:app --reload
    ```

## Usage

### Authentication

On the first run, if no tokens exist in the database, the application will generate a secure API token and print it to the console logs. Use this token for requests.

### API Endpoints

#### Get Transcript

`POST /transcript`

**Headers:**
- `Authorization: Bearer <YOUR_TOKEN>`

**Body:**
```json
{
  "video_id": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```
*Note: `video_id` accepts both full URLs and video IDs.*

**Response:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "transcript": "...",
  "source": "youtube" 
}
```
*`source` will be "cache" if the transcript was previously fetched.*

## Configuration

- **Database**: Stores data in `transcripts.db` (or `/data/transcripts.db` in Docker).
