# The intake

Seventeen questions, the ones the original Gig Getter asked, in its order. The quality of everything after depends on these answers, so let the member talk.

## How to run it: draft from the file first
The member has already told Build Room OS most of this. Don't make them say it again.

1. **`speak_pipeline.py prefill`.** It reads the Business File and returns two lists: the questions the file can answer, each with the text of the sections to draft from, and the questions only the member can answer. It also returns the sections the talks, bio, one-sheet and pitches are drafted from, and which sections are provisional or missing.
2. **Draft every answer the file supports**, in the member's own words, from that text only. Record each as a draft: `speak_pipeline.py answer --key audience --text-file a.txt --from "§2" --draft`. Use a file or single quotes; inside double quotes the shell eats dollar amounts.
3. **Draft the rest of the kit the same way before asking anything:** one to three talks (`talks.md`), the bio and the one-sheet (`one-sheet-and-bio.md`). Where the file is thin, leave the gap and note the question. Never fill it.
4. **Show the member one summary**: "Here is what I drafted from your Business File. Tell me what is wrong." Put the drafted answers, the talk titles and promises, and the bio on one screen, each with the section it came from. Fix what they correct. A provisional section is said aloud: "your avatar is still provisional, so this is too."
5. **`speak_pipeline.py confirm --all --by member`** (or `--keys a,b`). Nothing drafted is used until the member has confirmed it; `ready` refuses while a draft is unconfirmed.
6. **Then ask only what the file can't know**, one at a time, with the helper line. Usually eight questions: experience, formats, paid or unpaid, room size, virtual or in person, where they have spoken, any target event, availability. The member can say "skip". Ask them to speak their answers if they can; people say far more than they type, and the detail makes the stages fit.
7. **`speak_pipeline.py ready`** when the core four are in (expertise, audience, goal, topics) and there is a place to look.

With no Business File, or a nearly empty one, ask all seventeen in order and recommend the Ideal Client Avatar session first.

## The questions
| Key | Question | Helper | Often already in |
|---|---|---|---|
| `expertise` | What is your area of expertise? | The thing people already come to you for. | §1, §3 |
| `audience` | Who is your ideal audience? | The people who become your clients. | §2 |
| `experience` | How much speaking have you done? | A toast, a class, a team meeting all count. | |
| `goal` | What do you most want from speaking? | Clients, visibility, authority, a fee, or to share what you know. Pick the first. | §1 |
| `reach` | Local, national or international? | Local first is the fastest start. | |
| `formats` | Which formats are you comfortable with? | Talk, workshop, panel, guest webinar, podcast guest, Q&A. | |
| `credentials` | What certifications, results or recognition do you have? | Only what is true and you could show. | §18, §17 |
| `hosts` | What kind of hosts do you want? | Local groups, associations, conferences, companies, podcasts, online summits. | |
| `paid` | Paid, unpaid, or both? | Unpaid stages in front of your buyers often bring more than a fee. | |
| `size` | What size of room suits you? | Up to 50, 50 to 200, more than 200. | |
| `regions` | Which regions or cities should we look in? | Towns you can drive to, plus anywhere you travel anyway. | §1 |
| `mode` | Virtual, in person, or both? | | |
| `platforms` | Where are you active online? | Hosts look. | §14 |
| `topics` | What would you speak about? | One to three talks, or "need help with topics". | §3, §4 |
| `history` | Where have you spoken before? | "Nowhere yet" is a fine answer. | |
| `targets` | Is there a specific event or group you want to get into? | Name it, or say no. | |
| `availability` | When can you speak, and when can't you? | Days, months, travel, health or family limits. All private. | |

## Reading the answers
- **"Need help with topics"** goes to `talks.md` before any stage is looked for.
- **Goal is clients:** rank stages by whether the member's buyers are in the room. Goal is a fee: say plainly that paid stages mostly go to speakers with a record, and that a few unpaid talks to the right rooms are how the record is made.
- **Beginner, or "nowhere yet":** start with one warm stage the member can drive to: a group they belong to, a client's team, a library. Offer a practice group such as Toastmasters; it is for practice, not for bookings.
- **A named target event:** find its speaker page and its deadline first. If the call has closed, put next year's on the calendar.
- **Credentials thin:** years in the work and one true client story are enough for a local stage. Never pad.
- **Availability and health limits** shape the plan quietly. A member who can't drive at night gets lunch meetings.
