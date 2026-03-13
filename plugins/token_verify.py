import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import Config
from database.tokens_db import generate_token, verify_token
from database.users_db import set_user_verified, is_user_verified
from database.settings_db import get_settings
from helpers.shortener_api import shorten_url

@Client.on_callback_query(filters.regex("^get_verify_token$"))
async def get_token(client, cb):
    s = await get_settings()
    if not s.get("verify_enabled"):
        return await cb.answer("Disabled.", show_alert=True)
    if await is_user_verified(cb.from_user.id):
        return await cb.answer("Already verified!", show_alert=True)
    raw = await generate_token(cb.from_user.id, s.get("token_timeout", 86400))
    link = f"https://t.me/{Config.BOT_USERNAME}?start=verify_{raw}"
    short = await shorten_url(link, cb.from_user.id)
    btns = []
    if s.get("verify_tutorial_url"):
        btns.append([InlineKeyboardButton("Tutorial", url=s["verify_tutorial_url"])])
    btns.append([InlineKeyboardButton("Verify", url=short)])
    await cb.message.edit(f"Click to verify.\nExpires in {s.get('token_timeout',86400)//3600}h", reply_markup=InlineKeyboardMarkup(btns))

async def handle_verify_callback(client, message, token):
    s = await get_settings()
    uid = message.from_user.id
    if await is_user_verified(uid):
        return await message.reply("Already verified!")
    ok, msg = await verify_token(uid, token)
    if ok:
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=s.get("token_timeout", 86400))
        await set_user_verified(uid, token, exp)
        await message.reply("Verified! Send /start")
    else:
        await message.reply(f"Failed: {msg}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("New Token", callback_data="get_verify_token")]]))
