# Images: the member's photos first, Kie.ai for the rest

## The order of choice

1. **The member's own photos**: the founder, their place, their work, their real clients (with consent on file in §18). Real people get looked at; generic stock gets skipped [data, NN/g].
2. **Kie.ai-generated images** for what's missing: scenes, places, objects, textures, backgrounds and hands at work. Kie.ai is the provider Build Room already recommends (Ad Studio, Video Director).
3. **Licensed stock** only when the member already pays for it, with the licence noted.
4. **Never:** a taste-vault reference, a photo from someone else's site, or an image of unknown origin.

**Never generate a real person.** Don't generate the member, a client or any identifiable person as if photographed. Likeness law applies whatever a tool's terms say, and Kie's terms don't address likeness (unconfirmed). The only exception is a consented avatar or likeness on file in §18/§19, used the way those skills allow. Anonymous figures (seen from behind, hands, far away) are fine.

## Setting up Kie.ai (once)

`references/provider-signup.md` has the sign-up link and steps. In short:
- Make an account at kie.ai and buy a small credit pack. About 1 credit is about $0.005; failed jobs aren't charged.
- Create an API key and put it in the `.env` file in the vault root as `KIE_API_KEY=…`. Never paste it in the chat, and never print it.
- `python3 <skill>/scripts/gen.py --probe --provider kie` makes one harmless call (the credit balance) to prove the key works.

## Each batch of images

The shared media toolkit does the paid work (`gen.py` and `ledger.py`, the same copies as Ad Studio and Video Director). Its messages talk about "ads" and "concepts": read them as "the page" and "the images". `render_static.mjs` ships with the toolkit for the Ad Studio and isn't used here. Nothing is generated without the member's yes on the list and the cost.

**Work in one folder:** `Design/landing-page/images/`. Every path below is relative to it.

1. **The list** (`list.md`). For each image:
   - an ID (`IMG-HERO`, `IMG-PLACE`, …) and where it goes
   - the prompt, in `<id>.prompt.txt`
   - the shape: 16:9 for a hero, 4:5 for a side photo, 1:1 for a small one
   - "person: no"

   Prompts describe the member's world in plain, specific words. Name the photo treatment from the system (natural, warm or mono), and say "no text, no logos, no watermark". Never write "in the style of" a living artist or a reference site.
2. **Prices and model IDs, read from Kie.ai** before the batch. They change often, and model ID formats vary, so never hard-code them. Write `prices.json` with the date and the source (the format is in `gen.py --help`), then `jobs.json` with one job per image (`kind: image`, `out: ../page/img/<file>`).
   - Rule of thumb [practitioner]: most images cost $0.01–0.12. Three directions with 3–6 images each is usually well under $2 on a mid-tier model.
   - **In demo mode** there are no real prices. Write `prices.json` with `"source": "demo — not real prices"` and say so.
3. **The quote:** `python3 <skill>/scripts/gen.py --dry-run jobs.json --prices prices.json` prints each request and the total. Show the member the list and the total in credits and dollars.
4. **The ledger and the member's yes,** in this order, only after the member has seen the quote:
   ```
   ledger.py init      project.json --cycle <YYYY-MM>            (add --mode demo for a walkthrough: no paid calls)
   ledger.py gate      project.json --gate G0 --verdict pass --by producer --ref ../design.json
   ledger.py plan      project.json --asset-id IMG-HERO --provider kie --model <resolved id> --prompt-ref IMG-HERO.prompt.txt --kind plate
   ledger.py gate      project.json --gate G1 --verdict pass --by reviewer --ref list.md
   ledger.py gate      project.json --gate G2 --verdict pass --by member --ref "member approved the list and the quote of N credits, <date>"
   ledger.py authorize project.json --provider kie --cap <the quoted credits plus a small allowance> --units credits --note "…"
   gen.py jobs.json --project project.json --prices prices.json      (reserve, submit, poll, download)
   ```
   - Use one `plan` per image, and `--kind plate` for every still image.
   - **G0** is the design brief. **G1** is your review of the prompts: no real person, no reference copied, no text in the image.
   - **G2** is the member's yes, and only the member can give it. The ledger's wording for G2 talks about approved ad words; here it means the approved image list and quote.
5. **Save each image into the vault straight away.** Kie keeps files for about 14 days and download links expire in about 20 minutes (from the 4o Image docs; unconfirmed for every model). `gen.py` downloads to each job's `out` path at once.
6. Compress for the web: about 200 KB per photo, WebP or JPEG, at most 2400px wide for a full-width hero.

## images.json: where every picture came from

Keep `Design/landing-page/images.json` next to the page. `design_check.py --images` reads it.

```json
{"images": [
  {"file": "page/img/hero.jpg", "source": "own", "person": true, "consent": "founder's own photo"},
  {"file": "page/img/porch.jpg", "source": "kie", "person": false, "ledger_key": "2611.IMG-PORCH.r0"},
  {"file": "page/img/desk.jpg", "source": "licensed", "licence": "member's Adobe Stock plan, 2026-11"}
]}
```

`file` is relative to the folder that holds `images.json`. `source` is one of `own`, `kie`, `licensed` or `stock`.
- A `reference` or `unknown` source is a FIX.
- A `kie` image with `person: true` and no `consent` is a FIX.
- A `kie` image with no `ledger_key` is a WATCH.
- An image on the page that isn't listed is a WATCH ("where did it come from?").

## Copyright, in plain words

Purely AI-generated images often can't be copyrighted [practitioner], so the member may not be able to stop others copying them. Who owns Kie.ai outputs, and whether commercial use is allowed, isn't spelled out in Kie's terms (unconfirmed); each upstream model provider's own policy applies. Say this once, plainly, when a member plans to build their brand on generated images, and lean on their own photos for anything central.
