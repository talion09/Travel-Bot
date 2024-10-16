from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.deep_linking import get_start_link

from tgbot.filters.is_admin import IsSubscriber
from tgbot.handlers.users.start import ru_language, bot_start, suitable_menu

from tgbot.keyboards.default.phone import phonenumber, phonenumber_uz
from tgbot.states.users import Custom


async def ref_system(message: types.Message):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    deep_link = await get_start_link(payload=message.from_user.id)
    count = await db.count_referrals(referrer=int(message.from_user.id))
    text1 = _("Главное меню")
    text2 = _("{} вы имеете {} рефералов\nВот твоя реферальная ссылка: {}")
    user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
    full_name = user_in_db.get("full_name")
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text1)]], resize_keyboard=True, row_width=2)
    await message.answer(text2.format(full_name, count, deep_link), reply_markup=markup)


def register_referal_system(dp: Dispatcher):
    dp.register_message_handler(ref_system, IsSubscriber(), text=["👤 Dõslar bilan ulashish", "👤 Дустлар билан уланиш"])
