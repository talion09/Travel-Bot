import calendar

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from tgbot.keyboards.inline.catalog import flight_days, category_callback
from tgbot.states.users import Admin

# Функция для создания клавиатуры с отменой
cancel = types.ReplyKeyboardMarkup(resize_keyboard=True).add("⬅️ Назад")

cities = ["Ташкент", "Самарканд", "Бухара"]

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

reverse_month_names = {v: k for k, v in month_names.items()}


async def administration(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text="Рефералы"))
    markup.add(KeyboardButton(text="Добавить рейс"))
    markup.add(KeyboardButton(text="Главное меню"))
    await message.answer("Выберите", reply_markup=markup)


# Админ. Ввод города
async def add_flights(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for city in cities:
        markup.add(KeyboardButton(text=city))
    markup.add(KeyboardButton(text="⬅️ Назад"))
    await message.answer("Введите город", reply_markup=markup)
    await Admin.City.set()


# Admin.City
async def add_admin_city(message: types.Message, state: FSMContext):
    if "⬅️ Назад" in message.text:
        await state.reset_state()
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(text="Рефералы"))
        markup.add(KeyboardButton(text="Добавить рейс"))
        markup.add(KeyboardButton(text="Главное меню"))
        await message.answer("Выберите", reply_markup=markup)
    else:
        await state.update_data(city=message.text)
        await message.answer("Введите год", reply_markup=cancel)
        await Admin.Year.set()


# Admin.Year
async def add_admin_year(message: types.Message, state: FSMContext):
    if "⬅️ Назад" in message.text:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for city in cities:
            markup.add(KeyboardButton(text=city))
        markup.add(KeyboardButton(text="⬅️ Назад"))
        await message.answer("Введите город", reply_markup=markup)
        await Admin.City.set()
    else:
        try:
            int(message.text)
            await state.update_data(year=message.text)
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            for month in month_names.values():
                markup.add(KeyboardButton(text=month))
            markup.add(KeyboardButton(text="⬅️ Назад"))
            await message.answer("Введите месяц", reply_markup=markup)
            await Admin.Month.set()
        except:
            await message.answer("Введите год", reply_markup=cancel)
            await Admin.Year.set()



# Admin.Month
async def add_admin_month(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    city = data.get('city')
    year = int(data.get('year'))
    month = message.text
    if "⬅️ Назад" in message.text:
        await message.answer("Введите год", reply_markup=cancel)
        await Admin.Year.set()
    else:
        await state.update_data(month=message.text)
        await message.answer("Теперь надо выбрать дни, в которых есть рейсы", reply_markup=ReplyKeyboardRemove())
        month_number = int(reverse_month_names.get(month))
        flight = await db.add_flight(city=city, year=year, month=month_number, number_of_dates=[], econom=None, standart=None, vip=None)
        id_flight = int(flight.get("id"))
        print(f"Flight added: {id_flight}")
        _, num_days = calendar.monthrange(year, month_number)
        markup = InlineKeyboardMarkup(row_width=7)
        for day in range(1, num_days + 1):
            markup.insert(InlineKeyboardButton(text=str(day), callback_data=flight_days.new(action="day",
                                                                                            id_flight=id_flight,
                                                                                            day=day)))
        markup.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=flight_days.new(action="back",
                                                                                          id_flight=id_flight,
                                                                                          day="none")))
        await message.answer("Выберите дни", reply_markup=markup)
        await Admin.Days.set()


# Admin.Days
async def day_selected(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    await call.answer()
    data = await state.get_data()
    month = data.get('month')
    year = int(data.get('year'))
    action = callback_data.get('action')
    id_flight = int(callback_data.get('id_flight'))
    day = callback_data.get('day')
    if action == "back":
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for month in month_names.values():
            markup.add(KeyboardButton(text=month))
        markup.add(KeyboardButton(text="⬅️ Назад"))
        await db.delete_flight(id=id_flight)
        await call.bot.send_message(chat_id=call.from_user.id, text="Введите месяц", reply_markup=markup)
        await Admin.Month.set()
    else:
        select = await db.select_flight(id=id_flight)
        number_of_dates = select.get("number_of_dates")
        if action == "day_delete":
            number_of_dates.remove(int(day))
            await db.update_flight(id=id_flight, number_of_dates=number_of_dates)
        else:
            number_of_dates.append(int(day))
            await db.update_flight(id=id_flight, number_of_dates=number_of_dates)
        month_number = int(reverse_month_names.get(month))
        _, num_days = calendar.monthrange(year, month_number)
        markup = InlineKeyboardMarkup(row_width=7)
        for day in range(1, num_days + 1):
            if day in number_of_dates:
                markup.insert(InlineKeyboardButton(text=f"✅ {day}", callback_data=flight_days.new(action="day_delete",
                                                                                                id_flight=id_flight,
                                                                                                day=day)))
            else:
                markup.insert(InlineKeyboardButton(text=str(day), callback_data=flight_days.new(action="day",
                                                                                            id_flight=id_flight,
                                                                                            day=day)))
        markup.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=flight_days.new(action="back",
                                                                                          id_flight=id_flight,
                                                                                          day="none")))
        markup.add(InlineKeyboardButton(text="Завершить процесс", callback_data=flight_days.new(action="complete",
                                                                                          id_flight=id_flight,
                                                                                          day="none")))
        await call.bot.edit_message_text(text=f"Выберите дни", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=markup)
        await Admin.Days.set()


async def propose_categories(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    data = await state.get_data()
    id_flight = int(callback_data.get("id_flight"))
    flight = await db.select_flight(id=id_flight)
    existing_categories = {
        "econom": flight.get("econom"),
        "standart": flight.get("standart"),
        "vip": flight.get("vip"),
    }

    markup = InlineKeyboardMarkup(row_width=1)

    categories_to_add = []
    for category, value in existing_categories.items():
        if not value:
            categories_to_add.append(category)
            markup.add(InlineKeyboardButton(
                text=f"Добавить {category.capitalize()}",
                callback_data=category_callback.new(action="add", id_flight=id_flight, category=category)
            ))

    markup.add(InlineKeyboardButton(
        text=f"⬅️ Назад",
        callback_data=category_callback.new(action="back", id_flight=id_flight, category="none")
    ))

    if categories_to_add:
        await call.bot.edit_message_text(text="Выберите категорию для добавления:", chat_id=call.from_user.id,
                                         message_id=call.message.message_id, reply_markup=markup)
        await Admin.Category.set()
    else:
        await call.bot.edit_message_text(text="Все категории уже добавлены в Базу Данных", chat_id=call.from_user.id,
                                         message_id=call.message.message_id)
        await state.reset_state()


# Admin.Category
async def add_category(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    action = callback_data.get('action')
    category = callback_data.get('category')
    id_flight = int(callback_data.get('id_flight'))

    data = await state.get_data()
    month = data.get('month')
    year = int(data.get('year'))

    if action == "back":
        select = await db.select_flight(id=id_flight)
        number_of_dates = select.get("number_of_dates")
        month_number = reverse_month_names.get(month)
        _, num_days = calendar.monthrange(year, month_number)
        markup = InlineKeyboardMarkup(row_width=7)
        for day in range(1, num_days + 1):
            if day in number_of_dates:
                markup.insert(InlineKeyboardButton(text=f"✅ {day}", callback_data=flight_days.new(action="day",
                                                                                                id_flight=id_flight,
                                                                                                day=day)))
            else:
                markup.insert(InlineKeyboardButton(text=str(day), callback_data=flight_days.new(action="day",
                                                                                            id_flight=id_flight,
                                                                                            day=day)))
        markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=flight_days.new(action="back",
                                                                                          id_flight=id_flight,
                                                                                          day="none")))
        markup.insert(InlineKeyboardButton(text="Завершить процесс", callback_data=flight_days.new(action="complete",
                                                                                          id_flight=id_flight,
                                                                                          day="none")))
        await call.bot.edit_message_text(text=f"Выберите дни", chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=markup)
        await Admin.Days.set()
    else:
        await state.update_data(id_flight=id_flight)
        await state.update_data(category=category)
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id, text=f"Введите текст, включающий всю информацию для тарифа {category.capitalize()}", reply_markup=cancel)
        await Admin.Category_text.set()


async def add_category_text(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    id_flight = int(data.get('id_flight'))
    category = data.get('category')
    month = data.get('month')
    if "⬅️ Назад" in message.text:
        await message.answer("Действие отменено", reply_markup=ReplyKeyboardRemove())

        flight = await db.select_flight(id=id_flight)
        existing_categories = {
            "econom": flight.get("econom"),
            "standart": flight.get("standart"),
            "vip": flight.get("vip"),
        }
        markup = InlineKeyboardMarkup(row_width=1)
        categories_to_add = []
        for category, value in existing_categories.items():
            if not value:
                categories_to_add.append(category)
                markup.add(InlineKeyboardButton(
                    text=f"Добавить {category.capitalize()}",
                    callback_data=category_callback.new(action="add", id_flight=id_flight, category=category)
                ))
        markup.add(InlineKeyboardButton(
            text=f"⬅️ Назад",
            callback_data=category_callback.new(action="back", id_flight=id_flight, category="none")
        ))
        if categories_to_add:
            await message.answer(text="Выберите категорию для добавления:", reply_markup=markup)
            await Admin.Category.set()
        else:
            await message.answer(text="Все категории уже добавлены в Базу Данных", reply_markup=ReplyKeyboardRemove())
            await state.reset_state()
    else:
        if category == "econom":
            await db.update_flight(id=id_flight, econom=message.text)
        elif category == "standart":
            await db.update_flight(id=id_flight, standart=message.text)
        elif category == "vip":
            await db.update_flight(id=id_flight, vip=message.text)
        else:
            pass
        await message.answer("Информация о рейсе добавлена в Базу Данных", reply_markup=ReplyKeyboardRemove())
        flight = await db.select_flight(id=id_flight)
        existing_categories = {
            "econom": flight.get("econom"),
            "standart": flight.get("standart"),
            "vip": flight.get("vip"),
        }
        markup = InlineKeyboardMarkup(row_width=1)
        categories_to_add = []
        for category, value in existing_categories.items():
            if not value:
                categories_to_add.append(category)
                markup.add(InlineKeyboardButton(
                    text=f"Добавить {category.capitalize()}",
                    callback_data=category_callback.new(action="add", id_flight=id_flight, category=category)
                ))
        markup.add(InlineKeyboardButton(
            text=f"⬅️ Назад",
            callback_data=category_callback.new(action="back", id_flight=id_flight, category="none")
        ))
        if categories_to_add:
            await message.answer(text="Выберите категорию для добавления:", reply_markup=markup)
            await Admin.Category.set()
        else:
            await message.answer(text="Все категории уже добавлены в Базу Данных", reply_markup=ReplyKeyboardRemove())
            await state.reset_state()


async def add_owner(message: types.Message):
    db = message.bot.get('db')
    await db.add_administrator(telegram_id=int(153479611), name="Мухаммад")
    await message.answer("Выполнено")


async def drop_owner(message: types.Message):
    db = message.bot.get('db')
    await db.drop_users()
    await db.drop_admins()
    await db.drop_flights()
    await message.answer("Выполнено")


# Регистрация хендлеров
def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(administration, text="Администрация")
    dp.register_message_handler(add_flights, text="Добавить рейс")
    dp.register_message_handler(add_admin_city, state=Admin.City)
    dp.register_message_handler(add_admin_year, state=Admin.Year)
    dp.register_message_handler(add_admin_month, state=Admin.Month)
    dp.register_callback_query_handler(day_selected, flight_days.filter(action="day"), state=Admin.Days)
    dp.register_callback_query_handler(day_selected, flight_days.filter(action="back"), state=Admin.Days)
    dp.register_callback_query_handler(day_selected, flight_days.filter(action="day_delete"), state=Admin.Days)
    dp.register_callback_query_handler(propose_categories, flight_days.filter(action="complete"), state=Admin.Days)

    dp.register_callback_query_handler(add_category, category_callback.filter(), state=Admin.Category)
    dp.register_message_handler(add_category_text, state=Admin.Category_text)

    dp.register_message_handler(add_owner, Command("add_owner"))
    dp.register_message_handler(drop_owner, Command("drop_owner"))



