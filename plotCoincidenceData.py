import ROOT
import array
import datetime
import sys
import dataFunctions
import math

ROOT.gSystem.Setenv("TZ","America/Chicago")
ROOT.gStyle.SetTimeOffset(0);

# Analysis variables
bQuickMode = 1 # Batch mode
# Drawing variables
dataPerCanvas = 200 # How many extra seconds to draw (left and right)
avePV = -216.75 # PV average baseline
aveCM = 6.3 # CM average baseline
multCM = 10 # Factor by which to "compress" CM data
dispPV = -0.2 # PV data "displacement" from zero (for drawing)
dispCM = 0.2 # CM data "displacement" from zero (for drawing)
ROOT.gROOT.SetBatch(bQuickMode)

# Check input file
if len(sys.argv) > 1:
    timeList = sys.argv[1]
else:
    timeList = "Timestamps/coincidencesHvPmt_30s.dat"

# Read files
rootFile = "Data/DT_PV_CM.root"
fRoot = ROOT.TFile(rootFile,"READ")
gDT = fRoot.gDT
gPV = fRoot.gPV
gCM = fRoot.gCM

fTS = open(timeList)
fTS.readline()
pathTS = []
timePMT = array.array("d",[])
timeHV = array.array("d",[])
typeTS = []
intensityTS = array.array("d",[])
durationTS = array.array("d",[])
deltaTS = array.array("d",[])

for line in fTS:
    x = line.split()
    pathTS.append(x[0])
    timePMT.append(float(x[1]))
    timeHV.append(float(x[2]))
    typeTS.append(x[3])
    intensityTS.append(float(x[4]))
    durationTS.append(float(x[5]))
    deltaTS.append(float(x[6]))

# Create graph and canvas
c1 = ROOT.TCanvas()

# Find entry corresponding to timestamp
for i in range(len(timePMT)-1):

    # Set axis
    minX = timePMT[i]-dataPerCanvas
    maxX = timePMT[i]+dataPerCanvas
    minY = dispPV-0.2
    maxY = dispCM+0.1
    gDT.GetXaxis().SetTimeDisplay(1)
    gDT.GetXaxis().SetRangeUser(minX,maxX)
    gDT.GetYaxis().SetRangeUser(minY,maxY)

    # Set title
    eTime = dataFunctions.GetTimeString(timePMT[i])
    eDate = dataFunctions.GetDateString(timePMT[i])
    gTitle = "%s [%s]" %(eDate,eTime)
    gDT.SetTitle(gTitle)

    # Set lines
    lPMT = ROOT.TLine(timePMT[i],minY,timePMT[i],maxY)
    lPMT.SetLineWidth(3)
    lPMT.SetLineColor(2)
    lHV = ROOT.TLine(timeHV[i],minY,timeHV[i],maxY)
    lHV.SetLineWidth(3)
    lHV.SetLineColor(2)

    # Set paveText
    paveText = ROOT.TPaveText(0.6,0.7,0.95,0.92,"NDC")
    ptType = "Blip type: %s" %(typeTS[i])
    ptIntensity = "Intensity: %.2f V" %(intensityTS[i])
    ptDuration = "Duration: %.2f s" %(durationTS[i])
    ptDelta = "DeltaTime(PMT - HV): %.2f" %(deltaTS[i])
    paveText.AddText(ptType)
    paveText.AddText(ptIntensity)
    paveText.AddText(ptDuration)
    paveText.AddText(ptDelta)

    # Legend
    leg = ROOT.TLegend(0.6,0.11,0.89,0.25)
    leg.AddEntry(gDT, "Deviation Tracker", "p")
    leg.AddEntry(gPV, "PickOff Voltage", "p")
    leg.AddEntry(gCM, "Current Monitor", "p")
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    gDT.Draw("AP")
    gCM.Draw("SAMEP")
    gDT.Draw("SAMEP")
    gPV.Draw("SAMEP")
    leg.Draw()
    lPMT.Draw()
    lHV.Draw()
    paveText.Draw()
    c1.SaveAs("Plots_FromList/plot_"+str(timePMT[i])+".png")
