# The ledger — gates, spend and every paid job

The founder's warning from the 2026-09-16 session: you can spend a lot of money really fast by accident. The ledger is how the studio cannot. Adapted from the job ledger in the `create-ads-with-agents` skill (see `source-credit.md`).

`scripts/ledger.py` (shared with the Video Director; its source is `buildroom/shared/media/`) keeps one `project.json` per cycle in the member's ads folder (never inside the skill). It is local, makes no network calls and submits nothing. It records:

- the gates G0–G2 for the cycle and G3–G4 per ad, and who passed them (a G3/G4 pass from the author is refused);
- the spend cap per provider, in the provider's own units, with where the member approved it;
- every planned plate, every paid job with its quote, provider job id, result file and actual charge;
- every ad: its spec, rendered files with a checksum (sha256) of each, repairs (ceiling two by default) and the member's approval.

## The rules it enforces

1. **No paid call before G0, G1 and G2 pass, the mode is live, and a cap is authorised.**
2. **Reserve before you submit.** A job key is reserved with its quote; the reservation is refused if it would exceed the cap.
3. **Mark submitting right before the call; record the provider's job id right after.**
4. **One open job per plate.** A plate with a reserved, submitting, pending or unknown job cannot get another until it is reconciled.
5. **Uncertain means unknown, not failed.** A timeout or server error is recorded `unknown` and must be reconciled from the provider's records before any retry. A lookup that fails is not proof that nothing was submitted.
6. **A quote is not a receipt.** The committed total counts held quotes until the actual charge is recorded with evidence. Failed jobs may still be billed; their reservation stays until the account shows otherwise.
7. **Changed files are reviewed again.** New renders reset G3/G4 and the member's approval for that ad. So does a repair. "New" means the contents, not only the names: see below.
8. **The kit needs everything:** every ad rendered, G3 and G4 passed by the reviewer, approved by the member, every plate it uses completed, no uncertain jobs, and every file it ships unchanged since it was recorded for review.

## How a changed file is caught (rule 7)

`ledger.py ad --renders …` stores a sha256 checksum of each file beside the file list (`render_sha256` in the ad's entry). Paths are read relative to the ledger's folder (or the current folder if the file is not there), or as given when absolute.

- **Record the renders again after any re-render, even under the same file names.** If any checksum differs, a file was added or removed, or the list changed, the ledger sets G3 and G4 back to unverified, removes the member's approval, and says which files changed under `notices` in its output. Recording the same unchanged files again changes nothing.
- **A file that cannot be read** is recorded with no checksum, and the output says so. It counts as changed the next time, and the kit refuses it until it is recorded again.
- **The kit builders check again.** `review_pack.py kit` and `review_video.py kit` recompute the checksum of every file they are about to ship. A file that no longer matches is refused: "changed since it was reviewed; record it again and re-review". So is a file that was never recorded for that ad.
- **Older ledgers keep working.** An ad recorded before checksums existed has none. The first time its renders are recorded again with the same file list, the checksums are stored and nothing is reset (the output says they were recorded for the first time). Until then the kit still builds, and says it could not confirm those files are the ones that were reviewed.

The ledger's schema name is unchanged (`buildroom-media/1`); the checksums are an added field.

## Typical sequence

```sh
S=.claude/skills/buildroom-ad-studio/scripts     # or .codex/skills/... ; resolve the real path
P=ads/2026-10/project.json
python3 $S/ledger.py init $P --cycle 2026-10
python3 $S/ledger.py gate $P --gate G0 --verdict pass --by producer --ref ads/2026-10/brief.md
python3 $S/ledger.py gate $P --gate G1 --verdict pass --by producer --ref ads/2026-10/concepts.md
python3 $S/ledger.py gate $P --gate G2 --verdict pass --by member --ref ads/2026-10/copy-manifest.json   # the member's sign-off; refused otherwise (demo mode excepted)
python3 $S/ledger.py plan $P --asset-id PLATE-C2 --provider higgsfield --model <resolved id> --prompt-ref ads/2026-10/plates/C2.prompt.txt
python3 $S/gen.py --dry-run ads/2026-10/jobs.json --prices ads/2026-10/prices.json     # show the member
python3 $S/ledger.py authorize $P --provider higgsfield --cap 12 --units credits --note "member approved quote in session 2026-10-14"
python3 $S/gen.py ads/2026-10/jobs.json --project $P --prices ads/2026-10/prices.json
node $S/render_static.mjs ads/2026-10/specs/*.json --out ads/2026-10/renders --overlay --ratios 1x1,4x5,9x16
python3 $S/ledger.py ad $P --ad C2-H1 --concept C2 --layout photo-hook --spec ads/2026-10/specs/C2-H1.json --renders <the three pngs> --assets PLATE-C2
python3 $S/review_pack.py sheet --renders ads/2026-10/renders --manifest ads/2026-10/copy-manifest.json --out ads/2026-10/review
#   → separate reviewer → ledger.py gate --ad … --gate G3/G4 --by reviewer
python3 $S/ledger.py approve $P --ad C2-H1 --note "member approved in session"
python3 $S/review_pack.py kit --project $P --renders ads/2026-10/renders --manifest ads/2026-10/copy-manifest.json --out ads/2026-10/kit
#   video ads: the Video Director builds its own kit beside this one, with --out ads/2026-10/kit-video
```

## Interactive generation through the Higgsfield MCP

When plates are made through the Higgsfield MCP tools instead of `gen.py`, keep the same discipline by hand: `reserve` with the quote the tool shows, `record --status submitting`, call the tool, `record --status pending --job-id <id>`, then `completed --result <saved file>`. Never call a paid tool without a reservation.

## Recovery

`gen.py --resume --project P` polls every pending or unknown job that has a provider job id and finishes it. A job left `submitting` or `unknown` with no job id needs a look at the provider's dashboard: record `pending --job-id` if it exists, or `no_submission --evidence "…"` if it does not. Then, and only then, a new key for a retry.
