"""headamp.kicad_sch - lampowy wzmacniacz sluchawkowy SE EL84 (trioda) + 1/2 ECC82.
Zrodlo prawdy: ten plik (check.py = asercje netlisty), wzorowany na riaa/gen.py
(ten sam silnik: symlib.resolve/embed_text/pins, PINGEO, place/wire/junc/label/
glabel/noconn/gnd/pwrflag).

Etap 1 (ten plik, ten stan): kanal L (audio, kompletny) odtworzony 1:1 z
commitu b7d6cc9 (headamp/headamp.kicad_sch, ERC 0 bledow) - patrz
docs/PROJEKT-HEADAMP.md sekcja "Stan realizacji". Kolejne etapy (kanal P,
zasilacz) - patrz CLAUDE.md / PROJEKT-HEADAMP.md TODO.
"""
import os
import sys
import uuid as uuidlib

sys.path.insert(0, os.path.dirname(__file__))
import symlib


# Etap 0: deterministyczne UUID (uuid5) zamiast uuid4 losowego, zeby
# regeneracja byla idempotentna (git diff pusty przy dwoch uruchomieniach).
# Klucz jednoznacznie opisuje element (patrz wywolania U(...) nizej).
NAMESPACE = uuidlib.uuid5(uuidlib.NAMESPACE_URL, 'tercet-headamp')


def U(key):
    return str(uuidlib.uuid5(NAMESPACE, key))


ROOT = "fd162765-1b28-469c-8099-083c76e823f0"   # ten sam uuid arkusza co w b7d6cc9
PROJECT = "headamp"

# =======================  embedded library symbols  =======================
EMBED = []


def embed(lib, name, newname=None, value=None, datasheet=None, desc=None):
    if newname:
        sym = symlib.clone_as(lib, name, newname, value=value, datasheet=datasheet, desc=desc)
    else:
        sym = symlib.resolve(lib, name)
    EMBED.append(symlib.embed_text(sym, lib))


LIBPARTS = [
    ('Device', 'R'), ('Device', 'C'), ('Device', 'C_Polarized'),
    ('Device', 'R_Potentiometer_Dual_Separate'), ('Device', 'Transformer_1P_1S'),
    ('Switch', 'SW_SPST'),
    ('Valve', 'ECC81'), ('Valve', 'EL84'),
    ('power', 'GND'), ('power', 'PWR_FLAG'),
    # --- Etap 5b: zasilacz ---
    ('Device', 'D'), ('Device', 'Fuse'), ('Device', 'Transformer_1P_2S'),
    ('Device', 'L_Iron'), ('Device', 'Lamp_Neon'), ('Device', 'Varistor'),
    ('Device', 'Thermistor_NTC'), ('Connector', 'Screw_Terminal_01x03'),
    ('Regulator_Linear', 'LM317_TO-220'), ('Relay', 'Relay_SPDT'),
    ('Switch', 'SW_DPST_x2'), ('power', 'Earth_Protective'),
    # --- Etap B: crossfeed S1 + gniazda WE/WY ---
    ('Connector', 'Conn_Coaxial'), ('Switch', 'SW_DPDT_x2'),
    ('Connector_Audio', 'AudioJack3'),
]
for lib, name in LIBPARTS:
    embed(lib, name)
# UWAGA: w b7d6cc9 ECC82 NIE jest osobnym sklonowanym symbolem (inaczej niz
# w riaa/gen.py) - uzyty jest wprost "Valve:ECC81" z polem Value="ECC82"
# (tak zrobil Konnect). Klonowanie ECC81->ECC82 (jak w RIAA) daje lib_id
# ktorego nie ma w bibliotece systemowej -> ERC "lib_symbol_issues" (dodatkowe
# ostrzezenie, ktorego HEAD nie ma). Zachowujemy 1:1 podejscie z HEAD.

PINGEO = {}
for lib, name in LIBPARTS:
    PINGEO['%s:%s' % (lib, name)] = symlib.pins(symlib.resolve(lib, name))


def xform(dx, dy, rot, mirror):
    x, y = dx, -dy
    if mirror == 'y':
        x = -x
    if mirror == 'x':
        y = -y
    for _ in range(rot // 90):
        x, y = y, -x
    return x, y


SYMS = []


def rp(p):
    return (round(p[0], 2), round(p[1], 2))


def place(ref, libid, value, x, y, rot=0, unit=1, mirror=None, fields=None, tol=None):
    SYMS.append(dict(ref=ref, libid=libid, value=value, x=round(x, 2), y=round(y, 2),
                      rot=rot, unit=unit, mirror=mirror, fields=fields or {}, tol=tol,
                      uuid=U('sym:%s:u%d' % (ref, unit))))


def pin(ref, number, unit=None):
    for s in SYMS:
        if s['ref'] == ref and (unit is None or s['unit'] == unit):
            geo = PINGEO[s['libid']]
            u = s['unit'] if s['unit'] in geo else 0
            for num, px, py, a, l, nm in geo[u]:
                if num == str(number):
                    ox, oy = xform(px, py, s['rot'], s['mirror'])
                    return (round(s['x'] + ox, 2), round(s['y'] + oy, 2))
    raise KeyError((ref, number, unit))


WIRES = []
JUNCS = []
LABELS = []
GLABELS = []
TEXTS = []
NOCONN = []


def wire(*pts):
    pts = [rp(p) for p in pts]
    for a, b in zip(pts, pts[1:]):
        if a == b:
            continue
        assert a[0] == b[0] or a[1] == b[1], ('non-orthogonal', a, b)
        WIRES.append((a, b))


def junc(p):
    JUNCS.append(rp(p))


def label(name, p, rot=0, just='left bottom'):
    LABELS.append((name, rp(p), rot, just))


def glabel(name, p, rot=0, just='left'):
    GLABELS.append((name, rp(p), rot, just))


def text(s, x, y, size=1.27, rot=0):
    TEXTS.append((s, round(x, 2), round(y, 2), size, rot))


def noconn(p):
    NOCONN.append(rp(p))


FRAMES = []


def frame(x0, y0, x1, y1, title):
    """Ramka modulu (grafika arkusza, (rectangle ...)) + tytul w lewym
    gornym rogu (tekst 2,5mm) - DECYZJA 2026-09-08 "layout w ramkach"."""
    FRAMES.append((round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)))
    text(title, x0 + 1.27, y0 + 3.0, 2.5)


def gnd(x, y):
    place('#GND%d' % len(SYMS), 'power:GND', 'GND', x, y)


def pwrflag(x, y, rot=0):
    place('#FLG%d' % len(SYMS), 'power:PWR_FLAG', 'PWR_FLAG', x, y, rot=rot)


def pe(x, y, rot=0):
    place('#PE%d' % len(SYMS), 'power:Earth_Protective', 'Earth_Protective', x, y, rot=rot)


# =======================================================================
#  KANAL AUDIO (L, P) - funkcja parametryzowana dy (przesuniecie Y) i
#  numeracja referencji. Kanal L = odtworzony 1:1 z headamp.kicad_sch @
#  b7d6cc9 (kompletny commit z ERC=0); kanal P = ta sama geometria kanalu
#  L przesunieta w Y (dy), z refami +200 (Etap 5a, DECYZJA patrz
#  docs/PROJEKT-HEADAMP.md), na wspolnym RV1 (potencjometr podwojny,
#  R_Potentiometer_Dual_Separate) - unit=1 (piny 1/2/3) dla L, unit=2
#  (piny 4/5/6, ta sama geometria wzgledna) dla P.
# =======================================================================

# BUS_X - wspolna magistrala pionowa B+ (+300V), hybryda "druty zamiast
# etykiet" (DECYZJA 2026-09-08): zbiera odgalezienia z obu kanalow (korytarz
# nad kazdym modulem, y=80/y=185.41) i z zasilacza (CLC/R304/K1, patrz sekcja
# ponizej), zamiast global_label('+300V',...) uzywanego w commicie fc227e8.
# Wspolrzedna wybrana tak, by nie kolidowac z zadnym komponentem kanalu
# (max X kanalu ~227) ani z K1 w zasilaczu (K1 lezy PONIZEJ punktu koncowego
# magistrali - patrz "+300V bus" nizej).
BUS_X = 245.11


def chan(dy, lbl, potunit, u1unit, elref, tref, swref, off, out_flag=False):
    def rn(base):
        pfx = base[0]
        return pfx + str(int(base[1:]) + off)

    def y(v):
        return v + dy

    place('RV1', 'Device:R_Potentiometer_Dual_Separate', '50k log (podwojny)', 39.37, y(139.7),
          unit=potunit,
          fields={'ref_at': (34.925, y(139.7), 90), 'val_at': (36.83, y(139.7), 90),
                  'tol_at': (32.893, y(139.7), 90)}, tol='20%')
    place(rn('C1'), 'Device:C', '220n', 58.42, y(129.54), rot=90,
          fields={'ref_at': (55.88, y(128.905), 0), 'val_at': (60.96, y(128.905), 0),
                  'tol_at': (62.992, y(128.905), 0)}, tol='5%')
    place(rn('R1'), 'Device:R', '470k', 68.58, y(144.78),
          fields={'ref_at': (70.612, y(144.78), 90), 'val_at': (68.58, y(144.78), 90),
                  'tol_at': (66.548, y(144.78), 90)}, tol='5%')
    place(rn('R2'), 'Device:R', '1k', 80.01, y(129.54), rot=90,
          fields={'ref_at': (80.01, y(127.508), 90), 'val_at': (80.01, y(129.54), 90),
                  'tol_at': (80.01, y(131.572), 90)}, tol='5%')
    place('U1', 'Valve:ECC81', 'ECC82', 100.33, y(129.54), unit=u1unit,
          fields={'ref_at': (103.632, y(121.666), 0), 'val_at': (109.22, y(137.16), 0)})
    place(rn('R3'), 'Device:R', '1k5', 93.98, y(154.94),
          fields={'ref_at': (96.012, y(154.94), 90), 'val_at': (93.98, y(154.94), 90),
                  'tol_at': (91.948, y(154.94), 90)}, tol='1%')
    place(swref, 'Switch:SW_SPST', 'S2 wokal' if lbl == 'L' else 'S2 wokal (P)', 118.11, y(149.86), rot=270,
          fields={'ref_at': (121.285, y(149.86), 0), 'val_at': (115.57, y(149.86), 0)})
    place(rn('C2'), 'Device:C_Polarized', '1u/25V', 105.41, y(154.94),
          fields={'ref_at': (106.045, y(152.4), 0), 'val_at': (106.045, y(157.48), 0),
                  'tol_at': (106.045, y(159.512), 0)}, tol='20%')
    place(rn('C3'), 'Device:C_Polarized', '100u/25V', 118.11, y(166.37),
          fields={'ref_at': (118.745, y(163.83), 0), 'val_at': (118.745, y(168.91), 0),
                  'tol_at': (118.745, y(170.942), 0)}, tol='20%')
    place(rn('R4'), 'Device:R', '47k/2W', 100.33, y(105.41),
          fields={'ref_at': (102.362, y(105.41), 90), 'val_at': (100.33, y(105.41), 90),
                  'tol_at': (98.298, y(105.41), 90)}, tol='5%')
    place(rn('C4'), 'Device:C_Polarized', '47u/350V', 86.36, y(105.41),
          fields={'ref_at': (86.995, y(102.87), 0), 'val_at': (86.995, y(107.95), 0),
                  'tol_at': (86.995, y(109.982), 0)}, tol='20%')
    place(rn('R5'), 'Device:R', '10k/2W', 111.76, y(91.44), rot=90,
          fields={'ref_at': (111.76, y(89.408), 90), 'val_at': (111.76, y(91.44), 90),
                  'tol_at': (111.76, y(93.472), 90)}, tol='5%')
    place(rn('C5'), 'Device:C', '100n/400V', 125.73, y(118.11), rot=90,
          fields={'ref_at': (123.19, y(117.475), 0), 'val_at': (128.27, y(117.475), 0),
                  'tol_at': (130.302, y(117.475), 0)}, tol='5%')
    place(rn('R6'), 'Device:R', '470k', 135.89, y(132.08),
          fields={'ref_at': (137.922, y(132.08), 90), 'val_at': (135.89, y(132.08), 90),
                  'tol_at': (133.858, y(132.08), 90)}, tol='5%')
    place(rn('R7'), 'Device:R', '1k', 148.59, y(118.11), rot=90,
          fields={'ref_at': (148.59, y(116.078), 90), 'val_at': (148.59, y(118.11), 90),
                  'tol_at': (148.59, y(120.142), 90)}, tol='5%')
    place(elref, 'Valve:EL84', 'EL84 (trioda)', 171.45, y(124.46), unit=1,
          fields={'ref_at': (173.99, y(114.3), 0), 'val_at': (179.07, y(132.08), 0)})
    place(rn('R9'), 'Device:R', '100', 185.42, y(115.57),
          fields={'ref_at': (187.452, y(115.57), 90), 'val_at': (185.42, y(115.57), 90),
                  'tol_at': (183.388, y(115.57), 90)}, tol='5%')
    place(rn('R8'), 'Device:R', '270/5W', 166.37, y(149.86),
          fields={'ref_at': (168.402, y(149.86), 90), 'val_at': (166.37, y(149.86), 90),
                  'tol_at': (164.338, y(149.86), 90)}, tol='5%')
    place(rn('C6'), 'Device:C_Polarized', '470u/25V', 180.34, y(149.86),
          fields={'ref_at': (180.975, y(147.32), 0), 'val_at': (180.975, y(152.4), 0),
                  'tol_at': (180.975, y(154.432), 0)}, tol='20%')
    place(tref, 'Device:Transformer_1P_1S', 'OPT SE 5k:80R (>=25H, 45mA)', 209.55, y(107.95),
          fields={'ref_at': (209.55, y(101.6), 0), 'val_at': (209.55, y(115.57), 0)})

    # --- druty kanalu (topologia = literalna kopia wire/junction z b7d6cc9,
    #     przesunieta o dy w Y) ---
    wire((43.18, y(139.7)), (54.61, y(139.7)))
    wire((54.61, y(139.7)), (54.61, y(129.54)))
    wire((62.23, y(129.54)), (76.2, y(129.54)))
    wire((68.58, y(140.97)), (68.58, y(129.54)))
    wire((83.82, y(129.54)), (92.71, y(129.54)))
    wire((97.79, y(139.7)), (97.79, y(143.51)))
    wire((93.98, y(143.51)), (118.11, y(143.51)))
    wire((93.98, y(143.51)), (93.98, y(151.13)))
    wire((105.41, y(143.51)), (105.41, y(151.13)))
    wire((118.11, y(143.51)), (118.11, y(144.78)))
    wire((118.11, y(154.94)), (118.11, y(162.56)))
    wire((100.33, y(119.38)), (100.33, y(109.22)))
    wire((100.33, y(118.11)), (121.92, y(118.11)))
    wire((86.36, y(101.6)), (100.33, y(101.6)))
    wire((100.33, y(101.6)), (100.33, y(91.44)))
    wire((100.33, y(91.44)), (107.95, y(91.44)))
    wire((129.54, y(118.11)), (144.78, y(118.11)))
    wire((135.89, y(118.11)), (135.89, y(128.27)))
    wire((152.4, y(118.11)), (157.48, y(118.11)))
    wire((157.48, y(118.11)), (157.48, y(125.73)))
    wire((157.48, y(125.73)), (163.83, y(125.73)))
    wire((168.91, y(133.35)), (168.91, y(146.05)))
    wire((166.37, y(146.05)), (180.34, y(146.05)))
    wire((171.45, y(113.03)), (199.39, y(113.03)))
    wire((185.42, y(111.76)), (185.42, y(113.03)))
    wire((185.42, y(119.38)), (185.42, y(123.19)))
    wire((185.42, y(123.19)), (179.07, y(123.19)))
    wire((219.71, y(113.03)), (224.79, y(113.03)))
    wire((224.79, y(113.03)), (224.79, y(116.84)))
    wire((115.57, y(91.44)), (118.11, y(91.44)))
    wire((199.39, y(102.87)), (196.85, y(102.87)))
    wire((39.37, y(135.89)), (39.37, y(133.35)))
    wire((219.71, y(102.87)), (222.25, y(102.87)))

    for p in [(68.58, y(129.54)), (97.79, y(143.51)), (100.33, y(101.6)), (100.33, y(118.11)),
              (105.41, y(143.51)), (135.89, y(118.11)), (168.91, y(146.05)), (185.42, y(113.03))]:
        junc(p)

    # masa (GND) - 10x, dokladnie te same punkty co #PWR001..#PWR010 w b7d6cc9
    for gx, gy in [(39.37, 143.51), (68.58, 148.59), (93.98, 158.75), (105.41, 158.75),
                   (118.11, 170.18), (86.36, 109.22), (135.89, 135.89), (166.37, 153.67),
                   (180.34, 153.67), (224.79, 116.84)]:
        gnd(gx, y(gy))

    # B+ (+300V) - hybryda "druty zamiast etykiet" (DECYZJA 2026-09-08):
    # oba punkty +300V kanalu wyprowadzone drutem w gore, do korytarza nad
    # modulem (wolny od komponentow), a stamtad w prawo do wspolnej
    # magistrali pionowej BUS_X (karmiona z zasilacza, patrz nizej "B+ bus").
    wire((118.11, y(91.44)), (118.11, y(80.01)))
    wire((196.85, y(102.87)), (196.85, y(80.01)))
    wire((118.11, y(80.01)), (196.85, y(80.01)), (BUS_X, y(80.01)))
    junc((196.85, y(80.01)))
    # IN_L/IN_R, OUT_L/OUT_R - Etap B (DECYZJA 2026-09-08): global_label
    # zastapiony realnym drutem z modulu WEJSCIE/WYJSCIE (patrz nizej,
    # sekcje po chan()). Punkty (39.37, y(133.35)) i (222.25, y(102.87))
    # zostaja - tylko koncem drutu, bez wlasnej etykiety/symbolu tutaj.

    if out_flag:
        # PWR_FLAG na powrocie wtornym OPT do GND (jak w b7d6cc9) - tylko
        # RAZ na cala plansze (kolejne flagi na tym samym wezle GND daja
        # ERC error "Power output and Power output are connected").
        pwrflag(224.79, y(113.03))


# dy = 105.41 (83 * 1.27mm siatki) - kanal P dokladnie pod kanalem L,
# wspolrzedne pozostaja na siatce schematu (grid 1.27mm), inaczej ERC
# zglasza "endpoint_off_grid" na kazdym przesunietym drucie/pinie.
chan(dy=0, lbl='L', potunit=1, u1unit=1, elref='U2', tref='T1', swref='SW2', off=0, out_flag=True)
chan(dy=105.41, lbl='R', potunit=2, u1unit=2, elref='U202', tref='T201', swref='SW202', off=200)

# =======================================================================
#  WEJSCIE (DECYZJA 2026-09-08, S1 przeniesiony na wyjscie galezi krzyzowej):
#  gniazda RCA J401/J402 + crossfeed S1 (SW401, DPDT). Topologia i wartosci -
#  ZRODLO PRAWDY: sim/crossfeed_sw.cir (nie opis w PROJEKT-HEADAMP.md sprzed
#  tej daty - patrz tam sekcja "Przelaczniki charakteru" / "Decyzje").
#  Tor prosty R401||C401 (kanal L), R402||C402 (kanal P) ZAWSZE wpiety
#  bezposrednio miedzy gniazdo a RV1 (bez zadnego udzialu przelacznika).
#  Galaz krzyzowa jest teraz zasilana z gniazda WPROST (bez przelacznika):
#  J401 -> R403(2k2) -> mL (C403 220n do masy) -> R405(3k3) -> dopiero TU
#  wchodzi SW401 sekcja A (styk 1/NC 3) -> wspolny (COM, pin 2) -> wyjscie
#  kanalu P (RV1.4). Mirror: J402 -> R404 -> mR -> C404 -> R406 -> SW401
#  sekcja B (styk 4/NC 6) -> COM (pin 5) -> wyjscie kanalu L (RV1.1).
#  Powod zmiany (przeniesienie S1 z wejscia na wyjscie galezi krzyzowej):
#  przy starej topologii (przelacznik na wejsciu galezi) R405/C403 (R406/C404)
#  caly czas obciazaly wyjscia toru prostego nawet przy S1 "OFF" (martwy
#  koniec R403/R404 nie odlaczal R405/R406 od wyjscia) - ugiecie basu
#  ~1,4 dB (symulacja sim/crossfeed_sw.cir, wariant "OFF stara topologia").
#  Po przeniesieniu S1 na wyjscie, "OFF" odlacza cala galaz krzyzowa od
#  wyjsc - odchylka od plaskiej ~0,17 dB (20 Hz-20 kHz), tylko strata
#  wtraceniowa R401/RpotL (patrz sim/crossfeed_sw.cir, wariant "OFF nowa").
#  SW401 zamontowany mirror='y' (COM z lewej na prawa strone symbolu),
#  zeby geometrycznie: styk (wejscie z R405/R406, od strony galezi
#  krzyzowej) byl z LEWEJ (bliżej R405/R406), a COM (wyjscie, do magistrali
#  RV1) z PRAWEJ (bliżej wyjsc) - fizycznie odzwierciedla kierunek sygnalu.
#  Layout "X" (czytelnosc, bez przeciecia drutow): oba tory proste poziomo
#  (L u gory y=26,67; P u dolu y=60,96); galaz L->P schodzi w dol PO PRAWEJ
#  (konczy na magistrali outR x=185,42, dalej od osi), galaz P->L wchodzi w
#  gore PO LEWEJ (konczy na magistrali outL x=175,26, blizej osi) - dwie
#  przeciwbiezne linie miedzy rzedami L/P daja wrazenie "X" bez faktycznego
#  krzyzowania drutow (i bez junction w miejscu ktoregokolwiek przeciecia).
# =======================================================================
def _rv(x, y):
    """Pola ref/value dla R pionowego (rot=90) - stos wzdluz Y jak w chan()."""
    return {'ref_at': (x, y - 2.032, 90), 'val_at': (x, y, 90)}


def _cv(x, y):
    """Pola ref/value dla C pionowego (rot=90) - obok w X jak C1 w chan()."""
    return {'ref_at': (x - 2.54, y - 0.635, 0), 'val_at': (x + 2.54, y - 0.635, 0)}


place('J401', 'Connector:Conn_Coaxial', 'IN L (RCA)', 26.67, 30.48, mirror='y',
      fields={'ref_at': (16.51, 27.94, 0), 'val_at': (16.51, 33.02, 0)})
place('J402', 'Connector:Conn_Coaxial', 'IN R (RCA)', 26.67, 53.34, mirror='y',
      fields={'ref_at': (16.51, 50.8, 0), 'val_at': (16.51, 55.88, 0)})
# SW401 - obie sekcje obok siebie (sam x), tuz przed wyjsciami (miedzy R405/
# R406 x=130,81 a magistralami wyjsciowymi x=175,26/185,42). mirror='y':
# styk (pin1/pin4) po LEWEJ (od R405/R406), COM (pin2/pin5) po PRAWEJ
# (do magistrali RV1) - patrz komentarz wyzej.
place('SW401', 'Switch:SW_DPDT_x2', 'S1 crossfeed', 149.86, 39.37, unit=1, mirror='y',
      fields={'ref_at': (156.21, 32.51, 0), 'val_at': (156.21, 35.05, 0)})
place('SW401', 'Switch:SW_DPDT_x2', 'S1 crossfeed', 149.86, 52.07, unit=2, mirror='y',
      fields={'ref_at': (156.21, 44.45, 0), 'val_at': (156.21, 46.99, 0)})
place('R401', 'Device:R', '1k', 154.94, 26.67, rot=90, fields=_rv(154.94, 26.67))
place('C401', 'Device:C', '470n', 165.1, 26.67, rot=90, fields=_cv(165.1, 26.67))
place('R402', 'Device:R', '1k', 154.94, 60.96, rot=90, fields=_rv(154.94, 60.96))
place('C402', 'Device:C', '470n', 165.1, 60.96, rot=90, fields=_cv(165.1, 60.96))
place('R403', 'Device:R', '2k2', 105.41, 26.67, rot=90, fields=_rv(105.41, 26.67))
place('C403', 'Device:C', '220n', 116.84, 33.02, rot=90, fields=_cv(116.84, 33.02))
place('R405', 'Device:R', '3k3', 130.81, 33.02,
      fields={'ref_at': (132.842, 33.02, 90), 'val_at': (130.81, 33.02, 90)})
place('R404', 'Device:R', '2k2', 105.41, 60.96, rot=90, fields=_rv(105.41, 60.96))
place('C404', 'Device:C', '220n', 116.84, 45.72, rot=90, fields=_cv(116.84, 45.72))
place('R406', 'Device:R', '3k3', 130.81, 45.72,
      fields={'ref_at': (132.842, 45.72, 90), 'val_at': (130.81, 45.72, 90)})

# --- wejscia (jack -> bezposrednio do galezi krzyzowej R403/R404 ORAZ,
#     odgalezieniem nad/pod nia, do toru prostego R401/R402 - bez udzialu
#     przelacznika po tej stronie) ---
wire(pin('J401', 1), (45.72, 30.48))
wire((45.72, 30.48), (45.72, 26.67))
wire((45.72, 26.67), pin('R403', 1))                # -> galaz krzyzowa (wprost)
wire((45.72, 26.67), (45.72, 22.86))
wire((45.72, 22.86), (151.13, 22.86))
wire((151.13, 22.86), pin('R401', 1))               # -> tor prosty (nad galezia krzyzowa)
junc((45.72, 26.67))
wire(pin('J402', 1), (45.72, 53.34))
wire((45.72, 53.34), (45.72, 60.96))
wire((45.72, 60.96), pin('R404', 1))                # -> galaz krzyzowa (wprost)
wire((45.72, 60.96), (45.72, 64.77))
wire((45.72, 64.77), (151.13, 64.77))
wire((151.13, 64.77), pin('R402', 1))               # -> tor prosty (pod galezia krzyzowa)
junc((45.72, 60.96))
gnd(*pin('J401', 2))
gnd(*pin('J402', 2))

# --- tor prosty (ZAWSZE wpiety): R401||C401 (kanal L), R402||C402 (kanal P)
#     miedzy wezlem wejsciowym a wezlem "out" ---
wire(pin('R401', 1), pin('C401', 1))                # inL strona R401/C401
wire(pin('R401', 2), pin('C401', 2))                # outL strona
wire(pin('R402', 1), pin('C402', 1))                # inR strona
wire(pin('R402', 2), pin('C402', 2))                # outR strona

# --- magistrale wyjsciowe outL (x=175) / outR (x=185), zbieraja tez galaz
#     krzyzowa przeciwnego kanalu POPRZEZ SW401 (COM sekcji B->outL,
#     COM sekcji A->outR) ---
wire(pin('C401', 2), (175.26, 26.67))
wire((175.26, 21.59), (175.26, 49.53)); junc((175.26, 26.67))
wire((175.26, 21.59), (39.37, 21.59)); wire((39.37, 21.59), (39.37, 133.35))
wire(pin('C402', 2), (185.42, 60.96))
wire((185.42, 36.83), (185.42, 63.5)); junc((185.42, 60.96))
wire((185.42, 63.5), (20.32, 63.5))
wire((20.32, 63.5), (20.32, 238.76)); wire((20.32, 238.76), (39.37, 238.76))

# --- galaz krzyzowa L -> P: R403(2k2) wprost z gniazda -> mL, C403(220n)
#     mL->GND, R405(3k3) mL -> SW401 sekcja A (styk 1) -> COM (pin 2) ->
#     magistrala outR (kanal P) ---
wire(pin('R403', 2), (113.03, 26.67)); wire((113.03, 26.67), pin('C403', 1))
junc(pin('C403', 1))
wire(pin('C403', 2), (120.65, 33.02)); gnd(120.65, 33.02)
wire(pin('C403', 1), (130.81, 33.02)); wire((130.81, 33.02), pin('R405', 1))
wire(pin('R405', 2), pin('SW401', 1, unit=1))       # R405 -> styk A (obaj na y=36,83)
noconn(pin('SW401', 3, unit=1))                     # NC = pozycja "prosty" (galaz plywajaca)
wire(pin('SW401', 2, unit=1), (185.42, 39.37))
wire((185.42, 39.37), (185.42, 36.83))              # COM A -> magistrala outR

# --- galaz krzyzowa P -> L: R404(2k2) wprost z gniazda -> mR, C404(220n)
#     mR->GND, R406(3k3) mR -> SW401 sekcja B (styk 4) -> COM (pin 5) ->
#     magistrala outL (kanal L) ---
wire(pin('R404', 2), (113.03, 60.96)); wire((113.03, 60.96), pin('C404', 1))
junc(pin('C404', 1))
wire(pin('C404', 2), (120.65, 45.72)); gnd(120.65, 45.72)
wire(pin('C404', 1), (130.81, 45.72)); wire((130.81, 45.72), pin('R406', 1))
wire(pin('R406', 2), pin('SW401', 4, unit=2))       # R406 -> styk B (obaj na y=49,53)
noconn(pin('SW401', 6, unit=2))                     # NC = pozycja "prosty" (galaz plywajaca)
wire(pin('SW401', 5, unit=2), (175.26, 52.07))
wire((175.26, 52.07), (175.26, 49.53))              # COM B -> magistrala outL

text("S1 crossfeed: ON = przesluch -14 dB w basie (<700 Hz), OFF = tor prosty",
     92, 20, 1.27)

# =======================================================================
#  WYJSCIE (Etap B): jack sluchawkowy 6,3mm TRS J403 (DT 770 M, 80R).
#  T=L (T1 wtorne), R=P (T201 wtorne), S=GND (wspolna, jak wtorne OPT).
# =======================================================================
place('J403', 'Connector_Audio:AudioJack3', 'jack 6,3mm TRS (DT 770 M 80R)', 299.72, 190.5,
      fields={'ref_at': (289.56, 200.66, 0), 'val_at': (277.24, 205.74, 0)})
wire((222.25, 102.87), (285.75, 102.87), (285.75, pin('J403', 'T')[1]))
wire((285.75, pin('J403', 'T')[1]), pin('J403', 'T'))
junc((285.75, 102.87))
wire((222.25, 208.28), (280.67, 208.28), (280.67, pin('J403', 'R')[1]))
wire((280.67, pin('J403', 'R')[1]), pin('J403', 'R'))
junc((280.67, 208.28))
wire(pin('J403', 'S'), (304.8, 175.26)); gnd(304.8, 175.26)

# --- zarniki lamp NIE SA RYSOWANE (DECYZJA 2026-09-08) - unity grzania
#     ECC82 (U1 unit3), EL84 audio L (U2 unit2), EL84 audio P (U202 unit2)
#     usuniete razem z drutami/etykietami; ERC zglosi "missing_unit" dla
#     tych 3 nieumieszczonych unitow - OCZEKIWANE (patrz CLAUDE.md). Blok
#     zarzenia w zasilaczu (nizej) konczy sie etykietami HEAT_A/HEAT_B, z
#     adnotacja opisujaca podlaczenie zarnikow (patrz tekst przy U301). ---

# =======================================================================
#  ZASILACZ (Etap 5b) - layout drutami jak riaa/gen.py (bez etykiet
#  pomocniczych), pod obydwoma kanalami audio + grzaniem. Wartosci z
#  common/README.md i docs/PROJEKT-RIAA.md (sekcja zasilacza) - patrz
#  DECYZJE w docs/PROJEKT-HEADAMP.md. Wspolny B+ (+300V) dla obu kanalow
#  (bez podzialu per-kanal jak w RIAA - headamp ma jedno wzmocnienie na
#  kanal, mniejszy prad, nie potrzeba oddzielnych filtrow).
# =======================================================================

# PSU_DY - przesuniecie calego bloku zasilacza w Y. Etap 5b: 76,2mm (miejsce
# na rzad zarnikow lamp, usuniety w Etapie 6). Etap "kosmetyka arkusza"
# (2026-09-08, poprawki): miedzy ramka KANAL P (koniec Y=282,41) a rzedem
# zasilacza zostawal pusty pas ~57,6mm - PSU_DY zmniejszony o SHIFT=49,53mm
# (39*1,27mm - wielokrotnosc siatki, zeby wszystko zostalo na gridzie) do
# 26,67mm (nowy pas ~8mm, jak miedzy innymi modulami). Wspolrzedne ponizej
# zapisane jako juz-wyliczone wartosci absolutne (nie "baza + PSU_DY") zostaly
# recznie przeliczone o ten sam SHIFT (patrz komentarze przy nich) - reszta
# bloku uzywa PSU_DY/LR/NR/YP/YM/YHP/YHM wiec przesuwa sie automatycznie.
PSU_DY = 26.67

# --- siec (mains) ---
LR, NR = 292.1 + PSU_DY, 311.15 + PSU_DY          # L rail / N rail
place('J1', 'Connector:Screw_Terminal_01x03', 'MAINS 230V', 35.56, 294.64 + PSU_DY, mirror='y',
      fields={'ref_at': (30.48, 287.02 + PSU_DY, 0), 'val_at': (30.48, 289.56 + PSU_DY, 0)})
place('F1', 'Device:Fuse', 'T500mA', 49.53, LR, rot=90,
      fields={'ref_at': (49.53, 312.42, 90), 'val_at': (49.53, 308.61, 90)})  # -SHIFT(49.53) z 361.95/358.14
place('SW1', 'Switch:SW_DPST_x2', 'ON/OFF', 58.42, LR, unit=1,
      fields={'ref_at': (54.61, 287.02 + PSU_DY, 0), 'val_at': (54.61, 289.56 + PSU_DY, 0)})
place('SW1', 'Switch:SW_DPST_x2', 'ON/OFF', 58.42, NR, unit=2,
      fields={'ref_at': (48.26, 313.69 + PSU_DY, 0), 'val_at': (48.26, 316.23 + PSU_DY, 0)})
place('RT1', 'Device:Thermistor_NTC', 'NTC 10R', 69.85, LR, rot=90,
      fields={'ref_at': (64.77, 287.02 + PSU_DY, 0), 'val_at': (64.77, 289.56 + PSU_DY, 0)})
place('T301', 'Device:Transformer_1P_2S', 'EI84 100VA: 230V : 250V/0,15A + 7V/3A',
      106.68, 297.18 + PSU_DY,
      fields={'ref_at': (100.33, 276.86 + PSU_DY, 0), 'val_at': (93.98, 318.77 + PSU_DY, 0)})
wire(pin('J1', 1), pin('F1', 1))
wire(pin('F1', 2), pin('SW1', 1, unit=1))
wire(pin('SW1', 2, unit=1), pin('RT1', 1))
wire(pin('RT1', 2), (77.47, LR), (82.55, LR), (88.9, LR), (92.71, LR), pin('T301', 1))
junc((77.47, LR)); junc((82.55, LR)); junc((88.9, LR))
wire(pin('J1', 2), (43.18, 294.64 + PSU_DY), (43.18, NR), (53.34, NR))
wire(pin('SW1', 4, unit=2), (77.47, NR), (88.9, NR), (92.71, NR),
     (92.71, pin('T301', 2)[1]), pin('T301', 2))
junc((77.47, NR)); junc((88.9, NR))
# PE (flaga i symbol PE rozsuniete, zeby ich Value nie nachodzily na
# numery pinow J1 ani na siebie nawzajem)
wire(pin('J1', 3), (41.91, 297.18 + PSU_DY), (41.91, 299.72 + PSU_DY), (41.91, 308.61 + PSU_DY))
pe(41.91, 308.61 + PSU_DY)
wire((41.91, 299.72 + PSU_DY), (33.02, 299.72 + PSU_DY), (33.02, 302.26 + PSU_DY)); junc((41.91, 299.72 + PSU_DY))
pwrflag(33.02, 302.26 + PSU_DY)
text("PE -> wlasna sruba M4 na chassis", 22.86, 313.69 + PSU_DY, 1.27)
# warystor + neonowka (kontrolka) przez uzwojenie pierwotne, za wylacznikiem
place('RV301', 'Device:Varistor', 'S14K275', 77.47, 302.26 + PSU_DY,
      fields={'ref_at': (71.12, 300.99 + PSU_DY, 0), 'val_at': (69.85, 303.53 + PSU_DY, 0), 'val_just': 'right'})
wire((77.47, LR), (77.47, pin('RV301', 1)[1]))
wire(pin('RV301', 2), (77.47, NR))
place('R301', 'Device:R', '220k', 88.9, 322.58,  # -SHIFT(49.53) z 372.11
      fields={'ref_at': (90.17, 321.31, 90), 'val_at': (90.17, 323.85, 90)})
place('NE1', 'Device:Lamp_Neon', 'NE-2 (jewel)', 88.9, 331.47,  # -SHIFT z 381.0
      fields={'ref_at': (93.98, 330.2, 0), 'val_at': (93.98, 332.74, 0)})
wire((88.9, LR), pin('R301', 1))
wire(pin('R301', 2), pin('NE1', 2))
wire(pin('NE1', 1), (88.9, NR))
text("230V/0,15A (HT)", 88.9, 285.75 + PSU_DY, 1.27)
text("7V/3A (zarzenie)", 88.9, 309.88 + PSU_DY, 1.27)

# --- mostek HT (UF4007) + snubber RC + filtr CLC ---
YP, YM = 276.86 + PSU_DY, 309.88 + PSU_DY
place('D301', 'Device:D', 'UF4007', 127.0, 280.67 + PSU_DY, rot=270)
place('D302', 'Device:D', 'UF4007', 142.24, 280.67 + PSU_DY, rot=270)
place('D303', 'Device:D', 'UF4007', 127.0, 306.07 + PSU_DY, rot=270)
place('D304', 'Device:D', 'UF4007', 142.24, 306.07 + PSU_DY, rot=270)
# AC1 (T301 sec HT, pin3=SA) - D301.A (K->A, top->bottom of D301) - D303.K
wire(pin('D301', 2), pin('D303', 1))                       # pionowa noga AC1 (x=127)
wire(pin('T301', 3), (127.0, 313.69))  # -SHIFT(49.53) z 363.22
junc((127.0, 313.69))
# AC2 (T301 sec HT, pin4=SB) - D302.A - D304.K
wire(pin('D302', 2), pin('D304', 1))                       # pionowa noga AC2 (x=142.24)
wire(pin('T301', 4), (142.24, 321.31))  # -SHIFT z 370.84
junc((142.24, 321.31))
place('R302', 'Device:R', '470R', 130.81, 298.45 + PSU_DY, rot=90,
      fields={'ref_at': (127.0, 300.99 + PSU_DY, 90), 'val_at': (127.0, 303.53 + PSU_DY, 90)})
place('C301', 'Device:C', '10n/1kV', 138.43, 298.45 + PSU_DY, rot=90,
      fields={'ref_at': (134.62, 293.37 + PSU_DY, 0), 'val_at': (134.62, 295.91 + PSU_DY, 0)})
wire(pin('R302', 2), pin('C301', 1))
junc(pin('R302', 1)); junc(pin('C301', 2))
wire(pin('D301', 1), (142.24, YP), (151.13, YP)); junc((142.24, YP))
wire(pin('D303', 2), (142.24, YM), (146.05, YM)); junc((142.24, YM))
place('C302', 'Device:C_Polarized', '220u/400V', 151.13, 280.67 + PSU_DY,
      fields={'ref_at': (153.67, 285.75 + PSU_DY, 0), 'val_at': (153.67, 288.29 + PSU_DY, 0),
              'tol_at': (153.67, 290.83 + PSU_DY, 0)}, tol='20%')
place('L1', 'Device:L_Iron', '5-10H 100mA', 163.83, YP, rot=90,
      fields={'ref_at': (160.02, 271.78 + PSU_DY, 0), 'val_at': (166.37, 271.78 + PSU_DY, 0), 'val_just': 'left'})
text("L1 = dlawik zasilacza (nie mylic z Lp OPT >=25H - patrz T1/T201)", 151.13, 259.08 + PSU_DY, 1.27)
place('C303', 'Device:C_Polarized', '220u/400V', 176.53, 280.67 + PSU_DY,
      fields={'ref_at': (178.94, 285.75 + PSU_DY, 0), 'val_at': (178.94, 288.29 + PSU_DY, 0),
              'tol_at': (178.94, 290.83 + PSU_DY, 0)}, tol='20%')
wire((151.13, YP), pin('C302', 1)); junc((151.13, YP))
wire((151.13, YP), pin('L1', 1))
wire(pin('L1', 2), (176.53, YP)); junc((176.53, YP))
wire((176.53, YP), pin('C303', 1))
place('R303', 'Device:R', '220k/2W', 187.96, 280.67 + PSU_DY,
      fields={'ref_at': (189.99, 278.13 + PSU_DY, 90), 'val_at': (187.96, 278.13 + PSU_DY, 90),
              'tol_at': (185.93, 278.13 + PSU_DY, 90)}, tol='5%')
wire((176.53, YP), (187.96, YP)); junc((187.96, YP))
wire((187.96, YP), pin('R303', 1))
wire(pin('R303', 2), (187.96, YM))
wire((176.53, YP), (176.53, 266.7 + PSU_DY))
# masa filtra (jeden wspolny szyna GND, rozciagnieta az do elewacji
# R305/C304 - patrz nizej)
wire(pin('C302', 2), (151.13, YM))
wire(pin('C303', 2), (176.53, YM))
wire((146.05, YM), (151.13, YM), (176.53, YM), (187.96, YM), (210.82, YM), (218.44, YM))
for x in (151.13, 176.53, 187.96, 210.82, 218.44):
    junc((x, YM))
gnd(160.02, 313.69 + PSU_DY)
wire((160.02, YM), (160.02, 313.69 + PSU_DY))
junc((160.02, YM))

# --- elewacja zarzenia (+ELEV z B+ przez dzielnik) ---
place('R304', 'Device:R', '220k', 210.82, 281.94 + PSU_DY,
      fields={'ref_at': (212.09, 279.4 + PSU_DY, 0), 'val_at': (212.09, 281.94 + PSU_DY, 0)})
place('R305', 'Device:R', '47k', 210.82, 294.64 + PSU_DY,
      fields={'ref_at': (204.47, 293.37 + PSU_DY, 0), 'val_at': (208.28, 295.91 + PSU_DY, 0), 'val_just': 'right'})
wire(pin('R304', 1), (210.82, 266.7 + PSU_DY))
wire(pin('R304', 2), (210.82, 288.29 + PSU_DY))
wire((210.82, 288.29 + PSU_DY), pin('R305', 1))
wire(pin('R305', 2), (210.82, YM))
place('C304', 'Device:C_Polarized', '10u/100V', 218.44, 294.64 + PSU_DY,
      fields={'ref_at': (220.98, 296.52 + PSU_DY, 0), 'val_at': (220.98, 299.06 + PSU_DY, 0),
              'tol_at': (220.98, 301.6 + PSU_DY, 0)}, tol='20%')
wire((210.82, 288.29 + PSU_DY), (218.44, 288.29 + PSU_DY), pin('C304', 1))
junc((210.82, 288.29 + PSU_DY))
wire(pin('C304', 2), (218.44, YM))
label('ELEV', (213.36, 288.29 + PSU_DY))

# --- rozladowanie B+ (K1 + R306), 1:1 z riaa/common ---
place('K1', 'Relay:Relay_SPDT', '9V', 242.57, 280.67 + PSU_DY,
      fields={'ref_at': (251.46, 283.21 + PSU_DY, 0), 'val_at': (251.46, 285.75 + PSU_DY, 0)})
place('D305', 'Device:D', '1N4007', 229.87, 280.67 + PSU_DY, rot=270,
      fields={'ref_at': (222.25, 276.86 + PSU_DY, 0), 'val_at': (227.33, 279.4 + PSU_DY, 0), 'val_just': 'right'})
place('R306', 'Device:R', '4k7/10W', 247.65, 294.64 + PSU_DY,
      fields={'ref_at': (240.03, 292.1 + PSU_DY, 0), 'val_at': (245.11, 295.91 + PSU_DY, 0), 'val_just': 'right'})
wire(pin('K1', 'A1'), (237.49, 270.51 + PSU_DY), (231.14, 270.51 + PSU_DY))
label('V_RAW', (231.14, 270.51 + PSU_DY), just='right bottom')
# V_RAW zasilany tylko przez diody mostka (nie "power output" dla ERC) ->
# jeden PWR_FLAG na cala siec, zeby U301.VI (power input) mial sterownik.
pwrflag(231.14, 270.51 + PSU_DY - 2.54)
wire((231.14, 270.51 + PSU_DY), (231.14, 270.51 + PSU_DY - 2.54))
wire(pin('K1', 'A2'), (237.49, 293.37 + PSU_DY), (231.14, 293.37 + PSU_DY))
label('ELEV', (231.14, 293.37 + PSU_DY), just='right bottom')
wire(pin('D305', 1), (229.87, 273.05 + PSU_DY), (237.49, 273.05 + PSU_DY)); junc((237.49, 273.05 + PSU_DY))
wire(pin('D305', 2), (229.87, 288.29 + PSU_DY), (237.49, 288.29 + PSU_DY)); junc((237.49, 288.29 + PSU_DY))
wire(pin('K1', 12), (245.11, 267.97 + PSU_DY))
noconn(pin('K1', 14))
wire(pin('K1', 11), (247.65, 290.83 + PSU_DY))
wire(pin('R306', 2), (247.65, 300.99 + PSU_DY)); gnd(247.65, 300.99 + PSU_DY)
text("Rozladowanie: przy zaniku sieci K1 zwalnia, styk NC (11-12) laczy +300V z R306", 218.44, 320.04 + PSU_DY, 1.27)
text("-> B+ <50V w ok. 15 s. K1: cewka 9V (V_RAW), styki min. 250V. Bleeder R303 = wolna 2. linia.", 218.44, 322.58 + PSU_DY, 1.27)

# --- B+ (+300V) bus: laczy 3 punkty zasilacza (CLC, R304/elewacja, K1) z
#     korytarzami obu kanalow (chan(), BUS_X=245.11) - hybryda "druty
#     zamiast etykiet" (DECYZJA 2026-09-08), zastepuje global_label('+300V')
#     z commitu fc227e8.
_bp_y1 = 266.7 + PSU_DY   # = poziom CLC (176.53) i R304 (210.82)
_bp_y2 = 267.97 + PSU_DY  # = poziom K1 pin12 (245.11 = BUS_X)
wire((176.53, _bp_y1), (210.82, _bp_y1)); junc((210.82, _bp_y1))
wire((210.82, _bp_y1), (BUS_X, _bp_y1))
wire((BUS_X, _bp_y1), (BUS_X, _bp_y2))
wire((BUS_X, 80.01), (BUS_X, 185.42)); junc((BUS_X, 185.42))
wire((BUS_X, 185.42), (BUS_X, _bp_y1)); junc((BUS_X, _bp_y1))

# --- zarzenie: 7V -> mostek 1N5822 -> 10000u -> LD1085 (LDO) -> HEAT_A/HEAT_B ---
YHP, YHM = 312.42 + PSU_DY, 335.28 + PSU_DY
place('D306', 'Device:D', '1N5822', 287.02, 316.23 + PSU_DY, rot=270)
place('D307', 'Device:D', '1N5822', 299.72, 316.23 + PSU_DY, rot=270)
place('D308', 'Device:D', '1N5822', 287.02, 331.47 + PSU_DY, rot=270)
place('D309', 'Device:D', '1N5822', 299.72, 331.47 + PSU_DY, rot=270)
# AC1 (T301 sec zarzenia, pin5=SC) - D306.A / D308.K
wire(pin('D306', 2), pin('D308', 1))
wire(pin('T301', 5), (116.84, 350.52), (287.02, 350.52))  # -SHIFT(49.53) z 400.05
junc((287.02, 350.52))
# AC2 (T301 sec zarzenia, pin6=SD) - D307.A / D309.K (odsuniete o 2,54mm w X,
# zeby nie pokryc sie z galezia AC1)
wire(pin('D307', 2), pin('D309', 1))
wire(pin('T301', 6), (119.38, 334.01), (119.38, 354.33), (299.72, 354.33))  # -SHIFT z 383.54/403.86
junc((299.72, 354.33))
place('C305', 'Device:C_Polarized', '10000u/16V', 317.5, 316.23 + PSU_DY, tol='20%')
place('C306', 'Device:C_Polarized', '470u/25V', 337.82, 316.23 + PSU_DY,
      fields={'ref_at': (331.47, 320.04 + PSU_DY, 0), 'val_at': (336.55, 323.85 + PSU_DY, 0),
              'tol_at': (336.55, 326.39 + PSU_DY, 0), 'val_just': 'right'}, tol='20%')
place('U301', 'Regulator_Linear:LM317_TO-220', 'LD1085 (LDO)', 351.79, YHP,
      fields={'ref_at': (356.87, 303.53 + PSU_DY, 0), 'val_at': (356.87, 306.07 + PSU_DY, 0)})
wire(pin('D306', 1), (299.72, YHP), (317.5, YHP))
junc((299.72, YHP)); junc((317.5, YHP))
wire((317.5, YHP), pin('C305', 1))
wire((317.5, YHP), (337.82, YHP)); junc((337.82, YHP))
label('V_RAW', (320.04, YHP))
wire((337.82, YHP), pin('C306', 1))
wire((337.82, YHP), pin('U301', 3))
place('R307', 'Device:R', '240R', 364.49, 316.23 + PSU_DY, tol='1%')
place('R308', 'Device:R', '976R', 364.49, 326.39 + PSU_DY,
      fields={'ref_at': (358.14, 321.31 + PSU_DY, 0), 'val_at': (356.87, 326.39 + PSU_DY, 0),
              'tol_at': (356.87, 328.93 + PSU_DY, 0), 'val_just': 'right'}, tol='1%')
place('C307', 'Device:C_Polarized', '10u/25V', 372.11, 323.85 + PSU_DY,
      fields={'ref_at': (374.65, 320.04 + PSU_DY, 0), 'val_at': (374.65, 328.93 + PSU_DY, 0),
              'tol_at': (374.65, 331.47 + PSU_DY, 0)}, tol='20%')
place('C308', 'Device:C', '1u', 379.73, 316.23 + PSU_DY,
      fields={'ref_at': (382.27, 315.29 + PSU_DY, 0), 'val_at': (382.27, 317.83 + PSU_DY, 0)})
wire(pin('U301', 2), (364.49, YHP)); junc((364.49, YHP))
wire((364.49, YHP), pin('R307', 1))
wire(pin('U301', 1), (351.79, 320.04 + PSU_DY), (364.49, 320.04 + PSU_DY))
wire(pin('R307', 2), pin('R308', 1))
junc((364.49, 320.04 + PSU_DY))
wire((364.49, 320.04 + PSU_DY), (372.11, 320.04 + PSU_DY), pin('C307', 1))
wire(pin('R308', 2), (364.49, YHM))
wire(pin('C307', 2), (372.11, YHM))
wire((364.49, YHP), (379.73, YHP)); junc((379.73, YHP))
wire((379.73, YHP), pin('C308', 1))
wire(pin('C308', 2), (379.73, YHM))
wire((379.73, YHP), (384.81, YHP), (387.35, YHP))
wire(pin('D308', 2), (299.72, YHM), (317.5, YHM), (337.82, YHM), (364.49, YHM), (372.11, YHM),
     (379.73, YHM), (384.81, YHM), (387.35, YHM))
wire(pin('C305', 2), (317.5, YHM))
wire(pin('C306', 2), (337.82, YHM))
for x in (299.72, 317.5, 337.82, 364.49, 372.11, 379.73):
    junc((x, YHM))
wire((287.02, YHM), (281.94, YHM))
label('ELEV', (281.94, YHM), just='right bottom')
# HEAT_A ma sterownik (U301.VO); HEAT_B (powrot zarzenia) - PWR_FLAG tutaj,
# na koncu drutu wychodzacego z bloku (Etap 6, DECYZJA 2026-09-08: zarniki
# lamp nie sa rysowane - flaga z Etapu 5a przy grzaniu lamp usunieta razem
# z tamtym blokiem, przeniesiona tutaj, jedyne miejsce gdzie siec HEAT_B
# jeszcze istnieje).
pwrflag(387.35, YHM + 2.54, rot=180)
wire((387.35, YHM), (387.35, YHM + 2.54))
junc((384.81, YHP)); junc((384.81, YHM))

# =======================================================================
#  ZARNIKI LAMP (Etap "kosmetyka arkusza", 2026-09-08, DECYZJA - wariant a):
#  zarniki ECC82 (U1 unit3), EL84 audio L (U2 unit2), EL84 audio P (U202
#  unit2) PRZYWROCONE na schemat, WEWNATRZ ramki ZARZENIE, polaczone
#  DRUTAMI (nie etykietami) z wyjsciem VO (+6,3V, szyna na wysokosci YHP)
#  i z minusem zarzenia (szyna na wysokosci YHM, ta sama siec co ELEV).
#  Wszystkie piny zbiegaja sie na wspolnej linii bazowej Y_HEAT_PINS
#  (dokladnie w polowie miedzy YHP i YHM - stad brak kolizji: piny "+"
#  (F1) kazdej lampy odchodza w gore do YHP, piny "-" (F2/pin9) w dol do
#  YHM, nigdy nie dziela tego samego odcinka).
#  ECC82: piny 4 i 5 (oba F1) -> +6,3V; pin 9 (F2) -> minus (srodkowy
#  odczep zarzenia, zgodnie z zaleceniem - redukcja hum).
#  EL84: pin 4 (F1) -> +6,3V; pin 5 (F2) -> minus.
# =======================================================================
Y_HEAT_PINS = (YHP + YHM) / 2   # = 350.52, w polowie odleglosci YHP<->YHM (22.86mm)
HEAT_X1, HEAT_X2, HEAT_X3 = 402.59, 433.07, 463.55   # ECC82, EL84(U2 L), EL84(U202 P) - siatka 1.27mm

place('U1', 'Valve:ECC81', 'ECC82', HEAT_X1, Y_HEAT_PINS - 11.43, unit=3,
      fields={'ref_at': (HEAT_X1 + 5.08, Y_HEAT_PINS - 24.13, 0),
              'val_at': (HEAT_X1 + 5.08, Y_HEAT_PINS - 21.59, 0)})
place('U2', 'Valve:EL84', 'EL84 (trioda)', HEAT_X2, Y_HEAT_PINS - 10.16, unit=2,
      fields={'ref_at': (HEAT_X2 + 5.08, Y_HEAT_PINS - 22.86, 0),
              'val_at': (HEAT_X2 + 5.08, Y_HEAT_PINS - 20.32, 0)})
place('U202', 'Valve:EL84', 'EL84 (trioda)', HEAT_X3, Y_HEAT_PINS - 10.16, unit=2,
      fields={'ref_at': (HEAT_X3 + 5.08, Y_HEAT_PINS - 22.86, 0),
              'val_at': (HEAT_X3 + 5.08, Y_HEAT_PINS - 20.32, 0)})

# ECC82: piny 4/5 (F1) w gore do szyny +6,3V (YHP); pin 9 (F2) w dol do
# szyny minus (YHM). Wszystkie 3 piny wychodza z tej samej linii bazowej
# (Y_HEAT_PINS) ale w przeciwnych kierunkach - brak wspolnego odcinka.
wire(pin('U1', 4, unit=3), (HEAT_X1 - 2.54, YHP))
wire(pin('U1', 5, unit=3), (HEAT_X1 + 2.54, YHP))
wire(pin('U1', 9, unit=3), (HEAT_X1, YHM))

# EL84 (U2, kanal L): pin 4 (F1) w gore, pin 5 (F2) w dol.
wire(pin('U2', 4, unit=2), (HEAT_X2 - 2.54, YHP))
wire(pin('U2', 5, unit=2), (HEAT_X2 + 2.54, YHM))

# EL84 (U202, kanal P): pin 4 (F1) w gore, pin 5 (F2) w dol.
wire(pin('U202', 4, unit=2), (HEAT_X3 - 2.54, YHP))
wire(pin('U202', 5, unit=2), (HEAT_X3 + 2.54, YHM))

# szyna +6,3V (YHP) - przedluzona od U301.VO (387.35) przez wszystkie
# odczepy "+" trzech lamp (kolejnosc rosnaco w X)
wire((387.35, YHP), (HEAT_X1 - 2.54, YHP), (HEAT_X1 + 2.54, YHP),
     (HEAT_X2 - 2.54, YHP), (HEAT_X3 - 2.54, YHP))
for x in (HEAT_X1 - 2.54, HEAT_X1 + 2.54, HEAT_X2 - 2.54):
    junc((x, YHP))

# szyna minus zarzenia (YHM, = ELEV) - przedluzona od 387.35 przez
# wszystkie odczepy "-" trzech lamp
wire((387.35, YHM), (HEAT_X1, YHM), (HEAT_X2 + 2.54, YHM), (HEAT_X3 + 2.54, YHM))
junc((387.35, YHM))
for x in (HEAT_X1, HEAT_X2 + 2.54):
    junc((x, YHM))

text("Zarzenie: 6,3V DC / ok. 1,7A (2x EL84 0,76A + ECC82 0,15A; budzet 1,9A) z uzwojenia 7V/3A.",
     218.44, 344.17 + PSU_DY, 1.27)
text("Skrecona para na przewodach zarzenia. LD1085: blaszka = VOUT - izolacja od chassis.", 218.44, 346.71 + PSU_DY, 1.27)
text("LD1085 (LDO) - LM317 ma za duzy dropout przy 1,7A (V_RAW ~9V z uzwojenia 7V wystarcza).",
     218.44, 349.25 + PSU_DY, 1.27)
text("Zarzenie do lamp: skrecona para, minus = ELEV (+53V).", HEAT_X1, Y_HEAT_PINS + 26.67, 1.27)

# --- ground breaker (jedyny styk masy z chassis) ---
place('R309', 'Device:R', '10R/5W', 45.72, 325.12 + PSU_DY,
      fields={'ref_at': (39.37, 351.79, 90), 'val_at': (41.4, 351.79, 90)})  # -SHIFT z 401.32
place('D310', 'Device:D', '1N5408', 55.88, 325.12 + PSU_DY, rot=270,
      fields={'ref_at': (58.42, 349.25, 0), 'val_at': (58.42, 351.79, 0)})  # -SHIFT z 398.78/401.32
place('D311', 'Device:D', '1N5408', 66.04, 325.12 + PSU_DY, rot=90,
      fields={'ref_at': (68.58, 349.25, 0), 'val_at': (68.58, 351.79, 0)})  # -SHIFT z 398.78/401.32
place('C309', 'Device:C', '100n/630V', 76.2, 325.12 + PSU_DY,
      fields={'ref_at': (79.5, 351.79, 90), 'val_at': (81.5, 351.79, 90),
              'tol_at': (83.5, 351.79, 90)}, tol='10%')  # -SHIFT z 401.32
wire((40.64, 321.31 + PSU_DY), (45.72, 321.31 + PSU_DY), (55.88, 321.31 + PSU_DY), (66.04, 321.31 + PSU_DY), (76.2, 321.31 + PSU_DY))
wire((43.18, 328.93 + PSU_DY), (45.72, 328.93 + PSU_DY), (55.88, 328.93 + PSU_DY), (66.04, 328.93 + PSU_DY), (76.2, 328.93 + PSU_DY))
for x in (45.72, 55.88, 66.04):
    junc((x, 321.31 + PSU_DY)); junc((x, 328.93 + PSU_DY))
gnd(40.64, 321.31 + PSU_DY)
pe(43.18, 328.93 + PSU_DY, rot=180)
text("Ground breaker (jedyny styk masy z chassis): 10R przerywa petle masy;", 27.94, 340.36 + PSU_DY, 1.27)
text("przy usterce diody zwieraja GND do PE i bezpiecznik zadziala.", 27.94, 342.9 + PSU_DY, 1.27)

text("UWAGA: napiecia do ok. 330V DC - smiertelnie niebezpieczne. Po wylaczeniu odczekac na", 27.94, 347.98 + PSU_DY, 1.6)
text("rozladowanie (K1) i SPRAWDZIC woltomierzem KAZDA sekcje (<50V) przed praca.", 27.94, 350.52 + PSU_DY, 1.6)

# =======================================================================
#  RAMKI MODULOW (Etap A, DECYZJA 2026-09-08 "layout w ramkach") - czysto
#  graficzne (rectangle na arkuszu), druty moga je przechodzic swobodnie.
#  WEJSCIE/WYJSCIE rezerwowane puste (komponenty - Etap B, crossfeed+gniazda).
# =======================================================================
frame(15, 15, 255, 68, "WEJSCIE: gniazda RCA, crossfeed S1, glosnosc RV1")
frame(15, 74, 255, 177, "KANAL L: 1/2 ECC82 -> EL84 (trioda) -> OPT")
frame(15, 179.41, 255, 282.41, "KANAL P: 1/2 ECC82 -> EL84 (trioda) -> OPT")
frame(262, 130, 330, 235, "WYJSCIE: jack 6,3 mm")
frame(15, 290.47, 122, 380.47, "SIEC 230V + ground breaker")
frame(122, 290.47, 262, 380.47, "ZASILACZ B+ 300V (CLC) + rozladowanie K1")
frame(262, 290.47, 495.3, 380.47, "ZARZENIE 6,3V DC (LD1085, elewacja ELEV)")

# =======================================================================
#  serialize
# =======================================================================
def fmt(v):
    s = ('%.3f' % v).rstrip('0').rstrip('.')
    return s if s else '0'


def dedup_juncs(pts):
    seen = []
    for p in pts:
        if p not in seen:
            seen.append(p)
    return seen


out = []
out.append('(kicad_sch')
out.append('  (version 20231120)')
out.append('  (generator "eeschema")')
out.append('  (uuid "%s")' % ROOT)
out.append('  (paper "A2")')
out.append('  (lib_symbols')
out.extend(EMBED)
out.append('  )')
out.append('''  (title_block
    (title "TERCET headamp - SE EL84 (trioda) + 1/2 ECC82, OPT 5k:80")
    (company "TERCET")
    (comment 1 "Wzmacniacz sluchawkowy pod DT 770 M (80R); zero polprzewodnikow w torze")
    (comment 2 "Zrodlo prawdy: headamp/gen.py (check.py = asercje netlisty)")
  )''')

for p in dedup_juncs(JUNCS):
    out.append('  (junction (at %s %s) (diameter 0) (uuid %s))'
               % (fmt(p[0]), fmt(p[1]), U('junc:%s,%s' % (fmt(p[0]), fmt(p[1])))))
for (a, b) in WIRES:
    out.append('  (wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))'
                % (fmt(a[0]), fmt(a[1]), fmt(b[0]), fmt(b[1]),
                   U('wire:%s,%s-%s,%s' % (fmt(a[0]), fmt(a[1]), fmt(b[0]), fmt(b[1])))))
for p in NOCONN:
    out.append('  (no_connect (at %s %s) (uuid %s))'
               % (fmt(p[0]), fmt(p[1]), U('noconn:%s,%s' % (fmt(p[0]), fmt(p[1])))))
for (x0, y0, x1, y1) in FRAMES:
    out.append('  (rectangle (start %s %s) (end %s %s) (stroke (width 0.254) (type default)) '
                '(fill (type none)) (uuid %s))'
                % (fmt(x0), fmt(y0), fmt(x1), fmt(y1),
                   U('frame:%s,%s-%s,%s' % (fmt(x0), fmt(y0), fmt(x1), fmt(y1)))))
for (name, p, rot, just) in LABELS:
    out.append('  (label "%s" (at %s %s %d) (effects (font (size 1.27 1.27)) (justify %s)) (uuid %s))'
                % (name, fmt(p[0]), fmt(p[1]), rot, just,
                   U('label:%s:%s,%s' % (name, fmt(p[0]), fmt(p[1])))))
for (name, p, rot, just) in GLABELS:
    out.append('  (global_label "%s" (shape input) (at %s %s %d) '
                '(effects (font (size 1.27 1.27)) (justify %s)) (uuid %s))'
                % (name, fmt(p[0]), fmt(p[1]), rot, just,
                   U('glabel:%s:%s,%s' % (name, fmt(p[0]), fmt(p[1])))))
for (s, x, y, size, rot) in TEXTS:
    out.append('  (text "%s" (at %s %s %d) (effects (font (size %s %s)) (justify left bottom)) (uuid %s))'
                % (s, fmt(x), fmt(y), rot, fmt(size), fmt(size),
                   U('text:%s,%s:%s' % (fmt(x), fmt(y), s[:30]))))

for s in SYMS:
    libid = s['libid']; x, y, rot = s['x'], s['y'], s['rot']
    mir = (' (mirror %s)' % s['mirror']) if s['mirror'] else ''
    power = libid.startswith('power:')
    geo = PINGEO[libid]
    u = s['unit'] if s['unit'] in geo else 0
    out.append('  (symbol (lib_id "%s") (at %s %s %d)%s (unit %d)' % (libid, fmt(x), fmt(y), rot, mir, s['unit']))
    out.append('    (in_bom yes) (on_board yes) (dnp no)')
    out.append('    (uuid %s)' % s['uuid'])
    if power:
        vy = y + 3.81 if (libid.endswith('GND') or rot == 180) else y - 3.81
        out.append('    (property "Reference" "%s" (at %s %s 0) (effects (font (size 1.27 1.27)) hide))'
                    % (s['ref'], fmt(x), fmt(y)))
        out.append('    (property "Value" "%s" (at %s %s 0) (effects (font (size 1.27 1.27))))'
                    % (s['value'], fmt(x), fmt(vy)))
    else:
        # domyslne polozenie Reference/Value (gdy 'fields' nie podaje ref_at/
        # val_at jawnie) - jak w riaa/gen.py: zalezne od typu/orientacji.
        horiz = rot in (90, 270)
        if libid == 'Device:D':
            drpos, dvpos, dtpos = (x + 2.54, y - 1.27, 0), (x + 2.54, y + 1.27, 0), (x + 2.54, y + 3.81, 0)
        elif horiz:
            drpos, dvpos, dtpos = (x - 3.81, y - 5.08, 0), (x - 3.81, y - 2.54, 0), (x - 3.81, y, 0)
        else:
            drpos, dvpos, dtpos = (x + 2.54, y - 1.27, 0), (x + 2.54, y + 1.27, 0), (x + 2.54, y + 3.81, 0)
        rpos = s['fields'].get('ref_at', drpos)
        vpos = s['fields'].get('val_at', dvpos)
        out.append('    (property "Reference" "%s" (at %s %s %d) (effects (font (size 1.27 1.27))))'
                    % (s['ref'], fmt(rpos[0]), fmt(rpos[1]), rpos[2]))
        out.append('    (property "Value" "%s" (at %s %s %d) (effects (font (size 1.27 1.27))))'
                    % (s['value'], fmt(vpos[0]), fmt(vpos[1]), vpos[2]))
    out.append('    (property "Footprint" "" (at %s %s 0) (effects (font (size 1.27 1.27)) hide))' % (fmt(x), fmt(y)))
    out.append('    (property "Datasheet" "" (at %s %s 0) (effects (font (size 1.27 1.27)) hide))' % (fmt(x), fmt(y)))
    if s['tol']:
        tx, ty, trot = s['fields'].get('tol_at', dtpos)
        out.append('    (property "Tolerance" "%s" (at %s %s %d) (effects (font (size 1.27 1.27))))'
                    % (s['tol'], fmt(tx), fmt(ty), trot))
    for num, px, py, a, l, nm in geo[u]:
        out.append('    (pin "%s" (uuid %s))'
                   % (num, U('pin:%s:u%d:%s' % (s['ref'], s['unit'], num))))
    out.append('    (instances (project "%s" (path "/%s" (reference "%s") (unit %d))))'
                % (PROJECT, ROOT, s['ref'], s['unit']))
    out.append('  )')

out.append('  (sheet_instances (path "/" (page "1")))')
out.append(')')

if __name__ == '__main__':
    outpath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'headamp.kicad_sch')
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print('wrote', outpath, len(SYMS), 'symbols,', len(WIRES), 'wires,', len(dedup_juncs(JUNCS)), 'junctions')
