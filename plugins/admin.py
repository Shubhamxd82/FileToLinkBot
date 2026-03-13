import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database.users_db import total_users, total_groups, ban_user, unban_user, set_premium, remove_premium, get_user
from database.files_db import total_files
from database.clone_db import total_clones
from database.mongo import MongoDB
from helpers.redirect_manager import RedirectManager

@Client.on_message(filters.command("stats") & filters.private & filters.user(Config.ADMINS))
async def stats(client, message):
    u = await total_users()
    g = await total_groups()
    f = await total_files()
    c = await total_clones()
    db = "ON" if await MongoDB.ping() else "OFF"
    await message.reply(f"**Stats**\nUsers: {u}\nGroups: {g}\nFiles: {f}\nClones: {c}\nDB: {db}")

@Client.on_message(filters.command("ban") & filters.private & filters.user(Config.ADMINS))
async def ban(client, message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("/ban USER_ID")
    await ban_user(int(args[1]))
    await message.reply(f"Banned {args[1]}")

@Client.on_message(filters.command("unban") & filters.private & filters.user(Config.ADMINS))
async def unban(client, message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("/unban USER_ID")
    await unban_user(int(args[1]))
    await message.reply(f"Unbanned {args[1]}")

@Client.on_message(filters.command("addpremium") & filters.private & filters.user(Config.ADMINS))
async def addprem(client, message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("/addpremium UID [DAYS]")
    days = int(args[2]) if len(args) > 2 else 30
    exp = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    await set_premium(int(args[1]), exp)
    await message.reply(f"Premium for {args[1]}, {days}d")

@Client.on_message(filters.command("rmpremium") & filters.private & filters.user(Config.ADMINS))
async def rmprem(client, message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("/rmpremium UID")
    await remove_premium(int(args[1]))
    await message.reply(f"Removed premium {args[1]}")

@Client.on_message(filters.command("userinfo") & filters.private & filters.user(Config.ADMINS))
async def uinfo(client, message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("/userinfo UID")
    u = await get_user(int(args[1]))
    if not u:
        return await message.reply("Not found.")
    await message.reply(f"ID: {u['user_id']}\nName: {u.get('first_name')}\nBanned: {u.get('is_banned')}\nPremium: {u.get('is_premium')}\nVerified: {u.get('verified')}")

@Client.on_message(filters.command("redirect") & filters.private & filters.user(Config.ADMINS))
async def redirect_cmd(client, message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("/redirect set BOT_USERNAME\n/redirect off\n/redirect status")
    if args[1] == "set" and len(args) > 2:
        await RedirectManager.activate_redirect(args[2].replace("@",""))
        await message.reply(f"Redirect to @{args[2]}")
    elif args[1] == "off":
        await RedirectManager.deactivate_redirect()
        await message.reply("Redirect OFF")
    elif args[1] == "status":
        bot = await RedirectManager.get_active_bot_username()
        await message.reply(f"Active: @{bot}")

@Client.on_message(filters.command("shortener") & filters.private)
async def shortener_cmd(client, message):
    from database.users_db import get_user as gu
    from database.settings_db import get_settings as gs
    from database.mongo import get_col
    uid = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        s = await gs()
        u = await gu(uid)
        return await message.reply(f"Global: {'ON' if s.get('shortener_enabled') else 'OFF'}\nYours: {u.get('shortener_enabled','Global')}\n\n/shortener on|off\n/shortener set API URL\n/shortener reset")
    a = args[1].lower()
    col = get_col("users")
    if a == "on":
        await col.update_one({"user_id": uid}, {"$set": {"shortener_enabled": True}})
        await message.reply("ON")
    elif a == "off":
        await col.update_one({"user_id": uid}, {"$set": {"shortener_enabled": False}})
        await message.reply("OFF")
    elif a == "set" and len(args) >= 4:
        await col.update_one({"user_id": uid}, {"$set": {"custom_shortener_api": args[2], "custom_shortener_url": args[3], "shortener_enabled": True}})
        await message.reply(f"Set: {args[3]}")
    elif a == "reset":
        await col.update_one({"user_id": uid}, {"$set": {"custom_shortener_api": None, "custom_shortener_url": None, "shortener_enabled": None}})
        await message.reply("Reset.")
