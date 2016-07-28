import dji
from drtk import RTKadapter
import time
import shutil
from unpack_logfile import parse_logfile
import os

port = None
STOP_SIGNAL = False


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


def comscan_continuous(caller):
    import serial
    available = []
    print "scanning for available com port by", caller
    while True:
        for i in range(32):
            com = "com%d" % i
            try:
                s = serial.Serial(com)
                print "found port:", com
                return com
            except serial.SerialException:
                pass


def create_dir_by_time():
    dirname = "log_" + time.strftime("%Y%m%d%H%M%S", time.localtime())
    os.mkdir("./logs/%s" % dirname)
    return dirname


def recv_loop(dev):
    while True:
        msg = dev.comm_dev.receive_msg()
        time.sleep(1)


def run_receiver():
    import threading

    dev = get_rtk_dev()
    t = threading.Thread(target=recv_loop, args=(dev,))
    t.start()


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


def launch_test(repeat, timeout):
    repeat_times = repeat
    state = 0
    global STOP_SIGNAL

    adapter = get_rtk_dev()
    if adapter == -1:
        print "get rtk dev error!"
        return

    print "initializing test\r\nformatting..."
    adapter.format_sd()
    STOP_SIGNAL = False
    time.sleep(10)
    print "start test!"

    while repeat_times > 0:
        if STOP_SIGNAL:
            return
        for i in range(timeout):
            if STOP_SIGNAL:
                return
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


def run_test(loops, timeout):
    import threading

    t = threading.Thread(target=launch_test, args=(loops, timeout))
    t.start()


class TestControl:
    def __init__(self, target=None, loops=0, timeout=0):
        self.running = False
        self.idle = True
        self.target = target
        self.loops_remain = loops
        self.loop = 0
        self.timeout = timeout

    def de_init(self):
        adapter = get_rtk_dev()
        if adapter == -1:
            print "get rtk dev error!"
            return
        self.target = adapter

    def set_target(self, target):
        self.target = target

    def set_sequence(self, loops, timeout):
        self.loops_remain = loops
        self.timeout = timeout

    def start_test(self):
        self.running = True
        self._do_test()

    def run_test(self):
        import threading

        t = threading.Thread(target=self.start_test)
        t.start()

    def stop_test(self):
        self.running = False

    def is_running(self):
        return self.running

    def _sleep(self, sec):
        self.idle = True
        time.sleep(sec)
        self.idle = False

    def _do_test(self):
        if self.target is None:
            return

        adapter = self.target
        self.loop = 1
        print "initializing test\r\nformatting..."
        adapter.format_sd()
        self._sleep(10)

        print "start test!"

        while self.loops_remain > 0:
            if not self.running:
                print "stop by operator"
                return
            for i in range(self.timeout):
                if not self.running:
                    print "stop by operator"
                    return
                self._sleep(1)
                print "loop[%d], %ds/%ds\r" % (self.loop, i + 1, self.timeout),
            print "loop[%d] is done,rebooting..." % self.loop
            adapter.reboot()
            adapter.close()
            self._sleep(4)
            adapter = get_rtk_dev()
            self._sleep(20)
            self.loop += 1
            self.loops_remain -= 1
        print "test sequence complete!"
        adapter.enter_msd_mode()
        self._sleep(5)
        _dir = create_dir_by_time()
        for n in range(self.loops_remain):
            shutil.copy("F:\FLY%.3d.DAT" % n, ".\logs\%s" % _dir)
        print "reading data..."
        print "all clear!"


def stop_test():
    global STOP_SIGNAL
    STOP_SIGNAL = True


def get_com_dev():
    ports = comscan()
    if len(ports) > 0:
        # print ports
        return ports[0]
    else:
        print "Holy shit, no com port!"
        return -1


def get_rtk_dev():
    global port
    # port = get_com_dev()
    if port is None:
        port = comscan_continuous("auto-test")
    if port == -1:
        return -1
    dev = dji.DJI_dev(0x1a, 0x07, port, 115200, 2)
    # print "dev receiver:0x%x" % dev.receiver
    rtk_adpt = RTKadapter(dev)
    return rtk_adpt


def test_serial_min():
    adapter = get_rtk_dev()
    for i in range(20):
        print "interval:", 9 - i,
        adapter.reboot()
        time.sleep(9 - i)
        adapter = get_rtk_dev()
        if adapter == -1:
            print "fail"
        else:
            print "success"


if __name__ == '__main__':
    tc = TestControl(loops=10, timeout=300)
    tc.de_init()
    tc.run_test()
    # run_receiver()
    # dev = get_rtk_dev()
    # recv_loop(dev)
    # run_test(4, 20)
    # show_menu(rtk_adpt)
    # dev = get_rtk_dev()
    # dev.enter_msd_mode()
    # time.sleep(5)
    # for n in range(4):
    #     shutil.copy("F:\FLY%.3d.DAT" % n, ".\logs")
    # print create_dir_by_time()
    # s = comscan_continuous()
    # print s
    # test_serial_min()
