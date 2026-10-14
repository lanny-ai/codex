#!/usr/bin/env python3
"""Build Room media generation adapter: images, video B-roll and consented avatar twins,
through Higgsfield, Kie.ai or HeyGen, always through the ledger.

Shared by the Ad Studio and the Video Director (source: buildroom/shared/media/gen.py;
build-skills.sh copies it into each skill's scripts/). Edit the shared copy only.

Every paid call is reserved in the ledger first (spend cap enforced), marked submitting,
then recorded with the provider's job id. An uncertain outcome is recorded as unknown and
must be reconciled (--resume) before anything is retried. Nothing runs without --project,
and --dry-run never touches the network. fal.ai is deliberately not routed. Sora is never used.

Providers and job kinds
  higgsfield  image, video        key: HIGGSFIELD_API_KEY + HIGGSFIELD_API_SECRET
  kie         image, video        key: KIE_API_KEY
  heygen      twin (avatar video; refused without a consent reference)   key: HEYGEN_API_KEY

Schema status (2026-10-14). The request and response shapes were written from the
providers' public descriptions; their docs were unreachable from the build environment.
Each lives in PROVIDERS below as a body template ("$name" tokens are filled from the job;
a token with no value is dropped). Run --probe once per provider: one harmless authenticated
call, printed with secrets redacted. If a field name is wrong, fix the template. Nothing
else changes.

Usage
  gen.py --dry-run jobs.json [--prices prices.json]        print each request and the quote; no network
  gen.py --probe [--provider kie|higgsfield|heygen]        one harmless call per provider
  gen.py jobs.json --project project.json --prices prices.json   reserve, submit, poll, download, record
  gen.py --resume --project project.json [jobs.json] [--provider P]   reconcile jobs that have a job id

jobs.json
  {"provider": "kie",
   "jobs": [
    {"key": "2610.C1.plate.r0", "asset_id": "PLATE-C1", "kind": "image", "model": "<resolved id>",
     "prompt_file": "plates/C1.prompt.txt", "aspect_ratio": "4:5", "resolution": "2K", "out": "plates/C1.png"},
    {"key": "2610.V1.broll3.r0", "asset_id": "BROLL-3", "kind": "video", "model": "<resolved id>",
     "prompt_file": "broll/3.prompt.txt", "aspect_ratio": "9:16", "duration": 5,
     "image_urls": ["https://…/first-frame.png"], "out": "broll/3.mp4"},
    {"key": "2610.V2.twin.r0", "asset_id": "TWIN-1", "kind": "twin", "model": "heygen-v2",
     "script_file": "twin/hook2.txt", "avatar_id": "<member's avatar>", "voice_id": "<member's voice>",
     "width": 1080, "height": 1920, "consent_ref": "§19 likeness and voice consent, signed 2026-10-14", "out": "twin/hook2.mp4"}]}
  Paths are relative to jobs.json. image_urls must be public https URLs; for local references
  use the Higgsfield MCP in an interactive session, which uploads them.

prices.json  (read from the provider before the batch; never invented)
  {"checked_at": "2026-10-14", "source": "kie.ai pricing page",
   "kie": {"<model>": {"per_job": 18, "unit": "credits"}, "<video model>": {"per_second": 14, "unit": "credits"}}}
  "per_image" is accepted as a synonym of "per_job".

Environment (the member's .env; values are never printed)
  KIE_API_KEY, KIE_API_BASE (default https://api.kie.ai)
  HIGGSFIELD_API_KEY, HIGGSFIELD_API_SECRET, HIGGSFIELD_API_BASE (default https://platform.higgsfield.ai)
  HEYGEN_API_KEY, HEYGEN_API_BASE (default https://api.heygen.com)
"""
import argparse, copy, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger  # noqa: E402

# ---- Provider shapes: UNVERIFIED against live docs. Fix here after --probe if needed. ----
PROVIDERS = {
    "kie": {
        "base_env": "KIE_API_BASE", "base": "https://api.kie.ai",
        "auth": lambda: {"Authorization": "Bearer " + need("KIE_API_KEY")},
        "probe_path": "/api/v1/chat/credit",
        "kinds": {
            "image": {"submit_path": "/api/v1/jobs/createTask",
                      "body": {"model": "$model", "input": {"prompt": "$prompt", "aspect_ratio": "$aspect_ratio",
                               "resolution": "$resolution", "image_input": "$image_urls", "output_format": "png"}}},
            "video": {"submit_path": "/api/v1/jobs/createTask",
                      "body": {"model": "$model", "input": {"prompt": "$prompt", "aspect_ratio": "$aspect_ratio",
                               "duration": "$duration", "resolution": "$resolution", "image_urls": "$image_urls"}}},
        },
        "r_id": ["data", "taskId"],
        "status_path": "/api/v1/jobs/recordInfo?taskId={id}",
        "s_state": ["data", "state"], "s_done": {"success"}, "s_failed": {"fail", "failed"},
        "s_result_json": ["data", "resultJson"], "s_result_urls": ["resultUrls"], "s_error": ["data", "failMsg"],
    },
    "higgsfield": {
        "base_env": "HIGGSFIELD_API_BASE", "base": "https://platform.higgsfield.ai",
        "auth": lambda: {"Authorization": f"Key {need('HIGGSFIELD_API_KEY')}:{need('HIGGSFIELD_API_SECRET')}"},
        "probe_path": "/requests/00000000-0000-0000-0000-000000000000/status",
        "probe_404_ok": True,
        "kinds": {
            "image": {"submit_path": "/{model}",
                      "body": {"prompt": "$prompt", "aspect_ratio": "$aspect_ratio", "resolution": "$resolution",
                               "image_urls": "$image_urls"}},
            "video": {"submit_path": "/{model}",
                      "body": {"prompt": "$prompt", "aspect_ratio": "$aspect_ratio", "duration": "$duration",
                               "resolution": "$resolution", "image_url": "$first_image_url"}},
        },
        "r_id": ["request_id"],
        "status_path": "/requests/{id}/status",
        "s_state": ["status"], "s_done": {"completed"}, "s_failed": {"failed", "nsfw", "canceled"},
        "s_result_json": None, "s_result_urls": [["images", "*", "url"], ["video", "url"], ["videos", "*", "url"]],
        "s_error": ["error"],
    },
    "heygen": {
        "base_env": "HEYGEN_API_BASE", "base": "https://api.heygen.com",
        "auth": lambda: {"X-Api-Key": need("HEYGEN_API_KEY")},
        "probe_path": "/v2/user/remaining_quota",
        "kinds": {
            "twin": {"submit_path": "/v2/video/generate",
                     "body": {"video_inputs": [{"character": {"type": "avatar", "avatar_id": "$avatar_id", "avatar_style": "normal"},
                                                "voice": {"type": "text", "input_text": "$script", "voice_id": "$voice_id"}}],
                              "dimension": {"width": "$width", "height": "$height"}}},
        },
        "r_id": ["data", "video_id"],
        "status_path": "/v1/video_status.get?video_id={id}",
        "s_state": ["data", "status"], "s_done": {"completed"}, "s_failed": {"failed"},
        "s_result_json": None, "s_result_urls": [["data", "video_url"]], "s_error": ["data", "error"],
    },
}
POLL_SECONDS = float(os.environ.get("GEN_POLL_SECONDS", "5"))
POLL_LIMIT_SECONDS = 20 * 60


def need(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f"{name} is not set. Add it to .env in the member's folder (never paste it in chat).")
    return v


def load_dotenv():
    """Read the nearest .env (cwd and up to three parents) without printing anything."""
    for d in [Path.cwd(), *Path.cwd().parents][:4]:
        f = d / ".env"
        if f.is_file():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return


def base(provider):
    p = PROVIDERS[provider]
    return os.environ.get(p["base_env"], p["base"]).rstrip("/")


def dig(obj, path):
    """Follow a key path; '*' maps over a list. Returns a list when '*' is used."""
    if path is None:
        return None
    cur = [obj]
    for k in path:
        nxt = []
        for c in cur:
            if k == "*" and isinstance(c, list):
                nxt.extend(c)
            elif isinstance(c, dict) and k in c:
                nxt.append(c[k])
        cur = nxt
    if not cur:
        return None
    return cur if "*" in path else cur[0]


def fill(template, values):
    """Replace "$name" strings; drop keys whose token has no value."""
    if isinstance(template, dict):
        out = {}
        for k, v in template.items():
            r = fill(v, values)
            if r is not _MISSING:
                out[k] = r
        return out
    if isinstance(template, list):
        return [r for r in (fill(v, values) for v in template) if r is not _MISSING]
    if isinstance(template, str) and template.startswith("$"):
        v = values.get(template[1:])
        return _MISSING if v in (None, "", []) else v
    return template


_MISSING = object()


def http(method, url, headers, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={**headers, "Content-Type": "application/json",
                                          "Accept": "application/json", "User-Agent": "buildroom-media/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
        return r.status, (json.loads(raw) if raw.strip() else {})


def job_values(job, root):
    v = dict(job)
    if job.get("prompt_file"):
        v["prompt"] = (root / job["prompt_file"]).read_text(encoding="utf-8").strip()
    if job.get("script_file"):
        v["script"] = (root / job["script_file"]).read_text(encoding="utf-8").strip()
    urls = job.get("image_urls") or []
    for u in urls:
        if not str(u).startswith("https://"):
            raise SystemExit(f"{job['key']}: image_urls must be public https URLs; use the Higgsfield MCP for local files")
    v["image_urls"] = urls
    v["first_image_url"] = urls[0] if urls else None
    return v


def build_request(provider, job, root):
    p = PROVIDERS[provider]
    kind = job.get("kind", "image")
    if kind not in p["kinds"]:
        raise SystemExit(f"{job['key']}: {provider} does not handle '{kind}' jobs (has: {', '.join(p['kinds'])})")
    if kind == "twin" and not str(job.get("consent_ref", "")).strip():
        raise SystemExit(f"{job['key']}: an avatar twin needs consent_ref (written likeness and voice consent on file)")
    spec = p["kinds"][kind]
    body = fill(copy.deepcopy(spec["body"]), job_values(job, root))
    url = base(provider) + spec["submit_path"].format(model=urllib.parse.quote(str(job.get("model", "")), safe="/-_."))
    return url, body


def price_for(prices, provider, job):
    try:
        entry = prices[provider][job["model"]]
    except (KeyError, TypeError):
        raise SystemExit(f"no price for {provider}/{job.get('model')} in prices.json: read it from the provider first; never guess")
    if "per_second" in entry:
        if not job.get("duration"):
            raise SystemExit(f"{job['key']}: per-second price needs a duration on the job")
        return entry["per_second"] * float(job["duration"]), entry["unit"]
    return entry.get("per_job", entry.get("per_image")), entry["unit"]


def redact(text):
    for k in ("KIE_API_KEY", "HIGGSFIELD_API_KEY", "HIGGSFIELD_API_SECRET", "HEYGEN_API_KEY", "SUBMAGIC_API_KEY"):
        v = os.environ.get(k)
        if v:
            text = text.replace(v, "***")
    return text


def cmd_dry_run(jobs_path, prices_path):
    spec = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
    root = Path(jobs_path).resolve().parent
    provider = spec["provider"]
    if provider not in PROVIDERS:
        raise SystemExit(f"provider must be one of {sorted(PROVIDERS)} (fal.ai is not routed)")
    prices = json.loads(Path(prices_path).read_text(encoding="utf-8")) if prices_path else None
    total, unit = 0.0, None
    print(f"DRY RUN · provider {provider} · {len(spec['jobs'])} job(s) · nothing is sent\n")
    for job in spec["jobs"]:
        url, body = build_request(provider, job, root)
        line = f"[{job['key']}] {job.get('kind', 'image')} {job['asset_id']} → {job['out']}\n  POST {url}\n  {json.dumps(body, ensure_ascii=False)[:700]}"
        if prices:
            cost, unit = price_for(prices, provider, job)
            total += cost
            line += f"\n  quote: {cost:g} {unit}"
        print(line + "\n")
    if prices:
        print(f"TOTAL: {total:g} {unit}  (prices checked {prices.get('checked_at')} from {prices.get('source')})")
        print("Authorise this total plus the repair allowance with: ledger.py authorize ... --cap N --units", unit)
    else:
        print("No prices.json given: read current prices from the provider before quoting.")


def cmd_probe(provider):
    p = PROVIDERS[provider]
    url = base(provider) + p["probe_path"]
    try:
        status, body = http("GET", url, p["auth"](), timeout=30)
        print(f"{provider}: HTTP {status} · key accepted")
        print(redact(json.dumps(body, ensure_ascii=False)[:800]))
    except urllib.error.HTTPError as e:
        text = redact(e.read().decode("utf-8", "replace")[:800])
        if e.code == 404 and p.get("probe_404_ok"):
            print(f"{provider}: HTTP 404 on a dummy request id · key accepted")
        elif e.code in (401, 403):
            print(f"{provider}: HTTP {e.code} · key rejected or lacks permission. Check .env.")
        else:
            print(f"{provider}: HTTP {e.code} · read the body; fix PROVIDERS if a path or field is wrong")
        print(text)
    except urllib.error.URLError as e:
        print(f"{provider}: could not reach {url}: {e.reason}")


def result_urls(provider, body):
    p = PROVIDERS[provider]
    src = body
    if p["s_result_json"]:
        rj = dig(body, p["s_result_json"])
        src = json.loads(rj) if isinstance(rj, str) else (rj or {})
    paths = p["s_result_urls"]
    paths = paths if isinstance(paths[0], list) else [paths]
    for path in paths:
        got = dig(src, path)
        if got:
            return got if isinstance(got, list) else [got]
    return []


def poll(provider, job_id):
    p = PROVIDERS[provider]
    url = base(provider) + p["status_path"].format(id=urllib.parse.quote(job_id))
    deadline = time.time() + POLL_LIMIT_SECONDS
    while time.time() < deadline:
        try:
            _, body = http("GET", url, p["auth"](), timeout=30)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  poll error (will retry): {e}")
            time.sleep(POLL_SECONDS)
            continue
        state = str(dig(body, p["s_state"]) or "").lower()
        if state in p["s_done"]:
            return "completed", result_urls(provider, body), body
        if state in p["s_failed"]:
            return "failed", [], body
        time.sleep(POLL_SECONDS)
    return "pending", [], None


def download(url, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "buildroom-media/1"})
    with urllib.request.urlopen(req, timeout=300) as r, open(out, "wb") as fh:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            fh.write(chunk)


def rec(project, key, status, **kw):
    fields = {"key": key, "status": status, "job_id": None, "result": None,
              "charged": None, "charge_evidence": None, "evidence": None}
    fields.update(kw)
    ledger.apply(project, ledger.cmd_record, **fields)


def finish(project, provider, job, job_id, root):
    state, urls, body = poll(provider, job_id)
    if state == "completed" and urls:
        download(urls[0], root / job["out"])
        rec(project, job["key"], "completed", result=str(job["out"]))
        print(f"  done → {job['out']}  (record the actual charge when the provider shows it:"
              f" ledger.py record --key {job['key']} --status completed --charged N --charge-evidence ...)")
    elif state == "failed":
        err = dig(body, PROVIDERS[provider]["s_error"]) if body else None
        rec(project, job["key"], "failed", evidence=str(err or "provider reported failure")[:300])
        print(f"  failed: {err}. Failed jobs may still be billed; check the account before a repair pass.")
    elif state == "completed":
        rec(project, job["key"], "unknown", evidence="completed with no result URL in the response")
        print("  provider says completed but returned no file URL; recorded unknown. Fix s_result_urls in PROVIDERS?")
    else:
        print(f"  still running after {POLL_LIMIT_SECONDS // 60} min; left pending. Run --resume later; do not resubmit.")


def cmd_run(jobs_path, project, prices_path):
    spec = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
    root = Path(jobs_path).resolve().parent
    provider = spec["provider"]
    if provider not in PROVIDERS:
        raise SystemExit(f"provider must be one of {sorted(PROVIDERS)} (fal.ai is not routed)")
    prices = json.loads(Path(prices_path).read_text(encoding="utf-8"))
    headers = PROVIDERS[provider]["auth"]()
    for job in spec["jobs"]:
        cost, _unit = price_for(prices, provider, job)
        url, body = build_request(provider, job, root)
        print(f"[{job['key']}] reserving {cost:g} …")
        ledger.apply(project, ledger.cmd_reserve, key=job["key"], asset_id=job["asset_id"], cost=cost,
                     quote=str(prices_path), request_ref=f"{jobs_path}#{job['key']}")
        rec(project, job["key"], "submitting")
        try:
            status, resp = http("POST", url, headers, body)
        except urllib.error.HTTPError as e:
            text = redact(e.read().decode("utf-8", "replace")[:300])
            if 400 <= e.code < 500:
                rec(project, job["key"], "no_submission", evidence=f"HTTP {e.code}: {text}")
                print(f"  rejected (HTTP {e.code}): {text}\n  Recorded no_submission; fix the request and use a new key.")
            else:
                rec(project, job["key"], "unknown", evidence=f"HTTP {e.code}: {text}")
                print(f"  server error (HTTP {e.code}); recorded unknown. Check the provider dashboard before any retry.")
            continue
        except (urllib.error.URLError, TimeoutError) as e:
            rec(project, job["key"], "unknown", evidence=f"transport: {e}")
            print(f"  no response ({e}); recorded unknown. Check the provider dashboard before any retry.")
            continue
        job_id = dig(resp, PROVIDERS[provider]["r_id"])
        if not job_id:
            rec(project, job["key"], "unknown", evidence=f"no job id in response: {redact(json.dumps(resp))[:300]}")
            print(f"  response had no job id (fix r_id in PROVIDERS?): {redact(json.dumps(resp))[:300]}")
            continue
        rec(project, job["key"], "pending", job_id=str(job_id))
        print(f"  submitted · job {job_id}")
        finish(project, provider, job, str(job_id), root)


def cmd_resume(project, jobs_path, only_provider):
    data = ledger.load(ledger.project_path(project))
    spec = json.loads(Path(jobs_path).read_text(encoding="utf-8")) if jobs_path else {"jobs": []}
    by_key = {j["key"]: j for j in spec.get("jobs", [])}
    root = Path(jobs_path).resolve().parent if jobs_path else Path(project).resolve().parent
    for j in data["jobs"]:
        if j["status"] not in {"pending", "unknown", "submitting"}:
            continue
        if only_provider and j["provider"] != only_provider:
            continue
        if j["provider"] not in PROVIDERS:
            continue  # e.g. submagic jobs are reconciled by submagic.py
        if not j.get("job_id"):
            print(f"[{j['key']}] {j['status']} with no job id: check the provider dashboard, then record "
                  f"pending --job-id ID, or no_submission --evidence '...'. Do not resubmit blind.")
            continue
        job = by_key.get(j["key"], {"key": j["key"], "out": f"generated/{j['asset_id']}"})
        print(f"[{j['key']}] reconciling job {j['job_id']} …")
        if j["status"] != "pending":
            rec(project, j["key"], "pending", job_id=j["job_id"])
        finish(project, j["provider"], job, j["job_id"], root)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jobs", nargs="?")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--provider", choices=sorted(PROVIDERS))
    ap.add_argument("--project")
    ap.add_argument("--prices")
    a = ap.parse_args()
    load_dotenv()
    try:
        if a.probe:
            for prov in ([a.provider] if a.provider else sorted(PROVIDERS)):
                cmd_probe(prov)
        elif a.dry_run:
            if not a.jobs:
                raise SystemExit("--dry-run needs jobs.json")
            cmd_dry_run(a.jobs, a.prices)
        elif a.resume:
            if not a.project:
                raise SystemExit("--resume needs --project")
            cmd_resume(a.project, a.jobs, a.provider)
        else:
            if not (a.jobs and a.project and a.prices):
                raise SystemExit("a live run needs jobs.json, --project and --prices (and a dry run shown to the member first)")
            cmd_run(a.jobs, a.project, a.prices)
    except ValueError as e:  # ledger refusals: cap, gates, open jobs
        print(f"ledger refused: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
