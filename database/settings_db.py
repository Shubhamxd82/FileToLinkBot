from database.mongo import get_col

DEFAULT = {"setting_id":"global","custom_start_msg":None,"custom_start_pic":None,"shortener_enabled":False,"shortener_url":None,"shortener_api":None,"auto_delete_enabled":True,"auto_delete_time":600,"verify_enabled":False,"verify_tutorial_url":None,"token_timeout":86400,"protect_content":False,"get_file_again_btn":True,"cf_enabled":False,"cf_worker_url":None,"cf_secret_key":None,"force_sub_channels":[],"request_to_join":False,"redirect_enabled":False,"redirect_bot_username":None}

async def get_settings(sid="global"):
    col = get_col("settings")
    s = await col.find_one({"setting_id": sid})
    if not s:
        s = {**DEFAULT, "setting_id": sid}
        await col.insert_one(s)
    return s

async def update_setting(key, value, sid="global"):
    await get_col("settings").update_one({"setting_id": sid}, {"$set": {key: value}}, upsert=True)

async def toggle_setting(key, sid="global"):
    s = await get_settings(sid)
    new = not s.get(key, False)
    await update_setting(key, new, sid)
    return new

async def add_force_sub_channel(channel_id, sid="global"):
    await get_col("settings").update_one({"setting_id": sid}, {"$addToSet": {"force_sub_channels": channel_id}}, upsert=True)

async def remove_force_sub_channel(channel_id, sid="global"):
    await get_col("settings").update_one({"setting_id": sid}, {"$pull": {"force_sub_channels": channel_id}})

async def get_force_sub_channels(sid="global"):
    s = await get_settings(sid)
    return s.get("force_sub_channels", [])
