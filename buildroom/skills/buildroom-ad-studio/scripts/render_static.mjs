#!/usr/bin/env node
/*
 * Ad Studio static renderer: real photo or generated plate + real fonts + exact approved copy
 * + brand kit, recomposed for 1:1, 4:5 and 9:16, with overflow, safe-zone and contrast checks.
 * The image model never sets a word; this does.
 *
 * Usage
 *   node render_static.mjs specs/C1-H1.json [more specs...] --out renders/ [--overlay] [--ratios 1x1,4x5,9x16]
 *
 * Needs Playwright (npm i playwright in the ads folder, then npx playwright install chromium),
 * or CHROME_PATH pointing at an installed Chrome, Edge or Chromium.
 *
 * Writes renders/<id>_<ratio>.png per ratio, renders/<id>_<ratio>_safe.png with --overlay
 * (the safe zone drawn, for the reviewer), and renders/<id>.report.json with every check.
 * Exit code 1 if any file fails a check.
 *
 * Spec (paths relative to the spec file):
 * {
 *  "id": "C1-H1", "concept": "C1", "layout": "photo-hook",
 *  "brand": {"name": "Acme Bookkeeping", "logo": "brand/logo.png",
 *            "display_font": "Fraunces", "body_font": "Inter", "font_files": {"display": "brand/Display.woff2"},
 *            "bg": "#0f1424", "fg": "#f4f6fa", "accent": "#f97316", "muted": "#a9b2c6", "paper": "#fffdf6"},
 *  "picture": {"src": "plates/C1.png", "kind": "plate|photo|deliverable", "focus": "50% 40%"},
 *  "inset": {"src": "vault/founder.jpg", "caption": "[first name], owner"},
 *  "copy": {"hook": "...", "sub": "...", "bullets": [], "quote": "", "attribution": "", "source": "",
 *           "rating": "", "number": "", "label": "", "title": "", "lines": [], "left_label": "", "right_label": "",
 *           "rows": [["old way", "this way"]], "offer": "", "price": "", "terms": "", "question": "",
 *           "options": [], "cta": "Book the 20-minute call"},
 *  "ai_label": false,
 *  "draft_label": ""
 * }
 */
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';

const RATIOS = { '1x1': [1080, 1080], '4x5': [1080, 1350], '9x16': [1080, 1920] };
// Fractions of the canvas kept clear of platform UI. 9:16 follows the Reels overlay (14% top,
// 35% bottom, 6% sides), the strictest placement; verify against Meta's current guide.
const SAFE = { '1x1': { t: .055, b: .055, s: .055 }, '4x5': { t: .05, b: .05, s: .055 }, '9x16': { t: .14, b: .35, s: .06 } };
const LAYOUTS = ['photo-hook', 'split', 'quote-card', 'stat', 'notes', 'us-vs-them', 'offer-card', 'quiz'];
const AI_LABEL = 'Includes AI-generated imagery';

function loadPlaywright() {
  const tries = [path.join(process.cwd(), 'noop.js'), fileURLToPath(import.meta.url)];
  for (const from of tries) {
    const req = createRequire(from);
    for (const name of ['playwright', 'playwright-core']) {
      try { return req(name); } catch { /* next */ }
    }
  }
  console.error('Playwright not found. In the ads folder run: npm i playwright && npx playwright install chromium\n(or npm i playwright-core and set CHROME_PATH to an installed Chrome).');
  process.exit(2);
}

async function launch(pw) {
  const candidates = [process.env.CHROME_PATH, undefined,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
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
const contrast = (a, b) => { const x = lum(a), y = lum(b); if (x == null || y == null) return null; return +(((Math.max(x, y) + .05) / (Math.min(x, y) + .05)).toFixed(2)); };
const onColor = bg => (contrast('#111111', bg) ?? 0) >= (contrast('#ffffff', bg) ?? 0) ? '#111111' : '#ffffff';
const rgba = (hex, a) => { const n = parseInt(hex.replace('#', ''), 16); return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`; };

function fontCss(brand, base) {
  // font_files: {"display": "file.woff2" | [{"src": "file.ttf", "weight": 700}], "body": [...]}
  const local = brand.font_files || {};
  const faces = (fam, v) => (Array.isArray(v) ? v : v ? [{ src: v }] : [])
    .map(f => `@font-face{font-family:"${fam}";src:url("${fileUrl(base, f.src)}");font-weight:${f.weight || '100 900'};font-style:${f.style || 'normal'};font-display:block}`).join('');
  const css = faces(brand.display_font, local.display) + faces(brand.body_font, local.body);
  const remote = [[brand.display_font, local.display], [brand.body_font, local.body]].filter(([f, l]) => f && !l).map(([f]) => f);
  const link = remote.length ? `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?${[...new Set(remote)].map(f => 'family=' + encodeURIComponent(f).replace(/%20/g, '+') + ':wght@400;600;700;800').join('&')}&display=block">` : '';
  return { css, link };
}

function brandMark(brand, base) {
  return brand.logo
    ? `<img class="logo" data-t="brand" src="${fileUrl(base, brand.logo)}" alt="${esc(brand.name)}">`
    : `<div class="bname" data-t="brand"><i></i>${esc(brand.name)}</div>`;
}
const cta = c => c.cta ? `<div class="cta" data-t="cta">${esc(c.cta)}<span aria-hidden="true"> →</span></div>` : '';
const list = (items, cls, mark) => (items || []).map((t, i) => `<li class="${cls}" data-t="${cls}${i + 1}" data-fit="42,30"><b aria-hidden="true">${mark}</b><span>${esc(t)}</span></li>`).join('');

function body(spec, base, ratio) {
  const c = spec.copy || {}, b = spec.brand, L = spec.layout;
  const inset = spec.inset?.src ? `<figure class="inset"><img src="${fileUrl(base, spec.inset.src)}" alt="">${spec.inset.caption ? `<figcaption data-t="inset_caption">${esc(spec.inset.caption)}</figcaption>` : ''}</figure>` : '';
  const head = `<header>${brandMark(b, base)}</header>`;
  const foot = (extra = '') => `<footer>${cta(c)}${extra}</footer>`;
  switch (L) {
    case 'photo-hook': return `${head}<main><h1 data-t="hook" data-fit="104,52">${esc(c.hook)}</h1>${c.sub ? `<p class="sub" data-t="sub" data-fit="42,30">${esc(c.sub)}</p>` : ''}</main>${foot(inset)}`;
    case 'split': return `${head}<main><h1 data-t="hook" data-fit="86,44">${esc(c.hook)}</h1><ul class="bul">${list(c.bullets, 'b', '✓')}</ul></main>${foot()}`;
    case 'quote-card': return `${head}<main>${inset}<div class="qm" aria-hidden="true">“</div><blockquote data-t="quote" data-fit="74,34">${esc(c.quote)}</blockquote><p class="attr" data-t="attribution" data-fit="36,30">${esc(c.attribution)}</p>${c.rating ? `<p class="rating" data-t="rating">${esc(c.rating)}</p>` : ''}${c.source ? `<p class="src" data-t="source">${esc(c.source)}</p>` : ''}</main>${foot()}`;
    case 'stat': return `${head}<main><div class="num" data-t="number" data-fit="330,120">${esc(c.number)}</div><h2 data-t="label" data-fit="76,36">${esc(c.label)}</h2>${c.sub ? `<p class="sub" data-t="sub" data-fit="36,30">${esc(c.sub)}</p>` : ''}${c.source ? `<p class="src" data-t="source">${esc(c.source)}</p>` : ''}</main>${foot()}`;
    case 'notes': return `<main><div class="paper"><h1 data-t="title" data-fit="74,38">${esc(c.title)}</h1><ul class="lines">${(c.lines || []).map((l, i) => { const o = typeof l === 'string' ? { text: l } : l; return `<li data-t="line${i + 1}" data-fit="46,30"><b aria-hidden="true">${o.done ? '✓' : '•'}</b><span>${esc(o.text)}</span></li>`; }).join('')}</ul></div></main>${foot(`<div class="sig">${brandMark(b, base)}</div>`)}`;
    case 'us-vs-them': return `${head}<main><h1 data-t="hook" data-fit="80,40">${esc(c.hook)}</h1><table class="vs"><thead><tr><th data-t="left_label">${esc(c.left_label)}</th><th data-t="right_label">${esc(c.right_label)}</th></tr></thead><tbody>${(c.rows || []).map((r, i) => `<tr><td data-t="row${i + 1}_left" data-fit="38,30"><div class="cell"><b aria-hidden="true">✕</b><span>${esc(r[0])}</span></div></td><td data-t="row${i + 1}_right" data-fit="38,30"><div class="cell"><b aria-hidden="true">✓</b><span>${esc(r[1])}</span></div></td></tr>`).join('')}</tbody></table></main>${foot()}`;
    case 'offer-card': return `${head}<main><h1 data-t="offer" data-fit="84,42">${esc(c.offer || c.hook)}</h1>${c.sub ? `<p class="sub" data-t="sub" data-fit="36,30">${esc(c.sub)}</p>` : ''}<ul class="bul">${list(c.bullets, 'b', '✓')}</ul>${c.price ? `<div class="price" data-t="price">${esc(c.price)}</div>` : ''}${c.terms ? `<p class="src" data-t="terms">${esc(c.terms)}</p>` : ''}</main>${foot()}`;
    case 'quiz': return `${head}<main><h1 data-t="question" data-fit="92,42">${esc(c.question)}</h1><ol class="opts">${(c.options || []).map((o, i) => `<li data-t="option${i + 1}" data-fit="44,30"><b aria-hidden="true">${'ABCDEF'[i]}</b><span>${esc(o)}</span></li>`).join('')}</ol>${c.sub ? `<p class="sub" data-t="sub" data-fit="34,30">${esc(c.sub)}</p>` : ''}</main>${foot()}`;
  }
  throw new Error(`unknown layout ${L}; use one of ${LAYOUTS.join(', ')}`);
}

function html(spec, base, ratio) {
  const [W, H] = RATIOS[ratio], s = SAFE[ratio], b = spec.brand;
  const fg = b.fg || '#f4f6fa', bg = b.bg || '#0f1424', accent = b.accent || '#f97316', muted = b.muted || '#a9b2c6', paper = b.paper || '#fffdf6';
  const safe = { top: Math.round(H * s.t), bottom: Math.round(H * s.b), side: Math.round(W * s.s) };
  const tall = ratio === '9x16', L = spec.layout;
  const pic = spec.picture?.src ? fileUrl(base, spec.picture.src) : '';
  const fonts = fontCss(b, base);
  const df = `"${b.display_font || 'Georgia'}", Georgia, "Times New Roman", serif`;
  const bf = `"${b.body_font || 'Helvetica Neue'}", "Helvetica Neue", Arial, sans-serif`;
  // where the picture sits, per layout and ratio
  let picBox = '', safeOverride = '';
  if (pic) {
    if (L === 'split' && !tall) { picBox = `left:0;top:0;bottom:0;width:44%`; safeOverride = `left:${Math.round(W * .44) + 48}px;`; }
    else if (L === 'split' && tall) { picBox = `left:0;top:0;right:0;height:${Math.round(H * .3)}px`; safeOverride = `top:${Math.round(H * .3) + 36}px;`; }
    else if (L === 'offer-card') { picBox = `left:0;top:0;right:0;height:${Math.round(H * (tall ? .3 : .34))}px`; safeOverride = `top:${Math.round(H * (tall ? .3 : .34)) + 36}px;`; }
    else picBox = 'inset:0';
  }
  // photo-hook: dark at the top where the words sit, clear through the middle so the picture reads,
  // dark again at the bottom under the CTA. Card layouts over a plate: a near-solid veil.
  const sc = tall ? [0, 44, 60, 74, 100] : [0, 50, 64, 80, 100];
  const scrim = !pic ? '' : L === 'photo-hook'
    ? `<div class="scrim" style="background:linear-gradient(180deg, ${rgba(bg, .9)} ${sc[0]}%, ${rgba(bg, .82)} ${sc[1]}%, ${rgba(bg, .25)} ${sc[2]}%, ${rgba(bg, .2)} ${sc[3]}%, ${rgba(bg, .78)} ${sc[4]}%)"></div>`
    : (L === 'stat' || L === 'quiz' || L === 'quote-card') ? `<div class="scrim" style="background:${rgba(bg, .88)}"></div>` : '';
  return `<!doctype html><html><head><meta charset="utf-8">${fonts.link}<style>
${fonts.css}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:${W}px;height:${H}px;overflow:hidden;background:${bg}}
#ad{position:relative;width:${W}px;height:${H}px;overflow:hidden;background:${L === 'notes' ? accent : bg};color:${fg};font-family:${bf};-webkit-font-smoothing:antialiased}
.pic{position:absolute;${picBox}}
.pic img{width:100%;height:100%;object-fit:cover;object-position:${spec.picture?.focus || '50% 50%'};display:block}
.scrim{position:absolute;inset:0}
.deco{position:absolute;right:-${Math.round(W * .26)}px;bottom:-${Math.round(W * .26)}px;width:${Math.round(W * .52)}px;height:${Math.round(W * .52)}px;border-radius:50%;border:${Math.round(W * .014)}px solid ${accent};opacity:.32}
.safe{position:absolute;top:${safe.top}px;bottom:${safe.bottom}px;left:${safe.side}px;right:${safe.side}px;${safeOverride}display:flex;flex-direction:column;gap:${tall ? 30 : 26}px;overflow:hidden}
header{flex:none;display:flex;align-items:center}
main{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;gap:${tall ? 28 : 22}px;overflow:hidden}
footer{flex:none;display:flex;align-items:flex-end;justify-content:space-between;gap:24px}
.logo{height:64px;width:auto;max-width:60%;object-fit:contain}
.bname{font-family:${df};font-weight:700;font-size:34px;letter-spacing:.01em;display:flex;align-items:center;gap:12px}
.bname i{width:16px;height:16px;border-radius:50%;background:${accent};display:inline-block}
h1,h2,.num,blockquote{font-family:${df};font-weight:700;line-height:1.04;text-wrap:balance;letter-spacing:-.01em}
h1{font-size:96px}
h2{font-size:60px;line-height:1.08}
.sub{font-size:40px;line-height:1.28;color:${fg};opacity:.92;text-wrap:pretty}
.src{font-size:24px;line-height:1.35;color:${muted}}
.cta{background:${accent};color:${onColor(accent)};font-weight:700;font-size:36px;line-height:1;padding:24px 34px;border-radius:18px;white-space:nowrap;flex:none}
.inset{flex:none;display:flex;flex-direction:column;align-items:center;gap:10px}
.inset img{width:${tall ? 240 : 210}px;height:${tall ? 240 : 210}px;border-radius:50%;object-fit:cover;border:8px solid ${accent}}
.inset figcaption{font-size:24px;color:${fg};font-weight:600;text-align:center;max-width:280px}
.bul{list-style:none;display:flex;flex-direction:column;gap:18px}
.bul li,.opts li{display:flex;gap:18px;align-items:flex-start;font-size:42px;line-height:1.22}
.bul b{color:${accent};flex:none;width:1em}
.L-split h1{font-size:86px}
.L-quote-card main,.L-stat main,.L-quiz main,.L-us-vs-them main{justify-content:center}
.L-offer-card main{justify-content:space-evenly}
.qm{font-family:${df};font-size:200px;line-height:.6;color:${accent};height:90px}
blockquote{font-size:58px;line-height:1.16;font-weight:600}
.attr{font-size:34px;font-weight:700}
.rating{font-size:30px;color:${accent};font-weight:700}
.L-quote-card main .inset{flex-direction:row;align-self:flex-start}
.L-quote-card main .inset img{width:150px;height:150px;border-width:6px}
.num{font-size:250px;line-height:.9;color:${accent}}
.paper{background:${paper};color:#1d1d1f;border-radius:28px;padding:${tall ? 56 : 52}px ${tall ? 54 : 56}px;flex:1;min-height:0;display:flex;flex-direction:column;gap:${tall ? 32 : 24}px;box-shadow:0 18px 40px rgba(0,0,0,.18);overflow:hidden}
.paper h1{font-family:${bf};font-size:62px;font-weight:800;letter-spacing:-.02em;color:#1d1d1f}
.lines{list-style:none;display:flex;flex-direction:column;gap:${tall ? 22 : 16}px}
.lines li{display:flex;gap:20px;align-items:flex-start;font-size:40px;line-height:1.3}
.lines b{flex:none;width:1em;color:${accent};font-weight:800;text-align:center}
.L-notes .safe{gap:22px}
.L-notes main{justify-content:center}
.L-notes .paper{flex:none}
.L-notes footer{align-items:center}
.L-notes .sig .bname{color:${onColor(accent)};font-size:30px}
.L-notes .sig .bname i{background:${onColor(accent)}}
.L-notes .cta{background:${onColor(accent)};color:${accent}}
.vs{width:100%;border-collapse:separate;border-spacing:0 12px;table-layout:fixed}
.vs th{font-size:30px;text-transform:uppercase;letter-spacing:.08em;text-align:left;padding:0 18px 6px;color:${muted}}
.vs th+th{color:${accent}}
.vs td{font-size:32px;line-height:1.25;padding:20px 18px;vertical-align:top;background:${rgba(fg, .06)}}
.vs td+td{background:${rgba(accent, .16)};font-weight:600}
.vs .cell{display:flex;gap:12px;align-items:flex-start}
.vs td b{flex:none;color:${muted}}
.vs td+td b{color:${accent}}
.vs td:first-child{border-radius:14px 0 0 14px}.vs td:last-child{border-radius:0 14px 14px 0}
.price{font-family:${df};font-size:76px;font-weight:800;color:${accent};line-height:1}
.opts{list-style:none;display:flex;flex-direction:column;gap:18px}
.opts li{border:3px solid ${rgba(fg, .35)};border-radius:18px;padding:20px 24px;align-items:center}
.opts b{flex:none;width:52px;height:52px;border-radius:50%;background:${accent};color:${onColor(accent)};display:flex;align-items:center;justify-content:center;font-size:30px}
.ailabel{flex:none;font-size:22px;line-height:1.2;color:${L === 'notes' ? onColor(accent) : fg};opacity:.85}
.draft{position:absolute;left:0;right:0;top:0;height:${Math.max(30, Math.round(H * s.t * .6))}px;background:#dc2626;color:#fff;font:700 22px/${Math.max(30, Math.round(H * s.t * .6))}px ${bf};text-align:center;letter-spacing:.12em;z-index:9}
</style></head><body><div id="ad" class="L-${L} R-${ratio}">
${pic ? `<div class="pic"><img src="${pic}" alt=""></div>` : (['quote-card', 'stat', 'offer-card'].includes(L) ? '<div class="deco"></div>' : '')}${scrim}
<div class="safe">${body(spec, base, ratio)}${spec.ai_label ? `<div class="ailabel" data-t="ai_label">${AI_LABEL}</div>` : ''}</div>
${spec.draft_label ? `<div class="draft">${esc(spec.draft_label)}</div>` : ''}
</div></body></html>`;
}

async function fitAndCheck(page, spec, ratio) {
  return page.evaluate(({ safeFrac, fg, bg, accent }) => {
    const ad = document.getElementById('ad'), safe = ad.querySelector('.safe'), main = ad.querySelector('main');
    const fits = [...ad.querySelectorAll('[data-fit]')].map(el => { const [max, min] = el.dataset.fit.split(',').map(Number); el.style.fontSize = max + 'px'; return { el, size: max, min }; });
    // only what the shrinking can fix: the flexible main area and words wider than their box
    const over = () => main.scrollHeight > main.clientHeight + 1 || [...main.querySelectorAll('[data-t]')].some(e => e.scrollWidth > e.clientWidth + 1);
    let guard = 0;
    while (over() && guard++ < 80) {
      let changed = false;
      for (const f of fits) if (f.size > f.min) { f.size = Math.max(f.min, Math.round(f.size * .95)); f.el.style.fontSize = f.size + 'px'; changed = true; }
      if (!changed) break;
    }
    const W = ad.clientWidth, H = ad.clientHeight;
    // photo-hook: keep the scrim dark down to the last line of text, then let the picture through
    const scrimEl = ad.querySelector('.scrim');
    if (scrimEl && ad.classList.contains('L-photo-hook')) {
      const n = parseInt(bg.slice(1), 16), c = `${n >> 16 & 255},${n >> 8 & 255},${n & 255}`;
      const kids = [...main.children]; const textBottom = kids.length ? Math.max(...kids.map(k => k.getBoundingClientRect().bottom)) : H * .4;
      const footTop = ad.querySelector('footer')?.getBoundingClientRect().top ?? H * .8;
      const p1 = Math.min(98, (textBottom + 28) / H * 100), p2 = Math.min(99, p1 + 10), p3 = Math.max(p2, (footTop - 40) / H * 100);
      scrimEl.style.background = `linear-gradient(180deg, rgba(${c},.9) 0%, rgba(${c},.84) ${p1}%, rgba(${c},.22) ${p2}%, rgba(${c},.22) ${p3}%, rgba(${c},.8) 100%)`;
    }
    const sr = safe.getBoundingClientRect();
    const zone = { top: H * safeFrac.t, bottom: H * (1 - safeFrac.b), left: W * safeFrac.s, right: W * (1 - safeFrac.s) };
    const overflow = [], outside = [], text = {};
    if (main.scrollHeight > main.clientHeight + 1) overflow.push('main');
    if (safe.scrollHeight > safe.clientHeight + 2) overflow.push('safe area (header/footer too tall)');
    for (const e of ad.querySelectorAll('[data-t]')) {
      const k = e.dataset.t; text[k] = e.tagName === 'IMG' ? '[logo]' : e.innerText.trim();
      if (e.scrollWidth > e.clientWidth + 1) overflow.push(k);
      const r = e.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) continue;
      if (r.bottom > sr.bottom + 1 || r.top < sr.top - 1) overflow.push(k + ' (clipped)');
      if ((r.top < zone.top - 1 || r.bottom > zone.bottom + 1 || r.left < zone.left - 1 || r.right > zone.right + 1)) outside.push(k);
    }
    const sizes = Object.fromEntries(fits.map(f => [f.el.dataset.t, f.size]));
    const atMin = fits.filter(f => f.size === f.min).map(f => f.el.dataset.t);
    const fonts = {};
    for (const el of [document.querySelector('h1,h2,.num,blockquote,.bname'), document.querySelector('.sub,.bul li,.lines li,.cta,.attr,td')].filter(Boolean)) {
      const cs = getComputedStyle(el), first = cs.fontFamily.split(',')[0].replace(/"/g, '').trim();
      fonts[first] = (fonts[first] ?? true) && document.fonts.check(`${cs.fontWeight} 32px "${first}"`) && [...document.fonts].some(f => f.family.replace(/"/g, '') === first && f.status === 'loaded');
    }
    return { overflow: [...new Set(overflow)], outside_safe: [...new Set(outside)], sizes, at_min: atMin, fonts, text };
  }, { safeFrac: SAFE[ratio], fg: spec.brand.fg, bg: spec.brand.bg, accent: spec.brand.accent });
}

async function main() {
  const args = process.argv.slice(2);
  const specs = [], opts = { out: 'renders', overlay: false, ratios: Object.keys(RATIOS) };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--out') opts.out = args[++i];
    else if (args[i] === '--overlay') opts.overlay = true;
    else if (args[i] === '--ratios') opts.ratios = args[++i].split(',');
    else specs.push(args[i]);
  }
  if (!specs.length) { console.error('usage: node render_static.mjs spec.json [...] --out renders/ [--overlay] [--ratios 1x1,4x5,9x16]'); process.exit(2); }
  const pw = loadPlaywright();
  const browser = await launch(pw);
  const outDir = path.resolve(opts.out); fs.mkdirSync(path.join(outDir, '.build'), { recursive: true });
  let failed = 0;
  for (const specPath of specs) {
    const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
    const base = path.dirname(path.resolve(specPath));
    if (!LAYOUTS.includes(spec.layout)) throw new Error(`${specPath}: layout must be one of ${LAYOUTS.join(', ')}`);
    for (const k of ['picture', 'inset']) if (spec[k]?.src && !fs.existsSync(path.resolve(base, spec[k].src))) throw new Error(`${specPath}: ${k} file not found: ${spec[k].src}`);
    if (spec.brand?.logo && !fs.existsSync(path.resolve(base, spec.brand.logo))) throw new Error(`${specPath}: logo not found`);
    const report = { id: spec.id, concept: spec.concept, layout: spec.layout, spec: path.resolve(specPath), rendered_at: new Date().toISOString(), files: [] };
    const solid = !spec.picture?.src || ['notes', 'us-vs-them', 'split', 'offer-card'].includes(spec.layout);
    for (const ratio of (spec.ratios || opts.ratios)) {
      const [W, H] = RATIOS[ratio];
      const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
      const tmp = path.join(outDir, '.build', `${spec.id}_${ratio}.html`);
      fs.writeFileSync(tmp, html(spec, base, ratio));
      await page.goto(pathToFileURL(tmp).href, { waitUntil: 'load', timeout: 30000 }).catch(() => {});
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(150);
      const res = await fitAndCheck(page, spec, ratio);
      const file = path.join(outDir, `${spec.id}_${ratio}.png`);
      await page.screenshot({ path: file, clip: { x: 0, y: 0, width: W, height: H } });
      if (opts.overlay) {
        const s = SAFE[ratio];
        await page.evaluate(({ s }) => { const d = document.createElement('div'); d.style.cssText = `position:absolute;z-index:99;top:${s.t * 100}%;bottom:${s.b * 100}%;left:${s.s * 100}%;right:${s.s * 100}%;outline:6px dashed rgba(0,200,255,.95);box-shadow:0 0 0 9999px rgba(0,0,0,.35)`; document.getElementById('ad').appendChild(d); }, { s });
        await page.screenshot({ path: path.join(outDir, `${spec.id}_${ratio}_safe.png`), clip: { x: 0, y: 0, width: W, height: H } });
      }
      const b = spec.brand;
      const checks = {
        contrast_text_on_bg: solid ? contrast(spec.layout === 'notes' ? '#1d1d1f' : b.fg, spec.layout === 'notes' ? (b.paper || '#fffdf6') : b.bg) : 'photo background: check by eye',
        contrast_cta: contrast(onColor(b.accent), b.accent),
      };
      const contrastFail = (typeof checks.contrast_text_on_bg === 'number' && checks.contrast_text_on_bg < 4.5) || (checks.contrast_cta != null && checks.contrast_cta < 4.5);
      const fontFail = Object.values(res.fonts).some(v => !v);
      const pass = !res.overflow.length && !res.outside_safe.length && !contrastFail;
      if (!pass) failed++;
      report.files.push({ ratio, width: W, height: H, file: path.relative(process.cwd(), file), pass, ...res, ...checks,
        warnings: [...(fontFail ? ['a brand font did not load; fallback used (check network or font_files)'] : []), ...Object.entries(res.text).filter(([k, v]) => /['"]/.test(v)).map(([k]) => `straight quote marks in ${k}: use ’ “ ” in the copy manifest`), ...(res.at_min.length ? [`at minimum size: ${res.at_min.join(', ')} (consider shorter copy)`] : [])] });
      console.log(`${pass ? 'PASS' : 'FAIL'}  ${path.basename(file)}${res.overflow.length ? '  overflow: ' + res.overflow.join(', ') : ''}${res.outside_safe.length ? '  outside safe zone: ' + res.outside_safe.join(', ') : ''}${contrastFail ? '  contrast below 4.5:1' : ''}${fontFail ? '  (font fallback)' : ''}`);
      await page.close();
    }
    fs.writeFileSync(path.join(outDir, `${spec.id}.report.json`), JSON.stringify(report, null, 2));
  }
  await browser.close();
  process.exit(failed ? 1 : 0);
}

main().catch(e => { console.error(e.message || e); process.exit(2); });
