from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound
import secrets

import database
import utils

# Configure logging
# We rely on Uvicorn's logging configuration in production, but set a fallback here.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.init_db()

    # Check if any tokens exist, if not generate a secure one
    if not await database.has_any_token():
        new_token = secrets.token_urlsafe(32)
        await database.add_token(new_token)
        logger.warning(f"No API tokens found. Generated a new secure token: {new_token}")

    yield

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1", "http://localhost"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["POST"],  # Allows only POST method
    allow_headers=["Content-type", "Authorization"],  # Allows specific headers
)

security = HTTPBearer()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

class TranscriptRequest(BaseModel):
    video_id: str

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    is_valid = await database.is_token_valid(token)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return token

async def get_transcript_data(video_id: str):
    """
    Helper function to fetch transcript data from cache or YouTube.
    Returns a tuple (transcript, source).
    """
    # Check cache
    cached_transcript = await database.get_cached_transcript(video_id)
    if cached_transcript:
        return cached_transcript, "cache"

    # Fetch from YouTube
    try:
        # Run the synchronous library call in a threadpool to avoid blocking the event loop
        transcript = await run_in_threadpool(utils.fetch_youtube_transcript, video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        logger.warning(f"Transcript not found for video {video_id}")
        raise HTTPException(status_code=404, detail="English transcript not found or transcripts disabled")
    except Exception as e:
        logger.error(f"Error fetching transcript for {video_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    # Save to cache
    await database.save_transcript(video_id, transcript)
    return transcript, "youtube"

@app.post("/transcript")
async def get_transcript(request: TranscriptRequest, token: str = Depends(verify_token)):
    video_id_input = request.video_id

    # Extract the actual video ID
    video_id = utils.extract_video_id(video_id_input)

    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid video ID or URL")

    transcript, source = await get_transcript_data(video_id)

    return {"video_id": video_id, "transcript": transcript, "source": source}

@app.post("/transcript_simple")
async def get_transcript_simple(request: TranscriptRequest, token: str = Depends(verify_token)):
    video_id_input = request.video_id

    # Extract the actual video ID
    video_id = utils.extract_video_id(video_id_input)

    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid video ID or URL")

    transcript, source = await get_transcript_data(video_id)

    simple_text = " ".join([item["text"] for item in transcript])
    return {"video_id": video_id, "transcript": simple_text, "source": source}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, proxy_headers=True, forwarded_allow_ips="*")
