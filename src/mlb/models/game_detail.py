class InningDetail:
    def __init__(self, num, awayRuns, homeRuns):
        self.num = num
        self.awayRuns = awayRuns
        self.homeRuns = homeRuns

    num = ''
    awayRuns = None
    homeRuns = None

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
        self.abstractGameState = ''
        self.detailedState = ''
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
        return self.abstractGameState == 'Final'

    @property
    def isLive(self):
        """Returns true if the game is currently being played"""
        return self.abstractGameState == 'Live'

    @property
    def isPreview(self):
        """Returns true if the game has not started yet"""
        return self.abstractGameState == 'Preview'

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

    @property
    def isPostponed(self):
        """Returns true if the game was postponed"""
        return self.detailedState.startswith('Postponed')

    @property
    def isDelayed(self):
        """Returns true if the game was delayed"""
        return self.detailedState.startswith('Delayed')

    @property
    def isCancelled(self):
        """Returns true if the game was cancelled"""
        return self.detailedState.startswith('Cancelled')

    @property
    def isStatusExceptional(self):
        """Returns true if the game has an out-of-the-ordinary status that should be displayed"""
        if self.isPreview and self.detailedState == 'Scheduled':
            return False

        if self.isLive and self.detailedState == 'In Progress':
            return False

        if self.isFinal and self.detailedState == 'Final':
            return False
        
        return True