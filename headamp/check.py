"""Weryfikacja netlisty headamp - kanal L (SE EL84 trioda + 1/2 ECC82).
Wzorowane na riaa/check.py. Wejscie: headamp/headamp.net
(kicad-cli sch export netlist --format kicadsexpr -o headamp.net headamp.kicad_sch).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import symlib
import check_geom

NETFILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'headamp.net')
SCHFILE = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), 'headamp.kicad_sch')

tree, _ = symlib.parse(symlib.tokenize(open(NETFILE, encoding='utf-8').read()), 0)
nets = {}
node2net = {}
for n in tree:
    if isinstance(n, list) and n[0] == 'nets':
        for net in n[1:]:
            if not (isinstance(net, list) and net[0] == 'net'):
                continue
            name = None
            members = []
            for e in net:
                if isinstance(e, list) and e[0] == 'name':
                    name = symlib.unq(e[1])
                if isinstance(e, list) and e[0] == 'node':
                    ref = pinn = None
                    for f in e:
                        if isinstance(f, list) and f[0] == 'ref':
                            ref = symlib.unq(f[1])
                        if isinstance(f, list) and f[0] == 'pin':
                            pinn = symlib.unq(f[1])
                    members.append((ref, pinn))
            for m in members:
                node2net[m] = name
            nets[name] = members


def N(ref, pin):
    return node2net.get((ref, str(pin)), '<<UNCONNECTED %s.%s>>' % (ref, pin))


fails = []


def same(*nodes):
    names = {N(r, p) for r, p in nodes}
    if len(names) != 1:
        fails.append('NOT SAME NET: ' + ', '.join('%s.%s=%s' % (r, p, N(r, p)) for r, p in nodes))


def diff(a, b):
    if N(*a) == N(*b):
        fails.append('UNEXPECTED SHORT: %s and %s on %s' % (a, b, N(*a)))


# =======================================================================
#  KANAL (L, P) - funkcja parametryzowana, wzor: driver 1/2 ECC82 (U1)
#  + EL84 (elref) + OPT (tref) + potencjometr podwojny RV1 (unit ppins).
#  Kanal L: U1 unit A (pin6=A,7=G,8=K), RV1 unit1 (1/2/3), U2, T1.
#  Kanal P: U1 unit B (pin1=A,2=G,3=K), RV1 unit2 (4/5/6), U202, T201.
#  (Etap 5a, DECYZJA RV1 = potencjometr podwojny R_Potentiometer_Dual_Separate
#  - patrz docs/PROJEKT-HEADAMP.md.)
# =======================================================================

def chan(rn, sfx, ppins, u1pins, elref, tref, swref, off):
    A, G, K = u1pins
    p1, p2, p3 = ppins

    # wejscie -> RV1 (glosnosc) -> C1 -> siatka drivera (R2 stopper)
    same(('RV1', p2), (rn('C1'), '1'))
    same((rn('C1'), '2'), (rn('R1'), '1'), (rn('R2'), '1'))
    same((rn('R2'), '2'), ('U1', G))                            # R2 -> siatka U1

    # katoda drivera: R3 (1k5 na stale) + C2 (1u na stale) + SW -> C3 (100u)
    same(('U1', K), (rn('R3'), '1'), (rn('C2'), '1'), (swref, '1'))
    same((swref, '2'), (rn('C3'), '1'))                         # S w galezi C3 (100u)

    # anoda drivera: R4 (47k/2W anodowy) + C5 (sprzegajacy) do siatki EL84;
    # odsprzeganie B+ drivera: R4/R5 + C4
    same(('U1', A), (rn('R4'), '2'), (rn('C5'), '1'))
    same((rn('R4'), '1'), (rn('R5'), '1'), (rn('C4'), '1'))
    same((rn('R5'), '2'), (tref, '1'))                          # B+ (+300V) -> anoda drivera

    # siatka EL84 (elref, unit A EL84: pin2=G1, pin3=K_G3, pin7=A, pin9=G2):
    # siatka elref przez R7 do wezla C5/R6 (grid leak)
    same((rn('C5'), '2'), (rn('R6'), '1'), (rn('R7'), '1'))
    same((rn('R7'), '2'), (elref, '2'))

    # zwora triodowa R9 miedzy A (7) i G2 (9) EL84
    same((elref, '9'), (rn('R9'), '2'))
    same((rn('R9'), '1'), (elref, '7'), (tref, '2'))            # zwora + anoda -> OPT primary

    # katoda EL84 (elref k=3): R8 (270R/5W) + C6 (470u)
    same((elref, '3'), (rn('R8'), '1'), (rn('C6'), '1'))

    # tref (OPT SE 5k:80): primary = +300V (pin1) / anoda-zwora (pin2);
    # wtorne = OUT (pin3) / GND (pin4)

    # masa (GND) - wspolny wezel
    same((rn('C2'), '2'), (rn('C3'), '2'), (rn('C4'), '2'), (rn('C6'), '2'),
         (rn('R1'), '2'), (rn('R3'), '2'), (rn('R6'), '2'), (rn('R8'), '2'),
         ('RV1', p3), (tref, '3'))

    diff((rn('R5'), '2'), (tref, '3'))          # +300V != GND
    diff(('RV1', p1), (tref, '4'))              # IN != OUT (obie dyndaja, ale to rozne sieci)
    diff(('U1', A), ('U1', G))                  # anoda != siatka
    diff(('U1', A), ('U1', K))                  # anoda != katoda
    diff((elref, '7'), (elref, '9'))            # anoda != g2 (R9 miedzy nimi - to nie zwarcie)
    diff((elref, '2'), (elref, '3'))            # siatka != katoda


def rn_id(off):
    def rn(base):
        pfx = base[0]
        return pfx + str(int(base[1:]) + off)
    return rn


chan(rn_id(0), 'L', ('1', '2', '3'), ('6', '7', '8'), 'U2', 'T1', 'SW2', 0)
chan(rn_id(200), 'P', ('4', '5', '6'), ('1', '2', '3'), 'U202', 'T201', 'SW202', 200)

# =======================================================================
#  zarzenia (grzanie) - DECYZJA 2026-09-08 (wariant a, "kosmetyka arkusza"):
#  zarniki lamp PRZYWROCONE, rysowane drutami wewnatrz ramki ZARZENIE.
#  ECC82 (U1 unit3): piny 4 i 5 (oba F1) -> +6,3V (U301.VO); pin 9 (F2) ->
#  minus zarzenia (ta sama siec co ELEV). EL84 (U2, U202, unit2): pin 4
#  (F1) -> +6,3V; pin 5 (F2) -> minus.
# =======================================================================
same(('U301', '2'), ('U1', '4'), ('U1', '5'), ('U2', '4'), ('U202', '4'))          # +6,3V (HEAT_A)
same(('R308', '2'), ('C307', '2'), ('C308', '2'),
     ('U1', '9'), ('U2', '5'), ('U202', '5'), ('R304', '2'))                       # minus zarzenia = ELEV
diff(('U301', '2'), ('U1', '9'))            # +6,3V != minus
diff(('U1', '4'), ('R1', '2'))              # HEAT != GND

# =======================================================================
#  diff() - sieci ktore MUSZA byc rozne (dodatkowe, poza chan())
# =======================================================================
diff(('RV1', '1'), ('RV1', '4'))          # IN_L != IN_R
diff(('T1', '4'), ('T201', '4'))          # OUT_L != OUT_R
diff(('U1', '6'), ('U1', '1'))            # anoda kanalu L != anoda kanalu P (na tej samej lampie)

# =======================================================================
#  ZASILACZ (Etap 5b) - asercje wg PROJEKT-HEADAMP.md / polecenia etapu
# =======================================================================

# +300V - wspolna szyna dla obu kanalow + zasilacza
same(('R5', '2'), ('R205', '2'), ('T1', '1'), ('T201', '1'), ('L1', '2'),
     ('C303', '1'), ('R303', '1'), ('R304', '1'), ('K1', '12'))

# ELEV (elewacja zarzenia +50V wzgledem HEAT_A/HEAT_B)
same(('R304', '2'), ('R305', '1'), ('C304', '1'), ('K1', 'A2'), ('D305', '2'))

# HEAT_A / HEAT_B - wyjscie LD1085 (U301), strona zasilacza (DECYZJA
# 2026-09-08: zarniki lamp nie sa rysowane - dawne asercje az do U1/U2/U202
# usuniete, zostaje tylko to co faktycznie jest na schemacie: U301 (wyjscie
# regulatora) i R307/R308/C307/C308 (dzielnik + odsprzeganie), az do
# etykiet HEAT_A/HEAT_B na koncach drutow).
same(('U301', '2'), ('R307', '1'), ('C308', '1'))                            # HEAT_A
same(('R308', '2'), ('C307', '2'), ('C308', '2'))                            # HEAT_B

# V_RAW - wyjscie mostka Schottky zarzenia, zasila K1 i U301.VI
same(('D306', '1'), ('D307', '1'), ('C305', '1'), ('C306', '1'), ('U301', '3'),
     ('K1', 'A1'), ('D305', '1'))

# GND wspolna (sygnalowa) - potwierdzenie ze kanal L, kanal P i zasilacz
# sa na TEJ SAMEJ sieci (nie oddzielnych GND-ach)
same(('R1', '2'), ('R201', '2'), ('C302', '2'), ('C303', '2'), ('R306', '2'))

# siec 230V (mains)
same(('J1', '1'), ('F1', '1'))
same(('F1', '2'), ('SW1', '1'))
same(('SW1', '2'), ('RT1', '1'))
same(('RT1', '2'), ('T301', '1'), ('RV301', '1'), ('R301', '1'))
same(('J1', '2'), ('SW1', '3'))
same(('SW1', '4'), ('T301', '2'), ('RV301', '2'), ('NE1', '1'))
same(('R301', '2'), ('NE1', '2'))

# mostek HT + filtr CLC
same(('T301', '3'), ('D301', '2'), ('D303', '1'), ('R302', '1'))
same(('T301', '4'), ('D302', '2'), ('D304', '1'), ('C301', '2'))
same(('D301', '1'), ('D302', '1'), ('C302', '1'), ('L1', '1'))
same(('D303', '2'), ('D304', '2'), ('C302', '2'))

# zarzenie: 7V -> mostek 1N5822 -> V_RAW -> LD1085 -> HEAT_A/HEAT_B
same(('T301', '5'), ('D306', '2'), ('D308', '1'))
same(('T301', '6'), ('D307', '2'), ('D309', '1'))
same(('D308', '2'), ('D309', '2'), ('C305', '2'), ('C306', '2'))
same(('U301', '1'), ('R307', '2'), ('R308', '1'))

# ground breaker (masa <-> PE, jedyny styk)
same(('J1', '3'), ('R309', '2'), ('D310', '2'), ('D311', '1'), ('C309', '2'))
same(('R309', '1'), ('D310', '1'), ('D311', '2'), ('C309', '1'), ('R1', '2'))

diff(('R5', '2'), ('R1', '2'))            # +300V != GND
diff(('R304', '2'), ('R1', '2'))          # ELEV != GND
diff(('D306', '1'), ('R304', '2'))        # V_RAW != ELEV
diff(('U301', '2'), ('R308', '2'))        # HEAT_A != HEAT_B
diff(('R5', '2'), ('R304', '2'))          # +300V != ELEV
diff(('J1', '1'), ('J1', '2'))            # L != N
diff(('J1', '2'), ('J1', '3'))            # N != PE
diff(('J1', '1'), ('J1', '3'))            # L != PE
diff(('J1', '3'), ('R1', '2'))            # PE != GND (ground breaker rozdziela)

# =======================================================================
#  CROSSFEED S1 + gniazda WE/WY (DECYZJA 2026-09-08, S1 przeniesiony na
#  wyjscie galezi krzyzowej) - topologia wg sim/crossfeed_sw.cir (ZRODLO
#  PRAWDY). Tor prosty R401/C401 (R402/C402) ZAWSZE wpiety bezposrednio
#  miedzy gniazdo a RV1 (bez udzialu przelacznika - jak wczesniej).
#  Galaz krzyzowa jest teraz zasilana z gniazda WPROST (bez przelacznika):
#  J401->R403->mL->C403->R405, i DOPIERO na koncu (po R405) wchodzi SW401
#  sekcja A (styk 1, NC=3) -> COM (pin 2) -> wyjscie kanalu P (RV1.4).
#  Mirror: J402->R404->mR->C404->R406->SW401 sekcja B (styk 4, NC=6) ->
#  COM (pin 5) -> wyjscie kanalu L (RV1.1). Pozycji przelacznika
#  (prosty/krzyzowy) NIE DA SIE zweryfikowac statyczna netlista - schemat
#  rysuje jedna (zalaczona) pozycje, jak w cir.
# =======================================================================
same(('J401', '1'), ('R401', '1'), ('R403', '1'), ('C401', '1'))   # gniazdo L -> tor prosty (in) + galaz krzyzowa (wprost)
same(('R401', '2'), ('C401', '2'), ('RV1', '1'), ('SW401', '5'))   # tor prosty (out) + SW401 COM sekcji B -> RV1 kanalu L
same(('J402', '1'), ('R402', '1'), ('R404', '1'), ('C402', '1'))   # gniazdo P -> tor prosty (in) + galaz krzyzowa (wprost)
same(('R402', '2'), ('C402', '2'), ('RV1', '4'), ('SW401', '2'))   # tor prosty (out) + SW401 COM sekcji A -> RV1 kanalu P

same(('R403', '2'), ('C403', '1'), ('R405', '1'))                  # mL: R krzyzowy + C do masy
same(('R405', '2'), ('SW401', '1'))                                # R405 -> SW401 styk A (wejscie sekcji A)
same(('R404', '2'), ('C404', '1'), ('R406', '1'))                  # mR: R krzyzowy + C do masy
same(('R406', '2'), ('SW401', '4'))                                # R406 -> SW401 styk B (wejscie sekcji B)
same(('C403', '2'), ('R1', '2'))                                   # C403 do masy
same(('C404', '2'), ('R1', '2'))                                   # C404 do masy

diff(('SW401', '1'), ('SW401', '2'))          # styk A != COM A (S1 rozwiera ta sciezke w pozycji "prosty")
diff(('SW401', '4'), ('SW401', '5'))          # styk B != COM B
# diff(('RV1','1'),('RV1','4')) juz sprawdzone wyzej (IN_L != IN_R)

# gniazda WY (J403 TRS 6,3mm): T=kanal L, R=kanal P, S=GND
same(('T1', '4'), ('J403', 'T'))
same(('T201', '4'), ('J403', 'R'))
same(('J403', 'S'), ('R1', '2'))

# =======================================================================
#  test geometrii drutow (check_geom.py) - Eeschema scala wspolliniowe
#  odcinki przy zapisie; jesli gen.py wyemituje nakladajace sie odcinki
#  (albo odcinek przechodzacy przez pin/koniec drutu bez junction),
#  polaczenie ginie PO otwarciu w Eeschema mimo ze kicad-cli tego nie
#  widzi (netlista/ERC na "surowym" pliku z gen.py wychodzi czysto) -
#  patrz docs/PROJEKT-HEADAMP.md. Uruchamiamy zawsze razem z asercjami
#  netlisty powyzej.
if os.path.isfile(SCHFILE):
    geom_fails = check_geom.run(SCHFILE, NETFILE if os.path.isfile(NETFILE) else None)
    if geom_fails:
        fails.append('GEOMETRIA DRUTOW (check_geom.py):')
        fails.extend('  ' + f for f in geom_fails)

print('Nety:', len(nets))
if fails:
    print('FAILURES:')
    [print(' ', f) for f in fails]
    sys.exit(1)
print('WSZYSTKIE ASERCJE NETLISTY OK (kanal L)')
