#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 12:18:22 2016

@author: chrisbetters
"""

import sys
import time
import numpy as np

from scipy.optimize import leastsq
from scipy.signal import savgol_filter
import peakdetect
from numba import jit

if 'updreceiver' not in sys.modules:
    import updreceiver

# from remoteexecutor import remoteexecutor

SHOULDPLOT_RB = 0
SHOULDPLOT_etalon = 0
pRbstart = [0.1, 0.1, 0, 135, 10000, -1000]

@jit(cache=True,nopython=True)
def lorentzian(x, p):
    numerator = (p[0] ** 2)
    denominator = (x - (p[1])) ** 2 + p[0] ** 2
    y = p[2] * (numerator / denominator)
    return y


@jit(cache=True,nopython=True)
def square(x):
    return x ** 2


@jit(cache=True,nopython=True)
def LorenPart(x, ab, c, f):
    y = (1 / (1 + 4 * ((x - c) / f) ** 2)) ** ab
    return y


@jit(cache=True,nopython=True)
def AsymLorentzian(xdata, p):
    a = p[0]
    b = p[1]
    cen = p[2]
    wid = p[3]
    Amp = p[4]
    offset = p[5]

    LHS = (xdata <= cen)
    RHS = (xdata > cen)
    y = np.zeros(xdata.size)
    # fit=lorentzian(xdata,[a,cen,wid])

    y[LHS] = LorenPart(xdata[LHS], a, cen, wid)
    y[RHS] = LorenPart(xdata[RHS], b, cen, wid)

    #    plt.clf()
    #    plt.plot(xdata,y)
    #    plt.show()

    y = Amp * y + offset
    return y

@jit(cache=True,nopython=True)
def residualsEtalon(p, y, x):
    err = y - AsymLorentzian(x, p)
    return err

@jit(cache=True,nopython=True)
def residualsRb(p, y, x):
    err = y - AsymLorentzian(x, p)
    return err

@jit(cache=True)
def fitEtalon(x, data, centrestart):
    p = [1, 1, centrestart, 45000, 3200, 0]

    pbest = leastsq(residualsEtalon, p, args=(data, x), full_output=1)
    best_parameters = pbest[0]

    if SHOULDPLOT_etalon:
        fit = AsymLorentzian(x, best_parameters)
        plt.clf()
        plt.plot(x, data, x, fit)
        plt.show()

    return best_parameters[2]


def fitRblines(x, datab, start, finish):
    global pRbstart
    datab = savgol_filter(datab, 11, 3)
    xsubwin = x

    # defining the 'background' part of the spectrum #
    ind_bg_low = (x > start) & (x < start + 4000)
    ind_bg_high = (x > finish - 5000) & (x < finish)

    x_bg = np.concatenate((x[ind_bg_low], x[ind_bg_high]))
    b_bg = np.concatenate((datab[ind_bg_low], datab[ind_bg_high]))

    # fitting the background to a line #
    pf = np.poly1d(np.polyfit(x_bg, b_bg, 3))

    # xsubwin=x[start:finish]
    # removing fitted background #
    background = pf(xsubwin)
    b_bg_corr = datab - background

    if 0:
        plt.plot(x, b_bg_corr, x, datab, x, background)
        plt.xlim(start, finish)
        plt.ylim(0, 3500)
        plt.pause(0.01)

    try:
        pkslocs = peakdetect.peakdetect(b_bg_corr, xsubwin, delta=100)
        locs, pks = zip(*pkslocs[0])
        pks, locs = (list(t) for t in zip(*sorted(zip(pks, locs), reverse=True)))
        locs = locs[0:3]
        pks = pks[0:3]

        if SHOULDPLOT_RB:
            plt.plot(xsubwin, b_bg_corr, locs, pks, 'go')
    except ValueError:
        print("error rbfitting")
        #plt.plot(xsubwin, b_bg_corr)

    winsize = [250, 100, 100]
    centres = np.empty((3))
    for index, loc in enumerate(locs):
        if 1:
            win = (xsubwin > loc - winsize[index]) & (xsubwin < loc + winsize[index])
            
            # p = [100,loc,1000]  # [hwhm, peak center, intensity] # lor
            #p = [0.1, 0.1, loc, 135, 10000, -1000]  # asymlor
            p=pRbstart
            p[2]=loc

            # optimization #
            pbest = leastsq(residualsRb, p, args=(b_bg_corr[win], xsubwin[win]), full_output=1)
            best_parameters = pbest[0]
            centres[index] = best_parameters[2]
            pRbstart=best_parameters

            # plot fit to data #
            if SHOULDPLOT_RB:
                fit = AsymLorentzian(x[win], best_parameters)
                plt.plot(x[win], b_bg_corr[win], x[win], fit)
                plt.show()
                plt.pause(0.01)
        else:
            print(str(index) + " " + str(loc))
            centres[index] = loc

    return centres


if __name__ == '__main__':
    from matplotlib import pyplot as plt

    plt.ion()
    #ur = updreceiver.updreceiver(12345, 12346, 12347, 250000, "10.66.101.121")
    rbcentres = []
    etaloncentres = []

    x = np.arange(250000)
    # rbcentres = np.empty((6,1))
    t = time.time()
    for i in range(0, 1):
        ur.doALL()
        # b=(ur.dataB-ur.dataB[320000])*-1.0

        #start = np.argmin(ur.dataB[0:230000])- 19000
        
        start = np.argmin(ur.dataB[0:230000])- 8000
        print(start)
        finish = start + 15000
        newRBcentre = fitRblines(x[start:finish:1], ur.dataB[start:finish:1] * -1, start, finish)
        rbcentres.append(newRBcentre)
        # rbcentres=np.hstack([rbcentres,newRBcentre])

        centrestart = ur.dataA.argmax()
        etaloncentre = fitEtalon(x[centrestart - 40000:centrestart + 50000:1000],
                                 ur.dataA[centrestart - 40000:centrestart + 50000:1000], centrestart)
        etaloncentres.append(etaloncentre)
        # print(i)

    elapsed = time.time() - t

    print((i + 1) / elapsed)
    #del(ur)
#    errorsig = np.mean(rbcentres, axis=1) - etaloncentres
#    plt.clf()
#    plt.plot(etaloncentres - etaloncentres[0])
#    plt.plot(np.mean(rbcentres - rbcentres[0], axis=1))
#    # plt.plot(errorsig-errorsig[0])
#    plt.show()
#    # del ur
#    # centrestart=150000
##    a[ 2:21:2,:]
