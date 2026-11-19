# Old local copies of the tools

Members who installed Build Room OS from a zip have copies of every tool on their computer. Those copies are frozen at the day they unzipped. The connector always serves the current version. When both are present, an old local copy can be picked up instead of the current one, and the member never knows.

The fix is to move the old copies aside, once. Many members are not technical, so you do it for them. They only say yes.

## When to check

Once per conversation, the first time you use the connector in a place where you can read files (Cowork, Claude Code, Codex). In a regular chat there are no local copies, so there is nothing to check and nothing to say.

## How

1. Look for folders named `buildroom-*` in these places: `.claude/skills`, `.codex/skills` and `skills` in the working folder, and `.claude/skills` and `.codex/skills` in the member's home folder.
2. If there are none, say nothing and carry on with what the member asked.
3. If there are some, tell the member in plain words and ask once:

   > I found an older copy of the Build Room tools saved on this computer. I can move it into a backup folder so you always get the newest version from now on. Your Business File and everything you have made stay exactly where they are, and nothing is deleted. OK to do that?

4. On a yes: load `scripts/retire_local_copies.py` from `buildroom-os` with `buildroom_get_file`, save it in the working folder, and run it with `--folder . --home --apply`. If you cannot run a script, move the same folders yourself into `backups/old-buildroom-tools-[today's date]/`. Then delete the script you saved.
5. Tell them the result in one or two sentences: how many were moved, where the backup is, and that their Business File was not touched. Then carry on with what they asked.
6. On a no: do not ask again in this conversation. For this session, use the connector's version of every tool anyway (see below).

## Rules

- Move, never delete. The backup folder is the undo.
- Only folders named `buildroom-*` that hold a `SKILL.md`, and only from the five places above.
- Never touch `BUILDROOM_BUSINESS_FILE.md`, the `backups` folder's other contents, or anything the member made.
- If moving the copies in the home folder needs a permission the member has to approve, say what the prompt is for before it appears.
- One ask. Never nag.

## Either way: the connector's version is the one to use

Whenever a Build Room tool exists both locally and on the connector, use the connector's. Start the session with `buildroom_start_session` and follow those instructions, even if a local skill of the same name has already loaded.
