from os import environ

environ['TELEGRAM_BOT_TOKEN'] = 'token'
environ['DEV_CHAT_ID'] = '451'
environ['CACHE_FILE_PATH'] = 'cache'
environ['ACCESS_WHITE_LIST'] = 'a,b'
environ['DEFAULT_EXPORT_SPR_ID'] = 'spr_id'
environ['TEAMS_SPR_TEMPLATE_ID'] = 'templ_id'
environ['TOURNAMENT_SPR_TEMPLATE_ID'] = 'tourn_id'
environ['GRANT_SPR_PERMISSION'] = 'c,d'


def test_parse_config():
    from config import TELEGRAM_BOT_TOKEN, DEV_CHAT_ID, CACHE_FILE_PATH, ACCESS_WHITE_LIST, DEFAULT_SPR_ID,\
        TEAMS_TEMPLATE_ID, TOURNAMENT_TEMPLATE_ID, GRANT_SPR_PERMISSION

    assert TELEGRAM_BOT_TOKEN == 'token'
    assert DEV_CHAT_ID == 451
    assert CACHE_FILE_PATH == 'cache'
    assert ACCESS_WHITE_LIST == ['a', 'b']
    assert TEAMS_TEMPLATE_ID == 'templ_id'
    assert TOURNAMENT_TEMPLATE_ID == 'tourn_id'
    assert DEFAULT_SPR_ID == 'spr_id'
    assert GRANT_SPR_PERMISSION == ['c', 'd']
