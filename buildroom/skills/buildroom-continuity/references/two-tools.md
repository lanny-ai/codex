# Two tools on one project

For a project where Claude and Codex each handle part of the work. One project in one tool needs none of this.

**The rule: every file that changes has exactly one owner. Two tools never write the same file.**

```
projects/<short-name>/
  continuity/
    PROJECT.md      shared; both read it; one tool owns edits (say which in the file)
    DECISIONS.md    shared; added to by both, never rewritten, so neither overwrites the other
  claude/
    STATE.md        Claude's focus and next action; only Claude writes here
  codex/
    STATE.md        Codex's focus and next action; only Codex writes here
  shared/           finished work handed from one tool to the other; read only for the tool that did not make it
```

How to run it:

1. In `PROJECT.md`, write who owns what ("Claude: words and content. Codex: the build.").
2. Tell each tool its folder: "This is a two-tool project. You own the `claude/` folder. Read PROJECT and DECISIONS, keep your own STATE current, put only finished work in `shared/`, and never edit the other tool's folder."
3. A finished piece moves to `shared/` with a one-line DECISIONS entry saying what was handed over and when.
4. Keep the project under git, committing at each hand-off. If both tools must change the same files at the same time, give each its own branch and merge on purpose.

The Business File is read by both and written by neither.
