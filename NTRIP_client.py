import socket
import base64
import time
import datetime
from functools import reduce
import operator
from generate_sol import SolGenerator
from RTCMv3_decode import decode_rtcm3_from_net, set_generator

# dummyNMEA = "$GPGGA,100429.20,2232.1120000,N,11356.5668000,E,1,00,1.0,3.428,M,-3.428,M,0.0,*5C"

username = "P_dji1"  # username for RTCM correction service
password = "efb136d"  # password for RTCM correction service
# my_host = "rtk.qxwz.com"
# port = 8001  # port for the service
my_host = "127.0.0.1"
port = 50007  # port for the service
mount_point = "RTCM32_GGB"

'''Generate an encoding of the username:password for the service.
The string must be first encoded in ascii to be correctly parsed by the
base64.b64encode function.'''
pwd = base64.b64encode("{}:{}".format(username, password).encode('ascii'))

# The following decoding is necessary in order to remove the b' character that
# the ascii encoding add. Othrewise said character will be sent to the net and misinterpreted.
pwd = pwd.decode('ascii')


# header = \
#     "GET /mountpoint HTTP/1.1\r\n" + \
#     "Host my_host\r\n" + \
#     "Ntrip-Version: Ntrip/1.0\r\n" + \
#     "User-Agent: ntrip.py/0.1\r\n" + \
#     "Accept: */*" + \
#     "Connection: close\r\n" + \
#     "Authorization: Basic {}\r\n\r\n".format(pwd)

header = \
    "GET /%s HTTP/1.1\r\n" % mount_point + \
    "User-Agent: NTRIP_client.py/0.1\r\n" + \
    "Authorization: Basic {}\r\n\r\n".format(pwd)


def nmea_checksum(nmea_str):
    return reduce(operator.xor, map(ord, nmea_str), 0)


def generate_gga():
    # str1 = "GPGGA,133622.69,2232.1120000,N,11356.5668000,E,1,00,1.0,3.428,M,-3.428,M,0.0,"
    tst = datetime.datetime.utcnow().strftime("%H%M%S.00,")
    gga_str = "GPGGA," + tst + "2232.1120000,N,11356.5668000,E,1,00,1.0,3.428,M,-3.428,M,0.0,"
    # gga_str = "GPGGA,133622.69,2232.1120000,N,11356.5668000,E,1,00,1.0,3.428,M,-3.428,M,0.0,"
    gga_str += '*%02X' % nmea_checksum(gga_str)
    gga_str = '$' + gga_str
    print gga_str
    return gga_str


def recv_from_svr(s):
    f = open("ntrip.sol", "w")
    f_log = open("qxwz_rtcm32_ggb.log", "wb")
    sg = SolGenerator(f)
    set_generator(sg)
    while True:
        dat = s.recv(2048)

        if len(dat) > 0:
            print len(dat)
            f_log.writelines(dat)
            decode_rtcm3_from_net(dat)


def run_rcver(s):
    import threading

    print "begin recver thread..."
    t = threading.Thread(target=recv_from_svr, args=(s,))
    t.start()


class NTRIPclient:
    def __init__(self, request_handle, mount_point, pass_phrase):
        self.status = "init"
        self.connected = False
        self.source_caster = request_handle.server
        self.buff = ''
        self.mount_point = mount_point
        self.lat = 0.0
        self.lon = 0.0
        self.alt = 0.0
        self.pass_phrase = pass_phrase

    def push_data(self, data):
        self.buff += data

    def get_data(self):
        send_buff = self.buff
        self.flush()
        return send_buff

    def flush(self):
        self.buff = ''

    def auth_check(self):

        return True





if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((my_host, int(port)))

    print("Header sending... \n")
    s.send(header.encode('ascii'))

    print("Waiting answer...\n")
    data = s.recv(12).decode('ascii')
    print(data)
    run_rcver(s)


    while True:
        # generate_gga()
        s.send(generate_gga().encode('ascii'))
        s.send('\r\n\r\n')
        # s.send(dummyNMEA.encode('ascii'))
        # print "dummy GGA sent"
        # data = s.recv(1024)  # .decode('ascii')
        # print len(data)
        # f.write(data)
        # print(data)
        time.sleep(5)

    s.close()