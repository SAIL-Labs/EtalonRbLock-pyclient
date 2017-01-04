#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 12:18:22 2016

@author: chrisbetters
"""

import sys
import time

import numpy as np
from numba import jit
from scipy.constants import c
from scipy.optimize import leastsq
from scipy.signal import savgol_filter
import peakutils
import peakdetect

if 'TCPIPreceiver' not in sys.modules:
    import TCPIPreceiver

# from remoteexecutor import remoteexecutor

SHOULDPLOT_RB = 0
SHOULDPLOT_etalon = 0
pRbstart = [0.1, 0.1, 0, 135, 10000, -1000]


def nm2ms(wavelengthshift, lam0=780.2):
    ms = (c * wavelengthshift * (2 * lam0 + wavelengthshift)) \
         / (2 * lam0 ** 2 + 2 * lam0 * wavelengthshift + wavelengthshift ** 2)
    return ms


def fitwavelengthscale(centers):
    peaksep_wave = np.array([0, 0.000466750976329422, 0.000307404373188547, 0.000148057835076543,
                             3.66646723932718e-05, - 0.000122681755101439, - 0.000393421157355078])
    # peaksep_freq = np.array([0, - 229.851800000000, - 151.381500000000, - 72.9112000000000,
    #                         - 18.0555500000000, 60.4147500000000, 193.740700000000])
    peaksused = np.array([4, 5, 6])
    p = np.polyfit(centers, peaksep_wave[peaksused], 1)
    return p[0]


@jit(cache=True, nopython=True)
def lorentzian(x, p):
    numerator = (p[0] ** 2)
    denominator = (x - (p[1])) ** 2 + p[0] ** 2
    y = p[2] * (numerator / denominator)
    return y


@jit(cache=True, nopython=True)
def square(x):
    return x ** 2


@jit(cache=True, nopython=True)
def LorenPart(x, ab, c, f):
    y = (1 / (1 + 4 * ((x - c) / f) ** 2)) ** ab
    return y


@jit(cache=True, nopython=True)
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


@jit(cache=True, nopython=True)
def residualsEtalon(p, y, x):
    err = y - AsymLorentzian(x, p)
    return err


@jit(cache=True, nopython=True)
def residualsRb(p, y, x):
    err = y - AsymLorentzian(x, p)
    return err


#@jit(cache=True)
def fitEtalon(x, data, decimation=1):
    centrestart = data.argmax()
    if centrestart==0:
        raise RuntimeError
    #data = savgol_filter(data, 1001, 3)
    data=data/data.max()
    p = np.array([2, 2, centrestart, 9000, 1, 0])
    print(p)
    pbest = leastsq(residualsEtalon, p, args=(data[1000:centrestart*2:decimation], x[1000:centrestart*2:decimation]), full_output=True)
    best_parameters = pbest[0]

    # if SHOULDPLOT_etalon:
    #     fit = AsymLorentzian(x, best_parameters)
    #     plt.clf()
    #     plt.show()

    return best_parameters[2]


@jit(cache=True, nopython=True)
def getRbWindow(rbdata, left=0):
    if left:
        start = np.argmax(rbdata) - 19000
    else:
        start = np.argmax(rbdata) - 2000
    finish = start + 1500

    return start, finish


def fitRblines(x, datab):
    global pRbstart
    #datab = savgol_filter(datab, 101, 3)


    datab=(datab / datab.mean() - 1)

    start, finish = getRbWindow(datab)

    datab = datab[start:finish:1]
    x = x[start:finish:1]

    # defining the 'background' part of the spectrum #
    ind_bg_low = (x > start) & (x < start + 400)
    ind_bg_high = (x > finish - 400) & (x < finish)

    x_bg = np.concatenate((x[ind_bg_low], x[ind_bg_high]))
    b_bg = np.concatenate((datab[ind_bg_low], datab[ind_bg_high]))

    # fitting the background to a line #
    pf = np.poly1d(np.polyfit(x_bg, b_bg, 5))

    # xsubwin=x[start:finish]
    # removing fitted background #
    background = pf(x)
    b_bg_corr = datab - background
    b_bg_corr=b_bg_corr/b_bg_corr.max()

    if 0:
        plt.plot(x, b_bg_corr, x, datab, x, background)
        plt.xlim(start, finish)
        plt.ylim(0, 3500)
        plt.pause(0.01)

    try:
        if 1:
            indexes = peakutils.indexes(savgol_filter(b_bg_corr, 11, 3), thres=0.2, min_dist=50)
            locs = peakutils.interpolate(x,b_bg_corr,ind=indexes,width=20)

            pks=b_bg_corr[indexes]
            return locs

        else:
            pkslocs = peakdetect.peakdetect(b_bg_corr, xsubwin, delta=100, lookahead=60)
            locs, pks = zip(*pkslocs[0])
            # pks, locs = (list(t) for t in zip(*sorted(zip(pks, locs), reverse=True)))
            sort_index = np.argsort(locs)
            locs = np.asarray(locs)[sort_index]
            pks = np.asarray(pks)[sort_index]
            locs = locs[0:6]
            pks = pks[0:6]

        if SHOULDPLOT_RB:
            plt.plot(xsubwin, b_bg_corr, locs, pks, 'go')
    except ValueError:
        print("error rbfitting")
        #print(locs)
        return [0, 0, 0]
        # plt.plot(xsubwin, b_bg_corr)

    try:
        winsize = [200, 90, 90]
        centres = np.empty(6)
        for index, loc in enumerate(locs):
            if 0:
                win = (xsubwin > loc - winsize[index]) & (xsubwin < loc + winsize[index])

                # p = [100,loc,1000]  # [hwhm, peak center, intensity] # lor
                # p = [0.1, 0.1, loc, 135, 10000, -1000]  # asymlor
                p = pRbstart
                p[2] = loc

                # optimization #
                pbest = leastsq(residualsRb, p, args=(b_bg_corr[win], xsubwin[win]), full_output=1)
                best_parameters = pbest[0]
                centres[index] = best_parameters[2]
                pRbstart = best_parameters

                # plot fit to data #
                if SHOULDPLOT_RB:
                    fit = AsymLorentzian(x[win], best_parameters)
                    plt.plot(x[win], b_bg_corr[win], x[win], fit)
                    plt.show()
                    plt.pause(0.01)
            else:
                # print(str(index) + " " + str(loc))
                centres[index] = loc
    finally:
        pass

    return centres


if __name__ == '__main__':
    from matplotlib import pyplot as plt
    from scipy import signal
    from peakutils import plot as pkplot
    import socket

    sos = np.asarray(
        [[5.80953794660816e-06, 1.16190758932163e-05, 5.80953794660816e-06, 1, -1.99516198526679, 0.995185223418579],
         [0.00240740227660535, 0.00240740227660535, 0, 1, -0.995185195446789, 0]])
    rpIP = socket.gethostbyname('redpitaya1.sail-laboratories.com')

    SHOULDPLOT_RB = 0
    SHOULDPLOT_etalon = 0
    plt.ion()
    ur = TCPIPreceiver.TCPIPreceiver(12345, 12346, 12347, 20000, rpIP)
    rbcentres = []
    etaloncentres = []

    x = np.arange(20000)
    ur.sendAckResponse(4.5)
    time.sleep(0.2)
    ur.receiveDACData()
    ur.recieveTrigerTimeAndTemp()

    # rbcentres = np.empty((6,1))
    t = time.time()
    #plt.clf()
    for i in range(0, 20):
        ur.doALL(4.5)
        # b=(ur.dataB-ur.dataB[320000])*-1.0

        # start = np.argmin(ur.dataB[0:230000])- 19000

        #start, finish = getRbWindow(ur.dataB)
        newRBcentre = fitRblines(x, ur.dataB)

        rbcentres.append(newRBcentre)

        # rbcentres=np.hstack([rbcentres,newRBcentre])

        etalondata=signal.sosfiltfilt(sos, ur.dataA)
        etaloncentre = fitEtalon(x, etalondata,30)
        etaloncentres.append(etaloncentre)
        # print(i)

    fitwavelengthscale(newRBcentre)
    elapsed = time.time() - t

    print((i + 1) / elapsed)

    plt.plot(range(0, 20), (etaloncentres - np.mean(etaloncentres)), range(0, 20),
             np.mean(rbcentres, axis=1) - np.mean(rbcentres, axis=1).mean())
    plt.plot(range(0, 20), (etaloncentres - np.mean(etaloncentres))-(np.mean(rbcentres, axis=1) - np.mean(rbcentres, axis=1).mean()))

    # del(ur)
#    errorsig = np.mean(rbcentres, axis=1) - etaloncentres
#    plt.clf()
#    plt.plot(etaloncentres - etaloncentres[0])
#    plt.plot(np.mean(rbcentres - rbcentres[0], axis=1))
#    # plt.plot(errorsig-errorsig[0])
#    plt.show()
# del ur
# centrestart=150000
#    a[ 2:21:2,:]


