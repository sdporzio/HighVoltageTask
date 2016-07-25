"""histogrammer.py -- a histogram-maker for the ControlSystemStudio
rdb archive engine.

:authors: G.Horton-Smith, ...


To do:
 - retrieve data in 5000-sample-max chunks, or 1-day chunks, or something
 - replace graph of every point with graph of mean, max, min, rms.
 - make more "classy"
"""

import math
import psycopg2
import time
#import pprint
import ROOT
import array
import datetime

ROOT_CHANNEL=-999

class Histogrammer:
    """Class encapsulating various functions for retrieving data and
    calculating histograms.
    """
    def __init__(self):
        """Initialize the histogrammer -- opens the database on ifdbrep2
        [Currently the host is hard-coded, which should be fixed.]
        The smcreader password should be set in ~/.pgpass, 
        which should have mode 0600
        """
        self.conn = psycopg2.connect(host="ifdbrep2.fnal.gov", user="smcreader",
                                     port=5438,
                                     database="slowmoncon_archive")
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT channel_id,name,unit from channel natural join num_metadata;")
        rows = self.cur.fetchall()
        self.channel_name_by_id = d = dict( (int(r[0]),r[1]) for r in rows )
        self.channel_id_by_name = dict( (i[1],i[0]) for i in d.items() )
        self.channel_ids = d.keys()
        self.channel_ids.sort()
        self.unit_by_id = dict( (int(r[0]),r[2]) for r in rows )
        self.nchannel = len(self.channel_ids)
        self.datalist = []
        self.datadict = {}

    def query_unbinned_data(self, channel_id, tstart, tstop,
                              max_severity =7):
        """Get data for channel channel_id.
        tstart and tstop should be time strings in a format that
        postgresql understands (ideally ISO8601 / SQL standard), or
        a datetime object, or an integer unixtime.
        The optional max_severity parameter allows excluding samples whose
        severity status exceeds the specified value. 
        The data is not fetched.  
        The cur member of Histogrammer is the SQL cursor which may
        be used to retrieve data.
        The columns retrieved are (time, value).
        """
        if type(tstart) == int:
            tstart = datetime.datetime.fromtimestamp(tstart)
        if type(tstop) == int:
            tstop = datetime.datetime.fromtimestamp(tstop)
        query = """SELECT extract(epoch from smpl_time) as time,
float_val FROM sample
WHERE smpl_time >= %s and smpl_time < %s and channel_id = %s
and severity_id <= %s
ORDER BY time;"""
        self.cur.execute(query, (tstart, tstop, channel_id, max_severity))


    def histogram(self, channel, tstart, tstop):
        """Make a histogram of channel.  Channel can be a string or integer.
        """
        #-- convert channel to id
        if type(channel)==str:
            #-- look up string in name-to-id dictionary
            channel_id = self.channel_id_by_name[channel]
        elif type(channel)==int:
            #-- use integer directly
            channel_id = channel
        else:
            raise(Exception("Histogrammer.histogram: Bad type for channel"))
        #-- unit and short quantity name, value label
        channel_name = self.channel_name_by_id[channel_id]
        qname = channel_name[channel_name.rfind('/')+1:]
        unit = self.unit_by_id[channel_id].strip()
        #-- get chosen channel's data (t,x)
        self.query_unbinned_data(channel_id, tstart, tstop)
        xdat = list( (float(e[0]), float(e[1])) for e in self.cur.fetchall()
                     if e and e[0] and e[1])
        nxbin = len(xdat)
        if nxbin == 0:
            print "Warning, no data for %s" % channel_name
            return []
        t = list(x[0] for x in xdat)
        x = list(x[1] for x in xdat if not(math.isnan(x[1]) or math.isinf(x[1])))
        tnan = list(xdat[i][0] for i in range(nxbin) if math.isnan(xdat[i][1]))
        tinf = list(xdat[i][0] for i in range(nxbin) if math.isinf(xdat[i][1]))
        if tnan:
            print "Warning, nan in data for %s" % channel_name
        if tinf:
            print "Warning, inf in data for %s" % channel_name
        minx = min(x)
        maxx = max(x)
        mint = min(t)
        maxt = max(t)
        xlabel = '%s [%g,%g' % (qname, minx, maxx)
        if tnan:
            xlabel += " ; %d NaN" % len(tnan)
        if tinf:
            xlabel += " ; %d INF" % len(tinf)
        xlabel += ']'
        if unit:
            xlabel += ' (%s)' % (unit)
        h1 = ROOT.TH1F("h%d_%d_%d"%(channel_id,mint,maxt), 
                       "%s from %s to %s;%s" % 
                       (channel_name, tstart, tstop, xlabel),
                       100, minx, maxx)
        h1.FillN(nxbin, array.array('d',x), array.array('d',[1.0]*nxbin))
        g = ROOT.TGraph(nxbin, array.array('d', t), array.array('d', x))
        g.SetName("g%d_%d_%d"%(channel_id,mint,maxt))
        #g.SetTitle("%s from %s to %s" % (channel_name, tstart, tstop))
        xa = g.GetXaxis()
        xa.SetTimeDisplay(1)
        xa.SetTimeOffset(0)
        xa.SetTitle("%s to %s" % 
                    (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(mint)),
                     time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(maxt))) )
        ya = g.GetYaxis()
        ya.SetTitle(xlabel)
        self.datalist.append( [channel_name,h1,g,xdat,None] )
        self.datadict[channel_name] = self.datalist[-1]
        return self.datalist[-1]

    def draw(self, datalistelem):
        channel_name, h1, g = datalistelem[0:3]
        cname = "c_%s"%(h1.GetName())
        ctitle = "%s %s"%(channel_name, cname)
        c = ROOT.TCanvas(cname, ctitle)
        datalistelem[4] = c
        c.cd()
        c.Divide(1,2)
        c.cd(1)
        try:
            h1.Draw()
        except Exception,e:
            print "Warning, could not draw histo %s for %s due to %s" % (
                h1, channel_name, e)
        c.cd(2)
        try:
            g.Draw("AL")
        except Exception,e:
            print "Warning, could not draw graph %s for %s due to %s" % (
                g, channel_name, e)

    def print_all(self, filename):
        self.datalist.sort()
        nplot = len(self.datalist)
        self.datalist[0][4].Print("%s(" % filename)
        for i in range(1,nplot-1):
            self.datalist[i][4].Print("%s" % filename)
        self.datalist[-1][4].Print("%s)" % filename)


def test1():
    checklist = ["uB_DAQStatus_DAQX_evb/AvgBuilder_TrigRate_BNB",
                 "uB_DAQStatus_DAQX_evb/AvgBuilder_TrigRate_NuMI",
                 "uB_DAQStatus_DAQX_evb/AvgBuilder_TrigRate_EXT",
                 "uB_DAQStatus_DAQX_evb/AvgTrigIFDBRateRatio_BNB",
                 "uB_DAQStatus_DAQX_evb/AvgTrigIFDBRateRatio_NuMI",
                 "uB_DAQStatus_DAQX_evb/AvgSoftBuildRatio_BNB",
                 "uB_DAQStatus_DAQX_evb/AvgSoftBuildRatio_NuMI",
                 "uB_DAQStatus_DAQX_evb/AvgSoftBuildRatio_EXT_BNB",
                 "uB_DAQStatus_DAQX_evb/AvgSoftBuildRatio_EXT_NuMI",
                 "uB_DAQStatus_DAQX_evb/AvgSoftTrig_BNB_FEMBeam_Rate",
                 "uB_DAQStatus_DAQX_evb/AvgSoftTrig_NUMI_FEMBeamTrig_Rate",
                 "uB_DAQStatus_DAQX_evb/AvgSoftTrig_EXT_BNB_FEMBeam_Rate",
                 "uB_DAQStatus_DAQX_evb/AvgSoftTrig_EXT_NUMI_FEMBeam_Rate"
]
    trange = [['2016-05-18 00:00', '2016-05-22 12:00'],
              ['2016-05-28 00:00', '2016-06-01 12:00']]
    H = Histogrammer()
    for tr in trange:
        for v in checklist:
            dle = H.histogram(v, tr[0], tr[1])
            H.draw(dle)
    try:
        H.print_all("test1.pdf")
    except Exception,e:
        print e
    return H
