from aiogram.types import Message, ChatMemberStatus, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from tgbot.keyboards.inline.catalog import check_sub


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        db = message.bot.get('db')
        admins_list = []
        for id, telegram_id, name in await db.select_all_admins():
            admins_list.append(telegram_id)
        return message.from_user.id in admins_list


class IsSubscriber(BoundFilter):
     async def check(self, message: Message):
         chat_member = await message.bot.get_chat_member(chat_id=-1002467963296, user_id=message.from_user.id)
         if chat_member.status != ChatMemberStatus.LEFT:
             return True
         else:
             await message.answer("Iltimos, batafsil ma’lumot uchun kanalimizga ham ulanib oling")










