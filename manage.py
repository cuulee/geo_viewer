import struct
from read_log import parse_v1_pack
from visualization import plot_coord
import tkFileDialog
import os
#from draw_coordinate import plot_f

cnt = 10000
buff_len = 1024
fn = tkFileDialog.askopenfilename(initialdir = os.getcwd())
f = open(fn,"rb")
f_out = open("pvt.sol","w")
#f = open("FLY039.DAT","rb")
remain = ""
while cnt>0:
    cnt = cnt-1
    buff = f.read(buff_len)
    if buff is None:
        break
    remain = parse_v1_pack(remain+buff,0)
print "done!"



#plot_f(f_out,"green")



 
