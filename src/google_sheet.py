from datetime import datetime, timezone, timedelta
from typing import Optional

import pygsheets
from loguru import logger
from pygsheets import Spreadsheet, Worksheet
from pygsheets.client import Client

from config import DEFAULT_SPR_ID, TEAMS_TEMPLATE_ID, TOURNAMENT_TEMPLATE_ID, GRANT_SPR_PERMISSION
from models.telegram import CombinedPoll
from models.tournament import Tournament


class GoogleSheetExporter:
    def __init__(self, client_secret_path: str = 'client_secret.json', creds_dir: str = ''):
        self.client: Client = pygsheets.authorize(client_secret_path, credentials_directory=creds_dir)
        self.default_spr = self._get_spreadsheet(DEFAULT_SPR_ID)

    def _get_spreadsheet(self, sheet_id: str) -> Spreadsheet:
        spr_json = self.client.sheet.get(sheet_id)
        return Spreadsheet(self.client, spr_json)

    def _create_spreadsheet(self, name: str, template_id: str) -> Spreadsheet:
        template = self.client.sheet.get(template_id)
        spr = self.client.create(name, template)
        return spr

    @staticmethod
    def _add_worksheet(ws_name: str, spreadsheet: Spreadsheet, template_id: str) -> Worksheet:
        ws = spreadsheet.add_worksheet(ws_name, src_tuple=(template_id, 0))
        return ws

    def export_tournament(self, tournament: Tournament, spreadsheet: Optional[Spreadsheet] = None):
        dttm_now = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(tz=timezone(timedelta(hours=8)))
        ws_name = tournament.short_name or dttm_now.strftime("%d.%m.%Y %H:%M")
        spr = spreadsheet or self.default_spr
        ws = self._add_worksheet(ws_name, spr, TEAMS_TEMPLATE_ID)

        ws.update_value('A1', tournament.name)
        start_cells = [(col, row) for col in ('C', 'E', 'G', 'I') for row in (3, 9)]
        team_ranges = {}
        for i, team in enumerate(tournament.teams):
            col, row = start_cells[i]
            values = [[team.name]] + [[str(x)] for x in team.players]
            crange = f'{col}{row}:{col}{row + len(values) - 1}'
            ws.update_values(crange, values)
            team_ranges[team.name] = crange

        return ws, team_ranges

    def export_combined_tournament(self, combined_poll: CombinedPoll, tournaments: list[Tournament]):
        spr = self._create_spreadsheet(
            template_id=TOURNAMENT_TEMPLATE_ID,
            name=f'{combined_poll.location_nm} {combined_poll.event_dttm.strftime("%d.%m.%Y %H:%M")}',
        )

        main_ws = spr.worksheet()
        start_rows = (4, 11, 18)
        start_row_index = 0
        for tournament in tournaments:
            ws, team_ranges = self.export_tournament(tournament, spr)
            team_links = [[f'=HYPERLINK("#gid={ws.id}&range={team_ranges[x.name]}"; "{x.name}")'] for x in tournament.teams]
            for i in range(0, len(team_links), 4):
                crange = f'C{start_rows[start_row_index]}:C{start_rows[start_row_index] + 3}'
                main_ws.update_values(crange, team_links[i:i+4])
                start_row_index += 1

        for email in GRANT_SPR_PERMISSION:
            self.client.drive.create_permission(spr.id, 'writer', 'user', emailAddress=email)

        logger.info(f'Tournament table has been generated {spr.url}')
        return spr
