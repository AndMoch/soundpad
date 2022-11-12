# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'soundpad.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 500)
        MainWindow.setMinimumSize(QtCore.QSize(700, 500))
        MainWindow.setMaximumSize(QtCore.QSize(700, 500))
        font = QtGui.QFont()
        font.setKerning(True)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.categories_table = QtWidgets.QTableWidget(self.centralwidget)
        self.categories_table.setGeometry(QtCore.QRect(10, 80, 201, 351))
        self.categories_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.categories_table.setObjectName("categories_table")
        self.categories_table.setColumnCount(0)
        self.categories_table.setRowCount(0)
        self.categories_table.horizontalHeader().setStretchLastSection(True)
        self.sounds_table = QtWidgets.QTableWidget(self.centralwidget)
        self.sounds_table.setGeometry(QtCore.QRect(220, 80, 451, 351))
        self.sounds_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.sounds_table.setObjectName("sounds_table")
        self.sounds_table.setColumnCount(0)
        self.sounds_table.setRowCount(0)
        self.sounds_table.horizontalHeader().setStretchLastSection(True)
        self.add_sound = QtWidgets.QPushButton(self.centralwidget)
        self.add_sound.setGeometry(QtCore.QRect(10, 10, 201, 23))
        self.add_sound.setObjectName("add_sound")
        self.add_category = QtWidgets.QPushButton(self.centralwidget)
        self.add_category.setGeometry(QtCore.QRect(10, 40, 201, 23))
        self.add_category.setObjectName("add_category")
        self.activate_hotkeys = QtWidgets.QRadioButton(self.centralwidget)
        self.activate_hotkeys.setGeometry(QtCore.QRect(20, 460, 191, 17))
        self.activate_hotkeys.setObjectName("activate_hotkeys")
        self.play_button = QtWidgets.QPushButton(self.centralwidget)
        self.play_button.setGeometry(QtCore.QRect(220, 40, 75, 23))
        self.play_button.setObjectName("play_button")
        self.pause_button = QtWidgets.QPushButton(self.centralwidget)
        self.pause_button.setGeometry(QtCore.QRect(300, 40, 75, 23))
        self.pause_button.setObjectName("pause_button")
        self.stop_button = QtWidgets.QPushButton(self.centralwidget)
        self.stop_button.setGeometry(QtCore.QRect(380, 40, 75, 23))
        self.stop_button.setObjectName("stop_button")
        self.volume_slider = QtWidgets.QSlider(self.centralwidget)
        self.volume_slider.setGeometry(QtCore.QRect(540, 40, 131, 22))
        self.volume_slider.setMaximum(100)
        self.volume_slider.setProperty("value", 100)
        self.volume_slider.setOrientation(QtCore.Qt.Horizontal)
        self.volume_slider.setInvertedControls(False)
        self.volume_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.volume_slider.setTickInterval(0)
        self.volume_slider.setObjectName("volume_slider")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(480, 40, 61, 20))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.add_sound.setText(_translate("MainWindow", "Добавить новый звук "))
        self.add_category.setText(_translate("MainWindow", "Добавить новую категорию"))
        self.activate_hotkeys.setText(_translate("MainWindow", "Активировать горячие клавиши"))
        self.play_button.setText(_translate("MainWindow", "Включить"))
        self.pause_button.setText(_translate("MainWindow", "Пауза"))
        self.stop_button.setText(_translate("MainWindow", "Выключить"))
        self.label.setText(_translate("MainWindow", "Громкость"))