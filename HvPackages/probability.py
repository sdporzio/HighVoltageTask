import math

def prob1(nMonths,tWindow,nHV,nPMT):
    tTotal = 60*60*24*30*nMonths # seconds
    nBins = tTotal/tWindow
    pGen = 1./float(nBins)

    pHV = 1 - pow((1-pGen),nHV)
    pPMT = 1 - pow((1-pGen),nPMT)
    prob = pHV * pPMT * nBins

    return prob


def prob2(nMonths,tWindow,nHV,nPMT):
    tTotal = 60*60*24*30*nMonths # seconds
    nBins = tTotal/tWindow
    pGen = 1./float(nBins)

    prob = float((nHV * tWindow))/float(tTotal)
    prob = nPMT*prob*pow((1-prob),nPMT-1)

    return prob


def prob3(nMonths,tWindow,nHV,nPMT,nCoinc):
    tTotal = 60*60*24*30*nMonths # seconds
    nBins = tTotal/tWindow
    pGen = 1./float(nBins)

    rateHV = float(nHV)/float(tTotal)
    ratePMT = float(nPMT)/float(tTotal)
    coincidenceRate = rateHV * (1 - math.exp(-1 * ratePMT*tWindow))

    average = coincidenceRate * tTotal
    prob = float(pow(average,nCoinc) * math.exp(-1*average))/float(math.factorial(nCoinc))

    return prob
