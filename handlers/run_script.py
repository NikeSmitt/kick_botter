import stat

from MySQLHandler import MySQLHandler
from bot import bot, cool_logger


@bot.message_handler(commands=['run'])
def run_bash_script(message):
    """
    Создаем хендлер run script_name arg1 arg2 ...
    При получении команды, бот должен запустить скрипт с указанным именем.
    Полученный в результате вывод – возвращает ответным сообщением.
    :param message:
    :return:
    """
    import subprocess
    import os
    
    db = MySQLHandler()
    
    # проверяем права пользователя
    if not (db.is_root(message.from_user.id) or db.can_run_scripts(message.from_user.id)):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    try:
        script_name, *args = message.text.split()[1:]
        print(script_name)
        print(*args)
    
    except ValueError:
        print('Ошибка формата команды run')
        return
    
    word_dir = f'./work_dir/scripts/{script_name}'
    os.chmod(word_dir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
    output = subprocess.check_output([word_dir, script_name, *args])
    print(output.decode('utf-8'))
    bot.send_message(message.chat.id, output.decode('utf-8'))
