# DRAFT registration: BBH-RESERVED-CONFIRM (lead #4), the one-time read of BBH's sealed RESERVED side

STATUS: DRAFT for the registrar and the author. NOT REGISTERED; nothing sealed has been opened; zero LLM calls. Written by
the engine coder under D-2026-11-06-3 item (3) (`docs/agents/author_decisions/2026-11-06.md`, b42c3300; the author's
selection, verbatim, "Prepare BBH only (Recommended)", read there as "build the BBH sealed-side test and its
training-side estimate; nothing sealed is opened; the main session comes back to the author before the one-time opening
(and for the roster 128/342 and text admissibility)"). Lead #4 of `docs/agents/plans/2026-11-06_leads.md` (b42d58ef). The
author's open choices are written as OPTIONS below, not decided. Every number here is copied from the WORK estimate of
record (benchzoom `docs/bbh-reserved-prep.md` [P2], branch `bbh-reserved-prep` fa37758; EXPLORATORY, WORK rows only) or
from the record with its pointer ("prog" = `docs/judge_v2_program.md`); arithmetic of my own is marked "(coder's
arithmetic)". If registered, the heading would read: `## Registered <date> (before any code or call) — BBH-RESERVED-CONFIRM:
on BBH's sealed RESERVED side, does a per-subtask policy fitted on WORK beat the best single model, and do label-free cells
recover at least half of that gain? (zero-call; one-time sealed read)`.

## Question

README key result 1 rests on V2-DECLARED-CELLS (union EVAL, 18 models, content-closed v2 split): "G +2.67pp [+1.46,
+3.89], n 5,907 [BBH carries 0.728 of G; leave-BBH-out and MMLU-Pro intervals contain 0, DESCRIPTIVE]" (prog L21927). BBH
has a second, never-read response side: the 2,304 RESERVED items of SPLIT-1 (benchzoom `docs/bbh_census.md` [C-4]; RESERVED
responses read 0 by BBH-WORK, prog L25747-L25758, and by BBH-HIER, prog L25864-L25871). On it, with an Open LLM Leaderboard
roster, (C1) does the per-subtask policy fitted on the 3,457 WORK items beat the best single model fitted there, (C2) do
label-free cells (spherical k-means at the subtask count, k = 24, on the qwen3 512-d text vectors) beat it, and (C3) do
they recover at least half of the declared gain? C1 makes key result 1's BBH part a second-roster, sealed-side statement
(SQ5) or refuses it; C2 / C3 test the framing's last clause ("Cells are declared labels for the arena, and are read by a
TRAIN-only embedding taxonomy where labels are missing", framing of record L20) on the corpus where routing pays.

## Hygiene

- Split word: "the sealed RESERVED side of BBH SPLIT-1 (seed 20261027; ND-1 groups kept to one side; stratified by
  subtask; pins sha256-lf16:3d4d644a7ac34d22 / sha256-lf16:9ef05cc2cfe34c91)". NOT "content-closed": no CK-CLOSE check
  exists for BBH (framing S3; open item H1). The opening prints, beside, the RESERVED rows with a WORK cosine twin
  (>= 0.98, text only) and G_DEC without them.
- Read once, at the opening, and nothing else: the 2,304 RESERVED items' text (item columns of one part; census sha
  checked) and vectors (the pinned BBH npz, sha256 0e9ef33a...), and the acc_norm of the 2,304 RESERVED items for the
  registered roster's models only (R128: 294,912 values; R342: 787,968; coder's arithmetic). Under R128 the other 214
  KEPT models' RESERVED responses stay unread.
- Before the opening, the WORK side only, through the WORK estimate's loaders and its access audit (every parquet read
  filtered on WORK ids). The frozen WORK-side object (models, best single, DEC / FAM / PLACEBO policies, the FK centroids,
  the anchor-free tree's descent table, all policies) is written write-once by `freeze`; its sha256 is pinned in the
  runner (`FREEZE_SHA`) and bracketed into this registration BEFORE the opening; `open` recomputes it from WORK and
  refuses on any byte difference.
- The opening ledger `OPENED.json` is written (mode x) before the first RESERVED byte; a second opening refuses; any
  failure after the ledger (G4, an incomplete matrix) is recorded as `outcome_REFUSED_<UTC>.txt` and never retried.
- Zero LLM calls; CPU, one process; no TaxoArena pool or DB is read (BBH is benchzoom's corpus; rule 7 is not engaged);
  outputs never committed (`E:/benchzoom_demo/followups/bbh-reserved-confirm`, backup
  `E:/TaxoArena_backup_<date>_bbh-reserved-confirm` with SHA256SUMS).

## Instrument

benchzoom `examples/bbh-reserved-confirm.py` (branch `bbh-reserved-prep`, tip a922fe7, LF blob e0a6d70e; AST-identical
outside the module docstring to fa37758's blob d37382c8, at which the dry runs below ran), importing
`examples/bbh-reserved-prep.py` (LF blob dafd9eda, the WORK estimate's runner of record, unchanged since its run). Modes:
`reserved --dry-run --roster R --text T` (WORK side only; prints what the opening would read; refuses to open), `freeze`
(refused unless the registration constants are set and equal to the CLI), `open --registration <sha>
--open-sealed-reserved` (refused unless every condition of `open_refusals` holds: the flag; `REG_COMMIT`, `REG_ROSTER`,
`REG_TEXT` set and equal to the CLI; a clean committed tree; no outcome and no ledger; `FREEZE_SHA` set and equal to the
frozen file's sha256; every prediction target set). All four constants are PENDING at fa37758. Policies: per cell the
roster model with the largest summed WORK correctness (ties: first name in sorted order; an empty cell gets the best
single), as ROUTER-CLEAN-POLICY / V2-DECLARED-CELLS. Two-stage bootstrap B = 2,000 (`default_rng([20261106, 7])`):
WORK content clusters resampled within subtask with every policy refitted (cells fixed), then RESERVED content clusters
within subtask; content clusters = BBH-WORK's union (cos >= 0.98 on the 4,096-d rows UNION the census ND-1 group). Deciding
interval = point +- 1.96 x SE2; the percentile interval, the one-stage (policy frozen on WORK; `default_rng([20261106,
9])`) SE, the i.i.d. SE, DEFF, n_eff and MDE80 = 2.80 x SE2 printed beside every statistic. Selftest S1-S11 on synthetic
fixtures (109 checks); mutants 61 of 61 killed (table in the runner's docstring).

## Author's choices (options; nothing is decided here)

O1 Roster (D-2026-10-28-1 item 4 kept 128 for WORK; the leads file names 128 or 342).
- (a) R128, the seeded 128 of BBH-WORK (ids sha256 c47b3eb5...). WORK estimate: G_DEC +3.27pp (design A), projected SE
  1.24pp, power of C1 0.75, of C2 0.87, of C3 0.61 (lower bound 0.49). Leaves 214 models' RESERVED responses unread (a
  second sealed roster stays possible).
- (b) R342, all KEPT (ids sha256 71c12468...). WORK estimate: G_DEC +5.38pp, projected SE 1.34pp, power of C1 0.98, of C2
  0.995, of C3 0.91 (lower bound 0.81). Reads the whole sealed side.
- The best single is the same model at both rosters on WORK (internlm/internlm2_5-20b-chat, WORK accuracy 0.7382).

O2 Text admissibility for a RESERVED claim (BBH-WORK L3).
- (a) WORK texts only (inductive): every cell is fitted on the 3,457 WORK texts; the RESERVED texts are read only at the
  opening, to assign rows to cells (nearest unit centroid; nearest-child descent of the tree); C2's arm FK-I; the claim
  may say "a TRAIN-only embedding taxonomy"; V0 / V0m (fitted on all 5,761 texts) are not used.
- (b) all 5,761 texts admissible (transductive; V0's convention): FK-T and AF-T are fitted on all texts at `freeze`
  (before the opening it reads the RESERVED texts, no response, under a text-only audit that refuses any RESERVED score);
  C2's arm FK-T; the claim reads "cells fitted on all items' text (no response)", never "TRAIN-only".
- WORK estimate of the difference: |G_FKT - G_FKI| = 0.02pp (R128) / 0.11pp (R342); S_FKT 1.000 / 1.010 against S_FKI
  1.008 / 0.991 (the within-WORK analogue of (b)). The runner supports both; the option must be registered before `freeze`.

O3 Whether and when to open (the side is a one-shot resource), and which words of the record may cite the outcome: C1
for key result 1's BBH part as a second roster on a sealed side; C2 / C3 for the framing's last clause only under O2 (a).

## Readouts and criteria (disjoint; the INTERVAL decides each; the point decides only F1)

- T1 VALIDITY TRIGGER (evaluated first): the placebo (the 24 subtask labels permuted over all 5,761 items, sizes kept,
  `default_rng([20261106, 8])`; policy fitted on WORK) gain G_PLACEBO = acc_R(PLACEBO) - acc_R(BS): if its interval lies
  wholly above 0, C1-C3 read "UNDETERMINED (BY TRIGGER: T1 the placebo manufactures gain)", F1 is NOT EVALUATED, every
  prediction is UNDETERMINED (BY TRIGGER).
- G4 REFUSAL: a two-stage SE of 0 for G_DEC, G_FREE, G_PLACEBO or L refuses (a degenerate interval; never a verdict).
- C1 DECLARED GAIN: G_DEC = acc_R(DEC) - acc_R(BS), both fitted on all WORK rows: HELD iff wholly above 0; FAILED iff wholly
  below 0; UNDETERMINED otherwise.
- C2 LABEL-FREE GAIN: G_FREE = acc_R(FREE) - acc_R(BS), FREE = FK-I under O2 (a), FK-T under O2 (b) (k-means at k = 24, 5
  seeds, the arm's value the mean over seeds): the same three words.
- C3 AT LEAST HALF RECOVERED: L = G_FREE - 0.5 x G_DEC = acc_R(FREE) - 0.5 acc_R(DEC) - 0.5 acc_R(BS) (the share
  S = G_FREE / G_DEC exceeds 0.5 iff L > 0 when G_DEC > 0): NOT EVALUATED unless C1 is HELD; then HELD iff L's interval
  lies wholly above 0, FAILED iff wholly below 0, UNDETERMINED otherwise.
- Exclusivity: each criterion's three words are disjoint inequalities on one interval; C3 is gated on C1's HELD; T1 pre-empts
  all; no two criteria share a deciding statistic.
- PRINTED BESIDE (deciding nothing): S with its two-stage percentile interval; the anchor-free tree arm (AF-I under O2 (a),
  AF-T under (b); the axis_v1 recipe without groups, BBH-HIER's AF on WORK: 43 nodes / 22 leaves) with its gain and
  share; FAM (the 20 families); ORACLE; M = acc_R(FREE) - acc_R(DEC); per-subtask contributions; the leave-one-subtask-out
  range; the RESERVED rows with a WORK cosine twin and G_DEC without them; the one-stage interval of every statistic.

## Predictions (from the WORK estimate; no RESERVED value seen; 80 % ranges = design-A point +- 1.2816 x SE_proj)

| id | prediction | R128 | R342 | basis |
|---|---|---|---|---|
| P1 | C1 is HELD | 0.75 | 0.98 | power at the design-A point (projected two-stage SE) |
| P2 | G_DEC lies in the range | [+1.68, +4.86]pp | [+3.67, +7.10]pp | design A +3.27 / +5.38, SE_proj 1.24 / 1.34 |
| P3 | C2 is HELD | 0.87 | 0.995 | design A G_FKI +3.29 / +5.33, SE_proj 1.07 / 1.17 |
| P4 | S lies in [0.70, 1.30] | 0.85 | 0.90 | design A S_FKI 1.008 / 0.991; design-B mean point 0.97 / 0.98 |
| P5 | C3 is HELD | 0.61 | 0.91 | design A L +1.66 / +2.64pp, SE_L about 0.74 / 0.80pp (equal-variance approximation) |
| P6 | T1 does not fire | 0.98 | 0.98 | design A placebo -2.69 / -3.30pp; design B never above 0 in 20 splits |
| P7 | F1 does not fire | 0.99 | 0.99 | Phi(G_DEC / SE_proj) 0.996 / 1.000 |
| P8 | L lies in the range | [+0.71, +2.61]pp | [+1.62, +3.66]pp | design A L, SE_L as P5 |

The targets are in the runner (`PREDICTIONS`, per roster); the confidences are the coder's (from the projected powers).
Selection effect stated: the WORK numbers are from items BBH-WORK and BBH-HIER read; the sealed side is new to all of them.

## Support

(a) Deciding denominators: the 2,304 RESERVED items (24 subtasks; 0.40 of each stratum), in content clusters counted at the
opening; the WORK side's Kish 4.416 (2,662 clusters on 3,457 rows) is the planning transport (the opening prints the
RESERVED Kish). Fit side: the 3,457 WORK items.
(b) DEFF and source: MEASURED on WORK by design B (20 pseudo-splits at the sealed ratio, the registered analysis
unchanged): two-stage DEFF2 of G_DEC 3.02 (R128) / 3.42 (R342), of G_FKI 2.53 / 2.93, of M_FKI 12.8 / 12.2 (M's i.i.d. SE
is small because FREE and DEC agree on most rows). One-stage (design A, conditional) DEFF 1.04-1.14.
(c) n_eff of G_DEC: 2,304 / 3.02 = 763 (R128); 2,304 / 3.42 = 674 (R342) (coder's arithmetic).
(d) SE: PROJECTED from design B, SE_proj = mean SE2 x sqrt(0.6) (both sides of the sealed read are 1 / 0.6 times a
pseudo-split's): G_DEC 1.24 / 1.34pp; G_FKI 1.07 / 1.17pp; G_PLACEBO 1.22 / 1.34pp; M_FKI 0.66 / 0.69pp; L about 0.74 /
0.80pp (Var L = 0.25 x mean(Var G_DEC, Var G_FKI) + 0.5 x Var M: an equal-variance approximation; Cauchy-Schwarz upper
bound 0.86 / 0.93pp). The two-stage SE is CONSERVATIVE here: on WORK the pseudo-splits' points spread 0.42 / 0.48 of the
mean SE2 for G_DEC (overlapping splits, so the true bias is smaller but one-sided; bbh-reserved-prep [P2] post hoc (a)).
(e) MDE80 (2.80 x SE_proj): C1 3.47 / 3.75pp; C2 2.99 / 3.28pp; C3 about 2.08 / 2.23pp (upper 2.42 / 2.61pp).
(f) VERDICT LINE: R128: C1 THIN (the prediction +3.27pp lies 3.27pp from the bar, just below MDE80 3.47pp; power 0.75);
C2 SCOREABLE (3.29pp > 2.99pp; power 0.87); C3 THIN (1.66pp < 2.08pp; power 0.61, lower bound 0.49). R342: C1 SCOREABLE
(5.38 > 3.75; 0.98); C2 SCOREABLE (5.33 > 3.28; 0.995); C3 SCOREABLE (2.64 > 2.23; 0.91; at the upper SE 2.64 > 2.61,
0.81). The ratio S is DESCRIPTIVE-ONLY at both rosters (design B: its percentile interval's lower bound above 0.5 in 0 of
20 pseudo-splits at R128, 8 of 20 at R342); that is why C3 reads L.
(g) STRUCTURAL: C1 / C2 reachable iff the true sealed-side gain is non-zero (the WORK policy is fixed; no cap); C3 reachable
iff G_FREE differs from 0.5 G_DEC; the gains are bounded by ORACLE (+26.2pp on WORK) and the placebo is the floor.

## Falsifier

F1 FIRES iff the point G_DEC <= 0 on the sealed side: then the BBH part of key result 1 is not transported to a second
roster on a sealed side ("BBH carries 0.728" stays a one-roster, 18-model statement; nothing recorded is revised). C2 or C3
FAILED narrows the framing's last clause for BBH at this roster (the declared labels are needed where the labels exist);
each overturns only a wording, never a recorded number.

## Prior results touched (none revised)

V2-DECLARED-CELLS C1 (prog L21927); BBH-WORK (prog L25747-L25758: the split, the census, RESERVED read 0, the roster
128); BBH-HIER (prog L25864-L25871: families recovered by every anchor-free hierarchy); UNION-AF-ROUTE ([SC] cells
+1.52pp, thin); SKILL-BACKOFF (Z_bo on BBH +2.57, z 3.8); CELL-FLIPS (BBH task cells reorder models). Closed lines: none
(no judge, rubric, sub-anchor profile, frontier or GMM LR; key-scored end to end, acc_norm).

## Cost and consequence

Zero LLM calls, 0 cce; the opening is minutes of CPU after `freeze` (the AF tree on WORK, about 330 s). Preconditions
(in order): this registration with the author's O1 / O2 / O3; H1-H3 below; the constants set and `freeze` run and its
sha256 bracketed in; the adversarial reviewer's READY on that commit; the run-operator's `reserved --dry-run` then
`open`. Consequence: key result 1's BBH part becomes a two-roster (18 union models; R) statement on a sealed side, or is
refused for this roster; the framing's last clause gains (or loses) a sealed-side BBH instance.

## Does not show

Anything about judged verdicts, other corpora, other embedders, a content-closed split (H1), a model ranking, V0 / V0m,
cells finer than the subtask; a per-subtask claim (the contributions are concentrated: top-3 share 0.685 / 0.592 on
WORK); "the tree beats k-means" (AF is beside).

## Open items for the registrar (before any registration)

- H1 (data-steward): BBH's split is ND-1-group-disjoint by construction, not CK-CLOSE-checked; whether a CK-CLOSE check
  (text only, both sides) is owed before the opening, and the split word, are the registrar's. Such a check reads the
  RESERVED texts (no response): under O2 (a) that is a read before the opening the registration must admit.
- H2: the WORK plan's deviation (two scripts instead of one, benchzoom `docs/bbh-reserved-prep.md` [P1] (a)) and the C3
  design change from the ratio to L (that plan's [P2] post hoc (b)) were made before any registration; the registrar
  confirms or replaces them.
- H3: the predictions are proposals (the coder's confidences); the registrar fixes them, and the runner's `PREDICTIONS`
  are re-pinned to the registered text before `freeze`.

## Proof that the sealed side is unread (as of a922fe7, 2026-11-06)

- The WORK estimate of record (b4a3057): parquet reads 343 over 342 files, every one filtered on named WORK ids
  (1,185,751 ids requested and returned); RESERVED ids in any filter 0; RESERVED rows returned 0; SplitGuard RESERVED
  responses 0; RESERVED texts and vectors 0 (`work/meta.json` "audit", sha256 71d68f35...).
- The runner: `SealedReader` (the only RESERVED reader) is constructed only in `cmd_open` after `open_refusals`; all
  four constants are PENDING, so `open` refuses at the second condition; no `freeze` file, no `OPENED.json`, no outcome
  exists under `E:/benchzoom_demo/followups/bbh-reserved-confirm`.
- The real dry runs at fa37758 (text option (a); WORK side only; logs `E:/TaxoArena_backup_2026-11-06_bbh-reserved-prep/dry/`):
  R128: parquet reads 129 (128 with the score column) over 129 files, all filtered on WORK ids (445,953 ids); RESERVED ids
  in any filter 0; RESERVED rows returned 0; SplitGuard WORK values 442,496, RESERVED responses 0; "sealed reader
  constructed: 0; RESERVED responses read: 0"; frozen object (in memory, not written) sha256 a6da907dbf509861...
  (a second run: equal, so the opening's byte-identity check is reproducible). R342: parquet reads 343 over 342 files
  (1,185,751 ids); RESERVED 0 / 0; WORK values 1,182,294; reader constructed 0; frozen sha256 5320b3283434ea05... Each
  printed "the opening would read: the RESERVED texts of 2304 ids ... the scores of 2304 RESERVED ids in each of R parts"
  and "REFUSED to open: dry run".
- No `freeze_*.json`, no `OPENED.json` and no outcome exist (`E:/benchzoom_demo/followups/bbh-reserved-confirm` does not
  exist); `tests/test_bbh_reserved_confirm.py` asserts the four constants PENDING and that `open` and the CLI refuse
  without the flag and with PENDING constants, constructing no reader.
