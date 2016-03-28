import ROOT
import array
import datetime
import sys

fDT = open("dataDiffTrack.dat")
fPV = open("dataPickOffVolt.dat")
fCM = open("dataCurrMon.dat")
oPV = open("shortDataPickOffVolt.dat","w")
oCM = open("shortDataCurrMon.dat","w")
fDT.readline()
fPV.readline()
fCM.readline()

# Read data
t = 0
valDT = array.array("d",[])
timeDT = array.array("d",[])
valPV = array.array("d",[])
timePV = array.array("d",[])
valCM = array.array("d",[])
timeCM = array.array("d",[])

plotValDT = array.array("d",[])
plotTimeDT = array.array("d",[])
plotValPV = array.array("d",[])
plotTimePV = array.array("d",[])
plotValCM = array.array("d",[])
plotTimeCM = array.array("d",[])

d=0
p=0
c=0

for line in fDT:
    x = line.split()
    timeDT.append(float(x[0]))
    valDT.append(float(x[1]))
    d+=1

for line in fPV:
    x = line.split()
    timePV.append(float(x[0]))
    valPV.append(float(x[1]))
    p+=1

for line in fCM:
    x = line.split()
    timeCM.append(float(x[0]))
    valCM.append(float(x[1]))
    c+=1

j = 0
for j in range(0,p):
    if timePV[j] > 1449200128:
        myline = "%i\t%f\n" %(int(timePV[j]),valPV[j])
        oPV.write(myline)
j=0
for j in range(0,c):
    if timeCM[j] > 1449200128:
        myline = "%i\t%f\n" %(int(timeCM[j]),valCM[j])
        oCM.write(myline)
