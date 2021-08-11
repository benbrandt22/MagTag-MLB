from mlb.schedule.schedule_view_model import ScheduleViewModel
from adafruit_datetime import datetime, date
import time
import json
import board
import mlb.models.app_mode as AppMode
from mlb.schedule.schedule_view import ScheduleView
from mlb.scoreboard.scoreboard_view import ScoreboardView
import mlb.api as API
import alarm
from alarm_utils import pin_alarm_button, time_alarm_sec, all_button_alarms
from time_utils import utc_to_local, utc_now
from mlb.models.app_state import AppState
from mlb.message.message_view import MessageView

def start():
    print('MLB Project')

    appState = AppState()

    appState.appMode = AppMode.Schedule
    
    # Start up in Scoreboard mode if there's a live game now
    scoreboardGame = API.get_scoreboard_gamePk_and_status(appState.teamId)
    appState.scoreboardGamePk = scoreboardGame['gamePk']

    if scoreboardGame['status'] == 'Live':
        appState.appMode = AppMode.ScoreBoard

    while True:
        #----------------------------------------

        # if the device just woke up from a button, process the button press here
        if(alarm.wake_alarm is not None and type(alarm.wake_alarm) is alarm.pin.PinAlarm):
            # woken up by a button press
            
            if( alarm.wake_alarm.pin in [board.BUTTON_B, board.BUTTON_C] ):
                # B or C pressed, switch to the opposite of the previous mode
                previous_mode = alarm.sleep_memory[0]
                if(previous_mode == AppMode.Schedule):
                    appState.appMode = AppMode.ScoreBoard
                    loading_message = "Loading Scoreboard..."
                else:
                    appState.appMode = AppMode.Schedule
                    loading_message = "Loading Schedule..."
                
                MessageView(loading_message).render()
            
        
        # remember chosen mode for use in future button press wakeups
        alarm.sleep_memory[0] = appState.appMode

        #----------------------------------------
        if appState.appMode == AppMode.Schedule:

            gamePks = API.get_schedule_gamePks(appState.teamId)

            viewModel = ScheduleViewModel(
                (API.get_game_detailed_info(gamePks[0]) if gamePks[0] is not None else None),
                (API.get_game_detailed_info(gamePks[1]) if gamePks[1] is not None else None),
                (API.get_game_detailed_info(gamePks[2]) if gamePks[2] is not None else None)
            )
            view = ScheduleView(viewModel)
            view.render()

            if(viewModel.has_live_game()):
                # light sleep for 60 seconds from now to keep score updated during live game.
                alarm.light_sleep_until_alarms(time_alarm_sec(60), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C))

            else:
                # deep sleep for 1 hour, or until next game starts.
                next_game_start_utc = viewModel.get_next_game_start_utc()
                seconds_to_sleep = (2 * 3600) # 2 hours
                if next_game_start_utc is not None:
                    # there's an upcoming game
                    seconds_until_game = (next_game_start_utc - utc_now()).total_seconds()
                    if (seconds_until_game < seconds_to_sleep):
                        seconds_to_sleep = seconds_until_game

                alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(seconds_to_sleep), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C))

        #----------------------------------------
        
        if appState.appMode == AppMode.ScoreBoard:

            model = API.get_game_detailed_info(appState.scoreboardGamePk)
            view = ScoreboardView(model)
            view.render()

            if (model.status == "Live"):
                # light sleep for 60 seconds from now.
                alarm.light_sleep_until_alarms(time_alarm_sec(60), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C))
            else:
                scoreboard_retention_time_seconds = 3600
                alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(scoreboard_retention_time_seconds), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C))

        #----------------------------------------


#TODO: check at startup if woken by button press, if so show a loading screen of some sort while startup/time-sync is happening
#TODO: create a "basic game" type to hold gamePk, status, date, use in API calls at app startup
#TODO: Indicate battery level somehow. Red light when low? Icon on screen?
#TODO: Handle errors such as failed requests due to wifi/internet
#TODO: (maybe) play sound for runs?
#TODO: (maybe) only update display when model changes?