import os
import  time
import tkFileDialog
import traceback
from unpack_logfile import parse_v1log, parse_rtcm3log
from visualization import plot_bestpos, plot_MSM
from logger import init_logger, get_logger
from rtklib import log_open_c,log_close_c

class TraversalResolver(object):
    def __init__(self,parser,itype='DAT',otype='csv',otype1=None):
        self.itype = itype
        self.otype = otype
        self.otype1 = otype1
        self.parser = parser

    def resolve(self,rootDir):
        list_dirs = os.walk(rootDir)
        for root, dirs, files in list_dirs:
            for f in files:
                t_s = time.time()
                name, ext = f.split(".")
                sol_name = name + '.' + self.otype
                temp_name = name + '.' + self.otype + 'tmp'
                if ext != self.itype:
                    continue
                if sol_name in files:
                    continue
                fn_in = os.path.join(root, f)
                fn_out = os.path.join(root, temp_name)
                file_size = os.path.getsize(fn_in)
                print "resolving file:", fn_in,file_size,"bytes"
                print "output file:", fn_out
                # init_logger(fn_out)
                # log = get_logger()
                # log.set_file(fn_out)
                log_open_c(0,fn_out)
                if self.otype1 is not None:
                    fn_out1 = os.path.join(root, name+'.'+self.otype1+'tmp')
                    log_open_c(1,fn_out1)
                try:
                    self.parser(fn_in,file_size)
                    # log.flush()
                    # log.close()
                    log_close_c(0)
                    os.rename(fn_out,os.path.join(root, sol_name))
                    if self.otype1 is not None:
                        log_close_c(1)
                        os.rename(fn_out1,os.path.join(root, name + '.' + self.otype1))
                except Exception:
                    print traceback.format_exc()
                finally:
                    t_e = time.time()
                    print "done! time consumed:{}".format(t_e-t_s)
                    raw_input("press any key")
                
                

class TraversalPloter(object):
    def __init__(self,visualizer,itype='sol',otype='png'):
        self.itype = itype
        self.otype = otype
        self.visualizer = visualizer

    def plot(self,rootDir):
        list_dirs = os.walk(rootDir)
        for root, dirs, files in list_dirs:
            for f in files:
                name, ext = f.split(".")
                if ext != self.itype:
                    continue
                pic_name = name + '.' + self.otype
                if pic_name in files:
                    continue
                print "plotting file:", os.path.join(root, f),
                f_plot = open(os.path.join(root, f))
                self.visualizer(f_plot)
                f_plot.close()
                print "done"
        

if __name__ == '__main__':
    tr = TraversalResolver(parse_v1log,'DAT','sol')
    tr.resolve("./logs")
    tr1 = TraversalResolver(parse_rtcm3log,'rtcm3','obs','nav')
    tr1.resolve("./logs/rtcm_logs")
    

    # tp = TraversalPloter(plot_bestpos)
    # tp.plot("./logs")

    # raw_input("press any key to exit...")
    # traversal_resolve("./logs")
    # traversal_resolve_rtcm3("./logs")
    # time.sleep(3)
    # traversal_plot("./logs")
    # traversal_plot_msm("./logs")
    # raw_input()

