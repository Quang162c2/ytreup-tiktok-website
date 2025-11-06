from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import xml.etree.ElementTree as ET
from .config import SETTINGS
from .channels import mark_seen
from .detector import enqueue_video
from .storage import add_log

app = FastAPI(title="YT→TikTok WebSub Server")

@app.get("/websub/callback")
async def verify(hub_challenge: str | None = None, **kw):
    if hub_challenge: return PlainTextResponse(hub_challenge)
    return PlainTextResponse("OK")

@app.post("/websub/callback")
async def callback(request: Request):
    raw = await request.body()
    try:
        root = ET.fromstring(raw)
        ns = {"a":"http://www.w3.org/2005/Atom","yt":"http://www.youtube.com/xml/schemas/2015"}
        vid = root.findtext(".//yt:videoId", namespaces=ns)
        chid = root.findtext(".//a:channelId", namespaces=ns)
        if vid and chid:
            mark_seen(chid)
            await enqueue_video(chid, vid)
    except Exception as e:
        add_log(f"[WebSub] parse err {e}")
    return PlainTextResponse("OK")
