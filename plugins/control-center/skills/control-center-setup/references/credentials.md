# Credentials

## Rules
1. A secret is never typed into chat, a file in a repo, a commit message, or a screenshot.
2. Preferred store: the OS keychain (macOS Keychain, Windows Credential Manager, `secret-tool` on Linux).
3. Acceptable fallback: `~/control-center/.env`, mode `600`, listed in `.gitignore`.
4. The operator creates every key in their own account. Never share a key between people.
5. Scope keys to the minimum: read-only where reading is enough.
6. Record in `config/credentials.md` only the **name, purpose, scope, created date, and revoke URL** — never the value.

## Storing
macOS: `security add-generic-password -a "$USER" -s CC_OPENAI_KEY -w`
Windows: `cmdkey` / Credential Manager, or a user-scoped environment variable.
Linux: `secret-tool store --label="CC key" service control-center key CC_OPENAI_KEY`
Fallback: `printf 'NAME=value\n' >> ~/control-center/.env` typed by the operator, not by you.

## Verifying
Test every key with one read-only call and report only pass/fail. If a key fails, have the operator regenerate it — do not ask them to paste it into chat to "check it".

## Revoking
Keep a `config/revoke.md` with a one-line revoke URL per provider so the operator can kill everything in five minutes if a laptop is lost.
