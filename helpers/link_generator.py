import base64
import hashlib
import hmac
from config import Config
from database.settings_db import get_settings


class LinkGenerator:
    SECRET = Config.CF_SECRET_KEY or "default-secret"

    @classmethod
    def _sign(cls, data):
        return hmac.new(
            cls.SECRET.encode(), data.encode(), hashlib.sha256
        ).hexdigest()[:16]

    @classmethod
    def encode_file_uuid(cls, file_uuid):
        encoded = base64.urlsafe_b64encode(file_uuid.encode()).decode().rstrip("=")
        return f"{encoded}-{cls._sign(file_uuid)}"

    @classmethod
    def decode_file_uuid(cls, token):
        try:
            parts = token.rsplit("-", 1)
            if len(parts) != 2:
                return None
            encoded, sig = parts
            pad = 4 - len(encoded) % 4
            if pad != 4:
                encoded += "=" * pad
            uuid = base64.urlsafe_b64decode(encoded).decode()
            return uuid if cls._sign(uuid) == sig else None
        except Exception:
            return None

    @classmethod
    async def generate_bot_link(cls, file_uuid, bot_username=None):
        s = await get_settings()
        # Use DB redirect settings, fall back to Config
        if s.get("redirect_enabled") or Config.REDIRECT_ENABLED:
            redirect_username = s.get("redirect_bot_username") or Config.REDIRECT_BOT_USERNAME
            if redirect_username:
                bot_username = redirect_username
        if not bot_username:
            bot_username = Config.BOT_USERNAME
        return f"https://t.me/{bot_username}?start=file_{cls.encode_file_uuid(file_uuid)}"

    @classmethod
    async def generate_batch_link(cls, batch_uuid, bot_username=None):
        s = await get_settings()
        # Use DB redirect settings, fall back to Config
        if s.get("redirect_enabled") or Config.REDIRECT_ENABLED:
            redirect_username = s.get("redirect_bot_username") or Config.REDIRECT_BOT_USERNAME
            if redirect_username:
                bot_username = redirect_username
        if not bot_username:
            bot_username = Config.BOT_USERNAME
        return f"https://t.me/{bot_username}?start=batch_{cls.encode_file_uuid(batch_uuid)}"

    @classmethod
    async def generate_stream_link(cls, file_uuid):
        s = await get_settings()
        t = cls.encode_file_uuid(file_uuid)
        # Use DB CF settings, fall back to Config env variables
        cf_enabled = s.get("cf_enabled") or Config.CF_ENABLED
        cf_url = s.get("cf_worker_url") or Config.CF_WORKER_URL
        if cf_enabled and cf_url:
            return f"{cf_url}/watch/{t}"
        return f"{Config.BASE_URL}/watch/{t}"

    @classmethod
    async def generate_download_link(cls, file_uuid):
        s = await get_settings()
        t = cls.encode_file_uuid(file_uuid)
        # Use DB CF settings, fall back to Config env variables
        cf_enabled = s.get("cf_enabled") or Config.CF_ENABLED
        cf_url = s.get("cf_worker_url") or Config.CF_WORKER_URL
        if cf_enabled and cf_url:
            return f"{cf_url}/download/{t}"
        return f"{Config.BASE_URL}/download/{t}"
