import ROOT
import array
import datetime
import math
import sys
import numpy as np
workDir = '/Users/sdporzio/HighVoltageTask'
sys.path.insert(0, workDir)
import HvPackages.dataFunctions as dataFunctions

dates = np.genfromtxt("listToPlot.dat",delimiter="\t",names=True,dtype=None)
dt = []
for event in dates:
    dt.append(dataFunctions.GetChicagoTimestamp(event['Year'],event['Month'],event['Day'],event['Hour'],event['Minute'],event['Second']))
timestamps = np.array(dt)
print dates
print timestamps



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

# Read files
rootFile = workDir+"/Data_SlowMonCon/DT_PV_CM.root"
fRoot = ROOT.TFile(rootFile,"READ")
gDT = fRoot.gDT
gPV = fRoot.gPV
gCM = fRoot.gCM

# Create graph and canvas/home/sdporzio/HighVoltageTask
c1 = ROOT.TCanvas()

# Find entry corresponding to timestamp
for i in range(0,len(timestamps)-1):

    # Set axis
    minX = timestamps[i]-60*15
    maxX = timestamps[i]+60*15
    minY = dispPV-0.2
    maxY = dispCM+0.1
    gDT.GetXaxis().SetTimeDisplay(1)
    gDT.GetXaxis().SetRangeUser(minX,maxX)
    gDT.GetYaxis().SetRangeUser(minY,maxY)

    # Set title
    eTime = dataFunctions.GetTimeString(timestamps[i])
    eDate = dataFunctions.GetDateString(timestamps[i])
    gTitle = "%s [%s]" %(eDate,eTime)
    gDT.SetTitle(gTitle)

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
    c1.SaveAs("plot_"+str(timestamps[i])+".png")
