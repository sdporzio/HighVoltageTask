import ROOT
import array
import datetime
import math
import sys
import os
import numpy as np
from datetime import datetime as dt
projDir = os.environ.get('PROJDIR_HVANA')
sys.path.insert(0, projDir)
import HvPackages.dtOperations as DTO
import HvPackages.dataFunctions as dataFunctions

str2DT = lambda x: DTO.GetChicagoTimestampDT(dt.strptime(x,'%Y-%m-%d %H:%M:%S'))
catDown = np.genfromtxt(projDir+"/Extractor/cathodeDown.dat",delimiter="\t",names=True,dtype=None,converters={0:str2DT,1:str2DT})
def cathodeDown(time):
    for i in range(len(catDown)):
        if catDown['Start'][i] <= time <= catDown['End'][i]:
            return True
    return False

# THIS MUST GO AFTER ANY DTO FUNCTION! It's a global environment variable and it will mess with python scripts for datetime
ROOT.gSystem.Setenv("TZ","America/Chicago")
ROOT.gStyle.SetTimeOffset(0);

# Analysis variables
bNoLimit = 1 # Analyze portion of data (0) of all data (1)
bQuickMode = 1 # Batch mode
heightDev = 0.06 # How large a deviation from zero in the DT to start investigating the event
shortAveVal = 120 # Short average length (in seconds)
longAveVal = 900 # Long average length (in seconds)
allAveLR = 0.02 # Allowed average difference between left and right
allAveSL = 0.02 # Allowed average difference between short and long
peakobForBlip = 0.2 # Height over average to identify as blip
integralRatioForBlip = 0.4 # When integralRatio for DT diverge from 1 more than this value, events are identifies as baseline shifts
standDevForROI = 0.025 # How large short averages standard deviations are allowed to be, to claim well defined Region Of Interest

# Drawing variables
avePV = -216.75 # PV average baseline
aveCM = 6.3 # CM average baseline
multCM = 10 # Factor by which to "compress" CM data
dispPV = -0.2 # PV data "displacement" from zero (for drawing)
dispCM = 0.2 # CM data "displacement" from zero (for drawing)
ROOT.gROOT.SetBatch(bQuickMode)

# Time control
startData = 100 # Ignore the first "startData" points
endData = 500000 # Stop after "endData" points
dataPerCanvas = 200 # Beside the peak, how many extra datapoints to draw to the left and to the right

# Read files
fDT = open("Data_SlowMonCon/uB_TPCDrift_HV01_keithleyPickOff_voltDiff5s60s_160101_160615.dat")
fPV = open("Data_SlowMonCon/uB_TPCDrift_HV01_keithleyPickOff_getVoltage_160101_160615.dat")
fCM = open("Data_SlowMonCon/uB_TPCDrift_HV01_keithleyCurrMon_calcCurrent_160101_160615.dat")
# fDT = open("Data_SlowMonCon/differenceTracker.dat")
# fPV = open("Data_SlowMonCon/pickOffVoltage.dat")
# fCM = open("Data_SlowMonCon/currMon.dat")
fBL = open("Data_Events/hvEvents_"+str(heightDev)+"V.dat","w")
fDT.readline()
fPV.readline()
fCM.readline()
fBL.write('# Timestamp TypeDT TypePV ShortStatus LongStatus PeakRatio PeakOverBaseline FWHM\n')

# Read data from files
t = 0
valDT = array.array("d",[])
timeDT = array.array("d",[])
valPV = array.array("d",[])
timePV = array.array("d",[])
valCM = array.array("d",[])
timeCM = array.array("d",[])

for line in fDT:
    if line.startswith("#"):
        print "found one!"
        continue
    x = line.split()
    timeDT.append(float(x[0]))
    valDT.append(float(x[1]))
    t+=1
    if not bNoLimit:
        if t==endData:
            break

for line in fPV:
    if line.startswith("#"):
        print "found one!"
        continue
    x = line.split()
    timePV.append(float(x[0]))
    valPV.append(float(x[1])-avePV+dispPV)
    t+=1
    if not bNoLimit:
        if t==endData:
            break

for line in fCM:
    if line.startswith("#"):
        print "found one!"
        continue
    x = line.split()
    timeCM.append(float(x[0]))
    valCM.append((float(x[1])-aveCM)/multCM+dispCM)
    t+=1
    if not bNoLimit:
        if t==endData:
            break

# Create graph and canvas
c1 = ROOT.TCanvas()
gDT = ROOT.TGraph(len(timeDT)-1,timeDT,valDT)
gPV = ROOT.TGraph(len(timePV)-1,timePV,valPV)
gCM = ROOT.TGraph(len(timeCM)-1,timeCM,valCM)
gDT.GetXaxis().SetTimeDisplay(1)
gDT.SetMarkerColor(2)
gDT.SetMarkerStyle(7)
gPV.GetXaxis().SetTimeDisplay(1)
gPV.SetMarkerColor(3)
gPV.SetMarkerStyle(7)
gCM.GetXaxis().SetTimeDisplay(1)
gCM.SetMarkerColor(29)
gCM.SetMarkerStyle(7)


# Run the analysis
peakPointer = 0
iDT = 0
iPV = 0
iCM = 0
PVpointL = 0
PVpointR = 0
PVpointC = 0
while iDT < len(timeDT)-1:
    # if cathode is down go to next datapoint
    if cathodeDown(timeDT[iDT]):
        print "CathodeDown!"
        iDT += 1
        continue

    # Default analysis variable values
    bInteresting = False
    blipSign = 0 # Whether peak is positive (+1) or negative (-1)

    # Start analysis only after "startData" points
    while iDT<startData:
        iDT+=1

    # Determine if event is interesting (function)
    blipSign, bInteresting = dataFunctions.DetIfInteresting(valDT[iDT],heightDev,blipSign,bInteresting)

    if bInteresting:
        # Find DT key points
        DTpoint0,DTpointL1,DTpointC1,DTpointR1,DTpointL2zero,DTpointR2zero,DTpointL2,DTpointR2,DTpointC2 = dataFunctions.FindDTKeyPoints(blipSign,valDT,iDT)
        integral1,integral2,intRatio = dataFunctions.DetDTIntegral(valDT,timeDT,DTpointL1,DTpointR1,DTpointL2,DTpointR2)
        peakRatio = abs(valDT[DTpointC1]/valDT[DTpointC2])
        peakPointer = DTpointC1
        iDT = DTpointR2 # New starting point for analysis will be end of previous interesting region

        # Determine type of event based on DT data
        if abs(intRatio-1) < integralRatioForBlip:
            DTblipType = "Blip"
        else:
            DTblipType = "BaselineShift"

        # If event is baseline shift, left and right event lines coincide
        # if DTblipType == "BaselineShift":
        #     DTpointL1 = DTpointC1
        #     DTpointR1 = DTpointC1

        # Get other datasets "in sync" with DT
        while timePV[PVpointL] < timeDT[DTpointL1]:
            PVpointL+=1
        while timePV[PVpointR] < timeDT[DTpointR1]:
            PVpointR+=1
        while timePV[PVpointC] < timeDT[DTpointC1]:
            PVpointC+=1

        # Get PV short and long averages
        PVpointLSA,PVpointRSA,shortAveL,shortAveR = dataFunctions.DetLeftRightAverages(shortAveVal,timePV,valPV,PVpointL,PVpointR)
        PVpointLLA,PVpointRLA,longAveL,longAveR = dataFunctions.DetLeftRightAverages(longAveVal,timePV,valPV,PVpointL,PVpointR)
        sdL,sdR = dataFunctions.DetLeftRightStandardDeviations(shortAveVal,timePV,valPV,PVpointL,PVpointR,PVpointLSA,PVpointRSA,shortAveL,shortAveR)
        print "%.6f, %.6f" %(sdL,sdR)

        # Determine if other peaks are around ROI
        if max(sdL,sdR) > standDevForROI:
            wellDefinedROI = False
        else:
            wellDefinedROI = True

        # Determine PV baseline status
        if abs(longAveL-longAveR) < allAveLR:
            longBaselineStatus = "Steady"
        else:
            longBaselineStatus = "NotSteady"
        if abs(shortAveL-shortAveR) < allAveLR:
            shortBaselineStatus = "Flat"
        else:
            shortBaselineStatus = "NotFlat"

        if longBaselineStatus == "NotFlat" and DTblipType == "BaselineShift":
            if abs(shortAveL-longAveL) < allAveSL and abs(shortAveR-longAveR) < allAveSL:
                longBaselineStatus = "BaselineShift"
            else:
                longBaselineStatus = "Unsteady"

        if longBaselineStatus == "Flat" and abs(shortAveL-longAveL) < allAveSL and abs(shortAveR-longAveR) < allAveSL:
            longBaselineStatus = "Clear"


        # Find PV peak feet
        if shortBaselineStatus == "Flat":
            PVpointL1,PVpointR1 = dataFunctions.FindPVFeet(valPV,blipSign,PVpointC,shortAveR,shortAveL)
        else:
            if longBaselineStatus == "Flat" or longBaselineStatus == "Clear":
                PVpointL1,PVpointR1 = dataFunctions.FindPVFeet(valPV,blipSign,PVpointC,longAveR,longAveL)
            else:
                PVpointL1,PVpointR1 = dataFunctions.FindPVFeet(valPV,blipSign,PVpointC,shortAveR,shortAveL)

        PVpointC1 = dataFunctions.FindExtremum(blipSign,valPV,PVpointL1,PVpointR1)
        peakob = valPV[PVpointC1] - (shortAveR+shortAveL)/2

        # Determine peak width
        fwhm,fwhmPointL,fwhmPointR = dataFunctions.DetPVPeakWidth(valPV,timePV,blipSign,PVpointC1,PVpointL1,PVpointR1)

        # Determine PV blip type
        if shortBaselineStatus == "NotFlat":
            PVblipType = "BaselineShift"
        else:
            PVblipType = "Blip"

        if peakob > peakobForBlip:
            PVblipType = "Blip"


        # Get event data
        eTime = dataFunctions.GetTimeString(timeDT[DTpointL1])
        eDate = dataFunctions.GetDateString(timeDT[DTpointL1])
        print "DT blip type: %s" %(DTblipType)
        print "PV blip type: %s" %(PVblipType)
        print "Long baseline status: %s (delta: %.2f)" %(longBaselineStatus, abs(longAveL-longAveR))
        print "Short baseline status: %s (delta: %.2f)" %(shortBaselineStatus, abs(shortAveL-shortAveR))
        print "Starting time: %s %s" %(eDate,eTime)
        print "Duration: %i s" %(fwhm)
        print "Absolute PV peak: %.2f" %(peakob)



        # DRAWING SECTION

        # Drawing variables
        # maxX= timeDT[DTpointR1 + dataPerCanvas/2]
        # minX = timeDT[DTpointL1 - dataPerCanvas/2]
        minX = timePV[PVpointLLA]
        maxX = timePV[PVpointRLA]
        minY = dispPV-0.2
        maxY = dispCM+0.1
        lineLimitR = min(timePV[PVpointRLA],maxX)
        lineLimitL = max(timePV[PVpointLLA],minX)
        # minY = min(valDT[iDT],valPV[iPV],valCM[iCM])*1.5
        # maxY = max(valDT[iDT],valPV[iPV],valCM[iCM])*1.5
        # minY = -1*abs(valDT[DTpointC1])*1.5
        # maxY = abs(valDT[DTpointC1])*1.5

        # Lines
        lCenter = ROOT.TLine(minX,0,maxX,0)
        lDevU = ROOT.TLine(minX,heightDev,maxX,heightDev)
        lDevD = ROOT.TLine(minX,-heightDev,maxX,-heightDev)
        lTimeL = ROOT.TLine(timeDT[DTpointL1],minY,timeDT[DTpointL1],maxY)
        lTimeR = ROOT.TLine(timeDT[DTpointR1],minY,timeDT[DTpointR1],maxY)
        lTimeC = ROOT.TLine(timeDT[DTpointC1],minY,timeDT[DTpointC1],maxY)
        lInteresting = ROOT.TLine(timeDT[DTpointL1],valDT[DTpointL1],timeDT[DTpoint0],valDT[DTpoint0])
        lShortAveL = ROOT.TLine(timePV[PVpointLSA],shortAveL,timePV[PVpointL],shortAveL)
        lShortAveR = ROOT.TLine(timePV[PVpointRSA],shortAveR,timePV[PVpointR],shortAveR)
        lLongAveL = ROOT.TLine(lineLimitL,longAveL,timePV[PVpointL],longAveL)
        lLongAveR = ROOT.TLine(timePV[PVpointR],longAveR,lineLimitR,longAveR)
        lFwhm = ROOT.TLine(timePV[fwhmPointL],(valPV[fwhmPointL]+valPV[fwhmPointR])/2.,timePV[fwhmPointR],(valPV[fwhmPointL]+valPV[fwhmPointR])/2.)

        # Markers
        mark0 = ROOT.TMarker(timeDT[DTpoint0],valDT[DTpoint0],29)
        markL1 = ROOT.TMarker(timeDT[DTpointL1],valDT[DTpointL1],29)
        markC1 = ROOT.TMarker(timeDT[DTpointC1],valDT[DTpointC1],29)
        markR1 = ROOT.TMarker(timeDT[DTpointR1],valDT[DTpointR1],29)
        markL2 = ROOT.TMarker(timeDT[DTpointL2],valDT[DTpointL2],29)
        markC2 = ROOT.TMarker(timeDT[DTpointC2],valDT[DTpointC2],29)
        markR2 = ROOT.TMarker(timeDT[DTpointR2],valDT[DTpointR2],29)
        markPVL1 = ROOT.TMarker(timePV[PVpointL1],valPV[PVpointL1],29)
        markPVR1 = ROOT.TMarker(timePV[PVpointR1],valPV[PVpointR1],29)
        markPVC1 = ROOT.TMarker(timePV[PVpointC1],valPV[PVpointC1],29)

        mark0.SetMarkerColor(15)
        markL1.SetMarkerColor(1)
        markC1.SetMarkerColor(3)
        markR1.SetMarkerColor(1)
        markL2.SetMarkerColor(1)
        markC2.SetMarkerColor(4)
        markR2.SetMarkerColor(1)
        markPVL1.SetMarkerColor(1)
        markPVR1.SetMarkerColor(1)
        markPVC1.SetMarkerColor(2)
        lTimeL.SetLineColor(12)
        lTimeR.SetLineColor(12)
        lTimeC.SetLineColor(12)
        lDevU.SetLineColor(16)
        lDevD.SetLineColor(16)
        lFwhm.SetLineColor(16)
        lShortAveL.SetLineColor(12)
        lShortAveR.SetLineColor(12)
        lLongAveL.SetLineColor(12)
        lLongAveR.SetLineColor(12)
        lShortAveL.SetLineWidth(3)
        lShortAveR.SetLineWidth(3)
        lLongAveL.SetLineWidth(3)
        lLongAveR.SetLineWidth(3)

        # Lines for PaveText
        paveText = ROOT.TPaveText(0.6,0.7,0.95,0.92,"NDC")
        DTblipLine = "DT event type: %s" %(DTblipType)
        PVblipLine = "PV event type: %s" %(PVblipType)
        intLine = "DT Integral(1/2/R): %.2f/%.2f/%.2f" %(integral1,integral2,intRatio)
        heightLine = "PV PeakOvBase: %.2f" %(peakob)
        durationLine = "Duration: %i s" %(fwhm)
        baselineLine = "BaselineStatus: %s" %(longBaselineStatus)
        ROILine = "WellDefined ROI: %s" %(wellDefinedROI)
        sdLine = "StandDev: %.2f/%.2f" %(sdL,sdR)
        paveText.AddText(DTblipLine)
        paveText.AddText(PVblipLine)
        paveText.AddText(baselineLine)
        paveText.AddText(intLine)
        paveText.AddText(ROILine)
        paveText.AddText(sdLine)
        if DTblipType == "Blip":
            paveText.AddText(heightLine)
            paveText.AddText(durationLine)
        if DTblipType != PVblipType:
            paveText.SetFillColor(2)

        # Legend
        leg = ROOT.TLegend(0.6,0.11,0.89,0.25)
        leg.AddEntry(gDT, "Deviation Tracker", "p")
        leg.AddEntry(gPV, "PickOff Voltage", "p")
        leg.AddEntry(gCM, "Current Monitor", "p")
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)

        # Set title
        gTitle = "%s [%s]" %(eDate,eTime)
        gDT.SetTitle(gTitle)

        # Set axis
        gDT.GetXaxis().SetRangeUser(minX,maxX)
        gDT.GetYaxis().SetRangeUser(minY,maxY)

        # Draw everything
        gDT.Draw("AP")
        lCenter.Draw()
        lDevU.Draw()
        lDevD.Draw()
        lShortAveL.Draw()
        lShortAveR.Draw()
        if DTblipType == "Blip":
            lTimeL.Draw()
            lTimeR.Draw()
            lLongAveL.Draw()
            lLongAveR.Draw()
            lFwhm.Draw()
        else:
            lTimeC.Draw()
        gCM.Draw("SAMEP")
        gDT.Draw("SAMEP")
        gPV.Draw("SAMEP")
        mark0.Draw()
        markL1.Draw()
        markC1.Draw()
        markR1.Draw()
        markL2.Draw()
        markC2.Draw()
        markR2.Draw()
        markPVL1.Draw()
        markPVR1.Draw()
        markPVC1.Draw()
        paveText.Draw()
        leg.Draw()

        outPath = "Plots/Blips_"+str(heightDev)+"V/"
        if not os.path.isdir(outPath):
            os.makedirs(outPath)
        c1.SaveAs(outPath+"blip_"+str(int(timeDT[peakPointer]))+".png")
        outputline = "%i %s %s %s %s %f %f %f\n" %(timeDT[peakPointer],DTblipType,PVblipType,shortBaselineStatus,longBaselineStatus,peakRatio,peakob,fwhm)
        print outputline
        fBL.write(outputline)

        if not bQuickMode:
            raw_input()
        else:
            print "\n"



    iDT += 1
