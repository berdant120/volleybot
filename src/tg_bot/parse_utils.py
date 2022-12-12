import re
import traceback
from datetime import datetime
from typing import Optional

from loguru import logger


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


def parse_player_amount(question: str) -> Optional[int]:
    matches = re.findall(r'(\d)[xXхХ]\1', question)
    if len(matches) > 1:
        raise Exception(f'Only single split option allowed {matches}')

    if not matches:
        return None

    return int(matches[0])


def parse_create_poll_args(args_str: str):
    splitted_args = args_str.split()
    try:
        location_nm, date_str, time_str = splitted_args[1:4]
    except:
        logger.error(f'Cant parse input {args_str}')
        logger.error(traceback.print_exc())
        raise Exception('Incorrect format of input parameters')

    datetime_str = f'{date_str} {time_str}'
    try:
        dttm = datetime.fromisoformat(datetime_str)
    except:
        logger.error(f'Cant parse input datetime {datetime_str}')
        raise Exception(f'Incorrect format of input datetime {datetime_str}')

    return location_nm, dttm
