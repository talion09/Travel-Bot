from aiogram.utils.callback_data import CallbackData

calendar_cb = CallbackData('calendar_cb', 'action', 'year', 'month')

date_cb = CallbackData('date_cb', 'action', 'year', 'month', 'day')

flight_days = CallbackData('flight_days', 'action', 'id_flight', 'day')

category_callback = CallbackData("category_callback", "action", "id_flight", "category")

check_sub = CallbackData("check_sub", "user_id")




