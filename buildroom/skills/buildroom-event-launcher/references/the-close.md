# The close

The close is planned in Phase 1 and written down in `launches/<slug>/close.md`, the one source of truth every email, page and moderator message copies from: the tiers, prices, payment plans, the guarantee as signed off, the deadline and what it is, the cohort start date, the checkout links and the second checkout path, the replay link and when it expires.

## 1. Decide before the event

- **No more than three doors.** "People buy when they know which door is theirs." Name each by who it is for, not by its contents; state on every tier what it saves or gets them. Show buyers what they already have (the free seat, the tool, the VIP) next to what they would add. [founder]
- **A real deadline**, chosen from what is true: a cohort that starts on a date; a live buyer bonus session that happens once; a founding price that rises for the next group on a stated date; a number of places that is genuinely limited. If none is true, there is no deadline, and the close leans on the reason to start now. "This is your honest deadline. It's real, it's valuable, it's time-bound." [founder] Fake deadlines and resetting timers are enforced against (`launch-gate.md`).
- **A payment plan that does not punish.** "$997, or 3 payments of $349. $50 for the convenience, not $500." Plans that cost 50–137% more read as a penalty. A plan, never a deeper discount. [founder] About +17% conversion from offering plans is a vendor figure [data: SamCart, vendor].
- **The guarantee as signed off**, one guarantee only, said the same way on the page, at checkout and on air. If the guarantee is open in §3 or §13, it is not used.
- **Checkout or application.** Under about $2,000, checkout; above it, an application or a call booked at the event. For calls: the application on screen, a closer or concierge booking from the chat, and calls held within 48 hours.
- **VIP or upgrade as a checkbox after the main sale is locked**, never a second pitch that confuses the first. [founder's seminar rule]
- **A small first step, or not.** The founder's best mechanic: a $1 personalised brief that 102 people bought, which made the main offer a one-click upgrade. **Everyone who takes the small step must see the main offer**: 51 of his never did. [founder] For a call close, the analogue is an application finished during the event, or a short paid or free pre-call brief, so the call starts warm.
- **The deadline decision, made now.** Choose an honest deadline (for a call-closed service, the next install or cohort start date is usually the true one) or choose the no-deadline window (§4) on purpose. Never leave it open into the gate.

## 2. The offer shape on the day

The founder's 12-step offer template (adapted from classic infomercial structure): the reason why → the big benefit → "just for you" → walk through what it is → the price → bonus one → the risk reversal → the best bonus → recap → the best bonus again → the guarantee again. [founder] "The listener who is still deciding is deciding on exactly two things: what's the best thing I can get, and what happens if it doesn't work." [founder]

Then the doors, the deadline, the payment plan, the link (dropped by the moderator, twice, and on screen), and Q&A as objection handling. Put two or three **trial closes** before the price ("Does that make sense for where you are?", "Which door sounds like you so far?") so the room is answering before it is asked.

**If the guarantee is not signed off**, the risk-reversal steps are replaced, not invented: a damaging admission (who it is not for, what it will not do), the low-risk next step (the call is free and they can say no), and what happens in the first week. Never improvise a guarantee on air. The takeaway: who it is not for, said plainly. The last line, in the member's words, names the choice; then stop talking. "Don't talk past the close." [founder]

**Let ready buyers buy.** If someone wants to pay before the offer is presented, give them the link. The founder slowed eager buyers down by making them go through every step and called it the dumbest leak of the camp. [founder]

**Transparency at the close.** Say what the deadline is and why it is real, what the guarantee covers, and that the payment plan costs a little more and why.

## 3. Proof at the close

Only classified, consented proof (`run-the-room.md` §4). Earnings examples carry the typical result next to them or are left out. No paid-program result dressed as what the free event produced. [founder; FTC]

## 4. The cart window

**With a deadline.**
- **Length**: the deadline sets it; 3–5 days for a small list is common, 5–7 with partners [practitioner: Jeff Walker's Product Launch Formula, via summaries].
- **Mid-cart**: a live Q&A or an office hour for people deciding; the replay of the close (cut to the offer section, with both payment options and the guarantee).
- **Final day**: three emails (morning, afternoon, a few hours before), a short live session if the member can, and the deadline closes when it says it does. Plan on 35–60% of sales in the last 24–48 hours (`launch-math.md`).
- **Failed checkouts** get a personal email from the member the same day, naming what happened, with a working link.

**Without a deadline (chosen on purpose).** A replay week with the offer section, one email per segment saying what they would get and how to start, a live office hour if the member can, and a stated end of follow-up: "I'll stop asking about this after Friday", then stop. No countdowns, no "last chance".

**Call close.** Book from the chat and the application during the close (the concierge role), hold calls within 48 hours, and follow up a no-show call the same day. Calls booked, held and closed are logged like sales.

## 5. Logging

`launch_tracker.py log-close --present N --saw-price N`, then `log-sale --tier <name> --price P --count N [--payment full|plan --booked TOTAL]` for each tier, `log-calls --booked N --held N --closed N --value X` for call closes, and `log-refund` as refunds happen. Reconcile to one number: the founder's July camp had three sources reporting 12, 21 and 31 buyers. [founder]
