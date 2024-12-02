import asyncio
import logging

from telegram.error import Forbidden

from notifications.run_telegram_bot import BOT
from notifications.utils import get_admin_chat_ids, remove_chat_id


async def send_telegram_message_async(message: str) -> None:
    admin_chats = await get_admin_chat_ids()

    if not admin_chats:
        logging.warning("No admin chats to send messages to.")
        return

    for chat_id in admin_chats:
        try:
            await BOT.send_message(chat_id=chat_id, text=message)
            logging.info(f"Message sent to chat ID: {chat_id}")
        except Forbidden as e:
            logging.warning(
                f"Bot was blocked by user with chat ID: {chat_id}. "
                f"Removing from the list."
            )
            await remove_chat_id(chat_id)


def send_telegram_message(message: str) -> None:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        asyncio.ensure_future(send_telegram_message_async(message))
    else:
        loop.run_until_complete(send_telegram_message_async(message))
