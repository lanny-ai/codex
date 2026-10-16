#!/usr/bin/env node
/*
 * LinkedIn Engine renderer: the profile banner, document carousels, post image cards and Featured
 * thumbnails, set in the member's brand fonts and colours with every word taken from the approved spec.
 * Checks text overflow, minimum sizes, contrast (text, accent and muted colours against the background;
 * an accent below 3:1 FAILs when the accent carries text: kicker, CTA, numerals, swipe hint, list numbers),
 * that every declared brand font actually loaded (FAIL if not), and (banner) that nothing sits under the
 * profile photo. Warns on a card or slide headline over 20 words, a carousel without a document title,
 * and a card, featured image or carousel without alt text.
 *
 * Usage
 *   node render_linkedin.mjs linkedin/specs/banner.json [more specs...] --out linkedin/renders/ [--overlay]
 *
 * Needs Playwright (npm i playwright, then npx playwright install chromium), or CHROME_PATH pointing
 * at an installed Chrome, Edge or Chromium. A very long TMPDIR (Chromium's socket path limit) is replaced
 * by /tmp for the browser.
 *
 * Layouts and outputs
 *   banner    1584 × 396 (rendered at 2x)  → <id>.png (+ <id>_safe.png with --overlay: the photo zones marked)
 *   card      1200 × 1500 post image        → <id>.png
 *   featured  1200 × 627 Featured thumbnail → <id>.png
 *   carousel  1080 × 1350 per slide         → <id>.pdf (upload as a LinkedIn document) + <id>_01.png … previews
 * Report: <id>.report.json with every check, plus the spec's title and alt text (and, for a carousel, each
 * slide's kind, numeral and alt), so the file and its upload text travel together. Exit code 1 if any file
 * fails a check.
 *
 * Spec (paths relative to the spec file)
 * {
 *  "id": "banner", "layout": "banner|card|featured|carousel",
 *  "title": "Five cash checks for family firms",   (carousel: the document title LinkedIn asks for; warned if missing)
 *  "alt": "Card: 'Check cash weekly' in white on navy",  (alt text for the image, or the whole slide set; card,
 *                                                         featured and carousel warn when there is none)
 *  "brand": {"name": "Ruiz Advisory", "display_font": "Fraunces", "body_font": "Source Sans 3",
 *            "font_files": {"display": [{"src": "../brand/fonts/Fraunces-700.ttf", "weight": 700}], "body": [...]},
 *            "bg": "#0f1424", "fg": "#f4f6fa", "accent": "#f97316", "muted": "#a9b2c6", "logo": "brand/logo.png"},
 *  "photo": "brand/headshot.jpg",            (card and featured only, optional; a real photo, never generated)
 *  "copy": {"promise": "...", "proof": "...", "cta": "...",        (banner)
 *           "kicker": "...", "headline": "...", "sub": "...",      (card; featured: kicker + a 3–5 word headline)
 *           "author": "Dana Ruiz · Fractional CFO",               (card byline, carousel footer)
 *           "swipe": "Swipe"},                                    (carousel hook hint, drawn with an arrow; "" hides it)
 *  "show_sub": false,                         (featured only: true keeps copy.sub, at a larger minimum size)
 *  "slides": [{"kind": "hook", "title": "...", "sub": "...", "swipe": "Swipe"},
 *             {"kind": "point", "title": "...", "body": "...", "alt": "..."},
 *                 (numerals count the point slides from 1: the first point after the hook shows 1; "n": 4 sets
 *                  the numeral shown, "n": "" hides it and that slide is not counted; every slide may carry "alt")
 *             {"kind": "list", "title": "...", "items": ["...", "..."]},
 *             {"kind": "quote", "quote": "...", "who": "..."},
 *             {"kind": "cta", "title": "...", "sub": "..."}],
 *  "draft_label": ""                          (non-empty → a red DRAFT band, for proofs)
 * }
 */
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';

const SIZES = { banner: [1584, 396], card: [1200, 1500], featured: [1200, 627], carousel: [1080, 1350] };
const MIN_PX = { banner: 30, card: 34, featured: 30, carousel: 40 };
// Banner: the round profile photo covers the lower-left on desktop (about the first 28% of the width,
// lower 60% of the height) and sits further in on mobile; keep text in the right 64%, inside 10% top and bottom.
const BANNER_TEXT_ZONE = { left: 0.345, right: 0.975, top: 0.08, bottom: 0.92 };
const LARGE_PX = 40;   // text at or above this is "large" for contrast (3:1); smaller text needs 4.5:1
const BANNER_PHOTO_ZONES = [{ x: 0.02, y: 0.38, w: 0.26, h: 0.62, label: 'desktop photo' }, { x: 0.0, y: 0.5, w: 0.34, h: 0.5, label: 'mobile photo' }];

function loadPlaywright() {
  for (const from of [path.join(process.cwd(), 'noop.js'), fileURLToPath(import.meta.url)]) {
    const req = createRequire(from);
    for (const name of ['playwright', 'playwright-core']) {
      try { return req(name); } catch { /* next */ }
    }
  }
  console.error('Playwright not found. Run: npm i playwright && npx playwright install chromium\n(or npm i playwright-core and set CHROME_PATH to an installed Chrome).');
  process.exit(2);
}

// Chromium puts a Unix socket under TMPDIR; a long TMPDIR passes the 108-byte socket path limit and the
// browser dies on start. Use /tmp (or the OS default) when TMPDIR is long.
function shortTmp() {
  const t = process.env.TMPDIR || process.env.TMP || process.env.TEMP;
  if (process.platform === 'win32' || !t || t.length <= 60) return;
  for (const d of ['/tmp', '/var/tmp']) {
    try { fs.accessSync(d, fs.constants.W_OK); process.env.TMPDIR = d; return; } catch { /* next */ }
  }
}

async function launch(pw) {
  shortTmp();
  const candidates = [process.env.CHROME_PATH, undefined, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/opt/pw-browsers/chromium'];
  let last;
  for (const exe of candidates) {
    if (exe && !fs.existsSync(exe)) continue;
    try { return await pw.chromium.launch(exe ? { executablePath: exe } : {}); } catch (e) { last = e; }
  }
  console.error('Could not start Chromium. Run npx playwright install chromium, or set CHROME_PATH.\n' + (last?.message || ''));
  process.exit(2);
}

const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const fileUrl = (base, p) => p ? pathToFileURL(path.resolve(base, p)).href : '';
function lum(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex || ''); if (!m) return null;
  const n = parseInt(m[1], 16), ch = [n >> 16 & 255, n >> 8 & 255, n & 255].map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; });
  return .2126 * ch[0] + .7152 * ch[1] + .0722 * ch[2];
}
// numerals for point slides: counted over point slides only (from 1), "n" overrides, "" or false hides
function pointNumerals(slides) {
  let k = 0;
  return slides.map(s => {
    if (s.kind !== 'point') return null;
    if (s.n === '' || s.n === false) return '';
    k++;
    return s.n ?? k;
  });
}
// where the accent colour carries text (not just bars)
function accentTextUses(spec, layout) {
  const c = spec.copy || {}, uses = [];
  if (layout === 'banner' && c.cta) uses.push('CTA');
  if ((layout === 'card' || layout === 'featured') && c.kicker) uses.push('kicker');
  if (layout === 'carousel') {
    const slides = spec.slides || [], nums = pointNumerals(slides);
    if (slides.some(s => s.kind === 'hook' && (s.swipe ?? c.swipe ?? 'Swipe'))) uses.push('swipe hint');
    if (nums.some(x => x !== null && x !== '')) uses.push('point numerals');
    if (slides.some(s => s.kind === 'list' && (s.items || []).length)) uses.push('list numbers');
    if (slides.some(s => s.kind === 'quote')) uses.push('quote mark');
    if (slides.some(s => !['hook', 'point', 'list', 'quote'].includes(s.kind) && s.sub)) uses.push('CTA sub-line');
  }
  return uses;
}
const words = t => String(t || '').trim().split(/\s+/).filter(Boolean).length;
const contrast = (a, b) => { const x = lum(a), y = lum(b); if (x == null || y == null) return null; return +(((Math.max(x, y) + .05) / (Math.min(x, y) + .05)).toFixed(2)); };
const onColor = bg => (contrast('#111111', bg) ?? 0) >= (contrast('#ffffff', bg) ?? 0) ? '#111111' : '#ffffff';

function fontCss(brand, base) {
  const local = brand.font_files || {};
  const faces = (fam, v) => (Array.isArray(v) ? v : v ? [{ src: v }] : [])
    .map(f => `@font-face{font-family:"${fam}";src:url("${fileUrl(base, f.src)}");font-weight:${f.weight || '100 900'};font-display:block}`).join('');
  const css = faces(brand.display_font, local.display) + faces(brand.body_font, local.body);
  const remote = [[brand.display_font, local.display], [brand.body_font, local.body]].filter(([f, l]) => f && !l).map(([f]) => f);
  const link = remote.length ? `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?${[...new Set(remote)].map(f => 'family=' + encodeURIComponent(f).replace(/%20/g, '+') + ':wght@400;600;700;800').join('&')}&display=block">` : '';
  return { css, link };
}

function page(spec, base, W, H, inner) {
  const b = spec.brand || {};
  const bg = b.bg || '#0f1424', fg = b.fg || onColor(bg), accent = b.accent || '#f97316', muted = b.muted || fg;
  const { css, link } = fontCss(b, base);
  const df = `"${b.display_font || 'Georgia'}", Georgia, serif`, bf = `"${b.body_font || 'Helvetica'}", Helvetica, Arial, sans-serif`;
  return `<!doctype html><html><head><meta charset="utf-8">${link}<style>${css}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:${W}px;height:${H}px;overflow:hidden;background:${bg}}
.f{position:absolute;inset:0;background:${bg};color:${fg};font-family:${bf}}
.d{font-family:${df};font-weight:700;letter-spacing:-.01em;line-height:1.08;text-wrap:balance}
.acc{color:${accent}} .mut{color:${muted}}
.bar{position:absolute;background:${accent}}
.draft{position:absolute;left:0;right:0;top:0;height:${Math.round(H * .06)}px;background:#dc2626;color:#fff;font:700 ${Math.max(16, Math.round(H * .025))}px/${Math.round(H * .06)}px ${bf};text-align:center;letter-spacing:.08em;z-index:9}
[data-fit]{overflow-wrap:break-word}
.swipe{display:inline-flex;align-items:center;gap:18px}
.swipe svg{width:1.4em;height:.8em;flex:none}
</style></head><body><div class="f">${inner}${spec.draft_label ? `<div class="draft">${esc(spec.draft_label)}</div>` : ''}</div></body></html>`;
}

function bannerHtml(spec, base) {
  const [W, H] = SIZES.banner, c = spec.copy || {}, z = BANNER_TEXT_ZONE, b = spec.brand || {};
  const logo = b.logo ? `<img src="${fileUrl(base, b.logo)}" style="height:${Math.round(H * .13)}px;margin-bottom:${Math.round(H * .04)}px">` : '';
  return page(spec, base, W, H, `
  <div class="bar" style="left:${Math.round(W * z.left)}px;top:${Math.round(H * .22)}px;width:6px;height:${Math.round(H * .56)}px"></div>
  <div data-box style="position:absolute;left:${Math.round(W * z.left) + 28}px;right:${Math.round(W * (1 - z.right))}px;top:${Math.round(H * z.top)}px;bottom:${Math.round(H * (1 - z.bottom))}px;display:flex;flex-direction:column;justify-content:center">
    ${logo}
    <div class="d" data-t="promise" data-fit="78,40">${esc(c.promise)}</div>
    ${c.proof ? `<div class="mut" data-t="proof" data-fit="36,${MIN_PX.banner}" style="margin-top:${Math.round(H * .05)}px;font-weight:600">${esc(c.proof)}</div>` : ''}
    ${c.cta ? `<div class="acc" data-t="cta" data-fit="34,${MIN_PX.banner}" style="margin-top:${Math.round(H * .04)}px;font-weight:700">${esc(c.cta)}</div>` : ''}
  </div>`);
}

function cardHtml(spec, base, layout) {
  const [W, H] = SIZES[layout], c = spec.copy || {}, pad = Math.round(W * .08), b = spec.brand || {}, min = MIN_PX[layout];
  const featured = layout === 'featured';
  const photo = spec.photo ? `<div style="position:absolute;right:${pad}px;bottom:${pad}px;width:${Math.round(W * (layout === 'card' ? .28 : .22))}px;aspect-ratio:1;border-radius:50%;overflow:hidden;border:6px solid ${b.accent || '#f97316'}"><img src="${fileUrl(base, spec.photo)}" style="width:100%;height:100%;object-fit:cover"></div>` : '';
  // Featured thumbnails display small on the profile: kicker and a short title only, unless show_sub is set.
  const big = featured ? '96,60' : '110,52';
  const sub = c.sub && (!featured || spec.show_sub === true)
    ? `<div class="mut" data-t="sub" data-fit="${featured ? '50,44' : `42,${min}`}" style="margin-top:28px;line-height:1.3">${esc(c.sub)}</div>` : '';
  const author = c.author ? `<div class="mut" data-t="author" data-fit="${min},${min}" style="margin-top:24px;font-weight:600">${esc(c.author)}</div>` : '';
  return page(spec, base, W, H, `
  <div class="bar" style="left:${pad}px;top:${pad}px;width:${Math.round(W * .1)}px;height:8px"></div>
  <div data-box style="position:absolute;left:${pad}px;right:${pad}px;top:${pad + 40}px;bottom:${spec.photo ? Math.round(H * (layout === 'card' ? .3 : .12)) + pad : Math.round(pad * .7)}px;display:flex;flex-direction:column">
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center">
    ${c.kicker ? `<div class="acc" data-t="kicker" data-fit="${featured ? `36,${min}` : `40,${min}`}" style="font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin-bottom:24px">${esc(c.kicker)}</div>` : ''}
    <div class="d" data-t="headline" data-fit="${big}">${esc(c.headline)}</div>
    ${sub}
    </div>${author}
  </div>${photo}`);
}

function slideHtml(spec, base, s, i, n, numeral) {
  const [W, H] = SIZES.carousel, pad = Math.round(W * .085), c = spec.copy || {};
  let body = '';
  if (s.kind === 'hook') {
    // the swipe hint is spec copy (any language); the arrow is drawn, so no glyph can fall back to a system font
    const swipe = s.swipe ?? c.swipe ?? 'Swipe';
    const arrow = '<svg viewBox="0 0 56 32" aria-hidden="true"><path d="M2 16h48M36 3l15 13-15 13" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    body = `<div class="d" data-t="s${i}.title" data-fit="124,64">${esc(s.title)}</div>${s.sub ? `<div class="mut" data-t="s${i}.sub" data-fit="54,40" style="margin-top:40px;line-height:1.3">${esc(s.sub)}</div>` : ''}${swipe ? `<div class="acc swipe" data-t="s${i}.swipe" style="margin-top:64px;font-size:42px;font-weight:700"><span>${esc(swipe)}</span>${arrow}</div>` : ''}`;
  } else if (s.kind === 'point') {
    const num = numeral ?? '';
    body = `${num !== '' ? `<div class="acc d" style="font-size:120px;line-height:1;margin-bottom:28px">${esc(num)}</div>` : ''}<div class="d" data-t="s${i}.title" data-fit="84,52">${esc(s.title)}</div>${s.body ? `<div data-t="s${i}.body" data-fit="52,40" style="margin-top:32px;line-height:1.4">${esc(s.body)}</div>` : ''}`;
  } else if (s.kind === 'list') {
    body = `<div class="d" data-t="s${i}.title" data-fit="76,50" style="margin-bottom:48px">${esc(s.title)}</div>${(s.items || []).map((it, k) => `<div data-t="s${i}.item${k}" data-fit="54,40" style="display:flex;gap:26px;margin-bottom:32px;line-height:1.25"><span class="acc" style="font-weight:800">${k + 1}</span><span>${esc(it)}</span></div>`).join('')}`;
  } else if (s.kind === 'quote') {
    body = `<div class="acc d" style="font-size:150px;line-height:.6;margin-bottom:10px">“</div><div class="d" data-t="s${i}.quote" data-fit="76,50" style="font-weight:600">${esc(s.quote)}</div><div class="mut" data-t="s${i}.who" style="margin-top:40px;font-size:40px">${esc(s.who)}</div>`;
  } else {
    body = `<div class="d" data-t="s${i}.title" data-fit="96,56">${esc(s.title)}</div>${s.sub ? `<div class="acc" data-t="s${i}.sub" data-fit="54,40" style="margin-top:40px;font-weight:700;line-height:1.3">${esc(s.sub)}</div>` : ''}`;
  }
  return page(spec, base, W, H, `
  <div class="bar" style="left:${pad}px;top:${pad}px;width:96px;height:8px"></div>
  <div data-box style="position:absolute;left:${pad}px;right:${pad}px;top:${pad + 60}px;bottom:${pad + 80}px;display:flex;flex-direction:column;justify-content:${s.kind === 'point' || s.kind === 'list' ? 'flex-start' : 'center'}">${body}</div>
  <div class="mut" style="position:absolute;left:${pad}px;right:${pad}px;bottom:${Math.round(pad * .75)}px;display:flex;justify-content:space-between;font-size:32px;font-weight:600">
    <span data-t="author">${esc(c.author || (spec.brand || {}).name || '')}</span><span>${i} / ${n}</span></div>`);
}

// Pages are loaded from a temporary file next to the output, so file:// brand fonts are allowed to load.
async function load(pg, html, outDir) {
  const tmp = path.join(outDir, `.render-${process.pid}.html`);
  fs.writeFileSync(tmp, html);
  await pg.goto(pathToFileURL(path.resolve(tmp)).href, { waitUntil: 'load', timeout: 30000 }).catch(() => {});
  await pg.evaluate(() => document.fonts.ready);
  fs.rmSync(tmp, { force: true });
}

async function fitAndCheck(pg, W, H, minPx, layout, families) {
  return pg.evaluate(({ W, H, minPx, layout, zone, photos, families }) => {
    const overflow = [], small = [], outside = [], under = [], text = {};
    // Fit each text block as a whole: measure from the top (centred content hides overflow), then shrink
    // the element that is largest relative to its own maximum, two pixels at a time, until the block fits.
    const boxes = new Map();
    for (const el of document.querySelectorAll('[data-fit]')) {
      const [max, min0] = el.dataset.fit.split(',').map(Number);
      el._max = max; el._min = Math.max(min0, minPx); el._size = max; el.style.fontSize = max + 'px';
      const box = el.closest('[data-box]') || el.parentElement;
      if (!boxes.has(box)) boxes.set(box, []);
      boxes.get(box).push(el);
    }
    for (const [box, els] of boxes) {
      const jc = box.style.justifyContent; box.style.justifyContent = 'flex-start';
      const fits = () => box.scrollHeight <= box.clientHeight + 1 && els.every(e => e.scrollWidth <= e.clientWidth + 1);
      for (let n = 0; n < 400 && !fits(); n++) {
        const cand = els.filter(e => e._size > e._min).sort((x, y) => y._size / y._max - x._size / x._max)[0];
        if (!cand) break;
        cand._size -= 2; cand.style.fontSize = cand._size + 'px';
      }
      if (!fits()) overflow.push(...els.map(e => e.dataset.t));
      box.style.justifyContent = jc;
      for (const e of els) if (e._size <= e._min && e._size < e._max) small.push(e.dataset.t);
    }
    for (const el of document.querySelectorAll('[data-t]')) {
      text[el.dataset.t] = el.textContent.trim();
      const r = el.getBoundingClientRect();
      if (r.width === 0) continue;
      if (layout === 'banner') {
        if (r.left < W * zone.left - 2 || r.right > W * zone.right + 2 || r.top < H * zone.top - 2 || r.bottom > H * zone.bottom + 2) outside.push(el.dataset.t);
        for (const p of photos) {
          const px = { l: W * p.x, t: H * p.y, r: W * (p.x + p.w), b: H * (p.y + p.h) };
          if (r.left < px.r && r.right > px.l && r.top < px.b && r.bottom > px.t) under.push(`${el.dataset.t} under the ${p.label}`);
        }
      } else if (r.right > W || r.bottom > H || r.left < 0 || r.top < 0) outside.push(el.dataset.t);
    }
    // Every declared brand family must have actually loaded: a loaded FontFace with no face in error,
    // or (a font installed on this computer) text that measures differently from the generic fallbacks.
    const unq = f => f.replace(/^["']|["']$/g, '');
    const faces = [...document.fonts];
    const cv = document.createElement('canvas').getContext('2d');
    const width = font => { cv.font = font; return cv.measureText('Hamburgefonstiv 0123456789 WMQ').width; };
    const installed = fam => ['monospace', 'serif', 'sans-serif'].some(g => width(`72px "${fam}", ${g}`) !== width(`72px ${g}`));
    const missing = [];
    for (const { family, local } of families) {
      const mine = faces.filter(f => unq(f.family) === family);
      const errored = mine.filter(f => f.status === 'error').length;
      const loaded = mine.some(f => f.status === 'loaded');
      if (local ? (errored || !loaded) : !(loaded || installed(family))) missing.push(family + (errored ? ` (${errored} file(s) failed)` : ''));
    }
    return { overflow, small, outside, under, text, missingFonts: missing };
  }, { W, H, minPx, layout, zone: BANNER_TEXT_ZONE, photos: BANNER_PHOTO_ZONES, families });
}

async function renderOne(browser, specPath, outDir, overlay) {
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const base = path.dirname(path.resolve(specPath));
  const layout = spec.layout, id = spec.id || path.basename(specPath, '.json');
  if (!SIZES[layout]) throw new Error(`${specPath}: layout must be one of ${Object.keys(SIZES).join(', ')}`);
  const [W, H] = SIZES[layout];
  const scale = layout === 'banner' ? 2 : 1;
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: scale });
  const pg = await ctx.newPage();
  const b = spec.brand || {}, bg = b.bg || '#0f1424', fg = b.fg || onColor(bg);
  const report = { id, layout, size: [W, H], title: spec.title ?? null, alt: spec.alt ?? null, files: [], checks: [], warnings: [] };
  const fail = (what) => report.checks.push({ check: what, result: 'FAIL' });
  const cr = contrast(fg, bg);
  report.checks.push({ check: 'text contrast ≥ 4.5', result: cr == null || cr >= 4.5 ? 'pass' : 'FAIL', detail: cr });
  // accent carries the kicker, CTA, numerals and hints; muted carries proof, subs and bylines
  const accentUses = accentTextUses(spec, layout);
  for (const [name, col] of [['accent', b.accent || '#f97316'], ['muted', b.muted]]) {
    const r = col ? contrast(col, bg) : null;
    if (r == null) continue;
    const fails = name === 'accent' && r < 3 && accentUses.length > 0;
    report.checks.push({ check: `${name} contrast` + (name === 'accent' && accentUses.length ? ` ≥ 3 (accent carries the ${accentUses.join(', ')})` : ''),
      result: fails ? 'FAIL' : 'pass', detail: r });
    if (fails) report.warnings.push(`accent ${col} on ${bg} is ${r}:1, below 3:1, and the accent carries text (${accentUses.join(', ')}): pick a stronger accent`);
    else if (r < 3) report.warnings.push(`${name} ${col} on ${bg} is ${r}:1, below 3:1 even for large text: pick a stronger ${name}`);
    else if (r < 4.5) report.warnings.push(`${name} ${col} on ${bg} is ${r}:1: fine for large text (${LARGE_PX}px+), below 4.5:1 for small text such as the ${name === 'accent' ? 'kicker and CTA' : 'sub-lines and byline'}`);
  }
  const families = [[b.display_font, (b.font_files || {}).display], [b.body_font, (b.font_files || {}).body]]
    .filter(([f]) => f).map(([family, files]) => ({ family, local: !!(Array.isArray(files) ? files.length : files) }))
    .filter((x, k, all) => all.findIndex(y => y.family === x.family) === k);
  if (layout === 'featured') {
    const n = words((spec.copy || {}).headline);
    if (n > 6) report.warnings.push(`featured headline is ${n} words; thumbnails display small, so 3 to 5 words read best`);
    if ((spec.copy || {}).sub && spec.show_sub !== true) report.warnings.push('featured: the sub-line is left off (unreadable at thumbnail size); set "show_sub": true to keep it');
  }
  if (layout === 'card' && words((spec.copy || {}).headline) > 20) report.warnings.push(`card headline is ${words((spec.copy || {}).headline)} words; over about 20 reads as a paragraph: cut it, and move the rest to the sub-line or the post`);
  const slides = layout === 'carousel' ? (spec.slides || []) : [];
  const numerals = pointNumerals(slides);
  slides.forEach((s, i) => {
    const n = words(s.title);
    if (n > 20) report.warnings.push(`slide ${i + 1}: headline is ${n} words; over about 20 is hard to read on a phone: cut it, or split the slide`);
  });
  if (layout === 'carousel') {
    report.slides = slides.map((s, i) => ({ n: i + 1, kind: s.kind, numeral: numerals[i] === null || numerals[i] === '' ? null : numerals[i], alt: s.alt ?? null }));
    if (!String(spec.title || '').trim()) report.warnings.push('no "title": LinkedIn asks for a document title when the PDF is uploaded; add "title" to the spec');
    if (!String(spec.alt || '').trim() && slides.some(s => !String(s.alt || '').trim())) report.warnings.push('no alt text: add "alt" for the slide set, or "alt" on every slide');
  } else if ((layout === 'card' || layout === 'featured') && !String(spec.alt || '').trim()) {
    report.warnings.push('no alt text: add "alt" to the spec (what the image says and shows), to paste in when uploading');
  }
  const frames = layout === 'carousel' ? slides.map((s, i, a) => slideHtml(spec, base, s, i + 1, a.length, numerals[i]))
    : [layout === 'banner' ? bannerHtml(spec, base) : cardHtml(spec, base, layout)];
  if (layout === 'carousel' && (frames.length < 3 || frames.length > 12)) report.warnings.push(`${frames.length} slides; 5 to 10 is the usual range (LinkedIn accepts up to 300 pages)`);
  const pdfPages = [];
  for (let i = 0; i < frames.length; i++) {
    await load(pg, frames[i], outDir);
    const res = await fitAndCheck(pg, W, H, MIN_PX[layout], layout, families);
    const tag = layout === 'carousel' ? `slide ${i + 1}: ` : '';
    if (res.overflow.length) fail(`${tag}text fits (${res.overflow.join(', ')})`);
    if (res.outside.length) fail(`${tag}text inside the safe area (${res.outside.join(', ')})`);
    if (res.under.length) fail(`${tag}nothing under the profile photo (${res.under.join(', ')})`);
    if (res.small.length) report.warnings.push(`${tag}at minimum size: ${res.small.join(', ')} (consider shorter copy)`);
    if (res.missingFonts.length) fail(`${tag}brand fonts loaded (${res.missingFonts.join(', ')} did not load and a fallback was used: check the font_files paths, or that the Google font name is exact and the computer is online)`);
    for (const [k, v] of Object.entries(res.text)) if (/['"]/.test(v)) report.warnings.push(`${tag}straight quote marks in ${k}: use ’ “ ”`);
    const png = path.join(outDir, layout === 'carousel' ? `${id}_${String(i + 1).padStart(2, '0')}.png` : `${id}.png`);
    await pg.screenshot({ path: png });
    report.files.push(path.basename(png));
    if (layout === 'carousel') pdfPages.push(await pg.content());
    if (overlay && layout === 'banner') {
      await pg.evaluate(({ W, H, zone, photos }) => {
        // the label sits just outside its zone (above it), so it never covers the copy being checked
        const mk = (l, t, w, h, col, txt) => {
          const d = document.createElement('div'); Object.assign(d.style, { position: 'absolute', left: l + 'px', top: t + 'px', width: w + 'px', height: h + 'px', border: `4px dashed ${col}`, zIndex: 99 });
          const s = document.createElement('span'); Object.assign(s.style, { position: 'absolute', left: '-4px', bottom: '100%', marginBottom: '2px', color: col, font: '700 18px/1 sans-serif', whiteSpace: 'nowrap' });
          s.textContent = txt; d.appendChild(s); document.body.appendChild(d);
        };
        mk(W * zone.left, H * zone.top, W * (zone.right - zone.left), H * (zone.bottom - zone.top), '#22d3ee', 'text zone');
        for (const p of photos) mk(W * p.x, H * p.y, W * p.w, H * p.h, '#f43f5e', p.label);
      }, { W, H, zone: BANNER_TEXT_ZONE, photos: BANNER_PHOTO_ZONES });
      const safe = path.join(outDir, `${id}_safe.png`);
      await pg.screenshot({ path: safe }); report.files.push(path.basename(safe));
    }
  }
  if (layout === 'carousel' && pdfPages.length) {
    const all = pdfPages.map(h => h.replace(/^[\s\S]*<body>/, '').replace(/<\/body>[\s\S]*$/, '')).map(b2 => `<div style="position:relative;width:${W}px;height:${H}px;overflow:hidden;page-break-after:always">${b2}</div>`).join('');
    const head = pdfPages[0].match(/<head>[\s\S]*<\/head>/)[0].replace(/html,body\{[^}]*\}/, `html,body{width:${W}px;background:${bg}}`);
    await load(pg, `<!doctype html><html>${head}<body>${all}</body></html>`, outDir);
    const pdf = path.join(outDir, `${id}.pdf`);
    await pg.pdf({ path: pdf, width: `${W}px`, height: `${H}px`, printBackground: true, pageRanges: '' });
    report.files.push(path.basename(pdf));
    report.pages = pdfPages.length;
  }
  await ctx.close();
  report.result = report.checks.some(c => c.result === 'FAIL') ? 'FAIL' : 'PASS';
  fs.writeFileSync(path.join(outDir, `${id}.report.json`), JSON.stringify(report, null, 1));
  return report;
}

async function main() {
  const args = process.argv.slice(2);
  const outIdx = args.indexOf('--out');
  const outDir = outIdx >= 0 ? args[outIdx + 1] : 'renders';
  const overlay = args.includes('--overlay');
  const specs = args.filter((a, i) => a.endsWith('.json') && i !== outIdx + 1);
  if (!specs.length) { console.error('usage: node render_linkedin.mjs spec.json [...] --out dir [--overlay]'); process.exit(2); }
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await launch(loadPlaywright());
  let bad = 0;
  for (const s of specs) {
    const r = await renderOne(browser, s, outDir, overlay);
    console.log(`${r.result}  ${r.id} (${r.layout}) → ${r.files.join(', ')}${r.checks.filter(c => c.result === 'FAIL').map(c => '\n   FAIL ' + c.check).join('')}${r.warnings.map(w => '\n   note ' + w).join('')}`);
    if (r.result === 'FAIL') bad++;
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
}

main().catch(e => { console.error(e.message || e); process.exit(2); });
