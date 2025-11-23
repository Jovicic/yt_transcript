from urllib.parse import urlparse, parse_qs
from typing import Optional
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

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
    proxy_username = os.environ.get("WEBSHARE_USERNAME")
    proxy_password = os.environ.get("WEBSHARE_PASSWORD")

    if proxy_username and proxy_password:
        ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password,
            )
        )
    else:
        ytt_api = YouTubeTranscriptApi()

    transcript_list = ytt_api.list(video_id)

    # Filter for English transcripts (generated or manual)
    # We prefer manual english, but fallback to generated if needed, or translation?
    # The requirement says "only interested in english transcription language".
    # find_transcript(['en']) looks for manually created English transcripts.
    # If we want to support auto-generated English as well, we might need to be more flexible.

    # We search for standard English variants. find_transcript will pick the first available one.
    transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])

    # fetch() returns a list of dictionaries, but sometimes it might be wrapped or behave differently?
    # Let's ensure we return a pure list of dicts.
    fetched_data = transcript.fetch()

    # Convert to list of dicts manually to ensure JSON serializability
    # and avoid 'FetchedTranscriptSnippet object is not iterable' error
    return [
        {
            "text": item["text"] if isinstance(item, dict) else item.text,
            "start": item["start"] if isinstance(item, dict) else item.start,
            "duration": item["duration"] if isinstance(item, dict) else item.duration,
        }
        for item in fetched_data
    ]
