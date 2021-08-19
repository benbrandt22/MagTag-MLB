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
        return self.status == 'Final'

    @property
    def isLive(self):
        return self.status == 'Live'

    @property
    def isPreview(self):
        return self.status == 'Preview'