from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import Config
from database.files_db import get_file, update_file_caption

pending = {}

@Client.on_callback_query(filters.regex("^set_caption_"))
async def set_cap(client, cb):
    fuuid = cb.data.replace("set_caption_", "")
    fd = await get_file(fuuid)
    if not fd:
        return await cb.answer("Not found!", show_alert=True)
    if fd["user_id"] != cb.from_user.id and cb.from_user.id not in Config.ADMINS:
        return await cb.answer("Not yours!", show_alert=True)
    pending[cb.from_user.id] = {"fuuid": fuuid, "step": "caption"}
    await cb.message.edit("Send new caption.\nVars: {file_name} {file_size}\n/skip or /remove", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="cancel_cap")]]))

@Client.on_callback_query(filters.regex("^del_file_"))
async def del_file_cb(client, cb):
    from database.files_db import delete_file
    fuuid = cb.data.replace("del_file_", "")
    await delete_file(fuuid)
    await cb.answer("Deleted!", show_alert=True)
    await cb.message.delete()

@Client.on_callback_query(filters.regex("^cancel_cap$"))
async def cancel_cap(client, cb):
    if cb.from_user.id in pending:
        del pending[cb.from_user.id]
    await cb.message.delete()
