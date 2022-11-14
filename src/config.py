from os import environ

TELEGRAM_BOT_TOKEN = environ['TELEGRAM_BOT_TOKEN']
DEV_CHAT_ID = int(environ['DEV_CHAT_ID'])
CACHE_FILE_PATH = environ['CACHE_FILE_PATH']

ACCESS_WHITE_LIST = environ['ACCESS_WHITE_LIST'].split(',') if 'ACCESS_WHITE_LIST' in environ else None
