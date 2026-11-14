# Book principles: what the skill believes, and why

Each claim carries a tag: **[founder's method]** (the AI Momentum Labs book engine and its operating manual), **[official]**, **[data]**, **[practitioner]** or **[folklore]**. Say which kind a claim is when you use it with a member. Sources are in `research_notes/Book Builder/outside_research_2026.md` in the repository.

## 1. The beliefs

1. **The book is the author's, in the author's voice** [founder's method]. It's written from their answers, their stories and their method, with their exact framework names. Nothing is invented: no credentials, clients, numbers, quotations or studies.
2. **The biggest risk is made-up facts, not style** [practitioner]. In 2026 a trade non-fiction book shipped with AI-invented quotations and had an excerpt retracted. So the fact and source gate comes before anything cosmetic.
3. **Thin material makes a repetitive book** [founder's method]. If the intake can't support a chapter, ask the author for more or cut the chapter. Never stretch it.
4. **A memo is not a fix** [founder's method]. Naming a structural problem doesn't repair it. Every problem goes in the issue register and stays open until an edition fixes it and a check confirms it.
5. **A session can't grade its own draft** [practitioner]. The developmental review, the fact audit, the copyedit and the regression check are each run by an independent reader who hasn't seen the drafting conversation.
6. **Simulated readers suggest; real readers decide** [data]. Research on AI-simulated people shows they flatten variety, lean agreeable and change with how they're set up. No study tests them on book manuscripts. They're a cheap way to find likely problems before recruiting people. They're never counted as readers, quoted as testimonials or used as market evidence.
7. **Lengths are measured, never assumed** [founder's method]. A prompt's word target is a request. The scripts count what was written.

## 2. What the evidence says

- **Editing has an order** [practitioner; EFA, Reedsy]: developmental (the whole book's argument and structure), then line (voice and clarity), then copyedit (consistency and correctness), then proofread (the final files). Doing them out of order wastes the later ones.
- **AI prose has measurable tells** [data + practitioner]. Some vocabulary runs far above its normal rate ("delves" 25 to 28 times over trend in a study of 15 million abstracts), and some structures do too (trailing "-ing" clauses at 2 to 5 times the human rate). `voice.md` has the list. Use it as a density per chapter, never as a verdict on a sentence.
- **Readability** [practitioner]: Flesch-Kincaid grade 8 to 9 is the common target for general adult non-fiction. No source sets it for books specifically. The book's default ceiling is grade 9, and the member can change it.
- **Length** [practitioner]: business and self-help books usually run 40,000 to 60,000 words, sometimes 70,000, with chapters of 3,000 to 5,000 words. The default here (13 chapters, about 62,000 words, about 4,770 a chapter) is at the high end. A shorter book that says it once is better than a long one that repeats. Offer 45,000 to 55,000 when the material is modest.
- **Test readers** [practitioner]: five to ten invited from the target audience, before the copyedit; open "where" questions; a two-line "what is this book about" test; act when two or more readers flag the same place.
- **A living book record keeps a long manuscript consistent** [practitioner; editorial style sheets]: one record of names, terms, frameworks and stories, carried through every pass.

## 3. Folklore to correct

- "Every chapter needs the same skeleton" and "end every paragraph on a quotable line": no source supports either as good practice, and uniform chapters read as machine-made.
- "A longer book is a more serious book": readers stop reading padded books.
- "AI test readers tell you if the book will sell": they don't (§1.6).
- "Bestseller" as a promise: category rankings are short-lived and say little about readers. Never promise one.

## 4. What the script can and can't check

`book_check.py` reads text and records. It catches dashes, missing sections, placeholders, repeated passages, numbers and quotations that aren't in the author's material, named clients nobody supplied, banned lines, and stages that weren't done. It can't tell whether a claim is true, whether a story is really the author's, or whether the book is good. Those belong to the fact audit, the independent review and the readers. The gate checks that each one happened and that nothing they found is still open.
