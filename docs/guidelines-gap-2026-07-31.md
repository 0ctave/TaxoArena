# Guidelines gap report — TU Berlin thesis submission
Date: 2026-07-31
Source of authority: `C:\Users\octav\Downloads\Abschlussarbeit Hinweise_042025_eng.pdf`
("Guidelines for Completing Bachelor's and Master's Theses", Department I — Student Services, Examinations, IB / Updated: April 2025)
Audited artifact: `report/` LaTeX sources + built `../report/Abschlussarbeit_0510121.pdf` (208 pages, A4, twoside, 11pt, scrreprt).

---

## 1. Requirements extracted from the guidelines PDF

The document is a 9-item process/format sheet. It contains **no** margin, font, spacing, or page-limit rules — formatting and length are delegated to the degree program's regulations (item R3). Every stated requirement:

**R1 — Writing period.** "The writing period begins on the date set by the Examination Office. […] The writing period ends on the date specified on the form." (item 1)

**R2 — Extensions.** "Applications for extensions are to be submitted to the Examination Office **before the writing period ends**." Illness: sick note "within five days following the start of your sick leave"; content-related: "a statement from the first examiner to the relevant examination committee." (item 2)

**R3 — Program regulations govern.** "Essentially, the study and examination regulations of your degree program apply. This may mean that your thesis will need to include a short summary in German and/or English." (item 3)

**R4 — Non-German thesis.** "If a thesis is **not** in German, the examiner's approval must be provided when submitting the application for admission to the thesis. In such cases, **a short summary in German must also be included with the thesis**." (item 3)

**R5 — Group work.** "For group work projects, individual contributions must be clearly identifiable." (item 4) — N/A, single-author thesis.

**R6 — Citation and quotation marking.** "Quotations and text contributions from other works […], whether quoted literally or paraphrased, must be cited clearly in the references. Longer passages of direct quotation should be clearly identified as such either by indenting, italicizing, setting in parentheses, or by other suitable means. Failure to use such methods […] could be seen as an attempt to plagiarize." (item 5)

**R7 — Generative AI use.** "The regulations regarding the use of generative AI tools may vary from faculty to faculty. You should check with your faculty and read the declaration of authorship in section 8 beforehand. As a rule, use is permitted for conducting language checks and improving the language of your own texts or for systematic research. […] Examination law requires that the work you submit is your own work and that you disclose any third-party texts/products used." (item 6)

**R8 — AI documentation (recommendation, not requirement).** "To ensure maximum transparency, **we recommend** documenting communication such as prompts, chat histories, and the use of text taken from chats (for example by copying a chat into a PDF document)." Also: "neither copyrighted material nor sensitive information of third parties (e.g. test persons) may be input into the software." (item 6)

**R9 — Physical submission (default mode).** "You must submit **two bound copies** of your thesis **and one digital copy** on a USB stick or CD/DVD to the Examination Office. The bound copy must be bound in a such a way that pages cannot be added or removed. The electronic version is to be submitted together with the bound copies and **not separately by email**." (item 7)

**R10 — Digital-only submission (alternative mode).** "You may submit **a digital version only of your thesis by email** with the approval of **both reviewers**. Please send your thesis as a PDF file to the relevant examination team or upload it to the cloud and send us the link. Please also include a photo or scan of your registration form. You must name the file as follows: **Abschlussarbeit_yourmatriculationnumber.pdf**" (item 7)

**R11 — Content of the submission email** (digital-only mode). The email must include:
- Name
- Matriculation number
- Degree type and program
- Name and email address of the first examiner
- Name and email address of the second examiner
- Title of the thesis
- "Declaration that the thesis was completed independently in accordance with Section 60 (8) of the General Study and Examination Regulations (AllgStuPO)."
- "For theses written in a language other than the language of examination stated in the study and examination regulations: Declaration that the thesis contains a summary in German." (item 7)

**R12 — Earliest acceptance.** "Final theses can only be accepted by the Examination Office after at least half the writing time […] has passed"; earlier submission needs a justifying statement from the first examiner endorsed by the committee. (item 7)

**R13 — Deadline proof.** Postmark / info-desk stamp / in-person date / "Date of receipt via email by the Examination Office". Sunday/holiday extension to next workday — "If you submit a digital version only, the specified submission date applies." (item 7)

**R14 — Affidavit placement and content.** "A sworn affidavit is to be included **as the first page of the thesis**, bearing the statement below." The prescribed statement ("Declaration of authorship") has four elements: (a) own unaided work, only listed sources used, all taken passages marked; (b) "Where generative AI tools were used, I have indicated the **product name, manufacturer, the software version used, as well as the respective purpose**"; (c) noting the Principles for Ensuring Good Research Practice at TU Berlin dated 15 February 2023 (with URL); (d) not submitted in same/similar form to any other examination authority. Signed: "Berlin, (date) … Signature". (item 8)

**R15 — Topic changes.** "You should inform us of any minor editorial changes or digressions from the agreed topic […] In the event of more substantial changes, you are required to obtain written approval from the examiners and examination committee and provide this, at the latest when submitting your thesis." (item 9)

### What the guidelines do NOT regulate
No page/word limit, no font/margin/spacing rules, no prescribed chapter structure, no rules on ToC/lists/appendices, no language rule for headings. Any length limit would come from the AllgStuPO / subject StuPO of the (still-placeholder) degree program — **check the program's StuPO once the course of study is confirmed**. For reference, the built PDF is 208 physical pages: front matter ≈ 26 pages (title, affidavit, task sheet, acknowledgements, abstract, AI-use page, ToC, lists i–vii+), content chapters 1–6 = arabic pp. 1–113, bibliography pp. 115–123 (~9 pp.), appendices A–G pp. 125–~182 (~58 pp.).

---

## 2. Compliance table

| # | Requirement | Status | File | Fix |
|---|---|---|---|---|
| R1/R2 | Writing period / extension mechanics | CANNOT-VERIFY (process, not document) | — | Confirm the end date on the assignment form; today is 2026-07-31. |
| R3 | Program StuPO applies (incl. possible length limit) | CANNOT-VERIFY | `report/01_Document_administration/b_Meta.tex` | Course of study is still `Mein Studiengang`; look up the real program's StuPO for summary-language and length rules. |
| R4a | Examiner approval for English-language thesis | CANNOT-VERIFY (process) | — | Should have been given with the admission application; confirm it was. |
| R4b | **German short summary included in the thesis** | **GAP — HARD BLOCKER** | `report/02_Prematter/e_Abstract.tex` | German section is a literal placeholder: `[Platzhalter --- die deutsche Zusammenfassung fehlt noch …]`. Translate the English abstract (the file's own TODO says translate last, after the outstanding CS + mathematics runs land). |
| R5 | Group work identification | N/A | — | Single author. |
| R6 | Citations clear; long direct quotes visibly marked | COMPLIANT (mechanism) / author spot-check | `report/05_Literature_and_Index/Bibliography.bib`, chapters | biblatex+biber with a printed bibliography (pp. 115–123) is in place; csquotes is loaded. Author should spot-check that any longer verbatim quotations are indented/italicized per R6. |
| R7/R14b | AI use disclosed with product, manufacturer, version, purpose | **GAP — BLOCKER (small fix)** | `report/02_Prematter/i_AIUse.tex` | Table structure is exactly right, but the Version cell is the placeholder `[versions used]` and there is a stray empty `[further tool]` row. Fill the version(s), delete or fill the extra row. Until then, affidavit clause 2 is a false statement. See §4. |
| R8 | Prompt/chat documentation | COMPLIANT (recommendation only) | — | "We recommend" — not mandatory. Author's plan (no prompt-log file, disclosure email) does not violate anything. See §4. |
| R9/R10 | Submission mode (2 bound + USB, or digital-only by email) | CANNOT-VERIFY (process) | — | Digital-only requires the **approval of both reviewers** — obtain it explicitly. File must be named `Abschlussarbeit_<matriculationnumber>.pdf` (matric number itself is still `XXXXXX` in the sources). |
| R11 | Email contents for digital-only submission | CANNOT-VERIFY-YET | — | Template for the email is in §4. Examiner names/emails and program are currently unknown/placeholders in `b_Meta.tex`. |
| R12 | Half-the-writing-time rule | CANNOT-VERIFY (process) | — | Only relevant if submitting unusually early. |
| R13 | Deadline proof | CANNOT-VERIFY (process) | — | For email submission the date of receipt counts and the Sunday/holiday extension does **not** apply — do not plan to the last calendar day if it is a Sunday/holiday. |
| R14 (placement) | Affidavit "as the first page of the thesis" | SOFT GAP / VERIFY | `report/main.tex` (order of `a_Cover` vs `b_Declaration`) | Currently: title page (p. 1), blank verso, affidavit (pp. 3–4). Strictly read, the guideline wants the affidavit first; the template's title-then-affidavit order is the near-universal practice and usually accepted. Ask the examination team; the fix is a two-line swap in `main.tex` if they insist. |
| R14 (content) | Affidavit wording covers the four prescribed elements | COMPLIANT | `report/02_Prematter/b_Declaration.tex` | The B/M-thesis branch is the official TU bilingual four-clause affidavit: own-work clause, AI clause, Satzung of 15.02.2023 with the exact URL, not-submitted-elsewhere clause. Content matches R14 (a)–(d). |
| R14 (signature) | "Berlin, (date) … Signature" | GAP (mechanical, at submission) | printed copies / submitted PDF | Signature lines exist but must actually be **signed** in both bound copies (or scanned/inserted into the PDF for digital-only). Note the date prints `\today` = build date; rebuild on (or set the date to) the actual submission date. |
| R15 | Title matches the registered topic | CANNOT-VERIFY | `b_Meta.tex` (`\mytitle`) | Confirm "Query-Adaptive Multidimensional Ranking for Agents in Dynamic Domains" is exactly the registered topic; any digression must be reported (minor) or approved in writing (substantial) at the latest at submission. |
| — | Task sheet | **GAP — HARD BLOCKER** | `report/02_Prematter/c_Task.pdf` | Currently a one-page dummy reading "[Dummy Thesis Task Sheet]". Replace with the real signed task/registration sheet. (Not demanded by this guidelines PDF, but the template reserves the slot and the office expects the registration form scan with an email submission anyway.) |
| — | Author identity block | **GAP — HARD BLOCKER** | `b_Meta.tex` | Placeholders throughout: `\autor` = "M. Sc. \\ First name middle name last name" (note: the stray leading "M. Sc." renders on the title page and above every signature line — delete it), `\mymatriculationnumber` = XXXXXX, `\courseofstudy` = "Mein Studiengang", `\myadvisor` = "My advisor, M.Sc.", `\germankeywords`/`\englishkeywords` = Schlüsselwort1…/Keyword1… (these also leak into the PDF/XMP metadata via `\jobname.xmpdata`), `\orcid` = XXXX… (harmless — only rendered on the dissertation cover). |
| — | Faculty/institute/supervisor block | **GAP — HARD BLOCKER** | `b_Meta.tex` lines 72–77 (in the "NOT TO BE CHANGED" region) | Title page prints "Fakultät III – Prozesswissenschaften / Institut für Prozess- und Verfahrenstechnik / Fachgebiet Dynamik und Betrieb technischer Anlagen" and supervisor "Prof. Dr.-Ing. habil. Jens-Uwe Repke", plus the **dbta logo** (`a_Cover.tex`, `Logo_dbta`) — all template defaults from the originating chair, almost certainly wrong for this thesis. Must be replaced with the real faculty (likely Fakultät IV), institute, Fachgebiet, supervisor, and that chair's logo (or no second logo). Despite the "NOT TO BE CHANGED" comment, these lines are exactly what has to change. |
| — | Title-page language | SOFT | `a_Packages.tex` (babel: `english, ngerman` → **ngerman is the main language**) | The English-language thesis carries a German title page ("Wissenschaftliche Arbeit…", "vorgelegt von", "Matrikelnummer"), German list headings ("Abbildungsverzeichnis", "Literaturverzeichnis") and a German-first affidavit. No guideline forbids this, but if an English title page is wanted, swap the babel option order to `ngerman, english`. Decide deliberately — it flips every `\iflanguage` block. |

---

## 3. Hard blockers, ranked by lead time

1. **Real task/registration sheet** (`c_Task.pdf` is a dummy). Needs the official form — if a signed original or scan has to be obtained from the supervisor/Prüfungsamt, this has the longest external lead time. For email submission, a photo/scan of the registration form must also accompany the email (R10).
2. **Reviewer approval for digital-only submission** (R10) — requires answers from **both** examiners; ask now if email submission is the plan. Without it, fall back to two bound copies + USB/CD (R9), which needs print/bind lead time instead.
3. **German abstract** (`e_Abstract.tex`) — the only translation task, and per the file's own TODO it is gated on the outstanding computer-science and mathematics runs landing in Chapter 6. That coupling makes it late-path: schedule the translation immediately after those numbers freeze. Blocking under R4b, and its absence would also falsify the email declaration in R11.
4. **Identity/faculty metadata** (`b_Meta.tex` + `a_Cover.tex` logo) — 30 minutes of editing once the correct faculty/institute/Fachgebiet/supervisor strings are confirmed. Confirm, don't guess: the current block belongs to the process-engineering chair that authored the template.
5. **AI-use table completion** (`i_AIUse.tex`) — fill the version cell, remove the empty row (minutes). Blocking because affidavit clause 2 asserts this table is complete.
6. **Signatures + date** — sign the affidavit in the submitted copies; rebuild so `\today` shows the submission date. Zero lead time but easy to forget.
7. **Filename** — submitted PDF must be `Abschlussarbeit_<matriculationnumber>.pdf`, which requires blocker 4's matriculation number.

Non-blocking but confirm with the examination team: affidavit page order (title page before affidavit vs. "first page of the thesis", R14).

---

## 4. AI-disclosure judgment

**Does `i_AIUse.tex` + the email plan satisfy the guidelines?** Yes in structure, not yet in content.

- What the guidelines actually **require** (R7 + R14b) is the affidavit clause plus the disclosure of "product name, manufacturer, the software version used, as well as the respective purpose". The thesis satisfies this *in the document itself*: the affidavit (`b_Declaration.tex` clause 2) is the exact official wording, and `i_AIUse.tex` is a bilingual page with precisely the required four-column table (Product / Manufacturer / Version / Purpose), citing the Satzung of 15.02.2023. This is the right mechanism — the disclosure the affidavit refers to should live in the thesis, and it does.
- **Two content gaps make the page (and hence the affidavit) currently false:** the Version cell reads `[versions used]` and a placeholder row `[further tool]` prints as an empty table row. Fill the actual CLI/model versions used over the working period, add any other tools (DeepL, Copilot, …) or delete the row.
- **The prompt-log question:** R8 is explicitly a recommendation ("we recommend documenting communication such as prompts, chat histories"), not a requirement. Submitting no prompt-log file is compliant. A faculty-level rule could be stricter (R7: "regulations … may vary from faculty to faculty") — one more reason to pin down the actual faculty (blocker 4) and check its policy.
- **The disclosure email is supplementary, not a substitute.** Nothing in the guidelines provides for delivering the AI disclosure by email; the in-thesis page is what the affidavit points at, so the page must be complete regardless of the email. The email is harmless extra transparency — but its content must match the in-thesis table exactly (same tools, same versions, same purposes); a discrepancy between the two would itself look like an incomplete disclosure.

**What the submission email must contain** (this is required by R11 whenever the digital-only route is used, independent of the AI topic):

> - Name: …
> - Matriculation number: …
> - Degree type and program: Master of Science, <program>
> - First examiner (name + email): …
> - Second examiner (name + email): …
> - Title of the thesis: Query-Adaptive Multidimensional Ranking for Agents in Dynamic Domains
> - Declaration that the thesis was completed independently in accordance with Section 60 (8) AllgStuPO.
> - Declaration that the thesis contains a summary in German. *(required because the thesis is in English)*
> - Attachment 1: `Abschlussarbeit_<matriculationnumber>.pdf`
> - Attachment 2: photo/scan of the registration form
> - (Optional, author's plan) AI-use disclosure restating the `i_AIUse.tex` table, plus prompt/chat documentation if the faculty asks for it.

Note the second declaration is only truthful once the German abstract exists (blocker 3), and the whole email is only possible once both reviewers have approved digital-only submission (blocker 2).

---

## 5. Guideline requirements the template has no slot for

1. **Registration-form scan for email submission** (R10) — nothing in `report/` holds it; it travels as an email attachment. Keep a scan ready alongside the real task sheet.
2. **§60(8) AllgStuPO declaration and German-summary declaration** (R11) — email-body text, no template slot; draft from §4 above.
3. **Reviewer approvals for digital-only submission** (R10) — correspondence outside the document; archive them.
4. **Statement for early submission** (R12) and **written approval for substantial topic changes** (R15) — separate documents from examiner/committee, only if applicable.
5. **Second examiner** — the template's B/M-thesis cover has slots only for supervisor and advisor; the second examiner appears nowhere in the document. That is fine for the document, but the name and email are needed for the submission email (R11), so obtain them.
6. **Binding constraint** (R9: "pages cannot be added or removed") — a print-shop instruction (adhesive/thermal binding, no ring binders), not a LaTeX concern; relevant only if the digital-only route falls through.

---

## Bottom line

The document architecture is already guideline-conformant: correct official affidavit, a proper AI-disclosure page, abstract slots in both languages, task-sheet slot, bibliography. Everything that blocks submission is placeholder content, in five files: `b_Meta.tex` (identity + faculty block + keywords), `c_Task.pdf` (dummy), `e_Abstract.tex` (German abstract missing), `i_AIUse.tex` (version cell + stray row), and the two process items that need other people — reviewer approval for email submission and the signed task sheet. No formatting rework is needed; the guidelines impose no page limit, so the 208-page count is a StuPO question, not a Hinweise question.
