# From the stage to clients

The member's first goal is clients. Most stages forbid selling. Both are true, and the honest route between them is simple: be useful, offer one more useful thing with the host's permission, and follow up with the people who asked.

## 1. Ask the host, in writing, before the day
One short email, as soon as the date is booked. Record the answers with `speak_pipeline.py book --terms "…" --selling allowed|not allowed`.
- How long do I have, and is there time for questions?
- Who will be in the room, and about how many?
- May I mention a free resource at the end (a checklist, the slides) and how people can get it?
- May I leave a handout or a sign-up sheet, or stay afterwards to talk?
- Will it be recorded? May I have a copy, and may I use a short clip?
- Is there a microphone, a screen, and somewhere to stand notes?
- Anything you would rather I didn't do?

Whatever the host says is the rule. Some forbid any call to action at all, including a link to a free resource. Then the talk ends on the last takeaway and the member's name, and the follow-up comes from the conversations afterwards.

## 2. The resource
One useful thing tied to the talk: the checklist the talk taught, the worksheet, the slides. The room asks for it; nobody is added to anything they didn't ask for.
- **Lead Capture** ("Help me build my opt-in page") builds the page and the delivery. Say on the page exactly what people are signing up for.
- A printed QR code or a short link on the last slide, when the host allows it.
- A business card in a bowl isn't permission to send a newsletter. Email only the people who asked, about what they asked for.
- **The Decision Machine** ("Build my follow-up system") writes the follow-up that goes to them.

## 3. The talk itself
**Stories in place of a pitch.** On a stage that forbids selling, the member never needs to pitch. The work they do shows up inside the talk as the examples: "a roofer I worked with last spring had this exact problem, and here is what we changed." Each one is told with that client's permission, and none is dressed up. The room works out for itself what the member does for a living.

**Know the next step before the talk.** Settle, in one line, what a person who wants more is offered: the checklist, a conversation, the workshop. A speaker who hasn't decided this fumbles it when someone asks. And when someone does ask "do you also do this for…?", that is demand: note it.

The full talk, timed, with slides an older room can read and speaker notes, is the **Webinar Builder** ("Build my webinar"). Give it the talk on file and the host's rules. Two things carry over from here:
- A client story told from the stage is a testimonial. It comes from the proof bank with permission that covers `events`, word for word. If a result isn't what most clients get, say what most clients get.
- No income or results promise from the stage. "Results not typical" is no longer a defence.

## 4. On the day
- Arrive early. Test the microphone and use it, even in a small room: someone there can't hear without it.
- Notes in large type, on paper.
- Water, and the introduction printed for the host to read.
- End on time. Hosts remember that more than anything.
- Stay afterwards. The conversations are where clients come from.

## 5. Within two days
`speak_pipeline.py deliver --id … --attended N --leads N`, then:
1. **Thank the host**, in a short note (`after --thanked`).
2. **Send what was promised** to the people who asked.
3. **Ask the host for a line** the member may quote, and where it may be used (`after --testimonial-asked`). The **Proof Engine** ("Capture this win") records the words and the permission; only then can it go on the one-sheet.
4. **Ask who else should hear this talk** (`after --referral-asked`). One good talk is the best source of the next three stages. Add each as a stage with "member knows it: referred by …" as its source.
5. **Follow up the conversations**, one at a time, as the member would with any warm lead.

## 6. Count
`deliver` records how many were in the room and how many asked for the resource or a conversation. `after --clients N` records who became a client, weeks or months later. These counts are the member's own conversion figures, and the only ones worth trusting: every percentage in circulation was reported by someone selling a course. `speak_pipeline.py report` shows them and names the weakest step once there are ten pitches to judge by.

## 7. Reuse
Each talk given is also a LinkedIn post (**LinkedIn Engine**), a line of proof (**Proof Engine**), and with the host's permission a clip (**Video Director**). Offer one of these after each talk; don't do all three at once.
