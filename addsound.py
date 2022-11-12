# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(350, 140)
        Form.setMinimumSize(QtCore.QSize(350, 140))
        Form.setMaximumSize(QtCore.QSize(350, 140))
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, 81, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 61, 16))
        self.label_2.setObjectName("label_2")
        self.file_name = QtWidgets.QLineEdit(Form)
        self.file_name.setGeometry(QtCore.QRect(100, 7, 211, 20))
        self.file_name.setObjectName("file_name")
        self.category_choose = QtWidgets.QComboBox(Form)
        self.category_choose.setGeometry(QtCore.QRect(100, 40, 211, 22))
        self.category_choose.setObjectName("category_choose")
        self.set_hotkey = QtWidgets.QCheckBox(Form)
        self.set_hotkey.setGeometry(QtCore.QRect(0, 70, 181, 20))
        self.set_hotkey.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.set_hotkey.setTristate(False)
        self.set_hotkey.setObjectName("set_hotkey")
        self.ok_button = QtWidgets.QPushButton(Form)
        self.ok_button.setGeometry(QtCore.QRect(60, 100, 75, 23))
        self.ok_button.setObjectName("ok_button")
        self.cancel_button = QtWidgets.QPushButton(Form)
        self.cancel_button.setGeometry(QtCore.QRect(210, 100, 75, 23))
        self.cancel_button.setObjectName("cancel_button")
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Название звука"))
        self.label_2.setText(_translate("Form", "Категория"))
        self.set_hotkey.setText(_translate("Form", "Назначить горячую клавишу?"))
        self.ok_button.setText(_translate("Form", "ОК"))
        self.cancel_button.setText(_translate("Form", "Отмена"))