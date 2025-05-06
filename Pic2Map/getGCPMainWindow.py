# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Pic2Map
                                 A QGIS plugin
 Allow integration of oblique featuring inside a transversal module
                             -------------------
        begin                : 2014-02-19
        copyright            : (C) 2014 by Gillian Milani
        email                : gillian.milani@epfl.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import division

from builtins import str
from builtins import range
from builtins import object
from past.utils import old_div
from PyQt6 import QtGui, QtWidgets, QtCore
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from .ui_disprast import Ui_disprast
from .iconsdialog import icons_dialog
from .posedialog import Pose_dialog
from PIL import Image
from PIL import ImageQt
from PIL import ImageEnhance
from .GCPs import *
from numpy import arctan, arctan2, arcsin, sqrt, pi, cos, sin, array, zeros, dot, linalg, abs, asarray, tan
from .D3View import D3_view
# FIXME QtXml is no longer supported.
from PyQt6 import QtXml
import os, time
from math import ceil

try:
    QString = str
except NameError:
    # Python 3
    QString = str

class GetGCPMainWindow(QMainWindow):
    # signal used for reseting the GCP digitalization tool. Slot is located in the file "Pic2Map"
    resetToolSignal = pyqtSignal()
    clearMapTool2= pyqtSignal()
    #signal used for zooming on selected GCP. Slot is located in the file "Pic2Map"
    setCanvasExtentSignal = pyqtSignal(tuple)
    def __init__(self, iface, pointBuffer, picture_name, pathToData, isFrameBufferSupported, crs):
        QMainWindow.__init__(self)
        # pointBuffer mainly contain information relative to the 3D view
        self.pointBuffer = pointBuffer
        # The canvas is used here for management of GCP marker and rubberbands.
        # Others relations to the canvas are located in "Pic2Map"
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.sceneQgis = self.canvas.scene()
        self.pathToData = pathToData
        self.isFrameBufferSupported = isFrameBufferSupported
        self.crs = crs
        
        # create interface
        self.ui = Ui_disprast()
        self.ui.setupUi(self)
        #center the window in the screen
        #self.center()
        
        # zoomFactor is used by the zoom button and wheel events for zooming in and out
        self.zoomFactor = 1
        
        # reprojectedCross contain the east and north value of reprojectedCrossected points
        self.reprojectedCross = []
        self.poseCanvas = None
        self.canvasNumber = []
        self.canvasCross = []
        
        # uvTableAll contain all u and v reprojectedCrossection value from the model.
        # uvTableActivated contain u and v reprojectedCrossection value from the model for the GCP used for pose estimation
        # There are generated at each pose estimation
        self.uvTableAll = []
        self.uvTableActivated = []
        self.boolPose = False
        # goToMonoplot is a flag used by closeEvent
        self.goToMonoplot = False
        
        # picture_name is the landscape picture path
        self.picture_name = picture_name
        img = QImage(self.picture_name)
        self.sizePicture = [img.width(), img.height()]
        # iconSet contain setting used for displaying GCP in canvas and in the scene
        self.iconSet = icon_settings(self.sizePicture, self.pointBuffer.res)
        url = ":/plugins/Pic2Map/toolbar1.png"
        addGCPButton = QAction(QIcon(url), 'Add GCP to Table', self)
        # toolbarTable contains actions in relation with GCP digitalization
        # toolbarView contains actions in relation with the 3D openGL view
        # toolbarPose contains actions in relation with the pose estimation
        self.ui.toolbarTable = self.addToolBar('Table Actions')
        self.ui.toolbarView = self.addToolBar('View Actions')
        self.ui.toolbarPose = self.addToolBar('Pose Actions')
        self.ui.toolbarTable.addAction(addGCPButton)
        addGCPButton.triggered.connect(self.addGCP)
        
        removeGCPButton = QAction(QIcon(":/plugins/Pic2Map/toolbar2.png"), 'Remove selected GCP', self)
        self.ui.toolbarTable.addAction(removeGCPButton)
        removeGCPButton.triggered.connect(self.removeGCP)
        
        url = ":/plugins/Pic2Map/toolbar4.png"
        saveGCPButton = QAction(QIcon(url), 'Save GCP', self)
        self.ui.toolbarTable.addAction(saveGCPButton)
        saveGCPButton.triggered.connect(self.saveGCP)

        url = ":/plugins/Pic2Map/toolbar3.png"
        loadGCPButton = QAction(QIcon(url), 'Load GCP', self)
        self.ui.toolbarTable.addAction(loadGCPButton)
        loadGCPButton.triggered.connect(self.loadGCP)
        
        # url = ":/plugins/Pic2Map/toolbar13.png"
        # removereprojectedCrossectionsButton = QAction(QIcon(url), 'remove GCP reprojectedCrossections', self)
        # self.ui.toolbarTable.addAction(removereprojectedCrossectionsButton)
        # removereprojectedCrossectionsButton.triggered.connect(self.removereprojectedCrossections)
        
        url = ":/plugins/Pic2Map/toolbar5.png"
        self.ZoomInButton = QAction(QIcon(url), 'Zoom In', self)
        self.ui.toolbarView.addAction(self.ZoomInButton)
        self.ZoomInButton.setCheckable(True)
        self.ZoomInButton.triggered.connect(self.ZoomIn)
        
        url = ":/plugins/Pic2Map/toolbar6.png"
        self.ZoomOutButton = QAction(QIcon(url), 'Zoom Out', self)
        self.ui.toolbarView.addAction(self.ZoomOutButton)
        self.ZoomOutButton.setCheckable(True)
        self.ZoomOutButton.triggered.connect(self.ZoomOut)
        
        url = ":/plugins/Pic2Map/toolbar7.png"
        self.PanButton = QAction(QIcon(url), 'Pan', self)
        self.ui.toolbarView.addAction(self.PanButton)
        self.PanButton.setCheckable(True)
        self.PanButton.triggered.connect(self.Pan)
        
        # url = ":/plugins/Pic2Map/toolbar8.png"
        # IconsViewButton = QAction(QIcon(url), 'Symbols Settings', self)
        # self.ui.toolbarTable.addAction(IconsViewButton)
        # IconsViewButton.triggered.connect(self.iconsView)
        
        url = ":/plugins/Pic2Map/toolbar9.png"
        PoseButton = QAction(QIcon(url), 'Pose estimation', self)
        self.ui.toolbarPose.addAction(PoseButton)
        PoseButton.triggered.connect(self.PoseView)
        
        # url = ":/plugins/Pic2Map/toolbar10.png"
        # D3Button = QAction(QIcon(url), '3D-View', self)
        # self.ui.toolbarPose.addAction(D3Button)
        # D3Button.triggered.connect(self.call3DView)
        
        # url = ":/plugins/Pic2Map/toolbar11.png"
        # self.GoToMonoplotterButton = QAction(QIcon(url), 'Go to Monoplotter', self)
        # self.ui.toolbarPose.addAction(self.GoToMonoplotterButton)
        # self.GoToMonoplotterButton.setEnabled(False)
    
        
        url = ":/plugins/Pic2Map/toolbar15.png"
        self.saveAsKMLButton = QAction(QIcon(url), 'Save Pose as KML', self)
        self.ui.toolbarPose.addAction(self.saveAsKMLButton)
        self.saveAsKMLButton.triggered.connect(self.saveAsKML)
        
        url = ":/plugins/Pic2Map/toolbar16.png"
        self.loadAsKMLButton = QAction(QIcon(url), 'Load Pose as KML', self)
        self.ui.toolbarPose.addAction(self.loadAsKMLButton)
        self.loadAsKMLButton.triggered.connect(self.loadAsKML)
        
        url = ":/plugins/Pic2Map/toolbar12.png"
        ZoomOnCrossButton = QAction(QIcon(url), 'Zoom on selected GCP', self)
        self.ui.toolbarView.addAction(ZoomOnCrossButton)
        ZoomOnCrossButton.triggered.connect(self.zoomOnCross)

        # set a scene in the view
        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        self.middleClick = False
        self.scene.mousePressEvent = self.newPictureGCP
        self.scene.mouseReleaseEvent = self.releaseWheel
        #self.ui.graphicsView.mousePressEvent = self.test
        #self.scene.mouseMoveEvent = self.mouseMouseWheel
        #Use a TableModel for managing GCP
        self.model = GCPTableModel()#"GCPs.dat")#######
        self.ui.tableView.setModel(self.model)
        for i in range(0,8) :
            self.ui.tableView.setColumnWidth(i,89)
        # Hide 3D errors for now
        self.ui.tableView.setColumnHidden(6,True) 
        header = self.ui.tableView.horizontalHeader()
        self.ui.tableView.selectionModel().currentRowChanged.connect(self.refreshPictureGCP) 
        self.ui.tableView.selectionModel().currentRowChanged.connect(self.refreshCanvasGCP) 
        self.ui.graphicsView.wheelEvent = self.wheelEvent
        self.countZoom = 0    
        self.canvas.extentsChanged.connect(self.refreshCanvasGCPNumbers)
        
        # Following are parameters for pose estimation
        # The variables are chosen such that the integration of openGL is straightforward
        self.pos = None
        self.lookat = None
        self.FOV = 30
        self.roll = 0
        self.upWorld = asarray([0,1,0])
        self.paramPoseView  = [0,0,0,0,0,0,0,self.sizePicture[0]/2.0,self.sizePicture[1]/2.0]
        self.positionFixed = False
        # indice for fixed or free parameters for pose estimation
        self.whoIsChecked = [True, False, False]*7
        self.ui.statusbar.showMessage('Need at least 4 GCP and apriori values or 6 GCP for pose estimation')
                
    def saveAsKML(self):
        # Save the pose in KML file. It can be open in googleEarth
        if self.pos :
            pos = self.pos
            roll = self.roll
            FOV = self.FOV
            lookat = self.lookat
            dx = pos[0]-lookat[0]
            dy = pos[2]-lookat[2]
            dz = pos[1]-lookat[1]
            heading = old_div(arctan2(dx,-dy)*180,pi)
            tilt = old_div(arctan(old_div(-dz,sqrt(dx**2+dy**2)))*180,pi)+90
            
            crsT = "EPSG:" + str(self.crs.postgisSrid())
            crsSource = QgsCoordinateReferenceSystem(crsT)
            crsTarget = QgsCoordinateReferenceSystem("EPSG:4326")
            xform = QgsCoordinateTransform(crsSource, crsTarget, QgsProject.instance())
            WGSPos = xform.transform(QgsPointXY(-pos[0],pos[2]))
            altitude = pos[1]
            est = WGSPos[0]
            nord = WGSPos[1]
            ratio = self.sizePicture[0]/float(self.sizePicture[1])
            leftFOV = -ratio*FOV/2.0
            rightFOV = ratio*FOV/2.0
            topFOV = FOV/2.0
            bottomFOV = -FOV/2.0
            near = 300.0
            self.writeKML(est, nord, altitude, heading, tilt, roll, leftFOV, rightFOV, topFOV, bottomFOV, near)
            self.ui.statusbar.showMessage('Pose saved in KML file')
        else:
             QMessageBox.warning(self,"Error","Pose not valid")
        
    def loadAsKML(self):
        # Read a KML file created by th plugin or a KML for a picture pose in google Earth
        kmlName = '/' + (self.picture_name.split(".")[0]).split("/")[-1] + '_pose.kml'
        path = self.pathToData + kmlName
        fName = QFileDialog.getOpenFileName(self, 'Open file',path,("Kml (*.kml)"))[0]
        if not fName:
            return
        file=QFile(fName)

        if (not file.open(QIODevice.ReadOnly | QIODevice.Text)):
            QMessageBox.warning(self, 'Application', QString('Cannot read file %1:\n%2.').arg(fname).arg(file.errorString()))
            return False
        else:
            # FIXME QtXml is no longer supported.
            doc = QtXml.QDomDocument("EnvironmentML");
            if(not doc.setContent(file)):
                file.close()
                QMessageBox.warning(self,"Error","Could not parse xml file.")
            file.close()
            root = doc.documentElement();
            if(root.tagName()!="kml"):
                 QMessageBox.warning(self,"Error","Could not parse xml file. Root Element must be <kml/>.")
            else:
                try:
                    longitude = float(doc.elementsByTagName('longitude').at(0).firstChild().toText().data())
                    latitude = float(doc.elementsByTagName('latitude').at(0).firstChild().toText().data())
                    altitude = float(doc.elementsByTagName('altitude').at(0).firstChild().toText().data())
                    Heading = float(doc.elementsByTagName('heading').at(0).firstChild().toText().data())
                    Tilt = float(doc.elementsByTagName('tilt').at(0).firstChild().toText().data())
                    Roll = float(doc.elementsByTagName('roll').at(0).firstChild().toText().data())
                    altitudeMode = doc.elementsByTagName('altitudeMode').at(0).firstChild().toText().data()
                    if altitudeMode == '':
                        altitudeMode = doc.elementsByTagName('gx:altitudeMode').at(0).firstChild().toText().data()
                    leftFov = float(doc.elementsByTagName('leftFov').at(0).firstChild().toText().data())
                    rightFov = float(doc.elementsByTagName('rightFov').at(0).firstChild().toText().data())
                    bottomFov = float(doc.elementsByTagName('bottomFov').at(0).firstChild().toText().data())
                    topFov = float(doc.elementsByTagName('topFov').at(0).firstChild().toText().data())
                    try:
                        Rotation = float(doc.elementsByTagName('rotation').at(0).firstChild().toText().data())
                    except:
                        Rotation = 0
                except:
                     QMessageBox.warning(self,"Error","Could not use xml file. Problem parsing.")
                else:
                    #The focal has to be centered
                    if leftFov != -1*rightFov or bottomFov != -1*topFov:
                         QMessageBox.warning(self,"Error","Could not use xml file. Problem of field of view definition.")
                    #Only the absolute elevation is possible. The mode "above the ground" is not supported
                    if altitudeMode != 'absolute' and altitudeMode != 'relativeToSeaFloor':
                         QMessageBox.warning(self,"Error","Could not use xml file. Problem of altitude definition (1).")
                    #The has to be near zero given the construction of the KML. The roll is not given by the Roll, but by Rotation
                    #if Roll > 0.1:
                    #     QMessageBox.warning(QMainWindow(),"Error","Could not use xml file. Problem of roll definition.")
                    #Check if the latitude and longitude are valid
                    if latitude > 91 or latitude < -91 or longitude > 361 :
                         QMessageBox.warning(self,"Error","Could not use xml file. Problem of coordinates definition.")
                    
                    # Transform the position coordinates from wgs84 to the DEM coordinate system
                    crsT = "EPSG:" + str(self.crs.postgisSrid())
                    crsTarget = QgsCoordinateReferenceSystem(crsT)
                    crsSource = QgsCoordinateReferenceSystem("EPSG:4326")
                    xform = QgsCoordinateTransform(crsSource, crsTarget, QgsProject.instance())
                    LocalPos = xform.transform(QgsPointXY(longitude,latitude))
                    if altitudeMode == 'relativeToSeaFloor':
                        #try:
                        if self.cLayer:
                            ident =  self.cLayer.dataProvider().identify(QgsPointXY(LocalPos[0],LocalPos[1]),QgsRaster.IdentifyFormatValue).results()
                            if len(list(ident.items())) > 1:
                                raise IOError("Multiband layer selected")
                            value = ident.get(1)
                            altitude = altitude + value
                        #except :
                            #QMessageBox.warning(QMainWindow(),"Error","Could not use xml file. Problem of altitude definition (2).")
                    pos = [-LocalPos[0], altitude, LocalPos[1]]
                    FOV = 2*topFov
                    heading = Heading/180.0*pi
                    roll = Rotation/180.0*pi
                    tilt = Tilt/180.0*pi
                    swing = -roll

                    self.paramPoseView[0] = -LocalPos[0]
                    self.paramPoseView[1] = LocalPos[1]
                    self.paramPoseView[2] = altitude
                    self.paramPoseView[3] = Tilt
                    self.paramPoseView[4] = -Heading
                    self.paramPoseView[5] = -Rotation*180.0/pi
                    radFOV = FOV*pi/180
                    self.paramPoseView[6] = self.sizePicture[1]/(2*tan(radFOV/2))
                    self.whoIsChecked = [False, True, False]*7

                    

                    #try:
                    #    swing = arcsin(sin(roll)/(-sin(tilt)))
                    #except ZeroDivisionError:
                    #    print 'zero div'
                    #    swing = 0
     
                    
                    
                    #Create a rotation matrix . the point [0,0,-1] is rotated for the openGL "lookat" function.
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
                    # Get "look at" vector for openGL pose
                    ######################################
                    
                    #Generate vectors in camera system
                    dirCam = array([0.,0.,-1.])
                    upCam = array([0.,1.,0.])
                    downCam = array([0.,1.,0.])
                    
                    #Rotate in the world system
                    dirWorld = dot(linalg.inv(R),dirCam.T)
                    lookat_temp = array(dirWorld)+array([LocalPos[0], LocalPos[1] , altitude])
                    lookat = array([-lookat_temp[0], lookat_temp[2], lookat_temp[1]])
                    
                    upWorld_temp = dot(linalg.inv(R),upCam.T) 
                    upWorld = array([-upWorld_temp[0], -upWorld_temp[2], upWorld_temp[1]])
        
                    #not_awesome_vector = array([0,0,-1])
                    #fast_awesome_vector = dot(linalg.inv(R),not_awesome_vector)
                    #awesome_vector = array(fast_awesome_vector)+array([LocalPos[0], LocalPos[1] , altitude])
                    #lookat = array([-awesome_vector[0], awesome_vector[2], awesome_vector[1]])
                    
                    # Get parameters for pose in openGL
                    self.roll = roll
                    self.FOV = FOV
                    self.pos = pos
                    self.lookat = lookat
                    self.upWorld = upWorld
                    self.ui.statusbar.showMessage('Pose loaded from KML file.')
                    # self.GoToMonoplotterButton.setEnabled(True)
                    
                        
    def fixFocal(self, focalPixel):
        self.paramPoseView[6] = focalPixel
        self.whoIsChecked[19] = False
        self.whoIsChecked[20] = True
        self.whoIsChecked[18] = False

        
    def zoomOnCross(self):
        if self.ui.tableView.selectedIndexes() != []:
            index = self.ui.tableView.currentIndex()
            if not index.isValid():
                return
            row = index.row()
            pos = []
            for i in range(0,5):
                index = self.model.index(row, i)
                pos.append(self.model.data(index))
                if not isinstance(pos[i], (int, float)):
                   QMessageBox.warning(self, "Value - Error","Failed to load current point" )
                   return

            matrix = QTransform()
            zoomFactorOnCross = old_div(QGuiApplication.primaryScreen().geometry().height(),(10.0*(self.sizePicture[0]/80.0)))
            matrix.scale(zoomFactorOnCross, zoomFactorOnCross)
            self.ui.graphicsView.setTransform(matrix)
            hOffset = old_div(self.ui.graphicsView.size().width(),(2.0*zoomFactorOnCross))
            vOffset = old_div(self.ui.graphicsView.size().height(),(2.0*zoomFactorOnCross))
            hValue = (pos[0]-hOffset)*matrix.m11()
            vValue = (pos[1]-vOffset)*matrix.m22()
            self.ui.graphicsView.horizontalScrollBar().setValue(hValue)
            self.ui.graphicsView.verticalScrollBar().setValue(vValue)
            self.countZoom = 13
            self.resizeCross(1.21, True)
            self.setCanvasExtentSignal.emit((pos[2],pos[3]))
            self.ui.statusbar.showMessage('View zoomed on selected GCP')
        
    def call3DView(self):
        # create an openGL window.
        self.view3D = D3_view(self.pointBuffer, None,  self.roll, self.FOV, 100, self.pos, self.lookat, self.upWorld, self.isFrameBufferSupported)
        self.view3D.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.view3D.show()
        # emit when left click and Ctrl is pressed
        self.view3D.getGCPIn3DviewSignal.connect(self.getGCPIn3Dview) 
        
        #emit when left click and Alt is pressed   
        self.view3D.fixPositionSignal.connect(self.fixPosition)  

        #get same size as the scene
        resolution = QGuiApplication.primaryScreen().geometry()
        size = [0,0]
        size[1] = old_div(resolution.height(),2)
        size[0] = int(self.sizePicture[0]/float(self.sizePicture[1])*size[1])
        self.view3D.resize(size[0],size[1])
        offsetU = self.sizePicture[0]+2*abs(self.paramPoseView[7]-old_div(self.sizePicture[0],2))
        offsetV = self.sizePicture[1]+2*abs(self.paramPoseView[8]-old_div(self.sizePicture[1],2))
        #self.view3D.resize(offsetU,offsetV)
        self.refresh3DGCPs()
        self.ui.statusbar.showMessage('in 3D view: ctrl+click for GCP position, alt+click for camera position')
        
    def refresh3DGCPs(self):
        # draw GCP in the 3D view. The GCP from canvas are drawn, not the reprojectedCrossection
        rowCount = self.model.rowCount()
        GCPs = []
        for row in range(0,rowCount):
            if  self.model.checkValid(row)==0:
                continue
            index = self.model.index(row, 2)
            localx = -1*self.model.data(index)
            index = self.model.index(row,4)
            localy = self.model.data(index)
            index = self.model.index(row,3)
            localz = self.model.data(index)
            GCPs.append((localx,localy,localz))
        self.view3D.sheeps = GCPs
        self.view3D.sheepsSize = self.iconSet.S3d
        self.view3D.update()
    
    def fixPosition(self, position):
        # Fix position by alt + click on the 3D view before pose estimation
        # It fixes the position in the pose dialogue window
        self.paramPoseView[0] = position[0]
        self.paramPoseView[2] = position[1]+10
        self.paramPoseView[1] = position[2]
        #X
        self.whoIsChecked[0] = False
        self.whoIsChecked[1] = True
        self.whoIsChecked[2] = False
        #Y
        self.whoIsChecked[3] = False
        self.whoIsChecked[4] = True
        self.whoIsChecked[5] = False
        #Z
        self.whoIsChecked[6] = False
        self.whoIsChecked[7] = True
        self.whoIsChecked[8] = False
        
        self.ui.statusbar.showMessage('Position Fixed. For unfixing, open the pose estimation dialogue box and free the position')
        
    def getGCPIn3Dview(self):
        # Update world coordinates value of selected GCP when alt+click on the 3D view
        x = -self.view3D.result[0]
        z = self.view3D.result[1]
        y = self.view3D.result[2]
        self.updateLocalGCP(x,y,z)
        self.refresh3DGCPs()
        
    def PoseView(self):
        # create a dialogue window for pose estimation
        self.ui.tableView.clearSelection()
        self.refreshPictureGCP()
        rowCount = self.model.rowCount()
        # get needed inputs for pose estimation
        self.poseDialogue = Pose_dialog(self.model, self.paramPoseView, self.positionFixed, self.sizePicture, self.whoIsChecked, self.pathToData, self.picture_name, self.iface, self.crs)
        self.poseDialogue.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.poseDialogue.update.connect(self.updatePose)
        self.poseDialogue.importUpdate.connect(self.updateWithImport)
        if self.boolPose : 
            self.poseDialogue.actionOnButton("E", True)
            self.poseDialogue.actionOnButton("C", "G")
        self.poseDialogue.show()
        #result = self.poseDialogue.exec_()
        
    def updatePose(self):
        try:
            if hasattr(self, 'reprojectedCross'):
                    for ri in self.reprojectedCross:
                        self.canvas.scene().removeItem(ri)
            if not self.poseDialogue.done:
                raise ValueError
            else:
                
                self.lookat = [0,0,0]
                self.lookat[0] = self.poseDialogue.lookat[0]; self.lookat[2] = self.poseDialogue.lookat[1]; self.lookat[1] = self.poseDialogue.lookat[2]
                
                self.upWorld = [0,0,0]
                self.upWorld[0] = self.poseDialogue.upWorld[0]; self.upWorld[2] = self.poseDialogue.upWorld[1]; self.upWorld[1] = self.poseDialogue.upWorld[2]
                
                self.pos = [0,0,0]
                self.pos[0] = self.poseDialogue.pos[0]; self.pos[2] = self.poseDialogue.pos[1]; self.pos[1] = self.poseDialogue.pos[2]
                
                self.FOV = self.poseDialogue.FOV
                self.roll = self.poseDialogue.roll
                self.paramPoseView = self.poseDialogue.result
                self.whoIsChecked = self.poseDialogue.whoIsChecked
                self.XYZUsed = self.poseDialogue.gcp_xyz_used
                self.GCPErrorPos()
                self.getPositionInCanvas()
                self.boolPose = True
                # self.GoToMonoplotterButton.setEnabled(True)
                self.ui.statusbar.showMessage('You can save GCPs in .dat file or save pose estimation in KML file')
                
                
        except ValueError:
           QMessageBox.warning(self, "Pose Estimation- Error","Failed to estimate pose, consider to provide apriori values")
        
    def updateWithImport(self) :

            self.lookat = self.poseDialogue.lookat
            self.upWorld = self.poseDialogue.upWorld
            self.pos = self.poseDialogue.pos
            self.FOV = self.poseDialogue.FOV
            self.roll = self.poseDialogue.roll
            self.paramPoseView = self.poseDialogue.result
            self.whoIsChecked = self.poseDialogue.whoIsChecked
            # self.GoToMonoplotterButton.setEnabled(True)
            
    
    def getPositionInCanvas(self):
        self.canvas.scene().removeItem(self.poseCanvas)
        xPos = -self.paramPoseView[0]
        yPos = self.paramPoseView[1]
        
        points = QgsPointXY(xPos,yPos)
        self.poseCanvas = QgsVertexMarker(self.canvas)
        self.poseCanvas.setCenter(points)
        self.poseCanvas.setColor(QColor(255, 255, 0))
        self.poseCanvas.setIconSize(self.iconSet.SC)
        self.poseCanvas.setIconType(QgsVertexMarker.ICON_BOX)
        self.poseCanvas.setPenWidth(self.iconSet.WC)
        
            
    def GCPErrorPos(self):      
        nb_gcps = self.model.rowCount()
        pen = QPen(self.iconSet.colorC, self.iconSet.WM, Qt.SolidLine)

        # This is a dirty fix.
        self.uvTableActivated = []
        self.uvTableAll = []

        index_prediction = 0
        index_gcp = 0
        for index_gcp in range(0, nb_gcps):
            gcp_enabled = self.model.data(self.model.index(index_gcp,5)) == 1
            u = self.model.data(self.model.index(index_gcp, 0))
            v = self.model.data(self.model.index(index_gcp, 1))
            self.uvTableAll.append([u, v])

            if gcp_enabled:
                # Draw predictions in the picture
                prediction = self.poseDialogue.predictions[index_prediction]
                self.itemCross(prediction[0], prediction[1], pen, index_gcp)
                self.uvTableActivated.append([prediction[0], prediction[1]])
                # Update Pixel Errors
                pixel_error = round(self.poseDialogue.errors[index_prediction], 0)
                index_prediction += 1
            else:
                pixel_error = -1
            self.model.setData(self.model.index(index_gcp,7), int(pixel_error))
        self.poseDialogue.gcp_table_model = self.model
        self.refreshPictureGCP()
        
        #Used for report on GCPs
        self.poseDialogue.gcp_table_model = self.model
            

    def iconsView(self):
        # Settings of the icons
        self.iconDia = icons_dialog(self.iconSet)
        self.iconDia.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.iconDia.show()
        result = self.iconDia.exec_()
        if result == 1:
            self.iconSet.SM = self.iconDia.uiIcons.spinBoxSM.value()
            self.iconSet.WM = self.iconDia.uiIcons.spinBoxWM.value()
            self.iconSet.SC = self.iconDia.uiIcons.spinBoxSC.value()
            self.iconSet.WC = self.iconDia.uiIcons.spinBoxWC.value()
            self.iconSet.S3d = self.iconDia.uiIcons.spinBoxS3d.value()
            self.iconSet.colorC = self.iconDia.uiIcons.colorCButton.palette().color(1)
            self.iconSet.colorM = self.iconDia.uiIcons.colorMButton.palette().color(1)
         
        try:
            self.refreshPictureGCP()
            self.refreshCanvasGCP()
        except:
            QMessageBox.warning(self, "Icons - Error",
                    "Failed update icons: %s" % e)
        
    def wheelEvent(self, event):
        #Zoom with wheel
        self.ui.graphicsView.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.ui.graphicsView.setResizeAnchor(QGraphicsView.NoAnchor)
        
        oldPos = self.ui.graphicsView.mapToScene(event.pos())

        factor = 1.41 ** (event.angleDelta().y() / 240.0)
        self.zoomFactor = factor
        self.resizeCross(factor)

        newPos = self.ui.graphicsView.mapToScene(event.pos())
        delta = newPos - oldPos
        self.ui.graphicsView.translate(delta.x(), delta.y())

    def Pan(self, pressed):
        #Pan when pan button is toogled
        self.ZoomInButton.setChecked(False)
        self.ZoomOutButton.setChecked(False)
        if pressed:
            self.ui.tableView.clearSelection()
            self.ui.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
        else:
            self.ui.graphicsView.setDragMode(QGraphicsView.NoDrag)
    
    def ZoomOut(self, pressed):
        # zoom out when correponding button is pushed
        self.ui.statusbar.showMessage('Zoom out by clicking on the picture')
        self.ZoomInButton.setChecked(False) 
        self.PanButton.setChecked(False)
        self.ui.graphicsView.setDragMode(QGraphicsView.NoDrag)
        
        
    def ZoomIn(self, pressed):
        # zoom in when correponding button is pushed
        self.ui.statusbar.showMessage('Zoom in by clicking on the picture')
        self.ZoomOutButton.setChecked(False)
        self.PanButton.setChecked(False)
        self.ui.graphicsView.setDragMode(QGraphicsView.NoDrag)    
        
 
    def resizeCross(self, factor, zoomOnGCP=False):
        #redraw the crosses on the picture with a size matching the zoom
        ZoomInFactor = 1.1874
        ZoomOutFactor = 0.8421
        if factor > 1  and self.countZoom < 25 and zoomOnGCP == False :
            self.countZoom += 1
            self.ui.graphicsView.scale(ZoomInFactor, ZoomInFactor)
            self.iconSet.SM = self.iconSet.SM * ZoomOutFactor
            self.iconSet.WM = self.iconSet.WM * ZoomOutFactor

        elif factor < 1 and self.countZoom > -2 and zoomOnGCP == False :
            self.countZoom -= 1
            self.ui.graphicsView.scale(ZoomOutFactor, ZoomOutFactor)
            self.iconSet.SM = self.iconSet.SM * ZoomInFactor
            self.iconSet.WM = self.iconSet.WM * ZoomInFactor
        
        #self.iconSet.SM = int((-2.8148*self.countZoom) + 74.37)
        #self.iconSet.WM = int((-0.6666*self.countZoom) + 18.66)    
        self.refreshPictureGCP()
        


    def selectCanvasPoint(self, point):
        # Canvas coordinates for selected GCP are set
        try:
            if self.cLayer:
                ident =  self.cLayer.dataProvider().identify(point,QgsRaster.IdentifyFormatValue).results()
                if len(list(ident.items())) > 1:
                    raise IOError("Multiband layer selected")
                value = ident.get(1)
                self.updateLocalGCP(point.x(), point.y(), value)
            else:
                QMessageBox.warning(self, "DEM error","Failed to select layer")
        except:
            QMessageBox.warning(self, "DEM error", "Failed to get altitude of the point")
        
    def removeGCP(self):
        # remove GCP from table
        index = self.ui.tableView.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        row_text = row+1
        buffer = "Remove Point %d ?" % row_text
        if QMessageBox.question(self, "GCPs - Remove", buffer ,\
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.No:
            return
        self.model.removeRows(row)
        self.refreshPictureGCP()
        self.refreshCanvasGCP()
        index = self.model.index(row-1, 6)
        
    def reject(self):
        self.save()

    def saveGCP(self):
        # Save GCP to a .csv file
        gcpName = '/' + (self.picture_name.split(".")[0]).split("/")[-1] + '_GCPs'
        path = self.pathToData + gcpName
        fSaveName = QFileDialog.getSaveFileName(self, 'Save your GCPs as...',\
                                                  path,"File (*.csv)")[0]
        if fSaveName:
            try:
                self.model.save(fSaveName)
                self.ui.statusbar.showMessage('GCPS saved as csv')
            except:
                QMessageBox.warning(self, "Points - Error",
                        "Failed to save: %s" % e)
            
    def setImage(self, name, size):
        # Set the picture in the scene
        img = Image.open(name)
        self.picture = QPixmap(name)
        size_pic = self.picture.size()
        self.picture = self.picture.scaled(size_pic, Qt.AspectRatioMode.IgnoreAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.scene.addPixmap(self.picture)
        self.scene.update()
        self.ui.graphicsView.show()
        
    def closeEvent(self, event):
        # two different behaviors occurs. Either we quit the window, either we go to the monoplotter
        self.clearMapTool2.emit()
        self.ui.dockWidget_2.setFloating(False)
        if not self.goToMonoplot:    
            reply = QMessageBox.question(self, 'Message',
                "Are you sure to quit?", QMessageBox.Yes | 
                QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                event.accept()
                if hasattr(self, 'view3D'):
                    self.view3D.close()
                if hasattr(self, 'poseDialogue'):
                    self.poseDialogue.close()
                if hasattr(self, 'iconDia'):
                    self.iconDia.close()
                self.removereprojectedCrossections()
                for ri in self.canvasCross:
                    self.canvas.scene().removeItem(ri)
                for ri in self.canvasNumber:
                    self.canvas.scene().removeItem(ri)
                for ri in self.reprojectedCross:
                    self.canvas.scene().removeItem(ri)
                self.canvas.scene().removeItem(self.poseCanvas)
                self.model = None
                self.view3D = None
                
            else:
                event.ignore()
        else:
            if hasattr(self, 'view3D'):
                self.view3D.close()
            if hasattr(self, 'poseDialogue'):
                self.poseDialogue.close()
            if hasattr(self, 'iconDia'):
                self.iconDia.close()
            self.removereprojectedCrossections()
            for ri in self.canvasCross:
                self.canvas.scene().removeItem(ri)
            for ri in self.canvasNumber:
                self.canvas.scene().removeItem(ri)
            for ri in self.reprojectedCross:
                self.canvas.scene().removeItem(ri)
            self.canvas.scene().removeItem(self.poseCanvas)
            #self.canvas.refresh()
            #self.model = None
            #self.view3D = None

    def loadGCP(self):
        # load GCP from .dat file
        gcpName = '/' + (self.picture_name.split(".")[0]).split("/")[-1] + '_GCPs'
        path = self.pathToData + gcpName
        fLoadName = QFileDialog.getOpenFileName(self, 'Load your GCPs',\
                                                  path,"File (*.dat *.csv)")[0]
        discard = False
        cancel = False
        if self.model.rowCount() > 0  and fLoadName :                                           
            QuestionBox = QMessageBox(self)
            QuestionBox.setIcon(QMessageBox.Icon.Warning)
            QuestionBox.setWindowTitle("GCPs already present")
            QuestionBox.setText("How do you want to handle the current GCPs?")
            QuestionBox.setStandardButtons(QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel)
            ButtonDiscard = QuestionBox.button(QMessageBox.StandardButton.Discard)
            ButtonDiscard.setText("Replace")
            ButtonSave = QuestionBox.button(QMessageBox.StandardButton.Save)
            ButtonSave.setText("Keep")
            ret = QuestionBox.exec_()
            if ret == QMessageBox.StandardButton.Discard :
                discard = True
            elif ret == QMessageBox.StandardButton.Cancel :
                cancel = True

        if fLoadName and cancel == False :
            try:
                self.model.beginResetModel()
                self.model.load(fLoadName, discard)
                self.model.endResetModel()
                self.refreshPictureGCP()
                self.refreshCanvasGCP()
                
            except Exception as e:
                QMessageBox.warning(self, "GCPs - Error","Failed to load: %s" % e)

    def addGCP(self):
        # add a GCP to the table
        row = self.model.rowCount()
        self.model.insertRows(row)
        index = self.model.index(row, 0)
        self.ui.tableView.setFocus()
        self.ui.tableView.setCurrentIndex(index)
        self.ui.tableView.edit(index)
        self.refreshCanvasGCP()
        self.refreshPictureGCP()

        
    def updateLocalGCP(self, x,y, value):
        # update the X Y Z column of the GCP when a click on the canvas occurs
        index = self.ui.tableView.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        index = self.model.index(row, 2)
        self.model.setData(index, x)
        index = self.model.index(row, 3)
        self.model.setData(index, y)
        index = self.model.index(row, 4)
        self.model.setData(index, value)
        if hasattr(self, 'view3D'):
            self.refresh3DGCPs()
            self.view3D.update()
        return index
    
    def updatePictureGCP(self, position):
        # update U V column of the GCP when a click on the picture occurs
        index = self.ui.tableView.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        index = self.model.index(row, 0)
        self.model.setData(index, position.x())
        index = self.model.index(row, 1)
        self.model.setData(index, position.y())
        self.resetToolSignal.emit()
        return index

    def releaseWheel(self, ev): 
        if ev.button() == Qt.MidButton :
            self.ui.graphicsView.setDragMode(QGraphicsView.NoDrag)
        else : 
            return

    def newPictureGCP(self, ev):
        # mouse event when click on the picture with the GCP tool
        self.ui.graphicsView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.ui.graphicsView.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        if ev.button() == Qt.MouseButton.MiddleButton :
            self.ui.tableView.clearSelection()
            width = (ev.scenePos().x()*self.ui.graphicsView.size().width())/self.sizePicture[0]
            height = (ev.scenePos().y()*self.ui.graphicsView.size().height())/self.sizePicture[1]
            self.ui.graphicsView.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            pos = QPointF(width, height)
            fake = QMouseEvent(QEvent.Type.MouseButtonPress, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,  ev.modifiers())
            self.ui.graphicsView.mousePressEvent(fake)
         
        elif self.ZoomInButton.isChecked():
            self.zoomFactor = 1.5
            self.resizeCross(self.zoomFactor)
            
        elif self.ZoomOutButton.isChecked():
            self.zoomFactor = 0.66
            self.resizeCross(self.zoomFactor)

        else :
            self.ui.statusbar.showMessage('Get 3D coordinate by clicking in the QGIS canvas or in the 3D view')
            if self.ui.tableView.selectedIndexes() != []:
                if ev.button() == Qt.MouseButton.LeftButton:
                    a = ev.scenePos()
                    newDataIndex = self.updatePictureGCP(a)
                    self.refreshPictureGCP()
            
    def refreshPictureGCP(self):
        if self.model :#############
            # redraw all GCP in the picture
            rowCount = self.model.rowCount()
            self.scene.clear()
            self.scene.addPixmap(self.picture)
            for row in range(0,rowCount):
                if  self.model.checkValid(row)==0:
                    continue
                index = self.model.index(row, 0)
                posx = self.model.data(index)
                index = self.model.index(row,1)
                posy = self.model.data(index)
                if row == self.ui.tableView.currentIndex().row():
                    pen = QPen(QColor(255, 0, 0) , self.iconSet.WM, Qt.PenStyle.SolidLine)
                else:
                    pen = QPen(self.iconSet.colorM, self.iconSet.WM, Qt.PenStyle.SolidLine)
                self.itemCross(posx,posy, pen, row)
            
            #redraw reprojectedCrossection after pose estimation
            resolution = QGuiApplication.primaryScreen().geometry()
            size = [0,0]
            size[1] = old_div(resolution.height(),2)
            size[0] = int(self.sizePicture[0]/float(self.sizePicture[1])*size[1])
            for u,v in self.uvTableAll:
                pen = QPen(QColor(240, 160, 240) , self.iconSet.WM, Qt.PenStyle.SolidLine)
                self.itemCross(u,v, pen)
            for u,v in self.uvTableActivated:
                pen = QPen(self.iconSet.colorC , self.iconSet.WM, Qt.PenStyle.SolidLine)
                self.itemCross(u,v, pen)
        
    def refreshCanvasGCP(self):
        if self.model and self.goToMonoplot == False :##############
            # redraw canvas GCP
            rowCount = self.model.rowCount()
            for ri in self.canvasCross:
                self.canvas.scene().removeItem(ri)
            self.canvasCross = [None]*rowCount
            for row in range(0,rowCount):
                if  self.model.checkValid(row)==0:
                    continue
                index = self.model.index(row, 2)
                posx = self.model.data(index)
                index = self.model.index(row,3)
                posy = self.model.data(index)
                if row == self.ui.tableView.currentIndex().row():
                    color = QColor(255, 0, 0)
                else:
                    color = self.iconSet.colorC
                self.drawCanvasGCP(posx,posy,row,color)
        
            
    def drawCanvasGCP(self,posx,posy,row,color):
        # this is called from refreshCanvasGCP.
        self.canvasCross[row] = QgsVertexMarker(self.canvas)
        points = QgsPointXY(posx,posy)
        self.canvasCross[row].setCenter(points)
        self.canvasCross[row].setColor(color)
        self.canvasCross[row].setIconSize(self.iconSet.SC)
        self.canvasCross[row].setIconType(QgsVertexMarker.ICON_CROSS)
        self.canvasCross[row].setPenWidth(self.iconSet.WC)
        self.refreshCanvasGCPNumbers()

        
    def refreshCanvasGCPNumbers(self):
        if self.model and self.goToMonoplot == False :
            for ri in self.canvasNumber:
                self.canvas.scene().removeItem(ri)
            rowCount = self.model.rowCount()
            self.canvasNumber = [None]*rowCount
            for row in range(0,rowCount):
                if  self.model.checkValid(row)==0:
                    continue
                index = self.model.index(row, 2)
                posx = self.model.data(index)
                index = self.model.index(row,3)
                posy = self.model.data(index)
                
                self.canvasNumber[row] =  QGraphicsTextItem();
                font = QFont()
                font.setPixelSize(self.iconSet.SC)
                self.canvasNumber[row].setFont(font)
                u,v = self.WorldToPixelOfCanvasCoordinates(posx,posy)
                pos = QPointF(u,v)
                self.canvasNumber[row].setPos(pos)
                self.canvasNumber[row].setPlainText(str(row+1));
                self.canvasNumber[row].setDefaultTextColor(self.iconSet.colorC)
                self.sceneQgis.addItem(self.canvasNumber[row])
            
    def WorldToPixelOfCanvasCoordinates(self,x,y):
      # This function is called in "clickOnMonoplotter".
      # It convert CSR coordinates (world) into the screen coordinates for a given point in the canvas.
      canvasExtent =  self.canvas.extent()
      canvasBox =  [canvasExtent.xMinimum(), canvasExtent.yMinimum(), canvasExtent.xMaximum(), canvasExtent.yMaximum()]
      UPP = self.canvas.mapUnitsPerPixel()
      u = int(old_div((x-canvasBox[0]),UPP))
      v = int(old_div((canvasBox[3]-y),UPP))
      return (u,v)
        
    def drawCanvasGCPreprojectedCrossection(self,posx,posy,row,color,p0):
        # this is called from GCPErrorPos after pose estimation
        self.reprojectedCross.append(QgsVertexMarker(self.canvas))
        indice_r = len(self.reprojectedCross)-1
        points = QgsPointXY(posx,posy)
        self.reprojectedCross[indice_r].setCenter(points)
        self.reprojectedCross[indice_r].setColor(color)
        self.reprojectedCross[indice_r].setIconSize(self.iconSet.SC)
        self.reprojectedCross[indice_r].setIconType(QgsVertexMarker.ICON_CROSS)
        self.reprojectedCross[indice_r].setPenWidth(self.iconSet.WC)

        self.reprojectedCross.append(QgsRubberBand(self.canvas))
        points = [QgsPointXY(p0[0],p0[1]),  QgsPointXY(posx,posy)]
        self.reprojectedCross[indice_r+1].setToGeometry(QgsGeometry.fromPolylineXY(points), None)
        self.reprojectedCross[indice_r+1].setColor(color)
        self.reprojectedCross[indice_r+1].setWidth(self.iconSet.WC)
            
    def removereprojectedCrossections(self):
        # remove all reprojectedCrossections of GCP 
        self.uvTableActivated = []
        self.uvTableAll = []
        for ri in self.reprojectedCross:
            self.canvas.scene().removeItem(ri)
        self.refreshPictureGCP()
        self.ui.statusbar.showMessage('Reprojections are removed. Pose estimation remains')

    def itemCross(self, posx, posy, pen, row = None):
        # draw GCP as cross on scene
        rad = self.iconSet.SM
        x1 = posx-rad; y1 = posy-rad
        x2 = posx+rad; y2 = posy+rad
        x12 = posx-rad; y12 = posy+rad
        x22 = posx+rad; y22 = posy-rad
        item1 = QGraphicsLineItem(x1,y1,x2,y2,)
        item2 = QGraphicsLineItem(x12,y12,x22,y22)
        item1.setPen(pen); item2.setPen(pen)
        self.scene.addItem(item1); self.scene.addItem(item2)
        if row != None:
            rowText =  QGraphicsTextItem();
            font = QFont()
            font.setPixelSize(ceil(rad*2))
            rowText.setFont(font)
            pos = QPointF(posx+rad,posy-rad)
            rowText.setPos(pos)
            rowText.setPlainText(str(row+1));
            rowText.setDefaultTextColor(self.iconSet.colorM)
            self.scene.addItem(rowText)
            
            
    def center(self):
        # center the window in the screen
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def writeKML(self, est, nord, altitude,  heading, tilt, roll, leftFOV, rightFOV, topFOV, bottomFOV, near):
        # Write the KML 
       
        #The path is the same as the one use for the initialization step
        kmlName = '/' + (self.picture_name.split(".")[0]).split("/")[-1] + '_pose.kml'
        path = self.pathToData + kmlName

        pictureName = self.picture_name.split("/")[-1]
        picturePath = self.pathToData + "/" + pictureName
        if os.path.exists(picturePath):
            picturePathKML = "./" + pictureName
        else :
            picturePathKML = self.picture_name
       
       #Get the name of the saved KML file
        fName = QFileDialog.getSaveFileName(self,"save file dialog" ,path,"Images (*.kml)")[0]
        if fName:
            f = open(fName, 'w')
            f.write(
"""<?xml version="1.0" encoding="utf-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<PhotoOverlay id="space-needle">
    <name>%s</name>
    <Camera>
      <longitude>%.10f</longitude>
      <latitude>%.10f</latitude>
      <altitude>%.10f</altitude>
      <heading>%.10f</heading>
      <tilt>%.10f</tilt>
      <roll>0.0</roll>
      <altitudeMode>absolute</altitudeMode>
    </Camera>
    <Style>
        <IconStyle>
            <Icon>
                <href>:/camera_mode.png</href>
            </Icon>
        </IconStyle>
        <ListStyle>
            <listItemType>check</listItemType>
            <ItemIcon>
                <state>open closed error fetching0 fetching1 fetching2</state>
                <href>http://maps.google.com/mapfiles/kml/shapes/camera-lv.png</href>
            </ItemIcon>
            <bgColor>00ffffff</bgColor>
            <maxSnippetLines>2</maxSnippetLines>
        </ListStyle>
    </Style>
    <Icon>
      <href>%s</href>
    </Icon>
    <rotation>%.10f</rotation>
    <ViewVolume>
      <leftFov>%.10f</leftFov>
      <rightFov>%.10f</rightFov>
      <bottomFov>%.10f</bottomFov>
      <topFov>%.10f</topFov>
      <near>%.10f</near>
    </ViewVolume>
    <Point>
      <altitudeMode>absolute</altitudeMode>
      <coordinates>%.10f,%.10f,%.10f</coordinates>      
    </Point>
</PhotoOverlay>
</kml>"""  % (self.picture_name, est, nord, altitude, 
                      heading, tilt, picturePathKML, roll,
                      leftFOV,rightFOV,bottomFOV,topFOV,near,
                      est,nord,altitude) ) 
            f.close()

            
class icon_settings(object):
    def __init__(self, Size, resolutionDEM):
        # settings of GCP visualization
        self.SM = Size[0]/80.0
        self.WM = Size[0]/240.0
        self.SC = 20
        self.WC = 2
        self.colorC = QColor(0, 0, 255)
        self.colorM = QColor(255, 165, 0)
        self.S3d = resolutionDEM      
