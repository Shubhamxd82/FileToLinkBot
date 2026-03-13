from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import Config
from database.clone_db import add_clone, get_user_clones, get_all_clones, total_clones

clone_instances = {}

@Client.on_message(filters.command("clone") & filters.private)
async def clone_cmd(client, message):
    if not Config.CLONE_ENABLED:
        return await message.reply("Clone disabled.")
    args = message.text.split(" ", 1)
    if len(args) < 2:
        return await message.reply("Send: /clone YOUR_BOT_TOKEN")
    token = args[1].strip()
    st = await message.reply("Setting up clone...")
    try:
        c = Client(f"clone_{message.from_user.id}", Config.API_ID, Config.API_HASH, bot_token=token, in_memory=True, plugins=dict(root="plugins"))
        await c.start()
        info = await c.get_me()
        await add_clone(message.from_user.id, token, info.username, Config.API_ID, Config.API_HASH)
        clone_instances[token] = c
        await st.edit(f"Clone @{info.username} created!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"Open @{info.username}", url=f"https://t.me/{info.username}")]]))
    except Exception as e:
        await st.edit(f"Failed: {e}")

@Client.on_message(filters.command("myclones") & filters.private)
async def myclones(client, message):
    clones = get_user_clones(message.from_user.id)
    text = "**Your Clones:**\n"
    n = 0
    async for c in clones:
        n += 1
        text += f"{n}. @{c['bot_username']}\n"
    if n == 0:
        text += "None. Use /clone"
    await message.reply(text)

@Client.on_callback_query(filters.regex("^clone_info$"))
async def clone_info(client, cb):
    t = await total_clones()
    await cb.message.edit(f"**Clone Bot**\nTotal: {t}\nUse /clone BOT_TOKEN", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back_start")]]))

async def start_all_clones():
    clones = get_all_clones()
    n = 0
    async for c in clones:
        try:
            cl = Client(f"clone_{c['bot_username']}", c.get("api_id") or Config.API_ID, c.get("api_hash") or Config.API_HASH, bot_token=c["bot_token"], in_memory=True, plugins=dict(root="plugins"))
            await cl.start()
            clone_instances[c["bot_token"]] = cl
            n += 1
        except:
            pass
    print(f"Started {n} clones")
