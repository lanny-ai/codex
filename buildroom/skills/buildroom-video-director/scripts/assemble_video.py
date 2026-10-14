#!/usr/bin/env python3
"""Video Director assembly: an edit decision list (edit.json) in, platform-ready cuts out.

For each ratio in the EDL:
  1. every clip is trimmed, scaled and cropped (cover, with a focus point) to the frame, at one
     frame rate, with stereo 48 kHz audio (silence where a clip has none or is muted);
  2. the clips are joined; cutaways (B-roll laid over continuous voice, which is how the director
     makes L and J cuts) and the brand cue are overlaid; music is mixed under the voice and ducked;
  3. loudness is normalised in two passes to -14 LUFS integrated, -1 dBTP true peak;
  4. captions: "burn" sets them from the transcript in the brand font inside the safe zone;
     "submagic" leaves a clean cut for scripts/submagic.py; "none" ships the clean cut.

Every command, input checksum and output measurement goes into <id>.assemble.json, the audit log.
The same inputs always give the same output.

Usage
  assemble_video.py edit.json                 build the clean cut(s) and, if a transcript exists, the captioned final(s)
  assemble_video.py edit.json --ratios 9x16   only some ratios
  assemble_video.py edit.json --plan          print what would be built (durations, overlays), build nothing

Typical flow: assemble (clean cut + <id>.voice.wav, the voice alone) → transcribe.py on the voice stem →
assemble again (captions burn), or submagic.py on the clean cut.

edit.json (paths relative to it; "{ratio}" in a path is replaced, e.g. cards/end_{ratio}.png)
  {"id": "V1-C1H1", "playbook": "ad", "fps": 30, "ratios": ["9x16", "4x5"], "out_dir": "renders",
   "clips": [
     {"src": "footage/hook.mp4", "in": 0.4, "out": 3.1, "type": "aroll", "focus": "50% 35%"},
     {"src": "footage/body.mp4", "in": 1.0, "out": 14.2, "type": "aroll"},
     {"src": "cards/end_{ratio}.png", "type": "card", "dur": 3.0}],
   "cutaways": [{"src": "broll/desk.mp4", "at": 5.0, "dur": 2.4, "in": 0.0, "focus": "50% 50%"}],
   "brand_cue": {"src": "brand/logo.png", "at": 0, "dur": 2.0, "position": "top-left", "width_frac": 0.26},
   "music": {"src": "music/bed.mp3", "gain_db": -20, "duck": true},
   "captions": {"mode": "burn", "transcript": "transcript.json", "font": "Source Sans 3", "fontsdir": "brand/fonts",
                "size": 64, "color": "#FFFFFF", "box": "#0F1424", "box_alpha": 0.6, "max_chars": 26},
   "loudness": -14}
  brand_cue may instead be {"type": "face"} when the member's face opens the first clip.
"""
import argparse, hashlib, json, shutil, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from videolib import (RATIOS, SAFE, LOUDNESS_TARGET, TRUE_PEAK, ffmpeg_bin, run, probe, loudness,  # noqa: E402
                      load_json, caption_lines, write_srt)

V_ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high"]
SEG_ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p"]
A_ENC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def focus_xy(focus):
    try:
        fx, fy = [float(x.strip().rstrip("%")) / 100 for x in (focus or "50% 50%").split()]
    except ValueError:
        fx, fy = .5, .5
    return min(max(fx, 0), 1), min(max(fy, 0), 1)


def cover(W, H, focus):
    fx, fy = focus_xy(focus)
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})*{fy},setsar=1")


def resolve(base, src, ratio):
    p = (base / src.replace("{ratio}", ratio)).resolve()
    if not p.exists():
        raise SystemExit(f"missing input: {p}")
    return p


def clip_duration(c):
    if c.get("type") == "card" or str(c.get("src", "")).lower().endswith((".png", ".jpg", ".jpeg")):
        return float(c["dur"])
    return float(c["out"]) - float(c.get("in", 0))


def segment(c, src, W, H, fps, out, log):
    """One clip → one normalised segment with audio."""
    ff = ffmpeg_bin()
    dur = clip_duration(c)
    if dur <= 0:
        raise SystemExit(f"clip {c.get('src')}: out must be after in")
    still = c.get("type") == "card" or src.suffix.lower() in (".png", ".jpg", ".jpeg")
    if still:
        cmd = [ff, "-y", "-loop", "1", "-framerate", str(fps), "-t", f"{dur:.3f}", "-i", str(src),
               "-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
               "-filter_complex", f"[0:v]{cover(W, H, c.get('focus'))},fps={fps},format=yuv420p[v]",
               "-map", "[v]", "-map", "1:a"]
    else:
        has_audio = probe(src).get("acodec") is not None
        keep_audio = has_audio and c.get("audio", "source" if c.get("type", "aroll") == "aroll" else "mute") == "source"
        cmd = [ff, "-y", "-ss", f"{float(c.get('in', 0)):.3f}", "-t", f"{dur:.3f}", "-i", str(src)]
        if keep_audio:
            fc = (f"[0:v]{cover(W, H, c.get('focus'))},fps={fps},format=yuv420p[v];"
                  f"[0:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{dur:.3f}[a]")
            cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]"]
        else:
            cmd += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
                    "-filter_complex", f"[0:v]{cover(W, H, c.get('focus'))},fps={fps},format=yuv420p[v]",
                    "-map", "[v]", "-map", "1:a"]
    cmd += ["-t", f"{dur:.3f}", *SEG_ENC, *A_ENC, str(out)]
    run(cmd, log)
    return dur


def ass_color(hex_rgb, alpha=0.0):
    h = hex_rgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    a = int(round(alpha * 255))
    return f"&H{a:02X}{b}{g}{r}".upper()


def write_ass(cues, cap, ratio, path):
    W, H = RATIOS[ratio]
    s = SAFE[ratio]
    size = max(48, int(cap.get("size", 64)))
    margin_v = int(H * s["b"]) + 24
    margin_lr = int(W * s["s"]) + 20
    style = (f"Style: Default,{cap.get('font', 'Arial')},{size},{ass_color(cap.get('color', '#FFFFFF'))},"
             f"{ass_color(cap.get('color', '#FFFFFF'))},{ass_color(cap.get('box', '#000000'), 1 - float(cap.get('box_alpha', .6)))},"
             f"{ass_color(cap.get('box', '#000000'), 1 - float(cap.get('box_alpha', .6)))},-1,0,0,0,100,100,0,0,3,14,0,2,"
             f"{margin_lr},{margin_lr},{margin_v},1")
    def t(x):
        cs = int(round(x * 100))
        return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"
    nl = chr(92) + "N"  # the ASS line break, \N
    events = [f"Dialogue: 0,{t(c['start'])},{t(c['end'])},Default,,0,0,0,,{nl.join(x.replace('{', '(').replace('}', ')') for x in c['lines'])}"
              for c in cues]
    Path(path).write_text("\n".join([
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        style, "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text", *events, ""]),
        encoding="utf-8")
    return {"size": size, "margin_v": margin_v, "margin_lr": margin_lr, "max_lines": max(len(c["lines"]) for c in cues) if cues else 0}


def build_ratio(edl, base, ratio, out_dir, report, plan_only=False):
    W, H = RATIOS[ratio]
    fps = int(edl.get("fps", 30))
    eid = edl["id"]
    clips = edl["clips"]
    expected = sum(clip_duration(c) for c in clips)
    entry = {"ratio": ratio, "width": W, "height": H, "fps": fps, "expected_duration": round(expected, 3),
             "commands": [], "inputs": {}}
    for c in clips + edl.get("cutaways", []):
        p = resolve(base, c["src"], ratio)
        entry["inputs"][str(p.relative_to(base) if base in p.parents else p)] = sha(p)
    if plan_only:
        entry["plan"] = {"clips": [(c["src"], round(clip_duration(c), 3)) for c in clips],
                         "cutaways": [(c["src"], c["at"], c["dur"]) for c in edl.get("cutaways", [])]}
        report["ratios"].append(entry)
        return
    log = entry["commands"]
    ff = ffmpeg_bin()
    with tempfile.TemporaryDirectory(prefix="assemble-") as tmp:
        tmp = Path(tmp)
        segs = []
        for i, c in enumerate(clips):
            seg = tmp / f"seg{i:03d}.mp4"
            segment(c, resolve(base, c["src"], ratio), W, H, fps, seg, log)
            segs.append(seg)
        (tmp / "list.txt").write_text("".join(f"file '{s.name}'\n" for s in segs))
        joined = tmp / "joined.mp4"
        run([ff, "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-c", "copy", str(joined)], log)
        voice = out_dir / f"{eid}.voice.wav"  # the voice alone, before music: for transcription and speech checks
        if not report.get("_voice_done"):  # once per run; the voice is the same in every ratio
            run([ff, "-y", "-i", str(joined), "-vn", "-ac", "1", "-ar", "16000", str(voice)], log)
            report["_voice_done"] = True
            report["voice_stem"] = str(voice.relative_to(base) if base in voice.parents else voice)

        # overlays + music in one pass
        inputs, fc, vlab = ["-i", str(joined)], [], "0:v"
        n = 1
        for k, cw in enumerate(edl.get("cutaways", [])):
            cseg = tmp / f"cut{k:02d}.mp4"
            segment({"src": cw["src"], "in": cw.get("in", 0), "out": float(cw.get("in", 0)) + float(cw["dur"]),
                     "type": "broll", "focus": cw.get("focus")}, resolve(base, cw["src"], ratio), W, H, fps, cseg, log)
            inputs += ["-i", str(cseg)]
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{float(cw['at']):.3f}/TB[c{k}]")
            fc.append(f"[{vlab}][c{k}]overlay=eof_action=pass:enable='between(t,{float(cw['at']):.3f},{float(cw['at']) + float(cw['dur']):.3f})'[v{k}]")
            vlab = f"v{k}"
            n += 1
        cue = edl.get("brand_cue") or {}
        if cue.get("src"):
            s = SAFE[ratio]
            lw = int(W * float(cue.get("width_frac", .26)))
            x = int(W * s["s"]) + 12 if "left" in cue.get("position", "top-left") else W - int(W * s["s"]) - 12 - lw
            y = int(H * s["t"]) + 12
            inputs += ["-loop", "1", "-i", str(resolve(base, cue["src"], ratio))]
            at, d = float(cue.get("at", 0)), float(cue.get("dur", 2))
            fc.append(f"[{n}:v]scale={lw}:-1,format=rgba[logo]")
            fc.append(f"[{vlab}][logo]overlay={x}:{y}:shortest=1:enable='between(t,{at:.3f},{at + d:.3f})'[vb]")
            vlab = "vb"
            n += 1
        alab = "0:a"
        music = edl.get("music")
        if music:
            inputs += ["-stream_loop", "-1", "-i", str(resolve(base, music["src"], ratio))]
            g = float(music.get("gain_db", -20))
            fc.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{expected:.3f},volume={g}dB[m]")
            if music.get("duck", True):
                fc.append("[0:a]asplit=2[voice][sc]")
                fc.append("[m][sc]sidechaincompress=threshold=0.015:ratio=10:attack=15:release=350[md]")
                fc.append("[voice][md]amix=inputs=2:duration=first:normalize=0[amix]")
            else:
                fc.append("[0:a][m]amix=inputs=2:duration=first:normalize=0[amix]")
            alab = "amix"
            n += 1
        raw = tmp / "raw.mp4"
        cmd = [ff, "-y", *inputs]
        maps = []
        if fc:
            cmd += ["-filter_complex", ";".join(fc)]
        maps += ["-map", f"[{vlab}]" if vlab != "0:v" else "0:v", "-map", f"[{alab}]" if alab != "0:a" else "0:a"]
        cmd += [*maps, "-t", f"{expected:.3f}", "-r", str(fps), *V_ENC, *A_ENC, str(raw)]
        run(cmd, log)

        # two-pass loudness normalisation; video stream copied
        target = float(edl.get("loudness", LOUDNESS_TARGET))
        p1 = run([ff, "-hide_banner", "-nostats", "-i", str(raw), "-vn", "-af",
                  f"loudnorm=I={target}:TP={TRUE_PEAK - 0.5}:LRA=11:print_format=json", "-f", "null", "-"], log)
        meas = json.loads(p1.stderr[p1.stderr.rfind("{"):p1.stderr.rfind("}") + 1])
        silent = float(meas.get("input_i", "-70")) < -60
        cut = out_dir / f"{eid}_{ratio}.cut.mp4"
        if silent:  # nothing to normalise (no speech, no music)
            run([ff, "-y", "-i", str(raw), "-c", "copy", "-movflags", "+faststart", str(cut)], log)
        else:
            af = (f"loudnorm=I={target}:TP={TRUE_PEAK - 0.5}:LRA=11:measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:"
                  f"measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}:offset={meas['target_offset']}:linear=true,"
                  f"aresample=48000")
            run([ff, "-y", "-i", str(raw), "-map", "0:v", "-map", "0:a", "-c:v", "copy", "-af", af, *A_ENC,
                 "-movflags", "+faststart", str(cut)], log)
        entry["cut"] = str(cut.relative_to(base) if base in cut.parents else cut)

        cap = edl.get("captions") or {"mode": "none"}
        final = out_dir / f"{eid}_{ratio}.mp4"
        mode = cap.get("mode", "none")
        entry["captions"] = mode
        if mode == "burn":
            tpath = base / cap.get("transcript", "transcript.json")
            if not tpath.exists():
                entry["final"] = None
                entry["next"] = f"run transcribe.py on {report.get('voice_stem')} (writes {tpath.name}), then assemble again to burn captions"
            else:
                tr = load_json(tpath)
                cues = caption_lines(tr["words"], max_chars=int(cap.get("max_chars", 26)))
                ass = tmp / "captions.ass"
                entry["caption_style"] = write_ass(cues, cap, ratio, ass)
                write_srt(cues, out_dir / f"{eid}.srt")
                vf = "subtitles=captions.ass"
                if cap.get("fontsdir"):
                    fd = (base / cap["fontsdir"]).resolve()
                    shutil.copytree(fd, tmp / "fonts", dirs_exist_ok=True)
                    vf += ":fontsdir=fonts"
                shutil.copy(cut, tmp / "cut.mp4")
                cmd = [ff, "-y", "-i", "cut.mp4", "-vf", vf, *V_ENC, "-c:a", "copy", "-movflags", "+faststart", "final.mp4"]
                log.append("(cwd=tmp) " + " ".join(cmd))
                import subprocess
                p = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)
                if p.returncode != 0:
                    raise RuntimeError("caption burn failed:\n" + "\n".join(p.stderr.splitlines()[-12:]))
                if "fontselect" in p.stderr and "fallback" in p.stderr.lower():
                    entry.setdefault("warnings", []).append("caption font fell back; put the brand font's TTF/OTF in fontsdir")
                shutil.move(str(tmp / "final.mp4"), final)
                entry["final"] = str(final.relative_to(base) if base in final.parents else final)
                entry["transcript_approximate"] = bool(tr.get("approximate"))
        elif mode == "submagic":
            entry["final"] = None
            entry["next"] = f"run submagic.py on {entry['cut']} (captions by SubMagic), or set captions.mode to burn"
        else:
            shutil.copy(cut, final)
            entry["final"] = str(final.relative_to(base) if base in final.parents else final)

    for key in ("cut", "final"):
        if entry.get(key):
            p = base / entry[key] if not Path(entry[key]).is_absolute() else Path(entry[key])
            entry[key + "_probe"] = probe(p)
            entry[key + "_loudness"] = loudness(p)
            entry[key + "_sha"] = sha(p)
    d = entry.get("final_probe", entry.get("cut_probe", {})).get("duration")
    entry["duration_ok"] = d is not None and abs(d - expected) <= 0.1
    report["ratios"].append(entry)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edit")
    ap.add_argument("--ratios")
    ap.add_argument("--plan", action="store_true")
    a = ap.parse_args()
    edl_path = Path(a.edit).resolve()
    base = edl_path.parent
    edl = load_json(edl_path)
    ratios = a.ratios.split(",") if a.ratios else edl.get("ratios", ["9x16"])
    for r in ratios:
        if r not in RATIOS:
            raise SystemExit(f"unknown ratio {r}; use {', '.join(RATIOS)}")
    out_dir = (base / edl.get("out_dir", "renders")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"id": edl["id"], "playbook": edl.get("playbook"), "edit": str(edl_path.name), "edit_sha": sha(edl_path), "ratios": []}
    for r in ratios:
        print(f"[{edl['id']} {r}] building …", flush=True)
        build_ratio(edl, base, r, out_dir, report, plan_only=a.plan)
        e = report["ratios"][-1]
        if a.plan:
            print(f"  expected {e['expected_duration']}s · clips {len(e['plan']['clips'])} · cutaways {len(e['plan']['cutaways'])}")
            continue
        lf = e.get("final_loudness") or e.get("cut_loudness") or {}
        print(f"  cut {e['cut']} · final {e.get('final') or '— ' + e.get('next', '')}\n"
              f"  duration {e.get('final_probe', e.get('cut_probe', {})).get('duration')}s (expected {e['expected_duration']}s, "
              f"{'ok' if e['duration_ok'] else 'OFF'}) · loudness {lf.get('integrated')} LUFS · true peak {lf.get('true_peak')} dBTP")
    rp = out_dir / f"{edl['id']}.assemble.json"
    report.pop("_voice_done", None)
    rp.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(f"report → {rp}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"assembly failed: {e}", file=sys.stderr)
        sys.exit(1)
