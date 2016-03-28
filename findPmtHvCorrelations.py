import ROOT
import array
from dataFunctions import GetDateString as GDS
from dataFunctions import GetTimeString as GTS

coincidenceTime = 30 # in seconds
outName1 = "Timestamps/coincidencesHvPmt_"+str(coincidenceTime)+"s.dat"
outName2 = "Timestamps/WithOrigin/originFile_CoincidencesHvPmt_"+str(coincidenceTime)+"s.dat"

fHV = open("Timestamps/hvBlips.dat")
fPMT = open("Timestamps/pmtHits.dat")
fOut1 = open(outName1,"w")
fOut2 = open(outName2,"w")
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
            fOut1.write(str(timestampPMT)+"\n")
            fOut2.write(originFilePMT[j]+" "+str(timestampPMT)+"\n")
