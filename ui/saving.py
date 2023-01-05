from PyQt5 import QtCore, QtGui, QtWidgets
from Message_to_sql import *
from get_data import get_data
from MSG import *
import os
import signal
from PyQt5.Qt import *

class Ui_Saving(object):
    def setupUi(self, Saving):
        Saving.setObjectName("Saving")
        Saving.resize(462, 449)
        self.gridLayout_2 = QtWidgets.QGridLayout(Saving)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame = QtWidgets.QFrame(Saving)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 1, 1, 1)
        self.textEdit = QtWidgets.QTextEdit(self.frame)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 0, 0, 1, 3)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 2, 1, 1)
        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(Saving)
        QtCore.QMetaObject.connectSlotsByName(Saving)

    def retranslateUi(self, Saving):
        _translate = QtCore.QCoreApplication.translate
        Saving.setWindowTitle(_translate("Saving", "Open Data Feeds Receiver"))
        self.pushButton.setText(_translate("Saving", "Start"))
        self.pushButton_2.setText(_translate("Saving", "Exit"))

    def get_setting_info(self, sql_info,get_options,feeds_list,td_list,mvt_list,rtppm_list,Email,password):
        self.sql_info = sql_info
        self.get_options = get_options
        self.feeds_list = feeds_list
        self.td_list = td_list
        self.mvt_list = mvt_list
        self.rtppm_list = rtppm_list
        self.Email = Email
        self.password = password


    def click_success(self):
        self.get_msg()
        sys.stdout = EmitStr(textWrit=self.outputWrite)
        sys.stderr = EmitStr(textWrit=self.outputWrite)


    def click_success2(self):
        os.getpid()
        os.kill(os.getpid(), signal.SIGTERM)


    def outputWrite(self, text):
        self.textEdit.append(text)


    def get_msg(self):
        for i in self.feeds_list:
            if i == 'TD':
                for j in self.td_list:
                    area_id = j

                    if j == 'All':
                        _table_format = table_format['TD_All']
                    else:
                        _table_format = table_format['TD']

                    TD_mts = TD_msg(
                        schema_name=self.sql_info['schema_name'],
                        data_type='TD_' + area_id,
                        database_name=self.sql_info['database_name'],
                        sql_username=self.sql_info['sql_username'],
                        sql_password=self.sql_info['sql_password'],
                        sql_host=self.sql_info['sql_host'],
                        port=self.sql_info['port'],
                        table_format=_table_format,
                        area_id=area_id
                    )
                    TD_getdata = get_data(
                        mts=TD_mts,
                        username=self.Email,
                        password=self.password,
                        topic=topic_dict['TD'],
                        listener=Listener_dict['TD'],
                        msg_print=self.get_options['View'],
                        sts=self.get_options['Save_to_SQL'],
                        isdurable=self.get_options['Durable']
                    )
                    TD_getdata.start()


            if i == 'Train Movement':
                for j in self.mvt_list:
                    if j[1:5] == '0004':
                        continue;
                    else:
                        MVT_mts = TM_MVT_msg(
                            schema_name=self.sql_info['schema_name'],
                            data_type=TM_MESSAGES[j[1:5]],
                            database_name=self.sql_info['database_name'],
                            sql_username=self.sql_info['sql_username'],
                            sql_password=self.sql_info['sql_password'],
                            sql_host=self.sql_info['sql_host'],
                            port=self.sql_info['port'],
                            table_format=table_format['MVT'][j[1:5]],
                            MVT_type=j[1:5]
                        )
                        MVT_getdata = get_data(
                            mts=MVT_mts,
                            username=self.Email,
                            password=self.password,
                            topic=topic_dict['MVT'],
                            listener=Listener_dict['MVT'],
                            msg_print=self.get_options['View'],
                            sts=self.get_options['Save_to_SQL'],
                            isdurable=self.get_options['Durable']
                        )
                        MVT_getdata.start()


            if i == 'VSTP':
                VSTP_mts = VSTP_msg(
                    schema_name=self.sql_info['schema_name'],
                    data_type='VSTP',
                    database_name=self.sql_info['database_name'],
                    sql_username=self.sql_info['sql_username'],
                    sql_password=self.sql_info['sql_password'],
                    sql_host=self.sql_info['sql_host'],
                    port=self.sql_info['port'],
                    table_format=table_format['VSTP'],
                )
                VSTP_getdata = get_data(
                    mts=VSTP_mts,
                    username=self.Email,
                    password=self.password,
                    topic=topic_dict['VSTP'],
                    listener=Listener_dict['VSTP'],
                    msg_print=self.get_options['View'],
                    sts=self.get_options['Save_to_SQL'],
                    isdurable=self.get_options['Durable']
                )
                VSTP_getdata.start()


            if i == 'RTPPM':
                RTPPM_mts = RTPPM_msg(
                    schema_name=self.sql_info['schema_name'],
                    data_type='RTPPM',
                    database_name=self.sql_info['database_name'],
                    sql_username=self.sql_info['sql_username'],
                    sql_password=self.sql_info['sql_password'],
                    sql_host=self.sql_info['sql_host'],
                    port=self.sql_info['port'],
                    table_format=table_format['RTPPM'],
                    rtppm_list=self.rtppm_list,
                )
                RTPPM_getdata = get_data(
                    mts=RTPPM_mts,
                    username=self.Email,
                    password=self.password,
                    topic=topic_dict['RTPPM'],
                    listener=Listener_dict['RTPPM'],
                    msg_print=self.get_options['View'],
                    sts=self.get_options['Save_to_SQL'],
                    isdurable=self.get_options['Durable']
                )
                RTPPM_getdata.start()


class EmitStr(QObject):
    textWrit  = pyqtSignal(str)
    def write(self, text):
        self.textWrit.emit(str(text))
    def flush(self):
        pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Saving = QtWidgets.QWidget()
    ui = Ui_Saving()
    ui.setupUi(Saving)
    Saving.show()
    sys.exit(app.exec_())
