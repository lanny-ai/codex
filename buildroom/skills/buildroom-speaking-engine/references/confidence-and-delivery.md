# Confidence and delivery

Most members have never given a talk to strangers, and many are nervous about it. That is normal and it isn't a reason to wait. This file is the practical routine. The full talk, with slides and a rehearsal scorecard, is the **Webinar Builder**.

## Ask two questions, kindly
1. Do you get nervous before speaking?
2. From 1 to 10, how confident do you feel about giving this talk? (Recorded later with `debrief --confidence`, so the member can see it move.)

Don't diagnose and don't promise the nerves will go. Say what is true: almost everyone is nervous, the room is on the speaker's side, and preparation is what helps.

## What helps, in order of how much
1. **Say it aloud, standing, timed.** Three times before the day. A talk that has only been read silently will run long and feel strange in the mouth.
2. **Know the first two minutes by heart.** Nerves are worst at the start. After two minutes the member is simply talking about work they know.
3. **One story they have told before.** A client situation, with permission, or their own. Stories steady the speaker and are what the room remembers.
4. **Notes in large type**, a few words per point, on paper. Not a script to read.
5. **See the room first.** Arrive early, stand where they will stand, test the microphone, and talk to two people as they come in. Then the talk is to people they have met.
6. **Slow down.** Nervous speakers rush. A pause feels long to the speaker and normal to the room.
7. **Picture it going well, as a rehearsal.** Walk through the opening, the story and the close in the mind's eye, the same way each time. It is practice, not magic.
8. **A sentence to say to themselves** before starting, in their own words, that is true: "I know this, and these people can use it."
9. **Breathe out slowly** before standing up.

For a first talk, suggest a warm room: a group the member belongs to, or a client's team. A local practice club such as Toastmasters is a fine place to get repetitions.

## For an older first-time speaker
Experience is the asset: decades in the work is what a younger speaker can't offer. The practical points are the same for everyone: use the microphone even in a small room, have notes large enough to read without glasses, have water, and ask for a chair or a stool if standing for 45 minutes is hard. Nobody minds.

## For the room
- Use the microphone. Someone there can't hear without it.
- Slides in large type, strong contrast, few words. Say aloud what is on them.
- Repeat a question from the floor before answering it.

## After each talk
`speak_pipeline.py debrief --id … --well "…" --improve "…" --reaction "…" --confidence N`. Three questions, in the member's own words:
1. How did the room react? (Questions afterwards and people staying to talk are the signs that matter.)
2. What went well?
3. What is the one thing to change next time?

One change, not five. `today` reads it back before the next booked date, and `report` shows it.
