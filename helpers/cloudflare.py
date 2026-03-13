import aiohttp, hmac, hashlib, time
from config import Config

class CloudflareManager:
    @staticmethod
    def generate_cf_auth_header(path):
        ts = str(int(time.time()))
        sig = hmac.new(Config.CF_SECRET_KEY.encode(), f"{path}:{ts}".encode(), hashlib.sha256).hexdigest()
        return {"X-CF-Signature": sig, "X-CF-Timestamp": ts}

    @staticmethod
    async def register_redirect(old_bot, new_bot):
        if not Config.CF_WORKER_URL:
            return False
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(f"{Config.CF_WORKER_URL}/api/redirect", json={"old_bot": old_bot, "new_bot": new_bot, "secret": Config.CF_SECRET_KEY}, headers=CloudflareManager.generate_cf_auth_header("/api/redirect")) as r:
                    return r.status == 200
        except:
            return False
