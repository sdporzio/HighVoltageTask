import ROOT
import array
import datetime
import sys
fermilabOffset = -6*60*60
ROOT.gStyle.SetTimeOffset(fermilabOffset);
ROOT.gStyle.SetPalette(ROOT.kRainBow);

startTime = ROOT.TDatime(2015,10,01,00,00,00).Convert()
weekTime = 604800
nWeeks = 20
nDays = nWeeks*7
daysPerBin = 7
endTime = startTime + weekTime*nWeeks

bQuickMode = 1 # if QuickMode is on, plots won't be visible
ROOT.gROOT.SetBatch(bQuickMode)
ROOT.gStyle.SetOptStat(1)

fBL = open("Timestamps/hvBlips.dat","r")
fBL.readline()

t = 0
time = array.array("d",[])
DTblipType = []
PVblipType = []
shortBaselineStatus = []
longBaselineStatus = []
peakob = array.array("d",[])
duration = array.array("d",[])

for line in fBL:
    x = line.split()
    time.append(float(x[0]))
    DTblipType.append(x[1])
    PVblipType.append(x[2])
    shortBaselineStatus.append(x[3])
    longBaselineStatus.append(x[4])
    peakob.append(float(x[5]))
    duration.append(float(x[6]))
    t+=1

peakMax = peakob[0]
peakMin = peakob[0]
durMax = duration[0]
durMin = duration[0]
for i in range(0,t):
    if peakob[i] > peakMax:
        peakMax = peakob[i]
    if peakob[i] < peakMin:
        peakMin = peakob[i]
    if duration[i] > durMax:
        durMax = duration[i]
    if duration[i] < durMin:
        durMin = duration[i]

hAllTime = ROOT.TH2D("hAllTime","Type of events vs. Time",int(nDays/daysPerBin),startTime,endTime,3,0,3)
hAllHour = ROOT.TH2D("hAllHour","Type of events vs. Hour",24,0,24,3,0,3)
hAllDayWeek = ROOT.TH2D("hAllDayWeek","Type of events vs. Day of the week",7,1,8,3,0,3)
hBlipNumber = ROOT.TH1D("hBlipNumber","Blip - Events vs. Time",int(nDays/daysPerBin),startTime,endTime)
#hBlipHeight = ROOT.TH2D("hBlipHeight","Blip - Height (over baseline) vs. time",nDays,startTime,endTime,10,peakMin,peakMax)
#hBlipDuration = ROOT.TH2D("hBlipDuration","Blip - Duration vs. time",nDays,startTime,endTime,10,durMin,durMax)
hBlipHeight = ROOT.TH2D("hBlipHeight","Blip - Height (over baseline) vs. time",int(nDays/daysPerBin),startTime,endTime,10,0,0.7)
hBlipDuration = ROOT.TH2D("hBlipDuration","Blip - Duration vs. time",int(nDays/daysPerBin),startTime,endTime,10,0,80)
hBlipHeightDist = ROOT.TH1D("hBlipHeight","Blip - Height",10,0,0.7)
hBlipDurationDist = ROOT.TH1D("hBlipDuration","Blip - Duration",10,0,80)

timeDivisions = int(nWeeks/4) + 4*100
hAllTime.GetXaxis().SetTimeDisplay(1)
# hAllTime.GetXaxis().SetTimeOffset(0,"UCT")
hBlipNumber.GetXaxis().SetTimeDisplay(1)
hBlipHeight.GetXaxis().SetTimeDisplay(1)
hBlipDuration.GetXaxis().SetTimeDisplay(1)
hBlipHeight.GetYaxis().SetTitle("Volt")
hBlipDuration.GetYaxis().SetTitle("Seconds")
hAllTime.GetYaxis().SetNdivisions(3,1)
hAllTime.GetXaxis().SetNdivisions(timeDivisions,0)
hBlipNumber.GetXaxis().SetNdivisions(timeDivisions,0)
hBlipHeight.GetXaxis().SetNdivisions(timeDivisions,0)
hBlipDuration.GetXaxis().SetNdivisions(timeDivisions,0)
hAllTime.GetYaxis().SetBinLabel(3,"Blip")
hAllTime.GetYaxis().SetBinLabel(2,"BaselineShift")
hAllTime.GetYaxis().SetBinLabel(1,"NotDefinite")
hAllHour.GetYaxis().SetBinLabel(3,"Blip")
hAllHour.GetYaxis().SetBinLabel(2,"BaselineShift")
hAllHour.GetYaxis().SetBinLabel(1,"NotDefinite")
hAllDayWeek.GetYaxis().SetBinLabel(3,"Blip")
hAllDayWeek.GetYaxis().SetBinLabel(2,"BaselineShift")
hAllDayWeek.GetYaxis().SetBinLabel(1,"NotDefinite")
hAllDayWeek.GetXaxis().SetBinLabel(1,"Monday")
hAllDayWeek.GetXaxis().SetBinLabel(2,"Tuesday")
hAllDayWeek.GetXaxis().SetBinLabel(3,"Wednesday")
hAllDayWeek.GetXaxis().SetBinLabel(4,"Thursday")
hAllDayWeek.GetXaxis().SetBinLabel(5,"Friday")
hAllDayWeek.GetXaxis().SetBinLabel(6,"Saturday")
hAllDayWeek.GetXaxis().SetBinLabel(7,"Sunday")

# hAllTime.GetXaxis().SetRangeUser(time[0],time[t-1])
# hBlipNumber.GetXaxis().SetRangeUser(time[0],time[t-1])
# hBlipHeight.GetXaxis().SetRangeUser(time[0],time[t-1])
# hBlipDuration.GetXaxis().SetRangeUser(time[0],time[t-1])




for i in range(0,t):
    if DTblipType[i] == "Blip" and PVblipType[i] == "Blip":
        bType = 2
    elif DTblipType[i] == "BaselineShift" and PVblipType[i] == "BaselineShift":
        bType = 1
    else:
        bType = 0
    dayWeek = ROOT.TDatime(int(time[i])).GetDayOfWeek()
    hour = ROOT.TDatime(int(time[i])).GetHour()
    day = ROOT.TDatime(int(time[i])).GetDay()
    hAllTime.Fill(int(time[i]),bType)
    if bType == 2:
        hBlipNumber.Fill(int(time[i]))
    hAllDayWeek.Fill(dayWeek,bType)
    hAllHour.Fill(hour,bType)
    hBlipHeight.Fill(int(time[i]),peakob[i])
    hBlipDuration.Fill(int(time[i]),duration[i])
    hBlipHeightDist.Fill(peakob[i])
    hBlipDurationDist.Fill(duration[i])

c1 = ROOT.TCanvas("c1","c1",1366,768)
hAllTime.Draw("COLZ")
hAllTime.Draw("SAME TEXT")
c2 = ROOT.TCanvas("c2","c2",1366,768)
c2.Divide(1,2)
c2.cd(1)
hBlipHeight.Draw("COLZ")
hBlipHeight.Draw("SAME TEXT")
c2.cd(2)
hBlipDuration.Draw("COLZ")
hBlipDuration.Draw("SAME TEXT")
c3 = ROOT.TCanvas("c3","c3",1366,768)
c3.Divide(1,2)
c3.cd(1)
hAllHour.Draw("COLZ")
hAllHour.Draw("SAME TEXT")
c3.cd(2)
hAllDayWeek.Draw("COLZ")
hAllDayWeek.Draw("SAME TEXT")
c4 = ROOT.TCanvas("c4","c4",1366,768)
hBlipNumber.Draw("EH")
c5 = ROOT.TCanvas("c5","c5",1366,768)
c5.Divide(1,2)
c5.cd(1)
hBlipHeightDist.Draw("EH")
c5.cd(2)
hBlipDurationDist.Draw("EH")


c1.SaveAs("Plots_Blips/c1.png")
c2.SaveAs("Plots_Blips/c2.png")
c3.SaveAs("Plots_Blips/c3.png")
c4.SaveAs("Plots_Blips/c4.png")
c5.SaveAs("Plots_Blips/c5.png")

if not bQuickMode:
    print "Waiting for input"
    raw_input()
