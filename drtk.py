import dji


class RTKadapter:
    def __init__(self, comm_dev):
        self.inited = True
        self.activated = True
        self.baseLat = 0.0
        self.baseLon = 0.0
        self.baseHgt = 0.0
        self.comm_dev = comm_dev

    def reboot(self):
        self.comm_dev.send_msg(0x0a, 0x00, 0x0b, payload="")

    def query_status(self):
        self.comm_dev.send_msg(0x0a, 0x00, 0x0c, payload="")

    def query_version(self):
        self.comm_dev.send_msg(0x0a, 0x00, 0x01, payload="")

    def enter_msd_mode(self):
        self.comm_dev.send_msg(0x0a, 0x03, 0x39, payload="")
        self.comm_dev.close()

    def format_sd(self):
        import struct
        self.comm_dev.send_msg(0x0a, 0x03, 0x3a, payload=struct.pack("<b", 1))

    def close(self):
        self.comm_dev.close()
        self.comm_dev = None


class RTKcore:
    def __init__(self, comm_dev):
        self.inited = False
        self.comm_dev = comm_dev

    def reboot(self):
        self.comm_dev.send_msg(0x0a, 0xde, 0x00, 0x0b, payload="")

    def query_version(self):
        self.comm_dev.send_msg(0x0a, 0xde, 0x00, 0x0b, payload="")
