import struct
import serial
import time
from generate_sol import chkCRC8,chkCRC16,getHeader,unpack_v1_comm,parse_v1_pack,unpack_v1_comm

t = serial.Serial('com5',115200)
remain = ""
#str = t.read(1024)

while True:
    buff = t.read(t.in_waiting)
    #print len(buff)
    if len(buff) == 0:
        #print "buff empty"
        time.sleep(0.1)
        continue
    remain = parse_v1_pack(remain+buff, unpack_v1_comm)



