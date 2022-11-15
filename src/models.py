from dataclasses import dataclass, field, InitVar
from typing import List, Dict
from datetime import datetime

from telegram.utils.helpers import mention_html

from utils import parse_max_param


@dataclass
class UserModel:
    name: str
    link: str
    tg_id: int


@dataclass
class PollAnswerModel:
    user: UserModel
    datetime: datetime


@dataclass
class PollOption:
    text: str
    votes: Dict[int, PollAnswerModel] = field(default_factory=dict)

    def add_vote(self, user: UserModel):
        self.votes[user.tg_id] = PollAnswerModel(user, datetime.utcnow())

    def remove_vote(self, user_id: int):
        if user_id in self.votes:
            del self.votes[user_id]

    def users(self):
        return [x.user for x in sorted(self.votes.values(), key=lambda v: v.datetime)]

    def __len__(self):
        return len(self.votes)


@dataclass
class PollModel:
    message_id: int
    chat_id: int
    question: str
    options: InitVar[List[str]]
    created_dt: datetime = None
    option_1_limit: int = None
    answers: List[PollOption] = None
    closed: bool = False

    def __post_init__(self, options: List[str]):
        self.option_1_limit = parse_max_param(self.question)
        self.answers = [PollOption(x) for x in options]
        self.created_dt = datetime.utcnow()

    def update_answers(self, selected_options: List[int], user: UserModel):
        if not selected_options:
            for option in self.answers:
                option.remove_vote(user.tg_id)
            return

        for selected_option in selected_options:
            self.answers[selected_option].add_vote(user)

    def formatted_answer_voters(self, option_num: int, with_desc: bool = False) -> str:
        users = self.answers[option_num].users()
        users_htmls = [f'{i + 1}. {mention_html(x.tg_id, x.name)}' for i, x in enumerate(users)]
        user_list_str = '\n'.join(users_htmls)
        if not with_desc:
            return user_list_str

        return f'People who answered "{self.answers[option_num].text}":\n\n{user_list_str}'
