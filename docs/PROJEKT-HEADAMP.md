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
  głośności przy przełączaniu — normalny). **Implementacja na schemacie
  (Etap 6, SW401):** tor prosty (R401∥C401/R402∥C402) jest ZAWSZE
  wpięty (bypass przełącznika); SW401 przełącza tylko dopływ sygnału do
  gałęzi krzyżowej (patrz "Decyzje - Etap 6" niżej) - `sim/crossfeed.cir`
  jest źródłem prawdy dla dokładnej topologii.
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

## Stan realizacji (2026-09-08, po Etapie 6)
- Schemat generowany skryptem **`headamp/gen.py`** (+ `symlib.py` +
  `check.py`, wzor riaa/) - **zrodlo prawdy = gen.py, NIE edytowac
  `headamp.kicad_sch` recznie**. UUID deterministyczne (uuid5) -
  regeneracja jest idempotentna (git diff pusty przy dwoch uruchomieniach).
- Kanał L + kanał P + zasilacz + crossfeed S1 + gniazda WE/WY
  **kompletne, layout w ramkach modułów**. ERC: ostrzeżenia oczekiwane
  (4): missing_unit x3 (U1/U2/U202 - unity grzania nie są rysowane,
  DECYZJA) + multiple_net_names ELEV/HEAT_B (zamierzone, jak w
  common/riaa); **plus 3 błędy `missing_power_pin`** (te same 3 unity -
  konsekwencja typu pinu `power_in` w bibliotece Valve, patrz "Decyzje -
  Etap 6" i TODO - OTWARTE, wymaga decyzji użytkownika czy akceptować
  formalnie niezerowy ERC, czy przywrócić unity grzania).
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

## TODO (aktualizacja po Etapie 5b - skreslone zrobione)
- ~~gen.py + check.py (kanał L port 1:1)~~ ZROBIONE (Etap 0-1).
- ~~Kanał P~~ ZROBIONE (Etap 5a).
- ~~Zasilacz (B+, żarzenie, K1, ground breaker)~~ ZROBIONE (Etap 5b).
- ~~Crossfeed S1 (DPDT) + gniazda WE/WY na schemacie~~ ZROBIONE (Etap
  6/A-B, patrz sekcja "Decyzje - Etap 6" niżej).
- ~~Estetyka schematu (Etap 6)~~ ZROBIONE (przegląd render -> poprawki
  pól ref/value/tolerance w gen.py: domyślne offsety 3-liniowe, F1/SW1,
  J1/PWR_FLAG/Earth_Protective, R301/NE1, R303/L1, ground breaker).
  Layout w ramkach (Etap A) rozwiązał też ciasnotę rzędu grzania - rząd
  usunięty (żarniki nie są rysowane), moduły czytelne w ramkach.
- **OTWARTE (do decyzji użytkownika): ERC pokazuje 3 błędy
  `missing_power_pin`** (U1/U2/U202) - patrz "Decyzje - Etap 6" niżej,
  ostatni punkt. Do rozstrzygnięcia: zaakceptować błędy jako świadomą
  konsekwencję "żarniki nie są rysowane", czy przywrócić unity grzania
  (z realnym okablowaniem) żeby mieć ERC=0 błędów dosłownie.
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

**C. Crossfeed S1 - przełączany DPDT.** Element `SW401`
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

**F. Rozmiar arkusza: A2 zostaje** (DECYZJA). Treść po Etapie 6 zajmuje
ok. 400×428 mm (blisko górnej granicy A2 w orientacji poziomej,
594×420mm - jak w commicie sprzed tego etapu, `PSU_DY` zostawiony bez
zmian: część współrzędnych pól/tekstów w sekcji zasilacza jest zapisana
jako już-wyliczone wartości absolutne, nie "baza + PSU_DY", więc
zmniejszenie tej stałej rozjechałoby je względem reszty bloku - zbyt
ryzykowne dla zysku kilkudziesięciu mm). A3 (420×297) odpada z powodu
wysokości treści (428 mm > 297 mm) niezależnie od szerokości. Pusta
przestrzeń po prawej stronie arkusza (moduły kończą się ok. x=400 z 594)
pozostaje - do ew. dalszego wykorzystania (większy WYJŚCIE, adnotacje).
