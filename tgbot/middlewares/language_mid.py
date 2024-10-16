from typing import Tuple, Any
from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from tgbot.config import I18N_DOMAIN, LOCALES_DIR


async def get_lang(user_id, message, call, query, inline):
    try:
        db = message.bot.get("db")
    except:
        try:
            db = call.bot.get("db")
        except:
            try:
                db = query.bot.get("db")
            except:
                db = inline.bot.get("db")
    try:
        user = await db.select_user(telegram_id=int(user_id))
        lang = user.get("language")
        if user:
            return lang
    except:
        return "ru"


class ACLMidlleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]):
        user = types.User.get_current()
        message = types.Message.get_current()
        call = types.CallbackQuery.get_current()
        query = types.PreCheckoutQuery.get_current()
        inline = types.InlineQuery.get_current()
        return await get_lang(user.id, message, call, query, inline)


def setup_middleware(dp):
    i18n = ACLMidlleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
