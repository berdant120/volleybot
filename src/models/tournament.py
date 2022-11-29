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
        return '\n'.join([f'{self.name}:'] + [str(x) for x in self.players])


class Tournament:
    def __init__(self, name: str, users: List[UserModel], player_per_team: Optional[int],
            team_nms: Optional[List[str]] = None):
        self.users = users
        self.name = name
        team_nms = team_nms if team_nms else [f'Team {i}' for i in range(1, 100)]
        player_per_team = player_per_team if player_per_team else 4
        self.teams = self._create_teams(player_per_team, team_nms)
        logger.info(f'Created tournament with {len(self.teams)} teams')

    def _create_teams(self, player_per_team: int, team_nms: List[str]) -> List[Team]:
        users = self.users.copy()
        random.shuffle(users)
        # random.shuffle(self.team_nms)

        result = []
        for team_num, i in enumerate(range(0, len(users), player_per_team)):
            players = users[i: i + player_per_team]
            result.append(Team(team_nms[team_num], players))

        return result

    def __str__(self):
        return '\n\n'.join(str(x) for x in self.teams)
