#!/usr/bin/env python3
"""AI Momentum Labs Book Builder: the manuscript itself.

Sections are plain-prose files in <book>/manuscript/, each starting with a marker line
"=== SECTION: Chapter 3: Title ===" (Title Page, Introduction, Conclusion and About the Author use
their own names). A subhead is a line on its own starting "@@ ". Lengths are measured, never assumed.

Usage
  manuscript.py status   --book B                       every planned section: present, words measured, against its target
  manuscript.py context  --book B --chapter N           what to load before drafting chapter N: its brief, the book record
                                                        so far, earlier chapter summaries, and the end of the previous section
  manuscript.py assemble --book B [--out manuscript.md] one file, in book order
  manuscript.py edition  --book B --label v1 [--note "after the line edit"]
                                                        freezes an edition nobody edits: the text, a copy with paragraph
                                                        IDs (C03-P012) for reviewers, a map and a checksum
  manuscript.py diff     --book B --from v1 --to v2     which paragraphs changed, by section
  manuscript.py export   --book B [--edition v2] --docx out.docx
Every command prints JSON. Exit 1 on a refusal.
"""
import argparse, difflib, hashlib, html, sys, zipfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import booklib as bl  # noqa: E402

THIN = 0.6     # a section under 60% of its target is reported as thin


def planned(data, book):
    plan = bl.read_json(Path(book) / "plan.json", {"chapters": []})
    titles = ["Title Page", "Introduction"]
    for i in range(1, int(data["settings"]["chapters"]) + 1):
        chs = plan.get("chapters") or []
        t = chs[i - 1].get("title", "") if i <= len(chs) else ""
        titles.append(f"Chapter {i}" + (f": {t}" if t else ""))
    return titles + ["Conclusion", "About the Author"]


def status(data, book):
    secs = {bl.section_key(s["title"]): s for s in bl.read_manuscript(book)}
    t = bl.targets(data)
    rows, total = [], 0
    for title in planned(data, book):
        key = bl.section_key(title)
        s = secs.get(key)
        n = bl.section_words(s) if s else 0
        total += n
        tgt = t.get(key)
        state = "missing" if not s else "empty" if n == 0 else "thin" if tgt and n < tgt * THIN else "written"
        rows.append({"section": title, "state": state, "words": n, "target": tgt, "file": s["file"] if s else ""})
    extra = [s["title"] for k, s in secs.items() if k not in {bl.section_key(x) for x in planned(data, book)}]
    return {"sections": rows, "total_words": total, "target_words": int(data["settings"]["words"]),
            "missing": [r["section"] for r in rows if r["state"] in ("missing", "empty")],
            "thin": [r["section"] for r in rows if r["state"] == "thin"], "unplanned": extra,
            "complete": not any(r["state"] in ("missing", "empty") for r in rows if r["section"] != "Title Page")}


def cmd_status(a):
    data = bl.load_book(a.book)
    st = status(data, a.book)
    if st["complete"] and bl.stage(data, "draft").get("status") != "done":
        bl.set_stage(data, "draft", "done", words=st["total_words"])
        bl.save_book(a.book, data)
    return {"ok": True, **st}


def cmd_context(a):
    data = bl.load_book(a.book)
    plan = bl.read_json(Path(a.book) / "plan.json")
    chs = plan.get("chapters") or []
    if not 1 <= a.chapter <= len(chs):
        bl.refuse(f"the plan has {len(chs)} chapters")
    if bl.stage(data, "outline").get("status") != "approved":
        bl.refuse("the member has not approved the outline yet (book_plan.py approve --what outline --by member)")
    rec = bl.read_json(Path(a.book) / "record.json", {"entries": []})["entries"]
    earlier = [e for e in rec if e.get("chapter") is None or e["chapter"] < a.chapter]
    secs = bl.read_manuscript(a.book)
    prev = [s for s in secs if bl.order_key(s["title"]) < (2, a.chapter)]
    tail = "\n\n".join(prev[-1]["paras"][-3:]) if prev else "(nothing yet: this is the start of the book)"
    missing = [n for n in range(1, a.chapter) if not any(e["kind"] == "summary" and e.get("chapter") == n for e in rec)
               and any(bl.section_key(s["title"]) == f"Chapter {n}" for s in secs)]
    return {"ok": True, "chapter": a.chapter, "title": chs[a.chapter - 1].get("title"),
            "target_words": bl.targets(data)[f"Chapter {a.chapter}"],
            "book": {k: plan.get(k) for k in ("title", "promise", "voice", "thread")},
            "brief": chs[a.chapter - 1],
            "next_chapter": chs[a.chapter].get("title") if a.chapter < len(chs) else "Conclusion",
            "record": {k: [e["text"] for e in earlier if e["kind"] == k] for k in ("term", "framework", "name", "promise")},
            "stories_already_told": [f"ch {e.get('chapter')}: {e['text']}" for e in earlier if e["kind"] == "story"],
            "earlier_chapter_summaries": [f"ch {e['chapter']}: {e['text']}" for e in sorted(
                (e for e in earlier if e["kind"] == "summary"), key=lambda e: e["chapter"])],
            "end_of_previous_section": tail,
            "warnings": [f"chapter {n} is written but has no summary in the book record" for n in missing]}


def assemble(secs):
    return "\n\n".join(f"=== SECTION: {s['title']} ===\n\n" + "\n\n".join(s["paras"]) for s in secs) + "\n"


def cmd_assemble(a):
    bl.load_book(a.book)
    secs = bl.read_manuscript(a.book)
    if not secs:
        bl.refuse("no sections in manuscript/ yet")
    out = Path(a.out) if a.out else Path(a.book) / "manuscript.md"
    bl.write_atomic(out, assemble(secs))
    return {"ok": True, "out": str(out), "sections": len(secs), "words": sum(bl.section_words(s) for s in secs)}


def cmd_edition(a):
    data = bl.load_book(a.book)
    label = bl.slugify(a.label)
    d = Path(a.book) / "editions" / label
    if d.exists():
        bl.refuse(f"edition {label} already exists; an edition is never overwritten. Use the next label.")
    secs = bl.read_manuscript(a.book)
    if not secs:
        bl.refuse("no sections in manuscript/ yet")
    text = assemble(secs)
    ids, mp = [], []
    for s in secs:
        code = bl.section_code(s["title"])
        ids.append(f"=== SECTION: {s['title']} ===")
        for i, para in enumerate(s["paras"], 1):
            pid = f"{code}-P{i:03d}"
            ids.append(f"[{pid}] {para}")
            mp.append({"id": pid, "section": s["title"], "hash": hashlib.sha256(para.encode()).hexdigest()[:16]})
    sha = hashlib.sha256(text.encode()).hexdigest()
    bl.write_atomic(d / "manuscript.md", text)
    bl.write_atomic(d / "manuscript.ids.md", "\n\n".join(ids) + "\n")
    bl.write_json(d / "map.json", {"label": label, "sha256": sha, "date": bl.today(), "note": a.note or "",
                                   "sections": [{"title": s["title"], "code": bl.section_code(s["title"]),
                                                 "paragraphs": len(s["paras"]), "words": bl.section_words(s)} for s in secs],
                                   "paragraphs": mp})
    data.setdefault("editions", []).append({"label": label, "sha256": sha, "date": bl.today(), "note": a.note or "",
                                            "words": sum(bl.section_words(s) for s in secs)})
    bl.save_book(a.book, data)
    return {"ok": True, "edition": label, "sha256": sha[:16], "folder": str(d), "paragraphs": len(mp),
            "for_reviewers": str(d / "manuscript.ids.md")}


def load_edition(book, label):
    d = Path(book) / "editions" / bl.slugify(label)
    if not (d / "manuscript.md").exists():
        bl.refuse(f"no edition {label}")
    return bl.parse_sections(bl.read_text(d / "manuscript.md"))


def cmd_diff(a):
    bl.load_book(a.book)
    old = {bl.section_key(t): (t, p) for t, p in load_edition(a.book, getattr(a, "from"))}
    new = {bl.section_key(t): (t, p) for t, p in load_edition(a.book, a.to)}
    out = []
    for key in sorted(set(old) | set(new), key=lambda k: bl.order_key(k)):
        if key not in new:
            out.append({"section": key, "change": "removed"})
            continue
        if key not in old:
            out.append({"section": key, "change": "added", "paragraphs": len(new[key][1])})
            continue
        sm = difflib.SequenceMatcher(a=old[key][1], b=new[key][1], autojunk=False)
        chg = [{"op": op, "old": [i1 + 1, i2], "new": [j1 + 1, j2]} for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
        if chg or old[key][0] != new[key][0]:
            out.append({"section": new[key][0], "change": "edited", "paragraph_changes": chg,
                        "words": [sum(bl.words(p) for p in old[key][1]), sum(bl.words(p) for p in new[key][1])],
                        "retitled": old[key][0] != new[key][0]})
    return {"ok": True, "from": getattr(a, "from"), "to": a.to, "changed_sections": len(out), "changes": out}


def docx(secs, out, title):
    def para(text, style=None):
        st = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
        return f'<w:p>{st}<w:r><w:t xml:space="preserve">{html.escape(text, quote=False)}</w:t></w:r></w:p>'
    body = []
    for s in secs:
        body.append(para(s["title"], "Heading1"))
        for p in s["paras"]:
            body.append(para(p[3:].strip(), "Heading2") if bl.is_subhead(p) else para(p.replace("\n", " ")))
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/'
           'wordprocessingml/2006/main"><w:body>' + "".join(body) + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar '
           'w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>')
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/'
              'wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/>'
              '<w:sz w:val="24"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="200" w:line="360" '
              'w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" '
              'w:styleId="Normal"><w:name w:val="Normal"/></w:style><w:style w:type="paragraph" w:styleId="Heading1">'
              '<w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:pageBreakBefore/><w:spacing w:after="360"/>'
              '</w:pPr><w:rPr><w:b/><w:sz w:val="40"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading2">'
              '<w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="360"/></w:pPr>'
              '<w:rPr><w:b/><w:sz w:val="28"/></w:rPr></w:style></w:styles>')
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/'
          '2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships'
          '+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" '
          'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override '
          'PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles'
          '+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-'
          'properties+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/'
            'package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
            'relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.'
            'openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>')
    drels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/'
             'package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
             'relationships/styles" Target="styles.xml"/></Relationships>')
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.'
            'org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>'
            + html.escape(title, quote=False) + '</dc:title></cp:coreProperties>')
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("word/document.xml", doc)
        z.writestr("word/styles.xml", styles); z.writestr("word/_rels/document.xml.rels", drels)
        z.writestr("docProps/core.xml", core)


def cmd_export(a):
    data = bl.load_book(a.book)
    if a.edition:
        secs = [{"title": t, "paras": p} for t, p in load_edition(a.book, a.edition)]
    else:
        secs = bl.read_manuscript(a.book)
    if not secs:
        bl.refuse("nothing to export")
    plan = bl.read_json(Path(a.book) / "plan.json", {})
    docx(secs, a.docx, plan.get("title") or data.get("working_title") or "Manuscript")
    return {"ok": True, "docx": a.docx, "sections": len(secs), "words": sum(bl.section_words(s) for s in secs),
            "edition": a.edition or "working copy"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def p(name):
        x = sub.add_parser(name)
        x.add_argument("--book", required=True)
        return x
    p("status")
    x = p("context"); x.add_argument("--chapter", type=int, required=True)
    x = p("assemble"); x.add_argument("--out")
    x = p("edition"); x.add_argument("--label", required=True); x.add_argument("--note")
    x = p("diff"); x.add_argument("--from", required=True); x.add_argument("--to", required=True)
    x = p("export"); x.add_argument("--edition"); x.add_argument("--docx", required=True)
    a = ap.parse_args()
    out = globals()["cmd_" + a.cmd](a)
    bl.emit(out, 0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
