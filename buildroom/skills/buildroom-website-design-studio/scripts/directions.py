#!/usr/bin/env python3
"""Website Design Studio: the three directions, side by side.

A design project lives in the member's vault at Design/<project>/ (Design/landing-page/ by default).
Each round holds up to three very different takes of the same page, each in its own folder with an
index.html written on the page token contract (dslib.VAR_OF, dslib.SCALAR_VARS, dslib.ATTRS). This
script registers them, builds one side-by-side board, records the member's pick, and holds the cap
of three rounds so the session never turns into a slot machine.

Usage
  directions.py init   --project Design/landing-page [--deliverable "landing page"] [--audience 50plus|general]
                       [--copy path/to/approved-copy.md]
  directions.py new    --project P --name "Field Guide" --idea "…" --for "…" [--refs T-001,T-004,T-009] [--vault V]
                       [--round N]   a full round is refused: start the next one on purpose with --round N
                       writes directions/r<N>-<slug>/index.html as a starter on the token contract
  directions.py board  --project P [--round N] [--inline] [--out directions.html]
                       --inline puts each page's local images and stylesheets inside the board (one file to share)
  directions.py pick   --project P --name "Field Guide" [--round N] [--mix "the hero of Survey"] [--note "…"]
                       copies the chosen page to page/index.html for the tweak bar
  directions.py remove --project P --name "Front Page" [--round N]   takes a direction out (kept in directions/removed-…)
  directions.py status --project P
Every command prints JSON. Exit 1 on a refusal.
"""
import argparse, base64, html, mimetypes, os, re, shutil, sys, urllib.parse
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dslib  # noqa: E402

CAP_ROUNDS, PER_ROUND = 3, 3
DELIVERABLES = ("landing page", "opt-in page", "sales page", "thank-you page", "webinar slides", "one-pager", "other")

STARTER = """<!doctype html>
<html lang="en" data-eyebrows="off" data-head-italic="off" data-buttons="solid" data-photo="natural"
      data-hero="split" data-texture="none" data-density="regular" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<!-- Direction: {name}. {idea}
     Written on the Build Room page token contract: every colour, font and size below comes from these
     variables, and the data- attributes on <html> switch the tweak bar's toggles. -->
<style>
:root {{
  --c-bg: #ffffff; --c-surface: #f3f4f6; --c-ink: #161616; --c-muted: #4a4a4a;
  --c-accent: #1d4ed8; --c-accent-ink: #ffffff; --c-line: #d9d9d9;
  --font-head: "Archivo", system-ui, sans-serif; --font-body: "Source Serif 4", Georgia, serif;
  --w-head: 700; --size-base: {base}px; --scale: 1.25; --measure: 66ch; --leading: 1.6;
  --space: 8px; --radius: 6px; --shadow: 0 1px 2px rgba(0,0,0,.08); --motion: 1;
}}
[data-theme="dark"] {{ --c-bg: #121212; --c-surface: #1d1d1d; --c-ink: #f2f2f2; --c-muted: #bdbdbd; --c-line: #333333; }}
@media (prefers-reduced-motion: reduce) {{ :root {{ --motion: 0; }} }}
body {{ margin: 0; background: var(--c-bg); color: var(--c-ink); font: var(--size-base)/var(--leading) var(--font-body); }}
h1, h2, h3 {{ font-family: var(--font-head); font-weight: var(--w-head); line-height: 1.15; }}
</style>
</head>
<body>
<main>
  <!-- [write: hero — the headline and sub from the approved copy, one primary button] -->
  <!-- [write: the sections from the approved copy, in this direction's own layout] -->
</main>
</body>
</html>
"""


def proj(p):
    return Path(p)


def load(p):
    f = proj(p) / "design.json"
    if not f.exists():
        dslib.emit({"ok": False, "error": f"no design project at {p}; run init first"}, 1)
    return dslib.read_json(f)


def save(p, data):
    dslib.write_json(proj(p) / "design.json", data)


def cmd_init(a):
    f = proj(a.project) / "design.json"
    if f.exists():
        return {"ok": True, "project": str(proj(a.project)), "created": False, **status(dslib.read_json(f))}
    if a.deliverable not in DELIVERABLES:
        dslib.emit({"ok": False, "error": f"--deliverable must be one of {', '.join(DELIVERABLES)}"}, 1)
    data = {"schema": "buildroom-design-project/1", "project": proj(a.project).name, "created": str(date.today()),
            "deliverable": a.deliverable, "audience": a.audience, "copy": a.copy or "", "rounds": [],
            "picked": None, "cap_rounds": CAP_ROUNDS}
    proj(a.project).mkdir(parents=True, exist_ok=True)
    save(a.project, data)
    return {"ok": True, "project": str(proj(a.project)), "created": True, "deliverable": a.deliverable,
            "audience": a.audience}


def current_round(data):
    return data["rounds"][-1]["n"] if data["rounds"] else 0


def cmd_new(a):
    data = load(a.project)
    rnd = a.round or (current_round(data) or 1)
    if not a.round and data["rounds"] and len(data["rounds"][-1]["directions"]) >= PER_ROUND:
        dslib.emit({"ok": False, "error": f"round {rnd} already has {PER_ROUND} directions. A new round is one of only "
                    f"{CAP_ROUNDS}: start it on purpose, after the member asks for more, with --round {rnd + 1}; "
                    "or replace one with directions.py remove"}, 1)
    if rnd > data.get("cap_rounds", CAP_ROUNDS):
        dslib.emit({"ok": False, "error": f"round {rnd} is past the cap of {CAP_ROUNDS} rounds. Pick the closest "
                    "direction and fine-tune it with the tweak bar; say what is still wrong in words."}, 1)
    if rnd > current_round(data) + 1:
        dslib.emit({"ok": False, "error": f"round {current_round(data) + 1} comes next"}, 1)
    if rnd > current_round(data):
        data["rounds"].append({"n": rnd, "started": str(date.today()), "directions": []})
    r = next(x for x in data["rounds"] if x["n"] == rnd)
    slug = dslib.slugify(a.name)
    if any(d["slug"] == slug for d in r["directions"]):
        dslib.emit({"ok": False, "error": f"round {rnd} already has a direction called {a.name}"}, 1)
    if len(r["directions"]) >= PER_ROUND:
        dslib.emit({"ok": False, "error": f"round {rnd} already has {PER_ROUND} directions"}, 1)
    refs = [x.strip().upper() for x in (a.refs or "").split(",") if x.strip()]
    warnings = []
    if len(refs) < 3:
        warnings.append(f"{len(refs)} reference(s) named; each direction should draw on at least three")
    if refs and any(d["refs"][:1] == refs[:1] for d in r["directions"]):
        warnings.append(f"{refs[0]} is already the main reference of another direction in this round")
    if a.vault:
        tj = Path(a.vault) / "Design" / "Taste Vault" / "taste.json"
        known = {x["id"] for x in dslib.read_json(tj).get("refs", [])} if tj.exists() else set()
        missing = [x for x in refs if x not in known]
        if missing:
            dslib.emit({"ok": False, "error": f"not in the taste vault: {', '.join(missing)}"}, 1)
    d = {"name": a.name.strip(), "slug": slug, "idea": a.idea.strip(), "for": a.for_.strip(),
         "refs": refs,
         "dir": f"directions/r{rnd}-{slug}"}
    page = proj(a.project) / d["dir"] / "index.html"
    if not page.exists():
        base = dslib.MIN_BODY_PX_50PLUS if data.get("audience") == "50plus" else dslib.MIN_BODY_PX
        dslib.write_atomic(page, STARTER.format(title=html.escape(a.name), name=html.escape(a.name),
                                                idea=html.escape(a.idea), base=base))
    r["directions"].append(d)
    save(a.project, data)
    return {"ok": True, "round": rnd, "direction": d, "page": str(page), "warnings": warnings,
            "rounds_left_after_this": data.get("cap_rounds", CAP_ROUNDS) - rnd}


LOCAL = re.compile(r"^(https?:|data:|//|#|mailto:|tel:)", re.I)


def _local(base, ref):
    ref = urllib.parse.unquote(re.split(r"[?#]", ref.strip(), 1)[0])
    return (Path(base) / ref).resolve() if ref else None


def inline_assets(page_html, page_dir):
    """Local images (src, srcset, poster), stylesheets and CSS url() made self-contained (data: URIs / <style>).
    A url() inside a linked stylesheet is resolved from that stylesheet's own folder."""
    def data_uri(base, rel):
        if LOCAL.match(rel.strip()):
            return None
        p = _local(base, rel)
        if not p or not p.is_file():
            return None
        mt = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        return f"data:{mt};base64," + base64.b64encode(p.read_bytes()).decode()

    def css_urls(css, base):
        def url(m):
            val = m.group(1).strip().strip("'\"")
            d = data_uri(base, val)
            return f'url("{d}")' if d else m.group(0)
        return re.sub(r"url\(([^)]+)\)", url, css)

    def link(m):
        href = re.search(r'href\s*=\s*["\']([^"\']+)', m.group(0))
        if not href or LOCAL.match(href.group(1)):
            return m.group(0)
        p = _local(page_dir, href.group(1))
        return f"<style>{css_urls(dslib.read_text(p), p.parent)}</style>" if p and p.is_file() else m.group(0)
    out = re.sub(r"<link\b[^>]*rel\s*=\s*[\"']?stylesheet[^>]*>", link, page_html, flags=re.I)

    def src(m):
        d = data_uri(page_dir, m.group(3))
        return f'{m.group(1)}={m.group(2)}{d}{m.group(2)}' if d else m.group(0)
    out = re.sub(r'\b(src|poster)=(["\'])([^"\']+)\2', src, out)

    def srcset(m):
        parts = []
        for item in m.group(3).split(","):
            bits = item.strip().split()
            if bits:
                d = data_uri(page_dir, bits[0])
                parts.append(" ".join([d or bits[0]] + bits[1:]))
        return f'{m.group(1)}={m.group(2)}{", ".join(parts)}{m.group(2)}'
    out = re.sub(r'\b(srcset)=(["\'])([^"\']+)\2', srcset, out)
    return css_urls(out, page_dir)


def cmd_board(a):
    data = load(a.project)
    if not data["rounds"]:
        dslib.emit({"ok": False, "error": "no directions yet: directions.py new …"}, 1)
    rnd = a.round or current_round(data)
    r = next((x for x in data["rounds"] if x["n"] == rnd), None)
    if not r:
        dslib.emit({"ok": False, "error": f"no round {rnd}"}, 1)
    import design_check  # noqa: E402
    cards, problems = [], []
    for i, d in enumerate(r["directions"], 1):
        page = proj(a.project) / d["dir"] / "index.html"
        if not page.exists():
            problems.append(f"{d['name']}: {d['dir']}/index.html is missing")
            continue
        src = dslib.read_text(page)
        if "[write:" in src:
            problems.append(f"{d['name']}: still has [write: …] placeholders")
        tells = design_check.tells(src)
        if a.inline:
            src = inline_assets(src, page.parent)
        else:
            base = f'<base href="{html.escape(d["dir"])}/">'
            hm = re.search(r"<head\b[^>]*>", src, re.I)
            if hm:
                src = src[:hm.end()] + base + src[hm.end():]
            else:
                dm = re.match(r"\s*<!doctype[^>]*>", src, re.I)
                src = (src[:dm.end()] + base + src[dm.end():]) if dm else base + src
        refs = ", ".join(d["refs"]) or "none named"
        t_line = ("no generic tells found" if not tells else
                  f"{len(tells)} generic tell{'s' if len(tells) != 1 else ''}: " + "; ".join(t['name'] for t in tells))
        full = "" if a.inline else f'<a class="btn" href="{html.escape(d["dir"])}/index.html" target="_blank" rel="noopener">Open full size</a>'
        cards.append(f"""<article class="card">
<header><span class="num">{i}</span><div><h2>{html.escape(d['name'])}</h2><p class="idea">{html.escape(d['idea'])}</p></div></header>
<div class="frame" data-w="1280"><iframe title="{html.escape(d['name'])}" loading="lazy" srcdoc="{html.escape(src, quote=True)}"></iframe></div>
<p class="meta"><b>For:</b> {html.escape(d['for'])}<br><b>Draws on:</b> {html.escape(refs)}<br><span class="tells">{html.escape(t_line)}</span></p>
<div class="actions"><button type="button" class="btn phone">Phone view</button>{full}</div>
</article>""")
    out = proj(a.project) / (a.out or f"directions-round-{rnd}.html")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Three Directions</title><style>
:root{{--bg:#f6f6f4;--card:#ffffff;--ink:#1a1a1a;--muted:#555555;--line:#dddddd;--acc:#1d4ed8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141414;--card:#1e1e1e;--ink:#eeeeee;--muted:#aaaaaa;--line:#333333;--acc:#8fb0ff}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.5 system-ui,sans-serif;padding:24px 16px 64px}}
main{{max-width:1500px;margin:0 auto}} h1{{margin:0 0 6px;font-size:1.7rem}} .lead{{color:var(--muted);margin:0 0 20px;max-width:70ch}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,400px),1fr));gap:20px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;min-width:0}}
.card header{{display:flex;gap:12px;align-items:flex-start}} .num{{font-weight:700;font-size:1.3rem;color:var(--acc)}}
h2{{margin:0;font-size:1.2rem}} .idea{{margin:2px 0 12px;color:var(--muted)}}
.frame{{position:relative;width:100%;aspect-ratio:16/11;overflow:hidden;border:1px solid var(--line);border-radius:6px;background:#fff}}
.frame iframe{{position:absolute;top:0;left:0;width:1280px;height:880px;border:0;transform-origin:0 0}}
.frame.phone{{aspect-ratio:auto;height:640px}} .frame.phone iframe{{width:390px;height:844px}}
.meta{{font-size:.93rem;margin:12px 0}} .tells{{color:var(--muted)}}
.actions{{display:flex;gap:10px;flex-wrap:wrap}} .btn{{font:inherit;font-size:.95rem;padding:8px 14px;border-radius:6px;border:1px solid var(--line);background:transparent;color:var(--ink);cursor:pointer;text-decoration:none}}
.btn:focus-visible{{outline:2px solid var(--acc);outline-offset:2px}}
</style></head><body><main>
<h1>Three directions · round {rnd}</h1>
<p class="lead">The same page, three very different ways. Say what you like and what you don't about each, in plain words: "love the photo, hate the green". Then pick one, ask for three more like one of them, or mix two. Round {rnd} of {data.get('cap_rounds', CAP_ROUNDS)}.</p>
<div class="grid">{''.join(cards)}</div></main>
<script>
function fit(){{document.querySelectorAll('.frame').forEach(function(f){{var i=f.querySelector('iframe');var w=f.classList.contains('phone')?390:1280;var s=Math.min(1,f.clientWidth/w);i.style.transform='scale('+s+')';if(f.classList.contains('phone'))f.style.height=(844*s)+'px';}});}}
document.querySelectorAll('.phone').forEach(function(b){{b.addEventListener('click',function(){{var f=b.closest('.card').querySelector('.frame');f.classList.toggle('phone');if(!f.classList.contains('phone'))f.style.height='';b.textContent=f.classList.contains('phone')?'Desktop view':'Phone view';fit();}});}});
if(window.innerWidth<640){{document.querySelectorAll('.phone').forEach(function(b){{b.click();}});}}
window.addEventListener('resize',fit);fit();
</script></body></html>"""
    dslib.write_atomic(out, page)
    return {"ok": not problems, "board": str(out), "round": rnd, "directions": [d["name"] for d in r["directions"]],
            "problems": problems, "inline": bool(a.inline), "bytes": len(page.encode())}


def cmd_pick(a):
    data = load(a.project)
    d = rnd = None
    for r in sorted(data["rounds"], key=lambda x: -x["n"]):
        if a.round and r["n"] != a.round:
            continue
        d = next((x for x in r["directions"] if x["name"].lower() == a.name.lower() or x["slug"] == dslib.slugify(a.name)), None)
        if d:
            rnd = r["n"]
            break
    if not d:
        where = f"round {a.round}" if a.round else "any round"
        dslib.emit({"ok": False, "error": f"no direction '{a.name}' in {where}"}, 1)
    src = proj(a.project) / d["dir"]
    dest = proj(a.project) / "page"
    if dest.exists():
        keep = proj(a.project) / f"page-before-{date.today()}"
        n = 1
        while keep.exists():
            n += 1
            keep = proj(a.project) / f"page-before-{date.today()}-{n}"
        shutil.move(str(dest), keep)
    shutil.copytree(src, dest)
    fix_relative(dest / "index.html", src, dest)
    data["picked"] = {"name": d["name"], "slug": d["slug"], "round": rnd, "date": str(date.today()),
                      "mix": a.mix or "", "note": a.note or ""}
    save(a.project, data)
    return {"ok": True, "picked": data["picked"], "page": str(dest / "index.html"),
            "next": "tweakbar.py add --page " + str(dest / "index.html")}


def fix_relative(page, old_dir, new_dir):
    """A page moved up a folder: rewrite references that climb out of its folder (../../img.png) so they
    still point at the same files."""
    if not page.is_file():
        return
    txt = dslib.read_text(page)

    def fix(ref):
        r = ref.strip()
        if LOCAL.match(r) or not r.startswith("../"):
            return ref
        target = (Path(old_dir) / urllib.parse.unquote(re.split(r"[?#]", r, 1)[0])).resolve()
        rest = r[len(re.split(r"[?#]", r, 1)[0]):]
        return Path(os.path.relpath(target, Path(new_dir).resolve())).as_posix() + rest

    txt = re.sub(r'\b(src|href|poster)=(["\'])([^"\']+)\2', lambda m: f"{m.group(1)}={m.group(2)}{fix(m.group(3))}{m.group(2)}", txt)
    txt = re.sub(r"url\(([\"']?)([^)\"']+)\1\)", lambda m: f"url({m.group(1)}{fix(m.group(2))}{m.group(1)})", txt)
    dslib.write_atomic(page, txt)


def cmd_remove(a):
    data = load(a.project)
    rnd = a.round or current_round(data)
    r = next((x for x in data["rounds"] if x["n"] == rnd), None)
    d = r and next((x for x in r["directions"] if x["slug"] == dslib.slugify(a.name)), None)
    if not d:
        dslib.emit({"ok": False, "error": f"no direction '{a.name}' in round {rnd}"}, 1)
    r["directions"].remove(d)
    if not r["directions"] and r is data["rounds"][-1]:
        data["rounds"].pop()
    folder = proj(a.project) / d["dir"]
    if folder.exists():
        keep = proj(a.project) / "directions" / f"removed-{folder.name}"
        if keep.exists():
            shutil.rmtree(keep)
        shutil.move(str(folder), keep)
    save(a.project, data)
    return {"ok": True, "removed": d["name"], "round": rnd, "kept_in": str(proj(a.project) / "directions" / f"removed-{folder.name}")}


def status(data):
    return {"deliverable": data["deliverable"], "audience": data["audience"],
            "rounds": [{"n": r["n"], "directions": [d["name"] for d in r["directions"]]} for r in data["rounds"]],
            "rounds_left": data.get("cap_rounds", CAP_ROUNDS) - current_round(data), "picked": data["picked"]}


def cmd_status(a):
    return {"ok": True, **status(load(a.project))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("--project", required=True)
    p.add_argument("--deliverable", default="landing page")
    p.add_argument("--audience", choices=["50plus", "general"], default="50plus")
    p.add_argument("--copy")
    p = sub.add_parser("new"); p.add_argument("--project", required=True); p.add_argument("--name", required=True)
    p.add_argument("--idea", required=True); p.add_argument("--for", dest="for_", required=True)
    p.add_argument("--refs"); p.add_argument("--round", type=int); p.add_argument("--vault")
    p = sub.add_parser("remove"); p.add_argument("--project", required=True); p.add_argument("--name", required=True)
    p.add_argument("--round", type=int)
    p = sub.add_parser("board"); p.add_argument("--project", required=True); p.add_argument("--round", type=int)
    p.add_argument("--inline", action="store_true"); p.add_argument("--out")
    p = sub.add_parser("pick"); p.add_argument("--project", required=True); p.add_argument("--name", required=True)
    p.add_argument("--round", type=int); p.add_argument("--mix"); p.add_argument("--note")
    p = sub.add_parser("status"); p.add_argument("--project", required=True)
    a = ap.parse_args()
    out = globals()["cmd_" + a.cmd](a)
    dslib.emit(out, 0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
