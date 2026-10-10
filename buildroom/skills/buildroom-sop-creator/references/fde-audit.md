# The FDE Audit — Map It Before You Automate It

Reconstructed from the Build Room session of 2026-08-19 (host Lanny Morton, AI Momentum Labs), which taught the Forward Deployed Engineer playbook: "how the best engineers in the world get AI to actually work inside of real businesses." Quotations are Lanny's words with timestamps. *(inference)* marks a reading, not a statement.

This file extends the SOP Creator. The SOP Creator captures a process so a person can run it. The FDE audit captures it so an agent could, and decides honestly whether it should.

## Why this exists

"The gap was never AI, the gap is deployment. Getting your AI to do your work, your way, reliably enough to trust." [00:17:39]

"The secret is not better code, it's a better sequence." [00:18:53]

"There's one way to do a process right, and a thousand ways to do it wrong. Every business process is full of invisible rules, thresholds, exceptions, who signs off, what happens when the data doesn't match. The rules live in people's heads, not on a document. You cannot automate what you have not mapped, so the FDE never starts by building, they start by watching." [00:19:57–00:20:18]

Two audiences: the owner who wants the business to run without them, and the member who wants to do this for other businesses and charge for it. "It's relevant whether you have a business or you don't have a business." [00:12:03]

## The three phases

"The playbook has 3 phases. It has an audit phase. Map the process as it truly is. Phase 2 is an evaluation. You prove the automation on real historical examples. And phase three is deployment. Earn the trust in stages, never all at once." [00:22:47]

"The whole audit, to me, is the entire process, and that's the most important part." [00:30:25]

## Phase 1 — The audit (seven steps)

"The audit answers two questions. How does this process actually work? And should we automate it at all?" [00:27:22] Its two deliverables: "an operating map. It's the process written down with evidence" and "a go or no-go decision." [00:27:38] "Get the audit wrong, and the evals test the wrong thing, and deployment automates the wrong thing entirely." [00:30:10]

### A1. Watch the real work, never the SOP

"Documentation lies. The standard operating procedure describes the process as management believes it works. The audit captures it as the operator actually does it." [00:30:39–00:31:19]

"The FDE sits with an operator and watches real examples end-to-end. Real workflows, invoices, real tickets, real emails, every screen, every click, every pause." [00:31:27] Remote is fine: a screen recording with narration is valid intake. "You would just record yourself one time doing every single step all the way through the process." [01:29:15]

Listen for hedge words: "Usually, unless, it depends, except when." Each one "is a hidden rule that doesn't exist in the documentation. These hidden rules are where the automation dies." [00:31:43–00:32:02] In one member's experience, "about 35% of the time, management's process, as they understood it, was completely wrong." [00:55:12]

### A2. Write the operating map as-is, before to-be

"It should be exactly as the process is, not how you imagine it, not how it should be." [00:35:27] "Cheap corrections happen on the map, expensive corrections happen in production." [00:35:58] "Automating as-imagined process is the classic failure." [00:36:14]

**A mapped step names six things precisely** [00:36:31–00:37:55]:

| Field | Definition |
|---|---|
| Input | "What arrives, and in what forms." |
| Action | "What the operator actually does." |
| Output | "What exists after that didn't before." |
| Decision rule | "The exact threshold or condition that governs it." |
| Exception | "What happens when the rule doesn't apply." |
| Owner | "Who has the authority when it goes sideways." |

Each step carries evidence: which screen, which moment, what the operator said, "so the expert can point at any line and say, that's wrong, before a single line of automation exists." [00:36:28]

### A3. Pin the decision rules

"Match an invoice to a PO, the difference is over $25, flag it for review, over $500, Sarah signs off. No PO at all, email the vendor, don't guess." [00:38:27] "Vague rules cannot be automated. This step turns language into logic. First, flag the big ones." [00:38:35]

"A rule is not real until the person who lives it says, yes, that's the rule. So confirm it with the expert who's actually running the process. And the expert isn't the manager, the expert is the person who's actually operating the process." [00:39:08] Read back one rule at a time; propose what you believe the rule is and ask them to confirm.

### A4. Hunt the exceptions

Per step: "What arrives malformed? What's missing? What shows up twice?" [00:41:56] "Where does the work enter? Email, portal, spreadsheet, someone's memory, in how many formats. The messiest intake is usually the real bottleneck." [00:42:09]

Every failure mode gets one of three dispositions: **handle it, flag it, or route it to a human.** [00:42:23] "That never happens is not an answer, it's a prediction that it will happen in two weeks." [00:42:41] "In the audit, these exceptions are where the gold's at." [00:43:05]

### A5. Triage every step by judgment (the gates)

"Not all steps are equal. Before anything is built, every step gets classified. And this is where gates get placed." [00:43:41]

- **Green — deterministic.** "Same input, same output every time, safe to automate directly."
- **Yellow — model judgment.** "Requires interpretation or reading context. Automate with checks."
- **Red — human approval.** "Consequential, irreversible, or customer-facing. A person stays in the loop by design."

Gates move over time. Lanny's own email drafts sat behind a red gate for four or five months: "I found myself in the draft folder just hitting send every time. And then I went from red to green. I still watch it, though." [00:45:15–00:46:18]

### A6. The four safety questions, per step

"Answered before a single line of automation is written." [00:46:30]

1. "Do we have the right data? Does the automation have what it needs to decide correctly?"
2. "Are the required steps guaranteed? Are all prerequisite steps certain to have run?"
3. "Would a domain expert agree with the output?"
4. "Reversible if wrong? Sending money, emailing customers, deleting records: these never run without approval until deep into deployment."

The blast-radius story: "an email went out to 170,000 people. Totally wrong, and I did that." Sent autonomously, "without any shadow mode, without any approval gate." [00:47:09–00:47:50]

### A7. The go or no-go call

"The audit ends with a scored decision, not enthusiasm. Three scores: the value automation would create, the drag the current process causes, and the risk of automating it." [00:47:57]

- **Go** — high value, low risk. Proceed.
- **No-go** — high risk or thin value. Say so plainly.
- **Partial** — automate 80%, keep humans in 20%.

"Saying no, or only this part, is what makes an expert trustworthy. Anyone can promise automation. The professional tells you what not to automate." [00:48:50] A no-go still improves the SOP: "she can at least put it into her SOPs, and make her SOPs better, even if it doesn't become an automation." [00:32:48]

The first filter, before any of this: "Is there anything that's recurring in this process that happens continually?" [00:33:50] "Anything I touched, if I was gonna touch it more than once, I created a system for it." [01:26:08]

## Phase 2 — Evals

"Before anything goes live, build a golden dataset: 20 real historical examples of the process with known correct outcomes, pulled straight from the audit's evidence. Run the automation against all of them, report results in plain numbers. 50 runs, 41 pass, here's exactly what caused the 9 failures, grouped by cause." [00:57:09–00:57:26] Failures become "a fixable engineering list."

"No launch until automation passes on the client's own historic examples, a hard bar, like 90%." [00:58:08] "You're no longer asking anyone to believe you, you're showing them, with their own cases, their own data." [00:58:20]

## Phase 3 — Staged deployment

"Trust is earned in stages. Never flip a switch, climb a ladder." [00:59:01]

1. **Shadow mode** — "runs silently alongside a human. Outputs are compared, nothing is sent."
2. **Approve each** — "The automation drafts, the human approves every action before it executes."
3. **Autonomous** — "Only steps that have proven themselves to run on their own."

"Every action leaves an audit trail. If you can't show your receipts, you have not earned autonomy." [00:59:28] "Every human correction is treasure. When a reviewer edits a draft or rejects an action, that example goes straight into the golden dataset, and the bar the automation must clear rises." [00:59:53]

## The loop

"Audit and map, stage deployment, evaluate on data, repeat. It just becomes a perpetual thing. If you automate one bottleneck, oftentimes it reveals the next one. That's why an FDE is a relationship, not a project." [01:00:59–01:01:53]

Humans stay in: "The automation of things, or creating the workflow, includes humans. We're not excluding humans completely, and a lot of times they're necessary, and they never leave the process." [01:27:39]

## Doing this for other businesses

"Offering a free audit of a process is a pretty low bar to be able to build trust." [01:39:58] "You don't sell, I think they buy, when you present the solution." [01:27:12] Charge monthly and retain control: "if they stop paying you per month, you can pull it all away. Absolutely. I wouldn't do it any other way." [01:26:49] Don't pitch "I'm automating everything"; people "have been through that one before." [00:53:56]

## How this maps onto the SOP Creator's phases

*(inference, from what was taught)*

| SOP Creator phase | What the FDE audit adds |
|---|---|
| 1 · Inventory + triage | The recurrence question first. Then the three scores (value, drag, risk) → Go / No-go / Partial on each queued process, alongside the Frequency × Pain × Owner-Lock score. |
| 2 · Capture + SIPOC | Capture from the operator, not the manager; from a real run or a screen recording, never from the existing document. Log every hedge word as a hidden rule. Expand each process step to the six fields. Read back one rule at a time. |
| 3 · SOP build | As-is first. Pinned thresholds in the steps. The exception table gets a disposition column: handle / flag / route to a human. |
| 4 · Checklist + gate | Each step gets a gate colour and the four safety-question answers. Red steps name their approver (the Owner field). |
| 5 · Delegation pack | The pack can be delegated to a person or to an agent. For Go or Partial: the golden dataset (20 historical cases), the eval bar, the staged rollout per step, the logging requirement, and the feedback rule. For No-go: the improved SOP is the deliverable, and that is a win. |

## Quote bank

- "The gap was never AI, the gap is deployment." [00:17:39]
- "Documentation lies." [00:30:39]
- "Cheap corrections happen on the map, expensive corrections happen in production." [00:35:58]
- "A rule is not real until the person who lives it says, yes, that's the rule." [00:39:08]
- "That never happens is not an answer, it's a prediction that it will happen in two weeks." [00:42:41]
- "The audit ends with a scored decision, not enthusiasm." [00:47:57]
- "Anyone can promise automation. The professional tells you what not to automate." [00:48:50]
- "Never flip a switch, climb a ladder." [00:59:01]
- "If you can't show your receipts, you have not earned autonomy." [00:59:28]
- "Every human correction is treasure." [00:59:53]
- "An FDE is a relationship, not a project." [01:01:34]
