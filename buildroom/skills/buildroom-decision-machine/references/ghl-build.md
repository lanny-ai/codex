# Build it in GHL — from approved emails and trigger map to a working automation

_Added 2026-10-10. The session used to end with copy to paste and a trigger map to build by hand. This phase builds it: the API takes what the API accepts, the agent builds the rest in the browser, and the launch test proves it before anything in §6 is called "built." Runs in Claude Code or Codex in the member's project folder._

## The hard limit, stated up front

GoHighLevel's API does not create workflows. The founder's own August build hit this and the Decision Machine knowledge base records it. So "automatic" has two layers and the second is a browser:

| Layer | What | How | Proof |
|---|---|---|---|
| **API push** | tags, custom fields, email templates, pipeline and stage check | `scripts/ghl_push.py` with the member's private integration key from `.env` | the script's report: created / skipped / failed |
| **Browser build** | the workflows: trigger, each email step, waits, tags, exit; publish | the agent, in Claude Code or Codex with a browser (Claude in Chrome or Playwright), following the script's build sheet | the launch test |

The email-template endpoint is reported, not confirmed from the sandbox that wrote the script. The probe tells you in one call whether it works for this key; if not, the emails go into the workflow steps in the browser and nothing else changes.

## Steps

1. **Only after the emails are approved** (one at a time, Phase 4) and the trigger map is confirmed (Phase 6). Never push drafts.
2. **Ask once:** "Build this in your GoHighLevel now? I need the private integration key and the location id in `.env` as `GHL_API_KEY` and `GHL_LOCATION_ID`. Paste nothing here." Decision Machine rule applies: create the key before the build; tags batch through the API and go one at a time through the browser.
3. **Write `funnel-build.json`** from the session: the tags from the trigger map, custom fields the emails or application need, the pipeline and stages §6 names, every approved email (name, subject, HTML body, day), each workflow as trigger → ordered steps → exit, and the launch test in the order the spec gives it. Use the member's naming convention (lowercase kebab-case tags, one family prefix).
4. **`--dry-run`** and show the member every request and the build sheet. This is the approval step.
5. **`--probe`** once per location: confirms the key, the location, the tags scope, and whether the email builder endpoint answers.
6. **Push.** Idempotent: existing tags and fields are skipped, not duplicated. Read the report. A failed email push means `--skip-emails` and paste in the browser.
7. **Browser build**, workflow by workflow, from the sheet: create, set the trigger, add each step with the exact names, set the exit condition, **publish** (a Draft never fires). Say what you are clicking. If the agent has no browser, hand the member the sheet; it is written to be followed by a person.
8. **Launch test**, one real pass per path with the member's own contact: tags applied, email arrived, wait fired, exit fired on the exit tag, pipeline stage moved. Anything that did not fire is a defect, not a note.
9. **Record** in §6 CRM build: `location · tags/fields pushed (n) · workflows built (names) · launch test passed yes/no · date`. §13 gets one `shipped` row. Nothing is "built" in the file until step 8 passed.

## Rules

- Keys stay in `.env`. The script never prints them; the session never asks for them in chat.
- Nothing here sends a message to a real contact. The launch test uses the member's own contact.
- Push only approved copy. The script is a transport, not an editor.
- The Decision Machine reuses this script and this phase for its campaigns; its build map is the same JSON with more workflows.
- When the API refuses something, the browser build sheet still carries it. Degrade to the browser, never to "later."
