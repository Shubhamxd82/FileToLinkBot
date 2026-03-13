from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from database.files_db import create_batch
from helpers.link_generator import LinkGenerator
from helpers.shortener_api import shorten_url

batch_sessions = {}


@Client.on_message(filters.command("batch") & filters.private)
async def batch_cmd(client, message):
    uid = message.from_user.id
    if uid in batch_sessions and batch_sessions[uid]["active"]:
        return await message.reply("Already in batch mode. /endbatch or /cancelbatch")
    batch_sessions[uid] = {"files": [], "active": True}
    await message.reply("Batch started! Send files, then /endbatch")


@Client.on_message(filters.command("endbatch") & filters.private)
async def end_batch(client, message):
    uid = message.from_user.id
    if uid not in batch_sessions or not batch_sessions[uid]["active"]:
        return await message.reply("No active batch.")
    files = batch_sessions[uid]["files"]
    if not files:
        del batch_sessions[uid]
        return await message.reply("No files. Cancelled.")
    buuid = await create_batch(uid, files)
    bl = await LinkGenerator.generate_batch_link(buuid)
    bls = await shorten_url(bl, uid)
    del batch_sessions[uid]
    await message.reply(
        f"**Batch Created!**\nFiles: {len(files)}\nLink: `{bls}`",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Share", url=bl)]]
        )
    )


@Client.on_message(filters.command("cancelbatch") & filters.private)
async def cancel_batch(client, message):
    uid = message.from_user.id
    if uid in batch_sessions:
        del batch_sessions[uid]
    await message.reply("Batch cancelled.")


async def check_batch_mode(client, message, file_uuid):
    uid = message.from_user.id
    if uid in batch_sessions and batch_sessions[uid]["active"]:
        batch_sessions[uid]["files"].append(file_uuid)
        await message.reply(f"File #{len(batch_sessions[uid]['files'])} added to batch.")
        return True
    return False
