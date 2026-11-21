#!/usr/bin/env python3
"""Brand Kit: take in the brand a member already has, or build one with them, check it, and lock it so every
other Build Room session uses the same logo, colors and typefaces.

  brandkit.py read FILE [FILE ...]                 what is in the files a member handed over: logo size and colors,
                                                   the colors and fonts a saved web page or stylesheet uses, a font's name
  brandkit.py roles HEX [HEX ...] [--dark]         seven working colors proposed from the brand's own colors
  brandkit.py fonts KIT.json                       download the kit's Google Fonts into fonts/ beside the kit (goes online)
  brandkit.py check KIT.json                       everything that stops a lock (FIX) and everything worth a look (LOOK)
  brandkit.py board DIRECTIONS.json OUT.html       two to four candidate brands, each shown in use, on one page
  brandkit.py lock  KIT.json --out Design/System   writes the Design System, the logo files and the brand sheet
  brandkit.py section --system Design/System       the Business File lines for section 22 and section 18
  brandkit.py show  --system Design/System

Only `fonts` goes online, and only to Google Fonts. Nothing is sent anywhere. Paths inside a kit are relative to the kit file.
Standard library only.
"""
import argparse, json, re, shutil, sys, urllib.error, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import brandlib as bl  # noqa: E402
import brandpages as bp  # noqa: E402

SOURCES = ("uploaded", "website", "created")
LICENSES = ("ofl", "apache", "google", "bought", "system", "unknown")
RASTER = (".png", ".jpg", ".jpeg", ".webp")
DESIGN_FILES = (".ai", ".eps", ".psd", ".indd", ".sketch", ".fig")
PLACEHOLDER = re.compile(r"lorem ipsum|your (headline|name|business|logo) here|\bTBD\b|\[[^\]]*\]|headline goes here", re.I)


# ---------------------------------------------------------------- the kit
def load_kit(path):
    k = bl.read_json(path)
    if not isinstance(k, dict):
        sys.exit("The kit must be a JSON object.")
    return normalise(k)


def normalise(k):
    k = dict(k)
    k.setdefault("audience", "50plus")
    k["colors"] = {key: (bl.norm_hex(v) or v) for key, v in (k.get("colors") or {}).items()}
    fonts = {r: dict((k.get("fonts") or {}).get(r) or {}) for r in ("head", "body")}
    fonts["head"].setdefault("weight", 700)
    fonts["head"].setdefault("fallback", "Georgia, 'Times New Roman', serif")
    fonts["body"].setdefault("fallback", "system-ui, -apple-system, 'Segoe UI', Arial, sans-serif")
    k["fonts"] = fonts
    ty = dict(k.get("type") or {})
    ty.setdefault("base_px", 18 if k["audience"] == "50plus" else 17)
    ty.setdefault("scale", 1.25); ty.setdefault("measure_ch", 64); ty.setdefault("line_height", 1.6)
    k["type"] = ty
    sh = dict(k.get("shape") or {})
    sh.setdefault("radius_px", 4)
    k["shape"] = sh
    k.setdefault("logo", {"kind": "none"})
    k.setdefault("palette", [])
    return k


def problems(k, base, for_lock=True, direction=False):
    """(fixes, looks). A FIX stops the lock. A LOOK is for the session to read and the member to decide."""
    fix, look = [], []
    base = Path(base)
    name = (k.get("name") or "").strip()
    if not name:
        fix.append("name: the kit has no business name")
    if not direction and k.get("source") not in SOURCES:
        fix.append("source: say where this brand came from: uploaded (the member's own kit), website (read from their site) or created (made here)")
    # colors
    col = k["colors"]
    bad = [key for key in bl.COLOR_KEYS if not bl.norm_hex(col.get(key))]
    if bad:
        fix.append("colors: missing or not a hex color: " + ", ".join(bad) + ". Run `brandkit.py roles` on the brand's colors for a starting set")
    else:
        for fg, bg, r, need, sug in bl.contrast_problems(col):
            fix.append(f"colors: {bl.LABELS[fg].lower()} {col[fg]} on {bl.LABELS[bg].lower()} {col[bg]} is {r}:1 and needs {need}:1. "
                       f"{sug} passes. A brand color that is too faint for text keeps its place as a fill; text takes the darker shade")
        pal = {bl.norm_hex(p.get("hex")) for p in k["palette"] if isinstance(p, dict)}
        if k.get("source") in ("uploaded", "website"):
            if not pal - {None}:
                fix.append("palette: list the brand's own colors as the member gave them (name, hex, where it came from), before any working color is derived")
            added = [f"{key} {col[key]}" for key in ("bg", "ink", "accent") if col[key] not in pal and not bl.is_neutral(col[key])]
            if added:
                look.append("colors: not one of the brand's own colors: " + ", ".join(added) + ". Tell the member which colors were added and why")
        if k.get("source") == "created" or direction:
            if bl.is_cream(col["bg"]):
                look.append("tell: a cream page background is the default look of 2026. Keep it only if it comes from the member's references")
            if bl.is_purple(col["accent"]):
                look.append("tell: a purple accent is what arrives when nobody chooses. Keep it only if it comes from the member's world")
            vivid = [p for p in pal - {None} if not bl.is_neutral(p)]
            if len(vivid) > 3:
                look.append(f"palette: {len(vivid)} strong colors. A small business brand holds together with one or two")
    for p in k["palette"]:
        if not isinstance(p, dict) or not bl.norm_hex(p.get("hex")):
            fix.append(f"palette: every entry needs a hex color: {p!r}")
    # fonts
    for role in ("head", "body"):
        f = k["fonts"][role]
        fam = (f.get("family") or "").strip()
        if not fam:
            fix.append(f"fonts.{role}: no typeface named")
            continue
        missing = [s for s, _ in bp.font_files(f) if not (base / s).is_file()]
        if missing:
            fix.append(f"fonts.{role}: file not found: " + ", ".join(missing))
        lic = (f.get("license") or "unknown").lower()
        if lic not in LICENSES:
            fix.append(f"fonts.{role}: license must be one of " + ", ".join(LICENSES))
        elif lic == "unknown" and fam.lower() not in bl.SYSTEM_FONTS:
            look.append(f"fonts.{role}: the license for {fam} is not confirmed. Ask the member where the font came from before it goes on a public page")
        elif lic == "bought":
            look.append(f"fonts.{role}: {fam} is a bought font. The member checks that the license covers web pages and social images")
        if not bp.font_files(f) and fam.lower() not in bl.SYSTEM_FONTS:
            look.append(f"fonts.{role}: no font file for {fam}. Run `brandkit.py fonts` if it is a Google Font, or ask the member for the file")
        if (k.get("source") == "created" or direction) and role == "head" and fam.lower() in bl.DEFAULT_FONTS:
            look.append(f"tell: {fam} is a default typeface. A new brand deserves a face somebody chose: see creating.md")
    if k["type"]["base_px"] < bl.MIN_BODY.get(k["audience"], 16):
        fix.append(f"type: body text is {k['type']['base_px']}px and this audience needs {bl.MIN_BODY[k['audience']]}px")
    # logo
    lg = k["logo"]
    kind = lg.get("kind")
    if kind == "files":
        named = {key: lg.get(key) for key in ("on_light", "on_dark", "mark_on_light", "mark_on_dark") if lg.get(key)}
        if not (named.get("on_light") or named.get("on_dark")):
            fix.append("logo: name at least one logo file (on_light for light backgrounds, on_dark for dark ones)")
        for key, src in named.items():
            p = base / src
            if not p.is_file():
                fix.append(f"logo.{key}: file not found: {src}")
                continue
            for line, sev in inspect_logo(p):
                (fix if sev == "FIX" else look).append(f"logo.{key}: {line}")
        if named.get("on_light") and not named.get("on_dark"):
            look.append("logo: there is no version for dark backgrounds. Ask the member for a white or reversed logo; until then the logo is used on light grounds only")
        if named.get("on_dark") and not named.get("on_light"):
            look.append("logo: there is no version for light backgrounds. Ask the member for one; until then the logo is used on dark grounds only")
        if not (named.get("mark_on_light") or named.get("mark_on_dark")):
            look.append("logo: no small mark (a square version for profile pictures and browser tabs). Ask whether the member has one")
    elif kind == "wordmark":
        text = (lg.get("text") or "").strip()
        if not text:
            fix.append("logo: a wordmark needs its text")
        elif name and not _same_name(text, name) and not _same_name(text, k.get("person") or ""):
            fix.append(f'logo: the wordmark says "{text}" and the business is "{name}". A logo sets the real name; it never invents one')
        letters = ((lg.get("mark") or {}).get("letters") or "").strip()
        if letters and (len(letters) > 3 or not letters.replace("&", "").isalnum()):
            fix.append("logo.mark: one to three letters")
        if (lg.get("mark") or {}).get("shape", "square") not in ("none", "square", "circle"):
            fix.append("logo.mark.shape: none, square or circle")
        if lg.get("layout", "text") not in ("text", "mark-text"):
            fix.append("logo.layout: text or mark-text")
        if lg.get("font", "head") not in ("head", "body"):
            fix.append("logo.font: head or body")
        elif not fix or all(not x.startswith("fonts.") for x in fix):
            f = k["fonts"][lg.get("font", "head")]
            file = bp.pick_file(f, base, lg.get("weight"))
            if not file:
                (fix if for_lock else look).append("logo: the wordmark needs its font file to be drawn as vector shapes. Run `brandkit.py fonts` first")
            elif not bl.open_font(file):
                look.append(f"logo: {file.name} is not a TrueType file this tool can outline, so the logo files will carry live text. A .ttf gives real vector shapes")
            else:
                fo = bl.open_font(file)
                absent = sorted({ch for ch in bp.cased(text + letters, lg.get("case", "as-typed")) if ch != " " and not fo.has(ch)})
                if absent:
                    fix.append(f"logo: {f.get('family')} has no letter for: {' '.join(absent)}")
    elif kind == "none":
        look.append("logo: no logo. The business name is set in the heading typeface wherever a logo would go. Offer a wordmark")
    else:
        fix.append("logo.kind: files (the member's own logo files), wordmark (the name set in type) or none")
    # words shown on the board and the sheet
    sample = k.get("sample") or {}
    for key in ("headline", "body", "cta", "person", "role"):
        if sample.get(key) and PLACEHOLDER.search(sample[key]):
            fix.append(f"sample.{key}: placeholder text. Use the member's own words from the Business File, or leave it out")
    if direction:
        for key in ("idea", "from"):
            if not (k.get(key) or "").strip():
                fix.append(f"{key}: every direction says in one sentence " + ("why it suits this business" if key == "idea" else "what in the member's answers or references it comes from"))
    if for_lock and not direction:
        conf = k.get("confirmed") or {}
        waiting = [x for x in ("colors", "fonts", "logo") if conf.get(x) is not True]
        if waiting:
            fix.append("confirmed: the member has not said yes to: " + ", ".join(waiting) + ". Show them, then set confirmed." + waiting[0] + " (and the rest) to true. Nothing is locked on a guess")
        if not k.get("dos") or not k.get("donts"):
            look.append("rules: write two or three do and do-not lines with the member, in their words")
    return fix, look


def _same_name(a, b):
    na, nb = (re.sub(r"[^a-z0-9]", "", x.lower()) for x in (a, b))
    return bool(na) and bool(nb) and (na in nb or nb in na)


def inspect_logo(p):
    """[(line, FIX or LOOK)] about one logo file."""
    out = []
    ext = p.suffix.lower()
    data = p.read_bytes()
    if ext == ".svg":
        text = data.decode("utf-8", errors="replace")
        if "<image" in text:
            out.append(("this SVG wraps a picture, so it will blur when enlarged. Ask for the true vector file", "LOOK"))
        if re.search(r"<text\b", text):
            out.append(("this SVG carries live text, so it needs the font installed wherever it is opened. Ask the designer for outlines", "LOOK"))
    elif ext == ".png":
        info = bl.png_info(data)
        if not info:
            out.append(("not a readable PNG", "FIX"))
        else:
            if info["width"] < 600:
                out.append((f"only {info['width']} pixels wide. It will look soft on a banner or a slide: ask for the original (a vector file, or a PNG at least 1000 pixels wide)", "FIX"))
            elif info["width"] < 1000:
                out.append((f"{info['width']} pixels wide: fine for social images, small for print. Ask whether a larger or vector original exists", "LOOK"))
            if not info["alpha"]:
                out.append(("no transparent background, so it will sit in a box on any color but its own. Ask for a transparent PNG or an SVG", "LOOK"))
    elif ext in (".jpg", ".jpeg"):
        info = bl.jpeg_size(data)
        if info and info["width"] < 600:
            out.append((f"only {info['width']} pixels wide: ask for the original", "FIX"))
        out.append(("a JPEG has no transparent background and blurs fine edges. Ask for an SVG or a transparent PNG", "LOOK"))
    elif ext in DESIGN_FILES:
        out.append((f"a {ext} file cannot be placed on a page. Ask for an SVG or PNG export of it", "FIX"))
    elif ext not in RASTER:
        out.append((f"{ext or 'this file type'} is not a logo format a page can use. SVG is best, a transparent PNG is fine", "FIX"))
    return out


# ---------------------------------------------------------------- read
def cmd_read(a):
    out = []
    for raw in a.files:
        p = Path(raw)
        if not p.is_file():
            out.append({"file": raw, "error": "not found"})
            continue
        ext, data = p.suffix.lower(), p.read_bytes()
        e = {"file": raw, "bytes": len(data)}
        if ext == ".svg":
            text = data.decode("utf-8", errors="replace")
            vb = re.search(r'viewBox="([^"]+)"', text)
            e.update(kind="vector logo", view_box=vb.group(1) if vb else None, colors=bl.text_colors(text, 8), fonts=bl.text_fonts(text),
                     live_text=bool(re.search(r"<text\b", text)), wraps_a_picture="<image" in text)
        elif ext == ".png":
            info = bl.png_info(data) or {}
            e.update(kind="picture", width=info.get("width"), height=info.get("height"), transparent=info.get("alpha"), colors=bl.png_colors(data))
            if not e["colors"]:
                e["note"] = "could not sample the colors of this PNG: open it and name them by eye"
        elif ext in (".jpg", ".jpeg"):
            info = bl.jpeg_size(data) or {}
            e.update(kind="picture", width=info.get("width"), height=info.get("height"), transparent=False,
                     note="colors of a JPEG are not sampled here: open it and name them by eye, or ask for a PNG or SVG")
        elif ext in (".css", ".html", ".htm"):
            text = data.decode("utf-8", errors="replace")
            e.update(kind="web page or stylesheet", colors=bl.text_colors(text, 12), fonts=bl.text_fonts(text),
                     note="most-used first. A color used once may be an icon or a border, not the brand")
        elif ext in (".ttf", ".otf"):
            f = bl.open_font(p)
            e.update(kind="font", family=(f.name() if f else bl_font_name(data)), can_outline=bool(f))
        elif ext in (".woff", ".woff2"):
            e.update(kind="font", family=None, can_outline=False, note="a web font file. It works on pages; a .ttf is needed to draw a wordmark as vector shapes")
        elif ext == ".json":
            try:
                t = json.loads(data.decode("utf-8-sig"))
                e.update(kind="design system", colors=t.get("color"), fonts=[t.get("font", {}).get(r, {}).get("family") for r in ("head", "body")],
                         has_brand_kit=bool(t.get("brand")))
            except ValueError:
                e["error"] = "not valid JSON"
        elif ext == ".pdf":
            e.update(kind="document", note="open and read this yourself: brand guides give color values, font names and logo rules in words. This command does not read PDFs")
        elif ext in DESIGN_FILES:
            e.update(kind="design file", note="cannot be read or placed. Ask the member or their designer for SVG or PNG exports and the color values")
        else:
            e.update(kind="unknown", note="not a file type this command reads")
        out.append(e)
    print(json.dumps({"files": out, "wrote": "nothing"}, indent=2, ensure_ascii=False))


def bl_font_name(data):
    """The family name of an OpenType (.otf) font, read from its name table."""
    import struct
    try:
        n = struct.unpack(">H", data[4:6])[0]
        for i in range(n):
            tag, _cs, off, _ln = struct.unpack(">4sIII", data[12 + 16 * i:28 + 16 * i])
            if tag == b"name":
                count, so = struct.unpack(">HH", data[off + 2:off + 6])
                for j in range(count):
                    pid, _e, _l, nid, ln, o = struct.unpack(">6H", data[off + 6 + 12 * j:off + 18 + 12 * j])
                    if nid == 1:
                        raw = data[off + so + o:off + so + o + ln]
                        return (raw.decode("utf-16-be") if pid in (0, 3) else raw.decode("mac-roman")).strip()
    except Exception:
        pass
    return None


def cmd_roles(a):
    try:
        roles, changed = bl.propose_roles(a.colors, a.dark)
    except ValueError as e:
        sys.exit(str(e))
    print(json.dumps({"colors": roles, "not_the_brands_own": changed,
                      "contrast": {f"{fg} on {bg}": bl.contrast(roles[fg], roles[bg]) for fg, bg, _ in bl.PAIRS},
                      "say": "Show the member every color listed under not_the_brands_own before it is used."}, indent=2))


# ---------------------------------------------------------------- fonts (the one command that goes online)
def cmd_fonts(a):
    path = Path(a.kit)
    raw = bl.read_json(path)
    kits = raw["directions"] if isinstance(raw.get("directions"), list) else [raw]
    dest = path.parent / "fonts"
    got, failed = [], []
    for k in kits:
        for role in ("head", "body"):
            f = (k.get("fonts") or {}).get(role)
            if not isinstance(f, dict) or not f.get("family") or f["family"].lower() in bl.SYSTEM_FONTS:
                continue
            if any((path.parent / s).is_file() for s, _ in bp.font_files(f)):
                continue
            weights = sorted({int(f.get("weight", 700))} | ({int((k.get("logo") or {}).get("weight") or f.get("weight", 700))} if role == "head" else {400, 700}))
            files = []
            for w in weights:
                name = f"{re.sub(r'[^A-Za-z0-9]+', '', f['family'])}-{w}.ttf"
                if (dest / name).is_file() or _fetch_google(f["family"], w, dest / name):
                    files.append({"src": f"fonts/{name}", "weight": w})
            if files:
                f["files"] = files
                f.setdefault("license", "google")
                got.append(f"{f['family']} ({', '.join(str(x['weight']) for x in files)})")
            else:
                failed.append(f["family"])
    if got:
        bl.write_json(path, raw)
    print(json.dumps({"downloaded_to": str(dest), "fonts": got, "not_found": failed,
                      "note": ("Not on Google Fonts, or Google Fonts could not be reached: ask the member for the font files and name them under fonts.<role>.files."
                               if failed else "Font files are saved beside the kit and named in it. Confirm each family's license tab on fonts.google.com before the kit is locked.")},
                     indent=2, ensure_ascii=False))
    sys.exit(1 if failed and not got else 0)


def _fetch_google(family, weight, dest):
    url = "https://fonts.googleapis.com/css2?family=" + urllib.parse.quote_plus(family) + f":wght@{weight}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/4.0"})        # an old browser is sent plain .ttf files
        css = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")
        m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+\.ttf)\)", css)
        if not m:
            return False
        data = urllib.request.urlopen(urllib.request.Request(m.group(1), headers={"User-Agent": "Mozilla/4.0"}), timeout=60).read()
        if data[:4] not in (b"\x00\x01\x00\x00", b"true", b"OTTO"):
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except (urllib.error.URLError, OSError, ValueError):
        return False


# ---------------------------------------------------------------- check
def cmd_check(a):
    path = Path(a.kit)
    k = load_kit(path)
    fix, look = problems(k, path.parent)
    for x in fix:
        print("FIX  " + x)
    for x in look:
        print("LOOK  " + x)
    print(f"\n{len(fix)} to fix, {len(look)} to look at." + (" Ready to lock." if not fix else ""))
    sys.exit(1 if fix else 0)


# ---------------------------------------------------------------- board
def differ(a, b):
    """How many of four axes separate two directions: ground, accent, heading face, logo treatment."""
    ca, cb = a["colors"], b["colors"]
    n = 0
    n += bl.is_dark(ca["bg"]) != bl.is_dark(cb["bg"]) or bl.family(ca["bg"]) != bl.family(cb["bg"])
    ha, hb = bl.hls(ca["accent"])[0], bl.hls(cb["accent"])[0]
    n += min(abs(ha - hb), 360 - abs(ha - hb)) > 40 or bl.is_neutral(ca["accent"]) != bl.is_neutral(cb["accent"])
    n += a["fonts"]["head"].get("family", "").lower() != b["fonts"]["head"].get("family", "").lower()
    la, lb = a["logo"], b["logo"]
    n += (la.get("case", "as-typed"), la.get("layout", "text"), (la.get("mark") or {}).get("shape", "square")) != \
         (lb.get("case", "as-typed"), lb.get("layout", "text"), (lb.get("mark") or {}).get("shape", "square"))
    return n


def cmd_board(a):
    path = Path(a.directions)
    d = bl.read_json(path)
    dirs = d.get("directions")
    business = (d.get("business") or "").strip()
    sample = d.get("sample") or {}
    fix = []
    if not business:
        fix.append("business: the business name")
    if not isinstance(dirs, list) or not 2 <= len(dirs) <= 4:
        sys.exit("FIX  directions: two to four directions. Three is the usual number")
    for key in ("headline", "body"):
        if not (sample.get(key) or "").strip():
            fix.append(f"sample.{key}: the member's own words from the Business File. A direction is judged on real copy, never on placeholder text")
    kits = []
    for i, raw in enumerate(dirs, 1):
        k = normalise({**raw, "audience": d.get("audience", "50plus"), "sample": sample, "person": d.get("person"), "business": business})
        k.setdefault("logo", {})
        f, look = problems({**k, "name": k.get("name") or f"Direction {i}"}, path.parent, for_lock=False, direction=True)
        if k["logo"].get("kind") == "wordmark" and not _same_name(k["logo"].get("text", ""), business):
            f.append(f'logo: the wordmark says "{k["logo"].get("text", "")}" and the business is "{business}"')
        f = [x for x in f if not x.startswith("logo: the wordmark says") or business in x]
        fix += [f"direction {i} ({k.get('name', '?')}): {x}" for x in f]
        for x in look:
            print(f"LOOK  direction {i} ({k.get('name', '?')}): {x}")
        kits.append(k)
    if not fix:
        for i in range(len(kits)):
            for j in range(i + 1, len(kits)):
                if differ(kits[i], kits[j]) < 2:
                    fix.append(f"directions {i + 1} and {j + 1} ({kits[i]['name']}, {kits[j]['name']}) are the same idea twice: they differ on fewer than two of "
                               "ground, accent color, heading typeface and logo treatment. Make them really different, or show fewer")
    if fix:
        for x in fix:
            print("FIX  " + x)
        sys.exit(1)
    out = Path(a.out)
    html = bp.board_html(business, kits, sample, path.parent, out.parent, embed=a.embed)
    bl.write_atomic(out, html)
    print(f"Wrote {out}: {len(kits)} directions for {business}. Open it with the member; they choose one or mix.")


# ---------------------------------------------------------------- lock
def cmd_lock(a):
    path = Path(a.kit)
    k = load_kit(path)
    base = path.parent
    fix, look = problems(k, base)
    if fix:
        for x in fix:
            print("FIX  " + x, file=sys.stderr)
        sys.exit(f"{len(fix)} thing(s) to fix before the kit is locked. Run: brandkit.py check {a.kit}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    prev = out / "tokens.json"
    old = bl.read_json(prev) if prev.exists() else {}
    version = int(old.get("version", 0)) + 1
    locked = str(date.today())
    col, f, ty = k["colors"], k["fonts"], k["type"]
    own, rev = bp.grounds(k)
    ls = bp.logo_set(k, base)
    files = [("Brand Kit.html", "This page. Open it in a browser; print it to PDF to send it.")]
    logo = {"kind": ls["kind"]}
    if ls["kind"] == "wordmark":
        ldir = base / "logo"
        light_first = not bl.is_dark(own["bg"])
        names = {"on_own": "wordmark.svg" if light_first else "wordmark-on-dark.svg", "on_reverse": "wordmark-on-dark.svg" if light_first else "wordmark.svg",
                 "mark_own": "mark.svg" if light_first else "mark-on-dark.svg", "mark_reverse": "mark-on-dark.svg" if light_first else "mark.svg"}
        for key, name in names.items():
            bl.write_atomic(ldir / name, ls[key] + "\n")
        logo.update(on_light=bl.rel(ldir / "wordmark.svg", out), on_dark=bl.rel(ldir / "wordmark-on-dark.svg", out),
                    mark_on_light=bl.rel(ldir / "mark.svg", out), mark_on_dark=bl.rel(ldir / "mark-on-dark.svg", out), outlined=ls["outlined"])
        files += [("logo/wordmark.svg", "The logo for light backgrounds. A vector file: sharp at any size."),
                  ("logo/wordmark-on-dark.svg", "The logo for dark backgrounds and photographs."),
                  ("logo/mark.svg and logo/mark-on-dark.svg", "The small mark, for profile pictures and browser tabs."),
                  ("logo/*.png", "The same logos as pictures, for tools that will not take a vector file (made by brand_png.mjs).")]
    elif ls["kind"] == "files":
        lg = k["logo"]
        for key in ("on_light", "on_dark", "mark_on_light", "mark_on_dark"):
            if lg.get(key):
                logo[key] = bl.rel(base / lg[key], out)
                files.append((lg[key], {"on_light": "Your logo for light backgrounds.", "on_dark": "Your logo for dark backgrounds.",
                                        "mark_on_light": "Your small mark for light backgrounds.", "mark_on_dark": "Your small mark for dark backgrounds."}[key]))
    font_files = {role: [{"src": bl.rel(base / s, out), **({"weight": w} if w else {})} for s, w in bp.font_files(f[role]) if (base / s).is_file()]
                  for role in ("head", "body")}
    for role in ("head", "body"):
        for s, _ in bp.font_files(f[role]):
            files.append((s, f"{f[role]['family']}: the font file, for pages and images."))
    files += [("../System/design-system.md", "The same kit as a plain page of rules. Every Build Room session reads it."),
              ("../System/tokens.css", "The colors, typefaces and sizes as code, ready to paste into any web page."),
              ("kit.json" if path.name == "kit.json" else path.name, "The kit as data. Change it here, then lock again.")]
    keep = {key: old[key] for key in ("space", "shadow", "motion", "buttons", "photo", "hero", "texture", "density", "eyebrows", "head_italic", "refs", "attrs", "dark")
            if key in old}
    photo = k.get("photo") or {}
    tokens = {
        "schema": "buildroom-design/1", "name": k.get("direction") or (old.get("name") if old and not old.get("brand") else None) or f"{k['name']} brand",
        "look": old.get("look") or "Brand Kit", "locked": locked, "audience": k["audience"], "version": version,
        "color": {key: col[key] for key in bl.COLOR_KEYS}, "dark": keep.get("dark", {}),
        "font": {"head": {"family": f["head"]["family"], "fallback": f["head"]["fallback"], "weight": int(f["head"]["weight"]),
                          "weights": sorted({int(f["head"]["weight"])} | {w for _, w in bp.font_files(f["head"]) if w})},
                 "body": {"family": f["body"]["family"], "fallback": f["body"]["fallback"],
                          "weights": sorted({w for _, w in bp.font_files(f["body"]) if w} or {400, 700})},
                 "pair": "brand kit", "licence": "; ".join(f"{f[r]['family']}: {f[r].get('license', 'unknown')}" for r in ("head", "body"))},
        "type": {"base_px": ty["base_px"], "scale": ty["scale"], "measure_ch": ty["measure_ch"], "line_height": ty["line_height"]},
        "space": keep.get("space", {"unit_px": 8}), "radius_px": k["shape"]["radius_px"],
        "shadow": keep.get("shadow", "none"), "motion": keep.get("motion", "gentle"), "buttons": keep.get("buttons", "solid"),
        "photo": photo.get("treatment") or keep.get("photo", "natural"), "hero": keep.get("hero", "split"), "texture": keep.get("texture", "none"),
        "density": keep.get("density", "regular"), "eyebrows": keep.get("eyebrows", False), "head_italic": keep.get("head_italic", False),
        "imagery": {"source": photo.get("source") or (old.get("imagery") or {}).get("source", "own"),
                    "rules": photo.get("rules") or (old.get("imagery") or {}).get("rules", "")},
        "dos": list(k.get("dos") or old.get("dos") or []), "donts": list(k.get("donts") or old.get("donts") or []),
        "refs": keep.get("refs", []), "attrs": keep.get("attrs", {}),
        "brand": {"name": k["name"], "source": k["source"], "direction": k.get("direction"), "palette": k["palette"], "logo": logo,
                  "font_files": font_files, "reverse": rev, "kit": bl.rel(path, out), "sheet": bl.rel(base / "Brand Kit.html", out)},
    }
    tokens["vars"] = {**{bl.VAR_OF[key]: col[key] for key in bl.COLOR_KEYS},
                      "--font-head": bp.stack(f["head"], "serif"), "--font-body": bp.stack(f["body"]), "--w-head": str(int(f["head"]["weight"])),
                      "--size-base": f"{ty['base_px']:g}px", "--scale": f"{ty['scale']:g}", "--measure": f"{ty['measure_ch']:g}ch",
                      "--leading": f"{ty['line_height']:g}", "--space": f"{tokens['space']['unit_px']:g}px", "--radius": f"{tokens['radius_px']:g}px"}
    slides = slides_json(tokens)
    pages = {out / "tokens.css": tokens_css(tokens), out / "design-system.md": system_md(tokens, slides, k),
             out / "fonts.md": fonts_md(k), base / "Brand Kit.html": bp.sheet_html(k, base, base, files, version, locked)}
    if prev.exists():
        shutil.copy2(prev, out / f"tokens-v{version - 1}.json")
    bl.write_json(prev, tokens)
    bl.write_json(out / "slides.json", slides)
    for p, text in pages.items():
        bl.write_atomic(p, text)
    for x in look:
        print("LOOK  " + x)
    print(json.dumps({"ok": True, "version": version, "system": str(out), "sheet": str(base / "Brand Kit.html"),
                      "logo_files": [v for key, v in logo.items() if key.startswith(("on_", "mark_"))],
                      "next": ["Open the brand sheet with the member.",
                               "brandkit.py section --system " + str(out) + "  (the Business File lines)"]
                      + (["node brand_png.mjs " + str(base / "logo") + "  (PNG copies of the logo, if Node and Playwright are installed)"] if ls["kind"] == "wordmark" else [])},
                     indent=2, ensure_ascii=False))


def tokens_css(t):
    lines = [f"/* {t['brand']['name']} brand kit: version {t['version']}, locked {t['locked']}.",
             "   Paste into any page. Every color, typeface and size on the page comes from these. */", ":root {"]
    lines += [f"  {key}: {val};" for key, val in t["vars"].items()]
    lines += ["  --shadow: none;", "  --motion: 1;", "}"]
    rev = t["brand"]["reverse"]
    lines.append("/* The reverse ground: the text color as the background. Use it for a band, a card or a footer. */")
    lines.append('.reverse, [data-ground="reverse"] {')
    lines += [f"  {bl.VAR_OF[key]}: {rev[key]};" for key in bl.COLOR_KEYS]
    lines += ["}", "@media (prefers-reduced-motion: reduce) { :root { --motion: 0; } }"]
    return "\n".join(lines) + "\n"


def slides_json(t):
    theme = "dark" if bl.is_dark(t["color"]["bg"]) else "light"
    ground = "#141414" if theme == "dark" else "#ffffff"
    acc = bl.shade_to_contrast(t["color"]["accent"], ground, 4.5)
    fb = t["font"]["body"]["fallback"]
    font = "Georgia" if "serif" in fb and "sans" not in fb else "Arial"
    return {"theme": theme, "accent": acc.lstrip("#").upper(), "font": font,
            "flags": f"--theme {theme} --accent {acc.lstrip('#').upper()} --font \"{font}\"",
            "why_font": "slides open on other computers, so they use a font every computer has; the brand typefaces stay on the web and in images",
            "note": "" if acc == t["color"]["accent"] else f"accent darkened from {t['color']['accent']} to {acc} so it reads on slides"}


def system_md(t, slides, k):
    c, f, ty, b = t["color"], t["font"], t["type"], t["brand"]
    rows = "\n".join(f"| {bl.LABELS[key]} | `{c[key]}` | `{bl.VAR_OF[key]}` |" for key in bl.COLOR_KEYS)
    pal = "\n".join(f"- **{p.get('name') or bl.family(p['hex']).title()}** `{bl.norm_hex(p['hex'])}`" + (f": {p['role']}" if p.get("role") else "")
                    + (f" (from {p['from']})" if p.get("from") else "") for p in b["palette"]) or "- See the working colors below."
    lg = b["logo"]
    if lg["kind"] == "none":
        logo = "- No logo file. Set the business name in the heading typeface wherever a logo would go."
    else:
        logo = "\n".join(f"- {label}: `{lg[key]}`" for key, label in (("on_light", "On light backgrounds"), ("on_dark", "On dark backgrounds and photographs"),
                                                                    ("mark_on_light", "Small mark, light backgrounds"), ("mark_on_dark", "Small mark, dark backgrounds")) if lg.get(key))
        logo += "\n- Clear space: the height of the logo's capital letter on every side. Never stretch, tilt, recolor or add effects."
        if not lg.get("on_dark"):
            logo += "\n- There is no dark-ground version: use the logo on light grounds only."
        if not lg.get("on_light"):
            logo += "\n- There is no light-ground version: use the logo on dark grounds only."
    sizes = [ty["base_px"] * ty["scale"] ** n for n in (4, 3, 2, 1, 0)]
    dos = "\n".join(f"- {x}" for x in t["dos"]) or "- Use the accent for one thing per screen: the main button."
    donts = "\n".join(f"- {x}" for x in t["donts"]) or "- No colors or typefaces outside this page."
    src = {"uploaded": "the member's own brand kit, taken in and checked", "website": "read from the member's website and confirmed by them",
           "created": "created in the Brand Kit session"}[b["source"]]
    img = {"own": "the member's own photos", "kie": "generated images (logged in the media ledger)",
           "both": "the member's own photos first; generated images for scenes, textures and backgrounds"}.get(t["imagery"]["source"], t["imagery"]["source"])
    return f"""# Design System: {b['name']}

_Version {t['version']} · locked {t['locked']} · for a {'50+' if t['audience'] == '50plus' else 'general'} audience · brand: {src}_

This is how everything {b['name']} publishes looks: pages, posts, slides, ads and documents. Every Build Room session reads it before it designs anything. The same kit, laid out to look at, is `{b['sheet']}`.

## Logo

{logo}

## Brand colors

{pal}

## Working colors

| Use | Color | Variable |
|---|---|---|
{rows}

The reverse ground (the text color as a background) is in `tokens.css` as `.reverse`: background `{b['reverse']['bg']}`, text `{b['reverse']['ink']}`, accent `{b['reverse']['accent']}`.

## Typefaces

- **Headings:** {f['head']['family']} (weight {f['head']['weight']}). Fallback: {f['head']['fallback']}.
- **Text:** {f['body']['family']}. Fallback: {f['body']['fallback']}.
- Font files and licenses: see `fonts.md`.
- **On slides:** {slides['font']}, because slides open on other computers. Slide flags: `{slides['flags']}`.

## Sizes

- Body text **{ty['base_px']:g}px**, line height {ty['line_height']:g}, lines about {ty['measure_ch']:g} characters long.
- Headings step up by {ty['scale']:g}: {', '.join(f'{s:.0f}px' for s in sizes)}.
- Nothing under 14px, captions and fine print included.

## Shape

- Corners {t['radius_px']:g}px. Flat color: no gradients, glows or drop shadows unless the kit says so.

## Photos and images

- Source: {img}.
- {t['imagery']['rules'] or 'Real people only with their consent; a generated image never shows a real person.'}

## Do

{dos}

## Don't

{donts}
- Never a generated picture logo, and never a logo redrawn from memory: use the files above.

## Briefing a designer or VA

Send them the brand sheet, `tokens.css` and the logo files. Say: "Use only these colors and typefaces, at these sizes. Body text never under {ty['base_px']:g}px. One main button per screen, in the accent color. Check contrast before you send anything back."
"""


def fonts_md(k):
    lines = ["# Typefaces: files and licenses", ""]
    for role, label in (("head", "Headings"), ("body", "Text")):
        f = k["fonts"][role]
        files = [s for s, _ in bp.font_files(f)]
        lic = (f.get("license") or "unknown").lower()
        lines += [f"## {label}: {f['family']}", "",
                  "- Files: " + (", ".join(f"`{s}`" for s in files) if files else "none saved. Pages load it by name; add the files before going live."),
                  "- License: " + {"ofl": "SIL Open Font License. Free for commercial use; keep OFL.txt with the files.",
                                   "apache": "Apache 2.0. Free for commercial use.",
                                   "google": f"from Google Fonts, which carries open licenses. Confirm on https://fonts.google.com/specimen/{f['family'].replace(' ', '+')} (the license tab).",
                                   "bought": "bought by the member. Check that the license covers web pages and social images, and how many page views.",
                                   "system": "comes with the computer. Pages fall back to a similar face on computers that lack it.",
                                   "unknown": "NOT CONFIRMED. Find out where this font came from before it goes on a public page."}[lic], ""]
    lines += ["## On a web page", "", "Host the font files on the member's own site instead of loading them from another company's servers: it is faster and it keeps visitors' details at home.", "",
              "```css", '@font-face { font-family: "<Family>"; src: url("fonts/<file>") ; font-weight: 400 700; font-display: swap; }', "```", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- section, show
def cmd_section(a):
    sysdir = Path(a.system)
    t = bl.read_json(sysdir / "tokens.json")
    b = t.get("brand")
    if not b:
        sys.exit("This Design System has no brand kit yet. Run: brandkit.py lock KIT.json --out " + str(sysdir))
    c, lg = t["color"], b["logo"]
    src = {"uploaded": "the member's own", "website": "read from their website", "created": "made here"}[b["source"]]
    logos = ", ".join(lg[key] for key in ("on_light", "on_dark", "mark_on_light", "mark_on_dark") if lg.get(key)) or "no logo file: name set in the heading typeface"
    lines = [
        f"- **Brand kit** (yours or made here · logo files · brand sheet · locked): {src} · {logos} · {b['sheet']} · {t['locked']}",
        f"- **Locked system** (palette · fonts · type scale · corners · spacing · motion): {t['name']} v{t['version']} ({t['locked']}) · "
        f"bg {c['bg']} ink {c['ink']} accent {c['accent']} · {t['font']['head']['family']} / {t['font']['body']['family']} · "
        f"{t['type']['base_px']:g}px × {t['type']['scale']:g} · {t['radius_px']:g}px corners · {t['space']['unit_px']:g}px spacing · motion {t['motion']}",
        f"- **Imagery rules** (own photos / generated · provider · consent): {t['imagery']['source']}" + (f" · {t['imagery']['rules']}" if t["imagery"]["rules"] else ""),
        f"- **Do / don't:** {'; '.join(t['dos'][:3]) or '—'} / {'; '.join(t['donts'][:3]) or '—'}",
        f"- **Files** (design-system.md · tokens.json · tokens.css · slides.json · first page): {sysdir}/",
    ]
    print(json.dumps({"ok": True, "section_22": lines, "section_22_status": "provisional until a page has passed the Website Design Studio's go-live check; complete after",
                      "section_18_brand_kit": f"see §22 (Design System v{t['version']})",
                      "leave_alone": "§22 Taste vault, Directions tried and Used by: change them only if this session changed them"}, indent=2, ensure_ascii=False))


def cmd_show(a):
    t = bl.read_json(Path(a.system) / "tokens.json")
    b = t.get("brand") or {}
    print(json.dumps({"name": t.get("name"), "version": t.get("version"), "locked": t.get("locked"), "color": t.get("color"),
                      "fonts": [t["font"]["head"]["family"], t["font"]["body"]["family"]], "brand_kit": bool(b),
                      "source": b.get("source"), "logo": b.get("logo"), "sheet": b.get("sheet")}, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("read"); p.add_argument("files", nargs="+"); p.set_defaults(fn=cmd_read)
    p = sub.add_parser("roles"); p.add_argument("colors", nargs="+"); p.add_argument("--dark", action="store_true"); p.set_defaults(fn=cmd_roles)
    p = sub.add_parser("fonts"); p.add_argument("kit"); p.set_defaults(fn=cmd_fonts)
    p = sub.add_parser("check"); p.add_argument("kit"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("board"); p.add_argument("directions"); p.add_argument("out"); p.add_argument("--embed", action="store_true"); p.set_defaults(fn=cmd_board)
    p = sub.add_parser("lock"); p.add_argument("kit"); p.add_argument("--out", required=True); p.set_defaults(fn=cmd_lock)
    p = sub.add_parser("section"); p.add_argument("--system", required=True); p.set_defaults(fn=cmd_section)
    p = sub.add_parser("show"); p.add_argument("--system", required=True); p.set_defaults(fn=cmd_show)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
