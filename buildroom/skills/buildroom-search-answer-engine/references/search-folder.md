# The search folder

`search/` sits next to the Business File (inside the Obsidian vault when the member keeps one). Scripts run from the folder that holds the Business File: `python3 <skill>/scripts/question_map.py …`.

| File | Written by | Holds |
|---|---|---|
| `questions.json` | `question_map.py` | every question: id, question, slug, cluster, intent, source, scores, status, published URL and dates |
| `question-map.md` | `question_map.py md` | the readable map: next to answer, the ranked table, clusters and hub readiness, retired questions |
| `answers/<slug>.md` | the session, through `answer_check.py new` and `check` | one answer page per question, front matter plus body (`answer-standard.md`) |
| `answers/<slug>.jsonld` | `answer_check.py schema --out` | the optional Article and breadcrumb markup to paste into the builder |
| `answers/<slug>.html`, `answers/<slug>-paste.md` | `publish.py render` or `publish --builder manual` | the rendered page and the ten-minute paste checklist for builders with no API |
| `<key>.txt` | `publish.py indexnow-key` | the IndexNow key file the member uploads to the site root |
| `../.env` | the member | the builder and IndexNow keys, read by `publish.py`, never printed, never copied anywhere |
| `site.md` | the session (Phase 0, then as things change) | builder, domain, editors, verification dates, sitemap, crawler settings, Cloudflare, About page, service pages, workarounds |
| `profile.json` | `profile_tracker.py` | the Business Profile record, the activity log (photos, posts, asks, reviews, replies, updates) and the listings |
| `profile-check.md`, `profile-report.md` | `profile_tracker.py check --md`, `report --md` | the scored checklist and the monthly numbers |
| `checks/YYYY-MM.json` | `citation_check.py` | the month's prompts and logged results |
| `checks/YYYY-MM-prompts.md`, `checks/YYYY-MM-report.md` | `citation_check.py prompts`, `report --md` | the checklist to run and the month's report |
| `mentions.md` | the session | one line per mention asked for or earned: date, who, what, result |
| `robots.txt` | `answer_check.py robots --out search/robots.txt` | the crawler file to upload, or to compare against the builder's setting (`robots --check` reads the live one) |

Rules: no client or patient names anywhere in the folder except inside a consented proof entry copied by ID from `proof/` into an answer page (the Proof Engine keeps the words and the permission; this folder never holds review text or a reviewer's name of its own); `profile.json` holds ratings and dates, never who said what; `questions.json` and `profile.json` are edited by the scripts, not by hand; a page is never deleted from `answers/`, it is marked `needs-update` or its question `retired`.
