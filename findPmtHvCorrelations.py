import ROOT
import array
from dataFunctions import GetDateString as GDS
from dataFunctions import GetTimeString as GTS

coincidenceTime = 5 # in seconds
outName = "Timestamps/coincidencesHvPmt"+str(coincidenceTime)+"s.dat"

fHV = open("Timestamps/hvBlips.dat")
fPMT = open("Timestamps/pmtHits.dat")
outFile = open(outName,"w")
fHV.readline()
fPMT.readline()

timeHV = array.array("d",[])
timePMT = array.array("d",[])
originFilePMT = []

for line in fHV:
    x = line.split()
    timeHV.append(float(x[0]))

for line in fPMT:
    x = line.split()
    originFilePMT.append(x[0])
    timePMT.append(float(x[1]))

for i,timestampHV in enumerate(timeHV):
    for j,timestampPMT in enumerate(timePMT):
        deltaT = abs(timestampHV-timestampPMT)
        if deltaT < coincidenceTime:
            print originFilePMT[j], timestampPMT
