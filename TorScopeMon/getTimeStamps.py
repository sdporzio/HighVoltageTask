# The script gets the timestamp for interesting events from the root files in
# sporzio@ubdaq-prod-ws01.fnal.gov:/home/gahs/torscopemon.
import os
import ROOT

dirPath = "/uboone/app/users/sporzio/HighVoltageTask/TorScopeMonAna/GAHS/RootFiles/"
homePath = "/uboone/app/users/sporzio/HighVoltageTask/"

outPath = homePath+"Timestamps/pmtHits.dat"

if os.path.exists(outPath):
    print "Removing previous", outPath
    os.remove(outPath)
for filename in os.listdir(dirPath):
    fRoot = ROOT.TFile(dirPath+filename,"READ")
    fOut = open(outPath,"a")

    tree = fRoot.torscope_tree

    for eventNumber in range(tree.GetEntries()):
        tree.GetEntry(eventNumber)
        originFile = dirPath + filename
        firstTS = str(tree.unixtime[0])
        fOut.write(originFile+" "+firstTS + "\n")
        # for timestamp in tree.unixtime:
            # fOut.write(str(timestamp) + "\n")
