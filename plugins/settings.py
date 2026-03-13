from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import Config
from database.settings_db import get_settings, update_setting, toggle_setting, add_force_sub_channel, remove_force_sub_channel

@Client.on_message(filters.command("settings") & filters.private & filters.user(Config.ADMINS))
async def settings_cmd(client, message):
    await show_settings(client, message)

async def show_settings(client, msg_or_cb, edit=False):
    s = await get_settings()
    ic = lambda k: "✅" if s.get(k) else "❌"
    text = f"**Settings**\nShortener: {ic('shortener_enabled')}\nAuto-Del: {ic('auto_delete_enabled')} ({s.get('auto_delete_time',600)}s)\nVerify: {ic('verify_enabled')}\nProtect: {ic('protect_content')}\nGetAgain: {ic('get_file_again_btn')}\nCF: {ic('cf_enabled')}\nRedirect: {ic('redirect_enabled')}\nFSub: {len(s.get('force_sub_channels',[]))}"
    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{ic('shortener_enabled')} Shortener", callback_data="toggle_shortener_enabled"), InlineKeyboardButton(f"{ic('auto_delete_enabled')} AutoDel", callback_data="toggle_auto_delete_enabled")],
        [InlineKeyboardButton(f"{ic('verify_enabled')} Verify", callback_data="toggle_verify_enabled"), InlineKeyboardButton(f"{ic('protect_content')} Protect", callback_data="toggle_protect_content")],
        [InlineKeyboardButton(f"{ic('get_file_again_btn')} GetAgain", callback_data="toggle_get_file_again_btn"), InlineKeyboardButton(f"{ic('cf_enabled')} CF", callback_data="toggle_cf_enabled")],
        [InlineKeyboardButton(f"{ic('redirect_enabled')} Redirect", callback_data="toggle_redirect_enabled"), InlineKeyboardButton(f"{ic('request_to_join')} ReqJoin", callback_data="toggle_request_to_join")],
        [InlineKeyboardButton("Set Del Time", callback_data="set_del_time"), InlineKeyboardButton("Close", callback_data="close_settings")]
    ])
    if edit and isinstance(msg_or_cb, CallbackQuery):
        await msg_or_cb.message.edit(text, reply_markup=btns)
    else:
        t = msg_or_cb if isinstance(msg_or_cb, Message) else msg_or_cb.message
        await t.reply(text, reply_markup=btns)

@Client.on_callback_query(filters.regex("^toggle_") & filters.user(Config.ADMINS))
async def toggle_cb(client, cb):
    key = cb.data.replace("toggle_", "")
    new = await toggle_setting(key)
    await cb.answer(f"{'ON' if new else 'OFF'}", show_alert=True)
    await show_settings(client, cb, edit=True)

@Client.on_callback_query(filters.regex("^set_del_time$") & filters.user(Config.ADMINS))
async def del_time_cb(client, cb):
    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton("5m", callback_data="adt_300"), InlineKeyboardButton("10m", callback_data="adt_600"), InlineKeyboardButton("30m", callback_data="adt_1800")],
        [InlineKeyboardButton("1h", callback_data="adt_3600"), InlineKeyboardButton("6h", callback_data="adt_21600"), InlineKeyboardButton("24h", callback_data="adt_86400")],
        [InlineKeyboardButton("Back", callback_data="back_settings")]
    ])
    await cb.message.edit("Select auto-delete time:", reply_markup=btns)

@Client.on_callback_query(filters.regex("^adt_") & filters.user(Config.ADMINS))
async def adt_cb(client, cb):
    t = int(cb.data.replace("adt_", ""))
    await update_setting("auto_delete_time", t)
    await cb.answer(f"Set to {t}s", show_alert=True)
    await show_settings(client, cb, edit=True)

@Client.on_callback_query(filters.regex("^back_settings$") & filters.user(Config.ADMINS))
async def back_set(client, cb):
    await show_settings(client, cb, edit=True)

@Client.on_callback_query(filters.regex("^close_settings$"))
async def close_set(client, cb):
    await cb.message.delete()
