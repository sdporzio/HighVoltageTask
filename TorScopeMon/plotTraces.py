import ROOT
import time
import array
#import wave

MARKER_STYLES = [ROOT.kFullCircle, ROOT.kOpenCircle, ROOT.kOpenTriangleUp,
                 ROOT.kOpenSquare]

MARKER_COLORS = [ROOT.kYellow+1, ROOT.kBlue, ROOT.kViolet+1, ROOT.kGreen+3]


def plot_tormon_traces(tt, ientry=-1):
    """Make plots of traces from a torscope_tree.
    tt = a torscope tree
    ientry = entry number, or -1 for all
    """
    #-- parse ientry argument into list of entries
    if ientry == -1:
        entrylist = range(0, tt.GetEntries())
    else:
        entrylist = [ientry]
    #-- make plot of peak-to-peak voltage vs time
    if len(entrylist) > 1:
        tt.GetEntry(min(entrylist))
        t1 = min(tt.unixtime)
        timecode1 = time.strftime("%Y%m%d_%H%M%S%Z", time.localtime(t1))
        tt.GetEntry(max(entrylist))
        t2 = max(tt.unixtime)
        timecode2 = time.strftime("%Y%m%d_%H%M%S%Z", time.localtime(t2))
        c = ROOT.TCanvas("c","c")
        c.Divide(2,2)
        g = [None]*4
        for ich in range(4):
            c.cd(ich+1)
            tt.Draw("maxy[%d]-miny[%d]:unixtime[%d]" % (ich,ich,ich) )
            g[ich] = ROOT.TGraph(tt.GetEntries(), tt.GetV2(), tt.GetV1())
            g[ich].SetMarkerStyle(MARKER_STYLES[ich])
            g[ich].SetMarkerColor(MARKER_COLORS[ich])
            g[ich].SetTitle('Ch %d Pulse pp ampl, %s to %s (%d pulses)' %
                       (ich+1, timecode1,timecode2,len(entrylist)))
            xa = g[ich].GetHistogram().GetXaxis()
            xa.SetTimeFormat('%F1970-00-00 00:00:00s0')
            xa.SetTimeDisplay(1)
            g[ich].Draw('AWP')
            #ROOT.gPad.Modified()
        c.cd(0)
        #c.Modified()
        #c.Update()
        c.Print("pp-%s-%s.png" % (timecode1,timecode2))
        #pdf_fn = "pulses-%s-%s.pdf" % (timecode1,timecode2)
        #c.Print("%s(" % pdf_fn)
        ## open wave output file
        #fwavout = wave.open('pulses-%s-%s.wav' % (timecode1,timecode2), 'w')
    else:
        c = ROOT.TCanvas("c","c")
        tt.GetEntry(min(entrylist))
        t1 = min(tt.unixtime)
        t2 = max(tt.unixtime)
        timecode1 = time.strftime("%Y%m%d_%H%M%S%Z", time.localtime(t1))
        timecode2 = time.strftime("%Y%m%d_%H%M%S%Z", time.localtime(t2))
        #pdf_fn = "pulses-%s-%s.pdf" % (timecode1,timecode2)
        #c.Print("%s[" % pdf_fn)
        ## open wave output file
        #fwavout = wave.open('pulses-%s.wav' % (timecode1), 'w')
    #-- plot interesting pulses
    #fwavout.setnchannels(1)
    #fwavout.setsampwidth(1)
    #fwavout.setframerate(8000)
    #fwavout.setnframes(4*10000)
    nplotted = 0
    for ientry in entrylist:
        tt.GetEntry(ientry)
        # if not all(tt.maxy[i]-tt.miny[i] > 20 for i in range(4)):
        #     continue
        ix = array.array('d', range(0, 10000)*4)
        iy = array.array('d', list( (ord(i)+128)%256-128 for i in tt.trace ) )
        timetext = time.ctime(tt.unixtime[0])
        timecode = time.strftime("%Y%m%d_%H%M%S%Z", time.localtime(tt.unixtime[0]))
        c.Clear()
        c.DrawFrame(0, -128, 10000, 128,
                    "%s;sample;ADC counts" % timetext)
        gw = [None]*4
        for i in range(4):
            gw[i] = ROOT.TGraph(10000, ix[i*10000:(i+1)*10000],
                                iy[i*10000:(i+1)*10000])
            #gw[i].SetMarkerStyle(MARKER_STYLES[i])
            gw[i].SetLineColor(MARKER_COLORS[i])
            gw[i].SetLineWidth(5-i)
            gw[i].Draw("L")
        #c.Modified()
        #c.Update()
        c.Print("trace-%s.png" % timecode)
        #c.Print(pdf_fn)
        #plot
        #cy2 = ''.join( chr((ord(i)+128)%256) for i in tt.trace )
        #fwavout.writeframes(cy2)
        nplotted += 1
    #fwavout.close()
    #c.Print("%s]" % pdf_fn)
    print "Plotted %d pulses where all channels saw signal" % nplotted


def main(argv):
    """Command-line interface for plot_tormon_traces()
    Usage:  python plot_tormon_traces.py (root-filename) [entry number]
    Default is to plot all entries.
    """
    if len(argv) <= 1:
        print main.__doc__
        return 1
    f = ROOT.TFile(argv[1])
    tt = f.torscope_tree
    if len(argv)>2:
        ientry = int(argv[2])
    else:
        ientry = -1
    ROOT.gROOT.SetBatch(1)
    plot_tormon_traces(tt, ientry)
    f.Close()

if __name__ == "__main__":
    import sys
    main(sys.argv)
