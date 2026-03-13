from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database.settings_db import toggle_setting
from database.users_db import add_group

@Client.on_message(filters.command("protect") & filters.private & filters.user(Config.ADMINS))
async def protect(client, message):
    new = await toggle_setting("protect_content")
    await message.reply(f"Content Protection: {'ON' if new else 'OFF'}")

@Client.on_message(filters.group)
async def group_track(client, message):
    if message.chat:
        await add_group(message.chat.id, message.chat.title)
