# Projekt: lampowy przedwzmacniacz gramofonowy RIAA (stereo) — ustalenia

Stan na: 2026-08-25. Właściciel: Wiktoryn. Dokument jest "pamięcią" projektu —
przy kontynuacji w nowej sesji podać ten plik Claude'owi.

## Kontekst systemu (docelowo trzy pudełka, w 100% analogowe)

1. **RIAA phono stage** (ten projekt) — schemat gotowy, rev E w KiCad 7.
2. **Końcówka mocy lampowa** — następna w kolejności; z potencjometrem
   głośności na wejściu (Alps RK27 log stereo), który po zbudowaniu
   przedwzmacniacza zostanie trymerem czułości. Wskaźniki wychyłowe (VU,
   podświetlane na ciepło, z Aliexpress) napędzane biernie z wyjść
   głośnikowych (mostek z diod germanowych/Schottky + trymer). Czułość
   projektować na ~0,4–0,5 V pełnej mocy.
3. **Przedwzmacniacz liniowy** — na końcu: selektor wejść, głośność, balans,
   mono, filtry rumble/scratch, barwa (Baxandall + stopień odrabiający).
Kolejność budowy wynika z tego, że Sony (obecna integra tranzystorowa) nie
ma pewnego MAIN IN — sprawdzić; jeśli ma, przedwzmacniacz może być drugi.

Obecny sprzęt: gramofon Technics (wkładka MM), tani RIAA tranzystorowy
(do porównań A/B), integra Sony. Lampowy RIAA wpinać w wejście LINIOWE
(AUX/CD), nigdy w PHONO (podwójna korekcja!).

## Układ elektryczny RIAA (rev E)

- Topologia: 2 stopnie wzmocnienia ECC83 + wtórnik katodowy ECC82,
  pasywna korekcja RIAA między stopniami (3180/318/75 µs).
  V1 = ECC83 kanał L (obie połówki), V2 = ECC83 kanał R, V3 = ECC82
  (połówka A → L, połówka B → R). Wzmocnienie ~40 dB @ 1 kHz, Zwy ~1 kΩ.
- Wejście MM: 47k ∥ 150p. (Opcja na przyszłość, NIEzdecydowana: przełącznik
  MM/MC/PIEZO — MC przez transformatory SUT 1:10 w mu-metalu, PIEZO przez
  tłumik ~20 dB + obciążenie 47k; na razie czyste MM.)
- Sieć RIAA (na kanał): szeregowo 255k (dodaje się do Zwy stopnia 1 ≈39k →
  294k), boczniki: 3n3 ∥ (33k + 9n62) do masy; 9n62 = 8n2+1n2+220p, 1% PP.
  Grid leak 1M, grid stoppery 470R/1k przy samych pinach lamp.
- Punkty pracy: stopnie ECC83: Ra 100k, Rk 1k5 ∥ 220µ, ~1 mA.
  Wtórnik ECC82: Rk 2k2 + 47k (grid leak 1M do odczepu), ~2,4 mA, Vk ~118 V.
  Wyjście przez 2µ2/400V, bleeder 470k.
- Zasilacz anodowy: 230 V sekundar → mostek UF4007 (+ snubber RC 470R+10n/1kV
  przez uzwojenie) → C9 100µ/500V → **L1 dławik 10H/100mA** (opcja budżetowa:
  R 1k 5W zamiast — wtedy większe tętnienia) → C10 100µ/500V = B+3 (~300 V
  z dławikiem, ~285 V z rezystorem).
  **B+ rozdzielone per kanał**: z B+3 dwie gałęzie 10k→47µ (B+2L/R) →
  22k→47µ (B+1L/R). Bleedery 470k/1W na każdym z 4 kondensatorów gałęzi.
  C9+C10 przewidziane jako kubek wielosekcyjny 100+100µF/500V (JJ) na płycie
  górnej; obejma z przekładką izolacyjną (masa ≠ chassis!).
- Transformator (kupiony w sklepie): EI84/42, 100 VA, prim. 230 V (bezp.
  T500mA), wtórne: 230 V/0,3 A (anodowe), 0–6,3–7 V/4 A (żarzenie z uzwojenia
  7 V; odczep 6,3 V niepodłączony), 24 V/0,1 A (rezerwa na polaryzację siatek
  w przyszłej końcówce — niepodłączone).
- Żarzenie: uzwojenie 7 V → mostek 1N5822 → 10000µ/16V (=V_RAW, ~9 V) →
  470µ → **LD1085** (LDO! LM317 ma za duży dropout przy 9 V surowego;
  240R/976R → 6,33 V) na radiatorze wciskanym w PCB (NIE do płyty górnej —
  blaszka = VOUT). 6,3 V DC / 0,9 A (3 lampy, piny 4+5 równolegle).
  Przy głębokich zapadach sieci LDO może na moment wyjść ze stabilizacji —
  niegroźne dla żarzenia. Przekaźniki K1/K2/K3: cewki 9 V (zasilane z V_RAW).
  Żarzenie podniesione do +50 V (ELEV: dzielnik 470k/100k z B+3 + 22µ) —
  przydźwięk i Vhk wtórnika. Przewody żarzenia ZAWSZE skręcona para.
- Automatyczne rozładowanie: K1 (przekaźnik 9 V na V_RAW, styki min. 250 V,
  dioda gasząca) — przy zaniku sieci styk NC łączy B+3 z R24 4k7/10W → <50 V
  w ~15 s. Wszystkie kondensatory HT rozładowują się przez łańcuch;
  bleedery 470k to niezależna, wolna (minuty) druga linia. Przy włączeniu K1
  zapina się zanim B+ wzrośnie (żarzenie wstaje szybciej). MIMO TO: przed
  pracą zawsze pomiar woltomierzem na każdej sekcji.
- Wyciszenie wyjść: K2/K3 (Relay SPDT 9 V) zwierają wyjścia L/R do masy;
  Q1 2N7000 z RC 470k/220µ (D 1N4148 do szybkiego rozładowania przy
  wyłączeniu) otwiera po ~20 s od włączenia → brak stuków i szumu rozgrzewki,
  natychmiastowy mute przy wyłączeniu.
- Sieć: IEC z bezpiecznikiem T500mA (w L, przed wyłącznikiem) → SW1
  dwubiegunowy toggle (L i N, metalowa dźwignia, 250 VAC) → NTC 10R (inrush)
  → transformator. Warystor S14K275 przez L–N za wyłącznikiem (opcja: +100n
  X2). NE1 neonówka + 220k przez uzwojenie pierwotne = kontrolka w oprawce
  "jewel" (bursztyn) na froncie, osobno od wyłącznika. Świeci = trafo pod
  napięciem.

## Masa i bezpieczeństwo (NIEnegocjowalne)

- PE z IEC → osobna śruba M4 na płycie górnej (podkładka ząbkowana, nakrętka).
- Masa sygnałowa (GND) = osobna sieć wewnątrz; z chassis łączy się w JEDNYM
  punkcie przy gniazdach wejściowych przez **ground breaker**: 10R/5W ∥ dwie
  1N5408 antyrównolegle ∥ 100n/630V. Cisza pętli masy + przy usterce diody
  zwierają do PE i bezpiecznik działa.
- Gniazda RCA izolowane od metalu. Zacisk masy gramofonu → GND (nie chassis).
- KAŻDY dotykalny/sieciowy element metalowy (płyta górna, tylna blacha,
  front) → oczko na PE. Przewody 230 V: skrętka, podwójna izolacja,
  termokurczka na terminalach, z dala od wejść.
- Napięcia do ~330 V DC — śmiertelne. Praca dopiero po pomiarze <50 V.

## Obudowa (seria trzech urządzeń w tym samym stylu)

- Format: szerokość/głębokość jak standardowy sprzęt audio (~430×300).
  Wymiary finalne TBD — od nich DXF.
- Boki + spód: drewno (robi znajomy). Spód z tulejkami gwintowanymi (M3/M4)
  pod PCB zasilacza, pola otworów wentylacyjnych pod lampami i pod strefą
  zasilacza, wysokie nóżki; pod PCB zasilacza cienka blaszka/mata niepalna.
- Góra: stal nierdzewna lustrzana ("super mirror" No.8, 1,5 mm, cięta laserem
  z folią). Na wierzchu: 3 lampy (gniazda od spodu, szczelina wokół bańki =
  kominek), kubki elektrolitów HT, transformator (dzwon lub kubek ekranujący;
  transformator w rogu, ≥25 cm od lamp wejściowych). Góra = chassis
  elektryczne.
- Tył: blacha malowana proszkowo (2 mm alu) — RCA (izolowane), IEC+bezpiecznik,
  zacisk masy; szczeliny wentylacyjne (wylot) + siatka od środka.
- Przód: szczotkowana nierdzewka, wpuszczona/licowana w drewno (frez),
  mocowanie na wklejanych szpilkach M3 od tyłu (zero widocznych śrub).
  Na RIAA tylko: toggle + jewel neonówki. Wspólny wzór dla trzech urządzeń
  (ten sam prostokąt, promień naroży, czcionka — Futura/DIN, wersaliki).
- Oznaczenia frontu: znakowanie laserem fiber (annealing — czarne napisy na
  szczotce). Nie kwas, nie sitodruk.
- Wentylacja: wlot dołem, wylot tyłem + kominki lamp; ~15 W strat, bez
  wiatraków. Radiator LD1085 przy tylnych szczelinach,
  elektrolity po chłodnej stronie; 3–4 cm luzu nad PCB.

## Montaż

- Tor audio: turret board (tulejki 2 mm w laminacie), zawieszony na
  przedłużonych śrubach gniazd lamp (tulejki dystansowe 15–20 mm).
  Grid stoppery lutowane wprost na pinach gniazd. Kanały L/R lustrzanie.
  Gniazda: ceramiczne noval z kołnierzem, śruby imbusowe M3 nierdzewne.
- Zasilacz + automatyka (K1/K2/K3, LD1085, mostki, NTC): jedno PCB na spodzie,
  prawy tylny róg (przy IEC i trafo, daleko od wejść). Odstępy ścieżek ≥2,5 mm
  przy 300 V. PCB zaprojektuje Claude z tego samego projektu KiCad.
- Masa: szyna/gwiazda na turret boardzie, punkt styku z chassis przez ground
  breaker przy wejściach. Kubki: sekcje minusów w jednym punkcie.
- Sieć 230 V: bez PCB, na konektorach, w rogu zasilacza.

## Pliki projektu

- `riaa_preamp.kicad_sch` — schemat (KiCad 7, symbole osadzone, otwiera się
  bez bibliotek). Generowany skryptem `gen.py` (+ `symlib.py`, `check.py` —
  weryfikacja netlisty). Rev E = finalna wersja przed budową.
- `riaa_preamp.pdf` — render do czytania/druku.
- TBD po wymiarach: DXF płyt (góra lustrzana, tył, front ×3), layout PCB
  zasilacza, rysunek rozmieszczenia, BOM zakupowy.

## Oświetlenie lamp (opcja, oba warianty)

Miniaturowe żarówki 6,3 V/0,1 A (T1¼, E5/E10) pod podstawkami — światło przez
otwór po środkowym styku "shield" (nieużywany w noval; usunąć lub podstawka
z pustą tulejką) + przez szczelinę wokół bańki. Jasność: szeregowy REGULOWANY
rezystor drutowy 0–22R/10 W (z obejmą), strojony od środka. Wyłącznik SPST
(OŚWIETLENIE) na tylnej ściance. Przewód: skrętka w ekranie, ekran do GND
tylko od strony zasilacza. Zasilanie: rev E — wolny odczep 6,3 V AC;
rev P — uzwojenie 6,3 V EZ81 pod warunkiem dowiązania go do GND zamiast do
katody (Vhk = −300 V, limit EZ81 500 V) — inaczej oświetlenie na +300 V.
Montaż podstawek: otwór w płycie 26–28 mm, podstawka pod płytą na tulejkach
5–8 mm → pierścieniowa szczelina = kominek wentylacyjny + poświata
(podstawka przykręcona na styk do płyty zamyka otwór — tak NIE robić).

## TODO: filtrowanie zakłóceń (do ogarnięcia przed/na etapie budowy)

Temat otwarty — zakłócenia z dwóch kierunków, oba do rozwiązania:

**Z sieci 230 V (przewodzone):** obecnie mamy warystor + NTC + snubber RC na
uzwojeniu HT. Do dodania pełny filtr przeciwzakłóceniowy EMI na wejściu:
najprościej gniazdo IEC ze zintegrowanym filtrem (np. Schaffner FN9222,
Schurter 5110 — dławik wspólny + kondensatory X2/Y2 w jednej puszce,
prąd 1–2 A wystarczy) albo osobny moduł filtra za wyłącznikiem.
Uwaga na kondensatory Y (L→PE, N→PE): świetnie tłumią zakłócenia
wspólne, ale wpuszczają mały prąd upływu do PE — przy naszym ground
breakerze to nieszkodliwe (upływ idzie do chassis/PE, nie do masy
sygnałowej), lecz filtr MUSI być certyfikowany (X2/Y2), nie składany
z przypadkowych kondensatorów. Rozważyć też: osobne odkłócenie od strony
DC (perełki ferrytowe na wyjściach zasilacza do B+ i żarzenia).

**Z "powietrza" (RF/pola):** wejścia MM to najczulszy punkt — 5 mV przy
47 kΩ łapie radio, ładowarki, LED-y i telefon na obudowie. Warstwy obrony:
grid stoppery już są (470R/1k przy pinach); do rozważenia dodatkowo małe
perełki ferrytowe lub RC (np. 1k + 100p) bezpośrednio na gniazdach RCA
wejściowych; przewody wejściowe wewnątrz obudowy ekranowane (ekran do GND
tylko od strony gniazd); metalowa górna płyta + tylna blacha robią klatkę —
sprawdzić po złożeniu, czy drewniane boki nie wpuszczają RF (jeśli tak:
samoprzylepna folia miedziana/aluminiowa na wewnętrznych stronach desek,
połączona z PE w jednym punkcie); kabel od gramofonu możliwie krótki,
zacisk masy ramienia podłączony. Test praktyczny po budowie: telefon
z włączonym transferem danych położony na obudowie + max głośność —
cisza oznacza zdany egzamin.

Decyzje do podjęcia przy budowie: filtr IEC zintegrowany czy osobny moduł;
czy foliować drewno; czy RC na wejściach od razu, czy dopiero jeśli
słychać RF (wersja purystyczna: dodawać tylko to, co potrzebne).

## Wariant purystyczny (zero półprzewodników) — opcja do decyzji

Tor audio już jest w 100% lampowo-bierny; zmiany dotyczą wyłącznie zasilacza.

**Prostownik anodowy:** lampa EZ81/EZ80 (lub GZ34). Wymaga INNEGO trafo:
uzwojenie anodowe z odczepem środkowym (2×230 V) + uzwojenie żarzenia
prostownika. Bonus: naturalny miękki start (katoda grzeje się ~15 s,
B+ wstaje po lampach audio) — znika potrzeba układu wyciszania. Filtr LC
(dławik obowiązkowy). Kupione trafo EI84 NIE pasuje do tego wariantu.

**Żarzenie — prostowanie lampą NIE działa (rachunek):** lampy prostownicze
to wysokie V / małe I; przy 6,3 V/0,9 A spadek ~20 V na bańce oznacza
uzwojenie ~30 V i ~50 W strat (plus żarzenie samych prostowników), żeby
dostarczyć 5,7 W. Nikt tego nigdy nie robił. Dwie realne opcje:
1. **AC + humdinger**: skręcona para, potencjometr 100R między końcami
   żarzenia (suwak do masy/elewacji, strojenie na minimum brumu), elewacja
   +50 V zostaje. Klasyka (Marantz 7); ryzyko resztkowego przydźwięku.
2. **Bateria (era-correct "bateria A")**: AGM/żel 6 V / 10–12 Ah w obudowie.
   DC idealnie czyste (zero tętnień). 6–7 h grania przy rozładowaniu do 50%.
   Rygory: TYLKO AGM/żel (szczelny), bezpiecznik BEZPOŚREDNIO przy zacisku
   (ołów oddaje setki A w zwarcie), obejma do dna (masa sprzężona sztywno =
   + stabilność, − mikrofonowanie), z dala od ciepła lamp.
   Ładowanie: ładowarka ZEWNĘTRZNA (krzem poza obudową — nie jest częścią
   urządzenia), etapowa z trybem float 6,75–6,9 V — akumulator może wisieć
   na buforze bez ograniczeń (jak w UPS). Gniazdo ładowania z tyłu.
   Przełącznik dwupozycyjny PRACA/ŁADOWANIE na froncie (2-biegunowy, 6 V DC,
   bez trybu trzeciego — float załatwia sprawę).
   **Strażnik baterii**: przekaźnik z cewką 230 V AC za wyłącznikiem
   sieciowym, styk szeregowo bateria→żarzenie — sieć wyłączona = bateria
   odcięta (nie da się jej zapomnieć w pozycji PRACA). Drugi styk (NC) tego
   samego przekaźnika = rozładowanie B+ (funkcja K1 bez diody gaszącej;
   dla cewki AC snubber RC zamiast diody).
   **Woltomierz na froncie**: miernik wychyłowy + rezystor-mnożnik, wpięty
   ZA przekaźnikiem (wskazuje tylko podczas grania — brak stałego poboru);
   zielona strefa 6,0–6,4 V jako "wskaźnik paliwa".

**Reszta zamian:** K2/K3+Q1 (muting) → zbędne przy wolnym starcie EZ81
(ew. przekaźnik termiczny Amperite, NOS). NTC → rezystor drutowy 22–47R
w pierwotnym albo nic. Warystor → wypada (ceramika półprzewodnikowa).
Ground breaker: bez diod — 10R∥100n (kompromis) albo masa na sztywno do
chassis przy wejściach (jak vintage). Neonówka, snubbery RC, bleedery,
dławiki — zostają (czysty old-tech).

**Rekomendacja:** RIAA budować wg rev E (krzem tylko usługowo w zasilaczu);
wariant purystyczny rozważyć dla końcówki mocy (GZ34 = klasyka, żarzenie AC
tam bezproblemowe, trafo z odczepem i tak potrzebne). Bateria żarzenia —
najciekawsza do ew. "rev P" tego RIAA, jeśli przyjdzie ochota na budowę #2.

## Otwarte decyzje

- Przełącznik wkładek MM/MC/PIEZO (SUT + tłumik) — do decyzji; na razie MM.
- Dławik L1 vs rezystor 1k 5W — budżet.
- Rev E: własny symbol trafo EI84, zasilacz przerysowany (czytelny układ).
- Wariant purystyczny (patrz sekcja) — decyzja: rev E teraz, puryzm ew. później/w końcówce.
- Wymiary obudowy — po rozmowie ze stolarzem.
- Czy Sony ma PRE OUT/MAIN IN → kolejność budowy pudełka 2 i 3.
