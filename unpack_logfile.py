import struct
from generate_sol import resolve_v1, unpack_record
from rtcm.RTCMv3_decode import resolve_rtcm3
import tkFileDialog
import os
import time

bytes_processed = 0

def calc_process(fsize):
    global bytes_processed
    while bytes_processed < fsize:
        pct = bytes_processed * 100.0 / fsize
        print "processed: %{}\r".format(pct),
        time.sleep(1)

def start_calc(fsize):
    import threading
    
    t = threading.Thread(target = calc_process,args=(fsize,))
    t.setDaemon(True)
    t.start()

def parse_v1log(fn_in,fsize):
    cnt = 100000
    buff_len = 1024*64
    remain = ""
    global bytes_processed

    bytes_processed = 0
    f = open(fn_in,'rb')

    start_calc(fsize)
    while cnt>0:
        cnt = cnt-1
        buff = f.read(buff_len)
        if buff is None:
            break
        remain = resolve_v1(remain+buff, unpack_record)
        bytes_processed += len(buff)
    print "done!"
    f.close()

def parse_rtcm3log(fn_in,fsize):
    cnt = 100000
    buff_len = 1024*64
    remain = ""
    global bytes_processed

    f = open(fn_in,'rb')
    start_calc(fsize)
    while cnt>0:
        cnt = cnt-1
        buff = f.read(buff_len)
        if buff is None:
            break
        remain = resolve_rtcm3(remain+buff)
        bytes_processed += len(buff)
    print "done!"
    f.close()


if __name__ == '__main__':
    from logger import init_logger
    fn = tkFileDialog.askopenfilename(initialdir=os.getcwd())
    f = open(fn, "rb")
    fo = open("pvt.sol")
    f_size = os.path.getsize(fn)
    init_logger(fo)
    parse_v1log(f,f_size)
    # f_out = open("pvt.sol", "w")


#plot_f(f_out,"green")



 
