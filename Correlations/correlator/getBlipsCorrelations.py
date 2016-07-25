# MODULES
import time
import os
import sys
import pytz
import numpy as np
from datetime import datetime as dt
# LOCAL MODULES
projDir = os.environ.get('PROJDIR_HVANA')
sys.path.insert(0, projDir)
import HvPackages.dtOperations as DTO
import HvPackages.querySQL as QSQL
import HvPackages.myFunctions as MF
import correlator

# binWidth_list = [1,5,10,30] # seconds
binWidth_list = [1,5] # seconds
halfTimeWindow_list = [1,5,15] # minutes
# varName = 'uB_TPCDrift_HV01_keithleyPickOff/voltDiff5s60s'
varName = 'uB_TPCDrift_HV01_keithleyPickOff/getVoltage'

# SETTING VARIABLES
for binWidth in binWidth_list:
    for halfTimeWindow in halfTimeWindow_list:
        # OTHER SETTINGS
        c = correlator.Correlator()
        totalTime = 0

        # EXECUTION
        blipData = np.genfromtxt(projDir+"/Data_Events/hvEvents_0.1V.dat",delimiter=" ",names=True,dtype=None)

        for i,event in enumerate(blipData['Timestamp']):

            # EXTRACT CORRELATION
            startLoop =  time.time()
            leftTime = DTO.Timestamp2LocDatetime(event-halfTimeWindow*30).strftime("%Y-%m-%d %H:%M:%S")
            rightTime = DTO.Timestamp2LocDatetime(event+halfTimeWindow*30).strftime("%Y-%m-%d %H:%M:%S")
            corr_data = c.correlate1(varName, binWidth, leftTime, rightTime)
            endLoop = time.time()

            # TIMING OPERATIONS
            loopTime = endLoop - startLoop
            totalTime += loopTime
            aveTime = totalTime / float(i+1)
            ETA = aveTime * (len(blipData['Timestamp']) - i - 1)

            # OUTPUT
            print "%im_%is - Event %i of %i analyzed [Loop: %i s; ETA: %i minutes]" %(halfTimeWindow,binWidth,i,len(blipData['Timestamp']),loopTime,ETA/60)
            outPath = projDir+"/Data_CorrelationTables/%im_%is" %(halfTimeWindow,binWidth)
            MF.makedirp(outPath)
            np.savetxt(outPath+'/%i.dat' %(event),corr_data,delimiter=' ',fmt='%s',header='zScore Correlation BinNumber ID Name')
