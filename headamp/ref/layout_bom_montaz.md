# Montaż powietrzny — przydział elementów toru audio (listwy vs nóżki lamp)

Uzupełnienie do `headamp/ref/layout_top.svg`/`.png` (propozycja rozmieszczenia
w obudowie, 2026-09-08). Montaż **powietrzny** (bez PCB w torze audio):
część elementów dolutowana wprost do nóżek podstawek lampowych, część na
listwach lutowniczych pod górną płytą (patrz rysunek). Zasilacz — patrz
osobno `docs/PROJEKT-HEADAMP.md` (strefa zarezerwowana, decyzja PCB vs
powietrznie otwarta).

Numeracja jak w `headamp/gen.py`/schemacie: kanał L = refy bazowe (R1..R9,
C1..C6, U1 unit A, U2, T1), kanał P = te same refy **+200** (R201..R209,
C201..C206, U1 unit B, U202, T201) — identyczna topologia i przydział
montażowy, lustrzanie.

## Numery pinów (referencja)

- **ECC82** (`Valve:ECC81`, Value="ECC82"): unit A (driver kanału L) — grid=7,
  anoda=6, katoda=8; unit B (driver kanału P) — grid=2, anoda=1, katoda=3;
  żarzenie (unit F, wspólne dla obu sekcji) — piny 4 i 5 (końce), pin 9
  (odczep środkowy).
- **EL84**: grid1 (sterująca) = pin 2, katoda/g3 (zwarte) = pin 3, anoda =
  pin 7, grid2 (ekranująca) = pin 9; żarzenie = piny 4/5.

## Na nóżkach podstawek (bez listwy — montaż bezpośredni)

| Element | Miejsce | Uzasadnienie |
|---|---|---|
| R2 (1k, kanał L) / R202 (P) | między pinem 7 U1 unit A (grid, kanał L) a końcówką C1 — analogicznie R202 między pinem 2 U1 unit B a C201 | grid stopper tuż przy siatce lampy — minimalna indukcyjność/pojemność montażowa doprowadzenia do siatki (krytyczne dla stabilności WCz) |
| C1 (220n) / C201 | dolutowany do wolnej końcówki R2/R202 (patrz wyżej), drugi koniec do wypru RV1 | sprzęgający wejściowy — wisi bezpośrednio na nóżce grid-stoppera, brak dodatkowego punktu podparcia |
| **R1 (470k, grid leak drivera) / R201** | **na nóżce R2/C1 (węzeł siatki U1, za C1) → GND najbliższej listwy** — fizycznie na listwie A (przy wejściu siatki) albo wprost z nóżki R2/C1 do szyny masy, **NIE „między A i B"** (poprawka 2026-09-08: wcześniejszy zapis błędnie umieszczał R1 na trasie sprzęgacza driver→EL84 — R1 elektrycznie siedzi na węźle siatki ECC82, nie ma nic wspólnego z sygnałem po stronie EL84) | grid leak wejściowy — musi wisieć na tym samym węźle co grid stopper R2/C1, drugi koniec możliwie krótko do masy |
| R9 (100R, zwora triodowa) / R209 | między pinami 7 (anoda) i 9 (g2) EL84 U2/U202 | zwora g2→a definiująca pracę triodową — musi mieć minimalną długość przewodu (ryzyko oscylacji UHF przy dłuższych odcinkach) |
| R7 (1k) / R207 | jedna nóżka na pinie 2 (g1) EL84 U2/U202, druga do węzła sprzęgającego (patrz "między A i B" niżej) | grid stopper EL84 — jak R2, minimalna indukcyjność przy siatce |

## Listwa A (8–10 punktów, przy podstawce ECC82 U1) — wspólna dla obu kanałów, refy L i P obok siebie

| Punkt | Elementy | Węzeł |
|---|---|---|
| A1 | R3 (1k5) + C2 (1µ/25V) + C3 (100µ/25V, przez SW2) | katoda drivera (bias RC + obejście "wokal do przodu") |
| A2 | R4 (47k/2W) / R5 (10k/2W) + C4 (47µ/350V) | anoda drivera + odsprzęganie B+ drivera |
| A3 | R201 wersja kanału P (lustro A1) | jw., kanał P |
| A4 | R204/R205 + C204 (lustro A2) | jw., kanał P |

Uzasadnienie: węzły RC katodowe i odsprzęganie B+ na listwach (nie na
nóżkach) — łatwa wymiana/serwis, dostęp bez demontażu lampy; nie są
krytyczne pod względem długości przewodu (niska impedancja węzła katody,
niskie częstotliwości odsprzęgania).

## Między listwą A i listwą B_L/B_P (elementy sprzęgające, fizycznie pomiędzy)

**Poprawka 2026-09-08:** ta sekcja zawiera teraz tylko R6/R206 i C5/C205 — R1/R201
(grid leak *wejściowy*, strona ECC82) został z niej usunięty, patrz tabela
"Na nóżkach podstawek" wyżej (R1 siedzi na węźle siatki drivera, nie na trasie
sprzęgacza driver→EL84).

| Element | Uzasadnienie |
|---|---|
| R6 (470k, grid leak EL84) / R206 | elektrycznie w tym samym węźle co C5 (wyjście sprzęgacza, strona siatki EL84) — fizycznie musi sięgać od C5 (przy A) do GND (przy B) |
| C5 (100n/400V, sprzęgający driver→EL84) / C205 | łączy anodę drivera (listwa A) z grid-stopperem R7 przy EL84 — z definicji rozpięty między obiema strefami |

## Listwa B_L / B_P (5–6 punktów, przy podstawce EL84, osobna dla każdego kanału)

| Punkt | Elementy | Węzeł |
|---|---|---|
| B1 | R8 (270R/5W) + C6 (470µ/25V) | katoda EL84 (bias RC) |
| B2 | daleki koniec R6 (patrz wyżej) | grid leak EL84 → GND |
| B3 | daleki koniec R7 (patrz wyżej) | grid stopper EL84 → węzeł sprzęgający |

Kanał P: listwa B_P analogicznie z R208+C206 (punkt B1), R206/R207 (B2/B3).

## Listwa D (wyjściowa, przy jacku J403) — opcjonalna

Wtórne uzwojenia T1/T201 → jack 6,3 mm J403 (piny T/R/S) mogą iść
bezpośrednio (krótkie przewody, niska impedancja 80 Ω — długość przewodu
nieistotna). Listwa D przewidziana jako punkt pośredni tylko jeśli
mechanicznie wygodniej (np. odciążenie naprężeń przewodu do gniazda).

## Elektrolity wysokonapięciowe — z dala od gorących EL84

C4/C204 (47µ/**350V**, odsprzęganie B+ drivera) siedzą na **listwie A**
(przy ECC82), nie przy EL84: driver pracuje chłodniej niż końcówka mocy
(EL84 ~285 V/29 mA, 8,2 W rozpraszane w bańce), więc kondensator o
najwyższym napięciu izolacji w torze audio (poza zasilaczem) jest
umieszczony jak najdalej od źródła ciepła — dłuższa żywotność elektrolitu.
C6/C206 (470µ/25V, katoda EL84) musi siedzieć blisko EL84 (funkcjonalnie,
niska impedancja katody) — niższe napięcie, mniejsze ryzyko degradacji
termicznej niż przy 350 V.

## Szyna masy, żarzenie, B+ — trasy (patrz rysunek)

- **Szyna masy** (drut Ø1,5–2 mm): łamana ortogonalna wzdłuż rzędu listw
  (B_L→B_P poziomo, odczep pionowy do A), jeden punkt do chassis przez
  ground breaker (R309/D310/D311/C309) przy IEC — zgodnie z
  `docs/PROJEKT-HEADAMP.md` (jedyny styk GND↔PE). **Poprawka 2026-09-08
  (runda 2):** IEC J1+F1 przeniesione ze ściany tylnej na ścianę lewą
  (front, x=0, y≈6–54) — ground breaker fizycznie bliżej tego nowego
  miejsca, korytarz odgałęzienia od listwy B_L przesunięty z x≈98 na
  x≈101 mm (patrz `docs/PROJEKT-HEADAMP.md`).
- **Żarzenie** (skręcona para, 6,3 V DC z LD1085/U301): z uzwojenia T301
  wzdłuż lewej/tylnej krawędzi, korytarzem x≈101 mm, rzędem EL84 (U2→U202)
  do każdej podstawki — ECC82 piny 4+5 (+), pin 9 (−, odczep środkowy,
  redukcja przydźwięku); EL84 pin 4 (+), pin 5 (−). **Poprawka 2026-09-08
  (runda 2):** odgałęzienie do ECC82 (U1) idzie teraz prosto w dół ze
  środka między EL84 (x=178, nie od strony RV1/wejścia jak poprzednio) —
  skręcona para DC z dala od RV1/wejścia sygnału.
- **B+ (+300 V)**: przewód ze strefy zasilania do listw B_L/B_P i A —
  trasa poprowadzona z dala od toru wejściowego (crossfeed/RV1/RCA), aby
  uniknąć sprzężenia HV z sygnałem małej amplitudy.
- **Sygnał wejściowy**: RCA (tył, środek-prawo, J401/J402) → wzdłuż prawej
  krawędzi obudowy → listwa C (crossfeed, R401–R406/C401–C404; **przesunięta
  na prawo od RV1**, między RV1 a prawą ścianą — poprawka 2026-09-08, żeby
  sygnał z RCA nie krzyżował frontu) → RV1 → ECC82 (krótki tor siatkowy,
  patrz R2/R202 wyżej). Kabel ekranowany na całej trasie RCA→listwa C→RV1.
