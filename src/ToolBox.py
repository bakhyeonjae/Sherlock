from PySide import QtCore, QtGui
from PySide.QtGui import QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QGroupBox, QCheckBox, QLineEdit, QInputDialog, QTableWidget, QTableWidgetItem, QSizePolicy, QFrame

import ClusterDialog
import const
import HiddenDialog
import HiddenMessageDialog
import ShowLifeLineDialog

class ToolBox(QVBoxLayout):

    sig = QtCore.Signal(object)
    listThread = None
    groupBoxThreadInfo = None
    threadvbox = None
    mode = None

    def __init__(self, mode, parentQWidget = None):
        QVBoxLayout.__init__(self)

        self.sig.connect(self.addThreadList)
        self.mode = mode

        self.sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)

        self.groupBoxSearch = QGroupBox()
        self.groupBoxSearch.setStyleSheet("QGroupBox {border: 1px solid gray; border-radius: 4px; };")
        vboxSearch = QVBoxLayout()
        self.searchTitle = QLabel("Search Messages")
        vboxSearch.addWidget(self.searchTitle)
        self.searchHLayout = QHBoxLayout()
        self.editTextSearch = QTextEdit('')
        self.editTextSearch.setFixedSize(200,30)
        self.buttonSearch = QPushButton('Search')
        self.buttonSearch.setFixedSize(100,30)
        self.buttonSearch.clicked.connect(self.searchMsg)
        vboxSearch.addWidget(self.editTextSearch)
        self.searchHLayout.addWidget(self.buttonSearch)
        self.searchCursor = QLabel()
        self.searchHLayout.addWidget(self.searchCursor)
        vboxSearch.addLayout(self.searchHLayout)
        self.browseHLayout = QHBoxLayout()
        self.buttonLookUp = QPushButton('\u21e7')  #Arrow up
        self.buttonLookUp.setFixedWidth(100)
        self.buttonLookUp.clicked.connect(self.moveToPrev)
        self.buttonLookDown = QPushButton('\u21e9') #Arrow down
        self.buttonLookDown.setFixedWidth(100)
        self.buttonLookDown.clicked.connect(self.moveToNext)
        self.browseHLayout.addWidget(self.buttonLookUp)
        self.browseHLayout.addWidget(self.buttonLookDown)
        vboxSearch.addLayout(self.browseHLayout)
        self.groupBoxSearch.setLayout(vboxSearch)
        self.addWidget(self.groupBoxSearch)
        self.groupBoxSearch.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))

        self.buttonHiddenLifelines = QPushButton('Show hidden life-lines')
        self.buttonHiddenLifelines.setFixedWidth(200)
        self.buttonHiddenLifelines.clicked.connect(self.showHiddenLifelines)
        self.addWidget(self.buttonHiddenLifelines)

        self.buttonHiddenMessages = QPushButton('Show hidden Messages')
        self.buttonHiddenMessages.setFixedWidth(200)
        self.buttonHiddenMessages.clicked.connect(self.showHiddenMessages)
        self.addWidget(self.buttonHiddenMessages)

        if const.mode_interactive == mode:
            self.buttonCapture = QPushButton('Capture')
            self.buttonCapture.setFixedWidth(200)
            self.buttonCapture.clicked.connect(self.notifyCapture)
            self.addWidget(self.buttonCapture)
        self.msgRcv = []
        self.msgInfo = QLabel("Message Info.")
        self.groupBoxMessageInfo = QGroupBox()
        self.groupBoxMessageInfo.setStyleSheet("QGroupBox {border: 1px solid gray; border-radius: 9px; margin-top: 0.5em} QGroupBox::title {subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px;")
        vbox = QVBoxLayout()
        vbox.addWidget(self.msgInfo)
        self.tableTime = QtGui.QTableWidget(3,2)
        self.tableTime.setHorizontalHeaderLabels(['-','time'])
        self.tableTime.setColumnWidth(0,80)
        self.tableTime.setColumnWidth(1,150)
        vwidth = self.tableTime.verticalHeader().length()
        hwidth = self.tableTime.horizontalHeader().height()
        fwidth = self.tableTime.frameWidth() * 2
        self.tableTime.setFixedHeight(vwidth + hwidth + fwidth)
        self.tableTime.horizontalHeader().setStretchLastSection(True)
        self.tableTime.setItem(0,0,QTableWidgetItem('begin'))
        self.tableTime.setItem(0,1,QTableWidgetItem(' - '))
        self.tableTime.setItem(1,0,QTableWidgetItem('end'))
        self.tableTime.setItem(1,1,QTableWidgetItem(' - '))
        self.tableTime.setItem(2,0,QTableWidgetItem('duration'))
        self.tableTime.setItem(2,1,QTableWidgetItem(' - '))
        vbox.addWidget(self.tableTime)

        self.titleArg = QLabel('Argument List')
        vbox.addWidget(self.titleArg)

        max_arg_num = 10
        self.tableArgs = QtGui.QTableWidget(max_arg_num,2)
        self.tableArgs.setHorizontalHeaderLabels(['type','value'])
        for idx in range(0,max_arg_num):
            self.tableArgs.setItem(idx,0,QTableWidgetItem())
            self.tableArgs.setItem(idx,1,QTableWidgetItem())
        self.tableArgs.horizontalHeader().setStretchLastSection(True)
        vbox.addWidget(self.tableArgs)

        self.titleArg = QLabel('Return Value List')
        vbox.addWidget(self.titleArg)

        max_ret_num = 4
        self.tableRet = QtGui.QTableWidget(max_ret_num,2)
        self.tableRet.setHorizontalHeaderLabels(['type','value'])
        for idx in range(0,max_ret_num):
            self.tableRet.setItem(idx,0,QTableWidgetItem())
            self.tableRet.setItem(idx,1,QTableWidgetItem())
        self.tableRet.horizontalHeader().setStretchLastSection(True)
        vwidth = self.tableRet.verticalHeader().length()
        hwidth = self.tableRet.horizontalHeader().height()
        fwidth = self.tableRet.frameWidth() * 2
        self.tableRet.setFixedHeight(vwidth + hwidth + fwidth)
        vbox.addWidget(self.tableRet)

        self.buttonSrcView = QPushButton('view code')
        self.buttonSrcView.setFixedWidth(200)
        self.buttonSrcView.clicked.connect(self.openSourceViewer)
        self.buttonHide = QPushButton('Hide')
        self.buttonHide.setFixedWidth(200)
        self.buttonHide.clicked.connect(self.notifyHide)
        self.buttonHideAllMsg = QPushButton('Hide All')
        self.buttonHideAllMsg.setFixedWidth(200)
        self.buttonHideAllMsg.clicked.connect(self.hideAllMsgNamedAsSelected)
        self.groupBoxMessageInfo.setLayout(vbox)
        self.checkHideCircular = QCheckBox('Hide Circular Messages')
        self.checkHideCircular.setCheckState(QtCore.Qt.Unchecked)
        self.checkHideCircular.stateChanged.connect(self.changeHideCircularMessage)
        self.addWidget(self.checkHideCircular)
        self.addWidget(self.groupBoxMessageInfo)
        self.groupBoxMessageInfo.setSizePolicy(self.sizePolicy)

    def reset(self):
        for idx in reversed(range(0,self.listThread.count())):
            self.listThread.takeItem(idx)

    def setMsgInfoMessage(self,msg):
        self.strMessage = msg

    def changeHideCircularMessage(self,state):
        if state == QtCore.Qt.Unchecked:
            self.diagramView.hideCircularChanged(False)
        elif state == QtCore.Qt.Checked:
            self.diagramView.hideCircularChanged(True)
    
    def setMsgInfoModule(self,module):
        self.strModule = module

    def updateSearchStatus(self,curr,number):
        self.searchCursor.setText("%d/%d" % (curr,number))

    def connectSourceViewer(self,viewer):
        self.srcViewer = viewer

    def openSourceViewer(self):
        self.srcViewer.openViewer(self.strModule,self.strMessage)

    def setMessageInfoTime(self,begin,end,duration):
        self.tableTime.item(0,1).setText(begin)
        self.tableTime.item(1,1).setText(end)
        self.tableTime.item(2,1).setText(duration + ' msec')

    def setMessageInfoArg(self,listParam,listArg):
        if listArg:
            for idx, text in enumerate(listArg):
                self.tableArgs.item(idx,1).setText(text)
            for idx, text in enumerate(listParam):
                self.tableArgs.item(idx,0).setText(text)
        else:
            for idx in range(0,self.tableArgs.rowCount()):
                self.tableArgs.item(idx,1).setText('')
                self.tableArgs.item(idx,0).setText('')

    def setMessageInfoRet(self,listRet):
        if listRet:
            for idx, text in enumerate(listRet):
                self.tableRet.item(idx,1).setText(text)
        else:
            for idx in range(0,self.tableRet.rowCount()):
                self.tableRet.item(idx,1).setText('')
                self.tableRet.item(idx,0).setText('')

    def notifyInteractiveStateChanged(self,state):
        if const.mode_interactive != self.mode:
            return

        if const.STATE_INTERACTIVE_CAPTURING == state:
            self.buttonCapture.setEnabled(True)
            self.buttonCapture.setText('Stop Capture')
        if const.STATE_INTERACTIVE_PROCESSING == state:
            self.buttonCapture.setEnabled(False)
        if const.STATE_INTERACTIVE_IDLE == state:
            self.buttonCapture.setEnabled(True)
            self.buttonCapture.setText('Capture')
        if const.STATE_INTERACTIVE_RESET == state:
            self.buttonCapture.setEnabled(True)
            self.buttonCapture.setText('Capture')
        elif const.STATE_INTERACTIVE_ACTIVE == state:
            self.buttonCapture.setEnabled(True)
            self.buttonCapture.setText('Capture')

    def setMessageInfo(self,info):
        self.msgInfo.setText(info)

    def setAvailable(self,threads):
        self.sig.emit(threads)

    def toggleThreadDisplay(self,item):
        print(self.listThread.currentRow())
        #if item.isSelected():
        #    print(item.text() + "  is selected")
        #else:
        #    print(item.text() + "  is not selected")
        self.diagramView.showThread(self.listThread.currentRow(),item.isSelected())

    def hideAllMsgNamedAsSelected(self):
        self.diagramView.hideAllMessageSelected()

    def addThreadList(self,threads):

        if not self.groupBoxThreadInfo:
            self.groupBoxThreadInfo = QGroupBox()
            self.threadInfo = QLabel("Thread Info.")
            self.groupBoxThreadInfo.setStyleSheet("QGroupBox {border: 1px solid gray; border-radius: 9px; margin-top: 0.5em} QGroupBox::title {subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px;")

        if not self.threadvbox:
            self.threadvbox = QVBoxLayout()

        if not self.listThread:
            self.listThread = QListWidget()
            
        self.listThread.setFixedWidth(200)
        self.listThread.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        QtCore.QObject.connect(self.listThread, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.toggleThreadDisplay)
        self.threadvbox.addWidget(self.threadInfo)
        self.threadvbox.addWidget(self.listThread)
        self.groupBoxThreadInfo.setLayout(self.threadvbox)
        self.addWidget(self.groupBoxThreadInfo)
        self.groupBoxThreadInfo.setSizePolicy(self.sizePolicy)

        for id in threads:
            item = QtGui.QListWidgetItem(id)
            self.listThread.addItem(item)

    def connectController(self,controller):
        self.controller = controller
        self.connect(controller,QtCore.SIGNAL('setAvailable()'),self.setAvailable)
       
    def connectDiagramView(self,view):
        self.diagramView = view
 
    def disconnectMsgRcv(self,receiver):
        print("Implement this method !!! disconnectMsgRcv")

    def connectMsgRcv(self,receiver):
        self.msgRcv.append(receiver)

    def notifyHide(self):
        for rcv in self.msgRcv:
            rcv.activateHide(True)

    def showHiddenLifelines(self):
        response, selected_items = HiddenDialog.HiddenDialog.getSelectedItems(self.diagramView.getHiddenLifeLines())
        if response:
            self.diagramView.showLifelines(selected_items)

    def showHiddenMessages(self):
        response, selected_items = HiddenMessageDialog.HiddenMessageDialog.getSelectedItems(self.diagramView.getHiddenMessages(),self.diagramView.getHiddenLifeLines())
        if response:
            if selected_items[3] in self.diagramView.getHiddenLifeLines():
                confirmation = ShowLifeLineDialog.ShowLifeLineDialog.confirmToShowLifeLine(selected_items[3])
                if confirmation:
                    self.diagramView.showLifelines([selected_items[3]])
                    self.diagramView.showMessages(selected_items)
            else:
                self.diagramView.showMessages(selected_items)

    def notifyCapture(self):
        for rcv in self.msgRcv:
            rcv.activateCapture(True)
    
    def moveToPrev(self):
        for rcv in self.msgRcv:
            rcv.moveToPrev()
        
    def moveToNext(self):
        for rcv in self.msgRcv:
            rcv.moveToNext()

    def searchMsg(self):
        str = self.editTextSearch.toPlainText()
        for rcv in self.msgRcv:
            rcv.searchMessage(str)
