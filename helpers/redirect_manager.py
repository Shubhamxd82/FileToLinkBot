from database.settings_db import update_setting, get_settings
from helpers.cloudflare import CloudflareManager

class RedirectManager:
    @staticmethod
    async def activate_redirect(new_bot):
        await update_setting("redirect_enabled", True)
        await update_setting("redirect_bot_username", new_bot)
        s = await get_settings()
        if s.get("cf_enabled"):
            await CloudflareManager.register_redirect(s.get("current_bot_username", ""), new_bot)
        return True

    @staticmethod
    async def deactivate_redirect():
        await update_setting("redirect_enabled", False)
        await update_setting("redirect_bot_username", None)
        return True

    @staticmethod
    async def get_active_bot_username():
        s = await get_settings()
        if s.get("redirect_enabled") and s.get("redirect_bot_username"):
            return s["redirect_bot_username"]
        from config import Config
        return Config.BOT_USERNAME
