"""
Файл с хэндлерами логики работы бота
"""
import asyncio
import os
import re
from datetime import datetime, timedelta
from typing import Union

import xlsxwriter
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import LabeledPrice
from database.models import *
from database.states import FSMCreateReact, FSMAdmin, FSMImage
from handlers.echo import delete_message
from keyboards import key_text
from keyboards.keyboards import status_keyboard, menu_keyboard, friend_keyboard, rate_status_keyboard, \
    reaction_keyboard, delete_keyboard, new_friend_keyboard, next_create_keyboard, menu_react, menu_status, \
    free_menu_status, cancel_state
from loader import bot, logger
from settings import constants
from settings.settings import PAY_TOKEN


async def friend_logic(referral, user_id: int) -> Tuple:
    """
    Функция - обрабатывает логику друзей
    :param referral: ModelSelect
    :param user_id: int
    :return: None
    """
    try:
        user = Users.get(Users.user_id == user_id)
        if Friends.get_or_none(Friends.user == user.id, Friends.referral == referral.id) or\
                Friends.get_or_none(Friends.user == referral.id, Friends.referral == user.id):
            await bot.send_message(referral.user_id, constants.URA, reply_markup=await menu_keyboard(referral.user_id))
        else:
            Friends(user=user.id, referral=referral.id).save()
            user.friends += 1
            user.my_referral += 1
            user.save()
            referral.friends += 1
            referral.referral = True
            referral.save()
            try:
                photos = await bot.get_user_profile_photos(referral.user_id, limit=1)
                if photos['total_count'] > 0:
                    photo = photos['photos'][0][0]['file_id']
                else:
                    photo = open('media/anonymus.jpg', 'rb')
                await bot.send_photo(
                    user.user_id, photo=photo, caption=constants.NEW_FRIEND.format(referral.first_name),
                    reply_markup=await new_friend_keyboard(referral.id, 'new')
                )
                if user.friends == 1:
                    await bot.send_photo(
                        user.user_id, photo=open('media/what_now.jpg', 'rb'), caption=constants.WHAT_NOW,
                        reply_markup=await menu_keyboard(referral.user_id)
                    )
            except Exception:
                pass
            photos = await bot.get_user_profile_photos(user.user_id, limit=1)
            if photos['total_count'] > 0:
                await bot.send_photo(
                    referral.user_id, photo=photos['photos'][0][0]['file_id'],
                    caption=constants.NEW_FRIEND.format(user.first_name)
                )
            else:
                await bot.send_photo(
                    referral.user_id, photo=open('media/anonymus.jpg', 'rb'),
                    caption=constants.NEW_FRIEND.format(user.first_name)
                )
            if referral.friends == 1:
                await bot.send_photo(
                    referral.user_id, photo=open('media/what_now.jpg', 'rb'), caption=constants.WHAT_NOW,
                    reply_markup=await menu_keyboard(referral.user_id)
                )
            else:
                await bot.send_message(referral.user_id, constants.URA, reply_markup=await menu_keyboard(referral.user_id))
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def start_command(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает команду /start
    :param state:
    :param message: Message
    :return: None
    """
    try:
        if await state.get_state():
            await state.finish()
        await delete_message(message.from_user.id)
        users = Users.get_or_none(Users.user_id == message.from_user.id)
        if users:
            if re.findall(r'\d+', message.text) and [str(message.from_user.id)] != re.findall(r'\d+', message.text):
                await friend_logic(users, int(re.findall(r'\b\d+\b', message.text)[0]))
            else:
                if users.last_status is None:
                    await bot.send_message(message.from_user.id, constants.URA, reply_markup=await status_keyboard())
                else:
                    if users.friends > 0:
                        await bot.send_message(message.from_user.id, constants.URA, reply_markup=await menu_keyboard(message.from_user.id))
                    else:
                        await bot.send_message(
                            message.from_user.id, constants.FIRST_FRIEND, reply_markup=await friend_keyboard(),
                            disable_web_page_preview=True
                        )
        else:
            if message.from_user.first_name and message.from_user.last_name:
                first_name = f"{message.from_user.first_name} {message.from_user.last_name}"
            elif message.from_user.first_name:
                first_name = f"{message.from_user.first_name}"
            elif message.from_user.last_name:
                first_name = f"{message.from_user.last_name}"
            elif message.from_user.username:
                first_name = f"{message.from_user.username}"
            else:
                first_name = f"Аноним"
            Users(
                created_at=datetime.today(), user_id=message.from_user.id,
                username=message.from_user.username, first_name=first_name
            ).save()
            users = Users.get_or_none(Users.user_id == message.from_user.id)
            if re.findall(r'\d+', message.text) and [str(message.from_user.id)] != re.findall(r'\d+', message.text):
                await friend_logic(users, int(re.findall(r'\b\d+\b', message.text)[0]))
            else:
                await bot.send_message(message.from_user.id, constants.URA, reply_markup=await status_keyboard())
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def status_handler(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает нажатие на установку нового статуса
    :param state: FSMContext
    :param message: Message
    :return: None
    """
    try:
        await delete_message(message.from_user.id)
        status = Statuses.get_or_none(
            (Statuses.title == message.text) & (Statuses.user == 'Всем') | (Statuses.title == message.text) & (Statuses.user == str(message.from_user.id))
        )
        if status:
            logger.error(status.title)
            user = Users.get(Users.user_id == message.from_user.id)
            if user:
                if user.last_status is None:
                    diff = True
                else:
                    last_status = user.last_status + timedelta(minutes=10)
                    current_date = datetime.today()
                    if last_status.date() == current_date.date() and last_status.time() <= current_date.time() or last_status.date() < current_date.date():
                        diff = True
                    else:
                        diff = False
                if diff:
                    bot_message = await bot.send_message(message.from_user.id, constants.SEND_STATUS.format(status.title))
                    if user.friends == 0:
                        user.last_status = datetime.today() - timedelta(minutes=11)
                        user.save()
                        await asyncio.sleep(3)
                        await bot.send_message(
                            message.from_user.id, constants.EMPTY_FRIENDS.format(status.title),
                        )
                        await asyncio.sleep(3)
                        await bot.send_message(
                            message.from_user.id, constants.FIRST_FRIEND, reply_markup=await friend_keyboard(),
                            disable_web_page_preview=True
                        )
                    else:
                        async with state.proxy() as data:
                            if data.get('file_id', None):
                                image = (await bot.get_file(data['file_id'])).file_path
                                downloaded_file = await bot.download_file(image)
                                src = os.path.abspath(os.path.join('../friends/media/', image))
                                with open(src, 'wb') as new_file:
                                    new_file.write(downloaded_file.read())
                                await bot.delete_message(chat_id=message.from_user.id, message_id=data['message'])
                            else:
                                image = None
                            if status:
                                SendStatuses(
                                    created_at=datetime.today(), user=user.id, status=status.id, message_id=bot_message.message_id,
                                    message_text=f"{constants.SEND_STATUS.format(status.title)}\n\n", image=image
                                ).save()
                                status.quantity += 1
                                status.save()
                            user.send_status += 1
                            user.last_status = datetime.today()
                            user.last_active = datetime.today()
                            user.real_active = datetime.today()
                            user.save()
                            friends = Friends.select().where((Friends.user == user.id) | (Friends.referral == user.id))
                            if len(friends) > 0:
                                send_status = SendStatuses.select().where(
                                    SendStatuses.user == user.id).order_by(SendStatuses.created_at.desc()).get()
                                for friend in friends:
                                    try:
                                        if friend.user.id != user.id:
                                            recipient = friend.user.user_id
                                        else:
                                            recipient = friend.referral.user_id
                                        if user.username:
                                            text = constants.NEW_STATUS_LINK.format(user.username, user.first_name, status.title)
                                        else:
                                            text = constants.NEW_STATUS.format(user.first_name, status.title)
                                        photos = await bot.get_user_profile_photos(message.from_user.id, limit=1)
                                        if image:
                                            photo = open(f"../friends/media/{image}", 'rb')
                                        else:
                                            if photos['total_count'] > 0:
                                                photo = photos['photos'][0][0]['file_id']
                                            else:
                                                photo = open('media/anonymus.jpg', 'rb')
                                        await bot.send_photo(
                                            recipient, photo=photo, caption=text,
                                            reply_markup=await rate_status_keyboard(status.id, send_status.id, recipient)
                                        )
                                        user_fr = Users.get_or_none(Users.user_id == recipient)
                                        if user_fr:
                                            user_fr.get_status += 1
                                            count_reaction = SendReactions.select().where(
                                                SendReactions.user == user_fr.id).count()
                                            user_fr.percent = round((count_reaction / user_fr.get_status) * 100, 2)
                                            user_fr.save()
                                    except Exception as ex:
                                        logger.error(ex)
                                await state.finish()
                else:
                    async with state.proxy() as data:
                        if data.get('message', None):
                            await bot.delete_message(chat_id=message.from_user.id, message_id=data['message'])
                    if await state.get_state():
                        await state.finish()
                    await bot.send_message(message.from_user.id, constants.TEN_MINUTES)
        else:
            logger.error(message.text)
            await message.delete()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def user_react_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку реакции на статус
    :param call: CallbackQuery
    :return: None
    """
    try:
        await delete_message(call.from_user.id)
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            user.last_active = datetime.today()
            user.real_active = datetime.today()
            action, status_id, send_status_id, reaction_id = call.data.split('&')
            reaction = Reactions.get(Reactions.id == int(reaction_id))
            await bot.edit_message_reply_markup(
                chat_id=call.from_user.id, message_id=call.message.message_id,
                reply_markup=await reaction_keyboard(reaction.reaction)
            )
            photos = await bot.get_user_profile_photos(call.from_user.id, limit=1)
            send_status = SendStatuses.get_or_none(SendStatuses.id == int(send_status_id))
            if send_status:
                SendReactions(
                    created_at=datetime.today(), send_status=send_status.id, user=user.id, reaction=reaction.reaction
                ).save()
                count_reaction = SendReactions.select().where(SendReactions.user == user.id).count()
                user.percent = round((count_reaction / user.get_status) * 100, 2)
                user.save()
                if user.username:
                    text = constants.YOUR_LIKE_LINK.format(user.username, user.first_name, reaction.reaction, send_status.status.title)
                    username = f' <a href="{user.username}">{user.first_name}</a>\n'
                else:
                    text = constants.YOUR_LIKE.format(user.first_name, reaction.reaction, send_status.status.title)
                    username = f' {user.first_name}\n'
                try:
                    message_text = f"{send_status.message_text}{reaction.reaction}{username}"
                    send_status.message_text = message_text
                    send_status.save()
                    await bot.edit_message_text(chat_id=send_status.user.user_id, message_id=send_status.message_id, text=message_text)
                    if photos['total_count'] > 0:
                        photo = photos['photos'][0][0]['file_id']
                    else:
                        photo = open('media/anonymus.jpg', 'rb')
                    await bot.send_photo(send_status.user.user_id, photo=photo, caption=text)
                except Exception:
                    pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def delete_friends_handler(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку удаления друзей.
    :param state: FSMContext
    :param message: Message
    :return: None
    """
    try:
        if await state.get_state():
            await state.finish()
        await message.delete()
        await delete_message(message.from_user.id)
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if user:
            friends = Friends.select().where((Friends.user == user.id) | (Friends.referral == user.id)).count()
            bot_message = await bot.send_message(
                message.from_user.id, constants.WHO_DELETE.format(friends),
                reply_markup=await delete_keyboard(user.id)
            )
            DeleteMessage(chat_id=message.from_user.id, message_id=bot_message.message_id).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def delete_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку удаления определенного друга
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            friend_id = int(call.data.split('&')[1])
            friend = Friends.get_or_none(Friends.id == friend_id)
            if friend:
                if friend.user.user_id != call.from_user.id:
                    name = friend.user.first_name
                    user_fr = Users.get_or_none(Users.id == friend.user.id)
                    if user_fr:
                        user_fr.my_referral -= 1
                        user_fr.save()
                else:
                    name = friend.referral.first_name
                    user.my_referral -= 1
                await delete_message(call.from_user.id)
                await bot.send_message(call.from_user.id, constants.DELETE.format(name))
                friend.delete_instance()
                user.friends -= 1
                user.save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def add_friend(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку добавить друга
    :param state: FSMContext
    :param message: Message
    :return: None
    """
    try:
        if await state.get_state():
            await state.finish()
        await delete_message(message.from_user.id)
        await bot.send_message(message.from_user.id, constants.ADD_FRIEND)
        await bot.send_message(message.from_user.id, constants.REFERRAL.format(message.from_user.id))
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def welcome_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку welcome
    :param call:
    :return:
    """
    try:
        user_id = int(call.data.split('&')[1])
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=await new_friend_keyboard(user_id, 'send_welcome')
        )
        friend = Users.get_or_none(Users.id == user_id)
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if friend is not None and user is not None:
            photos = await bot.get_user_profile_photos(call.from_user.id, limit=1)
            if photos['total_count'] > 0:
                photo = photos['photos'][0][0]['file_id']
            else:
                photo = open('media/anonymus.jpg', 'rb')
            await bot.send_photo(friend.user_id, photo=photo, caption=constants.WELCOME.format(user.first_name))
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def create_handler(call: Union[types.CallbackQuery, types.Message], state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку create_react
    :param state: FSMContext
    :param call: CallbackQuery
    :return: None
    """
    try:
        if await state.get_state():
            await state.finish()
        await delete_message(call.from_user.id)
        await FSMCreateReact.reaction.set()
        bot_message = await bot.send_message(call.from_user.id, constants.CREATE, reply_markup=await next_create_keyboard())
        DeleteMessage(chat_id=call.from_user.id, message_id=bot_message.message_id).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def create_status_handler(call: Union[types.CallbackQuery, types.Message], state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку create_status
    :param state: FSMContext
    :param call: CallbackQuery
    :return: None
    """
    try:
        logger.error(call)
        if await state.get_state():
            await state.finish()
        await delete_message(call.from_user.id)
        await FSMCreateReact.status.set()
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            if user.free:
                bot_message = await bot.send_message(call.from_user.id, constants.CREATE_STATUS_PAY, reply_markup=await next_create_keyboard())
            else:
                bot_message = await bot.send_message(call.from_user.id, constants.CREATE_STATUS,  reply_markup=await next_create_keyboard())
            DeleteMessage(chat_id=call.from_user.id, message_id=bot_message.message_id).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def next_create_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку next_create
    :param state: FSMContext
    :param call: CallbackQuery
    :return: None
    """
    try:
        if await state.get_state():
            await state.finish()
        await delete_message(call.from_user.id)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def reaction_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние reaction
    :param state: FSMContext
    :param message: Message
    :return: None
    """
    try:
        await delete_message(message.from_user.id)
        if len(message.text) <= 12:
            async with state.proxy() as data:
                if isinstance(message, types.Message):
                    data['reaction'] = message.text
                    bot_message = await bot.send_message(message.from_user.id, data['reaction'])
                save_message = await bot.send_invoice(
                    chat_id=message.from_user.id,
                    title="Создание реакции",
                    description=constants.VIEW_REACT,
                    payload='1284561234',
                    provider_token=PAY_TOKEN,
                    currency='RUB',
                    start_parameter='test',
                    prices=[LabeledPrice(label='Руб', amount=10000)],
                    reply_markup=await menu_react()
                )
                DeleteMessage(chat_id=message.from_user.id, message_id=f"{bot_message.message_id}&{save_message.message_id}").save()
        else:
            await create_handler(message, state)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def status_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние status
    :param state: FSMContext
    :param message: Message
    :return: None
    """
    try:
        await delete_message(message.from_user.id)
        if len(message.text) <= 22:
            async with state.proxy() as data:
                if isinstance(message, types.Message):
                    data['status'] = message.text
                user = Users.get_or_none(Users.user_id == message.from_user.id)
                if user:
                    bot_message = await bot.send_message(message.from_user.id, data['status'])
                    if user.free:
                        save_message = await bot.send_invoice(
                            chat_id=message.from_user.id,
                            title="Создание статуса",
                            description=constants.VIEW_STATUS,
                            payload='1284561234',
                            provider_token=PAY_TOKEN,
                            currency='RUB',
                            start_parameter='test',
                            prices=[LabeledPrice(label='Руб', amount=10000)],
                            reply_markup=await menu_status()
                        )
                    else:
                        save_message = await bot.send_message(
                            message.from_user.id, constants.VIEW_STATUS, reply_markup=await free_menu_status()
                        )
                    DeleteMessage(chat_id=message.from_user.id, message_id=f"{bot_message.message_id}&{save_message.message_id}").save()
        else:
            await create_status_handler(message, state)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def super_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обарбатывает нажатие на кнопку super
    :param call: CallbackQuery
    :param state: FSMContext
    :return: None
    """
    try:
        await delete_message(call.from_user.id)
        async with state.proxy() as data:
            user = Users.get_or_none(Users.user_id == call.from_user.id)
            if user:
                user.free = True
                user.save()
                Statuses(user=str(call.from_user.id), title=data['status']).save()
                await bot.send_message(call.from_user.id, constants.SAVE_STATUS)
        await state.finish()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery) -> None:
    """
    Хэндлер - обрабатывает оплату
    :param pre_checkout_query: PreCheckoutQuery
    :return: None
    """
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def process_pay_handler(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает успешную оплату пользователя. Сохраняет реакцию.
    :param state: FSMContext
    :param message: Message
    :return: None
    """
    try:
        await delete_message(message.from_user.id)
        async with state.proxy() as data:
            if data.get('reaction', None):
                Reactions(user=str(message.from_user.id), reaction=data['reaction']).save()
                await bot.send_message(message.from_user.id, constants.SAVE_REACTIONS.format(data['reaction']))
            elif data.get('status', None):
                Statuses(user=str(message.from_user.id), title=data['status'], pay_status=True).save()
                await bot.send_message(message.from_user.id, constants.SAVE_STATUS)
        await state.finish()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def retention_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает нажатие команды retention
    :param message: Message
    :return: None
    """
    try:
        if message.from_user.id == 230971636:
            start_date = datetime.strptime('27.09.2022', '%d.%m.%Y').date()
            end_date = datetime.today().date() + timedelta(days=1)
            count = 0
            workbook = xlsxwriter.Workbook('statistics.xlsx')
            worksheet = workbook.add_worksheet()
            while start_date != end_date:
                users = Users.select().where(
                    (Users.created_at.year == start_date.year) & (Users.created_at.month == start_date.month) & (Users.created_at.day == start_date.day)
                )
                end_list = [datetime.strftime(start_date, '%d.%m.%Y'), len(users)]
                if count == 0:
                    header_list = ['Дата регистрации']
                    for i in range(0, (end_date - start_date).days + 1):
                        header_list.append(f"D{i}")
                    for y in range(len(header_list)):
                        worksheet.write(0, y, header_list[y])
                    count += 1
                if len(users) > 0:
                    users = [elem.id for elem in users]
                    send_statuses = SendStatuses.select().where(SendStatuses.user.in_(users))
                    send_reactions = SendReactions.select().where(SendReactions.user.in_(users))
                    add_list = []
                    work_list = []
                    if len(send_statuses) > 0:
                        for elem in send_statuses:
                            if [elem.created_at.date(), elem.user.id] not in add_list:
                                add_list.append([elem.created_at.date(), elem.user.id])
                                work_list.append(elem.created_at.date())
                    if len(send_reactions) > 0:
                        for elem in send_reactions:
                            if [elem.created_at.date(), elem.user.id] not in add_list:
                                add_list.append([elem.created_at.date(), elem.user.id])
                                work_list.append(elem.created_at.date())
                    if work_list:
                        string_date = start_date + timedelta(days=1)
                        while string_date != end_date:
                            end_list.append(work_list.count(string_date))
                            string_date += timedelta(days=1)
                for index, element in enumerate(end_list):
                    worksheet.write(count, index, element)
                start_date += timedelta(days=1)
                count += 1
            workbook.close()
            await bot.send_document(message.from_user.id, document=open('statistics.xlsx', 'rb'))
            os.remove('statistics.xlsx')
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def send_admin_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку send_admin
    :param message: Message
    :return: None
    """
    try:
        if message.from_user.id == 230971636:
            await FSMAdmin.message.set()
            await bot.send_message(message.from_user.id, constants.SEND_MESSAGE)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def admin_message_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние message. Делает рассылку пользователям
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        await bot.send_message(message.from_user.id, constants.COMPLETE_MESSAGE)
        await state.finish()
        users = Users.select()
        if len(users) > 0:
            for user in users:
                try:
                    await bot.send_message(user.user_id, message.text)
                except Exception:
                    pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def image_handler(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает изображение от пользователя
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        if await state.get_state():
            await state.finish()
        async with state.proxy() as data:
            data['message'] = message.message_id
            data['file_id'] = message.photo[len(message.photo) - 1].file_id
        await FSMImage.status.set()
        await bot.send_message(
            message.from_user.id, constants.IMAGE, reply_markup=await cancel_state()
        )
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def cancel_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обарбаытвает нажатие на кнопку отмены изображения
    :param call: CallbackQuery
    :param state: FSMContext
    :return: None
    """
    try:
        async with state.proxy() as data:
            await bot.delete_message(chat_id=call.from_user.id, message_id=data['message'])
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await state.finish()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_start_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_command, commands=['start'], state='*')
    dp.register_callback_query_handler(cancel_handler, Text(key_text.CANCEL_SEND), state=FSMImage.status)
    dp.register_callback_query_handler(user_react_handler, Text(startswith='react'), state='*')
    dp.register_message_handler(delete_friends_handler, Text(equals=key_text.DEL_FRIEND), state='*')
    dp.register_callback_query_handler(delete_handler, Text(startswith='delete'), state='*')
    dp.register_message_handler(add_friend, Text(equals=key_text.ADD_FRIEND), state='*')
    dp.register_callback_query_handler(welcome_handler, Text(startswith='welcome'), state='*')
    dp.register_callback_query_handler(create_handler, Text(key_text.CREATE), state='*')
    dp.register_message_handler(create_status_handler, Text(key_text.CREATE_STATUS), state='*')
    dp.register_callback_query_handler(next_create_handler, Text(key_text.NEXT_CREATE), state='*')
    dp.register_callback_query_handler(create_handler, Text(key_text.EDIT_REACT), state='*')
    dp.register_callback_query_handler(create_status_handler, Text(key_text.EDIT_STATUS), state='*')
    dp.register_message_handler(reaction_state, content_types=['text'], state=FSMCreateReact.reaction)
    dp.register_message_handler(status_state, content_types=['text'], state=FSMCreateReact.status)
    dp.register_callback_query_handler(super_state, Text(key_text.FREE_SUPER), state=FSMCreateReact.status)
    dp.register_pre_checkout_query_handler(pre_checkout_handler, lambda query: True, state='*')
    dp.register_message_handler(process_pay_handler, content_types=['successful_payment'], state='*')
    dp.register_message_handler(retention_handler, Text('/retention'), state='*')
    dp.register_message_handler(send_admin_handler, Text('/sendmessage'), state='*')
    dp.register_message_handler(admin_message_state, content_types=['text'], state=FSMAdmin.message)
    dp.register_message_handler(image_handler, content_types=['photo'], state='*')
    dp.register_message_handler(status_handler, content_types=['text'], state='*')
