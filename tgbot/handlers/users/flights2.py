import calendar
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.filters.is_admin import IsSubscriber
from tgbot.handlers.users.start import bot_start
from tgbot.keyboards.default.language import lang
from tgbot.keyboards.default.main_menu import m_menu, admin_menu, admin_menu_uz, m_menu_uz
from tgbot.keyboards.inline.catalog import calendar_cb, date_cb
from tgbot.states.users import Flight

month_names = {
    1: 'Yanvar',
    2: 'Fevral',
    3: 'Mart',
    4: 'Aprel',
    5: 'May',
    6: 'Iyun',
    7: 'Iyul',
    8: 'Avgust',
    9: 'Sentabr',
    10: 'Oktabr',
    11: 'Noyabr',
    12: 'Dekabr'
}

# month_name = month_names.get(month)


# Функция для получения доступных дат
async def get_available_dates(message: types.Message, city: str, month: int, year: int) -> list:
    db = message.bot.get("db")
    select = await db.select_flight(city=city, year=int(year), month=int(month))
    try:
        dates = select.get("number_of_dates")
        return dates
    except:
        return []


# Функция для поиска следующего месяца с доступными датами
async def get_next_available_month(message: [types.Message, types.CallbackQuery], city: str, start_month: int, year: int) -> (int, int):
    for month in range(start_month, 13):  # Проверка всех месяцев до конца года
        available_dates = await get_available_dates(message, city, month, year)
        if available_dates:
            return month, year

    # Если до конца года нет доступных дат, проверить следующий год
    for month in range(1, 13):
        available_dates = await get_available_dates(message, city, month, year + 1)
        if available_dates:
            return month, year + 1

    return None, None  # Если не найдены доступные даты


# Функция для поиска предыдущего месяца с доступными датами
async def get_prev_available_month(message: [types.Message, types.CallbackQuery], city: str, start_month: int, year: int) -> (int, int):
    for month in range(start_month, 0, -1):  # Проверка всех месяцев до начала года
        available_dates = await get_available_dates(message, city, month, year)
        if available_dates:
            return month, year

    # Если до начала года нет доступных дат, проверить предыдущий год
    for month in range(12, 0, -1):
        available_dates = await get_available_dates(message, city, month, year - 1)
        if available_dates:
            return month, year - 1

    return None, None  # Если не найдены доступные даты


# Функция для создания инлайн-клавиатуры календаря
async def get_calendar_keyboard(message: [types.Message, types.CallbackQuery], city: str, action: str, month: int = None, year: int = None):
    if year is None:
        year = datetime.now().year

    if month is None:
        month = datetime.now().month

    current_year = datetime.now().year
    current_month = datetime.now().month
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    month_index = month

    available_dates = await get_available_dates(message, city, month_index, year)

    if action == "default":
        if not available_dates:
            next_month, next_year = await get_next_available_month(message, city, month_index + 1, year)
            if next_month is not None:
                return await get_calendar_keyboard(message, city, "default", next_month, next_year)
            else:
                keyboard = InlineKeyboardMarkup(row_width=7)
                for day in week_days:
                    keyboard.insert(InlineKeyboardButton(text=day, callback_data="ignore"))
                prev_month_data = calendar_cb.new('prev_month', year, month_index)
                keyboard.row(
                    InlineKeyboardButton(text="←", callback_data=prev_month_data),
                    InlineKeyboardButton(text=f"Нет доступных дат", callback_data="ignore"),
                    InlineKeyboardButton(text=" ", callback_data="ignore")
                )
                return keyboard

    elif action == "prev_month":
        if not available_dates:
            prev_month, prev_year = await get_prev_available_month(message, city, month_index - 1, year)
            if prev_month is not None:
                return await get_calendar_keyboard(message, city, "default", prev_month, prev_year)
            else:
                return await get_calendar_keyboard(message, city, "default", current_month, current_year)

    first_day_of_month, num_days = calendar.monthrange(year, month_index)

    keyboard = InlineKeyboardMarkup(row_width=7)
    for day in week_days:
        keyboard.insert(InlineKeyboardButton(text=day, callback_data="ignore"))

    for _ in range(first_day_of_month):
        keyboard.insert(InlineKeyboardButton(text=" ", callback_data="ignore"))

    for day in range(1, num_days + 1):
        if day in available_dates:
            callback_data = date_cb.new('exact_date', year, month_index, day)
            keyboard.insert(InlineKeyboardButton(text=f"✅ {day}", callback_data=callback_data))
        else:
            keyboard.insert(InlineKeyboardButton(text=str(day), callback_data="ignore"))

    prev_month_data = calendar_cb.new('prev_month', year, month_index)
    next_month_data = calendar_cb.new('next_month', year, month_index)
    month_name = month_names.get(month)
    if month_index == current_month and year == current_year:
        keyboard.row(
            InlineKeyboardButton(text=" ", callback_data="ignore"),
            InlineKeyboardButton(text=f"{month_name} {year}", callback_data="ignore"),
            InlineKeyboardButton(text="→", callback_data=next_month_data)
        )
    else:
        keyboard.row(
            InlineKeyboardButton(text="←", callback_data=prev_month_data),
            InlineKeyboardButton(text=f"{month_name} {year}", callback_data="ignore"),
            InlineKeyboardButton(text="→", callback_data=next_month_data)
        )

    return keyboard


# Обработчик для выбора города отправления
async def flight_cities(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    text1 = _("Выберите город отправления")
    text2 = _("Назад")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    select = await db.select_all_flights()
    cities = []
    for id, city, year, month, number_of_dates, econom, standart, vip in select:
        if city not in cities:
            cities.append(city)
            markup.add(types.KeyboardButton(text=city))
    markup.add(types.KeyboardButton(text=text2))
    await message.answer(text1, reply_markup=markup)
    await Flight.City.set()


# Flight.City
async def flight_dates(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    text1 = _("Выберите даты")
    text2 = _("Назад")
    if message.text == text2:
        await state.reset_state()
        await bot_start(message, state)
    else:
        markup = await get_calendar_keyboard(message, message.text, "default")
        await message.answer(text1, reply_markup=markup)
        await state.update_data(city=message.text)


# Callback-обработчик для навигации по календарю
async def calendar_callback_handler(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    city = data['city']
    action = callback_data['action']
    year = int(callback_data['year'])
    month = int(callback_data['month'])

    if action == "prev_month":
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        keyboard = await get_calendar_keyboard(call, city, "prev_month", month, year)
    elif action == "next_month":
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        keyboard = await get_calendar_keyboard(call, city, "default", month, year)
    else:
        keyboard = await get_calendar_keyboard(call, city, "default", month, year)
    await call.message.edit_reply_markup(reply_markup=keyboard)
    await call.answer()


async def date_callback_handler(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    _ = call.bot.get("lang")
    await call.answer()
    data = await state.get_data()
    city = data['city']
    action = callback_data['action']
    year = int(callback_data['year'])
    month = int(callback_data['month'])
    day = int(callback_data['day'])

    keyboard = InlineKeyboardMarkup(row_width=3)
    select = await db.select_flight(city=city, year=int(year), month=int(month))
    econom = select.get("econom")
    standart = select.get("standart")
    vip = select.get("vip")
    text1 = _(f"Экономический")
    text2 = _(f"Стандартный")
    text3 = _(f"VIP")
    text4 = _(f"Назад")
    text5 = _(f"Выберите тариф")
    if econom is not None:
        callback_data = date_cb.new('econom', year, month, day)
        keyboard.insert(InlineKeyboardButton(text=text1, callback_data=callback_data))
    if standart is not None:
        callback_data = date_cb.new('standart', year, month, day)
        keyboard.insert(InlineKeyboardButton(text=text2, callback_data=callback_data))
    if vip is not None:
        callback_data = date_cb.new('vip', year, month, day)
        keyboard.insert(InlineKeyboardButton(text=text3, callback_data=callback_data))
    keyboard.add(InlineKeyboardButton(text=text4, callback_data=date_cb.new('back', year, month, day)))
    await call.bot.edit_message_text(text=text5, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)


async def order_callback_handler(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    _ = call.bot.get("lang")
    await call.answer()
    data = await state.get_data()
    city = data['city']
    action = callback_data['action']
    year = int(callback_data['year'])
    month = int(callback_data['month'])
    day = int(callback_data['day'])

    keyboard = InlineKeyboardMarkup(row_width=3)
    select = await db.select_flight(city=city, year=int(year), month=int(month))
    econom = select.get("econom")
    standart = select.get("standart")
    vip = select.get("vip")

    text1 = _(f"Назад")
    text2 = _(f"Забронировать на эту дату?")
    text4 = _(f"Забронировать")
    if action == "econom":
        text3 = f"{econom}\n\n{text2}"
    elif action == "standart":
        text3 = f"{standart}\n\n{text2}"
    else:
        text3 = f"{vip}\n\n{text2}"

    keyboard.add(InlineKeyboardButton(text=text4, callback_data=date_cb.new('order', year, month, day)))
    keyboard.add(InlineKeyboardButton(text=text1, callback_data=date_cb.new('back2', year, month, day)))
    await call.bot.edit_message_text(text=text3, chat_id=call.message.chat.id, message_id=call.message.message_id,
                                     reply_markup=keyboard)


async def confirm_order_callback_handler(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    _ = call.bot.get("lang")
    await call.answer()
    data = await state.get_data()
    city = data['city']
    action = callback_data['action']
    year = int(callback_data['year'])
    month = int(callback_data['month'])
    day = int(callback_data['day'])

    text1 = _(f"Спасибо за бронирование на эту дату! Ожидайте звонка")
    await call.bot.edit_message_text(text=text1, chat_id=call.message.chat.id, message_id=call.message.message_id)
    user_in_db = await db.select_user(telegram_id=int(call.from_user.id))
    full_name = user_in_db.get("full_name")
    number = user_in_db.get("number")
    language = user_in_db.get("language")

    text2 = _("Имя: {},\n"
              "Телефон: {},\n"
              "Язык: {},\n"
              "Бронь на {}.{}.{} года. В городе {}")
    await call.bot.send_message(chat_id=call.message.chat.id,
                                text=text2.format(full_name, number, language, day, month, year, city))


async def back_callback_handler(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    _ = call.bot.get("lang")
    data = await state.get_data()
    city = data['city']
    text1 = _("Выберите даты")
    markup = await get_calendar_keyboard(call, city, "default")
    await call.bot.edit_message_text(text=text1, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


# Регистрация обработчиков
def register_flights(dp: Dispatcher):
    dp.register_message_handler(flight_cities, IsSubscriber(), text=["✈️ Рейслар", "✈️ Reyslar"])
    dp.register_message_handler(flight_dates, state=Flight.City)
    dp.register_callback_query_handler(calendar_callback_handler,
                                       calendar_cb.filter(action=["prev_month", "next_month"]), state=Flight.City)
    dp.register_callback_query_handler(date_callback_handler,
                                       date_cb.filter(action=["exact_date", "back2"]), state=Flight.City)
    dp.register_callback_query_handler(order_callback_handler,
                                       date_cb.filter(action=["econom", "standart", "vip"]), state=Flight.City)
    dp.register_callback_query_handler(confirm_order_callback_handler,
                                       date_cb.filter(action="order"), state=Flight.City)
    dp.register_callback_query_handler(back_callback_handler,
                                       date_cb.filter(action="back"), state=Flight.City)



