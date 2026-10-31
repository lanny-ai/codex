#!/usr/bin/env python3
"""Ad Studio review pack and launch kit.

  review_pack.py sheet --renders renders/ --manifest copy-manifest.json --out review/
      Contact sheet (HTML, every ad in every ratio, safe-zone overlays beside them) and a
      reviewer checklist pre-filled with the automated results: renderer checks, exact match
      between each spec's words and the approved copy manifest, real PNG dimensions, and an
      OCR read-back when tesseract is installed. The G3/G4 judgement is left to the reviewer.

  review_pack.py kit --project project.json --renders renders/ --manifest copy-manifest.json --out kit/
      Refuses unless the ledger says every ad passed G3 and G4 and the member approved it.
      Builds kit/: ads/ with structured names, ads.csv (primary text, headline, description,
      CTA, UTM-keyed URL per ad), landing-headlines.md, test-plan.md, disclosure-sheet.md,
      and appends this cycle's rows to learning-library.csv next to the kit.

Stdlib only. The manifest format is in references/launch-kit.md.
"""
import argparse, csv, html, json, re, shutil, struct, subprocess, sys, urllib.parse
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger  # noqa: E402

RATIOS = {"1x1": (1080, 1080), "4x5": (1080, 1350), "9x16": (1080, 1920)}


def png_size(p):
    with open(p, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def norm(s):
    return re.sub(r"[^a-z0-9$%]+", " ", str(s).lower()).strip()


def flat_copy(c):
    out = {}
    for k, v in (c or {}).items():
        if isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    out[f"{k}[{i}]"] = item.get("text", "")
                elif isinstance(item, list):
                    for j, x in enumerate(item):
                        out[f"{k}[{i}][{j}]"] = x
                else:
                    out[f"{k}[{i}]"] = item
        elif v not in (None, ""):
            out[k] = v
    return out


def slug(s, n=24):
    full = re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    if len(full) > n:  # cut at a word boundary
        full = full[:n].rsplit("-", 1)[0] if "-" in full[:n] else full[:n]
    return full or "x"


def load_reports(renders):
    reps = {}
    for f in sorted(Path(renders).glob("*.report.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        reps[r["id"]] = r
    return reps


def ocr(path):
    if not shutil.which("tesseract"):
        return None
    try:
        out = subprocess.run(["tesseract", str(path), "-", "--psm", "11"], capture_output=True, text=True, timeout=60)
        return out.stdout
    except (subprocess.SubprocessError, OSError):
        return None


def cmd_sheet(a):
    renders, out = Path(a.renders), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    approved = {ad["id"]: ad for ad in manifest.get("ads", [])}
    reps = load_reports(renders)
    if not reps:
        raise SystemExit("no *.report.json in renders/: run render_static.mjs first")
    rows, md = [], [f"# Review checklist · cycle {manifest.get('cycle', '')}\n",
                    "Automated results first; the G3 and G4 judgement is the reviewer's, on the actual files. "
                    "Verdicts: pass / revise / unverified, with file, region, defect and smallest fix.\n"]
    for ad_id, rep in reps.items():
        spec = json.loads(Path(rep["spec"]).read_text(encoding="utf-8"))
        problems = []
        ap = approved.get(ad_id)
        if not ap:
            problems.append("not in the copy manifest: these words were never approved")
        else:
            want, got = flat_copy(ap.get("copy")), flat_copy(spec.get("copy"))
            for k in sorted(set(want) | set(got)):
                if str(want.get(k, "")).strip() != str(got.get(k, "")).strip():
                    problems.append(f"copy differs from approved at `{k}`: spec {got.get(k, '—')!r} vs approved {want.get(k, '—')!r}")
            if bool(spec.get("ai_label")) != bool(ap.get("ai_label")):
                problems.append("AI label setting differs from the manifest")
        cells, lines = [], []
        for f in rep["files"]:
            p = Path(f["file"]) if Path(f["file"]).is_absolute() else Path.cwd() / f["file"]
            if not p.exists():
                p = renders / Path(f["file"]).name
            size = png_size(p) if p.exists() else None
            exp = RATIOS.get(f["ratio"])
            dim_ok = size == exp
            text_seen = ocr(p)
            ocr_note = "OCR not available (install tesseract to read the words back)"
            if text_seen is not None and ap:
                seen = norm(text_seen)
                key = norm(ap["copy"].get("hook") or ap["copy"].get("quote") or ap["copy"].get("question")
                           or ap["copy"].get("title") or ap["copy"].get("offer") or ap["copy"].get("number") or "")
                words = [w for w in key.split() if len(w) > 2]
                hit = sum(1 for w in words if w in seen)
                ocr_note = f"OCR read back {hit}/{len(words)} key words of the main line"
            lines.append(f"  - `{p.name}` · {size[0] if size else '?'}×{size[1] if size else '?'} "
                         f"{'ok' if dim_ok else 'WRONG SIZE'} · renderer {'pass' if f['pass'] else 'FAIL'}"
                         f"{' · overflow: ' + ', '.join(f['overflow']) if f['overflow'] else ''}"
                         f"{' · outside safe zone: ' + ', '.join(f['outside_safe']) if f['outside_safe'] else ''}"
                         f" · text contrast {f.get('contrast_text_on_bg')} · CTA contrast {f.get('contrast_cta')}"
                         f"{' · ' + '; '.join(f['warnings']) if f.get('warnings') else ''} · {ocr_note}")
            safe = renders / f"{ad_id}_{f['ratio']}_safe.png"
            rel = lambda q: html.escape(Path(q).resolve().as_uri())
            cells.append(f"<figure><img src=\"{rel(p)}\" alt=\"\"><figcaption>{f['ratio']} · {'pass' if f['pass'] and dim_ok else 'CHECK'}</figcaption></figure>"
                         + (f"<figure class=s><img src=\"{rel(safe)}\" alt=\"\"><figcaption>{f['ratio']} safe zone</figcaption></figure>" if safe.exists() else ""))
        rows.append(f"<section><h2>{html.escape(ad_id)} <small>{html.escape(rep['layout'])} · concept {html.escape(str(rep.get('concept')))}</small></h2>"
                    + (f"<p class=bad>{'<br>'.join(html.escape(x) for x in problems)}</p>" if problems else "")
                    + f"<div class=row>{''.join(cells)}</div></section>")
        md.append(f"\n## {ad_id} ({rep['layout']})\n")
        md.append("**Automated**\n")
        md.extend(lines)
        md.append("  - copy manifest: " + ("matches the approved words exactly" if not problems else "; ".join(problems)))
        md.append("\n**G3 craft (reviewer)** — brand asset in first glance · reads on mute at phone size · safe zones clear by eye · "
                  "every word matches the manifest · real face intact, no generated hero · plate: light, contact, scale, no phantom text or logos · "
                  "one message, one proof, one CTA · ratios recomposed, not cropped\n  - verdict: ______ · issues (file · region · defect · fix):\n")
        md.append("**G4 compliance (reviewer)** — proof traced to vault IDs with consent · the picture claims nothing unbacked · "
                  "never-say claims absent · results in context · no sensitive-attribute copy · AI label where required · "
                  "likeness consent on file · no fake interface · destination matches · not political\n  - verdict: ______ · issues:\n")
    sheet = f"""<!doctype html><meta charset=utf-8><title>Contact sheet · {html.escape(str(manifest.get('cycle', '')))}</title>
<style>body{{font:15px/1.4 system-ui,sans-serif;background:#111;color:#eee;margin:24px}}h1{{font-size:22px}}h2{{font-size:18px;margin:28px 0 8px}}small{{color:#999;font-weight:400}}
.row{{display:flex;gap:14px;align-items:flex-end;flex-wrap:wrap}}figure{{margin:0}}img{{height:360px;width:auto;display:block;border:1px solid #333}}
figure.s img{{height:180px;opacity:.9}}figcaption{{font-size:12px;color:#aaa;margin-top:4px}}.bad{{color:#f87171}}</style>
<h1>Contact sheet · cycle {html.escape(str(manifest.get('cycle', '')))} · {len(reps)} ads</h1>
<p>Look at each ad at phone size first (about 360px tall here), then open the file at full size.</p>{''.join(rows)}"""
    (out / "contact_sheet.html").write_text(sheet, encoding="utf-8")
    (out / "checklist.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {out/'contact_sheet.html'} and {out/'checklist.md'} for {len(reps)} ads")


def cmd_kit(a):
    proj = ledger.project_path(a.project)
    data = ledger.load(proj)
    errs = ledger.errors_for(data, kit=True)
    if errs and not a.preview:
        raise SystemExit("kit refused: " + "; ".join(errs))
    manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    cycle = manifest.get("cycle") or data["cycle"]
    yymm = re.sub(r"\D", "", cycle)[2:6] or cycle
    concepts = {c["id"]: c for c in manifest.get("concepts", [])}
    reps = load_reports(a.renders)
    led_ads = {x["id"]: x for x in data["ads"]}
    final_out = Path(a.out)
    if final_out.exists() and any(final_out.iterdir()) and not a.force:
        raise SystemExit(f"{final_out} is not empty; pass --force to rebuild it")
    out = final_out.with_name(final_out.name + ".building")  # built aside, swapped in only when complete
    if out.exists():
        shutil.rmtree(out)
    (out / "ads").mkdir(parents=True, exist_ok=True)
    rows, disc, lib = [], [], []
    for ad in manifest["ads"]:
        c = concepts.get(ad["concept"], {})
        hook_id = ad["id"].split("-")[-1]
        name = f"{yymm}_{ad['concept']}-{slug(c.get('angle_slug') or c.get('angle', ''))}_{hook_id}-{slug(ad.get('hook_tactic', ''), 18)}_{slug(ad.get('layout') or c.get('layout', ''), 12)}"
        rep = reps.get(ad["id"])
        if not rep:
            raise SystemExit(f"{ad['id']}: no render report")
        for f in rep["files"]:
            src = Path(f["file"]) if Path(f["file"]).is_absolute() else Path.cwd() / f["file"]
            if not src.exists():
                src = Path(a.renders) / Path(f["file"]).name
            shutil.copy2(src, out / "ads" / f"{name}_{f['ratio']}.png")
        q = {"utm_source": a.utm_source, "utm_medium": "paid_social", "utm_campaign": f"{yymm}_{ad['concept']}", "utm_content": name}
        url = ad.get("url") or manifest.get("destination", "")
        sep = "&" if "?" in url else "?"
        rows.append({"ad_name": name, "files": ", ".join(f"{name}_{f['ratio']}.png" for f in rep["files"]),
                     "primary_text": ad.get("primary_text", ""), "headline": ad.get("headline", ""),
                     "description": ad.get("description", ""), "cta_button": ad.get("cta_button", ""),
                     "url": url + sep + urllib.parse.urlencode(q) if url else "PROPOSED: destination not live yet"})
        la = led_ads.get(ad["id"], {})
        gen = "; ".join(f"{g.get('asset')} ({g.get('provider')}, {g.get('model')})" for g in ad.get("generated", [])) or "none"
        ppl = "; ".join(f"{p.get('who')} (consent: {p.get('consent')})" for p in ad.get("people", [])) or "none"
        claims = "; ".join(f"{x.get('claim')} → {x.get('proof')}" for x in ad.get("claims", [])) or "none"
        disc.append(f"| {name} | {gen} | {ppl} | {'yes' if ad.get('ai_label') else 'no'} | {claims} | refused by default | "
                    f"G3 {la.get('G3', {}).get('verdict', 'unverified')} · G4 {la.get('G4', {}).get('verdict', 'unverified')} |")
        lib.append({"cycle": cycle, "ad_name": name, "concept": ad["concept"], "angle": c.get("angle", ""),
                    "persona": c.get("persona", ""), "awareness": c.get("awareness", ""), "mechanic": c.get("mechanic", ""),
                    "hook_tactic": ad.get("hook_tactic", ""), "layout": ad.get("layout") or c.get("layout", ""),
                    "hypothesis": c.get("hypothesis", ""), "spend": "", "impressions": "", "ctr": "", "leads": "",
                    "qualified_leads": "", "cost_per_qualified": "", "verdict": "", "failed_layer": "", "next_action": ""})
    with open(out / "ads.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    lh = [f"# Landing headlines · cycle {cycle}\n", "The page headline repeats the ad's angle (message match). One page variant per angle; "
          "if the page builder can't vary the headline, keep the angle closest to the page's current headline in the first test.\n"]
    for cid, c in concepts.items():
        lh.append(f"- **{cid} · {c.get('angle', '')}** → \"{c.get('landing_headline', 'WRITE ONE: the angle, as a promise, in the reader’s words')}\"")
    (out / "landing-headlines.md").write_text("\n".join(lh) + "\n", encoding="utf-8")
    b = manifest.get("budget", {})
    tp = [f"# Test plan · cycle {cycle}\n",
          f"**Budget:** {b.get('monthly', 'from §18')} a month. **Test share:** about {b.get('test_share', '20%')} in Meta's creative testing tool "
          "or one small sandbox ad set; the rest stays on what already works (or, on a first cycle, the strongest concept).",
          "**Window:** 10–14 days. Don't judge before day 7 or on fewer than about 1,000 impressions per ad.",
          "**Judge on:** hook rate (3-second views ÷ impressions, video only), click-through rate, cost per lead, and **cost per qualified lead from the CRM** "
          "(counting rule in §18). The platform's lead count alone is not the verdict.",
          "**Against:** the account's own median, not internet benchmarks. First cycle: this cycle sets the baseline.\n",
          "| Concept | Angle | What a win would teach | Hooks in test | Value-first? |", "|---|---|---|---|---|"]
    for cid, c in concepts.items():
        hooks = ", ".join(ad["id"] for ad in manifest["ads"] if ad["concept"] == cid)
        tp.append(f"| {cid} | {c.get('angle', '')} | {c.get('hypothesis', '')} | {hooks} | {'yes' if c.get('value_first') else 'no'} |")
    tp += ["\n**Diagnose by layer:** weak CTR with good engagement → the offer or CTA; good CTR, weak conversion → the landing page (check message match); "
           "leads but few qualified → the angle is attracting the wrong-fit reader. Kill an angle only after two or three differently hooked executions of it fail.",
           "**Fatigue:** watch frequency against audience size; refresh with a new hook or concept on the same brand platform, never a colour swap.",
           "**Come back:** after the window, say \"How did my ads do?\" and bring the numbers per ad name."]
    (out / "test-plan.md").write_text("\n".join(tp) + "\n", encoding="utf-8")
    ds = [f"# Disclosure sheet · cycle {cycle}\n",
          "| Ad | Generated imagery (asset, provider, model) | Real people (consent) | AI label on image | Claims → proof IDs | Political/issue | Review |",
          "|---|---|---|---|---|---|---|", *disc,
          "\nWhen uploading to Meta: answer the AI-content and special-category questions truthfully. Do not remove an on-image AI label. "
          "Keep the original generated files; their provenance metadata is part of the record. "
          "This sheet records the checks made; it is not legal advice or a guarantee of platform approval."]
    (out / "disclosure-sheet.md").write_text("\n".join(ds) + "\n", encoding="utf-8")
    libf = final_out.parent / "learning-library.csv"
    if errs:
        (out / "NOT-READY.txt").write_text("PREVIEW ONLY. Not upload-ready:\n- " + "\n- ".join(errs) + "\n", encoding="utf-8")
    if final_out.exists():
        shutil.rmtree(final_out)
    out.rename(final_out)
    out = final_out
    if errs:  # a preview never enters the learning library
        print(f"kit PREVIEW written to {out} · {len(rows)} ads · NOT upload-ready (see NOT-READY.txt)")
        return
    new = not libf.exists()
    with open(libf, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lib[0]))
        if new:
            w.writeheader()
        w.writerows(lib)
    print(f"kit written to {out} · {len(rows)} ads · learning library rows appended to {libf}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet"); s.add_argument("--renders", required=True); s.add_argument("--manifest", required=True)
    s.add_argument("--out", required=True)
    k = sub.add_parser("kit"); k.add_argument("--project", required=True); k.add_argument("--renders", required=True)
    k.add_argument("--manifest", required=True); k.add_argument("--out", required=True)
    k.add_argument("--utm-source", default="meta"); k.add_argument("--force", action="store_true")
    k.add_argument("--preview", action="store_true", help="build a labelled preview even if gates are open (never for upload)")
    a = ap.parse_args()
    (cmd_sheet if a.cmd == "sheet" else cmd_kit)(a)


if __name__ == "__main__":
    main()
