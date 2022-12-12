from datetime import datetime, timedelta

from babel.dates import format_date

from data_providers.poll_config_loader import PollConfigLoaderBase
from models.telegram import CombinedPoll, PollModel, League, UserModel
from models.templates import PollConfig


class PollGenerator:
    def __init__(self, poll_config_loader: PollConfigLoaderBase):
        self.poll_config_loader = poll_config_loader

    def create_combined_poll(self, chat_id: int, location_nm: str, dttm: datetime) -> CombinedPoll:
        cfg: PollConfig = self.poll_config_loader.load_template()
        if location_nm not in cfg.locations:
            raise Exception(f'Unknown location name "{location_nm}"')

        location_info = cfg.locations[location_nm]
        message = cfg.common_msg_template.format(
            date=format_date(dttm, 'd MMMM | ', locale='ru') + format_date(dttm, 'EEEE', locale='ru').capitalize(),
            time=f"{dttm.strftime('%H:%M')} до {(dttm + timedelta(hours=2)).strftime('%H:%M')}",
            location_nm=location_info.location_nm,
            location_link=location_info.location_link,
        )

        leagues = []
        for i, league in enumerate(cfg.leagues):
            leagues.append(League(
                name=f"Лига {league.league_desc.get('league_nm', f'#{i+1}')}",
                teams_cnt=league.team_cnt,
                player_per_team=league.player_per_team,
                poll=PollModel(
                    chat_id=chat_id,
                    question=cfg.poll_msg_template.format(**league.league_desc),
                    options=cfg.answer_options,
                    option_1_limit=league.team_cnt * league.player_per_team,
                ),
            ))

        result = CombinedPoll(
            event_dttm=dttm,
            chat_id=chat_id,
            common_message=message,
            leagues=leagues,
            location_nm=location_nm,
        )

        # for league in leagues:
        #     for i in range(league.poll.option_1_limit - 1):
        #         league.poll.update_answers([0], UserModel(f'player name {i}', '', f'tg_link_{i}', i))

        return result
