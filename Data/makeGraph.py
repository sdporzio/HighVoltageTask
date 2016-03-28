import ROOT
import array
import datetime
import sys
import dataFunctions
import math

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

# Read files
dirPath = "/uboone/data/users/sporzio/HighVoltageTask/ExtendedData/"
fDT = open(dirPath+"DifferenceTracker.dat")
fPV = open(dirPath+"PickOffVoltage.dat")
fCM = open(dirPath+"CurrMon.dat")
fRoot = ROOT.TFile("DT_PV_CM.root","RECREATE")
fDT.readline()
fPV.readline()
fCM.readline()
valDT = array.array("d",[])
timeDT = array.array("d",[])
valPV = array.array("d",[])
timePV = array.array("d",[])
valCM = array.array("d",[])
timeCM = array.array("d",[])

# Read data from files
for line in fDT:
    x = line.split()
    timeDT.append(float(x[0]))
    valDT.append(float(x[1]))
for line in fPV:
    x = line.split()
    timePV.append(float(x[0]))
    valPV.append(float(x[1])-avePV+dispPV)
for line in fCM:
    x = line.split()
    timeCM.append(float(x[0]))
    valCM.append((float(x[1])-aveCM)/multCM+dispCM)

# Create graph and canvas
c1 = ROOT.TCanvas()
gDT = ROOT.TGraph(len(timeDT)-1,timeDT,valDT)
gPV = ROOT.TGraph(len(timePV)-1,timePV,valPV)
gCM = ROOT.TGraph(len(timeCM)-1,timeCM,valCM)
gDT.SetName("gDT")
gPV.SetName("gPV")
gCM.SetName("gCM")
gDT.GetXaxis().SetTimeDisplay(1)
gDT.SetMarkerColor(2)
gDT.SetMarkerStyle(7)
gPV.GetXaxis().SetTimeDisplay(1)
gPV.SetMarkerColor(3)
gPV.SetMarkerStyle(7)
gCM.GetXaxis().SetTimeDisplay(1)
gCM.SetMarkerColor(29)
gCM.SetMarkerStyle(7)

# Set axis
minY = dispPV-0.2
maxY = dispCM+0.1
gDT.GetYaxis().SetRangeUser(minY,maxY)

# Legend
leg = ROOT.TLegend(0.6,0.11,0.89,0.25)
leg.AddEntry(gDT, "Deviation Tracker", "p")
leg.AddEntry(gPV, "PickOff Voltage", "p")
leg.AddEntry(gCM, "Current Monitor", "p")
leg.SetFillStyle(0)
leg.SetBorderSize(0)

gDT.Write()
gPV.Write()
gCM.Write()
