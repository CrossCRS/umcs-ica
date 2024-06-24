from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
import pandas as pd
import numpy as np
import mne
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from ui.Ui_MainWindow import Ui_MainWindow
from ui.Ui_OpenDialog import Ui_OpenDialog
from ui.Ui_ComponentDialog import Ui_ComponentDialog

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

        data = pd.read_csv(fileName[0], skiprows=int(self.sbSkipRows.text()), delimiter=self.leSeparator.text())
        n_channels = data.shape[1]
        n_samples = data.shape[0]

        if n_channels < 2:
            QMessageBox.critical(self, "Błąd", "Dane muszą zawierać przynajmniej 2 kanały")
            return

        if n_samples < 1:
            QMessageBox.critical(self, "Błąd", "Dane nie zawierają próbek")
            return

        self.lineEdit.setText(fileName[0])

        self.lblSampleCountValue.setText(str(n_samples))
        self.lblChannelsValue.setText(str(n_channels))
        self.sbFirstChannel.setMaximum(n_channels)
        self.sbFirstChannel.setValue(0)
        self.sbLastChannel.setMaximum(n_channels)
        self.sbLastChannel.setValue(n_channels)
        self.sbSkipRows.setMaximum(n_samples)

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

    def accept(self):
        if not self.lineEdit.text():
            return

        if self.sbFirstChannel.value() >= self.sbLastChannel.value():
            QMessageBox.critical(self, "Błąd", "Pierwszy kanał musi być mniejszy od ostatniego")
            return

        if self.sbLastChannel.value() - self.sbFirstChannel.value() < 2:
            QMessageBox.critical(self, "Błąd", "Muszą być wybrane przynajmniej 2 kanały")
            return

        super().accept()

class ComponentDialog(QDialog, Ui_ComponentDialog):
    def __init__(self, sources):
        super().__init__()
        self.setupUi(self)

        # Setup plot
        fig, axs = plt.subplots(len(sources), 1, figsize=(12, 6))

        for i, source in enumerate(sources):
            axs[i].plot(source)
            axs[i].set_title(f'Komponent {i}')

        plt.tight_layout()

        for i in reversed(range(self.layoutPlot.count())):
            self.layoutPlot.itemAt(i).widget().setParent(None)

        self.layoutPlot.addWidget(FigureCanvas(fig))

        # Setup checkboxes
        self.checkbox_group = QButtonGroup(self)
        self.checkbox_group.setExclusive(False)

        self.checkboxes = []

        for i in range(len(sources)):
            checkbox = QCheckBox(f"Komponent {i}")
            self.layoutCheckboxes.addWidget(checkbox)
            self.checkbox_group.addButton(checkbox)
            self.checkboxes.append(checkbox)

    def accept(self):
        super().accept()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.bOpen.clicked.connect(self.openDialog)
        self.bICA.clicked.connect(self.performICA)
        self.bApply.clicked.connect(self.applyICA)

        self.bICA.setEnabled(False)
        self.bApply.setEnabled(False)

    def openDialog(self):
        dialog = OpenDialog()

        if dialog.exec():
            path = dialog.lineEdit.text()
            data = pd.read_csv(path, skiprows=dialog.sbSkipRows.value(), delimiter=dialog.leSeparator.text())
            data = data.iloc[:, dialog.sbFirstChannel.value():dialog.sbLastChannel.value()].to_numpy()

            self.n_channels = data.shape[1]
            self.n_samples = data.shape[0]

            self.channel_names = []
            for i in range(self.n_channels):
                self.channel_names.append(f"CH{i}")

            self.info = mne.create_info(ch_names=self.channel_names, sfreq=1, ch_types='eeg')
            self.raw = mne.io.RawArray(data.transpose(), self.info)

            self.raw_plot = self.raw.plot(title=f"Sygnał", block=False, show=False, duration=self.n_samples / self.info['sfreq'], scalings='auto')

            for i in reversed(range(self.layoutPlot.count())):
                self.layoutPlot.itemAt(i).widget().setParent(None)

            self.layoutPlot.addWidget(self.raw_plot.canvas)

            self.bOpen.setEnabled(False)
            self.bICA.setEnabled(True)

    def performICA(self):
        self.n_components = 0
        if self.n_channels < 8:
            self.n_components = self.n_channels
        else:
            self.n_components = self.n_channels * 0.40

        self.ica = mne.preprocessing.ICA(n_components=self.n_components, random_state=97, max_iter=800)
        self.ica.fit(self.raw)

        sources = self.ica.get_sources(self.raw).get_data()
        dialog = ComponentDialog(sources)

        if dialog.exec():
            self.ica.exclude = [i for i, checkbox in enumerate(dialog.checkboxes) if checkbox.isChecked()]
            self.bICA.setEnabled(False)
            self.bApply.setEnabled(True)

    def applyICA(self):
        pass

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
