import os
import  time
import tkFileDialog
from unpack_logfile import parse_v1log, parse_rtcm3log
from visualization import plot_bestpos, plot_MSM
from logger import init_logger

class TraversalResolver(object):
    def __init__(self,parser,itype='DAT',otype='sol'):
        self.itype = itype
        self.otype = otype
        self.parser = parser

    def resolve(self,rootDir):
        list_dirs = os.walk(rootDir)
        for root, dirs, files in list_dirs:
            for f in files:
                name, ext = f.split(".")
                sol_name = name + '.' + self.otype
                if ext != self.itype:
                    continue
                if sol_name in files:
                    continue
                fn_in = os.path.join(root, f)
                fn_out = os.path.join(root, sol_name)
                file_size = os.path.getsize(fn_in)
                print "resolving file:", fn_in,file_size,"bytes"
                print "output file:", fn_out
                init_logger(fn_out)
                self.parser(fn_in,file_size)
                print "done"

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
    tr = TraversalResolver(parse_v1log)
    tr.resolve("./logs")
    tr1 = TraversalResolver(parse_rtcm3log,'log')
    tr1.resolve("./logs")

    tp = TraversalPloter(plot_bestpos)
    tp.plot("./logs")

    raw_input("press any key to exit...")
    # traversal_resolve("./logs")
    # traversal_resolve_rtcm3("./logs")
    # time.sleep(3)
    # traversal_plot("./logs")
    # traversal_plot_msm("./logs")
    # raw_input()

