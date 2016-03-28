"""monitor toroid scope waveforms, save to ROOT file only if interesting
trace seen"""

import ROOT
import array
import epics
import time
import datetime
import signal
import traceback

MIN_DT_FOR_RANDOM = 600
DY_CUT = 16
MAD_CUT = 4
NEWFILE_TIME = 8*3600


class TraceInfo:
  def __init__(self, ich):
    self.pv = epics.pv.get_pv('uB_TPCDrift_HV01_torscope_CH%d/waveform_raw' % ich, form='ctrl')
    self.lastt = 0
    self.lastv = []


class MonRoot:

  def __init__(self):
    self.traceinfo = [None]*4
    for ich in range(4):
      self.traceinfo[ich] = TraceInfo(ich+1)
    self.keep_running = True
    #-- nested function to handle ctrl-C
    def signal_handler(signal, frame):
      print('signal %s receieved, time to stop running' % signal)
      self.keep_running = False
    #-- install signal handler for ctrl-C
    self.signal_handler = signal_handler

    
  def mon_root(self):
    """This does the monitoring"""
    tt = ROOT.TTree("torscope_tree","torscope_tree")
    nch = len(self.traceinfo)
    maxsamp = 10000
    unixtime = array.array('d',[0.0]*nch)
    sevr = array.array('i',[-1]*nch)
    stat = array.array('i',[-1]*nch)
    nsamp = array.array('I',[0]*nch)
    trace = array.array('b',[0]*nch*maxsamp)
    miny = array.array('d',[0.0]*nch)
    maxy = array.array('d',[0.0]*nch)
    avgy = array.array('d',[0.0]*nch)
    mad0 = array.array('d',[0.0]*nch)
    tt.Branch("unixtime", unixtime, "unixtime[%d]/D" % nch)
    tt.Branch("severity", sevr,"severity[%d]/I" % nch)
    tt.Branch("status", stat, "status[%d]/I" % nch)
    tt.Branch("nsamp", nsamp, "nsamp[%d]/i" % nch)
    tt.Branch("trace", trace, "trace[%d][%d]/B" % (nch,maxsamp))
    tt.Branch("miny", miny, "miny[%d]/D" % nch)
    tt.Branch("maxy", maxy, "maxy[%d]/D" % nch)
    tt.Branch("avgy", avgy, "avgy[%d]/D" % nch)
    tt.Branch("mad0", mad0, "mad0[%d]/D" % nch)
    nevt = 0
    last_autosave_t = time.time()
    start_t = time.time()
    nevt_last_autosave = 0
    #-- set up to handle ctrl-C, etc.
    signal.signal(signal.SIGINT, self.signal_handler)
    signal.signal(signal.SIGTERM, self.signal_handler)
    signal.signal(signal.SIGHUP, self.signal_handler)
    #-- loop
    while self.keep_running:
      time.sleep(4)
      tnow = time.time()
      #-- autosave every minute, if there is anything new
      dt_autosave = tnow - last_autosave_t
      if dt_autosave >= 60 and nevt > nevt_last_autosave:
        tt.AutoSave("SaveSelf")
        last_autosave_t = tnow
        nevt_last_autosave = nevt
      #-- now get data
      new_data = False
      for ich in range(nch):
        try:
          ti = self.traceinfo[ich]
          pv = ti.pv
          v = pv.get(as_string=False)
          #-- if data is unchanged, no need to go further
          if len(v) == len(ti.lastv) and all( v[i] == ti.lastv[i] for i in range(len(v)) ):
            continue
          newt = pv.timestamp
          if newt == None:
            print "Error, timestamp was None"
            continue
          dt = newt - ti.lastt
          dlen = len(v)
          if dlen == 0:
            #print "length is zero"
            continue
          #-- convert new data to unsigned and copy to arrays in case we end up writing it
          # print "ich = %d" % ich
          # if len(v) != len(ti.lastv):
          #   print "  Unequal lengths, %d vs %d" % (len(v), len(ti.lastv))
          # else:
          #   print "  ( v == ti.lastv ) = %d" % ( (v==ti.lastv))
          #   for i in range(dlen):
          #     if (v[i] != ti.lastv[i]):
          #       print "  %d: %d %d\n" % (i, v[i], ti.lastv[i])
          # print "ich = %d, v[0:10] = %s, ti.lastv[0:10] = %s\n" % (ich, v[0:10], ti.lastv[0:10])
          trdat = array.array('b', ((i>=128 and i-256) or i for i in v))
          ti.lastv = list(x for x in v)
          avg = sum(x for x in trdat)/float(dlen)
          ydev = list(x-avg for x in trdat)
          mad = sum(abs(x) for x in ydev)/float(dlen)
          unixtime[ich] = newt
          stat[ich] = pv.status
          sevr[ich] = pv.severity
          nsamp[ich] = dlen
          trace[maxsamp*ich:maxsamp*ich+dlen] = trdat
          avgy[ich] = avg
          miny[ich] = min(ydev)
          maxy[ich] = max(ydev)
          mad0[ich] = mad
          #-- don't need this trace if maximum deviations are too small
          #   and mad is too small and dt is too small
          if ( abs(miny[ich]) < DY_CUT and maxy[ich] < DY_CUT
               and mad < MAD_CUT and dt < MIN_DT_FOR_RANDOM ):
            continue
          #-- we want new data.  Set flag and update last time
          print "New data for ich=%d: mad=%g miny=%g maxy=%g\n" % (ich, mad, miny[ich], maxy[ich])
          new_data = True
        except Exception:
          print traceback.print_exc()
      #-- end of channel loop
      if new_data:
        for ich in range(nch):
          self.traceinfo[ich].lastt = self.traceinfo[ich].pv.timestamp
        tt.Fill()
        nevt += 1
        if nevt%100 == 0:
          tt.FlushBaskets()
        print "Wrote traces at %s" % time.ctime()
      #-- exit when it's time for a new file.
      #   Start on multiples of NEWFILE_TIME
      if int(tnow/NEWFILE_TIME) > (start_t/NEWFILE_TIME):
        break
    #-- end of keep-running loop
    print "Writing TTree"
    tt.Write()

def main(argv):
  mr = MonRoot()
  while mr.keep_running:
    now = datetime.datetime.now()
    fnout = 'tormon_%s.root' % now.strftime("%Y%m%d_%H%M%S")
    print "Writing to ",fnout
    f = ROOT.TFile(fnout, "NEW")
    mr.mon_root()
    print "Closing file"
    f.Close()

if __name__ == '__main__':
  import sys
  main(sys.argv)

