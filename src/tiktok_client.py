import httpx, os
from .config import SETTINGS

HEADERS = {
    "Authorization": f"Bearer {SETTINGS.tiktok_access_token}",
    "Content-Type": "application/json; charset=utf-8",
}

async def init_direct_post_pull(video_url: str, caption: str="") -> dict:
    payload = {
        "source_info": {"source": "PULL_FROM_URL", "video_url": video_url},
        "post_info": {"title": caption[:2200], "privacy_level": "PUBLIC"},
    }
    url = SETTINGS.tiktok_base + SETTINGS.tiktok_direct_post_init
    async with httpx.AsyncClient(timeout=10.0) as cli:
        r = await cli.post(url, headers=HEADERS, json=payload)
        r.raise_for_status()
        return r.json()

async def init_direct_post_upload(filesize: int, caption: str="") -> dict:
    payload = {
        "source_info": {"source": "FILE_UPLOAD", "upload_type":"SIMPLE"},
        "post_info": {"title": caption[:2200], "privacy_level":"PUBLIC"},
        "media_file_info": {"size_in_bytes": filesize}
    }
    url = SETTINGS.tiktok_base + SETTINGS.tiktok_direct_post_init
    async with httpx.AsyncClient(timeout=10.0) as cli:
        r = await cli.post(url, headers=HEADERS, json=payload)
        r.raise_for_status()
        return r.json()

async def put_upload_binary(upload_url: str, file_path: str) -> None:
    size = os.path.getsize(file_path)
    headers = {"Content-Type":"video/mp4","Content-Length":str(size)}
    with open(file_path,"rb") as f:
        data = f.read()
    async with httpx.AsyncClient(timeout=None) as cli:
        r = await cli.put(upload_url, headers=headers, content=data)
        r.raise_for_status()
