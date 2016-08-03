import numpy as np
import matplotlib.pyplot as plt
import math
import random


# fig.add_subplot(2,2,3)
# fig.add_subplot(2,2,4)


def plot_bestpos(f):
    fig = plt.figure(figsize=(10, 8))
    fig.suptitle(f.name)
    fig.canvas.set_window_title(f.name)
    a1 = fig.add_subplot(2, 2, 1)
    a2 = fig.add_subplot(2, 2, 2)
    a3 = fig.add_subplot(2, 2, 3)
    a4 = fig.add_subplot(2, 2, 4)

    lat0 = 0.0
    lon0 = 0.0
    inited1 = 0
    inited2 = 0
    lat_fix = []
    lon_fix = []
    x = []
    y = []
    x_float = []
    y_float = []
    x_single = []
    y_single = []
    ms_diff = []
    rtkTrkSVs = []
    rtkSolSVs = []
    ttff = 0
    postype = []
    narrowInt_cnt = 0
    total_cnt = 1

    for line in f:
        if line.split(",")[0] != "[BestPos]":
            continue

        type, _solStt, _posType, _lat, _lon, _hgt, _undulation, _trkSVs, _solSVs, _ms = line.split(",")
        solStt, posType, undulation, trkSVs, solSVs, ms = map(int, (_solStt, _posType, _undulation, _trkSVs, _solSVs, _ms))
        lat, lon, hgt = map(float, (_lat, _lon, _hgt))

        if inited1 == 0:
            time_start = ms
            last_ms = time_start
            inited1 = 1
        else:
            total_cnt += 1.0
        postype.append(posType)
        rtkTrkSVs.append(trkSVs)
        rtkSolSVs.append(solSVs)
        ms_diff.append(ms - last_ms)
        last_ms = ms
        if posType < 48:
            if inited2 == 0:
                # continue
                pass
            if posType >= 32:
                x_float.append(111195 * (lat - lat0))
                y_float.append(111195 * math.cos(lat) * (lon - lon0))
            if posType == 16:
                x_single.append(111195 * (lat - lat0))
                y_single.append(111195 * math.cos(lat) * (lon - lon0))
            continue
        narrowInt_cnt += 1.0
        if inited2 == 0:
            lat0 = lat
            lon0 = lon
            ttff = (ms - time_start) / 1000
            inited2 = 1
        lat_fix.append(lat)
        lon_fix.append(lon)
        x.append(111195 * (lat_fix[-1] - lat0))
        y.append(111195 * math.cos(lat_fix[-1]) * (lon_fix[-1] - lon0))

    if len(x) > 0:
        minor_ticks_x = np.arange(int(min(x)) - 1, int(max(x)) + 1, 1)
        minor_ticks_y = np.arange(int(min(y)) - 1, int(max(y)) + 1, 1)
        a1.set_xticks(minor_ticks_x, minor=True)
        a1.set_yticks(minor_ticks_y, minor=True)
    plt.subplot(2, 2, 1, aspect=1)
    plt.title('position cloud')
    plt.grid(True, 'minor', 'both')
    plt.plot(x, y, 'o', color='green')
    plt.plot(x_float, y_float, 'o', color='purple')
    plt.plot(x_single, y_single, 'o', color='yellow')

    plt.subplot(2, 2, 2)
    plt.title('PosType (TTFF=%ds, fixRate=%f)' % (ttff, narrowInt_cnt / total_cnt))
    a2.set_ylim(0, 55)
    minor_ticks_y = np.arange(0, 55, 1)
    a2.set_yticks(minor_ticks_y, minor=True)
    plt.grid(True, 'minor', 'both')
    a2.plot(postype)

    plt.subplot(2, 2, 3)
    plt.title('packet time diff')
    a3.set_ylim(-800, 1000)
    a3.plot(ms_diff)

    plt.subplot(2, 2, 4)
    plt.title('trk/sol SVs')
    a4.plot(rtkTrkSVs, color="blue")
    a4.plot(rtkSolSVs, color="green")

    pic = "." + f.name.split(".")[1] + ".png"

    plt.savefig(pic, format='png')
    # plt.show()
    plt.close()


def plot_MSM(f):
    fig = plt.figure(figsize=(10, 8))
    fig.suptitle(f.name)
    fig.canvas.set_window_title(f.name)
    a1 = fig.add_subplot(2, 2, 1)
    a2 = fig.add_subplot(2, 2, 2)
    a3 = fig.add_subplot(2, 2, 3)

    gps_diff = []
    glo_diff = []
    bds_diff = []

    last_gps_tow = 0
    last_glo_tow = 0
    last_bds_tow = 0

    for line in f:
        if line.split(",")[0] != "[MSM5]":
            continue

        msm_type = line.split(",")[1]

        if msm_type == '1075':
            gps_diff.append(int(line.split(",")[2]) - last_gps_tow)
            last_gps_tow = int(line.split(",")[2])

        if msm_type == '1085':
            glo_diff.append(int(line.split(",")[2]) - last_glo_tow)
            last_glo_tow = int(line.split(",")[2])

        if msm_type == '1125':
            bds_diff.append(int(line.split(",")[2]) - last_bds_tow)
            last_bds_tow = int(line.split(",")[2])

    plt.subplot(2, 2, 1)
    plt.title('GPS packet time diff')
    a1.set_ylim(-1, 10)
    a1.plot(gps_diff)

    plt.subplot(2, 2, 2)
    plt.title('GLO packet time diff')
    a2.set_ylim(-1, 10)
    a2.plot(glo_diff)

    plt.subplot(2, 2, 3)
    plt.title('BDS packet time diff')
    a3.set_ylim(-1, 10)
    a3.plot(bds_diff)

    pic = "." + f.name.split(".")[1] + "_lost" + ".png"
    plt.savefig(pic, format='png')
    plt.close()


def plot_random():
    fig = plt.figure(figsize=(10, 8))
    a1 = fig.add_subplot(1, 3, 1)
    a2 = fig.add_subplot(1, 3, 2)
    a3 = fig.add_subplot(1, 3, 3)

    x_rtk_cloud = 2 * (np.random.random(100) - 0.5)
    y_rtk_cloud = 2 * (np.random.random(100) - 0.5)
    x_dgps_cloud = 80 * (np.random.random(100) - 0.5)
    y_dgps_cloud = 80 * (np.random.random(100) - 0.5)
    x_single_clout = 1000 * (np.random.random(100) - 0.5)
    y_single_clout = 1000 * (np.random.random(100) - 0.5)

    a1.set_xlim(-500,500)
    a1.set_ylim(-500, 500)
    a2.set_xlim(-500, 500)
    a2.set_ylim(-500, 500)
    a3.set_xlim(-500, 500)
    a3.set_ylim(-500, 500)
    a1.plot(x_rtk_cloud, y_rtk_cloud,'o', color="green")
    a2.plot(x_dgps_cloud, y_dgps_cloud,'o', color="green")
    a3.plot(x_single_clout, y_single_clout,'o', color="green")

    plt.show()


def plot_linechart(f, color):
    value_list = []

    for line in f:
        print line


if __name__ == '__main__':
    # f = open("pvt.sol")
    # plot_bestpos(f, "green")
    plot_random()
