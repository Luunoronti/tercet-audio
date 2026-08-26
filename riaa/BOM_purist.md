# TERCET — RIAA, wariant purystyczny (rev P) — BOM

Lista elementów wariantu **zero półprzewodników**.
Źródło: `riaa_preamp_purist.kicad_sch`, stan na 2026-08-26.

## Lampy

| Ilość | Element | Ref | Uwagi |
|---|---|---|---|
| 2 | ECC83 / 12AX7 | V1, V2 | tor audio, po jednej na kanał; egzemplarze o niskim szumie i mikrofonowaniu (selekcja „phono") |
| 1 | ECC82 / 12AU7 | V3 | wtórniki katodowe (połówka A → L, B → R) |
| 1 | EZ81 / 6CA4 | V4 | prostownik anodowy; JJ produkuje nowe |
| 4 | gniazdo noval B9A | — | ceramiczne z kołnierzem, montaż od spodu chassis, śruby M3 imbus nierdzewne |

## Transformator i dławik

| Ilość | Element | Ref | Uwagi |
|---|---|---|---|
| 1 | transformator sieciowy „lampowy" | T1 | prim. 230 V; wtórne: **2×230 V / min. 0,15 A (z odczepem środkowym!)** + 6,3 V / 1 A (żarzenie EZ81). ⚠ Kupione trafo EI84 100VA **nie pasuje** (brak odczepu) — dotyczy tylko rev E |
| 1 | dławik 10 H / 100 mA | L1 | DCR ≤ 200 Ω; filtr LC w tym wariancie **obowiązkowy** |

## Rezystory — tor audio

Metalizowane 0,6 W, o ile nie zaznaczono inaczej.

| Ilość | Wartość | Tol. | Moc | Ref | Funkcja |
|---|---|---|---|---|---|
| 2 | 47k | 1% | 0,6 W | R1, R101 | obciążenie wejścia MM |
| 2 | 470R | 5% | 0,6 W | R2, R102 | grid stopper wejściowy (lutować wprost na pinie gniazda) |
| 4 | 100k | 1% | **1 W** | R3, R9, R103, R109 | anodowe (1 W dla zapasu napięciowego) |
| 4 | 1k5 | 1% | 0,6 W | R4, R10, R104, R110 | katodowe stopni wzmacniających |
| 2 | 255k | **1%** | 0,6 W | R5, R105 | szeregowy RIAA (E96; alternatywnie 249k + 6k2) |
| 2 | 33k | **1%** | 0,6 W | R6, R106 | RIAA (bocznik szeregowy) |
| 4 | 1M | 5% | 0,6 W | R7, R11, R107, R111 | grid leak |
| 4 | 1k | 5% | 0,6 W | R8, R12, R108, R112 | grid stopper (na pinach gniazd) |
| 2 | 2k2 | 1% | 0,6 W | R13, R113 | katodowe wtórników (bias tap) |
| 2 | 47k | 1% | **1 W** | R14, R114 | katodowe wtórników (obciążenie) |
| 2 | 470k | 5% | 0,6 W | R15, R115 | upływowe wyjścia |

## Rezystory — zasilacz i pomocnicze

| Ilość | Wartość | Tol. | Moc | Ref | Funkcja |
|---|---|---|---|---|---|
| 2 | 10k | 5% | 1 W | R18, R118 | dropper B+3→B+2 (po jednym na kanał) |
| 2 | 22k | 5% | 1 W | R19, R119 | dropper B+2→B+1 |
| 4 | 470k | 5% | 1 W | R26, R27, R126, R127 | bleedery (wolne rozładowanie) |
| 1 | 470k | 5% | 1 W | R22 | dzielnik elewacji żarzenia (+50 V) |
| 1 | 100k | 5% | 0,6 W | R23 | dzielnik elewacji |
| 1 | 4k7 | 5% | 10 W drutowy | R24 | rozładowanie B+ (styk NC K1) |
| 1 | 10R | 5% | 5 W drutowy | R25 | ground breaker |
| 1 | 22R | 5% | 5 W drutowy | R34 | ogranicznik rozruchu w pierwotnym |
| 1 | 220k | 5% | 0,6 W | R32 | szeregowy neonówki |
| 1 | 100R | 5% | 0,6 W | R33 | snubber cewki K1 |
| 1 | wg miernika | 1% | 0,6 W | R30 | mnożnik woltomierza M1 (pełna skala ~8 V) |

## Kondensatory — tor audio

| Ilość | Wartość | Tol. | Typ | Ref | Funkcja |
|---|---|---|---|---|---|
| 2 | 150p | 2% | mika / C0G | C1, C101 | obciążenie wkładki MM |
| 4 | 220µ / 25 V | ±20% | elektrolit | C2, C6, C102, C106 | bocznikowanie katod |
| 4 | 100n / 630 V | 5% | polipropylen | C3, C7, C103, C107 | sprzęgające |
| 2 | 3n3 | **1%** | polipropylen | C4, C104 | RIAA (1% obowiązkowo) |
| 2 | 9n62 | **1%** | polipropylen | C5, C105 | RIAA; złożyć: 8n2 + 1n2 + 220p równolegle (wszystkie 1%) |
| 2 | 2µ2 / 400 V | 5% | polipropylen | C8, C108 | wyjściowe |

## Kondensatory — zasilacz

| Ilość | Wartość | Tol. | Typ | Ref | Funkcja |
|---|---|---|---|---|---|
| 1 | 47µ / 500 V | ±20% | elektrolit | C9 | **pierwszy po EZ81 — max 50 µF, limit lampy! Nie zwiększać** |
| 1 | 100µ / 500 V | ±20% | elektrolit | C10 | za dławikiem (B+3) |
| 4 | 47µ / 400 V | ±20% | elektrolit | C12, C13, C112, C113 | filtry B+ per kanał |
| 1 | 22µ / 100 V | ±20% | elektrolit | C17 | elewacja żarzenia |
| 1 | 100n / 630 V | 10% | polipropylen | C18 | ground breaker |
| 1 | 100n / 630 V | 10% | polipropylen | C21 | snubber cewki K1 |

> C9+C10 opcjonalnie jako kubek wielosekcyjny 50+100 µF / 500 V na płycie
> górnej — obejma z przekładką izolacyjną (masa ≠ chassis).

## Żarzenie z baterii

| Ilość | Element | Ref | Uwagi |
|---|---|---|---|
| 1 | akumulator AGM/żel 6 V / 10–12 Ah | BT1 | typ „UPS/alarm"; **tylko szczelny AGM lub żel** |
| 1 | bezpiecznik 2 A zwłoczny + oprawka | F2 | montaż **bezpośrednio przy zacisku baterii** |
| 1 | obejma / rama baterii | — | sztywne skręcenie z dnem obudowy |
| 1 | ładowarka buforowa 6 V AGM | — | **zewnętrzna**, etapowa z trybem float 6,75–6,9 V (nie wchodzi w BOM urządzenia) |

## Automatyka / sterowanie

| Ilość | Element | Ref | Uwagi |
|---|---|---|---|
| 1 | przekaźnik DPDT, cewka 230 V AC | K1 | np. Finder 40.52, Relpol R2; styki min. 250 V ze zdolnością łączenia DC; gniazdo + zatrzask |
| 1 | wyłącznik dźwigniowy sieciowy | SW1 | DPST/DPDT 250 V AC 3 A, metalowa dźwignia (front) |
| 1 | przełącznik PRACA/ŁADOWANIE | SW2 | DPDT 6 A, dźwigniowy (front); przełącza baterię: lampy / gniazdo J6 |
| 1 | neonówka NE-2 + oprawka „jewel" | NE1 | bursztynowa (front) |
| 1 | woltomierz wychyłowy | M1 | zakres ~8 V DC (lub 100 µA + R30); zaznaczyć strefę 6,0–6,4 V (front) |

## Złącza / mechanika / sieć

| Ilość | Element | Ref | Uwagi |
|---|---|---|---|
| 4 | gniazdo RCA | J1–J4 | **izolowane od chassis** (podkładki) |
| 1 | gniazdo IEC C14 z szufladką bezpiecznika | J5 | tylna ścianka |
| 1 | bezpiecznik T500mA (5×20, zwłoczny) | F1 | w L, przed SW1 |
| 1 | złącze zaciskowe 2-pin | J6 | ładowanie 6 V (tył); biegunowość opisać na panelu |
| 1 | zacisk masy gramofonu | — | śruba radełkowana; masa gramofonu → GND, nie chassis |
| — | przewód żarzenia | — | skręcona para, min. 1 mm² (0,9 A) |
| — | turret board, tulejki, dystanse | — | wg ustaleń montażowych (`docs/PROJEKT-RIAA.md`) |

## Oświetlenie lamp (opcja dekoracyjna)

| Ilość | Element | Ref | Uwagi |
|---|---|---|---|
| 3 | żarówka miniaturowa 6,3 V / 0,1 A | LA1–LA3 | T1¼ / trzonek E5 lub E10; pod podstawkami lamp audio (przez otwór po środkowym styku „shield") |
| 3 | oprawka E5/E10 | — | montaż pod podstawką |
| 1 | rezystor drutowy **regulowany** 0–22 Ω / 10 W | R35 | z obejmą/suwakiem; szeregowo — jasność ustawiana **od środka**, raz na stałe |
| 1 | wyłącznik SPST | SW3 | tylna ścianka: OŚWIETLENIE ON/OFF |
| — | przewód: skrętka w ekranie | — | ekran do GND **tylko z jednej strony** (od zasilacza); trasa po kątach, z dala od wejść |

**Zasilanie:** rev E — odczep 6,3 V AC trafo (izolowany od DC żarzenia).
Rev P — uzwojenie 6,3 V EZ81, **warunek:** koniec uzwojenia dowiązać do GND
zamiast do katody (Vhk EZ81 = −300 V, w limicie 500 V) — inaczej okablowanie
oświetlenia siedzi na +300 V!

**Montaż pod kominek + poświatę:** otwór w płycie 26–28 mm (większy niż
bańka ~22 mm), podstawka **pod** płytą na tulejkach dystansowych 5–8 mm →
pierścieniowa szczelina wokół szkła przepuszcza powietrze i światło;
pierścień ozdobny maskuje krawędź otworu. Środkowy styk „shield" podstawki
(nieużywany przez lampy noval) usunąć lub wybrać podstawkę z pustą tulejką.

## Uwagi końcowe

1. **Ground breaker bez diod** (10R ∥ 100n) — kompromis wariantu purystycznego;
   alternatywa vintage: masa na sztywno do chassis przy gniazdach wejściowych.
2. Napięcia robocze kondensatorów jak w tabelach (400/500/630 V) — nie schodzić niżej.
3. **Tolerancje:** 1% tam, gdzie wartość ustala korekcję lub punkt pracy
   (RIAA — obowiązkowo; katody/anody — dla powtarzalności kanałów);
   5% dla grid stopperów, upływowych, dropperów i bleederów; elektrolity ±20%
   (wartości filtrów mają duży zapas). Elementy RIAA kupić po kilka sztuk
   i sparować miernikiem między kanałami.
4. ⚠ **Napięcia do ~330 V DC.** Przed pracą odczekać na rozładowanie (K1/R24 +
   bleedery) i sprawdzić woltomierzem każdą sekcję (<50 V).
