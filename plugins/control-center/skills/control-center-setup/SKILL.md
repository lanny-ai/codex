---
name: control-center-setup
description: Guided onboarding that turns a personal computer into a remote-controllable Control Center. Use when a user wants to set up connectors, MCP servers, API keys, browser automation, scheduled routines, or remote dispatch so they can command their machine from their phone or anywhere. Trigger on "set up my control center", "command center", "control my computer remotely", "connect my email/calendar/drive", "add an MCP server", "add API keys", "remote dispatch", or "run things while I'm away".
---

# Control Center Setup

Goal: in one guided session, give the operator a machine they can command from anywhere — email, calendar, files, browser, code, publishing, and scheduled routines — with credentials stored safely and remote dispatch enabled.

Works in both Claude Code and Codex/ChatGPT desktop. Detect which host you are in and use that host's paths (see `references/host-differences.md`).

## Rules

- Never write an API key, token, password, or OAuth secret into a repo, a skill file, a prompt log, a screenshot, or a commit. Secrets go in the OS keychain or a `.env` file that is git-ignored (`references/credentials.md`).
- Confirm before any outward-facing or irreversible action: sending mail, publishing, paying, deleting, posting.
- One operator, one machine, one set of credentials. Never reuse another person's keys.
- Start every new capability in supervised mode. Promote to unattended only after three clean supervised runs.

## Onboarding workflow

Run these as an interview — one step at a time, confirming each before moving on. Keep a live checklist in the chat.

1. **Scope interview.** Ask what they most want to command remotely. Offer the menu in `references/capability-menu.md` and have them pick 3–5 for today. Do not install everything.
2. **Host check.** Confirm host (Claude Code CLI/web/desktop, or Codex), OS, and whether the machine stays powered on. Record it.
3. **Workspace.** Create `~/control-center/` with `config/`, `logs/`, `runbooks/`, `outbox/`, and a git-ignored `.env`. Copy `assets/starter/` into it and fill placeholders.
4. **Credentials.** Walk `references/credentials.md`: which keys are needed for the chosen capabilities, where each is obtained, and how to store it. Verify each one with a read-only test call. Never echo the value back.
5. **Connectors / MCP.** Install only the servers the chosen capabilities need, using `references/mcp-catalog.md`. Prefer first-party connectors (Gmail, Calendar, Drive, GitHub) over custom servers. Test each with one read-only call.
6. **Browser automation.** Set up the browser layer per `references/browser-automation.md` for anything without an API. Log in once, interactively, in a persistent profile; never script a password.
7. **Remote dispatch.** Enable the "command it from my phone" path per `references/remote-dispatch.md` — Claude Code on the web / Claude dispatch, or Codex remote — and prove it end to end with one trivial task sent from the phone.
8. **Routines.** Create at most two scheduled routines to start (morning brief, inbox triage). Use the host's scheduler; see `references/routines.md`. Give the operator the exact phrase that pauses them.
9. **Runbooks.** For each chosen capability, write a short runbook in `runbooks/` naming the trigger phrase, the steps, the guardrail, and the rollback.
10. **Handoff.** Print a one-page summary: what is connected, what phrases command it, what is still supervised, where the logs are, and how to revoke every credential.

## Verification gate

Do not declare the Control Center live until all of these pass and you state each result plainly:

- Each configured connector returned real data on a read-only test.
- One remote command sent from the phone completed and reported back.
- `.env` is git-ignored and no secret appears in any tracked file.
- The operator knows the pause phrase and the revoke procedure.

## Then

Hand off to `control-center-command` for daily operation.
