
"""

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""



from builtins import zip
from builtins import str
from builtins import range
from PyQt6 import QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .ui.ui_reportGCP import Ui_ReportGCP
from numpy import zeros, sqrt, pi
# create the dialog for zoom to point

class ReportDialog(QtWidgets.QDialog):
    #This class create a report about errors in projection and back-projection
    #It is also here that points are considered behind a hill or not.
    #More generally, if you want to add some functions for checking consistency of
    #projections or back projections, you can do it here.
    #
    #When the Pose dialog window is closed, the errors 
    def __init__(self, model, paramBool, paramList, pathToData, xyzUnProjected, error_report):
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.inconsistent = False
        self.ui = Ui_ReportGCP()
        self.ui.setupUi(self)
        #self.center()
        self.pathToData = pathToData
        self.xyzUnProjected = xyzUnProjected
        self.totalPointsOnHill = 0
        self.model = model
        self.error_report = error_report
        rowCount = model.rowCount()
        errorsPixels = zeros((rowCount,1))
        # errors3D = []
        # n_outOfHorizon = 0
        for row in range(0,rowCount):
            if model.checkValid(row)==0:
                 continue
            index = model.index(row, 6)
            error3D = model.data(index)
            # if error3D > 0:
            #     errors3D.append(error3D)
            # else:
            #     n_outOfHorizon += 1
            index = model.index(row,7)
            errorsPixels[row] = model.data(index)
        # if len(errors3D)>0:
        text = ''
        text += 'Projections errors:'
        
        text += '\n   mean: ' + str(round(error_report['mean'],2)) + ' [pixel]'
        text += '\n   min: ' + str(error_report['min']) + ' [pixel]'
        text += '\n   max: ' + str(error_report['max']) + ' [pixel]'
        text += '\n   std: ' + str(round(error_report['std'],2)) + ' [pixel]\n \n'
        # text += '\n\n3D reprojections errors:'
        # text += '\n   mean: ' + str(round(mean(errors3D),2)) + ' [m]'
        # text += '\n   min: ' + str(min(errors3D)) + ' [m]'
        # text += '\n   max: ' + str(max(errors3D)) + ' [m]'
        # text += '\n   std: ' + str(round(std(errors3D),2)) + ' [m]'
        """
        text += '\n' + str(round(mean(errorsPixels),2))
        text += '\n' + str(min(errorsPixels)) 
        text += '\n' + str(max(errorsPixels))
        text += '\n' + str(round(std(errorsPixels),2))
        text += '\n' + str(round(mean(errors3D),2))
        text += '\n' + str(min(errors3D))
        text += '\n' + str(max(errors3D))
        text += '\n' + str(round(std(errors3D),2)) 
        """
        text += 'Pose estimation parameters:'
        paramText = ['X position','Y Position','Z Position','Tilt [°]','Heading [°]', 'Swing [°]', 'Focal [pixel]']
        for name, bool, value in zip(paramText, paramBool, paramList):
            if bool:
                text += '\n'+ name + ', Free :' + ' ' + str(round(value,6))
            else:
                text += '\n'+ name + ', Fixed: ' + ' ' + str(round(value,6))
            
        self.ui.reportBrowser.setText(text)
        self.ui.pushButton.pressed.connect(self.saveReport)
        # test = self.isBehindHill(paramList,errors3D)
        # if test:
        #     QMessageBox.warning(self, "Reprojection - Warning",
        #             "%i GCP seems to be not visible from the camera location! The computed position could be behind relief or within the ground." % self.totalPointsOnHill)
        # else: 
        #     QMessageBox.warning(self, "Reprojection - Warning",
        #             "inconsistent pose, consider to provide apriori values")
        #     self.inconsistent = True
            
    def center(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def saveReport(self):
        #Save a small text file which contain the same information as the dialog. 
        path = self.pathToData + '/report.txt'
        fSaveName = QFileDialog.getSaveFileName(self, 'Save your report as...',\
                                                  path,"File (*.txt)")[0]
        if fSaveName:
            f = open(fSaveName, 'w')
            data = self.ui.reportBrowser.toPlainText()
            f.write(data)
            f.close()
            self.close()
        
    def isBehindHill(self, paramList,errors3D):
        # For checking if a point stand behind a hill, we compare the error
        # with the distance between camera position and back-projection
        x0 = -paramList[0]
        y0 = paramList[1]

        totalPointsOnHill = 0
        for xyz,error in zip(self.xyzUnProjected,errors3D):
            x = xyz[0]
            y = xyz[2]
            planimetricDistanceToCameraPosition = sqrt((x-x0)**2+(y-y0)**2)

            #If the error is bigger than the distance between camera position and 
            # back-projection, the point is considered to be behind a hill.
            if planimetricDistanceToCameraPosition < error:
                totalPointsOnHill += 1
        if totalPointsOnHill == 0:
            return False
        else:
            self.totalPointsOnHill = totalPointsOnHill
            return True
        
        
