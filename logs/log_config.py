import logging.handlers
import os

print('Loggers!!!!!!!')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', 'bot.log'))


log_handler = logging.handlers.TimedRotatingFileHandler(
    filename=file_path,
    encoding='utf-8',
    interval=1,
    when='midnight'
)
log_handler.setFormatter(formatter)
log_handler.suffix = '%Y-%m-%d'
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger = logging.getLogger('bot_logger')
logger.addHandler(log_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    # for testing purposes

    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')