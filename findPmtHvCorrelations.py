import ROOT
import array
from dataFunctions import GetDateString as GDS
from dataFunctions import GetTimeString as GTS


coincidenceTime = 30 # in seconds
for cutY in range(-210,-100, 10):
    outName = "Timestamps/coincidencesHvPmt_"+str(coincidenceTime)+"s_Cut"+str(cutY)+".dat"

    fHV = open("Timestamps/hvBlips.dat")
    fPMT = open("TorScopeMon/Timestamps/pmtHits_cutMinY"+str(cutY)+".dat")
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

    for i,timestampHV in enumerate(timeHV):
        for j,timestampPMT in enumerate(timePMT):
            deltaT = timestampPMT-timestampHV
            if abs(deltaT) < coincidenceTime:
                outString = originFilePMT[j]+" "+str(timestampPMT)+" "+ \
                str(timestampHV)+" "+blipType[i]+" "+str(blipIntensity[i])+" "+ \
                str(blipDuration[i])+" "+str(deltaT)+"\n"
                fOut.write(outString)
