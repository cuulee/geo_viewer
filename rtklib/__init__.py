from ctypes import *
import os
import time
import sys

if __name__ == '__main__':
    import sys
    sys.path.append("..")
    from logger import get_logger,get_progress_bar

    dll_path = os.getcwd() + "/rtklib.dll"
    rtklib = cdll.LoadLibrary(dll_path)

    logger = get_logger()
    bar = get_progress_bar()

    buff = "this that"
    print buff
    # bs = Bits()
    # bs.append(buff[0])
    # bs.append(buff[1])
    # print bs.read(4)
    # while True:
    #     print rtklib.timeget()
    #     time.sleep(1)
    size = len(buff)
    in_buff = c_char_p(buff)
    rtklib.test_call(in_buff,size)
    print buff
    rtklib.log_test()
    # rtklib.printf("hello world")
else:
    # sys.path.append('./rtklib')
    dll_path = os.getcwd() + "./rtklib/rtklib.dll"
    rtklib = cdll.LoadLibrary(dll_path)
    from logger import get_logger,get_progress_bar
    logger = get_logger()
    bar = get_progress_bar()








        
    # raw_input()
