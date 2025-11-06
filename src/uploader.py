import pathlib, shutil, http.server, socketserver, threading, os
from .config import SETTINGS

_server_started = False

def ensure_cdn_local():
    global _server_started
    if not SETTINGS.cdn_local_enable or _server_started: return
    root = pathlib.Path(SETTINGS.cdn_local_dir); root.mkdir(exist_ok=True, parents=True)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def translate_path(self, path):
            if path.startswith("/reup/"):
                return str(root / path[len("/reup/"):])
            return super().translate_path(path)
    httpd = socketserver.TCPServer(("0.0.0.0", SETTINGS.cdn_local_port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    _server_started = True

def put_to_cdn_local(file_path: str) -> str:
    ensure_cdn_local()
    dst = pathlib.Path(SETTINGS.cdn_local_dir)
    dst.mkdir(exist_ok=True, parents=True)
    name = pathlib.Path(file_path).name
    shutil.copyfile(file_path, dst / name)
    return SETTINGS.cdn_local_base_url + name

def file_to_verified_cdn_url(file_path:str)->str:
    return SETTINGS.tiktok_verified_cdn_base + os.path.basename(file_path)
