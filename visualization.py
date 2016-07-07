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
ax = fig.add_subplot(1,1,1)

def plot_coord(f,color):
    lat0 = 0.0
    lon0 = 0.0
    inited = 0
    lat = []
    lon = []
    x = []
    y = []
    for line in f:
        if line.split(",")[0] != "[BestPos]":
            continue
        if line.split(",")[2] != "50":
            continue
        if inited == 0:
            lat0 = float(line.split(",")[3])
            lon0 = float(line.split(",")[4])
            inited = 1
        lat.append(float(line.split(",")[3]))
        lon.append(float(line.split(",")[4]))
        x.append(111195*(lat[-1]-lat0))
        y.append(111195*math.cos(lat[-1])*(lon[-1]-lon0))
                 
    minor_ticks_x = np.arange(int(min(x))-1, int(max(x))+1, 1)
    minor_ticks_y = np.arange(int(min(y))-1, int(max(y))+1, 1)
    ax.set_xticks(minor_ticks_x, minor=True)
    ax.set_yticks(minor_ticks_y, minor=True)           
    plt.grid(True, 'minor', 'both')
    plt.plot(x,y,'o',color=color)
    plt.show()

def plot_linechart(f,color):
    value_list = []

    for line in f:
        print line
        

if __name__ == '__main__':
    f = open("pvt.sol")
    plot_coord(f,"green")

             
