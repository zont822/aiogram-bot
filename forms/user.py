from aiogram.fsm.state import State, StatesGroup



class Form(StatesGroup):
    name = State()
    number = State()
    service = State()
    date = State()
    time = State()