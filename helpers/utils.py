import asyncio
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

def parse_buttons(text):
    buttons = []
    for line in text.strip().split("\n"):
        row = []
        for part in line.split("]["):
            part = part.strip("[]").strip()
            if " - " in part:
                t, u = part.rsplit(" - ", 1)
                row.append(InlineKeyboardButton(t.strip(), url=u.strip()))
        if row:
            buttons.append(row)
    return buttons

async def auto_delete_message(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

def get_readable_time(seconds):
    r = ""
    for n, s in [("d",86400),("h",3600),("m",60),("s",1)]:
        if seconds >= s:
            v, seconds = divmod(seconds, s)
            r += f"{int(v)}{n} "
    return r.strip() or "0s"

async def check_force_sub(client, user_id, channels):
    nj = []
    for ch in channels:
        try:
            m = await client.get_chat_member(ch, user_id)
            if m.status in ["left","kicked"]:
                nj.append(ch)
        except:
            nj.append(ch)
    return nj

async def get_force_sub_buttons(client, channels):
    btns = []
    for ch in channels:
        try:
            c = await client.get_chat(ch)
            link = c.invite_link or await client.export_chat_invite_link(ch)
            btns.append([InlineKeyboardButton(f"Join {c.title}", url=link)])
        except:
            pass
    btns.append([InlineKeyboardButton("Try Again", callback_data="check_force_sub")])
    return InlineKeyboardMarkup(btns)
