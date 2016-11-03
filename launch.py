import sys
import os
import traceback
import time

from PySide.QtCore import *
from PySide.QtGui import *
from ui.analysis_window import AnalysisWindow
from logger import ProgressBar
from rtklib.lib_interface import *
from unpack_logfile import parse_rtcm3log



class AnalysisMain(AnalysisWindow,ProgressBar):
    # def __init__(self):
    #     super(AnalysisWindow,self).__init__()
        # ProgressBar.__init__()

    def run_progress(self):
        while self.running:
            pct = get_process_c()
            self.set_progress(pct)
            time.sleep(0.1)
        pass
    def start_test(self):
        if not self.ready():
            print "cannot start, file not available"
            return

        # name, ext = self.fn_rover.split(".")
        # sol_name = name + '.obs'
        # fn_in = self.fn_rover
        # fn_out = sol_name
        # file_size = os.path.getsize(fn_in)
        # print "resolving file:", fn_in,file_size,"bytes"
        # print "output file:", fn_out

        # log_open_c(0,fn_out)
        # fn_out1 = name+'.nav'
        # log_open_c(1,fn_out1)
        # fn_out2 = name+'.sta'
        # log_open_c(2,fn_out2)
        try:
            self.start_progress(self.rov_fsize)
            parse_rtcm3log(self.fn_rover)

            # log_close_c(0)
            # log_close_c(1)
            # log_close_c(2)

        except Exception,e:
            print traceback.format_exc()
        finally:
            pass
            # t_e = time.time()
            # print "done! time consumed:{}".format(t_e-t_s)
            # raw_input("press any key")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AnalysisMain()
    window.show()
    sys.exit(app.exec_())
