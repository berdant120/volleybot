from datetime import datetime

import pytest

from data_providers.poll_config_loader import JsonPollConfigLoader
from tg_bot.poll_generator import PollGenerator


@pytest.fixture
def poll_generator():
    loader = JsonPollConfigLoader('test/resources/poll_template.json')
    return PollGenerator(loader)


def test_create_combined_poll(poll_generator):
    combined_poll = poll_generator.create_combined_poll(351, 'berawa', datetime(2020, 5, 5, 16, 20))

    assert len(combined_poll.leagues) == 2
    assert combined_poll.leagues[0].poll.question == 'Лига A | Уровень: Высокий\nФормат игр: 2x2'
    assert combined_poll.chat_id == 351
    assert 'Дата: 5 мая' in combined_poll.common_message
    assert 'Время: 16:20' in combined_poll.common_message
    assert 'Локация: [Пляж Berawa' in combined_poll.common_message


def test_combined_poll_closed(poll_generator):
    combined_poll = poll_generator.create_combined_poll(351, 'berawa', datetime(2020, 5, 5, 16, 20))
    assert not combined_poll.closed

    combined_poll.leagues[0].poll.closed = True
    assert not combined_poll.closed

    combined_poll.leagues[1].poll.closed = True
    assert combined_poll.closed
