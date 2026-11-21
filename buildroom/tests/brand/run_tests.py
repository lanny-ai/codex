#!/usr/bin/env python3
"""Brand Kit: taking in a member's own brand, building one, the checks, the board, the lock and the wiring.

Usage:  python3 buildroom/tests/brand/run_tests.py
Everything runs offline. The font used here is built by the test itself (a few rectangles), so no font file is shipped.
"""
import sys
sys.dont_write_bytecode = True
import json, os, re, shutil, struct, subprocess, tempfile, zlib  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / "skills/buildroom-brand-kit"
S = SK / "scripts"
sys.path.insert(0, str(S))
import brandlib as bl  # noqa: E402
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {str(detail)[:400]}" if detail and not ok else ""))


def run(*a, cwd=None):
    r = subprocess.run([sys.executable, "-B", str(S / "brandkit.py"), *map(str, a)], capture_output=True, text=True, cwd=cwd,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return r.returncode, r.stdout + r.stderr


# ---------------------------------------------------------------- fixtures made by the test
def make_png(path, w, h, rgba, alpha=True):
    px = bytes(rgba if alpha else rgba[:3])
    raw = b"".join(b"\x00" + px * w for _ in range(h))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6 if alpha else 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def make_png_padded(path, w, h, box, rgba=(11, 79, 108, 255)):
    """A transparent PNG whose picture fills only `box` (x0, y0, x1, y1), like a logo in the middle of a big canvas."""
    x0, y0, x1, y1 = box
    blank, full = bytes(4) * w, bytes(4) * x0 + bytes(rgba) * (x1 - x0) + bytes(4) * (w - x1)
    raw = b"".join(b"\x00" + (full if y0 <= y < y1 else blank) for y in range(h))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def make_ttf(path, chars="NORTHLINEBKPGnorthlinebkpg &HP", family="Testface"):
    """A real, tiny TrueType font: every letter is a rectangle (a different width each), which is all the outline code needs."""
    chars = sorted(set(chars))
    glyphs = [b""]                                                   # glyph 0: empty .notdef
    adv = [500]
    for i, ch in enumerate(chars):
        if ch == " ":
            glyphs.append(b""); adv.append(250)
            continue
        w = 300 + 20 * (i % 9)
        pts = [(50, 0), (50, 700), (50 + w, 700), (50 + w, 0)]
        g = struct.pack(">hhhhh", 1, 50, 0, 50 + w, 700) + struct.pack(">H", 3) + struct.pack(">H", 0) + bytes([1, 1, 1, 1])
        xs = [pts[0][0]] + [pts[k][0] - pts[k - 1][0] for k in range(1, 4)]
        ys = [pts[0][1]] + [pts[k][1] - pts[k - 1][1] for k in range(1, 4)]
        g += b"".join(struct.pack(">h", v) for v in xs) + b"".join(struct.pack(">h", v) for v in ys)
        glyphs.append(g + b"\x00" * (-len(g) % 4)); adv.append(w + 100)
    glyf, loca, off = b"", [], 0
    for g in glyphs:
        loca.append(off); glyf += g; off += len(g)
    loca.append(off)
    loca_t = b"".join(struct.pack(">I", o) for o in loca)
    n = len(glyphs)
    head = struct.pack(">IIIIHHQQhhhhHHhhh", 0x00010000, 0x00010000, 0, 0x5F0F3CF5, 0, 1000, 0, 0, 0, 0, 1000, 800, 0, 8, 2, 1, 0)
    hhea = struct.pack(">IhhhHhhhhhhhhhhhH", 0x00010000, 800, -200, 0, 1000, 0, 0, 1000, 1, 0, 0, 0, 0, 0, 0, 0, n)
    maxp = struct.pack(">IH", 0x00010000, n) + b"\x00" * 26
    hmtx = b"".join(struct.pack(">Hh", a, 50) for a in adv)
    codes = [ord(c) for c in chars]
    segs = [(c, c, (i + 1) - c) for i, c in enumerate(codes)] + [(0xFFFF, 0xFFFF, 1)]
    sc = len(segs)
    sub = struct.pack(">HHHHHHH", 4, 16 + 8 * sc, 0, sc * 2, 0, 0, 0)
    sub += b"".join(struct.pack(">H", e) for _, e, _ in segs) + struct.pack(">H", 0)
    sub += b"".join(struct.pack(">H", s) for s, _, _ in segs) + b"".join(struct.pack(">h", ((d + 32768) % 65536) - 32768) for _, _, d in segs)
    sub += b"\x00\x00" * sc
    cmap = struct.pack(">HHHHI", 0, 1, 3, 1, 12) + sub
    nm = family.encode("utf-16-be")
    name = struct.pack(">HHH", 0, 1, 18) + struct.pack(">6H", 3, 1, 0x409, 1, len(nm), 0) + nm
    tables = {b"cmap": cmap, b"glyf": glyf, b"head": head, b"hhea": hhea, b"hmtx": hmtx, b"loca": loca_t, b"maxp": maxp, b"name": name}
    out = struct.pack(">IHHHH", 0x00010000, len(tables), 128, 3, 0)
    pos = 12 + 16 * len(tables)
    body = b""
    for tag in sorted(tables):
        d = tables[tag] + b"\x00" * (-len(tables[tag]) % 4)
        out += struct.pack(">4sIII", tag, 0, pos + len(body), len(tables[tag]))
        body += d
    Path(path).write_bytes(out + body)


COL = {"bg": "#ffffff", "surface": "#f4f5f3", "ink": "#16211c", "muted": "#56605b", "accent": "#b3261e", "accent_ink": "#ffffff", "line": "#d5d9d6"}
SAMPLE = {"headline": "Know what your business *really* made last month.", "body": "Monthly bookkeeping for owner-run trades firms.",
          "cta": "Book a 20-minute call", "person": "Dana Whitfield", "role": "Owner"}


def made_kit(**over):
    k = {"name": "Northline Bookkeeping", "source": "created", "direction": "Ledger", "audience": "50plus", "sample": SAMPLE,
         "palette": [{"name": "Ledger Ink", "hex": "#16211c", "role": "text and logo"}, {"name": "Rule Red", "hex": "#b3261e", "role": "one button"}],
         "colors": dict(COL),
         "fonts": {"head": {"family": "Testface", "weight": 700, "files": [{"src": "fonts/Testface-700.ttf", "weight": 700}], "license": "ofl"},
                   "body": {"family": "Arial", "license": "system"}},
         "logo": {"kind": "wordmark", "text": "Northline", "descriptor": "Bookkeeping", "mark": {"letters": "N", "shape": "square"}},
         "shape": {"radius_px": 2}, "dos": ["One red thing per page"], "donts": ["Nothing that looks like a bank"],
         "photo": {"source": "own", "rules": "Dana's own photos."}, "confirmed": {"colors": True, "fonts": True, "logo": True}}
    k.update(over)
    return k


def main():
    rd = lambda p: (ROOT / p).read_text(encoding="utf-8")  # noqa: E731
    work = Path(tempfile.mkdtemp(prefix="buildroom-brand-tests-"))
    try:
        body(rd, work)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    return 0 if all(RESULTS) else 1


def body(rd, work):
    # ---- colour maths ----
    check("contrast: black on white is 21:1", bl.contrast("#000", "#fff") == 21.0)
    check("contrast: a faint grey fails 4.5:1 and the nearest passing shade is found",
          bl.contrast("#999999", "#ffffff") < 4.5 and bl.contrast(bl.shade_to_contrast("#999999", "#ffffff"), "#ffffff") >= 4.5)
    check("shade: on a dark ground the shade goes lighter", bl.luminance(bl.shade_to_contrast("#333333", "#101010")) > bl.luminance("#333333"))
    roles, changed = bl.propose_roles(["#12263f", "#e0a526", "#f4f1ea"])
    check("roles: every proposed pairing passes its floor", not bl.contrast_problems(roles), roles)
    check("roles: a brand colour too faint for a button keeps its place and another carries the button, and the member is told",
          roles["accent"] == "#12263f" and "#e0a526" in changed.get("accent", "") and "stays in the brand" in changed["accent"], changed)
    check("roles: the brand's own light colour is the page, and its dark colour is the text", roles["bg"] == "#f4f1ea" and roles["ink"] == "#12263f")
    roles2, changed2 = bl.propose_roles(["#0a7d5a"])
    check("roles: one colour gives a full, passing set, and every added shade is listed", not bl.contrast_problems(roles2)
          and {"ink", "bg", "surface", "muted", "line"} <= set(changed2), changed2)
    roles3, _ = bl.propose_roles(["#ff5a1f", "#1b1b1b"], dark=True)
    check("roles: a dark brand gets a dark page and light text", bl.is_dark(roles3["bg"]) and not bl.contrast_problems(roles3), roles3)
    check("tells: cream and purple are recognised, white and navy are not", bl.is_cream("#f6efe0") and bl.is_purple("#7c3aed")
          and not bl.is_cream("#ffffff") and not bl.is_purple("#12263f"))

    # ---- reading files ----
    d = work / "intake"
    (d / "logo").mkdir(parents=True)
    make_png(d / "logo/big.png", 1400, 300, (11, 79, 108, 255))
    make_png(d / "logo/small.png", 420, 100, (11, 79, 108), alpha=False)
    (d / "logo/vec.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 80"><text font-family="Lora" fill="#0b4f6c">Harbor</text><rect fill="#f26a4b"/><rect fill="#0b4f6c"/></svg>')
    (d / "site.css").write_text("body{color:#04202b;background:#fff;font-family:'Lora',serif}a{color:#f26a4b}h1{color:#04202b}.x{color:rgb(4, 32, 43)}")
    (d / "guide.pdf").write_bytes(b"%PDF-1.4")
    (d / "logo.ai").write_bytes(b"%!PS-Adobe")
    info = bl.png_info((d / "logo/big.png").read_bytes())
    check("png: size and transparency are read", info["width"] == 1400 and info["alpha"] is True and bl.png_info((d / "logo/small.png").read_bytes())["alpha"] is False)
    cols = bl.png_colours((d / "logo/big.png").read_bytes()) if hasattr(bl, "png_colours") else bl.png_colors((d / "logo/big.png").read_bytes())
    check("png: the dominant colour is found", cols and cols[0]["hex"] == "#0b4f6c", cols)
    before = sorted(p.name for p in d.rglob("*"))
    code, out = run("read", "logo/big.png", "logo/small.png", "logo/vec.svg", "site.css", "guide.pdf", "logo.ai", "missing.png", cwd=d)
    r = {x["file"]: x for x in json.loads(out)["files"]}
    check("read: reports each file and writes nothing", code == 0 and json.loads(out)["wrote"] == "nothing" and sorted(p.name for p in d.rglob("*")) == before)
    check("read: a vector logo gives its colours, its font and a live-text warning", r["logo/vec.svg"]["live_text"] is True
          and r["logo/vec.svg"]["colors"][0]["hex"] == "#0b4f6c" and "Lora" in r["logo/vec.svg"]["fonts"], r["logo/vec.svg"])
    check("read: a stylesheet gives colours by use and the typeface", r["site.css"]["colors"][0]["hex"] == "#04202b" and r["site.css"]["fonts"] == ["Lora"], r["site.css"])
    check("read: a PDF guide is handed back to the session to read, a design file to the designer, a missing file is named",
          "read this yourself" in r["guide.pdf"]["note"] and "SVG or PNG" in r["logo.ai"]["note"] and r["missing.png"]["error"] == "not found")
    code, out = run("roles", "0b4f6c", "f26a4b", cwd=d)
    rr = json.loads(out)
    check("roles command: seven colours, the contrast of each pairing, and what to tell the member", code == 0 and set(rr["colors"]) == set(bl.COLOR_KEYS)
          and min(rr["contrast"].values()) >= 3.0 and "not_the_brands_own" in rr and "Show the member" in rr["say"], rr)

    # ---- a real font, made here ----
    c = work / "made/Design/Brand"
    (c / "fonts").mkdir(parents=True)
    make_ttf(c / "fonts/Testface-700.ttf")
    f = bl.open_font(c / "fonts/Testface-700.ttf")
    check("font: a TrueType file is read (name, letters, widths)", f is not None and f.name() == "Testface" and f.has("N") and not f.has("Z") and f.upm == 1000)
    pd, w, box = f.path("NO", 100, 0, 0, 0.1) if f else ("", 0, (0, 0, 0, 0))
    check("font: letters become closed vector paths with a true size", pd.count("M") == 2 and pd.count("Z") == 2 and box[1] == -70 and box[3] == 0 and w > 60, (pd, w, box))
    pd2, w2, _ = f.path("NO", 100, 0, 0, 0.1, {"NO": -0.2}) if f else ("", 0, 0)
    check("font: a kerning pair moves the second letter", round(w - w2, 2) == 20.0, (w, w2))
    (c / "fonts/not-a-font.ttf").write_bytes(b"wOF2" + b"\x00" * 64)
    check("font: a file that cannot be outlined is refused quietly, not with a crash", bl.open_font(c / "fonts/not-a-font.ttf") is None)

    # ---- check ----
    K = c / "kit.json"

    def chk(kit):
        K.write_text(json.dumps(kit))
        code, out = run("check", K)
        return code, out
    code, out = chk(made_kit())
    check("check: a complete, confirmed kit is ready to lock", code == 0 and "Ready to lock" in out and "FIX" not in out, out)
    code, out = chk(made_kit(confirmed={"colors": True}))
    check("check: nothing locks until the member has said yes to colours, typefaces and logo", code == 1 and "has not said yes to: fonts, logo" in out, out)
    code, out = chk(made_kit(colors={**COL, "muted": "#9aa39f"}))
    check("check: a text colour that is too faint is a FIX, with the shade that passes", code == 1 and "quiet text #9aa39f" in out and "needs 4.5:1" in out
          and re.search(r"#[0-9a-f]{6} passes", out), out)
    code, out = chk(made_kit(logo={"kind": "wordmark", "text": "Apex Ledgers"}))
    check("check: a wordmark never sets a name that is not the business's", code == 1 and 'says "Apex Ledgers"' in out and "never invents" in out, out)
    code, out = chk(made_kit(fonts={"head": {"family": "Testface", "weight": 700}, "body": {"family": "Arial", "license": "system"}}))
    check("check: a wordmark needs its font file before the lock", code == 1 and "needs its font file" in out, out)
    code, out = chk(made_kit(sample={**SAMPLE, "headline": "Your headline here"}))
    check("check: placeholder words are refused", code == 1 and "placeholder text" in out, out)
    code, out = chk(made_kit(type={"base_px": 15}))
    check("check: body text under the floor for this audience is a FIX", code == 1 and "15px" in out and "needs 18px" in out, out)
    code, out = chk(made_kit(colors={**COL, "bg": "#f6efe0", "surface": "#efe6d2", "accent": "#7c3aed"},
                             fonts={"head": {"family": "Inter", "weight": 700, "license": "google"}, "body": {"family": "Arial", "license": "system"}},
                             logo={"kind": "none"}))
    check("check: in a new brand, a cream page, a purple accent and a default typeface are each flagged to look at",
          out.count("tell:") == 3 and "cream" in out and "purple" in out and "Inter is a default typeface" in out, out)
    make_png(c / "small.png", 420, 100, (11, 79, 108), alpha=False)
    make_png(c / "big.png", 1400, 300, (11, 79, 108, 255))
    (c / "old.ai").write_bytes(b"x")
    up = dict(name="Harbor & Pine", source="uploaded", palette=[{"name": "Harbor Blue", "hex": "#0b4f6c", "from": "brand guide"}],
              colors={**COL, "ink": "#04202b", "accent": "#0b4f6c"}, fonts={"head": {"family": "Georgia", "license": "system"}, "body": {"family": "Arial", "license": "system"}})
    code, out = chk(made_kit(**up, logo={"kind": "files", "on_light": "small.png"}))
    check("intake: a logo too small to use is a FIX, with what to ask for", code == 1 and "only 420 pixels wide" in out and "ask for the original" in out, out)
    code, out = chk(made_kit(**up, logo={"kind": "files", "on_light": "old.ai"}))
    check("intake: a design file is refused, with what to ask for", code == 1 and "SVG or PNG export" in out, out)
    code, out = chk(made_kit(**up, logo={"kind": "files", "on_light": "big.png"}))
    check("intake: a usable logo locks, and what is missing is said plainly", code == 0 and "no version for dark backgrounds" in out and "no small mark" in out, out)
    check("intake: a working colour that is not the brand's own is pointed out", "not one of the brand's own colors: ink #04202b" in out, out)
    code, out = chk(made_kit(**{**up, "palette": []}, logo={"kind": "files", "on_light": "big.png"}))
    check("intake: the brand's own colours must be recorded as given", code == 1 and "palette: list the brand's own colors" in out, out)
    code, out = chk(made_kit(fonts={"head": {"family": "Testface", "weight": 700, "files": ["fonts/Testface-700.ttf"]}, "body": {"family": "Arial", "license": "system"}}))
    check("check: an unconfirmed font licence is raised with the member", code == 0 and "license for Testface is not confirmed" in out, out)

    # ---- the board ----
    D = c / "directions.json"
    base = {k: v for k, v in made_kit().items() if k in ("palette", "colors", "fonts", "logo", "shape")}
    d1 = {**base, "name": "Ledger", "idea": "Ink on white, one line of red.", "from": "The ledger pages you showed."}
    d2 = {**base, "name": "Workshop", "idea": "A plain sign on deep green.", "from": "Your clients' vans.",
          "colors": {"bg": "#f6f6f2", "surface": "#eceee6", "ink": "#12281f", "muted": "#4f5d55", "accent": "#0f6b47", "accent_ink": "#ffffff", "line": "#cfd5cc"},
          "logo": {"kind": "wordmark", "text": "NORTHLINE", "case": "upper", "layout": "mark-text", "mark": {"letters": "N", "shape": "circle"}}}
    d3 = {**base, "name": "Night", "idea": "Calm navy with a brass line.", "from": "The brass plate on your door.",
          "colors": {"bg": "#10192b", "surface": "#1a2740", "ink": "#f3f1ea", "muted": "#a9b3c4", "accent": "#d9a441", "accent_ink": "#10192b", "line": "#33415c"},
          "logo": {"kind": "wordmark", "text": "northline", "case": "lower", "mark": {"letters": "n", "shape": "none", "case": "lower"}}}

    def board(dirs, sample=SAMPLE, business="Northline Bookkeeping"):
        D.write_text(json.dumps({"business": business, "audience": "50plus", "sample": sample, "directions": dirs}))
        return run("board", D, c / "directions.html")
    code, out = board([d1, d2, d3])
    html = (c / "directions.html").read_text() if code == 0 else ""
    check("board: three directions are written to one page", code == 0 and "3 directions" in out and all(x in html for x in ("Ledger", "Workshop", "Night")), out)
    check("board: the member's own words are on it, with the marked word carried by the accent", "Know what your business <b>really</b> made last month." in html
          and "Monthly bookkeeping for owner-run trades firms." in html and "Book a 20-minute call" in html)
    check("board: every direction is shown in use: both grounds, a post image both ways, a web page, a signature and the small-size test",
          html.count('class="post"') == 6 and html.count('class="site"') == 3 and html.count('class="sig"') == 3 and html.count("browser-tab size") == 3)
    check("board: the logo is real vector shapes, not live text", html.count("<path d=") >= 12 and "<text" not in html)
    check("board: nothing on it is decoration: no gradient, glow, blur or shadow effect", not re.search(r"gradient|blur\(|text-shadow|drop-shadow|backdrop-filter", html))
    check("board: it says no picture symbol was generated, and why", "No picture symbol was generated" in html and "designer" in html)
    code, out = board([d1, {**d1, "name": "Ledger Two", "colors": {**COL, "accent": "#b3261f"}}])
    check("board: two directions that are the same idea twice are refused", code == 1 and "the same idea twice" in out, out)
    code, out = board([d1, d2], sample={"headline": "", "body": ""})
    check("board: it will not run on placeholder or missing words", code == 1 and "sample.headline" in out and "never on placeholder text" in out, out)
    code, out = board([{**d1, "idea": "", "from": ""}, d2])
    check("board: every direction says why it suits the business and where it comes from", code == 1 and "idea:" in out and "from:" in out, out)
    code, out = board([d1])
    check("board: one direction is not a choice", code == 1 and "two to four" in out, out)
    code, out = board([{**d1, "logo": {"kind": "wordmark", "text": "Apex"}}, d2])
    check("board: a direction cannot rename the business", code == 1 and 'says "Apex"' in out, out)

    # ---- the lock ----
    SYS = c.parent / "System"
    K.write_text(json.dumps(made_kit(confirmed={})))
    code, out = run("lock", K, "--out", SYS)
    check("lock: an unconfirmed kit is refused and nothing is written", code != 0 and "has not said yes" in out and not SYS.exists(), out)
    K.write_text(json.dumps(made_kit()))
    code, out = run("lock", K, "--out", SYS)
    t = json.loads((SYS / "tokens.json").read_text()) if code == 0 else {}
    check("lock: the Design System, the logo files and the brand sheet are written", code == 0
          and all((SYS / n).is_file() for n in ("tokens.json", "tokens.css", "slides.json", "design-system.md", "fonts.md"))
          and all((c / "logo" / n).is_file() for n in ("wordmark.svg", "wordmark-on-dark.svg", "mark.svg", "mark-on-dark.svg")) and (c / "Brand Kit.html").is_file(), out)
    check("lock: tokens use the shared schema, so every other session can read them", t.get("schema") == "buildroom-design/1" and t.get("version") == 1
          and t["color"] == COL and t["font"]["head"]["family"] == "Testface" and t["type"]["base_px"] == 18 and t["radius_px"] == 2
          and t["vars"]["--c-accent"] == "#b3261e" and "--font-head" in t["vars"], t)
    b = t.get("brand", {})
    check("lock: the brand block names the logo for each ground, the font files and the reverse colours, relative to the system folder",
          b.get("source") == "created" and b["logo"]["on_light"] == "../Brand/logo/wordmark.svg" and b["logo"]["mark_on_dark"] == "../Brand/logo/mark-on-dark.svg"
          and b["font_files"]["head"] == [{"src": "../Brand/fonts/Testface-700.ttf", "weight": 700}] and b["reverse"]["bg"] == "#16211c"
          and (SYS / b["logo"]["on_dark"]).resolve().is_file() and b["sheet"] == "../Brand/Brand Kit.html", b)
    wm, wd, mk = ((c / "logo" / n).read_text() for n in ("wordmark.svg", "wordmark-on-dark.svg", "mark.svg"))
    check("logo: drawn as outlines in the brand's colours, cropped tight, with no live text and no effects", "<path d=" in wm and "<text" not in wm
          and 'fill="#16211c"' in wm and 'fill="#ffffff"' in wd and "viewBox=" in wm and not re.search(r"filter|gradient|stroke=", wm + mk))
    check("logo: the small mark is a square in the accent with the letter in its text colour", 'viewBox="0 0 100 100"' in mk and 'fill="#b3261e"' in mk and 'fill="#ffffff"' in mk and "<rect" in mk)
    sheet = (c / "Brand Kit.html").read_text()
    check("sheet: logo, color, type, the kit in use, rules and files are all there", all(f"<h2>{h}</h2>" in sheet for h in ("Logo", "Color", "Type", "In use", "Photos and rules", "Files")))
    check("sheet: every colour pairing is shown with its measured contrast", sheet.count("needs 4.5:1") == 5 and "Quiet text on a panel" in sheet and "needs 3.0:1" in sheet and "16.56:1" in sheet)
    check("sheet: the member's rules and words are on it, in American spelling", "One red thing per page" in sheet and "Nothing that looks like a bank" in sheet
          and "Dana&#x27;s own photos" not in sheet and "Dana's own photos." in sheet and "colour" not in sheet and "licence" not in sheet)
    check("sheet: the logo rules are stated, and a designer's brief is given instead of a generated symbol", "clear space" in sheet and "Never stretch it" in sheet
          and "If you want a drawn symbol later" in sheet and "trademark professional" in sheet)
    check("sheet: no decoration", not re.search(r"gradient|blur\(|text-shadow|drop-shadow|backdrop-filter", sheet))
    css = (SYS / "tokens.css").read_text()
    check("tokens.css: the working colours, the typefaces and the reverse ground", "--c-accent: #b3261e;" in css and "--font-head: 'Testface'" in css and ".reverse" in css
          and "--c-bg: #16211c;" in css and "prefers-reduced-motion" in css)
    md = (SYS / "design-system.md").read_text()
    check("design-system.md: logo files, brand colours, working colours and the never-generate rule", "../Brand/logo/wordmark.svg" in md and "**Ledger Ink** `#16211c`" in md
          and "| Accent (buttons, links) | `#b3261e` |" in md and "Never a generated picture logo" in md and "Clear space" in md)
    check("fonts.md: where each typeface's files are and what its licence is", "fonts/Testface-700.ttf" in (SYS / "fonts.md").read_text() and "SIL Open Font License" in (SYS / "fonts.md").read_text()
          and "comes with the computer" in (SYS / "fonts.md").read_text())
    sl = json.loads((SYS / "slides.json").read_text())
    check("slides.json: a font every computer has, and an accent that reads on slides", sl["font"] in ("Arial", "Georgia") and sl["theme"] == "light" and "--accent" in sl["flags"])
    code, out = run("section", "--system", SYS)
    sec = json.loads(out) if code == 0 else {}
    check("section: the §22 lines and the §18 pointer", code == 0 and sec["section_22"][0].startswith("- **Brand kit** (yours or made here") and "made here" in sec["section_22"][0]
          and any("Testface / Arial" in x for x in sec["section_22"]) and sec["section_18_brand_kit"] == "see §22 (Design System v1)", sec)
    check("section: paths are written as the Business File sees them, and the directions tried are named", "Design/Brand/logo/wordmark.svg" in sec["section_22"][0]
          and "../Brand" not in " ".join(sec["section_22"]) and "Design/Brand/Brand Kit.html" in sec["section_22"][0]
          and any(x.startswith("- **Directions tried**") and "Ledger, Workshop" in x and "chosen Ledger" in x for x in sec["section_22"]), sec)
    code, out = run("show", "--system", SYS)
    check("show: the locked kit in brief", code == 0 and json.loads(out)["brand_kit"] is True and json.loads(out)["source"] == "created")
    # a second lock keeps the first, and keeps what the Website Design Studio set
    t["hero"] = "stacked"; t["refs"] = ["T-001"]; t["attrs"] = {"data-hero": "stacked"}
    (SYS / "tokens.json").write_text(json.dumps(t))
    K.write_text(json.dumps(made_kit(colors={**COL, "accent": "#a11d16"})))
    code, out = run("lock", K, "--out", SYS)
    t2 = json.loads((SYS / "tokens.json").read_text())
    check("re-lock: the earlier system is kept as a version, and the page settings survive", code == 0 and t2["version"] == 2 and (SYS / "tokens-v1.json").is_file()
          and t2["color"]["accent"] == "#a11d16" and t2["hero"] == "stacked" and t2["refs"] == ["T-001"], out)
    t3v = t2["version"] + 2          # two more locks follow before the preview test reads the version
    # a mark with no shape, a mark-text layout, and a font that cannot be outlined
    K.write_text(json.dumps(made_kit(logo={"kind": "wordmark", "text": "NORTHLINE", "case": "upper", "layout": "mark-text", "mark": {"letters": "N", "shape": "circle"}})))
    code, out = run("lock", K, "--out", SYS)
    wm = (c / "logo/wordmark.svg").read_text()
    check("logo: the mark-and-name layout puts a circle mark beside the name", code == 0 and 'rx="' in wm and wm.count("<path d=") >= 2, out)
    shutil.copy(c / "fonts/not-a-font.ttf", c / "fonts/Web.woff2")
    K.write_text(json.dumps(made_kit(fonts={"head": {"family": "Webface", "weight": 700, "files": ["fonts/Web.woff2"], "license": "bought"}, "body": {"family": "Arial", "license": "system"}})))
    code, out = run("lock", K, "--out", SYS)
    check("logo: a font that cannot be outlined still gives a logo, and the member is told it carries live text", code == 0 and "<text" in (c / "logo/wordmark.svg").read_text()
          and "live text" in out and "live text, so they need the font installed" in (c / "Brand Kit.html").read_text() and "bought font" in out, out)

    # ---- intake lock: the member's own files, nothing redrawn ----
    u = work / "own/Design/Brand"
    (u / "logo").mkdir(parents=True)
    make_png(u / "logo/harbor.png", 1400, 300, (11, 79, 108, 255))
    raw = (u / "logo/harbor.png").read_bytes()
    UK = u / "kit.json"
    UK.write_text(json.dumps(made_kit(**up, logo={"kind": "files", "on_light": "logo/harbor.png"}, direction=None)))
    code, out = run("lock", UK, "--out", u.parent / "System")
    ut = json.loads((u.parent / "System/tokens.json").read_text()) if code == 0 else {}
    us = (u / "Brand Kit.html").read_text() if code == 0 else ""
    check("intake lock: the member's logo file is used as it is and never changed", code == 0 and (u / "logo/harbor.png").read_bytes() == raw
          and ut["brand"]["logo"] == {"kind": "files", "on_light": "../Brand/logo/harbor.png"} and ut["brand"]["source"] == "uploaded"
          and not (u / "logo/wordmark.svg").exists(), out)
    check("intake lock: the logo is never shown on a ground it was not made for; the name stands in and the gap is stated", "There is no logo file for dark backgrounds yet" in us
          and "Harbor &amp; Pine</span>" in us and us.count("logo/harbor.png") >= 2 and "only on light backgrounds until" in us and "no small square mark yet" in us, us[:0])
    check("intake lock: the sheet says the brand is the member's own, and offers no designer brief for a symbol", "Your own brand, taken in and checked" in us
          and "If you want a drawn symbol later" not in us)
    check("intake lock: design-system.md tells other sessions the dark-ground logo is missing", "no dark-ground version" in (u.parent / "System/design-system.md").read_text())

    # ---- found by the trial run: the preview, a typed mark, padded logo pictures, mixes, and the gaps in the checks ----
    K.write_text(json.dumps(made_kit(confirmed={})))
    code, out = run("preview", K, c / "Preview.html")
    pv = (c / "Preview.html").read_text() if code == 0 else ""
    check("preview: the member can be shown the sheet before saying yes, clearly marked as a draft, and nothing is locked", code == 0 and "Nothing is locked yet" in pv
          and "<h2>Logo</h2>" in pv and "Nothing is locked" in out and json.loads((SYS / "tokens.json").read_text())["version"] == t3v, out)
    check("sheet: the color table says which colors are the member's own and which were added", "your brand color" in pv and "a working shade added for this job" in pv)
    code, out = chk(made_kit(logo={"kind": "wordmark", "text": "Northline", "descriptor": "Trusted since 1998"}))
    check("check: a logo's second line is the rest of the name, never a tagline, a year or a claim", code == 1 and '"Trusted since 1998" is not part of the business name' in out, out)
    code, out = chk(made_kit(colors={**COL, "ink": "#12263f", "accent": "#1b3a5c", "muted": "#4a5a6c"}))
    check("check: an accent too close to the text color is pointed out, because a marked word would not show", "close to the text color" in out, out)
    code, out = chk(made_kit(colors={**COL, "surface": "#d9dcd9", "muted": "#6b746f"}))
    check("check: quiet text is measured on panels as well as on the page", code == 1 and "quiet text #6b746f on panels and cards" in out, out)
    code, out = board([d1, {**d1, "name": "Ledger in green", "idea": "The first one's lettering in the green.", "from": "Your mix.", "colors": d2["colors"]}])
    code2, out2 = (lambda: (D.write_text(D.read_text()), run("board", D, c / "mix.html", "--mix"))[1])()
    check("board: a mix that differs from its original on one thing is refused in round one and allowed on a mix board", code == 1 and "same idea twice" in out and code2 == 0, out + out2)
    rr2 = json.loads(run("roles", "0b4f6c", "f26a4b", "eef2f3", "--page", "eef2f3", "--accent", "f26a4b")[1])
    rr3 = json.loads(run("roles", "0b4f6c", "f26a4b", "eef2f3", "--page", "ffffff")[1])
    check("roles: a job the brand guide states for a color is honored, and the panel is a quiet neutral, not a tint of the accent", rr2["colors"]["bg"] == "#eef2f3"
          and rr3["colors"]["bg"] == "#ffffff" and bl.is_neutral(rr3["colors"]["surface"]) and min(rr3["contrast"].values()) >= 3.0, (rr2, rr3))
    # the member's own logo in the middle of a big empty canvas
    make_png_padded(u / "logo/padded.png", 1600, 400, (40, 140, 1016, 260))
    check("png: the picture inside an empty canvas is measured", bl.png_content_box((u / "logo/padded.png").read_bytes()) == (0.025, 0.35, 0.635, 0.65))
    shutil.copytree(c / "fonts", u / "fonts")
    own = made_kit(**{**up, "fonts": {"head": {"family": "Testface", "weight": 700, "files": [{"src": "fonts/Testface-700.ttf", "weight": 700}], "license": "ofl"},
                                      "body": {"family": "Arial", "license": "system"}}}, direction=None,
                   logo={"kind": "files", "on_light": "logo/padded.png", "mark": {"letters": "H&P", "shape": "square"}, "rules": ["Always on white. Never on photos."]})
    UK.write_text(json.dumps(own))
    code, out = run("check", UK)
    check("intake: wide empty margins around a logo are reported, and a typed mark is flagged as new for the member's yes", code == 0 and "wide empty margins" in out
          and "fills 61% of the width" in out and "this small mark is new" in out, out)
    padded_raw = (u / "logo/padded.png").read_bytes()
    code, out = run("lock", UK, "--out", u.parent / "System")
    ut2 = json.loads((u.parent / "System/tokens.json").read_text()) if code == 0 else {"brand": {"logo": {}}}
    us2 = (u / "Brand Kit.html").read_text() if code == 0 else ""
    lg2 = ut2["brand"]["logo"]
    check("intake lock: a padded logo is shown cropped to its lettering, the crop is passed on, and the file is untouched", code == 0 and lg2.get("trim") == {"on_light": [35.0, 36.5, 35.0, 2.5]}
          and "object-view-box:inset(35.0% 36.5% 35.0% 2.5%)" in us2 and (u / "logo/padded.png").read_bytes() == padded_raw, lg2)
    check("intake lock: the typed mark is written beside the member's logo, as vector shapes, and labeled as made here", lg2.get("typed_mark") is True
          and lg2.get("mark_on_light") == "../Brand/logo/typed-mark.svg" and "<path d=" in (u / "logo/typed-mark.svg").read_text() and lg2["on_light"] == "../Brand/logo/padded.png"
          and "The small mark is new" in us2 and "Your logo itself is unchanged" in us2, lg2)
    check("intake lock: the rule that came with the member's logo comes first, and the default that contradicts it is dropped", us2.index("Always on white. Never on photos.") < us2.index("Keep clear space")
          and "busy photo" not in us2 and "The member's own rule: Always on white. Never on photos." in (u.parent / "System/design-system.md").read_text())
    UK.write_text(json.dumps({**own, "logo": {"kind": "wordmark", "text": "Harbor & Pine"}}))
    code, out = run("check", UK)
    check("intake: a member's own logo is never replaced by a typeset name", code == 1 and "has their own logo" in out and "would replace it" in out, out)

    # ---- the scripts themselves ----
    src = {n: (S / n).read_text() for n in ("brandkit.py", "brandlib.py", "brandpages.py")}
    std = {"argparse", "base64", "colorsys", "json", "os", "re", "shutil", "struct", "sys", "tempfile", "zlib", "urllib.error", "urllib.parse", "urllib.request",
           "datetime", "pathlib", "brandlib", "brandpages"}
    used = set()
    for s in src.values():
        for m in re.finditer(r"^\s*(?:import|from)\s+([\w.]+(?:\s*,\s*[\w.]+)*)", s, re.M):
            used |= {x.strip() for x in m.group(1).split(",")}
    check("scripts: standard library only", used <= std, used - std)
    check("scripts: only the fonts command goes online, and only to Google Fonts", "urlopen" not in src["brandlib.py"] + src["brandpages.py"]
          and set(re.findall(r"https://([\w.]+)", src["brandkit.py"])) <= {"fonts.googleapis.com", "fonts.gstatic.com", "fonts.google.com", "fonts"}
          and src["brandkit.py"].count("urlopen(") == 2)
    check("scripts: no image model is ever called for a logo", not re.search(r"gen\.py|kie\.ai|openai|replicate|generate_image", "".join(src.values()), re.I))
    png = (S / "brand_png.mjs").read_text()
    check("png export: transparent copies beside the vector files, nothing online", "omitBackground: true" in png and "http" not in png.replace("xmlns", ""))
    check("png export: the drawing is opened as the page, checked to have drawn, and a failure is not reported as success", "page.goto(pathToFileURL" in png and "setContent" not in png
          and "getBBox().width > 0" in png and "process.exit(1)" in png)
    check("fonts: a designer's short name is tried under the family's current name, and the rename is reported", '" 3"' in src["brandkit.py"] and '"renamed"' in src["brandkit.py"])
    check("linkedin renderer: a padded logo picture is cropped when shown", "object-view-box:inset(" in rd("skills/buildroom-linkedin/scripts/render_linkedin.mjs") and "lg.trim" in rd("skills/buildroom-linkedin/scripts/render_linkedin.mjs"))

    # ---- the skill and the wiring ----
    sk = rd("skills/buildroom-brand-kit/SKILL.md")
    refs = {n: rd(f"skills/buildroom-brand-kit/references/{n}.md") for n in ("quality-bar", "intake", "creating", "kit-file")}
    alltext = sk + "".join(refs.values())
    check("skill: both ways in, and the phrases a member says", all(x in sk for x in ("set up my brand kit", "here is my brand kit", "I don't have a brand", "make me a logo",
                                                                                   "**They have a brand**", "**They have none.**")))
    check("skill: an existing brand is never restyled, and nothing locks without a yes", "You never restyle a brand a member already has" in sk and "Nothing is locked on a guess" in sk)
    check("skill: never a generated logo, an invented name or a trademark promise", "Never generate a logo, a symbol or an icon with an image model" in sk
          and "Never invent a business name, a tagline" in sk and "Never promise that a name or a logo can be registered" in sk)
    check("skill: every reference it names exists", all((SK / "references" / f"{n}.md").is_file() for n in refs) and all(f"references/{n}.md" in sk for n in refs))
    check("references: the tells, the floor and the review before the member sees anything", all(x in refs["quality-bar"] for x in ("Glows, blurred blobs", "Gradient text", "4.5:1", "18px or more",
                                                                                                                           "Your review before the member sees anything", "one idea in three colors")))
    check("references: intake records exactly, fills only gaps, and says what was added", "record it exactly, check it, fill only the gaps, and say what you added" in refs["intake"]
          and "never recolor, redraw, trace or regenerate" in refs["intake"] and "**Added by me:**" in refs["intake"])
    check("references: creating starts from the member's world, never from colour psychology or a favourite colour", "\"Blue means trust\" is folklore" in refs["creating"]
          and "never ask for a favorite color" in refs["creating"] and "at most three rounds" in refs["creating"].lower())
    check("references: the kit file documents every command the script has", all(f"brandkit.py {cmd}" in refs["kit-file"] for cmd in ("read", "roles", "fonts", "check", "preview", "board", "lock", "section", "show")))
    check("skill: the member sees a draft before the yes, their own headline is checked against what they refuse to claim, and their logo is never swapped out",
          "brandkit.py preview" in sk and "not a description" in sk and "*Never claim or promise*" in sk and "Never replace a member's own logo with a typeset name" in sk
          and "never replaces it" in refs["intake"] and "--mix" in refs["creating"])
    check("skill text: no em or en dashes, American spelling", "—" not in alltext and "–" not in alltext and not re.search(r"\bcolour|\blicence\b|\bfavourite", alltext))
    check("font pairings: the same vetted list the Website Design Studio uses", rd("skills/buildroom-brand-kit/assets/font-pairs.json") == rd("skills/buildroom-website-design-studio/assets/font-pairs.json"))
    tpl = rd("templates/BUILDROOM_BUSINESS_FILE.md")
    s22 = tpl[tpl.index("## 22. Design System"):tpl.index("## 23.")]
    check("template: version 1.13, §22 is built by Brand Kit and the Website Design Studio, with a Brand kit line first", "**File version:** 1.13" in tpl
          and "Built by: Brand Kit" in s22 and s22.index("- **Brand kit** (yours or made here") < s22.index("- **Taste vault**"))
    check("template: every skill's copy matches", all(rd(f"skills/{p.name}/references/business-file-template.md") == tpl
                                                     for p in (ROOT / "skills").iterdir() if (p / "references/business-file-template.md").exists()))
    spec = rd("BUSINESS-FILE-SPEC.md")
    check("spec: 1.13 records the field and the shared section", "**Version 1.13" in spec and "| 22 | Design System | Brand Kit · Website Design Studio |" in spec and "Version 1.13 adds one field to §22" in spec)
    road = rd("skills/buildroom-os/references/roadmap.md")
    check("roadmap: Brand Kit comes before anything public is made, with its phrases", "`buildroom-brand-kit`" in road and "before anything public is made" in road and "\"Set up my brand kit\"" in road)
    uni = rd("rollout/universal/CLAUDE.md")
    check("universal instructions: the look comes from the brand kit, and decoration is ruled out", "`buildroom-brand-kit`" in uni and "offer `buildroom-brand-kit` once" in uni
          and "Never add glows, gradients, pills, badges" in uni)
    check("member docs: the tool is listed", "`buildroom-brand-kit`" in rd("rollout/MEMBER-README.md") and "`buildroom-brand-kit`" in rd("README.md"))
    guide = rd("connector/guide.html")
    check("guide page: Brand Kit is a tool, and the count is forty-three", '"brand-kit","Brand Kit","Set up my brand kit"' in guide and '<span id="n1">43</span>' in guide)
    check("there are forty-three skills", len([p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists()]) == 43)
    dl = rd("skills/buildroom-website-design-studio/scripts/design_lock.py")
    wds = rd("skills/buildroom-website-design-studio/SKILL.md")
    check("website design studio: a re-lock keeps the brand block, and directions start from the kit", 'tokens["brand"] = old["brand"]' in dl and "A brand kit in §22" in wds)
    check("ad studio: the logo and fonts come from the brand kit", "`brand.logo`" in rd("skills/buildroom-ad-studio/SKILL.md"))
    rl = rd("skills/buildroom-linkedin/scripts/render_linkedin.mjs")
    check("linkedin renderer: reads the kit's brand block", "function resolveBrand" in rl and "br.reverse" in rl and "lg.on_dark" in rl)
    check("no __pycache__ written into the skill folder", not list(SK.rglob("__pycache__")))


if __name__ == "__main__":
    sys.exit(main())
