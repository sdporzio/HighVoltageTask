import ROOT
import array
import xdrlib
import time


def mon_xdr_to_root(fin):
  p1 = xdrlib.Unpacker([])
  p2 = xdrlib.Unpacker([])
  tt = ROOT.TTree("torscope_tree","torscope_tree")
  t = array.array('d',[0.0])
  sevr = array.array('i',[-1])
  stat = array.array('i',[-1])
  nsamp = array.array('I',[0])
  trace = array.array('b',[0]*10000)
  packetlen = array.array('I',[0])
  mad0 = array.array('d',[0.0])
  tt.Branch("unixtime", t, "unixtime/D")
  tt.Branch("severity", sevr,"severity/I")
  tt.Branch("status", stat, "status/I")
  tt.Branch("nsamp", nsamp, "nsamp/i")
  tt.Branch("trace", trace, "trace[nsamp]/B")
  tt.Branch("packetlen", packetlen, "packetlen/i")
  tt.Branch("mad0", mad0, "mad0/D")
  totsize = 0
  nevt = 0
  lastv = ''
  while True:
    data1 = fin.read(4)
    if len(data1) == 0:
      print "End of data"
      break
    if len(data1) < 4:
      print "Error, truncated data at packet length. %d read" % len(data1)
      break
    totsize += 4
    p1.reset(data1)
    p2len = p1.unpack_uint()
    if p2len <= 0:
      print "Error, non-positive packet length"
      break
    data2 = fin.read(p2len)
    totsize += p2len
    if len(data2) < p2len:
      print "Error, truncated data. %d read where %d expected" % (
        len(data2), p2len)
    p2.reset(data2)
    t[0] = p2.unpack_double()
    stat[0] = p2.unpack_int()
    sevr[0] = p2.unpack_int()
    dlen = p2.unpack_uint()
    if dlen > 0:
      v = p2.unpack_fopaque(dlen)
    else:
      v = ''
    if v == lastv:
      continue
    lastv = v
    nsamp[0] = dlen
    if dlen > 0:
      # figure out if this is unsigned or signed waveform data
      trdat = array.array('b',v)
      avgabs = sum(abs(x) for x in trdat)/float(dlen)
      if avgabs > 64.0:
        trdat = array.array('b', list(ord(x)-128 for x in v))
        avgabs = sum(abs(x) for x in trdat)/float(dlen)
        if avgabs > 64.0:
          print "Warning, uncertain signedness in trace at ", time.ctime(t[0])
      trace[0:dlen] = trdat
    else:
      avgabs = 0.0
    mad0[0] = avgabs
    packetlen[0] = p2len
    tt.Fill()
    nevt += 1
  tt.Write()
  print "total bytes read: ", totsize
  print "number of entries written: ", nevt
  print "number of entries in tree: ", tt.GetEntries()

def main(argv):
  fnin = 'mon.dat'
  fnout = 'mon.root'
  if argv:
    if len(argv) > 1:
      fnin = argv[1]
    if len(argv) > 2:
      fnout = argv[2]
  f = ROOT.TFile(fnout, "UPDATE")
  mon_xdr_to_root(file(fnin,"rb"))
  f.Close()

if __name__ == '__main__':
  import sys
  main(sys.argv)

