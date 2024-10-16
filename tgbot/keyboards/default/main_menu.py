from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✈️ Рейслар")
        ],
        [
            KeyboardButton(text="ℹ️ Биз хакимизда"),
            KeyboardButton(text="📍 Геолокация"),
        ],
        [
            KeyboardButton(text="⚙️ Созламалар"),
            KeyboardButton(text="👤 Дустлар билан уланиш")
        ],
        [
            KeyboardButton(text="Администрация"),
        ]
    ], resize_keyboard=True)


admin_menu_uz = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✈️ Reyslar")
        ],
        [
            KeyboardButton(text="ℹ️ Biz haqimizda"),
            KeyboardButton(text="📍 Geolokaziya"),
        ],
        [
            KeyboardButton(text="⚙️ Sozlamalar"),
            KeyboardButton(text="👤 Dõslar bilan ulashish")
        ],
        [
            KeyboardButton(text="Администрация"),
        ]
    ], resize_keyboard=True)


m_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✈️ Рейслар")
        ],
        [
            KeyboardButton(text="ℹ️ Биз хакимизда"),
            KeyboardButton(text="📍 Геолокация"),
        ],
        [
            KeyboardButton(text="⚙️ Созламалар"),
            KeyboardButton(text="👤 Дустлар билан уланиш")
        ]
    ], resize_keyboard=True)


m_menu_uz = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✈️ Reyslar")
        ],
        [
            KeyboardButton(text="ℹ️ Biz haqimizda"),
            KeyboardButton(text="📍 Geolokaziya"),
        ],
        [
            KeyboardButton(text="⚙️ Sozlamalar"),
            KeyboardButton(text="👤 Dõslar bilan ulashish")
        ]
    ], resize_keyboard=True)