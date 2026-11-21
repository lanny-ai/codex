# Today's post: research, write, picture, on the daily page

_Added 2026-11-21._

On a posting day the member's daily page starts with a card for the post: the words to copy, the picture to save, the alt text, and a tick. This file is how that card gets made. Everything in `content-system.md` still applies (the pillars, voice first, the archetypes, the post gate), and `account-safety.md` applies in full: the member publishes every post by hand.

## How often

The member chooses when they set up: three, five or seven posts a week. `li_pipeline.py settings --posts-per-week 3|5|7` stores it, and `li_pipeline.py today` says whether today is a posting day (three: Tuesday to Thursday; five: Monday to Friday; seven: every day).

**Three is the default, and say why.** The evidence in `linkedin-principles.md` is that most of the gain comes between two and five posts a week, and a busy owner can keep three up for a year from their own material. Five or seven only works for a member with a full story bank. If the bank runs low, say so and go back to three; a thin post is worse than no post. Never fill a day with a generic one.

## 1. Research: a reason for the post to exist today

Research finds the hook. It never supplies the substance; that is the member's own story, fact or opinion.

1. **Start from the member.** Read the pillars, the story bank and the calendar. Pick today's pillar and an unused story or view. No story used twice within four weeks.
2. **Look for something timely,** where you can reach the web: a new rule or deadline in their field, a study or report published in the last 30 days, a question their clients are asking this week, a seasonal moment in their trade. Prefer the primary source (the regulator, the journal, the body that published it) over a blog about it.
3. **Keep the link and the date.** Record the source's title and full address. The member is told to check it before posting.
4. **A figure needs its source or it is the member's own.** No statistic from memory, no "studies show". If the source cannot be found, the figure does not go in.
5. **Without web access,** say so once and build the post from the story bank and the idea matrix alone. That is a complete post; most good ones need no news.
6. **Stay inside the pillars.** A trending topic that is not the member's subject teaches the feed the wrong thing.

## 2. Write it

Follow `content-system.md` §6 and run the post gate in §8. In short:

- The member's voice, from their own words. Capture first (ask them for two minutes of talking about it) when the story bank has only a headline.
- The topic is clear in the first 140 characters. A whole idea, usually 1,300 to 2,500 characters.
- The timely hook is one or two sentences. The rest is what the member has seen, done or thinks.
- No engagement bait, no result promised, nothing the member refuses to claim, no client's words or results without recorded permission, no retired line.
- At most one link, usually none. If a link matters, put it in the first comment and give that as `first_comment`.

## 3. The picture

- **The default is a rendered card or carousel in the member's own brand** (`render_linkedin.mjs`, layouts `card` and `carousel`). Set `"brand"` in the spec to the path of their locked kit, `Design/System/tokens.json`: the logo, colors and typefaces all come from it, and nothing is typed in by hand. `"ground": "reverse"` gives the same card on the kit's dark (or light) ground, so a week of posts varies without leaving the brand. The words on the card come from the post. Mark the one to three words that carry the headline with asterisks (`"Production is *not* profit."`) and they take the accent color. Keep the headline short enough to read in one glance: ten words is plenty.
- **The card is flat and typographic on purpose:** the logo, one headline, a hairline and a byline. No glows, gradients, pills, badges or decorative shapes, and never an attempt to make it "pop" with effects. Those are what make an image look machine-made, and that costs the member trust. If a card looks plain, the fix is a better headline or a real photo, not decoration.
- **No brand kit yet (§22 empty)?** Say so once: "Your images will look far more like you with a brand kit. It takes about fifteen minutes. Say: set up my brand kit." If they want the post today, spell the brand out in the spec from what the Business File holds and say the image is a stand-in.
- **A real photo** of the member or their work is better still when they have one. Ask.
- **An AI-made picture is optional,** only when the member asks for one and already has an image-generation account: write the prompt, show them the price, and run it through `scripts/gen.py` with its spend ledger (`provider-signup.md` covers the account). Mark the post `"ai_image": true`. Rules for these: never a picture of a real person, a client, or the member themselves; never something presented as a real photo of real work; never a logo or brand that is not theirs. LinkedIn labels AI images and readers can flag them; say so, and never remove the label.
- **No stock photos.**
- **Every picture gets alt text:** what it shows, in a sentence.

A post with no picture is fine. A text-only post is a normal LinkedIn post.

## 4. Put it on the daily page

Add the post as the first item in `linkedin/today.json`:

```json
{"do": "post", "name": "Today's post", "url": "https://www.linkedin.com/feed/",
 "based_on": "the member's own story or view this post is built on",
 "source": {"title": "where the timely fact came from", "url": "https://..."},
 "own_numbers": false,
 "text": "the post",
 "image": "renders/post-1124.png", "alt": "what the image shows", "ai_image": false,
 "first_comment": "optional"}
```

Then `li_today.py build linkedin/today.json linkedin/Today.html --pipeline linkedin/pipeline.json`. It refuses the page while the post has no stated basis in the member's own material, carries a figure with no source (unless every figure is the member's own), uses engagement bait or machine-sounding filler, promises a result, has more than one link, is too short or too long, or names a picture that is missing or has no alt text. One post a day at most.

The check reads for patterns. It does not judge whether the post is true, interesting or theirs. The member reads it and edits it before posting, every time.

## 5. After it is up

The member pastes the link. `li_pipeline.py log-post --url <link> --pillar "<pillar>" --format image|carousel|text` records it and marks the calendar. Remind them of the one thing that matters most in the first hour: stay and answer every comment with a real reply or a question.

## Rules

- The member's own material is the post. Research is the hook.
- A source for every figure that is not theirs, with its link, checked by the member.
- The member publishes by hand. Nothing here posts or schedules.
- An AI picture is the member's choice, at their cost, labelled, and never of a real person.
- Nothing here promises reach, followers, leads or clients.
