# PROJEKT-HEADAMP — pamięć projektu wzmacniacza słuchawkowego

Dokument ustaleń, analogicznie do PROJEKT-RIAA.md. Przy pracy z AI podawać
ten plik na starcie sesji.

## Słuchawki — rekomendacja (żeby nie zapomnieć)
Kryterium nadrzędne: **jak najsilniejsze pasywne tłumienie hałasu** (praca
w głośnym otoczeniu; test odniesienia: syrena centralki alarmowej ma być
znośna). Bez ANC.

1. **Beyerdynamic DT 770 M** — WYBÓR GŁÓWNY (pod niego projektowany
   wzmacniacz). Uwaga: koniecznie wersja **"M"** (monitoring, dla perkusistów),
   nie zwykłe DT 770 Pro! ~35 dBA tłumienia (najwięcej wśród nausznych),
   80 Ω, mocny docisk (cena izolacji). OPT 5k:80 dobrany pod tę impedancję.
2. **Sennheiser HD 280 Pro** — plan B / budżetowo: do 32 dB, 64 Ω,
   ~85% izolacji DT 770 M za mniej niż połowę ceny; brzmienie poprawne, suche.
3. **Etymotic ER2SE / ER4SR (douszne + pianki)** — najlepsza izolacja
   w ogóle (35–42 dB) i wzorcowa neutralność, jeśli douszne wchodzą w grę;
   niska impedancja/wysoka czułość — uwaga na szum i dobór odczepu OPT.
Odrzucone: Direct Sound EX-29, Vic Firth SIH2 (izolacja OK, dźwięk słaby).

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
- **S1 crossfeed (DPDT)**, między gniazdami wejściowymi a potencjometrem.
  Wartości po strojeniu w ngspice: tor prosty R 1k ∥ C 470n; krzyżowy
  R 2k2 → C 220n do masy → R 3k3 do przeciwnego kanału. Efekt: przesłuch
  −14 dB w basie, wygasa >~700 Hz; strata wtrąceniowa ~1–3 dB (skok
  głośności przy przełączaniu — normalny). Tor prosty (R401∥C401/
  R402∥C402) jest ZAWSZE wpięty (bypass przełącznika) - to się nie
  zmieniło. **Implementacja na schemacie - przełącznik po stronie
  WYJŚCIOWEJ galęzi krzyżowej (DECYZJA 2026-09-08, patrz "Decyzje -
  crossfeed S1 na wyjściu" niżej dla pełnego uzasadnienia i liczb z
  symulacji)** - `sim/crossfeed_sw.cir` jest źródłem prawdy dla dokładnej
  topologii (trzy warianty: ON, OFF nowa topologia, OFF stara topologia -
  porównanie).
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

## TODO (patrz tez aktualna lista na koncu dokumentu, po Etapie 5b)
1. Zakup DT 770 M; sprawdzić sterowniki 0202 pod Windows na maszynie roboczej.
2. Specyfikacja OPT dla nawijacza (5k:80, ≥45 mA, Lp ≥25 H, opc. odczepy
   32/300 Ω) + wycena (Ogonowski / Trafco itp.).
3. ~~`headamp/gen.py` + `check.py` (asercje netlisty jak w RIAA).~~ ZROBIONE.
4. BOM z symbolami TME; przenieść blok żarzenia z `common/` 1:1.
5. ~~Rozładowanie B+ (220k/2W przez C11) — przejąć automatykę K1 z common.~~
   ZROBIONE (Etap 5b: R303 bleeder + K1/R306).
6. Decyzja obudowy: wpisać w serię TERCET (drewno + stal + widoczne lampy).

## Decyzje - Etap 5a (kanal P, 2026-09-07)
- RV1 = **potencjometr podwojny** (jedna fizyczna os), symbol
  `Device:R_Potentiometer_Dual_Separate` (biblioteka systemowa KiCad 10):
  unit 1 (piny 1/2/3) = kanal L, unit 2 (piny 4/5/6, identyczna geometria
  wzgledna) = kanal P. Brak wczesniejszej decyzji w tym dokumencie -
  wybrano zamiast dwoch osobnych RV1A/RV1B, bo w bibliotece jest gotowy
  symbol dual, a w praktyce kupujemy jeden fizyczny podwojny potencjometr
  (Alps/inny), nie dwa osobne.
- Kanal P: refy +200 wzgledem kanalu L (R201-R209, C201-C206, SW202,
  T201, U202=drugi EL84); U1 (ECC82) unit B (piny 1=A,2=G,3=K) dla
  drivera kanalu P - ta sama fizyczna lampa co kanal L. Etykiety
  IN_R/OUT_R (nie IN_P/OUT_P - zgodnie z konwencja L/R jak w RIAA).
- Layout: kanal P = identyczna geometria kanalu L, przesunieta o
  dy=105,41 mm w Y (wielokrotnosc siatki 1,27 mm - inna wartosc daje
  ERC "endpoint_off_grid" na kazdym przesunietym drucie/pinie).
- Grzanie: wspolna szyna HEAT_A/HEAT_B dla wszystkich 3 lamp (ECC82
  U1 unit F, EL84 U2 i U202, kazdy wlasny unit grzania) - jak w RIAA.
- PWR_FLAG na powrocie wtornym OPT do GND: tylko JEDEN na cala plansze
  (przy T1/kanal L) - drugi (na T201/kanal P) daje ERC error "Power
  output and Power output are connected" (oba na tym samym wezle GND).
- Paper: na razie zostaje **A3** (kanal P miesci sie, max Y ~275 mm);
  decyzja o A2 odlozona do Etapu 5b (zasilacz), patrz TODO.

## Decyzje - Etap 5b (zasilacz, 2026-09-07)
- Zasilacz narysowany na tym samym arkuszu co audio (nie osobny arkusz
  hierarchiczny), layout DRUTAMI jak riaa/gen.py, pod kanalem P i
  grzaniem lamp. Numeracja 3xx (R301.., C301.., D301..), z wyjatkami
  nazwanymi wprost (F1, SW1, J1, RT1, RV301, NE1, T301, L1, K1, U301) -
  zgodnie z poleceniem etapu.
- **Paper zmieniony z A3 na A2** (DECYZJA) - zasilacz + oba kanaly +
  grzanie nie miesciy sie w A3 (docelowa wysokosc tresci ~427mm).
- **B+ (+300V) WSPOLNY dla obu kanalow** (bez podzialu per-kanal jak w
  RIAA) - headamp ma mniejszy pobor pradu (2x EL84 + ECC82, bez
  wtornika mocy), jeden wezel +300V po filtrze CLC wystarcza; brak
  osobnych R/C dropperow per kanal.
- Transformator: `Device:Transformer_1P_2S` (2 uzwojenia wtorne - HT +
  zarzenie), NIE customowy symbol jak w RIAA (headamp nie potrzebuje
  uzwojenia 24V rezerwowego ani odczepu 6,3V - tylko jedno uzwojenie
  zarzenia 7V/3A na 3 lampy, patrz common/README.md).
  Wartosc pola Value: "EI84 100VA: 230V : 250V/0,15A + 7V/3A".
- Mostek HT: 4x UF4007 + snubber RC 470R/10n-1kV przez uzwojenie (1:1
  z riaa/common). Filtr: C 220u/400V -> L1 (dlawik, etykieta wartosci
  "5-10H 100mA", uwaga: Lp OPT >=25H to co innego - dlawik zasilacza
  nie ma zwiazku z indukcyjnoscia pierwotna OPT) -> C 220u/400V = +300V.
  Bleeder 220k/2W (R303) na wyjsciu (zamyka TODO 5 z listy glownej).
- Elewacja zarzenia: 220k (R304, z +300V) -> ELEV -> 47k (R305) -> GND;
  10u/100V (C304) ELEV->GND. Wartosci z PROJEKT-HEADAMP (220k/47k),
  NIE z RIAA (470k/100k) - inny prad/napiecie docelowe (+50V dla 6,3V
  vs RIAA gdzie wtornik ma Vhk wiekszy).
- Rozladowanie K1: 1:1 z riaa/common (przekaznik 9V cewka V_RAW/ELEV,
  dioda 1N4007 gaszaca, styk NC(11-12) -> R306 4k7/10W -> GND, COM(12)
  na +300V, NO(14) niepodlaczony).
- Zarzenie: 7V -> 4x 1N5822 -> 10000u/16V (=V_RAW) -> 470u/25V ->
  LD1085 (symbol Regulator_Linear:LM317_TO-220, adnotacja "LD1085
  (LDO)") -> 240R/976R -> 6,3V DC (HEAT_A/HEAT_B), 10u/25V + 1u
  odsprzegajace. Wartosci identyczne jak common/riaa.
- PWR_FLAG: zasada "jeden na siec" - usuniete zdublowane flagi (HEAT_A
  ma juz sterownik U301.VO, drugi punkt zwarty do GND przez OPT
  sekundarny nie potrzebuje wlasnej flagi skoro siec GND ma juz inna).
  Dodana 1 nowa flaga na V_RAW (mostek Schottky to elementy bierne,
  ERC wymaga sterownika dla U301.VI).
- ERC: multiple_net_names ELEV/HEAT_B (heater powrot zwarty do ELEV,
  jak w common/riaa) - OSTRZEZENIE OCZEKIWANE, zaakceptowane zgodnie
  z poleceniem etapu.
- Ground breaker: 1:1 z common/riaa (10R/5W + 2x1N5408 antyrownolegle
  + 100n/630V), jedyny styk masy sygnalowej (GND) z PE/chassis.

## Stan realizacji (2026-09-08, po kosmetyce arkusza)
- Schemat generowany skryptem **`headamp/gen.py`** (+ `symlib.py` +
  `check.py`, wzor riaa/) - **zrodlo prawdy = gen.py, NIE edytowac
  `headamp.kicad_sch` recznie**. UUID deterministyczne (uuid5) -
  regeneracja jest idempotentna (git diff pusty przy dwoch uruchomieniach).
- Kanał L + kanał P + zasilacz + crossfeed S1 + gniazda WE/WY + żarniki
  lamp **kompletne, layout w ramkach modułów**. **ERC: 0 błędów, 0
  ostrzeżeń** (po przywróceniu żarników drutami - patrz "Decyzje -
  kosmetyka arkusza" niżej; `multiple_net_names` ELEV/HEAT_B też
  zniknęło, bo etykieta HEAT_B na końcu szyny została usunięta, a jedyna
  pozostała nazwa na tej sieci to ELEV).
- UWAGA numeracja na schemacie różni się od sekcji "Wartości" wyżej:
  C2=1µ (katoda, stały), C3=100µ (za SW2), C5=100n (sprzęgający),
  C6=470µ (katoda EL84), R9=100R (zwora triodowa) - kanał L; kanał P =
  te same refy +200; moduł wejściowy (crossfeed+gniazda) = refy 4xx
  (J401/J402/J403, SW401, R401-R406, C401-C404). Schemat (gen.py) =
  źródło prawdy.
- Tolerancje (pole `Tolerance`, widoczne pod Value; DECYZJA): rezystory 5%
  (R3 1k5 katoda drivera — 1%, punkt pracy), folie C1/C5 5%, elektrolity
  20%, RV1 20%. Lampy/OPT/przełączniki bez tolerancji. Zaimplementowane
  w gen.py (parametr `tol=` w `place()`).
- Kanał P (Etap 5a): unit B ECC82 (driver), drugi EL84 (U202), drugi OPT
  (T201), RV1 = potencjometr podwójny. Layout = geometria kanału L
  przesunięta w Y (dy=105,41mm, siatka 1,27mm).
- Zasilacz (Etap 5b): B+ wspólny 300V (CLC), elewacja 220k/47k, K1
  rozładowanie, żarzenie LD1085, ground breaker - patrz sekcja DECYZJE
  wyżej.
- Crossfeed S1 + gniazda WE/WY (Etap 6/A-B): narysowane w gen.py, wg
  `sim/crossfeed.cir` - patrz "Decyzje - Etap 6" wyżej dla pełnego opisu.
- Layout w ramkach modułów + hybryda "druty zamiast etykiet" dla B+
  (Etap 6/A) - patrz "Decyzje - Etap 6".
- Kolejne kroki i stan narzędzi (Konnect/KiCad): patrz CLAUDE.md w korzeniu.

## TODO (aktualizacja po kosmetyce arkusza - skreslone zrobione)
- ~~gen.py + check.py (kanał L port 1:1)~~ ZROBIONE (Etap 0-1).
- ~~Kanał P~~ ZROBIONE (Etap 5a).
- ~~Zasilacz (B+, żarzenie, K1, ground breaker)~~ ZROBIONE (Etap 5b).
- ~~Crossfeed S1 (DPDT) + gniazda WE/WY na schemacie~~ ZROBIONE (Etap
  6/A-B, patrz sekcja "Decyzje - Etap 6" niżej).
- ~~Estetyka schematu (Etap 6)~~ ZROBIONE (przegląd render -> poprawki
  pól ref/value/tolerance w gen.py: domyślne offsety 3-liniowe, F1/SW1,
  J1/PWR_FLAG/Earth_Protective, R301/NE1, R303/L1, ground breaker).
- ~~ERC `missing_power_pin` (3 błędy, U1/U2/U202)~~ ZAŁATWIONE (2026-09-08,
  wariant a): żarniki lamp przywrócone na schemat, rysowane drutami
  wewnątrz ramki ŻARZENIE - patrz "Decyzje - kosmetyka arkusza" niżej.
  ERC = 0 błędów, 0 ostrzeżeń.
- BOM (TME) + specyfikacja OPT dla nawijacza (5k:80, ≥45mA, Lp≥25H).
- Zakup DT 770 M; sprawdzić sterowniki 0202 pod Windows.
- Decyzja obudowy (seria TERCET).

## Decyzje - Etap 6 (layout w ramkach, crossfeed, gniazda, 2026-09-08)

**A. Hybryda "druty zamiast etykiet".** Połączenia MIĘDZY modułami
(B+ → oba kanały i OPT, sygnał wejście → crossfeed → RV1 → kanały,
wyjścia OPT → gniazdo słuchawkowe) są teraz rysowane prawdziwymi drutami
(z junctions), bez global/local labels - poza HEAT_A/HEAT_B i ELEV,
które explicite zostają etykietami (patrz punkt B) i GND/PE, które
zostają symbolami power (fizycznie szyna masy), zgodnie z konwencją
common/riaa. B+ (+300V): jedna magistrala pionowa `BUS_X=245,11mm`
(`headamp/gen.py`) łącząca korytarze nad oboma kanałami (y=80,01/185,42,
powyżej wszystkich komponentów kanału - brak kolizji) z zasilaczem (CLC,
R304/elewacja, K1) - zamiast 7 wcześniejszych `global_label('+300V')`.

**B. Żarniki lamp NIE SĄ RYSOWANE (DECYZJA).** Unity grzania ECC82 (U1
unit3), EL84 audio L/P (U2/U202 unit2) usunięte ze schematu razem z
drutami i etykietami po stronie lamp (dawny "rząd grzania" pod kanałem
P, Etap 5a). Blok zasilacza (LD1085/U301) kończy się jak wcześniej
etykietami lokalnymi **HEAT_A** (+6,3 V) i **HEAT_B** (= ELEV, minus
żarzenia, stąd oczekiwane ostrzeżenie ERC `multiple_net_names`) na
końcach drutów, z adnotacją tekstową na schemacie (obok U301):
"Zarzenie do lamp (skrecona para): ECC82 piny 4+5 -> HEAT_A, pin 9 ->
HEAT_B; EL84 (x2) pin 4 -> HEAT_A, pin 5 -> HEAT_B." - montażysta
łączy żarniki punkt-punkt wg tego opisu, nie wg schematu.
**Konsekwencja odkryta w tym etapie (różni się od pierwotnego briefu):**
piny grzania w bibliotece `Valve` (ECC81 unit C, EL84 unit B) są typu
`power_in`. KiCad ERC dla unitu z pinami `power_in`, który w ogóle nie
jest umieszczony na schemacie, zgłasza nie tylko ostrzeżenie
`missing_unit` (przewidziane), ale też **błąd `missing_power_pin`** (dla
każdego z U1/U2/U202 - 3 błędy). Domyślna severity tej reguły
(`error`) jest zapisana w `headamp.kicad_pro`
(`erc/rule_severities/missing_power_pin`), pliku poza zakresem zmian
generatora (nie ruszać/nie commitować - patrz CLAUDE.md) - nie da się
więc obniżyć jej z poziomu `gen.py`/`check.py`. Efekt: ERC schematu ma
formalnie 3 błędy, nie tylko same ostrzeżenia. Zaakceptowane jako
świadoma, udokumentowana konsekwencja decyzji "żarniki nie są rysowane"
- alternatywa (przywrócenie unitów z realnym okablowaniem) cofnęłaby tę
decyzję i wymaga wyraźnego wyboru użytkownika (patrz TODO wyżej).

**C. Crossfeed S1 - przełączany DPDT.** ***UWAGA: topologia opisana w tym
punkcie (przełącznik po stronie WEJŚCIOWEJ galęzi krzyżowej) została
ZASTĄPIONA decyzją z 2026-09-08 - patrz sekcja "Decyzje - crossfeed S1 na
wyjściu (2026-09-08)" na końcu dokumentu. Punkt C zostaje jako zapis
historyczny (uzasadnienie zmiany, liczby z porównania).*** Element `SW401`
(`Switch:SW_DPDT_x2`), Value "S1 crossfeed", numeracja 4xx (moduł
wejściowy: J401/J402, SW401, R401-R406, C401-C404). **Topologia i
wartości - ŹRÓDŁO PRAWDY: `headamp/sim/crossfeed.cir`** (nie opis niżej
w tym dokumencie sprzed Etapu 6, ani wcześniejsza wersja - cir nie
zawiera samego przełącznika, modeluje topologię z pozycją "krzyżowy"
załączoną). Implementacja: tor prosty R401∥C401 (kanał L), R402∥C402
(kanał P) jest **ZAWSZE wpięty** między gniazdo a RV1 (bypass
przełącznika - w cir to węzły `l1->lout`/`r1->rout`, obecne bez
przełącznika w ogóle). SW401 przełącza **tylko dopływ sygnału do gałęzi
krzyżowej**: pole 1 (piny 1/2, unit1) doprowadza IN_L do R403; pole 2
(piny 4/5, unit2) doprowadza IN_R do R404; trzeci pin każdego pola (3/6)
jest NC - to reprezentuje pozycję "prosty" (gałąź krzyżowa odłączona,
pływająca). Gałąź krzyżowa: R403(2k2) SW->mL, C403(220n) mL->GND,
R405(3k3) mL->outR (przeciwny kanał); mirror: R404/mR/C404/R406->outL.
Pozycji przełącznika (obu) nie da się zweryfikować statyczną netlistą -
schemat rysuje jedną (załączoną) pozycję, jak w cir; `check.py` sprawdza
to co da się sprawdzić statycznie (patrz komentarz w pliku).

**D. Gniazda WE/WY.** Wejście: 2× RCA `Connector:Conn_Coaxial` - J401
(IN L), J402 (IN R); pin sygnału -> crossfeed, ekran -> GND. Wyjście:
TRS 6,3 mm `Connector_Audio:AudioJack3` - J403; piny T=kanał L (T1
wtórne), R=kanał P (T201 wtórne), S=GND (wspólna z wtórnymi OPT).

**E. Layout w ramkach.** Moduły w ramkach (`(rectangle ...)` na
arkuszu, obsługiwane w formacie 20231120 - zweryfikowane) z tytułem w
lewym górnym rogu: WEJŚCIE, KANAŁ L, KANAŁ P, WYJŚCIE, SIEĆ 230V,
ZASILACZ B+ 300V, ŻARZENIE. Rozmieszczenie: lewo-góra WEJŚCIE;
KANAŁ L nad KANAŁ P (środek, ta sama geometria + dy); WYJŚCIE na prawo
od kanałów, między nimi w Y; dół (cała szerokość): SIEĆ | ZASILACZ B+ |
ŻARZENIE.

**F. Rozmiar arkusza: A2 zostaje** (DECYZJA, potwierdzona 2026-09-08 przy
kosmetyce arkusza - patrz niżej). Treść po Etapie 6 zajmowała ok.
400×428 mm (blisko górnej granicy A2 w orientacji poziomej, 594×420mm).
A3 (420×297) odpadał z powodu wysokości treści (428 mm > 297 mm)
niezależnie od szerokości, i nadal odpada po zmniejszeniu `PSU_DY` (patrz
"Decyzje - kosmetyka arkusza" niżej): treść ma teraz ok. 378 mm wysokości
- dalej ponad limit A3 (297 mm) o ~80 mm, więc A2 zostaje.

## Decyzje - kosmetyka arkusza (2026-09-08)

**G. Żarniki lamp przywrócone (wariant a).** Decyzja z Etapu 6 ("żarniki
nie są rysowane", ERC z 3 błędami `missing_power_pin`) COFNIĘTA na
wyraźne życzenie użytkownika. Unity grzania ECC82 (U1 unit3, piny 4/5/9)
i EL84 audio L/P (U2/U202 unit2, piny 4/5) są teraz narysowane WEWNĄTRZ
ramki „ŻARZENIE 6,3V DC", połączone **drutami** (nie etykietami) z
wyjściem VO regulatora LD1085 (U301, szyna „+6,3V" na wysokości `YHP`) i
z minusem żarzenia (szyna na wysokości `YHM`, ta sama sieć co ELEV).
Etykiety `HEAT_A`/`HEAT_B` oraz opisowy tekst z mapowaniem pinów
usunięte - teraz widać połączenia bezpośrednio na rysunku. Topologia:
ECC82 piny 4 i 5 (oba nazwane `F1` w symbolu, dwa końce żarnika) → +6,3V;
pin 9 (`F2`, środkowy odczep) → minus (redukcja przydźwięku, zgodnie z
zaleceniem). EL84: pin 4 (`F1`) → +6,3V; pin 5 (`F2`) → minus. Wszystkie
piny każdej lampy „zbiegają się" na wspólnej linii bazowej w połowie
odległości między szynami (`Y_HEAT_PINS = (YHP+YHM)/2`) i stamtąd
rozchodzą się w przeciwne strony (+ w górę, − w dół) - dzięki temu żaden
odcinek drutu nie nakłada się na inny (kluczowe dla ECC82, gdzie pin
środkowy `9` siedzi geometrycznie między pinami `4` i `5`). Krótki tekst
na schemacie: "Zarzenie do lamp: skrecona para, minus = ELEV (+53V)."
Ramka ŻARZENIE poszerzona (x1: 400→495,3mm), żeby pomieścić 3 lampy w
rzędzie (rozstaw 30,48/29,21mm - konwencja z wcześniejszej wersji
rysunku, commit fc227e8). **Efekt: ERC = 0 błędów, 0 ostrzeżeń**
(zniknęły `missing_unit` x3 i `missing_power_pin` x3; `multiple_net_names`
ELEV/HEAT_B też zniknęło, bo etykieta `HEAT_B` na końcu szyny została
usunięta - jedyna nazwa na tej sieci to teraz `ELEV`). check.py: dodane
asercje `same`/`diff` dla żarników po stronie lamp (U1.4/U1.5/U1.9,
U2.4/U2.5, U202.4/U202.5) w sekcji "zarzenia (grzanie)".

**H. Prąd żarzenia poprawiony: 1,7 A, nie 0,3 A.** Błąd merytoryczny w
tekście na schemacie ("ok. 0,3A z uzwojenia 7V (3 lampy)") - to była
literówka/nieporozumienie, prawidłowa wartość to **ok. 1,7 A** (2×EL84 ≈
0,76 A każda + ECC82 ≈ 0,15 A na obie połówki; budżet w tym dokumencie
to ≈1,9 A, patrz sekcja "Wartości" wyżej). Tekst poprawiony na: "Zarzenie:
6,3V DC / ok. 1,7A (2x EL84 0,76A + ECC82 0,15A; budzet 1,9A) z
uzwojenia 7V/3A." Inne liczby na schemacie/w dokumentacji sprawdzone przy
okazji (bez zmian, uznane za spójne):
- Uzwojenie żarzenia 7V/3A (T301) - zapas przy 1,7 A poboru, OK.
- B+ ~300V @ ~65mA (dokumentacja, nie schemat) - zgodne z symulacją
  (2×29mA EL84 + 2×2,8mA driver ≈ 63,6mA ≈ "~65mA").
- LD1085 3A - z dużym zapasem ponad 1,7A wymagane.
- Dropout LD1085 przy 1,7A: uzwojenie 7V AC -> mostek Schottky 1N5822 ->
  V_RAW (peak ~7×1,41−2×~0,5≈8,9V, pod obciążeniem realnie kilka mV/V
  mniej z tętnieniem) - z zapasem pokrywa Vout(6,3V)+dropout LD1085
  (typowo ~1,3-1,5V przy tym prądzie); tekst na schemacie zaktualizowany
  na "LD1085 (LDO) - LM317 ma za duzy dropout przy 1,7A (V_RAW ~9V z
  uzwojenia 7V wystarcza)." Zastrzeżenie: nie zmierzone na prototypie,
  wartość orientacyjna z danych katalogowych.

**I. Pusty pas między KANAŁ P a rzędem zasilacza zamknięty.** Między
ramką KANAŁ P (kończy się Y=282,41mm) a rzędem SIEC/ZASILACZ/ŻARZENIE
(zaczynał się Y=340mm) był pusty pas ~57,6mm. `PSU_DY` (przesunięcie
całego bloku zasilacza w Y) zmniejszony z 76,2mm do 26,67mm (SHIFT =
49,53mm = 39×1,27mm - wielokrotność siatki schematu, żeby wszystko
zostało na gridzie). Nowy pas ~8mm, jak między innymi modułami na
arkuszu. Współrzędne zapisane wcześniej jako już-wyliczone wartości
absolutne (nie "baza + PSU_DY": pola ref/value F1/R301/NE1/R309/D310/
D311/C309, kilka punktów drutów mostka HT/żarzenia) zostały ręcznie
przeliczone o ten sam SHIFT - reszta bloku (`LR`/`NR`/`YP`/`YM`/`YHP`/
`YHM` i wszystko wyrażone przez `PSU_DY`) przesunęła się automatycznie.
Zweryfikowane: regeneracja idempotentna (dwa uruchomienia `gen.py` dają
identyczny plik), ERC = 0/0, cała treść arkusza mieści się wygodnie w
obrębie ramki A2 (marginesy zachowane, nic nie dotyka ramki arkusza ani
tabliczki tytułowej - sprawdzone na renderze PDF w powiększeniu).

## Decyzje - crossfeed S1 na wyjściu (2026-09-08)

**Powód zmiany.** W topologii z Etapu 6 (SW401 na WEJŚCIU galęzi
krzyżowej - patrz punkt C wyżej) rezystory R405/R406 (3k3) i kondensatory
C403/C404 (220n) galęzi krzyżowej ZOSTAWAŁY na wyjściach nawet przy S1
w pozycji "prosty" (OFF): przełącznik odcinał tylko dopływ z wejścia do
R403/R404, ale R405+C403 (R406+C404) nadal wisiały jako obciążenie RC na
wyjściach toru prostego. Zmierzone symulacją (patrz niżej): ugięcie
pasma ~1,4 dB w rejonie 100-200 Hz - słyszalne, niepożądane przy "S1
OFF" (tor prosty powinien być dokładnie płaski). DECYZJA: przenieść S1
na stronę WYJŚCIOWĄ galęzi krzyżowej (za R405/R406, tuż przed wspólnym
węzłem z torem prostym) - przy S1 OFF cała galąź krzyżowa (R403..R406,
C403/C404) jest odcięta od wyjść, więc nie ma żadnego wpływu na tor
prosty.

**Symulacja (ngspice NIEDOSTĘPNY w PATH - nie zainstalowany, zgodnie z
poleceniem "jeśli nie - zgłoś, nie instaluj" NIE zainstalowano go; wyniki
niżej policzone analitycznie - nodal/MNA solver dla dokładnie tej samej
topologii RLC co w `sim/crossfeed_sw.cir`, skrypt jednorazowy, nie
commitowany). Plik `headamp/sim/crossfeed_sw.cir` zawiera 3 warianty
gotowe do uruchomienia w ngspice, gdy będzie dostępny (`ngspice -b
headamp/sim/crossfeed_sw.cir`):**

1. **ON (krzyżowy załączony)** - identyczny elektrycznie w obu
   topologiach (pozycja przełącznika nie zmienia, gdzie w torze siedzi,
   tylko czy jest zamknięty). Przesłuch (poziom na wyjściu
   przeciwnego kanału, sygnał testowy tylko w L): **-15,8 dB @100 Hz,
   -30,0 dB @1 kHz** (zanika >~700 Hz, zgodnie z wcześniejszym opisem
   "-14 dB w basie" - różnica rzędu 1-2 dB wobec wcześniejszego zapisu to
   normalna rozbieżność modelu, rząd wielkości ten sam).
2. **OFF, nowa topologia (S1 na wyjściu galęzi krzyżowej)** - odchyłka
   odpowiedzi kanału prostego (20 Hz-20 kHz) od płaskiej: **~0,17 dB**
   (od -0,19 dB @20 Hz do -0,02 dB @20 kHz) - to wyłącznie efekt C401/
   C402 (470n) w torze prostym (nie samego dzielnika R401/RpotL, który
   sam w sobie byłby idealnie płaski); brak przesłuchu (kanały całkowicie
   rozłączone, cross = -∞ dB w modelu).
3. **OFF, stara topologia (S1 na wejściu galęzi krzyżowej, ODRZUCONA)** -
   odpowiedź kanału prostego NIE jest płaska: dołek ok. **-1,58 dB w
   okolicy 200 Hz** względem końców pasma (-0,23 dB @20 Hz, -0,28 dB
   @20 kHz) - efekt obciążenia wyjścia przez R405 (3k3) szeregowo z C403
   (220n) do masy, mimo otwartego S1. Rozstęp całkowity ~1,36 dB - to
   właśnie "ugięcie basu" uzasadniające zmianę topologii.

**Zmiany w `headamp/gen.py` (moduł WEJŚCIE).** SW401 przeniesiony z
x=90,17 (przy wejściach) na x=149,86 (tuż przed magistralami wyjściowymi
outL/outR, x=175,26/185,42), obie sekcje (unit1/unit2) w tym samym x,
różne y (39,37 i 52,07) - "obok siebie". Element umieszczony z
`mirror='y'`, żeby COM (wspólny) wypadł po PRAWEJ (do wyjścia), a styk
(od strony R405/R406) po LEWEJ - odzwierciedla kierunek sygnału.
Wejścia J401/J402 podłączone teraz WPROST do R403/R404 (galąź krzyżowa)
i - osobnym odgałęzieniem nad/pod galęzią krzyżową (y=22,86 / y=64,77) -
do R401/R402 (tor prosty); przełącznik nie leży już na tej ścieżce.
R405/R406 łączą się ze stykiem SW401 (piny 1/4), NC (piny 3/6) pozostaje
jak wcześniej ("pozycja prosty = galąź pływająca"), COM (piny 2/5)
podłączony do magistrali wyjściowej przeciwnego kanału (sekcja A -> outR/
RV1.4, sekcja B -> outL/RV1.1). Layout "X" bez przecięcia drutów: galąź
L->P kończy na dalszej (prawej) magistrali outR, galąź P->L na bliższej
(lewej) magistrali outL - dwie przeciwbieżne ścieżki między rzędami L
(u góry) i P (u dole), bez wspólnego junction w żadnym miejscu
przecięcia. Podpis na schemacie: "S1 crossfeed: ON = przesluch -14 dB w
basie (<700 Hz), OFF = tor prosty".

**Zmiany w `headamp/check.py`.** Sekcja "CROSSFEED S1" przepisana pod
nową topologię: `same(J401.1, R401.1, R403.1, C401.1)` (gniazdo L, bez
przełącznika po tej stronie), `same(R401.2, C401.2, RV1.1, SW401.5)`
(wyjście toru prostego L + COM sekcji B), analogicznie dla P; `same(R405.2,
SW401.1)` / `same(R406.2, SW401.4)` (R405/R406 -> styk); dodane
`diff(SW401.1, SW401.2)` / `diff(SW401.4, SW401.5)` (styk != COM - test
że nie ma przypadkowego zwarcia stykiem-COM na schemacie).

## Montaż — propozycja rozmieszczenia (2026-09-08, poprawki tego samego dnia)

Propozycja fizycznego rozmieszczenia elementów w obudowie (rzut z góry,
**260×200 mm wnętrza** — zmniejszone z pierwotnych 300×250, patrz "Obudowa
zwarta" niżej, skala 1:1) — `headamp/layout/layout_top.py` (Python +
matplotlib, bez KiCada) → `headamp/ref/layout_top.svg`/`.png`. Tabela
przydziału elementów toru audio (nóżki podstawek lamp vs listwy
lutownicze) — `headamp/ref/layout_bom_montaz.md`.

Założenia (nie zmieniać bez decyzji użytkownika): montaż **powietrzny**
toru audio (listwy lutownicze + elementy dolutowane wprost do nóżek
podstawek lamp, wg zasady "stoppery/zwora przy lampie, RC katodowe i
odsprzęganie na listwach"). Lewa strefa (x 0–100 mm) = zasilanie: T301 (oś
równolegle do X) tył-lewo, L1 przed nim, IEC+F1 **w ścianie lewej, z
przodu** (patrz "Poprawki 2026-09-08, runda 2" niżej — pierwotnie planowane
w ścianie tylnej, przeniesione z powodu kolizji z T301), zarezerwowana
strefa "PCB zasilacza" 90×140 mm pod płytą. Prawa strefa (x 100–260) =
audio: OPT T1/T201 przy tylnej ścianie (oś obrócona 90° względem T301),
EL84 tuż przed swoimi OPT, ECC82 z przodu pośrodku między EL84 (≥35 mm
odstępu między lampami, ≥25 mm od transformatorów, **oraz ≥100 mm
T301↔RV1/RCA/ECC82** — wszystkie trzy reguły sprawdzone w skrypcie
automatycznie, geometria OK bez kolizji). Front (y=0), od lewej: J1+F1
(ściana lewa, x=0, y≈6–54) — SW1+NE1 (przesunięte w prawo, x=58/80) —
SW401 (crossfeed) — RV1 — SW2/SW202 — J403. Tył (y=200): J401/J402 RCA
(środek-prawo, z dala od T301).

**DECYZJA: zasilacz na PCB** (nie powietrznie; potwierdzone 2026-09-08,
zamyka wcześniejszą "otwartą decyzję"). Strefa 90×140 mm pod płytą (lewa
strefa zasilania) to **PCB zasilacza**: mostki HT, filtr CLC (bez dużych
elektrolitów, jeśli C302/C303 pójdą w "kubku" na górnej płycie — obie
opcje zostają otwarte, patrz niżej), K1 (przekaźnik rozładowania),
LD1085 + radiator, sieć ochronna wejścia (NTC/warystor/neon-rezystor),
ground breaker (jeden punkt GND↔PE, przy IEC). Uzasadnienie decyzji:
1) elementy mechaniczne wymagają solidnego mocowania, którego PCB nie
   zapewnia dobrze samo z siebie: radiator LD1085 (skręcany do chassis),
   przekaźnik K1 (masa, wibracje), potencjalnie 10000 µF (V_RAW) — to
   wszystko lepiej trzymać na płytce przykręconej do chassis, nie na
   przewodach powietrznych; 2) odstępy izolacyjne przy ~300 V DC są
   łatwiejsze do zagwarantowania i powtarzalne na projektowanej płytce
   (kontrolowane szczeliny/prześwity) niż przy ręcznym montażu
   powietrznym; 3) **blok wspólny serii** (`common/`, LD1085 + elewacja +
   K1 + ground breaker identyczne jak RIAA) — jedna płytka PCB obsługuje
   docelowo trzy urządzenia serii TERCET, więc zaprojektowana raz się
   nie marnuje.
   Elementy pozostające na chassis (górna płyta), NIE na PCB: **T301, L1,
   IEC J1+F1, SW1, NE1** (front) — mechaniczne/ciężkie lub muszą fizycznie
   przebijać obudowę (gniazda/przełączniki panelowe).
   TODO: projekt PCB zasilacza (KiCad; Konnect wymaga konfiguracji IPC dla
   narzędzi PCB — patrz CLAUDE.md).

**L1 (dławik 5–10 H, ~0,5–1 kg) — DECYZJA: zostaje na chassis (górnej
płycie), NIE na PCB.** Powód: masa i objętość dławika (rdzeń z
uzwojeniem) czynią go elementem typowo mocowanym mechanicznie do metalu
(śruba przez rdzeń/klamrę), a nie lutowanym na płytce — PCB nie udźwignie
takiego ciężaru bez dodatkowego wsparcia mechanicznego, więc prościej
zostawić go tam, gdzie mocowanie jest naturalne. L1 stoi na górnej płycie
tuż przed T301 (patrz rysunek), w tej samej strefie co PCB zasilacza
(PCB fizycznie POD nim, na osobnej warstwie — brak kolizji, to inna
płaszczyzna montażu).

**Obudowa zwarta: 260×200 mm (z 300×250).** Przeliczone na realnych
footprintach: T301 85×70, L1 55×45, OPT 55×45 ×2, podstawki noval Ø22 +
kołnierz, RV1 (galka Ø26 + korpus 40×26 od spodu). Zmiany geometrii
względem pierwszej propozycji:
- Strefa zasilania (x 0–100) bez zmian szerokości (T301 i tak potrzebuje
  ~95 mm z marginesem) — oszczędność przyszła z osi Y i strefy audio.
- EL84 (U2/U202) przesunięte bliżej środka (x=128/228, było 140/240) i
  bliżej frontu (y=90, było 150) — mniejszy odstęp od OPT (nadal ≥25 mm,
  sprawdzone: 28,5 mm po korekcie) i od siebie (100 mm, zapas nad
  wymaganymi 35 mm).
- ECC82 (U1) przesunięty na x=178 (było 190), y=45 bez zmian.
- Wysokość obudowy zmniejszona ze 250 na 200 mm — puste pole audio
  (dawne y≈60–140 z pierwszej propozycji) zamknięte przez przesunięcie
  EL84/OPT bliżej frontu.
- Wynik: 260×200 mm = 52 000 mm² vs 300×250 mm = 75 000 mm² (~31%
  mniejsza powierzchnia górnej płyty), marginesy od ścian dla elementów
  stojących swobodnie (T301/L1/OPT/lampy/strefa PCB) zachowane w
  okolicach 8–13 mm (nie ściśle wymuszone skryptem — sprawdzone wizualnie
  na renderze, patrz "Weryfikacja" niżej).

**Trasa sygnału i listwa C (poprawka).** Listwa C (crossfeed, R401–R406/
C401–C404) przesunięta **na prawo od RV1** (między RV1 a prawą ścianą,
blisko trasy z RCA) — poprzednio leżała na lewo od RV1, co oznaczało
krzyżowanie się trasy sygnału z frontem płyty. Nowa trasa: RCA (tył,
środek-prawo) → wzdłuż prawej krawędzi obudowy → listwa C → RV1 → ECC82.
Kabel ekranowany na całej tej trasie (podpisane na rysunku).

**Szyna masy (poprawka rysunku, aktualna wersja — patrz też "runda 2"
niżej).** Łamana **ortogonalna** (bez przekątnych): odcinek poziomy na
wysokości listw B (y=122) łączący wprost listwa B_L → listwa B_P, plus
pionowy odczep w x=178 do listwy A (y=122→70). Od listwy B_L dodatkowy
odcinek — korytarzem x≈101 mm (czysty prześwit między L1/T301 a T1, bez
przecinania żadnego transformatora/dławika) — do punktu ground breaker
**na PCB zasilacza, przy IEC** (aktualnie w ścianie lewej, front — patrz
"runda 2") — jedyny styk masy sygnałowej z chassis/PE, podpisane wprost
na rysunku ("masa sygnałowa ≠ chassis poza tym punktem").

**Weryfikacja (po poprawkach).** `layout_top.py` — wynik automatycznej
kontroli geometrii: **brak kolizji na górnej płycie, wszystko w
obudowie, odstępy lamp/trafo (≥35 mm między lampami, ≥25 mm lampa↔trafo)
oraz nowa reguła T301↔RV1/RCA/ECC82 (≥100 mm, liczone środek-środek)
zachowane** — najciaśniejszy margines to U2/U202↔OPT, 28,5 mm (zapas
3,5 mm nad wymogiem). `check.py` (schemat, bez zmian w tym kroku):
wszystkie asercje OK (58 sieci). ERC: **0 błędów, 0 ostrzeżeń** (bez
zmian względem stanu sprzed tej zmiany — rysunek montażowy nie dotyka
`headamp.kicad_sch`). Idempotencja `gen.py`: bez zmian (nie ruszany w tym
kroku). Render PNG obejrzany i poprawiony pod kątem kolizji etykiet
(m.in. opis strefy PCB zasilacza rozbity na krótki tytuł + osobny akapit,
żeby nie nachodził na etykietę L1; opis frontu rozbity na dwie linie,
żeby nie wychodził poza kadr; trasy masy/żarzenia/B+ poprowadzone poza
obrysami transformatorów zamiast po przekątnej przez nie).

**Poprawka R1/R201 (grid leak wejściowy).** W tabeli
`headamp/ref/layout_bom_montaz.md` R1 (470k, kanał L) i R201 (kanał P)
były błędnie przypisane do sekcji "między listwą A i B" (trasa sprzęgacza
driver→EL84). W rzeczywistości R1/R201 siedzą na węźle **siatki ECC82**
(między nóżką R2/C1 — pin 7 U1 unit A dla kanału L, pin 2 unit B dla
kanału P — a GND), elektrycznie niezwiązanym z sprzęgaczem C5/R6 po
stronie EL84. Poprawione: R1/R201 przeniesione do tabeli "na nóżkach
podstawek" (fizycznie: na listwie A przy wejściu siatki, albo wprost z
nóżki R2/C1 do szyny masy); sekcja "między A i B" zawiera już tylko
R6/R206 i C5/C205 — R7/R207 (grid stopper EL84) zostaje bez zmian na
nóżce EL84, jak poprzednio.

**Poprawki 2026-09-08, runda 2 (kolizja IEC, trasa żarzenia, szyna masy).**

1. **J1+F1 (IEC C14 + bezpiecznik) — kolizja z T301, przeniesione na
   ścianę lewą.** Gniazdo IEC z bezpiecznikiem ma korpus ~48×28 mm na
   ścianie i wchodzi ~30–35 mm w głąb obudowy (plus przewody) — w
   pierwotnej propozycji (ściana tylna, x≈42) kolidowało to z T301, który
   przy tej ścianie sięga do y=190. Skrypt dostał bryłę "głębokości" IEC
   48×35 mm włączoną do automatycznej kontroli kolizji. Rozważone warianty:
   (a) IEC na wysokości L1 (y≈65) + przesunięcie L1 w prawo — **odrzucony**:
   geometrycznie niewykonalny (L1, 55 mm szerokości, nie mieści się między
   krawędzią IEC a wymaganym 25 mm odstępem od U2 — dostępne miejsce to
   tylko 52 mm); (b) IEC z przodu ściany lewej (x=0, y≈6–54) +
   przesunięcie SW1/NE1 w prawo — **wybrany**. L1 zostaje bez zmian.
   Powód wyboru: najkrótsze i najprostsze prowadzenie przewodu sieciowego
   IEC(+F1) → SW1 → sieć ochronna (PCB) → T301, cały czas w obrębie strefy
   zasilania (x<100), bez zbliżania 230 V do frontu przy RV1 (x=140).
   Skutki uboczne: SW1 przesunięty z x=18 na x=58, NE1 z x=34 na x=80 (obie
   dalej na froncie, y=13, kolejność na panelu bez zmian: SW1→NE1→SW401→
   RV1→SW2→J403); C302/C303 (ilustracyjne elektrolity PCB zasilacza,
   pod płytą) przesunięte z y=45 na y=150 (nadal w strefie PCB, teraz pod
   T301) — poprzednia pozycja kolidowała wizualnie z etykietą nowego J1+F1.
2. **Trasa żarzenia (poprawka).** Korytarz między T301/L1 a T1 przesunięty
   z x≈98 na x≈101 (razem z odgałęzieniem szyny masy, patrz niżej — większy
   margines po przesunięciu L1... choć L1 finalnie zostało bez zmian,
   korytarz i tak przesunięty dla większego zapasu). Ważniejsza poprawka:
   odgałęzienie do U1 (ECC82, 178,45) **już nie schodzi przy RV1/wejściu**
   (dawna trasa: korytarz → y=45 → w prawo pod RV1/U1); teraz żarzenie
   idzie rzędem EL84 (y=90) od U2 do U202, a do U1 odczep **prosto w dół ze
   środka między EL84 (x=178, y=90→56)** — z dala od RV1 (x=140) i wejścia.
   Podpis na rysunku: "żarzenie DC – skręcona para, z dala od wejścia".
3. **Szyna masy — dostosowana do nowego IEC.** Odgałęzienie od listwy B_L
   do ground breakera zaktualizowane: korytarz x≈101 → y=45 → w lewo do
   x=20 → w dół do y=30 (wewnątrz nowej bryły J1+F1) — fizycznie
   najkrótsza droga do PCB zasilacza przy nowej pozycji IEC (ściana lewa,
   front), bez przecinania L1/T301/SW1.

**Weryfikacja (runda 2).** `layout_top.py`: kontrola geometrii automatyczna
— brak kolizji na górnej płycie (w tym nowa bryła głębokości J1+F1), wszystko
w obudowie, odstępy lamp/trafo i reguła T301↔RV1/RCA/ECC82 zachowane. Render
PNG obejrzany i poprawiony (etykieta szyny masy B_L→A→B_P podniesiona, żeby
nie nachodziła na opis listwy B_L; C302/C303 przesunięte, żeby nie nachodziły
na etykietę J1+F1). Zmiana nie dotyka `headamp.kicad_sch` / `gen.py` / ERC —
tylko rysunku montażowego i tego dokumentu.

### Uwagi do projektu PCB zasilacza (2026-09-08)
- T301 stoi na górnej płycie nad strefą PCB — śruby mocujące transformatora
  muszą minąć płytkę: przewidzieć wycięcia/otwory w PCB albo przesunąć
  płytkę ~30 mm w przód (poza obrys T301). Do rozstrzygnięcia przy projekcie.
- Crossfeed S1 — kontrolne liczby z niezależnej analizy węzłowej (źródło
  100 Ω, obciążenie 50 k): ON przesłuch −14 dB @100 Hz / −29 dB @1 kHz,
  strata wtrąceniowa 0,6–1,6 dB; OFF (S1 po stronie wyjścia) 0…−0,4 dB;
  stary wariant OFF (S1 na wejściu) dołek −1,6 dB w basie. `sim/crossfeed_sw.cir`
  do uruchomienia w ngspice, gdy będzie dostępny (brak na stacji Windows).
