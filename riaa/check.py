"""Verify netlist connectivity — rev D (stereo, per-channel B+, muting, discharge)."""
import re, sys
import symlib

tree, _ = symlib.parse(symlib.tokenize(open('riaa.net').read()), 0)
nets = {}; node2net = {}
for n in tree:
    if isinstance(n, list) and n[0] == 'nets':
        for net in n[1:]:
            name = None; members = []
            for e in net:
                if isinstance(e, list) and e[0] == 'name': name = symlib.unq(e[1])
                if isinstance(e, list) and e[0] == 'node':
                    ref = pinn = None
                    for f in e:
                        if isinstance(f, list) and f[0]=='ref': ref = symlib.unq(f[1])
                        if isinstance(f, list) and f[0]=='pin': pinn = symlib.unq(f[1])
                    members.append((ref,pinn))
            for m in members: node2net[m] = name
            nets[name] = members

def N(ref, pin): return node2net.get((ref,str(pin)), '<<UNCONNECTED %s.%s>>' % (ref,pin))

fails = []
def same(*nodes):
    names = {N(r,p) for r,p in nodes}
    if len(names) != 1:
        fails.append('NOT SAME NET: ' + ', '.join('%s.%s=%s'%(r,p,N(r,p)) for r,p in nodes))
def diff(a, b):
    if N(*a) == N(*b):
        fails.append('UNEXPECTED SHORT: %s and %s on %s' % (a,b,N(*a)))

def chan(rn, jin, jout, vref, cfref, cfp, dropR, dropC, bleed, mute_relay):
    A,G,K = cfp
    same((jin,1),(rn('R1'),1),(rn('C1'),1),(rn('R2'),1))
    same((rn('R2'),2),(vref,7))
    same((vref,6),(rn('R3'),2),(rn('C3'),1))
    same((vref,8),(rn('R4'),1),(rn('C2'),1))
    same((rn('C3'),2),(rn('R5'),1))
    same((rn('R5'),2),(rn('C4'),1),(rn('R6'),1),(rn('R7'),1),(rn('R8'),1))
    same((rn('R6'),2),(rn('C5'),1))
    same((rn('R8'),2),(vref,2))
    same((vref,1),(rn('R9'),2),(rn('C7'),1))
    same((vref,3),(rn('R10'),1),(rn('C6'),1))
    same((rn('C7'),2),(rn('R11'),1),(rn('R12'),1))
    same((rn('R12'),2),(cfref,G))
    same((cfref,K),(rn('R13'),1),(rn('C8'),1))
    same((rn('R13'),2),(rn('R14'),1),(rn('R11'),2))
    same((rn('C8'),2),(rn('R15'),1),(jout,1),(mute_relay,11))     # wyjscie + mute
    same((rn('R1'),2),(rn('C1'),2),(jin,2),(rn('R4'),2),(rn('C2'),2),(rn('C4'),2),
         (rn('C5'),2),(rn('R7'),2),(rn('R10'),2),(rn('C6'),2),(rn('R14'),2),
         (rn('R15'),2),(jout,2),('C9',2))
    diff((jin,2),('J5',3))
    # B+ per kanal
    same((rn('R3'),1),(dropC[1],1),(dropR[1],2),(bleed[1],1))     # B+1x
    same((rn('R9'),1),(dropC[0],1),(dropR[0],2),(dropR[1],1),(bleed[0],1))  # B+2x
    same((cfref,A),('C10',1),(dropR[0],1))                        # B+3
    diff((vref,6),(vref,7)); diff((rn('C8'),1),(rn('C8'),2))
    diff((vref,6),(vref,1)); diff((rn('R5'),2),(rn('C3'),1))

chan(lambda b: b, 'J1','J2','V1','V3',(6,7,8),
     ('R18','R19'),('C12','C13'),('R26','R27'),'K2')
chan(lambda b: b[0]+str(int(b[1:])+100), 'J3','J4','V2','V3',(1,2,3),
     ('R118','R119'),('C112','C113'),('R126','R127'),'K3')
diff(('V1',6),('V2',6)); diff(('J2',1),('J4',1)); diff(('R5',2),('R105',2))
diff(('R3',1),('R103',1)); diff(('R9',1),('R109',1))              # B+ kanaly osobno

# masa (GND) — bez PE
same(('C9',2),('C10',2),('C12',2),('C13',2),('C112',2),('C113',2),
     ('R26',2),('R27',2),('R126',2),('R127',2),('R23',2),('C17',2),('R24',2),
     ('R25',1),('D10',1),('D11',2),('C18',1),('K2',12),('K3',12))
# PE / chassis
same(('J5',3),('R25',2),('D10',2),('D11',1),('C18',2))
diff(('J5',3),('C9',2))

# siec 230V
same(('J5',1),('F1',1))
same(('F1',2),('SW1',1))
same(('SW1',2),('RT1',1))
same(('RT1',2),('T1',1),('RV1',1),('R32',1))
same(('J5',2),('SW1',3))
same(('SW1',4),('T1',2),('RV1',2),('NE1',1))
same(('R32',2),('NE1',2))
diff(('SW1',1),('SW1',2)); diff(('SW1',3),('SW1',4))
diff(('T1',1),('T1',2))

# HT: mostek, snubber, filtr
same(('T1',3),('D1',2),('D3',1),('RS1',1))
same(('T1',4),('D2',2),('D4',1),('CS1',2))
same(('RS1',2),('CS1',1))
same(('D1',1),('D2',1),('C9',1),('L1',1))
same(('L1',2),('C10',1),('R18',1),('R118',1),('R22',1),('K1',12))  # B+3
same(('D3',2),('D4',2),('C9',2))
same(('R22',2),('R23',1),('C17',1))
# rozladowanie
same(('K1',11),('R24',1))
diff(('K1',11),('K1',12)); diff(('K1','A1'),('K1','A2'))

# zarzenie
same(('T1',7),('D5',2),('D7',1))
same(('T1',9),('D6',2),('D8',1))
same(('D5',1),('D6',1),('C14',1),('C19',1),('U1',3),('K1','A1'),('D9',1),
     ('K2','A1'),('K3','A1'),('D12',1),('D13',1),('R31',1))        # V_RAW
same(('U1',2),('R20',1),('C16',1),('V1',4),('V1',5),('V2',4),('V2',5),('V3',4),('V3',5))
same(('U1',1),('R20',2),('R21',1),('C15',1))
same(('D7',2),('D8',2),('C14',2),('C19',2),('R21',2),('C15',2),('C16',2),
     ('R22',2),('Q1',1),('C20',2),('V1',9),('V2',9),('V3',9))      # ELEV
diff(('D5',1),('U1',2)); diff(('U1',2),('D7',2)); diff(('D7',2),('C9',2))
# muting
same(('R31',2),('D13',2),('C20',1),('Q1',2))                       # gate
same(('Q1',3),('K2','A2'),('K3','A2'),('D12',2))                   # drain
diff(('Q1',2),('Q1',3)); diff(('K2',11),('K2',12)); diff(('K3',11),('K3',12))
diff(('K2',11),('K3',11))

print('Nets:', len(nets))
if fails:
    print('FAILURES:'); [print(' ', f) for f in fails]; sys.exit(1)
print('ALL CONNECTIVITY CHECKS PASSED')
