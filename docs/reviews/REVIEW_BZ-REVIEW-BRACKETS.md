# REVIEW: BZ-REVIEW-BRACKETS (benchzoom `review-brackets`, b86c014..798521c; five insertion-only plan-doc brackets)

2026-10-28. Authority: D-2026-10-28-1 (with D-2026-10-27-4/-5); scope = the registrar's list "BENCHZOOM DOC BRACKETS
OWED" (TaxoArena ab5222fe, `docs/judge_v2_program.md` L25757 _as_of d78972f2). Reviewer: zero LLM calls; read-only on
both repos except this file; one pytest run (TMP/TEMP/TMPDIR/basetemp in `E:/TaxoArena_tmp/rev_review_brackets_124718`,
BLAS 1, one process).
Object: worktree `Z:/FAC/TUBerlin/benchzoom_wt_review-brackets`, branch `review-brackets`, tip 798521cf9de4 (1 commit),
parent = master b86c014 (master tip unchanged; fast-forward), 0 remotes, worktree clean (`git status --porcelain | wc -l`
= 0, before and after my test run).

## Verdict

**BRACKETS CONFIRMED AS OWED (exact words, insertion only, LF kept, no code). MERGEABLE (merge_ok yes, fast-forward).**
No BLOCKER, no HIGH. One MEDIUM follow-up outside this branch's scope (F1), two LOW wording notes (F2, F3).

## Per-claim table (deciding claims)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Docs only, 5 files, no code | `git diff --name-only b86c014 798521c \| wc -l` = 5, all `docs/<x>.md`; 0 under src/ examples/ tests/; execution graph not owed | CONFIRMED | - |
| 2 | Insertion only: numstat 19/17/20/10/7, 0 deletions | numstat embed2 19/0, bbh 17/0, planted 20/0, tau 10/0, design 7/0. Stronger: for each file the first `size(b86c014 blob)` bytes of the 798521c blob hash to the b86c014 blob (5/5 Y) | CONFIRMED | - |
| 3 | Line endings: blobs LF 0 CR; working copies uniform CRLF | CR bytes in committed blobs old 0 / new 0 (5/5); working copy CR count = line count (364/343/281/290/308); `git hash-object <wt file>` = tip blob (5/5; autocrlf=true, no .gitattributes). Tip LF blobs: embed2 `blob:2b4bb2c8`, bbh `blob:e34cca50`, planted `blob:3b62dde2`, tau `blob:0b901a47`, design `blob:c3f1cc81` | CONFIRMED | - |
| 4 | Inserted spans L346-364 / L327-343 / L262-281 / L281-290 / L302-308, one blank separator each | Own line counts: identical; first inserted line empty in all 5 | CONFIRMED | - |
| 5 | 25/25 quoted spans occur verbatim in the review or the plan | Own script (whitespace-normalised, insertion = new[len(old):]): 25 spans, 25 found; 23 in the POSTRUN, 10 in the b86c014 plan (8 in both). Every quote that states a NEW wording is in the POSTRUN's fix text; every quote of OLD wording is in the plan | CONFIRMED | - |
| 6 | Each bracket answers its review (exact words) | Per file below; severities match the POSTRUNs (D1-D4 MEDIUM; C1 HIGH, C2/C3 MEDIUM; Q1 HIGH, Q3 MEDIUM, Q5 LOW; L1/L2 LOW); each bracket cites its review commit (1 hit each) and ab5222fe (1 each); the 5 review files have one commit each (unchanged since) | CONFIRMED | - |
| 7 | Every defect id is carried or named as not carried | embed2 D1-D4 carried, D5-D8 named; bbh C1-C3 / L1-L5; planted Q1, Q3, Q5 / Q2, Q4; tau L1, L2 / C1-C3, L3-L4; design L1 / C1-C4, L2-L6. Full partition of each POSTRUN's defect list (counted against the review files) | CONFIRMED | - |
| 8 | Numbers in the brackets | Every numeric token of the 5 insertions occurs in its POSTRUN or plan except commit/date fragments (ab5222fe, 56da993f, d8441df7, 2026-10-28). Spot check, weaker than row 5 (my M1 shows a 1-digit change can survive it) | CONFIRMED (spot) | - |
| 9 | tau L1 pin: `examples/mmlu_confirm_items.py` is sha256-lf16:bf48432fa5460a30, CRLF 1af0b528f4072413; e977fffa is `CATEGORIES_PY_SHA256` | `git show b86c014:<file> \| sha256sum` bf48432fa5460a30; CRLF rendering and working file 1af0b528f4072413; L57 `CATEGORIES_PY_SHA256 = "e977fffa..."`; plan section 6 (b) L150-152 "file sha256 e977fffa..." | CONFIRMED | - |
| 10 | No test reads these docs; five tests 19 passed, 3 deselected; full suite 941 passed | `grep -rlE '<5 names>' tests \| wc -l` = 0, src 0; the 5 runners name the plan only as a label and in tau-cont-all's `git status --porcelain` dirty check (a committed bracket leaves it clean; no runner reads plan content). Own run of the 5 test files: 19 passed, 3 deselected (160 s). Full suite NOT re-run by me (docs-only, 0 references) | CONFIRMED | - |

Per-file mapping (bracket wording vs the POSTRUN's words; spans in the b86c014 plan located by grep):
- embed2-work [P3]: answers POSTRUN_EMBED2-WORK L28-29 verbatim. D1 old span = plan L330 reading (1); D1/D2/D3/D4 fix
  words = review L55-56, L60-61, L65-66, L68-69. D3 omits "(K MMLU 0.89)" and D4 omits "as in POSTRUN_V5-ORTH D2": no
  change of meaning.
- bbh-work [P3]: C1 quote = review L75-76 verbatim; fix "registrar brackets [P2] reading (2)" (L77) answered, widened to
  [P2]'s words and PB4 (plan L176, L299-300, L320-321). C2 old span plan L320 reading (1); new words review L81-82. C3 old
  span plan L322 reading (3); new words review L87-88; "is informative only about the axis rule's split choices" = plan L166.
- planted-power [P2]: answers review L19-20 and Q5 L82. Old spans plan L236-237 (rule line) and L254 (reading (1));
  "ideal reader" / "attainable scale" occur in the plan (L70, L88, L163, L183) and [P1] (L247, L249, L258) as claimed.
- tau-cont-all [P2]: L1 = review L119-122; L2 = review L123-124; [P1] (a) L263-264 prints both regimes as the bracket says.
- design-surface [P3]: L1 = review L82-84; old span plan L294 inside reading (1).

## Defects / follow-ups (none blocks the merge)

- **F1 MEDIUM (outside this branch's scope; orchestrator's call): two readout tables keep the unqualified wording.**
  design-surface [P2] reading (4) "does not help ... and trails K' everywhere" (L296-297) and reading (5) "MDE80 is below
  the draft's distances for D_K (0.150 < 0.17)" (L297-298), and tau-cont-all [P1] reading (1) "keep sign and 3-SE status"
  (L274), are exactly what POSTRUN_DESIGN-SURFACE C1/C3 and POSTRUN_TAU-CONT-ALL C1 qualify. The new brackets only point
  to them ("not carried by this bracket (see the POSTRUN and the registrar's record)"); the registrar's record carries
  the qualifiers (prog L25740-25760). Since D-2026-10-28-1 makes the cell-aware SE PRIMARY for BZ-AXIS-CONFIRM-FRESH,
  C3's line "for D_K, 'below the draft's distance' does not survive under the cell-aware SE" now bears on the next
  registration's planning, and the runner docstring names design-surface.md [P2] as its readout. Fix: a further
  insertion-only bracket ([P4] design-surface carrying C1's and C3's fix words; [P3] tau-cont-all carrying C1's quote),
  or the registration cites the POSTRUNs rather than these readings.
- **F2 LOW (planted-power Q1 mapping).** The bracket maps reading (1)'s "by up to x2.3 for the random-cell reader" onto
  "x1.38-1.65 on the 9 degeneracy-free pairs ...", a range that excludes RND (the 9 pairs are V0/K/N x the three 0.10
  structures; all RND and NONE pairs are degenerate). It follows the review's Q1 quote rule literally, and the RND reading
  is carried by the next clause ("degeneracy-inflated (non-degenerate 0.91-1.69)"). Fix (optional, next bracket): say
  the RND clause is not quoted and RND reads only as degeneracy-inflated.
- **F3 LOW (bbh C2 substitution).** Replacing reading (1)'s "DEFF 11-15 from templated items" by the review's words
  drops the number from the substituted text; the bracket keeps it in its next sentence. Follows the review verbatim. No fix.

## Own mutants (on my own checks; sandbox copies under the session scratchpad, never the repo)

| id | change | result | decisive |
|---|---|---|---|
| M1 | one digit in a quoted span (planted "x1.38" -> "x1.39") | quote check killed (24/25); number spot check SURVIVED | yes (row 5); row 8 named spot |
| M2 | one byte deleted inside the old part of design-surface | prefix assertion killed | yes (row 2) |
| M3 | same deletion, sandbox git repo | numstat 8/1 (deletion seen) | yes (row 2) |

## Commands (worktree Z:/FAC/TUBerlin/benchzoom_wt_review-brackets; scripts quotes.py / nums.py in the session scratchpad)

```
git log --oneline -3; git rev-parse master; git remote -v | wc -l; git status --porcelain | wc -l      # b86c014; 0; 0
git diff --numstat b86c014 798521c; git diff --name-only b86c014 798521c | wc -l                       # 5 files, 0 del
for f in <5>; do git show 798521c:docs/$f.md | head -c $(git cat-file -s b86c014:docs/$f.md) | git hash-object --stdin; \
  git rev-parse b86c014:docs/$f.md; git show <c>:docs/$f.md | tr -cd '\r' | wc -c; tr -cd '\r' < docs/$f.md | wc -c; \
  wc -l < docs/$f.md; git hash-object docs/$f.md; done                                                    # 5/5 prefix, LF, CRLF wt
python -I quotes.py <scratch>    # 25 quoted spans: 25 found (POSTRUN or b86c014 plan)
python -I nums.py <scratch>      # numeric tokens: only sha/date fragments missing
git show b86c014:examples/mmlu_confirm_items.py | sha256sum; ... | sed 's/$/\r/' | sha256sum           # bf48432f.. / 1af0b528..
grep -rlE 'embed2-work\.md|bbh-work\.md|planted-power\.md|tau-cont-all\.md|design-surface\.md' tests | wc -l   # 0 (src 0)
PYTHONPATH=src python -m pytest tests/test_{embed2_work,bbh_work,planted_power,tau_cont_all,design_surface}.py -q   # 19 passed, 3 deselected
grep -n 'BENCHZOOM DOC BRACKETS OWED' docs/judge_v2_program.md                                           # L25757 (TaxoArena)
```

## Delta review 2026-10-28: `review-brackets-2` (06c075f..abd820c; the F1 and F2 brackets)

Object: worktree `Z:/FAC/TUBerlin/benchzoom_wt_review-brackets-2`, branch `review-brackets-2`, tip abd820c4d4d5 (1
commit), parent = master 06c075f (master tip unchanged; fast-forward), 0 remotes, worktree clean before and after my test
run (`git status --porcelain | wc -l` = 0). Scope: the diff only; rows 1-10 above (798521c) are cited, not re-derived.
Authority D-2026-10-28-1/-2. Zero LLM calls; read-only except this file.

**Verdict: F1 AND F2 BRACKETS CONFIRMED (exact words 36/36, insertion only, LF, docs only). MERGEABLE (merge_ok yes,
fast-forward).** No BLOCKER, HIGH or MEDIUM. Two LOW notes (G1, G2); one relay outside this branch (G3).

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| D1 | Docs only, 3 files | `git diff --name-only 06c075f abd820c \| wc -l` = 3 (docs/design-surface, tau-cont-all, planted-power .md); 0 code | CONFIRMED | - |
| D2 | Insertion only 33/0, 17/0, 7/0 | numstat design 33/0, tau 17/0, planted 7/0; the first size(06c075f blob) bytes of each abd820c blob hash to the 06c075f blob (3/3 Y) | CONFIRMED | - |
| D3 | Blobs LF, working copies CRLF | CR in blobs old 0 / new 0 (3/3); working CR count = line count 341/307/288; `git hash-object <wt>` = tip blob (3/3; autocrlf true, no .gitattributes). Tip pins (LF of record): design `blob:d3deff67` sha256-lf16:7a2cab3d8755617f (sha256-crlf16:cced0d348f9d22ef); tau `blob:4f84f528` lf16 4c7a4e18afea5a69 (crlf16 fd7a8762a1638aa7); planted `blob:cba482b2` lf16 ca1d30acd0f28ec4 (crlf16 8802fc05e2c648ec) | CONFIRMED | - |
| D4 | Spans design [P4] L310-318, [P5] L320-341; tau [P3] L292-307; planted [P3] L283-288 | identical; separators L309, L319, L291, L282 empty; inserted lines <= 120 chars, 0 non-ASCII | CONFIRMED | - |
| D5 | 36/36 quoted spans verbatim | own `quotes2.py` (whitespace-normalised, insertion = new[len(old):]): 36 spans, 36 found, each in the source the bracket names: C1/C3 in POSTRUN_DESIGN-SURFACE; C1 + row 10 in POSTRUN_TAU-CONT-ALL; F2's "the 9 pairs ..." in this file L56-57; the D-2026-10-28-1 Meaning in the decisions file at f81992b1 (D-1's text byte-identical to d78972f2); "the declared resampling SE_cell decides" at prog L25763 at f81992b1 (= HEAD; last programme commit a9138c19); "NO n* IS LICENSED" in POSTRUN_FRESH-SIZE and benchzoom docs/fresh-size.md; old wording in the 06c075f docs. The unquoted "C3 goes on, verbatim: So for D_K, ..." sentence is verbatim in C3 L75-76 (True) | CONFIRMED | - |
| D6 | Numbers | `nums2.py`: every numeric token of the 3 insertions is in its sources except commit/line fragments (25763, f81992b1, b8968b42). Spot check (M6) | CONFIRMED (spot) | - |
| D7 | Each bracket answers F1 / F2 in the review's words | per bracket below | CONFIRMED | LOW (G1, G2) |
| D8 | No test or runner reads these docs | `grep -rlE '<3 names>' tests \| wc -l` = 0; the 3 runners use PLAN only as a label/record field and in tau's dirty-check list (L919); no plan pin. Own run of the 3 test files: 11 passed, 2 deselected (98 s). Full suite not re-run (docs only, 0 readers; builder's 958 passed cited) | CONFIRMED | - |
| D9 | Cited commits | 5fb34baa, 1d23c3c7, 8f0f5f1c, b8968b42, 613c1c03 = the named review (one commit each, clean); d78972f2 / f81992b1 = D-2026-10-28-1 / -2; a9138c19 = L25763; ab5222fe's programme insertion carries "MDE80 0.196 at m 2.76", "clustered (SUBSTITUTED), lower bound", "0.18-0.30", "content-cluster SE; under V0-leaf SE ..." (1 hit each), so "also carries" holds | CONFIRMED | - |

Per bracket (review sentence -> bracket):
- design [P4] = F1 / POSTRUN_DESIGN-SURFACE C1 (L58-65). Old span [P2] reading (4) (06c075f L296-297). C1's fix words
  carried exactly: the KILLED qualifier quote; never "nesting does not help" without it; "Trails K' everywhere" true of
  point estimates only. "KILLED (pre-specified)" matches [P1]'s printed "NEST RULE (pre-specified, ...)". Not owed, not
  carried: C1's NEST SE 0.0825 vs 0.017 and power <= 0.07 sentences.
- design [P5] = F1 / C3 (L70-78). Old span reading (5) (L297-300). The cell figures are matched correctly ([P2] prints P
  "0.310 cell / 0.182 meter"; 0.182 = C3's meter P); the label "clustered (SUBSTITUTED), lower bound", C3's meter row,
  D_K 0.18-0.30 and "does not survive" are verbatim; not extended to D_N / G(N|L2+V0) (C3 gives an SE_cell figure for
  D_K only: true). C3's fix order (meter first) is not adopted because its premise D-2026-10-27-5 B is replaced
  (D-2026-10-28-1); the order is left to the registrar, consistent with F1's alternative. Not a defect.
- tau [P3] = F1 / POSTRUN_TAU-CONT-ALL C1 (L91-104) + row 10. Fix quote and leaf DEFF / n_eff verbatim; "-3.41 (f2) ->
  -2.98 (cont)" matches [P1] L250-256 (rule O "z f2 -> cont"; the leaf line tagged descriptive).
- planted [P3] = F2 (this file L55-59). Fix carried: "reading (1)'s RND clause is not quoted"; RND reads only as
  "degeneracy-inflated (non-degenerate 0.91-1.69)".

Defects (none blocks the merge):
- **G1 LOW ([P5], which clause names the deciding SE).** The bracket quotes L25763's "the declared resampling SE_cell
  decides", which sits in the record's paragraph "A. P DECIDES ON SE_cell"; D-2026-10-28-2 (1) has since removed P's
  pass/fail word, while the bracket says D-2026-10-28-1 is "kept by D-2026-10-28-2" without saying that. The D_K
  inference holds on the same line's F clause ("the SE every F contrast already decides on"), which is not quoted. Also,
  C3's meter row is "(my interpolation, same rule)" in C3; the bracket drops the parenthesis (attribution to C3 kept).
  Fix (optional; next bracket or the registration): quote the F clause and add "P carries no pass/fail word
  (D-2026-10-28-2)".
- **G2 LOW (tau [P3], a leg dropped).** C1's "MATH V0 - random is within 3 SE in both regimes (+2.02 / +2.06)" (V0-leaf
  SE) is not carried. C1's fix quote does not require it and V0 vs random is not a FRESH deciding comparison, but with
  the cell-aware SE now primary a reader may take MATH V0 vs random as 3-SE under the leaf SE. Fix (optional): carry it
  beside -3.41 -> -2.98.
- **G3 relay (registrar; outside this branch).** The programme, queue and results carry 0 occurrences of D-2026-10-28-2
  (`git grep -c` prints no file); L25763's "A. P DECIDES ON SE_cell ... the POINT against 3 SE_cell decides" stands
  unbracketed against D-2026-10-28-2 (1) "P is reported with its interval and carries no pass/fail word".

Own mutants (sandbox copies `mut_M4..M6` in the session scratchpad; never the repo):

| id | change | result | decisive |
|---|---|---|---|
| M4 | one digit in the tau row-10 quote (n_eff 1,998 -> 1,989) | quote check killed (35/36); number check killed | yes (D5) |
| M5 | one byte deleted in the old part of planted-power | prefix assertion killed | yes (D2) |
| M6 | unquoted [P5] figure 0.18-0.30 -> 0.18-0.31 | quote check SURVIVED (unquoted); number check killed | yes (D6 is the only guard of unquoted figures) |

Commands (worktree `Z:/FAC/TUBerlin/benchzoom_wt_review-brackets-2`; scripts `quotes2.py`, `nums2.py` in the session
scratchpad `rb2/`):
```
git rev-parse HEAD master; git merge-base --is-ancestor master HEAD; git remote -v | wc -l; git status --porcelain | wc -l
git diff --numstat master HEAD; git diff --name-only master HEAD | wc -l                         # 33/0 7/0 17/0; 3
for f in design-surface tau-cont-all planted-power; do git show HEAD:docs/$f.md \
  | head -c "$(git cat-file -s master:docs/$f.md)" | git hash-object --stdin; git rev-parse master:docs/$f.md; \
  git show HEAD:docs/$f.md | tr -cd '\r' | wc -c; tr -cd '\r' < docs/$f.md | wc -c; git hash-object docs/$f.md; done
python -I quotes2.py rb2; python -I nums2.py rb2                                                 # 36/36; fragments only
git -C <TaxoArena> show f81992b1:docs/judge_v2_program.md | sed -n 25763p                         # P paragraph + F clause
grep -rlE 'design-surface\.md|tau-cont-all\.md|planted-power\.md' tests | wc -l                  # 0
PYTHONPATH=src python -m pytest tests/test_{design_surface,tau_cont_all,planted_power}.py -q -p no:cacheprovider  # 11 passed
git -C <TaxoArena> grep -c 'D-2026-10-28-2' HEAD -- docs/judge_v2_program.md docs/agents/queue.json docs/agents/results/
```
