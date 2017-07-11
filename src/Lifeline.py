from PySide import QtGui
from PySide import QtCore

class Lifeline(object):

    position = 0

    def __init__(self,view,header,name,flagCluster = False):
        self.view = view
        self.depthDiff = 3 
        self.flagVisible = True
        self.headerView = header
        self.classname = name
        self.message = []
        self.flagCluster = flagCluster
        self.clusterLifeline = None

    def setClusterLifeline(self,l):
        self.clusterLifeline = l

    def getClusterLifeline(self):
        return self.clusterLifeline

    def getFlagCluster(self):
        return self.flagCluster

    def setFlagCluster(self,flag):
        self.flagCluster = flag

    def setVisible(self,flag):
        self.flagVisible = flag

    def getVisible(self):
        return self.flagVisible
 
    def checkPosHead(self,x,y):
        if self.flagVisible == False:
            return False
        
        if self.headLeftPos < x and x < self.headRightPos:
            if self.headTopPos < y and y < self.headBottomPos:
                return True
        
        return False

    def addMessage(self,msg):
        if msg not in self.message:
            self.message.append(msg)

    def getMessageList(self):
        """
        Pass back message list called in this life-lines
        """
        return self.message

    def setLifelineLength(self,length):
        self.lifeLineLength = length

    def getClassName(self):
        return self.classname

    def getLinePosition(self):
        if True == self.flagCluster:
            return self.position
        elif None == self.clusterLifeline:
            return self.position
        else:
            return self.clusterLifeline.getLinePosition()
 
    def drawAt(self,x,color,name):
        if self.flagVisible == True:
            #self.classname = name
            w = 180
            h = 40
            t = 10
            self.position = x + w/2

            self.headLeftPos = x
            self.headRightPos = x+w
            self.headTopPos = t
            self.headBottomPos = t+h

            qp = QtGui.QPainter()
            qp.begin(self.view)

            qp.drawLine(x+w/2,0,x+w/2,self.lifeLineLength)

            qp.end()

    def drawBody(self,beginPos,endPos,depth,colour):

        if self.flagVisible == True:
            h = endPos - beginPos

            qp = QtGui.QPainter()
            qp.begin(self.view)

            flagIgnoreDepth = False
            if not self.flagCluster and self.clusterLifeline:
                flagIgnoreDepth = self.clusterLifeline.getFlagCluster()

            depth = (self.depthDiff*(depth-1)) if not flagIgnoreDepth else 0

            qp.setBrush(QtGui.QColor(255,255,255))
            qp.drawRect(self.getLinePosition()-5+depth,beginPos,10,h)

            qp.setBrush(QtGui.QColor(colour[0],colour[1],colour[2],50))
            qp.drawRect(self.getLinePosition()-5+depth,beginPos,10,h)
            #qp.drawRect(self.getLinePosition()-5+(self.depthDiff*(depth-1)),beginPos,10,h)

            qp.end()
