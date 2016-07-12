import dji
from drtk import RTKadapter
import time
import shutil
from unpack_logfile import parse_logfile
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
    print "available comm:", available
    # for port in available:
    #     print port, ",",
    # print ""
    return available

def comscan_continuous():
    import serial
    available = []
    while True:
        for i in range(32):
            com = "com%d" % i
            try:
                s = serial.Serial(com)
                return com
            except serial.SerialException:
                pass

def create_dir_by_time():
    dirname = "log_" + time.strftime("%Y%m%d%H%M%S", time.localtime())
    os.mkdir("./logs/%s" % dirname)
    return dirname


def recv_loop(dev):
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


def run_test(repeat, timeout):
    repeat_times = repeat
    state = 0

    adapter = get_rtk_dev()
    if adapter == -1:
        print "get rtk dev error!"
        return

    print "initializing test\r\nformatting..."
    adapter.format_sd()
    time.sleep(10)
    print "start test!"

    while repeat_times > 0:
        for i in range(timeout):
            time.sleep(1)
            print "loop[%d], %ds/%ds\r" % (repeat - repeat_times + 1, i + 1, timeout),
        print "loop[%d] is done,rebooting..." % (repeat - repeat_times + 1)
        adapter.reboot()
        adapter.close()
        time.sleep(4)
        adapter = get_rtk_dev()
        time.sleep(20)
        repeat_times = repeat_times - 1
    print "test sequence complete!"
    adapter.enter_msd_mode()
    time.sleep(5)
    # os.mkdir("logs\")
    dir = create_dir_by_time()
    for n in range(repeat):
        shutil.copy("F:\FLY%.3d.DAT" % n, ".\logs\%s" % dir)
    print "reading data..."
    print "all clear!"
    raw_input("press enter to quit")


def analyse_log():
    analysis_file = open("./logs/analysis.txt", "w")

    analysis_file.writelines("analysis for FLY000.DAT\n")

    parse_logfile("./logs/")


def get_com_dev():
    ports = comscan()
    if len(ports) > 0:
        # print ports
        return ports[0]
    else:
        print "Holy shit, no com port!"
        return -1


def get_rtk_dev():
    # port = get_com_dev()
    port = comscan_continuous()
    if port == -1:
        return -1
    dev = dji.DJI_dev(0x1a, 0x07, port, 115200, 2)
    # print "dev receiver:0x%x" % dev.receiver
    rtk_adpt = RTKadapter(dev)
    return rtk_adpt


def test_serial_min():
    adapter = get_rtk_dev()
    for i in range(20):
        print "interval:",9-i,
        adapter.reboot()
        time.sleep(9-i)
        adapter = get_rtk_dev()
        if adapter == -1:
            print "fail"
        else:
            print "success"

if __name__ == '__main__':
    run_test(4, 20)
    analyse_log()
    # show_menu(rtk_adpt)
    # dev = get_rtk_dev()
    # dev.enter_msd_mode()
    # time.sleep(5)
    # for n in range(4):
    #     shutil.copy("F:\FLY%.3d.DAT" % n, ".\logs")
    # print create_dir_by_time()
    # s = comscan_continuous()
    # print s
    #test_serial_min()
