#!/usr/bin/env python3
"""Website Design Studio: the taste vault, inside the member's Obsidian vault.

The member drops screenshots of designs they like into Design/Taste Vault/inbox/ (a sub-folder
of the inbox becomes a collection). This script files them, numbers them T-001, T-002 …, reads
the dominant colours where it can, keeps the member's one-word reactions, writes an Obsidian note
and an HTML contact sheet, and reports the patterns for the "what you keep choosing" read.
References are for mood only: nothing in the vault is ever used on a page (design_check.py
refuses a page that does).

Usage
  taste_vault.py init     --vault <obsidian vault>
  taste_vault.py sort     --vault V [--collection unsorted] [--kind gallery|niche|own|other] [--source URL]
  taste_vault.py add      --vault V FILE... [--collection C] [--kind K] [--source URL] [--word W]
  taste_vault.py react    --vault V --id T-003 [--word calm] [--likes "big photo"] [--dislikes "busy"]
                          [--kind niche] [--collection heroes] [--colours "#1f3b2d,#f4efe6"] [--source URL]
  taste_vault.py feedback --vault V --direction "Field Guide" --text "too clean" [--round 1]
  taste_vault.py confirm  --vault V --read "big real photos" --read "one bold colour" ...
  taste_vault.py sheet    --vault V            writes "Taste Vault.md" and contact-sheet.html
  taste_vault.py read     --vault V            JSON: counts, words, colours, the gate, the confirmed read

Kinds: gallery (Pinterest, Dribbble, a design gallery), niche (a business in the member's own field
or a competitor), own (the member's own past material), other.
Every command prints JSON. Exit 1 on a refusal.
"""
import argparse, hashlib, html, re, shutil, sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dslib  # noqa: E402

IMG = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
KINDS = ("gallery", "niche", "own", "other")
MIN_REFS, MIN_WORDS = 5, 3
STOP = set("a an the and or of to in on with for is it this that very too so my i like love not no but "
           "just really bit more less".split())


def tv(vault):
    return Path(vault) / "Design" / "Taste Vault"


def load(vault):
    p = tv(vault) / "taste.json"
    if not p.exists():
        dslib.emit({"ok": False, "error": f"no taste vault at {tv(vault)}; run init first"}, 1)
    return dslib.read_json(p)


def save(vault, data):
    dslib.write_json(tv(vault) / "taste.json", data)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def next_id(data):
    n = max([int(r["id"][2:]) for r in data["refs"]] + [0]) + 1
    return f"T-{n:03d}"


def cmd_init(a):
    root = tv(a.vault)
    if not Path(a.vault).is_dir():
        dslib.emit({"ok": False, "error": f"vault folder not found: {a.vault}"}, 1)
    (root / "inbox").mkdir(parents=True, exist_ok=True)
    (root / "collections").mkdir(parents=True, exist_ok=True)
    p = root / "taste.json"
    created = not p.exists()
    if created:
        save(a.vault, {"schema": "buildroom-taste/1", "created": str(date.today()), "refs": [],
                       "direction_feedback": [], "read": [], "read_confirmed": None})
    readme = root / "inbox" / "README.md"
    if not readme.exists():
        dslib.write_atomic(readme, "# Drop screenshots here\n\nAny design you like: a whole page, a section, a "
                           "colour, a photo style. Put them in a sub-folder (heroes, colours, pages) if you like; "
                           "the sub-folder becomes a collection. Then say \"sort my taste vault\".\n")
    return {"ok": True, "taste_vault": str(root), "created": created, "inbox": str(root / "inbox")}


def _file(a, data, src, collection, kind, source, word):
    h = sha(src)
    for r in data["refs"]:
        if r["sha256"] == h:
            return None, r["id"]
    rid = next_id(data)
    coll = dslib.slugify(collection or "unsorted")
    dest_dir = tv(a.vault) / "collections" / coll
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{rid}{Path(src).suffix.lower()}"
    shutil.copy2(src, dest)
    rec = {"id": rid, "file": str(dest.relative_to(tv(a.vault))), "original_name": Path(src).name,
           "collection": coll, "kind": kind or "other", "source": source or "", "added": str(date.today()),
           "word": word or "", "likes": "", "dislikes": "", "colours": dslib.dominant_colours(dest),
           "sha256": h}
    data["refs"].append(rec)
    return rec, None


def cmd_sort(a):
    data = load(a.vault)
    inbox = tv(a.vault) / "inbox"
    added, dupes = [], []
    for f in sorted(inbox.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in IMG:
            continue
        rel = f.relative_to(inbox)
        coll = rel.parts[0] if len(rel.parts) > 1 else a.collection
        rec, dup = _file(a, data, f, coll, a.kind, a.source, None)
        if rec:
            added.append(rec["id"])
        else:
            dupes.append({"file": str(rel), "same_as": dup})
        f.unlink()
    save(a.vault, data)
    return {"ok": True, "added": added, "duplicates_skipped": dupes, "total": len(data["refs"]),
            "no_colours": [r["id"] for r in data["refs"] if r["id"] in added and not r["colours"]]}


def cmd_add(a):
    data = load(a.vault)
    added, dupes, missing = [], [], []
    for f in a.files:
        p = Path(f)
        if not p.is_file() or p.suffix.lower() not in IMG:
            missing.append(f)
            continue
        rec, dup = _file(a, data, p, a.collection, a.kind, a.source, a.word)
        (added.append(rec["id"]) if rec else dupes.append({"file": f, "same_as": dup}))
    save(a.vault, data)
    return {"ok": not missing, "added": added, "duplicates_skipped": dupes, "not_images": missing,
            "total": len(data["refs"])}


def find(data, rid):
    for r in data["refs"]:
        if r["id"].lower() == rid.lower():
            return r
    dslib.emit({"ok": False, "error": f"no reference {rid}"}, 1)


def cmd_react(a):
    data = load(a.vault)
    r = find(data, a.id)
    for k in ("word", "likes", "dislikes", "source"):
        v = getattr(a, k)
        if v is not None:
            r[k] = v.strip()
    if a.kind:
        r["kind"] = a.kind
    if a.colours:
        cols = [dslib.norm_hex(c) for c in a.colours.split(",")]
        if not all(cols):
            dslib.emit({"ok": False, "error": "colours must be hex, e.g. #1f3b2d,#f4efe6"}, 1)
        r["colours"] = cols
    if a.collection:
        new = dslib.slugify(a.collection)
        if new != r["collection"]:
            old = tv(a.vault) / r["file"]
            dest = tv(a.vault) / "collections" / new / old.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old), dest)
            r["file"], r["collection"] = str(dest.relative_to(tv(a.vault))), new
    save(a.vault, data)
    return {"ok": True, "ref": {k: v for k, v in r.items() if k != "sha256"}}


def cmd_feedback(a):
    data = load(a.vault)
    data["direction_feedback"].append({"date": str(date.today()), "direction": a.direction.strip(),
                                       "round": a.round, "text": a.text.strip()})
    save(a.vault, data)
    return {"ok": True, "feedback_count": len(data["direction_feedback"])}


def cmd_confirm(a):
    data = load(a.vault)
    data["read"] = [x.strip() for x in a.read if x.strip()]
    data["read_confirmed"] = str(date.today()) if data["read"] else None
    save(a.vault, data)
    return {"ok": bool(data["read"]), "read": data["read"], "confirmed": data["read_confirmed"]}


def words(data):
    c = Counter()
    for r in data["refs"]:
        for field in ("word", "likes"):
            for w in re.findall(r"[a-z][a-z'-]+", r.get(field, "").lower()):
                if w not in STOP:
                    c[w] += 1
    d = Counter()
    for r in data["refs"]:
        for w in re.findall(r"[a-z][a-z'-]+", r.get("dislikes", "").lower()):
            if w not in STOP:
                d[w] += 1
    return c, d


def gate(data):
    refs = data["refs"]
    missing = []
    if len(refs) < MIN_REFS:
        missing.append(f"{MIN_REFS - len(refs)} more reference(s): at least {MIN_REFS} before the directions")
    if not any(r["kind"] in ("niche", "own") for r in refs):
        missing.append("one reference from the member's own field (a competitor, a business they admire) "
                       "or their own past material")
    reacted = [r for r in refs if r.get("word")]
    if len(reacted) < MIN_WORDS:
        missing.append(f"a one-word reaction on {MIN_WORDS - len(reacted)} more reference(s)")
    if not data.get("read_confirmed"):
        missing.append("the 'what you keep choosing' read, confirmed by the member (confirm --read …)")
    return {"ready": not missing, "missing": missing}


def summary(data):
    refs = data["refs"]
    likes, dislikes = words(data)
    fam, firsts, accents = Counter(), Counter(), Counter()
    light = dark = 0
    for r in refs:
        cols = r.get("colours") or []
        if cols:
            _, l0, _ = dslib.hls(cols[0])
            light += l0 >= 0.8
            dark += l0 <= 0.25
            firsts[dslib.family(cols[0])] += 1
        for c in cols:
            fam[dslib.family(c)] += 1
            _, l, s = dslib.hls(c)
            if s >= 0.35 and 0.2 <= l <= 0.7:
                accents[dslib.family(c)] += 1
    with_cols = sum(1 for r in refs if r.get("colours"))
    return {
        "refs": len(refs),
        "by_collection": dict(Counter(r["collection"] for r in refs)),
        "by_kind": dict(Counter(r["kind"] for r in refs)),
        "words_liked": likes.most_common(12),
        "words_disliked": dislikes.most_common(8),
        "backgrounds": {"light": light, "dark": dark, "mid": with_cols - light - dark,
                        "read_by_eye": len(refs) - with_cols},
        "background_families": firsts.most_common(5),
        "accent_families": accents.most_common(5),
        "colour_families": fam.most_common(8),
        "direction_feedback": data.get("direction_feedback", [])[-12:],
        "no_colours": [r["id"] for r in refs if not r.get("colours")],
        "read": data.get("read", []), "read_confirmed": data.get("read_confirmed"),
        "gate": gate(data),
    }


def cmd_read(a):
    return {"ok": True, **summary(load(a.vault))}


def cmd_sheet(a):
    data = load(a.vault)
    root = tv(a.vault)
    s = summary(data)
    md = ["# Taste Vault", "", f"_{len(data['refs'])} references · updated {date.today()}_", ""]
    if data.get("read"):
        md += ["## What I keep choosing", ""] + [f"- {x}" for x in data["read"]] + [""]
    by = {}
    for r in data["refs"]:
        by.setdefault(r["collection"], []).append(r)
    for coll, rs in sorted(by.items()):
        md += [f"## {coll.replace('-', ' ').title()}", ""]
        for r in rs:
            bits = [b for b in (r.get("word"), r.get("likes") and "likes: " + r["likes"],
                                r.get("dislikes") and "not: " + r["dislikes"]) if b]
            md += [f"### {r['id']} · {r['kind']}" + (f" · {' · '.join(bits)}" if bits else ""),
                   f"![[{Path(r['file']).name}]]", ""]
            if r.get("source"):
                md += [f"Source: {r['source']}", ""]
            if r.get("colours"):
                md += ["Colours: " + " ".join(f"`{c}`" for c in r["colours"]), ""]
    dslib.write_atomic(root / "Taste Vault.md", "\n".join(md) + "\n")

    cards = []
    for coll, rs in sorted(by.items()):
        items = []
        for r in rs:
            sw = "".join(f'<span class="sw" style="background:{c}" title="{c}"></span>' for c in r.get("colours", []))
            note = " · ".join(html.escape(b) for b in (r.get("word"), r.get("likes"), r.get("dislikes") and "not " + r["dislikes"]) if b)
            items.append(f'<figure><img src="{html.escape(r["file"])}" alt="Reference {r["id"]}" loading="lazy">'
                         f'<figcaption><b>{r["id"]}</b> <span class="k">{html.escape(r["kind"])}</span><br>{note}'
                         f'<div>{sw}</div></figcaption></figure>')
        cards.append(f"<h2>{html.escape(coll.replace('-', ' ').title())}</h2><div class=grid>{''.join(items)}</div>")
    read = "".join(f"<li>{html.escape(x)}</li>" for x in data.get("read", []))
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Taste Vault</title><style>
:root{{--bg:#fafafa;--ink:#1b1b1b;--muted:#5b5b5b;--line:#dddddd}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151515;--ink:#eeeeee;--muted:#a8a8a8;--line:#333333}}}}
body{{margin:0;padding:24px 16px 64px;background:var(--bg);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}
main{{max-width:1200px;margin:0 auto}} h1{{margin:0 0 4px}} h2{{margin:36px 0 12px;font-size:1.2rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}}
figure{{margin:0}} img{{width:100%;border:1px solid var(--line);border-radius:6px;display:block}}
figcaption{{font-size:.9rem;color:var(--muted);margin-top:6px}} .k{{font-size:.75rem;border:1px solid var(--line);border-radius:4px;padding:0 5px}}
.sw{{display:inline-block;width:18px;height:18px;border-radius:3px;margin:4px 4px 0 0;border:1px solid var(--line)}}
</style><main><h1>Taste Vault</h1><p>{s['refs']} references.</p>{'<h2>What I keep choosing</h2><ul>' + read + '</ul>' if read else ''}
{''.join(cards)}</main></html>"""
    dslib.write_atomic(root / "contact-sheet.html", page)
    return {"ok": True, "note": str(root / "Taste Vault.md"), "sheet": str(root / "contact-sheet.html"),
            "refs": s["refs"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("init", "sort", "add", "react", "feedback", "confirm", "sheet", "read"):
        p = sub.add_parser(name)
        p.add_argument("--vault", required=True)
        if name in ("sort", "add"):
            p.add_argument("--collection", default="unsorted")
            p.add_argument("--kind", choices=KINDS)
            p.add_argument("--source")
        if name == "add":
            p.add_argument("files", nargs="+")
            p.add_argument("--word")
        if name == "react":
            p.add_argument("--id", required=True)
            for k in ("word", "likes", "dislikes", "colours", "collection", "source"):
                p.add_argument("--" + k)
            p.add_argument("--kind", choices=KINDS)
        if name == "feedback":
            p.add_argument("--direction", required=True)
            p.add_argument("--text", required=True)
            p.add_argument("--round", type=int, default=1)
        if name == "confirm":
            p.add_argument("--read", action="append", default=[], required=True)
    a = ap.parse_args()
    out = globals()["cmd_" + a.cmd](a)
    dslib.emit(out, 0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
