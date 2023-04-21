"""
Файл - содержит хэндлер для отлова сообщений вне сценария и удаления сообщений пользователя
"""
import asyncio
from datetime import timedelta, datetime
from aiogram import Dispatcher, types
from loader import logger, bot
from database.models import *
from settings import constants


async def delete_message(user_id: int) -> None:
    """
    Функция - обрабатывает удаление сообщений
    :param user_id: int
    :return: None
    """
    try:
        message = DeleteMessage.select().where(DeleteMessage.chat_id == user_id)
        if len(message):
            for mess in message:
                if '&' in mess.message_id:
                    mes_ids = mess.message_id.split('&')
                    for elem in mes_ids:
                        try:
                            await bot.delete_message(chat_id=mess.chat_id, message_id=int(elem))
                        except Exception as ex:
                            print(ex)
                else:
                    try:
                        await bot.delete_message(chat_id=mess.chat_id, message_id=int(mess.message_id))
                    except Exception as ex:
                        print(ex)
                try:
                    mess.delete_instance()
                except Exception as ex:
                    print(ex)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def timer_func(sleep_for: int) -> None:
    """
    Функция - работающая в отдельном потоке, отправляет уведомление пользователю, если он не был активен 12 часов
    :param sleep_for: int
    :return: None
    """
    try:
        while True:
            await asyncio.sleep(sleep_for)
            users = Users.select()
            if len(users) > 0:
                for user in users:
                    if user.last_active:
                        active = user.last_active + timedelta(hours=12)
                        if active.timestamp() <= datetime.today().timestamp():
                            try:
                                user.last_active = datetime.today()
                                user.save()
                                await bot.send_message(user.user_id, constants.TIMER)
                            except Exception:
                                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def echo_handler(message: types.Message) -> None:
    """
    Хэндлер - оповещает бота о некорректной команде (Эхо)
    :param message: Message
    :return: None
    """
    try:
        logger.error(f"Эхо {message.text}")
        await message.delete()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_echo_handlers(dp: Dispatcher) -> None:
    """
    Функция - регистрирует все хэндлеры файла echo.py
    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(echo_handler, state='*')
