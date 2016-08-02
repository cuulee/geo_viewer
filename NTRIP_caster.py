import socket
import SocketServer
import time
import datetime
import Queue
from NTRIP_client import NTRIPclient
from NTRIP_server import NTRIPserver

HOST = "10.80.57.162"
PORT = 50007
# rf = open("qxwz_rtcm32_ggb.log", "rb")

class RequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        print '...connected from:', self.client_address
        header = self.request.recv(1024).strip()
        header_info = decode_ntrip_header(header)
        print header_info
        if header_info is None:
            return
            # self.finish()

        if header_info[0] is 'server':
            ntrip_svr = NTRIPserver(self, header_info[1])
            caster.add_server(ntrip_svr)
            self.request.sendall("ICY 200 OK")
        elif header_info[0] is 'client':
            ntrip_clt = NTRIPclient(self, header_info[1], header_info[4])
            caster.add_client(ntrip_clt)
            self.request.sendall(get_client_resp().encode('ascii'))
        while True:
            if header_info[0] is 'server':
                data = self.request.recv(256).strip()
                if data is not None:
                    ntrip_svr.cache(data)
                    caster.bytes_rcved += len(data)
                    print "received:{} sent:{}".format(caster.bytes_rcved, caster.bytes_sent)
                # self.request.sendall('[%s] %s' % (time.ctime(), data))
                # self.client_address
                # print data
            elif header_info[0] is 'client':
                # print "here in a loop for client"
                # data = self.request.recv(1024).strip()
                # handle_ntrip_client_data(data)
                resp = ntrip_clt.get_data()
                # resp = rf.read(256)
                # print len(resp)
                if resp is not None:
                    # print "{}bytes sent to client".format(len(resp))
                    self.request.sendall(resp)
                    caster.bytes_sent += len(resp)
                    # time.sleep(0.2)
            else:
                pass


def handle_ntrip_client_data(data):
    pass


def get_client_resp():
    timephr = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
    ack = \
        "ICY 200 OK\r\n" + \
        "Server: POP_GW_Ntrip_1.0_1467449209/1.0\r\n".format(caster.name) + \
        "Via: n4_2\r\n" + \
        "Date: {}\r\n".format(timephr) + \
        "Connection: keep-alive\r\n\r\n"
    return ack


def decode_ntrip_header(buff):
    if "GET" in buff:
        role = 'client'

    elif "SOURCE" in buff:
        role = 'server'
    else:
        role = None

    if role is 'server':
        source = buff.split('\r\n')
        passwd = source[0].split(' ')[1]
        mount_point = source[0].split(' ')[2]
        agent = source[1].split(' ')[1]
        ext_str = source[2].split(' ')[1]
        return role, mount_point, passwd, agent, ext_str

    elif role is 'client':
        request = buff.split('\r\n')
        mount_point = request[0].split(' ')[1]
        agent = request[1].split(' ')[1]
        auth_type = request[2].split(' ')[1]
        auth_phrase = request[2].split(' ')[2]
        return role, mount_point, agent, auth_type, auth_phrase

    return None


class NTRIPcaster:
    def __init__(self, host="0.0.0.0", server_port=50007, client_port=50008, max_server=1, max_client=1,
                 name="C_DJI_NTRIP_1.0_2938"):
        self.running = False
        self.servers = []
        self.clients = []
        self.address_svr = (host, server_port)
        self.address_clt = (host, client_port)
        self.max_server = max_server
        self.max_client = max_client
        self.svr_handle = None
        self.clt_handle = None
        self.name = name
        self.bytes_rcved = 0
        self.bytes_sent = 0

    def run_svr_handle(self):
        handle = SocketServer.ThreadingTCPServer(self.address_svr, RequestHandler)
        print 'waiting for Ntrip servers...'
        self.svr_handle = handle

        handle.serve_forever()

    def run_clt_handle(self):
        handle = SocketServer.ThreadingTCPServer(self.address_clt, RequestHandler)
        print 'waiting for Ntrip clients...'
        self.clt_handle = handle

        handle.serve_forever()

    def run_all(self):
        from threading import Thread

        t2 = Thread(target=self.run_svr_handle)
        t2.setDaemon(True)
        t2.start()

        self.running = True

        t1 = Thread(target=self.run_router)
        t1.setDaemon(True)
        t1.start()

        t3 = Thread(target=self.run_clt_handle)
        t3.setDaemon(True)
        t3.start()



    def run_router(self):
        while True:
            if not self.running:
                # svr.shutdown()
                # print "not running"
                break
            for s in self.servers:
                for c in self.clients:
                    trans = s.get_data()
                    if trans is None:
                        # print "no data to be sent"
                        continue
                    if s.mount_point == c.mount_point:
                        # print "mount point match!"
                        while trans is not None:
                        # print "[{}][{},{}]".format(time.ctime(),s.mount_point, c.mount_point)
                            c.push_data(trans)
                            trans = s.get_data()


            # print "servers:{},clients:{}".format(len(self.servers), len(self.clients))
            # time.sleep(1)

    def stop(self):
        self.running = False

    def add_server(self, svr):
        self.servers.append(svr)

    def add_client(self, clt):
        self.clients.append(clt)

    def shutdown(self):
        self.running = False



if __name__ == '__main__':
    caster = NTRIPcaster()
    caster.run_all()
    while True:
        pass
