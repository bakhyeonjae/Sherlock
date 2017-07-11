#!/usr/bin/python3.4

from PySide import QtCore, QtGui
from PySide.QtGui import QLabel, QScrollArea, QWidget, QApplication, QHBoxLayout, QVBoxLayout, QCursor
import sys

import CaptainServer
import Kitchen
import Header
import ToolBox
import const
import pdb
import subprocess
import SourceViewer

class MainView(QLabel):
    def __init__(self, parentQExampleScrollArea, parentQWidget = None):
        QLabel.__init__(self, parentQWidget)
        self.parentQExampleScrollArea = parentQExampleScrollArea
        self.scale = 1.0
        self.position = (0, 0)
        self.pressed = None
        self.anchor = None
        self.drawer = CaptainServer.CaptainServer(self)
        self.drawer.initUI()
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.drawer.createMenus) 
        #self.views = []

    def moveTo(self,x,y):
        self.parentQExampleScrollArea.scrollTo(x,y)

    def updateViewSize(self,width,height):
        self.drawer.updateViewSize(width,height)

    def mousePressEvent (self, eventQMouseEvent):
        self.pressed = eventQMouseEvent.pos()
        self.anchor = self.position

    def mouseReleaseEvent (self, eventQMouseEvent):
        self.pressed = None
        self.drawer.handleRelease(eventQMouseEvent.x(),eventQMouseEvent.y())

    def mouseMoveEvent (self, eventQMouseEvent):
        if (self.pressed):
            dx, dy = eventQMouseEvent.x() - self.pressed.x(), eventQMouseEvent.y() - self.pressed.y()
            self.position = (self.anchor[0] - dx, self.anchor[1] - dy)
        self.drawer.handleMouseMove(eventQMouseEvent.x(),eventQMouseEvent.y())
        self.update()

    def wheelEvent (self, eventQWheelEvent):
        oldscale = self.scale
        self.scale += eventQWheelEvent.delta() / 1200.0
        if (self.scale < 0.1):
            self.scale = oldscale
        screenpoint = self.mapFromGlobal(QCursor.pos())
        dx, dy = screenpoint.x(), screenpoint.y()
        oldpoint = (screenpoint.x() + self.position[0], screenpoint.y() + self.position[1])
        newpoint = (oldpoint[0] * (self.scale/oldscale), oldpoint[1] * (self.scale/oldscale))
        self.position = (newpoint[0] - dx, newpoint[1] - dy)
        print(self.position[0])
        print(self.position[1])
        print("  ")
        self.update()

    def paintEvent (self, eventQPaintEvent):
        scaledWidth  = self.parentQExampleScrollArea.size().width() - 16 
        scaledHeight = self.parentQExampleScrollArea.size().height() - 16 
        width = self.drawer.getWidth()
        height = self.drawer.getHeight()
        self.setFixedSize(width,height)
        self.drawer.paintEvent(eventQPaintEvent)

    def connectHeaderView(self, view):
        self.drawer.connectHeaderView(view)

    def setPositionHor(self,x):
        self.drawer.setPositionHor(x)

    def setPositionVer(self,y):
        self.drawer.setPositionVer(y)

class ScrollArea (QScrollArea):
    def __init__ (self, parentQWidget = None):
        QScrollArea.__init__(self)
        self.mainView = MainView(self)
        self.setWidget(self.mainView)
        self.horizontalScrollBar().valueChanged.connect(self.mainView.setPositionHor)
        self.verticalScrollBar().valueChanged.connect(self.mainView.setPositionVer)
        self.resizeEvent = self.onResize

    def scrollTo(self,x,y):
        self.verticalScrollBar().setValue(y-(self.viewport().size().height())/2)
        self.horizontalScrollBar().setValue(x-(self.viewport().size().width())/2)

    def mousePressEvent (self, eventQMouseEvent):
        QScrollArea.mousePressEvent(self, eventQMouseEvent)
        self.mainView.mousePressEvent(eventQMouseEvent)

    def mouseReleaseEvent (self, eventQMouseEvent):
        QScrollArea.mouseReleaseEvent(self, eventQMouseEvent)
        self.mainView.mouseReleaseEvent(eventQMouseEvent)

    def mouseMoveEvent (self, eventQMouseEvent):
        QScrollArea.mouseMoveEvent(self, eventQMouseEvent)
        print("hello")
        self.mainView.mouseMoveEvent(eventQMouseEvent)

    def wheelEvent (self, eventQWheelEvent):
        self.mainView.wheelEvent(eventQWheelEvent)
        

    def connectView(self, view):
        self.mainView.connectView(view)

    def connectHeaderView(self, view):
        self.mainView.connectHeaderView(view)
        self.horizontalScrollBar().valueChanged.connect(view.setPosition)

    def onResize(self,event):
        self.mainView.updateViewSize(self.width(),self.height())

class MainWindow(QWidget):
    def __init__(self, argv, parentQWidget = None):
        QWidget.__init__(self)

        const.mode_interactive = 1
        const.mode_file = 2
        const.mode_batch = 3
        const.mode_default = const.mode_batch

        arg_file = ''
        if '-i' in argv:
            mode = const.mode_interactive
        elif '-b' in argv:
            mode = const.mode_batch
        elif '-f' in argv:
            mode = const.mode_file
            idx = argv.index('-f')
            arg_file = argv[idx+1]

        src_path = None
        if '-s' in argv:
            idx = argv.index('-s')
            src_path = argv[idx+1]

        if '-c' in argv:
            idx = argv.index('-c')
            cfg_file = argv[idx+1]

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        scrollView = ScrollArea()
        headerView = Header.Header(self)
        scrollView.connectHeaderView(headerView)
        headerView.connectMainView(scrollView.mainView.drawer)
        vbox.addWidget(headerView)
        vbox.addWidget(scrollView)

        toolBox = ToolBox.ToolBox(mode)

        hbox.addLayout(vbox)
        hbox.addLayout(toolBox)

        self.controller = Kitchen.Kitchen(mode,arg_file,cfg_file)
        self.controller.connectView(scrollView.mainView.drawer)
        self.controller.connectToolBox(toolBox)
        self.controller.start()

        srcViewer = SourceViewer.SourceViewer()
        srcViewer.createIndex(src_path)

        toolBox.connectMsgRcv(headerView)
        toolBox.connectMsgRcv(scrollView.mainView.drawer)
        toolBox.connectMsgRcv(self.controller)
        toolBox.connectDiagramView(scrollView.mainView.drawer)

        scrollView.mainView.drawer.setToolBox(toolBox)
        scrollView.mainView.drawer.connectSourceViewer(srcViewer)

        self.setLayout(hbox)

    def closeEvent(self,event):
        self.controller.terminate()

app = QApplication(sys.argv)
mainWindow = MainWindow(sys.argv)
mainWindow.show()
mainWindow.resize(400,400)
mainWindow.move(500,500)
sys.exit(app.exec_())
