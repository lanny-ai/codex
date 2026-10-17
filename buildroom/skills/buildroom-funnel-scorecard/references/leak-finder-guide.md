# The Funnel Test — Method Guide

Reconstructed from the founder's sessions of 2026-09-10 (Platinum implementation review), 2026-09-16 (Build Room weekly build), 2026-05-27, and the Build Lab sessions of 08-10 and 08-31 (host Lanny Morton, AI Momentum Labs). Timestamped sources cite [hh:mm:ss]; plain transcripts cite the line. *(inference)* marks a reading, not a statement. No members or clients are named.

## 1. What it is

The founder calls it the funnel test: a scheduled pass over every stage of the pipeline that reads the recent numbers, says where people drop off, and proposes fixes he accepts with one word.

"Every 4 hours, it's doing a conversion check of every stage of the pipeline, and looking at the data from the last 4 hours, and suggesting optimizations where the funnel is leaking as an automated task. And every 4 hours, I go, yep, those are great suggestions, do it. And it's making changes on the fly." [09-10 00:21:59]

"An engine that's gonna look for problems and suggest solutions as traffic starts to flow through the process. Run the funnel test. It's gonna go through, look at the numbers, and it's suggesting fixes based on where the leaks in the funnel are." [09-16 L330–331] "It's gonna say, hey, I see people are dropping off here and here, here's a couple ways we can fix that. And then you just hit a button, and it fixes it." [09-16 L332]

The precondition almost nobody meets: "If I lined up 100 entrepreneurs and said, show me your KPIs, step by step by step, maybe 2 or 3 could actually show me the failure rate at every step of their entire business. Not many." [09-16 L374–375] So the first job of the scorecard is to install the measurement.

A sibling run, the lead follow-up sweep: "Has every single lead been followed up with today? Looking at every single lead, where it's at in the CRM system. How many people did you move to the next stage today, and how much revenue did it create? And it's like, oh, we moved 25 people across the line." [09-10 00:21:59]

## 2. Stages are failure points

"It's first gonna establish what are these failure points of the funnel, or the process, so it's gonna establish a sales pipeline of every different failure point." [09-16 L315–316] "What's the automation required to get people unstuck at each one of these failure points? It's going to create the automation in GoHighLevel for every single failure point. And it's gonna write the emails and fill in those emails, and whatever those touches are to move people through the process." [09-16 L317–318]

That is the Decision Machine's campaign per conversion point, measured. The Funnel Map defines the stages and names the drop-off hypothesis in §6. The Decision Machine installs a campaign on each conversion point in §16. The scorecard measures each point and routes every leak to the campaign that owns it. A conversion point with no campaign is itself a finding. *(inference)*

The gates between stages are the conversion points: "The gate from 1 to 2 asks for an email address. The gate between 2 and 3 asks for a dollar. The gate between 3 and 4 is a one-click upsell." [08-10 01:26:52]

## 3. Where the numbers live, and how often to look

The founder's stack: his own app owns the user record and pushes to GoHighLevel, which does the reaching out; high-value touches go out of Gmail; revenue comes from Stripe inside the app; email engagement is measured by GHL automations. [09-10 00:26:01; 08-10 02:24:45; 05-27 L591] Ad statistics are never named as an input.

Minimum data set *(inference)*: stage counts from the CRM pipeline (or the member's app database) and revenue from the payment processor. Email opens, clicks and replies are enrichments. Access is the API first, the browser second: "I'm literally doing everything through the API. I'm not logging into anything." [08-10 02:24:45] "It needs API access, and I would also give it web browser permissions." [09-16 L398]

Cadence: "The only reason I'm doing every 4 hours is because there's literally 600,000 emails going out every day right now. If I had a slower trickle of people, I would not do it that often. But even if you did a once-a-week check-in, like, hey, check all the app users for the last 7 days, and tell me where the funnel is leaking, and then give me recommendations on how we can make it better, would be a really good recurring task." [09-10 00:36:59–00:37:11] The window analysed equals the cadence.

The rule for making it recurring: "If you catch yourself doing any single thing a second time, just stop and make it recurring. And then establish the rules for how you want it to be done. How would you, as a person, do that task? Then set it up on a recurring basis on whatever cadence you want, and set up notifications. I want notifications if something happens, because it's important, and I need to do a personal reach out." [09-10 00:28:47]

## 4. What a leak is

A leak is a drop-off between adjacent stages in the window just measured: "I see people are dropping off here and here." [09-16 L332] "Whatever your funnel is, it's gonna look at it and say, how do we optimize this based on the traffic that's gone through and the failure points? So the cool thing is everything is measured." [09-16 L373]

No numeric benchmark or ranking rule is stated. This skill ranks by revenue at risk: the drop at a stage, times the volume entering it, times the value of a conversion downstream, compared with the prior window. Industry benchmarks are a secondary flag at most. *(inference)*

"Establish your KPI of what's important, but don't box it in on how it increases the value of the KPI, because it might come up with something you haven't thought of." [09-10 00:26:01] Fix categories he names: "Maybe some UX things, maybe it's training, maybe it's messaging." [09-10 00:26:01]

## 5. Propose, then approve

"It's gonna suggest fixes, and if you want it, you press a button, and it's gonna do those fixes. And you don't have to take the fixes either, or you can change those fixes." [09-16 L375–376] "I am double-checking it, but I'm not doing any of it." [08-10 02:24:45]

Fixes never touch the live account directly: "It's gonna be a snapshot that goes in, so it doesn't touch anything, and then when it does touch things, it's just touching that snapshot. It has a gate around that particular thing." [09-16 L369–371]

The feedback rule: "You don't change the emails, you give it feedback and have it change the emails every single time, because it learns every single time you do that." [09-10 00:14:47] "Don't just accept something that isn't up to the standard of what you want. Next time you run this process, please XYZ." [09-10 00:14:47] "Don't leave AI blind." [09-10 00:19:17]

## 6. Tooling

A recurring task in Codex or Claude Code, not a chat: "Their ability to do recurring tasks like that, and to do them really, really well, is mind-blowing." [09-10 00:14:47] "You might not even need the command center. Tell it, hey, I have this workflow that sucks, and I sure would like to automate it." [09-10 00:10:37] Frontier model for this task ("you definitely want to use the latest model on those tasks" [09-10 00:14:47]), the cheap model for grunt work.

Fail loud. The founder's own vault records the lesson: a scheduled job that stops running is invisible unless something checks that it ran. The routine reports what it couldn't read at the top of every run and alerts on a missed or empty run.

## 7. Don'ts

- Don't run it every four hours on a trickle. Weekly, and the window equals the cadence.
- Don't hand-edit the outputs. Give feedback so the next run improves.
- Don't box in how the KPI gets improved.
- Don't let fixes touch the live account. Gate them to a snapshot; approve each one.
- Don't ship an AI-built automation unchecked. His own miss: an AI-built registration page made a three-day event look like pick-one-day. "Sometimes this automation, you should double-check it. I should have double-checked that." [09-16 L404–405] The workaround: "I'll give the link to AI. Here, go test this for me, and then tell me what's broken." [09-16 L409]
- Don't estimate a number. A stage you can't read stays blank and flagged.
- Don't make the member build tracking by hand: the first finding of a scorecard with no stage counts is "install the pipeline stages", and the skill writes the exact stages to create.

## 8. Open questions

- The founder never states a leak threshold or a ranking rule; this skill's revenue-at-risk ranking is a design choice, labelled as such in every output.
- Whether email engagement and ad spend belong in the scorecard depends on the member's funnel; the skill offers them as enrichments after the stage table exists.
- The founder's version lives partly inside his own app. The member version is a recurring task reading the CRM through its API, with the browser as fallback.

## 9. Quote bank

- "Every 4 hours, I go, yep, those are great suggestions, do it." [09-10 00:21:59]
- "Check all the app users for the last 7 days, and tell me where the funnel is leaking." [09-10 00:37:11]
- "Maybe 2 or 3 could actually show me the failure rate at every step of their entire business. Not many." [09-16 L375]
- "A sales pipeline of every different failure point." [09-16 L316]
- "How many people did you move to the next stage today, and how much revenue did it create?" [09-10 00:21:59]
- "If you catch yourself doing any single thing a second time, just stop and make it recurring." [09-10 00:28:47]
- "Don't box it in on how it increases the value of the KPI." [09-10 00:26:01]
- "You give it feedback and have it change the emails every single time." [09-10 00:14:47]
- "It has a gate around that particular thing." [09-16 L371]
- "Here, go test this for me, and then tell me what's broken." [09-16 L409]
