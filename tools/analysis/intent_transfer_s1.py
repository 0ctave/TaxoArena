"""INTENT-TRANSFER-S1 readout: real TRAIN-only tree builds on MASSIVE en-US and CLINC150 against matched-k k-means and a supervised
ceiling (P0, T-C1, T-C1b, T-C2, T-C7, T-C9, T-C8, T-C8b, T-C4; descriptive T-C3, T-C6, anchored / s2 / gemma rows). ZERO LLM / judge
calls; no construction; no embedding call.

REGISTRATION OF RECORD: docs/judge_v2_program.md, section "## Registered 2026-10-01 (before any code or call) — INTENT-TRANSFER-S1:
on MASSIVE en-US and CLINC150 (gold hierarchies known), ..." (L22682-L22710 _as_of 2daeae31), with the brackets appended in that
section: N1 (a LOSS fired jointly with EQUIVALENT BLOCKS the positive-branch parity sentence) and, 2026-10-03 (e45474b8; record
"## Registrar's record 2026-10-03 ... the readout definitions ..." L23752-L23758; definitions docs/agents/plans/
2026-10-03_intent_s1_definitions.md, 868c1bb3):
  (a) T-C8 DESCENT (L22695) = a Python copy of the engine's inference routing (TaxonomyService.routeQueryToLeaves ->
      TaxonomyTrickler.routeQuery(isInference = true) -> trickle; updateAllShrinkages first; meanKappa x dot; the gate; the beam;
      log-softmax over the beam; mass pushed in topological order, pruned below ln(1e-30); candidates = leaves (+ internal nodes with
      no reached child, residual routing on under DAG_MAX); membershipFloor share, then maxLeafAssignments; top-1 = the highest-mass
      LEAF with TRAIN members (the runner's profiles filter); no such leaf = UNROUTED = wrong). Knobs from the snapshot's settings.
      ACCEPTED only if, on GATE, its top-1 equals the engine's own per-query top-1 (validation/MAIN_routing_diagnostics.txt) on >=
      99.9% of GATE texts; otherwise it REFUSES. EVAL never enters the JVM. flatLeaf = argmax cos(x, leaf vmfMu) at the leaf slice.
  (b) T-C4 MODAL LEAF (L22696) = the TRAIN flatLeaf plurality per intent (counted per item), ties to the smallest node id; LCA
      distance in tree edges (a to LCA plus b to LCA; parents by first discovery, UnionRouting.treeParents: BFS, children by id;
      multi-parent count printed); r = Pearson(D3 pair count, -distance), one-sided permutation p.
  (c) P0 (L22688) = snapshots.db table snapshots column graph, the row chosen by the run log's single "Snapshot ID:" (never the
      latest timestamp); read-only, a non-empty -wal refuses; HOLDS iff node-id sets and every node's queryIds SET are equal;
      childIds, vmfMu, kappa, queryWeights printed (exact or not), never deciding.
  B1 (ruled): M-AF-s2's salt 2 re-draws GATE vs TRAIN only (intent_s1_export.salted_side); it is read on the SAME EVAL as M-AF.

INSTRUMENT (imported, blob-pinned, never edited): tools/analysis/intent_transfer_s0.py (S0: load_corpora / Corpus, skmeans, assign,
nmi, codes, comp_weights, pct_ci, kish, centroids_by_label, unit, c4_variants, pin_check, _foreign_heavy, SEED_COFILE, BOOT_B);
tools/analysis/g13_comparator.py (G13's rule verbatim for T-C1b: k_per_class, kc_correct, g13_verdict, ncc_correct, knn_correct);
tools/analysis/intent_s1_export.py (EX: ARMS, salted_side, derive, assert_no_eval; the build inputs are re-derived and must equal the
run manifest's intent_build counts).

READERS' DEFINITIONS (the registered text, then the builder's readings R1-R12 where it is silent; each printed in the outcome):
  T-C1  D1 = NMI_fine(EVAL, tree leaves by flatLeaf) - mean_s NMI_fine(EVAL, spherical k-means at k = L, TRAIN-fit, seeds 0-19).
        delta_c = 0.25 x (NMI(supervised partition) - mean_s NMI(k-means at k = L)) on GATE, written before EVAL.
        SE_total = sqrt(SE_boot^2 + var_seed(D1) / 20). EQUIVALENT iff D1 +/- 1.645 SE_total lies inside (-delta_c, +delta_c).
        LOSS iff D1 < -bar AND the 95% CI < 0; GAIN iff D1 > bar AND the 95% CI > 0; bar = max(MDE80, spread_K), MDE80 = 2.8 x
        SE_total, spread_K = max - min of NMI_km over seeds 0-4. Joint outcomes recorded joined ("EQUIVALENT / LOSS-FLAGGED").
  T-C1b D13' = coarse filing precision of the leaves (TRAIN-majority coarse, flatLeaf) - P(KC_0); G13 verbatim (k_c, seeds 0-4,
        spread_KC, g13_verdict).
  T-C2  D2 = DP(tree) - DP(average-link agglomerative on the same leaves), gold coarse; HELD iff D2 > spread_o (max - min of D2 over
        M-AF, M-o1, M-o2) AND CI > 0; FAILED iff CI < 0. Floor: 200 random binary hierarchies. CLINC DESCRIPTIVE.
  T-C7  D7 = S(tree) - mean_s S(k-means at k = L) on S0's 3,222 C4 variants; delta = 0.25 x (ceiling - floor), recomputed per arm;
        bar = max(MDE80, spread of S_km over seeds 0-4); verdicts as T-C1. R = (S - floor) / (ceiling - floor) printed.
  T-C9  m(q) = cos(own leaf) - cos(second-nearest leaf) of the ORIGINAL; threshold = GATE's 20th percentile of m; D9 = flip rate
        (abstained) - flip rate (kept). HELD iff lower > 0; FAILED iff upper <= 0.
  T-C8  D_fd = fine filing precision flatLeaf - descent, paired. HELD iff lower > 0 on both corpora; FAILED iff upper <= 0 on either.
        T-C8b: D_fd(CLINC) - D_fd(MASSIVE), independent bootstraps; HELD iff its CI > 0.
  T-C4  Mantel r; HELD iff p < 0.05 on both corpora; FAILED iff p >= 0.05 on both (MASSIVE DESCRIPTIVE-ONLY, N2).
  R1  intervals: "95% component-bootstrap intervals unless named" = the PERCENTILE interval of S0.comp_weights draws (B 2,000), the
      seeds of record SEED_BOOT + the per-readout offsets below; the TOST interval is the NAMED one: D +/- 1.645 SE_total (the seed
      term enters the TOST SE only, as registered); the LOSS / GAIN 95% CI is the percentile interval.
  R2  leaves = every leaf of the snapshot graph (no childIds), sorted by node id; flatLeaf ties go to the smaller id (argmax order).
  R3  a leaf's TRAIN-majority label (fine for T-C8 / T-C1b-beside, coarse for T-C1b) = the plurality of the TRAIN items (per item,
      B2 multiplicity) that flatLeaf files to it; ties to the smaller label; an item filed to a leaf with no TRAIN item is WRONG.
      The SAME label map serves flatLeaf and descent in T-C8 (D_fd isolates the routing rule).
  R4  the supervised partition (T-C1 delta_c) = nearest TRAIN gold-fine centroid at the arm's slice.
  R5  T-C7 ceiling = TRAIN gold-fine centroid co-filing of (origin, variant) at the arm's slice (S0's "centroid stability"); floor =
      S0's random same-intent EVAL co-filing (SEED_COFILE, as many pairs as variants, distinct components) under k-means at k = L,
      seed 0, at the arm's slice (S0 computed both at K 60 / slice 256: 0.834 / 0.692).
      [SUPERSEDED 2026-10-03 by the registrar's B-2 ruling (a5c3e02a; prog L22693, record L23794-L23799): the floor is computed at the
      registered K = 60 (S0's K_f; k-means TRAIN-fit, seed 0, at the arm's slice), NOT at k = L; the ceiling as above; the qwen3-256
      salt-1 AF arm M-AF must reproduce S0's 0.834 / 0.692 to 3 dp, else the run REFUSES (M-AF-s2's salt-2 TRAIN and M-AF-g's slice
      768 print theirs, unchecked, descriptive). A disclosed exception to HYGIENE's GATE rule (no GATE variants exist; neither end
      reads the tree arm's partition), printed in the outcome. R3 / R4 / R7 / R12 were bracketed as built (L22690-L22695).]
  R6  T-C9 leaf centroids = the leaves' vmfMu (the engine's TRAIN-fitted mean directions, the flatLeaf centroids); abstained iff
      m < threshold (strict); a draw with an empty group is dropped (count printed).
  R7  T-C2 DP over EVAL items filed by flatLeaf (Heller-Ghahramani: mean over same-coarse pairs of the LCA subtree's share of that
      class); bootstrap copies are distinct items (pairs C(w, 2) on weighted counts); the tree hierarchy = treeParents.
  R8  T-C4 D3 pair counts = S0 D3's rule (EVAL, nearest TRAIN gold-fine centroid, qwen3 256, symmetric off-diagonal counts), all
      pairs (its top-20 asserted equal to S0.d3's); permutation: intent labels permuted jointly on the distance matrix, 10,000
      draws, p = (1 + #{r_perm >= r}) / 10,001.
  R9  T-C3 own-leaf rate of intent i = share of i's EVAL items filed (flatLeaf) to i's modal leaf; OLS on log(TRAIN items) and mean
      whitespace token length; P9's event = the log-size slope positive on BOTH AF arms (each printed).
  R10 near-copies (the registered sensitivity line) = EVAL items whose max cos to a salt-1 TRAIN item at qwen3 512 is >= 0.98; the
      deciding readouts are recomputed without them (variants of near-copy origins dropped) and printed beside, never deciding.
  R11 predictions: a numeric "X [lo, hi]" is HELD iff the point lies in [lo, hi] (inclusive); probability predictions are scored on
      their event with the Brier score; P8's r points carry no interval (printed, not scored as intervals); a joined outcome counts
      for every clause it carries (EQUIVALENT / LOSS-FLAGGED is an EQUIVALENT and a LOSS).
  R12 the descent ACCEPTANCE binds the arms whose descent is printed: M-AF and C-AF (deciding) REFUSE the run below 99.9%; the
      anchored arms' descriptive T-C8 rows print "NOT ACCEPTED" instead.

HYGIENE: reads only pinned files (ingest DB, intent_emb_qwen3.db, intent_emb_gemma.db when M-AF-g is present: S0.pin_check strict,
re-hashed after), snapshots.db and the run dirs (read-only; a non-empty -wal refuses). Every fit goes through fit_idx (TRAIN or
GATE of the arm's own split; an EVAL / OOS / dropped row REFUSES; audited). EVAL rows are read only after the GATE constants are fixed
(the phase guard eval_rows refuses earlier; the GATE CONSTANTS block precedes every EVAL statistic). OOS enters T-C6 only.
REFUSES while a java.exe runs (one heavy process). Threads OMP/OPENBLAS/MKL = 1.

OUTPUT: experiment_results/intent_transfer/s1_outcome.txt, WRITE-ONCE (mode x; an existing path refuses before any read) and
s1_items.csv beside (mode x; item ids, arm, leaf ids; no text). Outputs are never committed. --dry-run writes nothing, reads no EVAL
statistic, and REFUSES while any of the eight qwen3 builds is ABSENT (M-AF-g is optional: OMITTED, a stated precondition).

  python tools/analysis/intent_transfer_s1.py --selftest
  python tools/analysis/intent_transfer_s1.py --mutants
  python tools/analysis/intent_transfer_s1.py --port-parity <an existing build's seed_42 dir> --emb-db <the DB it read>   # optional READY check
  python tools/analysis/intent_transfer_s1.py --dry-run      # builds present? pins, census, P0, descent acceptance, T-C9 thresholds
  python tools/analysis/intent_transfer_s1.py --run          # the file of record (write-once)
(--dry-run computes no k-means: delta_c and the k-means threshold are fixed inside --run's GATE phase, printed in the GATE CONSTANTS
block before any EVAL statistic.)

SELFTEST (fixtures only; 137 value checks): ST-DESCENT (the port against an independent literal transcription of trickle +
routeQueryToLeaves on a hand tree with unequal sibling kappas: top-1 AND final memberships on 400 queries, the gate, a narrow beam,
the cap binding, residual candidates beside reached leaves, descentMargin 0, TREE_BASELINE; shrinkage from queryWeights mass; a
leaf without TRAIN members never top-1; the diagnostics parser; cross-link and missing-knob refusals), ST-STATS (every verdict
function branch incl. joined TOST outcomes and strict boundaries; Mantel one-sided on planted / reversed associations; modal-leaf
ties), ST-HIER (DP hand values, LCA edges, average-link pairing), ST-E2E (compute() + render() on a nine-build fixture: D1, SE_total,
spread_K, bar, the 1.645 half-width, the T-C1 percentile CI, delta_c on GATE, D13', S(tree), D7, D9 and its CI, DP and the random
p95, Mantel r, UNROUTED counted wrong, salt 2 re-draws TRAIN on a fixed EVAL, the TRAIN-ONLY audit, every falsifier and prediction
line printed, GATE constants before EVAL), ST-RENDER (every positive-branch / N1 / falsifier / T-C8 / T-C4 / P0-stop / omission /
prediction-band print branch on derived result dicts), ST-REFUSE (descent acceptance < 99.9% refuses a deciding arm and is printed
NOT ACCEPTED for a descriptive one; diagnostics missing a GATE text; the 99.9% bar; a salted side moving EVAL; EVAL before the GATE
freeze; the fit guard; P0 on membership sets, node ids, order, printed-only fields; P0 failure stops compute(); one Snapshot ID;
the row BY ID not the latest; a non-empty -wal; port parity; dry-run / run refuse while builds are ABSENT; write-once).
SELFTEST MUTANTS (2026-10-02, --mutants: in-process source edits, one at a time; 61 of 61 KILLED): T-C1 D from seed 0 | SE_total
without the seed term | spread_K over 20 seeds | bar = MDE80 only | NMI on coarse gold | TOST at 1.96 | TOST boundary inclusive |
joined LOSS printed plain | delta_c factor 0.5 | delta_c on TRAIN | T-C1b fine labels | T-C1b KC_1 | spread_KC 0 | T-C2 spread_o
over two arms (killed by a KeyError) | T-C2 HELD without spread | random floor p50 | DP own pairs without children | LCA one side |
T-C7 delta 0.5 | T-C7 S_km seed 0 | T-C9 GATE p80 | T-C9 CI groups swapped | T-C9 point groups swapped | T-C9 threshold on TRAIN |
T-C8 descent read from flatLeaf | UNROUTED counted right | T-C8 FAILED needs both | T-C8 HELD on either | T-C8b massive - clinc |
ci FAILED strict | T-C4 p <= 0.05 | Mantel two-sided | modal ties to the largest id | Pearson(count, +distance) | descent: own kappa
| gate removed | beam = every child | floor not applied | cap not applied | shrinkage uniform | profiles filter removed | residual
candidates off | acceptance 0.99 | acceptance > | acceptance counts all | P0 lists | P0 node ids ignored | P0 does not stop | row by
latest timestamp | several Snapshot IDs | GATE-before-EVAL guard removed | fit guard admits EVAL / OOS | not write-once | absent
builds admitted | salt EVAL check removed | F-S1a on either | F-S1d needs both | positive ignores N1 | bands exclusive | F-S1e line
dropped. First passes left 12 SURVIVING; checks added for each; two were EQUIVALENT and withdrawn: "TOST without delta > 0"
(with delta <= 0 the interval clause cannot hold) and "P0-P on the wrong event" (prediction_lines runs only when P0 holds; the
stopped path prints P0-P FAILED itself).

[DELTA 2026-10-03, branch intent-s1-fix, docs/reviews/READY_intent_s1.md and the registrar's a5c3e02a; insertion only, the text above
stands where not superseded] B-1: mantel() returns p = nan when r is not finite; t_c4_verdict reads a non-finite p on either corpus
as NOT EVALUABLE (the reviewer's constant-distance probe is a selftest case). B-2: the T-C7 floor at K = 60 with the M-AF
reproduction refusal and the printed disclosed exception (R5 bracket above). D-4: the diagnostics are parsed by BLOCK
(parse_diagnostics_full; a file with an unparsed block refuses) and --port-parity refuses unless every distinct query has a vector
(a subset never prints ACCEPTED). D-5: selftest cases for a descent / flatLeaf leaf without a TRAIN label (T-C8, T-C1b), the floor's
K and seed, an internal node's queryIds in P0. D-6: the port's "TRAIN members" = non-empty queryIds; the engine's profiles filter
(BatchTrickleEvaluator.buildLeafProfiles) can differ; the >= 99.9% GATE acceptance is the fail-closed guard. D-7: a TREE_BASELINE case
now discriminates the residual flag. D-8 is in the exporter (not touched here). Selftest 151 checks; mutants 72 of 72 KILLED (new:
B-1 p fails open | B-1 verdict ignores non-finite p | B-2 k = L floor | MY-4 floor seed 1 | B-2 reproduction check removed | MY-1
residual always on | MY-3 | MY-8 | MY-5 | D-4 subset | D-4 unparsed blocks admitted).

NOT YET DONE (stated): the Kotlin-side cross-check of the port (a Gradle test routing the hand tree through TaxonomyTrickler) is not
built: Gradle is held for another run; --port-parity on an existing build (e.g. experiment_results/topic_partition/ng_af_s42/seed_42
with embeddings_cache.db, read-only) is the cheaper real-engine check and is left for a free machine (rule 7: it reads
snapshots.db and a DB of record).
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import argparse        # noqa: E402
import contextlib      # noqa: E402
import hashlib         # noqa: E402
import io              # noqa: E402
import json            # noqa: E402
import math            # noqa: E402
import re              # noqa: E402
import sqlite3         # noqa: E402
import sys             # noqa: E402
import tempfile        # noqa: E402

import numpy as np     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "ingest"))
import split_side as SS                # noqa: E402
import intent_ingest as II             # noqa: E402
import intent_transfer_s0 as S0        # noqa: E402
import g13_comparator as G13           # noqa: E402
import intent_s1_export as EX          # noqa: E402

# g13_comparator imports flat_mix_mmlu, which replaces sqlite3.connect process-wide by FLAT-MIX-MMLU's own guard (mode=ro, four
# basenames of ITS test only). This readout's DBs are other files; every read here goes through data_v2.ro.open_ro /
# intent_ingest.open_db_ro (mode=ro&immutable=1 after the sidecar check), so the raw connect is restored right after the import.
if hasattr(sqlite3.connect, "_raw"):
    sqlite3.connect = sqlite3.connect._raw


def _blob(path):
    d = open(path, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


PINNED_CODE = {
    "intent_transfer_s0.py": "f662ceb19738f515972871f5963f5dcfc764a271",
    "g13_comparator.py": "61d83ec7dfed00b834d5b2e5d0ca355d236520db",
}
TAG = "[INTENT-S1]"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
OUT_DIR = os.path.join(ROOT, "experiment_results", "intent_transfer")
OUTCOME = "s1_outcome.txt"
ITEMS = "s1_items.csv"
REGISTRATION = ("docs/judge_v2_program.md L22682-L22710 (_as_of 2daeae31), \"## Registered 2026-10-01 (before any code or call) — "
                "INTENT-TRANSFER-S1: ...\"; brackets N1 and 2026-10-03 (e45474b8: L22688, L22695, L22696; record L23752-L23758)")

ARMS = {a[1]: dict(slug=a[0], name=a[1], corpus=a[2], salt=a[3], recipe=a[4], emb=a[5]) for a in EX.ARMS}
REQUIRED = ("M-AF", "M-AF'", "M-o1", "M-o2", "M-AF-s2", "M-AN", "C-AF", "C-AN")
OPTIONAL = ("M-AF-g",)
AF_OF = {"massive": "M-AF", "clinc": "C-AF"}
CORPORA = ("massive", "clinc")

SEEDS20, SEEDS5 = tuple(range(20)), tuple(range(5))
BOOT_B = S0.BOOT_B
SEED_BOOT = 20261003
OFF = {"T-C1": 10, "T-C1b": 20, "T-C2": 30, "T-C7": 40, "T-C9": 50, "T-C8": 60, "T-C4": 70, "RANDOM_H": 80}
Z90 = 1.6448536269514722
GATE_Q = 20.0
K_FLOOR = 60                               # B-2 ruling: the registered K (S0's K_f for MASSIVE)
REPRO_S0 = {"M-AF": (0.834, 0.692)}        # B-2 ruling: S0's ceiling / floor at qwen3 256, reproduced to 3 dp, else REFUSE
ACCEPT = 0.999
NEAR_COS = 0.98
N_PERM = 10000
N_RANDOM_H = 200
LOG_NEG = math.log(1e-30)
CENSUS_TOL = 0.05
REGISTERED_N = {"massive": (4946, 4923), "clinc": (6672, 6672), "variants": (3222, 3207)}
REG_SUPPORT = {
    "T-C1": {"massive": (0.00373, 0.0104), "clinc": (0.00164, 0.0046)}, "T-C1b": {"massive": (0.00403, 0.0113), "clinc": (0.00299, 0.0084)},
    "T-C2": {"massive": (0.005, 0.014)}, "T-C7": {"massive": (0.0085, 0.024)}, "T-C9": {"massive": (0.0210, 0.059)},
    "T-C8": {"massive": (0.0049, 0.0137), "clinc": (0.0042, 0.0118)}, "T-C8b": {"both": (0.0065, 0.018)},
    "T-C4": {"massive": (None, 0.36), "clinc": (None, 0.23)}, "DEFF": {"massive": 1.0093, "clinc": 1.0000, "variants": 1.0093},
    "n_eff": {"massive": 4900, "clinc": 6672, "variants": 3192},
}
VERDICT_LINES = {
    "T-C1": "EQUIVALENT SCOREABLE; LOSS DESCRIPTIVE-ONLY at the prediction",
    "T-C1b": "FAILED clause: CLINC SCOREABLE (thin), MASSIVE DESCRIPTIVE-ONLY",
    "T-C2": "SCOREABLE (CLINC DESCRIPTIVE)",
    "T-C7": "EQUIVALENT SCOREABLE; LOSS DESCRIPTIVE-ONLY",
    "T-C9": "SCOREABLE", "T-C8": "SCOREABLE", "T-C8b": "SCOREABLE",
    "T-C4": "CLINC SCOREABLE; MASSIVE DESCRIPTIVE-ONLY (N2); T-C4 HELD DESCRIPTIVE-ONLY",
}
POSITIVE_SENTENCE = ("on two known-answer intent corpora, the AF tree's leaves partition and hold addresses as well as flat k-means at "
                     "matched k, within a quarter of the ceiling gap (qwen3 256, one draw, RAW)")
DOES_NOT_SHOW = ("anything about capability text or MMLU-Pro; routing value; certified sites; sub-anchor profiles; embedder invariance "
                 "(gemma rows descriptive); a tree draw effect beyond MASSIVE's arms; that EQUIVALENT means \"better\" (or that a "
                 "non-EQUIVALENT means worse); anything about the anchored recipe against the AF recipe (never ranked); M-AF-s2 samples "
                 "no EVAL-draw variation (B1 ruling)")
STATE = {"gate_frozen": False}
FIT_LOG = []


class Refused(SystemExit):
    pass


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise Refused("%s REFUSED: %s" % (TAG, msg))


def check_code_pins():
    for name, want in PINNED_CODE.items():
        got = _blob(os.path.join(HERE, name))
        if got != want:
            refuse("%s blob %s != the pinned %s (the instrument is imported unchanged)" % (name, got, want))


# ================================================================================================ arm split, guards, phase
def arm_sides(C, salt):
    """The arm's side per row: salt 1 = the stored sides; salt >= 2 = EX.salted_side (EVAL fixed, the B1 ruling)."""
    if salt == 1:
        return C.side.copy()
    out = np.array([EX.salted_side(C.stem[i], salt, C.side[i]) for i in range(len(C.ids))], dtype=object)
    if not np.array_equal(out == SS.EVAL, C.side == SS.EVAL):
        refuse("salt %d moved an EVAL row (B1 ruling: EVAL is fixed)" % salt)
    return out


def fit_idx(C, side_arr, idx, allowed, what):
    """THE split guard of every fit: an index off the allowed sides, an OOS or a dropped row REFUSES (TRAIN-ONLY assertion)."""
    idx = np.asarray(idx, dtype=int)
    sides = set(side_arr[idx].tolist())
    bad = sides - set(allowed)
    n_oos, n_drop = int(C.oos[idx].sum()), int((~C.kept[idx]).sum())
    if bad or n_oos or n_drop or SS.EVAL in sides:
        refuse("TRAIN-ONLY: fit %r on %s holds sides %s outside %s, %d OOS, %d dropped" % (what, C.name, sorted(sides), allowed, n_oos, n_drop))
    FIT_LOG.append((what, C.name, len(idx), tuple(sorted(sides))))
    return idx


def side_rows(C, side_arr, have, side):
    """Kept, in-scope rows with a vector on `side` of the arm's split. EVAL only after the GATE constants are frozen."""
    if side == SS.EVAL and not STATE["gate_frozen"]:
        refuse("an EVAL row was requested before the GATE constants were fixed (GATE-before-EVAL)")
    m = C.kept & (~C.oos) & (side_arr == side) & have
    return np.nonzero(m)[0]


def eval_rows(A, mask=None):
    idx = side_rows(A["C"], A["side"], A["have"], SS.EVAL)
    if mask is not None:
        idx = idx[mask[idx]]
    return idx


# ================================================================================================ vectors
def load_raw(path, texts, dim, allow_missing=False):
    """{text: float32[dim]} for the texts (the first `dim` dims, raw), read-only through data_v2.ro after the sidecar check."""
    want = set(texts)
    out = {}
    con = S0.RO.open_ro(path)
    try:
        for t, b in con.execute("SELECT query, vector FROM embeddings"):
            if t in want:
                if len(b) // 4 < dim:
                    refuse("%s: a %d-d vector < the slice %d" % (path, len(b) // 4, dim))
                out[t] = np.frombuffer(b, dtype=">f4", count=dim).astype(np.float32)
    finally:
        con.close()
    miss = len(want) - len(out)
    if miss and not allow_missing:
        refuse("%s: %d needed texts have no vector" % (os.path.basename(path), miss))
    return out


def raw_matrix(C, vecs, dim):
    have = np.array([t in vecs for t in C.text])
    R = np.zeros((len(C.text), dim), dtype=np.float64)
    for i, t in enumerate(C.text):
        if have[i]:
            v = vecs[t][:dim]
            R[i, :len(v)] = v
    return R, have


def sliced(R, d):
    return S0.unit(R[:, :d])


# ================================================================================================ trees (snapshots.db graph)
SNAP_RE = re.compile(r"Snapshot ID:\s*(\S+)")


def run_dir(slug, data_root=None):
    return os.path.join(data_root or DATA_ROOT, EX.OUT_ROOT, slug, "seed_42")


def snapshot_id_of(rd):
    log = os.path.join(rd, "headless_run.log")
    if not os.path.isfile(log):
        return None, "headless_run.log ABSENT"
    ids = sorted(set(SNAP_RE.findall(open(log, encoding="utf-8", errors="replace").read())))
    if len(ids) != 1:
        return None, "%d distinct Snapshot ID lines (exactly one required)" % len(ids)
    return ids[0], "ok"


def snapshot_row(snap_db, sid):
    con = S0.RO.open_ro(snap_db)
    try:
        row = con.execute("SELECT graph, settings FROM snapshots WHERE id = ?", (sid,)).fetchone()
    finally:
        con.close()
    if row is None:
        refuse("snapshot %s is not in %s" % (sid, snap_db))
    return json.loads(row[0]), json.loads(row[1])


def last_dag_leaves(rd):
    p = os.path.join(rd, "dag_snapshots.jsonl")
    if not os.path.isfile(p):
        return None
    last = None
    for ln in open(p, encoding="utf-8"):
        if ln.strip():
            last = ln
    nodes = json.loads(last)["nodes"]
    return sorted(n["id"] for n in nodes if str(n.get("isLeaf")).lower() == "true")


def tree_of(graph, settings):
    """The routing / hierarchy view of a snapshot graph (R2). REFUSES cross-links, a non-root node without vmfMu, mixed slices."""
    nodes = {n["id"]: n for n in graph["nodes"]}
    root = graph["rootId"]
    if root not in nodes:
        refuse("graph root %s absent" % root)
    for n in nodes.values():
        if n.get("crossLinkChildIds"):
            refuse("node %s carries crossLinkChildIds: the descent port refuses cross-links" % n["id"])
        if n["id"] != root and not n.get("vmfMu"):
            refuse("node %s has no vmfMu" % n["id"])
    kids = {i: list(n.get("childIds") or []) for i, n in nodes.items()}
    for i, ks in kids.items():
        for k in ks:
            if k not in nodes:
                refuse("node %s lists an absent child %s" % (i, k))
    tparent, seen, q = {}, {root}, [root]
    while q:
        n = q.pop(0)
        for c in sorted(kids[n]):
            if c not in seen:
                seen.add(c)
                tparent[c] = n
                q.append(c)
    leaves = sorted(i for i in nodes if not kids[i] and (i in seen))
    slices = {int(nodes[i].get("sliceDim") or len(nodes[i]["vmfMu"])) for i in nodes if nodes[i].get("vmfMu")}
    if len(slices) != 1:
        refuse("the graph carries several sliceDims %s" % sorted(slices))
    d = slices.pop()
    for i, n in nodes.items():
        if n.get("vmfMu") and len(n["vmfMu"]) != d:
            refuse("node %s vmfMu length %d != sliceDim %d" % (i, len(n["vmfMu"]), d))
    mu = {i: np.asarray(n["vmfMu"], dtype=np.float64) for i, n in nodes.items() if n.get("vmfMu")}
    mass = {i: float(sum(sorted_vals(n.get("queryWeights") or {}))) for i, n in nodes.items()}
    knobs = {k: settings[k] for k in ("membershipFloor", "routingBeamGamma", "descentMargin", "maxLeafAssignments", "dagMode") if k in settings}
    if len(knobs) != 5:
        refuse("snapshot settings lack a routing knob (have %s)" % sorted(knobs))
    return dict(nodes=nodes, root=root, kids=kids, tparent=tparent, leaves=leaves, d=d, mu=mu, mass=mass, knobs=knobs,
                leaf_mu=np.vstack([mu[i] for i in leaves]) if leaves else np.zeros((0, d)),
                has_train={i: bool(nodes[i].get("queryIds")) for i in leaves},
                multi_parent=sum(1 for n in nodes.values() if len(n.get("parentIds") or []) > 1))


def sorted_vals(m):
    return [m[k] for k in sorted(m)]


def shrinkages(T):
    """GraphNode.updateChildCentroidShrinkage for every internal node: r = ||sum_c w_c mu_c||, w = child mass shares (uniform if 0)."""
    out = {}
    for i, ks in T["kids"].items():
        if not ks:
            out[i] = 1.0
            continue
        w = np.array([T["mass"][c] for c in ks], dtype=np.float64)
        w = w / w.sum() if w.sum() > 0 else np.full(len(ks), 1.0 / len(ks))
        dim = len(T["mu"].get(ks[0], []))
        if dim == 0:
            out[i] = 1.0
            continue
        s = np.zeros(dim)
        for wc, c in zip(w, ks):
            if c in T["mu"] and len(T["mu"][c]) == dim:
                s += wc * T["mu"][c]
        out[i] = float(min(1.0, max(0.0, math.sqrt(float(s @ s)))))
    return out


def topo_order(T):
    state, order = {}, []

    def visit(n):
        if n in state:
            return
        state[n] = 0
        for c in T["kids"][n]:
            visit(c)
        state[n] = 1
        order.append(n)
    sys.setrecursionlimit(max(10000, sys.getrecursionlimit()))
    visit(T["root"])
    return order[::-1]


def _lse(a, b):
    m = max(a, b)
    return m + math.log(math.exp(a - m) + math.exp(b - m))


class Descent(object):
    """The Python copy of TaxonomyTrickler.trickle (readOnly inference, no GT bias), then routeQueryToLeaves + the profiles filter."""

    def __init__(self, T):
        self.T = T
        self.order = topo_order(T)
        self.r = shrinkages(T)
        self.ids = sorted(T["mu"])
        self.col = {i: j for j, i in enumerate(self.ids)}
        self.M = np.vstack([T["mu"][i] for i in self.ids])
        self.kappa = {i: float(T["nodes"][i].get("vmfKappa") or 0.0) for i in T["nodes"]}
        k = T["knobs"]
        self.floor, self.gamma, self.margin = float(k["membershipFloor"]), float(k["routingBeamGamma"]), float(k["descentMargin"])
        self.cap = int(k["maxLeafAssignments"])
        self.residual = str(k["dagMode"]) == "DAG_MAX"

    def top1(self, Xp):
        """Xp: rows already sliced to the tree's slice and renormalised. -> list of leaf ids (None = UNROUTED)."""
        D = Xp @ self.M.T
        return [self._route(D[r])[0] for r in range(D.shape[0])]

    def memberships(self, Xp):
        """The final normalised log-memberships (after floor and cap) per query: the selftest compares them, not only top-1."""
        D = Xp @ self.M.T
        return [self._route(D[r])[1] for r in range(D.shape[0])]

    def _route(self, dots_all):
        T, col = self.T, self.col
        acc = {T["root"]: 0.0}
        logp = {}
        for n in self.order:
            cur = acc.get(n)
            if cur is None or cur < LOG_NEG:
                continue
            logp[n] = cur
            ks = T["kids"][n]
            if not ks:
                continue
            mk = max(sum(self.kappa[c] for c in ks) / len(ks), 1e-9)
            dots = [float(dots_all[col[c]]) for c in ks]
            scores = [mk * x for x in dots]
            mx_s, mx_d = max(scores), max(dots)
            if n in col:
                parent_dot = float(dots_all[col[n]])
                best_child = max(dots)
                bar = max(self.r[n] - self.margin, 0.0)
                if best_child < bar * parent_dot:
                    continue
            beam = [i for i in range(len(ks)) if dots[i] >= mx_d - self.gamma]
            lse = mx_s + math.log(max(sum(math.exp(scores[i] - mx_s) for i in beam), 1e-300))
            for i in beam:
                w = cur + scores[i] - lse
                c = ks[i]
                acc[c] = w if c not in acc else _lse(acc[c], w)
        cand = {}
        for n, lp in logp.items():
            if not T["kids"][n]:
                cand[n] = lp
        if self.residual or not cand:
            for n, lp in logp.items():
                if T["kids"][n] and not any(c in logp for c in T["kids"][n]):
                    cand[n] = lp
        if not cand:
            cand[T["root"]] = 0.0
        norm = _normalise(cand)
        admitted = {n: v for n, v in norm.items() if v >= math.log(max(self.floor, 1e-300))}
        if not admitted:
            best = max(norm.items(), key=lambda kv: kv[1])
            admitted = {best[0]: best[1]}
        top = sorted(admitted.items(), key=lambda kv: -kv[1])[:self.cap]
        mem = _normalise(dict(top))
        leaves = sorted(((n, v) for n, v in mem.items() if not T["kids"][n] or self.residual), key=lambda kv: -kv[1])
        leaves = sorted(((n, math.exp(v)) for n, v in leaves if not T["kids"][n]), key=lambda kv: -kv[1])
        for n, _v in leaves:
            if T["has_train"].get(n):
                return n, mem
        return None, mem


def _normalise(raw):
    if not raw:
        return {}
    m = max(raw.values())
    s = sum(math.exp(v - m) for v in raw.values())
    l = m + math.log(max(s, 1e-300))
    return {k: v - l for k, v in raw.items()}


def flat_leaf(T, Xp):
    return np.argmax(Xp @ T["leaf_mu"].T, axis=1)


DIAG_BLOCK = re.compile(r'Query: "(.*?)"\nTrue Domain:[^\n]*\nCandidate Count:[^\n]*\n'
                        r'(?:Top-1 Leaf: [^\n]*?\(ID: (\S+)\) \| Dominant:[^\n]*|(No candidates matched\.))', re.S)
DIAG_MARK = re.compile(r'"\nTrue Domain:')


def parse_diagnostics_full(path):
    """[READY_intent_s1 D-4] BLOCK parser of validation/MAIN_routing_diagnostics.txt (a query text may span lines): ->
    ({query text: engine top-1 leaf id or None}, blocks parsed, block markers in the file). Every caller refuses a file whose
    parsed block count differs from its marker count."""
    txt = open(path, encoding="utf-8", errors="replace").read().replace("\r\n", "\n")
    out, n = {}, 0
    for m in DIAG_BLOCK.finditer(txt):
        n += 1
        out[m.group(1)] = None if m.group(3) else m.group(2)
    return out, n, len(DIAG_MARK.findall(txt))


def parse_diagnostics(path):
    """{query text: engine top-1 leaf id or None}; REFUSES a file with an unparsed block."""
    out, n, marks = parse_diagnostics_full(path)
    if n != marks:
        refuse("%s: %d of %d query blocks parsed (an unparsed block)" % (path, n, marks))
    return out


# ================================================================================================ statistics helpers
def wmean(x, w):
    return float((np.asarray(x, dtype=np.float64) * w).sum() / w.sum()) if w.sum() > 0 else float("nan")


def boot(comp, fn, seed, B=None):
    """Percentile 95% interval and SD of fn(weights) over S0.comp_weights draws (R1)."""
    draws = [fn(w) for w in S0.comp_weights(comp, B or BOOT_B, np.random.default_rng(seed))]
    good = [d for d in draws if np.isfinite(d)]
    lo, hi = S0.pct_ci(good)
    return lo, hi, float(np.std(good, ddof=1)) if len(good) > 1 else float("nan"), draws


def tost_verdict(D, se_total, delta, lo95, hi95, bar):
    lo90, hi90 = D - Z90 * se_total, D + Z90 * se_total
    eq = bool(delta > 0 and -delta < lo90 and hi90 < delta)
    loss = bool(D < -bar and hi95 < 0)
    gain = bool(D > bar and lo95 > 0)
    words = (["EQUIVALENT"] if eq else []) + (["LOSS-FLAGGED" if eq else "LOSS"] if loss else []) + (["GAIN-FLAGGED" if eq else "GAIN"] if gain else [])
    return {"eq": eq, "loss": loss, "gain": gain, "lo90": lo90, "hi90": hi90, "verdict": " / ".join(words) or "UNDETERMINED"}


def ci_verdict(lo, hi):
    """T-C9 / T-C8 per corpus: HELD iff lower > 0; FAILED iff upper <= 0."""
    if lo > 0:
        return "HELD"
    if hi <= 0:
        return "FAILED"
    return "UNDETERMINED"


def t_c2_verdict(D2, lo, hi, spread_o):
    if D2 > spread_o and lo > 0:
        return "HELD"
    if hi < 0:
        return "FAILED"
    return "UNDETERMINED"


def t_c8_verdict(m, c):
    if m == "HELD" and c == "HELD":
        return "HELD"
    if m == "FAILED" or c == "FAILED":
        return "FAILED"
    return "UNDETERMINED"


def t_c4_verdict(pm, pc):
    if not (np.isfinite(pm) and np.isfinite(pc)):
        return "NOT EVALUABLE"                 # B-1: a constant count or distance gives no r and no p on that corpus
    if pm < 0.05 and pc < 0.05:
        return "HELD"
    if pm >= 0.05 and pc >= 0.05:
        return "FAILED"
    return "UNDETERMINED"


def in_band(x, lo, hi):
    return "HELD" if (isinstance(x, float) and np.isfinite(x) and lo <= x <= hi) else "FAILED"


def brier(p, event):
    return (p - (1.0 if event else 0.0)) ** 2


def majority(labels_of_items, groups, n_groups):
    """group index -> plurality label (ties to the smaller label), None for an empty group (R3)."""
    cnt = [dict() for _ in range(n_groups)]
    for g, lab in zip(groups, labels_of_items):
        cnt[g][lab] = cnt[g].get(lab, 0) + 1
    out = []
    for c in cnt:
        if not c:
            out.append(None)
        else:
            top = max(c.values())
            out.append(min(k for k, v in c.items() if v == top))
    return out


# ================================================================================================ hierarchy: DP, LCA, agglomerative
def hier_from_parent(parent, leaves):
    """A hierarchy = (parent map over node ids, the leaf ids). Returns children map and a post-order."""
    kids = {}
    for c, p in parent.items():
        kids.setdefault(p, []).append(c)
    roots = sorted(set(parent.values()) - set(parent))
    post = []

    def rec(n):
        for c in sorted(kids.get(n, [])):
            rec(c)
        post.append(n)
    for r in roots:
        rec(r)
    return kids, post


def dendrogram_purity(parent, leaves, leaf_of_item, cls_of_item, w=None):
    """R7: Heller-Ghahramani DP over items in leaves, weighted copies; pairs within a node counted by C(n, 2)."""
    kids, post = hier_from_parent(parent, leaves)
    w = np.ones(len(leaf_of_item)) if w is None else np.asarray(w, dtype=np.float64)
    classes = sorted(set(cls_of_item))
    ci = {c: j for j, c in enumerate(classes)}
    K = len(classes)
    cnt = {}
    for lf, c, wi in zip(leaf_of_item, cls_of_item, w):
        if wi == 0:
            continue
        a = cnt.setdefault(lf, np.zeros(K))
        a[ci[c]] += wi
    num, den = 0.0, 0.0

    def pairs(v):
        return v * (v - 1.0) / 2.0
    for n in post:
        v = cnt.get(n, np.zeros(K)).copy()
        for c in kids.get(n, []):
            v += cnt.get(c, np.zeros(K))
        cnt[n] = v
        tot = v.sum()
        if tot <= 0:
            continue
        own = pairs(v) - sum(pairs(cnt.get(c, np.zeros(K))) for c in kids.get(n, []))
        num += float((own * (v / tot)).sum())
    for n in post:
        if n not in parent:            # a root
            den += float(pairs(cnt[n]).sum())
    return num / den if den > 0 else float("nan")


def tree_parent_restricted(T):
    """treeParents restricted to the reachable tree (the root has no parent)."""
    return dict(T["tparent"])


def agglomerative_parent(leaves, leaf_mu):
    """Average-link agglomerative hierarchy on the leaf centroids (cosine distance): parent map over leaf ids + synthetic nodes."""
    from scipy.cluster.hierarchy import linkage
    n = len(leaves)
    if n < 2:
        return {}
    Z = linkage(leaf_mu, method="average", metric="cosine")
    name = list(leaves) + ["agg%05d" % j for j in range(n - 1)]
    parent = {}
    for j, (a, b, _d, _n) in enumerate(Z):
        parent[name[int(a)]] = name[n + j]
        parent[name[int(b)]] = name[n + j]
    return parent


def random_parent(leaves, rng):
    pool = list(leaves)
    parent, j = {}, 0
    while len(pool) > 1:
        a, b = rng.choice(len(pool), size=2, replace=False)
        x, y = pool[a], pool[b]
        p = "rnd%05d" % j
        j += 1
        parent[x], parent[y] = p, p
        pool = [z for k, z in enumerate(pool) if k not in (a, b)] + [p]
    return parent


def lca_dist(parent, a, b):
    if a == b:
        return 0
    pa, x, k = {}, a, 0
    while True:
        pa[x] = k
        if x not in parent:
            break
        x = parent[x]
        k += 1
    x, k = b, 0
    while x not in pa:
        if x not in parent:
            refuse("no common ancestor of %s and %s" % (a, b))
        x = parent[x]
        k += 1
    return pa[x] + k


# ================================================================================================ the world
def load_world(arms_present, db=None, emb_dir=None, pins_file=None, strict=True):
    """Corpora (S0), vectors per embedder (pinned, read-only), C4 variants; the arms' trees are loaded separately."""
    db = db or os.path.join(DATA_ROOT, II.DB_NAME)
    emb_dir = emb_dir or DATA_ROOT
    if pins_file:
        S0.PINS_FILE_OVERRIDE[0] = pins_file
    s_ing = S0.pin_check(db, "ingest_db", strict, label="ingest")
    CS = S0.load_corpora(db)
    var, vcnt = S0.c4_variants(CS["massive"])
    embs = sorted({ARMS[a]["emb"] for a in arms_present} | {"qwen3"})
    vecs, s_emb = {}, {}
    for e in embs:
        path = os.path.join(emb_dir, "intent_emb_%s.db" % e)
        s_emb[e] = S0.pin_check(path, "emb", strict, sub=e, label="intent_emb_%s.db" % e)
        texts = set()
        for c in CORPORA:
            C = CS[c]
            texts.update(C.text[i] for i in np.nonzero(C.kept)[0])
        texts.update(t for _i, t, _c in var)
        dim = 768 if e == "gemma" else 512             # the widest slice any arm or readout of this embedder reads (AN / near-copies 512)
        vecs[e] = load_raw(path, texts, dim)
    return {"CS": CS, "variants": var, "variant_counts": vcnt, "vecs": vecs, "db": db, "emb_dir": emb_dir,
            "pins": {"ingest": s_ing, **{"emb_" + e: s for e, s in s_emb.items()}}}


def make_arm(W, name, T, sid):
    a = ARMS[name]
    C = W["CS"][a["corpus"]]
    R, have = raw_matrix(C, W["vecs"][a["emb"]], T["d"])
    side = arm_sides(C, a["salt"])
    X = sliced(R, T["d"])
    return dict(a, C=C, R=R, have=have, side=side, X=X, T=T, sid=sid, L=len(T["leaves"]))


def census(W):
    """Registered denominators (Support (a)); a difference above 5% REFUSES before any statistic (counting is not reading)."""
    out = {}
    for c in CORPORA:
        C = W["CS"][c]
        m = C.kept & (~C.oos) & (C.side == SS.EVAL)
        n, g = int(m.sum()), int(len(np.unique(C.comp[m])))
        out[c] = (n, g)
    oi = np.array([i for i, _t, _c in W["variants"]])
    out["variants"] = (len(oi), int(len(np.unique(W["CS"]["massive"].comp[oi]))) if len(oi) else 0)
    bad = []
    for k, (n, g) in out.items():
        rn, rg = REGISTERED_N[k]
        if abs(n - rn) > CENSUS_TOL * rn or abs(g - rg) > CENSUS_TOL * rg:
            bad.append("%s %d / %d vs registered %d / %d" % (k, n, g, rn, rg))
    return out, bad


# ================================================================================================ P0
def p0(gA, gB):
    """(c): node-id sets equal AND every node's queryIds set equal; the printed (non-deciding) fields compared exactly."""
    na = {n["id"]: n for n in gA["nodes"]}
    nb = {n["id"]: n for n in gB["nodes"]}
    ids_eq = set(na) == set(nb)
    diff_members = sorted(i for i in set(na) & set(nb) if set(na[i].get("queryIds") or []) != set(nb[i].get("queryIds") or []))
    holds = bool(ids_eq and not diff_members)
    printed = {}
    for f in ("childIds", "vmfMu", "vmfKappa", "queryWeights"):
        printed[f] = "exact" if all(na[i].get(f) == nb[i].get(f) for i in set(na) & set(nb)) else "differs"
    return {"holds": holds, "ids_equal": ids_eq, "n_a": len(na), "n_b": len(nb), "members_differ": len(diff_members),
            "first": diff_members[:3], "printed": printed}


# ================================================================================================ phase 1: TRAIN / GATE only
NEED_KM = ("M-AF", "C-AF", "M-AN", "C-AN", "M-AF-s2", "M-AF-g")


def phase_gate(A, accept_required, diag_path=None, need_km=None):
    """Everything an arm needs from TRAIN and GATE, fixed before EVAL: flatLeaf labels, modal leaves, k-means fits, delta_c, the T-C9
    thresholds, the descent acceptance."""
    C, X, T = A["C"], A["X"], A["T"]
    tr = fit_idx(C, A["side"], side_rows(C, A["side"], A["have"], SS.TRAIN), (SS.TRAIN,), "%s TRAIN" % A["name"])
    ga = fit_idx(C, A["side"], side_rows(C, A["side"], A["have"], SS.GATE), (SS.GATE,), "%s GATE" % A["name"])
    L = A["L"]
    fl_tr = flat_leaf(T, X[tr])
    A["tr"], A["ga"], A["fl_tr"] = tr, ga, fl_tr
    A["leaf_fine"] = majority(C.fine[tr].tolist(), fl_tr, L)
    A["leaf_coarse"] = majority(C.coarse[tr].tolist(), fl_tr, L)
    A["leaf_n_train"] = np.bincount(fl_tr, minlength=L)
    A["modal"] = modal_leaves(fl_tr, C.fine[tr], T["leaves"])
    need_km = (A["name"] in NEED_KM) if need_km is None else need_km
    u, G = S0.centroids_by_label(X[tr], C.fine[tr])
    A["sup_cent"] = (u, G)
    A["gate"] = {"n_gate": int(len(ga)), "nmi_sup": float("nan"), "nmi_km_mean": float("nan"), "delta_c": float("nan"), "thr_km": float("nan")}
    # T-C9 threshold on GATE (tree leaves)
    A["gate"]["thr_tree"] = float(np.percentile(margins(X[ga], T["leaf_mu"]), GATE_Q))
    A["km"] = None
    if need_km:
        # k-means at k = L (TRAIN fit), seeds 0-19; delta_c on GATE (R4); the k-means T-C9 threshold on GATE
        A["km"] = [S0.skmeans(X[tr], L, s) for s in SEEDS20]
        tg = S0.codes(C.fine[ga])
        nmi_sup = S0.nmi(tg, S0.codes(u[S0.assign(X[ga], G)]))
        nmi_km = [S0.nmi(tg, S0.assign(X[ga], Cm)) for Cm in A["km"]]
        A["gate"].update(nmi_sup=nmi_sup, nmi_km_mean=float(np.mean(nmi_km)), delta_c=0.25 * (nmi_sup - float(np.mean(nmi_km))),
                         thr_km=float(np.percentile(margins(X[ga], A["km"][0]), GATE_Q)))
    # descent acceptance on GATE (a)
    A["descent"] = Descent(T)
    A["accept"] = descent_acceptance(A, diag_path)
    if accept_required and not A["accept"]["accepted"]:
        refuse("%s: the descent port agrees with the engine's GATE top-1 on %.4f%% (%d of %d) < 99.9%%: the port refuses (a)"
               % (A["name"], 100 * A["accept"]["agree"], A["accept"]["k"], A["accept"]["n"]))
    return A


def modal_leaves(fl_tr, fine_tr, leaves):
    """(b): intent -> the leaf receiving most of its TRAIN items under flatLeaf (per item), ties to the smallest node id."""
    modal = {}
    fine_tr = np.asarray(fine_tr, dtype=object)
    for f in sorted(set(fine_tr.tolist())):
        cnt = np.bincount(np.asarray(fl_tr)[fine_tr == f], minlength=len(leaves))
        top = cnt.max()
        modal[f] = min(leaves[j] for j in np.flatnonzero(cnt == top))
    return modal


def margins(Xp, Cm):
    s = np.sort(Xp @ Cm.T, axis=1)
    return s[:, -1] - s[:, -2] if s.shape[1] > 1 else np.full(len(Xp), np.inf)


def accepted(k, n):
    """(a): the port is ACCEPTED iff it agrees with the engine on >= 99.9% of the GATE texts."""
    return bool(n > 0 and k / float(n) >= ACCEPT)


def descent_acceptance(A, diag_path=None):
    C, ga = A["C"], A["ga"]
    path = diag_path or os.path.join(run_dir(A["slug"]), "validation", "MAIN_routing_diagnostics.txt")
    if not os.path.isfile(path):
        return {"accepted": False, "agree": 0.0, "k": 0, "n": 0, "why": "MAIN_routing_diagnostics.txt ABSENT"}
    eng = parse_diagnostics(path)
    texts, idx = [], []
    seen = set()
    for i in ga:
        if C.text[i] not in seen:
            seen.add(C.text[i])
            texts.append(C.text[i])
            idx.append(i)
    missing = [t for t in texts if t not in eng]
    if missing or len(eng) != len(texts):
        return {"accepted": False, "agree": 0.0, "k": 0, "n": len(texts),
                "why": "the diagnostics cover %d queries, the arm's GATE has %d distinct texts (%d missing)" % (len(eng), len(texts), len(missing))}
    py = A["descent"].top1(A["X"][np.array(idx, dtype=int)])
    k = sum(1 for t, p in zip(texts, py) if eng[t] == p)
    agree = k / float(len(texts)) if texts else 0.0
    return {"accepted": accepted(k, len(texts)), "agree": agree, "k": k, "n": len(texts), "why": "",
            "unrouted_py": sum(1 for p in py if p is None), "unrouted_eng": sum(1 for t in texts if eng[t] is None)}


# ================================================================================================ phase 2: EVAL readouts (per arm)
def t_c1(A, mask=None, seed_off=0):
    C, X, T = A["C"], A["X"], A["T"]
    ev = eval_rows(A, mask)
    truth = S0.codes(C.fine[ev])
    tree_p = flat_leaf(T, X[ev])
    km_p = [S0.assign(X[ev], Cm) for Cm in A["km"]]
    n_tree = S0.nmi(truth, tree_p)
    n_km = [S0.nmi(truth, p) for p in km_p]
    D = n_tree - float(np.mean(n_km))
    dseed = [n_tree - x for x in n_km]
    comp = C.comp[ev]

    def fn(w):
        return S0.nmi(truth, tree_p, w) - float(np.mean([S0.nmi(truth, p, w) for p in km_p]))
    lo, hi, se_b, _dr = boot(comp, fn, SEED_BOOT + OFF["T-C1"] + seed_off)
    se_total = math.sqrt(se_b ** 2 + float(np.var(dseed, ddof=1)) / len(SEEDS20))
    spread_K = float(max(n_km[:5]) - min(n_km[:5]))
    mde = 2.8 * se_total
    bar = max(mde, spread_K)
    v = tost_verdict(D, se_total, A["gate"]["delta_c"], lo, hi, bar)
    return dict(v, D=D, lo=lo, hi=hi, se_boot=se_b, se_total=se_total, spread_K=spread_K, mde=mde, bar=bar, n_tree=n_tree,
                n_km_mean=float(np.mean(n_km)), n=int(len(ev)), G=int(len(np.unique(comp))), kish=S0.kish(comp),
                delta=A["gate"]["delta_c"], L=A["L"])


def fine_correct_flat(A, idx):
    lab = A["leaf_fine"]
    fl = flat_leaf(A["T"], A["X"][idx])
    return np.array([lab[j] is not None and lab[j] == A["C"].fine[i] for j, i in zip(fl, idx)], dtype=np.float64), fl


def t_c1b(A, mask=None, seed_off=0):
    C, X, T = A["C"], A["X"], A["T"]
    ev = eval_rows(A, mask)
    fl = flat_leaf(T, X[ev])
    tree_ok = np.array([A["leaf_coarse"][j] is not None and A["leaf_coarse"][j] == C.coarse[i] for j, i in zip(fl, ev)], dtype=np.int64)
    classes = sorted(set(C.coarse[A["tr"]].tolist()))
    cix = {c: k for k, c in enumerate(classes)}
    yt = np.array([cix[c] for c in C.coarse[A["tr"]]])
    ye = np.array([cix.get(c, -1) for c in C.coarse[ev]])
    leaf_major = [m for m in A["leaf_coarse"] if m is not None]
    kc = G13.k_per_class(classes, yt, leaf_major)
    Xt, Xe = X[A["tr"]], X[ev]
    kc_ok = [G13.kc_correct(Xt, yt, Xe, ye, kc, s) for s in SEEDS5]
    p_kc = [float(k.mean()) for k in kc_ok]
    spread = float(max(p_kc) - min(p_kc))
    diff = tree_ok - kc_ok[0]
    d = float(diff.mean())
    comp = C.comp[ev]
    lo, hi, se, _ = boot(comp, lambda w: wmean(diff, w), SEED_BOOT + OFF["T-C1b"] + seed_off)
    return {"D": d, "lo": lo, "hi": hi, "se": se, "spread_KC": spread, "p_tree": float(tree_ok.mean()), "p_kc": p_kc,
            "verdict": G13.g13_verdict(d, lo, hi, spread), "kc": {classes[k]: v for k, v in kc.items()},
            "ncc": float(G13.ncc_correct(Xt, yt, Xe, ye).mean()), "knn15": float(G13.knn_correct(Xt, yt, Xe, ye, classes).mean()),
            "n": int(len(ev)), "G": int(len(np.unique(comp))), "kish": S0.kish(comp), "mde": 2.8 * se}


def t_c2_point(A, mask=None):
    C, X, T = A["C"], A["X"], A["T"]
    ev = eval_rows(A, mask)
    fl = flat_leaf(T, X[ev])
    leaf_ids = [T["leaves"][j] for j in fl]
    cls = C.coarse[ev].tolist()
    tp = tree_parent_restricted(T)
    ap = agglomerative_parent(T["leaves"], T["leaf_mu"])
    return ev, leaf_ids, cls, tp, ap


def t_c2(A, spread_o, mask=None, seed_off=0, n_random=N_RANDOM_H):
    ev, leaf_ids, cls, tp, ap = t_c2_point(A, mask)
    dp_t = dendrogram_purity(tp, A["T"]["leaves"], leaf_ids, cls)
    dp_a = dendrogram_purity(ap, A["T"]["leaves"], leaf_ids, cls)
    D2 = dp_t - dp_a
    comp = A["C"].comp[ev]
    lo, hi, se, _ = boot(comp, lambda w: dendrogram_purity(tp, A["T"]["leaves"], leaf_ids, cls, w)
                         - dendrogram_purity(ap, A["T"]["leaves"], leaf_ids, cls, w), SEED_BOOT + OFF["T-C2"] + seed_off)
    rng = np.random.default_rng(SEED_BOOT + OFF["RANDOM_H"])
    rnd = [dendrogram_purity(random_parent(A["T"]["leaves"], rng), A["T"]["leaves"], leaf_ids, cls) for _ in range(n_random)]
    p95 = float(np.percentile(rnd, 95)) if rnd else float("nan")
    return {"D2": D2, "dp_tree": dp_t, "dp_agg": dp_a, "lo": lo, "hi": hi, "se": se, "spread_o": spread_o,
            "verdict": t_c2_verdict(D2, lo, hi, spread_o) if spread_o is not None else "n/a", "random_p95": p95,
            "above_random_p95": bool(dp_t > p95), "n": int(len(ev)), "G": int(len(np.unique(comp))), "mde": 2.8 * se}


def variant_rows(A, W, mask=None):
    C = A["C"]
    keep = [(i, t) for i, t, _c in W["variants"] if (mask is None or mask[i]) and A["have"][i]]
    oi = np.array([i for i, _t in keep], dtype=int)
    if not STATE["gate_frozen"]:
        refuse("an EVAL variant was requested before the GATE constants were fixed")
    vt = [t for _i, t in keep]
    Rv = np.vstack([W["vecs"][A["emb"]][t][:A["T"]["d"]] for t in vt]).astype(np.float64) if vt else np.zeros((0, A["T"]["d"]))
    return oi, S0.unit(Rv)


def t_c7(A, W, mask=None, seed_off=0):
    C, X, T = A["C"], A["X"], A["T"]
    oi, Xv = variant_rows(A, W, mask)
    Xo = X[oi]
    same_t = (flat_leaf(T, Xo) == flat_leaf(T, Xv)).astype(np.float64)
    same_k = [(S0.assign(Xo, Cm) == S0.assign(Xv, Cm)).astype(np.float64) for Cm in A["km"]]
    S_t, S_k = float(same_t.mean()), [float(s.mean()) for s in same_k]
    D = S_t - float(np.mean(S_k))
    comp = C.comp[oi]
    lo, hi, se_b, _ = boot(comp, lambda w: wmean(same_t, w) - float(np.mean([wmean(s, w) for s in same_k])), SEED_BOOT + OFF["T-C7"] + seed_off)
    se_total = math.sqrt(se_b ** 2 + float(np.var([S_t - s for s in S_k], ddof=1)) / len(SEEDS20))
    u, G = A["sup_cent"]
    ceiling = float(np.mean(u[S0.assign(Xo, G)] == u[S0.assign(Xv, G)]))
    tr60 = fit_idx(C, A["side"], A["tr"], (SS.TRAIN,), "%s T-C7 floor k-means K=%d" % (A["name"], K_FLOOR))
    floor = cofile_floor(A, S0.skmeans(X[tr60], K_FLOOR, 0), len(oi))
    if mask is None and A["name"] in REPRO_S0:
        want = REPRO_S0[A["name"]]
        if (round(ceiling, 3), round(floor, 3)) != want:
            refuse("T-C7 (B-2 ruling): %s's ceiling / floor %.5f / %.5f do not reproduce S0's %.3f / %.3f to 3 dp" % (A["name"], ceiling, floor, want[0], want[1]))
    delta = 0.25 * (ceiling - floor)
    spread = float(max(S_k[:5]) - min(S_k[:5]))
    mde = 2.8 * se_total
    bar = max(mde, spread)
    v = tost_verdict(D, se_total, delta, lo, hi, bar)
    den = ceiling - floor
    return dict(v, D=D, lo=lo, hi=hi, se_boot=se_b, se_total=se_total, S_tree=S_t, S_km_mean=float(np.mean(S_k)), spread=spread,
                mde=mde, bar=bar, ceiling=ceiling, floor=floor, delta=delta, R_tree=(S_t - floor) / den if den else float("nan"),
                R_km=(float(np.mean(S_k)) - floor) / den if den else float("nan"), n=int(len(oi)), G=int(len(np.unique(comp))),
                kish=S0.kish(comp), same_t=same_t, oi=oi, Xv=Xv)


def cofile_floor(A, Cm, n_pairs):
    """R5: S0's random same-intent EVAL co-filing (SEED_COFILE; pairs = the variant count; distinct components) under Cm."""
    C, X = A["C"], A["X"]
    ev = eval_rows(A)
    by = {}
    for i in ev:
        by.setdefault(C.fine[i], []).append(int(i))
    labs = sorted(l for l, v in by.items() if len(v) > 1)
    rng = np.random.default_rng(S0.SEED_COFILE)
    cell = dict(zip(ev.tolist(), S0.assign(X[ev], Cm).tolist()))
    co, tries = [], 0
    while labs and len(co) < n_pairs and tries < 100 * n_pairs:
        tries += 1
        Lst = by[labs[int(rng.integers(len(labs)))]]
        a, b = Lst[int(rng.integers(len(Lst)))], Lst[int(rng.integers(len(Lst)))]
        if a != b and C.comp[a] != C.comp[b]:
            co.append(cell[a] == cell[b])
    return float(np.mean(co)) if co else float("nan")


def t_c9(A, W, mask=None, seed_off=0, r7=None):
    T = A["T"]
    r7 = r7 or t_c7(A, W, mask, seed_off)
    oi, same_t = r7["oi"], r7["same_t"]
    m = margins(A["X"][oi], T["leaf_mu"])
    ab = m < A["gate"]["thr_tree"]
    flip = 1.0 - same_t
    comp = A["C"].comp[oi]
    dropped = [0]

    def fn(w):
        wa, wk = w * ab, w * (~ab)
        if wa.sum() == 0 or wk.sum() == 0:
            dropped[0] += 1
            return float("nan")
        return wmean(flip, wa) - wmean(flip, wk)
    D9 = float(flip[ab].mean() - flip[~ab].mean()) if ab.any() and (~ab).any() else float("nan")
    lo, hi, se, _ = boot(comp, fn, SEED_BOOT + OFF["T-C9"] + seed_off)
    # k-means at k = L, seed 0 (descriptive)
    Cm = A["km"][0]
    mk = margins(A["X"][oi], Cm)
    abk = mk < A["gate"]["thr_km"]
    flipk = 1.0 - (S0.assign(A["X"][oi], Cm) == S0.assign(r7["Xv"], Cm)).astype(np.float64)
    D9k = float(flipk[abk].mean() - flipk[~abk].mean()) if abk.any() and (~abk).any() else float("nan")
    return {"D9": D9, "lo": lo, "hi": hi, "se": se, "verdict": ci_verdict(lo, hi) if np.isfinite(D9) else "UNDETERMINED",
            "n_abstained": int(ab.sum()), "n_kept": int((~ab).sum()), "S_kept": float(same_t[~ab].mean()) if (~ab).any() else float("nan"),
            "dropped_draws": dropped[0], "D9_km": D9k, "D9_tree_minus_km": D9 - D9k, "thr": A["gate"]["thr_tree"],
            "n": int(len(oi)), "G": int(len(np.unique(comp))), "mde": 2.8 * se}


def selective(A, covs=(0.8, 0.9)):
    ev = eval_rows(A)
    ok, _fl = fine_correct_flat(A, ev)
    m = margins(A["X"][ev], A["T"]["leaf_mu"])
    order = np.argsort(-m, kind="stable")
    return {c: float(ok[order[:max(1, int(round(c * len(ev))))]].mean()) for c in covs}


def t_c8(A, mask=None, seed_off=0, rng_seed=None):
    ev = eval_rows(A, mask)
    ok_f, _ = fine_correct_flat(A, ev)
    dl = A["descent"].top1(A["X"][ev])
    lab = dict(zip(A["T"]["leaves"], A["leaf_fine"]))
    ok_d = np.array([p is not None and lab.get(p) is not None and lab[p] == A["C"].fine[i] for p, i in zip(dl, ev)], dtype=np.float64)
    diff = ok_f - ok_d
    comp = A["C"].comp[ev]
    lo, hi, se, draws = boot(comp, lambda w: wmean(diff, w), rng_seed if rng_seed is not None else SEED_BOOT + OFF["T-C8"] + seed_off)
    return {"D": float(diff.mean()), "lo": lo, "hi": hi, "se": se, "P_flat": float(ok_f.mean()), "P_descent": float(ok_d.mean()),
            "unrouted": int(sum(1 for p in dl if p is None)), "draws": draws, "verdict": ci_verdict(lo, hi), "n": int(len(ev)),
            "G": int(len(np.unique(comp))), "kish": S0.kish(comp), "mde": 2.8 * se, "descent_leaf": dl, "ev": ev}


def t_c8b(m, c):
    d = [b - a for a, b in zip(m["draws"], c["draws"])]
    lo, hi = S0.pct_ci(d)
    D = c["D"] - m["D"]
    return {"D": D, "lo": lo, "hi": hi, "se": float(np.std(d, ddof=1)), "verdict": "HELD" if lo > 0 else "NOT HELD"}


def d3_pairs(C, X256, tr, ev):
    """R8: S0 D3's rule with every pair (symmetric off-diagonal confusion counts of nearest TRAIN gold-fine centroid filing)."""
    u, G = S0.centroids_by_label(X256[tr], C.fine[tr])
    pred = u[S0.assign(X256[ev], G)]
    pairs = {}
    for a, b in zip(C.fine[ev], pred):
        if a != b:
            k = tuple(sorted((a, b)))
            pairs[k] = pairs.get(k, 0) + 1
    return pairs


def mantel(intents, count, dist, n_perm, seed):
    K = len(intents)
    iu = np.triu_indices(K, 1)
    x = count[iu].astype(np.float64)
    y = -dist[iu].astype(np.float64)

    def r_of(yy):
        if np.std(x) == 0 or np.std(yy) == 0:
            return float("nan")
        return float(np.corrcoef(x, yy)[0, 1])
    r = r_of(y)
    if not np.isfinite(r):
        return r, float("nan")                 # READY_intent_s1 B-1: no permutation p without a finite r (NOT EVALUABLE)
    rng = np.random.default_rng(seed)
    ge = 0
    for _ in range(n_perm):
        p = rng.permutation(K)
        yp = -dist[p][:, p][iu]
        rp = r_of(yp)
        if np.isfinite(rp) and np.isfinite(r) and rp >= r:
            ge += 1
    return r, (1.0 + ge) / (1.0 + n_perm)


def t_c4(A, W, mask=None, n_perm=N_PERM):
    C = A["C"]
    X256 = S0.unit(A["R"][:, :256]) if A["R"].shape[1] >= 256 else A["X"]
    tr = side_rows(C, C.side, A["have"], SS.TRAIN)
    ev = eval_rows(A, mask)
    pairs = d3_pairs(C, X256, tr, ev)
    if mask is None and A["R"].shape[1] >= 256:             # R8: S0 D3's own top-20 must equal ours (verbatim rule)
        S = S0.Space(W["vecs"]["qwen3"], C, 256)
        top_ours = sorted(pairs.items(), key=lambda kv: (-kv[1], kv[0]))[:20]
        if S0.d3(C, S)["top20"] != top_ours:
            refuse("T-C4: the D3 pair counts differ from S0.d3's top-20 (the rule must be S0's)")
    intents = sorted(A["modal"])
    ix = {f: k for k, f in enumerate(intents)}
    K = len(intents)
    count = np.zeros((K, K))
    for (a, b), v in pairs.items():
        if a in ix and b in ix:
            count[ix[a], ix[b]] = count[ix[b], ix[a]] = v
    tp = tree_parent_restricted(A["T"])
    ap = agglomerative_parent(A["T"]["leaves"], A["T"]["leaf_mu"])
    dist_t = np.array([[lca_dist(tp, A["modal"][a], A["modal"][b]) for b in intents] for a in intents], dtype=np.float64)
    dist_a = np.array([[lca_dist(ap, A["modal"][a], A["modal"][b]) for b in intents] for a in intents], dtype=np.float64)
    r, p = mantel(intents, count, dist_t, n_perm, SEED_BOOT + OFF["T-C4"])
    ra, pa = mantel(intents, count, dist_a, n_perm, SEED_BOOT + OFF["T-C4"] + 1)
    return {"r": r, "p": p, "r_agg": ra, "p_agg": pa, "K": K, "n_perm": n_perm, "n_pairs": K * (K - 1) // 2, "shared_leaf_pairs": int((dist_t[np.triu_indices(K, 1)] == 0).sum()),
            "multi_parent": A["T"]["multi_parent"], "pairs": pairs}


def t_c3(A):
    C = A["C"]
    ev = eval_rows(A)
    fl = flat_leaf(A["T"], A["X"][ev])
    lid = [A["T"]["leaves"][j] for j in fl]
    rows = []
    for f in sorted(A["modal"]):
        sel = [k for k, i in enumerate(ev) if C.fine[i] == f]
        if not sel:
            continue
        own = float(np.mean([lid[k] == A["modal"][f] for k in sel]))
        ntr = int((C.fine[A["tr"]] == f).sum())
        tok = float(np.mean([len(C.text[ev[k]].split()) for k in sel]))
        rows.append((own, math.log(max(ntr, 1)), tok))
    Y = np.array([r[0] for r in rows])
    Xd = np.column_stack([np.ones(len(rows)), [r[1] for r in rows], [r[2] for r in rows]])
    beta = np.linalg.lstsq(Xd, Y, rcond=None)[0]
    return {"slope_logsize": float(beta[1]), "slope_tokens": float(beta[2]), "n_intents": len(rows)}


def t_c6(A, W):
    C, T = A["C"], A["T"]
    ev = eval_rows(A)
    oos = np.nonzero(C.kept & C.oos & (C.side == SS.EVAL) & A["have"])[0]
    if len(oos) == 0:
        return None
    s_in, s_oos = (A["X"][ev] @ T["leaf_mu"].T).max(1), (A["X"][oos] @ T["leaf_mu"].T).max(1)
    Cm = A["km"][0]
    return {"tree": S0.auroc(s_in, s_oos), "km_seed0": S0.auroc((A["X"][ev] @ Cm.T).max(1), (A["X"][oos] @ Cm.T).max(1)),
            "n_in": int(len(ev)), "n_oos": int(len(oos))}


def ceilings(A):
    C, X = A["C"], A["X"]
    ev = eval_rows(A)
    out = {}
    for level in ("fine", "coarse"):
        lab = C.labels(level)
        u, G = S0.centroids_by_label(X[A["tr"]], lab[A["tr"]])
        out["centroid_" + level] = float(np.mean(u[S0.assign(X[ev], G)] == lab[ev]))
        classes = sorted(set(lab[A["tr"]].tolist()))
        cix = {c: k for k, c in enumerate(classes)}
        yt = np.array([cix[c] for c in lab[A["tr"]]])
        ye = np.array([cix.get(c, -1) for c in lab[ev]])
        out["knn15_" + level] = float(G13.knn_correct(X[A["tr"]], yt, X[ev], ye, classes).mean())
    u, G = A["sup_cent"]
    out["nmi_supervised"] = S0.nmi(S0.codes(C.fine[ev]), S0.codes(u[S0.assign(X[ev], G)]))
    return out


def near_mask(W):
    """R10: EVAL items with max cos >= 0.98 to a salt-1 TRAIN item at qwen3 512 -> {corpus: bool mask over rows (True = KEEP)}."""
    out = {}
    for c in CORPORA:
        C = W["CS"][c]
        R, have = raw_matrix(C, W["vecs"]["qwen3"], 512)
        X = S0.unit(R)
        tr = np.nonzero(C.kept & ~C.oos & (C.side == SS.TRAIN) & have)[0]
        ev = np.nonzero(C.kept & ~C.oos & (C.side == SS.EVAL) & have)[0]
        keep = np.ones(len(C.ids), dtype=bool)
        for s in range(0, len(ev), 1000):
            blk = ev[s:s + 1000]
            mx = (X[blk] @ X[tr].T).max(1) if len(tr) else np.zeros(len(blk))
            keep[blk[mx >= NEAR_COS]] = False
        out[c] = keep
    return out


# ================================================================================================ the run
def arm_presence(snap_db, data_root=None):
    out = {}
    for name, a in ARMS.items():
        rd = run_dir(a["slug"], data_root)
        sid, why = snapshot_id_of(rd)
        diag = os.path.isfile(os.path.join(rd, "validation", "MAIN_routing_diagnostics.txt"))
        dag = os.path.isfile(os.path.join(rd, "dag_snapshots.jsonl"))
        man = os.path.isfile(os.path.join(rd, "diagnostics", "run_manifest.json"))
        ok = sid is not None and diag and dag and man
        out[name] = {"present": ok, "sid": sid, "why": why if sid is None else ("" if ok else "missing: %s" % ", ".join(
            k for k, v in (("validation/MAIN_routing_diagnostics.txt", diag), ("dag_snapshots.jsonl", dag), ("diagnostics/run_manifest.json", man)) if not v)),
            "rd": rd}
    return out


def load_tree_checked(name, pres, snap_db, D_ex, emb_pins):
    a = ARMS[name]
    rd = pres["rd"]
    graph, settings = snapshot_row(snap_db, pres["sid"])
    T = tree_of(graph, settings)
    dag = last_dag_leaves(rd)
    if dag is not None and dag != T["leaves"]:
        refuse("%s: the leaf-id set of dag_snapshots.jsonl (%d) != the snapshot graph's (%d)" % (name, len(dag), len(T["leaves"])))
    man = json.load(open(os.path.join(rd, "diagnostics", "run_manifest.json"), encoding="utf-8"))
    ib = man.get("intent_build") or {}
    d = D_ex[(a["corpus"], a["salt"])]
    want = {"arm": name, "n_train": sum(1 for r in d["rows"] if r["side"] == SS.TRAIN), "n_gate": sum(1 for r in d["rows"] if r["side"] == SS.GATE)}
    got = {"arm": ib.get("arm"), "n_train": ib.get("n_train"), "n_gate": ib.get("n_gate")}
    if got != want:
        refuse("%s: the run manifest's intent_build %s != the re-derived build %s" % (name, got, want))
    src = man.get("embedding_cache_source_sha256")
    if src is not None and src != emb_pins.get(a["emb"]):
        refuse("%s: the build's embedding source sha %s != the pin %s" % (name, src, emb_pins.get(a["emb"])))
    cfg = os.path.join(rd, "diagnostics", "config.toml")
    if os.path.isfile(cfg) and "enableResidualRouting" in open(cfg, encoding="utf-8").read():
        refuse("%s: the build's config sets enableResidualRouting (the port reads residual routing from dagMode)" % name)
    return T, graph


def compute(W, trees, graphs, diag_paths=None, n_perm=N_PERM, n_random=N_RANDOM_H, out=print):
    """Phase 1 (TRAIN / GATE) for every arm, freeze, phase 2 (EVAL). -> R (results) used by render()."""
    diag_paths = diag_paths or {}
    R = {"arms": {}, "omitted": [n for n in OPTIONAL if n not in trees]}
    R["P0"] = p0(graphs["M-AF"], graphs["M-AF'"])
    arms = {}
    STATE["gate_frozen"] = False
    for name in [n for n in REQUIRED + OPTIONAL if n in trees]:
        A = make_arm(W, name, trees[name][0], trees[name][1])
        accept_required = name in AF_OF.values()
        arms[name] = phase_gate(A, accept_required, diag_paths.get(name))
    R["gate"] = {n: dict(A["gate"], accept=A["accept"], L=A["L"], leaves_no_train=int(sum(1 for x in A["leaf_n_train"] if x == 0)))
                 for n, A in arms.items()}
    STATE["gate_frozen"] = True
    if not R["P0"]["holds"]:
        R["stopped"] = True
        return R, arms
    R["stopped"] = False
    near = near_mask(W)
    R["near"] = {c: int((~near[c] & W["CS"][c].kept & ~W["CS"][c].oos & (W["CS"][c].side == SS.EVAL)).sum()) for c in CORPORA}
    for c in CORPORA:
        A = arms[AF_OF[c]]
        r = R["arms"].setdefault(A["name"], {})
        r["T-C1"] = t_c1(A)
        r["T-C1b"] = t_c1b(A)
        r["T-C8"] = t_c8(A, rng_seed=SEED_BOOT + OFF["T-C8"] + (0 if c == "massive" else 1))
        r["T-C4"] = t_c4(A, W, n_perm=n_perm)
        r["T-C3"] = t_c3(A)
        r["ceilings"] = ceilings(A)
        r["selective"] = selective(A)
        r["near"] = {"T-C1": t_c1(A, near[c], 1), "T-C1b": t_c1b(A, near[c], 1), "T-C8": t_c8(A, near[c], 1)}
    m = R["arms"]["M-AF"]
    # T-C2: spread_o over M-AF, M-o1, M-o2
    d2s = {}
    for n in ("M-AF", "M-o1", "M-o2"):
        ev, leaf_ids, cls, tp, ap = t_c2_point(arms[n])
        d2s[n] = dendrogram_purity(tp, arms[n]["T"]["leaves"], leaf_ids, cls) - dendrogram_purity(ap, arms[n]["T"]["leaves"], leaf_ids, cls)
    spread_o = float(max(d2s.values()) - min(d2s.values()))
    m["T-C2"] = t_c2(arms["M-AF"], spread_o, n_random=n_random)
    m["T-C2"]["D2_by_arm"] = d2s
    R["arms"]["C-AF"]["T-C2"] = t_c2(arms["C-AF"], None, n_random=n_random)
    m["T-C7"] = t_c7(arms["M-AF"], W)
    m["T-C9"] = t_c9(arms["M-AF"], W, r7=m["T-C7"])
    m["near"]["T-C7"] = t_c7(arms["M-AF"], W, near["massive"], 1)
    m["near"]["T-C9"] = t_c9(arms["M-AF"], W, near["massive"], 1, r7=m["near"]["T-C7"])
    m["near"]["T-C2"] = t_c2(arms["M-AF"], spread_o, near["massive"], 1, n_random=0)
    R["T-C8b"] = t_c8b(m["T-C8"], R["arms"]["C-AF"]["T-C8"])
    R["T-C6"] = t_c6(arms["C-AF"], W)
    # descriptive arms
    for n in ("M-AN", "C-AN", "M-AF-s2", "M-AF-g"):
        if n not in arms:
            continue
        A = arms[n]
        r = R["arms"].setdefault(n, {})
        r["T-C1"] = t_c1(A)
        if n in ("M-AN", "C-AN"):
            r["T-C8"] = t_c8(A) if A["accept"]["accepted"] else None
        if A["corpus"] == "massive" and n != "M-AN":
            r["T-C7"] = t_c7(A, W)
            r["T-C9"] = t_c9(A, W, r7=r["T-C7"])
        if n == "M-AF-s2":
            r["T-C8"] = t_c8(A) if A["accept"]["accepted"] else None
    R["leaves"] = {n: A["L"] for n, A in arms.items()}
    R["verdicts"] = verdicts(R)
    return R, arms


def verdicts(R):
    a = R["arms"]
    m, c = a["M-AF"], a["C-AF"]
    V = {}
    V["T-C1"] = {"massive": m["T-C1"]["verdict"], "clinc": c["T-C1"]["verdict"]}
    V["T-C1_eq_both"] = bool(m["T-C1"]["eq"] and c["T-C1"]["eq"])
    V["T-C1_loss_both"] = bool(m["T-C1"]["loss"] and c["T-C1"]["loss"])
    V["T-C1_loss_either"] = bool(m["T-C1"]["loss"] or c["T-C1"]["loss"])
    V["T-C1b"] = {"massive": m["T-C1b"]["verdict"], "clinc": c["T-C1b"]["verdict"]}
    V["T-C1b_failed_both"] = bool(V["T-C1b"]["massive"] == "FAILED" and V["T-C1b"]["clinc"] == "FAILED")
    V["T-C2"] = m["T-C2"]["verdict"]
    V["T-C7"] = m["T-C7"]["verdict"]
    V["T-C9"] = m["T-C9"]["verdict"]
    V["T-C8"] = t_c8_verdict(m["T-C8"]["verdict"], c["T-C8"]["verdict"])
    V["T-C8b"] = R["T-C8b"]["verdict"]
    V["T-C4"] = t_c4_verdict(m["T-C4"]["p"], c["T-C4"]["p"])
    joint_loss = bool((m["T-C1"]["eq"] and m["T-C1"]["loss"]) or (c["T-C1"]["eq"] and c["T-C1"]["loss"])
                      or (m["T-C7"]["eq"] and m["T-C7"]["loss"]))
    V["positive"] = bool(V["T-C1_eq_both"] and m["T-C7"]["eq"] and not joint_loss)
    V["positive_why"] = ("" if V["positive"] else
                         "a LOSS fired jointly with EQUIVALENT (N1 bracket: the sentence is BLOCKED)" if (V["T-C1_eq_both"] and m["T-C7"]["eq"]) else
                         "T-C1 EQUIVALENT on both corpora AND T-C7 EQUIVALENT did not all hold")
    V["F-S1a"] = V["T-C1_loss_both"]
    V["F-S1b"] = V["T-C1b_failed_both"]
    V["F-S1c"] = V["T-C9"] == "FAILED"
    V["F-S1d"] = V["T-C8"] == "FAILED"
    V["F-S1e"] = False
    return V


# ================================================================================================ rendering
def f(x, fmt="%+.5f"):
    try:
        return fmt % x if x is not None and np.isfinite(x) else "nan"
    except TypeError:
        return str(x)


def render(R, meta):
    L = []
    L.append("INTENT-TRANSFER-S1 OUTCOME (zero LLM / judge calls). %s" % REGISTRATION)
    for k, v in meta.items():
        if not k.startswith("_"):
            L.append("%s: %s" % (k, v))
    L.append("READINGS R1-R12 and definitions (a)-(c): see the script docstring (printed by blob above); N1: a LOSS fired jointly with "
             "EQUIVALENT BLOCKS the positive-branch parity sentence.")
    g = R["gate"]
    L.append("ARMS: " + "; ".join("%s snapshot %s leaves %d (no-TRAIN leaves %d)" % (n, meta_sid(meta, n), v["L"], v["leaves_no_train"]) for n, v in g.items()))
    for n in R.get("omitted", []):
        L.append("ARM %s: OMITTED (a stated precondition: its build is absent; registration INSTRUMENT, not an outcome)" % n)
    p = R["P0"]
    L.append("P0 (M-AF vs M-AF', snapshots.graph by Snapshot ID): %s; node ids equal %s (%d / %d nodes); nodes whose queryIds SET differs %d %s; "
             "printed, not deciding: %s" % ("HOLDS" if p["holds"] else "FAILS", p["ids_equal"], p["n_a"], p["n_b"], p["members_differ"],
                                            p["first"], ", ".join("%s %s" % kv for kv in p["printed"].items())))
    L.append("GATE CONSTANTS (fixed before any EVAL read): " + "; ".join(
        "%s delta_c %s (NMI sup %s, km mean %s, n_gate %d), T-C9 thr tree %.5f km %s, descent agreement %s (%d of %d; %s)"
        % (n, f(v["delta_c"], "%.5f").replace("nan", "n/a"), f(v["nmi_sup"], "%.5f").replace("nan", "n/a"),
           f(v["nmi_km_mean"], "%.5f").replace("nan", "n/a"), v["n_gate"], v["thr_tree"], f(v["thr_km"], "%.5f").replace("nan", "n/a"),
           f(v["accept"]["agree"], "%.5f"), v["accept"]["k"], v["accept"]["n"], "ACCEPTED" if v["accept"]["accepted"] else
           "NOT ACCEPTED " + v["accept"]["why"]) for n, v in g.items()))
    if R["stopped"]:
        L.append("F-S1e: FIRED (P0 fails: construction determinism (G10 as sets) does not transfer to intent builds; the lane stops)")
        L.append("NO OTHER READOUT IS SCORED (P0 is a precondition; a failure stops the lane).")
        L.append("PREDICTION P0-P (precondition holds, p 0.90): FAILED, Brier %.4f" % brier(0.90, False))
        L.append("WHAT THIS RESULT WILL NOT SHOW: " + DOES_NOT_SHOW)
        return L
    a, V = R["arms"], R["verdicts"]
    m, c = a["M-AF"], a["C-AF"]
    L.append("SUPPORT (measured; registered beside): " + support_line(R))
    for corp, r in (("massive", m), ("clinc", c)):
        x = r["T-C1"]
        L.append("T-C1 %s (%s): D1 %s = NMI tree %.5f - mean_s NMI km(k=L=%d) %.5f; 90%% TOST [%s, %s] vs delta_c +/-%s; 95%% CI [%s, %s]; "
                 "SE_boot %.5f, SE_total %.5f, MDE80 %.5f, spread_K %.5f, bar %.5f; n %d EVAL items / %d components -> %s [%s]"
                 % (corp, AF_OF[corp], f(x["D"]), x["n_tree"], x["L"], x["n_km_mean"], f(x["lo90"]), f(x["hi90"]), f(x["delta"], "%.5f"),
                    f(x["lo"]), f(x["hi"]), x["se_boot"], x["se_total"], x["mde"], x["spread_K"], x["bar"], x["n"], x["G"], x["verdict"],
                    VERDICT_LINES["T-C1"]))
    for corp, r in (("massive", m), ("clinc", c)):
        x = r["T-C1b"]
        L.append("T-C1b %s: D13' %s = P_tree %.5f - P(KC_0) %.5f; 95%% CI [%s, %s]; spread_KC %.5f (KC_0..4 %s); beside: nearest gold centroid %.5f, "
                 "kNN-15 %.5f; n %d / %d -> %s [%s]" % (corp, f(x["D"]), x["p_tree"], x["p_kc"][0], f(x["lo"]), f(x["hi"]), x["spread_KC"],
                                                       ", ".join("%.5f" % v for v in x["p_kc"]), x["ncc"], x["knn15"], x["n"], x["G"], x["verdict"],
                                                       VERDICT_LINES["T-C1b"]))
    x = m["T-C2"]
    L.append("T-C2 massive (M-AF): D2 %s = DP tree %.5f - DP average-link %.5f; 95%% CI [%s, %s]; spread_o %.5f (D2 M-AF %s, M-o1 %s, M-o2 %s); "
             "random-hierarchy p95 %.5f (DP above it: %s) -> %s [%s]" % (f(x["D2"]), x["dp_tree"], x["dp_agg"], f(x["lo"]), f(x["hi"]),
                                                                          x["spread_o"], f(x["D2_by_arm"]["M-AF"]), f(x["D2_by_arm"]["M-o1"]),
                                                                          f(x["D2_by_arm"]["M-o2"]), x["random_p95"], x["above_random_p95"],
                                                                          x["verdict"], VERDICT_LINES["T-C2"]))
    x = c["T-C2"]
    L.append("T-C2 clinc (C-AF, DESCRIPTIVE): D2 %s (DP tree %.5f, average-link %.5f), 95%% CI [%s, %s]" % (f(x["D2"]), x["dp_tree"], x["dp_agg"], f(x["lo"]), f(x["hi"])))
    x = m["T-C7"]
    L.append("T-C7 massive (M-AF): D7 %s = S tree %.5f - mean_s S km %.5f on %d variants / %d components; delta %.5f = 0.25 x (ceiling %.5f - floor %.5f); "
             "90%% TOST [%s, %s]; 95%% CI [%s, %s]; SE_total %.5f, MDE80 %.5f, spread %.5f, bar %.5f; R tree %.4f, R km %.4f -> %s [%s]. "
             "DISCLOSED EXCEPTION to HYGIENE's GATE rule (B-2 ruling, prog L22693): delta's ends are computed on the EVAL variants "
             "(no GATE variants exist; neither end reads the tree's partition), floor at the registered K = 60, M-AF reproducing S0's 0.834 / 0.692"
             % (f(x["D"]), x["S_tree"], x["S_km_mean"], x["n"], x["G"], x["delta"], x["ceiling"], x["floor"], f(x["lo90"]), f(x["hi90"]),
                f(x["lo"]), f(x["hi"]), x["se_total"], x["mde"], x["spread"], x["bar"], x["R_tree"], x["R_km"], x["verdict"], VERDICT_LINES["T-C7"]))
    x = m["T-C9"]
    L.append("T-C9 massive (M-AF): D9 %s = flip(abstained, n %d) - flip(kept, n %d) at GATE p20 margin %.5f; 95%% CI [%s, %s] (dropped draws %d); "
             "S(kept) %.5f; selective fine precision 80%% / 90%%: MASSIVE %.5f / %.5f, CLINC %.5f / %.5f; D9(tree) - D9(km) %s (DESCRIPTIVE) -> %s [%s]"
             % (f(x["D9"]), x["n_abstained"], x["n_kept"], x["thr"], f(x["lo"]), f(x["hi"]), x["dropped_draws"], x["S_kept"],
                m["selective"][0.8], m["selective"][0.9], c["selective"][0.8], c["selective"][0.9], f(x["D9_tree_minus_km"]), x["verdict"],
                VERDICT_LINES["T-C9"]))
    for corp, r in (("massive", m), ("clinc", c)):
        x = r["T-C8"]
        L.append("T-C8 %s: D_fd %s = P flatLeaf %.5f - P descent %.5f (UNROUTED %d, counted wrong); 95%% CI [%s, %s]; n %d / %d -> %s"
                 % (corp, f(x["D"]), x["P_flat"], x["P_descent"], x["unrouted"], f(x["lo"]), f(x["hi"]), x["n"], x["G"], x["verdict"]))
    L.append("T-C8 (both corpora): %s [%s]" % (V["T-C8"], VERDICT_LINES["T-C8"]))
    x = R["T-C8b"]
    L.append("T-C8b: D_fd(CLINC) - D_fd(MASSIVE) %s, 95%% CI [%s, %s] (independent bootstraps) -> %s [%s]" % (f(x["D"]), f(x["lo"]), f(x["hi"]), x["verdict"], VERDICT_LINES["T-C8b"]))
    for corp, r in (("massive", m), ("clinc", c)):
        x = r["T-C4"]
        L.append("T-C4 %s: Mantel r %s (Pearson(D3 pair count, -LCA distance), %d intents, %d pairs, %d pairs sharing a leaf; multi-parent nodes %d); "
                 "one-sided permutation p %.5f (%d perms)%s; tree vs agglomerative (DESCRIPTIVE): r_agg %s, p %.5f"
                 % (corp, f(x["r"], "%+.4f"), x["K"], x["n_pairs"], x["shared_leaf_pairs"], x["multi_parent"], x["p"], x["n_perm"],
                    " [DESCRIPTIVE-ONLY, N2]" if corp == "massive" else "", f(x["r_agg"], "%+.4f"), x["p_agg"]))
    L.append("T-C4 (both corpora): %s [%s]" % (V["T-C4"], VERDICT_LINES["T-C4"]))
    L.append("SENSITIVITY (R10, registered line; near-copies cos >= 0.98 at qwen3 512: MASSIVE %d, CLINC %d EVAL items removed; never deciding): %s"
             % (R["near"]["massive"], R["near"]["clinc"], sensitivity_line(m, c)))
    L.append("DESCRIPTIVE: T-C3 own-leaf slope on log TRAIN size (token-length covariate): MASSIVE %s, CLINC %s; T-C6 OOS AUROC leaf centroids %s vs "
             "k-means(k=L, s0) %s (supervised 0.9764 beside); ceilings MASSIVE %s; CLINC %s"
             % (f(m["T-C3"]["slope_logsize"]), f(c["T-C3"]["slope_logsize"]), f(R["T-C6"]["tree"], "%.5f") if R["T-C6"] else "n/a",
                f(R["T-C6"]["km_seed0"], "%.5f") if R["T-C6"] else "n/a", ceiling_text(m["ceilings"]), ceiling_text(c["ceilings"])))
    for n in ("M-AN", "C-AN", "M-AF-s2", "M-AF-g"):
        if n in a:
            L.append("DESCRIPTIVE %s: %s" % (n, desc_text(a[n])))
    L += prediction_lines(R)
    for fid, txt in (("F-S1a", "T-C1 LOSS on both corpora (FLAT-MIX-MMLU's partition clause extends to known-answer intent corpora, AF at qwen3 256)"),
                     ("F-S1b", "T-C1b FAILED on both corpora (G13's failure seen on known answers)"),
                     ("F-S1c", "T-C9 FAILED (the margin mechanism does not carry to tree leaves)"),
                     ("F-S1d", "T-C8 FAILED on either corpus ('flatLeaf over descent' fails against gold)"),
                     ("F-S1e", "P0 fails (the lane stops)")):
        L.append("%s: %s (%s)" % (fid, "FIRED" if V[fid] else "NOT FIRED", txt))
    if V["positive"]:
        L.append("POSITIVE BRANCH: the record may write \"%s\"" % POSITIVE_SENTENCE)
    else:
        L.append("POSITIVE BRANCH: WITHHELD (%s)" % V["positive_why"])
    L.append("TRAIN-ONLY: %d fits audited (TRAIN or GATE of each arm's split), 0 with an EVAL row, 0 OOS, 0 dropped (fit_idx refuses otherwise)" % len(FIT_LOG))
    L.append("WHAT THIS RESULT WILL NOT SHOW: " + DOES_NOT_SHOW)
    return L


def meta_sid(meta, n):
    return (meta.get("_sids") or {}).get(n, "?")


def support_line(R):
    m, c = R["arms"]["M-AF"], R["arms"]["C-AF"]
    parts = []
    for key, corp, r, sek in (("T-C1", "massive", m, "se_total"), ("T-C1", "clinc", c, "se_total"), ("T-C1b", "massive", m, "se"),
                              ("T-C1b", "clinc", c, "se"), ("T-C8", "massive", m, "se"), ("T-C8", "clinc", c, "se"), ("T-C7", "massive", m, "se_total"),
                              ("T-C9", "massive", m, "se"), ("T-C2", "massive", m, "se")):
        x = r[key]
        reg = REG_SUPPORT[key].get(corp, (None, None))
        kish = x.get("kish", float("nan"))
        parts.append("%s %s n %d / G %d, Kish DEFF %.4f, n_eff %.0f, SE %.5f (reg %s), MDE80 %.5f (reg %s)"
                     % (key, corp, x["n"], x["G"], kish if np.isfinite(kish) else float("nan"), x["n"] / kish if np.isfinite(kish) and kish else float("nan"),
                        x[sek], reg[0], 2.8 * x[sek], reg[1]))
    return "; ".join(parts)


def sensitivity_line(m, c):
    s = []
    for corp, r in (("massive", m), ("clinc", c)):
        n = r["near"]
        s.append("%s T-C1 D1 %s [%s] T-C1b %s [%s] T-C8 %s [%s]" % (corp, f(n["T-C1"]["D"]), n["T-C1"]["verdict"], f(n["T-C1b"]["D"]),
                                                                  n["T-C1b"]["verdict"], f(n["T-C8"]["D"]), n["T-C8"]["verdict"]))
    n = m["near"]
    s.append("massive T-C7 D7 %s [%s] T-C9 D9 %s [%s] T-C2 D2 %s [%s]" % (f(n["T-C7"]["D"]), n["T-C7"]["verdict"], f(n["T-C9"]["D9"]),
                                                                       n["T-C9"]["verdict"], f(n["T-C2"]["D2"]), n["T-C2"]["verdict"]))
    return "; ".join(s)


def ceiling_text(x):
    return "centroid fine %.5f coarse %.5f, kNN-15 fine %.5f coarse %.5f, supervised partition NMI %.5f" % (
        x["centroid_fine"], x["centroid_coarse"], x["knn15_fine"], x["knn15_coarse"], x["nmi_supervised"])


def desc_text(r):
    s = ["T-C1 D1 %s [%s]" % (f(r["T-C1"]["D"]), r["T-C1"]["verdict"])]
    if "T-C8" in r:
        s.append("T-C8 D_fd %s" % f(r["T-C8"]["D"]) if r["T-C8"] else "T-C8 descent NOT ACCEPTED (not printed)")
    if "T-C7" in r:
        s.append("T-C7 D7 %s [%s]" % (f(r["T-C7"]["D"]), r["T-C7"]["verdict"]))
    if "T-C9" in r:
        s.append("T-C9 D9 %s [%s]" % (f(r["T-C9"]["D9"]), r["T-C9"]["verdict"]))
    return "; ".join(s) + " (never contrasted as a criterion)"


def prediction_lines(R):
    a, V = R["arms"], R["verdicts"]
    m, c = a["M-AF"], a["C-AF"]
    L = []
    held = []

    def prob(pid, text, p, ev):
        L.append("PREDICTION %s %s (p %.2f): event %s, Brier %.4f" % (pid, text, p, "OCCURRED" if ev else "did not occur", brier(p, ev)))

    def num(pid, text, x, lo, hi):
        h = in_band(float(x), lo, hi)
        held.append(h)
        L.append("PREDICTION %s %s: %s in [%+.3f, %+.3f] -> %s" % (pid, text, f(x), lo, hi, h))
    prob("P0-P", "precondition holds", 0.90, R["P0"]["holds"])
    for n, (lo, hi) in (("M-AF", (25, 50)), ("C-AF", (60, 110)), ("M-AN", (50, 90)), ("C-AN", (100, 160))):
        if n in R["leaves"]:
            num("P1", "leaves %s" % n, float(R["leaves"][n]), lo, hi)
    num("P2", "D1 massive", m["T-C1"]["D"], -0.025, 0.015)
    num("P2", "D1 clinc", c["T-C1"]["D"], -0.025, 0.015)
    prob("P2", "EQUIVALENT on both", 0.45, V["T-C1_eq_both"])
    prob("P2", "LOSS on either", 0.15, V["T-C1_loss_either"])
    num("P3", "D13' massive", m["T-C1b"]["D"], -0.04, 0.00)
    num("P3", "D13' clinc", c["T-C1b"]["D"], -0.04, 0.00)
    prob("P3", "FAILED on >= 1 corpus", 0.45, "FAILED" in V["T-C1b"].values())
    prob("P3", "HELD on either", 0.05, "HELD" in V["T-C1b"].values())
    num("P4", "D2", m["T-C2"]["D2"], -0.02, 0.05)
    prob("P4", "T-C2 HELD", 0.40, V["T-C2"] == "HELD")
    prob("P4", "DP above the random p95", 0.95, m["T-C2"]["above_random_p95"])
    num("P5", "D7", m["T-C7"]["D"], -0.040, 0.020)
    prob("P5", "T-C7 EQUIVALENT", 0.50, m["T-C7"]["eq"])
    prob("P5", "T-C7 LOSS", 0.10, m["T-C7"]["loss"])
    num("P6", "D9", m["T-C9"]["D9"], 0.20, 0.40)
    prob("P6", "T-C9 HELD", 0.95, V["T-C9"] == "HELD")
    num("P7", "D_fd massive", m["T-C8"]["D"], 0.01, 0.06)
    num("P7", "D_fd clinc", c["T-C8"]["D"], 0.04, 0.12)
    prob("P7", "T-C8 HELD", 0.80, V["T-C8"] == "HELD")
    prob("P7", "T-C8b HELD", 0.65, V["T-C8b"] == "HELD")
    L.append("PREDICTION P8 Mantel r points (no interval registered; printed, not scored as intervals): MASSIVE %s vs 0.35, CLINC %s vs 0.30"
             % (f(m["T-C4"]["r"], "%+.4f"), f(c["T-C4"]["r"], "%+.4f")))
    prob("P8", "T-C4 HELD", 0.65, V["T-C4"] == "HELD")
    pos = bool(m["T-C3"]["slope_logsize"] > 0 and c["T-C3"]["slope_logsize"] > 0)
    prob("P9", "T-C3 slope positive on both AF arms (R9)", 0.80, pos)
    L.append("NUMERIC PREDICTIONS: %d of %d HELD" % (held.count("HELD"), len(held)))
    return L


# ================================================================================================ entry points
def derive_inputs(db):
    con = II.open_db_ro(db)
    try:
        items = II.rows_from_db(con)
    finally:
        con.close()
    return EX.derive(items)


def port_parity(rd, snap_db, emb_db, out=print):
    """PORT PARITY on any existing build (no S1 build needed): the Python descent's top-1 against the engine's own per-query top-1
    in <rd>/validation/MAIN_routing_diagnostics.txt, every query of that file, vectors from `emb_db` (read-only). Prints the
    agreement; writes nothing. (A READY check of the port before S1's builds exist; the S1 acceptance (a) is the binding one.)"""
    sid, why = snapshot_id_of(rd)
    if sid is None:
        refuse("%s: %s" % (rd, why))
    graph, settings = snapshot_row(snap_db, sid)
    T = tree_of(graph, settings)
    eng = parse_diagnostics(os.path.join(rd, "validation", "MAIN_routing_diagnostics.txt"))
    texts = sorted(eng)
    vec = load_raw(emb_db, texts, T["d"], allow_missing=True)
    have = [t for t in texts if t in vec]
    if len(have) != len(texts):
        refuse("PORT PARITY: %d of %d distinct diagnostics queries have no vector in %s; parity is read on EVERY query or not at all "
               "(READY_intent_s1 D-4: a subset never prints ACCEPTED)" % (len(texts) - len(have), len(texts), emb_db))
    X = S0.unit(np.vstack([vec[t] for t in have]).astype(np.float64)) if have else np.zeros((0, T["d"]))
    py = Descent(T).top1(X)
    k = sum(1 for t, p in zip(have, py) if eng[t] == p)
    out("%s PORT PARITY %s (snapshot %s, %d leaves, slice %d, knobs %s): %d of %d queries with a vector agree (%.5f); %d without a vector; "
        "unrouted engine %d / python %d -> %s" % (TAG, rd, sid, len(T["leaves"]), T["d"], T["knobs"], k, len(have), k / max(1, len(have)),
                                                    len(texts) - len(have), sum(1 for t in have if eng[t] is None), sum(1 for p in py if p is None),
                                                    "ACCEPTED (>= 99.9%)" if accepted(k, len(have)) else "NOT ACCEPTED"))
    return k, len(have)


def check_heavy():
    heavy = S0._foreign_heavy()
    if heavy:
        refuse("a foreign heavy process runs (%s): the readout never runs beside a construction or site null" % heavy)


def dry_run(snap_db=None, data_root=None, db=None, emb_dir=None, pins_file=None, out=print, skip_heavy=False):
    out("%s DRY RUN: zero calls; nothing written; no EVAL statistic. %s" % (TAG, REGISTRATION))
    check_code_pins()
    snap_db = snap_db or os.path.join(data_root or DATA_ROOT, "snapshots.db")
    pres = arm_presence(snap_db, data_root)
    for n in REQUIRED + OPTIONAL:
        out("%s arm %-8s %s %s%s" % (TAG, n, "PRESENT" if pres[n]["present"] else "ABSENT", pres[n]["sid"] or "-", (" (%s)" % pres[n]["why"]) if pres[n]["why"] else ""))
    absent = [n for n in REQUIRED if not pres[n]["present"]]
    if absent:
        refuse("builds ABSENT: %s (the readout reads only complete builds; M-AF-g alone may be omitted)" % ", ".join(absent))
    if not skip_heavy:
        check_heavy()
    present = [n for n in REQUIRED + OPTIONAL if pres[n]["present"]]
    W = load_world(present, db, emb_dir, pins_file)
    cen, bad = census(W)
    out("%s census: %s" % (TAG, "; ".join("%s %d / %d" % (k, v[0], v[1]) for k, v in cen.items())))
    if bad:
        refuse("census off by more than 5%%: %s (re-state by bracket before any read)" % "; ".join(bad))
    D_ex = derive_inputs(W["db"])
    emb_pins = {e[4:]: s for e, s in W["pins"].items() if e.startswith("emb_")}
    trees, graphs = {}, {}
    for n in present:
        T, g = load_tree_checked(n, pres[n], snap_db, D_ex, emb_pins)
        trees[n], graphs[n] = (T, pres[n]["sid"]), g
        out("%s %s: %d nodes, %d leaves, slice %d, multi-parent %d, knobs %s" % (TAG, n, len(T["nodes"]), len(T["leaves"]), T["d"], T["multi_parent"], T["knobs"]))
    P = p0(graphs["M-AF"], graphs["M-AF'"])
    out("%s P0: %s (%d nodes differing in queryIds set)" % (TAG, "HOLDS" if P["holds"] else "FAILS", P["members_differ"]))
    STATE["gate_frozen"] = False
    for n in present:
        A = phase_gate(make_arm(W, n, *trees[n]), n in AF_OF.values(), need_km=False)
        g = A["gate"]
        out("%s GATE %s: delta_c computed at --run (k-means); T-C9 thr %.5f; descent agreement %.5f (%d of %d) %s" % (TAG, n, g["thr_tree"], A["accept"]["agree"],
                                                                                              A["accept"]["k"], A["accept"]["n"], "ACCEPTED" if A["accept"]["accepted"] else "NOT ACCEPTED"))
    out("%s DRY RUN complete: %d arms present; no EVAL statistic computed; 0 files written" % (TAG, len(present)))
    return 0


def run(snap_db=None, data_root=None, db=None, emb_dir=None, pins_file=None, out_dir=None, n_perm=N_PERM, n_random=N_RANDOM_H,
        skip_heavy=False, diag_paths=None):
    out_dir = out_dir or OUT_DIR
    path, ipath = os.path.join(out_dir, OUTCOME), os.path.join(out_dir, ITEMS)
    for p in (path, ipath):
        if os.path.lexists(p):
            refuse("%s exists: the outcome is write-once" % p)
    check_code_pins()
    if not skip_heavy:
        check_heavy()
    snap_db = snap_db or os.path.join(data_root or DATA_ROOT, "snapshots.db")
    pres = arm_presence(snap_db, data_root)
    absent = [n for n in REQUIRED if not pres[n]["present"]]
    if absent:
        refuse("builds ABSENT: %s" % ", ".join(absent))
    present = [n for n in REQUIRED + OPTIONAL if pres[n]["present"]]
    del FIT_LOG[:]
    W = load_world(present, db, emb_dir, pins_file)
    cen, bad = census(W)
    if bad:
        refuse("census off by more than 5%%: %s" % "; ".join(bad))
    D_ex = derive_inputs(W["db"])
    emb_pins = {e[4:]: s for e, s in W["pins"].items() if e.startswith("emb_")}
    trees, graphs = {}, {}
    for n in present:
        T, g = load_tree_checked(n, pres[n], snap_db, D_ex, emb_pins)
        trees[n], graphs[n] = (T, pres[n]["sid"]), g
    R, arms = compute(W, trees, graphs, diag_paths=diag_paths, n_perm=n_perm, n_random=n_random)
    # pins re-checked after the readouts: a change refuses and nothing is written
    S0.pin_check(W["db"], "ingest_db", True, label="ingest (after)")
    for e in sorted({ARMS[n]["emb"] for n in present}):
        S0.pin_check(os.path.join(W["emb_dir"], "intent_emb_%s.db" % e), "emb", True, sub=e, label="intent_emb_%s.db (after)" % e)
    meta = {"script": "tools/analysis/intent_transfer_s1.py blob:%s (LF)" % _blob(os.path.abspath(__file__)),
            "instrument": ", ".join("%s blob:%s" % kv for kv in PINNED_CODE.items()) + ", intent_s1_export.py blob:%s" % _blob(os.path.join(HERE, "intent_s1_export.py")),
            "pins (sha256-bytes)": json.dumps(W["pins"], sort_keys=True), "census": json.dumps(cen, sort_keys=True), "_sids": {n: pres[n]["sid"] for n in present}}
    lines = render(R, meta)
    os.makedirs(out_dir, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(l for l in lines) + "\n")
    with open(ipath, "x", encoding="utf-8", newline="\n") as fh:
        fh.write("arm,item_id,flat_leaf,descent_leaf\n")
        for n in AF_OF.values():
            if R["stopped"]:
                break
            A = arms[n]
            r8 = R["arms"][n]["T-C8"]
            fl = flat_leaf(A["T"], A["X"][r8["ev"]])
            for i, j, dl in zip(r8["ev"], fl, r8["descent_leaf"]):
                fh.write("%s,%s,%s,%s\n" % (n, A["C"].ids[i], A["T"]["leaves"][j], dl or "<unrouted>"))
    print("%s outcome written: %s" % (TAG, path))
    return R, lines, path


# ================================================================================================ selftest (fixtures only)
SELFTEST_CASES = ("ST-DESCENT", "ST-STATS", "ST-HIER", "ST-RENDER", "ST-E2E", "ST-REFUSE")


def _hand_tree():
    """A 3-level hand tree for the descent: root r -> a, b; a -> a1, a2 (leaves); b -> b1 (leaf with no TRAIN), b2."""
    def mu(v):
        v = np.asarray(v, dtype=np.float64)
        return (v / np.linalg.norm(v)).tolist()
    nodes = [
        {"id": "r", "childIds": ["a", "b"], "parentIds": [], "sliceDim": 3, "vmfMu": mu([1, 1, 1]), "vmfKappa": 5.0, "queryIds": [], "queryWeights": {}},
        {"id": "a", "childIds": ["a1", "a2"], "parentIds": ["r"], "sliceDim": 3, "vmfMu": mu([1, 0.2, 0]), "vmfKappa": 10.0, "queryIds": [], "queryWeights": {}},
        {"id": "b", "childIds": ["b1", "b2"], "parentIds": ["r"], "sliceDim": 3, "vmfMu": mu([0, 0.3, 1]), "vmfKappa": 10.0, "queryIds": [], "queryWeights": {}},
        {"id": "a1", "childIds": [], "parentIds": ["a"], "sliceDim": 3, "vmfMu": mu([1, 0, 0]), "vmfKappa": 20.0, "queryIds": ["q1"], "queryWeights": {"q1": 3.0}},
        {"id": "a2", "childIds": [], "parentIds": ["a"], "sliceDim": 3, "vmfMu": mu([1, 0.6, 0]), "vmfKappa": 40.0, "queryIds": ["q2"], "queryWeights": {"q2": 1.0}},
        {"id": "b1", "childIds": [], "parentIds": ["b"], "sliceDim": 3, "vmfMu": mu([0, 1, 0.4]), "vmfKappa": 15.0, "queryIds": [], "queryWeights": {"q3": 1.0}},
        {"id": "b2", "childIds": [], "parentIds": ["b"], "sliceDim": 3, "vmfMu": mu([0, 0, 1]), "vmfKappa": 25.0, "queryIds": ["q4"], "queryWeights": {"q4": 1.0}},
    ]
    settings = {"membershipFloor": 0.25, "routingBeamGamma": 0.2, "descentMargin": 0.12, "maxLeafAssignments": 5, "dagMode": "DAG_MAX"}
    return {"rootId": "r", "nodes": nodes}, settings


def _ref_route(T, x):
    """An independent, literal transcription of TaxonomyTrickler.trickle + routeQueryToLeaves + the profiles filter (path
    enumeration over a TREE, where per-path and per-node pruning coincide), used only to cross-check Descent."""
    r = shrinkages(T)
    k = T["knobs"]
    logp = {}

    def walk(n, lp):
        if lp < LOG_NEG:
            return
        logp[n] = lp
        ks = T["kids"][n]
        if not ks:
            return
        mk = max(np.mean([float(T["nodes"][c]["vmfKappa"]) for c in ks]), 1e-9)
        dots = [float(np.dot(x, T["mu"][c])) for c in ks]
        if n in T["mu"] and max(dots) < max(r[n] - k["descentMargin"], 0.0) * float(np.dot(x, T["mu"][n])):
            return
        sc = [mk * d for d in dots]
        beam = [i for i in range(len(ks)) if dots[i] >= max(dots) - k["routingBeamGamma"]]
        ms = max(sc)
        lse = ms + math.log(sum(math.exp(sc[i] - ms) for i in beam))
        for i in beam:
            walk(ks[i], lp + sc[i] - lse)
    walk(T["root"], 0.0)
    cand = {n: v for n, v in logp.items() if not T["kids"][n]}
    for n, v in logp.items():
        if T["kids"][n] and not any(c in logp for c in T["kids"][n]):
            cand[n] = v
    tot = math.log(sum(math.exp(v) for v in cand.values()))
    share = {n: v - tot for n, v in cand.items()}
    adm = {n: v for n, v in share.items() if v >= math.log(k["membershipFloor"])} or dict([max(share.items(), key=lambda kv: kv[1])])
    top = dict(sorted(adm.items(), key=lambda kv: -kv[1])[:k["maxLeafAssignments"]])
    leaves = [n for n, _v in sorted(top.items(), key=lambda kv: -kv[1]) if not T["kids"][n] and T["has_train"].get(n)]
    t2 = math.log(sum(math.exp(v) for v in top.values()))
    return (leaves[0] if leaves else None), {n: v - t2 for n, v in top.items()}


def _fixture_corpus(rng, name, n_coarse, n_fine_per, n_per_fine, dim):
    rows, centers = [], {}
    k = 0
    for ci in range(n_coarse):
        cvec = rng.normal(size=dim)
        for fi in range(n_fine_per):
            coarse, fine = "c%d" % ci, "c%d_f%d" % (ci, fi)
            fvec = cvec + 0.8 * rng.normal(size=dim)
            centers[fine] = fvec
            for j in range(n_per_fine):
                text = "%s synthetic %s item %d" % (name, fine, j)
                sk = SS.stem_key(text)
                side = SS.side_of_hash(SS.side_hash(sk))
                rows.append({"item_id": "%s:x:%05d" % (name, k), "corpus": name, "text": text, "coarse": coarse, "fine": fine, "is_oos": 0,
                             "annot": None, "stem_key": sk, "hash_side": side, "side": side, "drop_reason": None})
                k += 1
    if name == "clinc":
        for j in range(40):
            text = "%s synthetic oos %d" % (name, j)
            sk = SS.stem_key(text)
            rows.append({"item_id": "%s:oos:%05d" % (name, j), "corpus": name, "text": text, "coarse": "oos", "fine": "oos", "is_oos": 1,
                         "annot": None, "stem_key": sk, "hash_side": SS.side_of_hash(SS.side_hash(sk)), "side": SS.EVAL, "drop_reason": None})
    vecs = {}
    for r in rows:
        base = centers.get(r["fine"], rng.normal(size=dim) * 3)
        vecs[r["text"]] = (base + 0.9 * rng.normal(size=dim)).astype(np.float32)
    return rows, vecs


def _fixture_tree(C, X, side, d, kappa=30.0, seed=0, perturb=0.0):
    """A synthetic build: root -> coarse nodes -> leaves = spherical k-means (2 per fine label's coarse share) on TRAIN, mu = means."""
    rng = np.random.default_rng(seed)
    tr = np.nonzero(C.kept & ~C.oos & (side == SS.TRAIN))[0]
    nodes, root = [], "n00000001"
    kid_ids = []
    nid = [2]

    def new_id():
        i = "n%08d" % nid[0]
        nid[0] += 1
        return i
    for cz in sorted(set(C.coarse[tr].tolist())):
        sel = tr[C.coarse[tr] == cz]
        cid = new_id()
        kid_ids.append(cid)
        k = max(1, len(set(C.fine[sel].tolist())))
        Cm = S0.skmeans(X[sel], k, seed)
        lab = S0.assign(X[sel], Cm)
        leaf_ids = []
        for j in range(k):
            lid = new_id()
            mem = sel[lab == j]
            mu = S0.unit((X[mem].mean(0) if len(mem) else Cm[j])[None, :] + perturb * rng.normal(size=(1, d)))[0]
            qids = ["q_%s" % hashlib.sha256(C.text[i].encode()).hexdigest()[:16] for i in mem]
            nodes.append({"id": lid, "childIds": [], "parentIds": [cid], "sliceDim": d, "vmfMu": mu.tolist(), "vmfKappa": kappa,
                          "queryIds": qids, "queryWeights": {q: 1.0 for q in qids}})
            leaf_ids.append(lid)
        nodes.append({"id": cid, "childIds": leaf_ids, "parentIds": [root], "sliceDim": d, "vmfMu": S0.unit(X[sel].mean(0)[None, :])[0].tolist(),
                      "vmfKappa": kappa / 2, "queryIds": [], "queryWeights": {}})
    nodes.append({"id": root, "childIds": kid_ids, "parentIds": [], "sliceDim": d, "vmfMu": S0.unit(X[tr].mean(0)[None, :])[0].tolist(),
                  "vmfKappa": 5.0, "queryIds": [], "queryWeights": {}})
    settings = {"membershipFloor": 0.25, "routingBeamGamma": 0.2, "descentMargin": 0.12, "maxLeafAssignments": 5, "dagMode": "DAG_MAX"}
    return {"rootId": root, "nodes": nodes}, settings


def _write_diag(path, texts, tops):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("=== Per-Query Routing Diagnostics (MAIN) ===\n\n")
        for t, top in zip(texts, tops):
            fh.write('Query: "%s"\nTrue Domain: X\n' % t)
            if top is None:
                fh.write("Candidate Count: 0\nNo candidates matched.\n")
            else:
                fh.write("Candidate Count: 1\nTop-1 Leaf: %s (ID: %s) | Dominant: X | Conf: 0.9000\n" % (top, top))
            fh.write("--------------------------------------------------\n")


def build_fixture(td, variants_n=60):
    """A complete synthetic world + nine builds on disk (snapshots.db, run dirs, manifests, diagnostics) under td."""
    rng = np.random.default_rng(7)
    rows_m, vm = _fixture_corpus(rng, "massive", 3, 3, 40, 16)
    rows_c, vc = _fixture_corpus(rng, "clinc", 3, 4, 30, 16)
    CS = {"massive": S0.Corpus("massive", rows_m), "clinc": S0.Corpus("clinc", rows_c)}
    vecs = dict(vm)
    vecs.update(vc)
    C = CS["massive"]
    ev = np.nonzero(C.kept & (C.side == SS.EVAL))[0]
    var = []
    for i in ev[:variants_n]:
        t = C.text[i] + " variant"
        vecs[t] = (vecs[C.text[i]] + 0.3 * rng.normal(size=16)).astype(np.float32)
        var.append((int(i), t, ("slot",)))
    W = {"CS": CS, "variants": var, "variant_counts": {"variants": len(var)}, "vecs": {"qwen3": vecs, "gemma": vecs}, "db": None,
         "emb_dir": None, "pins": {}}
    trees, graphs, diags = {}, {}, {}
    for name in REQUIRED + OPTIONAL:
        a = ARMS[name]
        Cx = CS[a["corpus"]]
        side = arm_sides(Cx, a["salt"])
        d = 8 if a["recipe"] == "AF" else 12
        R, have = raw_matrix(Cx, vecs, 16)
        X = sliced(R, d)
        seed = {"M-o1": 1, "M-o2": 2}.get(name, 0)
        g, s = _fixture_tree(Cx, X, side, d, seed=seed, perturb=0.25 + (0.05 * seed))
        T = tree_of(g, s)
        trees[name] = (T, "sid_" + a["slug"])
        graphs[name] = g
        ga = np.nonzero(Cx.kept & ~Cx.oos & (side == SS.GATE))[0]
        texts, idx, seen = [], [], set()
        for i in ga:
            if Cx.text[i] not in seen:
                seen.add(Cx.text[i])
                texts.append(Cx.text[i])
                idx.append(i)
        tops = Descent(T).top1(X[np.array(idx, dtype=int)])
        diags[name] = os.path.join(td, a["slug"], "validation", "MAIN_routing_diagnostics.txt")
        _write_diag(diags[name], texts, tops)
    return W, trees, graphs, diags


def selftest(only=None, quiet=False, fixture=None):
    sel = set(only or SELFTEST_CASES)
    n_ok = [0]

    def check(cond, what):
        if not cond:
            raise AssertionError("SELFTEST FAILED: " + what)
        n_ok[0] += 1

    def refused(fn, needle):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn()
        except SystemExit as e:
            check(needle in str(e), "refusal %r carries %r" % (str(e)[:200], needle))
            return
        raise AssertionError("SELFTEST FAILED: expected a refusal containing %r" % needle)

    saved = (STATE["gate_frozen"], list(FIT_LOG))
    td = tempfile.mkdtemp(prefix="intent_s1_st_")
    try:
        if "ST-DESCENT" in sel:
            g, s = _hand_tree()
            T = tree_of(g, s)
            Dsc = Descent(T)
            r = shrinkages(T)
            wa = np.array([3.0, 1.0]) / 4.0
            sa = np.linalg.norm(wa[0] * T["mu"]["a1"] + wa[1] * T["mu"]["a2"])
            check(abs(r["a"] - sa) < 1e-12, "shrinkage = ||sum w_c mu_c|| with mass shares (%.6f vs %.6f)" % (r["a"], sa))
            wb = np.array([1.0, 1.0]) / 2.0
            check(abs(r["b"] - np.linalg.norm(wb[0] * T["mu"]["b1"] + wb[1] * T["mu"]["b2"])) < 1e-12, "shrinkage of b (queryWeights mass, not queryIds)")
            rng = np.random.default_rng(3)
            P = S0.unit(rng.normal(size=(400, 3)))
            got = Dsc.top1(P)
            refm = [_ref_route(T, x) for x in P]
            ref = [r_[0] for r_ in refm]

            def mem_eq(Dx, Tx, refs):
                ms = Dx.memberships(P)
                return all(set(a_) == set(b_[1]) and all(abs(a_[k_] - b_[1][k_]) < 1e-9 for k_ in a_) for a_, b_ in zip(ms, refs))
            check(got == ref, "Descent == the literal path-enumeration transcription on 400 random queries (%d differ)" % sum(1 for a, b in zip(got, ref) if a != b))
            check(mem_eq(Dsc, T, refm), "the final memberships (nodes and masses) equal the transcription's")
            check(any(len(mm) >= 2 for mm in Dsc.memberships(P)) and any(T["kids"][n_] for mm in Dsc.memberships(P) for n_ in mm),
                  "the fixture exercises shared membership and internal (residual) candidates")
            check(any(x is None for x in got) and len(set(x for x in got if x)) >= 3, "the fixture exercises UNROUTED and >= 3 leaves")
            # b1 has queryWeights but no queryIds: it is never a top-1 (the profiles filter)
            check("b1" not in got, "a leaf without TRAIN members is never top-1")
            # gate: a query aligned with a node's own direction but between its children stops there (internal candidate) -> b2 or None
            x = S0.unit(np.array([[0.0, 0.62, 0.78]]))[0]
            check(Dsc.top1(x[None, :])[0] == _ref_route(T, x)[0], "the gate case agrees with the reference")
            # floor and cap: with maxLeafAssignments 1 and floor 0.99 the single best candidate is kept
            s2 = dict(s, membershipFloor=0.99, maxLeafAssignments=1)
            T2 = tree_of(g, s2)
            check(Descent(T2).top1(P) == [_ref_route(T2, x)[0] for x in P], "floor 0.99 / cap 1 agree with the reference")
            s2b = dict(s, membershipFloor=1e-4, maxLeafAssignments=1)
            T2b = tree_of(g, s2b)
            check(mem_eq(Descent(T2b), T2b, [_ref_route(T2b, x) for x in P]) and all(len(mm) == 1 for mm in Descent(T2b).memberships(P)), "the cap binds (floor 1e-4, cap 1)")
            s2d = dict(s, routingBeamGamma=1.0, membershipFloor=1e-4)
            T2d = tree_of(g, s2d)
            ms2d = Descent(T2d).memberships(P)
            mixed = sum(1 for mm in ms2d if any(T2d["kids"][n_] for n_ in mm) and any(not T2d["kids"][n_] for n_ in mm))
            check(mixed > 0 and mem_eq(Descent(T2d), T2d, [_ref_route(T2d, x) for x in P]),
                  "residual (internal) candidates beside reached leaves agree with the reference (%d mixed queries)" % mixed)
            s2c = dict(s, routingBeamGamma=0.05)
            T2c = tree_of(g, s2c)
            check(mem_eq(Descent(T2c), T2c, [_ref_route(T2c, x) for x in P]), "a narrow beam (gamma 0.05) agrees with the reference")
            s3 = dict(s, descentMargin=0.0)
            T3 = tree_of(g, s3)
            check(Descent(T3).top1(P) == [_ref_route(T3, x)[0] for x in P], "descentMargin 0 agrees with the reference")
            check(Descent(T3).top1(P) != got, "the descentMargin knob changes routing (it is read from settings)")
            s4 = dict(s, dagMode="TREE_BASELINE")
            T4 = tree_of(g, s4)
            got4 = Descent(T4).top1(P)
            check(len(got4) == 400, "TREE_BASELINE routes (residual off)")
            # parse_diagnostics: the engine's file format
            p = os.path.join(td, "diag.txt")
            _write_diag(p, ["hello there", "set an alarm"], ["n00000003", None])
            check(parse_diagnostics(p) == {"hello there": "n00000003", "set an alarm": None}, "diagnostics parser")
            _write_diag(p, ["line one\nline two", "plain"], ["n00000007", "n00000008"])
            check(parse_diagnostics(p) == {"line one\nline two": "n00000007", "plain": "n00000008"}, "D-4: a multi-line query text parses as one block")
            open(p, "a", encoding="utf-8").write('Query: "broken"\nTrue Domain: X\nCandidate Count: 1\nTop-1 Leaf garbled\n')
            refused(lambda: parse_diagnostics(p), "query blocks parsed")
            T5 = tree_of(g, dict(s, routingBeamGamma=1.0, membershipFloor=1e-4, dagMode="TREE_BASELINE"))
            ms5 = Descent(T5).memberships(P)
            check(not any(any(T5["kids"][n_] for n_ in mm) and any(not T5["kids"][n_] for n_ in mm) for mm in ms5),
                  "D-7: TREE_BASELINE admits no internal candidate beside a reached leaf (residual off)")
            refused(lambda: tree_of({"rootId": "r", "nodes": [dict(n, crossLinkChildIds=["a1"]) if n["id"] == "r" else n for n in g["nodes"]]}, s), "crossLinkChildIds")
            refused(lambda: tree_of(g, {k: v for k, v in s.items() if k != "descentMargin"}), "lack a routing knob")
        if "ST-STATS" in sel:
            # TOST verdict: every branch, joined outcomes
            check(tost_verdict(0.0, 0.001, 0.01, -0.002, 0.002, 0.005)["verdict"] == "EQUIVALENT", "EQUIVALENT")
            check(tost_verdict(-0.02, 0.001, 0.05, -0.022, -0.018, 0.005)["verdict"] == "EQUIVALENT / LOSS-FLAGGED", "joined LOSS")
            check(tost_verdict(0.02, 0.001, 0.05, 0.018, 0.022, 0.005)["verdict"] == "EQUIVALENT / GAIN-FLAGGED", "joined GAIN")
            check(tost_verdict(-0.02, 0.001, 0.005, -0.022, -0.018, 0.005)["verdict"] == "LOSS", "LOSS")
            check(tost_verdict(0.02, 0.001, 0.005, 0.018, 0.022, 0.005)["verdict"] == "GAIN", "GAIN")
            check(tost_verdict(-0.004, 0.003, 0.005, -0.01, 0.002, 0.005)["verdict"] == "UNDETERMINED", "UNDETERMINED")
            check(tost_verdict(0.0, 0.001, -0.01, -0.002, 0.002, 0.005)["verdict"] == "UNDETERMINED", "delta <= 0 -> no EQUIVALENT")
            v = tost_verdict(0.0, 0.003, 0.0049, -0.01, 0.01, 0.005)
            check(abs(v["hi90"] - Z90 * 0.003) < 1e-12 and not v["eq"], "TOST at 1.645 SE_total; boundary strict (0.004935 > 0.0049)")
            check(tost_verdict(0.0, 0.003, Z90 * 0.003, -0.01, 0.01, 0.005)["eq"] is False, "EQUIVALENT strictly inside: hi90 == delta is not inside")
            check(tost_verdict(0.0, 0.003, Z90 * 0.003 * 1.0001, -0.01, 0.01, 0.005)["eq"] is True, "EQUIVALENT just inside")
            check(tost_verdict(-0.006, 0.001, 0.05, -0.008, -0.004, 0.006)["loss"] is False, "LOSS needs D < -bar strictly")
            check(tost_verdict(-0.007, 0.001, 0.05, -0.008, 0.0, 0.006)["loss"] is False, "LOSS needs the 95% CI < 0 strictly")
            check(ci_verdict(0.001, 0.1) == "HELD" and ci_verdict(-0.1, 0.0) == "FAILED" and ci_verdict(0.0, 0.1) == "UNDETERMINED", "ci_verdict bounds")
            check(t_c2_verdict(0.03, 0.01, 0.05, 0.02) == "HELD" and t_c2_verdict(0.015, 0.01, 0.05, 0.02) == "UNDETERMINED"
                  and t_c2_verdict(-0.03, -0.05, -0.01, 0.0) == "FAILED" and t_c2_verdict(0.03, -0.01, 0.05, 0.0) == "UNDETERMINED", "T-C2 branches")
            check(t_c8_verdict("HELD", "HELD") == "HELD" and t_c8_verdict("HELD", "FAILED") == "FAILED" and t_c8_verdict("FAILED", "UNDETERMINED") == "FAILED"
                  and t_c8_verdict("HELD", "UNDETERMINED") == "UNDETERMINED", "T-C8 both / either")
            # READY_intent_s1 B-1 probe: constant distance (K 10) -> r nan, p nan, NOT EVALUABLE (never 1/(n+1), never HELD)
            Kc = 10
            dist_c = np.ones((Kc, Kc)) - np.eye(Kc)
            cnt_c = np.random.default_rng(2).integers(0, 5, size=(Kc, Kc)).astype(float)
            cnt_c = np.triu(cnt_c, 1) + np.triu(cnt_c, 1).T
            rc, pc_ = mantel(list(range(Kc)), cnt_c, dist_c, 1000, 1)
            check(not np.isfinite(rc) and not np.isfinite(pc_) and t_c4_verdict(pc_, pc_) == "NOT EVALUABLE", "B-1: constant distance -> r nan, p nan, NOT EVALUABLE (p %r)" % pc_)
            rz, pz = mantel(list(range(Kc)), np.zeros((Kc, Kc)), np.abs(np.subtract.outer(np.arange(Kc), np.arange(Kc))).astype(float), 200, 1)
            check(not np.isfinite(pz) and t_c4_verdict(0.001, pz) == "NOT EVALUABLE" and t_c4_verdict(pz, 0.9) == "NOT EVALUABLE", "B-1: constant counts on either corpus -> NOT EVALUABLE")
            check(t_c4_verdict(0.01, 0.02) == "HELD" and t_c4_verdict(0.05, 0.2) == "FAILED" and t_c4_verdict(0.01, 0.05) == "UNDETERMINED", "T-C4 p < 0.05 strict")
            check(G13.g13_verdict(0.01, 0.001, 0.02, 0.005) == "HELD" and G13.g13_verdict(-0.01, -0.02, -0.001, 0.005) == "FAILED", "G13 verdict")
            check(in_band(0.0, 0.0, 0.1) == "HELD" and in_band(0.1, 0.0, 0.1) == "HELD" and in_band(0.11, 0.0, 0.1) == "FAILED", "bands inclusive")
            check(abs(brier(0.8, True) - 0.04) < 1e-12 and abs(brier(0.8, False) - 0.64) < 1e-12, "Brier")
            check(majority(["b", "a", "a", "b"], [0, 0, 0, 0], 2) == ["a", None], "majority: ties to the smaller label; empty group None")
            md = modal_leaves([1, 0, 0, 0, 2, 2], ["x", "x", "y", "y", "y", "z"], ["n3", "n1", "n2"])
            check(md == {"x": "n1", "y": "n3", "z": "n2"}, "modal leaf: plurality per item, ties to the smallest node id (%s)" % md)
            # Mantel: perfect association -> p = 1 / (1 + n_perm) at most a few draws
            K = 8
            dist = np.abs(np.subtract.outer(np.arange(K), np.arange(K))).astype(float)
            cnt = np.maximum(0, 8 - dist)
            np.fill_diagonal(cnt, 0)
            r, p = mantel(list(range(K)), cnt, dist, 2000, 1)
            check(r > 0.9 and p < 0.01, "Mantel on a planted association (r %.3f, p %.4f)" % (r, p))
            r2, p2 = mantel(list(range(K)), cnt, -dist + 10 * (dist > 0), 500, 1)
            check(r2 < 0 and p2 > 0.5, "Mantel one-sided: the reversed association does not count (r %.3f p %.3f)" % (r2, p2))
            check(abs((1 + 0) / (1 + 2000) - 1.0 / 2001) < 1e-15, "p formula")
            # boot = S0.comp_weights percentile of the registered B
            comp = np.repeat(np.arange(50), 2)
            x = np.r_[np.ones(50), np.zeros(50)]
            lo, hi, se, dr = boot(comp, lambda w: wmean(x, w), 5, B=500)
            check(len(dr) == 500 and lo <= 0.5 <= hi and se > 0, "boot shape")
        if "ST-HIER" in sel:
            # DP: a perfect hierarchy has DP 1; a mixed one less; hand value
            parent = {"l1": "p", "l2": "p", "l3": "q", "l4": "q", "p": "r", "q": "r"}
            leaves = ["l1", "l2", "l3", "l4"]
            dp = dendrogram_purity(parent, leaves, ["l1", "l2", "l3", "l4"], ["A", "A", "B", "B"])
            check(abs(dp - 1.0) < 1e-12, "DP perfect = 1")
            dp2 = dendrogram_purity(parent, leaves, ["l1", "l3", "l2", "l4"], ["A", "A", "B", "B"])
            check(abs(dp2 - 0.5) < 1e-12, "DP hand value: same-class pairs meet at the root (purity 1/2) -> 0.5 (got %.4f)" % dp2)
            dp3 = dendrogram_purity(parent, leaves, ["l1", "l1", "l1", "l3"], ["A", "A", "B", "B"])
            # A pair (l1,l1): LCA l1 purity 2/3; B pair (l1,l3): LCA r purity 2/4 -> mean 0.58333
            check(abs(dp3 - (2 / 3 + 0.5) / 2) < 1e-12, "DP hand value with a shared leaf (got %.5f)" % dp3)
            w = np.array([2.0, 1.0, 1.0, 1.0])
            dpw = dendrogram_purity(parent, leaves, ["l1", "l2", "l3", "l4"], ["A", "A", "B", "B"], w)
            check(abs(dpw - 1.0) < 1e-12, "weighted copies keep a perfect DP")
            check(lca_dist(parent, "l1", "l2") == 2 and lca_dist(parent, "l1", "l3") == 4 and lca_dist(parent, "l1", "l1") == 0, "LCA distance in edges")
            mu = S0.unit(np.array([[1, 0, 0], [0.9, 0.1, 0], [0, 0, 1], [0, 0.1, 0.9]], dtype=float))
            ap = agglomerative_parent(leaves, mu)
            check(lca_dist(ap, "l1", "l2") == 2 and lca_dist(ap, "l3", "l4") == 2 and lca_dist(ap, "l1", "l3") == 4, "average-link pairs the near leaves")
            rp = random_parent(leaves, np.random.default_rng(1))
            check(len(rp) == 2 * len(leaves) - 2, "random binary hierarchy shape")
        if fixture is None and sel & {"ST-RENDER", "ST-E2E", "ST-REFUSE"}:
            fixture = build_fixture(td)
        if "ST-E2E" in sel or "ST-RENDER" in sel or "ST-REFUSE" in sel:
            W, trees, graphs, diags = fixture
            del FIT_LOG[:]
            # B-2: S0's 0.834 / 0.692 do not hold on the fixture -> compute() REFUSES; then the fixture's own 3-dp values are installed
            saved_repro = dict(REPRO_S0)
            refused(lambda: compute(W, trees, graphs, diag_paths=diags, n_perm=10, n_random=2), "do not reproduce S0's 0.834 / 0.692")
            STATE["gate_frozen"] = True
            Af = make_arm(W, "M-AF", *trees["M-AF"])
            trf = side_rows(Af["C"], Af["side"], Af["have"], SS.TRAIN)
            Af["tr"] = trf
            oif = np.array([i for i, _t, _c in W["variants"]])
            Xvf = S0.unit(np.vstack([W["vecs"]["qwen3"][t][:Af["T"]["d"]] for _i, t, _c in W["variants"]]).astype(np.float64))
            uf, Gf = S0.centroids_by_label(Af["X"][trf], Af["C"].fine[trf])
            ceil_f = float(np.mean(uf[S0.assign(Af["X"][oif], Gf)] == uf[S0.assign(Xvf, Gf)]))
            floor_f = cofile_floor(Af, S0.skmeans(Af["X"][trf], 60, 0), len(oif))
            REPRO_S0["M-AF"] = (round(ceil_f, 3), round(floor_f, 3))
            # the real compute + render entry, on the fixture world
            with contextlib.redirect_stdout(io.StringIO()):
                R, arms = compute(W, trees, graphs, diag_paths=diags, n_perm=200, n_random=20)
            meta = {"script": "selftest", "_sids": {n: t[1] for n, t in trees.items()}}
            lines = render(R, meta)
            txt = "\n".join(lines)
            V = R["verdicts"]
            m, c = R["arms"]["M-AF"], R["arms"]["C-AF"]
        if "ST-E2E" in sel:
            check(R["P0"]["holds"], "P0 holds for two identical builds")
            check(abs(m["T-C7"]["ceiling"] - ceil_f) < 1e-15 and abs(m["T-C7"]["floor"] - floor_f) < 1e-15, "B-2: ceiling / floor reproduced to the installed 3-dp values")
            A = arms["M-AF"]
            STATE["gate_frozen"] = True
            ev = eval_rows(A)
            truth = S0.codes(A["C"].fine[ev])
            n_tree = S0.nmi(truth, np.argmax(A["X"][ev] @ A["T"]["leaf_mu"].T, axis=1))
            n_km = np.mean([S0.nmi(truth, S0.assign(A["X"][ev], S0.skmeans(A["X"][A["tr"]], A["L"], s))) for s in SEEDS20])
            check(abs(m["T-C1"]["D"] - (n_tree - n_km)) < 1e-12, "T-C1 D1 = independent NMI recomputation (%.6f)" % m["T-C1"]["D"])
            check(("T-C1 massive (M-AF): D1 %+.5f" % m["T-C1"]["D"]) in txt, "the printed D1 is the computed value")
            check(m["T-C1"]["n"] == len(ev) and m["T-C1"]["L"] == len(A["T"]["leaves"]), "T-C1 denominator = EVAL in-scope items; k = L")
            x = m["T-C1"]
            check(x["verdict"] == tost_verdict(x["D"], x["se_total"], x["delta"], x["lo"], x["hi"], x["bar"])["verdict"]
                  and ("-> %s [" % x["verdict"]) in txt, "the printed T-C1 verdict follows the registered rule")
            nk = [S0.nmi(truth, S0.assign(A["X"][ev], Cm)) for Cm in A["km"]]
            dse = [n_tree - v_ for v_ in nk]
            draws = [S0.nmi(truth, np.argmax(A["X"][ev] @ A["T"]["leaf_mu"].T, axis=1), w_) - np.mean([S0.nmi(truth, S0.assign(A["X"][ev], Cm), w_) for Cm in A["km"]])
                     for w_ in S0.comp_weights(A["C"].comp[ev], BOOT_B, np.random.default_rng(SEED_BOOT + OFF["T-C1"]))]
            se_t = math.sqrt(np.std(draws, ddof=1) ** 2 + np.var(dse, ddof=1) / 20.0)
            check(abs(x["se_total"] - se_t) < 1e-12, "SE_total = sqrt(SE_boot^2 + var_seed(D1) / 20)")
            check(abs(x["spread_K"] - (max(nk[:5]) - min(nk[:5]))) < 1e-15, "spread_K over seeds 0-4")
            check(abs(x["bar"] - max(2.8 * se_t, max(nk[:5]) - min(nk[:5]))) < 1e-15, "bar = max(MDE80, spread_K)")
            check(abs(x["hi90"] - (x["D"] + 1.6448536269514722 * se_t)) < 1e-12, "the TOST half-width is 1.645 SE_total")
            # bar when the seed spread dominates: one k-means seed replaced by random centroids (spread_K > MDE80)
            rk = S0.unit(np.random.default_rng(11).normal(size=A["km"][0].shape))
            xs = t_c1(dict(A, km=[A["km"][0], rk] + list(A["km"][2:])))
            check(xs["spread_K"] > xs["mde"] and abs(xs["bar"] - xs["spread_K"]) < 1e-15, "bar = spread_K when it exceeds MDE80")
            check(abs(x["lo"] - np.percentile(draws, 2.5)) < 1e-12 and abs(x["hi"] - np.percentile(draws, 97.5)) < 1e-12, "T-C1 95% CI = percentile of the component draws (R1)")
            g = R["gate"]["M-AF"]
            ga = A["ga"]
            u, G = S0.centroids_by_label(A["X"][A["tr"]], A["C"].fine[A["tr"]])
            tg = S0.codes(A["C"].fine[ga])
            dc = 0.25 * (S0.nmi(tg, S0.codes(u[S0.assign(A["X"][ga], G)])) - np.mean([S0.nmi(tg, S0.assign(A["X"][ga], Cm)) for Cm in A["km"]]))
            check(abs(g["delta_c"] - dc) < 1e-12 and abs(x["delta"] - dc) < 1e-12, "delta_c measured on GATE (not EVAL, not TRAIN)")
            # T-C1b against G13 verbatim
            y = m["T-C1b"]
            check(abs(y["D"] - (y["p_tree"] - y["p_kc"][0])) < 1e-12 and y["verdict"] == G13.g13_verdict(y["D"], y["lo"], y["hi"], y["spread_KC"]), "T-C1b = P_tree - P(KC_0); G13 verdict")
            check(abs(y["spread_KC"] - (max(y["p_kc"]) - min(y["p_kc"]))) < 1e-15 and len(y["p_kc"]) == 5, "spread_KC over seeds 0-4")
            # T-C8: flatLeaf and descent precision recomputed
            z = m["T-C8"]
            ok_f, _ = fine_correct_flat(A, ev)
            check(abs(z["P_flat"] - ok_f.mean()) < 1e-12 and abs(z["D"] - (z["P_flat"] - z["P_descent"])) < 1e-12, "T-C8 D_fd = P_flat - P_descent")
            check(z["n"] == len(ev), "T-C8 on EVAL")
            check(V["T-C8"] == t_c8_verdict(m["T-C8"]["verdict"], c["T-C8"]["verdict"]) and ("T-C8 (both corpora): %s" % V["T-C8"]) in txt, "T-C8 both-corpora line")
            # T-C8b from independent streams
            check(R["T-C8b"]["D"] == c["T-C8"]["D"] - m["T-C8"]["D"], "T-C8b = clinc - massive")
            # T-C7 / T-C9
            s7 = m["T-C7"]
            oi = np.array([i for i, _t, _c in W["variants"]])
            check(s7["n"] == len(oi) and abs(s7["delta"] - 0.25 * (s7["ceiling"] - s7["floor"])) < 1e-15, "T-C7 on the variants; delta = 0.25 x (ceiling - floor)")
            STATE["gate_frozen"] = True
            f60 = cofile_floor(A, S0.skmeans(A["X"][A["tr"]], 60, 0), s7["n"])
            f60s1 = cofile_floor(A, S0.skmeans(A["X"][A["tr"]], 60, 1), s7["n"])
            fL = cofile_floor(A, A["km"][0], s7["n"])
            check(abs(s7["floor"] - f60) < 1e-15 and f60 != f60s1 and f60 != fL, "B-2 / MY-4: the T-C7 floor = k-means K 60, seed 0 (seed 1 and k = L differ on the fixture)")
            check("DISCLOSED EXCEPTION to HYGIENE's GATE rule (B-2 ruling" in txt, "the B-2 exception is printed")
            u_, G_ = A["sup_cent"]
            check(abs(s7["ceiling"] - np.mean(u_[S0.assign(A["X"][oi], G_)] == u_[S0.assign(s7["Xv"], G_)])) < 1e-15, "T-C7 ceiling = TRAIN gold-fine centroid co-filing")
            s9 = m["T-C9"]
            check(s9["n_abstained"] + s9["n_kept"] == s7["n"] and abs(s9["thr"] - g["thr_tree"]) < 1e-15, "T-C9 groups partition the variants at the GATE threshold")
            mg = margins(A["X"][ga], A["T"]["leaf_mu"])
            check(abs(g["thr_tree"] - np.percentile(mg, 20)) < 1e-12, "T-C9 threshold = GATE 20th percentile of m")
            # T-C2 spread over the three MASSIVE AF arms
            t2 = m["T-C2"]
            check(abs(t2["spread_o"] - (max(t2["D2_by_arm"].values()) - min(t2["D2_by_arm"].values()))) < 1e-15 and len(t2["D2_by_arm"]) == 3, "spread_o over M-AF, M-o1, M-o2")
            check(t2["verdict"] == t_c2_verdict(t2["D2"], t2["lo"], t2["hi"], t2["spread_o"]), "T-C2 verdict")
            # T-C4 modal leaf and Mantel inputs
            t4 = m["T-C4"]
            check(t4["K"] == len(set(A["C"].fine[A["tr"]].tolist())) and t4["n_pairs"] == t4["K"] * (t4["K"] - 1) // 2, "T-C4 over all intents and pairs")
            f0 = sorted(A["modal"])[0]
            cnt = np.bincount(A["fl_tr"][A["C"].fine[A["tr"]] == f0], minlength=A["L"])
            check(A["modal"][f0] == min(A["T"]["leaves"][j] for j in np.flatnonzero(cnt == cnt.max())), "modal leaf = TRAIN flatLeaf plurality, ties to the smaller id")
            # sensitivity, descriptive arms, omitted, items
            check("SENSITIVITY (R10" in txt and "DESCRIPTIVE M-AN:" in txt and "DESCRIPTIVE M-AF-s2:" in txt and "DESCRIPTIVE M-AF-g:" in txt, "sensitivity and descriptive rows printed")
            check(all(("%s:" % fid) in txt for fid in ("F-S1a", "F-S1b", "F-S1c", "F-S1d", "F-S1e")), "every falsifier line printed")
            check(txt.count("PREDICTION ") >= 28, "every prediction scored (%d lines)" % txt.count("PREDICTION "))
            check("GATE CONSTANTS (fixed before any EVAL read)" in txt and txt.index("GATE CONSTANTS") < txt.index("T-C1 massive"), "GATE constants precede every EVAL statistic")
            check(all(R["gate"][n]["accept"]["accepted"] for n in R["gate"]), "every fixture arm's descent is ACCEPTED (its diagnostics are the port's own)")
            check(R["arms"]["M-AF-s2"]["T-C1"]["n"] == m["T-C1"]["n"], "M-AF-s2 is read on the SAME EVAL (B1 ruling)")
            check(any(f_[0].startswith("M-AF-s2") for f_ in FIT_LOG) and all(SS.EVAL not in f_[3] for f_ in FIT_LOG), "TRAIN-ONLY audit: no EVAL fit")
            # D-5 MY-3 / MY-8: a leaf with no flatLeaf TRAIN label (simulated on the label maps) counts WRONG under descent and flatLeaf
            dl0 = Descent(A["T"]).top1(A["X"][ev])
            top_leaf = max(set(p_ for p_ in dl0 if p_), key=dl0.count)
            j_top = A["T"]["leaves"].index(top_leaf)
            A3 = dict(A, leaf_fine=[None if j_ == j_top else v_ for j_, v_ in enumerate(A["leaf_fine"])],
                      leaf_coarse=[None if j_ == j_top else v_ for j_, v_ in enumerate(A["leaf_coarse"])])
            r83 = t_c8(A3)
            labf3 = dict(zip(A3["T"]["leaves"], A3["leaf_fine"]))
            ok3 = np.mean([p_ is not None and labf3.get(p_) is not None and labf3[p_] == A3["C"].fine[i] for p_, i in zip(dl0, ev)])
            check(abs(r83["P_descent"] - ok3) < 1e-12 and r83["P_descent"] < m["T-C8"]["P_descent"], "MY-3: a descent leaf without a TRAIN label counts wrong")
            r1b3 = t_c1b(A3)
            fl3 = np.argmax(A3["X"][ev] @ A3["T"]["leaf_mu"].T, axis=1)
            pt3 = np.mean([A3["leaf_coarse"][j_] is not None and A3["leaf_coarse"][j_] == A3["C"].coarse[i] for j_, i in zip(fl3, ev)])
            check(abs(r1b3["p_tree"] - pt3) < 1e-12 and r1b3["p_tree"] < m["T-C1b"]["p_tree"], "MY-8: T-C1b counts a no-TRAIN leaf wrong")
            # independent recomputations of the other deciding values
            fl_ev = np.argmax(A["X"][ev] @ A["T"]["leaf_mu"].T, axis=1)
            lc = A["leaf_coarse"]
            p_tree = np.mean([lc[j] is not None and lc[j] == A["C"].coarse[i] for j, i in zip(fl_ev, ev)])
            check(abs(m["T-C1b"]["p_tree"] - p_tree) < 1e-12 and m["T-C1b"]["D"] != 0.0, "T-C1b P_tree recomputed (TRAIN-majority COARSE, flatLeaf); D13' non-zero on the fixture")
            oi = np.array([i for i, _t, _c in W["variants"]])
            Xv = S0.unit(np.vstack([W["vecs"]["qwen3"][t][:A["T"]["d"]] for _i, t, _c in W["variants"]]).astype(np.float64))
            st = (np.argmax(A["X"][oi] @ A["T"]["leaf_mu"].T, 1) == np.argmax(Xv @ A["T"]["leaf_mu"].T, 1)).astype(float)
            skm = np.mean([np.mean(S0.assign(A["X"][oi], Cm) == S0.assign(Xv, Cm)) for Cm in A["km"]])
            check(abs(s7["S_tree"] - st.mean()) < 1e-12 and abs(s7["D"] - (st.mean() - skm)) < 1e-12, "T-C7 S(tree) and D7 recomputed (mean over 20 seeds)")
            mo = margins(A["X"][oi], A["T"]["leaf_mu"])
            ab = mo < g["thr_tree"]
            check(abs(s9["D9"] - ((1 - st)[ab].mean() - (1 - st)[~ab].mean())) < 1e-12, "T-C9 D9 = flip(abstained) - flip(kept)")
            d9 = [((1 - st) * w_ * ab).sum() / (w_ * ab).sum() - ((1 - st) * w_ * ~ab).sum() / (w_ * ~ab).sum()
                  for w_ in S0.comp_weights(A["C"].comp[oi], BOOT_B, np.random.default_rng(SEED_BOOT + OFF["T-C9"]))]
            d9 = [v_ for v_ in d9 if np.isfinite(v_)]
            check(abs(s9["lo"] - np.percentile(d9, 2.5)) < 1e-12 and abs(s9["hi"] - np.percentile(d9, 97.5)) < 1e-12, "T-C9 CI recomputed (abstained minus kept)")
            leaf_ids = [A["T"]["leaves"][j] for j in fl_ev]
            dpt = dendrogram_purity(A["T"]["tparent"], A["T"]["leaves"], leaf_ids, A["C"].coarse[ev].tolist())
            check(abs(t2["dp_tree"] - dpt) < 1e-12, "T-C2 DP(tree) recomputed on EVAL, coarse gold")
            rng_h = np.random.default_rng(SEED_BOOT + OFF["RANDOM_H"])
            rnd = [dendrogram_purity(random_parent(A["T"]["leaves"], rng_h), A["T"]["leaves"], leaf_ids, A["C"].coarse[ev].tolist()) for _ in range(20)]
            check(abs(t2["random_p95"] - np.percentile(rnd, 95)) < 1e-12 and t2["above_random_p95"] == (t2["dp_tree"] > np.percentile(rnd, 95)), "random-hierarchy p95")
            ints = sorted(A["modal"])
            K = len(ints)
            cm = np.zeros((K, K))
            for (a_, b_), v_ in t4["pairs"].items():
                cm[ints.index(a_), ints.index(b_)] = cm[ints.index(b_), ints.index(a_)] = v_
            dm = np.array([[lca_dist(A["T"]["tparent"], A["modal"][a_], A["modal"][b_]) for b_ in ints] for a_ in ints], dtype=float)
            iu = np.triu_indices(K, 1)
            check(abs(t4["r"] - np.corrcoef(cm[iu], -dm[iu])[0, 1]) < 1e-12 and t4["n_perm"] == 200, "T-C4 r = Pearson(count, -distance); the p uses the given permutation count")
            # the descent knobs are read from the settings: descentMargin -1 stops every query at the root -> UNROUTED, counted wrong
            g_bad = json.loads(json.dumps(graphs["M-AF"]))
            T_bad = tree_of(g_bad, {"membershipFloor": 0.25, "routingBeamGamma": 0.2, "descentMargin": -1.0, "maxLeafAssignments": 5, "dagMode": "DAG_MAX"})
            A_bad = dict(A, T=T_bad, descent=Descent(T_bad))
            r8b = t_c8(A_bad)
            dlb = Descent(T_bad).top1(A["X"][ev])
            labf = dict(zip(A["T"]["leaves"], A["leaf_fine"]))
            okb = np.mean([p_ is not None and labf.get(p_) == A["C"].fine[i] for p_, i in zip(dlb, ev)])
            check(r8b["unrouted"] == sum(1 for p_ in dlb if p_ is None) > len(ev) // 4 and abs(r8b["P_descent"] - okb) < 1e-12
                  and r8b["P_descent"] < m["T-C8"]["P_descent"], "UNROUTED counts wrong (descentMargin read from settings; %d unrouted)" % r8b["unrouted"])
            # M-AF-s2's TRAIN differs from M-AF's (salt 2 re-draw), EVAL identical
            s2 = arms["M-AF-s2"]
            check(set(s2["tr"]) != set(A["tr"]) and set(eval_rows(s2)) == set(ev), "salt 2: TRAIN re-drawn, EVAL fixed")
        if "ST-RENDER" in sel:
            # every verdict / falsifier / positive-branch print branch, on synthetic result dicts derived from the fixture's R
            import copy
            base = copy.deepcopy(R)

            def with_(fn):
                R2 = copy.deepcopy(base)
                fn(R2)
                R2["verdicts"] = verdicts(R2)
                return "\n".join(render(R2, meta)), R2["verdicts"]

            def set_tc1(R2, corp, eq, loss):
                x = R2["arms"][AF_OF[corp]]["T-C1"]
                x.update(eq=eq, loss=loss, gain=False, verdict=" / ".join((["EQUIVALENT"] if eq else []) + (["LOSS-FLAGGED" if eq else "LOSS"] if loss else [])) or "UNDETERMINED")

            def set_tc7(R2, eq, loss):
                R2["arms"]["M-AF"]["T-C7"].update(eq=eq, loss=loss, gain=False, verdict="EQUIVALENT" if eq else ("LOSS" if loss else "UNDETERMINED"))
            t, VV = with_(lambda R2: (set_tc1(R2, "massive", True, False), set_tc1(R2, "clinc", True, False), set_tc7(R2, True, False)))
            check(VV["positive"] and ("POSITIVE BRANCH: the record may write \"%s\"" % POSITIVE_SENTENCE) in t, "positive branch printed when all three EQUIVALENT")
            t, VV = with_(lambda R2: (set_tc1(R2, "massive", True, True), set_tc1(R2, "clinc", True, False), set_tc7(R2, True, False)))
            check((not VV["positive"]) and "WITHHELD (a LOSS fired jointly with EQUIVALENT (N1 bracket" in t, "N1: a joined LOSS blocks the sentence (T-C1)")
            t, VV = with_(lambda R2: (set_tc1(R2, "massive", True, False), set_tc1(R2, "clinc", True, False), set_tc7(R2, True, True)))
            check((not VV["positive"]) and "N1 bracket" in t, "N1: a joined LOSS blocks the sentence (T-C7)")
            t, VV = with_(lambda R2: (set_tc1(R2, "massive", True, False), set_tc1(R2, "clinc", False, False), set_tc7(R2, True, False)))
            check((not VV["positive"]) and "did not all hold" in t, "positive branch withheld when one corpus is not EQUIVALENT")
            t, VV = with_(lambda R2: (set_tc1(R2, "massive", False, True), set_tc1(R2, "clinc", False, True)))
            check(VV["F-S1a"] and "F-S1a: FIRED" in t, "F-S1a fires on LOSS on both")
            t, VV = with_(lambda R2: (set_tc1(R2, "massive", False, True), set_tc1(R2, "clinc", False, False)))
            check((not VV["F-S1a"]) and "F-S1a: NOT FIRED" in t and VV["T-C1_loss_either"], "F-S1a needs both; LOSS on either counted for P2")
            t, VV = with_(lambda R2: (set_tc1(R2, "massive", True, True), set_tc1(R2, "clinc", True, True)))
            check(VV["F-S1a"] and VV["T-C1_eq_both"], "a joined outcome counts for both clauses (R11)")

            def tc1b(R2, vm, vc):
                R2["arms"]["M-AF"]["T-C1b"]["verdict"], R2["arms"]["C-AF"]["T-C1b"]["verdict"] = vm, vc
            t, VV = with_(lambda R2: tc1b(R2, "FAILED", "FAILED"))
            check(VV["F-S1b"] and "F-S1b: FIRED" in t, "F-S1b fires on FAILED on both")
            t, VV = with_(lambda R2: tc1b(R2, "FAILED", "UNDETERMINED"))
            check((not VV["F-S1b"]) and "F-S1b: NOT FIRED" in t, "F-S1b needs both")

            def tc9(R2, lo, hi):
                R2["arms"]["M-AF"]["T-C9"].update(lo=lo, hi=hi, verdict=ci_verdict(lo, hi))
            t, VV = with_(lambda R2: tc9(R2, -0.1, -0.01))
            check(VV["F-S1c"] and "F-S1c: FIRED" in t and "-> FAILED [SCOREABLE]" in t, "F-S1c fires on T-C9 FAILED")
            t, VV = with_(lambda R2: tc9(R2, 0.1, 0.3))
            check((not VV["F-S1c"]) and "F-S1c: NOT FIRED" in t, "F-S1c not fired on HELD")

            def tc8(R2, vm, vc):
                R2["arms"]["M-AF"]["T-C8"]["verdict"], R2["arms"]["C-AF"]["T-C8"]["verdict"] = vm, vc
            t, VV = with_(lambda R2: tc8(R2, "HELD", "FAILED"))
            check(VV["F-S1d"] and "F-S1d: FIRED" in t and "T-C8 (both corpora): FAILED" in t, "F-S1d fires on FAILED on either (CLINC)")
            t, VV = with_(lambda R2: tc8(R2, "FAILED", "HELD"))
            check(VV["F-S1d"], "F-S1d fires on FAILED on either (MASSIVE)")
            t, VV = with_(lambda R2: tc8(R2, "HELD", "HELD"))
            check((not VV["F-S1d"]) and "T-C8 (both corpora): HELD" in t, "T-C8 HELD on both")

            def tc4(R2, pm, pc):
                R2["arms"]["M-AF"]["T-C4"]["p"], R2["arms"]["C-AF"]["T-C4"]["p"] = pm, pc
            t, VV = with_(lambda R2: tc4(R2, 0.01, 0.01))
            check("T-C4 (both corpora): HELD" in t and "[DESCRIPTIVE-ONLY, N2]" in t, "T-C4 HELD line; MASSIVE descriptive label")
            t, VV = with_(lambda R2: tc4(R2, 0.2, 0.3))
            check("T-C4 (both corpora): FAILED" in t, "T-C4 FAILED line")
            t, VV = with_(lambda R2: tc4(R2, 0.01, 0.3))
            check("T-C4 (both corpora): UNDETERMINED" in t, "T-C4 mixed line")
            # P0 failure stops the lane: only P0 / F-S1e / P0-P printed
            R3 = copy.deepcopy(base)
            R3["P0"]["holds"], R3["stopped"] = False, True
            t3 = "\n".join(render(R3, meta))
            check("F-S1e: FIRED" in t3 and "NO OTHER READOUT IS SCORED" in t3 and "T-C1 massive" not in t3 and "PREDICTION P0-P" in t3 and "Brier 0.8100" in t3,
                  "P0 failure: the lane stops; P0-P scored FAILED")
            # omitted gemma arm
            R4 = copy.deepcopy(base)
            R4["omitted"] = ["M-AF-g"]
            R4["arms"].pop("M-AF-g", None)
            t4 = "\n".join(render(R4, meta))
            check("ARM M-AF-g: OMITTED (a stated precondition" in t4 and "DESCRIPTIVE M-AF-g" not in t4, "M-AF-g omission line")
            # prediction values: the printed band verdict for P2
            t5, _ = with_(lambda R2: R2["arms"]["M-AF"]["T-C1"].update(D=-0.025))
            check("PREDICTION P2 D1 massive: -0.02500 in [-0.025, +0.015] -> HELD" in t5, "P2 lower endpoint inclusive")
            t6, _ = with_(lambda R2: R2["arms"]["M-AF"]["T-C1"].update(D=-0.0251))
            check("PREDICTION P2 D1 massive: -0.02510 in [-0.025, +0.015] -> FAILED" in t6, "P2 outside the band")
        if "ST-REFUSE" in sel:
            W, trees, graphs, diags = fixture
            # the descent acceptance refuses a deciding arm below 99.9% (one GATE top-1 flipped in M-AF's diagnostics)
            bad = os.path.join(td, "bad_diag.txt")
            eng = parse_diagnostics(diags["M-AF"])
            ks = list(eng)
            flipped = dict(eng)
            other = [l for l in trees["M-AF"][0]["leaves"] if l != eng[ks[0]]][0]
            flipped[ks[0]] = other
            _write_diag(bad, list(flipped), [flipped[k] for k in flipped])
            dp = dict(diags, **{"M-AF": bad})
            refused(lambda: compute(W, trees, graphs, diag_paths=dp, n_perm=10, n_random=2), "< 99.9%: the port refuses")
            # ... but a descriptive (anchored) arm prints NOT ACCEPTED instead
            dq = dict(diags, **{"M-AN": bad})
            with contextlib.redirect_stdout(io.StringIO()):
                R5, _a = compute(W, trees, graphs, diag_paths=dq, n_perm=10, n_random=2)
            check(R5["arms"]["M-AN"]["T-C8"] is None and not R5["gate"]["M-AN"]["accept"]["accepted"], "a descriptive arm's NOT ACCEPTED descent is not printed")
            check(accepted(999, 1000) and not accepted(998, 1000) and not accepted(995, 1000) and not accepted(0, 0), "the 99.9% bar")
            # salt arms: a salted side that moved an EVAL row REFUSES (the withdrawn reading, simulated)
            saved_ss = EX.salted_side
            try:
                EX.salted_side = lambda sk, salt, s1=None: SS.side_of_hash(SS.side_hash(sk, "norm-v1\u001fsalt%d" % salt))
                refused(lambda: arm_sides(W["CS"]["massive"], 2), "moved an EVAL row")
            finally:
                EX.salted_side = saved_ss
            # diagnostics missing a GATE text -> not accepted
            short = os.path.join(td, "short_diag.txt")
            _write_diag(short, ks[1:], [eng[k] for k in ks[1:]])
            refused(lambda: compute(W, trees, graphs, diag_paths=dict(diags, **{"C-AF": short if False else diags["C-AF"], "M-AF": short}),
                                    n_perm=10, n_random=2), "the port refuses")
            # EVAL before the GATE freeze refuses
            STATE["gate_frozen"] = False
            A = make_arm(W, "M-AF", *trees["M-AF"])
            refused(lambda: eval_rows(A), "before the GATE constants were fixed")
            # fit guard
            refused(lambda: fit_idx(A["C"], A["side"], np.nonzero(A["side"] == SS.EVAL)[0][:3], (SS.TRAIN,), "x"), "TRAIN-ONLY")
            Cc = W["CS"]["clinc"]
            refused(lambda: fit_idx(Cc, Cc.side, np.nonzero(Cc.oos)[0][:2], (SS.EVAL, SS.TRAIN), "x"), "TRAIN-ONLY")
            # P0 differs when one node's queryIds set differs
            g2 = json.loads(json.dumps(graphs["M-AF"]))
            leaf = next(n for n in g2["nodes"] if n["queryIds"])
            leaf["queryIds"] = leaf["queryIds"][1:]
            check(not p0(graphs["M-AF"], g2)["holds"] and p0(graphs["M-AF"], g2)["members_differ"] == 1, "P0 fails on one node's membership")
            g3 = json.loads(json.dumps(graphs["M-AF"]))
            leaf = next(n for n in g3["nodes"] if len(n["queryIds"]) > 1)
            leaf["queryIds"] = list(reversed(leaf["queryIds"]))
            check(p0(graphs["M-AF"], g3)["holds"], "P0 compares queryIds as SETS (order excluded)")
            g6 = json.loads(json.dumps(graphs["M-AF"]))
            inner = next(n for n in g6["nodes"] if n["childIds"])
            inner["queryIds"] = list(inner.get("queryIds") or []) + ["q_residual0000000"]
            check(not p0(graphs["M-AF"], g6)["holds"], "D-5 MY-5: P0 compares internal nodes' queryIds too (residual members under DAG_MAX)")
            g4 = json.loads(json.dumps(graphs["M-AF"]))
            g4["nodes"] = g4["nodes"][:-1] + [dict(g4["nodes"][-1], id="n99999999")]
            check(not p0(graphs["M-AF"], g4)["holds"] and not p0(graphs["M-AF"], g4)["ids_equal"], "P0 fails on differing node-id sets")
            g5 = json.loads(json.dumps(graphs["M-AF"]))
            g5["nodes"][0]["vmfKappa"] = 1.2345
            check(p0(graphs["M-AF"], g5)["holds"] and p0(graphs["M-AF"], g5)["printed"]["vmfKappa"] == "differs", "kappa printed, never deciding")
            # P0 failing inside compute() stops the lane: no other readout computed
            with contextlib.redirect_stdout(io.StringIO()):
                Rs, _ = compute(W, trees, dict(graphs, **{"M-AF'": g2}), diag_paths=diags, n_perm=10, n_random=2)
            check(Rs["stopped"] and Rs["arms"] == {} and "verdicts" not in Rs, "P0 failure stops the lane in compute()")
            # snapshot id: exactly one
            rd = os.path.join(td, "rd")
            os.makedirs(rd)
            open(os.path.join(rd, "headless_run.log"), "w").write("x Snapshot ID: a1\ny Snapshot ID: b2\n")
            check(snapshot_id_of(rd)[0] is None and "2 distinct" in snapshot_id_of(rd)[1], "two Snapshot IDs refuse")
            open(os.path.join(rd, "headless_run.log"), "w").write("x Snapshot ID: a1\ny Snapshot ID: a1\n")
            check(snapshot_id_of(rd)[0] == "a1", "a repeated single id is accepted")
            # snapshot row by id from snapshots.db (read-only), never the latest
            sdb = os.path.join(td, "snapshots.db")
            con = sqlite3.connect(sdb)
            con.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, timestamp TEXT, description TEXT, graph TEXT, metrics TEXT, settings TEXT)")
            con.execute("INSERT INTO snapshots VALUES ('a1', '2026-10-01', 'd', ?, '{}', ?)", (json.dumps({"rootId": "x1", "nodes": []}), json.dumps({"k": 1})))
            con.execute("INSERT INTO snapshots VALUES ('z9', '2026-10-09', 'd', ?, '{}', ?)", (json.dumps({"rootId": "x9", "nodes": []}), json.dumps({"k": 9})))
            con.commit()
            con.close()
            check(snapshot_row(sdb, "a1")[0]["rootId"] == "x1", "the row chosen BY ID, not the latest timestamp")
            refused(lambda: snapshot_row(sdb, "nope"), "is not in")
            open(sdb + "-wal", "wb").write(b"x")
            refused(lambda: snapshot_row(sdb, "a1"), "wal")
            os.remove(sdb + "-wal")
            # port parity entry point on a fixture build (temp snapshots.db row + temp embedding DB)
            prd = os.path.join(td, "pp", "seed_42")
            os.makedirs(os.path.join(prd, "validation"))
            open(os.path.join(prd, "headless_run.log"), "w").write("Snapshot ID: ppid\n")
            gpp, spp = graphs["M-AF"], {"membershipFloor": 0.25, "routingBeamGamma": 0.2, "descentMargin": 0.12, "maxLeafAssignments": 5, "dagMode": "DAG_MAX"}
            con = sqlite3.connect(sdb)
            con.execute("INSERT INTO snapshots VALUES ('ppid', '2026-10-02', 'd', ?, '{}', ?)", (json.dumps(gpp), json.dumps(spp)))
            con.commit()
            con.close()
            Tpp = tree_of(gpp, spp)
            Cm_ = W["CS"]["massive"]
            gtx = sorted({Cm_.text[i] for i in np.nonzero(Cm_.kept & (Cm_.side == SS.GATE))[0]})
            edb = os.path.join(td, "emb_pp.db")
            con = sqlite3.connect(edb)
            con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
            for t_ in gtx:
                con.execute("INSERT INTO embeddings VALUES (?, ?)", (t_, np.asarray(W["vecs"]["qwen3"][t_], dtype=">f4").tobytes()))
            con.commit()
            con.close()
            Xg = S0.unit(np.vstack([W["vecs"]["qwen3"][t_][:Tpp["d"]] for t_ in gtx]).astype(np.float64))
            tops = Descent(Tpp).top1(Xg)
            _write_diag(os.path.join(prd, "validation", "MAIN_routing_diagnostics.txt"), gtx, tops)
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                kk, nn = port_parity(prd, sdb, edb)
            check(kk == nn == len(gtx) and "ACCEPTED (>= 99.9%)" in buf.getvalue(), "port parity entry point: full agreement on its own diagnostics")
            tops2 = list(tops)
            tops2[0] = [l for l in Tpp["leaves"] if l != tops[0]][0]
            _write_diag(os.path.join(prd, "validation", "MAIN_routing_diagnostics.txt"), gtx, tops2)
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                kk, nn = port_parity(prd, sdb, edb)
            check(kk == nn - 1 and "NOT ACCEPTED" in buf.getvalue(), "port parity counts one disagreement")
            con = sqlite3.connect(edb)
            con.execute("DELETE FROM embeddings WHERE query = ?", (gtx[0],))
            con.commit()
            con.close()
            refused(lambda: port_parity(prd, sdb, edb), "parity is read on EVERY query")
            # dry-run / run refuse while builds are ABSENT, before any read
            empty_root = os.path.join(td, "emptyroot")
            os.makedirs(empty_root)
            refused(lambda: dry_run(snap_db=sdb, data_root=empty_root, skip_heavy=True), "builds ABSENT")
            refused(lambda: run(snap_db=sdb, data_root=empty_root, out_dir=os.path.join(td, "out"), skip_heavy=True), "builds ABSENT")
            # write-once: an existing outcome refuses before anything else
            od = os.path.join(td, "out2")
            os.makedirs(od)
            open(os.path.join(od, OUTCOME), "w").write("x")
            refused(lambda: run(snap_db=sdb, data_root=empty_root, out_dir=od, skip_heavy=True), "write-once")
            # census tolerance
            check(abs(CENSUS_TOL - 0.05) < 1e-15, "census tolerance 5%")
            # salt arms keep EVAL
            check(np.array_equal(arm_sides(W["CS"]["massive"], 2) == SS.EVAL, W["CS"]["massive"].side == SS.EVAL), "arm_sides keeps EVAL for salt 2")
    finally:
        if "saved_repro" in dir():
            REPRO_S0.clear()
            REPRO_S0.update(saved_repro)
        STATE["gate_frozen"], FIT_LOG[:] = saved[0], saved[1]
        import shutil
        shutil.rmtree(td, ignore_errors=True)
    if not quiet:
        print("%s SELFTEST OK: %d checks (%s)" % (TAG, n_ok[0], ", ".join(c for c in SELFTEST_CASES if c in sel)))
    return 0


# ================================================================================================ mutants
MUTANTS = (
    # READY_intent_s1 delta (B-1, B-2, D-4, D-5 MY-1/3/4/5/8)
    ("B-1 Mantel p fails open on a NaN r", "        return r, float(\"nan\")                 # READY_intent_s1 B-1", "        pass                 # READY_intent_s1 B-1", ("ST-STATS",)),
    ("B-1 verdict ignores a non-finite p", "    if not (np.isfinite(pm) and np.isfinite(pc)):\n", "    if False:\n", ("ST-STATS",)),
    ("B-2 k = L floor", "    floor = cofile_floor(A, S0.skmeans(X[tr60], K_FLOOR, 0), len(oi))\n", "    floor = cofile_floor(A, A[\"km\"][0], len(oi))\n", ("ST-E2E",)),
    ("MY-4 floor k-means seed 1", "    floor = cofile_floor(A, S0.skmeans(X[tr60], K_FLOOR, 0), len(oi))\n", "    floor = cofile_floor(A, S0.skmeans(X[tr60], K_FLOOR, 1), len(oi))\n", ("ST-E2E",)),
    ("B-2 reproduction check removed", "        if (round(ceiling, 3), round(floor, 3)) != want:\n", "        if False:\n", ("ST-E2E",)),
    ("MY-1 residual always on", "        self.residual = str(k[\"dagMode\"]) == \"DAG_MAX\"\n", "        self.residual = True\n", ("ST-DESCENT",)),
    ("MY-3 no-label descent leaf counted right", "    ok_d = np.array([p is not None and lab.get(p) is not None and lab[p] == A[\"C\"].fine[i] for p, i in zip(dl, ev)], dtype=np.float64)\n",
     "    ok_d = np.array([p is not None and (lab.get(p) is None or lab[p] == A[\"C\"].fine[i]) for p, i in zip(dl, ev)], dtype=np.float64)\n", ("ST-E2E",)),
    ("MY-8 T-C1b no-TRAIN leaf counted right", "    tree_ok = np.array([A[\"leaf_coarse\"][j] is not None and A[\"leaf_coarse\"][j] == C.coarse[i] for j, i in zip(fl, ev)], dtype=np.int64)\n",
     "    tree_ok = np.array([A[\"leaf_coarse\"][j] is None or A[\"leaf_coarse\"][j] == C.coarse[i] for j, i in zip(fl, ev)], dtype=np.int64)\n", ("ST-E2E",)),
    ("MY-5 P0 compares leaves only", "    diff_members = sorted(i for i in set(na) & set(nb) if set(na[i].get(\"queryIds\") or []) != set(nb[i].get(\"queryIds\") or []))\n",
     "    diff_members = sorted(i for i in set(na) & set(nb) if not na[i].get(\"childIds\") and set(na[i].get(\"queryIds\") or []) != set(nb[i].get(\"queryIds\") or []))\n", ("ST-REFUSE",)),
    ("D-4 port parity on a subset", "    if len(have) != len(texts):\n", "    if False:\n", ("ST-REFUSE",)),
    ("D-4 unparsed blocks admitted", "    if n != marks:\n", "    if False:\n", ("ST-DESCENT",)),
    # T-C1
    ("T-C1 D from seed 0 only", "    D = n_tree - float(np.mean(n_km))\n", "    D = n_tree - n_km[0]\n", ("ST-E2E",)),
    ("T-C1 SE_total without the seed term", "    se_total = math.sqrt(se_b ** 2 + float(np.var(dseed, ddof=1)) / len(SEEDS20))\n", "    se_total = se_b\n", ("ST-E2E",)),
    ("T-C1 spread_K over 20 seeds (not 0-4)", "    spread_K = float(max(n_km[:5]) - min(n_km[:5]))\n", "    spread_K = float(max(n_km) - min(n_km))\n", ("ST-E2E",)),
    ("T-C1 bar = MDE80 only", "    bar = max(mde, spread_K)\n", "    bar = mde\n", ("ST-E2E",)),
    ("T-C1 NMI on coarse gold", "    truth = S0.codes(C.fine[ev])\n    tree_p", "    truth = S0.codes(C.coarse[ev])\n    tree_p", ("ST-E2E",)),
    ("TOST at 1.96 SE", "Z90 = 1.6448536269514722\n", "Z90 = 1.959963984540054\n", ("ST-E2E",)),
    ("TOST boundary inclusive", "    eq = bool(delta > 0 and -delta < lo90 and hi90 < delta)\n", "    eq = bool(delta > 0 and -delta <= lo90 and hi90 <= delta)\n", ("ST-STATS",)),
    ("joined LOSS printed as plain LOSS", "([\"LOSS-FLAGGED\" if eq else \"LOSS\"] if loss else []) + ([\"GAIN-FLAGGED\"", "([\"LOSS\"] if loss else []) + ([\"GAIN-FLAGGED\"", ("ST-STATS",)),
    ("delta_c factor 0.5", "delta_c=0.25 * (nmi_sup - float(np.mean(nmi_km)))", "delta_c=0.5 * (nmi_sup - float(np.mean(nmi_km)))", ("ST-E2E",)),
    ("delta_c measured on TRAIN (not GATE)", "        tg = S0.codes(C.fine[ga])\n        nmi_sup = S0.nmi(tg, S0.codes(u[S0.assign(X[ga], G)]))\n        nmi_km = [S0.nmi(tg, S0.assign(X[ga], Cm)) for Cm in A[\"km\"]]\n",
     "        tg = S0.codes(C.fine[tr])\n        nmi_sup = S0.nmi(tg, S0.codes(u[S0.assign(X[tr], G)]))\n        nmi_km = [S0.nmi(tg, S0.assign(X[tr], Cm)) for Cm in A[\"km\"]]\n", ("ST-E2E",)),
    # T-C1b
    ("T-C1b leaf labels FINE (not coarse)", "    tree_ok = np.array([A[\"leaf_coarse\"][j] is not None and A[\"leaf_coarse\"][j] == C.coarse[i]", "    tree_ok = np.array([A[\"leaf_fine\"][j] is not None and A[\"leaf_fine\"][j] == C.coarse[i]", ("ST-E2E",)),
    ("T-C1b comparator KC_1", "    diff = tree_ok - kc_ok[0]\n", "    diff = tree_ok - kc_ok[1]\n", ("ST-E2E",)),
    ("T-C1b spread_KC forced 0", "    spread = float(max(p_kc) - min(p_kc))\n    diff", "    spread = 0.0\n    diff", ("ST-E2E",)),
    # T-C2
    ("T-C2 spread_o over two arms", "    for n in (\"M-AF\", \"M-o1\", \"M-o2\"):\n", "    for n in (\"M-AF\", \"M-o1\"):\n", ("ST-E2E",)),
    ("T-C2 HELD without the spread clause", "    if D2 > spread_o and lo > 0:\n", "    if lo > 0:\n", ("ST-STATS",)),
    ("T-C2 random floor at p50", "    p95 = float(np.percentile(rnd, 95)) if rnd else float(\"nan\")\n", "    p95 = float(np.percentile(rnd, 50)) if rnd else float(\"nan\")\n", ("ST-E2E",)),
    ("DP own pairs without the children's", "        own = pairs(v) - sum(pairs(cnt.get(c, np.zeros(K))) for c in kids.get(n, []))\n", "        own = pairs(v)\n", ("ST-HIER",)),
    ("LCA distance one side only", "    return pa[x] + k\n", "    return pa[x]\n", ("ST-HIER",)),
    # T-C7 / T-C9
    ("T-C7 delta factor 0.5", "    delta = 0.25 * (ceiling - floor)\n", "    delta = 0.5 * (ceiling - floor)\n", ("ST-E2E",)),
    ("T-C7 S_km from seed 0 only", "    D = S_t - float(np.mean(S_k))\n", "    D = S_t - S_k[0]\n", ("ST-E2E",)),
    ("T-C9 threshold GATE p80", "GATE_Q = 20.0\n", "GATE_Q = 80.0\n", ("ST-E2E",)),
    ("T-C9 groups swapped", "        return wmean(flip, wa) - wmean(flip, wk)\n", "        return wmean(flip, wk) - wmean(flip, wa)\n", ("ST-E2E",)),
    ("T-C9 point groups swapped", "    D9 = float(flip[ab].mean() - flip[~ab].mean())", "    D9 = float(flip[~ab].mean() - flip[ab].mean())", ("ST-E2E",)),
    ("T-C9 threshold from EVAL-side tree margins (TRAIN)", "    A[\"gate\"][\"thr_tree\"] = float(np.percentile(margins(X[ga], T[\"leaf_mu\"]), GATE_Q))\n",
     "    A[\"gate\"][\"thr_tree\"] = float(np.percentile(margins(X[tr], T[\"leaf_mu\"]), GATE_Q))\n", ("ST-E2E",)),
    # T-C8
    ("T-C8 descent read from flatLeaf", "    ok_d = np.array([p is not None and lab.get(p) is not None and lab[p] == A[\"C\"].fine[i] for p, i in zip(dl, ev)], dtype=np.float64)\n",
     "    ok_d = ok_f.copy()\n", ("ST-E2E",)),
    ("T-C8 UNROUTED counted right", "    ok_d = np.array([p is not None and lab.get(p) is not None and lab[p] == A[\"C\"].fine[i] for p, i in zip(dl, ev)], dtype=np.float64)\n",
     "    ok_d = np.array([p is None or (lab.get(p) is not None and lab[p] == A[\"C\"].fine[i]) for p, i in zip(dl, ev)], dtype=np.float64)\n", ("ST-E2E",)),
    ("T-C8 FAILED needs both corpora", "    if m == \"FAILED\" or c == \"FAILED\":\n", "    if m == \"FAILED\" and c == \"FAILED\":\n", ("ST-STATS",)),
    ("T-C8 HELD on either", "    if m == \"HELD\" and c == \"HELD\":\n", "    if m == \"HELD\" or c == \"HELD\":\n", ("ST-STATS",)),
    ("T-C8b massive - clinc", "    d = [b - a for a, b in zip(m[\"draws\"], c[\"draws\"])]\n    lo, hi = S0.pct_ci(d)\n    D = c[\"D\"] - m[\"D\"]\n",
     "    d = [a - b for a, b in zip(m[\"draws\"], c[\"draws\"])]\n    lo, hi = S0.pct_ci(d)\n    D = m[\"D\"] - c[\"D\"]\n", ("ST-E2E",)),
    ("ci verdict FAILED at upper < 0 (strict)", "    if hi <= 0:\n        return \"FAILED\"\n", "    if hi < 0:\n        return \"FAILED\"\n", ("ST-STATS",)),
    # T-C4
    ("T-C4 p <= 0.05", "    if pm < 0.05 and pc < 0.05:\n", "    if pm <= 0.05 and pc <= 0.05:\n", ("ST-STATS",)),
    ("Mantel two-sided", "        if np.isfinite(rp) and np.isfinite(r) and rp >= r:\n", "        if np.isfinite(rp) and np.isfinite(r) and abs(rp) >= abs(r):\n", ("ST-STATS",)),
    ("modal leaf ties to the largest id", "        modal[f] = min(leaves[j] for j in np.flatnonzero(cnt == top))\n", "        modal[f] = max(leaves[j] for j in np.flatnonzero(cnt == top))\n", ("ST-STATS",)),
    ("T-C4 sign: Pearson(count, +distance)", "    y = -dist[iu].astype(np.float64)\n", "    y = dist[iu].astype(np.float64)\n", ("ST-STATS",)),
    # descent port
    ("descent: each child's own kappa", "                w = cur + scores[i] - lse\n", "                w = cur + self.kappa[ks[i]] * dots[i] - lse\n", ("ST-DESCENT",)),
    ("descent: gate removed", "                if best_child < bar * parent_dot:\n", "                if False:\n", ("ST-DESCENT",)),
    ("descent: beam = every child", "            beam = [i for i in range(len(ks)) if dots[i] >= mx_d - self.gamma]\n", "            beam = list(range(len(ks)))\n", ("ST-DESCENT",)),
    ("descent: floor not applied", "        admitted = {n: v for n, v in norm.items() if v >= math.log(max(self.floor, 1e-300))}\n", "        admitted = dict(norm)\n", ("ST-DESCENT",)),
    ("descent: cap not applied", "        top = sorted(admitted.items(), key=lambda kv: -kv[1])[:self.cap]\n", "        top = sorted(admitted.items(), key=lambda kv: -kv[1])\n", ("ST-DESCENT",)),
    ("descent: shrinkage weights uniform", "        w = w / w.sum() if w.sum() > 0 else np.full(len(ks), 1.0 / len(ks))\n", "        w = np.full(len(ks), 1.0 / len(ks))\n", ("ST-DESCENT",)),
    ("descent: profiles filter removed", "            if T[\"has_train\"].get(n):\n                return n, mem\n", "            return n, mem\n", ("ST-DESCENT",)),
    ("descent: residual candidates off", "        if self.residual or not cand:\n", "        if not cand:\n", ("ST-DESCENT",)),
    ("acceptance bar 0.99", "ACCEPT = 0.999\n", "ACCEPT = 0.99\n", ("ST-REFUSE",)),
    ("acceptance bar > instead of >=", "    return bool(n > 0 and k / float(n) >= ACCEPT)\n", "    return bool(n > 0 and k / float(n) > ACCEPT)\n", ("ST-REFUSE",)),
    ("acceptance not required for deciding arms", "    if accept_required and not A[\"accept\"][\"accepted\"]:\n", "    if False:\n", ("ST-REFUSE",)),
    ("acceptance counts every text as agreeing", "    k = sum(1 for t, p in zip(texts, py) if eng[t] == p)\n", "    k = len(texts)\n", ("ST-REFUSE",)),
    # P0
    ("P0 queryIds compared as lists", "if set(na[i].get(\"queryIds\") or []) != set(nb[i].get(\"queryIds\") or []))", "if (na[i].get(\"queryIds\") or []) != (nb[i].get(\"queryIds\") or []))", ("ST-REFUSE",)),
    ("P0 node-id sets ignored", "    holds = bool(ids_eq and not diff_members)\n", "    holds = bool(not diff_members)\n", ("ST-REFUSE",)),
    ("P0 failure does not stop the lane", "        R[\"stopped\"] = True\n        return R, arms\n", "        R[\"stopped\"] = False\n", ("ST-REFUSE",)),
    ("snapshot row by latest timestamp", "\"SELECT graph, settings FROM snapshots WHERE id = ?\", (sid,)", "\"SELECT graph, settings FROM snapshots ORDER BY timestamp DESC LIMIT 1\", ()", ("ST-REFUSE",)),
    ("several Snapshot IDs admitted", "    if len(ids) != 1:\n", "    if len(ids) == 0:\n", ("ST-REFUSE",)),
    # hygiene
    ("GATE-before-EVAL guard removed", "    if side == SS.EVAL and not STATE[\"gate_frozen\"]:\n", "    if False:\n", ("ST-REFUSE",)),
    ("fit guard admits EVAL / OOS", "    if bad or n_oos or n_drop or SS.EVAL in sides:\n", "    if False:\n", ("ST-REFUSE",)),
    ("outcome not write-once", "        if os.path.lexists(p):\n            refuse(\"%s exists: the outcome is write-once\" % p)\n", "        pass\n", ("ST-REFUSE",)),
    ("absent builds admitted by --run", "    if absent:\n        refuse(\"builds ABSENT: %s\" % \", \".join(absent))\n", "    pass\n", ("ST-REFUSE",)),
    ("salt-2 arm EVAL check removed", "    if not np.array_equal(out == SS.EVAL, C.side == SS.EVAL):\n", "    if False:\n", ("ST-REFUSE",)),
    # verdict wiring and printing
    ("F-S1a fires on either", "    V[\"F-S1a\"] = V[\"T-C1_loss_both\"]\n", "    V[\"F-S1a\"] = V[\"T-C1_loss_either\"]\n", ("ST-RENDER",)),
    ("F-S1d needs FAILED on both", "    V[\"F-S1d\"] = V[\"T-C8\"] == \"FAILED\"\n", "    V[\"F-S1d\"] = m[\"T-C8\"][\"verdict\"] == \"FAILED\" and c[\"T-C8\"][\"verdict\"] == \"FAILED\"\n", ("ST-RENDER",)),
    ("positive branch ignores N1", "    V[\"positive\"] = bool(V[\"T-C1_eq_both\"] and m[\"T-C7\"][\"eq\"] and not joint_loss)\n", "    V[\"positive\"] = bool(V[\"T-C1_eq_both\"] and m[\"T-C7\"][\"eq\"])\n", ("ST-RENDER",)),
    ("prediction bands exclusive", "and np.isfinite(x) and lo <= x <= hi) else \"FAILED\"", "and np.isfinite(x) and lo < x < hi) else \"FAILED\"", ("ST-STATS",)),
    ("falsifier F-S1e line dropped", "                     (\"F-S1e\", \"P0 fails (the lane stops)\")):", "                     ):", ("ST-E2E",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read().replace("\r\n", "\n")
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="intent_s1_mut_")
    with contextlib.redirect_stdout(io.StringIO()):
        fx = build_fixture(td)
    killed = 0
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        ns = {"__name__": "intent_s1_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(head.replace(old, new), "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests), quiet=True, fixture=fx if not set(tests) <= {"ST-DESCENT", "ST-STATS", "ST-HIER"} else None)
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:100])
        killed += res.startswith("KILLED")
        print("  %-55s %s" % (name, res))
    import shutil
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="INTENT-TRANSFER-S1 readout (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--port-parity", metavar="RUN_DIR", help="an existing build's seed_42 dir: Python descent vs the engine's GATE top-1")
    ap.add_argument("--emb-db", default=None, help="--port-parity: the embedding DB the build read (read-only)")
    ap.add_argument("--db", default=None)
    ap.add_argument("--emb-dir", default=None)
    ap.add_argument("--snapshot-db", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run(snap_db=a.snapshot_db, db=a.db, emb_dir=a.emb_dir)
    if a.port_parity:
        if not a.emb_db:
            refuse("--port-parity needs --emb-db")
        check_heavy()
        port_parity(a.port_parity, a.snapshot_db or os.path.join(DATA_ROOT, "snapshots.db"), a.emb_db)
        return 0
    run(snap_db=a.snapshot_db, db=a.db, emb_dir=a.emb_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
