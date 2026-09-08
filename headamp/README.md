# headamp — lampowy wzmacniacz słuchawkowy (SE EL84)

Czwarte urządzenie serii (poza kanonicznym "tercetem"): biurkowy wzmacniacz
słuchawkowy pod Beyerdynamic DT 770 M (80 Ω), źródło: DAC (E-MU 0202 USB,
wyjście liniowe). W torze sygnałowym wyłącznie lampy i transformatory.

**Topologia (na kanał):** ½ ECC82 (wspólna katoda) → RC → EL84 w triodzie
(g2→a przez 100R) → transformator SE 5k:80 Ω. Bez globalnego NFB.
B+ ~300 V (CLC), żarzenie DC + elewacja +50 V — blok wspólny, patrz
`common/` (LD1085, identyczny jak w RIAA).

**Przełączniki charakteru (oba czysto pasywne):**
- **S1 (DPDT)** — crossfeed między DAC a potencjometrem: bas −14 dB do
  przeciwnego kanału, wygasa >~700 Hz; scena "z kolumn".
- **S2 (DPST)** — "wokal do przodu": odłącza C2b 100µ przy katodzie drivera
  (zostaje 1µ) → półka −3 dB poniżej ~200 Hz.

**Wyniki symulacji** (ngspice, modele Korena; `sim/`):
wzmocnienie 24,7 dB @1 kHz; pasmo −3 dB: 24 Hz…>100 kHz (dół ograniczony
Lp OPT=15 H — zamówić ≥25 H); Zout ~36 Ω; THD @0,6 Vrms: 0,20%
(niemal czysta H2, H3 −87 dB); EL84: 285 V / 29 mA (8,2 W).

Szczegóły i log decyzji: `docs/PROJEKT-HEADAMP.md`.

## Pliki
- `gen.py` — generator schematu KiCad (`headamp.kicad_sch`); **źródło
  prawdy jest w tym pliku, NIE edytować schematu ręcznie w Eeschema**
  (regeneracja go nadpisze). UUID deterministyczne (uuid5) — dwa
  uruchomienia dają identyczny plik. Layout w ramkach modułów (WEJŚCIE,
  KANAŁ L, KANAŁ P, WYJŚCIE, SIEĆ, ZASILACZ B+, ŻARZENIE); połączenia
  między modułami drutami (nie global_label), poza ELEV (etykieta
  lokalna, tam gdzie łączy dzielnik elewacji z blokiem żarzenia) i GND/PE
  (symbole power). Żarniki lamp (ECC82 U1 unit3, EL84 U2/U202 unit2)
  narysowane wewnątrz ramki ŻARZENIE, połączone drutami z wyjściem
  LD1085 i z minusem żarzenia (= ELEV).
- `symlib.py` — parser symboli KiCad (kopia `riaa/symlib.py`, inna
  ścieżka domyślna biblioteki: Windows).
- `check.py` — asercje netlisty (wzór `riaa/check.py`): kanał L, kanał
  P (funkcja `chan()` parametryzowana referencjami), zasilacz, crossfeed
  S1, gniazda WE/WY.
- `sim/amp.cir` — pełny tor (driver + końcówka + OPT), .op / .ac / THD
- `sim/crossfeed.cir` — sieć crossfeedu S1, wariant "ON" (bez przełącznika,
  same wartości R/C) - historyczny, poprzednik `crossfeed_sw.cir`.
- `sim/crossfeed_sw.cir` — **źródło prawdy** dla topologii narysowanej w
  `gen.py` (SW401 na WYJŚCIU galęzi krzyżowej, DECYZJA 2026-09-08 - patrz
  docs/PROJEKT-HEADAMP.md). Trzy warianty w jednym pliku (ngspice batch,
  kolejne `.end`): 1) ON (krzyżowy załączony), 2) OFF nowa topologia
  (S1 na wyjściu - odłącza całą galąź krzyżową od wyjść), 3) OFF stara
  topologia (S1 na wejściu, ODRZUCONA - R405/R406+C403/C404 nadal
  obciążają wyjścia, ugięcie basu ~1,4 dB - uzasadnienie zmiany).
- `ref/se_el84.svg`, `ref/crossfeed.svg` — schematy poglądowe (schemdraw,
  historyczne, przed generatorem)
- `layout/layout_top.py` — generator (matplotlib, bez KiCada) propozycji
  **rozmieszczenia elementów w obudowie** (rzut z góry, 260×200 mm, skala
  1:1 — zmniejszone 2026-09-08 z pierwotnych 300×250, patrz
  docs/PROJEKT-HEADAMP.md) → `ref/layout_top.svg`/`.png`. Zasilacz na
  chassis (górnej płycie) tylko jako bryły T301/L1/J1+F1/SW1/NE1; reszta
  zasilacza na **PCB** (DECYZJA, nie powietrznie — patrz
  docs/PROJEKT-HEADAMP.md) w zarezerwowanej strefie pod płytą. Montaż
  powietrzny toru audio: listwy lutownicze + elementy na nóżkach
  podstawek lamp — szczegółowy przydział w `ref/layout_bom_montaz.md`.
- `ref/layout_bom_montaz.md` — tabela przydziału elementów toru audio:
  na nóżkach podstawek lamp vs listwy lutownicze A/B_L/B_P/D, z numerami
  pinów (ECC82/EL84) i uzasadnieniem.

## Workflow (regeneracja schematu)
```
python headamp/gen.py
kicad-cli sch export netlist --format kicadsexpr -o headamp/headamp.net headamp/headamp.kicad_sch
python headamp/check.py
kicad-cli sch erc --format json --severity-all -o erc.json headamp/headamp.kicad_sch
```
Oczekiwane: check.py OK; **ERC = 0 błędów, 0 ostrzeżeń**. Szczegóły i
log decyzji: docs/PROJEKT-HEADAMP.md.

## Uruchomienie symulacji
```
cd headamp/sim
ngspice -b amp.cir
ngspice -b crossfeed_sw.cir
```
