"""riaa_preamp_purist.kicad_sch rev P — lampowy przedwzmacniacz RIAA, STEREO, wersja finalna.
2x ECC83 + ECC82 CF, pasywna RIAA, B+ rozdzielone per kanal, dlawik (opcja R),
bleedery, auto-rozladowanie K1, muting K2/K3 z opoznieniem, SW1 DPST + neonowka,
NTC, warystor, snubber RC, ground breaker GND/PE."""
import uuid as uuidlib
import symlib

def U(): return str(uuidlib.uuid4())

ROOT = U()
PROJECT = "riaa_preamp"

# ---------- embedded library symbols ----------
EMBED = []
def embed(lib, name, newname=None, value=None, datasheet=None, desc=None):
    if newname:
        sym = symlib.clone_as(lib, name, newname, value=value, datasheet=datasheet, desc=desc)
    else:
        sym = symlib.resolve(lib, name)
    EMBED.append(symlib.embed_text(sym, lib))

LIBPARTS = [('Device','R'),('Device','C'),('Device','C_Polarized'),('Device','D'),
            ('Device','Fuse'),('Device','Transformer_1P_2S'),('Device','L_Iron'),
            ('Device','Lamp_Neon'),('Device','Varistor'),('Device','Thermistor_NTC'),
            ('Connector','Conn_Coaxial'),('Connector','Screw_Terminal_01x03'),
            ('Regulator_Linear','LM317_TO-220'),('Relay','Relay_SPDT'),
            ('Switch','SW_DPST_x2'),('Switch','SW_DPDT_x2'),('Transistor_FET','2N7000'),
            ('Relay','G5V-2'),('Device','Battery'),('Device','Voltmeter_DC'),
            ('Connector','Screw_Terminal_01x02'),
            ('Valve','ECC83'),
            ('power','GND'),('power','PWR_FLAG'),('power','Earth_Protective')]
for lib,name in LIBPARTS:
    embed(lib,name)
embed('Valve','ECC81','ECC82', value='ECC82',
      datasheet='http://www.r-type.org/pdfs/ecc82.pdf', desc='double triode')

PINGEO = {}
for lib,name in LIBPARTS:
    PINGEO[f'{lib}:{name}'] = symlib.pins(symlib.resolve(lib,name))
PINGEO['Valve:ECC82'] = symlib.pins(symlib.resolve('Valve','ECC81'))

def xform(dx, dy, rot, mirror):
    x, y = dx, -dy
    if mirror == 'y': x = -x
    if mirror == 'x': y = -y
    for _ in range(rot // 90):
        x, y = y, -x
    return x, y

SYMS = []
def rp(p): return (round(p[0],2), round(p[1],2))
def place(ref, libid, value, x, y, rot=0, unit=1, mirror=None, fields=None):
    SYMS.append(dict(ref=ref, libid=libid, value=value, x=round(x,2), y=round(y,2),
                     rot=rot, unit=unit, mirror=mirror, fields=fields or {}, uuid=U()))

def pin(ref, number, unit=None):
    for s in SYMS:
        if s['ref'] == ref and (unit is None or s['unit'] == unit):
            geo = PINGEO[s['libid']]
            u = s['unit'] if s['unit'] in geo else 0
            for num, px, py, a, l, nm in geo[u]:
                if num == str(number):
                    ox, oy = xform(px, py, s['rot'], s['mirror'])
                    return (round(s['x']+ox, 2), round(s['y']+oy, 2))
    raise KeyError((ref, number, unit))

WIRES = []; JUNCS = []; LABELS = []; TEXTS = []; NOCONN = []
def wire(*pts):
    pts = [rp(p) for p in pts]
    for a, b in zip(pts, pts[1:]):
        if a == b: continue
        assert a[0]==b[0] or a[1]==b[1], ('non-orthogonal', a, b)
        WIRES.append((a, b))
def junc(p): JUNCS.append(rp(p))
def label(name, p, rot=0, just='left bottom'):
    LABELS.append((name, rp(p), rot, just))
def text(s, x, y, size=1.27, rot=0):
    TEXTS.append((s, round(x,2), round(y,2), size, rot))
def noconn(p): NOCONN.append(rp(p))

def gnd(x, y):
    place('#GND%d'%len(SYMS), 'power:GND', 'GND', x, y)
def pwrflag(x, y):
    place('#FLG%d'%len(SYMS), 'power:PWR_FLAG', 'PWR_FLAG', x, y)
def pe(x, y):
    place('#PE%d'%len(SYMS), 'power:Earth_Protective', 'Earth_Protective', x, y)

# =======================  AUDIO CHANNEL  =======================
def channel(o, rn, sfx, jin, jout, vref, cfref, cfu, chname):
    A,G,K = ('6','7','8') if cfu == 1 else ('1','2','3')
    YS = 88.9+o; YC = 73.66+o
    text(chname, 27.94, 53.34+o, 2.0)
    place(jin,'Connector:Conn_Coaxial','IN (MM)', 27.94, YS, mirror='y')
    place(rn('R1'),'Device:R','47k', 38.1, 96.52+o)
    place(rn('C1'),'Device:C','150p', 46.99, 96.52+o)
    place(rn('R2'),'Device:R','470R', 55.88, YS, rot=90)
    place(vref,'Valve:ECC83','ECC83', 67.31, YS, unit=1)
    wire(pin(jin,1), (38.1,YS), (46.99,YS), (46.99,pin(rn('C1'),1)[1]))
    wire((38.1,YS), pin(rn('R1'),1))
    wire((46.99,YS), pin(rn('R2'),1))
    junc((38.1,YS)); junc((46.99,YS))
    wire(pin(rn('R1'),2), (38.1,104.14+o)); gnd(38.1,104.14+o)
    wire(pin(rn('C1'),2), (46.99,104.14+o)); gnd(46.99,104.14+o)
    wire(pin(rn('R2'),2), pin(vref,'7',unit=1))
    wire(pin(jin,2), (27.94,96.52+o)); gnd(27.94,96.52+o)
    place(rn('R3'),'Device:R','100k', 67.31, 66.04+o)
    wire(pin(rn('R3'),2), pin(vref,'6',unit=1))
    wire(pin(rn('R3'),1), (67.31,57.15+o)); label('B+1'+sfx,(67.31,57.15+o))
    place(rn('R4'),'Device:R','1k5', 64.77,105.41+o)
    place(rn('C2'),'Device:C_Polarized','220u/25V', 74.93,105.41+o)
    wire(pin(vref,'8',unit=1), pin(rn('R4'),1))
    wire(pin(rn('R4'),1),(74.93,pin(rn('R4'),1)[1]), pin(rn('C2'),1))
    junc(pin(rn('R4'),1))
    wire(pin(rn('R4'),2),(64.77,111.76+o),(69.85,111.76+o),(74.93,111.76+o))
    wire((74.93,111.76+o), pin(rn('C2'),2))
    wire((69.85,111.76+o),(69.85,114.3+o)); gnd(69.85,114.3+o)
    junc((69.85,111.76+o))
    place(rn('C3'),'Device:C','100n', 78.74, YC, rot=90)
    place(rn('R5'),'Device:R','255k', 90.17, YC, rot=90)
    wire(pin(vref,'6',unit=1), (67.31,YC))
    wire((67.31,YC), pin(rn('C3'),1))
    junc((67.31,YC))
    wire(pin(rn('C3'),2), pin(rn('R5'),1))
    wire(pin(rn('R5'),2),(105.41,YC),(113.03,YC),(120.65,YC),(127.0,YC),(127.0,YS),(130.81,YS))
    junc((105.41,YC)); junc((113.03,YC)); junc((120.65,YC))
    place(rn('C4'),'Device:C','3n3', 105.41, 80.01+o)
    wire((105.41,YC), pin(rn('C4'),1)); wire(pin(rn('C4'),2),(105.41,86.36+o)); gnd(105.41,86.36+o)
    place(rn('R6'),'Device:R','33k', 113.03, 80.01+o)
    place(rn('C5'),'Device:C','9n62', 113.03, 90.17+o)
    wire((113.03,YC), pin(rn('R6'),1)); wire(pin(rn('R6'),2), pin(rn('C5'),1))
    wire(pin(rn('C5'),2),(113.03,96.52+o)); gnd(113.03,96.52+o)
    place(rn('R7'),'Device:R','1M', 120.65, 80.01+o)
    wire((120.65,YC), pin(rn('R7'),1))
    gnd(120.65,83.82+o)
    place(rn('R8'),'Device:R','1k', 134.62, YS, rot=90)
    place(vref,'Valve:ECC83','ECC83', 146.05, YS, unit=2)
    wire(pin(rn('R8'),2), pin(vref,'2',unit=2))
    place(rn('R9'),'Device:R','100k', 146.05, 66.04+o)
    wire(pin(rn('R9'),2), pin(vref,'1',unit=2))
    wire(pin(rn('R9'),1),(146.05,57.15+o)); label('B+2'+sfx,(146.05,57.15+o))
    place(rn('R10'),'Device:R','1k5', 143.51,105.41+o)
    place(rn('C6'),'Device:C_Polarized','220u/25V', 153.67,105.41+o)
    wire(pin(vref,'3',unit=2), pin(rn('R10'),1))
    wire(pin(rn('R10'),1),(153.67,pin(rn('R10'),1)[1]), pin(rn('C6'),1))
    junc(pin(rn('R10'),1))
    wire(pin(rn('R10'),2),(143.51,111.76+o),(148.59,111.76+o),(153.67,111.76+o))
    wire((153.67,111.76+o), pin(rn('C6'),2))
    wire((148.59,111.76+o),(148.59,114.3+o)); gnd(148.59,114.3+o)
    junc((148.59,111.76+o))
    place(rn('C7'),'Device:C','100n', 157.48, YC, rot=90)
    wire(pin(vref,'1',unit=2),(146.05,YC)); junc((146.05,YC))
    wire((146.05,YC), pin(rn('C7'),1))
    place(rn('R11'),'Device:R','1M', 166.37, 80.01+o)
    place(rn('R12'),'Device:R','1k', 177.8, YS, rot=90)
    wire(pin(rn('C7'),2),(166.37,YC),(172.72,YC),(172.72,YS),(173.99,YS))
    junc((166.37,YC))
    wire((166.37,YC), pin(rn('R11'),1))
    place(cfref,'Valve:ECC82','ECC82', 189.23, YS, unit=cfu)
    wire(pin(rn('R12'),2), pin(cfref,G,unit=cfu))
    wire(pin(cfref,A,unit=cfu),(189.23,64.77+o)); label('B+3',(189.23,64.77+o))
    place(rn('R13'),'Device:R','2k2', 186.69,105.41+o)
    place(rn('R14'),'Device:R','47k', 186.69,115.57+o)
    wire(pin(cfref,K,unit=cfu), pin(rn('R13'),1))
    wire(pin(rn('R13'),2), pin(rn('R14'),1))
    junc(pin(rn('R13'),2))
    wire(pin(rn('R14'),2),(186.69,121.92+o)); gnd(186.69,121.92+o)
    wire(pin(rn('R11'),2),(166.37,109.22+o),(186.69,109.22+o))
    place(rn('C8'),'Device:C','2u2/400V', 199.39, 101.6+o, rot=90)
    junc(pin(rn('R13'),1))
    wire(pin(rn('R13'),1), (195.58,101.6+o))
    place(rn('R15'),'Device:R','470k', 210.82,107.95+o)
    place(jout,'Connector:Conn_Coaxial','OUT', 223.52, 101.6+o)
    wire(pin(rn('C8'),2),(210.82,101.6+o),(215.9,101.6+o),(218.44,101.6+o))
    junc((210.82,101.6+o))
    label('MUTE_'+sfx,(215.9,101.6+o))
    wire((210.82,101.6+o), pin(rn('R15'),1))
    wire(pin(rn('R15'),2),(210.82,114.3+o)); gnd(210.82,114.3+o)
    wire(pin(jout,2),(223.52,109.22+o)); gnd(223.52,109.22+o)
    text("Wejscie MM: 47k / 150p", 27.94, 82.55+o)
    text("OUT -> wzm. mocy", 218.44, 96.52+o, 1.27)

channel(0.0,   lambda b: b, 'L', 'J1','J2','V1','V3',1,'KANAL LEWY (L)')
channel(80.01, lambda b: b[0]+str(int(b[1:])+100), 'R', 'J3','J4','V2','V3',2,'KANAL PRAWY (R)')

text("Siec RIAA (pasywna, na kanal): 3180us / 318us / 75us.", 238.76, 68.58, 1.6)
text("R5 uwzglednia Zwy stopnia 1 (ok. 39k): 255k + 39k = 294k.", 238.76, 71.12, 1.6)
text("C5 = 9,62n -> 8n2 + 1n2 + 220p (rownolegle), 1% PP.  C4 = 3n3 1% PP.", 238.76, 73.66, 1.6)
text("Wzmocnienie ok. 40 dB @ 1 kHz.  Zwy ok. 1k (wtornik katodowy).", 238.76, 76.2, 1.6)
text("Sprzegajace C3, C7: 100n / 630V polipropylen.", 238.76, 78.74, 1.6)
text("V1 = ECC83 kanal L, V2 = ECC83 kanal R (obie polowki).", 238.76, 83.82, 1.6)
text("V3 = ECC82: polowka A -> L, polowka B -> R (wtorniki).", 238.76, 86.36, 1.6)
text("Punkty pracy: stopnie 1/2: ok. 1mA, Vk ok. 1,5V.  Wtornik: ok. 2,4mA, Vk ok. 120V.", 238.76, 91.44, 1.6)

# =======================  custom symbols: trafo CT + EZ81  =======================
def tr_ct_symbol():
    g = []
    def arc(x0,y0,x1,y1,mx,my):
        g.append('(arc (start %s %s) (mid %s %s) (end %s %s) (stroke (width 0.254) (type default)) (fill (type none)))' % (x0,y0,mx,my,x1,y1))
    def line(x0,y0,x1,y1):
        g.append('(polyline (pts (xy %s %s) (xy %s %s)) (stroke (width 0.254) (type default)) (fill (type none)))' % (x0,y0,x1,y1))
    y = -10.16
    for _ in range(8):
        arc(-5.08,y,-5.08,y+2.54,-3.81,y+1.27); y += 2.54
    line(-5.08,10.16,-7.62,10.16); line(-5.08,-10.16,-7.62,-10.16)
    y = 5.08
    for _ in range(4):
        arc(5.08,y,5.08,y+2.54,3.81,y+1.27); y += 2.54
    line(5.08,15.24,7.62,15.24); line(5.08,5.08,7.62,5.08); line(5.08,10.16,7.62,10.16)
    y = -12.7
    for _ in range(2):
        arc(5.08,y,5.08,y+2.54,3.81,y+1.27); y += 2.54
    line(5.08,-7.62,7.62,-7.62); line(5.08,-12.7,7.62,-12.7)
    line(-0.635,-16.51,-0.635,16.51); line(0.635,-16.51,0.635,16.51)
    pins = [(1,-10.16,10.16,0),(2,-10.16,-10.16,0),
            (3,10.16,15.24,180),(4,10.16,10.16,180),(5,10.16,5.08,180),
            (6,10.16,-7.62,180),(7,10.16,-12.7,180)]
    ptxt = ['(pin passive line (at %s %s %d) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "%d" (effects (font (size 1.27 1.27)))))' % (px,py,ang,num) for num,px,py,ang in pins]
    head = '  (symbol "Custom:TR_CT" (pin_names (offset 0)) (in_bom yes) (on_board yes)\n'
    head += '    (property "Reference" "T" (at 0 19.05 0) (effects (font (size 1.27 1.27))))\n'
    head += '    (property "Value" "2x230V + 6,3V" (at 0 -19.05 0) (effects (font (size 1.27 1.27))))\n'
    head += '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
    head += '    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
    head += '    (symbol "TR_CT_0_1"\n        ' + '\n        '.join(g) + '\n    )\n'
    head += '    (symbol "TR_CT_1_1"\n        ' + '\n        '.join(ptxt) + '\n    )\n  )'
    return head

def ez81_symbol():
    g0, g1, g2 = [], [], []
    def P(lst, pts, w=0.254):
        lst.append('(polyline (pts %s) (stroke (width %s) (type default)) (fill (type none)))' % (' '.join('(xy %s %s)'%p for p in pts), w))
    # envelope (unit 0 = wspolne)
    g0.append('(arc (start -5.08 -2.54) (mid 0 -7.5979) (end 5.08 -2.54) (stroke (width 0) (type default)) (fill (type none)))')
    g0.append('(arc (start 5.08 2.54) (mid 0 7.5979) (end -5.08 2.54) (stroke (width 0) (type default)) (fill (type none)))')
    P(g0, [(5.08,2.54),(5.08,-2.54)], 0)
    P(g0, [(-5.08,2.54),(-5.08,-2.54)], 0)
    # unit1: dwie anody + katoda
    P(g1, [(-4.06,2.54),(-1.02,2.54)])
    P(g1, [(1.02,2.54),(4.06,2.54)])
    P(g1, [(-2.54,2.54),(-2.54,7.62)], 0)
    P(g1, [(2.54,2.54),(2.54,7.62)], 0)
    g1.append('(arc (start 2.54 -5.08) (mid 0 -3.0968) (end -2.54 -5.08) (stroke (width 0.254) (type default)) (fill (type none)))')
    P(g1, [(0,-7.62),(-2.54,-5.08)], 0)
    p1 = ['(pin passive line (at -2.54 10.16 270) (length 2.54) (name "A1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))',
          '(pin passive line (at 2.54 10.16 270) (length 2.54) (name "A2" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))',
          '(pin passive line (at 0 -10.16 90) (length 2.54) (name "K" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))']
    # unit2: zarzenie
    P(g2, [(-2.54,-6.35),(0,-4.45),(2.54,-6.35)])
    p2 = ['(pin power_in line (at -2.54 -11.43 90) (length 5.08) (name "F1" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))',
          '(pin power_in line (at 2.54 -11.43 90) (length 5.08) (name "F2" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))']
    s = '  (symbol "Custom:EZ81" (pin_names (offset 0)) (in_bom yes) (on_board yes)\n'
    s += '    (property "Reference" "V" (at 3.302 7.874 0) (effects (font (size 1.27 1.27))))\n'
    s += '    (property "Value" "EZ81" (at 8.89 -7.62 0) (effects (font (size 1.27 1.27))))\n'
    s += '    (property "Footprint" "Valve:Valve_Noval_P" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
    s += '    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
    s += '    (symbol "EZ81_0_1"\n        ' + '\n        '.join(g0) + '\n    )\n'
    s += '    (symbol "EZ81_1_1"\n        ' + '\n        '.join(g1+p1) + '\n    )\n'
    s += '    (symbol "EZ81_2_1"\n        ' + '\n        '.join(g2+p2) + '\n    )\n  )'
    return s

EMBED.append(tr_ct_symbol())
EMBED.append(ez81_symbol())
PINGEO['Custom:TR_CT'] = {1: [
    ('1',-10.16,10.16,0,2.54,'~'),('2',-10.16,-10.16,0,2.54,'~'),
    ('3',10.16,15.24,180,2.54,'~'),('4',10.16,10.16,180,2.54,'~'),
    ('5',10.16,5.08,180,2.54,'~'),('6',10.16,-7.62,180,2.54,'~'),
    ('7',10.16,-12.7,180,2.54,'~')]}
PINGEO['Custom:EZ81'] = {
    1: [('1',-2.54,10.16,270,2.54,'A1'),('7',2.54,10.16,270,2.54,'A2'),
        ('3',0,-10.16,90,2.54,'K')],
    2: [('4',-2.54,-11.43,90,5.08,'F1'),('5',2.54,-11.43,90,5.08,'F2')]}

# =======================  PSU: mains (bez polprzewodnikow)  =======================
LR, NR = 292.1, 311.15
place('J5','Connector:Screw_Terminal_01x03','MAINS 230V', 35.56,294.64, mirror='y',
      fields={'ref_at':(30.48,287.02),'val_at':(30.48,289.56)})
place('F1','Device:Fuse','T500mA', 49.53,LR, rot=90)
place('SW1','Switch:SW_DPST_x2','ON/OFF', 58.42,LR, unit=1,
      fields={'ref_at':(54.61,287.02),'val_at':(54.61,289.56)})
place('SW1','Switch:SW_DPST_x2','ON/OFF', 58.42,NR, unit=2,
      fields={'ref_at':(48.26,313.69),'val_at':(48.26,316.23)})
place('R34','Device:R','22R 5W', 69.85,LR, rot=90,
      fields={'ref_at':(64.77,287.02),'val_at':(64.77,289.56)})
place('T1','Custom:TR_CT','2x230V 0,15A + 6,3V 1A', 106.68,297.18,
      fields={'ref_at':(100.33,276.86),'val_at':(93.98,318.77)})
wire(pin('J5',1), pin('F1',1))
wire(pin('F1',2), pin('SW1',1,unit=1))
wire(pin('SW1',2,unit=1), pin('R34',1))
wire(pin('R34',2),(82.55,LR),(88.9,LR),(92.71,LR),(92.71,287.02),(96.52,287.02))
junc((88.9,LR))
label('L_SW',(82.55,LR))
wire(pin('J5',2),(43.18,294.64),(43.18,NR),(53.34,NR))
wire(pin('SW1',4,unit=2),(82.55,NR),(88.9,NR),(92.71,NR),(92.71,307.34),(96.52,307.34))
junc((88.9,NR))
label('N_SW',(82.55,NR))
wire(pin('J5',3),(41.91,297.18),(41.91,299.72),(41.91,303.53)); pe(41.91,303.53)
wire((41.91,299.72),(39.37,299.72)); junc((41.91,299.72))
pwrflag(39.37,299.72)
text("PE -> wlasna sruba M4 na chassis", 27.94, 310.13, 1.27)
place('R32','Device:R','220k', 88.9,296.52,
      fields={'ref_at':(90.17,294.64),'val_at':(90.17,297.18)})
place('NE1','Device:Lamp_Neon','NE-2 (jewel)', 88.9,305.41,
      fields={'ref_at':(90.17,303.53),'val_at':(90.17,306.07)})
wire((88.9,LR), pin('R32',1))
wire(pin('R32',2), pin('NE1',2))
wire(pin('NE1',1),(88.9,NR))
text("2x230V 0,15A", 119.38, 278.13, 1.27)
text("6,3V 1A (zarz. EZ81)", 121.92, 315.6 if False else 314.96, 1.27)

# =======================  prostownik lampowy EZ81 + filtr LC  =======================
YP, YG = 276.86, 314.96
place('V4','Custom:EZ81','EZ81', 144.78,264.16, unit=1,
      fields={'ref_at':(151.13,259.08),'val_at':(151.13,261.62)})
wire(pin('T1',3),(121.92,281.94),(121.92,251.46),(142.24,251.46))
wire((142.24,251.46), pin('V4','1',unit=1))
wire(pin('T1',5),(119.38,292.1),(119.38,246.38),(147.32,246.38))
wire((147.32,246.38), pin('V4','7',unit=1))
wire(pin('T1',4),(124.46,287.02),(124.46,297.18)); gnd(124.46,297.18)
wire(pin('V4','3',unit=1),(144.78,YP),(151.13,YP))
label('EZH_B',(147.32,YP))
wire(pin('T1',6),(121.92,304.8)); label('EZH_A',(121.92,304.8))
wire(pin('T1',7),(121.92,309.88)); label('EZH_B',(121.92,309.88))
place('C9','Device:C_Polarized','47u/500V !', 151.13,280.67,
      fields={'ref_at':(153.67,285.75),'val_at':(153.67,288.29)})
place('L1','Device:L_Iron','10H 100mA', 163.83,YP, rot=90,
      fields={'ref_at':(160.02,271.78),'val_at':(172.72,274.32),'val_just':'right'})
place('C10','Device:C_Polarized','100u/500V', 176.53,280.67)
wire((151.13,YP), pin('C9',1)); junc((151.13,YP))
wire((151.13,YP), pin('L1',1))
wire(pin('L1',2),(176.53,YP)); junc((176.53,YP))
wire((176.53,YP), pin('C10',1))
wire((176.53,YP),(176.53,266.7)); label('B+3',(176.53,266.7))
# --- droppery kanal L i R (jak rev E) ---
place('R18','Device:R','10k 1W', 187.96,YP, rot=90)
place('C12','Device:C_Polarized','47u/400V', 198.12,280.67)
place('R26','Device:R','470k 1W', 205.74,280.67,
      fields={'ref_at':(208.28,278.13),'val_at':(208.28,280.67)})
place('R19','Device:R','22k 1W', 214.63,YP, rot=90)
place('C13','Device:C_Polarized','47u/400V', 224.79,280.67)
place('R27','Device:R','470k 1W', 232.41,280.67,
      fields={'ref_at':(234.95,278.13),'val_at':(234.95,280.67)})
wire((176.53,YP), pin('R18',1))
wire(pin('R18',2),(198.12,YP)); junc((198.12,YP))
wire((198.12,YP), pin('C12',1))
wire((198.12,YP),(198.12,266.7)); label('B+2L',(198.12,266.7))
wire((198.12,YP),(205.74,YP)); junc((205.74,YP))
wire((205.74,YP), pin('R26',1))
wire((205.74,YP), pin('R19',1))
wire(pin('R19',2),(224.79,YP)); junc((224.79,YP))
wire((224.79,YP), pin('C13',1))
wire((224.79,YP),(224.79,266.7)); label('B+1L',(224.79,266.7))
wire((224.79,YP),(232.41,YP))
wire((232.41,YP), pin('R27',1))
label('B+3',(245.11,YP), just='right bottom')
place('R118','Device:R','10k 1W', 248.92,YP, rot=90)
place('C112','Device:C_Polarized','47u/400V', 259.08,280.67)
place('R126','Device:R','470k 1W', 266.7,280.67,
      fields={'ref_at':(269.24,278.13),'val_at':(269.24,280.67)})
place('R119','Device:R','22k 1W', 275.59,YP, rot=90)
place('C113','Device:C_Polarized','47u/400V', 285.75,280.67)
place('R127','Device:R','470k 1W', 293.37,280.67,
      fields={'ref_at':(295.91,278.13),'val_at':(295.91,280.67)})
wire((245.11,YP), pin('R118',1))
wire(pin('R118',2),(259.08,YP)); junc((259.08,YP))
wire((259.08,YP), pin('C112',1))
wire((259.08,YP),(259.08,266.7)); label('B+2R',(259.08,266.7))
wire((259.08,YP),(266.7,YP)); junc((266.7,YP))
wire((266.7,YP), pin('R126',1))
wire((266.7,YP), pin('R119',1))
wire(pin('R119',2),(285.75,YP)); junc((285.75,YP))
wire((285.75,YP), pin('C113',1))
wire((285.75,YP),(285.75,266.7)); label('B+1R',(285.75,266.7))
wire((285.75,YP),(293.37,YP))
wire((293.37,YP), pin('R127',1))
# gnd rail
wire(pin('C9',2),(151.13,YG))
wire(pin('C10',2),(176.53,YG))
for xc in (198.12,205.74,224.79,232.41,259.08,266.7,285.75,293.37):
    wire((xc,284.48),(xc,YG))
wire((151.13,YG),(160.02,YG),(176.53,YG),(198.12,YG),(205.74,YG),(224.79,YG),(232.41,YG),(259.08,YG),(266.7,YG),(285.75,YG),(293.37,YG),(311.15,YG),(318.77,YG),(323.85,YG))
for x in (160.02,176.53,198.12,205.74,224.79,232.41,259.08,266.7,285.75,293.37,311.15,318.77):
    junc((x,YG))
wire((160.02,YG),(160.02,317.5)); gnd(160.02,317.5)
pwrflag(323.85,YG)
# dzielnik elewacji (ELEV = minus zarzenia, +50V)
place('R22','Device:R','470k', 311.15,281.94,
      fields={'ref_at':(304.8,280.67),'val_at':(308.61,283.21),'val_just':'right'})
place('R23','Device:R','100k', 311.15,294.64,
      fields={'ref_at':(304.8,293.37),'val_at':(308.61,295.91),'val_just':'right'})
wire(pin('R22',1),(311.15,266.7)); label('B+3',(311.15,266.7))
wire(pin('R22',2),(311.15,288.29))
wire((311.15,288.29), pin('R23',1))
wire(pin('R23',2),(311.15,YG))
place('C17','Device:C_Polarized','22u/100V', 318.77,294.64,
      fields={'ref_at':(321.31,303.53),'val_at':(321.31,306.07)})
wire((311.15,288.29),(318.77,288.29), pin('C17',1))
junc((311.15,288.29))
wire(pin('C17',2),(318.77,YG))
label('HTR_B', (313.69,288.29))

# ==============  K1: straznik baterii + rozladowanie (cewka 230V AC)  ==============
place('K1','Relay:G5V-2','DPDT, cewka 230V AC', 349.25,280.67,
      fields={'ref_at':(335.28,292.1),'val_at':(335.28,294.64)})
wire(pin('K1',1),(339.09,267.97),(327.66,267.97),(302.26,267.97))
label('L_SW',(302.26,267.97), just='right bottom')
junc((327.66,267.97))
wire(pin('K1',16),(339.09,300.99),(327.66,300.99),(302.26,300.99))
label('N_SW',(302.26,300.99), just='right bottom')
junc((327.66,300.99))
place('R33','Device:R','100R', 327.66,271.78,
      fields={'ref_at':(321.31,270.51),'val_at':(326.39,273.05),'val_just':'right'})
place('C21','Device:C','100n/630V', 327.66,281.94,
      fields={'ref_at':(318.77,280.67),'val_at':(326.39,283.21),'val_just':'right'})
wire(pin('R33',1),(327.66,267.97))
wire(pin('R33',2), pin('C21',1))
wire(pin('C21',2),(327.66,300.99))
# pole1: straznik baterii (NO)
wire(pin('K1',4),(349.25,309.88)); label('BATT_SW',(349.25,309.88))
wire(pin('K1',8),(351.79,264.16),(335.28,264.16))
label('HTR_A',(335.28,264.16), just='right bottom')
noconn(pin('K1',6))
# pole2: rozladowanie B+ (NC)
wire(pin('K1',11),(356.87,260.35)); label('B+3',(356.87,260.35))
noconn(pin('K1',9))
place('R24','Device:R','4k7 10W', 364.49,294.64,
      fields={'ref_at':(367.03,292.1),'val_at':(367.03,294.64)})
wire(pin('K1',13),(359.41,290.83),(364.49,290.83))
wire((364.49,290.83), pin('R24',1))
wire(pin('R24',2),(364.49,300.99)); gnd(364.49,300.99)
text("K1 (np. Finder 40.52, cewka 230V AC): siec jest -> bateria dolaczona (styk NO)", 368.3, 253.99 if False else 254.0, 1.6)
text("i rozladowanie odlaczone; siec znika -> bateria odcieta (nie rozladuje sie", 368.3, 256.54, 1.6)
text("w pozycji PRACA), a NC laczy B+3 z R24 (B+ <50V w ok. 15 s). Snubber R33/C21.", 368.3, 259.08, 1.6)

# ==============  zarzenie z baterii (6V AGM) + PRACA/LADOWANIE + woltomierz  ==============
place('F2','Device:Fuse','2A (przy zacisku!)', 375.92,300.99,
      fields={'ref_at':(378.46,299.72),'val_at':(378.46,302.26)})
place('BT1','Device:Battery','AGM 6V 10-12Ah', 375.92,313.69,
      fields={'ref_at':(368.3,318.77),'val_at':(370.84,321.31),'val_just':'right'})
place('SW2','Switch:SW_DPDT_x2','PRACA/LADOW.', 391.16,294.64, unit=1,
      fields={'ref_at':(387.35,285.75),'val_at':(387.35,288.29)})
place('SW2','Switch:SW_DPDT_x2','PRACA/LADOW.', 391.16,309.88, unit=2,
      fields={'ref_at':(387.35,318.77),'val_at':(387.35,321.31)})
place('J6','Connector:Screw_Terminal_01x02','LADOWANIE (tyl)', 424.18,321.31, mirror='y',
      fields={'ref_at':(419.1,316.23),'val_at':(416.56,314.96)})
wire(pin('BT1',1), pin('F2',2))
wire(pin('F2',1),(375.92,294.64), pin('SW2',2,unit=1))
wire(pin('SW2',1,unit=1),(401.32,292.1)); label('BATT_SW',(401.32,292.1))
wire(pin('SW2',3,unit=1),(401.32,297.18)); label('CHG_P',(401.32,297.18))
wire(pin('BT1',2),(375.92,321.31),(383.54,321.31),(383.54,309.88))
wire((383.54,309.88), pin('SW2',5,unit=2))
wire(pin('SW2',4,unit=2),(401.32,307.34)); label('HTR_B',(401.32,307.34))
wire(pin('SW2',6,unit=2),(401.32,312.42)); label('CHG_N',(401.32,312.42))
wire(pin('J6',1),(434.34,321.31)); label('CHG_P',(434.34,321.31))
wire(pin('J6',2),(434.34,323.85)); label('CHG_N',(434.34,323.85))
place('R30','Device:R','dobrac do M1', 414.02,318.77,
      fields={'ref_at':(408.94,315.6 if False else 314.96),'val_at':(408.94,317.5),'val_just':'right'})
place('M1','Device:Voltmeter_DC','6V (strefa 6,0-6,4)', 414.02,331.47,
      fields={'ref_at':(419.1,328.93),'val_at':(419.1,331.47)})
wire((414.02,311.15),(414.02,pin('R30',1)[1])); label('HTR_A',(414.02,311.15))
wire(pin('R30',2), pin('M1',2))
wire(pin('M1',1),(414.02,339.09)); label('HTR_B',(414.02,339.09))
text("Bateria: TYLKO AGM/zel. F2 bezposrednio przy zacisku. Obejma do dna (masa=stabilnosc).", 355.6, 344.17, 1.6)
text("Ladowarka ZEWNETRZNA (buforowa, float 6,75-6,9V) -> gniazdo J6 z tylu.", 355.6, 346.71, 1.6)
text("SW2 na froncie: PRACA (gora) / LADOWANIE (dol). M1 wskazuje tylko podczas grania.", 355.6, 349.25, 1.6)

# tube heaters (audio z baterii, EZ81 z uzwojenia 6,3V)
for ref, lid, val, xh in (('V1','Valve:ECC83','ECC83',256.54),
                          ('V2','Valve:ECC83','ECC83',281.94),
                          ('V3','Valve:ECC82','ECC82',307.34)):
    place(ref, lid, val, xh, 355.6, unit=3)
    y0 = 367.03
    wire((xh-2.54,y0),(xh-2.54,372.11),(xh+2.54,372.11))
    wire((xh+2.54,y0),(xh+2.54,372.11))
    wire((xh-2.54,372.11),(xh-7.62,372.11))
    junc((xh-2.54,372.11))
    label('HTR_A',(xh-7.62,372.11), just='right bottom')
    wire((xh,y0),(xh,369.57),(xh+7.62,369.57))
    label('HTR_B',(xh+7.62,369.57))
place('V4','Custom:EZ81','EZ81', 345.44,355.6, unit=2,
      fields={'ref_at':(351.79,353.06),'val_at':(351.79,355.6)})
wire(pin('V4','4',unit=2),(342.9,369.57),(337.82,369.57))
label('EZH_A',(337.82,369.57), just='right bottom')
wire(pin('V4','5',unit=2),(347.98,372.11),(353.06,372.11))
label('EZH_B',(353.06,372.11))

# ==============  ground breaker (bez diod - wariant purystyczny)  ==============
place('R25','Device:R','10R 5W', 45.72,325.12,
      fields={'ref_at':(43.18,316.23),'val_at':(43.18,318.77)})
place('C18','Device:C','100n/630V', 55.88,325.12,
      fields={'ref_at':(50.8,332.74),'val_at':(50.8,335.28)})
wire((40.64,321.31),(45.72,321.31),(55.88,321.31))
wire((43.18,328.93),(45.72,328.93),(55.88,328.93))
junc((45.72,321.31)); junc((45.72,328.93))
gnd(40.64,321.31)
pe(43.18,328.93)
text("Ground breaker BEZ diod (puryzm): 10R || 100n.", 27.94, 340.36, 1.27)
text("Kompromis: brak twardej sciezki zwarciowej GND->PE;", 27.94, 342.9, 1.27)
text("alternatywa vintage: masa na sztywno do chassis", 27.94, 345.44, 1.27)
text("przy gniazdach wejsciowych.", 27.94, 347.98, 1.27)

# =======================  annotations  =======================
text("PRZEDWZMACNIACZ GRAMOFONOWY RIAA (STEREO)  -  WARIANT PURYSTYCZNY: ZERO POLPRZEWODNIKOW  -  rev P", 27.94, 27.94, 2.54)
text("Prostownik: EZ81 (dwupolowkowy, trafo 2x230V z odczepem). C9 max 50uF - limit EZ81!", 146.05, 224.79, 1.6)
text("Miekki start: katoda EZ81 grzeje sie ~15 s -> B+ wstaje po lampach audio; uklad mute ZBEDNY.", 146.05, 227.33, 1.6)
text("Zarzenie lamp audio: bateria AGM 6V (DC idealne, zero tetnien). Zarzenie EZ81: uzwojenie 6,3V,", 146.05, 229.87, 1.6)
text("koniec uzwojenia dowiazany do katody (EZH_B). Minus zarzenia (HTR_B) podniesiony do +50V (R22/R23).", 146.05, 232.41, 1.6)
text("B+3 ok. 285-300V (zaleznie od trafo i DCR dlawika). B+2 ok. 285V. B+1 ok. 265V.", 146.05, 234.95, 1.6)
text("Alternatywa zarzenia bez baterii: AC + skrecona para + humdinger 100R + elewacja (ryzyko brumu).", 146.05, 237.49, 1.6)
text("UWAGA: napiecia do ok. 330V DC - smiertelnie niebezpieczne. Po wylaczeniu odczekac na", 27.94, 359.41, 1.6)
text("rozladowanie (K1/R24 + bleedery) i SPRAWDZIC woltomierzem KAZDA sekcje (<50V).", 27.94, 361.95, 1.6)
text("UWAGA 2: zwarcie baterii AGM = setki amperow. F2 przy zacisku to nie opcja.", 27.94, 366.71 if False else 366.4, 1.6)

# wariant purystyczny: bez ukladu mute -> etykiety MUTE_* z toru audio usuwamy
LABELS[:] = [l for l in LABELS if not l[0].startswith('MUTE_')]

# =======================  serialize  =======================
def fmt(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return s if s else '0'

out = []
out.append('(kicad_sch (version 20230121) (generator eeschema)')
out.append('  (uuid %s)' % ROOT)
out.append('  (paper "A2")')
out.append('''  (title_block
    (title "Przedwzmacniacz gramofonowy RIAA - lampowy (stereo) - WARIANT PURYSTYCZNY")
    (date "2026-08-25")
    (rev "P")
    (company "PlotTwist / Wiktoryn")
    (comment 1 "ZERO POLPRZEWODNIKOW: EZ81, zarzenie z baterii AGM 6V, straznik K1 230V AC")
    (comment 2 "2x ECC83 + ECC82, pasywna RIAA, B+ per kanal, filtr LC, woltomierz baterii")
  )''')
out.append('  (lib_symbols')
out.extend(EMBED)
out.append('  )')

for (a,b) in WIRES:
    out.append('  (wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))'
               % (fmt(a[0]),fmt(a[1]),fmt(b[0]),fmt(b[1]),U()))
for p in JUNCS:
    out.append('  (junction (at %s %s) (diameter 0) (color 0 0 0 0) (uuid %s))'
               % (fmt(p[0]),fmt(p[1]),U()))
for p in NOCONN:
    out.append('  (no_connect (at %s %s) (uuid %s))' % (fmt(p[0]),fmt(p[1]),U()))
for (name,p,rot,just) in LABELS:
    out.append('  (label "%s" (at %s %s %d) (effects (font (size 1.27 1.27)) (justify %s)) (uuid %s))'
               % (name,fmt(p[0]),fmt(p[1]),rot,just,U()))
for (s,x,y,size,rot) in TEXTS:
    out.append('  (text "%s" (at %s %s %d) (effects (font (size %s %s)) (justify left bottom)) (uuid %s))'
               % (s,fmt(x),fmt(y),rot,fmt(size),fmt(size),U()))

for s in SYMS:
    libid = s['libid']; x,y,rot = s['x'],s['y'],s['rot']
    mir = (' (mirror %s)' % s['mirror']) if s['mirror'] else ''
    power = libid.startswith('power:')
    geo = PINGEO[libid]
    u = s['unit'] if s['unit'] in geo else 0
    out.append('  (symbol (lib_id "%s") (at %s %s %d)%s (unit %d)' % (libid,fmt(x),fmt(y),rot,mir,s['unit']))
    out.append('    (in_bom %s) (on_board yes) (dnp no)' % ('no' if power else 'yes'))
    out.append('    (uuid %s)' % s['uuid'])
    pang = (360 - rot) % 360
    horiz = rot in (90, 270)
    if libid.startswith('Valve:'):
        rpos, vpos = (x+6.35, y-6.35), (x+6.35, y-3.81)
        if s['unit']==3: rpos, vpos = (x+6.35, y-2.54), (x+6.35, y)
    elif libid == 'Device:D':
        rpos, vpos = (x+2.54, y-1.27), (x+2.54, y+1.27)
    elif horiz:
        rpos, vpos = (x-3.81, y-5.08), (x-3.81, y-2.54)
    else:
        rpos, vpos = (x+2.54, y-1.27), (x+2.54, y+1.27)
    if 'ref_at' in s['fields']: rpos = s['fields']['ref_at']
    if 'val_at' in s['fields']: vpos = s['fields']['val_at']
    vjust = s['fields'].get('val_just','left')
    ref_effects = '(effects (font (size 1.27 1.27)) (justify left))'
    val_effects = '(effects (font (size 1.27 1.27)) (justify %s))' % vjust
    if power:
        out.append('    (property "Reference" "%s" (at %s %s 0) (effects (font (size 1.27 1.27)) hide))' % (s['ref'],fmt(x),fmt(y)))
        vhide = 'hide' if (libid.endswith('PWR_FLAG') or libid.endswith('Earth_Protective')) else ''
        out.append('    (property "Value" "%s" (at %s %s 0) (effects (font (size 1.27 1.27)) %s))'
                   % (s['value'],fmt(x),fmt(y+3.81 if libid.endswith('GND') else y-3.81),vhide))
    else:
        out.append('    (property "Reference" "%s" (at %s %s %d) %s)' % (s['ref'],fmt(rpos[0]),fmt(rpos[1]),pang,ref_effects))
        out.append('    (property "Value" "%s" (at %s %s %d) %s)' % (s['value'],fmt(vpos[0]),fmt(vpos[1]),pang,val_effects))
    out.append('    (property "Footprint" "" (at %s %s 0) (effects (font (size 1.27 1.27)) hide))' % (fmt(x),fmt(y)))
    out.append('    (property "Datasheet" "" (at %s %s 0) (effects (font (size 1.27 1.27)) hide))' % (fmt(x),fmt(y)))
    for num,px,py,a,l,nm in geo[u]:
        out.append('    (pin "%s" (uuid %s))' % (num,U()))
    out.append('    (instances (project "%s" (path "/%s" (reference "%s") (unit %d))))' % (PROJECT,ROOT,s['ref'],s['unit']))
    out.append('  )')

out.append('  (sheet_instances (path "/" (page "1")))')
out.append(')')

with open('riaa_preamp_purist.kicad_sch','w') as f:
    f.write('\n'.join(out) + '\n')
print('wrote riaa_preamp.kicad_sch,', len(SYMS), 'symbols,', len(WIRES), 'wires')
