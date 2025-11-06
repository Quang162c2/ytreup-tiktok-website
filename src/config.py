from pydantic import BaseModel
from dotenv import load_dotenv
import os, pathlib

load_dotenv()

class Settings(BaseModel):
    host: str = os.getenv("HOST","127.0.0.1")
    port: int = int(os.getenv("PORT","8080"))
    public_base_url: str = os.getenv("PUBLIC_BASE_URL","").rstrip("/")

    yt_hub: str = os.getenv("YOUTUBE_HUB","https://pubsubhubbub.appspot.com")

    ffmpeg: str = os.getenv("FFMPEG_PATH","ffmpeg")
    ffprobe: str = os.getenv("FFPROBE_PATH","ffprobe")
    yt_dlp: str = os.getenv("YT_DLP_PATH","yt-dlp")

    target_w: int = int(os.getenv("TARGET_WIDTH","1080"))
    target_h: int = int(os.getenv("TARGET_HEIGHT","1920"))
    target_fps: int = int(os.getenv("TARGET_FPS","30"))
    target_duration: int = int(os.getenv("TARGET_DURATION","61"))

    tiktok_base: str = os.getenv("TIKTOK_BASE","https://open.tiktokapis.com").rstrip("/")
    tiktok_access_token: str = os.getenv("TIKTOK_ACCESS_TOKEN","")
    tiktok_use_pull: bool = os.getenv("TIKTOK_USE_PULL_FROM_URL","true").lower()=="true"
    tiktok_direct_post_init: str = os.getenv("TIKTOK_DIRECT_POST_INIT","/v2/post/publish/video/init/")
    tiktok_verified_cdn_base: str = os.getenv("TIKTOK_VERIFIED_CDN_BASE","").rstrip("/") + "/"

    cdn_local_enable: bool = os.getenv("CDN_LOCAL_ENABLE","false").lower()=="true"
    cdn_local_port: int = int(os.getenv("CDN_LOCAL_PORT","9090"))
    cdn_local_base_url: str = os.getenv("CDN_LOCAL_BASE_URL","http://127.0.0.1:9090/reup/").rstrip("/") + "/"
    cdn_local_dir: str = os.getenv("CDN_LOCAL_DIR",".cdn_store")

    encode_workers: int = int(os.getenv("ENCODE_WORKERS","3"))

    workdir: str = str(pathlib.Path(".work").absolute())
    state_dir: str = ".state"

SETTINGS = Settings()
pathlib.Path(SETTINGS.workdir).mkdir(parents=True, exist_ok=True)
pathlib.Path(SETTINGS.state_dir).mkdir(parents=True, exist_ok=True)
