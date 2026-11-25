# GoHighLevel values: from a finished run to a file ready to load

_Added 2026-11-21._

A member who uses GoHighLevel can have the Build Room OS snapshot: one funnel, one form, one calendar, one pipeline and fourteen emails, with every piece of text that changes per member held in a custom value. This step fills in those values from an approved Autopilot run and writes them to a file.

**It prepares a file. It does not connect to GoHighLevel, and nothing is sent, published or switched on.** Loading the file into an account is a separate step that the member starts: see *Pushing the values into the account* at the end. Writing custom values into a live sub-account has been proven; the snapshot's pages, emails and workflows have not yet been built in a live account. Say so if the member asks.

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

## Pushing the values into the account

Only when the member asks ("Push my build to GoHighLevel"), only after the export above, and only into their own sub-account.

**What the member sets up once, themselves.** In their sub-account: Settings, then Private Integrations, then a new integration with *View Custom Values*, *Edit Custom Values* and *View Locations*. They save two lines in the `.env` file of their working folder: `GHL_TOKEN=` (the token) and `GHL_LOCATION_ID=` (the string after `/location/` in the account's web address). **Never ask a member to paste a token into the chat, never read `.env` aloud, and never put a token on a command line.**

1. `ghl_push.py plan autopilot/ghl` reads the account and prints what would be added and what would change, with the old and new text side by side. It changes nothing. **Show the member this plan.**
2. On their go-ahead: `ghl_push.py push autopilot/ghl --yes`. It creates or updates each value, waits, reads the account back, and writes `GHL_Push_Report.md` and `push_report.json`.
3. Give the member the report, then the list of what only they can do: open each page and read it with their values in place, connect a domain and a sending address, set calendar hours, send themselves a test before turning any workflow on.

What it does and does not do:

- It writes custom values on the snapshot's list and nothing else. It never deletes a value and leaves every other value in the account alone.
- It does not publish a page, send an email, switch a workflow on or touch a contact.
- If the file is marked not complete, it refuses. `--partial` pushes what is ready; that is the member's choice, said in their words, because a page would show a blank where a must-have is missing.
- If the account has no Build Room values at all, the snapshot is probably not loaded. Say so: the values can be written, but nothing will show them.
- A refusal from GoHighLevel is reported in plain words (the token was rotated, the token is for a different account, the token lacks a permission). Values already written stay written; running it again is safe.
