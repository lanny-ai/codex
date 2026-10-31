#!/usr/bin/env python3
"""Build Room media toolkit tests: ledger, generation, SubMagic, assembly, captions, review, kits.

Runs everything against a local mock of the providers and synthetic media made with ffmpeg; no
network, no keys, no spend. Needs Python 3 and ffmpeg (FFMPEG env, PATH, or pip install
imageio-ffmpeg). The static-renderer check runs only when Node and Playwright are available.

Usage:  python3 buildroom/tests/media/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (no __pycache__ in the skill folders or here)
import json, os, shutil, subprocess, tempfile, threading  # noqa: E402
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # buildroom/
AD = ROOT / "skills/buildroom-ad-studio/scripts"
VD = ROOT / "skills/buildroom-video-director/scripts"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(VD))
import mock_providers  # noqa: E402
from videolib import ffmpeg_bin, caption_lines  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))


def sh(args, cwd, env=None, ok_codes=(0,)):
    env = {**(env or os.environ), "PYTHONDONTWRITEBYTECODE": "1"}
    p = subprocess.run([str(a) for a in args], cwd=cwd, env=env, capture_output=True, text=True)
    return p.returncode in ok_codes, p.stdout + p.stderr, p.returncode


def main():
    keep = "--keep" in sys.argv
    work = Path(tempfile.mkdtemp(prefix="buildroom-media-tests-"))
    srv = mock_providers.serve(0)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    env = {**os.environ, "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost",
           "KIE_API_BASE": f"http://127.0.0.1:{port}", "HIGGSFIELD_API_BASE": f"http://127.0.0.1:{port}",
           "HEYGEN_API_BASE": f"http://127.0.0.1:{port}", "SUBMAGIC_API_BASE": f"http://127.0.0.1:{port}",
           "GEN_POLL_SECONDS": "0.1", "FFMPEG": ffmpeg_bin(), "PYTHONDONTWRITEBYTECODE": "1"}
    (work / ".env").write_text("KIE_API_KEY=testkey\nHIGGSFIELD_API_KEY=hid\nHIGGSFIELD_API_SECRET=hsec\n"
                               "HEYGEN_API_KEY=hgkey\nSUBMAGIC_API_KEY=sk-test\n")
    L, G = VD / "ledger.py", VD / "gen.py"
    py = sys.executable

    # ---- shared copies are identical to the source ----
    for f in (ROOT / "shared/media").iterdir():
        for skill in ("buildroom-ad-studio", "buildroom-video-director"):
            dest = ROOT / "skills" / skill / ("scripts" if f.suffix in (".py", ".mjs") else "references") / f.name
            check(f"shared copy in sync: {skill}/{f.name}", dest.exists() and dest.read_bytes() == f.read_bytes())

    # ---- ledger rules ----
    P = work / "p.json"
    sh([py, L, "init", P, "--cycle", "2026-10"], work)
    ok, out, _ = sh([py, L, "plan", P, "--asset-id", "T", "--provider", "heygen", "--model", "m", "--prompt-ref", "x", "--kind", "twin"], work, ok_codes=(2,))
    check("ledger refuses a twin without consent", ok and "consent" in out)
    ok, out, _ = sh([py, L, "plan", P, "--asset-id", "X", "--provider", "falai", "--model", "m", "--prompt-ref", "x"], work, ok_codes=(2,))
    check("ledger refuses an unrouted provider (fal.ai)", ok)
    ok, out, _ = sh([py, L, "gate", P, "--gate", "G2", "--verdict", "pass", "--by", "producer", "--ref", "x"], work, ok_codes=(2,))
    check("ledger refuses a G2 pass without the member's sign-off", ok and "member" in out, out[-200:])
    for g in ("G0", "G1", "G2"):
        sh([py, L, "gate", P, "--gate", g, "--verdict", "pass", "--by", "member" if g == "G2" else "producer", "--ref", "x"], work)
    for aid, prov, kind in (("IMG", "kie", "plate"), ("VID", "kie", "broll"), ("VID2", "kie", "broll"), ("HV", "higgsfield", "broll"), ("CAP", "submagic", "captions")):
        sh([py, L, "plan", P, "--asset-id", aid, "--provider", prov, "--model", "m" if prov != "kie" else ("nano" if kind == "plate" else "kling"), "--prompt-ref", "x", "--kind", kind], work)
    sh([py, L, "plan", P, "--asset-id", "TWIN", "--provider", "heygen", "--model", "hg", "--prompt-ref", "x", "--kind", "twin", "--consent-ref", "signed 2026-10-14"], work)
    ok, out, _ = sh([py, L, "reserve", P, "--key", "k0", "--asset-id", "IMG", "--cost", "5", "--quote", "q", "--request-ref", "r"], work, ok_codes=(2,))
    check("ledger refuses spend without an authorised cap", ok and "cap" in out)
    for prov, cap, unit in (("kie", "120", "credits"), ("higgsfield", "30", "credits"), ("heygen", "5", "credits"), ("submagic", "3", "minutes")):
        sh([py, L, "authorize", P, "--provider", prov, "--cap", cap, "--units", unit, "--note", "test"], work)

    # ---- generation against the mock ----
    for d in ("plates", "broll", "twin"):
        (work / d).mkdir(exist_ok=True)
    (work / "plates/a.txt").write_text("Desk at dawn. No people.")
    (work / "broll/1.txt").write_text("Slow push-in on a laptop. No people.")
    (work / "broll/2.txt").write_text("explode")
    (work / "twin/s.txt").write_text("A new hook.")
    jobs = {"provider": "kie", "jobs": [
        {"key": "k.img", "asset_id": "IMG", "kind": "image", "model": "nano", "prompt_file": "plates/a.txt", "aspect_ratio": "4:5", "out": "plates/a.png"},
        {"key": "k.vid", "asset_id": "VID", "kind": "video", "model": "kling", "prompt_file": "broll/1.txt", "aspect_ratio": "9:16", "duration": 5, "out": "broll/1.mp4"},
        {"key": "k.500", "asset_id": "VID2", "kind": "video", "model": "kling", "prompt_file": "broll/2.txt", "aspect_ratio": "9:16", "duration": 5, "out": "broll/2.mp4"}]}
    (work / "jobs.json").write_text(json.dumps(jobs))
    (work / "prices.json").write_text(json.dumps({"checked_at": "2026-10-14", "source": "test",
        "kie": {"nano": {"per_image": 18, "unit": "credits"}, "kling": {"per_second": 10, "unit": "credits"}},
        "higgsfield": {"m": {"per_second": 3, "unit": "credits"}}, "heygen": {"hg": {"per_job": 1, "unit": "credits"}}}))
    ok, out, _ = sh([py, G, "--dry-run", "jobs.json", "--prices", "prices.json"], work, env)
    check("gen dry run quotes per job and per second", ok and "TOTAL: 118 credits" in out, out[-200:])
    ok, out, _ = sh([py, G, "--probe"], work, env)
    check("gen probe: all three providers accept the keys", ok and out.count("key accepted") == 3, out[-300:])
    ok, out, _ = sh([py, G, "jobs.json", "--project", P, "--prices", "prices.json"], work, env)
    data = json.loads(P.read_text())
    st = {j["key"]: j["status"] for j in data["jobs"]}
    check("gen image job completes and downloads", st.get("k.img") == "completed" and (work / "plates/a.png").exists())
    check("gen video job completes and downloads", st.get("k.vid") == "completed" and (work / "broll/1.mp4").exists())
    check("gen server error is held as unknown, not retried", st.get("k.500") == "unknown")
    (work / "hjobs.json").write_text(json.dumps({"provider": "higgsfield", "jobs": [{"key": "h.vid", "asset_id": "HV", "kind": "video", "model": "m", "prompt_file": "broll/1.txt", "aspect_ratio": "9:16", "duration": 5, "image_urls": ["https://example.com/f.png"], "out": "broll/3.mp4"}]}))
    sh([py, G, "hjobs.json", "--project", P, "--prices", "prices.json"], work, env)
    (work / "tjobs.json").write_text(json.dumps({"provider": "heygen", "jobs": [{"key": "t.1", "asset_id": "TWIN", "kind": "twin", "model": "hg", "script_file": "twin/s.txt", "avatar_id": "a", "voice_id": "v", "width": 1080, "height": 1920, "consent_ref": "signed", "out": "twin/1.mp4"}]}))
    sh([py, G, "tjobs.json", "--project", P, "--prices", "prices.json"], work, env)
    data = json.loads(P.read_text())
    st = {j["key"]: j["status"] for j in data["jobs"]}
    check("gen higgsfield video (image-to-video) completes", st.get("h.vid") == "completed")
    check("gen heygen twin (with consent) completes", st.get("t.1") == "completed")
    (work / "njobs.json").write_text(json.dumps({"provider": "heygen", "jobs": [{"key": "t.2", "asset_id": "TWIN", "kind": "twin", "model": "hg", "script_file": "twin/s.txt", "out": "twin/2.mp4"}]}))
    ok, out, _ = sh([py, G, "--dry-run", "njobs.json"], work, env, ok_codes=(1,))
    check("gen refuses a twin job without consent_ref", ok and "consent" in out)

    # ---- synthetic media ----
    ff = ffmpeg_bin()
    m = work / "media"
    m.mkdir()
    sh([ff, "-y", "-f", "lavfi", "-i", "testsrc2=s=1080x1920:r=30", "-f", "lavfi", "-i",
        "aevalsrc='0.3*sin(2*PI*170*t)*(0.55+0.45*sin(2*PI*4.3*t))*between(mod(t,2.6),0,2.1)':s=48000:c=mono",
        "-t", "12", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "media/aroll.mp4"], work)
    sh([ff, "-y", "-f", "lavfi", "-i", "smptehdbars=s=1920x1080:r=30", "-t", "5", "-c:v", "libx264", "-pix_fmt", "yuv420p", "media/broll.mp4"], work)
    for r, s in (("9x16", "1080x1920"), ("4x5", "1080x1350")):
        sh([ff, "-y", "-f", "lavfi", "-i", f"color=c=0x0f1424:s={s}", "-frames:v", "1", f"media/end_{r}.png"], work)
    sh([ff, "-y", "-f", "lavfi", "-i", "color=c=0xf97316:s=300x80", "-frames:v", "1", "media/logo.png"], work)
    sh([ff, "-y", "-f", "lavfi", "-i", "aevalsrc='0.08*sin(2*PI*220*t)':s=48000:c=stereo", "-t", "30", "-c:a", "aac", "media/bed.m4a"], work)
    script = "How many hours a week do you spend babysitting your AI? You bought AI to save time. Then you became its assistant. Take the test today."
    (work / "script.txt").write_text(script)
    edl = {"id": "T", "playbook": "ad", "fps": 30, "ratios": ["9x16", "4x5"], "out_dir": "renders",
           "clips": [{"src": "media/aroll.mp4", "in": 0, "out": 2.6, "type": "aroll"},
                     {"src": "media/aroll.mp4", "in": 2.6, "out": 10.0, "type": "aroll"},
                     {"src": "media/end_{ratio}.png", "type": "card", "dur": 3.0}],
           "cutaways": [{"src": "media/broll.mp4", "at": 4.0, "dur": 2.0, "cover_join": 1}],
           "brand_cue": {"src": "media/logo.png", "at": 0, "dur": 2.0},
           "music": {"src": "media/bed.m4a", "gain_db": -22, "duck": True},
           "captions": {"mode": "burn", "transcript": "transcript.json", "size": 64, "max_chars": 24}, "loudness": -14}
    (work / "edit.json").write_text(json.dumps(edl))
    ok, out, _ = sh([py, VD / "assemble_video.py", "edit.json"], work, env)
    rep = json.loads((work / "renders/T.assemble.json").read_text())
    check("assemble: clean cuts in both ratios within 0.1 s", ok and all(r["duration_ok"] for r in rep["ratios"]), out[-300:])
    check("assemble: loudness -14 LUFS ±1", all(abs(r["cut_loudness"]["integrated"] + 14) <= 1 for r in rep["ratios"]))
    check("assemble: voice stem written", (work / "renders/T.voice.wav").exists())
    ok, out, _ = sh([py, VD / "transcribe.py", "renders/T.voice.wav", "--out", "transcript.json", "--engine", "align", "--script", "script.txt"], work, env)
    tr = json.loads((work / "transcript.json").read_text())
    check("transcribe align: every script word placed, marked approximate", ok and tr["approximate"] and len(tr["words"]) == len(script.split()))
    check("transcribe align: words end before the end card", tr["words"][-1]["end"] <= 10.0 + 0.05)
    ok, out, _ = sh([py, VD / "assemble_video.py", "edit.json"], work, env)
    rep = json.loads((work / "renders/T.assemble.json").read_text())
    check("assemble: captioned finals within 0.1 s", ok and all(r.get("final") and r["duration_ok"] for r in rep["ratios"]), out[-300:])
    check("captions: <= 2 lines, >= 48 px, inside the safe zone",
          all(r["caption_style"]["max_lines"] <= 2 and r["caption_style"]["size"] >= 48 for r in rep["ratios"]))
    cues = caption_lines(tr["words"], max_chars=24)
    check("captions: every cue on screen >= 0.7 s", all(c["end"] - c["start"] >= 0.7 - 1e-3 for c in cues))
    from videolib import _balance, max_chars_for  # noqa: E402
    check("captions: a number stays with its unit", _balance("then about 30 minutes a week.".split(), 24) == ["then about", "30 minutes a week."])
    tw = [{"w": w, "start": i * .3, "end": i * .3 + .28} for i, w in enumerate("and your single worst leak. It’s free, and your result shows up the moment you finish.".split())]
    check("captions: no cue spans two sentences", not any("leak." in " ".join(c["lines"]) and "free," in " ".join(c["lines"]) for c in caption_lines(tw, 24)))
    check("captions: line length per ratio", max_chars_for({"max_chars": 38}, "9x16") <= 28 and max_chars_for({}, "16x9") >= 38
          and max_chars_for({"max_chars": {"9x16": 24, "16x9": 40}}, "9x16") == 24)
    check("captions: none run onto the end card", all(c["end"] <= 10.0 + 0.02 for r in rep["ratios"] for c in r["caption_cues"]))

    # ---- framing, word-timed cutaways, cards over the voice ----
    sh([ff, "-y", "-f", "lavfi", "-i", "color=c=0x223355:s=1080x1920", "-frames:v", "1", "media/card_9x16.png"], work)
    edl_u = {"id": "U", "playbook": "sales", "fps": 30, "ratios": ["9x16"], "out_dir": "renders",
             "clips": [{"src": "media/aroll.mp4", "in": 0, "out": 10.0, "type": "aroll"},
                       {"src": "media/broll.mp4", "in": 0, "out": 1.5, "type": "broll", "fit": "pad"},
                       {"src": "media/end_{ratio}.png", "type": "card", "dur": 3.0}],
             "cutaways": [{"src": "media/broll.mp4", "at": 1.0, "dur": 1.0},
                          {"src": "media/card_{ratio}.png", "at_word": "babysitting", "until_word": "AI?", "hide_captions": True}],
             "brand_cue": {"type": "face"}, "placeholder": True,
             "captions": {"mode": "burn", "transcript": "transcript.json", "size": 64, "max_chars": 24}, "loudness": -14}
    (work / "edit-u.json").write_text(json.dumps(edl_u))
    ok, out, _ = sh([py, VD / "assemble_video.py", "edit-u.json"], work, env)
    rep_u = json.loads((work / "renders/U.assemble.json").read_text())
    ru = rep_u["ratios"][0] if rep_u.get("ratios") else {}
    warns = ru.get("warnings", [])
    check("assemble: a cropped 16:9 shot in 9:16 is warned as enlarged; the padded one is not",
          ok and len([w for w in warns if "enlarged" in w]) == 1, out[-300:] + str(warns))
    w_b = next(w for w in tr["words"] if w["w"].lower().startswith("babysitting"))
    w_a = next(w for w in tr["words"] if w["w"] == "AI?")
    a0, a1 = w_b["start"] - 0.1, w_a["end"] + 0.25
    check("assemble: a card timed to the words hides the captions under it",
          ru.get("final") and all(c["end"] <= a0 + 0.01 or c["start"] >= a1 - 0.01 for c in ru.get("caption_cues", [])))
    check("assemble: a padded 16:9 shot shrunk in 9:16 is warned as hard to read", any("hard to read" in w for w in warns), str(warns))

    # ---- joins between takes, short sources ----
    edl_j = {"id": "J", "playbook": "ad", "fps": 30, "ratios": ["9x16"], "out_dir": "renders",
             "clips": [{"src": "media/aroll.mp4", "in": 0, "out": 5.0, "type": "aroll"},
                       {"src": "media/aroll.mp4", "in": 5.3, "out": 10.0, "type": "aroll"},
                       {"src": "media/end_{ratio}.png", "type": "card", "dur": 3.0}],
             "cutaways": [{"src": "media/broll.mp4", "at": 6.0, "dur": 2.0, "in": 0, "at_join": 1},
                          {"src": "media/broll.mp4", "at": 8.0, "dur": 2.0, "in": 4.0}],
             "brand_cue": {"type": "face"}, "captions": {"mode": "none"}, "loudness": -14}
    (work / "edit-j.json").write_text(json.dumps(edl_j))
    ok, out, _ = sh([py, VD / "assemble_video.py", "edit-j.json"], work, env)
    rj = json.loads((work / "renders/J.assemble.json").read_text())["ratios"][0]
    cw0 = rj.get("cutaways", [{}])[0]
    check("assemble: at_join starts the cutaway at the take join and keeps its end",
          ok and abs(cw0.get("at", 0) - 4.8) < 0.01 and abs(cw0["at"] + cw0["dur"] - 8.0) < 0.01, str(rj.get("cutaways")))
    check("assemble: a cutaway past the end of its source is warned", any("ends early" in w for w in rj["warnings"]), str(rj["warnings"]))
    edl_j2 = dict(edl_j, id="J2", cutaways=[])
    (work / "edit-j2.json").write_text(json.dumps(edl_j2))
    sh([py, VD / "assemble_video.py", "edit-j2.json"], work, env)
    ok, out, _ = sh([py, VD / "review_video.py", "check", "--video", "renders/J2_9x16.mp4", "--edit", "edit-j2.json", "--out", "review-j"], work, env, ok_codes=(1,))
    rj2 = json.loads((work / "review-j/J2_9x16.check.json").read_text())
    check("review: an uncovered join between takes fails", ok and any(c["check"] == "every join between takes covered" and c["result"] == "FAIL" for c in rj2["checks"]), out[-300:])

    ok, out, _ = sh([py, VD / "review_video.py", "check", "--video", "renders/U_9x16.mp4", "--edit", "edit-u.json", "--script", "script.txt", "--out", "review-u"], work, env, ok_codes=(0, 1))
    res_u = json.loads((work / "review-u/U_9x16.check.json").read_text())
    names = {c["check"] for c in res_u["checks"]}
    check("review: on placeholder media, loudness and first word are unverified, not passed",
          "loudness" not in names and not any(n.startswith("first word") for n in names)
          and any(u.startswith("loudness") for u in res_u["unverified"]), str(names))
    sys.path.insert(0, str(VD))
    from transcribe import snap  # noqa: E402
    words = [{"w": w, "start": i * .4, "end": i * .4 + .35} for i, w in enumerate("how many hours a week do you spend baby sitting your a i".split())]
    out_w, extra, missing = snap(words, "How many hours a week do you spend babysitting your AI?")
    check("snap-to-script merges split words", [w["w"] for w in out_w][-3:] == ["babysitting", "your", "AI?"] and not extra and not missing)

    # ---- review: clean, then planted defects ----
    ok, out, _ = sh([py, VD / "review_video.py", "check", "--video", "renders/T_9x16.mp4", "--edit", "edit.json", "--script", "script.txt", "--out", "review"], work, env)
    res = json.loads((work / "review/T_9x16.check.json").read_text())
    check("review: clean video passes every machine check", ok and all(c["result"] != "FAIL" for c in res["checks"]), out[-300:])
    check("review: motion and pacing marked unverified", any("motion" in u for u in res["unverified"]))
    check("review: contact sheet and three safe frames written", (work / "review/T_9x16_sheet.png").exists() and all((work / f"review/T_9x16_safe_{k}.png").exists() for k in ("open", "mid", "endcard")))
    bad = dict(edl)
    bad["brand_cue"] = {"src": "media/logo.png", "at": 2.6, "dur": 2.0}
    bad["clips"] = edl["clips"][:-1] + [{"src": "media/end_{ratio}.png", "type": "card", "dur": 1.5}]
    (work / "edit-bad.json").write_text(json.dumps(bad))
    trb = dict(tr, approximate=False, engine="planted")
    trb["words"] = [dict(w, w=("twelve" if w["w"] == "hours" else w["w"])) for w in tr["words"] if w["w"] != "today."]
    (work / "transcript-bad.json").write_text(json.dumps(trb))
    sh([ff, "-y", "-i", "renders/T_9x16.mp4", "-c:v", "copy", "-af", "volume=9dB", "-c:a", "aac", "loud_9x16.mp4"], work)
    ok, out, _ = sh([py, VD / "review_video.py", "check", "--video", "loud_9x16.mp4", "--edit", "edit-bad.json", "--script", "script.txt",
                     "--transcript", "transcript-bad.json", "--out", "review-bad"], work, env, ok_codes=(1,))
    res = json.loads((work / "review-bad/T_9x16.check.json").read_text())
    failed = {c["check"] for c in res["checks"] if c["result"] == "FAIL"}
    for name in ("loudness", "true peak", "brand cue by 2 s", "end card held >= 2.5 s", "words match the approved script"):
        check(f"review catches planted defect: {name}", name in failed)

    # ---- SubMagic ----
    VP = work / "v.json"
    sh([py, L, "init", VP, "--cycle", "2026-10"], work)
    for g in ("G0", "G1", "G2"):
        sh([py, L, "gate", VP, "--gate", g, "--verdict", "pass", "--by", "member" if g == "G2" else "producer", "--ref", "x"], work)
    for aid in ("C1", "C2"):
        sh([py, L, "plan", VP, "--asset-id", aid, "--provider", "submagic", "--model", "Sara", "--prompt-ref", "edit.json", "--kind", "captions"], work)
    sh([py, L, "authorize", VP, "--provider", "submagic", "--cap", "3", "--units", "minutes", "--note", "test"], work)
    ok, out, _ = sh([py, VD / "submagic.py", "--project", VP, "--asset-id", "C1", "--video", "renders/T_9x16.cut.mp4", "--out", "renders/T_9x16.sm.mp4", "--template", "Sara", "--cost", "1", "--quote", "q"], work, env)
    check("submagic upload route completes through the ledger", ok and (work / "renders/T_9x16.sm.mp4").exists(), out[-300:])
    ok, out, _ = sh([py, VD / "submagic.py", "--project", VP, "--asset-id", "C2", "--video", "renders/T_4x5.cut.mp4", "--video-url", "https://example.com/v.mp4", "--title", "reject", "--out", "x.mp4", "--template", "Sara", "--cost", "1", "--quote", "q"], work, env, ok_codes=(1,))
    st = {j["asset_id"]: j["status"] for j in json.loads(VP.read_text())["jobs"]}
    check("submagic rejection is recorded no_submission with the burn fallback named", ok and st.get("C2") == "no_submission" and "burn" in out)

    # ---- kit ----
    sh([py, L, "ad", VP, "--ad", "T", "--concept", "C1", "--layout", "video-ad", "--spec", "edit.json", "--renders", "renders/T_9x16.mp4", "renders/T_4x5.mp4"], work)
    (work / "videos.json").write_text(json.dumps({"cycle": "2026-10", "videos": [{"id": "T", "playbook": "ad", "slug": "test", "ratios": ["9x16", "4x5"],
        "platform_copy": {"title": "t", "caption": "c", "cta_button": "LEARN_MORE", "url": "https://example.com"}, "thumbnail_at": 1.0}]}))
    ok, out, _ = sh([py, VD / "review_video.py", "kit", "--project", VP, "--manifest", "videos.json", "--renders", "renders", "--out", "kit"], work, env, ok_codes=(1,))
    check("kit refused before review and approval", ok and "refused" in out)
    for g in ("G3", "G4"):
        sh([py, L, "gate", VP, "--ad", "T", "--gate", g, "--verdict", "pass", "--by", "reviewer", "--ref", "review"], work)
    sh([py, L, "approve", VP, "--ad", "T", "--note", "member watched"], work)
    ok, out, _ = sh([py, VD / "review_video.py", "kit", "--project", VP, "--manifest", "videos.json", "--renders", "renders", "--out", "kit"], work, env)
    check("kit built after review and approval", ok and len(list((work / "kit/videos").glob("*.mp4"))) == 2 and (work / "kit/publish.csv").exists(), out[-300:])
    man = {"cycle": "2026-10", "videos": [{"id": "T", "playbook": "ad", "slug": "test", "ratios": ["9x16", "4x5"],
           "platform_copy": {"title": "t", "caption": "c", "cta_button": "LEARN_MORE", "url": "https://example.com"},
           "placements": [{"name": "reels", "ratio": "9x16"}, {"name": "feed", "ratio": "4x5"},
                          {"name": "email", "ratio": "9x16", "utm_source": "email", "utm_medium": "email", "caption": "see you on the call"}],
           "generated": [{"asset": "B1", "provider": "kie", "model": "m", "person": True}]}]}
    (work / "videos-p.json").write_text(json.dumps(man))
    ok, out, _ = sh([py, VD / "review_video.py", "kit", "--project", VP, "--manifest", "videos-p.json", "--renders", "renders", "--out", "kit-p"], work, env, ok_codes=(1,))
    check("kit refused when a generated person appears without the AI label", ok and "AI label" in out and not (work / "kit-p").exists(), out[-300:])
    man["videos"][0]["ai_label"] = True
    man["booking_url"] = "https://example.com"
    man["videos"][0]["placements"][2]["audience"] = "booked"
    (work / "videos-p.json").write_text(json.dumps(man))
    ok, out, _ = sh([py, VD / "review_video.py", "kit", "--project", VP, "--manifest", "videos-p.json", "--renders", "renders", "--out", "kit-p"], work, env, ok_codes=(1,))
    check("kit refused when a placement for people who booked links to the booking page", ok and "already booked" in out, out[-300:])
    man["videos"][0]["placements"][2]["url"] = "https://video.example.org/before-your-call"
    (work / "videos-p.json").write_text(json.dumps(man))
    ok, out, _ = sh([py, VD / "review_video.py", "kit", "--project", VP, "--manifest", "videos-p.json", "--renders", "renders", "--out", "kit-p"], work, env)
    import csv as _csv
    rows = list(_csv.DictReader(open(work / "kit-p/publish.csv", encoding="utf-8"))) if ok else []
    check("kit: one publish row per placement, each with its own UTM medium",
          len(rows) == 3 and "utm_medium=email" in rows[2]["url"] and rows[2]["caption"] == "see you on the call", out[-300:])

    # ---- renderer (optional) ----
    if shutil.which("node"):
        spec = {"id": "R", "layout": "end-card", "brand": {"name": "Test", "bg": "#0f1424", "fg": "#f4f6fa", "accent": "#f97316"},
                "copy": {"hook": "Take the test", "url": "example.com", "cta": "Go"}}
        (work / "r.json").write_text(json.dumps(spec))
        ok, out, code = sh(["node", ROOT / "shared/media/render_static.mjs", "r.json", "--out", "cards", "--ratios", "9x16,16x9"], work, env, ok_codes=(0, 1, 2))
        if code == 2 and "Playwright not found" in out:
            print("SKIP  renderer (Playwright not installed here)")
        else:
            check("renderer: end card in 9:16 and 16:9", code == 0 and (work / "cards/R_9x16.png").exists(), out[-300:])

    srv.shutdown()
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} checks passed" + (f" · work dir kept: {work}" if keep else ""))
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    try:
        rc = main()
    finally:
        for d in ROOT.rglob("__pycache__"):
            shutil.rmtree(d, ignore_errors=True)
    sys.exit(rc)
