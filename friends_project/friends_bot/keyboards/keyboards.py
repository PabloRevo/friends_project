from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.models import *
from keyboards import key_text


async def status_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    statuses = Statuses.select().where(Statuses.user == 'Всем').order_by(Statuses.weight.desc())
    add_list = []
    if len(statuses) > 0:
        for index, status in enumerate(statuses):
            add_list.append(KeyboardButton(text=status.title))
            if (index + 1) % 2 == 0:
                keyboard.add(add_list[0], add_list[1])
                add_list = []
        if add_list:
            keyboard.add(add_list[0])
    return keyboard


async def menu_keyboard(user_id: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    work_list = []
    user_status = Statuses.select().where(Statuses.user == str(user_id)).order_by(Statuses.id.desc())
    if len(user_status) > 0:
        for user_st in user_status:
            work_list.append(KeyboardButton(text=user_st.title))
    statuses = Statuses.select().where(Statuses.user == 'Всем').order_by(Statuses.weight.desc())
    if len(statuses) > 0:
        for status in statuses:
            work_list.append(KeyboardButton(text=status.title))
    if work_list:
        add_list = []
        for index, elem in enumerate(work_list):
            add_list.append(elem)
            if (index + 1) % 2 == 0:
                keyboard.add(add_list[0], add_list[1])
                add_list = []
        if add_list:
            keyboard.add(add_list[0])
    keyboard.add(KeyboardButton(key_text.CREATE_STATUS))
    return keyboard.add(
        KeyboardButton(key_text.ADD_FRIEND),
        KeyboardButton(key_text.DEL_FRIEND)
    )


async def friend_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    return keyboard.add(
        KeyboardButton(key_text.ADD_FRIEND),
    )


async def rate_status_keyboard(status_id: int, send_status: int, user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)
    reactions = Reactions.select().where(Reactions.user == 'Всем').order_by(Reactions.id.asc())
    reaction_list = []
    if len(reactions) > 0:
        for reaction in reactions:
            reaction_list.append(InlineKeyboardButton(reaction.reaction, callback_data=f"react&{status_id}&{send_status}&{reaction.id}"))
    user_reactions = Reactions.select().where(Reactions.user == str(user_id)).order_by(Reactions.id.asc())
    if len(user_reactions) > 0:
        for us_reaction in user_reactions:
            reaction_list.append(InlineKeyboardButton(us_reaction.reaction, callback_data=f"react&{status_id}&{send_status}&{us_reaction.id}"))
    if reaction_list:
        add_list = []
        for index, react in enumerate(reaction_list):
            add_list.append(react)
            if (index + 1) % 2 == 0:
                keyboard.add(add_list[0], add_list[1])
                add_list = []
    if add_list:
        keyboard.add(add_list[0])
    return keyboard.add(
        InlineKeyboardButton(text=key_text.CREATE, callback_data=key_text.CREATE)
    )


async def reaction_keyboard(reaction: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(InlineKeyboardButton(reaction, callback_data='pass'))


async def delete_keyboard(user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    friends = Friends.select().where((Friends.user == user_id) | (Friends.referral == user_id))
    for friend in friends:
        if friend.user.id != user_id:
            text = f'❌ {friend.user.first_name}'
        else:
            text = f'❌ {friend.referral.first_name}'
        keyboard.add(InlineKeyboardButton(text=text, callback_data=f"delete&{friend.id}"))
    return keyboard


async def new_friend_keyboard(user_id: int, text: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    if text == 'new':
        return keyboard.add(InlineKeyboardButton(key_text.WELCOME_FRIEND, callback_data=f"welcome&{user_id}"))
    else:
        return keyboard.add(InlineKeyboardButton(key_text.SEND_WELCOME, callback_data="pass"))


async def next_create_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(InlineKeyboardButton(key_text.NEXT_CREATE, callback_data=key_text.NEXT_CREATE))


async def menu_react() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(key_text.SUPER, pay=True),
        InlineKeyboardButton(key_text.EDIT_REACT, callback_data=key_text.EDIT_REACT),
        InlineKeyboardButton(key_text.NEXT_CREATE, callback_data=key_text.NEXT_CREATE),
    )


async def menu_status() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(key_text.SUPER, pay=True),
        InlineKeyboardButton(key_text.EDIT_STATUS, callback_data=key_text.EDIT_STATUS),
        InlineKeyboardButton(key_text.NEXT_CREATE, callback_data=key_text.NEXT_CREATE),
    )


async def free_menu_status() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(key_text.FREE_SUPER, callback_data=key_text.FREE_SUPER),
        InlineKeyboardButton(key_text.EDIT_STATUS, callback_data=key_text.EDIT_STATUS),
        InlineKeyboardButton(key_text.NEXT_CREATE, callback_data=key_text.NEXT_CREATE),
    )


async def cancel_state() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(key_text.CANCEL_SEND, callback_data=key_text.CANCEL_SEND)
    )

