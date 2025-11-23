from unittest.mock import patch

def test_get_transcript_simple_success_mock(client):
    video_id = "dQw4w9WgXcQ"
    mock_transcript = [
        {"text": "Never gonna give you up", "start": 0.0, "duration": 1.0},
        {"text": "Never gonna let you down", "start": 1.0, "duration": 1.0}
    ]
    expected_simple_text = "Never gonna give you up Never gonna let you down"

    # Mock the utility function that calls YouTube API
    with patch("utils.fetch_youtube_transcript", return_value=mock_transcript) as mock_fetch:
        response = client.post(
            "/transcript_simple",
            json={"video_id": video_id},
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == video_id
        assert data["transcript"] == expected_simple_text
        assert data["source"] == "youtube"

        # Verify mock was called
        mock_fetch.assert_called_once_with(video_id)

    # Test caching: Call again, should come from cache
    # We mock again to ensure it's NOT called
    with patch("utils.fetch_youtube_transcript") as mock_fetch_2:
        response2 = client.post(
            "/transcript_simple",
            json={"video_id": video_id},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["source"] == "cache"
        assert data2["transcript"] == expected_simple_text
        mock_fetch_2.assert_not_called()
