#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import time
from collections import deque


class RingBuffer():
    def __init__(self,size=0):
        self.size=size
        self.data = np.zeros(size, dtype='f')
        self.totaldataadded = 0
        if size is 0:
            self.useAppend = True
        else:
            self.useAppend = False


    def append(self, x):
        # if self.totaldataadded == 0:
        #     self.data = np.asarray(x,dtype='f')
        # else:
        #     self.data = np.append(self.data, x, axis=0)
        #
        #if self.data.shape
        if self.useAppend:
            self.data = np.append(self.data, x)
        else:
            self.data = np.vstack((self.data, x))
            if self.totaldataadded == 0:
                self.popleft()


        self.totaldataadded += 1

    def popleft(self):
        value = self.data[0]
        self.data = np.delete(self.data, 0,0)
        return value

    def pop(self):
        value = self.data[-1]
        self.data = np.delete(self.data, -1,0)
        self.totaldataadded -= 1
        return value

    def clear(self):
        self.data = np.zeros(self.size, dtype='f')
        self.totaldataadded = 0

    def __len__(self):
        return len(self.data)


def ringbuff_numpy_testoriginial():
    start_t = time.time()
    ringlen = 0
    ringbuff = RingBuffer()
    for i in range(40):
        ringbuff.extend(np.zeros(10000, dtype='f'))  # write
        ringbuff.get()  # read

    fin_t = time.time() - start_t
    print('Main2: ', fin_t)


def ringbuff_numpy_test():
    start_t = time.time()
    ringlen = 0
    ringbuff = RingBuffer()

    for i in range(10000):
        ringbuff.append(np.array(i, dtype='f'))  # write
        plotdata = ringbuff.data[-2000:]

    for i in range(2000):
        ringbuff.popleft()  # read

    fin_t = time.time() - start_t
    print('Mainringbuff: ', fin_t)


def ringbuff_deque_test():
    start_t = time.time()
    ringbuff = deque()

    for i in range(10000):
        ringbuff.append(np.zeros(1, dtype='f'))  # write
        plotdata = np.asarray(list(ringbuff))[-2000:]

    # for i in range(10000):
    #     ringbuff.popleft() #read

    fin_t = time.time() - start_t
    print('MainDeque: ', fin_t)


if __name__ == '__main__':
#    ringbuff_numpy_test()
#    ringbuff_deque_test()
    centres=np.array([1, 2, 3, 4, 5, 6])

    rbcentres=RingBuffer(size=6)

    rbcentres.append(centres)


other = RingBuffer()

other.append(np.array([1]))


