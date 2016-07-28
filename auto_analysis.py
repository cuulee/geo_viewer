from unpack_logfile import parse_logfile
from visualization import plot_bestpos, plot_MSM
from generate_sol import SolGenerator
from RTCMv3_decode import set_generator
import tkFileDialog
import os
import  time


def traversal_resolve(rootDir):
    list_dirs = os.walk(rootDir)

    for root, dirs, files in list_dirs:
        for f in files:
            name, ext = f.split(".")
            sol_name = name + ".sol"
            if ext != "DAT":
                continue
            if sol_name in files:
                continue
            print "resolving file:", os.path.join(root, f)
            f_in = open(os.path.join(root, f), "rb")
            f_out = open(os.path.join(root, sol_name), "w")
            print "output file:", os.path.join(root, sol_name)
            sg = SolGenerator(f_out)
            # sg.run()
            set_generator(sg)
            parse_logfile(f_in)
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
    traversal_resolve("./logs")
    # time.sleep(3)
    traversal_plot("./logs")
    traversal_plot_msm("./logs")
    # raw_input()

