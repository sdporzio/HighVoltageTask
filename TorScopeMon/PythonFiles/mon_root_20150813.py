"""monitor toroid scope waveforms, save to ROOT file only if interesting
trace seen"""

import ROOT
import array
import epics
import time
import datetime
import signal

MIN_DT_FOR_RANDOM = 600
DY_CUT = 16
MAD_CUT = 4


class MonRoot:

  def __init__(self):
    self.pv = epics.pv.get_pv('uB_TPCDrift_HV01_torscope/waveform_raw')
    self.keep_running = True
    
    def signal_handler(signal, frame):
      print('signal %s receieved, time to stop running' % signal)
      self.keep_running = False

    self.signal_handler = signal_handler

    
  def mon_root(self):
    tt = ROOT.TTree("torscope_tree","torscope_tree")
    unixtime = array.array('d',[0.0])
    sevr = array.array('i',[-1])
    stat = array.array('i',[-1])
    nsamp = array.array('I',[0])
    trace = array.array('b',[0]*10000)
    miny = array.array('d',[0.0])
    maxy = array.array('d',[0.0])
    mad0 = array.array('d',[0.0])
    tt.Branch("unixtime", unixtime, "unixtime/D")
    tt.Branch("severity", sevr,"severity/I")
    tt.Branch("status", stat, "status/I")
    tt.Branch("nsamp", nsamp, "nsamp/i")
    tt.Branch("trace", trace, "trace[nsamp]/B")
    tt.Branch("miny", miny, "miny/D")
    tt.Branch("maxy", maxy, "maxy/D")
    tt.Branch("mad0", mad0, "mad0/D")
    nevt = 0
    lastv = None
    lastt = 0
    last_autosave_t = time.time()
    nevt_last_autosave = 0
    #-- set up to handle ctrl-C, etc.
    signal.signal(signal.SIGINT, self.signal_handler)
    signal.signal(signal.SIGTERM, self.signal_handler)
    signal.signal(signal.SIGHUP, self.signal_handler)
    #-- loop
    while self.keep_running:
      try:
        time.sleep(4)
        #-- autosave every minute, if there is anything new
        dt_autosave = time.time() - last_autosave_t
        if dt_autosave >= 60 and nevt > nevt_last_autosave:
          tt.AutoSave("SaveSelf")
          last_autosave_t = time.time()
          nevt_last_autosave = nevt
        #-- now get data
        v = self.pv.get(as_string=False)
        newt = self.pv.timestamp
        if newt == lastt:
          #print "no time change"
          continue
        dt = newt - lastt
        dlen = len(v)
        if dlen == 0:
          #print "length is zero"
          continue
        lastt = newt
        lastv = v
        unixtime[0] = newt
        stat[0] = self.pv.status
        sevr[0] = self.pv.severity
        nsamp[0] = dlen
        if dlen > 0:
          # figure out if this is unsigned or signed waveform data
          trdat = array.array('b', ((i>=128 and i-256) or i for i in v))
          avgabs = sum(abs(x) for x in trdat)/float(dlen)
          if avgabs > 64.0:
            # probably unsigned data, centered around 128. Shift it.
            trdat2 = array.array('b', (i-128 for i in v))
            avgabs2 = sum(abs(x) for x in trdat2)/float(dlen)
            if avgabs2 >= avgabs:
              print "Warning, uncertain signedness in trace at ", time.ctime(newt)
              # don't use avgabs2
            else:
              trdat = trdat2
              avgabs = avgabs2
          if trdat[0:dlen] == trace[0:dlen]:
            continue
          trace[0:dlen] = trdat
        else:
          avgabs = 0.0
          continue
        mad0[0] = avgabs
        miny[0] = min(trace)
        maxy[0] = max(trace)
        # don't write trace if maximum deviations are too small
        # and mad is too small and dt is too small
        if ( abs(miny[0]) < DY_CUT and maxy[0] < DY_CUT
             and avgabs < MAD_CUT and dt < MIN_DT_FOR_RANDOM ):
          continue
        tt.Fill()
        nevt += 1
        if nevt%100 == 0:
          tt.FlushBaskets()
      except Exception, e:
        print e
    #-- end of loop
    print "Writing TTree"
    tt.Write()

def main(argv):
  now = datetime.datetime.now()
  fnout = 'tormon_%s.root' % now.strftime("%Y%m%d_%H%M%S")
  if argv:
    if len(argv) > 1:
      fnout = argv[1]
  print "Writing to ",fnout
  f = ROOT.TFile(fnout, "NEW")
  mr = MonRoot()
  mr.mon_root()
  print "Closing file"
  f.Close()

if __name__ == '__main__':
  import sys
  main(sys.argv)

