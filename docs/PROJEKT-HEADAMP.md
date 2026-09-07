# PROJEKT-HEADAMP — pamięć projektu wzmacniacza słuchawkowego

Dokument ustaleń, analogicznie do PROJEKT-RIAA.md. Przy pracy z AI podawać
ten plik na starcie sesji.

## Kontekst i wymagania
- Słuchawki: **Beyerdynamic DT 770 M** (80 Ω) — wybrane za najsilniejsze
  pasywne tłumienie hałasu wśród nausznych (~35 dBA); jeszcze nie kupione.
- Źródło: komputer w pracy → **E-MU 0202 USB** jako DAC (wyjście liniowe;
  sekcja słuchawkowa 0202 nieużywana — 22 Ω wyjścia, 16 mW).
  Odtwarzanie: lossless, tryb WASAPI Exclusive/ASIO, głośność 100%.
- Cel brzmieniowy: **lampowe ciepło** (dominacja H2), **dobra scena**,
  **wyraźny wokal** (możliwość uwypuklenia).
- Wymóg: w torze audio **zero półprzewodników** (krzem tylko w zasilaczu).
- Docelowo praca na biurku; bezpieczeństwo jak w RIAA (~300 V!).

## Topologia (DECYZJA)
Na kanał: ½ ECC82 wspólna katoda → sprzężenie RC → EL84 w trybie triodowym
(g2→anoda przez 100R) → transformator wyjściowy SE 5k:80 Ω.
- Odrzucone: OTL (Zout za wysokie przy 80 Ω), hybryda lampa+MOSFET
  (półprzewodnik w torze), White follower (projekt "na później").
- **Bez globalnego NFB** — świadomie: pełny profil H2, brak ryzyka
  niestabilności z OPT w pętli. Opcja na przyszłość: przełączane ~6 dB
  (Zout →~16 Ω, THD /2, gain −6 dB).

## Wartości (punkt startowy, zweryfikowany symulacją)
Driver: Ra 47k/2W, Rk 1k5 + C 100µ (patrz S2), grid leak 470k, stopper 1k,
odsprzęganie B+ drivera 10k/2W + 47µ/350V. Sprzężenie 100n/400V, grid leak
EL84 470k, stopper 1k. EL84: Rk 270R/5W + 470µ/25V, zwora g2 100R.
OPT: SE 5k:80, szczelina, ≥45 mA DC, **Lp ≥ 25 H** (symulowane 15 H daje
dół −3 dB @24 Hz — zamówić większą indukcyjność), rozproszenie ≤10 mH.
Zasilanie: 230→250 V, mostek UF4007, 220µ + dławik 5–10 H + 220µ, B+ ~300 V.
Żarzenie: blok z `common/` (Schottky → 10000µ → LD1085 → 6,3 V DC,
elewacja +50 V z dzielnika B+ 220k/47k + 10µ). Budżet: 2×EL84 + ECC82 ≈1,9 A.

## Przełączniki charakteru (obie funkcje pasywne, DECYZJA)
- **S1 crossfeed (DPDT)**, między DAC a potencjometrem. Wartości po
  strojeniu w ngspice: tor prosty R 1k ∥ C 470n; krzyżowy R 2k2 → C 220n
  do masy → R 3k3 do przeciwnego kanału. Efekt: przesłuch −14 dB w basie,
  wygasa >~700 Hz; strata wtrąceniowa ~1–3 dB (skok głośności przy
  przełączaniu — normalny).
- **S2 "wokal do przodu" (DPST, po sekcji na kanał)**: katoda drivera ma
  C2a 1µ na stałe + C2b 100µ dołączane przełącznikiem. S2 otwarty →
  półka −3 dB poniżej ~200 Hz (lokalna degeneracja katodowa), wokal
  na pierwszym planie. Niskie napięcie (~4 V) — dowolny mały przełącznik.

## Wyniki symulacji (ngspice, modele Korena; headamp/sim/)
- Punkt pracy: EL84 285 V a-k / 29 mA (8,2 W z 12 W max); driver 140 V / 2,8 mA.
- Wzmocnienie 24,7 dB @1 kHz (ogromny zapas przy 2 Vrms z DAC).
- Pasmo (Lp=15 H): −3 dB @ 24 Hz i >100 kHz; Zout ~36 Ω (DF~2,2 przy 80 Ω).
- THD 1 kHz: 0,6 Vrms → 0,20% / 1,8 Vrms → 0,59% / 5,3 Vrms → 1,84%;
  widmo zdominowane przez H2 (H3 niżej o 20–33 dB) — profil "ciepły".
- Zastrzeżenie: modele Korena wiarygodne co do trendu, nie co do setnych %.

## Narzędzia / workflow (DECYZJA)
- KiCad 10; schemat docelowo generowany skryptem jak `riaa/gen.py` — TODO.
- MCP: wtyczka **Konnect** (github.com/mixelpixx/Konnect, beta, AGPL —
  darmowa dla hobbysty; PCM install + wpis w konfigu Claude Desktop).
- Symulacje: ngspice (netlisty w `headamp/sim/`).

## TODO
1. Zakup DT 770 M; sprawdzić sterowniki 0202 pod Windows na maszynie roboczej.
2. Specyfikacja OPT dla nawijacza (5k:80, ≥45 mA, Lp ≥25 H, opc. odczepy
   32/300 Ω) + wycena (Ogonowski / Trafco itp.).
3. `headamp/gen.py` + `check.py` (asercje netlisty jak w RIAA).
4. BOM z symbolami TME; przenieść blok żarzenia z `common/` 1:1.
5. Rozładowanie B+ (220k/2W przez C11) — przejąć automatykę K1 z common.
6. Decyzja obudowy: wpisać w serię TERCET (drewno + stal + widoczne lampy).
