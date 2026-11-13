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
NAMED = {"white": "#ffffff", "black": "#000000", "red": "#ff0000", "green": "#008000", "blue": "#0000ff",
         "gray": "#808080", "grey": "#808080", "lightgray": "#d3d3d3", "lightgrey": "#d3d3d3", "darkgray": "#a9a9a9",
         "darkgrey": "#a9a9a9", "dimgray": "#696969", "dimgrey": "#696969", "silver": "#c0c0c0", "gainsboro": "#dcdcdc",
         "whitesmoke": "#f5f5f5", "ivory": "#fffff0", "beige": "#f5f5dc", "linen": "#faf0e6", "oldlace": "#fdf5e6",
         "cornsilk": "#fff8dc", "floralwhite": "#fffaf0", "navy": "#000080", "teal": "#008080", "maroon": "#800000",
         "olive": "#808000", "purple": "#800080", "orange": "#ffa500", "gold": "#ffd700", "yellow": "#ffff00",
         "tomato": "#ff6347", "crimson": "#dc143c", "darkgreen": "#006400", "forestgreen": "#228b22",
         "darkblue": "#00008b", "royalblue": "#4169e1", "steelblue": "#4682b4", "slategray": "#708090",
         "darkslategray": "#2f4f4f", "indigo": "#4b0082", "rebeccapurple": "#663399", "hotpink": "#ff69b4",
         "pink": "#ffc0cb", "coral": "#ff7f50", "salmon": "#fa8072", "khaki": "#f0e68c", "tan": "#d2b48c",
         "brown": "#a52a2a", "sienna": "#a0522d", "chocolate": "#d2691e", "aliceblue": "#f0f8ff",
         "ghostwhite": "#f8f8ff", "honeydew": "#f0fff0", "mintcream": "#f5fffa", "snow": "#fffafa", "seashell": "#fff5ee"}
HSL_RE = re.compile(r"hsla?\(\s*(-?[\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%(?:[\s,/]+([\d.]+%?))?\s*\)")


def _alpha(a):
    if a is None:
        return 1.0
    return float(a.rstrip("%")) / (100 if a.endswith("%") else 1)


def parse_colour(v):
    """(hex, None) for an opaque colour; (None, reason) when it is translucent or cannot be read."""
    if not v:
        return None, "empty"
    s = v.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3,8})", s)
    if m:
        if len(s) == 9 and int(s[7:9], 16) < 250:
            return None, "translucent"
        if len(s) == 5 and s[4] != "f":
            return None, "translucent"
        h = norm_hex(s)
        return (h, None) if h else (None, "unreadable")
    if s in NAMED:
        return NAMED[s], None
    if s in ("transparent", "currentcolor", "inherit", "initial", "unset"):
        return None, s
    m = RGB_RE.fullmatch(s)
    if m:
        if _alpha(m.group(4)) < 0.98:
            return None, "translucent"
        return to_hex(int(m.group(1)), int(m.group(2)), int(m.group(3))), None
    m = HSL_RE.fullmatch(s)
    if m:
        if _alpha(m.group(4)) < 0.98:
            return None, "translucent"
        r, g, b = colorsys.hls_to_rgb((float(m.group(1)) % 360) / 360, float(m.group(3)) / 100, float(m.group(2)) / 100)
        return to_hex(r * 255, g * 255, b * 255), None
    return None, "unreadable"


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


def _strip_comments(css):
    out, i, n, q = [], 0, len(css), None
    while i < n:
        c = css[i]
        if q:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(css[i + 1]); i += 2; continue
            if c == q:
                q = None
        elif c in "\"'":
            q = c; out.append(c)
        elif css.startswith("/*", i):
            j = css.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def _split_top(s, sep):
    """Split on sep outside quotes, parentheses and braces."""
    parts, buf, depth, q, i = [], [], 0, None, 0
    while i < len(s):
        c = s[i]
        if q:
            buf.append(c)
            if c == "\\" and i + 1 < len(s):
                buf.append(s[i + 1]); i += 2; continue
            if c == q:
                q = None
        elif c in "\"'":
            q = c; buf.append(c)
        elif c in "({":
            depth += 1; buf.append(c)
        elif c in ")}":
            depth -= 1; buf.append(c)
        elif c == sep and depth == 0:
            parts.append("".join(buf)); buf = []
        else:
            buf.append(c)
        i += 1
    parts.append("".join(buf))
    return parts


def _match_brace(css, i):
    """Index of the brace closing the one at i, skipping quotes."""
    depth, q, n = 0, None, len(css)
    while i < n:
        c = css[i]
        if q:
            if c == "\\":
                i += 2; continue
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n


def css_rules(css):
    """Flat list of (selector, {prop: value}, media) including rules inside @media / @supports blocks.
    Given a whole HTML page, it reads the <style> blocks only. Quotes, data: URLs and nested
    rules (&:hover {…}) are handled; @font-face, @keyframes and @import carry no rules."""
    if re.search(r"<style\b", css, re.I):
        css = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", css, re.S | re.I))
    css = _strip_comments(css)
    out = []

    def walk(text, media):
        i, n = 0, len(text)
        while i < n:
            j = i
            q = None
            while j < n:
                c = text[j]
                if q:
                    if c == q:
                        q = None
                elif c in "\"'":
                    q = c
                elif c in "{;}":
                    break
                j += 1
            if j >= n:
                return
            if text[j] in ";}":
                i = j + 1
                continue
            sel = text[i:j].strip()
            k = _match_brace(text, j)
            body = text[j + 1:k]
            if sel.startswith("@media") or sel.startswith("@supports") or sel.startswith("@layer") or sel.startswith("@container"):
                walk(body, (media + " " + sel).strip())
            elif sel.startswith("@"):
                pass
            else:
                props = {}
                for decl in _split_top(body, ";"):
                    if "{" in decl:
                        decl = decl[decl.rfind("}") + 1:] if "}" in decl else ""
                    if ":" in decl and "{" not in decl:
                        kk, v = decl.split(":", 1)
                        kk = kk.strip().lower()
                        if kk and not kk.startswith("&"):
                            props[kk] = v.strip()
                out.append((sel, props, media))
            i = k + 1
    walk(css, "")
    return out


def media_key(media):
    return re.sub(r"\s+", "", media or "").lower()


def is_dark_selector(sel):
    return bool(re.search(r"data-theme\s*=\s*[\"']?dark", sel or "", re.I)) or ".dark" in (sel or "")


def root_vars(css):
    """Custom properties set on :root / html with no media condition (the defaults every visitor gets)."""
    vals = {}
    for sel, props, media in css_rules(css):
        if media:
            continue
        sels = [s.strip() for s in sel.split(",")]
        if any(s in (":root", "html") for s in sels):
            for k, v in props.items():
                if k.startswith("--"):
                    vals[k] = v
    return vals


def resolve(value, vars_, depth=0):
    """Replace var(--x, fallback) with its value, innermost first, until nothing changes."""
    if value is None:
        return value
    pat = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)")

    def sub(m):
        name, fb = m.group(1), m.group(2)
        if name in vars_:
            return vars_[name]
        return (fb or "").strip()
    for _ in range(12):
        new = pat.sub(sub, value)
        if new == value:
            break
        value = new
    return value


def px(value, base=16.0, root=16.0):
    """'18px' -> 18, '1.125rem' -> 18 (root 16), 'clamp(1rem, 2vw, 1.5rem)' -> the minimum.
    root is the html font-size in px (62.5% makes 1rem = 10px)."""
    if value is None:
        return None
    v = value.strip().lower()
    m = re.match(r"(?:clamp|max)\(\s*([^,]+),", v)
    if m:
        v = m.group(1)
    m = re.match(r"min\(\s*([^,]+),", v)
    if m:
        v = m.group(1)
    m = re.match(r"^(-?[\d.]+)\s*(px|rem|em|pt|%)?$", v.strip())
    if not m:
        return None
    num, unit = float(m.group(1)), m.group(2) or "px"
    return {"px": num, "rem": num * root, "em": num * base, "pt": num * 4 / 3, "%": num / 100 * base}[unit]


def first_family(value):
    if not value:
        return None
    f = value.split(",")[0].strip().strip("'\"")
    return f or None


def shorthand_family(value):
    """The family list in a `font:` shorthand ('700 2rem/1.2 "Papyrus", serif' -> '"Papyrus", serif')."""
    m = re.search(r"(?:^|\s)[\d.]+(?:px|rem|em|pt|%)(?:\s*/\s*[\d.]+[a-z%]*)?\s+(.+)$", (value or "").strip())
    return m.group(1) if m else None


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


PS_SHRINK = (
    "Add-Type -AssemblyName System.Drawing; $i=[System.Drawing.Image]::FromFile($args[0]);"
    "$s=[Math]::Min(1.0, 240.0/[Math]::Max($i.Width,$i.Height));"
    "$b=New-Object System.Drawing.Bitmap $i, ([int]([Math]::Max(1,$i.Width*$s))), ([int]([Math]::Max(1,$i.Height*$s)));"
    "$b.Save($args[1], [System.Drawing.Imaging.ImageFormat]::Png); $b.Dispose(); $i.Dispose()")


def _downscaled_copy(path):
    """A small PNG copy of any screenshot (PNG, JPEG, large or retina), made by a tool the computer already has:
    sips on a Mac, PowerShell's System.Drawing on Windows, ImageMagick elsewhere when installed. None if none."""
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    if sys.platform == "darwin":
        cmds = [["sips", "-s", "format", "png", "-Z", "240", str(path), "--out", tmp]]
    elif sys.platform.startswith("win"):
        cmds = [["powershell", "-NoProfile", "-Command", "& {" + PS_SHRINK + "}", str(path), tmp]]
    else:
        cmds = [["magick", str(path), "-resize", "240x240", tmp], ["convert", str(path), "-resize", "240x240", tmp]]
    for cmd in cmds:
        try:
            subprocess.run(cmd, capture_output=True, timeout=60, check=True)
            if Path(tmp).stat().st_size > 0:
                return Path(tmp)
        except Exception:
            continue
    Path(tmp).unlink(missing_ok=True)
    return None


def dominant_colours(path, k=5):
    """Up to k dominant colours as hex, most common first. Small PNGs are read directly; anything else
    (a JPEG, a retina screenshot) is shrunk first with a tool the computer has. [] if neither works:
    the session then names the colours by eye (taste_vault.py react --colours)."""
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
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        emit({"ok": False, "error": f"{p.name} is not valid JSON: {e}"}, 1)


def read_text(path):
    """A page as text: UTF-8 (with or without a BOM), falling back to Windows-1252, never a traceback."""
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


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
