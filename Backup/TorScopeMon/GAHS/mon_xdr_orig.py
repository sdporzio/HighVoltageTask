import time
import epics
import xdrlib

pv = epics.pv.get_pv('uB_TPCDrift_HV01_torscope/waveform_raw')

def mon(fout):
  p1 = xdrlib.Packer()
  p2 = xdrlib.Packer()
  t = 0
  while True:
    try:
      v = pv.get(as_string=True)
      newt = pv.timestamp
      if newt == t:
        continue
      t = newt
      p2.pack_double(t)
      p2.pack_int(pv.status)
      p2.pack_int(pv.severity)
      p2.pack_string(v)
      p1.pack_string(p2.get_buffer())
      fout.write(p1.get_buffer())
      fout.flush()
      p1.reset()
      p2.reset()
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

