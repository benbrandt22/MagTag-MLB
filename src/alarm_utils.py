import alarm
import time
import board
from adafruit_datetime import datetime

# shortcut functions for generating device-wakeup alarms

def time_alarm_sec(seconds: int):
    current_timestamp = int(time.time())
    wakeup_timestamp = current_timestamp + seconds
    print(f'Setting sleep alarm for {seconds} sec [Current: {datetime.fromtimestamp(current_timestamp)}] [Wakeup: {datetime.fromtimestamp(wakeup_timestamp)}]')
    return alarm.time.TimeAlarm(epoch_time=wakeup_timestamp)

def all_button_alarms():
    """Returns a set of pin alarms that includes all buttons"""
    return [ pin_alarm_button(board.BUTTON_A), pin_alarm_button(board.BUTTON_B), pin_alarm_button(board.BUTTON_C), pin_alarm_button(board.BUTTON_D) ]

def pin_alarm_button(button_pin):
    """Returns a pin alarm for the specified button pin. Use 'board.BUTTON_A' through 'D'"""
    return alarm.pin.PinAlarm(pin=button_pin, value=False, pull=True)

def was_woken_by_pin(button_pin):
    """Returns true if the device was woken by the specified pin"""
    return ( alarm.wake_alarm is not None \
        and type(alarm.wake_alarm) is alarm.pin.PinAlarm \
        and alarm.wake_alarm.pin == button_pin )

def was_woken_by_time():
    """Returns true if the device was woken by a TimeAlarm"""
    return ( alarm.wake_alarm is not None and type(alarm.wake_alarm) is alarm.time.TimeAlarm )

def was_woken_by_powerup():
    """Returns true if the device was turned on, and not woken by any alarm"""
    return ( alarm.wake_alarm is None )

def clear_wake_alarm():
    """Clears out the reason why the device was last woken"""
    alarm.wake_alarm = None