from utils import parse_max_param
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
