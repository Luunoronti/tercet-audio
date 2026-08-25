# TERCET

Trzyczęściowy, w pełni analogowy lampowy tor audio DIY — trzy urządzenia
w spójnej serii (drewno + lustrzana stal nierdzewna + żarzenie lamp):

1. **`riaa/`** — przedwzmacniacz gramofonowy RIAA (stereo).
   2× ECC83 + ECC82 (wtórnik katodowy), pasywna korekcja 3180/318/75 µs,
   B+ rozdzielone per kanał, dławik w filtrze, automatyczne rozładowanie
   kondensatorów, wyciszanie wyjść z opóźnieniem, ground breaker GND/PE.
   **Stan: schemat rev E — gotowy do budowy.**
2. **`power-amp/`** — lampowa końcówka mocy z regulacją głośności
   i analogowymi wskaźnikami wychyłowymi. *Stan: planowanie.*
3. **`preamp/`** — przedwzmacniacz liniowy: selektor wejść, głośność,
   balans, mono, filtry, barwa. *Stan: planowanie.*

Pozostałe katalogi: **`common/`** — bloki współdzielone między urządzeniami
(żarzenie DC z LD1085, automatyka rozładowania/mute), **`enclosure/`** —
pliki obudów (DXF płyt pod cięcie laserowe, grawer frontów),
**`docs/`** — dokument ustaleń projektu (`PROJEKT-RIAA.md` = "pamięć"
projektu; przy pracy z AI podawać ten plik na starcie sesji).

## Jak pracujemy z plikami KiCada

Schematy są **generowane skryptem**: `riaa/gen.py` (+ `symlib.py`) buduje
`riaa_preamp.kicad_sch` od zera, z symbolami osadzonymi w pliku (otwiera się
w KiCadzie 7+ bez zewnętrznych bibliotek). Weryfikacja: `check.py` eksportuje
netlistę przez `kicad-cli` i sprawdza ~60 asercji połączeń (w tym rozdział
masy sygnałowej od PE i separację kanałów).

```
cd riaa
python3 gen.py
kicad-cli sch export netlist -o riaa.net riaa_preamp.kicad_sch
python3 check.py
kicad-cli sch export pdf -o riaa_preamp.pdf riaa_preamp.kicad_sch
```

Zmiany koncepcyjne robimy w `gen.py` i regenerujemy; drobne poprawki ręczne
w Eeschema są OK, ale wtedy plik `.kicad_sch` staje się źródłem prawdy —
odnotować w commicie. Etap PCB: planowany interaktywnie przez wtyczkę
Konnect (KiCad 10 + MCP).

## Bezpieczeństwo

W urządzeniach występują napięcia do ~330 V DC — śmiertelnie niebezpieczne.
Zasady (PE, ground breaker, rozładowanie, pomiar przed pracą) opisane
w `docs/PROJEKT-RIAA.md` i na schematach. Budujesz na własną
odpowiedzialność.
