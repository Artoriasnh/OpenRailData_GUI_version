# pyuic5 -o saving.py saving.ui -x

from PyQt5 import QtCore, QtGui, QtWidgets
from ui.account_verify import verify_credentials_selenium
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.Qt import *
import time

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(480, 225)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 10, 450, 21))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(20, 110, 70, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(20, 60, 60, 16))
        self.label_5.setObjectName("label_5")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(100, 100, 321, 31))
        self.lineEdit_2.setInputMask("")
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setGeometry(QtCore.QRect(100, 50, 321, 31))
        self.lineEdit_3.setText("")
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(100, 150, 261, 26))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 441, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action123 = QtWidgets.QAction(MainWindow)
        self.action123.setObjectName("action123")
        self.action123_2 = QtWidgets.QAction(MainWindow)
        self.action123_2.setObjectName("action123_2")

        self.layoutWidget.setGeometry(QtCore.QRect(100, 150, 320, 30))
        self.pushButton.setMinimumHeight(30)
        self.pushButton_2.setMinimumHeight(30)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Open Data Feeds Receiver"))
        self.label_3.setText(_translate("MainWindow", "Enter your Open Data Feeds account number and password."))
        self.label_4.setText(_translate("MainWindow", "Password:"))
        self.label_5.setText(_translate("MainWindow", "Email:"))
        self.pushButton.setText(_translate("MainWindow", "Log in"))
        self.pushButton_2.setText(_translate("MainWindow", "sign up"))
        self.action123.setText(_translate("MainWindow", "123"))
        self.action123_2.setText(_translate("MainWindow", "123"))

    # def click_success_1(self):
    #     password = self.lineEdit_2.text()
    #     Email = self.lineEdit_3.text()
    #     self._signal.emit(Email, password)
    #     self.close()
    #     time.sleep(0.5)
    #     self.Recveiver_Setting.show()
    def click_success_1(self):
        password = self.lineEdit_2.text()
        email = self.lineEdit_3.text()

        if verify_credentials_selenium(email, password):
            print("Login Success")
            self._signal.emit(email, password)
            self.close()
            time.sleep(0.5)
            self.Recveiver_Setting.show()
        else:
            QMessageBox.warning(self, "Login Fail", "Incorrect username or password.")

        # 连接信号
        # self.Rec_Setting._signal.connect(self.getData)

    def click_success_2(self):
        # url = QUrl("https://datafeeds.networkrail.co.uk/ntrod/login;jsessionid=0F01DD532B6D302A99FCD4DBF7E2661A")
        url = QUrl("https://datafeeds.networkrail.co.uk/ntrod/create-account")
        QDesktopServices.openUrl(url)



    def Account_verification(self):
        password = self.lineEdit_2.text()
        Email = self.lineEdit_3.text()

        # url = QUrl("https://datafeeds.networkrail.co.uk/ntrod/login;jsessionid=0F01DD532B6D302A99FCD4DBF7E2661A")
        # sleep(1)
        # username.send_keys(self.username)
        # sleep(1)
        # password.send_keys(self.password)




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.pushButton.clicked.connect(ui.click_success_1)
    ui.pushButton_2.clicked.connect(ui.click_success_2)
    MainWindow.show()
    sys.exit(app.exec_())
