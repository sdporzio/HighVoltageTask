import ROOT
import array

coincidenceTime = 30 # in seconds
outName = "Timestamps/coincidencesHvPmt_"+str(coincidenceTime)+"s.dat"

fHV = open("Timestamps/hvBlips.dat")
fPMT = open("Timestamps/pmtHits.dat")
fOut = open(outName,"w")
fHV.readline()
fPMT.readline()

timeHV = array.array("d",[])
blipType = []
blipDuration = array.array("d",[])
blipIntensity = array.array("d",[])
originFilePMT = []
timePMT = array.array("d",[])

for line in fHV:
    x = line.split()
    timeHV.append(float(x[0]))
    blipType.append(x[1])
    blipIntensity.append(float(x[5]))
    blipDuration.append(float(x[6]))

for line in fPMT:
    x = line.split()
    originFilePMT.append(x[0])
    timePMT.append(float(x[1]))
