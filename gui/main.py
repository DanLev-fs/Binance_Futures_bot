# This Python file uses the following encoding: utf-8
import sys
import os
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QVBoxLayout, QSpacerItem
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QDialog, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap
import dialog
import mainform
import delete
import resources
import edit
import binance_f
from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *
from binance_f.model.constant import *
import sqlite3
import threading

class AccountsDB():
    def __init__(self):
        self.sql = sqlite3.connect('accounts.db')
        self.cursor = self.sql.cursor()
        try:
            self.cursor.execute("CREATE TABLE accounts (name text, api text, private text);")
            self.sql.commit()
        except:
            pass

    def GetAccounts(self):
        self.cursor.execute("select * from accounts;")
        return self.cursor.fetchall()

    def SaveAccount(self, name, api, private):
        accs = self.GetAccounts()
        if (accs != []):
            for i in accs:
                if (name != i[0] and api != i[1] and private != i[2]):
                    self.cursor.execute("insert into accounts (name, api, private) values (?,?,?);", (name, api, private))
                    self.sql.commit()
                else:  
                    return False
        else: 
            self.cursor.execute("insert into accounts (name, api, private) values (?,?,?);", (name, api, private))
            self.sql.commit()
        return True
    
    def DeleteAccount(self, name):
        self.cursor.execute('DELETE FROM accounts WHERE name="'+name+'";')
        self.sql.commit()
    
    def AccountUpdate(self, name, api, private):
        self.cursor.execute("update accounts set name=?, api=?, private=? where name=?;", (name, api, private, name))
        self.sql.commit()

class binance():
    def GetOrders(self, api, private):
        try:
            request_client = RequestClient(api_key=api, secret_key=private)
            result = request_client.get_adl_quantile()
            results = []
            for i in result:
                results.append(request_client.get_all_orders(symbol=i["symbol"]))
            return results
        except:
            pass

    def GetBalance(self, api, private):
        try:
            request_client = RequestClient(api_key=api, secret_key=private)
            result = request_client.get_account_information_v2()
            return result.availableBalance
        except binance_f.exception.binanceapiexception.BinanceApiException:
            return -1

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.ui = mainform.Ui_MainWindow()
        self.ui.setupUi(self)
        self.connectacc = self.findChild(QPushButton, 'connectacc')
        self.listwidget = self.findChild(QVBoxLayout, 'verticalLayout_3')
        self.connectacc.clicked.connect(self.connectaccE)
        self.binanceapi = binance()
        self.accountdb = AccountsDB()

    def CheckAccountsFromDB(self):
        accs = self.accountdb.GetAccounts()
        if (accs != []):
            for i in accs:
                name = i[0]
                api = i[1]
                private = i[2]
                self.AddAccount(name, api, private, self.binanceapi.GetBalance(api, private))
                print(self.binanceapi.GetOrders(api, private))

    def AddAccount(self, name, api, private, balance):
        frame = QFrame(self)
        frame.setMinimumSize(QSize(0, 70))
        frame.setMaximumSize(QSize(16777215, 70))
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)
        horizontalLayout_2 = QHBoxLayout(frame)
        label_7 = QLabel("  ", frame)
        horizontalLayout_2.addWidget(label_7)
        label_2 = QLabel(frame)
        label_2.setMinimumSize(QSize(30, 35))
        label_2.setMaximumSize(QSize(30, 35))
        label_2.setPixmap(QPixmap(u":/binance/binance-coin-bnb-logo.png"))
        label_2.setScaledContents(True)
        horizontalLayout_2.addWidget(label_2)

        verticalLayout_2 = QVBoxLayout()
        verticalLayout_2.setSpacing(0)
        verticalLayout_2.setObjectName(u"verticalLayout_2")
        #verticalLayout_2.setContentsMargins(-1, 10, 0, 10)
        label = QLabel("<html><head/><body><p><span style=\" font-size:14pt;\">Binance </span><span style=\" font-size:12pt; vertical-align:super;\">Futures</span></p></body></html>", frame)
        horizontalLayout_2.addWidget(label)
        label_4 = QLabel("  "+name+"  ", frame)
        label_4.setMaximumSize(QSize(16777215, 15))
        label_4.setStyleSheet("color:grey")
        verticalLayout_2.addWidget(label)
        verticalLayout_2.addWidget(label_4)

        horizontalLayout_2.addLayout(verticalLayout_2)
        label_8 = QLabel("  ", frame)
        label_5 = QLabel(frame)
        connect = "Подключена"
        label_5.setStyleSheet("color:green")
        if (balance == -1):
            connect = "Ошибка"
            label_5.setStyleSheet("color:red")
        label_5.setText(connect)
        horizontalLayout_2.addWidget(label_5)
        label_9 = QLabel("  ", frame)
        horizontalLayout_2.addWidget(label_9)
        def editE(event):
            edites = QDialog()
            ui = edit.Ui_Dialog()
            ui.setupUi(edites)
            if (edites.exec_() == QDialog.Accepted):
                frame.deleteLater()
                self.accountdb.AccountUpdate(name, api, private)
                self.AddAccount(name, api, private, balance)
        label_6 = QLabel("Редактировать", frame)
        label_6.setStyleSheet("color:grey")
        label_6.mousePressEvent = editE
        horizontalLayout_2.addWidget(label_6)
        label_11 = QLabel("  ", frame)
        horizontalLayout_2.addWidget(label_11)
        def deleteE(event):
            deletes = QDialog()
            ui = delete.Ui_Dialog()
            ui.setupUi(deletes)
            if (deletes.exec_() == QDialog.Accepted):
                frame.deleteLater()
                self.accountdb.DeleteAccount(name)
        label_10 = QLabel("Удалить", frame)
        label_10.setStyleSheet("color:red")
        label_10.mousePressEvent = deleteE
        horizontalLayout_2.addWidget(label_10)
        horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontalLayout_2.addItem(horizontalSpacer)
        label_12 = QLabel("Баланс: ", frame)
        horizontalLayout_2.addWidget(label_12)
        label_3 = QLabel("$"+str(balance), frame)
        horizontalLayout_2.addWidget(label_3)
        self.listwidget.insertWidget(self.listwidget.count() - 1, frame)

    def connectaccE(self):
        dialogu = QDialog()
        ui = dialog.Ui_Dialog()
        ui.setupUi(dialogu)
        if (dialogu.exec_() == QDialog.Accepted):
                api, private, name = ui.GetApi()
                balance = self.binanceapi.GetBalance(api, private)
                if (self.accountdb.SaveAccount(name, api, private)):
                    self.AddAccount(name, api, private, balance)
        dialogu.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    threading.Thread(target=window.CheckAccountsFromDB()).start()
    window.show()
    sys.exit(app.exec_())
