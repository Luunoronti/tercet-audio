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

    glabel('+300V', (118.11, y(91.44)), rot=0, just='left')
    glabel('+300V', (196.85, y(102.87)), rot=180, just='right')
    glabel('IN_' + lbl, (39.37, y(133.35)), rot=0, just='left')
    glabel('OUT_' + lbl, (222.25, y(102.87)), rot=0, just='left')

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

# --- grzanie (heater) - jednostki wspolne: ECC82 (U1, unit 3, jeden dla
#     obu polowek/kanalow), EL84 audio L (U2, unit 2), EL84 audio P
#     (U202, unit 2). Odrebnie narysowane POD obydwoma kanalami audio
#     (przesuniete +64,77 mm wzgledem b7d6cc9, zeby nie kolidowac z
#     kanalem P - patrz DECYZJA w docs/PROJEKT-HEADAMP.md). ---
place('U1', 'Valve:ECC81', 'ECC82', 59.69, 289.56, unit=3,
      fields={'ref_at': (62.992, 281.686, 0), 'val_at': (68.58, 297.18, 0)})
place('U2', 'Valve:EL84', 'EL84 (trioda)', 90.17, 289.56, unit=2,
      fields={'ref_at': (92.71, 279.4, 0), 'val_at': (97.79, 297.18, 0)})
place('U202', 'Valve:EL84', 'EL84 (trioda)', 120.65, 289.56, unit=2,
      fields={'ref_at': (123.19, 279.4, 0), 'val_at': (128.27, 297.18, 0)})

# etykiety grzania + globalne + PWR_FLAG (dokladnie jak #PWR011..#PWR013,
# rozszerzone o U202)
label('HEAT_A', (57.15, 300.99))
label('HEAT_A', (62.23, 300.99))
label('HEAT_A', (87.63, 299.72))
label('HEAT_A', (118.11, 299.72))
label('HEAT_B', (59.69, 300.99))
label('HEAT_B', (92.71, 299.72))
label('HEAT_B', (123.19, 299.72))

# HEAT_A ma teraz sterownik (U301.VO w zasilaczu, Etap 5b) - flaga tylko
# na HEAT_B (bez naturalnego sterownika, to "powrot" zarzenia).
pwrflag(92.71, 299.72, rot=180)

# =======================================================================
#  ZASILACZ (Etap 5b) - layout drutami jak riaa/gen.py (bez etykiet
#  pomocniczych), pod obydwoma kanalami audio + grzaniem. Wartosci z
#  common/README.md i docs/PROJEKT-RIAA.md (sekcja zasilacza) - patrz
#  DECYZJE w docs/PROJEKT-HEADAMP.md. Wspolny B+ (+300V) dla obu kanalow
#  (bez podzialu per-kanal jak w RIAA - headamp ma jedno wzmocnienie na
#  kanal, mniejszy prad, nie potrzeba oddzielnych filtrow).
# =======================================================================

# --- siec (mains) ---
LR, NR = 292.1 + 76.2, 311.15 + 76.2          # L rail / N rail
place('J1', 'Connector:Screw_Terminal_01x03', 'MAINS 230V', 35.56, 294.64 + 76.2, mirror='y',
      fields={'ref_at': (30.48, 287.02 + 76.2, 0), 'val_at': (30.48, 289.56 + 76.2, 0)})
place('F1', 'Device:Fuse', 'T500mA', 49.53, LR, rot=90,
      fields={'ref_at': (49.53, 361.95, 90), 'val_at': (49.53, 358.14, 90)})
place('SW1', 'Switch:SW_DPST_x2', 'ON/OFF', 58.42, LR, unit=1,
      fields={'ref_at': (54.61, 287.02 + 76.2, 0), 'val_at': (54.61, 289.56 + 76.2, 0)})
place('SW1', 'Switch:SW_DPST_x2', 'ON/OFF', 58.42, NR, unit=2,
      fields={'ref_at': (48.26, 313.69 + 76.2, 0), 'val_at': (48.26, 316.23 + 76.2, 0)})
place('RT1', 'Device:Thermistor_NTC', 'NTC 10R', 69.85, LR, rot=90,
      fields={'ref_at': (64.77, 287.02 + 76.2, 0), 'val_at': (64.77, 289.56 + 76.2, 0)})
place('T301', 'Device:Transformer_1P_2S', 'EI84 100VA: 230V : 250V/0,15A + 7V/3A',
      106.68, 297.18 + 76.2,
      fields={'ref_at': (100.33, 276.86 + 76.2, 0), 'val_at': (93.98, 318.77 + 76.2, 0)})
wire(pin('J1', 1), pin('F1', 1))
wire(pin('F1', 2), pin('SW1', 1, unit=1))
wire(pin('SW1', 2, unit=1), pin('RT1', 1))
wire(pin('RT1', 2), (77.47, LR), (82.55, LR), (88.9, LR), (92.71, LR), pin('T301', 1))
junc((77.47, LR)); junc((82.55, LR)); junc((88.9, LR))
wire(pin('J1', 2), (43.18, 294.64 + 76.2), (43.18, NR), (53.34, NR))
wire(pin('SW1', 4, unit=2), (77.47, NR), (88.9, NR), (92.71, NR),
     (92.71, pin('T301', 2)[1]), pin('T301', 2))
junc((77.47, NR)); junc((88.9, NR))
# PE (flaga i symbol PE rozsuniete, zeby ich Value nie nachodzily na
# numery pinow J1 ani na siebie nawzajem)
wire(pin('J1', 3), (41.91, 297.18 + 76.2), (41.91, 299.72 + 76.2), (41.91, 308.61 + 76.2))
pe(41.91, 308.61 + 76.2)
wire((41.91, 299.72 + 76.2), (33.02, 299.72 + 76.2), (33.02, 302.26 + 76.2)); junc((41.91, 299.72 + 76.2))
pwrflag(33.02, 302.26 + 76.2)
text("PE -> wlasna sruba M4 na chassis", 22.86, 313.69 + 76.2, 1.27)
# warystor + neonowka (kontrolka) przez uzwojenie pierwotne, za wylacznikiem
place('RV301', 'Device:Varistor', 'S14K275', 77.47, 302.26 + 76.2,
      fields={'ref_at': (71.12, 300.99 + 76.2, 0), 'val_at': (69.85, 303.53 + 76.2, 0), 'val_just': 'right'})
wire((77.47, LR), (77.47, pin('RV301', 1)[1]))
wire(pin('RV301', 2), (77.47, NR))
place('R301', 'Device:R', '220k', 88.9, 372.11,
      fields={'ref_at': (90.17, 370.84, 90), 'val_at': (90.17, 373.38, 90)})
place('NE1', 'Device:Lamp_Neon', 'NE-2 (jewel)', 88.9, 381.0,
      fields={'ref_at': (93.98, 379.73, 0), 'val_at': (93.98, 382.27, 0)})
wire((88.9, LR), pin('R301', 1))
wire(pin('R301', 2), pin('NE1', 2))
wire(pin('NE1', 1), (88.9, NR))
text("230V/0,15A (HT)", 88.9, 285.75 + 76.2, 1.27)
text("7V/3A (zarzenie)", 88.9, 309.88 + 76.2, 1.27)

# --- mostek HT (UF4007) + snubber RC + filtr CLC ---
YP, YM = 276.86 + 76.2, 309.88 + 76.2
place('D301', 'Device:D', 'UF4007', 127.0, 280.67 + 76.2, rot=270)
place('D302', 'Device:D', 'UF4007', 142.24, 280.67 + 76.2, rot=270)
place('D303', 'Device:D', 'UF4007', 127.0, 306.07 + 76.2, rot=270)
place('D304', 'Device:D', 'UF4007', 142.24, 306.07 + 76.2, rot=270)
# AC1 (T301 sec HT, pin3=SA) - D301.A (K->A, top->bottom of D301) - D303.K
wire(pin('D301', 2), pin('D303', 1))                       # pionowa noga AC1 (x=127)
wire(pin('T301', 3), (127.0, 363.22))
junc((127.0, 363.22))
# AC2 (T301 sec HT, pin4=SB) - D302.A - D304.K
wire(pin('D302', 2), pin('D304', 1))                       # pionowa noga AC2 (x=142.24)
wire(pin('T301', 4), (142.24, 370.84))
junc((142.24, 370.84))
place('R302', 'Device:R', '470R', 130.81, 298.45 + 76.2, rot=90,
      fields={'ref_at': (127.0, 300.99 + 76.2, 90), 'val_at': (127.0, 303.53 + 76.2, 90)})
place('C301', 'Device:C', '10n/1kV', 138.43, 298.45 + 76.2, rot=90,
      fields={'ref_at': (134.62, 293.37 + 76.2, 0), 'val_at': (134.62, 295.91 + 76.2, 0)})
wire(pin('R302', 2), pin('C301', 1))
junc(pin('R302', 1)); junc(pin('C301', 2))
wire(pin('D301', 1), (142.24, YP), (151.13, YP)); junc((142.24, YP))
wire(pin('D303', 2), (142.24, YM), (146.05, YM)); junc((142.24, YM))
place('C302', 'Device:C_Polarized', '220u/400V', 151.13, 280.67 + 76.2,
      fields={'ref_at': (153.67, 285.75 + 76.2, 0), 'val_at': (153.67, 288.29 + 76.2, 0),
              'tol_at': (153.67, 290.83 + 76.2, 0)}, tol='20%')
place('L1', 'Device:L_Iron', '5-10H 100mA', 163.83, YP, rot=90,
      fields={'ref_at': (160.02, 271.78 + 76.2, 0), 'val_at': (166.37, 271.78 + 76.2, 0), 'val_just': 'left'})
text("L1 = dlawik zasilacza (nie mylic z Lp OPT >=25H - patrz T1/T201)", 151.13, 259.08 + 76.2, 1.27)
place('C303', 'Device:C_Polarized', '220u/400V', 176.53, 280.67 + 76.2,
      fields={'ref_at': (178.94, 285.75 + 76.2, 0), 'val_at': (178.94, 288.29 + 76.2, 0),
              'tol_at': (178.94, 290.83 + 76.2, 0)}, tol='20%')
wire((151.13, YP), pin('C302', 1)); junc((151.13, YP))
wire((151.13, YP), pin('L1', 1))
wire(pin('L1', 2), (176.53, YP)); junc((176.53, YP))
wire((176.53, YP), pin('C303', 1))
place('R303', 'Device:R', '220k/2W', 187.96, 280.67 + 76.2,
      fields={'ref_at': (189.99, 278.13 + 76.2, 90), 'val_at': (187.96, 278.13 + 76.2, 90),
              'tol_at': (185.93, 278.13 + 76.2, 90)}, tol='5%')
wire((176.53, YP), (187.96, YP)); junc((187.96, YP))
wire((187.96, YP), pin('R303', 1))
wire(pin('R303', 2), (187.96, YM))
wire((176.53, YP), (176.53, 266.7 + 76.2)); glabel('+300V', (176.53, 266.7 + 76.2), rot=0, just='left')
# masa filtra (jeden wspolny szyna GND, rozciagnieta az do elewacji
# R305/C304 - patrz nizej)
wire(pin('C302', 2), (151.13, YM))
wire(pin('C303', 2), (176.53, YM))
wire((146.05, YM), (151.13, YM), (176.53, YM), (187.96, YM), (210.82, YM), (218.44, YM))
for x in (151.13, 176.53, 187.96, 210.82, 218.44):
    junc((x, YM))
gnd(160.02, 313.69 + 76.2)
wire((160.02, YM), (160.02, 313.69 + 76.2))
junc((160.02, YM))

# --- elewacja zarzenia (+ELEV z B+ przez dzielnik) ---
place('R304', 'Device:R', '220k', 210.82, 281.94 + 76.2,
      fields={'ref_at': (212.09, 279.4 + 76.2, 0), 'val_at': (212.09, 281.94 + 76.2, 0)})
place('R305', 'Device:R', '47k', 210.82, 294.64 + 76.2,
      fields={'ref_at': (204.47, 293.37 + 76.2, 0), 'val_at': (208.28, 295.91 + 76.2, 0), 'val_just': 'right'})
wire(pin('R304', 1), (210.82, 266.7 + 76.2))
glabel('+300V', (210.82, 266.7 + 76.2), rot=0, just='left')
wire(pin('R304', 2), (210.82, 288.29 + 76.2))
wire((210.82, 288.29 + 76.2), pin('R305', 1))
wire(pin('R305', 2), (210.82, YM))
place('C304', 'Device:C_Polarized', '10u/100V', 218.44, 294.64 + 76.2,
      fields={'ref_at': (220.98, 296.52 + 76.2, 0), 'val_at': (220.98, 299.06 + 76.2, 0),
              'tol_at': (220.98, 301.6 + 76.2, 0)}, tol='20%')
wire((210.82, 288.29 + 76.2), (218.44, 288.29 + 76.2), pin('C304', 1))
junc((210.82, 288.29 + 76.2))
wire(pin('C304', 2), (218.44, YM))
label('ELEV', (213.36, 288.29 + 76.2))

# --- rozladowanie B+ (K1 + R306), 1:1 z riaa/common ---
place('K1', 'Relay:Relay_SPDT', '9V', 242.57, 280.67 + 76.2,
      fields={'ref_at': (251.46, 283.21 + 76.2, 0), 'val_at': (251.46, 285.75 + 76.2, 0)})
place('D305', 'Device:D', '1N4007', 229.87, 280.67 + 76.2, rot=270,
      fields={'ref_at': (222.25, 276.86 + 76.2, 0), 'val_at': (227.33, 279.4 + 76.2, 0), 'val_just': 'right'})
place('R306', 'Device:R', '4k7/10W', 247.65, 294.64 + 76.2,
      fields={'ref_at': (240.03, 292.1 + 76.2, 0), 'val_at': (245.11, 295.91 + 76.2, 0), 'val_just': 'right'})
wire(pin('K1', 'A1'), (237.49, 270.51 + 76.2), (231.14, 270.51 + 76.2))
label('V_RAW', (231.14, 270.51 + 76.2), just='right bottom')
# V_RAW zasilany tylko przez diody mostka (nie "power output" dla ERC) ->
# jeden PWR_FLAG na cala siec, zeby U301.VI (power input) mial sterownik.
pwrflag(231.14, 270.51 + 76.2 - 2.54)
wire((231.14, 270.51 + 76.2), (231.14, 270.51 + 76.2 - 2.54))
wire(pin('K1', 'A2'), (237.49, 293.37 + 76.2), (231.14, 293.37 + 76.2))
label('ELEV', (231.14, 293.37 + 76.2), just='right bottom')
wire(pin('D305', 1), (229.87, 273.05 + 76.2), (237.49, 273.05 + 76.2)); junc((237.49, 273.05 + 76.2))
wire(pin('D305', 2), (229.87, 288.29 + 76.2), (237.49, 288.29 + 76.2)); junc((237.49, 288.29 + 76.2))
wire(pin('K1', 12), (245.11, 267.97 + 76.2))
glabel('+300V', (245.11, 267.97 + 76.2), rot=0, just='left')
noconn(pin('K1', 14))
wire(pin('K1', 11), (247.65, 290.83 + 76.2))
wire(pin('R306', 2), (247.65, 300.99 + 76.2)); gnd(247.65, 300.99 + 76.2)
text("Rozladowanie: przy zaniku sieci K1 zwalnia, styk NC (11-12) laczy +300V z R306", 218.44, 320.04 + 76.2, 1.27)
text("-> B+ <50V w ok. 15 s. K1: cewka 9V (V_RAW), styki min. 250V. Bleeder R303 = wolna 2. linia.", 218.44, 322.58 + 76.2, 1.27)

# --- zarzenie: 7V -> mostek 1N5822 -> 10000u -> LD1085 (LDO) -> HEAT_A/HEAT_B ---
YHP, YHM = 312.42 + 76.2, 335.28 + 76.2
place('D306', 'Device:D', '1N5822', 287.02, 316.23 + 76.2, rot=270)
place('D307', 'Device:D', '1N5822', 299.72, 316.23 + 76.2, rot=270)
place('D308', 'Device:D', '1N5822', 287.02, 331.47 + 76.2, rot=270)
place('D309', 'Device:D', '1N5822', 299.72, 331.47 + 76.2, rot=270)
# AC1 (T301 sec zarzenia, pin5=SC) - D306.A / D308.K
wire(pin('D306', 2), pin('D308', 1))
wire(pin('T301', 5), (116.84, 400.05), (287.02, 400.05))
junc((287.02, 400.05))
# AC2 (T301 sec zarzenia, pin6=SD) - D307.A / D309.K (odsuniete o 2,54mm w X,
# zeby nie pokryc sie z galezia AC1)
wire(pin('D307', 2), pin('D309', 1))
wire(pin('T301', 6), (119.38, 383.54), (119.38, 403.86), (299.72, 403.86))
junc((299.72, 403.86))
place('C305', 'Device:C_Polarized', '10000u/16V', 317.5, 316.23 + 76.2, tol='20%')
place('C306', 'Device:C_Polarized', '470u/25V', 337.82, 316.23 + 76.2,
      fields={'ref_at': (331.47, 320.04 + 76.2, 0), 'val_at': (336.55, 323.85 + 76.2, 0),
              'tol_at': (336.55, 326.39 + 76.2, 0), 'val_just': 'right'}, tol='20%')
place('U301', 'Regulator_Linear:LM317_TO-220', 'LD1085 (LDO)', 351.79, YHP,
      fields={'ref_at': (356.87, 303.53 + 76.2, 0), 'val_at': (356.87, 306.07 + 76.2, 0)})
wire(pin('D306', 1), (299.72, YHP), (317.5, YHP))
junc((299.72, YHP)); junc((317.5, YHP))
wire((317.5, YHP), pin('C305', 1))
wire((317.5, YHP), (337.82, YHP)); junc((337.82, YHP))
label('V_RAW', (320.04, YHP))
wire((337.82, YHP), pin('C306', 1))
wire((337.82, YHP), pin('U301', 3))
place('R307', 'Device:R', '240R', 364.49, 316.23 + 76.2, tol='1%')
place('R308', 'Device:R', '976R', 364.49, 326.39 + 76.2,
      fields={'ref_at': (358.14, 321.31 + 76.2, 0), 'val_at': (356.87, 326.39 + 76.2, 0),
              'tol_at': (356.87, 328.93 + 76.2, 0), 'val_just': 'right'}, tol='1%')
place('C307', 'Device:C_Polarized', '10u/25V', 372.11, 323.85 + 76.2,
      fields={'ref_at': (374.65, 320.04 + 76.2, 0), 'val_at': (374.65, 328.93 + 76.2, 0),
              'tol_at': (374.65, 331.47 + 76.2, 0)}, tol='20%')
place('C308', 'Device:C', '1u', 379.73, 316.23 + 76.2,
      fields={'ref_at': (382.27, 315.29 + 76.2, 0), 'val_at': (382.27, 317.83 + 76.2, 0)})
wire(pin('U301', 2), (364.49, YHP)); junc((364.49, YHP))
wire((364.49, YHP), pin('R307', 1))
wire(pin('U301', 1), (351.79, 320.04 + 76.2), (364.49, 320.04 + 76.2))
wire(pin('R307', 2), pin('R308', 1))
junc((364.49, 320.04 + 76.2))
wire((364.49, 320.04 + 76.2), (372.11, 320.04 + 76.2), pin('C307', 1))
wire(pin('R308', 2), (364.49, YHM))
wire(pin('C307', 2), (372.11, YHM))
wire((364.49, YHP), (379.73, YHP)); junc((379.73, YHP))
wire((379.73, YHP), pin('C308', 1))
wire(pin('C308', 2), (379.73, YHM))
wire((379.73, YHP), (384.81, YHP), (387.35, YHP)); label('HEAT_A', (387.35, YHP))
wire(pin('D308', 2), (299.72, YHM), (317.5, YHM), (337.82, YHM), (364.49, YHM), (372.11, YHM),
     (379.73, YHM), (384.81, YHM), (387.35, YHM))
wire(pin('C305', 2), (317.5, YHM))
wire(pin('C306', 2), (337.82, YHM))
for x in (299.72, 317.5, 337.82, 364.49, 372.11, 379.73):
    junc((x, YHM))
label('HEAT_B', (387.35, YHM))
wire((287.02, YHM), (281.94, YHM))
label('ELEV', (281.94, YHM), just='right bottom')
# brak PWR_FLAG tutaj: HEAT_A juz ma sterownik (U301.VO), HEAT_B ma
# PWR_FLAG postawiony przy grzaniu lamp (Etap 5a) - druga flaga na tym
# samym wezle daje ERC error "Power output and Power output connected".
junc((384.81, YHP)); junc((384.81, YHM))
text("Zarzenie: 6,3V DC / ok. 0,3A z uzwojenia 7V (3 lampy). LD1085 (LDO) - LM317 ma za duzy dropout.", 218.44, 344.17 + 76.2, 1.27)
text("Skrecona para na przewodach zarzenia. LD1085: blaszka = VOUT - izolacja od chassis.", 218.44, 346.71 + 76.2, 1.27)

# --- ground breaker (jedyny styk masy z chassis) ---
place('R309', 'Device:R', '10R/5W', 45.72, 325.12 + 76.2,
      fields={'ref_at': (39.37, 401.32, 90), 'val_at': (41.4, 401.32, 90)})
place('D310', 'Device:D', '1N5408', 55.88, 325.12 + 76.2, rot=270,
      fields={'ref_at': (58.42, 398.78, 0), 'val_at': (58.42, 401.32, 0)})
place('D311', 'Device:D', '1N5408', 66.04, 325.12 + 76.2, rot=90,
      fields={'ref_at': (68.58, 398.78, 0), 'val_at': (68.58, 401.32, 0)})
place('C309', 'Device:C', '100n/630V', 76.2, 325.12 + 76.2,
      fields={'ref_at': (79.5, 401.32, 90), 'val_at': (81.5, 401.32, 90),
              'tol_at': (83.5, 401.32, 90)}, tol='10%')
wire((40.64, 321.31 + 76.2), (45.72, 321.31 + 76.2), (55.88, 321.31 + 76.2), (66.04, 321.31 + 76.2), (76.2, 321.31 + 76.2))
wire((43.18, 328.93 + 76.2), (45.72, 328.93 + 76.2), (55.88, 328.93 + 76.2), (66.04, 328.93 + 76.2), (76.2, 328.93 + 76.2))
for x in (45.72, 55.88, 66.04):
    junc((x, 321.31 + 76.2)); junc((x, 328.93 + 76.2))
gnd(40.64, 321.31 + 76.2)
pe(43.18, 328.93 + 76.2, rot=180)
text("Ground breaker (jedyny styk masy z chassis): 10R przerywa petle masy;", 27.94, 340.36 + 76.2, 1.27)
text("przy usterce diody zwieraja GND do PE i bezpiecznik zadziala.", 27.94, 342.9 + 76.2, 1.27)

text("UWAGA: napiecia do ok. 330V DC - smiertelnie niebezpieczne. Po wylaczeniu odczekac na", 27.94, 424.18, 1.6)
text("rozladowanie (K1) i SPRAWDZIC woltomierzem KAZDA sekcje (<50V) przed praca.", 27.94, 426.72, 1.6)

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
