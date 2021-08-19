class InningDetail:
    def __init__(self, num, awayRuns, homeRuns):
        self.num = num
        self.awayRuns = awayRuns
        self.homeRuns = homeRuns

    num = ''
    awayRuns = ''
    homeRuns = ''

class GameTeamDetail:
    def __init__(self):
        self.teamName = ''
        self.teamAbbreviation = ''
        self.runs = ''
        self.hits = ''
        self.errors = ''

class GameDetail:
    def __init__(self):
        self.home = GameTeamDetail()
        self.away = GameTeamDetail()
        self.date = ''
        self.localTime = ''
        self.dateTimeUtc = ''
        self.status = ''
        self.scheduledInnings = 9
        self.inningHalf = ''
        self.currentInning = ''
        self.currentInningOrdinal = ''
        self.innings = []
        self.balls = ''
        self.strikes = ''
        self.outs = ''
        self.postOnFirst = False
        self.postOnSecond = False
        self.postOnThird = False

    @property
    def isFinal(self):
        """Returns true if the game has finished"""
        return self.status == 'Final'

    @property
    def isLive(self):
        """Returns true if the game is currently being played"""
        return self.status == 'Live'

    @property
    def isPreview(self):
        """Returns true if the game has not started yet"""
        return self.status == 'Preview'

    @property
    def isInningTop(self):
        """Returns true if the game is Live and is in the Top half of the inning"""
        return (self.isLive and self.inningHalf == 'Top')

    @property
    def isInningBottom(self):
        """Returns true if the game is Live and is in the Bottom half of the inning"""
        return (self.isLive and self.inningHalf == 'Bottom')

    @property
    def inningCount(self):
        """Returns the number of innings played (including partial or in-progress)"""
        return len(self.innings)

    @property
    def isExtraInnings(self):
        """Returns true if the game went into extra innings"""
        return (self.inningCount > self.scheduledInnings)