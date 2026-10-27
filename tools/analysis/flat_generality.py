"""FLAT-GENERALITY (docs/judge_v2_program.md L21646-L21678, "## Registered 2026-09-27 (before any code or call) - FLAT-GENERALITY",
registered at a357ef0, parent b9491bf, before any code; plan R-D; arm (a) = queue FLAT-MIX-ANCHORED). ZERO calls: no judge, no LLM,
no embedding call, no cap, no temperature, no call cache.

Question (the registration's): is the FLAT-MIX-MMLU loss (af_clean_s42 a measurably worse partition than a flat vMF mixture at the
same k) a property of one draw, or does it appear in the three existing anchor-free re-draws (af_s137, af_s2048, af_s42_o1), and
does the anchored tree o0_clean_s42 lose to a flat mixture at its own k = 84 or to a label-anchored flat arm V_A?

Launch sequence (the run-operator; zero calls; ONE single-threaded python process; a pool reader (rule 7): never inside a
construction or a W-window; after the data-steward's closure check on pd610c9a / p19d9f47 / p8a29 and the delta READY):
  python tools/analysis/flat_generality.py --selftest        # synthetic only; every print branch executed; FG-E2E runs this
                                                             # driver's --dry-run / --run / --analyze end to end on a replica
                                                             # data root in a temp dir (V_A with a TEST ruling, never shipped)
  python tools/analysis/flat_generality.py --mutants         # every check removed in turn; every mutant must be KILLED
  python tools/analysis/flat_generality.py --inertness       # SYNTHETIC: flat_mix_mmlu.py at its base blob c5cc7934 vs this
                                                             # build, run / analyze / dry-run / identity-check end to end on
                                                             # a replica data root in a temp dir; byte comparison, with an
                                                             # execution witness (leg B ran assemble_res and the k=None
                                                             # defaults) and a sensitivity control (a one-constant change of
                                                             # BOOT_SEED must change the outcome)
  python tools/analysis/flat_generality.py --dry-run         # pool lines first; per tree the pool, fit set, EVAL counts, twin
                                                             # groups, hygiene counts, anchors; pins; cost; NO measure
  python tools/analysis/flat_generality.py --identity-check  # THE DELTA READY's check (real data): af_clean_s42 through the
                                                             # parameterised path must print M1 0.727 [0.712, 0.741], M2 +12.785
  python tools/analysis/flat_generality.py --run [--tree NAME] [--max-chunks N]   # one arm-seed per chunk, write-once state
  python tools/analysis/flat_generality.py --analyze         # REFUSES unless every partition of every tree is present and the
                                                             # V_A rulings are made; outcome of record WRITE-ONCE (mode 'x')
  Set TAXOARENA_DATA_ROOT to the main checkout when running from a worktree.

The instrument (the registration: "flat_mix_mmlu.py PARAMETERISED (tree, fit set, held-out pool, embedding DB, K, DIM)"):
  tools/analysis/flat_mix_mmlu.py is imported, its blob VERIFIED on import (FLAT_MIX_PIN below), and its measure code is called
  with the new keyword parameters (fit_set(snapshot, fit_n), fit_partition(name, X, k, tree_kw), load_T(run, leaves, dim, name),
  measures(names, dim), paired(arm, refs), table_pins(snapshots, runs)); nothing of the measures is re-implemented here. M1-M4,
  arms V and K, the paired bootstrap (seed 20260926, stem_key twin groups whole) and spread_V exactly as FLAT-MIX-MMLU.
  EMBEDDING DB: only embeddings_cache.db (qwen3) is admissible until EMBEDDER-PLUMBING's vmfMu guard merges (the registration).

Trees (each read on ITS OWN EVAL set and fit set; no EVAL question enters any fit; labels only in M1, keys only in M2):
  af_s137      experiment_results/anchorfree/redraw/af_s137/seed_137, snapshot 20260918_041114, pool pd610c9ad05255f16 (3,448),
               79 leaves, fit 8,126 root texts
  af_s2048     .../af_s2048/seed_2048, snapshot 20260918_043908, pool p19d9f473b5a610a0 (3,446), 81 leaves, fit 8,130
  af_s42_o1    .../af_s42_o1/seed_42, snapshot 20260918_050715, pool p8a29d8f3ff75aa55 (3,437), 81 leaves, fit 8,133
               (membership-identical to af/seed_42: its draw is NOT independent of ANCHOR-FREE's tree; disclosed)
  o0_clean_s42 .../o0_clean_s42/seed_42, snapshot 20260918_040207, pool p2dca21ab5f4ef3ae (3,445), 84 leaves, fit 8,125;
               arm (a): O against V at k = 84 and against V_A
  af_clean_s42 the identity tree only (FLAT-MIX-MMLU's T; M1 0.727 [0.712, 0.741], M2 +12.785; P6)
  The fit counts are the engine-coder's census of 2026-09-27 (snapshot graphs read mode=ro&immutable=1, counts only; no
  statistic); the script ASSERTS each and REFUSES otherwise. The EVAL set of a tree is its snapshot's reserved_queries
  (judgeable), which must hash to the tree's pool id AND equal the dataset DB's reserved_pool rows for that id (pool_guard's
  two checks, with the snapshot as the id source; for p2dca also pool_guard.assert_pool_of_record). Split words (rule 12):
  af_clean_s42 / o0_clean_s42 content-closed under stem_key at norm-v1 on p2dca; the re-draws "id-disjoint only" until the
  data-steward's closure check passes (the outcome says "EVAL side", never "held-out", for them).

V_A (arm (a); the tree-construction-specialist's definition): within each of O's 14 depth-1 anchors a flat vMF mixture with O's
  per-anchor leaf count [11, 9, 5, 6, 5, 6, 3, 8, 5, 6, 7, 5, 5, 3] (asserted in O's depth-1 order), seeds 0-4 (seed s for every
  anchor's EM), fitted on the fit texts O files to that anchor; questions routed to an anchor by O's own filing, then to the
  nearest component. THREE READINGS ARE UNRULED and the script does not choose (VA_RULINGS is all None; --run skips the V_A
  fits and --analyze REFUSES until a PRE-DATA bracket rules them, as the registration requires of any change to V_A):
    fit_filing      O's snapshot graph files 379 of its 8,125 fit texts under TWO anchors (engine-coder's census; the
                    registration asserts "one anchor per text"): "graph-exclusive" (graph membership, the doubly-filed texts
                    excluded and counted) or "routed" (every fit text filed by the held-out rule below)
    heldout_anchor  "leaf_ancestor" (the depth-1 ancestor of O's flatLeaf leaf) or "d1_nearest" (the nearest depth-1 centroid)
    assign          "map" (the anchor mixture's MAP, V's rule) or "nearest" (the nearest component mean, the registration's word)
  M4 is NOT registered for V_A and is printed NA.
[DELTA 2026-09-27, the engine-coder, after READY 4f5e03d and ruling R3 (programme L21831-L21846, 3fdc5d2); insertion only,
the paragraph above stands as the builder's report] R3: V_A files by DECLARED LABEL: every question (fit, EVAL side and keyed)
goes to the anchor whose label equals its MMLU-Pro category (O's 14 anchor labels are the 14 categories; a label that maps to no
anchor REFUSES); within each anchor the flat mixture is fitted on the texts filed there and assignment is by NEAREST MEAN.
VA_RULINGS = (declared_label, declared_label, nearest); the other readings stay implemented. OWED, not ruled (R3): N1 (d) one EM
seed per anchor (the build uses seed s for every anchor, as before) and (e) P2 / P7 per re-draw, M4 NA for V_A, the census fit
sizes pinned. ARM (c) is built AS REGISTERED: on af_clean_s42's fit set at its own k 82, V_s (seeds 0-4) is fitted by EM, then
the fit texts are hard-assigned (MAP) and, until every component holds >= 55 fit members, the smallest component below 55
(ties: the lower index) is merged into the component whose mean direction has the largest cosine with its own (mean direction =
the normalised sum of the members' unit vectors; no EM refit; empty components are dropped first, counted); the merged partition
assigns by nearest mean; M4 by m4_refit. Partitions S0-S4 beside af_clean_s42's T, DESCRIPTIVE (T - S_s printed, no criterion).
The builder's readings of "merged into their nearest neighbour after convergence" are printed in the outcome for the registrar.
Rebased onto EMBEDDER-PLUMBING (RP08): flat_mix_mmlu.py re-pinned; FLAT-GENERALITY still admits only embeddings_cache.db (ruling
R2: no flag = the DB of record), so the vmfMu guard has no non-qwen3 read to guard here. READY 4f5e03d N3: RV1-RV9 are killed
by value-asserting checks (FG-E2E recomputes the paired V0 difference, spread_V_A over A0-A4, A0 - T, the discordance against V0
from the per-question arms; an injected fit/EVAL overlap makes run() REFUSE; a foreign script identity makes analyze() REFUSE;
the p2dca id-file cross-check refuses; the held-out-anchor and routed-filing rulings change the cells).
[DELTA 2026-09-29, the engine-coder, after delta READY fd6a349 B5-1 and the registrar's record of 2026-09-29 (e09e551: the
orchestrator's B5-1 ruling, rulings 11-12); insertion only, the paragraphs above stand as the builder's reports] B5-1: V_A
routes EVAL-side and keyed questions LABEL-FREE, by the nearest component mean across ALL anchors' components
(heldout_anchor = "all_components_nearest"; only assign = "nearest" is admitted with it); FIT filing stays declared_label (R3
narrowed to the fit set), and the TRAIN rows that label M1's cells are filed by declared label then nearest mean within the
anchor (va_cell_fn: the fit side is the matrix Qt only; no EVAL-side or keyed label can reach va_assign, the helper is not
given them). "declared_label" is no longer an admitted held-out reading (VA_CHOICES). Selftest FG-VA-ORACLE: on labels drawn AT
RANDOM, V_A's M1 through FM.m1_block with the shipped rulings is <= chance + 0.1, and the R3 reading on the same fixture is
>= 0.9 (the check discriminates). Ruling 11 (seed s in all 14 anchors) is what fit_va does. Ruling 12: M4 for V_A prints "NA
(not registered for arm a; V_A has no global mixture weights)"; P2 / P7 are per re-draw ("n of 3", no pooled verdict), as
built; the per-anchor fit sizes (declared-label filing, O's depth-1 order) are printed by --dry-run and --run, VA_FIT_SIZES
holds the registrar's pin, --run fits NO V_A partition while the pin is owed and REFUSES before any fit of the tree on a
mismatch.
[DELTA 2026-09-29 w0-delta3, the engine-coder, after delta-2 READY b2ad5ef C5-1 / C5-2; insertion only] C5-1: the random-label
check now runs THE PATH THE RUN TAKES. FG-E2E-RANDOM: a replica whose declared categories are drawn at random; run() fits the
anchored tree (pin from the run's own printed sizes), tree_measures() scores V_A; asserted every A_s M1 <= chance + 0.1 (0.3625
<= 0.3625 + 0.1 on the fixture), tree_measures' V_A hits / EVAL cells / cell majorities EQUAL an independent recomputation
(_va_recompute: no va_assign / va_cell_fn / anchor_index / m1_block / score_cells), and the R3 oracle on the same data >= 0.9
(1.0000; the leg can see a leak). FG-E2E also asserts the equality on the structured replica through analyze(). C5-2:
VA_FIT_SIZES = the steward's pin for o0_clean_s42 (8c2b846; sum 8,125), value-checked by FG-PIN. Mutants (each leg alone):
Y5-B (EVAL filed with its labels in tree_measures) KILLED by FG-E2E-RANDOM (M1 0.6950 > 0.4625) and by FG-E2E; Y5-C (lab_t
reversed) KILLED by both (recomputation); Y5-D (every matrix filed by its labels) KILLED by both; Y5-E (A0 scored for every
seed) KILLED by both; pin off by one / anchors reordered KILLED by FG-PIN. --mutants 40 of 40.
READOUTS (the registration's, verbatim in the render): D1 per re-draw C1_r / C2_r (a WIN) and L1_r (a LOSS; THE deciding rule;
  the seed-wise all-5-CIs rule printed as the registered secondary); D2 k = number of re-draws with L1_r fired; A1 (O vs V0 at
  k 84, M2, the L1 form); A2 (V_A0 vs O, M2, the win form); predictions P1-P7; falsifiers F1 (k = 0), F2 (A2 fires); SUPPORT
  (a)-(g) with the measured Kish m-bar, n_eff and the observed-discordance MDE beside the registered SE / MDE.
PINS: flat_mix_mmlu.table_pins over the six DB tables, the five snapshot rows and the five run dirs' dag_snapshots.jsonl, BEFORE
  and AFTER --run and --analyze (both printed); any change REFUSES. The connect guard is flat_mix_mmlu's (four DBs, mode=ro,
  immutable=1 added, a non-empty -wal / -journal refused).
Outputs: experiment_results/flat_generality/state/<tree>/{meta.json, part_*.json} (write-once);
         experiment_results/flat_generality/flat_generality_outcome.txt and flat_generality_arms.csv (--analyze only, write-once).
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy is imported (the author's cap: single-threaded)
    os.environ[_v] = "1"

import sys
import csv
import io
import json
import math
import time
import struct
import hashlib
import sqlite3
import argparse
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
import contextlib
import subprocess
import gc

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard  # noqa: E402

TAG = "[FLAT-GEN]"
REGISTRATION = "docs/judge_v2_program.md L21646-L21678 (registered at a357ef0, parent b9491bf)"
# [2026-09-29 EMB-TARGET2, insertion: the RP08 pin was blob cdb354f1 / sha256-lf16:4e5fec853e3ec463; re-pinned for flat_mix's
# C-ET-3 arm-copy gate (READY_emb_target 6202766), inert here: FLAT-GENERALITY reads only embeddings_cache.db]
FLAT_MIX_PIN = ("flat_mix_mmlu.py", "555ae3ac31b2f27ea040e4bb6a9b20be0eeeecd2", "b80cec50c2eef49d")  # re-pinned after EMB-TARGET2 C-ET-3 (was cdb354f1 after RP08)
FLAT_MIX_BASE_BLOB = "c5cc7934474c6de77c36fb755cb321736d6c3b71"     # the FLAT-MIX-MMLU instrument of record (the inertness base)


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _pins_of_bytes(data):
    data = data.replace(b"\r\n", b"\n")
    return dict(blob=hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest(),
                lf16=hashlib.sha256(data).hexdigest()[:16],
                crlf16=hashlib.sha256(data.replace(b"\n", b"\r\n")).hexdigest()[:16])


def _verify_flat_mix():
    with open(os.path.join(HERE, FLAT_MIX_PIN[0]), "rb") as f:
        got = _pins_of_bytes(f.read())
    if got["blob"] != FLAT_MIX_PIN[1] or got["lf16"] != FLAT_MIX_PIN[2]:
        refuse("pin mismatch on tools/analysis/%s: got blob:%s / sha256-lf16:%s, pinned blob:%s / sha256-lf16:%s"
               % (FLAT_MIX_PIN[0], got["blob"][:8], got["lf16"], FLAT_MIX_PIN[1][:8], FLAT_MIX_PIN[2]))


_verify_flat_mix()                            # the instrument is the pinned one, or nothing runs
import flat_mix_mmlu as FM                    # noqa: E402  (verifies its own imports; installs the connect guard)
import anchor_free_readout as AF              # noqa: E402
import free_tests_f4_f7 as F                  # noqa: E402
import split_side                             # noqa: E402

POOL_OF_RECORD = "p2dca21ab5f4ef3ae"
DIM = FM.DIM
SEEDS = FM.SEEDS
EMB_DB = "embeddings_cache.db"
EMB_DB_ADMISSIBLE = ("embeddings_cache.db",)  # until EMBEDDER-PLUMBING's Python vmfMu guard merges (the registration)
REDRAW_DIR = os.path.join("experiment_results", "anchorfree", "redraw")
REDRAWS = ("af_s137", "af_s2048", "af_s42_o1")
ANCHORED = "o0_clean_s42"
ID_ONLY = "id-disjoint only (the data-steward's CK-CLOSE closure check on this split is owed; W0 RP02)"
CLOSED = "content-closed under stem_key at norm-v1 on p2dca (FLAT-MIX-MMLU's hygiene; steward 9073a8a for af_clean_s42)"
O_ANCHOR_LEAVES = (11, 9, 5, 6, 5, 6, 3, 8, 5, 6, 7, 5, 5, 3)
TREES = {
    "af_s137": dict(arm="b", run=os.path.join(REDRAW_DIR, "af_s137", "seed_137"), snapshot="20260918_041114_Headless_Run_Auto_ge",
                    pool="pd610c9ad05255f16", eval_n=3448, leaves=79, fit_n=8126, split_word=ID_ONLY),
    "af_s2048": dict(arm="b", run=os.path.join(REDRAW_DIR, "af_s2048", "seed_2048"), snapshot="20260918_043908_Headless_Run_Auto_ge",
                     pool="p19d9f473b5a610a0", eval_n=3446, leaves=81, fit_n=8130, split_word=ID_ONLY),
    "af_s42_o1": dict(arm="b", run=os.path.join(REDRAW_DIR, "af_s42_o1", "seed_42"), snapshot="20260918_050715_Headless_Run_Auto_ge",
                      pool="p8a29d8f3ff75aa55", eval_n=3437, leaves=81, fit_n=8133, split_word=ID_ONLY),
    "o0_clean_s42": dict(arm="a", run=FM.O_RUN, snapshot="20260918_040207_Headless_Run_Auto_ge", pool=POOL_OF_RECORD, eval_n=3445,
                         leaves=84, fit_n=8125, split_word=CLOSED, anchors=O_ANCHOR_LEAVES),
}
IDENTITY = dict(run=FM.T_RUN, snapshot=FM.T_SNAPSHOT, pool=POOL_OF_RECORD, eval_n=3445, leaves=FM.T_LEAVES, fit_n=FM.FIT_N,
                split_word=CLOSED)
VA_RULINGS = dict(fit_filing="declared_label", heldout_anchor="all_components_nearest", assign="nearest")   # B5-1 (e09e551); R3 fit only
VA_CHOICES = dict(fit_filing=("graph-exclusive", "routed", "declared_label"),
                  heldout_anchor=("leaf_ancestor", "d1_nearest", "all_components_nearest"),
                  assign=("map", "nearest"))
VA_FIT_SIZES = {"o0_clean_s42": (944, 905, 587, 647, 504, 792, 267, 558, 656, 423, 542, 286, 666, 348)}
# ruling 12: tree -> per-anchor declared-label fit sizes (O's depth-1 order), the registrar's pin (READY_w0_delta2 C5-2; the
# data-steward's count at 8c2b846, docs/reviews/STEWARD_w0_preconditions.md; sum 8,125 = O's fit_n). --run asserts it.
SF_FLOOR = 55                                  # arm (c): components below 55 fit members are merged (the registration)
SF_TREE = "af_clean_s42"
SE_M1, SE_M2 = 0.00663, 0.357e-3              # REALISED in the FLAT-MIX-MMLU outcome, section 6 (the forward rule binds)
MDE_M1, MDE_M2 = 0.0186, 1.00e-3              # 2.80 x SE
OUT_DIR = os.path.join(ROOT, "experiment_results", "flat_generality")
STATE_DIR = os.path.join(OUT_DIR, "state")
OUTCOME = os.path.join(OUT_DIR, "flat_generality_outcome.txt")
ARMS_CSV = os.path.join(OUT_DIR, "flat_generality_arms.csv")
CHUNK_WALL_S = 240.0


def data_path(rel):
    return os.path.join(FM.DATA_ROOT, rel)


def script_pins():
    with open(os.path.abspath(__file__), "rb") as f:
        return _pins_of_bytes(f.read())


def names_of(tree, spec=None):
    spec = (sf_spec() if tree == SF_TREE else TREES[tree]) if spec is None else spec
    if spec["arm"] == "c":
        return ("T",) + tuple("S%d" % s for s in SEEDS)
    base = ("T",) + tuple("V%d" % s for s in SEEDS) + tuple("K%d" % s for s in SEEDS)
    return base + (tuple("A%d" % s for s in SEEDS) if spec["arm"] == "a" else ())


def sf_spec():
    """Arm (c)'s tree: af_clean_s42 (the identity tree), read at its own k."""
    return dict(IDENTITY, arm="c")


def all_snapshots():
    return tuple(TREES[t]["snapshot"] for t in TREES) + (IDENTITY["snapshot"],)


def all_runs():
    return tuple(TREES[t]["run"] for t in TREES) + (IDENTITY["run"],)


def pin_kw():
    return dict(snapshots=all_snapshots(), runs=all_runs())


def assert_emb_db(name=EMB_DB):
    if name not in EMB_DB_ADMISSIBLE:
        refuse("embedding DB %r is not admissible: only %s until EMBEDDER-PLUMBING's vmfMu guard merges (the registration)"
               % (name, EMB_DB_ADMISSIBLE))
    return name


# ------------------------------------------------------------------------------------------------ pools and corpora
def tree_pool(spec, snap_db=None, data_db=None):
    """-> (pool id, frozenset of judgeable EVAL ids). The snapshot's reserved_queries must hash to spec['pool'] and list
    spec['eval_n'] judgeable ids, and the dataset DB's reserved_pool rows for that id must hash to it and hold the same ids."""
    con = pool_guard.open_ro(snap_db or data_path("snapshots.db"))
    try:
        row = con.execute("SELECT reserved_queries FROM snapshots WHERE id = ?", (spec["snapshot"],)).fetchone()
    finally:
        con.close()
    if row is None or not row[0]:
        refuse("snapshot %s carries no reserved_queries" % spec["snapshot"])
    judg = pool_guard.judgeable(json.loads(row[0]))
    pid = pool_guard.compute_pool_id(judg)
    if pid != spec["pool"]:
        refuse("snapshot %s's reserved_queries hash to %s, not %s" % (spec["snapshot"], pid, spec["pool"]))
    n = sum(len(v) for v in judg.values())
    if n != spec["eval_n"]:
        refuse("pool %s lists %d judgeable ids, registered %d" % (pid, n, spec["eval_n"]))
    con = pool_guard.open_ro(data_db or data_path("mmlu_pro_dataset_cache_v2.db"))
    try:
        rows = pool_guard.pool_rows(con, pid)
    finally:
        con.close()
    if not rows or pool_guard.compute_pool_id(rows) != pid:
        refuse("the dataset DB's reserved_pool rows for %s are absent or do not hash to it" % pid)
    if {(k, q) for k, v in rows.items() for q in v} != {(k, q) for k, v in judg.items() for q in v}:
        refuse("the dataset DB's reserved_pool rows for %s differ from snapshot %s's reserved_queries" % (pid, spec["snapshot"]))
    return pid, frozenset(q for v in judg.values() for q in v)


@contextlib.contextmanager
def eval_ids_override(pool_id, ids):
    """anchor_free_readout.corpus reads pool_guard.eval_ids(pool_id) (the registry's id files); a re-draw's pool is not in the
    registry, so the verified snapshot ids are served for THAT pool id only, and the original is restored on exit."""
    orig = pool_guard.eval_ids

    def patched(pid):
        return ids if pid == pool_id else orig(pid)
    pool_guard.eval_ids = patched
    try:
        yield
    finally:
        pool_guard.eval_ids = orig


def corpus_for(spec, ids):
    if spec["pool"] == POOL_OF_RECORD and ids != pool_guard.eval_ids(POOL_OF_RECORD):
        refuse("the snapshot ids of a p2dca tree differ from the pool file's judgeable ids")
    with eval_ids_override(spec["pool"], ids):
        return AF.corpus(spec["pool"])


def load_tree(tree, spec):
    return FM.load_T("T", run=spec["run"], leaves=spec["leaves"], dim=DIM, name=tree)


def hygiene(fit_texts, eval_texts):
    """-> (exact, stem): fit texts equal to an EVAL text (REFUSED when > 0: no EVAL question enters any fit) and fit texts
    whose stem_key equals an EVAL text's (a count for the steward's closure check; decided there, not here)."""
    ev = set(eval_texts)
    exact = sum(1 for t in fit_texts if t in ev)
    if exact:
        refuse("%d fit texts are EVAL texts of the same tree (no EVAL question may enter any fit)" % exact)
    ek = set(split_side.stem_key(t) for t in ev)
    return exact, sum(1 for t in fit_texts if split_side.stem_key(t) in ek)


# ------------------------------------------------------------------------------------------------ V_A (arm (a))
def va_rulings(r=None):
    r = VA_RULINGS if r is None else r
    unruled = [k for k in ("fit_filing", "heldout_anchor", "assign") if r.get(k) is None]
    if unruled:
        refuse("V_A readings unruled: %s (choices %s); the registration requires a PRE-DATA bracket before the READY for any change "
               "to V_A; the script does not choose" % (", ".join(unruled), {k: VA_CHOICES[k] for k in unruled}))
    for k, v in r.items():
        if v not in VA_CHOICES[k]:
            refuse("V_A reading %s = %r is not one of %s" % (k, v, VA_CHOICES[k]))
    if r["heldout_anchor"] == "all_components_nearest" and r["assign"] != "nearest":
        refuse("V_A held-out routing all_components_nearest admits assign = nearest only (got %r; B5-1)" % r["assign"])
    return r


def check_anchors(tree, spec):
    got = [sum(1 for d in tree["leaf_d1"] if d == a) for a in tree["d1_ids"]]
    if tuple(got) != tuple(spec["anchors"]):
        refuse("O's per-anchor leaf counts %s (depth-1 order %s) != registered %s" % (got, tree["d1_ids"], list(spec["anchors"])))
    return got


def label_anchor_map(tree):
    """ruling R3: category (lower-case) -> anchor index; O's anchor labels must be distinct categories."""
    m = {}
    for i, a in enumerate(tree["d1_ids"]):
        lab = str(tree["label"][a]).strip().lower()
        if lab in m:
            refuse("two anchors carry the label %r" % lab)
        m[lab] = i
    return m


def anchor_index(tree, Q, rule, labels=None):
    """O's filing of a question to one of its depth-1 anchors (index in tree['d1_ids']). declared_label (ruling R3): the anchor
    whose label equals the question's MMLU-Pro category (labels: one category per row of Q)."""
    if rule == "declared_label":
        if labels is None or len(labels) != Q.shape[0]:
            refuse("declared-label filing needs one category per row (%s for %d rows)" % (None if labels is None else len(labels), Q.shape[0]))
        m = label_anchor_map(tree)
        bad = sorted(set(str(c).lower() for c in labels) - set(m))
        if bad:
            refuse("categories with no anchor of that label: %s (anchors %s)" % (bad[:5], sorted(m)))
        return np.array([m[str(c).lower()] for c in labels], dtype=int)
    if rule == "leaf_ancestor":
        pos = {d: i for i, d in enumerate(tree["d1_ids"])}
        leaf = np.argmax(Q @ tree["leaf_mu"].T, axis=1)
        return np.array([pos[tree["leaf_d1"][j]] for j in leaf], dtype=int)
    if rule == "d1_nearest":
        return np.argmax(Q @ tree["d1_mu"].T, axis=1)
    refuse("unknown held-out anchor rule %r" % rule)


def graph_anchor_sets(tree, byid, ids, text):
    """text -> the set of anchor indices whose snapshot-graph region holds one of its ids."""
    out = {}
    for i, a in enumerate(tree["d1_ids"]):
        for q in FM.region_query_ids(a, byid):
            if q in text:
                out.setdefault(text[q], set()).add(i)
    return out


def va_filing(tree, texts, X, sets, rulings, decl=None):
    """-> (anchor index per fit text, -1 = not filed; counts). graph-exclusive: the one anchor whose region holds it (texts in
    two or more anchors, or none, are excluded and counted); routed: the held-out rule applied to the fit text's embedding."""
    if rulings["fit_filing"] == "graph-exclusive":
        idx = np.array([next(iter(sets[t])) if len(sets.get(t, ())) == 1 else -1 for t in texts], dtype=int)
    elif rulings["fit_filing"] == "declared_label":
        if decl is None or any(t not in decl for t in texts):
            refuse("declared-label filing: %d fit texts have no declared category" % (len(texts) if decl is None else sum(1 for t in texts if t not in decl)))
        idx = anchor_index(tree, X, "declared_label", [decl[t] for t in texts])
    elif rulings["fit_filing"] == "routed" and rulings["heldout_anchor"] == "declared_label":
        idx = anchor_index(tree, X, "declared_label", None if decl is None else [decl.get(t) for t in texts])
    elif rulings["fit_filing"] == "routed":
        idx = anchor_index(tree, X, rulings["heldout_anchor"])
    else:
        refuse("unknown fit filing %r" % rulings["fit_filing"])
    multi = sum(1 for t in texts if len(sets.get(t, ())) > 1)
    none = sum(1 for t in texts if not sets.get(t))
    return idx, dict(filed=int((idx >= 0).sum()), excluded=int((idx < 0).sum()), multi=multi, none=none)


def fit_va(name, X, idx, tree, spec, rulings):
    t0 = time.process_time()
    seed = int(name[1:])
    anchors = []
    for i, (a, k_a) in enumerate(zip(tree["d1_ids"], spec["anchors"])):
        Xa = X[idx == i]
        if Xa.shape[0] <= k_a:
            refuse("V_A %s: anchor %s has %d filed fit texts for %d components" % (name, a, Xa.shape[0], k_a))
        r = FM.vmf_em(Xa, k_a, seed)
        anchors.append(dict(anchor=a, label=tree["label"][a], k=int(k_a), n=int(Xa.shape[0]), mu=r["mu"].tolist(),
                            kappa=r["kappa"].tolist(), pi=r["pi"].tolist(), iters=r["iters"], converged=r["converged"]))
    return dict(rule="anchored", partition=name, anchors=anchors, rulings=dict(rulings), n_excluded=int((idx < 0).sum()),
                iters=max(a["iters"] for a in anchors), converged=all(a["converged"] for a in anchors),
                cpu_s=time.process_time() - t0, script=script_pins())


def va_assign(body, tree, Q, rulings, labels=None, side="heldout"):
    """-> the V_A cell id of every row of Q. side "fit" (the TRAIN rows that label the cells) under fit_filing declared_label:
    the anchor of the row's category, then the anchor mixture's component. side "heldout" (EVAL side, keyed; B5-1): under
    all_components_nearest the nearest component mean across ALL anchors' components, label-free; otherwise O's anchor filing by
    the held-out rule, then the anchor mixture's component (MAP or nearest mean)."""
    if side not in ("fit", "heldout"):
        refuse("va_assign side %r" % side)
    if side == "fit" and rulings["fit_filing"] == "declared_label":
        a_idx = anchor_index(tree, Q, "declared_label", labels)
    elif rulings["heldout_anchor"] == "all_components_nearest":
        names = ["%s|%s_c%02d" % (body["partition"], A["anchor"], j) for A in body["anchors"] for j in range(len(A["mu"]))]
        MU = np.vstack([np.array(A["mu"]) for A in body["anchors"]])
        return [names[int(j)] for j in FM.nearest_assign(Q, MU)]
    else:
        a_idx = anchor_index(tree, Q, rulings["heldout_anchor"], labels)
    out = [None] * Q.shape[0]
    for i, A in enumerate(body["anchors"]):
        rows = np.flatnonzero(a_idx == i)
        if not rows.size:
            continue
        mu = np.array(A["mu"])
        if rulings["assign"] == "map":
            j = FM.map_assign(Q[rows], mu, np.array(A["kappa"]), np.array(A["pi"]))
        elif rulings["assign"] == "nearest":
            j = FM.nearest_assign(Q[rows], mu)
        else:
            refuse("unknown V_A assignment %r" % rulings["assign"])
        for r_, jj in zip(rows, j):
            out[r_] = "%s|%s_c%02d" % (body["partition"], A["anchor"], int(jj))
    return out


def va_cell_fn(body, tree, rulings, Qt, lab_t):
    """The assign function the M1 / M2 blocks call (B5-1): the matrix Qt (TRAIN rows) is filed on the fit side with its declared
    categories lab_t; every other matrix (EVAL side, keyed) is routed on the held-out side with NO labels (none are given here)."""
    return lambda Q: va_assign(body, tree, Q, rulings, lab_t if Q is Qt else None, side="fit" if Q is Qt else "heldout")


def va_fit_sizes(idx, tree):
    return tuple(int((idx == i).sum()) for i in range(len(tree["d1_ids"])))


# ------------------------------------------------------------------------------------------------ arm (c): the size-floor V
def size_floor_merge(X, labels, k, floor=SF_FLOOR):
    """-> (final label per fit row in 0..k'-1, merge log, dropped empty). Until every component holds >= floor members: the smallest
    component below the floor (ties: lower original index) is merged into the component whose mean direction (normalised sum of
    member unit vectors) has the largest cosine with its own. No refit."""
    members = {j: list(np.flatnonzero(labels == j)) for j in range(k)}
    empty = sorted(j for j, m in members.items() if not m)
    for j in empty:
        del members[j]
    log = []
    while len(members) > 1:
        small = sorted((len(m), j) for j, m in members.items() if len(m) < floor)
        if not small:
            break
        n_s, j = small[0]
        mean = lambda ids: X[ids].sum(axis=0) / max(np.linalg.norm(X[ids].sum(axis=0)), 1e-300)
        mj = mean(members[j])
        others = sorted(members)
        others.remove(j)
        cos = [(float(mean(members[o]) @ mj), -o) for o in others]
        best = -max(cos)[1]
        log.append((int(j), int(best), int(n_s)))
        members[best] = sorted(members[best] + members.pop(j))
    order = sorted(members)
    out = np.empty(X.shape[0], dtype=int)
    for new, j in enumerate(order):
        out[members[j]] = new
    return out, log, empty


def fit_size_floor(name, X, k, floor=SF_FLOOR):
    t0 = time.process_time()
    seed = int(name[1:])
    r = FM.vmf_em(X, k, seed)
    lab = FM.map_assign(X, r["mu"], r["kappa"], r["pi"])
    fin, log, empty = size_floor_merge(X, lab, k, floor)
    k2 = int(fin.max()) + 1
    centers = [list(X[fin == j].sum(axis=0) / np.linalg.norm(X[fin == j].sum(axis=0))) for j in range(k2)]
    return dict(rule="nearest", partition=name, centers=centers, k_em=int(k), k_after=k2, floor=int(floor), merges=log,
                empty_dropped=empty, sizes=[int((fin == j).sum()) for j in range(k2)], iters=r["iters"], converged=r["converged"],
                cpu_s=time.process_time() - t0, script=script_pins(), **FM.m4_refit(X, fin, k2))


# ------------------------------------------------------------------------------------------------ state
def ensure_meta(state_dir, tree, spec):
    body = json.dumps(dict(test="FLAT-GENERALITY", registration=REGISTRATION, tree=tree,
                           spec={k: (list(v) if isinstance(v, tuple) else v) for k, v in spec.items()},
                           script=script_pins(), flat_mix=FLAT_MIX_PIN[1], imports={k: v[0] for k, v in FM.IMPORT_PINS.items()},
                           k=spec["leaves"], seeds=SEEDS, dim=DIM, emb_db=assert_emb_db(), v=[FM.V_MAX_ITER, FM.V_TOL],
                           km=FM.K_MAX_ITER, boot=[FM.BOOT_B, FM.BOOT_SEED], va=dict(VA_RULINGS) if spec["arm"] == "a" else None,
                           threads={v: os.environ.get(v) for v in THREAD_VARS}), sort_keys=True)
    p = os.path.join(state_dir, "meta.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            if f.read() != body:
                refuse("%s differs from this script's meta; a new state directory is needed" % p)
    else:
        FM.write_once(p, body)


def tree_state(state_dir, tree):
    return FM.read_state(os.path.join(state_dir, tree))


def run(state_dir=STATE_DIR, only=None, max_chunks=None):
    header()
    before = FM.table_pins(**pin_kw())
    for k, v in before.items():
        print("[PIN before] %s %s" % (k, v))
    n = 0
    for tree, spec in list(TREES.items()) + [(SF_TREE, sf_spec())]:
        if only is not None and tree != only:
            continue
        sdir = os.path.join(state_dir, tree)
        ensure_meta(sdir, tree, spec)
        texts, g, ids, text = FM.fit_set(snapshot=spec["snapshot"], fit_n=spec["fit_n"])
        _, eval_ids = tree_pool(spec)
        train, heldout, _ = corpus_for(spec, eval_ids)
        decl = dict(train)
        hygiene(texts, [t for t, _ in heldout])          # REFUSES if an EVAL text of this tree is in its fit set
        X = FM.fit_matrix(texts, dim=DIM)
        done = FM.read_state(sdir)
        todo = [nm for nm in names_of(tree, spec) if nm not in done]
        va, va_why = None, None
        if any(nm[0] == "A" for nm in todo):
            try:
                rul = va_rulings()
            except SystemExit as e:
                rul, va_why = None, str(e).replace(TAG + " REFUSED: ", "")
            if rul is not None:
                otree = load_tree(tree, spec)
                check_anchors(otree, spec)
                idx, cnt = va_filing(otree, texts, X, graph_anchor_sets(otree, g["byid"], ids, text), rul, decl)
                print("%s %s: V_A filing %s: %s" % (TAG, tree, json.dumps(rul, sort_keys=True), cnt))
                sizes, pin = va_fit_sizes(idx, otree), VA_FIT_SIZES.get(tree)
                print("%s %s: V_A FIT SIZES (fit filing, O's depth-1 order): %s; pinned %s" % (TAG, tree, list(sizes),
                                                                                         "OWED" if pin is None else list(pin)))
                if pin is None:
                    va_why = "ruling 12: the per-anchor fit sizes are pinned by a registrar bracket before --run; pin OWED"
                elif tuple(pin) != sizes:
                    refuse("%s: V_A fit sizes %s != the pinned %s (ruling 12); nothing of this tree is fitted" % (tree, list(sizes), list(pin)))
                else:
                    va = (otree, idx, rul)
            if va is None:
                print("%s %s: V_A partitions NOT fitted (%s)" % (TAG, tree, va_why))
        for name in todo:
            if max_chunks is not None and n >= max_chunks:
                break
            t0 = time.perf_counter()
            if name[0] == "A":
                if va is None:
                    break
                body = fit_va(name, X, va[1], va[0], spec, va[2])
            elif name[0] == "S":
                body = fit_size_floor(name, X, spec["leaves"])
            else:
                body = FM.fit_partition(name, X, k=spec["leaves"], tree_kw=dict(run=spec["run"], leaves=spec["leaves"], dim=DIM, name=tree))
                body["instrument"] = body["script"]
                body["script"] = script_pins()
            body["wall_s"] = time.perf_counter() - t0
            FM.write_once(os.path.join(sdir, "part_%s.json" % name), json.dumps(body, sort_keys=True))
            n += 1
            print("%s %s partition %s fitted (%.1f s wall%s); no measure is printed by --run"
                  % (TAG, tree, name, body["wall_s"], "" if body["wall_s"] <= CHUNK_WALL_S else "; OVER the 4-min chunk budget"))
        print("%s %s: present %s" % (TAG, tree, ",".join(sorted(FM.read_state(sdir)))))
    print("%s %d partition(s) written this run" % (TAG, n))
    FM.check_pins_after(before, **pin_kw())
    return 0


# ------------------------------------------------------------------------------------------------ measures and readouts
def tree_measures(tree, spec, parts, keyed, veck):
    pid, ids = tree_pool(spec)
    train, heldout, cs = corpus_for(spec, ids)
    heldout_ids = sorted(ids)
    vec = AF.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    names = names_of(tree, spec)
    base = tuple(nm for nm in names if nm[0] != "A")
    arms = FM.measures(parts, train, heldout, heldout_ids, vec, keyed, veck, names=base, dim=DIM)
    if spec["arm"] == "a":
        rul = va_rulings()
        otree = load_tree(tree, spec)
        check_anchors(otree, spec)
        Qt, Qh = AF.sliced(vec, [t for t, _ in train], DIM), AF.sliced(vec, [t for t, _ in heldout], DIM)
        # ruling R3: every row's declared category (train / EVAL side from the corpus; keyed from eval_results), by the row order
        # of the matrix m1_block / m2_block pass (Qt, Qh, then m2_block's keyed matrix)
        lab_t = [c for _, c in train]          # B5-1: the TRAIN side only; EVAL-side and keyed rows are routed label-free
        for nm in names:
            if nm[0] != "A":
                continue
            b = parts[nm]
            fn = va_cell_fn(b, otree, rul, Qt, lab_t)
            sc, hits, kh = FM.m1_block(fn, Qt, Qh, train, heldout)
            m2 = FM.m2_block(fn, keyed, veck)
            arms[nm] = dict(m1=sc["acc"], m1_lo=sc["lo"], m1_hi=sc["hi"], hits=sc["hits"], sc=sc, per1=hits, m2=m2["mean"],
                            per2=m2["per_q"], m3=FM.m3_block(kh, heldout, heldout_ids), m4=None, per4=None,
                            m4_void="NA (not registered for arm a; V_A has no global mixture weights)", cells_h=kh)
    groups, G = FM.twin_groups([t for t, _ in heldout])
    LAST.setdefault("arms", {})[tree] = arms
    LAST.setdefault("groups", {})[tree] = (groups, G)
    return arms, groups, G, heldout


LAST = {}      # the last analyze()'s per-question arms and result (read by the selftest's value checks only)


def sf_readout(tree, spec, arms, groups, G):
    """arm (c), DESCRIPTIVE: T (af_clean_s42) against each size-floor partition S_s."""
    names = tuple("S%d" % s for s in SEEDS)
    return dict(tree=tree, n=len(groups), G=G, mbar=FM.kish_mbar(groups), leaves=spec["leaves"], n_keyed=len(arms["T"]["per2"]),
                paired=FM.paired(arms, None, groups, arm="T", refs=names),
                spread_S={m: FM.spread_opt([arms[a][m] for a in names]) for m in ("m1", "m2")},
                arms={a: {k: arms[a][k] for k in ("m1", "m1_lo", "m1_hi", "hits", "m2", "m3", "m4", "m4_void") if k in arms[a]} for a in arms})


def tree_readout(tree, spec, arms, groups, G):
    refs = tuple("V%d" % s for s in SEEDS) + ("K0",)
    out = dict(tree=tree, arm=spec["arm"], n=len(groups), G=G, mbar=FM.kish_mbar(groups), leaves=spec["leaves"], pool=spec["pool"],
               split_word=spec["split_word"], n_keyed=len(arms["T"]["per2"]),
               paired=FM.paired(arms, None, groups, arm="T", refs=refs),
               spread_V={m: FM.spread_opt([arms["V%d" % s][m] for s in SEEDS]) for m in ("m1", "m2", "m4")},
               spread_K={m: FM.spread_opt([arms["K%d" % s][m] for s in SEEDS]) for m in ("m1", "m2", "m4")},
               discordance=float(np.mean(arms["T"]["per1"] != arms["V0"]["per1"])),
               arms={a: {k: arms[a][k] for k in ("m1", "m1_lo", "m1_hi", "hits", "m2", "m3", "m4", "m4_void") if k in arms[a]} for a in arms})
    if spec["arm"] == "a":
        out["va"] = FM.paired(arms, None, groups, arm="A0", refs=("T", "V0"))
        out["spread_VA"] = {m: FM.spread_opt([arms["A%d" % s][m] for s in SEEDS]) for m in ("m1", "m2")}
    return out


def d1_verdict(r):
    p, sv = r["paired"]["V0"], r["spread_V"]
    l1_m1 = FM.loss(p["d1"], sv["m1"], p["d1_lo"], p["d1_hi"])
    l1_m2 = FM.loss(p["d2"], sv["m2"], p["d2_lo"], p["d2_hi"])
    return dict(c1=FM.criterion(p["d1"], sv["m1"], p["d1_lo"], p["d1_hi"]), c2=FM.criterion(p["d2"], sv["m2"], p["d2_lo"], p["d2_hi"]),
                l1_m1=l1_m1, l1_m2=l1_m2, l1=bool(l1_m1 or l1_m2),
                seed_m1=bool(all(r["paired"]["V%d" % s]["d1_hi"] < 0 for s in SEEDS)),
                seed_m2=bool(all(r["paired"]["V%d" % s]["d2_hi"] < 0 for s in SEEDS)))


def a_verdicts(r):
    p, sv = r["paired"]["V0"], r["spread_V"]
    a2 = r["va"]["T"]
    return dict(a1=FM.loss(p["d2"], sv["m2"], p["d2_lo"], p["d2_hi"]),
                a2=FM.criterion(a2["d2"], r["spread_VA"]["m2"], a2["d2_lo"], a2["d2_hi"]),
                p5=bool(r["arms"]["A0"]["m2"] >= r["arms"]["V0"]["m2"]))


def _sc(ok):
    return "HELD" if ok else "FAILED"


def fnum(x, f):
    return "NA" if x is None else f % x


def render(res):
    """res: the per-tree readouts, the identity and the info lines -> (lines, verdict). Every branch is executed by --selftest."""
    L = ["=== FLAT-GENERALITY outcome (%s; zero calls) ===" % REGISTRATION]
    L.extend(res.get("info", []))
    ident = res["identity"]
    ident_ok = bool(ident["m1"] == FM.RECORD_M1 and ident["m2"] == FM.RECORD_M2)
    L.append("IDENTITY (P6): af_clean_s42 through the parameterised path: M1 %s (recorded %s), M2 %s (recorded %s) -> %s"
             % (ident["m1"], FM.RECORD_M1, ident["m2"], FM.RECORD_M2, "REPRODUCED" if ident_ok else "MISMATCH (a READY defect)"))
    L.append("")
    L.append("PER TREE (M1 purity on the tree's own EVAL side [Wilson 95%], M2 F6 x1000 on the keyed questions, M3 split-half R(SB) at "
             "leaves, M4 EVAL-side mean ll in nats):")
    for tree in list(REDRAWS) + [ANCHORED]:
        r = res["trees"][tree]
        L.append("  [%s] pool %s (%s); EVAL side %d questions in %d stem_key twin groups (Kish mean size %.4f); k %d; keyed %d"
                 % (tree, r["pool"], r["split_word"], r["n"], r["G"], r["mbar"], r["leaves"], r["n_keyed"]))
        for a in names_of(tree):
            m = r["arms"][a]
            L.append("    %-3s M1 %.3f [%.3f, %.3f] (%d/%d) | M2 %+.3f | M3 %s | M4 %s"
                     % ("O" if (tree == ANCHORED and a == "T") else ("V_A" + a[1:] if a[0] == "A" else a), m["m1"], m["m1_lo"], m["m1_hi"],
                        m["hits"], r["n"], 1000 * m["m2"], fnum(m["m3"], "%.3f"), "%.4f" % m["m4"] if m["m4"] is not None else
                        (m.get("m4_void") or "M4 VOID (ruling O2)")))
        sv, sk = r["spread_V"], r["spread_K"]
        L.append("    spread_V: M1 %.4f, M2 %.3f x1e-3, M4 %s | spread_K: M1 %.4f, M2 %.3f x1e-3"
                 % (sv["m1"], 1000 * sv["m2"], fnum(sv["m4"], "%.4f"), sk["m1"], 1000 * sk["m2"]))
    L.append("")
    L.append("D1 (per re-draw r, against V0_r at the tree's own k; the POINT decides the spread leg and the INTERVAL the CI leg, one "
             "conjunctive clause each; L1_r is THE deciding rule):")
    ver = {}
    for tree in REDRAWS:
        r = res["trees"][tree]
        v = d1_verdict(r)
        ver[tree] = v
        p, sv = r["paired"]["V0"], r["spread_V"]
        L.append("  %s: C1_r M1(T) - M1(V0) = %+.4f [%+.4f, %+.4f], spread_V %.4f -> %s; C2_r M2 %+.3f [%+.3f, %+.3f] x1e-3, spread_V "
                 "%.3f x1e-3 -> %s" % (tree, p["d1"], p["d1_lo"], p["d1_hi"], sv["m1"], "WIN" if v["c1"] else "no win",
                                       1000 * p["d2"], 1000 * p["d2_lo"], 1000 * p["d2_hi"], 1000 * sv["m2"], "WIN" if v["c2"] else "no win"))
        L.append("    L1_r LOSS FLAG: %s (M1 loss %s, M2 loss %s)%s" % ("FIRES" if v["l1"] else "does not fire", "yes" if v["l1_m1"] else "no",
                 "yes" if v["l1_m2"] else "no", " | a WIN and a LOSS on the same tree: recorded JOINED, a mixed pattern, no sentence"
                 if v["l1"] and (v["c1"] or v["c2"]) else ""))
        L.append("    registered secondary (seed-wise: every one of the 5 CIs against V0-V4 excludes 0 on the negative side): M1 %s, M2 %s"
                 % ("yes" if v["seed_m1"] else "no", "yes" if v["seed_m2"] else "no"))
        k0 = r["paired"]["K0"]
        L.append("    BESIDE (reported only) against K0: M1 %+.4f [%+.4f, %+.4f], M2 %+.3f [%+.3f, %+.3f] x1e-3"
                 % (k0["d1"], k0["d1_lo"], k0["d1_hi"], 1000 * k0["d2"], 1000 * k0["d2_lo"], 1000 * k0["d2_hi"]))
        if p["d4"] is not None:
            L.append("    M4 (DESCRIPTIVE BY DESIGN): T - V0 = %+.4f nats [%+.4f, %+.4f]" % (p["d4"], p["d4_lo"], p["d4_hi"]))
        else:
            L.append("    M4 (DESCRIPTIVE BY DESIGN): T - V0 not computed (M4 VOID for T, ruling O2; D1 unaffected)")
    k = sum(1 for t in REDRAWS if ver[t]["l1"])
    L.append("D2: the loss appears in %d of 3 qwen3 re-draws (L1_r fired: %s)" % (k, ", ".join(t for t in REDRAWS if ver[t]["l1"]) or "none"))
    L.append("")
    r = res["trees"][ANCHORED]
    av = a_verdicts(r)
    p, sv, va = r["paired"]["V0"], r["spread_V"], r["va"]
    L.append("ARM (a) (O = o0_clean_s42, 84 leaves; M2 decides; M1 is label-advantaged for O and V_A and is printed only):")
    L.append("  A1 O vs V0 at k 84 (M2, the L1 form): M2(O) - M2(V0) = %+.3f [%+.3f, %+.3f] x1e-3, spread_V %.3f x1e-3 -> %s"
             % (1000 * p["d2"], 1000 * p["d2_lo"], 1000 * p["d2_hi"], 1000 * sv["m2"], "FIRES" if av["a1"] else "does not fire"))
    L.append("     M1 printed only: M1(O) - M1(V0) = %+.4f [%+.4f, %+.4f]" % (p["d1"], p["d1_lo"], p["d1_hi"]))
    L.append("  A2 V_A vs O (M2, the win form): M2(V_A0) - M2(O) = %+.3f [%+.3f, %+.3f] x1e-3, spread_V_A %.3f x1e-3 -> %s"
             % (1000 * va["T"]["d2"], 1000 * va["T"]["d2_lo"], 1000 * va["T"]["d2_hi"], 1000 * r["spread_VA"]["m2"],
                "FIRES" if av["a2"] else "does not fire"))
    L.append("     M1 printed only: M1(V_A0) - M1(O) = %+.4f [%+.4f, %+.4f]; V_A readings: %s"
             % (va["T"]["d1"], va["T"]["d1_lo"], va["T"]["d1_hi"], res.get("va_rulings", "as ruled")))
    L.append("  POST-HOC-SEEN (disclosed): O vs V0 at k = 82 read 0.770 / 0.770 and F6 +13.949 / +14.318 in FLAT-MIX-MMLU (reported only).")
    if res.get("sf") is not None:
        sf = res["sf"]
        L.append("")
        L.append("ARM (c) (DESCRIPTIVE): the size-floor V beside af_clean_s42 (k %d; EM seeds 0-4, then components below %d fit members "
                 "merged into their nearest neighbour; builder's readings: MAP hard assignment of the fit texts, the smallest "
                 "component first, the neighbour by the cosine of the mean directions, no refit, nearest-mean assignment):"
                 % (sf["leaves"], SF_FLOOR))
        for s_ in SEEDS:
            a = "S%d" % s_
            m, pr = sf["arms"][a], sf["paired"][a]
            part = res.get("sf_parts", {}).get(a, {})
            L.append("  %s: k after merging %s (merges %s, empty dropped %s) | M1 %.3f [%.3f, %.3f] | M2 %+.3f | T - %s: M1 %+.4f [%+.4f, "
                     "%+.4f], M2 %+.3f [%+.3f, %+.3f] x1e-3" % (a, part.get("k_after", "?"), len(part.get("merges", ())),
                                                               len(part.get("empty_dropped", ())), m["m1"], m["m1_lo"], m["m1_hi"],
                                                               1000 * m["m2"], a, pr["d1"], pr["d1_lo"], pr["d1_hi"], 1000 * pr["d2"],
                                                               1000 * pr["d2_lo"], 1000 * pr["d2_hi"]))
        L.append("  spread_S: M1 %.4f, M2 %.3f x1e-3 (no criterion; DESCRIPTIVE as registered)" % (sf["spread_S"]["m1"], 1000 * sf["spread_S"]["m2"]))
    L.append("")
    L.append("PREDICTIONS (unsourced priors, as registered):")
    L.append("  P1 k: 0 with 0.10, 1 with 0.30, 2 with 0.35, 3 with 0.25; observed k = %d (registered probability %.2f); \"L1 fires in >= 2 "
             "of 3\" (p 0.60) -> %s" % (k, {0: 0.10, 1: 0.30, 2: 0.35, 3: 0.25}[k], _sc(k >= 2)))
    for tree in REDRAWS:
        p_ = res["trees"][tree]["paired"]["V0"]
        L.append("  P2 %s: dM1 = -0.035, 80%% [-0.060, -0.010]: observed %+.4f -> %s; dM2 = -1.2e-3, 80%% [-2.2, -0.2] x1e-3: observed "
                 "%+.3f -> %s" % (tree, p_["d1"], _sc(-0.060 <= p_["d1"] <= -0.010), 1000 * p_["d2"], _sc(-2.2e-3 <= p_["d2"] <= -0.2e-3)))
    L.append("  P3 A1 does not fire (p 0.75): A1 %s -> %s; dM2 O - V0 = -0.3e-3, 80%% [-1.2, +0.6] x1e-3: observed %+.3f -> %s"
             % ("fired" if av["a1"] else "not fired", _sc(not av["a1"]), 1000 * p["d2"], _sc(-1.2e-3 <= p["d2"] <= 0.6e-3)))
    L.append("  P4 A2 does not fire (O ties V_A on M2) (p 0.65): A2 %s -> %s" % ("fired" if av["a2"] else "not fired", _sc(not av["a2"])))
    L.append("  P5 V_A0 >= V0 at k 84 on M2 at the point (p 0.60): V_A0 %+.3f, V0 %+.3f x1e-3 -> %s"
             % (1000 * r["arms"]["A0"]["m2"], 1000 * r["arms"]["V0"]["m2"], _sc(av["p5"])))
    L.append("  P6 the identity check reproduces af_clean_s42's M1 / M2 (p 0.95): -> %s" % _sc(ident_ok))
    for tree in REDRAWS:
        s1 = res["trees"][tree]["spread_V"]["m1"]
        L.append("  P7 %s: spread_V(M1) in [0.015, 0.045] (p 0.75): %.4f -> %s" % (tree, s1, _sc(0.015 <= s1 <= 0.045)))
    L.append("")
    if k == 0:
        L.append("FALSIFIER F1 FIRES (k = 0): FLAT's partition clause narrows to \"one draw (af_clean_s42)\": it overturns the generality "
                 "the framing would otherwise state, not the FLAT-MIX-MMLU number.")
    else:
        L.append("FALSIFIER F1 does not fire (k = %d)." % k)
    if av["a2"]:
        L.append("FALSIFIER F2 FIRES (A2 fired): the loss belongs to the construction even when anchored: it overturns the DESCRIPTIVE "
                 "qualifier \"the anchored control ties, reported only\" (FLAT-MIX-MMLU item 7) as the framing's reading.")
    else:
        L.append("FALSIFIER F2 does not fire (A2 not fired).")
    L.append("READING: \"the loss appears in %d of 3 qwen3 re-draws\"" % k)
    L.append("")
    L.append("SUPPORT:")
    L.append("  (a) denominators: M1 per tree its EVAL side (%s); M2 the keyed questions (%s); paired designs."
             % (", ".join("%s %d" % (t, res["trees"][t]["n"]) for t in list(REDRAWS) + [ANCHORED]),
                ", ".join("%s %d" % (t, res["trees"][t]["n_keyed"]) for t in list(REDRAWS) + [ANCHORED])))
    for tree in list(REDRAWS) + [ANCHORED]:
        r_ = res["trees"][tree]
        neff = r_["n"] / r_["mbar"]
        se_obs = math.sqrt(r_["discordance"] / neff) if neff > 0 else float("nan")
        L.append("  (b)-(e) %s: DEFF M1 <= %.4f (Kish m-bar of its own twin groups, measured), n_eff %.0f; SE M1 registered %.5f, from the "
                 "observed T-V0 discordance %.4f: %.5f (MDE80 %.4f); M2 SE registered %.3f x1e-3; MDE80 M1 %.4f, M2 %.2f x1e-3; "
                 "effective bars max(MDE, spread_V): M1 %.4f, M2 %.3f x1e-3"
                 % (tree, r_["mbar"], neff, SE_M1, r_["discordance"], se_obs, 2.80 * se_obs, 1000 * SE_M2, MDE_M1, 1000 * MDE_M2,
                    max(MDE_M1, r_["spread_V"]["m1"]), 1000 * max(MDE_M2, r_["spread_V"]["m2"])))
    L.append("  (f) VERDICT LINE: D1 / L1_r SCOREABLE for the predicted re-draw loss (margin 0.0045 on the registered bars, thin); A1 and "
             "A2 DESCRIPTIVE-ONLY (the predicted differences lie inside 1.00e-3); cross-draw readings DESCRIPTIVE.")
    L.append("  (g) STRUCTURAL LEG: the seed-spread leg does not shrink with n; a loss smaller than max(MDE, spread_V) is unreachable at "
             "any budget, so \"not fired\" is a registered live outcome, never read as parity.")
    return L, dict(k=k, d1=ver, a=av, identity=ident_ok)


def arms_csv_text(res):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["tree", "arm", "M1", "M1_lo", "M1_hi", "hits", "M2_x1000", "M3_R", "M4_nats", "iters", "converged"])
    for tree in list(REDRAWS) + [ANCHORED]:
        r = res["trees"][tree]
        for a in names_of(tree):
            m = r["arms"][a]
            part = res["parts"][tree][a]
            w.writerow([tree, a, repr(m["m1"]), repr(m["m1_lo"]), repr(m["m1_hi"]), m["hits"], repr(1000 * m["m2"]),
                        "" if m["m3"] is None else repr(m["m3"]), "NA" if m["m4"] is None else repr(m["m4"]), part.get("iters", ""),
                        part.get("converged", "")])
    if res.get("sf") is not None:
        for a in names_of(SF_TREE, dict(arm="c")):
            m, part = res["sf"]["arms"][a], res["sf_parts"][a]
            w.writerow([SF_TREE, a, repr(m["m1"]), repr(m["m1_lo"]), repr(m["m1_hi"]), m["hits"], repr(1000 * m["m2"]),
                        "" if m["m3"] is None else repr(m["m3"]), "NA" if m["m4"] is None else repr(m["m4"]), part.get("iters", ""),
                        part.get("converged", "")])
    return buf.getvalue()


def identity_values(keyed=None, veck=None):
    spec = IDENTITY
    tree = load_tree("af_clean_s42", spec)
    _, ids = tree_pool(spec)
    train, heldout, _ = corpus_for(spec, ids)
    vec = AF.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    keyed = F.keyed_questions() if keyed is None else keyed
    veck = F.embed_matrix(AF.EMB_DB, list(keyed[3].values()), DIM) if veck is None else veck
    return FM.identity(tree, train, heldout, vec, keyed, veck, dim=DIM)


def analyze(state_dir=STATE_DIR, outcome=OUTCOME, arms_csv=ARMS_CSV):
    header()
    for p in (outcome, arms_csv):
        if os.path.exists(p):
            refuse("%s exists: outcome files of record are WRITE-ONCE" % p)
    va_rulings()
    before = FM.table_pins(**pin_kw())
    for k, v in before.items():
        print("[PIN before] %s %s" % (k, v))
    parts = {}
    for tree, spec in TREES.items():
        ensure_meta(os.path.join(state_dir, tree), tree, spec)
        parts[tree] = tree_state(state_dir, tree)
        FM.require_all(parts[tree], names=names_of(tree))
        if {json.dumps(b["script"], sort_keys=True) for b in parts[tree].values()} != {json.dumps(script_pins(), sort_keys=True)}:
            refuse("%s: partitions were written by another script identity" % tree)
    sfs = sf_spec()
    ensure_meta(os.path.join(state_dir, SF_TREE), SF_TREE, sfs)
    sf_parts = tree_state(state_dir, SF_TREE)
    FM.require_all(sf_parts, names=names_of(SF_TREE, sfs))
    if {json.dumps(b["script"], sort_keys=True) for b in sf_parts.values()} != {json.dumps(script_pins(), sort_keys=True)}:
        refuse("%s: partitions were written by another script identity" % SF_TREE)
    keyed = F.keyed_questions()
    veck = F.embed_matrix(AF.EMB_DB, list(keyed[3].values()), DIM)
    LAST.clear()
    trees = {}
    for tree, spec in TREES.items():
        arms, groups, G, _ = tree_measures(tree, spec, parts[tree], keyed, veck)
        trees[tree] = tree_readout(tree, spec, arms, groups, G)
    arms_sf, groups_sf, G_sf, _ = tree_measures(SF_TREE, sfs, sf_parts, keyed, veck)
    res = dict(trees=trees, parts=parts, identity=identity_values(keyed, veck), va_rulings=json.dumps(VA_RULINGS, sort_keys=True),
               sf=sf_readout(SF_TREE, sfs, arms_sf, groups_sf, G_sf), sf_parts=sf_parts,
               info=["script tools/analysis/flat_generality.py %s; instrument tools/analysis/flat_mix_mmlu.py blob:%s / sha256-lf16:%s; "
                     "state %s" % (FM.fmt_pins(script_pins()), FLAT_MIX_PIN[1][:8], FLAT_MIX_PIN[2], state_dir),
                     "af_s42_o1 is on p8a29 and membership-identical to af/seed_42: its draw is not independent of ANCHOR-FREE's tree."])
    L, verdict = render(res)
    LAST["res"] = res
    txt = "\n".join(L) + "\n"
    FM.check_pins_after(before, **pin_kw())
    FM.write_once(outcome, txt)
    FM.write_once(arms_csv, arms_csv_text(res))
    print(txt)
    print("%s wrote %s and %s (write-once)" % (TAG, outcome, arms_csv))
    return 0


# ------------------------------------------------------------------------------------------------ header / dry-run / identity
def header():
    pid = pool_guard.assert_pool_of_record(POOL_OF_RECORD)
    print("pool %s (pool_guard.assert_pool_of_record: id file and reserved_pool rows agree; opened mode=ro&immutable=1): the pool "
          "of o0_clean_s42, af_clean_s42 (identity) and the keyed questions' unit" % pid)
    print("[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    print("[SCRIPT] tools/analysis/flat_generality.py %s" % FM.fmt_pins(script_pins()))
    print("[PIN] tools/analysis/flat_mix_mmlu.py %s (pinned on import; verified)" % FM.fmt_pins(FM.script_pins()))
    for f, (b, l) in FM.IMPORT_PINS.items():
        print("[PIN] tools/analysis/%s %s (flat_mix_mmlu's registered imports; verified)" % (f, FM.fmt_pins(FM.pins_of(os.path.join(HERE, f)))))
    print("[DATA] DATA_ROOT %s; embedding DB %s (admissible: %s)" % (FM.DATA_ROOT, assert_emb_db(), ", ".join(EMB_DB_ADMISSIBLE)))
    return pid


def dry_run():
    header()
    print("[MODE] --dry-run: pools, counts, pins and the plan only; NO measure (M1-M4), no fit, nothing written")
    t0 = time.perf_counter()
    pins = FM.table_pins(**pin_kw())
    for k, v in pins.items():
        print("[PIN table/row/file] %s %s" % (k, v))
    print("[PIN] %.1f s (taken before and after --run and --analyze)" % (time.perf_counter() - t0))
    for tree, spec in list(TREES.items()) + [("af_clean_s42 (identity)", IDENTITY)]:
        pid, ids = tree_pool(spec)
        train, heldout, cs = corpus_for(spec, ids)
        tr = load_tree(tree.split(" ")[0], spec)
        texts, g, fids, text = FM.fit_set(snapshot=spec["snapshot"], fit_n=spec["fit_n"])
        exact, stem = hygiene(texts, [t for t, _ in heldout])
        groups, G = FM.twin_groups([t for t, _ in heldout])
        sizes = np.bincount(groups)
        print("TREE %s: %s | %d leaves, %d depth-1, slice %d, manifest pool %s" % (tree, tr["name"], len(tr["leaves"]), len(tr["d1_ids"]),
              tr["dim"], tr["manifest"].get("reserved_pool_id", "?")))
        print("  POOL %s: snapshot %s reserved_queries hash to it, %d judgeable (registered %d); the dataset DB's reserved_pool rows "
              "agree; split word: %s" % (pid, spec["snapshot"], len(ids), spec["eval_n"], spec["split_word"]))
        print("  EVAL side %d questions (%d distinct texts); label (train) set %d texts; %d stem_key twin groups, %d with more than one "
              "question (holding %d); Kish mean group size %.4f (the M1 DEFF bound the registration asked the dry-run to print)"
              % (len(heldout), len(set(t for t, _ in heldout)), len(train), G, int((sizes > 1).sum()), int(sizes[sizes > 1].sum()),
                 FM.kish_mbar(groups)))
        print("  FIT SET: %d root texts (ASSERTED %d); fit texts equal to an EVAL text %d (asserted 0); fit texts sharing an EVAL "
              "text's stem_key %d (for the steward's closure check)" % (len(texts), spec["fit_n"], exact, stem))
        if spec.get("anchors"):
            got = check_anchors(tr, spec)
            sets = graph_anchor_sets(tr, g["byid"], fids, text)
            cnt = {}
            for t in texts:
                cnt[len(sets.get(t, ()))] = cnt.get(len(sets.get(t, ())), 0) + 1
            print("  ANCHORS (V_A): %s; per-anchor leaf counts %s (ASSERTED); fit texts by number of anchors whose graph region holds "
                  "them: %s" % (", ".join(tr["label"][a] for a in tr["d1_ids"]), got, ", ".join("%d anchor(s): %d" % kv for kv in sorted(cnt.items()))))
            try:
                rul = va_rulings()
                print("  V_A readings: %s" % json.dumps(VA_RULINGS, sort_keys=True))
                if rul["fit_filing"] == "declared_label":
                    idx, _c = va_filing(tr, texts, np.zeros((len(texts), 1)), sets, rul, dict(train))
                    pin = VA_FIT_SIZES.get(tree.split(" ")[0])
                    print("  V_A FIT SIZES (fit filing, O's depth-1 order): %s; pinned %s (ruling 12: the registrar pins these before --run)"
                          % (list(va_fit_sizes(idx, tr)), "OWED" if pin is None else list(pin)))
            except SystemExit as e:
                print("  V_A: %s" % str(e).replace(TAG + " REFUSED: ", ""))
    keyed = F.keyed_questions()
    print("KEYED (F6): %d questions, %d models" % (len(keyed[4]), len(keyed[0])))
    print("PLAN: per tree T, V0-V4 and K0-K4 at the tree's own k (79 / 81 / 81 / 84); o0_clean_s42 also V_A0-V_A4; one partition per "
          "chunk; V: EM max_iter %d, tol %g; K: spherical k-means, max_iter %d; bootstrap %d twin-group resamples (seed %d); F6 CI by "
          "boot_mean_ci (B %d, seed 42)" % (FM.V_MAX_ITER, FM.V_TOL, FM.K_MAX_ITER, FM.BOOT_B, FM.BOOT_SEED, F.B))
    rng = np.random.default_rng(1)
    Xs = FM.unit_rows(rng.standard_normal((8130, DIM)))
    t0 = time.process_time()
    FM.vmf_em(Xs, 84, 0, max_iter=5, tol=0.0)
    per_it = (time.process_time() - t0) / 5
    print("COST (SYNTHETIC timing, n 8130 x %d, k 84): EM %.3f s/iteration -> <= %.1f CPU-min for 20 V seeds at %d iterations (plus V_A, "
          "K and the readout functions); registered about 1 CPU-h" % (DIM, per_it, per_it * FM.V_MAX_ITER * 20 / 60, FM.V_MAX_ITER))
    print("%s dry-run complete: zero measures on real data, nothing written" % TAG)
    return 0


def identity_check():
    header()
    print("[MODE] --identity-check (the delta READY's check; real data; writes nothing)")
    got = identity_values()
    ok = got["m1"] == FM.RECORD_M1 and got["m2"] == FM.RECORD_M2
    print("IDENTITY: af_clean_s42 through the parameterised path (tree_pool, corpus_for, load_T(run, leaves, dim), identity(dim)): M1 %s "
          "(recorded %s), M2 %s (recorded %s) -> %s" % (got["m1"], FM.RECORD_M1, got["m2"], FM.RECORD_M2,
                                                       "REPRODUCED" if ok else "MISMATCH (a READY defect)"))
    return 0 if ok else 1


# ------------------------------------------------------------------------------------------------ selftest
def _synthetic_tree_readout(tree, arm="b", d1=0.0, ci1=(-0.01, 0.01), d2=0.0, ci2=(-0.3e-3, 0.3e-3), sv1=0.0305, sv2=0.822e-3,
                            seed_hi1=0.01, seed_hi2=0.3e-3, a2=0.0, ci_a2=(-0.3e-3, 0.3e-3), sva2=0.8e-3, va0m2=0.0141, v0m2=0.0140):
    arms = {a: dict(m1=0.73, m1_lo=0.71, m1_hi=0.75, hits=2500, m2=0.0140, m3=0.8, m4=-1.5, m4_void=None)
            for a in names_of(tree, dict(arm=arm))}
    arms["V0"]["m2"] = v0m2
    if arm == "a":
        for a in arms:
            if a[0] == "A":
                arms[a].update(m4=None, m4_void="NA (not registered for arm a; V_A has no global mixture weights)")
        arms["A0"]["m2"] = va0m2
    pv = {}
    for s in SEEDS:
        pv["V%d" % s] = dict(d1=d1, d1_lo=ci1[0], d1_hi=(ci1[1] if s == 0 else seed_hi1), d2=d2, d2_lo=ci2[0],
                             d2_hi=(ci2[1] if s == 0 else seed_hi2), d4=-0.2, d4_lo=-0.3, d4_hi=-0.1)
    pv["K0"] = dict(pv["V0"], d1=-d1 + 0.05, d1_lo=-ci1[1] + 0.05, d1_hi=-ci1[0] + 0.05, d2=-d2 + 2e-3, d2_lo=-ci2[1] + 2e-3,
                    d2_hi=-ci2[0] + 2e-3)                 # K0 differs from V0 (READY 4f5e03d RV1: the deciding reference is V0)
    r = dict(tree=tree, arm=arm, n=3448, G=3448, mbar=1.0, leaves=79, pool="pdeadbeef", split_word=ID_ONLY, n_keyed=10925,
             paired=pv, spread_V=dict(m1=sv1, m2=sv2, m4=0.01), spread_K=dict(m1=0.02, m2=0.5e-3, m4=0.01), discordance=0.2, arms=arms)
    if arm == "a":
        r["va"] = {"T": dict(d1=0.01, d1_lo=0.0, d1_hi=0.02, d2=a2, d2_lo=ci_a2[0], d2_hi=ci_a2[1], d4=None, d4_lo=None, d4_hi=None),
                   "V0": dict(d1=0.01, d1_lo=0.0, d1_hi=0.02, d2=0.0, d2_lo=-1e-4, d2_hi=1e-4, d4=None, d4_lo=None, d4_hi=None)}
        r["spread_VA"] = dict(m1=0.02, m2=sva2)
    return r


def _res(redraw_kw=None, anch_kw=None, ident=(None, None)):
    redraw_kw = redraw_kw or {}
    trees = {t: _synthetic_tree_readout(t, **redraw_kw.get(t, {})) for t in REDRAWS}
    trees[ANCHORED] = _synthetic_tree_readout(ANCHORED, arm="a", **(anch_kw or {}))
    sfa = {"S%d" % s: dict(m1=0.72, m1_lo=0.70, m1_hi=0.74, hits=2480, m2=0.0130, m3=0.8, m4=-1.6, m4_void=None) for s in SEEDS}
    sfp = {"S%d" % s: dict(d1=0.004, d1_lo=-0.01, d1_hi=0.02, d2=0.1e-3, d2_lo=-0.3e-3, d2_hi=0.5e-3, d4=None, d4_lo=None, d4_hi=None)
           for s in SEEDS}
    sf = dict(tree=SF_TREE, n=3445, G=3445, mbar=1.0, leaves=82, n_keyed=10925, paired=sfp, spread_S=dict(m1=0.01, m2=0.2e-3), arms=sfa)
    return dict(trees=trees, identity=dict(m1=ident[0] or FM.RECORD_M1, m2=ident[1] or FM.RECORD_M2), info=["synthetic"], sf=sf,
                sf_parts={a: dict(k_after=80, merges=[(1, 2, 40), (3, 4, 50)], empty_dropped=[]) for a in sfa})


LOSS = dict(d1=-0.04, ci1=(-0.06, -0.02))
LOSS_M2 = dict(d2=-1.5e-3, ci2=(-2.5e-3, -0.5e-3))
WIN = dict(d1=0.04, ci1=(0.02, 0.06))


def _line(t, key):
    return t.split(key)[1].split("\n")[0]


def st_render(chk):
    def txt(**kw):
        L, v = render(_res(**kw))
        return "\n".join(L), v
    t, v = txt()
    chk.ok(v["k"] == 0 and "D2: the loss appears in 0 of 3 qwen3 re-draws (L1_r fired: none)" in t and "FALSIFIER F1 FIRES (k = 0)" in t,
           "branch: no loss anywhere -> k 0, F1 FIRES")
    chk.ok("-> FAILED" in _line(t, "\"L1 fires in >= 2 of 3\"") and "registered probability 0.10" in t, "branch: P1 FAILED at k 0, prior 0.10 printed")
    chk.ok(all("does not fire" in _line(t, "%s: C1_r" % x) or "does not fire" in t.split("%s: C1_r" % x)[1].split("\n")[1] for x in REDRAWS),
           "branch: L1_r does not fire on each re-draw")
    chk.ok("A1 O vs V0" in t and "-> does not fire" in _line(t, "A1 O vs V0") and "-> does not fire" in _line(t, "A2 V_A vs O")
           and "FALSIFIER F2 does not fire" in t, "branch: A1 / A2 do not fire; F2 silent")
    chk.ok("-> HELD" in _line(t, "P3 A1") and "-> HELD" in _line(t, "P4 A2") and "-> HELD" in _line(t, "P5 V_A0") and "-> HELD" in _line(t, "P6 the identity"),
           "branch: P3 / P4 / P5 / P6 HELD")
    chk.ok(all("-> HELD" in _line(t, "P7 %s" % x) for x in REDRAWS) and all(_line(t, "P2 %s" % x).count("-> FAILED") == 2 for x in REDRAWS),
           "branch: P7 HELD per re-draw; P2 FAILED on both measures per re-draw (a tie is outside the predicted loss)")
    t, v = txt(redraw_kw={"af_s137": LOSS})
    chk.ok(v["k"] == 1 and "(L1_r fired: af_s137)" in t and "FALSIFIER F1 does not fire (k = 1)" in t and "registered probability 0.30" in t,
           "branch: one loss on M1 -> k 1; F1 silent")
    chk.ok("FIRES (M1 loss yes, M2 loss no)" in t.split("af_s137: C1_r")[1].split("\n")[1] and "-> HELD" in _line(t, "P2 af_s137").split(";")[0],
           "branch: L1_r on M1; P2 dM1 HELD")
    chk.ok("-> FAILED" in _line(t, "\"L1 fires in >= 2 of 3\""), "branch: P1 FAILED at k 1")
    chk.ok("M1 no, M2 no" in t.split("af_s137: C1_r")[1].split("\n")[2],
           "branch: the seed-wise secondary does not fire when only the V0 CI is negative (all 5 required)")
    t, v = txt(redraw_kw={"af_s137": LOSS, "af_s2048": LOSS_M2})
    chk.ok(v["k"] == 2 and "-> HELD" in _line(t, "\"L1 fires in >= 2 of 3\"") and "FIRES (M1 loss no, M2 loss yes)" in t.split("af_s2048: C1_r")[1].split("\n")[1],
           "branch: k 2 (one M2 loss) -> P1 HELD")
    chk.ok("-> HELD" in _line(t, "P2 af_s2048").split(";")[1], "branch: P2 dM2 HELD")
    t, v = txt(redraw_kw={t_: dict(LOSS, **LOSS_M2) for t_ in REDRAWS})
    chk.ok(v["k"] == 3 and "registered probability 0.25" in t and "D2: the loss appears in 3 of 3" in t and "READING: \"the loss appears in 3 of 3 qwen3 re-draws\"" in t,
           "branch: k 3; the reading words carry k")
    t, v = txt(redraw_kw={"af_s137": dict(d1=-0.04, ci1=(-0.06, 0.001))})
    chk.ok(v["k"] == 0, "branch: a loss beyond the spread whose CI reaches 0 does not fire L1_r (the CI leg)")
    t, v = txt(redraw_kw={"af_s137": dict(d1=-0.02, ci1=(-0.03, -0.01))})
    chk.ok(v["k"] == 0 and "-> HELD" in _line(t, "P2 af_s137").split(";")[0], "branch: a negative CI inside the seed spread does not fire L1_r (the spread leg)")
    t, v = txt(redraw_kw={"af_s137": WIN})
    chk.ok("-> WIN" in _line(t, "af_s137: C1_r") and v["k"] == 0 and "recorded JOINED" not in t, "branch: C1_r WIN alone")
    t, v = txt(redraw_kw={"af_s137": dict(d2=1.5e-3, ci2=(0.5e-3, 2.5e-3))})
    chk.ok("x1e-3 -> WIN" in _line(t, "af_s137: C1_r"), "branch: C2_r WIN")
    t, v = txt(redraw_kw={"af_s137": dict(WIN, **LOSS_M2)})
    chk.ok(v["k"] == 1 and "recorded JOINED, a mixed pattern" in t, "branch: a WIN on M1 and a LOSS on M2 on one tree -> joined, counted in k")
    t, v = txt(redraw_kw={"af_s137": dict(LOSS, seed_hi1=-0.001)})
    chk.ok("M1 yes, M2 no" in t.split("af_s137: C1_r")[1].split("\n")[2], "branch: the seed-wise secondary fires on M1 (all 5 CIs negative)")
    t, v = txt(redraw_kw={"af_s137": dict(LOSS_M2, seed_hi2=-0.1e-3)})
    chk.ok("M1 no, M2 yes" in t.split("af_s137: C1_r")[1].split("\n")[2], "branch: the seed-wise secondary fires on M2")
    t, v = txt(redraw_kw={"af_s137": dict(sv1=0.05)})
    chk.ok("-> FAILED" in _line(t, "P7 af_s137"), "branch: P7 FAILED for one re-draw")
    t, v = txt(anch_kw=dict(d2=-1.5e-3, ci2=(-2.5e-3, -0.5e-3)))
    chk.ok(v["a"]["a1"] and "-> FIRES" in _line(t, "A1 O vs V0") and "-> FAILED" in _line(t, "P3 A1").split(";")[0]
           and "-> FAILED" in _line(t, "P3 A1").split(";")[1], "branch: A1 FIRES; P3 FAILED on both parts")
    t, v = txt(anch_kw=dict(a2=1.5e-3, ci_a2=(0.5e-3, 2.5e-3), va0m2=0.0155))
    chk.ok(v["a"]["a2"] and "-> FIRES" in _line(t, "A2 V_A vs O") and "FALSIFIER F2 FIRES" in t and "-> FAILED" in _line(t, "P4 A2"),
           "branch: A2 FIRES -> F2 FIRES, P4 FAILED")
    t, v = txt(anch_kw=dict(a2=1.5e-3, ci_a2=(-0.1e-3, 2.5e-3)))
    chk.ok(not v["a"]["a2"], "branch: A2 with a CI reaching 0 does not fire (the CI leg)")
    t, v = txt(anch_kw=dict(a2=0.5e-3, ci_a2=(0.1e-3, 0.9e-3)))
    chk.ok(not v["a"]["a2"], "branch: A2 inside spread_V_A does not fire (the spread leg)")
    t, v = txt(anch_kw=dict(va0m2=0.0130))
    chk.ok("-> FAILED" in _line(t, "P5 V_A0"), "branch: P5 FAILED")
    t, v = txt(ident=("0.726 [0.711, 0.740]", None))
    chk.ok("MISMATCH (a READY defect)" in t and "-> FAILED" in _line(t, "P6 the identity"), "branch: P6 FAILED on an identity mismatch (M1)")
    t, v = txt(ident=(None, "+12.786"))
    chk.ok("-> FAILED" in _line(t, "P6 the identity"), "branch: P6 FAILED on an identity mismatch (M2 alone)")
    r = _res()
    r["trees"]["af_s137"]["paired"]["V0"].update(d4=None, d4_lo=None, d4_hi=None)
    r["trees"]["af_s137"]["arms"]["T"].update(m4=None, m4_void="M4 VOID (ruling O2): synthetic")
    r["trees"]["af_s137"]["spread_V"]["m4"] = None
    L, v = render(r)
    t = "\n".join(L)
    chk.ok("T - V0 not computed (M4 VOID for T" in t and "M4 VOID (ruling O2): synthetic" in t and "M4 NA" in t, "branch: T's M4 VOID printed; D1 unaffected")
    chk.ok("O   M1" in t and "V_A0 M1" in t and "M4 NA (not registered for arm a; V_A has no global mixture weights)" in t, "branch: O and V_A labels; V_A M4 NA (ruling 12 wording)")
    chk.ok("DEFF M1 <= 1.0000" in t and "n_eff 3448" in t and "(MDE80 " in t and "effective bars max(MDE, spread_V): M1 0.0305" in t,
           "branch: the support readout prints m-bar, n_eff, the observed-discordance MDE and the effective bars")
    chk.ok("EVAL side" in t and "held-out" not in t.replace("held-out rule", ""), "branch: rule 12 words: 'EVAL side', never 'held-out' in the outcome")
    chk.ok("S3: k after merging 80 (merges 2, empty dropped 0)" in t and "T - S3: M1 +0.0040" in t and "spread_S: M1 0.0100" in t,
           "branch: arm (c) printed per seed (k after merging, merges, T - S_s) with its spread, DESCRIPTIVE")
    t, v = txt(redraw_kw={"af_s137": LOSS})
    chk.ok(v["d1"]["af_s137"]["l1"] and "BESIDE (reported only) against K0: M1 +0.0900" in t,
           "RV1: L1_r is decided against V0 (K0 here reads a WIN; the loss still fires)")


def _mk_db(path, ddl, rows):
    con = FM._RAW_CONNECT(path)
    for d in ddl:
        con.execute(d)
    for sql, rs in rows:
        con.executemany(sql, rs)
    con.commit()
    con.close()


def st_pool(chk):
    with tempfile.TemporaryDirectory() as td:
        snap = os.path.join(td, "snapshots.db")
        data = os.path.join(td, "mmlu_pro_dataset_cache_v2.db")
        res_ = {"math": [1, 2, 3, -1], "law": [7, 8]}
        judg = pool_guard.judgeable(res_)
        pid = pool_guard.compute_pool_id(judg)
        _mk_db(snap, ["CREATE TABLE snapshots (id TEXT, reserved_queries TEXT)"],
               [("INSERT INTO snapshots VALUES (?, ?)", [("s1", json.dumps(res_)), ("s2", json.dumps({"math": [1, 2, 3], "law": [9, 8]}))])])
        _mk_db(data, ["CREATE TABLE reserved_pool (pool_id TEXT, domain TEXT, question_id INTEGER)"],
               [("INSERT INTO reserved_pool VALUES (?, ?, ?)", [(pid, k, q) for k, v in judg.items() for q in v])])
        spec = dict(snapshot="s1", pool=pid, eval_n=5)
        got = tree_pool(spec, snap, data)
        chk.ok(got == (pid, frozenset([1, 2, 3, 7, 8])), "FG-POOL the snapshot ids (sentinel dropped) hash to the pool and match the DB rows")
        chk.ok(FM.expect_refusal(lambda: tree_pool(dict(spec, pool="p0000000000000000"), snap, data), "hash to"), "FG-POOL a wrong pool id REFUSES")
        chk.ok(FM.expect_refusal(lambda: tree_pool(dict(spec, eval_n=6), snap, data), "registered 6"), "FG-POOL a wrong judgeable count REFUSES")
        chk.ok(FM.expect_refusal(lambda: tree_pool(dict(spec, snapshot="s3"), snap, data), "no reserved_queries"), "FG-POOL an absent snapshot REFUSES")
        pid2 = pool_guard.compute_pool_id(pool_guard.judgeable({"math": [1, 2, 3], "law": [9, 8]}))
        chk.ok(FM.expect_refusal(lambda: tree_pool(dict(snapshot="s2", pool=pid2, eval_n=5), snap, data), "absent or do not hash"),
               "FG-POOL a pool without DB rows REFUSES")
    orig = pool_guard.eval_ids
    with eval_ids_override("pX", frozenset([5])):
        inside = pool_guard.eval_ids("pX")
    chk.ok(inside == frozenset([5]) and pool_guard.eval_ids is orig, "FG-POOL the eval_ids override serves one pool and is restored")
    chk.ok(FM.expect_refusal(lambda: assert_emb_db("embeddings_cache_bge.db"), "not admissible") and assert_emb_db() == "embeddings_cache.db",
           "FG-EMB only embeddings_cache.db is admissible")
    chk.ok(FM.expect_refusal(lambda: hygiene(["a", "b"], ["b", "c"]), "1 fit texts are EVAL texts") and hygiene(["What is x?"], ["what  is X?"]) == (0, 1),
           "FG-HYG an exact fit/EVAL overlap REFUSES; a stem_key collision is counted")


def _synthetic_o(rng, d=16):
    """A 3-anchor tree with leaf counts (2, 3, 2), unit centroids, and fit / query clouds around its leaves."""
    unit = FM.unit_rows
    A = unit(rng.standard_normal((3, d)) * 3)
    leaf_mu, leaf_d1 = [], []
    for i, n_l in enumerate((2, 3, 2)):
        for _ in range(n_l):
            leaf_mu.append(A[i] + 0.12 * rng.standard_normal(d))
            leaf_d1.append("a%d" % i)
    leaf_mu = unit(np.array(leaf_mu))
    tree = dict(leaf_mu=leaf_mu, leaf_d1=leaf_d1, leaf_ids=["l%d" % j for j in range(len(leaf_d1))], d1_ids=["a0", "a1", "a2"],
                d1_mu=A, label={"a0": "Zero", "a1": "One", "a2": "Two"}, dim=d)
    X = unit(np.repeat(leaf_mu, 60, axis=0) + 0.08 * rng.standard_normal((60 * len(leaf_d1), d)))
    return tree, X


def st_va(chk):
    rng = np.random.default_rng(91)
    tree, X = _synthetic_o(rng)
    spec = dict(anchors=(2, 3, 2))
    chk.ok(check_anchors(tree, spec) == [2, 3, 2] and FM.expect_refusal(lambda: check_anchors(tree, dict(anchors=(3, 2, 2))), "registered"),
           "FG-VA per-anchor leaf counts asserted in depth-1 order")
    chk.ok(FM.expect_refusal(lambda: va_rulings(dict(fit_filing=None, heldout_anchor="leaf_ancestor", assign="map")), "unruled")
           and FM.expect_refusal(lambda: va_rulings(dict(fit_filing="routed",
           heldout_anchor="leaf_ancestor", assign="soft")), "not one of"), "FG-VA the shipped rulings are unruled and REFUSE; an unknown reading REFUSES")
    la = anchor_index(tree, X, "leaf_ancestor")
    dn = anchor_index(tree, X, "d1_nearest")
    truth = np.repeat([0] * 2 + [1] * 3 + [2] * 2, 60)
    chk.ok(np.array_equal(la, truth) and float(np.mean(dn == truth)) > 0.9, "FG-VA anchor filing: leaf-ancestor exact on the fixture; nearest depth-1 close")
    texts = ["t%04d" % i for i in range(X.shape[0])]
    sets = {t: {int(truth[i])} for i, t in enumerate(texts)}
    sets[texts[0]] = {0, 1}
    del sets[texts[1]]
    ok_r = dict(fit_filing="graph-exclusive", heldout_anchor="leaf_ancestor", assign="map")
    idx, cnt = va_filing(tree, texts, X, sets, ok_r)
    chk.ok(idx[0] == -1 and idx[1] == -1 and cnt == dict(filed=len(texts) - 2, excluded=2, multi=1, none=1),
           "FG-VA graph-exclusive filing excludes and counts the doubly-filed and the unfiled texts")
    idx2, cnt2 = va_filing(tree, texts, X, sets, dict(ok_r, fit_filing="routed"))
    chk.ok(np.array_equal(idx2, la) and cnt2["excluded"] == 0 and cnt2["multi"] == 1, "FG-VA routed filing files every text by the held-out rule")
    body = fit_va("A0", X, idx2, tree, spec, dict(ok_r, fit_filing="routed"))
    chk.ok([a["k"] for a in body["anchors"]] == [2, 3, 2] and sum(a["n"] for a in body["anchors"]) == X.shape[0] and body["rule"] == "anchored",
           "FG-VA one mixture per anchor with that anchor's leaf count, fitted on its filed texts only")
    for assign in ("map", "nearest"):
        cells = va_assign(body, tree, X, dict(ok_r, assign=assign))
        anch = [c.split("|")[1].split("_c")[0] for c in cells]
        chk.ok(anch == ["a%d" % a for a in la] and len(set(cells)) == 7 and all(c.startswith("A0|") for c in cells),
               "FG-VA %s assignment: every question lands in a component of the anchor O files it to; 7 distinct cells" % assign)
    b1 = dict(body, anchors=[dict(a) for a in body["anchors"]])
    b1["anchors"][1] = dict(b1["anchors"][1], pi=[0.98, 0.01, 0.01], kappa=[5.0, 400.0, 400.0])
    cm = va_assign(b1, tree, X, dict(ok_r, assign="map"))
    cn = va_assign(b1, tree, X, dict(ok_r, assign="nearest"))
    chk.ok(cm != cn, "FG-VA MAP and nearest-mean differ when the anchor mixture's weights / concentrations differ (both readings live)")
    chk.ok(FM.expect_refusal(lambda: fit_va("A1", X[:10], np.zeros(10, dtype=int), tree, spec, ok_r), "filed fit texts"),
           "FG-VA an anchor with no more filed texts than components REFUSES")
    # ruling R3: declared-label filing and routing, on a fixture whose labels DISAGREE with the geometry for a known subset
    labs = ["zero", "one", "two"]
    decl_lab = [labs[(int(truth[i]) + (1 if i % 10 == 0 else 0)) % 3] for i in range(X.shape[0])]
    decl = dict(zip(texts, decl_lab))
    r3 = dict(fit_filing="declared_label", heldout_anchor="declared_label", assign="nearest")
    b51 = dict(fit_filing="declared_label", heldout_anchor="all_components_nearest", assign="nearest")
    chk.ok(va_rulings() == b51, "FG-VA the shipped rulings are B5-1's: declared_label (fit) / all_components_nearest / nearest")
    chk.ok(FM.expect_refusal(lambda: va_rulings(dict(b51, assign="map")), "admits assign = nearest only")
           and FM.expect_refusal(lambda: va_rulings(r3), "not one of"),
           "FG-VA all_components_nearest with MAP REFUSES; declared_label is no longer an admitted held-out reading")
    idx3, cnt3 = va_filing(tree, texts, X, sets, r3, decl)
    want = np.array([labs.index(c) for c in decl_lab])
    chk.ok(np.array_equal(idx3, want) and cnt3["excluded"] == 0 and int((idx3 != la).sum()) == int((np.arange(X.shape[0]) % 10 == 0).sum()),
           "FG-VA declared-label filing files every fit text to the anchor of its category (the relabelled tenth moves)")
    body3 = fit_va("A0", X, idx3, tree, spec, r3)
    cells3 = va_assign(body3, tree, X, r3, decl_lab)
    anch3 = [c.split("|")[1].split("_c")[0] for c in cells3]
    chk.ok(anch3 == ["a%d" % i for i in want], "FG-VA declared-label routing: every question lands in its category's anchor")
    cells_la = va_assign(body3, tree, X, dict(r3, heldout_anchor="leaf_ancestor"), decl_lab)
    chk.ok(cells_la != cells3, "RV5: the held-out-anchor ruling changes the cells (leaf_ancestor differs from declared_label)")
    # B5-1 value checks on a hand-built two-anchor body: the held-out side takes the nearest component across ALL anchors
    hb = dict(partition="A0", anchors=[dict(anchor="a0", mu=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
                                       dict(anchor="a1", mu=[[0.0, 0.0, 1.0], [0.6, 0.0, 0.8]])])
    htree = dict(tree, d1_ids=["a0", "a1"], label={"a0": "zero", "a1": "one"})
    Qh3 = FM.unit_rows(np.array([[0.9, 0.1, 0.0], [0.1, 0.0, 0.95], [0.55, 0.05, 0.8], [0.0, 1.0, 0.1]]))
    got_h = va_assign(hb, htree, Qh3, b51, None, side="heldout")
    chk.ok(got_h == ["A0|a0_c00", "A0|a1_c00", "A0|a1_c01", "A0|a0_c01"],
           "FG-VA B5-1 held-out side: nearest component across all anchors' components, both anchors reached (%s)" % got_h)
    got_f = va_assign(hb, htree, Qh3, b51, ["one", "zero", "zero", "one"], side="fit")
    chk.ok(got_f == ["A0|a1_c01", "A0|a0_c00", "A0|a0_c00", "A0|a1_c00"],
           "FG-VA B5-1 fit side: the declared category's anchor, then its nearest component (%s)" % got_f)
    fn_ = va_cell_fn(hb, htree, b51, Qh3, ["one", "zero", "zero", "one"])
    Qcopy = Qh3.copy()
    chk.ok(fn_(Qh3) == got_f and fn_(Qcopy) == got_h, "FG-VA va_cell_fn: Qt filed on the fit side, any other matrix label-free")
    chk.ok(FM.expect_refusal(lambda: va_assign(body3, tree, X, r3, None), "one category per row")
           and FM.expect_refusal(lambda: va_filing(tree, texts, X, sets, r3, dict(decl, **{texts[5]: "history"})), "no anchor of that label"),
           "FG-VA declared labels are required and must name an anchor")
    rolled = dict(tree, d1_mu=np.roll(tree["d1_mu"], 1, axis=0))
    idx_r, _ = va_filing(rolled, texts, X, sets, dict(ok_r, fit_filing="routed"))
    chk.ok(np.array_equal(idx_r, la) and not np.array_equal(anchor_index(rolled, X, "d1_nearest"), la),
           "RV9: routed filing follows the held-out ruling (leaf_ancestor), not the nearest depth-1 centroid")
    # arm (c): the merge on a fixture with KNOWN sizes
    Xs_ = FM.unit_rows(np.vstack([np.tile([1.0, 0.0, 0.0], (70, 1)), np.tile([0.9, 0.3, 0.0], (20, 1)), np.tile([0.0, 1.0, 0.0], (60, 1)),
                                  np.tile([0.0, 0.2, 1.0], (10, 1))]) + 1e-3 * rng.standard_normal((160, 3)))
    lab_ = np.repeat([0, 1, 2, 4], [70, 20, 60, 10])
    fin, log, empty = size_floor_merge(Xs_, lab_, 5, 55)
    chk.ok(empty == [3] and log == [(4, 2, 10), (1, 0, 20)] and np.bincount(fin).tolist() == [90, 70],
           "ARM (c) size floor: empty dropped; 10 -> its nearest (2), then 20 -> its nearest (0); sizes 90 / 70 (%s, %s)" % (log, np.bincount(fin).tolist()))


def st_va_oracle(chk):
    """B5-1 (READY_w0_delta1): on declared labels drawn AT RANDOM (no relation to the geometry), V_A's M1 through the deciding
    path (va_filing -> fit_va -> va_cell_fn -> FM.m1_block -> AF.score_cells) under the SHIPPED rulings is at most chance + 0.1;
    the R3 reading (held-out filed by declared label) on the same fixture reaches >= 0.9, so the check discriminates."""
    rng = np.random.default_rng(91)
    tree, X = _synthetic_o(rng)
    spec = dict(anchors=(2, 3, 2))
    labs = [str(tree["label"][a]).lower() for a in tree["d1_ids"]]
    n = X.shape[0]
    texts = ["t%04d" % i for i in range(n)]
    cat = [labs[i] for i in rng.integers(0, len(labs), n)]
    perm = rng.permutation(n)
    tr_i, he_i = perm[: n // 2], perm[n // 2:]
    train = [(texts[i], cat[i]) for i in tr_i]
    held = [(texts[i], cat[i]) for i in he_i]
    Qt, Qh = X[tr_i], X[he_i]
    rul = va_rulings()
    idx, _c = va_filing(tree, [t for t, _ in train], Qt, {}, rul, dict(train))
    body = fit_va("A0", Qt, idx, tree, spec, rul)
    sc, _h, _k = FM.m1_block(va_cell_fn(body, tree, rul, Qt, [c for _, c in train]), Qt, Qh, train, held)
    chance = max(np.bincount([labs.index(c) for _, c in held])) / float(len(held))
    chk.ok(sc["acc"] <= chance + 0.1, "FG-VA-ORACLE shipped rulings on RANDOM labels: M1 %.4f (%d/%d) <= chance %.4f + 0.1"
           % (sc["acc"], sc["hits"], sc["n"], chance))
    r3 = dict(rul, heldout_anchor="declared_label")
    lab_all = dict(train + held)
    oracle = lambda Q: va_assign(body, tree, Q, r3, [c for _, c in (train if Q is Qt else held)])
    so, _h, _k = FM.m1_block(oracle, Qt, Qh, train, held)
    chk.ok(so["acc"] >= 0.9 and len(lab_all) == n, "FG-VA-ORACLE the R3 reading on the same fixture: M1 %.4f >= 0.9 (the label oracle "
           "the check exists to catch)" % so["acc"])


def st_state(chk):
    with tempfile.TemporaryDirectory() as td:
        ensure_meta(td, "af_s137", TREES["af_s137"])
        ensure_meta(td, "af_s137", TREES["af_s137"])
        chk.ok(os.path.exists(os.path.join(td, "meta.json")), "FG-STATE meta.json written once, re-read equal")
        chk.ok(FM.expect_refusal(lambda: ensure_meta(td, "af_s2048", TREES["af_s2048"]), "differs"), "FG-STATE a different meta REFUSES")
        q = os.path.join(td, "o.txt")
        FM.write_once(q, "a")
        try:
            FM.write_once(q, "b")
            second = False
        except FileExistsError:
            second = True
        chk.ok(second, "FG-STATE a second write of an outcome file REFUSES")
    chk.ok(names_of("af_s137") == ("T",) + tuple("V%d" % s for s in SEEDS) + tuple("K%d" % s for s in SEEDS) and len(names_of(ANCHORED)) == 16,
           "FG-STATE partitions: 11 per re-draw, 16 for o0_clean_s42 (V_A0-V_A4)")
    chk.ok(FM.expect_refusal(lambda: FM.require_all({n: {} for n in names_of(ANCHORED) if n != "A3"}, names=names_of(ANCHORED)), "A3"),
           "FG-STATE the analysis REFUSES without V_A3")
    chk.ok([TREES[t]["fit_n"] for t in TREES] == [8126, 8130, 8133, 8125] and [TREES[t]["leaves"] for t in TREES] == [79, 81, 81, 84]
           and [TREES[t]["eval_n"] for t in TREES] == [3448, 3446, 3437, 3445], "FG-STATE the tree specs carry the registered leaves / EVAL counts")


def _e2e_values():
    """Independent recomputation, from the per-question arms of the last analyze(), of the quantities RV1-RV3 / RV8 target."""
    res, arms = LAST.get("res"), LAST.get("arms", {})
    if not res or not arms:
        return {}
    ok = {}
    ok["paired_v0"] = all(abs(res["trees"][t]["paired"]["V0"]["d1"] - float(np.mean(arms[t]["T"]["per1"] - arms[t]["V0"]["per1"]))) < 1e-12
                          for t in list(REDRAWS) + [ANCHORED])
    a = arms[ANCHORED]
    r = res["trees"][ANCHORED]
    ok["spread_va"] = all(abs(r["spread_VA"][m] - FM.spread_opt([a["A%d" % s][m] for s in SEEDS])) < 1e-15 for m in ("m1", "m2")) \
        and abs(r["spread_VA"]["m1"] - FM.spread_opt([a["V%d" % s]["m1"] for s in SEEDS])) > 1e-12
    common = [q for q in a["A0"]["per2"] if q in a["T"]["per2"]]
    ok["va_t"] = abs(r["va"]["T"]["d1"] - float(np.mean(a["A0"]["per1"] - a["T"]["per1"]))) < 1e-12 and \
        abs(r["va"]["T"]["d2"] - float(np.mean([a["A0"]["per2"][q] - a["T"]["per2"][q] for q in common]))) < 1e-15 and \
        abs(_va_t_perturbed(a) - float(np.mean(a["A0"]["per1"] - a["T"]["per1"]))) < 1e-12
    ok["disc"] = all(abs(res["trees"][t]["discordance"] - float(np.mean(arms[t]["T"]["per1"] != arms[t]["V0"]["per1"]))) < 1e-15
                     for t in list(REDRAWS) + [ANCHORED]) and any(
        abs(float(np.mean(arms[t]["T"]["per1"] != arms[t]["V0"]["per1"])) - float(np.mean(arms[t]["T"]["per1"] != arms[t]["K0"]["per1"]))) > 1e-12
        for t in list(REDRAWS) + [ANCHORED])
    sa = arms[SF_TREE]
    ok["sf"] = all(abs(res["sf"]["paired"]["S%d" % s]["d1"] - float(np.mean(sa["T"]["per1"] - sa["S%d" % s]["per1"]))) < 1e-12 for s in SEEDS) \
        and all(res["sf_parts"]["S%d" % s]["k_after"] <= 6 for s in SEEDS)
    return ok


def _va_t_perturbed(a):
    """The replica's V_A seeds can coincide (A0 == A1 there), so A2's arm is also read on a copy whose A1 is flipped: the
    contrast must stay A0 - T."""
    a2 = dict(a, A1=dict(a["A1"], per1=1.0 - a["A1"]["per1"]))
    gr, G_ = LAST["groups"][ANCHORED]
    return tree_readout(ANCHORED, TREES[ANCHORED], a2, gr, G_)["va"]["T"]["d1"]


def _replica_fg(td, rng, overlap=False, random_cats=False):
    """A replica data root for THIS driver: one embedding / dataset DB, four trees with their own pools, snapshots, fit regions
    and run dirs (three two-cell re-draws; an anchored tree with three anchors of two leaves each, a tenth of its fit texts filed
    under two anchors, as O's are), and the identity tree. Synthetic; nothing of record is read."""
    d_emb, n_lat, n_all = 24, 9, 1500
    unit = FM.unit_rows
    C = unit(rng.standard_normal((n_lat, d_emb)))
    cats = ["math", "law", "physics"]                 # the anchored tree's three anchors carry these labels (ruling R3)
    models = sorted(AF.p8.ARENA12) + ["extra-model"]
    texts, lat, cat_of, vecs = [], {}, {}, {}
    for i in range(n_all):
        c = int(rng.integers(n_lat))
        t = "replica question %04d on theme %d?" % (i, c)
        texts.append(t)
        u = rng.uniform()                                 # one draw either way: random_cats changes the labels only
        lat[t], cat_of[t] = c, (cats[min(int(u * 3), 2)] if random_cats else cats[(c + int(u < 0.25)) % 3])
        vecs[t] = C[c] + 0.45 * rng.standard_normal(d_emb)
    eid = {t: i + 1 for i, t in enumerate(texts)}
    qid = {t: "q_" + hashlib.sha256(t.encode("utf-8")).hexdigest()[:16] for t in texts}
    fwd = lambda p: p.replace("\\", "/")
    emb, ev, snap = (os.path.join(td, n) for n in ("embeddings_cache.db", "mmlu_pro_dataset_cache_v2.db", "snapshots.db"))
    _mk_db(emb, ["CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)", "CREATE TABLE queries (id TEXT PRIMARY KEY, distilled_text TEXT)"],
           [("INSERT INTO embeddings VALUES (?, ?)", [(t, struct.pack(">%df" % d_emb, *vecs[t])) for t in texts]),
            ("INSERT INTO queries VALUES (?, ?)", [(qid[t], t) for t in texts])])
    opts = {t: json.dumps(["A %d" % i, "B %d" % i]) for i, t in enumerate(texts)}
    skill = rng.uniform(0.2, 0.9, size=(len(models), n_lat))
    specs, pool_rows, snaps = {}, [], []
    for tree in list(REDRAWS) + [ANCHORED, "af_clean_s42"]:
        perm = rng.permutation(n_all)
        ev_t = [texts[j] for j in perm[:400]]
        fit_t = [texts[j] for j in perm[400:900]]
        if overlap and tree == REDRAWS[0]:
            fit_t = fit_t + [ev_t[0]]                     # RV4: one EVAL text of this tree also in its fit set
        res = {"math": sorted(eid[t] for t in ev_t)}
        pid = pool_guard.compute_pool_id(res)
        pool_rows += [(pid, "math", q) for q in res["math"]]
        rel = os.path.join("replica_runs", tree, "seed_1")
        rd = os.path.join(td, rel)
        os.makedirs(rd)
        L = unit(C[:6, :16] + 0.35 * rng.standard_normal((6, 16)))
        n_d1 = 3 if tree == ANCHORED else 2
        per = 6 // n_d1
        leaves = [dict(id="L%d" % j, depth=2, isLeaf=True, vmfMu=list(L[j]), sliceDim=16, childIds=[], label="leaf %d" % j,
                       parentIds=["D%d" % (j // per)]) for j in range(6)]
        d1 = [dict(id="D%d" % i, depth=1, isLeaf=False, vmfMu=list(L[i * per:(i + 1) * per].sum(0)), sliceDim=16,
                   childIds=["L%d" % j for j in range(i * per, (i + 1) * per)], label=(cats[i] if tree == ANCHORED else "anchor %d" % i),
                   parentIds=["R"]) for i in range(n_d1)]
        root = dict(id="R", depth=0, isLeaf=False, vmfMu=list(L.sum(0)), sliceDim=16, childIds=[d["id"] for d in d1], label="root", parentIds=[])
        with open(os.path.join(rd, "dag_snapshots.jsonl"), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(dict(iteration=1, nodes=[root] + d1 + leaves)) + "\n")
        Xf = unit(np.stack([vecs[t][:16] for t in fit_t]))
        lab = np.argmax(Xf @ L.T, axis=1)
        held = {"L%d" % j: [] for j in range(6)}
        for t, j in zip(fit_t, lab):
            held["L%d" % j].append(qid[t])
            if rng.uniform() < 0.10:                      # a tenth filed twice, under the next leaf (and anchor) too
                held["L%d" % ((j + per) % 6)].append(qid[t])
        gnodes = [dict(id="R", childIds=[d["id"] for d in d1], queryIds=[])]
        gnodes += [dict(id=d["id"], childIds=d["childIds"], queryIds=[]) for d in d1]
        gnodes += [dict(id="L%d" % j, childIds=[], queryIds=held["L%d" % j]) for j in range(6)]
        sid = "replica_%s" % tree
        snaps.append((sid, json.dumps(dict(rootId="R", nodes=gnodes)), json.dumps(res)))
        specs[tree] = dict(arm="a" if tree == ANCHORED else "b", run=rel, snapshot=sid, pool=pid, eval_n=400, leaves=6, fit_n=len(set(fit_t)),
                           split_word=CLOSED if tree == ANCHORED else ID_ONLY)
        if tree == ANCHORED:
            specs[tree]["anchors"] = (2, 2, 2)
    eres = [(eid[t], m, int(rng.uniform() < skill[mi, lat[t]]), opts[t], cat_of[t]) for t in texts for mi, m in enumerate(models)]
    _mk_db(ev, ["CREATE TABLE mmlu_pro (id INTEGER PRIMARY KEY, question TEXT, options TEXT, category TEXT)",
                "CREATE TABLE eval_question_link (question_id INTEGER PRIMARY KEY, question_text TEXT)",
                "CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, is_correct INTEGER, options_json TEXT, category TEXT, "
                "PRIMARY KEY (question_id, model_name))",
                "CREATE TABLE reserved_pool (pool_id TEXT, domain TEXT, question_id INTEGER, PRIMARY KEY (pool_id, question_id))"],
           [("INSERT INTO mmlu_pro VALUES (?, ?, ?, ?)", [(eid[t], t, opts[t], cat_of[t].capitalize()) for t in texts]),
            ("INSERT INTO eval_question_link VALUES (?, ?)", [(eid[t], t) for t in texts]),
            ("INSERT INTO eval_results VALUES (?, ?, ?, ?, ?)", eres),
            ("INSERT INTO reserved_pool VALUES (?, ?, ?)", pool_rows)])
    _mk_db(snap, ["CREATE TABLE snapshots (id TEXT PRIMARY KEY, graph TEXT, reserved_queries TEXT)"],
           [("INSERT INTO snapshots VALUES (?, ?, ?)", snaps)])
    ident = specs.pop("af_clean_s42")
    return dict(trees=specs, identity=ident, emb=fwd(emb), ev=fwd(ev), eval_ids=frozenset(), pid=None, leaves=6)


def _va_recompute(tree, spec, parts):
    """C5-1 (READY_w0_delta2): V_A's M1 recomputed INDEPENDENTLY of va_assign / va_cell_fn / anchor_index / FM.m1_block /
    AF.score_cells, from the stored partitions and the corpus: TRAIN rows -> the anchor whose label is the row's OWN declared
    category, then the nearest component mean of that anchor; EVAL rows -> the nearest component mean across ALL anchors'
    components (label-free); cell majority over TRAIN (first-seen wins a tie, Counter.most_common's order); hits on EVAL.
    Also the R3 oracle (EVAL rows filed by their own label, as the TRAIN rows) for the leg's discrimination."""
    from collections import Counter, defaultdict
    _pid, ids = tree_pool(spec)
    train, heldout, _cs = corpus_for(spec, ids)
    vec = AF.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    Qt, Qh = AF.sliced(vec, [t for t, _ in train], DIM), AF.sliced(vec, [t for t, _ in heldout], DIM)
    otree = load_tree(tree, spec)
    lab2a = {str(otree["label"][a]).lower(): a for a in otree["d1_ids"]}
    out = {}
    for nm in sorted(parts):
        if nm[0] != "A":
            continue
        b = parts[nm]
        by = {A["anchor"]: A for A in b["anchors"]}

        def within(Q, labels):
            ks = []
            for r, c in enumerate(labels):
                A = by[lab2a[str(c).lower()]]
                M = np.array(A["mu"], dtype=np.float64)
                M = M / np.linalg.norm(M, axis=1, keepdims=True)
                ks.append("%s|%s_c%02d" % (b["partition"], A["anchor"], int(np.argmax(M @ Q[r]))))
            return ks
        allc = [(A["anchor"], j, np.array(A["mu"][j], dtype=np.float64)) for A in b["anchors"] for j in range(len(A["mu"]))]
        MU = np.stack([m / np.linalg.norm(m) for _a, _j, m in allc])
        kt = within(Qt, [c for _, c in train])
        kh = ["%s|%s_c%02d" % (b["partition"], allc[i][0], allc[i][1]) for i in np.argmax(Qh @ MU.T, axis=1)]
        tc = defaultdict(Counter)
        for k, (_, c) in zip(kt, train):
            tc[k][c] += 1
        major = {k: cnt.most_common(1)[0][0] for k, cnt in tc.items()}
        hits = sum(1 for k, (_, c) in zip(kh, heldout) if major.get(k) == c)
        ko = within(Qh, [c for _, c in heldout])
        out[nm] = dict(hits=hits, n=len(heldout), kh=kh, major=major,
                       oracle=sum(1 for k, (_, c) in zip(ko, heldout) if major.get(k) == c) / float(len(heldout)))
    cnt = Counter(c for _, c in heldout)
    return out, max(cnt.values()) / float(len(heldout))


def _va_matches(arms, rec):
    """-> (all equal, per-partition (shipped hits, recomputed hits)): tree_measures' V_A arms against _va_recompute."""
    eq, rows = True, {}
    for nm, r in rec.items():
        a = arms.get(nm, {})
        same = (a.get("hits") == r["hits"] and a.get("sc", {}).get("hits") == r["hits"] and list(a.get("cells_h", [])) == r["kh"]
                and a.get("sc", {}).get("major") == r["major"] and abs(a.get("m1", -1.0) - r["hits"] / float(r["n"])) < 1e-15)
        eq = eq and same
        rows[nm] = (a.get("hits"), r["hits"])
    return eq and len(rec) == 5, rows


def st_e2e_random(chk):
    """C5-1 (READY_w0_delta2): the random-label check on THE PATH THE RUN TAKES. A replica whose declared categories are drawn AT
    RANDOM (no relation to the geometry); run() fits the anchored tree's 11 partitions (pin set from the run's own printed sizes);
    tree_measures() -- the function analyze() calls -- scores V_A. Asserted: every A_s M1 <= chance + 0.1; tree_measures' V_A
    hits, EVAL cells and cell majorities EQUAL the independent recomputation; and the R3 oracle on the same data >= 0.9 (so the
    leg can see a label leak). Kills Y5-B (EVAL side filed with its labels in tree_measures) and Y5-C (lab_t misaligned)."""
    g = globals()
    saved = {k: g[k] for k in ("TREES", "IDENTITY", "VA_RULINGS", "DIM", "VA_FIT_SIZES")}
    saved_fm, saved_b = FM.DATA_ROOT, F.B
    res = {}
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        rep = _replica_fg(td, np.random.default_rng(20260927), random_cats=True)
        try:
            g.update(TREES=rep["trees"], IDENTITY=rep["identity"], DIM=16, VA_RULINGS=dict(VA_RULINGS), VA_FIT_SIZES={})
            FM.DATA_ROOT, F.B = td, 200
            tree = _arm_a_tree()
            sd = os.path.join(td, "rnd", "state")
            with _replica_env(td, rep):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    run(state_dir=os.path.join(td, "rnd", "owed"), only=tree, max_chunks=0)
                    _pin_from_dry(buf.getvalue())
                    run(state_dir=sd, only=tree)
                    keyed = F.keyed_questions()
                    veck = F.embed_matrix(AF.EMB_DB, list(keyed[3].values()), DIM)
                    parts = tree_state(sd, tree)
                    arms, _g, _G, _h = tree_measures(tree, TREES[tree], parts, keyed, veck)
                    rec, chance = _va_recompute(tree, TREES[tree], parts)
                res = dict(arms=arms, rec=rec, chance=chance, n_parts=len(parts))
        finally:
            g.update(saved)
            FM.DATA_ROOT, F.B = saved_fm, saved_b
            gc.collect()
    arms, rec, chance = res.get("arms", {}), res.get("rec", {}), res.get("chance", 1.0)
    m1 = {nm: arms[nm]["m1"] for nm in sorted(arms) if nm[0] == "A"}
    chk.ok(len(m1) == 5 and max(m1.values()) <= chance + 0.1,
           "FG-E2E-RANDOM tree_measures on RANDOM declared labels: V_A M1 max %.4f (A0 %.4f) <= chance %.4f + 0.1"
           % (max(m1.values()) if m1 else float("nan"), m1.get("A0", float("nan")), chance))
    eq, rows = _va_matches(arms, rec)
    chk.ok(eq, "FG-E2E-RANDOM tree_measures' V_A hits / EVAL cells / majorities == the independent recomputation (%s)"
           % ", ".join("%s %s/%s" % (k, a, b) for k, (a, b) in sorted(rows.items())))
    orc = min(r["oracle"] for r in rec.values()) if rec else 0.0
    chk.ok(orc >= 0.9, "FG-E2E-RANDOM the R3 oracle (EVAL filed by its own label) on the same data: M1 min %.4f >= 0.9 "
           "(the leg discriminates a label leak)" % orc)


def _arm_a_tree():
    return [t for t, sp in TREES.items() if sp["arm"] == "a"][0]


def _pin_from_dry(txt):
    """Selftest only: read the dry run's printed fit sizes and set them as the pin (the registrar's act on real data)."""
    import re
    m = re.search(r"V_A FIT SIZES \(fit filing, O's depth-1 order\): \[([0-9, ]+)\]", txt)
    if not m:
        raise SystemExit("no V_A FIT SIZES line in the dry run")
    sizes = tuple(int(x) for x in m.group(1).split(","))
    globals()["VA_FIT_SIZES"] = {_arm_a_tree(): sizes}
    return sizes


def _with_pin(tree, fn):
    good = dict(VA_FIT_SIZES)
    globals()["VA_FIT_SIZES"] = dict(good, **{tree: tuple(x + (1 if i == 0 else 0) for i, x in enumerate(good[tree]))})
    try:
        return fn()
    finally:
        globals()["VA_FIT_SIZES"] = good


def st_e2e(chk):
    """This driver's --dry-run, --run and --analyze END TO END on a replica data root (synthetic; every sqlite open outside the
    temp dir raises): the pools, fit sets, V_A filing, measures, readouts, render and the write-once outcome all execute."""
    g = globals()
    saved = {k: g[k] for k in ("TREES", "IDENTITY", "VA_RULINGS", "DIM", "VA_FIT_SIZES")}
    saved_fm, saved_b = FM.DATA_ROOT, F.B
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        rep = _replica_fg(td, np.random.default_rng(20260927))
        out = {}
        try:
            g.update(TREES=rep["trees"], IDENTITY=rep["identity"], DIM=16,
                     VA_RULINGS=dict(VA_RULINGS), VA_FIT_SIZES={})       # the SHIPPED rulings (B5-1), end to end; pin OWED
            FM.DATA_ROOT, F.B = td, 200
            sd = os.path.join(td, "fg", "state")
            oc, ac = os.path.join(td, "fg", "outcome.txt"), os.path.join(td, "fg", "arms.csv")
            with _replica_env(td, rep):
                for mode, fn in (("dry", dry_run),
                                 ("owed", lambda: run(state_dir=os.path.join(td, "fg", "owed"), only=_arm_a_tree(), max_chunks=0)),
                                 ("pin", lambda: _pin_from_dry(out["dry"][1])),
                                 ("mismatch", lambda: _with_pin(_arm_a_tree(), lambda: run(state_dir=os.path.join(td, "fg", "mm"),
                                                                                         only=_arm_a_tree(), max_chunks=0))),
                                 ("run", lambda: run(state_dir=sd)), ("analyze", lambda: analyze(sd, oc, ac)),
                                 ("again", lambda: analyze(sd, oc, ac))):
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf):
                        try:
                            rc = fn()
                        except SystemExit as e:
                            rc = "SystemExit: %s" % e
                    out[mode] = (rc, buf.getvalue())
            txt = open(oc, encoding="utf-8").read() if os.path.exists(oc) else ""
            rows = open(ac, encoding="utf-8").read().splitlines() if os.path.exists(ac) else []
            out["values"] = _e2e_values()
            with _replica_env(td, rep):                        # C5-1: the deciding path's V_A against the recomputation
                with contextlib.redirect_stdout(io.StringIO()):
                    at = _arm_a_tree()
                    out["va_rec"] = _va_recompute(at, TREES[at], tree_state(sd, at))
            # RV6: copy the state, forge one partition's script identity, analyze must refuse
            import shutil
            sd2 = os.path.join(td, "fg2", "state")
            shutil.copytree(sd, sd2)
            pf = os.path.join(sd2, REDRAWS[0], "part_V1.json")
            b_ = json.load(open(pf, encoding="utf-8"))
            b_["script"] = dict(b_["script"], blob="0" * 40)
            os.chmod(pf, 0o666)
            with open(pf, "w", encoding="utf-8") as f:
                f.write(json.dumps(b_, sort_keys=True))
            with _replica_env(td, rep):
                with contextlib.redirect_stdout(io.StringIO()):
                    try:
                        analyze(sd2, os.path.join(td, "fg2", "o.txt"), os.path.join(td, "fg2", "a.csv"))
                        out["foreign"] = ("no refusal", "")
                    except SystemExit as e:
                        out["foreign"] = ("SystemExit: %s" % e, "")
            # RV7: the p2dca cross-check
            with _replica_env(td, rep), eval_ids_override(POOL_OF_RECORD, frozenset([1, 2])):   # no open outside the replica
                out["p2dca"] = bool(FM.expect_refusal(lambda: corpus_for(dict(pool=POOL_OF_RECORD), frozenset([3])), "differ from the pool file"))
            # RV4: a replica whose first re-draw files one of its EVAL texts in its fit set
            td3 = os.path.join(td, "ov")
            os.makedirs(td3)
            rep3 = _replica_fg(td3, np.random.default_rng(20260927), overlap=True)
            g.update(TREES=rep3["trees"], IDENTITY=rep3["identity"])
            FM.DATA_ROOT = td3
            with _replica_env(td3, rep3):
                with contextlib.redirect_stdout(io.StringIO()):
                    try:
                        run(state_dir=os.path.join(td3, "st"), max_chunks=1)
                        out["overlap"] = ("no refusal", "")
                    except SystemExit as e:
                        out["overlap"] = ("SystemExit: %s" % e, "")
        finally:
            g.update(saved)
            FM.DATA_ROOT, F.B = saved_fm, saved_b
            gc.collect()
    chk.ok(out["dry"][0] == 0 and "dry-run complete: zero measures" in out["dry"][1] and "1 anchor(s): " in out["dry"][1]
           and "2 anchor(s): " in out["dry"][1], "FG-E2E --dry-run completes on the replica; O's multi-anchor filing is counted")
    pinned = out.get("pin", (None, ""))[0]
    chk.ok(isinstance(pinned, tuple) and len(pinned) == 3 and sum(pinned) > 0 and "; pinned OWED (ruling 12" in out["dry"][1],
           "FG-E2E ruling 12: --dry-run prints the per-anchor fit sizes (%s) with the pin OWED" % (pinned,))
    chk.ok(out["owed"][0] == 0 and "V_A partitions NOT fitted (ruling 12" in out["owed"][1] and "pinned OWED" in out["owed"][1],
           "FG-E2E ruling 12: --run with the pin OWED fits no V_A partition and says why")
    chk.ok(isinstance(out["mismatch"][0], str) and "!= the pinned" in out["mismatch"][0] and "fitted (" not in out["mismatch"][1],
           "FG-E2E ruling 12: a pin that differs from the sizes REFUSES before any fit of the tree")
    chk.ok(("pinned %s" % list(pinned)) in out["run"][1] if isinstance(pinned, tuple) else False,
           "FG-E2E ruling 12: --run with the pin set prints the equal pin and fits V_A")
    chk.ok(out["run"][0] == 0 and out["run"][1].count("fitted (") == 3 * 11 + 16 + 6 and "[PIN] before == after" in out["run"][1],
           "FG-E2E --run fits 55 partitions (3 x 11 + 16 + arm (c) T and S0-S4); pins equal before and after")
    chk.ok(out["analyze"][0] == 0 and "D2: the loss appears in" in txt and "A2 V_A vs O" in txt and "READING:" in txt
           and "SUPPORT:" in txt and "ARM (c) (DESCRIPTIVE)" in txt and len(rows) == 1 + 3 * 11 + 16 + 6,
           "FG-E2E --analyze writes the outcome (D1, D2, A1, A2, arm (c), P1-P7, F1, F2, support) and the 55-row arms CSV")
    val = out.get("values", {})
    for key_, what in (("paired_v0", "RV1/RV8: paired V0 d1 = mean(per1_T - per1_V0) on every tree"),
                       ("spread_va", "RV2: spread_V_A = the spread over A0-A4 (M1, M2)"),
                       ("va_t", "RV3: A2's contrast is A0 - T (d1 and d2 from the per-question arms)"),
                       ("disc", "RV8: the support discordance is T against V0"),
                       ("sf", "ARM (c): T - S_s = mean(per1_T - per1_S_s); k after merging <= 6")):
        chk.ok(val.get(key_) is True, "FG-E2E " + what)
    rec_, _ch = out.get("va_rec", ({}, None))
    eq_, rows_ = _va_matches(LAST.get("arms", {}).get(_arm_a_tree(), {}), rec_) if rec_ else (False, {})
    chk.ok(eq_, "FG-E2E C5-1: analyze()'s V_A hits / EVAL cells / majorities == the independent recomputation (%s)"
           % ", ".join("%s %s/%s" % (k, a, b) for k, (a, b) in sorted(rows_.items())))
    chk.ok(out.get("overlap", ("", ""))[0].startswith("SystemExit") and "fit texts are EVAL texts" in out["overlap"][0],
           "RV4: an injected fit/EVAL exact overlap makes run() REFUSE (%s)" % out.get("overlap", ("",))[0][:80])
    chk.ok(out.get("foreign", ("", ""))[0].startswith("SystemExit") and "another script identity" in out["foreign"][0],
           "RV6: a partition with a foreign script identity makes analyze() REFUSE")
    chk.ok(out.get("p2dca") is True, "RV7: a p2dca tree whose snapshot ids differ from the pool file REFUSES in corpus_for")
    chk.ok(out["analyze"][1].count("[PIN before] ") == out["analyze"][1].count("[PIN after ] ") > 0,
           "FG-E2E --analyze prints the before-pins and the after-pins")
    chk.ok(isinstance(out["again"][0], str) and "WRITE-ONCE" in out["again"][0], "FG-E2E a second --analyze REFUSES (write-once)")
    chk.ok("MISMATCH (a READY defect)" in txt, "FG-E2E the replica's identity tree does not carry the record's numbers: P6 prints MISMATCH")


def selftest(only=None, quiet=False):
    chk = FM._Checks(quiet)
    sel = (lambda name: only is None or name in only)
    if sel("FG-THREADS"):
        chk.ok(all(os.environ.get(v) == "1" for v in THREAD_VARS), "FG-THREADS the three thread variables are 1")
    if sel("FG-RENDER"):
        st_render(chk)
    if sel("FG-POOL"):
        st_pool(chk)
    if sel("FG-VA"):
        st_va(chk)
    if sel("FG-VA-ORACLE"):
        st_va_oracle(chk)
    if sel("FG-STATE"):
        st_state(chk)
    if sel("FG-E2E"):
        st_e2e(chk)
    if sel("FG-E2E-RANDOM"):
        st_e2e_random(chk)
    if sel("FG-PIN"):
        pin = VA_FIT_SIZES.get(ANCHORED)
        chk.ok(set(VA_FIT_SIZES) == {ANCHORED} and pin == (944, 905, 587, 647, 504, 792, 267, 558, 656, 423, 542, 286, 666, 348)
               and len(pin) == len(O_ANCHOR_LEAVES) == 14 and sum(pin) == TREES[ANCHORED]["fit_n"] == 8125
               and all(n > k for n, k in zip(pin, O_ANCHOR_LEAVES)),
               "FG-PIN C5-2: VA_FIT_SIZES = the steward's pin for o0_clean_s42 (14 anchors, sum %s = fit_n 8,125, each > its k)"
               % (None if pin is None else sum(pin)))
    return chk.n


MUTANTS = (
    ("D2 counts wins", '    k = sum(1 for t in REDRAWS if ver[t]["l1"])', '    k = sum(1 for t in REDRAWS if ver[t]["c1"] or ver[t]["c2"])', ("FG-RENDER",)),
    ("L1_r on M1 only", "l1=bool(l1_m1 or l1_m2),", "l1=bool(l1_m1),", ("FG-RENDER",)),
    ("A1 in the win form", '    return dict(a1=FM.loss(p["d2"], sv["m2"], p["d2_lo"], p["d2_hi"]),',
     '    return dict(a1=FM.criterion(p["d2"], sv["m2"], p["d2_lo"], p["d2_hi"]),', ("FG-RENDER",)),
    ("A2 against spread_V, not spread_V_A", '                a2=FM.criterion(a2["d2"], r["spread_VA"]["m2"], a2["d2_lo"], a2["d2_hi"]),',
     '                a2=FM.criterion(a2["d2"], sv["m2"] * 0.1, a2["d2_lo"], a2["d2_hi"]),', ("FG-RENDER",)),
    ("seed-wise rule on any seed", '                seed_m1=bool(all(r["paired"]["V%d" % s]["d1_hi"] < 0 for s in SEEDS)),',
     '                seed_m1=bool(any(r["paired"]["V%d" % s]["d1_hi"] < 0 for s in SEEDS)),', ("FG-RENDER",)),
    ("F1 on k <= 1", "    if k == 0:\n        L.append(\"FALSIFIER F1 FIRES", "    if k <= 1:\n        L.append(\"FALSIFIER F1 FIRES", ("FG-RENDER",)),
    ("P1 on k >= 1", '"of 3\\" (p 0.60) -> %s" % (k, {0: 0.10, 1: 0.30, 2: 0.35, 3: 0.25}[k], _sc(k >= 2)))',
     '"of 3\\" (p 0.60) -> %s" % (k, {0: 0.10, 1: 0.30, 2: 0.35, 3: 0.25}[k], _sc(k >= 1)))', ("FG-RENDER",)),
    ("P6 on M1 only", "    ident_ok = bool(ident[\"m1\"] == FM.RECORD_M1 and ident[\"m2\"] == FM.RECORD_M2)",
     "    ident_ok = bool(ident[\"m1\"] == FM.RECORD_M1)", ("FG-RENDER",)),
    ("P5 strict", '                p5=bool(r["arms"]["A0"]["m2"] >= r["arms"]["V0"]["m2"]))', '                p5=bool(r["arms"]["A0"]["m2"] > r["arms"]["V0"]["m2"] + 1e-3))', ("FG-RENDER",)),
    ("pool hash check removed", "    if pid != spec[\"pool\"]:\n        refuse(\"snapshot %s's", "    if False:\n        refuse(\"snapshot %s's", ("FG-POOL",)),
    ("pool count check removed", "    if n != spec[\"eval_n\"]:\n", "    if False:\n", ("FG-POOL",)),
    ("pool DB rows unchecked", "    if not rows or pool_guard.compute_pool_id(rows) != pid:", "    if False:", ("FG-POOL",)),
    ("eval_ids override not restored", "    finally:\n        pool_guard.eval_ids = orig", "    finally:\n        pass", ("FG-POOL",)),
    ("any embedding DB admissible", "    if name not in EMB_DB_ADMISSIBLE:\n", "    if False:\n", ("FG-POOL",)),
    ("EVAL text in the fit admitted", "    if exact:\n        refuse(", "    if False:\n        refuse(", ("FG-POOL",)),
    ("V_A rulings not required", "    if unruled:\n        refuse(\"V_A readings unruled", "    if False:\n        refuse(\"V_A readings unruled", ("FG-VA",)),
    ("anchor leaf counts unchecked", "    if tuple(got) != tuple(spec[\"anchors\"]):\n", "    if False:\n", ("FG-VA",)),
    ("graph-exclusive keeps doubly-filed", "next(iter(sets[t])) if len(sets.get(t, ())) == 1 else -1", "next(iter(sets[t])) if len(sets.get(t, ())) >= 1 else -1", ("FG-VA",)),
    ("V_A assigns by nearest anchor only", "        rows = np.flatnonzero(a_idx == i)\n", "        rows = np.flatnonzero(a_idx >= 0) if i == 0 else np.array([], dtype=int)\n", ("FG-VA",)),
    ("V_A MAP ignores weights", "            j = FM.map_assign(Q[rows], mu, np.array(A[\"kappa\"]), np.array(A[\"pi\"]))",
     "            j = FM.nearest_assign(Q[rows], mu)", ("FG-VA",)),
    ("meta not compared", "            if f.read() != body:\n", "            if False:\n", ("FG-STATE",)),
    ("threads not pinned", "for _v in THREAD_VARS:                       # BEFORE numpy", "for _v in ():                       # BEFORE numpy", ("FG-THREADS",)),
    ("arm (c) floor ignored", "        small = sorted((len(m), j) for j, m in members.items() if len(m) < floor)",
     "        small = sorted((len(m), j) for j, m in members.items() if len(m) < 0)", ("FG-VA",)),
    ("arm (c) merges into the farthest", "        best = -max(cos)[1]", "        best = -min(cos)[1]", ("FG-VA",)),
    ("declared label filed by geometry", '        idx = anchor_index(tree, X, "declared_label", [decl[t] for t in texts])',
     '        idx = anchor_index(tree, X, "leaf_ancestor")', ("FG-VA",)),
    ("shipped rulings not B5-1's", 'VA_RULINGS = dict(fit_filing="declared_label", heldout_anchor="all_components_nearest", assign="nearest")',
     'VA_RULINGS = dict(fit_filing="declared_label", heldout_anchor="leaf_ancestor", assign="nearest")', ("FG-VA",)),
    ("B5-1: declared_label re-admitted as the held-out reading (the oracle)",
     'VA_RULINGS = dict(fit_filing="declared_label", heldout_anchor="all_components_nearest", assign="nearest")',
     'VA_RULINGS = dict(fit_filing="declared_label", heldout_anchor="declared_label", assign="nearest")', ("FG-VA", "FG-VA-ORACLE")),
    ("B5-1: held-out side restricted to the first anchor", '        MU = np.vstack([np.array(A["mu"]) for A in body["anchors"]])\n',
     '        MU = np.vstack([np.array(A["mu"]) for A in body["anchors"][:1]])\n', ("FG-VA",)),
    ("B5-1: farthest component (min for max)", '        return [names[int(j)] for j in FM.nearest_assign(Q, MU)]',
     '        return [names[int(j)] for j in np.argmin(Q @ FM.unit_rows(MU).T, axis=1)]', ("FG-VA", "FG-VA-ORACLE")),
    ("B5-1: fit side routed label-free", '    if side == "fit" and rulings["fit_filing"] == "declared_label":\n',
     '    if False:\n', ("FG-VA",)),
    ("B5-1: every matrix on the fit side", '    return lambda Q: va_assign(body, tree, Q, rulings, lab_t if Q is Qt else None, side="fit" if Q is Qt else "heldout")',
     '    return lambda Q: va_assign(body, tree, Q, rulings, lab_t if Q is Qt else None, side="fit")', ("FG-VA", "FG-VA-ORACLE")),
    ("B5-1: MAP admitted with all_components", '    if r["heldout_anchor"] == "all_components_nearest" and r["assign"] != "nearest":\n',
     '    if False:\n', ("FG-VA",)),
    ("ruling 12: pin mismatch not refused", "                elif tuple(pin) != sizes:\n", "                elif False:\n", ("FG-E2E",)),
    ("ruling 12: owed pin ignored", "                if pin is None:\n                    va_why", "                if False:\n                    va_why",
     ("FG-E2E",)),
    ("Y5-B tree_measures files EVAL with its labels", "            fn = va_cell_fn(b, otree, rul, Qt, lab_t)\n",
     "            fn = va_cell_fn(b, otree, rul, Qh, [c for _, c in heldout])\n", ("FG-E2E", "FG-E2E-RANDOM")),
    ("Y5-C lab_t misaligned with Qt (reversed)", "        lab_t = [c for _, c in train]          # B5-1",
     "        lab_t = [c for _, c in train][::-1]          # B5-1", ("FG-E2E", "FG-E2E-RANDOM")),
    ("Y5-D every matrix filed by its labels in tree_measures", "            fn = va_cell_fn(b, otree, rul, Qt, lab_t)\n",
     "            fn = lambda Q, b=b: va_assign(b, otree, Q, rul, lab_t if Q is Qt else [c for _, c in heldout], side=\"fit\")\n",
     ("FG-E2E", "FG-E2E-RANDOM")),
    ("Y5-E tree_measures scores A0 for every seed", "            b = parts[nm]\n", "            b = parts[\"A0\"]\n", ("FG-E2E", "FG-E2E-RANDOM")),
    ("C5-2 pin first anchor off by one", "VA_FIT_SIZES = {\"o0_clean_s42\": (944,", "VA_FIT_SIZES = {\"o0_clean_s42\": (945,", ("FG-PIN",)),
    ("C5-2 pin anchors reordered", "(944, 905, 587, 647, 504, 792, 267, 558, 656, 423, 542, 286, 666, 348)}",
     "(905, 944, 587, 647, 504, 792, 267, 558, 656, 423, 542, 286, 666, 348)}", ("FG-PIN",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index(chr(10) + "MUTANTS = (")
    head, tail = src[:cut], src[cut:]
    print("MUTANTS (%d): each removes or alters one check; KILLED iff the targeted selftest subset fails" % len(MUTANTS))
    killed = 0
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: the target text occurs %d times (must be exactly 1)" % (TAG, name, head.count(old)))
        ok_orig = _exec_selftest(src, tests)
        res = _exec_selftest(head.replace(old, new) + tail, tests)
        k = (res is not True) and ok_orig is True
        killed += int(k)
        print("  %-42s tests %-10s original %-4s mutant %-8s | %s" % (name, ",".join(tests), "PASS" if ok_orig is True else "FAIL",
                                                                   "KILLED" if k else "SURVIVED", "" if res is True else res[:110]))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def _exec_selftest(src, tests):
    saved = {v: os.environ.get(v) for v in THREAD_VARS}
    ns = {"__name__": "flat_generality_mutant", "__file__": os.path.abspath(__file__)}
    guarded = sqlite3.connect
    try:
        for v in THREAD_VARS:
            os.environ.pop(v, None)
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True)
        return True
    except BaseException as e:                   # noqa: B902 - a killed mutant may raise anything
        return "%s: %s" % (type(e).__name__, str(e)[:120])
    finally:
        for v, x in saved.items():
            os.environ[v] = x
        pool_guard.eval_ids = _ORIG_EVAL_IDS
        sqlite3.connect = guarded


_ORIG_EVAL_IDS = pool_guard.eval_ids


# ------------------------------------------------------------------------------------------------ inertness (flat_mix_mmlu.py)
def _git_blob(blob):
    out = subprocess.run(["git", "-C", ROOT, "cat-file", "blob", blob], capture_output=True, check=True).stdout
    if _pins_of_bytes(out)["blob"] != blob:
        refuse("git object %s does not hash to itself" % blob)
    return out.replace(b"\r\n", b"\n")


def _replica(td, rng):
    """A replica data root: embeddings_cache.db, mmlu_pro_dataset_cache_v2.db, snapshots.db and two run dirs, synthetic. Nine
    overlapping latent topics, a 6-leaf tree whose centroids are perturbed off them (T and O differently), noisy labels and keys
    that depend on the topic, so the arms genuinely differ (the sensitivity control must see a one-constant change)."""
    d_emb, n_lat, n_leaves = 24, 9, 6
    C = FM.unit_rows(rng.standard_normal((n_lat, d_emb)))
    cats = ["math", "law", "physics", "biology"]
    models = sorted(AF.p8.ARENA12) + ["extra-model"]
    n_train, n_eval = 700, 600
    texts, cat_of, vecs, lat = [], {}, {}, {}
    for i in range(n_train + n_eval):
        c = int(rng.integers(n_lat))
        t = "synthetic question %04d about topic %d?" % (i, c)
        texts.append(t)
        lat[t] = c
        cat_of[t] = cats[(c + int(rng.uniform() < 0.25)) % 4]
        vecs[t] = C[c] + 0.45 * rng.standard_normal(d_emb)
    train_t, eval_t = texts[:n_train], texts[n_train:]
    qid = {t: "q_" + hashlib.sha256(t.encode("utf-8")).hexdigest()[:16] for t in texts}
    fwd = lambda p: p.replace("\\", "/")
    emb = os.path.join(td, "embeddings_cache.db")
    _mk_db(emb, ["CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)", "CREATE TABLE queries (id TEXT PRIMARY KEY, distilled_text TEXT)"],
           [("INSERT INTO embeddings VALUES (?, ?)", [(t, struct.pack(">%df" % d_emb, *vecs[t])) for t in texts]),
            ("INSERT INTO queries VALUES (?, ?)", [(qid[t], t) for t in texts])])
    ev = os.path.join(td, "mmlu_pro_dataset_cache_v2.db")
    eval_ids = list(range(1, n_eval + 1))
    opts = {t: json.dumps(["A %d" % i, "B %d" % i]) for i, t in enumerate(texts)}
    skill = rng.uniform(0.2, 0.9, size=(len(models), n_lat))
    eres = []
    for q, t in [(eval_ids[j], t) for j, t in enumerate(eval_t)] + [(10000 + i, t) for i, t in enumerate(train_t)]:
        for mi, m in enumerate(models):
            eres.append((q, m, int(rng.uniform() < skill[mi, lat[t]]), opts[t], cat_of[t]))
    pool_rows = {"math": eval_ids}
    pid = pool_guard.compute_pool_id(pool_rows)
    _mk_db(ev, ["CREATE TABLE mmlu_pro (id INTEGER PRIMARY KEY, question TEXT, options TEXT, category TEXT)",
                "CREATE TABLE eval_question_link (question_id INTEGER PRIMARY KEY, question_text TEXT)",
                "CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, is_correct INTEGER, options_json TEXT, category TEXT, "
                "PRIMARY KEY (question_id, model_name))",
                "CREATE TABLE reserved_pool (pool_id TEXT, domain TEXT, question_id INTEGER, PRIMARY KEY (pool_id, question_id))"],
           [("INSERT INTO mmlu_pro VALUES (?, ?, ?, ?)", [(i + 1, t, opts[t], cat_of[t].capitalize()) for i, t in enumerate(texts)]),
            ("INSERT INTO eval_question_link VALUES (?, ?)", [(eval_ids[j], t) for j, t in enumerate(eval_t)]),
            ("INSERT INTO eval_results VALUES (?, ?, ?, ?, ?)", eres),
            ("INSERT INTO reserved_pool VALUES (?, ?, ?)", [(pid, "math", q) for q in eval_ids])])
    fit_t = train_t[:600]
    graph = dict(rootId="r", nodes=[dict(id="r", childIds=["a", "b"], queryIds=[]), dict(id="a", childIds=[], queryIds=[qid[t] for t in fit_t[:350]]),
                                    dict(id="b", childIds=[], queryIds=[qid[t] for t in fit_t[300:]])])
    snap = os.path.join(td, "snapshots.db")
    _mk_db(snap, ["CREATE TABLE snapshots (id TEXT PRIMARY KEY, graph TEXT, reserved_queries TEXT)"],
           [("INSERT INTO snapshots VALUES (?, ?, ?)", [(FM.T_SNAPSHOT, json.dumps(graph), json.dumps(pool_rows))])])
    for rel, jitter in ((FM.T_RUN, 0.35), (FM.O_RUN, 0.55)):
        rd = os.path.join(td, rel)
        os.makedirs(rd)
        L = FM.unit_rows(C[:n_leaves, :16] + jitter * rng.standard_normal((n_leaves, 16)))
        leaves = [dict(id="L%d" % j, depth=2, isLeaf=True, vmfMu=list(L[j]), sliceDim=16, childIds=[], label="leaf %d" % j,
                       parentIds=["D%d" % (j // 2)]) for j in range(n_leaves)]
        d1 = [dict(id="D%d" % i, depth=1, isLeaf=False, vmfMu=list(L[2 * i] + L[2 * i + 1]), sliceDim=16,
                   childIds=["L%d" % (2 * i), "L%d" % (2 * i + 1)], label="d1 %d" % i, parentIds=["R"]) for i in range(n_leaves // 2)]
        root = dict(id="R", depth=0, isLeaf=False, vmfMu=list(L.sum(0)), sliceDim=16, childIds=[d["id"] for d in d1], label="root", parentIds=[])
        with open(os.path.join(rd, "dag_snapshots.jsonl"), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(dict(iteration=1, nodes=[root] + d1 + leaves)) + "\n")
    return dict(pid=pid, eval_ids=frozenset(eval_ids), fit_n=len(fit_t), emb=fwd(emb), ev=fwd(ev), leaves=n_leaves)


@contextlib.contextmanager
def _replica_env(td, rep):
    """Point every module the FLAT instrument reads at the replica, and admit NO sqlite open outside td."""
    saved = dict(AF_EMB=AF.EMB_DB, AF_EVAL=AF.EVAL_DB, F_EMB=F.EMB_DB, RJ_EVAL=FM.RJ.EVAL_DB, eval_ids=pool_guard.eval_ids,
                 apor=pool_guard.assert_pool_of_record, connect=sqlite3.connect)
    true_raw = FM._RAW_CONNECT
    root = os.path.abspath(td).replace("\\", "/").lower()

    def checked_raw(database, *a, **k):
        s = str(database).replace("\\", "/").lower()
        if root not in s:
            raise AssertionError("INERTNESS HARNESS: an sqlite open outside the replica: %s" % database)
        return true_raw(database, *a, **k)
    checked_raw._raw = checked_raw
    try:
        AF.EMB_DB, AF.EVAL_DB, F.EMB_DB, FM.RJ.EVAL_DB = rep["emb"], rep["ev"], rep["emb"], rep["ev"]
        pool_guard.eval_ids = lambda pid: rep["eval_ids"] if pid == FM.POOL_ID else saved["eval_ids"](pid)
        pool_guard.assert_pool_of_record = lambda pid, *a, **k: pid
        sqlite3.connect = checked_raw
        yield
    finally:
        AF.EMB_DB, AF.EVAL_DB, F.EMB_DB, FM.RJ.EVAL_DB = saved["AF_EMB"], saved["AF_EVAL"], saved["F_EMB"], saved["RJ_EVAL"]
        pool_guard.eval_ids, pool_guard.assert_pool_of_record = saved["eval_ids"], saved["apor"]
        sqlite3.connect = saved["connect"]


def _leg(src_bytes, td, rep, tag):
    """exec one rendering of flat_mix_mmlu.py in a fresh namespace inside the replica; run its modes; return outputs."""
    ns = {"__name__": "flat_mix_leg_" + tag, "__file__": os.path.join(HERE, "flat_mix_mmlu.py")}
    exec(compile(src_bytes.decode("utf-8"), "<flat_mix_%s>" % tag, "exec"), ns)
    AF.EMB_DB, AF.EVAL_DB, F.EMB_DB, ns["RJ"].EVAL_DB = rep["emb"], rep["ev"], rep["emb"], rep["ev"]   # the leg's import reset them
    pins = _pins_of_bytes(src_bytes)
    ns.update(DATA_ROOT=td, K=rep["leaves"], DIM=16, T_LEAVES=rep["leaves"], FIT_N=rep["fit_n"],
              script_pins=lambda: pins, OUT_DIR=os.path.join(td, "leg"))
    calls = {"assemble_res": 0, "fit_partition_default_k": 0, "embedding_guard_neutralised": 0}
    if "embedding_guard_flat" in ns:
        # EMBEDDER-PLUMBING (RP08) added a read-and-print (or refuse) guard to header(); the replica's 24-d vectors can never pass
        # its qwen3 native-dimension check, so on leg B it is replaced by a COUNTED no-op and the comparison covers everything
        # else. The guard's own branches are proved by embedder_guard.py / flat_mix_mmlu.py FT-EMBGUARD, not here (disclosed).
        def guard_noop(*a, **k):
            calls["embedding_guard_neutralised"] += 1
        ns["embedding_guard_flat"] = guard_noop
    if "assemble_res" in ns:
        inner = ns["assemble_res"]

        def counted(*a, **k):
            calls["assemble_res"] += 1
            return inner(*a, **k)
        ns["assemble_res"] = counted
        fp = ns["fit_partition"]

        def counted_fp(name, X, k=None, tree_kw=None):
            calls["fit_partition_default_k"] += int(k is None and tree_kw is None)
            return fp(name, X, k, tree_kw)
        ns["fit_partition"] = counted_fp
    out = {}
    sd = os.path.join(td, "leg", "state")

    rp08 = "EG" in ns                   # leg B carries EMBEDDER-PLUMBING's registered import (embedder_guard.py, pinned)

    def mask(x):
        for form in (json.dumps(os.path.abspath(td))[1:-1], td, td.replace("\\", "/"), os.path.abspath(td)):
            x = x.replace(form, "<REPLICA>")
        if rp08:                        # RP08's pin line of its own import, masked and COUNTED (disclosed by inertness())
            keep = [ln for ln in x.split(chr(10)) if "tools/analysis/embedder_guard.py" not in ln]
            calls["rp08_pin_lines_masked"] = calls.get("rp08_pin_lines_masked", 0) + (x.count(chr(10)) + 1 - len(keep))
            x = chr(10).join(keep)
        return x
    for mode, fn in (("dry", lambda: ns["dry_run"]()), ("run", lambda: ns["run"](state_dir=sd)),
                     ("analyze", lambda: ns["analyze"](state_dir=sd, outcome=os.path.join(td, "leg", "outcome.txt"),
                                                       arms_csv=os.path.join(td, "leg", "arms.csv"))),
                     ("identity", lambda: ns["identity_check"]())):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                rc = fn()
            except SystemExit as e:
                rc = "SystemExit: %s" % e
        out[mode] = (rc if not isinstance(rc, str) else mask(rc), mask(buf.getvalue().replace(ns["fmt_pins"](pins), "<SCRIPT PINS>")))
    with open(os.path.join(td, "leg", "outcome.txt"), "rb") as f:
        out["outcome"] = mask(f.read().decode("utf-8").replace(ns["fmt_pins"](pins), "<SCRIPT PINS>")).encode("utf-8")
    with open(os.path.join(td, "leg", "arms.csv"), "rb") as f:
        out["csv"] = f.read()
    parts = {}
    for fn_ in sorted(os.listdir(sd)):
        with open(os.path.join(sd, fn_), encoding="utf-8") as f:
            b = json.load(f)
        if fn_.startswith("part_"):
            parts[fn_] = mask(json.dumps({k: v for k, v in b.items() if k not in ("script", "cpu_s", "wall_s")}, sort_keys=True))
        else:
            if rp08 and isinstance(b.get("imports"), dict) and "embedder_guard.py" in b["imports"]:
                b = dict(b, imports={k: v for k, v in b["imports"].items() if k != "embedder_guard.py"})
                calls["rp08_meta_import_masked"] = calls.get("rp08_meta_import_masked", 0) + 1
            parts[fn_] = mask(json.dumps({k: v for k, v in b.items() if k != "script"}, sort_keys=True))
    out["state"] = parts
    out["calls"] = calls
    out["has_assemble_res"] = "assemble_res" in ns
    return out


def _norm(text):
    keep = []
    for line in text.splitlines():
        if line.startswith("[PIN] ") and " s (taken before" in line:
            continue
        if line.startswith("COST (SYNTHETIC"):
            continue
        if " fitted (" in line and " s wall" in line:
            line = line.split(" fitted (")[0] + " fitted (<wall>)"
        keep.append(line)
    return keep


def inertness():
    """flat_mix_mmlu.py's DEFAULT path (no new keyword given) at the base blob c5cc7934 vs this build, on the same replica."""
    print("pool %s (inertness: SYNTHETIC replica only; no DB of record is opened: every sqlite open outside the temp dir raises)"
          % POOL_OF_RECORD)
    print("[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    print("[SCRIPT] tools/analysis/flat_generality.py %s" % FM.fmt_pins(script_pins()))
    base = _git_blob(FLAT_MIX_BASE_BLOB)
    with open(os.path.join(HERE, "flat_mix_mmlu.py"), "rb") as f:
        cur = f.read().replace(b"\r\n", b"\n")
    print("LEG A: flat_mix_mmlu.py %s (git object, the FLAT-MIX-MMLU instrument of record)" % FM.fmt_pins(_pins_of_bytes(base)))
    print("LEG B: flat_mix_mmlu.py %s (this build's working tree)" % FM.fmt_pins(_pins_of_bytes(cur)))
    legs = {}
    guarded = sqlite3.connect
    try:
        ctl = cur.replace(b"BOOT_B, BOOT_SEED = 1000, 20260926", b"BOOT_B, BOOT_SEED = 1000, 20260927")
        if ctl == cur:
            refuse("the sensitivity control's mutation did not apply")
        for tag, src in (("A", base), ("B", cur), ("C", ctl)):
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:   # readers leave sqlite handles open (Windows)
                rep = _replica(td, np.random.default_rng(20260927))
                with _replica_env(td, rep):
                    legs[tag] = _leg(src, td, rep, tag)
                gc.collect()
    finally:
        sqlite3.connect = guarded
    A, B, Cc = legs["A"], legs["B"], legs["C"]
    ok = True
    print("  return codes (dry-run, run, analyze, identity-check): A %s | B %s (identity-check returns 1 on the replica in both: its "
          "numbers are not the record's)" % ([A[m][0] for m in ("dry", "run", "analyze", "identity")],
                                             [B[m][0] for m in ("dry", "run", "analyze", "identity")]))
    ok &= [A[m][0] for m in ("dry", "run", "analyze", "identity")] == [0, 0, 0, 1]

    def cmp(what, a, b, note=""):
        nonlocal ok
        same = a == b
        ok &= same
        print("  %-58s %s%s" % (what, "IDENTICAL" if same else "DIFFERENT", note))
        if not same:
            la_, lb_ = (json.dumps(a, sort_keys=True, default=str) if not isinstance(a, (bytes, str)) else str(a)),                        (json.dumps(b, sort_keys=True, default=str) if not isinstance(b, (bytes, str)) else str(b))
            i = next((j for j in range(min(len(la_), len(lb_))) if la_[j] != lb_[j]), min(len(la_), len(lb_)))
            print("    first difference at char %d: A ...%r... | B ...%r..." % (i, la_[max(0, i - 80):i + 80], lb_[max(0, i - 80):i + 80]))
    cmp("--run state: 12 partition bodies (minus script / cpu / wall)", A["state"], B["state"],
        " (%d files)" % len(A["state"]))
    cmp("--analyze outcome file (bytes; the script-pin string masked)", A["outcome"], B["outcome"], " (%d bytes)" % len(A["outcome"]))
    cmp("--analyze arms CSV (bytes)", A["csv"], B["csv"], " (%d bytes)" % len(A["csv"]))
    cmp("--dry-run stdout (timing lines masked)", (A["dry"][0], _norm(A["dry"][1])), (B["dry"][0], _norm(B["dry"][1])))
    cmp("--run stdout (wall times masked)", (A["run"][0], _norm(A["run"][1])), (B["run"][0], _norm(B["run"][1])))
    cmp("--identity-check stdout and rc", A["identity"], B["identity"])
    la, lb = _norm(A["analyze"][1]), _norm(B["analyze"][1])
    extra = [l for l in lb if l.startswith("[PIN before] ")]
    cmp("--analyze stdout minus leg B's '[PIN before]' lines (registered LOW fix)", (A["analyze"][0], la),
        (B["analyze"][0], [l for l in lb if not l.startswith("[PIN before] ")]))
    n_pin = sum(1 for l in la if l.startswith("[PIN after ] "))
    print("  --analyze: leg B prints %d '[PIN before]' lines beside the %d '[PIN after ]' lines (post-run review 643995a LOW); leg A %d"
          % (len(extra), n_pin, sum(1 for l in la if l.startswith("[PIN before] "))))
    ok &= len(extra) == n_pin and n_pin > 0
    print("  EXECUTION WITNESS: leg B called assemble_res %d time(s) and fit_partition through its k=None / tree_kw=None defaults %d "
          "time(s); leg A has assemble_res: %s" % (B["calls"]["assemble_res"], B["calls"]["fit_partition_default_k"], A["has_assemble_res"]))
    ok &= B["calls"]["assemble_res"] == 1 and B["calls"]["fit_partition_default_k"] == 12 and not A["has_assemble_res"]
    print("  RP08 DISCLOSURE (leg B only): embedding_guard_flat replaced by a counted no-op %d time(s) (the replica cannot pass the "
          "qwen3 native-dimension check; the guard is proved by its own selftests); embedder_guard.py pin lines masked %d, the meta "
          "imports entry masked %d time(s); leg A: %d / %d / %d" % (
              B["calls"].get("embedding_guard_neutralised", 0), B["calls"].get("rp08_pin_lines_masked", 0),
              B["calls"].get("rp08_meta_import_masked", 0), A["calls"].get("embedding_guard_neutralised", 0),
              A["calls"].get("rp08_pin_lines_masked", 0), A["calls"].get("rp08_meta_import_masked", 0)))
    ok &= A["calls"].get("embedding_guard_neutralised", 0) == 0 and A["calls"].get("rp08_pin_lines_masked", 0) == 0
    print("  outcome head (leg B): %s" % B["outcome"].decode("utf-8").splitlines()[0])
    sens = Cc["outcome"] != B["outcome"] and Cc["csv"] == B["csv"]
    print("  SENSITIVITY CONTROL (leg C = this build with BOOT_SEED 20260926 -> 20260927): outcome %s from leg B, arms CSV %s (the "
          "comparison is not vacuous: a one-constant change in the bootstrap is seen)" % ("DIFFERS" if Cc["outcome"] != B["outcome"] else
                                                                                         "IDENTICAL", "identical" if Cc["csv"] == B["csv"] else "differs"))
    ok &= sens
    print("INERTNESS %s" % ("PROVED: flat_mix_mmlu.py's default path is byte-identical to c5cc7934 on every output compared" if ok
                            else "FAILED"))
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--inertness", "--dry-run", "--identity-check", "--run", "--analyze"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--tree", choices=tuple(TREES), default=None)
    ap.add_argument("--max-chunks", type=int, default=None)
    a = ap.parse_args(argv)
    if a.selftest or a.mutants:
        print("pool %s (selftest: synthetic only; the pool is not read)" % POOL_OF_RECORD)
        print("[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
        print("[SCRIPT] tools/analysis/flat_generality.py %s" % FM.fmt_pins(script_pins()))
        print("[PIN] tools/analysis/flat_mix_mmlu.py %s (pinned on import; verified)" % FM.fmt_pins(FM.script_pins()))
        if a.mutants:
            return run_mutants()
        t0 = time.perf_counter()
        n = selftest()
        print("SELFTEST PASSED: %d checks (%.0f s)" % (n, time.perf_counter() - t0))
        return 0
    if a.inertness:
        return inertness()
    if a.dry_run:
        return dry_run()
    if a.identity_check:
        return identity_check()
    if a.run:
        return run(only=a.tree, max_chunks=a.max_chunks)
    return analyze()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
