#!/usr/bin/env python3
"""Build Room media ledger: the gates, the spend cap and every paid job, in one local file.

Shared by the Ad Studio and the Video Director (source: buildroom/shared/media/ledger.py;
build-skills.sh copies it into each skill's scripts/). Edit the shared copy only.

Adapted from the job ledger in the create-ads-with-agents skill (workflow_state.py,
v2.1.2): reserve a job key before any paid call, mark it submitting, record the
provider's job id, reconcile an uncertain job before any retry, never exceed the cap.
Made provider-neutral (Higgsfield, Kie.ai, HeyGen, SubMagic) for images, video B-roll,
consented avatar twins and captions, and wired to the Build Room gates G0-G4 and the
member's approval. An "ad" record is any deliverable: a static ad or a video.

It is local, makes no network calls, and never submits anything. It checks structure,
not truth: a passed gate here means someone recorded a pass, not that the ad is good.

Usage
  ledger.py init      ads/2026-10/project.json --cycle 2026-10 [--mode demo]
  ledger.py authorize P --provider kie --cap 400 --units credits --note "quote q1 approved by member 2026-10-14"
  ledger.py plan      P --asset-id PLATE-C1 --provider kie --model <resolved id> --prompt-ref plates/c1.prompt.txt
                        [--kind plate|broll|twin|captions] [--consent-ref "§19 consent, signed 2026-10-14"]  (twin needs consent)
  ledger.py reserve   P --key 2610.C1.plate.r0 --asset-id PLATE-C1 --cost 18 --quote prices.json --request-ref jobs.json
  ledger.py record    P --key 2610.C1.plate.r0 --status submitting|pending|completed|failed|canceled|unknown|no_submission
                        [--job-id ID] [--result path] [--charged N --charge-evidence ref] [--evidence text]
  ledger.py gate      P --gate G0|G1|G2 --verdict pass|revise|unverified --by producer --ref brief.md
                        (a G2 pass is the member's sign-off on the words: --by member, except in demo mode)
  ledger.py ad        P --ad C1-H1 --concept C1 --layout photo-hook --spec specs/C1-H1.json [--renders a.png b.png ...]
  ledger.py gate      P --ad C1-H1 --gate G3|G4 --verdict pass --by reviewer --ref review/review.md
  ledger.py repair    P --ad C1-H1 --note "headline overflowed 9x16; shortened sub"  (ceiling: 2, or --ceiling N if the member set one)
  ledger.py approve   P --ad C1-H1 --note "member approved in session"
  ledger.py check     P [--for-production | --for-kit]
  ledger.py summary   P
"""
import argparse, json, os, sys, tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

SCHEMA = "buildroom-media/1"  # shared by the Ad Studio and the Video Director
OLD_SCHEMAS = {"buildroom-ad-studio/1"}  # read as-is, upgraded on the next write
PROVIDERS = {"higgsfield", "kie", "heygen", "submagic"}
KINDS = {"plate", "broll", "twin", "captions"}
STATES = {
    "reserved": {"submitting", "no_submission"},
    "submitting": {"pending", "completed", "failed", "unknown", "no_submission"},
    "pending": {"pending", "completed", "failed", "canceled", "unknown"},
    "unknown": {"pending", "completed", "failed", "canceled", "no_submission"},
    "completed": set(), "failed": set(), "canceled": set(), "no_submission": set(),
}
OPEN = {"reserved", "submitting", "pending", "unknown"}
GATES_PROJECT = ("G0", "G1", "G2")
GATES_AD = ("G3", "G4")
VERDICTS = {"pass", "revise", "unverified"}
DEFAULT_REPAIR_CEILING = 2


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def amount(value):
    try:
        d = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"not a number: {value}")
    if not d.is_finite() or d < 0:
        raise ValueError(f"must be a nonnegative number: {value}")
    return d


@contextmanager
def locked(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = str(path) + ".lock"
    with open(lock_path, "a+", encoding="utf-8") as fh:
        try:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except ImportError:  # Windows: one writer at a time, by convention
            try:
                import msvcrt
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
                try:
                    yield
                finally:
                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            except (ImportError, OSError):
                yield


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if data.get("schema") in OLD_SCHEMAS:
        data["schema"] = SCHEMA
    if data.get("schema") != SCHEMA:
        raise ValueError("not a Build Room media ledger (schema mismatch)")
    return data


def save(path, data):
    data["updated_at"] = now()
    fd, tmp = tempfile.mkstemp(prefix=".ledger-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def project_path(value):
    p = Path(value).expanduser().resolve()
    skill_root = Path(__file__).resolve().parents[1]
    if p == skill_root or skill_root in p.parents:
        raise ValueError("keep the ledger in the member's project folder (ads/ or videos/), not inside the skill")
    return p


# ---------- money ----------

def committed(data, provider):
    """Charged where known, else the reserved quote: what this provider's cap must hold."""
    total = Decimal("0")
    for j in data["jobs"]:
        if j["provider"] != provider:
            continue
        total += amount(j["charged"] if j.get("charged") is not None else j["reserved"])
    return total


def summary(data):
    out = {"cycle": data["cycle"], "mode": data["mode"],
           "gates": {g: data["gates"].get(g, {}).get("verdict", "unverified") for g in GATES_PROJECT},
           "providers": {}, "open_jobs": [j["key"] for j in data["jobs"] if j["status"] in OPEN],
           "ads": len(data["ads"]),
           "ads_reviewed": sum(1 for a in data["ads"] if all(a.get(g, {}).get("verdict") == "pass" for g in GATES_AD)),
           "ads_approved": sum(1 for a in data["ads"] if a.get("approved"))}
    for prov, cap in data["budget"]["caps"].items():
        used = committed(data, prov)
        out["providers"][prov] = {"units": cap["units"], "cap": cap["cap"], "committed": str(used),
                                  "remaining": str(amount(cap["cap"]) - used),
                                  "over_cap": used > amount(cap["cap"])}
    for prov in {j["provider"] for j in data["jobs"]} - set(out["providers"]):
        out["providers"][prov] = {"committed": str(committed(data, prov)), "cap": None}
    out["note"] = "Committed counts held quotes where the actual charge is not yet known."
    return out


# ---------- checks ----------

def errors_for(data, production=False, kit=False):
    errs = []
    if production or kit:
        if data["mode"] != "live":
            errs.append("demo mode: no production or kit")
        for g in GATES_PROJECT:
            if data["gates"].get(g, {}).get("verdict") != "pass":
                errs.append(f"{g} has not passed")
    if production:
        if not data["budget"]["caps"]:
            errs.append("no spend authorised: run authorize with the member's approved cap")
        if not data["assets"]:
            errs.append("no generation asset planned")
    if kit:
        if not data["ads"]:
            errs.append("no ads recorded")
        for a in data["ads"]:
            if not a.get("renders"):
                errs.append(f"{a['id']}: no rendered files recorded")
            for g in GATES_AD:
                if a.get(g, {}).get("verdict") != "pass":
                    errs.append(f"{a['id']}: {g} has not passed")
            if not a.get("approved"):
                errs.append(f"{a['id']}: not approved by the member")
        used = {aid for a in data["ads"] for aid in a.get("assets", [])}
        for asset in data["assets"]:
            if asset["id"] in used and not asset.get("result_ref"):
                errs.append(f"{asset['id']}: used by an ad but has no completed generation")
        open_jobs = [j["key"] for j in data["jobs"] if j["status"] in {"submitting", "unknown"}]
        if open_jobs:
            errs.append("reconcile uncertain jobs first: " + ", ".join(open_jobs))
    return errs


# ---------- commands ----------

def cmd_init(path, a):
    if path.exists():
        raise ValueError("ledger exists: resume it; never re-initialise over spending history")
    return {"schema": SCHEMA, "created_at": now(), "cycle": a.cycle, "mode": a.mode,
            "gates": {}, "budget": {"caps": {}, "authorizations": []},
            "assets": [], "jobs": [], "ads": []}


def cmd_authorize(data, a):
    if a.provider not in PROVIDERS:
        raise ValueError(f"provider must be one of {sorted(PROVIDERS)}")
    if not a.note or not a.note.strip():
        raise ValueError("--note must say where the member approved this cap")
    cap = amount(a.cap)
    prev = data["budget"]["caps"].get(a.provider)
    if prev and prev["units"] != a.units:
        raise ValueError(f"units differ from the existing cap ({prev['units']})")
    if committed(data, a.provider) > cap:
        raise ValueError("new cap is below what is already committed")
    data["budget"]["caps"][a.provider] = {"cap": str(cap), "units": a.units}
    data["budget"]["authorizations"].append({"provider": a.provider, "cap": str(cap), "units": a.units,
                                             "note": a.note, "at": now()})


def cmd_plan(data, a):
    if a.provider not in PROVIDERS:
        raise ValueError(f"provider must be one of {sorted(PROVIDERS)}")
    if any(x["id"] == a.asset_id for x in data["assets"]):
        raise ValueError("asset id exists")
    kind = getattr(a, "kind", None) or "plate"
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {sorted(KINDS)}")
    consent = (getattr(a, "consent_ref", None) or "").strip()
    if kind == "twin" and not consent:
        raise ValueError("an avatar twin needs --consent-ref: written likeness and voice consent on file")
    data["assets"].append({"id": a.asset_id, "kind": kind, "provider": a.provider, "model": a.model,
                           "prompt_ref": a.prompt_ref, "consent_ref": consent or None,
                           "result_ref": None, "planned_at": now()})


def cmd_reserve(data, a):
    errs = errors_for(data, production=True)
    if errs:
        raise ValueError("; ".join(errs))
    assets = {x["id"]: x for x in data["assets"]}
    if a.asset_id not in assets:
        raise ValueError("reserve needs --asset-id of a planned asset (ledger.py plan)")
    asset = assets[a.asset_id]
    if any(j["key"] == a.key for j in data["jobs"]):
        raise ValueError("key exists: resume or reconcile it; never submit a duplicate")
    if any(j["asset_id"] == a.asset_id and j["status"] in OPEN for j in data["jobs"]):
        raise ValueError("this asset has an unresolved job: reconcile it first")
    prov = asset["provider"]
    cap = data["budget"]["caps"].get(prov)
    if not cap:
        raise ValueError(f"no authorised cap for {prov}")
    cost = amount(a.cost)
    if committed(data, prov) + cost > amount(cap["cap"]):
        raise ValueError(f"over the authorised cap for {prov}: committed {committed(data, prov)} + {cost} > {cap['cap']} {cap['units']}")
    data["jobs"].append({"key": a.key, "asset_id": a.asset_id, "provider": prov, "model": asset["model"],
                         "status": "reserved", "reserved": str(cost), "units": cap["units"],
                         "quote_ref": a.quote, "request_ref": a.request_ref,
                         "history": [{"status": "reserved", "at": now()}]})


def cmd_record(data, a):
    jobs = [j for j in data["jobs"] if j["key"] == a.key]
    if len(jobs) != 1:
        raise ValueError("no such job key")
    j = jobs[0]
    if a.status not in STATES[j["status"]] and not (a.status == j["status"] == "pending"):
        raise ValueError(f"invalid transition {j['status']} -> {a.status}")
    if j["status"] == "reserved" and a.status == "submitting":
        errs = errors_for(data, production=True)
        if errs:
            raise ValueError("; ".join(errs))
    if a.job_id:
        if j.get("job_id") and j["job_id"] != a.job_id:
            raise ValueError("cannot replace a recorded provider job id")
        if any(o.get("job_id") == a.job_id for o in data["jobs"] if o is not j):
            raise ValueError("that provider job id belongs to another key")
        j["job_id"] = a.job_id
    if a.status in {"pending", "completed"} and not j.get("job_id"):
        raise ValueError(f"{a.status} needs the provider's job id")
    if a.status == "completed":
        if not a.result:
            raise ValueError("completed needs --result (the saved file)")
        j["result_ref"] = a.result
        for asset in data["assets"]:
            if asset["id"] == j["asset_id"]:
                asset["result_ref"] = a.result
    if a.status == "no_submission":
        if j.get("job_id") or not a.evidence:
            raise ValueError("no_submission needs --evidence and no provider job id")
        j["charged"], j["charge_evidence"] = "0", a.evidence
    if a.charged is not None:
        if not a.charge_evidence:
            raise ValueError("an actual charge needs --charge-evidence (provider receipt, balance before/after)")
        j["charged"], j["charge_evidence"] = str(amount(a.charged)), a.charge_evidence
    j["status"] = a.status
    j["history"].append({"status": a.status, "at": now(), "evidence": a.evidence,
                         "charged": a.charged})


def find_ad(data, ad_id):
    for x in data["ads"]:
        if x["id"] == ad_id:
            return x
    raise ValueError(f"no ad {ad_id}: record it with `ledger.py ad` first")


def cmd_ad(data, a):
    try:
        ad = find_ad(data, a.ad)
    except ValueError:
        ad = {"id": a.ad, "repairs": [], "created_at": now()}
        data["ads"].append(ad)
    for k in ("concept", "layout", "spec"):
        if getattr(a, k):
            ad[k] = getattr(a, k)
    if a.renders:
        if ad.get("renders") and ad["renders"] != a.renders:
            for g in GATES_AD:  # changed files must be reviewed again
                if g in ad:
                    ad[g] = {"verdict": "unverified", "at": now(), "by": "ledger", "ref": "renders changed"}
            ad.pop("approved", None)
        ad["renders"] = a.renders
    if a.assets:
        ad["assets"] = a.assets


def cmd_gate(data, a):
    if a.verdict not in VERDICTS:
        raise ValueError(f"verdict must be one of {sorted(VERDICTS)}")
    rec = {"verdict": a.verdict, "by": a.by, "ref": a.ref, "at": now()}
    if a.ad:
        if a.gate not in GATES_AD:
            raise ValueError("per-ad gates are G3 and G4")
        ad = find_ad(data, a.ad)
        if a.verdict == "pass" and not ad.get("renders"):
            raise ValueError("G3/G4 can only pass on rendered files")
        if a.verdict == "pass" and a.by in {"producer", "author"}:
            raise ValueError("G3/G4 pass must come from the reviewer, not the author")
        ad[a.gate] = rec
    else:
        if a.gate not in GATES_PROJECT:
            raise ValueError("project gates are G0, G1, G2")
        if a.gate == "G2" and a.verdict == "pass" and a.by != "member" and data["mode"] == "live":
            raise ValueError("G2 is the member's sign-off on the approved words (guarantees included): record it --by member")
        data["gates"][a.gate] = rec


def cmd_repair(data, a):
    ad = find_ad(data, a.ad)
    ceiling = a.ceiling or DEFAULT_REPAIR_CEILING
    if len(ad["repairs"]) >= ceiling:
        raise ValueError(f"{a.ad} reached its repair ceiling ({ceiling}); deliver what passed and name what did not")
    ad["repairs"].append({"note": a.note, "at": now()})
    for g in GATES_AD:
        if g in ad:
            ad[g] = {"verdict": "unverified", "at": now(), "by": "ledger", "ref": "repaired; review again"}
    ad.pop("approved", None)


def cmd_approve(data, a):
    ad = find_ad(data, a.ad)
    for g in GATES_AD:
        if ad.get(g, {}).get("verdict") != "pass":
            raise ValueError(f"{a.ad}: {g} has not passed; the member approves reviewed ads")
    ad["approved"] = {"note": a.note, "at": now()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("path"); s.add_argument("--cycle", required=True)
    s.add_argument("--mode", choices=["live", "demo"], default="live")
    s = sub.add_parser("authorize"); s.add_argument("path")
    for f in ("provider", "cap", "units", "note"):
        s.add_argument("--" + f, required=True)
    s = sub.add_parser("plan"); s.add_argument("path")
    for f in ("asset-id", "provider", "model", "prompt-ref"):
        s.add_argument("--" + f, required=True)
    s.add_argument("--kind", choices=sorted(KINDS), default="plate"); s.add_argument("--consent-ref")
    s = sub.add_parser("reserve"); s.add_argument("path")
    for f in ("key", "asset-id", "cost", "quote", "request-ref"):
        s.add_argument("--" + f, required=True)
    s = sub.add_parser("record"); s.add_argument("path"); s.add_argument("--key", required=True)
    s.add_argument("--status", required=True, choices=sorted(STATES))
    for f in ("job-id", "result", "charged", "charge-evidence", "evidence"):
        s.add_argument("--" + f)
    s = sub.add_parser("ad"); s.add_argument("path"); s.add_argument("--ad", required=True)
    for f in ("concept", "layout", "spec"):
        s.add_argument("--" + f)
    s.add_argument("--renders", nargs="*"); s.add_argument("--assets", nargs="*")
    s = sub.add_parser("gate"); s.add_argument("path"); s.add_argument("--gate", required=True)
    s.add_argument("--ad"); s.add_argument("--verdict", required=True)
    s.add_argument("--by", required=True); s.add_argument("--ref", required=True)
    s = sub.add_parser("repair"); s.add_argument("path"); s.add_argument("--ad", required=True)
    s.add_argument("--note", required=True); s.add_argument("--ceiling", type=int)
    s = sub.add_parser("approve"); s.add_argument("path"); s.add_argument("--ad", required=True)
    s.add_argument("--note", required=True)
    s = sub.add_parser("check"); s.add_argument("path")
    s.add_argument("--for-production", action="store_true"); s.add_argument("--for-kit", action="store_true")
    s = sub.add_parser("summary"); s.add_argument("path")
    a = ap.parse_args()
    try:
        path = project_path(a.path)
        with locked(path):
            if a.cmd == "init":
                data = cmd_init(path, a)
                save(path, data)
            else:
                data = load(path)
                handler = {"authorize": cmd_authorize, "plan": cmd_plan, "reserve": cmd_reserve,
                           "record": cmd_record, "ad": cmd_ad, "gate": cmd_gate, "repair": cmd_repair,
                           "approve": cmd_approve}.get(a.cmd)
                if handler:
                    handler(data, a)
                    save(path, data)
                elif a.cmd == "check":
                    errs = errors_for(data, production=a.for_production, kit=a.for_kit)
                    if errs:
                        raise ValueError("; ".join(errs))
            out = summary(data)
            if a.cmd == "check":
                out["ok"] = True
                out["note"] = "Structure only. Truth, taste and compliance need the reviewer and the member."
            print(json.dumps(out, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    return 0


# Imported by gen.py so reservations and records go through the same lock and rules.
def apply(path, fn, **kwargs):
    path = project_path(path)
    with locked(path):
        data = load(path)
        result = fn(data, argparse.Namespace(**kwargs))
        save(path, data)
        return result, data


if __name__ == "__main__":
    sys.exit(main())
