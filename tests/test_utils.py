from utils import extract_video_id

def test_extract_video_id_standard_url():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_short_url():
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_raw_id():
    vid = "dQw4w9WgXcQ"
    assert extract_video_id(vid) == "dQw4w9WgXcQ"

def test_extract_video_id_with_extra_params():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s"
    assert extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_non_youtube_string():
    # The function assumes anything not matching youtube domains is a raw ID
    random_str = "some-random-string"
    assert extract_video_id(random_str) == "some-random-string"
