# Logins and private codes — keeping them safe without scaring anyone

## What you say to them

Only this, when a code is actually needed:

> *"This one needs a private code from [Service]. I'll walk you through it — three clicks.*
> *1. Open this link: [exact URL]*
> *2. Click [exact button name]*
> *3. Copy the long code it shows you and paste it here.*
> *I'll lock it in your computer's vault right away — I won't keep it in any file, and it never leaves this machine."*

After they paste it:
> *"✅ Locked in your computer's vault. Testing it… ✅ working."*

Then **never** repeat the value back, not even partially.

## What you actually do

1. Prefer a built-in connector so **no code is needed at all**. Always check that first.
2. If a code is needed, store it in the machine's own vault:
   - macOS: `security add-generic-password -a "$USER" -s CC_<NAME> -w`
   - Windows: Credential Manager (`cmdkey`) or a user-scoped environment variable
   - Linux: `secret-tool store --label="Control Center" service control-center key CC_<NAME>`
3. Fallback only if the vault isn't available: `~/control-center/.env`, permissions `600`, already listed in `.gitignore`.
4. Record in `config/credentials.md` the **name, what it's for, when it was made, and the link to shut it off** — never the value.
5. Ask for the smallest permission that works. Read-only if reading is enough.
6. Test it with one harmless read. Report pass/fail only.
7. If it fails, don't ask them to re-read it to you — send them back to regenerate a fresh one. *"That one didn't take. Grab a fresh one from the same page — 20 seconds."*

## The "lost laptop" card
Fill `config/revoke.md` with one shut-off link per service, and tell them in one line at handoff: *"If you ever lose this computer, open ~/control-center/config/revoke.md — every off-switch is in there."*
