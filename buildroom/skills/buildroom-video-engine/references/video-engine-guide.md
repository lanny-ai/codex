# Build Room Video Engine — Method Guide

Reconstructed from the Build Room session of 2026-05-20 (host Lanny Morton, AI Momentum Labs). Quotations are Lanny's words from that session, with timestamps. Anything marked *(inference)* is a reading of the transcript, not a statement in it.

The Video Engine is a Claude Code project, shipped as a zip, that bolts an automated production line onto the Build Room Content Creation Pack: research → script → avatar video → B-roll and stills → composite → captions → a finished MP4 in a folder on the member's computer. Posting stays manual.

> "this process from start to finish was completely automated. the only thing I did was set up the automation. So, I didn't write the script, I didn't do the video, I didn't do the editing, I didn't do the captioning, I didn't do anything." [00:17:45]

## 1. What it is for, and what it is really teaching

The problem: scripts nobody records. "If I looked at my LinkedIn daily posts automation… it's been doing it for months. Guess how many I've actually done? Zero. None." [00:47:40] The engine removes the human recording step.

The real lesson, said three ways:

- "whether you're going to use this process or not is kind of irrelevant… because the skill set of doing it is really, really powerful." [00:44:43]
- "that was the real lesson today… API integrations. Forget that it's content, forget that it's HeyGen… The real big takeaway is using Claude Code" [01:22:52]
- "It's not about videos, and it's not about content creation… It's about using Cloud Code and the APIs to just make your life so much easier." [02:06:52]

And the honest gate: "I'm not selling you on this… If this money makes a difference for you… please don't do this." [00:23:22] "80-90% of your activity in life should be on the one or two things that make you all the money. And then allocate 10%… for stuff that is like this." [01:55:55]

## 2. The pipeline

"Anytime you see API, just think superglue." [00:36:50] "Claude… can be the orchestrator." [00:46:05]

| # | Step | Tool | In Lanny's words |
|---|---|---|---|
| 0 | Start, on a schedule | Claude Code scheduled task (cron / launchd / scheduled-task MCP) | "a start button… which is a recurring task and automated, at least it should be" [00:48:44] |
| 1 | Research | Claude's native web research, no external key | "The first step of the process is research." [00:48:58] |
| 2 | Script | Claude + platform knowledge base + copywriting instructions + a winning-scripts folder | "affected by a knowledge base. And it's infected by instructions." [00:49:25] Business KB required or it's "generic, crappy stuff" [02:30:35] |
| 3 | Avatar video | HeyGen API (Avatar IV twin); Hedra Character-3 Lite adapter added in v2 as the cheaper alternative | "send that script into HeyGen" [00:50:19] |
| 4 | B-roll and stills | Pexels API (free) and fal.ai API (pay-as-you-go image generation) | "then… it's gonna go ahead and find that B-roll footage." [00:51:16] |
| 5 | Composite | FFmpeg, run locally by Claude Code | "basically tape. It's gonna tape it all together." [00:51:24] |
| 6 | Captions | SubMagic API, optional | "You can run captions for free, they just don't look as good. So SubMagic is, like, sexy captions." [00:53:45] |
| 7 | Finished video | A local folder | "the finished product is actually going to be in a folder on your computer." [00:56:49] |
| 8 | Post | Manual | "the only thing you have to do is basically post." [00:46:52] |

"1, 2, 3, 4, 5, different API calls inside of this one process." [00:57:01] Any provider is swappable: "you don't have to use HeyGen" [00:27:04]; "if you're not using the digital twin, why use HeyGen?" [00:30:40]

*(inference)* The transcript mentions "Pexels storage" as temporary storage between steps; Pexels has no upload API, so the actual intermediate store is unknown. Treat it as local disk unless the zip says otherwise.

## 3. The `.env` file: the whole heavy lift

"We need to create a .env file. That holds our keys, and that's how we keep them safe." [01:00:50] "do it one time, and then that's something that Claude can then use to gain access to all the different platforms, without exposing your keys out to the world." [01:01:15] Protect keys like a credit card [01:01:02].

The recipe: "I say, give me a .env file template for my keys, so all I have to do is copy and paste the keys into the file." [01:02:01] Format is `VARIABLE=value`, "no spaces" [01:18:27]. The zip ships `.env.template`; the member copies it to `.env` and pastes keys in [01:16:26].

Keys seen or implied: HeyGen API key, avatar ID, voice ID; Pexels key; fal.ai key; SubMagic key (optional); Hedra key (v2, optional). *(inference)* Exact variable names live in the zip's template; do not guess them, read the template.

"really, the heavy lift is creating that .env file with your API keys. If you've done that, the rest is really easy." [02:18:45]

## 4. Accounts and costs, as stated

| Account | Required? | Notes |
|---|---|---|
| Claude desktop app with Claude Code | Yes | Chat / Cowork / Code in the left sidebar. "I don't think the web app codes" [00:45:10] |
| Pexels | Yes | "required… It's free." [00:31:06] |
| fal.ai | Yes | "everybody should have this… pay as you go" [00:32:17]; "last 7 days, it's cost me $2.30… 5-cent images" [00:32:41] |
| HeyGen | Optional | Creator tier (about $24–27/mo) only to create the Avatar IV twin; runtime is API credits. The checklist PDF wrongly said Pro was required [01:10:35] |
| Hedra | Optional | Character-3 Lite "about $32 a month… From $175" [01:31:58]; rated 9/10 vs HeyGen Pro 8.5/10 by Claude's research [01:31:30] |
| SubMagic | Optional | Captions |
| Local | Yes | FFmpeg and Python; Windows also Git and PowerShell. Claude Code prompts each install |

Monthly running cost stated on the call: required-only at one video a day, $100–150; three to five videos a day, $200–325 [00:22:15–00:23:04]. Buy at the source: a member paid roughly $800 a year for what was likely a wrapper around a 5-cent image model. "Hoodwinked." [01:38:02–01:43:23]

## 5. Avatar setup (HeyGen path)

"go to HeyGen, go to Avatar 4, and create a new avatar. you record 3 minutes of footage in the lighting and outfit you want for every video… Takes approximately 30 minutes for processing." [01:08:00] The Hedra path's avatar setup was not resolved on the call [01:35:43].

## 6. Install, as taught

Do not follow the checklist by hand. "I wouldn't do all these things. Because, Claude Code will do these things… I would upload the whole zip file into Claude Code. And say, run this." [01:09:35] "Forget about all those instructions. Just drag it in there and say, run this." [01:28:41]

1. Download the zip from the members' Drive. "There's no magic that I can do for you that will get around the you-don't download the zip file part of the process." [01:30:30]
2. Make an empty local folder, not in Google Drive, suggested `buildroom-video-engine` rather than Downloads [01:08:57, 01:13:29].
3. Claude desktop → Code → new session → add that folder [01:59:40].
4. Add the zip with the "+" and type **"install this"** (or "run this" / "set this up") [02:01:28].
5. Say yes to Claude's questions: create `.env` from the template, install FFmpeg, and on Windows Git, PowerShell, Python [01:16:57, 01:43:33, 01:25:03].
6. Paste the keys into `.env`.
7. Run. Without keys "it's gonna say, I don't have the keys… It's gonna trip up." [01:26:59]
8. Upgrade: in the same session, upload the new zip and say "here's the upgraded version" [02:06:10].
9. Schedule: "You just have to say the words, run this 3 times a day at 9am, noon, and 3 p.m. And it will create the cron job to do that." [01:21:04]

## 7. The feedback loop

"I would think of this as a starting point, not a finishing point." [01:04:18] Winners go into the winning-scripts folder; give feedback each run; refresh the platform knowledge bases; keep the business knowledge base current. "the difference between a bad script and a good script is pretty massive" [00:57:26].

## 8. Code or Cowork

Claude's own comparison, read on the call [01:19:42–01:23:34]: "Building custom pipelines with code, shell tools, and API integrations, Cloud code, no contest." [01:22:45] "Daily scheduled runs of an already-built workflow with simple components, co-work is great." [01:23:27] Cowork is better for the scheduled-task GUI, the HeyGen MCP (uses plan credits, no API key), folder permissions, and non-technical members. Lanny's rule for this project: "I want you to do this in code and not in co-work" [01:12:05], and Cowork-first for a member with no APIs at all [02:13:58].

## 9. Troubleshooting, as taught

- Paste the failure: "copy and paste that whole failure into Claude and say, what do I need to do?" [02:34:14]
- Delegate installs: "I've already downloaded FFmpeg… please go ahead and install it for me." [02:35:00]
- Windows: `winget install ffmpeg` in Claude Code's built-in terminal (dropdown under the X) [02:27:38]; wrong working directory and the source-vs-binary FFmpeg page confused two members.
- For a stuck first-run install, a live-video screen-share assistant helped where the chat could not [02:03:32].
- Expect friction: "Is everybody okay with sucky today?" [00:06:05] "the juice is worth the squeeze" [02:05:28]

Unresolved on the call: two Windows members could not get Claude Code's first-run extras installed; the Hedra avatar via API; the free-captions path.

## 10. The lead-capture bridge

The keyword call to action: the viewer comments a keyword, GoHighLevel "is listening for that, grabs it, and starts an automated conversation to get their contact information to create a lead, and then delivers the free thing." [01:48:37] "I created over a thousand leads overnight… Organic leads." GHL "replaces ManyChat." Instruction to the script step: "I want to use a call to action to a keyword, and that keyword gives away a free thing. Make that part of the script, and it will." [01:50:15] The demo CTA copied a Lead Gen Camp line; "I wouldn't end the CTA exactly like that" [01:48:49].

## 11. Open questions for the member's own install

1. The actual zip tree, script names, and the exact `.env.template` variables come from the zip; this guide does not reproduce them.
2. Whether the pipeline calls the Anthropic API directly or runs inside the Claude Code subscription.
3. Output specs (aspect ratio, resolution, duration target, per-platform variants).
4. The scheduling mechanism actually configured, and the Windows equivalent.

## 12. Quote bank

- "Anytime you see API, just think superglue." [00:36:50]
- "Claude… Can be the orchestrator." [00:46:05]
- "all we're doing is we're adding a whole production assembly line on the back of that" [00:52:09]
- "I would think of this as a starting point, not a finishing point." [01:04:18]
- "This is like making Zapier on steroids" [01:54:47]
- "really, the heavy lift is creating that .env file with your API keys." [02:18:45]
- "if you don't have the knowledge base file, you'll want to create that… otherwise, it'll be generic, crappy stuff." [02:30:35]
