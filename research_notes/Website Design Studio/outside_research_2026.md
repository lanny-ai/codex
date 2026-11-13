# Website Design Studio: outside research (2026-11-13)

Research pass for the Build Room OS "Website Design Studio" skill (taste vault, three HTML directions, tweak bar, locked design system, Kie.ai images).

**Method and limits.** Web search worked. Direct page fetches were blocked for most hosts in this session, including kie.ai, docs.kie.ai, w3.org, nngroup.com, web.dev and fonts.google.com. Only raw GitHub files could be read in full. Most claims below rest on search-result excerpts of the cited pages. Anything marked **unconfirmed** must be checked on the live page before the skill ships, and that applies to every Kie.ai price and model ID.

**Tags.**
- `[data]`: a measured study or dataset.
- `[official]`: a standards body, vendor docs or a license text.
- `[practitioner]`: write-ups and open-source skills by working designers or developers.
- `[folklore]`: widely repeated, with a weak, missing or misread source.

---

## 1. Kie.ai (image generation API)

### 1.1 What it is
- Kie.ai is an aggregator: one API key gives access to many third-party image, video, music and chat models, billed in prepaid credits. [official] https://kie.ai/pricing
- Kie says 1 credit is about USD 0.005, that failed tasks are not charged, and that credits do not expire. The first two are on the pricing page. The non-expiry claim comes only from a third-party review, so it is **unconfirmed** as official. [official] https://kie.ai/pricing ; [practitioner] https://www.bitdoze.com/kie-ai-review/
- An open-source MCP server's cost example (about 1,580 credits for about $7.90) matches the $0.005-per-credit rate. [practitioner] https://github.com/elibarnett/kie-mcp

### 1.2 Image models listed (late 2026)
This list comes from the kie-mcp README and the Kie market listing. It is a snapshot and the names change often. [practitioner] https://github.com/elibarnett/kie-mcp ; [official] https://kie.ai/market ; https://docs.kie.ai/market/quickstart
- **OpenAI GPT Image:** GPT Image 2.6 (Flare / Sunburst / Economy), 2.5, 2, GPT-4o Image, GPT Image 1.5.
- **Google:** Nano Banana 2.1, Nano Banana 2 / 2 Lite / Pro / Edit, Imagen 4 (Fast / Standard / Ultra).
- **Black Forest Labs Flux:** FLUX 3 Klein (text-to-image and edit), Flux Kontext Pro/Max, Flux 2 Pro/Flex.
- **ByteDance Seedream:** 3.0, 4.0, 4.5, 5.0 Lite, 5.0 Pro. The official docs also list "Seedream 5.5".
- **Ideogram:** v3, Character, Edit, Remix, Reframe. Useful when the image must contain legible text.
- **Others:** Qwen Image 3.0 / 3.0 Pro, Wan 2.7 Image, xAI Grok Imagine, Z-Image, Recraft, and Topaz (upscaling).
- **Midjourney:** Kie documents a Midjourney endpoint (`/api/v1/mj/generate`, task type `mj_txt2img`, with speed set to relaxed, fast or turbo). [official] https://docs.kie.ai/mj-api/quickstart
  - One comparison site says Kie removed Midjourney access, which contradicts Kie's docs. Current availability is **unconfirmed**. [practitioner] https://www.cometapi.com/cometapi-vs-kie-ai-2026/

### 1.3 Approximate prices per image (all unconfirmed; sources conflict)
| Model | Reported price | Source |
|---|---|---|
| GPT Image 2 (1K) | ~$0.03 (vs ~$0.21 official OpenAI) | Kie homepage, via search excerpt: https://kie.ai/pricing |
| Nano Banana 2.1 | 4 credits (~$0.02) | https://github.com/elibarnett/kie-mcp |
| Nano Banana 2 | 15 credits at 1K/2K, 25 credits at 4K (reseller listing) | https://kinovi.ai/docs/seedance2.0/nanobanana2-text-to-image |
| Nano Banana Pro | $0.09-0.12 at 1-2K, $0.12-0.24 at 4K | https://www.bitdoze.com/kie-ai-review/ ; https://creati.ai/ai-tools/kie-ai-affordable-and-reliable-nano-banana-api-for-image-generation-editing |
| FLUX 3 Klein | 1.6 credits (~$0.008) | https://github.com/elibarnett/kie-mcp |
| GPT Image 2.6 Economy | 5 credits flat | https://github.com/elibarnett/kie-mcp |
| Qwen Image 3.0 Pro | $0.032 at 1K, $0.060 at 2K | https://www.bitdoze.com/kie-ai-review/ |
| Midjourney text-to-image | 4 / 8 / 12 credits (relaxed / fast / turbo), from a third-party table | https://bylo.ai/features/mj-api |
| Seedream, Ideogram, Flux 2 Pro | not found at Kie-specific prices | **unconfirmed** |

Planning rule of thumb [practitioner]: most image calls cost about $0.01 to $0.12. A three-direction run with 3 to 6 images per direction should cost well under $2 on mid-tier models. Show the member the estimated credits before every batch, because prices are a moving target.

### 1.4 Request flow at a high level
- **Auth:** every request carries `Authorization: Bearer <KIE_API_KEY>`. [official] https://docs.kie.ai/market/common/get-task-detail ; https://kieai.mintlify.app/flux-kontext-api/get-image-details
- **Market models (unified flow):**
  - `POST https://api.kie.ai/api/v1/jobs/createTask` with a body of `{ model, input:{...}, callBackUrl? }`. It returns a `taskId`, not the image. [official] https://docs.kie.ai/market/quickstart
  - `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=...` reports `state` (waiting, queuing, generating, success or fail). On success, `resultJson` is a JSON *string* containing the result URLs, so it must be parsed. [official] https://docs.kie.ai/market/common/get-task-detail
- **Older model-specific endpoints** (4o Image, Flux Kontext, Veo, Midjourney) have their own generate and record-info routes. They use a numeric `successFlag` (0 = processing, 1 = success, 2 or 3 = failed) and return `resultUrls`. The skill must handle both shapes. [official] https://docs.kie.ai/old-model/1973341m0 ; https://kieai.mintlify.app/flux-kontext-api/get-image-details
- **Callbacks:** Kie recommends `callBackUrl` over polling in production. When polling, examples use intervals of about 30 seconds for slow models. [official] https://docs.kie.ai/4o-image-api/generate-4-o-image-callbacks
- **Credit balance:** `GET /api/v1/chat/credit`. [practitioner] https://www.mintlify.com/Greg-LeDall/pulse-content/api/services/kieai
- **Retention:** the 4o Image docs say generated files are kept for 14 days, and download-url links expire after 20 minutes. Whether this applies to every model is **unconfirmed**. Download and save each image into the vault right away. [official] https://docs.kie.ai/4o-image-api/generate-4-o-image
- **Rate limits:** Kie returns HTTP 429 when a limit is hit and 433 when a sub-key exceeds its limit. The exact numbers are **unconfirmed**. [official] https://docs.kie.ai
- **Model ID strings** mix formats (`google/nano-banana`, `nano-banana-pro`, `gpt-image-2-text-to-image`, `seedream/5-pro-text-to-image`). Read them from the live docs or a `list_models` call and never hard-code them from memory. [practitioner] https://www.bitdoze.com/kie-ai-review/

### 1.5 Terms: commercial use, ownership, real people
- Kie's Terms of Use say users keep ownership of the content they *upload* and grant Kie a non-exclusive licence to operate and improve the service. [official] https://kie.ai/terms-of-use
- Ownership of generated *outputs* is **unconfirmed**. One reviewer says the terms never mention outputs. A wiki summary says outputs belong to the user, subject to the upstream model provider's terms. [practitioner] https://sharkly.ai/blog/is-kie-ai-legit/ ; [folklore] https://ai.miraheze.org/wiki/Kie.ai
- I found no Kie clause that expressly allows commercial use of outputs or covers real people's likeness (**unconfirmed**). In practice the upstream provider's policy (OpenAI, Google, BFL, ByteDance and so on) still applies to each output.
- Likeness law applies whatever the tool's terms say. Using an identifiable person's likeness commercially without consent can breach publicity rights even when the image is AI-generated. [practitioner] https://getimg.ai/blog/can-ai-generated-images-and-videos-be-used-commercially
- Copyright in purely AI-generated images is "not automatically" available in most jurisdictions. A member may not be able to stop others copying them. [practitioner] same source.
- **Skill policy:** do not generate the member, clients or any real person as if photographed. Use AI images only for scenes, objects, textures and anonymous figures, and use real photos for the founder.

---

## 2. Why 2026 AI-built sites look generic ("slop tells")

### 2.1 Tells most often named
- **Purple-to-blue or indigo hero gradients**, traced to `indigo-500`-style defaults that are common in tutorials and starter kits rather than to any one library. [practitioner] https://dev.to/alanwest/why-every-ai-built-website-looks-the-same-blame-tailwinds-indigo-500-3h2p ; https://prg.sh/ramblings/Why-Your-AI-Keeps-Building-the-Same-Purple-Gradient-Website
- **A centered hero set in Inter**, with a small pill badge above the headline, rounded corners everywhere and a three-column feature grid. [practitioner] https://illos.dev/guides/vibe-coded-websites ; https://thecrit.co/resources/vibe-coding-design-guide
- **The "calm editorial" default:** a cream or beige background, a big serif headline with one italic word, and clay, terracotta, olive or sage accents, used whatever the business is. Several write-ups link it to Claude's house style; that link is their opinion, not Anthropic's. [practitioner] https://capitalandcompute.net/blog/fix-ai-slop-design/ ; https://claudecodehq.com/playbooks/unslop-ui ; https://impeccable.style/gallery
- **A repeating section recipe:** eyebrow label, Title Case serif headline, grey subtitle, pill button. [practitioner] https://web.mit.edu/phillipi/www/claude-tells.pdf
- **Card patterns:** identical rounded cards with the same soft shadow, cards nested inside cards, a rounded-square icon tile above every heading, and grey text on coloured backgrounds. [practitioner] https://raw.githubusercontent.com/pbakaus/impeccable/main/README.md
- **Decoration and motion:** floating pill nav, glassmorphism, bounce or elastic easing, and dark glows. [practitioner] https://instagit.com/Nutlope/hallmark/what-are-the-named-ai-slop-anti-patterns.md ; https://emelia.io/hub/impeccable-ai-design-skill
- **Other tells:** emoji bullets, fake "trusted by" logo rows, placeholder stock imagery and invented details such as street numbers. These come from practitioner checklists. The emoji and logo-row items are common lore that I found only in passing, so treat them as [practitioner/folklore]. https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/README.md ; https://github.com/Laith0003/ux-skill/wiki/Anti-AI-slop-ban-list
- **Key nuance:** a tell is an *unexamined default*, not a banned colour or font. A cream background chosen for a reason is fine. [practitioner] https://claudecodehq.com/playbooks/unslop-ui

### 2.2 Open-source anti-slop skills (summarised in my words)
**Anthropic frontend-design skill** [practitioner/official]. Source: https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md
- Derive the look from the subject's own world (industry, materials, vernacular), and open the hero with the most characteristic thing about the business, not a stat plus a gradient.
- Let type carry the personality: one family, or two clearly different ones, with a deliberate scale.
- Use dividers, numbers and labels only when they carry information. Don't number things "01 / 02 / 03" unless they really are a sequence.
- Plan before building: 4 to 6 named colours, type roles and a few layout sketches. Then review that plan for generic defaults before writing code.
- Spend boldness on one memorable element and keep everything else quiet.
- Use one orchestrated motion moment at most. No fade-up on every section and no hover effect on every card.
- Patterns to avoid:
  - italic, bold or coloured emphasis on one headline word
  - tracked all-caps eyebrow labels
  - cream with a high-contrast serif and a terracotta accent
  - near-black with a single acid accent
  - decorative gradient washes
  - identical card grids
  - newspaper-style hairline layouts
  - middle-dot meta strings and arrows tacked onto button text
- Quality floor: responsive layout, visible focus, reduced-motion support and accessible contrast.

**Impeccable** (pbakaus) [practitioner]. Sources: https://raw.githubusercontent.com/pbakaus/impeccable/main/README.md ; https://emelia.io/hub/impeccable-ai-design-skill
- It extends the Anthropic skill with reference files on typography, OKLCH colour, spacing, motion, interaction, responsive layout and UX writing.
- It adds named fix commands (audit, polish, distill, typeset, colorize, quieter, layout, animate).
- A standalone detector flags around two dozen issues, including purple gradients, side-tab borders, bounce easing, cramped padding and skipped heading levels.
- It warns against Inter-for-everything and overused system fonts.

**taste-skill** (Leonxlnx, MIT) [practitioner]. Sources: https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/README.md ; https://mer.vin/2026/07/taste-skill-explained-anti-slop-agent-skills-for-ai-frontend-design/
- First classify the page (software, service, place and so on). That classification picks the palette, font pairing, hero layout and which effects are allowed.
- Service businesses get calm pages built from photography, type and flat colour. Shaders and scroll scenes are reserved for tech and gaming.
- Use real photos or clearly labelled stand-ins, never placeholders.
- A browser check catches empty visuals, contrast drops, misaligned columns and placeholder text, and blocks hand-off for up to three fix rounds.
- Its "dials", such as visual density, are close to our tweak-bar idea.

**Common fix across write-ups** [practitioner]: make the decisions yourself (type pair, one accent, real imagery, page-wide rules) and give them to the model. Naming a specific palette is enough to break the gradient reflex. https://robotsonpayroll.substack.com/p/how-to-avoid-that-vibe-coded-look ; https://www.regards.design/blog/make-website-look-less-vibe-coded

---

## 3. Accessibility and readability for readers aged 55-75

### 3.1 WCAG 2.2 AA thresholds
- **1.4.3 Contrast (Minimum):** 4.5:1 for body text, and 3:1 for large text (at least 24px regular, or about 18.66px bold). [official] https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- **1.4.11 Non-text Contrast:** 3:1 for UI component boundaries, focus rings and meaningful graphics against their neighbours. The thresholds are not rounded, so 2.999:1 fails. [official] https://webaim.org/standards/wcag/wcag22 ; https://www.w3.org/WAI/WCAG22/Understanding/
- **2.5.8 Target Size (Minimum, new in 2.2):** at least 24x24 CSS px, or enough spacing that 24px circles around targets don't overlap. [official] https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
  - The AAA level (2.5.5) asks for 44x44. Aim for 44 to 48px for this audience. [official] same.
- **2.4.11 Focus Not Obscured** and the other 2.2 additions also apply; sticky headers must not cover focused items. [official] https://w3.org/WAI/standards-guidelines/wcag/new-in-22/
- **1.4.12 Text Spacing (AA):** the layout must survive a user increasing line height to 1.5, paragraph spacing to 2x and letter and word spacing. [official] https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation
- **1.4.8 Visual Presentation (AAA, a good target):**
  - lines of 80 characters or fewer
  - line spacing of 1.5 within paragraphs
  - paragraph spacing at least 1.5x the line spacing
  - no justified text
  - text resizable to 200% without horizontal scrolling

  [official] https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation

### 3.2 Motion
- **2.3.3 Animation from Interactions (AAA):** users should be able to switch off non-essential motion. The sufficient technique is the CSS `prefers-reduced-motion` media query (technique C39). [official] https://w3c.github.io/wcag/understanding/animation-from-interactions.html ; https://www.w3.org/WAI/WCAG22/Techniques/css/C39.html
- Don't blanket-kill every animation with `* {animation:none}`, because that breaks spinners and progress bars. Shorten or crossfade them instead. [practitioner] https://testparty.ai/blog/wcag-animation-interactions-guide

### 3.3 Text size and older readers
- **NN/g** [data]:
  - In the 2013 round, users over 65 succeeded on 55.3% of tasks versus 74.5% for younger users, and they were about 43% slower. https://www.nngroup.com/articles/usability-seniors-improvements/ ; https://www.nngroup.com/videos/design-elderly/
  - In the 2018-19 round, small, light-grey interface text was repeatedly a barrier. https://www.nngroup.com/articles/usability-seniors-improvements/
  - NN/g's own guidance is to let users enlarge text, not to name one fixed pixel size. https://www.nngroup.com/alertbox/seniors.html
- **GOV.UK Design System** [official] uses 19px body text (25px line height). From Frontend v6 it no longer shrinks body text on small screens, because smaller text harms people with visual impairments. 16px is reserved for secondary text. https://design-system.service.gov.uk/styles/type-scale ; https://designnotes.blog.gov.uk/2022/12/12/making-the-gov-uk-frontend-typography-scale-more-accessible
- **Systematic review (Frontiers in Psychology, 2022)** [data]: older adults prefer larger text, but readability drops past a critical size. No single size suits everyone, and studies are hard to compare. https://pmc.ncbi.nlm.nih.gov/articles/PMC9376262/
- **"16px is enough"** is the browser default and a common web baseline. **"18px+ for seniors"** is practitioner consensus rather than an RCT result. Senior-friendly guidance of 12-14pt (NIA/NLM, cited in Becker 2004) predates high-DPI screens. [practitioner/folklore] https://course.ccs.neu.edu/csg170/ssl/becker04.pdf
  - **Recommendation:** 18-20px body text, with nothing under 16px. This follows GOV.UK's 19px and the NN/g findings. [official+data inference]

### 3.4 Line length and leading
- Baymard recommends 50-75 characters per line for body text. Baymard's own site sets 20px text in a 560px column, which gives about 72 characters. [data/practitioner] https://baymard.com/blog/line-length-readability
- The research on line length is mixed; it interacts with size and leading. [practitioner] https://news.ycombinator.com/item?id=5193835
- **Working spec:**
  - body line height 1.5-1.6
  - headings 1.1-1.25
  - measure about 60-70ch
  - serif body text needs slightly more leading than sans

  [official/practitioner] https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation ; https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md

---

## 4. Fonts: license and pairings

### 4.1 License facts
- Google Fonts can be used commercially, including in logos and in products sold commercially. Most families are under the SIL Open Font License; a few use Apache 2.0 or the Ubuntu Font License. [official] https://developers.google.com/fonts/faq
- **Self-hosting is allowed.** Files can be downloaded from the official Google Fonts GitHub repository. [official] https://developers.google.com/fonts/faq
- **OFL 1.1** [official] https://spdx.org/licenses/OFL-1.1.html
  - Fonts may be used, embedded, modified, bundled and sold *with* software.
  - They may not be sold *by themselves*.
  - The copyright notice and licence must travel with the font files.
  - Documents and websites made with the font are not bound by the OFL.
  - Modified versions can't use a Reserved Font Name.
- No attribution is needed on the finished website. [practitioner] https://fontsplugin.com/google-fonts-commercial-use
- **GDPR angle:** in January 2022 the Munich Regional Court (3 O 17493/20) awarded €100 because a site loaded Google Fonts from Google's servers and passed visitors' IP addresses without consent. The ruling is first-instance and not binding EU-wide. Self-hosting avoids the issue. [official/practitioner] https://www.theregister.com/2022/01/31/website_fine_google_fonts_gdpr/ ; https://jsdelivr.com/blog/how-the-german-courts-ruling-on-google-fonts-affects-jsdelivr-and-why-it-is-safe-to-use
  - **Skill rule:** always self-host the font files with their OFL.txt.

### 4.2 Avoid as defaults
These are the faces that read as "AI default" today, so use them only when there is a clear reason:
- Inter for everything
- an italic display serif as the headline signature (Instrument Serif, Fraunces italic, Playfair italic)
- Space Grotesk on non-tech businesses
- Poppins or Montserrat

[practitioner] https://raw.githubusercontent.com/pbakaus/impeccable/main/README.md ; https://capitalandcompute.net/blog/fix-ai-slop-design/

### 4.3 Ten vetted pairings (heading / body)
- Character notes are my editorial judgment [practitioner].
- Each family appears on Google Fonts, believed OFL. I could not open the specimen pages from this session, so check the licence tab (https://fonts.google.com/specimen/<Name>) before locking a pairing.
- Atkinson Hyperlegible Next's OFL status is confirmed. [official] https://www.printmag.com/design-news/braille-institute-s-atkinson-hyperlegible-typeface-launches-on-google-fonts-for-visually-impaired/ ; https://fontsource.org/fonts/atkinson-hyperlegible-next/about

| # | Heading | Body | Character |
|---|---|---|---|
| 1 | Young Serif | Atkinson Hyperlegible Next | Warm, sturdy serif over a face built for low-vision legibility. Best default for a 55+ audience. |
| 2 | Libre Franklin (700-800) | Lora | Confident American-gothic headline over a soft, bookish serif. Suits trusted advisors and authors. |
| 3 | Bitter | Source Sans 3 | Friendly slab with an engineered feel. Practical and dependable, good for trades-turned-consultants. |
| 4 | Archivo (expanded/semi-expanded) | Literata | Wide, assertive headline over a highly readable text serif. Modern without looking techy. |
| 5 | Epilogue | Newsreader | Geometric-grotesque headlines over a magazine text serif. Editorial without the cream-and-italic cliché. |
| 6 | Zilla Slab | Karla | Bold slab with personality over a quirky, humane grotesque. Approachable coaching brands. |
| 7 | Alegreya | Alegreya Sans | Matched superfamily with calligraphic warmth. Good for wellness, story-led, literary practices. |
| 8 | Bricolage Grotesque | Hanken Grotesk | Characterful, slightly irregular display over a clean workhorse. Energetic; don't overuse it, as it is getting popular. https://hookagency.com/blog/best-google-fonts-for-headings/ |
| 9 | Merriweather (bold) | Fira Sans | Screen-first serif headlines over a humanist sans. Sober and authoritative, good for finance and legal advisors. |
| 10 | Instrument Sans | Crimson Pro | Crisp sans headlines over a classic old-style text serif. Quiet luxury, inverted from the usual serif-headline pattern. |

Pairing principle: a distinctive heading face needs a neutral, very legible body face, and two display faces should not fight. [practitioner] https://designproject.io/resources/downloads/choose-font-pairings.md

---

## 5. Landing-page design facts relevant to conversion

### 5.1 Attention above the fold
- In NN/g's eyetracking study (120 participants, 130,000+ fixations, 1920x1080), 57% of viewing time was above the fold and 74% within the first two screenfuls. That is down from 80% above the fold in 2010. [data] https://www.nngroup.com/articles/scrolling-and-attention/
- **Implication:** the first screen must say who it's for, what the offer is and the one next step. People do still scroll, so the page need not be one screen.

### 5.2 Single call to action
- Unbounce benchmark data: pages with a single CTA averaged 13.5% conversion, against 11.9% with two CTAs and 10.5% with three. That is a modest effect and the result is correlational. [data] https://www.marketingprofs.com/charts/2018/33935/what-converts-web-landing-page-benchmarks-and-trends-infographic
- The widely quoted "single CTA = +266%" has no primary source that I could find, and blogs even disagree on which direction it points. [folklore] https://studiomeyer.io/en/blog/landing-page-design.md

### 5.3 Real photos vs stock
- NN/g eyetracking found users ignore generic stock photos of people but scrutinise photos of real people and products that carry information. The findings are mostly from around 2010. [data] https://www.nngroup.com/articles/photos-as-web-content/
- The claim that a founder photo lifts conversion by X% is common, but I found no rigorous primary source for any figure. [folklore]

### 5.4 Speed and Core Web Vitals
- **Deloitte "Milliseconds Make Millions"** (commissioned by Google; 37 brands; four weeks): a 0.1s mobile speed improvement went with +8.4% conversions in retail and +10.1% in travel. The study was vendor-commissioned and correlational. [data] https://web.dev/case-studies/milliseconds-make-millions
- **web.dev case studies** [data, vendor-curated] https://web.dev/case-studies/vitals-business-impact
  - Vodafone: 31% better LCP, 8% more sales.
  - Rakuten 24: +33% conversion rate.
- **"Bounce probability +32% from 1s to 3s"** is a *relative* modelled increase from a Google/SOASTA analysis of ad landing pages. It is often misquoted as a bounce rate. [data, narrow] https://thinkwithgoogle.com/data/page-load-time-statistics
- **"53% abandon after 3 seconds"**: I couldn't trace the methodology. [folklore] https://www.webfx.com/blog/seo/site-speed-statist
- **Implications:**
  - Keep the page light: self-hosted, subset fonts (two families, three or four weights), compressed AVIF/WebP images with explicit dimensions, and little or no JavaScript.
  - Core Web Vitals "good" thresholds: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1. [official] https://web.dev/why-speed-matters/

### 5.5 Mobile share of traffic
- StatCounter puts mobile at roughly 50-60% of worldwide web traffic in mid to late 2026, with month-to-month swings; one September 2026 snapshot shows about 60% mobile. [data] https://gs.statcounter.com/platform-market-share/desktop-mobile/worldwide
- The share for an older, professional audience is probably more desktop-heavy. That is **unconfirmed**, so members should check their own analytics.
- **Rule:** design and review mobile first, and also check a 1280px desktop view.

---

## 6. Where non-designers find references, and the inspiration/copying line

### 6.1 Sources
Access status as reported; verify before relying on it.

| Source | Best for | Free? / sign-in | Citation |
|---|---|---|---|
| Pinterest | Mood, colour, photography style | Free; heavy login prompts when browsing (not verified this session) | **unconfirmed** |
| Dribbble | Polished UI shots (often unrealistic concepts) | Free to browse; Pro tiers about $4-100/mo for creators | https://www.inspoai.io/blogs/dribbble-alternatives |
| Behance | Full brand case studies | Free | https://www.inspoai.io/blogs/dribbble-alternatives |
| Land-book | Real landing pages by industry and style | Free to browse; paid extras | https://tinystartups.com/tools/land-book |
| Lapa Ninja | Landing pages by category | Free | https://www.inspoai.io/blogs/land-book-alternatives |
| Godly | Bold, animated, award-style sites | Free | https://www.inspoai.io/blogs/land-book-alternatives |
| One Page Love | One-page sites (close to our format) | Free | https://www.inspoai.io/blogs/land-book-alternatives |
| SaaS Landing Page / SaaSFrame | SaaS sections | Free; paid tiers | https://www.inspoai.io/blogs/land-book-alternatives |
| Mobbin | App and web flows | Paid (about $19/mo reported); sign-in | https://www.inspoai.io/blogs/land-book-alternatives |
| Awwwards | Award-winning sites | Free to browse | https://community-jp.eagle.cool/tools/graphic/inspiration |
| 21st.dev | React/Tailwind components | Core library free, premium planned; sign-in to publish | https://www.producthunt.com/p/21st-dev-the-npm-for-design-engineers/21st-dev-2 |
| X / Instagram design accounts | Trend-spotting | Free; login walls | **unconfirmed** |

[practitioner] Galleries skew toward tech and SaaS. For coaches and consultants, the best references are often real sites of admired peers, local businesses, book covers, magazines and hotel or restaurant sites. These feed the taste vault better than Dribbble concepts.

### 6.2 Inspiration vs copying (plain words; not legal advice)
- **Not protected by copyright:** ideas, methods, systems, layout principles, names, short phrases and typeface designs (US). [official] https://www.copyright.gov/circs/circ33.pdf ; https://www.copyright.gov/help/faq/faq-protect.html
  - A general look ("big photo left, headline right, warm colours") is free to borrow.
- **Protected:** someone else's actual photos, illustrations, written copy and code, automatically and without registration. [practitioner] https://lib.pstcc.edu/websitecopyright ; https://dribbble.com/stories/2020/12/28/what-designers-need-to-know-about-copyright-infringement
- **Trade dress and trademark:** logos, brand names and a distinctive overall look that identifies a company can be protected. Copying a competitor's whole look closely enough to confuse buyers is the risky zone. [practitioner] https://thomasdigital.com/the-legalities-of-copying-a-website-design ; https://jipel.law.nyu.edu/vol-5-no-1-2-yezril/
- **Screenshots in a private vault:** keeping them for personal reference is low-risk in practice. Republishing them or shipping their images is not. I found no authoritative ruling on reference screenshots, so the legal position is **unconfirmed**. Fair use is decided case by case.
- **Practical line** [practitioner]:
  - Take *qualities* (spacing, mood, contrast, type feel) from many references.
  - Never take *assets* (images, text, logos, code) from any of them.
  - Never take the whole composition of one site.
  - Mix at least three references per direction.

---

## Implications for the skill

1. Keep a **Kie adapter with two response shapes**: Market `createTask`/`recordInfo` with `state` and a `resultJson` string, and legacy model endpoints with `successFlag`/`resultUrls`. Poll with backoff and support `callBackUrl` where hosting allows it.
2. **Never hard-code Kie model IDs or prices.** Read them at runtime from the docs or the model list, show the estimated credits, ask for confirmation before each batch, and check the balance first.
3. **Download every generated image right away** into the member's vault (`assets/`), because Kie links expire (14 days for files, 20 minutes for download URLs, per the 4o docs).
4. **No real-person likeness.** Don't generate the founder or clients as photos. AI images are only for scenes, objects, textures and anonymous figures, and the founder photo must be real. Label AI images in the design-system file.
5. Treat Kie output ownership and commercial terms as **unconfirmed**. Tell members the upstream model's terms apply and that AI images may not be copyrightable. Re-check https://kie.ai/terms-of-use before launch.
6. Write our own **anti-slop rulebook** as checkable rules: no italic-last-word headline, eyebrows only where they inform, no default cream or purple gradient, no three identical cards, no fake logo row, no emoji bullets, no pill-badge-above-headline, one CTA style, and one bold move per page.
7. Make the **three directions differ structurally**, not just in colour: different layout archetype, type pairing and image treatment. Derive each from the member's business world and vault tags, following the frontend-design "subject vernacular" rule.
8. **Accessibility floor baked into tokens**, with failing combinations blocked rather than just warned about:
   - body 18-20px (never below 16px)
   - line height 1.5-1.6
   - measure about 65ch
   - contrast 4.5:1 for text and 3:1 for UI and focus
   - targets 44px or more
   - visible focus
   - `prefers-reduced-motion` honoured
9. **Tweak-bar sliders stay within safe ranges.** Clamp text size, contrast and spacing so a member can't slide into a failing design; show a live contrast badge.
10. **Self-host fonts** with OFL.txt in the locked design system, which helps both GDPR and speed. Offer the 10 vetted pairings, defaulting to Young Serif plus Atkinson Hyperlegible Next for older audiences.
11. **Performance budget per page:** two font families, three or four weights, AVIF/WebP with set dimensions, minimal JavaScript, and LCP of 2.5s or less on mobile. Mention speed plainly, without the folklore stats.
12. Design the hero for **the first screen**: who it's for, the promise, one CTA, and a real founder photo. Tell members "one clear CTA" is a modest, evidence-backed edge, not a 266% miracle.
13. **Review mobile first** (roughly half or more of traffic is mobile), then check desktop at 1280px.
14. **Taste-vault intake teaches "take qualities, not assets":** tag each screenshot with what the member likes (colour, type, mood, layout), store it privately, and never ship reference images or copy.
15. **Point members to free, no-login sources first** (One Page Love, Lapa Ninja, Land-book, Godly, Awwwards, Behance), plus peers' real sites and print. Treat Pinterest, Dribbble and Mobbin as optional.
