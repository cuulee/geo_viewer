import struct
from generate_sol import parse_v1_pack, unpack_record, SolGenerator
from RTCMv3_decode import set_generator
import tkFileDialog
import os

def parse_logfile(f_in):
    cnt = 10000
    buff_len = 1024
    remain = ""
    while cnt>0:
        cnt = cnt-1
        buff = f_in.read(buff_len)
        if buff is None:
            break
        remain = parse_v1_pack(remain+buff, unpack_record)
    print "done!"


if __name__ == '__main__':
    fn = tkFileDialog.askopenfilename(initialdir=os.getcwd())
    f = open(fn, "rb")
    fo = open("pvt.sol")
    sg = SolGenerator(fo)
    set_generator(sg)
    parse_logfile(f)
    # f_out = open("pvt.sol", "w")


#plot_f(f_out,"green")



 
