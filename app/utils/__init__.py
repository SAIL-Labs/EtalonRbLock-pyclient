import os
from astropy.time import Time


def current_time(flatten=False, datetime=False, pretty=False):
    """ Convenience method to return the "current" time according to the system

    Returns:
        (astropy.time.Time):    `Time` object representing now.
    """

    _time = Time.now()

    if flatten:
        _time = flatten_time(_time)

    if pretty:
        _time = _time.isot.split('.')[0].replace('T', ' ')

    if datetime:
        _time = _time.datetime

    return _time


def flatten_time(t):
    """ Given an astropy Time, flatten to have no extra chars besides integers """
    return t.isot.replace('-', '').replace(':', '').split('.')[0]