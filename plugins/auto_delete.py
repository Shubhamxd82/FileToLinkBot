from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database.settings_db import get_settings
from helpers.utils import get_readable_time

@Client.on_message(filters.command("autodel") & filters.private & filters.user(Config.ADMINS))
async def autodel(client, message):
    s = await get_settings()
    await message.reply(f"Auto-Delete: {'ON' if s.get('auto_delete_enabled') else 'OFF'}\nTime: {get_readable_time(s.get('auto_delete_time',600))}\n\nUse /settings to change.")
