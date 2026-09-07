"""Weryfikacja netlisty headamp - kanal L (SE EL84 trioda + 1/2 ECC82).
Wzorowane na riaa/check.py. Wejscie: headamp/headamp.net
(kicad-cli sch export netlist --format kicadsexpr -o headamp.net headamp.kicad_sch).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import symlib

NETFILE = os.path.join(os.path.dirname(__file__), 'headamp.net')

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
#  zarzenia (grzanie) - wspolne dla obu kanalow, dwie wspolne szyny
#  ECC82 (U1, unit F): pin4 + pin5 -> HEAT_A, pin9 -> HEAT_B
#  EL84 U2/U202 (unit heater): pin4 -> HEAT_A, pin5 -> HEAT_B
# =======================================================================
same(('U1', '4'), ('U1', '5'), ('U2', '4'), ('U202', '4'))     # HEAT_A (wspolna dla 3 lamp)
same(('U1', '9'), ('U2', '5'), ('U202', '5'))                  # HEAT_B (wspolna dla 3 lamp)

# =======================================================================
#  diff() - sieci ktore MUSZA byc rozne (dodatkowe, poza chan())
# =======================================================================
diff(('U1', '4'), ('U1', '9'))            # HEAT_A != HEAT_B
diff(('R5', '2'), ('U1', '4'))            # B+ != zarzenie
diff(('RV1', '1'), ('RV1', '4'))          # IN_L != IN_R
diff(('T1', '4'), ('T201', '4'))          # OUT_L != OUT_R
diff(('U1', '6'), ('U1', '1'))            # anoda kanalu L != anoda kanalu P (na tej samej lampie)

print('Nety:', len(nets))
if fails:
    print('FAILURES:')
    [print(' ', f) for f in fails]
    sys.exit(1)
print('WSZYSTKIE ASERCJE NETLISTY OK (kanal L)')
