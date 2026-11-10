# DRAFT v2 registration: BBH-RESERVED-CONFIRM (lead #4), the one-time read of BBH's sealed RESERVED side

STATUS: DRAFT v2 for the registrar: the registration text to register. NOT REGISTERED; nothing sealed has been opened;
zero LLM calls. Written by the engine coder under D-2026-11-07-1 (`docs/agents/author_decisions/2026-11-07.md`, a9bb09d3)
on top of D-2026-11-06-3 (b42c3300). It replaces, for registration, the options draft
`docs/agents/plans/2026-11-06_bbh-reserved-confirm_registration_draft.md` (b1baa4cb; that file stays the record of the
options as they were put to the author). It applies READY_bbh-reserved-confirm (`docs/reviews/READY_bbh-reserved-confirm.md`,
814bafa6) C1-C6, L1, L2 and the registrar's rulings (i)-(iv) of `## Registrar's record 2026-11-07 ...` (prog L25891,
_as_of 79ef14a7). Every number is copied from a file of record named beside it ("prog" = `docs/judge_v2_program.md`);
arithmetic of my own is marked "(coder's arithmetic)". The four registration constants of the runner (REG_COMMIT,
REG_ROSTER, REG_TEXT, FREEZE_SHA) stay PENDING (brief of D-2026-11-07-1: "Do NOT set the four registration constants
yet").

Proposed heading (the sealed runner's registration check (READY C3) requires, at REG_COMMIT, exactly ONE line of
`docs/judge_v2_program.md` matching `^## Registered \d{4}-\d{2}-\d{2} .*— BBH-RESERVED-CONFIRM:`; the em dash and the
colon are part of the pattern):

`## Registered <YYYY-MM-DD> (before any call; the sealed runner is pre-registration code, ruling (ii)) — BBH-RESERVED-CONFIRM: on BBH's sealed RESERVED side, with all 342 KEPT models, does a per-subtask policy fitted on WORK beat the best single model, and do the anchor-free tree's cells, built from the WORK texts only, recover at least half of that gain? (zero-call; one-time sealed read)`

## The author's choices (decided; D-2026-11-07-1, verbatim)

- O1 roster: "All 342 models (Recommended)": the sealed read uses all 342 KEPT models (ids sha256 71c12468cd49b0dca1004233ea0ee7fae393eb06039b7114d1af37e0ba192b9c, the
  tree-arm WORK run's gate, = BBH-WORK's printed prefix 71c12468cd49b0dc); nothing sealed stays for later.
- O2 texts: "Training side only (Recommended)": every cell is built from the 3,457 WORK texts; no RESERVED text shapes a
  cell. The RESERVED texts and vectors are read at the opening only, to file each RESERVED row into the frozen cells
  (nearest unit centroid; nearest-child descent of the tree). The runner has no transductive path any more (FK-T, AF-T,
  the text audit removed; `--text all` refuses). The claim may say "a TRAIN-only embedding taxonomy" (the framing's
  clause) under the split word below.
- C4 the label-free criteria: "Anchor-free tree (Recommended)": C2 / C3 read AF-I, the anchor-free tree (the axis_v1
  recipe without groups, BBH-HIER's AF) fitted on the 3,457 WORK texts; its leaf count is chosen by the recipe (22 on all
  WORK rows), not taken from the labels. k-means at k = 24 prints beside, labelled "k set to the declared count" (one
  integer of label information; READY C4). "Its training-side share is computed first and the predictions are redone":
  done by BBH-RESERVED-TREE (benchzoom plan [P3] 01d9c79, run [P4] below) before this draft.
- OPEN, the author's (O3; nothing decided here): whether and when to open (the side is a one-shot resource), and which
  words of the record may cite the outcome (C1 for key result 1's BBH part as a second roster on a sealed side; C2 / C3
  for the framing's last clause). D-2026-11-07-1 (5): it comes back to the author after the fixes, this registration and
  a delta READY.

## Question

README key result 1 rests on V2-DECLARED-CELLS (union EVAL, 18 models, content-closed v2 split): "G +2.67pp [+1.46,
+3.89], n 5,907 [BBH carries 0.728 of G; leave-BBH-out and MMLU-Pro intervals contain 0, DESCRIPTIVE]" (prog L21927). BBH
has a second, never-read response side: the 2,304 RESERVED items of SPLIT-1 (benchzoom `docs/bbh_census.md` [C-4];
RESERVED responses read 0 by BBH-WORK, prog L25747-L25758, by BBH-HIER, prog L25864-L25871, by BBH-RESERVED-PREP and by
BBH-RESERVED-TREE). On it, with all 342 KEPT models of the Open LLM Leaderboard, (C1) does the per-subtask policy fitted
on the 3,457 WORK items beat the best single model fitted there, (C2) do the anchor-free tree's cells (built from the
WORK texts only) beat it, and (C3) do they recover at least half of the declared gain? C1 makes key result 1's BBH part a
second-roster, sealed-side statement (SQ5) or refuses it; C2 / C3 test the framing's last clause ("Cells are declared
labels for the arena, and are read by a TRAIN-only embedding taxonomy where labels are missing", framing of record L20) on
the corpus where routing pays, with a taxonomy whose cell count no label set.

## Hygiene

- Split word (ruling (iii)): "the sealed RESERVED side of BBH SPLIT-1 (seed 20261027; ND-1 groups kept to one side;
  stratified by subtask; pins sha256-lf16:3d4d644a7ac34d22 / sha256-lf16:9ef05cc2cfe34c91)", "sealed" =
  ND-1-group-disjoint by construction; NOT "content-closed" (no CK-CLOSE check exists for BBH; H1 below). The opening
  prints, beside, the RESERVED rows with a WORK cosine twin (>= 0.98, text only) and G_DEC without them.
- Read once, at the opening, and nothing else: the 2,304 RESERVED items' text (item columns of one part; census sha
  checked) and vectors (the pinned BBH npz, sha256 0e9ef33a...), only to file the rows into the frozen cells; the acc_norm
  of the 2,304 RESERVED items for the 342 models (787,968 values; coder's arithmetic 2,304 x 342).
- Before the opening, the WORK side only, through the WORK estimate's loaders and its access audit (every parquet read
  filtered on WORK ids; a RESERVED id in a filter refuses). The frozen WORK-side object (models, best single, DEC / FAM /
  PLACEBO policies, the FK centroids, the anchor-free tree's descent table, all policies) is written write-once by
  `freeze`; its sha256 is pinned in the runner (`FREEZE_SHA`) and bracketed into this registration BEFORE the opening;
  `open` recomputes it from WORK and refuses on any byte difference.
- The opening ledger `OPENED.json` is written (mode x, carrying the registration and the code manifest) before the first
  RESERVED byte; a second opening refuses; any failure after the ledger (G4, an incomplete matrix) is recorded as
  `outcome_REFUSED_<UTC>.txt` and never retried.
- Zero LLM calls; CPU, one process; no TaxoArena pool or DB is read (BBH is benchzoom's corpus; rule 7 is not engaged);
  outputs never committed (`E:/benchzoom_demo/followups/bbh-reserved-confirm`, backup
  `E:/TaxoArena_backup_<date>_bbh-reserved-confirm` with SHA256SUMS).
- L2 (READY): the sealed read's placebo permutes the 24 subtask labels over all 5,761 items (`default_rng([20261106,
  8])`; metadata, no text), the WORK estimate's within WORK (stream 3): P6's basis is the analogue design.

## Instrument (pre-registration code; ruling (ii))

benchzoom branch `bbh-reserved-prep` (local; not merged), tip 727cc67 (blobs LF, `git hash-object`): the sealed runner
`examples/bbh-reserved-confirm.py` blob:5acb0671; the shared code check and AF pool `examples/bbh_reserved_common.py`
blob:fe5530b0; the WORK estimate's core `examples/bbh-reserved-prep.py` blob:dafd9eda (unchanged since its run of
record b4a3057); the tree-arm WORK runner `examples/bbh-reserved-tree.py` blob:cc955d59 (its run of record ran at
f87461a with that blob); the tests `tests/test_bbh_reserved_confirm.py` blob:877e9cc7; the plan
`docs/bbh-reserved-prep.md` blob:bc6fb750. The runner was built before any registration, as D-2026-11-06-3 (3) asked
(ruling (ii)); H2's two deviations stand as stated there and are confirmed or replaced by the registrar: (a) two scripts
instead of one (benchzoom plan [P1] (a)); (b) C3 read on the linear contrast L instead of the ratio (plan [P2] post hoc
(b)). This registration precedes the commit that sets the four constants; a delta READY follows that commit and
includes a real `reserved --dry-run --roster 342 --text work` (READY 814bafa6 verdict).

Modes: `reserved --dry-run --roster 342 --text work` (WORK side only; prints the code state, the registration check,
what the opening would read and the Support lines below with their words; constructs no sealed reader; refuses to open);
`freeze --roster 342 --text work` (refused unless the constants are set and equal to the CLI, the registration check
and the code check pass); `open --roster 342 --text work --registration <sha> --open-sealed-reserved`, refused unless,
in this order: the flag; REG_COMMIT / REG_ROSTER / REG_TEXT set and equal to the CLI; `--registration` = REG_COMMIT;
the registration check (READY C3: REG_COMMIT exists in TaxoArena, lies on `main`, and `docs/judge_v2_program.md` AT that
commit carries exactly one heading matching the pattern above); the code check (READY C1: `git status --porcelain
--untracked-files=all` over `examples`, `src`, the test file and the plan clean, and every repository module the process
executes, lazily imported ones preloaded, tracked with its working LF blob equal to HEAD's; a `benchzoom` module loaded
from outside the checkout is dirty); no outcome and no ledger; FREEZE_SHA set and equal to the frozen file's sha256;
every prediction target set; the frozen object recomputed from WORK byte-identical. Policies: per cell the roster model
with the largest summed WORK correctness (ties: first name in sorted order; an empty cell gets the best single), as
ROUTER-CLEAN-POLICY / V2-DECLARED-CELLS. Two-stage bootstrap B = 2,000 (`default_rng([20261106, 7])`): WORK content
clusters resampled within subtask with every policy refitted (cells fixed), then RESERVED content clusters within
subtask; content clusters = BBH-WORK's union (cos >= 0.98 on the 4,096-d rows UNION the census ND-1 group). Deciding
interval = point +- 1.96 x SE2; the percentile interval, the one-stage (`default_rng([20261106, 9])`) SE, the i.i.d.
SE, DEFF, n_eff and MDE80 = 2.80 x SE2 printed beside every statistic. Selftest S1-S14 on synthetic fixtures and
sandbox git repositories (156 checks); mutants 97 of 98 (Z7 the one survivor, equivalent) killed (table in the runner's
docstring).

## Readouts and criteria (disjoint; the INTERVAL decides each; the point decides only F1)

- G4 REFUSAL (evaluated FIRST; READY C6): a two-stage SE of 0 (or not finite) for G_DEC, G_AFI, G_PLACEBO or L refuses
  (a degenerate interval; never a verdict). It precedes T1 because T1 reads an interval.
- T1 VALIDITY TRIGGER (evaluated second, before any criterion): the placebo (the 24 subtask labels permuted over all
  5,761 items, sizes kept, `default_rng([20261106, 8])`; policy fitted on WORK) gain G_PLACEBO = acc_R(PLACEBO) -
  acc_R(BS): if its interval lies wholly above 0, C1-C3 read "UNDETERMINED (BY TRIGGER: T1 the placebo manufactures
  gain)", F1 is NOT EVALUATED, every prediction is UNDETERMINED (BY TRIGGER).
- C1 DECLARED GAIN: G_DEC = acc_R(DEC) - acc_R(BS), both fitted on all WORK rows: HELD iff wholly above 0; FAILED iff
  wholly below 0; UNDETERMINED otherwise.
- C2 LABEL-FREE GAIN (the anchor-free tree): G_AFI = acc_R(AFI) - acc_R(BS), AFI = the anchor-free tree fitted on the
  3,457 WORK texts (the leaves of the tree of all WORK rows; RESERVED rows filed by nearest-child descent): the same
  three words.
- C3 AT LEAST HALF RECOVERED: L = G_AFI - 0.5 x G_DEC = acc_R(AFI) - 0.5 acc_R(DEC) - 0.5 acc_R(BS) (the share
  S = G_AFI / G_DEC exceeds 0.5 iff L > 0 when G_DEC > 0): NOT EVALUATED unless C1 is HELD; then HELD iff L's interval
  lies wholly above 0, FAILED iff wholly below 0, UNDETERMINED otherwise.
- Exclusivity: each criterion's three words are disjoint inequalities on one interval; C3 is gated on C1's HELD; G4 and
  T1 pre-empt all; no two criteria share a deciding statistic.
- PRINTED BESIDE (deciding nothing): S with its two-stage percentile interval; L's SE by the identity beside the
  replicates' SE2; k-means FK-I ("k set to the declared count", 24; one integer of label information) with G_FKI, L_FKI
  and S_FKI; FAM (the 20 families); ORACLE; M = acc_R(AFI) - acc_R(DEC); per-subtask contributions; the
  leave-one-subtask-out range; the RESERVED rows with a WORK cosine twin and G_DEC without them; the one-stage interval of
  every statistic; the modules executed after the code check (0 expected).

## Predictions (R342; from the WORK estimates; no RESERVED value seen; 80 % ranges = design-A point +- 1.2816 x SE)

| id | prediction | confidence | basis (BBH-RESERVED-TREE, `tree/summary.txt` sha256 87e4ca96fe97cd07...) |
|---|---|---|---|
| P1 | C1 is HELD | 0.98 | power at the design-A G_DEC +5.38pp with SE_proj 1.34pp: Phi(5.38 / 1.339 - 1.96) |
| P2 | G_DEC lies in [+3.66, +7.10]pp | 0.80 | design-A G_DEC +5.38pp +- 1.2816 x SE_proj 1.339pp (the 2026-11-06 draft's [+3.67, +7.10] rounded the SE to 1.34) |
| P3 | C2 (G_AFI) is HELD | 0.98 | power at the design-A G_AFI +4.91pp with design B's SE_proj 1.23pp |
| P4 | S = G_AFI / G_DEC lies in [0.70, 1.30] | 0.86 | delta method on the projected variances (SE_S 0.183); design B' points in the range in 17 of 20 splits (0.85); design A S_AFI 0.913 [0.833, 1.003] |
| P5 | C3 (L_AFI) is HELD | 0.68 | power at the design-A L_AFI +2.22pp with SE_L(identity) 0.917pp |
| P6 | T1 does not fire | 0.98 | design A G_PLACEBO -3.30pp, design B never above 0 in 20 splits (1 - power 0.999995), capped at 0.98: the sealed placebo permutes over all 5,761 items, the WORK one within WORK (L2: the analogue design) |
| P7 | F1 does not fire | 1.00 | Phi(G_DEC / SE_proj) = Phi(5.38 / 1.339) |
| P8 | L_AFI lies in [+1.05, +3.40]pp | 0.80 | design-A L_AFI +2.22pp +- 1.2816 x SE_L(identity) 0.917pp |

The targets are in the runner (`PREDICTIONS[342]`); the confidences are the coder's (H3: the registrar fixes them, and
the runner's PREDICTIONS are re-pinned to the registered text before `freeze`). Selection effect stated: the WORK numbers
are from items BBH-WORK, BBH-HIER, BBH-RESERVED-PREP and BBH-RESERVED-TREE read; the sealed side is new to all of them.

## Support (R342)

(a) Deciding denominators: the 2,304 RESERVED items (24 subtasks; 0.40 of each stratum), in content clusters counted at
the opening; the WORK side's Kish 4.416 (2,662 clusters on 3,457 rows) is the planning transport (the opening prints the
RESERVED Kish). Fit side: the 3,457 WORK items.
(b) DEFF and source: MEASURED on WORK by design B / B' (20 pseudo-splits at the sealed ratio, the registered analysis
unchanged; B' adds AF-I fitted on each pseudo-WORK side; B's rows reproduced to 1e-12 by B'): two-stage DEFF2 of G_DEC
3.42 (bbh-reserved-prep [P2]), of G_AFI 3.39, of L_AFI 4.14, of M_AFI 4.99. One-stage (design A,
conditional) DEFF G_DEC 1.11, G_AFI 1.06, L_AFI 1.05.
(c) n_eff = 2,304 / DEFF2 (coder's arithmetic): G_DEC 674; G_AFI 680; L_AFI 557.
(d) SE: PROJECTED from design B / B', SE_proj = mean SE2 x sqrt(0.6): G_DEC 1.34pp; G_AFI 1.23pp; M_AFI
1.04pp; G_PLACEBO 1.34pp. C3's SE from the exact identity (READY C2) Var L = 0.5 Var G_AFI - 0.25 Var G_DEC +
0.5 Var M_AFI on those projected SEs: SE_L 0.917pp (the identity holds per split on the replicate variances to
6.3e-16 relative; the direct projected SE of L 0.922pp and sqrt(mean Var L) x sqrt(0.6) 0.936pp beside; no
approximation and no bound is used). The two-stage SE is CONSERVATIVE here (bbh-reserved-prep [P2] post hoc (a):
calibration SD(points) / mean SE2 of G_DEC 0.48 at R342; design B' for G_AFI 0.58).
(e) MDE80 = 2.80 x SE: C1 3.75pp; C2 3.43pp; C3 2.57pp (the runner's SUPPORT_PLAN rounds each number to 0.01pp, so
its dry run prints C2 3.44pp and C3 2.58pp; the words are the same).
(f) VERDICT LINE (ruling (i): SCOREABLE iff the prediction's distance from the bar exceeds its MDE80, else
DESCRIPTIVE-ONLY; power prints beside and decides no word):
C1 SCOREABLE (the prediction +5.38pp lies 5.38pp from the bar 0, above MDE80 3.75pp; power 0.98 beside); C2 SCOREABLE
(+4.91pp > 3.43pp; power 0.98); C3 DESCRIPTIVE-ONLY (L_AFI +2.22pp < MDE80 2.57pp by the identity SE 0.92pp; power 0.68;
with the direct SE 0.92pp the same word). C3 stays a registered criterion with its three words (a HELD would still be
read on its interval), but its Support reads DESCRIPTIVE-ONLY at R342: a FAILED or UNDETERMINED C3 is weak evidence.
Beside, deciding nothing: the k-means arm's L_FKI +2.64pp > MDE80 1.94pp would read SCOREABLE; the author's C4 choice
puts the deciding C3 on the tree arm (coder's reading; the registrar words the consequence). The ratio S is
DESCRIPTIVE-ONLY (design B: its percentile interval's lower bound above 0.5 in 8 of 20 pseudo-splits at R342,
bbh-reserved-prep [P2]); that is why C3 reads L.
(g) STRUCTURAL: C1 / C2 reachable iff the true sealed-side gain is non-zero (the WORK policy is fixed; no cap); C3
reachable iff G_AFI differs from 0.5 G_DEC; the gains are bounded by ORACLE (+26.2pp on WORK, R342) and the placebo is
the floor. The tree arm's design B' fits on about 2,040 rows (leaves 15-19), the sealed read's on 3,457 (22
leaves): design B' is a rougher analogue for AF-I than for DEC; design A' (fold trees on about 2,766 rows, 19-24
leaves) gives the points.
Beside (deciding nothing): k-means FK-I ("k set to the declared count") G_FKI +5.33pp (SE_proj 1.17pp), L_FKI
+2.64pp (SE_L by the identity 0.69pp).

## Falsifier

F1 FIRES iff the point G_DEC <= 0 on the sealed side: then the BBH part of key result 1 is not transported to a second
roster on a sealed side ("BBH carries 0.728" stays a one-roster, 18-model statement; nothing recorded is revised). C2 or
C3 FAILED narrows the framing's last clause for BBH at this roster (a taxonomy built without the labels does not recover
the declared gain there); each overturns only a wording, never a recorded number.

## Prior results touched (none revised)

V2-DECLARED-CELLS C1 (prog L21927); BBH-WORK (prog L25747-L25758: the split, the census, RESERVED read 0); BBH-HIER (prog
L25864-L25871: families recovered by every anchor-free hierarchy; the AF tree 43 / 22 / 7); BBH-RESERVED-PREP (benchzoom
plan [P2]; prog L25891); UNION-AF-ROUTE ([SC] cells +1.52pp); SKILL-BACKOFF (Z_bo on BBH +2.57, z 3.8); CELL-FLIPS
(BBH task cells reorder models). Closed lines: none (no judge, rubric, sub-anchor profile, frontier or GMM LR;
key-scored end to end, acc_norm).

## Cost and consequence

Zero LLM calls, 0 cce; the opening is minutes of CPU after `freeze` (the AF tree on WORK, about 330 s). Preconditions
(in order): this registration (with O3 the author's); H1 decided; the constants commit (REG_COMMIT, REG_ROSTER 342,
REG_TEXT "work") with `freeze` run and its sha256 bracketed in and pinned as FREEZE_SHA; the adversarial reviewer's delta
READY on that commit, with a real `reserved --dry-run --roster 342 --text work`; the author's go (O3); the
run-operator's `open`. Consequence: key result 1's BBH part becomes a two-roster (18 union models; 342 OLL models)
statement on a sealed side, or is refused for this roster; the framing's last clause gains (or loses) a sealed-side BBH
instance read by a taxonomy whose cell count no label set.

## Does not show

Anything about judged verdicts, other corpora, other embedders, a content-closed split (H1), a model ranking, V0 / V0m,
cells finer than the subtask; a per-subtask claim (the contributions are concentrated: top-3 share 0.592 at R342 on
WORK); "the tree beats k-means" or the reverse (FK-I is beside, k set from the labels); the share S as a decision (its
interval is DESCRIPTIVE-ONLY: design B's lower bound above 0.5 in 8 of 20 pseudo-splits at R342, bbh-reserved-prep
[P2]).

## Open items

- O3 (the author's): whether and when to open; which words may cite the outcome.
- H1 (the registrar's, with the data-steward): BBH's split is ND-1-group-disjoint by construction, not CK-CLOSE-checked;
  whether a CK-CLOSE check (text only, both sides) is owed before the opening, decided at the registration (ruling
  (iii)). Under O2 such a check reads the RESERVED texts before the opening (no response); the registration must admit
  that read if it orders it. The runner prints the cross-side cosine twins at the opening in any case.
- H2 (the registrar's): confirm or replace the two pre-registration deviations (Instrument).
- H3 (the registrar's): fix the predictions; the runner's PREDICTIONS are re-pinned to the registered text before
  `freeze`.

## READY 814bafa6 conditions: where each is met

| id | condition | where | mutant (killed) |
|---|---|---|---|
| C1 HIGH | the clean-tree check of open / freeze covers the opening script and every executed module | `code_check` / `bbh_reserved_common.code_state`; selftest S12 (a sandbox repository: the confirm script, tau-grid, a src module, the test file, the plan edited; an untracked file; an --assume-unchanged edit; a module outside the covered paths; a benchzoom module loaded from outside the checkout; a module loaded after the check printed) and S14 (lazy modules in a fresh process) | the reviewer's OM6 refuses now (S12 "the confirm script modified and uncommitted"); Y6, Y50, Z2-Z6, Z8, Z9, Z11, Z40, Z42 (Z7 equivalent: the HEAD-blob lookup refuses the same files) |
| C2 MEDIUM | C3's SE from the exact identity; P5, P8 re-derived; no "upper bound" | BBH-RESERVED-TREE (design B' identity per split; SE_L(identity)); Support (d); P5, P8 above; the outcome prints the identity beside L | tree X13-X16, X19; confirm Z27, Z37 |
| C3 MEDIUM | open verifies REG_COMMIT exists and carries the heading (count 1) | `registration_check` (exists, on main, the programme AT the commit, exactly one heading); freeze and open; S13 | Z12-Z19 |
| C4 MEDIUM | the label-free arm carries "k set to the declared count", or the anchor-free tree decides | decided by the author: AF-I decides C2 / C3 (C4 above); FK-I beside with that label | Z20-Z23, Z39 |
| C5 LOW | no "THIN" Support word | `support_word` (SCOREABLE / DESCRIPTIVE-ONLY only); Support (f) | Z25, Z26, Z28; tree X17, X36 |
| C6 LOW | the order of T1 / G4 matches the draft | G4 first, then T1, in the code and in this text; S10 (a degenerate placebo SE with a firing point refuses; a degenerate DEC SE with a firing placebo refuses) | Z29 |
| L1 LOW | the refusal test passes fixture or tripwire paths | `Tripwire` in the pytest wrapper and S11 | - |
| L2 LOW | P6's basis is the analogue design | Hygiene (last item); P6's basis | - |

## Proof that the sealed side is unread (as of 727cc67)

- BBH-RESERVED-TREE's run of record (f87461a): parquet reads 343 over 342 files, every one filtered
  on named WORK ids (1185751 ids requested and returned); RESERVED ids in any filter 0; RESERVED rows returned 0;
  SplitGuard RESERVED responses 0; RESERVED texts and vectors 0 (`tree/meta.json` "audit", sha256 893f3b2393b2a616...).
- The runner: `SealedReader` (the only RESERVED reader) is constructed only in `cmd_open` after `open_refusals`; the
  four constants are PENDING, so `open` refuses at the second condition; no `freeze` file, no `OPENED.json`, no outcome
  exists under `E:/benchzoom_demo/followups/bbh-reserved-confirm` (the directory does not exist).
- The real dry run at 727cc67 (`reserved --dry-run --roster 342 --text work`; WORK side only; log `E:/TaxoArena_backup_2026-11-07_bbh-reserved-tree-logs/dry_342.log`), its lines verbatim:
  `registration constants: REG_COMMIT PENDING; REG_ROSTER PENDING; REG_TEXT PENDING; FREEZE_SHA PENDING`
  `registration check (C3): not run (REG_COMMIT PENDING)`
  `code state (C1; freeze and open refuse unless clean): head 727cc6764375f818d7fe0de0bfd5ca231b891693; manifest 31 files, sha256 36543d3de42936b1111c7d39278e618cac8a8522f8bd200ddfdf54b2e0bd2b65; findings 0`
  `roster R342: 342 models (ids sha256 71c12468cd49b0dc), 1182294 WORK values, no NaN, binary`
  `access audit (work): parquet reads 343 (342 with the score column, 1 item columns only) over 342 files, every one filtered on named ids (1185751 ids requested, 1185751 rows returned); RESERVED ids in any filter 0; RESERVED rows returned 0 (with a score 0)`
  `SplitGuard: WORK values read 1182294; RESERVED responses read 0; RESERVED texts read 0; RESERVED vectors read 0`
  `frozen WORK-side object (roster R342, text option 'work') in memory: sha256 5320b3283434ea0511a4df0bd8fb1fac9b574a0c61257debed15692b13b21b82; best single internlm/internlm2_5-20b-chat; DEC picks 10 distinct models over 24 subtasks; AF tree [43, 22, 7] (its 22 leaves are C2 / C3's cells)`
  `the opening would read: the RESERVED texts of 2304 ids (item columns, one part) and their vectors; the scores of 2304 RESERVED ids in each of 342 parts (787968 values); nothing else`
  `Support C1 (G_DEC): prediction +5.38pp from the bar 0; SE 1.34pp; MDE80 3.75pp; power 0.980 (beside) -> SCOREABLE`
  `Support C2 (G_AFI): prediction +4.91pp from the bar 0; SE 1.23pp; MDE80 3.44pp; power 0.979 (beside) -> SCOREABLE`
  `Support C3 (L_AFI): prediction +2.22pp from the bar 0; SE 0.92pp; the direct projected SE 0.92pp beside; MDE80 2.58pp; power 0.675 (beside) -> DESCRIPTIVE-ONLY`
  `sealed reader constructed: 0; RESERVED responses read: 0`
  `REFUSED to open: dry run (the opening needs --open-sealed-reserved, --registration and the registration constants)`
  The run exited 0. Its in-memory frozen object (sha256 5320b3283434ea05...) is byte-identical to the 2026-11-06 R342
  dry run's (prep READY row 2): the frozen WORK side did not move with the code changes. Before and after it, no
  `OPENED.json` and no `freeze_R*.json` exist under `E:/benchzoom_demo` (find: 0) and
  `E:/benchzoom_demo/followups/bbh-reserved-confirm` does not exist. Nothing else of the sealed side was read by
  this work: the selftests and mutants read synthetic fixtures in sandboxes only.
