# 8. ICA
# * Wczytanie pliku sygnału
# * Wskazanie parametrów sygnału (liczba próbek, próbkowanie)
# * Wyświetlenie sygnału w postaci oscylogramu
# * Wykonanie analizy niezależnych składowych
# * Wyświetlenie odnalezionych komponentów w postaci oscylogramu
# * Usunięcie z sygnału wskazanego komponentu
# * Zapisanie wynikowych komponentów do pliku .csv
# 9. ICA na bogato (praca dla dwóch osób)
# * Program w wersji 8 rozbudowany o wskazywanie fragmentów, z których chcemy usuwać
# komponent
# Wartości dla kolejnych kanałów sygnału w plikach .csv rozdzielane są średnikiem. Kolejne próbki są
# w nowych liniach. Dla jednokanałowego sygnału wszystkie wartości znajdują się w jednej kolumnie.

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
from ui.Ui_HelpDialog import Ui_HelpDialog

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

class HelpDialog(QDialog, Ui_HelpDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.bOpen.clicked.connect(self.openDialog)
        self.bExport.clicked.connect(self.export)
        self.bICA.clicked.connect(self.performICA)
        self.bApply.clicked.connect(self.applyICA)
        self.bHelp.clicked.connect(self.showHelp)

        self.bICA.setEnabled(False)
        self.bApply.setEnabled(False)

    def replacePlot(self, fig):
        for i in reversed(range(self.layoutPlot.count())):
            self.layoutPlot.itemAt(i).widget().setParent(None)

        self.layoutPlot.addWidget(fig)

    def showHelp(self):
        HelpDialog().exec()

    def export(self):
        fileName = QFileDialog.getSaveFileName(self, "Zapisz sygnał", ".", "Pliki .csv (*.csv)")
        if not fileName[0]:
            return
        
        df = pd.DataFrame(self.new_raw.get_data().transpose())
        df.to_csv(fileName[0], sep=';', header=False, index=False)

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
            self.raw_plot.fake_keypress('a')
            self.raw_plot.mne.fig_annotation._add_description("Wybrane")

            self.replacePlot(self.raw_plot)

            self.bOpen.setEnabled(False)
            self.bICA.setEnabled(True)

    def performICA(self):
        # TODO: Add dialog for selecting number of components manually?
        self.n_components = 0
        if self.n_channels < 8:
            self.n_components = self.n_channels
        else:
            self.n_components = self.n_channels * 0.40

        self.ica = mne.preprocessing.ICA(n_components=self.n_components, max_iter="auto")
        self.ica.fit(self.raw)

        sources = self.ica.get_sources(self.raw).get_data()
        dialog = ComponentDialog(sources)

        if dialog.exec():
            self.ica.exclude = [i for i, checkbox in enumerate(dialog.checkboxes) if checkbox.isChecked()]
            self.bICA.setEnabled(False)
            self.bApply.setEnabled(True)

    def applyICA(self):
        self.bApply.setEnabled(False)

        if self.raw.annotations:
            # Select only annotated segments
            data_segments = []

            for annot in self.raw.annotations:
                start = annot['onset']
                stop = start + annot['duration']
                
                start_sample, stop_sample = self.raw.time_as_index([start, stop])
                
                data, _ = self.raw[:, start_sample:stop_sample]
                
                data_segments.append(data)

            concatenated_data = np.concatenate(data_segments, axis=1)

            self.new_raw = mne.io.RawArray(concatenated_data, self.raw.info)
            self.new_raw = self.ica.apply(self.new_raw)
        else:
            # Apply to the whole data
            self.new_raw = self.ica.apply(self.raw.copy())

        self.new_raw_plot = self.new_raw.plot(title=f"Sygnał po ICA", block=False, show=False, duration=self.new_raw.get_data().shape[1] / self.info['sfreq'], scalings='auto')
        self.replacePlot(self.new_raw_plot)

        self.bExport.setEnabled(True)

def main():
    mne.viz.set_browser_backend("pyqtgraph")

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
