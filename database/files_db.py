import datetime, secrets
from database.mongo import get_col

async def save_file(file_id, file_ref, file_name, file_size, file_type, mime_type, user_id, message_id, channel_id, caption=None, custom_caption=None, custom_buttons=None, auto_delete_time=None):
    col = get_col("files")
    file_uuid = secrets.token_urlsafe(12)
    await col.insert_one({
        "file_uuid": file_uuid, "file_id": file_id, "file_ref": file_ref,
        "file_name": file_name, "file_size": file_size, "file_type": file_type,
        "mime_type": mime_type, "user_id": user_id, "message_id": message_id,
        "channel_id": channel_id, "caption": caption, "custom_caption": custom_caption,
        "custom_buttons": custom_buttons or [], "auto_delete_time": auto_delete_time,
        "created_at": datetime.datetime.utcnow(), "access_count": 0, "is_active": True
    })
    return file_uuid

async def get_file(file_uuid):
    return await get_col("files").find_one({"file_uuid": file_uuid, "is_active": True})

async def increment_access(file_uuid):
    await get_col("files").update_one({"file_uuid": file_uuid}, {"$inc": {"access_count": 1}})

async def update_file_caption(file_uuid, custom_caption, custom_buttons=None):
    update = {"custom_caption": custom_caption}
    if custom_buttons is not None:
        update["custom_buttons"] = custom_buttons
    await get_col("files").update_one({"file_uuid": file_uuid}, {"$set": update})

async def delete_file(file_uuid):
    await get_col("files").update_one({"file_uuid": file_uuid}, {"$set": {"is_active": False}})

async def total_files():
    return await get_col("files").count_documents({"is_active": True})

async def create_batch(user_id, file_uuids):
    col = get_col("batches")
    batch_uuid = secrets.token_urlsafe(12)
    await col.insert_one({"batch_uuid": batch_uuid, "user_id": user_id, "file_uuids": file_uuids, "created_at": datetime.datetime.utcnow(), "is_active": True})
    return batch_uuid

async def get_batch(batch_uuid):
    return await get_col("batches").find_one({"batch_uuid": batch_uuid, "is_active": True})

async def get_batch_files(batch_uuid):
    batch = await get_batch(batch_uuid)
    if not batch:
        return []
    files = []
    for fuuid in batch.get("file_uuids", []):
        f = await get_col("files").find_one({"file_uuid": fuuid, "is_active": True})
        if f:
            files.append(f)
    return files
