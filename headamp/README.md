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
- `sim/amp.cir` — pełny tor (driver + końcówka + OPT), .op / .ac / THD
- `sim/crossfeed.cir` — sieć crossfeedu S1
- `ref/se_el84.svg`, `ref/crossfeed.svg` — schematy poglądowe (schemdraw);
  docelowo generator `gen.py` jak w `riaa/` — TODO

## Uruchomienie symulacji
```
cd headamp/sim
ngspice -b amp.cir
ngspice -b crossfeed.cir
```
