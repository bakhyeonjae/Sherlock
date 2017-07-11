from PySide.QtGui import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit, QListWidget
from PySide import QtGui, QtCore

class HiddenDialog(QDialog):
   
    lifelines = None 

    def __init__(self, hiddenLifeline, parent = None):
        super(HiddenDialog, self).__init__(parent)

        self.lifelines = hiddenLifeline
        layout = QVBoxLayout(self)

        listTitle = QLabel('Hidden Life-lines')
        layout.addWidget(listTitle)

        self.listHiddenLifelines = QListWidget()
        self.listHiddenLifelines.setFixedWidth(400)
        self.listHiddenLifelines.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

        for text in self.lifelines:
            item = QtGui.QListWidgetItem(text)
            self.listHiddenLifelines.addItem(item)

        layout.addWidget(self.listHiddenLifelines)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        buttons.button(QDialogButtonBox.Ok).setText('Show')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def getSelectedItems(lifelines, parent = None):
        dialog = HiddenDialog(lifelines,parent)
        result = dialog.exec_()
        return (result, [str(x.text()) for x in dialog.listHiddenLifelines.selectedItems()])

