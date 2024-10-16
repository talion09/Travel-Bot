from re import compile

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ChatMemberStatus, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.default.language import lang
from tgbot.keyboards.default.main_menu import m_menu, admin_menu, admin_menu_uz, m_menu_uz
from tgbot.keyboards.inline.catalog import check_sub
from tgbot.states.users import User


async def ru_language(message):
    db = message.bot.get("db")
    user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
    if user_in_db.get("language") == "ru":
        return True


async def suitable_menu(message):
    db = message.bot.get("db")
    admins_list = []
    for id, telegram_id, name in await db.select_all_admins():
        admins_list.append(telegram_id)
    if message.from_user.id in admins_list:
        if await ru_language(message):
            menu = admin_menu
        else:
            menu = admin_menu_uz
    else:
        if await ru_language(message):
            menu = m_menu
        else:
            menu = m_menu_uz
    return menu


async def start_deep(message: types.Message):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    print("sgfsgsegs")
    referrer = message.get_args()
    user = message.from_user.id
    name = message.from_user.full_name
    user_in_db = await db.select_user(telegram_id=int(referrer))
    try:
        ref_full_name = user_in_db.get("full_name")
        if int(referrer) != int(user):
            try:
                await db.add_referral(referrer=int(referrer), referral=int(user))
                text = _("Вы были приглашены пользователем {}")
                text2 = _("Вы пригласили {}\n")
                await message.answer(text.format(ref_full_name))
                await message.bot.send_message(int(referrer), text2.format(name))
            except Exception as err:
                text3 = _("<b>Вы уже приглашены другим пользователем!</b>")
                await message.answer(text3)
        else:
            text4 = _("<b>Нельзя переходить по своей реферальной ссылке!</b>")
            await message.answer(text4)
    except AttributeError:
        text5 = _("<b>Ссылка не действительна!</b>")
        await message.answer(text5)


async def bot_start(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    await state.reset_state()
    try:
        user_in_db =await db.select_user(telegram_id=int(message.from_user.id))
        full_name = user_in_db.get("full_name")
        menu = await suitable_menu(message)
        chat_member = await message.bot.get_chat_member(chat_id=-1002467963296, user_id=message.from_user.id)
        if chat_member.status != ChatMemberStatus.LEFT:
            if await ru_language(message):
                await message.answer(f"<b>{full_name}</b>, Сизни қизиқтирган нарсани танланг:", reply_markup=menu)
            else:
                await message.answer(f"<b>{full_name}</b>, Sizni qiziqtirgan narsani tanlang:", reply_markup=menu)
        else:

            if await ru_language(message):
                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(InlineKeyboardButton(text="Каналга уланиб олиш", url="https://t.me/salaamtravell"))
                keyboard.add(
                    InlineKeyboardButton(text="Текшириш", callback_data=check_sub.new(user_id=message.from_user.id)))
                await message.answer("Илтимос, батафсил малумот учун каналимизга хам уланиб олинг",
                                     reply_markup=keyboard)
            else:
                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(InlineKeyboardButton(text="Kanalga ulanib olish", url="https://t.me/salaamtravell"))
                keyboard.add(
                    InlineKeyboardButton(text="Tekshirish", callback_data=check_sub.new(user_id=message.from_user.id)))
                await message.answer("Iltimos, batafsil ma’lumot uchun kanalimizga ham ulanib oling",
                                     reply_markup=keyboard)
    except AttributeError:
        await message.answer(
            f"Ассалому Алейкум! {message.from_user.full_name}\nТилни танланг:\n\nAssalomu Alaykum!\nTilni tanlang:",
            reply_markup=lang)
        await User.Lang.set()



def register_start(dp: Dispatcher):
    dp.register_message_handler(start_deep, CommandStart(deep_link=compile(r"\d\d\d\d\d\d\d")), state="*")

    dp.register_message_handler(bot_start, CommandStart(), state="*")
    dp.register_message_handler(bot_start, state="*", text=["Главное меню", "Asosiy menyu", "Асосий меню"])
    dp.register_message_handler(bot_start, text=["Главное меню", "Asosiy menyu", "Асосий меню"])
