from PySide import QtGui
from PySide import QtCore

import Lifeline
import Signalline
import re
import copy
import traceback
import Utils
import MessageMenu

class CaptainServer(object):
    
    toolBox = None
    srcViewer = None
    cluster = []
    headerView = None
    flagHideCircularLine = False
    messages_to_be_plotted = []
    numberMessage = 0
    currPosX = 0
    currPoxY = 0
    messageMenu = None
    PREVENT_DRAWING_SKIP_PROCESS = 10

    def __init__(self,view):
        """
        Initialise diagram view control unit.

        Args:
            view (QWidget): CaptainServer is not a type of QWidget. It's a control unit of diagram view which occupies major part of screen.

        Returns:
            None
        """
        
        self.view = view
        self.distance = 35
        self.eventoffset = 50
        self.classWidth = 200
        self.messageMenu = MessageMenu.MessageMenu(self)

        self.colour = []
        
        colour_list = [[0,0,255],
                      [255,0,0],
                      [0,0,0],
                      [255,100,0],
                      [100,100,0],
                      [100,0,0],
                      [0,100,0],
                      [0,0,100],
                      [0,100,100],
                      [100,0,100]]

        self.view.setMouseTracking(True)

        for repeat in range(0,10):   #Create 100 colour list
            for colour_idx, colour_item in enumerate(colour_list):
                self.colour.append(colour_item)

        self.reset()

    def connectSourceViewer(self,viewer):
        """
        Connects source viewer objects
        Args:
            viewer (SourceViewer): Source code viewer will be called when a user tries to view a source code by clicking message-line menu
        """
        self.srcViewer = viewer

    def openCodeViewer(self):
        """
        Opens source code viewer. It passes class or module name and message(method or function) name.
        """
        self.srcViewer.openViewer(self.highlightObject['dest'],self.highlightObject['message'])

    def createMenus(self):
        """
        Display popup window and allow users select an action on the selected message.
        When clicking right button of mouse, menu will be pops up.
        """
        msg = self.getMessageLine(self.currPosX,self.currPosY)
        self.highlightObject = msg
        self.selectMessage(self.highlightObject)
        
        menu = QtGui.QMenu()
        menu.addAction(self.messageMenu.actHide)
        menu.addAction(self.messageMenu.actHideAll)
        menu.addAction(self.messageMenu.actViewCode)
        menu.addAction(self.messageMenu.actCloseBody)
        menu.exec_(QtGui.QCursor.pos())

    def reset(self):
        """
        Resets all the data related to sequence drawing
        """
        self.signal = []
        self.lifeLine = []
        self.maxIndex = 0
        self.numberMessage = 0
        self.highlightObject = None
        self.hideString = []
        self.hideThread = []
        self.hideMessage = []
        self.pos_x = 0
        self.pos_y = 0
        self.viewWidth = 1000
        self.initialised = False
        self.srchIdx = []
        self.currIdx = 0
        self.screenY = 0
        self.limitSearchBottomIndex = 0
        self.limitSearchTopIndex = 0
        if self.headerView:
            self.headerView.reset()
        if self.toolBox:
            self.toolBox.reset()

    def getLifeLines(self):
        """
        Pass back the life-lines to a caller
        Returns:
            Lifeline: The list of life-lines
        """
        return self.lifeLine

    def setHideCircularLine(self,flag):
        """
        If circular-hide flag is set, all the self-call message will be erased and the diagram will be re-organised.

        @param flag True when self-call message is erased. False self-call message is displayed.
        @return nothing
        """
        self.flagHideCircularLine = flag

    def initUI(self):
        """
        Initialise the view object given.
        """
        if self.view.layout() != None:
            QtGui.QWidget().setLayout(self.view.layout())  # to remove existing layout
        self.view.show()

    def setToolBox(self,toolBox):
        """
        Connect the tool-box with itself
        """
        self.toolBox = toolBox

    def createCluster(self,name):
        """
        Initially, Sherlock displays all the messages and allow users simplify it.
        When a user wants to merge multiple life-lines into one module or one package, createCluster method will create a new life-line.
        Its name is a package or module name which contains multiple life-line represents classes.
        Life-lines for the classes will be hidden and messages connected to the class life-lines are re-organised and connected to newly created module life-line.

        @param name package name or module name 
        """
        flag = False
        for l in self.lifeLine:
            if name in l.getClassName():
                flag = True
                break

        if not flag:
            return False

        l = Lifeline.Lifeline(self.view,self.headerView,name,True)

        index = 1
        for idx in range(1,len(self.lifeLine)):
            if not self.lifeLine[idx].getFlagCluster():
                index = idx
                break

        self.lifeLine.insert(index,l)
        self.cluster.append({'name':name, 'lifeline':l})

        self.refreshClusters()
        self.refreshData()
        self.view.update()

        return True

    def removeCluster(self, name):
        """
        """
        life_line = next((l for l in self.lifeLine if l.getClassName() == name),None)
        self.lifeLine.remove(life_line)
        cluster = next((l for l in self.cluster if l['name'] == name),None)
        self.cluster.remove(cluster)

        self.refreshClusters()
        self.refreshData()
        self.view.update()

    def hideCircularChanged(self,flag):
        """
        Circular message-line is a message that the caller and the callee is the same.
        This method hide all the circular message lines and update the digram view.
        """
        self.setHideCircularLine(flag)
        self.refreshData()
        self.view.update()
        
    def refreshClusters(self):
        """
        When clusters are added or removed, clusters and life-lines are refreshed.
        After calling this refreshes diagram view.
        """
        # Reset lifeline's cluster flag and cluster lifeline vars
        for l in self.lifeLine:
            if False == l.getFlagCluster():
                l.setClusterLifeline(None)

        # Modify cluster on elementry lifeline's 
        for l in self.lifeLine:
            for cname in self.cluster:
                if cname['name'] in l.getClassName():
                    l.setClusterLifeline(cname['lifeline'])

    def closeCurrentHighLightedBody(self):
        """
        Hide all the messages starts from the highlighted body.
        It looks like it closes its body.
        """
        if self.highlightObject:
            self.hideChildMessages()
            self.refreshData()
            self.view.update() 
        
    def hideChildMessages(self):
        """
        Hide messages generated by the highlighted message and the highlighted message
        """
        index = self.signal.index(self.highlightObject)
        for idx in range(index+1, len(self.signal)):
            if self.signal[idx]['tid'] == self.highlightObject['tid']:
                if len(self.signal[idx]['stack']) > len(self.highlightObject['stack']):
                    self.hideMessage.append(self.signal[idx])
                else:
                    break

    def hideCurrentHighLighted(self):
        """
        Hide the current highlighted message and the child messages.
        And update the view.
        """
        if self.highlightObject not in self.hideMessage:
            self.hideMessage.append(self.highlightObject)
            self.hideChildMessages()

        self.refreshData()
        self.view.update()

    def hideAllMessageSelected(self):
        if self.highlightObject not in self.hideMessage:
            message_name = self.highlightObject['message']
            message_class = self.highlightObject['dest']

            self.hideMessage.append(self.highlightObject)

            for msg in self.signal:
                if msg['message'] == message_name and msg['dest'] == message_class:
                    self.hideMessage.append(msg)
                    index = self.signal.index(msg)
                    for idx in range(index+1, len(self.signal)):
                        if self.signal[idx]['tid'] == msg['tid']:
                            if len(self.signal[idx]['stack']) > len(msg['stack']):
                                self.hideMessage.append(self.signal[idx])
                            else:
                                break

        self.refreshData()
        self.view.update()

    def setDrawingAvailable(self):
        """
        This signals drawing available. Until this method is called, diagram will not be displayed.
        """
        self.initialised = True
        self.pos_y = self.PREVENT_DRAWING_SKIP_PROCESS  # If Y coordinate of screen is the same as scroll coordinate, drawing process doesn't do anything - message line will not be displayed.

        for msg in self.signal:
            if None == msg['bodyendidx']:
                life_line = next((l for l in self.lifeLine if l.getClassName() == msg['dest']),None)
                msg['lifeline'] = life_line
                msg['endtime'] = None
                msg['bodyendidx'] = self.maxIndex
                msg['bodydepth'] = len([d['class'] for d in msg['stack'] if msg['dest'] == d['class']]) + 1

    def updateViewSize(self,width,height):
        """
        Update diagram view geometry and header view geometry
        """
        self.viewWidth = width
        self.viewHeight = height
        self.headerView.updateViewSize(self.viewWidth,self.viewHeight)

    def handleMouseMove(self,x,y):
        """
        Mouse move event to display tool tip
        """
        self.currPosX = x
        self.currPosY = y

        msg = self.getMessageLine(x,y)
        if msg:
            tooltip_str = "<< message info >> \nfrom: " + msg['departure']['class'] + "\n to   : " + msg['dest']
            self.view.setToolTip(tooltip_str)
        else:
            msg = self.getMessageBody(x,y)
            if msg:
                tooltip_str = "<< message body >> \n message: " + msg['message']
                self.view.setToolTip(tooltip_str)
            else:
                self.view.setToolTip(".")

    def selectMessage(self,msg):
        """
        Set a message as the highlighted message and display information on the message.
        """
        self.view.update()
        if msg: 
            hidden_call_flag, hidden_calls = self.getHiddenCalls(msg)
        
        #hidden_call_str = "\n"
        #for hc in hidden_calls:
        #    hidden_call_str += hc['class'] + "\n"

        if msg:
            self.toolBox.setMessageInfoRet(msg['ret'])
            self.toolBox.setMessageInfoArg(msg['params'],msg['args'])
            self.toolBox.setMessageInfoTime(msg['time'],msg['endtime'],"%d"%(Utils.calcTimeConsumed(msg['time'],msg['endtime'])))
            self.toolBox.setMsgInfoMessage(msg['message'])
            self.toolBox.setMsgInfoModule(msg['dest'])

    def handleRelease(self,x,y):
        """
        When mouse button released, set a message as highlighted
        """
        self.currPosX = x
        self.currPosY = y
        msg = self.getMessageLine(x,y)
        self.highlightObject = msg
        self.selectMessage(self.highlightObject)
        
    def getMessageList(self,lifeLineName):
        """
        Get messages that contatined in a life-line

        Args:
            lifeLineName (Lifeline): a life-line object that 

        Returns:
            list of messages belong to the given life-line
        """
        msg_list = None
        for l in self.lifeLine:
            if l.getClassName() == lifeLineName:
                msg_list = l.getMessageList()
                break
        return msg_list

    def getHiddenCalls(self, msg):
        """
        Args:
            msg ():

        Returns:
            bool: True if 
        """
        theVisible = next((s for s in reversed(msg['stack']) for l in self.lifeLine if s['class'] == l.getClassName() and True == l.getVisible()),None)
        theInvisible = []
        for s in reversed(msg['stack']):
            if s['class'] == theVisible['class']:
                break
            else:
                theInvisible.append(s)

        flagHiddenCalls = True if len(theInvisible) > 0 else False

        return flagHiddenCalls, theInvisible

    def getMessageBodyCoordinate(self,msg):
        """
        """
        
        x = next((x for x in self.lifeLine if x.getClassName() == msg['dest']), None).getLinePosition()
        left = x - 10
        right = x + 10
        top = self.eventoffset + Utils.calcCoordinate(self.index_mapper[msg['index']]['mapper'])
        bottom = self.eventoffset + Utils.calcCoordinate(self.index_mapper[msg['bodyendidx']]['mapper'])

        return left, right, top, bottom    
     
    def getMessageLineCoordinate(self,msg):
        """
        Calculate and return coordinate of a message line
        """
        departure_coord = 0

        dest_coord = next((x for x in self.lifeLine if x.getClassName() == msg['dest']), None).getLinePosition()
        departure_coord = next((l for s in reversed(msg['stack']) for l in self.lifeLine if s['class'] == l.getClassName() and True == l.getVisible()), None).getLinePosition()

        y_coord = self.eventoffset+Utils.calcCoordinate(self.index_mapper[msg['index']]['mapper'])

        return departure_coord, dest_coord, y_coord

    def getMessageBody(self,x,y):
        """
        """
        ret_obj = None
        for idx in range(self.limitSearchTopIndex,self.limitSearchBottomIndex+1):
            msg = self.signal[idx]
            l,r,t,b = self.getMessageBodyCoordinate(msg)
            if l < x < r and t < y < b:
                ret_obj = msg
                break

        return ret_obj

    def getMessageLine(self,x,y):
        """
        Get a message line object using a given coordiate
        """
        ret_obj = None
        msg = [s for s in self.signal if y+5 > self.getMessageLineCoordinate(s)[2] > y-Signalline.Signalline.squareLength-5]
        if msg:
            x_departure, x_dest, y = self.getMessageLineCoordinate(msg[0])
            if x_departure == x_dest:
                if x_departure < x < x_departure + Signalline.Signalline.squareLength+10:
                    ret_obj = msg[0]
            else:
                if x_departure < x < x_dest or x_dest < x < x_departure:
                    ret_obj = msg[0]

        return ret_obj

    def getBody(self,x,y):
        pass
    
    def hideLifeline(self,classname):
        """
        """
        self.hideString.append(classname)

    def getHiddenLifeLines(self):
        """
        """
        return self.hideString

    def getHiddenMessages(self):
        """
        Get hidden message list
        """
        return self.hideMessage
        
    def connectController(self,controller):
        """
        """
        self.controller = controller

    def addLifeline(self,classname):
        """
        """
        self.lifeLine.append(Lifeline.Lifeline(self.view,self.headerView,classname))
        self.view.update()

    def setPositionHor(self, x):
        """
        """
        self.pos_x = x
        self.view.update()

    def setPositionVer(self, y):
        """
        """
        self.pos_y = y
        self.view.update()

    def decisionOnMsgShow(self,departure,destination,message):
        """
        """
        if False == departure.getVisible():
            return False 
        if False == destination.getVisible():
            return False
        if message['tid'] in self.hideThread:
            return False
        if message in self.hideMessage:
            return False
        if departure.getLinePosition() == destination.getLinePosition() and True == self.flagHideCircularLine:
            return False

        return True

    def decisionOnBodyShow(self,departure,destination,message):
        """
        """
        if not message['lifeline']:
            return False
        if not destination.getVisible():
            return False
        if message['tid'] in self.hideThread:
            return False
        if message in self.hideMessage:
            return False
        if departure.getLinePosition() == destination.getLinePosition() and True == self.flagHideCircularLine:
            return False

        return True

    def refreshData(self,lifeLineLength = 100000):
        """
        """
        margin = 2 # I don't have any ground for this variable. I'm not sure why the length doesn't match real signal position

        for l in self.lifeLine:
            if l.getClassName() in self.hideString:
                l.setVisible(False)
                l.setLifelineLength(Utils.calcCoordinate(lifeLineLength+margin)+self.eventoffset)
            else:
                l.setVisible(True)
                l.setLifelineLength(Utils.calcCoordinate(lifeLineLength+margin)+self.eventoffset)

        self.index_mapper = []
        for i in range(self.maxIndex+1):
            data = {'mapper':0, 'hiddencall':[]}
            self.index_mapper.append(data)
        
        for msg in self.signal:
            departure_class = next((l for s in reversed(msg['stack']) for l in self.lifeLine if s['class'] == l.getClassName() and True == l.getVisible()),None)
            destination_class = next((l for l in self.lifeLine if msg['dest'] == l.getClassName()),None)
            self.index_mapper[msg['index']]['mapper'] = 1 if self.decisionOnMsgShow(departure_class,destination_class,msg) else 0

            if self.decisionOnBodyShow(departure_class,destination_class,msg):
                self.index_mapper[msg['bodyendidx']]['mapper'] = 1

        for i,v in enumerate(self.index_mapper):
            if i > 0:
                v['mapper'] += self.index_mapper[i-1]['mapper']

    def paintEvent(self, event):
        """
        """
        if False == self.initialised:
            return

        self.drawLifeLine()        
        self.drawMessageLine() 

    def showThread(self, threadIndex, flag):
        """
        """
        if flag:
            self.hideThread.append(threadIndex)
        else:
            idx = self.hideThread.index(threadIndex)
            del self.hideThread[idx]

        self.refreshData()
        self.view.update()

    def drawLifeLine(self):
        """
        """
        # Draw lifelines
        lifeLineIndex = -1 
        self.headerView.resetLifelines()
        for l in self.lifeLine:
            if l.getVisible():
                if (False == l.getFlagCluster() and None == l.getClusterLifeline()) or True == l.getFlagCluster():
                    lifeLineIndex = lifeLineIndex + 1
                    l.drawAt(10+lifeLineIndex*self.classWidth,QtGui.QColor(250,220,200),l.getClassName())
                    head_color = QtGui.QColor(100,200,100) if l.getFlagCluster() else QtGui.QColor(250,220,200)
                    self.headerView.drawAtHeaderRegion(10+lifeLineIndex*self.classWidth,head_color,l.getClassName(),l.getFlagCluster())
        self.headerView.update()

    def drawMessageLine(self):
        """
        """
        # Draw message lines
        max_end_idx = 0
        
        if self.screenY < self.pos_y:   #Down
            tmp_arr = self.messages_to_be_plotted[:]
            for msg in tmp_arr:
                coord_end    = self.eventoffset + Utils.calcCoordinate(self.index_mapper[msg['bodyendidx']]['mapper']) + 25

                if coord_end < self.pos_y:
                    self.messages_to_be_plotted.remove(msg)

            del tmp_arr[:]

            for idx in range(self.limitSearchBottomIndex,len(self.signal)):
                msg = self.signal[idx]
                coord_begin  = self.eventoffset + Utils.calcCoordinate(self.index_mapper[msg['index']]['mapper'])
                coord_end    = self.eventoffset + Utils.calcCoordinate(self.index_mapper[msg['bodyendidx']]['mapper']) + 25

                if coord_end < self.pos_y:
                    continue
                if coord_begin > self.pos_y + self.viewHeight:
                    break

                tmp_bottom_idx = idx
                if msg not in self.messages_to_be_plotted:
                    self.messages_to_be_plotted.append(msg)

        if self.screenY > self.pos_y:  # Up
            tmp_arr = self.messages_to_be_plotted[:]
            for msg in tmp_arr:
                coord_begin = self.eventoffset + Utils.calcCoordinate(self.index_mapper[msg['index']]['mapper'])

                if coord_begin > self.pos_y + self.viewHeight:
                    self.messages_to_be_plotted.remove(msg)

            del tmp_arr[:]
            
            for idx in reversed(range(0,self.limitSearchBottomIndex)):
                msg = self.signal[idx]
                coord_begin = self.eventoffset + Utils.calcCoordinate(self.index_mapper[msg['index']]['mapper'])
                coord_end   = self.eventoffset + Utils.calcCoordinate(self.index_mapper[msg['bodyendidx']]['mapper']) + 25

                if coord_end < self.pos_y:
                    continue
                if coord_begin > self.pos_y + self.viewHeight:
                    continue
            
                if msg not in self.messages_to_be_plotted:
                    self.messages_to_be_plotted.insert(0,msg)
 
        message_idx_list = [l['messageindex'] for l in self.messages_to_be_plotted] 
        if message_idx_list:
            self.limitSearchBottomIndex = max(message_idx_list)
            self.limitSearchTopIndex = min(message_idx_list)
        self.screenY = self.pos_y

        for msg in sorted(self.messages_to_be_plotted, key=lambda k: k['bodydepth']):

            if msg['tid'] in self.hideThread:
                continue
            if msg in self.hideMessage:
                continue

            departure_class = next((l for m in reversed(msg['stack']) for l in self.lifeLine if l.getClassName() == m['class'] and l.flagVisible == True),None)
            destination_class = next((l for l in self.lifeLine if l.getClassName() == msg['dest']),None)

            if departure_class.getLinePosition() == destination_class.getLinePosition() and self.flagHideCircularLine:
                continue
           
            event_colour = self.colour[msg['tid']]
            signal_line = Signalline.Signalline(self.view)
            signal_line.setParentViewGeometry(self.viewWidth,self.viewHeight)

            highlight_flag = True if msg == self.highlightObject else False 
            multi_call_flag, multi_hidden_call = self.getHiddenCalls(msg)
            signal_line.draw(departure_class,destination_class,self.eventoffset+Utils.calcCoordinate(self.index_mapper[msg['index']]['mapper']),QtGui.QColor(event_colour[0],event_colour[1],event_colour[2]),msg['message'],msg['depth'],self.pos_x,highlight_flag,multi_call_flag,multi_hidden_call,msg['messageindex'])

            if departure_class == destination_class:
                msg['lifeline'].drawBody(self.eventoffset+Utils.calcCoordinate(self.index_mapper[msg['index']]['mapper'])+25,self.eventoffset+Utils.calcCoordinate(self.index_mapper[msg['bodyendidx']]['mapper']),msg['bodydepth'],event_colour)
            else:
                msg['lifeline'].drawBody(self.eventoffset+Utils.calcCoordinate(self.index_mapper[msg['index']]['mapper']),self.eventoffset+Utils.calcCoordinate(self.index_mapper[msg['bodyendidx']]['mapper']),msg['bodydepth'],event_colour)

    def sendSignal(self,departure,destination,pSignal,tid,time,index,stack,args,params):
        """
        """
        self.signal.append({'messageindex':self.numberMessage, 'departure':departure,'dest':destination,'message':pSignal,'tid':tid,'time':time,'index':index,'stack':stack.list()[:],'depth':stack.depth('compareClass'), 'lifeline':None, 'endtime':None, 'bodyendidx':None, 'bodydepth':None, 'args':args, 'ret':None, 'params':params})
        self.numberMessage += 1 

        if self.maxIndex < index:
            self.maxIndex = index

    def completeTask(self,className,message,tid,time,indexEnd,bodyDepth,ret):
        """
        """
        circular_flag = False
        body_begin_index = 0
        for msg in reversed(self.signal):
            if className == msg['dest']: # destination
                if msg['message'] == message: # pSignal
                    life_line = next((l for l in self.lifeLine if l.getClassName() == className),None)
                    life_line.addMessage(message)

                    msg['lifeline'] = life_line
                    msg['endtime'] = time
                    msg['bodyendidx'] = indexEnd
                    msg['bodydepth'] = bodyDepth
                    msg['ret'] = ret
                    break

        if self.maxIndex < indexEnd:
            self.maxIndex = indexEnd

    def getWidth(self):
        """
        """
        margin = 100
        
        cnt = 0
        for l in self.lifeLine:
            if False == l.getVisible():
                continue
            if not l.getFlagCluster() and l.getClusterLifeline():
                continue
            cnt += 1

        return cnt*self.classWidth + margin

    def getHeight(self):
        """
        """
        margin = 100
        if 0 == len(self.signal):
            return 100
        else:
            last_index = self.index_mapper[-1]['mapper']
            return self.eventoffset+Utils.calcCoordinate(last_index)+margin

    def connectHeaderView(self,view):
        """
        """
        self.headerView = view

    def activateHide(self,flag):
        """
        """
        self.hideCurrentHighLighted()

    def resetAllLifelines(self):
        """
        """
        del self.hideString[:]
        self.refreshData()
        self.view.update()

    def showLifelines(self, listLifelines):
        """
        """
        for item in listLifelines:
            self.hideString.remove(item)
        self.refreshData()
        self.view.update()

    def showMessages(self, msg):
        """
        """
        selected = [x for x in self.hideMessage if x['messageindex'] == int(msg[0])]
        self.hideMessage.remove(selected[0])
        self.refreshData()
        self.view.update()

    def activateCapture(self,flag):
        """
        """
        pass

    def searchMessage(self,str):
        """
        """
        del self.srchIdx[:]
        for signal in self.signal:
            if str in signal['message']:
                self.srchIdx.append(signal['index'])

        if len(self.srchIdx) > 0:
            self.currIdx = 0
            self.moveToMessage(self.currIdx)

        self.selectMessage(self.highlightObject)
        self.toolBox.updateSearchStatus(self.currIdx+1,len(self.srchIdx))

    def moveToPrev(self):
        """
        """
        if self.currIdx > 0:
            self.moveToMessage(self.currIdx-1)
            self.selectMessage(self.highlightObject)
            self.toolBox.updateSearchStatus(self.currIdx+1,len(self.srchIdx))
        
    def moveToNext(self):
        """
        """
        if self.currIdx < len(self.srchIdx)-1:
            self.moveToMessage(self.currIdx+1)
            self.selectMessage(self.highlightObject)
            self.toolBox.updateSearchStatus(self.currIdx+1,len(self.srchIdx))

    def moveToMessage(self,idx):
        """
        """
        departure_coord = 0
        dest_coord = 0
        self.currIdx = idx
        # find an object which contains specific value in 'index' field 
        msg = [d for d in self.signal if d['index'] == self.srchIdx[self.currIdx]][0]
        
        hidden_cnt = 0
        for _idx, lifeline in enumerate(self.lifeLine):

            if False == lifeline.getVisible():
                hidden_cnt += 1
            if msg['departure'] == lifeline.getClassName():
                departure_coord = (_idx-hidden_cnt)*self.classWidth
            if msg['dest'] == lifeline.getClassName():
                dest_coord = (_idx-hidden_cnt)*self.classWidth
        
        self.highlightObject = msg 
        self.view.moveTo((departure_coord+dest_coord)/2,self.eventoffset+Utils.calcCoordinate(self.index_mapper[self.srchIdx[self.currIdx]]['mapper']))

    def traceForward(self,index):
        """
        """
        msg = self.signal[index]
        sub_plot = []
        sub_plot.append(msg)

        for idx in range(index+1, len(self.signal)):
            if self.signal[idx]['tid'] == msg['tid']:
                if self.signal[idx]['stack']['class'] != msg['stack']:
                    sub_plot.append(self.signal[idx])
                else:
                    break

        print(sub_plot) 
