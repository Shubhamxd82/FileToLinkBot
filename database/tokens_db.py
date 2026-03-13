import datetime, secrets, hashlib
from database.mongo import get_col

async def generate_token(user_id, timeout=86400):
    raw = secrets.token_urlsafe(32)
    h = hashlib.sha256(raw.encode()).hexdigest()
    await get_col("tokens").insert_one({"user_id": user_id, "token_hash": h, "created_at": datetime.datetime.utcnow(), "expires_at": datetime.datetime.utcnow() + datetime.timedelta(seconds=timeout), "is_used": False, "is_active": True})
    return raw

async def verify_token(user_id, raw_token):
    h = hashlib.sha256(raw_token.encode()).hexdigest()
    t = await get_col("tokens").find_one({"user_id": user_id, "token_hash": h, "is_active": True})
    if not t:
        return False, "Invalid token."
    if t["expires_at"] < datetime.datetime.utcnow():
        await get_col("tokens").update_one({"_id": t["_id"]}, {"$set": {"is_active": False}})
        return False, "Token expired."
    await get_col("tokens").update_one({"_id": t["_id"]}, {"$set": {"is_used": True}})
    return True, "Verified."

async def revoke_all_tokens(user_id):
    await get_col("tokens").update_many({"user_id": user_id}, {"$set": {"is_active": False}})
