#!/usr/bin/env python3
"""Speaking Engine: the speaker one-sheet, the single page a host asks for.

  one_sheet.py template [--folder speaking]              writes speaking/one-sheet/one-sheet.json to fill in
  one_sheet.py build [--data speaking/one-sheet/one-sheet.json] [--out speaking/one-sheet/one-sheet.html]
                     [--business-file BUILDROOM_BUSINESS_FILE.md] [--folder speaking]

`build` checks the content first and writes the page only when nothing is wrong. The page is one
self-contained HTML file, sized for US Letter, that the member opens in a browser and prints to PDF.
It uses the member's locked look (Design/System/tokens.css) when there is one.

The content rules are the pitch check's: the member's own facts or nothing. On top of them:
  - one to three talks, each with a title, a promise and three takeaways (from the talks on file)
  - a bio of 120 words or fewer, in the third person
  - every testimonial names its proof bank ID (P-01), and that entry must be consented (named or
    anonymous) with `events` or `site` in its scope; a pending, declined, withdrawn or unanswered
    story is refused
  - a way to book: an email address or a booking link
  - a photo is optional; without one the page shows the name alone, never a stock or generated face
Exit 0 when the page is written, 1 when the content needs fixing, 2 on a usage error.
"""
import argparse, html, json, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import speaklib as sl  # noqa: E402

TEMPLATE = {
    "name": "", "tagline": "", "bio": "", "photo": "",
    "audiences": [], "formats": [], "credentials": [],
    "talks": [1],
    "testimonials": [{"proof_id": "", "quote": "", "attribution": ""}],
    "contact": {"email": "", "phone": "", "website": "", "booking_link": ""},
    "based_in": "", "travels": "",
}
BAD_PERMISSION = ("pending", "declined", "withdrawn", "no answer")


def proof_rows(folder):
    """ID -> the proof bank's index row, as lower-case cells."""
    bank = folder.resolve().parent / "proof" / "proof-bank.md"
    rows = {}
    if bank.is_file():
        for line in sl.read_text(bank).splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and re.fullmatch(r"P-\d+", cells[0]):
                rows[cells[0].upper()] = [c.lower() for c in cells]
    return rows, bank


def validate(d, a, data, bf):
    fix, watch = [], []
    name = str(d.get("name", "")).strip()
    if not name:
        fix.append("no name")
    if sl.words(str(d.get("tagline", ""))) > 14:
        fix.append("the tagline is over fourteen words")
    bio = str(d.get("bio", "")).strip()
    if not bio:
        fix.append("no bio")
    elif sl.words(bio) > 120:
        fix.append(f"the bio is {sl.words(bio)} words; 120 at most")
    elif re.search(r"\b(?:I|my|me)\b", bio):
        watch.append("the bio is in the first person; hosts paste it into a programme, so write it in the third person")
    picks = d.get("talks") or []
    talks = []
    if not 1 <= len(picks) <= 3:
        fix.append("one to three talks (by their number in `speak_pipeline.py talk list`)")
    for n in picks:
        t = next((t for t in data["talks"] if t.get("n") == n), None) if isinstance(n, int) else None
        if t is None:
            fix.append(f"talk {n} is not on file (speak_pipeline.py talk add)")
        else:
            talks.append(t)
    rows, bank = proof_rows(sl.folder(a))
    proof = re.sub(r"\s+", " ", sl.plain(sl.proof_text(sl.folder(a))).lower())
    tests = [t for t in (d.get("testimonials") or []) if isinstance(t, dict) and (t.get("quote") or t.get("proof_id"))]
    for t in tests:
        pid = str(t.get("proof_id", "")).strip().upper()
        if not re.fullmatch(r"P-\d+", pid):
            fix.append("a testimonial has no proof bank ID (P-01): only stories the Proof Engine recorded, with permission, go on the page")
            continue
        row = rows.get(pid)
        if row is None:
            fix.append(f"{pid} is not in {bank.name} beside the Business File")
            continue
        perm = row[3] if len(row) > 3 else ""
        scope = row[4] if len(row) > 4 else ""
        if any(b in perm for b in BAD_PERMISSION) or not any(g in perm for g in ("named", "anonymous")):
            fix.append(f"{pid}: permission is '{perm or 'not recorded'}'; it cannot be used")
        elif not any(re.search(r"\b(?:events?|site|website)\b", part) and not re.match(r"\s*(?:no|not|never|except)\b", part)
                     for part in re.split(r"[,;/]", scope)):
            fix.append(f"{pid}: its permission covers '{scope}', not a speaker sheet (needs events or site)")
        if "anonymous" in perm and str(t.get("attribution", "")).strip() and not re.match(r"(?i)an? ", str(t["attribution"]).strip()):
            fix.append(f"{pid} is anonymous: attribute it as \"a [kind of client]\", never by name")
        quote = re.sub(r"\s+", " ", sl.plain(str(t.get("quote", ""))).lower()).strip(" .,!?\"'")
        if not quote:
            fix.append(f"{pid}: the quote is empty; copy the words from the proof bank, exactly")
        elif quote not in proof:
            fix.append(f"{pid}: the quote is not in the proof bank word for word (proof/proof-bank.md or proof/stories/). "
                       "Copy it exactly, or leave it out")
    c = d.get("contact") or {}
    if not (str(c.get("email", "")).strip() or str(c.get("booking_link", "")).strip()):
        fix.append("no way to book: give an email address or a booking link")
    photo = str(d.get("photo", "")).strip()
    photo_path = None
    if photo:
        for cand in (Path(photo), Path(a.data).parent / photo, sl.folder(a) / photo):
            if cand.is_file():
                photo_path = cand
                break
        if photo_path is None:
            fix.append(f"the photo was not found: {photo}")
    else:
        watch.append("no photo: the page shows the name alone. Hosts like a real, recent photo of the member; never a generated one")
    # the member's own facts or nothing
    known = sl.known_text(a, bf)
    nums = sl.number_sets(known)
    body = "\n".join([str(d.get("tagline", "")), bio, " . ".join(map(str, d.get("credentials") or [])),
                      " . ".join(map(str, d.get("audiences") or [])), " . ".join(map(str, d.get("formats") or [])),
                      str(d.get("based_in", "")), str(d.get("travels", "")),
                      " . ".join(str(t.get("attribution", "")) for t in tests)])
    body = re.sub(r"\b(\d+)[- ]minutes?\b", " ", body)
    un = sl.unsourced_numbers(body, nums)
    if un:
        fix.append("figures the member did not give: " + ", ".join(un[:6]))
    cl = sl.unsupported_claims(body, known)
    if cl:
        fix.append("claims the member's own material does not contain: " + ", ".join(cl[:6]))
    everything = body + " " + " ".join(str(t.get("quote", "")) for t in tests) + " " + \
        " ".join(" ".join([str(t.get("title", "")), str(t.get("promise", "")), str(t.get("for", ""))] + list(map(str, t.get("takeaways", []))))
                 for t in talks)
    if any(x in everything for x in sl.DASHES):
        fix.append("an em or en dash")
    if sl.PLACEHOLDER.search(everything):
        fix.append("placeholder text")
    low = re.sub(r"\s+", " ", sl.plain(everything).lower())
    for kind, line in sl.banned_lines(bf):
        if re.sub(r"\s+", " ", line.lower()) in low:
            fix.append(f"{kind} in the Business File: \"{line[:60]}\"")
    if not bf:
        watch.append("no Business File was found, so retired lines and never-say claims were not checked")
    return fix, watch, talks, tests, photo_path


def esc(s):
    return html.escape(str(s or ""), quote=True)


def page(d, talks, tests, photo_path, tokens_css):
    c = d.get("contact") or {}
    chips = lambda xs: "".join(f"<li>{esc(x)}</li>" for x in xs if str(x).strip())  # noqa: E731
    talk_html = "".join(
        f"<section class='talk'><h3>{esc(t['title'])}</h3><p class='promise'>{esc(t['promise'])}</p>"
        f"<ul>{''.join(f'<li>{esc(x)}</li>' for x in t['takeaways'])}</ul>"
        f"<p class='meta'>For {esc(t['for'])} · {esc(' or '.join(str(m) for m in t.get('lengths', [])))} minutes</p></section>"
        for t in talks)
    test_html = "".join(f"<blockquote><p>{esc(t['quote'])}</p><footer>{esc(t.get('attribution') or '')}</footer></blockquote>" for t in tests)
    contact = " · ".join(esc(x) for x in (c.get("email"), c.get("phone"), c.get("website"), c.get("booking_link")) if str(x or "").strip())
    photo = (f"<img class='photo' src='{esc(photo_path.resolve().as_uri())}' alt='{esc(d['name'])}'>" if photo_path else "")
    where = " · ".join(esc(x) for x in (d.get("based_in"), d.get("travels")) if str(x or "").strip())
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{esc(d['name'])}: speaker one-sheet</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
{tokens_css}
@page {{ size: Letter; margin: 0.55in; }}
* {{ box-sizing: border-box; }}
html {{ font-size: 18px; }}
body {{ margin: 0 auto; max-width: 7.4in; padding: 0.4in 0; color: var(--c-ink, #1a1f2e); background: var(--c-bg, #ffffff);
  font-family: var(--f-body, Georgia, 'Times New Roman', serif); line-height: 1.45; }}
header {{ display: flex; gap: 0.3in; align-items: center; border-bottom: 3px solid var(--c-accent, #1d4ed8); padding-bottom: 0.2in; }}
.photo {{ width: 1.5in; height: 1.5in; object-fit: cover; border-radius: 8px; }}
h1 {{ font-family: var(--f-head, Georgia, serif); font-size: 2rem; line-height: 1.1; margin: 0 0 6px; }}
.tag {{ font-size: 1.1rem; margin: 0; }}
h2 {{ font-family: var(--f-head, Georgia, serif); font-size: 1rem; text-transform: uppercase; letter-spacing: .06em;
  color: var(--c-accent, #1d4ed8); margin: 0.28in 0 0.08in; }}
h3 {{ font-family: var(--f-head, Georgia, serif); font-size: 1.15rem; margin: 0 0 4px; }}
p {{ margin: 0 0 0.1in; }}
ul {{ margin: 0 0 0.1in; padding-left: 1.1em; }}
.talk {{ break-inside: avoid; margin-bottom: 0.18in; }}
.promise {{ font-style: italic; }}
.meta, .where {{ font-size: 1rem; }}
.chips {{ list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 6px 14px; }}
blockquote {{ margin: 0 0 0.14in; padding-left: 0.16in; border-left: 3px solid var(--c-accent, #1d4ed8); break-inside: avoid; }}
blockquote footer {{ font-size: 1rem; }}
.book {{ margin-top: 0.25in; padding: 0.16in; border: 2px solid var(--c-accent, #1d4ed8); border-radius: 8px; font-size: 1.05rem; break-inside: avoid; }}
@media print {{ body {{ padding: 0; }} }}
</style></head><body>
<header>{photo}<div><h1>{esc(d['name'])}</h1><p class="tag">{esc(d.get('tagline'))}</p><p class="where">{where}</p></div></header>
<h2>{'Talks' if len(talks) > 1 else 'The talk'}</h2>
{talk_html}
<h2>About {esc(d['name'].split()[0] if d['name'].split() else '')}</h2>
<p>{esc(d.get('bio'))}</p>
{('<ul class="chips">' + chips(d.get('credentials') or []) + '</ul>') if d.get('credentials') else ''}
{('<h2>Speaks to</h2><ul class="chips">' + chips(d.get('audiences') or []) + '</ul>') if d.get('audiences') else ''}
{('<h2>Formats</h2><ul class="chips">' + chips(d.get('formats') or []) + '</ul>') if d.get('formats') else ''}
{('<h2>What hosts and clients say</h2>' + test_html) if tests else ''}
<div class="book"><strong>To book {esc(d['name'])}:</strong> {contact}</div>
</body></html>
"""


def cmd_template(a):
    out = sl.folder(a) / "one-sheet" / "one-sheet.json"
    if out.exists():
        sl.refuse(f"{out} is already there; edit it, or move it away first")
    sl.write_json(out, TEMPLATE)
    return {"ok": True, "template": str(out), "next": "fill it from the member's own answers, then one_sheet.py build"}, 0


def cmd_build(a):
    a.data = a.data or str(sl.folder(a) / "one-sheet" / "one-sheet.json")
    if not Path(a.data).is_file():
        return {"ok": False, "error": f"file not found: {a.data} (one_sheet.py template writes a blank one)"}, 2
    d = sl.read_json(a.data, TEMPLATE)
    data = sl.read_json(sl.folder(a) / "pipeline.json", {"profile": {}, "talks": [], "stages": []})
    bf = sl.find_business_file(a)
    fix, watch, talks, tests, photo_path = validate(d, a, data, bf)
    if fix:
        return {"ok": False, "verdict": "FIX", "fix": fix, "watch": watch, "written": False}, 1
    css = ""
    for cand in (Path("Design/System/tokens.css"), sl.folder(a).resolve().parent / "Design" / "System" / "tokens.css"):
        if cand.is_file():
            css = sl.read_text(cand)
            break
    out = Path(a.out) if a.out else Path(a.data).with_suffix(".html")
    sl.write_atomic(out, page(d, talks, tests, photo_path, css))
    return {"ok": True, "verdict": "CLEAN", "written": True, "page": str(out), "watch": watch,
            "uses_design_system": bool(css), "talks": [t["title"] for t in talks],
            "next": "open it in a browser, print to PDF (Letter, no headers or footers), and read it once on a phone"}, 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("template"); t.add_argument("--folder"); t.add_argument("--today")
    b = sub.add_parser("build"); b.add_argument("--data"); b.add_argument("--out"); b.add_argument("--business-file"); b.add_argument("--folder")
    b.add_argument("--today")
    a = ap.parse_args()
    try:
        out, code = (cmd_template if a.cmd == "template" else cmd_build)(a)
    except (KeyError, AttributeError, TypeError, IndexError) as e:
        out, code = {"ok": False, "error": f"a file here is missing something the engine wrote ({type(e).__name__}: {e}); "
                                            "it was probably edited by hand. Restore it from a backup"}, 2
    sl.emit(out, code)


if __name__ == "__main__":
    main()
