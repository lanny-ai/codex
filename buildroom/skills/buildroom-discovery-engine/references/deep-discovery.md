# Deep Discovery: the member's own business

_Added 2026-11-19. The research-first idea taken further for a member's own business: read what they already have, show them what was found, ask only the few questions that matter most, and say plainly how ready the file is._

Deep Discovery is how the engine runs on **the member's own business**. A client or a prospect still runs the original pipeline in `discovery-method.md`.

The helper is `scripts/discover.py`. It never opens a member's file and never goes online. It lists file names, and it checks and prints the ledger the session writes.

## The order

1. Agree the scope
2. Research in three rings
3. Write the findings ledger
4. Show "What I found"
5. Ask the few questions that matter
6. Say how ready the file is

Never ask a question before step 4. The member sees the work first.

## 1. Agree the scope, before reading anything

Research reads private files, so the member decides what is read.

- **A folder or an Obsidian vault** (Cowork, Claude Code, Codex): run `discover.py inventory <folder>`. It lists file names, sizes and dates, most useful first, and opens nothing. Files whose names look private (passwords, tax, bank, medical, payroll and the like) are listed separately and are **not** read unless the member says so. Show the member the list and ask: "Is there any folder or file here you want me to leave alone?" Re-run with `--exclude` for what they name.
- **Google Drive or another drive** (only if the member has that connector switched on): search for titles first, show the list of titles, and get the same agreement before opening any document. If no drive connector is present, say so in one line and move on. Never ask for a password or a share link to get around it.
- **A regular chat with no folder:** the member attaches or pastes what they want read. That is the scope.

Record the agreement in the ledger's `scope`: what was read, what was excluded, and the date with the member's words. `discover.py check` fails without it.

Everything read stays on the member's computer. Nothing from their files is sent anywhere except to the model doing the reading.

## 2. Research in three rings

Work from the inside out. Inner rings outrank outer ones when they disagree about what is true **today**, but never silently: a disagreement goes to the member (see step 3).

| Ring | What | What it is best for |
|---|---|---|
| **1. Their own files** | notes, proposals, sales pages, transcripts, emails they kept, client documents | offer, price, process, how they talk, real client results |
| **2. Their public footprint** | website, LinkedIn, Google Business Profile, reviews, podcasts, posts | what a stranger sees today, review language, public proof |
| **3. Their market** | who a client would compare them with, and the words buyers use in public | the alternative, the category, client language |

Ring 3 is light here. The Audience Insight session owns deep market language; name it as a next step instead of redoing it.

While reading, collect three things that later sessions need and that a member rarely thinks to hand over:

- **Voice samples.** Short passages the member wrote or said themselves (an email, a post, a transcript), copied exactly, with where each came from. Three to six is enough. Never a passage someone else wrote for them, and never one you tidied.
- **Proof.** Real client results found in the files or in public reviews, copied exactly with the source. Record whether permission to use it is known. If it is not, write "permission unknown". Finding a result is not permission to publish it; the Proof Engine session owns that.
- **Client words.** Exact phrases clients used, from reviews, emails or transcripts, with the source.

Read with a purpose. Open the files the inventory ranks highest, stop when the ledger's fields are covered, and tell the member how many files were opened.

## 3. The findings ledger

Every fact goes into `discovery/ledger.json` with where it came from and how sure it is. Nothing is written into the Business File from memory of the reading.

```json
{
  "subject": "Business name",
  "date": "2026-11-19",
  "scope": {"read": ["Vault: Offers, Clients"], "excluded": ["Personal"], "agreed": "2026-11-19: 'leave out Personal'"},
  "findings": [
    {"id": "f1", "field": "1.price", "value": "$4,500",
     "source": {"kind": "file", "ref": "Offers/2026 program.md", "date": "2026-08-02"}, "confidence": "likely"},
    {"id": "f2", "field": "2.language", "value": "tired of guessing what to post", "quote": "I'm just tired of guessing what to post",
     "source": {"kind": "web", "ref": "https://example.com/reviews"}, "confidence": "likely"}
  ]
}
```

**Source kinds:** `file` (with its path), `web` (with the full address), `member` (they said it in this session), `hypothesis` (your reasoning, with a note on what it was reasoned from).

**Confidence, in three plain words:**

| Word | Rule |
|---|---|
| **confirmed** | the member said so, or two independent sources agree |
| **likely** | one good source says it plainly |
| **inferred** | reasoned from evidence. A hypothesis is always this, and never more |

One source is never "confirmed". The script refuses it.

**Fields.** The field keys are fixed, so the script can rank and score them: `1.what_i_do`, `1.who_i_serve`, `1.core_result`, `1.price`, `1.lead_sources`, `1.tools`, `2.profile`, `2.pains`, `2.dream`, `2.trigger`, `2.objections`, `2.negative`, `2.language`, `3.offer_name`, `3.promise`, `3.structure`, `3.deliverables`, `3.guarantee`, `4.alternative`, `4.category`, `4.differentiator`, `x.story`, `x.voice`, `x.proof`. Client words, voice samples and proof must carry the exact `quote`.

**When sources disagree, record both.** An old proposal says $3,000 and the website says $4,500: that is two findings, not one decision. Add a `date` to each source where you can see one. `discover.py conflicts` lists every disagreement. You never pick. The member does.

Run `discover.py check` and fix everything it lists before showing the member anything.

## 4. Show "What I found"

Run `discover.py page` and give the member the page, saved as `discovery/What_I_Found.md`. It lists what was read and left alone, each finding with its confidence and source, the things that disagree, what could not be found, and the readiness guide.

Say one thing with it: "Read this and tell me what is wrong. You do not need to answer anything yet." A person corrects a wrong statement faster than they answer an open question, and it shows them the work was done.

Every correction becomes a new finding with source kind `member`, confidence `confirmed`. A member finding settles a disagreement and outranks every other source. Do not delete the findings it replaces; the ledger is the record.

## 5. Ask the few questions that matter

Run `discover.py gaps`. It returns at most ten questions, in order:

1. the disagreements first, because those are corrections,
2. then the four things that must be known (what they do, who they serve, the core result, the core promise),
3. then the other fields nothing reliable was found for, the ones most later work depends on first.

Ask them one at a time, in that order. Where something is half known, the question quotes the guess. The member may skip any question; a skipped one stays a gap and is not asked again in this session. Whatever is left over is not asked now. It is listed as "left for the build sessions", which do their own intake.

Do not go past ten. A member who has just seen their business laid out will answer ten good questions. They will not answer thirty.

Each answer is a `member` finding. Re-run `check` when the questions are done.

## 6. Say how ready the file is

Run `discover.py ready`. It prints a number out of 100 and one of two verdicts.

- **Ready:** the score is 70 or more **and** four things are at least "likely": what they do, who they serve, the core result, and the core promise.
- **Not ready yet:** it names what must be known first and the questions that would help most.

Tell the member what the number is: a guide to how much is known, not a measurement of the business and not a prediction of results. A thin file gives thin work later, so a low score is useful news, not a failure.

## What goes into the Business File

The provenance rule does not bend. Only what the member confirmed goes in as fact.

| Section | What is written | Status |
|---|---|---|
| **§1** | empty fields that now have a `confirmed` finding | as it stands |
| **§2** | confirmed pains, objections, dream state, trigger; every exact client phrase into **Sourced language** with its tag; anything inferred into **Hypothesis language** | `provisional` |
| **§3** | offer name, promise, structure, deliverables, price, guarantee, as confirmed | `provisional` |
| **§4** | the alternative, category and differentiator, as confirmed | `provisional` |
| **§13** | one `captured` row per disagreement the member has not settled, and per friction point the research surfaced | n/a |
| **§8** | the session row, with the readiness number | n/a |

`likely` and `inferred` findings the member did not confirm stay in the ledger and the page. They do not enter the file as fact.

§2, §3 and §4 stay `provisional` because their own sessions own them. Deep Discovery gives those sessions a running start. It does not replace them.

**Not written into the file:** the voice samples and the proof list. Save them as `discovery/Voice_Samples.md` and `discovery/Proof_Found.md`, and name both in the §8 note. The Compass session owns §17 and the Proof Engine session owns consent.

## Rules

- Scope first. Nothing is opened before the member has seen the list and agreed.
- Files that look private are never read without a clear yes.
- A source and a confidence on every finding. No exceptions, and no "confirmed" from one source.
- Disagreements go to the member. Never choose between sources yourself.
- Show the page before asking a single question.
- Ten questions at most, most important first, skippable.
- The readiness number is a guide, said as a guide.
- Nothing inferred enters the Business File as fact.
- Finding a client result is not permission to use it.
