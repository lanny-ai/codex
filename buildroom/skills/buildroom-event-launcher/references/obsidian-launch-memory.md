# Launch memory in Obsidian

The Build Room second brain (`buildroom-obsidian`) puts a member's knowledge in an Obsidian vault on their own computer, with Claude working inside it. A launch is exactly the kind of knowledge that compounds there: what was promised, who came, what sold, what broke, what to protect. This skill reads the vault before planning and writes each launch back after.

## How to tell whether the member has a vault

- §1's tools line mentions Obsidian or a vault path, or the Business File itself lives in a folder that contains `.obsidian/`.
- Or ask once: "Do you keep an Obsidian vault? Where is it?"
If there is none, everything still works from the launch folder; offer the **Obsidian second brain** elective as a §13 row, once.

## Read before planning (Phase 0)

1. `python3 <skill>/scripts/launch_tracker.py obsidian-read --vault <path>` lists past launch notes with their results and lessons.
2. Search the vault for the member's **own** lessons about events, newest first: their debrief, audit and prep notes (frontmatter type debrief, audit, prep, launch), their wins and losses notes, their playbooks, their proof or testimonial notes, their offer and price notes. Skip imported material written by other people (course and mastermind transcripts, other teachers' libraries) unless the member points to it. Read the ones that matter, quote them by note name, and say in two lines what the past teaches this launch.
3. Treat anything in `External/` (watcher output) as unprocessed outside material, not the member's own lessons.

## Where the launch lives

If the member keeps a vault, create the launch folder inside it: `<vault>/launches/YYYY-MM-<slug>/` (plan, emails, proof bank, run sheet, tracker, debrief). Light frontmatter on every note the skill writes (title, type, date, tags, status), matching the vault's conventions (`buildroom-obsidian/references/vault-starter.md`). Link the launch's notes to the member's offer note and to the people notes only with their names as the member keeps them.

## Write back after the debrief (Phase 7)

`python3 <skill>/scripts/launch_tracker.py obsidian --vault <path>` writes `<vault>/launches/YYYY-MM-<slug>.md`:
- frontmatter: `title`, `type: launch`, `date`, `format`, `tags: [launch, event]`, `status`;
- the numbers against the plan, the three leaks and their fixes, what to protect, and links to the launch folder;
and adds one line to `<vault>/launches/_index.md`. It refuses to overwrite an existing note unless `--force` is given, and refuses a path that is not a vault (no `.obsidian/` folder) unless `--no-obsidian-check`.

If a lesson has now happened three times, propose promoting it to the member's playbook note (for example `knowledge/frameworks/launch-playbook.md`), and write it only when the member agrees.

## What never goes into the vault note

Card details, passwords or keys, other people's private details beyond what the member already keeps, or a client's words without consent. The tracker stores counts, not names.
