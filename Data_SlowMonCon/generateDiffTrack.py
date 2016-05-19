import ROOT
import array
import datetime
import sys

fPV = open("pickOffVoltage.dat")
fDT = open("differenceTracker.dat","w")
fPV.readline()

# Read data from files
t = 0
valDT = array.array("d",[])
timeDT = array.array("d",[])
valPV = array.array("d",[])
timePV = array.array("d",[])

for line in fPV:
    x = line.split()
    timePV.append(float(x[0]))
    valPV.append(float(x[1]))
    t+=1

for i in range(60,t):
    j = 0
    k = 0
    fiveSecAve = 0
    sixtySecAve = 0

    while timePV[i]-timePV[i-j]<5:
        fiveSecAve += valPV[i-j]
        j+=1
    while timePV[i]-timePV[i-k]<60:
        sixtySecAve += valPV[i-k]
        k+=1
    fiveSecAve = fiveSecAve/(j)
    sixtySecAve = sixtySecAve/(k)
    DiffTrack = fiveSecAve - sixtySecAve

    #timeDT.append(timePV[i])
    #valDT.append(DiffTrack)
    outputline = "%i %f\n" %(timePV[i],DiffTrack)
    fDT.write(outputline)
    # print DiffTrack
