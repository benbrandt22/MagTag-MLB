from mlb.schedule.schedule_view_model import ScheduleViewModel
from adafruit_datetime import datetime, date
import time
import json
import mlb.models.app_mode as AppMode
from mlb.schedule.schedule_view import ScheduleView
from mlb.scoreboard.scoreboard_view import ScoreboardView
import mlb.api as API
import alarm
from alarm_utils import time_alarm_sec
from time_utils import utc_to_local, utc_now
from secrets import secrets

def start():
    print('MLB Project')

    team_id = secrets['team_id']

    app_mode = AppMode.Schedule
    # is there a live game now?
    live_gamePk = API.get_live_gamePk(team_id)
    
    if live_gamePk is not None:
        app_mode = AppMode.ScoreBoard

    while True:
        
        #----------------------------------------
        if app_mode == AppMode.Schedule:

            gamePks = API.get_schedule_gamePks(team_id)

            viewModel = ScheduleViewModel(
                (API.get_game_detailed_info(gamePks[0]) if gamePks[0] is not None else None),
                (API.get_game_detailed_info(gamePks[1]) if gamePks[1] is not None else None),
                (API.get_game_detailed_info(gamePks[2]) if gamePks[2] is not None else None)
            )
            view = ScheduleView(viewModel)
            view.render()

            if(viewModel.has_live_game()):
                # light sleep for 60 seconds from now to keep score updated during live game.
                alarm.light_sleep_until_alarms(time_alarm_sec(60))
            else:
                # deep sleep for 1 hour, or until next game starts.
                next_game_start_utc = viewModel.get_next_game_start_utc()
                seconds_to_sleep = 3600
                if next_game_start_utc is not None:
                    # there's an upcoming game
                    seconds_until_game = (next_game_start_utc - utc_now()).total_seconds()
                    if (seconds_until_game < seconds_to_sleep):
                        seconds_to_sleep = seconds_until_game

                alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(seconds_to_sleep))

        #----------------------------------------
        
        if app_mode == AppMode.ScoreBoard:

            model = API.get_game_detailed_info(live_gamePk)
            view = ScoreboardView(model)
            view.render()

            if (model.status == "Live"):
                # light sleep for 60 seconds from now.
                alarm.light_sleep_until_alarms(time_alarm_sec(60))
            else:
                scoreboard_retention_time_seconds = 3600
                alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(scoreboard_retention_time_seconds))

        #----------------------------------------
        


#TODO: Add light and deep sleep where appropriate
#TODO: Indicate battery level somehow. Red light when low? Icon on screen?
#TODO: Handle errors such as failed requests due to wifi/internet
#TODO: app mode switching via buttons
#TODO: (maybe) play sound for runs?
#TODO: (maybe) only update display when model changes?