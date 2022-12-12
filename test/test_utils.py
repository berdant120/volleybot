from datetime import datetime

from tg_bot.parse_utils import parse_max_param, parse_player_amount, parse_create_poll_args
import pytest


@pytest.mark.parametrize('input_str', [
    'question max 11',
    'questionmax 11',
    'question MAX 11',
    'question (max 11)',
    'question[max 11]',
])
def test_parse_max_param(input_str):
    assert parse_max_param(input_str) == 11


@pytest.mark.parametrize('input_str', [
    'asdf7x7asdf',
    'asdf7X7asdf',
    'asdf7х7asdf',
    'asdf7Х7asdf',
])
def test_parse_max_param(input_str):
    assert parse_player_amount(input_str) == 7


@pytest.mark.parametrize('input_str', [
    'asdf7xsf',
    'asdf7X6',
    'asdf7х57asdf',
    'asdf7v7asdf',
])
def test_parse_max_param_empty(input_str):
    assert parse_player_amount(input_str) is None


@pytest.mark.parametrize('input_str, expected', [
    ('/create_poll berawa 2022-11-05 16:00', ('berawa', datetime(2022, 11, 5, 16, 0))),
])
def test_parse_create_poll_args(input_str, expected):
    assert parse_create_poll_args(input_str) == expected
