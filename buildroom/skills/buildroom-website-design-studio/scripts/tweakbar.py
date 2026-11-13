#!/usr/bin/env python3
"""Website Design Studio: the tweak bar (sliders and toggles on the chosen page).

The bar only changes the page token contract: the CSS variables on :root and the data- attributes
on <html> (dslib.VAR_OF, dslib.SCALAR_VARS, dslib.ATTRS). It shows only the controls the page
actually uses, about twelve to start, the rest behind "Show advanced". Palettes are checked for
contrast before they go in, and fixed (with a note) when they fail.

Usage
  tweakbar.py add    --page Design/landing-page/page/index.html [--palettes palettes.json]
                     [--fonts <skill>/assets/font-pairs.json] [--level starter|advanced]
                     [--audience 50plus|general] [--open]
  tweakbar.py remove --page P                       takes the bar out again
  tweakbar.py save   --tweaks Design/landing-page/tweaks.json --from tweaks-export.json
                     adds the looks the member saved (copied from the bar, or downloaded)
  tweakbar.py final  --tweaks T --name "Look 2"     marks the look the member chose
  tweakbar.py apply  --page P --tweaks T [--name "Look 2"] [--out P]
                     bakes the look into the page's :root and <html>, and takes the bar out
  tweakbar.py list   --tweaks T

palettes.json: [{"name": "Sage", "bg": "#…", "surface": "#…", "ink": "#…", "muted": "#…",
                 "accent": "#…", "accent_ink": "#…", "line": "#…"}, …]  (from the taste read)
Every command prints JSON. Exit 1 on a refusal.
"""
import argparse, html, json, re, sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dslib  # noqa: E402

ASSETS = HERE.parent / "assets"
START, END = "<!-- buildroom-tweakbar:start -->", "<!-- buildroom-tweakbar:end -->"
BAR_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
CONTRACT_VARS = set(dslib.VAR_OF.values()) | set(dslib.SCALAR_VARS)
PAIRS = [("ink", "bg", dslib.AA_TEXT), ("muted", "bg", dslib.AA_TEXT), ("ink", "surface", dslib.AA_TEXT),
         ("accent_ink", "accent", dslib.AA_TEXT), ("accent", "bg", dslib.AA_LARGE)]


def supported(src):
    vars_ = sorted(v for v in CONTRACT_VARS if re.search(r"var\(\s*" + re.escape(v) + r"\b", src))
    attrs = {}
    for a, opts in dslib.ATTRS.items():
        if re.search(r"\[\s*" + re.escape(a) + r"\s*=", src) or (a == "data-theme" and "data-theme" in src):
            attrs[a] = list(opts)
    return vars_, attrs


def fix_palette(p):
    p = {k: (dslib.norm_hex(v) if k in dslib.COLOR_KEYS else v) for k, v in p.items()}
    notes = []
    for k in dslib.COLOR_KEYS:
        if not p.get(k):
            return None, [f"palette {p.get('name', '?')}: {k} is missing or not a hex colour"]
    for fg, bg, need in PAIRS:
        r = dslib.contrast(p[fg], p[bg])
        if r < need:
            new = dslib.shade_to_contrast(p[fg], p[bg], need)
            notes.append(f"{p['name']}: {fg} {p[fg]} on {bg} was {r}:1, changed to {new}")
            p[fg] = new
    return p, notes


def strip_bar(src):
    return BAR_RE.sub("", src)


def cmd_add(a):
    page = Path(a.page)
    if not page.is_file():
        dslib.emit({"ok": False, "error": f"page not found: {page}"}, 1)
    src = strip_bar(page.read_text(encoding="utf-8"))
    vars_, attrs = supported(src)
    if not vars_:
        dslib.emit({"ok": False, "error": "the page uses none of the token variables (var(--c-bg) and the rest); "
                    "rewrite it on the page token contract first (tweak-bar.md)"}, 1)
    rv = dslib.root_vars(src)
    initial_vars = {k: v for k, v in rv.items() if k in CONTRACT_VARS}
    initial_attrs = {}
    m = re.search(r"<html\b([^>]*)>", src, re.I)
    if m:
        for k, v in re.findall(r'(data-[\w-]+)="([^"]*)"', m.group(1)):
            if k in attrs:
                initial_attrs[k] = v
    palettes, notes = [], []
    if a.palettes:
        for p in dslib.read_json(a.palettes):
            fixed, n = fix_palette(p)
            if fixed is None:
                dslib.emit({"ok": False, "error": n[0]}, 1)
            palettes.append(fixed)
            notes += n
    built = {"name": "As built"}
    for k in dslib.COLOR_KEYS:
        h = dslib.norm_hex(dslib.resolve(rv.get(dslib.VAR_OF[k], ""), rv) or "")
        if h:
            built[k] = h
    if len(built) == len(dslib.COLOR_KEYS) + 1:
        palettes.insert(0, built)
    fonts_file = Path(a.fonts) if a.fonts else ASSETS / "font-pairs.json"
    fonts = dslib.read_json(fonts_file)["pairs"]
    audience = a.audience
    if not audience:
        dj = page.parent.parent / "design.json"
        audience = dslib.read_json(dj).get("audience", "50plus") if dj.exists() else "50plus"
    cfg = {"audience": audience,
           "min_px": dslib.MIN_BODY_PX_50PLUS if audience == "50plus" else dslib.MIN_BODY_PX,
           "supported": {"vars": vars_, "attrs": attrs}, "level": a.level, "palettes": palettes,
           "fonts": [{"name": f["name"], "head": f["head"], "body": f["body"], "preview_css": f.get("preview_css", "")}
                     for f in fonts],
           "initial": {"vars": initial_vars, "attrs": initial_attrs}, "open": bool(a.open)}
    js = (ASSETS / "tweakbar.js").read_text(encoding="utf-8")
    css = (ASSETS / "tweakbar.css").read_text(encoding="utf-8")
    blob = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    bar = (f'{START}\n<style id="bt-style">{css}</style>\n'
           f'<script type="application/json" id="bt-config">{blob}</script>\n<script>{js}</script>\n{END}\n')
    if re.search(r"</body>", src, re.I):
        out = re.sub(r"</body>", lambda _: bar + "</body>", src, count=1, flags=re.I)
    else:
        out = src + bar
    dslib.write_atomic(page, out)
    return {"ok": True, "page": str(page), "audience": audience, "vars_supported": vars_,
            "toggles_supported": sorted(attrs), "palettes": [p["name"] for p in palettes], "font_pairs": len(fonts),
            "palette_fixes": notes,
            "unsupported": sorted(CONTRACT_VARS - set(vars_)) + sorted(set(dslib.ATTRS) - set(attrs)),
            "note": "open the page in a browser and click Tweaks (bottom right)"}


def cmd_remove(a):
    page = Path(a.page)
    src = page.read_text(encoding="utf-8")
    out = strip_bar(src)
    dslib.write_atomic(page, out)
    return {"ok": True, "removed": out != src, "page": str(page)}


def load_tweaks(p):
    return dslib.read_json(p, default={"schema": "buildroom-tweaks/1", "presets": [], "final": None})


def valid_preset(p):
    errs = []
    if not isinstance(p, dict) or not str(p.get("name", "")).strip():
        return ["a look with no name"]
    for k, v in (p.get("vars") or {}).items():
        if k not in CONTRACT_VARS:
            errs.append(f"{p['name']}: {k} is not a token variable")
        elif k.startswith("--c-") and not (dslib.norm_hex(v) or dslib.RGB_RE.search(v)):
            errs.append(f"{p['name']}: {k} = {v} is not a colour")
        elif re.search(r"[<>{};]", str(v)):
            errs.append(f"{p['name']}: {k} has characters a CSS value cannot hold")
    for k, v in (p.get("attrs") or {}).items():
        if k not in dslib.ATTRS or v not in dslib.ATTRS[k]:
            errs.append(f"{p['name']}: {k}={v} is not a known toggle")
    return errs


def cmd_save(a):
    try:
        exp = json.loads(Path(getattr(a, "from")).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        dslib.emit({"ok": False, "error": f"could not read the saved looks: {e}"}, 1)
    presets = exp.get("presets") if isinstance(exp, dict) else exp
    if not isinstance(presets, list) or not presets:
        dslib.emit({"ok": False, "error": "no looks in that file"}, 1)
    errs = [e for p in presets for e in valid_preset(p)]
    if errs:
        dslib.emit({"ok": False, "error": "; ".join(errs[:6])}, 1)
    t = load_tweaks(a.tweaks)
    names = []
    for p in presets:
        rec = {"name": p["name"].strip(), "palette": p.get("palette", ""), "fonts": p.get("fonts", ""),
               "vars": {k: str(v).strip() for k, v in (p.get("vars") or {}).items()},
               "attrs": dict(p.get("attrs") or {}), "saved": p.get("saved") or str(date.today())}
        t["presets"] = [x for x in t["presets"] if x["name"] != rec["name"]] + [rec]
        names.append(rec["name"])
    dslib.write_json(a.tweaks, t)
    return {"ok": True, "saved": names, "looks": [x["name"] for x in t["presets"]], "final": t.get("final")}


def get_preset(t, name):
    name = name or t.get("final")
    if not name:
        dslib.emit({"ok": False, "error": "say which look: --name, or mark one with final"}, 1)
    p = next((x for x in t["presets"] if x["name"].lower() == name.lower()), None)
    if not p:
        dslib.emit({"ok": False, "error": f"no look called {name}; saved: {', '.join(x['name'] for x in t['presets'])}"}, 1)
    return p


def cmd_final(a):
    t = load_tweaks(a.tweaks)
    p = get_preset(t, a.name)
    t["final"] = p["name"]
    t["final_date"] = str(date.today())
    dslib.write_json(a.tweaks, t)
    return {"ok": True, "final": p["name"]}


def bake(src, preset):
    """Write the preset's values into the first :root { } block and the <html> attributes."""
    vars_ = preset.get("vars", {})
    blocks = list(re.finditer(r":root\s*\{([^}]*)\}", src))
    m = max(blocks, key=lambda x: x.group(1).count("--c-"), default=None)
    if m is not None and "--c-" not in m.group(1):
        m = blocks[0]
    if not m:
        block = ":root { " + " ".join(f"{k}: {v};" for k, v in vars_.items()) + " }\n"
        src = re.sub(r"<style>", "<style>\n" + block, src, count=1) if "<style>" in src else src
    else:
        body = m.group(1)
        for k, v in vars_.items():
            pat = re.compile(re.escape(k) + r"\s*:\s*[^;]*;")
            body = pat.sub(lambda _: f"{k}: {v};", body, count=1) if pat.search(body) else body.rstrip() + f" {k}: {v};"
        src = src[:m.start(1)] + body + src[m.end(1):]
    hm = re.search(r"<html\b([^>]*)>", src, re.I)
    if hm:
        attrs_txt = hm.group(1)
        for k, v in (preset.get("attrs") or {}).items():
            if re.search(re.escape(k) + r'="[^"]*"', attrs_txt):
                attrs_txt = re.sub(re.escape(k) + r'="[^"]*"', f'{k}="{html.escape(v)}"', attrs_txt)
            else:
                attrs_txt += f' {k}="{html.escape(v)}"'
        src = src[:hm.start(1)] + attrs_txt + src[hm.end(1):]
    return src


FONT_LINK_RE = re.compile(r'<link[^>]*data-buildroom-fonts[^>]*>\n?')


def font_link(src, preset, fonts_file=None):
    """Point the page at the chosen pair's web fonts (a preview link; fonts.md says how to self-host)."""
    pairs = dslib.read_json(fonts_file or ASSETS / "font-pairs.json")["pairs"]
    pair = next((x for x in pairs if x["name"] == preset.get("fonts")), None)
    if not pair:
        head = dslib.first_family(preset.get("vars", {}).get("--font-head", ""))
        pair = next((x for x in pairs if x["head"]["family"] == head), None)
    if not pair or not pair.get("preview_css"):
        return src
    src = FONT_LINK_RE.sub("", src)
    tag = f'<link rel="stylesheet" href="{html.escape(pair["preview_css"])}" data-buildroom-fonts>\n'
    return re.sub(r"</head>", lambda _: tag + "</head>", src, count=1, flags=re.I) if "</head>" in src.lower() else tag + src


def cmd_apply(a):
    t = load_tweaks(a.tweaks)
    p = get_preset(t, a.name)
    errs = valid_preset(p)
    if errs:
        dslib.emit({"ok": False, "error": "; ".join(errs)}, 1)
    page = Path(a.page)
    out = font_link(bake(strip_bar(page.read_text(encoding="utf-8")), p), p)
    dest = Path(a.out) if a.out else page
    dslib.write_atomic(dest, out)
    return {"ok": True, "look": p["name"], "page": str(dest), "vars": len(p.get("vars", {})),
            "toggles": p.get("attrs", {})}


def cmd_list(a):
    t = load_tweaks(a.tweaks)
    return {"ok": True, "looks": [{"name": x["name"], "palette": x.get("palette"), "fonts": x.get("fonts"),
                                   "saved": x.get("saved")} for x in t["presets"]], "final": t.get("final")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add"); p.add_argument("--page", required=True); p.add_argument("--palettes")
    p.add_argument("--fonts"); p.add_argument("--level", choices=["starter", "advanced"], default="starter")
    p.add_argument("--audience", choices=["50plus", "general"]); p.add_argument("--open", action="store_true")
    p = sub.add_parser("remove"); p.add_argument("--page", required=True)
    p = sub.add_parser("save"); p.add_argument("--tweaks", required=True); p.add_argument("--from", required=True)
    p = sub.add_parser("final"); p.add_argument("--tweaks", required=True); p.add_argument("--name", required=True)
    p = sub.add_parser("apply"); p.add_argument("--page", required=True); p.add_argument("--tweaks", required=True)
    p.add_argument("--name"); p.add_argument("--out")
    p = sub.add_parser("list"); p.add_argument("--tweaks", required=True)
    a = ap.parse_args()
    out = globals()["cmd_" + a.cmd](a)
    dslib.emit(out, 0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
