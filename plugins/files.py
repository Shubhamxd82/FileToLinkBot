from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import Config
from database.users_db import is_user_banned
from database.files_db import save_file
from helpers.file_properties import get_file_info, get_human_size
from helpers.link_generator import LinkGenerator
from helpers.shortener_api import shorten_url

MEDIA = filters.document | filters.video | filters.audio | filters.photo | filters.voice | filters.video_note | filters.sticker | filters.animation

@Client.on_message(MEDIA & filters.private)
async def handle_file(client, message):
    uid = message.from_user.id
    if await is_user_banned(uid):
        return
    fi = get_file_info(message)
    if not fi:
        return await message.reply("Unsupported file.")
    pm = await message.reply("Processing...", quote=True)
    try:
        fwd = await message.copy(Config.DB_CHANNEL_ID)
        fuuid = await save_file(fi["file_id"], fi["file_ref"], fi["file_name"], fi["file_size"], fi["file_type"], fi["mime_type"], uid, fwd.id, Config.DB_CHANNEL_ID, message.caption)
        from plugins.batch import check_batch_mode
        if await check_batch_mode(client, message, fuuid):
            return await pm.delete()
        bl = await LinkGenerator.generate_bot_link(fuuid)
        sl = await LinkGenerator.generate_stream_link(fuuid)
        dl = await LinkGenerator.generate_download_link(fuuid)
        bls = await shorten_url(bl, uid)
        sls = await shorten_url(sl, uid)
        dls = await shorten_url(dl, uid)
        text = f"**File Stored!**\n\nName: `{fi['file_name']}`\nSize: {get_human_size(fi['file_size'])}\n\nLink: `{bls}`\nStream: `{sls}`\nDownload: `{dls}`"
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("Share", url=bl)],[InlineKeyboardButton("Stream", url=sl), InlineKeyboardButton("Download", url=dl)],[InlineKeyboardButton("Caption", callback_data=f"set_caption_{fuuid}"), InlineKeyboardButton("Delete", callback_data=f"del_file_{fuuid}")]])
        await pm.edit(text, reply_markup=btns)
    except Exception as e:
        await pm.edit(f"Error: {e}")

@Client.on_message(MEDIA & filters.channel)
async def handle_channel(client, message):
    if message.chat.id != Config.DB_CHANNEL_ID:
        return
    fi = get_file_info(message)
    if fi:
        await save_file(fi["file_id"], fi["file_ref"], fi["file_name"], fi["file_size"], fi["file_type"], fi["mime_type"], 0, message.id, message.chat.id, message.caption)
