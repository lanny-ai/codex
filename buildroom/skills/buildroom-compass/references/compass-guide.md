# The Compass — Method Guide

Reconstructed from the Build Room session of 2026-07-22 (the live test of the Compass web app, host Lanny Morton, AI Momentum Labs) and the sessions where the Compass is explained (the February 2026 bootcamp, 03-11, 04-15, 06-01, 07-08, 07-20, 07-27, 08-05, 08-10, 08-14, 09-16). Zoom transcripts carry no timestamps, so quotes cite date and line, for example [07-27 L114]; knowledge notes cite a timestamp. *(inference)* marks a reading, not a statement.

## 1. What the Compass is

A personal clarity document, not a product spec. "I wanted a tool where I could have a document, and from that document, I could drop that document into any AI thread, and ask myself the question, is this the right situation for me?" [07-27 L114] "The Compass was designed to be like, who am I at a really, really deep level. Like, what's really, really important to me?" [07-27 L130–131] "It's like, who are you? What matters to you? It's values, it's spark zone, drain zone, it's personality type, it's a bunch of different modalities of who you are." [08-14 L398–399]

Its fields, as the founder read them off his own Compass: "Core values and beliefs, life philosophy and mission statement, personality snapshot, zone of genius, energy map, spark zone, drain zone, goals, motivations, short-term, long-term vision, core motivational driver." [02-23] The full document adds hidden opportunities, blind spots, a unique truth, an alignment analysis, and closes with the Compass Statement: "You thrive when you honor your values of [X], lead with your natural [pattern], stay in your Spark Zone of [Y], and pursue [Hidden Opportunity]. Avoid [Drain Zone]. Your compass points toward [Core Vision]."

Size and effort: "A couple pages at most. Page and a half. There's twenty pages to get there." [03-11] About nineteen questions, thirty to forty-five minutes [08-05 L205–214]. "Garbage in, garbage out." [07-22 L527] "If the compass statement isn't amazing, the whole process is dead." [08-05 L220]

Naming: the tool was the Navigator, renamed "like four times"; the output is the Compass. "Magic Wand" was a short-lived rebrand: "ignore the magic wand thing." [04-15 00:08:28]

## 2. How the interview runs

The founder's own system prompt for the Compass sets the rules the skill keeps:

- One question at a time. "You should never ask more than one question at a time, it doesn't work." [07-22 L386]
- Reflect before advancing: acknowledge what was said before the next question. That reflection is why the process lands: "a really deep reservoir of a great knowledge base" and a validating reflection after every answer [07-27 L124].
- Adapt: the questions are frameworks, not scripts. Follow the emotional thread.
- Reveal an insight after each section, not during. Make it specific to what the person said.
- No jargon, ever. The frameworks run silently; the person should feel understood, not studied.
- Not "newbie-centric" is a failure: plain words, a microphone if the tool has one.

Five sections, then the reveal: Core Values and Identity (five to eight questions: what they refuse to compromise on, their philosophy in a sentence, how people who know them describe them at their best, what they want said at the end); Energy Mapping (three to five: what makes them feel most alive, what drains them even when they're good at it, when they lose track of time); Personality Discovery (five to seven: instinct or analysis, take charge or build enthusiasm or keep harmony or ensure quality, results or relationships or structure, response to sudden change, feedback straight or diplomatic); Goals and Direction (three to five: the next twelve months, five to ten years across work, relationships, health, fulfilment, what keeps them moving, what they'd do with money, time and fear removed); Alignment and Reflection (two to three: where they feel aligned and where there's friction, the advice they'd give their younger self).

The reveal is a narrative, not a list, covering values, philosophy, personality pattern, zone of genius, spark and drain zones, motivational core, hidden opportunities, blind spots, the unique truth, and the statement. "After delivering the Compass, pause and let the person respond. This is the emotional peak."

## 3. What comes after it

The founder's flow: "Phase 1 is the Compass document, Phase 2 is the blueprint, Phase 3 is the build plan, and Phase 4 is you build it." [07-20 L626] "The first stage is the Compass, which is who am I, and what is my North Star? The second phase was the Blueprint. What should my business execute? The third phase was build brief. What exact product should I build?" [08-05 L390–391]

The Blueprint opens with three paths, "launch, expand, or leverage" [08-05 L419], and produces a strategic direction, a business model, and a 30/90-day plan. By September the founder had replaced it: "Phase 1 Compass is exactly the same. Phase 2 is normally the Blueprint. I took that out, and I changed that to a Discover and Design step." [09-16 L258–260] Does the Blueprint need the Compass? "Not necessarily. It could go right to a Blueprint. I think that this without this creates emotion, more than this does." [08-14 L395–402]

In the Build Room, the Blueprint's content already has homes: its business model is §2 Avatar, §3 Offer and §4 Positioning; its 30/90-day plan is §13 Build Plan; the build brief is a §13 row with a goal statement. So this skill produces the Compass, writes it to §17, and then points the compass at the sequences instead of writing a second plan. *(inference)*

## 4. Where the Compass gets used

"The Compass is something everybody should have on a Google Doc somewhere, where you can drop it in anywhere you want. Because that thing is the essence of what drains you, what sparks you, who you are, and that's relevant in anything." [08-10 L1510]

- In any AI thread: "is this right for me?" [07-27 L114]
- In the Decision Machine's intake: "the Compass tells Claude exactly how this person communicates; the SOS emails now sound like them." [04-15 00:08:28] Email voice and tone come from the personality snapshot and spark zone; belief targets from the blind spots and resistance patterns.
- In the first context step of any Codex build: "I'd put your Compass statement in there, for sure." [08-10 L430]
- In a high-reasoning brainstorm when a project doesn't spark. [08-10 L1153]
- Redo it when circumstances change. [06-01 00:35:07] Old custom-GPT Compasses "will not translate, so you have to redo it." [09-16 L256]

In the Build Room, §17 is that Google Doc: every skill that wants voice, energy constraints, or a fit filter reads it there.

## 5. The 07-22 live test, in brief

The web app ran Sonnet on the questions and the strongest models on the two outputs that matter: "There's two steps that really, really matter, as far as model goes. One step is the Compass statement, and the other one is the Blueprint." [07-22 L102] The founder fixed the Phase 3 screen live because it asked six questions at once with no microphone; the rebuilt version asked one question at a time with a microphone on every open answer. Members then dragged the build pack into Codex and pressed "Pursue Goal"; the first tester's app came back "Built and verified" and four more were building by the close. One 41-minute build produced the wrong app: the remedy the founder gave is the one this skill uses for any build, "start with brainstorming the idea before you start coding. Ask Codex, I want you to create the goal statement of what's going to be done, make sure you're okay with what the goal is, then cut it loose." [07-22 L2006–2008] "It was more important to me that you did build something." [07-22 L2126]

## 6. Failure modes

- Shallow answers give a generic Compass. The founder redid his own "as if I was a new person" and rejected outputs "closer to ten times." [07-22 L204–206]
- A cheap model on the statement: "it just sucked." [08-05 L248] The interview can run light; the synthesis needs the strong model.
- Long threads lose the statement; in the custom-GPT era 75 of 351 attendees "bit the dust" at the copy-paste step [02-23]. In the Build Room the statement goes into §17 the moment it exists.
- Multi-question forms with no microphone stall non-technical members.
- A vague build brief builds the wrong thing; the goal statement comes first.

## 7. Open questions

- Whether the web app's PDF carries hidden opportunities, blind spots, unique truth and alignment analysis; the founder's February read-out did not list them. This skill produces all of them.
- The founder's preference is a standalone Compass document. §17 holds the compact form and links to the full document; the full text stays the member's own file.
- Whether the Build Room OS should follow the July flow or the September Discover-and-Design variant. This skill follows September: Compass, then route.

## 8. Quote bank

- "Who am I at a really, really deep level. What's really, really important to me?" [07-27 L130]
- "Drop that document into any AI thread, and ask myself the question, is this the right situation for me?" [07-27 L114]
- "If the compass statement isn't amazing, the whole process is dead." [08-05 L220]
- "You should never ask more than one question at a time, it doesn't work." [07-22 L386]
- "The Compass tells Claude exactly how this person communicates." [04-15]
- "Something everybody should have on a Google Doc somewhere, where you can drop it in anywhere you want." [08-10 L1510]
- "Start with brainstorming the idea before you start coding." [07-22 L2006]
- "It was more important to me that you did build something." [07-22 L2126]
