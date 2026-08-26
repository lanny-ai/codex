# Build Room Library — Gap Analysis and Production Plan

**Scope:** the five artifacts supplied for review — `BuildRoom_Master_Roadmap_2026.docx`,
`BUILDROOM_APRIL_v2_Complete_Bundle.zip`, `AUTOMATION_W1_Funnel_Map_and_First_Automation.zip`,
`Lead_Capture_Complete_Install_Bundle.zip`, and `SourceWatcher_Complete_Install_Bundle.zip`.

**Type:** analysis only. No curriculum content, skills, or bundles were created or modified.

---

## 1. Executive summary

The roadmap commits to 36 weekly automations across nine monthly themes (April–December 2026).
Six of those 36 slots are filled by the artifacts supplied, plus one seventh artifact that does not
correspond to any roadmap slot. That is **17% roadmap coverage**, five months into a nine-month program.

Three findings matter more than the raw count:

1. **Production stopped following the roadmap after April.** April was delivered on schedule and in
   full. Every artifact produced since then belongs to either the October theme or a month that does
   not exist on the roadmap. Six roadmap months have no artifacts at all.
2. **Packaging is proven and nearly free.** Converting a raw weekly bundle into an installable
   `.skill` was, in the one case where both formats survive, a byte-for-byte file rename plus one
   hand-written `SKILL.md`. The backlog of unpackaged weeks is a formatting task, not an authoring task.
3. **Delivered ZIPs contain two of the four files the roadmap advertises.** The gap is presentational
   rather than substantive — the missing pieces are embedded inside the delivered files rather than absent
   — but the member-facing promise and the member-facing artifact do not currently match.

---

## 2. Inventory of what exists

| # | Automation | Theme / Week | Format | Authored |
|---|---|---|---|---|
| 1 | Ideal Client Avatar Machine | Offer Clarity · W1 | Raw 2-file | 2026-03-29 |
| 2 | Signature Offer Builder | Offer Clarity · W2 | Raw 2-file | 2026-03-29 |
| 3 | Positioning & Messaging System | Offer Clarity · W3 | Raw 2-file | 2026-03-29 |
| 4 | Offer Page Copy Generator | Offer Clarity · W4 | Raw 2-file | 2026-03-29 |
| 5 | Funnel Map & First Automation | Automation & Funnels · W1 | Raw 2-file | 2026-04-08 |
| 6 | Lead Capture System | Automation & Funnels · W3 | **Full install bundle** | 2026-05-13 |
| 7 | Source Watcher Generator | Obsidian Knowledge Base · W3 | `.skill` only | 2026-06-17 |

Two further artifacts are referenced by delivered material but were not supplied for review:

- **Decision Machine** (Automation & Funnels W2). The Lead Capture presentation deck
  (`LEAD_CAPTURE_Gamma_v2.txt`) tells members "Week 2 — Decision Machine: you built the automated
  follow-up that converts leads over time," so it is presented to members as already delivered.
- **Obsidian Knowledge Base W1, W2, W4.** The Source Watcher README describes a four-week month
  (W1 vault setup, W2 YouTube watcher, W3 this skill, W4 optimization) of which only W3 was supplied.

Whether these exist and were simply not included in this upload, or were never produced, cannot be
determined from the artifacts alone. It is the first thing to confirm.

---

## 3. Coverage against the roadmap

| Month | Theme | Slots filled |
|---|---|---|
| April | Offer Clarity & Positioning | **4 / 4** |
| May | Lead Generation Engine | 0 / 4 |
| June | Sales Conversations | 0 / 4 |
| July | Content That Converts | 0 / 4 |
| August | Client Delivery Systems | 0 / 4 |
| September | Operations & SOPs | 0 / 4 |
| October | Automation & Funnels | **2 / 4** (W1, W3) |
| November | Retention & Revenue Growth | 0 / 4 |
| December | Year-End Reset & 2027 Launch | 0 / 4 |
| — | *Obsidian Knowledge Base (off-roadmap)* | *1 artifact* |

**Total: 6 / 36 roadmap slots (17%).**

### 3.1 The sequencing divergence

Authoring dates tell a clear story:

- **2026-03-29** — all four April weeks, delivered as a complete month, immediately before April.
- **2026-04-08** — Automation & Funnels W1. Per the roadmap this is an **October** automation, produced
  in the slot where **May W1 (Lead Magnet Creator)** was promised.
- **2026-05-13** — Automation & Funnels W3, produced where **June W2** was promised.
- **2026-06-17** — Obsidian Knowledge Base W3, a month absent from the roadmap entirely.

After April, month-by-month sequencing was abandoned. Production continued at a steady pace, but
against a different plan than the one published. This is the single most consequential finding, because
the roadmap's core promise to members is sequential: *"Every ZIP builds on the last."* The April
material honours this — W2's prompt system opens by requiring the W1 ICA document, W3 requires W1 and W2,
W4 requires all three. Members who received April and then received Automation & Funnels W1 experienced a
jump from "Offer Page Copy" to "Funnel Mapping," skipping the entire Lead Generation Engine month that the
sequence was designed to depend on.

Two coherent resolutions, and picking one is the highest-leverage decision available:

- **Re-sequence the roadmap** to match what is actually being produced and published, reissuing it to
  members. Honest, immediate, and cheap.
- **Return to roadmap order** and treat the Automation & Funnels and Obsidian artifacts as
  already-banked inventory for their proper months.

The first is recommended. The delivered artifacts are internally coherent as their own sequence
(Funnel Map → Decision Machine → Lead Capture is a sound progression), and reissuing a roadmap costs
far less than authoring six months of material out of order.

---

## 4. Format inconsistencies

### 4.1 Three delivery formats are in circulation simultaneously

| Format | Contents | Used by |
|---|---|---|
| **Raw 2-file ZIP** | `STEP1_Knowledge_Base.txt`, `STEP2_Prompt_System.txt` | April W1–W4, Automation W1 |
| **Full install bundle** | `.skill` + original ZIP + `Quick_Start.html` + `README.md` + Gamma deck | Lead Capture only |
| **`.skill` only** | `.skill` + `Quick_Start.html` + `README.md` | Source Watcher |

Only Lead Capture ships both the `.skill` and the raw ZIP, and its README explicitly frames this as a
deliberate choice: *"Use the .skill OR the ZIP — both produce the same result. The .skill is more
elegant; the ZIP is more transparent."* That is the right standard. Neither of the other formats meets it.
Five of seven automations cannot be installed as a skill, and one cannot be used in the drag-and-drop
workflow the roadmap describes as the product's central mechanic.

### 4.2 Delivered ZIPs do not match the advertised ZIP

The roadmap promises four files inside every weekly ZIP:

> 📋 SYSTEM PROMPT · 🔄 WORKFLOW FILE · 📝 INPUT TEMPLATE · 📖 ONE-PAGE GUIDE

Every delivered ZIP contains **two** files. Mapping the promise onto what ships:

| Promised | Actual location |
|---|---|
| System prompt | Inside `STEP2`, under the heading `SYSTEM PROMPT` |
| Workflow file | Inside `STEP2`, as `PROMPT 1`–`PROMPT 5` |
| Input template | Inside `STEP2`, under the heading `INPUT TEMPLATE` |
| One-page guide | **Not present in any bundle** |

Three of the four exist and are simply consolidated into one file rather than split into three. The
one-page guide — the piece that states what this builds, why it matters, and the business ROI — has no
equivalent in any delivered bundle. The knowledge base file, which is genuinely valuable and is the
larger of the two files, is not mentioned in the promise at all.

Either split the files to match the promise, or restate the promise to match the files. The second is
cheaper and loses nothing, provided a one-page guide is added — it is the only item on the list that a
member cannot currently get.

### 4.3 Supporting assets are inconsistent

| Asset | April W1–W4 | Automation W1 | Lead Capture | Source Watcher |
|---|---|---|---|---|
| `README.md` | — | — | ✅ | ✅ |
| `Quick_Start.html` | — | — | ✅ | ✅ |
| Gamma presentation deck | — | — | ✅ | — |
| `.skill` package | — | — | ✅ | ✅ |

No automation has the complete set. Lead Capture is closest and is the natural template for a standard.

### 4.4 Off-roadmap month naming

The Source Watcher belongs to an "Obsidian Knowledge Base Month" that does not appear on the 2026
roadmap. Its README describes a full four-week arc for that month. Either the roadmap is out of date or
this month is an unplanned insertion; in either case the published roadmap and the material members are
receiving disagree about what program they are in.

---

## 5. Roadmap prompt names do not match delivered prompt names

The roadmap advertises five named prompts per week. The delivered `STEP2` files also contain exactly
five prompts — the count is right everywhere — but the names differ substantially. April W1:

| Roadmap promises | Bundle delivers |
|---|---|
| ICA Deep-Dive Prompt | PROMPT 1 — JTBD-First ICA Profile |
| Pain Stack Generator | PROMPT 2 — Full Switching Force Map |
| Dream State Builder | PROMPT 3 — Awareness Stage Analysis & Buying Journey Map |
| Buying Trigger Identifier | PROMPT 4 — Verbatim Language Bank |
| Objection Pre-Handler | PROMPT 5 — Objection Bank + Negative Avatar |

**This is a labelling mismatch, not a content gap.** The advertised concepts are present in the delivered
material — "pain stack," "dream state," and "buying trigger" all appear inside the W1 files as concepts
the prompts work with. They are simply not the titles of discrete prompts. April W2 shows the same
pattern: "Deliverables Packager" and "Price Anchoring Script" appear nowhere by name, but
`PROMPT 2 — Obstacle Map + Deliverables Build` and `PROMPT 3 — Value Stack + Pricing Architecture`
clearly cover that ground.

The practical risk is member-facing: someone who bought against the roadmap opens the ZIP and finds five
prompts, none of which carry the names they were sold. The fix is to align the roadmap's prompt names to
the delivered titles — the delivered titles are more precise and more descriptive of what the prompts
actually produce.

---

## 6. What is strong

The gaps above are real, but they sit on top of unusually solid content.

- **The `STEP1`/`STEP2` template is rigid and consistent.** Every knowledge base opens with
  `SECTION 1: THE CORE TRUTH ABOUT [topic]`, proceeds through `SECTION 2: THE FOUR MASTER FRAMEWORKS`,
  and closes with `THE OPERATING PRINCIPLES CLAUDE WILL APPLY`. Every prompt system runs
  `SYSTEM PROMPT → INPUT TEMPLATE → PROMPT 1–5`. Five of five bundles conform without deviation. This
  consistency is what makes the automation described in §7 straightforward.
- **The frameworks are properly sourced.** Christensen and Ulwick on JTBD, Zaltman on subconscious
  decision-making, Hormozi on value equations, Dunford on positioning, Schwartz on awareness stages,
  Ogilvy and Caples and Sugarman and Halbert on copy. The knowledge bases cite named practitioners and
  specific works rather than generic marketing advice.
- **Cumulative dependency is enforced in the material.** Each April prompt system opens with a checklist
  requiring the prior weeks' outputs. W4 states plainly: *"Everything you built in April feeds into this
  session."* The compounding promise is real where the sequence was respected.
- **The Source Watcher's safety architecture is genuinely rigorous.** Four documented pillars of vault
  protection, enforced at the code level by a path check that refuses writes outside `/External` and raises
  a `SecurityError`. Defence in depth rather than an instruction to the model.

---

## 7. Recommended production plan

### 7.1 The packaging recipe is already proven

The Lead Capture bundle ships both its raw source files and its packaged `.skill`, which makes the
conversion method directly recoverable. Comparing them:

```
LEAD_CAPTURE_STEP1_Knowledge_Base.txt  →  references/knowledge-base.md   md5 0cb0c7eb…  IDENTICAL
LEAD_CAPTURE_STEP2_Prompt_System.txt   →  references/prompt-system.md    md5 9453b946…  IDENTICAL
```

Both files are **byte-for-byte identical** to their raw sources. Packaging was a rename into
`references/`, plus a hand-authored `SKILL.md` with YAML frontmatter, plus in this case one genuinely new
reference file (`kern-framework.md`) carrying voice guidance specific to that week.

So converting a raw bundle to an installable skill requires authoring exactly one file:

```
buildroom-<slug>/
├── SKILL.md                        ← the only new writing: frontmatter + phase flow
└── references/
    ├── knowledge-base.md           ← STEP1 .txt, renamed, unchanged
    └── prompt-system.md            ← STEP2 .txt, renamed, unchanged
```

Zip that directory, rename to `.skill`, done. The `SKILL.md` needs a `name`, a trigger-rich `description`
(both existing skills use a long multi-sentence description dense with trigger phrases — worth preserving,
since that is what makes the skill fire without the member invoking it by name), a "Your Foundation"
section instructing the model to read both references first, and a phase-by-phase flow mirroring the five
prompts.

### 7.2 Sequenced recommendations

**First — resolve the two open questions.** Confirm whether Decision Machine (Automation W2) and Obsidian
W1/W2/W4 exist. Four of the six named gaps in this report may already be closed. Nothing else should be
planned until the true inventory is known.

**Second — reconcile the roadmap with reality.** Re-sequence the published roadmap to the order actually
being produced, add the Obsidian month, and align the 36 advertised prompt names to the delivered prompt
titles. This is a document revision, and it removes every mismatch in §3, §4.4, and §5 at once.

**Third — standardise the bundle.** Adopt the Lead Capture structure as the definition of a complete
weekly deliverable: raw ZIP + `.skill` + `README.md` + `Quick_Start.html` + one-page guide, with the
Gamma deck where a live session is planned. Write the one-page guide template once; it is the only
member-facing promise currently unmet by any bundle.

**Fourth — back-package the five raw weeks.** April W1–W4 and Automation W1 become installable skills at
the cost of five `SKILL.md` files. Nothing else needs authoring.

**Fifth — build the generator.** The `STEP1`/`STEP2` template is regular enough to be parsed
mechanically: section headings are fixed strings, prompts are numbered `PROMPT N — TITLE`, and the input
template is a single delimited block. A script that takes a `STEP1`/`STEP2` pair and emits a complete
bundle — `SKILL.md` scaffolded from the parsed prompt titles, references copied verbatim, README and
Quick Start rendered from templates — converts the remaining roadmap weeks from a packaging problem into
a review problem. With roughly 29 weeks still to produce, this pays for itself almost immediately.

---

## 8. Note on repository placement

This report is committed to `lanny-ai/codex`, which currently contains a single unrelated product:
the **OS Cortex AEO Publisher** Codex plugin, distributed through `.agents/plugins/marketplace.json`
and installed via `codex plugin marketplace add`. That product targets the ChatGPT desktop/Codex app.

The Build Room library targets Claude Cowork and is distributed as uploaded `.skill` files and
drag-and-drop ZIPs. The two product lines share an owner (AI Momentum Labs) and a skill-authoring
convention — both use `SKILL.md` with `name` and `description` frontmatter over a `references/` directory
— but they use different plugin manifests, different install paths, and different runtimes.

If the Build Room library is eventually version-controlled here, it warrants its own top-level directory
and its own marketplace entry rather than being folded into the AEO plugin. Nothing in this report
assumes that decision has been made.

---

*Analysis of five supplied artifacts. No curriculum content was created or modified.*
