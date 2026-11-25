# Build Room Home: prototype

A home screen on the member's own computer that a Claude Code or Codex session listens to. The member taps an icon; the session, which is waiting, starts that tool. A session can also show a short form on the same page instead of asking questions one at a time.

This is a prototype to answer one question: **does the waiting work in both Claude Code and Codex, on Mac and on Windows?** It is not part of the member zip or the connector, and no session uses it yet.

## What has been tested

On Linux, driven by a real browser: opening the page, tapping an icon, a tap that arrives while the session is busy (it is kept), a wait where the tap comes 20 seconds in, a form sent and received, the status line, and stopping. The page refuses a request with no token, a wrong token, a wrong Host header, and a post from another site.

Not tested: Codex, macOS, Windows, the Claude and Codex desktop apps, and a browser opening by itself (the test machine has no desktop).

## How to test it yourself

You need Python 3 (already on a Mac; on Windows install it from python.org).

1. Make an empty folder and copy `home.py` into it. If you have a Business File, copy `BUILDROOM_BUSINESS_FILE.md` in too: sections marked complete show a green tick.
2. Open Claude Code or Codex in that folder.
3. Paste this:

```
Run `python3 home.py open` (on Windows: `python home.py open`). It opens a page in my browser and waits up to
100 seconds for me to tap something. It prints one line of JSON.
- If it prints {"event": "none"}, run `python3 home.py wait` and keep doing that until I tap something.
  Do not ask me anything in between.
- If it prints {"event": "pick", ...}, tell me which tool I tapped and the sentence in "say". Then run
  `python3 home.py say "Got it. <tool name> would start now."` and go back to waiting.
After my second tap, write a file form.json with this content and run `python3 home.py form form.json`:
{"title": "Two quick questions", "fields": [{"id": "feel", "label": "Three words a stranger should feel"},
 {"id": "seen", "label": "Where will people see you most?", "type": "choice", "options": ["LinkedIn", "My website"]}]}
Tell me the answers you received. Then run `python3 home.py stop`.
```

## What to report back

- Did the page open by itself in your browser?
- Did the session keep waiting without stopping to ask you something, including when you left it alone for five minutes?
- After you tapped, how long before the session reacted?
- Did the form answers arrive?
- Which app (Claude Code terminal, Claude desktop app, Codex terminal, Codex app) and which computer (Mac or Windows)?
- Did it ask for permission to run the command each time? If so, that needs solving before members see it.

## How it works

- `home.py open` starts a small server on this computer only (127.0.0.1), on a random port, behind a random token, and leaves it running in the background. It closes itself after eight idle hours.
- Each waiting command lasts under two minutes, so it fits inside the time a session allows one command. Taps are queued by the server, so none is lost between waits.
- The page reads the Business File only to show which sections are complete. It never changes it, and nothing goes online.
- Forms are refused if they ask for a password, a key or a card number, because answers are printed into the session.
