import time
import epics

pv = epics.pv.get_pv('uB_TPCDrift_HV01_torscope/waveform_raw')

def mon():
  v0=pv.get()
  t0=pv.timestamp
  while True:
    time.sleep(5)
    v1=pv.get()
    t1=pv.timestamp
    vari = sum( (v0[i]-v1[i])**2 for i in range(min(len(v0),len(v1))) )
    print t1-t0, vari

if __name__ == "__main__":
  mon()
