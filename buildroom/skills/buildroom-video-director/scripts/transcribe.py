#!/usr/bin/env python3
"""Video Director transcription: word-timed transcript of a cut, for captions and review.

Engines, tried in this order with --engine auto:
  faster-whisper   local, free     pip install faster-whisper
  whisper          local, free     pip install openai-whisper
  openai           API, paid       OPENAI_API_KEY in .env (whisper-1, word timestamps)
  align            no speech model: spreads the approved script's words over the detected speech in
                   the audio. Timings are approximate and labelled so; never the default.

--snap-to-script script.txt keeps the engine's timings but replaces the recognised words with the
approved script's words wherever the two line up, so captions carry the approved wording (curly
quotes, numbers, brand names) instead of the recogniser's guesses. Words the speaker said that are not
in the script are kept and listed, so the reviewer sees every departure.

Usage
  transcribe.py renders/V1_9x16.cut.mp4 --out transcript.json [--engine auto|faster-whisper|whisper|openai]
                [--snap-to-script script.txt] [--language en]
  transcribe.py renders/V1_9x16.cut.mp4 --out transcript.json --engine align --script script.txt
"""
import argparse, difflib, json, os, re, sys, tempfile, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from videolib import ffmpeg_bin, run, silences, probe, norm_words  # noqa: E402


def load_dotenv():
    for d in [Path.cwd(), *Path.cwd().parents][:4]:
        f = d / ".env"
        if f.is_file():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return


def extract_wav(src, tmp):
    wav = Path(tmp) / "audio.wav"
    run([ffmpeg_bin(), "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    return wav


def eng_faster_whisper(wav, lang):
    from faster_whisper import WhisperModel
    model = WhisperModel(os.environ.get("WHISPER_MODEL", "small"), compute_type="int8")
    segs, _ = model.transcribe(str(wav), language=lang, word_timestamps=True)
    return [{"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in segs for w in (s.words or [])]


def eng_whisper(wav, lang):
    import whisper
    model = whisper.load_model(os.environ.get("WHISPER_MODEL", "small"))
    r = model.transcribe(str(wav), language=lang, word_timestamps=True)
    return [{"w": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)}
            for s in r["segments"] for w in s.get("words", [])]


def eng_openai(wav, lang):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    boundary = uuid.uuid4().hex
    parts = []
    for name, val in (("model", "whisper-1"), ("response_format", "verbose_json"),
                      ("timestamp_granularities[]", "word"), ("language", lang)):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}\r\n".encode())
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"audio.wav\"\r\n"
                 f"Content-Type: audio/wav\r\n\r\n".encode() + Path(wav).read_bytes() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/")
    req = urllib.request.Request(base + "/v1/audio/transcriptions", data=b"".join(parts), method="POST",
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.loads(r.read())
    return [{"w": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)} for w in d.get("words", [])]


def eng_align(src, script_text):
    """Spread the script's words over the speech regions (the gaps between silences), in order,
    in proportion to each word's length. Approximate by construction; run it on the voice stem
    (<id>.voice.wav from assemble_video.py), not on a mix with music."""
    dur = probe(src)["duration"] or 0
    quiet = [(s, e if e is not None else dur) for s, e in silences(src, noise="-38dB", min_d=0.25)]
    speech, t = [], 0.0
    for s, e in sorted(quiet):
        if s - t > 0.15:
            speech.append((t, s))
        t = max(t, e)
    if dur - t > 0.15:
        speech.append((t, dur))
    words = script_text.split()
    if not speech or not words:
        return []
    total = sum(e - s for s, e in speech)
    weights = [len(w) + 2 for w in words]
    scale = total / sum(weights)

    def at(pos):  # position on the concatenated speech timeline → real time
        for s, e in speech:
            if pos <= (e - s) + 1e-9:
                return s + pos
            pos -= (e - s)
        return speech[-1][1]
    out, acc = [], 0.0
    for w, wt in zip(words, weights):
        a0, a1 = acc * scale, (acc + wt) * scale
        st, en = at(a0 + 1e-6), at(a1)
        if en <= st:  # a word straddling a pause ends at its region's end
            en = st + min(wt * scale, 0.4)
        out.append({"w": w, "start": round(st, 3), "end": round(en, 3)})
        acc += wt
    return out


def snap(words, script_text):
    """Keep timings, take the approved wording where recognised and approved words line up."""
    script_words = script_text.split()
    a = [norm_words(w["w"])[0] if norm_words(w["w"]) else "" for w in words]
    b = [norm_words(w)[0] if norm_words(w) else "" for w in script_words]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    out, extra, missing = [], [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out.append({**words[i1 + k], "w": script_words[j1 + k]})
        elif tag == "replace" and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                out.append({**words[i1 + k], "w": script_words[j1 + k], "snapped_from": words[i1 + k]["w"]})
        elif tag == "replace" and "".join(a[i1:i2]) == "".join(b[j1:j2]):
            # same letters, split differently ("baby sitting" / "babysitting", "a i" / "AI"): spread the
            # approved words over the recognised span
            t0, t1 = words[i1]["start"], words[i2 - 1]["end"]
            n = j2 - j1
            for k in range(n):
                out.append({"w": script_words[j1 + k], "start": round(t0 + (t1 - t0) * k / n, 3),
                            "end": round(t0 + (t1 - t0) * (k + 1) / n, 3),
                            "snapped_from": " ".join(w["w"] for w in words[i1:i2])})
        else:
            for k in range(i1, i2):
                out.append(words[k])
                extra.append(words[k]["w"])
            missing += script_words[j1:j2]
    return out, extra, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media")
    ap.add_argument("--out", required=True)
    ap.add_argument("--engine", default="auto", choices=["auto", "faster-whisper", "whisper", "openai", "align"])
    ap.add_argument("--script", help="approved script (required for --engine align)")
    ap.add_argument("--snap-to-script")
    ap.add_argument("--language", default="en")
    a = ap.parse_args()
    load_dotenv()
    src = Path(a.media)
    result = {"source": src.name, "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "approximate": False}
    if a.engine == "align":
        if not a.script:
            raise SystemExit("--engine align needs --script (the approved script)")
        result["engine"] = "align"
        result["approximate"] = True
        result["words"] = eng_align(src, Path(a.script).read_text(encoding="utf-8"))
        result["note"] = "Timings spread over detected speech, not recognised. Check the captions by eye; use a speech engine for exact timing."
    else:
        engines = ["faster-whisper", "whisper", "openai"] if a.engine == "auto" else [a.engine]
        fns = {"faster-whisper": eng_faster_whisper, "whisper": eng_whisper, "openai": eng_openai}
        errors = {}
        with tempfile.TemporaryDirectory() as tmp:
            wav = extract_wav(src, tmp)
            for e in engines:
                try:
                    result["words"] = fns[e](wav, a.language)
                    result["engine"] = e
                    break
                except Exception as ex:  # module missing, key missing, network
                    errors[e] = f"{type(ex).__name__}: {str(ex)[:160]}"
        if "words" not in result:
            raise SystemExit("no transcription engine available: " + "; ".join(f"{k}: {v}" for k, v in errors.items()) +
                             "\nInstall one (pip install faster-whisper), add OPENAI_API_KEY to .env, or use --engine align --script script.txt (approximate).")
        if a.snap_to_script:
            result["words"], result["extra_words"], result["missing_words"] = snap(result["words"], Path(a.snap_to_script).read_text(encoding="utf-8"))
            result["snapped_to"] = Path(a.snap_to_script).name
    result["text"] = " ".join(w["w"] for w in result["words"])
    Path(a.out).write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{result['engine']}: {len(result['words'])} words → {a.out}" + ("  (approximate timing)" if result["approximate"] else ""))
    if result.get("extra_words") or result.get("missing_words"):
        print(f"  said but not in the script: {result.get('extra_words')}\n  in the script but not heard: {result.get('missing_words')}")


if __name__ == "__main__":
    main()
