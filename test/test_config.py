from os import environ

environ['TELEGRAM_BOT_TOKEN'] = 'token'
environ['DEV_CHAT_ID'] = '451'
environ['CACHE_FILE_PATH'] = 'cache'
environ['ACCESS_WHITE_LIST'] = 'a,b'
environ['DEFAULT_EXPORT_SPR_ID'] = 'spr_id'
environ['EXPORT_SPR_TEMPLATE_ID'] = 'templ_id'


def test_parse_config():
    from config import TELEGRAM_BOT_TOKEN, DEV_CHAT_ID, CACHE_FILE_PATH, ACCESS_WHITE_LIST, TEMPLATE_ID, DEFAULT_SPR_ID

    assert TELEGRAM_BOT_TOKEN == 'token'
    assert DEV_CHAT_ID == 451
    assert CACHE_FILE_PATH == 'cache'
    assert ACCESS_WHITE_LIST == ['a', 'b']
    assert TEMPLATE_ID == 'templ_id'
    assert DEFAULT_SPR_ID == 'spr_id'
