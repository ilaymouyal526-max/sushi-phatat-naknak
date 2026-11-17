"""Minimal HEIC -> JPEG: extracts the thumbnail (or the tiled primary image) HEVC
items from the ISOBMFF container and decodes them with ffmpeg.
usage: python3 -I heic2jpg.py in.heic out.jpg
"""
import struct, subprocess, sys, os, tempfile

def boxes(buf, off, end):
    while off + 8 <= end:
        size, typ = struct.unpack('>I4s', buf[off:off+8]); hdr = 8
        if size == 1: size = struct.unpack('>Q', buf[off+8:off+16])[0]; hdr = 16
        elif size == 0: size = end - off
        yield typ.decode('latin1'), off + hdr, off + size
        off += size

def find(buf, off, end, path):
    for t, s, e in boxes(buf, off, end):
        if t == path[0]:
            if len(path) == 1: return s, e
            # full boxes with version/flags before children
            skip = 4 if t in ('meta',) else 0
            return find(buf, s + skip, e, path[1:])
    return None

def main(src, dst):
    b = open(src, 'rb').read()
    ms, me = find(b, 0, len(b), ['meta'])
    ms += 4
    # pitm
    ps, pe = find(b, ms, me, ['pitm'])
    ver = b[ps]; primary = struct.unpack('>H' if ver == 0 else '>I', b[ps+4:ps+6 if ver == 0 else ps+8])[0]
    # iinf: item types
    is_, ie = find(b, ms, me, ['iinf'])
    ver = b[is_]; p = is_ + 4; p += 2 if ver == 0 else 4
    types = {}
    for t, s, e in boxes(b, p, ie):
        if t != 'infe': continue
        v = b[s]; q = s + 4
        if v >= 2:
            iid = struct.unpack('>H' if v == 2 else '>I', b[q:q+(2 if v == 2 else 4)])[0]; q += 2 if v == 2 else 4
            q += 2
            types[iid] = b[q:q+4].decode('latin1')
    # iloc
    ls, le = find(b, ms, me, ['iloc'])
    ver = b[ls]; p = ls + 4
    o_sz = b[p] >> 4; l_sz = b[p] & 15; bo_sz = b[p+1] >> 4; ix_sz = (b[p+1] & 15) if ver in (1, 2) else 0; p += 2
    def rd(n):
        nonlocal p
        if n == 0: return 0
        v = int.from_bytes(b[p:p+n], 'big'); p += n; return v
    cnt = rd(2 if ver < 2 else 4)
    loc = {}
    for _ in range(cnt):
        iid = rd(2 if ver < 2 else 4)
        if ver in (1, 2): rd(2)
        rd(2); base = rd(bo_sz); ext = rd(2); data = b''
        for _ in range(ext):
            if ver in (1, 2) and ix_sz: rd(ix_sz)
            o = rd(o_sz); l = rd(l_sz); data += b[base+o:base+o+l]
        loc[iid] = data
    # iprp: ipco properties + ipma associations
    cs, ce = find(b, ms, me, ['iprp', 'ipco'])
    props = list(boxes(b, cs, ce))
    as_, ae = find(b, ms, me, ['iprp', 'ipma'])
    ver = b[as_]; flags = int.from_bytes(b[as_+1:as_+4], 'big'); p = as_ + 4
    n = struct.unpack('>I', b[p:p+4])[0]; p += 4
    assoc = {}
    for _ in range(n):
        if ver < 1: iid = struct.unpack('>H', b[p:p+2])[0]; p += 2
        else: iid = struct.unpack('>I', b[p:p+4])[0]; p += 4
        k = b[p]; p += 1; lst = []
        for _ in range(k):
            if flags & 1: v = struct.unpack('>H', b[p:p+2])[0] & 0x7fff; p += 2
            else: v = b[p] & 0x7f; p += 1
            lst.append(v)
        assoc[iid] = lst
    # iref thmb: find thumbnail of primary
    thumb = None
    r = find(b, ms, me, ['iref'])
    dimg = []
    if r:
        rs, re_ = r; rv = b[rs]
        for t, s, e in boxes(b, rs + 4, re_):
            w = 2 if rv == 0 else 4
            frm = int.from_bytes(b[s:s+w], 'big'); c = int.from_bytes(b[s+w:s+w+2], 'big')
            tos = [int.from_bytes(b[s+w+2+i*w:s+w+2+(i+1)*w], 'big') for i in range(c)]
            if t == 'thmb' and primary in tos: thumb = frm
            if t == 'dimg' and frm == primary: dimg = tos
    def hevc_annexb(iid):
        out = b''
        for pi in assoc.get(iid, []):
            t, s, e = props[pi - 1]
            if t == 'hvcC':
                q = s + 22; na = b[q]; q += 1
                for _ in range(na):
                    q += 1; nn = struct.unpack('>H', b[q:q+2])[0]; q += 2
                    for _ in range(nn):
                        l = struct.unpack('>H', b[q:q+2])[0]; q += 2
                        out += b'\0\0\0\1' + b[q:q+l]; q += l
        d = loc[iid]; q = 0
        while q + 4 <= len(d):
            l = struct.unpack('>I', d[q:q+4])[0]; out += b'\0\0\0\1' + d[q+4:q+4+l]; q += 4 + l
        return out
    def irot(iid):
        for pi in assoc.get(iid, []):
            t, s, e = props[pi - 1]
            if t == 'irot': return b[s] & 3
        return 0
    def decode(iid, path):
        with tempfile.NamedTemporaryFile(suffix='.hevc', delete=False) as f:
            f.write(hevc_annexb(iid)); hp = f.name
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', hp, '-frames:v', '1', path], check=True)
        os.unlink(hp)
    rot = irot(primary)
    tmp = dst + '.raw.png'
    if types.get(primary) == 'hvc1':
        decode(primary, tmp)
    elif thumb is not None:
        decode(thumb, tmp)
    else:
        # grid: decode tiles and stitch
        g = loc[primary]; cols = g[3] + 1; rows = g[2] + 1
        tiles = []
        for i, t in enumerate(dimg):
            tp = f'{dst}.t{i}.png'; decode(t, tp); tiles.append(tp)
        subprocess.run(['montage', *tiles, '-tile', f'{cols}x{rows}', '-geometry', '+0+0', tmp], check=True)
        for t in tiles: os.unlink(t)
    rotate = {0: [], 1: ['-rotate', '-90'], 2: ['-rotate', '180'], 3: ['-rotate', '90']}[rot]
    subprocess.run(['convert', tmp, *rotate, '-resize', '640x640>', '-quality', '82', dst], check=True)
    os.unlink(tmp)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
