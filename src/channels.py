import json, subprocess, time
from typing import Optional, List, Dict
from .config import SETTINGS
from .storage import read_json, write_json, add_log
from .utils import YOUTUBE_ID_RE

STATE_KEY = "channels.json"

def _load()->dict:
    return read_json(STATE_KEY, {"items":[]})

def _save(data:dict): write_json(STATE_KEY, data)

def list_channels()->List[Dict]:
    return _load()["items"]

def get_channel(cid:str)->Optional[Dict]:
    for c in list_channels():
        if c["channel_id"]==cid: return c
    return None

def _resolve_channel_id(input_str:str)->Dict:
    raw = input_str.strip()
    m = YOUTUBE_ID_RE.search(raw)
    if m: return {"channel_id": m.group(1), "title": None}
    url = raw if not raw.startswith("@") else f"https://www.youtube.com/{raw}"
    cmd = [SETTINGS.yt_dlp, "-J", url]
    meta = json.loads(subprocess.check_output(cmd))
    cid = meta.get("channel_id") or meta.get("uploader_id")
    title = meta.get("channel") or meta.get("uploader") or meta.get("title")
    if not cid: raise RuntimeError("Cannot resolve channel_id")
    return {"channel_id": cid, "title": title}

def add_channel(input_str:str)->Dict:
    data = _load()
    meta = _resolve_channel_id(input_str)
    cid = meta["channel_id"]
    if any(x["channel_id"]==cid for x in data["items"]):
        return get_channel(cid) or meta
    data["items"].append({"channel_id": cid, "title": meta.get("title"),
                          "subscribed": False, "last_seen": None})
    _save(data); add_log(f"[CHANNEL] added {cid}")
    return meta

def remove_channel(cid:str):
    data = _load()
    data["items"] = [x for x in data["items"] if x["channel_id"]!=cid]
    _save(data); add_log(f"[CHANNEL] removed {cid}")

def mark_seen(cid:str):
    data = _load()
    for x in data["items"]:
        if x["channel_id"]==cid: x["last_seen"] = time.time()
    _save(data)

def set_subscribed(cid:str, ok:bool):
    data = _load()
    for x in data["items"]:
        if x["channel_id"]==cid: x["subscribed"] = ok
    _save(data)
