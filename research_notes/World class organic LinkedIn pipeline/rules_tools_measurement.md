# Rules, tools and measurement: research notes

Stream: the rules, the tools, and the measurement for the Build Room OS organic LinkedIn pipeline skill.
Compiled: 2026-10-16.

## How these notes were made (read first)

- **I could not open LinkedIn or Microsoft pages directly.** In this session, WebFetch failed on every host ("getaddrinfo ENOTFOUND"), and the sandbox proxy refused linkedin.com and learn.microsoft.com. Everything below comes from **web-search result extracts**. Where the search tool showed text from a linkedin.com or learn.microsoft.com page, I mark it **verified (search extract)**. Before anyone puts that wording in front of members, someone should open the live page and check it word for word.
- The web-search budget ran out (200 searches per turn, shared across agents) before I could finish. The gaps are listed under "Open items".
- Labels: **verified** = LinkedIn or Microsoft primary page, seen through a search extract. **reported** = a third party, named. **unclear** = sources conflict or nothing primary was found. **[training knowledge]** = the clause wording as I remember it from LinkedIn's agreement; secondary sources back it up, but I did not see it on a live page in this session.

---

## What matters most (10 lines)

1. User Agreement s.8.2 bans bots or "unauthorized automated methods" that add contacts, send messages, or create, comment on, like or share posts. It also bans browser plugins and extensions that scrape the site or automate activity on it. So the skill must never click, send or post inside linkedin.com for the member.
2. The Professional Community Policies ban artificially boosting engagement and agreeing in advance to like or reshare. Engagement pods, "CFBR" rings and comment swaps are out. LinkedIn's March 2026 feed update said it is targeting pods and comment automation.
3. Drafting with AI is allowed. LinkedIn asks members to "review, edit, and approve" AI-assisted content and suggests disclosing it when AI played a major role. Since late July 2026, a "Seems like AI slop" button lets readers flag posts, and LinkedIn says flagged content gets 40% fewer views. Generic AI text is now a reach risk, though not a terms violation.
4. LinkedIn's own scheduler handles personal posts from 10 minutes to 3 months ahead. It is the safest way to publish on a timetable.
5. A member's own app can post legitimately through the self-serve "Share on LinkedIn" product (`w_member_social`, `POST /rest/posts`). The app has to be attached to a LinkedIn Page. Reading the member's own post list (`r_member_social`) is closed.
6. Per-post analytics through the API (`memberCreatorPostAnalytics`, `r_member_postAnalytics`) belong to the Community Management API, which is for registered legal organisations and needs review. An individual should not count on it. Read native analytics or an XLSX export instead.
7. Native creator analytics export to .XLSX for windows from 7 to 365 days. That export plus the member's own pipeline log are the honest data sources for a weekly scorecard.
8. LinkedIn publishes no invitation numbers. The weekly invitation restriction lasts one week and cannot be lifted. Reported caps are about 100 to 200 per week, and free members get a handful of personalised notes a month (official page: 5 at 200 characters; recent reports: 3). The "300-character" note limit in the brief is unclear: 300 is reported for Premium, 200 for free.
9. Third-party tools: Buffer, Hootsuite and other Member Post Analytics API launch partners use official APIs. Taplio and AuthoredUp work through Chrome extensions in the member's session, which is a grey area under the "browser plug-ins" clause. Kleo's extension was shut down in early 2026, and Shield closed on 2026-05-18.
10. Prospect data: s.8.2 bans copying information from the Services without the owner's consent. Under GDPR, a solo expert needs a legitimate-interest basis, the smallest set of fields, an Article 14 notice at first contact, and fast handling of objections and deletion requests. Store notes the member typed by hand, not scraped profiles.

---

## 1. What LinkedIn prohibits

### 1.1 User Agreement, section 8.2 "Don'ts"
Source: https://www.linkedin.com/legal/user-agreement. One secondary source (contentin.io, 2026-07-28) gives the current version's effective date as **3 November 2025**. The Generative AI clause dates from the **20 November 2024** version (The Register, 2024-10-09). Status of the effective date: **reported**.

Clauses that matter for this skill. The wording is **[training knowledge]**, corroborated by LinkedIn's help page a1341387 (which restates s.8.2) and by several secondary sources. The live page was not opened.

- "Develop, support or use software, devices, scripts, robots or any other means or processes (such as crawlers, browser plugins and add-ons or any other technology) to scrape or copy the Services, including profiles and other data from the Services;"
- "Override any security feature or bypass or circumvent any access controls or use limits of the Services (such as caps on keyword searches or profile views);"
- "Copy, use, display or distribute any information (including content) obtained from the Services, whether directly or through third parties (such as search engines), without the consent of the content owner (such as LinkedIn for content it creates);" **Verified (search extract):** this phrase appears in Help a1341387.
- "Use bots or other unauthorized automated methods to access the Services, add or download contacts, send or redirect messages, create, comment on, like, share, or re-share posts, or otherwise drive inauthentic engagement;" **Reported** with this exact wording by supered.io, contextbolt.com, connectsafely.ai and pettauer.net (2026). linagora/twalk issue #201 notes that the ban is spread across several 8.2 items, not one "official clients only" clause.
- "Overlay or otherwise modify the Services or their appearance (such as by inserting elements into the Services or removing, covering, or obscuring an advertisement included on the Services);" [training knowledge]. Help a1341387 is reported to list overlaying or altering the site's appearance.
- "Sell, sponsor, or otherwise monetize any Service or any related data or access to the same, without LinkedIn's consent;" [training knowledge]
- "Create a false identity on LinkedIn, misrepresent your identity, create a Member profile for anyone other than yourself (a real person), or use or attempt to use another's account;" [training knowledge]. This is relevant if a VA or agency would be "acting as" the member.

Generative AI clause (s.3, "Generative AI Features"). **Verified (search extract)**, quoted in The Register (2024-10-09) and TechRadar:
> "...The content that is generated might be inaccurate, incomplete, delayed, misleading or not suitable for your purposes. Please review and edit such content before sharing with others. Like all content you share on our Services, you are responsible for ensuring it complies with our Professional Community Policies..."

That clause is about LinkedIn's own AI features, but it states the general principle that the member is responsible for what they post.

### 1.2 Help Center: "Prohibited software and extensions" (a1341387)
URL: https://www.linkedin.com/help/linkedin/answer/a1341387. Date not shown; the page was live in 2026 search results. **Verified (search extract):**
> "In order to protect our members' data and our website, we don't permit the use of any third party software, including "crawlers", bots, browser plug-ins, or browser extensions that scrape, modify the appearance of, or automate activity on LinkedIn's website."
> "All of these tools violate the User Agreement, including, but not limited to, the following prohibitions listed in Section 8.2..."

Consequences, as summarised in the search extract (**verified**, paraphrased): members using such tools risk having their accounts restricted or shut down, and the tools "may become non-operational without notice".

### 1.3 Help Center: "Account restrictions" (a1340522) and "Automated activity on LinkedIn" (a1340567)
- https://www.linkedin.com/help/linkedin/answer/a1340522 says automated inauthentic activity "violates the LinkedIn User Agreement and can result in temporary or permanent restriction of your account". **Verified (search extract).** The search tool flagged this page as old.
- https://www.linkedin.com/help/linkedin/answer/a1340567: a restricted member can disable the offending software, and the account is re-enabled when the suspension ends. **Verified (search extract, paraphrase).**
- Identity verification. Help a1342692, "Verify your identity to recover account access" (https://www.linkedin.com/help/linkedin/answer/a1342692): a restricted account can be recovered by verifying identity through **Persona**, using a photo of a government ID and sometimes a selfie. Other methods are offered for members who decline. **Verified (search extract, paraphrase).** Related pages: a1631613 and a1631614 (Persona).
- Brynne Tillman (Substack, 2026) **reports** that LinkedIn is permanently closing accounts for automation and shared logins. That is a practitioner report and is not quantified.
- Scale: the hiQ v. LinkedIn Ninth Circuit opinion (2019-09-09) records that LinkedIn blocked about 95 million automated scraping attempts a day and had restricted over 11 million accounts. **Verified (court record), but dated.**
- Fortune (2026-07-31) **reports** that LinkedIn blocks "hundreds of thousands" of automated comment attempts daily, and that it blocked billions of other automation attempts over a couple of months.

### 1.4 Professional Community Policies: fake engagement and pods
URL: https://www.linkedin.com/legal/professional-community-policies. Page date not captured. **Verified (search extract, paraphrase of the "Don't spam" / authentic engagement section):** members should not "try to do things to artificially increase engagement with your content". The page asks members to respond authentically to others' content and not to pre-arrange likes or reshares. The search tool **could not confirm the exact phrase "agreeing in advance"**. Status of the exact wording: **unclear**.

- Help a1338787, "Spam" (https://www.linkedin.com/help/linkedin/answer/a1338787). **Verified (search extract):** LinkedIn may remove or limit the distribution of content "designed to artificially increase engagement through misuse or misrepresentation of LinkedIn's features". Examples include emoji or reaction polls and "chain letter"-type content asking for likes, reactions and shares.
- March 2026 feed update. **Reported** by Search Engine Land (dated 2026-03-16) and Teamfluence (dated 2026-03-12): LLM-based retrieval and ranking, plus action against "comment automation tools, browser extensions, and engagement pods". Reported measures: automated comments hidden from "Most Relevant", and members who took part in pods or automation warned about restrictions and removal from programmes such as Top Voices. **I could not find LinkedIn's own post** about this. Status: unclear/reported.
- Gyanda Sachdeva, LinkedIn VP Product, is **reported** (Stampede Social and others) as saying: "Our goal is to make engagement pods entirely ineffective." Sources disagree on whether that was 2025 or 2026.
- Buying followers or engagement: I found no separate LinkedIn clause in this session. It falls under the s.8.2 "inauthentic engagement" item and the s.8.2 ban on monetising access, plus the policy against artificially increasing engagement. Status: **unclear** (no dedicated quote found).

### 1.5 Limits: invitations, notes and messages
| Item | Official (LinkedIn) | Reported in practice | Status |
|---|---|---|---|
| Weekly invitation limit | Help a550555, "Invitation limit reached" (https://www.linkedin.com/help/linkedin/answer/a550555): the restriction is temporary and lasts **one week**. Withdrawing invites does not lift it, support cannot shorten it or explain it, and Basic and Premium members are both subject to it. **No number is published.** | About 100 a week on a rolling 7 days, up to about 200 for strong accounts. Premium does not raise it. New accounts sit lower (50 to 80). Pending invites are capped somewhere between 500 and 1,500 (Salesforge, Taplio blog, Overloop, Evaboot, 2026). | Official: verified (extract). Numbers: reported. |
| Personalised notes, free accounts | Help a563153, "Personalize invitations to connect" (https://www.linkedin.com/help/linkedin/answer/a563153), cached copy about 4.6 years old: "you can add a personalized message for up to five of the connection requests that you send each month, each with a character limit of 200." Premium: no monthly cap. | **3 a month** (RevenueFlow, Leonar, others in 2026; one says it was cut in late 2025). Richard van der Blom reports experiments between 5 and 15. | **Unclear**: the official page may be stale. |
| Note length | 200 characters for free accounts (same cached page). | 300 for Premium (widely reported). Some vendors claim 300 for everyone. | **Unclear**. The brief's "300" holds only for Premium or Sales Navigator. The skill should cap notes at **200 characters** unless the member says they are on Premium. |
| Messages to 1st-degree connections | No published cap found. | Vendors cite "safe" daily DM counts with no basis. | Unclear. Not researched further (search budget). |
| InMail | Credits depend on the Premium plan; I did not verify the numbers this session. | n/a | Unverified. |
| Event invites | Help a550496: up to 1,000 invitations a week for events. | n/a | Verified (extract). |

---

## 2. AI-generated content

- **Help a1481496, "Best practices for content created with the help of AI"** (https://www.linkedin.com/help/linkedin/answer/a1481496). **Verified (search extract):**
  > "We urge you to review, edit, and approve of any content that you've used AI to create. You are ultimately responsible for everything you post on LinkedIn."
  > "As with other content you create and share on LinkedIn, follow our Professional Community Policies to keep your engagement safe, trustworthy, and professional."
  The page also recommends telling readers when AI played a major role in creating or modifying content, unless that is clear from context (paraphrase). It frames AI as a way to augment the member's own expression.
- **The User Agreement's Generative AI clause** (s.3, effective 2024-11-20): see 1.1.
- **C2PA "Content Credentials" ("CR" icon).** LinkedIn announced on 2024-05-15 that images and videos carrying C2PA Content Credentials are labelled automatically. Clicking the icon shows the source, including AI tools. LinkedIn says it cannot detect and label all AI content, and the label depends on metadata. **Reported** by Fortune (2024-11-26) and several 2026 blogs. **I did not find LinkedIn's own help page** in this session. Status: reported. Implication: images made with OpenAI, Adobe Firefly or similar tools may show the CR label. The skill should never advise stripping metadata to hide it.
- **AI text.** No LinkedIn rule bans AI-written text. No official text classifier or penalty is documented.
  - "Seems like AI slop" feedback button, launched in late July 2026. **Reported** by Fortune (2026-07-31), Forbes (2026-07-30 and 2026-08-10), Engadget, Social Media Today and Campaign. CPO Hari Srinivasan is quoted saying the button trains LinkedIn's models, that flagged content now gets **40% fewer views**, and that there were over 1 million reports in the first weeks. LinkedIn says the button is for personal feed control, not policy enforcement, and that using AI to polish language is acceptable. LinkedIn is adding a notice in post analytics when a post has been flagged, and is replacing its own "enhance your post" writer with a proofreader that keeps the author's voice. Status: reported (company claims passed on by the press).
  - Originality.ai found 54% of long posts likely AI in Oct 2024 (8,795 posts) and 81.2% in July 2026 (5,000 posts). Its 2025 study of 3,368 posts says likely-AI posts got **45% less engagement**. Pangram (July 2026) put fully-AI long posts at about 41%. All **reported**. None of these is a controlled test of LinkedIn's ranking.
  - SocialNexis claims an "originality classifier" caps reach to the first-degree network. That is a vendor claim with no source: **treat as unreliable**.
- **Design implication:** AI drafts are allowed. The output must be the member's own story, data and voice, and the member edits it. Generic AI-sounding text is now a measurable reach risk because of reader flags.

---

## 3. Posting and scheduling tools

### 3.1 Native scheduling (personal profile)
- Help a1347212, "Schedule posts" (https://www.linkedin.com/help/linkedin/answer/a1347212). The search showed it updated about 6 days before 2026-10-16. **Verified (search extract):** the clock icon in "Create a post" works on desktop (lower right) and mobile (upper right). The time chosen "must be within 10 minutes to 3 months from the current time". Scheduled posts can be viewed, rescheduled and deleted from the Scheduled posts list.
- Page posts (a1419179): 1 hour to 3 months ahead. Rescheduling and deleting work on desktop and iOS only.

### 3.2 Official APIs a member could use
- **Share on LinkedIn** (self-serve product, scope `w_member_social`). The docs live at learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin, which **I could not open**. **Reported** by Blotato, upload-post, zernio, Marcus Noble (2025-02-02), dev.to (2026) and swarmhit:
  - It is self-serve with no partner review. It lets an app post, comment and react **as the authorising member**.
  - The current endpoint is the versioned Posts API, `POST https://api.linkedin.com/rest/posts`, with a `Linkedin-Version` header. It replaces the old `ugcPosts` and Share endpoints.
  - Creating an app at developer.linkedin.com requires **attaching a LinkedIn Page**, and a Page admin verifies the link. A placeholder Page is reported to work. So **an individual can create an app and post through the API in 2026**, but only with a Page attached.
  - Access tokens last about 60 days and refresh tokens about 365 (reported).
  - `r_member_social`, which reads the member's posts, is **closed**. The app can post but cannot list the member's posts.
- **Rate limits.** learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits. **Verified (search extract):** there are daily application and member limits that reset at midnight UTC, and "standard limits are not published in documentation". The actual figure is shown in the Developer Portal under the app's Analytics tab after one call. Over the limit, the API returns 429. Admins are emailed at 75% of quota. **Reported** (vendor guide): Share on LinkedIn allows 150 requests per member per day and 100,000 per app per day; Community Management Development tier allows 100 per member and 500 per app per day.
- **Member post analytics through the API.** learn.microsoft.com/en-us/linkedin/marketing/community-management/members/post-statistics (view li-lms-2026-09). **Verified (search extract):**
  - Endpoint `memberCreatorPostAnalytics`. `q=entity` returns one post; `q=me` returns aggregates.
  - Metrics include IMPRESSION, MEMBERS_REACHED, REACTION, COMMENT and RESHARE. Postiz issue #1680 also lists POST_SAVE, POST_SEND, FOLLOWER_GAINED_FROM_CONTENT and PROFILE_VIEW_FROM_CONTENT (reported).
  - Scope `r_member_postAnalytics`, documented from version 202506, is part of the **Community Management API**.
  - Version 202510 sunsets on 2026-10-15.
  - Launch partners (2025-07-08): Hootsuite, Buffer, Metricool, Sprinklr, Oktopost, Zoho, mLabs, SocialPilot, Later, Publer and Vista Social (PPC Land, Destination CRM, Social Media Today).
- **Community Management API eligibility.** **Verified (search extract)** from the CM API Migration Guide:
  > "At this time, our Community Management APIs are only available to registered legal organizations for commercial use cases only."
  It also requires a verified business email, legal name, address, website and privacy policy. "All applications start with Development tier. You must apply separately to upgrade to the Standard tier." Standard tier needs a form and a screen recording, and the integration must be finished within 12 months.
  "Increasing Access" frames it more loosely ("open to all approved developers"). **That is a conflict in LinkedIn's own docs; the Migration Guide is the more specific.** Conclusion: **a solo member should not plan on API analytics.** A sole trader registering as a "legal organisation" is **unclear**.

### 3.3 Third-party schedulers and analytics tools
| Tool | How it connects | Status (Oct 2026) | Risk note | Status of claim |
|---|---|---|---|---|
| **Buffer** | Official LinkedIn API; launch partner for Member Post Analytics | Active; schedules to personal profiles | Low; uses official OAuth | Reported (DemandBird, PPC Land) |
| **Hootsuite** | Official API; marketing partner; Member Post Analytics launch partner | Active | Low | Reported |
| **Taplio** | Web app plus Chrome extension or session cookie (reported) | Active. LinkedIn reportedly restricted Taplio's own Page and temporarily blocked its access in **April 2025** | Medium: the extension and cookie model conflicts with the "browser plug-ins" clause. No public case found of a member banned for scheduling alone. Mass DM and auto-engage features are the high-risk parts | Reported (Kondo, MagicPost, SocialNexis; competitors, so biased) |
| **AuthoredUp** | Chrome extension inside the member's session (editor, preview, scheduling, analytics capture); imports the member's GDPR data export | Active | Medium-low. The vendor says no auto-likes, auto-comments, scraping or cookie collection, but it is still an extension "reading" LinkedIn pages. Not an official API | Reported (vendor and reviews) |
| **Kleo** | Was a Chrome extension | LinkedIn reportedly shut the extension down in **early 2026** for ToS problems (scraping, overlays). Relaunched as a paid web app ("Kleo 3.0") | The old extension is gone; the new app's method is unverified | Reported (contentin.io 2026-08-25, Postiv, Scripe) |
| **Shield** | Disputed: one source says official API, others say extension | **Shut down 2026-05-18** (co-founder Andreas Jonsson); extension removed from the Chrome Web Store | n/a; do not recommend it | Reported (Postiv, PublishFlow, LinkHub) |

**Where official docs and practice differ:** vendors sell "safe limits" for extensions and cloud automation, but LinkedIn's text has no carve-out for small amounts. Any extension or tool that automates activity is prohibited whatever the volume. Official-API tools (Buffer, Hootsuite and other Member Post Analytics partners) are the only clearly compliant third-party route for scheduling and analytics.

**For this skill**, Claude Code or Codex driving a browser (Claude in Chrome, computer use, Playwright and the like) to click "Post", "Connect" or "Send" on linkedin.com is exactly an "unauthorized automated method". I ran out of search budget before checking for any 2026 LinkedIn statement on AI browser agents specifically. Status: **unclear**, but the general clause plainly covers it.

---

## 4. Measurement available to a member

### 4.1 Native post analytics (per post: "View analytics")
- Help a516971, "Post analytics for your content" (https://www.linkedin.com/help/linkedin/answer/a516971) and a525196. **Verified (search extract):**
  - Impressions: the number of times the post was displayed. "This number is an estimate and may not be precise."
  - Unique viewers ("members reached" in the API): "the number of members your post was displayed to at least once".
  - "Who's viewed your profile since this post": Premium shows viewers from the first month. The section disappears after 90 days or if there were no viewers.
- Saves ("The number of times members saved your post") and Sends on LinkedIn ("...sent your post to others on LinkedIn"): verified (search extract, help a701208 and related pages). Added in 2025 (Social Media Today).
- "Profile Activity" section with **profile viewers from this post** and **followers gained from this post**. Reported by Website Builder Expert and Adobe, and mentioned in a post by Sam Corrao Clanon (LinkedIn director of creator products). LinkedIn also notifies members when a post drives profile views or followers, at about 3 and 7 days (Search Engine Journal, reported).
- Demographics of viewers (top job titles, companies, locations, industries): help a1624090, "Recent changes to top demographics of unique viewers". Verified that the page exists; I did not read the details.
- From late July 2026: a notice in post analytics when readers flag a post as "Seems like AI slop" (reported, Engadget and Forbes).

### 4.2 Creator analytics and export
- Help a704175, "View your creator analytics" (https://www.linkedin.com/help/linkedin/answer/a704175). **Verified (search extract):**
  > "To export your analytics to an .XLSX file, click on the Export button on the upper-right corner."
  The date range is set from the dropdown, from "the past seven days up to the past 365 days" (default 7 days). It covers the Content/Posts tab.
- Audience analytics, help a1373345 (https://www.linkedin.com/help/linkedin/answer/a1373345): follower growth trend and follower demographics, with a 7 to 365 day range for the New followers graph and Top demographics. **Verified (search extract).**
- Path in the UI (training knowledge, confirm live): Me > Posts & Activity, or the "Analytics" section on the member's own profile > Content impressions > Export. The help pages are 2 to 4 years old, so labels may have moved.

### 4.3 Profile views
- Help a548046 (https://www.linkedin.com/help/linkedin/answer/a548046). **Verified (search extract):** Basic accounts see the last 90 days, but "shows three most recent viewers if your profile viewing option is set to display name & headline". Premium sees up to 365 days with filters (a LinkedIn Learning tutorial says Career gets 90 days and Business 365). Private-mode viewers stay anonymous to everyone.

### 4.4 SSI
- linkedin.com/sales/ssi is **reported** as still live and free in 2026 (contentin.io, Reply.io 2026, LinkedAPI guide). It gives a 0 to 100 score across four 25-point parts and recalculates daily. LinkedIn is **reported** to be giving it less prominence (Neal Schaffer). Status: **unclear** (no 2026 LinkedIn statement). Treat it as an optional vanity or activity gauge, not a KPI.

### 4.5 Account data export
- "Get a copy of your data": Me > Settings & Privacy > Data privacy > Get a copy of your data. Help a566336 (https://www.linkedin.com/help/linkedin/answer/a566336) and a1339364. **Verified (search extract).** The Connections CSV has first name, last name, title, company and date connected. Email appears only where the connection allows it. "You currently can't export a list of your contacts that aren't 1st-degree connections." The full archive (posts, messages, invitations) arrives later by email. I did not confirm file names.

### 4.6 Weekly scorecard: what goes in it and where each number comes from
| Metric | Source | How it gets in (no automation) |
|---|---|---|
| Posts published (count, format, topic pillar) | Skill's own queue log | Skill records it when the member confirms "posted" |
| Impressions per post and per week | Native post analytics / creator analytics XLSX | Member exports XLSX weekly (7-day range) or pastes the numbers |
| Members reached (unique viewers) | Native post analytics | Member pastes it per post |
| Engagements (reactions, comments, reposts), engagement rate = engagements / impressions | Post analytics / XLSX | XLSX import |
| Saves and sends (the strongest intent signals) | Post analytics | Member pastes |
| Profile viewers from post; followers gained from post | Post analytics "Profile Activity" | Member pastes |
| Net new followers (week) | Audience analytics / XLSX | XLSX import |
| Profile views (week) | Profile "Analytics" > Profile viewers (free: count only, 3 names) | Member pastes the number |
| Comments the member left on others' posts (target accounts) | Skill's comment queue log | Member marks each as "posted by me" |
| Connection requests sent / accepted, acceptance % | Skill's outreach log + My Network > Manage invitations | Member logs sends; checks accepted manually |
| DMs sent, replies, reply % | Skill's DM log | Member logs |
| Conversations started → calls booked → proposals → won (£/$) | Skill's pipeline (CRM) | Member logs |
| Inbound signals (DMs, comments asking "how", profile-to-call) | Member logs | Manual |
| Reader flags ("Seems like AI slop" notices) | Post analytics notice | Member logs any |
| Leading vs lagging split | n/a | Inputs (posts, comments, DMs) vs outputs (replies, calls, revenue) |

Optional: if the member uses Buffer or Hootsuite (official API partners), their post-level numbers can come from that tool's export. Buffer's numbers are reported to differ from native ones; native is the source of truth.

---

## 5. Data and privacy

- **User Agreement s.8.2** (see 1.1): no scraping or copying of profiles or data, and no copying or using "any information (including content) obtained from the Services ... without the consent of the content owner". So a CRM must not be filled by scraping, bulk export of non-connections, or "enrichment" tools that pull LinkedIn data. **Verified (search extract via a1341387) / [training knowledge] for the exact 8.2 wording.**
- What is reasonably defensible: the member's own 1st-degree Connections export (LinkedIn offers it), and short notes the member types themselves (name, company, role, where they met, what was discussed, next step). The prospect knowingly shared those with the member. Copying full profile text, photos, or contact data of non-connections is the risky part. Status: **unclear**; this is my reading, not a LinkedIn statement.
- **GDPR / UK GDPR basics for a solo expert** (sources: ICO "Right to be informed" and "Right to object" pages, reported via search; secondary write-ups by SalesPrep, Sales.co, folkfox and Adverizeo, 2026):
  - A solo expert is still a **controller**. The household exemption does not cover business prospecting.
  - Lawful basis: usually **legitimate interests** (Art 6(1)(f)), with a short written legitimate interests assessment. Professional details people publish in a work role fit what they would reasonably expect.
  - **Article 14 notice**: when data was not collected from the person, they must be told who you are, why you hold it, where it came from and their rights, within one month at the latest, or **at first contact if you contact them sooner**. Practically, include a one-line privacy notice with a link in the first DM or email, or link a privacy page from the LinkedIn profile.
  - **Right to object** to direct marketing is absolute. Stop at once and suppress the contact. The ICO gives one month to respond to requests.
  - Data minimisation and storage limits: keep only the fields you need, and set a retention rule (for example, delete cold prospects with no interaction after 12 months).
  - **E-privacy**: emailing prospects is governed by PECR in the UK and national laws in the EU. Sole traders and partnerships are treated as individuals in the UK (training knowledge; verify with ICO PECR guidance). LinkedIn DMs inside the platform are generally treated differently from email. Status: unclear.
  - Security: a local file on the member's computer is fine if the disk is encrypted and the file is not synced to shared drives without care.
  - Italian Garante ruling (about €2m) on B2B contact data: reported by folkfox. Details not verified.

---

## Open items (not reached; search budget used up or pages unreachable)
- Live wording of User Agreement s.8.2 and of the Professional Community Policies "engagement" section (open the pages and quote them exactly).
- LinkedIn's own help page for the C2PA / Content Credentials icon.
- LinkedIn's primary March 2026 feed-update post (newsroom or engineering blog).
- Any 2026 LinkedIn statement on AI browser agents (Claude in Chrome, ChatGPT Atlas, Comet).
- Official DM limits and InMail credit numbers per plan.
- The Share on LinkedIn docs page on learn.microsoft.com (to confirm self-serve status, the Page requirement and limits first-hand).

---

## Sources (date = page date where known / date seen in search)
LinkedIn and Microsoft primary sources (seen through search extracts on 2026-10-16; not opened directly):
- User Agreement: https://www.linkedin.com/legal/user-agreement (version effective 2025-11-03, reported)
- Professional Community Policies: https://www.linkedin.com/legal/professional-community-policies (undated)
- Prohibited software and extensions: https://www.linkedin.com/help/linkedin/answer/a1341387
- Account restrictions: https://www.linkedin.com/help/linkedin/answer/a1340522
- Automated activity on LinkedIn: https://www.linkedin.com/help/linkedin/answer/a1340567
- Verify your identity: https://www.linkedin.com/help/linkedin/answer/a1342692 ; Persona: https://www.linkedin.com/help/linkedin/answer/a1631613
- Invitation limit reached: https://www.linkedin.com/help/linkedin/answer/a550555
- Personalize invitations: https://www.linkedin.com/help/linkedin/answer/a563153 (cached copy about 4.6 years old)
- Event invitation limits: https://www.linkedin.com/help/linkedin/answer/a550496
- Spam: https://www.linkedin.com/help/linkedin/answer/a1338787
- Best practices for AI content: https://www.linkedin.com/help/linkedin/answer/a1481496
- Schedule posts: https://www.linkedin.com/help/linkedin/answer/a1347212 (updated about 2026-10-10); Page scheduling: https://www.linkedin.com/help/linkedin/answer/a1419179
- Post analytics: https://www.linkedin.com/help/linkedin/answer/a516971 ; https://www.linkedin.com/help/linkedin/answer/a525196 ; Combined post analytics: https://www.linkedin.com/help/linkedin/answer/a701208
- Creator analytics: https://www.linkedin.com/help/linkedin/answer/a704175 ; Audience analytics: https://www.linkedin.com/help/linkedin/answer/a1373345 ; Demographics: https://www.linkedin.com/help/linkedin/answer/a1624090
- Who's viewed your profile: https://www.linkedin.com/help/linkedin/answer/a548046
- Export connections: https://www.linkedin.com/help/linkedin/answer/a566336 ; Download account data: https://www.linkedin.com/help/learning/answer/a1339364/
- Rate limits: https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits
- Member Post Statistics: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/members/post-statistics?view=li-lms-2026-09
- Recent Marketing API changes: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/recent-changes?view=li-lms-2026-01
- CM API Migration Guide: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-api-migration-guide?view=li-lms-2026-09
- Increasing Access: https://learn.microsoft.com/en-us/linkedin/marketing/increasing-access?view=li-lms-2026-09
- hiQ Labs v. LinkedIn (9th Cir., 2019-09-09): https://www.fr.com/uploads/4878-hiq-labs-inc-v-linkedin-corp-ninth-circuit-september-9-2019.pdf

Press and third parties (reported):
- Fortune, 2026-07-31: https://fortune.com/2026/07/31/linkedin-seems-like-ai-slop-button-billions-automated-comments-attempts/
- Forbes, 2026-07-30: https://www.forbes.com/sites/codyluongo/2026/07/30/linkedin-adds-new-feature-to-flag-ai-slop/ ; 2026-08-10: https://www.forbes.com/sites/jodiecook/2026/08/10/what-linkedins-ai-slop-crackdown-means-for-your-posts/
- Engadget (2026): https://www.engadget.com/2241857/linkedin-says-its-ai-slop-button-is-working/ ; Social Media Today: https://www.socialmediatoday.com/news/linkedin-says-1m-people-have-reported-ai-slop/828465/
- The Register, 2024-10-09: https://www.theregister.com/2024/10/09/linkedin_ai_misinformation_agreement/
- Fortune, 2024-11-26 (C2PA): https://fortune.com/2024/11/26/linkedin-content-credentials-labeling-challenges-c2pa
- AdNews (Originality.ai 81.2%): https://www.adnews.com.au/news/more-than-four-in-five-linkedin-posts-now-likely-ai-generated
- Search Engine Land, 2026-03-16: https://searchengineland.com/linkedin-updates-feed-algorithm-llm-ranking-retrieval-471708 ; Teamfluence: https://teamfluence.com/blog/linkedin-feed-algorithm-update-2026-social-selling/
- Stampede Social (pods): https://www.stampede.social/linkedin-is-cracking-down-on-engagement-pods-good
- PPC Land, 2025-07: https://ppc.land/linkedin-enables-third-party-analytics-access-with-new-member-post-api/ ; Destination CRM: https://www.destinationcrm.com/Articles/CRM-News/CRM-Across-the-Wire/LinkedIn-Launches-Member-Post-Analytics-API-170402.aspx ; Social Media Today: https://www.socialmediatoday.com/news/linkedin-provides-analytics-data-members-third-party-platforms/752638/ ; https://www.socialmediatoday.com/news/linkedin-adds-save-and-send-data-to-content-insights/759828/
- Search Engine Journal (post alerts): https://www.searchenginejournal.com/linkedin-alerts-you-when-posts-drive-profile-views-followers/554066/
- Postiz issue #1680: https://github.com/gitroomhq/postiz-app/issues/1680 ; TryPost issue #377: https://github.com/trypostit/trypost/issues/377 ; linagora/twalk #201: https://github.com/linagora/twalk/issues/201
- Posting via the API (Marcus Noble, 2025-02-02): https://marcusnoble.co.uk/2025-02-02-posting-to-linkedin-via-the-api/ ; Blotato: https://www.blotato.com/blog/linkedin-posting-api ; zernio: https://zernio.com/blog/linkedin-posting-api
- Limits (vendor): https://www.salesforge.ai/blog/linkedin-connection-request-limit ; https://taplio.com/blog/linkedin-connection-request-limit ; https://www.revenueflow.com/blog/linkedin-invitation ; Richard van der Blom: https://www.linkedin.com/posts/richardvanderblom_free-users-of-linkedin-are-being-limited-activity-7136636331375427584-i_DP
- Tools: Kondo on Taplio: https://www.trykondo.com/blog/is-taplio-safe-understanding-the-risks-to-your-linkedin-account ; MagicPost: https://magicpost.in/blog/is-taplio-safe ; AuthoredUp reviews: https://magicpost.in/blog/authoredup-review ; Kleo: https://contentin.io/blog/kleo-alternatives/ ; Shield shutdown: https://postiv.ai/blog/shield-alternatives , https://publishflow.io/blog/shield-analytics-winding-down ; DemandBird scheduling: https://demandbird.com/resources/best-linkedin-scheduling-tools/
- Automation commentary: https://contentin.io/blog/linkedin-mcp-terms-of-service/ (2026-07-28) ; https://brynnetillman.substack.com/p/warning-linkedin-is-permanently-closing
- SSI: https://contentin.io/glossary/social-selling-index/ ; https://nealschaffer.com/weave-social-traditional-selling-strategies/
- GDPR: ICO right to be informed: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-be-informed/ ; ICO right to object: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-object/ ; SalesPrep: https://salesprep.ai/blog/gdpr-legal-basis-b2b-prospecting ; Sales.co: https://sales.co/blog/is-it-legal-to-buy-an-email-list ; folkfox: https://folkfox.com/b2b-contact-data-garante-erasure-ruling/

---

## Design rules for the skill

### The skill must never
1. Log in to, click on, type into, or send anything on linkedin.com or the LinkedIn apps. That rules out browser automation, computer use, Playwright or Selenium, extensions and cookie or session reuse (s.8.2 "bots or other unauthorized automated methods"; a1341387).
2. Send connection requests, DMs, comments, reactions or reposts for the member, even "just one" or "at safe limits". The rules have no volume carve-out.
3. Scrape or bulk-copy profiles, search results, post commenters, follower lists or non-connection data, or call unofficial or "LinkedIn data" APIs or enrichment services (s.8.2 scrape/copy clauses).
4. Organise, join, recommend or simulate engagement pods, comment swaps, "CFBR" rings, or prearranged likes or reshares. Never suggest buying followers or engagement (Professional Community Policies; spam help a1338787).
5. Advise getting around limits: rotating accounts, withdrawing invites to "reset", shared logins, a VA logged in as the member, or several profiles (s.8.2 access-control and identity clauses).
6. Advise stripping C2PA or Content Credentials metadata, or hiding AI use where AI did the main work.
7. Publish generic, unedited AI text. Every draft must contain member-supplied specifics and must be marked "draft: member edits before posting".
8. Write engagement bait ("comment YES", "like if you agree", reaction polls). It is reduced in distribution under the spam policy.
9. Store prospect data the member did not knowingly receive. No profile photos, no full profile text, no personal emails or phones the prospect did not give.

### The skill may automate (off-platform, on the member's computer)
- Drafting posts, hooks, comments, connection notes (capped at **200 characters** unless the member confirms Premium, then 300) and DMs, in the member's voice from their own stories and notes.
- Queues and calendars: post backlog, a "comments to write today" list built from accounts the member names, DM follow-up reminders, and a pacing guard (for example, warn above about 20 invites a day or 80 a week, and above 3 personalised notes a month on free accounts).
- Pipeline tracking (a local CSV, markdown or SQLite CRM) with lawful-basis fields, source, consent or objection flags, last contact, and a retention date. Auto-flag records due for deletion.
- Analytics import: parsing the member's own creator-analytics **XLSX export**, Connections CSV, or full-archive files, then building the weekly scorecard and trends.
- Optional, member-owned official API: if the member creates their own LinkedIn developer app (Page attached, Share on LinkedIn / `w_member_social`), the skill may publish a post the member approved through `POST /rest/posts`, one at a time and on explicit confirmation. Prefer native scheduling. Never use it to comment, react or bulk-post. Treat this as an advanced opt-in.
- A one-line Article 14 privacy notice and link for first-contact DMs or emails; objection and deletion handling.

### Must be done by the member's own hand
- Publishing: paste into LinkedIn, or use LinkedIn's native scheduler (10 minutes to 3 months ahead).
- Every connection request, every DM, every comment, every reaction and repost, typed or pasted and sent by the member inside LinkedIn.
- The final edit and approval of every AI draft (LinkedIn a1481496: "review, edit, and approve").
- Choosing whom to contact and comment on, by looking at profiles themselves.
- Exporting analytics XLSX and data archives from LinkedIn settings, and confirming "posted / sent / accepted / replied" back to the skill.
- Identity verification and recovery if LinkedIn restricts the account.
- Deciding whether to disclose AI use, and replying personally to every comment and DM.
