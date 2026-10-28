#!/usr/bin/env python3
"""Publish a gated answer page and get it indexed, for the Search & Answer Engine.

Takes a page that passed `answer_check.py check`, renders it to clean HTML, and publishes it through
the member's builder where the builder has an API (WordPress, Webflow, Shopify, Wix blog). For every
other builder (Squarespace, Kajabi, GoHighLevel, Google Sites, Carrd) it writes the HTML and a paste
checklist. Then it tells Bing and Copilot through IndexNow, checks the live page, and records the URL.

Keys live in `.env` in the folder that holds the Business File (`KEY=value` lines). They are read,
never printed, never written anywhere else. `keys` says which are set, by name only.

  python3 publish.py keys                                        # which keys .env holds (names only) and which builders that unlocks
  python3 publish.py render search/answers/<slug>.md [--site https://…] [--schema search/answers/<slug>.jsonld]   # HTML + paste checklist, no network
  python3 publish.py publish search/answers/<slug>.md --builder wordpress|webflow|shopify|wix|manual --site https://… [--path answers/<slug>] [--draft] [--dry-run]
  python3 publish.py indexnow-key [--site https://…]             # write the key file the member uploads to the site root
  python3 publish.py indexnow https://…/answers/<slug> [--site https://…] [--dry-run]
  python3 publish.py verify https://…/answers/<slug> [--expect "<a phrase from the page>"]   # live? indexable? in the sitemap? crawlers allowed?
  python3 publish.py record search/answers/<slug>.md --url https://…/answers/<slug> [--questions search/questions.json]

Keys by builder (`.env`): WordPress `WP_USER`, `WP_APP_PASSWORD` (an application password, not the login password);
Webflow `WEBFLOW_API_TOKEN`, `WEBFLOW_COLLECTION_ID`; Shopify `SHOPIFY_STORE` (the myshopify.com host), `SHOPIFY_ACCESS_TOKEN`;
Wix `WIX_API_KEY`, `WIX_SITE_ID`; IndexNow `INDEXNOW_KEY` (any 32-character key; `indexnow-key` makes one).
Google has no legitimate API for requesting indexing of ordinary pages: the sitemap, the home-page link and the
member's click on "request indexing" in Search Console are the route, and `verify` checks the first two.

Exit code 0 on success, 1 when a check fails or a request is refused, 2 on a usage error.
"""
import argparse
import base64
import html
import json
import os
import re
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True

BUILDERS = ("wordpress", "webflow", "shopify", "wix", "manual")
NEEDS = {"wordpress": ("WP_USER", "WP_APP_PASSWORD"), "webflow": ("WEBFLOW_API_TOKEN", "WEBFLOW_COLLECTION_ID"),
         "shopify": ("SHOPIFY_STORE", "SHOPIFY_ACCESS_TOKEN"), "wix": ("WIX_API_KEY", "WIX_SITE_ID"), "manual": ()}
ALL_KEYS = sorted({k for v in NEEDS.values() for k in v} | {"INDEXNOW_KEY"})
NO_API = ("Squarespace", "Kajabi", "GoHighLevel", "Google Sites", "Carrd")
SEARCH_CRAWLERS = ("Googlebot", "Bingbot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User",
                   "Claude-SearchBot", "Claude-User", "Applebot", "Amzn-SearchBot", "Meta-WebIndexer")
TIMEOUT = 20
UA = "BuildRoomOS-publish/1.0"
MARKER = re.compile(r"\[(S\d+|own|method)\]")
FENCE = re.compile(r"```(\w*)\n(.*?)```", re.S)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------- .env

def load_env(folder="."):
    """KEY=value lines from .env next to the Business File; the process environment wins. Values are never printed."""
    env = {}
    p = Path(folder) / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip().lstrip("export ").strip()
            v = v.strip().strip("'\"")
            if k:
                env[k] = v
    for k in ALL_KEYS:
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def mask(text, env):
    """Replace any secret value with ••• so a dry run or an error can be shown safely."""
    for v in env.values():
        if v and len(v) >= 6:
            text = text.replace(v, "•••")
    return text


def cmd_keys(a):
    env = load_env(a.env_dir)
    present = [k for k in ALL_KEYS if env.get(k)]
    unlocked = [b for b, needs in NEEDS.items() if b != "manual" and all(env.get(k) for k in needs)]
    print(json.dumps({"ok": True, "keys_set": present, "keys_missing": [k for k in ALL_KEYS if k not in present],
                      "builders_unlocked": unlocked, "indexnow": bool(env.get("INDEXNOW_KEY")),
                      "note": "Values are never shown. Squarespace, Kajabi, GoHighLevel, Google Sites and Carrd have no page API: use `render` and paste."}, indent=2))


# ---------------------------------------------------------------- markdown → html

def parse_front_matter(text):
    m = re.match(r"^﻿?---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, text
    fm, body, key = {}, m.group(2), None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        line = re.sub(r"\s+#\s.*$", "", line)
        lm = re.match(r"^\s+-\s*(.*)$", line)
        if lm and key:
            fm.setdefault(key, [])
            if not isinstance(fm[key], list):
                fm[key] = [fm[key]] if fm[key] else []
            fm[key].append(lm.group(1).strip())
            continue
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km:
            key = km.group(1).strip()
            fm[key] = km.group(2).strip()
    return fm, body


def inline(md):
    """Bold, italic, links, source markers as footnote links; [own]/[method] removed."""
    t = html.escape(md, quote=False)
    t = re.sub(r"\[(S(\d+))\]", lambda m: f'<sup><a href="#source-{m.group(2)}">{m.group(2)}</a></sup>', t)
    t = re.sub(r"\s*\[(?:own|method)\]", "", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*\n]+?)\*(?!\w)", r"<em>\1</em>", t)
    return t


def md_to_html(body):
    """A small, predictable converter for the answer-page shape: H1 (dropped, the builder sets the title), H2/H3,
    paragraphs, bullet and numbered lists, pipe tables, code fences dropped (schema goes in the head)."""
    body = FENCE.sub("", body)
    out, para, lst, table = [], [], None, []
    h1 = ""

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []

    def flush_list():
        nonlocal lst
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            lst = None

    def flush_table():
        nonlocal table
        if table:
            rows = [r for r in table if not re.match(r"^\s*\|?\s*-{2,}", r)]
            cells = [[inline(c.strip()) for c in r.strip().strip("|").split("|")] for r in rows]
            if cells:
                head = "".join(f"<th>{c}</th>" for c in cells[0])
                rest = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in cells[1:])
                out.append(f"<table><thead><tr>{head}</tr></thead><tbody>{rest}</tbody></table>")
            table = []

    for raw in body.splitlines():
        line = raw.rstrip()
        if line.startswith("# ") and not h1:
            h1 = line[2:].strip()
            continue
        if not line.strip():
            flush_para(); flush_list(); flush_table()
            continue
        if line.startswith("|"):
            flush_para(); flush_list()
            table.append(line)
            continue
        flush_table()
        hm = re.match(r"^(#{2,3})\s+(.*)$", line)
        if hm:
            flush_para(); flush_list()
            level = len(hm.group(1))
            text = hm.group(2).strip()
            hid = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(f'<h{level} id="{hid}">{inline(text)}</h{level}>')
            continue
        lm = re.match(r"^\s*[-*]\s+(.*)$", line)
        nm = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if lm or nm:
            flush_para()
            tag = "ul" if lm else "ol"
            item = (lm or nm).group(1)
            sm = re.match(r"^\[S(\d+)\]\s*(.*)$", item)
            li = f'<li id="source-{sm.group(1)}">{inline(sm.group(2))}</li>' if sm else f"<li>{inline(item)}</li>"
            if lst and lst[0] == tag:
                lst[1].append(li)
            else:
                flush_list()
                lst = (tag, [li])
            continue
        flush_list()
        para.append(line.strip())
    flush_para(); flush_list(); flush_table()
    return h1, "\n".join(out)


def render_page(path, site="", schema_path=""):
    p = Path(path)
    if not p.exists():
        die(f"{p} not found")
    fm, body = parse_front_matter(p.read_text(encoding="utf-8"))
    if fm is None:
        die("no front matter; run answer_check.py check first")
    if fm.get("status") not in ("ready", "published", "needs-update"):
        die(f"the page's status is '{fm.get('status')}'; set it to ready once answer_check.py check says READY")
    h1, inner = md_to_html(body)
    title = fm.get("title") or h1
    desc = ""
    m = re.search(r"<p><strong>Short answer:</strong>\s*(.*?)</p>", inner, re.S)
    if m:
        desc = re.sub(r"<[^>]+>", "", m.group(1)).strip()[:300]
    schema = ""
    if schema_path and Path(schema_path).exists():
        schema = Path(schema_path).read_text(encoding="utf-8").strip()
    return fm, {"title": title, "h1": h1, "description": desc, "slug": fm.get("slug", p.stem), "inner_html": inner, "schema": schema,
                "author": fm.get("author", ""), "published": fm.get("published", ""), "updated": fm.get("updated", "")}


def full_html(page, site="", path=""):
    url = f"{site.rstrip('/')}/{path.strip('/')}" if site and path else ""
    head = [f"<title>{html.escape(page['title'])}</title>", '<meta charset="utf-8">', '<meta name="viewport" content="width=device-width, initial-scale=1">']
    if page["description"]:
        head.append(f'<meta name="description" content="{html.escape(page["description"], quote=True)}">')
    if url:
        head.append(f'<link rel="canonical" href="{html.escape(url, quote=True)}">')
    if page["schema"]:
        head.append('<script type="application/ld+json">\n' + page["schema"] + "\n</script>")
    return "<!doctype html>\n<html lang=\"en\">\n<head>\n" + "\n".join(head) + "\n</head>\n<body>\n<article>\n" + \
           f"<h1>{html.escape(page['h1'])}</h1>\n" + page["inner_html"] + "\n</article>\n</body>\n</html>\n"


def paste_checklist(page, site, path):
    url = f"{site.rstrip('/')}/{path.strip('/')}" if site else f"/{path.strip('/')}"
    return "\n".join([
        f"# Paste checklist · {page['title']}", "",
        "Your builder has no page API, so this is a ten-minute paste. Tick each line.", "",
        f"1. New page. Address (slug): `{path.strip('/')}` so the page lives at {url}.",
        f"2. Page title: {page['title']}",
        f"3. Heading at the top (H1): {page['h1']}",
        "4. Paste the body from the HTML file (or type it): the short answer first, then each heading as a Heading 2, the lists as lists, the table as a table.",
        f"5. Page description (the search snippet): {page['description'] or '(the short answer, first sentence)'}",
        "6. The author line and the Updated date are in the body; leave them.",
        "7. Alt text on any image.",
        "8. If the builder has a header-code field for this page, paste the schema file; if not, skip it.",
        "9. Publish. Open the page on your phone: does it load, is the answer at the top, does the next-step link work?",
        "10. Link to this page from its service page and from one older answer; make sure the home page links to every service page.",
        "11. Google Search Console → URL inspection → paste the address → Request indexing.",
        f"12. Then: `publish.py indexnow {url}` (Bing and Copilot) and `publish.py verify {url}`.",
        f"13. Then: `publish.py record <page.md> --url {url}`.", "",
    ])


def cmd_render(a):
    fm, page = render_page(a.file, a.site, a.schema)
    folder = Path(a.file).parent
    path = a.path or f"answers/{page['slug']}"
    out_html = folder / f"{page['slug']}.html"
    out_md = folder / f"{page['slug']}-paste.md"
    out_html.write_text(full_html(page, a.site, path), encoding="utf-8")
    out_md.write_text(paste_checklist(page, a.site, path), encoding="utf-8")
    print(json.dumps({"ok": True, "html": str(out_html), "checklist": str(out_md), "title": page["title"], "description_chars": len(page["description"])}, indent=2))


# ---------------------------------------------------------------- http

def reroute(url):
    """Tests point every outside call at a local server with BUILDROOM_TEST_ENDPOINT; never set in normal use."""
    base = os.environ.get("BUILDROOM_TEST_ENDPOINT")
    if not base:
        return url
    u = urllib.parse.urlparse(url)
    return base.rstrip("/") + u.path + (("?" + u.query) if u.query else "")


def request(method, url, env, headers=None, data=None, dry_run=False, expect=(200, 201)):
    url = reroute(url)
    hdrs = {"User-Agent": UA, "Accept": "application/json"}
    hdrs.update(headers or {})
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    if dry_run:
        shown = {k: ("•••" if k.lower() in ("authorization", "x-shopify-access-token") else v) for k, v in hdrs.items()}
        return {"dry_run": True, "method": method, "url": url, "headers": shown, "body": json.loads(mask(json.dumps(data), env)) if data is not None else None}
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read().decode("utf-8", errors="replace")
            try:
                return {"status": r.status, "json": json.loads(raw) if raw.strip() else {}}
            except json.JSONDecodeError:
                return {"status": r.status, "text": raw[:500]}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")[:500]
        return {"status": e.code, "error": mask(raw, env)}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {"status": 0, "error": mask(str(e), env)}


def fetch(url, env=None, headers=None):
    url = reroute(url)
    hdrs = {"User-Agent": UA}
    hdrs.update(headers or {})
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.read().decode("utf-8", errors="replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace"), dict(e.headers)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, str(e), {}


def need(env, builder):
    missing = [k for k in NEEDS[builder] if not env.get(k)]
    if missing:
        die(f"{builder} needs {', '.join(missing)} in .env (never paste a key into the chat; put it in the file)")


# ---------------------------------------------------------------- builders

def publish_wordpress(page, env, site, path, draft, dry_run):
    need(env, "wordpress")
    api = f"{site.rstrip('/')}/wp-json/wp/v2/pages"
    token = base64.b64encode(f"{env['WP_USER']}:{env['WP_APP_PASSWORD']}".encode()).decode()
    hdrs = {"Authorization": f"Basic {token}"}
    slug = path.strip("/").split("/")[-1]
    data = {"title": page["title"], "slug": slug, "status": "draft" if draft else "publish", "content": page["inner_html"],
            "excerpt": page["description"]}
    existing = request("GET", f"{api}?slug={urllib.parse.quote(slug)}&status=any", env, hdrs, dry_run=dry_run) if not dry_run else {"json": []}
    items = existing.get("json") if isinstance(existing.get("json"), list) else []
    if items:
        r = request("POST", f"{api}/{items[0]['id']}", env, hdrs, data, dry_run)
    else:
        r = request("POST", api, env, hdrs, data, dry_run)
    url = (r.get("json") or {}).get("link", "") if not dry_run else ""
    return r, url, "WordPress page (application password; the page's header code is the theme's job, paste the schema into an SEO plugin's field if you use one)"


def publish_webflow(page, env, site, path, draft, dry_run):
    need(env, "webflow")
    coll = env["WEBFLOW_COLLECTION_ID"]
    hdrs = {"Authorization": f"Bearer {env['WEBFLOW_API_TOKEN']}"}
    slug = path.strip("/").split("/")[-1]
    data = {"isDraft": bool(draft), "isArchived": False,
            "fieldData": {"name": page["title"], "slug": slug, "post-body": page["inner_html"], "post-summary": page["description"]}}
    endpoint = f"https://api.webflow.com/v2/collections/{coll}/items" + ("" if draft else "/live")
    r = request("POST", endpoint, env, hdrs, data, dry_run)
    url = f"{site.rstrip('/')}/{path.strip('/')}" if site and not dry_run and r.get("status") in (200, 201, 202) else ""
    return r, url, "Webflow CMS item (fields name, slug, post-body, post-summary; rename them to match your collection if they differ)"


def publish_shopify(page, env, site, path, draft, dry_run):
    need(env, "shopify")
    store = env["SHOPIFY_STORE"].replace("https://", "").strip("/")
    hdrs = {"X-Shopify-Access-Token": env["SHOPIFY_ACCESS_TOKEN"]}
    slug = path.strip("/").split("/")[-1]
    data = {"page": {"title": page["title"], "handle": slug, "body_html": page["inner_html"], "published": not draft}}
    r = request("POST", f"https://{store}/admin/api/2025-01/pages.json", env, hdrs, data, dry_run)
    url = f"https://{store.replace('.myshopify.com', '')}/pages/{slug}" if site == "" else f"{site.rstrip('/')}/pages/{slug}"
    return r, (url if not dry_run and r.get("status") in (200, 201) else ""), "Shopify page (Admin API; pages live at /pages/<handle>)"


def ricos_text(md):
    """Ricos rich-content text nodes from one line of markdown: bold and links as decorations."""
    nodes, pos = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)", md):
        if m.start() > pos:
            nodes.append({"type": "TEXT", "textData": {"text": md[pos:m.start()], "decorations": []}})
        if m.group(1):
            nodes.append({"type": "TEXT", "textData": {"text": m.group(1), "decorations": [{"type": "BOLD", "fontWeightValue": 700}]}})
        else:
            nodes.append({"type": "TEXT", "textData": {"text": m.group(2), "decorations": [{"type": "LINK", "linkData": {"link": {"url": m.group(3)}}}]}})
        pos = m.end()
    if pos < len(md):
        nodes.append({"type": "TEXT", "textData": {"text": md[pos:], "decorations": []}})
    return [n for n in nodes if n["textData"]["text"]]


def md_to_ricos(body):
    body = FENCE.sub("", body)
    nodes, para, items = [], [], []

    def clean(t):
        return re.sub(r"\s*\[(?:own|method)\]", "", re.sub(r"\[S(\d+)\]", r"[\1]", t))

    def flush_para():
        nonlocal para
        if para:
            nodes.append({"type": "PARAGRAPH", "nodes": ricos_text(clean(" ".join(para)))})
            para = []

    def flush_list():
        nonlocal items
        if items:
            nodes.append({"type": "BULLETED_LIST", "nodes": [{"type": "LIST_ITEM", "nodes": [{"type": "PARAGRAPH", "nodes": ricos_text(clean(i))}]} for i in items]})
            items = []

    for raw in body.splitlines():
        line = raw.rstrip()
        if line.startswith("# "):
            continue
        if not line.strip():
            flush_para(); flush_list()
            continue
        hm = re.match(r"^(#{2,3})\s+(.*)$", line)
        if hm:
            flush_para(); flush_list()
            nodes.append({"type": "HEADING", "headingData": {"level": len(hm.group(1))}, "nodes": ricos_text(clean(hm.group(2)))})
            continue
        lm = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*)$", line)
        if lm:
            flush_para()
            items.append(lm.group(1))
            continue
        if line.startswith("|"):
            if re.match(r"^\s*\|?\s*-{2,}", line):
                continue
            flush_list()
            para.append(" · ".join(c.strip() for c in line.strip().strip("|").split("|")))
            flush_para()
            continue
        flush_list()
        para.append(line.strip())
    flush_para(); flush_list()
    return {"nodes": nodes}


def publish_wix(page, env, site, path, draft, dry_run, body_md=""):
    need(env, "wix")
    hdrs = {"Authorization": env["WIX_API_KEY"], "wix-site-id": env["WIX_SITE_ID"]}
    slug = path.strip("/").split("/")[-1]
    data = {"draftPost": {"title": page["title"], "slug": slug, "excerpt": page["description"], "richContent": md_to_ricos(body_md)},
            "publish": not draft}
    r = request("POST", "https://www.wixapis.com/blog/v3/draft-posts", env, hdrs, data, dry_run)
    url = ""
    if not dry_run and r.get("status") in (200, 201):
        post = (r.get("json") or {}).get("draftPost", {})
        url = post.get("url", {}).get("url", "") if isinstance(post.get("url"), dict) else f"{site.rstrip('/')}/post/{slug}"
    return r, url, "Wix blog post (Blog API; tables become one line per row; the page lives under /post/<slug> unless your blog uses another path)"


def cmd_publish(a):
    env = load_env(a.env_dir)
    if a.builder not in BUILDERS:
        die(f"--builder must be one of {', '.join(BUILDERS)}")
    fm, page = render_page(a.file, a.site, a.schema)
    path = a.path or f"answers/{page['slug']}"
    folder = Path(a.file).parent
    if a.builder == "manual":
        (folder / f"{page['slug']}.html").write_text(full_html(page, a.site, path), encoding="utf-8")
        (folder / f"{page['slug']}-paste.md").write_text(paste_checklist(page, a.site, path), encoding="utf-8")
        print(json.dumps({"ok": True, "builder": "manual", "html": str(folder / f"{page['slug']}.html"), "checklist": str(folder / f"{page['slug']}-paste.md"),
                          "note": f"No page API for {', '.join(NO_API)}: paste from the checklist, then `indexnow`, `verify` and `record`."}, indent=2))
        return
    body_md = parse_front_matter(Path(a.file).read_text(encoding="utf-8"))[1]
    fn = {"wordpress": publish_wordpress, "webflow": publish_webflow, "shopify": publish_shopify}.get(a.builder)
    if a.builder == "wix":
        r, url, how = publish_wix(page, env, a.site, path, a.draft, a.dry_run, body_md)
    else:
        r, url, how = fn(page, env, a.site, path, a.draft, a.dry_run)
    if a.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "builder": a.builder, "how": how, "request": r}, indent=2, ensure_ascii=False))
        return
    ok = r.get("status") in (200, 201, 202)
    out = {"ok": ok, "builder": a.builder, "how": how, "status": r.get("status"), "url": url, "draft": a.draft}
    if not ok:
        out["error"] = r.get("error") or r.get("text") or "the builder refused the request"
        out["next"] = "check the key in .env, the site address and the builder's permissions; nothing was recorded"
    else:
        out["next"] = (f"open {url or 'the page'} on a phone; then `publish.py indexnow {url}`, `publish.py verify {url}`, "
                       f"`publish.py record {a.file} --url {url}`; then Search Console → URL inspection → Request indexing")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    sys.exit(0 if ok else 1)


# ---------------------------------------------------------------- indexnow

def cmd_indexnow_key(a):
    env = load_env(a.env_dir)
    key = env.get("INDEXNOW_KEY") or secrets.token_hex(16)
    folder = Path(a.env_dir)
    (folder / "search").mkdir(parents=True, exist_ok=True)
    keyfile = folder / "search" / f"{key}.txt"
    keyfile.write_text(key, encoding="utf-8")
    if not env.get("INDEXNOW_KEY"):
        with open(folder / ".env", "a", encoding="utf-8") as f:
            f.write(f"\nINDEXNOW_KEY={key}\n")
    site = a.site.rstrip("/") if a.site else "https://YOUR-DOMAIN"
    print(json.dumps({"ok": True, "key_file": str(keyfile), "upload_to": f"{site}/{key}.txt",
                      "note": "Upload the key file to the site root (Wix and WordPress with Rank Math can host it for you; Squarespace cannot, so skip IndexNow there). "
                              "The key is in .env; it is not a secret in the usual sense but keep it there."}, indent=2))


def cmd_indexnow(a):
    env = load_env(a.env_dir)
    key = env.get("INDEXNOW_KEY")
    if not key:
        die("INDEXNOW_KEY is not in .env; run `indexnow-key` first")
    urls = a.urls
    host = urllib.parse.urlparse(urls[0]).netloc
    if not host:
        die("give full page addresses, https://…")
    key_url = f"https://{host}/{key}.txt"
    if not a.dry_run and not a.skip_key_check:
        status, text, _ = fetch(key_url, env)
        if status != 200 or text.strip() != key:
            print(json.dumps({"ok": False, "key_file": key_url, "status": status,
                              "note": "the key file is not live at the site root, so IndexNow will ignore the ping; upload it first (`indexnow-key` wrote it)"}, indent=2))
            sys.exit(1)
    data = {"host": host, "key": key, "keyLocation": key_url, "urlList": urls}
    r = request("POST", "https://api.indexnow.org/indexnow", env, {}, data, a.dry_run, expect=(200, 202))
    if a.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "request": r}, indent=2))
        return
    ok = r.get("status") in (200, 202)
    print(json.dumps({"ok": ok, "status": r.get("status"), "urls": urls,
                      "note": "Accepted: Bing and Copilot (and the other IndexNow engines) will fetch it; this does not reach Google." if ok
                      else f"refused ({r.get('error') or r.get('text') or 'no detail'}); 403 usually means the key file is wrong, 422 a bad URL"}, indent=2))
    sys.exit(0 if ok else 1)


# ---------------------------------------------------------------- verify

def robots_blocks(text, agents):
    groups, current, open_run = {}, [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, val = [x.strip() for x in line.split(":", 1)]
        k = key.lower()
        if k == "user-agent":
            if not open_run:
                current, open_run = [], True
            current.append(val.lower())
            groups.setdefault(val.lower(), [])
        elif k in ("allow", "disallow"):
            open_run = False
            for ua in current or ["*"]:
                groups.setdefault(ua, []).append((k, val))
        else:
            open_run = False
    blocked = []
    for agent in agents:
        rules = groups.get(agent.lower(), groups.get("*", []))
        best = None
        for rule, path in rules:
            if rule == "disallow" and path == "":
                continue
            if path and "/".startswith(path):
                if best is None or len(path) > len(best[1]):
                    best = (rule, path)
        if best and best[0] == "disallow":
            blocked.append(agent)
    return blocked


def sitemap_has(site_root, url, env, depth=0):
    """True if the URL appears in /sitemap.xml (following a sitemap index one level)."""
    status, text, _ = fetch(f"{site_root}/sitemap.xml", env)
    if status != 200:
        return None
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text)
    if url in locs or url.rstrip("/") in [l.rstrip("/") for l in locs]:
        return True
    if "<sitemapindex" in text and depth == 0:
        for child in locs[:20]:
            s, t, _ = fetch(child, env)
            if s == 200 and (url in t or url.rstrip("/") + "<" in t):
                return True
    return False


def cmd_verify(a):
    env = load_env(a.env_dir)
    url = a.url
    parsed = urllib.parse.urlparse(url)
    if not parsed.netloc:
        die("give the full page address, https://…")
    root = f"{parsed.scheme}://{parsed.netloc}"
    checks = {}
    status, text, headers = fetch(url, env)
    checks["live_200"] = status == 200
    low = text.lower()
    checks["has_h1"] = "<h1" in low
    checks["no_noindex"] = not re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', text, re.I) and "noindex" not in (headers.get("X-Robots-Tag") or "").lower()
    canon = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', text, re.I)
    checks["canonical_matches"] = (canon is None) or canon.group(1).rstrip("/") == url.rstrip("/")
    checks["has_title"] = bool(re.search(r"<title>[^<]{5,}</title>", text, re.I))
    if a.expect:
        checks["expected_text_present"] = a.expect.lower() in re.sub(r"<[^>]+>", " ", low)
    rs, rtext, _ = fetch(f"{root}/robots.txt", env)
    blocked = robots_blocks(rtext, SEARCH_CRAWLERS) if rs == 200 else []
    checks["answer_crawlers_allowed"] = not blocked
    in_map = sitemap_has(root, url, env)
    checks["in_sitemap"] = bool(in_map)
    ok = all(checks.values())
    notes = []
    if not checks["live_200"]:
        notes.append(f"the page returned {status or 'no response'}; it is not live yet, or the address differs")
    if not checks["no_noindex"]:
        notes.append("the page carries noindex; turn it off in the builder's page settings")
    if not checks["canonical_matches"]:
        notes.append(f"the canonical points elsewhere ({canon.group(1)}); fix the page setting or use that address")
    if blocked:
        notes.append("robots.txt blocks " + ", ".join(blocked) + ": turn off the builder's 'block AI bots' switch")
    if in_map is None:
        notes.append("no sitemap at /sitemap.xml; find the builder's sitemap address and submit it in Search Console and Bing")
    elif not in_map:
        notes.append("the page is not in the sitemap yet; most builders add it within a day, then Search Console → request indexing")
    if a.expect and not checks.get("expected_text_present", True):
        notes.append("the expected phrase is not on the live page; the paste may be incomplete")
    print(json.dumps({"ok": ok, "url": url, "checks": checks, "notes": notes,
                      "google": "Google: Search Console → URL inspection → Request indexing (a click the member makes; there is no legitimate API for ordinary pages). "
                                "Bing and Copilot: `publish.py indexnow`. ChatGPT and Perplexity crawl on their own once the page is linked and allowed."}, indent=2))
    sys.exit(0 if ok else 1)


# ---------------------------------------------------------------- record

def cmd_record(a):
    p = Path(a.file)
    if not p.exists():
        die(f"{p} not found")
    text = p.read_text(encoding="utf-8")
    fm, _ = parse_front_matter(text)
    if fm is None:
        die("no front matter")
    today = date.today().isoformat()
    text = re.sub(r"^status:.*$", "status: published", text, count=1, flags=re.M)
    if re.search(r"^url:.*$", text, flags=re.M):
        text = re.sub(r"^url:.*$", f"url: {a.url}", text, count=1, flags=re.M)
    else:
        text = re.sub(r"^(updated:.*)$", rf"\1\nurl: {a.url}", text, count=1, flags=re.M)
    if not fm.get("published"):
        text = re.sub(r"^published:.*$", f"published: {today}", text, count=1, flags=re.M)
    p.write_text(text, encoding="utf-8")
    out = {"ok": True, "file": str(p), "url": a.url, "status": "published"}
    qp = Path(a.questions) if a.questions else None
    if qp and qp.exists() and fm.get("id"):
        data = json.loads(qp.read_text(encoding="utf-8"))
        q = next((x for x in data.get("questions", []) if x.get("id") == fm["id"]), None)
        if q:
            q["status"] = "published"
            q["published_url"] = a.url
            q["published_on"] = q.get("published_on") or today
            q["updated_on"] = today
            data["updated"] = today
            qp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            out["question"] = fm["id"]
        else:
            out["note"] = f"{fm['id']} is not in the question map; add it so the map stays the one list"
    print(json.dumps(out, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env-dir", default=".", help="the folder holding .env (default: the current folder, where the Business File lives)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("keys"); s.set_defaults(f=cmd_keys)
    s = sub.add_parser("render"); s.add_argument("file"); s.add_argument("--site", default=""); s.add_argument("--path", default=""); s.add_argument("--schema", default=""); s.set_defaults(f=cmd_render)
    s = sub.add_parser("publish"); s.add_argument("file"); s.add_argument("--builder", required=True); s.add_argument("--site", default="")
    s.add_argument("--path", default=""); s.add_argument("--schema", default=""); s.add_argument("--draft", action="store_true"); s.add_argument("--dry-run", action="store_true"); s.set_defaults(f=cmd_publish)
    s = sub.add_parser("indexnow-key"); s.add_argument("--site", default=""); s.set_defaults(f=cmd_indexnow_key)
    s = sub.add_parser("indexnow"); s.add_argument("urls", nargs="+"); s.add_argument("--site", default=""); s.add_argument("--dry-run", action="store_true")
    s.add_argument("--skip-key-check", action="store_true"); s.set_defaults(f=cmd_indexnow)
    s = sub.add_parser("verify"); s.add_argument("url"); s.add_argument("--expect", default=""); s.set_defaults(f=cmd_verify)
    s = sub.add_parser("record"); s.add_argument("file"); s.add_argument("--url", required=True); s.add_argument("--questions", default=""); s.set_defaults(f=cmd_record)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
