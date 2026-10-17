# Filling the event and getting people to show up

Every email here is drafted one at a time through Kern (`kern-framework.md`), in the member's voice, approved before the next. Every email names who teaches live. Nothing in this file is a script to paste; each is a job an email does, with the founder's rules for doing it.

## 1. The one belief, before any invite

Write one sentence the buyer must believe for the offer to be the obvious next step. Under it, three supporting beliefs, each replacing a false one [founder; "big domino" and false-belief replacement are Russell Brunson's terms]:
1. **Opportunity**: this matters now, and it is real.
2. **Identity**: it works for someone like me (age, background, skill, time).
3. **Mechanism**: this way of doing it is doable, and I can see the first step.

The order is deliberate: "want it, then qualify yourself in, then believe it is doable." [founder] Write them in the buyer's words from §2. "Sell the freedom, not the technology. The moment it smells like homework, we lose them." [founder]

**The belief emails (three, a day apart).** One per supporting belief, each with a story or a concrete example, no offer, one easy reply prompt at the end ("Hit reply and tell me which one you are") so readers sort themselves by temperature and objection. [founder]

## 2. The invitation sequence

A pre-frame first, then invitations: "Do not lead with the register link. Earn the click with the pre-frame." [founder]

**The default sequence** (send dates from `launch_plan.py timeline`, counted back from Day 1):
- Days −21 to −19: three belief emails, one a day.
- Days −18 to −15: the first-win tool, two or three emails whose only call to action is the free tool.
- Day −16: the launch gate passes (before any invitation).
- Days −14 to −1: the invitations, five for a small list (jobs 1, 2, 4, 5, 7 below) or seven for a large one, every other day, then daily in the last three days.
- Then the confirmation, the reminders (§4) and the night-after emails.
The founder's July 2026 camp ran 7 value emails pointing to the free tool, then 7 invitations, then event-day emails [founder]; the default is a smaller version of the same shape.

**The jobs, in order:**
- **The first-win tool first**, if there is one: the only call to action is the free tool; the event is mentioned at the end of the run.
- **Invitation emails**, a day apart, each doing one job:
  1. What happens on each day, and what they walk out with.
  2. One proof story, classified and consented, in the person's own words with an honest qualifier. If no consented story exists, the host's own story with a damaging admission.
  3. The repeat-attendee objection ("You may have seen me run this before").
  4. The time objection ("Three days is a lot"), with what each day gives them.
  5. Who it is for and who it is not for.
  6. The fence-sitter: one plain reason to come.
  7. The last word.
- **Every call to action is the same: save the free seat, then show up live.** "One decision, repeated." [founder]
- **Tease the offer only**: "at the end, I'll make an offer for those who want to go further with me." Answer "why is it free" honestly. [founder]
- **No replay promises in the invitation.** "The replay watchers mean well, and most of them never press play." [founder]

**Segments.** Hot (past buyers, recent replies, engaged) get a personal note from the member for the top few; warm get the full sequence; cold get value-only emails first with engagement scoring and only then the invitation. Send from a warmed subdomain, ramp volume, and drop the unengaged before the launch. [founder; bulk-sender rules]

**Registration form.** First name and email; one to three questions only if each changes the follow-up (the problem, their stage). "If you ask for first name, last name, email, country, mobile phone, a checkbox… nobody's gonna fill that out." [founder] SMS consent is a separate, unchecked, optional box.

## 3. The confirmation

Immediately after registering: the join link, an add-to-calendar button for every day (`event_ics.py build` writes the `.ics` and prints Google and Outlook links), a time-zone table (Pacific, Mountain, Central, Eastern, London, plus a converter link), and **one** pre-work action: finish the first-win tool, with its real duration. [founder] The thank-you page says the same and offers the VIP tier if there is one.

A calendar file cannot carry a per-person join link; if the link is per-person, the `.ics` carries the registration page and the emails carry the link. Use UTC times for one-off sessions; test the file in Google, Outlook and Apple calendars on a phone. [rules research]

## 4. Show-up engineering

| When | What | Channel |
|---|---|---|
| Between registering and Day 1 | Pre-work nudges: the first-win tool; one short "how to prepare" | Email |
| Day before | "How to prepare": be at a computer, not a phone; come ready to do it; the time in their zone | Email |
| Morning of each day | "Today is the day", the join link, today's promise | Email |
| 15 minutes before | "15 minutes", the link | Email; SMS only with consent |
| Live now | "We're live", the link | Email; SMS only with consent |
| **Night after each day except the last** | What happened today, tomorrow's promise, "tomorrow is the one" before the final day | Email |
| Morning of the close | The day's promise and the reminder that the offer is today | Email |

`event_ics.py reminders --spec event.json --recipient-tz <zones>` prints the schedule in local and UTC time and flags any text outside 8 a.m.–9 p.m. in a recipient's zone. The founder's July camp missed the night-after emails and had reminders fire about four hours early on two days; both are gate items. [founder]

**A reason to come live that does not gate the content.** Live building, personalised help, being named, the timed challenge, the live close bonus. His live-only access code "just created friction" and he removed it on air. [founder]

**Reward people for showing up.** Read out, by first name with permission, the people who did the pre-work or came back; on the last day, acknowledge the people still there. [founder]

## 5. Partners and other channels

Partners' emails go through the same rules: they name who teaches live, disclose their commission, and carry the same promise (`launch-partners.md`). Who sends, from which account, on which dates, is written down; the founder's July sending sat with a partner's team and he could not fix the reminders himself. [founder]

LinkedIn posts go through the LinkedIn Engine; ads through the Ad Studio; a short invitation video through the Video Director.

## 6. Logging the fill

Log registrations daily by source (`launch_tracker.py log-reg N --source email:<id>|segment:<name>|partner:<name>|ads|social`), so the debrief can say which email filled the room. `launch_tracker.py pace` compares registrations to date with what the list should give by now (registrations bunch up late: about half arrive in the final week and about one in seven on the day itself [data: Livestorm, vendor]). If behind at the halfway point, change one thing (a personal send to the hottest segment, a partner's second mailing, a new subject line), not five.
