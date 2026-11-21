#!/usr/bin/env python3
"""The Brand Kit's pictures and pages: the logo files (a wordmark and a small mark, set in real vector outlines),
the directions board (several candidate brands shown in use, side by side) and the brand sheet (the finished kit
as one page a member can send to a designer, a printer or a new hire).
Standard library only. Imported by brandkit.py; not run directly.
"""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brandlib as bl  # noqa: E402

esc = bl.esc


# ---------------------------------------------------------------- fonts
def font_files(font):
    """[(path, weight or None)] from a kit font's "files" list (plain paths or {"src", "weight"})."""
    out = []
    for f in font.get("files") or []:
        if isinstance(f, str):
            out.append((f, None))
        elif isinstance(f, dict) and f.get("src"):
            out.append((f["src"], f.get("weight")))
    return out


def pick_file(font, base, weight=None):
    """The font file closest to `weight`, as an absolute path, or None."""
    files = font_files(font)
    if not files:
        return None
    want = weight or font.get("weight") or 400
    src, _ = min(files, key=lambda fw: abs((fw[1] or want) - want))
    p = (Path(base) / src).resolve()
    return p if p.is_file() else None


def fonts_css(kits, base, out_dir, embed=False):
    """(css, link tag) that loads every font the kits name: local files where the kit has them, Google Fonts otherwise."""
    css, remote, seen = [], [], set()
    for k in kits:
        for role in ("head", "body"):
            f = (k.get("fonts") or {}).get(role) or {}
            fam = f.get("family")
            if not fam or fam.lower() in bl.SYSTEM_FONTS:
                continue
            files = [(Path(base) / s, w) for s, w in font_files(f) if (Path(base) / s).is_file()]
            if files:
                for p, w in files:
                    key = (fam, str(p))
                    if key in seen:
                        continue
                    seen.add(key)
                    url = bl.data_uri(p) if embed else bl.rel(p, out_dir)
                    css.append(f'@font-face{{font-family:"{fam}";src:url("{url}");font-weight:{w or "100 900"};font-display:swap}}')
            elif fam not in remote:
                remote.append(fam)
    link = ""
    if remote:
        q = "&".join("family=" + fam.replace(" ", "+") + ":wght@400;500;600;700;800" for fam in remote)
        link = f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{q}&display=swap">'
    return "".join(css), link


def stack(font, generic="sans-serif"):
    fb = (font.get("fallback") or generic).replace('"', "'")
    return f"'{font.get('family', '')}', {fb}"


# ---------------------------------------------------------------- grounds
def grounds(kit):
    """The kit's own ground and its reverse (text color as the background), each as a full set of working colors."""
    c = kit["colors"]
    rbg = c["ink"] if bl.contrast(c["ink"], c["bg"]) >= 7 else ("#111111" if not bl.is_dark(c["bg"]) else "#ffffff")
    rink = c["bg"] if bl.contrast(c["bg"], rbg) >= 7 else ("#ffffff" if bl.is_dark(rbg) else "#111111")
    racc = c["accent"] if bl.contrast(c["accent"], rbg) >= bl.AA_LARGE else bl.shade_to_contrast(c["accent"], rbg, bl.AA_LARGE)
    over = kit.get("reverse") or {}                   # the kit may name its own accent for the reverse ground
    if bl.norm_hex(over.get("accent")) and bl.contrast(over["accent"], rbg) >= bl.AA_LARGE:
        racc = bl.norm_hex(over["accent"])
    rev = {"bg": rbg, "surface": bl.mix(rbg, rink, 0.08), "ink": rink,
           "muted": bl.shade_to_contrast(bl.mix(rink, rbg, 0.35), rbg, bl.AA_TEXT), "accent": racc,
           "accent_ink": bl.best_on(racc, rbg, rink), "line": bl.mix(rbg, rink, 0.2)}
    return dict(c), rev


def css_vars(col, kit):
    f = kit["fonts"]
    shape = kit.get("shape") or {}
    v = {"--bg": col["bg"], "--surface": col["surface"], "--ink": col["ink"], "--muted": col["muted"], "--accent": col["accent"],
         "--accent-ink": col["accent_ink"], "--line": col["line"], "--fh": stack(f["head"], "serif"), "--fb": stack(f["body"]),
         "--wh": str(f["head"].get("weight", 700)), "--r": f"{shape.get('radius_px', 4)}px"}
    return ";".join(f"{k}:{val}" for k, val in v.items())


# ---------------------------------------------------------------- the logo
def cased(text, case):
    return text.upper() if case == "upper" else text.lower() if case == "lower" else text


def _text_run(font_obj, fam, text, size, tracking, kern, weight, embed_file=None):
    """One line of type as (svg fragment drawn from x=0, baseline y=0; width; top; bottom). Real outlines when the
    font file is a TrueType we can read; otherwise live text, which needs the font wherever the file is opened."""
    if font_obj and all(font_obj.has(ch) or ch == " " for ch in text):
        d, w, box = font_obj.path(text, size, 0, 0, tracking, kern)
        return f'<path d="{d}"/>', box[2], box[1], max(box[3], 0), True
    w = sum(0.6 if ch.isupper() else 0.3 if ch in " il.,'" else 0.52 for ch in text) * size + tracking * size * max(0, len(text) - 1)
    face = f'<style>@font-face{{font-family:"{fam}";src:url("{bl.data_uri(embed_file)}")}}</style>' if embed_file else ""
    frag = (f'{face}<text x="0" y="0" font-family="{esc(fam)}" font-weight="{weight}" font-size="{size}" '
            f'letter-spacing="{tracking * size:.2f}">{esc(text)}</text>')
    return frag, w, -size * 0.74, size * 0.22, False


def logo_parts(kit, base):
    """What a wordmark kit needs to draw its logo: the type run(s), the mark, and whether everything is real outlines."""
    lg = kit["logo"]
    role = lg.get("font", "head")
    font = kit["fonts"][role]
    weight = lg.get("weight") or font.get("weight") or 700
    file = pick_file(font, base, weight)
    fobj = bl.open_font(file) if file else None
    text = cased(lg["text"], lg.get("case", "as-typed"))
    run = _text_run(fobj, font["family"], text, 100, float(lg.get("tracking_em", 0)), lg.get("kern"), weight, file if not fobj else None)
    desc = None
    if lg.get("descriptor"):
        # The second line is set in the text typeface when that can be drawn as outlines, otherwise in the logo's own
        # typeface, so a logo is never half vector shapes and half live text.
        bfont = kit["fonts"]["body"]
        bfile = pick_file(bfont, base, 600)
        bobj = bl.open_font(bfile) if bfile else None
        dtext = cased(lg["descriptor"], lg.get("descriptor_case", "as-typed"))
        if not bobj and fobj and all(fobj.has(ch) or ch == " " for ch in dtext):
            bfont, bfile, bobj = font, file, fobj
        desc = _text_run(bobj, bfont["family"], dtext, 34, float(lg.get("descriptor_tracking_em", 0.04)), None, 600, bfile if not bobj else None)
    mark = lg.get("mark") or {}
    letters = cased(mark.get("letters") or text[:1], mark.get("case", "upper" if lg.get("case") != "lower" else "lower"))
    mrun = _text_run(fobj, font["family"], letters, 100, float(mark.get("tracking_em", 0)), None, weight, file if not fobj else None)
    cap = (fobj.cap / fobj.upm * 100) if fobj else 70
    return {"run": run, "desc": desc, "mrun": mrun, "letters": letters, "cap": cap, "outlined": run[4] and mrun[4] and (not desc or desc[4]),
            "shape": mark.get("shape", "square"), "layout": lg.get("layout", "text"), "radius": (kit.get("shape") or {}).get("radius_px", 4)}


def mark_svg(parts, col, size=100, standalone=True):
    """The small mark: one to three letters, bare or on a square or circle of the accent color."""
    frag, w, top, bottom, _ = parts["mrun"]
    shape = parts["shape"]
    h_letters = bottom - top
    target = {1: 0.52, 2: 0.42}.get(len(parts["letters"]), 0.34) * size
    s = min(target / max(h_letters, 1), (size * 0.72) / max(w, 1)) if shape != "none" else size / max(h_letters, w, 1)
    lw, lh = w * s, h_letters * s
    tx, ty = (size - lw) / 2, (size - lh) / 2 - top * s
    if shape == "none":
        body = f'<g fill="{col["accent"]}" transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})">{frag}</g>'
    else:
        rx = size / 2 if shape == "circle" else min(size * 0.22, parts["radius"] * size / 48)
        body = (f'<rect width="{size}" height="{size}" rx="{rx:.2f}" fill="{col["accent"]}"/>'
                f'<g fill="{col["accent_ink"]}" transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})">{frag}</g>')
    if not standalone:
        return body
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" role="img" aria-label="{esc(parts["letters"])}">{body}</svg>'


def wordmark_svg(parts, col, label):
    """The wordmark, cropped tight to its letters. Clear space is a rule on the brand sheet, not blank space in the file."""
    frag, w, top, bottom, _ = parts["run"]
    x = 0.0
    out = []
    cap = parts["cap"]
    if parts["layout"] == "mark-text":
        m = cap * 1.55
        out.append(f'<g transform="translate(0 {-(cap + m) / 2:.2f})">{mark_svg(parts, col, m, standalone=False)}</g>')
        x = m + cap * 0.42
        top, bottom = min(top, -(cap + m) / 2), max(bottom, (m - cap) / 2)
    out.append(f'<g fill="{col["ink"]}" transform="translate({x:.2f} 0)">{frag}</g>')
    width = x + w
    if parts["desc"]:
        dfrag, dw, dtop, dbottom, _ = parts["desc"]
        dy = bottom + 16 - dtop if parts["layout"] != "mark-text" else max(bottom, 0) + 14 - dtop
        out.append(f'<g fill="{col["muted"]}" transform="translate({x:.2f} {dy:.2f})">{dfrag}</g>')
        bottom, width = dy + dbottom, max(width, x + dw)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {top:.2f} {width:.2f} {bottom - top:.2f}" role="img" '
            f'aria-label="{esc(label)}">{"".join(out)}</svg>')


def logo_set(kit, base):
    """{"on_own": svg, "on_reverse": svg, "mark_own": svg, "mark_reverse": svg, "outlined": bool} for a wordmark kit,
    or image tags for a kit built on the member's own logo files."""
    lg = kit.get("logo") or {}
    own, rev = grounds(kit)
    if lg.get("kind") == "wordmark":
        parts = logo_parts(kit, base)
        return {"kind": "wordmark", "on_own": wordmark_svg(parts, own, kit["name"]), "on_reverse": wordmark_svg(parts, rev, kit["name"]),
                "mark_own": mark_svg(parts, own), "mark_reverse": mark_svg(parts, rev), "outlined": parts["outlined"]}
    if lg.get("kind") == "files":
        # Only what the member really has. A logo is never shown on a ground it was not made for: where a version
        # is missing, the business name is set in type instead, so the gap is plain to see.
        pick = (lambda light, dark: dark if bl.is_dark(own["bg"]) else light)
        on_light, on_dark, mark_l, mark_d = (lg.get(x) for x in ("on_light", "on_dark", "mark_on_light", "mark_on_dark"))
        return {"kind": "files", "on_own": pick(on_light, on_dark), "on_reverse": pick(on_dark, on_light),
                "mark_own": pick(mark_l, mark_d), "mark_reverse": pick(mark_d, mark_l), "outlined": True}
    return {"kind": "none"}


def logo_inner(ls, key, base, out_dir, kit, embed=False):
    """The logo itself: inline vector for a wordmark kit, an image for the member's own file, "" when there is none."""
    if ls["kind"] == "wordmark":
        return ls[key]
    if ls["kind"] == "files" and ls.get(key):
        p = Path(base) / ls[key]
        src = bl.data_uri(p) if embed and p.is_file() else bl.rel(p, out_dir)
        return f'<img src="{esc(src)}" alt="{esc(kit["name"])} logo">'
    return ""


def logo_html(ls, key, base, out_dir, kit, cls="logo", embed=False):
    inner = logo_inner(ls, key, base, out_dir, kit, embed)
    if inner:
        return f'<span class="{cls}">{inner}</span>'
    return f'<span class="{cls} typed">{esc(kit["name"])}</span>'


# ---------------------------------------------------------------- the kit in use
APP_CSS = """
.k{background:var(--bg);color:var(--ink);font-family:var(--fb)}
.k *{box-sizing:border-box}
.app{container-type:inline-size;overflow:hidden;position:relative;font-family:var(--fb)}
.app > div{background:var(--bg);color:var(--ink)}
.app .logo{display:block;line-height:0}.app .logo svg,.app .logo img{height:100%;width:auto;display:block}
.app .logo.typed{font-family:var(--fh);font-weight:var(--wh);line-height:1}
.post{aspect-ratio:4/5;padding:9cqw;display:flex;flex-direction:column}
.post .logo{height:7.4cqw;font-size:5cqw}
.post h4{font:var(--wh) 10.4cqw/1.06 var(--fh);letter-spacing:-.015em;margin:auto 0 0;text-wrap:balance}
.post h4 b{font-weight:inherit;color:var(--accent)}
.post .by{margin-top:7cqw;padding-top:4cqw;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;font-size:3.5cqw;color:var(--muted);gap:4cqw}
.post .by .logo{height:8cqw;flex:none}
.site{aspect-ratio:16/10;display:grid;grid-template-columns:1.15fr .85fr}
.site .l{padding:5cqw 5cqw 5cqw 5.5cqw;display:flex;flex-direction:column;min-width:0}
.site .nav{display:flex;justify-content:space-between;align-items:center}
.site .nav .logo{height:3.6cqw;font-size:2.8cqw}
.site .nav i{display:flex;gap:2.4cqw}.site .nav i span{width:5cqw;height:.7cqw;background:var(--line);border-radius:9px}
.site h4{font:var(--wh) 5.6cqw/1.08 var(--fh);letter-spacing:-.015em;margin:auto 0 0;text-wrap:balance}
.site p{font-size:2.15cqw;line-height:1.5;color:var(--muted);margin:2.2cqw 0 0;max-width:38ch}
.site .btn{display:inline-block;align-self:flex-start;margin-top:3cqw;background:var(--accent);color:var(--accent-ink);font-weight:700;font-size:2.1cqw;padding:1.5cqw 2.6cqw;border-radius:var(--r)}
.site .r{background:var(--accent);position:relative;overflow:hidden}
.site .r .logo{position:absolute;width:150%;left:-18%;top:-12%;height:auto;opacity:.16}
.site .r .logo svg,.site .r .logo img{width:100%;height:auto}
.site .r img.ph{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.sig{padding:7cqw;display:flex;gap:6cqw;align-items:center;border:1px solid var(--line)}
.sig .logo{height:17cqw;flex:none}
.sig.stack{flex-direction:column;align-items:flex-start;gap:4cqw}.sig.stack .logo{height:8cqw;font-size:6cqw}
.sig b{display:block;font:var(--wh) 5.4cqw/1.2 var(--fh)}.sig span{display:block;font-size:4cqw;color:var(--muted);margin-top:1cqw}
.sizes{display:flex;align-items:flex-end;gap:14px;padding:16px;border:1px solid var(--line)}
.sizes .logo{display:block;line-height:0;border-radius:50%;overflow:hidden;flex:none}
.sizes .logo svg,.sizes .logo img{width:100%;height:100%;display:block;object-fit:cover}
.sizes small{font-size:12px;color:var(--muted);margin-left:auto;align-self:center;max-width:16ch;text-align:right;line-height:1.35}
"""


def emph(text):
    """Member copy with *marked* words carried by the accent color. Everything else is escaped as it stands."""
    return re.sub(r"\*([^*]+)\*", r"<b>\1</b>", esc(text))


def app_post(kit, ls, col, key, mkey, base, out, sample, embed=False):
    by = " · ".join(x for x in (sample.get("person"), sample.get("role")) if x) or kit["name"]
    return (f'<div class="app" style="{css_vars(col, kit)}"><div class="post">{logo_html(ls, key, base, out, kit, embed=embed)}'
            f'<h4>{emph(sample["headline"])}</h4><div class="by"><span>{esc(by)}</span>{logo_html(ls, mkey, base, out, kit, embed=embed) if ls.get(mkey) else ""}</div></div></div>')


def app_site(kit, ls, col, key, mkey, base, out, sample, embed=False):
    photo = sample.get("photo")
    right = (f'<img class="ph" src="{esc(bl.data_uri(Path(base) / photo) if embed else bl.rel(Path(base) / photo, out))}" alt="">'
             if photo and (Path(base) / photo).is_file() else (logo_html(ls, mkey, base, out, kit, embed=embed) if ls["kind"] == "wordmark" else ""))
    btn = f'<span class="btn">{esc(sample["cta"])}</span>' if sample.get("cta") else ""
    return (f'<div class="app" style="{css_vars(col, kit)}"><div class="site"><div class="l"><div class="nav">{logo_html(ls, key, base, out, kit, embed=embed)}'
            f'<i><span></span><span></span><span></span></i></div><h4>{emph(sample["headline"]).replace("<b>", "").replace("</b>", "")}</h4>'
            f'<p>{esc(sample["body"])}</p>{btn}</div><div class="r">{right}</div></div></div>')


def app_sig(kit, ls, col, mkey, key, base, out, sample, embed=False):
    if not sample.get("person"):
        return ""
    wide = not ls.get(mkey)
    logo = logo_html(ls, key if wide else mkey, base, out, kit, embed=embed)
    return (f'<div class="app" style="{css_vars(col, kit)}"><div class="sig{" stack" if wide else ""}">{logo}'
            f'<div><b>{esc(sample["person"])}</b><span>{esc(" · ".join(x for x in (sample.get("role"), kit.get("business") or kit["name"]) if x))}</span></div></div></div>')


def app_sizes(kit, ls, col, mkey, base, out, embed=False):
    if not ls.get(mkey):
        return ""
    dots = "".join(f'<span class="logo" style="width:{s}px;height:{s}px">{logo_inner(ls, mkey, base, out, kit, embed)}</span>' for s in (96, 48, 24))
    return f'<div class="sizes" style="{css_vars(col, kit)};background:var(--bg)">{dots}<small>The mark at profile-photo, comment and browser-tab size</small></div>'


def swatches(kit):
    c = kit["colors"]
    named = [(p.get("name") or bl.family(p["hex"]).title(), bl.norm_hex(p["hex"]), p.get("role") or "") for p in kit.get("palette") or [] if bl.norm_hex(p.get("hex"))]
    if not named:
        named = [(bl.LABELS[k], c[k], "") for k in ("accent", "ink", "bg")]
    out = []
    for name, hx, role in named:
        r, g, b = bl.rgb(hx)
        on = bl.best_on(hx, c["ink"], c["bg"])
        out.append(f'<div class="sw" style="background:{hx};color:{on}"><b>{esc(name)}</b><span>{hx.upper()}</span><span>RGB {r} {g} {b}</span>'
                   f'{f"<em>{esc(role)}</em>" if role else ""}</div>')
    return "".join(out)


# ---------------------------------------------------------------- the directions board
BOARD_CSS = """
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:#fff;color:#16181b;font:16px/1.5 system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
header.top{padding:40px clamp(16px,4vw,56px) 28px;border-bottom:1px solid #e3e5e8}
header.top h1{font-size:clamp(26px,3.4vw,40px);line-height:1.1;margin:0 0 10px;letter-spacing:-.02em}
header.top p{margin:0;max-width:70ch;color:#4b5158;font-size:17px}
nav.jump{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid #e3e5e8;padding:10px clamp(16px,4vw,56px);display:flex;gap:8px;flex-wrap:wrap}
nav.jump a{color:#16181b;text-decoration:none;border:1px solid #cfd3d8;border-radius:6px;padding:8px 14px;font-weight:600;font-size:15px}
nav.jump a:hover{background:#f3f4f6}
section.dir{padding:48px clamp(16px,4vw,56px) 56px;border-bottom:1px solid #e3e5e8}
.dh{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:24px 48px;align-items:end;margin-bottom:32px}
.dh h2{font-size:clamp(24px,3vw,34px);margin:0;letter-spacing:-.02em;line-height:1.1}
.dh h2 small{display:block;font-size:14px;font-weight:600;color:#6b7178;letter-spacing:0;margin-bottom:6px}
.dh p{margin:0;font-size:17px;color:#2b2f34}.dh p + p{margin-top:8px;font-size:15px;color:#5b6168}
.grid{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:32px 48px;align-items:start}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.tile{aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;padding:12%;border:1px solid #e3e5e8}
.tile .logo{display:block;width:100%;line-height:0;text-align:center}.tile .logo svg,.tile .logo img{max-width:100%;max-height:72px;width:auto;height:auto}
.tile .logo.typed{font:var(--wh) 28px/1 var(--fh);color:var(--ink)}
.sws{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:0;margin-top:20px;border:1px solid #e3e5e8}
.sw{padding:14px 14px 16px;min-height:118px;display:flex;flex-direction:column;justify-content:flex-end;font-size:13px;line-height:1.4}
.sw b{font-size:14px}.sw em{font-style:normal;opacity:.85;margin-top:4px}
.spec{margin-top:20px;border:1px solid #e3e5e8;padding:22px 24px;background:var(--bg)}
.spec .big{font:var(--wh) 44px/1.05 var(--fh);letter-spacing:-.015em;color:var(--ink)}
.spec .bod{font:400 var(--base)/1.55 var(--fb);color:var(--ink);margin-top:14px;max-width:60ch}
.spec .cap{font-size:13px;color:#5b6168;margin-top:14px}
.apps{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,5fr);gap:16px;align-items:start}
.apps .wide{grid-column:1/-1}
.cap2{font-size:13px;color:#6b7178;margin:6px 0 0}
.note{margin:28px clamp(16px,4vw,56px) 48px;max-width:75ch;color:#4b5158;font-size:15px}
.shadow{box-shadow:0 0 0 1px #e3e5e8}
@media (max-width:860px){.dh,.grid,.apps{grid-template-columns:minmax(0,1fr)}.apps .wide{grid-column:auto}}
@media print{nav.jump{display:none}section.dir{break-inside:avoid-page}}
"""


def _dir_section(i, k, base, out, sample, embed):
    ls = logo_set(k, base)
    own, rev = grounds(k)
    f = k["fonts"]
    base_px = (k.get("type") or {}).get("base_px", 18)
    sig = app_sig(k, ls, own, "mark_own", "on_own", base, out, sample, embed)
    return f"""<section class="dir" id="d{i}" style="{css_vars(own, k)};--base:{base_px}px">
<div class="dh"><h2><small>Direction {i}</small>{esc(k['name'])}</h2><div><p>{esc(k.get('idea', ''))}</p><p>Where it comes from: {esc(k.get('from', ''))}</p></div></div>
<div class="grid"><div>
 <div class="tiles"><div class="tile" style="background:{own['bg']}">{logo_html(ls, 'on_own', base, out, k, embed=embed)}</div>
 <div class="tile" style="background:{rev['bg']};{css_vars(rev, k)}">{logo_html(ls, 'on_reverse', base, out, k, embed=embed)}</div></div>
 <div class="sws">{swatches(k)}</div>
 <div class="spec"><div class="big">{esc(f['head']['family'])}</div><div class="bod">{esc(sample['body'])}</div>
 <div class="cap">Headings in {esc(f['head']['family'])} {esc(f['head'].get('weight', 700))} · text in {esc(f['body']['family'])} at {base_px}px</div></div>
 <div style="margin-top:20px">{app_sizes(k, ls, own, 'mark_own', base, out, embed)}</div>
</div><div class="apps">
 <div><div class="shadow">{app_post(k, ls, own, 'on_own', 'mark_own', base, out, sample, embed)}</div><p class="cap2">A LinkedIn post image</p></div>
 <div><div class="shadow">{app_post(k, ls, rev, 'on_reverse', 'mark_reverse', base, out, sample, embed)}</div><p class="cap2">The same image, reversed</p></div>
 <div class="wide"><div class="shadow">{app_site(k, ls, own, 'on_own', 'mark_reverse', base, out, sample, embed)}</div><p class="cap2">The top of a web page</p></div>
 {f'<div class="wide">{sig}<p class="cap2">An email signature</p></div>' if sig else ''}
</div></div></section>"""


def board_html(business, kits, sample, base, out_dir, embed=False):
    css, link = fonts_css(kits, base, out_dir, embed)
    jump = "".join(f'<a href="#d{i}">{i}. {esc(k["name"])}</a>' for i, k in enumerate(kits, 1))
    secs = "".join(_dir_section(i, k, base, out_dir, sample, embed) for i, k in enumerate(kits, 1))
    n = {2: "Two", 3: "Three", 4: "Four"}.get(len(kits), str(len(kits)))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(business)}: brand directions</title>{link}<style>{css}{BOARD_CSS}{APP_CSS}</style></head><body>
<header class="top"><h1>{n} directions for {esc(business)}</h1>
<p>Each one is a complete brand: a logo, colors, typefaces and how they look in use. The words are yours, so judge the look, not the copy. Pick one, or say what you would take from each.</p></header>
<nav class="jump" aria-label="Directions">{jump}</nav>
{secs}
<p class="note">Nothing here is final. The logo is your name set in type, drawn as real vector shapes. No picture symbol was generated: a drawn symbol is a job for a designer, and the finished kit includes a brief for one if you want it.</p>
</body></html>"""


# ---------------------------------------------------------------- the brand sheet
SHEET_CSS = """
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:var(--base)/1.55 var(--fb)}
.wrap{max-width:1120px;margin:0 auto;padding:0 clamp(16px,4vw,48px)}
.cover{min-height:56vh;display:flex;flex-direction:column;justify-content:space-between;padding-top:48px;padding-bottom:40px;border-bottom:1px solid var(--line)}
.cover .logo{display:block;line-height:0;max-width:min(620px,82%)}.cover .logo svg,.cover .logo img{width:100%;height:auto;max-height:240px}
.cover .logo.typed{font:var(--wh) clamp(40px,8vw,96px)/1 var(--fh)}
.cover dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px 32px;margin:0;font-size:15px}
.cover dt{color:var(--muted)}.cover dd{margin:2px 0 0;font-weight:600}
.cover .ttl{font:var(--wh) clamp(18px,2.2vw,24px)/1.2 var(--fh);margin:0 0 16px}
section.s{padding:64px 0;border-bottom:1px solid var(--line)}
section.s h2{font:var(--wh) clamp(28px,4vw,44px)/1.1 var(--fh);letter-spacing:-.015em;margin:0 0 8px}
section.s p.lead{margin:0 0 32px;max-width:62ch;color:var(--muted)}
h3{font:var(--wh) 20px/1.25 var(--fh);margin:32px 0 10px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}.three{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.tile{display:flex;align-items:center;justify-content:center;padding:9% 12%;border:1px solid var(--line);min-height:200px}
.tile .logo{display:block;width:100%;line-height:0;text-align:center}.tile .logo svg,.tile .logo img{max-width:100%;max-height:96px;width:auto;height:auto}
.tile .logo.typed{font:var(--wh) 34px/1 var(--fh);color:var(--ink)}
.tile.mk .logo svg,.tile.mk .logo img{max-height:120px}
.clear{position:relative;display:inline-block;padding:var(--cs);outline:1px dashed var(--muted);outline-offset:-1px;line-height:0}
.clear .logo svg,.clear .logo img{height:64px;width:auto;max-width:100%}
ul.rules{margin:0;padding-left:1.15em;max-width:66ch}ul.rules li{margin:6px 0}
.sws{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));border:1px solid var(--line)}
.sw{padding:18px 18px 20px;min-height:170px;display:flex;flex-direction:column;justify-content:flex-end;font-size:14px;line-height:1.45}
.sw b{font:var(--wh) 18px/1.2 var(--fh)}.sw em{font-style:normal;margin-top:6px}
table{border-collapse:collapse;width:100%;font-size:16px}th,td{text-align:left;padding:10px 12px 10px 0;border-bottom:1px solid var(--line);vertical-align:top}
th{font-weight:600;color:var(--muted);font-size:14px}
td .chip{display:inline-block;width:18px;height:18px;border:1px solid var(--line);vertical-align:-3px;margin-right:8px}
.pair{display:inline-block;padding:4px 10px;font-weight:700;border-radius:var(--r)}
.scroll{overflow-x:auto}
.spec .big{font:var(--wh) clamp(56px,11vw,132px)/.95 var(--fh);letter-spacing:-.02em}
.spec .fam{font-size:15px;color:var(--muted);margin-top:10px}
.scale div{border-top:1px solid var(--line);padding:12px 0;display:grid;grid-template-columns:90px 1fr;align-items:baseline;gap:16px}
.scale small{font-size:14px;color:var(--muted)}
.apps{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;align-items:start}.apps .wide{grid-column:1/-1}
.shadow{box-shadow:0 0 0 1px var(--line)}
.cap2{font-size:14px;color:var(--muted);margin:6px 0 0}
.dd{display:grid;grid-template-columns:1fr 1fr;gap:32px}
.brief{border:1px solid var(--line);padding:24px;background:var(--surface);max-width:70ch}
footer{padding:32px 0 56px;font-size:14px;color:var(--muted)}
@media (max-width:760px){.two,.three,.apps,.dd{grid-template-columns:minmax(0,1fr)}.apps .wide{grid-column:auto}}
@media print{section.s{break-inside:avoid-page;padding:36px 0}.cover{min-height:auto;gap:120px}body{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""

USE = {"bg": "The page itself.", "surface": "Panels, cards and table stripes.", "ink": "All text, and the logo on a light ground.",
       "muted": "Captions and secondary text. Never smaller than 14px.", "accent": "The one main button, and links. One job per screen.",
       "accent_ink": "Text on the accent color.", "line": "Borders and dividers."}


def sheet_html(kit, base, out_dir, files, version, locked, embed=False):
    ls = logo_set(kit, base)
    own, rev = grounds(kit)
    f, c = kit["fonts"], kit["colors"]
    ty = kit.get("type") or {}
    base_px, scale = ty.get("base_px", 18), ty.get("scale", 1.25)
    css, link = fonts_css([kit], base, out_dir, embed)
    sample = kit.get("sample") or {}
    L = lambda key, cls="logo": logo_html(ls, key, base, out_dir, kit, cls=cls, embed=embed)
    src = {"uploaded": "Your own brand, taken in and checked", "website": "Read from your website, confirmed by you",
           "created": "Created in Build Room OS"}.get(kit.get("source"), "")
    wordmark = ls["kind"] == "wordmark"
    logo_rules = ["Keep clear space around the logo of at least the height of its capital letter, on every side.",
                  "On screen the wordmark is never narrower than 120 pixels. In print, never narrower than 25 mm. The small mark is never under 24 pixels.",
                  "Use the dark-ground version on dark backgrounds and photographs. Put a plain panel behind the logo on a busy photo.",
                  "Never stretch it, tilt it, recolor it outside this palette, or add a shadow, an outline or a glow."]
    if wordmark and not ls["outlined"]:
        logo_rules.append("These logo files carry live text, so they need the font installed wherever they are opened. A designer can convert them to outlines in a few minutes.")
    gap = ""
    if ls["kind"] == "files" and not (ls.get("on_own") and ls.get("on_reverse")):
        which = "dark" if (ls.get("on_own") and not bl.is_dark(own["bg"])) or (ls.get("on_reverse") and bl.is_dark(own["bg"])) else "light"
        gap = (f'<p class="cap2">There is no logo file for {which} backgrounds yet. Until there is one, the business name is set in type there, as shown. '
               f'Ask whoever made the logo for a version for {which} backgrounds.</p>')
        logo_rules[2] = f"Use the logo only on {'light' if which == 'dark' else 'dark'} backgrounds until a version for {which} backgrounds exists. Never place it on a busy photo without a plain panel behind it."
    mark_tiles = [f'<div class="tile mk" style="background:{g["bg"]}">{L(key)}</div>' for key, g in (("mark_own", own), ("mark_reverse", rev)) if ls.get(key)]
    marks = (f'<div class="two" style="margin-top:16px">{"".join(mark_tiles)}</div>'
             '<p class="cap2">The small mark, for profile pictures, browser tabs and anywhere the full name will not fit.</p>') if mark_tiles else ""
    if ls["kind"] == "files" and not mark_tiles:
        logo_rules[1] = "On screen the logo is never narrower than 120 pixels. In print, never narrower than 25 mm. There is no small square mark yet: ask whoever made the logo for one, for profile pictures and browser tabs."
    rows = "".join(f'<tr><td><span class="chip" style="background:{c[k]}"></span>{bl.LABELS[k]}</td><td>{c[k].upper()}</td><td>{USE[k]}</td></tr>' for k in bl.COLOR_KEYS)
    pair_name = {("ink", "bg"): "Text on the page", ("muted", "bg"): "Quiet text on the page", ("ink", "surface"): "Text on a panel",
                 ("accent_ink", "accent"): "Text on the accent", ("accent", "bg"): "The accent on the page"}
    pairs = "".join(f'<tr><td><span class="pair" style="background:{c[b]};color:{c[a]}">{pair_name[(a, b)]}</span></td>'
                    f'<td>{bl.contrast(c[a], c[b])}:1</td><td>needs {need}:1</td></tr>' for a, b, need in bl.PAIRS)
    sizes = [(n, base_px * scale ** n) for n in (4, 3, 2, 1)]
    head = sample.get("headline", kit["name"]).replace("*", "")

    def fit(text, px):
        out = ""
        for w in text.split():
            if len(out) + len(w) + 1 > 1000 / px:
                break
            out = (out + " " + w).strip()
        return out or text[:int(1000 / px)]
    scale_rows = "".join(f'<div><small>{px:.0f}px</small><span style="font:var(--wh) {px:.0f}px/1.1 var(--fh)">{esc(fit(head, px))}</span></div>' for n, px in sizes)
    dos = "".join(f"<li>{esc(x)}</li>" for x in kit.get("dos") or [])
    donts = "".join(f"<li>{esc(x)}</li>" for x in kit.get("donts") or [])
    photo = kit.get("photo") or {}
    apps = ""
    if sample.get("headline") and sample.get("body"):
        sig = app_sig(kit, ls, own, "mark_own", "on_own", base, out_dir, sample, embed)
        apps = f"""<section class="s"><div class="wrap"><h2>In use</h2><p class="lead">The same few parts, wherever your business shows up.</p>
<div class="apps"><div><div class="shadow">{app_post(kit, ls, own, 'on_own', 'mark_own', base, out_dir, sample, embed)}</div><p class="cap2">A LinkedIn post image</p></div>
<div><div class="shadow">{app_post(kit, ls, rev, 'on_reverse', 'mark_reverse', base, out_dir, sample, embed)}</div><p class="cap2">The same image, reversed</p></div>
<div class="wide"><div class="shadow">{app_site(kit, ls, own, 'on_own', 'mark_reverse', base, out_dir, sample, embed)}</div><p class="cap2">The top of a web page</p></div>
{f'<div>{sig}<p class="cap2">An email signature</p></div>' if sig else ''}
<div>{app_sizes(kit, ls, own, 'mark_own', base, out_dir, embed)}</div></div></div></section>"""
    file_rows = "".join(f"<tr><td>{esc(n)}</td><td>{esc(w)}</td></tr>" for n, w in files)
    lic = lambda x: {"ofl": "open license (SIL OFL), free for commercial use", "apache": "open license (Apache 2.0), free for commercial use",
                     "google": "open license, from Google Fonts", "bought": "a license you bought: check that it covers web and social use",
                     "system": "comes with the computer", "unknown": "license not confirmed yet"}.get((x.get("license") or "unknown").lower(), x.get("license"))
    brief = ""
    if wordmark:
        brief = f"""<h3>If you want a drawn symbol later</h3><div class="brief"><p style="margin-top:0">This logo is your name set in type. That is a complete, professional logo, and many well-known firms use nothing more. If you later want a drawn symbol beside it, hire a designer and send them this page. Say:</p>
<p style="margin-bottom:0">"Here is our brand kit. Keep the typeface, the colors and the wordmark as they are. Design one simple symbol that sits to the left of the wordmark and also works alone as a profile picture at 24 pixels, in one color. Deliver vector files (SVG and PDF) for a light and a dark ground."</p></div>"""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(kit['name'])}: brand kit</title>{link}<style>{css}:root{{{css_vars(own, kit)};--base:{base_px}px;--cs:28px}}{SHEET_CSS}{APP_CSS}</style></head><body>
<header class="cover wrap">{L('on_own')}<div><p class="ttl">Brand kit</p><dl><div><dt>Business</dt><dd>{esc(kit['name'])}</dd></div><div><dt>Version</dt><dd>{version} · {esc(locked)}</dd></div>
<div><dt>Source</dt><dd>{esc(src)}</dd></div><div><dt>Built for</dt><dd>{'readers aged 50 and over' if kit.get('audience', '50plus') == '50plus' else 'a general audience'}</dd></div></dl></div></header>
<section class="s"><div class="wrap"><h2>Logo</h2><p class="lead">{'Your name, set in ' + esc(f[(kit['logo'].get('font') or 'head')]['family']) + ' and drawn as vector shapes, so it stays sharp at any size.' if wordmark else 'Your logo, as you supplied it.' if ls['kind'] == 'files' else 'There is no logo file yet. Wherever a logo would go, the business name is set in the heading typeface.'}</p>
<div class="two"><div class="tile" style="background:{own['bg']}">{L('on_own')}</div><div class="tile" style="background:{rev['bg']};{css_vars(rev, kit)}">{L('on_reverse')}</div></div>
{gap}{marks}
<h3>Rules</h3><ul class="rules">{''.join(f'<li>{esc(r)}</li>' for r in logo_rules)}</ul>{brief}</div></section>
<section class="s"><div class="wrap"><h2>Color</h2><p class="lead">A small palette, each color with one job. Every text pairing below has been measured for readability.</p>
<div class="sws">{swatches(kit)}</div>
<h3>Where each color goes</h3><div class="scroll"><table><tr><th>Job</th><th>Color</th><th>Use it for</th></tr>{rows}</table></div>
<h3>Readable pairings</h3><div class="scroll"><table><tr><th>Pairing</th><th>Contrast</th><th>Standard</th></tr>{pairs}</table></div></div></section>
<section class="s spec"><div class="wrap"><h2>Type</h2><p class="lead">Two typefaces. Headings carry the character, the text face does the reading.</p>
<div class="dd"><div><div class="big">Aa</div><div class="fam">{esc(f['head']['family'])} · weight {esc(f['head'].get('weight', 700))} · headings · {esc(lic(f['head']))}</div></div>
<div><div class="big" style="font-family:var(--fb);font-weight:400">Aa</div><div class="fam">{esc(f['body']['family'])} · text · {esc(lic(f['body']))}</div></div></div>
<h3>Sizes</h3><div class="scale">{scale_rows}<div><small>{base_px}px</small><span>{esc(sample.get('body') or 'Body text is set at this size, with lines about 60 to 70 characters long.')}</span></div></div>
<ul class="rules" style="margin-top:20px"><li>Body text is never smaller than {base_px}px on a page. Nothing anywhere is smaller than 14px.</li><li>Slides and documents that open on other computers use a font every computer has. The brand typefaces stay on the web and in images.</li></ul></div></section>
{apps}
<section class="s"><div class="wrap"><h2>Photos and rules</h2><p class="lead">{esc(photo.get('rules') or 'Real photos of real people, with their consent. A generated image never shows a real person.')}</p>
<div class="dd"><div><h3 style="margin-top:0">Do</h3><ul class="rules">{dos or '<li>Use the accent color for one thing per screen: the main button.</li>'}</ul></div>
<div><h3 style="margin-top:0">Do not</h3><ul class="rules">{donts or '<li>No colors or typefaces outside this page.</li>'}</ul></div></div></div></section>
<section class="s"><div class="wrap"><h2>Files</h2><p class="lead">Everything sits in one folder. Send this page and the logo files to anyone who makes something for you.</p>
<div class="scroll"><table><tr><th>File</th><th>What it is for</th></tr>{file_rows}</table></div></div></section>
<footer class="wrap">{esc(kit['name'])} brand kit · version {version} · {esc(locked)}. A name used as a logo is not automatically free to register as a trademark. Check with a trademark professional before you register it.</footer>
</body></html>"""
