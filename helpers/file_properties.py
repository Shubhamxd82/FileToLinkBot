from pyrogram.types import Message

def get_file_info(message: Message):
    for attr, ftype in [("document","document"),("video","video"),("audio","audio"),("photo","photo"),("voice","voice"),("video_note","video_note"),("sticker","sticker"),("animation","animation")]:
        m = getattr(message, attr, None)
        if m:
            fid = m.file_id
            fref = getattr(m, "file_reference", None)
            fname = getattr(m, "file_name", None) or f"{ftype}_{fid[:10]}"
            fsize = getattr(m, "file_size", 0) or 0
            mime = getattr(m, "mime_type", "application/octet-stream")
            return {"file_id": fid, "file_ref": fref.hex() if isinstance(fref, bytes) else str(fref) if fref else None, "file_name": fname, "file_size": fsize, "file_type": ftype, "mime_type": mime}
    return None

def get_human_size(size):
    if not size:
        return "0 B"
    units = ["B","KB","MB","GB","TB"]
    i = 0
    s = float(size)
    while s >= 1024 and i < len(units)-1:
        s /= 1024
        i += 1
    return f"{s:.2f} {units[i]}"
