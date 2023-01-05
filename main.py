from PyQt5 import QtCore, QtWidgets
from PyQt5.Qt import *
from ui.menu import Ui_ReceiverSetting
from ui.Log_in import Ui_MainWindow
from ui.saving import Ui_Saving
import sys


class Login_windows(QtWidgets.QMainWindow, Ui_MainWindow):

    _signal = QtCore.pyqtSignal(str,str)
    def __init__(self):
        super(Login_windows, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.click_success_1)
        self.pushButton_2.clicked.connect(self.click_success_2)
        self.Recveiver_Setting = Recveiver_Setting()
        self._signal.connect(self.Recveiver_Setting.get_feeds_account)

        self.Recveiver_Setting.pushButton_2.clicked.connect(self.show)
        self.Recveiver_Setting.pushButton_2.clicked.connect(self.Recveiver_Setting.close)


class Recveiver_Setting(QMainWindow, Ui_ReceiverSetting):
    _signal2 = QtCore.pyqtSignal(dict,dict,list,list,list,list,str,str)

    def __init__(self):
        super(Recveiver_Setting, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.Saving_view = Saving_view()
        self._signal2.connect(self.Saving_view.get_setting_info)
        self.pushButton.clicked.connect(self.click_success1)

class Saving_view(QtWidgets.QFrame,Ui_Saving):
    def __init__(self):
        super(Saving_view, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.pushButton.clicked.connect(self.click_success)
        self.pushButton_2.clicked.connect(self.click_success2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Login_windows= Login_windows()
    Receiver_setting = Recveiver_Setting()
    Saving_view = Saving_view()
    Login_windows.show()
    sys.exit(app.exec_())


