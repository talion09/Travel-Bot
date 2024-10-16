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

from aiogram.dispatcher.filters.state import StatesGroup, State

class Flight(StatesGroup):
    City = State()
    Tariff = State()  # Новый шаг для выбора тарифа
    Date = State()

calendar_cb = CallbackData('calendar_cb', 'action', 'year', 'month')

date_cb = CallbackData('date_cb', 'action', 'year', 'month', 'day')

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

# Функция для получения доступных дат
async def get_available_dates(message: types.Message, city: str, month: int, year: int, tariff: str) -> list:
    db = message.bot.get("db")
    select = await db.select_flight(city=city, year=int(year), month=int(month))
    try:
        dates = select.get(f"{tariff}")  # Используем выбранный тариф для фильтрации дат
        return dates
    except:
        return []

# Функция для создания инлайн-клавиатуры календаря
async def get_calendar_keyboard(message: [types.Message, types.CallbackQuery], city: str, tariff: str, action: str, month: int = None, year: int = None):
    if year is None:
        year = datetime.now().year

    if month is None:
        month = datetime.now().month

    current_year = datetime.now().year
    current_month = datetime.now().month
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    month_index = month

    available_dates = await get_available_dates(message, city, month_index, year, tariff)

    if action == "default":
        if not available_dates:
            next_month, next_year = await get_next_available_month(message, city, month_index + 1, year)
            if next_month is not None:
                return await get_calendar_keyboard(message, city, tariff, "default", next_month, next_year)
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


# Функция для получения следующего месяца с доступными датами
async def get_next_available_month(message: types.Message, city: str, month: int, year: int):
    db = message.bot.get("db")

    while month <= 12:
        available_dates = await get_available_dates(message, city, month, year, tariff='econom')  # Используем тариф по умолчанию
        if available_dates:
            return month, year
        month += 1

    # Если текущий год закончился, начинаем проверять следующий год
    year += 1
    for next_month in range(1, 13):
        available_dates = await get_available_dates(message, city, next_month, year, tariff='econom')  # Используем тариф по умолчанию
        if available_dates:
            return next_month, year

    return None, None  # Если нет доступных дат в будущем


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

# Обработчик для выбора тарифа
async def flight_tariffs(message: types.Message, state: FSMContext):
    _ = message.bot.get("lang")
    text1 = _("Выберите тариф")
    text2 = _("Назад")
    if message.text == text2:
        await state.reset_state()
        await bot_start(message, state)
    else:
        await state.update_data(city=message.text)
        markup = InlineKeyboardMarkup(row_width=3)
        markup.add(InlineKeyboardButton(text="Эконом", callback_data="econom"))
        markup.add(InlineKeyboardButton(text="Стандарт", callback_data="standart"))
        markup.add(InlineKeyboardButton(text="VIP", callback_data="vip"))
        markup.add(InlineKeyboardButton(text=text2, callback_data="back"))
        await message.answer(text1, reply_markup=markup)
        await Flight.Tariff.set()

# Callback-обработчик для выбора тарифа и отображения доступных дат
async def tariff_callback_handler(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    _ = call.bot.get("lang")
    tariff = callback_data['action']
    data = await state.get_data()
    city = data['city']
    text1 = _("Выберите дату")
    markup = await get_calendar_keyboard(call, city, tariff, "default")
    await call.message.edit_text(text=text1, reply_markup=markup)
    await state.update_data(tariff=tariff)
    await Flight.Date.set()

# Callback-обработчик для навигации по календарю
async def calendar_callback_handler(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    city = data['city']
    tariff = data['tariff']
    action = callback_data['action']
    year = int(callback_data['year'])
    month = int(callback_data['month'])

    if action == "prev_month":
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        keyboard = await get_calendar_keyboard(call, city, tariff, "prev_month", month, year)
    elif action == "next_month":
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        keyboard = await get_calendar_keyboard(call, city, tariff, "default", month, year)
    else:
        keyboard = await get_calendar_keyboard(call, city, tariff, "default", month, year)
    await call.message.edit_reply_markup(reply_markup=keyboard)
    await call.answer()

# Регистрация обработчиков
def register_flights(dp: Dispatcher):
    dp.register_message_handler(flight_cities, IsSubscriber(), text=["✈️ Рейслар", "✈️ Reyslar"])
    dp.register_message_handler(flight_tariffs, state=Flight.City)
    dp.register_callback_query_handler(tariff_callback_handler, text=["econom", "standart", "vip"], state=Flight.Tariff)
    dp.register_callback_query_handler(calendar_callback_handler,
                                       calendar_cb.filter(action=["prev_month", "next_month"]), state=Flight.Date)
