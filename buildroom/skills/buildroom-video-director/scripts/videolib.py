#!/usr/bin/env python3
"""Shared helpers for the Video Director scripts: find ffmpeg, probe media, measure loudness,
the ratio and safe-zone table, transcript I/O. Standard library only."""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

RATIOS = {"9x16": (1080, 1920), "4x5": (1080, 1350), "1x1": (1080, 1080), "16x9": (1920, 1080)}
# Fractions of the frame kept clear of platform interface. 9:16 follows the Reels overlay (14% top,
# 35% bottom, 6% sides), the strictest placement; verify against the platform's current guide.
SAFE = {"9x16": {"t": .14, "b": .35, "s": .06}, "4x5": {"t": .05, "b": .08, "s": .055},
        "1x1": {"t": .055, "b": .07, "s": .055}, "16x9": {"t": .06, "b": .1, "s": .05}}
LOUDNESS_TARGET, TRUE_PEAK = -14.0, -1.0


def ffmpeg_bin():
    """FFMPEG env, then PATH, then the imageio-ffmpeg wheel (pip install imageio-ffmpeg)."""
    for cand in (os.environ.get("FFMPEG"), shutil.which("ffmpeg")):
        if cand and Path(cand).exists():
            return cand
    try:
        import imageio_ffmpeg  # noqa
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    sys.exit("ffmpeg not found. Install it (macOS: brew install ffmpeg · Windows: winget install ffmpeg · "
             "any OS: pip install imageio-ffmpeg) or set FFMPEG to its path.")


def ffprobe_bin():
    cand = os.environ.get("FFPROBE") or shutil.which("ffprobe")
    return cand if cand and Path(cand).exists() else None


def run(cmd, log=None, check=True):
    """Run a command; keep the command line for the audit log."""
    if log is not None:
        log.append(" ".join(_q(c) for c in cmd))
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        tail = "\n".join(p.stderr.strip().splitlines()[-15:])
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(cmd[:6])} …\n{tail}")
    return p


def _q(s):
    s = str(s)
    return s if re.fullmatch(r"[\w./:=,+-]+", s) else "'" + s.replace("'", "'\\''") + "'"


def probe(path):
    """Duration, size, fps, codecs and audio presence. ffprobe if present, else ffmpeg's banner."""
    fp = ffprobe_bin()
    if fp:
        p = run([fp, "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)])
        d = json.loads(p.stdout)
        v = next((s for s in d["streams"] if s["codec_type"] == "video"), {})
        a = next((s for s in d["streams"] if s["codec_type"] == "audio"), {})
        num, _, den = (v.get("r_frame_rate") or "0/1").partition("/")
        return {"duration": float(d["format"].get("duration", 0)), "width": v.get("width"), "height": v.get("height"),
                "fps": round(float(num) / float(den or 1), 3) if v else None, "vcodec": v.get("codec_name"),
                "pix_fmt": v.get("pix_fmt"), "acodec": a.get("codec_name"), "sample_rate": int(a["sample_rate"]) if a else None}
    p = run([ffmpeg_bin(), "-hide_banner", "-i", str(path)], check=False)
    err = p.stderr
    out = {"duration": None, "width": None, "height": None, "fps": None, "vcodec": None, "pix_fmt": None,
           "acodec": None, "sample_rate": None}
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    if m:
        out["duration"] = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    m = re.search(r"Stream #[^\n]*Video: (\w+)[^\n]*?, (\w+)\(?[^\n]*?, (\d{2,5})x(\d{2,5})[^\n]*?, ([\d.]+) (?:fps|tbr)", err)
    if m:
        out.update(vcodec=m[1], pix_fmt=m[2], width=int(m[3]), height=int(m[4]), fps=float(m[5]))
    m = re.search(r"Stream #[^\n]*Audio: (\w+)[^\n]*?, (\d+) Hz", err)
    if m:
        out.update(acodec=m[1], sample_rate=int(m[2]))
    return out


def loudness(path):
    """Integrated loudness (LUFS) and true peak (dBTP) via ebur128."""
    p = run([ffmpeg_bin(), "-hide_banner", "-nostats", "-i", str(path), "-filter_complex",
             "ebur128=peak=true", "-f", "null", "-"], check=False)
    s = p.stderr[p.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", s)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", s)
    return {"integrated": float(i[1]) if i else None, "true_peak": float(tp[1]) if tp else None}


def silences(path, noise="-35dB", min_d=0.6):
    p = run([ffmpeg_bin(), "-hide_banner", "-nostats", "-i", str(path), "-af",
             f"silencedetect=noise={noise}:d={min_d}", "-f", "null", "-"], check=False)
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", p.stderr)]
    return [(s, ends[i] if i < len(ends) else None) for i, s in enumerate(starts)]


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def norm_words(text):
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.findall(r"[a-z0-9$%']+", text.lower())


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


BREAK_BEFORE = {"and", "but", "so", "or", "because", "then", "when", "while", "which", "that", "what", "who",
                "to", "in", "on", "with", "for", "from", "at", "by", "of", "if", "until", "before", "after"}
# words a caption line or cue should never end on: they lean on the next word
NO_END = {"the", "a", "an", "we", "i", "you", "your", "our", "my", "to", "of", "in", "on", "at", "for", "and", "or",
          "but", "with", "by", "is", "are", "be", "it’s", "it's", "this", "that", "every", "one", "no",
          "its", "their", "his", "her", "who", "which"}


def max_chars_for(cap, ratio):
    """Characters a caption line, per ratio: about 26 for the 1080-wide ratios, about 40 for 16:9.
    captions.max_chars may be one number (used for 1080-wide ratios; 16:9 gets at least 40) or
    {"16x9": 40, "9x16": 24}."""
    mc = cap.get("max_chars")
    if isinstance(mc, dict):
        return int(mc.get(ratio, 40 if ratio == "16x9" else 26))
    if mc is None:
        return 40 if ratio == "16x9" else 26
    return max(int(mc), 40) if ratio == "16x9" else min(int(mc), 28)


def _bare(w):
    return w.lower().strip("“”\"'‘’(),.:;!?")


def _balance(words, max_chars, max_lines=2):
    """One line if it fits; otherwise the two-line split with the shortest longer line."""
    one = " ".join(words)
    if len(one) <= max_chars or len(words) == 1:
        return [one]
    best = None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        worst = max(len(a), len(b))
        if words[k - 1][:1].isupper() and words[k][:1].isupper():
            worst += 8  # keep a capitalised name ("Babysitting Test") on one line
        if _bare(words[k - 1]) in NO_END or "-" in words[k - 1][-1:]:
            worst += 10  # a line never ends on "the", "a", "we" …
        if words[k - 1].endswith((",", ";", ":")):
            worst -= 3  # prefer breaking after punctuation
        elif any(ch.isdigit() for ch in words[k - 1]) and not words[k - 1][-1:] in ".?!":
            worst += 8  # a number stays with its unit ("30 minutes", "14 days")
        if best is None or worst < best[0]:
            best = (worst, [a, b])
    return best[1]


def _fits(words, max_chars, max_lines=2):
    return all(len(line) <= max_chars for line in _balance(words, max_chars, max_lines))


def _chunks(sentence, max_chars, max_dur):
    """Split one sentence (timed words) into caption chunks at natural phrase breaks."""
    out, i, n = [], 0, len(sentence)
    while i < n:
        j = i + 1
        while j < n and _fits([w["w"] for w in sentence[i:j + 1]], max_chars) and sentence[j]["end"] - sentence[i]["start"] <= max_dur:
            j += 1
        if j < n:  # sentence continues: step back to the best phrase break, keeping >= 3 words each side
            best, best_score = None, None
            for k in range(j, i + 1, -1):  # candidate break before word k; both sides at least two words
                if n - k < 2 or k - i < 2:
                    continue
                prev, nxt = sentence[k - 1]["w"], _bare(sentence[k]["w"])
                if _bare(prev) in NO_END:
                    continue
                score = 0.15 * (k - i)                                   # fuller first chunk
                score += 3 if prev.endswith((",", ";", ":")) else (2 if nxt in BREAK_BEFORE else 0)
                score += 2.5 if n - k >= 3 else 0                        # no two-word tail
                if best_score is None or score > best_score:
                    best, best_score = k, score
            if best is None:
                best = j if n - j >= 2 else max(i + 2, n - 2)
            j = best
        out.append(sentence[i:j])
        i = j
    return out


def caption_lines(words, max_chars=26, max_lines=2, max_dur=3.4, min_dur=0.7, end_by=None):
    """Group timed words into cues of at most two balanced lines. Cues follow sentences, split long
    sentences at phrase breaks (after commas, before conjunctions and prepositions), never leave a
    one- or two-word cue when the sentence can avoid it, and hold each cue until the next begins."""
    sentences, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if nxt else 9
        if w["w"].rstrip().endswith((".", "?", "!")) or gap > 0.7:
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)
    groups, sid = [], []  # chunks, and the sentence each came from
    for n_s, snt in enumerate(sentences):
        for ch in _chunks(snt, max_chars, max_dur):
            groups.append(ch)
            sid.append(n_s)
    dur = lambda g: g[-1]["end"] - g[0]["start"]
    fits = lambda g: _fits([w["w"] for w in g], max_chars)
    # a cue shorter than min_dur cannot be read. Merge it into a neighbour from the same sentence when
    # the pair fits two lines; otherwise move the break between them so both last min_dur. A cue never
    # takes words from another sentence ("leak. It's free," reads as one thought); a short cue that
    # cannot be fixed is held on screen a little longer below.
    i = 0
    while i < len(groups):
        g = groups[i]
        if dur(g) < min_dur and len(groups) > 1:
            done = False
            for j in (i + 1, i - 1):
                if 0 <= j < len(groups) and sid[j] == sid[i]:
                    a0, a1 = min(i, j), max(i, j)
                    pair = groups[a0] + groups[a1]
                    if fits(pair):
                        groups[a0:a1 + 1] = [pair]
                        sid[a0:a1 + 1] = [sid[i]]
                        i = a0
                        done = True
                        break
                    best = None
                    for k in range(2, len(pair) - 1):
                        x, y = pair[:k], pair[k:]
                        if fits(x) and fits(y) and dur(x) >= min_dur and dur(y) >= min_dur and _bare(x[-1]["w"]) not in NO_END:
                            sc = (3 if x[-1]["w"].endswith((",", ";", ":")) else 0) - abs(len(x) - len(y)) * 0.2
                            if best is None or sc > best[0]:
                                best = (sc, k)
                    if best:
                        groups[a0:a1 + 1] = [pair[:best[1]], pair[best[1]:]]
                        done = True
                        break
            if done:
                continue
        i += 1
    cues = [{"start": g[0]["start"], "end": g[-1]["end"], "lines": _balance([w["w"] for w in g], max_chars, max_lines)} for g in groups]
    if end_by is not None:  # nothing runs onto the end card
        cues = [c for c in cues if c["start"] < end_by - 0.2]
        for c in cues:
            c["end"] = min(c["end"], end_by)
    for i in range(len(cues) - 1):
        c, n = cues[i], cues[i + 1]
        short = c["start"] + min_dur - n["start"]
        if 0 < short <= 0.25:  # hold a short cue for min_dur; the next starts up to 0.25 s late
            n["start"] = round(c["start"] + min_dur, 3)
        c["end"] = min(max(c["end"], c["start"] + min_dur), n["start"])
    return cues


def write_srt(cues, path):
    out = []
    for i, c in enumerate(cues, 1):
        out += [str(i), f"{srt_time(c['start'])} --> {srt_time(c['end'])}", *c["lines"], ""]
    Path(path).write_text("\n".join(out), encoding="utf-8")
