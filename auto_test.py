import dji
from drtk import RTKadapter
import time
import shutil
import os


def comscan():
    import serial
    available = []
    for i in range(256):
        com = "com%d" % i
        try:
            s = serial.Serial(com)
            available.append(com)
            s.close()
        except serial.SerialException:
            pass
    print "available comm:",
    for port in available:
        print port, ",",
    print ""
    return available


def recv_loop():
    while True:
        msg = dev.receive_msg()


def show_menu(rtk_adpt):
    btn = raw_input("1,reboot\r\n2,enter msd mode\r\n3,show version\r\n4,print log\r\n")
    if btn == "1":
        rtk_adpt.reboot()
    if btn == "2":
        rtk_adpt.enter_msd_mode()
    if btn == "3":
        rtk_adpt.query_version()
    if btn == "4":
        recv_loop()
    if btn == "5":
        rtk_adpt.format_sd()


def run_test(adapter, repeat, timeout):
    inited = False;
    repeat_times = repeat
    state = 0

    while repeat_times > 0:
        if not inited:
            print "initializing test\r\nformatting..."
            adapter.format_sd()
            time.sleep(10)
            inited = True
            print "start test!"
        for i in range(timeout):
            time.sleep(1)
            print "loop[%d], %ds/%ds\r" % (repeat - repeat_times + 1, i, timeout),
        print "loop[%d] is done,rebooting..." % (repeat - repeat_times + 1)
        adapter.reboot()
        time.sleep(25)
        repeat_times = repeat_times - 1
    print "test sequence complete!"
    adapter.enter_msd_mode()
    time.sleep(5)
    # os.mkdir("logs\")
    shutil.copy("F:\FLY000.DAT", ".\logs")
    print "reading data..."
    print "all clear!"
    raw_input("press enter to quit")


def analyse_log():
    analysis_file = open("./logs/analysis.txt", "w")

    analysis_file.writelines("analysis for FLY000.DAT\n")


if __name__ == '__main__':
    ports = comscan()
    if ports is not None:
        port = ports[0]
    else:
        print "Holy shit, no com port!"

    dev = dji.DJI_dev(0x1e, 0x07, port, 115200, 2)
    print "dev receiver:0x%x"%dev.receiver
    rtk_adpt = RTKadapter(dev)

    # run_test(rtk_adpt, 10, 5)
    # analyse_log()
    show_menu(rtk_adpt)
