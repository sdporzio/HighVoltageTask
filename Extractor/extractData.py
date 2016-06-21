# MODULES
import time
import os
import sys
import numpy as np
from datetime import datetime as dt
# LOCAL MODULES
projDir = os.environ.get('PROJDIR_HVANA')
sys.path.insert(0, projDir)
import HvPackages.dtOperations as DTO
import HvPackages.querySQL as QSQL

# StartTime and endTime for queries
startTime = dt(2016, 1, 1, 0, 0, 0)
endTime = dt(2016, 6, 15, 0, 0, 0)
stepSize = 24*60*60 # in seconds

# CathodeDown operations
str2DT = lambda x: DTO.GetChicagoTimestampDT(dt.strptime(x,'%Y-%m-%d %H:%M:%S'))
catDown = np.genfromtxt(projDir+"/Extractor/cathodeDown.dat",delimiter="\t",names=True,dtype=None,converters={0:str2DT,1:str2DT})
def cathodeDown(time):
    for i in range(len(catDown)):
        if catDown['Start'][i] <= time <= catDown['End'][i]:
            return True
    return False


# Variable names
varNames = np.genfromtxt(projDir+"/Extractor/channelNames.dat",names=True,dtype=None)
varPaths = []

# Loop through variables
for k,name in enumerate(varNames['VariableName']):
    data = QSQL.GetVarArrayIntervalTimestamp(name,startTime,endTime)
    print "Finished for %s (%i out of %i)" %(name,k+1,len(varNames))

    outPath = projDir+"/Extractor/Data/"+name.replace('/','_')+"_"+startTime.strftime('%y%m%d')+"_"+endTime.strftime('%y%m%d')+".dat"
    np.savetxt(outPath,np.array((data)),delimiter=' ',fmt="%s",header='Timestamp Value')
    varPaths.append(projDir+"/"+outPath)

np.savetxt(projDir+'/Extractor/Data/outList.dat',np.array(varPaths),delimiter=' ',fmt="%s",header='VariablePath')
