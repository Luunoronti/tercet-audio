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


def U():
    return str(uuidlib.uuid4())


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
    ('Device', 'R_Potentiometer'), ('Device', 'Transformer_1P_1S'),
    ('Switch', 'SW_SPST'),
    ('Valve', 'ECC81'), ('Valve', 'EL84'),
    ('power', 'GND'), ('power', 'PWR_FLAG'),
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
                      rot=rot, unit=unit, mirror=mirror, fields=fields or {}, tol=tol, uuid=U()))


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


# =======================================================================
#  KANAL L (audio) - odtworzony 1:1 z headamp.kicad_sch @ b7d6cc9
#  (kompletny commit z ERC=0). Wspolrzedne/pola/tolerancje wyciete z
#  tamtego pliku (git show b7d6cc9:headamp/headamp.kicad_sch).
# =======================================================================

place('RV1', 'Device:R_Potentiometer', '50k log', 39.37, 139.7,
      fields={'ref_at': (34.925, 139.7, 90), 'val_at': (36.83, 139.7, 90),
              'tol_at': (32.893, 139.7, 90)}, tol='20%')
place('C1', 'Device:C', '220n', 58.42, 129.54, rot=90,
      fields={'ref_at': (55.88, 128.905, 0), 'val_at': (60.96, 128.905, 0),
              'tol_at': (62.992, 128.905, 0)}, tol='5%')
place('R1', 'Device:R', '470k', 68.58, 144.78,
      fields={'ref_at': (70.612, 144.78, 90), 'val_at': (68.58, 144.78, 90),
              'tol_at': (66.548, 144.78, 90)}, tol='5%')
place('R2', 'Device:R', '1k', 80.01, 129.54, rot=90,
      fields={'ref_at': (80.01, 127.508, 90), 'val_at': (80.01, 129.54, 90),
              'tol_at': (80.01, 131.572, 90)}, tol='5%')
place('U1', 'Valve:ECC81', 'ECC82', 100.33, 129.54, unit=1,
      fields={'ref_at': (103.632, 121.666, 0), 'val_at': (109.22, 137.16, 0)})
place('R3', 'Device:R', '1k5', 93.98, 154.94,
      fields={'ref_at': (96.012, 154.94, 90), 'val_at': (93.98, 154.94, 90),
              'tol_at': (91.948, 154.94, 90)}, tol='1%')
place('SW2', 'Switch:SW_SPST', 'S2 wokal', 118.11, 149.86, rot=270,
      fields={'ref_at': (121.285, 149.86, 0), 'val_at': (115.57, 149.86, 0)})
place('C2', 'Device:C_Polarized', '1u/25V', 105.41, 154.94,
      fields={'ref_at': (106.045, 152.4, 0), 'val_at': (106.045, 157.48, 0),
              'tol_at': (106.045, 159.512, 0)}, tol='20%')
place('C3', 'Device:C_Polarized', '100u/25V', 118.11, 166.37,
      fields={'ref_at': (118.745, 163.83, 0), 'val_at': (118.745, 168.91, 0),
              'tol_at': (118.745, 170.942, 0)}, tol='20%')
place('R4', 'Device:R', '47k/2W', 100.33, 105.41,
      fields={'ref_at': (102.362, 105.41, 90), 'val_at': (100.33, 105.41, 90),
              'tol_at': (98.298, 105.41, 90)}, tol='5%')
place('C4', 'Device:C_Polarized', '47u/350V', 86.36, 105.41,
      fields={'ref_at': (86.995, 102.87, 0), 'val_at': (86.995, 107.95, 0),
              'tol_at': (86.995, 109.982, 0)}, tol='20%')
place('R5', 'Device:R', '10k/2W', 111.76, 91.44, rot=90,
      fields={'ref_at': (111.76, 89.408, 90), 'val_at': (111.76, 91.44, 90),
              'tol_at': (111.76, 93.472, 90)}, tol='5%')
place('C5', 'Device:C', '100n/400V', 125.73, 118.11, rot=90,
      fields={'ref_at': (123.19, 117.475, 0), 'val_at': (128.27, 117.475, 0),
              'tol_at': (130.302, 117.475, 0)}, tol='5%')
place('R6', 'Device:R', '470k', 135.89, 132.08,
      fields={'ref_at': (137.922, 132.08, 90), 'val_at': (135.89, 132.08, 90),
              'tol_at': (133.858, 132.08, 90)}, tol='5%')
place('R7', 'Device:R', '1k', 148.59, 118.11, rot=90,
      fields={'ref_at': (148.59, 116.078, 90), 'val_at': (148.59, 118.11, 90),
              'tol_at': (148.59, 120.142, 90)}, tol='5%')
place('U2', 'Valve:EL84', 'EL84 (trioda)', 171.45, 124.46, unit=1,
      fields={'ref_at': (173.99, 114.3, 0), 'val_at': (179.07, 132.08, 0)})
place('R9', 'Device:R', '100', 185.42, 115.57,
      fields={'ref_at': (187.452, 115.57, 90), 'val_at': (185.42, 115.57, 90),
              'tol_at': (183.388, 115.57, 90)}, tol='5%')
place('R8', 'Device:R', '270/5W', 166.37, 149.86,
      fields={'ref_at': (168.402, 149.86, 90), 'val_at': (166.37, 149.86, 90),
              'tol_at': (164.338, 149.86, 90)}, tol='5%')
place('C6', 'Device:C_Polarized', '470u/25V', 180.34, 149.86,
      fields={'ref_at': (180.975, 147.32, 0), 'val_at': (180.975, 152.4, 0),
              'tol_at': (180.975, 154.432, 0)}, tol='20%')
place('T1', 'Device:Transformer_1P_1S', 'OPT SE 5k:80R (>=25H, 45mA)', 209.55, 107.95,
      fields={'ref_at': (209.55, 101.6, 0), 'val_at': (209.55, 115.57, 0)})

# --- grzanie (heater) U1/U2 - jednostki 3 (ECC82) / 2 (EL84), odrebnie
#     narysowane pod schematem audio, dokladnie jak w b7d6cc9 ---
place('U1', 'Valve:ECC81', 'ECC82', 59.69, 224.79, unit=3,
      fields={'ref_at': (62.992, 216.916, 0), 'val_at': (68.58, 232.41, 0)})
place('U2', 'Valve:EL84', 'EL84 (trioda)', 90.17, 224.79, unit=2,
      fields={'ref_at': (92.71, 214.63, 0), 'val_at': (97.79, 232.41, 0)})

# --- druty kanalu L (topologia = literalna kopia wire/junction z b7d6cc9) ---
wire((43.18, 139.7), (54.61, 139.7))
wire((54.61, 139.7), (54.61, 129.54))
wire((62.23, 129.54), (76.2, 129.54))
wire((68.58, 140.97), (68.58, 129.54))
wire((83.82, 129.54), (92.71, 129.54))
wire((97.79, 139.7), (97.79, 143.51))
wire((93.98, 143.51), (118.11, 143.51))
wire((93.98, 143.51), (93.98, 151.13))
wire((105.41, 143.51), (105.41, 151.13))
wire((118.11, 143.51), (118.11, 144.78))
wire((118.11, 154.94), (118.11, 162.56))
wire((100.33, 119.38), (100.33, 109.22))
wire((100.33, 118.11), (121.92, 118.11))
wire((86.36, 101.6), (100.33, 101.6))
wire((100.33, 101.6), (100.33, 91.44))
wire((100.33, 91.44), (107.95, 91.44))
wire((129.54, 118.11), (144.78, 118.11))
wire((135.89, 118.11), (135.89, 128.27))
wire((152.4, 118.11), (157.48, 118.11))
wire((157.48, 118.11), (157.48, 125.73))
wire((157.48, 125.73), (163.83, 125.73))
wire((168.91, 133.35), (168.91, 146.05))
wire((166.37, 146.05), (180.34, 146.05))
wire((171.45, 113.03), (199.39, 113.03))
wire((185.42, 111.76), (185.42, 113.03))
wire((185.42, 119.38), (185.42, 123.19))
wire((185.42, 123.19), (179.07, 123.19))
wire((219.71, 113.03), (224.79, 113.03))
wire((224.79, 113.03), (224.79, 116.84))
wire((115.57, 91.44), (118.11, 91.44))
wire((199.39, 102.87), (196.85, 102.87))
wire((39.37, 135.89), (39.37, 133.35))
wire((219.71, 102.87), (222.25, 102.87))

for p in [(68.58, 129.54), (97.79, 143.51), (100.33, 101.6), (100.33, 118.11),
          (105.41, 143.51), (135.89, 118.11), (168.91, 146.05), (185.42, 113.03)]:
    junc(p)

# masa (GND) - 10x, dokladnie te same punkty co #PWR001..#PWR010 w b7d6cc9
gnd(39.37, 143.51)
gnd(68.58, 148.59)
gnd(93.98, 158.75)
gnd(105.41, 158.75)
gnd(118.11, 170.18)
gnd(86.36, 109.22)
gnd(135.89, 135.89)
gnd(166.37, 153.67)
gnd(180.34, 153.67)
gnd(224.79, 116.84)

# etykiety grzania + globalne + PWR_FLAG (dokladnie jak #PWR011..#PWR013)
label('HEAT_A', (57.15, 236.22))
label('HEAT_A', (62.23, 236.22))
label('HEAT_A', (87.63, 234.95))
label('HEAT_B', (59.69, 236.22))
label('HEAT_B', (92.71, 234.95))

glabel('+300V', (118.11, 91.44), rot=0, just='left')
glabel('+300V', (196.85, 102.87), rot=180, just='right')
glabel('IN_L', (39.37, 133.35), rot=0, just='left')
glabel('OUT_L', (222.25, 102.87), rot=0, just='left')

pwrflag(224.79, 113.03)
pwrflag(87.63, 234.95, rot=180)
pwrflag(92.71, 234.95, rot=180)

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
out.append('  (paper "A3")')
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
    out.append('  (junction (at %s %s) (diameter 0) (uuid %s))' % (fmt(p[0]), fmt(p[1]), U()))
for (a, b) in WIRES:
    out.append('  (wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))'
                % (fmt(a[0]), fmt(a[1]), fmt(b[0]), fmt(b[1]), U()))
for p in NOCONN:
    out.append('  (no_connect (at %s %s) (uuid %s))' % (fmt(p[0]), fmt(p[1]), U()))
for (name, p, rot, just) in LABELS:
    out.append('  (label "%s" (at %s %s %d) (effects (font (size 1.27 1.27)) (justify %s)) (uuid %s))'
                % (name, fmt(p[0]), fmt(p[1]), rot, just, U()))
for (name, p, rot, just) in GLABELS:
    out.append('  (global_label "%s" (shape input) (at %s %s %d) '
                '(effects (font (size 1.27 1.27)) (justify %s)) (uuid %s))'
                % (name, fmt(p[0]), fmt(p[1]), rot, just, U()))
for (s, x, y, size, rot) in TEXTS:
    out.append('  (text "%s" (at %s %s %d) (effects (font (size %s %s)) (justify left bottom)) (uuid %s))'
                % (s, fmt(x), fmt(y), rot, fmt(size), fmt(size), U()))

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
        rpos = s['fields']['ref_at']; vpos = s['fields']['val_at']
        out.append('    (property "Reference" "%s" (at %s %s %d) (effects (font (size 1.27 1.27))))'
                    % (s['ref'], fmt(rpos[0]), fmt(rpos[1]), rpos[2]))
        out.append('    (property "Value" "%s" (at %s %s %d) (effects (font (size 1.27 1.27))))'
                    % (s['value'], fmt(vpos[0]), fmt(vpos[1]), vpos[2]))
    out.append('    (property "Footprint" "" (at %s %s 0) (effects (font (size 1.27 1.27)) hide))' % (fmt(x), fmt(y)))
    out.append('    (property "Datasheet" "" (at %s %s 0) (effects (font (size 1.27 1.27)) hide))' % (fmt(x), fmt(y)))
    if s['tol']:
        tx, ty, trot = s['fields']['tol_at']
        out.append('    (property "Tolerance" "%s" (at %s %s %d) (effects (font (size 1.27 1.27))))'
                    % (s['tol'], fmt(tx), fmt(ty), trot))
    for num, px, py, a, l, nm in geo[u]:
        out.append('    (pin "%s" (uuid %s))' % (num, U()))
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
