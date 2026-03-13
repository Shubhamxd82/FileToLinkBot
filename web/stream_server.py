import os
import logging
import jinja2
import aiohttp_jinja2
from aiohttp import web
from pyrogram import Client
from config import Config
from database.files_db import get_file, increment_access
from helpers.link_generator import LinkGenerator
from helpers.file_properties import get_human_size

logger = logging.getLogger(__name__)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


class StreamServer:
    def __init__(self, bot: Client):
        self.bot = bot
        self.app = web.Application()

        # Setup Jinja2 templates
        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.FileSystemLoader(TEMPLATE_DIR)
        )

        # Routes
        self.app.router.add_get("/", self.home)
        self.app.router.add_get("/health", self.health)
        self.app.router.add_get("/stream/{token}", self.stream_file)
        self.app.router.add_get("/dl/{token}", self.download_file)
        self.app.router.add_get("/watch/{token}", self.watch_page)
        self.app.router.add_get("/download/{token}", self.download_page)

    # ─── Landing Page ───
    async def home(self, request):
        context = {
            "bot_username": Config.BOT_USERNAME,
            "base_url": Config.BASE_URL,
        }
        return aiohttp_jinja2.render_template("index.html", request, context)

    # ─── Health Check ───
    async def health(self, request):
        return web.json_response({"status": "ok", "bot": Config.BOT_USERNAME})

    # ─── Watch/Stream Page (HTML Player) ───
    async def watch_page(self, request):
        token = request.match_info["token"]
        file_data = await self._get_file_data(token)
        if not file_data:
            return web.Response(
                text="<h1>404 — File Not Found</h1>",
                status=404,
                content_type="text/html"
            )

        fd, fuuid = file_data
        file_type = fd.get("file_type", "document")
        mime_type = fd.get("mime_type", "application/octet-stream")

        # Determine player type
        player_type = "other"
        if file_type in ["video", "animation"] or mime_type.startswith("video"):
            player_type = "video"
        elif file_type in ["audio", "voice"] or mime_type.startswith("audio"):
            player_type = "audio"
        elif file_type == "photo" or mime_type.startswith("image"):
            player_type = "image"

        context = {
            "file_name": fd.get("file_name", "Unknown"),
            "file_size": get_human_size(fd.get("file_size", 0)),
            "file_size_bytes": fd.get("file_size", 0),
            "file_type": file_type,
            "player_type": player_type,
            "mime_type": mime_type,
            "stream_url": f"/stream/{token}",
            "download_url": f"/dl/{token}",
            "download_page_url": f"/download/{token}",
            "watch_url": f"/watch/{token}",
            "token": token,
            "bot_username": Config.BOT_USERNAME,
            "base_url": Config.BASE_URL,
            "access_count": fd.get("access_count", 0),
        }
        return aiohttp_jinja2.render_template("stream.html", request, context)

    # ─── Download Page (HTML) ───
    async def download_page(self, request):
        token = request.match_info["token"]
        file_data = await self._get_file_data(token)
        if not file_data:
            return web.Response(
                text="<h1>404 — File Not Found</h1>",
                status=404,
                content_type="text/html"
            )

        fd, fuuid = file_data
        file_name = fd.get("file_name", "Unknown")
        mime_type = fd.get("mime_type", "application/octet-stream")
        file_type = fd.get("file_type", "document")

        # File extension
        file_extension = file_name.rsplit(".", 1)[-1].upper() if "." in file_name else "FILE"

        # File emoji
        file_emoji = self._get_file_emoji(mime_type, file_type)

        # Can stream check
        can_stream = file_type in ["video", "animation", "audio", "voice"] or mime_type.startswith(("video", "audio"))

        context = {
            "file_name": file_name,
            "file_size": get_human_size(fd.get("file_size", 0)),
            "file_size_bytes": fd.get("file_size", 0),
            "file_type": file_type,
            "mime_type": mime_type,
            "file_extension": file_extension,
            "file_emoji": file_emoji,
            "can_stream": can_stream,
            "stream_url": f"/stream/{token}",
            "download_url": f"/dl/{token}",
            "watch_url": f"/watch/{token}",
            "download_page_url": f"/download/{token}",
            "token": token,
            "bot_username": Config.BOT_USERNAME,
            "base_url": Config.BASE_URL,
            "access_count": fd.get("access_count", 0),
        }
        return aiohttp_jinja2.render_template("download.html", request, context)

    # ─── Raw Stream (inline) ───
    async def stream_file(self, request):
        return await self._serve(request, request.match_info["token"], inline=True)

    # ─── Raw Download (attachment) ───
    async def download_file(self, request):
        return await self._serve(request, request.match_info["token"], inline=False)

    # ─── Core File Server with Proper Range Support ───
    async def _serve(self, request, token, inline):
        file_data = await self._get_file_data(token)
        if not file_data:
            return web.Response(text="Not found", status=404)

        fd, fuuid = file_data
        fsize = fd.get("file_size", 0)
        fname = fd.get("file_name", "file")
        mime = fd.get("mime_type", "application/octet-stream")

        # Parse Range header
        range_header = request.headers.get("Range")
        offset = 0
        end = fsize - 1
        status = 200

        if range_header:
            try:
                range_str = range_header.replace("bytes=", "")
                parts = range_str.split("-")
                offset = int(parts[0]) if parts[0] else 0
                end = int(parts[1]) if len(parts) > 1 and parts[1] else fsize - 1
                if end >= fsize:
                    end = fsize - 1
                if offset >= fsize:
                    return web.Response(
                        status=416,
                        headers={"Content-Range": f"bytes */{fsize}"}
                    )
                status = 206
            except (ValueError, IndexError):
                pass

        content_length = end - offset + 1

        headers = {
            "Content-Type": mime,
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Cache-Control": "public, max-age=3600",
        }

        if status == 206:
            headers["Content-Range"] = f"bytes {offset}-{end}/{fsize}"

        disp = "inline" if inline else "attachment"
        headers["Content-Disposition"] = f'{disp}; filename="{fname}"'

        resp = web.StreamResponse(status=status, headers=headers)
        await resp.prepare(request)

        try:
            msg = await self.bot.get_messages(fd["channel_id"], fd["message_id"])
            if not msg or msg.empty:
                logger.error(f"Message not found: {fd['message_id']}")
                return resp

            # Convert byte offset to 1MB chunk number (Telegram expects chunk index, not bytes)
            chunk_size = 1024 * 1024
            first_chunk = offset // chunk_size   # chunk index to start streaming from
            skip_bytes = offset % chunk_size     # bytes to skip at the start of first chunk

            bytes_sent = 0
            bytes_to_send = content_length
            is_first_chunk = True

            async for chunk in self.bot.stream_media(msg, offset=first_chunk):
                if bytes_sent >= bytes_to_send:
                    break

                # Discard leading bytes in first chunk that are before the requested offset
                if is_first_chunk and skip_bytes:
                    chunk = chunk[skip_bytes:]
                    is_first_chunk = False

                # Trim last chunk if it exceeds the requested byte range
                remaining = bytes_to_send - bytes_sent
                if len(chunk) > remaining:
                    chunk = chunk[:remaining]

                try:
                    await resp.write(chunk)
                    bytes_sent += len(chunk)
                except ConnectionResetError:
                    logger.info(f"Client disconnected: {fname}")
                    break
                except Exception:
                    break

        except Exception as e:
            logger.error(f"Stream error: {e}")

        try:
            await increment_access(fuuid)
        except Exception:
            pass

        return resp

    # ─── Helper: Get file data from token ───
    async def _get_file_data(self, token):
        fuuid = LinkGenerator.decode_file_uuid(token)
        if not fuuid:
            return None
        fd = await get_file(fuuid)
        if not fd:
            return None
        return fd, fuuid

    # ─── Helper: Get emoji for file type ───
    @staticmethod
    def _get_file_emoji(mime_type, file_type):
        emoji_map = {
            "video": "🎬",
            "audio": "🎵",
            "photo": "🖼️",
            "animation": "🎞️",
            "sticker": "🎨",
            "voice": "🎤",
            "video_note": "📹",
        }
        if file_type in emoji_map:
            return emoji_map[file_type]
        if mime_type:
            if mime_type.startswith("video"):
                return "🎬"
            elif mime_type.startswith("audio"):
                return "🎵"
            elif mime_type.startswith("image"):
                return "🖼️"
            elif "pdf" in mime_type:
                return "📕"
            elif any(x in mime_type for x in ["zip", "rar", "7z", "tar", "gzip"]):
                return "🗜️"
            elif "android" in mime_type:
                return "📱"
            elif mime_type.startswith("text"):
                return "📝"
        return "📄"

    # ─── Start Server ───
    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, Config.WEB_SERVER_BIND, Config.WEB_SERVER_PORT)
        await site.start()
        logger.info(f"Stream server started on port {Config.WEB_SERVER_PORT}")
