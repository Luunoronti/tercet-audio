"""Verify netlist — wariant purystyczny rev P."""
import sys
import symlib

tree, _ = symlib.parse(symlib.tokenize(open('riaa_purist.net').read()), 0)
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

def N(r,p): return node2net.get((r,str(p)), '<<UNCONNECTED %s.%s>>' % (r,p))
fails = []
def same(*nodes):
    names = {N(r,p) for r,p in nodes}
    if len(names) != 1:
        fails.append('NOT SAME NET: ' + ', '.join('%s.%s=%s'%(r,p,N(r,p)) for r,p in nodes))
def diff(a,b):
    if N(*a) == N(*b): fails.append('SHORT: %s %s on %s' % (a,b,N(*a)))

def chan(rn, jin, jout, vref, cfref, cfp, dropR, dropC, bleed):
    A,G,K = cfp
    same((jin,1),(rn('R1'),1),(rn('C1'),1),(rn('R2'),1))
    same((rn('R2'),2),(vref,7))
    same((vref,6),(rn('R3'),2),(rn('C3'),1))
    same((rn('C3'),2),(rn('R5'),1))
    same((rn('R5'),2),(rn('C4'),1),(rn('R6'),1),(rn('R7'),1),(rn('R8'),1))
    same((rn('R8'),2),(vref,2))
    same((vref,1),(rn('R9'),2),(rn('C7'),1))
    same((rn('C7'),2),(rn('R11'),1),(rn('R12'),1))
    same((rn('R12'),2),(cfref,G))
    same((cfref,K),(rn('R13'),1),(rn('C8'),1))
    same((rn('R13'),2),(rn('R14'),1),(rn('R11'),2))
    same((rn('C8'),2),(rn('R15'),1),(jout,1))
    same((rn('R1'),2),(jin,2),(rn('R4'),2),(rn('R14'),2),(rn('R15'),2),(jout,2),('C9',2))
    same((rn('R3'),1),(dropC[1],1),(dropR[1],2),(bleed[1],1))
    same((rn('R9'),1),(dropC[0],1),(dropR[0],2),(dropR[1],1),(bleed[0],1))
    same((cfref,A),('C10',1),(dropR[0],1))
    diff((vref,6),(vref,7)); diff((rn('C8'),1),(rn('C8'),2))

chan(lambda b: b, 'J1','J2','V1','V3',(6,7,8),('R18','R19'),('C12','C13'),('R26','R27'))
chan(lambda b: b[0]+str(int(b[1:])+100), 'J3','J4','V2','V3',(1,2,3),('R118','R119'),('C112','C113'),('R126','R127'))
diff(('R3',1),('R103',1)); diff(('R9',1),('R109',1)); diff(('J2',1),('J4',1))

# masa / PE
same(('C9',2),('C10',2),('C12',2),('C113',2),('R26',2),('R127',2),('R23',2),
     ('C17',2),('R24',2),('R25',1),('C18',1),('T1',4))
same(('J5',3),('R25',2),('C18',2))
diff(('J5',3),('C9',2))

# siec: J5->F1->SW1A->R34->T1.1 (+R32, cewka K1 przez L_SW/N_SW)
same(('J5',1),('F1',1))
same(('F1',2),('SW1',1))
same(('SW1',2),('R34',1))
same(('R34',2),('T1',1),('R32',1),('K1',1),('R33',1))
same(('J5',2),('SW1',3))
same(('SW1',4),('T1',2),('NE1',1),('K1',16),('C21',2))
same(('R32',2),('NE1',2))
same(('R33',2),('C21',1))
diff(('SW1',1),('SW1',2)); diff(('T1',1),('T1',2))

# prostownik EZ81 + LC
same(('T1',3),('V4',1))
same(('T1',5),('V4',7))
same(('V4',3),('C9',1),('L1',1),('V4',5),('T1',7))   # katoda + EZH_B (zarzenie dowiazane)
same(('T1',6),('V4',4))                               # EZH_A
same(('L1',2),('C10',1),('R18',1),('R118',1),('R22',1),('K1',11))  # B+3, NC rozladowania
same(('R22',2),('R23',1),('C17',1))
diff(('V4',1),('V4',7)); diff(('V4',3),('C9',2))

# rozladowanie przez NC (pole2)
same(('K1',13),('R24',1))
diff(('K1',13),('K1',11))

# bateria / straznik / woltomierz
same(('BT1',1),('F2',2))
same(('F2',1),('SW2',2))
same(('SW2',1),('K1',4))                              # BATT_SW -> COM straznika
same(('K1',8),('V1',4),('V1',5),('V2',4),('V2',5),('V3',4),('V3',5),('R30',1))  # HTR_A
same(('BT1',2),('SW2',5))
same(('SW2',4),('V1',9),('V2',9),('V3',9),('M1',1),('R22',2))  # HTR_B = ELEV
same(('R30',2),('M1',2))
same(('SW2',3),('J6',1))                              # CHG_P
same(('SW2',6),('J6',2))                              # CHG_N
diff(('SW2',1),('SW2',3)); diff(('SW2',4),('SW2',6))
diff(('BT1',1),('BT1',2)); diff(('K1',4),('K1',8))
diff(('K1',8),('SW2',4))                              # HTR_A != HTR_B
diff(('T1',6),('K1',8))                               # zarzenie EZ81 != zarzenie audio

print('Nets:', len(nets))
if fails:
    print('FAILURES:'); [print(' ', f) for f in fails]; sys.exit(1)
print('ALL CONNECTIVITY CHECKS PASSED')
