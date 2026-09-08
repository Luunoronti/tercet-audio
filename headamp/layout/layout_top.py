#!/usr/bin/env python3
"""headamp - propozycja rozmieszczenia elementow w obudowie (rzut z gory).

Obudowa: 260 (szer, X) x 200 (glab, Y) mm, wnetrze - wersja zwarta
(2026-09-08, poprawki uzytkownika do pierwszej propozycji 300x250).
Front = y=0 (dol rysunku), tyl = y=200 (gora rysunku). Skala 1:1 w mm.

Zrodla danych: docs/PROJEKT-HEADAMP.md (topologia, numeracja, DECYZJA
"zasilacz na PCB"), headamp/gen.py (pelna lista elementow toru audio),
zadanie uzytkownika (zalozenia geometrii + poprawki, 2026-09-08).

Zasilacz: DECYZJA - PCB (nie powietrznie), patrz PROJEKT-HEADAMP.md sekcja
"Montaz". Na chassis (gorna plyta) zostaja tylko elementy mechaniczne/ciezkie
i te ktore fizycznie musza przebijac obudowe: T301, L1, IEC J1+F1, SW1, NE1.
Reszta zasilacza (mostki, CLC bez duzych elektrolitow, K1, LD1085+radiator,
siec NTC/warystor/neon-rezystor, ground breaker) - na PCB pod plyta, w
zarezerwowanej strefie "PCB zasilacza".

Wyjscie: headamp/ref/layout_top.svg + .png (obok tego skryptu).
"""
import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_SVG = os.path.join(HERE, '..', 'ref', 'layout_top.svg')
OUT_PNG = os.path.join(HERE, '..', 'ref', 'layout_top.png')

W, H = 260.0, 200.0  # chassis interior, mm (zmniejszone z 300x250)

# kolory (per zalozenia zadania)
C_TOP = 'black'        # gorna plyta (linia ciagla)
C_UNDER = '#1f5fbf'     # pod plyta (niebieski, przerywane/polprzezroczyste)
C_MAINS = '#c00000'     # siec/HV (czerwony)
C_SIG = '#2e8b30'       # sygnal (zielony)
C_HEAT = '#e08a00'      # zarzenie (pomaranczowy)
C_GND = '#666666'       # masa (szary)

fig, ax = plt.subplots(figsize=(13, 12))
ax.set_xlim(-15, W + 15)
ax.set_ylim(-33, H + 40)
ax.set_aspect('equal')
ax.invert_yaxis()  # nie uzywane - trzymamy y rosnace w gore rysunku (front=0 na dole)
ax.invert_yaxis()  # podwojne invert = powrot do normalnego (y rosnie w gore ekranu)

# ------------------------------------------------------------------
# obrys obudowy + siatka co 50mm
# ------------------------------------------------------------------
ax.add_patch(mpatches.Rectangle((0, 0), W, H, fill=False, edgecolor='black', linewidth=2.2, zorder=5))
for gx in range(0, int(W) + 1, 50):
    ax.axvline(gx, color='#dddddd', linewidth=0.6, zorder=0)
    if 0 < gx < W:
        ax.text(gx, -6, f'{gx}', ha='center', va='top', fontsize=7, color='#888')
for gy in range(0, int(H) + 1, 50):
    ax.axhline(gy, color='#dddddd', linewidth=0.6, zorder=0)
    if 0 < gy < H:
        ax.text(-6, gy, f'{gy}', ha='right', va='center', fontsize=7, color='#888')
ax.text(W / 2, -19, 'FRONT (y=0)', ha='center', va='top', fontsize=11, fontweight='bold')
ax.text(W / 2, H + 2, 'TYL (y=200)', ha='center', va='bottom', fontsize=11, fontweight='bold')
ax.text(-12, H / 2, 'mm', ha='center', va='center', fontsize=8, rotation=90, color='#888')

# granica stref zasilanie/audio (umowna - nie fizyczna sciana, marginesy 10mm
# od SCIAN OBUDOWY dotycza tylko elementow stojacych swobodnie na plycie
# gornej: T301/L1/lampy/OPT/strefa PCB - nie elementow panelowych na y=0/y=H)
ax.axvline(100, color='#aaaaaa', linewidth=1.0, linestyle=':', zorder=1)
ax.text(50, H + 9, 'strefa ZASILANIE', ha='center', fontsize=9, style='italic', color='#555')
ax.text(180, H + 9, 'strefa AUDIO', ha='center', fontsize=9, style='italic', color='#555')


def rect_top(cx, cy, w, h, label, rot=0, fs=7.5, lcolor=C_TOP, note=None):
    """Bryla na gornej plycie (linia ciagla)."""
    if rot == 90:
        w, h = h, w
    x0, y0 = cx - w / 2, cy - h / 2
    ax.add_patch(mpatches.Rectangle((x0, y0), w, h, fill=False, edgecolor=lcolor,
                                     linewidth=1.4, zorder=4))
    txt = label if not note else f'{label}\n{note}'
    ax.text(cx, cy, txt, ha='center', va='center', fontsize=fs, zorder=6)
    return (x0, y0, x0 + w, y0 + h)


def rect_under(cx, cy, w, h, label, fs=7, note=None):
    """Bryla pod plyta (przerywana, polprzezroczysta, niebieska)."""
    x0, y0 = cx - w / 2, cy - h / 2
    ax.add_patch(mpatches.Rectangle((x0, y0), w, h, fill=True, facecolor=C_UNDER,
                                     alpha=0.10, edgecolor=C_UNDER, linewidth=1.2,
                                     linestyle='--', zorder=3))
    txt = label if not note else f'{label}\n{note}'
    ax.text(cx, cy, txt, ha='center', va='center', fontsize=fs, color=C_UNDER, zorder=6)
    return (x0, y0, x0 + w, y0 + h)


def circ_top(cx, cy, d, label, fs=7, lcolor=C_TOP, label_dy=None, note=None, no_label=False):
    ax.add_patch(mpatches.Circle((cx, cy), d / 2, fill=False, edgecolor=lcolor,
                                  linewidth=1.4, zorder=4))
    if not no_label:
        dy = label_dy if label_dy is not None else (d / 2 + 5)
        txt = label if not note else f'{label}\n{note}'
        ax.text(cx, cy - dy, txt, ha='center', va='top', fontsize=fs, zorder=6)
    return (cx - d / 2, cy - d / 2, cx + d / 2, cy + d / 2)


def circ_under(cx, cy, d, label, fs=6.5):
    ax.add_patch(mpatches.Circle((cx, cy), d / 2, fill=True, facecolor=C_UNDER, alpha=0.10,
                                  edgecolor=C_UNDER, linewidth=1.0, linestyle='--', zorder=3))
    ax.text(cx, cy, label, ha='center', va='center', fontsize=fs, color=C_UNDER, zorder=6)


def dashed_route(pts, color, label=None, lw=1.6, label_at=None):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=color, linewidth=lw, linestyle='--', zorder=2, alpha=0.9)
    if label:
        lx, ly = label_at if label_at else pts[len(pts) // 2]
        ax.text(lx, ly, label, color=color, fontsize=7, ha='left', va='bottom', zorder=6)


# ==========================================================================
# GORNA PLYTA (linia ciagla) - elementy montowane na chassis / widoczne z gory
# ==========================================================================

# --- strefa ZASILANIE (x 0-100): tylko elementy mechaniczne/ciezkie + panel ---
bb_t301 = rect_top(50, 155, 85, 70, 'T301', note='EI84 100VA\n(os rdzenia || X)')
bb_l1 = rect_top(50, 85, 55, 45, 'L1', note='dlawik 5-10H, 0,5-1kg\n(chassis, nie PCB)')
# SW1/NE1 - POPRAWKA 2026-09-08: przesuniete w prawo (z x=18/34), zeby
# zrobic miejsce na J1+F1 przenoszone w ten rejon sciany lewej (patrz nizej) -
# obie bryly kolidowaly z nowa pozycja IEC (x=0-35, y=6-54).
bb_sw1 = rect_top(58, 13, 22, 14, 'SW1', fs=7.5)
bb_ne1 = circ_top(80, 13, 8, 'NE1', no_label=True)
ax.text(80, 24.5, 'NE1', ha='center', va='bottom', fontsize=7)
# J1+F1 (IEC C14 + bezpiecznik) - POPRAWKA 2026-09-08: przeniesione ze
# sciany tylnej (kolidowala z T301, ktory siega do y=190) na sciane LEWA
# (x=0), z przodu, przed strefa L1/T301 (korpus IEC ~48x28mm + ~30-35mm
# glebokosci w obudowie). Warianty rozwazone: (a) IEC na wysokosci L1
# (y~65) + przesuniecie L1 w prawo - odrzucony, geometrycznie niewykonalny
# (L1 55mm szerokosci nie miesci sie miedzy krawedzia IEC a wymaganym
# 25mm odstepem od U2); (b) IEC z przodu (y~6-54, ten wariant) + przesuniecie
# SW1/NE1 w prawo - wybrany, L1 zostaje na miejscu, przewod sieciowy
# IEC->F1->SW1 krotki i caly czas w strefie zasilania (x<100), z dala od
# frontu przy RV1 (x=140). Bryla "glebokosci" 35(x) x 48(y) mm dodana do
# kontroli kolizji ponizej.
bb_j1 = rect_top(17.5, 30, 35, 48, 'J1+F1', fs=6.5,
                  note='IEC C14 + bezp.\n(sciana lewa, x=0)')
ax.text(-13, 30 - 24 - 3, 'IEC(+F1)->SW1->siec ochr.(PCB)->T301',
        ha='left', va='top', fontsize=5.8, style='italic', color='#555')

# --- front panel (obie strefy) ---
bb_sw401 = rect_top(105, 13, 14, 10, 'SW401', fs=6.5)
# RV1: galka na plycie gornej (widoczna z gory), korpus pod plyta (patrz nizej)
bb_rv1_knob = circ_top(140, 14, 26, 'RV1', fs=7.5)
bb_sw2 = rect_top(185, 13, 14, 10, 'SW2', fs=7.5)
bb_j403 = circ_top(235, 13, 12, 'J403', fs=7.5)

# opis calego rzedu przednich elementow - jedna zwarta linia pod FRONT,
# zamiast wielolinijkowych notatek przy kazdym (unika kolizji tekstow)
ax.text(W / 2, -24.5,
        'Front, od lewej: SW1 (siec ON/OFF) - NE1 (kontrolka) - SW401 (S1 crossfeed) -\n'
        'RV1 (50k log, podwojny, galka) - SW2/SW202 (S2 wokal, 1 przelacznik/2 sekcje) - '
        'J403 (jack 6,3mm, DT770 M 80R)',
        ha='center', va='top', fontsize=7)

# --- strefa AUDIO (x 100-260): lampy + OPT ---
bb_u1 = circ_top(178, 45, 22, 'U1', note='1/2 ECC82\n(driver, obie sekcje)')
bb_u2 = circ_top(128, 90, 22, 'U2', note='EL84 (L)\ntrioda')
bb_u202 = circ_top(228, 90, 22, 'U202', note='EL84 (P)\ntrioda')
bb_t1 = rect_top(128, 160, 45, 55, 'T1', note='OPT 5k:80\n(os obr. 90 wzgl. T301)')
bb_t201 = rect_top(228, 160, 45, 55, 'T201', note='OPT 5k:80\n(os obr. 90 wzgl. T301)')

# --- tyl: gniazda RCA wejsciowe (przesuniete od naroznika, z dala od T201) ---
bb_j401 = rect_top(182, 192, 10, 8, 'J401', fs=6, note=None)
bb_j402 = rect_top(198, 192, 10, 8, 'J402', fs=6, note=None)
ax.text(190, 200 - 3, 'RCA IN L/R', ha='center', fontsize=6.5)

# ==========================================================================
# POD PLYTA (przerywane/polprzezroczyste, niebieskie)
# ==========================================================================
bb_pcb = rect_under(50, 100, 90, 140, '', fs=1)  # tylko obrys strefy, opisy nizej osobno
ax.text(50, 105, 'PCB zasilacza (DECYZJA)', ha='center', va='center', fontsize=7,
        color=C_UNDER, fontweight='bold', zorder=6)
ax.text(50, 130, 'mostki, CLC (bez duzych elektrolitow\njesli w kubku), K1, LD1085+radiator,\n'
                 'siec NTC/warystor/neon-R, ground breaker',
        ha='center', va='center', fontsize=6, color=C_UNDER, zorder=6)
# C302/C303 przesuniete z y=45 na y=150 (pod T301, nadal w strefie PCB
# zasilacza) - POPRAWKA 2026-09-08: poprzednia pozycja wizualnie kolidowala
# z etykieta nowego J1+F1 (sciana lewa, front)
circ_under(25, 150, 26, 'C302\n220u/400V\n(PCB/kubek)', fs=6)
circ_under(75, 150, 26, 'C303\n220u/400V\n(PCB/kubek)', fs=6)

bb_rv1_body = rect_under(140, 38, 40, 26, 'RV1 (korpus,\nod spodu plyty)', fs=6.5)
bb_strA = rect_under(178, 70, 42, 11, 'listwa A (8-10 pkt)\nprzy U1', fs=6.5)
bb_strBL = rect_under(128, 122, 30, 9, 'listwa B_L (5-6 pkt)', fs=6)
bb_strBP = rect_under(228, 122, 30, 9, 'listwa B_P (5-6 pkt)', fs=6)
bb_strC = rect_under(215, 29, 50, 12, 'listwa C - crossfeed\n(R401-406, C401-404)\n(na prawo od RV1)', fs=6)
bb_strD = rect_under(248, 48, 18, 9, 'listwa D\n(wyjsciowa)', fs=5.8)

# ==========================================================================
# TRASY (pod plyta) - masa, zarzenie, B+, sygnal wejsciowy
# ==========================================================================
# szyna masy - prosty odcinek wzdluz listw A -> B_L/B_P (bez "V" przez puste
# pole - w tym ukladzie pole miedzy A i B jest juz male, patrz kompaktowa
# geometria), jeden punkt do chassis przez ground breaker NA PCB przy IEC.
dashed_route([(128, 122), (228, 122)], C_GND,
             label='szyna masy: B_L -> A -> B_P (odczep pionowy)', label_at=(150, 132), lw=1.8)
dashed_route([(178, 122), (178, 70)], C_GND, lw=1.8)
# korytarz x=101 (miedzy L1/T301 i T1, >=4,5mm marginesu po obu stronach po
# przesunieciu L1 - patrz POPRAWKA IEC nizej) - bez przeciecia ktoregokolwiek
# transformatora/dlawika, prosto do ground breakera na PCB przy nowym IEC
dashed_route([(128, 122), (101, 122), (101, 45), (20, 45), (20, 30)], C_GND,
             label='szyna masy (Dia 1,5-2mm)\n-> ground breaker (PCB, przy IEC)',
             label_at=(103, 108), lw=1.8)
ax.text(150, 60, 'masa sygnalowa != chassis poza tym jednym punktem',
        ha='center', fontsize=6.3, color=C_GND, style='italic')

# zarzenie - skrecona para z T301 do podstawek. POPRAWKA 2026-09-08: korytarz
# przesuniety z x=98 na x=101 (razem z korytarzem masy, patrz wyzej) i - co
# wazniejsze - odgalezienie do U1 (ECC82) juz NIE schodzi przy RV1/wejsciu
# (dawniej (98,90)->(98,45)->(167,45)); teraz idzie rzedem EL84 (y=90) do
# U202, a do U1 odczep prosto w dol ze srodka miedzy EL84 (x=178).
dashed_route([(72, 120), (72, 112), (101, 112), (101, 90), (117, 90)], C_HEAT,
             label='zarzenie DC - skrecona para, z dala od wejscia', label_at=(103, 96), lw=1.8)
dashed_route([(139, 90), (217, 90)], C_HEAT, lw=1.8)
dashed_route([(178, 90), (178, 56)], C_HEAT, label='-> U1', label_at=(180, 70), lw=1.8)

# B+ (+300V) - z PCB zasilacza do listw B_L/B_P i A, z dala od toru
# wejsciowego (crossfeed/RV1/RCA lezacych w pasie y<40)
dashed_route([(95, 120), (110, 120), (110, 122), (113, 122)], C_MAINS, lw=1.8)
dashed_route([(128, 76), (128, 117)], C_MAINS, lw=1.8)
dashed_route([(110, 120), (128, 120), (128, 117)], C_MAINS, lw=1.8)
dashed_route([(228, 76), (228, 117)], C_MAINS, lw=1.8)
dashed_route([(128, 76), (228, 76)], C_MAINS, label='B+ -> listwy B_L/B_P (przez A)', label_at=(150, 78), lw=1.8)

# sygnal wejsciowy: RCA (tyl, srodek-prawo) -> wzdluz prawej krawedzi ->
# listwa C (na PRAWO od RV1) -> RV1 -> ECC82. Kabel ekranowany.
dashed_route([(190, 188), (253, 188), (253, 29), (240, 29)], C_SIG,
             label='sygnal (kabel ekranowany): RCA -> wzdluz prawej krawedzi -> listwa C',
             label_at=(200, 178), lw=1.8)
dashed_route([(190, 29), (165, 38)], C_SIG, lw=1.8)
dashed_route([(165, 38), (150, 27)], C_SIG, lw=1.8)
dashed_route([(150, 27), (150, 20)], C_SIG, label='RV1->U1', label_at=(155, 24), lw=1.8)
dashed_route([(150, 20), (167, 45)], C_SIG, lw=1.8)

# ==========================================================================
# adnotacje ogolne
# ==========================================================================
ax.text(130, 233, 'TERCET headamp - propozycja rozmieszczenia (rzut z gory), 260 x 200 mm, skala 1:1',
        ha='center', fontsize=12, fontweight='bold')
ax.text(130, 223, 'UWAGA: napiecia do ok. 330V DC w strefie zasilania - smiertelnie niebezpieczne. '
                     'Rozladowac (K1) i sprawdzic woltomierzem przed praca.',
        ha='center', fontsize=7.5, color=C_MAINS)

ax.text(263, 190, 'OPT (T1/T201)\nobrocone o 90 st.\nwzgl. T301', ha='left', va='center', fontsize=6.5,
        color='#333', style='italic')
ax.text(263, 155, 'T301 >=100mm od\nRV1/RCA/ECC82\n(sprawdzone automat.)', ha='left', va='center', fontsize=6.5,
        color='#333', style='italic')

# ==========================================================================
# legenda
# ==========================================================================
legend_elems = [
    Line2D([0], [0], color=C_TOP, lw=1.4, label='gorna plyta (widoczne z gory)'),
    mpatches.Patch(facecolor=C_UNDER, alpha=0.10, edgecolor=C_UNDER, linestyle='--',
                   label='pod plyta (listwy, RV1 od spodu, PCB zasilacza, trasy)'),
    Line2D([0], [0], color=C_GND, lw=1.8, linestyle='--', label='szyna masy'),
    Line2D([0], [0], color=C_HEAT, lw=1.8, linestyle='--', label='zarzenie (skrecona para)'),
    Line2D([0], [0], color=C_MAINS, lw=1.8, linestyle='--', label='B+ (+300V DC)'),
    Line2D([0], [0], color=C_SIG, lw=1.8, linestyle='--', label='sygnal wejsciowy (male V, ekranowany)'),
]
ax.legend(handles=legend_elems, loc='lower left', bbox_to_anchor=(1.01, 0.0), fontsize=8, frameon=True)

ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()

# ==========================================================================
# WERYFIKACJA GEOMETRII (bez rysowania) - te same bbox co uzyte wyzej
# ==========================================================================
def overlap(a, b, pad=0.0):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 + pad <= bx0 or bx1 + pad <= ax0 or ay1 + pad <= by0 or by1 + pad <= ay0)


TOP_BOXES = {
    'T301': bb_t301, 'L1': bb_l1, 'SW1': bb_sw1, 'NE1': bb_ne1, 'J1+F1': bb_j1,
    'SW401': bb_sw401, 'RV1(knob)': bb_rv1_knob, 'SW2/SW202': bb_sw2, 'J403': bb_j403,
    'U1': bb_u1, 'U2': bb_u2, 'U202': bb_u202, 'T1': bb_t1, 'T201': bb_t201,
    'J401': bb_j401, 'J402': bb_j402,
}
problems = []
names = list(TOP_BOXES.keys())
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = TOP_BOXES[names[i]], TOP_BOXES[names[j]]
        if overlap(a, b):
            problems.append(f'KOLIZJA (top): {names[i]} x {names[j]}')

for name, (x0, y0, x1, y1) in TOP_BOXES.items():
    if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
        problems.append(f'POZA OBUDOWA: {name} bbox={(x0, y0, x1, y1)}')

# odleglosci lamp (>=35mm miedzy soba, center-center)
lamp_centers = {'U1': (178, 45), 'U2': (128, 90), 'U202': (228, 90)}
lnames = list(lamp_centers.keys())
for i in range(len(lnames)):
    for j in range(i + 1, len(lnames)):
        p, q = lamp_centers[lnames[i]], lamp_centers[lnames[j]]
        d = math.hypot(p[0] - q[0], p[1] - q[1])
        if d < 35:
            problems.append(f'LAMPY ZA BLISKO: {lnames[i]}-{lnames[j]} d={d:.1f}mm (<35mm)')

# odleglosc lamp od transformatorow (krawedz-krawedz, >=25mm)
def edge_dist_circle_rect(c, d, rect):
    cx, cy = c
    x0, y0, x1, y1 = rect
    nx = max(x0 - cx, 0, cx - x1)
    ny = max(y0 - cy, 0, cy - y1)
    dist_center_to_rect = math.hypot(nx, ny)
    return dist_center_to_rect - d / 2

xf_boxes = {'T301': bb_t301, 'T1': bb_t1, 'T201': bb_t201, 'L1': bb_l1}
for lname, c in lamp_centers.items():
    for xname, box in xf_boxes.items():
        dd = edge_dist_circle_rect(c, 22, box)
        if dd < 25:
            problems.append(f'LAMPA-TRAFO ZA BLISKO: {lname}-{xname} gap={dd:.1f}mm (<25mm)')

# T301 >=100mm (center-center) od RV1, RCA (srodek J401/J402), ECC82 (U1)
t301_c = (50, 155)
rv1_c = (140, 14)
rca_c = ((182 + 198) / 2, 192)
u1_c = lamp_centers['U1']
for name, c in [('RV1', rv1_c), ('RCA(J401/J402)', rca_c), ('U1(ECC82)', u1_c)]:
    d = math.hypot(t301_c[0] - c[0], t301_c[1] - c[1])
    if d < 100:
        problems.append(f'T301 ZA BLISKO {name}: d={d:.1f}mm (<100mm)')

if problems:
    print('PROBLEMY GEOMETRII:')
    for p in problems:
        print(' -', p)
else:
    print('Geometria OK: brak kolizji (gorna plyta), wszystko w obudowie, '
          'odstepy lamp/trafo oraz T301-RV1/RCA/ECC82 (>=100mm) zachowane.')

os.makedirs(os.path.dirname(OUT_SVG), exist_ok=True)
fig.savefig(OUT_SVG, format='svg')
fig.savefig(OUT_PNG, format='png', dpi=180)
print('Zapisano:', OUT_SVG)
print('Zapisano:', OUT_PNG)
