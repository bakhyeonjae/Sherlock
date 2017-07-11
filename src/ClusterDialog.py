from PySide.QtGui import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit
from PySide import QtGui, QtCore

import Lifeline

class ClusterDialog(QDialog):
    
    editClusterName = None
    def __init__(self, lifeline, defaultName, parent = None):
        super(ClusterDialog, self).__init__(parent)

        self.lifeline = lifeline
        layout = QVBoxLayout(self)

        message = QLabel('Enter group name')
        layout.addWidget(message)

        self.editClusterName = QLineEdit(defaultName)
        self.editClusterName.setFixedHeight(30)
        self.editClusterName.setFixedWidth(400)
        self.editClusterName.textChanged.connect(self.validateCluster)
        layout.addWidget(self.editClusterName)

        self.validation_msg = QLabel(' ')
        layout.addWidget(self.validation_msg)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.validateCluster()

    def validateCluster(self):
        cnt = 0
        for l in self.lifeline:
            if self.editClusterName.text() in l.getClassName() and not l.getFlagCluster() and not l.getClusterLifeline():
                cnt += 1

        available_flag = True
        for l in self.lifeline:
            if self.editClusterName.text() in l.getClassName() and l.getFlagCluster():
                available_flag = False
                break

        if available_flag:
            self.validation_msg.setText("group name includes %d life-lines" % (cnt))
        else:
            self.validation_msg.setText("group name is not available")

    def getClusterText(self):
        return self.editClusterName.text()
    
    @staticmethod
    def getClusterName(lifelines, defaultName, parent = None):
        dialog = ClusterDialog(lifelines,defaultName,parent)
        result = dialog.exec_()
        return (result, dialog.getClusterText())

         
