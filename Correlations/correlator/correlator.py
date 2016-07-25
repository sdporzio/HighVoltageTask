"""correlator.py -- implements a correlation-finder for the ControlSystemStudio
rdb archive engine.

:authors: G.Horton-Smith, ...
"""

import math
import psycopg2
import time
import pprint
import ROOT
import datetime

ROOT_CHANNEL=-999

class Correlator:
    """Class encapsulating various functions for retrieving data and
    calculating correlations.
    """
    def __init__(self):
        """Initialize the correlator -- opens the database on ifdbrep2
        [Currently the host is hard-coded, which should be fixed.]
        The smcreader password should be set in ~/.pgpass,
        which should have mode 0600
        """
        # self.conn = psycopg2.connect(host="ifdbrep2.fnal.gov", user="smcreader",
        #                              port=5438,
        #                              database="slowmoncon_archive")

        self.conn = psycopg2.connect(host="127.0.0.1",
                                     user="uboonedb",
                                     port=8080,
                                     database="uboonedb")

        self.cur = self.conn.cursor()
        self.cur.execute("SELECT channel_id,name from channel;")
        rows = self.cur.fetchall()
        self.channel_name_by_id = d = dict( (int(r[0]),r[1]) for r in rows )
        self.channel_id_by_name = dict( (i[1],i[0]) for i in d.items() )
        self.channel_ids = d.keys()
        self.channel_ids.sort()
        self.nchannel = len(self.channel_ids)

    # A note on the SQL query implemented in the following function:
    #  A big part of making this take reasonable time is how you make the
    #  SQL request.  The archiver database sample table is indexed first
    #  on channel_id, then on smpl_time.  If you specify a particular
    #  channel_id, then it's reasonably speedy.  If you don't, the best
    #  the server can do is to try each channel_id consecutively and then
    #  extract the samples in the requested time range for each one.
    #  A poorly chosen set of search and sort options can actually make it
    #  do much worse than that, even to the point of making it search every
    #  sample in the database for entries matching the selection criteria.
    #
    # The following 1-hour query takes about 55 seconds on
    # ifdbrep2.fnal.gov (tested on 2016/02/25):
    #
    #   select channel_id, floor(extract(epoch from smpl_time)/60) as t60,
    #      avg(float_val) from sample where smpl_time >= '2016-02-13 00:00:00'
    #      and smpl_time < '2016-02-13 1:00:00' group by channel_id,t60
    #      order by channel_id,t60;
    #
    # This returns 20591 rows from 1 hour of data.
    #     (It would be 61306 rows with no grouping.)
    # 30 minutes of data takes the same amount of time.
    #  5 minutes of data takes the same amount of time.
    #
    # If I add "and channel_id = 4483" to the where clause, it takes 2.8 ms.
    #
    # If I retrieve every channel one channel at a time, it takes 2.6 s.
    # (See test_1() below.)
    #
    def query_timebinned_data(self,channel_id, dt_s, tstart, tstop,
                              max_severity =3):
        """Get data for channel channel_id binned in steps of
        dt_s. The channel_id must be an integer.  dt_s is in seconds.
        tstart and tstop should be time strings in a format that
        postgresql understands (ideally ISO8601 / SQL standard), or
        a datetime object, or an integer unixtime.
        The optional max_severity parameter allows excluding samples whose
        severity status exceeds the specified value. The default 3 allows
        OK, MINOR, and MAJOR severity samples while excluding INVALID samples.
        The data is not fetched.
        The cur member of Correlator is the SQL cursor which may
        be used to retrieve data.
        The columns retrieved are (channel_id, tbin, avg).
        """
        if type(tstart) == int:
            tstart = datetime.datetime.fromtimestamp(tstart)
        if type(tstop) == int:
            tstop = datetime.datetime.fromtimestamp(tstop)
        query = """SELECT channel_id,
floor(extract(epoch from smpl_time)/%s) as tbin,
avg(float_val) FROM sample
WHERE smpl_time >= %s and smpl_time < %s and channel_id = %s
and severity_id <= %s
GROUP BY channel_id,tbin ORDER BY tbin;"""
        self.cur.execute(query, (dt_s, tstart, tstop, channel_id, max_severity))

    def query_root(self, rootfnvar, dt_s, tstart, tstop):
        """Make a histogram from a TTree::Draw in a root file and use it as data.
        Syntax of rootfnvar:
            rootdraw:filename;tree;expression;cut;option
        E.g.
            rootdraw:myfile.root;torscope_tree;unixtime;unixtime>12345678
        or
            rootdraw:myfile.root;torscope_tree;mad0:unixtime;unixtime>12345678;PROF
        """
        pieces = rootfnvar.split(';')
        fn = pieces[0][9:]
        treename, expr = pieces[1:3]
        cut = len(pieces)>3 and pieces[3] or ""
        option = len(pieces)>4 and pieces[4] or ""
        # quantize start time down to dt_s boundary
        tstart = math.floor(tstart/dt_s)*dt_s
        nbin = int(math.ceil((tstop-tstart)/dt_s))
        tstop = tstart + nbin*dt_s
        if 'prof' in option.lower():
            hist_1 = ROOT.TProfile("hist_1", "hist_1", nbin, tstart, tstop)
        else:
            hist_1 = ROOT.TH1F("hist_1","hist_1", nbin, tstart, tstop)
        f = ROOT.TFile(fn)
        tree = f.Get(treename)
        ROOT.gROOT.SetBatch(1)
        ROOT.gROOT.cd()
        tree.Draw(expr+" >>+hist_1", cut, option)
        #for i in xrange(hist_1.GetNbinsX()+1):
        #  print hist_1.GetBinCenter(i)
        #  print hist_1.GetBinContent(i)
        xdat = list( (math.floor(hist_1.GetBinCenter(i+1)/dt_s), hist_1.GetBinContent(i+1)) for i in range(nbin) )
        #print xdat
        #raw_input()
        return xdat


    def correlate1(self, channel, dt_s, tstart, tstop):
        """Get the correlation coefficients of a given channel with
        all channels.  channel may be an integer or a string.  dt_s
        is in seconds.  tstart and tstop should be time strings in a
        format that postgresql understands (ideally ISO8601 / SQL
        standard), or a datetime object.
        The correlation coefficient calculated is sample-weighted
        rather than time-weighted. Only time bins where both variables
        have a sample in the same time bin are used.
        The data returned is list of (zscore, corr, n, id, name) tuples,

        where corr is the correlation coefficient,
        n is the number of same-time-bin samples found,
        id is the channel id, name is the channel name,
        zscore is the number of standard deviations of significance.
        See
          https://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient#Using_the_Fisher_transformation
          https://en.wikipedia.org/wiki/Standard_score

        Note: it is the same number of queries to get the correlation of all
        channels, although it requires more memory.  If a master correlation
        matrix of all variables is desired, it would be more efficient to
        refactor this function rather than calling it once for each channel.
        """
        #-- convert channel to id
        if type(channel)==str:
            #-- is this a root file query?
            if channel.startswith("rootdraw:"):
                channel_id = ROOT_CHANNEL
            else:
                #-- look up string in name-to-id dictionary
                channel_id = self.channel_id_by_name[channel]
        elif type(channel)==int:
            #-- use integer directly
            channel_id = channel
        else:
            raise(Exception("Correlator.correlate: Bad type for channel"))
        #-- get chosen channel's data (t,x)
        if channel_id == ROOT_CHANNEL:
            xdat = self.query_root(channel, dt_s, tstart, tstop)
        else:
            self.query_timebinned_data(channel_id, dt_s, tstart, tstop)
            xdat = list( (int(e[1]), float(e[2])) for e in self.cur.fetchall()
                     if e and e[1] and e[2])
        nxbin = len(xdat)
        if nxbin == 0:
            return []
        #-- get other channels' data and build correlation and covariance
        corr_data = [(0.0, 0.0, 0, 0, '')]*self.nchannel
        for i in range(self.nchannel):
            cid1 = self.channel_ids[i]
            self.query_timebinned_data(cid1, dt_s, tstart, tstop)
            ydat = list( (int(e[1]), float(e[2])) for e in self.cur.fetchall()
                         if e and e[1] and e[2])
            nybin = len(ydat)
            if nybin == 0:
                corr_data[i] = (0.0, 0.0, 0, cid1, self.channel_name_by_id[cid1])
            else:
                cor, n, xyt = cor_xy(xdat, ydat)
                if n <= 3:
                    z = 0.0
                elif abs(cor) >= 1.0:
                    z = cor*float('inf')
                else:
                    z = math.atanh(cor) * math.sqrt(n-3)
                corr_data[i] = (z, cor, n, cid1, self.channel_name_by_id[cid1])
        return corr_data


def cor_xy(xdat, ydat):
    """Given two sparse lists [(id,xdat),...] and [(id,ydat),...],
    sorted in order of increasing id, find the correlation coefficient
      corr = <dx dy> / (stddev(dx)*stddev(dy))
    using only entries with common ids.
    Returns (corr, n, xytdat), where corr is as defined above,
    n is the number of samples, and xytdat is the list of (x,y,id) for the
    common ids.  Returns corr=0 if n <= 1.  Meaningless for n <= 2.
    """
    #*** Note this could be made faster using scipy or numpy, but I have
    # not found either on uboonegpvm03.  Anyway, it is plenty fast as is.

    #-- make a list of common samples
    xytdat = []
    i = j = 0
    while i<len(xdat) and j<len(ydat):
        if xdat[i][0] == ydat[j][0]:
            xytdat.append( (xdat[i][1], ydat[j][1], xdat[i][0]) )
            i += 1
            j += 1
        elif xdat[i][0] > ydat[j][0]:
            j += 1
        else:
            i += 1
    n = len(xytdat)
    #-- return early if not enough common samples to make a correlation
    if n <= 1:
        return (0.0, n, [])
    #-- compute the correlation coefficient
    xmean = sum(xy[0] for xy in xytdat)/float(n)
    ymean = sum(xy[1] for xy in xytdat)/float(n)
    dxydat = list( (xy[0]-xmean, xy[1]-ymean) for xy in xytdat)
    vxx = sum(d[0]*d[0] for d in dxydat)
    #-- early exit if there is no variance
    if vxx == 0.0:
        return (0.0, n, [])
    vyy = sum(d[1]*d[1] for d in dxydat)
    if vyy == 0.0:
        return (0.0, n, [])
    #-- finally we are at the end
    cxy = sum(d[0]*d[1] for d in dxydat)
    cor = cxy/(vxx*vyy)**0.5
    return (cor, n, xytdat)


def test_1():
    """A test function for the data retrieval.
    Retrieves all data in a 1-hour period for channels 1 through 4483,
    one channel at a time.
    """
    c = Correlator()
    timing_data = []
    for channel_id in range(1,4484):
        t0 = time.time()
        c.query_timebinned_data(channel_id, 60, '2016-02-13 00:00:00', '2016-02-13 01:00:00')
        result = c.cur.fetchall()
        dt = time.time()-t0
        timing_data.append( (channel_id, len(result), dt) )
    pprint.pprint( timing_data )
    return timing_data


def test_2():
    """A test function for the 1-to-all correlation function correlate1().
    Retrieves all data for a 1-day period and finds correlation coefficients
    for correlations of any variable with
    uB_TPCDrift_HV01_keithleyPickOff/voltDiff5s60s
    and the corresponding z-score significances of the correlations.
    """
    c = Correlator()
    cor = c.correlate1('uB_TPCDrift_HV01_keithleyPickOff/voltDiff5s60s',
                       60, '2016-02-13 00:00:00', '2016-02-14 00:00:00')
    pprint.pprint( cor )
    return cor, c

def test3():
    c = Correlator()
    cor = c.correlate1("rootdraw:/uboone/app/users/afurmans/HVmonitoringAnalysis/toroidStuff/torscope_files/torscope_all.root;torscope_tree;unixtime;unixtime>0",43200,1458000000, 1461500000)

    pprint.pprint(cor)
    return cor

def test4():
    c = Correlator()
    xdat = c.query_root("rootdraw:/uboone/app/users/afurmans/HVmonitoringAnalysis/toroidStuff/torscope_files/torscope_all.root;torscope_tree;unixtime[0];unixtime[0]>0",3600,1461100000, 1461300000)

    pprint.pprint(xdat)
    return xdat
