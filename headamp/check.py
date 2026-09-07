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
#  KANAL L - driver 1/2 ECC82 (U1, unit A: pin6=A, pin7=G, pin8=K)
# =======================================================================

# wejscie -> RV1 (glosnosc) -> C1 -> siatka drivera (R2 stopper)
same(('RV1', '2'), ('C1', '1'))
same(('C1', '2'), ('R1', '1'), ('R2', '1'))
same(('R2', '2'), ('U1', '7'))                              # R2 -> siatka U1A

# katoda drivera: R3 (1k5 na stale) + C2 (1u na stale) + SW2 -> C3 (100u)
same(('U1', '8'), ('R3', '1'), ('C2', '1'), ('SW2', '1'))
same(('SW2', '2'), ('C3', '1'))                              # S2 w galezi C3 (100u)

# anoda drivera: R4 (47k/2W anodowy) + C5 (sprzegajacy) do siatki EL84;
# odsprzeganie B+ drivera: R4/R5 + C4
same(('U1', '6'), ('R4', '2'), ('C5', '1'))
same(('R4', '1'), ('R5', '1'), ('C4', '1'))
same(('R5', '2'), ('T1', '1'))                               # B+ (+300V) -> anoda drivera

# siatka EL84 (U2, unit A EL84: pin2=G1, pin3=K_G3, pin7=A, pin9=G2):
# siatka U2 przez R7 do wezla C5/R6 (grid leak)
same(('C5', '2'), ('R6', '1'), ('R7', '1'))
same(('R7', '2'), ('U2', '2'))

# zwora triodowa R9 miedzy A (7) i G2 (9) EL84
same(('U2', '9'), ('R9', '2'))
same(('R9', '1'), ('U2', '7'), ('T1', '2'))                  # zwora + anoda -> OPT primary

# katoda EL84 (U2 k=3): R8 (270R/5W) + C6 (470u)
same(('U2', '3'), ('R8', '1'), ('C6', '1'))

# T1 (OPT SE 5k:80): primary = +300V (pin1) / anoda-zwora (pin2);
# wtorne = OUT_L (pin3) / GND (pin4)

# masa (GND) - wspolny wezel
same(('C2', '2'), ('C3', '2'), ('C4', '2'), ('C6', '2'),
     ('R1', '2'), ('R3', '2'), ('R6', '2'), ('R8', '2'),
     ('RV1', '3'), ('T1', '3'))

# zarzenia (grzanie) - odrebne od reszty toru, dwie wspolne szyny
# ECC82 (U1, unit F): pin4 + pin5 -> HEAT_A, pin9 -> HEAT_B
same(('U1', '4'), ('U1', '5'), ('U2', '4'))                  # HEAT_A (wspolna dla obu lamp)
same(('U1', '9'), ('U2', '5'))                               # HEAT_B (wspolna dla obu lamp)

# =======================================================================
#  diff() - sieci ktore MUSZA byc rozne
# =======================================================================
diff(('R5', '2'), ('T1', '3'))            # +300V != GND
diff(('RV1', '1'), ('T1', '4'))           # IN_L != OUT_L (obie dyndaja, ale to rozne sieci)
diff(('U1', '4'), ('U1', '9'))            # HEAT_A != HEAT_B
diff(('U1', '6'), ('U1', '7'))            # anoda != siatka (U1A)
diff(('U1', '6'), ('U1', '8'))            # anoda != katoda (U1A)
diff(('U2', '7'), ('U2', '9'))            # anoda != g2 (R9 miedzy nimi - to nie zwarcie)
diff(('U2', '2'), ('U2', '3'))            # siatka != katoda (U2A)
diff(('R5', '2'), ('U1', '4'))            # B+ != zarzenie

print('Nety:', len(nets))
if fails:
    print('FAILURES:')
    [print(' ', f) for f in fails]
    sys.exit(1)
print('WSZYSTKIE ASERCJE NETLISTY OK (kanal L)')
