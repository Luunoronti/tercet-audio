"""Test geometrii drutow dla headamp.kicad_sch (i dowolnego innego .kicad_sch
z tego samego silnika, np. riaa) - wywolywany z check.py.

Powod istnienia: Eeschema (KiCad 10.0.6) SCALA wspolliniowe odcinki drutu
przy wczytaniu/zapisie pliku. Jesli generator (gen.py) wyemitowal dwa
wspolliniowe odcinki ktore na siebie NACHODZA (np. .../-> (X,A)-(X,B) i
(X,B)-(X,C) gdzie B lezy MIEDZY A i C), Eeschema scala je w jeden odcinek
(X,A)-(X,C) i punkt B PRZESTAJE byc wierzcholkiem/koncem drutu. Jesli w B
konczyl sie inny drut albo pin (bez junction w B), to polaczenie ginie ->
ERC "pin_not_connected" / "unconnected_wire_endpoint" (obserwowane w
headamp.kicad_sch po przesejwowaniu w Eeschema, patrz docs/PROJEKT-HEADAMP.md).

Cztery testy geometryczne (na surowym pliku .kicad_sch, NIEZALEZNIE od
gen.py - parsujemy plik wynikowy tak jak zrobilby to czlowiek/Eeschema):

  (a) zadne dwa wspolliniowe odcinki nie moga sie nakladac (wspolna czesc
      dluzsza niz 0 - dotykanie samymi koncami jest OK).
  (b) zaden odcinek nie moze przechodzic PRZEZ pin symbolu ani przez KONIEC
      innego drutu bez junction dokladnie w tym punkcie (wymog Eeschema:
      T-polaczenie w srodku odcinka wymaga junction).
  (c) brak odcinkow krotszych niz 1.27 mm (siatka schematu).
  (d) kazdy koniec drutu ma polaczenie: lezy na pinie, na junction, na
      no_connect, lub pokrywa sie z koncem/srodkiem innego drutu (jesli
      srodkiem - to tylko gdy jest tam junction, patrz (b)) - brak
      dyndajacych koncow.

Emulacja Eeschema (kluczowy test regresji, patrz emulate_merge()): scala
wspolliniowe odcinki stykajace sie KONCAMI w punkcie w ktorym NIE ma ani
pinu, ani junction, ani trzeciego drutu (dokladnie tak jak robi to
Eeschema przy zapisie) - a potem liczy polaczenia (piny <-> odcinki <->
junctions) na wynikowym, scalonym zbiorze odcinkow. Partycja pinow na
sieci z tej emulacji MUSI byc identyczna z tym co zwraca
`kicad-cli sch export netlist` (prawdziwy silnik Eeschema) - patrz
netlist_partition_matches().
"""
import os
import sys
import itertools

sys.path.insert(0, os.path.dirname(__file__))
import symlib

TOL = 1e-6
MIN_LEN = 1.27  # siatka schematu (mm)


def rp(p):
    return (round(p[0], 3), round(p[1], 3))


# =======================================================================
#  parsowanie .kicad_sch
# =======================================================================

def load_sch(path):
    text = open(path, encoding='utf-8').read()
    tree, _ = symlib.parse(symlib.tokenize(text), 0)
    return tree


def _num(v):
    return float(v)


def extract(tree):
    """Zwraca dict: wires, junctions, noconns, pins (lista (ref,num,(x,y)))."""
    wires = []
    junctions = []
    noconns = []
    pins = []
    pwrflag_refs = set()
    gnd_pins = []  # piny symboli 'power:GND' - kicad-cli laczy je globalnie
                   # (etykieta niejawna = Value, "GND" wszedzie na tym
                   # arkuszu) niezaleznie od polozenia/drutow; PWR_FLAG
                   # (power:PWR_FLAG) NIE dziala tak - to zwykly pin
                   # polaczony wylacznie fizycznym drutem w miejscu
                   # wystapienia, wiec go tu NIE dodajemy.

    for node in tree:
        if not isinstance(node, list):
            continue
        tag = node[0]
        if tag == 'wire':
            pts = None
            for x in node:
                if isinstance(x, list) and x[0] == 'pts':
                    pts = x
            xy = [n for n in pts if isinstance(n, list) and n[0] == 'xy']
            assert len(xy) == 2, ('wire z != 2 punktami', node)
            a = rp((_num(xy[0][1]), _num(xy[0][2])))
            b = rp((_num(xy[1][1]), _num(xy[1][2])))
            wires.append((a, b))
        elif tag == 'junction':
            at = next(x for x in node if isinstance(x, list) and x[0] == 'at')
            junctions.append(rp((_num(at[1]), _num(at[2]))))
        elif tag == 'no_connect':
            at = next(x for x in node if isinstance(x, list) and x[0] == 'at')
            noconns.append(rp((_num(at[1]), _num(at[2]))))
        elif tag == 'symbol':
            libid = None
            at = None
            mirror = None
            unit = 1
            ref = None
            for x in node:
                if not isinstance(x, list):
                    continue
                if x[0] == 'lib_id':
                    libid = symlib.unq(x[1])
                elif x[0] == 'at':
                    at = (_num(x[1]), _num(x[2]), int(float(x[3])))
                elif x[0] == 'mirror':
                    mirror = x[1]
                elif x[0] == 'unit':
                    unit = int(x[1])
                elif x[0] == 'property' and symlib.unq(x[1]) == 'Reference':
                    ref = symlib.unq(x[2])
            if libid is None or at is None:
                continue
            if libid not in _PINGEO_CACHE:
                lib, name = libid.split(':', 1)
                _PINGEO_CACHE[libid] = symlib.pins(symlib.resolve(lib, name))
            geo = _PINGEO_CACHE[libid]
            u = unit if unit in geo else 0
            x0, y0, rot = at
            for num, px, py, angle, length, nm in geo.get(u, []):
                ox, oy = symlib.xform(px, py, rot, mirror)
                ppos = rp((x0 + ox, y0 + oy))
                pins.append((ref, num, ppos))
                if libid == 'power:GND':
                    gnd_pins.append((ref, num, ppos))
                if libid == 'power:PWR_FLAG':
                    pwrflag_refs.add(ref)

    return dict(wires=wires, junctions=junctions, noconns=noconns, pins=pins,
                 gnd_pins=gnd_pins, pwrflag_refs=pwrflag_refs)


_PINGEO_CACHE = {}


# =======================================================================
#  geometria pomocnicza
# =======================================================================

def is_collinear(a, b, c):
    """Czy c lezy na prostej przechodzacej przez a-b (a-b musi byc pozioma
    lub pionowa - jak wszystkie druty na tym schemacie)."""
    if abs(a[0] - b[0]) < TOL:  # pionowy, x = const
        return abs(c[0] - a[0]) < TOL
    if abs(a[1] - b[1]) < TOL:  # poziomy, y = const
        return abs(c[1] - a[1]) < TOL
    return False  # nieortogonalny odcinek (nie powinno sie zdarzyc)


def on_segment_interior(p, a, b):
    """Czy p lezy SCISLE wewnatrz odcinka a-b (bez koncow), zakladajac
    ortogonalnosc a-b."""
    if not is_collinear(a, b, p):
        return False
    if abs(a[0] - b[0]) < TOL:  # pionowy
        lo, hi = sorted((a[1], b[1]))
        return lo + TOL < p[1] < hi - TOL and abs(p[0] - a[0]) < TOL
    else:  # poziomy
        lo, hi = sorted((a[0], b[0]))
        return lo + TOL < p[0] < hi - TOL and abs(p[1] - a[1]) < TOL


def seg_len(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])  # ortogonalne -> Manhattan = euklides


def interval_overlap(a0, a1, b0, b1):
    """Dlugosc czesci wspolnej dwoch przedzialow (posortowanych granic)."""
    lo = max(min(a0, a1), min(b0, b1))
    hi = min(max(a0, a1), max(b0, b1))
    return max(0.0, hi - lo)


# =======================================================================
#  (a) nakladajace sie wspolliniowe odcinki
# =======================================================================

def check_overlaps(wires):
    fails = []
    for (i, (a1, b1)), (j, (a2, b2)) in itertools.combinations(enumerate(wires), 2):
        vert1 = abs(a1[0] - b1[0]) < TOL
        vert2 = abs(a2[0] - b2[0]) < TOL
        horiz1 = abs(a1[1] - b1[1]) < TOL
        horiz2 = abs(a2[1] - b2[1]) < TOL
        if vert1 and vert2 and abs(a1[0] - a2[0]) < TOL:
            ov = interval_overlap(a1[1], b1[1], a2[1], b2[1])
        elif horiz1 and horiz2 and abs(a1[1] - a2[1]) < TOL:
            ov = interval_overlap(a1[0], b1[0], a2[0], b2[0])
        else:
            continue
        if ov > TOL:
            fails.append('OVERLAP: wire %s-%s naklada sie z wire %s-%s (dlugosc wspolna %.3f mm)'
                          % (a1, b1, a2, b2, ov))
    return fails


# =======================================================================
#  (b) odcinek przechodzacy przez pin/koniec innego drutu bez junction
# =======================================================================

def check_through_points(wires, pins, junctions):
    fails = []
    jset = set(junctions)
    endpoints = set()
    for a, b in wires:
        endpoints.add(a)
        endpoints.add(b)
    poi = set(endpoints)
    for ref, num, p in pins:
        poi.add(p)
    for idx, (a, b) in enumerate(wires):
        for p in poi:
            if p == a or p == b:
                continue
            if on_segment_interior(p, a, b) and p not in jset:
                who = [('%s.%s' % (ref, num)) for ref, num, pp in pins if pp == p]
                what = ('pin ' + ','.join(who)) if who else 'koniec innego drutu'
                fails.append('THROUGH-NO-JUNCTION: wire %s-%s przechodzi przez %s w %s bez junction'
                              % (a, b, what, p))
    return fails


# =======================================================================
#  (c) zbyt krotkie odcinki
# =======================================================================

def check_short(wires):
    fails = []
    for a, b in wires:
        L = seg_len(a, b)
        if L < MIN_LEN - TOL:
            fails.append('SHORT WIRE: %s-%s dlugosc %.4f mm < %.2f mm' % (a, b, L, MIN_LEN))
    return fails


# =======================================================================
#  (d) dyndajace konce drutow
# =======================================================================

def check_dangling(wires, pins, junctions, noconns):
    fails = []
    jset = set(junctions)
    ncset = set(noconns)
    pinpts = set(p for r, n, p in pins)
    endpoint_count = {}
    for a, b in wires:
        endpoint_count[a] = endpoint_count.get(a, 0) + 1
        endpoint_count[b] = endpoint_count.get(b, 0) + 1

    # punkty gdzie inny drut ma SRODEK (do sprawdzenia polaczenia przez
    # T-junction) - tylko takie z junction sa "polaczone" (patrz check b).
    def touches_wire_midpoint_with_junction(p):
        for a, b in wires:
            if on_segment_interior(p, a, b) and p in jset:
                return True
        return False

    for a, b in wires:
        for p in (a, b):
            ok = (p in pinpts) or (p in jset) or (p in ncset) or (endpoint_count[p] >= 2)
            if not ok:
                ok = touches_wire_midpoint_with_junction(p)
            if not ok:
                fails.append('DANGLING END: koniec drutu %s (odcinek %s-%s) nie lezy na pinie/'
                              'junction/no_connect ani nie styka sie z innym drutem' % (p, a, b))
    return fails


# =======================================================================
#  emulacja scalania kolinearnych odcinkow przez Eeschema
# =======================================================================

def emulate_merge(wires, pins, junctions, noconns):
    """Zwraca nowa liste odcinkow po scaleniu kolinearnych par stykajacych
    sie KONCAMI w punkcie bez pinu/junction/no_connect/trzeciego drutu -
    dokladnie tak jak robi to Eeschema przy wczytaniu/zapisie pliku."""
    jset = set(junctions)
    ncset = set(noconns)
    pinpts = set(p for r, n, p in pins)
    segs = list(wires)

    def protected(p):
        return p in jset or p in ncset or p in pinpts

    changed = True
    while changed:
        changed = False
        endpoint_count = {}
        for a, b in segs:
            endpoint_count[a] = endpoint_count.get(a, 0) + 1
            endpoint_count[b] = endpoint_count.get(b, 0) + 1
        for i in range(len(segs)):
            a1, b1 = segs[i]
            for j in range(len(segs)):
                if i == j:
                    continue
                a2, b2 = segs[j]
                # szukamy wspolnego punktu (koniec segmentu i == koniec segmentu j)
                for shared, other1 in ((a1, b1), (b1, a1)):
                    if shared == a2:
                        other2 = b2
                    elif shared == b2:
                        other2 = a2
                    else:
                        continue
                    if endpoint_count.get(shared, 0) != 2:
                        continue
                    if protected(shared):
                        continue
                    if not is_collinear(other1, shared, other2):
                        continue
                    # sa dokladnie 2 druty w tym punkcie, kolinearne, punkt
                    # nie jest chroniony -> scal w jeden odcinek other1-other2
                    new_seg = (other1, other2)
                    remove = {i, j}
                    segs = [s for k, s in enumerate(segs) if k not in remove]
                    segs.append(new_seg)
                    changed = True
                    break
                if changed:
                    break
            if changed:
                break
    return segs


# =======================================================================
#  partycja sieci z modelu (po emulacji) - do porownania z kicad-cli
# =======================================================================

class DSU:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[rx] = ry


def compute_partition(wires, pins, junctions, gnd_pins=()):
    """Model polaczen: kazdy drut laczy swoje 2 konce; punkt (pin lub koniec
    innego drutu) lezacy SCISLE w srodku jakiegos drutu laczy sie z tym
    drutem TYLKO jesli w tym punkcie jest junction (regula Eeschema).
    Dodatkowo wszystkie piny 'power:GND' laczymy globalnie (tak jak robi to
    kicad-cli - symbol power tworzy niejawna globalna siec wg Value)."""
    dsu = DSU()
    for a, b in wires:
        dsu.union(a, b)

    jset = set(junctions)
    endpoints = set()
    for a, b in wires:
        endpoints.add(a)
        endpoints.add(b)
    poi = set(endpoints) | set(p for r, n, p in pins)

    for p in poi:
        if p not in jset:
            continue
        for a, b in wires:
            if on_segment_interior(p, a, b):
                dsu.union(p, a)

    if gnd_pins:
        first = gnd_pins[0][2]
        for _, _, p in gnd_pins[1:]:
            dsu.union(first, p)

    # grupuj piny wg klasy
    pin2class = {}
    for ref, num, p in pins:
        pin2class[(ref, num)] = dsu.find(p)
    return pin2class


def partition_signature(pin2class):
    """{class_root: frozenset(pinow)} - niezalezne od konkretnych etykiet
    korzeni DSU, do porownania miedzy dwoma przebiegami."""
    groups = {}
    for pin, root in pin2class.items():
        groups.setdefault(root, set()).add(pin)
    return set(frozenset(g) for g in groups.values())


# =======================================================================
#  parsowanie netlisty kicad-cli (kicadsexpr) - kompatybilne z check.py
# =======================================================================

def load_netlist_partition(netfile):
    tree, _ = symlib.parse(symlib.tokenize(open(netfile, encoding='utf-8').read()), 0)
    groups = set()
    for n in tree:
        if isinstance(n, list) and n[0] == 'nets':
            for net in n[1:]:
                if not (isinstance(net, list) and net[0] == 'net'):
                    continue
                members = []
                for e in net:
                    if isinstance(e, list) and e[0] == 'node':
                        ref = pinn = None
                        for f in e:
                            if isinstance(f, list) and f[0] == 'ref':
                                ref = symlib.unq(f[1])
                            if isinstance(f, list) and f[0] == 'pin':
                                pinn = symlib.unq(f[1])
                        members.append((ref, pinn))
                if members:
                    groups.add(frozenset(members))
    return groups


def netlist_partition_matches(schfile, netfile):
    """Emuluje scalanie Eeschema na schfile, liczy partycje pinow, i
    porownuje z prawdziwa netlista wyeksportowana przez kicad-cli. Zwraca
    (ok: bool, fails: list[str])."""
    data = extract(load_sch(schfile))
    merged = emulate_merge(data['wires'], data['pins'], data['junctions'], data['noconns'])
    pin2class = compute_partition(merged, data['pins'], data['junctions'], data['gnd_pins'])
    # kicad-cli export netlist nie wypisuje pinow PWR_FLAG ani power:GND
    # (refy '#FLGxx'/'#GNDxx', wygenerowane, ukryte) jako wezlow sieci - to
    # tylko wewnetrzne "punkty widokowe" dla ERC, nie prawdziwe piny
    # komponentu - usun je przed porownaniem partycji, inaczej falszywa
    # roznica (siec GND w netliscie i tak jest kompletna - reprezentuja ja
    # inne, prawdziwe piny na tej samej sieci: R1.2, C2.2, itd.).
    gnd_refs = {ref for ref, _, _ in data['gnd_pins']}
    excluded_refs = data['pwrflag_refs'] | gnd_refs
    pin2class = {pn: c for pn, c in pin2class.items() if pn[0] not in excluded_refs}
    model_groups = partition_signature(pin2class)

    # kicad-cli grupuje TYLKO piny faktycznie polaczone z czyms (jeden pin
    # sam w sobie na wlasnej sieci tez sie liczy) - odfiltruj u nas grupy z
    # jednym elementem tak samo jak robi to netlist (kazda siec z >=1 pin).
    real_groups = load_netlist_partition(netfile)

    fails = []
    if model_groups != real_groups:
        only_model = model_groups - real_groups
        only_real = real_groups - model_groups
        for g in sorted(only_model, key=lambda s: sorted(s))[:20]:
            fails.append('EMULACJA != NETLISTA (grupa tylko w modelu): %s' % sorted(g))
        for g in sorted(only_real, key=lambda s: sorted(s))[:20]:
            fails.append('EMULACJA != NETLISTA (grupa tylko w kicad-cli): %s' % sorted(g))
    return (not fails), fails


# =======================================================================
#  entry point
# =======================================================================

def run(schfile, netfile=None):
    """Uruchamia testy (a)-(d) + (jesli podano netfile) test regresji
    emulacji scalania vs kicad-cli. Zwraca liste komunikatow bledow
    (pusta = OK)."""
    data = extract(load_sch(schfile))
    fails = []
    fails += check_overlaps(data['wires'])
    fails += check_through_points(data['wires'], data['pins'], data['junctions'])
    fails += check_short(data['wires'])
    fails += check_dangling(data['wires'], data['pins'], data['junctions'], data['noconns'])
    if netfile and os.path.isfile(netfile):
        ok, netfails = netlist_partition_matches(schfile, netfile)
        fails += netfails
    return fails


if __name__ == '__main__':
    schfile = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'headamp.kicad_sch')
    netfile = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), 'headamp.net')
    fails = run(schfile, netfile if os.path.isfile(netfile) else None)
    if fails:
        print('GEOMETRIA: FAILURES (%d):' % len(fails))
        for f in fails:
            print(' ', f)
        sys.exit(1)
    print('GEOMETRIA: OK')
