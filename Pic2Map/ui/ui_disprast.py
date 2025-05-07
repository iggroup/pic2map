# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QAction

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtCore.QCoreApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtCore.QCoreApplication.translate(context, text, disambig)

class Ui_disprast(object):
    def setupUi(self, disprast):
        disprast.setObjectName("disprast")
        disprast.resize(766, 836)
        disprast.setAnimated(True)
        self.centralwidget = QtWidgets.QWidget(disprast)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setAcceptDrops(True)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        disprast.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(disprast)
        self.statusbar.setObjectName("statusbar")
        disprast.setStatusBar(self.statusbar)
        self.dockWidget_2 = QtWidgets.QDockWidget(disprast)
        self.dockWidget_2.setFloating(False)
        self.dockWidget_2.setObjectName("dockWidget_2")
        self.dockWidget_2.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tableView = TableView(self.dockWidgetContents_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setMouseTracking(False)
        self.tableView.setAutoFillBackground(False)
        self.tableView.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhNone)
        self.tableView.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.tableView.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.tableView.setMidLineWidth(2)
        self.tableView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tableView.setAutoScroll(False)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        self.tableView.setTabKeyNavigation(True)
        self.tableView.setProperty("showDropIndicator", False)
        #self.tableView.setDragDropOverwriteMode(False)
        #self.tableView.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setShowGrid(True)
        self.tableView.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
        self.tableView.setSortingEnabled(False)
        self.tableView.setWordWrap(True)
        self.tableView.setCornerButtonEnabled(False)
        self.tableView.setObjectName("tableView")
        self.tableView.verticalHeader().setVisible(True)
        self.verticalLayout_2.addWidget(self.tableView)
        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        disprast.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockWidget_2)
        self.actionOption1_1 = QAction(disprast)
        self.actionOption1_1.setObjectName("actionOption1_1")
        self.actionOption1_2 = QAction(disprast)
        self.actionOption1_2.setObjectName("actionOption1_2")
        self.actionOption1_3_1 = QAction(disprast)
        self.actionOption1_3_1.setObjectName("actionOption1_3_1")
        self.actionOption1_3_2 = QAction(disprast)
        self.actionOption1_3_2.setObjectName("actionOption1_3_2")
        self.actionOption2_1 = QAction(disprast)
        self.actionOption2_1.setObjectName("actionOption2_1")

        self.retranslateUi(disprast)
        QtCore.QMetaObject.connectSlotsByName(disprast)

    def retranslateUi(self, disprast):
        disprast.setWindowTitle(_translate("disprast", "GCP Positioning Window", None))
        self.dockWidget_2.setWindowTitle(_translate("disprast", "GCP Table", None))

class TableView(QtWidgets.QTableView):
    """
    A simple table to demonstrate the QComboBox delegate.
    """
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.checkValues = ['Disable', 'Enable']
        self.setItemDelegateForColumn(5,ComboBoxDelegate(self, self.checkValues))
        
        
class ComboBoxDelegate(QtWidgets.QItemDelegate):
 
    def __init__(self, owner, itemslist):
        QtWidgets.QItemDelegate.__init__(self, owner)
        self.itemslist = itemslist
        self.owner = owner
 
    def paint(self, painter, option, index):        
        # Get Item Data
        self.owner.openPersistentEditor(index)
        value = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        # fill style options with item data
        style = QtWidgets.QApplication.style()
        opt = QtWidgets.QStyleOptionComboBox()
        opt.currentText = str(self.itemslist[value])
        opt.rect = option.rect
 
        # draw item data as ComboBox
        style.drawComplexControl(QtWidgets.QStyle.ComplexControl.CC_ComboBox, opt, painter)
 
    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        editor.addItems(self.itemslist)
        editor.setCurrentIndex(0)
        editor.installEventFilter(self)            
        return editor
 
    def setEditorData(self, editor, index):
        text = self.itemslist[index.data(QtCore.Qt.ItemDataRole.DisplayRole)]
        pos = editor.findText(text)
        if pos == -1:  
            pos = 0
        editor.setCurrentIndex(pos)
 
    def setModelData(self,editor,model,index):
        #editor.setCurrentIndex(int(index.model().data(index)))
        value = editor.currentIndex()
        model.setData(index, value)
 
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
 
        
