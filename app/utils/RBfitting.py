#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 12:18:22 2016

@author: chrisbetters
"""

import sys
import time

import numpy as np
#from numba import jit
from scipy.constants import c
from scipy.optimize import leastsq, least_squares
from scipy import optimize
from scipy.signal import savgol_filter
import peakutils
from peakutils.plot import plot as pplot
#from matplotlib import pyplot as plt
eps = np.finfo(float).eps

from . import peakdetect
from ..comms.TCPIPreceiver import TCPIPreceiver
from .. import erlBase

erlb = erlBase()
decimation = erlb.config.decimation

# from remoteexecutor import remoteexecutor

SHOULDPLOT_RB = 0
SHOULDPLOT_etalon = 0
pRbstart = [0.1, 0.1, 0, 135, 10000, -1000]
#from matplotlib import pyplot as plt


def nm2ms(wavelengthshift, lam0=780.2):
    """ Converts a wavelength (nm) difference to velocity (m/s)

    :param wavelengthshift: differential wavelength change/shift
    :param lam0: reference wavelength for velocity conversion
    :return:  velocity
    """

    ms = (c * wavelengthshift * (2 * lam0 + wavelengthshift)) \
        / (2 * lam0 ** 2 + 2 * lam0 * wavelengthshift + wavelengthshift ** 2)
    return ms


def fitwavelengthscale(centers):
    """

    :param centers:
    :return:
    """
    peaksep_wave = np.array([0, 0.000466750976329422, 0.000307404373188547, 0.000148057835076543,
                             3.66646723932718e-05, - 0.000122681755101439, - 0.000393421157355078])
    # peaksep_freq = np.array([0, - 229.851800000000, - 151.381500000000, - 72.9112000000000,
    #                         - 18.0555500000000, 60.4147500000000, 193.740700000000])
    peaksused = np.array([2, 3, 4, 5, 6])
    p = np.polyfit(centers, peaksep_wave[peaksused], 1)
    return p[0]


#@jit(cache=True, nopython=True)
def lorentzian(x, p):
    """

    :param x:
    :param p:
    :return:
    """
    numerator = (p[0] ** 2)
    denominator = (x - (p[1])) ** 2 + p[0] ** 2
    y = p[2] * (numerator / denominator)
    return y


#@jit(cache=True, nopython=True)
def square(x):
    """

    :param x:
    :return:
    """
    return x ** 2


#@jit(cache=True, nopython=True)
def LorenPart(x, ab, c, f):
    """

    :param x:
    :param ab:
    :param c:
    :param f:
    :return:
    """
    y = (1 / (1 + 4 * ((x - c) / f) ** 2)) ** ab
    return y


#@jit(cache=True, nopython=True)
def AsymLorentzian(xdata, p):
    """

    :param xdata:
    :param p:
    :return:
    """
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


#@jit(cache=True, nopython=True)
def residualsEtalon(p, y, x):
    """

    :param p:
    :param y:
    :param x:
    :return:
    """

    err = y - AsymLorentzian(x, p)
    return err


#@jit(cache=True, nopython=True)
def residualsRb(p, y, x):
    """

    :param p:
    :param y:
    :param x:
    :return:
    """
    err = y - AsymLorentzian(x, p)
    return err


# @jit(cache=True)
def fitEtalon(x, data, dec=1):
    """

    :param x:
    :param data:
    :param dec:
    :return:
    """
    centrestart = data.argmax()
    if centrestart == 0:
        raise RuntimeError
    #data = savgol_filter(data, 1001, 3)
    data = data / data.max()
    p = np.array([1.5, 1.5, centrestart, 0.42 *
                  erlb.config.aquisitionsize, 1, 0.03])
    # print(p)
    # pbest = leastsq(residualsEtalon, p, args=(data[centrestart-5000:centrestart+5000:dec], x[centrestart-5000:centrestart+5000:dec]), full_output=True)
    # best_parameters = pbest[0]

    #pbest = least_squares(residualsEtalon, p, args=(data[centrestart-8000:centrestart+8000:dec], x[centrestart - 8000:centrestart + 5000:dec]), method='lm')
    if 0:
        pbest = least_squares(residualsEtalon, p, args=(
            data[::dec], x[::dec]), method='lm')
        best_parameters = pbest.x
    else:
        best_parameters, pcov = optimize.curve_fit(
            AsymLorentzianAlt, x[::dec], data[::dec], p)

    # print(best_parameters)

    # if SHOULDPLOT_etalon:
    #     fit = AsymLorentzian(x, best_parameters)
    #     plt.plot(x,fit,x,data)
    #     plt.clf()
    #     plt.show()

    return best_parameters[2]


# @jit(cache=True)
def getRbWindow(rbdata, left=1, pk_thres=0.3, pk_min_dist=50):
    """

    :param rbdata:
    :param left:
    :return:
    """
    centre = min(peakutils.indexes(savgol_filter(rbdata, 501, 1),
                                   thres=pk_thres, min_dist=pk_min_dist))
    #pplot(range(len(rbdata)),rbdata,peakutils.indexes(rbdata, thres=0.6,min_dist=1000))
    if left:
        start = centre - 60000 // decimation
    else:
        start = np.argmax(rbdata) - 256000 // decimation
    finish = start + 120000 // decimation
    #pyplot.figure(figsize=(10, 6))
    #pplot(np.linspace(0, len(rbdata), len(rbdata)), rbdata, np.asarray([start, centre, finish], dtype=np.int))
    return int(start), int(finish)
    #
    #pplot(np.linspace(0, len(rbdata), len(rbdata)), savgol_filter(rbdata,501,3), peakutils.indexes(savgol_filter(rbdata,501,3), thres=0.2,min_dist=50))


def fitRblines(x, datab, numpeaks=3, sf_window_length=31, sf_polyorder=5):
    locs = np.zeros(numpeaks)

    datab = datab - datab.mean()
    datab = datab / datab.min()

    start, finish = getRbWindow(datab[1:1152000 // decimation])

    datab = datab[start:finish:1]
    x = x[start:finish:1]

    RbDeriv = savgol_filter(np.diff(savgol_filter(datab, 31, 5)), 61, 5)

    s = np.sign(RbDeriv)
    s[s == 0] = -1  # replace zeros with -1
    zero_crossings = np.where(np.diff(s))[0]

    zero_crossings = zero_crossings[s[zero_crossings - 1]
                                    > s[zero_crossings + 1]]

    pks_sort, indexes_sort = zip(
        *sorted(zip(datab[zero_crossings], zero_crossings)))
    locs[0:numpeaks] = np.sort(x[np.asarray(indexes_sort)[-numpeaks:]])

    #locs = peakutils.interpolate(x, datab, ind=indexes_sort[-numpeaks:], width=2560 // decimation, func=loren_fit)

    return locs


def fitRblinesAlt(x, datab):
    """plt.plot(x, b_bg_corr, x, datab, x, background)

    :param x:
    :param datab:
    :return:
    """
    global pRbstart
    #datab = savgol_filter(datab, 101, 3)

    #datab=(datab / datab.mean() - 1)
    datab = datab - datab.mean()
    datab = datab / datab.min()

    start, finish = getRbWindow(datab[1:1152000 // decimation])

    datab = datab[start:finish:1]
    x = x[start:finish:1]

    if 1:
        locs = np.zeros(3)
        indexes = peakutils.indexes(-1 * savgol_filter(np.diff(savgol_filter(np.diff(savgol_filter(datab, 31, 5)), 31, 5)), 31, 5), thres=0.45,
                                    min_dist=20)
        locs[0:3] = x[indexes]
        return locs

    # defining the 'background' part of the spectrum #
    ind_bg_low = (x >= start) & (x < (start + 51200 // decimation))
    ind_bg_high = (x > finish - 32000 // decimation) & (x <= finish)

    x_bg = np.concatenate((x[ind_bg_low], x[ind_bg_high]))
    b_bg = np.concatenate((datab[ind_bg_low], datab[ind_bg_high]))

    # fitting the background to a line #
    pf = np.poly1d(np.polyfit(x_bg, b_bg, 4))

    # xsubwin=x[start:finish]
    # removing fitted background #
    background = pf(x)
    b_bg_corr = datab - background
    b_bg_corr = b_bg_corr / b_bg_corr.max()

    if 0:
        plt.plot(x, b_bg_corr, x, datab, x, background)
        plt.xlim(start, finish)
        plt.ylim(0, 3500)
        plt.pause(0.01)

    # try:
    if 0:
        locs = np.zeros(6)
        pks = np.zeros(6)

        indexes = peakutils.indexes(savgol_filter(
            datab, 101, 3), thres=0.05, min_dist=20)
        pks_sort, indexes_sort = zip(*sorted(zip(b_bg_corr[indexes], indexes)))
        #locsfit = peakutils.interpolate(x,b_bg_corr, ind=indexes, width=2560//decimation, func=loren_fit)
        #pyplot.figure(figsize=(10, 6))
        #pplot(np.linspace(0,len(b_bg_corr),len(b_bg_corr)),b_bg_corr, indexes)
        locs[0:6] = x[np.sort(indexes_sort[-6:])]
        #locs[0:6] = locsfit
        pks[0:6] = b_bg_corr[np.sort(indexes_sort[-6:])]
        return locs

    else:
        pkslocs = peakdetect.peakdetect(
            b_bg_corr, erlb.config.xsubwin, delta=100, lookahead=60)
        locs, pks = zip(*pkslocs[0])
        # pks, locs = (list(t) for t in zip(*sorted(zip(pks, locs), reverse=True)))
        sort_index = np.argsort(locs)
        locs = np.asarray(locs)[sort_index]
        pks = np.asarray(pks)[sort_index]
        locs = locs[0:6]
        pks = pks[0:6]

    if SHOULDPLOT_RB:
        plt.plot(erlb.config.xsubwin, b_bg_corr, locs, pks, 'go')
    # except ValueError:
    #     print("error rbfitting")
    #     print(locs)
    #     return np.asarray([0, 0, 0])
    #     # plt.plot(xsubwin, b_bg_corr)

    try:
        winsize = [200, 90, 90]
        centres = np.empty(6)
        for index, loc in enumerate(locs):
            if 0:
                win = (erlb.config.xsubwin > loc -
                       winsize[index]) & (erlb.config.xsubwin < loc + winsize[index])

                # p = [100,loc,1000]  # [hwhm, peak center, intensity] # lor
                # p = [0.1, 0.1, loc, 135, 10000, -1000]  # asymlor
                p = pRbstart
                p[2] = loc

                # optimization #
                pbest = leastsq(residualsRb, p, args=(
                    b_bg_corr[win], erlb.config.xsubwin[win]), full_output=1)
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


#@jit(cache=True, nopython=True)
def gaussian(x, ampl, center, dev, d):
    '''Computes the Gaussian function.

    Parameters
    ----------
    x : number
        Point to evaluate the Gaussian for.
    a : number
        Amplitude.
    b : number
        Center.
    c : number
        Width.

    Returns
    -------
    float
        Value of the specified Gaussian at *x*
    '''
    return ampl * np.exp(-(x - float(center)) ** 2 / (2.0 * dev ** 2 + eps)) + d


def gaussian_fit(x, y, center_only=True):
    '''Performs a Gaussian fitting of the specified data.

    Parameters
    ----------
    x : ndarray
        Data on the x axis.
    y : ndarray
        Data on the y axis.
    center_only: bool
        If True, returns only the center of the Gaussian for `interpolate` compatibility

    Returns
    -------
    ndarray or float
        If center_only is `False`, returns the parameters of the Gaussian that fits the specified data
        If center_only is `True`, returns the center position of the Gaussian
    '''
    initial = [np.max(y), x[np.argmax(y)], (x[1] - x[0]) * 10, 0]
    params, pcov = optimize.curve_fit(gaussian, x, y, initial)
    #plt.plot(x, y, x, gaussian(x,params[0],params[1],params[2],params[3]))
    if center_only:
        return params[1]
    else:
        return params


def loren_fit(x, y, center_only=True):
    '''Performs a Gaussian fitting of the specified data.

    Parameters
    ----------
    x : ndarray
        Data on the x axis.
    y : ndarray
        Data on the y axis.
    center_only: bool
        If True, returns only the center of the Gaussian for `interpolate` compatibility

    Returns
    -------
    ndarray or float
        If center_only is `False`, returns the parameters of the Gaussian that fits the specified data
        If center_only is `True`, returns the center position of the Gaussian
    '''
    initial = [1, 1, x[np.argmax(y)], (x[1] - x[0]) * 40, np.max(y), 0]
    params, pcov = optimize.curve_fit(AsymLorentzianAlt, x, y, initial)
    #plt.plot(x, y, x, gaussian(x,params[0],params[1],params[2],params[3]))
    if center_only:
        return params[2]
    else:
        return params


#@jit(cache=True, nopython=True)
def AsymLorentzianAlt(xdata, a, b, cen, wid, Amp, offset):
    """

    :param xdata:
    :param p:
    :return:
    """
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
