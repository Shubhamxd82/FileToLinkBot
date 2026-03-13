import asyncio, datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from config import Config
from database.users_db import get_all_users, get_all_groups

@Client.on_message(filters.command("broadcast") & filters.private & filters.user(Config.ADMINS))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast.")
    st = await message.reply("Broadcasting...")
    users = get_all_users()
    total = success = failed = 0
    async for u in users:
        total += 1
        try:
            await message.reply_to_message.copy(u["user_id"])
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            failed += 1
    await st.edit(f"Done!\nSuccess: {success}\nFailed: {failed}\nTotal: {total}")

@Client.on_message(filters.command("gbroadcast") & filters.private & filters.user(Config.ADMINS))
async def gbroadcast(client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message.")
    pin = "pin" in message.text.lower()
    st = await message.reply("Broadcasting to groups...")
    groups = get_all_groups()
    total = success = pinned = 0
    async for g in groups:
        total += 1
        try:
            sent = await message.reply_to_message.copy(g["group_id"])
            success += 1
            if pin:
                try:
                    await sent.pin()
                    pinned += 1
                except:
                    pass
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            pass
    await st.edit(f"Done!\nSuccess: {success}\nPinned: {pinned}\nTotal: {total}")
