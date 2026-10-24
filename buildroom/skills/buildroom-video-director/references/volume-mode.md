# Volume mode: a content series, and the Video Engine zip

Volume mode is for members who want many videos a week: a content series made in batches. It replaces the old Video Engine elective, whose durable lessons live here. Read it only for the content playbook's series work or when a member brings the Video Engine zip.

## The money gate (say it first, every time)

Volume costs money and attention. As stated in the 2026-05-20 Video Engine session: about $100–150 a month at one video a day, $200–325 at three to five a day. "If this money makes a difference for you… please don't do this." Most members' first win is one great video a week, not three a day. Ask once whether they want to proceed; do not push.

## The director's batch mode (the default)

1. **The series plan (once a month).** From §2 pains and objections, §4 villain and differentiator, and §14: three or four topic pillars; 8–20 titles, each with its hook, structure (`story-structures.md`, content), and soft ask. The keyword call to action works well here: "Comment GUIDE and I'll send it" (the CRM listens for the keyword, captures the contact and delivers the free thing; GoHighLevel can do this). Approve the list, not each video.
2. **Scripts, one at a time** through Kern, approved individually (the house rule holds even in volume).
3. **One batch shoot.** One 30–45 minute session films the A-roll for the month: same outfit, same light, a teleprompter with every script, three takes of every hook (`shoot-list.md`).
4. **Batch edit.** One `edit.json` per video from a series template (same brand cue, end card, caption template, music bed); `assemble_video.py` per video.
5. **Captions** with the series' SubMagic template or the burned style.
6. **Review every video.** The machine checks run on all of them; the reviewer reviews every final (it can take the contact sheets in one pass); the member watches each before approval. Volume never skips review.
7. **Kits by week**, named so results join back to each video.
8. **Scale variants (optional).** Once a script has proven itself, new hooks on the same body can be made with the member's consented avatar twin (`video-router.md`): new hooks only, never a testimonial, never the first video in a series.

A routine can draft next week's scripts from the series plan (opt-in, like the Weekly Ops routine): it drafts, applies nothing, spends nothing, and the member approves on their next session. No routine posts or spends.

## The Video Engine zip (members who have it)

The engine is a separate Claude Code project shipped as a zip on the members' Drive: research → script → avatar video → B-roll and stills → FFmpeg composite → captions → an MP4 in a local folder, on a schedule. This skill does not contain it. Without the zip: "There's no magic that … will get around the you-don't-download-the-zip-file part of the process."

Install, as taught:

1. Make an empty local folder (not in Google Drive), open a Claude Code or Codex session on it.
2. Add the zip and say **"install this."** Say yes to creating `.env` from its template and to installing FFmpeg and Python (on Windows also Git and PowerShell; `winget install ffmpeg`).
3. Paste keys into `.env` as `VARIABLE=value`, no spaces. Read the variable names from the zip's `.env.template`; never guess them. Never print a key back.
4. Run once. A missing key trips it: name the empty variable, not its value.
5. Schedule in one sentence: "run this three times a day at 9am, noon and 3pm." Confirm the mechanism (cron, launchd, a scheduled task) and where the videos land.
6. Upgrade: add the new zip in the same session and say "here's the upgraded version."

The zip's own pipeline uses Pexels and fal.ai for B-roll and stills and HeyGen or Hedra for the avatar. The Build Room's routed providers are Higgsfield and Kie.ai (fal.ai is not routed; `provider-signup.md`); a member who prefers them can ask the session to swap that step. Either way, the Build Room rules apply to anything the engine makes: no synthetic person presented as a customer, the avatar twin only with written consent, captions and claims checked before posting, the member watches before posting.

The feedback loop: put each good script in the engine's winning-scripts folder, keep the business knowledge base current (without it the scripts are "generic, crappy stuff"), refresh the platform knowledge base. "A starting point, not a finishing point."

The durable lesson under all of it: Claude Code as the orchestrator, APIs as superglue, keys in one `.env` file. "Whether you're going to use this process or not is kind of irrelevant, because the skill set of doing it is really, really powerful."
