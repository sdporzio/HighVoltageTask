import pytz
import time
from pytz import timezone
from datetime import datetime as dt

CST = timezone("US/Central")
GMT = timezone("Europe/London")
EUR = timezone("Europe/Rome")

# Get string with date
def GetDateString(iTime):
    naive = dt.utcfromtimestamp(iTime)
    aware = pytz.UTC.localize(naive)
    local = aware.astimezone(CST).strftime('%d %B %y')
    return local

# Get string with time
def GetTimeString(iTime):
    naive = dt.utcfromtimestamp(iTime)
    aware = pytz.UTC.localize(naive)
    local = aware.astimezone(CST).strftime('%H:%M:%S')
    return local

# Get a unix timestamp for Chicago
def GetChicagoTimestamp(year,month,day,hour,minute,second):
    naive = dt(year,month,day,hour,minute,second)
    aware = CST.localize(naive).astimezone(pytz.utc)
    unixtime = time.mktime(aware.timetuple())
    return unixtime

# Get a unix timestamp for Chicago from dtObj
def GetChicagoTimestampDT(dtObj):
    aware = CST.localize(dtObj).astimezone(pytz.utc)
    unixtime = time.mktime(aware.timetuple())
    return int(unixtime)

# Move a datetime object (dtObj) -
# - by a certain amount (secForward) of seconds forward
# [Doesn't need to be localized because it is self-consistent]
def MoveDatetimeForward(dtObj,secForward):
    return dt.fromtimestamp(time.mktime(dtObj.timetuple()) + secForward)
