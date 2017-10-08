from django.utils import timezone
from datetime import datetime

def parse_datetime(date, time):
    date = datetime.strptime(date, "%Y-%m-%d")
    time = datetime.strptime(time, "%H:%M:%S")
    ans = datetime(year=date.year, month=date.month, day=date.day, hour=time.hour, minute=time.minute, second=time.second)
    return ans