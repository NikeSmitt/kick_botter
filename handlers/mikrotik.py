from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from utils import router_role_and_get_response


@bot.message_handler(commands=['role_start'])
def activate_role(message):
    # MikroTik
    
    db = MySQLHandler()
    
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    to_send = router_role_and_get_response(disable=False)
    
    bot.send_message(message.from_user.id, to_send)


@bot.message_handler(commands=['role_stop'])
def activate_role(message):
    # MikroTik
    
    db = MySQLHandler()
    
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.from_user.id, 'У вас нет прав на выполнение данной команды')
        return
    
    to_send = router_role_and_get_response(disable=True)
    
    bot.send_message(message.from_user.id, to_send)
