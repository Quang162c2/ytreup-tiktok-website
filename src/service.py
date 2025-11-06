import asyncio, threading
import uvicorn, httpx
from .config import SETTINGS
from .storage import add_log
from .channels import list_channels, set_subscribed
from .server_websub import app as websub_app
from .worker import worker_loop

class ServiceController:
    def __init__(self):
        self._server_thread: threading.Thread | None = None
        self._loop = None
        self._running = False

    def start(self, workers:int):
        if self._running: return
        self._running = True
        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_loop, args=(workers,), daemon=True).start()
        self._server_thread = threading.Thread(target=self._run_server, daemon=True)
        self._server_thread.start()
        asyncio.run(self._subscribe_all())
        add_log("[SERVICE] started")

    def stop(self):
        self._running = False
        add_log("[SERVICE] stop requested")

    def _run_loop(self, workers:int):
        asyncio.set_event_loop(self._loop)
        for i in range(workers):
            asyncio.ensure_future(worker_loop(i+1))
        self._loop.run_forever()

    def _run_server(self):
        uvicorn.run(websub_app, host=SETTINGS.host, port=SETTINGS.port, log_level="warning")

    async def _subscribe_all(self):
        cb = f"{SETTINGS.public_base_url}/websub/callback"
        if not cb: 
            add_log("[WebSub] PUBLIC_BASE_URL missing — set in .env"); 
            return
        async with httpx.AsyncClient(timeout=10.0) as cli:
            for ch in list_channels():
                topic = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['channel_id']}"
                form = {"hub.mode":"subscribe","hub.topic":topic,"hub.callback":cb,"hub.verify":"async"}
                try:
                    r = await cli.post(SETTINGS.yt_hub, data=form); r.raise_for_status()
                    set_subscribed(ch["channel_id"], True)
                    add_log(f"[WebSub] subscribed {ch['channel_id']}")
                except Exception as e:
                    add_log(f"[WebSub] subscribe error {ch['channel_id']}: {e}")

SERVICE = ServiceController()
