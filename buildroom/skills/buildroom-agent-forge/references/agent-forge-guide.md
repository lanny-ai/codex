# Agent Forge — Method Guide

Reconstructed from the Build Room session of 2026-07-29 (a seventeen-minute preview, host Lanny Morton, AI Momentum Labs), the same-day bootcamp where the tool was shown again, the 2026-08-03 office hours follow-up, and the 08-06 and 08-13 sessions. Timestamps are from the recordings' notes; bootcamp quotes cite the block at [03:16:06]. *(inference)* marks a reading, not a statement.

## 1. What it was, and what survives

Agent Forge was a web app the founder had Codex build in July 2026: an agent builder with a researched knowledge base behind it. "It's an agent builder. And there's some really good, deep research in the knowledge base of this thing, so I didn't just slap this thing together, this took some time." [07-29 00:00:35] "When I say I, I mean, like, Codex is building this, I'm not doing anything." [07-29 00:00:35]

The app never reached members. The link returned access denied the same night; on 08-03 the founder read Codex's diagnosis aloud, "The hosting workspace blocks public internet publish, so platform rejected access change" [08-03 02:04:56], asked for a widget workaround, and the tool is not mentioned again in any session through September. On 08-13 he said his production agents are not built in any builder: "It would actually be coded and then put into the code. They're literally written into the code." [08-13 00:27:19–00:28:19]

What survives is the checklist, and the founder said that was the point: "There are thirteen steps in the process of creating a great agent. I can tell you right now, you don't need to know any of these thirteen. You can just call it information, and then you can forget it forever, and you can still create agents." [bootcamp 03:16:06] "You could just say, I need you to build me an agent. And guess what? ChatGPT and Claude knows all thirteen of these things, and they can build them for you." [bootcamp 03:16:06] This skill is that: the thirteen elements applied for the member, producing an agent definition they can install.

## 2. The problem it solves

"The two things you add that you don't have in chat are a knowledge base and instructions. There's actually probably thirteen different elements that make an agent. Constraints, safety measures, guardrails, all that stuff." [08-13 00:26:38–00:27:19] "If you were gonna start from scratch and build a world-class agent, these are the things you would do." [07-29 00:02:45] "I could strip this down just to four or five, and it would probably be fine. But if I was going to create a world-class agent, these are everything that you would want." [bootcamp 03:16:06]

## 3. The thirteen elements

Named in order on 07-29: "the basics, the outcome, identity, context, knowledge, files and sources, memory, tools, workflow, boundaries, escalation, verification, metrics, and review." [00:02:45] That is fourteen words; on the bootcamp the founder folded knowledge and its source files together, so this skill treats "knowledge and sources" as one element and "review" as the closing gate.

| # | Element | In the founder's words | What it produces |
|---|---|---|---|
| 1 | Basics | "the name, the descriptions"; demo: "agent name, LinkedIn Lead Generator, department sales" | Name, one-line description, department or owner |
| 2 | Outcome | "The outcome is the first thing. What do you want the outcome to be, from this agent?" | One outcome statement with its definition of done |
| 3 | Identity | "What's the identity of this agent? How does it sound? What's its role?" | Role and voice |
| 4 | Context | "I had two different COO agents, one that was a problem solver, and one that was a planner. They both had the same role, but two different contexts of how I programmed them to operate" | Operating mode and situation |
| 5 | Knowledge and sources | "What is the thing that they're operating from? If I was creating a Michael Jordan agent, would I want the DNA of the whole world in there? No, I just want Michael Jordan" | A tightly scoped knowledge base and the files it reads |
| 6 | Memory | "What is there to remember?" | What persists between runs, and where |
| 7 | Tools | "What are some of the tools that it has the ability to use?" | The tool list, nothing more |
| 8 | Workflow | "What's that workflow sequence of things that are gonna happen?" | Ordered steps with inputs and outputs |
| 9 | Boundaries | "What can't it do? That's important, especially if you're giving it access to sensitive information. It has to have really, really tight guardrails." | The can't-do list |
| 10 | Escalation | "When does the human jump in the loop?" | Human-in-the-loop triggers |
| 11 | Verification | "How can we prove that the output was valid and correct?" | Checks the agent runs on its own output |
| 12 | Metrics | "How are we measuring? What are the KPIs?" | The numbers that say it's working |
| 13 | Review | "This is just a review stage to validate and push." | The member's sign-off before it runs |

Three ways in, from the app: "You can start from scratch, which is a thirteen-step guided builder with intelligent defaults. You can use a template, or you can just use plain language, describe what you need." [07-29 00:02:45] Templates shown: appointment booking, lead qualifying, customer support, client onboarding, sales follow-up. A fourth way was agreed with a member on the call: "refine an existing" [07-29 00:09:00], feeding in a markdown file, and "if you found something cool on the internet, but you're afraid of it, you could put it in there and it could basically scan it for safety and recreate it." [07-29 00:09:17]

The only worked example, spoken as the plain-language path: "I need an agent that'll go on the job boards and find companies looking to hire somebody to do AI automations and AI services. Those would be really good leads." [07-29 00:02:45]

## 4. Agent, skill, or automation

A member's answer the founder let stand: "The skill is how it does it. The agent uses skills to do stuff. The agent has guardrails around, here's where you start, here's where you finish, and this is the definition of done." [07-29 00:11:33–00:11:45] The founder's version: "the person is like the agent, the skill is the thing you're doing." [bootcamp 03:16:06]

In the Build Room the FDE audit in the SOP Creator decides *whether* a process should be automated (go, no-go, partial) and maps it; §9 lists the automation candidates with their stage. Agent Forge is where a Go or Partial candidate becomes an agent definition. *(inference)*

## 5. Building it once the definition exists

The founder's loop from 08-06, for anything built in Claude Code or Codex: "You do a brainstorming session first. Prompt number two, let it come up with your pursue goal statement. Then you take prompt three and it'll start building the thing for you. One, two, three, that's it." [08-06 02:18:12–02:18:55] "If you don't get one, two, and three, the rest don't matter." [08-06 01:41:02] For an agent, the thirteen elements are the content of steps one and two; the definition this skill produces is the goal statement. *(inference)*

Trust is staged, as the FDE audit teaches: shadow mode, then approve-each, then autonomous, one step at a time, and every human correction goes into the test set.

## 6. Don'ts

- Don't install agents or skills from strangers. "People will create skills and say, here, have my skill, or have my agent, and it can be a Trojan horse into your computer." Remedy: "take my skill and scrub it, and turn it, and redo it, just in case." [bootcamp 04:17:28] That is the refine-an-existing path here: read it, list what it does and what it reaches, rebuild it clean.
- Don't put the whole world in the knowledge base. "I just want Michael Jordan."
- Don't skip boundaries when the agent touches money, customers, or sensitive data.
- Don't memorise the thirteen. Ask for them.
- Don't rely on a vendor's builder for production agents; the definition is the asset, the build is code. [08-13]
- Don't announce a giveaway before the link works. [08-03]

## 7. Open questions

- The app's own export format was never shown. This skill outputs a markdown agent definition in a fixed shape (`references/agent-definition-template.md`), which installs as a Claude Code or Codex skill or agent, or reads as a spec for any other platform.
- Whether "refine an existing" and the community catalogue were ever built: no evidence after 08-03.
- The deep-research knowledge base behind the app is not in the vault; this skill's foundation is the founder's own words plus the SOP Creator's audit.

## 8. Quote bank

- "There's some really good, deep research in the knowledge base of this thing, so I didn't just slap this thing together." [07-29 00:00:35]
- "You don't need to know any of these thirteen. You can forget it forever, and you can still create agents." [bootcamp 03:16:06]
- "ChatGPT and Claude knows all thirteen of these things, and they can build them for you." [bootcamp 03:16:06]
- "Would I want the DNA of the whole world in there? No, I just want Michael Jordan." [bootcamp 03:16:06]
- "When does the human jump in the loop? How can we prove that the output was valid and correct? What are the KPIs?" [bootcamp 03:16:06]
- "It can be a Trojan horse into your computer." [bootcamp 04:17:28]
- "One, two, three, that's it." [08-06 02:18:55]
