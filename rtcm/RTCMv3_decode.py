#!/usr/bin/env python
''' Decode RTCM v3 messages and extract parameters required to generate v2 Type 1 and 3 messages.

The end game here is to be able to use RTCMv3 broadcast CORS corrections from, e.g. Geoscience
Australia, as RTCMv2 input to COTS uBlox receviers

Much of this work, esp. getting the unit conversions right, is based on  rtcm.c and rtcm3.c from
rtklib.

'''

import sys, time
import bitstring as bs
# import satPosition, util, RTCMv2, positionEstimate
import util
import RTCMv2
from rtklib import Bits

# from bitstring import BitStream
from bitstream import BitStream
import logging
from logger import get_logger,get_progress_bar

try:
    range = xrange
except NameError:
    pass

# logger = logging.getLogger('middle_solution')
logger = get_logger()
bar = get_progress_bar()

max_sats = 12

RTCMv3_PREAMBLE = 0xD3
PRUNIT_GPS = 299792.458
CLIGHT = 299792458.0

gpsPi = 3.1415926535898

RANGE_MS = CLIGHT*0.001

P2_10 = 0.0009765625          # 2^-10 
P2_24 = 5.960464477539063E-08 # 2^-24 
P2_27 = 7.450580596923828E-09 # 2^-27 
P2_29 = 1.862645149230957E-09 # 2^-29 
P2_30 = 9.313225746154785E-10 # 2^-30 

FREQ1 = 1.57542E9
FREQ2 = 1.22760E9
FREQ5 = 1.17645E9
FREQ6 = 1.27875E9
FREQ7 = 1.20714E9
FREQ8 = 1.191795E9

L2codes = ['CODE_L2C', 'CODE_L2P', 'CODE_L2W', 'CODE_L2W']

lam_carr = [CLIGHT / FREQ1, CLIGHT / FREQ2, CLIGHT / FREQ5, CLIGHT / FREQ6, CLIGHT / FREQ7, CLIGHT / FREQ8]

# Globals required to build v2 messages
corr_set = {}
statid = 0  # initially only support 1 reference station

eph = {}
prs = {}
week = 0
itow = 0

ref_pos = None

correct_rxclk = True

rtcm = RTCMv2.RTCMBits()
rtcm.type1_send_time = 0
rtcm.type3_send_time = 0

logfile = time.strftime('satlog-%y%m%d-%H%M.txt')


class DynamicEph:
    pass

class SatMeas:
    pass

class SigMeas:
    pass

class MSMHead:
    pass


satlog = None


def save_satlog(t, errset):
    global satlog
    if satlog is None:
        satlog = open(logfile, 'w')

    eset = [str(errset.get(s, '0')) for s in range(33)]

    satlog.write(str(t) + "," + ",".join(eset) + "\n")
    satlog.flush()


cp_hist = {}


def adjcp(sat, freq, cp):
    '''Adjust carrier phase for rollover'''
    if not sat in cp_hist or cp_hist[sat] is None:
        cp_hist[sat] = [0.0, 0.0]

    if cp_hist[sat][freq] == 0.0:
        return cp
    elif cp > cp_hist[sat][freq] - 750.0:
        cp += 1500.0
    elif cp > cp_hist[sat][freq] + 750.0:
        cp -= 1500.0

    cp_hist[sat][freq] = cp

    return cp


lock_hist = {}


def lossoflock(sat, freq, lock):
    '''Calc loss of lock indication'''
    if not sat in lock_hist or lock_hist[sat] is None:
        lock_hist[sat] = [0, 0]

    lli = (not lock and not lock_hist[sat][freq]) or (lock < lock_hist[sat][freq])

    lock_hist[sat][freq] = lock

    return lli


def snratio(snr):
    return int(snr <= 0.0 or 0.0 if 255.5 <= snr else snr * 4.0 + 0.5)


def decode_1004(pkt):
    global statid, itow, prs, corr_set

    statid = pkt.read(12).uint

    tow = pkt.read(30).uint * 0.001
    sync = pkt.read(1).uint
    nsat = pkt.read(5).uint

    smoothed = bool(pkt.read(1).uint)
    smint = pkt.read(3).uint

    prs = {}
    temp_corrs = {}

    for n in range(nsat):
        svid = pkt.read(6).uint
        temp_corrs[svid] = {}

        code1 = pkt.read(1).uint
        pr1 = pkt.read(24).uint
        ppr1 = pkt.read(20).int
        lock1 = pkt.read(7).uint
        amb = pkt.read(8).uint
        cnr1 = pkt.read(8).uint
        code2 = pkt.read(2).uint
        pr21 = pkt.read(14).int
        ppr2 = pkt.read(20).int
        lock2 = pkt.read(7).uint
        cnr2 = pkt.read(8).uint

        pr1 = pr1 * 0.02 + amb * PRUNIT_GPS

        if ppr1 != 0x80000:
            temp_corrs[svid]['P1'] = pr1
            cp1 = adjcp(svid, 0, ppr1 * 0.0005 / lam_carr[0])
            temp_corrs[svid]['L1'] = pr1 / lam_carr[0] + cp1

        temp_corrs[svid]['LLI1'] = lossoflock(svid, 0, lock1)
        temp_corrs[svid]['SNR1'] = snratio(cnr1 * 0.25)
        temp_corrs[svid]['CODE1'] = 'CODE_P1' if code1 else 'CODE_C1'

        if pr21 != 0xE000:
            temp_corrs[svid]['P2'] = pr1 + pr21 * 0.02

        if ppr2 != 0x80000:
            cp2 = adjcp(svid, 1, ppr2 * 0.0005 / lam_carr[1])
            temp_corrs[svid]['L2'] = pr1 / lam_carr[1] + cp2

        temp_corrs[svid]['LLI2'] = lossoflock(svid, 1, lock2)
        temp_corrs[svid]['SNR2'] = snratio(cnr2 * 0.25)
        temp_corrs[svid]['CODE2'] = L2codes[code2]

    # Sort the list of sats by SNR, trim to 10 sats
    quals = sorted([(s, temp_corrs[s]['SNR1']) for s in temp_corrs], key=lambda x: x[1])
    if len(quals) > max_sats:
        print("Drop {} sats for encode".format(len(quals) - max_sats))
        quals = quals[:max_sats]
    print(nsat, len(quals), quals)

    # Copy the kept sats in to the correction set 
    corr_set = {}
    for sv, snr in quals:
        corr_set[sv] = temp_corrs[sv]
        prs[sv] = temp_corrs[sv]['P1']

    itow = tow


def decode_1005(pkt):
    from util import PosVector
    
    global ref_pos, statid, itow, prs, corr_set

    statid = pkt.read(12).uint
    itrf = pkt.read(6).uint
    gps_flg = pkt.read(1).uint
    glo_flg = pkt.read(1).uint
    gal_flg = pkt.read(1).uint
    sta_flg = pkt.read(1).uint
    arp_ecef_x = pkt.read(38).int
    vco_flg = pkt.read(1).uint
    bds_flg = pkt.read(1).uint
    arp_ecef_y = pkt.read(38).int
    quater_cyc_flg = pkt.read(2)
    arp_ecef_z = pkt.read(38).int

    ecef = PosVector(arp_ecef_x, arp_ecef_y, arp_ecef_z)
    llh = ecef.ToLLH()

    seq = "[BaseARP],%.8f,%.8f,%f" % (llh.lat, llh.lon, llh.alt)
    logger.info(seq)

def decode_1006(pkt):
    global ref_pos

    staid = pkt.read(12).uint

    # Only set reference station location if it's the one used by
    # the observations
    if staid != statid:
        return

    itrf = pkt.read(6).uint
    pkt.read(4)
    ref_x = pkt.read(38).int * 0.0001
    pkt.read(2)
    ref_y = pkt.read(38).int * 0.0001
    pkt.read(2)
    ref_z = pkt.read(38).int * 0.0001
    anth = pkt.read(16).uint * 0.0001

    ref_pos = [ref_x, ref_y, ref_z]
    # print(ref_pos)
    # print(util.PosVector(*ref_pos).ToLLH())


def decode_1033(pkt):
    # Don't really care about any of this stuff at this stage..
    des = ''
    sno = ''
    rec = ''
    ver = ''
    rsn = ''

    stat_id = pkt.read(12).uint

    n = pkt.read(8).uint
    for i in range(n):
        des = des + chr(pkt.read(8).uint)

    setup = pkt.read(8).uint

    n = pkt.read(8).uint
    for i in range(n):
        sno = sno + chr(pkt.read(8).uint)

    n = pkt.read(8).uint
    for i in range(n):
        rec = rec + chr(pkt.read(8).uint)

    n = pkt.read(8).uint
    for i in range(n):
        ver = ver + chr(pkt.read(8).uint)

    n = pkt.read(8).uint
    for i in range(n):
        rsn = rsn + chr(pkt.read(8).uint)

        # print(des, sno, rec, ver, rsn)


def decode_1019(pkt):
    global eph, week

    svid = pkt.read(6).uint
    week = pkt.read(10).uint
    acc = pkt.read(4).uint
    l2code = pkt.read(2).uint
    idot = pkt.read(14).int
    iode = pkt.read(8).uint
    toc = pkt.read(16).uint
    af2 = pkt.read(8).int
    af1 = pkt.read(16).int
    af0 = pkt.read(22).int
    iodc = pkt.read(10).uint
    crs = pkt.read(16).int
    deltan = pkt.read(16).int
    m0 = pkt.read(32).int
    cuc = pkt.read(16).int
    e = pkt.read(32).uint
    cus = pkt.read(16).int
    rootA = pkt.read(32).uint
    toe = pkt.read(16).uint
    cic = pkt.read(16).int
    omega0 = pkt.read(32).int
    cis = pkt.read(16).int
    i0 = pkt.read(32).int
    crc = pkt.read(16).int
    omega = pkt.read(32).int
    omegadot = pkt.read(24).int
    tgd = pkt.read(8).int
    health = pkt.read(6).uint
    l2p = pkt.read(1).uint
    fit = pkt.read(1).uint

    eph[svid] = DynamicEph()

    eph[svid].crs = crs * pow(2, -5)
    eph[svid].cuc = cuc * pow(2, -29)
    eph[svid].cus = cus * pow(2, -29)
    eph[svid].cic = cic * pow(2, -29)
    eph[svid].cis = cis * pow(2, -29)
    eph[svid].crc = crc * pow(2, -5)

    eph[svid].deltaN = deltan * pow(2, -43) * gpsPi
    eph[svid].M0 = m0 * pow(2, -31) * gpsPi
    eph[svid].ecc = e * pow(2, -33)
    eph[svid].A = pow(rootA * pow(2, -19), 2)
    eph[svid].omega0 = omega0 * pow(2, -31) * gpsPi
    eph[svid].i0 = i0 * pow(2, -31) * gpsPi
    eph[svid].omega = omega * pow(2, -31) * gpsPi
    eph[svid].omega_dot = omegadot * pow(2, -43) * gpsPi

    eph[svid].toe = toe * pow(2, 4)
    eph[svid].idot = idot * pow(2, -43) * gpsPi
    eph[svid].iode = iode
    eph[svid].toc = toc * pow(2, 4)
    eph[svid].Tgd = tgd * pow(2, -31)
    eph[svid].af0 = af0 * pow(2, -31)
    eph[svid].af1 = af1 * pow(2, -43)
    eph[svid].af2 = af2 * pow(2, -55)

def decode_1020(pkt):
    pass


def decode_msm_head(pkt, type):
    sats = []
    sigs = []
    cellmask = []
    
    nsat = 0
    nsig = 0
    ncell = 0
    header = MSMHead()

    staid = pkt.read(12).uint

    # decode msm header
    if type >= 1081 and type < 1087:  # GLONASS
        dow = pkt.read(3).uint
        tod = pkt.read(27).uint * 0.001
        tow = dow * 24 * 60 * 60 + tod
        adjday_glot(pkt, tod)
    else:
        tow = pkt.read(30).uint * 0.001
        adjweek(pkt, tow)

    sync = pkt.read(1).uint
    header.tow = tow
    header.iod = pkt.read(3).uint
    header.time_s = pkt.read(7).uint
    header.clk_str = pkt.read(2).uint
    header.clk_ext = pkt.read(2).uint
    header.smooth = pkt.read(1).uint
    header.tint_s = pkt.read(3).uint
    for i in range(65):
        mask = pkt.read(1).uint
        if mask==1:
            sats.append(i+1)
            nsat += 1
    for i in range(32):
        mask = pkt.read(1).uint
        if mask==1:
            sigs.append(i+1)
            nsig += 1
    # print 'nsat:{} nsig:{}'.format(nsat,nsig)

    for i in range(nsat*nsig):
        maskv = pkt.read(1).uint
        cellmask.append(maskv)
        if maskv == 1:
            ncell += 1

    header.nsat = nsat
    header.nsig = nsig
    header.sats = sats
    header.sigs = sigs
    header.cellmask = cellmask

    return header


def decode_msm4(pkt, type):
    return decode_msm_head(pkt, type)


def decode_msm5(pkt, type):
    r = [] # range
    rr = [] # phase range rate
    ex = [] # extended info
    pr = [] # pseudorange
    cp = [] # phase range
    lock = [] # lock time
    half = [] # half-cycle ambiguity
    cnr = [] # cnr
    rrf = [] # phase range rate

    header = decode_msm_head(pkt, type)

    # decode satellite data
    for i in range(header.nsat):
        rng = pkt.read(8).int
        if True:#rng!=255:
            r.append(float(rng) * RANGE_MS)

    for i in range(header.nsat):
        ex.append(pkt.read(4).int)

    for i in range(header.nsat):
        rng_m = pkt.read(10).int
        if r[i]!=0.0:
             r[i] += float(rng_m)*P2_10*RANGE_MS

    for i in range(header.nsat):
        rate = pkt.read(14).int
        if True:#rate!=-8192:
            rr.append(float(rate)*1.0)

    for i in range(header.nsat):
        prv = pkt.read(15).int
        if True:#prv!=-16284:
            pr.append(float(prv)*P2_24*RANGE_MS)
    
    for i in range(header.nsat):
        cpv = pkt.read(22).int
        if True:#cpv!=-2097152:
            cp.append(float(cpv)*P2_29*RANGE_MS)

    for i in range(header.nsat):
        lock.append(pkt.read(4).int)
    
    for i in range(header.nsat):
        half.append(pkt.read(1).int)

    for i in range(header.nsat):
        cnr.append(float(pkt.read(6).int)*1.0)
    
    for i in range(header.nsat):
        rrv = pkt.read(15).int
        if True:#rrv!=-16384:
            rrf.append(float(rrv)*0.0001)

    seq = "[MSM_head],%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % \
            (type,header.tow, header.iod,header.time_s, \
            header.clk_str, header.clk_ext, header.smooth, \
            header.tint_s, header.nsat, header.nsig)
    logger.info(seq)
    for i in range(header.nsat):
        seq = "[MSM5],%d,%lf,%d,%lf,%lf,%lf,%d,%d,%f,%lf" % \
                    (header.sats[i], r[i], ex[i], rr[i], pr[i], \
                    cp[i], lock[i], half[i], cnr[i], rrf[i])
        logger.info(seq)


def adjday_glot(pkt, tod):
    pass


def adjweek(pke, tow):
    pass


# def regen_v2_type1():
#     if ref_pos is None:
#         return
#
#     errset = {}
#     pranges = {}
#     for svid in prs:
#
#         if svid not in eph:
#             # print("Don't have ephemeris for {}, only {}".format(svid, eph.keys()))
#             continue
#
#         toc = eph[svid].toc
#         tof = prs[svid] / util.speedOfLight
#
#         # assume the time_of_week is the exact receiver time of week that the message arrived.
#         # subtract the time of flight to get the satellite transmit time
#         transmitTime = itow - tof
#
#         T = util.correctWeeklyTime(transmitTime - toc)
#
#         satpos = satPosition.satPosition_raw(eph[svid], svid, transmitTime)
#         Trel = satpos.extra
#
#         satPosition.correctPosition_raw(satpos, tof)
#
#         geo = satpos.distance(util.PosVector(*ref_pos))
#
#         dTclck = eph[svid].af0 + eph[svid].af1 * T + eph[svid].af2 * T * T + Trel - eph[svid].Tgd
#
#         # Incoming PR is already corrected for receiver clock bias
#         prAdjusted = prs[svid] + dTclck * util.speedOfLight
#
#         errset[svid] = geo - prAdjusted
#         pranges[svid] = prAdjusted
#
#     save_satlog(itow, errset)
#
#     if correct_rxclk:
#         rxerr = positionEstimate.clockLeastSquares_ranges(eph, pranges, itow, ref_pos, 0)
#         if rxerr is None:
#             return
#
#         rxerr *= util.speedOfLight
#
#         for svid in errset:
#             errset[svid] += rxerr
#             pranges[svid] += rxerr
#
#         rxerr = positionEstimate.clockLeastSquares_ranges(eph, pranges, itow, ref_pos, 0) * util.speedOfLight
#
#         print("Residual RX clock error {}".format(rxerr))
#
#     iode = {}
#     for svid in eph:
#         iode[svid] = eph[svid].iode
#
#     msg = rtcm.RTCMType1_ext(errset, itow, week, iode)
#     if len(msg) > 0:
#         return msg


# def regen_v2_type3():
#     msg = rtcm.RTCMType3_ext(itow, week, util.PosVector(*ref_pos))
#     if len(msg) > 0:
#         return msg


def parse_rtcmv3(pkt):
    # 
    pkt_type = pkt.read(12).uint
    # logger.info("[RTCM{}]".format(pkt_type))

    # print pkt_type
    if pkt_type == 1004:
        decode_1004(pkt)
        return # regen_v2_type1()
    if pkt_type == 1005:
        decode_1005(pkt)
    elif pkt_type == 1006:
        decode_1006(pkt)
        return # regen_v2_type3()
    elif pkt_type == 1019:
        decode_1019(pkt)
    elif pkt_type == 1020:
        decode_1020(pkt)
    elif pkt_type == 1033:
        decode_1033(pkt)
    elif pkt_type in [1074, 1084, 1124]:
        msg = decode_msm4(pkt, pkt_type)
        msm4_handler(pkt_type, msg)
        # else:
        #    print "Ignore"
    elif pkt_type in [1075, 1085, 1125]:
        decode_msm5(pkt, pkt_type)
        # msm5_handler(pkt_type, tow)
    else:
        unknown_msg_handler(pkt_type)


def decode_rtcm3_pack(buff):
    d = ord(buff[0])
    if d != RTCMv3_PREAMBLE:
        print "RTCM3 preamble error!", d
        return

    pack_stream = BitStream()

    l1 = ord(buff[1])
    l2 = ord(buff[2])

    pack_stream.append(bs.pack('2*uint:8', l1, l2))
    pack_stream.read(6)
    pkt_len = pack_stream.read(10).uint

    pkt = buff[3:3 + pkt_len]
    parity = buff[3 + pkt_len:-1]

    if True:  # TODO check parity
        for d in pkt:
            pack_stream.append(bs.pack('uint:8', ord(d)))

        msg = parse_rtcmv3(pack_stream)

        # if msg is not None and rtcm_callback is not None:
        #     rtcm_callback(msg)


def resolve_rtcm3(buff):
    sync_head = 0
    while sync_head < len(buff):
        if ord(buff[sync_head]) != RTCMv3_PREAMBLE:
            sync_head += 1
            bar.mark(1)
            continue

        pack_stream = Bits()

        pack_stream.append(buff[sync_head+1])
        pack_stream.append(buff[sync_head+2])
        pack_stream.read(6)
        pkt_len = pack_stream.read(10).uint
        # print "pkt_len:",pkt_len

        # pkt = buff[3:3 + pkt_len]
        parity = buff[sync_head+pkt_len+3:sync_head+pkt_len+6]

        if True:  # TODO check parity
            # for d in pkt:
                # pack_stream.append(bs.pack('uint:8', ord(d)))
                # pack_stream.append(d)
            pack_stream.from_buffer(buff[sync_head+3:sync_head+3+pkt_len])

            msg = parse_rtcmv3(pack_stream)
        
        sync_head += pkt_len + 6
        bar.feed(sync_head)
    return sync_head


def msm5_handler(type, tow):
    
    # generate_msm_sol(type, tow)
    seq = "[MSM5],%d,%d" % (type, tow)
    logger.info(seq)


def msm4_handler(type, msg):
    
    # generate_msm_sol(type, tow)
    seq = "[MSM4],%d,%d" % (type, msg[0])
    logger.info(seq)


def unknown_msg_handler(pkt_type):
    
    seq = "[unknown],%d" % pkt_type
    logger.info(seq)


def RTCM_converter_thread(server, port, username, password, mountpoint, rtcm_callback=None):
    import subprocess

    nt = subprocess.Popen(["./ntripclient",
                           "--server", server,
                           "--password", password,
                           "--user", username,
                           "--mountpoint", mountpoint],
                          stdout=subprocess.PIPE)

    """nt = subprocess.Popen(["./ntrip.py", server, str(port), username, password, mountpoint],
                            stdout=subprocess.PIPE)"""

    if nt is None or nt.stdout is None:
        indev = sys.stdin
    else:
        indev = nt.stdout

    print("RTCM using input {}".format(indev))

    while True:
        sio = indev

        d = ord(sio.read(1))
        if d != RTCMv3_PREAMBLE:
            continue

        pack_stream = BitStream()

        l1 = ord(sio.read(1))
        l2 = ord(sio.read(1))

        pack_stream.append(bs.pack('2*uint:8', l1, l2))
        pack_stream.read(6)
        pkt_len = pack_stream.read(10).uint

        pkt = sio.read(pkt_len)
        parity = sio.read(3)

        if len(pkt) != pkt_len:
            print "Length error {} {}".format(len(pkt), pkt_len)
            continue

        if True:  # TODO check parity
            for d in pkt:
                pack_stream.append(bs.pack('uint:8', ord(d)))

            msg = parse_rtcmv3(pack_stream)

            if msg is not None and rtcm_callback is not None:
                rtcm_callback(msg)


def run_RTCM_converter(server, port, user, passwd, mount, rtcm_callback=None, force_rxclk_correction=True):
    global correct_rxclk
    import threading

    correct_rxclk = force_rxclk_correction

    t = threading.Thread(target=RTCM_converter_thread, args=(server, port, user, passwd, mount, rtcm_callback,))
    t.start()


def _printer(p):
    print(p)



if __name__ == '__main__':
    RTCM_converter_thread('192.104.43.25', 2101, sys.argv[1], sys.argv[2], 'TID10', _printer)
