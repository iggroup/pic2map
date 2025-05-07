# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_PoseDialog(object):
    def setupUi(self, PoseDialog):
        self.needRefresh = PoseDialog.needRefresh
        PoseDialog.setObjectName(_fromUtf8("PoseDialog"))
        PoseDialog.adjustSize()
        self.mainGridLayout = QtWidgets.QGridLayout(PoseDialog)
        self.mainGridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtWidgets.QDialogButtonBox(PoseDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.mainGridLayout.addWidget(self.buttonBox, 3, 4, 1, 1)
        self.frame = QtWidgets.QFrame(PoseDialog)
        self.frame.setMinimumSize(QtCore.QSize(0, 318))
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.parametersGridLayout = QtWidgets.QGridLayout(self.frame)
        self.parametersGridLayout.setObjectName(_fromUtf8("parametersGridLayout"))

        self.XPosFree = QtWidgets.QRadioButton(self.frame)
        self.XPosFree.setObjectName(_fromUtf8("XPosFree"))
        self.XPosFixed = QtWidgets.QRadioButton(self.frame)
        self.XPosFixed.setObjectName(_fromUtf8("XPosFixed"))
        self.XPosIni = QtWidgets.QRadioButton(self.frame)
        self.XPosIni.setObjectName(_fromUtf8("XPosIni"))
        self.XPosGroup = QtWidgets.QButtonGroup(PoseDialog)
        self.XPosGroup.setObjectName(_fromUtf8("XPosGroup"))
        self.XPosGroup.addButton(self.XPosFixed)
        self.XPosGroup.addButton(self.XPosFree)
        self.XPosGroup.addButton(self.XPosIni)
        self.parametersGridLayout.addWidget(self.XPosFree, 0, 1, 1, 1)
        self.parametersGridLayout.addWidget(self.XPosFixed, 0, 2, 1, 1)
        self.parametersGridLayout.addWidget(self.XPosIni, 0, 3, 1, 1)
        
        self.YPosFree = QtWidgets.QRadioButton(self.frame)
        self.YPosFree.setObjectName(_fromUtf8("YPosFree"))
        self.YPosFixed = QtWidgets.QRadioButton(self.frame)
        self.YPosFixed.setObjectName(_fromUtf8("YPosFixed"))
        self.YPosIni = QtWidgets.QRadioButton(self.frame)
        self.YPosIni.setObjectName(_fromUtf8("YPosIni"))
        self.YPosGroup = QtWidgets.QButtonGroup(PoseDialog)
        self.YPosGroup.setObjectName(_fromUtf8("YPosGroup"))
        self.YPosGroup.addButton(self.YPosFree)
        self.YPosGroup.addButton(self.YPosFixed)
        self.YPosGroup.addButton(self.YPosIni)
        self.parametersGridLayout.addWidget(self.YPosFree, 1, 1, 1, 1)
        self.parametersGridLayout.addWidget(self.YPosFixed, 1, 2, 1, 1)
        self.parametersGridLayout.addWidget(self.YPosIni, 1, 3, 1, 1)

        self.ZPosFree = QtWidgets.QRadioButton(self.frame)
        self.ZPosFree.setObjectName(_fromUtf8("ZPosFree"))
        self.ZPosFixed = QtWidgets.QRadioButton(self.frame)
        self.ZPosFixed.setObjectName(_fromUtf8("ZPosFixed"))
        self.ZPosIni = QtWidgets.QRadioButton(self.frame)
        self.ZPosIni.setObjectName(_fromUtf8("ZPosIni"))
        self.ZPoseGroup = QtWidgets.QButtonGroup(PoseDialog)
        self.ZPoseGroup.setObjectName(_fromUtf8("ZPoseGroup"))
        self.ZPoseGroup.addButton(self.ZPosFixed)
        self.ZPoseGroup.addButton(self.ZPosFree)
        self.ZPoseGroup.addButton(self.ZPosIni)
        self.parametersGridLayout.addWidget(self.ZPosFree, 2, 1, 1, 1)
        self.parametersGridLayout.addWidget(self.ZPosFixed, 2, 2, 1, 1)
        self.parametersGridLayout.addWidget(self.ZPosIni, 2, 3, 1, 1)
        
        self.tiltFree = QtWidgets.QRadioButton(self.frame)
        self.tiltFree.setObjectName(_fromUtf8("tiltFree"))
        self.tiltFixed = QtWidgets.QRadioButton(self.frame)
        self.tiltFixed.setObjectName(_fromUtf8("tiltFixed"))
        self.tiltIni = QtWidgets.QRadioButton(self.frame)
        self.tiltIni.setObjectName(_fromUtf8("tiltIni"))
        self.tiltgroup = QtWidgets.QButtonGroup(PoseDialog)
        self.tiltgroup.setObjectName(_fromUtf8("tiltgroup"))
        self.tiltgroup.addButton(self.tiltFree)
        self.tiltgroup.addButton(self.tiltFixed)
        self.tiltgroup.addButton(self.tiltIni)
        self.parametersGridLayout.addWidget(self.tiltFree, 3, 1, 1, 1)
        self.parametersGridLayout.addWidget(self.tiltFixed, 3, 2, 1, 1)
        self.parametersGridLayout.addWidget(self.tiltIni, 3, 3, 1, 1)
        
        self.headingFree = QtWidgets.QRadioButton(self.frame)
        self.headingFree.setObjectName(_fromUtf8("headingFree"))
        self.headingFixed = QtWidgets.QRadioButton(self.frame)
        self.headingFixed.setObjectName(_fromUtf8("headingFixed"))
        self.headingIni = QtWidgets.QRadioButton(self.frame)
        self.headingIni.setObjectName(_fromUtf8("headingIni"))
        self.headinggroup = QtWidgets.QButtonGroup(PoseDialog)
        self.headinggroup.setObjectName(_fromUtf8("headinggroup"))
        self.headinggroup.addButton(self.headingFree)
        self.headinggroup.addButton(self.headingFixed)
        self.headinggroup.addButton(self.headingIni)
        self.parametersGridLayout.addWidget(self.headingFree, 4, 1, 1, 1)
        self.parametersGridLayout.addWidget(self.headingFixed, 4, 2, 1, 1)
        self.parametersGridLayout.addWidget(self.headingIni, 4, 3, 1, 1)
        
        self.swingFree = QtWidgets.QRadioButton(self.frame)
        self.swingFree.setObjectName(_fromUtf8("swingFree"))
        self.swingFixed = QtWidgets.QRadioButton(self.frame)
        self.swingFixed.setObjectName(_fromUtf8("swingFixed"))
        self.swingIni = QtWidgets.QRadioButton(self.frame)
        self.swingIni.setObjectName(_fromUtf8("swingIni"))
        self.swinggroup = QtWidgets.QButtonGroup(PoseDialog)
        self.swinggroup.setObjectName(_fromUtf8("swinggroup"))
        self.swinggroup.addButton(self.swingFree)
        self.swinggroup.addButton(self.swingFixed)
        self.swinggroup.addButton(self.swingIni)
        self.parametersGridLayout.addWidget(self.swingFree, 5, 1, 1, 1)
        self.parametersGridLayout.addWidget(self.swingFixed, 5, 2, 1, 1)
        self.parametersGridLayout.addWidget(self.swingIni, 5, 3, 1, 1)
        
        self.focalFree = QtWidgets.QRadioButton(self.frame)
        self.focalFree.setObjectName(_fromUtf8("focalFree"))
        self.focalFixed = QtWidgets.QRadioButton(self.frame)
        self.focalFixed.setObjectName(_fromUtf8("focalFixed"))
        self.focalIni = QtWidgets.QRadioButton(self.frame)
        self.focalIni.setObjectName(_fromUtf8("focalIni"))
        self.focalgroup = QtWidgets.QButtonGroup(PoseDialog)
        self.focalgroup.setObjectName(_fromUtf8("focalgroup"))
        self.focalgroup.addButton(self.focalFixed)
        self.focalgroup.addButton(self.focalFree)
        self.focalgroup.addButton(self.focalIni)
        self.parametersGridLayout.addWidget(self.focalFree, 6, 1, 1, 1)
        self.parametersGridLayout.addWidget(self.focalFixed, 6, 2, 1, 1)
        self.parametersGridLayout.addWidget(self.focalIni, 6, 3, 1, 1)

        self.XPosLine = QtWidgets.QLineEdit(self.frame)
        self.XPosLine.setObjectName(_fromUtf8("XPosLine"))
        self.parametersGridLayout.addWidget(self.XPosLine, 0, 4, 1, 1)
        
        self.YPosLine = QtWidgets.QLineEdit(self.frame)
        self.YPosLine.setObjectName(_fromUtf8("YPosLine"))
        self.parametersGridLayout.addWidget(self.YPosLine, 1, 4, 1, 1)
        
        self.ZPosLine = QtWidgets.QLineEdit(self.frame)
        self.ZPosLine.setObjectName(_fromUtf8("ZPosLine"))
        self.parametersGridLayout.addWidget(self.ZPosLine, 2, 4, 1, 1)
        
        self.tiltLine = QtWidgets.QLineEdit(self.frame)
        self.tiltLine.setObjectName(_fromUtf8("tiltLine"))
        self.parametersGridLayout.addWidget(self.tiltLine, 3, 4, 1, 1)
        
        self.headingLine = QtWidgets.QLineEdit(self.frame)
        self.headingLine.setObjectName(_fromUtf8("headingLine"))
        self.parametersGridLayout.addWidget(self.headingLine, 4, 4, 1, 1)
        
        self.swingLine = QtWidgets.QLineEdit(self.frame)
        self.swingLine.setObjectName(_fromUtf8("swingLine"))
        self.parametersGridLayout.addWidget(self.swingLine, 5, 4, 1, 1)
        
        self.focalLine = QtWidgets.QLineEdit(self.frame)
        self.focalLine.setObjectName(_fromUtf8("focalLine"))
        self.parametersGridLayout.addWidget(self.focalLine, 6, 4, 1, 1)

        self.XPosLabel = QtWidgets.QLabel(self.frame)
        self.XPosLabel.setObjectName(_fromUtf8("XPosLabel"))
        self.parametersGridLayout.addWidget(self.XPosLabel, 0, 0, 1, 1)
        self.YPosLabel = QtWidgets.QLabel(self.frame)
        self.YPosLabel.setObjectName(_fromUtf8("YPosLabel"))
        self.parametersGridLayout.addWidget(self.YPosLabel, 1, 0, 1, 1)
        self.ZPosLabel = QtWidgets.QLabel(self.frame)
        self.ZPosLabel.setObjectName(_fromUtf8("ZPosLabel"))
        self.parametersGridLayout.addWidget(self.ZPosLabel, 2, 0, 1, 1)
        self.tiltLabel = QtWidgets.QLabel(self.frame)
        self.tiltLabel.setObjectName(_fromUtf8("tiltLabel"))
        self.parametersGridLayout.addWidget(self.tiltLabel, 3, 0, 1, 1)
        self.headingLabel = QtWidgets.QLabel(self.frame)
        self.headingLabel.setObjectName(_fromUtf8("headingLabel"))
        self.parametersGridLayout.addWidget(self.headingLabel, 4, 0, 1, 1)
        self.swingLabel = QtWidgets.QLabel(self.frame)
        self.swingLabel.setObjectName(_fromUtf8("swingLabel"))
        self.parametersGridLayout.addWidget(self.swingLabel, 5, 0, 1, 1)
        self.focalLabel = QtWidgets.QLabel(self.frame)
        self.focalLabel.setObjectName(_fromUtf8("focalLabel"))
        self.parametersGridLayout.addWidget(self.focalLabel, 6, 0, 1, 1)
   
        self.mainGridLayout.addWidget(self.frame, 1, 1, 1, 4)

        self.poseEstimationButton = QtWidgets.QCommandLinkButton(PoseDialog)
        self.poseEstimationButton.setObjectName(_fromUtf8("poseEstimationButton"))
        self.mainGridLayout.addWidget(self.poseEstimationButton, 2, 3, 1, 2)

        self.exifButton = QtWidgets.QPushButton(PoseDialog)
        self.exifButton.setObjectName(_fromUtf8("exifButton"))
        self.mainGridLayout.addWidget(self.exifButton, 2, 2, 1, 1)

        self.importParamButton = QtWidgets.QPushButton(PoseDialog)
        self.importParamButton.setObjectName(_fromUtf8("importParamButton"))
        self.mainGridLayout.addWidget(self.importParamButton, 2, 1, 1, 1)

        self.XPosFree.setChecked(True)
        self.YPosFree.setChecked(True)
        self.ZPosFree.setChecked(True)
        self.tiltFree.setChecked(True)
        self.headingFree.setChecked(True)
        self.swingFree.setChecked(True)
        self.focalFree.setChecked(True)
        
        self.reportButton = QtWidgets.QPushButton(PoseDialog)
        self.reportButton.setObjectName(_fromUtf8("reportButton"))
        self.reportButton.setEnabled(False)
        self.mainGridLayout.addWidget(self.reportButton, 3, 2, 1, 1)
        
        self.cameraPositionButton = QtWidgets.QPushButton(PoseDialog)
        self.cameraPositionButton.setObjectName(_fromUtf8("cameraPositionButton"))
        self.mainGridLayout.addWidget(self.cameraPositionButton, 3, 1, 1, 1)
        self.cameraPositionButton.setEnabled(False)

        self.retranslateUi(PoseDialog)
        self.buttonBox.accepted.connect(PoseDialog.accept)
        self.buttonBox.rejected.connect(PoseDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PoseDialog)
        
        self.XPosLine.setReadOnly(True)
        self.XPosFixed.toggled.connect(self.XPosFixedclicked)
        self.XPosFree.toggled.connect(self.XPosFreeclicked)
        self.XPosIni.toggled.connect(self.XPosIniclicked)
        self.XPosLine.textEdited.connect(self.lineEditEdited)
        
        self.YPosLine.setReadOnly(True)
        self.YPosFixed.toggled.connect(self.YPosFixedclicked)
        self.YPosFree.toggled.connect(self.YPosFreeclicked)
        self.YPosIni.toggled.connect(self.YPosIniclicked)
        self.YPosLine.textEdited.connect(self.lineEditEdited)
        
        self.ZPosLine.setReadOnly(True)
        self.ZPosFixed.toggled.connect(self.ZPosFixedclicked)
        self.ZPosFree.toggled.connect(self.ZPosFreeclicked)
        self.ZPosIni.toggled.connect(self.ZPosIniclicked)
        self.ZPosLine.textEdited.connect(self.lineEditEdited)
        
        self.headingLine.setReadOnly(True)
        self.headingFixed.toggled.connect(self.headingFixedclicked)
        self.headingFree.toggled.connect(self.headingFreeclicked)
        self.headingIni.toggled.connect(self.headingIniclicked)
        self.headingLine.textEdited.connect(self.lineEditEdited)
        
        self.tiltLine.setReadOnly(True)
        self.tiltFixed.toggled.connect(self.tiltFixedclicked)
        self.tiltFree.toggled.connect(self.tiltFreeclicked)
        self.tiltIni.toggled.connect(self.tiltIniclicked)
        self.tiltLine.textEdited.connect(self.lineEditEdited)
        
        self.swingLine.setReadOnly(True)
        self.swingFixed.toggled.connect(self.swingFixedclicked)
        self.swingFree.toggled.connect(self.swingFreeclicked)
        self.swingIni.toggled.connect(self.swingIniclicked)
        self.swingLine.textEdited.connect(self.lineEditEdited)
        
        self.focalLine.setReadOnly(True)
        self.focalFixed.toggled.connect(self.focalFixedclicked)
        self.focalFree.toggled.connect(self.focalFreeclicked)
        self.focalIni.toggled.connect(self.focalIniclicked)
        self.focalLine.textEdited.connect(self.lineEditEdited)

    def hide_layout(self, layout):
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.hide()  # Hide each widget in the layout

    def lineEditEdited(self):
        self.needRefresh.emit() 
    
    def focalFixedclicked(self):
        if self.focalFixed.isChecked():
            self.focalLine.setReadOnly(False)
            self.needRefresh.emit()  
    def focalFreeclicked(self):
        if self.focalFree.isChecked():
            #self.focalLine.setText('')
            self.focalLine.setReadOnly(True)
            self.needRefresh.emit()
    def focalIniclicked(self):
        if self.focalIni.isChecked():
            self.focalLine.setReadOnly(False)
            self.needRefresh.emit()
            
    def swingFixedclicked(self):
        if self.swingFixed.isChecked():
            self.swingLine.setReadOnly(False) 
            self.needRefresh.emit()
    def swingFreeclicked(self):
        if self.swingFree.isChecked():
            #self.swingLine.setText('')
            self.swingLine.setReadOnly(True)
            self.needRefresh.emit()
    def swingIniclicked(self):
        if self.swingIni.isChecked():
            self.swingLine.setReadOnly(False)
            self.needRefresh.emit()
            
    def tiltFixedclicked(self):
        if self.tiltFixed.isChecked():
            self.tiltLine.setReadOnly(False)
            self.needRefresh.emit() 
    def tiltFreeclicked(self):
        if self.tiltFree.isChecked():
            #self.tiltLine.setText('')
            self.tiltLine.setReadOnly(True)
            self.needRefresh.emit()
    def tiltIniclicked(self):
        if self.tiltIni.isChecked():
            self.tiltLine.setReadOnly(False)
            self.needRefresh.emit()
            
    def headingFixedclicked(self):
        if self.headingFixed.isChecked():
            self.headingLine.setReadOnly(False)
            self.needRefresh.emit() 
    def headingFreeclicked(self):
        if self.headingFree.isChecked():
            #self.headingLine.setText('')
            self.headingLine.setReadOnly(True)
            self.needRefresh.emit()
    def headingIniclicked(self):
        if self.headingIni.isChecked():
            self.headingLine.setReadOnly(False)
            self.needRefresh.emit()
            
    def ZPosFixedclicked(self):
        if self.ZPosFixed.isChecked():
            self.ZPosLine.setReadOnly(False)
            self.needRefresh.emit() 
    def ZPosFreeclicked(self):
        if self.ZPosFree.isChecked():
            #self.ZPosLine.setText('')
            self.ZPosLine.setReadOnly(True)
            self.needRefresh.emit()
    def ZPosIniclicked(self):
        if self.ZPosIni.isChecked():
            self.ZPosLine.setReadOnly(False)
            self.needRefresh.emit()
            
    def YPosFixedclicked(self):
        if self.YPosFixed.isChecked():
            self.YPosLine.setReadOnly(False)
            self.needRefresh.emit() 
    def YPosFreeclicked(self):
        if self.YPosFree.isChecked():
            #self.YPosLine.setText('')
            self.YPosLine.setReadOnly(True)
            self.needRefresh.emit()
    def YPosIniclicked(self):
        if self.YPosIni.isChecked():
            self.YPosLine.setReadOnly(False)
            self.needRefresh.emit()
            
    def XPosFixedclicked(self):
        if self.XPosFixed.isChecked():
            self.XPosLine.setReadOnly(False)
            self.needRefresh.emit()
    def XPosFreeclicked(self):
        if self.XPosFree.isChecked():
            #self.XPosLine.setText('')
            self.XPosLine.setReadOnly(True)
            self.needRefresh.emit()
    def XPosIniclicked(self):
        if self.XPosIni.isChecked():
            self.XPosLine.setReadOnly(False)
            self.needRefresh.emit()
            
            
    def retranslateUi(self, PoseDialog):
        PoseDialog.setWindowTitle(_translate("PoseDialog", "Pose estimation", None))
        
        self.XPosFree.setText(_translate("PoseDialog", "Free", None))
        self.XPosFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.XPosIni.setText(_translate("PoseDialog", "Apriori", None))
        
        self.YPosFree.setText(_translate("PoseDialog", "Free", None))
        self.YPosFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.YPosIni.setText(_translate("PoseDialog", "Apriori", None))
        
        self.ZPosFree.setText(_translate("PoseDialog", "Free", None))
        self.ZPosFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.ZPosIni.setText(_translate("PoseDialog", "Apriori", None))
        
        self.tiltFree.setText(_translate("PoseDialog", "Free", None))
        self.tiltFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.tiltIni.setText(_translate("PoseDialog", "Apriori", None))
        
        self.headingFree.setText(_translate("PoseDialog", "Free", None))
        self.headingFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.headingIni.setText(_translate("PoseDialog", "Apriori", None))
        
        self.swingFree.setText(_translate("PoseDialog", "Free", None))
        self.swingFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.swingIni.setText(_translate("PoseDialog", "Apriori", None))
        
        self.focalFree.setText(_translate("PoseDialog", "Free", None))
        self.focalFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.focalIni.setText(_translate("PoseDialog", "Apriori", None))

        self.XPosLabel.setText(_translate("PoseDialog", "X Position [m]", None))
        self.YPosLabel.setText(_translate("PoseDialog", "Y Position [m]", None))
        self.ZPosLabel.setText(_translate("PoseDialog", "Z Position [m]", None))
        self.tiltLabel.setText(_translate("PoseDialog", "tilt [°]", None))
        self.headingLabel.setText(_translate("PoseDialog", "heading [°]", None))
        self.swingLabel.setText(_translate("PoseDialog", "swing [°]", None))
        self.focalLabel.setText(_translate("PoseDialog", "focal [pixel]", None))
        self.reportButton.setText(_translate("PoseDialog", "Report on GCPs", None))
        self.cameraPositionButton.setText(_translate("PoseDialog" , "Export camera position", None))

        self.exifButton.setText(_translate("PoseDialog", "Show EXIF", None))
        self.importParamButton.setText(_translate("PoseDialog", "Import camera position", None))

        self.poseEstimationButton.setText(_translate("PoseDialog", "Update Pose Estimation", None))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PoseDialog = QtWidgets.QDialog()
    ui = Ui_PoseDialog()
    ui.setupUi(PoseDialog)
    PoseDialog.show()
    sys.exit(app.exec())

