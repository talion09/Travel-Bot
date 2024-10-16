import calendar

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from tgbot.keyboards.inline.catalog import flight_days, category_callback
from tgbot.states.users import Admin


async def show_referals(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text="Администрация"))
    text = f"Топ реферреров:\n\n"
    select = await db.select_all_referrers()
    all_referrers = {}

    for id, referrer, referral in select:
        if referrer not in all_referrers:
            count = await db.count_referrals(referrer=int(referrer))
            all_referrers[referrer] = count

    # Sort the dictionary by count in descending order
    sorted_referrers = sorted(all_referrers.items(), key=lambda x: x[1], reverse=True)

    # Format the text with sorted referrers
    for referrer, count in sorted_referrers:
        user_in_db = await db.select_user(telegram_id=int(referrer))
        ref_full_name = user_in_db.get("full_name")
        text += f"\n{ref_full_name} - {count}"
    await message.answer(text, reply_markup=markup)


# Регистрация хендлеров
def register_referals(dp: Dispatcher):
    dp.register_message_handler(show_referals, text="Рефералы")




