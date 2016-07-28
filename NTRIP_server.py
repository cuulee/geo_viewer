import serial
import socket
import time

class NTRIPserver:
    def __init__(self, request_handle=None, mount_point=None, host="127.0.0.1", port=50007):
        self.status = "init"
        self.connected = False
        self.target_caster = request_handle
        self.buf = ''
        self.lat = 0.0
        self.lon = 0.0
        self.alt = 0.0
        self.mount_point = mount_point
        self.connection = None
        self.remote = (host, port)


    def cache(self, data):
        self.buf = data

    def flush(self):
        self.buf = ''

    def connect(self):
        print "connecting to caster:", self.remote
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.remote)
        s.sendall(req_ntrip_source())
        print s.recv(1024)
        self.connection = s
        self.connected = True

    def shutdown(self):
        self.connection.close()
        pass

def req_ntrip_source():
    passwd = "123456"
    mount = "RTCM32_GGB"
    lat = "22.63901900"
    lon = "113.81104800"
    alt = "3.85"
    req = \
        "SOURCE {} {}\r\n".format(passwd, mount) + \
        "Source-Agent: pyCaster/0.1\r\n" + \
        "STR: lat {} lon {} alt {}\r\n\r\n".format(lat,lon,alt)
    return req

if __name__ == '__main__':
    svr = NTRIPserver()
    svr.connect()
    serial = serial.Serial('/dev/ttyUSB0', 115200)
    while True:
        data = serial.read(1024)
        if len(data) > 0:
            svr.connection.sendall(data)
