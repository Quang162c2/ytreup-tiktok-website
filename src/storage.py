import pathlib, json, time, hashlib, threading, queue
from typing import Any

STATE = pathlib.Path(".state"); STATE.mkdir(exist_ok=True)
LOG_FILE = STATE / "events.log"
_log_lock = threading.Lock()

def _p(name:str)->pathlib.Path:
    h = hashlib.sha1(name.encode()).hexdigest()[:20]
    return STATE / f"{h}.json"

def read_json(name:str, default:Any)->Any:
    p = _p(name)
    if p.exists(): return json.loads(p.read_text(encoding="utf-8"))
    return default

def write_json(name:str, data:Any)->None:
    _p(name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def add_log(line:str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with _log_lock:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"{ts} {line}\n")

def tail_logs(limit:int=300)->str:
    if not LOG_FILE.exists(): return ""
    with LOG_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    return "".join(lines)

def seen_video(video_id:str)->bool:
    return _p("yt:"+video_id).exists()

def mark_video(video_id:str):
    write_json("yt:"+video_id, {"video_id":video_id,"ts":time.time()})

def temp_file(suffix:str)->str:
    p = pathlib.Path(".work")/f"{int(time.time()*1000)}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:6]}{suffix}"
    p.parent.mkdir(parents=True, exist_ok=True); return str(p)

# job queue cho workers
JOB_Q: "queue.Queue[dict]" = queue.Queue(maxsize=1000)
