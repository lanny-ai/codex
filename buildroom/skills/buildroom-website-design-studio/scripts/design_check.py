#!/usr/bin/env python3
"""Website Design Studio: the go-live check for a page, and the generic-tells finder.

  design_check.py check --page Design/landing-page/page/index.html
                        [--tokens Design/System/tokens.json] [--audience 50plus|general]
                        [--images Design/landing-page/images.json] [--vault <obsidian vault>]
                        [--business-file BUILDROOM_BUSINESS_FILE.md] [--copy approved-copy.md]
                        [--render] [--out Design/landing-page/check.md]
  design_check.py tells --page index.html        the generic 2026 "AI made this" tells only

FIX items block the page (verdict FIX); WATCH items are advice. GO means no FIX item.
  FIX   body text under 16px (18px for a 50+ audience) · any text under 12px · text contrast
        under 4.5:1 (buttons and links included) · no mobile viewport · lorem ipsum or other
        placeholder text · an image with no alt text · an image from the taste vault · an image
        that is a reference, of unknown origin, or a generated person with no consent on file ·
        with --tokens: a colour or font that is not in the locked system, or core variables that
        drifted from it · with --render: sideways scroll on a 375px phone · with --business-file
        or --copy: a number on the page that is in neither
  WATCH the generic tells (each named) · more than 3 font weights · motion with no reduced-motion
        fallback · a heavy page (over 2 MB) · no single main action · not exactly one h1 ·
        missing lang or title · an image not listed in images.json · fixed widths a phone may not fit
Exit 0 on GO, 1 on FIX, 2 on a usage error. JSON on stdout; --out also writes check.md.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile, urllib.parse
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dslib  # noqa: E402


# ---------------------------------------------------------------- a small DOM
class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text")

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.children, self.parent, self.text = tag, dict(attrs), [], parent, []

    def elements(self):
        return [c for c in self.children if isinstance(c, Node)]

    def walk(self):
        yield self
        for c in self.elements():
            yield from c.walk()

    def all_text(self):
        out = []
        for c in self.children:
            out.append(c.all_text() if isinstance(c, Node) else c)
        return re.sub(r"\s+", " ", " ".join(out)).strip()

    def cls(self):
        return (self.attrs.get("class") or "").lower()


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.cur = self.root
        self.styles, self.links, self.in_style, self.in_script = [], [], False, False

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        self.cur.children.append(n)
        if tag == "style":
            self.in_style = True
        if tag == "script":
            self.in_script = True
        if tag == "link" and "stylesheet" in (n.attrs.get("rel") or ""):
            self.links.append(n.attrs.get("href") or "")
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.cur.tag == tag:
            self.cur = self.cur.parent

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        if tag == "script":
            self.in_script = False
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)
            return
        if self.in_script:
            return
        self.cur.children.append(data)


def parse(page_html):
    t = Tree()
    t.feed(page_html)
    t.close()
    return t


def page_css(tree, page_dir=None):
    css = "\n".join(tree.styles)
    if page_dir:
        seen = set()
        todo = [(Path(page_dir), h) for h in tree.links]
        for m in re.finditer(r"@import\s+(?:url\()?[\"']?([^\"')\s;]+)", css):
            todo.append((Path(page_dir), m.group(1)))
        while todo:
            base, href = todo.pop(0)
            p = local_path(base, href)
            if p and p.is_file() and p not in seen:
                seen.add(p)
                sub = dslib.read_text(p)
                css += "\n" + sub
                for m in re.finditer(r"@import\s+(?:url\()?[\"']?([^\"')\s;]+)", sub):
                    todo.append((p.parent, m.group(1)))
    inline = []
    for n in tree.root.walk():
        if n is not tree.root and n.attrs.get("style"):
            inline.append(f"[inline-{n.tag}]{{{n.attrs['style']}}}")
    return css + "\n" + "\n".join(inline)


def local_path(base, ref):
    """A local file a page refers to, or None for a web address. Handles %20, ?v=2 and #frag."""
    if not ref or re.match(r"^(https?:|//|data:|mailto:|tel:|#)", ref.strip(), re.I):
        return None
    clean = urllib.parse.unquote(re.split(r"[?#]", ref.strip(), 1)[0])
    return (Path(base) / clean) if clean else None


def to_hex(value, vars_):
    """An opaque colour as hex, or None (translucent, a gradient, an image, or unreadable)."""
    if not value:
        return None
    v = dslib.resolve(value, vars_).strip().lower()
    if re.search(r"gradient\(|url\(", v):
        return None
    h, _ = dslib.parse_colour(v)
    if h:
        return h
    first = re.match(r"(#[0-9a-f]{3,8}|(?:rgba?|hsla?)\([^)]*\)|[a-z]+)(?:\s|$)", v)
    if first:
        h, _ = dslib.parse_colour(first.group(1))
        return h
    return None


def colour_problem(value, vars_):
    if not value:
        return None
    v = dslib.resolve(value, vars_).strip().lower()
    _, why = dslib.parse_colour(v)
    return why


# ---------------------------------------------------------------- the generic tells
EMOJI_RE = re.compile("^[\U0001F300-\U0001FAFF☀-➿⭐✅✨]")
EYEBROW_CLASS = re.compile(r"eyebrow|kicker|overline|pretitle|pre-title|section-label|tagline|label")
LOGO_ROW = re.compile(r"\b(trusted by|as seen (in|on)|featured (in|on)|loved by (teams|people) at|used by teams at)\b", re.I)


def uppercase_classes(rules):
    out = set()
    for sel, props, _ in rules:
        if props.get("text-transform", "").startswith("uppercase") and "letter-spacing" in props:
            for m in re.finditer(r"\.([\w-]+)", sel):
                out.add(m.group(1).lower())
    return out


def tells(page_html, page_dir=None):
    tree = parse(page_html)
    rules = dslib.css_rules(page_css(tree, page_dir))
    vars_ = dslib.root_vars(page_css(tree, page_dir))
    html_attrs = next((n.attrs for n in tree.root.walk() if n.tag == "html"), {})
    found = []

    # 1. serif headline with an italic last word
    italic_rule = any(re.search(r"\bh1\b[^,{]*\b(em|i)\b", sel) and "italic" in props.get("font-style", "italic")
                      for sel, props, _ in rules)
    for h in (n for n in tree.root.walk() if n.tag == "h1"):
        kids = h.elements()
        text = h.all_text().rstrip(" .!?")
        if kids and kids[-1].tag in ("em", "i") and text.endswith(kids[-1].all_text().rstrip(" .!?")):
            found.append({"id": "italic_last_word", "name": "headline ending in an italic word",
                          "where": h.all_text()[:80]})
            break
    else:
        if html_attrs.get("data-head-italic") == "on" or (italic_rule and any(
                n.tag == "h1" and any(k.tag in ("em", "i") for k in n.elements()) for n in tree.root.walk())):
            found.append({"id": "italic_last_word", "name": "headline ending in an italic word", "where": "h1"})

    # 2. eyebrows over most section headings
    upper = uppercase_classes(rules)
    h2s = [n for n in tree.root.walk() if n.tag == "h2"]
    brows = 0
    for h in h2s:
        sib = h.parent.elements() if h.parent else []
        i = sib.index(h)
        cands = []
        if i > 0:
            cands.append(sib[i - 1])
        if h.parent and h.parent.parent and h.parent.elements() and h.parent.elements()[0] is h:
            ps = h.parent.parent.elements()
            j = ps.index(h.parent)
            if j > 0:
                cands.append(ps[j - 1])
        for c in cands:
            classes = set(c.cls().split())
            if c.tag in ("p", "span", "div", "small", "strong") and len(c.all_text()) <= 40 and (
                    EYEBROW_CLASS.search(c.cls()) or classes & upper):
                brows += 1
                break
    if html_attrs.get("data-eyebrows") == "on" or (len(h2s) >= 2 and brows >= max(2, len(h2s) / 2)):
        found.append({"id": "eyebrows", "name": "small uppercase labels over most section headings",
                      "where": f"{brows} of {len(h2s)} section headings"})

    # 3. the default cream background
    bg = to_hex(vars_.get("--c-bg"), vars_)
    if not bg:
        for sel, props, media in rules:
            if re.search(r"(^|[\s,])(body|html)([\s,]|$)", sel) and not media:
                bg = to_hex(props.get("background-color") or props.get("background"), vars_) or bg
    if bg and dslib.is_cream(bg):
        found.append({"id": "cream_background", "name": "the default cream background", "where": bg})

    # 4. pill buttons everywhere
    pill = html_attrs.get("data-buttons") == "pill"
    for sel, props, _ in rules:
        if re.search(r"button|\.btn|\.button|\.cta", sel) and "border-radius" in props and "data-buttons" not in sel:
            r = dslib.resolve(props["border-radius"], vars_).strip()
            v = dslib.px(r.split()[0]) if r else None
            if r.endswith("%") and dslib.px(r.split()[0]) and float(re.match(r"[\d.]+", r).group(0)) >= 50:
                pill = True
            elif v is not None and v >= 24:
                pill = True
    if pill:
        found.append({"id": "pill_buttons", "name": "fully rounded pill buttons", "where": "button styles"})

    # 5. three equal cards
    for n in tree.root.walk():
        kids = n.elements()
        if len(kids) == 3 and len({(k.tag, k.cls()) for k in kids}) == 1 and all(
                any(d.tag in ("h3", "h4") for d in k.walk()) and any(d.tag == "p" for d in k.walk()) for k in kids):
            found.append({"id": "three_cards", "name": "three equal feature cards in a row",
                          "where": (kids[0].cls() or kids[0].tag)})
            break

    # 6. gradient glow
    css = page_css(tree, page_dir)
    glow = False
    for m in re.finditer(r"(linear|radial|conic)-gradient\(([^;{}]*)\)", css):
        for hx in dslib.HEX_RE.findall(dslib.resolve(m.group(2), vars_)):
            if dslib.is_purple(hx):
                glow = True
    if re.search(r"filter\s*:\s*blur\(\s*([4-9]\d|\d{3,})px", css):
        glow = True
    if glow:
        found.append({"id": "gradient_glow", "name": "purple gradient or blurred glow blobs", "where": "background"})

    # 7. emoji bullets
    em = [n for n in tree.root.walk() if n.tag in ("li", "h3", "h4") and EMOJI_RE.match(n.all_text())]
    if len(em) >= 3:
        found.append({"id": "emoji_bullets", "name": "emoji as bullets or card icons", "where": f"{len(em)} items"})

    # 8. a 'trusted by' row with no logos
    for n in tree.root.walk():
        if n.tag in ("p", "h2", "h3", "span", "div", "small") and LOGO_ROW.search(" ".join(
                c for c in n.children if isinstance(c, str))):
            box = n.parent or n
            logos = [d for d in box.walk() if d.tag in ("img", "svg", "picture")]
            named = [d for d in logos if re.search(r"logo", " ".join(str(d.attrs.get(k, "")) for k in ("src", "alt", "class")), re.I)]
            if len(logos) < 3 and not named:
                found.append({"id": "empty_logo_row", "name": "a 'trusted by' line with no real logos",
                              "where": n.all_text()[:60]})
                break
    return found


# ---------------------------------------------------------------- the check
PLACEHOLDER = re.compile(r"lorem ipsum|dolor sit amet|\[write:|\bTODO\b|your (headline|tagline|company|name) here|"
                         r"headline goes here|example\.com|\bacme\b|john doe|jane doe|\bXX%|\$X\b|"
                         r"placeholder text", re.I)
NUMBER_RE = re.compile(r"(?:[$£€]\s?\d[\d,]*(?:\.\d+)?(?:\s?[kKmM]\b)?|\b\d[\d,]*(?:\.\d+)?\s?%|"
                       r"\b\d(?:\.\d)?\s?(?:/|out of)\s?5\b|"
                       r"\b\d[\d,]*\+?\s(?:[a-z-]+\s)?(?:clients|students|members|people|years|customers|businesses|"
                       r"coaches|reviews|families|women|men|days|weeks|months|spots|seats|subscribers|followers|readers|"
                       r"sales|downloads|ratings|stars|graduates|leaders|companies|countries|cities|lives|hours))", re.I)


def num_core(s):
    return re.sub(r"[^\d.]", "", s).rstrip(".")


def run_render(page, vw=375):
    node = shutil.which("node")
    if not node:
        return None, "node is not installed here"
    script = r"""
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport: {width: %d, height: 800}});
  await p.goto(process.argv[2], {waitUntil: 'load', timeout: 30000});
  const r = await p.evaluate(() => {
    const d = document.documentElement;
    const fs = parseFloat(getComputedStyle(document.body).fontSize);
    let min = 99; for (const el of document.querySelectorAll('body *')) {
      if (!el.childNodes.length || ![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
      const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      min = Math.min(min, parseFloat(cs.fontSize)); }
    let edge = 99, wrapped = [];
    for (const el of document.querySelectorAll('h1,h2,h3,p,li,blockquote')) {
      const r = el.getBoundingClientRect(); if (!r.width) continue;
      edge = Math.min(edge, r.left, d.clientWidth - r.right); }
    for (const el of document.querySelectorAll('a.btn,a.button,a.cta,button,.btn')) {
      const cs = getComputedStyle(el), lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.3;
      const r = el.getBoundingClientRect(); const pad = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
      if (r.height - pad > lh * 1.6 && el.textContent.trim()) wrapped.push(el.textContent.trim().slice(0, 40)); }
    return {scrollWidth: d.scrollWidth, clientWidth: d.clientWidth, bodyPx: fs, minPx: min, edge: edge, wrapped: wrapped};
  });
  console.log(JSON.stringify(r)); await b.close();
})().catch(e => { console.log(JSON.stringify({error: String(e).slice(0, 300)})); process.exit(0); });
""" % vw
    with tempfile.TemporaryDirectory() as td:
        sp = Path(td) / "measure.cjs"
        sp.write_text(script)
        env = dict(os.environ)
        paths = [x for x in env.get("NODE_PATH", "").split(os.pathsep) if x]
        npm = shutil.which("npm")
        if npm:
            try:
                g = subprocess.run([npm, "root", "-g"], capture_output=True, text=True, timeout=20).stdout.strip()
                if g:
                    paths.append(g)
            except Exception:
                pass
        env["NODE_PATH"] = os.pathsep.join(paths)
        try:
            p = subprocess.run([node, str(sp), Path(page).resolve().as_uri()], capture_output=True, text=True, timeout=90,
                               env=env)
        except subprocess.TimeoutExpired:
            return None, "the browser timed out"
    try:
        r = json.loads((p.stdout or "").strip().splitlines()[-1])
    except Exception:
        return None, (p.stderr or "could not run the browser")[:200]
    if "error" in r:
        return None, "Playwright is not available here" if "Cannot find module" in r["error"] else r["error"]
    return r, None


def check(a):
    page = Path(a.page)
    if not page.is_file():
        return {"ok": False, "error": f"page not found: {page}"}, 2
    src = page.read_text(encoding="utf-8", errors="replace")
    tree = parse(src)
    css = page_css(tree, page.parent)
    rules = dslib.css_rules(css)
    vars_ = dslib.root_vars(css)
    tokens = dslib.read_json(a.tokens) if a.tokens else None
    audience = a.audience or (tokens or {}).get("audience")
    if not audience:
        for dj in (page.parent / "design.json", page.parent.parent / "design.json", page.parent.parent.parent / "design.json"):
            if dj.is_file():
                audience = dslib.read_json(dj).get("audience")
                break
    audience = audience or "50plus"
    for f in (a.business_file, a.copy, a.images, a.tokens):
        if f and not Path(f).is_file():
            return {"ok": False, "error": f"file not found: {f}"}, 2
    min_body = dslib.MIN_BODY_PX_50PLUS if audience == "50plus" else dslib.MIN_BODY_PX
    items = []

    def add(level, cid, msg, fix=""):
        items.append({"level": level, "id": cid, "message": msg, "fix": fix})

    # ---- size
    root_px = 16.0
    for sel, props, media in rules:
        if not media and re.fullmatch(r"\s*(html|:root)\s*", sel) and props.get("font-size"):
            root_px = dslib.px(dslib.resolve(props["font-size"], vars_), base=16, root=16) or 16.0
    body_px = dslib.px(dslib.resolve(vars_.get("--size-base"), vars_), root=root_px) if vars_.get("--size-base") else None
    for sel, props, media in rules:
        if re.search(r"(^|[\s,])(body|html)([\s,]|$)", sel) and not media:
            fs = props.get("font-size")
            if not fs and props.get("font"):
                m = re.search(r"(?:^|\s)((?:var\([^)]*\)|[\d.]+(?:px|rem|em|pt)))\s*(?:/|\s)", dslib.resolve(props["font"], vars_) + " ")
                fs = m.group(1) if m else None
            if fs and sel.strip() not in ("html", ":root"):
                v = dslib.px(dslib.resolve(fs, vars_), base=root_px, root=root_px)
                if v:
                    body_px = v
                elif not body_px:
                    body_px = None
    if body_px is None:
        add("WATCH", "body_size", "the body text size is not set; browsers default to 16px",
            f"set --size-base to {min_body}px")
    elif body_px < min_body:
        add("FIX", "body_size", f"body text is {body_px:g}px; this audience needs at least {min_body}px",
            f"set --size-base to {min_body}px or more")
    smallest = None
    for sel, props, media in rules:
        fs = props.get("font-size")
        if fs:
            v = dslib.px(dslib.resolve(fs, vars_), base=body_px or 16, root=root_px)
            if v and (smallest is None or v < smallest[0]):
                smallest = (v, sel)
    if smallest and smallest[0] < 12:
        add("FIX", "tiny_text", f"text at {smallest[0]:g}px ({smallest[1][:40]}) is too small to read",
            "nothing under 14px; captions and fine print included")
    elif smallest and smallest[0] < 14:
        add("WATCH", "small_text", f"text at {smallest[0]:g}px ({smallest[1][:40]})", "14px is the smallest worth using")

    # ---- contrast
    def pair_check(vs, label):
        c = {k: to_hex(vs.get(dslib.VAR_OF[k]), vs) for k in dslib.COLOR_KEYS}
        accent_as_text = any("var(--c-accent)" in props.get("color", "") for _, props, _ in rules)
        pairs = [("ink", "bg", dslib.AA_TEXT, "body text"), ("muted", "bg", dslib.AA_TEXT, "secondary text"),
                 ("ink", "surface", dslib.AA_TEXT, "text on panels"),
                 ("accent_ink", "accent", dslib.AA_TEXT, "button text"),
                 ("accent", "bg", dslib.AA_TEXT if accent_as_text else dslib.AA_LARGE,
                  "links and accent text" if accent_as_text else "buttons against the page")]
        for k in dslib.COLOR_KEYS:
            raw = vs.get(dslib.VAR_OF[k])
            if raw and not c.get(k):
                add("WATCH", f"colour_unread_{k}{label}", f"{dslib.VAR_OF[k]} ({raw[:30]}) is {colour_problem(raw, vs) or 'unreadable'}, "
                    "so its contrast was not checked", "use a solid colour (hex, rgb() or hsl()) for the token")
        for fg, bgk, need, what in pairs:
            if c.get(fg) and c.get(bgk):
                r = dslib.contrast(c[fg], c[bgk])
                if r < need:
                    add("FIX", f"contrast_{fg}_{bgk}{label}",
                        f"{what}{' (dark mode)' if label else ''}: {c[fg]} on {c[bgk]} is {r}:1; it needs {need}:1",
                        f"try {dslib.shade_to_contrast(c[fg], c[bgk], need)} for {dslib.VAR_OF[fg]}")
        return c
    colours = pair_check(vars_, "")
    if not any(colours.values()) and not any(to_hex(props.get("color"), vars_) for _, props, _ in rules):
        add("WATCH", "contrast_unchecked", "no colours could be read from the page's styles, so contrast was not checked",
            "put the colours in the --c- variables in a <style> block or a local stylesheet")
    dark = {}
    for sel, props, media in rules:
        if dslib.is_dark_selector(sel) or "prefers-color-scheme:dark" in dslib.media_key(media):
            dark.update({k: v for k, v in props.items() if k.startswith("--c-")})
    if dark:
        pair_check({**vars_, **dark}, "_dark")
    for sel, props, media in rules:
        fg = to_hex(props.get("color"), vars_)
        bgv = to_hex(props.get("background-color") or props.get("background"), vars_)
        if fg and bgv and not dslib.is_dark_selector(sel) and "dark" not in dslib.media_key(media):
            r = dslib.contrast(fg, bgv)
            large = bool(re.search(r"(^|[\s,>])h[12]\b|\.display\b", sel)) and not re.search(r"\s(p|li|span|a|small)\b", sel)
            need = dslib.AA_LARGE if large else dslib.AA_TEXT
            if r < need and not any(fg in i["message"] and bgv in i["message"] for i in items):
                add("FIX", "contrast_rule", f"{sel[:50]}: {fg} on {bgv} is {r}:1; it needs {need}:1",
                    f"try {dslib.shade_to_contrast(fg, bgv, need)}")

    # ---- the locked system
    if tokens:
        tcol = {k: dslib.norm_hex(v) for k, v in tokens.get("color", {}).items()}
        allowed = set(tcol.values()) | {dslib.norm_hex(v) for v in tokens.get("dark", {}).values()} | {"#ffffff", "#000000"}
        drift = [f"{dslib.VAR_OF[k]} is {colours.get(k)} (locked {tcol[k]})" for k in dslib.COLOR_KEYS
                 if tcol.get(k) and colours.get(k) and colours[k] != tcol[k]]
        if drift:
            add("FIX", "token_drift", "the page's colours drifted from the locked system: " + "; ".join(drift),
                "copy the variables from tokens.css")
        stray = set()
        for sel, props, media in rules:
            for k, v in props.items():
                if k.startswith("--c-"):
                    continue
                for hx in dslib.HEX_RE.findall(v):
                    if len(hx) in (5, 9):
                        continue
                    h = dslib.norm_hex(hx)
                    if h and h not in allowed:
                        stray.add(h)
        if stray:
            add("FIX", "off_system_colours", "colours not in the locked system: " + ", ".join(sorted(stray)[:8]),
                "use the --c- variables, or add the colour to the system on purpose")
        fams = {f.lower() for f in (tokens.get("font", {}).get("head", {}).get("family"),
                                    tokens.get("font", {}).get("body", {}).get("family")) if f}
        mono = tokens.get("font", {}).get("mono", {}).get("family")
        if mono:
            fams.add(mono.lower())
        bad = set()
        for sel, props, media in rules:
            for k in ("font-family", "--font-head", "--font-body", "font"):
                if k in props:
                    val = dslib.resolve(props[k], vars_)
                    if k == "font":
                        val = dslib.shorthand_family(val)
                    f = dslib.first_family(val)
                    if f and f.lower() not in fams and f.lower() not in dslib.GENERIC_FAMILIES:
                        bad.add(f)
        if bad:
            add("FIX", "off_system_fonts", "fonts not in the locked system: " + ", ".join(sorted(bad)),
                "use --font-head and --font-body")
    else:
        hexes = set()
        for sel, props, media in rules:
            for k, v in props.items():
                if not k.startswith("--"):
                    hexes |= {dslib.norm_hex(h) for h in dslib.HEX_RE.findall(v) if len(h) not in (5, 9)}
        hexes.discard(None)
        if len(hexes) > 6:
            add("WATCH", "colours_outside_variables", f"{len(hexes)} colours are written outside the variables",
                "route colours through --c- variables so the tweak bar and the lock can see them")

    # ---- mobile
    vp = [n for n in tree.root.walk() if n.tag == "meta" and (n.attrs.get("name") or "").lower() == "viewport"]
    if not vp or "width=device-width" not in (vp[0].attrs.get("content") or "").replace(" ", ""):
        add("FIX", "viewport", "no mobile viewport tag, so phones show a shrunken desktop page",
            '<meta name="viewport" content="width=device-width, initial-scale=1">')
    wide = []
    for sel, props, media in rules:
        if "max-width" in media and "min-width" not in media:
            continue
        for k in ("width", "min-width"):
            v = dslib.px(dslib.resolve(props.get(k, ""), vars_)) if props.get(k) else None
            if v and v > 400 and "min-width" not in media and not sel.startswith("[inline-iframe"):
                wide.append(sel[:30])
    if wide:
        add("WATCH", "fixed_widths", "fixed widths a phone may not fit: " + ", ".join(sorted(set(wide))[:5]),
            "use max-width, or set it inside a min-width media query")
    if a.render:
        r, why = run_render(page)
        if r is None:
            add("WATCH", "render", f"the phone test did not run ({why}); open the page on a phone and scroll sideways",
                "")
        else:
            if r["scrollWidth"] > r["clientWidth"] + 1:
                add("FIX", "sideways_scroll", f"the page scrolls sideways on a 375px phone ({r['scrollWidth']}px wide)",
                    "find the element wider than the screen: images need max-width:100%")
            if r.get("edge") is not None and r["edge"] < 12:
                add("WATCH", "phone_gutter", f"text comes within {max(0, r['edge']):.0f}px of the screen edge on a phone",
                    "keep at least 16px of space each side")
            if r.get("wrapped"):
                add("WATCH", "button_wraps", "a button label wraps onto two lines on a phone: " + "; ".join(r["wrapped"][:3]),
                    "shorten the label or let the button go full width")
            if r.get("bodyPx") and r["bodyPx"] < min_body and not any(i["id"] == "body_size" and i["level"] == "FIX" for i in items):
                add("FIX", "body_size_rendered", f"the body renders at {r['bodyPx']:g}px; this audience needs {min_body}px",
                    "")

    # ---- words
    text = tree.root.all_text()
    ph = sorted({m.group(0) for m in PLACEHOLDER.finditer(text)} | ({"[write: …]"} if "[write:" in src else set()))
    if ph:
        add("FIX", "placeholders", "placeholder text on the page: " + ", ".join(ph[:6]),
            "use the approved copy; never invent a line")
    known = ""
    for f in (a.business_file, a.copy):
        if f and Path(f).is_file():
            known += dslib.read_text(f)
    nums = sorted({m.group(0).strip() for m in NUMBER_RE.finditer(text)})
    if nums:
        if known:
            known_cores = {num_core(m.group(0)) for m in NUMBER_RE.finditer(known)} | set(re.findall(r"\d[\d,.]*", known))
            known_cores = {k.replace(",", "").rstrip(".") for k in known_cores}
            unknown = [n for n in nums if num_core(n).replace(",", "") not in known_cores]
            if unknown:
                add("FIX", "unsourced_numbers", "numbers on the page that are not in the Business File or the approved "
                    "copy: " + ", ".join(unknown[:8]), "take them out, or add the source to the File first")
        else:
            add("WATCH", "numbers", "numbers on the page to check against the Business File: " + ", ".join(nums[:8]), "")

    # ---- images
    imgs = [n for n in tree.root.walk() if n.tag == "img"]
    noalt = [n.attrs.get("src", "?")[:60] for n in imgs if "alt" not in n.attrs]
    if noalt:
        add("FIX", "img_alt", f"{len(noalt)} image(s) with no alt text: " + ", ".join(noalt[:4]),
            'describe the picture in a few words, or alt="" if it is decoration')
    manifest = {}
    if a.images and Path(a.images).is_file():
        for im in dslib.read_json(a.images).get("images", []):
            manifest[str(Path(im.get("file", "")).as_posix())] = im
    vault_hashes = set()
    if a.vault:
        tvdir = Path(a.vault) / "Design" / "Taste Vault"
        for f in tvdir.rglob("*"):
            if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                vault_hashes.add(hashlib.sha256(f.read_bytes()).hexdigest())
    local_bytes = len(src.encode())
    img_base = Path(a.images).parent if a.images else page.parent
    for n in imgs:
        s = n.attrs.get("src") or ""
        if re.match(r"^(https?:|//|data:)", s):
            if "taste vault" in s.lower():
                add("FIX", "reference_image", f"{s[:60]} comes from the taste vault", "references are for mood only")
            continue
        p = local_path(page.parent, s) or (page.parent / s)
        if "taste vault" in urllib.parse.unquote(s).lower() or (p.is_file() and vault_hashes and
                                          hashlib.sha256(p.read_bytes()).hexdigest() in vault_hashes):
            add("FIX", "reference_image", f"{s} is a taste-vault reference",
                "references are for mood only: use the member's photo or a generated image")
        if p.is_file():
            local_bytes += p.stat().st_size
        if a.images:
            try:
                key = str(p.resolve().relative_to(img_base.resolve()).as_posix())
            except ValueError:
                key = s
            im = manifest.get(key) or manifest.get(s)
            if not im:
                add("WATCH", "image_unlisted", f"{s} is not in images.json: where did it come from?",
                    "add it with its source (own, kie, licensed, stock)")
                continue
            source = (im.get("source") or "").lower()
            if source in ("reference", "unknown", ""):
                add("FIX", "image_rights", f"{s}: source '{source or 'blank'}' cannot go on a page",
                    "use the member's own photo, a licensed one, or generate one")
            if source == "kie" and im.get("person") and not im.get("consent"):
                add("FIX", "image_consent", f"{s}: a generated person with no consent on file",
                    "a real person's likeness needs §18 likeness consent; otherwise use a scene with no face")
            if source == "kie" and not im.get("ledger_key"):
                add("WATCH", "image_ledger", f"{s}: generated, but no ledger key recorded", "")
            if source == "stock" and not im.get("licence"):
                add("WATCH", "image_licence", f"{s}: stock photo with no licence noted", "")
    for href in tree.links:
        p = page.parent / href
        if href and p.is_file():
            local_bytes += p.stat().st_size
    if local_bytes > 2_000_000:
        add("WATCH", "page_weight", f"the page and its local files weigh {local_bytes / 1e6:.1f} MB",
            "compress photos (about 200 KB each is plenty) and use WebP or JPEG")

    # ---- structure
    h1 = [n for n in tree.root.walk() if n.tag == "h1"]
    if len(h1) != 1:
        add("WATCH", "h1", f"{len(h1)} main headings (h1); a page reads best with exactly one", "")
    html_el = next((n for n in tree.root.walk() if n.tag == "html"), None)
    if not html_el or not html_el.attrs.get("lang"):
        add("WATCH", "lang", "no lang attribute on <html>; screen readers guess the language", '<html lang="en">')
    if not any(n.tag == "title" for n in tree.root.walk()):
        add("WATCH", "title", "no <title>; the browser tab and search results show the file name", "")
    ctas = set()
    for n in tree.root.walk():
        if ((n.tag == "button" and (n.attrs.get("type") or "submit").lower() == "submit" and "aria-expanded" not in n.attrs)
                or (n.tag == "a" and re.search(r"\b(btn|button|cta)\b", n.cls()))) and not any(
                p.tag in ("nav", "header", "footer", "details", "summary") for p in ancestors(n)):
            t = n.all_text().strip().lower()
            if t:
                ctas.add(t)
    if len(ctas) > 2:
        add("WATCH", "one_action", "more than two different main actions: " + "; ".join(sorted(ctas)[:5]),
            "one action, repeated, converts better than several competing ones")
    weights = set()
    for sel, props, media in rules:
        for k in ("font-weight", "--w-head"):
            if k in props:
                weights.add(dslib.resolve(props[k], vars_).strip())
    if len(weights) > 3:
        add("WATCH", "weights", f"{len(weights)} font weights ({', '.join(sorted(weights))})", "two or three is enough")
    moves = re.search(r"@keyframes|animation\s*:|transition\s*:", css)
    if moves and "prefers-reduced-motion" not in css:
        add("WATCH", "reduced_motion", "motion with no reduced-motion setting; some visitors get dizzy",
            "@media (prefers-reduced-motion: reduce) { :root { --motion: 0; } }")
    if re.search(r"fonts\.(googleapis|gstatic)\.com", src):
        add("WATCH", "font_hosting", "fonts load from Google's servers",
            "self-host the font files before going live (fonts.md)")
    for t in tells(src, page.parent):
        add("WATCH", "tell_" + t["id"], f"generic tell: {t['name']} ({t['where']})",
            "see anti-generic.md for the fix")

    fixes = [i for i in items if i["level"] == "FIX"]
    verdict = "GO" if not fixes else "FIX"
    out = {"ok": verdict == "GO", "verdict": verdict, "page": str(page), "audience": audience,
           "body_px": body_px, "fix": len(fixes), "watch": len(items) - len(fixes), "items": items,
           "checked": str(date.today()), "with_tokens": bool(tokens)}
    if a.out:
        md = [f"# Design check · {page.name}", "", f"**{verdict}** · {date.today()} · audience {audience}"
              + (" · against the locked system" if tokens else ""), ""]
        for lvl in ("FIX", "WATCH"):
            rows = [i for i in items if i["level"] == lvl]
            if rows:
                md += [f"## {lvl} ({len(rows)})", ""]
                md += [f"- **{i['id']}**: {i['message']}" + (f". Fix: {i['fix']}" if i["fix"] else "") for i in rows]
                md.append("")
        if not items:
            md.append("Nothing to fix or watch.")
        dslib.write_atomic(a.out, "\n".join(md) + "\n")
    return out, 0 if verdict == "GO" else 1


def ancestors(n):
    p = n.parent
    while p is not None:
        yield p
        p = p.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--page", required=True)
    c.add_argument("--tokens"); c.add_argument("--audience", choices=["50plus", "general"])
    c.add_argument("--images"); c.add_argument("--vault"); c.add_argument("--business-file"); c.add_argument("--copy")
    c.add_argument("--render", action="store_true"); c.add_argument("--out")
    t = sub.add_parser("tells"); t.add_argument("--page", required=True)
    a = ap.parse_args()
    if a.cmd == "tells":
        p = Path(a.page)
        if not p.is_file():
            dslib.emit({"ok": False, "error": f"page not found: {p}"}, 2)
        found = tells(p.read_text(encoding="utf-8", errors="replace"), p.parent)
        dslib.emit({"ok": True, "count": len(found), "tells": found})
    out, code = check(a)
    dslib.emit(out, code)


if __name__ == "__main__":
    main()
