# GoHighLevel values: from a finished run to a file ready to load

_Added 2026-11-21._

A member who uses GoHighLevel can have the Build Room OS snapshot: one funnel, one form, one calendar, one pipeline and fourteen emails, with every piece of text that changes per member held in a custom value. This step fills in those values from an approved Autopilot run and writes them to a file.

**It prepares a file. It does not connect to GoHighLevel, and nothing is sent, published or switched on.** Loading the file into an account is a separate step that the member starts. The snapshot itself has not yet been proven in a live account; say so if the member asks.

Run it only when the member asks ("Prepare my GoHighLevel values") and only after the run's handover, when the drafts have passed `drafts.py check`.

## Steps

1. `ghl_values.py template` prints every value: its key, what it is, where it comes from, how long it may be, whether it is a must-have, and whether it is a **fact**.
2. Write `autopilot/ghl/values.json` from the member's drafts. For each value:
   - Take the text from the draft that owns it (the opt-in page, the offer page, the emails). Copy it; do not rewrite it into something new.
   - Give it its basis: `confirmed` for the member's own word, `files` for something from their current files, `reviewed` for a draft they approved, `drafted` for anything else.
   - **A fact is never drafted.** Prices, the guarantee, proof, links, names, dates and deadlines come from the member or their files, or the value is left out.
   - **Leave out what is not known.** No placeholder text, no `[needs you]`, no guess. An optional value left out means the member removes that section of the page.
   - Keep to the length limit. If the draft is longer, use the part that fits whole; do not cut a sentence in half.
3. `ghl_values.py check --dir autopilot autopilot/ghl/values.json`. Fix every `FIX`. Read every `LOOK` against what the member refuses to claim. It lists the must-haves still missing; those are the member's to supply, usually a link.
4. `ghl_values.py export --dir autopilot autopilot/ghl/values.json autopilot/ghl`. It writes:
   - `GHL_Values_Review.md`: every value in plain sight, tagged as theirs, from their files, or drafted, with what is still needed and what was left empty. **Give the member this first.**
   - `custom_values.json` and `custom_values.csv`: the same values keyed for the snapshot. The file is marked not complete while a must-have is missing.
5. Tell the member what is still needed from them, and what only they can do: connect a domain and a sending address, set calendar hours, test with their own email before turning any workflow on.

## Rules

- Nothing leaves the member's computer in this step.
- Every value reaches a stranger, so every value is held to the draft rules: no retired line, no figure nobody confirmed, no guarantee the member does not have, no client's words without permission.
- Never fill a must-have to make the file complete. An incomplete file that says so is the right result.
- No text messages, no payment pages, no ads. The snapshot has none.
