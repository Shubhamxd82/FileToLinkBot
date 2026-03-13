import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import Config
from database.users_db import add_user, is_user_banned, is_user_verified
from database.files_db import get_file, get_batch_files, increment_access
from database.settings_db import get_settings, get_force_sub_channels
from helpers.link_generator import LinkGenerator
from helpers.shortener_api import shorten_url
from helpers.utils import check_force_sub, get_force_sub_buttons, auto_delete_message, get_readable_time
from helpers.file_properties import get_human_size

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    uid = message.from_user.id
    s = await get_settings()
    await add_user(uid, message.from_user.username, message.from_user.first_name)
    if await is_user_banned(uid):
        return await message.reply("Banned.")
    fsub = await get_force_sub_channels()
    if fsub and uid not in Config.ADMINS:
        nj = await check_force_sub(client, uid, fsub)
        if nj:
            return await message.reply("Join channels first:", reply_markup=await get_force_sub_buttons(client, nj))
    if s.get("verify_enabled") and uid not in Config.ADMINS:
        if not await is_user_verified(uid):
            btns = []
            if s.get("verify_tutorial_url"):
                btns.append([InlineKeyboardButton("Tutorial", url=s["verify_tutorial_url"])])
            btns.append([InlineKeyboardButton("Get Token", callback_data="get_verify_token")])
            return await message.reply("Verification required.", reply_markup=InlineKeyboardMarkup(btns))
    args = message.text.split(" ", 1)
    if len(args) > 1:
        p = args[1]
        if p.startswith("file_"):
            fuuid = LinkGenerator.decode_file_uuid(p[5:])
            if not fuuid:
                return await message.reply("Invalid link.")
            fd = await get_file(fuuid)
            if not fd:
                return await message.reply("File not found.")
            return await send_file(client, message, fd, s)
        elif p.startswith("batch_"):
            buuid = LinkGenerator.decode_file_uuid(p[6:])
            if not buuid:
                return await message.reply("Invalid batch.")
            files = await get_batch_files(buuid)
            if not files:
                return await message.reply("Batch empty.")
            st = await message.reply(f"Sending {len(files)} files...")
            for i, fd in enumerate(files):
                await send_file(client, message, fd, s)
                if i < len(files)-1:
                    await asyncio.sleep(1)
            return await st.delete()
        elif p.startswith("verify_"):
            from plugins.token_verify import handle_verify_callback
            return await handle_verify_callback(client, message, p[7:])
    text = s.get("custom_start_msg") or f"Hello {message.from_user.mention}!\n\nI'm a File to Link bot.\nSend me any file!"
    pic = s.get("custom_start_pic")
    btns = InlineKeyboardMarkup([[InlineKeyboardButton("Help", callback_data="help_menu"), InlineKeyboardButton("Clone", callback_data="clone_info")]])
    if pic:
        await message.reply_photo(pic, caption=text, reply_markup=btns)
    else:
        await message.reply(text, reply_markup=btns)

async def send_file(client, message, fd, s):
    try:
        msg = await client.get_messages(fd["channel_id"], fd["message_id"])
        if not msg or msg.empty:
            return await message.reply("File unavailable.")
        cap = fd.get("custom_caption") or fd.get("caption") or ""
        btns = []
        sl = await shorten_url(await LinkGenerator.generate_stream_link(fd["file_uuid"]), message.from_user.id)
        dl = await shorten_url(await LinkGenerator.generate_download_link(fd["file_uuid"]), message.from_user.id)
        btns.append([InlineKeyboardButton("Stream", url=sl), InlineKeyboardButton("Download", url=dl)])
        if fd.get("custom_buttons"):
            for row in fd["custom_buttons"]:
                btns.append([InlineKeyboardButton(b["text"], url=b["url"]) for b in row])
        if s.get("get_file_again_btn", True):
            bl = await LinkGenerator.generate_bot_link(fd["file_uuid"])
            btns.append([InlineKeyboardButton("Get Again", url=bl)])
        sent = await msg.copy(message.chat.id, caption=cap or None, reply_markup=InlineKeyboardMarkup(btns) if btns else None, protect_content=s.get("protect_content", False))
        await increment_access(fd["file_uuid"])
        if s.get("auto_delete_enabled"):
            dt = fd.get("auto_delete_time") or s.get("auto_delete_time", 600)
            notice = await message.reply(f"Auto-delete in {get_readable_time(dt)}")
            asyncio.create_task(auto_delete_message(sent, dt))
            asyncio.create_task(auto_delete_message(notice, dt))
    except Exception as e:
        await message.reply(f"Error: {e}")

@Client.on_callback_query(filters.regex("^check_force_sub$"))
async def fsub_cb(client, cb):
    nj = await check_force_sub(client, cb.from_user.id, await get_force_sub_channels())
    if nj:
        await cb.answer("Join all channels first!", show_alert=True)
    else:
        await cb.message.delete()
        await cb.answer("Verified! Send /start", show_alert=True)

@Client.on_callback_query(filters.regex("^help_menu$"))
async def help_cb(client, cb):
    await cb.message.edit("**Commands:**\n/start /batch /endbatch /clone /settings /stats /broadcast /ban /unban", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back_start")]]))

@Client.on_callback_query(filters.regex("^back_start$"))
async def back_cb(client, cb):
    s = await get_settings()
    text = s.get("custom_start_msg") or f"Hello {cb.from_user.mention}!\nSend me any file!"
    await cb.message.edit(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Help", callback_data="help_menu"), InlineKeyboardButton("Clone", callback_data="clone_info")]]))
