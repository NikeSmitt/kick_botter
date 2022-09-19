from typing import List, NamedTuple, Union

from telebot import types, custom_filters
from telebot.apihelper import ApiTelegramException
from telebot.handler_backends import State, StatesGroup  # States
from telebot.types import User

from MySQLHandler import MySQLHandler
from bot import cool_logger
from bot_loader import bot


class MyStates(StatesGroup):
    group = State()
    users = State()


class UserCandidate(NamedTuple):
    user_name: str
    status: str
    send_link: bool = False
    telegram_user_id: Union[int, None] = None


@bot.message_handler(commands=['add_users'], for_root=True)
def start_ex(message):
    """
    Start command. Here we are starting state
    """
    bot.set_state(message.from_user.id, MyStates.group, message.chat.id)
    bot.send_message(message.chat.id, 'Добавление пользователей списком'
                                      '\nУкажите имя группы'
                                      '\nДля отмены команда /cancel')


# Any state
@bot.message_handler(state="*", commands=['cancel'])
def any_state(message):
    """
    Cancel state
    """
    bot.send_message(message.chat.id, "Your state was cancelled.")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=MyStates.group)
def group_name_get(message: types.Message):
    db = MySQLHandler()
    
    # проверяем наличие группы в бд
    group_id = db.get_telegram_group_id(message.text)
    
    if group_id:
        
        # проверяем наличие группы в телеграм
        try:
            chat = bot.get_chat(group_id)
        except ApiTelegramException as e:
            cool_logger.error(f'Группы с именем {message.text} в тг не существует')
            bot.reply_to(message, f'Группы с именем {message.text} в ТГ не существует')
            bot.delete_state(message.from_user.id)
            
            return
        
        bot.send_message(message.chat.id, 'Теперь передайте список имен пользователей в столбик')
        bot.set_state(message.from_user.id, MyStates.users, message.chat.id)
        with bot.retrieve_data(message.from_user.id) as data:
            data['group_id'] = group_id
            data['group_name'] = message.text
    else:
        bot.send_message(message.chat.id, f"Группы с таким именем {message.text} не существует в бд")
        bot.delete_state(message.from_user.id)
        return


@bot.message_handler(state=MyStates.users)
def ask_users(message):
    """
    Получили все данные
    """
    
    db = MySQLHandler()
    user_names = list(map(lambda name: name.strip(), message.text.split('\n')))
    
    # тут собираем результаты выполнения команды
    result_output = []
    
    with bot.retrieve_data(message.from_user.id) as data:
        # bot.send_message(message.chat.id, f'Добавляем в {data["group_name"]} этих пользователей {user_names}')
        
        users = check_users_to_send_link(user_names, telegram_group_id=data['group_id'], db=db)
        
        try:
            link = bot.create_chat_invite_link(data['group_id'], f'Ссылка в группу {data["group_name"]}')
        except ApiTelegramException as e:
            bot.reply_to(message, e.result_json['description'])
            cool_logger.error('Ошибка создания инвайт ссылки при добавлении пользователей')
            cool_logger.error(e)
            bot.delete_state(message.from_user.id)
            return
        
        for user in users:
            
            # Если отправляем ссылку пользователю
            if user.send_link:
                try:
                    # отправляем ему ссылку
                    bot.send_message(user.telegram_user_id, link.invite_link)
                    
                    # удаляем из группы в базе (по логике прошлых команд [revert])
                    db.delete_user_in_group(data['group_id'], user.telegram_user_id)
                except ApiTelegramException as e:
                    cool_logger.error(f'Ошибка отправки инвайт ссылки пользователю {user.user_name}')
                    cool_logger.error(e)
                    result_output.append(
                        f'{user.user_name} не отправлена ссылка из-за ошибки {e.result_json["description"]}')
                    continue
            result_output.append(f'{user.user_name} {user.status}')
    
    bot.send_message(message.chat.id, '\n'.join(result_output))
    bot.delete_state(message.from_user.id)


# register filters
# САМАЯ ВАЖНАЯ СТРОЧКА
bot.add_custom_filter(custom_filters.StateFilter(bot))


def check_users_to_send_link(users: list, telegram_group_id: int, db) -> List[UserCandidate]:
    """
    Проверяем каким пользователям отправлять ссылку в данную группу
    :param db: database
    :param users:
    :param telegram_group_id:
    :return:
    """
    output = []
    users_already_in_group = db.get_users_in_group(telegram_group_id)
    for user_name in users:
        telegram_user_id = db.get_telegram_user_id(user_name)
        
        if not telegram_user_id:
            user = UserCandidate(
                user_name=user_name,
                status='не зарегистрирован',
            )
        
        elif telegram_user_id in users_already_in_group and not db.is_user_in_group_kicked(telegram_group_id,
                                                                                           telegram_user_id):
            user = UserCandidate(
                user_name=user_name,
                status='уже есть в группе',
                telegram_user_id=telegram_user_id
            )
        
        else:
            user = UserCandidate(
                user_name=user_name,
                status='cсылка отправлена',
                send_link=True,
                telegram_user_id=telegram_user_id
            )
        output.append(user)
    
    return output
