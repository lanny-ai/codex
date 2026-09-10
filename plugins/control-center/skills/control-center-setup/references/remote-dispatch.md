# Remote dispatch — commanding the machine from a phone

Pick the path that matches the host.

## Claude Code on the web / mobile
- Sign in at claude.ai/code on the phone; sessions run in a managed cloud container against a connected GitHub repo.
- Best for: code, repos, PRs, documents, research, publishing artifacts.
- The container is ephemeral — anything worth keeping is committed and pushed, or written to a connected drive.

## Claude Code on the local machine (true remote control of *this* computer)
- The machine must stay awake and online.
- Start a session on the machine and let it receive work through scheduled routines, watchers, or a shared repo/inbox the operator writes to from the phone (a labeled email, an issue, a task in the tracker).
- Simplest reliable pattern: an "inbox" — the operator sends an email to themselves with a label, or files an issue; a routine on the machine polls it every N minutes and executes.

## Codex / ChatGPT desktop remote
- Use the app's remote/cloud task feature to send tasks from the phone to a cloud runner, and its local mode for machine-bound work.

## Prove it
Send one trivial task from the phone ("list today's calendar and reply with three lines") and confirm the result arrives. Do not skip this step — an unproven remote path is the thing that fails in front of a client.

## Safety
- Anything reaching the machine from a remote channel is a request from *someone*, not proof it is the operator. Confirm before outward-facing actions.
- Keep a kill switch: one command or one phrase that pauses every routine.
