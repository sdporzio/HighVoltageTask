import ROOT
import time
import array
import wave

def plot_tormon_traces(tt, ientry=-1):
    """Make plots of traces from a torscope_tree.
    tt = a torscope tree
    ientry = entry number, or -1 for all
    """
    if ientry == -1:
        entrylist = range(0, tt.GetEntries())
    else:
        entrylist = [ientry]
    if len(entrylist) > 1:
        tt.GetEntry(min(entrylist))
        t1 = tt.unixtime
        timecode1 = time.strftime("%Y%m%d_%H%M%S%Z", time.localtime(t1))
        tt.GetEntry(max(entrylist))
        t2 = tt.unixtime
        timecode2 = time.strftime("%Y%m%d_%H%M%S%Z", time.localtime(t2))
        c = ROOT.TCanvas("c","c")
        tt.Draw("maxy-miny:unixtime")
        g = ROOT.TGraph(tt.GetEntries(), tt.GetV2(), tt.GetV1())
        g.SetMarkerStyle(ROOT.kCircle)
        g.SetTitle('Pulse pp ampl, %s to %s (%d pulses)' % (timecode1,timecode2,len(entrylist)))
        xa = g.GetHistogram().GetXaxis()
        xa.SetTimeFormat('%F1970-00-00 00:00:00s0')
        xa.SetTimeDisplay(1)
        g.Draw('AP')
        c.Print("pp-%s-%s.png" % (timecode1,timecode2))
        c.Close()
        c = None
        fwavout = wave.open('pulses-%s-%s.wav' % (timecode1,timecode2), 'w')
    else:
        t1 = tt.unixtime
        timecode1 = time.strftime("%Y%m%d_%H%M%S%Z", time.localtime(t1))
        fwavout = wave.open('pulses-%s.wav' % (timecode1), 'w')
    fwavout.setnchannels(1)
    fwavout.setsampwidth(1)
    fwavout.setframerate(8000)
    fwavout.setnframes(10000*len(entrylist))
    for ientry in entrylist:
        tt.GetEntry(ientry)
        ix = array.array('d', range(0, tt.nsamp))
        iy = array.array('d', list( (ord(i)+128)%256-128 for i in tt.trace ) )
        timetext = time.ctime(tt.unixtime)
        timecode = time.strftime("%Y%m%d_%H%M%S%Z", time.localtime(tt.unixtime))
        c = ROOT.TCanvas("c","c")
        g = ROOT.TGraph(tt.nsamp, ix, iy)
        g.SetTitle(timetext)
        g.Draw("ALW")
        c.Print("trace-%s.png" % timecode)
        c.Close()
        c = None
        cy2 = ''.join( chr((ord(i)+128)%256) for i in tt.trace )
        fwavout.writeframes(cy2)
    fwavout.close()


def main(argv):
    f = ROOT.TFile(argv[1])
    tt = f.torscope_tree
    if len(argv)>2:
        ientry = int(argv[2])
    else:
        ientry = -1
    plot_tormon_traces(tt, ientry)
    f.Close()

if __name__ == "__main__":
    import sys
    main(sys.argv)
