#!/usr/bin/env python3
"""Website Design Studio: lock the chosen look into the member's Design System.

  design_lock.py lock    --tweaks Design/landing-page/tweaks.json [--name "Look 2"]
                         --page Design/landing-page/page/index.html --out Design/System
                         [--direction "Field Guide"] [--audience 50plus|general] [--refs T-001,T-004,T-009]
                         [--do "…"]... [--dont "…"]... [--imagery own|kie|both] [--photo-rules "…"]
                         [--fonts <skill>/assets/font-pairs.json]
  design_lock.py section --system Design/System [--taste-vault "<vault>/Design/Taste Vault"]
                         [--project Design/landing-page]      prints the Business File §22 lines
  design_lock.py show    --system Design/System

lock writes, in --out:
  tokens.json        the system, machine-readable (other skills read this)
  tokens.css         the same as CSS variables, ready to paste into any page
  slides.json        the Webinar Builder's slide_builder.py flags (theme, accent, font)
  design-system.md   one page for humans: colours, fonts, sizes, shapes, photos, do and don't,
                     and how to brief a designer or VA
  fonts.md           which font files to self-host and where to get them
A previous tokens.json is kept as tokens-v<N>.json. The lock refuses a look that fails contrast or
that sets body text under the audience minimum.
"""
import argparse, json, re, shutil, sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dslib  # noqa: E402
import tweakbar  # noqa: E402

SLIDE_BG = {"light": "#ffffff", "dark": "#141414"}
SHADOW_NAMES = {"none": "none", "0 1px 2px rgba(0,0,0,.08), 0 4px 12px rgba(0,0,0,.06)": "soft",
                "0 2px 4px rgba(0,0,0,.12), 0 16px 40px rgba(0,0,0,.18)": "deep"}
MOTION_NAMES = {"0": "off", "1": "gentle", "1.6": "lively"}
LABELS = {"bg": "Page background", "surface": "Panels and cards", "ink": "Text", "muted": "Quiet text",
          "accent": "Accent (buttons, links)", "accent_ink": "Text on the accent", "line": "Lines and borders"}


def colour(v):
    if v is None:
        return None
    return dslib.parse_colour(v.strip())[0]


def split_family(v):
    parts = [p.strip() for p in (v or "").split(",") if p.strip()]
    if not parts:
        return None, ""
    return parts[0].strip("'\""), ", ".join(parts[1:])


def dark_block(page_src):
    out = {}
    for sel, props, media in dslib.css_rules(page_src):
        if dslib.is_dark_selector(sel):
            for k, v in props.items():
                if k in dslib.VAR_OF.values():
                    h = colour(v)
                    if h:
                        out[next(c for c, n in dslib.VAR_OF.items() if n == k)] = h
    return out


def num(v, default=None):
    m = re.match(r"\s*(-?[\d.]+)", v or "")
    return float(m.group(1)) if m else default


def cmd_lock(a):
    t = tweakbar.load_tweaks(a.tweaks)
    p = tweakbar.get_preset(t, a.name)
    if a.page and not Path(a.page).is_file():
        dslib.emit({"ok": False, "error": f"page not found: {a.page}"}, 1)
    page_src = dslib.read_text(a.page) if a.page else ""
    base_vars = dslib.root_vars(page_src) if page_src else {}
    vars_ = {**{k: v for k, v in base_vars.items() if k in tweakbar.CONTRACT_VARS}, **p.get("vars", {})}
    attrs = dict(p.get("attrs") or {})
    audience = a.audience
    if not audience and a.page:
        for dj in (Path(a.page).parent / "design.json", Path(a.page).parent.parent / "design.json"):
            if dj.is_file():
                audience = dslib.read_json(dj).get("audience")
                break
    audience = audience or "50plus"
    min_px = dslib.MIN_BODY_PX_50PLUS if audience == "50plus" else dslib.MIN_BODY_PX
    col = {}
    for k in dslib.COLOR_KEYS:
        h = colour(dslib.resolve(vars_.get(dslib.VAR_OF[k]), vars_))
        if not h:
            dslib.emit({"ok": False, "error": f"{dslib.VAR_OF[k]} is not set in the look or the page"}, 1)
        col[k] = h
    problems = []
    for fg, bg, need in tweakbar.PAIRS:
        r = dslib.contrast(col[fg], col[bg])
        if r < need:
            problems.append(f"{LABELS[fg]} on {LABELS[bg].lower()}: {col[fg]} on {col[bg]} is {r}:1, needs {need}:1 "
                            f"(try {dslib.shade_to_contrast(col[fg], col[bg], need)})")
    base_px = dslib.px(vars_.get("--size-base", "")) or 16
    if base_px < min_px:
        problems.append(f"body text is {base_px:g}px; this audience needs {min_px}px")
    if problems:
        dslib.emit({"ok": False, "error": "this look cannot be locked yet", "problems": problems}, 1)
    dark = dark_block(page_src)
    dark_problems = []
    if dark:
        dfull = {**col, **dark}
        for fg, bg, need in tweakbar.PAIRS:
            if dslib.contrast(dfull[fg], dfull[bg]) < need:
                dark_problems.append(f"dark mode {fg} on {bg} is {dslib.contrast(dfull[fg], dfull[bg])}:1")
    head_f, head_fb = split_family(dslib.resolve(vars_.get("--font-head"), vars_))
    body_f, body_fb = split_family(dslib.resolve(vars_.get("--font-body"), vars_))
    if not head_f or not body_f:
        dslib.emit({"ok": False, "error": "the look sets no heading or body font (--font-head, --font-body); "
                    "pick a font pairing on the tweak bar, save, and lock again"}, 1)
    pairs = dslib.read_json(Path(a.fonts) if a.fonts else HERE.parent / "assets" / "font-pairs.json")["pairs"]
    pair = next((x for x in pairs if x["head"]["family"] == head_f and x["body"]["family"] == body_f), None)
    weight = int(num(vars_.get("--w-head"), 700))
    tokens = {
        "schema": "buildroom-design/1", "name": a.direction or p["name"], "look": p["name"],
        "locked": str(date.today()), "audience": audience, "version": 1,
        "color": col, "dark": dark,
        "font": {"head": {"family": head_f, "fallback": head_fb, "weight": weight,
                          "weights": (pair or {}).get("head", {}).get("weights", [weight])},
                 "body": {"family": body_f, "fallback": body_fb,
                          "weights": (pair or {}).get("body", {}).get("weights", [400, 700])},
                 "pair": (pair or {}).get("name", "custom"),
                 "licence": "check each family's licence tab on fonts.google.com before going live; self-host"},
        "type": {"base_px": base_px, "scale": num(vars_.get("--scale"), 1.25),
                 "measure_ch": num(vars_.get("--measure"), 66), "line_height": num(vars_.get("--leading"), 1.6)},
        "space": {"unit_px": dslib.px(vars_.get("--space", "")) or 8},
        "radius_px": dslib.px(vars_.get("--radius", "")) or 0,
        "shadow": SHADOW_NAMES.get(vars_.get("--shadow", "").strip(), vars_.get("--shadow", "soft")),
        "motion": MOTION_NAMES.get(str(vars_.get("--motion", "1")).strip(), "gentle"),
        "buttons": attrs.get("data-buttons", "solid"), "photo": attrs.get("data-photo", "natural"),
        "hero": attrs.get("data-hero", "split"), "texture": attrs.get("data-texture", "none"),
        "density": attrs.get("data-density", "regular"),
        "eyebrows": attrs.get("data-eyebrows", "off") == "on", "head_italic": attrs.get("data-head-italic", "off") == "on",
        "imagery": {"source": a.imagery, "rules": a.photo_rules or ""},
        "dos": [x.strip() for x in a.do if x.strip()], "donts": [x.strip() for x in a.dont if x.strip()],
        "refs": [x.strip().upper() for x in (a.refs or "").split(",") if x.strip()],
        "vars": {k: v for k, v in vars_.items()}, "attrs": attrs,
    }
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    prev = out / "tokens.json"
    if prev.exists():
        old = dslib.read_json(prev)
        tokens["version"] = int(old.get("version", 1)) + 1
    slides = slides_json(tokens, pair)
    files = {"tokens.css": tokens_css(tokens), "design-system.md": system_md(tokens, slides),
             "fonts.md": fonts_md(tokens, pair)}          # everything is built before anything is written
    if prev.exists():
        shutil.copy2(prev, out / f"tokens-v{tokens['version'] - 1}.json")
    dslib.write_json(prev, tokens)
    dslib.write_json(out / "slides.json", slides)
    for name, text in files.items():
        dslib.write_atomic(out / name, text)
    return {"ok": True, "system": str(out), "name": tokens["name"], "version": tokens["version"],
            "files": ["tokens.json", "tokens.css", "slides.json", "design-system.md", "fonts.md"],
            "dark_mode_problems": dark_problems, "slides_flags": slides["flags"],
            "next": "design_check.py check --page <final page> --tokens " + str(prev)}


def tokens_css(t):
    lines = ["/* Build Room Design System: " + t["name"] + f", version {t['version']}, locked {t['locked']}.",
             "   Paste into any page. Every colour, font and size on the page should come from these. */", ":root {"]
    for k in dslib.COLOR_KEYS:
        lines.append(f"  {dslib.VAR_OF[k]}: {t['color'][k]};")
    f = t["font"]
    lines += [f"  --font-head: \"{f['head']['family']}\", {f['head']['fallback']};" if f["head"]["fallback"] else
              f"  --font-head: \"{f['head']['family']}\";",
              f"  --font-body: \"{f['body']['family']}\", {f['body']['fallback']};" if f["body"]["fallback"] else
              f"  --font-body: \"{f['body']['family']}\";",
              f"  --w-head: {f['head']['weight']};", f"  --size-base: {t['type']['base_px']:g}px;",
              f"  --scale: {t['type']['scale']:g};", f"  --measure: {t['type']['measure_ch']:g}ch;",
              f"  --leading: {t['type']['line_height']:g};", f"  --space: {t['space']['unit_px']:g}px;",
              f"  --radius: {t['radius_px']:g}px;"]
    sh = {v: k for k, v in SHADOW_NAMES.items()}.get(t["shadow"], t["shadow"])
    lines += [f"  --shadow: {sh};", f"  --motion: {({v: k for k, v in MOTION_NAMES.items()}).get(t['motion'], '1')};", "}"]
    if t["dark"]:
        lines.append('[data-theme="dark"] {')
        lines += [f"  {dslib.VAR_OF[k]}: {v};" for k, v in t["dark"].items()]
        lines.append("}")
    lines.append("@media (prefers-reduced-motion: reduce) { :root { --motion: 0; } }")
    return "\n".join(lines) + "\n"


def slides_json(t, pair):
    theme = "dark" if (t.get("attrs", {}).get("data-theme") == "dark" or dslib.luminance(t["color"]["bg"]) < 0.18) else "light"
    acc = dslib.shade_to_contrast(t["color"]["accent"], SLIDE_BG[theme], 4.5)
    font = ((pair or {}).get("slides_fonts") or {}).get("body") or (
        "Georgia" if "serif" in t["font"]["body"]["fallback"] and "sans" not in t["font"]["body"]["fallback"] else "Arial")
    note = "" if acc == t["color"]["accent"] else f"accent darkened from {t['color']['accent']} to {acc} so it reads on slides"
    return {"theme": theme, "accent": acc.lstrip("#").upper(), "font": font,
            "flags": f"--theme {theme} --accent {acc.lstrip('#').upper()} --font \"{font}\"",
            "why_font": "slides open on other computers, so they use a font every computer has; the web fonts stay on the web",
            "note": note}


def system_md(t, slides):
    c, f, ty = t["color"], t["font"], t["type"]
    rows = "\n".join(f"| {LABELS[k]} | `{c[k]}` | `{dslib.VAR_OF[k]}` |" for k in dslib.COLOR_KEYS)
    sizes = [ty["base_px"] * ty["scale"] ** n for n in (4, 3, 2, 1, 0)]
    dark = ("\n**Dark mode:** " + ", ".join(f"{LABELS[k].lower()} `{v}`" for k, v in t["dark"].items()) + "\n") if t["dark"] else ""
    dos = "\n".join(f"- {x}" for x in t["dos"]) or "- Use the accent for one thing per screen: the main button."
    donts = "\n".join(f"- {x}" for x in t["donts"]) or "- No colours or fonts outside this sheet."
    generic = ["- No small uppercase labels over every heading." if not t["eyebrows"] else "",
               "- No italic last word in headlines." if not t["head_italic"] else "",
               "- Never a photo or logo taken from a reference: references are for mood only."]
    refs = ", ".join(t["refs"]) or "see the taste vault"
    img = {"own": "the member's own photos", "kie": "images generated with Kie.ai (logged in the media ledger)",
           "both": "the member's own photos first; Kie.ai for scenes, textures and backgrounds"}[t["imagery"]["source"]]
    return f"""# Design System: {t['name']}

_Version {t['version']} · locked {t['locked']} · for a {'50+' if t['audience'] == '50plus' else 'general'} audience · look "{t['look']}"_

This is how everything you publish looks: your pages, slides, ads, one-pagers and lead magnets. Every Build Room session reads it before it designs anything.

## Colours

| Use | Colour | Variable |
|---|---|---|
{rows}
{dark}
## Fonts

- **Headings:** {f['head']['family']} (weight {f['head']['weight']}). Fallback: {f['head']['fallback'] or 'system'}.
- **Body text:** {f['body']['family']}. Fallback: {f['body']['fallback'] or 'system'}.
- **Pairing:** {f['pair']}. Self-host the files (see `fonts.md`).
- **On slides:** {slides['font']}, because slides open on other computers. Slide flags: `{slides['flags']}`.

## Sizes

- Body text **{ty['base_px']:g}px**, line height {ty['line_height']:g}, lines about {ty['measure_ch']:g} characters long.
- Headings step up by {ty['scale']:g}: {', '.join(f'{s:.0f}px' for s in sizes)}.
- Nothing under 14px, captions and fine print included.

## Shape and feel

- Corners {t['radius_px']:g}px · spacing unit {t['space']['unit_px']:g}px ({t['density']}) · shadows {t['shadow']} · motion {t['motion']}, always off for visitors who ask for less motion.
- Buttons: {t['buttons']}. Top of the page: {t['hero']}. Background: {t['texture']}.

## Photos and images

- Source: {img}.
- Treatment: {t['photo']}.
{('- ' + t['imagery']['rules']) if t['imagery']['rules'] else '- Real people only with their consent; a generated image never shows a real person.'}

## Do

{dos}

## Don't

{donts}
{chr(10).join(x for x in generic if x)}

## The references behind it

{refs} in the taste vault.

## Briefing a designer or VA

Send them this page, `tokens.css` and the logo. Say: "Use only these colours and fonts, at these sizes. Body text never under {ty['base_px']:g}px. One main button per screen, in the accent colour. Photos: {img}. Check contrast before you send anything back."
"""


def fonts_md(t, pair):
    fams = [t["font"]["head"]["family"], t["font"]["body"]["family"]]
    lines = ["# Fonts to self-host", "",
             "Host the font files on your own site instead of loading them from Google's servers: it is faster, and "
             "it avoids sending visitors' details to Google (a German court fined a site for that in 2022).", ""]
    for fam in dict.fromkeys(fams):
        slug = fam.lower().replace(" ", "")
        lines += [f"## {fam}", "",
                  f"- Licence: check https://fonts.google.com/specimen/{fam.replace(' ', '+')} (the licence tab). "
                  "Most are SIL Open Font License: free for commercial use; keep OFL.txt with the files.",
                  f"- Files: https://github.com/google/fonts (search for `{slug}`), or download the family from its "
                  "Google Fonts page. Use the .woff2 files.", ""]
    lines += ["## On the page", "", "```css",
              "@font-face { font-family: \"<Family>\"; src: url(\"fonts/<file>.woff2\") format(\"woff2\");",
              "  font-weight: 400 700; font-display: swap; }", "```", "",
              "While designing, the tweak bar loads them from Google Fonts for the preview only."]
    return "\n".join(lines) + "\n"


def cmd_section(a):
    sysdir = Path(a.system)
    t = dslib.read_json(sysdir / "tokens.json")
    taste = None
    if a.taste_vault and (Path(a.taste_vault) / "taste.json").exists():
        taste = dslib.read_json(Path(a.taste_vault) / "taste.json")
    proj = dslib.read_json(Path(a.project) / "design.json") if a.project and (Path(a.project) / "design.json").exists() else None
    c = t["color"]
    tried = ""
    if proj:
        names = [d["name"] for r in proj["rounds"] for d in r["directions"]]
        pk = proj.get("picked") or {}
        why = "; ".join(x for x in (pk.get("mix"), pk.get("note")) if x)
        tried = f"{', '.join(names)} · chosen {pk.get('name', '—')}" + (f" · {why}" if why else "")
    tv = ""
    if taste:
        tv = (f"{a.taste_vault} · {len(taste['refs'])} references · "
              f"{len({r['collection'] for r in taste['refs']})} collections · \"" + "; ".join(taste.get("read", [])) + "\"")
    lines = [
        f"- **Taste vault** (location · references · collections · \"what I keep choosing\"): {tv or '—'}",
        f"- **Directions tried** (names · chosen · why): {tried or '—'}",
        f"- **Locked system** (palette · fonts · type scale · corners · spacing · motion): {t['name']} v{t['version']} "
        f"({t['locked']}) · bg {c['bg']} ink {c['ink']} accent {c['accent']} · {t['font']['head']['family']} / "
        f"{t['font']['body']['family']} · {t['type']['base_px']:g}px × {t['type']['scale']:g} · "
        f"{t['radius_px']:g}px corners · {t['space']['unit_px']:g}px spacing · motion {t['motion']}",
        f"- **Imagery rules** (own photos / generated · provider · consent): {t['imagery']['source']}"
        + (f" · {t['imagery']['rules']}" if t["imagery"]["rules"] else ""),
        f"- **Do / don't:** {'; '.join(t['dos'][:3]) or '—'} / {'; '.join(t['donts'][:3]) or '—'}",
        f"- **Files** (design-system.md · tokens.json · tokens.css · slides.json · first page): {sysdir}/"
        + (f" · {Path(a.project) / 'page' / 'index.html'}" if a.project else ""),
        "- **Used by** (skills that have read it · last date): —",
    ]
    return {"ok": True, "section": "22", "lines": lines}


def cmd_show(a):
    t = dslib.read_json(Path(a.system) / "tokens.json")
    return {"ok": True, "name": t["name"], "version": t["version"], "locked": t["locked"], "color": t["color"],
            "fonts": [t["font"]["head"]["family"], t["font"]["body"]["family"]], "base_px": t["type"]["base_px"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lock")
    p.add_argument("--tweaks", required=True); p.add_argument("--name"); p.add_argument("--page")
    p.add_argument("--out", required=True); p.add_argument("--direction")
    p.add_argument("--audience", choices=["50plus", "general"]); p.add_argument("--refs")
    p.add_argument("--do", action="append", default=[]); p.add_argument("--dont", action="append", default=[])
    p.add_argument("--imagery", choices=["own", "kie", "both"], default="both"); p.add_argument("--photo-rules")
    p.add_argument("--fonts")
    p = sub.add_parser("section"); p.add_argument("--system", required=True); p.add_argument("--taste-vault")
    p.add_argument("--project")
    p = sub.add_parser("show"); p.add_argument("--system", required=True)
    a = ap.parse_args()
    out = globals()["cmd_" + a.cmd](a)
    dslib.emit(out, 0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
