#!/usr/bin/env python3
"""Shared helpers for the Brand Kit scripts: color maths and WCAG contrast, reading logo and font files,
turning a TrueType font's letters into real vector outlines, and safe file writes.
Standard library only. Imported by brandkit.py and brandpages.py; not run directly.
"""
import base64, colorsys, json, os, re, struct, sys, tempfile, zlib
from pathlib import Path

COLOR_KEYS = ("bg", "surface", "ink", "muted", "accent", "accent_ink", "line")
VAR_OF = {k: "--c-" + k.replace("_", "-") for k in COLOR_KEYS}
LABELS = {"bg": "Page background", "surface": "Panels and cards", "ink": "Text", "muted": "Quiet text",
          "accent": "Accent (buttons, links)", "accent_ink": "Text on the accent", "line": "Lines and borders"}
AA_TEXT, AA_LARGE = 4.5, 3.0
PAIRS = [("ink", "bg", AA_TEXT), ("muted", "bg", AA_TEXT), ("ink", "surface", AA_TEXT),
         ("accent_ink", "accent", AA_TEXT), ("accent", "bg", AA_LARGE)]
MIN_BODY = {"50plus": 18, "general": 16}
# Fonts that arrive by default when nobody chooses. Fine when the member's own brand uses them; a tell in a new kit.
DEFAULT_FONTS = {"inter", "poppins", "montserrat", "roboto", "open sans", "space grotesk", "playfair display",
                 "instrument serif", "lato", "dm sans"}
SYSTEM_FONTS = {"arial", "helvetica", "georgia", "verdana", "times new roman", "calibri", "tahoma", "trebuchet ms",
                "courier new", "garamond", "palatino", "century gothic", "segoe ui", "helvetica neue"}


# ---------------------------------------------------------------- color
def norm_hex(h):
    if not isinstance(h, str):
        return None
    h = h.strip().lower()
    if not h.startswith("#"):
        h = "#" + h
    if not re.fullmatch(r"#[0-9a-f]{3}|#[0-9a-f]{6}", h):
        return None
    if len(h) == 4:
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def rgb(h):
    h = norm_hex(h)
    if not h:
        raise ValueError(f"not a hex color: {h!r}")
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def to_hex(r, g, b):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in (r, g, b))


def luminance(h):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return round((max(la, lb) + 0.05) / (min(la, lb) + 0.05), 2)


def hls(h):
    r, g, b = (v / 255 for v in rgb(h))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, ll, ss


def from_hls(hue, light, sat):
    r, g, b = colorsys.hls_to_rgb((hue % 360) / 360, max(0, min(1, light)), max(0, min(1, sat)))
    return to_hex(r * 255, g * 255, b * 255)


def mix(a, b, t):
    """a moved a fraction t of the way towards b."""
    ra, rb = rgb(a), rgb(b)
    return to_hex(*(x + (y - x) * t for x, y in zip(ra, rb)))


def is_dark(h):
    return luminance(h) < 0.18


def is_neutral(h):
    _, light, sat = hls(h)
    return sat < 0.16 or light > 0.95 or light < 0.08


def is_cream(h):
    hue, light, sat = hls(h)
    return 0.88 <= light < 0.985 and 0.2 <= sat <= 0.9 and 25 <= hue <= 60


def is_purple(h):
    hue, light, sat = hls(h)
    return 250 <= hue <= 300 and sat >= 0.35 and 0.25 <= light <= 0.8


def family(h):
    hue, light, sat = hls(h)
    if light >= 0.93:
        return "near-white" if sat < 0.25 or light > 0.97 else "warm off-white" if 20 <= hue <= 70 else "tinted white"
    if light <= 0.12:
        return "near-black"
    if sat < 0.12:
        return "gray"
    for edge, name in [(15, "red"), (40, "orange"), (65, "yellow"), (160, "green"), (200, "teal"), (250, "blue"),
                       (290, "purple"), (335, "pink"), (361, "red")]:
        if hue < edge:
            base = name
            break
    return ("deep " if light < 0.35 else "pale " if light > 0.75 else "muted " if sat < 0.35 else "") + base


def shade_to_contrast(fg, bg, target=AA_TEXT):
    """The nearest shade of fg that reaches target against bg: darker on a light ground, lighter on a dark one."""
    fg = norm_hex(fg)
    if contrast(fg, bg) >= target:
        return fg
    hue, light, sat = hls(fg)
    step = -0.01 if not is_dark(bg) else 0.01
    for _ in range(110):
        light = max(0.0, min(1.0, light + step))
        cand = from_hls(hue, light, sat)
        if contrast(cand, bg) >= target:
            return cand
    return "#000000" if step < 0 else "#ffffff"


def best_on(bg, *candidates):
    """The first candidate that reads on bg at 4.5:1 (the brand's own colors come first), else black or white."""
    for c in candidates:
        if norm_hex(c) and contrast(c, bg) >= AA_TEXT:
            return norm_hex(c)
    return max(["#ffffff", "#111111"], key=lambda c: contrast(c, bg))


def propose_roles(colors, dark=False):
    """Seven working roles from the brand's own colors. The brand colors stay exactly as given wherever they
    are used as fills; where one is too light or too dark to carry text, a text-safe shade is proposed beside it
    and listed in `changed`, so the member sees every color that is not literally theirs."""
    cols = [norm_hex(c) for c in colors if norm_hex(c)]
    if not cols:
        raise ValueError("no usable colors")
    vivid = sorted((c for c in cols if not is_neutral(c)), key=lambda c: -hls(c)[2] * (1 - abs(hls(c)[1] - 0.5)))
    darkest = min(cols, key=luminance)
    lightest = max(cols, key=luminance)
    primary = vivid[0] if vivid else darkest
    changed = {}
    if dark:
        bg = darkest if luminance(darkest) < 0.08 else mix(darkest, "#000000", 0.55)
        ink = lightest if luminance(lightest) > 0.7 else "#f5f5f2"
        surface = mix(bg, "#ffffff", 0.07)
        line = mix(bg, "#ffffff", 0.2)
    else:
        bg = lightest if luminance(lightest) > 0.85 and not is_cream(lightest) or (lightest in cols and luminance(lightest) > 0.85) else "#ffffff"
        ink = darkest if luminance(darkest) < 0.06 else mix(darkest, "#000000", 0.6) if luminance(darkest) < 0.3 else "#15171a"
        surface = mix(bg, primary, 0.05)
        line = mix(bg, ink, 0.16)
    if ink not in cols:
        changed["ink"] = f"a near-{'white' if dark else 'black'} for text" + (f", darkened from {darkest}" if not dark and darkest != ink and luminance(darkest) < 0.3 else "")
    if bg not in cols:
        changed["bg"] = "a plain ground; none of the brand colors is a page background"
    accent_pick = next((c for c in vivid if contrast(c, bg) >= AA_LARGE), None)
    if accent_pick:
        accent = accent_pick
        if accent != primary:
            changed["accent"] = (f"{primary} is too faint against this page to carry a button or a link, so {accent} does that job; "
                                 f"{primary} stays in the brand for highlights and large fills")
    else:
        accent = shade_to_contrast(primary, bg, AA_LARGE)
        if accent != primary:
            changed["accent"] = f"{primary} shaded to {accent} so buttons and links show against the page; {primary} stays the brand color for large fills"
    muted = shade_to_contrast(mix(ink, bg, 0.38), bg, AA_TEXT)
    acc_ink = best_on(accent, ink, bg)
    roles = {"bg": bg, "surface": surface, "ink": ink, "muted": muted, "accent": accent, "accent_ink": acc_ink, "line": line}
    for k in ("surface", "muted", "line"):
        changed.setdefault(k, "worked out from the brand colors")
    if acc_ink not in cols:
        changed.setdefault("accent_ink", "black or white, whichever reads on the accent")
    return roles, changed


def contrast_problems(col):
    out = []
    for fg, bg, need in PAIRS:
        r = contrast(col[fg], col[bg])
        if r < need:
            out.append((fg, bg, r, need, shade_to_contrast(col[fg], col[bg], need)))
    return out


# ---------------------------------------------------------------- images
def png_info(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 33:
        return None
    w, h, depth, ctype = struct.unpack(">IIBB", data[16:26])
    alpha = ctype in (4, 6) or b"tRNS" in data[:4096]
    return {"width": w, "height": h, "alpha": alpha, "depth": depth, "ctype": ctype}


def jpeg_size(data):
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        m = data[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return {"width": w, "height": h}
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def png_colors(data, k=6, max_pixels=4_000_000):
    """Dominant opaque colors of a PNG, most common first, with their share. [] when it cannot be read."""
    info = png_info(data)
    if not info or info["depth"] != 8 or info["ctype"] not in (0, 2, 3, 4, 6) or info["width"] * info["height"] > max_pixels:
        return []
    w, h, ctype = info["width"], info["height"], info["ctype"]
    pos, idat, plte, trns, inter = 8, [], None, None, 0
    while pos + 8 <= len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR":
            inter = chunk[12]
        elif typ == b"PLTE":
            plte = chunk
        elif typ == b"tRNS":
            trns = chunk
        elif typ == b"IDAT":
            idat.append(chunk)
        elif typ == b"IEND":
            break
    if inter:
        return []
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    try:
        raw = zlib.decompress(b"".join(idat))
    except zlib.error:
        return []
    stride = w * bpp
    prev = bytearray(stride)
    step = max(1, int((w * h / 60000) ** 0.5))
    buckets, p, total = {}, 0, 0
    for y in range(h):
        f = raw[p]
        line = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                line[i] = (line[i] + (((line[i - bpp] if i >= bpp else 0) + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        prev = line
        if y % step:
            continue
        for x in range(0, w, step):
            o = x * bpp
            if ctype == 2:
                px = (line[o], line[o + 1], line[o + 2])
            elif ctype == 6:
                if line[o + 3] < 200:
                    continue
                px = (line[o], line[o + 1], line[o + 2])
            elif ctype == 0:
                px = (line[o],) * 3
            elif ctype == 4:
                if line[o + 1] < 200:
                    continue
                px = (line[o],) * 3
            else:
                idx = line[o]
                if not plte or (trns and idx < len(trns) and trns[idx] < 200):
                    continue
                px = tuple(plte[idx * 3:idx * 3 + 3])
            e = buckets.setdefault((px[0] >> 3, px[1] >> 3, px[2] >> 3), [0, 0, 0, 0])
            e[0] += px[0]; e[1] += px[1]; e[2] += px[2]; e[3] += 1
            total += 1
    out = []
    for r, g, b, c in sorted(buckets.values(), key=lambda e: -e[3]):
        hx = to_hex(r / c, g / c, b / c)
        if c / max(1, total) < 0.01:
            break
        if all(sum((x - y) ** 2 for x, y in zip(rgb(hx), rgb(o["hex"]))) ** 0.5 > 36 for o in out):
            out.append({"hex": hx, "share": round(c / total, 3), "family": family(hx)})
        if len(out) >= k:
            break
    return out


COLOR_IN_TEXT = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}[^)]*\)")


def text_colors(text, k=10):
    """Colors named in SVG, CSS or HTML source, most used first."""
    counts = {}
    for m in COLOR_IN_TEXT.findall(text):
        if m.startswith("#"):
            h = norm_hex(m)
        else:
            n = [int(x) for x in re.findall(r"\d{1,3}", m)[:3]]
            h = to_hex(*n)
        if h:
            counts[h] = counts.get(h, 0) + 1
    return [{"hex": h, "uses": c, "family": family(h)} for h, c in sorted(counts.items(), key=lambda kv: -kv[1])[:k]]


def text_fonts(text):
    fams = {}
    for m in re.findall(r"font-family\s*[:=]\s*[\"']?([^;\"'}<>]+)", text):
        first = m.split(",")[0].strip().strip("'\"")
        if first and first.lower() not in ("inherit", "serif", "sans-serif", "monospace", "system-ui") and not first.startswith("var("):
            fams[first] = fams.get(first, 0) + 1
    for m in re.findall(r"fonts\.googleapis\.com/css2?\?([^\"'>\s]+)", text):
        for fam in re.findall(r"family=([^:&]+)", m):
            name = fam.replace("+", " ").replace("%20", " ")
            fams[name] = fams.get(name, 0) + 1
    return [f for f, _ in sorted(fams.items(), key=lambda kv: -kv[1])]


# ---------------------------------------------------------------- TrueType: names, widths and outlines
class Font:
    """Just enough of a TrueType reader to set a name in real vector outlines: the family name, the letter-to-glyph
    map, advance widths and the glyph contours. Raises ValueError for anything it cannot read (a .woff2, an
    OpenType/CFF .otf, a font collection): the caller then falls back to live text."""

    def __init__(self, path):
        self.file = Path(path)
        d = self.data = self.file.read_bytes()
        if d[:4] not in (b"\x00\x01\x00\x00", b"true"):
            raise ValueError("not a TrueType (.ttf) file with glyph outlines")
        n = struct.unpack(">H", d[4:6])[0]
        self.t = {}
        for i in range(n):
            tag, _cs, off, ln = struct.unpack(">4sIII", d[12 + 16 * i:28 + 16 * i])
            self.t[tag.decode("latin-1")] = (off, ln)
        for need in ("head", "hhea", "hmtx", "maxp", "cmap", "loca", "glyf"):
            if need not in self.t:
                raise ValueError(f"the font has no {need} table")
        ho = self.t["head"][0]
        self.upm = struct.unpack(">H", d[ho + 18:ho + 20])[0]
        self.loca_long = struct.unpack(">h", d[ho + 50:ho + 52])[0] == 1
        hh = self.t["hhea"][0]
        self.ascent, self.descent = struct.unpack(">hh", d[hh + 4:hh + 8])
        self.n_hm = struct.unpack(">H", d[hh + 34:hh + 36])[0]
        self.n_glyphs = struct.unpack(">H", d[self.t["maxp"][0] + 4:self.t["maxp"][0] + 6])[0]
        self.cmap = self._cmap()
        self.cap = self._metric(88) or int(self.upm * 0.7)
        self.xh = self._metric(86) or int(self.upm * 0.5)

    def _metric(self, off):
        """sxHeight (byte 86) or sCapHeight (byte 88) from the OS/2 table, version 2 and later."""
        if "OS/2" not in self.t or self.t["OS/2"][1] < off + 2:
            return None
        o = self.t["OS/2"][0]
        if struct.unpack(">H", self.data[o:o + 2])[0] < 2:
            return None
        v = struct.unpack(">h", self.data[o + off:o + off + 2])[0]
        return v if v > 0 else None

    def _cmap(self):
        d, base = self.data, self.t["cmap"][0]
        n = struct.unpack(">H", d[base + 2:base + 4])[0]
        best, rank = None, -1
        for i in range(n):
            pid, eid, off = struct.unpack(">HHI", d[base + 4 + 8 * i:base + 12 + 8 * i])
            fmt = struct.unpack(">H", d[base + off:base + off + 2])[0]
            r = {(3, 10, 12): 4, (0, 4, 12): 4, (0, 6, 12): 4, (3, 1, 4): 3, (0, 3, 4): 3}.get((pid, eid, fmt), 1 if fmt in (4, 12) else -1)
            if r > rank:
                best, rank = (base + off, fmt), r
        if not best:
            raise ValueError("the font has no usable letter map")
        o, fmt = best
        m = {}
        if fmt == 12:
            ng = struct.unpack(">I", d[o + 12:o + 16])[0]
            for i in range(ng):
                s, e, g = struct.unpack(">III", d[o + 16 + 12 * i:o + 28 + 12 * i])
                if e - s > 70000:
                    continue
                for c in range(s, e + 1):
                    m[c] = g + c - s
        else:
            seg = struct.unpack(">H", d[o + 6:o + 8])[0] // 2
            ends = struct.unpack(f">{seg}H", d[o + 14:o + 14 + 2 * seg])
            p = o + 16 + 2 * seg
            starts = struct.unpack(f">{seg}H", d[p:p + 2 * seg])
            deltas = struct.unpack(f">{seg}h", d[p + 2 * seg:p + 4 * seg])
            ro = p + 4 * seg
            ranges = struct.unpack(f">{seg}H", d[ro:ro + 2 * seg])
            for i in range(seg):
                for c in range(starts[i], ends[i] + 1):
                    if c == 0xFFFF:
                        continue
                    if ranges[i] == 0:
                        g = (c + deltas[i]) & 0xFFFF
                    else:
                        q = ro + 2 * i + ranges[i] + 2 * (c - starts[i])
                        g = struct.unpack(">H", d[q:q + 2])[0]
                        if g:
                            g = (g + deltas[i]) & 0xFFFF
                    if g:
                        m[c] = g
        return m

    def name(self):
        if "name" not in self.t:
            return None
        d, o = self.data, self.t["name"][0]
        count, so = struct.unpack(">HH", d[o + 2:o + 6])
        got = {}
        for i in range(count):
            pid, eid, _lid, nid, ln, off = struct.unpack(">6H", d[o + 6 + 12 * i:o + 18 + 12 * i])
            if nid not in (1, 16):
                continue
            raw = d[o + so + off:o + so + off + ln]
            try:
                s = raw.decode("utf-16-be") if pid in (0, 3) else raw.decode("mac-roman")
            except UnicodeDecodeError:
                continue
            got.setdefault(nid, s.strip())
        return got.get(16) or got.get(1)

    def advance(self, gid):
        o = self.t["hmtx"][0]
        i = min(gid, self.n_hm - 1)
        return struct.unpack(">H", self.data[o + 4 * i:o + 4 * i + 2])[0]

    def _glyph_range(self, gid):
        o = self.t["loca"][0]
        if self.loca_long:
            a, b = struct.unpack(">II", self.data[o + 4 * gid:o + 4 * gid + 8])
        else:
            a, b = (2 * v for v in struct.unpack(">HH", self.data[o + 2 * gid:o + 2 * gid + 4]))
        return self.t["glyf"][0] + a, b - a

    def contours(self, gid, depth=0):
        """A glyph as a list of contours, each a list of (x, y, on_curve) in font units."""
        if gid >= self.n_glyphs or depth > 6:
            return []
        o, ln = self._glyph_range(gid)
        if ln <= 0:
            return []
        d = self.data
        nc = struct.unpack(">h", d[o:o + 2])[0]
        p = o + 10
        if nc >= 0:
            ends = struct.unpack(f">{nc}H", d[p:p + 2 * nc]) if nc else ()
            p += 2 * nc
            p += 2 + struct.unpack(">H", d[p:p + 2])[0]
            npts = ends[-1] + 1 if ends else 0
            flags = []
            while len(flags) < npts:
                f = d[p]; p += 1
                flags.append(f)
                if f & 8:
                    r = d[p]; p += 1
                    flags.extend([f] * r)
            flags = flags[:npts]

            def coords(short, same):
                nonlocal p
                v, out = 0, []
                for f in flags:
                    if f & short:
                        dv = d[p]; p += 1
                        v += dv if f & same else -dv
                    elif not f & same:
                        v += struct.unpack(">h", d[p:p + 2])[0]; p += 2
                    out.append(v)
                return out
            xs = coords(2, 16)
            ys = coords(4, 32)
            out, start = [], 0
            for e in ends:
                out.append([(xs[i], ys[i], bool(flags[i] & 1)) for i in range(start, e + 1)])
                start = e + 1
            return out
        out = []
        while True:
            fl, g = struct.unpack(">HH", d[p:p + 4]); p += 4
            if fl & 1:
                a1, a2 = struct.unpack(">hh", d[p:p + 4]); p += 4
            else:
                a1, a2 = struct.unpack(">bb", d[p:p + 2]); p += 2
            a, b, c, dd = 1.0, 0.0, 0.0, 1.0
            if fl & 8:
                a = dd = struct.unpack(">h", d[p:p + 2])[0] / 16384; p += 2
            elif fl & 0x40:
                a, dd = (v / 16384 for v in struct.unpack(">hh", d[p:p + 4])); p += 4
            elif fl & 0x80:
                a, b, c, dd = (v / 16384 for v in struct.unpack(">hhhh", d[p:p + 8])); p += 8
            dx, dy = (a1, a2) if fl & 2 else (0, 0)
            for con in self.contours(g, depth + 1):
                out.append([(a * x + c * y + dx, b * x + dd * y + dy, on) for x, y, on in con])
            if not fl & 0x20:
                break
        return out

    def has(self, ch):
        return ord(ch) in self.cmap

    def path(self, text, size, x0=0.0, baseline=0.0, tracking=0.0, kern=None):
        """(svg path data, advance width, (min x, min y, max x, max y)) for text set at `size` px with its
        baseline at y=baseline. tracking is in em; kern maps a pair of letters ("AV") to an adjustment in em."""
        s = size / self.upm
        x, parts, kern = x0, [], kern or {}
        box = [1e9, 1e9, -1e9, -1e9]
        for i, ch in enumerate(text):
            gid = self.cmap.get(ord(ch), 0)
            for con in self.contours(gid):
                pts = [(x + px * s, baseline - py * s, on) for px, py, on in con]
                for px, py, _ in pts:
                    box = [min(box[0], px), min(box[1], py), max(box[2], px), max(box[3], py)]
                parts.append(_contour_path(pts))
            x += self.advance(gid) * s
            if i < len(text) - 1:
                x += (tracking + float(kern.get(ch + text[i + 1], 0))) * size
        if box[0] > box[2]:
            box = [x0, baseline, x, baseline]
        return "".join(parts), x - x0, tuple(box)


def _contour_path(pts):
    if not pts:
        return ""
    if not any(p[2] for p in pts):                     # all off-curve: start from the midpoint of the last and first
        a, b = pts[-1], pts[0]
        pts = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, True)] + pts
    else:
        while not pts[0][2]:
            pts = pts[1:] + pts[:1]
    f = lambda v: ("%.2f" % v).rstrip("0").rstrip(".")
    out = [f"M{f(pts[0][0])} {f(pts[0][1])}"]
    n, i = len(pts), 1
    while i <= n:
        p = pts[i % n]
        if p[2]:
            out.append(f"L{f(p[0])} {f(p[1])}")
            i += 1
        else:
            nx = pts[(i + 1) % n]
            end = (nx[0], nx[1]) if nx[2] else ((p[0] + nx[0]) / 2, (p[1] + nx[1]) / 2)
            out.append(f"Q{f(p[0])} {f(p[1])} {f(end[0])} {f(end[1])}")
            i += 2 if nx[2] else 1
    return "".join(out) + "Z"


def open_font(path):
    try:
        return Font(path)
    except (OSError, ValueError, struct.error, IndexError):
        return None


def data_uri(path):
    p = Path(path)
    mime = {".ttf": "font/ttf", ".otf": "font/otf", ".woff2": "font/woff2", ".woff": "font/woff", ".svg": "image/svg+xml",
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(p.suffix.lower(), "application/octet-stream")
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")


# ---------------------------------------------------------------- files
def read_json(path):
    p = Path(path)
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except OSError as e:
        sys.exit(f"Cannot read {p}: {e}")
    except ValueError as e:
        sys.exit(f"{p.name} is not valid JSON: {e}")


def write_atomic(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".tmp-", suffix=p.suffix)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, p)


def write_json(path, data):
    write_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def esc(s):
    return str(s if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def rel(target, start):
    """target as a path relative to the folder `start`, with forward slashes."""
    return os.path.relpath(Path(target).resolve(), Path(start).resolve()).replace(os.sep, "/")
