import ROOT
import array
import math
import os

# Path to input/output and variables
rootDir = "/Users/sdporzio/HighVoltageTask/TorScopeMon/GAHS/RootFiles/"
originFile = []
timestamp = array.array("f",[])
miny1 = array.array("f",[])
miny2 = array.array("f",[])
miny3 = array.array("f",[])
miny4 = array.array("f",[])
avgy1 = array.array("f",[])
avgy2 = array.array("f",[])
avgy3 = array.array("f",[])
avgy4 = array.array("f",[])
maxy1 = array.array("f",[])
maxy2 = array.array("f",[])
maxy3 = array.array("f",[])
maxy4 = array.array("f",[])

totEntries = 0
# Loop through each file in rootDir
for filename in os.listdir(rootDir):
    # Open TTree
    fRoot = ROOT.TFile(rootDir+filename,"READ")
    tree = fRoot.torscope_tree
    # Loop through each event and store values
    nEntries = tree.GetEntries()
    totEntries = totEntries + nEntries
    for eventNumber in range(nEntries):
        tree.GetEntry(eventNumber)
        originFile.append(filename)
        timestamp.append(float(tree.unixtime[0]))
        miny1.append(float(tree.miny[0]))
        miny2.append(float(tree.miny[1]))
        miny3.append(float(tree.miny[2]))
        miny4.append(float(tree.miny[3]))
        avgy1.append(float(tree.avgy[0]))
        avgy2.append(float(tree.avgy[1]))
        avgy3.append(float(tree.avgy[2]))
        avgy4.append(float(tree.avgy[3]))
        maxy1.append(float(tree.maxy[0]))
        maxy2.append(float(tree.maxy[1]))
        maxy3.append(float(tree.maxy[2]))
        maxy4.append(float(tree.maxy[3]))
print "Done! (%i entries)" %(totEntries)

outName = "../Timestamps/pmtHitsFromTorScopeMon.dat"
fOut = open(outName,"w")
outString = "OriginFile Timestamp MinY1 MinY2 MinY3 MinY4\n"
fOut.write(outString)
for i in range(totEntries):
        outString = str(originFile[i])+" "+str(timestamp[i])+" "+str(miny1[i])+" "+str(miny2[i])+" "+str(miny3[i])+" "+str(miny4[i])+"\n"
        fOut.write(outString)
