import numpy as np
import time
from collections import deque

class RingBuffer():

    def __init__(self):
        self.data = np.zeros(0, dtype='f')
        self.totaldataadded = 0

    def append(self, x):
        self.data = np.append(self.data,x)
        self.totaldataadded += 1

    def popleft(self):
        value = self.data[0]
        self.data = np.delete(self.data, 0)
        return value

    def clear(self):
        self.data = np.zeros(0, dtype='f')
        self.totaldataadded = 0

    def __len__(self):
        return len(self.data)


def ringbuff_numpy_testoriginial():
    start_t = time.time()
    ringlen = 0
    ringbuff = RingBuffer()
    for i in range(40):
        ringbuff.extend(np.zeros(10000, dtype='f')) # write
        ringbuff.get() #read

    fin_t = time.time() - start_t
    print('Main2: ', fin_t)


def ringbuff_numpy_test():
    start_t = time.time()
    ringlen = 0
    ringbuff = RingBuffer()

    for i in range(10000):
        ringbuff.append(np.array(i, dtype='f')) # write
        plotdata=ringbuff.data[-2000:]

    for i in range(2000):
        ringbuff.popleft() #read

    fin_t = time.time() - start_t
    print('Mainringbuff: ', fin_t)

def ringbuff_deque_test():
    start_t = time.time()
    ringbuff = deque()

    for i in range(10000):
        ringbuff.append(np.zeros(1, dtype='f')) # write
        plotdata=np.asarray(list(ringbuff))[-2000:]

    # for i in range(10000):
    #     ringbuff.popleft() #read

    fin_t = time.time() - start_t
    print('MainDeque: ', fin_t)


if __name__ == '__main__':
    ringbuff_numpy_test()
    ringbuff_deque_test()