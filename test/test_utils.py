from utils import parse_max_param, parse_player_amount
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
