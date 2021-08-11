import mlb.models.app_mode as AppMode
from secrets import secrets

class AppState:
    def __init__(self):
        self.appMode = AppMode.Schedule
        self.teamId = secrets['team_id']
        self.scoreboardGamePk = None
