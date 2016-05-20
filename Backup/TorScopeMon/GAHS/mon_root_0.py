.... not working ....

import time
import epics
import root
import array

pv = epics.pv.get_pv('uB_TPCDrift_HV01_torscope/waveform_raw')

def branch1v(t, vdef):
  vname, vtype = vdef.split('/',1)
  if t.GetBranch(vname):
    return
  t = 

def get_torscope_tree():
  tt = ROOT.gDirectory.Get("torscope_tree")
  if not tt:
    tt = ROOT.TTree("torscope_tree","torscope_tree")
  branch1v(tt, "unixtime/D")
  branch1v(tt, "severity/I")
  branch1v(tt, "status/I")
  branch1v(tt, "nsamp/i")
  branch1v(tt, "trace[nsamp]/B")
  return tt

def mon():
  tt = get_torscope_tree()
  t = array.array('d',[0.0])
  sevr = array.array('i',[-1])
  stat = array.array('i',[-1])
  nsamp = array.array('I',[0])
  trace = array.array('b',[0]*10000)
  while True:
    try:
      v = pv.get(as_string=True)
      newt = pv.timestamp
      if newt == t:
        continue
      t = newt
      tt.t = t
      tt.status = pv.status
      tt.severity = pv.severity
      tt.nsamp = len(v)
      tt.trace = v
      ....
      p.pack_int(pv.status)
      p.pack_int(pv.severity)
      p.pack_string(v)
      fout.write(p.get_buffer())
      fout.flush()
      p.reset()
      time.sleep(4)
    except Exception, e:
      print e

def main(argv):
  if argv and len(argv) > 1:
    mon(file(argv[1],"ab"))
  else:
    mon(file("mon.dat","ab"))

if __name__ == '__main__':
  import sys
  main(sys.argv)

