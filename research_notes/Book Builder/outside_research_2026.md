# Book Builder: outside research pass (2026-11-14)

Scope: evidence and practitioner guidance for the "AI Momentum Labs Book Builder" skill (13 chapters, about 62,000 words, manuscript only).

## How to read this file

- Tags: **data** (measured study), **official** (regulator, standards body, platform policy), **practitioner** (working editors, publishers, lawyers writing for authors), **folklore** (widely repeated, no evidence found).
- **Access limit, important.** In this session every direct page fetch failed (hosts outside the allowed network: en.wikipedia.org, the-efa.org, kdp.amazon.com, copyright.gov, janefriedman.com, pangram.com). Everything below comes from search-result extracts of the cited pages. Where the claim rests on a primary source I could not open, it is marked **unconfirmed (primary not opened)**. Re-check those before quoting them to members.
- Nothing here is legal advice. Section 5 and 6 are plain-word orientation only.
- No private individuals are named. Papers are cited by title.

---

## 1. Good practical non-fiction vs generic AI-written books

### 1.1 What the evidence says

- A study of over 15 million PubMed abstracts (2010-2024) measured "excess vocabulary" after LLMs arrived. "Delves" appeared about 25-28 times more often than the pre-LLM trend predicted; "showcasing" and "underscores" were also sharply up. The authors estimate at least 13.5% of 2024 abstracts were LLM-processed (a lower bound; earlier versions said 10%). [data] https://arxiv.org/abs/2406.07016v5 and https://languagelog.ldc.upenn.edu/nll/?p=64877
- A corpus study ("Do LLMs write like humans? Variation in grammatical and rhetorical styles") found instruction-tuned models use present-participle clauses ("..., highlighting the need for...") at 2 to 5 times the human rate and nominalisations at 1.5 to 2 times the human rate, and fail to match human stylistic variation. [data] https://arxiv.org/pdf/2410.16107v1
- A university stylometry study reported that AI models produce "compact, predictable styles" while human writing stays more varied and idiosyncratic. [data] https://www.ucc.ie/en/news/2025/new-study-reveals-that-ai-cannot-fully-write-like-a-human.html
- The Reuters Institute describes the two families of tells as (a) previously rare words that became cliches and (b) "a formulaic sentence structure repeatedly used in the same text". [practitioner] https://reutersinstitute.politics.ox.ac.uk/news/how-ai-generated-prose-diverges-human-writing-and-why-it-matters
- Wikipedia's "Signs of AI writing" (WikiProject AI Cleanup, roughly 15,000 words) is the most-cited field guide. Reported contents: an AI vocabulary list (delve, intricate, tapestry, pivotal, underscore, landscape, foster, testament, enhance, crucial); "stands/serves as a testament", "plays a vital/significant role", "underscores its importance", "continues to captivate", "leaves a lasting impact", "deeply rooted", "rich cultural heritage"; negative parallelisms ("not just X, but also Y", "not X, but Y"); overuse of the rule of three; em dashes used more than human editors use them. **Unconfirmed (primary not opened)**; taken from mirrors and summaries. [practitioner] https://www.bespacific.com/?p=117756 ; https://www.beutlerink.com/blog/how-to-spot-ai-writing ; https://www.blakestockton.com/takeaways-from-wikipedias-signs-of-ai-writing-2/
- The same guide carries two caveats that matter for us: the list is advice, not a ban, and not all text with these signs is AI-generated, because models learned them from human writing. Rule of three "used sparingly" is normal in argumentative and promotional writing. [practitioner] https://www.beutlerink.com/blog/how-to-spot-ai-writing
- Editors' lists add: generic or empty introductions, padded verbs ("serves as", "helps with"), and endings that "gently summarize everything" ("Ultimately...") with unnatural regularity. [practitioner] https://contently.com/2025/10/14/how-to-edit-the-ai-isms-out-of-your-content-no-detectors-needed/ ; https://decrypt.co/348923/5-biggest-tells-something-written-ai
- "In today's fast-paced world" is named as the single biggest tell on several practitioner lists; "It is important to note" should simply be deleted ("just say the thing"). [practitioner] https://ehprybylski.substack.com/p/current-ai-tells ; https://www.ritnerdigital.com/blog/the-phrases-that-give-away-ai-writing-and-how-to-edit-them-out-before-they-cost-you-trust
- Counter-view: several phrases ("game-changer") were human cliches for two decades before LLMs, and critics call banned-word lists overblown. Treat every item as a weak signal, read in context. [practitioner] https://www.businessday.co.za/bt/business-and-economy/2025-02-09-arthur-goldstuck-ai-telltale-signs-stop-sounding-like-a-bot/
- Scale of the issue: a 2025 ghostwriting-firm survey reported 58% of non-fiction authors and 68% of ghostwriters using AI. An anonymous senior non-fiction editor is quoted saying undisclosed AI work is widespread. Survey method not checked. [practitioner] https://www.bespacific.com/?p=125121
- The costly failure is not style, it is fabrication. In May 2026 a trade non-fiction book about AI and truth shipped with more than half a dozen fake or misattributed quotes traced to AI tools; a magazine retracted its excerpt. Commentary: the workflow had no verification gate. Primary press reports not opened. [practitioner] https://www.techdirt.com/2026/05/21/ai-fabricated-quotes-in-a-book-about-ai-undermining-truth-the-author-says-this-proves-his-point/ ; https://oecd.ai/en/incidents/2026-05-19-f57e ; https://news.northeastern.edu/2026/05/28/book-publishing-ai-reckoning/
- Not found: any source confirming "uniform chapter skeleton" or "every paragraph ends on a quotable line" as documented editor tells for books. These are plausible extensions of the "formulaic structure repeated in the same text" finding, but as book-level claims they are **folklore** until tested on our own drafts.

### 1.2 What fixes it (drawn from the sources above)

- Replace abstraction with the author's particulars: a named place, a number, a date, what was said. The measured gap is variation and specificity, not vocabulary alone. [data] https://arxiv.org/pdf/2410.16107v1
- Cut the wrapper: delete the throat-clearing opener and the summarising closer, then see if the paragraph still stands. [practitioner] https://contently.com/2025/10/14/how-to-edit-the-ai-isms-out-of-your-content-no-detectors-needed/
- State the claim directly instead of denying a position nobody held ("not X, but Y"). [practitioner] https://www.blakestockton.com/takeaways-from-wikipedias-signs-of-ai-writing-2/
- Keep a shared phrase library so every pass flags the same things. [practitioner] https://easycontent.io/resources/overused-ai-phrases-for-content-teams/
- Do not swap one tell for another. Removing em dashes or "delve" by find-and-replace leaves the formula intact; the rewrite has to change the sentence. [practitioner] https://www.beutlerink.com/blog/how-to-spot-ai-writing

### 1.3 Flag list for automatic checking (58 items)

Use as a density check per chapter, never as a verdict. Sources for each group are given; groups E and F are partly our own extension and tagged so.

**A. Vocabulary (flag when two or more per 1,000 words)** [data + practitioner] https://arxiv.org/abs/2406.07016v5 ; https://www.beutlerink.com/blog/how-to-spot-ai-writing
1. delve / delves / delving
2. tapestry
3. intricate / intricacies
4. pivotal
5. underscore(s)
6. landscape (figurative)
7. foster
8. testament
9. crucial
10. enhance
11. showcase / showcasing
12. leverage (as a verb)
13. unlock
14. transform / revolutionize / future-proof
15. game-changer
16. robust, seamless, holistic (group; practitioner lists) https://dev.to/q404365631/300-ai-words-and-phrases-to-avoid-in-2026-complete-list-20f0
17. journey (figurative), realm, beacon (group; same source)

**B. Stock phrases** [practitioner] https://www.bespacific.com/?p=117756 ; https://ehprybylski.substack.com/p/current-ai-tells ; https://www.ritnerdigital.com/blog/the-phrases-that-give-away-ai-writing-and-how-to-edit-them-out-before-they-cost-you-trust
18. "In today's fast-paced world" / "In today's digital age"
19. "In an era of..." / "In a world where..."
20. "stands as a testament to" / "serves as a testament"
21. "plays a vital/significant/crucial role"
22. "underscores the importance of"
23. "leaves a lasting impact" / "continues to captivate"
24. "deeply rooted" / "rich heritage"
25. "It is important to note that" / "It's worth noting"
26. "Let's dive in" / "Let's unpack this" / "Let's explore"
27. "navigate the complexities of" (on our list; no source found that names it: folklore)
28. "When it comes to..."
29. "At its core" / "At the end of the day"
30. "The truth is" / "Here's the thing" / "Here's the kicker"
31. "In conclusion" / "In summary" / "Ultimately," as a paragraph opener
32. "Whether you're a ... or a ..., "
33. "Imagine a world where" / "Picture this"
34. "more than just a" / "isn't merely"
35. "serves as" / "acts as" / "helps with" where "is" or a real verb would do https://contently.com/2025/10/14/how-to-edit-the-ai-isms-out-of-your-content-no-detectors-needed/

**C. Sentence patterns** [data + practitioner] https://arxiv.org/pdf/2410.16107v1 ; https://www.blakestockton.com/takeaways-from-wikipedias-signs-of-ai-writing-2/
36. "It's not X, it's Y" / "This isn't about X. It's about Y."
37. "not just X, but (also) Y" / "not only... but also"
38. "Y rather than X" used to correct a view nobody stated
39. Three-item lists ("clear, concise, and compelling"): flag when more than about one per 300 words
40. Trailing participle clause: ", highlighting / underscoring / reflecting / ensuring ..."
41. Em dashes: flag above a set rate (suggest more than 2 per 1,000 words; threshold is ours)
42. Colon reveal: "The result? ..." / "The answer: ..."
43. Rhetorical question immediately answered by the writer
44. Stacked adjectives before a noun (three or more)
45. Heavy nominalisation ("the implementation of the utilisation of")
46. Stacked hedges ("can often potentially help")
47. Unattributed authority: "Studies show", "Experts agree", "Research suggests" with no source
48. Intensifiers and sincerity markers: truly, really, genuinely, honestly, incredibly
49. Signposting: "As we'll see", "As mentioned earlier", "Now that we've covered"

**D. Paragraph patterns** [practitioner] https://decrypt.co/348923/5-biggest-tells-something-written-ai ; https://reutersinstitute.politics.ox.ac.uk/news/how-ai-generated-prose-diverges-human-writing-and-why-it-matters
50. Paragraph ends on a short aphorism or restatement (measure: share of paragraphs whose last sentence is under 10 words)
51. Paragraph opens with a one-line "hook" then explains it
52. Uniform paragraph length (low variance in sentences per paragraph)
53. Uniform sentence length (low variance in words per sentence)

**E. Chapter and book patterns** [folklore as book-level tells; see 1.1]
54. Every chapter uses the same skeleton (story, lesson, three points, recap, bridge)
55. Every chapter ends with "Key takeaways" plus a teaser for the next chapter
56. Same opening move in consecutive chapters (anecdote, question, statistic)

**F. Substance flags (the ones that actually hurt)** [practitioner] https://www.techdirt.com/2026/05/21/ai-fabricated-quotes-in-a-book-about-ai-undermining-truth-the-author-says-this-proves-his-point/
57. Any quotation, statistic, study or date with no source in the intake material
58. Any anecdote the author did not supply (invented client, composite presented as real, "a client of mine, Sarah")

---

## 2. Editing stages: definitions and order

- Order, per the Editorial Freelancers Association (EFA) guide for new authors: developmental editing, then line editing, then copyediting, then proofreading. **Unconfirmed (primary not opened)**. [official] https://www.the-efa.org/editorial-services-definitions/ (described at https://www.ebookpbook.com/2026/04/30/developmental-editing-copy-editing-proofreading/)
- EFA: developmental editors deal with content, organisation and genre; line editors work at sentence and paragraph level; line editing may be done separately, with developmental editing once big-picture issues are settled, or with copyediting. **Unconfirmed (primary not opened)**. [official] https://www.the-efa.org/editorial-services-definitions/
- Reedsy lists editorial assessment, developmental editing, copy editing, proofreading, plus fact-checking for non-fiction. Copy editing happens only once structure is set. [practitioner] https://reedsy.com/blog/types-of-editing/
- Rationale for the order: work from the largest problems inward; copyediting text that may be cut or restructured is wasted effort. [practitioner] https://www.ebookpbook.com/2026/04/30/developmental-editing-copy-editing-proofreading/
- Terms are not fully standard. Editors Canada does not list developmental editing among its core skills; "line editing" is sometimes called "substantive editing" or "heavy copyediting". [official] https://editors.ca/hire/skills ; [practitioner] https://thecraftyfoxwriterscorner.substack.com/p/lets-talk-editing-take-2
- Chicago Manual of Style: I could not confirm its own wording (the terms usually attributed to it are "mechanical editing" and "substantive editing" inside "manuscript editing"). **Unconfirmed**. One secondary source says recent editions name four levels. [practitioner] https://www.ebookpbook.com/2026/04/30/developmental-editing-copy-editing-proofreading/

Typical checks by stage (synthesis of the sources above; the split is practitioner convention):

| Stage | Question it answers | Typical checks |
|---|---|---|
| Assessment / developmental memo | Is this the right book? | Promise to reader, audience fit, argument, chapter order, gaps, repetition, what to cut |
| Developmental edit | Does each chapter do its job? | Structure, logic, evidence, examples, pacing, balance of story and instruction |
| Line edit | Does it sound like the author and read well? | Voice, rhythm, clarity, word choice, transitions, paragraph shape |
| Copyedit | Is it correct and consistent? | Grammar, spelling, punctuation, usage, numbers, capitalisation, terms, cross-references, queries on facts |
| Proofread | Did anything slip through? | Typos, missing words, formatting slips; normally done on laid-out pages, so in a manuscript-only skill this is a final clean read |

- Fact-checking and permissions sit beside this ladder, not inside it; Reedsy treats fact-checking as its own non-fiction service. [practitioner] https://reedsy.com/blog/types-of-editing/

---

## 3. Test readers: human and simulated

### 3.1 Human beta readers (all practitioner)

- When: before copyediting, because their feedback drives edits; most sources put them after self-editing or developmental work. One publisher blog says after copyedit; minority view. https://www.ebookpbook.com/2026/07/03/beta-readers-before-or-after-editing/ ; https://kwepub.substack.com/p/how-to-choose-your-beta-readers-and
- How many: advice ranges from 2-3 up to "several dozen". The common figure is 5 to 10 invited, expecting about half to finish with useful notes. https://scribemedia.com/beta-readers/ ; https://www.writingbeginner.com/?p=12445 ; https://nybookeditors.com/2017/10/what-you-need-to-know-about-working-with-beta-readers/
- Who: people in the exact target audience. For non-fiction, non-experts show where the explanation moves too fast and what they expected to learn but did not; an expert can be asked to read only the part in their field. https://www.ebookpbook.com/2026/07/03/beta-readers-before-or-after-editing/ ; https://buildbookbuzz.com/beta-readers/
- How many questions: keep it short. One non-fiction editor warns against more than ten; another range is 5 to 15. **Primary not opened.** https://janefriedman.com/what-to-ask-your-beta-readers/ ; https://www.lisatener.com/2018/02/beta-readers-find-questions-ask/
- Avoid leading: no yes/no and no "did you like it?". Ask open questions, and ask "where", not "whether" ("Where did you lose interest?"), so answers point to passages. https://janefriedman.com/what-to-ask-your-beta-readers/ ; https://www.bookwriter.vip/tools/beta-reader-questions-generator (vendor page)
- Comprehension test for non-fiction: ask the reader to write a two-line summary of the book's point. If summaries differ, the argument is not landing. https://bookmachine.org/2017/09/18/quick-easy-guide-using-beta-readers-authors
- Weighing: look for patterns; do not act on one reader's taste. If two or more readers flag the same spot, treat it as real. The author decides. https://www.well-storied.com/blog/how-writers-can-prepare-for-a-fantastic-beta-reader-experience ; https://scribemedia.com/beta-readers/
- Not found: a source that directly tests "friends and family give softer feedback". Commonly said; **folklore** here.

### 3.2 LLM-simulated readers: what the research supports

- The founding paper ("Out of One, Many", Political Analysis 2023) showed GPT-3 conditioned on real demographic backstories could reproduce group-level survey patterns ("algorithmic fidelity"). This is about aggregate opinion distributions, not reactions to a text. [data] https://arxiv.org/pdf/2209.06899.pdf
- "Synthetic replacements for human survey data? The perils of large language models" (Political Analysis 2024) compared ChatGPT personas with a national election survey and warned of distortions, including less variation than real respondents and sensitivity to prompt wording and model version. [data] https://www.cambridge.org/core/services/aop-cambridge-core/content/view/B92267DC26195C7F36E63EA04A47D2FE/S1047198724000056a.pdf/synthetic-replacements-for-human-survey-data-the-perils-of-large-language-models.pdf
- "Large language models that replace human participants can harmfully misportray and flatten identity groups" (3,200 human participants, 16 demographic groups, 4 models): persona-prompted models portray groups the way outsiders imagine them and erase within-group variety. Journal venue unconfirmed; arXiv version seen. [data] https://arxiv.org/pdf/2402.01908
- "The threat of analytic flexibility in using large language models to simulate human data" (2025): across defensible setup choices, human-to-silicon correlations ranged from r = .23 to r = .84. The result depends heavily on how you configure it. [data] https://arxiv.org/pdf/2509.13397
- "Generative Agent Simulations of 1,000 People" (2024 preprint): agents built from two-hour interviews with 1,052 real people matched those people's survey answers 85% as well as the people matched themselves two weeks later, and beat demographic-only personas. The lift came from rich individual data, which a book persona prompt does not have. [data] https://arxiv.org/abs/2411.10109v1
- A usability-research firm re-ran three real studies with synthetic users: useful for broad attitudes, but responses were "one-dimensional"; position is that research still needs real users. A vendor summary adds that synthetic groups agreed with each other more and rated things more favourably. **Primary not opened**; second claim comes from a vendor with a stake. [practitioner] https://ballparkhq.com/research-glossary/synthetic-users ; https://www.koji.so/docs/synthetic-users-research-methodology
- A measurement firm's review of 12 comparison papers is reported as 9 encouraging against 14 discouraging findings. Secondhand. [practitioner] https://pmtoolkit.ai/learn/experimentation/synthetic-users-promise-and-trap
- Evidence is mixed, not uniformly negative; some studies find response distributions simulated well. [data] https://arxiv.org/pdf/2509.13397
- Gap: I found **no study** testing LLM personas as predictors of real readers' reactions to a book manuscript. All evidence is transferred from survey and UX research.

Honest summary for the skill: simulated readers are a cheap way to generate hypotheses ("a busy owner may stall in chapter 4"). They tend to be agreeable, to converge on the average reader, and to change with the prompt. They cannot report boredom, confusion or disbelief they did not feel. They are not evidence that readers will like the book and must never be reported to the member as if they were.

---

## 4. Readability, chapter length, total length

- Flesch Reading Ease 60 to 70 is the standard "plain English" band; Flesch himself preferred 60-70. [practitioner] https://pages.stern.nyu.edu/wstarbuc/Writing/Flesch.htm
- A university accessibility guide suggests about 60-70 for an adult readership. [official] https://accessibility.huit.harvard.edu/technique-writing-readable-content
- 60-70 maps to roughly Flesch-Kincaid grade 8-9; tool guides commonly state "grade 8 or below" for general audiences. [practitioner] https://wordcount.com/guides/what-is-a-good-readability-score ; https://typecount.com/blog/flesch-reading-ease-score
- No source found that sets a readability target specifically for non-fiction books. The grade 8 figure is a web and plain-language convention applied to books by analogy. [folklore as a book standard]
- Readability formulas only count sentence and word length; they do not measure whether the idea is clear. Sources warn against treating Reading Ease and grade level as the same thing. [practitioner] https://howmanywords.app/blog/readability-scores-explained
- Total length: self-help and how-to 40,000-70,000 words (one range starts at 20,000); business 40,000-60,000 called the current sweet spot; self-help 30,000-70,000. [practitioner] https://danieljtortora.com/blog/word-count-nonfiction-book ; https://www.builtwritten.com/blog/how-many-words-in-a-business-book-for-2025 ; https://clearsightbooks.com/how-long-nonfiction-book/
- So 62,000 words is inside the range but at the upper end; 45,000-55,000 would be closer to the most-recommended band. [practitioner] same sources
- Chapter length: 3,000-5,000 words for self-help, 3,500-5,000 for business and leadership; other sources say 2,000-4,000 or 2,500-5,000. [practitioner] https://typecount.com/blog/book-chapter-word-count ; https://danieljtortora.com/blog/how-many-words-in-a-nonfiction-book-chapter ; https://scribemedia.com/how-long-should-a-chapter-be/
- 62,000 / 13 chapters is about 4,770 words per chapter: inside the norm, upper half. One source advises keeping chapters within about 10% of the average length. [practitioner] https://danieljtortora.com/blog/how-many-words-in-a-nonfiction-book-chapter
- All length figures come from editorial and publisher blogs, not industry datasets.

---

## 5. Honesty and legal basics, in plain words (not legal advice)

**Real people and client stories**
- Getting permission from people you feature is a standard way to reduce claims. [practitioner] https://authorsguild.org/resource/writing-about-real-people-libel-defamation-rights-of-privacy-and-publicity/
- Changing a name is not enough. If a person can be recognised from setting, description or circumstances, they may still have a claim. Composites and "fictionalising" are not automatic protection. [practitioner] https://writersdigest.com/business-legal-matters/can-the-truth-get-a-writer-in-trouble ; https://www.authorsalliance.org/2023/12/05/authors-alliance-releases-new-legal-guide-to-writing-about-real-people/
- Truth defends against defamation but not against privacy claims: revealing true but private, embarrassing facts about a private person can still be actionable. [practitioner] https://writersdigest.com/business-legal-matters/can-the-truth-get-a-writer-in-trouble
- Highest risk: private, non-famous people (family, former partners, clients) and self-published authors with no publisher legal read. [practitioner] https://janefriedman.com/ask-the-editor-how-can-i-avoid-lawsuits-when-writing-memoir/ (primary not opened)
- Coaches and consultants often also owe clients confidentiality by contract or professional code; that is separate from the law above. No source checked; treat as a prompt to ask the member. [folklore]

**Quoting other writers**
- Fair use is judged on four factors: purpose of the use, nature of the work, amount used, effect on the market. There is no fixed formula. [official] https://www.copyright.gov/fair-use/more-info.html (primary not opened)
- There is no safe word count. "300 words of prose is fine" is a publisher rule of thumb, not law. [practitioner] https://copyright.nova.edu/?p=57 ; https://www.geist.com/for-writers/quotability
- Short quotations with attribution for comment or criticism are generally accepted; attribution does not replace permission when permission is needed. [practitioner] https://www.libraries.rutgers.edu/copyright/fair-use
- Song lyrics and poetry: publishers ask for permission for even a line or two, because a line is a large share of a short work. One academic publisher states lyrics need permission, including as an epigraph. Song titles are free to use. [practitioner] https://lupress.lehigh.edu/sites/lupress.lehigh.edu/files/docs/2024-05/rl-permissions-guide-2024.pdf ; https://careerauthors.com/quoting-song-lyrics-in-fiction
- Epigraphs are decorative, not commentary, so the fair-use case is weaker; publishers commonly require clearance. Public-domain sources are fine, but check modern translations. [practitioner] https://utpress.utexas.edu/permission-guidelines/

**Health, money and results claims**
- US FTC health guidance (December 2022): health-benefit claims need "competent and reliable scientific evidence", generally good human clinical studies; anecdotes do not count. Staff guidance, not binding law. [official] https://ftc.gov/system/files/ftc_gov/pdf/Health-Products-Compliance-Guidance.pdf (primary not opened); [practitioner] https://www.cov.com/en/news-and-insights/insights/2023/01/ftc-issues-new-guidance-on-health-related-claims-to-replace-the-dietary-supplements-advertising-guide
- Advertisers are responsible when they use books to promote their products. For a coach whose book sells a programme, the book can be read as marketing. [practitioner] https://www.mcdermottlaw.com/insights/after-almost-25-years-ftc-issues-new-health-products-compliance-guidance/
- Income claims: the FTC has told sellers that "results may vary" wording does not undo the impression that a success story is typical, and that even true testimonials mislead unless typical outcomes are disclosed. Coaching programmes are within scope. [official] https://FTC.GOV/system/files/attachments/penalty-offenses-concerning-money-making-opportunities/cover-letter-mmo.pdf ; [practitioner] https://natlawreview.com/article/ten-compliance-mistakes-made-online-training-and-business-coaching-program-providers
- A disclaimer page ("not medical, legal or financial advice") is normal practice but does not rescue a claim the evidence does not support. Inferred from the two items above; no source states it in those words. [practitioner]

**Testimonials and endorsements**
- FTC Endorsement Guides (updated June 2023) require disclosure of payment or other material connections. The Guides themselves are not law. [practitioner] https://dwt.com/insights/2024/08/ftc-finalizes-rule-banning-fake-consumer-reviews
- The Consumer Reviews and Testimonials Rule (16 CFR Part 465, in force 21 October 2024) bans fake or false reviews and testimonials, buying reviews conditioned on sentiment, and undisclosed insider reviews, with civil penalties (about $53,000 per violation in 2025, adjusted yearly). AI-written fake testimonials are covered. [official, via law-firm summaries] https://www.morganlewis.com/pubs/2024/08/ftc-issues-final-rule-on-consumer-reviews-and-testimonials ; https://frostbrowntodd.com/ftcs-new-rule-on-consumer-reviews-ensuring-compliance-with-human-and-ai-generated-content
- Plain reading for the skill: never invent a testimonial, client result or endorsement, and never polish a real one into something the person did not say.
- All of section 5 is US-centred. Members elsewhere (UK, Canada, Australia, EU) face different defamation and consumer rules. Not researched.

---

## 6. Amazon KDP and US copyright

**KDP** (kdp.amazon.com could not be opened; every item below is **unconfirmed against the live policy page** https://kdp.amazon.com/en_US/help/topic/G200672390)
- Since September 2023 KDP asks publishers to declare AI-generated content (text, images, translations) when publishing or republishing. [official, via coverage] https://authorsguild.org/news/amazon-adds-to-kdp-generative-ai-policy-caps-daily-self-publishing-uploads/ ; https://thebookseller.com/news/amazon-revises-kdp-guidelines-to-compel-disclosure-of-ai-content
- "AI-generated" = created by an AI tool, reported to apply even if you edited it heavily afterwards. "AI-assisted" = you created it and used AI to brainstorm, edit, refine or check it; no declaration required. [official, via copies] https://www.lesswrong.com/posts/4csaBfAgiyzrFXvEj/amazon-kdp-ai-content-guidelines ; https://www.luminarepress.com/?p=17241
- Consequence for this skill: if the skill drafts the chapters and the member edits them, the text is most likely "AI-generated" under KDP's definition and should be declared. That is my reading of the reported definition, not a quote.
- The declaration is not shown to shoppers; it is for Amazon's records. [practitioner] https://www.ebookpbook.com/2026/05/27/declare-ai-use-kdp/
- The publisher stays responsible for all content meeting the guidelines, including intellectual property. [official, via copies] https://denivan.substack.com/p/ai-generated-content-guidelines-for
- Limit: three new titles per day per account, announced September 2023, "may be adjusted". Whether it still stands in late 2026 is **unconfirmed**. Irrelevant to a member writing one book, but it signals Amazon's stance on volume. [official, via coverage] https://www.theregister.com/2023/09/22/amazon_ai_book_publishing_limit/ ; https://authorsguild.org/news/amazon-adds-to-kdp-generative-ai-policy-caps-daily-self-publishing-uploads/
- Vendor blogs report stricter 2025-2026 enforcement (removals, suspensions for non-disclosure). No Amazon source. [folklore] https://writeo.app/news/amazon-kdp-ai-disclosure-enforcement-2026

**US copyright** (copyright.gov could not be opened; law-firm summaries used)
- US copyright requires a human author. [official] Copyright and Artificial Intelligence, Part 2: Copyrightability, 29 January 2025, summarised at https://www.skadden.com/insights/publications/2025/02/copyright-office-publishes-report
- Prompts alone do not make you the author of the output, with today's tools. [official, via summary] https://www.jenner.com/en/news-insights/publications/client-alert-us-copyright-office-issues-report-on-copyrightability-of-works-incorporating-ai-generated-material
- Using AI as a tool does not disqualify a work. What the human wrote, plus the human's selection, arrangement and substantial modification of AI material, can be protected. Decided case by case. [official, via summary] same Skadden and Jenner links
- March 2023 registration guidance: applicants should disclose AI-generated material that is more than trivial and claim only the human part. **Unconfirmed in this session** (from prior knowledge; Federal Register 88 FR 16190). [official] https://www.copyright.gov/ai/
- Courts: the D.C. Circuit (2025) held a work with no human author cannot be registered, while noting the rule does not bar works made "with the assistance of" AI. The Supreme Court declined review on 2 March 2026. The case does not say how much human input is enough. [official, via summary] https://www.mayerbrown.com/en/insights/publications/2026/03/supreme-court-denies-review-in-ai-authorship-case
- Plain words: the more of the book that is the member's own stories, wording and rewriting, the stronger their claim. Passages left as the model wrote them may not be protected. A member who registers should describe AI use truthfully.

---

## 7. Keeping a long manuscript consistent across passes

- A style sheet is a manuscript-specific record of every editorial decision; the proofreader uses it so earlier decisions are not undone. [practitioner] https://www.ebookpbook.com/2026/03/04/style-sheet-editing-books/ ; https://thebluegarret.squarespace.com/blog/what-is-a-style-sheet
- Standard contents: reference works used (for US general non-fiction, Chicago and Merriam-Webster); spelling variant; hyphenation decisions; numbers and dates; capitalisation; list of looked-up words. [practitioner] https://theeditingco.com/blog/understanding-a-style-sheet-what-authors-and-editors-need-to-know ; https://knowadays.com/?p=7945
- Fiction adds a character list, places and a timeline (the "bible"); series keep a separate series bible. [practitioner] https://www.sfwa.org/?p=7483 ; https://blog.ciep.uk/rpg-style-sheets/
- Deliberate departures must be written down, or a later copyedit "will standardize it away in good faith". This is the main protection for an author's voice quirks. [practitioner] https://www.ebookpbook.com/2026/03/04/style-sheet-editing-books/
- Non-fiction equivalent of the bible (our adaptation, no single source): people and client stories with status of permission; defined terms and framework names; numbers and claims with source; promises made to the reader and where they are paid off; cross-reference map; timeline of the author's own history. [practitioner, adapted]
- Regression risk is recognised in practice: each pass can undo an earlier one, which is why the sheet travels with the manuscript from copyedit to proof. [practitioner] https://karenrobinsonedits.squarespace.com/blog/using-style-sheets

---

## Implications for the skill

1. **Put the fact gate ahead of the style gate.** The 2026 fabricated-quote scandal came from no verification step, not from "delve". Every quote, statistic, study and anecdote needs a source in the intake file or a P0 issue. No sourced intake, no drafting.
2. **Run the flag list as a density score per chapter, not a word ban.** Report counts against thresholds and rewrite the sentence, never find-and-replace. Say plainly that the signs also occur in human writing.
3. **Measure variation.** Sentence-length and paragraph-length spread, share of paragraphs ending on a sentence under 10 words, and opening-move repetition across chapters are checkable and closer to the measured evidence than vocabulary.
4. **Vary chapter skeletons on purpose at outline approval.** Record each chapter's opening move and shape in the outline so sameness is caught before drafting. Label this as our hypothesis; no source confirms it as a known tell.
5. **Keep the editing order strict:** developmental memo, sample-chapter approval, line edit, then copyedit, then final clean read. Never copyedit text that may still move. Call the last pass a "final read", since true proofreading needs laid-out pages.
6. **Label simulated readers honestly.** Call them "simulated reader notes: guesses to test", run them before human readers to sharpen the questionnaire, and never count them toward the final gate. Expect them to be agreeable and average.
7. **Human test readers: 5 to 10 invited from the real audience, before copyedit, at most 10 open questions.** Include "where" questions and the two-line summary test. Log an issue when two or more readers flag the same spot.
8. **Give the 55-75 audience plain numbers:** target Flesch Reading Ease 60-70, grade 8-9, reported per chapter, with a note that the score checks sentence length, not clarity.
9. **Reconsider the 62,000-word default.** It is within range but above the 40,000-60,000 band most sources recommend for business books. Offer 45,000-55,000 as the standard and 62,000 as the long option; keep chapters within about 10% of average.
10. **Build a permissions register into intake:** every real person, client story, quotation, lyric, epigraph and testimonial gets a row with status (permission held, anonymised and unrecognisable, public source, cut). Lyrics and poetry epigraphs default to "cut or clear".
11. **Hard rules on claims:** no invented testimonials or results; income and health claims need evidence and a typical-result statement; a disclaimer page is added but never treated as a fix. Flag anything medical, legal or financial for the member's own professional review.
12. **Tell the member the truth about publishing:** a book drafted by the skill is probably "AI-generated" in KDP's terms and should be declared; the label is not public. Copyright is strongest in what they wrote and rewrote. Both statements need a "check the current page" note.
13. **Carry one living "book bible" through every pass:** style sheet, voice quirks to protect, terms, people and permissions, claims and sources, promises and payoffs. Load it at the start of each session and update it at the end.
14. **Regression check = diff against the bible and the issue register.** After copyedit, confirm that closed P0 and P1 issues stayed closed and that protected voice choices were not standardised away.
15. **Before release, re-verify the items marked unconfirmed** (EFA wording, Chicago terms, live KDP policy and title limit, Copyright Office 2023 guidance, the primary beta-reader article) once network access to those hosts is allowed.
