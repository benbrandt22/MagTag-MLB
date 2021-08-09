from connect import get_json
import secrets
import rtc
import time
from adafruit_datetime import datetime, timedelta
import time_utils


_utc_offset_seconds = None


def sync_time():
    print("Time Sync...")

    local_timezone = secrets.secrets['timezone']

    #TODO: revisit this and see if the Adafruit IO API will let us get a local and UTC time to determine offset

    time_data = get_json(f'http://worldtimeapi.org/api/timezone/{local_timezone}')

    time_utils._utc_offset_seconds = int(time_data['raw_offset']) + int(time_data['dst_offset'])

    dt = parse_iso_time( time_data['datetime'] )  # 2021-08-05T19:28:36.934217-05:00

    api_dow = int(time_data['day_of_week']) # World Time API starts week with Sunday as 0
    internal_dow = (6 if api_dow == 0 else (api_dow-1))
    day_of_year = int(time_data['day_of_year'])
    dst = (1 if time_data['dst'] else 0)

    # https://circuitpython.readthedocs.io/en/latest/shared-bindings/time/#time.struct_time
    now = time.struct_time(
        #(year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst)
        # week_day = 0(Mon)-6(Sun)
        (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, internal_dow, day_of_year, dst)
    )
    
    # set the internal clock
    rtc.RTC().datetime = now

    print(f'Synced Time: {datetime.now()}')


def local_now():
    """returns the current local time"""
    return datetime.now()


def utc_now():
    """returns the UTC time"""
    return (datetime.now() - timedelta(seconds=time_utils._utc_offset_seconds))


def utc_to_local(utc_datetime):
    return (utc_datetime + timedelta(seconds=time_utils._utc_offset_seconds))


def parse_iso_time(iso_time):
    """parses a basic 'yyyy-mm-ddThh:mm:ssZ' time"""
    year = int(iso_time[0:4])
    month = int(iso_time[5:7])
    day = int(iso_time[8:10])
    hour = int(iso_time[11:13])
    minute = int(iso_time[14:16])
    second = int(iso_time[17:19])

    dt = datetime(year, month, day, hour, minute, second)

    return dt

def month_name(dt):
    months = ['?','January','February','March','April','May','June','July','August','September','October','November','December']
    return months[dt.month]

def month_name_short(dt):
    return month_name(dt)[0:3]

def hour_12(dt):
    if dt.hour == 0:
        return 12
    if dt.hour > 12:
        return (dt.hour - 12)
    return dt.hour

def ampm(dt):
    return ('AM' if dt.hour <= 12 else 'PM')

def relative_day(dt):
    """Returns 'Yesterday'/'Today'/'Tomorrow' if the given date is one of these, otherwise None"""
    if(dt.date() == datetime.now().date()):
        return 'Today'
    if(dt.date() == (datetime.now() + timedelta(days=1)).date()):
        return 'Tomorrow'
    if(dt.date() == (datetime.now() - timedelta(days=1)).date()):
        return 'Yesterday'
    return None

def day_of_week(dt):
    """returns the day of week name for the given datetime"""
    # dt.weekday() returns 0(Monday) - 6(Sunday)
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    return days[dt.weekday()]