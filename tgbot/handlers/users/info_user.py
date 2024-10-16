from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberStatus

from tgbot.handlers.users.start import suitable_menu
from tgbot.keyboards.default.main_menu import m_menu_uz, m_menu
from tgbot.keyboards.default.phone import phonenumber, phonenumber_uz
from tgbot.keyboards.inline.catalog import check_sub
from tgbot.states.users import User


# User.Lang
async def info_lang(message: types.Message, state: FSMContext):
    if message.text == "Lotin":
        language = "Lotin"
        await message.answer("Ismingizni kiriting")
        await state.update_data(lang=language)
        await User.Name.set()
    elif message.text == "Kirill":
        language = "Kirill"
        await message.answer("Исмгизни киритинг")
        await state.update_data(lang=language)
        await User.Name.set()
    else:
        await message.answer("Тилни танланг:\n\nTilni tanlang:")


# User.Name
async def info_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("lang")
    await state.update_data(name=message.text)
    if language == "Kirill":
        await message.answer("Телефон рақамингизни юборинг (+998ххххххххх):", reply_markup=phonenumber)
    else:
        await message.answer("Telefon raqamingizni yuboring (+998xxxxxxxxx):", reply_markup=phonenumber_uz)
    await User.Phone.set()


# User.Phone
async def info_phone(message: types.Message, state: FSMContext):
    contc = message.contact.phone_number
    await state.update_data(number=contc)
    await User.Next.set()
    await info_next(message, state)


# User.Phone
async def info_phone_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("lang")
    phone = message.text[1:]
    try:
        int(phone)
        if "+998" in str(message.text) and len(message.text) == 13:
            await state.update_data(number=phone)
            await User.Next.set()
            await info_next(message, state)
        else:
            if language == "Kirill":
                await message.answer("Телефон рақамингизни юборинг (+998ххххххххх):", reply_markup=phonenumber)
            else:
                await message.answer("Telefon raqamingizni yuboring (+998xxxxxxxxx):", reply_markup=phonenumber_uz)
            await User.Phone.set()
    except:
        if language == "Kirill":
            await message.answer("Телефон рақамингизни юборинг (+998ххххххххх):", reply_markup=phonenumber)
        else:
            await message.answer("Telefon raqamingizni yuboring (+998xxxxxxxxx):", reply_markup=phonenumber_uz)
        await User.Phone.set()


# User.Next
async def info_next(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    language = data.get("lang")
    number = data.get("number")
    name = data.get("name")
    if language == "Kirill":
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(text="Каналга уланиб олиш", url="https://t.me/salaamtravell"))
        keyboard.add(InlineKeyboardButton(text="Текшириш", callback_data=check_sub.new(user_id=message.from_user.id)))
        await message.answer("Илтимос, батафсил малумот учун каналимизга хам уланиб олинг", reply_markup=keyboard)
        language = "ru"
    else:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(text="Kanalga ulanib olish", url="https://t.me/salaamtravell"))
        keyboard.add(InlineKeyboardButton(text="Tekshirish", callback_data=check_sub.new(user_id=message.from_user.id)))
        await message.answer("Iltimos, batafsil ma’lumot uchun kanalimizga ham ulanib oling", reply_markup=keyboard)
        language = "uz"

    await db.add_user(
        full_name=name,
        telegram_id=int(message.from_user.id),
        number=int(number),
        language=language
    )

    await state.reset_state()


async def check_subscription(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    _ = call.bot.get("lang")
    await call.answer()
    chat_member = await call.bot.get_chat_member(chat_id=-1002467963296, user_id=call.from_user.id)
    if chat_member.status != ChatMemberStatus.LEFT:
        user_in_db =await db.select_user(telegram_id=int(call.from_user.id))
        full_name = user_in_db.get("full_name")
        menu = await suitable_menu(call)
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id, text=f"<b>{full_name}</b>, Sizni qiziqtirgan narsani tanlang:", reply_markup=menu)
    else:
        await call.bot.send_message("Iltimos, batafsil ma’lumot uchun kanalimizga ham ulanib oling")



def register_info_user(dp: Dispatcher):
    dp.register_message_handler(info_lang, state=User.Lang)
    dp.register_message_handler(info_name, state=User.Name)
    dp.register_message_handler(info_phone_text, state=User.Phone, content_types=types.ContentType.TEXT)
    dp.register_message_handler(info_phone, state=User.Phone, content_types=types.ContentType.CONTACT)
    dp.register_message_handler(info_next, state=User.Next)

    dp.register_callback_query_handler(check_subscription,check_sub.filter())


