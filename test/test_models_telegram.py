import pytest

from models.telegram import PollModel, UserModel


@pytest.fixture
def poll():
    return PollModel(123, 234, 'abc max 3', ['a', 'b', 'c'], 3)


@pytest.fixture
def user_1():
    return UserModel('u1', None, 'l1', 1001)


@pytest.fixture
def user_2():
    return UserModel('u2', None, 'l2', 1002)


def test_poll_model_create(poll):
    assert poll.option_1_limit == 3
    assert len(poll.answers) == 3


def test_poll_model_update(poll, user_1, user_2):
    poll.update_answers([0, 1], user_1)
    poll.update_answers([0, 2], user_2)
    poll.update_answers([0], user_1)

    assert [len(x) for x in poll.answers] == [2, 1, 1]
    assert poll.answers[0].users() == [user_2, user_1]

    poll.update_answers([], user_2)

    assert [len(x) for x in poll.answers] == [1, 1, 0]
    assert user_2.tg_id not in poll.answers[0].votes


def test_formatted_answer_voters(poll, user_1, user_2):
    poll.update_answers([1], user_1)
    poll.update_answers([1], user_2)

    res_1 = poll.formatted_answer_voters(1)
    res_2 = poll.formatted_answer_voters(1, True)

    expected = '1. <a href="tg://user?id=1001">u1</a>\n2. <a href="tg://user?id=1002">u2</a>'
    assert res_1 == expected
    assert expected in res_2
