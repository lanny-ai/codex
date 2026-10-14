#!/usr/bin/env python3
"""SubMagic captions for an assembled cut, through the ledger.

The director assembles a clean cut (assemble_video.py, captions.mode "submagic"), then this sends
it to SubMagic with the member's caption template, waits, and saves the captioned video. Every
call is reserved in the ledger first. Without a key, or if SubMagic fails, the fallback is the
director's own burned captions (captions.mode "burn" in assemble_video.py), and this says so.

Sign-up: https://submagic.co/?via=harrison22
  This is my affiliate link. If you sign up through it, I earn a commission, at no extra cost to you.
  (Or go to submagic.co directly.) Key: SUBMAGIC_API_KEY in .env (starts with sk-), never in chat.

Schema status (2026-10-14). From SubMagic's public API reference as summarised in search results
(the docs host was unreachable from the build environment): POST {base}/v1/projects with an
x-api-key header and {title, language, videoUrl (public, no auth), templateName}; the default
template is "Sara". The local-file upload path (/v1/projects/upload, multipart), the status
fields and whether an explicit export call is needed are less certain. All of it lives in SHAPE
below. Run --probe once; fix SHAPE if a field is wrong.

Usage
  submagic.py --probe                                         key works? which templates?
  submagic.py --dry-run --video renders/V1_9x16.cut.mp4 [--video-url https://…] --template "Hormozi 2"
  submagic.py --project project.json --asset-id CAPTIONS-V1-916 --video renders/V1_9x16.cut.mp4 \
              --out renders/V1_9x16.mp4 --template "Hormozi 2" [--video-url https://…] --cost 1 --quote "plan minutes"
  submagic.py --resume --project project.json --asset-id CAPTIONS-V1-916 --out renders/V1_9x16.mp4
"""
import argparse, json, mimetypes, os, sys, time, urllib.error, urllib.request, uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger  # noqa: E402

SHAPE = {
    "base_env": "SUBMAGIC_API_BASE", "base": "https://api.submagic.co",
    "key_env": "SUBMAGIC_API_KEY", "key_header": "x-api-key",
    "create_path": "/v1/projects",            # JSON body with a public videoUrl
    "upload_path": "/v1/projects/upload",     # multipart with the file (UNVERIFIED)
    "status_path": "/v1/projects/{id}",
    "export_path": "/v1/projects/{id}/export",  # called once if completed without a download URL (UNVERIFIED)
    "templates_path": "/v1/templates",
    "f_title": "title", "f_language": "language", "f_video_url": "videoUrl", "f_template": "templateName",
    "f_file": "file",
    "r_id": ["id"], "s_state": ["status"], "s_done": {"completed", "done", "exported"},
    "s_failed": {"failed", "error"}, "s_download": [["downloadUrl"], ["directUrl"], ["output", "url"]],
    "s_words": [["words"], ["transcription", "words"]],
}
POLL = float(os.environ.get("GEN_POLL_SECONDS", "6"))
LIMIT = 30 * 60


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


def base():
    return os.environ.get(SHAPE["base_env"], SHAPE["base"]).rstrip("/")


def key():
    k = os.environ.get(SHAPE["key_env"])
    if not k:
        raise SystemExit("SUBMAGIC_API_KEY is not set in .env. Either add it (sign-up link and disclosure in the "
                         "header of this script and in provider-signup.md) or use the director's own captions: "
                         "set captions.mode to \"burn\" in edit.json and assemble again.")
    return k


def dig(obj, path):
    for k in path:
        if isinstance(obj, dict) and k in obj:
            obj = obj[k]
        else:
            return None
    return obj


def first(obj, paths):
    for p in paths:
        v = dig(obj, p)
        if v:
            return v
    return None


def redact(t):
    k = os.environ.get(SHAPE["key_env"])
    return t.replace(k, "***") if k else t


def http_json(method, path, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base() + path, data=data, method=method,
                                 headers={SHAPE["key_header"]: key(), "Content-Type": "application/json",
                                          "Accept": "application/json", "User-Agent": "buildroom-video/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
        return json.loads(raw) if raw.strip() else {}


def http_upload(path, fields, file_path, timeout=900):
    b = uuid.uuid4().hex
    parts = [f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode() for k, v in fields.items()]
    ctype = mimetypes.guess_type(str(file_path))[0] or "video/mp4"
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{SHAPE['f_file']}\"; filename=\"{Path(file_path).name}\"\r\n"
                 f"Content-Type: {ctype}\r\n\r\n".encode() + Path(file_path).read_bytes() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(base() + path, data=b"".join(parts), method="POST",
                                 headers={SHAPE["key_header"]: key(), "Content-Type": f"multipart/form-data; boundary={b}",
                                          "User-Agent": "buildroom-video/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace") or "{}")


def request_for(a):
    fields = {SHAPE["f_title"]: a.title or Path(a.video).stem, SHAPE["f_language"]: a.language,
              SHAPE["f_template"]: a.template}
    if a.video_url:
        return "json", SHAPE["create_path"], {**fields, SHAPE["f_video_url"]: a.video_url}
    return "upload", SHAPE["upload_path"], fields


def rec(project, k, status, **kw):
    f = {"key": k, "status": status, "job_id": None, "result": None, "charged": None, "charge_evidence": None, "evidence": None}
    f.update(kw)
    ledger.apply(project, ledger.cmd_record, **f)


def wait_and_save(project, k, job_id, out):
    deadline, exported = time.time() + LIMIT, False
    while time.time() < deadline:
        try:
            d = http_json("GET", SHAPE["status_path"].format(id=job_id))
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  poll error (will retry): {e}")
            time.sleep(POLL)
            continue
        state = str(dig(d, SHAPE["s_state"]) or "").lower()
        url = first(d, SHAPE["s_download"])
        if url:
            req = urllib.request.Request(url, headers={"User-Agent": "buildroom-video/1"})
            Path(out).parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(req, timeout=600) as r, open(out, "wb") as fh:
                fh.write(r.read())
            words = first(d, SHAPE["s_words"])
            if words:
                Path(out).with_suffix(".submagic-words.json").write_text(json.dumps(words, indent=1), encoding="utf-8")
            rec(project, k, "completed", result=str(out))
            print(f"  captioned → {out}" + ("  (SubMagic's word list saved for the review)" if words else ""))
            return True
        if state in SHAPE["s_done"] and not exported:
            try:
                http_json("POST", SHAPE["export_path"].format(id=job_id), {})
                exported = True
                print("  processed; export requested …")
            except urllib.error.HTTPError as e:
                print(f"  export call refused (HTTP {e.code}); waiting for a download URL")
                exported = True
        if state in SHAPE["s_failed"]:
            rec(project, k, "failed", evidence=redact(json.dumps(d))[:300])
            print("  SubMagic reported a failure. Fallback: captions.mode \"burn\" in edit.json, then assemble again.")
            return False
        time.sleep(POLL)
    print("  still processing after 30 min; left pending. Run --resume later; do not resubmit.")
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--project"); ap.add_argument("--asset-id"); ap.add_argument("--key")
    ap.add_argument("--video"); ap.add_argument("--video-url"); ap.add_argument("--out")
    ap.add_argument("--template", default="Sara"); ap.add_argument("--language", default="en")
    ap.add_argument("--title"); ap.add_argument("--cost"); ap.add_argument("--quote")
    a = ap.parse_args()
    load_dotenv()
    if a.probe:
        try:
            d = http_json("GET", SHAPE["templates_path"])
            print("submagic: key accepted · templates:", redact(json.dumps(d))[:600])
        except urllib.error.HTTPError as e:
            print(f"submagic: HTTP {e.code}", "· key rejected" if e.code in (401, 403) else "· read the body; fix SHAPE if a path is wrong")
            print(redact(e.read().decode("utf-8", "replace")[:400]))
        except urllib.error.URLError as e:
            print(f"submagic: could not reach {base()}: {e.reason}")
        return
    if a.dry_run:
        if not a.video:
            raise SystemExit("--dry-run needs --video")
        kind, path, body = request_for(a)
        print(f"DRY RUN · nothing is sent\n  {'POST' if kind == 'json' else 'POST multipart'} {base()}{path}\n  {json.dumps(body)}"
              + (f"\n  file: {a.video} ({Path(a.video).stat().st_size // 1024} KB)" if kind == "upload" else ""))
        print("  then: poll status until a download URL appears; save it; record it in the ledger.")
        return
    if not (a.project and a.asset_id and a.out):
        raise SystemExit("needs --project, --asset-id and --out")
    k = a.key or f"{a.asset_id}.r0"
    if a.resume:
        data = ledger.load(ledger.project_path(a.project))
        job = next((j for j in data["jobs"] if j["asset_id"] == a.asset_id and j["status"] in {"pending", "unknown", "submitting"}), None)
        if not job or not job.get("job_id"):
            raise SystemExit("nothing to resume with a job id; check SubMagic's dashboard and record it by hand")
        if job["status"] != "pending":
            rec(a.project, job["key"], "pending", job_id=job["job_id"])
        wait_and_save(a.project, job["key"], job["job_id"], a.out)
        return
    if not (a.video and a.cost and a.quote):
        raise SystemExit("needs --video, --cost (in the plan's units) and --quote (where the price came from)")
    try:
        ledger.apply(a.project, ledger.cmd_reserve, key=k, asset_id=a.asset_id, cost=a.cost, quote=a.quote,
                     request_ref=f"submagic:{Path(a.video).name}:{a.template}")
    except ValueError as e:
        raise SystemExit(f"ledger refused: {e}")
    rec(a.project, k, "submitting")
    kind, path, body = request_for(a)
    try:
        resp = http_json("POST", path, body) if kind == "json" else http_upload(path, body, a.video)
    except urllib.error.HTTPError as e:
        text = redact(e.read().decode("utf-8", "replace")[:300])
        status = "no_submission" if 400 <= e.code < 500 else "unknown"
        rec(a.project, k, status, evidence=f"HTTP {e.code}: {text}")
        print(f"  SubMagic said HTTP {e.code}: {text}\n  Recorded {status}. Fallback: captions.mode \"burn\" in edit.json.")
        sys.exit(1)
    except (urllib.error.URLError, TimeoutError) as e:
        rec(a.project, k, "unknown", evidence=f"transport: {e}")
        print(f"  no response ({e}); recorded unknown. Check SubMagic's dashboard before any retry.")
        sys.exit(1)
    job_id = dig(resp, SHAPE["r_id"])
    if not job_id:
        rec(a.project, k, "unknown", evidence=f"no project id: {redact(json.dumps(resp))[:300]}")
        raise SystemExit("SubMagic's response had no project id; fix r_id in SHAPE?")
    rec(a.project, k, "pending", job_id=str(job_id))
    print(f"  submitted · project {job_id}")
    if not wait_and_save(a.project, k, str(job_id), a.out):
        sys.exit(1)


if __name__ == "__main__":
    main()
