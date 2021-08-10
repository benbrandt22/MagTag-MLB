import alarm
import time

# shortcut functions for generating device-wakeup alarms


def time_alarm_sec(seconds: int):
    return alarm.time.TimeAlarm(epoch_time=(time.time() + seconds))