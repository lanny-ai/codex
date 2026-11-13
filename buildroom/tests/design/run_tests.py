#!/usr/bin/env python3
"""Website Design Studio tests: colour maths and the CSS reader, the PNG reader, the taste vault, the
directions board and the round cap, the tweak bar (static, and in a real browser when Playwright is
here), the lock, the go-live check (every FIX item made to fail once, every generic tell found), and
consistency and wiring across the skill.

Local only: synthetic files in a temporary folder, no network.

Usage:  python3 buildroom/tests/design/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import json, os, re, shutil, struct, subprocess, tempfile, zlib  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # buildroom/
SK = ROOT / "skills/buildroom-website-design-studio"
S, R, A, FX = SK / "scripts", SK / "references", SK / "assets", HERE / "fixtures"
PY = sys.executable
TV, DIR, TB, LOCK, CHECK = (S / n for n in ("taste_vault.py", "directions.py", "tweakbar.py", "design_lock.py",
                                             "design_check.py"))
sys.path.insert(0, str(S))
import dslib  # noqa: E402
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {str(detail)[:600]}" if detail and not ok else ""))


def run(args, cwd):
    p = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return p.returncode, p.stdout + p.stderr


def pj(out):
    try:
        return json.loads(out[out.index("{"):])
    except Exception:
        return {}


def png(path, w, h, colour, ctype=2, filt=0):
    """A solid PNG, rows encoded with the given filter type (0-4), to exercise the reader."""
    bpp = {0: 1, 2: 3, 6: 4}[ctype]
    px_ = bytes(colour[:bpp]) if ctype != 0 else bytes(colour[:1])
    rows, prev = [], bytes(w * bpp)
    for _ in range(h):
        line = px_ * w
        if filt == 0:
            enc = line
        else:
            enc = bytearray(len(line))
            for i in range(len(line)):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                if filt == 1:
                    pr = a
                elif filt == 2:
                    pr = b
                elif filt == 3:
                    pr = (a + b) >> 1
                else:
                    pp = a + b - c
                    pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                    pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
                enc[i] = (line[i] - pr) & 255
            enc = bytes(enc)
        rows.append(bytes([filt]) + enc)
        prev = line

    def ch(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
                           + ch(b"IDAT", zlib.compress(b"".join(rows))) + ch(b"IEND", b""))


def items(d):
    return {i["id"] for i in d.get("items", [])}


# ---------------------------------------------------------------- 1. colour maths and CSS
def t_dslib():
    check("contrast black on white is 21:1", dslib.contrast("#000", "#fff") == 21.0)
    check("contrast #777 on white is just under 4.5:1", 4.4 < dslib.contrast("#777777", "#ffffff") < 4.5)
    check("contrast is symmetric", dslib.contrast("#1f5c46", "#ffffff") == dslib.contrast("#ffffff", "#1f5c46"))
    check("norm_hex expands short hex", dslib.norm_hex("#abc") == "#aabbcc")
    check("norm_hex drops alpha", dslib.norm_hex("#aabbccdd") == "#aabbcc")
    check("norm_hex refuses junk", dslib.norm_hex("blue-ish") is None and dslib.norm_hex("#12") is None)
    check("cream is spotted", dslib.is_cream("#f5efe3") and dslib.is_cream("#faf6ee"))
    check("pure white and cool grey are not cream", not dslib.is_cream("#ffffff") and not dslib.is_cream("#f3f4f6"))
    check("purple is spotted", dslib.is_purple("#7c3aed") and not dslib.is_purple("#1f5c46"))
    fixed = dslib.shade_to_contrast("#9a98b0", "#ffffff", 4.5)
    check("shade_to_contrast reaches 4.5:1 on white", dslib.contrast(fixed, "#ffffff") >= 4.5, fixed)
    fixed = dslib.shade_to_contrast("#3a3a3a", "#121212", 4.5)
    check("shade_to_contrast lightens on a dark page", dslib.contrast(fixed, "#121212") >= 4.5, fixed)
    check("px reads px, rem, pt", dslib.px("18px") == 18 and dslib.px("1.125rem") == 18 and round(dslib.px("12pt")) == 16)
    check("px reads the minimum of clamp()", dslib.px("clamp(1rem, 2vw, 1.5rem)") == 16)
    check("px returns None for calc()", dslib.px("calc(1rem + 2px)") is None)
    css = ":root{--a:#111;--b:var(--a)} @media (prefers-color-scheme: dark){:root{--a:#eee}} @media (max-width:600px){.x{width:100px}}"
    rules = dslib.css_rules(css)
    check("css_rules reads rules inside @media", any(s == ".x" and "max-width" in m for s, _, m in rules))
    rv = dslib.root_vars(css)
    check("root_vars ignores the dark-mode block", rv.get("--a") == "#111", rv)
    check("resolve follows var() chains", dslib.resolve("var(--b)", rv) == "#111")
    check("resolve uses the fallback", dslib.resolve("var(--zz, 12px)", rv) == "12px")
    check("css_rules reads <style> out of a whole page", dslib.root_vars("<html><style>:root{--c-bg:#fff}</style>")
          .get("--c-bg") == "#fff")
    check("family names a colour in plain words", dslib.family("#1f5c46").endswith("green") and dslib.family("#ffffff") == "near-white")


def t_png(tmp):
    for ctype, col in ((2, (31, 92, 70)), (6, (200, 40, 40, 255)), (0, (128,))):
        for f in range(5):
            p = tmp / f"p{ctype}{f}.png"
            png(p, 24, 10, col, ctype, f)
            got = dslib.dominant_colours(p)
            want = dslib.to_hex(*(col[:3] if ctype != 0 else (col[0],) * 3))
            check(f"PNG reader: colour type {ctype}, filter {f}", got and got[0] == want, (got, want))
    jpg = tmp / "x.jpg"
    jpg.write_bytes(b"\xff\xd8\xff" + b"0" * 100)
    check("a JPEG returns no colours (read by eye) without failing", dslib.dominant_colours(jpg) == [])


# ---------------------------------------------------------------- 2. taste vault
def t_taste(tmp):
    v = tmp / "vault"
    v.mkdir()
    code, out = run([PY, TV, "init", "--vault", "missing-vault"], tmp)
    check("init refuses a vault folder that does not exist", code == 1)
    code, out = run([PY, TV, "init", "--vault", v], tmp)
    d = pj(out)
    root = v / "Design" / "Taste Vault"
    check("init makes the inbox inside the Obsidian vault", code == 0 and (root / "inbox").is_dir() and d.get("created"))
    check("init is safe to run twice", pj(run([PY, TV, "init", "--vault", v], tmp)[1]).get("created") is False)
    png(root / "inbox" / "heroes" / "a.png", 30, 20, (245, 239, 227))
    png(root / "inbox" / "b.png", 30, 20, (31, 59, 45))
    shutil.copy(root / "inbox" / "b.png", root / "inbox" / "b-copy.png")
    (root / "inbox" / "notes.txt").write_text("not an image")
    code, out = run([PY, TV, "sort", "--vault", v, "--kind", "gallery"], tmp)
    d = pj(out)
    check("sort files two references", code == 0 and len(d.get("added", [])) == 2, out)
    check("sort skips a duplicate screenshot", len(d.get("duplicates_skipped", [])) == 1)
    data = json.loads((root / "taste.json").read_text())
    colls = {r["collection"] for r in data["refs"]}
    check("an inbox sub-folder becomes a collection", "heroes" in colls and "unsorted" in colls, colls)
    check("dominant colours are read from PNGs", all(r["colours"] for r in data["refs"]))
    check("files are renamed by ID", all(Path(r["file"]).stem == r["id"] for r in data["refs"]))
    check("the inbox is emptied of images", not list((root / "inbox").rglob("*.png")))
    check("non-images stay in the inbox", (root / "inbox" / "notes.txt").exists())
    extra = tmp / "c.png"
    png(extra, 10, 10, (200, 80, 20))
    code, out = run([PY, TV, "add", "--vault", v, extra, "--kind", "niche", "--word", "warm", "--collection", "Colours"], tmp)
    check("add files a reference with a word and kind", code == 0 and pj(out).get("added") == ["T-003"], out)
    code, out = run([PY, TV, "add", "--vault", v, tmp / "nope.png"], tmp)
    check("add refuses a missing file", code == 1)
    code, out = run([PY, TV, "react", "--vault", v, "--id", "T-001", "--word", "calm", "--likes", "big photo",
                     "--dislikes", "busy footer"], tmp)
    check("react records the member's words", code == 0 and pj(out)["ref"]["likes"] == "big photo")
    code, out = run([PY, TV, "react", "--vault", v, "--id", "T-001", "--colours", "#12,zz"], tmp)
    check("react refuses colours that are not hex", code == 1)
    code, out = run([PY, TV, "react", "--vault", v, "--id", "T-002", "--collection", "pages"], tmp)
    moved = pj(out).get("ref", {}).get("file", "")
    check("react moves a reference to another collection", code == 0 and moved.startswith("collections/pages/")
          and (root / moved).exists(), out)
    code, out = run([PY, TV, "react", "--vault", v, "--id", "T-099", "--word", "x"], tmp)
    check("react refuses an unknown ID", code == 1)
    d = pj(run([PY, TV, "read", "--vault", v], tmp)[1])
    check("the gate is not ready with three references", not d["gate"]["ready"] and any("more reference" in m for m in d["gate"]["missing"]))
    check("the gate asks for the confirmed read", any("what you keep choosing" in m for m in d["gate"]["missing"]))
    for i, col in enumerate([(20, 20, 20), (240, 240, 240), (40, 90, 200)]):
        p = tmp / f"m{i}.png"
        png(p, 10, 10, col)
        run([PY, TV, "add", "--vault", v, p, "--word", f"word{i}"], tmp)
    run([PY, TV, "feedback", "--vault", v, "--direction", "Field Guide", "--text", "love the photo, hate the green"], tmp)
    code, out = run([PY, TV, "confirm", "--vault", v, "--read", "big real photos", "--read", "one bold colour"], tmp)
    check("confirm stores the read", code == 0 and pj(out)["read"] == ["big real photos", "one bold colour"])
    d = pj(run([PY, TV, "read", "--vault", v], tmp)[1])
    check("the gate is ready: six refs, one niche, words, a confirmed read", d["gate"]["ready"], d["gate"])
    check("read reports liked words", any(w == "calm" for w, _ in d["words_liked"]), d["words_liked"])
    check("read reports disliked words", any(w == "busy" for w, _ in d["words_disliked"]))
    check("read counts light and dark backgrounds", d["backgrounds"]["light"] >= 2 and d["backgrounds"]["dark"] >= 2, d["backgrounds"])
    check("read keeps direction feedback", d["direction_feedback"][-1]["text"].startswith("love the photo"))
    code, out = run([PY, TV, "sheet", "--vault", v], tmp)
    note = (root / "Taste Vault.md").read_text()
    check("sheet writes an Obsidian note with embeds", code == 0 and "![[T-001.png]]" in note and "## What I keep choosing" in note)
    sheet = (root / "contact-sheet.html").read_text()
    check("sheet writes an HTML contact sheet", "T-003" in sheet and "prefers-color-scheme:dark" in sheet)
    return v


# ---------------------------------------------------------------- 3. directions
def t_directions(tmp, vault):
    P = vault / "Design" / "landing-page"
    code, out = run([PY, DIR, "init", "--project", P, "--deliverable", "website"], tmp)
    check("init refuses an unknown deliverable", code == 1)
    code, out = run([PY, DIR, "init", "--project", P], tmp)
    d = pj(out)
    check("init defaults to a landing page for a 50+ audience", code == 0 and d["deliverable"] == "landing page"
          and d["audience"] == "50plus")
    names = ["Field Guide", "Kitchen Table", "Front Page"]
    for n in names:
        code, out = run([PY, DIR, "new", "--project", P, "--name", n, "--idea", f"{n} idea", "--for", "people who read",
                         "--refs", "t-001,T-004"], tmp)
    d = pj(out)
    starter = (P / "directions" / "r1-front-page" / "index.html").read_text()
    check("new writes a starter on the token contract", "--c-accent-ink" in starter and 'data-eyebrows="off"' in starter)
    check("the starter uses 18px for a 50+ audience", "--size-base: 18px" in starter)
    check("refs are normalised", d["direction"]["refs"] == ["T-001", "T-004"])
    code, out = run([PY, DIR, "new", "--project", P, "--name", "Front Page", "--idea", "x", "--for", "y", "--round", "1"], tmp)
    check("a duplicate name in a round is refused", code == 1)
    code, out = run([PY, DIR, "new", "--project", P, "--name", "Fourth", "--idea", "x", "--for", "y", "--round", "1"], tmp)
    check("a fourth direction in a round is refused", code == 1)
    code, out = run([PY, DIR, "board", "--project", P], tmp)
    d = pj(out)
    check("the board names unfinished directions", code == 1 and len(d["problems"]) == 3)
    good = (FX / "good.html").read_text()
    slop = (FX / "slop.html").read_text()
    for n, src in zip(["field-guide", "kitchen-table", "front-page"], [good, slop, good.replace("Retire from", "Leave")]):
        (P / "directions" / f"r1-{n}" / "index.html").write_text(src)
    img = P / "directions" / "r1-field-guide" / "img"
    img.mkdir()
    png(img / "hero.png", 8, 8, (10, 120, 90))
    (P / "directions" / "r1-field-guide" / "index.html").write_text(good.replace("img/hero.jpg", "img/hero.png"))
    code, out = run([PY, DIR, "board", "--project", P], tmp)
    d = pj(out)
    board = Path(d.get("board", "")).read_text() if d.get("board") else ""
    check("the board builds when every page is written", code == 0, out)
    check("the board shows all three side by side", board.count('class="card"') == 3)
    check("each page keeps its own folder for images (base href)", "&lt;base href=&quot;directions/r1-field-guide/&quot;" in board)
    check("the board reports generic tells per direction", "8 generic tells" in board and "no generic tells found" in board, board[:0])
    check("the board has a phone view", "Phone view" in board)
    code, out = run([PY, DIR, "board", "--project", P, "--inline", "--out", "share.html"], tmp)
    share = (P / "share.html").read_text()
    check("--inline puts local images inside the board", code == 0 and "data:image/png;base64" in share)
    check("--inline drops the file links", "Open full size" not in share)
    code, out = run([PY, DIR, "new", "--project", P, "--name", "Round two A", "--idea", "x", "--for", "y"], tmp)
    check("a full round refuses a fourth direction unless the next round is started on purpose", code == 1 and "--round 2" in out)
    for n in ("A", "B", "C"):
        run([PY, DIR, "new", "--project", P, "--name", f"Round two {n}", "--idea", "x", "--for", "y", "--round", "2"], tmp)
    d = pj(run([PY, DIR, "status", "--project", P], tmp)[1])
    check("the next round starts when asked for", [r["n"] for r in d["rounds"]] == [1, 2], d)
    run([PY, DIR, "new", "--project", P, "--name", "Round three", "--idea", "x", "--for", "y", "--round", "3"], tmp)
    code, out = run([PY, DIR, "new", "--project", P, "--name", "Round four", "--idea", "x", "--for", "y", "--round", "4"], tmp)
    check("a fourth round is refused (no slot machine)", code == 1 and "cap" in out)
    code, out = run([PY, DIR, "new", "--project", P, "--name", "Skip", "--idea", "x", "--for", "y", "--round", "5"], tmp)
    check("skipping a round is refused", code == 1)
    code, out = run([PY, DIR, "pick", "--project", P, "--name", "field guide", "--mix", "the headline of Front Page"], tmp)
    d = pj(out)
    check("pick finds a direction in an earlier round", code == 0 and d["picked"]["round"] == 1, out)
    check("pick copies the page and its images", (P / "page" / "index.html").exists() and (P / "page" / "img" / "hero.png").exists())
    code, out = run([PY, DIR, "pick", "--project", P, "--name", "Front Page"], tmp)
    check("picking again keeps the earlier page", code == 0 and any(x.name.startswith("page-before-") for x in P.iterdir()))
    run([PY, DIR, "pick", "--project", P, "--name", "Field Guide"], tmp)
    code, out = run([PY, DIR, "pick", "--project", P, "--name", "Nope"], tmp)
    check("pick refuses an unknown name", code == 1)
    return P


# ---------------------------------------------------------------- 4. tweak bar
def t_tweakbar(tmp, P):
    bare = tmp / "bare.html"
    bare.write_text("<html><body><h1>Hi</h1><style>body{color:#111}</style></body></html>")
    code, out = run([PY, TB, "add", "--page", bare], tmp)
    check("add refuses a page not on the token contract", code == 1 and "token" in out)
    pal = tmp / "pal.json"
    pal.write_text(json.dumps([
        {"name": "Sage", "bg": "#ffffff", "surface": "#eef3f0", "ink": "#16211c", "muted": "#43524a",
         "accent": "#1f5c46", "accent_ink": "#ffffff", "line": "#cdd8d2"},
        {"name": "Dusk", "bg": "#f7f7fb", "surface": "#ebebf3", "ink": "#1c1b2e", "muted": "#9a98b0",
         "accent": "#c2410c", "accent_ink": "#ffffff", "line": "#d6d5e3"}]))
    page = P / "page" / "index.html"
    code, out = run([PY, TB, "add", "--page", page, "--palettes", pal, "--open"], tmp)
    d = pj(out)
    check("add puts the bar in", code == 0 and "buildroom-tweakbar:start" in page.read_text(), out)
    check("add offers the page's own palette first", d["palettes"][0] == "As built", d.get("palettes"))
    check("add fixes a palette that fails contrast", any("Dusk: muted" in n for n in d["palette_fixes"]))
    check("add shows only toggles the page supports", "data-eyebrows" in d["unsupported"] and "data-hero" in d["toggles_supported"])
    check("add reads the audience from design.json", d["audience"] == "50plus")
    run([PY, TB, "add", "--page", page, "--palettes", pal], tmp)
    check("adding twice leaves one bar", page.read_text().count("buildroom-tweakbar:start") == 1)
    cfg = json.loads(re.search(r'id="bt-config">(.*?)</script>', page.read_text(), re.S).group(1))
    check("the config's min size follows the audience", cfg["min_px"] == 18)
    bad = tmp / "badpal.json"
    bad.write_text(json.dumps([{"name": "Broken", "bg": "white"}]))
    code, out = run([PY, TB, "add", "--page", page, "--palettes", bad], tmp)
    check("a palette missing colours is refused", code == 1)
    run([PY, TB, "add", "--page", page, "--palettes", pal, "--open"], tmp)
    export = tmp / "export.json"
    browser = shutil.which("node") and subprocess.run(["node", "-e", "require('playwright')"], capture_output=True).returncode == 0
    if browser:
        js = tmp / "drive.cjs"
        js.write_text(r"""
const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:900}});
const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto('file://'+process.argv[2]);
const info=await p.evaluate(()=>({controls:window.buildroomTweaks.controls,starter:window.buildroomTweaks.starter,
  open:!document.getElementById('bt-panel').hidden,warn:document.querySelector('.bt-warn').textContent,
  visible:document.querySelectorAll('#bt-panel .bt-ctl:not([hidden])').length}));
await p.selectOption('#bt-panel select >> nth=0','Dusk');
const bg=await p.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--c-bg').trim());
const muted=await p.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--c-muted').trim());
let tells=0;for(let i=0;i<25;i++){await p.click('[data-act=shuffle]');
  tells+=await p.evaluate(()=>['data-eyebrows','data-head-italic'].filter(a=>document.documentElement.getAttribute(a)==='on').length+
    (document.documentElement.getAttribute('data-buttons')==='pill'?1:0));}
const minSize=await p.evaluate(()=>parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--size-base')));
await p.click('[data-act=adv]');
const adv=await p.evaluate(()=>document.querySelectorAll('#bt-panel .bt-ctl:not([hidden])').length);
await p.selectOption('#bt-panel select >> nth=0','Sage');
const warnSmall=await p.evaluate(()=>{const r=document.querySelector('#bt-panel input[type=range]');const min=r.min;
  document.documentElement.style.setProperty('--size-base','14px');r.dispatchEvent(new Event('change'));
  const sel=document.querySelector('#bt-panel select');sel.dispatchEvent(new Event('input'));
  return min+'|'+document.querySelector('.bt-warn').textContent;});
await p.evaluate(()=>{const r=document.querySelector('#bt-panel input[type=range]');r.value=20;r.dispatchEvent(new Event('input'));});
await p.selectOption('#bt-panel select[data-x], #bt-panel label:has-text("Light or dark") select','dark');
const darkBg=await p.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--c-bg').trim());
await p.fill('.bt-name','Look A');await p.click('[data-act=save]');
const exp=await p.inputValue('.bt-out textarea');
await p.click('[data-act=reset]');
const resetBg=await p.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--c-bg').trim());
await p.setViewportSize({width:375,height:812});
const sw=await p.evaluate(()=>document.documentElement.scrollWidth);
await p.keyboard.press('Escape');
const closed=await p.evaluate(()=>document.getElementById('bt-panel').hidden);
console.log(JSON.stringify({info,bg,muted,tells,minSize,adv,warnSmall,darkBg,exp,resetBg,sw,closed,errs}));await b.close();})();
""")
        p = subprocess.run(["node", str(js), str(page.resolve())], capture_output=True, text=True, timeout=120)
        try:
            r = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception:
            r = {}
        check("browser: the bar runs with no script errors", r and not r["errs"], p.stdout[-400:] + p.stderr[-400:])
        if r:
            check("browser: starts open with about twelve controls", r["info"]["open"] and 10 <= r["info"]["visible"] <= 14, r["info"])
            check("browser: advanced shows every control", r["adv"] == r["info"]["controls"] and r["adv"] > r["info"]["visible"])
            check("browser: the palette changes the page", r["bg"] == "#f7f7fb")
            check("browser: the fixed palette colour is used", r["muted"] != "#9a98b0", r["muted"])
            check("browser: shuffle never turns a generic tell on", r["tells"] == 0)
            check("browser: shuffle keeps text at the audience minimum", r["minSize"] >= 18)
            check("browser: the size slider cannot go under the audience minimum", r["warnSmall"].startswith("18|"), r["warnSmall"])
            check("browser: text under the minimum raises a warning", "your readers need 18px" in r["warnSmall"], r["warnSmall"])
            check("browser: dark mode uses the page's dark colours", r["darkBg"] == "#111714", r["darkBg"])
            check("browser: reset goes back to the page as built", r["resetBg"] == "#ffffff", r["resetBg"])
            check("browser: no sideways scroll on a phone with the bar", r["sw"] <= 375, r["sw"])
            check("browser: Escape closes the panel", r["closed"])
            try:
                e = json.loads(r["exp"])
                ok = (e["presets"][0]["name"] == "Look A" and e["presets"][0]["attrs"].get("data-theme") == "dark"
                      and e["presets"][0]["vars"].get("--c-bg") == "#ffffff")
                e["presets"][0]["attrs"]["data-theme"] = "light"      # the member then goes back to light and keeps it
                export.write_text(json.dumps(e))
            except Exception:
                ok = False
            check("browser: Save this look keeps dark mode as chosen, with the light colours", ok, r.get("exp", "")[:300])
    if not export.exists():
        export.write_text(json.dumps({"schema": "buildroom-tweaks-export/1", "presets": [
            {"name": "Look A", "palette": "Sage", "fonts": "Sturdy & Clear",
             "vars": {"--c-bg": "#ffffff", "--c-surface": "#eef3f0", "--c-ink": "#16211c", "--c-muted": "#43524a",
                      "--c-accent": "#1f5c46", "--c-accent-ink": "#ffffff", "--c-line": "#cdd8d2",
                      "--font-head": "\"Young Serif\", Georgia, serif", "--font-body": "\"Atkinson Hyperlegible Next\", system-ui, sans-serif",
                      "--size-base": "20px", "--radius": "4px", "--space": "8px", "--w-head": "600"},
             "attrs": {"data-buttons": "outline", "data-hero": "stacked", "data-theme": "light"}}]}))
        check("browser: skipped (Playwright not here); a saved look is simulated", True)
    T = P / "tweaks.json"
    for label, preset in (("a variable outside the contract", {"name": "X", "vars": {"--evil": "1"}}),
                          ("a colour that is not a colour", {"name": "X", "vars": {"--c-bg": "banana"}}),
                          ("CSS injection in a value", {"name": "X", "vars": {"--radius": "4px;} body{display:none"}}),
                          ("an unknown toggle value", {"name": "X", "attrs": {"data-hero": "carousel"}}),
                          ("a look with no name", {"vars": {}})):
        f = tmp / "bad-export.json"
        f.write_text(json.dumps({"presets": [preset]}))
        code, out = run([PY, TB, "save", "--tweaks", T, "--from", f], tmp)
        check(f"save refuses {label}", code == 1)
    code, out = run([PY, TB, "save", "--tweaks", T, "--from", export], tmp)
    check("save keeps the member's look", code == 0 and "Look A" in pj(out)["saved"], out)
    code, out = run([PY, TB, "apply", "--page", page, "--tweaks", T], tmp)
    check("apply needs a final look or a name", code == 1)
    code, out = run([PY, TB, "final", "--tweaks", T, "--name", "look a"], tmp)
    check("final marks the chosen look", code == 0 and pj(out)["final"] == "Look A")
    preset = json.loads(T.read_text())["presets"][0]
    code, out = run([PY, TB, "apply", "--page", page, "--tweaks", T], tmp)
    src = page.read_text()
    check("apply takes the bar out", code == 0 and "buildroom-tweakbar" not in src)
    check("apply writes the look into :root", all(f"{k}: {v};" in src for k, v in preset["vars"].items() if k.startswith("--c-")),
          preset["vars"])
    check("apply sets the toggles on <html>", 'data-hero="stacked"' in src)
    check("apply links the chosen fonts for the preview", "data-buildroom-fonts" in src or not preset.get("fonts"))
    run([PY, TB, "apply", "--page", page, "--tweaks", T], tmp)
    check("applying twice keeps one font link", page.read_text().count("data-buildroom-fonts") <= 1)
    check("list shows the looks", pj(run([PY, TB, "list", "--tweaks", T], tmp)[1])["final"] == "Look A")
    run([PY, TB, "add", "--page", page], tmp)
    code, out = run([PY, TB, "remove", "--page", page], tmp)
    check("remove takes the bar out again", code == 0 and pj(out)["removed"] and "bt-config" not in page.read_text())
    return T, page


# ---------------------------------------------------------------- 5. lock
def t_lock(tmp, P, T, page):
    sysdir = P.parent / "System"
    weak = tmp / "weak.json"
    weak.write_text(json.dumps({"presets": [{"name": "Weak", "vars": {"--c-ink": "#999999", "--size-base": "15px"}}],
                                "final": "Weak"}))
    code, out = run([PY, LOCK, "lock", "--tweaks", weak, "--page", page, "--out", sysdir], tmp)
    d = pj(out)
    check("lock refuses a look that fails contrast", code == 1 and any("Text on page" in x for x in d.get("problems", [])), out)
    check("lock refuses body text under 18px for a 50+ audience", any("15px" in x for x in d.get("problems", [])))
    check("nothing is written by a refused lock", not (sysdir / "tokens.json").exists())
    code, out = run([PY, LOCK, "lock", "--tweaks", T, "--page", page, "--out", sysdir, "--direction", "Field Guide",
                     "--refs", "t-001,T-004", "--do", "Real photos of the member", "--dont", "No beach stock photos",
                     "--imagery", "both"], tmp)
    d = pj(out)
    check("lock writes the five files", code == 0 and all((sysdir / f).exists() for f in d["files"]), out)
    tok = json.loads((sysdir / "tokens.json").read_text())
    check("tokens.json carries every colour", set(tok["color"]) == set(dslib.COLOR_KEYS))
    check("tokens.json carries the dark-mode colours from the page", tok["dark"].get("bg") == "#111714", tok["dark"])
    check("tokens.json carries the fonts", tok["font"]["head"]["family"] and tok["font"]["body"]["family"])
    check("tokens.json keeps the refs and the do/don't", tok["refs"] == ["T-001", "T-004"] and tok["donts"] == ["No beach stock photos"])
    css = (sysdir / "tokens.css").read_text()
    check("tokens.css has every variable", all(v in css for v in dslib.VAR_OF.values()) and "--size-base" in css)
    check("tokens.css turns motion off for visitors who ask", "prefers-reduced-motion" in css)
    md = (sysdir / "design-system.md").read_text()
    check("design-system.md is a page for humans", "## Colours" in md and "## Briefing a designer or VA" in md
          and "No beach stock photos" in md)
    check("design-system.md keeps the generic-tells rule", "No small uppercase labels" in md)
    check("fonts.md says to self-host", "self-host" in (sysdir / "fonts.md").read_text().lower())
    sl = json.loads((sysdir / "slides.json").read_text())
    check("slides.json gives the slide builder's flags", sl["flags"].startswith("--theme light --accent "))
    check("the slide accent reads on a white slide", dslib.contrast("#" + sl["accent"], "#ffffff") >= 4.5)
    pale = tmp / "pale.json"
    pv = dict(json.loads(T.read_text())["presets"][0]["vars"])
    pv.update({"--c-accent": "#3fa37a", "--c-accent-ink": "#0b1a13", "--size-base": "20px"})
    pale.write_text(json.dumps({"presets": [{"name": "Pale", "vars": pv}], "final": "Pale"}))
    code, out = run([PY, LOCK, "lock", "--tweaks", pale, "--page", page, "--out", sysdir], tmp)
    sl = json.loads((sysdir / "slides.json").read_text())
    check("a light accent is darkened for slides, and says so", code == 0 and sl["accent"] != "3FA37A" and "darkened" in sl["note"], out)
    check("locking again keeps the earlier version", (sysdir / "tokens-v1.json").exists()
          and json.loads((sysdir / "tokens.json").read_text())["version"] == 2)
    run([PY, LOCK, "lock", "--tweaks", T, "--page", page, "--out", sysdir, "--direction", "Field Guide"], tmp)
    code, out = run([PY, LOCK, "section", "--system", sysdir, "--project", P,
                     "--taste-vault", P.parent / "Taste Vault"], tmp)
    d = pj(out)
    lines = "\n".join(d.get("lines", []))
    check("section prints the seven §22 lines", code == 0 and len(d["lines"]) == 7)
    check("section names the directions tried and the pick", "chosen Field Guide" in lines)
    check("section carries the taste read", "big real photos" in lines)
    check("show prints the system", pj(run([PY, LOCK, "show", "--system", sysdir], tmp)[1])["version"] == 3)
    return sysdir


# ---------------------------------------------------------------- 6. the check
def t_check(tmp, vault, sysdir):
    good = (FX / "good.html").read_text()
    work = tmp / "check"
    (work / "img").mkdir(parents=True)
    png(work / "img" / "hero.png", 8, 8, (10, 120, 90))
    good = good.replace("img/hero.jpg", "img/hero.png")

    def go(src, *extra, name="p.html"):
        f = work / name
        f.write_text(src)
        code, out = run([PY, CHECK, "check", "--page", f, *extra], tmp)
        return code, pj(out)
    code, d = go(good)
    check("the good page says GO", code == 0 and d["verdict"] == "GO", d.get("items"))
    check("the good page has no generic tells", not any(i["id"].startswith("tell_") for i in d["items"]))
    code, d = go((FX / "slop.html").read_text())
    tl = {i["id"] for i in d["items"] if i["id"].startswith("tell_")}
    for t in ("italic_last_word", "eyebrows", "cream_background", "pill_buttons", "three_cards", "gradient_glow",
              "emoji_bullets", "empty_logo_row"):
        check(f"tell found: {t}", "tell_" + t in tl, tl)
    check("the generic page says FIX", code == 1 and d["verdict"] == "FIX")
    code, out = run([PY, CHECK, "tells", "--page", FX / "slop.html"], tmp)
    check("tells lists the eight tells on its own", code == 0 and pj(out)["count"] == 8, out)
    cases = [
        ("body text under 18px", good.replace("--size-base: 19px", "--size-base: 16px"), "body_size"),
        ("text under 12px", good.replace(".lede { color", ".lede { font-size: 11px; color"), "tiny_text"),
        ("text contrast", good.replace("--c-ink: #16211c", "--c-ink: #9aa3a0"), "contrast_ink_bg"),
        ("button text contrast", good.replace("--c-accent-ink: #ffffff", "--c-accent-ink: #2a6b52"), "contrast_accent_ink_accent"),
        ("dark-mode contrast", good.replace("--c-muted: #b9c6bf", "--c-muted: #333d38"), "contrast_muted_bg_dark"),
        ("no viewport", good.replace('<meta name="viewport" content="width=device-width, initial-scale=1">', ""), "viewport"),
        ("lorem ipsum", good.replace("We plan both.", "Lorem ipsum dolor sit amet."), "placeholders"),
        ("a [write:] marker", good.replace("</main>", "<!-- --><p>[write: footer]</p></main>"), "placeholders"),
        ("an image with no alt", good.replace(' alt="Margaret on her porch with a notebook"', ""), "img_alt"),
        ("a rule with poor contrast", good.replace(".story {", ".story { color: #999999; background: #ffffff;"), "contrast_rule"),
    ]
    for label, src, cid in cases:
        code, d = go(src)
        check(f"FIX: {label}", code == 1 and cid in items(d), [i["id"] for i in d.get("items", [])])
    code, d = go(good, "--audience", "general")
    check("a general audience allows 16px", code == 0)
    code, d = go(good.replace("--size-base: 19px", "--size-base: 16px"), "--audience", "general")
    check("16px passes for a general audience", code == 0, d.get("items"))
    # the taste vault and images.json
    tvimg = next((vault / "Design" / "Taste Vault" / "collections").rglob("*.png"))
    shutil.copy(tvimg, work / "img" / "copied.png")
    code, d = go(good.replace("img/hero.png", "img/copied.png"), "--vault", vault)
    check("FIX: a taste-vault image copied onto the page (by content)", code == 1 and "reference_image" in items(d))
    man = work / "images.json"
    man.write_text(json.dumps({"images": [{"file": "img/hero.png", "source": "reference"}]}))
    code, d = go(good, "--images", man)
    check("FIX: an image whose source is a reference", code == 1 and "image_rights" in items(d))
    man.write_text(json.dumps({"images": [{"file": "img/hero.png", "source": "kie", "person": True, "ledger_key": "k1"}]}))
    code, d = go(good, "--images", man)
    check("FIX: a generated person with no consent", code == 1 and "image_consent" in items(d))
    man.write_text(json.dumps({"images": [{"file": "img/hero.png", "source": "kie", "person": False}]}))
    code, d = go(good, "--images", man)
    check("a generated scene passes, with a ledger reminder", code == 0 and "image_ledger" in items(d), d.get("items"))
    man.write_text(json.dumps({"images": []}))
    code, d = go(good, "--images", man)
    check("WATCH: an image missing from images.json", "image_unlisted" in items(d))
    man.write_text(json.dumps({"images": [{"file": "img/hero.png", "source": "own"}]}))
    code, d = go(good, "--images", man)
    check("the member's own photo passes", code == 0 and not any(i.startswith("image_") for i in items(d)))
    # the locked system
    tok = sysdir / "tokens.json"
    final = json.loads(tok.read_text())
    locked = good
    for k in dslib.COLOR_KEYS:
        locked = re.sub(re.escape(dslib.VAR_OF[k]) + r": #[0-9a-f]{6};", f"{dslib.VAR_OF[k]}: {final['color'][k]};", locked, count=1)
    locked = locked.replace('"Young Serif", Georgia, serif', f'"{final["font"]["head"]["family"]}", serif')
    locked = locked.replace('"Atkinson Hyperlegible Next", system-ui, sans-serif', f'"{final["font"]["body"]["family"]}", sans-serif')
    code, d = go(locked, "--tokens", tok)
    check("a page on the locked system says GO", code == 0, d.get("items"))
    code, d = go(locked.replace(f"--c-accent: {final['color']['accent']};", "--c-accent: #0a4d8c;"), "--tokens", tok)
    check("FIX: colours drifted from the locked system", code == 1 and "token_drift" in items(d))
    code, d = go(locked.replace(".story {", ".story { border-left: 4px solid #e11d48;"), "--tokens", tok)
    check("FIX: a colour outside the system", code == 1 and "off_system_colours" in items(d))
    code, d = go(locked.replace("h1, h2, h3 { font-family: var(--font-head);", "h1, h2, h3 { font-family: Poppins, sans-serif;"),
                 "--tokens", tok)
    check("FIX: a font outside the system", code == 1 and "off_system_fonts" in items(d))
    # numbers
    bf = work / "BUILDROOM_BUSINESS_FILE.md"
    bf.write_text("## 3. Signature Offer\n- 12 weeks, small group of 8 people, $2,400\n")
    code, d = go(good.replace("We plan both.", "We plan both. 500+ clients helped."), "--business-file", bf)
    check("FIX: a number on the page that is not in the File", code == 1 and "unsourced_numbers" in items(d))
    code, d = go(good.replace("We plan both.", "We plan both. $2,400 for 12 weeks."), "--business-file", bf)
    check("numbers from the File pass", code == 0 and "unsourced_numbers" not in items(d), d.get("items"))
    code, d = go(good)
    check("without the File, numbers are only a WATCH", "numbers" in items(d) and code == 0)
    # watches
    code, d = go(good.replace("@media (prefers-reduced-motion: reduce) { :root { --motion: 0; } }", ""))
    check("WATCH: motion with no reduced-motion setting", "reduced_motion" in items(d) and code == 0)
    code, d = go(good.replace("</head>", '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora">\n</head>'))
    check("WATCH: fonts loaded from Google", "font_hosting" in items(d))
    code, d = go(good.replace("</main>", '<a class="btn" href="#">Download the guide</a><a class="btn" href="#">Watch the video</a></main>'))
    check("WATCH: more than two main actions", "one_action" in items(d))
    code, d = go(good.replace("<h2>Why", "<h1>Why").replace("hard</h2>", "hard</h1>"))
    check("WATCH: more than one h1", "h1" in items(d))
    code, d = go(good.replace('<html lang="en"', "<html"))
    check("WATCH: no lang attribute", "lang" in items(d))
    out_md = work / "check.md"
    code, d = go(good, "--out", out_md)
    check("--out writes check.md", out_md.exists() and "**GO**" in out_md.read_text())
    code, out = run([PY, CHECK, "check", "--page", work / "missing.html"], tmp)
    check("a missing page is a usage error (exit 2)", code == 2)
    browser = shutil.which("node") and subprocess.run(["node", "-e", "require('playwright')"], capture_output=True).returncode == 0
    if browser:
        code, d = go(good.replace("</main>", '<div style="width:900px">wide</div></main>'), "--render")
        check("render: FIX for sideways scroll on a phone", code == 1 and "sideways_scroll" in items(d), d.get("items"))
        code, d = go(good, "--render")
        check("render: the good page fits a phone", code == 0 and "sideways_scroll" not in items(d), d.get("items"))
    else:
        code, d = go(good, "--render")
        check("render: says plainly when the phone test could not run", "render" in items(d))


# ---------------------------------------------------------------- 7. consistency and wiring
def t_consistency():
    skill = (SK / "SKILL.md").read_text()
    m = re.match(r"---\nname: (.+)\ndescription: \|\n  (.+?)\n---", skill, re.S)
    check("SKILL.md has the frontmatter", m and m.group(1) == "buildroom-website-design-studio")
    check("the description is under 1024 characters", m and len(m.group(2)) < 1024, len(m.group(2)) if m else 0)
    for f in sorted(R.glob("*.md")):
        check(f"SKILL.md names references/{f.name}", f.name in skill)
    for ref in set(re.findall(r"references/([\w.-]+\.md)", skill)):
        check(f"named reference exists: {ref}", (R / ref).exists())
    for f in ("taste_vault.py", "directions.py", "tweakbar.py", "design_lock.py", "design_check.py", "gen.py", "ledger.py"):
        check(f"SKILL.md uses scripts/{f}", f in skill)
        check(f"scripts/{f} exists", (S / f).exists())
    for f in ("tweakbar.js", "tweakbar.css", "font-pairs.json"):
        check(f"assets/{f} exists", (A / f).exists())
    fonts = json.loads((A / "font-pairs.json").read_text())["pairs"]
    check("ten vetted font pairs", len(fonts) == 10)
    check("no pair uses the AI-default faces", not any(p["head"]["family"] in ("Inter", "Instrument Serif", "Playfair Display",
                                                                                 "Poppins", "Montserrat") or p["body"]["family"] == "Inter"
                                                         for p in fonts))
    check("every pair names safe slide fonts", all(p["slides_fonts"]["body"] in ("Arial", "Georgia", "Verdana", "Calibri") for p in fonts))
    allt = skill + "".join(f.read_text() for f in R.glob("*.md"))
    check("no TODO-REVIEW markers", "TODO-REVIEW" not in allt)
    check("Kie.ai is the image provider", "Kie.ai" in skill and "KIE_API_KEY" in allt)
    check("the taste vault lives in the Obsidian vault", "Design/Taste Vault" in skill)
    check("a landing page is the default deliverable", "landing page" in skill.lower())
    check("references are for mood only", "mood only" in allt)
    for p in ROOT.rglob("*"):
        if p.is_file() and SK in p.parents and p.suffix in (".py", ".md", ".js", ".json", ".css"):
            txt = p.read_text(errors="replace")
            if re.search(r"(sk-[A-Za-z0-9]{20,}|kie_[A-Za-z0-9]{20,}|Bearer [A-Za-z0-9]{24,})", txt):
                check(f"no key in {p.name}", False)
    check("no API keys in the skill", True)
    bs = (ROOT / "build-skills.sh").read_text()
    check("build-skills.sh gives the skill the shared media toolkit", "buildroom-website-design-studio" in bs)
    for f in ("gen.py", "ledger.py"):
        src, dst = ROOT / "shared/media" / f, S / f
        check(f"scripts/{f} is the shared copy", dst.exists() and dst.read_bytes() == src.read_bytes())
    tpl = (ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_text()
    check("the template has §22 Design System", "## 22. Design System" in tpl and "Built by: Website Design Studio" in tpl)
    check("the template is version 1.8", re.search(r"1\.8", tpl.split("\n", 6)[-1][:2000] + tpl[:600]) is not None)
    check("§18 Brand kit points to §22", "§22" in tpl.split("## 18. Advertising")[1].split("## 19.")[0])
    spec = (ROOT / "BUSINESS-FILE-SPEC.md").read_text()
    check("the spec documents §22", "22" in spec and "Design System" in spec)
    check("the skill's template copy matches", (R / "business-file-template.md").read_bytes() == (ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_bytes())
    road = (ROOT / "skills/buildroom-os/references/roadmap.md").read_text()
    check("the navigator's roadmap names the skill", "buildroom-website-design-studio" in road)
    for s in ("buildroom-lead-capture", "buildroom-offer-page-copy", "buildroom-webinar-builder", "buildroom-ad-studio",
              "buildroom-video-director"):
        check(f"{s} reads §22 before designing", "§22" in (ROOT / "skills" / s / "SKILL.md").read_text())
    vs = (ROOT / "skills/buildroom-obsidian/references/vault-starter.md").read_text()
    check("the Second Brain's vault starter has the Design folder", "Design/" in vs)
    claude = (ROOT / "rollout/universal/CLAUDE.md").read_text()
    check("the universal CLAUDE.md lists the skill", "buildroom-website-design-studio" in claude)



# ---------------------------------------------------------------- 8. regressions from the dry run and the review
def t_regress(tmp):
    import importlib
    sys.path.insert(0, str(S))
    tb = importlib.import_module("tweakbar")
    w = tmp / "reg"
    w.mkdir()
    good = (FX / "good.html").read_text().replace(' <img src="img/hero.jpg" alt="Margaret on her porch with a notebook" width="800" height="600">', "")

    def go(src, *extra, name="r.html", where=None):
        f = (where or w) / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(src if isinstance(src, bytes) else src.encode())
        code, out = run([PY, CHECK, "check", "--page", f, *extra], tmp)
        return code, pj(out)
    # bake
    out = tb.bake("<html><style>:root{--c-bg:#fff;--c-ink:#111}</style></html>", {"vars": {"--size-base": "22px"}})
    check("bake adds a semicolon before a new variable", "--c-ink:#111; --size-base: 22px;" in out, out)
    out = tb.bake("<html><style>:root{--c-bg:#fff;--size-base:16px} @media (min-width:900px){:root{--size-base:17px}}</style></html>",
                  {"vars": {"--size-base": "20px"}})
    check("bake makes the look win over a later :root", "/* buildroom-look */ :root { --size-base: 20px; }" in out, out)
    out = tb.bake("<html data-theme='light'><style>:root{--c-bg:#fff}</style></html>", {"vars": {"--c-bg": "#fafafa"},
                                                                                      "attrs": {"data-theme": "dark"}})
    check("bake replaces a single-quoted toggle instead of adding a second", out.count("data-theme") == 1 and 'data-theme="dark"' in out, out)
    try:
        out = tb.bake("<html><style>:root{--c-bg:#fff}</style></html>", {"vars": {"--font-head": '"A\\1", serif'}})
        ok = "A\\1" in out
    except Exception as e:
        ok = False
    check("bake keeps a backslash in a value without crashing", ok)
    try:
        tb.bake("<html><body>no styles</body></html>", {"vars": {"--c-bg": "#fff"}})
        ok = False
    except ValueError:
        ok = True
    check("bake refuses a page with nowhere to write the look", ok)
    # palettes
    fixed, notes = tb.fix_palette({"name": "Sun", "bg": "#ffffff", "surface": "#fff8e1", "ink": "#222222", "muted": "#666666",
                                   "accent": "#ffd400", "accent_ink": "#ffffff", "line": "#eeeeee"})
    check("a yellow-accent palette is fixed so every pair passes",
          fixed and all(dslib.contrast(fixed[f], fixed[b]) >= n for f, b, n in tb.PAIRS), (fixed, notes))
    check("a palette with no name is refused, not a crash", tb.fix_palette({"bg": "#fff"})[0] is None)
    check("hsl() colours are accepted in a saved look", not tb.valid_preset({"name": "H", "vars": {"--c-bg": "hsl(210, 20%, 98%)"}}))
    # the CSS reader feeding the check
    code, d = go(good.replace("[data-theme=\"dark\"] {", "@media (prefers-color-scheme:dark){:root{--c-bg:#000000;--c-ink:#ffffff}} [data-theme=\"dark\"] {"))
    check("a minified dark-mode block is not read as the light page", code == 0, d.get("items"))
    code, d = go(good.replace("--size-base: 19px", "--size-base: 16px").replace("</style>", "@media (min-width:900px){:root{--size-base:19px}}</style>"))
    check("a bigger size only on wide screens does not pass a phone", code == 1 and "body_size" in items(d))
    rv = dslib.root_vars(":root{--motion:1} @media (prefers-reduced-motion: reduce){:root{--motion:0}}")
    check("reduced motion is not the default motion", rv.get("--motion") == "1", rv)
    code, d = go(good.replace("--c-ink: #16211c", "--c-ink: rgba(22,33,28,.4)"))
    check("a translucent text colour is a WATCH, not a silent pass", "colour_unread_ink" in items(d))
    code, d = go(good.replace("--c-ink: #16211c", "--c-ink: lightgray"))
    check("a named colour is read (and fails contrast)", code == 1 and "contrast_ink_bg" in items(d))
    code, d = go(good.replace("--size-base: 19px", "--size-base: 1.6rem").replace("* { box-sizing", "html { font-size: 62.5%; } * { box-sizing"))
    check("rem follows html font-size: 62.5% (1.6rem is 16px)", code == 1 and "body_size" in items(d), d.get("body_px"))
    css_dir = w / "linked"
    css_dir.mkdir()
    (css_dir / "style.css").write_text(":root{--c-bg:#ffffff;--c-ink:#bbbbbb} body{font-size:19px;color:var(--c-ink);background:var(--c-bg)}")
    bare = '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>x</title>' \
           '<link rel="stylesheet" href="style.css?v=2"></head><body><h1>Hi</h1><p>Text</p></body></html>'
    code, d = go(bare, name="p.html", where=css_dir)
    check("a stylesheet with ?v=2 is read", code == 1 and "contrast_ink_bg" in items(d), d.get("items"))
    code, d = go(bare.replace('<link rel="stylesheet" href="style.css?v=2">', ""), name="q.html", where=css_dir)
    check("a page with no readable colours says so", "contrast_unchecked" in items(d))
    code, d = go(good.replace(".story {", ".grad { color: #ffffff; background: linear-gradient(#ffffff, #1d4ed8); } .story {"))
    check("a gradient background is not read as its first colour", "contrast_rule" not in items(d), d.get("items"))
    code, d = go(good.replace("</main>", '<form><label>Company name <input placeholder="you@example.com"></label></form></main>'))
    check("a form's 'Company name' label and placeholder hint are not placeholders", "placeholders" not in items(d), d.get("items"))
    bf = w / "BF.md"
    bf.write_text("- Clients served so far: 140.\n- 12 weeks\n")
    code, d = go(good.replace("We plan both.", "We plan both. 140 clients so far."), "--business-file", bf)
    check("a number from the File followed by a full stop passes", code == 0, d.get("items"))
    code, d = go(good.replace("We plan both.", "We plan both. 500 happy clients and a 4.9/5 rating."), "--business-file", bf)
    msg = " ".join(i["message"] for i in d.get("items", []))
    check("'500 happy clients' and '4.9/5' are caught", code == 1 and "500 happy clients" in msg and "4.9/5" in msg, msg)
    code, d = go(good, "--business-file", w / "nope.md")
    check("a mistyped --business-file path is an error, not a quiet pass", code == 2)
    tok = w / "tokens.json"
    tok.write_text(json.dumps({"audience": "50plus", "color": {"bg": "#ffffff", "surface": "#eef3f0", "ink": "#16211c", "muted": "#43524a",
                    "accent": "#1f5c46", "accent_ink": "#ffffff", "line": "#cdd8d2"}, "dark": {},
                    "font": {"head": {"family": "Young Serif"}, "body": {"family": "Atkinson Hyperlegible Next"}}}))
    code, d = go(good.replace("h1 { font-size", "h2 { font: 700 2rem 'Papyrus', fantasy; } h1 { font-size"), "--tokens", tok)
    check("a font set with the font: shorthand is checked against the system", code == 1 and "off_system_fonts" in items(d))
    code, d = go(good.replace('[data-theme="dark"] {', "[data-theme=dark] {").replace("--c-muted: #b9c6bf", "--c-muted: #333d38"))
    check("an unquoted [data-theme=dark] block is checked", code == 1 and "contrast_muted_bg_dark" in items(d))
    check("nested var() fallbacks resolve the outer variable",
          dslib.resolve("var(--a, var(--b, #000))", {"--a": "#123456"}) == "#123456")
    code, d = go(good.replace(".lede { color: var(--c-muted); }", ".hero p { color: #8a8a8a; background: #ffffff; } .lede { color: var(--c-muted); }"))
    check("body text inside .hero gets the 4.5:1 rule, not 3:1", code == 1, d.get("items"))
    code, d = go(good.replace("</main>", "<details><summary>Question</summary><p>Answer</p></details><button type=\"button\" aria-expanded=\"false\">More</button>"
                              "<button type=\"button\" aria-expanded=\"false\">Less</button></main>"))
    check("FAQ and accordion buttons are not competing main actions", "one_action" not in items(d))
    code, d = go(good.replace(".btn {", '[data-buttons="pill"] .btn { border-radius: 999px; } .btn {'))
    check("a pill rule kept for the toggle is not a tell", "tell_pill_buttons" not in items(d))
    code, d = go(good.replace("</main>", '<section><p>Trusted by leading schools</p><img src="x.png" alt="classroom"></section></main>'))
    check("'trusted by' next to one ordinary photo is still a tell", "tell_empty_logo_row" in items(d))
    code, d = go(b"\xef\xbb\xbf" + good.replace("We plan both.", "Caf\xe9 mornings.").encode("cp1252", errors="replace"))
    check("a page saved by Notepad (BOM, Windows-1252) is read, not a traceback", code in (0, 1) and d.get("verdict"))
    # the taste vault image check with %20 and ?v=
    v = w / "vault"
    v.mkdir()
    run([PY, TV, "init", "--vault", v], tmp)
    png(v / "Design" / "Taste Vault" / "inbox" / "a.png", 6, 6, (1, 2, 3))
    run([PY, TV, "sort", "--vault", v], tmp)
    pg = v / "Design" / "landing-page" / "page"
    pg.mkdir(parents=True)
    code, d = go(good.replace("</main>", '<img src="../../Taste%20Vault/collections/unsorted/T-001.png?v=2" alt="x"></main>'), "--vault", v,
                 name="index.html", where=pg)
    check("a taste-vault image written with %20 and ?v=2 is caught", code == 1 and "reference_image" in items(d))
    (v / "Design" / "landing-page" / "design.json").write_text(json.dumps({"audience": "general"}))
    code, d = go(good.replace("--size-base: 19px", "--size-base: 16px"), name="index.html", where=pg)
    check("the audience is read from the project's design.json", code == 0 and d.get("audience") == "general", d.get("audience"))
    # sort keeps the member's folder
    v2 = w / "vault2"
    v2.mkdir()
    run([PY, TV, "init", "--vault", v2], tmp)
    inbox = v2 / "Design" / "Taste Vault" / "inbox"
    png(inbox / "a.png", 6, 6, (9, 9, 9))
    png(inbox / "heroes" / "a.png", 6, 6, (9, 9, 9))
    d = pj(run([PY, TV, "sort", "--vault", v2], tmp)[1])
    data = json.loads((v2 / "Design" / "Taste Vault" / "taste.json").read_text())
    check("a duplicate keeps the member's sub-folder collection", data["refs"][0]["collection"] == "heroes", data["refs"])
    check("stored paths use forward slashes", "\\" not in data["refs"][0]["file"])
    # directions: refs, remove, <HEAD>, srcset, pick across depths
    P = w / "vault" / "Design" / "lp2"
    run([PY, DIR, "init", "--project", P], tmp)
    code, out = run([PY, DIR, "new", "--project", P, "--name", "A", "--idea", "x", "--for", "y", "--refs", "T-001,T-404", "--vault", v], tmp)
    check("a reference not in the taste vault is refused", code == 1 and "T-404" in out)
    code, out = run([PY, DIR, "new", "--project", P, "--name", "A", "--idea", "x", "--for", "y", "--refs", "T-001", "--vault", v], tmp)
    check("fewer than three references is a warning", code == 0 and pj(out)["warnings"])
    code, out = run([PY, DIR, "new", "--project", P, "--name", "B", "--idea", "x", "--for", "y", "--refs", "T-001"], tmp)
    check("two directions on the same main reference is a warning", any("main reference" in x for x in pj(out)["warnings"]))
    code, out = run([PY, DIR, "remove", "--project", P, "--name", "B"], tmp)
    st = pj(run([PY, DIR, "status", "--project", P], tmp)[1])
    check("remove takes a direction out and keeps its files", code == 0 and st["rounds"][0]["directions"] == ["A"]
          and (P / "directions" / "removed-r1-b").exists())
    da = P / "directions" / "r1-a"
    (da / "img").mkdir(exist_ok=True)
    png(da / "img" / "s.png", 4, 4, (200, 10, 10))
    shared = P.parent / "shared"
    shared.mkdir()
    png(shared / "bg.png", 4, 4, (10, 200, 10))
    (da / "css").mkdir()
    (da / "css" / "s.css").write_text(".x{background:url(../img/s.png)}")
    (da / "index.html").write_text('<!DOCTYPE html><HTML lang="en"><HEAD class="x"><meta charset="utf-8"><link rel="stylesheet" href="css/s.css">'
                                   '</HEAD><body><h1>A</h1><img srcset="img/s.png 1x, img/s.png 2x" src="img/s.png" alt="a">'
                                   '<img src="../../../shared/bg.png" alt="b"></body></HTML>')
    run([PY, DIR, "board", "--project", P], tmp)
    board = (P / "directions-round-1.html").read_text()
    check("the base path goes inside <HEAD class>, never before the doctype",
          "&lt;HEAD class=&quot;x&quot;&gt;&lt;base href=" in board, board[board.find("srcdoc"):board.find("srcdoc") + 200])
    run([PY, DIR, "board", "--project", P, "--inline", "--out", "inline.html"], tmp)
    il = (P / "inline.html").read_text()
    check("--inline embeds srcset images and a stylesheet's own url()", il.count("data:image/png;base64") >= 4 and "s.png" not in il.split("srcdoc")[1][:0] + il.replace("data:image/png", ""), il.count("data:image/png;base64"))
    run([PY, DIR, "pick", "--project", P, "--name", "A"], tmp)
    picked = (P / "page" / "index.html").read_text()
    check("pick rewrites ../ paths so they still reach the same files", 'src="../../shared/bg.png"' in picked
          and (P / "page" / "../../shared/bg.png").resolve().exists(), picked[-200:])
    # the lock
    sysdir = w / "System"
    nofont = w / "nofont.json"
    nofont.write_text(json.dumps({"final": "N", "presets": [{"name": "N", "vars": {"--c-bg": "#ffffff", "--c-surface": "#f3f3f3",
        "--c-ink": "#111111", "--c-muted": "#444444", "--c-accent": "#1d4ed8", "--c-accent-ink": "#ffffff", "--c-line": "#dddddd",
        "--size-base": "19px"}}]}))
    nofont_page = w / "nf.html"
    nofont_page.write_text("<html><style>:root{--c-bg:#fff}</style></html>")
    code, out = run([PY, LOCK, "lock", "--tweaks", nofont, "--page", nofont_page, "--out", sysdir], tmp)
    check("a look with no fonts is refused before anything is written", code == 1 and not sysdir.exists(), out)
    named = json.loads(nofont.read_text())
    named["presets"][0]["vars"].update({"--font-head": '"Bitter", serif', "--font-body": '"Source Sans 3", sans-serif'})
    named["presets"][0]["palette"] = "custom"
    nofont.write_text(json.dumps(named))
    code, out = run([PY, LOCK, "lock", "--tweaks", nofont, "--page", nofont_page, "--out", sysdir], tmp)
    check("the system is named after the look, not 'custom'", code == 0 and json.loads((sysdir / "tokens.json").read_text())["name"] == "N", out)
    check("design-system.md says 50+, matching the setting", "50+" in (sysdir / "design-system.md").read_text())
    # the font link on apply
    page = w / "fl.html"
    page.write_text('<html><head><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Young+Serif"></head>'
                    '<style>:root{--c-bg:#fff;--font-head:"Young Serif", serif}</style><body></body></html>')
    out = tb.font_link(tb.bake(page.read_text(), {"fonts": "Dependable", "vars": {}}), {"fonts": "Dependable", "vars": {}})
    check("apply replaces the direction's own font link with the chosen pair's",
          out.count("fonts.googleapis.com") == 1 and "Bitter" in out and "gstatic" not in out, out[:300])
    browser = shutil.which("node") and subprocess.run(["node", "-e", "require('playwright')"], capture_output=True).returncode == 0
    if browser:
        code, d = go(good.replace("main { max-width: 1100px; margin: 0 auto; padding: calc(var(--space) * 4) 16px; }",
                                  "main { max-width: 1100px; margin: 0 auto; padding: calc(var(--space) * 4) 0; }"), "--render")
        check("render: text touching the phone's edge is a WATCH", "phone_gutter" in items(d), d.get("items"))

def main():
    keep = "--keep" in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix="design-tests-"))
    try:
        t_dslib()
        t_png(tmp)
        vault = t_taste(tmp)
        P = t_directions(tmp, vault)
        T, page = t_tweakbar(tmp, P)
        sysdir = t_lock(tmp, P, T, page)
        t_check(tmp, vault, sysdir)
        t_regress(tmp)
        t_consistency()
    finally:
        if keep:
            print("kept", tmp)
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    bad = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
