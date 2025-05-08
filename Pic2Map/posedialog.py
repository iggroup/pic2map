
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
"""
from __future__ import division
from __future__ import print_function

from builtins import str
from builtins import range
from past.utils import old_div
from PyQt6 import QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from .ui.ui_pose import Ui_PoseDialog
from PIL import Image
import piexif
from numpy import zeros, array, sin, cos, dot, linalg, pi, mean, std, min, max, std, arcsin, arctan, abs
from .reportDialog import ReportDialog
from .exifInfo import ExifInfo
from osgeo import ogr, osr
from qgis.core import *
from qgis.gui import *
import os
from .GCPs import GCPTableModel
from .smapshotgeoreferencer import georeferencerUtils as georef_utils

class PoseDialog(QtWidgets.QDialog):
    update = pyqtSignal()
    needRefresh = pyqtSignal()
    importUpdate = pyqtSignal()
    def __init__(self, gcp_table_model: GCPTableModel, paramPosIni, sizePicture, whoIsChecked,pathToData,picture_name, iface,crs):
        #QtGui.QDialog.__init__(self)
        QtWidgets.QDialog.__init__(self)
        self.uiPoseDialog = Ui_PoseDialog()
        self.uiPoseDialog.setupUi(self)
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
        self.uiPoseDialog.poseEstimationButton.clicked.connect(self.estimatePose)
        self.uiPoseDialog.reportButton.clicked.connect(self.showReportOnGCP)
        self.uiPoseDialog.importParamButton.clicked.connect(self.importPositionCamera)
        self.uiPoseDialog.cameraPositionButton.clicked.connect(self.savePositionCamera)
        self.uiPoseDialog.exifButton.clicked.connect(self.exifInfoDisp)
        self.uiPoseDialog.needRefresh.connect(self.refreshButton)
        self.buttonColor = "R"
        self.actionOnButton("C", self.buttonColor)
        
        #Set previous estimated value to text boxes
        indice = 0
        self.poseLineEdit = []
        for line in self.findChildren(QtWidgets.QLineEdit):
                value = self.paramPosIni[indice]
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
        self.report = ReportDialog(self.gcp_table_model, self.parameterBool, self.result, self.pathToData, self.xyzUnProjected, self.errorReport)
        
    def showReportOnGCP(self):
        if hasattr(self, 'report'):
            self.report.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            self.report.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.report.show()
            result = self.report.exec()
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
            self.exifInfo.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.exifInfo.show()
        except:
            QMessageBox.warning(self, "Read - Error","Failed to load EXIF information.\nPicture may not have meta-data" )
        
    def importXYButtonPress(self):
        for item in self.exifInfo.transformCoord : 
            if item[1] == "pos" :
                self.uiPoseDialog.XPosLine.setText(str(round(item[0][0],3)))
                self.uiPoseDialog.YPosLine.setText(str(round(item[0][1],3)))
                self.uiPoseDialog.XYZPosIni.setChecked(True)
            elif item[1] == "alt" :
                self.uiPoseDialog.ZPosLine.setText(str(round(item[0],3)))
                self.uiPoseDialog.XYZPosIni.setChecked(True)

            elif item [1] == "heading" :
                self.uiPoseDialog.headingLine.setText(str(round(item[0],3)))
                self.uiPoseDialog.headingIni.setChecked(True)
        
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
        self.uiPoseDialog.focalLine.setText(str(focalPixel))
        self.uiPoseDialog.focalIni.setChecked(True)
        #self.uiPose.focalIni.toggle()

    def estimatePose(self):

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
        gcpTableModel: GCPTableModel = self.gcp_table_model
        totalGcps: int = gcpTableModel.rowCount()
        totalEnabledGcps = 0
        for rowIdx in range(0, totalGcps):
            if gcpTableModel.data(gcpTableModel.index(rowIdx,5)) == 1:
                totalEnabledGcps += 1

        gcpXYZArray = zeros((totalEnabledGcps, 3))
        gcpUVArray = zeros((totalEnabledGcps,2))
        gcpIdx = 0
        for rowIdx in range(0, totalGcps):
            if gcpTableModel.checkValid(rowIdx)==0:
                continue
            if gcpTableModel.data(gcpTableModel.index(rowIdx,5)) == 0:
                continue
            index = gcpTableModel.index(rowIdx, 0)
            gcpUVArray[gcpIdx,0] = gcpTableModel.data(index)
            index = gcpTableModel.index(rowIdx,1)
            gcpUVArray[gcpIdx,1] = gcpTableModel.data(index)
            index = gcpTableModel.index(rowIdx,2)
            gcpXYZArray[gcpIdx,0] = gcpTableModel.data(index)
            index = gcpTableModel.index(rowIdx,3)
            gcpXYZArray[gcpIdx,1] = gcpTableModel.data(index)
            index = gcpTableModel.index(rowIdx,4)
            gcpXYZArray[gcpIdx,2] = gcpTableModel.data(index)
            gcpIdx +=1

        # self.gcp_xyz_used are GCP which have 6th column enabled 
        self.gcpXYZUsed = array([-1*gcpXYZArray[:,0],gcpXYZArray[:,1],gcpXYZArray[:,2]]).T
        
        lineEdits = self.findChildren(QtWidgets.QLineEdit)
        parameterTypeList = []
        parameterValueList = []
        parameterIdx = 0
        """
        Read the list of Parameter of camera
        0. X Position 
        1. Y Position
        2. Z Position
        3. tilt
        4. heading
        5. swing
        6. focal
        Parameters 7 and 8 are the central point. It is fixed to the center of image for convenience with openGL
        parameter_bool is an array with 0 if the parameter is fixed, or 1 if the parameter is free
        """
        #For each radio button (Free, Fixed, Apriori) for each parameters
        for radioButton in self.findChildren(QtWidgets.QRadioButton):
            if radioButton.isChecked():
                isXYZPose = parameterIdx == 0
                parametersToProcess = 3 if isXYZPose else 1

                for i in range(parametersToProcess):
                    if (radioButton.text() == "Free"):
                        parameterTypeList.append(0) # The parameters is free
                        parameterValueList.append(0)
                    else:
                            if (radioButton.text() == "Apriori"): #Apriori
                                parameterTypeList.append(1) #The parameters is aprior
                            elif (radioButton.text() == "Fixed"): #Fixed
                                parameterTypeList.append(2) #The parameters is fixed
                            value = float(lineEdits[parameterIdx].text())
                            # if parameterIdx == 0:
                            #     value = -value
                            if parameterIdx > 2 and parameterIdx < 6:
                                value *=  old_div(pi,180) #angle are displayed in degree
                            if parameterIdx == 7:
                                value += self.sizePicture[0]/2.0 #central point is displayed in reference to the center of image
                            if parameterIdx == 8:
                                value += self.sizePicture[1]/2.0  #central point is displayed in reference to the center of image
                            parameterValueList.append(value)
                    parameterIdx += 1

        # We fix anyway the central point. Future work can take it into account. It is therefore used here as parameter.
        #U0
        parameterTypeList.append(0)
        parameterValueList.append(old_div(self.sizePicture[0],2))
        #V0
        parameterTypeList.append(0)
        parameterValueList.append(old_div(self.sizePicture[1],2))


        ##########################
        # SMAPSHOT GEOREFERENCER #
        ##########################

        # Convert gcp location from the current Crs to EPSG:4326
        sourceCrs = QgsProject.instance().crs()
        targetCrs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(sourceCrs, targetCrs, QgsProject.instance())
        reverseTransform = QgsCoordinateTransform(targetCrs, sourceCrs, QgsProject.instance())
        gcpSmapshotList = []
        for gcpIdx in range(totalEnabledGcps):
            x, y, z = gcpXYZArray[gcpIdx]
            gcpPointXY = QgsPointXY(x, y)
            gcpPointLngLat = transform.transform(gcpPointXY)
            gcpSmapshotList.append({
                "longitude": gcpPointLngLat.x(),
                "latitude": gcpPointLngLat.y(),
                "altitude": z,
                "x": gcpUVArray[gcpIdx, 0],
                "y": gcpUVArray[gcpIdx, 1]
            })

        # Initial data (free)
        posePointXY0 = QgsPointXY(parameterValueList[0], parameterValueList[1])
        posePointLngLat0 = transform.transform(posePointXY0)
        lng0 = posePointLngLat0.x()
        lat0 = posePointLngLat0.y()
        alt0 = parameterValueList[2]
        tiltDeg = parameterValueList[3]
        azimuthDeg = parameterValueList[4]
        rollDeg = parameterValueList[5]
        focal = georef_utils.computeDiagonal(self.sizePicture[0], self.sizePicture[1])

        if parameterTypeList[0] == 2:
            (
                lngComp,
                latComp,
                altComp,
                azimuthComp,
                tiltComp,
                rollComp,
                focalComp,
                pComp,
                gcpCompList,
                imageCoordinates,
                method,
            ) = georef_utils.georeferencerLocked(
                lng0,
                lat0,
                alt0,
                azimuthDeg,
                tiltDeg,
                rollDeg,
                focal,
                self.sizePicture[0],
                self.sizePicture[1],
                gcpSmapshotList
            )
        else:
            (
                lngComp,
                latComp,
                altComp,
                azimuthComp,
                tiltComp,
                rollComp,
                focalComp,
                pComp,
                gcpCompList,
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
                gcpSmapshotList
            )

        gcpPointLngLat = QgsPointXY(lngComp, latComp)
        gcpPointXY = reverseTransform.transform(gcpPointLngLat)

        # Convert the computed pose location from EPSG:4326 to the current Crs
        resultLS = [
            gcpPointXY.x(),
            gcpPointXY.y(),
            altComp,
            azimuthComp,
            tiltComp,
            rollComp,
            focal
        ]
        lookAt = [0, 0, 0]
        upWorld = [0, 0, 0]
        predictions = [[gcpComp["xReproj"], gcpComp["yReproj"]] for gcpComp in gcpCompList]
        errors = [gcp_comp["dxy"] for gcp_comp in gcpCompList]
        errorReport = {"mean": mean(errors), "std": std(errors), "min": min(errors), "max": max(errors)}

        # Compute the result vector
        result = [*resultLS, *parameterValueList[-2:]]

        # Set result in the dialog box
        gcpIdx = 0
        self.poseLineEdit = []
        for line in self.findChildren(QtWidgets.QLineEdit):
            value = result[gcpIdx]
            if gcpIdx == 7:
                value-=self.sizePicture[0]/2.0
            if gcpIdx == 8:
                value-=self.sizePicture[1]/2.0
            text = str(round(value,3))
            line.setText(text)
            self.poseLineEdit.append(text)
            gcpIdx +=1
        
        # Set the variable for next computation and for openGL pose
        self.parameterBool = parameterTypeList
        self.parameterList = parameterValueList
        self.done = True
        self.result = result
        # self.LProj = Lproj OPENGL SPECIFIC - NOT NEEDED
        self.lookat = lookAt
        self.upWorld = upWorld
        self.predictions = predictions
        self.errorReport = errorReport
        self.errors = errors
        self.pos = result[0:3]
        # The focal, here calculate in pixel, has to be translated in term of vertical field of view for openGL
        if result[6] != 0 :
            self.FOV = old_div((2*arctan(float(self.sizePicture[1]/2.0)/result[6]))*180,pi)
        else :
            self.FOV = 0 
        self.roll = arcsin(-sin(result[3])*sin(result[5]))
        
        gcpIdx = 0
        for radio in self.findChildren(QtWidgets.QRadioButton):
            self.whoIsChecked[gcpIdx] = radio.isChecked()
            gcpIdx +=1
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
            self.uiPoseDialog.cameraPositionButton.setEnabled(arg)
            self.uiPoseDialog.reportButton.setEnabled(arg)
        
        elif action == "C" :
            self.buttonColor = arg
            if arg == "R": 
                self.uiPoseDialog.cameraPositionButton.setStyleSheet("background-color: rgb(255, 90, 90);")
                self.uiPoseDialog.reportButton.setStyleSheet("background-color: rgb(255, 90, 90);")

            elif arg == "Y" :
                self.uiPoseDialog.cameraPositionButton.setStyleSheet("background-color: rgb(255, 255, 90);")
                self.uiPoseDialog.reportButton.setStyleSheet("background-color: rgb(255, 255, 90);")

            elif arg == "G" :
                self.uiPoseDialog.cameraPositionButton.setStyleSheet("background-color: rgb(90, 255, 90);")
                self.uiPoseDialog.reportButton.setStyleSheet("background-color: rgb(90, 255, 90);")

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
            ret = QMessageBox.question(self, "Load Camera Position", "Do you want to load the camera position on the canvas?", QMessageBox.StandardButton.Yes| QMessageBox.StandardButton.No)
            if ret == QMessageBox.StandardButton.Yes : 
                self.iface.addVectorLayer(outShapefile, filename, "ogr")
