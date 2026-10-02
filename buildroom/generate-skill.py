#!/usr/bin/env python3
"""Generate a Build Room skill scaffold from a STEP1/STEP2 curriculum pair.

Parses the fixed weekly-bundle format (SECTION headings in the knowledge base;
SYSTEM PROMPT / INPUT TEMPLATE / PROMPT N — TITLE blocks in the prompt system),
copies both files byte-for-byte into references/, and writes a SKILL.md draft
wired into the Business File protocol. Every spot needing human judgment is
marked TODO-REVIEW; build-skills.sh refuses to package a skill until all
markers are resolved.

Usage:
  python3 generate-skill.py --step1 W1_KB.txt --step2 W1_PS.txt \
      --name buildroom-discovery-call --writes 9 \
      --writes-label "Sales Conversations" --requires 2,3

Stdlib only. Run from anywhere; output lands in <buildroom>/skills/<name>/.
"""
import argparse, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def tc(text):
    """Title-case without mangling apostrophes ("Dunford's", "I've")."""
    return re.sub(r"(\w)'(\w)", lambda m: m.group(1) + "'" + m.group(2).lower(), text.title())
RULE = re.compile(r'^[━─═]{10,}\s*$')
REGISTRY = {1: "Business Snapshot", 2: "Ideal Client Avatar", 3: "Signature Offer",
            4: "Positioning & Messaging", 5: "Offer Page", 6: "Funnel & Automation",
            7: "Lead Capture", 8: "Session Log"}

def blocks(text):
    """Split on heavy-rule lines; yield (heading, body) per block."""
    out, cur = [], []
    for line in text.splitlines():
        if RULE.match(line):
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(line)
    if cur:
        out.append(cur)
    result = []
    for b in out:
        stripped = [l for l in b if l.strip()]
        if stripped:
            result.append((stripped[0].strip(), "\n".join(b)))
    return result

def parse_step2(text):
    title, prompts, inputs = None, [], []
    for heading, body in blocks(text):
        m = re.match(r'^(.*?)\s*—\s*PROMPT SYSTEM', heading)
        if m and not title:
            title = tc(m.group(1).strip())
        m = re.match(r'^PROMPT\s+(\d+)\s*[—-]\s*(.+)$', heading)
        if m:
            prompts.append((int(m.group(1)), tc(m.group(2).strip())))
    # Input fields live between the INPUT TEMPLATE heading and PROMPT 1 (across rule lines).
    m = re.search(r'^INPUT TEMPLATE\s*$(.*?)^PROMPT\s+1\b', text, re.M | re.S)
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            core = re.sub(r'\s*\([^)]*\)', '', line)  # drop parentheticals like "(current)"
            if core.endswith(":") and len(core) > 3 and not re.search(r'[a-z]', core):
                inputs.append(tc(core[:-1]))
    return title, sorted(prompts), inputs

def parse_step1(text):
    topic, sections = None, []
    m = re.search(r'^KNOWLEDGE BASE:\s*(.+)$', text, re.M)
    if m:
        topic = tc(m.group(1).strip())
    for m in re.finditer(r'^SECTION\s+\d+\s*[:—]\s*(.+)$', text, re.M):
        sections.append(tc(m.group(1).strip()))
    return topic, sections

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step1", required=True, type=Path)
    ap.add_argument("--step2", required=True, type=Path)
    ap.add_argument("--name", required=True, help="skill name, e.g. buildroom-discovery-call")
    ap.add_argument("--title", help="session title (default: parsed from STEP2 header)")
    ap.add_argument("--writes", type=int, required=True, help="Business File section number this skill writes")
    ap.add_argument("--writes-label", help="section name (required for sections not yet in the registry)")
    ap.add_argument("--requires", default="", help="comma-separated prerequisite section numbers, e.g. 2,3")
    ap.add_argument("--out", type=Path, default=ROOT / "skills")
    a = ap.parse_args()

    s1, s2 = a.step1.read_text(encoding="utf-8"), a.step2.read_text(encoding="utf-8")
    topic, kb_sections = parse_step1(s1)
    title, prompts, inputs = parse_step2(s2)
    title = a.title or title or (topic or a.name)
    if not prompts:
        sys.exit("ERROR: no 'PROMPT N — TITLE' blocks found in STEP2 — is this a standard bundle?")
    wl = a.writes_label or REGISTRY.get(a.writes)
    if not wl:
        sys.exit(f"ERROR: §{a.writes} is not in the registry — pass --writes-label and add it to "
                 "templates/BUILDROOM_BUSINESS_FILE.md and BUSINESS-FILE-SPEC.md.")
    reqs = [int(x) for x in a.requires.split(",") if x.strip()]
    req_txt = (" and ".join(f"§{r} ({REGISTRY.get(r, 'see registry')})" for r in reqs)
               if reqs else None)

    d = a.out / a.name
    (d / "references").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(a.step1, d / "references/knowledge-base.md")
    shutil.copyfile(a.step2, d / "references/prompt-system.md")

    n = len(prompts)
    phase_lines = "\n".join(
        f"{i}. **{t}** — <!-- TODO-REVIEW: one-line purpose of this prompt -->"
        for i, t in prompts)
    kb_topics = ", ".join(kb_sections[:6]) if kb_sections else "the week's frameworks"
    intake = "; ".join(inputs) if inputs else "the input template fields"
    prereq_block = (f"""**Requires {req_txt}.** <!-- TODO-REVIEW: say in one sentence WHY these are needed. -->

If a prerequisite is missing, follow the protocol's two-path fallback: recommend running the missing session first, or run the provisional interview and mark §{a.writes} `provisional`."""
        if reqs else
        "None. <!-- TODO-REVIEW: confirm this session truly has no prerequisites. -->")

    skill_md = f"""---
name: {a.name}
description: |
  {title}: guided Build Room session covering {kb_topics}. TODO-REVIEW: rewrite this description in the house style — what it builds, who it's for, and 6-10 member trigger phrases ("help me...", "I need..."). Reads the member's Build Room Business File and writes the {wl} section when the session ends.
---

# Build Room — {title}

<!-- TODO-REVIEW: 2-3 sentence identity paragraph: who you are, what the member walks away with. Mirror the SYSTEM PROMPT in references/prompt-system.md. -->

## Your Foundation

Read these reference files, in order, before any member-facing work:

1. **`references/knowledge-base.md`** — the research foundation for this session.
2. **`references/prompt-system.md`** — the session's engine. Adopt its SYSTEM PROMPT as your operating identity and its quality standards as non-negotiable. (Ignore its manual load/paste instructions — this skill replaces that mechanic.)
3. **`references/business-file-protocol.md`** — how you read and write the member's Build Room Business File. Follow it exactly.

## Prerequisites

{prereq_block}

## Session Flow

### Phase 0 — Business File intake

Follow the protocol: ask for the member's Business File first. Pre-fill the input template from it{f" (prerequisite sections {', '.join('§'+str(r) for r in reqs)}{'' if 1 in reqs else ' plus §1'})" if reqs else " (§1 and any relevant sections)"}; ask only what remains, one question at a time. Input template fields: {intake}. <!-- TODO-REVIEW: map each field to its file section; note which are genuinely new questions. -->

### Phases 1–{n} — the build

Run the {n} prompts from `references/prompt-system.md` in order, one at a time, confirming each output before the next:

{phase_lines}

<!-- TODO-REVIEW: add this session's quality bar (pull from the SYSTEM PROMPT's standards). -->

### Phase {n + 1} — Deliverable + Business File update

1. Assemble the complete session deliverable and tell the member to save it as its own document. <!-- TODO-REVIEW: name the deliverable. -->
2. Update the Business File per the protocol:
   - **§{a.writes} {wl}** — distilled decisions and key facts, link to the full document, status set (`complete`, or `provisional` per the inheritance rule).
   - **§8 Session Log** — append the row; ask for the 1–5 rating.
3. Emit the entire updated file in one code block with the "what changed" summary.
4. Close by naming the next session in the sequence. <!-- TODO-REVIEW: which session follows this one? -->

## Voice & Style Rules

- One question at a time. Recommendations before open questions.
<!-- TODO-REVIEW: add session-specific voice rules from the SYSTEM PROMPT. -->

## What This Skill Does NOT Do

<!-- TODO-REVIEW: 2-3 boundary bullets (what neighboring sessions own; what must never be fabricated). -->

## When the Session Is Complete

The member has: the session deliverable saved separately, and an updated Business File with §{a.writes} set and a Session Log entry.
"""
    (d / "SKILL.md").write_text(skill_md, encoding="utf-8")

    todo = skill_md.count("TODO-REVIEW")
    print(f"Generated {d}")
    print(f"  parsed: {n} prompts, {len(kb_sections)} KB sections, {len(inputs)} input groups")
    print(f"  {todo} TODO-REVIEW markers to resolve (build-skills.sh will refuse to package until they're gone)")
    print("\nNext steps:")
    print("  1. Resolve every TODO-REVIEW in SKILL.md (description trigger phrases matter most).")
    if a.writes not in REGISTRY:
        print(f"  2. Register §{a.writes} '{wl}': add it to templates/BUILDROOM_BUSINESS_FILE.md,")
        print("     the BUSINESS-FILE-SPEC.md registry, and buildroom-os/references/roadmap.md.")
    else:
        print(f"  2. Confirm §{a.writes} guidance in buildroom-os/references/roadmap.md covers this session.")
    print("  3. bash build-skills.sh && test-drive the .skill in Cowork before shipping.")

if __name__ == "__main__":
    main()
