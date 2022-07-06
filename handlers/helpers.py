import json
from typing import Optional

import requests
import telebot

import config
from MySQLHandler import MySQLHandler
from bot import cool_logger
from utils import create_time_stamp


def get_invite_link(bot: telebot.TeleBot, db: MySQLHandler, telegram_group_id: int, group_name: str) -> Optional[str]:
    # проверяем, что существует инвайт линк
    export_invite_link = db.get_last_invite_link(telegram_group_id)
    cool_logger.debug(f'Получена инвайт ссылка из бд для группы {group_name}')
    
    if not export_invite_link:
        # Создаем основную ссылку для приглашения в группу
        try:
            export_chat_invite_link = bot.export_chat_invite_link(telegram_group_id)
            cool_logger.debug(f'Создана инвайт ссылка для группы {group_name}')
        
        except Exception as err:
            cool_logger.error(f'Ошибка создания инвайт ссылки для группы {group_name}')
            cool_logger.error(f'{err}')
        
        else:
            # Сохраняем инвайт ссылку
            db.save_last_invite_link(export_chat_invite_link, telegram_group_id)
    
    # создаем дату, которой будет действовать ссылка
    expire_date = create_time_stamp(days=7)
    
    # создаем ссылку
    url = f"https://api.telegram.org/bot{config.TOKEN}/createChatInviteLink?" \
          f"chat_id={telegram_group_id}&expire_date={expire_date}"
    
    # запрос
    req = requests.request("GET", url)
    
    # делаем json и забераем ссылку
    json_response = json.loads(req.text)
    
    # отправляем ссылку в группу
    if 'result' in json_response and 'invite_link' in json_response['result']:
        new_invite_link = json_response['result']['invite_link']
        cool_logger.debug(f'Создана новая инвайт ссылка для группы {group_name}')
        return new_invite_link
    else:
        cool_logger.error(f'Ошибка создания новой инвайт ссылки для группы {group_name}')


def is_root(message: telebot.types.Message, session: MySQLHandler, logger, bot: telebot.TeleBot) -> bool:
    """
    Проверяем, что пользователь root
    :param bot: telebot
    :param logger: logger
    :param session: database
    :param message: message
    :return: bool
    """
    if not session.is_root(message.from_user.id):
        logger.warning(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return False
    return True
