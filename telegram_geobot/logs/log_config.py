"""Config file for the app."""

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
)

# Logging to file
file_handler = logging.FileHandler('telegram_geobot/logs/geobot.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Logging to terminal
terminal_handler = logging.StreamHandler()
terminal_handler.setLevel(logging.INFO)
terminal_handler.setFormatter(formatter)

# Adding handlers
logger.addHandler(file_handler)
logger.addHandler(terminal_handler)


if __name__ == '__main__':
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
