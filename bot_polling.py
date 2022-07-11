from bot_loader import bot


if __name__ == "__main__":
    print('Bot started...')
    # test_api()
    # pprint(len(bot.message_handlers))
    
    bot.polling(non_stop=True)
    bot.send_message(416205005, 'Bot started...')
