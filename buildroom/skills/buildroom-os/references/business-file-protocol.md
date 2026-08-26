# Business File Protocol

Every Build Room skill follows this protocol. It is what turns 36 standalone sessions into one compounding system: the member's context persists in a single document — the **Build Room Business File** — that every session reads at the start and updates at the end.

A blank copy of the file lives at `references/business-file-template.md`.

---

## The contract

1. **Read before asking.** At session start, ask the member for their Business File. Every input question the file already answers is skipped — confirmed, not re-asked.
2. **Write before ending.** At session end, hand back the complete updated file. A session that ends without updating the file is unfinished.
3. **The member's edits always win.** The file is theirs. Never overwrite hand-edited content without asking; never "correct" their file silently.
4. **Never invent facts into the file.** Only member-confirmed content goes in. Drafts and inferences stay in session deliverables until the member approves them.

---

## Session start — intake

Open every session with (adapt wording to the skill's voice):

> "Do you have your **Build Room Business File**? Paste it or attach it and I'll pick up exactly where your business left off. If you don't have one yet, no problem — I'll create it for you as we go."

**If they provide the file:**
- Parse the section statuses and content.
- Pre-fill this session's input template from it. Show the member a short summary of what you already know ("Here's what I'm working from…") and ask them to confirm or correct — one message, not a re-interview.
- Only ask the input-template questions the file leaves blank.
- If the file marks a prerequisite section `provisional`, tell the member their outputs today will inherit that provisional status until the prerequisite session is run properly.

**If they don't have the file:**
- Say you'll create one. Run the skill's normal intake questions, and additionally capture the §1 Business Snapshot fields if they emerge naturally (don't add a separate interview for them).
- Build the file from `references/business-file-template.md` at session end.

**If a prerequisite section is missing** (each skill's SKILL.md names its prerequisites):
- Offer two paths, member's choice:
  a. **Run the prerequisite session first** (recommend this when the gap is §2 ICA — everything downstream depends on it), or
  b. **Provisional interview** — a compressed 4–6 question version of the prerequisite's core inputs, 5 minutes, clearly framed as a stopgap. Mark every section built on it `provisional` in the file, and say plainly: "This will work, but the output gets meaningfully stronger once you run the full [session name] session."
- Never silently fabricate the missing foundation.

## During the session

- When a prompt in `references/prompt-system.md` says to pull from a Week-N document ("Pull this from your Week 1 ICA document"), pull it from the corresponding Business File section instead. The file is the canonical carrier of prior work.
- If the member contradicts the file mid-session ("actually we raised our price"), use the new fact and note it for the end-of-session update.

## Session end — the update

Before closing, always:

1. **Update the sections this session built.** Distilled decisions and key verbatims only — the file stores the *essence*; full deliverables (complete ICA document, full page copy, full email sequence) are separate documents the member saves, referenced from the file by name.
2. **Set the status line** on each touched section: `complete` or `provisional`, today's date, this skill's name.
3. **Append one Session Log row**: date, session name, outputs produced, status, the member's 1–5 rating (ask for it — one question: "Quick gut check: 1–5, how usable is what we built today?"), and any note worth keeping.
4. **Emit the ENTIRE updated file** in a single fenced code block — not a diff, not just the changed sections — so the member can replace their saved copy in one paste. Precede it with a 2–4 bullet "What changed in your Business File" summary.
5. Remind them: "Save this over your old copy. Bring it to every Build Room session."

## Size discipline

The file must stay light enough to paste into any session. Target **under ~2,500 words**. If a section is bloating, distill harder and push detail into the linked full document. Never paste an entire deliverable into the file.

## Conflict rules

- File content vs. member's live statement → the live statement wins; update the file.
- File content vs. this skill's generated draft → the file wins until the member approves the draft.
- Two file sections that contradict each other → surface it to the member ("your §3 price says $5K but §1 says $3.5K — which is current?"), fix per their answer.
