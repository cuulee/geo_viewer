import socket
import SocketServer
from time import ctime
import datetime
from NTRIP_client import NTRIPclient
from NTRIP_server import NTRIPserver



class RequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        print '...connected from:', self.client_address
        header = self.request.recv(1024).strip()
        header_info = decode_ntrip_header(header)
        print header_info
        if header_info is None:
            self.finish()

        if header_info[0] is 'server':
            ntrip_svr = NTRIPserver(self, header_info[1])
            caster.add_server(ntrip_svr)
        elif header_info[0] is 'client':
            ntrip_clt = NTRIPclient(self, header_info[1], header_info[4])
            caster.add_client(ntrip_clt)
            self.request.sendall(get_client_resp())
        while True:
            if header_info[0] is 'server':
                data = self.request.recv(1024).strip()
                ntrip_svr.cache(data)
                self.request.sendall('[%s] %s' % (ctime(), data))
                # self.client_address
                print data
            elif header_info[0] is 'client':
                data = self.request.recv(1024).strip()
                handle_ntrip_client_data(data)
                resp = ntrip_clt.get_data()
                if len(resp) > 0:
                    self.request.sendall(resp)
            else:
                pass


def handle_ntrip_client_data(data):
    pass


def get_client_resp():
    timephr = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
    ack = \
        "ICY 200 OK\r\n" + \
        "Server: {} \r\n".format(caster.name) + \
        "Via: n4_2\r\n" + \
        "Date: {}\r\n".format(timephr) + \
        "Connection: keep-alive\r\n\r\n"
    return ack

def decode_ntrip_header(buff):
    if "GET" in buff:
        role = 'client'

    elif "SOURCE" in buff:
        role = 'server'

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
    def __init__(self, host="127.0.0.1", server_port=50007, client_port=50008, max_server=1, max_client=1, name="C_DJI_NTRIP_1.0_2938"):
        self.running = False
        self.servers = []
        self.clients = []
        self.address_svr = (host, server_port)
        self.address_clt = (host, client_port)
        self.max_server = max_server
        self.max_client = max_client
        self.svr = None
        self.name = name

    def run(self):
        svr = SocketServer.ThreadingTCPServer(self.address_svr, RequestHandler)
        print 'waiting for connection...'
        svr.serve_forever()
        self.svr = svr
        self.running = True

        while True:
            if not self.running:
                svr.shutdown()
                break

    def stop(self):
        self.running = False

    def add_server(self, svr):
        self.servers.append(svr)

    def add_client(self, clt):
        self.clients.append(clt)

    def shutdown(self):
        self.running = False


caster = NTRIPcaster()

if __name__ == '__main__':
    caster.run()
