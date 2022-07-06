import os.path
from datetime import datetime
from pathlib import Path, PurePath
import re

from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
import telebot

from handlers.helpers import is_root


@bot.message_handler(commands=['logs'])
def get_logs(message: telebot.types.Message):
    """
    Получаем логи от бота
    :param message:
    :return:
    """
    
    db = MySQLHandler()
    
    if not is_root(
            message=message,
            logger=cool_logger,
            session=db,
            bot=bot
    ):
        return
    
    
    # получаем путь к папке с логами
    logs_folder_path = Path(__file__).parent.parent.joinpath('logs')
    
    # парсим команду
    if len(message.text.split()) == 1:
        send_log_text(logs_folder_path.joinpath('bot.log'), message)
        return
    try:
        request_date = datetime.strptime(message.text.split(' ')[1], '%d-%m-%Y')
    except (ValueError, IndexError) as e:
        bot.send_message(message.chat.id, f'Ошибка формата команды. Формат - /logs дд-мм-гггг')
        cool_logger.error('Ошибка формата команды logs')
        cool_logger.error(e)
        return
    
    
    
    # флаг нахождения файла
    is_found = False
    
    for file in logs_folder_path.iterdir():
        if re.search(r'\d{4}-\d{2}-\d{2}', file.suffix):
            try:
                log_file_date = datetime.strptime(file.suffix[1:], '%Y-%m-%d')
            except (ValueError, IndexError):
                cool_logger.error('Ошибка парсинга даты в лог файле')
            
            else:
                if request_date == log_file_date:
                    send_log_text(file, message)
                    is_found = True
                    break
    
    if not is_found:
        bot.send_message(message.from_user.id, f'Логи с датой {request_date.strftime("%d-%m-%Y")} не найдены')


def send_log_text(file_path, message):
    try:
        with open(file_path, 'r') as f:
            
            new_name_path = os.path.join(file_path.parent, file_path.name + '.' + 'txt')
            with open(new_name_path, 'w', encoding='utf-8') as file_to_save:
                file_to_save.write(f.read())
            
            with open(new_name_path, 'rb') as file_to_send:
                bot.send_document(message.from_user.id, file_to_send)
                cool_logger.info(f'Отправлен лог файл {file_path.name} пользователю {message.from_user.username}')
        
        os.remove(new_name_path)
    except Exception as e:
        cool_logger.error(e)
        bot.send_document(message.from_user.id, f'Ошибка отправки лог файла')


if __name__ == '__main__':
    pass
