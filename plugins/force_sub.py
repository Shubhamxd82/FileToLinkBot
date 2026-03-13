from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import Config
from database.settings_db import get_settings, get_force_sub_channels, add_force_sub_channel, remove_force_sub_channel

@Client.on_chat_join_request()
async def join_req(client, req: ChatJoinRequest):
    s = await get_settings()
    if not s.get("request_to_join"):
        return
    fsub = await get_force_sub_channels()
    if req.chat.id not in fsub:
        return
    try:
        await req.approve()
        await client.send_message(req.from_user.id, "Approved! /start", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Start", url=f"https://t.me/{Config.BOT_USERNAME}?start=start")]]))
    except:
        pass

@Client.on_message(filters.command("fsub") & filters.private & filters.user(Config.ADMINS))
async def fsub_cmd(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("/fsub add ID\n/fsub remove ID\n/fsub list")
    if args[1] == "add" and len(args) > 2:
        await add_force_sub_channel(int(args[2]))
        await message.reply("Added!")
    elif args[1] == "remove" and len(args) > 2:
        await remove_force_sub_channel(int(args[2]))
        await message.reply("Removed!")
    elif args[1] == "list":
        ch = await get_force_sub_channels()
        await message.reply(f"Channels: {ch}" if ch else "None.")
