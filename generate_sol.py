import struct
import time
from dji.dji import chkCRC8, chkCRC16, getHeader
# from RTCMv3_decode import decode_rtcm3_pack
from rtcm.RTCMv3_decode import *
import logging

buff_len = 1024
# state = 0
# len_ver = [0,0];

# f = open('pvt.sol', 'w')
# f1 = open('baserange.sol', 'w')
unicore_msgType_list = [0x8f1, 0x8f7, 0x8fe]
CNR_MSG_LIST = [0x900, 0x901, 0x902, 0x903, 0x904, 0x905, 0x906, 0x907, 0x908]
RTCM_msgType_list = [1075, 1085, 1125, 1033, 1019, 1020, 1041, 1006, 1005, 1004]
station_info_msg_list = [0x8ee,0x8ef]
write_done = False


def unpack_v1_comm(bytes):
    sync, len_ver, crc8, sender, receiver, seq, cmd_type, cmd_set, cmd_id = struct.unpack("<BhBBBhBBB", bytes[0:11])
    length = len_ver & 0x3ff
    ver = len_ver >> 10 & 0x3f
    # print "length:%.2x sender:%.2x rcver:%.2x seq:%.4x cmdset:%.2x cmdid:%.2x"%(length,sender,receiver,seq,cmd_set,cmd_id)
    if cmd_set == 0x00 and cmd_id == 0x0e:
        print bytes[12:-2]


def unpack_record(bytes):
    buff = ""
    sync, length, crc8, data_type, key = struct.unpack("<BhBhB", bytes[0:7])
    if data_type in unicore_msgType_list:
        # print "%.2x len:%.4x datatype:%.4x key:%.2x"%(sync,length,data_type,key)
        for val in bytes[10:10 + length]:
            buff += chr(ord(val) ^ key)
        # print buff
        unpack_unicore(buff)
        # if data_type == 0x8f7:
        #     uniSync, msgID, msgType = struct.unpack("<IhB", buff[0:7])
        #     print ">base range here [%x][%d][%d]<" % (uniSync, msgID, msgType)
    if data_type in RTCM_msgType_list:
        for val in bytes[10:10 + length]:
            buff += chr(ord(val) ^ key)
        unpack_rtcm(buff)
        # uniSync,msgID,msgType,portAddr,msgLen,seq = struct.unpack("<IhBBhh",bytes[10:22])
        # print "%.8x msgID:%.4x msgType:%.2x"%(uniSync,msgID,msgType)
    if data_type in station_info_msg_list:  # rover info
        for val in bytes[10:10 + length]:
            buff += chr(ord(val) ^ key)
        unpack_station_info(buff,data_type)
        # print "find g rtk status pack!"

    if data_type in CNR_MSG_LIST:
        pass
        # for val in bytes[10:10 + length]:
        #     buff += chr(ord(val) ^ key)


def unpack_unicore(bytes):
    logger = logging.getLogger('middle_solution')
    # uniSync,msgID,msgType,portAddr,msgLen,seq = struct.unpack("<IhBBhh",bytes[0:12])
    uniSync, msgID, msgType, portAddr, msgLen, seq, idleTime, timeStt, week, ms, rsv2, timeOffset, rsv3 = struct.unpack(
        "<IhBBhhBBhIIhh", bytes[0:28])
    # print "msgID:%.4x len:%.4x seq:%.4x"%(msgID,msgLen,seq)
    if msgID == 42:
        solStt, posType, lat, lon, hgt, undulation = struct.unpack("<IIdddf", bytes[28:64])
        trkSVs, solSVs = struct.unpack("<BB", bytes[92:94])
        seq = "[BestPos],%d,%d,%.8f,%.8f,%f,%d,%d,%d,%d" % (
            solStt, posType, lat, lon, hgt, undulation, trkSVs, solSVs, ms)
        logger.info(seq)
    if msgID == 283:
        seq = "[BaseRange],%d,%d" % (week, ms)
        logger.info(seq)
    return 0


def unpack_rtcm(bytes):
    # print "rtcm msm packet", ord(bytes[1]) + 1, "of", ord(bytes[0])g
    # total_num = ord(bytes[0])
    # pack_num = ord(bytes[1])

    cvt.input(bytes)


def unpack_station_info(bytes,datatype):
    logger = logging.getLogger('middle_solution')
    boot_cnt, hardware_ver, software_ver = struct.unpack("<III", bytes[:12])
    if datatype == 0x8ef:
        seq = "[BaseInfo],boot_cnt:%d,hardware:%d,software:%d" % (boot_cnt, hardware_ver, software_ver)
    if datatype == 0x8ee:
        seq = "[RoverInfo],boot_cnt:%d,hardware:%d,software:%d" % (boot_cnt, hardware_ver, software_ver)
    logger.info(seq)


class RTCMPack:  # self packed rtcm frame with 2 bytes of header
    def __init__(self):
        self.pack_idx = 0
        self.num_of_pack = 0
        self.valid = False
        self._buff = ""

    def input(self, buff):
        self.pack_idx = ord(buff[1])
        self.num_of_pack = ord(buff[0])

        if self.num_of_pack == 1:
            self.valid = True
            self._buff = buff[2:-1]
        else:
            self._buff += buff[2:-1]
            if self.pack_idx + 1 < self.num_of_pack:
                self.valid = False
            else:
                self.valid = True
        self._output()

    def _output(self):
        if self.valid:
            decode_rtcm3_pack(self._buff)


def generate_msm_sol(type, tow):
    pass


def resolve_v1(buff, handler):
    search_idx = 0
    pack_1 = ""

    while search_idx < len(buff):
        headBegin = getHeader(buff[search_idx:-1])
        if headBegin == -1:
            break

        headBegin = headBegin + search_idx

        if headBegin + 4 > len(buff):
            return buff[headBegin:-1]
        sync, len_ver, headCRC = struct.unpack("<BhB", buff[headBegin:headBegin + 4])
        length = len_ver & 0x3ff
        # print length
        # print "%x %x %x"%(sync,len_ver,headCRC)
        crc8_chk = chkCRC8(buff[headBegin:headBegin + 4])
        # print "crc8:%.2x"%crc8_chk
        search_idx = headBegin + 1
        if crc8_chk != 0:
            # print "crc8 err", search_idx
            continue
        pack_1 = buff[headBegin:headBegin + length]
        if length + headBegin > len(buff):
            return pack_1

        handler(pack_1)

        search_idx = headBegin + length
        crc16_chk = chkCRC16(pack_1)
        if crc16_chk != 0:
            # print "crc16 error"
            pass

    return pack_1


cvt = RTCMPack()
