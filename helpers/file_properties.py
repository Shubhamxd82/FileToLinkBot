from pyrogram.types import Message


def get_file_info(message: Message):
    media_types = [
        ("document", "document"),
        ("video", "video"),
        ("audio", "audio"),
        ("photo", "photo"),
        ("voice", "voice"),
        ("video_note", "video_note"),
        ("sticker", "sticker"),
        ("animation", "animation"),
    ]

    for attr, ftype in media_types:
        m = getattr(message, attr, None)
        if m:
            fid = m.file_id
            fref = getattr(m, "file_reference", None)
            fname = getattr(m, "file_name", None) or f"{ftype}_{fid[:10]}"
            fsize = getattr(m, "file_size", 0) or 0
            mime = getattr(m, "mime_type", "application/octet-stream")

            # Handle file_reference
            if isinstance(fref, bytes):
                fref_str = fref.hex()
            elif fref:
                fref_str = str(fref)
            else:
                fref_str = None

            return {
                "file_id": fid,
                "file_ref": fref_str,
                "file_name": fname,
                "file_size": fsize,
                "file_type": ftype,
                "mime_type": mime,
            }

    return None


def get_human_size(size):
    if not size:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    s = float(size)
    while s >= 1024 and i < len(units) - 1:
        s /= 1024
        i += 1
    return f"{s:.2f} {units[i]}"
