# Deep Discovery: the member's own business

_Added 2026-11-19. Revised 2026-11-21 after three trial runs. The research-first idea taken further for a member's own business: read what they already have, show them what was found, ask only the few questions that matter most, and say plainly how ready the file is._

Deep Discovery is how the engine runs on **the member's own business**. A client or a prospect still runs the original pipeline in `discovery-method.md`.

The helper is `scripts/discover.py`. It never opens a member's file and never goes online. It lists file names, and it checks and prints the ledger the session writes.

## The order

1. Agree the scope
2. Research in three rings
3. Write the findings ledger
4. Show "What I found"
5. Ask the few questions that matter
6. Say how ready the file is, and what to do about it

The scope question in step 1 and the Business File intake come first. After those, ask nothing about the business until the member has seen the page in step 4.

Deep Discovery produces the page, the ledger and two lists. It does not produce a Discovery Brief, and it does not ask for a 1 to 5 rating. Those belong to the full Genie run.

## 1. Agree the scope, before reading anything

Research reads private files, so the member decides what is read.

- **A folder or an Obsidian vault** (Cowork, Claude Code, Codex): run `discover.py inventory <folder>`. It lists file names, sizes and dates, most useful first, and opens nothing. It lists the Business File on its own line: that is the member's own word, not research. If it finds two Business Files, ask which is current before anything else (the protocol says how). Files whose names look private (passwords, tax returns, bank statements, medical records, payroll, a Personal or Private folder, a journal) are listed separately and are **not** read unless the member says so. Show the member the list and ask: "Is there any folder or file here you want me to leave alone?" Re-run with `--exclude` followed by each folder or file they name. The output confirms what was left out.
- **Google Drive or another drive** (only if the member has that connector turned on): search for titles first, show the list of titles, and get the same agreement before opening any document. If no drive connector is present, say so in one line and move on. Never ask for a password or a share link to get around it.
- **A regular chat with no folder:** the member attaches or pastes what they want read. That is the scope.

The inventory never lists `discovery/`, `autopilot/` or `backups/`. Those hold what Build Room sessions wrote. A draft is never evidence about the business, wherever it is saved.

Record the agreement in the ledger's `scope`: what was read, what was excluded, how many files were opened, and the date with the member's words. `discover.py check` fails without it.

Everything read stays on the member's computer. Nothing from their files is sent anywhere except to the model doing the reading.

## 2. Research in three rings

Work from the inside out.

| Ring | What | What it is best for |
|---|---|---|
| **1. Their own files** | notes, proposals, sales pages, transcripts, emails they kept, client documents | offer, price, process, how they talk, real client results |
| **2. Their public footprint** | website, LinkedIn, Google Business Profile, reviews, podcasts, posts | what a stranger sees today, review language, public proof |
| **3. Their market** | who a client would compare them with, and the words buyers use in public | the alternative, the category, client language |

Ring 3 is light here. The Audience Insight session owns deep market language; name it as a next step instead of redoing it. With no web access, say so once and skip rings 2 and 3.

While reading, collect:

- **Voice samples.** Short passages the member wrote or said themselves (an email, a post, a transcript, a voice memo), copied exactly, with where each came from. Three to six is enough. Never a passage someone else wrote for them, and never one you tidied. A private note to themselves is not a voice sample.
- **Proof.** Real client results found in the files or in public reviews, copied exactly with the source, who said it, and whether permission to use it is known: `yes` only where the files show the client agreed, `no` where the client asked not to be named or quoted, otherwise `unknown`. Finding a result is not permission to publish it; the Proof Engine session owns that. A result the member only heard about ("someone told me revenue doubled, I never saw numbers") is not proof. Leave it out.
- **Client words.** Exact phrases a client or prospect used first-hand, from reviews, emails, messages or transcripts, with who said it. Not the member describing their clients, and not hearsay.
- **Retired lines.** Read §1 Retired lines in the Business File before you start. When a retired line turns up in a file, record the finding with `"retired": true`. It is never used, and the page tells the member where it still lives.

**Old material.** A source is out of date when it sits in an archive or "Old" folder, is dated well before a newer source on the same subject, or names something the member has since changed. Record what it says with `"stale": true` and confidence `inferred`. Do not throw it away and do not rely on it. For prices, guarantees, offer names and how the work runs, an old finding with nothing newer is always put to the member.

Read with a purpose. Open the files the inventory ranks highest, stop when the ledger's fields are covered, and record how many files were opened.

## 3. The findings ledger

Every fact goes into `discovery/ledger.json` with where it came from and how sure it is. Nothing is written into the Business File from memory of the reading.

```json
{
  "subject": "Business name",
  "date": "2026-11-21",
  "scope": {"read": ["Vault: Offers, Clients"], "excluded": ["Personal"], "opened": 9, "agreed": "2026-11-21: 'leave out Personal'"},
  "findings": [
    {"id": "f1", "field": "1.who_i_serve", "value": "Owner-dentists with one or two locations", "claim": "independent dental practice owners",
     "source": {"kind": "business_file", "ref": "§1"}, "confidence": "confirmed"},
    {"id": "f2", "field": "1.who_i_serve", "value": "Bookkeeping for independent dental practices", "claim": "independent dental practice owners",
     "source": {"kind": "web", "ref": "https://example.com/"}, "confidence": "likely"},
    {"id": "f3", "field": "1.price", "value": "$3,000",
     "source": {"kind": "file", "ref": "Old/Proposal 2024.md", "date": "2024-05-01"}, "confidence": "inferred", "stale": true},
    {"id": "f4", "field": "x.proof", "value": "Overhead found to be 71 percent in three months", "quote": "Three months in I knew my overhead was 71 percent",
     "who": "a named client", "permission": "yes", "source": {"kind": "file", "ref": "Clients/testimonials.md"}, "confidence": "likely"}
  ],
  "skipped": ["1.tools"],
  "files_current": ""
}
```

**Source kinds**

| Kind | Means | Needs |
|---|---|---|
| `business_file` | already in their Business File. This is the member's own word from an earlier session. It may be `confirmed`. | the section, for example `§1` |
| `member` | they said it in this session. Always `confirmed`. | a note such as "said in session" |
| `file` | found in one of their files | the path, and a `date` where you can see one |
| `web` | found on a public page | the full address |
| `hypothesis` | your reasoning. Always `inferred`. | what it was reasoned from |

**Confidence, in three plain words**

| Word | Rule |
|---|---|
| **confirmed** | the member's own word (this session or the Business File), or two independent sources agree |
| **likely** | one good, current source says it plainly |
| **inferred** | reasoned from evidence, or found only in an out-of-date source |

One source is never "confirmed", and two parts of the same file are one source. The script refuses both.

**Keep `value` in the source's words. Say what it claims in `claim`.** Two sources rarely use the same sentence. Give findings on the same single-answer field a short `claim` in your own plain words. Findings with the same claim agree. Findings with different claims disagree, and `discover.py conflicts` lists them. This is the one place you judge whether two sources mean the same thing, so judge narrowly: "bookkeeping for dental practices" and "monthly bookkeeping plus a numbers call for dentists" are the same claim about what they do; "$3,000" and "$4,800" never are. When in doubt, give them different claims and let the member decide. Prices compare on their numbers without a claim.

**When sources disagree, record both.** You never pick. The member does.

**Other keys**

- `quote`: required for client words, voice samples and proof. The exact words.
- `who`: who said it, for client words and proof ("a named client", "a prospect, by direct message", "a Google reviewer").
- `permission`: required for proof. `yes`, `no` or `unknown`.
- `stale`: true for a finding from an out-of-date source.
- `retired`: true for a finding that contains a retired line.
- `absent`: true when the member tells you there is none (no guarantee, no testimonials yet). Only the member can say this. "No guarantee" is a real answer. "No proof" is not proof, and earns no readiness.
- `skipped` (top level): the fields whose question the member skipped. They are not asked again.
- `files_current` (top level): filled in step 4, see below.

**Fields.** The field keys are fixed, so the script can rank and score them: `1.what_i_do`, `1.who_i_serve`, `1.core_result`, `1.price`, `1.lead_sources`, `1.tools`, `1.booking`, `2.profile`, `2.pains`, `2.dream`, `2.trigger`, `2.objections`, `2.negative`, `2.language`, `3.offer_name`, `3.promise`, `3.structure`, `3.deliverables`, `3.guarantee`, `3.typical_result`, `4.alternative`, `4.category`, `4.differentiator`, `x.story`, `x.credentials`, `x.voice`, `x.proof`. A sentence that speaks to two fields is recorded once under each.

Something that fits no field (an idea for a future offer, a to-do) is not a finding. Put it in §13 as a `captured` row if the member would want it kept.

Run `discover.py check discovery/ledger.json --business-file BUILDROOM_BUSINESS_FILE.md` and fix everything it lists before showing the member anything. With the Business File it also catches a retired line you missed.

## 4. Show "What I found"

Run `discover.py page` and give the member the page, saved as `discovery/What_I_Found.md`. It lists what was read and left alone, each finding with its confidence and every source, who said each quote and whether it may be used, the things that disagree, older material that is not being relied on, retired lines still sitting in their files, what could not be found, and the readiness guide.

Say two things with it:

> Read this and tell me what is wrong. You do not need to answer anything yet.
>
> One question while you read: the lines marked "your file" came from your own documents. Are any of them out of date?

A person corrects a wrong statement faster than they answer an open question, and it shows them the work was done.

- Every correction becomes a new finding with source kind `member`, confidence `confirmed`. A member finding settles a disagreement and outranks every other source. Do not delete the findings it replaces; the ledger is the record.
- If they say their files are current, record their words and the date in `files_current`. From then on a `likely` finding from one of their own current files counts as theirs: it earns full readiness, it is not asked about again, and it may go into the Business File. This does not cover web pages, your own guesses, or anything marked stale.
- If they name something as out of date, mark those findings `stale`.
- If they say nothing is wrong, that is not a confirmation of your guesses. `inferred` findings stay inferred.

## 5. Ask the few questions that matter

Run `discover.py gaps`. It returns at most ten questions, ordered by how much harm a wrong answer would do:

1. the disagreements, because those are corrections,
2. old material on a price, a guarantee, an offer name or how the work runs ("an older source says X. Is that still true?"),
3. the four things that must be known (what they do, who they serve, the core result, the core promise),
4. the other facts nothing reliable was found for,
5. fields with nothing at all, the ones most later work depends on first,
6. last, fields where all you have is your own guess to confirm.

Ask them one at a time, in that order. The member may skip any question. Add a skipped field to `skipped` so it is never asked again. Whatever is left over is listed as "left for the build sessions", which do their own intake.

Do not go past ten. A member who has just seen their business laid out will answer ten good questions. They will not answer thirty.

Each answer is a `member` finding. When the answer is "none" (no guarantee, no testimonials), record it with `"absent": true`. Re-run `check` when the questions are done.

## 6. Say how ready the file is, and what to do about it

Run `discover.py ready`. It prints a number out of 100 and one of two verdicts.

- **Ready:** the score is 70 or more **and** four things are at least "likely": what they do, who they serve, the core result, and the core promise.
- **Not ready yet:** it names what must be known first and the questions that would help most, leaving out the ones the member skipped.

Tell the member what the number is: a guide to how much is known, not a measurement of the business and not a prediction of results.

**When it says not ready, say so plainly and give the member three choices:**

1. answer the questions it names now (a few minutes),
2. run one session by hand, usually the Ideal Client Avatar, which interviews them properly,
3. go ahead with Autopilot anyway, knowing most of what it produces will be blanks and guesses.

Recommend the first. Do not recommend Autopilot to a member who is not ready. A long run on a thin file mostly hands their own few sentences back in different shapes.

## What goes into the Business File

The provenance rule does not bend. Three kinds of finding may go in:

1. what the member said in this session,
2. what two independent sources agree on,
3. a `likely` finding from their own current file, **only after** they said their files are current in step 4. Tag it `[file: path]`.

Nothing `inferred`, nothing stale, nothing retired, and nothing from a web page alone.

| Section | What is written | Status |
|---|---|---|
| **§1** | empty fields that now qualify. Content already there is left as it is. | as it stands |
| **§2** | the one-line profile, pains, objections, dream state, trigger and who they do not serve, as qualified; every first-hand client phrase into **Sourced language** with a tag; your own guesses into **Hypothesis language** | `provisional` |
| **§3** | offer name, promise, structure, deliverables, price, guarantee, as qualified. "Guarantee: none" when the member said none. | `provisional` |
| **§4** | the alternative, category and differentiator, as qualified | `provisional` |
| **§13** | one `captured` row per disagreement the member has not settled, per retired line still in their files, and per idea worth keeping | n/a |
| **§8** | one session row, with the readiness number | n/a |

Sourced-language tags: `[client]` for a client's own words, `[prospect]` for someone who is not a client, `[web: source]` for a public review, each followed by `[file: path]` where it was found in a file. A phrase from a private call or message also gets "not for public quoting".

A section with nothing written into it keeps its old status. Do not mark an empty section `provisional`.

§2, §3 and §4 stay `provisional` because their own sessions own them. Deep Discovery gives those sessions a running start. It does not replace them.

Where you can write files, update the Business File in place and tell the member what changed. Emit the whole file in a code block only in a chat with no folder.

**Not written into the file:** the voice samples and the proof list. Save them as `discovery/Voice_Samples.md` and `discovery/Proof_Found.md`, each item with its source, who said it and its permission, and name both in the §8 note. The Compass session owns §17 and the Proof Engine session owns consent.

## Rules

- Scope first. Nothing is opened before the member has seen the list and agreed.
- Files that look private are never read without a clear yes.
- A source and a confidence on every finding. No exceptions, and no "confirmed" from one source.
- Disagreements go to the member. Never choose between sources yourself.
- Old material is recorded as old, never relied on, and asked about when it is a price, a guarantee, an offer name or how the work runs.
- Retired lines are never used, and the member is told where they still live.
- Hearsay is not proof and is not a client's words.
- Show the page before asking a single question about the business.
- Ten questions at most, most harmful gaps first, skippable. A skipped question is not asked again.
- The readiness number is a guide, said as a guide. When it says not ready, say so and recommend answering first.
- Nothing inferred enters the Business File as fact.
- Finding a client result is not permission to use it.
- A draft a Build Room session wrote is never evidence about the business.
