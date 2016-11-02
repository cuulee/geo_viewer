import logging
import logging.handlers
import time
from ctypes import *

LOG_FILE = 'tst.log'


def init_logger(f):
    # str = f.name
    handler = logging.handlers.RotatingFileHandler(f, maxBytes = 0, backupCount = 5) 
    handler1 = logging.handlers.MemoryHandler(64,target = handler)
    fmt = '%(message)s'  
    formatter = logging.Formatter(fmt)
    handler1.setFormatter(formatter)        
    logger = logging.getLogger('middle_solution')     
    logger.addHandler(handler1)
    logger.setLevel(logging.DEBUG)  

class SolLogger(object):
    def __init__(self,name,ofilename=None,buff_size=128):
        self.name = name
        self.buff_size = buff_size
        self._buff = []
        self.ofile = ofilename
        if self.ofile is not None:
            self.f = open(ofilename,'w')

    def set_file(self,fn):
        self.ofile = fn
        self.f = open(fn,'w')
    
    def push(self,data):
        self._buff.append(data)
        if len(self._buff)> self.buff_size:
            self.flush()
    
    def log(self,msg):
        msg1 = msg + '\n'
        self.push(msg1)

    def flush(self):
        self.f.writelines(self._buff)
        self._buff = []

    def info(self,msg):
        self.log(msg)
        pass

    def close(self):
        self.f.close()


logger = SolLogger('mlog',buff_size=1024)

def get_logger():
    return logger


class ProgressBar(object):
    def __init__(self,update_cb=None):
        self.running = False
        self.work_size = 0
        self.progress = 0
        self.marks = 0
        self.update_cb = update_cb
        pass

    def register(self):
        import threading

        t = threading.Thread(target=self.run_progress)
        t.start()

    def set_cb(self,cb):
        self.update_cb = cb

    def start_progress(self,size):
        self.work_size = size
        self.progress = 0
        self.marks = 0
        self.running = True

        self.register()

    def stop_progress(self):
        self.running = False
        print '                           \r',

    def feed(self,margain):
        self.progress += margain

    def mark(self,cnt):
        self.marks += cnt

    def run_progress(self):
        while self.running:
            if self.update_cb is not None:
                pct = self.update_cb()
            else:
                pct = self.progress * 100.0 / self.work_size
            print "processed: %{},lost:{}\r".format(pct,self.marks),
            if self.progress >= self.work_size:
                # break
                pass
            time.sleep(0.1)


bar = ProgressBar()
# bar.register()

def get_progress_bar():
    return bar



                
    


