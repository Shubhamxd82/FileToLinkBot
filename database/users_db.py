import datetime
from database.mongo import get_col

async def add_user(user_id, username=None, first_name=None):
    col = get_col("users")
    await col.update_one({"user_id": user_id}, {"$setOnInsert": {
        "user_id": user_id, "username": username, "first_name": first_name,
        "joined_date": datetime.datetime.utcnow(), "is_banned": False,
        "is_premium": False, "premium_expiry": None, "verified": False,
        "verify_token": None, "verify_expiry": None, "shortener_enabled": None,
        "custom_shortener_api": None, "custom_shortener_url": None, "files_count": 0
    }}, upsert=True)

async def get_user(user_id):
    return await get_col("users").find_one({"user_id": user_id})

async def get_all_users():
    return get_col("users").find({})

async def total_users():
    return await get_col("users").count_documents({})

async def ban_user(user_id):
    await get_col("users").update_one({"user_id": user_id}, {"$set": {"is_banned": True}})

async def unban_user(user_id):
    await get_col("users").update_one({"user_id": user_id}, {"$set": {"is_banned": False}})

async def is_user_banned(user_id):
    user = await get_user(user_id)
    return user.get("is_banned", False) if user else False

async def set_premium(user_id, expiry=None):
    await get_col("users").update_one({"user_id": user_id}, {"$set": {"is_premium": True, "premium_expiry": expiry}})

async def remove_premium(user_id):
    await get_col("users").update_one({"user_id": user_id}, {"$set": {"is_premium": False, "premium_expiry": None}})

async def is_premium(user_id):
    user = await get_user(user_id)
    if not user or not user.get("is_premium"):
        return False
    expiry = user.get("premium_expiry")
    if expiry and expiry < datetime.datetime.utcnow():
        await remove_premium(user_id)
        return False
    return True

async def set_user_verified(user_id, token, expiry):
    await get_col("users").update_one({"user_id": user_id}, {"$set": {"verified": True, "verify_token": token, "verify_expiry": expiry}})

async def is_user_verified(user_id):
    user = await get_user(user_id)
    if not user or not user.get("verified"):
        return False
    expiry = user.get("verify_expiry")
    if expiry and expiry < datetime.datetime.utcnow():
        await get_col("users").update_one({"user_id": user_id}, {"$set": {"verified": False, "verify_token": None, "verify_expiry": None}})
        return False
    return True

async def add_group(group_id, title=None):
    await get_col("groups").update_one({"group_id": group_id}, {"$setOnInsert": {
        "group_id": group_id, "title": title, "joined_date": datetime.datetime.utcnow(), "is_banned": False
    }}, upsert=True)

async def get_all_groups():
    return get_col("groups").find({})

async def total_groups():
    return await get_col("groups").count_documents({})
