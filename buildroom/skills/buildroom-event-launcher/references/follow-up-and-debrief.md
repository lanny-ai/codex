# Follow-up and the debrief

## 1. Follow up by where each person stopped

"Don't restart the pitch. Restart the work: one email, one person's exact next step, one link." [founder] Segment by the last thing each person did, not just "attended or not". The founder's production data showed nine real segments after his July camp [founder]. The usual ones:

| Where they stopped | What they get | When |
|---|---|---|
| Registered, never came | The first-win tool directly (if they didn't finish it), then the shortest useful replay; never "sorry you missed it" | Within hours of Day 1 ending |
| Came Day 1 only | What they missed on Day 2 in five lines, and the link to the next live day | Night of Day 2 |
| Stayed to the end, did not buy | One email to find the reason (money, doubt, timing), with the cohort date so "not now" becomes a date; for the most engaged, a personal note referencing something they actually said | Day after the close, then the cart window |
| Took a small first step (a $1 or low-price item) and never saw the main offer | The offer, personally, with what they already own shown | Same day |
| Started checkout, did not finish | A personal email the same day naming what happened, with a working link | Same day |
| Bought | Their first win within 24 hours, access they can prove they reached, the live buyer session if promised, a welcome | Within 24 hours |
| Bought on a custom term | The term written into their client record and the payment link sent the same day | Same day |

The re-engagement shape for the non-buyers, once the cart closes: about five emails over ten days (the thing they built, proof, the objection, the deadline, a clean "I'll stop asking about this", then actually stop). [founder] Follow-up workflows are built and published before the event (gate item), and the **Decision Machine** builds them in GoHighLevel.

## 2. Replay

Send the replay within 1–3 hours of each day ending [data: WebinarNinja, vendor: opens fall about 40% after three hours]. Keep it about seven days, and say when it expires. Cut the close day into a short replay of the offer with both payment options and the guarantee. Turn the recordings into written how-to steps for buyers. Promoting the replay to non-attendees adds about 15% more viewers [practitioner, via Demio]. Keep one replay index (the founder's members asked "where's the replay" every week without one). [founder]

## 3. Buyers first

A sale is delivered when the buyer has reached the thing they paid for, not when they paid. [founder] Every buyer gets their login, their first step and a welcome within 24 hours, and someone checks that they got in. The founder's own records show a recurring list of customers who could not reach what they had bought; he calls it his most expensive pattern. [founder]

## 4. The debrief

Once the cart closes and the follow-up has run, send a three-question survey to everyone who came (what helped most, what got in the way, what would have made you buy or buy sooner); the answers go into the debrief.

1. **The numbers.** `python3 <skill>/scripts/launch_tracker.py report --md` (writes `launches/<slug>/debrief-numbers.md`; never the member's own `debrief.md`): every step against the plan, day-over-day retention, the share who saw the price and bought, cash and booked, refunds, revenue per registrant, and the three biggest shortfalls with one fix each. Reconcile buyers and revenue to one number first.
2. **Feedback as a gift, in two passes** [founder]: what worked (protect these), then what could be better. The member self-assesses first; push for specifics ("which email, which minute").
3. **The three leaks**, ranked by money lost, each with one change for next time.
4. **What to protect**: the things that worked and must survive the next launch's changes.
5. **Lessons promoted to the playbook** when they have happened three times. [founder]

## 5. Write it where the next launch will read it

- `launches/<slug>/debrief.md` always.
- The member's Obsidian vault, if they keep one: `launch_tracker.py obsidian --vault <path>` writes `launches/YYYY-MM-<slug>.md` with light frontmatter and appends a line to `launches/_index.md` (`obsidian-launch-memory.md`). It never overwrites an existing note without `--force`.
- §20 *Results*, *Lessons for next time*, and one line under *Past launches*.
- A §13 row for each thing to build before the next launch (a consented case study, a replay index, a cohort calendar, a price page).

## 6. What comes next (decide two weeks after the cart closes)

- **Run it again** as a next cohort with the lessons applied (the usual choice after a first launch).
- **Turn it into an evergreen version** (a recorded or "just-in-time" event that runs on its own) only once a live run has converted well; expect roughly half the live conversion [practitioner: Porterfield about 9% live vs 5–6% evergreen; vendor figures similar]. The live host can still run the Q&A and close.
- **Pause** and build what the debrief said was missing (proof, a page, a list).
The non-buyers go back into the member's regular nurture, not into silence; the people who said "not now" get the next cohort date.

The next launch's Phase 0 reads all of this before it plans anything.
