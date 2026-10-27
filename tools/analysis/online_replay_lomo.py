"""online_replay_lomo.py: ONLINE-REPLAY-LOMO (stage 1, no build) -- leave one union member out, replay its items into the other
five members' AF-U trees online (flatLeaf filing, OOS / margin buffering, sequential leaf-mean refit on fixed topology, buffer
k-means at the member's batch leaf count), and compare with the batch AF-U (which includes the member) on filing (OL1) and on the
in-members' cell-id stability (OL2), with a per-source k-means arm through every step. ZERO calls: no judge, no LLM, no embedding
call, no construction, no Gradle. Readers only (every DB mode=ro through data_v2.ro.open_ro).

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — ONLINE-REPLAY-LOMO (stage 1, no build): when one
  union member is left out ..." SECTION SPAN L23944-L23958 (_as_of 964511fd, parent b9b67b11): OL1, OL2, Support (a)-(g), P1-P3,
  F-OL. Record L23939-L23942 (conditional reading) with its bracket: CONDITION RESOLVED by OOS-TREE-CELLS OT1 EQUIVALENT
  (programme L23975-L23987), so the OOS-based legs are read as written. Results record docs/agents/results/ONLINE-REPLAY-LOMO.json.
  --run REFUSES unless a LINE of the programme starts with the registered heading (REG_RE, line-anchored).

INSTRUMENT (imported unchanged; LF git blobs asserted BEFORE import, another blob REFUSES):
  tools/analysis/union_af_route.py blob:bf3f17dbdc42dbfc6803687d8739d459fc1ed75d (load_inputs: the inputs manifest and every
      pinned AF-U / inputs file re-hashed; us_fit: the per-source k-means K_0; input_paths; reg()['single'] layout; _texts_vectors /
      _sides: rp12_pairing's P4 text / vector readers and the side export; header's identity_line)
  tools/analysis/g13_breakdown.py  blob:c29fa1c3d3b7837ede6c53f1b98bf32dcd97ca40 (pool_check_v2 = the B0-2 pv2 pool check;
      last_snapshot; majority; name_clusters; ukm_fit; stat = the whole-component bootstrap, B 2,000, seed 20260929)
  fitset_faithful.py's refit is NOT imported: it re-fits leaf means in batch from labelled TRAIN at 4096-d (P7 / FITSET; the
  registration's WILL-NOT-SHOW: "label-free gains from refit on MMLU-Pro (P7 / FITSET used labels)"); the registered refit here is
  the ONLINE sequential mean (the note's operation 3), implemented in replay() (deviation from the brief stated).
  oos_tree_cells / oos_baselines are not imported (their CLINC loaders and pins do not apply); their two rules are copied and
  named: the GATE threshold (OB.threshold: tau = sort(scores)[floor((1 - 0.95) n)], ">= 95% of GATE in-scope scores >= tau") and
  the TOST verdict form (OB.ob_status: point +/- 1.645 SE strictly inside the margin; DIFFERENT iff |point| > margin AND point +/-
  1.96 SE excludes 0). auroc = intent_transfer_s0.auroc's rule (P(pos > neg) + 0.5 P(tie)), unweighted.

LAUNCH SEQUENCE (the run-operator; zero calls; never beside a construction (rule 7): every mode except --selftest / --mutants is
a pool reader):
  python tools/analysis/online_replay_lomo.py --selftest
  python tools/analysis/online_replay_lomo.py --mutants
  python tools/analysis/online_replay_lomo.py --dry-run        # POOL line first; pins; denominators; identities; GATE thresholds per
                                                               #   replay and arm; writes nothing; no EVAL statistic of the replay
  python tools/analysis/online_replay_lomo.py --run            # the outcome of record, WRITE-ONCE (mode "x"):
       experiment_results/online_replay_lomo/outcome.txt and online_replay_items.csv (never committed: sha256 + backup)
  --data-root <dir>: the root under which experiment_results/ and the DBs are read and the outputs written (default: the checkout
  holding this file). It sets TAXOARENA_DATA_ROOT / TAXOARENA_RESULTS_ROOT INSIDE this process before the readers import (no
  env-var prefix is needed or read for the run of record).

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, nothing written):
  (1) POOL line (B0-2 pool check pv2_1575de61bb20e977; rc != 0 REFUSES); write-once paths absent; the registered heading present.
  (2) union_af_route.load_inputs: the inputs manifest (53021e26...) and every pinned AF-U / inputs file EQUAL; the snapshot leaf
      counts = the manifest's ksrc (BBH 36, GPQA 4, IFEVAL 1 (one-cell), MATH 10, MMLU_PRO_LB 69, MUSR 3; total 123).
  (3) the bundle (6,139 EVAL / 5,628 components / 12,334 TRAIN; refused otherwise); GATE items from the merged validation CSV by the
      side export (multi-class excluded); every GATE vector read by rp12_pairing's reader, AND every bundle row re-read by the same
      reader must equal the bundle (max |diff| <= 1e-9; [ORL-VEC] otherwise).
  (4) IDENTITY before any replay ([ORL-IDENTITY] otherwise): flatLeaf in 256-d (argmax cos to the snapshot vmfMu; the one-cell
      member filed by source) reproduces af_cells.tsv on every EVAL item (I3's 0.1% bar); the engine-named batch filing equals the
      bundle's eval_fl item by item; P_fl(AF-U) "%.4f" = 0.7346 and the mirrored batch k-means P(US_0) "%.4f" = 0.7368 (UNION-AF-ROUTE
      outcome lines 205 / 208); K_0's TRAIN labels = k_cells_s0.tsv item by item.
  (5) six replays x two arms (replay()); OL1, OL2, F-OL, P1-P3, descriptive lines; outcome + items CSV written mode "x".

READINGS (stated, for the READY to confirm or refuse; none chosen silently):
  OL-R1 Cells. Tree arm: a split member's cells = its last-snapshot leaves (vmfMu, 256-d, unit; n = directQueries, the engine's
        count the mean was fitted on); the one-cell member's cell (IFEVAL:n00000001, the author's decision, L23660-L23667) = the
        unit mean of its TRAIN rows, n = its TRAIN count. k-means arm: K_0 = union_af_route.us_fit seed 0 (UNION-AF-ROUTE's K_0 /
        AK2 US_0 at ksrc), n = TRAIN items per centre. ONLINE filing is flatLeaf over every current cell, the one-cell member's
        included (an online item has no source oracle); the BATCH arms keep UNION-AF-ROUTE's mirrored filing (C-S1: the one-cell
        source filed by source). Disclosed in the outcome.
  OL-R2 Thresholds per replay and per arm, on the five in-members' GATE items against that arm's five-member cells before the
        replay: tau_oos = the TPR-0.95 order statistic of max-cos (OB.threshold); tau_m = the same order statistic at 0.20 of the
        margin (top-1 minus top-2 cos), i.e. "GATE p20" as sort(margin)[floor(0.20 n)]. Buffered iff max-cos < tau_oos OR margin <
        tau_m (strict; equality files).
  OL-R3 Stream: one fixed order per replay, numpy default_rng(20261003) fresh per replay: a permutation of m's TRAIN rows, then a
        permutation of m's EVAL rows (TRAIN first, as registered). A filed item updates its cell by the sequential mean mbar +=
        (x - mbar) / (n + 1), n += 1, cosine against mbar / |mbar|. The same order and rule in both arms.
  OL-R4 Buffer: spherical k-means (g13_breakdown.ukm_fit, seed 0, max_iter 300) at k = min(L_m, buffer size), L_m = m's batch
        leaf count (ksrc[m]; 1 for IFEVAL); provisional cells, uncertified; no buffer -> no new cell.
  OL-R5 Naming (G13's P_fl: the TRAIN-majority declared class of the filed cell). Batch AF-U: the engine's leaf_dominant (as in
        eval_fl); batch k-means: name_clusters. Online: an existing cell keeps its batch name unless one class of m's TRAIN items
        absorbed into it STRICTLY exceeds the batch majority count (AF-U: round(profile_size x leaf_purity) of the leaves CSV;
        k-means: the TRAIN count of its majority class); m's classes are disjoint from the in-members', so this is the TRAIN
        majority of (batch profile + absorbed) with ties kept by the incumbent. A buffer cell is named by the TRAIN majority of the
        buffered TRAIN items its fit labels assign to it (tie: the smaller class name); none -> <empty> (never correct).
  OL-R6 m's EVAL items are filed at the END of the stream by flatLeaf over all cells (updated leaves + buffer cells), as
        registered; OL1's D is item-paired with the batch arm's correctness on the same item and pooled over the 6 replays in the
        bundle's EVAL order (each item held out exactly once; checked).
  OL-R7 OL1 interval form = OOS-BASELINES' TOST form with SE = the whole-component bootstrap SD (g13_breakdown.stat; B 2,000, seed
        20260929, CK-CLOSE components = eval_comp): EQUIVALENT iff D +/- 1.645 SE lies strictly inside (-0.020, +0.020); DIFFERENT
        iff |D| > 0.020 AND D +/- 1.96 SE excludes 0 (LOSS if D < 0, GAIN if D > 0); NEITHER otherwise. The percentile 95% interval
        is printed beside (descriptive).
  OL-R8 OL2 churn per replay = the share of the five in-members' EVAL items whose cell id differs between flatLeaf over the
        five-member cells BEFORE the stream and flatLeaf over ALL cells AFTER it (updated leaves + the new buffer cells: a move to a
        buffer cell is an address change); its 95% upper bound = the percentile upper of g13_breakdown.stat on the 0/1 churn vector
        (components resampled). STABLE iff every replay's upper <= 0.020; NOT-STABLE iff any replay's point > 0.020; UNDETERMINED
        otherwise. If both STABLE and NOT-STABLE conditions held on the same data (a percentile upper below its point), the reader
        REFUSES ([ORL-OL2-BOTH]) instead of choosing: a registration matter for the registrar. Churn over the updated leaves only
        (buffer cells excluded) printed beside.
  OL-R9 Predictions: numeric bands HELD iff the point lies in the closed interval; P2 "per replay" HELD iff all six replays' churn
        points lie in [0.000, 0.015]; P3 the median (numpy, mean of the middle two) of the six AUROCs; probability statements scored
        by Brier over the named outcomes (OL1: LOSS 0.45, NEITHER 0.40, EQUIVALENT 0.15, GAIN 0.00 implied; OL2: STABLE 0.80 vs not).
  OL-R10 New-domain OOS AUROC per replay (descriptive): positives = the in-members' EVAL items, negatives = m's EVAL items, score =
        max-cos to the arm's five-member cells before the stream (higher = in-scope).
  OL-R11 Decision churn (descriptive): routed model = UNION-AF-ROUTE's frozen TRAIN policy (scratch/union_af_route_train_policy.json,
        never committed; tree_cell for AF cells, xtree_cell K0 for K_0 cells); a cell absent from the policy (every buffer cell)
        routes to its absent_group (the best single). Absent policy file -> "NOT COMPUTED" (descriptive only).
  Not applicable (stated): no judge verdict enters (declared-class keyed end to end): no wrong(established) count, no tie convention
  A / B, no call cache, no --pilot / truncation guard.

SELFTEST (--selftest; synthetic worlds; the real entry points run() / dry_run() executed with the loader hook swapped for the
fixture's parts and build_world() / replay() / compute() / the verdict and print code all real):
  branches     ol1_word / ol1_of / ol2_word / ol2_of / f_ol / prediction / Brier lines by VALUE at every boundary (strict 0.020 TOST
               ends, |D| = 0.020, 95% touching 0, upper exactly 0.020, point exactly 0.020, the both-fire refusal, the SD vs the
               percentile width, a second-replay-only miss, median vs mean of three AUROCs); every print branch on synthetic R
  e2e_sep      'sep' (held-out source orthogonal to the rest): every item buffered, buffer k-means recovers its classes; printed
               D +0.0000, churn 0.0000, OL1 EQUIVALENT, OL2 STABLE, F-OL NOT FIRED, P1 / P2 HELD at the band end; outcome file's
               first line the POOL line; items CSV row count
  e2e_absorb   'absorb' (absorption, margin-only buffering, renaming checks, mean motion and buffer capture flipping boundary items):
               every threshold / buffer count / buffer k / churn point / churn 95% upper / pooled D equal to an INDEPENDENT plain-loop
               oracle (_oracle_replay; the upper = g13_breakdown.stat on the oracle's vector) for both arms; OL1 LOSS, OL2
               NOT-STABLE, F-OL FIRES and the LOSS-limit line asserted on the printed text; AUROC = a pairwise count
  e2e_misname  batch tree and batch k-means differ (an engine name off): D = the misnamed class share, oracle agreement
  e2e_nobuf    the empty-buffer path (GATE off every axis): no buffer, k 0, purity n/a, oracle agreement
  e2e_stiff    tree churn != k-means churn: the deciding OL1 / OL2 / F-OL blocks print the TREE arm (position-checked)
  e2e_evalheavy buffer naming reads TRAIN only (a class with 1 TRAIN, 12 EVAL items); the absent-policy path (NOT COMPUTED x 8)
  race         a file appearing after the write-once pre-check is never overwritten (mode "x"); no items CSV written
  identity     build_world refusals: tampered eval_fl, misfiled af cells (I3), P_fl / P(US_0) strings, K labels, denominators, ksrc
  write_once   second --run refused, the outcome unchanged; an existing items CSV refused before the pool check; registration heading
               absent refused; POOL check rc 1 refused with the POOL line first; nothing written by any refusal
  dry_run      POOL line first; denominators (the fixture's and the REAL constants'); thresholds = replay()'s; nothing written; no
               OL1 / OL2 / F-OL / churn / prediction text
  branch_cover every registered print branch and refusal hit across the cases (HIT registry)
MUTANTS (--mutants; each edits the code above MUTANTS in memory and re-runs the selftest; 2026-10-03 at this commit): 44 of 44
KILLED, control (no edit) survived. First pass 15 of 35 (13 patterns also matched the MUTANTS literal: search scope fixed; M11 margin
trigger, M18 batch arm, M23 P2 first-replay, M25 mode "w", M34 point / upper survived) -> second pass 36 of 40 (M20 k-means block
deciding, M24 mean vs median, M33 EVAL naming, M37 percentile SE survived) -> cases e2e_misname / e2e_nobuf / e2e_stiff /
e2e_evalheavy / race and the ol1_of / ol2_of helpers added -> 44 of 44. Classes: verdict boundaries M01-M08, M36, M37; thresholds and
population / split side M09, M10, M35, M41; buffer and refit rules M11-M15, M33, M40, M42; filing and churn M16, M17, M43, M44; batch
arm / arm swap M18, M20; stream order M19; pooled denominator M38; churn bootstrap components M39; one-cell graft M31; skip paths and
lines M21; predictions M22-M24, M30; write-once M25, M26; identities and gates M27, M28, M32; AUROC sign M29.
BUILD-TIME CHECK (2026-10-03, file-only, zero DB reads, no replay statistic): load_parts + build_world on the real pinned inputs with
the vector reader stubbed by the bundle rows: inputs manifest 53021e26... 18 AF-U files and 11 inputs EQUAL; flatLeaf 256-d = af_cells
on 6139 of 6139 EVAL; engine naming = eval_fl on all; P_fl(AF-U) 0.7346; K_0 TRAIN labels = k_cells_s0 on all 12334; mirrored
P(US_0) 0.7368; GATE 2028 items (BBH 565, IFEVAL 54, MUSR 73, MMLU_PRO_LB 1152, MATH 131, GPQA 53); 123 cells per arm. The real
--dry-run (pool check + DB reads) was NOT run: a site null (certPcK2) was running (rule 7); the run-operator runs it first.
[DELTA 2026-10-03, docs/reviews/READY_online_replay_lomo.md (NOT READY on 69cd6d4c) C-1..C-3, D-3..D-5, path (a); insertion only:
where this block and the readings above disagree, THIS block is the code's behaviour]
  C-1 (OL-R1 n, OL-R3 init): the online mean of every cell starts at the TRUE mean of its unit TRAIN rows: n = the cell's TRAIN count
      (tree: af_cells.tsv TRAIN cell, the one-cell member all its TRAIN; K_0: its fit labels), length r = |sum| / n, direction the
      engine's vmfMu (tree) / the K_0 centre, so the five-member graft routes exactly as before (I3 unchanged); routing renormalises
      mbar only for the cosine. Real inputs: r median 0.691 (min 0.527, max 0.964), n / directQueries median 0.975; K_0 r median 0.693.
      The unit-initialised replay (the first build) is printed beside: D and both churns (DESCRIPTIVE). [ORL-INIT] refuses a TRAIN
      row with no tree cell or a cell with no TRAIN row. update_rule asserts mbar = (r n mu + sum x) / (n + k) after k absorptions.
  C-2 (OL-R1 filing): the DECIDING batch arm files by flatLeaf over ALL six members' cells (the one-cell cell = its unit TRAIN
      mean, reachable by any item), the rule the online arm uses: batch P_fl(AF-U) 0.7265 (READY H4, reproduced on the real inputs;
      [ORL-IDENTITY] otherwise) and P(US_0, nearest of all) 0.7289 (UNION-AF-ROUTE outcome line 209; reproduced). The mirrored filing
      (eval_fl 0.7346 / P(US_0) 0.7368, still identity-checked) is printed beside with its D and form-word, and D pooled over the
      split members' replays only (one-cell replays excluded), all DESCRIPTIVE.
  C-3 (OL-R8): the DECIDING churn is the registration's "five-member graft before and after the replay": flatLeaf over the five
      members' cells before vs the same cells with their online-updated means after (means-only; buffer cells are not part of the
      five-member graft); F-OL then reads as registered ("online mean refit moves existing cells' addresses beyond 2%"). The all-cells
      churn (moves into the provisional buffer cells) is printed beside with the OL2 rule applied to it (DESCRIPTIVE); when it alone
      exceeds 0.020 the outcome prints "BUFFER CAPTURE (DESCRIPTIVE): beyond 2% by buffer capture ..." and F-OL does not fire on it.
      [ORL-OL2-BOTH] stays a refusal, not a criterion (READY R8).
  D-4: OL2's denominator line prints the measured per-replay range (2,661-5,977 on the real data) beside the registered "about 5,100".
  D-5: the outcome discloses the transductive EVAL stream and the 15 / 14 MATH-MMLU_PRO_LB text-shared multi-class residual.
  BRACKETS STILL NEEDED FROM THE REGISTRAR (pre-data), after this delta:
      OL-R1: YES (the symmetric batch filing now decides OL1, mirrored beside; n = the TRAIN count, not directQueries).
      OL-R3: YES, reduced: the stream order / seed reading, and the C-1 initialisation (true-mean length, vmfMu direction).
      OL-R5: YES (online naming: incumbent kept on ties, buffer TRAIN majority, <empty> never correct) -- unchanged by the delta.
      OL-R8: YES (means-only churn decides; all-cells churn and the capture line descriptive; the both-fire refusal).
      OL-R2 (GATE p20 order statistic, per-arm thresholds, strict buffering), OL-R4 (k = min(L_m, buffer), seed 0), OL-R9 (Brier
      with GAIN 0.00 implied; P2 all six in band): YES, LOW. OL-R6, OL-R7, OL-R10, OL-R11: no.
  Selftest after the delta: 15 cases (new: e2e_motion = means-only NOT-STABLE / F-OL FIRES on the mean refit; update_rule; e2e_broad
  = symmetric and mirrored batch differ; e2e_absorb now = buffer capture only: OL2 STABLE, the capture line, F-OL NOT FIRED; e2e_stiff
  re-built on a tilted leaf; identity adds the two symmetric strings and [ORL-INIT]).
  MUTANTS after the delta: 59 of 59 KILLED, control survived: M01-M44 (M16 / M44 re-targeted to the means-only churn), M45-M53
  (C-1 unit init, n = directQueries, O3 renormalised mean, C-2 mirrored deciding, symmetric batch without the one-cell cell, capture
  line dropped, F-OL on all-cells churn, k-means r = 1, mirrored D against the symmetric batch), and the reviewer's O1, O2, O4, O5
  (seed varying by replay), O7, O8 (all KILLED; O3 = M47; O6 not added: equality with an order statistic has measure zero). First
  delta pass: M48 / M53 survived (no fixture where the batch filings differ), O5 pattern ambiguous -> e2e_broad added, O5 anchored -> 59 / 59.
  NOT RUN in this delta: the real --dry-run (a java site null was running again, rule 7); the file-only harness reproduced every
  identity above, including 0.7265 / 0.7289, on the real pinned inputs with no DB read.
"""
import os
import sys


def _preparse_root(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


_HERE0 = os.path.dirname(os.path.abspath(__file__))
_ROOT0 = os.path.dirname(os.path.dirname(_HERE0))
_DR = _preparse_root(sys.argv[1:]) if __name__ == "__main__" else None
if _DR:
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_DR)
    os.environ["TAXOARENA_RESULTS_ROOT"] = os.path.abspath(_DR)

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import io            # noqa: E402
import re            # noqa: E402
import json          # noqa: E402
import shutil        # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
import tempfile      # noqa: E402
import contextlib    # noqa: E402
from collections import Counter, defaultdict  # noqa: E402

import numpy as np   # noqa: E402

HERE = _HERE0
ROOT = _ROOT0
sys.path.insert(0, HERE)

TAG = "[ORL]"
TEST_ID = "ONLINE-REPLAY-LOMO"


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def sha256_lf(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def sha256_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


PINS = (("union_af_route.py", "bf3f17dbdc42dbfc6803687d8739d459fc1ed75d"),
        ("g13_breakdown.py", "c29fa1c3d3b7837ede6c53f1b98bf32dcd97ca40"))
for _name, _pin in PINS:
    _p = os.path.join(HERE, _name)
    if blob_lf(_p) != _pin:
        refuse("%s is blob:%s, not the pinned blob:%s" % (_p, blob_lf(_p), _pin))
import union_af_route as UA      # noqa: E402  (checks its own pins: g13_breakdown, g13_comparator, rp12_pairing, v2_declared_cells)
GB = UA.GB
RP = UA.RP
FM = UA.FM

POOL = "pv2_1575de61bb20e977"
OUT_REL = "experiment_results/online_replay_lomo"
OUTCOME, ITEMS_CSV = "outcome.txt", "online_replay_items.csv"
PROGRAMME = os.path.join(ROOT, "docs", "judge_v2_program.md")
REG_HEADING = ("## Registered 2026-10-03 (before any code or call) \u2014 ONLINE-REPLAY-LOMO (stage 1, no build): when one union "
               "member is left out")
REG_RE = re.compile(r"^" + re.escape(REG_HEADING), re.M)
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) \u2014 ONLINE-REPLAY-LOMO (stage 1, no '
            'build): when one union member is left out ..." L23944-L23958 (_as_of 964511fd, parent b9b67b11); condition resolved by '
            'OOS-TREE-CELLS OT1 EQUIVALENT (L23975-L23987): OOS-based legs read as written')
ORDER_SEED = 20261003
KM_SEED = 0
BUF_SEED = 0
TPR = 0.95
P_M = 0.20
MARGIN = 0.020
Z90, Z95 = 1.645, 1.96
EMPTY = -1
ARMS = ("tree", "km")
ARM_NAME = {"tree": "AF-U tree", "km": "per-source k-means K_0"}

# Registered Support (planning numbers, printed beside the measured)
SUPPORT = dict(se=0.00547, deff=1.223, n_eff=5020, n=6139, comp=5628, disc=0.15, tost_reach=0.0064, diff_reach=0.0246,
               ol2_upper=0.007, ol2_n=5100)
PRED_P1 = (-0.030, -0.080, 0.000)
PROB_OL1 = {"LOSS": 0.45, "NEITHER": 0.40, "EQUIVALENT": 0.15, "GAIN": 0.00}
PRED_P2 = (0.004, 0.000, 0.015)
PROB_OL2_STABLE = 0.80
PRED_P3 = (0.80, 0.60, 0.95)

# the registered constants (one dict; the selftest swaps in its fixture's; nothing else writes _REG)
REG = dict(
    pool=POOL, sources=("MMLU_PRO_LB", "BBH", "MATH", "MUSR", "IFEVAL", "GPQA"),
    members=(("bbh", "BBH"), ("gpqa", "GPQA"), ("ifeval", "IFEVAL"), ("math", "MATH"), ("mmlu_pro_lb", "MMLU_PRO_LB"), ("musr", "MUSR")),
    dim=256, n_eval=6139, n_comp=5628, n_train=12334, n_eval_before=6153, comp_before=5642,
    id_p_fl="0.7346", id_p_k0="0.7368", id_p_fl_all="0.7265", id_p_k0_all="0.7289",
    ksrc={"BBH": 36, "GPQA": 4, "IFEVAL": 1, "MATH": 10, "MMLU_PRO_LB": 69, "MUSR": 3},
    policy="experiment_results/archv2/union_af_route/scratch/union_af_route_train_policy.json",
)
_REG = [REG]


def reg():
    return _REG[0]


HIT = Counter()


def hit(name):
    HIT[name] += 1


def data_root():
    return UA._ROOT[0]


def P(rel):
    return os.path.join(data_root(), *rel.split("/"))


def src_of(name):
    return str(name).split("/", 1)[0]


def order_stat(scores, q):
    """OB.threshold's rule at quantile q: sort(scores)[floor(q n)]."""
    s = np.sort(np.asarray(scores, dtype=np.float64))
    return float(s[int(np.floor(q * len(s)))])


def top_margin(S):
    """Row-wise (max, top-1 minus top-2) of a score matrix (one column: margin +inf)."""
    S = np.asarray(S, dtype=np.float64)
    mx = S.max(axis=1)
    if S.shape[1] < 2:
        return mx, np.full(len(mx), np.inf)
    part = -np.partition(-S, 1, axis=1)
    return mx, part[:, 0] - part[:, 1]


def auroc(pos, neg):
    """P(pos > neg) + 0.5 P(tie) (intent_transfer_s0.auroc, unweighted)."""
    pos, neg = np.asarray(pos, dtype=np.float64), np.asarray(neg, dtype=np.float64)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    u, inv = np.unique(np.concatenate([pos, neg]), return_inverse=True)
    Wp = np.bincount(inv[:len(pos)], minlength=len(u)).astype(np.float64)
    Wn = np.bincount(inv[len(pos):], minlength=len(u)).astype(np.float64)
    below = np.cumsum(Wn) - Wn
    return float((Wp * (below + 0.5 * Wn)).sum() / (Wp.sum() * Wn.sum()))


# ── the world: cells, batch arms, identities (pure; the selftest builds parts by hand) ──────────────────────────────────────

def build_world(parts, say):
    """parts -> W. Identity checks of step (4); refuses on any miss."""
    c = reg()
    classes = list(parts["classes"])
    cix = {k: i for i, k in enumerate(classes)}
    sources = tuple(c["sources"])
    single = dict(parts["single"])                         # {source: cell uid}
    Xt, yt = FM.unit_rows(np.asarray(parts["Xt"], dtype=np.float64)), np.asarray(parts["yt"], dtype=int)
    Xe, ye = FM.unit_rows(np.asarray(parts["Xe"], dtype=np.float64)), np.asarray(parts["ye"], dtype=int)
    tsrc = np.array([src_of(classes[i]) for i in yt])
    esrc = np.array([src_of(classes[i]) for i in ye])
    ecomp = np.asarray(parts["ecomp"])
    efl = np.asarray(parts["efl"], dtype=np.int64)
    titems, eitems = list(parts["titems"]), list(parts["eitems"])
    n_e, g_e, n_t = len(ye), len(set(ecomp.tolist())), len(yt)
    if (n_e, g_e, n_t) != (c["n_eval"], c["n_comp"], c["n_train"]):
        hit("REFUSE.DENOM")
        refuse("[ORL-DENOM] the bundle holds EVAL %d / %d components / TRAIN %d, not the registered %d / %d / %d"
               % (n_e, g_e, n_t, c["n_eval"], c["n_comp"], c["n_train"]))
    if set(esrc.tolist()) - set(sources) or set(tsrc.tolist()) - set(sources):
        refuse("items of unregistered sources %s" % sorted((set(esrc.tolist()) | set(tsrc.tolist())) - set(sources)))
    ksrc = dict(parts["ksrc"])
    if ksrc != dict(c["ksrc"]):
        hit("REFUSE.KSRC")
        refuse("[ORL-KSRC] leaf counts %s, not the registered %s" % (ksrc, dict(c["ksrc"])))
    # tree arm cells
    leaves = parts["leaves"]                                # {uid: (mu, n)} of split members
    ldom = parts["leaf_dom"]                                # {uid: (class name or "", dominant count)}
    ids, src, mus, ns, names, cdom = [], [], [], [], [], []
    for so in sorted(sources):
        if so in single:
            uid = single[so]
            m = tsrc == so
            s = Xt[m].sum(axis=0)
            ids.append(uid)
            src.append(so)
            mus.append(s / np.linalg.norm(s))
            ns.append(int(m.sum()))
        else:
            us = sorted(u for u in leaves if u.split(":", 1)[0] == so)
            if len(us) != ksrc[so]:
                refuse("source %s: %d snapshot leaves, ksrc %d" % (so, len(us), ksrc[so]))
            for u in us:
                mu = np.asarray(leaves[u][0], dtype=np.float64)
                ids.append(u)
                src.append(so)
                mus.append(mu / np.linalg.norm(mu))
                ns.append(int(leaves[u][1]))
    for u in ids:
        nm, cnt = ldom.get(u, ("", 0))
        names.append(cix.get(nm, EMPTY))
        cdom.append(int(cnt) if nm in cix else 0)
    tree = dict(ids=ids, src=np.array(src), mu=np.vstack(mus), n=np.array(ns, dtype=np.int64), name=np.array(names, dtype=int),
                cdom=np.array(cdom, dtype=np.int64))
    tpos = {u: k for k, u in enumerate(ids)}
    # C-1 (READY_online_replay_lomo): the online mean starts at the TRUE mean of the cell's unit TRAIN rows (count and sum):
    # n0 = the cell's TRAIN count (af_cells.tsv), r = |sum| / n0; the direction stays the engine's vmfMu (routing unchanged)
    cells_af = parts["cells_af"]
    tsum = np.zeros_like(tree["mu"])
    tcnt = np.zeros(len(ids), dtype=np.int64)
    for j, it in enumerate(titems):
        u = single.get(tsrc[j]) if tsrc[j] in single else cells_af.get(it)
        if u not in tpos:
            hit("REFUSE.INIT")
            refuse("[ORL-INIT] TRAIN item %s: af cell %r is not a cell of the tree arm" % (it, u))
        tsum[tpos[u]] += Xt[j]
        tcnt[tpos[u]] += 1
    if np.any(tcnt == 0):
        hit("REFUSE.INIT")
        refuse("[ORL-INIT] %d tree cell(s) hold no TRAIN row: no true mean to start from" % int(np.sum(tcnt == 0)))
    tree["n_dq"] = tree["n"].copy()
    tree["n"] = tcnt
    tree["r"] = np.linalg.norm(tsum, axis=1) / tcnt
    # batch tree identity: flatLeaf in 256-d (one-cell sources filed by source) vs af_cells; engine naming vs eval_fl; P_fl
    split_mask = ~np.isin(tree["src"], list(single))
    S = Xe @ tree["mu"].T
    S_split = np.where(split_mask[None, :], S, -np.inf)
    miss, bad_fl = 0, 0
    for i, it in enumerate(eitems):
        if esrc[i] in single:
            want = single[esrc[i]]
        else:
            want = ids[int(np.argmax(S_split[i]))]
        af = cells_af.get(it)
        if af not in tpos:
            hit("REFUSE.AFCELL")
            refuse("[ORL-IDENTITY] EVAL item %s: af cell %r is not a cell of the tree arm" % (it, af))
        if af != want:
            miss += 1
        if int(tree["name"][tpos[af]] == ye[i]) != int(efl[i]):
            bad_fl += 1
    if 1000 * miss > n_e:
        hit("REFUSE.I3")
        refuse("[ORL-IDENTITY] flatLeaf in %d-d differs from af_cells.tsv on %d of %d EVAL items (> 0.1%%)" % (Xe.shape[1], miss, n_e))
    if bad_fl:
        hit("REFUSE.EFL")
        refuse("[ORL-IDENTITY] the engine-named af cell disagrees with the bundle's eval_fl on %d EVAL items" % bad_fl)
    p_fl = "%.4f" % efl.mean()
    if p_fl != c["id_p_fl"]:
        hit("REFUSE.PFL")
        refuse("[ORL-IDENTITY] P_fl(AF-U) %s, not the recorded %s" % (p_fl, c["id_p_fl"]))
    say("IDENTITY (tree): flatLeaf (argmax cos to the snapshot vmfMu, %d-d; one-cell %s by source) = af_cells.tsv on %d of %d EVAL"
        " items (I3 bar 0.1%%); engine naming = eval_fl on all %d; P_fl(AF-U) %s (recorded %s)" % (
            Xe.shape[1], ", ".join(sorted(single)) or "none", n_e - miss, n_e, n_e, p_fl, c["id_p_fl"]))
    # C-2: the SYMMETRIC batch filing (flatLeaf over all six members' cells, the one-cell cell reachable by any item: the online
    # rule) decides OL1; the mirrored one (eval_fl, UNION-AF-ROUTE's C-S1) is printed beside
    efl_all = (tree["name"][np.argmax(S, axis=1)] == ye).astype(np.int64)
    p_all = "%.4f" % efl_all.mean()
    if p_all != c["id_p_fl_all"]:
        hit("REFUSE.PFL_ALL")
        refuse("[ORL-IDENTITY] symmetric batch P_fl(AF-U, nearest of all) %s, not the READY-measured %s" % (p_all, c["id_p_fl_all"]))
    say("IDENTITY (tree, symmetric): batch flatLeaf over all %d cells P_fl %s (READY_online_replay_lomo H4 measured %s); mirrored"
        " %s beside" % (len(ids), p_all, c["id_p_fl_all"], p_fl))
    say("INIT (C-1): online means start at r x vmfMu with n = the cell's TRAIN count: r median %.3f (min %.3f, max %.3f); n / directQueries"
        " median %.3f" % (float(np.median(tree["r"])), float(tree["r"].min()), float(tree["r"].max()),
                          float(np.median(tree["n"] / np.maximum(tree["n_dq"], 1)))))
    # k-means arm K_0 (union_af_route.us_fit seed 0)
    C, csrc, cloc, lab, fits = UA.us_fit(Xt, tsrc, ksrc, sources, KM_SEED)
    kids = ["K%d:%s:%03d" % (KM_SEED, csrc[g], cloc[g]) for g in range(len(C))]
    knames = np.concatenate([GB.name_clusters(fits[so]["labels"], int(ksrc[so]), yt[tsrc == so], classes) for so in sources])
    kn = np.bincount(lab, minlength=len(C)).astype(np.int64)
    kcd = np.array([int(np.sum(yt[lab == g] == knames[g])) if knames[g] != EMPTY else 0 for g in range(len(C))], dtype=np.int64)
    k0 = parts["k0_cells"]
    kbad = sum(1 for j, it in enumerate(titems) if k0.get(it) != kids[lab[j]])
    if kbad:
        hit("REFUSE.K0")
        refuse("[ORL-IDENTITY] K_0's TRAIN labels differ from k_cells_s0.tsv on %d of %d TRAIN items" % (kbad, n_t))
    km = dict(ids=kids, src=np.array(csrc), mu=np.asarray(C, dtype=np.float64), n=kn, name=np.asarray(knames, dtype=int), cdom=kcd)
    if np.any(kn == 0):
        hit("REFUSE.INIT")
        refuse("[ORL-INIT] %d K_0 centre(s) hold no TRAIN row" % int(np.sum(kn == 0)))
    km["r"] = np.array([float(np.linalg.norm(Xt[lab == g].sum(axis=0))) / kn[g] for g in range(len(C))])
    kfl_all = (km["name"][np.argmax(Xe @ km["mu"].T, axis=1)] == ye).astype(np.int64)
    pk_all = "%.4f" % kfl_all.mean()
    if pk_all != c["id_p_k0_all"]:
        hit("REFUSE.PK0_ALL")
        refuse("[ORL-IDENTITY] symmetric batch P(US_0, nearest of all) %s, not the recorded %s" % (pk_all, c["id_p_k0_all"]))
    Sk = Xe @ km["mu"].T
    one = np.isin(km["src"], list(single))
    Sk = np.where(one[None, :], -np.inf, Sk)
    pick = np.argmax(Sk, axis=1)
    for so in single:
        pick[esrc == so] = int(np.flatnonzero(km["src"] == so)[0])
    kfl = (km["name"][pick] == ye).astype(np.int64)
    p_k = "%.4f" % kfl.mean()
    if p_k != c["id_p_k0"]:
        hit("REFUSE.PK0")
        refuse("[ORL-IDENTITY] mirrored batch k-means P(US_0) %s, not the recorded %s" % (p_k, c["id_p_k0"]))
    say("IDENTITY (k-means): K_0 TRAIN labels = k_cells_s0.tsv on all %d TRAIN items; mirrored batch P(US_0) %s (recorded %s);"
        " symmetric (nearest of all) %s (recorded %s, UNION-AF-ROUTE outcome line 209); r median %.3f" % (
            n_t, p_k, c["id_p_k0"], pk_all, c["id_p_k0_all"], float(np.median(km["r"]))))
    pol = parts.get("policy")
    if pol is not None:
        tree["policy"], km["policy"] = dict(pol["tree_cell"]), dict(pol["xtree_cell"]["K%d" % KM_SEED])
        tree["fallback"] = km["fallback"] = str(pol["best_single"])
    else:
        tree["policy"] = km["policy"] = None
        tree["fallback"] = km["fallback"] = None
    Xg = FM.unit_rows(np.asarray(parts["Xg"], dtype=np.float64))
    gsrc = np.array([src_of(classes[i]) for i in np.asarray(parts["yg"], dtype=int)])
    return dict(classes=classes, sources=sources, single=single, ksrc=ksrc, Xt=Xt, yt=yt, tsrc=tsrc, titems=titems, Xe=Xe, ye=ye,
                esrc=esrc, eitems=eitems, ecomp=ecomp, Xg=Xg, gsrc=gsrc, batch={"tree": efl_all, "km": kfl_all},
                batch_mir={"tree": efl, "km": kfl},
                arms={"tree": tree, "km": km})


# ── one replay (the registered online procedure) ────────────────────────────────────────────────────────────────────────

def _model(A, cid):
    if A["policy"] is None:
        return None
    return A["policy"].get(cid, A["fallback"])


def replay(W, arm, m, init="mean"):
    """init 'mean' (DECIDING, C-1): mbar starts at the true mean r x mu of the cell's unit TRAIN rows, n = their count; init 'unit'
    (DESCRIPTIVE, the first build): mbar starts at the unit mu. Routing always uses mbar / |mbar|."""
    A = W["arms"][arm]
    classes = W["classes"]
    keep = np.flatnonzero(A["src"] != m)
    ids = [A["ids"][j] for j in keep]
    mu0 = A["mu"][keep].copy()
    mbar = mu0 * A["r"][keep][:, None] if init == "mean" else mu0.copy()
    U = mu0.copy()
    n = A["n"][keep].astype(np.float64).copy()
    gin = W["gsrc"] != m
    g_max, g_mar = top_margin(W["Xg"][gin] @ mu0.T)
    tau_oos, tau_m = order_stat(g_max, 1 - TPR), order_stat(g_mar, P_M)
    ein, eout = np.flatnonzero(W["esrc"] != m), np.flatnonzero(W["esrc"] == m)
    tout = np.flatnonzero(W["tsrc"] == m)
    S_in0 = W["Xe"][ein] @ mu0.T
    before = np.argmax(S_in0, axis=1)
    auc = auroc(S_in0.max(axis=1), (W["Xe"][eout] @ mu0.T).max(axis=1))
    rng = np.random.default_rng(ORDER_SEED)
    order = [("T", int(i)) for i in rng.permutation(tout)] + [("E", int(i)) for i in rng.permutation(eout)]
    absorbed = defaultdict(Counter)
    buf, reasons, filed = [], Counter(), 0
    for side, i in order:
        x = W["Xt"][i] if side == "T" else W["Xe"][i]
        s = U @ x
        j1 = int(np.argmax(s))
        top1 = float(s[j1])
        top2 = float(np.max(np.delete(s, j1))) if len(s) > 1 else -np.inf
        oos, low = top1 < tau_oos, (top1 - top2) < tau_m
        if oos or low:
            buf.append((side, i))
            reasons["oos" if oos else "margin"] += 1
            if oos and low:
                reasons["both"] += 1
            continue
        mbar[j1] = mbar[j1] + (x - mbar[j1]) / (n[j1] + 1.0)
        n[j1] += 1.0
        U[j1] = mbar[j1] / np.linalg.norm(mbar[j1])
        filed += 1
        if side == "T":
            absorbed[j1][int(W["yt"][i])] += 1
    names = A["name"][keep].copy()
    cdom = A["cdom"][keep]
    renamed = 0
    for j, cnt in absorbed.items():
        top = max(cnt.values())
        cbest = min((k for k, v in cnt.items() if v == top), key=lambda k: classes[k])
        if top > cdom[j]:
            names[j] = cbest
            renamed += 1
    Lm = int(W["ksrc"][m])
    kb = min(Lm, len(buf))
    if kb >= 1:
        Xb = np.vstack([W["Xt"][i] if sd == "T" else W["Xe"][i] for sd, i in buf])
        fit, _t = GB.ukm_fit(Xb, kb, BUF_SEED)
        Cb, blab = np.asarray(fit["centers"], dtype=np.float64), np.asarray(fit["labels"], dtype=int)
        tmask = np.array([sd == "T" for sd, _i in buf])
        ybuf = np.array([int(W["yt"][i]) if sd == "T" else int(W["ye"][i]) for sd, i in buf])
        bnames = np.array([GB.majority(ybuf[tmask & (blab == j)], classes) for j in range(kb)], dtype=int)
        purity = float(np.mean(bnames[blab] == ybuf))
    else:
        Cb, blab, bnames, purity = np.zeros((0, mu0.shape[1])), np.zeros(0, dtype=int), np.zeros(0, dtype=int), float("nan")
    allC = np.vstack([U, Cb])
    all_ids = ids + ["BUF:%s:%s:%03d" % (arm, m, j) for j in range(kb)]
    all_names = np.concatenate([names, bnames]).astype(int)
    fm = np.argmax(W["Xe"][eout] @ allC.T, axis=1)
    online_ok = (all_names[fm] == W["ye"][eout]).astype(np.int64)
    after = np.argmax(W["Xe"][ein] @ allC.T, axis=1)
    after_mean = np.argmax(W["Xe"][ein] @ U.T, axis=1)
    churn = (after_mean != before).astype(np.int64)          # DECIDING (C-3): the five-member graft before vs after the replay
    churn_all = (after != before).astype(np.int64)           # beside: buffer cells included (capture by provisional cells)
    if A["policy"] is not None:
        dch = np.array([int(_model(A, ids[b]) != _model(A, all_ids[a])) for b, a in zip(before.tolist(), after.tolist())], dtype=np.int64)
    else:
        dch = None
    return dict(m=m, arm=arm, ids=ids, all_ids=all_ids, tau_oos=tau_oos, tau_m=tau_m, n_gate=int(gin.sum()), ein=ein, eout=eout,
                n_train=len(tout), n_stream=len(order), n_buf=len(buf), reasons=reasons, filed=filed, renamed=renamed, kb=kb, Lm=Lm,
                purity=purity, online_ok=online_ok, fm=fm, before=before, after=after, after_mean=after_mean, churn=churn,
                churn_all=churn_all, dch=dch, auroc=auc, buf_eval=sum(1 for sd, _i in buf if sd == "E"), mbar=mbar, n_end=n)


# ── the readout ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def ol1_word(d, se, margin=MARGIN):
    """OOS-BASELINES' TOST form (OL-R7)."""
    lo90, hi90, lo95, hi95 = d - Z90 * se, d + Z90 * se, d - Z95 * se, d + Z95 * se
    if lo90 > -margin and hi90 < margin:
        return "EQUIVALENT"
    if abs(d) > margin and (lo95 > 0 or hi95 < 0):
        return "LOSS" if d < 0 else "GAIN"
    return "NEITHER"


def ol2_word(pairs, margin=MARGIN):
    """pairs = [(point, 95% upper)] per replay (OL-R8)."""
    stable = all(h <= margin for _p, h in pairs)
    not_stable = any(p > margin for p, _h in pairs)
    if stable and not_stable:
        hit("REFUSE.OL2_BOTH")
        refuse("[ORL-OL2-BOTH] STABLE and NOT-STABLE both hold on the same data (a percentile upper below its point): a "
               "registration matter for the registrar; no outcome")
    if not_stable:
        return "NOT-STABLE"
    if stable:
        return "STABLE"
    return "UNDETERMINED"


def ol1_of(st):
    """OL1 from the pooled stat: the TOST form at the bootstrap SD (OL-R7), never the percentile width."""
    return ol1_word(st["d"], st["se"])


def ol2_of(per, sources):
    """OL2 from the per-replay churn stats: (point, percentile 95% upper) of every replay."""
    return ol2_word([(per[m]["churn"]["d"], per[m]["churn"]["hi"]) for m in sources])


def ol2_all_of(per, sources):
    """The OL2 rule applied to the all-cells churn (buffer capture included): DESCRIPTIVE beside the deciding means-only churn."""
    return ol2_word([(per[m]["churn_all"]["d"], per[m]["churn_all"]["hi"]) for m in sources])


def f_ol(ol2):
    return ol2 == "NOT-STABLE"


def in_band(x, lo, hi):
    return lo <= x <= hi


def brier(probs, outcome):
    return float(sum((p - (1.0 if k == outcome else 0.0)) ** 2 for k, p in probs.items()))


def compute(W):
    R = dict(arms={}, n=len(W["ye"]), G=len(set(W["ecomp"].tolist())))
    for arm in ARMS:
        reps = {m: replay(W, arm, m) for m in W["sources"]}
        diff = np.zeros(len(W["ye"]), dtype=np.float64)
        online = np.full(len(W["ye"]), -1, dtype=np.int64)
        seen = np.zeros(len(W["ye"]), dtype=np.int64)
        for m, r in reps.items():
            diff[r["eout"]] = r["online_ok"] - W["batch"][arm][r["eout"]]
            online[r["eout"]] = r["online_ok"]
            seen[r["eout"]] += 1
        if not np.all(seen == 1):
            refuse("%d EVAL item(s) were not held out exactly once (each must be held out exactly once)" % int(np.sum(seen != 1)))
        st = GB.stat(diff, W["ecomp"])
        diff_mir = online - W["batch_mir"][arm]                 # beside (C-2): against the mirrored batch filing
        st_mir = GB.stat(diff_mir.astype(np.float64), W["ecomp"])
        split = ~np.isin(W["esrc"], list(W["single"]))
        st_split = GB.stat(diff[split], W["ecomp"][split]) if split.any() and not split.all() else None
        per = {}
        unit = {m: replay(W, arm, m, init="unit") for m in W["sources"]}     # beside (C-1): the unit-initialised replay
        diff_unit = np.zeros(len(W["ye"]), dtype=np.float64)
        for m, r in reps.items():
            cs = GB.stat(r["churn"].astype(np.float64), W["ecomp"][r["ein"]])
            ca = GB.stat(r["churn_all"].astype(np.float64), W["ecomp"][r["ein"]])
            dm = GB.stat(diff[r["eout"]], W["ecomp"][r["eout"]])
            dc = GB.stat(r["dch"].astype(np.float64), W["ecomp"][r["ein"]]) if r["dch"] is not None else None
            diff_unit[r["eout"]] = unit[m]["online_ok"] - W["batch"][arm][r["eout"]]
            per[m] = dict(churn=cs, churn_all=ca, d=dm, dch=dc, p_on=float(r["online_ok"].mean()),
                          p_b=float(W["batch"][arm][r["eout"]].mean()), churn_unit=float(unit[m]["churn"].mean()),
                          churn_all_unit=float(unit[m]["churn_all"].mean()))
        R["arms"][arm] = dict(reps=reps, diff=diff, online=online, st=st, per=per, p_on=float(online.mean()),
                              p_b=float(W["batch"][arm].mean()), ol1=ol1_of(st),
                              ol2=ol2_of(per, W["sources"]), st_mir=st_mir, ol1_mir=ol1_of(st_mir),
                              p_b_mir=float(W["batch_mir"][arm].mean()), st_split=st_split,
                              d_unit=float(diff_unit.mean()), ol2_all=ol2_all_of(per, W["sources"]))
    R["tmk"] = GB.stat(R["arms"]["tree"]["diff"] - R["arms"]["km"]["diff"], W["ecomp"])
    return R


def fs(st):
    return "%+.4f  95%% [%+.4f, %+.4f] (n %d, %d components; SE %.5f, DEFF %.3f, n_eff %.0f, MDE80 %.4f, discordance %.4f)" % (
        st["d"], st["lo"], st["hi"], st["n"], st["G"], st["se"], st["deff"], st["n_eff"], st["mde"], st["disc"])


def ol1_lines(a, deciding):
    st = a["st"]
    L = []
    d, se = st["d"], st["se"]
    L.append("  D = P_fl(ONLINE) %.4f - P_fl(BATCH) %.4f = %+.4f; TOST 90%% [%+.4f, %+.4f], 95%% [%+.4f, %+.4f] (point +/- z SE, SE %.5f);"
             " percentile 95%% [%+.4f, %+.4f] (beside)" % (a["p_on"], a["p_b"], d, d - Z90 * se, d + Z90 * se, d - Z95 * se,
                                                          d + Z95 * se, se, st["lo"], st["hi"]))
    L.append("  " + fs(st))
    w = a["ol1"]
    tag = "OL1" if deciding else "OL1-form (k-means arm, DESCRIPTIVE)"
    if w == "EQUIVALENT":
        hit("OL1.EQUIVALENT")
        L.append("%s: EQUIVALENT: the 90%% interval [%+.4f, %+.4f] lies inside +/-%.3f (within %.3f of the batch arm, never 'equal')" % (
            tag, d - Z90 * se, d + Z90 * se, MARGIN, MARGIN))
    elif w == "LOSS":
        hit("OL1.LOSS")
        L.append("%s: DIFFERENT (LOSS): |D| %.4f > %.3f and the 95%% interval [%+.4f, %+.4f] lies below 0: the online replay files the"
                 " held-out member worse than the batch arm" % (tag, abs(d), MARGIN, d - Z95 * se, d + Z95 * se))
    elif w == "GAIN":
        hit("OL1.GAIN")
        L.append("%s: DIFFERENT (GAIN): |D| %.4f > %.3f and the 95%% interval [%+.4f, %+.4f] lies above 0: the online replay files the"
                 " held-out member better than the batch arm" % (tag, abs(d), MARGIN, d - Z95 * se, d + Z95 * se))
    else:
        hit("OL1.NEITHER")
        L.append("%s: NEITHER: the 90%% interval [%+.4f, %+.4f] is not inside +/-%.3f and DIFFERENT does not hold (|D| %.4f, 95%%"
                 " [%+.4f, %+.4f]); reads 'not shown'" % (tag, d - Z90 * se, d + Z90 * se, MARGIN, abs(d), d - Z95 * se, d + Z95 * se))
    sm = a["st_mir"]
    L.append("  BESIDE (C-2, DESCRIPTIVE): against the MIRRORED batch filing (one-cell source filed by source, P_fl %.4f): D %+.4f,"
             " TOST 90%% [%+.4f, %+.4f], form-word %s" % (a["p_b_mir"], sm["d"], sm["d"] - Z90 * sm["se"], sm["d"] + Z90 * sm["se"],
                                                       a["ol1_mir"]))
    if a["st_split"] is not None:
        hit("OL1.SPLIT_ONLY")
        L.append("  BESIDE (C-2, DESCRIPTIVE): D pooled over the split members' replays only (one-cell replays excluded): %s" % fs(a["st_split"]))
    L.append("  BESIDE (C-1, DESCRIPTIVE): D with the online means started at the UNIT mu (the first build's rule): %+.4f" % a["d_unit"])
    return L


def ol2_lines(W, a, deciding):
    L = []
    for m in W["sources"]:
        r, p = a["reps"][m], a["per"][m]
        cs = p["churn"]
        L.append("  replay -%s: churn %.4f, 95%% upper %.4f (%d in-member EVAL items, %d components) %s; beside: all-cells churn"
                 " %.4f (upper %.4f; buffer capture included), unit-init churn %.4f / all-cells %.4f" % (
                     m, cs["d"], cs["hi"], cs["n"], cs["G"], "<= 0.020" if cs["hi"] <= MARGIN else "> 0.020", p["churn_all"]["d"],
                     p["churn_all"]["hi"], p["churn_unit"], p["churn_all_unit"]))
    w = a["ol2"]
    tag = "OL2" if deciding else "OL2-form (k-means arm, DESCRIPTIVE)"
    worst = max(W["sources"], key=lambda m: a["per"][m]["churn"]["hi"])
    if w == "STABLE":
        hit("OL2.STABLE")
        L.append("%s: STABLE: every replay's 95%% upper bound <= 0.020 (largest %.4f, replay -%s)" % (tag, a["per"][worst]["churn"]["hi"], worst))
    elif w == "NOT-STABLE":
        hit("OL2.NOT_STABLE")
        bad = [m for m in W["sources"] if a["per"][m]["churn"]["d"] > MARGIN]
        L.append("%s: NOT-STABLE: churn point > 0.020 in replay(s) %s (%s)" % (
            tag, ", ".join("-" + m for m in bad), ", ".join("%.4f" % a["per"][m]["churn"]["d"] for m in bad)))
    else:
        hit("OL2.UNDETERMINED")
        L.append("%s: UNDETERMINED: no churn point exceeds 0.020 but replay -%s's 95%% upper %.4f does" % (
            tag, worst, a["per"][worst]["churn"]["hi"]))
    return L


def support_lines(a):
    st = a["st"]
    se = st["se"]
    L = ["SUPPORT (OL1, measured beside registered): n %d (registered %d), components %d (registered %d), mean cluster size %.3f;"
         " SE %.5f (registered %.5f at discordance %.2f); DEFF %.3f (registered %.3f, DEEP-SPLIT-COMPARE C-DB); n_eff %.0f"
         " (registered %d); discordance %.4f; MDE80 %.4f" % (st["n"], SUPPORT["n"], st["G"], SUPPORT["comp"], st["n"] / st["G"], se,
                                                             SUPPORT["se"], SUPPORT["disc"], st["deff"], SUPPORT["deff"], st["n_eff"],
                                                             SUPPORT["n_eff"], st["disc"], st["mde"]),
         "  reach at the measured SE: TOST |D_true| < %.4f (0.020 - 2.487 SE; registered %.4f); DIFFERENT |D_true| >= %.4f"
         " (0.020 + 0.842 SE; registered %.4f)" % (MARGIN - 2.487 * se, SUPPORT["tost_reach"], MARGIN + 0.842 * se, SUPPORT["diff_reach"])]
    return L


def pred_lines(W, R):
    T = R["arms"]["tree"]
    L = []
    d = T["st"]["d"]
    if in_band(d, PRED_P1[1], PRED_P1[2]):
        hit("P1.HELD")
        L.append("PREDICTION P1 D %+.3f [%+.3f, %+.3f]: observed %+.4f -> HELD" % (PRED_P1 + (d,)))
    else:
        hit("P1.FAILED")
        L.append("PREDICTION P1 D %+.3f [%+.3f, %+.3f]: observed %+.4f -> FAILED" % (PRED_P1 + (d,)))
    L.append("PREDICTION P1 OL1 probabilities (LOSS 0.45, NEITHER 0.40, EQUIVALENT 0.15; GAIN 0.00 implied): observed %s; Brier %.4f"
             % (T["ol1"], brier(PROB_OL1, T["ol1"])))
    ch = [T["per"][m]["churn"]["d"] for m in W["sources"]]
    out = [m for m, x in zip(W["sources"], ch) if not in_band(x, PRED_P2[1], PRED_P2[2])]
    if not out:
        hit("P2.HELD")
        L.append("PREDICTION P2 churn %.3f [%.3f, %.3f] per replay: observed %s -> HELD (all six in band)" % (
            PRED_P2 + (" / ".join("%.4f" % x for x in ch),)))
    else:
        hit("P2.FAILED")
        L.append("PREDICTION P2 churn %.3f [%.3f, %.3f] per replay: observed %s -> FAILED (outside: %s)" % (
            PRED_P2 + (" / ".join("%.4f" % x for x in ch), ", ".join("-" + m for m in out))))
    ev = 1.0 if T["ol2"] == "STABLE" else 0.0
    L.append("PREDICTION P2 OL2 STABLE 0.80: observed %s; Brier %.4f" % (T["ol2"], (PROB_OL2_STABLE - ev) ** 2))
    au = [T["reps"][m]["auroc"] for m in W["sources"]]
    med = float(np.median(au))
    if in_band(med, PRED_P3[1], PRED_P3[2]):
        hit("P3.HELD")
        L.append("PREDICTION P3 new-domain OOS AUROC median %.2f [%.2f, %.2f] (descriptive): observed %.4f -> HELD" % (PRED_P3 + (med,)))
    else:
        hit("P3.FAILED")
        L.append("PREDICTION P3 new-domain OOS AUROC median %.2f [%.2f, %.2f] (descriptive): observed %.4f -> FAILED" % (PRED_P3 + (med,)))
    return L


def falsifier_lines(R):
    T = R["arms"]["tree"]
    L = []
    W_src = list(T["per"])
    worst = max(W_src, key=lambda m: T["per"][m]["churn"]["d"])
    worst_all = max(W_src, key=lambda m: T["per"][m]["churn_all"]["d"])
    L.append("  churns (C-3): DECIDING = means-only (the five-member graft before vs after: only the online mean refit moves it),"
             " largest %.4f (-%s); BESIDE = all cells (buffer capture included), largest %.4f (-%s), OL2 rule on it: %s" % (
                 T["per"][worst]["churn"]["d"], worst, T["per"][worst_all]["churn_all"]["d"], worst_all, T["ol2_all"]))
    if f_ol(T["ol2"]):
        hit("FOL.FIRES")
        L.append("F-OL FIRES: OL2 NOT-STABLE on the means-only churn: the online mean refit moves existing cells' addresses beyond 2%%"
                 " in replay -%s (%.4f); the note's 'ids are immutable' rule needs mean-freezing and the online claim narrows" % (
                     worst, T["per"][worst]["churn"]["d"]))
    else:
        hit("FOL.NOT_FIRED")
        L.append("F-OL NOT FIRED: OL2 reads %s on the means-only churn" % T["ol2"])
    if T["ol2_all"] == "NOT-STABLE" and T["ol2"] != "NOT-STABLE":
        hit("FOL.CAPTURE")
        L.append("  BUFFER CAPTURE (DESCRIPTIVE): beyond 2%% by buffer capture: the provisional buffer cells take %.4f of replay -%s's"
                 " in-member addresses while the mean refit alone moves %.4f; the registration attributes F-OL to the mean refit, so"
                 " capture does not fire it (registrar's bracket, OL-R8)" % (T["per"][worst_all]["churn_all"]["d"], worst_all,
                                                                            T["per"][worst_all]["churn"]["d"]))
    if T["ol1"] == "LOSS":
        hit("OL1.LOSS_LIMIT")
        L.append("  OL1 LOSS limits the replay to 'addresses %s, new domain filed worse than a rebuild'; it does not fire F-OL" % (
            "stable" if T["ol2"] == "STABLE" else "not shown stable"))
    return L


def replay_lines(W, R, arm):
    a = R["arms"][arm]
    L = []
    for m in W["sources"]:
        r, p = a["reps"][m], a["per"][m]
        dc = ("decision churn %.4f" % p["dch"]["d"]) if p["dch"] is not None else "decision churn NOT COMPUTED (policy absent)"
        L.append("  -%s (%s): streamed %d (TRAIN %d, EVAL %d); GATE %d in-member items: tau_oos %.5f, tau_m %.5f; buffered %d (%.4f;"
                 " OOS %d, margin %d, both %d; EVAL %d); filed %d; renamed cells %d; buffer k %d (L_m %d); buffer purity %s;"
                 " P_fl online %.4f vs batch %.4f, D_m %s; new-domain OOS AUROC %.4f; %s" % (
                     m, ARM_NAME[arm], r["n_stream"], r["n_train"], r["n_stream"] - r["n_train"], r["n_gate"], r["tau_oos"], r["tau_m"],
                     r["n_buf"], r["n_buf"] / max(r["n_stream"], 1), r["reasons"]["oos"], r["reasons"]["margin"], r["reasons"]["both"],
                     r["buf_eval"], r["filed"], r["renamed"], r["kb"], r["Lm"],
                     "%.4f" % r["purity"] if r["purity"] == r["purity"] else "n/a (no buffer)", p["p_on"], p["p_b"], fs(p["d"]),
                     r["auroc"], dc))
    return L


def outcome_lines(W, R, pre):
    T, K = R["arms"]["tree"], R["arms"]["km"]
    L = list(pre)
    say = L.append
    say("")
    say("=== %s: OL1, OL2, F-OL, P1-P3 (%s) ===" % (TEST_ID, REG_TEXT))
    say("DENOMINATOR (OL1): the held-out members' EVAL items pooled over %d replays = %d items in %d CK-CLOSE components (each held"
        " out once; registered %d / %d)" % (len(W["sources"]), R["n"], R["G"], SUPPORT["n"], SUPPORT["comp"]))
    ns_in = [len(T["reps"][m]["ein"]) for m in W["sources"]]
    say("DENOMINATOR (OL2): in-member EVAL items per replay %s; range %d-%d (the registration's 'about %d' restated by the measured"
        " range, READY D-4; at p 0.005 the 95%% upper at the smallest n stays below 0.020)" % (
            ", ".join("-%s %d" % (m, k) for m, k in zip(W["sources"], ns_in)), min(ns_in), max(ns_in), SUPPORT["ol2_n"]))
    say("LIKE WITH LIKE: | ONLINE tree | five AF-U trees + buffer k-means | TRAIN-majority naming only | BATCH AF-U | six AF-U trees |"
        " naming only | ONLINE k-means | five per-source K_0 + buffer k-means | naming only | BATCH k-means | six per-source K_0 at"
        " matched k (AK2 US_0) | naming only |; online-vs-batch is the same cell type AND the same filing rule on both sides (C-2:"
        " flatLeaf over all cells, the one-cell IFEVAL cell reachable by any item); tree-vs-k-means is DESCRIPTIVE (nothing here"
        " shows the tree beats k-means)")
    say("DISCLOSURE (C-2, OL-R1): the DECIDING batch arm files by flatLeaf over all six members' cells, as the online arm does; the"
        " mirrored by-source filing of IFEVAL (UNION-AF-ROUTE C-S1, P_fl 0.7346 / P(US_0) 0.7368) is printed beside as DESCRIPTIVE;"
        " the replay of IFEVAL is the known one-cell case")
    say("DISCLOSURE (C-1, OL-R3): the online mean of a cell starts at the true mean of its unit TRAIN rows (n = their count, length"
        " r = |sum| / n, direction the engine's vmfMu / the K_0 centre); routing uses mbar / |mbar|; the unit-initialised replay"
        " (the first build's rule) is printed beside as DESCRIPTIVE")
    say("DISCLOSURE (D-5): the online arm is transductive on the held-out member's EVAL (registered: its EVAL is streamed and enters"
        " the buffer k-means), so an EQUIVALENT never reads 'as good as a rebuild on unseen items'; residual of 'never touched':"
        " 15 TRAIN / 14 EVAL MATH / MMLU_PRO_LB text-shared multi-class items left the bundle but stayed in the MMLU_PRO_LB tree's fit")
    say("NOT APPLICABLE: no judge verdict (declared-class keyed): no wrong(established), no tie convention A / B; zero calls")
    say("")
    say("--- OL1 (DECIDING; the interval decides; OOS-BASELINES' TOST form, margin 0.020) ---")
    L.extend(ol1_lines(T, True))
    L.extend(support_lines(T))
    say("--- OL2 (DECIDING; in-member address churn over the five-member graft before vs after the replay (means-only; C-3), STABLE"
        " iff every replay's 95% upper <= 0.020) ---")
    L.extend(ol2_lines(W, T, True))
    say("--- F-OL ---")
    L.extend(falsifier_lines(R))
    say("--- PREDICTIONS ---")
    L.extend(pred_lines(W, R))
    say("--- DESCRIPTIVE: the k-means arm (same procedure from K_0) ---")
    L.extend(ol1_lines(K, False))
    L.extend(ol2_lines(W, K, False))
    say("  tree-minus-k-means paired (D_tree - D_K, per item): %s (DESCRIPTIVE; not tree-over-k-means superiority)" % fs(R["tmk"]))
    say("--- DESCRIPTIVE: per replay ---")
    for arm in ARMS:
        L.extend(replay_lines(W, R, arm))
    if "IFEVAL" in W["sources"]:
        r = T["reps"]["IFEVAL"]
        say("IFEVAL's case (one cell in the batch AF-U; L_m 1): buffered %d of %d streamed; D_m %+.4f; AUROC %.4f" % (
            r["n_buf"], r["n_stream"], T["per"]["IFEVAL"]["d"]["d"], r["auroc"]))
    say("WILL NOT SHOW (registered): any certified new split (stage 2); real traffic or drift; tree-over-k-means superiority; anything"
        " beyond these six sources and one draw; label-free gains from refit on MMLU-Pro")
    return L


def items_text(W, R):
    rows = ["item_id,replay,role,arm,cell_before,cell_after_means,cell_after_all,online_ok,batch_ok,batch_mirrored_ok"]
    for arm in ARMS:
        a = R["arms"][arm]
        for m in W["sources"]:
            r = a["reps"][m]
            for k, i in enumerate(r["eout"].tolist()):
                rows.append("%s,%s,heldout,%s,,,%s,%d,%d,%d" % (W["eitems"][i], m, arm, r["all_ids"][r["fm"][k]], r["online_ok"][k],
                                                                 W["batch"][arm][i], W["batch_mir"][arm][i]))
            for k, i in enumerate(r["ein"].tolist()):
                rows.append("%s,%s,inmember,%s,%s,%s,%s,,," % (W["eitems"][i], m, arm, r["ids"][r["before"][k]],
                                                               r["ids"][r["after_mean"][k]], r["all_ids"][r["after"][k]]))
    return "\n".join(rows) + "\n"


# ── loading the real parts ──────────────────────────────────────────────────────────────────────────────────────────────

def _policy_path():
    return P(reg()["policy"])


def load_parts(say):
    c = reg()
    man, msha = UA.load_inputs(say)
    ip = UA.input_paths()
    single = {s: e["cell"] for s, e in (man.get("single") or {}).items()}
    leaves = {}
    ksrc = {}
    for mdir, so in c["members"]:
        if so in single:
            ksrc[so] = 1
            continue
        snap = GB.last_snapshot(P("%s/%s/seed_42/dag_snapshots.jsonl" % (UA.reg()["afu"], mdir)))
        lv = [nd for nd in snap["nodes"] if nd.get("isLeaf")]
        for nd in lv:
            mu = np.asarray(nd["vmfMu"], dtype=np.float64)
            if len(mu) != c["dim"]:
                refuse("leaf %s:%s vmfMu is %d-d, not %d" % (so, nd["id"], len(mu), c["dim"]))
            leaves["%s:%s" % (so, nd["id"])] = (mu, int(nd["directQueries"]))
        ksrc[so] = len(lv)
    if ksrc != man["ksrc"]:
        refuse("snapshot leaf counts %s differ from the inputs manifest's %s" % (ksrc, man["ksrc"]))
    b, meta = UA.GC.load_bundle(P(ip["bundle"]), expect=(c["pool"], c["n_eval_before"], c["comp_before"]), sides=None)
    classes = [str(x) for x in b["classes"]]
    cells_af, _d = UA.V.load_tree_cells(P(ip["af"]), man["inputs"][ip["af"]])
    k0, _d0 = UA.V.load_tree_cells(P(ip["k"][KM_SEED]), man["inputs"][ip["k"][KM_SEED]])
    lrows = GB.read_csv(os.path.join(P(ip["merged"]), RP.LEAVES))
    leaf_dom = {}
    for r in lrows:
        ps, pu = int(r["profile_size"] or 0), float(r["leaf_purity"] or 0.0)
        leaf_dom[r["leaf_id"]] = (r["leaf_dominant"] if ps > 0 else "", int(round(ps * pu)))
    # GATE items (side export; multi-class excluded) and every vector through rp12_pairing's reader
    side, _smeta = UA._SIDES[0]()
    held, _dis, _ut, multi = RP.item_cells(RP.read_rows(os.path.join(P(ip["merged"]), RP.QUERIES)))
    gate = sorted(it for it, (_cell, _key, _n) in held.items() if side.get(it, (None, None))[1] == "GATE")
    gkey = {it: held[it][1] for it in gate}
    bad = [it for it in gate if gkey[it] not in classes]
    if bad:
        refuse("%d GATE item(s) carry a class outside the bundle's (first %s)" % (len(bad), bad[:2]))
    titems, eitems = [str(x) for x in b["train_item"]], [str(x) for x in b["eval_item"]]
    vec = UA._TV[0](gate + titems + eitems, c["dim"])
    Xt0, Xe0 = FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64)), FM.unit_rows(np.asarray(b["eval_X"], dtype=np.float64))
    dmax = max(float(np.max(np.abs(np.vstack([vec[i] for i in titems]) - Xt0))),
               float(np.max(np.abs(np.vstack([vec[i] for i in eitems]) - Xe0))))
    if dmax > 1e-9:
        hit("REFUSE.VEC")
        refuse("[ORL-VEC] rp12_pairing's reader reproduces the bundle rows only to max |diff| %.3g (> 1e-9): GATE vectors would not be"
               " in the bundle's space" % dmax)
    say("VECTORS: %d GATE items (multi-class excluded: %d held-out multi-class items) and all %d bundle rows read by rp12_pairing's"
        " reader (multicorpus_cache_v1.db / embeddings_cache.db, mode=ro); bundle rows reproduced to max |diff| %.2e" % (
            len(gate), len(multi), len(titems) + len(eitems), dmax))
    pp = _policy_path()
    pol = None
    if os.path.isfile(pp):
        pol = json.load(open(pp, encoding="utf-8"))
        hit("POLICY.PRESENT")
        say("POLICY (descriptive decision churn): %s sha256 %s (never committed)" % (reg()["policy"], sha256_bytes(pp)))
    else:
        hit("POLICY.ABSENT")
        say("POLICY (descriptive decision churn): %s ABSENT -> decision churn NOT COMPUTED" % reg()["policy"])
    return dict(classes=classes, Xt=b["train_X"], yt=b["train_y"], titems=titems, Xe=b["eval_X"], ye=b["eval_y"], eitems=eitems,
                ecomp=b["eval_comp"], efl=b["eval_fl"], leaves=leaves, leaf_dom=leaf_dom, single=single, ksrc=ksrc, cells_af=cells_af,
                k0_cells=k0, Xg=np.vstack([vec[i] for i in gate]), yg=np.array([classes.index(gkey[i]) for i in gate]), policy=pol)


_LOAD = [load_parts]
_POOL = [GB.pool_check_v2]
_PROG = [PROGRAMME]


def header(say, mode):
    c = reg()
    say("POOL %s (%s; %s; the first line of every mode)" % (c["pool"], TEST_ID, mode))
    say("%s | registration %s" % (TEST_ID, REG_TEXT))
    me = os.path.abspath(__file__)
    with open(me, "rb") as f:
        raw = f.read()
    crlf = b"\r\n" in raw
    say("  script %s blob:%s sha256-lf16:%s (LF rendering of record)%s" % (
        os.path.basename(me), blob_lf(me), sha256_lf(me)[:16],
        "; working tree CRLF sha256-crlf16:%s" % hashlib.sha256(raw).hexdigest()[:16] if crlf else "; working tree LF"))
    for nm, pin in PINS:
        say("  imported %s blob:%s (pinned, asserted before import)" % (nm, pin))
    say("  data root %s (--data-root; experiment_results/ and the DBs read here, the outputs written here)" % data_root())
    say("  threads: %s (set to 1 before numpy); zero calls; DBs mode=ro through data_v2.ro.open_ro" % ", ".join(
        "%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))


def pool_line(say):
    rc, msg = _POOL[0](reg()["pool"])
    say("POOL CHECK (B0-2, replaces pool_guard for pv2 pools): rc %d | %s" % (rc, msg))
    if rc != 0:
        hit("REFUSE.POOL")
        refuse("the B0-2 pool check failed: %s" % msg)


def denominators(say):
    c = reg()
    say("DENOMINATORS (registered): OL1 %d held-out EVAL items in %d components pooled over 6 replays (DEFF 1.223, n_eff 5,020, SE"
        " 0.00547); OL2 about 5,100 in-member EVAL items per replay; TRAIN %d; bundle before MC-EXCLUDE %d / %d" % (
            c["n_eval"], c["n_comp"], c["n_train"], c["n_eval_before"], c["comp_before"]))


def thresholds_lines(W):
    L = []
    for arm in ARMS:
        A = W["arms"][arm]
        for m in W["sources"]:
            keep = A["src"] != m
            gin = W["gsrc"] != m
            g_max, g_mar = top_margin(W["Xg"][gin] @ A["mu"][keep].T)
            L.append("  %s -%s: %d cells before the stream; %d in-member GATE items; tau_oos %.5f, tau_m %.5f; stream TRAIN %d then EVAL"
                     " %d; L_m %d" % (ARM_NAME[arm], m, int(keep.sum()), int(gin.sum()), order_stat(g_max, 1 - TPR),
                                      order_stat(g_mar, P_M), int((W["tsrc"] == m).sum()), int((W["esrc"] == m).sum()),
                                      int(W["ksrc"][m])))
    return L


def out_paths(out_dir=None):
    d = out_dir or P(OUT_REL)
    return os.path.join(d, OUTCOME), os.path.join(d, ITEMS_CSV)


def dry_run(out=print, out_dir=None):
    say = out
    header(say, "--dry-run")
    pool_line(say)
    denominators(say)
    prog = _PROG[0]
    found = bool(REG_RE.search(open(prog, encoding="utf-8").read())) if os.path.isfile(prog) else False
    say("REGISTRATION heading %s in %s" % ("FOUND" if found else "NOT FOUND (--run would refuse)", prog))
    po, pc = out_paths(out_dir)
    say("OUTPUTS (write-once, mode x): %s %s; %s %s" % (po, "EXISTS (--run would refuse)" if os.path.exists(po) else "absent",
                                                        pc, "EXISTS (--run would refuse)" if os.path.exists(pc) else "absent"))
    W = build_world(_LOAD[0](say), say)
    say("CELLS: tree %d (%s); k-means %d; per-source k %s" % (
        len(W["arms"]["tree"]["ids"]), ", ".join(sorted(W["single"])) + " one-cell" if W["single"] else "no one-cell member",
        len(W["arms"]["km"]["ids"]), ", ".join("%s %d" % (s, W["ksrc"][s]) for s in W["sources"])))
    for s in W["sources"]:
        say("  source %-12s EVAL %d (components %d), TRAIN %d, GATE %d" % (
            s, int((W["esrc"] == s).sum()), len(set(W["ecomp"][W["esrc"] == s].tolist())), int((W["tsrc"] == s).sum()),
            int((W["gsrc"] == s).sum())))
    say("THRESHOLDS (GATE only; no EVAL statistic of the replay):")
    for ln in thresholds_lines(W):
        say(ln)
    say("DRY-RUN: nothing written; no OL1 / OL2 statistic computed or printed.")
    hit("DRY.DONE")
    return 0


def run(out=print, out_dir=None):
    pre = []

    def say(s_):
        pre.append(s_)
        out(s_)
    header(say, "--run")
    po, pc = out_paths(out_dir)
    for p in (po, pc):
        if os.path.exists(p):
            hit("REFUSE.WRITE_ONCE")
            refuse("%s exists (write-once); refused before any read" % p)
    pool_line(say)
    prog = _PROG[0]
    if not (os.path.isfile(prog) and REG_RE.search(open(prog, encoding="utf-8").read())):
        hit("REFUSE.REG")
        refuse("no line of %s starts with the registered heading %r" % (prog, REG_HEADING[:80]))
    say("REGISTRATION heading FOUND (line-anchored) in %s" % prog)
    denominators(say)
    W = build_world(_LOAD[0](say), say)
    R = compute(W)
    L = outcome_lines(W, R, pre[:])
    os.makedirs(os.path.dirname(po), exist_ok=True)
    text = "\n".join(L) + "\n"
    with open(po, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(pc, "x", encoding="utf-8", newline="\n") as f:
        f.write(items_text(W, R))
    for ln in L[len(pre):]:
        out(ln)
    out("WROTE (write-once) %s sha256 %s; %s sha256 %s (never committed: pin + backup)" % (po, sha256_bytes(po), pc, sha256_bytes(pc)))
    hit("RUN.DONE")
    return R


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--data-root", default=None, help="root of experiment_results/ and the DBs (default: this checkout)")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if a.mutants:
        return run_mutants()
    if a.data_root and os.path.abspath(a.data_root) != os.path.abspath(UA._ROOT[0]):
        refuse("--data-root %s was not applied before the readers imported (UA root %s)" % (a.data_root, UA._ROOT[0]))
    if a.dry_run:
        return dry_run(out)
    run(out)
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────

FX_SOURCES = ("AA", "BB", "CC", "DD")


def _unit(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def _fx_parts(variant="sep", seed=3):
    """A synthetic world, dim 10. Sources AA (2 leaves: AA/a, AA/b), BB (2 leaves: BB/c, BB/d), CC (one-cell: CC/x), DD (1 leaf,
    DD/y; a split member with a single leaf). 'sep': every source on its own axes (a held-out member is orthogonal to the rest);
    'absorb': BB/c sits next to AA/b and BB/d between AA/a and AA/b (absorption, margin-only buffering, mean motion that flips
    noiseless boundary AA/a items); 'misname': 'sep' with AA:n2's engine name AA/a (batch tree and batch k-means then differ);
    'nobuf': 'sep' with GATE items off every axis (tau_oos and tau_m near 0: nothing is buffered, the empty-buffer path)."""
    rng = np.random.default_rng(seed)
    dim = 10
    E = np.eye(dim)
    ax = {"AA/a": E[0], "AA/b": E[1], "BB/c": E[2], "BB/d": E[3], "CC/x": E[4], "DD/y": E[5]}
    if variant == "evalheavy":                                  # DD/z: 1 TRAIN, 12 EVAL items beside DD/y (buffer naming reads TRAIN only)
        ax["DD/z"] = _unit(E[5] + 0.3 * E[8])
    if variant in ("absorb", "stiff", "motion"):                          # BB/c sits next to AA/b (cos 0.989); boundary AA/a items below
        ax["BB/c"] = _unit(E[2] * 0.35 + E[1] * 0.94)
        if variant == "absorb":                                 # stiff keeps BB/d on its own axis: churn then comes from mean motion only
            ax["BB/d"] = _unit(E[0] * 0.70 + E[1] * 0.70 + E[3] * 0.25)
    classes = sorted(ax)
    noise = 0.08 if variant in ("absorb", "stiff", "motion") else 0.12

    def draw(cls, k):
        if variant == "broad" and cls == "CC/x":               # the one-cell source is bimodal: its e5-side items are nearest DD's leaf
            return [_unit((E[4] if q % 2 == 0 else _unit(E[5] * 0.9 + E[4] * 0.3)) + noise * rng.standard_normal(dim))
                    for q in range(k)]
        return [_unit(ax[cls] + noise * rng.standard_normal(dim)) for _ in range(k)]
    Xt, yt, Xe, ye, Xg, yg, titems, eitems, ecomp = [], [], [], [], [], [], [], [], []
    ntr = {"AA/a": 14, "AA/b": 12, "BB/c": 10, "BB/d": 9, "CC/x": 8, "DD/y": 7, "DD/z": 1}
    nev = {"AA/a": 7, "AA/b": 6, "BB/c": 6, "BB/d": 5, "CC/x": 4, "DD/y": 4, "DD/z": 12}
    ngt = {"AA/a": 4, "AA/b": 4, "BB/c": 3, "BB/d": 3, "CC/x": 3, "DD/y": 3, "DD/z": 1}
    comp = 0
    for cls in classes:
        for v in draw(cls, ntr[cls]):
            Xt.append(v)
            yt.append(classes.index(cls))
            titems.append("t%03d" % len(titems))
        for k, v in enumerate(draw(cls, nev[cls])):
            Xe.append(v)
            ye.append(classes.index(cls))
            eitems.append("e%03d" % len(eitems))
            ecomp.append(comp)
            if k % 3 != 1:                                     # some two-item components
                comp += 1
        comp += 1
        if variant in ("absorb", "stiff", "motion") and cls == "AA/a":   # noiseless boundary items between AA/a and AA/b (filed AA/a)
            for _k in range(4):
                Xe.append(_unit(E[0] * 0.7105 + E[1] * 0.7037))
                ye.append(classes.index(cls))
                eitems.append("e%03d" % len(eitems))
                ecomp.append(comp)
                comp += 1
        for v in draw(cls, ngt[cls]):
            Xg.append(v)
            yg.append(classes.index(cls))
        if variant in ("absorb", "stiff", "motion") and cls == "AA/a":   # low-score, low-margin GATE items (they set tau_oos / tau_m low)
            for _k in range(4):
                Xg.append(_unit(E[0] * 0.70 + E[1] * 0.70 + E[6] * 0.2 * (_k + 1)))
                yg.append(classes.index(cls))
    Xt, Xe = np.vstack(Xt), np.vstack(Xe)
    yt, ye = np.array(yt), np.array(ye)
    # leaves of split members = TRAIN class means (n = TRAIN count); CC one-cell; DD a single leaf
    leaves, leaf_dom = {}, {}
    nid = {"AA/a": "AA:n1", "AA/b": "AA:n2", "BB/c": "BB:n1", "BB/d": "BB:n2", "DD/y": "DD:n1"}
    for cls, u in nid.items():
        m = yt == classes.index(cls)
        s = Xt[m].sum(axis=0)
        leaves[u] = (s / np.linalg.norm(s), int(m.sum()) + 2)       # directQueries != TRAIN count, as in the engine
        leaf_dom[u] = (cls, int(m.sum()))
    leaf_dom["CC:n0"] = ("CC/x", ntr["CC/x"])
    if variant == "misname":
        leaf_dom["AA:n2"] = ("AA/a", 3)
    if variant == "stiff":                                      # the tree's AA/b leaf tilted away from AA/a: tree churn != k-means churn
        leaves["AA:n2"] = (_unit(leaves["AA:n2"][0] - 0.35 * E[0]), leaves["AA:n2"][1])
    if variant == "nobuf":
        Xg = [_unit(E[7] + 0.3 * rng.standard_normal(dim) * (np.arange(dim) >= 6)) for _ in Xg]
    single = {"CC": "CC:n0"}
    ksrc = {"AA": 2, "BB": 2, "CC": 1, "DD": 1}
    # af cells: flatLeaf over split leaves (CC by source)
    ids = sorted(leaves)
    M = np.vstack([leaves[u][0] for u in ids])
    cells_af = {}
    for i, it in enumerate(eitems):
        cells_af[it] = "CC:n0" if classes[ye[i]].startswith("CC") else ids[int(np.argmax(Xe[i] @ M.T))]
    for j, it in enumerate(titems):
        cells_af[it] = "CC:n0" if classes[yt[j]].startswith("CC") else ids[int(np.argmax(Xt[j] @ M.T))]
    name = {u: leaf_dom[u][0] for u in list(ids) + ["CC:n0"]}
    efl = np.array([int(name[cells_af[it]] == classes[ye[i]]) for i, it in enumerate(eitems)])
    parts = dict(classes=classes, Xt=Xt, yt=yt, titems=titems, Xe=Xe, ye=ye, eitems=eitems, ecomp=np.array(ecomp), efl=efl,
                 leaves=leaves, leaf_dom=leaf_dom, single=single, ksrc=ksrc, cells_af=cells_af, k0_cells=None,
                 Xg=np.vstack(Xg), yg=np.array(yg), policy=None)
    # K_0 cells from the same us_fit (the identity the real reader checks against k_cells_s0.tsv)
    tsrc = np.array([src_of(classes[i]) for i in yt])
    C, csrc, cloc, lab, fits = UA.us_fit(FM.unit_rows(Xt), tsrc, ksrc, FX_SOURCES, KM_SEED)
    parts["k0_cells"] = {it: "K%d:%s:%03d" % (KM_SEED, csrc[lab[j]], cloc[lab[j]]) for j, it in enumerate(titems)}
    pol = dict(best_single="M0", tree_cell={u: ("M1" if k % 2 else "M2") for k, u in enumerate(list(ids) + ["CC:n0"])},
               xtree_cell={"K0": {"K0:%s:%03d" % (csrc[g], cloc[g]): ("M1" if g % 2 else "M3") for g in range(len(C))}})
    parts["policy"] = None if variant == "evalheavy" else pol     # evalheavy: the absent-policy path (decision churn NOT COMPUTED)
    # batch identity targets of the fixture (independent: plain loops)
    knames = {}
    for g in range(len(C)):
        so = csrc[g]
        ys = [int(yt[j]) for j in range(len(yt)) if lab[j] == g]
        knames[g] = GB.majority(ys, classes)
    kok = []
    for i in range(len(ye)):
        so = src_of(classes[ye[i]])
        if so in single:
            g = [h for h in range(len(C)) if csrc[h] == so][0]
        else:
            best, g = -9.0, -1
            for h in range(len(C)):
                if csrc[h] in single:
                    continue
                v = float(np.dot(FM.unit_rows(Xe[i:i + 1])[0], C[h]))
                if v > best:
                    best, g = v, h
        kok.append(int(knames[g] == ye[i]))
    reg_fx = dict(REG, sources=FX_SOURCES, members=(), dim=dim, n_eval=len(ye), n_comp=len(set(ecomp)), n_train=len(yt),
                  id_p_fl="%.4f" % efl.mean(), id_p_k0="%.4f" % np.mean(kok), ksrc=ksrc)
    ob_t, ob_k = _oracle_batch(parts, "tree", reg_fx), _oracle_batch(parts, "km", reg_fx)
    reg_fx["id_p_fl_all"] = "%.4f" % np.mean(list(ob_t.values()))
    reg_fx["id_p_k0_all"] = "%.4f" % np.mean(list(ob_k.values()))
    return parts, reg_fx


@contextlib.contextmanager
def _swapped(parts, reg_fx, pool=None, prog=None):
    saved = (_LOAD[0], _POOL[0], _PROG[0], _REG[0])
    _LOAD[0] = lambda say: parts
    _POOL[0] = pool or (lambda p: (0, "fixture pool check OK"))
    _PROG[0] = prog
    _REG[0] = reg_fx
    try:
        yield
    finally:
        _LOAD[0], _POOL[0], _PROG[0], _REG[0] = saved


def _fx_prog(tmp, with_heading=True):
    p = os.path.join(tmp, "prog.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write("preamble\n" + (REG_HEADING + " ... (fixture)\n" if with_heading else "## Registered other\n") + "tail\n")
    return p


def _capture(fn, *a, **k):
    buf = []
    r = fn(*a, out=buf.append, **k)
    return "\n".join(buf), r


def _need(text, *needles):
    for nd in needles:
        if nd not in text:
            raise AssertionError("missing %r" % nd)


def _oracle_cells(parts, arm, reg_fx, init="mean"):
    """[id, src, mbar, n, name, cdom] per cell; init 'mean': mbar = |mean of the cell's unit TRAIN rows| x its direction, n = their
    count (C-1); 'unit': mbar = the unit direction (tree n = directQueries, k-means n = the count)."""
    classes = parts["classes"]
    Xt = [_unit(v) for v in parts["Xt"]]
    yt = list(parts["yt"])
    S = lambda c: src_of(classes[c])    # noqa: E731
    cells = []
    if arm == "tree":
        for so in sorted(reg_fx["sources"]):
            if so in parts["single"]:
                vs = [Xt[j] for j in range(len(yt)) if S(yt[j]) == so]
                cells.append([parts["single"][so], so, _unit(np.sum(vs, axis=0)), float(len(vs)), None, None])
            else:
                for u in sorted(k for k in parts["leaves"] if k.split(":")[0] == so):
                    cells.append([u, so, _unit(parts["leaves"][u][0]), float(parts["leaves"][u][1]), None, None])
        for cl in cells:
            nm, cnt = parts["leaf_dom"][cl[0]]
            cl[4], cl[5] = classes.index(nm), cnt
            if init == "mean":
                rows = [Xt[j] for j, it in enumerate(parts["titems"])
                        if (parts["single"].get(S(yt[j])) if S(yt[j]) in parts["single"] else parts["cells_af"][it]) == cl[0]]
                cl[2] = cl[2] * (np.linalg.norm(np.sum(rows, axis=0)) / len(rows))
                cl[3] = float(len(rows))
    else:
        tsrc = np.array([S(c) for c in yt])
        C, csrc, cloc, lab, fits = UA.us_fit(np.vstack(Xt), tsrc, reg_fx["ksrc"], reg_fx["sources"], KM_SEED)
        for g in range(len(C)):
            ys = [yt[j] for j in range(len(yt)) if lab[j] == g]
            nm = GB.majority(ys, classes)
            rows = [Xt[j] for j in range(len(yt)) if lab[j] == g]
            mb = np.array(C[g]) * (np.linalg.norm(np.sum(rows, axis=0)) / len(rows)) if init == "mean" else np.array(C[g])
            cells.append(["K0:%s:%03d" % (csrc[g], cloc[g]), csrc[g], mb, float(len(ys)), nm, sum(1 for y in ys if y == nm)])
    return cells


def _oracle_batch(parts, arm, reg_fx):
    """{EVAL index: correct} of the SYMMETRIC batch filing: nearest of all six members' cells (C-2), plain loops."""
    cells = _oracle_cells(parts, arm, reg_fx, "unit")
    out = {}
    for i, v in enumerate(parts["Xe"]):
        x = _unit(v)
        sc = [float(np.dot(x, _unit(cl[2]))) for cl in cells]
        out[i] = int(cells[sc.index(max(sc))][4] == int(parts["ye"][i]))
    return out


def _oracle_replay(parts, arm, m, reg_fx, init="mean"):
    """Independent plain-loop implementation of the registered procedure (lists and dot products; no shared code but
    ukm_fit for the buffer and us_fit for K_0, which are the registered instruments)."""
    classes = parts["classes"]
    Xt = [_unit(v) for v in parts["Xt"]]
    Xe = [_unit(v) for v in parts["Xe"]]
    Xg = [_unit(v) for v in parts["Xg"]]
    yt, ye, yg = list(parts["yt"]), list(parts["ye"]), list(parts["yg"])
    S = lambda c: src_of(classes[c])    # noqa: E731
    cells = _oracle_cells(parts, arm, reg_fx, init)
    cells = [cl for cl in cells if cl[1] != m]
    unitc = lambda cl: _unit(cl[2])     # noqa: E731

    def scores(x):
        return [float(np.dot(x, unitc(cl))) for cl in cells]

    gmax, gmar = [], []
    for x, y in zip(Xg, yg):
        if S(y) == m:
            continue
        s = sorted(scores(x), reverse=True)
        gmax.append(s[0])
        gmar.append(s[0] - s[1])
    gmax.sort()
    gmar.sort()
    t_o, t_m = gmax[int(np.floor(0.05 * len(gmax)))], gmar[int(np.floor(0.20 * len(gmar)))]
    ein = [i for i in range(len(ye)) if S(ye[i]) != m]
    eout = [i for i in range(len(ye)) if S(ye[i]) == m]
    tout = [j for j in range(len(yt)) if S(yt[j]) == m]
    before = {}
    for i in ein:
        s = scores(Xe[i])
        before[i] = cells[s.index(max(s))][0]
    rng = np.random.default_rng(ORDER_SEED)
    order = [("T", int(j)) for j in rng.permutation(np.array(tout, dtype=int))] + \
            [("E", int(i)) for i in rng.permutation(np.array(eout, dtype=int))]
    absorbed = [Counter() for _ in cells]
    buf = []
    for sd, i in order:
        x = Xt[i] if sd == "T" else Xe[i]
        s = scores(x)
        j = s.index(max(s))
        rest = s[:j] + s[j + 1:]
        if s[j] < t_o or s[j] - max(rest) < t_m:
            buf.append((sd, i))
            continue
        cl = cells[j]
        cl[2] = cl[2] + (x - cl[2]) / (cl[3] + 1.0)
        cl[3] += 1.0
        if sd == "T":
            absorbed[j][yt[i]] += 1
    for j, cnt in enumerate(absorbed):
        if cnt:
            top = max(cnt.values())
            cb = sorted([k for k, v in cnt.items() if v == top], key=lambda k: classes[k])[0]
            if top > cells[j][5]:
                cells[j][4] = cb
    newc = []
    kb = min(int(reg_fx["ksrc"][m]), len(buf))
    if kb:
        Xb = np.vstack([Xt[i] if sd == "T" else Xe[i] for sd, i in buf])
        fit, _t = GB.ukm_fit(Xb, kb, BUF_SEED)
        for g in range(kb):
            ys = [yt[i] for (sd, i), lb in zip(buf, fit["labels"]) if sd == "T" and lb == g]
            newc.append(["BUF:%s:%s:%03d" % (arm, m, g), m, np.array(fit["centers"][g]), 0.0, GB.majority(ys, classes), 0])
    allc = cells + newc

    def file_all(x):
        s = [float(np.dot(x, _unit(cl[2]))) for cl in allc]
        return allc[s.index(max(s))]
    ok = {i: int(file_all(Xe[i])[4] == ye[i]) for i in eout}
    def file_means(x):
        s = [float(np.dot(x, _unit(cl[2]))) for cl in cells]
        return cells[s.index(max(s))]
    churn = [int(file_means(Xe[i])[0] != before[i]) for i in ein]             # DECIDING: the five-member graft (C-3)
    churn_all = [int(file_all(Xe[i])[0] != before[i]) for i in ein]
    churn_vec = np.array(churn, dtype=np.float64)
    return dict(ok=ok, churn=float(np.mean(churn)), churn_vec=churn_vec, churn_all=float(np.mean(churn_all)), ein=ein,
                n_buf=len(buf), t_o=t_o, t_m=t_m, kb=kb)


def st_branches():
    # OL1 boundaries (TOST strict ends; DIFFERENT |D| > 0.020 strict; 95% touching 0)
    assert ol1_word(0.0, 0.0) == "EQUIVALENT"
    assert ol1_word(0.0, 0.020 / Z90) == "NEITHER"                      # 90% end exactly at 0.020: not strictly inside
    assert ol1_word(0.0, 0.0199 / Z90) == "EQUIVALENT"
    assert ol1_word(-0.0300, 0.005) == "LOSS"
    assert ol1_word(+0.0300, 0.005) == "GAIN"
    assert ol1_word(-0.020, 0.001) == "NEITHER"                         # |D| = 0.020 is not > 0.020
    assert ol1_word(-0.0201, 0.0201 / Z95) == "NEITHER"                 # 95% touches 0 (hi = 0): not excluding
    assert ol1_word(-0.0201, 0.0200 / Z95) == "LOSS"
    assert ol1_word(-0.025, 0.02) == "NEITHER"
    # OL2
    assert ol2_word([(0.001, 0.005), (0.0, 0.020)]) == "STABLE"         # upper exactly 0.020 counts (<=)
    assert ol2_word([(0.001, 0.005), (0.0, 0.0201)]) == "UNDETERMINED"
    assert ol2_word([(0.0201, 0.03), (0.0, 0.001)]) == "NOT-STABLE"
    assert ol2_word([(0.020, 0.03)]) == "UNDETERMINED"                  # point exactly 0.020 is not > 0.020
    try:
        ol2_word([(0.03, 0.01)])
        raise AssertionError("both-fire not refused")
    except SystemExit as e:
        assert "[ORL-OL2-BOTH]" in str(e)
    assert f_ol("NOT-STABLE") is True and f_ol("STABLE") is False and f_ol("UNDETERMINED") is False
    assert ol1_of(dict(d=-0.025, se=0.02, lo=-0.03, hi=-0.02)) == "NEITHER"   # the SD decides, not the percentile width
    assert ol1_of(dict(d=-0.025, se=0.002, lo=-0.06, hi=0.01)) == "LOSS"
    W3 = dict(sources=("AA", "BB", "CC"))
    T3 = dict(st=dict(d=-0.03, lo=-0.04, hi=-0.02, se=0.005), ol1="LOSS", ol2="STABLE",
              per={m: dict(churn=dict(d=0.004, hi=0.006)) for m in W3["sources"]},
              reps={m: dict(auroc=x) for m, x in zip(W3["sources"], (0.61, 0.62, 0.0))})
    _need("\n".join(pred_lines(W3, dict(arms=dict(tree=T3)))), "observed 0.6100 -> HELD")      # median, not mean 0.41
    per = {"AA": dict(churn=dict(d=0.001, hi=0.004)), "BB": dict(churn=dict(d=0.010, hi=0.025))}
    assert ol2_of(per, ("AA", "BB")) == "UNDETERMINED"                 # point <= 0.020, upper > 0.020 in the SECOND replay
    per["BB"]["churn"] = dict(d=0.030, hi=0.040)
    assert ol2_of(per, ("AA", "BB")) == "NOT-STABLE"
    per["BB"]["churn"] = dict(d=0.0, hi=0.0)
    assert ol2_of(per, ("AA", "BB")) == "STABLE"
    assert abs(brier(PROB_OL1, "LOSS") - ((0.55) ** 2 + 0.40 ** 2 + 0.15 ** 2)) < 1e-12
    assert abs(brier(PROB_OL1, "GAIN") - (0.45 ** 2 + 0.40 ** 2 + 0.15 ** 2 + 1.0)) < 1e-12
    assert order_stat([5, 1, 4, 2, 3], 0.05) == 1 and order_stat(list(range(20)), 0.05) == 1 and order_stat(list(range(10)), 0.20) == 2
    mx, mg = top_margin(np.array([[0.1, 0.5, 0.3], [0.2, 0.2, 0.0]]))
    assert np.allclose(mx, [0.5, 0.2]) and np.allclose(mg, [0.2, 0.0])
    assert abs(auroc([3, 2], [1, 2]) - (1 + 1 + 1 + 0.5) / 4) < 1e-12
    # synthetic R through every print branch of pred_lines / falsifier_lines / ol1_lines / ol2_lines
    W = dict(sources=("AA", "BB"))

    def st(d, lo=None, hi=None, se=0.004):
        return dict(d=d, lo=d - 0.01 if lo is None else lo, hi=d + 0.01 if hi is None else hi, se=se, deff=1.1, n=100, G=90,
                    n_eff=91, mde=0.01, disc=0.1)
    for ol1, d, se, want in (("EQUIVALENT", 0.001, 0.004, "OL1: EQUIVALENT"), ("LOSS", -0.04, 0.005, "OL1: DIFFERENT (LOSS)"),
                             ("GAIN", 0.04, 0.005, "OL1: DIFFERENT (GAIN)"), ("NEITHER", -0.019, 0.01, "OL1: NEITHER")):
        a = dict(st=st(d, se=se), p_on=0.7, p_b=0.7 - d, ol1=ol1, st_mir=st(d - 0.008, se=se), p_b_mir=0.708 - d, ol1_mir="NEITHER",
                 st_split=st(d + 0.001), d_unit=d + 0.002)
        assert ol1_word(d, se) == ol1
        txt = "\n".join(ol1_lines(a, True))
        _need(txt, want, "D = P_fl(ONLINE) 0.7000 - P_fl(BATCH) %.4f = %+.4f" % (0.7 - d, d),
              "against the MIRRORED batch filing (one-cell source filed by source, P_fl %.4f): D %+.4f," % (0.708 - d, d - 0.008),
              "form-word NEITHER", "one-cell replays excluded): %+.4f" % (d + 0.001), "(the first build's rule): %+.4f" % (d + 0.002))
    for churns, want in (([(0.001, 0.004), (0.002, 0.006)], "OL2: STABLE: every replay's 95% upper bound <= 0.020 (largest 0.0060, replay -BB)"),
                         ([(0.03, 0.04), (0.002, 0.006)], "OL2: NOT-STABLE: churn point > 0.020 in replay(s) -AA (0.0300)"),
                         ([(0.01, 0.025), (0.002, 0.006)], "OL2: UNDETERMINED: no churn point exceeds 0.020 but replay -AA's 95% upper 0.0250")):
        per = {m: dict(churn=st(p, lo=0.0, hi=h), churn_all=st(0.05, hi=0.06), churn_unit=0.0, churn_all_unit=0.0)
               for m, (p, h) in zip(("AA", "BB"), churns)}
        reps = {m: dict(ein=np.arange(50)) for m in ("AA", "BB")}
        a = dict(per=per, reps=reps, ol2=ol2_word(churns))
        _need("\n".join(ol2_lines(W, a, True)), want)
    for d, ol1, churn, ol2, auc, wants in (
            (-0.03, "LOSS", (0.004, 0.003), "STABLE", (0.8, 0.7),
             ("P1 D -0.030 [-0.080, +0.000]: observed -0.0300 -> HELD", "observed LOSS; Brier 0.4850", "observed 0.0040 / 0.0030 -> HELD",
              "OL2 STABLE 0.80: observed STABLE; Brier 0.0400", "observed 0.7500 -> HELD", "F-OL NOT FIRED: OL2 reads STABLE",
              "addresses stable, new domain filed worse than a rebuild", "BUFFER CAPTURE (DESCRIPTIVE): beyond 2% by buffer capture:",
              "take 0.0500 of replay -AA's in-member addresses while the mean refit alone moves 0.0040")),
            (0.001, "EQUIVALENT", (0.03, 0.0), "NOT-STABLE", (0.5, 0.55),
             ("observed +0.0010 -> FAILED", "observed EQUIVALENT; Brier 1.0850", "-> FAILED (outside: -AA)",
              "OL2 STABLE 0.80: observed NOT-STABLE; Brier 0.6400", "observed 0.5250 -> FAILED", "F-OL FIRES")),
            (-0.081, "LOSS", (0.0, 0.016), "UNDETERMINED", (0.96, 0.97),
             ("observed -0.0810 -> FAILED", "-> FAILED (outside: -BB)", "observed 0.9650 -> FAILED", "addresses not shown stable"))):
        call = (0.05, 0.001) if ol2 == "STABLE" else (0.001, 0.001)
        T = dict(st=st(d), ol1=ol1, ol2=ol2, per={m: dict(churn=st(c), churn_all=st(x, hi=x + 0.01)) for m, c, x in zip(("AA", "BB"), churn, call)},
                 reps={m: dict(auroc=x) for m, x in zip(("AA", "BB"), auc)},
                 ol2_all=ol2_word([(x, x + 0.01) for x in call]))
        R = dict(arms=dict(tree=T))
        txt = "\n".join(pred_lines(W, R) + falsifier_lines(R))
        _need(txt, *wants)
        if ol2 != "NOT-STABLE":
            assert "F-OL FIRES" not in txt
        if ol2 != "STABLE":
            assert "BUFFER CAPTURE" not in txt
        _need(txt, "churns (C-3): DECIDING = means-only")
    # Brier hand values above: LOSS -> 0.55^2+0.40^2+0.15^2 = 0.485; EQUIVALENT -> 0.45^2+0.40^2+0.85^2 = 1.085


def _run_fx(tmp, variant):
    parts, reg_fx = _fx_parts(variant)
    out_dir = os.path.join(tmp, "out_" + variant)
    with _swapped(parts, reg_fx, prog=_fx_prog(tmp)):
        txt, R = _capture(run, out_dir=out_dir)
        W = build_world(parts, lambda s: None)
    return parts, reg_fx, txt, R, W, out_dir


def _check_against_oracle(parts, reg_fx, txt, R, W):
    for arm in ARMS:
        a = R["arms"][arm]
        ob = _oracle_batch(parts, arm, reg_fx)                # the SYMMETRIC batch filing, plain loops (C-2)
        assert all(ob[i] == int(W["batch"][arm][i]) for i in ob), (arm, "symmetric batch")
        diff = np.zeros(len(W["ye"]))
        diff_unit = np.zeros(len(W["ye"]))
        diff_mir = np.zeros(len(W["ye"]))
        for m in FX_SOURCES:
            o = _oracle_replay(parts, arm, m, reg_fx)
            ou = _oracle_replay(parts, arm, m, reg_fx, init="unit")
            r = a["reps"][m]
            assert abs(o["t_o"] - r["tau_oos"]) < 1e-12 and abs(o["t_m"] - r["tau_m"]) < 1e-12, (arm, m, "thresholds")
            assert o["n_buf"] == r["n_buf"], (arm, m, o["n_buf"], r["n_buf"])
            for i, ok in o["ok"].items():
                diff[i] = ok - ob[i]
                diff_mir[i] = ok - int(parts["efl"][i]) if arm == "tree" else diff_mir[i]
            for i, ok in ou["ok"].items():
                diff_unit[i] = ok - ob[i]
            assert abs(o["churn"] - a["per"][m]["churn"]["d"]) < 1e-12, (arm, m, o["churn"], a["per"][m]["churn"]["d"])
            assert abs(o["churn_all"] - a["per"][m]["churn_all"]["d"]) < 1e-12, (arm, m, "all", o["churn_all"])
            assert abs(ou["churn"] - a["per"][m]["churn_unit"]) < 1e-12, (arm, m, "unit", ou["churn"])
            up = GB.stat(o["churn_vec"], W["ecomp"][o["ein"]])["hi"]          # the registered instrument on the oracle's vector
            if arm == "tree":
                _need(txt, "  replay -%s: churn %.4f, 95%% upper %.4f (" % (m, o["churn"], up),
                      "beside: all-cells churn %.4f (upper" % o["churn_all"])
            else:
                assert abs(up - a["per"][m]["churn"]["hi"]) < 1e-12, (arm, m, up)
            _need(txt, "buffer k %d (L_m %d)" % (o["kb"], int(reg_fx["ksrc"][m])))
            _need(txt, "  -%s (%s): streamed" % (m, ARM_NAME[arm]), "buffered %d (" % o["n_buf"])
        d = float(diff.mean())
        assert abs(d - a["st"]["d"]) < 1e-12, (arm, d, a["st"]["d"])
        assert abs(float(diff_unit.mean()) - a["d_unit"]) < 1e-12, (arm, "unit D")
        if arm == "tree":
            _need(txt, "= %+.4f; TOST 90%%" % d, "rule): %+.4f" % float(diff_unit.mean()),
                  "P_fl %.4f): D %+.4f," % (float(np.mean(parts["efl"])), float(diff_mir.mean())))
    return True


def st_e2e_sep(tmp):
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "sep")
    _check_against_oracle(parts, reg_fx, txt, R, W)
    T = R["arms"]["tree"]
    # by construction: a held-out member is orthogonal to every in-member cell -> every streamed item is buffered, no mean moves,
    # buffer k-means at L_m recovers its classes -> online filing = batch filing; churn 0 (buffer cells sit on other axes)
    for m in FX_SOURCES:
        r = T["reps"][m]
        assert r["n_buf"] == r["n_stream"] and r["filed"] == 0, (m, r["n_buf"], r["n_stream"])
        assert T["per"][m]["churn"]["d"] == 0.0
    assert T["st"]["d"] == 0.0 and T["ol1"] == "EQUIVALENT" and T["ol2"] == "STABLE"
    _need(txt, "= +0.0000; TOST 90% [+0.0000, +0.0000]", "OL1: EQUIVALENT: the 90% interval [+0.0000, +0.0000] lies inside +/-0.020",
          "OL2: STABLE: every replay's 95% upper bound <= 0.020 (largest 0.0000", "F-OL NOT FIRED: OL2 reads STABLE",
          "PREDICTION P1 D -0.030 [-0.080, +0.000]: observed +0.0000 -> HELD", "observed EQUIVALENT; Brier 1.0850",
          "  replay -AA: churn 0.0000, 95% upper 0.0000", "  replay -DD: churn 0.0000", "-> HELD (all six in band)",
          "DENOMINATOR (OL1): the held-out members' EVAL items pooled over 4 replays = %d items" % len(W["ye"]))
    assert "IFEVAL's case" not in txt
    with open(os.path.join(out_dir, OUTCOME), encoding="utf-8") as f:
        body = f.read()
    assert body.splitlines()[0].startswith("POOL %s" % POOL), body.splitlines()[0]
    _need(body, "OL1: EQUIVALENT", "OL2: STABLE", "F-OL NOT FIRED", "decision churn 0.0000")
    rows = open(os.path.join(out_dir, ITEMS_CSV), encoding="utf-8").read().splitlines()
    assert rows[0] == "item_id,replay,role,arm,cell_before,cell_after_means,cell_after_all,online_ok,batch_ok,batch_mirrored_ok"
    n_in = sum(len(R["arms"]["tree"]["reps"][m]["ein"]) for m in FX_SOURCES)
    assert len(rows) - 1 == 2 * (len(W["ye"]) + n_in), (len(rows), len(W["ye"]), n_in)


def st_e2e_absorb(tmp):
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "absorb")
    _check_against_oracle(parts, reg_fx, txt, R, W)
    T = R["arms"]["tree"]
    r = T["reps"]["BB"]
    assert r["filed"] > 0 and r["n_buf"] < r["n_stream"], ("absorb fixture absorbs nothing", r["filed"], r["n_buf"])
    d = T["st"]["d"]
    want_ol1 = ol1_word(d, T["st"]["se"])
    assert T["ol1"] == want_ol1
    pairs = [(T["per"][m]["churn"]["d"], T["per"][m]["churn"]["hi"]) for m in FX_SOURCES]
    assert T["ol2"] == ol2_word(pairs)
    assert T["ol1"] == "LOSS", (T["ol1"], d, T["st"]["se"])
    # C-3: here only buffer capture moves addresses (BB/d's provisional cells take boundary AA/a items); the mean refit moves none
    assert T["ol2"] == "STABLE" and T["ol2_all"] == "NOT-STABLE", (pairs, T["ol2_all"])
    cb = T["per"]["BB"]
    _need(txt, "OL1: DIFFERENT (LOSS): |D| %.4f > 0.020" % abs(d), "OL2: STABLE: every replay's 95% upper bound <= 0.020",
          "F-OL NOT FIRED: OL2 reads STABLE on the means-only churn", "  OL1 LOSS limits the replay to 'addresses stable",
          "BUFFER CAPTURE (DESCRIPTIVE): beyond 2%% by buffer capture: the provisional buffer cells take %.4f of replay -BB's"
          " in-member addresses while the mean refit alone moves %.4f" % (cb["churn_all"]["d"], cb["churn"]["d"]))
    assert "F-OL FIRES" not in txt
    # AUROC printed equals an independent pairwise count for replay -BB (tree)
    A = W["arms"]["tree"]
    keep = A["src"] != "BB"
    pos = [float(np.max(W["Xe"][i] @ A["mu"][keep].T)) for i in range(len(W["ye"])) if W["esrc"][i] != "BB"]
    neg = [float(np.max(W["Xe"][i] @ A["mu"][keep].T)) for i in range(len(W["ye"])) if W["esrc"][i] == "BB"]
    au = sum((1.0 if p > q else 0.5 if p == q else 0.0) for p in pos for q in neg) / (len(pos) * len(neg))
    _need(txt, "new-domain OOS AUROC %.4f" % au)


def st_e2e_motion(tmp):
    """Means-only churn > 0.020 (the mean refit flips boundary items): OL2 NOT-STABLE, F-OL FIRES, attributed to the mean refit."""
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "motion")
    _check_against_oracle(parts, reg_fx, txt, R, W)
    T = R["arms"]["tree"]
    c = T["per"]["BB"]["churn"]["d"]
    assert T["ol2"] == "NOT-STABLE" and c > MARGIN, (T["ol2"], c)
    _need(txt, "OL2: NOT-STABLE: churn point > 0.020 in replay(s) -BB (%.4f)" % c,
          "F-OL FIRES: OL2 NOT-STABLE on the means-only churn: the online mean refit moves existing cells' addresses beyond 2%% in"
          " replay -BB (%.4f)" % c, "addresses not shown stable")
    assert "BUFFER CAPTURE" not in txt


def st_update_rule(tmp):
    """C-1 / O3: after k absorptions a cell's mbar = (r n mu + sum x) / (n + k) exactly (no renormalisation of mbar between steps)."""
    parts, reg_fx = _fx_parts("motion")
    _REG_SAVED = _REG[0]
    _REG[0] = reg_fx
    try:
        W = build_world(parts, lambda s: None)
    finally:
        _REG[0] = _REG_SAVED
    for arm in ARMS:
        A = W["arms"][arm]
        r = replay(W, arm, "BB")
        keep = np.flatnonzero(A["src"] != "BB")
        moved = 0
        for jj, j in enumerate(keep):
            k = int(round(r["n_end"][jj] - A["n"][j]))
            if k == 0:
                assert np.allclose(r["mbar"][jj], A["r"][j] * A["mu"][j], atol=1e-13)
                continue
            moved += 1
            # the absorbed items: replay the same order and rule by hand (the filed items of this cell) via the CSV-free route
            want_sum = (r["mbar"][jj] * (A["n"][j] + k) - A["r"][j] * A["n"][j] * A["mu"][j])
            assert np.linalg.norm(want_sum) <= k + 1e-9, (arm, j, "sum of k unit rows longer than k")
            # independent: rebuild the cell's absorbed set from the oracle and compare the closed form
            o = _oracle_cells(parts, arm, reg_fx)
            assert np.allclose(o[j][2], A["r"][j] * A["mu"][j], atol=1e-12) and o[j][3] == A["n"][j], (arm, j, "init")
        assert moved >= 1, (arm, "no cell absorbed anything")
    # direct closed form on a two-step toy: mu = e0, r = 0.5, n = 2; absorb x1 = e1, x2 = e1
    mb, n = 0.5 * np.array([1.0, 0.0]), 2.0
    for x in (np.array([0.0, 1.0]), np.array([0.0, 1.0])):
        mb = mb + (x - mb) / (n + 1.0)
        n += 1.0
    assert np.allclose(mb, (0.5 * 2 * np.array([1.0, 0.0]) + 2 * np.array([0.0, 1.0])) / 4.0)
    # the replay's own update on a constructed world: one cell, every streamed item filed into it
    Wt = _toy_world()
    r = replay(Wt, "tree", "ZZ")
    A = Wt["arms"]["tree"]
    xs = Wt["Xt"][Wt["tsrc"] == "ZZ"].sum(axis=0) + Wt["Xe"][Wt["esrc"] == "ZZ"].sum(axis=0)
    k = int((Wt["tsrc"] == "ZZ").sum() + (Wt["esrc"] == "ZZ").sum())
    assert r["n_buf"] == 0 and r["filed"] == k, (r["n_buf"], r["filed"], k)
    j = 0
    want = (A["r"][j] * A["n"][j] * A["mu"][j] + xs) / (A["n"][j] + k)
    assert np.allclose(r["mbar"][j], want, atol=1e-12), (r["mbar"][j][:3], want[:3])


def _toy_world():
    """Two sources: YY (cells y0 on e0, y1 on e1) and ZZ (streamed; every item near e0 + 0.3 e2, all filed into y0)."""
    dim = 4
    E = np.eye(dim)
    rng = np.random.default_rng(7)
    Xt = np.vstack([_unit(E[0] + 0.05 * rng.standard_normal(dim)) for _ in range(6)] +
                   [_unit(E[1] + 0.05 * rng.standard_normal(dim)) for _ in range(6)] +
                   [_unit(E[0] + 0.3 * E[2] + 0.02 * rng.standard_normal(dim)) for _ in range(5)])
    tsrc = np.array(["YY"] * 12 + ["ZZ"] * 5)
    yt = np.array([0] * 6 + [1] * 6 + [2] * 5)
    Xe = np.vstack([_unit(E[0] + 0.3 * E[2] + 0.02 * rng.standard_normal(dim)) for _ in range(3)] + [E[0], E[1]])
    esrc = np.array(["ZZ"] * 3 + ["YY"] * 2)
    ye = np.array([2, 2, 2, 0, 1])
    mu = np.vstack([_unit(Xt[:6].sum(axis=0)), _unit(Xt[6:12].sum(axis=0)), _unit(Xt[12:].sum(axis=0))])
    r = np.array([np.linalg.norm(Xt[:6].mean(axis=0)), np.linalg.norm(Xt[6:12].mean(axis=0)), np.linalg.norm(Xt[12:].mean(axis=0))])
    tree = dict(ids=["YY:0", "YY:1", "ZZ:0"], src=np.array(["YY", "YY", "ZZ"]), mu=mu, n=np.array([6, 6, 5]), r=r,
                name=np.array([0, 1, 2]), cdom=np.array([6, 6, 5]), policy=None, fallback=None)
    Xg = np.vstack([E[3]] * 4)                                   # GATE off every cell: tau_oos, tau_m near 0 (nothing buffered)
    return dict(classes=["YY/a", "YY/b", "ZZ/c"], sources=("YY", "ZZ"), single={}, ksrc={"YY": 2, "ZZ": 1}, Xt=Xt, yt=yt, tsrc=tsrc,
                Xe=Xe, ye=ye, esrc=esrc, ecomp=np.arange(5), Xg=Xg, gsrc=np.array(["YY"] * 4), arms={"tree": tree})


def st_e2e_broad(tmp):
    """C-2: the one-cell source's items reach another cell under the symmetric batch filing: the deciding batch differs from the
    mirrored one, both D values printed and equal to the oracle's."""
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "broad")
    assert np.any(W["batch"]["tree"] != W["batch_mir"]["tree"]), "broad fixture: symmetric = mirrored"
    assert reg_fx["id_p_fl_all"] != reg_fx["id_p_fl"], (reg_fx["id_p_fl_all"], reg_fx["id_p_fl"])
    _check_against_oracle(parts, reg_fx, txt, R, W)
    _need(txt, "IDENTITY (tree, symmetric): batch flatLeaf over all", "P_fl %s" % reg_fx["id_p_fl_all"],
          "one-cell replays excluded): ")


def st_e2e_misname(tmp):
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "misname")
    assert np.any(W["batch"]["tree"] != W["batch"]["km"]), "misname fixture: batch arms do not differ"
    _check_against_oracle(parts, reg_fx, txt, R, W)
    # AA held out: the batch tree misnames AA/b's leaf, the online buffer cell is named by TRAIN majority -> D_AA > 0 on AA/b
    T = R["arms"]["tree"]
    nb = int(np.sum(W["ye"] == W["classes"].index("AA/b")))
    assert abs(T["st"]["d"] - nb / len(W["ye"])) < 1e-12, (T["st"]["d"], nb, len(W["ye"]))
    _need(txt, "= %+.4f; TOST 90%%" % (nb / len(W["ye"])))


def st_e2e_nobuf(tmp):
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "nobuf")
    _check_against_oracle(parts, reg_fx, txt, R, W)
    T = R["arms"]["tree"]
    empty = [m for m in FX_SOURCES if T["reps"][m]["n_buf"] == 0]
    assert len(empty) >= 3, [(m, T["reps"][m]["n_buf"]) for m in FX_SOURCES]
    for m in empty:
        r = T["reps"][m]
        assert r["kb"] == 0 and r["filed"] == r["n_stream"], (m, r["kb"], r["filed"])
    _need(txt, "buffer k 0 (L_m 2); buffer purity n/a (no buffer)", "buffered 0 (0.0000;")


def st_e2e_stiff(tmp):
    """The deciding OL1 / OL2 blocks print the TREE arm (the k-means arm differs here: its AA/b centre moves, the tree's does not)."""
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "stiff")
    _check_against_oracle(parts, reg_fx, txt, R, W)
    T, K = R["arms"]["tree"], R["arms"]["km"]
    assert T["per"]["BB"]["churn"]["d"] != K["per"]["BB"]["churn"]["d"], (T["per"]["BB"]["churn"]["d"], K["per"]["BB"]["churn"]["d"])
    assert T["ol2"] != K["ol2"], (T["ol2"], K["ol2"])
    blk = txt.split("--- OL2 (DECIDING")[1].split("--- F-OL ---")[0]
    for m in FX_SOURCES:
        _need(blk, "  replay -%s: churn %.4f, 95%% upper %.4f (" % (m, T["per"][m]["churn"]["d"], T["per"][m]["churn"]["hi"]))
    _need(blk, "OL2: %s" % T["ol2"])
    assert "OL2: %s" % K["ol2"] not in blk
    b1 = txt.split("--- OL1 (DECIDING")[1].split("--- OL2 (DECIDING")[0]
    pr = {"EQUIVALENT": "OL1: EQUIVALENT", "LOSS": "OL1: DIFFERENT (LOSS)", "GAIN": "OL1: DIFFERENT (GAIN)", "NEITHER": "OL1: NEITHER"}
    _need(b1, "= %+.4f; TOST 90%%" % T["st"]["d"], pr[T["ol1"]])
    _need(txt.split("--- F-OL ---")[1].split("--- PREDICTIONS ---")[0], "F-OL %s" % ("FIRES" if T["ol2"] == "NOT-STABLE" else "NOT FIRED"))


def st_e2e_evalheavy(tmp):
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "evalheavy")
    _check_against_oracle(parts, reg_fx, txt, R, W)
    assert txt.count("decision churn NOT COMPUTED (policy absent)") == 2 * len(FX_SOURCES), txt.count("NOT COMPUTED")
    assert "decision churn 0." not in txt
    r = R["arms"]["tree"]["reps"]["DD"]
    assert r["kb"] == 1 and r["buf_eval"] >= 12, (r["kb"], r["buf_eval"])


def st_race(tmp):
    """M25 class: the outcome is opened mode 'x' even after the pre-check (a file appearing in between is never overwritten)."""
    parts, reg_fx = _fx_parts("sep")
    out_dir = os.path.join(tmp, "race")
    po = os.path.join(out_dir, OUTCOME)

    def loader(say):
        os.makedirs(out_dir, exist_ok=True)
        with open(po, "w", encoding="utf-8") as f:
            f.write("PEER\n")
        return parts
    with _swapped(parts, reg_fx, prog=_fx_prog(tmp)):
        _LOAD[0] = loader
        try:
            _capture(run, out_dir=out_dir)
            raise AssertionError("a file appearing after the pre-check was overwritten")
        except FileExistsError:
            pass
    assert open(po, encoding="utf-8").read() == "PEER\n"
    assert not os.path.exists(os.path.join(out_dir, ITEMS_CSV))


def st_identity(tmp):
    parts, reg_fx = _fx_parts("sep")
    cases = []
    p1 = dict(parts, efl=parts["efl"].copy())
    p1["efl"][0] = 1 - p1["efl"][0]
    cases.append(("efl", p1, reg_fx, "[ORL-IDENTITY] the engine-named af cell disagrees"))
    p2 = dict(parts, cells_af=dict(parts["cells_af"]))
    for it in list(p2["cells_af"])[:5]:
        if it.startswith("e") and p2["cells_af"][it] != "CC:n0":
            p2["cells_af"][it] = "AA:n2" if p2["cells_af"][it] != "AA:n2" else "AA:n1"
    cases.append(("i3", p2, reg_fx, "[ORL-IDENTITY]"))
    cases.append(("pfl", parts, dict(reg_fx, id_p_fl="0.0001"), "[ORL-IDENTITY] P_fl(AF-U) "))
    cases.append(("pk0", parts, dict(reg_fx, id_p_k0="0.0001"), "[ORL-IDENTITY] mirrored batch k-means"))
    p5 = dict(parts, k0_cells=dict(parts["k0_cells"]))
    p5["k0_cells"]["t000"] = "K0:ZZ:999"
    cases.append(("k0", p5, reg_fx, "[ORL-IDENTITY] K_0's TRAIN labels differ"))
    cases.append(("denom", parts, dict(reg_fx, n_eval=reg_fx["n_eval"] + 1), "[ORL-DENOM]"))
    cases.append(("ksrc", parts, dict(reg_fx, ksrc=dict(reg_fx["ksrc"], AA=3)), "[ORL-KSRC]"))
    cases.append(("pfl_all", parts, dict(reg_fx, id_p_fl_all="0.0001"), "[ORL-IDENTITY] symmetric batch P_fl(AF-U, nearest of all)"))
    cases.append(("pk0_all", parts, dict(reg_fx, id_p_k0_all="0.0001"), "[ORL-IDENTITY] symmetric batch P(US_0, nearest of all)"))
    p8 = dict(parts, cells_af=dict(parts["cells_af"]))
    p8["cells_af"]["t000"] = "ZZ:nowhere"
    cases.append(("init", p8, reg_fx, "[ORL-INIT] TRAIN item t000"))
    for nm, pp, rr, want in cases:
        out_dir = os.path.join(tmp, "id_" + nm)
        with _swapped(pp, rr, prog=_fx_prog(tmp)):
            try:
                _capture(run, out_dir=out_dir)
                raise AssertionError("identity case %s not refused" % nm)
            except SystemExit as e:
                assert want in str(e), (nm, str(e))
        assert not os.path.exists(os.path.join(out_dir, OUTCOME)), nm


def st_write_once(tmp):
    parts, reg_fx = _fx_parts("sep")
    out_dir = os.path.join(tmp, "wo")
    with _swapped(parts, reg_fx, prog=_fx_prog(tmp)):
        _capture(run, out_dir=out_dir)
        before = open(os.path.join(out_dir, OUTCOME), encoding="utf-8").read()
        try:
            _capture(run, out_dir=out_dir)
            raise AssertionError("second run not refused")
        except SystemExit as e:
            assert "write-once" in str(e)
        assert open(os.path.join(out_dir, OUTCOME), encoding="utf-8").read() == before
    od2 = os.path.join(tmp, "wo2")
    os.makedirs(od2)
    open(os.path.join(od2, ITEMS_CSV), "w").close()
    calls = []
    with _swapped(parts, reg_fx, prog=_fx_prog(tmp), pool=lambda p: (calls.append(p), (0, "x"))[1]):
        try:
            _capture(run, out_dir=od2)
            raise AssertionError("existing items CSV not refused")
        except SystemExit as e:
            assert "write-once" in str(e) and not calls, (str(e), calls)
    assert not os.path.exists(os.path.join(od2, OUTCOME))
    with _swapped(parts, reg_fx, prog=_fx_prog(tmp, with_heading=False)):
        try:
            _capture(run, out_dir=os.path.join(tmp, "wo3"))
            raise AssertionError("missing heading not refused")
        except SystemExit as e:
            assert "registered heading" in str(e)
    buf = []
    with _swapped(parts, reg_fx, prog=_fx_prog(tmp), pool=lambda p: (1, "a writer is open")):
        try:
            run(out=buf.append, out_dir=os.path.join(tmp, "wo4"))
            raise AssertionError("pool rc 1 not refused")
        except SystemExit as e:
            assert "B0-2 pool check failed" in str(e)
    assert buf[0].startswith("POOL %s" % POOL) and any("POOL CHECK (B0-2" in b and "rc 1" in b for b in buf), buf[:3]
    assert not os.path.exists(os.path.join(tmp, "wo4", OUTCOME))


def st_dry_run(tmp):
    parts, reg_fx = _fx_parts("absorb")
    out_dir = os.path.join(tmp, "dry")
    with _swapped(parts, reg_fx, prog=_fx_prog(tmp)):
        txt, rc = _capture(dry_run, out_dir=out_dir)
        W = build_world(parts, lambda s: None)
    assert rc == 0 and txt.splitlines()[0].startswith("POOL %s" % POOL)
    _need(txt, "POOL CHECK (B0-2", "DENOMINATORS (registered): OL1 %d held-out EVAL items in %d components" % (reg_fx["n_eval"], reg_fx["n_comp"]),
          "REGISTRATION heading FOUND", "THRESHOLDS (GATE only", "DRY-RUN: nothing written")
    for bad in ("OL1:", "OL2:", "F-OL", "churn", "PREDICTION"):
        assert bad not in txt, bad
    assert not os.path.exists(out_dir)
    # the printed thresholds equal the replay's (GATE only)
    r = replay(W, "tree", "BB")
    _need(txt, "AF-U tree -BB: %d cells before the stream; %d in-member GATE items; tau_oos %.5f, tau_m %.5f" % (
        len(r["ids"]), r["n_gate"], r["tau_oos"], r["tau_m"]))
    # the REAL constants' denominator line
    buf = []
    denominators(buf.append)
    _need(buf[0], "OL1 6139 held-out EVAL items in 5628 components", "TRAIN 12334", "6153 / 5642")


REGISTERED_BRANCHES = ("OL1.EQUIVALENT", "OL1.LOSS", "OL1.GAIN", "OL1.NEITHER", "OL2.STABLE", "OL2.NOT_STABLE", "OL2.UNDETERMINED",
                       "FOL.FIRES", "FOL.NOT_FIRED", "OL1.LOSS_LIMIT", "P1.HELD", "P1.FAILED", "P2.HELD", "P2.FAILED", "P3.HELD",
                       "P3.FAILED", "REFUSE.OL2_BOTH", "REFUSE.WRITE_ONCE", "REFUSE.REG", "REFUSE.POOL", "REFUSE.EFL", "REFUSE.I3",
                       "REFUSE.PFL", "REFUSE.PK0", "REFUSE.K0", "REFUSE.DENOM", "REFUSE.KSRC", "RUN.DONE", "DRY.DONE",
                       "FOL.CAPTURE", "OL1.SPLIT_ONLY", "REFUSE.PFL_ALL", "REFUSE.PK0_ALL", "REFUSE.INIT")


def st_branch_cover():
    miss = [b for b in REGISTERED_BRANCHES if HIT[b] == 0]
    assert not miss, "print branches never hit: %s" % miss


CASES = (("branches", st_branches, False), ("e2e_sep", st_e2e_sep, True), ("e2e_absorb", st_e2e_absorb, True),
         ("e2e_motion", st_e2e_motion, True), ("update_rule", st_update_rule, True), ("e2e_broad", st_e2e_broad, True),
         ("e2e_misname", st_e2e_misname, True), ("e2e_nobuf", st_e2e_nobuf, True), ("e2e_stiff", st_e2e_stiff, True),
         ("e2e_evalheavy", st_e2e_evalheavy, True), ("race", st_race, True),
         ("identity", st_identity, True), ("write_once", st_write_once, True), ("dry_run", st_dry_run, True),
         ("branch_cover", st_branch_cover, False))


def selftest(only=None, quiet=False):
    HIT.clear()
    for nm, fn, needs_tmp in CASES:
        if only and nm not in only and nm != "branch_cover":
            continue
        if nm == "branch_cover" and only:
            continue
        if needs_tmp:
            tmp = tempfile.mkdtemp(prefix="orl_st_")
            try:
                fn(tmp)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        else:
            fn()
        if not quiet:
            print("%s selftest %-12s OK" % (TAG, nm))
    if not quiet:
        print("%s SELFTEST PASSED (%d cases)" % (TAG, len(CASES)))


# ── mutants (each edits this file's source in memory; the selftest must fail) ──────────────────────────────────────────────

MUTANTS = (
    ("M01 TOST at 95% instead of 90%", "    if lo90 > -margin and hi90 < margin:\n        return \"EQUIVALENT\"",
     "    if lo95 > -margin and hi95 < margin:\n        return \"EQUIVALENT\""),
    ("M02 TOST inclusive ends", "    if lo90 > -margin and hi90 < margin:", "    if lo90 >= -margin and hi90 <= margin:"),
    ("M03 DIFFERENT without |D| > margin", "    if abs(d) > margin and (lo95 > 0 or hi95 < 0):", "    if (lo95 > 0 or hi95 < 0):"),
    ("M04 LOSS / GAIN swapped", "        return \"LOSS\" if d < 0 else \"GAIN\"", "        return \"GAIN\" if d < 0 else \"LOSS\""),
    ("M05 OL2 STABLE by any replay (first-site-only)", "    stable = all(h <= margin for _p, h in pairs)",
     "    stable = any(h <= margin for _p, h in pairs)"),
    ("M06 OL2 upper strict", "    stable = all(h <= margin for _p, h in pairs)", "    stable = all(h < margin for _p, h in pairs)"),
    ("M07 OL2 NOT-STABLE on the upper bound", "    not_stable = any(p > margin for p, _h in pairs)",
     "    not_stable = any(h > margin for _p, h in pairs)"),
    ("M08 F-OL on UNDETERMINED", "    return ol2 == \"NOT-STABLE\"", "    return ol2 != \"STABLE\""),
    ("M09 tau_oos at TPR 0.95 read as the 95th percentile", "    tau_oos, tau_m = order_stat(g_max, 1 - TPR), order_stat(g_mar, P_M)",
     "    tau_oos, tau_m = order_stat(g_max, TPR), order_stat(g_mar, P_M)"),
    ("M10 thresholds from the held-out member's GATE (wrong population)", "    gin = W[\"gsrc\"] != m\n    g_max, g_mar = top_margin(W[\"Xg\"][gin] @ mu0.T)",
     "    gin = W[\"gsrc\"] == m\n    g_max, g_mar = top_margin(W[\"Xg\"][gin] @ mu0.T)"),
    ("M11 buffer on OOS only (margin trigger dropped)", "        if oos or low:\n            buf.append((side, i))",
     "        if oos:\n            buf.append((side, i))"),
    ("M12 no mean update (frozen means)", "        mbar[j1] = mbar[j1] + (x - mbar[j1]) / (n[j1] + 1.0)", "        mbar[j1] = mbar[j1]"),
    ("M13 mean update without the count (x replaces the mean)", "        mbar[j1] = mbar[j1] + (x - mbar[j1]) / (n[j1] + 1.0)",
     "        mbar[j1] = mbar[j1] + (x - mbar[j1]) / 1.0"),
    ("M14 renaming on ties (>= instead of >)", "        if top > cdom[j]:", "        if top >= cdom[j]:"),
    ("M15 buffer k = 1 always", "    kb = min(Lm, len(buf))", "    kb = min(1, len(buf))"),
    ("M16 deciding churn over ALL cells (buffer capture counted; C-3 reverted)", "    churn = (after_mean != before).astype(np.int64)",
     "    churn = (after != before).astype(np.int64)"),
    ("M17 held-out EVAL filed before the stream (initial cells)", "    fm = np.argmax(W[\"Xe\"][eout] @ allC.T, axis=1)",
     "    fm = np.argmax(W[\"Xe\"][eout] @ np.vstack([mu0, Cb]).T, axis=1)"),
    ("M18 OL1 against the k-means batch arm", "            diff[r[\"eout\"]] = r[\"online_ok\"] - W[\"batch\"][arm][r[\"eout\"]]",
     "            diff[r[\"eout\"]] = r[\"online_ok\"] - W[\"batch\"][\"km\"][r[\"eout\"]]"),
    ("M19 stream EVAL before TRAIN", "    order = [(\"T\", int(i)) for i in rng.permutation(tout)] + [(\"E\", int(i)) for i in rng.permutation(eout)]",
     "    order = [(\"E\", int(i)) for i in rng.permutation(eout)] + [(\"T\", int(i)) for i in rng.permutation(tout)]"),
    ("M20 OL2 verdict from the k-means arm in the deciding block", "    L.extend(ol2_lines(W, T, True))", "    L.extend(ol2_lines(W, K, True))"),
    ("M21 F-OL line omitted", "    L.extend(falsifier_lines(R))\n    say(\"--- PREDICTIONS ---\")", "    say(\"--- PREDICTIONS ---\")"),
    ("M22 P1 band exclusive", "def in_band(x, lo, hi):\n    return lo <= x <= hi", "def in_band(x, lo, hi):\n    return lo < x < hi"),
    ("M23 P2 scored on the max only", "    out = [m for m, x in zip(W[\"sources\"], ch) if not in_band(x, PRED_P2[1], PRED_P2[2])]",
     "    out = [m for m, x in zip(W[\"sources\"][:1], ch[:1]) if not in_band(x, PRED_P2[1], PRED_P2[2])]"),
    ("M24 P3 mean instead of median", "    med = float(np.median(au))", "    med = float(np.mean(au))"),
    ("M25 write-once by overwrite", "    with open(po, \"x\", encoding=\"utf-8\", newline=\"\\n\") as f:",
     "    with open(po, \"w\", encoding=\"utf-8\", newline=\"\\n\") as f:"),
    ("M26 write-once check skipped", "        if os.path.exists(p):\n            hit(\"REFUSE.WRITE_ONCE\")",
     "        if False:\n            hit(\"REFUSE.WRITE_ONCE\")"),
    ("M27 eval_fl identity skipped", "    if bad_fl:\n        hit(\"REFUSE.EFL\")", "    if False:\n        hit(\"REFUSE.EFL\")"),
    ("M28 P(US_0) identity skipped", "    if p_k != c[\"id_p_k0\"]:", "    if False:"),
    ("M29 OOS AUROC sign (in-scope as negatives)", "    auc = auroc(S_in0.max(axis=1), (W[\"Xe\"][eout] @ mu0.T).max(axis=1))",
     "    auc = auroc((W[\"Xe\"][eout] @ mu0.T).max(axis=1), S_in0.max(axis=1))"),
    ("M30 Brier misses the GAIN term", "    return float(sum((p - (1.0 if k == outcome else 0.0)) ** 2 for k, p in probs.items()))",
     "    return float(sum((p - (1.0 if k == outcome else 0.0)) ** 2 for k, p in probs.items() if k != \"GAIN\"))"),
    ("M31 one-cell source left out of the online graft", "    keep = np.flatnonzero(A[\"src\"] != m)",
     "    keep = np.flatnonzero((A[\"src\"] != m) & ~np.isin(A[\"src\"], list(W[\"single\"])))"),
    ("M32 pool check result ignored", "    if rc != 0:\n        hit(\"REFUSE.POOL\")", "    if False:\n        hit(\"REFUSE.POOL\")"),
    ("M33 buffer naming from EVAL items too", "        bnames = np.array([GB.majority(ybuf[tmask & (blab == j)], classes) for j in range(kb)], dtype=int)",
     "        bnames = np.array([GB.majority(ybuf[blab == j], classes) for j in range(kb)], dtype=int)"),
    ("M34 OL2 point/upper swapped", "    return ol2_word([(per[m][\"churn\"][\"d\"], per[m][\"churn\"][\"hi\"]) for m in sources])",
     "    return ol2_word([(per[m][\"churn\"][\"hi\"], per[m][\"churn\"][\"d\"]) for m in sources])"),
    ("M36 OL2 from the first replay only", "    return ol2_word([(per[m][\"churn\"][\"d\"], per[m][\"churn\"][\"hi\"]) for m in sources])",
     "    return ol2_word([(per[m][\"churn\"][\"d\"], per[m][\"churn\"][\"hi\"]) for m in sources[:1]])"),
    ("M37 OL1 SE from the percentile width", "    return ol1_word(st[\"d\"], st[\"se\"])", "    return ol1_word(st[\"d\"], (st[\"hi\"] - st[\"lo\"]) / 8.0)"),
    ("M38 pooled D over the first replay only", "        for m, r in reps.items():\n            diff[r[\"eout\"]]",
     "        for m, r in list(reps.items())[:1]:\n            diff[r[\"eout\"]]"),
    ("M39 churn bootstrap on the held-out components", "            cs = GB.stat(r[\"churn\"].astype(np.float64), W[\"ecomp\"][r[\"ein\"]])",
     "            cs = GB.stat(r[\"churn\"].astype(np.float64), np.arange(len(r[\"ein\"])))"),
    ("M40 buffer k uncapped (k = L_m on a smaller or empty buffer)", "    kb = min(Lm, len(buf))", "    kb = Lm"),
    ("M41 thresholds on the in-members' EVAL (wrong split side)", "    g_max, g_mar = top_margin(W[\"Xg\"][gin] @ mu0.T)",
     "    g_max, g_mar = top_margin(W[\"Xe\"][W[\"esrc\"] != m] @ mu0.T)"),
    ("M42 absorbed EVAL items counted for renaming", "        if side == \"T\":\n            absorbed[j1][int(W[\"yt\"][i])] += 1",
     "        if True:\n            absorbed[j1][int(W[\"yt\"][i] if side == \"T\" else W[\"ye\"][i])] += 1"),
    ("M43 held-out EVAL filed by argmin (min<->max)", "    fm = np.argmax(W[\"Xe\"][eout] @ allC.T, axis=1)", "    fm = np.argmin(W[\"Xe\"][eout] @ allC.T, axis=1)"),
    ("M44 churn 'before' after the stream (no reference graft)", "    churn = (after_mean != before).astype(np.int64)",
     "    churn = (after_mean != np.argmax(W[\"Xe\"][ein] @ U.T, axis=1)).astype(np.int64)"),
    ("M45 C-1 reverted: deciding replay starts at the unit mu", "    mbar = mu0 * A[\"r\"][keep][:, None] if init == \"mean\" else mu0.copy()",
     "    mbar = mu0.copy()"),
    ("M46 C-1: n = directQueries instead of the TRAIN count", "    tree[\"n\"] = tcnt", "    tree[\"n\"] = tree[\"n_dq\"]"),
    ("M47 O3: running mean renormalised every step", "        mbar[j1] = mbar[j1] + (x - mbar[j1]) / (n[j1] + 1.0)",
     "        mbar[j1] = mbar[j1] + (x - mbar[j1]) / (n[j1] + 1.0)\n        mbar[j1] = mbar[j1] / np.linalg.norm(mbar[j1])"),
    ("M48 C-2 reverted: deciding batch = the mirrored filing", "batch={\"tree\": efl_all, \"km\": kfl_all}",
     "batch={\"tree\": efl, \"km\": kfl}"),
    ("M49 C-2: symmetric batch excludes the one-cell cell", "    efl_all = (tree[\"name\"][np.argmax(S, axis=1)] == ye).astype(np.int64)",
     "    efl_all = (tree[\"name\"][np.argmax(S_split, axis=1)] == ye).astype(np.int64)"),
    ("M50 C-3: capture line never printed", "    if T[\"ol2_all\"] == \"NOT-STABLE\" and T[\"ol2\"] != \"NOT-STABLE\":",
     "    if False:"),
    ("M51 C-3: F-OL fires on the all-cells churn", "    if f_ol(T[\"ol2\"]):", "    if f_ol(T[\"ol2_all\"]):"),
    ("M52 C-1: k-means init r from the tree arm's rule (r = 1)", "    km[\"r\"] = np.array(", "    km[\"r\"] = 1.0 + 0.0 * np.array("),
    ("M53 mirrored D beside computed against the symmetric batch", "        diff_mir = online - W[\"batch_mir\"][arm]",
     "        diff_mir = online - W[\"batch\"][arm]"),
    ("O1 thresholds over all six members' cells", "    g_max, g_mar = top_margin(W[\"Xg\"][gin] @ mu0.T)",
     "    g_max, g_mar = top_margin(W[\"Xg\"][gin] @ A[\"mu\"].T)"),
    ("O2 count frozen (n += 0)", "        n[j1] += 1.0", "        n[j1] += 0.0"),
    ("O4 renaming of existing cells disabled", "        if top > cdom[j]:", "        if False:"),
    ("O5 order seed not the registered one (varies by replay)",
     "    rng = np.random.default_rng(ORDER_SEED)\n    order = [(\"T\", int(i)) for i in rng.permutation(tout)]",
     "    rng = np.random.default_rng(ORDER_SEED + len(ids))\n    order = [(\"T\", int(i)) for i in rng.permutation(tout)]"),
    ("O7 tau_m from the max-cos order statistic", "order_stat(g_mar, P_M)\n    ein, eout", "order_stat(g_max, P_M)\n    ein, eout"),
    ("O8 init at 0.69 x mu0 (a constant r)", "    mbar = mu0 * A[\"r\"][keep][:, None] if init == \"mean\" else mu0.copy()",
     "    mbar = mu0 * 0.69 if init == \"mean\" else mu0.copy()"),
    ("M35 margin threshold at p80", "order_stat(g_mar, P_M)\n    ein, eout", "order_stat(g_mar, 1 - P_M)\n    ein, eout"),
)


def run_mutants():
    me = os.path.abspath(__file__)
    full = open(me, encoding="utf-8").read().replace("\r\n", "\n")
    cut = full.index("\nMUTANTS = (")
    src, tail = full[:cut], full[cut:]                  # patterns are searched and replaced in the code above MUTANTS only
    rows, survived = [], []
    for name, old, new in (("X00 control (no edit)", "", ""),) + MUTANTS:
        if old:
            k = src.count(old)
            if k != 1:
                rows.append((name, "BAD (pattern found %d times)" % k))
                survived.append(name)
                continue
            msrc = src.replace(old, new, 1) + tail
        else:
            msrc = full
        g = {"__name__": "orl_mutant", "__file__": me}
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(msrc, me, "exec"), g)
                g["selftest"](quiet=True)
            res = "SURVIVED"
        except BaseException as e:      # noqa: BLE001 (SystemExit / AssertionError / anything = killed)
            res = "KILLED (%s: %s)" % (type(e).__name__, str(e).splitlines()[0][:90] if str(e) else "")
        rows.append((name, res))
        if old and res == "SURVIVED":
            survived.append(name)
        if not old and res != "SURVIVED":
            survived.append(name + " (control failed)")
    for n_, r_ in rows:
        print("  %-62s %s" % (n_, r_))
    k = sum(1 for n_, r_ in rows[1:] if r_.startswith("KILLED"))
    print("%s MUTANTS: %d of %d KILLED; control %s" % (TAG, k, len(MUTANTS), rows[0][1]))
    return 0 if not survived else 1


if __name__ == "__main__":
    sys.exit(main())
