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
                file_path = os.path.join(root, f)
                file_size = os.path.getsize(file_path)
                print "resolving file:", file_path,file_size,"bytes"
                f_in = open(file_path, "rb")
                f_out = open(os.path.join(root, sol_name), "w")
                print "output file:", os.path.join(root, sol_name)
                init_logger(f_out)
                self.parser(f_in,file_size)
                print "done"

def traversal_plot(rootDir):
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for f in files:
            name, ext = f.split(".")
            pic_name = name + ".png"
            if ext != "sol":
                continue
            if pic_name in files:
                continue
            print "plotting file:", os.path.join(root, f),
            f_plot = open(os.path.join(root, f))
            plot_bestpos(f_plot)
            print "done"

def traversal_plot_msm(rootDir):
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for f in files:
            name, ext = f.split(".")
            pic_name = name + "_lost" + ".png"
            if ext != "sol":
                continue
            if pic_name in files:
                continue
            print "plotting lost file:", os.path.join(root, f),
            f_plot = open(os.path.join(root, f))
            plot_MSM(f_plot)
            print "done"

if __name__ == '__main__':
    tr = TraversalResolver(parse_v1log)
    tr.resolve("./logs")
    tr1 = TraversalResolver(parse_rtcm3log,'log')
    tr1.resolve("./logs")
    # traversal_resolve("./logs")
    # traversal_resolve_rtcm3("./logs")
    # time.sleep(3)
    # traversal_plot("./logs")
    # traversal_plot_msm("./logs")
    # raw_input()

