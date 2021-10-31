# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'company_info_widget_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(745, 532)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.symbol = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.symbol.setFont(font)
        self.symbol.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.symbol.setObjectName("symbol")
        self.gridLayout.addWidget(self.symbol, 1, 0, 1, 1)
        self.p_close = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.p_close.setFont(font)
        self.p_close.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
        self.p_close.setObjectName("p_close")
        self.gridLayout.addWidget(self.p_close, 1, 3, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.name = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.name.setFont(font)
        self.name.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.name.setObjectName("name")
        self.gridLayout.addWidget(self.name, 1, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.set_chosen = QtWidgets.QPushButton(Form)
        self.set_chosen.setText("")
        self.set_chosen.setObjectName("set_chosen")
        self.horizontalLayout.addWidget(self.set_chosen)
        self.download = QtWidgets.QPushButton(Form)
        self.download.setText("")
        self.download.setObjectName("download")
        self.horizontalLayout.addWidget(self.download)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 3, 1, 1)
        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 3)
        self.verticalLayout.addLayout(self.gridLayout)
        self.widget_graph = QtWidgets.QWidget(Form)
        self.widget_graph.setObjectName("widget_graph")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget_graph)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout.addWidget(self.widget_graph)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.p_high = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.p_high.setFont(font)
        self.p_high.setObjectName("p_high")
        self.gridLayout_2.addWidget(self.p_high, 1, 1, 1, 1)
        self.p_low = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.p_low.setFont(font)
        self.p_low.setObjectName("p_low")
        self.gridLayout_2.addWidget(self.p_low, 2, 1, 1, 1)
        self.p_open = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.p_open.setFont(font)
        self.p_open.setObjectName("p_open")
        self.gridLayout_2.addWidget(self.p_open, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 3)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 5)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.symbol.setText(_translate("Form", "TextLabel"))
        self.p_close.setText(_translate("Form", "TextLabel"))
        self.name.setText(_translate("Form", "TextLabel"))
        self.p_high.setText(_translate("Form", "TextLabel"))
        self.p_low.setText(_translate("Form", "TextLabel"))
        self.p_open.setText(_translate("Form", "TextLabel"))
        self.label.setText(_translate("Form", "open:"))
        self.label_2.setText(_translate("Form", "high:"))
        self.label_3.setText(_translate("Form", "low:"))