# Build Room OS releases

Dated copies of the member zip, so members can download by link. Each is the output of `build-universal-bundle.sh` at the commit it was added. Keep only the current one plus the previous one.

| File | Built | What changed |
|---|---|---|
| `BuildRoom_OS_2026-11-04.zip` | 2026-11-04 | Thirty-six skills. **Safe updates:** the zip no longer carries a Business File (only a blank template in `templates/`), so unzipping a release can never replace a member's filled-in file; new `update.sh` / `update.ps1` replace only the toolkit, back up everything they replace and prove the Business File unchanged; every skill now starts from the member's current file, never the blank template. **New:** the Continuity System from community member Jenn ("Set up the continuity system for this project"), which reads the Business File and never writes it. Includes the 2026-10-31 finishing crew (Triage, Finish It, Build It); the 2026-10-31 zip was never posted and is replaced by this one. |
| `BuildRoom_OS_2026-10-28.zip` | 2026-10-28 | Thirty-two skills: the Search & Answer Engine ("Get found on Google"): found and cited in Google, Maps, YouTube and AI answers without ads, on October 2026 research and the founder's OS Cortex AEO method; the Business Profile scored (rank items before buyer items), a rated question map, one honest answer page a week through a gate, the review loop under Google's policy and the FTC rule, five free listings, publishing by API where the builder has one (WordPress, Webflow, Shopify, Wix) and a paste checklist where it does not, IndexNow and a live-page check, a monthly citation check; Business File spec 1.6 adds §21; the printable guide gains page 6. Rebuilt 2026-10-31 from the read-through fixes (progress view to §21, File version 1.6, neutral Brainstorm Board placeholder); contents otherwise unchanged. |

Download link pattern: `https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/releases/<file>`.
