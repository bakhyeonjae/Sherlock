from PySide import QtGui
from PySide.QtGui import QFont
from PySide import QtCore

class Signalline(object):

    squareLength = 25

    def __init__(self,view):
        self.view = view
        self.textWidth = 200

    def setParentViewGeometry(self,width,height):
        self.viewWidth = width
        self.viewHeight = height

    def draw(self,departure,destination,timePos,colour,name,depth,screenPosX,highlight,hiddenFlag,hiddenList,index):
       
        if departure.getVisible() == True and destination.getVisible() == True:
            qp = QtGui.QPainter()
            qp.begin(self.view)

            #if departure != destination:
            if departure.getLinePosition() != destination.getLinePosition():
                self.drawStraightLine(departure,destination,timePos,colour,name,qp,depth,screenPosX,highlight,hiddenFlag,hiddenList,index)
            else:
                self.drawCircularLine(departure,timePos,colour,name,qp,depth,highlight,index)
            qp.end()
        
        #self.view.update()

    def drawCircularLine(self,lifeLine,timePos,colour,name,qp,depth,highlight,index):

        pen_width = 3 if True == highlight else 1
        squarelineLen = self.squareLength
        textHeight = 15
        margin = 10

        pos = lifeLine.getLinePosition()     
        pos += 5+3*(depth-1)

        qp.setBrush(colour)
        qp.setPen(QtGui.QPen(colour,pen_width))

        qp.drawLine(pos,timePos,pos+squarelineLen,timePos)
        qp.drawLine(pos+squarelineLen,timePos,pos+squarelineLen,timePos+squarelineLen)
        qp.drawLine(pos+squarelineLen,timePos+squarelineLen,pos+5,timePos+squarelineLen)
        
        qp.setPen(QtGui.QPen(colour,1))
        needle = QtGui.QPolygon([QtCore.QPoint(pos+5,timePos+squarelineLen), QtCore.QPoint(pos+15,timePos-5+squarelineLen), QtCore.QPoint(pos+15,timePos+5+squarelineLen)])

        qp.drawPolygon(needle)

        qp.setPen(colour)
        font = QtGui.QFont('Decorative', 10, QFont.Bold if True == highlight else QFont.Normal)
        qp.setFont(font)
        wd = QtGui.QFontMetrics(font).boundingRect(" %d : %s "%(index,name)).width()
        qp.drawText(QtCore.QRect(pos+squarelineLen+margin,timePos+(squarelineLen-textHeight)/2,wd,15), QtCore.Qt.AlignCenter, "%d : %s"%(index,name)) 

    def drawStraightLine(self,departure,destination,timePos,colour,name,qp,depth,screenPosX,highlight,hiddenFlag,hiddenCallList,index):
        pen_width = 3 if True == highlight else 1

        posFrom = departure.getLinePosition()     
        posTo = destination.getLinePosition()

        if posFrom < posTo:
            posFrom += 5+3*(depth-1)
        else:
            posFrom += 3*(depth-1)-5

        qp.setPen(QtGui.QPen(colour,pen_width))
        #qp.setRenderHint(QtGui.QPainter.Antialiasing,True)

        if posFrom < posTo:
            line_margin = -10
            multi_msg_margin = 10
            needle = QtGui.QPolygon([QtCore.QPoint(posTo-5,timePos), QtCore.QPoint(posTo-15,timePos-5), QtCore.QPoint(posTo-15,timePos+5)])
        else:
            line_margin = 10
            multi_msg_margin = -10
            needle = QtGui.QPolygon([QtCore.QPoint(posTo+5,timePos), QtCore.QPoint(posTo+15,timePos-5), QtCore.QPoint(posTo+15,timePos+5)])
          
        window_width = self.viewWidth
        if posFrom <= posTo:
            d_posFrom = screenPosX if posFrom < screenPosX else posFrom
            d_posTo   = screenPosX+window_width if posTo > screenPosX+window_width else posTo
        else:
            d_posTo   = screenPosX if posTo < screenPosX else posTo
            d_posFrom = screenPosX+window_width if posFrom > screenPosX+window_width else posFrom 

        if True == hiddenFlag:
            qp.drawLine(d_posFrom,timePos,(d_posTo+d_posFrom)/2-multi_msg_margin,timePos)
            qp.drawLine((d_posFrom+d_posTo)/2+multi_msg_margin,timePos,d_posTo+line_margin,timePos)
            self.drawWave(qp,d_posTo,d_posFrom,timePos,multi_msg_margin,colour,pen_width)
        else:
            qp.drawLine(posFrom,timePos,posTo+line_margin,timePos)

        qp.setBrush(colour)
        qp.setPen(QtGui.QPen(colour,1))
        qp.drawPolygon(needle)

        qp.setPen(colour)
        font = QtGui.QFont('Decorative', 10, QFont.Bold if True == highlight else QFont.Normal)
        qp.setFont(font)

        if True == hiddenFlag:
            text_from = d_posFrom
            text_to = (d_posTo+d_posFrom)/2 - multi_msg_margin
            hidden_call_text = hiddenCallList[-1]['message']
            wd = QtGui.QFontMetrics(font).boundingRect(" %s " % hidden_call_text).width()
            clipped_text_begin_pos = ((text_from+text_to)-wd)/2
            if text_to > text_from:
                clipped_text_begin_pos = text_to - wd if clipped_text_begin_pos > text_to - wd else clipped_text_begin_pos
            else:
                clipped_text_begin_pos = text_to if clipped_text_begin_pos < text_to else clipped_text_begin_pos
                
            qp.drawText(QtCore.QRect(clipped_text_begin_pos,timePos-5-15,wd,15), QtCore.Qt.AlignCenter, hidden_call_text)

            text_from = (d_posTo+d_posFrom)/2 + multi_msg_margin
            text_to = d_posTo
            wd = QtGui.QFontMetrics(font).boundingRect(" %d : %s " % (index,name)).width()
            clipped_text_begin_pos = ((text_from+text_to)-wd)/2
            if text_to > text_from:
                clipped_text_begin_pos = text_from if clipped_text_begin_pos < text_from else clipped_text_begin_pos
            else:
                clipped_text_begin_pos = text_from - wd  if clipped_text_begin_pos > text_from - wd else clipped_text_begin_pos
                
            qp.drawText(QtCore.QRect(clipped_text_begin_pos,timePos-5-15,wd,15), QtCore.Qt.AlignCenter, "%d : %s"%(index,name))
        else:
            wd = QtGui.QFontMetrics(font).boundingRect(" %d : %s "%(index,name)).width()
            qp.drawText(QtCore.QRect(((d_posFrom+d_posTo)-wd)/2,timePos-5-15,wd,15), QtCore.Qt.AlignCenter, "%d : %s"%(index,name)) 

    def drawWave(self,qp,posTo,posFrom,timePos,margin,colour,pen_width):

        if posTo < posFrom:
            tmp = posTo
            posTo = posFrom
            posFrom = tmp

        amplitude = 15
        path = QtGui.QPainterPath()
        a = (posTo+posFrom)/2-margin
        path.moveTo(a,timePos)
        path.cubicTo(a,timePos-amplitude,(posTo+posFrom)/2,timePos-amplitude,(posTo+posFrom)/2,timePos)
        qp.setPen(QtGui.QPen(colour, pen_width, QtCore.Qt.SolidLine, QtCore.Qt.FlatCap, QtCore.Qt.MiterJoin))
        qp.drawPath(path)
        path.cubicTo((posTo+posFrom)/2,timePos+amplitude,(posTo+posFrom)/2+margin,timePos+amplitude,(posTo+posFrom)/2+margin,timePos)
        qp.drawPath(path)

