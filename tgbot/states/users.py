from aiogram.dispatcher.filters.state import StatesGroup, State


class User(StatesGroup):
    Lang = State()
    Name = State()
    Phone = State()
    Next = State()


class Flight(StatesGroup):
    City = State()
    Month = State()
    Date = State()
    type = State()
    Next = State()


class Admin(StatesGroup):
    City = State()
    Year = State()
    Month = State()
    Days = State()
    Category = State()
    Category_text = State()


class Custom(StatesGroup):
    Lang = State()
    Name = State()
    Phone = State()


class Location(StatesGroup):
    City = State()

