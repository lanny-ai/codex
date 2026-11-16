#!/usr/bin/env python3
"""Positioning fields: market sophistication and the belief to move (Business File §4, version 1.11).

Usage:  python3 buildroom/tests/positioning/run_tests.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))


def main():
    rd = lambda p: (ROOT / p).read_text(encoding="utf-8")  # noqa: E731
    tpl = rd("templates/BUILDROOM_BUSINESS_FILE.md")
    s4 = tpl[tpl.index("## 4. Positioning"):tpl.index("## 5. Offer Page")]
    check("template: §4 has market sophistication and the belief to move", "**Market sophistication**" in s4 and "**Belief to move**" in s4)
    check("template: they sit before the Messaging Bible link", s4.index("**Belief to move**") < s4.index("Full Messaging Bible"))
    check("template: §2 still holds the awareness stage, once", tpl.count("Awareness stage (Schwartz)") == 1)
    for skill in sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "references/business-file-template.md").exists()):
        if rd(f"skills/{skill}/references/business-file-template.md") != tpl:
            check(f"{skill}: template copy matches", False)
    check("every skill's template copy carries the new fields", all(
        "**Market sophistication**" in rd(f"skills/{p.name}/references/business-file-template.md")
        for p in (ROOT / "skills").iterdir() if (p / "references/business-file-template.md").exists()))
    pos = rd("skills/buildroom-positioning-messaging/SKILL.md")
    ref = rd("skills/buildroom-positioning-messaging/references/market-sophistication.md")
    check("positioning: the reference is in the foundation list and has a phase", "references/market-sophistication.md" in pos and "Phase 5b" in pos)
    check("positioning: §4 update writes both fields", "market sophistication (stage and evidence), the belief to move" in pos)
    check("reference: five stages and five starting points", all(f"| {n} |" in ref for n in "12345") and all(
        x in ref for x in ("Unaware", "Problem-aware", "Solution-aware", "Product-aware", "Most aware")))
    check("reference: a judgement from evidence, not a measurement", "not measurements" in ref and "evidence" in ref)
    check("reference: no competitor page is described from memory", "from memory" in ref)
    check("reference: a stage never justifies a bigger claim", "more specific, not more inflated" in ref)
    check("reference: no percentages or invented figures", "%" not in ref)
    copy = rd("skills/buildroom-copy-engine/SKILL.md")
    check("copy engine: the fact sheet reads both fields and falls back to §2", "§4 market sophistication" in copy and "§4 belief to move" in copy
          and "§2's awareness stage" in copy)
    ads = rd("skills/buildroom-ad-studio/SKILL.md") + rd("skills/buildroom-ad-studio/references/concept-matrix.md")
    check("ad studio: sophistication sets the hook", "market sophistication" in ads and "The stage never changes a claim" in ads)
    check("spec: the two fields are recorded under version 1.11", "*Market sophistication* and *Belief to move*" in rd("BUSINESS-FILE-SPEC.md"))
    check("viewer: the sample file carries the fields", "**Market sophistication**" in rd("rollout/Business_File_Viewer.html"))
    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    return 0 if all(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
