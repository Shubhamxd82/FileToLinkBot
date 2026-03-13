import aiohttp
from config import Config
from database.settings_db import get_settings
from database.users_db import get_user

async def shorten_url(url, user_id=None):
    s = await get_settings()
    if not s.get("shortener_enabled"):
        return url
    api = s.get("shortener_api") or Config.SHORTENER_API
    surl = s.get("shortener_url") or Config.SHORTENER_URL
    if user_id:
        u = await get_user(user_id)
        if u:
            if u.get("shortener_enabled") is False:
                return url
            if u.get("custom_shortener_api") and u.get("custom_shortener_url"):
                api = u["custom_shortener_api"]
                surl = u["custom_shortener_url"]
    if not api or not surl:
        return url
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{surl}/api", params={"api": api, "url": url}, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    d = await r.json()
                    return d.get("shortenedUrl", url)
    except:
        pass
    return url
