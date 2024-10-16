from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

phonenumber = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Ракамни юбориш",
                           request_contact=True)
        ]
    ],
    resize_keyboard=True
)

phonenumber_uz = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Raqamni yuborish",
                           request_contact=True)
        ]
    ],
    resize_keyboard=True
)