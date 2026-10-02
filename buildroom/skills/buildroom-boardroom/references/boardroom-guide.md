# The C-Suite Boardroom — Method Guide

Reconstructed from the Build Room session of 2026-07-01 (host Lanny Morton, AI Momentum Labs), the office hours of 07-06 and 07-20, and the 06-24 session where the board was first shown. The 07-01 transcript carries no timestamps, so quotes are cited by transcript line `[L123]`; other sessions by date and line. *(inference)* marks a reading, not a statement.

The five persona files beside this guide (`ceo-architect.md`, `cfo-scorekeeper.md`, `cmo-advocate.md`, `cso-strategist.md`, `chairperson.md`) are the founder's plugin files, unchanged. This guide is what the session taught around them.

## 1. What it is for

"It forced me to think of things that I hadn't thought of. It brought things to my awareness. I was like, oh, crap, I didn't even think of that as a possible problem, or as a possible pitfall that's coming my way, or an opportunity." [L134]

"It allows you to get out of yourself and create these other perspectives, which I think are really valuable." [L136] "Forget about the fact that it's a CMO and a CSO and a CEO. What kind of outside perspectives can you create to conspire for your good?" [L137]

The honest caveat, from the man who built it: "I don't think it's gonna work quite the same as how it worked for me, because I'm on a different type of technology, which allows more of the real-time conversation to happen, and for agents to react to each other differently, but I did the best I could at building it." [L22–24] The plugin is a decision memo with a debate in front of it, then a live cross-examination. The real-time multi-agent argument on his own system is not what ships.

The board is blunt by design. "It was hilariously good. And then a little bit painful, but good. Jeez, it nailed me." [L277–278] "Painfully accurate, and it was not sugar-coated." [L396] A member: "Ouch, they really don't hold back." [L390] Another member had Claude "put in a steward, in case the voices get sharp." [L401]

## 2. The context gate

The board is only as good as what it knows about the business. "If it was just running this process without any data or information, it would just be generic fluffy bullshit. The knowledge base comes first." [06-24 L731–732] "Generic BS and general BS is kind of worthless. When it gets really specific, it gets really good. And what I find is it gets really specific once I have that Obsidian stuff." [L116–118]

In the session, context arrived three ways: "use everything you know about my business, and you answer these" [L375]; an uploaded document ("do you have a book in a PDF format? So hit the plus button and upload it right now" [L523–525]); or pointing Cowork at the vault ("You can just point it at your brain." [L541]). The plugin itself reads no business file. In the Build Room the Business File is the board pack, and this skill reads it before the board convenes.

## 3. How the personas were built, and why that is the real lesson

"The reason I'm getting to the how was this built? Because this can be used to build anything. So I'm gonna tell you the methodology of building it, so that you can build whatever you want, whenever you want." [L40–41]

"The research behind this was, like, five world-class CEOs. Give me five world-class CMOs, five world-class CFOs, actual people. So then I researched about these people, and built that in: what made them special? How did they think? How did they process? I tried to capture as much as I could of who these people were, and then build a knowledge base that encompasses all five of them." [L36–39] "I just use the deep research functionality." [L165] "I was more focusing on their methodologies, how they made decisions, how they ran things." [L171]

The formula: "Do some research on what world class looks like in whatever that is. Add that into the knowledge base, and then create instructions that deliver the outcome that you want, and then create from there, and then test and tweak." [L140–141] "It's the same knowledge base, but you can repurpose that knowledge base multiple different ways." [L54] "These are assets that you can create on demand. You create it once, and then you can use it on demand anytime you want." [L556]

What he would do differently: "There could be an intake process before you actually create the agents. Have that brainstorming process with AI first before you go into execution mode. When I created these agents, I didn't do that." [L130–132] Research hygiene: when it matters, run the deep research "on Grok, on ChatGPT, and Claude, and then I'll compare them." [L185] "Think of it as something you have to train, and you have to tweak. It's not a perfect science by any stretch." [L126–127]

The persona files name no real people; the research was distilled into behaviour. That is why the board can be given away.

## 4. The roles, as shipped

| Role | Lens | Clashes with |
|---|---|---|
| CEO, The Architect | vision, positioning, three-to-five-year compounding; trades short-term revenue for positioning | CFO on thesis versus model; CMO when vision outruns customer readiness |
| CFO, The Scorekeeper | the actual number, cash-flow timing, unit economics, modelled downside | CEO constantly; CSO when speed outruns return math |
| CMO, The Advocate | ideal-customer perception, trust as a balance-sheet item, market readiness | CEO and CFO when the customer pays for their alignment |
| CSO, The Strategist | offensive versus reactive moves, timing windows, durability, sequencing | CFO on closing windows; CEO on visionary versus merely well-timed |
| The Chairperson | not a fifth opinion; names the decisive constraint, gives the call plus the one condition that flips it | nobody; speaks last and shortest |

No COO, no CTO, no KPIs at board level: "I didn't really think about KPIs at the C level, but obviously that would be super helpful." [L77] The founder's own system has mid-level and execution tiers under the board ("I built the C-level first, then the mid-level, the people that would take and go and execute, and then I built the execution agents, and the execution agents were tied to KPIs" [L74–75]); those tiers depend on his platform and did not ship. [07-06 L1081]

## 5. Working the room

"At the end, it says, push any executive, pit two against each other, or give me the retention number and I will reconvene. Make this an interactive thing, where you're going back and forth with this boardroom." [L279–281] Voice works: "hit the microphone and boss these guys around and tell them what you need help on." [L507]

Model: "If you want to increase the quality for this exercise, you could change it from Sonnet to a more advanced model." [L530] No API keys, no `.env`; the only cost is the member's Claude subscription.

## 6. Installing the original plugin (for members who want it outside the Build Room)

The plugin is a zip from the members' Drive. "It should run as a plugin, not a skill." [L215] Three routes were tried on the call. The drag-into-Cowork "install this" route failed for at least two members. The route that worked: **Customize → Personal Plugins + → Add → Upload Plugin → the downloaded zip** [L475–479], then `/boardroom` in any chat. The commonest mistake: pasting the Drive link into Claude instead of downloading the file. "The link was so you could download the file. That was the step you missed." [L566–567] "It's a zip file. Don't click on it, don't run it, don't do anything. Then just go hit plus, and you upload it." [L575]

In the Build Room this skill installs like every other Build Room skill and needs none of that.

## 7. Don'ts

- Don't ask the board who should be on the board. "This one already has all of these roles built in, so go ahead and ask. Pretend like you're in a boardroom right now." [L506]
- Don't run it on empty context. Check "does it already know about your book?" [L519] before trusting an answer.
- Don't expect it to execute anything. Members asked for the "minions" layer; it is not possible in this form. [07-06 L1079–1081]
- Don't trust a first run. Train it, tweak it.
- Don't manufacture consensus, ever. The friction is the product.

## 8. The member variant the founder called better

A member wrote a fourteen-question "dream team" prompt: who should be on *your* board specifically, deep research on each, persona files saved into a vault folder, wrapped in a skill. Its extras: guardrails that strip a persona's negative traits, and it picks only the advisors relevant to each question. It had no chairperson, so conflicts stayed unresolved. The founder: "I just want to acknowledge that theirs is better. Like, it really is." [L261] *(inference)* That is the personalisation step this skill offers after the first board: build the member's own advisors with the same method, and keep the chairperson.

## 9. Open questions

1. Whether the plugin should carry a business-context slot itself; this skill answers that with the Business File, the original does not.
2. KPIs or a COO at board level were asked for and not answered.
3. The founder's later platform work (agents as members of a chat workspace, "you can literally hit the mic and talk to your boardroom" [08-12 L293]) may supersede the plugin for members on that platform.
4. On 06-24 the founder called the automated version "a product" and asked members not to productise it, then shared the plugin a week later. The board is for members' own decisions, not for resale.

## 10. Quote bank

- "What kind of outside perspectives can you create to conspire for your good?" [L137]
- "The knowledge base is really kind of what makes them pretty cool and special." [L35]
- "Give me five world-class CMOs, five world-class CFOs, actual people." [L37]
- "Generic BS and general BS is kind of worthless. When it gets really specific, it gets really good." [L117]
- "Do some research on what world class looks like. Add that into the knowledge base. Create instructions that deliver the outcome that you want. Then test and tweak." [L140–141]
- "Push any executive, pit two against each other, or give me the retention number and I will reconvene." [L279]
- "These are assets that you can create on demand." [L556]
- "The knowledge base comes first." [06-24 L732]
