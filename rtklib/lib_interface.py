from ctypes import *
from rtklib import rtklib, logger, bar

def getbitu(buff, pos, b_len):
    size = len(buff)
    in_buff = c_char_p(buff)
    retval = rtklib.getbitu(in_buff, pos, b_len)
    return retval


def getbits(buff, pos, b_len):
    size = len(buff)
    in_buff = c_char_p(buff)
    retval = rtklib.getbits(in_buff, pos, b_len)
    return retval


class RetVal(object):

    def __init__(self, buff, pos, bitlen):
        self.buff = buff
        self.pos = pos
        self.bitlen = bitlen

    @property
    def uint(self):
        ret = getbitu(self.buff, self.pos, self.bitlen)
        return ret

    @property
    def int(self):
        ret = getbits(self.buff, self.pos, self.bitlen)
        return ret


class Bits(object):

    def __init__(self, buff = ''):
        self._buff = buff
        self.idx = 0

    def append(self, byte):
        self._buff += byte

    def read(self, len):
        ret = RetVal(self._buff, self.idx, len)
        self.idx += len
        return ret

    def from_buffer(self, buff):
        self._buff = buff
        self.idx = 0


class RTCMResolver(object):

    def __init__(self):
        pass

    def input(self, buff):
        size = len(buff)
        in_buff = c_char_p(buff)
        bytes_processed = rtklib.resolve_rtcm3(in_buff, size)
        print 'rtklib processed:', bytes_processed


def resolve_rtcm3_c(buff):
    c_uint_p = POINTER(c_uint32)
    size = len(buff)
    in_buff = c_char_p(buff)
    rtklib.resolve_rtcm3(in_buff, size)


def log_open_c(type, fn):
    fn_p = c_char_p(fn)
    _type = c_uint32(type)
    rtklib.log_open(_type, fn_p)


def log_close_c(type):
    _type = c_uint32(type)
    rtklib.log_close(_type)


class LogListener(object):

    def __init__(self):
        self.buff = ' ' * 256
        self.len = 0
        self.cnt = 0
        self.last_cnt = 0
        self.lock = True

    def poll_msg(self):
        while True:
            data = c_char_p(self.buff)
            length = c_void_p(self.len)
            rtklib.pop_log(data, length)
            log_buff = self.buff[:self.len]
            logger.push(log_buff)
            rtklib.log_done()

    def start(self):
        import threading
        t = threading.Thread(target=self.poll_msg)
        t.start()


def get_process_c():
    return rtklib.get_process()

