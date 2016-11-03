import struct
from threading import Thread
from generate_sol import resolve_v1, unpack_record
from rtcm.RTCMv3_decode import resolve_rtcm3
import tkFileDialog
import os
import time
from logger import get_progress_bar
from rtklib.lib_interface import *

bar = get_progress_bar()

# bytes_processed = 0

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
    # global bytes_processed

    bytes_processed = 0
    f = open(fn_in,'rb')

    # start_calc(fsize)
    while cnt>0:
        cnt = cnt-1
        buff = f.read(buff_len)
        if buff is None:
            break
        remain = resolve_v1(remain+buff, unpack_record)
        # bytes_processed += len(buff)
    # print "done!"
    f.close()

def parse_rtcm3log(fn_in):
    t = Thread(target=_parse_rtcm3_log,args=(fn_in,))
    t.setDaemon(True)
    t.start()
    

def _parse_rtcm3_log(fn_in):
    cnt = 0
    buff_len = 1024*1024
    buff_max = 1024*1024*480
    remain = 0
    # global bytes_processed

    t_s = time.time()

    name, ext = fn_in.split(".")
    sol_name = name + '.obs'
    # fn_in = self.fn_rover
    fn_out = sol_name
    fsize = os.path.getsize(fn_in)
    print "resolving file:", fn_in,fsize,"bytes"
    print "output file:", fn_out

    log_open_c(0,fn_out)
    fn_out1 = name+'.nav'
    log_open_c(1,fn_out1)
    fn_out2 = name+'.sta'
    log_open_c(2,fn_out2)

    
    f = open(fn_in,'rb')

    buff = f.read(buff_max)
    bar.set_cb(get_process_c)
    bar.start_progress(fsize)

    resolve_rtcm3_c(buff)

    bar.stop_progress()
    f.close()
    log_close_c(0)
    log_close_c(1)
    log_close_c(2)

    t_e = time.time()
    print "done! time consumed:{}".format(t_e-t_s)

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



 
