import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
    OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
    ADMINS = list(set([int(os.environ.get("OWNER_ID", "0"))] + [int(x) for x in os.environ.get("ADMINS", "").split() if x.isdigit()]))
    MONGO_URI = os.environ.get("MONGO_URI", "")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "FileToLinkBot")
    DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", "0"))
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "0"))
    FORCE_SUB_CHANNELS = [int(x) for x in os.environ.get("FORCE_SUB_CHANNELS", "").split() if x]
    WEB_SERVER_BIND = "0.0.0.0"
    WEB_SERVER_PORT = int(os.environ.get("PORT", 8080))
    FQDN = os.environ.get("FQDN", "")
    HAS_SSL = os.environ.get("HAS_SSL", "True").lower() == "true"
    URL_PREFIX = "https" if HAS_SSL else "http"
    BASE_URL = f"{URL_PREFIX}://{FQDN}" if FQDN else ""
    CF_ENABLED = os.environ.get("CF_ENABLED", "False").lower() == "true"
    CF_WORKER_URL = os.environ.get("CF_WORKER_URL", "")
    CF_SECRET_KEY = os.environ.get("CF_SECRET_KEY", "default-secret")
    SHORTENER_ENABLED = os.environ.get("SHORTENER_ENABLED", "False").lower() == "true"
    SHORTENER_API = os.environ.get("SHORTENER_API", "")
    SHORTENER_URL = os.environ.get("SHORTENER_URL", "")
    AUTO_DELETE_ENABLED = os.environ.get("AUTO_DELETE_ENABLED", "True").lower() == "true"
    AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", "600"))
    VERIFY_ENABLED = os.environ.get("VERIFY_ENABLED", "False").lower() == "true"
    VERIFY_TUTORIAL_URL = os.environ.get("VERIFY_TUTORIAL_URL", "")
    TOKEN_TIMEOUT = int(os.environ.get("TOKEN_TIMEOUT", "86400"))
    PROTECT_CONTENT = os.environ.get("PROTECT_CONTENT", "False").lower() == "true"
    CUSTOM_START_MSG = os.environ.get("CUSTOM_START_MSG", None)
    CUSTOM_START_PIC = os.environ.get("CUSTOM_START_PIC", None)
    GET_FILE_AGAIN_BTN = os.environ.get("GET_FILE_AGAIN_BTN", "True").lower() == "true"
    CLONE_ENABLED = os.environ.get("CLONE_ENABLED", "True").lower() == "true"
    REDIRECT_BOT_USERNAME = os.environ.get("REDIRECT_BOT_USERNAME", "")
    REDIRECT_ENABLED = os.environ.get("REDIRECT_ENABLED", "False").lower() == "true"
