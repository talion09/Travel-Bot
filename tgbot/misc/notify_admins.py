import logging

from aiogram import Dispatcher

from tgbot.config import load_config


async def on_startup_notify(dp: Dispatcher):
    config = load_config(".env")
    ADMINS = config.tg_bot.admin_ids
    try:
        await dp.bot.send_message(int(ADMINS), "Бот Запущен")
    except Exception as err:
        logging.exception(err)