import asyncio
import logging
import os
from telegram import Bot, Update
from telegram.error import Forbidden, NetworkError
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_bot() -> None:
    async with Bot(TELEGRAM_BOT_TOKEN) as bot:
        try:
            update_id = (await bot.get_updates())[0].update_id
        except IndexError:
            update_id = None

        logger.info("Listening for new messages...")

        while True:
            try:
                update_id = await handle_updates(bot, update_id)
            except NetworkError:
                await asyncio.sleep(1)
            except Forbidden:
                update_id += 1


async def handle_updates(bot: Bot, update_id: int) -> int:
    updates = await bot.get_updates(
        offset=update_id, timeout=30, allowed_updates=Update.ALL_TYPES
    )
    for update in updates:
        next_update_id = update.update_id + 1

        if update.message and update.message.text:
            text_to_reply = "Sorry, can't handle it."
            if update.message.text == "/start":
                text_to_reply = "Welcome to the DNA Library service"
            elif update.message.text == "python":
                text_to_reply = "Better than Java!"
            logger.info(f"Received message: {update.message.text}")
            await update.message.reply_text(text_to_reply)

        return next_update_id
    return update_id


if __name__ == "__main__":
    asyncio.run(start_bot())
