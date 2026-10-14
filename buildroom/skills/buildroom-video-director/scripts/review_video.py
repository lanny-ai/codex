#!/usr/bin/env python3
"""Video Director review pack and kit.

  review_video.py check --video renders/V1_9x16.mp4 --edit edit.json --script script.txt
                        [--transcript transcript.json] --out review/
      Measures what can be measured and says plainly what cannot:
        technical    codec, pixel format, size, frame rate, audio, duration against the edit (±0.1 s)
        loudness     integrated -14 LUFS (±1 LU), true peak at or below -1 dBTP
        opening      brand cue on screen by 2.0 s; first spoken word by 1.0 s (ads) or 2.0 s (others)
        ending       call-to-action end card held at least 2.5 s
        words        what was said (transcript) against the approved script, word for word
        captions     size >= 48 px, at most two lines, inside the safe zone, each cue >= 0.7 s
        pacing aids  dead air over 1.2 s inside the speech; cuts per minute
        frames       a contact sheet (one frame a second) and a safe-zone overlay frame
      Motion, pacing and feel are marked UNVERIFIED: the member watches the full cut with sound.
      Rebuilds review/checklist.md from every check so far.

  review_video.py kit --project project.json --manifest videos.json --renders renders/ --out kit/ [--preview] [--force]
      Refuses unless the ledger says every video passed G3 and G4 and the member approved it.
      Builds kit/: videos/ (structured names), captions/*.srt, thumbnails/*.jpg, publish.csv
      (title, caption, description, CTA, UTM-keyed URL per video and ratio), disclosure-sheet.md.

Standard library plus ffmpeg (ffprobe optional). Manifest format: references/delivery.md.
"""
import argparse, csv, difflib, json, re, shutil, sys, urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from videolib import (RATIOS, SAFE, LOUDNESS_TARGET, TRUE_PEAK, ffmpeg_bin, run, probe, loudness, silences,  # noqa: E402
                      load_json, norm_words, caption_lines)
import ledger  # noqa: E402

HOOK_LIMIT = {"ad": 1.0}


def ratio_of(path, info):
    for r, (w, h) in RATIOS.items():
        if (info.get("width"), info.get("height")) == (w, h):
            return r
    m = re.search(r"_(9x16|4x5|1x1|16x9)\b", Path(path).name)
    return m[1] if m else None


def check(a):
    video, out = Path(a.video), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    edl_path = Path(a.edit)
    edl = load_json(edl_path)
    base = edl_path.resolve().parent
    info = probe(video)
    ratio = ratio_of(video, info)
    res = {"video": str(video), "id": edl["id"], "ratio": ratio, "playbook": edl.get("playbook"), "checks": [], "unverified": []}

    def add(name, ok, detail, severity="fix"):
        res["checks"].append({"check": name, "result": "pass" if ok else ("FAIL" if severity == "fix" else "note"), "detail": detail})

    # technical
    exp_w, exp_h = RATIOS.get(ratio, (None, None))
    fps = float(edl.get("fps", 30))
    add("size", (info["width"], info["height"]) == (exp_w, exp_h), f"{info['width']}×{info['height']} (expected {exp_w}×{exp_h} for {ratio})")
    add("codec", info["vcodec"] == "h264" and info["pix_fmt"] in ("yuv420p", None), f"{info['vcodec']} {info['pix_fmt']}")
    add("frame rate", info["fps"] is not None and abs(info["fps"] - fps) < 0.05, f"{info['fps']} fps (edit says {fps:g})")
    add("audio", info["acodec"] == "aac" and info["sample_rate"] == 48000, f"{info['acodec']} {info['sample_rate']} Hz")
    expected = 0.0
    for c in edl["clips"]:
        expected += float(c["dur"]) if c.get("type") == "card" or str(c["src"]).lower().endswith((".png", ".jpg", ".jpeg")) else float(c["out"]) - float(c.get("in", 0))
    add("duration", info["duration"] is not None and abs(info["duration"] - expected) <= 0.1, f"{info['duration']:.2f} s (edit {expected:.2f} s, ±0.1)")
    # loudness
    L = loudness(video)
    target = float(edl.get("loudness", LOUDNESS_TARGET))
    add("loudness", L["integrated"] is not None and abs(L["integrated"] - target) <= 1.0, f"{L['integrated']} LUFS integrated (target {target:g} ±1)")
    add("true peak", L["true_peak"] is not None and L["true_peak"] <= TRUE_PEAK + 0.05, f"{L['true_peak']} dBTP (limit {TRUE_PEAK:g})")
    # opening and ending
    cue = edl.get("brand_cue") or {}
    first_clip = edl["clips"][0] if edl["clips"] else {}
    if cue.get("src"):
        add("brand cue by 2 s", float(cue.get("at", 0)) <= 2.0 and float(cue.get("dur", 0)) > 0, f"{Path(cue['src']).name} at {cue.get('at', 0)} s for {cue.get('dur')} s")
    elif cue.get("type") == "face":
        add("brand cue by 2 s", first_clip.get("type", "aroll") == "aroll", "the member's face opens the first clip (check by eye that it is in frame from 0 s)")
        res["unverified"].append("face in frame from the first frame (look at the 0 s frame on the sheet)")
    else:
        add("brand cue by 2 s", False, "no brand cue in the edit (logo, name or the member's face)")
    last = edl["clips"][-1] if edl["clips"] else {}
    hold = float(last.get("dur", 0)) if last.get("type") == "card" else 0
    add("end card held >= 2.5 s", hold >= 2.5, f"last clip is {'an end card held ' + str(hold) + ' s' if last.get('type') == 'card' else 'not an end card'}")
    # words
    tr = None
    tpath = Path(a.transcript) if a.transcript else base / (edl.get("captions") or {}).get("transcript", "transcript.json")
    if tpath.exists():
        tr = load_json(tpath)
        words = tr.get("words", [])
        limit = HOOK_LIMIT.get(edl.get("playbook"), 2.0)
        if words:
            add(f"first word by {limit:g} s", words[0]["start"] <= limit, f"first word at {words[0]['start']:.2f} s"
                + (" (approximate timing)" if tr.get("approximate") else ""), severity="fix" if edl.get("playbook") == "ad" else "note")
        if a.script:
            said, approved = norm_words(" ".join(w["w"] for w in words)), norm_words(Path(a.script).read_text(encoding="utf-8"))
            sm = difflib.SequenceMatcher(a=approved, b=said, autojunk=False)
            ratio_m = sm.ratio()
            diffs = [f"{tag}: '{' '.join(approved[i1:i2])}' → '{' '.join(said[j1:j2])}'" for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
            if tr.get("approximate"):
                res["unverified"].append("words said vs the approved script: the transcript was aligned from the script (no speech engine), so it cannot show a departure. Listen, or transcribe with a speech engine.")
            else:
                add("words match the approved script", not diffs, f"{ratio_m:.0%} match" + ("" if not diffs else "; " + "; ".join(diffs[:8])))
        # captions geometry (burned by the director)
        rep_path = base / edl.get("out_dir", "renders") / f"{edl['id']}.assemble.json"
        cap = (edl.get("captions") or {})
        if cap.get("mode") == "burn" and rep_path.exists():
            rep = load_json(rep_path)
            st = next((r.get("caption_style") for r in rep["ratios"] if r["ratio"] == ratio), None)
            if st:
                H = RATIOS[ratio][1]
                add("caption size >= 48 px", st["size"] >= 48, f"{st['size']} px")
                add("captions <= 2 lines", st["max_lines"] <= 2, f"longest cue: {st['max_lines']} line(s)")
                add("captions inside the safe zone", st["margin_v"] >= SAFE[ratio]["b"] * H, f"bottom margin {st['margin_v']} px (unsafe band {int(SAFE[ratio]['b'] * H)} px)")
            cues = caption_lines(words, max_chars=int(cap.get("max_chars", 26)))
            short = [c for c in cues if c["end"] - c["start"] < 0.7 - 1e-3]
            add("each caption on screen >= 0.7 s", not short, f"{len(cues)} cues; {len(short)} shorter than 0.7 s" if short else f"{len(cues)} cues")
            if tr.get("approximate"):
                res["unverified"].append("caption timing follows an approximate transcript; watch that captions track the voice")
        elif cap.get("mode") == "submagic":
            sw = video.with_suffix(".submagic-words.json")
            res["unverified"].append("captions were set by SubMagic: check spelling of names, numbers and brand words against the script on the contact sheet"
                                     + (" (SubMagic's word list is saved beside the video)" if sw.exists() else ""))
    else:
        res["unverified"].append("no transcript: the words said and the caption timing were not checked")
    # pacing aids
    voice = base / edl.get("out_dir", "renders") / f"{edl['id']}.voice.wav"
    speech_end = expected - (hold or 0)
    if voice.exists():
        gaps = [(s, e) for s, e in silences(voice, noise="-38dB", min_d=1.2) if e is not None and s > 0.3 and e < speech_end - 0.3]
        add("no dead air over 1.2 s", not gaps, "; ".join(f"{s:.1f}–{e:.1f} s" for s, e in gaps) or "none", severity="note")
    p = run([ffmpeg_bin(), "-hide_banner", "-nostats", "-i", str(video), "-vf", "scdet=threshold=12", "-f", "null", "-"], check=False)
    cuts = len(re.findall(r"lavfi\.scd\.time", p.stderr))
    res["cuts_per_minute"] = round(cuts / max(info["duration"] or 1, 1) * 60, 1)
    # frames
    stem = f"{edl['id']}_{ratio}"
    W, H = RATIOS.get(ratio, (1080, 1920))
    cols = 6 if H > W else 4
    n = int((info["duration"] or 1)) + 1
    rows = (n + cols - 1) // cols
    tw = 220 if H > W else 360
    run([ffmpeg_bin(), "-y", "-i", str(video), "-vf", f"fps=1,scale={tw}:-2,tile={cols}x{rows}:padding=6:color=0x1b1b22",
         "-frames:v", "1", "-update", "1", str(out / f"{stem}_sheet.png")])
    s = SAFE.get(ratio, {"t": 0, "b": 0, "s": 0})
    box = f"drawbox=x={int(W * s['s'])}:y={int(H * s['t'])}:w={int(W * (1 - 2 * s['s']))}:h={int(H * (1 - s['t'] - s['b']))}:color=cyan@0.9:t=6"
    mid = min(max(1.0, (info["duration"] or 2) * 0.35), (info["duration"] or 2) - 0.1)
    run([ffmpeg_bin(), "-y", "-ss", f"{mid:.2f}", "-i", str(video), "-vf", box, "-frames:v", "1", "-update", "1", str(out / f"{stem}_safe.png")])
    res["frames"] = {"sheet": f"{stem}_sheet.png", "safe_overlay": f"{stem}_safe.png"}
    res["unverified"].append("motion, pacing, performance and how it feels: the member watches the full cut with sound before approving")
    res["loudness"] = L
    res["probe"] = info
    (out / f"{stem}.check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    fails = [c for c in res["checks"] if c["result"] == "FAIL"]
    print(f"{stem}: {len(res['checks']) - len(fails)}/{len(res['checks'])} checks pass" + (f" · FAIL: {', '.join(c['check'] for c in fails)}" if fails else "")
          + f" · {len(res['unverified'])} unverified · sheet {out / res['frames']['sheet']}")
    write_checklist(out)
    return 1 if fails else 0


def write_checklist(out):
    md = ["# Video review checklist", "",
          "Automated results first. The G3 craft and G4 compliance verdicts are the reviewer's, on the actual files "
          "(contact sheets, safe-zone frames, and the full video with sound where the reviewer can play it). "
          "Verdicts: pass / revise / unverified, with timestamp, defect and the smallest fix.", ""]
    for f in sorted(out.glob("*.check.json")):
        r = load_json(f)
        md.append(f"## {r['id']} · {r['ratio']} · {r.get('playbook')}")
        for c in r["checks"]:
            md.append(f"- {'✅' if c['result'] == 'pass' else ('⚠️' if c['result'] == 'note' else '❌')} **{c['check']}** — {c['detail']}")
        md.append(f"- cuts per minute: {r.get('cuts_per_minute')}")
        for u in r["unverified"]:
            md.append(f"- ⬜ unverified: {u}")
        md.append(f"- frames: `{r['frames']['sheet']}`, `{r['frames']['safe_overlay']}`")
        md += ["", "**G3 craft (reviewer)** — hook lands and pays off · every beat adds something · real face intact, no generated hero · "
               "B-roll plausible and on-message · captions readable, accurate, off faces · brand cue early · CTA clear and held · "
               "sound: voice clear over music", "  - verdict: ______ · issues (time · defect · fix):", "",
               "**G4 compliance (reviewer)** — every claim and number traced to proof · guarantees word for word · no synthetic customer or "
               "testimonial · consent on file for every person and voice · AI label where a generated person appears · music licensed · "
               "destination matches the CTA", "  - verdict: ______ · issues:", ""]
    (out / "checklist.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def slug(s, n=28):
    full = re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    if len(full) > n:
        full = full[:n].rsplit("-", 1)[0] if "-" in full[:n] else full[:n]
    return full or "x"


def kit(a):
    data = ledger.load(ledger.project_path(a.project))
    errs = ledger.errors_for(data, kit=True)
    if errs and not a.preview:
        raise SystemExit("kit refused: " + "; ".join(errs))
    m = load_json(a.manifest)
    cycle = m.get("cycle") or data["cycle"]
    yymm = re.sub(r"\D", "", cycle)[2:6] or cycle
    out, renders = Path(a.out), Path(a.renders)
    if out.exists() and any(out.iterdir()):
        if not a.force:
            raise SystemExit(f"{out} is not empty; pass --force to rebuild it")
        shutil.rmtree(out)
    for d in ("videos", "captions", "thumbnails"):
        (out / d).mkdir(parents=True, exist_ok=True)
    rows, disc = [], []
    led = {x["id"]: x for x in data["ads"]}
    for v in m["videos"]:
        name = f"{yymm}_{v['playbook']}_{slug(v.get('slug') or v.get('title', v['id']))}_{v['id']}"
        copy = v.get("platform_copy", {})
        for r in v.get("ratios", ["9x16"]):
            src = renders / f"{v['id']}_{r}.mp4"
            if not src.exists():
                raise SystemExit(f"{v['id']}: missing final {src}")
            dst = out / "videos" / f"{name}_{r}.mp4"
            shutil.copy2(src, dst)
            url = copy.get("url", "")
            if url:
                q = {"utm_source": copy.get("utm_source", "meta"), "utm_medium": "paid_social" if v["playbook"] == "ad" else "organic_video",
                     "utm_campaign": f"{yymm}_{v['id']}", "utm_content": f"{name}_{r}"}
                url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(q)
            rows.append({"file": dst.name, "ratio": r, "title": copy.get("title", ""), "caption": copy.get("caption", ""),
                         "description": copy.get("description", ""), "cta_button": copy.get("cta_button", ""), "url": url})
        srt = renders / f"{v['id']}.srt"
        if srt.exists():
            shutil.copy2(srt, out / "captions" / f"{name}.srt")
        first = renders / f"{v['id']}_{v.get('ratios', ['9x16'])[0]}.mp4"
        run([ffmpeg_bin(), "-y", "-ss", str(v.get("thumbnail_at", 1.0)), "-i", str(first), "-frames:v", "1", "-q:v", "2", "-update", "1",
             str(out / "thumbnails" / f"{name}.jpg")])
        lv = led.get(v["id"], {})
        gen = "; ".join(f"{g.get('asset')} ({g.get('provider')}, {g.get('model')})" for g in v.get("generated", [])) or "none"
        ppl = "; ".join(f"{p.get('who')} (consent: {p.get('consent')})" for p in v.get("people", [])) or "none"
        claims = "; ".join(f"{c.get('claim')} → {c.get('proof')}" for c in v.get("claims", [])) or "none"
        disc.append(f"| {name} | {gen} | {ppl} | {'yes' if v.get('ai_label') else 'no'} | {v.get('music', 'none')} | {claims} | "
                    f"G3 {lv.get('G3', {}).get('verdict', 'unverified')} · G4 {lv.get('G4', {}).get('verdict', 'unverified')} |")
    with open(out / "publish.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    (out / "disclosure-sheet.md").write_text("\n".join([
        f"# Disclosure sheet · videos · cycle {cycle}", "",
        "| Video | Generated footage (asset, provider, model) | Real people (consent) | AI label on screen | Music (licence) | Claims → proof | Review |",
        "|---|---|---|---|---|---|---|", *disc, "",
        "When uploading: answer each platform's AI-content questions truthfully; never remove an on-screen AI label; keep the original "
        "generated files (their provenance metadata is part of the record). This sheet records the checks made; it is not legal advice "
        "or a guarantee of platform approval."]) + "\n", encoding="utf-8")
    if errs:
        (out / "NOT-READY.txt").write_text("PREVIEW ONLY. Not ready to publish:\n- " + "\n- ".join(errs) + "\n", encoding="utf-8")
        print(f"kit PREVIEW written to {out} · {len(m['videos'])} videos · NOT ready (see NOT-READY.txt)")
    else:
        print(f"kit written to {out} · {len(m['videos'])} videos · {len(rows)} files")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--video", required=True); c.add_argument("--edit", required=True)
    c.add_argument("--script"); c.add_argument("--transcript"); c.add_argument("--out", required=True)
    k = sub.add_parser("kit")
    k.add_argument("--project", required=True); k.add_argument("--manifest", required=True)
    k.add_argument("--renders", required=True); k.add_argument("--out", required=True)
    k.add_argument("--preview", action="store_true"); k.add_argument("--force", action="store_true")
    a = ap.parse_args()
    sys.exit(check(a) if a.cmd == "check" else (kit(a) or 0))


if __name__ == "__main__":
    main()
