from PySide import QtCore, QtGui
from PySide.QtGui import QLabel

import Utils
import ClusterDialog

class HeadInfo(object):
    @Utils.argumentsToAttributes
    def __init__(self,x,color,name):
        pass 

class Header(QLabel):
    currPosX = 0
    currPosY = 0
    selectedHeader = None
    def __init__(self,parent = None):
        QLabel.__init__(self, parent)
        self.headers = []
        self.position = 0
        self.viewWidth = 800
        self.viewHeight = 100
        self.hideFlag = False
        self.w = 180
        self.h = 40
        self.t = 10
        self.setMouseTracking(True)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.createHeaderMenus)

        self.deleteAct = QtGui.QAction('Hide', self)
        self.deleteAct.setStatusTip('Hide this life-line')
        self.deleteAct.triggered.connect(self.hideLifeLine)

        self.groupAct = QtGui.QAction('Make a cluster', self)
        self.groupAct.setStatusTip('Make a cluster of multiple life-lines')
        self.groupAct.triggered.connect(self.showClusterDialog)

        self.scatterAct = QtGui.QAction('Scatter', self)
        self.scatterAct.setStatusTip('Scatter this cluster')
        self.scatterAct.triggered.connect(self.scatterCluster)

    def connectMainView(self,mainView):
        """
        mainView contains sequence diagram
        """
        self.mainView = mainView

    def reset(self):
        self.headers = []
        self.update() # Clear up all the heads

    def createHeaderMenus(self):
        for headInfo in self.headers:
            x = headInfo['x']
            x = x - self.position
            if self.currPosX > x and self.currPosX < x+self.w and self.currPosY > self.t and self.currPosY < self.h+self.t:
                if 0 == self.headers.index(headInfo):
                    break

                self.selectedHeader = headInfo
                menu = QtGui.QMenu()
                if headInfo['flagCluster']:
                    menu.addAction(self.scatterAct)
                else:
                    menu.addAction(self.deleteAct)
                    menu.addAction(self.groupAct)
                menu.exec_(QtGui.QCursor.pos())

    def showClusterDialog(self):
        response, cluster_name = ClusterDialog.ClusterDialog.getClusterName(self.mainView.getLifeLines(),self.selectedHeader['name'])

        if response:
            if self.mainView.createCluster(cluster_name):
                pass
            else:
                pass

    def scatterCluster(self):
        self.mainView.removeCluster(self.selectedHeader['name'])
        
    def hideLifeLine(self):
        self.mainView.hideLifeline(self.selectedHeader['name'])
        self.mainView.refreshData()

    def mouseMoveEvent(self,e):
        self.currPosX = e.x()
        self.currPosY = e.y()
        selected_head_name = None
        for headInfo in self.headers:
            x = headInfo['x']
            headx = x - self.position
            if e.x() > headx and e.x() < headx+self.w and e.y() > self.t and e.y() < self.h+self.t:
                msg_list = self.mainView.getMessageList(headInfo['name'])
                formatted = '<< ' + headInfo['name'] + ' >>\n'
                for m in msg_list:
                    formatted += '\n- ' + m
                self.setToolTip(formatted)
                break
            else:
                self.setToolTip('')

    def updateViewSize(self,width,height):
        self.viewWidth = width
        self.setFixedHeight(self.viewHeight)

    def paintEvent(self, event):
        QLabel.paintEvent(self,event)

        self.resize(self.viewWidth,self.viewHeight)

        for headInfo in self.headers:
            name = headInfo['name']
            x = headInfo['x']
            x = x - self.position

            if x+self.w < 0:
                continue

            if x > self.viewWidth:
                continue

            self.headLeftPos = x
            self.headRightPos = x+self.w
            self.headTopPos = self.t
            self.headBottomPos = self.t+self.h

            qp = QtGui.QPainter()
            qp.begin(self)

            qp.setBrush(headInfo['color'])
            qp.drawRect(x,self.t,self.w,self.h)
            qp.setPen(QtGui.QColor(20, 20, 30))
            qp.setFont(QtGui.QFont('Decorative', 10))

            leaf_name = list(reversed(name.split(".")))[0]
            parent_name = ".".join(list(reversed(list(reversed(name.split(".")))[1:])))

            if parent_name == "":
                qp.setFont(QtGui.QFont('Decorative', 11))
                wd = QtGui.QFontMetrics(self.font()).boundingRect(leaf_name).width()
                align_option = QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter if wd > self.w-20 else QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
                qp.drawText(QtCore.QRect(x+10,self.t,self.w-20,self.h), align_option, leaf_name) 
            else:
                qp.setFont(QtGui.QFont('Decorative', 7))
                wd = QtGui.QFontMetrics(self.font()).boundingRect(parent_name).width()
                align_option = QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter if wd > self.w-20 else QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
                qp.drawText(QtCore.QRect(x+10,self.t,self.w-20,self.h/2), align_option, parent_name) 
                qp.setFont(QtGui.QFont('Decorative', 11))
                qp.drawText(QtCore.QRect(x+10,self.t+self.h/2,self.w-20,self.h/2), QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter, leaf_name) 

            qp.drawLine(x+self.w/2,self.h+self.t,x+self.w/2,90000)

            qp.end()

    def mouseReleaseEvent(self, e):
        self.currPosX = e.x()
        self.currPosY = e.y()
        selected_head_name = None

    def wheelEvent(self, e):
        print("mouse wheel event")

    def drawAtHeaderRegion(self,x,color,name,flagCluster):
        item = {'x':x, 'color':color, 'name':name, 'flagCluster':flagCluster}
        if item not in self.headers:
            self.headers.append(item)

    def resetLifelines(self):
        del self.headers[:]

    def setPosition(self, x):
        self.position = x
        self.update()

    def activateHide(self,flag):
        self.hideFlag = flag

    def resetAllLifelines(self):
        pass

    def activateCapture(self,flag):
        pass

    def searchMessage(self,str):
        pass

    def moveToPrev(self):
        pass
        
    def moveToNext(self):
        pass
