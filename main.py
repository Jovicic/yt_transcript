from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound
import secrets

import database
import utils

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.init_db()

    # Check if any tokens exist, if not generate a secure one
    if not await database.has_any_token():
        new_token = secrets.token_urlsafe(32)
        await database.add_token(new_token)
        print(f"\n{'='*60}")
        print("WARNING: No API tokens found. Generated a new secure token:")
        print(f"Token: {new_token}")
        print(f"{'='*60}\n")

    yield

app = FastAPI(lifespan=lifespan)
security = HTTPBearer()

class TranscriptRequest(BaseModel):
    video_id: str

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    is_valid = await database.is_token_valid(token)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return token

@app.post("/transcript")
async def get_transcript(request: TranscriptRequest, token: str = Depends(verify_token)):
    video_id_input = request.video_id

    # Extract the actual video ID
    video_id = utils.extract_video_id(video_id_input)

    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid video ID or URL")

    # Check cache
    cached_transcript = await database.get_cached_transcript(video_id)
    if cached_transcript:
        return {"video_id": video_id, "transcript": cached_transcript, "source": "cache"}

    # Fetch from YouTube
    try:
        # Run the synchronous library call in a threadpool to avoid blocking the event loop
        transcript = await run_in_threadpool(utils.fetch_youtube_transcript, video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        raise HTTPException(status_code=404, detail="English transcript not found or transcripts disabled")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save to cache
    await database.save_transcript(video_id, transcript)

    return {"video_id": video_id, "transcript": transcript, "source": "youtube"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, proxy_headers=True, forwarded_allow_ips="*")
