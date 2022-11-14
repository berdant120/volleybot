from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class UserModel:
    name: str
    link: str
    tg_id: int


@dataclass
class PollAnswerModel:
    user: UserModel


@dataclass
class PollModel:
    message_id: int
    chat_id: int
    question: str
    options: List[str]
    option_1_limit: int
    closed: bool = False
    answers: Dict[int, List[PollAnswerModel]] = field(default_factory=dict)

    def __post_init__(self):
        self.answers = {i: [] for i in range(len(self.options))}
