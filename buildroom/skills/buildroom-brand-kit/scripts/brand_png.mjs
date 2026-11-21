#!/usr/bin/env node
/*
 * Brand Kit: PNG copies of the logo files, for tools that will not take a vector file.
 *
 *   node brand_png.mjs Design/Brand/logo [--width 2000]
 *
 * For every .svg in the folder it writes a .png beside it with a transparent background: wordmarks at --width
 * pixels wide (default 2000), marks at 1024 × 1024. Nothing else is changed and nothing goes online.
 * Needs Playwright (npm i playwright, then npx playwright install chromium), or CHROME_PATH pointing at an
 * installed Chrome, Edge or Chromium. The vector files are the logo; these are convenience copies.
 */
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';

function loadPlaywright() {
  const req = createRequire(path.join(process.cwd(), 'x.js'));
  for (const name of ['playwright', 'playwright-core']) {
    try { return req(name); } catch { /* next */ }
    try { return createRequire(import.meta.url)(name); } catch { /* next */ }
  }
  console.error('Playwright is not installed. Run: npm i playwright && npx playwright install chromium');
  process.exit(2);
}

const args = process.argv.slice(2);
const dir = args.find(a => !a.startsWith('--'));
const wi = args.indexOf('--width');
const width = wi >= 0 ? Math.max(200, Math.min(6000, parseInt(args[wi + 1], 10) || 2000)) : 2000;
if (!dir || !fs.existsSync(dir)) { console.error('Usage: node brand_png.mjs <folder with the logo .svg files> [--width 2000]'); process.exit(2); }
const svgs = fs.readdirSync(dir).filter(f => f.toLowerCase().endsWith('.svg')).sort();
if (!svgs.length) { console.error('No .svg files in ' + dir); process.exit(1); }

const { chromium } = loadPlaywright();
let browser;
try {
  browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
} catch (e) {
  console.error('Could not start Chromium. Run npx playwright install chromium, or set CHROME_PATH.\n' + e.message);
  process.exit(2);
}
const out = [];
for (const f of svgs) {
  const src = fs.readFileSync(path.join(dir, f), 'utf8');
  const vb = /viewBox="([-\d.\s]+)"/.exec(src);
  if (!vb) { console.error('Skipped ' + f + ': no viewBox'); continue; }
  const [, , vw, vh] = vb[1].trim().split(/\s+/).map(Number);
  const mark = Math.abs(vw - vh) < 0.5;
  const W = mark ? 1024 : width, H = Math.max(1, Math.round(W * vh / vw));
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.setContent(`<html><body style="margin:0;background:transparent"><img src="${pathToFileURL(path.resolve(dir, f)).href}" style="display:block;width:${W}px;height:${H}px"></body></html>`);
  await page.waitForLoadState('networkidle');
  const png = path.join(dir, f.replace(/\.svg$/i, '.png'));
  await page.screenshot({ path: png, omitBackground: true });
  await page.close();
  out.push({ file: png, width: W, height: H });
}
await browser.close();
console.log(JSON.stringify({ wrote: out }, null, 2));
