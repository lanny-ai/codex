# Deep Discovery: the member's own business

_Added 2026-11-19. Revised 2026-11-21 after two rounds of trial runs. The research-first idea taken further for a member's own business: read what they already have, show them what was found, ask only the few questions that matter most, and say plainly how ready the file is._

Deep Discovery is how the engine runs on **the member's own business**. A client or a prospect still runs the original pipeline in `discovery-method.md`.

The helper is `scripts/discover.py`. It never opens a member's file and never goes online. It lists file names, and it checks and prints the ledger the session writes.

## The order

1. Agree the scope
2. Research in three rings
3. Write the findings ledger
4. Show "What I found"
5. Ask the few questions that matter
6. Say how ready the file is, and what to do about it

The scope question in step 1 and the Business File intake come first. Skip the intake's confirm-or-correct summary here: the page in step 4 does that job better. After those, ask nothing about the business until the member has seen the page.

Deep Discovery produces the page, the ledger and two lists. It does not produce a Discovery Brief, and it does not ask for a 1 to 5 rating. Those belong to the full Genie run.

## 1. Agree the scope, before reading anything

Research reads private files, so the member decides what is read.

- **A folder or an Obsidian vault** (Cowork, Claude Code, Codex): run `discover.py inventory <folder>`. It lists file names, sizes and dates, most useful first, and opens nothing. It lists the Business File on its own line: that is the member's own word, not research. If it finds two Business Files, ask which is current before anything else (the protocol says how). Files whose names look private (passwords, taxes, bank statements, profit and loss, medical or therapy records, payroll, a Personal or Private folder, a journal) are listed separately and are **not** read unless the member says so. Show the member the list and ask: "Is there any folder or file here you want me to leave alone?" Re-run with `--exclude` followed by each folder or file they name. The output confirms what was left out.
- **Google Drive or another drive** (only if the member has that connector turned on): search for titles first, show the list of titles, and get the same agreement before opening any document. If no drive connector is present, say so in one line and move on. Never ask for a password or a share link to get around it.
- **A regular chat with no folder:** the member attaches or pastes what they want read. That is the scope.

The inventory never lists `discovery/`, `autopilot/` or `backups/`. Those hold what Build Room sessions wrote. A draft is never evidence about the business, wherever it is saved. If a session's output sits in the top folder (a brief, a script, a log a session wrote), leave it out yourself.

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
- **Proof.** Real client results found in the files or in public reviews, copied exactly with the source, who said it, and whether permission to use it is known: `yes` only where the files show the client agreed, `no` where the client asked not to be named or quoted, otherwise `unknown`. Finding a result is not permission to publish it; the Proof Engine session owns that. A result the member only heard about ("someone told me revenue doubled, I never saw numbers") is not proof. Leave it out; the script refuses it. A public review stays `unknown`: a draft may point to where the reviews are, and may not reproduce one until the member says yes.
- **Client words.** Exact phrases a client or prospect used first-hand, from reviews, emails, messages or transcripts, with who said it. Not the member describing their clients, and not hearsay. A line in the member's own notes that sounds like a client but names no speaker is recorded as `inferred` with `who` "not named, from your own notes", and goes under Hypothesis language, never Sourced language.
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
- `guess_ok`: true on a `member` finding when the wording is yours and the member only said yes to it. See step 5.
- `retired`: true for a finding that contains a retired line.
- `absent`: true when the member tells you there is none (no guarantee, no testimonials yet). Only the member can say this. "No guarantee" is a real answer. "No proof" is not proof, and earns no readiness.
- `skipped` (top level): the fields whose question the member skipped. They are not asked again.
- `files_current` (top level): filled in step 4, see below.

**Fields.** The field keys are fixed, so the script can rank and score them: `1.what_i_do`, `1.who_i_serve`, `1.core_result`, `1.price`, `1.lead_sources`, `1.tools`, `1.booking`, `2.profile`, `2.pains`, `2.dream`, `2.trigger`, `2.objections`, `2.negative`, `2.language`, `3.offer_name`, `3.promise`, `3.structure`, `3.deliverables`, `3.guarantee`, `3.typical_result`, `4.alternative`, `4.category`, `4.differentiator`, `x.story`, `x.credentials`, `x.voice`, `x.proof`. A sentence that speaks to two fields is recorded once under each, with one exception: a §1 line of the Business File is recorded under its §1 field only, not reused to fill a §2 to §4 field.

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
- If they name the files or folders that are out of date, that is also the answer for the rest: mark every finding from the named ones `stale`, and record their words and the date in `files_current`. The rest of their files are current.
- If they say their files are current, record their words and the date in `files_current`. From then on a `likely` finding from one of their own current files counts as theirs: it earns full readiness, it is not asked about again, and it may go into the Business File. This does not cover web pages, your own guesses, or anything marked stale.
- If they name one line as out of date, mark that finding `stale`.
- If they do not answer the question about their files at all, leave `files_current` empty. Do not ask twice.
- If they say nothing is wrong, that is not a confirmation of your guesses. `inferred` findings stay inferred.

## 5. Ask the few questions that matter

Run `discover.py gaps`. It returns at most ten questions, in this order:

1. the disagreements, because those are corrections,
2. old material on a price, a guarantee, an offer name or how the work runs ("an older source says X. Is that still true?"),
3. the four things that must be known (what they do, who they serve, the core result, the core promise). When the core result is already the member's own word and the promise is not known, the promise is put as that result to confirm, not as an open question,
4. what every owner knows off the top of their head: the price, what a client receives, how someone books, the guarantee, how the work runs, their background, the offer's name,
5. the other fields with nothing reliable, the ones most later work depends on first,
6. last, fields where all you have is your own guess to confirm.

Ask them one at a time, in that order. The member may skip any question. Add a skipped field to `skipped` so it is never asked again. If an answer to one question also answers another, record it under both. Whatever is left over is listed as "left for the build sessions", which do their own intake.

Do not go past ten in this round. A member who has just seen their business laid out will answer ten good questions. They will not answer thirty.

Each answer is a `member` finding.

- When the answer is "none" (no guarantee, no testimonials yet, no typical result they can back up), record it with `"absent": true`. That question is then answered and is not asked again.
- When the question was "my best guess is X. Is that right?" and the member only says yes, the wording is still yours. Record a `member` finding with `"guess_ok": true`. It earns full readiness, the page shows it as "my wording; you said it looks right", and it goes into the Business File tagged `[reviewed draft]`. It is never shown as something the member said. If they reword it, it is their word and carries no flag.

Re-run `check` when the questions are done, then run `page` again and save it, so the saved page shows the answers.

## 6. Say how ready the file is, and what to do about it

Run `discover.py ready`. It prints a number out of 100 and one of two verdicts.

- **Ready:** the score is 70 or more **and** four things are at least "likely": what they do, who they serve, the core result, and the core promise. A core result in the member's own words stands in for a missing promise, because a promise can be drafted as a plain restatement of it.
- **Not ready yet:** it names what must be known first, the questions that would help most (leaving out the ones the member skipped or answered with "none"), and the one session to run by hand.

Tell the member what the number is: a guide to how much is known, not a measurement of the business and not a prediction of results.

**When it says not ready, say so plainly, once, and give the member their choices:**

1. answer the questions it names now (a few minutes). Offer this only when it names some,
2. run the session it names by hand, which interviews them properly,
3. go ahead with Autopilot anyway, knowing most of what it produces will be blanks and guesses.

Recommend the first when there are questions to ask, otherwise the second. Do not recommend Autopilot to a member who is not ready. A long run on a thin file mostly hands their own few sentences back in different shapes.

**One more round, then stop.** If they choose to answer, ask the questions `ready` names, five at most, and run `ready` again. That is the last round. If it still says not ready, do not ask again and do not offer more questions: tell them the number, name the session to run by hand, and leave the choice with them. When `ready` says there is nothing left to ask, there is no extra round at all.

If Autopilot starts straight after this in the same conversation, it does not put the same choice to the member again.

## What goes into the Business File

The provenance rule does not bend. Three kinds of finding may go in:

1. what the member said in this session. A guess of yours they said yes to (`guess_ok`) goes in tagged `[reviewed draft]`,
2. what two independent sources agree on, tagged with both: `[sources: a; b]`,
3. a `likely` finding from their own current file, **only after** they said their files are current in step 4. Tag it `[file: path]`.

Nothing `inferred`, nothing stale, nothing retired, and nothing from a web page alone.

| Section | What is written | Status |
|---|---|---|
| **§1** | empty fields that now qualify, including how someone books, their background, a typical client result, and anything they refuse to claim. A line the member retires goes into Retired lines at once, in quotation marks, entries separated by semicolons. Content already there is left as it is. | as it stands |
| **§2** | the one-line profile, pains, objections, dream state, trigger and who they do not serve, as qualified; every first-hand client phrase into **Sourced language** with a tag (an exact quote with its source does not wait for the member to say their files are current); your own guesses into **Hypothesis language** | `provisional` |
| **§3** | offer name, promise, structure, deliverables, price, guarantee, as qualified. "Guarantee: none" when the member said none. | `provisional` |
| **§4** | the alternative, category and differentiator, as qualified | `provisional` |
| **§13** | one `captured` row per disagreement the member has not settled, per retired line still in their files, and per idea worth keeping | no status line to set |
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
- Ten questions at most, then one more round of five at most if the file is not ready. A skipped question, or one answered with "none", is not asked again.
- A guess the member said yes to is their approval of your wording, not their own words.
- The readiness number is a guide, said as a guide. When it says not ready, say so and recommend answering first.
- Nothing inferred enters the Business File as fact.
- Finding a client result is not permission to use it.
- A draft a Build Room session wrote is never evidence about the business.
