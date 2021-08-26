from mlb.schedule.schedule_view_model import ScheduleViewModel
from adafruit_datetime import datetime, timedelta
import time
import json
import board
import mlb.models.app_mode as AppMode
from mlb.schedule.schedule_view import ScheduleView
from mlb.scoreboard.scoreboard_view import ScoreboardView
import mlb.api as API
import alarm
from alarm_utils import pin_alarm_button, time_alarm_sec, was_woken_by_pin, was_woken_by_time, was_woken_by_powerup
from time_utils import local_now, utc_to_local, utc_now
from mlb.models.app_state import AppState
from mlb.message.message_view import MessageView
from time_utils import sync_time

def start():

    if( was_woken_by_time() ):
        # just woke up from deep sleep after a time alarm, don't show a splash screen, just let it update when the data is ready
        pass
    else:
        # starting up from the power switch or a pin alarm, show a splash screen to indicate it's working
        MessageView("Loading...").render()

    # set the clock from an online source
    try:
        sync_time()
    except Exception as ex:
        MessageView(f"Time Synchronization failed,\nunable to launch.\nRetrying in 1 minute...\n\n({repr(ex)})").render()
        alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(60))

    appState = AppState()
    appState.appMode = AppMode.Schedule
    
    # Start up in Scoreboard mode if there's a live game now
    try:
        scoreboardGame = API.get_scoreboard_gamePk_and_status(appState.teamId)
        appState.scoreboardGamePk = scoreboardGame['gamePk']
    except Exception as ex:
        MessageView(f"Unable to load game data,\nretrying in 1 minute...\n\n({repr(ex)})").render()
        alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(60))

    if scoreboardGame['status'] == 'Live':
        appState.appMode = AppMode.ScoreBoard


    while True:
        #----------------------------------------

        # if the device just woke up from a button, process the button press here    
        if( was_woken_by_pin(board.BUTTON_B) or was_woken_by_pin(board.BUTTON_C) ):
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

            tries = 5
            for n in range(tries):
                try:
                    gamePks = API.get_schedule_gamePks(appState.teamId)

                    viewModel = ScheduleViewModel(
                        (API.get_game_detailed_info(gamePks[0]) if gamePks[0] is not None else None),
                        (API.get_game_detailed_info(gamePks[1]) if gamePks[1] is not None else None),
                        (API.get_game_detailed_info(gamePks[2]) if gamePks[2] is not None else None)
                    )
                    break
                except Exception as ex:
                    if n < (tries - 1):
                        print(f"failed to load schedule data, retrying...")
                        time.sleep(5)
                    else:
                        # failed all retries
                        MessageView(f"Unable to load schedule data,\nrestarting in 1 minute...\n\n({repr(ex)})").render()
                        alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(60))

            view = ScheduleView(viewModel)
            view.render()

            if(viewModel.has_live_game()):
                # light sleep for 90 seconds from now to keep score updated during live game.
                alarm.light_sleep_until_alarms(time_alarm_sec(90), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C))
            if(viewModel.has_delayed_game()):
                alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(300), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C))

            else:
                # deep sleep until tomorrow morning, or until next game starts.
                tomorrow = (local_now() + timedelta(days=1)).date()
                next_midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
                seconds_to_sleep = ((next_midnight - local_now()).total_seconds() + 60) # (sleep until slightly past midnight, then the "day" labels can update)
                print(f'Seconds until midnight = {seconds_to_sleep}')
                
                next_game_start_utc = viewModel.get_next_game_start_utc()
                if next_game_start_utc is not None:
                    # there's an upcoming game
                    seconds_until_game = (next_game_start_utc - utc_now()).total_seconds()
                    print(f'Seconds until game = {seconds_until_game}')
                    if (seconds_until_game < seconds_to_sleep):
                        seconds_to_sleep = seconds_until_game

                print(f'Deep sleeping for {seconds_to_sleep} seconds...')
                alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(seconds_to_sleep), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C))

        #----------------------------------------
        
        if appState.appMode == AppMode.ScoreBoard:
            tries = 5
            for n in range(tries):
                try:
                    model = API.get_game_detailed_info(appState.scoreboardGamePk)
                    break
                except Exception as ex:
                    if n < (tries - 1):
                        print(f"failed to load scoreboard data, retrying...")
                        time.sleep(5)
                    else:
                        # failed all retries
                        MessageView(f"Unable to load game data,\nrestarting in 1 minute...\n\n({repr(ex)})").render()
                        alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(60))


            view = ScoreboardView(model)
            view.render()

            if (model.isLive):
                alarm.light_sleep_until_alarms(time_alarm_sec(90), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C))
            if (model.isDelayed):
                alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(300), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C))
            else:
                scoreboard_retention_time_seconds = 3600
                alarm.exit_and_deep_sleep_until_alarms(time_alarm_sec(scoreboard_retention_time_seconds), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C))

        #----------------------------------------