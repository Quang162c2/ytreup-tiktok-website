import json, subprocess
from .config import SETTINGS
from .storage import temp_file

def get_meta_by_video_id(video_id: str) -> dict:
    cmd = [SETTINGS.yt_dlp, "-J", f"https://www.youtube.com/watch?v={video_id}"]
    info = json.loads(subprocess.check_output(cmd))
    return {"duration": int(info.get("duration") or 0), "title": info.get("title") or ""}

def download_first_61s(video_id: str) -> str:
    out = temp_file(".mp4")
    cmd = [
        SETTINGS.yt_dlp, "--quiet", "--no-warnings",
        "--download-sections", "*0-61",
        "-f", "bv*[height<=480]+ba/b[height<=480]/bestaudio/best",
        "-o", out,
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    subprocess.check_call(cmd)
    return out

def resolve_stream_url(video_id: str) -> str:
    cmd = [SETTINGS.yt_dlp, "-f", "bv*[height<=480]+ba/best", "--get-url",
           f"https://www.youtube.com/watch?v={video_id}"]
    url = subprocess.check_output(cmd).decode().strip().splitlines()[-1]
    return url
