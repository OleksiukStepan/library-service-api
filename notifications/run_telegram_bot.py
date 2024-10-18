import asyncio
import logging
import os
import sys
from time import sleep

import django
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate
from telegram import Bot, Update
from telegram.error import Forbidden, NetworkError


# Django Setup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")

django.setup()

# Logging Setup

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Bot Setup
BOT = Bot(token=settings.TELEGRAM_BOT_TOKEN)


# Sessions Setup

user_sessions = {}


async def start_bot() -> None:
    async with BOT:
        try:
            update_id = (await BOT.get_updates())[0].update_id
        except IndexError:
            update_id = None

        logger.info("Listening for new messages...")

        while True:
            try:
                update_id = await handle_updates(BOT, update_id)
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

        if update.message is None:
            sleep(1)
            continue

        chat_id = update.message.chat_id
        if chat_id not in user_sessions:
            user_sessions[chat_id] = {"state": "waiting_for_start"}
        session = user_sessions[chat_id]

        if update.message and update.message.text:

            text = update.message.text

            logger.info(f"Received message: {text} from chat {chat_id}")

            if session["state"] == "waiting_for_start" and text == "/start":
                await update.message.reply_text("Please enter your email:")
                session["state"] = "waiting_for_email"

            elif session["state"] == "waiting_for_email":
                session["email"] = text
                await update.message.reply_text("Please enter your password:")
                session["state"] = "waiting_for_password"

            elif session["state"] == "waiting_for_password":
                session["password"] = text
                if await authenticate_admin(
                    session["email"], session["password"], chat_id
                ):
                    session["is_authenticated"] = True
                    del session["password"]
                    await update.message.reply_text(
                        "You are authenticated as an admin."
                    )
                else:
                    await update.message.reply_text("You don't have permissions.")
                    user_sessions.pop(chat_id)

        return next_update_id
    return update_id


@sync_to_async
def authenticate_admin(email: str, password: str, telegram_chat_id: int) -> bool:
    user = authenticate(username=email, password=password)

    if user and user.is_staff:
        user.telegram_chat_id = telegram_chat_id
        user.save()

    return user and user.is_staff


if __name__ == "__main__":
    asyncio.run(start_bot())
