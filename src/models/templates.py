from typing import List, Dict

from pydantic import BaseModel, validator


class TournamentLocation(BaseModel):
    location_nm: str
    location_link: str


class LeagueConfig(BaseModel):
    team_cnt: int
    player_per_team: int
    league_desc: Dict[str, str]


class PollConfig(BaseModel):
    common_msg_template: str
    poll_msg_template: str
    answer_options: List[str]
    locations: Dict[str, TournamentLocation]
    leagues: List[LeagueConfig]

    @validator('common_msg_template')
    def validate_template_params(cls, v):
        if '{time}' not in v or '{date}' not in v:
            raise ValueError('Poll message template doesnt contain date/time parameters')

        if '{location_nm}' not in v or '{location_link}' not in v:
            raise ValueError('Poll message template doesnt contain location parameters')

        return v
