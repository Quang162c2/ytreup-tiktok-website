from .storage import seen_video, mark_video, add_log, JOB_Q

async def enqueue_video(channel_id:str, video_id:str):
    if seen_video(video_id): return
    mark_video(video_id)  # chống lặp sớm
    JOB_Q.put({"video_id": video_id, "channel_id": channel_id})
    add_log(f"[NEW] {channel_id}:{video_id} queued")
