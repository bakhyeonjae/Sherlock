from PySide.QtGui import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit, QListWidget
from PySide import QtGui, QtCore

class ShowLifeLineDialog(QDialog):
   
    theHidden = None 

    def __init__(self, hiddenLifeline, parent = None):
        super(ShowLifeLineDialog, self).__init__(parent)

        self.theHidden = hiddenLifeline
        layout = QVBoxLayout(self)

        listTitle = QLabel("The message you want to see is blocked by a hidden class object.\n\n%s\n\nDo you want to show the hidden class object?" % hiddenLifeline)
        layout.addWidget(listTitle)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        buttons.button(QDialogButtonBox.Ok).setText('Yes')
        buttons.button(QDialogButtonBox.Cancel).setText('No')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def confirmToShowLifeLine(theHidden, parent = None):
        dialog = ShowLifeLineDialog(theHidden,parent)
        result = dialog.exec_()
        return result

