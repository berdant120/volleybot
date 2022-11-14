from os import environ

environ['TELEGRAM_BOT_TOKEN'] = 'token'
environ['DEV_CHAT_ID'] = '451'
environ['CACHE_FILE_PATH'] = 'cache'
environ['ACCESS_WHITE_LIST'] = 'a,b'


def test_parse_config():
    from config import TELEGRAM_BOT_TOKEN, DEV_CHAT_ID, CACHE_FILE_PATH, ACCESS_WHITE_LIST

    assert TELEGRAM_BOT_TOKEN == 'token'
    assert DEV_CHAT_ID == 451
    assert CACHE_FILE_PATH == 'cache'
    assert ACCESS_WHITE_LIST == ['a', 'b']
