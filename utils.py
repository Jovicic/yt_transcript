from urllib.parse import urlparse, parse_qs
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(input_str: str) -> Optional[str]:
    """
    Extracts the YouTube video ID from a URL or returns the string if it's already an ID.
    """
    # Check if input is a URL
    if "youtube.com" in input_str or "youtu.be" in input_str:
        parsed_url = urlparse(input_str)
        if "youtube.com" in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            return query_params.get("v", [None])[0]
        elif "youtu.be" in parsed_url.netloc:
            return parsed_url.path.lstrip("/")

    # Assume it's a raw ID if not a URL
    return input_str

def fetch_youtube_transcript(video_id: str):
    """
    Fetches the English transcript for a given YouTube video ID.
    """
    # list_transcripts returns a TranscriptList object
    # We need to instantiate the API class first
    transcript_list = YouTubeTranscriptApi().list(video_id)

    # Filter for English transcripts (generated or manual)
    # We prefer manual english, but fallback to generated if needed, or translation?
    # The requirement says "only interested in english transcription language".
    # find_transcript(['en']) looks for manually created English transcripts.
    # If we want to support auto-generated English as well, we might need to be more flexible.
    # Usually find_transcript(['en']) is strict.
    # Let's try to find 'en' first.

    try:
        transcript = transcript_list.find_transcript(['en'])
    except Exception:
        # If strict 'en' not found, maybe 'en-US', 'en-GB' etc?
        # Or maybe auto-generated English?
        # For now, let's stick to the library's find_transcript which supports a list of language codes.
        # We can provide a list of english variants.
        transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])

    return transcript.fetch()
