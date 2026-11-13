#!/usr/bin/env python3
"""Shared helpers for the Website Design Studio scripts: colour maths, WCAG contrast,
the page token contract, a small CSS reader, a PNG reader for dominant colours, and
safe file writes. Standard library only. Imported by the other scripts; not run directly.
"""
import colorsys, json, os, re, struct, subprocess, sys, tempfile, zlib
from pathlib import Path

# ---------------------------------------------------------------- the page token contract
# Every page the skill writes uses these CSS custom properties on :root, so one tweak bar
# and one lock step work on any direction. design-principles.md and tweak-bar.md list them.
COLOR_KEYS = ("bg", "surface", "ink", "muted", "accent", "accent_ink", "line")
VAR_OF = {k: "--c-" + k.replace("_", "-") for k in COLOR_KEYS}
SCALAR_VARS = {
    "--font-head": "font head", "--font-body": "font body", "--w-head": "heading weight",
    "--size-base": "body size (px)", "--scale": "type scale", "--measure": "line length (ch)",
    "--leading": "line height", "--space": "spacing unit (px)", "--radius": "corner radius (px)",
    "--shadow": "shadow", "--motion": "motion multiplier",
}
ATTRS = {
    "data-eyebrows": ("off", "on"), "data-head-italic": ("off", "on"),
    "data-buttons": ("solid", "outline", "pill"), "data-photo": ("natural", "warm", "mono", "rounded"),
    "data-hero": ("split", "stacked", "full-photo"), "data-texture": ("none", "paper", "grain"),
    "data-density": ("airy", "regular", "compact"), "data-theme": ("light", "dark"),
}

MIN_BODY_PX = 16
MIN_BODY_PX_50PLUS = 18
AA_TEXT = 4.5
AA_LARGE = 3.0


# ---------------------------------------------------------------- colour
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
RGB_RE = re.compile(r"rgba?\(\s*(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})(?:[\s,/]+([\d.]+%?))?\s*\)")
NAMED = {"white": "#ffffff", "black": "#000000"}


def norm_hex(h):
    """'#abc' -> '#aabbcc'; '#aabbccdd' -> '#aabbcc' (alpha dropped). None if not a colour."""
    if not isinstance(h, str):
        return None
    h = h.strip().lower()
    h = NAMED.get(h, h)
    if not re.fullmatch(r"#[0-9a-f]{3,8}", h) or len(h) not in (4, 5, 7, 9):
        return None
    if len(h) in (4, 5):
        h = "#" + "".join(c * 2 for c in h[1:4])
    return h[:7]


def rgb(h):
    h = norm_hex(h)
    if not h:
        raise ValueError(f"not a hex colour: {h!r}")
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
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def hls(h):
    r, g, b = (v / 255 for v in rgb(h))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, ll, ss


def is_cream(h):
    """The default 2026 'warm paper' background: very light, warm hue, a little saturation."""
    try:
        hue, light, sat = hls(h)
    except ValueError:
        return False
    return 0.88 <= light < 0.985 and 0.2 <= sat <= 0.9 and 25 <= hue <= 60


def is_purple(h):
    try:
        hue, light, sat = hls(h)
    except ValueError:
        return False
    return 250 <= hue <= 300 and sat >= 0.35 and 0.25 <= light <= 0.8


def shade_to_contrast(fg, bg, target=AA_TEXT):
    """Darken (or lighten, on a dark bg) fg in small steps until it reaches target against bg."""
    fg = norm_hex(fg)
    if contrast(fg, bg) >= target:
        return fg
    hue, light, sat = hls(fg)
    step = -0.02 if luminance(bg) > 0.18 else 0.02
    for _ in range(60):
        light = max(0.0, min(1.0, light + step))
        r, g, b = colorsys.hls_to_rgb(hue / 360, light, sat)
        cand = to_hex(r * 255, g * 255, b * 255)
        if contrast(cand, bg) >= target:
            return cand
    return "#000000" if step < 0 else "#ffffff"


def family(h):
    """A plain-words colour name for the taste read."""
    try:
        hue, light, sat = hls(h)
    except ValueError:
        return "unknown"
    if light >= 0.93:
        return "near-white" if sat < 0.25 or light > 0.97 else "warm off-white" if 20 <= hue <= 70 else "tinted white"
    if light <= 0.12:
        return "near-black"
    if sat < 0.12:
        return "grey"
    names = [(15, "red"), (40, "orange"), (65, "yellow"), (160, "green"), (200, "teal"), (250, "blue"),
             (290, "purple"), (335, "pink"), (361, "red")]
    for edge, name in names:
        if hue < edge:
            base = name
            break
    if light < 0.35:
        return "deep " + base
    if light > 0.75:
        return "pale " + base
    if sat < 0.35:
        return "muted " + base
    return base


# ---------------------------------------------------------------- CSS
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)


def css_rules(css):
    """Flat list of (selector, {prop: value}, media) including rules inside @media blocks.
    Given a whole HTML page, it reads the <style> blocks only."""
    if re.search(r"<style\b", css, re.I):
        css = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", css, re.S | re.I))
    css = COMMENT_RE.sub("", css)
    out = []
    i, n = 0, len(css)
    stack_prefix = []
    buf = ""
    while i < n:
        c = css[i]
        if c == "{":
            sel = buf.strip()
            buf = ""
            if sel.startswith("@"):
                stack_prefix.append(sel)
                i += 1
                continue
            j = css.find("}", i)
            if j < 0:
                break
            body = css[i + 1:j]
            props = {}
            for decl in body.split(";"):
                if ":" in decl:
                    k, v = decl.split(":", 1)
                    props[k.strip().lower()] = v.strip()
            media = " ".join(stack_prefix)
            out.append((sel, props, media))
            i = j + 1
            continue
        if c == "}":
            if stack_prefix:
                stack_prefix.pop()
            buf = ""
            i += 1
            continue
        buf += c
        i += 1
    return out


def root_vars(css):
    """Custom properties set on :root / html outside dark-mode and print blocks (the light defaults)."""
    vals = {}
    for sel, props, media in css_rules(css):
        if "prefers-color-scheme: dark" in media.replace(" :", ":") or "print" in media:
            continue
        sels = [s.strip() for s in sel.split(",")]
        if any(s in (":root", "html") for s in sels):
            for k, v in props.items():
                if k.startswith("--"):
                    vals[k] = v
    return vals


def resolve(value, vars_, depth=0):
    if depth > 8 or value is None:
        return value

    def sub(m):
        name, fb = m.group(1), m.group(2)
        if name in vars_:
            return resolve(vars_[name], vars_, depth + 1)
        return (fb or "").strip()
    return re.sub(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)", sub, value)


def px(value, base=16.0):
    """'18px' -> 18, '1.125rem' -> 18 (base 16), 'clamp(1rem, 2vw, 1.5rem)' -> the minimum."""
    if value is None:
        return None
    v = value.strip().lower()
    m = re.match(r"(?:clamp|max)\(\s*([^,]+),", v)
    if m:
        v = m.group(1)
    m = re.match(r"min\(\s*([^,]+),", v)
    if m:
        v = m.group(1)
    m = re.match(r"^(-?[\d.]+)\s*(px|rem|em|pt|%)?$", v)
    if not m:
        return None
    num, unit = float(m.group(1)), m.group(2) or "px"
    return {"px": num, "rem": num * 16, "em": num * base, "pt": num * 4 / 3, "%": num / 100 * base}[unit]


def first_family(value):
    if not value:
        return None
    f = value.split(",")[0].strip().strip("'\"")
    return f or None


GENERIC_FAMILIES = {"serif", "sans-serif", "monospace", "system-ui", "cursive", "fantasy", "ui-sans-serif",
                    "ui-serif", "ui-monospace", "inherit", "initial", "unset", "-apple-system", "blinkmacsystemfont"}


# ---------------------------------------------------------------- PNG (dominant colours)
def _png_pixels(data, max_pixels=1_500_000):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos, idat, plte, trns = 8, [], None, None
    w = h = depth = ctype = inter = None
    while pos + 8 <= len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR":
            w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", chunk)
        elif typ == b"PLTE":
            plte = chunk
        elif typ == b"tRNS":
            trns = chunk
        elif typ == b"IDAT":
            idat.append(chunk)
        elif typ == b"IEND":
            break
    if w is None or depth != 8 or inter or ctype not in (0, 2, 3, 4, 6) or w * h > max_pixels:
        return None
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(b"".join(idat))
    stride = w * bpp
    prev = bytearray(stride)
    rows = []
    p = 0
    for _ in range(h):
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
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
                line[i] = (line[i] + pr) & 255
        rows.append(line)
        prev = line
    px_ = []
    step = max(1, int((w * h / 40000) ** 0.5))
    for y in range(0, h, step):
        line = rows[y]
        for x in range(0, w, step):
            o = x * bpp
            if ctype == 2:
                px_.append((line[o], line[o + 1], line[o + 2]))
            elif ctype == 6:
                if line[o + 3] > 127:
                    px_.append((line[o], line[o + 1], line[o + 2]))
            elif ctype == 0:
                px_.append((line[o],) * 3)
            elif ctype == 4:
                if line[o + 1] > 127:
                    px_.append((line[o],) * 3)
            elif ctype == 3 and plte:
                k = line[o]
                if trns and k < len(trns) and trns[k] <= 127:
                    continue
                px_.append(tuple(plte[k * 3:k * 3 + 3]))
    return px_


def _downscaled_copy(path):
    """On a Mac, sips makes a small PNG copy fast; elsewhere return None."""
    if sys.platform != "darwin":
        return None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        subprocess.run(["sips", "-s", "format", "png", "-Z", "240", str(path), "--out", tmp],
                       capture_output=True, timeout=30, check=True)
        return Path(tmp)
    except Exception:
        return None


def dominant_colours(path, k=5):
    """Up to k dominant colours of a PNG as hex, most common first. [] if it cannot be read here
    (a JPEG, a very large file on a non-Mac computer): the session then names colours by eye."""
    path = Path(path)
    pixels = None
    try:
        data = path.read_bytes()
        pixels = _png_pixels(data)
    except Exception:
        pixels = None
    if pixels is None:
        small = _downscaled_copy(path)
        if small:
            try:
                pixels = _png_pixels(small.read_bytes())
            except Exception:
                pixels = None
            finally:
                small.unlink(missing_ok=True)
    if not pixels:
        return []
    buckets = {}
    for r, g, b in pixels:
        key = (r >> 4, g >> 4, b >> 4)
        e = buckets.setdefault(key, [0, 0, 0, 0])
        e[0] += r; e[1] += g; e[2] += b; e[3] += 1
    ranked = sorted(buckets.values(), key=lambda e: -e[3])
    out = []
    for r, g, b, c in ranked:
        h = to_hex(r / c, g / c, b / c)
        if all(_dist(h, o) > 40 for o in out):
            out.append(h)
        if len(out) >= k:
            break
    return out


def _dist(a, b):
    ra, rb = rgb(a), rgb(b)
    return sum((x - y) ** 2 for x, y in zip(ra, rb)) ** 0.5


# ---------------------------------------------------------------- files
def read_json(path, default=None):
    p = Path(path)
    if not p.exists():
        if default is not None:
            return default
        raise FileNotFoundError(str(p))
    return json.loads(p.read_text(encoding="utf-8"))


def write_atomic(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".tmp-", suffix=p.suffix)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, p)


def write_json(path, data):
    write_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def emit(obj, code=0):
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    sys.exit(code)


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "untitled"
