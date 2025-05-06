
"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
This file contains the algorithm of pose estimation. It is therefore the
most computational and the only one with non-trivial mathematical
expressions.

Part of this file has been written by Marcos Duarte - duartexyz@gmail.com.
More precisely, Marcos has written the functions DLTcalibration and Normalization.
"""
from __future__ import division
from __future__ import print_function

from builtins import str
from builtins import range
from past.utils import old_div
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .ui_pose import Ui_Pose
from copy import copy
from PIL import Image
import piexif
from numpy import any, zeros, array, sin, cos, dot, linalg, pi, asarray, mean, std, min, max, sqrt, flipud, std, concatenate, ones, arccos, arcsin, arctan,arctan2, size, abs, matrix, diag
from .reportDialog import ReportDialog
from .exifInfo import ExifInfo
from osgeo import ogr, osr
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
import os
from .GCPs import GCPTableModel
from .smapshotgeoreferencer import georeferencerUtils as georef_utils

class Pose_dialog(QtWidgets.QDialog):
    update = pyqtSignal()
    needRefresh = pyqtSignal()
    importUpdate = pyqtSignal()
    def __init__(self, gcp_table_model: GCPTableModel, paramPosIni, positionFixed, sizePicture, whoIsChecked,pathToData,picture_name, iface,crs):
        #QtGui.QDialog.__init__(self)
        QtWidgets.QDialog.__init__(self)
        self.uiPose = Ui_Pose()
        self.uiPose.setupUi(self)
        #self.center()
        self.done = False
        self.sizePicture = sizePicture
        self.gcp_table_model = gcp_table_model
        self.whoIsChecked = whoIsChecked
        self.pathToData = pathToData
        self.xyzUnProjected = None
        self.picture_name = picture_name
        self.paramPosIni = paramPosIni
        self.iface = iface
        self.crs = crs
        self.result = paramPosIni
        self.uiPose.legacyPoseEstimationButton.clicked.connect(lambda: self.estimatePose(smapshot_georeferencer=False))
        self.uiPose.poseEstimationButton.clicked.connect(lambda: self.estimatePose(smapshot_georeferencer=True))
        self.uiPose.reportButton.clicked.connect(self.showReportOnGCP)
        self.uiPose.importParamButton.clicked.connect(self.importPositionCamera)
        self.uiPose.cameraPositionButton.clicked.connect(self.savePositionCamera)
        self.uiPose.exifButton.clicked.connect(self.exifInfoDisp)
        self.uiPose.needRefresh.connect(self.refreshButton)
        self.buttonColor = "R"
        self.actionOnButton("C", self.buttonColor)
        
        #Set previous estimated value to text boxes
        indice = 0
        self.poseLineEdit = []
        for line in self.findChildren(QtWidgets.QLineEdit):
                value = self.paramPosIni[indice]
                if indice == 0:
                    value *= -1
                #if indice > 2 and indice < 6:
                #    value *= old_div(180,pi)
                if indice == 7:
                    value -= old_div(self.sizePicture[0],2)
                if indice == 8:
                    value -= old_div(self.sizePicture[1],2)
                text = str(round(value,3))
                line.setText(text)
                self.poseLineEdit.append(text)
                indice +=1
        
        indice = 0
        for radio in self.findChildren(QtWidgets.QRadioButton):
            radio.setChecked(self.whoIsChecked[indice])
            indice +=1
                
    def center(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def reportOnGCPs(self):
        self.report = ReportDialog(self.gcp_table_model, self.parameter_bool, self.result, self.pathToData, self.xyzUnProjected, self.error_report)
        
    def showReportOnGCP(self):
        if hasattr(self, 'report'):
            self.report.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            self.report.setWindowModality(Qt.ApplicationModal)
            self.report.show()
            result = self.report.exec_()
        else:
            QMessageBox.warning(self, "Estimation - Error",
                    "There is currently no estimation of position done with GCPs")

    def exifInfoDisp(self):
        try:
            self.exifInfo = ExifInfo(self.picture_name, self.crs)
            if self.exifInfo.transformCoord : 
                self.exifInfo.ui_exif_info.importXYButton.setEnabled(True)
                self.exifInfo.ui_exif_info.importXYButton.pressed.connect(self.importXYButtonPress)
            if self.buttonColor == "G" :
                self.exifInfo.ui_exif_info.saveXYButton.setEnabled(True)
                self.exifInfo.ui_exif_info.saveXYButton.pressed.connect(self.saveXYButtonPress)
            self.exifInfo.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            self.exifInfo.fixFocalSignal.connect(self.fixFocal)
            self.exifInfo.setWindowModality(Qt.ApplicationModal)
            self.exifInfo.show()
        except:
            QMessageBox.warning(self, "Read - Error","Failed to load EXIF information.\nPicture may not have meta-data" )
        
    def importXYButtonPress(self):
        for item in self.exifInfo.transformCoord : 
            if item[1] == "pos" :
                self.uiPose.XPosLine.setText(str(round(item[0][0],3)))
                self.uiPose.XPosIni.setChecked(True)
                self.uiPose.YPosLine.setText(str(round(item[0][1],3)))
                self.uiPose.YPosIni.setChecked(True)
            elif item[1] == "alt" :
                self.uiPose.ZPosLine.setText(str(round(item[0],3)))
                self.uiPose.ZPosIni.setChecked(True)

            elif item [1] == "heading" :
                self.uiPose.headingLine.setText(str(round(item[0],3)))
                self.uiPose.headingIni.setChecked(True)
        
        self.refreshButton()
    
    def saveXYButtonPress(self):

        img = Image.open(self.picture_name)
        exifInfo = piexif.load(img.info['exif'])

        crsS = "EPSG:" + str(self.crs.postgisSrid())
        crsSource = QgsCoordinateReferenceSystem(crsS)
        crsTarget = QgsCoordinateReferenceSystem("EPSG:4326")
        xform = QgsCoordinateTransform(crsSource, crsTarget, QgsProject.instance())
        LocalPos = xform.transform(QgsPointXY(-self.result[0],self.result[1]))
        intLong = int(LocalPos[0])
        if intLong > 0 :
            refLong = 'E'
        else :
            refLong = 'W'
        
        intLat = int(LocalPos[1])
        if intLat > 0 :
            refLat = 'N'
        else :
            refLat = 'S'
        
        valMult = 10000

        longdec = abs(LocalPos[0] - intLong) * 60 * valMult
        latdec = abs(LocalPos[1] - intLat) * 60 * valMult

        longitude = ( (abs(intLong), 1), ( int(longdec), valMult ), (0, 1) ) 
        latitude = ( (intLat, 1), ( int(latdec), valMult ), (0, 1) ) 
        altitude = (int(self.result[2]), 1)
        
        intHeading = int(self.result[4]*1000) 
        heading = (intHeading, 1000)
        refHeading = 'T'
        
        exifInfo['GPS'][piexif.GPSIFD.GPSLatitudeRef] = refLat
        exifInfo['GPS'][piexif.GPSIFD.GPSLatitude] = latitude
        exifInfo['GPS'][piexif.GPSIFD.GPSLongitudeRef] = refLong
        exifInfo['GPS'][piexif.GPSIFD.GPSLongitude] = longitude
        exifInfo['GPS'][piexif.GPSIFD.GPSAltitude] = altitude
        exifInfo['GPS'][piexif.GPSIFD.GPSImgDirection] = heading
        exifInfo['GPS'][piexif.GPSIFD.GPSImgDirectionRef] = refHeading
        exif_bytes = piexif.dump(exifInfo)
        img.save(self.picture_name, "jpeg", exif=exif_bytes)

        img.close()
        self.exifInfo.setTextBrowser()

    def fixFocal(self, focalPixel):
        self.uiPose.focalLine.setText(str(focalPixel))
        self.uiPose.focalIni.setChecked(True)
        #self.uiPose.focalIni.toggle()

    def estimatePose(self, smapshot_georeferencer=False):
        
        # Function called when the user press "Estimate Pose"
        """
        Read the model (table) and get all the values from the 5th first columns
    
        In the least square (which is opposed to the total least square), a relation
        is found between ordinates (x) and observationservations (y). The least square 
        algorithms gives an error probability on observationservations but consider
        true ordinates.
        Column 1 and 2 are seen has observationservations.
        Columns 3,4,5 form the ordinate on which the observationservation in done.
        """
        gcp_table_model: GCPTableModel = self.gcp_table_model
        total_gcps: int = gcp_table_model.rowCount()
        total_enabled_gcps = 0
        for row_idx in range(0, total_gcps):
            if gcp_table_model.data(gcp_table_model.index(row_idx,5)) == 1:
                total_enabled_gcps += 1

        gcp_xyz_array = zeros((total_enabled_gcps, 3))
        gcp_uv_array = zeros((total_enabled_gcps,2))
        gcp_idx = 0
        for row_idx in range(0, total_gcps):
            if gcp_table_model.checkValid(row_idx)==0:
                continue
            if gcp_table_model.data(gcp_table_model.index(row_idx,5)) == 0:
                continue
            index = gcp_table_model.index(row_idx, 0)
            gcp_uv_array[gcp_idx,0] = gcp_table_model.data(index)
            index = gcp_table_model.index(row_idx,1)
            gcp_uv_array[gcp_idx,1] = gcp_table_model.data(index)
            index = gcp_table_model.index(row_idx,2)
            gcp_xyz_array[gcp_idx,0] = gcp_table_model.data(index)
            index = gcp_table_model.index(row_idx,3)
            gcp_xyz_array[gcp_idx,1] = gcp_table_model.data(index)
            index = gcp_table_model.index(row_idx,4)
            gcp_xyz_array[gcp_idx,2] = gcp_table_model.data(index)
            gcp_idx +=1

        # self.gcp_xyz_used are GCP which have 6th column enabled 
        self.gcp_xyz_used = array([-1*gcp_xyz_array[:,0],gcp_xyz_array[:,1],gcp_xyz_array[:,2]]).T
        
        table = self.findChildren(QtWidgets.QLineEdit)
        parameter_bool = zeros((9))
        parameter_list = []
        parameter_idx = 0
        """
        Read the list of Parameter of camera
        0. X Position 
        1. Y Position
        2. Z Position
        3. Tilt
        4. heading
        5. swing
        6. focal
        Parameters 7 and 8 are the central point. It is fixed to the center of image for convenience with openGL
        parameter_bool is an array with 0 if the parameter is fixed, or 1 if the parameter is free
        """
        
        #For each radio button (Free, Fixed, Apriori) for each parameters
        for radioButton in self.findChildren(QtWidgets.QRadioButton):

            if (radioButton.text() == "Free"):
                if radioButton.isChecked():

                    parameter_bool[parameter_idx] = int(1) # The parameters is free
                    parameter_list.append(0)
                     
            elif (radioButton.text() == "Fixed"):
                if radioButton.isChecked():

                    parameter_bool[parameter_idx] = int(0) #The parameters is fixed

                    value = float(table[parameter_idx].text())
                    if parameter_idx == 0:
                        value = -value
                    if parameter_idx > 2 and parameter_idx < 6:
                        value *=  old_div(pi,180)  #angle are displayed in degree
                    if parameter_idx == 7:
                        value += self.sizePicture[0]/2.0 #central point is displayed in reference to the center of image
                    if parameter_idx == 8:
                        value += self.sizePicture[1]/2.0  #central point is displayed in reference to the center of image
                    parameter_list.append(value)
                    
            elif (radioButton.text() == "Apriori"): #Apriori
                
                if radioButton.isChecked():

                    parameter_bool[parameter_idx] = int(2) #The parameters is aprior

                    value = float(table[parameter_idx].text())
                    if parameter_idx == 0:
                        value = -value
                    if parameter_idx > 2 and parameter_idx < 6:
                        value *=  old_div(pi,180)  #angle are displayed in degree
                    if parameter_idx == 7:
                        value += self.sizePicture[0]/2.0 #central point is displayed in reference to the center of image
                    if parameter_idx == 8:
                        value += self.sizePicture[1]/2.0  #central point is displayed in reference to the center of image
                    parameter_list.append(value)
                
                #Incrementation of the indice of the parameters (each 3 button)
                parameter_idx += 1

        # We fix anyway the central point. Future work can take it into account. It is therefore used here as parameter.
        #U0
        parameter_bool[7] = 0
        parameter_list.append(old_div(self.sizePicture[0],2))
        #V0
        parameter_bool[8] = 0
        parameter_list.append(old_div(self.sizePicture[1],2))

        if smapshot_georeferencer:
            # Convert gcp location from the current Crs to EPSG:4326
            source_crs = QgsProject.instance().crs()
            target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            transform = QgsCoordinateTransform(source_crs, target_crs, QgsProject.instance())
            reverse_transform = QgsCoordinateTransform(target_crs, source_crs, QgsProject.instance())
            gcp_smapshot_list = []
            for gcp_idx in range(total_enabled_gcps):
                x, y, z = gcp_xyz_array[gcp_idx]
                point_xy = QgsPointXY(x, y)
                point_lnglat = transform.transform(point_xy)
                gcp_smapshot_list.append({
                    "longitude": point_lnglat.x(),
                    "latitude": point_lnglat.y(),
                    "altitude": z,
                    "x": gcp_uv_array[gcp_idx, 0],
                    "y": gcp_uv_array[gcp_idx, 1]
                })

            # Initial data (free)
            lng0 = 0
            lat0 = 0
            alt0 = 0
            azimuthDeg = 0
            tiltDeg = 0
            rollDeg = 0
            focal = georef_utils.computeDiagonal(self.sizePicture[0], self.sizePicture[1])

            (
                lngComp,
                latComp,
                altComp,
                azimuthComp,
                tiltComp,
                rollComp,
                focalComp,
                pComp,
                gcp_comp_list,
                imageCoordinates,
                method,
            ) = georef_utils.georeferencer(
                lng0,
                lat0,
                alt0,
                azimuthDeg,
                tiltDeg,
                rollDeg,
                focal,
                self.sizePicture[0],
                self.sizePicture[1],
                gcp_smapshot_list,
                plotBool=False,
            )

            point_lnglat = QgsPointXY(lngComp, latComp)
            point_xy = reverse_transform.transform(point_lnglat)

            # Convert the computed pose location from EPSG:4326 to the current Crs
            resultLS = [
                point_xy.x(),
                point_xy.y(),
                altComp,
                azimuthComp,
                tiltComp,
                rollComp,
                focal
            ]
            lookAt = [0, 0, 0]
            upWorld = [0, 0, 0]
            predictions = [[gcp_comp["xReproj"], gcp_comp["yReproj"]] for gcp_comp in gcp_comp_list]
            errors = [gcp_comp["dxy"] for gcp_comp in gcp_comp_list]
            error_report = {"mean": mean(errors), "std": std(errors), "min": min(errors), "max": max(errors)}

        else:

            if list(parameter_bool[:7]) == [0]*7 : 

                tilt = parameter_list[3]
                heading = parameter_list[4]
                swing = parameter_list[5]

                R = zeros((3,3))
                R[0,0] = -cos(heading)*cos(swing)-sin(heading)*cos(tilt)*sin(swing)
                R[0,1] =  sin(heading)*cos(swing)-cos(heading)*cos(tilt)*sin(swing) 
                R[0,2] = -sin(tilt)*sin(swing)
                R[1,0] =  cos(heading)*sin(swing)-sin(heading)*cos(tilt)*cos(swing)
                R[1,1] = -sin(heading)*sin(swing)-cos(heading)*cos(tilt)*cos(swing) 
                R[1,2] = -sin(tilt)*cos(swing)
                R[2,0] = -sin(heading)*sin(tilt)
                R[2,1] = -cos(heading)*sin(tilt)
                R[2,2] =  cos(tilt)

                dirCam = array([0,0,-parameter_list[6]])
                upCam = array([0,-1,0])
                
                dirWorld = dot(linalg.inv(R),dirCam.T)
                lookat_temp = array(dirWorld)+array([parameter_list[0], parameter_list[1] , parameter_list[2]])
                upWorld_temp = dot(linalg.inv(R),upCam.T) 

                tilt = (parameter_list[3]*180)/pi
                heading = (parameter_list[4]*180)/pi 
                swing = (parameter_list[5]*180)/pi 
                
                self.pos = [parameter_list[0], parameter_list[2], parameter_list[1]]
                self.FOV = old_div((2*arctan(float(self.sizePicture[1]/2.0)/parameter_list[6]))*180,pi)
                self.roll = arcsin(-sin(tilt)*sin(swing))
                self.lookat = array([lookat_temp[0], lookat_temp[2], lookat_temp[1]])
                self.upWorld = array([upWorld_temp[0], upWorld_temp[2], upWorld_temp[1]])
                self.result = [parameter_list[0], parameter_list[1], parameter_list[2], tilt, heading, swing, parameter_list[6]]
                self.whoIsChecked = [False, True, False]*7 
                self.importUpdate.emit()
                return

            try:
                #Check if consistency of inputs
                if gcp_uv_array.shape[0] != gcp_xyz_array.shape[0]:
                    raise ValueError
                    
                #Check if there is at least 4 GCP
                elif (gcp_uv_array.shape[0] < 4):
                    raise IOError("There are only %d GCP and no apriori values. A solution can not be computed. You can either provide 4 GCP and apriori values (solved with least-square) or 6 GCP (solved with DLT)" % (gcp_uv_array.shape[0]))
                    
                #Check if there is at least 4 GCP
                elif (gcp_uv_array.shape[0] < 6) and any(parameter_bool[0:7]==1):
                    raise IOError("There are only %d GCP and no apriori values. A solution can not be computed. You can either provide apriori values (solved with least-square) or 6 GCP (solved with DLT)" % (gcp_uv_array.shape[0]))
                    

                #Check if there is at least 6 GCP
                #if (uv1.shape[0] < 6) and any(parameter_bool[0:7]==1):
                #    raise nCorrError2

            except IOError as x:

                QMessageBox.warning(self, "GCP error", str(x))
                self.done = False

            except ValueError:
                QMessageBox.warning(self, "GCP - Error",
                        'xyz (%d points) and uv (%d points) have different number of points.' %(gcp_xyz_array.shape[0], gcp_uv_array.shape[0]))
                self.done = False

            else:
                
                if (gcp_xyz_array.shape[0] >= 6):
                    
                    if any(parameter_bool[0:7]==1):
                        #There are free values a DLT is performed
                        print ('Position is fixed but orientation is unknown')
                        print ('The orientation is initialized with DLT')
                        
                        resultInitialization, L, v, upWorld = self.DLTMain(gcp_xyz_array,gcp_uv_array)
                    else:
                        #There is only fixed or apriori values LS is performed
                        print ('There is only fixed or apriori values LS is performed')
                        resultInitialization = parameter_list

                else:
                    print ('There are less than 6 GCP: every parameter must be fixed or apriori, LS is performed')
                    resultInitialization = parameter_list

                """
                The least square works well only if the initial guess is not too far from the optimal solution
                The DLT algorithm provides good estimates of parameters.
                However, it is not possible to fix some parameter with the DLT.
                For this last task, a least square has been constructed with variable number of parameter.
                
                After the initial DLT, we get an estimate for all parameters. 
                We take the fixed parameters from the dialog box and give the initial
                guess from the DLT to free parameters. 
                """
                resultLS, Lproj, lookAt, upWorld, predictions, error_report, errors = self.LS(gcp_xyz_array,gcp_uv_array,parameter_bool,parameter_list,resultInitialization)

        # Compute the result vector
        result = [0]*9
        # Length of resultLS is [9 - length of parameter_list]
        # We reconstruct the "result" vector which contains the output parameters
        k = 0
        for i in range(9):
            if (parameter_bool[i]==1) or (parameter_bool[i]==2):
                result[i] = resultLS[k]
                k +=1
            else:
                result[i]=parameter_list[i]
        result[0] *= -1

        # Set result in the dialog box
        gcp_idx = 0
        self.poseLineEdit = []
        for line in self.findChildren(QtWidgets.QLineEdit):
            value = result[gcp_idx]
            if gcp_idx == 0:
                value *= -1
            if not smapshot_georeferencer and gcp_idx > 2 and gcp_idx < 6:
                value *= old_div(180,pi)
            if gcp_idx == 7:
                value-=self.sizePicture[0]/2.0
            if gcp_idx == 8:
                value-=self.sizePicture[1]/2.0
            text = str(round(value,3))
            line.setText(text)
            self.poseLineEdit.append(text)
            gcp_idx +=1
        
        # Set the variable for next computation and for openGL pose
        self.parameter_bool = parameter_bool
        self.parameter_list = parameter_list
        self.done = True
        self.result = result
        # self.LProj = Lproj OPENGL SPECIFIC - NOT NEEDED
        self.lookat = lookAt
        self.upWorld = upWorld
        self.predictions = predictions
        self.error_report = error_report
        self.errors = errors
        self.pos = result[0:3]
        # The focal, here calculate in pixel, has to be translated in term of vertical field of view for openGL
        if result[6] != 0 :
            self.FOV = old_div((2*arctan(float(self.sizePicture[1]/2.0)/result[6]))*180,pi)
        else :
            self.FOV = 0 
        self.roll = arcsin(-sin(result[3])*sin(result[5]))
        
        gcp_idx = 0
        for radio in self.findChildren(QtWidgets.QRadioButton):
            self.whoIsChecked[gcp_idx] = radio.isChecked()
            gcp_idx +=1
        # Update projected and reprojected points for drawing
        self.update.emit()

        # Create the report on GCP
        self.reportOnGCPs()
        if self.report.inconsistent == False :
            self.actionOnButton("E", True)
            self.actionOnButton("C", "G")

    def refreshButton(self):
        if self.buttonColor == "G":
            self.actionOnButton("C", "Y")
        elif self.buttonColor == "Y" :
            radioVal = []
            lineVal = []
            for radio in self.findChildren(QtWidgets.QRadioButton):
                radioVal.append(radio.isChecked())
            for line in self.findChildren(QtWidgets.QLineEdit):
                lineVal.append(line.text())
            if radioVal == self.whoIsChecked and lineVal == self.poseLineEdit :
                self.actionOnButton("C", "G")

    
    def actionOnButton(self, action, arg=None):
        if action == "E" :
            self.uiPose.cameraPositionButton.setEnabled(arg)
            self.uiPose.reportButton.setEnabled(arg)
        
        elif action == "C" :
            self.buttonColor = arg
            if arg == "R": 
                self.uiPose.cameraPositionButton.setStyleSheet("background-color: rgb(255, 90, 90);")
                self.uiPose.reportButton.setStyleSheet("background-color: rgb(255, 90, 90);")

            elif arg == "Y" :
                self.uiPose.cameraPositionButton.setStyleSheet("background-color: rgb(255, 255, 90);")
                self.uiPose.reportButton.setStyleSheet("background-color: rgb(255, 255, 90);")

            elif arg == "G" :
                self.uiPose.cameraPositionButton.setStyleSheet("background-color: rgb(90, 255, 90);")
                self.uiPose.reportButton.setStyleSheet("background-color: rgb(90, 255, 90);")


    def LS(self,abscissa,observations,PARAM,x_fix,x_ini):
        # The initial parameters are the ones from DLT but where the radio button is set as free
        x = []
        for i in range(9):
            if (PARAM[i]==1) or (PARAM[i]==2):
                #Free or apriori values
                x.append(x_ini[i])
        if x :

            x = array(x)

            # 2D coordinates are understood as observations
            observations = array(observations)
            # 3D coordinates are understood as the abscissas
            abscissa = array(abscissa)
            npoints = size(observations[:,1])
            
            l_x = size(x)#9-size(nonzero(PARAM==0)[0])#int(sum(PARAM))#Number of free parameters
            sigmaobservationservation = 1
            Kl =  zeros(shape=(2*npoints,2*npoints))
            
            # A error of "sigmaobservationservation" pixels is a priori set
            for i in range (npoints):
                Kl[2*i-1,2*i-1]=sigmaobservationservation**2
                Kl[2*i,2*i]=sigmaobservationservation**2
             
            # The P matrix is a weight matrix, useless if equal to identity (but can be used in some special cases)    
            P=linalg.pinv(Kl);
            # A is the Jacobian matrix
            A = zeros(shape=(2*npoints,l_x))
            # H is the hessian matrix
            H = zeros(shape=(l_x,l_x))
            # b is a transition matrix
            b = zeros(shape=(l_x))
            # v contains the residual errors between observations and predictions
            v = zeros(shape=(2*npoints))
            # v_test contain the residual errors between observations and predictions after an update of H
            v_test = zeros(shape=(2*npoints))
            # x_test is the updated parameters after an update of H
            x_test = zeros(shape=(l_x))
            # dx is the update vector of x and x_test
            dx = array([0.]*l_x)
            
            it=-1;            
            maxit=1000;     
            # At least one iteration, dx > inc
            dx[0]=1
            # Lambda is the weightage parameter in Levenberg-marquart between the gradient and the gauss-newton parts.
            Lambda = 0.01
            # increment used for Jacobian and for convergence criterium
            inc = 0.001
            while (max(abs(dx))> inc) & (it<maxit):
                #new iteration, parameters updates are greater than the convergence criterium
                it=it+1;
                # For each observations, we compute the derivative with respect to each parameter
                # We form therefore the Jacobian matrix
                for i in range(npoints):
                    #ubul and vbul are the prediction with current parameters
                    ubul, vbul = self.dircal(x, abscissa[i,:], x_fix, PARAM)
                    # The difference between the observation and prediction is used for parameters update
                    v[2*i-1]=observations[i,0]-ubul
                    v[2*i]=observations[i,1]-vbul
                    for j in range(l_x):
                        x_temp = copy(x);
                        x_temp[j] = x[j]+inc
                        u2, v2 = self.dircal(x_temp,abscissa[i,:],x_fix,PARAM)
                        A[2*i-1,j]= old_div((u2-ubul),inc)
                        A[2*i,j]= old_div((v2-vbul),inc)
                # The sum of the square of residual (S0) must be as little as possible.             
                # That's why we speak of "least square"... tadadam !
                S0 = sum(v**2);
                H = dot(dot(matrix.transpose(A),P),A);
                b = dot(dot(matrix.transpose(A),P),v);
                try:
                    dx = dot(linalg.pinv(H+Lambda*diag(diag(H))),b);
                    x_test = x+dx;
                except:
                    # The matrix is not always reversal.
                    # In this case, we don't accept the update and go for another iteration 
                    S2 = S0
                else:
                    for i in range(npoints):
                        # We check that the update has brought some good stuff in the pocket
                        # In other words, we check that the sum of square of less than before (better least square!)
                        utest, vtest = self.dircal(x_test,abscissa[i,:],x_fix,PARAM);
                        v_test[2*i-1]=observations[i,0]-utest;
                        v_test[2*i]=observations[i,1]-vtest; 
                        S2 = sum(v_test**2);
                # Check if sum of square is less
                if S2<S0:
                    Lambda = old_div(Lambda,10)
                    x = x + dx
                else:
                    Lambda = Lambda*10
            
            # Covariance matrix of parameters
            self.Qxx = sqrt(diag(linalg.inv(dot(dot(matrix.transpose(A),P),A))))
            
        else :
            tab = [0.0]*7
            self.Qxx = array(tab)
        
        p = zeros(shape=(len(PARAM)))
        m = 0 
        for k in range(len(PARAM)):
            if (PARAM[k]==1) or (PARAM[k]==2):
                p[k] = x[m]
                m += 1
            else:
                p[k] = x_fix[k]
                
        L1p = self.CoeftoMatrixProjection(p)
        
        x0 = p[0];
        y0 = p[1];
        z0 = p[2];
        tilt = p[3];
        azimuth = p[4];
        swing = p[5];
        focal = p[6];
        u0 = p[7];
        v0 = p[8];
        
        R = zeros((3,3))
        R[0,0] = -cos(azimuth)*cos(swing)-sin(azimuth)*cos(tilt)*sin(swing)
        R[0,1] =  sin(azimuth)*cos(swing)-cos(azimuth)*cos(tilt)*sin(swing) 
        R[0,2] = -sin(tilt)*sin(swing)
        R[1,0] =  cos(azimuth)*sin(swing)-sin(azimuth)*cos(tilt)*cos(swing)
        R[1,1] = -sin(azimuth)*sin(swing)-cos(azimuth)*cos(tilt)*cos(swing) 
        R[1,2] = -sin(tilt)*cos(swing)
        R[2,0] = -sin(azimuth)*sin(tilt)
        R[2,1] = -cos(azimuth)*sin(tilt)
        R[2,2] =  cos(tilt)
        # Get "look at" vector for openGL pose
        ######################################
        
        #Generate vectors in camera system
        dirCam = array([0,0,-focal])
        upCam = array([0,-1,0])
        downCam = array([0,1,0])
        
        #Rotate in the world system
        dirWorld = dot(linalg.inv(R),dirCam.T)
        lookat = array(dirWorld)+array([x0,y0,z0])
        
        upWorld = dot(linalg.inv(R),upCam.T) 
        #not_awesome_vector = array([0,0,-focal])
        #almost_awesome_vector = dot(linalg.inv(R),not_awesome_vector.T)
        #awesome_vector = array(almost_awesome_vector)+array([x0,y0,z0])

        # predictions contains npoints predicted points from LS
        predictions = zeros(shape=(npoints, 2))
        for i in range(npoints):
            predictions[i, :] = self.dircal(x,abscissa[i,:],x_fix,PARAM)

        # Compute the error
        error_report = {}
        errors = linalg.norm(observations - predictions, axis=1)
        error_report['mean'] = mean(errors)
        error_report['std'] = std(errors)
        error_report['min'] = min(errors)
        error_report['max'] = max(errors)

        return x, L1p, lookat, upWorld, predictions, error_report, errors
    
    def CoeftoMatrixProjection(self,x):
        L1p = zeros((4,4))
        L1_line = zeros(12)
        x0 = x[0]
        y0 = x[1]
        z0 = x[2]
        tilt = x[3]
        azimuth = x[4]
        swing = x[5]
        focal = x[6]
        u0 = x[7]
        v0 = x[8]
        R = zeros((3,3))
        R[0,0] = -cos(azimuth)*cos(swing)-sin(azimuth)*cos(tilt)*sin(swing)
        R[0,1] =  sin(azimuth)*cos(swing)-cos(azimuth)*cos(tilt)*sin(swing) 
        R[0,2] = -sin(tilt)*sin(swing)
        R[1,0] =  cos(azimuth)*sin(swing)-sin(azimuth)*cos(tilt)*cos(swing)
        R[1,1] = -sin(azimuth)*sin(swing)-cos(azimuth)*cos(tilt)*cos(swing) 
        R[1,2] = -sin(tilt)*cos(swing)
        R[2,0] = -sin(azimuth)*sin(tilt)
        R[2,1] = -cos(azimuth)*sin(tilt)
        R[2,2] =  cos(tilt)
        D = -(x0*R[2,0]+y0*R[2,1]+z0*R[2,2])
        L1_line[0] = old_div((u0*R[2,0]-focal*R[0,0]),D)
        L1_line[1] = old_div((u0*R[2,1]-focal*R[0,1]),D)
        L1_line[2] = old_div((u0*R[2,2]-focal*R[0,2]),D)
        L1_line[3] = old_div(((focal*R[0,0]-u0*R[2,0])*x0+(focal*R[0,1]-u0*R[2,1])*y0+(focal*R[0,2]-u0*R[2,2])*z0),D)
        L1_line[4] = old_div((v0*R[2,0]-focal*R[1,0]),D)
        L1_line[5] = old_div((v0*R[2,1]-focal*R[1,1]),D)
        L1_line[6] = old_div((v0*R[2,2]-focal*R[1,2]),D)
        L1_line[7] = old_div(((focal*R[1,0]-v0*R[2,0])*x0+(focal*R[1,1]-v0*R[2,1])*y0+(focal*R[1,2]-v0*R[2,2])*z0),D)
        L1_line[8] = old_div(R[2,0],D)
        L1_line[9] = old_div(R[2,1],D)
        L1_line[10] = old_div(R[2,2],D)
        L1_line[11] = 1
        L1p =  L1_line.reshape(3,4)
        return L1p
    
    def DLTcalibration(self, xyz, uv):
        # written by Marcos Duarte - duartexyz@gmail.com
        """
        Methods for camera calibration and point reconstruction based on DLT.
    
        DLT is typically used in two steps: 
        1. Camera calibration. Function: L, err = DLTcalib(nd, xyz, uv). 
        2. Object (point) reconstruction. Function: xyz = DLTrecon(nd, nc, Ls, uvs)
    
        The camera calibration step consists in digitizing points with known coordinates 
         in the real space and find the camera parameters.
        At least 4 points are necessary for the calibration of a plane (2D DLT) and at 
         least 6 points for the calibration of a volume (3D DLT). For the 2D DLT, at least
         one view of the object (points) must be entered. For the 3D DLT, at least 2 
         different views of the object (points) must be entered.
        These coordinates (from the object and image(s)) are inputed to the DLTcalib 
         algorithm which estimates the camera parameters (8 for 2D DLT and 11 for 3D DLT).
        Usually it is used more points than the minimum necessary and the overdetermined 
         linear system is solved by a least squares minimization algorithm. Here this 
         problem is solved using singular value decomposition (SVD).
        With these camera parameters and with the camera(s) at the same position of the 
         calibration step, we now can reconstruct the real position of any point inside 
         the calibrated space (area for 2D DLT and volume for the 3D DLT) from the point 
         position(s) viewed by the same fixed camera(s).
        This code can perform 2D or 3D DLT with any number of views (cameras).
        For 3D DLT, at least two views (cameras) are necessary.
        """
        """
        Camera calibration by DLT using known object points and their image points.

        This code performs 2D or 3D DLT camera calibration with any number of views (cameras).
        For 3D DLT, at least two views (cameras) are necessary.
        Inputs:
         nd is the number of dimensions of the object space: 3 for 3D DLT and 2 for 2D DLT.
         xyz are the coordinates in the object 3D or 2D space of the calibration points.
         uv are the coordinates in the image 2D space of these calibration points.
         The coordinates (x,y,z and u,v) are given as columns and the different points as rows.
         For the 2D DLT (object planar space), only the first 2 columns (x and y) are used.
         There must be at least 6 calibration points for the 3D DLT and 4 for the 2D DLT.
        Outputs:
         L: array of the 8 or 11 parameters of the calibration matrix.
         err: error of the DLT (mean residual of the DLT transformation in units 
          of camera coordinates).
        """
        
        # Convert all variables to numpy array:
        xyz = asarray(xyz)
        uv = asarray(uv)
        # Number of points:
        npoints = xyz.shape[0]
        # Check the parameters:
            
        # Normalize the data to improve the DLT quality (DLT is dependent on the
        #  system of coordinates).
        # This is relevant when there is a considerable perspective distortion.
        # Normalization: mean position at origin and mean distance equals to 1 
        #  at each direction.
        Txyz, xyzn = self.Normalization(3,xyz)
        Tuv, uvn = self.Normalization(2, uv)
        # Formulating the problem as a set of homogeneous linear equations, M*p=0:
        A = []
        for i in range(npoints):
            x,y,z = xyzn[i,0], xyzn[i,1], xyzn[i,2]
            u,v = uvn[i,0], uvn[i,1]
            A.append( [x, y, z, 1, 0, 0, 0, 0, -u*x, -u*y, -u*z, -u] )
            A.append( [0, 0, 0, 0, x, y, z, 1, -v*x, -v*y, -v*z, -v] )

        # Convert A to array: 
        A = asarray(A) 
        # Find the 11 (or 8 for 2D DLT) parameters: 

        U, S, Vh = linalg.svd(A)
        # The parameters are in the last line of Vh and normalize them: 
        L = old_div(Vh[-1,:], Vh[-1,-1])
        # Camera projection matrix: 
        H = L.reshape(3,4)

        # Denormalization: 
        H = dot( dot( linalg.pinv(Tuv), H ), Txyz );
        H = old_div(H, H[-1,-1])
        L = H.flatten()
        # Mean error of the DLT (mean residual of the DLT transformation in 
        #  units of camera coordinates): 
        uv2 = dot( H, concatenate( (xyz.T, ones((1,xyz.shape[0]))) ) ) 
        uv2 = old_div(uv2,uv2[2,:]) 
        # Mean distance: 
        err = sqrt( mean(sum( (uv2[0:2,:].T - uv)**2,1 )) ) 
        return L, err

    def Normalization(self, nd,x):
        # written by Marcos Duarte - duartexyz@gmail.com
        """Normalization of coordinates (centroid to the origin and mean distance of sqrt(2 or 3)).
        Inputs:
         nd: number of dimensions (2 for 2D; 3 for 3D)
         x: the data to be normalized (directions at different columns and points at rows)
        Outputs:
         Tr: the transformation matrix (translation plus scaling)
         x: the transformed data
        """
        x = asarray(x)
        m = mean(x,0)
        if nd==2:
            Tr = array([[std(x[:,0]), 0, m[0]], [0, std(x[:,1]), m[1]], [0, 0, 1]])
        else:
            Tr = array([[std(x[:,0]), 0, 0, m[0]], [0, std(x[:,1]), 0, m[1]], [0, 0, std(x[:,2]), m[2]], [0, 0, 0, 1]])
            
        Tr = linalg.inv(Tr)

        x = dot( Tr, concatenate( (x.T, ones((1,x.shape[0]))) ) )
        x = x[0:nd,:].T
        return Tr, x


    def DLTMain(self,xyz,uv1):
        L1, err1 = self.DLTcalibration(xyz, uv1)
        L1p = array([[L1[0],L1[1],L1[2], L1[3]],[L1[4], L1[5], L1[6], L1[7]],[L1[8], L1[9], L1[10], L1[11]]])

        #Reconstruction of parameters
        D2=old_div(1,(L1[8]**2+L1[9]**2+L1[10]**2));
        D = sqrt(D2);
        u0 = D2*(L1[0]*L1[8]+L1[1]*L1[9]+L1[2]*L1[10]);
        v0 = D2*(L1[4]*L1[8]+L1[5]*L1[9]+L1[6]*L1[10]);
        x0y0z0 = dot(linalg.pinv(L1p[0:3,0:3]),[[-L1[3]],[-L1[7]],[-1]]);
        du2 = D2*((u0*L1[8]-L1[0])**2+(u0*L1[9]-L1[1])**2+(u0*L1[10]-L1[2])**2);
        dv2 = D2*((v0*L1[8]-L1[4])**2+(v0*L1[9]-L1[5])**2+(v0*L1[10]-L1[6])**2);
        du = sqrt(du2);
        dv = sqrt(dv2);
        focal = old_div((du+dv),2)

        R_mat = array([[old_div((u0*L1[8]-L1[0]),du),old_div((u0*L1[9]-L1[1]),du),old_div((u0*L1[10]-L1[2]),du)],\
                [old_div((v0*L1[8]-L1[4]),dv),old_div((v0*L1[9]-L1[5]),dv),old_div((v0*L1[10]-L1[6]),dv)],\
                [L1[8],L1[9],L1[10]]]);

        if linalg.det(R_mat) < 0:
            R_mat = -R_mat;
        R = D * array(R_mat);
        U,s,V = linalg.svd(R,full_matrices=True,compute_uv=True)
        R = dot(U,V)


        tilt = arccos(R[2,2])
        swing = arctan2(-R[0,2],-R[1,2])
        azimuth = arctan2(-R[2,0],-R[2,1])
        not_awesome_vector = array([0,0,-1])
        
        #Generate vectors in camera system
        dirCam = array([0,0,-1])
        upCam = array([0,-1,0])
        downCam = array([0,1,0])
        
        #Rotate in the world system
        dirWorld = dot(linalg.inv(R),dirCam.T)
        upWorld = dot(linalg.inv(R),upCam.T) 
        
        #almost_awesome_vector = dot(linalg.inv(R),not_awesome_vector)
        lookat = array(dirWorld)+array([x0y0z0[0,0],x0y0z0[1,0],x0y0z0[2,0]])
        
        return [x0y0z0[0,0],x0y0z0[1,0],x0y0z0[2,0],tilt,azimuth,swing,focal,u0,v0], L1p, lookat, upWorld#awesome_vector
    
    def rq(self, A): 
         Q,R = linalg.qr(flipud(A).T)
         R = flipud(R.T)
         Q = Q.T 
         return R[:,::-1],Q[::-1,:]
    
    
    
    def dircal(self,x_unkown,abscissa,x_fix,PARAM):
        p = zeros(shape=(len(PARAM)))
        m = 0
        #n = 0
        for k in range(len(PARAM)):
            if (PARAM[k]==1) or (PARAM[k]==2): #Apriori or free
                p[k] = x_unkown[m]
                m = m+1
            else:
                p[k] = x_fix[k]###############
                #n = n+1

        x1 = abscissa[0];
        y1 = abscissa[1];
        z1 = abscissa[2];
        x0 = p[0];
        y0 = p[1];
        z0 = p[2];
        tilt = p[3];
        azimuth = p[4];
        swing = p[5];
        focal = p[6];
        u0 = p[7];
        v0 = p[8];
        R = zeros((3,3))
        R[0,0] = -cos(azimuth)*cos(swing)-sin(azimuth)*cos(tilt)*sin(swing)
        R[0,1] =  sin(azimuth)*cos(swing)-cos(azimuth)*cos(tilt)*sin(swing) 
        R[0,2] = -sin(tilt)*sin(swing)
        R[1,0] =  cos(azimuth)*sin(swing)-sin(azimuth)*cos(tilt)*cos(swing)
        R[1,1] = -sin(azimuth)*sin(swing)-cos(azimuth)*cos(tilt)*cos(swing) 
        R[1,2] = -sin(tilt)*cos(swing)
        R[2,0] = -sin(azimuth)*sin(tilt)
        R[2,1] = -cos(azimuth)*sin(tilt)
        R[2,2] =  cos(tilt)
        
        ures = old_div(-focal*(R[0,0]*(x1-x0)+R[0,1]*(y1-y0)+R[0,2]*(z1-z0)),\
            (R[2,0]*(x1-x0)+R[2,1]*(y1-y0)+R[2,2]*(z1-z0)))+u0;
        vres = old_div(-focal*(R[1,0]*(x1-x0)+R[1,1]*(y1-y0)+R[1,2]*(z1-z0)),\
            (R[2,0]*(x1-x0)+R[2,1]*(y1-y0)+R[2,2]*(z1-z0)))+v0;

        return ures,vres

    def importPositionCamera(self):
        
        fieldName = ["X", "Y", "Z", "tilt", "heading", "swing", "focal"]
        fieldValue = []
        allField = True
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "Load your shapefile ", self.pathToData , "Shapefile (*.shp)")[0]
        if fname :
            vLayer = QgsVectorLayer(fname, "", "ogr")
            for feat in vLayer.getFeatures() :
                for item in fieldName :
                    try :
                        value = feat.attribute(item)
                        fieldValue.append(value)
                    except :
                        fieldValue.append(0)
                        allField = False
    
            indice = 0
            whoToCheck = []
            for line in self.findChildren(QtWidgets.QLineEdit):
                value = fieldValue[indice]
                text = str(round(value,3))
                line.setText(text)
                if value == 0 : 
                    whoToCheck.extend([True,False,False])
                else :  
                    whoToCheck.extend([False,True,False])
                indice +=1
        
            indice = 0
            for radio in self.findChildren(QtWidgets.QRadioButton):
                radio.setChecked(whoToCheck[indice])
                indice +=1
            
            if allField :

                tilt = (fieldValue[3]*pi)/180 
                heading = (fieldValue[4]*pi)/180 
                swing = (fieldValue[5]*pi)/180 

                R = zeros((3,3))
                R[0,0] = -cos(heading)*cos(swing)-sin(heading)*cos(tilt)*sin(swing)
                R[0,1] =  sin(heading)*cos(swing)-cos(heading)*cos(tilt)*sin(swing) 
                R[0,2] = -sin(tilt)*sin(swing)
                R[1,0] =  cos(heading)*sin(swing)-sin(heading)*cos(tilt)*cos(swing)
                R[1,1] = -sin(heading)*sin(swing)-cos(heading)*cos(tilt)*cos(swing) 
                R[1,2] = -sin(tilt)*cos(swing)
                R[2,0] = -sin(heading)*sin(tilt)
                R[2,1] = -cos(heading)*sin(tilt)
                R[2,2] =  cos(tilt)

                dirCam = array([0,0,-fieldValue[6]])
                upCam = array([0,-1,0])
                
                dirWorld = dot(linalg.inv(R),dirCam.T)
                lookat_temp = array(dirWorld)+array([-fieldValue[0], fieldValue[1] , fieldValue[2]])
                upWorld_temp = dot(linalg.inv(R),upCam.T) 
                
                self.pos = [-fieldValue[0], fieldValue[2], fieldValue[1]]
                self.FOV = old_div((2*arctan(float(self.sizePicture[1]/2.0)/fieldValue[6]))*180,pi)
                self.roll = arcsin(-sin(tilt)*sin(swing))
                self.lookat = array([lookat_temp[0], lookat_temp[2], lookat_temp[1]])
                self.upWorld = array([upWorld_temp[0], upWorld_temp[2], upWorld_temp[1]])
                self.result = [-fieldValue[0], fieldValue[1], fieldValue[2], fieldValue[3], fieldValue[4], fieldValue[5], fieldValue[6]]
                self.whoIsChecked = whoToCheck 
                self.importUpdate.emit()
            
            else :
                self.refreshButton()

    def savePositionCamera(self) :
        xPos = -self.result[0]
        yPos = self.result[1]
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(xPos, yPos)

        camPosName = '/' + (self.picture_name.split(".")[0]).split("/")[-1] + '_CameraPosition'
        path = self.pathToData + camPosName

        shapeSaveName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Camera Position" ,path, "Shapefile (*.shp)")
        
        filename = (shapeSaveName.split("/")[-1]).split(".")[0]
        layers = QgsProject.instance().mapLayers()
        for layer in layers:
            f = QFileInfo(layer)
            head, sep, tail = f.filePath().partition("CameraPosition")
            baseName = head + sep
            if filename == baseName :
                QgsProject.instance().removeMapLayer(f.filePath())
                canvas = self.iface.mapCanvas()
                canvas.refresh()

            
        if shapeSaveName:
            outShapefile = shapeSaveName
            outDriver = ogr.GetDriverByName("ESRI Shapefile")
            
            # Remove output shapefile if it already exists
            if os.path.exists(outShapefile):
                outDriver.DeleteDataSource(outShapefile)
            
            # Create the output shapefile
            outDataSource = outDriver.CreateDataSource(outShapefile)
            if outDataSource is None :
                QMessageBox.warning(self, "Camera Position is an active layer", "You tried to delete a camera position present in the project layer. \n The camera postion layer was remove. Please try again")
                return 0
            
            #Create projection
            camPosSRS = osr.SpatialReference()
            epsg = int(self.crs.postgisSrid())
            camPosSRS.ImportFromEPSG(epsg)#2056)
            
            outLayer = outDataSource.CreateLayer(filename, camPosSRS, geom_type = ogr.wkbPoint)
            
            # Add an ID field
            XField = ogr.FieldDefn("X", ogr.OFTReal)
            outLayer.CreateField(XField)
            YField = ogr.FieldDefn("Y", ogr.OFTReal)
            outLayer.CreateField(YField)
            ZField = ogr.FieldDefn("Z", ogr.OFTReal)
            outLayer.CreateField(ZField)
            tiltField = ogr.FieldDefn("tilt", ogr.OFTReal)
            outLayer.CreateField(tiltField)
            headingField = ogr.FieldDefn("heading", ogr.OFTReal)
            outLayer.CreateField(headingField)
            swingField = ogr.FieldDefn("swing", ogr.OFTReal)
            outLayer.CreateField(swingField)
            focalField = ogr.FieldDefn("focal", ogr.OFTReal)
            outLayer.CreateField(focalField)
            nameField = ogr.FieldDefn("picture", ogr.OFTString)
            outLayer.CreateField(nameField)
            
            # Create the feature and set values
            featureDefn = outLayer.GetLayerDefn()
            feature = ogr.Feature(featureDefn)
            feature.SetGeometry(point)
            feature.SetField("picture", (self.picture_name.split(".")[0]).split("/")[-1])
            feature.SetField("X",-self.result[0])
            feature.SetField("Y",self.result[1])
            feature.SetField("Z",self.result[2])
            feature.SetField("tilt",self.result[3])
            feature.SetField("heading",self.result[4])
            feature.SetField("swing",self.result[5])
            feature.SetField("focal",self.result[6])
            outLayer.CreateFeature(feature)

            # Close DataSource
            outDataSource.Destroy()
            ret = QMessageBox.question(self, "Load Camera Position", "Do you want to load the camera position on the canvas?", QMessageBox.Yes| QMessageBox.No)
            if ret == QMessageBox.Yes : 
                self.iface.addVectorLayer(outShapefile, filename, "ogr")
