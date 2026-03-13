import asyncio, logging
from pyrogram import Client, idle
from config import Config
from database.mongo import MongoDB
from web.stream_server import StreamServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class FileToLinkBot:
    def __init__(self):
        self.bot = Client("FileToLinkBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN, plugins=dict(root="plugins"), workers=8, in_memory=True)
        self.stream = None

    async def start(self):
        logger.info("Connecting to MongoDB...")
        MongoDB.get_instance()
        if await MongoDB.ping():
            logger.info("MongoDB connected!")
        else:
            logger.error("MongoDB failed!")
            return
        logger.info("Starting bot...")
        await self.bot.start()
        info = await self.bot.get_me()
        Config.BOT_USERNAME = info.username
        logger.info(f"Bot: @{info.username}")
        logger.info("Starting stream server...")
        self.stream = StreamServer(self.bot)
        await self.stream.start()
        logger.info("Starting clones...")
        from plugins.clone import start_all_clones
        await start_all_clones()
        try:
            await self.bot.send_message(Config.LOG_CHANNEL_ID, f"Bot Started!\n@{info.username}\n{Config.BASE_URL}")
        except:
            pass
        logger.info("Bot is running!")
        await idle()

    async def stop(self):
        await self.bot.stop()
        await MongoDB.close()

if __name__ == "__main__":
    bot = FileToLinkBot()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.start())
    except KeyboardInterrupt:
        loop.run_until_complete(bot.stop())
