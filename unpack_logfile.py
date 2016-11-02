import struct
from generate_sol import resolve_v1, unpack_record
from rtcm.RTCMv3_decode import resolve_rtcm3
import tkFileDialog
import os
import time
from logger import get_progress_bar
from rtklib.lib_interface import resolve_rtcm3_c,get_process_c

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

def parse_rtcm3log(fn_in,fsize):
    cnt = 0
    buff_len = 1024*1024
    buff_max = 1024*1024*480
    remain = 0
    # global bytes_processed

    f = open(fn_in,'rb')
    # if fsize < 480000000:
    #     f_ram = f.read()
    #     while len(f_ram)>0:
    #         f_ram = resolve_rtcm3(f_ram)
    #     bytes_processed += len(f_ram)
    #     print "whole file read done! len", len(f_ram)
    #     f.close()
    #     return
    # start_calc(fsize)
    buff = f.read(buff_max)
    bar.set_cb(get_process_c)
    bar.start_progress(fsize)
    # print "file size:{},buff len:{}".format(fsize,len(buff))
    resolve_rtcm3_c(buff)
    # while cnt>0:
    #     cnt = cnt-1
    #     if remain >= fsize:
    #         break
    #     remain += resolve_rtcm3(buff[remain:])
    #     while len(buff)-remain>1023:
    #         remain += resolve_rtcm3(buff[remain:])
    # print "done!"
    bar.stop_progress()
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



 
