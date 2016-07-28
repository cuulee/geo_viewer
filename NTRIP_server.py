

passwd = "123456"
mount = "RTCM32_GGB"

header = "SOURCE %s %s\r\n" % (passwd, mount) + \
         "Source-Agent: pyCaster/0.1\r\n" + \
         "STR: come and use this source!\r\n\r\n"


class NTRIPserver:
    def __init__(self, request_handle, mount_point):
        self.status = "init"
        self.connected = False
        self.target_caster = request_handle.server
        self.buf = ''
        self.lat = 0.0
        self.lon = 0.0
        self.alt = 0.0
        self.mount_point = mount_point

    def cache(self, data):
        self.buf = data

    def flush(self):
        self.buf = ''

