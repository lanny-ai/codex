# The proof bank

`proof/` is the **one** place proof lives. `proof/proof-bank.md` is the index; `proof/stories/P-NN.md` holds one story each; `proof/consents/` holds the clients' replies. Other tools keep their own views (a launch's `proof-bank.md`, the LinkedIn `story-bank.md`, the Ad Studio's copy manifest) by **ID**, copied from here by Place mode, never typed fresh. Counts only go into the Business File (§18); the words stay here.

## IDs

`P-01`, `P-02`, … in order of capture. An ID is never reused, even after a decline or withdrawal; the Ad Studio and others cite it.

## The index

```
# Proof bank

Updated: 2026-10-24 · Consented (named or anonymous): 4 (D 3 · B 1) · Pending: 2 · Declined: 1 · Withdrawn: 0

| ID | Origin | Kind | Permission | Scope | Result (one line) | Proves | Placed |
|---|---|---|---|---|---|---|---|
| P-01 | D | result | named | site, emails, social; no ads; photo no | 13-week cash view in 20 minutes a week, 6 weeks | Cash Flow Program | offer page proof section; launch 2026-12 Day 2 |
| P-02 | B | money | anonymous | site, emails | First paid client 9 days after the free workshop | Workshop → program | LinkedIn post 2026-10-20 |
| P-03 | U | transformation | pending | — | Bootcamp quote, words not yet matched to the recording | — | — |
```

"Consented" counts entries whose state is `named` or `anonymous`, nothing else.

## One story

```
---
id: P-01
title: From guessing to a 13-week cash view
date_captured: 2026-10-24
source: interview by email, 2026-10-22 (proof/consents/P-01-2026-10-23.eml)
origin: D                  # A B D E H X R U
kind: result               # money | result | transformation | freedom
permission: named          # named | anonymous | pending | declined | withdrawn
scope: site, emails, social   # site emails social ads video events
name: yes
company: yes
photo_or_logo: no
material_connection: none  # none | free or discounted | beta | partner | affiliate | relative | other (say what)
reviewed_wording: yes, 2026-10-24 (client saw the offer-page block)
reconfirm_by: 2027-10-24
proves: Cash Flow Program (§3)
placed:
  - offer page, proof section, 2026-10-24
  - launches/2026-12-cash-bootcamp/proof-bank.md, Day 2, 2026-11-30
---

## Before (their words)
"A normal Tuesday was me opening the bank app and hoping."

## Result (their numbers, their timeframe, how measured)
A 13-week cash view the owner updates in 20 minutes on Mondays; six weeks from start; two months of "no surprises". No revenue figure given; none claimed.

## Verbatim
"I used to open the bank app and hope. Now I know what's coming for the next quarter, and I sleep." — Dana Ruiz, owner, Ruiz Advisory

## Typical result to show beside it
"Most clients have a working 13-week view inside two months." (from §3, confirmed by the member)

## Not allowed
Ads (scope), a photo (scope), any free-event claim (origin D).
```

## Rules of the file

- A story with `permission: pending`, `declined` or `withdrawn` is never copied out of this folder.
- `id`, `origin`, `permission`, `scope` and `material_connection` travel with the words whenever another tool uses them.
- Consents (the client's reply, or the dated note of a spoken yes plus its same-day email) are kept in `proof/consents/`, named by ID and date. The Video Director's signed consent forms are referenced here by path.
- A composite (origin X) is its own entry with the label in the verbatim block, so it is never mistaken for a person.
- A withdrawal: set `withdrawn` with the date, remove every placement under `placed` within 10 business days, note anything that cannot be recalled, tell the client when it is done.
- When Place mode hands a story to another tool, it appends the placement to `placed` the same day; the weekly check confirms each placement is live and still consented.
