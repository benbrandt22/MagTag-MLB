from adafruit_datetime import datetime, date, timedelta
from time_utils import utc_now, parse_iso_time, utc_to_local
from connect import get_json
from mlb.models.game_basic import GameBasic
from mlb.models.game_detail import GameDetail, InningDetail


def _get_item_at_index(list, index):
    """Returns the item if it exists, otherwise returns None"""
    if len(list) == 0:
        return None
    if index >= 0 and index < len(list):
        return list[index]
    return None

def get_schedule_gamePks(teamId):
    # returns three gamePks for display on the schedule view
    start_date = (utc_now() - timedelta(days=7)).date()
    end_date = (utc_now() + timedelta(days=7)).date()
    scheduledata = get_json(f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={teamId}&startDate={start_date}&endDate={end_date}&fields=dates,games,gamePk,gameDate,status,abstractGameState')
    games = []
    #(assuming games are provided in chronological order)
    for d in scheduledata['dates']:
        for g in d['games']:
            games.append( (g['gamePk'], g['gameDate'], g['status']['abstractGameState']) )
    # find last "Final" game in list
    last_finalgame_index = -1
    for i in range(len(games)-1, -1, -1):
        if games[i][2] == 'Final':
            last_finalgame_index = i
            break
    # now get this one and the next two games
    gamePks = []
    for i in range(3):
        g = _get_item_at_index(games, (last_finalgame_index + i) )
        gamePk = g[0] if g is not None else None
        gamePks.append(gamePk)
    return gamePks

def get_live_gamePk(teamId):
    """If the specified team has a Live game now, returns the gamePk for that game, otherwise None"""
    start_date = (utc_now() - timedelta(days=1)).date()
    end_date = (utc_now() + timedelta(days=1)).date()
    scheduledata = get_json(f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={teamId}&startDate={start_date}&endDate={end_date}&fields=dates,games,gamePk,gameDate,status,abstractGameState')
    games = []
    #(assuming games are provided in chronological order)
    for d in scheduledata['dates']:
        for g in d['games']:
            games.append( (g['gamePk'], g['gameDate'], g['status']['abstractGameState']) )
    for g in games:
        if g[2] == "Live":
            return g[0]
    return None

def get_game_detailed_info(gamePk):
    fields = ['gameData','datetime','dateTime','officialDate','time','ampm','status','abstractGameState',
        'teams','away','home','clubName','abbreviation','liveData','linescore','inningHalf','currentInning',
        'currentInningOrdinal','runs','innings','num','hits','errors','plays','currentPlay','count','balls',
        'strikes','outs','matchup','postOnFirst','postOnSecond','postOnThird','scheduledInnings']
    data = get_json(f'https://statsapi.mlb.com/api/v1.1/game/{gamePk}/feed/live?fields={",".join(fields)}')
    gameData = data['gameData']
    liveData = data['liveData']

    model = GameDetail()
    model.date = gameData['datetime']['officialDate']
    model.localTime = f"{gameData['datetime']['time']} {gameData['datetime']['ampm']}"
    model.dateTimeUtc = parse_iso_time( gameData['datetime']['dateTime'] )
    model.status = gameData['status']['abstractGameState']
    model.away.teamName = gameData['teams']['away']['clubName']
    model.home.teamName = gameData['teams']['home']['clubName']
    model.away.teamAbbreviation = gameData['teams']['away']['abbreviation']
    model.home.teamAbbreviation = gameData['teams']['home']['abbreviation']
    model.scheduledInnings = int(liveData['linescore']['scheduledInnings'] or 9)
    if model.status == "Live":
        model.inningHalf = liveData['linescore']['inningHalf']
        model.currentInning = liveData['linescore']['currentInning']
        model.currentInningOrdinal = liveData['linescore']['currentInningOrdinal']
    if model.status == "Live" or model.status == "Final":
        model.away.runs = liveData['linescore']['teams']['away']['runs']
        model.away.hits = liveData['linescore']['teams']['away']['hits']
        model.away.errors = liveData['linescore']['teams']['away']['errors']
        model.home.runs = liveData['linescore']['teams']['home']['runs']
        model.home.hits = liveData['linescore']['teams']['home']['hits']
        model.home.errors = liveData['linescore']['teams']['home']['errors']
        
    if model.status == "Live" or model.status == "Final":
        for i in liveData['linescore']['innings']:
            num = i['num']
            awayRuns = i['away']['runs'] if 'runs' in i['away'] else ''
            homeRuns = i['home']['runs'] if 'runs' in i['home'] else ''
            model.innings.append( InningDetail(num, awayRuns, homeRuns) )

    if model.status == "Live":
        # get current play info
        current_play = liveData['plays']['currentPlay']
        model.balls = current_play['count']['balls']
        model.strikes = current_play['count']['strikes']
        model.outs = current_play['count']['outs']
        model.postOnFirst = ('postOnFirst' in current_play['matchup'])
        model.postOnSecond = ('postOnSecond' in current_play['matchup'])
        model.postOnThird = ('postOnThird' in current_play['matchup'])

    return model