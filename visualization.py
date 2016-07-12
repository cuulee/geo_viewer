import numpy as np
import os
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import math
import string
import tkFileDialog
from decimal import Decimal

fig = plt.figure()
fig.suptitle('holy')
ax = fig.add_subplot(2, 2, 1)
ay = fig.add_subplot(2, 2, 2)
fig.add_subplot(2,2,3)
fig.add_subplot(2,2,4)


def plot_coord(f, color):
    lat0 = 0.0
    lon0 = 0.0
    inited = 0
    lat = []
    lon = []
    x = []
    y = []
    ms = []
    ttff = 0
    postype = []
    narrowInt_cnt = 0
    total_cnt = 1

    time_start = int(f.readline().split(",")[9])
    last_ms = time_start
    for line in f:
        if line.split(",")[0] != "[BestPos]":
            continue
        if inited:
            total_cnt += 1.0
        postype.append(line.split(",")[2])
        ms.append(int(line.split(",")[9]) - last_ms)
        last_ms = int(line.split(",")[9])
        if line.split(",")[2] != "50":
            continue
        narrowInt_cnt += 1.0
        if inited == 0:
            lat0 = float(line.split(",")[3])
            lon0 = float(line.split(",")[4])
            ttff = (int(line.split(",")[9]) - time_start) / 1000
            inited = 1
        lat.append(float(line.split(",")[3]))
        lon.append(float(line.split(",")[4]))
        x.append(111195 * (lat[-1] - lat0))
        y.append(111195 * math.cos(lat[-1]) * (lon[-1] - lon0))

    minor_ticks_x = np.arange(int(min(x)) - 1, int(max(x)) + 1, 1)
    minor_ticks_y = np.arange(int(min(y)) - 1, int(max(y)) + 1, 1)
    ax.set_xticks(minor_ticks_x, minor=True)
    ax.set_yticks(minor_ticks_y, minor=True)
    plt.subplot(221)
    plt.title('position cloud')
    plt.grid(True, 'minor', 'both')
    plt.plot(x, y, 'o', color=color)

    plt.subplot(222)
    plt.title('PosType (TTFF=%ds, fixRate=%f)' % (ttff, narrowInt_cnt / total_cnt))
    ay.set_ylim(0, 55)
    minor_ticks_y = np.arange(0, 55, 1)
    ay.set_yticks(minor_ticks_y, minor=True)
    plt.grid(True, 'minor', 'both')
    plt.plot(postype)

    plt.subplot(223)
    plt.title('packet time diff')
    plt.plot(ms)

    plt.subplot(224)
    plt.title('cnr average')


    plt.show()


def plot_linechart(f, color):
    value_list = []

    for line in f:
        print line


if __name__ == '__main__':
    f = open("pvt.sol")
    plot_coord(f, "green")
