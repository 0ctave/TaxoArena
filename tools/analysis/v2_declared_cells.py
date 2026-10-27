"""V2-DECLARED-CELLS (RP03) -- the zero-call v2 key reader, legs U and M (ZERO judge calls, zero construction, no embedder).

REGISTRATION OF RECORD: docs/judge_v2_program.md, section "## Registered 2026-09-27 (before any code or call) —
V2-DECLARED-CELLS: on the content-closed v2 split, does a per-cell policy fitted on TRAIN beat the best single model on the
union EVAL at DECLARED (source, domain) cells (leg U: a sensitivity and wording conversion, NOT a replication), and is the
MMLU-Pro key profile's interaction-only reliability above its null on the 13 declared categories with no tree and no
embedder (leg M; K12 and K37)? (zero-call; plan R-B, formerly REG-1)" (L21582-L21614 as of a357ef0; resolve by the
heading, the last bracket wins). BINDING RULING: docs/reviews/RULING_w0_seal_k46_reuse.md (c5a8cb6), sections 2-4 (B1-B4,
W1-W12). This script is BUILT TO that text; its readings are listed under READINGS and are for the READY to confirm.

  python tools/analysis/v2_declared_cells.py --selftest            # synthetic sealed fixtures under tempfile; opens NO DB of record
  python tools/analysis/v2_declared_cells.py --dry-run [--leg U|M] # 0 calls, WRITES NOTHING, prints NO statistic: pins, shas,
                                                                   #   pools, rosters, counts, coverage, floors, preconditions
  python tools/analysis/v2_declared_cells.py --c0 --leg U|M        # the C0 reproduction gate ONLY (paeec / p2dca); no v2 EVAL read
  python tools/analysis/v2_declared_cells.py --run --leg U|M       # ONE read of the EVAL key per leg (B1); write-once outcome

LAUNCH SEQUENCE (registration FLOW): registration a357ef0 -> this script (engine-coder) -> the data-steward's half bracketed in
(key join, multi-response variant rule, per-item coverage, the 422-in-pv2_41dbd count; W0 RP02) -> the registrar's parameters
below set by a delta of this script -> adversarial-reviewer READY (code-only) -> run-operator --dry-run -> --run --leg U and
--run --leg M in ONE W1 rule-7 window (W12: the W1-W5 probe shows every pool DB FREE, >= 12 GB RAM free, single-threaded,
one process, no JVM, never beside a construction) -> adversarial-reviewer on the numbers -> registrar. Run from the MAIN
checkout (the v2 views and the C0 inputs are untracked there); TAXOARENA_DATA_ROOT may point the v2 inputs elsewhere.

PRECONDITIONS THAT REFUSE --run WHILE UNSET (PRECONDITIONS below; each is owed by a named party, none is chosen here):
  variant_rule      the data-steward's multi-response variant rule (registration HYGIENE leg U: "owed; a failed precondition
                    until bracketed in"); implemented options: UNUSABLE_CELL, AGREE_OR_UNUSABLE, REFUSE (VARIANT_RULES).
  steward_bracket   the programme line / commit of the steward's half (coverage, variant rule, the 422 count).
  residual_file     (path, sha256-bytes) of the steward's list of the 422 residual EVAL items ("G without the 422 residual
                    items" and leg M's "number of the 422 residual items inside pv2_41dbd" are declared PRINTED BESIDE; B2
                    requires them at the read, and no committed list exists).
  train_unit        leg U's TRAIN-stage resampling unit ("component" or "item"): the registration says "clusters = CK-CLOSE
                    components" and ROUTER-CLEAN-POLICY resampled TRAIN QUESTIONS within stratum; whether the TRAIN stage is
                    component-clustered is not stated (the EVAL stage is: components within stratum). AMBIGUITY A1.
  p2_measure        how "BBH carries >= 50% of G" (P2) is measured: "contribution" = (n_BBH / N) x G_BBH / G, or
                    "leave_out" = 1 - G_nonBBH / G. AMBIGUITY A2.

GUARDS, executed and printed in every real mode:
  (1) the first printed line is the pool id of the leg (pv2_1575de61bb20e977 for U, pv2_41dbd3dbcd399df0 for M); the pool row
      is read from the view and its component / item counts are asserted (5,642 / 6,153; 3,400 / 3,492).
  (2) every view is opened ONLY through data_v2.views (open_generation("policy_fit") for leg U's fit; open_eval("route") for
      leg U's score; open_eval("arena") for leg M), pinned by sha256-bytes (gen c2930c60..., eval e35b7518...), mode=ro&
      immutable=1 after the -wal / -journal refusal (data_v2.ro.open_ro); the sha is printed BEFORE and AFTER the read.
  (3) KEY TRIPWIRE (v2_reader_guards.KeyTripwire): every statement is checked; output_zlib, gt_raw, answer_text, pred and
      the reference table are NEVER admitted (ruling section 2 "never" column); is_correct / is_correct_mathfix are SEALED
      in --dry-run and until (U) the B3 policy file exists / (M) the preconditions pass.
  (4) B3 ORDER: leg U writes its frozen TRAIN policy write-once and prints its sha256 BEFORE open_eval("route") is called;
      the opener refuses while the policy file is absent.
  (5) B1: a write-once one-read marker per leg is written BEFORE the EVAL key is read; an existing marker REFUSES the run.
  (6) G3: every policy fit asserts that the items carrying weight are TRAIN items (SystemExit, python -O safe); --run
      refuses unless the executed count equals B + 1 (1 point fit + B two-stage fits; the C0 fit is counted separately).
  (7) Meta-Llama-3-70B-Instruct asserted absent from every roster; |roster U| == 18; K37's sha256-text == 3a3204cc...6f91
      (the stage-1 roster); K12 = rubric_p8.ARENA12 inside K37.
  (8) G4: a zero two-stage variance of G (C1) or of the placebo contrast refuses (every interval degenerate = a defect).
  (9) C0 (validity, evaluated FIRST, before any v2 read): leg U reproduces ROUTER-CLEAN-POLICY's C0 on paeec (best single
      Qwen2.5-72B-Instruct 0.5912, TRUE (source, domain) 0.6220) through THIS script's fit; leg M reproduces PROFILE-
      RELIABILITY-INTERACTION's K12 0.8665 on p2dca through THIS script's key builder and profile wrapper; to 4 dp. A miss
      VOIDs the leg: SystemExit, nothing written, no v2 file opened (a READY defect, not an outcome).

INSTRUMENT.
  Leg U (ROUTER-CLEAN-POLICY's fit and two-stage bootstrap, router_clean_policy.py blob:2a726529 the base): arms best single
  (argmax TRAIN accuracy; tie-break = the first model in sorted-name order) | TRUE source | TRUE (source, domain) | oracle |
  PLACEBO (the item-level (source, domain) labels of every scored item, sorted by item_id, shuffled by random.Random(42);
  per-pseudo-stratum argmax on TRAIN). Absent group -> best single (MC-E2E pick()). Key = is_correct with the MATH-FIX
  overlay (is_correct_mathfix where non-null; W7), the overlaid cells counted per side. Scored set: items whose 18 cells are
  all usable under the variant rule. B = 2,000, numpy default_rng(42), per replicate: TRAIN resampled within stratum by the
  train_unit (component stratum = the split's component table), EVERY policy re-fitted, then EVAL components resampled
  within stratum and scored. DECIDING interval = point +- 1.96 x SE_2stage (ROUTER-CLEAN-POLICY's form, carried); the
  percentile interval and the i.i.d. SE (EVAL items i.i.d., policy fixed) beside; measured DEFF = var_2stage / var_iid,
  n_eff = N / DEFF, MDE80 = 2.80 x SE_2stage.
  Leg U C2 and leg M C3 (PROFILE-RELIABILITY-INTERACTION's estimator, imported and unchanged: pri.leg, pri.intervals,
  pri.null_tables; 40 halvings random.Random(7); per-half key accuracy; model- AND cell-demeaned; Spearman-Brown; the
  leave-one-cell-out jackknife RE-HALVED (the primary of record: 0.8665 [0.8000, 0.9330] is the re-halved interval) decides,
  FIXED beside; the logit-additive no-interaction null, 20 tables, RandomState seeds 1..20; p95 = the 19th of the 20
  interaction-only null reads). Cells: sorted declared keys; a cell is admitted iff its key-complete item count (from cell
  existence, BEFORE the key is read) is >= 120; the admitted list is printed before any R; history is excluded BY NAME in
  leg M.

CRITERIA (registered; ONE deciding statistic each; the INTERVAL decides, the point decides nothing):
  C1 (U) G = acc_EVAL(TRUE (source, domain)) - acc_EVAL(best single): HELD iff the two-stage interval lies wholly above 0;
     FAILED iff wholly below; UNDETERMINED otherwise. VALIDITY TRIGGER T1 (registered, PRINTED BESIDE): the placebo's
     two-stage interval wholly above 0 VOIDS C1.
  C2 (U) interaction-only R of the union key profile at the pv2_1575 EVAL strata with >= 120 items: HELD iff the jackknife
     95% lower bound EXCEEDS the null p95; FAILED iff the upper bound is AT OR BELOW it; UNDETERMINED otherwise.
  C3 (M) per roster (K12, K37 separately), the C2 rule over the scored declared categories against that roster's null.
PRINTED BESIDE (declared; decide nothing): G without the 422 residual items; leave-BBH-out G; per-source G; the placebo;
the two name-matched models of the stage-1 37 (disclosure); leg M's recorded K12 0.8665 / K46 0.8118 on p2dca as
DESCRIPTIVE comparators (roster, split, filing and question set all differ). Words (W1-W3) are printed in every outcome.
PREDICTIONS P1-P7 and FALSIFIERS F1-F3 as registered (verdict_lines_u / verdict_lines_m); every print branch is executed
by --selftest (Branches registry; TOPIC-PARTITION D1 / D7).

READINGS (stated, not silent; each is for the READY to confirm or refuse):
  (a) T1 pre-empts C1 and every C1-derived prediction (P1, P2, P3, P7 read UNDETERMINED (BY TRIGGER)), and F1 is NOT
      EVALUATED under T1 (ROUTER-CLEAN-POLICY's ruled form, d6b5ca8 (a)/(b)); C2, P4 and F3 are not pre-empted.
  (b) A prediction "X [lo, hi]" is HELD iff the observed point lies in [lo, hi], endpoints inclusive (d6b5ca8 (b)).
  (c) P6 ("C0 reproduces both gates") is printed per leg as that leg's half; it is HELD iff BOTH outcome files print their
      C0 HELD (the registrar joins them); a C0 miss writes no outcome, so its refusal log carries P6 FAILED.
  (d) Leave-BBH-out G and per-source G use the policy fitted on ALL of TRAIN, restricted to the EVAL items of the subset (the
      paeec analogue +1.305 on 4,754 items is exactly this, router_clean_policy_outcome.txt L125-L132); their intervals come
      from the same two-stage replicates restricted to the subset.
  (e) The C2 / C3 floors are applied to the key-complete count computed from CELL EXISTENCE before the key is read (under
      AGREE_OR_UNUSABLE a cell's usability depends on values; the pre-read list is then fixed and the post-read count is
      printed beside, never used to re-select).
  (f) Leg M's C0 feeds pri.load_record's question set (the 2,811 judged p2dca questions, a p2dca judged-family OBJECT used
      only to reproduce a KEY number; no judged number is printed) into this script's builder.
[DELTA 2026-09-27, the engine-coder, after READY review e451753 and ruling R4 (programme L21831-L21846, 3fdc5d2); insertion
only] D1: every key SELECT filters its scope IN SQL with bound parameters (corpus_version, model IN the leg's roster, item_id IN
the side's items, chunked), so no GATE row, no model outside the roster (K37 on leg M) and no item outside the side reaches the
process; the rows fetched are counted and printed, and the selftest asserts that count against an independent in-scope count
on a fixture that carries out-of-scope rows. R4 (iii): variant_rule = UNUSABLE_CELL (the ruled default). R4 (ii): the other
four preconditions are NOT settable from the record and stay None (REPORTED): steward_bracket and residual_file (the data-
steward's half, owed, W0 RP02); train_unit (A1) and p2_measure (A2), which the review found genuinely ambiguous and R4 does not
rule. D2: the reviewer's 11 mutants are killed by value-asserting checks (the C1 interval = point +- 1.96 sd; per-stratum EVAL
unit counts in every replicate; the null re-derived with seeds 1..20; NO_RESIDUAL's n; P2 against a hand value; the C1
boundaries hi = -1e-9 / 0). D7: --c0 / --run refuse unless OMP / MKL / OPENBLAS are "1". D9 / D12: disclosure lines in the
outcomes. D10: the tripwire refuses a "*" select list. D11: a wrong K37 sha refuses (an unmutated negative check).
Key-scored end to end; no judge verdict enters, so no wrong(established) count and no convention A / B arises (stated).
Denominators: leg U 6,153 EVAL items / 5,642 CK-CLOSE components of pv2_1575de61bb20e977 (the scored subset printed); leg M
3,492 EVAL items / 3,400 components of pv2_41dbd3dbcd399df0, 13 categories after history (the scored subset printed).
[DELTA 2026-09-29 w0-delta3, the engine-coder, after delta-2 READY b2ad5ef C34-3; insertion only, the paragraphs above stand]
PRECONDITIONS set from the registrar's record of 2026-09-29 (e09e551) and the steward's counts 5572465: steward_bracket
(5572465 / e09e551), residual_file (experiment_configs/v2_residual_band15_19_eval_422.txt, sha256-bytes LF of record
b35b3e03...; load_residual now hashes the LF rendering, so a CRLF working tree identifies to the LF pin and both shas are
printed), train_unit "item" (ruling 3), p2_measure "contribution" (ruling 4). PLAN re-pinned to ruling 9 (D3 ADOPTED): C1
scored N 5,907 in 5,404 components, Kish 1.3115, n_eff 4,504, SE 0.00674, MDE80 1.89pp; C2 at 14 strata SE 0.0339, MDE80
0.095, SCOREABLE while the null p95 <= 0.60 (break-even about 0.745); "14 of the 52 union strata (13 MMLU-Pro + IFEval)" is
printed beside C2 and F3 (ruling 9); under T1 F1's line adds "USE clause NOT licensed as content-closed" (ruling 10). The
selftest's precondition refusals now run on explicitly unset copies; value checks on PRECONDITIONS, PLAN and the committed
residual file (422 ids).
[DELTA 2026-09-29 rp12-et, the engine-coder: the G14 TREE-CELL ARM of ARCH-V2-E-T (RP12), registered at 0a0361b
(docs/judge_v2_program.md L22028-L22060, G14 and Support (a)-(f)); insertion only, nothing above is rewritten]
  python tools/analysis/v2_declared_cells.py --dry-run --leg U --tree-cells <tsv> --tree-cells-sha256 <sha256 of its LF rendering>
  python tools/analysis/v2_declared_cells.py --run --leg U --tree-cells <tsv> --tree-cells-sha256 <hex>
  WITHOUT --tree-cells every mode is the pre-RP12 script (the selftest runs the base blob f7f30ebe and this file on the same
  fixture and compares the leg U outcome text line for line, the script-identity lines and the fixture paths normalised).
  WITH it (leg U only): the tree-cells file (header "# taxoarena-tree-cells-v1 ...", then "item_id<TAB>tree_cell"; one row per
  scored item, TRAIN and EVAL; tree_cell = the (source, domain) key B0's flatLeaf filing gives the item, "<unrouted>" allowed
  as its own cell; pinned by the sha256 of its LF rendering, a missing scored item REFUSES) adds a sixth arm, TREE cell: the
  per-cell policy fitted on TRAIN over the tree cells, by the SAME fit (fit(), absent group -> best single, argmax tie-break),
  inside the SAME two-stage replicates (the tree grouping draws no random number, so every other arm's replicates are
  unchanged). G_tree = acc(TREE cell) - acc(best single); M = G_tree - G_declared (TRUE (source, domain)); both through
  contrast(), the reader's deciding form (point +- 1.96 SE_2stage; percentile beside). G14 HELD iff lower(G_tree) > 0; FAILED
  iff upper(G_tree) <= 0; UNDETERMINED iff the interval covers 0. M is DESCRIPTIVE-ONLY (Support (f)). IDENTITY PRECONDITION
  (registered): the declared arm's C1 must print +2.67pp [+1.46pp, +3.89pp] (V2-DECLARED-CELLS C1 of record) to the printed
  digits, else [G14-IDENTITY] refuses and no outcome is written (the B1 marker stands: a failed precondition, not an outcome).
  C2 is not re-read in this run (V2-DECLARED-CELLS' criterion, recorded). Own write-once files: v2_declared_cells_G14_
  train_policy.json (B3: the TRAIN policy of BOTH the declared and the tree arm, written before open_eval), v2_declared_cells_
  G14_outcome.txt, v2_declared_cells_G14.READ_STARTED (B1). P5 (G_tree +2.5pp [+1.3, +3.7], M -0.2pp [-1.0, +0.6], endpoints
  inclusive, reading (b)) printed.
  SELFTEST (G14, executed through mode() on the sealed fixture): the base-blob inertness comparison; the identity tree (cell =
  the declared key: G_tree == C1 exactly, M == 0); the source-level tree (G_tree == the TRUE source arm's G, point and interval;
  M = G_tree - C1 by sign and value); the frozen tree policy; the identity-miss, missing-cell and pin refusals; the CRLF pin;
  the verdict boundaries and the P5 lines by value. MUTANTS (harness, one temporary edit at a time, reverted; T0 control
  survived): T1 tree arm scored on the declared cells, T2 G_tree against TDOM, T3 M sign flipped, T4 FAILED needs hi < 0, T5
  HELD admits lo = 0, T6 identity precondition removed, T7 pin check removed, T8 the tree branch skipped, T9 the P5 band
  shifted, T10 a legacy leg-U line changed (the inertness check), T11 the tree policy not frozen, T12 CRLF not normalised:
  12 of 12 killed; the 22 standing mutants still killed.
[DELTA 2026-09-30 rp12-et2, READY_rp12_et C-5; insertion only] with --tree-cells, the TRAIN items in rp12_pairing's
<no-routing-row> cell are printed (fitted as their own cell); an EVAL item of the scoring set (structurally key-complete) in
that cell REFUSES ([G14-NOROW]) BEFORE the B1 marker and the EVAL key read. [DELTA 2026-10-01 rp12-pair-mc, G14 RULING (b)
(orchestrator); insertion only] G14 does NOT exclude multi-class items (rows under two declared classes in B0's readout): the
declared arm must reproduce RP03's +2.67pp [+1.46pp, +3.89pp] on the full set, as registered; rp12_pairing gives them their modal
cell and discloses their keys. A tree-cells file carrying "<multi-class>" REFUSES at load ([G14-MULTI]). Selftest: the identity
passes with two such items present (scored, full set); the load refusal. Mutants (V0 control survived): V1 the load refusal
removed: killed. Mutants: R7 the refusal removed, R8 the count taken
outside the scoring set: 2 of 2 killed.
OUTPUTS (aggregates only, W11; write-once, mode "x"): experiment_results/archv2/v2_declared_cells/
  v2_declared_cells_U_train_policy.json (B3), v2_declared_cells_U_outcome.txt, v2_declared_cells_M_outcome.txt, and the B1
  markers *.READ_STARTED. No per-item EVAL key row is written anywhere.
[DELTA 2026-10-01 rp12-r2-lane; insertion only] --lane {r1,r2} (tools/analysis/rp12_lane.py; default r1 = the commands of
record, unchanged): a --tree-cells file of the other lane REFUSE; in lane r2 they must lie inside
experiment_configs/rp12_r2/ or experiment_results/archv2/rp12_r2/; lane r2 writes G14's files under
experiment_results/archv2/rp12_r2/g14/ (lane r1: OUT_DIR, unchanged); --lane without --tree-cells refuses.
[DELTA 2026-10-02 union-af-route, the engine-coder: UNION-AF-ROUTE (RP13; docs/judge_v2_program.md L22627-L22653 and the
AF-VS-KMEANS addition L23093-L23116, _as_of 50c71784); insertion only] Library hooks for tools/analysis/union_af_route.py, which
drives leg U through mode(); NO CLI flag is added here. cfg.xtrees ({arm name: {item_id: cell}}, only beside cfg.tree) adds one
policy arm per name (grouping "x:<name>", arm index 6.. in sorted name order) fitted by the SAME fit() inside the SAME two-stage
replicates (a grouping draws no random number); policy_json freezes their per-cell picks under "xtree_cell" (B3, re-checked
beside EVAL); the [G14-NOROW] refusal covers every extra arm. cfg.tail replaces g14_tail as the readout of a tree run. ABSENT
(no cfg.xtrees, no cfg.tail) every mode is byte-for-byte the previous blob c5b90278: union_af_route.py --selftest case
"vdc_inert" runs blob c5b90278 (git show) and this file on this file's fixture with a tree and compares the G14 outcome line for
line and the frozen policy key for key; this file's own --selftest (base blob f7f30ebe comparison) still passes.
[DELTA 2026-10-02 union-af-route C-4 (READY_union_af_route 502191e7); insertion only] cfg.pre_eval(cfg, policy, sha, say), when
set, runs right after the B3 policy file is written and BEFORE the EVAL view opens / the B1 marker (RP13's R10 equality); absent,
nothing changes (vdc_inert re-run).
"""
import os, sys, io, json, math, random, argparse, tempfile, shutil, hashlib, stat, re, contextlib, csv
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import v2_reader_guards as G
from data_v2 import ro as dv2ro
from data_v2 import views as dv2views
import profile_reliability_interaction as pri

pr = pri.pr
TEST_ID = "V2-DECLARED-CELLS"
PROG = "docs/judge_v2_program.md L21582-L21614 (as of a357ef0)"
RULING = "docs/reviews/RULING_w0_seal_k46_reuse.md (c5a8cb6)"
EXCLUDED = "Meta-Llama-3-70B-Instruct"
SPLIT_LABEL = "REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
GEN_REL = os.path.join("data_v2", SPLIT_LABEL, "gen_view_REG.db")
EVAL_REL = os.path.join("data_v2", SPLIT_LABEL, "eval_view_REG.db")
SIDE_TSV_REL = os.path.join("data_v2", "manifests", SPLIT_LABEL + "_side.tsv")
GEN_SHA = "c2930c609c67d6c7e1f8b8fbcd8f6f1970478a28f844d086d0b0db169d10c0ec"
EVAL_SHA = "e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369"
SIDE_TSV_TABLE_SHA = "75b4662eacf9adeb3aa44046e99c61712952668dd489a4933148fe9c5951117b"
POOL_U, CV_U = "pv2_1575de61bb20e977", "mc6-2026-09-11"
POOL_M, CV_M = "pv2_41dbd3dbcd399df0", "mmlu-pro-v2"
OUT_DIR = os.path.join(ROOT, "experiment_results", "archv2", "v2_declared_cells")
FORBIDDEN = ("output_zlib", "gt_raw", "answer_text", "pred", "reference")
VARIANT_RULES = ("UNUSABLE_CELL", "AGREE_OR_UNUSABLE", "REFUSE")
TRAIN_UNITS = ("component", "item")
P2_MEASURES = ("contribution", "leave_out")

# ---- the registrar's / steward's parameters: None REFUSES --run (set only by a delta of this script after a bracket) ----
# READY_w0_delta2 (b2ad5ef) C34-3: the four owed values set from the registrar's record of 2026-09-29 (e09e551; rulings 3, 4)
# and the steward's counts 5572465 (docs/reviews/STEWARD_w0_counts.md sections 1-2).
RESIDUAL_REL = "experiment_configs/v2_residual_band15_19_eval_422.txt"
RESIDUAL_SHA_LF = "b35b3e03b9bcda48b5f447e76249d2184b418a711920b9e80224d16ff50cee90"   # sha256-bytes, LF rendering (of record)
PRECONDITIONS = dict(variant_rule="UNUSABLE_CELL",  # ruling R4 (iii), programme L21831-L21846 (3fdc5d2): the ruled default
                     steward_bracket=("steward 5572465 (docs/reviews/STEWARD_w0_counts.md section 1: variant_rule UNUSABLE_CELL;"
                                      " leg U scored N 5,907 in 5,404 components, Kish 1.3115, 14 strata >= 120; leg M K12 3,351 /"
                                      " K37 3,350 key-complete of 3,492; 23 of the 422 residual inside pv2_41dbd3dbcd399df0;"
                                      " NO_RESIDUAL n 5,487), bracketed in the registrar's record of 2026-09-29 (e09e551)"),
                     residual_file=(RESIDUAL_REL, RESIDUAL_SHA_LF),       # steward 5572465 section 2 (422 ids)
                     train_unit="item",                                    # ruling 3 (A1), e09e551
                     p2_measure="contribution")                            # ruling 4 (A2), e09e551

# ---- the registered numbers (none is a CLI knob) ----
REG = dict(n_train_side=12358, n_gate=2033, n_eval_u=6153, comp_eval_u=5642, n_eval_m=3492, comp_eval_m=3400, roster_u=18,
           floor=120, excluded_categories=("history",), n_categories_m=14, B=2000, seed=42, placebo_seed=42, n_null=20,
           null_seeds=tuple(range(1, 21)), registry_m_total=47, registry_m_active=46, roster_k37=37, k12=12,
           c0_best="Qwen2.5-72B-Instruct", c0_bs="0.5912", c0_tdom="0.6220", c0_n_routed=21606, c0_n_eval=6482,
           c0_n_train=15124, c0_k12="0.8665", residual_n=422)
K37_DROPPED = ("deepseek", "flash_0shots_00_35_03", "gemini-1.5-flash-002", "gemini-1.5-pro-002", "gpt4o(2024-05-13)",
               "jamba-1.5-large", "opus_2shots_00_37_14", "sonnet-3.5_0shots_09_34_29", "sonnet_0shots_12_01_18")
K37_SHA = "3a3204cc35cf600495506e6e1f545ab379707b26c16371df78ce654837846f91"
NAME_MATCHED = (("Llama-3.1-70B-Instruct", "Meta-Llama-3_1-70B-Instruct"), ("Mixtral-8x7B-Instruct-v0.1", "Mixtral-8x7B-Instruct-v0.1"))
# Support (registered planning numbers, printed beside the measured ones)
# ruling 9 (D3 ADOPTED, e09e551): C1 at scored N 5,907 / Kish 1.3115, SE 0.00674, MDE 1.89pp; C2 at 14 strata SE 0.0339, MDE
# 0.095, SCOREABLE while the null p95 <= 0.60 (break-even about 0.745). The superseded registered plan (1.711 / 3,596 / 0.00659)
# is not printed.
STRATA_BESIDE = "14 of the 52 union strata (13 MMLU-Pro + IFEval)"
PLAN = dict(C1=dict(deff=1.3115, n=5907, components=5404, n_eff=round(5907 / 1.3115), se=0.00674, mde=round(2.80 * 0.00674, 4),
                    verdict="SCOREABLE (ruling 9, D3 ADOPTED)"),
            C2=dict(se=0.0339, mde=0.095, verdict="SCOREABLE while the null p95 <= 0.60 (break-even about 0.745); " + STRATA_BESIDE),
            C3_K12=dict(se=0.0339, mde=0.095, verdict="SCOREABLE"), C3_K37=dict(se=0.0441, mde=0.124, verdict="SCOREABLE"))
PRED = dict(P1=(0.015, 0.040, 0.030), P3=(0.0, 0.025, 0.012), P4=(0.78, 0.90, 0.84), P5_K12=(0.80, 0.93, 0.87),
            P5_K37=(0.74, 0.90, 0.82), P7=(1.3, 2.2, None))
COMPARATORS_M = dict(K12="0.8665 [0.8000, 0.9330]", K46="0.8118 [0.7254, 0.8983]")

BS, TSRC, TDOM, ORACLE, PLAC = range(5)
ARMS = ("best single", "TRUE source", "TRUE source/domain", "oracle", "PLACEBO")
# RP12 G14 (0a0361b): the tree-cell arm, present only with --tree-cells
TREE = 5
ARM_TREE = "TREE cell (B0 flatLeaf)"
G14_REG = "docs/judge_v2_program.md L22028-L22060 (ARCH-V2-E-T, registered at 0a0361b)"
G14_IDENTITY = ("+2.67pp", "+1.46pp", "+3.89pp")     # V2-DECLARED-CELLS C1 of record, the declared arm's printed digits
P5_G14 = dict(G=(0.013, 0.037), M=(-0.010, 0.006))
TREE_CELLS_FORMAT = "taxoarena-tree-cells-v1"
NO_ROUTING_ROW = "<no-routing-row>"                  # rp12_pairing's P6 cell (READY_rp12_et C-5)
MULTI_CLASS = "<multi-class>"                        # G14 RULING (b) 2026-10-01: never a tree cell (G14 does not exclude)
MUTANT = None       # SELFTEST-ONLY defect switch; every real mode refuses when it is set
EVENTS = []         # ordered event log (selftest observation of the B3 order)

BRANCHES_U = ("C0U.HELD", "T1.FIRED", "T1.NOT_FIRED", "C1.HELD", "C1.FAILED", "C1.UNDETERMINED", "C1.VOID",
              "C2.HELD", "C2.FAILED", "C2.UNDETERMINED", "P1.HELD", "P1.FAILED", "P1.UNDET_TRIGGER", "P2.HELD", "P2.FAILED",
              "P2.UNDET_TRIGGER", "P2.UNDET_G", "P3.HELD", "P3.FAILED", "P3.UNDET_TRIGGER", "P4.HELD", "P4.FAILED",
              "P6.HALF_HELD", "P7.HELD", "P7.FAILED", "P7.UNDET_TRIGGER", "F1.FIRED", "F1.NOT_FIRED", "F1.NOT_EVALUATED",
              "F3.FIRED", "F3.NOT_FIRED")
BRANCHES_M = ("C0M.HELD", "C3.HELD", "C3.FAILED", "C3.UNDETERMINED", "P5.HELD", "P5.FAILED", "P6.HALF_HELD", "F2.FIRED",
              "F2.NOT_FIRED")
BRANCHES_G14 = ("G14.IDENTITY_OK", "G14.HELD", "G14.FAILED", "G14.UNDETERMINED", "P5T.HELD", "P5T.FAILED")
BR = G.Branches(BRANCHES_U + BRANCHES_M + ("G3.REFUSED", "G4.REFUSED", "C0.REFUSED", "B3.REFUSED") + BRANCHES_G14)


def ev(name):
    EVENTS.append(name)


# ============================================================================================ configuration
class Cfg:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def real_cfg():
    import rubric_p8
    return Cfg(gen_path=os.path.join(DATA_ROOT, GEN_REL), eval_path=os.path.join(DATA_ROOT, EVAL_REL),
               side_tsv=os.path.join(DATA_ROOT, SIDE_TSV_REL), gen_sha=GEN_SHA, eval_sha=EVAL_SHA,
               pool_u=POOL_U, cv_u=CV_U, pool_m=POOL_M, cv_m=CV_M, reg=dict(REG), pre=dict(PRECONDITIONS),
               k12=tuple(sorted(rubric_p8.ARENA12)), k37_dropped=K37_DROPPED, k37_sha=K37_SHA,
               policy_path=os.path.join(OUT_DIR, "v2_declared_cells_U_train_policy.json"),
               out_u=os.path.join(OUT_DIR, "v2_declared_cells_U_outcome.txt"),
               out_m=os.path.join(OUT_DIR, "v2_declared_cells_M_outcome.txt"),
               mark_u=os.path.join(OUT_DIR, "v2_declared_cells_U.READ_STARTED"),
               mark_m=os.path.join(OUT_DIR, "v2_declared_cells_M.READ_STARTED"),
               c0_u=c0_rcp_real, c0_m=c0_pri_real, residual_root=ROOT, hook=None)


def missing_preconditions(cfg):
    bad = []
    p = cfg.pre
    if p.get("variant_rule") not in VARIANT_RULES:
        bad.append("variant_rule (the data-steward's multi-response variant rule; options %s)" % (VARIANT_RULES,))
    if not p.get("steward_bracket"):
        bad.append("steward_bracket (the programme line / commit of the steward's half: coverage, variant rule, 422 count)")
    if not (isinstance(p.get("residual_file"), tuple) and len(p["residual_file"]) == 2):
        bad.append("residual_file ((path, sha256-bytes) of the steward's 422 residual EVAL item ids)")
    if p.get("train_unit") not in TRAIN_UNITS:
        bad.append("train_unit (AMBIGUITY A1: leg U's TRAIN-stage resampling unit, %s)" % (TRAIN_UNITS,))
    if p.get("p2_measure") not in P2_MEASURES:
        bad.append("p2_measure (AMBIGUITY A2: the measure of P2 'BBH carries >= 50%% of G', %s)" % (P2_MEASURES,))
    return bad


def precondition_lines(cfg):
    out = ["PRECONDITIONS (None REFUSES --run; set only by a delta of this script after the bracket that decides each):"]
    for k in ("variant_rule", "steward_bracket", "residual_file", "train_unit", "p2_measure"):
        out.append("  %-16s %r" % (k, cfg.pre.get(k)))
    miss = missing_preconditions(cfg)
    out.append("  -> %s" % ("ALL SET" if not miss else "%d UNSET: %s" % (len(miss), "; ".join(miss))))
    return out


def load_residual(cfg):
    rf = cfg.pre.get("residual_file")
    if not rf:
        return None, "owed (the steward's list; precondition residual_file unset)"
    path = rf[0] if os.path.isabs(rf[0]) else os.path.join(cfg.residual_root, rf[0])
    with open(path, "rb") as f:
        raw = f.read()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()      # the LF rendering is of record (CONTEXT rule 8)
    if got != rf[1]:
        raise SystemExit("[PIN] residual file %s sha256-bytes (LF) %s != the pinned %s" % (path, got, rf[1]))
    ids = [l.strip() for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")]
    if len(ids) != len(set(ids)):
        raise SystemExit("[PIN] residual file carries repeated ids")
    return frozenset(ids), "%s sha256-bytes (LF) %s (file bytes %s), %d ids" % (path, got, hashlib.sha256(raw).hexdigest(), len(ids))


def load_tree_cells(path, sha_lf):
    """RP12 G14: {item_id: tree_cell} from the tree-cells file, pinned by the sha256 of its LF rendering."""
    with open(path, "rb") as f:
        raw = f.read()
    lf = raw.replace(b"\r\n", b"\n")
    got = hashlib.sha256(lf).hexdigest()
    if got != sha_lf:
        raise SystemExit("[G14-PIN] tree-cells file %s sha256 (LF) %s != the pinned %s" % (path, got, sha_lf))
    lines = lf.decode("utf-8").split("\n")
    if not lines[0].startswith("# " + TREE_CELLS_FORMAT) or len(lines) < 2 or lines[1].split("\t") != ["item_id", "tree_cell"]:
        raise SystemExit("[G14-PIN] tree-cells file %s: bad header (want '# %s ...' then item_id<TAB>tree_cell)" % (path, TREE_CELLS_FORMAT))
    cells = {}
    for ln in lines[2:]:
        if not ln:
            continue
        parts = ln.split("\t")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise SystemExit("[G14-PIN] tree-cells file %s: malformed row %r" % (path, ln[:80]))
        if parts[0] in cells:
            raise SystemExit("[G14-PIN] tree-cells file %s: item %s repeated" % (path, parts[0]))
        if parts[1] == MULTI_CLASS:
            raise SystemExit("[G14-MULTI] tree-cells file %s: item %s carries %s; G14 does not exclude multi-class items (ruling (b)):"
                             " rebuild the file with rp12_pairing, which gives them their modal cell" % (path, parts[0], MULTI_CLASS))
        cells[parts[0]] = parts[1]
    return cells, "%s sha256 (LF) %s, %d items, %d distinct tree cells; header %r" % (path, got, len(cells),
                                                                                          len(set(cells.values())), lines[0][:120])


# ============================================================================================ reading (views)
def open_tw(kind, stage, path, sha, label, say):
    before = G.sha256_file(path)
    say("  %s %s | sha256-bytes BEFORE %s (%s) | sidecars: %s" % (label, path, before,
                                                                   "= the pinned sha" if before == sha else "NOT the pinned %s" % sha,
                                                                   G.sidecar_line(path)))
    if before != sha:
        raise SystemExit("[PIN] %s: sha256-bytes %s != the pinned %s" % (path, before, sha))
    conn = dv2views.open_generation(stage, path, sha) if kind == "gen" else dv2views.open_eval(stage, path, sha)
    ev("open:%s:%s" % (kind, stage))
    return G.KeyTripwire(conn, FORBIDDEN, label="%s(%s)" % (label, stage)), before


def after_sha(path, before, label, say):
    after = G.sha256_file(path)
    say("  %s sha256-bytes AFTER %s (%s)" % (label, after, "EQUAL to before" if after == before else "DIFFERS from before %s" % before))
    return after == before


def pool_row(tw, pool_id, cv):
    for pid, scope, nc, by in tw.execute("SELECT pool_id, scope, n_components, n_items_by_scope FROM pool").fetchall():
        if pid == pool_id:
            d = json.loads(by)
            if cv not in d:
                raise SystemExit("[POOL] pool %s: n_items_by_scope %r lacks %s" % (pid, by, cv))
            return int(nc), int(d[cv]), scope
    raise SystemExit("[POOL] the view carries no pool row %s" % pool_id)


def registry(tw, cv):
    rows = tw.execute("SELECT model, status FROM model_registry WHERE corpus_version=?", (cv,)).fetchall()
    return {m: s for m, s in rows}


def side_items(tw, cv, side):
    """{item_id: (component_id, stratum_source, stratum_domain)} for the items of corpus cv on `side` (side JOIN item ON the
    corpus version; the counted ids asserted distinct)."""
    rows = tw.execute("SELECT s.item_id, s.component_id, s.stratum_source, s.stratum_domain FROM side s JOIN item i ON"
                      " i.item_id = s.item_id AND i.corpus_version = ? WHERE s.side = ?", (cv, side)).fetchall()
    d = {r[0]: (r[1], r[2], r[3]) for r in rows}
    if len(d) != len(rows):
        raise SystemExit("[READ] side JOIN item returned repeated ids for %s / %s" % (cv, side))
    return d


def side_counts(tw):
    return Counter(s for (s,) in tw.execute("SELECT side FROM side"))


def component_strata(tw):
    return {c: (s, d, sd) for c, s, d, sd in tw.execute("SELECT component_id, stratum_source, stratum_domain, side FROM component")}


def cell_counts(tw, table, cv, models, items):
    """{item: {model: number of response rows}} over `items` and `models` (NO key column is selected)."""
    ms = set(models)
    out = defaultdict(dict)
    for m, iid, n in tw.execute("SELECT model, item_id, COUNT(*) FROM %s WHERE corpus_version=? GROUP BY model, item_id" % table,
                                (cv,)):
        if m in ms and iid in items:
            out[iid][m] = int(n)
    return out


def structurally_complete(cc, models, rule):
    """Items whose every model cell can be usable under `rule` BEFORE the key is read: single-response cells for
    UNUSABLE_CELL; >= 1 response for AGREE_OR_UNUSABLE / REFUSE (a REFUSE multi cell refuses at the read)."""
    need_one = rule == "UNUSABLE_CELL"
    ok = set()
    for iid, d in cc.items():
        if all((d.get(m, 0) == 1) if need_one else (d.get(m, 0) >= 1) for m in models):
            ok.add(iid)
    return ok


def multi_cells(cc, models):
    return sum(1 for d in cc.values() for m in models if d.get(m, 0) > 1)


def read_key(tw, table, cv, models, items, overlay, rule):
    """THE KEY READ. {item: {model: 0/1}} over usable cells, and the counts. overlay: is_correct_mathfix where non-null."""
    cols = "model, item_id, is_correct" + (", is_correct_mathfix" if overlay else "")
    ms = set(models)
    vals = defaultdict(list)
    n_overlay = n_overlay_changed = 0
    fetched = 0
    mlist = sorted(ms)
    ilist = sorted(items)
    # D1 (READY e451753; ruling R4 (i)): the scope is filtered IN SQL, bound parameters, never after SQLite returned the row
    rows = []
    for s0 in range(0, len(ilist), 500):
        ch = ilist[s0:s0 + 500]
        if MUTANT == "sql_unfiltered":
            if s0 == 0:
                rows.extend(tw.execute("SELECT %s FROM %s WHERE corpus_version=?" % (cols, table), (cv,)))
            continue
        rows.extend(tw.execute("SELECT %s FROM %s WHERE corpus_version=? AND model IN (%s) AND item_id IN (%s)"
                               % (cols, table, ",".join("?" * len(mlist)), ",".join("?" * len(ch))), [cv] + mlist + ch))
    for row in rows:
        fetched += 1
        m, iid, c = row[0], row[1], int(row[2])
        if m not in ms or iid not in items:
            continue
        v = c
        if overlay and MUTANT != "no_overlay" and row[3] is not None:
            n_overlay += 1
            v = int(row[3])
            n_overlay_changed += int(v != c)
        vals[(iid, m)].append(v)
    K = defaultdict(dict)
    st = Counter()
    for (iid, m), vs in vals.items():
        if len(vs) == 1:
            K[iid][m] = vs[0]; st["single"] += 1
            continue
        st["multi"] += 1
        if MUTANT == "multi_last_wins":
            K[iid][m] = vs[-1]
        elif rule == "REFUSE":
            raise SystemExit("[VARIANT-RULE] REFUSE: (model %s, item %s) carries %d responses" % (m, iid, len(vs)))
        elif rule == "AGREE_OR_UNUSABLE" and len(set(vs)) == 1:
            K[iid][m] = vs[0]; st["multi_agree_used"] += 1
        else:
            st["multi_unusable"] += 1
    st["overlay_rows"] = n_overlay
    st["overlay_changed"] = n_overlay_changed
    st["key_rows_fetched"] = fetched
    return K, st


def complete_items(K, models):
    return sorted(i for i, d in K.items() if all(m in d for m in models))


def k37_roster(reg_map, cfg):
    active = sorted(m for m, s in reg_map.items() if s == "ACTIVE")
    quar = sorted(m for m, s in reg_map.items() if s != "ACTIVE")
    bad = []
    if len(reg_map) != cfg.reg["registry_m_total"]: bad.append("registry %d != %d" % (len(reg_map), cfg.reg["registry_m_total"]))
    if len(active) != cfg.reg["registry_m_active"]: bad.append("ACTIVE %d != %d" % (len(active), cfg.reg["registry_m_active"]))
    if EXCLUDED in active: bad.append("%s ACTIVE" % EXCLUDED)
    miss = [m for m in cfg.k37_dropped if reg_map.get(m) != "ACTIVE"]
    if miss: bad.append("dropped models not ACTIVE / absent: %s" % miss)
    roster = [m for m in active if m not in set(cfg.k37_dropped)]
    sha = hashlib.sha256("\n".join(roster).encode("utf-8")).hexdigest()
    if len(roster) != cfg.reg["roster_k37"]: bad.append("|K37| %d != %d" % (len(roster), cfg.reg["roster_k37"]))
    if sha != cfg.k37_sha and MUTANT != "k37_sha_off": bad.append("K37 sha256-text %s != %s" % (sha, cfg.k37_sha))
    k12_out = sorted(set(cfg.k12) - set(roster))
    if k12_out: bad.append("K12 models outside K37: %s" % k12_out)
    if len(set(cfg.k12)) != cfg.reg["k12"]: bad.append("|K12| %d != %d" % (len(set(cfg.k12)), cfg.reg["k12"]))
    if bad:
        raise SystemExit("[ROSTER] leg M roster check failed: " + "; ".join(bad))
    return roster, quar, sha


# ============================================================================================ leg U arrays, fit, bootstrap
class UD:
    pass


def _index(labels):
    keys = sorted(set(labels)); pos = {k: i for i, k in enumerate(keys)}
    return keys, np.array([pos[x] for x in labels], dtype=np.int64)


def build_ud(models, train_meta, eval_meta, K_tr, K_ev, comp_strata, train_unit, residual, placebo_seed, tree=None, xtrees=None):
    """Positions = every scored item (TRAIN key-complete + EVAL key-complete), sorted by item_id (the placebo's order)."""
    D = UD(); D.models = list(models); m = len(models)
    tr = [i for i in complete_items(K_tr, models)]; evl = [i for i in complete_items(K_ev, models)]
    if set(tr) & set(evl):
        raise SystemExit("[G3(2)] an item is on both sides")
    meta = dict((i, train_meta[i]) for i in tr); meta.update((i, eval_meta[i]) for i in evl)
    items = sorted(meta); D.items = items; D.n = n = len(items)
    D.is_eval = np.array([i in eval_meta for i in items], dtype=bool)
    D.A = np.array([[(K_ev if D.is_eval[k] else K_tr)[i][mm] for mm in models] for k, i in enumerate(items)],
                   dtype=np.int64).reshape(n, m)
    D.src = [meta[i][1] for i in items]; D.dom = [(meta[i][1], meta[i][2]) for i in items]
    D.comp = [meta[i][0] for i in items]
    D.src_keys, D.g_tsrc = _index(D.src)
    D.dom_keys, D.g_tdom = _index(D.dom)
    labels = [int(x) for x in D.g_tdom]
    plac = labels[:]
    if MUTANT != "placebo_identity":
        random.Random(placebo_seed).shuffle(plac)
    D.g_plac = np.array(plac, dtype=np.int64)
    D.groupings = {"tsrc": (D.g_tsrc, len(D.src_keys)), "tdom": (D.g_tdom, len(D.dom_keys)), "plac": (D.g_plac, len(D.dom_keys))}
    if tree is not None:                                         # RP12 G14: the tree-cell grouping (absent = the pre-RP12 arrays)
        miss = [i for i in items if i not in tree]
        if miss:
            raise SystemExit("[G14] %d scored item(s) carry no tree cell (first %s)" % (len(miss), miss[:3]))
        D.tree_keys, D.g_tree = _index([tree[i] for i in items])
        D.groupings["tree"] = (D.g_tree, len(D.tree_keys))
    if xtrees:                                                   # RP13 UNION-AF-ROUTE: extra tree-cell arms (absent = unchanged)
        if tree is None:
            raise SystemExit("[RP13] the extra tree-cell arms need the tree arm")
        D.xnames, D.xkeys = sorted(xtrees), {}
        for nm in D.xnames:
            miss = [i for i in items if i not in xtrees[nm]]
            if miss:
                raise SystemExit("[RP13] arm %s: %d scored item(s) carry no cell (first %s)" % (nm, len(miss), miss[:3]))
            D.xkeys[nm], g_ = _index([xtrees[nm][i] for i in items])
            D.groupings["x:" + nm] = (g_, len(D.xkeys[nm]))
    D.flat = {k: (g[:, None] * m + np.arange(m)[None, :]).ravel() for k, (g, _) in D.groupings.items()}
    D.E = np.flatnonzero(D.is_eval); D.T = np.flatnonzero(~D.is_eval)
    D.train_set = frozenset(np.flatnonzero(~D.is_eval).tolist())
    # EVAL units: components within the item stratum (a multi-stratum EVAL component refuses)
    ecomp_str = {}
    for k in D.E:
        c = D.comp[k]
        if ecomp_str.setdefault(c, D.dom[k]) != D.dom[k]:
            raise SystemExit("[CLUSTER] EVAL component %s spans strata" % c)
    D.eval_units = _units([int(k) for k in D.E], (lambda k: D.comp[k]) if MUTANT != "eval_item_unit" else (lambda k: D.items[k]),
                          lambda k: D.dom[k], base=D.E)
    if train_unit == "component" and MUTANT != "train_unit_ignored":
        D.train_units = _units([int(k) for k in D.T], lambda k: D.comp[k],
                               lambda k: (comp_strata[D.comp[k]][0], comp_strata[D.comp[k]][1]), base=None)
    else:
        D.train_units = _units([int(k) for k in D.T], lambda k: D.items[k], lambda k: D.dom[k], base=None)
    D.fit_asserts = 0
    # subsets over EVAL positions
    srcE = [D.src[k] for k in D.E]
    subs = [("ALL", np.ones(len(D.E), bool))]
    if residual is not None:
        subs.append(("NO_RESIDUAL", np.array([D.items[k] not in residual for k in D.E], bool)))
    subs.append(("NON_BBH", np.array([s != "BBH" for s in srcE], bool)))
    for s in sorted(set(srcE)):
        subs.append(("SRC:" + s, np.array([x == s for x in srcE], bool)))
    D.subsets = subs
    D.n_train, D.n_eval = len(D.T), len(D.E)
    return D


def _units(positions, unit_of, stratum_of, base):
    """-> dict(unit_pos: array over `positions` of unit index, strata: [array of unit indices per stratum (sorted keys)],
    n_units). base: when positions are EVAL positions, unit_pos is aligned with base (positions within E)."""
    ukeys = sorted(set(unit_of(k) for k in positions))
    upos = {u: j for j, u in enumerate(ukeys)}
    unit_pos = np.array([upos[unit_of(k)] for k in positions], dtype=np.int64)
    ustr = {}
    for k in positions:
        ustr.setdefault(unit_of(k), stratum_of(k))    # a TRAIN component's stratum is its component row (one value per unit)
    by = defaultdict(list)
    for u, s in ustr.items():
        by[s].append(upos[u])
    strata = [np.array(sorted(by[s]), dtype=np.int64) for s in sorted(by)]
    return dict(unit_pos=unit_pos, strata=strata, n_units=len(ukeys), positions=np.array(positions, dtype=np.int64))


def draw_units(rng, U):
    cnt = np.zeros(U["n_units"], dtype=np.int64)
    for arr in U["strata"]:
        if len(arr):
            cnt += np.bincount(arr[rng.integers(0, len(arr), len(arr))], minlength=U["n_units"])
    return cnt[U["unit_pos"]]


class Policy:
    pass


def fit(D, w):
    """Every policy fitted on the items carrying weight w (integer multiplicities over positions). G3: the support of w must
    be TRAIN (checked at the call; SystemExit, python -O safe)."""
    nz = np.flatnonzero(w)
    if MUTANT != "g3_off" and not set(nz.tolist()) <= D.train_set:
        BR.hit("G3.REFUSED")
        raise SystemExit("[G3(4)] a policy fit received %d EVAL item(s)" % len(set(nz.tolist()) - D.train_set))
    D.fit_asserts += 1
    m = len(D.models)
    W = D.A * w[:, None]
    tot = W.sum(axis=0)
    P = Policy()
    P.gb = int(np.argmax(tot)) if MUTANT != "tie_last" else int(m - 1 - np.argmax(tot[::-1]))
    Wr = W.ravel().astype(np.float64); wf = w.astype(np.float64)
    P.pol = {}
    for k, (g, ng) in D.groupings.items():
        S = np.bincount(D.flat[k], weights=Wr, minlength=ng * m).reshape(ng, m)
        mass = np.bincount(g, weights=wf, minlength=ng)
        pol = S.argmax(axis=1).astype(np.int64) if MUTANT != "tie_last" else (m - 1 - S[:, ::-1].argmax(axis=1)).astype(np.int64)
        pol[mass < 1] = -1
        P.pol[k] = pol
    return P


def correctness_E(D, P):
    gb = np.full(len(D.E), P.gb, dtype=np.int64)
    res = lambda k: np.where(P.pol[k][D.groupings[k][0][D.E]] < 0, gb, P.pol[k][D.groupings[k][0][D.E]])
    A = D.A[D.E]; r = np.arange(len(D.E))
    rows = [A[r, gb], A[r, res("tsrc")], A[r, res("tdom")], A.max(axis=1), A[r, res("plac")]]
    if "tree" in P.pol:                                          # RP12 G14: the sixth arm, TREE (index 5)
        rows.append(A[r, res("tree")])
    for nm in getattr(D, "xnames", ()):                          # RP13: the extra arms, indices 6.. in sorted name order
        rows.append(A[r, res("x:" + nm)])
    return np.stack(rows).astype(np.float64)


def train_full(D):
    w = np.zeros(D.n, dtype=np.int64); w[D.T] = 1
    if MUTANT == "fit_on_eval":
        w[D.E[:3]] = 1
    return w


def policy_json(D, P, cfg, gen_sha):
    tdom = {"%s/%s" % D.dom_keys[i]: (D.models[p] if p >= 0 else None) for i, p in enumerate(P.pol["tdom"])}
    tsrc = {D.src_keys[i]: (D.models[p] if p >= 0 else None) for i, p in enumerate(P.pol["tsrc"])}
    pj = dict(test=TEST_ID, leg="U", kind="frozen TRAIN policy (B3: the declared arm of every later EVAL read on %s)" % cfg.pool_u,
                pool=cfg.pool_u, corpus_version=cfg.cv_u, gen_view_sha256_bytes=gen_sha, roster=D.models,
                tie_break="the first model in sorted-name order (numpy argmax over the sorted roster)",
                absent_group="best single", key="is_correct with the MATH-FIX overlay (is_correct_mathfix where non-null)",
                variant_rule=cfg.pre.get("variant_rule"), train_items_scored=int(D.n_train),
                best_single=D.models[P.gb], true_source=tsrc, true_source_domain=tdom,
                script=G.script_identity(os.path.abspath(__file__))[0])
    if "tree" in P.pol:                                          # RP12 G14: the tree arm's frozen TRAIN policy
        pj["tree_cell"] = {D.tree_keys[i]: (D.models[q] if q >= 0 else None) for i, q in enumerate(P.pol["tree"])}
        pj["g14"] = "the tree-cell arm of %s (tree cells: %s)" % (G14_REG, getattr(cfg, "tree_desc", None))
    if getattr(D, "xnames", ()):                                 # RP13: the extra arms' frozen TRAIN policies
        pj["xtree_cell"] = {nm: {D.xkeys[nm][i]: (D.models[q] if q >= 0 else None) for i, q in enumerate(P.pol["x:" + nm])}
                            for nm in D.xnames}
    return pj


def run_boot(D, B, seed, hook=None):
    P0 = fit(D, train_full(D)); CE0 = correctness_E(D, P0)
    NE = len(D.E); S = len(D.subsets); NA = CE0.shape[0]          # NA = 5 arms, 6 with the RP12 tree arm
    masks = [mk for _, mk in D.subsets]
    def score(CE, v):
        out = np.empty((S, NA))
        for j, mk in enumerate(masks):
            vv = v * mk
            out[j] = CE @ vv / vv.sum() if vv.sum() else np.nan
        return out
    point = score(CE0, np.ones(NE))
    rng = np.random.default_rng(seed); iid = np.empty((B, S, NA))
    for b in range(B):
        iid[b] = score(CE0, np.bincount(rng.integers(0, NE, NE), minlength=NE).astype(np.float64))
    rng = np.random.default_rng(seed); two = np.empty((B, S, NA))
    for b in range(B):
        wt = np.zeros(D.n, dtype=np.int64); wt[D.T] = draw_units(rng, D.train_units)
        P = fit(D, wt)
        v = draw_units(rng, D.eval_units).astype(np.float64)
        two[b] = score(correctness_E(D, P), v)
        if hook: hook(D, wt, v)
    return dict(P0=P0, point=point, iid=iid, two=two, B=B)


def _var(x):
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    if x.size < 2 or float(np.ptp(x)) == 0.0:
        return 0.0
    return float(np.var(x, ddof=1))


def contrast(bt, D, sub, a, b):
    j = [n for n, _ in D.subsets].index(sub)
    pt = float(bt["point"][j, a] - bt["point"][j, b])
    d2 = bt["two"][:, j, a] - bt["two"][:, j, b]; di = bt["iid"][:, j, a] - bt["iid"][:, j, b]
    v2, vi = _var(d2), _var(di)
    se2, sei = math.sqrt(v2), math.sqrt(vi)
    n = int(D.subsets[j][1].sum())
    deff = (v2 / vi) if vi > 0 else float("nan")
    if MUTANT == "deff_inverse" and v2 > 0:
        deff = vi / v2
    return dict(sub=sub, point=pt, se2=se2, lo=pt - 1.96 * se2, hi=pt + 1.96 * se2, se_iid=sei, var2=v2,
                pct=tuple(float(x) for x in np.nanpercentile(d2, [2.5, 97.5])), n=n, deff=deff,
                n_eff=(n / deff) if deff == deff and deff > 0 else float("nan"), mde=2.80 * se2)


def gate_g4(c1, cp):
    for name, c in (("C1", c1), ("PLACEBO", cp)):
        if c["var2"] == 0.0:
            BR.hit("G4.REFUSED")
            raise SystemExit("[G4] the two-stage variance of %s is 0: every interval is degenerate; refusing" % name)


# ============================================================================================ profiles (C2, C3; pri estimator)
def key_builder(K, models):
    def kb(cqs):
        d = {}
        for m in models:
            v = [K[q][m] for q in cqs if q in K and m in K[q]]
            if v:
                d[m] = sum(v) / len(v)
        return d if len(d) == len(models) else None
    return kb


def profile_leg(cells, K, models, tag, null=True, progress=None):
    qsel = set(q for v in cells.values() for q in v)
    d = pri.leg(cells, qsel, key_builder(K, models), models, tag, progress=progress)
    iv = pri.intervals(d, "both")
    out = dict(R=iv["R"], sd=iv["sd"], lo=iv["lo_re"], hi=iv["hi_re"], lo_fx=iv["lo_fx"], hi_fx=iv["hi_fx"],
               se_re=iv["se_re"], n_halvings=iv["n"], cells=list(cells), n_items=sum(len(v) for v in cells.values()),
               R_model=pri.intervals(d, "model")["R"])
    if MUTANT == "jk_fixed_decides":
        out["lo"], out["hi"] = iv["lo_fx"], iv["hi_fx"]
    if null:
        nt = pri.null_tables(cells, K, models, len(REG["null_seeds"]), list(REG["null_seeds"]))
        inter = sorted(x[1] for x in nt["reads"])
        out["null_reads"] = inter
        out["null_p95"] = inter[-1] if MUTANT == "p95_max" else inter[18]
        out["null_median"] = pri.summarise_null(nt["reads"], 1)[0]
        out["null_clipped"] = nt["clipped"]
        vd = pri.variance_decomposition(nt["k"], nt["n"])
        out["vd_shares"] = vd["shares"]
    return out


def r_verdict(p):
    """The C2 / C3 rule: HELD iff lo > p95; FAILED iff hi <= p95; UNDETERMINED otherwise."""
    if G.as_bool(p["lo"] > p["null_p95"]):
        return "HELD"
    if G.as_bool(p["hi"] <= p["null_p95"]) if MUTANT != "strict_hi" else G.as_bool(p["hi"] < p["null_p95"]):
        return "FAILED"
    return "UNDETERMINED"


def in_range(x, lo, hi):
    return G.as_bool(x == x and lo <= x <= hi)


# ============================================================================================ verdict lines (every branch hit)
def _pp(x):
    return "%+.2fpp" % (100 * x)


def verdict_lines_u(st):
    L = []
    say = L.append
    c1, cp = st["C1"], st["PLAC"]
    say("")
    say("=== VERDICTS (leg U) ===")
    say("C0 (validity, evaluated FIRST, before any v2 read): best single %s %s, TRUE (source, domain) %s | registered %s / %s / %s"
        " -> HELD" % (st["c0"]["best"], st["c0"]["bs"], st["c0"]["tdom"], REG["c0_best"], REG["c0_bs"], REG["c0_tdom"]))
    BR.hit("C0U.HELD")
    say("    DISCLOSURE (READY e451753 D9): C0-U runs through ROUTER-CLEAN-POLICY's loader, so it tests the fit and the fallbacks,"
        " not read_key, the variant rule or the MATH-FIX overlay (the selftest covers those)")
    say("    DISCLOSURE (D12): the placebo's TRAIN pseudo-strata depend on the set of key-complete EVAL items (the shuffle runs over"
        " TRAIN plus EVAL; the carried RCP form); the placebo is a trigger only, not part of the B3 file")
    t1 = G.as_bool(cp["lo"] > 0) if MUTANT != "t1_ignored" else False
    say("PLACEBO P = acc(PLACEBO) - acc(best single) = %s | two-stage [%s, %s] | percentile [%s, %s] (printed beside; validity"
        " trigger T1)" % (_pp(cp["point"]), _pp(cp["lo"]), _pp(cp["hi"]), _pp(cp["pct"][0]), _pp(cp["pct"][1])))
    if t1:
        BR.hit("T1.FIRED")
        say("  T1 FIRED: the placebo's two-stage interval lies wholly above 0: the instrument manufactures gain from noise;"
            " C1 is VOID")
    else:
        BR.hit("T1.NOT_FIRED")
        say("  T1 not fired (the placebo's two-stage interval is not wholly above 0)")
    say("C1 DECLARED-CELL GAIN G = acc_EVAL(TRUE (source, domain)) - acc_EVAL(best single) = %s | DECIDING two-stage interval"
        " [%s, %s] (point +- 1.96 x %.5f) | beside: percentile [%s, %s], i.i.d. SE %.5f | bar 0 | n = %d EVAL items"
        % (_pp(c1["point"]), _pp(c1["lo"]), _pp(c1["hi"]), c1["se2"], _pp(c1["pct"][0]), _pp(c1["pct"][1]), c1["se_iid"], c1["n"]))
    say("    SUPPORT (measured): SE_2stage %.5f | SE_iid %.5f -> DEFF %.3f, n_eff %.0f, MDE80 = 2.80 x SE = %s"
        % (c1["se2"], c1["se_iid"], c1["deff"], c1["n_eff"], _pp(c1["mde"])))
    say("    SUPPORT (plan of record, ruling 9): scored N %d in %d components, DEFF %.4f (Kish), n_eff %d, SE %.5f, MDE80 %s; %s"
        % (PLAN["C1"]["n"], PLAN["C1"]["components"], PLAN["C1"]["deff"], PLAN["C1"]["n_eff"], PLAN["C1"]["se"],
           _pp(PLAN["C1"]["mde"]), PLAN["C1"]["verdict"]))
    if t1:
        c1w = "VOID"; BR.hit("C1.VOID")
        say("  C1 -> VOID (BY TRIGGER T1: the placebo's interval lies wholly above 0); its interval is printed, not scored")
    elif G.as_bool(c1["lo"] > 0):
        c1w = "HELD"; BR.hit("C1.HELD"); say("  C1 -> HELD (the two-stage interval lies wholly above 0)")
    elif G.as_bool(c1["hi"] < 0):
        c1w = "FAILED"; BR.hit("C1.FAILED"); say("  C1 -> FAILED (the two-stage interval lies wholly below 0)")
    else:
        c1w = "UNDETERMINED"; BR.hit("C1.UNDETERMINED"); say("  C1 -> UNDETERMINED (the two-stage interval contains 0)")
    p = st["C2"]
    say("C2 interaction-only R of the union key profile over %d declared strata (>= %d key-complete EVAL items; listed above)"
        ": R = %.4f | DECIDING jackknife (re-halved) 95%% [%.4f, %.4f] | fixed beside [%.4f, %.4f] | halving SD %.4f |"
        " null p95 (19th of 20) %.4f, median %.4f" % (len(p["cells"]), st["floor"], p["R"], p["lo"], p["hi"], p["lo_fx"],
                                                      p["hi_fx"], p["sd"], p["null_p95"], p["null_median"]))
    say("    SUPPORT: jackknife SE %.4f, MDE80 %.3f (measured) | registered SE %.4f, MDE80 %.3f; %s; the jackknife over cells"
        " carries the clustering" % (p["se_re"], 2.80 * p["se_re"], PLAN["C2"]["se"], PLAN["C2"]["mde"], PLAN["C2"]["verdict"]))
    c2w = r_verdict(p)
    BR.hit("C2." + c2w)
    say("  C2 -> %s (HELD iff the lower bound exceeds the null p95; FAILED iff the upper bound is at or below it)" % c2w)
    # predictions
    say("PREDICTIONS (HELD iff the observed point lies in the registered interval, endpoints included; C1-derived"
        " predictions UNDETERMINED (BY TRIGGER) under T1):")
    lo, hi, _ = PRED["P1"]
    if t1:
        BR.hit("P1.UNDET_TRIGGER"); say("  P1 G in [%s, %s]: UNDETERMINED (BY TRIGGER T1)" % (_pp(lo), _pp(hi)))
    else:
        w = "HELD" if in_range(c1["point"], lo, hi) else "FAILED"; BR.hit("P1." + w)
        say("  P1 G predicted +3.00pp [%s, %s], observed %s -> %s (C1's realised class: %s; registered C1 HELD 0.80 /"
            " UNDETERMINED 0.18 / FAILED 0.02)" % (_pp(lo), _pp(hi), _pp(c1["point"]), w, c1w))
    sh = st["p2_share"]
    if t1:
        BR.hit("P2.UNDET_TRIGGER"); say("  P2 BBH carries >= 50%% of G: UNDETERMINED (BY TRIGGER T1)")
    elif sh is None:
        BR.hit("P2.UNDET_G"); say("  P2 BBH carries >= 50%% of G: UNDETERMINED (G <= 0: a share of a non-positive gain is"
                                   " undefined)")
    else:
        w = "HELD" if G.as_bool(sh >= 0.5) else "FAILED"; BR.hit("P2." + w)
        say("  P2 BBH share of G (%s) = %.3f -> %s (beside: contribution %.3f, leave-out %.3f)" % (st["p2_measure"], sh, w,
                                                                                               st["p2_both"][0], st["p2_both"][1]))
    lo, hi, _ = PRED["P3"]; lb = st["NON_BBH"]
    if t1:
        BR.hit("P3.UNDET_TRIGGER"); say("  P3 leave-BBH-out G: UNDETERMINED (BY TRIGGER T1)")
    else:
        w = "HELD" if in_range(lb["point"], lo, hi) else "FAILED"; BR.hit("P3." + w)
        say("  P3 leave-BBH-out G predicted +1.20pp [%s, %s], observed %s (two-stage [%s, %s]; DESCRIPTIVE) -> %s"
            % (_pp(lo), _pp(hi), _pp(lb["point"]), _pp(lb["lo"]), _pp(lb["hi"]), w))
    lo, hi, _ = PRED["P4"]
    w = "HELD" if in_range(p["R"], lo, hi) else "FAILED"; BR.hit("P4." + w)
    say("  P4 R(U) predicted 0.84 [%.2f, %.2f], observed %.4f -> %s (C2's realised class: %s; registered C2 HELD 0.85)"
        % (lo, hi, p["R"], w, c2w))
    BR.hit("P6.HALF_HELD")
    say("  P6 (this leg's half): C0-U HELD; P6 is HELD iff leg M's outcome also prints C0-M HELD (the registrar joins them)")
    lo, hi, _ = PRED["P7"]
    if t1:
        BR.hit("P7.UNDET_TRIGGER"); say("  P7 measured composite DEFF of C1: UNDETERMINED (BY TRIGGER T1)")
    else:
        w = "HELD" if in_range(c1["deff"], lo, hi) else "FAILED"; BR.hit("P7." + w)
        say("  P7 measured composite DEFF of C1 in [%.1f, %.1f]: observed %.3f -> %s" % (lo, hi, c1["deff"], w))
    say("FALSIFIERS:")
    if t1:
        BR.hit("F1.NOT_EVALUATED"); say("  F1 NOT EVALUATED (C1 VOID by T1): USE clause NOT licensed as content-closed (ruling 10)")
    elif c1w != "HELD":
        BR.hit("F1.FIRED")
        say("  F1 FIRED (C1 %s): the USE clause is WITHDRAWN as a content-closed claim; +2.92 / +3.09 stay id-disjoint-only"
            " history (not revised)" % c1w)
    else:
        BR.hit("F1.NOT_FIRED"); say("  F1 NOT FIRED (C1 HELD): the USE clause may be worded content-closed (a sensitivity"
                                     " and wording conversion, NOT a replication)")
    if c2w == "FAILED":
        BR.hit("F3.FIRED"); say("  F3 FIRED (C2 FAILED): the union key-profile licence (0.8537, 52 strata, id-disjoint only)"
                                 " does not carry to v2; " + STRATA_BESIDE)
    else:
        BR.hit("F3.NOT_FIRED"); say("  F3 NOT FIRED (C2 %s); %s" % (c2w, STRATA_BESIDE))
    return L, dict(C1=c1w, C2=c2w, T1=t1)


def verdict_lines_m(st):
    L = []
    say = L.append
    say("")
    say("=== VERDICTS (leg M) ===")
    say("C0 (validity, evaluated FIRST, before any v2 read): K12 interaction-only R on p2dca through this script's path = %s"
        " | registered %s -> HELD" % (st["c0"], REG["c0_k12"]))
    BR.hit("C0M.HELD")
    words = {}
    for tag in ("K12", "K37"):
        p = st[tag]
        say("C3 (%s, %d models) interaction-only R over %d declared categories (%d key-complete EVAL items): R = %.4f |"
            " DECIDING jackknife (re-halved) 95%% [%.4f, %.4f] | fixed beside [%.4f, %.4f] | halving SD %.4f | null p95 (19th"
            " of 20) %.4f, median %.4f | model-demeaned R beside %.4f" % (tag, st["n_models"][tag], len(p["cells"]),
                                                                           p["n_items"], p["R"], p["lo"], p["hi"], p["lo_fx"],
                                                                           p["hi_fx"], p["sd"], p["null_p95"], p["null_median"],
                                                                           p["R_model"]))
        pl = PLAN["C3_" + tag]
        say("    SUPPORT: jackknife SE %.4f, MDE80 %.3f (measured) | registered SE %.4f, MDE80 %.3f; %s" % (
            p["se_re"], 2.80 * p["se_re"], pl["se"], pl["mde"], pl["verdict"]))
        say("    DESCRIPTIVE comparator (roster, split, filing and question set all differ): recorded %s on p2dca (id-disjoint"
            " only, filed by the qwen3 tree bareq512_s42)" % (COMPARATORS_M["K12"] if tag == "K12" else "K46 " + COMPARATORS_M["K46"]))
        w = r_verdict(p); words[tag] = w
        BR.hit("C3." + w)
        say("  C3 %s -> %s" % (tag, w))
    say("PREDICTIONS:")
    for tag in ("K12", "K37"):
        lo, hi, c = PRED["P5_" + tag]
        w = "HELD" if in_range(st[tag]["R"], lo, hi) else "FAILED"; BR.hit("P5." + w)
        say("  P5 R(M, %s) predicted %.2f [%.2f, %.2f], observed %.4f -> %s (C3 realised: %s; registered C3 HELD 0.80)"
            % (tag, c, lo, hi, st[tag]["R"], w, words[tag]))
    BR.hit("P6.HALF_HELD")
    say("  P6 (this leg's half): C0-M HELD; P6 is HELD iff leg U's outcome also prints C0-U HELD (the registrar joins them)")
    say("FALSIFIERS:")
    for tag in ("K12", "K37"):
        if words[tag] == "FAILED":
            BR.hit("F2.FIRED")
            say("  F2 FIRED for %s (C3 FAILED): the key-R clause stays 'id-disjoint only, filed by a qwen3 tree' for this roster"
                " (K12 0.8665 / K46 0.8118 not revised)" % tag)
        else:
            BR.hit("F2.NOT_FIRED"); say("  F2 NOT FIRED for %s (C3 %s)" % (tag, words[tag]))
    return L, words


# ============================================================================================ C0 gates
def c0_compare_u(got):
    ok = (got["best"] == REG["c0_best"] and got["bs"] == REG["c0_bs"] and got["tdom"] == REG["c0_tdom"])
    if MUTANT == "c0_not_checked":
        ok = True
    if not ok:
        BR.hit("C0.REFUSED")
        raise SystemExit("[C0] leg U VOID (a READY defect, not an outcome): best single %s %s / TRUE s/d %s vs registered %s %s / %s"
                         % (got["best"], got["bs"], got["tdom"], REG["c0_best"], REG["c0_bs"], REG["c0_tdom"]))
    return got


def c0_compare_m(got):
    ok = got == REG["c0_k12"] or MUTANT == "c0_not_checked"
    if not ok:
        BR.hit("C0.REFUSED")
        raise SystemExit("[C0] leg M VOID (a READY defect, not an outcome): K12 %s vs registered %s" % (got, REG["c0_k12"]))
    return got


def c0_fit_generic(models, rows, say):
    """THIS script's fit on a generic (item, source, domain, is_eval, {model: 0/1}) table: -> best single name, acc strings.
    Used by the C0 gate (paeec) and by the selftest (fixture)."""
    K_tr = {r[0]: r[4] for r in rows if not r[3]}; K_ev = {r[0]: r[4] for r in rows if r[3]}
    tm = {r[0]: ("c:" + str(r[0]), r[1], r[2]) for r in rows if not r[3]}
    em = {r[0]: ("c:" + str(r[0]), r[1], r[2]) for r in rows if r[3]}
    D = build_ud(models, tm, em, K_tr, K_ev, {}, "item", None, REG["placebo_seed"])
    P = fit(D, train_full(D)); CE = correctness_E(D, P)
    return dict(best=D.models[P.gb], bs="%.4f" % CE[BS].mean(), tdom="%.4f" % CE[TDOM].mean(), n_train=D.n_train, n_eval=D.n_eval)


def c0_rcp_real(say):
    """Leg U's C0 on paeec: ROUTER-CLEAN-POLICY's own loader (pool guard, mode=ro&immutable=1, MATH-FIX overlay, roster 18)
    feeding THIS script's fit. No embedding is read: the TRUE arms need none, and every complete question is routed
    (asserted: the complete count equals the registered 21,606)."""
    import router_clean_policy as rcp
    cfg = rcp.real_cfg()
    rcp.wal_guard(cfg)
    rcp.guard_pool(cfg)
    con, _ = rcp.open_union(cfg)
    try:
        Q, models, Gk, pool = rcp.load_union(con, cfg)
    finally:
        con.close()
    qs = sorted(q for q in Q if len(Gk[q]) == len(models))
    n_ev = sum(1 for q in qs if q in pool)
    say("  C0-U inputs: %d complete questions (registered %d), EVAL %d (registered %d), TRAIN %d (registered %d), roster %d"
        % (len(qs), REG["c0_n_routed"], n_ev, REG["c0_n_eval"], len(qs) - n_ev, REG["c0_n_train"], len(models)))
    if len(qs) != REG["c0_n_routed"] or n_ev != REG["c0_n_eval"]:
        raise SystemExit("[C0] the paeec question set differs from the record's; leg U VOID")
    rows = [(q, Q[q][0], Q[q][1], q in pool, Gk[q]) for q in qs]
    return c0_fit_generic(models, rows, say)


def c0_pri_real(say):
    """Leg M's C0 on p2dca: PROFILE-RELIABILITY-INTERACTION's own loader (pins 9,142 / 12,394 / 2,811; the 14 anchors) feeding
    THIS script's key builder and profile wrapper (no null)."""
    D = pri.load_record(lambda s: say("  " + s))
    p = profile_leg(D["usable"], D["K"], D["models12"], "C0-K12", null=False)
    return "%.4f" % p["R"]


# ============================================================================================ modes
def header(cfg, leg, say):
    say("POOL %s (%s leg %s; %s; the first line of every mode)" % (cfg.pool_u if leg == "U" else cfg.pool_m, TEST_ID, leg,
                                                                    cfg.cv_u if leg == "U" else cfg.cv_m))
    say("%s | registration %s | ruling %s" % (TEST_ID, PROG, RULING))
    for f in (os.path.abspath(__file__), G.__file__, pri.__file__, pr.__file__):
        say("  " + G.identity_line(f))
    say("  MUTANT %r (must be None in every real mode)" % MUTANT)
    say("  WORDS (W1): v2 objects are 'content-closed under CK-CLOSE-v2 (residual disclosed: 1,142 P pairs in the 15-19-token"
        " band covering 422 EVAL items, 1,096 of the pairs BBH; O 20)'; comparators 'id-disjoint only (bound 2.03pp)'"
        " (p2dca / bareq512_s42) and '(bound 1.32pp)' (paeec).")
    say("  WORDS (W2): this leg 'contains no embedder' (declared cells; no tree or embedding read); never 'embedder-invariant'.")
    if leg == "U":
        say("  WORDS (W3): leg U is 'a content-closed sensitivity and wording conversion, NOT a replication' (same item family,"
            " same 18 models; twin removal already reads +3.28 [+2.12, +4.44], ledger L182).")
    say("  [P-FAM] (W4): this leg prints no judged number.")


def refuse_mutant():
    if MUTANT is not None:
        raise SystemExit("[MUTANT] %r is set: a real mode refuses" % MUTANT)


def side_tsv_counts(cfg, say):
    """Leg U's dry-run reads the EVAL STRUCTURE from the committed side export (no DB; B3 forbids opening eval_view before the
    policy file). Its table_sha is recomputed exactly as data_v2.ro.table_sha would not apply (a TSV); the header's
    table_sha and row count are compared with the manifest's."""
    rows = []
    head = None
    with open(cfg.side_tsv, encoding="utf-8") as f:
        for l in f:
            if l.startswith("#"):
                head = l.strip(); continue
            rows.append(l.rstrip("\n").rstrip("\r").split("\t"))
    cols, rows = rows[0], rows[1:]
    ok = head is not None and ("table_sha=%s" % SIDE_TSV_TABLE_SHA) in head and ("rows=%d" % len(rows)) in head
    say("  side export %s: %d rows | header table_sha / rows equal the manifest's (%s...): %s | sha256 (LF) %s"
        % (cfg.side_tsv, len(rows), SIDE_TSV_TABLE_SHA[:8], "YES" if ok else "NO",
           hashlib.sha256(open(cfg.side_tsv, "rb").read().replace(b"\r\n", b"\n")).hexdigest()[:16]))
    ix = {c: i for i, c in enumerate(cols)}
    ev_ = [r for r in rows if r[ix["side"]] == "EVAL" and cfg.cv_u in r[ix["corpora"]].split(",")]
    comps = defaultdict(set)
    for r in ev_:
        comps[r[ix["component_id"]]].add((r[ix["stratum_source"]], r[ix["stratum_domain"]]))
    st = Counter((r[ix["stratum_source"]], r[ix["stratum_domain"]]) for r in ev_)
    say("  EVAL (%s) from the side export: %d items (registered %d), %d components (registered %d), %d multi-stratum"
        " components, %d strata, %d strata with >= %d EVAL items (before coverage; the key-complete floor is applied in --run"
        " before the read)" % (cfg.cv_u, len(ev_), cfg.reg["n_eval_u"], len(comps), cfg.reg["comp_eval_u"],
                               sum(len(v) > 1 for v in comps.values()), len(st), sum(v >= cfg.reg["floor"] for v in st.values()),
                               cfg.reg["floor"]))
    for k in sorted(st):
        say("    %-50s %5d%s" % ("%s/%s" % k, st[k], "  (>= floor)" if st[k] >= cfg.reg["floor"] else ""))


def leg_u(cfg, say, dry):
    header(cfg, "U", say)
    for l in precondition_lines(cfg):
        say(l)
    tree = getattr(cfg, "tree", None)                            # RP12 G14 (None = the pre-RP12 leg U)
    xtrees = getattr(cfg, "xtrees", None)                        # RP13 UNION-AF-ROUTE (None = the G14 / pre-RP12 leg U)
    if tree is not None:
        say("  G14 TREE-CELL ARM (%s): tree cells %s; outputs %s, %s, %s" % (G14_REG, cfg.tree_desc, cfg.policy_path, cfg.out_u, cfg.mark_u))
    rule = cfg.pre.get("variant_rule")
    if not dry:
        miss = missing_preconditions(cfg)
        if miss:
            raise SystemExit("[PRECONDITION] --run refused: %s" % "; ".join(miss))
        for p in (cfg.policy_path, cfg.out_u, cfg.mark_u):
            if os.path.exists(p):
                raise SystemExit("[WRITE-ONCE] %s exists; refused before any read" % p)
        say("")
        say("--- C0 (validity; before any v2 read) ---")
        c0 = c0_compare_u(cfg.c0_u(say))
        ev("c0")
    residual, rdesc = load_residual(cfg) if cfg.pre.get("residual_file") else (None, "owed (precondition residual_file unset)")
    say("  residual list (the 422 EVAL items; W1 residual): %s" % rdesc)
    say("")
    say("--- TRAIN (gen_view, open_generation('policy_fit')) ---")
    tw, gsha = open_tw("gen", "policy_fit", cfg.gen_path, cfg.gen_sha, "gen_view", say)
    nc, ni, scope = pool_row(tw, cfg.pool_u, cfg.cv_u)
    say("  pool %s (scope %r): %d components (registered %d), %d items of %s (registered %d)" % (
        cfg.pool_u, scope, nc, cfg.reg["comp_eval_u"], ni, cfg.cv_u, cfg.reg["n_eval_u"]))
    if nc != cfg.reg["comp_eval_u"] or ni != cfg.reg["n_eval_u"]:
        raise SystemExit("[POOL] pool counts differ from the registration")
    regm = registry(tw, cfg.cv_u)
    models = sorted(m for m, s in regm.items() if s == "ACTIVE")
    say("  roster (%s ACTIVE, sorted = the argmax tie-break order): %d (registered %d); %s absent: %s" % (
        cfg.cv_u, len(models), cfg.reg["roster_u"], EXCLUDED, EXCLUDED not in models))
    if len(models) != cfg.reg["roster_u"] or EXCLUDED in models:
        raise SystemExit("[ROSTER] leg U roster check failed")
    say("  roster: " + ", ".join(models))
    for a, b in NAME_MATCHED:
        say("  DISCLOSURE: %s (leg U roster: %s) is name-matched to %s of the stage-1 37 (a name match only; protocol differs:"
            " OLL-v2 log-likelihood argmax vs TIGER generative CoT)" % (a, "present" if a in models else "ABSENT", b))
    sc = side_counts(tw)
    say("  gen_view side rows: TRAIN %d (registered %d), GATE %d (registered %d; REFUSED and COUNTED), EVAL %d (must be 0)"
        % (sc.get("TRAIN", 0), cfg.reg["n_train_side"], sc.get("GATE", 0), cfg.reg["n_gate"], sc.get("EVAL", 0)))
    if sc.get("EVAL", 0):
        raise SystemExit("[VIEW] the generation view carries EVAL rows")
    train_meta = side_items(tw, cfg.cv_u, "TRAIN" if MUTANT != "gate_side" else "GATE")
    if MUTANT == "gate_side":
        train_meta.update(side_items(tw, cfg.cv_u, "TRAIN"))
    comp_strata = component_strata(tw)
    cc_tr = cell_counts(tw, "response_lite", cfg.cv_u, models, train_meta)
    if tree is not None:                                         # READY_rp12_et C-5: printed by side
        say("  G14 tree cells: TRAIN items of %s in %s: %d (fitted as their own cell)" % (
            cfg.cv_u, NO_ROUTING_ROW, sum(1 for i in train_meta if tree.get(i) == NO_ROUTING_ROW)))
    no_resp = sum(1 for i in train_meta if i not in cc_tr)
    say("  TRAIN items of %s: %d; with no response of the roster (sentinel-like, COUNTED, not scored): %d; (model, item)"
        " cells with several responses: %d" % (cfg.cv_u, len(train_meta), no_resp, multi_cells(cc_tr, models)))
    for r_ in ((rule,) if rule else ("UNUSABLE_CELL", "AGREE_OR_UNUSABLE")):
        say("  structurally key-complete TRAIN items under %s: %d%s" % (r_, len(structurally_complete(cc_tr, models, r_)),
                                                                        "" if rule else " (rule unset: a count per candidate, no key read)"))
    if dry:
        tw.close()
        after_sha(cfg.gen_path, gsha, "gen_view", say)
        say("")
        say("--- EVAL structure (NOT opened in the dry-run: B3 forbids open_eval before the policy file) ---")
        if cfg.side_tsv:
            side_tsv_counts(cfg, say)
        else:
            say("  side export: none configured (fixture)")
        say("  eval_view pin: %s sha256-bytes pinned %s (hashed in --run before the open)" % (cfg.eval_path, cfg.eval_sha))
        say("  C0-U inputs (not run by --dry-run): ROUTER-CLEAN-POLICY's loader on %s" % _c0u_path())
        say("PLANNED: B = %d two-stage replicates (default_rng(%d)), placebo random.Random(%d), 40 halvings random.Random(7),"
            " null 20 tables (RandomState 1..20); outputs %s, %s, %s (write-once)" % (
                cfg.reg["B"], cfg.reg["seed"], cfg.reg["placebo_seed"], cfg.policy_path, cfg.out_u, cfg.mark_u))
        say("DRY-RUN: no key column was selected (tripwire statements: %d, all key-free); no statistic printed." % len(tw.log))
        return None
    tw.unseal("policy_fit on TRAIN (B3 step 1: the TRAIN policy is fitted before the EVAL view is opened)")
    K_tr, kst_tr = read_key(tw, "response_lite", cfg.cv_u, models, train_meta, True, rule)
    tw.close()
    if MUTANT == "b3_reorder":                                   # SELFTEST-ONLY defect: EVAL opened before the policy file
        open_tw("eval", "route", cfg.eval_path, cfg.eval_sha, "eval_view", lambda s: None)[0].close()
    ok_g = after_sha(cfg.gen_path, gsha, "gen_view", say)
    say("  TRAIN key: cells single %d, multi %d (unusable %d, agreeing used %d); MATH-FIX overlay rows %d, value changed %d;"
        " key rows fetched %d (TRAIN items x roster, filtered in SQL)"
        % (kst_tr["single"], kst_tr["multi"], kst_tr["multi_unusable"], kst_tr["multi_agree_used"], kst_tr["overlay_rows"],
           kst_tr["overlay_changed"], kst_tr["key_rows_fetched"]))
    # the point policy on TRAIN alone, written BEFORE the EVAL view opens (B3)
    Dtr = build_ud(models, train_meta, {}, K_tr, {}, comp_strata, cfg.pre["train_unit"], None, cfg.reg["placebo_seed"], tree=tree, xtrees=xtrees)
    P_tr = fit(Dtr, train_full(Dtr))
    pol = policy_json(Dtr, P_tr, cfg, gsha)
    txt = json.dumps(pol, sort_keys=True, indent=1) + "\n"
    G.write_once(cfg.policy_path, txt)
    ev("policy_written")
    psha = hashlib.sha256(txt.encode("utf-8")).hexdigest()
    say("  B3 FROZEN TRAIN POLICY written write-once: %s | sha256 %s | TRAIN items scored %d | best single %s"
        % (cfg.policy_path, psha, Dtr.n_train, pol["best_single"]))
    if getattr(cfg, "pre_eval", None) is not None:              # RP13 C-4: a TRAIN-only check BEFORE the EVAL view opens
        cfg.pre_eval(cfg, pol, psha, say)
    # --- EVAL ---
    say("")
    say("--- EVAL (eval_view, open_eval('route'); opened only now, after the policy file) ---")
    b3_guard(cfg)
    tw, esha = open_tw("eval", "route", cfg.eval_path, cfg.eval_sha, "eval_view", say)
    nc2, ni2, _ = pool_row(tw, cfg.pool_u, cfg.cv_u)
    if (nc2, ni2) != (nc, ni):
        raise SystemExit("[POOL] eval_view pool row differs from gen_view's")
    eval_meta = side_items(tw, cfg.cv_u, "EVAL")
    comps = set(v[0] for v in eval_meta.values())
    say("  EVAL items of %s: %d (registered %d) in %d components (registered %d)" % (
        cfg.cv_u, len(eval_meta), cfg.reg["n_eval_u"], len(comps), cfg.reg["comp_eval_u"]))
    if len(eval_meta) != cfg.reg["n_eval_u"] or len(comps) != cfg.reg["comp_eval_u"]:
        raise SystemExit("[POOL] EVAL item / component counts differ from the registration")
    regE = registry(tw, cfg.cv_u)
    if sorted(m for m, s in regE.items() if s == "ACTIVE") != models:
        raise SystemExit("[ROSTER] eval_view's roster differs from gen_view's")
    cc_ev = cell_counts(tw, "response", cfg.cv_u, models, eval_meta)
    pre_ok = structurally_complete(cc_ev, models, rule)
    strat_n = Counter((eval_meta[i][1], eval_meta[i][2]) for i in pre_ok)
    floor = cfg.reg["floor"]
    admitted = sorted(k for k, n in strat_n.items() if n >= floor or MUTANT == "floor_off")
    say("  EVAL items with no response of the roster (sentinels, COUNTED, not scored): %d; multi-response cells: %d;"
        " structurally key-complete under %s: %d" % (sum(1 for i in eval_meta if i not in cc_ev), multi_cells(cc_ev, models),
                                                     rule, len(pre_ok)))
    if residual is not None:
        say("  residual items (the 422) among this pool's EVAL items: %d" % len(residual & set(eval_meta)))
    if tree is not None:
        # READY_rp12_et C-5: an EVAL item of the scoring set without B0's routing row has no tree cell of record; refused
        # here, BEFORE the B1 marker and the EVAL key read (a failed precondition, not an outcome)
        norow = sorted(i for i in pre_ok if tree.get(i) == NO_ROUTING_ROW)
        say("  G14 tree cells: EVAL items of the scoring set in %s: %d (must be 0)" % (NO_ROUTING_ROW, len(norow)))
        if norow:
            raise SystemExit("[G14-NOROW] %d EVAL item(s) of the scoring set have no routing row in B0's readout (first %s): the"
                             " tree cell is undefined for them; refused before the EVAL key read" % (len(norow), norow[:3]))
        for nm in sorted(xtrees or {}):                          # RP13: the same refusal for every extra arm
            norow_x = sorted(i for i in pre_ok if xtrees[nm].get(i) == NO_ROUTING_ROW)
            say("  RP13 arm %s: EVAL items of the scoring set in %s: %d (must be 0)" % (nm, NO_ROUTING_ROW, len(norow_x)))
            if norow_x:
                raise SystemExit("[G14-NOROW] arm %s: %d EVAL item(s) of the scoring set have no cell (first %s); refused before"
                                 " the EVAL key read" % (nm, len(norow_x), norow_x[:3]))
    say("  C2 CELL LIST (fixed BEFORE the key is read; key-complete count >= %d): %d strata" % (floor, len(admitted)))
    for k in sorted(strat_n):
        say("    %-50s %5d  %s" % ("%s/%s" % k, strat_n[k], "ADMITTED" if k in admitted else "below the floor"))
    if MUTANT != "marker_off":
        G.read_marker(cfg.mark_u, "V2-DECLARED-CELLS leg U: the EVAL key read started (B1). policy sha256 %s" % psha)
    tw.unseal("route read of EVAL after the B3 policy file sha256 %s" % psha)
    K_ev, kst_ev = read_key(tw, "response", cfg.cv_u, models, eval_meta, True, rule)
    tw.close()
    ok_e = after_sha(cfg.eval_path, esha, "eval_view", say)
    say("  EVAL key: cells single %d, multi %d (unusable %d, agreeing used %d); MATH-FIX overlay rows %d, value changed %d;"
        " key rows fetched %d (EVAL items x roster, filtered in SQL)"
        % (kst_ev["single"], kst_ev["multi"], kst_ev["multi_unusable"], kst_ev["multi_agree_used"], kst_ev["overlay_rows"],
           kst_ev["overlay_changed"], kst_ev["key_rows_fetched"]))
    # full arrays; the point policy must equal the file's
    D = build_ud(models, train_meta, eval_meta, K_tr, K_ev, comp_strata, cfg.pre["train_unit"], residual, cfg.reg["placebo_seed"], tree=tree, xtrees=xtrees)
    D.fit_asserts = 0
    say("  scored: TRAIN %d, EVAL %d key-complete items (of %d); EVAL units %d components; TRAIN units %d (%s)" % (
        D.n_train, D.n_eval, len(eval_meta), D.eval_units["n_units"], D.train_units["n_units"], cfg.pre["train_unit"]))
    bt = run_boot(D, cfg.reg["B"], cfg.reg["seed"], hook=cfg.hook)
    nn = lambda d: {k: v for k, v in d.items() if v is not None}
    if nn(policy_json(D, bt["P0"], cfg, gsha)["true_source_domain"]) != nn(pol["true_source_domain"]) or D.models[bt["P0"].gb] != pol["best_single"]:
        raise SystemExit("[B3] the point policy re-fitted beside EVAL differs from the frozen file")
    if tree is not None and nn(policy_json(D, bt["P0"], cfg, gsha)["tree_cell"]) != nn(pol["tree_cell"]):
        raise SystemExit("[B3] the tree-cell policy re-fitted beside EVAL differs from the frozen file")
    if xtrees and {k: nn(v) for k, v in policy_json(D, bt["P0"], cfg, gsha)["xtree_cell"].items()} !=             {k: nn(v) for k, v in pol["xtree_cell"].items()}:
        raise SystemExit("[B3] an RP13 extra arm's policy re-fitted beside EVAL differs from the frozen file")
    want = cfg.reg["B"] + 1
    say("fit-call TRAIN-subset checks executed: %d (must equal B + 1 = %d)" % (D.fit_asserts, want))
    if D.fit_asserts != want:
        raise SystemExit("[G3] %d fit checks executed, not %d" % (D.fit_asserts, want))
    c1 = contrast(bt, D, "ALL", TDOM, BS); cp = contrast(bt, D, "ALL", PLAC, BS)
    gate_g4(c1, cp)
    if tree is not None:                                         # RP12 G14: its own readout; C2 is not re-read here
        return (getattr(cfg, "tail", None) or g14_tail)(cfg, say, D, bt, c1, pol, ok_g and ok_e, kst_tr, kst_ev, residual, K_ev)
    st = dict(C1=c1, PLAC=cp, c0=c0, floor=floor, p2_measure=cfg.pre["p2_measure"])
    st["NON_BBH"] = contrast(bt, D, "NON_BBH", TDOM, BS)
    subs = [n for n, _ in D.subsets]
    say("")
    say("ARM ACCURACIES on EVAL (point | two-stage SE | i.i.d. SE), n = %d:" % D.n_eval)
    for a in range(5):
        say("    %-20s %.4f  %.5f  %.5f" % (ARMS[a], bt["point"][0, a], math.sqrt(_var(bt["two"][:, 0, a])), math.sqrt(_var(bt["iid"][:, 0, a]))))
    say("PRINTED BESIDE (declared; deciding nothing): G on subsets, policy fitted on all TRAIN (reading (d)):")
    for s in subs:
        c = contrast(bt, D, s, TDOM, BS)
        say("    %-16s n %5d  G %s  two-stage [%s, %s]  i.i.d. SE %.5f" % (s, c["n"], _pp(c["point"]), _pp(c["lo"]), _pp(c["hi"]), c["se_iid"]))
    oc = contrast(bt, D, "ALL", ORACLE, BS)
    say("    oracle - best single %s (descriptive)" % _pp(oc["point"]))
    nb = int(D.subsets[subs.index("SRC:BBH")][1].sum()) if "SRC:BBH" in subs else 0
    g_bbh = contrast(bt, D, "SRC:BBH", TDOM, BS)["point"] if nb else 0.0
    contrib = (nb / D.n_eval) * g_bbh / c1["point"] if c1["point"] > 0 else None
    leave = 1.0 - st["NON_BBH"]["point"] / c1["point"] if c1["point"] > 0 else None
    st["p2_both"] = (contrib if contrib is not None else float("nan"), leave if leave is not None else float("nan"))
    st["p2_share"] = None if c1["point"] <= 0 else (contrib if cfg.pre["p2_measure"] == "contribution" else leave)
    # C2
    cells = {"%s/%s" % k: sorted(i for i in D.items if i in eval_meta and (eval_meta[i][1], eval_meta[i][2]) == k and i in K_ev
                                 and all(m in K_ev[i] for m in models)) for k in admitted}
    say("  C2 post-read key-complete counts: " + ", ".join("%s %d" % (k, len(v)) for k, v in cells.items()))
    st["C2"] = profile_leg(cells, K_ev, models, "U-C2")
    lines, words = verdict_lines_u(st)
    for l in lines:
        say(l)
    return dict(st=st, words=words, ok_sha=ok_g and ok_e, D=D, bt=bt, policy=pol, cells=cells, kst=dict(train=kst_tr, eval=kst_ev),
                residual=residual, K_ev=K_ev)


def g14_verdict(g):
    """HELD iff lower(G_tree) > 0; FAILED iff upper(G_tree) <= 0; UNDETERMINED iff the interval covers 0."""
    if g["lo"] > 0:
        return "HELD"
    if g["hi"] <= 0:
        return "FAILED"
    return "UNDETERMINED"


def verdict_lines_g14(st):
    L = []
    say = L.append
    c1, g, m = st["C1"], st["G"], st["M"]
    say("")
    say("=== G14 (policy consequence; %s) ===" % G14_REG)
    say("IDENTITY PRECONDITION: the declared arm C1 = acc(TRUE (source, domain)) - acc(best single) = %s [%s, %s] (two-stage);"
        " V2-DECLARED-CELLS C1 of record %s [%s, %s] -> REPRODUCED to the printed digits" % (
            (_pp(c1["point"]), _pp(c1["lo"]), _pp(c1["hi"])) + tuple(st["identity"])))
    BR.hit("G14.IDENTITY_OK")
    say("G_tree = acc(%s) - acc(best single) = %s | two-stage [%s, %s] (point +- 1.96 SE_2stage, the reader's deciding form) |"
        " percentile [%s, %s] | n %d, SE_2stage %.5f, i.i.d. SE %.5f, DEFF %.3f, n_eff %.0f, MDE80 %s (registered SE 0.00618,"
        " DEFF 1.269, n_eff 4,656, MDE80 +1.73pp)" % (ARM_TREE, _pp(g["point"]), _pp(g["lo"]), _pp(g["hi"]), _pp(g["pct"][0]),
                                                     _pp(g["pct"][1]), g["n"], g["se2"], g["se_iid"], g["deff"], g["n_eff"], _pp(g["mde"])))
    v = g14_verdict(g)
    if v == "HELD":
        BR.hit("G14.HELD"); say("  G14 -> HELD (the interval lies wholly above 0)")
    elif v == "FAILED":
        BR.hit("G14.FAILED"); say("  G14 -> FAILED (the interval's upper bound is at or below 0)")
    else:
        BR.hit("G14.UNDETERMINED"); say("  G14 -> UNDETERMINED (the interval covers 0)")
    say("M = G_tree - G_declared = %s | two-stage [%s, %s] | percentile [%s, %s] | DESCRIPTIVE-ONLY (Support (f): the prediction"
        " -0.2pp is inside MDE80 1.11pp); no parity is written (no TOST registered)" % (_pp(m["point"]), _pp(m["lo"]), _pp(m["hi"]),
                                                                                      _pp(m["pct"][0]), _pp(m["pct"][1])))
    for key, label, x in (("G", "P5 G_tree = +2.5pp [+1.3, +3.7]", g["point"]), ("M", "P5 M = -0.2pp [-1.0, +0.6]", m["point"])):
        ok = in_range(x, *P5_G14[key])
        BR.hit("P5T.HELD" if ok else "P5T.FAILED")
        say("%s: observed %s -> %s" % (label, _pp(x), "HELD" if ok else "FAILED"))
    say("P5 'G14 HELD' (probability 0.85): observed %s" % v)
    say("WORDS: arena cells stay DECLARED (S1); the tree cell is a policy arm read from B0's flatLeaf filing, not an arena cell;"
        " key-scored end to end, no judge verdict (no wrong(established) count, no convention A / B arises)")
    return L, dict(G14=v)


def g14_tail(cfg, say, D, bt, c1, pol, ok_sha, kst_tr, kst_ev, residual, K_ev):
    ident = tuple(getattr(cfg, "g14_identity", G14_IDENTITY))
    got = (_pp(c1["point"]), _pp(c1["lo"]), _pp(c1["hi"]))
    if got != ident:
        raise SystemExit("[G14-IDENTITY] the declared arm prints C1 = %s [%s, %s], not V2-DECLARED-CELLS C1 of record %s [%s, %s]:"
                         " a failed precondition, no outcome written" % (got + ident))
    say("")
    say("ARM ACCURACIES on EVAL (point | two-stage SE | i.i.d. SE), n = %d:" % D.n_eval)
    for a, name in enumerate(ARMS + (ARM_TREE,)):
        say("    %-24s %.4f  %.5f  %.5f" % (name, bt["point"][0, a], math.sqrt(_var(bt["two"][:, 0, a])), math.sqrt(_var(bt["iid"][:, 0, a]))))
    say("  tree cells over the scored items: %d distinct (TRAIN %d items, EVAL %d items)" % (len(D.tree_keys), D.n_train, D.n_eval))
    st = dict(C1=c1, G=contrast(bt, D, "ALL", TREE, BS), M=contrast(bt, D, "ALL", TREE, TDOM), identity=ident)
    lines, words = verdict_lines_g14(st)
    for l in lines:
        say(l)
    return dict(st=st, words=words, ok_sha=ok_sha, D=D, bt=bt, policy=pol, cells={}, kst=dict(train=kst_tr, eval=kst_ev),
                residual=residual, K_ev=K_ev)


def _c0u_path():
    try:
        import pool_guard
        return pool_guard.db_path(pool_guard.UNION_POOL)
    except Exception as e:                                     # descriptive only (dry-run)
        return "unresolved (%s)" % e


def leg_m(cfg, say, dry):
    header(cfg, "M", say)
    for l in precondition_lines(cfg):
        say(l)
    rule = cfg.pre.get("variant_rule")
    if not dry:
        miss = missing_preconditions(cfg)
        if miss:
            raise SystemExit("[PRECONDITION] --run refused: %s" % "; ".join(miss))
        for p in (cfg.out_m, cfg.mark_m):
            if os.path.exists(p):
                raise SystemExit("[WRITE-ONCE] %s exists; refused before any read" % p)
        say("")
        say("--- C0 (validity; before any v2 read) ---")
        c0 = c0_compare_m(cfg.c0_m(say))
        ev("c0")
    residual, rdesc = load_residual(cfg) if cfg.pre.get("residual_file") else (None, "owed (precondition residual_file unset)")
    say("  residual list (the 422 EVAL items): %s" % rdesc)
    say("")
    say("--- EVAL (eval_view, open_eval('arena')) ---")
    tw, esha = open_tw("eval", "arena", cfg.eval_path, cfg.eval_sha, "eval_view", say)
    nc, ni, scope = pool_row(tw, cfg.pool_m, cfg.cv_m)
    say("  pool %s (scope %r): %d components (registered %d), %d items (registered %d)" % (
        cfg.pool_m, scope, nc, cfg.reg["comp_eval_m"], ni, cfg.reg["n_eval_m"]))
    if nc != cfg.reg["comp_eval_m"] or ni != cfg.reg["n_eval_m"]:
        raise SystemExit("[POOL] pool counts differ from the registration")
    regm = registry(tw, cfg.cv_m)
    k37, quar, sha = k37_roster(regm, cfg)
    k12 = list(cfg.k12)
    say("  K12 = rubric_p8.ARENA12 (%d): %s" % (len(k12), ", ".join(k12)))
    say("  K37 = ACTIVE - the 9 dropped (%d); sha256-text %s (registered %s); quarantined %s; %s absent from both: %s" % (
        len(k37), sha, cfg.k37_sha, quar, EXCLUDED, EXCLUDED not in k37 and EXCLUDED not in k12))
    items = side_items(tw, cfg.cv_m, "EVAL")
    comps = set(v[0] for v in items.values())
    srcs = Counter(v[1] for v in items.values())
    say("  EVAL items of %s: %d (registered %d), %d components (registered %d); stratum sources %s" % (
        cfg.cv_m, len(items), cfg.reg["n_eval_m"], len(comps), cfg.reg["comp_eval_m"], dict(srcs)))
    if len(items) != cfg.reg["n_eval_m"] or len(comps) != cfg.reg["comp_eval_m"] or set(srcs) != {"MMLU_PRO"}:
        raise SystemExit("[POOL] leg M EVAL items differ from the registration")
    cats = Counter(v[2] for v in items.values())
    say("  declared categories (%d; registered %d): %s" % (len(cats), cfg.reg["n_categories_m"],
                                                           ", ".join("%s %d" % kv for kv in sorted(cats.items()))))
    if residual is not None:
        say("  residual items (the 422) inside %s: %d (the steward's count)" % (cfg.pool_m, len(residual & set(items))))
    cc = cell_counts(tw, "response", cfg.cv_m, k37, items)
    say("  (model, item) cells with several responses over K37: %d (over K12: %d); items with no K37 response: %d" % (
        multi_cells(cc, k37), multi_cells(cc, k12), sum(1 for i in items if i not in cc)))
    if not rule:
        for r_ in ("UNUSABLE_CELL", "AGREE_OR_UNUSABLE"):
            say("  structurally key-complete EVAL items under %s (rule unset: a count per candidate, no key read): K12 %d, K37 %d"
                % (r_, len(structurally_complete(cc, k12, r_)), len(structurally_complete(cc, k37, r_))))
    admitted = {}
    for tag, models in (("K12", k12), ("K37", k37)):
        ok = structurally_complete(cc, models, rule or "UNUSABLE_CELL")
        n = Counter(items[i][2] for i in ok)
        adm = sorted(c for c in n if (n[c] >= cfg.reg["floor"] or MUTANT == "floor_off")
                     and (c not in cfg.reg["excluded_categories"] or MUTANT == "history_kept"))
        admitted[tag] = adm
        say("  %s CELL LIST (fixed BEFORE the key is read; key-complete >= %d under %s%s; history excluded BY NAME): %d categories"
            % (tag, cfg.reg["floor"], rule or "UNUSABLE_CELL", "" if rule else " [rule unset: dry-run count only]", len(adm)))
        for c in sorted(cats):
            say("    %-20s EVAL %4d | key-complete %4d | %s" % (c, cats[c], n.get(c, 0), "ADMITTED" if c in adm else (
                "EXCLUDED BY NAME" if c in cfg.reg["excluded_categories"] else "below the floor")))
    if dry:
        if MUTANT == "dry_reads_key":                          # SELFTEST-ONLY defect: a dry-run that reads the key
            tw.execute("SELECT is_correct FROM response LIMIT 1")
        tw.close()
        after_sha(cfg.eval_path, esha, "eval_view", say)
        say("  C0-M inputs (not run by --dry-run): PROFILE-RELIABILITY-INTERACTION's loader (x12 %s; x20; eval DB; bareq512_s42)"
            % os.path.join("experiment_results", "x12_crossdomain"))
        say("PLANNED: 40 halvings random.Random(7), LOCO jackknife re-halved (deciding) and fixed, null 20 tables (RandomState"
            " 1..20); outputs %s, %s (write-once)" % (cfg.out_m, cfg.mark_m))
        say("DRY-RUN: no key column was selected (tripwire statements: %d, all key-free); no statistic printed." % len(tw.log))
        return None
    if MUTANT != "marker_off":
        G.read_marker(cfg.mark_m, "V2-DECLARED-CELLS leg M: the EVAL key read started (B1)")
    tw.unseal("arena read of EVAL (leg M; preconditions set; B1 marker written)")
    K, kst = read_key(tw, "response", cfg.cv_m, k37, items, False, rule)
    tw.close()
    ok_e = after_sha(cfg.eval_path, esha, "eval_view", say)
    say("  key: cells single %d, multi %d (unusable %d, agreeing used %d); key rows fetched %d (EVAL items x K37, filtered in SQL)"
        % (kst["single"], kst["multi"], kst["multi_unusable"], kst["multi_agree_used"], kst["key_rows_fetched"]))
    st = dict(c0=c0, n_models={"K12": len(k12), "K37": len(k37)})
    for tag, models in (("K12", k12), ("K37", k37)):
        cells = {c: sorted(i for i in items if items[i][2] == c and i in K and all(m in K[i] for m in models))
                 for c in admitted[tag]}
        say("  %s post-read key-complete counts: %s" % (tag, ", ".join("%s %d" % (c, len(v)) for c, v in cells.items())))
        st[tag] = profile_leg(cells, K, models, "M-" + tag)
    lines, words = verdict_lines_m(st)
    for l in lines:
        say(l)
    return dict(st=st, words=words, ok_sha=ok_e, admitted=admitted, kst=kst)


def b3_guard(cfg):
    """B3: open_eval('route') is refused while the frozen TRAIN policy file is absent."""
    if not os.path.exists(cfg.policy_path):
        BR.hit("B3.REFUSED")
        raise SystemExit("[B3] the frozen TRAIN policy file %s is absent: open_eval('route') refused" % cfg.policy_path)


def write_outcome(path, text):
    if MUTANT == "write_w":                                     # SELFTEST-ONLY defect: an overwriting open
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return path
    return G.write_once(path, text)


def mode(cfg, leg, dry):
    lines = []
    def say(s):
        lines.append(s); print(s, flush=True)
    res = (leg_u if leg == "U" else leg_m)(cfg, say, dry)
    if dry or res is None:
        return res
    out = cfg.out_u if leg == "U" else cfg.out_m
    if not res["ok_sha"]:
        G.write_once(out.replace(".txt", "_VOID.txt"), "\n".join(lines) + "\n[VOID] a view's sha differs after the read\n")
        raise SystemExit("[PIN] a view's sha256 differs after the read: outcome written to _VOID, not to the file of record")
    write_outcome(out, "\n".join(lines) + "\n")
    print("OUTCOME written write-once: %s" % out)
    return res


# ============================================================================================ selftest
def _mk_view(path, kind, sides, spec):
    """A sealed synthetic view with the column names of data_v2 (views._view_ddl + split DDL)."""
    c = dv2ro.create_new(path)
    c.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    for k, v in (("view_kind", kind), ("of_record", "SELFTEST FIXTURE"), ("seed", "SELFTEST")):
        c.execute("INSERT INTO meta VALUES (?,?)", (k, v))
    c.execute("CREATE TABLE side (item_id TEXT PRIMARY KEY, component_id TEXT, side TEXT, stratum_source TEXT,"
              " stratum_domain TEXT, corpora TEXT)")
    c.execute("CREATE TABLE component (component_id TEXT PRIMARY KEY, n_items INTEGER, stratum_source TEXT, stratum_domain TEXT,"
              " n_strata_voted INTEGER, rank_hex TEXT, side TEXT)")
    c.execute("CREATE TABLE pool (pool_id TEXT PRIMARY KEY, scope TEXT, n_components INTEGER, n_items_by_scope TEXT)")
    c.execute("CREATE TABLE item (corpus_version TEXT, item_id TEXT, stem_key TEXT, PRIMARY KEY (corpus_version, item_id))")
    c.execute("CREATE TABLE model_registry (corpus_version TEXT, model TEXT, status TEXT, reason TEXT, n_responses INTEGER,"
              " PRIMARY KEY (corpus_version, model))")
    rt = "response_lite" if kind == "gen" else "response"
    c.execute("CREATE TABLE %s (corpus_version TEXT, response_id TEXT, model TEXT, legacy_qid INTEGER, source TEXT, seen_ck TEXT,"
              " item_id TEXT, options_ordered_sha TEXT, gt_raw TEXT, answer_text TEXT, pred TEXT, is_correct INTEGER,"
              " is_correct_mathfix INTEGER, category TEXT, output_sha256 TEXT%s, PRIMARY KEY (corpus_version, response_id))"
              % (rt, ", output_zlib BLOB" if kind == "eval" else ""))
    c.execute("CREATE TABLE variant (corpus_version TEXT, variant_id TEXT, item_id TEXT, PRIMARY KEY (corpus_version, variant_id))")
    c.execute("CREATE TABLE reference (corpus_version TEXT, variant_id TEXT, vintage TEXT, source_key TEXT, item_id TEXT,"
              " correct INTEGER, PRIMARY KEY (corpus_version, variant_id, vintage, source_key))")
    for p in spec["pools"]:
        c.execute("INSERT INTO pool VALUES (?,?,?,?)", p)
    for cv, m, s in spec["registry"]:
        c.execute("INSERT INTO model_registry VALUES (?,?,?,?,?)", (cv, m, s, None, 0))
    comps = {}
    for it in spec["items"]:
        if it["side"] not in sides:
            continue
        c.execute("INSERT INTO side VALUES (?,?,?,?,?,?)", (it["id"], it["comp"], it["side"], it["src"], it["dom"], ",".join(it["cvs"])))
        comps.setdefault(it["comp"], (it["src"], it["dom"], it["side"], 0))
        s0 = comps[it["comp"]]; comps[it["comp"]] = (s0[0], s0[1], s0[2], s0[3] + 1)
        for cv in it["cvs"]:
            c.execute("INSERT INTO item VALUES (?,?,?)", (cv, it["id"], it["id"]))
            c.execute("INSERT INTO variant VALUES (?,?,?)", (cv, "v" + it["id"], it["id"]))
    for cid, (s, d, sd, n) in comps.items():
        c.execute("INSERT INTO component VALUES (?,?,?,?,?,?,?)", (cid, n, s, d, 1, "00", sd))
    k = 0
    for r in spec["responses"]:
        if r["side"] not in sides:
            continue
        k += 1
        vals = (r["cv"], "x%d" % k, r["model"], k, r["src"], "v" + r["item"], r["item"], "o", "gt", "at", "p", r["c"], r["mf"],
                "cat", "sha")
        if kind == "eval":
            vals = vals + (b"z",)
        c.execute("INSERT INTO %s VALUES (%s)" % (rt, ",".join("?" * len(vals))), vals)
    c.commit()
    return dv2ro.seal(c, path, "selftest %s view" % kind)["sha256_bytes"]


def _fixture_spec(seed=11, n_models_u=9, n_models_m=14, floor=50):
    rs = np.random.RandomState(seed)
    mu = ["u%02d" % i for i in range(n_models_u)]
    mm = ["k%02d" % i for i in range(n_models_m)]
    k12 = mm[:9]
    dropped = ("zz_drop1", "zz_drop2")
    registry = [("mc6", m, "ACTIVE") for m in mu] + [("mmlu", m, "ACTIVE") for m in mm] + \
               [("mmlu", d, "ACTIVE") for d in dropped] + [("mmlu", EXCLUDED, "QUARANTINED")]
    items, responses = [], []
    au = rs.normal(0, 0.5, n_models_u)
    am = rs.normal(0, 0.5, n_models_m)
    # leg U strata: 7 strata with EVAL >= floor + one small stratum; interaction strong so the policy gains
    strata_u = [("BBH", "b%d" % j) for j in range(3)] + [("MMLU_PRO", "x%d" % j) for j in range(3)] + [("MATH", "z0"), ("MATH", "tiny")]
    inter_u = rs.normal(0, 1.2, (len(strata_u), n_models_u))
    nid = [0]
    def new_id():
        nid[0] += 1
        return "i:%05d" % nid[0]
    for si, (src, dom) in enumerate(strata_u):
        for side, n in (("TRAIN", 150), ("EVAL", 72 if dom != "tiny" else 20), ("GATE", 10)):
            j = 0
            while j < n:
                twins = 2 if (rs.rand() < 0.2 and j + 1 < n) else 1
                cid = "c:%s" % new_id()
                for t in range(twins):
                    iid = new_id()
                    items.append(dict(id=iid, comp=cid, side=side, src=src, dom=dom, cvs=["mc6"]))
                    d = rs.normal(0, 0.5)
                    for mi, m in enumerate(mu):
                        p = 1 / (1 + np.exp(-(au[mi] + inter_u[si, mi] - d)))
                        cval = int(rs.rand() < p)
                        mf = None
                        if src == "MATH" and rs.rand() < 0.1:
                            mf = 1 - cval
                        responses.append(dict(cv="mc6", model=m, item=iid, side=side, src=src, c=cval, mf=mf))
                        if rs.rand() < 0.01:                                         # a multi-response cell (twin legacy row)
                            responses.append(dict(cv="mc6", model=m, item=iid, side=side, src=src, c=1 - cval, mf=None))
                j += twins
    # an EVAL sentinel (no response)
    items.append(dict(id=new_id(), comp="c:sentinel", side="EVAL", src="MATH", dom="z0", cvs=["mc6"]))
    # leg M: 7 categories, history small
    cats = ["biology", "chemistry", "economics", "history", "law", "math", "physics", "psychology"]
    inter_m = rs.normal(0, 1.0, (len(cats), n_models_m))
    for ci, cat in enumerate(cats):
        n = 70
        for j in range(n):
            iid = new_id()
            items.append(dict(id=iid, comp="c:" + iid, side="EVAL", src="MMLU_PRO", dom=cat, cvs=["mmlu"]))
            d = rs.normal(0, 0.5)
            for mi, m in enumerate(mm + list(dropped)):
                a = am[mi] if mi < n_models_m else 0.0
                it = inter_m[ci, mi] if mi < n_models_m else 0.0
                cval = int(rs.rand() < 1 / (1 + np.exp(-(a + it - d))))
                responses.append(dict(cv="mmlu", model=m, item=iid, side="EVAL", src="MMLU_PRO", c=cval, mf=None))
                if mi == 0 and j == 0:
                    responses.append(dict(cv="mmlu", model=m, item=iid, side="EVAL", src="MMLU_PRO", c=cval, mf=None))
    ev_u = [it for it in items if it["side"] == "EVAL" and "mc6" in it["cvs"]]
    ev_m = [it for it in items if it["side"] == "EVAL" and "mmlu" in it["cvs"]]
    pools = [("pv_u", "all corpora + mc6", len(set(i["comp"] for i in ev_u)), json.dumps({"all corpora": len(ev_u), "mc6": len(ev_u)})),
             ("pv_m", "mmlu", len(set(i["comp"] for i in ev_m)), json.dumps({"mmlu": len(ev_m)}))]
    k37 = sorted(mm)
    return dict(items=items, responses=responses, registry=registry, pools=pools, models_u=mu, k12=tuple(sorted(k12)),
                k37=k37, dropped=dropped, floor=floor,
                reg=dict(REG, n_train_side=sum(1 for i in items if i["side"] == "TRAIN"),
                         n_gate=sum(1 for i in items if i["side"] == "GATE"), n_eval_u=len(ev_u),
                         comp_eval_u=len(set(i["comp"] for i in ev_u)), n_eval_m=len(ev_m),
                         comp_eval_m=len(set(i["comp"] for i in ev_m)), roster_u=n_models_u, floor=floor,
                         n_categories_m=len(cats), B=60, registry_m_total=n_models_m + len(dropped) + 1,
                         registry_m_active=n_models_m + len(dropped), roster_k37=n_models_m, k12=9))


def _fixture_cfg(tmp, spec, name, pre=None, c0u=None, c0m=None):
    d = os.path.join(tmp, name); os.makedirs(d)
    gp, ep = os.path.join(d, "gen.db"), os.path.join(d, "eval.db")
    gs = _mk_view(gp, "gen", ("TRAIN", "GATE"), spec)
    es = _mk_view(ep, "eval", ("EVAL",), spec)
    out = os.path.join(d, "out")
    rp = os.path.join(d, "residual.txt")
    evu = [it["id"] for it in spec["items"] if it["side"] == "EVAL"]
    with open(rp, "w", encoding="utf-8", newline="\n") as f:
        f.write("# selftest residual list\n" + "\n".join(evu[:12] + evu[-5:]) + "\n")
    pre = dict(pre or dict(variant_rule="UNUSABLE_CELL", steward_bracket="SELFTEST", residual_file=("residual.txt", G.sha256_file(rp)),
                           train_unit="component", p2_measure="contribution"))
    return Cfg(gen_path=gp, eval_path=ep, side_tsv=None, gen_sha=gs, eval_sha=es, pool_u="pv_u", cv_u="mc6", pool_m="pv_m",
               cv_m="mmlu", reg=spec["reg"], pre=pre, k12=spec["k12"], k37_dropped=spec["dropped"],
               k37_sha=hashlib.sha256("\n".join(spec["k37"]).encode("utf-8")).hexdigest(),
               policy_path=os.path.join(out, "pol.json"), out_u=os.path.join(out, "U.txt"), out_m=os.path.join(out, "M.txt"),
               mark_u=os.path.join(out, "U.READ_STARTED"), mark_m=os.path.join(out, "M.READ_STARTED"),
               c0_u=c0u or (lambda say: dict(best=REG["c0_best"], bs=REG["c0_bs"], tdom=REG["c0_tdom"])),
               c0_m=c0m or (lambda say: REG["c0_k12"]), residual_root=d, hook=None)


def _naive_point(spec, rule, overlay=True):
    """INDEPENDENT recomputation of leg U's point G (plain Python loops over the fixture's raw rows)."""
    mu = sorted(spec["models_u"])
    side = {it["id"]: it for it in spec["items"] if "mc6" in it["cvs"]}
    cells = defaultdict(list)
    for r in spec["responses"]:
        if r["cv"] != "mc6" or r["side"] == "GATE":
            continue
        v = r["mf"] if (overlay and r["mf"] is not None) else r["c"]
        cells[(r["item"], r["model"])].append(v)
    val = {}
    for k, vs in cells.items():
        if len(vs) == 1: val[k] = vs[0]
        elif rule == "AGREE_OR_UNUSABLE" and len(set(vs)) == 1: val[k] = vs[0]
    comp = lambda i: all((i, m) in val for m in mu)
    tr = [i for i, it in side.items() if it["side"] == "TRAIN" and comp(i)]
    evl = [i for i, it in side.items() if it["side"] == "EVAL" and comp(i)]
    tot = {m: sum(val[(i, m)] for i in tr) for m in mu}
    best = max(mu, key=lambda m: (tot[m], -mu.index(m)))
    per = defaultdict(lambda: defaultdict(int))
    for i in tr:
        for m in mu:
            per[(side[i]["src"], side[i]["dom"])][m] += val[(i, m)]
    pol = {k: max(mu, key=lambda m: (d[m], -mu.index(m))) for k, d in per.items()}
    bs = sum(val[(i, best)] for i in evl) / len(evl)
    td = sum(val[(i, pol.get((side[i]["src"], side[i]["dom"]), best))] for i in evl) / len(evl)
    return best, bs, td, len(tr), len(evl)


def selftest():
    global MUTANT
    import time
    t0 = time.time()
    tmp = tempfile.mkdtemp(prefix="v2dc_selftest_")
    checks = []
    def check(name, ok):
        checks.append((name, bool(ok))); print("  [%s] %s" % ("PASS" if ok else "FAIL", name), flush=True)
    quiet = lambda s: None
    try:
        # --- guards
        class FakeConn:
            def execute(self, sql, p=()): return iter(())
        tw = G.KeyTripwire(FakeConn(), FORBIDDEN, label="t")
        for sql, want in (("SELECT output_zlib FROM response", True), ("SELECT is_correct FROM response", True),
                          ("SELECT model, item_id, COUNT(*) FROM response", False), ("SELECT x FROM reference", True),
                          ("SELECT * FROM side", True), ("SELECT item_id, r.* FROM side r", True)):
            try:
                tw.execute(sql); got = False
            except SystemExit:
                got = True
            check("tripwire %s -> refused %s" % (sql[:40], want), got == want)
        tw.unseal("selftest")
        try:
            tw.execute("SELECT is_correct FROM response"); check("tripwire unsealed admits the key", True)
        except SystemExit:
            check("tripwire unsealed admits the key", False)
        p = os.path.join(tmp, "wo.txt"); G.write_once(p, "a")
        try:
            G.write_once(p, "b"); check("write_once refuses an existing path", False)
        except SystemExit:
            check("write_once refuses an existing path", open(p).read() == "a")
        # --- tie-break (first model in sorted order), independent of fixtures
        Dt = UD(); Dt.models = ["a", "b", "c"]; Dt.A = np.array([[1, 1, 0], [0, 0, 1], [1, 1, 1]]); Dt.n = 3
        Dt.groupings = {"tsrc": (np.zeros(3, np.int64), 1), "tdom": (np.zeros(3, np.int64), 1), "plac": (np.zeros(3, np.int64), 1)}
        Dt.flat = {k: (g[:, None] * 3 + np.arange(3)[None, :]).ravel() for k, (g, _) in Dt.groupings.items()}
        Dt.train_set = frozenset([0, 1, 2]); Dt.fit_asserts = 0
        P = fit(Dt, np.array([1, 1, 1]))
        check("argmax tie-break = the first model in sorted-name order (a, not b)", Dt.models[P.gb] == "a" and P.pol["tdom"][0] == 0)
        # --- the fixture
        spec = _fixture_spec()
        cfg = _fixture_cfg(tmp, spec, "main")
        EVENTS.clear()
        with contextlib.redirect_stdout(io.StringIO()):
            dry_u = mode(cfg, "U", True)
        check("dry-run U: returns None, writes nothing", dry_u is None and not os.path.exists(cfg.policy_path) and not os.path.exists(cfg.mark_u))
        with contextlib.redirect_stdout(io.StringIO()) as so:
            mode(cfg, "M", True)
        txt = so.getvalue()
        check("dry-run M: no statistic printed (no 'R =' / 'G =' / 'HELD' / 'FAILED')",
              not re.search(r"R = |G = | HELD| FAILED", txt) and "no key column was selected" in txt)
        check("dry-run M: writes nothing", not os.path.exists(cfg.out_m) and not os.path.exists(cfg.mark_m))
        # preconditions refuse
        cfgp = _fixture_cfg(tmp, spec, "pre", pre=dict(PRECONDITIONS, steward_bracket=None, residual_file=None, train_unit=None,
                                                         p2_measure=None))
        for leg in ("U", "M"):
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    mode(cfgp, leg, False)
                check("run %s refuses with preconditions unset" % leg, False)
            except SystemExit as e:
                check("run %s refuses with preconditions unset (%s)" % (leg, str(e)[:30]), "[PRECONDITION]" in str(e) and
                      all(k in str(e) for k in ("steward_bracket", "residual_file", "train_unit", "p2_measure")))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(_fixture_cfg(tmp, spec, "pre2", pre=dict(PRECONDITIONS, variant_rule=None)), "U", False)
            check("run U refuses with variant_rule unset", False)
        except SystemExit as e:
            check("run U refuses with variant_rule unset", "[PRECONDITION]" in str(e) and "variant_rule" in str(e))
        check("R4 (iii): the variant rule of record is UNUSABLE_CELL", PRECONDITIONS["variant_rule"] == "UNUSABLE_CELL")
        rset, rdesc = load_residual(Cfg(pre=dict(PRECONDITIONS), residual_root=ROOT))
        check("C34-3: PRECONDITIONS carry the e09e551 / 5572465 values (steward 5572465, the 422-id file at its LF pin, train_unit"
              " item, p2_measure contribution); missing_preconditions finds none; the committed file loads %d ids" % len(rset),
              PRECONDITIONS["steward_bracket"].startswith("steward 5572465 (") and "e09e551" in PRECONDITIONS["steward_bracket"]
              and PRECONDITIONS["residual_file"] == ("experiment_configs/v2_residual_band15_19_eval_422.txt",
                                                     "b35b3e03b9bcda48b5f447e76249d2184b418a711920b9e80224d16ff50cee90")
              and PRECONDITIONS["train_unit"] == "item" and PRECONDITIONS["p2_measure"] == "contribution"
              and missing_preconditions(Cfg(pre=dict(PRECONDITIONS))) == [] and len(rset) == 422 == REG["residual_n"]
              and "b35b3e03b9bcda48b5f447e76249d2184b418a711920b9e80224d16ff50cee90" in rdesc)
        rpx = os.path.join(tmp, "resid_crlf.txt")
        with open(os.path.join(ROOT, RESIDUAL_REL), "rb") as f:
            lf_ = f.read().replace(b"\r\n", b"\n")
        with open(rpx, "wb") as f:
            f.write(lf_.replace(b"\n", b"\r\n"))
        r_cr, _d = load_residual(Cfg(pre=dict(residual_file=(rpx, RESIDUAL_SHA_LF)), residual_root=ROOT))
        with open(rpx, "wb") as f:
            f.write(lf_ + b"i:extra\n")
        try:
            load_residual(Cfg(pre=dict(residual_file=(rpx, RESIDUAL_SHA_LF)), residual_root=ROOT))
            bad_ = "no refusal"
        except SystemExit as e:
            bad_ = str(e)
        check("C34-3: the CRLF rendering identifies to the LF pin (%d ids); one added id REFUSES at the pin" % len(r_cr),
              r_cr == rset and "[PIN] residual file" in bad_)
        check("C34-3 PLAN = ruling 9: C1 N 5,907 / 5,404 comps / Kish 1.3115 / n_eff %d / SE 0.00674 / MDE80 %.4f; C2 SE 0.0339,"
              " MDE80 0.095, null p95 <= 0.60 (break-even 0.745)" % (PLAN["C1"]["n_eff"], PLAN["C1"]["mde"]),
              PLAN["C1"]["n"] == 5907 and PLAN["C1"]["components"] == 5404 and PLAN["C1"]["deff"] == 1.3115
              and PLAN["C1"]["n_eff"] == 4504 and PLAN["C1"]["se"] == 0.00674 and PLAN["C1"]["mde"] == 0.0189
              and PLAN["C2"]["se"] == 0.0339 and PLAN["C2"]["mde"] == 0.095 and "null p95 <= 0.60" in PLAN["C2"]["verdict"]
              and "0.745" in PLAN["C2"]["verdict"] and STRATA_BESIDE in PLAN["C2"]["verdict"])
        # C0 refusal
        cfgc = _fixture_cfg(tmp, spec, "c0", c0u=lambda s: dict(best="x", bs="0.1", tdom="0.2"), c0m=lambda s: "0.1234")
        for leg in ("U", "M"):
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    mode(cfgc, leg, False)
                check("C0 miss refuses leg %s" % leg, False)
            except SystemExit as e:
                check("C0 miss refuses leg %s before any v2 file is opened" % leg, "[C0]" in str(e) and
                      not os.path.exists(cfgc.mark_u) and not os.path.exists(cfgc.mark_m) and not os.path.exists(cfgc.policy_path))
        # C0 fit on a generic table equals the naive fit
        rows = []
        rs = np.random.RandomState(3)
        for q in range(400):
            rows.append((q, "S%d" % (q % 3), "d%d" % (q % 7), q % 4 == 0, {m: int(rs.rand() < 0.3 + 0.1 * j) for j, m in enumerate("abcde")}))
        got = c0_fit_generic(list("abcde"), rows, quiet)
        tr = [r for r in rows if not r[3]]; evr = [r for r in rows if r[3]]
        tot = {m: sum(r[4][m] for r in tr) for m in "abcde"}; best = max("abcde", key=lambda m: (tot[m], -"abcde".index(m)))
        per = defaultdict(lambda: defaultdict(int))
        for r in tr:
            for m in "abcde": per[(r[1], r[2])][m] += r[4][m]
        pol = {k: max("abcde", key=lambda m: (d[m], -"abcde".index(m))) for k, d in per.items()}
        td = sum(r[4][pol.get((r[1], r[2]), best)] for r in evr) / len(evr)
        check("C0 generic fit equals the naive fit (best, bs, tdom to 4 dp)", got["best"] == best and got["tdom"] == "%.4f" % td
              and got["bs"] == "%.4f" % (sum(r[4][best] for r in evr) / len(evr)))
        # --- the real run on the fixture, with the unit hooks
        seen = dict(eval_const=True, train_const=True, n=0, strat_ok=True)
        def hook(D, wt, v):
            seen["n"] += 1
            for arr in D.eval_units["strata"]:
                su = set(arr.tolist())
                drawn = {}
                for j in range(len(D.E)):
                    u = int(D.eval_units["unit_pos"][j])
                    if u in su:
                        drawn[u] = v[j]
                if int(round(sum(drawn.values()))) != len(arr):
                    seen["strat_ok"] = False
            for pos_arr, vec in ((D.E, v), (None, None)):
                pass
            ce = defaultdict(set)
            for j, k in enumerate(D.E): ce[D.comp[k]].add(v[j])
            if any(len(s) > 1 for s in ce.values()): seen["eval_const"] = False
            ct = defaultdict(set)
            for k in D.T: ct[D.comp[k]].add(int(wt[k]))
            if any(len(s) > 1 for s in ct.values()): seen["train_const"] = False
        cfg.hook = hook
        EVENTS.clear()
        with contextlib.redirect_stdout(io.StringIO()):
            ru = mode(cfg, "U", False)
        check("run U: outcome, policy and marker written", all(os.path.exists(p) for p in (cfg.out_u, cfg.policy_path, cfg.mark_u)))
        check("B3 order: the policy file is written BEFORE open_eval('route')",
              "policy_written" in EVENTS and "open:eval:route" in EVENTS and EVENTS.index("policy_written") < EVENTS.index("open:eval:route"))
        check("two-stage EVAL resampling is by COMPONENT (weights constant within a component)", seen["eval_const"] and seen["n"] == cfg.reg["B"])
        check("two-stage TRAIN resampling by component when train_unit = component", seen["train_const"])
        best, bs, td, ntr, nev = _naive_point(spec, "UNUSABLE_CELL")
        c1 = ru["st"]["C1"]
        check("point G equals the independent recomputation (best %s, %.4f / %.4f, TRAIN %d, EVAL %d)" % (best, bs, td, ntr, nev),
              ru["policy"]["best_single"] == best and abs(c1["point"] - (td - bs)) < 1e-12 and ru["D"].n_eval == nev and ru["D"].n_train == ntr)
        bt, D = ru["bt"], ru["D"]
        d2 = bt["two"][:, 0, TDOM] - bt["two"][:, 0, BS]; di = bt["iid"][:, 0, TDOM] - bt["iid"][:, 0, BS]
        check("DEFF = var_2stage / var_iid (independent)", abs(c1["deff"] - np.var(d2, ddof=1) / np.var(di, ddof=1)) < 1e-9)
        check("C2 cells = the strata with >= floor key-complete EVAL items (tiny excluded)", "MATH/tiny" not in ru["cells"] and len(ru["cells"]) == 7)
        # --- READY e451753 D2: value-asserting checks on the deciding paths (each kills a reviewer mutant)
        sd2 = float(np.std(d2, ddof=1))
        check("R1: C1's deciding interval = point +- 1.96 x sd(two-stage contrast) [%.6f, %.6f]" % (c1["point"] - 1.96 * sd2, c1["point"] + 1.96 * sd2),
              abs(c1["lo"] - (c1["point"] - 1.96 * sd2)) < 1e-12 and abs(c1["hi"] - (c1["point"] + 1.96 * sd2)) < 1e-12)
        check("R2: every replicate draws each EVAL stratum's own unit count (%d replicates)" % seen["n"], seen["strat_ok"] and seen["n"] == cfg.reg["B"])
        p0 = ru["st"]["C2"]
        nt0 = pri.null_tables({k: v for k, v in ru["cells"].items()}, ru["K_ev"], sorted(spec["models_u"]), 20, list(range(1, 21)))
        check("R3: the C2 null re-derived with RandomState seeds 1..20 equals the run's null reads",
              [round(x, 12) for x in sorted(x[1] for x in nt0["reads"])] == [round(x, 12) for x in p0["null_reads"]])
        res_ev = set(ru["residual"]) & set(D.items[k] for k in D.E)
        c_nr = contrast(bt, D, "NO_RESIDUAL", TDOM, BS)
        check("R4: NO_RESIDUAL n = N - |residual in scored EVAL| = %d - %d" % (D.n_eval, len(res_ev)), len(res_ev) > 0 and c_nr["n"] == D.n_eval - len(res_ev))
        nbb = sum(1 for k in D.E if D.src[k] == "BBH")
        gbb = contrast(bt, D, "SRC:BBH", TDOM, BS)["point"]
        hand = (nbb / D.n_eval) * gbb / c1["point"]
        check("R5: P2 contribution = (n_BBH / N) x G_BBH / G = (%d / %d) x %.6f / %.6f = %.6f" % (nbb, D.n_eval, gbb, c1["point"], hand),
              c1["point"] > 0 and abs(ru["st"]["p2_both"][0] - hand) < 1e-12)
        stb = dict(c0=dict(best=REG["c0_best"], bs=REG["c0_bs"], tdom=REG["c0_tdom"]), floor=120, p2_measure="contribution", p2_share=None,
                   p2_both=(float("nan"),) * 2, PLAC=dict(point=0.0, lo=-0.01, hi=0.01, se2=0.005, pct=(-0.01, 0.01), se_iid=0.004, n=100,
                                                          deff=1.5, n_eff=66, mde=0.014, var2=1e-5),
                   C2=dict(R=0.8, lo=0.7, hi=0.9, lo_fx=0.7, hi_fx=0.9, sd=0.02, se_re=0.03, null_p95=0.5, null_median=0.2, cells=["a"], n_items=1, R_model=0.9))
        def c1_class(hi):
            x = dict(stb, C1=dict(point=hi - 0.01, lo=hi - 0.02, hi=hi, se2=0.005, pct=(0, 0), se_iid=0.004, n=100, deff=1.5, n_eff=66, mde=0.014, var2=1e-5),
                     NON_BBH=dict(point=0.0, lo=-0.01, hi=0.01, se2=0.005, pct=(0, 0), se_iid=0.004, n=50, deff=1.5, n_eff=33, mde=0.014, var2=1e-5))
            with contextlib.redirect_stdout(io.StringIO()):
                return verdict_lines_u(x)[1]["C1"]
        check("R6: C1 boundaries: hi = -1e-9 -> FAILED, hi = 0 -> UNDETERMINED, hi = 0.005 -> UNDETERMINED",
              c1_class(-1e-9) == "FAILED" and c1_class(0.0) == "UNDETERMINED" and c1_class(0.005) == "UNDETERMINED")
        # C34-3 printed values (ruling 9 plan, strata beside C2 and F3; ruling 10's line under T1)
        def u_text(plac_lo, c2_hi):
            x = dict(stb, PLAC=dict(stb["PLAC"], lo=plac_lo, hi=plac_lo + 0.02, point=plac_lo + 0.01),
                     C2=dict(stb["C2"], hi=c2_hi, lo=min(stb["C2"]["lo"], c2_hi - 0.1)),
                     C1=dict(point=0.03, lo=0.02, hi=0.04, se2=0.005, pct=(0, 0), se_iid=0.004, n=100, deff=1.5, n_eff=66, mde=0.014, var2=1e-5),
                     NON_BBH=dict(point=0.0, lo=-0.01, hi=0.01, se2=0.005, pct=(0, 0), se_iid=0.004, n=50, deff=1.5, n_eff=33, mde=0.014, var2=1e-5))
            with contextlib.redirect_stdout(io.StringIO()):
                return "\n".join(verdict_lines_u(x)[0])
        t_ok, t_t1 = u_text(-0.01, 0.9), u_text(0.001, 0.45)
        check("C34-3 print: C1 plan of record (ruling 9) by value; C2 plan and the 14-of-52 strata beside C2 and F3",
              "SUPPORT (plan of record, ruling 9): scored N 5907 in 5404 components, DEFF 1.3115 (Kish), n_eff 4504, SE 0.00674,"
              " MDE80 +1.89pp; SCOREABLE (ruling 9, D3 ADOPTED)" in t_ok
              and "registered SE 0.0339, MDE80 0.095; SCOREABLE while the null p95 <= 0.60 (break-even about 0.745); 14 of the 52"
                  " union strata (13 MMLU-Pro + IFEval)" in t_ok
              and "F3 NOT FIRED (C2 HELD); 14 of the 52 union strata (13 MMLU-Pro + IFEval)" in t_ok
              and "does not carry to v2; 14 of the 52 union strata (13 MMLU-Pro + IFEval)" in t_t1)
        check("C34-3 print (ruling 10): under T1 F1 reads NOT EVALUATED and 'USE clause NOT licensed as content-closed'",
              "T1 FIRED" in t_t1 and "F1 NOT EVALUATED (C1 VOID by T1): USE clause NOT licensed as content-closed (ruling 10)" in t_t1
              and "USE clause NOT licensed" not in t_ok)
        # D1: the rows fetched equal the in-scope rows (the fixture carries GATE rows and rows of models outside the roster)
        mu_ = set(spec["models_u"])
        in_tr = sum(1 for r in spec["responses"] if r["cv"] == "mc6" and r["side"] == "TRAIN" and r["model"] in mu_)
        in_ev = sum(1 for r in spec["responses"] if r["cv"] == "mc6" and r["side"] == "EVAL" and r["model"] in mu_)
        n_gate = sum(1 for r in spec["responses"] if r["cv"] == "mc6" and r["side"] == "GATE")
        check("D1: leg U key rows fetched = in-scope rows (TRAIN %d, EVAL %d; the %d GATE rows are never fetched)" % (in_tr, in_ev, n_gate),
              n_gate > 0 and ru["kst"]["train"]["key_rows_fetched"] == in_tr and ru["kst"]["eval"]["key_rows_fetched"] == in_ev)
        p = ru["st"]["C2"]
        check("C2 null p95 = the 19th of 20 interaction-only reads", abs(p["null_p95"] - sorted(p["null_reads"])[18]) < 1e-15)
        check("C2 decides on the RE-HALVED jackknife (both jackknives finite and different)", all(np.isfinite([p["lo"], p["hi"], p["lo_fx"], p["hi_fx"]]))
              and (p["lo"] != p["lo_fx"] or p["hi"] != p["hi_fx"]))
        check("placebo labels are a permutation of the true labels, not the identity",
              sorted(D.g_plac.tolist()) == sorted(D.g_tdom.tolist()) and D.g_plac.tolist() != D.g_tdom.tolist())
        otxt = open(cfg.out_u, encoding="utf-8").read()
        check("outcome U first line is the pool id", otxt.startswith("POOL pv_u"))
        check("outcome U carries W1 / W2 / W3 words and the name-match disclosure",
              "content-closed under CK-CLOSE-v2" in otxt and "contains no embedder" in otxt and "NOT a replication" in otxt and "name-matched" in otxt)
        # a re-run is refused by the B1 marker, and the policy / outcome are write-once
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfg, "U", False)
            check("re-run U refused", False)
        except SystemExit as e:
            check("re-run U refused (%s)" % str(e)[:14], "[WRITE-ONCE]" in str(e) or "[B1]" in str(e))
        os.remove(cfg.out_u); os.remove(cfg.policy_path)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfg, "U", False)
            check("re-run U refused by the B1 marker alone", False)
        except SystemExit as e:
            check("re-run U refused by the existing B1 marker (policy / outcome not re-created)", ("[B1]" in str(e) or
                  cfg.mark_u in str(e)) and not os.path.exists(cfg.out_u) and not os.path.exists(cfg.policy_path))
        EVENTS.clear()
        with contextlib.redirect_stdout(io.StringIO()):
            rm = mode(cfg, "M", False)
        check("run M: outcome and marker written", os.path.exists(cfg.out_m) and os.path.exists(cfg.mark_m))
        check("leg M: history EXCLUDED BY NAME from both rosters (it clears the fixture floor)", all("history" not in v for v in rm["admitted"].values())
              and all(len(v) == 7 for v in rm["admitted"].values()))
        check("leg M: K12 and K37 each read", rm["st"]["K12"]["R"] == rm["st"]["K12"]["R"] and rm["st"]["K37"]["R"] == rm["st"]["K37"]["R"])
        mtxt = open(cfg.out_m, encoding="utf-8").read()
        k37s = set(spec["k37"])
        in_m = sum(1 for r in spec["responses"] if r["cv"] == "mmlu" and r["model"] in k37s)
        out_m = sum(1 for r in spec["responses"] if r["cv"] == "mmlu" and r["model"] not in k37s)
        check("D1: leg M key rows fetched = the K37 rows (%d; the %d rows of models outside K37 are never fetched)" % (in_m, out_m),
              out_m > 0 and rm["kst"]["key_rows_fetched"] == in_m)
        try:
            cw = _fixture_cfg(tmp, spec, "k37wrong"); cw.k37_sha = "0" * 64
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cw, "M", False)
            check("D11: a wrong K37 sha refuses", False)
        except SystemExit as e:
            check("D11: a wrong K37 sha refuses before the read", "[ROSTER]" in str(e) and not os.path.exists(cw.mark_m))
        check("outcome M first line is the pool id", mtxt.startswith("POOL pv_m"))
        # AGREE rule equals its naive recomputation; REFUSE refuses
        cfga = _fixture_cfg(tmp, spec, "agree", pre=dict(cfg.pre, variant_rule="AGREE_OR_UNUSABLE"))
        with contextlib.redirect_stdout(io.StringIO()):
            ra = mode(cfga, "U", False)
        b2, bs2, td2, _, nev2 = _naive_point(spec, "AGREE_OR_UNUSABLE")
        check("AGREE_OR_UNUSABLE: point G equals the naive recomputation", abs(ra["st"]["C1"]["point"] - (td2 - bs2)) < 1e-12 and ra["D"].n_eval == nev2)
        cfgr = _fixture_cfg(tmp, spec, "refuse", pre=dict(cfg.pre, variant_rule="REFUSE"))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfgr, "U", False)
            check("REFUSE rule refuses on a multi-response cell", False)
        except SystemExit as e:
            check("REFUSE rule refuses on a multi-response cell", "[VARIANT-RULE]" in str(e))
        # --- branch coverage of the verdict lines (synthetic stats)
        base_c = lambda pt, lo, hi: dict(point=pt, lo=lo, hi=hi, se2=0.005, pct=(lo, hi), se_iid=0.004, n=100, deff=1.5, n_eff=66, mde=0.014, var2=1e-5)
        base_p = lambda R, lo, hi, p95: dict(R=R, lo=lo, hi=hi, lo_fx=lo, hi_fx=hi, sd=0.02, se_re=0.03, null_p95=p95, null_median=0.2,
                                             cells=["a", "b"], n_items=300, R_model=0.9)
        c0d = dict(best=REG["c0_best"], bs=REG["c0_bs"], tdom=REG["c0_tdom"])
        cases = [
            dict(C1=base_c(0.03, 0.01, 0.05), PLAC=base_c(0.0, -0.01, 0.01), C2=base_p(0.85, 0.80, 0.90, 0.5), p2_share=0.6, p2_both=(0.6, 0.55), NON_BBH=base_c(0.012, -0.01, 0.03)),
            dict(C1=base_c(-0.03, -0.05, -0.01), PLAC=base_c(0.0, -0.01, 0.01), C2=base_p(0.40, 0.30, 0.50, 0.5), p2_share=None, p2_both=(float("nan"),) * 2, NON_BBH=base_c(0.05, 0.03, 0.07)),
            dict(C1=base_c(0.01, -0.01, 0.03), PLAC=base_c(0.0, -0.01, 0.01), C2=base_p(0.55, 0.45, 0.65, 0.5), p2_share=0.3, p2_both=(0.3, 0.2), NON_BBH=base_c(0.012, -0.01, 0.03)),
            dict(C1=base_c(0.03, 0.01, 0.05), PLAC=base_c(0.02, 0.005, 0.035), C2=base_p(0.85, 0.80, 0.90, 0.5), p2_share=0.6, p2_both=(0.6, 0.55), NON_BBH=base_c(0.012, -0.01, 0.03)),
            dict(C1=base_c(0.05, 0.03, 0.07), PLAC=base_c(0.0, -0.01, 0.01), C2=base_p(0.95, 0.9, 0.99, 0.5), p2_share=0.6, p2_both=(0.6, 0.55), NON_BBH=base_c(0.012, -0.01, 0.03)),
        ]
        cases[4]["C1"]["deff"] = 3.0
        for cs in cases:
            cs.update(c0=c0d, floor=120, p2_measure="contribution")
            with contextlib.redirect_stdout(io.StringIO()):
                verdict_lines_u(cs)
        # C2 boundary: hi == p95 is FAILED; lo == p95 is not HELD
        check("C2 rule: hi == p95 -> FAILED; lo == p95 -> UNDETERMINED",
              r_verdict(base_p(0.5, 0.4, 0.5, 0.5)) == "FAILED" and r_verdict(base_p(0.6, 0.5, 0.7, 0.5)) == "UNDETERMINED")
        # a numpy.bool_ verdict value still prints (never identity-tested)
        check("as_bool(numpy.bool_(True)) is True", G.as_bool(np.bool_(True)) is True)
        for st in (dict(c0="0.8665", n_models={"K12": 12, "K37": 37}, K12=base_p(0.87, 0.81, 0.93, 0.4), K37=base_p(0.40, 0.30, 0.40, 0.4)),
                   dict(c0="0.8665", n_models={"K12": 12, "K37": 37}, K12=base_p(0.50, 0.35, 0.65, 0.4), K37=base_p(0.95, 0.91, 0.99, 0.4))):
            with contextlib.redirect_stdout(io.StringIO()):
                verdict_lines_m(st)
        # G4 refusal executed
        try:
            gate_g4(dict(var2=0.0), dict(var2=1.0)); check("G4 refuses a zero variance", False)
        except SystemExit:
            check("G4 refuses a zero variance", True)
        # --- the B3 refusal branch, executed
        try:
            b3_guard(_fixture_cfg(tmp, spec, "b3probe")); check("B3 guard refuses without the policy file", False)
        except SystemExit as e:
            check("B3 guard refuses without the policy file", "[B3]" in str(e))
        # --- RP12 G14 (the tree-cell arm; 0a0361b) -------------------------------------------------------------------------
        # (1) INERTNESS: without --tree-cells, leg U's outcome equals the base blob f7f30ebe's on the same fixture, line for line
        #     (the script-identity lines and the fixture directories normalised); the base is run from git, not from memory.
        import importlib.util as _ilu, subprocess
        base_src = subprocess.run(["git", "show", "f7f30ebea2b2f729743e682cf2fa6cae0f16b0e9"], cwd=ROOT, capture_output=True, check=True).stdout
        bdir = os.path.join(tmp, "basemod"); os.makedirs(bdir)
        bpath = os.path.join(bdir, "v2dc_base_f7f30ebe.py")
        with open(bpath, "wb") as f:
            f.write(base_src)
        spec_b = _ilu.spec_from_file_location("v2dc_base_f7f30ebe", bpath); basemod = _ilu.module_from_spec(spec_b)
        spec_b.loader.exec_module(basemod)
        cfg_n, cfg_b = _fixture_cfg(tmp, spec, "inert_new"), _fixture_cfg(tmp, spec, "inert_base")
        with contextlib.redirect_stdout(io.StringIO()):
            mode(cfg_n, "U", False)
            basemod.mode(cfg_b, "U", False)
        def norm_(path, d):
            out_ = []
            for l in open(path, encoding="utf-8").read().splitlines():
                if "v2_declared_cells" in l or "v2dc_base_f7f30ebe" in l:
                    continue
                # the B3 line's policy sha covers the policy's "script" key (the script identity); the policy content is
                # compared below with that key removed
                out_.append(re.sub(r"\| sha256 [0-9a-f]{64} \|", "| sha256 <POLICY-SHA> |", l.replace(d, "<D>")))
            return out_
        tn = norm_(cfg_n.out_u, os.path.dirname(cfg_n.gen_path)); tb = norm_(cfg_b.out_u, os.path.dirname(cfg_b.gen_path))
        check("G14 INERTNESS: no --tree-cells -> leg U outcome equal to base blob f7f30ebe's (%d lines; identity lines and paths"
              " normalised)" % len(tn), tn == tb and len(tn) > 40 and any(l.startswith("C1 = ") or " C1 " in l for l in tn))
        pn = json.load(open(cfg_n.policy_path)); pb = json.load(open(cfg_b.policy_path))
        pn.pop("script"); pb.pop("script"); pn.pop("gen_view_sha256_bytes"); pb.pop("gen_view_sha256_bytes")
        check("G14 INERTNESS: the frozen TRAIN policy equals the base blob's (no tree_cell key)", pn == pb and "tree_cell" not in pn)
        # (2) the tree arm on the fixture: identity tree (cell = the declared key) and the source-level tree
        c1_ref = ru["st"]["C1"]
        ident_fx = (_pp(c1_ref["point"]), _pp(c1_ref["lo"]), _pp(c1_ref["hi"]))
        mc6 = [it for it in spec["items"] if "mc6" in it["cvs"] and it["side"] in ("TRAIN", "EVAL")]
        def tree_file(name, cell_of, drop=0):
            pth = os.path.join(tmp, name + ".tsv")
            rows_ = ["%s\t%s" % (it["id"], cell_of(it)) for it in mc6][drop:]
            with open(pth, "w", encoding="utf-8", newline="\n") as f:
                f.write("# %s b0_snapshot=FIXTURE rule=flatLeaf\nitem_id\ttree_cell\n" % TREE_CELLS_FORMAT + "\n".join(rows_) + "\n")
            return pth, hashlib.sha256(open(pth, "rb").read()).hexdigest()
        def g14_cfg(name, cell_of, ident=ident_fx, drop=0):
            c = _fixture_cfg(tmp, spec, name)
            pth, sh = tree_file(name, cell_of, drop)
            c.tree, c.tree_desc = load_tree_cells(pth, sh)
            c.g14_identity = ident
            c.policy_path = c.policy_path.replace("pol.json", "G14_pol.json"); c.out_u = c.out_u.replace("U.txt", "G14.txt")
            c.mark_u = c.mark_u.replace("U.READ_STARTED", "G14.READ_STARTED")
            return c
        cfg_i = g14_cfg("g14_identity", lambda it: "%s/%s" % (it["src"], it["dom"]))
        with contextlib.redirect_stdout(io.StringIO()):
            ri = mode(cfg_i, "U", False)
        gi, mi = ri["st"]["G"], ri["st"]["M"]
        gtxt = open(cfg_i.out_u, encoding="utf-8").read()
        check("G14 identity tree: G_tree == C1 (%s) and M == 0 exactly; the declared arm reproduces the fixture's C1 digits"
              % _pp(gi["point"]), abs(gi["point"] - c1_ref["point"]) < 1e-12 and mi["point"] == 0.0 and mi["lo"] == 0.0 and mi["hi"] == 0.0
              and ri["st"]["C1"]["lo"] == c1_ref["lo"] and ri["st"]["C1"]["hi"] == c1_ref["hi"])
        check("G14 identity tree: the outcome prints the G14 and M lines with these values and writes the G14 files only",
              ("G_tree = acc(%s) - acc(best single) = %s | two-stage [%s, %s]" % (ARM_TREE, _pp(gi["point"]), _pp(gi["lo"]), _pp(gi["hi"]))) in gtxt
              and "M = G_tree - G_declared = +0.00pp | two-stage [+0.00pp, +0.00pp]" in gtxt
              and "REPRODUCED to the printed digits" in gtxt and os.path.exists(cfg_i.policy_path) and os.path.exists(cfg_i.mark_u)
              and not os.path.exists(cfg_i.out_u.replace("G14.txt", "U.txt")) and "C2 " not in gtxt.split("=== G14")[1])
        cfg_s = g14_cfg("g14_source", lambda it: it["src"])
        with contextlib.redirect_stdout(io.StringIO()):
            rs_ = mode(cfg_s, "U", False)
        tsrc_g = contrast(rs_["bt"], rs_["D"], "ALL", TSRC, BS)
        gs = rs_["st"]["G"]
        check("G14 source-level tree: G_tree equals the TRUE source arm's G (%s), point and two-stage interval" % _pp(tsrc_g["point"]),
              abs(gs["point"] - tsrc_g["point"]) < 1e-12 and abs(gs["lo"] - tsrc_g["lo"]) < 1e-12 and abs(gs["hi"] - tsrc_g["hi"]) < 1e-12
              and abs(gs["point"] - c1_ref["point"]) > 1e-6)
        ms_ = rs_["st"]["M"]
        check("G14 source-level tree: M = G_tree - G_declared = %s (sign and value)" % _pp(ms_["point"]),
              abs(ms_["point"] - (tsrc_g["point"] - rs_["st"]["C1"]["point"])) < 1e-12 and ms_["point"] < 0)
        pol_s = json.load(open(cfg_s.policy_path))
        check("G14 B3: the frozen policy carries the tree arm's per-cell picks (one per source)", sorted(pol_s["tree_cell"]) == ["BBH", "MATH", "MMLU_PRO"])
        # (3) refusals: the identity miss (no outcome), a missing scored item, the pin
        cfg_x = g14_cfg("g14_miss", lambda it: "%s/%s" % (it["src"], it["dom"]), ident=("+9.99pp", "+1.00pp", "+2.00pp"))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfg_x, "U", False)
            check("G14 identity miss refuses", False)
        except SystemExit as e:
            check("G14 identity miss refuses with [G14-IDENTITY] and writes no outcome", str(e).startswith("[G14-IDENTITY] the declared arm prints C1 = %s" % ident_fx[0])
                  and not os.path.exists(cfg_x.out_u))
        cfg_d = g14_cfg("g14_drop", lambda it: "%s/%s" % (it["src"], it["dom"]), drop=len(mc6))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfg_d, "U", False)
            check("G14 missing tree cells refuse", False)
        except SystemExit as e:
            check("G14 missing tree cells refuse (%s)" % str(e)[:40], str(e).startswith("[G14] ") and "scored item(s) carry no tree cell" in str(e))
        # C-5: an EVAL item of the scoring set in <no-routing-row> refuses BEFORE the marker; a TRAIN one is printed and fitted
        first_ev = sorted(it["id"] for it in mc6 if it["side"] == "EVAL")[0]
        first_tr = sorted(it["id"] for it in mc6 if it["side"] == "TRAIN")[0]
        cfg_n = g14_cfg("g14_norow", lambda it: NO_ROUTING_ROW if it["id"] == first_ev else "%s/%s" % (it["src"], it["dom"]))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfg_n, "U", False)
            check("C-5 an EVAL item in <no-routing-row> refuses", False)
        except SystemExit as e:
            check("C-5 an EVAL item in <no-routing-row> refuses before the B1 marker", str(e).startswith(
                "[G14-NOROW] 1 EVAL item(s) of the scoring set have no routing row in B0's readout (first ['%s'])" % first_ev)
                  and not os.path.exists(cfg_n.mark_u))
        cfg_t = g14_cfg("g14_norow_tr", lambda it: NO_ROUTING_ROW if it["id"] == first_tr else "%s/%s" % (it["src"], it["dom"]))
        with contextlib.redirect_stdout(io.StringIO()) as so_t:
            rt = mode(cfg_t, "U", False)
        check("C-5 a TRAIN item in <no-routing-row> is printed (1) and fitted; EVAL count printed 0",
              "G14 tree cells: TRAIN items of mc6 in <no-routing-row>: 1 (fitted as their own cell)" in so_t.getvalue()
              and "G14 tree cells: EVAL items of the scoring set in <no-routing-row>: 0 (must be 0)" in so_t.getvalue()
              and NO_ROUTING_ROW in rt["policy"]["tree_cell"])
        # G14 RULING (b): two "multi-class" items (one EVAL, one TRAIN) present with their modal cells (here a cell of another
        # source, as a tie of two rows under two classes can give): [G14-IDENTITY] passes on the FULL set (C1 = the fixture's
        # record digits) and both items are scored; a <multi-class> cell is refused at load
        ev_ids = sorted(it["id"] for it in mc6 if it["side"] == "EVAL")
        mc_ev1, mc_tr1 = ev_ids[1], sorted(it["id"] for it in mc6 if it["side"] == "TRAIN")[1]
        cfg_m = g14_cfg("g14_multi", lambda it: "OTHER/modal" if it["id"] in (mc_ev1, mc_tr1) else "%s/%s" % (it["src"], it["dom"]))
        with contextlib.redirect_stdout(io.StringIO()):
            rm_ = mode(cfg_m, "U", False)
        mtxt = open(cfg_m.out_u, encoding="utf-8").read()
        check("G14 ruling (b): with the multi-class items present, [G14-IDENTITY] passes (C1 %s [%s, %s] REPRODUCED on the full set)"
              " and both items are scored" % ident_fx,
              "REPRODUCED to the printed digits" in mtxt and rm_["st"]["C1"]["lo"] == c1_ref["lo"] and rm_["st"]["C1"]["hi"] == c1_ref["hi"]
              and mc_ev1 in rm_["D"].items and mc_tr1 in rm_["D"].items and len(rm_["D"].items) == len(ri["D"].items))
        pth_m, sh_m = tree_file("g14_multicell", lambda it: MULTI_CLASS if it["id"] == mc_ev1 else "%s/%s" % (it["src"], it["dom"]))
        try:
            load_tree_cells(pth_m, sh_m); check("G14 ruling (b): a <multi-class> cell refuses", False)
        except SystemExit as e:
            check("G14 ruling (b): a <multi-class> cell refuses at load ([G14-MULTI])", str(e).startswith("[G14-MULTI] tree-cells file")
                  and mc_ev1 in str(e))
        # rp12-r2-lane: G14's lane guard and output dir (lane r1 = OUT_DIR, unchanged)
        class _A:
            tree_cells, tree_cells_sha256, leg, dry_run, run = "experiment_results/archv2/rp12/g14/cells.tsv", "0" * 64, "U", True, False
        for lane_, needle in (("r2", "--tree-cells experiment_results/archv2/rp12/g14/cells.tsv is an object of lane r1, the run is lane r2"),):
            _A.lane = lane_
            try:
                g14_configure(_fixture_cfg(tmp, spec, "g14_lane"), _A); check("G14 lane guard refuses", False)
            except SystemExit as e:
                check("G14 lane guard: an R1 tree-cells file in lane r2 refuses", needle in str(e))
        _A.lane, _A.tree_cells = "r1", "experiment_results/archv2/rp12_r2/g14/cells.tsv"
        try:
            g14_configure(_fixture_cfg(tmp, spec, "g14_lane1"), _A); check("G14 lane guard refuses (r1)", False)
        except SystemExit as e:
            check("G14 lane guard: an R2 tree-cells file in lane r1 refuses", "is an object of lane r2, the run is lane r1" in str(e))
        check("G14 output dir per lane: r1 = OUT_DIR, r2 = experiment_results/archv2/rp12_r2/g14",
              g14_out_dir("r1") == OUT_DIR and g14_out_dir("r2") == os.path.join(ROOT, "experiment_results", "archv2", "rp12_r2", "g14"))
        pth_, sh_ = tree_file("g14_pin", lambda it: it["src"])
        try:
            load_tree_cells(pth_, "0" * 64); check("G14 pin refuses", False)
        except SystemExit as e:
            check("G14 pin refuses a wrong sha", str(e).startswith("[G14-PIN] tree-cells file") and "!= the pinned 0000" in str(e))
        crp = pth_ + ".crlf"
        with open(crp, "wb") as f:
            f.write(open(pth_, "rb").read().replace(b"\n", b"\r\n"))
        check("G14 pin: the CRLF rendering loads to the LF pin", load_tree_cells(crp, sh_)[0] == load_tree_cells(pth_, sh_)[0])
        # (4) verdict branches and boundaries (synthetic contrasts)
        g_ = lambda pt, lo, hi: dict(point=pt, lo=lo, hi=hi, se2=0.006, pct=(lo, hi), se_iid=0.005, n=5907, deff=1.27, n_eff=4650, mde=0.0173, var2=3.6e-5)
        def g14w(g, m=None):
            with contextlib.redirect_stdout(io.StringIO()):
                L_, w_ = verdict_lines_g14(dict(C1=g_(0.0267, 0.0146, 0.0389), G=g, M=m or g_(-0.002, -0.01, 0.006), identity=G14_IDENTITY))
            return w_["G14"], "\n".join(L_)
        v_h, t_h = g14w(g_(0.025, 0.013, 0.037))
        v_f, _ = g14w(g_(-0.01, -0.02, 0.0))
        v_u, _ = g14w(g_(0.01, 0.0, 0.02))
        v_u2, t_u2 = g14w(g_(0.05, -0.001, 0.101), g_(0.02, 0.0, 0.04))
        check("G14 verdicts: lo > 0 HELD; hi = 0 FAILED; lo = 0 UNDETERMINED; an interval across 0 UNDETERMINED",
              (v_h, v_f, v_u, v_u2) == ("HELD", "FAILED", "UNDETERMINED", "UNDETERMINED"))
        check("G14 P5 lines by value: +2.50pp in [+1.3, +3.7] HELD, -0.20pp in [-1.0, +0.6] HELD; +5.00pp FAILED, +2.00pp FAILED",
              "P5 G_tree = +2.5pp [+1.3, +3.7]: observed +2.50pp -> HELD" in t_h and "P5 M = -0.2pp [-1.0, +0.6]: observed -0.20pp -> HELD" in t_h
              and "P5 G_tree = +2.5pp [+1.3, +3.7]: observed +5.00pp -> FAILED" in t_u2 and "P5 M = -0.2pp [-1.0, +0.6]: observed +2.00pp -> FAILED" in t_u2
              and "P5 'G14 HELD' (probability 0.85): observed HELD" in t_h)
        # --- mutants: each must be KILLED by the selftest's own checks (a SystemExit counts only when it is the expected one)
        counter = [0]
        def fresh(**kw):
            counter[0] += 1
            return _fixture_cfg(tmp, spec, "mut%d" % counter[0], **kw)
        def m_point():
            r = mode(fresh(), "U", False)
            return not (r["policy"]["best_single"] == best and abs(r["st"]["C1"]["point"] - (td - bs)) < 1e-12
                        and r["D"].n_eval == nev and r["D"].n_train == ntr)
        def m_units():
            c = fresh(); s = dict(e=True, t=True)
            def hk(D_, wt, v):
                ce = defaultdict(set)
                for j, k in enumerate(D_.E): ce[D_.comp[k]].add(v[j])
                if any(len(x) > 1 for x in ce.values()): s["e"] = False
                ct = defaultdict(set)
                for k in D_.T: ct[D_.comp[k]].add(int(wt[k]))
                if any(len(x) > 1 for x in ct.values()): s["t"] = False
            c.hook = hk; mode(c, "U", False)
            return not (s["e"] and s["t"])
        def m_order():
            EVENTS.clear(); mode(fresh(), "U", False)
            return not (EVENTS.index("policy_written") < EVENTS.index("open:eval:route"))
        def m_placebo():
            r = mode(fresh(), "U", False)
            return r["D"].g_plac.tolist() == r["D"].g_tdom.tolist()
        def m_cells():
            r = mode(fresh(), "U", False)
            return "MATH/tiny" in r["cells"] or len(r["cells"]) != 7
        def m_p95():
            p = mode(fresh(), "U", False)["st"]["C2"]
            return abs(p["null_p95"] - sorted(p["null_reads"])[18]) > 1e-15
        def m_jk():
            p = mode(fresh(), "U", False)["st"]["C2"]
            return p["lo"] == p["lo_fx"] and p["hi"] == p["hi_fx"]
        def m_marker():
            c = fresh(); mode(c, "U", False); os.remove(c.out_u); os.remove(c.policy_path)
            mode(c, "U", False)
            return True                                       # a second EVAL read went through: the defect is observed
        def m_write():
            pth = os.path.join(tmp, "ww%d.txt" % counter[0]); counter[0] += 1
            write_outcome(pth, "a"); write_outcome(pth, "b")
            return True                                       # the overwrite went through: observed
        def m_c0():
            mode(fresh(c0u=lambda s: dict(best="x", bs="0.1", tdom="0.2")), "U", False)
            return True                                       # no refusal on a C0 miss: observed
        def m_deff():
            r = mode(fresh(), "U", False); bt_ = r["bt"]
            d2_ = bt_["two"][:, 0, TDOM] - bt_["two"][:, 0, BS]; di_ = bt_["iid"][:, 0, TDOM] - bt_["iid"][:, 0, BS]
            return abs(r["st"]["C1"]["deff"] - np.var(d2_, ddof=1) / np.var(di_, ddof=1)) > 1e-9
        def m_history():
            return any("history" in v for v in mode(fresh(), "M", False)["admitted"].values())
        def m_k37():
            c = fresh(); c.k37_sha = "0" * 64; mode(c, "M", False)
            return True                                       # a wrong roster sha was admitted: observed
        def m_strict():
            return r_verdict(base_p(0.5, 0.4, 0.5, 0.5)) != "FAILED"
        def m_t1():
            return verdict_lines_u(dict(cases[3]))[1]["C1"] != "VOID"
        def m_tie():
            Dt.fit_asserts = 0
            return fit(Dt, np.array([1, 1, 1])).gb != 0
        def m_sqlscope():
            r = mode(fresh(), "U", False)
            return r["kst"]["train"]["key_rows_fetched"] != in_tr
        def m_dry():
            mode(fresh(), "M", True)
            return False
        MUTS = [("fit_on_eval", lambda: mode(fresh(), "U", False) and False, "[G3(4)]"), ("tie_last", m_tie, None),
                ("no_overlay", m_point, None), ("multi_last_wins", m_point, None), ("gate_side", m_point, None),
                ("eval_item_unit", m_units, None), ("train_unit_ignored", m_units, None), ("b3_reorder", m_order, None),
                ("placebo_identity", m_placebo, None), ("floor_off", m_cells, None), ("p95_max", m_p95, None),
                ("jk_fixed_decides", m_jk, None), ("marker_off", m_marker, None), ("write_w", m_write, None),
                ("c0_not_checked", m_c0, None), ("deff_inverse", m_deff, None), ("history_kept", m_history, None),
                ("k37_sha_off", m_k37, None), ("strict_hi", m_strict, None), ("t1_ignored", m_t1, None),
                ("dry_reads_key", m_dry, "[KEY-TRIPWIRE]"), ("sql_unfiltered", m_sqlscope, None)]
        for name, fn, expect_exit in MUTS:
            MUTANT = name
            msg = ""
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    k = bool(fn())
            except SystemExit as e:
                msg = str(e)
                k = bool(expect_exit) and expect_exit in msg
            finally:
                MUTANT = None
            check("MUTANT %-20s killed%s" % (name, "" if k else " -- SURVIVED (%s)" % msg[:90]), k)
        miss = BR.missing()
        check("every declared print branch executed (%d / %d); missing: %s" % (len(BR.declared) - len(miss), len(BR.declared), miss), not miss)
    finally:
        for r_, ds, fs in os.walk(tmp):
            for f in fs:
                try:
                    os.chmod(os.path.join(r_, f), stat.S_IWRITE)
                except OSError:
                    pass
        shutil.rmtree(tmp, ignore_errors=True)
    n_fail = sum(1 for _, ok in checks if not ok)
    n_mut = sum(1 for n, _ in checks if n.startswith("MUTANT"))
    n_kill = sum(1 for n, ok in checks if n.startswith("MUTANT") and ok)
    print("SELFTEST %s: %d checks, %d failed; mutants %d / %d killed; %.1fs" % ("PASS" if n_fail == 0 else "FAIL", len(checks), n_fail,
                                                                              n_kill, n_mut, time.time() - t0))
    return 0 if n_fail == 0 else 1


def g14_out_dir(lane):
    """rp12-r2-lane: lane r1 writes G14's files where it always did (OUT_DIR); lane r2 under experiment_results/archv2/rp12_r2/g14."""
    import rp12_lane as LN
    return OUT_DIR if lane == "r1" else LN.out_path(lane, "g14")


def g14_configure(cfg, a):
    """RP12 G14: leg U only, --dry-run or --run only, both flags; the tree-cell arm writes its OWN write-once files."""
    if not (a.tree_cells and a.tree_cells_sha256):
        raise SystemExit("[G14] --tree-cells and --tree-cells-sha256 go together")
    import rp12_lane as LN
    lane = getattr(a, "lane", "r1")
    LN.guard(lane, [("--tree-cells", a.tree_cells)])                                             # rp12-r2-lane
    if a.leg != "U" or not (a.dry_run or a.run):
        raise SystemExit("[G14] the tree-cell arm runs with --leg U and --dry-run or --run only")
    cfg.tree, cfg.tree_desc = load_tree_cells(a.tree_cells, a.tree_cells_sha256)
    cfg.g14_identity = G14_IDENTITY
    od = g14_out_dir(lane)
    cfg.policy_path = os.path.join(od, "v2_declared_cells_G14_train_policy.json")
    cfg.out_u = os.path.join(od, "v2_declared_cells_G14_outcome.txt")
    cfg.mark_u = os.path.join(od, "v2_declared_cells_G14.READ_STARTED")
    return cfg


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--dry-run", action="store_true")
    g.add_argument("--c0", action="store_true"); g.add_argument("--run", action="store_true")
    ap.add_argument("--leg", choices=("U", "M", "both"), default=None)
    ap.add_argument("--tree-cells", default=None, help="RP12 G14: the tree-cells TSV (leg U, --dry-run / --run only)")
    ap.add_argument("--tree-cells-sha256", default=None, help="RP12 G14: sha256 of the tree-cells file's LF rendering")
    ap.add_argument("--lane", choices=("r1", "r2"), default=None, help="RP12 lane of the G14 tree-cell arm (with --tree-cells only)")
    a = ap.parse_args()
    if a.lane is not None and a.tree_cells is None:
        raise SystemExit("[G14] --lane goes with --tree-cells only (the pre-RP12 legs have no lane)")
    a.lane = a.lane or "r1"
    for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        if os.environ.get(k) != "1":
            print("[W12] %s is %r (the run-operator sets 1; single-threaded)" % (k, os.environ.get(k)))
            if a.c0 or a.run:                                    # READY e451753 D7: refuse, never only warn, on a real read
                raise SystemExit("[W12] --c0 / --run refused: %s is %r, not '1' (export it before starting python)" % (k, os.environ.get(k)))
    if a.selftest:
        sys.exit(selftest())
    refuse_mutant()
    cfg = real_cfg()
    if a.tree_cells is not None or a.tree_cells_sha256 is not None:      # RP12 G14 (absent = every mode unchanged)
        g14_configure(cfg, a)
    if a.dry_run:
        for leg in (("U", "M") if a.leg in (None, "both") else (a.leg,)):
            mode(cfg, leg, True)
            print()
        return
    if a.leg not in ("U", "M"):
        raise SystemExit("--c0 / --run need --leg U or --leg M (each leg reads EVAL once, B1)")
    if a.c0:
        say = lambda s: print(s, flush=True)
        header(cfg, a.leg, say)
        if a.leg == "U":
            got = c0_compare_u(cfg.c0_u(say))
            print("C0-U: best single %s %s, TRUE (source, domain) %s -> HELD" % (got["best"], got["bs"], got["tdom"]))
        else:
            got = c0_compare_m(cfg.c0_m(say))
            print("C0-M: K12 interaction-only R %s -> HELD" % got)
        return
    mode(cfg, a.leg, False)


if __name__ == "__main__":
    main()
