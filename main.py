from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
import pandas as pd

from ui.Ui_MainWindow import Ui_MainWindow
from ui.Ui_OpenDialog import Ui_OpenDialog

class OpenDialog(QDialog, Ui_OpenDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.bBrowse.clicked.connect(self.browse)

    def browse(self):
        fileName = QFileDialog.getOpenFileName(self, "Wybierz plik z danymi", ".", "Pliki .csv (*.csv)")
        if not fileName[0]:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            return
        
        self.lineEdit.setText(fileName[0])

        data = pd.read_csv(self.lineEdit.text(), skiprows=int(self.sbSkipRows.text()), delimiter=self.leSeparator.text())
        n_channels = data.shape[1]
        n_samples = data.shape[0]

        self.lblSampleCountValue.setText(str(n_samples))
        self.lblChannelsValue.setText(str(n_channels))
        self.sbFirstChannel.setMaximum(n_channels)
        self.sbFirstChannel.setValue(0)
        self.sbLastChannel.setMaximum(n_channels)
        self.sbLastChannel.setValue(n_channels)
        self.sbSkipRows.setMaximum(n_samples)

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.bOpen.clicked.connect(self.openDialog)

    def openDialog(self):
        dialog = OpenDialog()
        
        if dialog.exec():
            print(dialog.lineEdit.text())

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()