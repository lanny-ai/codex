# Vault Protection Architecture

The core non-negotiable design principle of every watcher this skill generates: **the member's proprietary thinking is protected from any contamination by external content**.

This document defines the architecture and rules every generated watcher must follow.

---

## The Four Pillars of Protection

### Pillar 1: Folder Isolation

External content lives ONLY in a dedicated top-level folder. Default: `/External`.

Structure:
```
[Vault Root]/
├── (member's existing notes — UNTOUCHED)
├── (member's proprietary work — UNTOUCHED)
└── /External/                          ← All watcher output goes here
    ├── /Podcasts/
    │   ├── /2026-06/
    │   │   ├── 2026-06-15 - Tim Ferriss - Naval on Wealth.md
    │   │   └── ...
    │   └── /2026-07/
    ├── /YouTube/
    │   ├── /2026-06/
    │   └── ...
    ├── /Twitter/
    ├── /Newsletters/
    └── ...
```

**Hard rule:** The watcher's `obsidian_writer.py` module has ONE write path: `[vault_root]/External/[source_type]/[YYYY-MM]/[filename].md`. No other paths are written to. Ever.

**Validation:** The watcher code includes a path safety check that REFUSES to write anywhere outside `/External`.

---

### Pillar 2: Read-Only Vault Access

The watcher NEVER reads from the member's existing notes. It only writes new files.

**What this means in code:**
- No `os.walk()` over the vault root
- No reading existing markdown files
- No "find similar notes" features
- No backlink generation across existing notes
- The watcher's Python code has no function that opens any file outside `/External`

**What gets enforced:**
```python
def safe_write_path(vault_root: Path, source_type: str, date: str, filename: str) -> Path:
    """The ONLY way the watcher writes files. Hardcoded to /External."""
    external = vault_root / "External" / source_type / date
    external.mkdir(parents=True, exist_ok=True)
    return external / filename

# No reading function exists.
# No alternative write function exists.
```

---

### Pillar 3: Tag-Based Identification

Every note written by the watcher includes these YAML frontmatter tags:

```yaml
tags:
  - external
  - source/podcast      # or /youtube, /twitter, etc.
  - unprocessed         # signals "external content, not yet integrated"
```

Plus the source-specific tags extracted from the content.

**Why "unprocessed":**
This tag lets the member easily query "everything I haven't yet integrated into my own thinking" using Obsidian's tag search. When they decide to integrate something, they remove `unprocessed` and replace with `integrated` (or similar).

**Recommended member-side conventions** (suggested in the README, never enforced):
- `#my-thinking` on the member's own notes
- `#proprietary` on synthesis and original work
- `#integrated` when external content has been folded into proprietary thinking

But the watcher only enforces its OWN tags. It doesn't require the member to tag their existing work.

---

### Pillar 4: Manual Promotion Pattern

When external content becomes important enough to integrate, the member MANUALLY moves the file out of `/External` into their main vault.

This is the "safe promotion" pattern:

```
/External/Podcasts/2026-06/[some-episode].md
         ↓ (member drags file out manually)
[Vault Root]/My Notes/Naval on Wealth - Integrated.md
         ↓ (member adds their own thinking, links to their own notes)
File is now proprietary. Watcher will never touch it.
```

**Why this is safe:**
- Promotion is a conscious act
- The watcher has no awareness of files outside `/External` (per Pillar 2)
- Once moved, the file is no longer at the path the watcher writes to, so future runs won't overwrite it
- If the member wants the original external version preserved, they copy instead of move

---

## What This Protects Against

### Scenario 1: Watcher overwrites member's work
**Prevented by:** Pillar 1 (folder isolation). The watcher can only write to `/External/`.

### Scenario 2: External content gets linked into member's notes via auto-backlinks
**Prevented by:** Pillar 2 (read-only access). The watcher doesn't scan existing notes, so it has no knowledge of them to generate backlinks against.

### Scenario 3: Member can't tell what's their thinking vs. AI-curated external
**Prevented by:** Pillar 3 (tag-based identification). Every external note is clearly tagged.

### Scenario 4: External content "creeps" into proprietary notes through editing
**Prevented by:** Pillar 4 (manual promotion). External content stays external until the member makes a conscious choice to integrate.

---

## What's Allowed

The member can:
- Use Obsidian's link syntax `[[Topic]]` inside external notes — links resolve to other external notes by default
- Manually move/copy/edit external notes once they're written
- Promote external notes by moving them out of `/External`
- Add their own notes/comments to external files (their edits won't be overwritten because the watcher uses GUIDs to dedupe and won't rewrite existing notes)
- Customize the folder name from `/External` to something else (e.g., `/Inbox`, `/Feeds`, `/Raw`)

The watcher allows all of this without compromising safety.

---

## What's NOT Allowed (Watcher Behavior)

The watcher will NEVER:
- Read any file outside `/External`
- Write any file outside `/External`
- Modify or delete existing files in `/External` once written (only creates new files)
- Generate backlinks to the member's existing proprietary notes
- Suggest connections between external and proprietary content
- Auto-tag or auto-modify the member's proprietary notes
- Move files between folders
- Run cleanup or "consolidation" operations on the vault

---

## Code-Level Enforcement

In every generated watcher, the `obsidian_writer.py` module includes this safety check:

```python
from pathlib import Path

def write_to_vault(episode_data, knowledge, score, vault_root_path):
    """
    Write to vault. ENFORCES /External path safety.
    """
    vault_root = Path(vault_root_path).resolve()
    
    # SAFETY: only write to /External subtree
    external_base = vault_root / "External"
    external_base.mkdir(exist_ok=True)
    
    # Build the target path
    target_dir = external_base / SOURCE_TYPE / date_subfolder
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    
    # SAFETY: verify the resolved path is still under /External
    if external_base not in target_path.resolve().parents:
        raise SecurityError(
            f"Refusing to write outside /External. "
            f"Attempted path: {target_path}"
        )
    
    # SAFETY: never overwrite existing files
    if target_path.exists():
        print(f"Skipping (already exists): {target_path.name}")
        return target_path
    
    target_path.write_text(markdown_content, encoding='utf-8')
    return target_path
```

This check happens on every write. If the path escapes `/External`, the watcher refuses to write.

---

## Why This Matters

A knowledge base is only as valuable as the proprietary thinking inside it. If external content can contaminate or overwrite the member's original work, the system creates more anxiety than value.

This architecture makes the watcher SAFE to leave running unattended. The member can configure it once and let it run for years without ever worrying that it will damage their accumulated thinking.

That safety is what makes the system actually usable, not just demoable.
