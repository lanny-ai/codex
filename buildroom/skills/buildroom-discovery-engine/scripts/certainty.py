#!/usr/bin/env python3
"""Certainty adapter for the Build Room Discovery Engine.

Scores the engine's answer sheet with a decision model, so "is this question
answered by the evidence?" comes back as a calibrated probability instead of a
model's self-assessment. Optional: without a key the engine keeps its
three-word scale (confirmed / likely / inferred).

Providers
  jev     TypeSafe AI's Jev        POST {JEV_API_BASE_URL}/v1/systemone   key: JEV_API_KEY
  openai  OpenAI Decisions API     POST {OPENAI_BASE_URL}/v1/decisions     key: OPENAI_API_KEY

Schema status (2026-10-08)
  jev     request/response shape taken from the vendor's public README
          (model, state, questions keyed by id with type/instructions;
          result.answers keyed by id). Confirm with --probe before relying on it.
  openai  endpoint, model id and the three question types (predicate, choice,
          score) are reported by secondary sources only; the exact field names
          are a best guess held in OPENAI_SHAPE below. Run --probe, read the
          error or the response, and fix OPENAI_SHAPE once. Nothing else changes.

Usage
  certainty.py --dry-run  sheet.json                 print the request bodies, call nothing
  certainty.py --probe    --provider jev|openai      one tiny call to confirm the schema
  certainty.py sheet.json [--provider auto|jev|openai] [--threshold 0.8] [--out scored.json]

Input: sheet.json
  {"subject": "Acme Co",
   "items": [{"id": "q7", "question": "What range of products or services do you offer?",
              "evidence": ["[web: https://acme.com/services] Three packages: ...", "..."]},
             ...],
   "identity": {"candidates": [{"name": "acme.com", "description": "..."}, ...]}   # optional
  }

Output: one record per item with
  state         answered | partial | gap
  p_answered    probability the evidence answers the question (predicate / noul)
  certainty     confirmed (>= threshold) | likely (>= 0.5) | inferred (< 0.5)
  raw           the provider's answer object, untouched

Keys stay in the environment. This script never prints them.
"""
import argparse, json, os, sys, urllib.request, urllib.error

# ---------- OpenAI Decisions API shape (UNVERIFIED: adjust after --probe) ----------
OPENAI_SHAPE = {
    "path": "/v1/decisions",
    "model": "gpt-6-luna",
    # request
    "input_field": "input",          # where the evidence text goes
    "questions_field": "questions",  # list of question objects
    "q_id": "id", "q_text": "question", "q_type": "type", "q_options": "options",
    "type_predicate": "predicate", "type_choice": "choice", "type_score": "score",
    # response
    "answers_field": "answers",      # list or dict of answers
    "a_id": "id", "a_probability": "probability", "a_answer": "answer", "a_probabilities": "probabilities",
}

# ---------- Jev shape (from the vendor README) ----------
JEV_MODEL_DEFAULT = "typesafe/jev-1.13"
JEV_BASE_DEFAULT = "https://thejevai.com"


def _post(url, key, body, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:2000]
        sys.exit(f"{url} -> HTTP {e.code}. The vendor said:\n{detail}\n"
                 f"If this names a field, fix the shape at the top of certainty.py and rerun.")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        sys.exit(f"Could not reach {url}: {getattr(e, 'reason', e)}. Check the base URL and your network; nothing was scored.")


# ---------- request builders ----------
def jev_request(subject, items, identity=None):
    questions = {}
    for it in items:
        questions[it["id"]] = {
            "type": "noul",
            "instructions": (f"Does the evidence directly and reliably answer this question about {subject}: "
                             f"\"{it['question']}\"? Yes only if a sourced fact answers it; "
                             f"no if nothing reliable is present or the answer must be inferred."),
            "criteria": {"true": "a sourced fact in the evidence answers the question",
                         "false": "the evidence is silent, contradictory, or only suggestive"},
        }
    if identity and identity.get("candidates"):
        questions["identity"] = {
            "type": "choice",
            "instructions": f"Which candidate is the real {subject}?",
            "options": [{"name": c["name"], "description": c.get("description", "")}
                        for c in identity["candidates"]] + [{"name": "none-of-the-above",
                                                              "description": "no candidate is clearly the subject"}],
        }
    state = {"subject": subject,
             "evidence": {it["id"]: it.get("evidence", []) for it in items}}
    return {"model": os.environ.get("JEV_MODEL", JEV_MODEL_DEFAULT), "state": state, "questions": questions}


def openai_request(subject, items, identity=None):
    S = OPENAI_SHAPE
    qs = []
    for it in items:
        qs.append({S["q_id"]: it["id"], S["q_type"]: S["type_predicate"],
                   S["q_text"]: (f"The evidence directly and reliably answers this question about {subject}: "
                                 f"\"{it['question']}\"")})
    if identity and identity.get("candidates"):
        qs.append({S["q_id"]: "identity", S["q_type"]: S["type_choice"],
                   S["q_text"]: f"Which candidate is the real {subject}?",
                   S["q_options"]: [c["name"] for c in identity["candidates"]] + ["none-of-the-above"]})
    evidence = "\n\n".join(f"[{it['id']}] {it['question']}\n" + "\n".join(it.get("evidence", []) or ["(no evidence)"])
                           for it in items)
    return {"model": S["model"], S["input_field"]: evidence, S["questions_field"]: qs}


# ---------- response readers ----------
def jev_read(resp):
    answers = (resp.get("result") or {}).get("answers") or resp.get("answers") or {}
    out = {}
    for qid, a in answers.items():
        if qid == "identity":
            out[qid] = {"selected": a.get("selected") or a.get("choice"), "probabilities": a.get("probabilities"),
                        "confidence": a.get("confidence"), "raw": a}
        else:
            p = a.get("noul", a.get("probability"))
            out[qid] = {"p_answered": p, "raw": a}
    return out


def openai_read(resp):
    S = OPENAI_SHAPE
    answers = resp.get(S["answers_field"]) or resp.get("output") or []
    if isinstance(answers, dict):
        answers = [dict(v, **{S["a_id"]: k}) for k, v in answers.items()]
    out = {}
    for a in answers:
        qid = a.get(S["a_id"])
        if qid == "identity":
            out[qid] = {"selected": a.get(S["a_answer"]), "probabilities": a.get(S["a_probabilities"]), "raw": a}
        else:
            out[qid] = {"p_answered": a.get(S["a_probability"]), "raw": a}
    return out


def classify(p, threshold):
    if p is None:
        return "gap", "inferred"
    if p >= threshold:
        return "answered", "confirmed"
    if p >= 0.5:
        return "partial", "likely"
    return "gap", "inferred"


def pick_provider(name):
    if name == "jev" or (name == "auto" and os.environ.get("JEV_API_KEY")):
        return "jev"
    if name == "openai" or (name == "auto" and os.environ.get("OPENAI_API_KEY")):
        return "openai"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheet", nargs="?", help="answer sheet JSON")
    ap.add_argument("--provider", default="auto", choices=["auto", "jev", "openai"])
    ap.add_argument("--threshold", type=float, default=0.8)
    ap.add_argument("--dry-run", action="store_true", help="print request bodies, call nothing")
    ap.add_argument("--probe", action="store_true", help="one tiny call to confirm the schema")
    ap.add_argument("--out", help="write scored JSON here (default: stdout)")
    a = ap.parse_args()

    provider = pick_provider(a.provider)
    if a.probe:
        if not provider:
            sys.exit("No key found. Set JEV_API_KEY or OPENAI_API_KEY in the environment (your .env), then rerun.")
        items = [{"id": "probe", "question": "What is the business called?",
                  "evidence": ["[web: https://example.com] Example Co is a bakery in Austin."]}]
        if provider == "jev":
            body = jev_request("Example Co", items)
            url = os.environ.get("JEV_API_BASE_URL", JEV_BASE_DEFAULT).rstrip("/") + "/v1/systemone"
            resp = _post(url, os.environ["JEV_API_KEY"], body)
            print(json.dumps({"provider": "jev", "parsed": jev_read(resp), "raw_response": resp}, indent=2))
        else:
            body = openai_request("Example Co", items)
            url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/") + OPENAI_SHAPE["path"]
            resp = _post(url, os.environ["OPENAI_API_KEY"], body)
            print(json.dumps({"provider": "openai", "parsed": openai_read(resp), "raw_response": resp}, indent=2))
            print("\nIf 'parsed' is empty, the field names in OPENAI_SHAPE do not match: "
                  "compare raw_response and edit OPENAI_SHAPE once.", file=sys.stderr)
        return

    if not a.sheet:
        ap.error("sheet.json is required unless --probe")
    sheet = json.load(open(a.sheet, encoding="utf-8"))
    subject, items, identity = sheet["subject"], sheet["items"], sheet.get("identity")

    if a.dry_run:
        print(json.dumps({"jev": jev_request(subject, items, identity),
                          "openai": openai_request(subject, items, identity)}, indent=2))
        return

    if not provider:
        sys.exit("No key found. Set JEV_API_KEY or OPENAI_API_KEY (keep them in .env). "
                 "Without a key the Discovery Engine uses its three-word certainty scale instead.")

    if provider == "jev":
        url = os.environ.get("JEV_API_BASE_URL", JEV_BASE_DEFAULT).rstrip("/") + "/v1/systemone"
        parsed = jev_read(_post(url, os.environ["JEV_API_KEY"], jev_request(subject, items, identity)))
    else:
        url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/") + OPENAI_SHAPE["path"]
        parsed = openai_read(_post(url, os.environ["OPENAI_API_KEY"], openai_request(subject, items, identity)))

    scored = []
    for it in items:
        r = parsed.get(it["id"], {})
        state, cert = classify(r.get("p_answered"), a.threshold)
        scored.append({"id": it["id"], "question": it["question"], "state": state,
                       "p_answered": r.get("p_answered"), "certainty": cert, "raw": r.get("raw")})
    result = {"provider": provider, "threshold": a.threshold, "subject": subject, "items": scored}
    if "identity" in parsed:
        result["identity"] = parsed["identity"]
    text = json.dumps(result, indent=2)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"wrote {a.out}: {sum(1 for s in scored if s['state']=='answered')} answered, "
              f"{sum(1 for s in scored if s['state']=='partial')} partial, "
              f"{sum(1 for s in scored if s['state']=='gap')} gap")
    else:
        print(text)


if __name__ == "__main__":
    main()
