import os.path
import random
from loguru import logger
from typing import Optional

from telegram import ParseMode
from telegram.ext import CallbackContext

from google_sheet import GoogleSheetExporter
from models.telegram import PollModel, CombinedPoll
from models.tournament import Tournament
from tg_bot.parse_utils import parse_player_amount


class TelegramUpdateHandler:
    def __init__(self, google_sheet_exporter: GoogleSheetExporter):
        self.google_sheet_exporter = google_sheet_exporter

    @staticmethod
    def create_tg_poll(poll_model: PollModel, context: CallbackContext, combined_poll_message_id: Optional[int] = None):
        message = context.bot.send_poll(
            chat_id=poll_model.chat_id,
            question=poll_model.question,
            options=[x.text for x in poll_model.answers],
            allows_multiple_answers=False,
            is_anonymous=False,
            is_closed=False,
        )

        poll_model.message_id = message.message_id
        poll_model.combined_poll_message_id = combined_poll_message_id
        context.bot_data[message.poll.id] = poll_model
        logger.info(f'Created poll {message.poll.id}:{poll_model}')

        return message.poll.id

    def on_single_poll_closed(self, poll_model: PollModel, context: CallbackContext):
        context.bot.send_message(
            poll_model.chat_id,
            f'Poll is finished. {poll_model.formatted_answer_voters(0, True)}',
            reply_to_message_id=poll_model.message_id,
            parse_mode=ParseMode.HTML,
        )

        player_per_team = parse_player_amount(poll_model.question)
        tournament = Tournament(poll_model.question, poll_model.answers[0].users(), player_per_team=player_per_team)
        context.bot.send_message(poll_model.chat_id, str(tournament))

        ws, _ = self.google_sheet_exporter.export_tournament(tournament)
        context.bot.send_message(poll_model.chat_id, f'Created table link: {ws.url}')

        # del context.bot_data[poll_id]

    def on_combined_poll_closed(self, combined_poll: CombinedPoll, context: CallbackContext):
        league_team_nms = self._load_team_names(len(combined_poll.leagues))
        tournaments = [Tournament(
            name=league.poll.question,
            users=league.poll.answers[0].users(),
            player_per_team=league.player_per_team,
            short_name=league.name,
            team_nms=team_nms,
        ) for league, team_nms in zip(combined_poll.leagues, league_team_nms)]

        message = '\n'.join([f'==== {t.short_name.upper()} ====\n{t}\n' for t in tournaments])
        context.bot.send_message(combined_poll.chat_id, message, reply_to_message_id=combined_poll.message_id,
            parse_mode=ParseMode.HTML)
        context.bot_data['tournaments'][combined_poll.message_id] = tournaments

        table_link = self.google_sheet_exporter.export_combined_tournament(combined_poll, tournaments).url
        context.bot.send_message(combined_poll.chat_id, f'Created table link: {table_link}')

    @staticmethod
    def _load_team_names(league_cnt: int) -> list[Optional[list[str]]]:
        file_path = 'data/team_names.txt'
        if not os.path.exists(file_path):
            return [None] * league_cnt

        with open(file_path, 'r') as f:
            team_nms = f.readlines()

        random.shuffle(team_nms)
        list_size = len(team_nms) // league_cnt + 1
        return [team_nms[i:i + list_size] for i in range(0, len(team_nms), list_size)]
