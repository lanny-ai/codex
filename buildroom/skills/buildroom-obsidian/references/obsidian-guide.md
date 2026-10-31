# The Second Brain — Obsidian + Claude Code, Method Guide

Reconstructed from the Build Room sessions of 2026-06-03 (Week 1, setup), 2026-06-10 (Week 2, the knowledge base and the YouTube extraction tool), 2026-06-24 (Week 4, the graph, commands, personas, routines), and the office hours of 06-08, 06-15 and 06-29 (host Lanny Morton, AI Momentum Labs). Week 3, the watchers, is its own elective (`buildroom-source-watcher`). These Zoom transcripts carry no timestamps, so quotes cite the session and transcript line, for example [W1 L79]. *(inference)* marks a reading, not a statement. Members are not named.

## 1. What it is and why

"Today we stop using AI and start building AI that knows you. By the end of the session, you will own a knowledge base that Claude can think, work, and create inside of, on your machine. Yours forever. So the data goes from the cloud to your computer." [W1 L59–60]

The problem: "It has amnesia. Every new chat feels like it starts from zero, you have to re-explain things, your offers, your voice, again and again." [W1 L67] "Imagine hiring a brilliant assistant who forgets everything you told them every single morning." [W1 L68] The principle: "You capture it once, but you leverage it forever." [W1 L79]

The pairing: "Obsidian alone is beautiful notes that just sit there. Claude Code alone is brilliant, but forgetful." [W1 L118] "Obsidian is the memory. Claude Code is the mind. Put the mind inside the memory, and you've got a thinking system that runs your business, not a chatbot you babysit." [W1 L131–133] Plainer: "Claude Code is the worker. Obsidian is just the brain." [W2 L459] "Notion, Airtable, spreadsheets, SQL, all are passive storage. None of them think." [W1 L84] "Your mind doesn't think in folders, it thinks in connections." [W1 L106]

Ownership: "It lives on your machine, there's no platform can lock it, delete it, or train on it." [W1 L157] "Obsidian is free." [W1 L158] Business value: the data "becomes a value layer in your company. It would make a legitimate and significant difference in the sale of a company." [W1 L180–182]

The pattern underneath, the one this whole month teaches: "Chat, apps or GPTs, agents, swarms. When you go to the apps and GPTs, you have two different things to work from. One is a knowledge base. The other one is instructions. Everything we're talking about this month is about this knowledge base." [W2 L151–157] "If the knowledge base is awesome, everything's better." [W2 L269] "The knowledge base comes first. If it's not operating from what really matters to you, then it's just generic fluffy BS." [W4 L732–733]

Expectations: "The setup is probably the hardest part of the whole process. Once it's set up, it's actually really, really easy to use." [W1 L402] "The juice on this one is worth the squeeze. You don't have to get it today." [W1 L96]

## 2. Setup, as taught (Week 1)

1. **Obsidian, the desktop app.** "obsidian.md, download it and run it." [W1 L433–434] Two traps: being on the website instead of the app ("go to your download folder and run the download" [W1 L556–561]) and running the installer instead of the program ("You open the program, not the installer." [W1 L639]).
2. **A vault, which is a folder.** "Click Create New Vault. It's just a folder on your computer where your notes are kept. Give it a name like Brain." [W1 L443–444] "Don't use OneDrive." [W1 L630] If the first attempt went wrong: "just create a new one. Let's not do brain damage." [W1 L519]
3. **Claude Code.** Mac: Terminal, paste the install line "from the curl all the way to the bash." [W1 L947] Windows: PowerShell, paste the line "all the way to IEX, the whole thing." [W2 L1182] A failing `claude --version` right after install is normal; reopen the terminal. Some members used `winget install Anthropic.ClaudeCode`. [W1 L1181]
4. **The Terminal plugin, optional.** Settings → Community Plugins → browse → "Terminal" → install → enable. Then Cmd-P (Ctrl-P on Windows) → "Open Terminal Integrated" → type `claude`. [W1 L645–681, L1085–1093] On Windows the integrated terminal is an old cmd: type `powershell` first, then `claude`. [W2 L238–242]
5. **First run.** "Definitely do Claude with a subscription, don't want to do API, that way you're not using API tokens." [W1 L1277–1278] Copy the auth URL into a browser, Authorize, paste the code back, "Yes, I trust this folder." "This is a one-time thing." [W1 L1282]
6. **First conversation.** "Just say hi. I want you to help me get all my data into Obsidian." [W1 L1386–1398]
7. **Two starter files.** Run `/init` so Claude writes a CLAUDE.md of standing instructions, with "always check my knowledge base first," and ask for a one-page cheat sheet of commands. "The cheat sheet is for the human, CLAUDE.md is for the AI." [W1 L3550–3605]

**The shortcut, learned a week later.** "You can just point Cowork or Claude Code at the folder you've created for Obsidian, and basically get the same benefit. You don't have to do all that PowerShell nonsense." [W2 L209–226] Claude's own verdict, read aloud: "What the embedded terminal setup actually buys you is ergonomics, not capabilities. The live feedback loop is a real one; Obsidian re-renders it instantly." [OH 06-08 L1103–1105] "I should have known that last Wednesday." [OH 06-08 L1114] So: the plugin is nice; opening Claude Code (or Codex, or Cowork) on the vault folder is the requirement.

Troubleshooting, taught more than any fix: "Copy and paste that whole block and feed it in and say, huh? And it'll figure it out for you." [W1 L357–358]

## 3. The first fill (Week 2)

"Point it at my knowledge. Get everything from this drive, that drive, my Google Drive. You could search through my emails, look for the stuff that's valuable, not the stupid promo stuff." [W2 L419–420] "Go look at this folder and grab everything. It'll transcribe the videos for you." [W2 L275–276]

The coaching prompt: "I'm getting my Obsidian database going, I want you to coach me through this. Research what are the five best first steps, then say, okay, go do it." [W2 L441–444] Give it context first: "This is my focus, these are my goals, so it has a context of what is important to you." [W2 L433]

Claude's "five smartest things," read out on the call: capture before plugins or themes ("an empty vault is worthless"); link generously, even to notes that don't exist yet; one frictionless capture habit; "light, consistent front matter from day one: type, tags, date, and source"; learn search and backlinks; put the vault under git or Sync. [W2 L1025–1045]

**Quality gates.** "If you're allowing crap in, then you're really not gaining the benefit. Putting a quality gate is literally adding a but: avoid XYZ, or make sure it's useful to what I'm doing." [W2 L789–792]

**Then stop.** "Based on everything you know about my business, what are the five highest leveraged ways I can use this?" [W2 L761] "Just have it do one thing that crushes it for you, and stop there." [W2 L773] Members' first wins: a brand voice document; "The interview me is really fun, getting information out of your head." [W1 L3639–3640]

**Sources that keep flowing in.** YouTube channels and single videos (the Video-to-Vault skills, in the Source Watcher elective), podcasts and anything else (the Watcher Master), and Zoom: "Did you give it access so it can go into Zoom and you don't have to? It's not as simple as grabbing an API key with Zoom. But it's not that hard either." [W2 L1005–1019] The founder's runs nightly: "It downloads the transcripts for the day, and it brings it into the brain." [W1 L187]

**Sessions vanish** in the embedded terminal; a member's fix was a prompt that sets up a session-log folder with auto-append, or "create me a skill that after every session, when I say save, a markdown file will be created in my vault." [OH 06-29 L710]

## 4. Commands, hats, routines (Week 4)

1. **Slash commands.** "After Claude does something useful, you can tell it to save that as a command, and then you can just run it by typing one word. It's almost like a hotkey." [W4 L124]
2. **Expert hats.** "From now on, when I say, as my CFO, copywriter, or strategist, answer in that role and use the relevant notes in my vault as your knowledge. Add this to my CLAUDE.md so you remember it every time, confirm when it's set." [W4 L127] Built live: "I want to create an agent that represents Napoleon Hill. Do a deep research task. Do you have any questions that'll help us make this a more elite agent?" [W4 L926–933] "You do the work once, now you can command them anytime you want." [W4 L981–982]
3. **Morning briefing, scheduled.** "Look at my recent notes, open loops, and anything marked as a task or follow-up in my vault. Tell me my three top priorities today, what's waiting on me, and one thing I'm probably forgetting. Keep it short." [W4 L343]
4. **Ask your brain.** "Search my whole vault and answer this. Tell me which notes you used." [W4 L389]
5. **Weekly synthesis.** "Review the notes I added or changed in the last 7 days. Surface the 3 most useful connections or patterns. Flag anything I left unfinished, and turn the single best insight into a short post in my voice." [W4 L392–393]
6. **Frictionless capture.** "Here's a rough, messy thought. File it properly." [W4 L407]
7. **Find what you're missing.** "Tell me what is thin or missing, then research the web to fill the single biggest gap." [W4 L412] "If you want to know why my custom apps are good, it's because I know where my blind spots are." [W4 L414]
8. **One note, many outputs,** one at a time: "Don't ask for all of these things in one output. If it gives it to you in one output, all three are gonna suck." [W4 L458–461]

**Graph maintenance.** "I don't have to be organized, it does the organization for me. I also run maintenance runs, usually once a week: connect all the things that aren't connected, because I'm in dumping mode still." [W4 L141] "When I see a lot of disconnected nodes, I'll do a connection sweep." [W4 L553]

**Where CLAUDE.md lives.** A `.claude` folder in the vault holds the project CLAUDE.md, which takes precedence over the global one. [W4 L157–162] Does the founder direct Claude to the vault? "Pretty much, because it's there in the folder." [W4 L178]

**The rhythm.** "Daily, capture one thing into your vault and ask your brain one question. Weekly, 20 minutes, run your weekly synthesis, turn it into one piece of content." [W4 L473] "The vault stops being something you maintain; it becomes something that briefs you, answers you, and produces for you." [W4 L475] The bridge to the next month: "Tell me some things that I do on a regular basis that I could systematize and create SOPs for and have you do." [W4 L378]

## 5. Failure modes from office hours, with the answers

- **"claude is not recognized."** A path problem. Fully quit and reopen Obsidian; or paste the error into Claude and run its path commands one at a time; on Windows, add the `.local\bin` folder under Environment Variables, then reopen PowerShell. [W1 L1192–1195, L1627; W2 L1198–1240]
- **The vault landed in OneDrive** because OneDrive had taken over Documents. Make a fresh vault under This PC → Local Disk. [W1 L2765–2780]
- **PowerShell too old.** Update it; one member needed PowerShell 7 from IT. [W1 L805–813]
- **Can't paste into the embedded terminal.** Ctrl-C to reset, or use the external terminal. [W1 L1498–1566]
- **Lost auth after switching machines.** Run `claude` and redo the browser authorization. [W2 L973–996]
- **"Does everything I do in Claude flow into the vault?"** "I don't think it's just gonna randomly start sucking in all of your conversations. There has to be an action that causes that trigger." [OH 06-29 L686–687] Think instead: "What are the recurring ways in which I want it to grow that don't require my presence?" [OH 06-29 L670]
- **Obsidian terminal or the desktop app?** "If you're working on your brain, making the brain better, then do it inside of Obsidian, but if you're trying to build an app, do it here [the desktop app]." [OH 06-15 L1305] Outside Obsidian, "you have to make sure that they're on the same folder." [OH 06-15 L1350]
- **Many projects, one vault?** "You can't confuse Obsidian. It's a repository. Obsidian doesn't think." [OH 06-15 L947–950]
- **It started coding when you wanted to think.** "Say, I don't want you to code anything right now. I just want to collaborate with you." [OH 06-08 L51–52]
- **Tokens.** Settings → Usage; the terminal uses "less tokens overall than the desktop app." [W2 L1505–1512]
- Honesty: "I literally had somebody email me and say, this isn't for me, I want a refund." [W1 L3661] "On the other side of crappy is something really amazing." [OH 06-08 L117]

## 6. Costs and accounts

| Item | Required | As stated |
|---|---|---|
| Obsidian desktop | Yes | Free. Obsidian Sync "$5 to $10 a month" only if you want the vault on your phone. [W1 L169] |
| Claude subscription with Claude Code (or Codex, or Cowork pointed at the folder) | Yes | "With a subscription, not API tokens." [W1 L1278] Heavy watching suits the top plan. |
| Terminal community plugin | Optional | Free. Ergonomics, not capabilities. |
| yt-dlp, ffmpeg (Mac via Homebrew); PowerShell 7 (Windows) | Only for the video skills | Free |
| Zoom app connection | Optional | A few steps; Claude walks it. |
| Storage | Local disk | "$180 for two more terabytes" if it ever comes to that. [W1 L200] |
| An always-on machine | No | The founder's is his choice: "I'm not recommending that you go pay." [W4 L310–311] |

Manual once: install, authorise, choose the vault, point at the first sources, research the personas, set the quality gates. Recurring by design: Zoom nightly, channel watches weekly, the morning briefing, the weekly synthesis, the weekly connection sweep.

## 7. Open questions

- One blessed Windows path (embedded cmd → `powershell` → `claude`, versus editing the PATH, versus winget) was never consolidated. This skill teaches "open Claude Code on the folder" as the requirement and the plugin as optional.
- The Zoom connection type was not shown on the call.
- How the morning briefing is scheduled (a scheduled task in Cowork, cron, launchd) was not specified; say the words and confirm what the tool created.
- The token cost of continuous channel watching on smaller plans was raised, not measured.

## 8. Quote bank

- "You capture it once, but you leverage it forever." [W1 L79]
- "Obsidian is the memory. Claude Code is the mind." [W1 L131]
- "Your mind doesn't think in folders, it thinks in connections." [W1 L106]
- "Point Obsidian through Claude Code at your whole Google Drive. And just save." [W1 L332–333]
- "Claude Code is the worker. Obsidian is just the brain." [W2 L459]
- "If you're allowing crap in, then you're really not gaining the benefit. Put quality gates on it." [W2 L791]
- "Just have it do one thing that crushes it for you, and stop there." [W2 L773]
- "Daily, capture one thing into your vault and ask your brain one question. Weekly, 20 minutes, run your weekly synthesis." [W4 L473]
- "If it gives it to you in one output, all three are gonna suck." [W4 L461]
- "What the embedded terminal setup actually buys you is ergonomics, not capabilities." [OH 06-08 L1103]
