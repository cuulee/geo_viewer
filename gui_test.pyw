import sys
from PyQt4 import QtCore, QtGui, uic
from auto_test import TestControl

qtCreatorFile = "test_panel.ui"  # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.startTestBtn.clicked.connect(self.start_test)
        self.stopBtn.clicked.connect(self.stop_test)
        self.test_control = TestControl(loops=10, timeout=300)
        # tc = TestControl(loops=10, timeout=300)
        self.test_control.de_init()
        # tc.run_test()
        self.currentLoop.connect(self.get_current_loop)

    def run_printer(self):
        # auto_test.run_receiver()
        pass

    def start_test(self):
        loops = self.loopNum.value()
        timeout = self.timePerLoop.value()

        self.test_control.run_test(loops, timeout)

    def stop_test(self):
        self.test_control.stop_test()

    def get_current_loop(self):
        return self.test_control.loop


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
