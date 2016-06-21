import ROOT
import array
import math
import pytz
import time
from pytz import timezone
from datetime import datetime as dt

# Determine if datapoint signal an interesting event
def DetIfInteresting(val,heightDev,blipSign,bInteresting):
    if val > heightDev:
        blipSign = 1
        bInteresting = True
    elif val < -heightDev:
        blipSign = -1
        bInteresting = True
    else:
        bInteresting = False
    return blipSign, bInteresting


# Find feet of the peak given an interesting point (for DT data)
def FindDTFeet(sign,val,point0):
    i = 1
    j = 1
    while sign*val[point0-i]>nullSensitivity:
        i+=1
    leftFoot = point0-i+1
    while sign*val[point0+j]>nullSensitivity:
        j+=1
    rightFoot = point0+j-1
    return leftFoot, rightFoot


# Find extremum between two datapoints
def FindExtremum(sign,val,pointL,pointR):
    extremum = pointL
    for m in range(pointL,pointR):
        if sign*val[m] > sign*val[extremum]:
            extremum = m
    return extremum


# Find datapoint = 0 which separates positive and negative peaks
def FindZeroPoint(sign,val,point0):
    m = 1
    while True:
        if sign*val[point0+m]>0:
            m+=1
        else:
            zeroPoint = point0+m
            break
    return zeroPoint


# Run all DT related functions given interesting point
def FindDTKeyPoints(blipSign,val,i):
    point0 = i
    pointL1,pointR1 = FindDTFeet(blipSign,val,point0)
    pointC1 = FindExtremum(blipSign,val,pointL1,pointR1)
    pointL2zero = FindZeroPoint(blipSign,val,point0)
    pointR2zero = FindZeroPoint(-blipSign,val,pointL2zero)
    pointC2 = FindExtremum(-blipSign,val,pointL2zero,pointR2zero)
    pointL2, pointR2 = FindDTFeet(-blipSign,val,pointC2)
    return point0,pointL1,pointC1,pointR1,pointL2zero,pointR2zero,pointL2,pointR2,pointC2


# Calculate the integral of the DT high and low peaks
def DetDTIntegral(val,time,pointL1,pointR1,pointL2,pointR2):
    integral1 = 0
    integral2 = 0
    for i in range(pointL1,pointR1):
        integral1 += (time[i+1]-time[i])*(val[i]+val[i+1])/2.
    for i in range(pointL2,pointR2):
        integral2 += (time[i+1]-time[i])*(val[i]+val[i+1])/2.
    intRatio = 0
    if integral2 != 0:
        intRatio = abs(integral1/integral2)
    return integral1,integral2,intRatio


# Determine left and right averages
def DetLeftRightAverages(aveVal,time,val,pointL,pointR):
    i = 0
    j = 0
    aveL = 0
    aveR = 0
    while abs(time[pointL-i] - time[pointL]) < aveVal:
        i+=1
        aveL+=val[pointL-i]
    while abs(time[pointR+j] - time[pointR]) < aveVal:
        j+=1
        aveR+=val[pointR+j]
    pointLA = pointL-i
    pointRA = pointR+j
    aveL/=i
    aveR/=j
    return pointLA,pointRA,aveL,aveR


# Determine left and right standard deviations around left and right averages
def DetLeftRightStandardDeviations(aveVal,time,val,pointL,pointR,pointLA,pointRA,aveL,aveR):
    sdL = 0
    sdR = 0
    nL = abs(pointLA - pointL)
    nR = abs(pointRA - pointR)
    for i in range(pointLA,pointL):
        sdL += (aveL - val[i])**2
    for j in range(pointR,pointRA):
        sdR += (aveR - val[i])**2
    sdL = sdL/nL
    sdR = sdR/nR
    return math.sqrt(sdL),math.sqrt(sdR)


# Find feet of the peak given a point of it (for PV)
def FindPVFeet(val,sign,pointC,aveR,aveL):
    i = 0
    j = 0
    while sign*val[pointC-j] > sign*aveL:
        j+=1
    while sign*val[pointC+i] > sign*aveR:
        i+=1
    pointL1 = pointC-j
    pointR1 = pointC+i
    return pointL1,pointR1

# Calculate the width of the PV peak
def DetPVPeakWidth(val,time,sign,pointC,pointL,pointR):
    baseline = (val[pointL]+val[pointR])/2.
    halfmax = (val[pointC]+baseline)/2.
    i = 0
    j = 0
    while sign*val[pointC-j] > sign*halfmax:
        j+=1
    while sign*val[pointC+i] > sign*halfmax:
        i+=1
    fwhmPointL = pointC-j
    fwhmPointR = pointC+i
    fwhm = time[fwhmPointR]-time[fwhmPointL]
    return fwhm,fwhmPointL,fwhmPointR


# Date and Time stuff
CST = timezone("US/Central")
GMT = timezone("Europe/London")
EUR = timezone("Europe/Rome")
nullSensitivity = 0.005 # Where to find the "feet" of the peak (0 finds them on the 0 axis)

# Get string with date
def GetDateString(iTime):
    # year = ROOT.TDatime(int(iTime)).GetYear()
    # month = datetime.date(1900, ROOT.TDatime(int(iTime)).GetMonth(),1).strftime('%B')
    # day = ROOT.TDatime(int(iTime)).GetDay()
    naive = dt.utcfromtimestamp(iTime)
    aware = pytz.UTC.localize(naive)
    local = aware.astimezone(CST).strftime('%d %B %y')
    return local


# Get string with time
def GetTimeString(iTime):
    # hour = ROOT.TDatime(int(iTime)).GetHour()
    # minute = ROOT.TDatime(int(iTime)).GetMinute()
    # second = ROOT.TDatime(int(iTime)).GetSecond()
    # sTime = "%i:%i:%i" %(hour,minute,second)
    naive = dt.utcfromtimestamp(iTime)
    aware = pytz.UTC.localize(naive)
    local = aware.astimezone(CST).strftime('%H:%M:%S')
    return local

def GetChicagoTimestamp(year,month,day,hour,minute,second):
    naive = dt(year,month,day,hour,minute,second)
    aware = CST.localize(naive).astimezone(pytz.utc)
    unixtime = time.mktime(aware.timetuple())
    return unixtime
