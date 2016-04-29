import ROOT
import array
import sys
sys.path.insert(0, '/Users/sdporzio/HighVoltageTask')
from HvPackages.dataFunctions import GetDateString as GDS
from HvPackages.dataFunctions import GetTimeString as GTS
ROOT.gROOT.SetBatch(1)
histo = ROOT.TH1D("histo","Coincidences vs. minY cut",25,-200,50)

coincidenceTime = 30 # in seconds

for cutY in range(-210,50,10):
    outName = "Timestamps/Coincidences/coincidencesHvPmt_"+str(coincidenceTime)+"s_Cut"+str(cutY)+".dat"

    fHV = open("Timestamps/hvBlips.dat")
    fPMT = open("TorScopeMon/Timestamps/pmtHits_cutMinY"+str(cutY)+".dat")
    fOut = open(outName,"w")
    lHV = fHV.readlines()
    lPMT = fPMT.readlines()

    timeHV = array.array("d",[])
    blipType = []
    blipDuration = array.array("d",[])
    blipIntensity = array.array("d",[])
    originFilePMT = []
    timePMT = array.array("d",[])

    i = 0
    for line in lHV:
        x = line.split()
        timeHV.append(float(x[0]))
        blipType.append(x[1])
        blipIntensity.append(float(x[5]))
        blipDuration.append(float(x[6]))

    for line in lPMT:
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
                histo.Fill(cutY)

c1 = ROOT.TCanvas()
histo.Draw()
c1.SaveAs("Plots_Others/coincVsCut.png")
