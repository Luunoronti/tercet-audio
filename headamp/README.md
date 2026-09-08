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
  między modułami drutami (nie global_label), poza HEAT_A/HEAT_B/ELEV
  (etykiety lokalne) i GND/PE (symbole power).
- `symlib.py` — parser symboli KiCad (kopia `riaa/symlib.py`, inna
  ścieżka domyślna biblioteki: Windows).
- `check.py` — asercje netlisty (wzór `riaa/check.py`): kanał L, kanał
  P (funkcja `chan()` parametryzowana referencjami), zasilacz, crossfeed
  S1, gniazda WE/WY.
- `sim/amp.cir` — pełny tor (driver + końcówka + OPT), .op / .ac / THD
- `sim/crossfeed.cir` — sieć crossfeedu S1 (**źródło prawdy** dla
  topologii narysowanej w `gen.py` - SW401 + R401-R406 + C401-C404)
- `ref/se_el84.svg`, `ref/crossfeed.svg` — schematy poglądowe (schemdraw,
  historyczne, przed generatorem)

## Workflow (regeneracja schematu)
```
python headamp/gen.py
kicad-cli sch export netlist --format kicadsexpr -o headamp/headamp.net headamp/headamp.kicad_sch
python headamp/check.py
kicad-cli sch erc --format json --severity-all -o erc.json headamp/headamp.kicad_sch
```
Oczekiwane po Etapie 6: check.py OK; ERC ostrzeżenia: `missing_unit` ×3
(U1/U2/U202 - unity grzania nie są rysowane, DECYZJA) + `multiple_net_names`
ELEV/HEAT_B (zamierzone, jak w common/riaa); **plus 3 błędy
`missing_power_pin`** (też U1/U2/U202 - piny grzania typu `power_in` w
bibliotece Valve, KiCad flaguje to jako error nawet gdy unit po prostu
nie jest umieszczony; nie da się obniżyć bez zmiany `headamp.kicad_pro`,
poza zakresem generatora). Szczegóły i status decyzji:
docs/PROJEKT-HEADAMP.md.

## Uruchomienie symulacji
```
cd headamp/sim
ngspice -b amp.cir
ngspice -b crossfeed.cir
```
