from database.mongo import get_col

async def get_user_shortener(user_id):
    return await get_col("shortener").find_one({"user_id": user_id})

async def set_user_shortener(user_id, api_key, base_url, enabled=True):
    await get_col("shortener").update_one({"user_id": user_id}, {"$set": {"user_id": user_id, "api_key": api_key, "base_url": base_url, "enabled": enabled}}, upsert=True)
