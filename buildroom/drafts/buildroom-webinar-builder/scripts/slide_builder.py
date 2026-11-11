#!/usr/bin/env python3
"""Webinar Builder slides: build a deck an older room can read, and inspect any deck for type size, contrast
and words per slide.

Local only. Writes a standard .pptx (opens in PowerPoint, Keynote and Google Slides) with the speaker notes in
each slide's notes. No extra installs.

Usage
  slide_builder.py build --spec webinar.json --out slides.pptx [--theme light|dark] [--accent RRGGBB]
                         [--font "Arial"] [--body-pt 32] [--title-pt 44]
      One slide per entry in each segment's "slides" ({"title", "lines", "kind", "notes"}); a segment with no
      slides gets one title slide with its name. kinds: title, statement, list, quote, offer, chat, link.
      The lower right quarter of every slide is kept clear for the presenter's video. --accent colours titles
      only, and is refused (exit 2) unless it reaches 4.5:1 against the background. --body-pt below 28 or
      --title-pt below 40 is refused. Prints a JSON summary.
  slide_builder.py inspect DECK.pptx [--json]
      Per slide: the smallest type, the lowest text-to-background contrast (when both colours are set in the
      slide), the words, and the problems: type under 24pt (must), under 28pt body or 40pt title (should),
      contrast under 4.5:1 (must) or 7:1 (should), more than 25 words (should). Text whose size or colour is
      not set in the slide itself (inherited from a theme or layout) is listed as "not set: check by eye".
      Exit 0 when no must-level problem, 1 when there is one, 2 when the file cannot be read.

Standard library only.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import argparse, json, re, zipfile  # noqa: E402
from pathlib import Path  # noqa: E402
from xml.sax.saxutils import escape  # noqa: E402

EMU = 914400  # per inch
SW, SH = 12192000, 6858000  # 13.333 x 7.5 in, 16:9
THEMES = {"light": {"bg": "FFFFFF", "fg": "1A1A1A", "sub": "333333"},
          "dark": {"bg": "141414", "fg": "FFFFFF", "sub": "E6E6E6"}}
MIN_PT, BODY_PT, TITLE_PT = 24, 28, 40
MIN_CONTRAST, TARGET_CONTRAST, MAX_WORDS = 4.5, 7.0, 25


# ---------------------------------------------------------------- colour

def lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


# ---------------------------------------------------------------- package parts

NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
RT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_P = "application/vnd.openxmlformats-officedocument.presentationml"


def theme_xml(name, font):
    f = escape(font)
    clr = "".join(f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k, v in (
        ("dk1", "000000"), ("lt1", "FFFFFF"), ("dk2", "1F2937"), ("lt2", "F3F4F6"), ("accent1", "1D4ED8"),
        ("accent2", "B45309"), ("accent3", "047857"), ("accent4", "7C3AED"), ("accent5", "BE123C"),
        ("accent6", "0E7490"), ("hlink", "1D4ED8"), ("folHlink", "6D28D9")))
    fill = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    ln = '<a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="{name}"><a:themeElements>'
            f'<a:clrScheme name="{name}">{clr}</a:clrScheme>'
            f'<a:fontScheme name="{name}"><a:majorFont><a:latin typeface="{f}"/><a:ea typeface=""/><a:cs typeface=""/>'
            f'</a:majorFont><a:minorFont><a:latin typeface="{f}"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>'
            '</a:fontScheme>'
            f'<a:fmtScheme name="{name}"><a:fillStyleLst>{fill * 3}</a:fillStyleLst><a:lnStyleLst>{ln * 3}</a:lnStyleLst>'
            '<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle>'
            '<a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>'
            f'<a:bgFillStyleLst>{fill * 3}</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>')


def rels(items):
    body = "".join(f'<Relationship Id="{i}" Type="{t if t.startswith("http") else RT + "/" + t}" Target="{tg}"/>'
                   for i, t, tg in items)
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{body}</Relationships>')


def sp_tree(shapes):
    return ('<p:cSld>{bg}<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>'
            '</a:xfrm></p:grpSpPr>' + "".join(shapes) + '</p:spTree></p:cSld>')


def textbox(sid, name, x, y, w, h, paras, anchor="t"):
    """paras: list of (text, pt, hexcolour, bold, bullet)."""
    ps = []
    for text, pt, col, bold, bullet in paras:
        sp = '<a:spcAft><a:spcPts val="1400"/></a:spcAft>'
        bu = (f'<a:pPr marL="457200" indent="-457200">{sp}<a:buFont typeface="Arial"/><a:buChar char="&#8226;"/></a:pPr>'
              if bullet else f'<a:pPr>{sp}<a:buNone/></a:pPr>')
        rpr = (f'<a:rPr lang="en-US" sz="{int(pt * 100)}" b="{1 if bold else 0}" dirty="0">'
               f'<a:solidFill><a:srgbClr val="{col}"/></a:solidFill></a:rPr>')
        ps.append(f'<a:p>{bu}<a:r>{rpr}<a:t>{escape(text)}</a:t></a:r>'
                  f'<a:endParaRPr lang="en-US" sz="{int(pt * 100)}" dirty="0"/></a:p>')
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{escape(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="{anchor}"><a:normAutofit/>'
            '</a:bodyPr><a:lstStyle/>' + "".join(ps) + '</p:txBody></p:sp>')


def slide_xml(shapes, bg):
    bgx = f'<p:bg><p:bgPr><a:solidFill><a:srgbClr val="{bg}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<p:sld {NS}>' + sp_tree(shapes).replace("{bg}", bgx) +
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')


def notes_xml(n, text):
    paras = "".join(f'<a:p><a:r><a:rPr lang="en-US" dirty="0"/><a:t>{escape(t)}</a:t></a:r></a:p>'
                    for t in (text.splitlines() or [""])) or '<a:p><a:endParaRPr lang="en-US"/></a:p>'
    img = ('<p:sp><p:nvSpPr><p:cNvPr id="2" name="Slide Image"/><p:cNvSpPr><a:spLocks noGrp="1" noRot="1" '
           'noChangeAspect="1"/></p:cNvSpPr><p:nvPr><p:ph type="sldImg"/></p:nvPr></p:nvSpPr><p:spPr/></p:sp>')
    body = ('<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
            + paras + '</p:txBody></p:sp>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<p:notes {NS}>' + sp_tree([img, body]).replace("{bg}", "") +
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>')


CLRMAP = ('<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" '
          'accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>')


def master_xml():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<p:sldMaster {NS}>' + sp_tree([]).replace("{bg}", '<p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg>')
            + CLRMAP + '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
            '<p:txStyles><p:titleStyle><a:lvl1pPr><a:defRPr sz="4400"/></a:lvl1pPr></p:titleStyle>'
            '<p:bodyStyle><a:lvl1pPr><a:defRPr sz="3200"/></a:lvl1pPr></p:bodyStyle>'
            '<p:otherStyle><a:lvl1pPr><a:defRPr sz="1800"/></a:lvl1pPr></p:otherStyle></p:txStyles></p:sldMaster>')


def layout_xml():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<p:sldLayout {NS} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr>'
            '<p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>'
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')


def notes_master_xml():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<p:notesMaster {NS}>' + sp_tree([]).replace("{bg}", '<p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg>')
            + CLRMAP + '<p:notesStyle><a:lvl1pPr><a:defRPr sz="1400"/></a:lvl1pPr></p:notesStyle></p:notesMaster>')


def write_pptx(out, slides, font, title):
    """slides: list of (shapes_xml_list, bg_hex, notes_text)."""
    n = len(slides)
    ct = ['<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
          '<Default Extension="xml" ContentType="application/xml"/>',
          f'<Override PartName="/ppt/presentation.xml" ContentType="{CT_P}.presentation.main+xml"/>',
          f'<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="{CT_P}.slideMaster+xml"/>',
          f'<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="{CT_P}.slideLayout+xml"/>',
          f'<Override PartName="/ppt/notesMasters/notesMaster1.xml" ContentType="{CT_P}.notesMaster+xml"/>',
          '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
          '<Override PartName="/ppt/theme/theme2.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
          '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>']
    for i in range(1, n + 1):
        ct.append(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="{CT_P}.slide+xml"/>')
        ct.append(f'<Override PartName="/ppt/notesSlides/notesSlide{i}.xml" ContentType="{CT_P}.notesSlide+xml"/>')
    parts = {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.'
                               'openxmlformats.org/package/2006/content-types">' + "".join(ct) + '</Types>',
        "_rels/.rels": rels([("rId1", "officeDocument", "ppt/presentation.xml"),
                             ("rId2", "http://schemas.openxmlformats.org/package/2006/relationships/metadata/"
                                      "core-properties", "docProps/core.xml"),
                             ("rId3", "extended-properties", "docProps/app.xml")]),
        "docProps/core.xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties '
                              'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                              'xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>' + escape(title) +
                              '</dc:title></cp:coreProperties>'),
        "docProps/app.xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.'
                             'openxmlformats.org/officeDocument/2006/extended-properties"><Application>Build Room OS'
                             f'</Application><Slides>{n}</Slides></Properties>'),
        "ppt/presentation.xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                                 f'<p:presentation {NS} saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId '
                                 'id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId '
                                 'r:id="rId3"/></p:notesMasterIdLst><p:sldIdLst>' +
                                 "".join(f'<p:sldId id="{255 + i}" r:id="rId{10 + i}"/>' for i in range(1, n + 1)) +
                                 f'</p:sldIdLst><p:sldSz cx="{SW}" cy="{SH}"/><p:notesSz cx="6858000" cy="9144000"/>'
                                 '<p:defaultTextStyle><a:lvl1pPr><a:defRPr sz="1800"/></a:lvl1pPr></p:defaultTextStyle>'
                                 '</p:presentation>'),
        "ppt/_rels/presentation.xml.rels": rels([("rId1", "slideMaster", "slideMasters/slideMaster1.xml"),
                                                 ("rId2", "theme", "theme/theme1.xml"),
                                                 ("rId3", "notesMaster", "notesMasters/notesMaster1.xml")] +
                                                [(f"rId{10 + i}", "slide", f"slides/slide{i}.xml") for i in range(1, n + 1)]),
        "ppt/slideMasters/slideMaster1.xml": master_xml(),
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": rels([("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml"),
                                                              ("rId2", "theme", "../theme/theme1.xml")]),
        "ppt/slideLayouts/slideLayout1.xml": layout_xml(),
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": rels([("rId1", "slideMaster", "../slideMasters/slideMaster1.xml")]),
        "ppt/notesMasters/notesMaster1.xml": notes_master_xml(),
        "ppt/notesMasters/_rels/notesMaster1.xml.rels": rels([("rId1", "theme", "../theme/theme2.xml")]),
        "ppt/theme/theme1.xml": theme_xml("Build Room", font),
        "ppt/theme/theme2.xml": theme_xml("Build Room Notes", font),
    }
    for i, (shapes, bg, notes) in enumerate(slides, 1):
        parts[f"ppt/slides/slide{i}.xml"] = slide_xml(shapes, bg)
        parts[f"ppt/slides/_rels/slide{i}.xml.rels"] = rels([("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml"),
                                                            ("rId2", "notesSlide", f"../notesSlides/notesSlide{i}.xml")])
        parts[f"ppt/notesSlides/notesSlide{i}.xml"] = notes_xml(i, notes)
        parts[f"ppt/notesSlides/_rels/notesSlide{i}.xml.rels"] = rels([("rId1", "notesMaster", "../notesMasters/notesMaster1.xml"),
                                                                      ("rId2", "slide", f"../slides/slide{i}.xml")])
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", parts.pop("[Content_Types].xml"))
        for k, v in parts.items():
            z.writestr(k, v)


# ---------------------------------------------------------------- deck from webinar.json

def as_lines(x):
    return [str(v) for v in (x if isinstance(x, list) else [x] if x else [])]


def build_slide(sl, th, accent, body_pt, title_pt, sid0=2):
    """One slide's shapes. Text stays out of the lower right quarter (presenter video)."""
    kind = sl.get("kind") or ("list" if sl.get("lines") else "statement")
    fg, sub, tcol = th["fg"], th["sub"], accent or th["fg"]
    L, T = int(0.7 * EMU), int(0.6 * EMU)
    full_w = SW - 2 * L
    left_w = int(SW / 2 + 0.4 * EMU) - L  # body column ends left of the video quarter
    title, lines = str(sl.get("title", "")), as_lines(sl.get("lines"))
    shapes = []
    if kind == "title":
        shapes.append(textbox(sid0, "Title", L, int(1.6 * EMU), full_w, int(2.0 * EMU), [(title, title_pt + 8, tcol, True, False)], "b"))
        if lines:
            shapes.append(textbox(sid0 + 1, "Subtitle", L, int(3.8 * EMU), left_w, int(1.6 * EMU),
                                  [(x, body_pt, sub, False, False) for x in lines]))
    elif kind in ("statement", "quote", "chat"):
        head = {"chat": "In the chat:", "quote": ""}.get(kind, "")
        y = T
        if head or (kind != "statement" and title):
            shapes.append(textbox(sid0, "Title", L, y, full_w, int(1.2 * EMU), [(head or title, title_pt, tcol, True, False)]))
            y = int(2.0 * EMU)
            big = lines or ([title] if head else [])
        else:
            big = [title] + lines
        shapes.append(textbox(sid0 + 1, "Body", L, y, left_w, SH - y - int(0.6 * EMU),
                              [(("“" + x + "”") if kind == "quote" else x, body_pt + 8, fg, kind != "quote", False)
                               for x in big if x]))
    else:  # list, offer, link
        shapes.append(textbox(sid0, "Title", L, T, full_w, int(1.3 * EMU), [(title, title_pt, tcol, True, False)]))
        shapes.append(textbox(sid0 + 1, "Body", L, int(2.1 * EMU), left_w, SH - int(2.7 * EMU),
                              [(x, body_pt, fg, kind == "link", kind == "list") for x in lines]))
    return shapes


def cmd_build(a):
    try:
        spec = json.loads(Path(a.spec).read_text())
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"cannot read {a.spec}: {e}"}))
        sys.exit(2)
    if a.theme not in THEMES:
        print(json.dumps({"ok": False, "error": "--theme must be light or dark"}))
        sys.exit(2)
    if a.body_pt < BODY_PT or a.title_pt < TITLE_PT:
        print(json.dumps({"ok": False, "error": f"type below the floor: body at least {BODY_PT}pt, titles at least {TITLE_PT}pt"}))
        sys.exit(2)
    th = THEMES[a.theme]
    accent = None
    if a.accent:
        acc = a.accent.lstrip("#").upper()
        if not re.fullmatch(r"[0-9A-F]{6}", acc):
            print(json.dumps({"ok": False, "error": "--accent must be RRGGBB"}))
            sys.exit(2)
        c = contrast(acc, th["bg"])
        if c < MIN_CONTRAST:
            print(json.dumps({"ok": False, "error": f"accent {acc} is {c}:1 against the {a.theme} background; it needs "
                              f"{MIN_CONTRAST}:1. Use a darker shade (light theme) or a lighter one (dark theme)."}))
            sys.exit(2)
        accent = acc
    rec = bool(spec.get("recorded"))
    slides = []
    first = {"title": spec.get("title", ""), "kind": "title",
             "lines": [x for x in [spec.get("presenter", ""), "Recorded" if rec else ""] if x]}
    slides.append((build_slide(first, th, accent, a.body_pt, a.title_pt), th["bg"],
                   "Welcome. " + ("This is a recording of a session run live." if rec else "Recording notice and captions (CC).")))
    for s in spec.get("segments") or []:
        if s.get("kind") == "lobby":
            continue
        notes_default = "\n".join(as_lines(s.get("say")))
        if s.get("chat_prompt"):
            notes_default += ("\n" if notes_default else "") + "Ask: " + s["chat_prompt"]
        sls = s.get("slides") or [{"title": s.get("title", ""), "kind": "statement"}]
        for sl in sls:
            notes = sl.get("notes") or notes_default
            slides.append((build_slide(sl, th, accent, a.body_pt, a.title_pt), th["bg"], notes))
    write_pptx(a.out, slides, a.font, spec.get("title", "Webinar"))
    rep = inspect(a.out)
    print(json.dumps({"ok": True, "written": a.out, "slides": len(slides), "theme": a.theme,
                      "smallest_pt": rep["smallest_pt"], "lowest_contrast": rep["lowest_contrast"],
                      "must_problems": rep["must"], "should_problems": rep["should"]}))


# ---------------------------------------------------------------- inspect

def inspect(path):
    """Read a .pptx and report type sizes, contrast and words per slide."""
    with zipfile.ZipFile(path) as z:
        names = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                       key=lambda n: int(re.search(r"(\d+)", n.rsplit("/", 1)[1]).group(1)))
        order = names
        try:
            pres = z.read("ppt/presentation.xml").decode("utf8", "replace")
            prel = z.read("ppt/_rels/presentation.xml.rels").decode("utf8", "replace")
            rid = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', prel)) | \
                {k: v for v, k in re.findall(r'Target="([^"]+)"[^>]*Id="([^"]+)"', prel)}
            ids = re.findall(r'<p:sldId [^>]*r:id="([^"]+)"', pres)
            cand = ["ppt/" + rid[i].lstrip("/").replace("ppt/", "") for i in ids if i in rid]
            if cand and all(c in z.namelist() for c in cand):
                order = cand
        except KeyError:
            pass
        out, must, should = [], 0, 0
        all_pt, all_c = [], []
        for idx, n in enumerate(order, 1):
            x = z.read(n).decode("utf8", "replace")
            bgm = re.search(r"<p:bg>.*?<a:srgbClr val=\"([0-9A-Fa-f]{6})\"", x, re.S)
            bg = bgm.group(1).upper() if bgm else None
            texts, unset_size, unset_colour = [], 0, 0
            sizes, cons = [], []
            for sp in re.findall(r"<p:sp>.*?</p:sp>", x, re.S):
                is_title = bool(re.search(r'name="Title|type="(title|ctrTitle)"', sp))
                for rpr, body in re.findall(r"<a:r>(.*?)<a:t>(.*?)</a:t>", sp, re.S):
                    t = re.sub(r"<[^>]+>", "", body)
                    if not t.strip():
                        continue
                    texts.append(t)
                    m = re.search(r'sz="(\d+)"', rpr)
                    if m:
                        pt = int(m.group(1)) / 100
                        sizes.append((pt, is_title))
                    else:
                        unset_size += 1
                    cm = re.search(r'<a:solidFill><a:srgbClr val="([0-9A-Fa-f]{6})"', rpr)
                    if cm and bg:
                        cons.append(contrast(cm.group(1).upper(), bg))
                    else:
                        unset_colour += 1
            words = len(re.findall(r"\b\w[\w'’-]*\b", " ".join(texts)))
            probs = []
            if sizes:
                mn = min(p for p, _ in sizes)
                if mn < MIN_PT:
                    probs.append(("must", f"type at {mn:g}pt (under {MIN_PT}pt)"))
                body = [p for p, t in sizes if not t]
                ttl = [p for p, t in sizes if t]
                if body and min(body) < BODY_PT and min(body) >= MIN_PT:
                    probs.append(("should", f"body type at {min(body):g}pt (aim for {BODY_PT}pt or more)"))
                if ttl and min(ttl) < TITLE_PT:
                    probs.append(("should", f"title at {min(ttl):g}pt (aim for {TITLE_PT}pt or more)"))
            if cons:
                lc = min(cons)
                if lc < MIN_CONTRAST:
                    probs.append(("must", f"contrast {lc}:1 (under {MIN_CONTRAST}:1)"))
                elif lc < TARGET_CONTRAST:
                    probs.append(("should", f"contrast {lc}:1 (aim for {TARGET_CONTRAST}:1)"))
            if words > MAX_WORDS:
                probs.append(("should", f"{words} words (aim for {MAX_WORDS} or fewer: one idea a slide)"))
            if unset_size or unset_colour:
                probs.append(("note", f"not set in the slide: {unset_size} text run(s) without a size, "
                                      f"{unset_colour} without a colour or background; check by eye"))
            must += sum(1 for l, _ in probs if l == "must")
            should += sum(1 for l, _ in probs if l == "should")
            all_pt += [p for p, _ in sizes]
            all_c += cons
            out.append({"slide": idx, "smallest_pt": min((p for p, _ in sizes), default=None),
                        "lowest_contrast": min(cons, default=None), "words": words,
                        "problems": [{"level": l, "what": w} for l, w in probs]})
    return {"slides": out, "count": len(out), "smallest_pt": min(all_pt, default=None),
            "lowest_contrast": min(all_c, default=None), "must": must, "should": should}


def cmd_inspect(a):
    try:
        rep = inspect(a.deck)
    except (zipfile.BadZipFile, FileNotFoundError, KeyError) as e:
        print(json.dumps({"ok": False, "error": f"cannot read {a.deck}: {e}"}))
        sys.exit(2)
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        print(f"{rep['count']} slides · smallest type {rep['smallest_pt']}pt · lowest contrast {rep['lowest_contrast']}:1 "
              f"· {rep['must']} must · {rep['should']} should")
        for s in rep["slides"]:
            for p in s["problems"]:
                print(f"  slide {s['slide']}: {p['level'].upper()} {p['what']}")
    sys.exit(1 if rep["must"] else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Webinar Builder slides: build and inspect")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--spec", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--theme", default="light")
    b.add_argument("--accent")
    b.add_argument("--font", default="Arial")
    b.add_argument("--body-pt", type=int, default=32)
    b.add_argument("--title-pt", type=int, default=44)
    i = sub.add_parser("inspect")
    i.add_argument("deck")
    i.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    {"build": cmd_build, "inspect": cmd_inspect}[a.cmd](a)


if __name__ == "__main__":
    main()
