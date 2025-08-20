from datetime import datetime, timedelta
import pytz
from dateutil import parser

def convert_local_to_utc(time_obj, date_obj, timezone_str):
    """
    time_obj -> datetime.time
    date_obj -> datetime.date
    timezone_str -> e.g. America/Chicago
    """
    local_tz = pytz.timezone(timezone_str)
    local_dt = datetime.combine(date_obj, time_obj)
    local_dt = local_tz.localize(local_dt)
    return local_dt.astimezone(pytz.utc)

def daterange(start, end, delta_minutes=1):
    cur = start
    while cur < end:
        yield cur
        cur += timedelta(minutes=delta_minutes)

def linear_interpolate(pings, start, end):
    """
    pings: [(timestamp_utc, status), ...] sorted
    Fill from start to end at 1 minute resolution
    """
    timeline = []
    if not pings:
        return timeline

    for i in range(len(pings) - 1):
        t1, s1 = pings[i]
        t2, s2 = pings[i+1]
        for t in daterange(max(t1, start), min(t2, end)):
            timeline.append((t, s1))  # assume until t2 same as s1

    # tail
    t_last, s_last = pings[-1]
    for t in daterange(max(t_last, start), end):
        timeline.append((t, s_last))
    return timeline
