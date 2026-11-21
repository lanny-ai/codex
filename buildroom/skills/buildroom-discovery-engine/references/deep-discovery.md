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

The scope question in step 1 comes first, then the Business File intake. Skip the intake's confirm-or-correct summary here: the page in step 4 does that job better. After those, ask nothing about the business until the member has seen the page.

Deep Discovery produces the page, the ledger and two lists. It does not produce a Discovery Brief, and it does not ask for a 1 to 5 rating. Those belong to the full Genie run.

## 1. Agree the scope, before reading anything

Research reads private files, so the member decides what is read.

- **A folder or an Obsidian vault** (Cowork, Claude Code, Codex): run `discover.py inventory <folder>`. It lists file names, sizes and dates, most useful first, and opens nothing. It lists the Business File on its own line: that is the member's own word, not research. If it finds two Business Files, ask which is current before anything else (the protocol says how). Files whose names look private (passwords, taxes, bank statements, profit and loss, medical or therapy records, payroll, a Personal or Private folder, a journal) are listed separately and are **not** read unless the member says so. Show the member the list and ask: "Is there any folder or file here you want me to leave alone?" Re-run with `--exclude` followed by each folder or file they name. The output confirms what was left out.
- **Google Drive or another drive** (only if the member has that connector turned on): search for titles first, show the list of titles, and get the same agreement before opening any document. If no drive connector is present, say so in one line and move on. Never ask for a password or a share link to get around it.
- **A regular chat with no folder:** the member attaches or pastes what they want read. That is the scope.
- **Almost nothing to read** (fewer than three files worth opening and no website): offer the Quick Start interview below instead of research.

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
- **Client words.** Exact phrases a client or prospect used first-hand, from reviews, emails, messages or transcripts, with who said it. Words from a private message, email or call carry `"permission": "no"` unless the files show the person agreed: they inform the work and never appear in public copy. Not the member describing their clients, and not hearsay. A line in the member's own notes that sounds like a client but names no speaker is recorded as `inferred` with `who` "not named, from your own notes", and goes under Hypothesis language, never Sourced language.
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

Ask the second part only when the page has at least one line that came from a file. With nothing from a file, there is nothing to be out of date.

A person corrects a wrong statement faster than they answer an open question, and it shows them the work was done.

- Every correction becomes a new finding with source kind `member`, confidence `confirmed`. A member finding settles a disagreement and outranks every other source. Do not delete the findings it replaces; the ledger is the record.
- If they name the files or folders that are out of date, that is also the answer for the rest: mark every finding from the named ones `stale`, and record their words and the date in `files_current`. The rest of their files are current. Say that back in one line ("I will treat everything else as current") so they can correct it.
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
5. what they can say without looking anything up: how people find them, their tools, a typical result, who they turn away, why they started,
6. the other fields with nothing reliable, the ones most later work depends on first,
7. last, fields where all you have is your own guess to confirm.

Ask them one at a time, in that order. The member may skip any question. Add a skipped field to `skipped` so it is never asked again. If an answer to one question also answers another, record it under both. Whatever is left over is listed as "left for the build sessions", which do their own intake.

Do not go past ten in this round. A member who has just seen their business laid out will answer ten good questions. They will not answer thirty.

Each answer is a `member` finding.

- When the answer is "none" (no guarantee, no testimonials yet, no typical result they can back up), record it with `"absent": true`. That question is then answered and is not asked again.
- When the member says they dropped a guarantee, an offer name or a claim, its old wording goes into §1 Retired lines at once, in quotation marks, and every finding that carries it is marked `retired`.
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

**One more round, then stop.** If they choose to answer, ask the questions `ready` names, five at most, then set `"extra_round": true` at the top level of the ledger and run `ready` again. That is the last round. The extra round leaves out the harder questions in a section where the member already skipped two, because they will skip those too. If it still says not ready, do not ask again and do not offer more questions: tell them the number, name the session to run by hand, and leave the choice with them. When `ready` says there is nothing left to ask, there is no extra round at all.

If Autopilot starts straight after this in the same conversation, it does not put the same choice to the member again.

## The first session: a new member's first fifteen minutes

This is what runs when a brand-new member says **"I'm new here. Help me get started."** The navigator welcomes them and hands over to this section. The aim is that they leave with something they can use today, and that the first thing they see is their own business understood, not a form.

**Read only what this needs:** this section, the Business File protocol and the template. Not the Genie source, the discovery method or the certainty adapter. A new member should not wait while you read.

**A new member is not asked about a Business File.** They said they are new. If there is no file in the folder, create one in step 7. Do not ask whether they keep one somewhere else, do not ask for a rating at the end, and do not tell them to save over an old copy.

1. **Ask one thing.** "Do you have a website or a LinkedIn page for the business? Paste the address, or say you have nothing online." Nothing else yet.
2. **If they give an address and you can reach the web,** read that page and up to three more on the same site (about, services or pricing, contact). Read nothing else and nobody else's site. Record what you find as `web` findings in `discovery/ledger.json`, in the page's own words, with the scope `{"read": ["<the address>"], "agreed": "<date>: they gave the address"}`.
   Then show them, in the chat, **"Here is what I learned about your business"**: twelve lines at most, numbered, one fact to a line, the plainest facts first (the business's name and theirs, what you do, who it is for, the result, what you sell and what a client receives, the price if it is shown, how someone books, their background), each with the page it came from. If the site holds more than fits, say so in one line ("There is more on your site; I have left the rest for later"). End with: "Tell me what is wrong or out of date. If it is right, say so."
   - A line they correct becomes a `member` finding in their words, and the site's version is marked `"stale": true`.
   - A line they say is right becomes a `member` finding: it is their own site and they have just confirmed it. "The rest is right" covers only the lines they named or plainly meant.
   - **Then ask once about the lines they did not mention,** naming them so they do not have to scroll back: "You did not mention your booking call, Puppy Start or your background. Are those still right?" What they confirm becomes theirs. What they still do not confirm stays a `web` finding: it is not theirs yet and does not go into the Business File.
   - If they drop something (a guarantee, an offer name, a claim), mark that finding `"retired": true` at once. "I stopped offering it" about a guarantee means there is none now: record a `member` finding for the guarantee with `"absent": true`. The page check reads retired lines from the ledger, so it is barred before the Business File exists. Tell them once, plainly, that their site still shows it.
   - Never guess what a page does not say. A site with no price has no price.
3. **If they have nothing online, or you cannot reach the web,** say so in one line ("That is fine. I will just ask you a few things instead.") and go on. Do not ask them to paste their site.
4. **Ask only what is still missing,** one at a time, in these words or plainer ones. Skip any that the member has already said or confirmed. Any can be skipped; say so once at the start.
   1. "What is your name, and what do you call the business?" (Skip if they confirmed both from their site. This becomes the ledger's `subject` and the Business File header.)
   2. "In a sentence or two, what do you do for people?"
   3. "Who do you do it for?"
   4. "What is the main thing they get out of it?"
   5. "What do you charge today? A price or a range is fine."
   6. "What does someone actually get when they hire you?"
   7. "How do people find you today?"
   8. "When someone is ready, how do they book or buy?"
   9. "What should someone know about your background? Training, experience, how long you have done this."
   10. Only if they have something online: "What do you use to run things: email, website, calendar?" A member with nothing online is not asked about tools.
   Stop there. This is a first session, not the interview. `discover.py ready` may print more questions; do not ask them.
5. **Write up to three ways to say what they do,** from their own words only, as `discovery/first_words.json`: one sentence, one paragraph, and a short bio. Use their nouns and their phrasing; yours are only the joining words. Record their own name in the ledger's top-level `owner`, so the check knows it is theirs. Add no number, no result, no credential and no claim they did not give, and nothing from their site that they did not confirm. No bio unless they gave their background or their story. These are drafts and the page says so.
6. **Build the page:** `onepage.py check discovery/ledger.json --words discovery/first_words.json`. Fix every `FIX`. For every `LOOK`, which lists words in a draft that the member never used, keep a word only if it adds no fact of its own. A clean check is not proof; read the drafts once more against what they said. Then `onepage.py build discovery/ledger.json Your_Business_On_One_Page.html --words discovery/first_words.json --next "Help me describe my best customer" --why "This session works out who your best customer is, so everything after it is written to one person."` Tell them to open the page by double-clicking the file.
7. **Create the Business File** from the template:
   - the header's Owner and Business, from what they said. If they have no business name, use their own name for both the page and the Business line, and do not make one up;
   - §1 from what is now theirs, status `provisional`. Write their tools answer as they gave it, in place of the empty slots;
   - into §3, with status `provisional`, whatever they said or confirmed about what they sell: the offer's name, how the work runs, what a client receives, the price, any second offer, and "Guarantee: none" if they have none, so the offer session does not ask again;
   - anything they retired into §1 Retired lines;
   - a question they skipped is written as "skipped" in its field, and tools as "nothing online" for a member who has nothing online, so nobody asks again;
   - one §8 row, rating "not asked: first session".
   Where files can be written, save it in the folder and say where. Do not print it into the chat.
8. **Close with one next step,** not a menu. The last message holds three things and nothing else: where their page is, where their Business File is (with one line saying most of it is empty on purpose, because later sessions fill it in), and the one step: say **"Help me describe my best customer"**, the session that works out who their best customer is. No Compass, no second phrase, and no session names they have not heard.

**In a chat with no folder,** nothing can be saved and no script can run. Check the drafts by hand against the same rules. End with one message in this order: their words under plain headings; the drafts, each marked DRAFT; the one next step; and last, the start of their Business File in one code block, **only the header, §1, any §3 lines and the §8 row**, with one line saying "Save this as a note or a document. Later sessions add to it." Do not emit the empty template.

Keep it to about fifteen minutes. The page is the payoff: get to it.

## Quick Start: when there is little to read

Some members have nothing written down: no notes, no website, no saved emails. Research has nothing to find, and ten ranked questions put the hardest ones first. For them, run the short interview instead. It is also what a member gets when they say **"Interview me about my business"**.

Use it when the member asks for it, or when the inventory in step 1 shows fewer than three files worth reading and there is no website. Say why in one line ("There is not much written down to research, so the quickest way is a short interview") and let them choose.

1. Start the ledger as usual. With no files read, the scope is `{"read": [], "agreed": "<date>: interview only, no files read"}`. Record what the Business File already holds as `business_file` findings.
2. Run `discover.py interview`. It prints the questions still open, in three short blocks, the easy facts first: **your offer**, **your client**, **you and your business**. It leaves out anything already known, skipped or answered with "none", and it does not ask for client quotes, voice samples or proof, because those are found, not recalled.
3. Tell the member how many questions there are and how long it takes, that any can be skipped, and that "none" is a real answer. Ask them one at a time, in order. Say which block you are in when it changes.
4. Record each answer as a `member` finding **in their words**. Do not improve an answer. Ask a follow-up only when you cannot understand the answer. One pass only: when the list is done, the interview is done.
5. Run `check`, then `discover.py onepage`, and save it as `discovery/Your_Business_On_One_Page.md`. Show it to the member. It holds only what they said, as they said it, and lists what is still open. It is not copy and it is not polished.
6. Run `discover.py ready` and say what it says, as in step 6 above. Then update the Business File as below.

The interview does not replace the build sessions. It gives the Ideal Client Avatar and Signature Offer sessions, and an Autopilot run, real answers to start from.

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
- In the Quick Start interview, an answer is recorded as given. One pass, no polishing, no follow-up unless it cannot be understood.
- Nothing inferred enters the Business File as fact.
- Finding a client result is not permission to use it.
- A draft a Build Room session wrote is never evidence about the business.
