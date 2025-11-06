import subprocess
from .config import SETTINGS
from .storage import temp_file
from .utils import seconds_to_atempo_chain

def probe_duration(input_url_or_path: str) -> float:
    cmd = [SETTINGS.ffprobe, "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", input_url_or_path]
    try:
        out = subprocess.check_output(cmd).decode().strip()
        return float(out)
    except: return 0.0

def make_61s(input_url_or_path: str, duration_hint: float|None=None) -> str:
    target = temp_file(".mp4")
    dur = duration_hint if duration_hint is not None else probe_duration(input_url_or_path)
    vf_base = (f"scale={SETTINGS.target_w}:{SETTINGS.target_h}:force_original_aspect_ratio=decrease,"
               f"pad={SETTINGS.target_w}:{SETTINGS.target_h}:(ow-iw)/2:(oh-ih)/2:color=black,"
               f"format=yuv420p,fps={SETTINGS.target_fps}")
    if dur >= SETTINGS.target_duration:
        cmd = [SETTINGS.ffmpeg, "-y", "-ss", "0", "-t", str(SETTINGS.target_duration),
               "-i", input_url_or_path, "-vf", vf_base, "-r", str(SETTINGS.target_fps),
               "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-crf", "28",
               "-c:a", "aac", "-b:a", "128k", target]
    else:
        slow = SETTINGS.target_duration / max(dur, 0.001)
        atempos = seconds_to_atempo_chain(slow)
        af = ",".join([f"atempo={t}" for t in atempos])
        cmd = [SETTINGS.ffmpeg, "-y", "-i", input_url_or_path,
               "-vf", f"setpts={slow}*PTS,{vf_base}", "-r", str(SETTINGS.target_fps),
               "-af", af, "-t", str(SETTINGS.target_duration),
               "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-crf", "28",
               "-c:a", "aac", "-b:a", "128k", target]
    subprocess.check_call(cmd)
    return target
