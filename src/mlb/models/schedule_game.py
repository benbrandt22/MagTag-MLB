class ScheduleGame:
    """A minimal class used to hold some basic data from the schedule API"""

    def __init__(self, gamePk, gameDate, abstractGameState):
        self.gamePk = gamePk
        self.gameDate = gameDate
        self.abstractGameState = abstractGameState

    gamePk = ''
    gameDate = ''
    abstractGameState = ''