# Lokalne ślady GPX

Stan 6 XI 2026: 7 z 8 tras ma lokalny GPX. Vouni Panagias 9,8 km pozostaje nieprzygotowane: dostępna relacja OSM jest nieciągła i nie potwierdza właściwego wariantu. Timi terenowe 12 km także nie ma potwierdzonego śladu. Pełne oficjalne GPX rowerowe pozostają odnośnikami zewnętrznymi; warunki Visit Cyprus wymagają uprzedniej pisemnej zgody na redystrybucję (https://www.visitcyprus.com/uncategorised/terms-of-use/).

Geometria piesza: © OpenStreetMap contributors, ODbL 1.0, https://opendatacommons.org/licenses/odbl/1-0/ . Osobna baza pochodna: `sources/osm-network.json`. Zawiera współrzędne oryginalnych węzłów, krawędzie ways, kolejność marszu, wersje relacji, datę odczytu, adresy i SHA-256 pobranych źródeł. Oferujemy ją na tej samej licencji. Pełny tekst licencji: `sources/ODbL-1.0.txt`.

To eksport mapowanych ścieżek OSM, bez interpolacji, automatycznie wyznaczanej trasy ani syntetycznych łączników. Nie jest zapisem nowego przejścia w terenie. Każda kolejna para węzłów musi być krawędzią udokumentowanej drogi źródłowej. Skrypt `_src/route_sources.py` odtwarza pliki, a build porównuje wszystkie współrzędne i ich kolejność z bazą oraz sprawdza geometrię. Dopuszczone powroty po tym samym odcinku (Aphrodite, Pouziaris, Pissouromoutti, Doxa) i rzadsze węzły źródła opisano indywidualnie w bazie; nie dodano sztucznych punktów, aby przejść test.

Warianty porównano z mapami zarządcy: https://www.visitcyprus.com/wp-content/uploads/2023/09/hiking_WEB_ONLY.pdf (s. 19–22, 30–31 i 35) i https://www.visitcyprus.com/wp-content/uploads/2026/03/Hiking-Map-Nature-Trails.pdf (sieć Madari). Nie kopiujemy tych map do paczki.

Dystanse GPX różnią się od nominalnych wartości opisowych; oba pomiary są jawne na kartach. Złączenia kombinacji są rzeczywistymi wspólnymi węzłami OSM. Start Aphrodite obejmuje mapowane dojście 280 m w obie strony; Aphrodite + Adonis biegnie zewnętrznymi odcinkami przez Moutti tis Sotiras i Kefalovrysia. Smigies long + Pissouromoutti obejmuje łącznik przy picnic site oraz odnogę szczytową w obie strony. Madari obejmuje Doxa–punkt obserwacyjny w obie strony i pętlę Teisia, bez krótkiej dodatkowej odnogi widokowej.

Nie dołączono wysokości ani obliczonych podejść: brak wiarygodnego profilu wysokościowego. GPX, baza źródłowa i licencja należą do podstawowego zapisu offline; kafelki map nie są pobierane. Sprawdzenie GPX nie potwierdza otwarcia szlaku ani aktualnego stanu terenu.
