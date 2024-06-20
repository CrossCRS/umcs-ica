from PyQt6.QtWidgets import *
import pandas as pd
import numpy as np
import mne
import matplotlib.pyplot as plt

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

path = "Dane/dzwiek_czas_2_44100_158590.csv"
file_name = ""

data = pd.read_csv(path, skiprows=0, delimiter=";")
n_channels = data.shape[1]

#wskazanie ilosci probek 
n_samples = data.shape[0]

channel_names = []
for i in range(n_channels):
    channel_names.append(f"CH{i}")

info = mne.create_info(ch_names=channel_names, sfreq=1) #nadaje probkowanie 1:1 przez co nie ma znaczenia jakie probkowanie
                                                       #ma sygnal i kod staje sie uniwersalny (os czasu jest w czestotli-
                                                       #wosci probek)

raw = mne.io.RawArray(data.transpose(), info) #oczekuje channels as rows, w plikach jest channels as columns stad transpose


#wyswietlanie sygnalu w pierwotnej formie oscylogramu
fig = raw.plot(title=f"Sygnał + {file_name}", show=False)

layout.addWidget(fig.canvas)

# layout.addWidget(QPushButton('Top'))
layout.addWidget(QPushButton('Bottom'))
window.setLayout(layout)
window.show()
app.exec()