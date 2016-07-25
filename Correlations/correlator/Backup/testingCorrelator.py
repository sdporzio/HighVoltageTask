import correlator
c = correlator.Correlator()
print "Starting analysis"
corr_data = c.correlate1('uB_TPCDrift_HV01_keithleyPickOff/voltDiff5s60s',60, '2016-02-13 00:00:00', '2016-02-13 00:00:20')
print corr_data
