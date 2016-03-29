# The script gets the timestamp for interesting events from the root files in
# sporzio@ubdaq-prod-ws01.fnal.gov:/home/gahs/torscopemon.
import os
import ROOT

# Script variables
yLimit = 10


# Path to input and output
rootDir = "/uboone/app/users/sporzio/HighVoltageTask/TorScopeMonAna/GAHS/RootFiles/"
outPath = "/uboone/app/users/sporzio/HighVoltageTask/Timestamps/pmtHits.dat"

# Script is writing over existing file, so delete it first if it belongs
# to previous run
if os.path.exists(outPath):
    print "Removing previous", outPath
    os.remove(outPath)

# Loop through each file in rootDir
for filename in os.listdir(rootDir):
    fRoot = ROOT.TFile(rootDir+filename,"READ")
    fOut = open(outPath,"a")

    # Open TTree
    tree = fRoot.torscope_tree
    for eventNumber in range(tree.GetEntries()):
        tree.GetEntry(eventNumber)
        originFile = rootDir + filename
        firstTS = str(tree.unixtime[0])
        fOut.write(originFile+" "+firstTS + "\n")
        # for timestamp in tree.unixtime:
            # fOut.write(str(timestamp) + "\n")
