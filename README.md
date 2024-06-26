# ICA

ICA z możliwością wybierania fragmentów sygnału poprzez zaznaczanie na wykresie.

```
pip install -r requirements.txt
python main.py
```

Naciśnięcie przycisku **Importuj dane** otwiera okno dialogowe pozwalające na wczytanie danych. Dane powinny być zapisane w pliku CSV gdzie każdy kanał to oddzielna kolumna. Program pozwala na pomijanie wierszy, wczytywanie wybranych kolumn oraz wybór separatora. Po wczytaniu danych wyświetlane one są w głównym oknie.

Następnie możliwe jest przeprowadzenie analizy niezależnych składowych poprzez naciśnięcie przycisku **Przeprowadź ICA**. Po wykonaniu analizy w nowym okienku wyświetlane są odnalezione komponenty. Wybieramy komponenty które chcemy usunąć zaznaczając odpowiednie checkboxy.

Po wybraniu komponentów samo usuwanie przeprowadzane jest po naciśnięciu przycisku **Zaaplikuj ICA**. ICA możemy zaaplikować dla całego sygnału lub wybranych fragmentów, w tym celu zaznaczamy je przeciągając myszką po oscylogramie w głównym okienku programu.

Odseparowane sygnały możemy zapisać do pliku CSV używając przycisku **Eksportuj dane**.