import logging
from aiohttp import web
from pyrogram import Client
from config import Config
from database.files_db import get_file, increment_access
from helpers.link_generator import LinkGenerator
from helpers.file_properties import get_human_size

logger = logging.getLogger(__name__)

class StreamServer:
    def __init__(self, bot: Client):
        self.bot = bot
        self.app = web.Application()
        self.app.router.add_get("/", self.home)
        self.app.router.add_get("/health", self.health)
        self.app.router.add_get("/stream/{token}", self.stream)
        self.app.router.add_get("/dl/{token}", self.download)
        self.app.router.add_get("/watch/{token}", self.watch)

    async def home(self, req):
        return web.Response(text="<h1>FileToLink Stream Server</h1>", content_type="text/html")

    async def health(self, req):
        return web.json_response({"status": "ok"})

    async def stream(self, req):
        return await self._serve(req, req.match_info["token"], True)

    async def download(self, req):
        return await self._serve(req, req.match_info["token"], False)

    async def watch(self, req):
        token = req.match_info["token"]
        fuuid = LinkGenerator.decode_file_uuid(token)
        if not fuuid:
            return web.Response(text="Invalid", status=404)
        fd = await get_file(fuuid)
        if not fd:
            return web.Response(text="Not found", status=404)
        ft = fd.get("file_type","document")
        fn = fd.get("file_name","file")
        fs = get_human_size(fd.get("file_size",0))
        if ft in ["video","animation"]:
            player = f'<video controls autoplay style="max-width:100%"><source src="/stream/{token}"></video>'
        elif ft == "audio":
            player = f'<audio controls autoplay><source src="/stream/{token}"></audio>'
        else:
            player = f'<a href="/dl/{token}">Download {fn}</a>'
        html = f'<!DOCTYPE html><html><head><title>{fn}</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{{font-family:Arial;background:#1a1a2e;color:#eee;display:flex;flex-direction:column;align-items:center;min-height:100vh;margin:0}}h2{{color:#00d2ff}}.info{{color:#888}}a{{color:#00d2ff;padding:15px 30px;background:#333;border-radius:8px;text-decoration:none;display:inline-block;margin:20px}}</style></head><body><h2>{fn}</h2><p class="info">{fs} | {ft}</p>{player}<br><a href="/dl/{token}">Download</a></body></html>'
        return web.Response(text=html, content_type="text/html")

    async def _serve(self, req, token, inline):
        fuuid = LinkGenerator.decode_file_uuid(token)
        if not fuuid:
            return web.Response(text="Invalid", status=404)
        fd = await get_file(fuuid)
        if not fd:
            return web.Response(text="Not found", status=404)
        fsize = fd.get("file_size", 0)
        fname = fd.get("file_name", "file")
        mime = fd.get("mime_type", "application/octet-stream")
        rng = req.headers.get("Range")
        offset = 0
        limit = fsize
        status = 200
        if rng:
            parts = rng.replace("bytes=","").split("-")
            offset = int(parts[0]) if parts[0] else 0
            limit = int(parts[1])+1 if parts[1] else fsize
            status = 206
        headers = {"Content-Type": mime, "Accept-Ranges": "bytes", "Content-Length": str(limit-offset)}
        if status == 206:
            headers["Content-Range"] = f"bytes {offset}-{limit-1}/{fsize}"
        disp = "inline" if inline else "attachment"
        headers["Content-Disposition"] = f'{disp}; filename="{fname}"'
        resp = web.StreamResponse(status=status, headers=headers)
        await resp.prepare(req)
        try:
            msg = await self.bot.get_messages(fd["channel_id"], fd["message_id"])
            async for chunk in self.bot.stream_media(msg, offset=offset, limit=limit-offset):
                await resp.write(chunk)
        except Exception as e:
            logger.error(f"Stream error: {e}")
        await increment_access(fuuid)
        return resp

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, Config.WEB_SERVER_BIND, Config.WEB_SERVER_PORT)
        await site.start()
        logger.info(f"Stream server on port {Config.WEB_SERVER_PORT}")
