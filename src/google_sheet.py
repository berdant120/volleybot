from datetime import datetime, timezone, timedelta

import pygsheets
from pygsheets import Spreadsheet, Worksheet
from pygsheets.client import Client

from config import DEFAULT_SPR_ID, TEMPLATE_ID
from models.tournament import Tournament


class GoogleSheetExporter:
    def __init__(self, client_secret_path: str = 'client_secret.json', creds_dir: str = ''):
        self.client: Client = pygsheets.authorize(client_secret_path, credentials_directory=creds_dir)
        self.default_spr = self._get_spreadsheet(DEFAULT_SPR_ID)

    def _get_spreadsheet(self, sheet_id: str) -> Spreadsheet:
        spr_json = self.client.sheet.get(sheet_id)
        return Spreadsheet(self.client, spr_json)

    def _create_spreadsheet(self, name, template_id) -> Spreadsheet:
        template = self.client.sheet.get(template_id)
        sp = self.client.create(name, template)
        return sp

    def _add_worksheet(self, ws_name: str) -> Worksheet:
        ws = self.default_spr.add_worksheet(ws_name, src_tuple=(TEMPLATE_ID, 0))
        return ws

    def export_tournament(self, tournament: Tournament):
        dttm_now = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(tz=timezone(timedelta(hours=8)))
        dttm_str = dttm_now.strftime("%d.%m.%Y %H:%M")
        ws = self._add_worksheet(dttm_str)

        ws.update_value('A1', tournament.name)
        start_cells = [(col, row) for col in ('C', 'E', 'G', 'I') for row in (3, 9)]
        for i, team in enumerate(tournament.teams):
            col, row = start_cells[i]
            values = [[team.name]] + [[str(x)] for x in team.players]
            crange = f'{col}{row}:{col}{row + len(values) - 1}'
            ws.update_values(crange, values)

        return ws.url
