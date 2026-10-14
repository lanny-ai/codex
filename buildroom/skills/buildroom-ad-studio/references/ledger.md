# The ledger — gates, spend and every paid job

The founder's warning from the 2026-09-16 session: you can spend a lot of money really fast by accident. The ledger is how the studio cannot. Adapted from the job ledger in the `create-ads-with-agents` skill (see `source-credit.md`).

`scripts/ledger.py` keeps one `project.json` per cycle in the member's ads folder (never inside the skill). It is local, makes no network calls and submits nothing. It records:

- the gates G0–G2 for the cycle and G3–G4 per ad, and who passed them (a G3/G4 pass from the author is refused);
- the spend cap per provider, in the provider's own units, with where the member approved it;
- every planned plate, every paid job with its quote, provider job id, result file and actual charge;
- every ad: its spec, rendered files, repairs (ceiling two by default) and the member's approval.

## The rules it enforces

1. **No paid call before G0, G1 and G2 pass, the mode is live, and a cap is authorised.**
2. **Reserve before you submit.** A job key is reserved with its quote; the reservation is refused if it would exceed the cap.
3. **Mark submitting right before the call; record the provider's job id right after.**
4. **One open job per plate.** A plate with a reserved, submitting, pending or unknown job cannot get another until it is reconciled.
5. **Uncertain means unknown, not failed.** A timeout or server error is recorded `unknown` and must be reconciled from the provider's records before any retry. A lookup that fails is not proof that nothing was submitted.
6. **A quote is not a receipt.** The committed total counts held quotes until the actual charge is recorded with evidence. Failed jobs may still be billed; their reservation stays until the account shows otherwise.
7. **Changed files are reviewed again.** New renders reset G3/G4 and the member's approval for that ad. So does a repair.
8. **The kit needs everything:** every ad rendered, G3 and G4 passed by the reviewer, approved by the member, every plate it uses completed, no uncertain jobs.

## Typical sequence

```sh
S=.claude/skills/buildroom-ad-studio/scripts     # or .codex/skills/... ; resolve the real path
P=ads/2026-10/project.json
python3 $S/ledger.py init $P --cycle 2026-10
python3 $S/ledger.py gate $P --gate G0 --verdict pass --by producer --ref ads/2026-10/brief.md
python3 $S/ledger.py gate $P --gate G1 --verdict pass --by producer --ref ads/2026-10/concepts.md
python3 $S/ledger.py gate $P --gate G2 --verdict pass --by producer --ref ads/2026-10/copy-manifest.json
python3 $S/ledger.py plan $P --asset-id PLATE-C2 --provider higgsfield --model <resolved id> --prompt-ref ads/2026-10/plates/C2.prompt.txt
python3 $S/gen.py --dry-run ads/2026-10/jobs.json --prices ads/2026-10/prices.json     # show the member
python3 $S/ledger.py authorize $P --provider higgsfield --cap 12 --units credits --note "member approved quote in session 2026-10-14"
python3 $S/gen.py ads/2026-10/jobs.json --project $P --prices ads/2026-10/prices.json
node $S/render_static.mjs ads/2026-10/specs/*.json --out ads/2026-10/renders --overlay
python3 $S/ledger.py ad $P --ad C2-H1 --concept C2 --layout photo-hook --spec ads/2026-10/specs/C2-H1.json --renders <the three pngs> --assets PLATE-C2
python3 $S/review_pack.py sheet --renders ads/2026-10/renders --manifest ads/2026-10/copy-manifest.json --out ads/2026-10/review
#   → separate reviewer → ledger.py gate --ad … --gate G3/G4 --by reviewer
python3 $S/ledger.py approve $P --ad C2-H1 --note "member approved in session"
python3 $S/review_pack.py kit --project $P --renders ads/2026-10/renders --manifest ads/2026-10/copy-manifest.json --out ads/2026-10/kit
```

## Interactive generation through the Higgsfield MCP

When plates are made through the Higgsfield MCP tools instead of `gen.py`, keep the same discipline by hand: `reserve` with the quote the tool shows, `record --status submitting`, call the tool, `record --status pending --job-id <id>`, then `completed --result <saved file>`. Never call a paid tool without a reservation.

## Recovery

`gen.py --resume --project P` polls every pending or unknown job that has a provider job id and finishes it. A job left `submitting` or `unknown` with no job id needs a look at the provider's dashboard: record `pending --job-id` if it exists, or `no_submission --evidence "…"` if it does not. Then, and only then, a new key for a retry.
