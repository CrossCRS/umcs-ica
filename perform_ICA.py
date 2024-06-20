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

import pandas as pd
import numpy as np
import mne
import matplotlib.pyplot as plt

#narazie kod na brudno zeby sprawdzic czy wszystko dziala

#wszystko trzeba przerzucic do jupiter noteboook zeby plots dzialaly jak nalezy i zeby dalo sie kolaborowac

#pojawia sie ekranik na ktorym trzeba podac sciezke do pliku sygnalu 

path = "Dane/emg_2_56_57.csv"
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
raw.plot(title=f"Sygnał + {file_name}", block=True)



#wykonanie analizy niezaleznych skladowych
ica = mne.preprocessing.ICA(n_components=None, random_state=97, max_iter=800)
ica.fit(raw)

#wyplotowanie komponentow jako oscylogramow i zapisanie do tablicy sources
sources = ica.get_sources(raw).get_data()
plt.figure(figsize=(12, 6))
for i, source in enumerate(sources):
    plt.subplot(len(sources), 1, i+1)
    plt.plot(source)
    plt.title(f'Komponent {i+1}')
plt.tight_layout()
plt.show()
exit()
#sources to tablica w ktorej znajduja sie znalezione komponenty. na ekraniku wyswietlaja sie komponenty jakie odnalazlo 
#do przejrzenia, pod nim wyswietlaja sie dwa przyciski "apply to whole signal", "choose signal fragment", 
#po nacisnieciu "choose signal fragment" pojawia sie ekranik na ktorym mozna zaznaczyc fragment oscylogramu, po zaznaczeniu i
#nacisnieciu "save" wycina ten fragment sygnalu i przechodzi na kolejny ekranik gdzie widac wyciety sygnal i znow komponenty 
#(wygladajacy jak ten wczesniejszy) + miejsce na wpisanie numerow komponentow ktore chcemy usunac (one zapisuja sie w postaci 
#tablicy "komponenty wybrane"):

komponenty_wybrane = 0 #to dostajemy z indexu pierwszego wymiaru sources
ica.exclude = [komponenty_wybrane]
cleaned_fragment = ica.apply(raw.copy()) 

#zapisanie do pliku (podanie sciezki do pliku wyswietla  sie w kolejnym lub tym samym okienku)
output_file = ""
df = pd.DataFrame(cleaned_fragment.get_data().transpose()) #chyba? odwracam transpozycje w ten sposob??? 
df.to_csv(output_file, sep=';')