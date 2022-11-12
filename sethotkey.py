# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Hotkey_choose(object):
    def setupUi(self, Hotkey_choose):
        Hotkey_choose.setObjectName("Hotkey_choose")
        Hotkey_choose.resize(280, 104)
        self.ok_button = QtWidgets.QPushButton(Hotkey_choose)
        self.ok_button.setGeometry(QtCore.QRect(40, 70, 75, 23))
        self.ok_button.setObjectName("ok_button")
        self.cancel_button = QtWidgets.QPushButton(Hotkey_choose)
        self.cancel_button.setGeometry(QtCore.QRect(170, 70, 75, 23))
        self.cancel_button.setObjectName("cancel_button")
        self.key_line = QtWidgets.QLineEdit(Hotkey_choose)
        self.key_line.setGeometry(QtCore.QRect(40, 38, 205, 20))
        self.key_line.setReadOnly(True)
        self.key_line.setObjectName("key_line")
        self.label = QtWidgets.QLabel(Hotkey_choose)
        self.label.setGeometry(QtCore.QRect(68, 10, 151, 16))
        self.label.setObjectName("label")
        self.retranslateUi(Hotkey_choose)
        QtCore.QMetaObject.connectSlotsByName(Hotkey_choose)

    def retranslateUi(self, Hotkey_choose):
        _translate = QtCore.QCoreApplication.translate
        Hotkey_choose.setWindowTitle(_translate("Hotkey_choose", "Form"))
        self.ok_button.setText(_translate("Hotkey_choose", "ОК"))
        self.cancel_button.setText(_translate("Hotkey_choose", "Отмена"))
        self.label.setText(_translate("Hotkey_choose", "Нажмите на любую клавишу"))