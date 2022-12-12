import random
from dataclasses import dataclass
from typing import List, Optional

from loguru import logger

from models.telegram import UserModel


@dataclass
class Team:
    name: str
    players: List[UserModel]

    def __str__(self) -> str:
        return '\n'.join([f'<b>{self.name}:</b>'] + [f'• {x}' for x in self.players])


class Tournament:
    def __init__(self, name: str, users: list[UserModel], player_per_team: Optional[int],
            short_name: Optional[str] = None, team_nms: Optional[list[str]] = None):
        self.short_name = short_name
        self.users = users
        self.name = name
        team_nms = team_nms if team_nms else [f'Team {i}' for i in range(1, 100)]
        player_per_team = player_per_team if player_per_team else 4
        self.teams: list[Team] = self._create_teams(player_per_team, team_nms)
        logger.info(f'Created tournament with {len(self.teams)} teams')

    def _create_teams(self, player_per_team: int, team_nms: list[str]) -> list[Team]:
        users = self.users.copy()
        random.shuffle(users)

        result = []
        for team_num, i in enumerate(range(0, len(users), player_per_team)):
            players = users[i: i + player_per_team]
            result.append(Team(team_nms[team_num].strip(), players))

        return result

    def __str__(self):
        return '\n\n'.join(str(x) for x in self.teams)
