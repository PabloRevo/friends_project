"""
Файл с моделями машины состояний
"""


from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMCreateReact(StatesGroup):
    reaction = State()
    status = State()


class FSMAdmin(StatesGroup):
    message = State()


class FSMImage(StatesGroup):
    status = State()
