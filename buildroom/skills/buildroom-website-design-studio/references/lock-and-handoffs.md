# The lock, and how every other skill uses it

## Locking

```
design_lock.py lock --tweaks Design/landing-page/tweaks.json --page Design/landing-page/page/index.html \
  --out Design/System --direction "Field Guide" --refs T-001,T-004,T-009 \
  --do "Real photos of me at work" --dont "No beach stock photos" --imagery both
```

- It refuses a look that fails contrast, or one whose body text is under the audience minimum. Fix the look on the tweak bar and save again.
- It writes, in `Design/System/` inside the vault:
  - `tokens.json` (other skills read this)
  - `tokens.css` (paste into any page)
  - `slides.json` (flags for the Webinar Builder's deck)
  - `design-system.md` (the one page for humans, including how to brief a designer or VA)
  - `fonts.md` (what to self-host)
- Locking again keeps the earlier `tokens.json` as `tokens-v<N>.json` and bumps the version. A re-lock is a deliberate change: say what changed and why, in the Session Log.
- **Then the check:** `design_check.py check --page <the final page> --tokens Design/System/tokens.json --images Design/landing-page/images.json --vault <vault> --business-file BUILDROOM_BUSINESS_FILE.md --render --out Design/landing-page/check.md`. Only GO goes live.

## The do / don't list

Write 3–5 of each with the member, in their words, from what they said during the session:
- **Do:** "real photos of me at work", "one green button per screen".
- **Don't:** "no stock photos of couples on beaches", "nothing that looks like a bank".

Each line must be something another skill can follow without asking.

## Business File §22 Design System

`design_lock.py section --system Design/System --project Design/landing-page --taste-vault "<vault>/Design/Taste Vault"` prints the seven lines. Write them into §22, set the status, and update the header. On a later session, update the **Used by** line when another skill has read the system.

§18's **Brand kit** line points to §22 once §22 is complete: "Brand kit: see §22 (Design System v2)". The Ad Studio's locked assets (face, colour, name, line) stay in §18; colours and fonts come from §22, so there's one source of truth. If §18 already locked a colour or font before this session, Website Design Studio keeps it, unless the member says to change it, and records the change in both sections.

## What each skill does with it

Each of these skills reads §22 before it designs anything. If §22 is `complete`, it uses `Design/System/tokens.json` and the do/don't list and doesn't invent a palette or fonts. If §22 is empty, it carries on as before and offers this skill once.

| Skill | Uses |
|---|---|
| **Lead Capture** | `tokens.css` in the landing, opt-in and thank-you pages; the photo rules |
| **Offer Page Copy** | `tokens.css` in the sales page build; the do/don't list |
| **Webinar Builder** | `slides.json`: `slide_builder.py build … --theme <theme> --accent <accent> --font "<font>"` |
| **Ad Studio** | colours, fonts and photo rules for the brand kit; the do/don't list in the brief |
| **Video Director** | the accent and font for captions and end cards |
| **Proof Engine, Training Docs, One-pagers** | `tokens.css` for anything printed or shared |
| **Second Brain (Obsidian)** | the taste vault lives in `Design/Taste Vault/`; a weekly "add three references" routine keeps taste growing |

A page another skill builds from §22 should still pass `design_check.py check --tokens …`.
