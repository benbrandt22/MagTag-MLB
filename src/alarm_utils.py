import alarm
import time
import board
from digitalio import DigitalInOut, Direction, Pull

# shortcut functions for generating device-wakeup alarms

def time_alarm_sec(seconds: int):
    return alarm.time.TimeAlarm(epoch_time=(time.time() + seconds))

def all_button_alarms():
    """Returns a set of pin alarms that includes all buttons"""
    return [ pin_alarm_button(board.BUTTON_A), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C), pin_alarm_button(board.BUTTON_D) ]

def pin_alarm_button(button_pin):
    """Returns a pin alarm for the specified button pin. Use 'board.BUTTON_A' through 'D'"""
    return alarm.pin.PinAlarm(pin=button_pin, value=False, pull=True)
