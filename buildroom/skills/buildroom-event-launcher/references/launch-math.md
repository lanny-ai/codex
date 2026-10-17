# Launch math: from the goal back to the list

Work backwards from the goal before choosing anything else. The math is the honest conversation: it shows whether the list can carry the goal, and which single number matters most.

`python3 <skill>/scripts/launch_plan.py math --price P (or --tiers …) --goal-buyers N and/or --goal-cash X --list-size L --format bootcamp3|challenge5|workshop|webinar [--close checkout|call|both] [--paid-event] [--history-… R]` prints the typical path, how far each single stage could move it, the verdict against the goal, and the biggest lever. `launch_plan.py --help` lists the history flags; from the second launch on, use the member's own rates. Every constant it uses names its source.

## The chain

List → registrants → live on Day 1 → each following day → present at the close → saw the price → buyers.

| Step | Planning range | Source and strength |
|---|---|---|
| List → registrants | **No published benchmark.** Use the member's own history. Otherwise: warm, engaged list 10–30% (a Build Room assumption, said as one); a large cold or partner list far lower (a large partner-sent list registers well under 1% in the founder's experience) | Assumption; founder's run |
| Registration page conversion (visitors → registrants) | Warm traffic 35–50%, cold or social 15–30% | [data: ON24 25–30%, vendor, B2B; practitioner: Scale For Impact target about 40%] |
| Registrants → live Day 1 | Free event to a warm list 30–45%; free challenge 15–35%; paid $27–$97 event 50–70% | Derived from [data: Livestorm 51%, Univid 49%, Goldcast 33%, vendors; practitioner: Scale For Impact about 25% for creator funnels]; founder July 2026: 39% |
| Day-over-day retention | 50–80% of the previous day | [founder: rule of thumb about 80%; July 2026 measured 68% then 52%]; [practitioner: HSH 51.8% Day 1 → Day 5] |
| Saw the price | Those present at the close; the people reached later by the replay and cart emails are added only if the member sets an uplift from their own history | Member history |
| Present at the close | The final day's live count, minus those who leave before the offer (plan on half to two-thirds staying to the end) | [founder: 133 live on Day 3, 67 at the very end] |
| Buyers | Of those who **saw the price** (live at the close, plus those reached by the replay and cart emails): $97–497 8–15%; $500–1,500 5–10%; $2,000+ 1–4% (then sold on calls). Each door is modelled at its own price | [practitioner: Scale For Impact, 114 webinars, measured on webinar attendees, the closest available base] |
| Calls (call close) | About 10–20% of attendees book; plan on most booked calls being held; 10–25% of held calls close | [data: vendor and agency figures, weak; held-rate is a Build Room assumption] |
| Buyers as a share of the list | 1–2% normal, about 5% strong | [practitioner: Denise Duffield-Thomas; Nicola Moors] |
| VIP or upgrade (multi-day events) | 4–15% of registrants | [practitioner: Brunson secondhand 3.84%; Scale For Impact model] |
| Share of sales in the final 24–48 hours | 35–60% | [practitioner: Denise Duffield-Thomas 40% in final two days; McWilliams 40–60% affiliate sales last day] |

## The founder's July 2026 run, as one data point

A free 3-day boot camp, a $1 personalised brief, then a core program: 969 registered; 380 / 257 / 133 live on Days 1–3; 67 at the very end; 102 bought the $1 brief; 21 of those bought the program; in his follow-up analysis, 23 of the 41 people known to have seen the price bought (56%), while 51 brief buyers never saw it. [founder: his audit and follow-up analysis] Use it as one real example of the shape, not a promise: his list came through a large partner, and the format and offer were his.

## Reading the result with the member

- **Show the typical path and the gap to the goal**: what the list should give, what the goal needs, and how far each single stage could move it (its cautious and strong value with everything else typical). "Typical" is not a forecast; it is the middle of published ranges. The verdict: the typical path reaches the goal (reachable), 60–99% of it (stretch), or under 60% (not from this list alone).
- **Name the biggest lever.** The script names the stage where moving from typical to strong adds the most buyers, leaving out stages that rest only on an assumption. In practice it is often show-up or conversion; the founder's July show-up was 39% against a 65% target, and 51 people paid $1 and never saw the offer. The member's own history sharpens it from the second launch.
- **If the goal is out of reach from this list**, say it in one sentence and offer four choices: lower the goal, add partners (`launch-partners.md`), add ads (Ad Studio), or a longer runway with list building first.
- **Service businesses selling on calls:** the conversion event is a booked call. Track calls booked, held and closed separately; about 10–20% of attendees booking and 10–25% closing are vendor and agency figures, weak [data: vendors].
- **Refunds and chargebacks** belong in the plan: there is no reliable refund benchmark; card networks flag US merchants at about a 1.5% dispute ratio (Visa from April 2026). A clear guarantee honoured fast is the protection.

## After the event

`launch_tracker.py report` compares every step to the plan, ranks the three biggest shortfalls, and prints the member's own rates. From the second launch on, the member's history replaces the published ranges (`--history-reg-rate`, `--history-showup`).
