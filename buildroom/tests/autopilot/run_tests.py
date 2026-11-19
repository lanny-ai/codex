#!/usr/bin/env python3
"""Autopilot: the run keeper (plan, order, review gate, report) and the Foundation Reveal page.

Usage:  python3 buildroom/tests/autopilot/run_tests.py
"""
import copy, importlib.util, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / "skills/buildroom-autopilot"
AP, RV = SK / "scripts/autopilot.py", SK / "scripts/reveal.py"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))


def run(script, *args):
    p = subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


c = lambda v: {"v": v, "basis": "confirmed"}  # noqa: E731
f = lambda v, s: {"v": v, "basis": "files", "source": s}  # noqa: E731
d = lambda v: {"v": v, "basis": "drafted"}  # noqa: E731
GOOD = {"business": "Harbor <Coaching>", "date": "November 19, 2026",
        "avatar": {"name": d("Dana the Clinic Owner"), "profile": f("Owns one clinic and still treats patients.", "Clients/intake.md"),
                   "language": [f("Every month starts at zero.", "Call transcript, 2026-09-14"), f("I'm tired of <guessing>.", "Google review")],
                   "pain_surface": c("New patients swing month to month."), "objections_spoken": [c("No time."), d("Tried an agency.")]},
        "offer": {"name": c("The Full Schedule Program"), "promise": c("A steady flow of the right new patients."), "phases": [c("Weeks 1 to 3"), d("Weeks 4 to 8")],
                  "investment": c("$4,500"), "guarantee": f("Work with me until it moves.", "Offers/2026.md")},
        "positioning": {"differentiator": c("I filled my own clinic first."), "tagline": d("Fill the schedule."), "for_you": [c("You own one clinic")]}}


def main():
    tmp = Path(tempfile.mkdtemp())
    am, rm = mod(AP, "autopilot"), mod(RV, "reveal")

    # ---- every tool is classified ------------------------------------------------------------
    on_disk = {p.name[len("buildroom-"):] for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists()}
    listed = [t[0] for t in am.TOOLS]
    check("plan: every Build Room tool is classified, once, and nothing else", set(listed) == on_disk and len(listed) == len(set(listed)),
          f"missing {sorted(on_disk - set(listed))}, extra {sorted(set(listed) - on_disk)}")
    check("plan: every tool left out says why", all(t[4] for t in am.TOOLS if t[3] == "needs_you"))
    modes = {t[0]: t[3] for t in am.TOOLS}
    check("plan: nothing that spends, publishes media or needs real data runs on its own",
          all(modes[s] == "needs_you" for s in ("ad-studio", "video-director", "website-design-studio", "proof-engine", "funnel-scorecard", "ops-dashboard", "compass", "hiring-kit")))
    check("plan: the foundation is the avatar, the offer and the positioning, in that order",
          [t[0] for t in am.TOOLS if t[3] == "foundation"][1:] == ["ideal-client-avatar", "signature-offer", "positioning-messaging"] == list(am.MUST))
    guide = (ROOT / "connector/guide.html").read_text()
    names = dict(re.findall(r'^ \["[a-z]+","([a-z-]+)","([^"]+)"', guide, re.M))
    check("plan: tool names match the public guide", all(names.get(t[0]) == t[1] for t in am.TOOLS), [t[0] for t in am.TOOLS if names.get(t[0]) != t[1]])

    # ---- preflight -------------------------------------------------------------------------------
    tpl = (ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_text()
    bf = tmp / "BUILDROOM_BUSINESS_FILE.md"
    bf.write_text(tpl)
    code, out = run(AP, "preflight", bf)
    check("preflight: a blank file is not ready and is sent to Deep Discovery", code == 2 and "Not ready" in out and "Research my business first" in out and "What I do" in out)
    filled = tpl.replace("- **What I do:**", "- **What I do:** Coaching for clinic owners").replace(
        "- **Who I serve (niche + segment):**", "- **Who I serve (niche + segment):** Owners of one clinic").replace(
        "- **Core result I deliver:**", "- **Core result I deliver:** A full schedule")
    bf.write_text(filled)
    code, out = run(AP, "preflight", bf)
    check("preflight: a filled snapshot is ready, and says the rest will be drafted", code == 0 and "Ready to start" in out and "drafted from scratch" in out, out)
    check("preflight: no file at all is refused", run(AP, "preflight", tmp / "nope.md")[0] == 2)

    # ---- the run: order and the review gate ---------------------------------------------------
    D = tmp / "autopilot"
    code, out = run(AP, "plan", "--dir", D)
    check("plan: lists foundation then the run, review not yet", code == 0 and out.index("Ideal Client Avatar") < out.index("Offer Page Copy") and "Review: not yet" in out)
    check("plan: a second plan over an unfinished run is refused", run(AP, "plan", "--dir", D)[0] != 0)
    check("plan: the three core sessions cannot be skipped", run(AP, "plan", "--dir", tmp / "x", "--skip", "signature-offer")[0] != 0)
    check("plan: a tool outside the run cannot be 'skipped'", run(AP, "plan", "--dir", tmp / "x", "--skip", "ad-studio")[0] != 0)
    code, out = run(AP, "plan", "--dir", tmp / "y", "--skip", "linkedin", "--no-web")
    check("plan: a member can leave a step out; no web access drops the research step", code == 0 and "[skipped] LinkedIn Engine" in out and "[skipped] Audience Insight  (no web access" in out)

    nxt = lambda: run(AP, "next", "--dir", D)  # noqa: E731
    done = lambda slug, *a: run(AP, "done", "--dir", D, slug, *a)  # noqa: E731
    check("next: starts with the research step", "Audience Insight" in nxt()[1])
    check("done: out of order is refused", done("signature-offer", "--status", "drafted", "--outputs", "x.md")[0] != 0)
    check("done: drafted needs its outputs", done("audience-insight", "--status", "drafted")[0] != 0)
    check("done: blocked needs a reason", done("audience-insight", "--status", "blocked")[0] != 0)
    check("done: a blocked research step is allowed", done("audience-insight", "--status", "blocked", "--note", "no public reviews found")[0] == 0)
    check("approve: nothing to approve before the foundation is drafted", run(AP, "approve", "--dir", D, "--words", "go")[0] != 0)
    check("done: a core session cannot be skipped mid-run", done("ideal-client-avatar", "--status", "skipped", "--note", "x")[0] != 0)
    for s in ("ideal-client-avatar", "signature-offer", "positioning-messaging"):
        code, out = done(s, "--status", "drafted", "--outputs", f"{s}.md", "--gaps", "client proof")
        check(f"done: {s} recorded", code == 0)
    code, out = nxt()
    check("next: stops for the review before anything else runs", code == 3 and out.startswith("REVIEW") and "Nothing else runs until then" in out)
    check("done: a run step cannot be recorded before the review", done("offer-deep-dive", "--status", "drafted", "--outputs", "x.md")[0] != 0)
    check("approve: needs the member's own words", run(AP, "approve", "--dir", D)[0] != 0 and run(AP, "approve", "--dir", D, "--words", " ")[0] != 0)
    check("approve: records the go-ahead", run(AP, "approve", "--dir", D, "--words", "Looks right, go")[0] == 0
          and json.loads((D / "run.json").read_text())["approved"]["words"] == "Looks right, go")
    check("next: the run starts after the review", "Offer Deep Dive" in nxt()[1] and nxt()[0] == 0)
    done("offer-deep-dive", "--status", "blocked", "--note", "no prices for comparison")
    done("offer-page-copy", "--status", "drafted", "--outputs", "Offer_Page.md", "--gaps", "two testimonials")
    code, out = run(AP, "status", "--dir", D)
    check("status: resumable, shows what is done and what is pending", "[drafted] Offer Page Copy" in out and "[pending] Funnel Map" in out and "approved" in out)
    code, out = run(AP, "report", "--dir", D)
    check("report: drafted work with where it is saved and what it still needs", "### Offer Page Copy" in out and "Saved as: Offer_Page.md" in out and "Still needs you: two testimonials" in out)
    check("report: what could not be drafted, with the sentence to run it", "**Offer Deep Dive:** no prices for comparison" in out and "“Make my offer a no-brainer”" in out)
    check("report: unfinished steps are named, with how to carry on", "## Not reached yet" in out and "Funnel Map" in out and "Run autopilot" in out)
    check("report: every tool that needs the member is listed with its reason and start phrase",
          all(f"**{t[1]}:** {t[4]}. Say “{t[2]}”." in out for t in am.TOOLS if t[3] == "needs_you"))
    check("report: says nothing was published, sent or paid for, and promises nothing", "Nothing was published, sent or paid for." in out
          and not re.search(r"guarantee|will (get|bring|double)|more clients", out, re.I))
    # a core session that could not be drafted stops the run
    D2 = tmp / "ap2"
    run(AP, "plan", "--dir", D2, "--no-web")
    run(AP, "done", "--dir", D2, "ideal-client-avatar", "--status", "drafted", "--outputs", "a.md")
    run(AP, "done", "--dir", D2, "signature-offer", "--status", "blocked", "--note", "no price known")
    run(AP, "done", "--dir", D2, "positioning-messaging", "--status", "drafted", "--outputs", "p.md")
    code, out = run(AP, "next", "--dir", D2)
    check("next: a blocked core session stops the run and says to ask the member", code == 4 and "Signature Offer" in out and "Do not go on without it" in out)
    check("approve: cannot approve a foundation with a hole in it", run(AP, "approve", "--dir", D2, "--words", "go")[0] != 0)
    check("next: with no run, says how to start one", "Start one with" in run(AP, "next", "--dir", tmp / "none")[1])
    (tmp / "bad").mkdir()
    (tmp / "bad/run.json").write_text("{nope")
    check("a damaged run file is never silently replaced", "Do not start over" in run(AP, "status", "--dir", tmp / "bad")[1])
    src = AP.read_text()
    check("run keeper: standard library only, no network", not any(x in src for x in ("requests", "urllib", "socket", "http.client", "subprocess")))

    # ---- the Foundation Reveal ------------------------------------------------------------------
    fj = tmp / "foundation.json"

    def write(obj):
        fj.write_text(json.dumps(obj))

    write(GOOD)
    code, out = run(RV, "check", fj)
    check("reveal: a clean foundation passes and counts its lines", code == 0 and "8 confirmed, 4 from files, 4 drafted" in out and "0 to fix" in out, out)
    page = tmp / "Foundation_Reveal.html"
    code, out = run(RV, "build", fj, page)
    html = page.read_text()
    check("reveal: builds one self-contained page", code == 0 and html.startswith("<!doctype html>") and not re.search(r'(src|href)="https?:', html) and "@import" not in html and "url(" not in html)
    check("reveal: shows the three counts", all(x in html for x in ("<b>8</b><span>lines confirmed by you", "<b>4</b><span>lines from your own files", "<b>4</b><span>lines drafted for you")))
    check("reveal: every line carries its tag, and file lines carry their source", html.count('class="b drafted"') >= 5 and 'title="From your files: Clients/intake.md"' in html)
    check("reveal: client quotes show who said them", "Call transcript, 2026-09-14" in html and "<blockquote>" in html)
    check("reveal: everything is escaped", "Harbor &lt;Coaching&gt;" in html and "&lt;guessing&gt;" in html and "<guessing>" not in html and "<Coaching>" not in html)
    check("reveal: the three parts and the review form are there", all(x in html for x in ('id="avatar"', 'id="offer"', 'id="positioning"', "Copy my review", 'value="Looks right"', 'value="Change this"')))
    check("reveal: says nothing goes further without the member, and promises no results", "Nothing goes further until you say so." in html and "It does not promise results." in html)
    check("reveal: blanks are listed as still open, not filled", "Still open" in html and "Your offer: The 60-second pitch" in html and "left blank instead of guessed" in html)
    check("reveal: prints cleanly and works on a phone", "@media print" in html and "@media (max-width:760px)" in html)
    check("reveal: no long dashes on the page", "—" not in html and "–" not in html)
    code, out = run(RV, "text", fj)
    check("reveal: the chat version carries the same tags and the same review ask", code == 0 and "[draft]" in out and "[files]" in out and "“Every month starts at zero.” (Call transcript, 2026-09-14)" in out
          and "Nothing goes further until you say so." in out)

    def bad(mut, needle, name):
        g = copy.deepcopy(GOOD)
        mut(g)
        write(g)
        code, out = run(RV, "check", fj)
        check(f"reveal: {name}", code == 1 and needle in out, out)
        check(f"reveal: and refuses to build it ({name})", run(RV, "build", fj, tmp / "no.html")[0] == 1 and not (tmp / "no.html").exists())

    bad(lambda g: g["avatar"]["language"].append(d("I just want more clients")), "a drafted line is not a client's words", "a drafted line can never sit among client quotes")
    bad(lambda g: g["avatar"]["language"].append(c("We love it")), "needs who said it", "a quote with no source is refused")
    bad(lambda g: g["offer"].update(investment=d("$5,000")), "is a fact", "a price is never drafted")
    bad(lambda g: g["offer"].update(guarantee=d("Double your money back")), "is a fact", "a guarantee is never drafted")
    bad(lambda g: g["offer"].update(urgency=d("Only 3 spots left")), "is a fact", "a deadline or scarcity line is never drafted")
    bad(lambda g: g["avatar"].update(profile={"v": "x", "basis": "files"}), "needs the source", "a line from files must name its source")
    bad(lambda g: g["avatar"].update(profile="plain string"), "where it came from", "an untagged line is refused")
    bad(lambda g: g["avatar"].update(profile={"v": "x", "basis": "certain"}), "confirmed, files or drafted", "an unknown tag is refused")
    bad(lambda g: g["offer"].pop("promise"), "needed before the page is worth showing", "no promise, no page")
    bad(lambda g: g["offer"].update(bonus=c("x")), "not a field this page knows", "an unknown field is refused")
    bad(lambda g: g.pop("positioning"), "positioning: missing", "a missing part is refused")
    write(GOOD)
    check("reveal: output must be an .html file", run(RV, "build", fj, tmp / "out.txt")[0] != 0)
    rsrc = RV.read_text()
    check("reveal: standard library only, no network", not any(x in rsrc for x in ("requests", "urllib", "socket", "http.client", "subprocess")))
    ref = (SK / "references/foundation-reveal.md").read_text()
    check("reveal: every field the page knows is documented", all(f"`{k}`" in ref for _p, _t, fs in rm.PARTS for k, _l, _k in fs))

    # ---- the skill's instructions ------------------------------------------------------------------
    sk = (SK / "SKILL.md").read_text()
    me = (SK / "references/autopilot-method.md").read_text()
    head = sk.split("---")[1]
    check("skill: name, start phrases and a description that fits the listing", "name: buildroom-autopilot" in head and "run autopilot" in head and len(head) < 700)
    check("skill: needs a filled snapshot, a folder, and recommends Deep Discovery first", "autopilot.py preflight" in sk and "Cowork, Claude Code or Codex" in sk and "Deep Discovery first" in sk)
    check("skill: one stop, and only the member's own go-ahead passes it", "Never record a go-ahead they did not give." in sk and "Silence, or your own judgement that it is good, is not." in me)
    check("skill: never invents a fact to fill a blank", "A blank stays a marked blank." in sk and "A page with three invented facts is harmful." in me)
    check("skill: facts that are never drafted are named", all(x in me for x in ("prices, numbers, dates", "client names, quotes, testimonials and results", "credentials, awards", "guarantees and their terms")))
    check("skill: imagined client words never become quotes", "never **Sourced language**" in me and "never inside quotation marks" in me)
    check("skill: never publishes, sends, spends or connects an account", "Publish, send, post, spend, or connect an account." in sk and "Spend money or generate paid media." in me)
    check("skill: stays inside the file scope the member agreed", "Do not read outside that scope." in me)
    check("skill: no questions during the unattended phases", "Never ask a question during Phase 2 or Phase 4." in sk)
    check("skill: sections with drafted lines stay provisional", "Mark a section `complete` while it still holds drafted lines." in sk and "Sections written in Phase 4 are always `provisional`." in me)
    check("skill: keeps what the member already built and never uses retired lines", "do not rewrite a section the member built" in me and "Retired lines in §1 are never used" in me)
    check("skill: resumes, never starts over", "do not start over" in sk and "Never start a second run over an unfinished one." in me)
    check("skill: the method's tool groups match the run keeper", all(t[1] in me for t in am.TOOLS if t[0] != "autopilot"), [t[1] for t in am.TOOLS if t[1] not in me])
    check("skill: the presentation says little and does not praise itself", "Do not summarise the page in the chat, do not tell them it is good, and do not ask a question." in ref)
    check("skill: no promise of results anywhere in its instructions", "No promise of leads, clients, revenue or results" in sk)
    check("skill: no long dashes in its instructions", all("—" not in t and "–" not in t for t in (sk, me, ref)))
    check("skill: carries the shared protocol and template unchanged", (SK / "references/business-file-template.md").read_text() == tpl
          and (SK / "references/business-file-protocol.md").read_text() == (ROOT / "shared/business-file-protocol.md").read_text())

    # ---- wired in -----------------------------------------------------------------------------
    rd = lambda p: (ROOT / p).read_text()  # noqa: E731
    check("wired: the guide lists Autopilot with its start phrase", '"autopilot","Autopilot","Run autopilot"' in guide)
    check("wired: the roadmap names it and its phrases", "buildroom-autopilot" in rd("skills/buildroom-os/references/roadmap.md") and '"Run autopilot"' in rd("skills/buildroom-os/references/roadmap.md"))
    check("wired: the protocol counts forty-two sessions", "42 standalone sessions" in rd("shared/business-file-protocol.md"))
    check("wired: there are forty-two skills", len(on_disk) == 42, len(on_disk))
    check("wired: the member README and the repo README list it", "buildroom-autopilot" in rd("rollout/MEMBER-README.md") and "buildroom-autopilot" in rd("README.md"))

    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
