from PySide import QtCore, QtGui

class MessageMenu(QtCore.QObject):
   
    actHide = None
    actHideAll = None
    actViewCode = None
    actCloseBody = None
    diagramView = None
 
    def __init__(self,diagramView):
        QtCore.QObject.__init__(self)
        self.actHide = QtGui.QAction('Hide message', self)
        self.actHide.setStatusTip('Hide this message line')
        self.actHide.triggered.connect(self.hideOneMessage)

        self.actHideAll = QtGui.QAction('Hide all', self)
        self.actHideAll.setStatusTip('Hide all the messages')
        self.actHideAll.triggered.connect(self.hideAllMessage)

        self.actViewCode = QtGui.QAction('View code', self)
        self.actViewCode.setStatusTip('View source code of the message')
        self.actViewCode.triggered.connect(self.openCodeViewer)

        self.actCloseBody = QtGui.QAction('Close body', self)
        self.actCloseBody.setStatusTip('View source code of the message')
        self.actCloseBody.triggered.connect(self.closeBody)

        self.diagramView = diagramView

    def hideOneMessage(self):
        self.diagramView.activateHide(True)

    def hideAllMessage(self):
        self.diagramView.hideAllMessageSelected()

    def openCodeViewer(self):
        self.diagramView.openCodeViewer()

    def closeBody(self):
        self.diagramView.closeCurrentHighLightedBody()

    def createHeaderMenus(self):
        pass
        """
        for headInfo in self.headers:
            x = headInfo['x']
            x = x - self.position
            if self.currPosX > x and self.currPosX < x+self.w and self.currPosY > self.t and self.currPosY < self.h+self.t:
                if 0 == self.headers.index(headInfo):
                    break

                self.selectedHeader = headInfo
                menu = QtGui.QMenu()
                if headInfo['flagCluster']:
                    menu.addAction('Scatter')
                else:
                    menu.addAction(self.deleteAct)
                    menu.addAction(self.groupAct)
                menu.exec_(QtGui.QCursor.pos())
        """

