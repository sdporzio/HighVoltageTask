import ROOT
import array
import datetime
import math
import sys
sys.path.insert(0, '/Users/sdporzio/HighVoltageTask')
import HvPackages.dataFunctions as dataFunctions

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
    sys.exit("ERROR: No input file provided")

# Read files
rootFile = "Data/DT_PV_CM.root"
fRoot = ROOT.TFile(rootFile,"READ")
gDT = fRoot.gDT
gPV = fRoot.gPV
gCM = fRoot.gCM

fTS = open(timeList)
fTS.readline()
timeTS = array.array("d",[])
for line in fTS:
    timeTS.append(float(line))

# Create graph and canvas/home/sdporzio/HighVoltageTask
c1 = ROOT.TCanvas()

# Find entry corresponding to timestamp
for i in range(0,len(timeTS)-1):

    # Set axis
    minX = timeTS[i]-dataPerCanvas
    maxX = timeTS[i]+dataPerCanvas
    minY = dispPV-0.2
    maxY = dispCM+0.1
    gDT.GetXaxis().SetTimeDisplay(1)
    gDT.GetXaxis().SetRangeUser(minX,maxX)
    gDT.GetYaxis().SetRangeUser(minY,maxY)

    # Set title
    eTime = dataFunctions.GetTimeString(timeTS[i])
    eDate = dataFunctions.GetDateString(timeTS[i])
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
    c1.SaveAs("Plots_FromList/plot_"+str(timeTS[i])+".png")
