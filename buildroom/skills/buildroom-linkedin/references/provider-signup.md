# Provider sign-up, keys and the affiliate disclosure

Shared by the Ad Studio and the Video Director (source: `buildroom/shared/media/provider-signup.md`; the build copies it into each skill's `references/`). Edit the shared copy only.

## The disclosure, every time

Whenever a session offers a provider through the Build Room's referral link, the same sentence sits right next to the link, word for word:

> *This is my affiliate link. If you sign up through it, I earn a commission, at no extra cost to you.*

The plain sign-up route is always offered too. A member who already has an account skips the link and adds their key.

## The providers

| Provider | Used for | Sign-up (affiliate) | Plain route | Key(s) in `.env` |
|---|---|---|---|---|
| **Higgsfield** (default) | Image plates, video B-roll and scenes; interactive work through its MCP | https://higgsfield.ai?fpr=lanny-756d90 | higgsfield.ai | `HIGGSFIELD_API_KEY`, `HIGGSFIELD_API_SECRET` |
| **Kie.ai** | Pay-as-you-go images and video, no subscription | https://kie.ai?ref=62126a8991d5546179db893d9bc15a7c | kie.ai | `KIE_API_KEY` |
| **SubMagic** | Captions after the video is assembled (styled, animated, word-accurate) | https://submagic.co/?via=harrison22 | submagic.co | `SUBMAGIC_API_KEY` |
| **HeyGen** | The member's consented avatar twin, for scale variants only | — (no referral link) | heygen.com | `HEYGEN_API_KEY` |

Not routed: **fal.ai** (founder decision, 2026-10-14). Never used: **Sora** (discontinued in 2026).

## Keys

1. "Create an API key in your account settings and paste it into the `.env` file in this folder, on its own line, like `KIE_API_KEY=...`. Don't paste it here."
2. Never print, echo, log or repeat a key. The scripts read `.env` themselves and redact keys from anything they print.
3. Run the script's `--probe` once after adding a key. It makes one harmless call and says whether the key works.

## Interactive Higgsfield

Offer the Higgsfield MCP for interactive work (it handles sign-in and uploads local reference files): in Claude Code, `claude mcp add --transport http higgsfield https://mcp.higgsfield.ai/mcp`; in Codex, the same URL in its MCP settings. Paid calls made through the MCP still go through the ledger by hand: reserve, submitting, call, pending with the job id, completed with the saved file.

## Terms to verify

Commission rates and member discounts change. Confirm each program's current terms before quoting a percentage or discount to a member. Never promise a discount the provider does not show.
