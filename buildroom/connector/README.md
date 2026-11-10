# Build Room connector (pilot)

A remote MCP server that serves Build Room OS to current members, so nobody downloads a zip each week. A member connects once; every session they start comes from this server, checked against the member list each time. Updates reach everyone the moment the skills change here.

**What stays on the member's computer:** their Business File and everything they make. No tool asks for the Business File or stores it. Scripts a session needs run on the member's machine.

## Pilot: a member list you control

For the pilot, membership is a short list in `members.json` (kept out of git). The check lives in one place in `server.py` (`AllowlistSource`), so GoHighLevel can replace it later without changing anything a member sees.

```
python3 members.py --base-url https://YOUR-HOST add someone@example.com --until 2026-12-31 --name "Pat"
python3 members.py list
python3 members.py lapse someone@example.com          # access stops on their next request
python3 members.py reactivate someone@example.com
python3 members.py new-key someone@example.com        # a lost or shared key; the old one stops at once
python3 members.py remove someone@example.com
```

`add` and `new-key` print the member's access key and their connection instructions **once**. Only a fingerprint (sha256) of the key is stored. Send the key to the member privately.

Rules the server applies on every request:

| Member | Result |
|---|---|
| Key not on the list | Refused at connection (a mistyped link fails when it is added) |
| `active`, no end date or end date not passed | Allowed |
| `active`, end date passed by 7 days or less | Allowed (grace period, set by `grace_days` in members.json) |
| `active`, end date passed by more than 7 days | Connects, every session refused: "Your Build Room access has expired" |
| `lapsed` | Connects, every session refused: "Your Build Room membership is not current" |

Each refusal tells the member their Business File and work stay on their computer.

## What a connected member gets

| Tool | Does |
|---|---|
| `buildroom_status` | Their access and the connector version |
| `buildroom_list_sessions` | All sessions with the words that start them |
| `buildroom_start_session` | One session's full instructions, plus its file list |
| `buildroom_get_file` | One reference or script file of a session (listed files only) |
| `buildroom_whats_new` | The latest release notes |

The member just talks as they do today ("Get found on Google"); Claude picks the session through these tools.

## Run it

```
python3 server.py --port 8787                     # http://127.0.0.1:8787/mcp
python3 server.py --host 0.0.0.0 --port $PORT     # on a host
```

Python 3.9 or later, nothing to install. Settings: `--members` / `BUILDROOM_MEMBERS` (path to members.json; keep it on a persistent disk), `--skills` / `BUILDROOM_SKILLS` (defaults to `../skills`), `BUILDROOM_USAGE_LOG` (one line per tool call: when, member email, tool, session, outcome; never a key or member content).

**Hosting:** it must be served over HTTPS. Any host that runs a Python web process works (Render, Railway, Fly.io, a small server behind a TLS proxy). Deploying is a push of this repository plus a members.json on the host's disk. `GET /health` answers for uptime checks.

## On Railway (live)

Project **buildroom-connector**, service **connector**, in the lanny-ai workspace. Address: `https://connector-production-caa1d67a.up.railway.app` (health: `/health`).

- It builds `buildroom/connector/Dockerfile` (set by `railway.json`) from the branch `claude/new-session-1rmv4i`. Once PR #5 is merged, switch the service's branch to `main` in Settings, Source.
- It redeploys by itself when anything under `buildroom/skills/` changes on that branch, so members get updated sessions within minutes of a push.
- **The member list is the `BUILDROOM_MEMBERS_JSON` variable.** To change it: copy the variable's value from Railway into a local `members.json`, run `members.py` (add, lapse, reactivate, new-key, remove), then `python3 members.py export` and paste the line back as the variable's value. Railway redeploys in about a minute. Keep that local `members.json` somewhere private; it holds only key fingerprints.
- Usage lines (`usage {...}`) appear in the service's Deploy Logs.

## How members connect

**Claude desktop or claude.ai** (paid plans): Settings, Connectors, Add custom connector, and paste their link:

```
https://YOUR-HOST/mcp/<their key>
```

**Claude Code:**

```
claude mcp add --transport http buildroom https://YOUR-HOST/mcp --header "Authorization: Bearer <their key>"
```

**Codex:** add it as a remote MCP server in Codex's settings with the same URL and header. Not yet tried; confirm it with one pilot member before promising it.

## Checked

- `python3 buildroom/tests/connector/run_tests.py`: 52 checks (protocol, every membership rule, key rotation, path safety, logs carry no keys).
- The official MCP Python client connects with the key in the header and with the key in the link, lists the tools, starts a session, loads a reference, and is refused a path outside a session.
- Claude Code's `claude mcp add` and `claude mcp list` report it connected with a good key and refuse a wrong one.
- Live on Railway (2026-11-10): the same checks pass against the Railway address, and the owner connected it in Claude desktop as a custom connector.

## Before full launch (not in the pilot)

1. **Sign-in instead of keys.** The link with a key in it is a pilot shortcut: anyone holding the link gets in until the key is replaced. Full launch adds a proper sign-in (OAuth with the member's email), which Claude's connectors support.
2. **GoHighLevel as the membership source**, once the member data is cleaned up: one tag or field meaning "current Build Room member", ideally set by payments.
3. **The local kit**: the scripts members run on their own computer, shipped rarely, with the safe `update.sh` / `update.ps1`.
