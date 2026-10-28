# The question map

The map is the one list of questions customers ask that the member will answer, in order. `search/questions.json` holds it; `question_map.py` keeps it; `search/question-map.md` is the readable copy. The whole skill runs off it: every answer page starts as a question here, every monthly check uses it for prompts, every hub page is a cluster from it.

## 1. Where questions come from (in this order)

1. **The Business File.** §2's verbatim language bank, pain stack and buying trigger; §3's objections and FAQ; §4's "what makes you different"; §15's objection list; §16's follow-up questions. These are the member's buyers in their own words, already collected.
2. **The member's inbox, calls and notes.** "What do people ask you before they buy? What do they ask in the first week? What did the last three enquiries ask?" The questions answered repeatedly are the top of the map. (Audience Insight, if it has run, has mined the same thing from forums and reviews.)
3. **Reviews.** The member's own and their competitors' Google and Yelp reviews: the recurring phrases, the "I wish I'd known", the objections.
4. **Google itself.** Type the service and the town with "how to", "what is", "how much", "best", "is it worth", "vs"; read People Also Ask two levels down and the autocomplete list. Google Search Console, once verified: queries with impressions and few clicks at positions 5 to 20 are the cheapest wins.
5. **Where the engines look.** Reddit and local Facebook groups: search "[service] [town]" and "is it worth"; the language there is what Perplexity and ChatGPT weigh.
6. **Free tools, a few searches a day.** AnswerThePublic, AlsoAsked and Ubersuggest each allow about three free searches a day; enough for one cluster a week. Do not buy a tool for this.

Not a source any more: Google Business Profile Q&A (removed December 2025; Gemini's "Ask Maps" answers from the profile, the website and reviews instead, and the owner cannot write its answers). The questions people used to ask there go on the website.

## 2. Rating a question (five marks, 1 to 5 each)

`question_map.py add "…" --rate d,v,g,a,f`. The marks become the founder's weights: demand 25%, value 25%, gap 20%, answerable 20%, freshness 10%.

| Mark | 1 | 3 | 5 |
|---|---|---|---|
| **Demand** | nobody has asked it | asked sometimes; appears in People Also Ask | asked every week; autocomplete finishes it |
| **Value** (to the business) | curiosity, no purchase behind it | asked by people who might buy | asked right before buying: price, "near me", "vs", "is it worth", "how do I choose" |
| **Gap** (citation gap) | the current answer already names a good page like the member's | the answer cites only directories or big national sites | the answer is thin, wrong, or cites nobody local |
| **Answerable** | the member would be guessing | can answer from good sources | can answer from their own counted jobs, numbers and photos |
| **Freshness** | the answer never changes | changes every few years | changed this year (a rule, a price, a tool) |

A question needs **answerable 60 or more** (a mark of 3 or better) to be chosen; the engines cite experience, and a guessed page fails the gate. Imported questions arrive unrated at 60 each; rate them before `next`.

## 3. Intents and clusters

Intent (`--intent`): `definition`, `how-to`, `cost`, `compare`, `objection`, `local`, `diagnostic`, `other`. The first three pages follow the founder's order: definition, how-to, then compare or objection. After that, `cost` and `compare` questions tend to carry the most buying intent; `local` questions ("do you work in …", "what does a … in [town] cost") get one honest page each, never a templated set.

Cluster (`--cluster`): the service or topic the question belongs to (`pricing`, `cash-flow`, `roof-repair`). When a cluster has three published answers it gets a **hub page**: a short page that introduces the topic and links to each answer, and that every answer links back to. The hub is usually the service page itself. `question_map.py md` says when a cluster is ready.

## 4. Duplicates, holds and retirement

- A question already in the map (same words, or the same slug) is not added twice; `add` says which ID it matches.
- `hold`: a good question the member cannot answer yet (no counted data, a rule in flux). It stays visible; `next` skips it.
- `retired`: a question that should never be answered on this site (off-topic, a never-say claim in disguise, a regulated topic the member will not cover). Listed at the bottom of the map so nobody re-adds it.
- `needs-update` is a page status, not a question status: when a published answer's facts change, the page moves to `needs-update` and the question stays `published`.

## 5. Cadence

One question a week becomes a page. The map should hold 15 to 40 rated questions; more than that is a backlog nobody reads. Once a month, add the Search Console queries at positions 5 to 20 that are not yet in the map, and retire anything that has stopped being asked.
