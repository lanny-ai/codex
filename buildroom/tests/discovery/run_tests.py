#!/usr/bin/env python3
"""Discovery Engine: Deep Discovery for a member's own business (scope, ledger, disagreements, gaps, readiness).

Usage:  python3 buildroom/tests/discovery/run_tests.py
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / "skills/buildroom-discovery-engine"
SCRIPT = SK / "scripts/discover.py"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))


def run(*args):
    p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def F(i, field, value, kind, ref, conf, **kw):
    f = {"id": f"f{i}", "field": field, "value": value, "source": {"kind": kind, "ref": ref}, "confidence": conf}
    if "date" in kw:
        f["source"]["date"] = kw.pop("date")
    f.update(kw)
    return f


def main():
    tmp = Path(tempfile.mkdtemp())
    led = tmp / "ledger.json"

    def write(findings, scope=True, **top):
        d = {"subject": "Harbor Coaching", "date": "2026-11-19", "findings": findings, **top}
        if scope:
            d["scope"] = {"read": ["Vault: Offers"], "excluded": ["Personal"], "agreed": "2026-11-19: 'leave out Personal'"}
        led.write_text(json.dumps(d))

    # ---- inventory: names only, private files held back ----------------------------------------
    v = tmp / "vault"
    for rel, body in {"Offers/2026 program pricing.md": "SECRETPRICE 4500", "Clients/testimonials.md": "x", "Notes/random.md": "x",
                      "Personal/diary.md": "x", "Finance/bank statement 2026.pdf": "x", "Admin/passwords.txt": "hunter2",
                      ".obsidian/workspace.json": "{}", "node_modules/pkg/readme.md": "x", "Media/photo.png": "x", ".env": "KEY=1"}.items():
        (v / rel).parent.mkdir(parents=True, exist_ok=True)
        (v / rel).write_text(body)
    c, out = run("inventory", v)
    check("inventory: lists readable files, most useful first", c == 0 and out.index("Offers/2026 program pricing.md") < out.index("Notes/random.md"))
    check("inventory: never prints file contents", "SECRETPRICE" not in out and "hunter2" not in out)
    held = out[out.index("Looks private"):]
    check("inventory: private-looking files are held back, not offered for reading",
          "bank statement" in held and "passwords.txt" in held and "bank statement" not in out[:out.index("Looks private")])
    check("inventory: hidden folders, dependencies and non-text files are skipped", ".obsidian" not in out and "node_modules" not in out and "photo.png" not in out and ".env" not in out)
    check("inventory: says nothing has been opened and asks what to leave out", "Nothing has been opened yet" in out and "leave out" in out)
    c, out = run("inventory", v, "--exclude", "Personal")
    check("inventory: an excluded folder is gone", c == 0 and "diary.md" not in out)
    c, out = run("inventory", v, "--json")
    j = json.loads(out)
    check("inventory: JSON form carries the same split", any("pricing" in f["path"] for f in j["files"]) and any("passwords" in s for s in j["sensitive_not_listed_for_reading"]))
    check("inventory: a missing folder is refused", run("inventory", tmp / "nope")[0] != 0)

    # ---- check: sources and honest confidence -------------------------------------------------
    good = [F(1, "1.what_i_do", "Coaching for clinic owners", "member", "said in session", "confirmed"),
            F(2, "1.price", "$4,500", "file", "Offers/2026 program pricing.md", "likely", date="2026-08-02"),
            F(3, "2.language", "tired of guessing", "web", "https://example.com/reviews", "likely", quote="I'm tired of guessing what to post")]
    write(good)
    c, out = run("check", led)
    check("check: a clean ledger passes", c == 0 and "0 to fix" in out, out)
    write(good, scope=False)
    check("check: no recorded scope agreement fails", run("check", led)[0] == 1 and "scope" in run("check", led)[1])
    write([F(1, "1.price", "$4,500", "file", "a.md", "confirmed")])
    c, out = run("check", led)
    check("check: one source can never be 'confirmed'", c == 1 and "second independent source" in out, out)
    write([F(1, "1.price", "$4,500", "file", "a.md", "confirmed"), F(2, "1.price", "4500 dollars", "web", "https://example.com/work", "confirmed")])
    check("check: two independent sources that agree can be 'confirmed'", run("check", led)[0] == 0, run("check", led)[1])
    write([F(1, "1.price", "$4,500", "web", "https://www.example.com/a", "confirmed"), F(2, "1.price", "$4,500", "web", "https://example.com/b", "confirmed")])
    check("check: two pages of the same website are one source", run("check", led)[0] == 1)
    write([F(1, "2.pains", "no time", "hypothesis", "reasoned from the sales page", "likely")])
    c, out = run("check", led)
    check("check: a hypothesis can only be 'inferred'", c == 1 and "only be 'inferred'" in out)
    bad = [F(1, "9.nope", "x", "file", "a.md", "likely"), F(2, "1.price", "", "file", "a.md", "likely"), F(3, "1.price", "x", "web", "the website", "likely"),
           F(4, "1.price", "x", "file", "", "likely"), F(5, "1.price", "x", "rumour", "x", "likely"), F(6, "1.price", "x", "file", "a.md", "sure"),
           F(7, "x.proof", "doubled revenue", "file", "a.md", "likely"), F(7, "x.voice", "sample", "file", "a.md", "likely")]
    write(bad)
    c, out = run("check", led)
    check("check: catches unknown field, empty value, vague web source, missing path, bad kind, bad confidence, missing quote, repeated id",
          c == 1 and all(x in out for x in ("unknown field", "no value", "full address", "file's path", "source kind", "confirmed, likely or inferred", "exact quote", "used twice")), out)
    led.write_text("{nope")
    check("check: an unreadable ledger is refused plainly", run("check", led)[0] != 0 and "Cannot read" in run("check", led)[1])

    # ---- conflicts: never pick a side ---------------------------------------------------------
    clash = [F(1, "1.price", "$3,000", "file", "Old/proposal.md", "likely", date="2025-03-01"),
             F(2, "1.price", "$4,500", "web", "https://example.com/work", "likely"),
             F(3, "1.lead_sources", "referrals", "file", "a.md", "likely"), F(4, "1.lead_sources", "LinkedIn", "web", "https://example.com", "likely"),
             F(5, "3.offer_name", "The Harbor Method", "file", "a.md", "likely"), F(6, "3.offer_name", "the harbor method.", "web", "https://example.com", "likely")]
    write(clash)
    c, out = run("conflicts", led)
    check("conflicts: two prices from two sources are shown side by side with their dates", "$3,000" in out and "$4,500" in out and "2025-03-01" in out and "Never pick one yourself" in out)
    check("conflicts: list fields and same-meaning values are not disagreements", "Lead sources" not in out and "Offer name" not in out and out.count("to ask the member") == 1 and "1 to ask" in out)
    write(clash + [F(7, "1.price", "$4,500", "member", "said in session", "confirmed")])
    check("conflicts: the member's word settles it", "No disagreements" in run("conflicts", led)[1])
    write([F(1, "1.price", "$3,000", "file", "a.md", "likely"), F(2, "1.price", "$9,000", "hypothesis", "guessed from the market", "inferred")])
    check("conflicts: a guess is not a source that can disagree", "No disagreements" in run("conflicts", led)[1])

    # ---- gaps: few, ranked, disagreements first -----------------------------------------------
    write(clash)
    c, out = run("gaps", led)
    lines = [l for l in out.splitlines() if l[:1].isdigit()]
    check("gaps: at most ten questions", len(lines) == 10, len(lines))
    check("gaps: the disagreement is asked first, quoting both sides", lines[0].startswith("1. Current price") and "$3,000" in lines[0] and "$4,500" in lines[0])
    check("gaps: then the fields most work depends on", "what do you do" in lines[1] and "Who exactly do you serve" in lines[2])
    check("gaps: the four must-know fields come before everything else", all(any(q in l for l in lines[1:5]) for q in ("what do you do", "Who exactly do you serve", "main result", "promise a client")), lines[1:5])
    check("gaps: what is already likely is not asked again", "main offer called" not in out and "How do people find you" not in out)
    check("gaps: the rest is left for the build sessions, by name", "Left for the build sessions" in out and "Tools" in out)
    c, out = run("gaps", led, "--cap", "3")
    check("gaps: the cap can be lowered", len([l for l in out.splitlines() if l[:1].isdigit()]) == 3)
    write([F(1, "2.profile", "Clinic owners with one site", "hypothesis", "reasoned from the home page", "inferred")])
    c, out = run("gaps", led)
    check("gaps: a half-known field quotes the guess and says it is one", "my best guess is “Clinic owners with one site”" in out and "my guess, from" in out)

    # ---- readiness: a guide, with a floor ------------------------------------------------------
    c, out = run("ready", led)
    check("ready: a thin ledger is not ready and says what must be known first", c == 2 and "Not ready yet" in out and "What I do" in out and "Core promise" in out)
    check("ready: always called a guide, not a measurement", "a guide to how much is known, not a measurement" in out)
    import importlib.util
    spec = importlib.util.spec_from_file_location("discover", SCRIPT)
    dm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dm)
    full = [F(i, f[0], "known " + f[0], "member", "said in session", "confirmed", quote="q") for i, f in enumerate(dm.FIELDS)]
    write(full)
    c, out = run("ready", led)
    check("ready: everything confirmed is 100 and ready", c == 0 and "100 out of 100" in out and "Ready:" in out, out)
    write([f for f in full if f["field"] != "3.promise"])
    c, out = run("ready", led)
    check("ready: a high score without the core promise is still not ready", c == 2 and "Core promise" in out and int(out.split("Readiness: ")[1].split()[0]) >= 70, out)
    write([dict(f, source={"kind": "hypothesis", "ref": "reasoned"}, confidence="inferred") for f in full])
    c, out = run("ready", led)
    check("ready: guesses alone never reach ready", c == 2 and int(out.split("Readiness: ")[1].split()[0]) < 70, out)
    write([F(1, "1.price", "$4,500", "file", "a.md", "confirmed")])
    check("ready: refuses to score a ledger that fails its checks", run("ready", led)[0] not in (0, 2))
    w = full + [F(90, "1.price", "$1", "file", "a.md", "likely"), F(91, "1.price", "$2", "web", "https://example.com", "likely")]
    check("ready: weights sum is stable and core fields exist", all(k in dm.FIELD for k in dm.CORE) and sum(f[3] for f in dm.FIELDS) > 0 and len(w) > 0)

    # ---- the page -------------------------------------------------------------------------------
    write(clash + [F(8, "x.voice", "sample", "file", "Posts/a.md", "likely", quote="Here is the thing nobody tells you."),
                   F(9, "2.pains", "no time", "hypothesis", "the sales page", "inferred")])
    c, out = run("page", led)
    check("page: says what was read and what was left alone", "**What I read:** Vault: Offers" in out and "left alone, as you asked:** Personal" in out)
    check("page: every finding shows its confidence and where it came from", "_likely · your file a.md_" in out and "_inferred · my guess, from the sales page_" in out)
    check("page: disagreements are a section of their own, not a chosen answer", "## Things that disagree" in out and "“$3,000”" in out and "**Current price / price range:** $" not in out)
    check("page: voice samples print the exact quote", "“Here is the thing nobody tells you.”" in out)
    check("page: lists what could not be found and ends with the readiness guide", "## What I could not find" in out and "Guarantee" in out and "not a measurement of your business" in out)
    check("page: invites correction", "Correct anything that is wrong. Your word always wins." in out)

    # ---- the script touches nothing it should not ---------------------------------------------
    src = SCRIPT.read_text()
    check("script: standard library only, no network, no writing", not any(x in src for x in ("import requests", "urllib", "socket", "http.client", ".write_text(", "open(")))
    check("script: field labels cover what the method guide names", all(f"`{f[0]}`" in (SK / "references/deep-discovery.md").read_text() for f in dm.FIELDS))

    # ---- the skill's instructions ------------------------------------------------------------------
    sk = (SK / "SKILL.md").read_text()
    ref = (SK / "references/deep-discovery.md").read_text()
    check("skill: Deep Discovery is in the foundation list and the flow", "references/deep-discovery.md" in sk and "### Own business — Deep Discovery" in sk)
    check("skill: scope is agreed before anything is opened", "opens nothing" in sk and "Scope first. Nothing is opened before the member has seen the list and agreed." in ref)
    check("skill: the page is shown before any question", "before asking anything" in sk and "Show the page before asking a single question." in ref)
    check("skill: ten questions at most, skippable", "at most ten" in sk and "Do not go past ten." in ref and "may skip any question" in ref)
    check("skill: disagreements go to the member", "Choose between two sources that disagree. The member decides." in sk and "You never pick. The member does." in ref)
    check("skill: found proof is not permission", "Finding a client result is not permission to use it." in ref and "The Proof Engine session owns consent." in sk)
    check("skill: readiness is a guide and never a promise", "not a prediction of results" in ref and "does not measure the business or predict results" in sk)
    check("skill: only confirmed findings enter the Business File; §2 to §4 stay provisional",
          "do not enter the file as fact" in ref and ref.count("`provisional`") >= 4)
    check("skill: voice samples and proof are saved outside the Business File", "Voice_Samples.md" in ref and "Proof_Found.md" in ref and "never in the file" in sk)
    check("skill: no drive access is forced", "Never ask for a password or a share link" in ref)
    check("skill: client and prospect runs keep the original pipeline", "A client or a prospect still runs the original pipeline" in ref and "Client or prospect." in sk)
    check("skill: the description still fits the listing limit and names the new phrases", "research my business first" in sk.split("---")[1] and len(sk.split("---")[1]) < 700)
    check("reference: no long dashes in the method guide", "—" not in ref and "–" not in ref)
    tpl = (ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_text()
    check("skill: the shared template and protocol copies are untouched", (SK / "references/business-file-template.md").read_text() == tpl)

    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
