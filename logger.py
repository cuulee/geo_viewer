import logging
import logging.handlers


LOG_FILE = 'tst.log'


def init_logger(f):
    # str = f.name
    handler = logging.handlers.RotatingFileHandler(f, maxBytes = 0, backupCount = 5) 
    handler1 = logging.handlers.MemoryHandler(1024*4,target = handler)
    fmt = '%(message)s'  
    formatter = logging.Formatter(fmt)     
    handler1.setFormatter(formatter)        
    logger = logging.getLogger('middle_solution')     
    logger.addHandler(handler1)
    logger.setLevel(logging.DEBUG)  


