import datetime
from database.mongo import get_col

async def add_clone(user_id, bot_token, bot_username, api_id=None, api_hash=None):
    await get_col("clones").update_one({"bot_token": bot_token}, {"$set": {"user_id": user_id, "bot_token": bot_token, "bot_username": bot_username, "api_id": api_id, "api_hash": api_hash, "created_at": datetime.datetime.utcnow(), "is_active": True, "is_premium": False}}, upsert=True)

async def get_all_clones():
    return await get_col("clones").find({"is_active": True}).to_list(None)

async def get_user_clones(user_id):
    return await get_col("clones").find({"user_id": user_id, "is_active": True}).to_list(None)

async def remove_clone(bot_token):
    await get_col("clones").update_one({"bot_token": bot_token}, {"$set": {"is_active": False}})

async def total_clones():
    return await get_col("clones").count_documents({"is_active": True})
