from dataclasses import dataclass, field, InitVar
from datetime import datetime
from typing import List, Dict, Optional

from telegram.utils.helpers import mention_html


@dataclass
class UserModel:
    first_nm: str
    last_nm: Optional[str]
    link: Optional[str]
    tg_id: int

    def __str__(self):
        last_nm = f'@{self.link}' if self.link else self.last_nm if self.last_nm else ''
        return f'{self.first_nm} {last_nm}'

    @property
    def full_name(self):
        last_nm = f' {self.last_nm}' if self.last_nm else ''
        return f'{self.first_nm}{last_nm}'


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

    def users(self) -> List[UserModel]:
        return [x.user for x in sorted(self.votes.values(), key=lambda v: v.datetime)]

    def __len__(self) -> int:
        return len(self.votes)


@dataclass
class PollModel:
    chat_id: int
    question: str
    options: InitVar[List[str]]
    option_1_limit: int
    message_id: Optional[int] = None
    created_dt: datetime = None
    answers: List[PollOption] = None
    closed: bool = False
    combined_poll_message_id: Optional[int] = None

    def __post_init__(self, options: List[str]):
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
        users_htmls = [f'{i + 1}. {mention_html(x.tg_id, x.full_name)}' for i, x in enumerate(users)]
        user_list_str = '\n'.join(users_htmls)
        if not with_desc:
            return user_list_str

        return f'People who answered "{self.answers[option_num].text}":\n\n{user_list_str}'


@dataclass
class League:
    name: str
    teams_cnt: int
    player_per_team: int
    poll: PollModel


@dataclass
class CombinedPoll:
    chat_id: int
    common_message: str
    leagues: List[League]
    event_dttm: datetime
    location_nm: str
    message_id: Optional[int] = None

    @property
    def closed(self):
        return all(x.poll.closed for x in self.leagues)
