#!/usr/bin/env python3
"""Ad Studio generation adapter: still-image plates through Higgsfield or Kie.ai, through the ledger.

Every paid call is reserved in the ledger first (spend cap enforced), marked submitting,
then recorded with the provider's job id. An uncertain outcome is recorded as unknown and
must be reconciled (--resume) before anything is retried. Nothing is generated without
--project, and --dry-run never touches the network.

Providers (fal.ai is deliberately not routed here)
  higgsfield  POST {base}/{model}                        key: HIGGSFIELD_API_KEY + HIGGSFIELD_API_SECRET
  kie         POST {base}/api/v1/jobs/createTask         key: KIE_API_KEY

Schema status (2026-10-14). Both shapes were written from the providers' public
descriptions; the build environment could not reach either provider's docs. They live in
PROVIDERS below, one block each. Run --probe once: it makes one harmless authenticated
call and prints what came back. If a field name is wrong, fix it in PROVIDERS. Nothing
else changes.

Usage
  gen.py --dry-run jobs.json --prices prices.json            print each request and the quote; no network
  gen.py --probe --provider kie|higgsfield                   one harmless call: key valid? balance?
  gen.py jobs.json --project project.json --prices prices.json   reserve, submit, poll, download, record
  gen.py --resume --project project.json [--provider kie]    reconcile pending/unknown jobs that have a job id

jobs.json
  {"provider": "kie",
   "jobs": [{"key": "2610.C1.plate.r0", "asset_id": "PLATE-C1", "model": "nano-banana-pro",
             "prompt_file": "plates/C1.prompt.txt", "aspect_ratio": "4:5", "resolution": "2K",
             "image_urls": [], "out": "plates/C1.png"}]}
  Paths are relative to jobs.json. image_urls must be public https URLs (reference images);
  for local reference photos use the Higgsfield MCP in an interactive session, which uploads them.

prices.json  (read from the provider's pricing page or account before the batch; never invented)
  {"checked_at": "2026-10-14", "source": "kie.ai pricing page",
   "kie": {"nano-banana-pro": {"per_image": 18, "unit": "credits"}}}

Environment (the member's .env; values are never printed)
  KIE_API_KEY, KIE_API_BASE (default https://api.kie.ai)
  HIGGSFIELD_API_KEY, HIGGSFIELD_API_SECRET, HIGGSFIELD_API_BASE (default https://platform.higgsfield.ai)
"""
import argparse, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger  # noqa: E402

# ---- Provider shapes: UNVERIFIED against live docs. Fix here after --probe if needed. ----
PROVIDERS = {
    "kie": {
        "base_env": "KIE_API_BASE", "base": "https://api.kie.ai",
        "submit_path": "/api/v1/jobs/createTask",
        "status_path": "/api/v1/jobs/recordInfo?taskId={id}",
        "probe_path": "/api/v1/chat/credit",
        # body: {"model": m, "input": {...}}; response data.taskId
        "wrap_input": True, "f_model": "model", "f_input": "input",
        "f_prompt": "prompt", "f_ratio": "aspect_ratio", "f_resolution": "resolution",
        "f_images": "image_input", "extra_input": {"output_format": "png"},
        "r_id": ["data", "taskId"],
        "s_state": ["data", "state"], "s_done": {"success"}, "s_failed": {"fail", "failed"},
        "s_result_json": ["data", "resultJson"], "s_result_urls": ["resultUrls"],
        "s_error": ["data", "failMsg"],
    },
    "higgsfield": {
        "base_env": "HIGGSFIELD_API_BASE", "base": "https://platform.higgsfield.ai",
        "submit_path": "/{model}",
        "status_path": "/requests/{id}/status",
        "probe_path": "/requests/00000000-0000-0000-0000-000000000000/status",
        "wrap_input": False,
        "f_prompt": "prompt", "f_ratio": "aspect_ratio", "f_resolution": "resolution",
        "f_images": "image_urls", "extra_input": {},
        "r_id": ["request_id"],
        "s_state": ["status"], "s_done": {"completed"}, "s_failed": {"failed", "nsfw", "canceled"},
        "s_result_json": None, "s_result_urls": ["images", "*", "url"],
        "s_error": ["error"],
    },
}
POLL_SECONDS = 5
POLL_LIMIT_SECONDS = 15 * 60


def load_dotenv():
    """Read ./.env (and the ads folder's parents) without printing anything."""
    for d in [Path.cwd(), *Path.cwd().parents][:4]:
        f = d / ".env"
        if f.is_file():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return


def creds(provider):
    if provider == "kie":
        k = os.environ.get("KIE_API_KEY")
        if not k:
            raise SystemExit("KIE_API_KEY is not set. Add it to .env (never paste it in chat).")
        return {"Authorization": f"Bearer {k}"}
    k, s = os.environ.get("HIGGSFIELD_API_KEY"), os.environ.get("HIGGSFIELD_API_SECRET")
    if not (k and s):
        raise SystemExit("HIGGSFIELD_API_KEY and HIGGSFIELD_API_SECRET must be set in .env.")
    return {"Authorization": f"Key {k}:{s}"}


def base(provider):
    p = PROVIDERS[provider]
    return os.environ.get(p["base_env"], p["base"]).rstrip("/")


def dig(obj, path):
    """Follow a key path; '*' maps over a list."""
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


def http(method, url, headers, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={**headers, "Content-Type": "application/json",
                                          "Accept": "application/json", "User-Agent": "buildroom-ad-studio/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
        return r.status, (json.loads(raw) if raw.strip() else {})


def build_request(provider, job, root):
    p = PROVIDERS[provider]
    prompt = (root / job["prompt_file"]).read_text(encoding="utf-8").strip()
    for u in job.get("image_urls", []):
        if not u.startswith("https://"):
            raise SystemExit(f"{job['key']}: image_urls must be public https URLs; use the Higgsfield MCP for local photos")
    inp = {p["f_prompt"]: prompt, p["f_ratio"]: job["aspect_ratio"], **p["extra_input"]}
    if job.get("resolution"):
        inp[p["f_resolution"]] = job["resolution"]
    if job.get("image_urls"):
        inp[p["f_images"]] = job["image_urls"]
    if p["wrap_input"]:
        body = {p["f_model"]: job["model"], p["f_input"]: inp}
    else:
        body = inp
    url = base(provider) + p["submit_path"].format(model=urllib.parse.quote(job["model"], safe="/-_."))
    return url, body


def price_for(prices, provider, model):
    try:
        entry = prices[provider][model]
        return entry["per_image"], entry["unit"]
    except (KeyError, TypeError):
        raise SystemExit(f"no price for {provider}/{model} in prices.json: read it from the provider first; never guess")


def cmd_dry_run(jobs_path, prices_path):
    spec = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
    root = Path(jobs_path).resolve().parent
    provider = spec["provider"]
    prices = json.loads(Path(prices_path).read_text(encoding="utf-8")) if prices_path else None
    total, unit = 0, None
    print(f"DRY RUN · provider {provider} · {len(spec['jobs'])} job(s) · nothing is sent\n")
    for job in spec["jobs"]:
        url, body = build_request(provider, job, root)
        line = f"[{job['key']}] {job['asset_id']} → {job['out']}\n  POST {url}\n  {json.dumps(body, ensure_ascii=False)[:600]}"
        if prices:
            cost, unit = price_for(prices, provider, job["model"])
            total += cost
            line += f"\n  quote: {cost} {unit}"
        print(line + "\n")
    if prices:
        print(f"TOTAL: {total} {unit}  (prices checked {prices.get('checked_at')} from {prices.get('source')})")
        print("Authorise this total plus the repair allowance with: ledger.py authorize ... --cap N --units", unit)
    else:
        print("No prices.json given: read current prices from the provider before quoting.")


def cmd_probe(provider):
    p = PROVIDERS[provider]
    url = base(provider) + p["probe_path"]
    try:
        status, body = http("GET", url, creds(provider), timeout=30)
        print(f"{provider}: HTTP {status} · keys accepted")
        print(json.dumps(body, ensure_ascii=False)[:800])
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")[:800]
        if e.code == 404 and provider == "higgsfield":
            print(f"{provider}: HTTP 404 on a dummy request id · keys accepted (the request id does not exist)")
        elif e.code in (401, 403):
            print(f"{provider}: HTTP {e.code} · key rejected or lacks permission. Check .env.")
        else:
            print(f"{provider}: HTTP {e.code} · read the body; fix PROVIDERS if a path or field is wrong")
        print(text)
    except urllib.error.URLError as e:
        print(f"{provider}: could not reach {url}: {e.reason}")


def poll(provider, job_id):
    p = PROVIDERS[provider]
    url = base(provider) + p["status_path"].format(id=urllib.parse.quote(job_id))
    deadline = time.time() + POLL_LIMIT_SECONDS
    while time.time() < deadline:
        try:
            _, body = http("GET", url, creds(provider), timeout=30)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  poll error (will retry): {e}")
            time.sleep(POLL_SECONDS)
            continue
        state = str(dig(body, p["s_state"]) or "").lower()
        if state in p["s_done"]:
            src = body
            if p["s_result_json"]:
                rj = dig(body, p["s_result_json"])
                src = json.loads(rj) if isinstance(rj, str) else (rj or {})
            urls = dig(src, p["s_result_urls"]) or []
            urls = urls if isinstance(urls, list) else [urls]
            return "completed", urls, body
        if state in p["s_failed"]:
            return "failed", [], body
        time.sleep(POLL_SECONDS)
    return "pending", [], None


def download(url, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "buildroom-ad-studio/1"})
    with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as fh:
        fh.write(r.read())


def rec(project, key, status, **kw):
    fields = {"key": key, "status": status, "job_id": None, "result": None,
              "charged": None, "charge_evidence": None, "evidence": None}
    fields.update(kw)
    ledger.apply(project, ledger.cmd_record, **fields)


def finish(project, provider, job, job_id, root):
    state, urls, body = poll(provider, job_id)
    if state == "completed" and urls:
        out = root / job["out"]
        download(urls[0], out)
        rec(project, job["key"], "completed", result=str(job["out"]))
        print(f"  done → {job['out']}  (record the actual charge when the provider shows it:"
              f" ledger.py record --key {job['key']} --status completed --charged N --charge-evidence ...)")
    elif state == "failed":
        err = dig(body, PROVIDERS[provider]["s_error"]) if body else None
        rec(project, job["key"], "failed", evidence=str(err or "provider reported failure")[:300])
        print(f"  failed: {err}. Failed jobs may still be billed; check the account before a repair pass.")
    else:
        print(f"  still running after {POLL_LIMIT_SECONDS // 60} min; left pending. Run --resume later; do not resubmit.")


def cmd_run(jobs_path, project, prices_path):
    spec = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
    root = Path(jobs_path).resolve().parent
    provider = spec["provider"]
    if provider not in PROVIDERS:
        raise SystemExit(f"provider must be one of {sorted(PROVIDERS)}")
    prices = json.loads(Path(prices_path).read_text(encoding="utf-8"))
    headers = creds(provider)
    for job in spec["jobs"]:
        cost, _unit = price_for(prices, provider, job["model"])
        url, body = build_request(provider, job, root)
        print(f"[{job['key']}] reserving {cost} …")
        ledger.apply(project, ledger.cmd_reserve, key=job["key"], asset_id=job["asset_id"], cost=cost,
                     quote=str(prices_path), request_ref=f"{jobs_path}#{job['key']}")
        rec(project, job["key"], "submitting")
        try:
            status, resp = http("POST", url, headers, body)
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", "replace")[:300]
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
            rec(project, job["key"], "unknown", evidence=f"no job id in response: {json.dumps(resp)[:300]}")
            print(f"  response had no job id (fix r_id in PROVIDERS?): {json.dumps(resp)[:300]}")
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
        if not j.get("job_id"):
            print(f"[{j['key']}] {j['status']} with no job id: check the provider dashboard, then record "
                  f"pending --job-id ID, or no_submission --evidence '...'. Do not resubmit blind.")
            continue
        job = by_key.get(j["key"], {"key": j["key"], "out": f"plates/{j['asset_id']}.png"})
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
