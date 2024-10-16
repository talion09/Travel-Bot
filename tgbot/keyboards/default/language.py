from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

lang = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Lotin"),
            KeyboardButton(text="Kirill")
        ]
    ], resize_keyboard=True)