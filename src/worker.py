import os, time, asyncio
from .config import SETTINGS
from .storage import JOB_Q, add_log
from .fetcher import get_meta_by_video_id, download_first_61s, resolve_stream_url
from .editor import make_61s
from .uploader import put_to_cdn_local, file_to_verified_cdn_url
from .tiktok_client import init_direct_post_pull, init_direct_post_upload, put_upload_binary

async def worker_loop(idx:int):
    add_log(f"[WORKER#{idx}] start")
    while True:
        job = JOB_Q.get()
        vid, cid = job["video_id"], job["channel_id"]
        t0 = time.time()
        try:
            meta = get_meta_by_video_id(vid)
            title, dur = meta["title"], meta["duration"]
            # IO tối thiểu
            if dur >= SETTINGS.target_duration:
                clip = download_first_61s(vid)
                out = make_61s(clip, duration_hint=SETTINGS.target_duration)
            else:
                url = resolve_stream_url(vid)
                out = make_61s(url, duration_hint=dur)

            if SETTINGS.tiktok_use_pull:
                cdn_url = put_to_cdn_local(out) if SETTINGS.cdn_local_enable else file_to_verified_cdn_url(out)
                _ = await init_direct_post_pull(cdn_url, caption=title)
            else:
                size = os.path.getsize(out)
                init_res = await init_direct_post_upload(size, caption=title)
                upload_url = init_res.get("data",{}).get("upload_url") or init_res.get("upload_url")
                if upload_url: await put_upload_binary(upload_url, out)

            add_log(f"[OK] {cid}:{vid} in {time.time()-t0:.2f}s")
        except Exception as e:
            add_log(f"[ERR] {cid}:{vid} {e}")
        finally:
            JOB_Q.task_done()
