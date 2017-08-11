import pickle
from app.utils.RBfitting import *
import numpy as np
from matplotlib import pyplot as plt

erlb=erlBase()
decimation=erlb.config.decimation


with open('objs.pickle','rb') as f:  # Python 3: open(..., 'rb')
    datab, x = pickle.load(f)




datab=datab-datab.mean()
datab=datab/datab.min()

start, finish = getRbWindow(datab[1:1152000//decimation])
datab = datab[start:finish:1]
x = x[start:finish:1]

t = time.time()

indexes = peakutils.indexes(-1*savgol_filter(np.diff(savgol_filter(np.diff(datab), 31, 5)), 31, 5),thres=0.33, min_dist=20)
locsfit = peakutils.interpolate(x,datab, ind=indexes, width=20, func=gaussian_fit)


elapsed = time.time() - t
print(x[indexes])
print(locsfit)
print(locsfit-x[indexes])
print('Time: {} s ({} Hz)'.format(elapsed,1 / elapsed))

# indexes = peakutils.indexes(datab, thres=0.05, min_dist=20)

# pks_sort, indexes_sort = zip(*sorted(zip(datab[indexes], indexes)))


# pplot(x,datab, np.sort(indexes_sort[-6:]))
#
# pplot(x,datab, peakutils.indexes(savgol_filter(np.diff(datab), 31, 3),thres=0.05, min_dist=20))
# pplot(x[1:], savgol_filter(np.diff(datab), 31, 3), peakutils.indexes(savgol_filter(np.diff(datab), 31, 3),thres=0.1, min_dist=20))
#
# pplot(x[0:], datab, peakutils.indexes(-1*savgol_filter(np.diff(savgol_filter(np.diff(datab), 31, 5)), 31, 5),thres=0.33, min_dist=20))
