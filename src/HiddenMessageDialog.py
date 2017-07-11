from PySide.QtGui import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit, QListWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QFont, QBrush, QColor
from PySide import QtGui, QtCore
import Lifeline

class HiddenMessageDialog(QDialog):
   
    msgList = None 
    lifelineList = None
    

    def __init__(self, messages, hiddenLifelines, parent = None):
        super(HiddenMessageDialog, self).__init__(parent)

        self.lifelineList = hiddenLifelines
        self.msgList = messages
        layout = QVBoxLayout(self)

        listTitle = QLabel('Hidden Messages')
        layout.addWidget(listTitle)

        self.listHiddenMessages = QtGui.QTableWidget(len(self.msgList),4)
        self.listHiddenMessages.setHorizontalHeaderLabels(['Index','Name','Departure','Destination'])
        self.listHiddenMessages.setFixedWidth(400)
        #self.listHiddenMessages.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.listHiddenMessages.setSelectionBehavior(QAbstractItemView.SelectRows)

        for idx, msg in enumerate(self.msgList):
            self.listHiddenMessages.setItem(idx,0,QTableWidgetItem("%d" % msg['messageindex']))
            self.listHiddenMessages.setItem(idx,1,QTableWidgetItem(msg['message']))
            item = QTableWidgetItem(msg['departure']['class'])
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            if msg['departure']['class'] in self.lifelineList:
                item.setForeground(QColor(200,200,200)) 
            self.listHiddenMessages.setItem(idx,2,item)

            item = QTableWidgetItem(msg['dest'])
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            if msg['dest'] in self.lifelineList:
                item.setForeground(QColor(200,200,200)) 
            self.listHiddenMessages.setItem(idx,3,item)

        layout.addWidget(self.listHiddenMessages)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        buttons.button(QDialogButtonBox.Ok).setText('Show')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def getSelectedItems(msgList, parent = None):
        dialog = HiddenMessageDialog(msgList,parent)
        result = dialog.exec_()
        return (result, [x.text() for x in dialog.listHiddenMessages.selectedItems()])

