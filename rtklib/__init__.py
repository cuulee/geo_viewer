from ctypes import *
import os
import time
import sys


#dll = CDLL(os.getcwd() + "/rtklib.so")



def getbitu(buff,pos,b_len):
    size = len(buff)
    in_buff = c_char_p(buff)
    # in_buff.from_buffer(buff)

    retval = rtklib.getbitu(in_buff,pos,b_len)
    return retval

def getbits(buff,pos,b_len):
    size = len(buff)
    in_buff = c_char_p(buff)
    # in_buff.from_buffer(buff)

    retval = rtklib.getbits(in_buff,pos,b_len)
    return retval

class RetVal(object):
    def __init__(self,buff,pos,bitlen):
        self.buff = buff
        self.pos = pos
        self.bitlen = bitlen

    @property
    def uint(self):
        ret = getbitu(self.buff,self.pos,self.bitlen)
        return ret

    @property
    def int(self):
        ret = getbits(self.buff,self.pos,self.bitlen)
        return ret

class Bits(object):
    def __init__(self,buff=''):
        self._buff = buff
        self.idx = 0
        

    def append(self,byte):
        self._buff += byte
        # print "current Bits buff len:",len(self._buff)

    def read(self,len): # read len of bits data and return the value
        ret = RetVal(self._buff,self.idx,len)
        self.idx+=len
        return ret

    def from_buffer(self,buff):
        self._buff = buff
        self.idx = 0

class RTCMResolver(object):
    def __init__(self):
        pass

    def input(self,buff):
        # self.buff += buff
        size = len(buff)
        in_buff = c_char_p(buff)
        bytes_processed = rtklib.resolve_rtcm3(in_buff,size)
        print "rtklib processed:",bytes_processed

def resolve_rtcm3_c(buff):
    c_uint_p = POINTER(c_uint32)
    size = len(buff)
    in_buff = c_char_p(buff)
    progress = c_uint32(bar.progress)
    p_progress = c_uint_p(progress)
    # p_progress = POINTER(progress)
    # logfile = "rtklib_test.sol"
    # f_p = c_char_p(logfile)
    # rtklib.log_open(f_p)
    rtklib.resolve_rtcm3(in_buff,size,p_progress)
    # print "rtklib processed:",bytes_processed

def log_open_c(type,fn):
    fn_p = c_char_p(fn)
    _type = c_uint32(type)
    rtklib.log_open(_type,fn_p)

def log_close_c(type):
    _type = c_uint32(type)
    rtklib.log_close(_type)


class LogListener(object):
    def __init__(self):
        self.buff = ' '*256
        self.len = 0
        self.cnt = 0
        self.last_cnt = 0
        self.lock = True

    def poll_msg(self):
        while True:
        #     if self.lock:
        #         continue
        #     self.lock = True
        #     if self.cnt != self.last_cnt:
        #         self.last_cnt = self.cnt
        #         logger.log(self.buff[:len]
            data = c_char_p(self.buff)
            length = c_void_p(self.len)
            rtklib.pop_log(data,length)
            log_buff = self.buff[:self.len]
            logger.push(log_buff)
            rtklib.log_done()
        # time.sleep()

    def start(self):
        import threading

        t = threading.Thread(target=self.poll_msg)

        t.start()


if __name__ == '__main__':
    import sys
    sys.path.append("..")
    from logger import get_logger,get_progress_bar

    dll_path = os.getcwd() + "/rtklib.dll"
    rtklib = cdll.LoadLibrary(dll_path)

    logger = get_logger()
    bar = get_progress_bar()

    buff = "this that"
    print buff
    # bs = Bits()
    # bs.append(buff[0])
    # bs.append(buff[1])
    # print bs.read(4)
    # while True:
    #     print rtklib.timeget()
    #     time.sleep(1)
    size = len(buff)
    in_buff = c_char_p(buff)
    rtklib.test_call(in_buff,size)
    print buff
    rtklib.log_test()
    # rtklib.printf("hello world")
else:
    # sys.path.append('./rtklib')
    dll_path = os.getcwd() + "./rtklib/rtklib.dll"
    rtklib = cdll.LoadLibrary(dll_path)
    from logger import get_logger,get_progress_bar
    logger = get_logger()
    bar = get_progress_bar()








        
    # raw_input()
