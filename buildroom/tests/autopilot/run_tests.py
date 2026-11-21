#!/usr/bin/env python3
"""Autopilot: the run keeper (plan, decisions, order, review gate, report), the Foundation Reveal and the Your Build page.

Usage:  python3 buildroom/tests/autopilot/run_tests.py
"""
import copy, importlib.util, json, re, subprocess, sys, tempfile
from html import escape as html_escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / "skills/buildroom-autopilot"
AP, RV, HV = SK / "scripts/autopilot.py", SK / "scripts/reveal.py", SK / "scripts/handover.py"
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
d = lambda v, s=None: {"v": v, "basis": "drafted", **({"source": s} if s else {})}  # noqa: E731
GOOD = {"business": "Harbor <Coaching>", "date": "November 19, 2026",
        "avatar": {"name": d("Dana the Clinic Owner"), "profile": f("Owns one clinic and still treats patients.", "Clients/intake.md"),
                   "language": [f("Every month starts at zero.", "Call transcript, 2026-09-14"), f("I'm tired of <guessing>.", "Google review")],
                   "pain_surface": c("New patients swing month to month."), "objections_spoken": [c("No time."), d("Tried an agency.", "my wording; you skipped this question")]},
        "offer": {"name": c("The Full Schedule Program"), "promise": c("A steady flow of the right new patients."), "phases": [c("Weeks 1 to 3"), d("Weeks 4 to 8")],
                  "investment": c("$4,500"), "guarantee": f("Work with me until it moves.", "Offers/2026.md")},
        "positioning": {"differentiator": c("I filled my own clinic first."), "tagline": d("Fill the schedule."), "for_you": [c("You own one clinic")]}}
D = "autopilot/drafts/"


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
    check("plan: the sessions that came back half blank in the trials are the member's to start",
          all(modes[s] == "needs_you" for s in ("offer-deep-dive", "linkedin", "search-answer-engine")))
    check("plan: the foundation is the avatar, the offer and the positioning, in that order",
          [t[0] for t in am.TOOLS if t[3] == "foundation"][1:] == ["ideal-client-avatar", "signature-offer", "positioning-messaging"] == list(am.MUST))
    check("plan: every session a run drafts has a stated scope", all(t[0] in am.SCOPE and len(am.SCOPE[t[0]]) > 40 for t in am.TOOLS if t[3] in ("foundation", "auto"))
          and set(am.SCOPE) == {t[0] for t in am.TOOLS if t[3] in ("foundation", "auto")})
    sc = am.SCOPE
    check("plan: the scopes rule out what the sessions' own prompts ask for",
          "no invented complaints" in sc["ideal-client-avatar"] and "testimonial fragments" in sc["ideal-client-avatar"] and "dollar values per deliverable" in sc["signature-offer"]
          and "composite" in sc["offer-page-copy"] and "do not write a second one" in sc["decision-machine"] and "One module only" in sc["leadgen"] and "do not write as if it exists" in sc["lead-capture"])
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
    check("preflight: a filled snapshot lets a run be planned, without calling it ready", code == 0 and "a run can be planned" in out and "Ready to start" not in out)
    check("preflight: says it does not measure how much is known, and points at the readiness number", "does not say how much is known" in out and "--readiness" in out)
    check("preflight: no file at all is refused", run(AP, "preflight", tmp / "nope.md")[0] == 2)
    check("preflight: forgetting the file gives a usage error, not a crash", "required" in run(AP, "preflight")[1])

    # ---- planning: readiness is part of the plan --------------------------------------------------
    Dr = tmp / "autopilot"
    check("plan: readiness must be given", run(AP, "plan", "--dir", tmp / "r0")[0] != 0)
    code, out = run(AP, "plan", "--dir", tmp / "r1", "--readiness", "31")
    check("plan: a thin file is refused, with the three choices to offer", code == 5 and "Readiness is 31 out of 100" in out and "mostly blanks and guesses" in out
          and "answer the questions" in out and "--thin-ok" in out and not (tmp / "r1/run.json").exists(), out)
    code, out = run(AP, "plan", "--dir", tmp / "r2", "--readiness", "none")
    check("plan: no discovery at all is refused the same way", code == 5 and "no discovery ledger" in out)
    code, out = run(AP, "plan", "--dir", tmp / "r3", "--readiness", "31", "--thin-ok", "I know, go ahead anyway")
    check("plan: the member's own choice to go ahead is recorded and shown", code == 0 and "31 out of 100 (the member chose to go ahead: “I know, go ahead anyway”)" in out)
    check("plan: a made-up readiness is refused", run(AP, "plan", "--dir", tmp / "r4", "--readiness", "lots")[0] != 0 and run(AP, "plan", "--dir", tmp / "r4", "--readiness", "140")[0] != 0)
    code, out = run(AP, "plan", "--dir", Dr, "--readiness", "81")
    check("plan: lists foundation then the run, review not yet", code == 0 and out.index("Ideal Client Avatar") < out.index("Offer Page Copy") and "Review: not yet" in out and "81 out of 100" in out)
    check("plan: a second plan over an unfinished run is refused", run(AP, "plan", "--dir", Dr, "--readiness", "81")[0] != 0)
    check("plan: the three core sessions cannot be skipped", run(AP, "plan", "--dir", tmp / "x", "--readiness", "81", "--skip", "signature-offer")[0] != 0)
    check("plan: a tool outside the run cannot be 'skipped'", run(AP, "plan", "--dir", tmp / "x", "--readiness", "81", "--skip", "linkedin")[0] != 0)
    code, out = run(AP, "plan", "--dir", tmp / "y", "--readiness", "81", "--skip", "leadgen", "--no-web")
    check("plan: a member can leave a step out; no web access drops the research step", code == 0 and "[skipped] Lead Gen Machine" in out and "[skipped] Audience Insight  (no web access" in out)

    # ---- decisions: the member's rules travel with the run ---------------------------------------
    dec = lambda k, v: run(AP, "decide", "--dir", Dr, "--key", k, "--value", v)  # noqa: E731
    check("decide: records an answer", dec("price", "$4,500")[0] == 0 and dec("never_claim", "any medical outcome")[0] == 0 and dec("guarantee", "none")[0] == 0)
    check("decide: an unknown key and an empty answer are refused", dec("mood", "fine")[0] != 0 and dec("price", " ")[0] != 0)
    dec("never_claim", "any medical outcome, and doubling anything")
    code, out = run(AP, "next", "--dir", Dr)
    check("next: starts with the research step, with its scope and where to save", "Audience Insight" in out and "SCOPE  Public research only" in out and "SAVE  every document under autopilot/drafts/" in out)
    check("next: what the member refuses to claim and their guarantee are printed for every session, latest answer only",
          "RULE  Never claim or promise: any medical outcome, and doubling anything" in out and "RULE  Guarantee, exact wording, or none: none" in out
          and out.count("Never claim") == 1 and "RULE  Price" not in out)

    # ---- the run: order, where drafts go, and the review gate -----------------------------------
    nxt = lambda: run(AP, "next", "--dir", Dr)  # noqa: E731
    done = lambda slug, *a: run(AP, "done", "--dir", Dr, slug, *a)  # noqa: E731
    check("done: out of order is refused", done("signature-offer", "--status", "drafted", "--outputs", D + "x.md")[0] != 0)
    check("done: drafted needs its outputs", done("audience-insight", "--status", "drafted")[0] != 0)
    check("done: blocked needs a reason", done("audience-insight", "--status", "blocked")[0] != 0)
    check("done: a blocked research step is allowed", done("audience-insight", "--status", "blocked", "--note", "no public reviews found")[0] == 0)
    check("approve: nothing to approve before the foundation is drafted", run(AP, "approve", "--dir", Dr, "--words", "go")[0] != 0)
    check("done: a core session cannot be skipped mid-run", done("ideal-client-avatar", "--status", "skipped", "--note", "x")[0] != 0)
    code, out = done("ideal-client-avatar", "--status", "drafted", "--outputs", "ICA_Document.md")
    check("done: a draft saved outside autopilot/drafts is refused", code != 0 and "never mistaken for the member's own files" in out)
    check("done: nor a path that climbs out of the folder", done("ideal-client-avatar", "--status", "drafted", "--outputs", D + "../../x.md")[0] != 0)
    check("done: partial must say what was and was not drafted", done("ideal-client-avatar", "--status", "partial", "--outputs", D + "01.md")[0] != 0)
    check("done: a partly drafted core session is recorded as partial", done("ideal-client-avatar", "--status", "partial", "--outputs", D + "01_ICA.md", "--gaps", "A booking link",
          "--note", "Profile and pains drafted; triggers and objections unknown")[0] == 0)
    for i, s in enumerate(("signature-offer", "positioning-messaging"), 2):
        check(f"done: {s} recorded", done(s, "--status", "drafted", "--outputs", f"{D}0{i}_{s}.md", "--gaps", "A booking link", "a typical client result")[0] == 0)
    code, out = nxt()
    check("next: stops for the review before anything else runs", code == 3 and out.startswith("REVIEW") and "Nothing else runs until then" in out)
    check("done: a run step cannot be recorded before the review", done("offer-page-copy", "--status", "drafted", "--outputs", D + "x.md")[0] != 0)
    check("approve: needs the member's own words", run(AP, "approve", "--dir", Dr)[0] != 0 and run(AP, "approve", "--dir", Dr, "--words", " ")[0] != 0)
    check("approve: records the go-ahead", run(AP, "approve", "--dir", Dr, "--words", "Looks right, go")[0] == 0
          and json.loads((Dr / "run.json").read_text())["approved"]["words"] == "Looks right, go")
    code, out = nxt()
    check("next: the run starts after the review, with the offer page, its scope and the standing rules", code == 0 and "Offer Page Copy" in out and "composite" in out and "RULE  Never claim" in out)
    done("offer-page-copy", "--status", "drafted", "--outputs", D + "04_Offer_Page.md", "--gaps", "A booking link.", "Two testimonials you may use")
    done("funnel-map", "--status", "blocked", "--note", "No tools known, so the sequence has nowhere to live")
    code, out = run(AP, "status", "--dir", Dr)
    check("status: resumable, shows what is done and what is pending", "[drafted] Offer Page Copy" in out and "[partial] Ideal Client Avatar" in out and "[pending] Lead Capture" in out and "approved" in out)
    code, out = run(AP, "report", "--dir", Dr)
    check("report: opens with what to do first, built from the gaps that repeat", out.index("## What to do first") < out.index("## Drafted for you")
          and "1. A booking link (needed by Ideal Client Avatar, Signature Offer, Positioning & Messaging, Offer Page Copy)" in out, out[:900])
    check("report: the same gap worded twice is counted once", out.count("A booking link (needed by") == 1)
    check("report: says how ready the file was and what the member said at the start and at the review", "Readiness when it started: 81 out of 100." in out
          and "## What you told me at the start" in out and "**Never claim or promise:** any medical outcome, and doubling anything" in out and "“Looks right, go”" in out)
    check("report: partly drafted work is set apart from drafted work", "## Partly drafted" in out and "What was and was not drafted: Profile and pains drafted" in out
          and out.index("## Drafted for you") < out.index("## Partly drafted"))
    check("report: drafted work with where it is saved and what it still needs", "### Offer Page Copy" in out and "Saved as: autopilot/drafts/04_Offer_Page.md" in out and "Still needs you: Two testimonials you may use" in out)
    check("report: what could not be drafted, with the sentence to run it", "**Funnel Map:** No tools known" in out and "“Help me map my funnel”" in out)
    check("report: unfinished steps are named, with how to carry on", "## Not reached yet" in out and "Lead Capture" in out and "Run autopilot" in out)
    check("report: every tool that needs the member is listed with its reason and start phrase, and says to pick what fits",
          all(f"**{t[1]}:** {t[4]}. Say “{t[2]}”." in out for t in am.TOOLS if t[3] == "needs_you") and "Not all of them will fit your business" in out)
    check("report: says nothing was published, sent or paid for, and promises nothing", "Nothing was published, sent or paid for." in out
          and not re.search(r"will (get|bring|double)|more clients|guaranteed", out, re.I))
    # a core session that could not be drafted stops the run
    D2 = tmp / "ap2"
    run(AP, "plan", "--dir", D2, "--readiness", "75", "--no-web")
    run(AP, "done", "--dir", D2, "ideal-client-avatar", "--status", "drafted", "--outputs", D + "a.md")
    run(AP, "done", "--dir", D2, "signature-offer", "--status", "blocked", "--note", "no confirmed core result to restate")
    run(AP, "done", "--dir", D2, "positioning-messaging", "--status", "drafted", "--outputs", D + "p.md")
    code, out = run(AP, "next", "--dir", D2)
    check("next: a blocked core session stops the run and says to ask the member", code == 4 and "Signature Offer" in out and "Do not go on without it" in out)
    check("approve: cannot approve a foundation with a hole in it", run(AP, "approve", "--dir", D2, "--words", "go")[0] != 0)
    check("report: with no gaps at all, the first steps are still given", "1. Read the drafts" in run(AP, "report", "--dir", D2)[1])
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
    check("reveal: a clean foundation passes and counts its lines", code == 0 and "8 confirmed, 4 from files, 4 drafted, 0 approved drafts" in out and "0 to fix" in out, out)
    page = tmp / "Foundation_Reveal.html"
    code, out = run(RV, "build", fj, page)
    html = page.read_text()
    check("reveal: builds one self-contained page", code == 0 and html.startswith("<!doctype html>") and not re.search(r'(src|href)="https?:', html) and "@import" not in html and "url(" not in html)
    check("reveal: shows four counts, including what was left blank", all(x in html for x in ("<b>8</b><span>lines confirmed by you", "<b>4</b><span>lines from your own files",
          "<b>4</b><span>lines drafted for you to check", "</b><span>things left blank instead of guessed")))
    check("reveal: where a line came from is printed beside it, not hidden behind a hover", '<span class="src">Clients/intake.md</span>' in html
          and '<span class="src">my wording; you skipped this question</span>' in html and 'title="' not in html)
    check("reveal: every line carries its tag", html.count('class="b drafted"') >= 4 and html.count('class="b files"') >= 4)
    check("reveal: client quotes show where they were found, once", html.count("Call transcript, 2026-09-14") == 1 and "<blockquote>" in html)
    check("reveal: everything is escaped", "Harbor &lt;Coaching&gt;" in html and "&lt;guessing&gt;" in html and "<guessing>" not in html and "<Coaching>" not in html)
    check("reveal: the three parts, the review form and an explicit go-ahead are there", all(x in html for x in ('id="avatar"', 'id="offer"', 'id="positioning"', "Copy my review",
          'value="Looks right"', 'value="Change this"', 'id="go"', "Go ahead: ")))
    check("reveal: says nothing goes further without the member, and promises no results", "Nothing goes further until you say so." in html and "It does not promise results." in html)
    check("reveal: blanks are listed as still open, not filled", "Still open" in html and "Your offer: The 60-second pitch" in html and "left blank instead of guessed" in html)
    check("reveal: labels fit a person as well as a business", "What they want first" in html or "What they want first" in RV.read_text())
    check("reveal: prints cleanly and works on a phone", "@media print" in html and "@media (max-width:760px)" in html)
    check("reveal: no long dashes on the page", "—" not in html and "–" not in html)
    code, out = run(RV, "text", fj)
    check("reveal: the chat version carries the same tags, the sources and the same review ask", code == 0 and "[draft] (my wording; you skipped this question)" in out
          and "[files] (Clients/intake.md)" in out and "“Every month starts at zero.” [files] (Call transcript, 2026-09-14)" in out and "whether to go ahead" in out)
    # after the review: approved drafts are their own thing
    g = copy.deepcopy(GOOD)
    g["avatar"]["name"]["basis"] = "reviewed"
    g["positioning"]["tagline"]["basis"] = "reviewed"
    write(g)
    code, out = run(RV, "check", fj)
    run(RV, "build", fj, page)
    h2 = page.read_text()
    check("reveal: an approved draft is tagged as an approved draft, never as confirmed", code == 0 and "2 approved drafts" in out and 'class="b reviewed"' in h2
          and "Drafted, approved by you" in h2 and "<b>8</b><span>lines confirmed by you" in h2 and "<b>4</b><span>lines drafted for you, 2 of them approved by you" in h2)
    g = copy.deepcopy(GOOD)
    g["positioning"] = {"alternative": c("Hire a general agency.")}
    write(g)
    check("reveal: positioning may lead with the alternative when no honest differentiator exists", run(RV, "build", fj, page)[0] == 0 and "What they would do without you" in page.read_text())

    def bad(mut, needle, name, extra=()):
        g = copy.deepcopy(GOOD)
        mut(g)
        write(g)
        code, out = run(RV, "check", fj, *extra)
        check(f"reveal: {name}", code == 1 and needle in out, out)
        check(f"reveal: and refuses to build it ({name})", run(RV, "build", fj, tmp / "no.html", *extra)[0] == 1 and not (tmp / "no.html").exists())

    bad(lambda g: g["avatar"]["language"].append(d("I just want more clients")), "a drafted line is not a client's words", "a drafted line can never sit among client quotes")
    bad(lambda g: g["avatar"]["language"].append(f("Marcus doubled my revenue", "a client")), "needs where it was found", "a quote that says only who, not where, is refused")
    bad(lambda g: g["avatar"]["language"].append(c("We love it")), "needs where it was found", "a quote with no source is refused")
    bad(lambda g: g["offer"].update(investment=d("$5,000")), "is a fact", "a price is never drafted")
    bad(lambda g: g["offer"].update(guarantee=d("Double your money back")), "is a fact", "a guarantee is never drafted")
    bad(lambda g: g["offer"].update(urgency=d("Only 3 spots left")), "is a fact", "a deadline or scarcity line is never drafted")
    bad(lambda g: g["offer"].update(promise=d("Double your enrollment in 8 weeks or your money back.")), "reads as a guarantee or a promise of an outcome", "a drafted promise with guarantee language is refused")
    bad(lambda g: g["offer"].update(promise=d("A full schedule in 90 days.")), "No numbers and no timeframe", "a drafted promise may not add a number or a timeframe")
    bad(lambda g: g["positioning"].update(value_prop=d("Save $12,000 a year on overhead.")), "a figure nobody confirmed ($12,000)", "a drafted line may not carry a new figure")
    bad(lambda g: g["positioning"].update(villain=d("Agencies waste 40% of your budget.")), "a figure nobody confirmed (40%)", "nor a new percentage")
    bad(lambda g: g["avatar"].update(profile={"v": "x", "basis": "files"}), "needs the source", "a line from files must name its source")
    bad(lambda g: g["avatar"].update(profile="plain string"), "where it came from", "an untagged line is refused")
    bad(lambda g: g["avatar"].update(profile={"v": "x", "basis": "certain"}), "confirmed, files or drafted", "an unknown tag is refused")
    bad(lambda g: g["offer"].pop("promise"), "needed before the page is worth showing", "no promise, no page")
    bad(lambda g: g.update(positioning={"tagline": d("Fill it.")}), "positioning: needs at least one of", "positioning needs something real to stand on")
    bad(lambda g: g["offer"].update(bonus=c("x")), "not a field this page knows", "an unknown field is refused")
    bad(lambda g: g.pop("positioning"), "positioning: missing", "a missing part is refused")
    rbf = tmp / "BF_retired.md"
    rbf.write_text(tpl.replace("- **Retired lines** (never used again in any output, by any session — e.g. a credibility story, a claim, an old offer):",
                               "- **Retired lines** (never used again in any output, by any session — e.g. a credibility story, a claim, an old offer): \"Featured in Ceramics Monthly\""))
    bad(lambda g: g["positioning"].update(advantage=f("Featured in Ceramics Monthly. Eight years running a studio.", "Notes/bio old.md")), "carries a retired line", "a retired line is refused when the Business File is given", ("--business-file", rbf))
    g = copy.deepcopy(GOOD)
    g["positioning"]["value_prop"] = d("Two patient sources you own for $4,500.")
    write(g)
    check("reveal: a drafted line may repeat a figure the member has confirmed", run(RV, "check", fj)[0] == 0)
    g = copy.deepcopy(GOOD)
    g["offer"]["guarantee"] = c("None")
    write(g)
    check("reveal: a decision of 'none' is shown as itself", run(RV, "build", fj, page)[0] == 0 and "<p>None</p>" in page.read_text())
    write(GOOD)
    check("reveal: output must be an .html file", run(RV, "build", fj, tmp / "out.txt")[0] != 0)
    rsrc = RV.read_text()
    check("reveal: standard library only, no network", not any(x in rsrc for x in ("requests", "urllib", "socket", "http.client", "subprocess")))
    ref = (SK / "references/foundation-reveal.md").read_text()
    check("reveal: every field the page knows is documented", all(f"`{k}`" in ref for _p, _t, fs in rm.PARTS for k, _l, _k in fs))

    # ---- Your Build: the handover page ---------------------------------------------------------
    H = tmp / "member"
    (H / "autopilot/drafts").mkdir(parents=True)
    (H / "BUILDROOM_BUSINESS_FILE.md").write_text(tpl.replace("**Business:** [business name]", "**Business:** Harbor <Coaching>"))
    for n in ("01_ICA", "02_Offer", "03_Pos", "04_Page"):
        (H / "autopilot/drafts" / f"{n}.md").write_text("x")
    HA = H / "autopilot"
    hd = lambda slug, *a: run(AP, "done", "--dir", HA, slug, *a)  # noqa: E731
    run(AP, "plan", "--dir", HA, "--readiness", "74", "--no-web", "--skip", "leadgen")
    hd("ideal-client-avatar", "--status", "drafted", "--outputs", D + "01_ICA.md", "--gaps", "Two real client <quotes>", "A booking link")
    hd("signature-offer", "--status", "partial", "--outputs", D + "02_Offer.md", "--gaps", "A booking link", "--note", "Name, promise and price only")
    hd("positioning-messaging", "--status", "drafted", "--outputs", D + "03_Pos.md")
    hp = HA / "Your_Build.html"
    code, out = run(HV, "build", "--dir", HA, hp)
    h0 = hp.read_text()
    check("handover: builds before the review too, and says the foundation is not approved", code == 0 and "It has not been approved yet, so nothing after it has run." in h0 and "The run is not finished." in h0)
    run(AP, "approve", "--dir", HA, "--words", "go ahead")
    hd("offer-page-copy", "--status", "drafted", "--outputs", D + "04_Page.md", D + "Gone.md", "--gaps", "A photo of you", "--note", "Uses your guarantee wording exactly.")
    hd("funnel-map", "--status", "blocked", "--note", "No tools known")
    code, out = run(HV, "build", "--dir", HA, hp)
    hh = hp.read_text()
    check("handover: one self-contained page, named for the business from the Business File", code == 0 and hh.startswith("<!doctype html>") and "<title>Your Build · Harbor &lt;Coaching&gt;</title>" in hh
          and not re.search(r'(src|href)="https?:', hh) and "@import" not in hh and "url(" not in hh)
    check("handover: counts drafted pieces, open items and waiting sessions", "<b>4</b><span>pieces drafted for you, 1 of them only in part" in hh and "<b>4</b><span>things in them that still need you" in hh
          and f"<b>{sum(1 for t in am.TOOLS if t[3] == 'needs_you')}</b><span>sessions waiting" in hh)
    check("handover: leads with the answers that unlock more than one draft", "Answer these first" in hh and "A booking link" in hh.split("Answer these first")[1].split("</div>")[0]
          and "Two real client" not in hh.split("Answer these first")[1].split("</div>")[0])
    check("handover: a partly drafted piece says so, and what was and was not done", "· Partly drafted" in hh and "What was and was not drafted" in hh and "Name, promise and price only" in hh)
    check("handover: each drafted document that exists is a link, relative to the page", 'href="drafts/01_ICA.md"' in hh and 'href="drafts/04_Page.md"' in hh)
    check("handover: a missing file is named, not linked", "Gone.md <span" in hh and 'href="drafts/Gone.md"' not in hh and "not found where it was saved" in hh)
    check("handover: what still needs the member is a checklist, escaped", hh.count('type="checkbox"') == 4 and "Two real client &lt;quotes&gt;" in hh and "<quotes>" not in hh)
    check("handover: says what could not be drafted and gives the sentence to run it", "No tools known" in hh and "Could not be drafted" in hh and 'data-say="Help me map my funnel"' in hh)
    check("handover: lists what was left out and what was not reached", "Left out" in hh and "left out at the member&#x27;s request" in hh and "Not reached yet" in hh and "The run stopped before this step." in hh)
    check("handover: every session that needs the member, with its reason and a copy button, and says to pick what fits",
          all(f"Not run because {html_escape(t[4])}." in hh and f'data-say="{html_escape(t[2])}"' in hh for t in am.TOOLS if t[3] == "needs_you") and "Not all of them will fit your business" in hh)
    check("handover: shows the member's own approval words", "“go ahead”" in hh)
    check("handover: links to the foundation page only when it exists", "Open your foundation page" not in hh)
    (HA / "Foundation_Reveal.html").write_text("<html></html>")
    run(HV, "build", "--dir", HA, hp)
    check("handover: and does link it once it is there", 'href="Foundation_Reveal.html">Open your foundation page' in hp.read_text())
    check("handover: says nothing was published and promises no results", "Nothing was published, sent or paid for." in hh and "nothing on it promises results" in hh)
    check("handover: prints cleanly, works on a phone, no long dashes", "@media print" in hh and "@media (max-width:760px)" in hh and "—" not in hh and "–" not in hh)
    check("handover: every drafted tool has a plain line saying what it is for", all(t[0] in mod(HV, "handover").FOR for t in am.TOOLS if t[3] in ("foundation", "auto")))
    check("handover: output must be an .html file, and a missing run is refused", run(HV, "build", "--dir", HA, tmp / "x.txt")[0] != 0 and run(HV, "build", "--dir", tmp / "none", tmp / "x.html")[0] != 0)
    hsrc = HV.read_text()
    check("handover: standard library only, no network", not any(x in hsrc for x in ("requests", "urllib", "socket", "http.client", "subprocess")))

    # ---- the skill's instructions ------------------------------------------------------------------
    sk = (SK / "SKILL.md").read_text()
    me = (SK / "references/autopilot-method.md").read_text()
    head = sk.split("---")[1]
    check("skill: name, start phrases and a description that fits the listing", "name: buildroom-autopilot" in head and "run autopilot" in head and len(head) < 700)
    check("skill: needs a filled snapshot and a folder", "autopilot.py preflight BUILDROOM_BUSINESS_FILE.md" in sk and "Cowork, Claude Code or Codex" in sk)
    check("skill: a thin file is named for what it is, before the run", "mostly blanks and guesses" in sk and "Never supply those words yourself." in sk and "Say that before the run, not after." in me)
    check("skill: the never-draft list wins over a session's own prompts", "## The never-draft list wins" in me and "the list wins: leave that part out and mark the gap" in me
          and "The never-draft list wins." in sk)
    check("skill: what is never drafted is named", all(x in me for x in ("prices, dollar values, price tiers, anchors", "client names, quotes, testimonials, results", "composite stories",
          '"as if you had interviewed"', "credentials, awards", "guarantees and their terms", "scores and ratings presented as findings")))
    check("skill: imagined client words never become quotes", "never **Sourced language**" in me and "never inside quotation marks" in me)
    check("skill: the member's rules are carried into every session", "Give those to every session and every subagent, word for word." in me and "autopilot.py decide" in sk)
    check("skill: the questions asked are the ones that unblock the most", all(x in sk for x in ("A typical client result", "How someone books a call or buys", "The tools they use", "Ask this even when a file mentions one"))
          and "Eight at most" in sk)
    check("skill: the member is not asked to choose steps by name", "Do not ask the member to choose steps by name" in sk)
    check("skill: one stop, and only the member's own go-ahead passes it", "Never record a go-ahead they did not give." in sk and "Silence, or your own judgement that it is good, is not." in me
          and "means show them the page again" in me)
    check("skill: an approved draft is reviewed, never confirmed", "becomes reviewed, not confirmed" in sk and "it never becomes confirmed" in me and "Nothing becomes `confirmed` because it was glanced at." in ref)
    check("skill: never invents a fact to fill a blank", "A blank stays a marked blank." in sk and "A page with three invented facts is harmful." in me)
    check("skill: a session that is mostly blanks is recorded as partial or blocked, not drafted", "`--status partial`" in me and "a better result than a document of blanks listed as drafted" in me)
    check("skill: drafts are saved in one place, away from the member's files", "Save every document under `autopilot/drafts/`" in me and "Save a draft anywhere but `autopilot/drafts/`." in sk)
    check("skill: copy is written clean, with facts listed at the end", "without a tag on every sentence" in me and "**Facts used and where each came from**" in me and "prefer cutting such a sentence to tagging it" in me)
    check("skill: proof needs recorded permission before a stranger could read it", "only when permission is recorded as yes" in me and "is never named, anywhere" in me
          and "without permission recorded as yes" in sk)
    check("skill: stale, retired and unsettled findings are not sources", "Not findings marked `stale`, `retired` or `inferred`" in me and "Never a finding the ledger marks stale, retired, inferred or unsettled." in ref)
    check("skill: what a run writes into the Business File is narrow and tagged", "## What a run writes into the Business File" in me and "**Before the review:** nothing." in me
          and "only the name of its document" in me and "`[reviewed draft]`" in me and "Write unreviewed drafts into the Business File." in sk)
    check("skill: a run never marks a section complete", "A run never marks a section `complete`." in me and "Mark a section `complete`." in sk)
    check("skill: 'none' is never written into retired lines", '"None" is never written into Retired lines' in me)
    check("skill: one session log row for the run", "one row for the whole run" in me)
    check("skill: never publishes, sends, spends or connects an account", "Publish, send, post, spend, or connect an account." in sk and "Spend money or generate paid media." in me)
    check("skill: stays inside the file scope the member agreed", "Do not read outside that scope." in me)
    check("skill: no questions during the unattended phases", "Never ask a question during Phase 2 or Phase 4." in sk)
    check("skill: keeps what the member already built and never uses retired lines", "do not rewrite a section the member built" in me and "Retired lines in §1 are never used" in me)
    check("skill: resumes, never starts over", "do not start over" in sk and "Never start a second run over an unfinished one." in me)
    check("skill: the method's tool groups match the run keeper", all(t[1] in me for t in am.TOOLS if t[0] != "autopilot"), [t[1] for t in am.TOOLS if t[1] not in me])
    for grp, mode in (("**Run**", "auto"), ("**Needs you**", "needs_you")):
        row = next(l for l in me.splitlines() if l.startswith(f"| {grp}"))
        check(f"skill: the {mode} row of the method names exactly that group", all((t[1] in row) == (t[3] == mode) for t in am.TOOLS if t[3] in ("auto", "needs_you")))
    check("skill: the handover is the report and the Your Build page, given as they are", "handover.py build --dir autopilot autopilot/Your_Build.html" in sk and "Do not summarise them into something more flattering." in me)
    check("skill: the presentation says little and does not praise itself", "Do not summarise the page in the chat, do not tell them it is good, and do not ask a question." in ref)
    check("skill: no promise of results anywhere in its instructions", "No promise of leads, clients, revenue or results" in sk)
    check("skill: no long dashes in its instructions", all("—" not in t and "–" not in t for t in (sk, me, ref)))
    check("skill: carries the shared protocol and template unchanged", (SK / "references/business-file-template.md").read_text() == tpl
          and (SK / "references/business-file-protocol.md").read_text() == (ROOT / "shared/business-file-protocol.md").read_text())
    proto = (ROOT / "shared/business-file-protocol.md").read_text()
    check("protocol: the Autopilot exception is stated and narrow", "The one exception is an Autopilot run" in proto and "never a fact" in proto
          and "update the file in place instead" in proto and "of the member's own content" in proto)

    # ---- wired in -----------------------------------------------------------------------------
    rd = lambda p: (ROOT / p).read_text()  # noqa: E731
    check("wired: the guide lists Autopilot with its start phrase", '"autopilot","Autopilot","Run autopilot"' in guide)
    check("wired: public descriptions no longer promise LinkedIn or search drafts from a run",
          not any("LinkedIn and search work" in rd(p) for p in ("connector/guide.html", "connector/start.html", "rollout/MEMBER-README.md", "rollout/releases/README.md", "README.md",
                                                                "skills/buildroom-os/references/roadmap.md")))
    check("wired: the roadmap names it and its phrases", "buildroom-autopilot" in rd("skills/buildroom-os/references/roadmap.md") and '"Run autopilot"' in rd("skills/buildroom-os/references/roadmap.md"))
    check("wired: the protocol counts forty-two sessions", "42 standalone sessions" in proto)
    check("wired: there are forty-two skills", len(on_disk) == 42, len(on_disk))
    check("wired: the member README and the repo README list it", "buildroom-autopilot" in rd("rollout/MEMBER-README.md") and "buildroom-autopilot" in rd("README.md"))

    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
