from unittest.mock import patch
from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled

def test_get_transcript_no_auth(client):
    response = client.post("/transcript", json={"video_id": "test"})
    # FastAPI's HTTPBearer returns 403 when Authorization header is missing
    assert response.status_code == 403

def test_get_transcript_invalid_token(client):
    response = client.post(
        "/transcript",
        json={"video_id": "test"},
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication token"

def test_get_transcript_success_mock(client):
    video_id = "dQw4w9WgXcQ"
    mock_transcript = [{"text": "Never gonna give you up", "start": 0.0, "duration": 1.0}]

    # Mock the utility function that calls YouTube API
    with patch("utils.fetch_youtube_transcript", return_value=mock_transcript) as mock_fetch:
        response = client.post(
            "/transcript",
            json={"video_id": video_id},
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == video_id
        assert data["transcript"] == mock_transcript
        assert data["source"] == "youtube"

        # Verify mock was called
        mock_fetch.assert_called_once_with(video_id)

    # Test caching: Call again, should come from cache
    # We mock again to ensure it's NOT called
    with patch("utils.fetch_youtube_transcript") as mock_fetch_2:
        response2 = client.post(
            "/transcript",
            json={"video_id": video_id},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["source"] == "cache"
        assert data2["transcript"] == mock_transcript

        # Verify mock was NOT called (hit cache)
        mock_fetch_2.assert_not_called()

def test_get_transcript_not_found(client):
    # NoTranscriptFound requires arguments: video_id, requested_language_codes, transcript_data
    error = NoTranscriptFound("invalid-id", ["en"], None)
    with patch("utils.fetch_youtube_transcript", side_effect=error):
        response = client.post(
            "/transcript",
            json={"video_id": "invalid-id"},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

def test_get_transcript_disabled(client):
    # TranscriptsDisabled requires video_id
    error = TranscriptsDisabled("disabled-id")
    with patch("utils.fetch_youtube_transcript", side_effect=error):
        response = client.post(
            "/transcript",
            json={"video_id": "disabled-id"},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 404
        assert "disabled" in response.json()["detail"].lower()

def test_get_transcript_generic_error(client):
    with patch("utils.fetch_youtube_transcript", side_effect=Exception("Something went wrong")):
        response = client.post(
            "/transcript",
            json={"video_id": "error-id"},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 500
        assert "Something went wrong" in response.json()["detail"]
