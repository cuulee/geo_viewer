import time
import dji
# import drtk
from threading import Thread

# PORT = '/dev/ttyACM2'
PORT = 'com3'
BAUD = 115200

def recv_loop(dev):
    while True:
        msg = dev.receive_msg()
        # time.sleep(1)

if __name__ == '__main__':
    dev = dji.DJI_dev(0x1a, 0x07, PORT, BAUD, 2)
    # rtk_adpt = drtk.RTKadapter(dev)

    t = Thread(target=recv_loop, args=(dev,))
    t.setDaemon(True)
    t.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        dev.close()
        print "\ndev closed"


