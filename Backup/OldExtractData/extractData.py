import getDataAndrzej
import time
import datetime
import commands
import array
import ROOT

def cathodeDown(time):
    if (time > 1444400000) and (time < 1444530000):
        return True
    if (time > 1450008420) and (time < 1450040000):
        return True
    if (time > 1447840000) and (time < 1447875000):
        return True
    if (time > 1448640000) and (time < 1448670000):
        return True
    if (time > 1449600000) and (time < 1449800000):
        return True
    if (time > 1450010000) and (time < 1450040000):
        return True
    if (time > 1451448000) and (time < 1451468000):
        return True

    if (time > 1451447093) and (time < 1451467687):
        return True
    if (time > 1454421186) and (time < 1454447472):
        return True
    if (time > 1454502120) and (time < 1454618935):
        return True
    if (time > 1456930245) and (time < 1456930245):
        return True
    if (time > 1457188710) and (time < 1457202990):
        return True
    if (time > 1459947539) and (time < 1459981289):
        return True
    if (time > 1460041170) and (time < 1460057720):
        return True

    if timestamp > 1450006200 and timestamp < 1450041600:
        return True
    if timestamp > 1454418000 and timestamp < 1454551200:
        return True
    if timestamp > 1456927200 and timestamp < 1456981200:
        return True
    if timestamp > 1459976400 and timestamp < 1460088000:
        return True

    return False

timeArray = array.array("i",[0])
voltArray = array.array("d",[0])
#rootFile = ROOT.TFile("Data/peaks.root","recreate")
#tree = ROOT.TTree("PickoffPointVoltage","PickoffPointVoltage")
#tree.Branch("Time",timeArray,"Time/I")
#tree.Branch("Voltage",voltArray,"Voltage/D")


POP_voltage = "uB_TPCDrift_HV01_keithleyPickOff/getVoltage"
AnVoltage = "uB_TPCDrift_HV01_keithleyCurrMon/getVoltage"
AnCurrent = "uB_TPCDrift_HV01_keithleyCurrMon/calcCurrent"
POP_diff = "uB_TPCDrift_HV01_keithleyPickOff/voltDiff5s60s"

start_time = datetime.datetime(2016, 1, 28, 00, 00, 0)
end_time = datetime.datetime(2016, 1, 30, 00, 00, 0)

POP_result = getDataAndrzej.GetVarArrayInterval(POP_voltage, start_time, end_time)
AnV_result = getDataAndrzej.GetVarArrayInterval(AnVoltage, start_time, end_time)
AnC_result = getDataAndrzej.GetVarArrayInterval(AnCurrent, start_time, end_time)
Diff_result = getDataAndrzej.GetVarArrayInterval(POP_diff, start_time, end_time)


datapath = "./"
f_POP = open("PickOffVoltage.dat","w")
f_AnC = open("CurrMon.dat","w")
#f2_POP = open("Data/PickOffVoltage_peaks.dat","w")
#f_POP.write("TIME "+POP_voltage+"\n")
#f2_POP.write("TIME "+POP_voltage+"\n")
#f_Diff = open("Data/DifferenceTracker.dat","w")
#f2_Diff = open("Data/DifferenceTracker_peaks.dat","w")
#f_Diff.write("TIME "+POP_diff+"\n")
#f2_Diff.write("TIME "+POP_diff+"\n")
#f2_AnC = open("Data/CurrMon_peaks.dat","w")
#f_AnC.write("TIME "+AnCurrent+"\n")
#f2_AnC.write("TIME "+AnCurrent+"\n")
day = -1

for x in POP_result:
  time = ROOT.TDatime(x[0].year,x[0].month,x[0].day,x[0].hour,x[0].minute,x[0].second).Convert()
  if cathodeDown(time):
    continue
  if x[0].day != day:
    day = x[0].day
    print x[0]

  if x[1]:
    f_POP.write(str(time)+" "+str(x[1])+"\n")
    timeArray[0]=time
    voltArray[0]=x[1]
#    tree.Fill()
#    if x[1] > -216.8:
#      f2_POP.write(str(time)+" "+str(x[1])+"\n")

#tree.Write()
#day = -1
#for x in Diff_result:
#  time = ROOT.TDatime(x[0].year,x[0].month,x[0].day,x[0].hour,x[0].minute,x[0].second).Convert()
#  if cathodeDown(time):
#    continue
#  if x[0].day != day:
#    day = x[0].day
#    print x[0]
#  if x[1]:
#    f_Diff.write(str(time)+" "+str(x[1])+"\n")
#    if abs(x[1]) > 0.01:
#      f2_Diff.write(str(time)+" "+str(x[1])+"\n")

for x in AnC_result:
  time = ROOT.TDatime(x[0].year,x[0].month,x[0].day,x[0].hour,x[0].minute,x[0].second).Convert()
  if cathodeDown(time):
    continue
  if x[0].day != day:
    day = x[0].day
    print x[0]
  if x[1]:
    f_AnC.write(str(time)+" "+str(x[1])+"\n")
#    if abs(x[1]) > 0.01:
#      f2_AnC.write(str(time)+" "+str(x[1])+"\n")
