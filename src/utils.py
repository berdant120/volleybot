import re

from config import ACCESS_WHITE_LIST


def parse_max_param(question: str) -> int:
    question = question.lower()
    if 'max' not in question:
        msg = '"max" parameter is not found in the question'
        raise Exception(msg)

    question_split = re.split(r', |_|-|!|]|\[|\(|\)| ', question)
    max_indexes = [i for i, x in enumerate(question_split) if 'max' in x]
    if len(max_indexes) > 1:
        msg = '"max" parameter is ambiguous'
        raise Exception(msg)

    raw_value = question_split[max_indexes[0] + 1]
    return int(raw_value)


def check_permissions(user_name):
    if not ACCESS_WHITE_LIST:
        return

    error_msg = 'You don`t have permissions to use this function, please contact @berd_ant for more info'
    if user_name not in ACCESS_WHITE_LIST:
        raise Exception(error_msg)
