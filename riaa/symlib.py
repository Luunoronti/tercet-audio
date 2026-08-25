"""Extract KiCad symbol definitions + pin geometry from system libraries."""
import re, uuid, os

LIBDIR = "/usr/share/kicad/symbols"

def tokenize(text):
    return re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', text)

def parse(tokens, i=0):
    """Parse token list into nested lists starting at '(' at index i."""
    assert tokens[i] == '('
    out = []
    i += 1
    while tokens[i] != ')':
        if tokens[i] == '(':
            node, i = parse(tokens, i)
            out.append(node)
        else:
            out.append(tokens[i]); i += 1
    return out, i + 1

def unq(s):
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s

_lib_cache = {}
def load_lib(libname):
    if libname in _lib_cache: return _lib_cache[libname]
    with open(os.path.join(LIBDIR, libname + ".kicad_sym")) as f:
        text = f.read()
    tokens = tokenize(text)
    tree, _ = parse(tokens, 0)
    syms = {}
    for node in tree:
        if isinstance(node, list) and node and node[0] == 'symbol':
            syms[unq(node[1])] = node
    _lib_cache[libname] = syms
    return syms

def dump(node, indent=0):
    """Serialize parse tree back to s-expression text."""
    pad = '  ' * indent
    has_sub = any(isinstance(x, list) for x in node)
    if not has_sub:
        return pad + '(' + ' '.join(node) + ')'
    # keep short nodes inline, preserving element order
    if node[0] in ('at','xy','size','width','type','offset','font','justify',
                   'pts','stroke','fill','effects','color','diameter','name','number','length'):
        inner = ' '.join(dump(x, 0).strip() if isinstance(x, list) else x for x in node[1:])
        return pad + '(' + node[0] + ' ' + inner + ')'
    # multiline: leading atoms on head line, then items in original order
    i = 1
    head_atoms = [node[0]]
    while i < len(node) and not isinstance(node[i], list):
        head_atoms.append(node[i]); i += 1
    lines = [pad + '(' + ' '.join(head_atoms)]
    for x in node[i:]:
        if isinstance(x, list):
            lines.append(dump(x, indent + 1))
        else:
            lines.append('  ' * (indent + 1) + x)
    lines.append(pad + ')')
    return '\n'.join(lines)

def get_prop(sym, name):
    for n in sym:
        if isinstance(n, list) and n[0] == 'property' and unq(n[1]) == name:
            return n
    return None

def resolve(libname, symname):
    """Return a flattened copy (parse tree) of symbol, resolving 'extends'."""
    syms = load_lib(libname)
    sym = syms[symname]
    ext = None
    for n in sym:
        if isinstance(n, list) and n[0] == 'extends':
            ext = unq(n[1])
    if ext is None:
        return _deepcopy(sym)
    parent = resolve(libname, ext)
    # rename parent -> symname; override properties from child
    ren = _rename(parent, ext, symname)
    for n in sym:
        if isinstance(n, list) and n[0] == 'property':
            pname = unq(n[1])
            tgt = get_prop(ren, pname)
            if tgt:
                idx = ren.index(tgt)
                ren[idx] = _deepcopy(n)
            else:
                ren.append(_deepcopy(n))
    return ren

def _deepcopy(node):
    return [ _deepcopy(x) if isinstance(x, list) else x for x in node ]

def _rename(sym, old, new):
    sym = _deepcopy(sym)
    sym[1] = '"%s"' % new
    for n in sym:
        if isinstance(n, list) and n[0] == 'symbol':
            n[1] = '"%s"' % (new + unq(n[1])[len(old):])
    return sym

def clone_as(libname, srcname, newname, value=None, datasheet=None, desc=None):
    sym = resolve(libname, srcname)
    sym = _rename(sym, srcname, newname)
    if value:
        p = get_prop(sym, 'Value'); p[2] = '"%s"' % value
    if datasheet:
        p = get_prop(sym, 'Datasheet'); p[2] = '"%s"' % datasheet
    if desc:
        p = get_prop(sym, 'ki_description')
        if p: p[2] = '"%s"' % desc
    return sym

def embed_text(sym, libprefix):
    """Rename to 'Lib:Name' outer, keep inner unit names bare, return text."""
    sym = _deepcopy(sym)
    name = unq(sym[1])
    sym[1] = '"%s:%s"' % (libprefix, name)
    return dump(sym, 1)

def pins(sym):
    """Return {unit: [(number, x, y, angle, length, name)]}"""
    out = {}
    base = unq(sym[1])
    for n in sym:
        if isinstance(n, list) and n[0] == 'symbol':
            sub = unq(n[1])
            m = re.match(re.escape(base) + r'_(\d+)_(\d+)$', sub)
            if not m: continue
            unit = int(m.group(1))
            for p in n:
                if isinstance(p, list) and p[0] == 'pin':
                    at = next(x for x in p if isinstance(x, list) and x[0]=='at')
                    ln = next(x for x in p if isinstance(x, list) and x[0]=='length')
                    num = next(unq(x[1]) for x in p if isinstance(x, list) and x[0]=='number')
                    nam = next(unq(x[1]) for x in p if isinstance(x, list) and x[0]=='name')
                    out.setdefault(unit if unit>0 else 0, []).append(
                        (num, float(at[1]), float(at[2]), float(at[3]), float(ln[1]), nam))
    return out

if __name__ == '__main__':
    want = [('Device','R'),('Device','C'),('Device','C_Polarized'),('Device','D'),
            ('Device','Fuse'),('Device','Transformer_1P_2S'),
            ('Connector','Conn_Coaxial'),('Connector','Screw_Terminal_01x03'),
            ('Regulator_Linear','LM317_TO-220'),
            ('Valve','ECC83'),('Valve','ECC81'),
            ('power','GND'),('power','PWR_FLAG')]
    for lib, name in want:
        s = resolve(lib, name)
        print('===', lib, name)
        for unit, pl in sorted(pins(s).items()):
            for num,x,y,a,l,nm in pl:
                print('  unit %d pin %-3s %-6s at (%7.2f,%7.2f) ang %3d len %.2f' % (unit,num,nm,x,y,int(a),l))
