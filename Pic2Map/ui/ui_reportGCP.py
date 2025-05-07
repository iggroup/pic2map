# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets


class Ui_ReportGCP(object):
    def setupUi(self, ReportGCP):
        ReportGCP.setObjectName("ReportGCP")
        ReportGCP.resize(382, 277)
        self.gridLayout = QtWidgets.QGridLayout(ReportGCP)
        self.gridLayout.setObjectName("gridLayout")
        self.reportBrowser = QtWidgets.QTextBrowser(ReportGCP)
        self.reportBrowser.setObjectName("reportBrowser")
        self.reportBrowser.setStyleSheet('font-family : Courier')
        self.gridLayout.addWidget(self.reportBrowser, 0, 0, 1, 2)
        self.pushButton = QtWidgets.QPushButton(ReportGCP)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(ReportGCP)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)

        self.retranslateUi(ReportGCP)
        self.buttonBox.accepted.connect(ReportGCP.accept)
        self.buttonBox.rejected.connect(ReportGCP.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportGCP)

    def retranslateUi(self, ReportGCP):
        _translate = QtCore.QCoreApplication.translate
        ReportGCP.setWindowTitle(_translate("ReportGCP", "Report on GCPs"))
        self.pushButton.setText(_translate("ReportGCP", "Save Report"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ReportGCP = QtWidgets.QDialog()
    ui = Ui_ReportGCP()
    ui.setupUi(ReportGCP)
    ReportGCP.show()
    sys.exit(app.exec())
