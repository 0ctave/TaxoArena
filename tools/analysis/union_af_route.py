"""union_af_route.py: UNION-AF-ROUTE (RP13) -- the AF-cell arm, the per-source k-means comparator K_s, and the AF-VS-KMEANS
AK1 / AK2 reader, driving the v2 RP03 / G14 reader (v2_declared_cells.py). ZERO calls: no judge, no LLM, no embedding call, no
construction. Readers only.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins; spans _as_of 50c71784):
  docs/judge_v2_program.md "## Registered 2026-10-01 (before any code or call) — UNION-AF-ROUTE: on the content-closed v2 union
  split (draw 5a3e756), do the cells of a FRESH anchor-free, federated, TRAIN-only tree route ..." (L22627-L22653): U1, U2
  (= F-TAX L-1), U3a / U3b (TOST, delta 1.0pp, Holm), IDENTITY (+2.67pp [+1.46, +3.89]), Support (a)-(g), predictions, F-U1;
  and "## Registered 2026-10-02 (before any code or call) — UNION-AF-ROUTE, pre-data addition AF-VS-KMEANS: ..." (L23093-L23116):
  AK1, AK2, F-AK, AK-IDENTITY (B0: D_U +0.0738, D_Us +0.0656, spread_U 0.0414, spread_US 0.0233), Support (a)-(g), predictions.
  The F-TAX bracket of 2026-10-01 (L21573): an L-1 FIRE observed under U2 (DESCRIPTIVE-ONLY) counts; a non-fire is "not shown".
  Build TOMLs: experiment_configs/union_af_route/AF-U/ (branch union-af-tomls a994a722; not changed here).

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout; never beside a construction: every step below is a pool reader):
  0. python tools/analysis/union_af_route.py --selftest        # synthetic fixtures under tempfile; opens NO DB of record
     python tools/analysis/union_af_route.py --mutants         # the mutant table below, re-run
  1. (machine lane, rule 7) the AF-U build from the TOMLs (6 members, then the flatLeaf graft), one detached worktree, one commit.
  2. python tools/analysis/union_af_route.py --dry-run          # POOL line first; denominators; AK-IDENTITY on B0 (CPU, seen
                                                                #   numbers only); REFUSES while the AF-U outputs are ABSENT
  3. python tools/analysis/union_af_route.py --build-inputs     # B0-2 pool check; writes (write-once) under
       experiment_results/archv2/union_af_route/inputs/: af_u_bundle_256.{npz,json} (rp12_pairing.g13_bundle, dim 256),
       af_cells.tsv (R1), k_cells_s0..s4.tsv (R2-R4), inputs_manifest.json (every sha); reads multicorpus_cache_v1.db and
       embeddings_cache.db read-only (rp12_pairing's readers); no EVAL key, no statistic
  4. python tools/analysis/union_af_route.py --dry-run          # now with the inputs: pins, B0-2 pool check, the leg U dry-run
                                                                #   of v2_declared_cells with the AF and K arms (no key column)
  5. python tools/analysis/union_af_route.py --run              # ONE EVAL key read (B1 marker); outcome WRITE-ONCE:
       experiment_results/archv2/union_af_route/outcome.txt (+ union_af_route_train_policy.json, union_af_route.READ_STARTED)
  Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; write-once paths absent; B0-2 pool check (g13_breakdown.pool_check_v2: v2_union_pool.py --dry-run, the engine
      pool file's sha256-lf, 0-byte -wal / -journal); (2) the AF-U outputs present, one build commit across their
      run_manifest.json (D-8), every AF-U file and every input file equal to inputs_manifest.json; (3) AK-IDENTITY on B0's
      bundle (512-d, 133 leaves) reproduces the four registered strings, else [RP13-AK-IDENTITY]; (4) AK1 / AK2 / F-AK on AF-U's
      bundle (6,139 / 5,628, refused otherwise); the K_s centroids recomputed and the K-cells files re-derived (refused on any
      difference); (5) leg U's frozen TRAIN policy file (V2-DECLARED-CELLS) sha256 printed BEFORE EVAL opens (R3); (6)
      v2_declared_cells.mode(leg U) with cfg.tree = the AF cells, cfg.xtrees = K0..K4, cfg.tail = rp13_tail: C0, the B3 policy
      file (declared, AF and K arms frozen), the B1 marker, the EVAL key read, B = 2,000 two-stage replicates (default_rng(42));
      rp13_tail refuses unless the declared arm prints +2.67pp [+1.46pp, +3.89pp] ([RP13-IDENTITY]), the deciding set is 5,907
      items / 5,404 components ([RP13-DENOM]) and the declared policy equals leg U's frozen file ([RP13-R3]); then U1, U2, U3,
      F-U1, F-TAX lines, predictions, descriptive lines and the AK block; mode() writes the outcome write-once (mode "x").

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  R1  AF cell = the item's modal flatLeaf leaf_id over its routing rows (rp12_pairing P1's rule applied to leaf_id, i.e.
      g13_breakdown._modal_leaf: ties to the smallest id, an unrouted row counts as <unrouted>), NOT the leaf's TRAIN-majority
      name: the registration's "Cells: AF-U leaves" and its label-free claim (naming would merge leaves by declared class).
      G14's B0 arm used leaf_dominant; the two are never joined. Multi-class items keep their modal leaf (G14 ruling (b)); an
      item with no routing row is <no-routing-row> (TRAIN: fitted as its own cell; EVAL in the scoring set: [G14-NOROW]).
  R2  K_s fit set = the AF-U bundle's TRAIN items (MC-EXCLUDE'd; the AK fit set, 12,334 expected); k per source = the number of
      leaves in that member's LAST dag snapshot; a TRAIN item's source = the source of its declared class.
  R3  K_s cell of EVERY scored item (TRAIN and EVAL) = the nearest centroid (argmax cosine, 256-d unit rows) among the
      centroids of the item's declared source(s), read from its routing rows' true_key ("filed by source"); an item whose rows
      name two sources (the MATH / MMLU_PRO_LB multi-class items) is filed among both sources' centroids (kept, as G14 keeps
      them); no routing row -> <no-routing-row>. TRAIN items whose nearest-centroid cell differs from their final k-means
      label are counted and printed (they differ only where the fit stopped at max_iter).
  R4  The K_s fit is the call AK2 makes for US_s (g13_breakdown.ukm_fit per source, in the registered source order, seed s):
      U2's comparator and AK2 share their centroids; --run recomputes them and refuses if the K-cells files disagree.
  R5  G_K = mean over s = 0..4 of G_K,s; D_K = G_AF - G_K, paired inside the same two-stage replicates (arm weights +1 and
      -1/5 x 5); spread_K = max - min over s of the G_K,s points; deciding interval = point +- 1.96 SE_2stage (G14's reader
      form, v2_declared_cells.contrast); M_AF = G_AF - G_declared (TRUE (source, domain)).
  R6  U3 Holm over two TOSTs: TOST p = max of the two one-sided normal p-values with SE_2stage; the contrast with the smaller
      p is tested first at the two-sided 95% interval (z 1.96), the other at 90% (z 1.645) only if the first is EQUIVALENT
      (Holm stops otherwise); a tie in p puts U3a first; "inside +-1.0pp" is strict (an end point at +-1.0pp is outside).
      This is the reading under which Support (e) / (f) score U3b against 0.35pp (the first, 95% step).
  R7  F-TAX's "(lever leg not fired, by support) whenever U2 reads inside its bar": |D_K| <= max(MDE80 measured, spread_K).
  R8  AK1 k = AF-U's TOTAL snapshot leaf count (leaves without a TRAIN profile included); the count with a profile is printed
      beside; naming = TRAIN majority, tie to the smaller class name (g13_breakdown.majority); EVAL filed to the nearest of all
      centroids; AK2 primary = nearest of ALL centroids (no source oracle), within-true-source printed beside.
  R9  D_fd (descriptive) needs a descent graft; the AF-U TOMLs at a994a722 carry graft_flatleaf only, so D_fd prints
      "NOT COMPUTED" unless experiment_results/archv2/union_af_route/AF-U/graft_descent/seed_42/validation exists.
  R10 The declared arm's frozen TRAIN policy (best single, true_source_domain) must equal leg U's frozen file
      (experiment_results/archv2/v2_declared_cells/v2_declared_cells_U_train_policy.json), else [RP13-R3].
  R11 The B0-2 pool check replaces pool_guard.py for pv2 pools (programme L22165); it runs in --build-inputs, in --dry-run once
      the AF-U outputs exist, and in --run; the first printed line of every mode is the POOL line.
  R12 D-8: every AF-U run_manifest.json carries the same commit, else refused.
  Not applicable (stated): no judge verdict enters (key-scored end to end), so no wrong(established) count and no tie
  convention A / B; no call cache, --pilot or truncation guard (zero calls).

DEVIATION FROM THE REGISTRATION'S WORDING (stated): "the AF-cell arm and the K comparator in the v2 RP03/G14 reader, inert when
absent" is built as library hooks in v2_declared_cells.py (cfg.xtrees, cfg.tail; no CLI flag; byte-identical outputs when
absent, proved by the selftest case vdc_inert against blob c5b90278) driven by this file, which carries every RP13 line.

SELFTEST (--selftest; synthetic fixtures; the real entry points run() / dry_run() / build_inputs() executed on a complete
layout in a temp dir: v2_declared_cells' sealed fixture views (18 -> 9 models), AF-U member snapshots and graft CSVs with a
tie, an unrouted row, a no-row TRAIN item and a two-source multi-class EVAL item, the B0 identity on the same bundle;
rp12_pairing's text / vector / side readers and the pool check are stubbed, rp12_pairing.g13_bundle itself runs):
  branches       every U1 / U2 / U3 (Holm order, stop, 95% / 90%, strict end point) / F-U1 / F-TAX / AK1 / AK2 / F-AK branch and
                 prediction line asserted by VALUE (synthetic stats through u_lines / ak_lines, which the outcome prints verbatim);
                 tost_p and inside() against hand values
  branch_cover   the branch registry: every print branch hit (TOPIC-PARTITION D1 / D7)
  builders       R1 cells (modal leaf_id, the tie, <unrouted>, the no-row fill, the multi-class item kept, no declared name) and
                 R2-R4 K cells item by item against an independent oracle (direct per-source fits, filing by loops among the
                 allowed sources; the multi-class item lands on MMLU_PRO's centre); write-once refusals
  ak_e2e         AK1 / AK2 / F-AK against an independent oracle (P per seed, D, spreads, the bootstrap interval, the words)
  run_e2e        --run end to end: G_AF, G_K,s, G_K, spread_K, D_K, M_AF printed to 5 dp equal to independent plain-loop policy
                 accuracies; U1 / U2 words from the printed intervals by hand rules; the AK block values; the pre-read lines in
                 the outcome; a second --run refused with the outcome unchanged
  identity_tree  AF = the declared key and every K_s = the source: G_AF == C1, M_AF == 0 (U3b EQUIVALENT), G_K == the TRUE source
                 arm, spread 0, D_K == C1 - G_TSRC; the R4 refusal on hand-made K files; [G14-NOROW] for an extra arm; lin == contrast
  refusals       [RP13-IDENTITY], [RP13-AK-IDENTITY], [RP13-DENOM], [RP13-R3], changed pins, D-8, the pool check (POOL line still
                 first), the leaves CSV against the snapshots; no outcome written by any of them
  dry_run        AF-U ABSENT: POOL line first, the denominators, AK-IDENTITY, the refusal, nothing written; the REAL constants'
                 denominator lines (5907 / 5404, 6139 / 5628, 6153 / 5642, 12334, +2.67pp, the four AK strings); inputs absent;
                 inputs present: the leg U dry-run of v2_declared_cells with the arms, no statistic, nothing written
  desc           R9: D_fd with a descent graft against a hand value; NOT COMPUTED without
  vdc_inert      v2_declared_cells without cfg.xtrees / cfg.tail == blob c5b90278 on its fixture with a tree (G14 outcome line for
                 line, frozen policy key for key)
MUTANTS (--mutants; 63 + the X00 control; X* edit this file in memory, V* edit v2_declared_cells.py re-executed in the imported
module after the pin check, restored after each): 2026-10-02 at this commit 63 of 63 KILLED, control survived. First full pass
60 / 63: X11 (U2 reverse without its spread clause) and X23 (prediction bands exclusive at the ends) survived and were killed by
two added branch cases; the first V06 (an extra grouping fitted when only the tree is present) was an EQUIVALENT mutant (no
printed or frozen output reads it) and was replaced by V06 (an empty xtree_cell key frozen when absent), killed. The classes
(see MUTANTS for the exact edits): min<->max and seed-0-only (X01-X03), arm index / wrong arm / wrong population (X04-X06,
X29-X31), verdict boundaries (X07-X11, X18, X23, X25), Holm order / stop / z / TOST p / contrast (X12-X17), skip paths that drop
a required line (X21, X22, X26, X27, X56), zero items (X28), wrong split side (X32, X34), k (X33), R1-R4 rules (X35-X39), write-
once (X40, X41, X53), every refusal / gate (X42-X52), the outcome assembly (X54, X55), D_fd (X57), the vdc hooks (V01-V06).
NOT DONE HERE: the Kotlin suite (no JVM run: rule 7, the brief); the real --build-inputs / --run (no AF-U build exists).
[DELTA 2026-10-02 union-af-route, READY_union_af_route 502191e7 C-1..C-4, D-4, D-5; insertion only]
  C-4: R10 (r10_check) runs through v2_declared_cells' cfg.pre_eval right after the B3 policy file and BEFORE the EVAL view
  opens / the B1 marker; it compares EVERY policy key of leg U's frozen file (R10_KEYS: best single, true_source,
  true_source_domain, roster, TRAIN count, variant rule, key, tie-break, absent group); rp13_tail refuses if it did not run.
  C-1 / C-2 / C-3: refusals cases for one true_source_domain pick (best single equal; no marker written), a frozen extra-arm
  pick differing from the re-fit beside EVAL ([B3] ... extra arm), and the identity point equal with one interval end differing.
  D-4: u_lines prints the filing-information disclosure (K_s by TRUE source, AF-U flatLeaf over all leaves; against AF).
  D-5: the frozen TRAIN policy moved to experiment_results/archv2/union_af_route/scratch/union_af_route_train_policy.json (ignored
  by the existing scratch/ pattern; .gitignore NOT edited); --run REFUSES unless git check-ignore confirms it ignored and
  git ls-files shows it untracked; its sha256 is printed (B3 line) and it is never committed.
  New mutants: X58 (O1), X59 (O4), X60 (D-4 line), X61 (D-5 refusal), X62 (R10 not wired before EVAL), V07 (O2), V08 (pre_eval
  not called); X45 retargeted. MUTANTS: 70 of 70 KILLED, control survived (this commit).
[DELTA 2026-10-03 union-af-single-cell: THE AUTHOR's "one cell per unsplit member" (programme L23660-L23667, brackets L22633,
L22638, L22649, L23098); insertion only]
  DECLARATION experiment_results/archv2/union_af_route/AF-U/single_cell_members.json, appended by union_af_route_ops.py
  --member after a member's build refused as the anchor-free single leaf (absent = no one-cell member: every mode unchanged).
  single_evidence S1-S6 re-verifies every declared member from its outputDir (run_manifest anchor_free + the TOML's LF sha;
  the console log AF-U/<member>/build.log with the IllegalStateException and its siteId, read UTF-16 or UTF-8; no "Snapshot
  ID:"; proposals.csv: one GROW root site, every row NO_PROPOSAL min_pair_sep_below_bar with sep < the registered bar 0.025, no
  ACCEPTED / REJECTED row); the declared best_root_sep / n_site must equal the evidence. The real ifeval evidence of ops
  9a41adfe verifies (best 0.02111, n 325, 15 rows, root n00000001; checked on a temp copy, nothing written in main).
  GRAFT: the flatLeaf graft omits a one-cell member (union_af_route_ops.py --fill drops its placeholder and its corpus; the
  engine's assembleUnion requires corpora == the grafted sources and V2EnginePool.checkUnionMembers has no coverage
  requirement: NO engine change). The reader REFUSES a graft row or leaf of a one-cell source, writes inputs/
  validation_merged/ = the graft CSVs + one row per side item of the one-cell source (EVAL / GATE held-out, TRAIN), filed to
  its cell "<SOURCE>:<root>" and named by the TRAIN-majority declared class of its TRAIN side items, pins them in the manifest,
  and builds the bundle, the AF cells and the K cells from it. ksrc = 1 for the member (U2 / U3a K_s and AK2 US_s at k = 1;
  AK1's total k counts 1). The outcome prints single_lines (the member, its best root separation, n, the cell, and the
  filing-by-source disclosure) in the U block and in the AK block; ONE-CELL MEMBERS: none when the declaration is absent.
  New selftest cases single_e2e and single_refusals; mutants X63-X78 (results in the commit message of this delta).
[DELTA 2026-10-03 union-af-mirror: C-S1 / C-S2 of READY_union_af_single_cell, bracketed pre-data at programme L23098 / L23664
(d3653625; record L23669-L23674); insertion only]
  C-S1: with a one-cell source, the MIRRORED comparators decide AK1 / AK2 (ak_mirrored): AK1's U_s at k = L - |one-cell| on the
  other sources' TRAIN, each one-cell source's EVAL items filed to its own k = 1 centroid (named by its TRAIN majority) that no
  other item can reach; AK2's US_s with the one-cell source's items filed to its single centroid and that centroid excluded
  from every other item's search. The registered nearest-of-all AK1 / AK2 (P per seed, spread, D with its interval) are printed
  beside, DESCRIPTIVE. Spreads, verdicts, F-AK and the predictions read the mirrored values. Without a one-cell source nothing
  changes (R["mirrored"] False; ak_e2e, run_e2e, the B0 AK-IDENTITY unchanged).
  C-S2: single_lines' disclosure says like with like holds in k, filing is mirrored in AK1 / AK2 only, U2 / U3a's K_s files by
  true source as registered (D-4 for the others), no wider claim.
  Selftest: single_e2e checks the mirrored DECIDES lines against an independent loop oracle (_oracle_ak_mirror), the
  DESCRIPTIVE lines against the registered oracle, that the two differ on the fixture, the AK2 verdict from the mirrored interval,
  and the C-S2 words. Mutants X79 (nearest-of-all decides), X80-X82 (mirror defects), X83 (old disclosure), X84 (beside line
  omitted); X33 retargeted.
"""
import os
import sys

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import io
import json
import math
import hashlib
import argparse
import contextlib
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[RP13]"
TEST_ID = "UNION-AF-ROUTE"


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


PINS = (("g13_breakdown.py", "c29fa1c3d3b7837ede6c53f1b98bf32dcd97ca40"),
        ("g13_comparator.py", "61d83ec7dfed00b834d5b2e5d0ca355d236520db"),
        ("rp12_pairing.py", "35214b3f11c3ffe4c1174885316f89775442f5c3"),
        ("v2_declared_cells.py", "f0f568057995b5d0231da6e3d0d48755a7cf8386"))
for _name, _pin in PINS:
    _p = os.path.join(HERE, _name)
    if blob_lf(_p) != _pin:
        refuse("%s is blob:%s, not the pinned blob:%s" % (_p, blob_lf(_p), _pin))
import g13_breakdown as GB      # noqa: E402  (checks its own pins: g13_comparator, rp12_pairing, rp12_lane)
import g13_comparator as GC     # noqa: E402
import rp12_pairing as RP       # noqa: E402
import v2_declared_cells as V   # noqa: E402
FM = GC.FM
# flat_mix_mmlu (imported through g13_comparator) replaces sqlite3.connect at import with ITS test's guard, which admits only
# its own four DBs; this reader opens the v2 views and rp12_pairing's text / vector DBs, always through data_v2.ro.open_ro
# (mode=ro, immutable=1, after the -wal / -journal refusal). The raw connect is restored here and the fact printed in header().
import sqlite3                  # noqa: E402
SQLITE_GUARD_REMOVED = hasattr(sqlite3.connect, "_raw")
sqlite3.connect = getattr(sqlite3.connect, "_raw", sqlite3.connect)

REG_U = ('docs/judge_v2_program.md "## Registered 2026-10-01 (before any code or call) — UNION-AF-ROUTE: on the content-closed'
         ' v2 union split (draw 5a3e756), ..." L22627-L22653 (_as_of 50c71784)')
REG_AK = ('docs/judge_v2_program.md "## Registered 2026-10-02 (before any code or call) — UNION-AF-ROUTE, pre-data addition'
          ' AF-VS-KMEANS: ..." L23093-L23116 (_as_of 50c71784)')
POOL = "pv2_1575de61bb20e977"
RES = "experiment_results/archv2/union_af_route"
SEEDS = (0, 1, 2, 3, 4)
NO_ROW = RP.NO_ROW
UNROUTED = RP.UNROUTED

# ── the registered constants (one dict; the selftest swaps in its fixture's; nothing else writes _REG) ─────────────────────
REG = dict(
    pool=POOL, test=TEST_ID,
    members=(("bbh", "BBH"), ("gpqa", "GPQA"), ("ifeval", "IFEVAL"), ("math", "MATH"), ("mmlu_pro_lb", "MMLU_PRO_LB"), ("musr", "MUSR")),
    sources=("MMLU_PRO_LB", "BBH", "MATH", "MUSR", "IFEVAL", "GPQA"),
    dim=256,
    afu=RES + "/AF-U", inputs=RES + "/inputs",
    out=RES + "/outcome.txt", policy=RES + "/scratch/union_af_route_train_policy.json", marker=RES + "/union_af_route.READ_STARTED",
    leg_u_policy="experiment_results/archv2/v2_declared_cells/v2_declared_cells_U_train_policy.json",
    # U1-U3 deciding set (Support (a)) and the declared identity (V2-DECLARED-CELLS C1 of record)
    n_route=5907, comp_route=5404, identity=("+2.67pp", "+1.46pp", "+3.89pp"),
    # AK deciding set (AF-VS-KMEANS Support (a)); before MC-EXCLUDE 6,153 / 5,642 (the bundle's expectation)
    n_fl=6139, comp_fl=5628, n_eval_before=6153, comp_before=5642, n_train_fit=12334,
    # AK-IDENTITY on B0 (G13-BREAKDOWN B1 / B2, blob:3ca9629b outcome lines 38-39)
    b0_bundle="experiment_results/archv2/rp12_r2/B0/readouts/g13_bundle_flatleaf", b0_dir="experiment_results/archv2/rp12_r2/B0",
    b0_ksrc={"MMLU_PRO_LB": 74, "BBH": 36, "MATH": 9, "MUSR": 6, "IFEVAL": 5, "GPQA": 3}, b0_dim=512,
    ak_identity=dict(d_u="+0.0738", d_us="+0.0656", spread_u="0.0414", spread_us="0.0233"),
    delta=0.010, b0_g_tree="+2.62pp [+1.43, +3.82]", b0_p_fl="0.8119",
    # THE AUTHOR's "one cell per unsplit member" (2026-10-03, programme L23660-L23667): the declaration union_af_route_ops.py
    # writes after a member's verified single-leaf refusal; the registered bar it is checked against; the member TOMLs of record
    single_decl=RES + "/AF-U/single_cell_members.json", bar=0.025, tomls="experiment_configs/union_af_route/AF-U",
)
_REG = [REG]


def reg():
    return _REG[0]


# Support (registered planning numbers, printed beside the measured ones)
SUPPORT_U = dict(U1=dict(se=0.0061, mde=0.0171, deff=1.392, n_eff=4244),
                 U2=dict(se=0.0033, mde=0.0091, spread=0.005),
                 U3=dict(hw1=0.0065, hw2=0.0054))
SUPPORT_AK = dict(AK1=dict(se=0.00597, deff=1.341, n_eff=4578, mde=0.0167, spread=0.0414),
                  AK2=dict(se=0.00609, deff=1.449, n_eff=4237, mde=0.0171, spread=0.0233))
# PREDICTIONS (registrar's priors): "X [lo, hi]" HELD iff the point lies in [lo, hi], endpoints inclusive
PRED_U = {"U1 G_AF = +2.4pp [+1.2, +3.6]": (0.012, 0.036), "U2 D_K = +0.1pp [-0.8, +1.0]": (-0.008, 0.010),
          "U2 spread_K = 0.5pp [0.2, 1.0]": (0.002, 0.010), "U3b M_AF = -0.2pp [-1.0, +0.6]": (-0.010, 0.006)}
PRED_LEAVES = (70, 110)
PROB_U = {"U1": "HELD 0.85", "L-1": "fires 0.10", "U3a": "EQUIVALENT 0.45", "U3b": "EQUIVALENT 0.40"}
PRED_AK = {"P_fl(AF-U) 0.71 [0.64, 0.78]": ("p_fl", (0.64, 0.78)), "P(U_0) 0.73 [0.69, 0.77]": ("p_u0", (0.69, 0.77)),
           "P(US_0) 0.74 [0.70, 0.78]": ("p_us0", (0.70, 0.78)), "AK1 D_AU -0.015 [-0.050, +0.020]": ("d_au", (-0.050, 0.020)),
           "AK1 spread_AU 0.035 [0.015, 0.060]": ("spread_au", (0.015, 0.060)),
           "AK2 D_AUs -0.020 [-0.055, +0.015]": ("d_aus", (-0.055, 0.015)),
           "AK2 spread_AUs 0.025 [0.010, 0.045]": ("spread_aus", (0.010, 0.045))}
PROB_AK = {"AK1": "HELD 0.10, REVERSED 0.25, UNDETERMINED 0.65", "AK2": "HELD 0.10, REVERSED 0.35, UNDETERMINED 0.55",
           "F-AK": "fires 0.70"}

# hooks the selftest swaps (nothing else writes them)
_ROOT = [os.environ.get("TAXOARENA_RESULTS_ROOT", ROOT)]   # experiment_results/ and experiment_configs/ are read under it
_POOL = [GB.pool_check_v2]
_VDC_CFG = [V.real_cfg]
HIT = Counter()


def hit(name):
    HIT[name] += 1


def P(rel):
    return os.path.join(_ROOT[0], *rel.split("/"))


def src_of(name):
    return str(name).split("/", 1)[0]


def in_band(x, band):
    return band[0] <= x <= band[1]


def pp(x):
    return "%+.2fpp" % (100.0 * x)


# ── AF-U layout ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def afu_paths(single=()):
    """The AF-U files every mode needs. A ONE-CELL member (the author's decision 2026-10-03; declared in single_decl and
    verified by single_evidence) needs its refusal evidence (proposals.csv, headless_run.log and the console log the operator
    tees to AF-U/<member>/build.log: the engine's IllegalStateException goes to the console, not to headless_run.log, ops
    9a41adfe build_ifeval.log L232) instead of a snapshot."""
    c = reg()
    snaps, mans = [], []
    for m, src in c["members"]:
        base = "%s/%s/seed_42" % (c["afu"], m)
        if src in single:
            snaps += [("%s ONE-CELL proposals" % src, base + "/diagnostics/proposals.csv"), ("%s ONE-CELL log" % src, base + "/headless_run.log"),
                      ("%s ONE-CELL console" % src, "%s/%s/build.log" % (c["afu"], m))]
        else:
            snaps.append(("%s snapshot" % src, base + "/dag_snapshots.jsonl"))
        mans.append(("%s run_manifest" % src, base + "/diagnostics/run_manifest.json"))
    val = "%s/graft_flatleaf/seed_42/validation" % c["afu"]
    csvs = [("graft " + nm, "%s/%s" % (val, nm)) for nm in (RP.QUERIES, RP.TRAIN, RP.LEAVES)]
    gman = [("graft run_manifest", "%s/graft_flatleaf/seed_42/diagnostics/run_manifest.json" % c["afu"])]
    return snaps + mans + csvs + gman, val


# ── ONE-CELL members (THE AUTHOR's "one cell per unsplit member", 2026-10-03; programme L23660-L23667) ───────────────────
REFUSAL_LINE = "[ANCHOR-FREE] construction ended with the root as a single leaf"
SNAPSHOT_LINE = "Snapshot ID:"
SEP_RE = r"^min_pair_sep_below_bar\(sep=([0-9.]+),bar=([0-9.]+),"


def read_text(path):
    """A log as text: UTF-16 when it starts with a BOM (Windows PowerShell 5.1's Tee-Object / Out-File default), else UTF-8."""
    raw = open(path, "rb").read()
    if raw[:2] in (bytes([255, 254]), bytes([254, 255])):
        return raw.decode("utf-16", errors="replace")
    return raw.decode("utf-8-sig", errors="replace")


def single_evidence(member, src):
    """S1-S6: the member's build refused as the anchor-free single leaf for the registered reason, else REFUSES.
    S1 run_manifest: anchor_free true and split_v2.config_sha256_lf = the LF sha of the member's AF-U TOML of record;
    S2 the console log AF-U/<member>/build.log carries the [ANCHOR-FREE] single-leaf IllegalStateException naming the root's
       siteId, and NEITHER it NOR headless_run.log carries a "Snapshot ID:" line (no snapshot was saved);
    S3 proposals.csv has >= 1 row and NO row ACCEPTED or REJECTED anywhere;
    S4 every row is GROW at ONE site (the root), labelled with the member's source, one n_site;
    S5 every row is NO_PROPOSAL with reason min_pair_sep_below_bar(sep=s, bar=b, ...), b = the registered bar, s < b;
    S6 -> dict(member, source, root, cell "<SOURCE>:<root>", best_sep = max s, n_site, rows)."""
    import csv
    import re
    c = reg()
    base = "%s/%s/seed_42" % (c["afu"], member)
    man = json.load(open(P(base + "/diagnostics/run_manifest.json"), encoding="utf-8"))
    toml = P("%s/%s.toml" % (c["tomls"], member))
    want = sha256_lf(toml) if os.path.isfile(toml) else None
    got = (man.get("split_v2") or {}).get("config_sha256_lf")
    if man.get("anchor_free") is not True or got is None or got != want:
        refuse("ONE-CELL %s: S1 run_manifest anchor_free %r, config_sha256_lf %s vs the TOML %s's %s" % (
            member, man.get("anchor_free"), got, c["tomls"] + "/" + member + ".toml", want))
    log = read_text(P(base + "/headless_run.log"))
    con = read_text(P("%s/%s/build.log" % (c["afu"], member)))
    sm = re.search(re.escape(REFUSAL_LINE) + r".*?siteId=([A-Za-z0-9_]+)\)", con)
    if sm is None or SNAPSHOT_LINE in log or SNAPSHOT_LINE in con:
        refuse("ONE-CELL %s: S2 the console log %s the single-leaf refusal (with its siteId) and %s a saved snapshot" % (
            member, "carries" if sm else "LACKS", "names" if (SNAPSHOT_LINE in log or SNAPSHOT_LINE in con) else "no"))
    with open(P(base + "/diagnostics/proposals.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or any(r["decision"] in ("ACCEPTED", "REJECTED") for r in rows):
        refuse("ONE-CELL %s: S3 proposals.csv has %d rows, %d ACCEPTED / REJECTED (a proposal was offered: not the single-leaf case)"
               % (member, len(rows), sum(1 for r in rows if r["decision"] in ("ACCEPTED", "REJECTED"))))
    sites = {(r["type"], r["site_id"], r["site_label"], r["n_site"]) for r in rows}
    if len(sites) != 1 or list(sites)[0][0] != "GROW" or list(sites)[0][2] != src:
        refuse("ONE-CELL %s: S4 rows at %d (type, site, label, n) combinations %s, not one GROW root site labelled %s" % (
            member, len(sites), sorted(sites)[:3], src))
    seps = []
    for r in rows:
        m_ = re.match(SEP_RE, r["reason"])
        if r["decision"] != "NO_PROPOSAL" or not m_ or abs(float(m_.group(2)) - c["bar"]) > 1e-9 or not float(m_.group(1)) < float(m_.group(2)):
            refuse("ONE-CELL %s: S5 row %s / %r is not NO_PROPOSAL min_pair_sep_below_bar with sep < bar = %s" % (
                member, r["decision"], r["reason"], c["bar"]))
        seps.append(float(m_.group(1)))
    _t, root, _l, n = list(sites)[0]
    if sm.group(1) != root:
        refuse("ONE-CELL %s: S4 the console's refusal names siteId %s, proposals.csv's root is %s" % (member, sm.group(1), root))
    hit("SINGLE.VERIFIED")
    return dict(member=member, source=src, root=root, cell="%s:%s" % (src, root), best_sep=max(seps), n_site=int(n), rows=len(rows))


def declared_single():
    """The declaration (written by union_af_route_ops.py --member) -> {source: entry}; absent file = no one-cell member."""
    c = reg()
    dp = P(c["single_decl"])
    if not os.path.isfile(dp):
        return {}
    decl = json.load(open(dp, encoding="utf-8"))
    names = dict(c["members"])
    out = {}
    for e in decl.get("members", []):
        m, src = e.get("member"), e.get("source")
        if names.get(m) != src or src in out:
            refuse("ONE-CELL declaration %s: member %r / source %r is not a registered member (or repeated)" % (c["single_decl"], m, src))
        out[src] = e
    if len(out) >= len(c["members"]):
        refuse("ONE-CELL declaration: every member is declared one-cell; there is no graft to read")
    return out


def load_single(say, decl):
    """Every declared one-cell member verified by its evidence (single_evidence) -> {source: evidence}."""
    c = reg()
    out = {}
    for src, e in sorted(decl.items()):
        m = e["member"]
        ev = single_evidence(m, src)
        if "%.5f" % ev["best_sep"] != "%.5f" % float(e.get("best_root_sep", -1)) or ev["n_site"] != int(e.get("n_site", -1)):
            refuse("ONE-CELL declaration %s: %s declares best_root_sep %s / n_site %s, the evidence gives %.5f / %d" % (
                c["single_decl"], m, e.get("best_root_sep"), e.get("n_site"), ev["best_sep"], ev["n_site"]))
        out[src] = ev
    say("  ONE-CELL members (declaration %s sha256-lf %s): %s" % (c["single_decl"], sha256_lf(P(c["single_decl"]))[:16], "; ".join(
        "%s (member %s): best root separation %.5f < bar %s, n %d, %d NO_PROPOSAL rows, cell %s" % (
            s, e["member"], e["best_sep"], c["bar"], e["n_site"], e["rows"], e["cell"]) for s, e in sorted(out.items())) or "none"))
    return out


def single_lines(single):
    """The outcome's disclosure of the one-cell members (printed in the U block and in the AK block)."""
    c = reg()
    if not single:
        hit("SINGLE.NONE")
        return ["ONE-CELL MEMBERS: none (every member's anchor-free root cleared the bar %s)" % c["bar"]]
    hit("SINGLE.LISTED")
    out = ["ONE-CELL MEMBERS (THE AUTHOR's \"one cell per unsplit member\", 2026-10-03, programme L23660-L23667; a BUILD RESULT,"
           " never a criterion):"]
    for s, e in sorted(single.items()):
        out.append("  %s (member %s): no anchor-free split clears the bar (best root separation %.5f < %s, n %d; every root GROW row"
                   " NO_PROPOSAL min_pair_sep_below_bar); counts 1 leaf (cell %s)" % (s, e["member"], e["best_sep"], c["bar"], e["n_site"], e["cell"]))
    out.append("  DISCLOSURE: the flatLeaf graft omits a one-cell member; its items are filed to its one cell BY SOURCE, so no item of"
               " another source can be filed to it and none of its items to another member's leaf. Like with like holds IN k: K_s"
               " (U2 / U3a) and US_s (AK2) run at k = 1 there and U_s (AK1) counts its one cell in the total k. In FILING, AF-U's"
               " by-source filing IS MIRRORED in AK1 / AK2 only (C-S1: the comparator files the source to its single centroid, which no"
               " other item can reach; the registered nearest-of-all values printed beside, DESCRIPTIVE); U2 / U3a's K_s files every"
               " item by its true source as registered (symmetric for this source; D-4 stands for the others). No wider like-with-like"
               " claim (C-S2)")
    return out


def side_strata(path=None):
    """{item: (stratum_source, stratum_domain)} from the committed side export (read after EP.read_side verified it)."""
    path = path or os.path.join(ROOT, RP.EP.DEFAULT_SIDE)
    RP.EP.read_side(path)
    out = {}
    with open(path, encoding="utf-8") as f:
        for i, ln in enumerate(f):
            if i < 2:
                continue
            parts = ln.rstrip("\r\n").split("\t")
            if len(parts) == 6 and RP.UNION_CORPUS in parts[5].split(","):
                out[parts[0]] = (parts[3], parts[4])
    return out


_STRATA = [side_strata]


def merged_validation(val, dest, single, side, strata):
    """Write dest/{queries, train_queries, leaves}.csv = the graft's CSVs plus one routing row per side item of every one-cell
    source (EVAL and GATE to the held-out file, TRAIN to the TRAIN file), filed to its one cell; the cell's name is the TRAIN-
    majority declared class of the source's TRAIN side items (tie to the smaller name). REFUSES if the graft carries a row or a
    leaf of a one-cell source. -> {source: (n held-out, n TRAIN, majority)}."""
    import csv
    info, loaded = {}, {}
    for nm in (RP.QUERIES, RP.TRAIN, RP.LEAVES):                 # every graft file checked BEFORE anything is written
        with open(os.path.join(val, nm), encoding="utf-8", newline="") as f:
            rd = csv.DictReader(f)
            loaded[nm] = (rd.fieldnames, list(rd))
        for r in loaded[nm][1]:
            k = r.get("true_key") or ""
            if src_of(k) in single or src_of(r.get("leaf_id", "")).split(":")[0] in single or r.get("leaf_id", "").split(":")[0] in single:
                hit("REFUSE.SINGLE_IN_GRAFT")
                refuse("the graft's %s carries a row of a one-cell source (%s / %s): the graft must omit it" % (nm, k, r.get("leaf_id")))
    os.makedirs(dest, exist_ok=True)
    for nm in (RP.QUERIES, RP.TRAIN, RP.LEAVES):
        head, rows = loaded[nm]
        add = []
        for s, e in sorted(single.items()):
            tr = sorted(it for it, (_c, sd) in side.items() if sd == "TRAIN" and strata.get(it, ("",))[0] == s)
            cnt = Counter("%s/%s" % strata[it] for it in tr)
            if not cnt:
                refuse("one-cell source %s has no TRAIN side item" % s)
            top = max(cnt.values())
            maj = min(k for k, v in cnt.items() if v == top)
            want = ("TRAIN",) if nm == RP.TRAIN else ("EVAL", "GATE")
            its = sorted(it for it, (_c, sd) in side.items() if sd in want and strata.get(it, ("",))[0] == s)
            if nm == RP.LEAVES:
                add.append({"leaf_id": e["cell"], "leaf_label": s, "leaf_depth": "1", "profile_size": str(len(tr)), "leaf_dominant": maj,
                            "leaf_purity": "%.4f" % (top / len(tr))})
                continue
            for it in its:
                key = "%s/%s" % strata[it]
                row = {h: "" for h in head}
                row.update(true_key=key, true_source=s, rule="one-cell", leaf_id=e["cell"], leaf_label=s, leaf_depth="1",
                           leaf_dominant=maj, routed_source=s, routed_domain=maj, top1=str(int(maj == key)), source_ok="1",
                           domain_ok=str(int(maj == key)), item_id=it)
                add.append({h: row.get(h, "") for h in head})
            prev = info.get(s, (0, 0, maj))
            info[s] = (len(its), prev[1], maj) if nm == RP.QUERIES else (prev[0], len(its), maj)
        with open(os.path.join(dest, nm), "x", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=head, lineterminator="\n")
            w.writeheader()
            for r in rows + add:
                w.writerow(r)
    hit("SINGLE.MERGED")
    return info


def input_paths():
    c = reg()
    d = c["inputs"]
    return dict(bundle=d + "/af_u_bundle_256", af=d + "/af_cells.tsv", k={s: d + "/k_cells_s%d.tsv" % s for s in SEEDS},
                manifest=d + "/inputs_manifest.json", merged=d + "/validation_merged")


def presence(pairs):
    return [(lab, rel, os.path.isfile(P(rel))) for lab, rel in pairs]


def leaf_counts(base, members):
    """{source: number of leaves in the member's LAST dag snapshot} and {source: set of union leaf ids "<SOURCE>:<id>"}."""
    counts, ids = {}, {}
    for m, src in members:
        snap = GB.last_snapshot(P("%s/%s/seed_42/dag_snapshots.jsonl" % (base, m)))
        lv = ["%s:%s" % (src, n["id"]) for n in snap["nodes"] if n.get("isLeaf")]
        if not lv:
            refuse("member %s's last snapshot has no leaf" % m)
        counts[src], ids[src] = len(lv), set(lv)
    return counts, ids


def build_commits(pairs):
    """D-8 (R12): every AF-U run_manifest.json names the same commit -> (commit, {label: commit})."""
    got = {}
    for lab, rel in pairs:
        if lab.endswith("run_manifest"):
            got[lab] = str(json.load(open(P(rel), encoding="utf-8")).get("commit"))
    if len(set(got.values())) != 1:
        refuse("D-8: the AF-U run manifests name %d commits %s (one detached worktree pinned at one commit is registered)"
               % (len(set(got.values())), sorted(set(got.values()))))
    return list(got.values())[0], got


# ── the AF-cell arm (R1) and the K comparator (R2-R4) ────────────────────────────────────────────────────────────────────

def af_cells(validation, side):
    """R1: {item: modal flatLeaf leaf_id} for every side item tagged with the union corpus on TRAIN or EVAL; counts."""
    rows_h, rows_t = RP.read_rows(os.path.join(validation, RP.QUERIES)), RP.read_rows(os.path.join(validation, RP.TRAIN))
    held, _d_h, _u_h, m_h = RP.item_cells(rows_h)
    trn, _d_t, _u_t, m_t = RP.item_cells(rows_t)
    ev, tr, cnt = RP.split_items(held, trn, side)                 # P3's split-defect refusals
    ex = RP.multi_by_side(m_h, m_t, side)
    lh, lt = GB.item_leaves(rows_h), GB.item_leaves(rows_t)
    cells = {}
    for it in list(ev) + list(ex["EVAL"]):
        cells[it] = lh[it][0]
    for it in list(tr) + list(ex["TRAIN"]):
        cells[it] = lt[it][0]
    filled = {"EVAL": 0, "TRAIN": 0}
    for it, (_c, s) in side.items():
        if s in ("TRAIN", "EVAL") and it not in cells:
            cells[it] = NO_ROW
            filled[s] += 1
    counts = dict(eval_routed=len(ev) + len(ex["EVAL"]), train_routed=len(tr) + len(ex["TRAIN"]), no_row_eval=filled["EVAL"],
                  no_row_train=filled["TRAIN"], multi_eval=len(ex["EVAL"]), multi_train=len(ex["TRAIN"]),
                  gate_rows=cnt["held_gate"], unrouted=sum(1 for v in cells.values() if v == UNROUTED))
    return cells, counts


def item_sources(rows):
    """R3: {item: sorted declared sources of its routing rows (true_key)}."""
    by = defaultdict(set)
    for r in rows:
        by[r["item_id"]].add(src_of(r["true_key"]))
    return {it: sorted(s) for it, s in by.items()}


def us_fit(Xt, tsrc, ksrc, sources, seed):
    """R2 / R4: the per-source spherical k-means of AK2's US_s (g13_breakdown.ukm_fit, the registered source order, seed s).
    -> (centres (K, d), centre source (K,), local index (K,), final fit label of every TRAIN row (global centre index), fits)."""
    cents, csrc, cloc, fits = [], [], [], {}
    lab = np.full(len(Xt), -1, dtype=np.int64)
    off = 0
    for so in sources:
        m = tsrc == so
        k = int(ksrc.get(so, 0))
        if k < 1:
            refuse("source %s: k = %d (every registered source needs at least one leaf)" % (so, k))
        if k > int(m.sum()):
            refuse("source %s: k %d exceeds its %d TRAIN items" % (so, k, int(m.sum())))
        fit, _t = GB.ukm_fit(Xt[m], k, seed)
        fits[so] = fit
        cents.append(fit["centers"])
        csrc.extend([so] * k)
        cloc.extend(range(k))
        lab[np.flatnonzero(m)] = fit["labels"] + off
        off += k
    extra = sorted(set(tsrc.tolist()) - set(sources))
    if extra:
        refuse("TRAIN items of unregistered source(s) %s" % extra)
    return np.vstack(cents), np.array(csrc), np.array(cloc), lab, fits


def file_by_source(x, srcset, C, csrc):
    """R3: the global index of the nearest centre among the centres of the item's declared source(s)."""
    s = C @ x
    allowed = np.isin(csrc, list(srcset))
    if not allowed.any():
        refuse("an item's declared source(s) %s have no centre" % (srcset,))
    return int(np.flatnonzero(allowed)[np.argmax(s[allowed])])


def k_cells(seed, Xt, tsrc, titems, ksrc, sources, vec, srcs, cells_af):
    """R2-R4: {item: "K<s>:<SOURCE>:<j>"} over the same items as the AF cells (no-row items keep <no-routing-row>); counts."""
    C, csrc, cloc, lab, _f = us_fit(Xt, tsrc, ksrc, sources, seed)
    out, moved = {}, 0
    tpos = {it: j for j, it in enumerate(titems)}
    for it, afc in cells_af.items():
        if afc == NO_ROW:
            out[it] = NO_ROW
            continue
        if it not in vec:
            refuse("item %s has a routing row but no vector" % it)
        if it not in srcs:
            refuse("item %s has no declared source" % it)
        g = file_by_source(vec[it], srcs[it], C, csrc)
        out[it] = "K%d:%s:%03d" % (seed, csrc[g], cloc[g])
        if it in tpos and int(lab[tpos[it]]) != g:
            moved += 1
    return out, dict(moved_train=moved, centres=len(C))


def cells_text(cells, header):
    return "# %s %s\nitem_id\ttree_cell\n" % (V.TREE_CELLS_FORMAT, header) + "".join("%s\t%s\n" % (i, cells[i]) for i in sorted(cells))


def write_x(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def unit_bundle(b):
    return (FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64)), np.asarray(b["train_y"], dtype=int),
            FM.unit_rows(np.asarray(b["eval_X"], dtype=np.float64)), np.asarray(b["eval_y"], dtype=int))


# ── AK (AF-VS-KMEANS) ───────────────────────────────────────────────────────────────────────────────────────────────────

def ak_mirrored(Xt, yt, tsrc, Xe, esrc, L, ksrc, sources, single, classes, s):
    """C-S1 (programme L23098 bracket, d3653625): the k-means comparators with a one-cell source filed AS AF-U FILES IT.
    AK1 U_s: spherical k-means at k = L - (number of one-cell sources) on the OTHER sources' TRAIN items (AF-U's split members
    never saw a one-cell source's items), TRAIN-majority naming, the other EVAL items filed to the nearest of those centroids; each
    one-cell source's EVAL items filed to its own k = 1 centroid (named by its TRAIN majority), which no other item can reach.
    AK2 US_s: the registered per-source fits (the one-cell source at k = 1); a one-cell source's EVAL items filed to its centroid,
    every other item to the nearest centroid EXCLUDING the one-cell sources'. -> (predicted class index for AK1, for AK2)."""
    one = np.isin(tsrc, list(single))
    eone = np.isin(esrc, list(single))
    k_rest = L - len(single)
    if k_rest < 1 or k_rest > int((~one).sum()):
        refuse("C-S1: AK1's mirrored k %d for the split members is out of range" % k_rest)
    fit, _t = GB.ukm_fit(Xt[~one], k_rest, s)
    lab = GB.name_clusters(fit["labels"], k_rest, yt[~one], classes)
    p1 = lab[np.argmax(Xe @ fit["centers"].T, axis=1)]
    for so in sorted(single):
        m = tsrc == so
        GB.ukm_fit(Xt[m], 1, s)                                   # k = 1: the source centroid (named, filed by source)
        p1[esrc == so] = GB.majority(yt[m], classes)
    C, csrc, _cl, _lab, fits = us_fit(Xt, tsrc, ksrc, sources, s)
    names = np.concatenate([GB.name_clusters(fits[so]["labels"], int(ksrc[so]), yt[tsrc == so], classes) for so in sources])
    S = np.where(np.isin(csrc, list(single))[None, :], -np.inf, Xe @ C.T)
    p2 = names[np.argmax(S, axis=1)]
    for so in sorted(single):
        p2[esrc == so] = names[csrc == so][0]
    return p1, p2


def ak_compute(b, L, ksrc, sources, ladder=True, single=()):
    """AK1 / AK2 readouts on a bundle (g13_breakdown's B1 / B2 code path: ukm_fit, name_clusters, stat). With one-cell sources
    (C-S1) the MIRRORED comparators decide and the registered nearest-of-all ones are kept beside (R["reg"], descriptive)."""
    classes = [str(x) for x in b["classes"]]
    Xt, yt, Xe, ye = unit_bundle(b)
    comp, fl = np.asarray(b["eval_comp"]), np.asarray(b["eval_fl"], dtype=np.int64)
    esrc = np.array([src_of(classes[i]) for i in ye])
    tsrc = np.array([src_of(classes[i]) for i in yt])
    R = dict(n=len(ye), G=len(set(comp.tolist())), n_train=len(yt), L=L, ksrc=dict(ksrc), p_fl=float(fl.mean()),
             n_major=len(b["leaf_major"]))
    ug_ok = {}
    for s in SEEDS:
        fit, _t = GB.ukm_fit(Xt, L, s)
        lab = GB.name_clusters(fit["labels"], L, yt, classes)
        ug_ok[s] = (lab[np.argmax(Xe @ fit["centers"].T, axis=1)] == ye).astype(np.int64)
    us_ok, us_in = {}, {}
    for s in SEEDS:
        C, csrc, _cl, _lab, fits = us_fit(Xt, tsrc, ksrc, sources, s)
        names = np.concatenate([GB.name_clusters(fits[so]["labels"], int(ksrc[so]), yt[tsrc == so], classes) for so in sources])
        S = Xe @ C.T
        us_ok[s] = (names[np.argmax(S, axis=1)] == ye).astype(np.int64)
        Sin = np.where(csrc[None, :] == esrc[:, None], S, -np.inf)
        us_in[s] = (names[np.argmax(Sin, axis=1)] == ye).astype(np.int64)
    single = tuple(sorted(single))
    R["mirrored"] = bool(single)
    if single:                                                   # C-S1: the registered rule kept beside, the mirrored one decides
        R["reg"] = dict(p_u={s: float(ug_ok[s].mean()) for s in SEEDS}, p_us={s: float(us_ok[s].mean()) for s in SEEDS})
        R["reg"]["spread_au"] = GB.spread_of(R["reg"]["p_u"].values())
        R["reg"]["spread_aus"] = GB.spread_of(R["reg"]["p_us"].values())
        R["reg"]["AK1"], R["reg"]["AK2"] = GB.stat(fl - ug_ok[0], comp), GB.stat(fl - us_ok[0], comp)
        R["single_sources"] = single
        for s in SEEDS:
            p1, p2 = ak_mirrored(Xt, yt, tsrc, Xe, esrc, L, ksrc, sources, single, classes, s)
            ug_ok[s], us_ok[s] = (p1 == ye).astype(np.int64), (p2 == ye).astype(np.int64)
    R["p_u"] = {s: float(ug_ok[s].mean()) for s in SEEDS}
    R["p_us"] = {s: float(us_ok[s].mean()) for s in SEEDS}
    R["p_us_in"] = {s: float(us_in[s].mean()) for s in SEEDS}
    R["spread_au"] = GB.spread_of(R["p_u"].values())
    R["spread_aus"] = GB.spread_of(R["p_us"].values())
    R["AK1"] = GB.stat(fl - ug_ok[0], comp)
    R["AK2"] = GB.stat(fl - us_ok[0], comp)
    R["p_u0"], R["p_us0"] = R["p_u"][0], R["p_us"][0]
    R["d_au"], R["d_aus"] = R["AK1"]["d"], R["AK2"]["d"]
    R["by_source"] = {}
    for so in sources:
        m = esrc == so
        R["by_source"][so] = (int(m.sum()), GB.stat(fl[m] - ug_ok[0][m], comp[m]), GB.stat(fl[m] - us_ok[0][m], comp[m]))
    if ladder:
        R["p_ncc"] = float(GC.ncc_correct(Xt, yt, Xe, ye).mean())
        try:
            kc = GC.k_per_class(classes, yt, [str(x) for x in b["leaf_major"]])
            R["p_kc"] = float(GC.kc_correct(Xt, yt, Xe, ye, kc, 0).mean())
        except SystemExit as e:                     # descriptive rung only; the reason is printed
            R["p_kc"] = "not computable (%s)" % str(e)[:120]
    return R


def ak_identity_strings(R):
    return dict(d_u="%+.4f" % R["AK1"]["d"], d_us="%+.4f" % R["AK2"]["d"], spread_u="%.4f" % R["spread_au"],
                spread_us="%.4f" % R["spread_aus"])


def ak_identity(say):
    """AK-IDENTITY: the AK reader pointed at B0 (512-d, 133 leaves) reproduces G13-BREAKDOWN's four strings, else REFUSES."""
    c = reg()
    stem = P(c["b0_bundle"])
    b, _meta = GC.load_bundle(stem, expect=(c["pool"], c["n_eval_before"], c["comp_before"]), sides=None)
    if b["eval_X"].shape[1] != c["b0_dim"]:
        refuse("AK-IDENTITY: B0's bundle is %d-d, not %d" % (b["eval_X"].shape[1], c["b0_dim"]))
    ksrc, _ids = leaf_counts(c["b0_dir"], c["members"])
    if ksrc != c["b0_ksrc"]:
        refuse("AK-IDENTITY: B0's snapshot leaves per source %s, not the registered %s" % (ksrc, c["b0_ksrc"]))
    R = ak_compute(b, sum(ksrc.values()), ksrc, c["sources"], ladder=False)
    got, want = ak_identity_strings(R), dict(c["ak_identity"])
    say("AK-IDENTITY (B0, %d-d, %d leaves; bundle %s.npz sha256 %s): D_U %s, D_Us %s, spread_U %s, spread_US %s (registered %s, %s,"
        " %s, %s)" % (c["b0_dim"], sum(ksrc.values()), c["b0_bundle"], sha256_bytes(stem + ".npz")[:16], got["d_u"], got["d_us"],
                      got["spread_u"], got["spread_us"], want["d_u"], want["d_us"], want["spread_u"], want["spread_us"]))
    bad = [k for k in ("d_u", "d_us", "spread_u", "spread_us") if got[k] != want[k]]
    if bad:
        refuse("[RP13-AK-IDENTITY] %s reproduced as %s, registered %s: a failed precondition, no outcome" %
               (bad, [got[k] for k in bad], [want[k] for k in bad]))
    hit("AK.IDENTITY_OK")
    say("  -> AK-IDENTITY REPRODUCED to the printed digits")
    return R


def ak_verdict(st, spread):
    return GB.v_spread(st["d"], st["lo"], st["hi"], spread)


def fs(st):
    return "%+.4f  95%% [%+.4f, %+.4f] (n %d, %d components; SE %.5f, DEFF %.3f, n_eff %.0f, MDE80 %.4f, discordance %.4f)" % (
        st["d"], st["lo"], st["hi"], st["n"], st["G"], st["se"], st["deff"], st["n_eff"], st["mde"], st["disc"])


def ak_lines(R):
    """The AK block (render uses it verbatim; every branch executed by the selftest)."""
    L = []
    say = L.append
    c = reg()
    say("")
    say("=== AF-VS-KMEANS: AK1, AK2, F-AK (%s) ===" % REG_AK)
    say("DENOMINATOR (AK): union EVAL %d items in %d CK-CLOSE components (MC-EXCLUDE; registered %d / %d); Kish mean cluster size"
        " %.3f; never joined with U1-U3's %d" % (R["n"], R["G"], c["n_fl"], c["comp_fl"], R["n"] / R["G"], c["n_route"]))
    say("FIT SET: TRAIN %d items (registered expectation %d, B0's); k = %d (AF-U's total leaf count, a one-cell member counted 1; %d with a TRAIN profile);"
        " k per source %s; seeds %s, s = 0 the comparator of record" % (R["n_train"], c["n_train_fit"], R["L"], R["n_major"],
                                                                         ", ".join("%s %d" % (s, R["ksrc"][s]) for s in c["sources"]),
                                                                         "/".join(str(s) for s in SEEDS)))
    say("P_fl(AF-U) = %.4f (flatLeaf leaf named by its TRAIN-majority (source, domain), against the item's declared class)" % R["p_fl"])
    st1, st2 = R["AK1"], R["AK2"]
    if R.get("mirrored"):
        hit("AK.MIRRORED")
        one = ", ".join(R["single_sources"])
        say("AK1 U-global (MIRRORED, C-S1, DECIDES: one-cell %s filed by source to its k = 1 centroid, which no other item can"
            " reach; k = %d on the other sources' TRAIN): P(U_s) %s; spread_AU %.4f; D_AU = P_fl - P(U_0) %s" % (
                one, R["L"] - len(R["single_sources"]), " / ".join("%.4f" % R["p_u"][s] for s in SEEDS), R["spread_au"], fs(st1)))
        g = R["reg"]
        say("  DESCRIPTIVE (the registered nearest-of-all AK1, C-S1; it would give the comparator no by-source filing of %s while"
            " AF-U has it): P(U_s) %s; spread_AU %.4f; D_AU %s" % (one, " / ".join("%.4f" % g["p_u"][s] for s in SEEDS), g["spread_au"], fs(g["AK1"])))
        say("AK2 U-source (MIRRORED, C-S1, DECIDES: one-cell %s filed by source to its k = 1 centroid, excluded from every other"
            " item's nearest search): P(US_s) %s; spread_AUs %.4f; D_AUs = P_fl - P(US_0) %s" % (
                one, " / ".join("%.4f" % R["p_us"][s] for s in SEEDS), R["spread_aus"], fs(st2)))
        say("  DESCRIPTIVE (the registered nearest-of-ALL-centroids AK2, C-S1): P(US_s) %s; spread_AUs %.4f; D_AUs %s" % (
            " / ".join("%.4f" % g["p_us"][s] for s in SEEDS), g["spread_aus"], fs(g["AK2"])))
    else:
        say("AK1 U-global: P(U_s) %s; spread_AU %.4f; D_AU = P_fl - P(U_0) %s" % (" / ".join("%.4f" % R["p_u"][s] for s in SEEDS),
                                                                             R["spread_au"], fs(st1)))
        say("AK2 U-source (nearest of ALL centroids, no source oracle): P(US_s) %s; spread_AUs %.4f; D_AUs = P_fl - P(US_0) %s" % (
            " / ".join("%.4f" % R["p_us"][s] for s in SEEDS), R["spread_aus"], fs(st2)))
    say("  beside (U2's K_s form, EVAL filed within its true source): P(US_s in-source) %s" % " / ".join("%.4f" % R["p_us_in"][s] for s in SEEDS))
    words = {}
    for key, st, spread, sk, lab in (("AK1", st1, R["spread_au"], "spread_AU", "unsupervised k-means"),
                                     ("AK2", st2, R["spread_aus"], "spread_AUs", "source-aware unsupervised k-means")):
        sup = SUPPORT_AK[key]
        bar = max(st["mde"], spread)
        say("  support %s: SE %.5f (registered %.5f); DEFF %.3f (transported %.3f, measured here); n_eff %.0f (registered %d); MDE80"
            " %.4f (registered %.4f); bar = max(MDE80, %s) = %.4f (planning %.4f)" % (key, st["se"], sup["se"], st["deff"], sup["deff"],
                                                                                       st["n_eff"], sup["n_eff"], st["mde"], sup["mde"],
                                                                                       sk, bar, sup["spread"]))
        v = ak_verdict(st, spread)
        words[key] = v
        d = "D_AU" if key == "AK1" else "D_AUs"
        if v == "HELD":
            hit(key + ".HELD")
            say("%s: HELD (the anchor-free tree's discovered structure files better than %s): %s %+.4f, interval [%+.4f, %+.4f] wholly"
                " above 0 AND %s > %s %.4f" % (key, lab, d, st["d"], st["lo"], st["hi"], d, sk, spread))
        elif v == "REVERSED":
            hit(key + ".REVERSED")
            say("%s: REVERSED (its FAILED: %s files better than the anchor-free tree): %s %+.4f, interval [%+.4f, %+.4f] wholly below 0"
                " AND %s < -%s %.4f" % (key, lab, d, st["d"], st["lo"], st["hi"], d, sk, spread))
        else:
            if (st["lo"] > 0 or st["hi"] < 0):
                hit(key + ".UNDET_SPREAD")
                why = "UNDETERMINED by spread: the interval excludes 0 but |%s| %.4f <= %s %.4f" % (d, abs(st["d"]), sk, spread)
            else:
                hit(key + ".UNDET_INTERVAL")
                why = "UNDETERMINED: the interval [%+.4f, %+.4f] reaches 0" % (st["lo"], st["hi"])
            say("%s: %s; reads \"not shown\", never parity and never \"no difference\"" % (key, why))
    fires = bool(st2["hi"] <= R["spread_aus"])
    words["F-AK"] = "FIRES" if fires else "NOT FIRED"
    if fires:
        sub = "REVERSED" if words["AK2"] == "REVERSED" else "not better"
        hit("FAK.FIRES_REVERSED" if sub == "REVERSED" else "FAK.FIRES_NOTBETTER")
        say("F-AK FIRES (%s): AK2's upper bound %+.4f <= the measured spread_AUs %.4f: the anchor-free tree is NOT better than"
            " unsupervised, source-aware k-means at matched k beyond k-means' own seed spread; with G13 / C-a4 the SQ3 filing"
            " sentence reads \"once anchors are removed, the tree files no better than unsupervised k-means\" (through the"
            " author's D6)" % (sub, st2["hi"], R["spread_aus"]))
    else:
        hit("FAK.NOT_FIRED")
        say("F-AK does not fire: AK2's upper bound %+.4f > the measured spread_AUs %.4f; this is never \"the tree beats k-means\""
            " unless AK2 is HELD (AK2 %s)" % (st2["hi"], R["spread_aus"], words["AK2"]))
    say("  AK1 is reported beside and does not decide F-AK; AK1 / AK2 / F-AK feed no F-TAX leg (L-1 stays U2)")
    for ln in single_lines(R.get("single", {})):
        say(ln)
    say("DESCRIPTIVE per source (none scored): " + "; ".join(
        "%s n %d D_AU %s D_AUs %s" % (so, n, ("%+.4f" % a["d"]) if a else "n/a (0 items)", ("%+.4f" % b2["d"]) if b2 else "n/a (0 items)")
        for so, (n, a, b2) in R["by_source"].items()))
    kc = R.get("p_kc")
    say("LABEL LADDER (P_fl on the same %d EVAL items; each row names the labels it reads): U-global_0 %.4f (labels at naming only) |"
        " U-source_0 %.4f (source + labels at naming) | AF-U %.4f (labels at naming only; anchor-free, label-free partition) |"
        " anchored B0 %s of record (GT-seeded anchors; different recipe, slice and k; printed beside, never ranked) | NCC %s"
        " (class centroids) | KC_0 %s (class-conditional k-means at AF-U's leaf majors)" % (
            R["n"], R["p_u0"], R["p_us0"], R["p_fl"], c["b0_p_fl"], ("%.4f" % R["p_ncc"]) if "p_ncc" in R else "n/a",
            ("%.4f" % kc) if isinstance(kc, float) else (kc or "n/a")))
    for label, (key, band) in PRED_AK.items():
        ok = in_band(R[key], band)
        hit("PAK.HELD" if ok else "PAK.FAILED")
        say("PREDICTION %s: observed %+.4f -> %s" % (label, R[key], "HELD" if ok else "FAILED"))
    for key in ("AK1", "AK2", "F-AK"):
        say("PREDICTION %s verdict probabilities (%s): observed %s" % (key, PROB_AK[key], words[key]))
    return L, words


# ── U1-U3 on the two-stage replicates of v2_declared_cells ──────────────────────────────────────────────────────────────

def lin(bt, D, sub, w):
    """A linear contrast of arms (weights w {arm index: weight}) in v2_declared_cells.contrast's form (point +- 1.96 SE_2stage)."""
    j = [n for n, _ in D.subsets].index(sub)
    idx = sorted(w)
    wv = np.array([w[a] for a in idx], dtype=np.float64)
    pt = float(sum(w[a] * bt["point"][j, a] for a in idx))
    d2 = bt["two"][:, j, idx] @ wv
    di = bt["iid"][:, j, idx] @ wv
    v2, vi = V._var(d2), V._var(di)
    se2, sei = math.sqrt(v2), math.sqrt(vi)
    n = int(D.subsets[j][1].sum())
    deff = (v2 / vi) if vi > 0 else float("nan")
    return dict(sub=sub, point=pt, se2=se2, lo=pt - 1.96 * se2, hi=pt + 1.96 * se2, se_iid=sei, var2=v2,
                pct=tuple(float(x) for x in np.nanpercentile(d2, [2.5, 97.5])), n=n, deff=deff,
                n_eff=(n / deff) if deff == deff and deff > 0 else float("nan"), mde=2.80 * se2)


def u_stats(bt, D, c1):
    names = list(D.xnames)
    kidx = [V.TREE + 1 + i for i in range(len(names))]
    nk = len(kidx)
    st = dict(C1=c1, G=V.contrast(bt, D, "ALL", V.TREE, V.BS), M=V.contrast(bt, D, "ALL", V.TREE, V.TDOM), names=names)
    st["GK_s"] = {nm: V.contrast(bt, D, "ALL", k, V.BS) for nm, k in zip(names, kidx)}
    wk = {k: 1.0 / nk for k in kidx}
    wg = dict(wk)
    wg[V.BS] = -1.0
    wd = {k: -1.0 / nk for k in kidx}
    wd[V.TREE] = 1.0
    st["GK"] = lin(bt, D, "ALL", wg)
    st["DK"] = lin(bt, D, "ALL", wd)
    pts = [st["GK_s"][nm]["point"] for nm in names]
    st["spread_K"] = max(pts) - min(pts)
    return st


def u1_verdict(g):
    """U1 (the INTERVAL decides): HELD iff lower > 0; FAILED iff upper <= 0; UNDETERMINED otherwise."""
    if g["lo"] > 0:
        return "HELD"
    if g["hi"] <= 0:
        return "FAILED"
    return "UNDETERMINED"


def u2_verdict(dk, spread):
    """U2 (= F-TAX L-1; INTERVAL AND POINT, one conjunctive clause): FIRES iff lower > 0 AND D_K > spread_K; the reverse
    (upper < 0 AND D_K < -spread_K) reported beside; otherwise NOT FIRED."""
    if dk["lo"] > 0 and dk["point"] > spread:
        return "FIRES"
    if dk["hi"] < 0 and dk["point"] < -spread:
        return "REVERSE"
    return "NOT FIRED"


def _phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def tost_p(st, delta):
    """TOST p (normal, SE_2stage): max of the one-sided p-values of H0: D <= -delta and H0: D >= delta."""
    d, se = st["point"], st["se2"]
    if se == 0:
        return 0.0 if abs(d) < delta else 1.0
    return max(1.0 - _phi((d + delta) / se), _phi((d - delta) / se))


def inside(st, z, delta):
    return bool(st["point"] - z * st["se2"] > -delta and st["point"] + z * st["se2"] < delta)


def holm_u3(a, b, delta):
    """R6: Holm over the two TOSTs -> ({name: (EQUIVALENT|NOT EQUIVALENT, step, z, lo, hi, p)}, order)."""
    items = [("U3a", a), ("U3b", b)]
    order = sorted(items, key=lambda t: (tost_p(t[1], delta), 0 if t[0] == "U3a" else 1))
    (n1, s1), (n2, s2) = order
    e1 = inside(s1, 1.96, delta)
    e2 = e1 and inside(s2, 1.645, delta)
    out = {n1: ("EQUIVALENT" if e1 else "NOT EQUIVALENT", 1, 1.96, s1["point"] - 1.96 * s1["se2"], s1["point"] + 1.96 * s1["se2"],
                tost_p(s1, delta)),
           n2: ("EQUIVALENT" if e2 else "NOT EQUIVALENT", 2, 1.645, s2["point"] - 1.645 * s2["se2"], s2["point"] + 1.645 * s2["se2"],
                tost_p(s2, delta))}
    return out, (n1, n2), e1


def sup_line(name, s, plan):
    return ("  support %s: n %d, SE_2stage %.5f (registered %.5f), i.i.d. SE %.5f, DEFF %.3f, n_eff %.0f, MDE80 %s (registered %s)"
            % (name, s["n"], s["se2"], plan["se"], s["se_iid"], s["deff"], s["n_eff"], pp(s["mde"]), pp(plan["mde"])))


def u_lines(st, info):
    """U1, U2, U3, F-U1, the F-TAX lines, predictions, descriptive lines (rp13_tail prints them verbatim)."""
    L = []
    say = L.append
    c = reg()
    g, m, gk, dk, spread = st["G"], st["M"], st["GK"], st["DK"], st["spread_K"]
    say("")
    say("=== UNION-AF-ROUTE U1-U3 (%s) ===" % REG_U)
    say("DENOMINATOR (U1-U3): %d EVAL items in %d components (Support (a): %d / %d); TRAIN %d items; never joined with the AK"
        " block's %d" % (g["n"], info["eval_units"], c["n_route"], c["comp_route"], info["n_train"], c["n_fl"]))
    say("IDENTITY PRECONDITION: the declared arm C1 = %s [%s, %s] (two-stage); V2-DECLARED-CELLS C1 of record %s [%s, %s] ->"
        " REPRODUCED to the printed digits" % ((pp(st["C1"]["point"]), pp(st["C1"]["lo"]), pp(st["C1"]["hi"])) + tuple(c["identity"])))
    hit("U.IDENTITY_OK")
    say("U1: G_AF = acc(AF-U leaf cells) - acc(best single) = %s (%.5f) | two-stage [%s, %s] | percentile [%s, %s]" % (
        pp(g["point"]), g["point"], pp(g["lo"]), pp(g["hi"]), pp(g["pct"][0]), pp(g["pct"][1])))
    say(sup_line("U1", g, SUPPORT_U["U1"]))
    v1 = u1_verdict(g)
    if v1 == "HELD":
        hit("U1.HELD")
        say("  U1 -> HELD (the interval lies wholly above 0)")
    elif v1 == "FAILED":
        hit("U1.FAILED")
        say("  U1 -> FAILED (the interval's upper bound is at or below 0)")
    else:
        hit("U1.UNDETERMINED")
        say("  U1 -> UNDETERMINED (the interval covers 0)")
    say("K_s (per-source spherical k-means at AF-U's per-source leaf counts, seeds %s): G_K,s = %s" % (
        "/".join(str(s) for s in SEEDS), " / ".join("%s %s (%.5f)" % (nm, pp(st["GK_s"][nm]["point"]), st["GK_s"][nm]["point"])
                                                  for nm in st["names"])))
    say("G_K = mean over s = %s (%.5f) | two-stage [%s, %s]; spread_K = max - min over s = %s (%.5f)" % (
        pp(gk["point"]), gk["point"], pp(gk["lo"]), pp(gk["hi"]), pp(spread).lstrip("+"), spread))
    say("U2 (= F-TAX L-1): D_K = G_AF - G_K = %s (%.5f) | two-stage [%s, %s] | percentile [%s, %s]" % (
        pp(dk["point"]), dk["point"], pp(dk["lo"]), pp(dk["hi"]), pp(dk["pct"][0]), pp(dk["pct"][1])))
    say(sup_line("U2", dk, SUPPORT_U["U2"]) + "; bar = max(MDE80, spread_K) = %s (planning %s)" % (
        pp(max(dk["mde"], spread)), pp(max(SUPPORT_U["U2"]["mde"], SUPPORT_U["U2"]["spread"]))))
    hit("U2.D4_DISCLOSED")
    say("  DISCLOSURE (D-4): K_s files every item among the centroids of its TRUE declared source (registered \"EVAL filed by"
        " source\"), while AF-U's flatLeaf searches ALL grafted leaves; D_K therefore carries a filing-information asymmetry"
        " AGAINST AF (it pushes D_K down)")
    v2 = u2_verdict(dk, spread)
    if v2 == "FIRES":
        hit("U2.FIRES")
        say("  U2 -> L-1 FIRES: the interval lies wholly above 0 AND D_K %s > spread_K %s (DESCRIPTIVE-ONLY at its prediction; an"
            " observed FIRE counts, F-TAX bracket 2026-10-01)" % (pp(dk["point"]), pp(spread).lstrip("+")))
    elif v2 == "REVERSE":
        hit("U2.REVERSE")
        say("  U2 -> not fired; the REVERSE is observed (reported beside): the interval lies wholly below 0 AND D_K %s < -spread_K"
            " %s" % (pp(dk["point"]), pp(spread).lstrip("+")))
    else:
        hit("U2.NOT_FIRED")
        say("  U2 -> not fired: neither a gain nor parity is shown by U2 (interval [%s, %s], D_K %s, spread_K %s)" % (
            pp(dk["lo"]), pp(dk["hi"]), pp(dk["point"]), pp(spread).lstrip("+")))
    say("U3b: M_AF = G_AF - G_declared = %s (%.5f) | two-stage [%s, %s] | percentile [%s, %s]" % (
        pp(m["point"]), m["point"], pp(m["lo"]), pp(m["hi"]), pp(m["pct"][0]), pp(m["pct"][1])))
    say("  support U3b: n %d, SE_2stage %.5f, DEFF %.3f, n_eff %.0f (registered paired SE 0.0033)" % (m["n"], m["se2"], m["deff"], m["n_eff"]))
    u3, order, _e1 = holm_u3(dk, m, c["delta"])
    say("U3 (TOST, delta = %s, Holm over U3a and U3b; R6): TOST p U3a %.4g, U3b %.4g; Holm order %s first (95%%), %s second (90%%)"
        % (pp(c["delta"]).lstrip("+"), u3["U3a"][5], u3["U3b"][5], order[0], order[1]))
    for nm, lab in (("U3a", "D_K (AF against per-source k-means)"), ("U3b", "M_AF (AF against declared labels)")):
        word, step, z, lo, hi, _p = u3[nm]
        hit("%s.%s" % (nm, "EQ" if word == "EQUIVALENT" else "NEQ"))
        tail = "" if word == "EQUIVALENT" else (" (Holm stopped at the first step)" if step == 2 and u3[order[0]][0] != "EQUIVALENT"
                                                else " (the interval leaves +-%s)" % pp(c["delta"]).lstrip("+"))
        say("  %s %s: step %d, %d%% interval [%s, %s] -> %s%s" % (nm, lab, step, 95 if z == 1.96 else 90, pp(lo), pp(hi), word, tail))
    words = dict(U1=v1, U2=v2, U3a=u3["U3a"][0], U3b=u3["U3b"][0])
    if v1 == "FAILED":
        hit("FU1.FIRES")
        say("F-U1 FIRES (U1 FAILED): the union router gain on declared cells (+2.67pp) and on anchored tree cells (+2.62pp) does not"
            " transfer to label-free cells")
    else:
        hit("FU1.NOT_FIRED")
        say("F-U1 does not fire (U1 %s)" % v1)
    bar = max(dk["mde"], spread)
    if v2 == "FIRES":
        hit("FTAX.L1_FIRES")
        say("F-TAX L-1: FIRES (observed under U2; counts as a fire by the F-TAX bracket of 2026-10-01) -> F-TAX's F1 (lever); F-TAX's"
            " reading table: \"a lever AND N-1: recorded joined, no sentence\"")
        if words["U3a"] == "EQUIVALENT":
            hit("FTAX.JOINED")
            say("REGISTRAR'S NOTE: recorded joined \"L-1 FIRES / U3a EQUIVALENT\" (both clauses scored)")
    else:
        by_support = bool(abs(dk["point"]) <= bar)
        hit("FTAX.L1_NOT_BY_SUPPORT" if by_support else "FTAX.L1_NOT")
        say("F-TAX L-1: NOT FIRED -> \"a filing device only\" (N-1 fired)%s; a non-fire reads \"not shown\", never \"no lever\"" % (
            " (lever leg not fired, by support: |D_K| %s <= bar %s)" % (pp(abs(dk["point"])).lstrip("+"), pp(bar).lstrip("+"))
            if by_support else ""))
    if words["U3b"] == "EQUIVALENT":
        hit("FTAX.U3B_CLAUSE")
        say("LICENSED CLAUSE (U3b EQUIVALENT): \"label-free cells route equivalently to declared labels within 1pp (content-closed"
            " union, this roster)\"")
    else:
        hit("FTAX.NO_U3B_CLAUSE")
        say("No parity clause is licensed (U3b %s)" % words["U3b"])
    for label, band in PRED_U.items():
        x = {"U1": g["point"], "U2 D": dk["point"], "U2 s": spread, "U3b": m["point"]}[
            "U1" if label.startswith("U1") else "U2 D" if label.startswith("U2 D_K") else "U2 s" if label.startswith("U2 s") else "U3b"]
        ok = in_band(x, band)
        hit("PU.HELD" if ok else "PU.FAILED")
        say("PREDICTION %s: observed %s -> %s" % (label, pp(x), "HELD" if ok else "FAILED"))
    nl = info["n_leaves"]
    ok = in_band(nl, PRED_LEAVES)
    hit("PU.HELD" if ok else "PU.FAILED")
    say("PREDICTION leaves AF-U 70-110 in total: observed %d -> %s" % (nl, "HELD" if ok else "FAILED"))
    say("PREDICTION U1 verdict probability (%s): observed %s" % (PROB_U["U1"], v1))
    say("PREDICTION L-1 (%s): observed %s" % (PROB_U["L-1"], "FIRES" if v2 == "FIRES" else "not fired"))
    say("PREDICTION U3a (%s): observed %s; U3b (%s): observed %s" % (PROB_U["U3a"], words["U3a"], PROB_U["U3b"], words["U3b"]))
    for ln in single_lines(info.get("single", {})):
        say(ln)
    say("DESCRIPTIVE: AF-U leaves per source %s (total %d); AF cells over the scored items %d distinct; P_fl(AF-U) %s; D_fd %s;"
        " anchored B0 G_tree %s of record (not recomputed; recipes never ranked)" % (
            ", ".join("%s %d" % (s, info["ksrc"][s]) for s in c["sources"]), nl, info["af_distinct"], info["p_fl"], info["d_fd"],
            c["b0_g_tree"]))
    say("WORDS: arena cells stay DECLARED (S1); an AF-U leaf is a policy arm, not an arena cell; content-closed under CK-CLOSE-v2"
        " (residual disclosed); key-scored end to end, no judge verdict (no wrong(established) count, no convention A / B arises);"
        " aggregate G only, no per-leaf model rows in this outcome")
    say("WILL NOT SHOW (fixed before data): that the tree beats clustering in general (one draw, one recipe, one roster, qwen3"
        " 256); a gain over declared labels; parity outside +-1pp, or at all if U3 is not EQUIVALENT; anything for MMLU-Pro alone;"
        " any certificate; that a non-fire of L-1 is evidence of no lever")
    return L, words


R10_KEYS = ("best_single", "true_source", "true_source_domain", "roster", "train_items_scored", "variant_rule", "key", "tie_break",
            "absent_group")


def r10_check(cfg, pol, psha, say):
    """R10 / C-4: the declared arm's frozen TRAIN policy equals leg U's frozen file on every policy key (best single, both
    declared groupings, roster, TRAIN count, rules); v2_declared_cells calls it BEFORE the EVAL view opens and the B1 marker."""
    lu = cfg.rp13["leg_u_policy"]
    nn = lambda d: {k: v for k, v in d.items() if v is not None} if isinstance(d, dict) else d
    bad = [k for k in R10_KEYS if nn(lu.get(k)) != nn(pol.get(k))]
    if bad:
        hit("REFUSE.R3")
        raise SystemExit("[RP13-R3] the declared arm's frozen TRAIN policy differs from leg U's frozen file (sha256 %s) on %s: the"
                         " declared-label comparator of record (R3) is not reproduced; refused BEFORE the EVAL key read, no outcome"
                         % (cfg.rp13["leg_u_sha"], bad))
    line = ("R3 / R10 (before the EVAL view opened): the declared arm's frozen TRAIN policy (sha256 %s) equals leg U's frozen file"
            " %s (sha256 %s) on %s: best single %s, %d declared cells" % (psha, reg()["leg_u_policy"], cfg.rp13["leg_u_sha"],
                                                                          ", ".join(R10_KEYS), pol["best_single"],
                                                                          len(nn(pol["true_source_domain"]))))
    cfg.rp13["r10_line"] = line
    say(line)


def rp13_tail(cfg, say, D, bt, c1, pol, ok_sha, kst_tr, kst_ev, residual, K_ev):
    """The readout of the RP13 tree run (v2_declared_cells leg_u calls it in place of g14_tail)."""
    c = reg()
    ident = tuple(c["identity"])
    got = (pp(c1["point"]), pp(c1["lo"]), pp(c1["hi"]))
    if got != ident:
        raise SystemExit("[RP13-IDENTITY] the declared arm prints C1 = %s [%s, %s], not V2-DECLARED-CELLS C1 of record %s [%s, %s]:"
                         " a failed precondition, no outcome written" % (got + ident))
    if (D.n_eval, D.eval_units["n_units"]) != (c["n_route"], c["comp_route"]):
        raise SystemExit("[RP13-DENOM] the deciding set is %d EVAL items in %d components, not Support (a)'s %d / %d"
                         % (D.n_eval, D.eval_units["n_units"], c["n_route"], c["comp_route"]))
    if "r10_line" not in cfg.rp13:
        raise SystemExit("[RP13-R3] the R10 check did not run before the EVAL key read; no outcome written")
    say("")
    say("=== RP13 PRECONDITIONS (printed by union_af_route.py before the EVAL view opened; copied here verbatim) ===")
    for ln in cfg.rp13.get("pre_lines", ()):
        say("  | " + ln)
    say(cfg.rp13["r10_line"])
    say("ARM ACCURACIES on EVAL (point | two-stage SE | i.i.d. SE), n = %d:" % D.n_eval)
    arms = list(V.ARMS) + ["AF-U leaf cell"] + ["K_s %s" % nm for nm in D.xnames]
    for a, name in enumerate(arms):
        say("    %-24s %.4f  %.5f  %.5f" % (name, bt["point"][0, a], math.sqrt(V._var(bt["two"][:, 0, a])), math.sqrt(V._var(bt["iid"][:, 0, a]))))
    say("  cells over the scored items: AF %d distinct; %s" % (len(D.tree_keys), ", ".join("%s %d" % (nm, len(D.xkeys[nm])) for nm in D.xnames)))
    st = u_stats(bt, D, c1)
    info = dict(cfg.rp13["info"], eval_units=D.eval_units["n_units"], n_train=D.n_train, af_distinct=len(D.tree_keys))
    lines, words = u_lines(st, info)
    for ln in lines:
        say(ln)
    for ln in cfg.rp13["ak_lines"]:
        say(ln)
    words.update(cfg.rp13["ak_words"])
    return dict(st=st, words=words, ok_sha=ok_sha, D=D, bt=bt, policy=pol, cells={}, kst=dict(train=kst_tr, eval=kst_ev),
                residual=residual, K_ev=K_ev)


# ── modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────────

def header(say, mode):
    c = reg()
    say("POOL %s (%s, RP13; %s; the first line of every mode)" % (c["pool"], TEST_ID, mode))
    say("%s | registrations %s ; %s" % (TEST_ID, REG_U, REG_AK))
    say("  results root %s (TAXOARENA_RESULTS_ROOT %s); data root %s" % (_ROOT[0], os.environ.get("TAXOARENA_RESULTS_ROOT", "unset"),
                                                                       RP.C.DATA_ROOT))
    for f in [os.path.abspath(__file__)] + [os.path.join(HERE, n) for n, _ in PINS]:
        say("  " + V.G.identity_line(f))
    say("  threads: %s (set to 1 by this script before numpy)" % ", ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    say("  sqlite3.connect: flat_mix_mmlu's import-time guard %s; DBs are opened only through data_v2.ro.open_ro (mode=ro,"
        " immutable=1, -wal / -journal refused)" % ("removed (it admits only FLAT-MIX's own four DBs)" if SQLITE_GUARD_REMOVED else "absent"))


def denominators(say):
    c = reg()
    say("DENOMINATORS (registered): U1-U3 %d EVAL items in %d components (G14's; DEFF 1.392 measured there; n_eff 4,244; SE U1"
        " 0.61pp, U2 / U3 0.33pp) | AK1 / AK2 %d EVAL items in %d components (MC-EXCLUDE; Kish 1.091; before the exclusion %d /"
        " %d) | AK fit set TRAIN %d expected | the two sets are never joined" % (
            c["n_route"], c["comp_route"], c["n_fl"], c["comp_fl"], c["n_eval_before"], c["comp_before"], c["n_train_fit"]))
    say("IDENTITY TARGETS: declared arm C1 %s [%s, %s] (checked in --run before any new number); AK-IDENTITY on B0 D_U %s, D_Us %s,"
        " spread_U %s, spread_US %s" % (tuple(c["identity"]) + tuple(c["ak_identity"][k] for k in ("d_u", "d_us", "spread_u", "spread_us"))))
    lp = P(c["leg_u_policy"])
    say("R3 declared-label comparator: leg U's frozen TRAIN policy %s sha256 %s" % (
        c["leg_u_policy"], sha256_bytes(lp) if os.path.isfile(lp) else "ABSENT"))


def check_afu(say):
    decl = declared_single()
    if not decl:
        hit("SINGLE.NONE_DECLARED")
        say("  ONE-CELL members: none declared (%s absent)" % reg()["single_decl"])
    pairs, val = afu_paths(tuple(decl))
    pres = presence(pairs)
    for lab, rel, ok in pres:
        say("  AF-U %-28s %s %s" % (lab, "PRESENT" if ok else "ABSENT ", rel))
    miss = [rel for _l, rel, ok in pres if not ok]
    if miss:
        hit("REFUSE.AFU_ABSENT")
        refuse("AF-U build outputs ABSENT (%d of %d): the build (experiment_configs/union_af_route/AF-U/, rule 7) has not run or"
               " is incomplete; nothing else is read" % (len(miss), len(pres)))
    single = load_single(say, decl) if decl else {}
    return pairs, val, single


def afu_state(say):
    c = reg()
    pairs, val, single = check_afu(say)
    commit, _m = build_commits(pairs)
    ksrc, ids = leaf_counts(c["afu"], [(m, s) for m, s in c["members"] if s not in single])
    for s, e in single.items():                                  # a one-cell member counts one leaf (L22638 bracket)
        ksrc[s], ids[s] = 1, {e["cell"]}
    extra = sorted(set(ksrc) - set(c["sources"]))
    if extra or set(ksrc) != set(c["sources"]):
        refuse("AF-U members' sources %s are not the registered %s" % (sorted(ksrc), list(c["sources"])))
    lrows = GB.read_csv(os.path.join(P(val), RP.LEAVES))
    csv_ids = {r["leaf_id"] for r in lrows}
    snap_ids = set().union(*[v for k, v in ids.items() if k not in single])
    if csv_ids != snap_ids:
        refuse("the graft's leaves CSV covers %d leaves, the member snapshots %d (sets differ by %d)" % (
            len(csv_ids), len(snap_ids), len(csv_ids ^ snap_ids)))
    say("  AF-U build commit (D-8, every run_manifest): %s; leaves per source %s; total %d%s" % (
        commit, ", ".join("%s %d" % (s, ksrc[s]) for s in c["sources"]), sum(ksrc.values()),
        "; one-cell: %s" % ", ".join(sorted(single)) if single else ""))
    return pairs, val, ksrc, commit, single


def _sides():
    return RP.sides(os.path.join(ROOT, RP.EP.DEFAULT_SIDE))


def _texts_vectors(ids_needed, dim):
    """{item: unit vector} through rp12_pairing's P4 readers (multicorpus_cache_v1.db texts, embeddings_cache.db vectors)."""
    texts = RP.item_texts(os.path.join(RP.C.DATA_ROOT, "multicorpus_cache_v1.db"), None)
    miss = [i for i in ids_needed if i not in texts]
    if miss:
        refuse("%d routed item(s) have no text (first %s)" % (len(miss), miss[:3]))
    vec = RP.vectors(os.path.join(RP.C.DATA_ROOT, "embeddings_cache.db"), [texts[i] for i in ids_needed], dim)
    nov = [i for i in ids_needed if texts[i] not in vec]
    if nov:
        refuse("%d routed item(s) have no %d-d vector (first %s)" % (len(nov), dim, nov[:3]))
    return {i: vec[texts[i]] for i in ids_needed}


def _bundle_build(validation, stem, dim, out):
    return RP.g13_bundle(validation, os.path.join(ROOT, RP.EP.DEFAULT_SIDE), os.path.join(RP.C.DATA_ROOT, "multicorpus_cache_v1.db"),
                         None, os.path.join(RP.C.DATA_ROOT, "embeddings_cache.db"), stem, dim=dim, out=out)


_SIDES = [_sides]
_TV = [_texts_vectors]
_BUNDLE = [_bundle_build]


def build_inputs(out=print):
    """--build-inputs: the B0-2 pool check, the AF-U layout, then the write-once inputs (no EVAL key, no statistic)."""
    c = reg()
    say = out
    header(say, "--build-inputs")
    rc, msg = _POOL[0](c["pool"])
    say("POOL CHECK (B0-2): rc %d | %s" % (rc, msg))
    if rc != 0:
        refuse("the B0-2 pool check failed: %s" % msg)
    pairs, val, ksrc, commit, single = afu_state(say)
    ip = input_paths()
    outs = [ip["bundle"] + ".npz", ip["bundle"] + ".json", ip["af"], ip["manifest"]] + list(ip["k"].values())
    outs += [ip["merged"] + "/" + nm for nm in (RP.QUERIES, RP.TRAIN, RP.LEAVES)]
    ex = [p for p in outs if os.path.exists(P(p))]
    if ex:
        refuse("input file(s) exist (write-once): %s" % ex)
    side, smeta = _SIDES[0]()
    merged_info = {}
    if single:                                                   # one-cell members: the graft's CSVs + their one-cell rows
        merged_info = merged_validation(P(val), P(ip["merged"]), single, side, _STRATA[0]())
        for s_, (nh, nt, maj) in sorted(merged_info.items()):
            say("%s ONE-CELL %s: %d held-out and %d TRAIN routing rows added to %s, filed to %s (named %s)" % (
                TAG, s_, nh, nt, ip["merged"], single[s_]["cell"], maj))
        val = ip["merged"]
    os.makedirs(os.path.dirname(P(ip["bundle"])), exist_ok=True)
    _BUNDLE[0](P(val), P(ip["bundle"]), c["dim"], say)
    b, meta = GC.load_bundle(P(ip["bundle"]), expect=(c["pool"], c["n_eval_before"], c["comp_before"]), sides=None)
    if (len(b["eval_y"]), len(set(b["eval_comp"].tolist()))) != (c["n_fl"], c["comp_fl"]):
        refuse("the AF-U bundle holds %d EVAL items in %d components, not the registered %d / %d" % (
            len(b["eval_y"]), len(set(b["eval_comp"].tolist())), c["n_fl"], c["comp_fl"]))
    cells, cnt = af_cells(P(val), side)
    rows = RP.read_rows(os.path.join(P(val), RP.QUERIES)) + RP.read_rows(os.path.join(P(val), RP.TRAIN))
    srcs = item_sources(rows)
    routed = sorted(i for i, v in cells.items() if v != NO_ROW)
    vec = _TV[0](routed, c["dim"])
    classes = [str(x) for x in b["classes"]]
    Xt, yt, _Xe, _ye = unit_bundle(b)
    tsrc = np.array([src_of(classes[i]) for i in yt])
    titems = [str(x) for x in b["train_item"]]
    for j, it in enumerate(titems[:: max(1, len(titems) // 200)]):          # vectors agree with the bundle's (a sample)
        jj = titems.index(it)
        if not np.allclose(vec[it], Xt[jj], atol=1e-12):
            refuse("item %s: the K vector differs from the bundle's" % it)
    hdr = "afu_validation=%s rule=flatLeaf cell=leaf_id(R1) side_export=%s no_routing_row_eval=%d no_routing_row_train=%d" % (
        val, smeta.get("sha256_lf", "?")[:16], cnt["no_row_eval"], cnt["no_row_train"])
    sh_af = write_x(P(ip["af"]), cells_text(cells, hdr))
    say("%s AF cells %s: %d items (EVAL %d, TRAIN %d routed; multi-class EVAL %d, TRAIN %d kept with their modal leaf; %s: EVAL %d,"
        " TRAIN %d; <unrouted> %d), %d distinct cells; sha256 (LF) %s" % (TAG, ip["af"], len(cells), cnt["eval_routed"], cnt["train_routed"],
                                                                         cnt["multi_eval"], cnt["multi_train"], NO_ROW, cnt["no_row_eval"],
                                                                         cnt["no_row_train"], cnt["unrouted"], len(set(cells.values())), sh_af))
    shk, kinfo = {}, {}
    for s in SEEDS:
        kc, ki = k_cells(s, Xt, tsrc, titems, ksrc, c["sources"], vec, srcs, cells)
        shk[s] = write_x(P(ip["k"][s]), cells_text(kc, "comparator=K_s seed=%d k_per_source=%s fit=af_u_bundle TRAIN (R2-R4)" % (
            s, ",".join("%s:%d" % (so, ksrc[so]) for so in c["sources"]))))
        kinfo[s] = ki
        say("%s K cells seed %d %s: %d items, %d centres, %d distinct cells; TRAIN items whose nearest-centroid cell differs from the"
            " final fit label %d; sha256 (LF) %s" % (TAG, s, ip["k"][s], len(kc), ki["centres"], len(set(kc.values())), ki["moved_train"], shk[s]))
    man = dict(test=TEST_ID, pool=c["pool"], dim=c["dim"], afu_commit=commit, ksrc=ksrc, n_leaves=sum(ksrc.values()),
               builder_blob=blob_lf(os.path.abspath(__file__)),
               afu_files={rel: sha256_lf(P(rel)) for _l, rel in pairs},
               inputs=dict({ip["bundle"] + ".npz": sha256_bytes(P(ip["bundle"] + ".npz")), ip["bundle"] + ".json": sha256_lf(P(ip["bundle"] + ".json")),
                            ip["af"]: sh_af, **{ip["k"][s]: shk[s] for s in SEEDS}},
                           **({ip["merged"] + "/" + nm: sha256_lf(P(ip["merged"] + "/" + nm)) for nm in (RP.QUERIES, RP.TRAIN, RP.LEAVES)}
                              if single else {})),
               single={s_: dict(e, merged=list(merged_info.get(s_, ()))) for s_, e in single.items()},
               counts=dict(af=cnt, k={str(s): kinfo[s] for s in SEEDS}, bundle=meta.get("counts")))
    sh_m = write_x(P(ip["manifest"]), json.dumps(man, indent=1, sort_keys=True) + "\n")
    say("%s inputs manifest %s sha256 (LF) %s; no EVAL key read, no statistic computed" % (TAG, ip["manifest"], sh_m))
    hit("BUILD.DONE")
    return man


def load_inputs(say):
    """The inputs manifest, every pinned file re-hashed (AF-U files and inputs); -> (manifest, sha)."""
    ip = input_paths()
    mp = P(ip["manifest"])
    if not os.path.isfile(mp):
        hit("REFUSE.INPUTS_ABSENT")
        refuse("the inputs are not built (%s absent): run --build-inputs first" % ip["manifest"])
    man = json.load(open(mp, encoding="utf-8"))
    sh = sha256_lf(mp)
    bad = []
    for rel, want in list(man["afu_files"].items()):
        got = sha256_lf(P(rel)) if os.path.isfile(P(rel)) else None
        if got != want:
            bad.append(rel)
    for rel, want in man["inputs"].items():
        p = P(rel)
        got = (sha256_bytes(p) if rel.endswith(".npz") else sha256_lf(p)) if os.path.isfile(p) else None
        if got != want:
            bad.append(rel)
    if bad:
        hit("REFUSE.PIN")
        refuse("pinned file(s) changed since --build-inputs: %s" % bad)
    say("  inputs manifest %s sha256 (LF) %s: %d AF-U files and %d inputs EQUAL to their pins" % (
        ip["manifest"], sh, len(man["afu_files"]), len(man["inputs"])))
    return man, sh


def d_fd_text(b, val_desc):
    """R9: D_fd = P_fl - P_descent on the AK items when a descent graft exists; else NOT COMPUTED."""
    if not os.path.isdir(val_desc):
        hit("DFD.NOT_COMPUTED")
        return "NOT COMPUTED (no descent graft: the AF-U TOMLs at a994a722 carry graft_flatleaf only; R9)"
    cells_d, _d, _u, _m = RP.item_cells(RP.read_rows(os.path.join(val_desc, RP.QUERIES)))
    classes = [str(x) for x in b["classes"]]
    ye = np.asarray(b["eval_y"], dtype=int)
    eitems = [str(x) for x in b["eval_item"]]
    dok = np.array([int(it in cells_d and cells_d[it][0] == classes[ye[i]]) for i, it in enumerate(eitems)], dtype=np.int64)
    st = GB.stat(np.asarray(b["eval_fl"], dtype=np.int64) - dok, np.asarray(b["eval_comp"]))
    hit("DFD.COMPUTED")
    return "%+.4f [%+.4f, %+.4f] (P_descent %.4f; descriptive)" % (st["d"], st["lo"], st["hi"], dok.mean())


def make_cfg(man, say):
    c = reg()
    ip = input_paths()
    cfg = _VDC_CFG[0]()
    cfg.tree, cfg.tree_desc = V.load_tree_cells(P(ip["af"]), man["inputs"][ip["af"]])
    cfg.xtrees = {}
    for s in SEEDS:
        cells, _d = V.load_tree_cells(P(ip["k"][s]), man["inputs"][ip["k"][s]])
        cfg.xtrees["K%d" % s] = cells
    cfg.g14_identity = tuple(c["identity"])
    cfg.policy_path, cfg.out_u, cfg.mark_u = P(c["policy"]), P(c["out"]), P(c["marker"])
    cfg.tail = rp13_tail
    cfg.pre_eval = r10_check
    return cfg


def _git_ignored(path):
    """D-5: True iff git ignores the path (git check-ignore -q rc 0) and does not track it; the policy is never committed."""
    import subprocess
    pr = subprocess.run(["git", "check-ignore", "-q", path], cwd=_ROOT[0], capture_output=True)
    tr = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=_ROOT[0], capture_output=True)
    return pr.returncode == 0 and tr.returncode != 0


_IGNORED = [_git_ignored]


def dry_run(out=print):
    c = reg()
    say = out
    header(say, "--dry-run")
    denominators(say)
    ak_identity(say)
    pairs, val, ksrc, commit, single = afu_state(say)
    man, _sh = load_inputs(say)
    if man["ksrc"] != ksrc:
        refuse("the inputs were built at leaf counts %s, the AF-U snapshots now give %s" % (man["ksrc"], ksrc))
    rc, msg = _POOL[0](c["pool"])
    say("POOL CHECK (B0-2): rc %d | %s" % (rc, msg))
    if rc != 0:
        refuse("the B0-2 pool check failed: %s" % msg)
    cfg = make_cfg(man, say)
    say("--- v2_declared_cells leg U dry-run with the AF arm and K0..K4 (no key column; no statistic) ---")
    V.mode(cfg, "U", True)
    say("DRY-RUN: nothing written; no statistic of AF-U printed.")
    hit("DRY.DONE")
    return 0


def run(out=print):
    c = reg()
    pre = []

    def say(s_):
        pre.append(s_)
        out(s_)
    header(say, "--run")
    for p in (c["out"], c["policy"], c["marker"]):
        if os.path.exists(P(p)):
            hit("REFUSE.WRITE_ONCE")
            refuse("%s exists (write-once); refused before any read" % p)
    if not _IGNORED[0](P(c["policy"])):
        hit("REFUSE.D5")
        refuse("D-5: the frozen TRAIN policy path %s (per-leaf model picks; the registration publishes aggregate G only) is not"
               " git-ignored or is tracked; it must never be committed (the scratch/ pattern of .gitignore covers it)" % c["policy"])
    say("D-5: the frozen TRAIN policy %s is git-ignored and untracked (per-leaf picks; never committed; its sha256 is printed)"
        % c["policy"])
    rc, msg = _POOL[0](c["pool"])
    say("POOL CHECK (B0-2): rc %d | %s" % (rc, msg))
    if rc != 0:
        refuse("the B0-2 pool check failed: %s" % msg)
    denominators(say)
    pairs, val, ksrc, commit, single = afu_state(say)
    man, msha = load_inputs(say)
    if man["ksrc"] != ksrc:
        refuse("the inputs were built at leaf counts %s, the AF-U snapshots now give %s" % (man["ksrc"], ksrc))
    ak_identity(say)
    ip = input_paths()
    b, _meta = GC.load_bundle(P(ip["bundle"]), expect=(c["pool"], c["n_eval_before"], c["comp_before"]), sides=None)
    if (len(b["eval_y"]), len(set(b["eval_comp"].tolist()))) != (c["n_fl"], c["comp_fl"]):
        refuse("the AF-U bundle holds %d EVAL items in %d components, not the registered %d / %d" % (
            len(b["eval_y"]), len(set(b["eval_comp"].tolist())), c["n_fl"], c["comp_fl"]))
    R = ak_compute(b, sum(ksrc.values()), ksrc, c["sources"], ladder=True, single=tuple(single))
    R["single"] = single
    akL, akW = ak_lines(R)
    # R4: the K-cells files re-derived from the recomputed centroids, item by item, on the bundle's items
    classes = [str(x) for x in b["classes"]]
    Xt, yt, Xe, ye = unit_bundle(b)
    tsrc = np.array([src_of(classes[i]) for i in yt])
    esrc = np.array([src_of(classes[i]) for i in ye])
    items = [str(x) for x in b["train_item"]] + [str(x) for x in b["eval_item"]]
    X = np.vstack([Xt, Xe])
    S_ = np.concatenate([tsrc, esrc])
    for s in SEEDS:
        kc, _d = V.load_tree_cells(P(ip["k"][s]), man["inputs"][ip["k"][s]])
        C, csrc, cloc, _lab, _f = us_fit(Xt, tsrc, ksrc, c["sources"], s)
        diff = 0
        for j, it in enumerate(items):
            g = file_by_source(X[j], [S_[j]], C, csrc)
            if kc.get(it) != "K%d:%s:%03d" % (s, csrc[g], cloc[g]):
                diff += 1
        if diff:
            hit("REFUSE.K_REDERIVE")
            refuse("R4: the K-cells file of seed %d differs from the recomputed centroids on %d of %d bundle items" % (s, diff, len(items)))
    say("  R4: K0..K4 re-derived from the recomputed centroids on all %d bundle items: EQUAL" % len(items))
    lp = P(c["leg_u_policy"])
    if not os.path.isfile(lp):
        refuse("leg U's frozen TRAIN policy %s is absent (R3)" % c["leg_u_policy"])
    leg_u = json.load(open(lp, encoding="utf-8"))
    lsha = sha256_bytes(lp)
    say("R3 (before EVAL opens): leg U's frozen TRAIN policy %s sha256 %s (best single %s)" % (c["leg_u_policy"], lsha, leg_u["best_single"]))
    val_desc = P("%s/graft_descent/seed_42/validation" % c["afu"])
    cfg = make_cfg(man, say)
    cfg.rp13 = dict(leg_u_policy=leg_u, leg_u_sha=lsha, ak_lines=akL, ak_words=akW, pre_lines=pre,
                    info=dict(ksrc=ksrc, n_leaves=sum(ksrc.values()), p_fl="%.4f" % R["p_fl"], d_fd=d_fd_text(b, val_desc), single=single))
    say("--- v2_declared_cells leg U with the AF arm and K0..K4 (C0, B3, B1, the EVAL key read, B = %d) ---" % cfg.reg["B"])
    res = V.mode(cfg, "U", False)
    hit("RUN.DONE")
    return res


# ── CLI ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--build-inputs", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--only", nargs="*", default=None, help="--mutants: run only the mutants whose names start with these")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if a.mutants:
        return run_mutants(a.only)
    if V.MUTANT is not None:
        refuse("v2_declared_cells.MUTANT is set")
    if a.dry_run:
        return dry_run(out)
    if a.build_inputs:
        build_inputs(out)
        return 0
    run(out)
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────

FX_MEMBERS = (("bbh", "BBH"), ("math", "MATH"), ("mmlu", "MMLU_PRO"))
FX_SOURCES = ("MMLU_PRO", "BBH", "MATH")
# fixture AF-U leaves: (source, leaf id, the strata it collects); MMLU_PRO:L9 has no item (no TRAIN profile, R8)
FX_LEAVES = (("BBH", "L0", ("b0",)), ("BBH", "L1", ("b1", "b2")), ("MATH", "L0", ("z0", "tiny")),
             ("MMLU_PRO", "L0", ("x0",)), ("MMLU_PRO", "L1", ("x1",)), ("MMLU_PRO", "L2", ("x2",)), ("MMLU_PRO", "L9", ()))
FX_DIM = 8


class _Fx:
    pass


def _fx_vec(rs, si):
    v = np.zeros(FX_DIM)
    v[si % FX_DIM] = 1.0
    v = v + 0.55 * rs.normal(0, 1, FX_DIM)
    return v / np.linalg.norm(v)


def _write_csv(path, head, rows):
    import csv
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(head)
        for r in rows:
            w.writerow(r)


FX_SINGLE_ROWS = (("1", "0.02111", "2"), ("1", "0.01790", "3"), ("2", "0.02111", "2"))   # (iter, sep, emK) of the one-cell evidence


def _fx_single_evidence(tmp, afu, member, source, rows=FX_SINGLE_ROWS, n_site=450, decision="NO_PROPOSAL", bar="0.02500",
                        log_line=REFUSAL_LINE, snapshot=False, anchor_free=True, toml_sha=None, site2=False, commit="fixturecommit0",
                        console_site="n00000001"):
    """The refusal evidence of a one-cell member as the engine writes it (ops 9a41adfe's ifeval layout)."""
    d = os.path.join(tmp, *afu.split("/"), member, "seed_42")
    os.makedirs(os.path.join(d, "diagnostics"), exist_ok=True)
    with open(os.path.join(d, "diagnostics", "proposals.csv"), "w", encoding="utf-8", newline="") as f:
        f.write("iter,type,site_id,site_label,dJ,SE_dJ,z,dV,decision,reason,n_site\n")
        for j, (it, sep, emk) in enumerate(rows):
            site = "n00000002" if (site2 and j == 1) else "n00000001"
            f.write('%s,GROW,%s,%s,,,,,%s,"min_pair_sep_below_bar(sep=%s,bar=%s,k=2,emK=%s)",%d\n' % (it, site, source, decision, sep, bar, emk, n_site))
    with open(os.path.join(d, "headless_run.log"), "w", encoding="utf-8") as f:
        f.write("14:04:34 [INFO ] Engine - Early stopping\n" + ("Successfully generated and saved snapshot. Snapshot ID: 20261003_x\n" if snapshot else ""))
    with open(os.path.join(tmp, *afu.split("/"), member, "build.log"), "w", encoding="utf-8") as f:
        f.write("> Task :bootRun\n" + ("java.lang.IllegalStateException: " + log_line + ": the root was never split (or lost every child)."
                                      " see diagnostics/proposals.csv for the root's GROW rows (siteId=%s)\n" % console_site if log_line else ""))
    tp = os.path.join(tmp, "res", "tomls", member + ".toml")
    os.makedirs(os.path.dirname(tp), exist_ok=True)
    if not os.path.exists(tp):
        with open(tp, "w", encoding="utf-8", newline="\n") as f:
            f.write("# fixture member TOML %s\nanchorFree = true\n" % member)
    with open(os.path.join(d, "diagnostics", "run_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(dict(commit=commit, duration_ms=1, anchor_free=anchor_free,
                       split_v2=dict(config_sha256_lf=toml_sha or sha256_lf(tp))), f)


def _fx_write_decl(tmp, afu, entries):
    p_ = os.path.join(tmp, *afu.split("/"), "single_cell_members.json")
    if os.path.exists(p_):
        os.remove(p_)
    with open(p_, "w", encoding="utf-8") as f:
        json.dump(dict(test=TEST_ID, members=[dict(member=m, source=s_, best_root_sep=b, n_site=n, bar=0.025) for m, s_, b, n in entries]), f)


def _fixture(tmp, misfile=0.12, seed=5, extra_desc=False, single=None):
    """A complete layout under tmp: the v2_declared_cells fixture views, the AF-U member snapshots and graft CSVs, a B0
    layout (the same items, its own snapshots), the stubs for sides / texts / vectors; -> _Fx."""
    fx = _Fx()
    fx.tmp = tmp
    spec = V._fixture_spec()
    fx.spec = spec
    rs = np.random.RandomState(seed)
    mc6 = [it for it in spec["items"] if "mc6" in it["cvs"]]
    strata = sorted({(it["src"], it["dom"]) for it in mc6})
    sidx = {k: i for i, k in enumerate(strata)}
    fx.vec = {it["id"]: _fx_vec(rs, sidx[(it["src"], it["dom"])]) for it in mc6}
    leaf_of = {}
    for so, lid, doms in FX_LEAVES:
        for d in doms:
            leaf_of[(so, d)] = "%s:%s" % (so, lid)
    # routing rows; one TRAIN item has none (no-row), one EVAL MATH item carries a second row under MMLU_PRO/x0 (multi-class,
    # two sources), one TRAIN item is unrouted, one EVAL item has two rows in two leaves (a tie: the smaller id wins)
    train_ids = [it["id"] for it in mc6 if it["side"] == "TRAIN"]
    eval_ids = [it["id"] for it in mc6 if it["side"] == "EVAL"]
    fx.no_row = train_ids[3]
    fx.unrouted = train_ids[7]
    fx.mc = [it["id"] for it in mc6 if it["side"] == "EVAL" and it["src"] == "MATH" and it["dom"] == "z0"][2]
    fx.tie = [it["id"] for it in mc6 if it["side"] == "EVAL" and it["src"] == "BBH" and it["dom"] == "b1"][1]
    fx.vec[fx.mc] = _fx_vec(np.random.RandomState(99), sidx[("MMLU_PRO", "x0")])
    rows_q, rows_t, filed = [], [], {}
    leaves_by_src = defaultdict(list)
    for so, lid, _d in FX_LEAVES:
        leaves_by_src[so].append("%s:%s" % (so, lid))
    for it in mc6:
        if it["id"] == fx.no_row:
            continue
        lf = leaf_of[(it["src"], it["dom"])]
        if rs.rand() < misfile:
            others = [x for x in leaves_by_src[it["src"]] if x != lf and not x.endswith("L9")]
            if others:
                lf = others[rs.randint(len(others))]
        if it["id"] == fx.unrouted:
            lf = ""
        filed[it["id"]] = lf
    # TRAIN-majority names of the leaves (leaf_dominant)
    cnt = defaultdict(Counter)
    for it in mc6:
        if it["side"] == "TRAIN" and filed.get(it["id"]):
            cnt[filed[it["id"]]]["%s/%s" % (it["src"], it["dom"])] += 1
    dom_of = {lf: (min(k for k, v in c_.items() if v == max(c_.values())) if c_ else "") for lf, c_ in cnt.items()}
    fx.dom_of = dom_of
    def row(it, lf, key=None):
        key = key or "%s/%s" % (it["src"], it["dom"])
        return [key, src_of(key), "flatLeaf", lf, dom_of.get(lf, ""), 2 if lf else "", dom_of.get(lf, "") if lf else "", "1.0",
                "", "", "", "", "", it["id"]]
    for it in mc6:
        if it["id"] not in filed:
            continue
        r = row(it, filed[it["id"]])
        (rows_t if it["side"] == "TRAIN" else rows_q).append(r)
        if it["id"] == fx.mc:
            rows_q.append(row(it, filed[it["id"]], key="MMLU_PRO/x0"))
        if it["id"] == fx.tie:
            rows_q.append(row(it, "BBH:L0"))
            rows_q[-2][3] = "BBH:L1"
            rows_q[-2][4] = rows_q[-2][6] = dom_of["BBH:L1"]
    fx.filed = filed
    if single:                                                   # the graft omits a one-cell member: none of its rows or leaves
        rows_q = [r for r in rows_q if src_of(r[0]) != single]
        rows_t = [r for r in rows_t if src_of(r[0]) != single]
    c = dict(REG)
    afu = "res/AF-U"
    val = afu + "/graft_flatleaf/seed_42/validation"
    _write_csv(os.path.join(tmp, *val.split("/"), RP.QUERIES), GB.Q_HEAD, rows_q)
    _write_csv(os.path.join(tmp, *val.split("/"), RP.TRAIN), GB.Q_HEAD, rows_t)
    lrows = [[("%s:%s" % (so, lid)), "", 2, sum(cnt["%s:%s" % (so, lid)].values()), dom_of.get("%s:%s" % (so, lid), ""), "1.0"]
             for so, lid, _d in FX_LEAVES if so != single]
    _write_csv(os.path.join(tmp, *val.split("/"), RP.LEAVES), ["leaf_id", "leaf_label", "leaf_depth", "profile_size", "leaf_dominant",
                                                               "leaf_purity"], lrows)
    for base in (afu, "res/B0"):
        for m, so in FX_MEMBERS:
            d = os.path.join(tmp, *base.split("/"), m, "seed_42")
            os.makedirs(os.path.join(d, "diagnostics"), exist_ok=True)
            nodes = [dict(id="root", parentIds=[], isLeaf=False, label=so, depth=0, vmfMu=[0.0] * FX_DIM)]
            nodes += [dict(id=lid, parentIds=["root"], isLeaf=True, label=lid, depth=1, vmfMu=[0.0] * FX_DIM)
                      for s2, lid, _d in FX_LEAVES if s2 == so]
            if base == afu and so == single:
                continue
            with open(os.path.join(d, "dag_snapshots.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps(dict(iteration=0, nodes=[])) + "\n" + json.dumps(dict(iteration=1, nodes=nodes)) + "\n")
            with open(os.path.join(d, "diagnostics", "run_manifest.json"), "w", encoding="utf-8") as f:
                json.dump(dict(commit="fixturecommit0", duration_ms=1), f)
    fx.single = single
    if single:
        sm = [m for m, so in FX_MEMBERS if so == single][0]
        fx.single_member = sm
        _fx_single_evidence(tmp, afu, sm, single)
        _fx_write_decl(tmp, afu, [(sm, single, 0.02111, 450)])
    gd = os.path.join(tmp, *afu.split("/"), "graft_flatleaf", "seed_42", "diagnostics")
    os.makedirs(gd, exist_ok=True)
    with open(os.path.join(gd, "run_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(dict(commit="fixturecommit0", duration_ms=1), f)
    if extra_desc:
        dv = os.path.join(tmp, *afu.split("/"), "graft_descent", "seed_42", "validation")
        rows_d = [list(r) for r in rows_q]
        for r in rows_d:
            r[3], r[4], r[6] = "BBH:L0", dom_of["BBH:L0"], dom_of["BBH:L0"]
        _write_csv(os.path.join(dv, RP.QUERIES), GB.Q_HEAD, rows_d)
    fx.side = {it["id"]: (it["comp"], it["side"]) for it in mc6}
    fx.strata = {it["id"]: (it["src"], it["dom"]) for it in mc6}
    fx.ksrc = {so: sum(1 for s2, _l, _d in FX_LEAVES if s2 == so) for so in FX_SOURCES}
    fx.ksrc_b0 = dict(fx.ksrc)
    if single:
        fx.ksrc[single] = 1
    fx.val, fx.afu = val, afu
    # held-out (EVAL) items before the exclusion = EVAL items with a row (a one-cell source's EVAL items get theirs); the fixture REG
    ev_rows = {r[-1] for r in rows_q if fx.side[r[-1]][1] == "EVAL"} | {
        it["id"] for it in mc6 if it["side"] == "EVAL" and it["src"] == single}
    n_before, c_before = len(ev_rows), len({fx.side[i][0] for i in ev_rows})
    n_after = n_before - 1
    c_after = len({fx.side[i][0] for i in ev_rows if i != fx.mc})
    c.update(members=FX_MEMBERS, sources=FX_SOURCES, dim=FX_DIM, afu=afu, inputs="res/inputs", out="res/outcome.txt",
             policy="res/scratch/pol.json", marker="res/READ_STARTED", leg_u_policy="res/legU/pol.json",
             n_fl=n_after, comp_fl=c_after, n_eval_before=n_before, comp_before=c_before,
             n_train_fit=len(rows_t), b0_bundle="res/inputs/af_u_bundle_256", b0_dir="res/B0",
             b0_ksrc=dict(fx.ksrc_b0), b0_dim=FX_DIM, pool=RP.POOL_UNION, tomls="res/tomls",
             single_decl=afu + "/single_cell_members.json")
    fx.reg = c
    return fx


@contextlib.contextmanager
def _patched(fx, reg_=None):
    """The stubs: rp12_pairing's text / vector / side readers, the pool check, the v2 views, the registered constants."""
    saved = (RP.item_texts, RP.vectors, RP.sides, _ROOT[0], _POOL[0], _VDC_CFG[0], _REG[0], _SIDES[0], _TV[0], _BUNDLE[0], _IGNORED[0], _STRATA[0])
    _STRATA[0] = lambda: dict(fx.strata)
    _IGNORED[0] = lambda path: True
    RP.item_texts = lambda texts_db, mmlu_db=None: {i: i for i in fx.vec}
    RP.vectors = lambda emb_db, texts, dim: {t: fx.vec[t][:dim] / np.linalg.norm(fx.vec[t][:dim]) for t in texts if t in fx.vec}
    RP.sides = lambda path, corpus=None: (dict(fx.side), {"sha256_lf": "fixture" * 3})
    _ROOT[0] = fx.tmp
    _POOL[0] = lambda pool: (0, "fixture pool check (stub)")
    _REG[0] = reg_ or fx.reg
    _SIDES[0] = lambda: RP.sides(None)
    _TV[0] = lambda ids, dim: {i: fx.vec[i] for i in ids}
    _BUNDLE[0] = lambda validation, stem, dim, out: RP.g13_bundle(validation, None, "texts", None, "emb", stem, dim=dim, out=out)
    _VDC_CFG[0] = lambda: fx.cfg_factory()
    try:
        yield
    finally:
        (RP.item_texts, RP.vectors, RP.sides, _ROOT[0], _POOL[0], _VDC_CFG[0], _REG[0], _SIDES[0], _TV[0], _BUNDLE[0], _IGNORED[0], _STRATA[0]) = saved


def _fx_vdc_plain(fx):
    """A plain leg U run on the fixture views: the fixture's C1 digits, its leg U policy file, n / components."""
    cfg = V._fixture_cfg(fx.tmp, fx.spec, "legU")
    with contextlib.redirect_stdout(io.StringIO()):
        ru = V.mode(cfg, "U", False)
    c1 = ru["st"]["C1"]
    fx.reg["identity"] = (pp(c1["point"]), pp(c1["lo"]), pp(c1["hi"]))
    fx.reg["n_route"], fx.reg["comp_route"] = ru["D"].n_eval, ru["D"].eval_units["n_units"]
    fx.reg["leg_u_policy"] = os.path.relpath(cfg.policy_path, fx.tmp).replace(os.sep, "/")
    fx.c1 = c1
    k = [0]
    def factory():
        k[0] += 1
        return V._fixture_cfg(fx.tmp, fx.spec, "rp13_%d" % k[0])
    fx.cfg_factory = factory
    return ru


def _oracle_ak(fx, b, L, ksrc):
    """INDEPENDENT AK: direct FM.spherical_kmeans calls, naming and filing by plain loops."""
    classes = [str(x) for x in b["classes"]]
    Xt = FM.unit_rows(np.asarray(b["train_X"], float)); yt = [int(x) for x in b["train_y"]]
    Xe = FM.unit_rows(np.asarray(b["eval_X"], float)); ye = [int(x) for x in b["eval_y"]]
    fl = [int(x) for x in b["eval_fl"]]
    def name(labels, k, ys):
        out = []
        for j in range(k):
            cc = Counter(ys[i] for i in range(len(ys)) if labels[i] == j)
            if not cc:
                out.append(-1)
                continue
            top = max(cc.values())
            out.append(min((c_ for c_, v in cc.items() if v == top), key=lambda c_: classes[c_]))
        return out
    def filing(C, names):
        return [int(names[int(np.argmax([float(np.dot(x, cc)) for cc in C]))] == ye[i]) for i, x in enumerate(Xe)]
    pu, pus, ok_u0, ok_us0 = {}, {}, None, None
    for s in SEEDS:
        r = FM.spherical_kmeans(Xt, L, s, max_iter=300)
        ok = filing(r["centers"], name(list(r["labels"]), L, yt))
        pu[s] = sum(ok) / len(ok)
        if s == 0:
            ok_u0 = ok
        Cs, Ns = [], []
        for so in fx.reg["sources"]:
            idx = [i for i in range(len(yt)) if src_of(classes[yt[i]]) == so]
            r = FM.spherical_kmeans(Xt[idx], ksrc[so], s, max_iter=300)
            Cs.extend(list(r["centers"]))
            Ns.extend(name(list(r["labels"]), ksrc[so], [yt[i] for i in idx]))
        ok = filing(Cs, Ns)
        pus[s] = sum(ok) / len(ok)
        if s == 0:
            ok_us0 = ok
    d_u = sum(f - o for f, o in zip(fl, ok_u0)) / len(fl)
    d_us = sum(f - o for f, o in zip(fl, ok_us0)) / len(fl)
    groups = GC.comp_groups(b["eval_comp"])
    lo1, hi1, _ = GC.boot(np.array(fl) - np.array(ok_u0), groups)
    lo2, hi2, _ = GC.boot(np.array(fl) - np.array(ok_us0), groups)
    return dict(p_fl=sum(fl) / len(fl), pu=pu, pus=pus, d_u=d_u, d_us=d_us, spread_u=max(pu.values()) - min(pu.values()),
                spread_us=max(pus.values()) - min(pus.values()), ci1=(lo1, hi1), ci2=(lo2, hi2))


def _oracle_ak_mirror(fx, b, L, ksrc, single):
    """INDEPENDENT C-S1 oracle (plain loops, direct FM.spherical_kmeans calls): AK1 at k = L - |single| on the other sources'
    TRAIN, the one-cell source's EVAL items to its TRAIN-majority class; AK2 per source, the one-cell source's EVAL items to its
    single centroid's name, every other item to the nearest centroid of a NON-one-cell source."""
    classes = [str(x) for x in b["classes"]]
    Xt = FM.unit_rows(np.asarray(b["train_X"], float)); yt = [int(x) for x in b["train_y"]]
    Xe = FM.unit_rows(np.asarray(b["eval_X"], float)); ye = [int(x) for x in b["eval_y"]]
    fl = [int(x) for x in b["eval_fl"]]
    tsrc = [src_of(classes[c_]) for c_ in yt]
    esrc = [src_of(classes[c_]) for c_ in ye]

    def name(labels, k, ys):
        out = []
        for j in range(k):
            cc = Counter(ys[i] for i in range(len(ys)) if labels[i] == j)
            top = max(cc.values()) if cc else None
            out.append(min((c_ for c_, v in cc.items() if v == top), key=lambda c_: classes[c_]) if cc else -1)
        return out

    def maj(so):
        cc = Counter(yt[i] for i in range(len(yt)) if tsrc[i] == so)
        top = max(cc.values())
        return min((c_ for c_, v in cc.items() if v == top), key=lambda c_: classes[c_])
    pu, pus, ok_u0, ok_us0 = {}, {}, None, None
    for s_ in SEEDS:
        rest = [i for i in range(len(yt)) if tsrc[i] not in single]
        r = FM.spherical_kmeans(Xt[rest], L - len(single), s_, max_iter=300)
        nm = name(list(r["labels"]), L - len(single), [yt[i] for i in rest])
        ok = []
        for i, x in enumerate(Xe):
            pred = maj(esrc[i]) if esrc[i] in single else nm[int(np.argmax([float(np.dot(x, c_)) for c_ in r["centers"]]))]
            ok.append(int(pred == ye[i]))
        pu[s_] = sum(ok) / len(ok)
        ok_u0 = ok if s_ == 0 else ok_u0
        cents = []
        for so in fx.reg["sources"]:
            idx = [i for i in range(len(yt)) if tsrc[i] == so]
            r = FM.spherical_kmeans(Xt[idx], ksrc[so], s_, max_iter=300)
            for j, c_ in zip(range(ksrc[so]), name(list(r["labels"]), ksrc[so], [yt[i] for i in idx])):
                cents.append((so, r["centers"][j], c_))
        ok = []
        for i, x in enumerate(Xe):
            if esrc[i] in single:
                pred = [t for t in cents if t[0] == esrc[i]][0][2]
            else:
                pred = max((t for t in cents if t[0] not in single), key=lambda t: float(np.dot(x, t[1])))[2]
            ok.append(int(pred == ye[i]))
        pus[s_] = sum(ok) / len(ok)
        ok_us0 = ok if s_ == 0 else ok_us0
    groups = GC.comp_groups(b["eval_comp"])
    lo1, hi1, _ = GC.boot(np.array(fl) - np.array(ok_u0), groups)
    lo2, hi2, _ = GC.boot(np.array(fl) - np.array(ok_us0), groups)
    return dict(p_fl=sum(fl) / len(fl), pu=pu, pus=pus, d_u=sum(f - o for f, o in zip(fl, ok_u0)) / len(fl),
                d_us=sum(f - o for f, o in zip(fl, ok_us0)) / len(fl), spread_u=max(pu.values()) - min(pu.values()),
                spread_us=max(pus.values()) - min(pus.values()), ci1=(lo1, hi1), ci2=(lo2, hi2))


def _naive_arm(spec, cells):
    """INDEPENDENT leg U accuracy of a per-cell argmax policy (plain loops over the fixture's raw rows; UNUSABLE_CELL, MATH-FIX)."""
    mu = sorted(spec["models_u"])
    side = {it["id"]: it for it in spec["items"] if "mc6" in it["cvs"]}
    vals = defaultdict(list)
    for r in spec["responses"]:
        if r["cv"] != "mc6" or r["side"] == "GATE":
            continue
        vals[(r["item"], r["model"])].append(r["mf"] if r["mf"] is not None else r["c"])
    val = {k: v[0] for k, v in vals.items() if len(v) == 1}
    comp = lambda i: all((i, m) in val for m in mu)
    tr = [i for i, it in side.items() if it["side"] == "TRAIN" and comp(i)]
    ev = [i for i, it in side.items() if it["side"] == "EVAL" and comp(i)]
    tot = {m: sum(val[(i, m)] for i in tr) for m in mu}
    best = max(mu, key=lambda m: (tot[m], -mu.index(m)))
    per = defaultdict(lambda: defaultdict(int))
    for i in tr:
        for m in mu:
            per[cells[i]][m] += val[(i, m)]
    pol = {k: max(mu, key=lambda m: (d[m], -mu.index(m))) for k, d in per.items()}
    acc = sum(val[(i, pol.get(cells[i], best))] for i in ev) / len(ev)
    bs = sum(val[(i, best)] for i in ev) / len(ev)
    return acc, bs


def _fx_full(tmp, misfile=0.12, extra_desc=False, single=None):
    fx = _fixture(tmp, misfile=misfile, extra_desc=extra_desc, single=single)
    with _patched(fx):
        with contextlib.redirect_stdout(io.StringIO()):
            build_inputs(out=lambda s: None)
    # the B0 identity strings of the fixture: the INDEPENDENT oracle on the same bundle (B0 = the AF-U bundle here)
    b, _m = GC.load_bundle(os.path.join(tmp, "res", "inputs", "af_u_bundle_256"), expect=None)
    o = _oracle_ak(fx, b, sum(fx.ksrc_b0.values()), fx.ksrc_b0)
    fx.reg["ak_identity"] = dict(d_u="%+.4f" % o["d_u"], d_us="%+.4f" % o["d_us"], spread_u="%.4f" % o["spread_u"],
                                 spread_us="%.4f" % o["spread_us"])
    fx.oracle, fx.bundle = (o if not single else _oracle_ak_mirror(fx, b, sum(fx.ksrc.values()), fx.ksrc, {single})), b
    fx.oracle_reg = _oracle_ak(fx, b, sum(fx.ksrc.values()), fx.ksrc) if single else None
    _fx_vdc_plain(fx)
    return fx


def _capture(fn, fx, reg_=None):
    """-> (every printed line, this script's and v2_declared_cells' stdout interleaved in order, the refusal text or None)."""
    buf = io.StringIO()
    with _patched(fx, reg_):
        with contextlib.redirect_stdout(buf):
            try:
                fn(out=lambda s: print(s, flush=True))
                err = None
            except SystemExit as e:
                err = str(e)
    return buf.getvalue().splitlines(), err


def _need(text, *needles):
    for n in needles:
        if n not in text:
            raise AssertionError("missing %r" % n[:160])


def st_builders(tmp):
    fx = _fixture(tmp)
    with _patched(fx):
        with contextlib.redirect_stdout(io.StringIO()):
            man = build_inputs(out=lambda s: None)
        side, _m = RP.sides(None)
        cells, cnt = af_cells(os.path.join(tmp, *fx.val.split("/")), side)
    # R1 values: the modal leaf_id, the tie to the smaller id, <unrouted>, the no-row fill, the multi-class item kept
    assert cells[fx.tie] == "BBH:L0", cells[fx.tie]
    assert cells[fx.unrouted] == UNROUTED and cells[fx.no_row] == NO_ROW
    assert cells[fx.mc] == fx.filed[fx.mc] and cnt["multi_eval"] == 1 and cnt["no_row_train"] == 1 and cnt["no_row_eval"] == 0
    for it, lf in fx.filed.items():
        if it not in (fx.tie, fx.unrouted) and fx.side[it][1] in ("TRAIN", "EVAL"):
            assert cells[it] == lf, (it, cells[it], lf)
    assert not any(v in fx.dom_of.values() for v in cells.values()), "an AF cell carries a declared-class name (R1)"
    assert man["ksrc"] == fx.ksrc and man["n_leaves"] == 7
    txt = open(os.path.join(tmp, "res", "inputs", "af_cells.tsv"), encoding="utf-8").read()
    assert txt.startswith("# taxoarena-tree-cells-v1 ") and "\n%s\t%s\n" % (fx.tie, "BBH:L0") in txt
    # R2-R4: the K cells against an INDEPENDENT oracle (direct per-source fits; filing by loops among the allowed sources)
    b, _m = GC.load_bundle(os.path.join(tmp, "res", "inputs", "af_u_bundle_256"), expect=None)
    classes = [str(x) for x in b["classes"]]
    Xt = FM.unit_rows(np.asarray(b["train_X"], float)); yt = list(b["train_y"])
    for s in (0, 3):
        kc, _d = V.load_tree_cells(os.path.join(tmp, "res", "inputs", "k_cells_s%d.tsv" % s), man["inputs"]["res/inputs/k_cells_s%d.tsv" % s])
        cents = []
        for so in FX_SOURCES:
            idx = [i for i in range(len(yt)) if src_of(classes[yt[i]]) == so]
            r = FM.spherical_kmeans(Xt[idx], fx.ksrc[so], s, max_iter=300)
            cents.extend([(so, j, r["centers"][j]) for j in range(fx.ksrc[so])])
        for it, cell in kc.items():
            if it == fx.no_row:
                assert cell == NO_ROW
                continue
            allowed = {"MATH", "MMLU_PRO"} if it == fx.mc else {[x for x in fx.spec["items"] if x["id"] == it][0]["src"]}
            x = fx.vec[it]
            so, j, _c = max((t for t in cents if t[0] in allowed), key=lambda t: float(np.dot(x, t[2])))
            assert cell == "K%d:%s:%03d" % (s, so, j), (s, it, cell, so, j)
    kc0, _d = V.load_tree_cells(os.path.join(tmp, "res", "inputs", "k_cells_s0.tsv"), man["inputs"]["res/inputs/k_cells_s0.tsv"])
    assert ":MMLU_PRO:" in kc0[fx.mc], kc0[fx.mc]                    # filed among BOTH its sources (R3), here MMLU_PRO's centre
    # write-once: a second build refuses, files unchanged; write_x refuses an existing path
    lines, err = _capture(build_inputs, fx)
    assert err and "input file(s) exist (write-once)" in err, err
    try:
        write_x(os.path.join(tmp, "res", "inputs", "af_cells.tsv"), "x")
        raise AssertionError("write_x overwrote")
    except FileExistsError:
        pass


def st_ak_e2e(tmp):
    fx = _fx_full(tmp)
    o = fx.oracle
    with _patched(fx):
        R = ak_compute(fx.bundle, sum(fx.ksrc.values()), fx.ksrc, FX_SOURCES, ladder=True)
        L, W = ak_lines(R)
    assert "%.4f" % R["p_fl"] == "%.4f" % o["p_fl"]
    assert ["%.4f" % R["p_u"][s] for s in SEEDS] == ["%.4f" % o["pu"][s] for s in SEEDS], (R["p_u"], o["pu"])
    assert ["%.4f" % R["p_us"][s] for s in SEEDS] == ["%.4f" % o["pus"][s] for s in SEEDS], (R["p_us"], o["pus"])
    assert "%+.4f" % R["AK1"]["d"] == "%+.4f" % o["d_u"] and "%+.4f" % R["AK2"]["d"] == "%+.4f" % o["d_us"]
    assert "%.4f" % R["spread_au"] == "%.4f" % o["spread_u"] and "%.4f" % R["spread_aus"] == "%.4f" % o["spread_us"]
    assert abs(R["AK1"]["lo"] - o["ci1"][0]) < 1e-12 and abs(R["AK2"]["hi"] - o["ci2"][1]) < 1e-12
    assert R["L"] == 7 and R["n_major"] == 6, (R["L"], R["n_major"])          # R8: k = all snapshot leaves, 6 with a profile
    assert len(set(o["pu"].values())) > 1                                      # the fixture spreads the U seeds
    t = "\n".join(L)
    _need(t, "D_AU = P_fl - P(U_0) %+.4f  95%% [%+.4f, %+.4f]" % (o["d_u"], o["ci1"][0], o["ci1"][1]),
          "spread_AU %.4f" % o["spread_u"], "spread_AUs %.4f" % o["spread_us"], "D_AUs = P_fl - P(US_0) %+.4f" % o["d_us"])
    v1 = "HELD" if (o["ci1"][0] > 0 and o["d_u"] > o["spread_u"]) else "REVERSED" if (o["ci1"][1] < 0 and o["d_u"] < -o["spread_u"]) else "UNDETERMINED"
    v2 = "HELD" if (o["ci2"][0] > 0 and o["d_us"] > o["spread_us"]) else "REVERSED" if (o["ci2"][1] < 0 and o["d_us"] < -o["spread_us"]) else "UNDETERMINED"
    fak = "FIRES" if o["ci2"][1] <= o["spread_us"] else "NOT FIRED"
    assert (W["AK1"], W["AK2"], W["F-AK"]) == (v1, v2, fak), (W, v1, v2, fak)


def st_run_e2e(tmp):
    fx = _fx_full(tmp)
    lines, err = _capture(run, fx)
    assert err is None, err
    out = open(os.path.join(tmp, "res", "outcome.txt"), encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL pv_u (V2-DECLARED-CELLS leg U")
    _need(out, "  | POOL %s (UNION-AF-ROUTE, RP13; --run" % RP.POOL_UNION, "  |   -> AK-IDENTITY REPRODUCED", "  |   R4: K0..K4 re-derived",
          "  | R3 (before EVAL opens): leg U's frozen TRAIN policy", "REPRODUCED to the printed digits", "=== UNION-AF-ROUTE U1-U3", "=== AF-VS-KMEANS",
          "R3 / R10 (before the EVAL view opened): the declared arm's frozen TRAIN policy",
          "DISCLOSURE (D-4): K_s files every item among the centroids of its TRUE declared source",
          "D-5: the frozen TRAIN policy res/scratch/pol.json is git-ignored and untracked")
    vdc_part = out.split("--- EVAL (eval_view")[0]
    assert "R3 / R10 (before the EVAL view opened)" in vdc_part, "R10 did not run before the EVAL view opened (C-4)"
    # U values against the INDEPENDENT naive policy accuracies (AF cells, each K_s)
    man = json.load(open(os.path.join(tmp, "res", "inputs", "inputs_manifest.json")))
    af, _ = V.load_tree_cells(os.path.join(tmp, "res", "inputs", "af_cells.tsv"), man["inputs"]["res/inputs/af_cells.tsv"])
    acc_af, bs = _naive_arm(fx.spec, af)
    g_af = acc_af - bs
    gks = []
    for s in SEEDS:
        kc, _ = V.load_tree_cells(os.path.join(tmp, "res", "inputs", "k_cells_s%d.tsv" % s), man["inputs"]["res/inputs/k_cells_s%d.tsv" % s])
        a_, b_ = _naive_arm(fx.spec, kc)
        gks.append(a_ - b_)
    acc_d, _bs2 = _naive_arm(fx.spec, {it["id"]: "%s/%s" % (it["src"], it["dom"]) for it in fx.spec["items"]})
    g_k = sum(gks) / len(gks)
    d_k, spread, m_af = g_af - g_k, max(gks) - min(gks), acc_af - acc_d
    import re
    def num(pat):
        m_ = re.search(pat + r" [+-]?[0-9.]+pp \(([+-]?[0-9.]+)\)", out)
        if not m_:
            raise AssertionError("no line %r" % pat)
        return float(m_.group(1))
    for pat, want in ((r"G_AF = acc\(AF-U leaf cells\) - acc\(best single\) =", g_af), (r"G_K = mean over s =", g_k),
                      (r"spread_K = max - min over s =", spread), (r"D_K = G_AF - G_K =", d_k), (r"M_AF = G_AF - G_declared =", m_af)):
        got = num(pat)
        assert abs(got - want) <= 6e-6, (pat, got, want)                  # the printed 5 dp against the independent value
    for s, g in zip(SEEDS, gks):
        assert abs(num(r"K%d" % s) - g) <= 6e-6, (s, g)
    assert len(set("%.5f" % g for g in gks)) > 1, gks                                     # the seeds differ: spread > 0
    # the verdict words recomputed from the printed intervals by hand rules
    m1 = re.search(r"U1: G_AF = .*? \| two-stage \[([+-][0-9.]+)pp, ([+-][0-9.]+)pp\]", out)
    lo, hi = float(m1.group(1)), float(m1.group(2))
    want = "HELD" if lo > 0 else "FAILED" if hi <= 0 else "UNDETERMINED"
    _need(out, "  U1 -> %s" % want)
    m2 = re.search(r"D_K = G_AF - G_K = [+-][0-9.]+pp \(([+-]?[0-9.]+)\) \| two-stage \[([+-][0-9.]+)pp, ([+-][0-9.]+)pp\]", out)
    dkp, dlo, dhi = float(m2.group(1)), float(m2.group(2)) / 100, float(m2.group(3)) / 100
    want2 = "L-1 FIRES" if (dlo > 0 and dkp > spread) else "not fired; the REVERSE" if (dhi < 0 and dkp < -spread) else "not fired: neither"
    _need(out, "  U2 -> " + want2)
    _need(out, "k = 7 (AF-U's total leaf count, a one-cell member counted 1; 6 with a TRAIN profile)",
          "D_AU = P_fl - P(U_0) %+.4f  95%% [%+.4f, %+.4f]" % (fx.oracle["d_u"], fx.oracle["ci1"][0], fx.oracle["ci1"][1]),
          "D_AUs = P_fl - P(US_0) %+.4f  95%% [%+.4f, %+.4f]" % (fx.oracle["d_us"], fx.oracle["ci2"][0], fx.oracle["ci2"][1]))
    # write-once: a second --run refuses, outcome unchanged
    lines2, err2 = _capture(run, fx)
    assert err2 and "write-once" in err2 and open(os.path.join(tmp, "res", "outcome.txt"), encoding="utf-8").read() == out


def st_identity_tree(tmp):
    """AF cells = the declared key (an identity tree), every K_s = the source: G_AF == C1, M_AF == 0 (U3b EQUIVALENT at 0),
    G_K == the TRUE source arm, spread_K == 0, D_K == C1 - G_TSRC exactly."""
    fx = _fx_full(tmp)
    with _patched(fx):
        ip = input_paths()
        man = json.load(open(P(ip["manifest"])))
        mc6 = [it for it in fx.spec["items"] if "mc6" in it["cvs"] and it["side"] in ("TRAIN", "EVAL")]
        for rel, fn in [(ip["af"], lambda it: "%s/%s" % (it["src"], it["dom"]))] + [(ip["k"][s], lambda it: it["src"]) for s in SEEDS]:
            os.remove(P(rel))
            man["inputs"][rel] = write_x(P(rel), cells_text({it["id"]: fn(it) for it in mc6}, "identity"))
        os.remove(P(ip["manifest"]))
        write_x(P(ip["manifest"]), json.dumps(man, indent=1, sort_keys=True) + "\n")
    # the R4 re-derivation must refuse on these hand-made K files (they are not the centroids')
    lines, err = _capture(run, fx)
    assert err and "R4: the K-cells file of seed 0 differs" in err, err
    # bypass R4 for this case only by re-running the tail on the vdc fixture directly
    cfg = fx.cfg_factory()
    cfg.tree, cfg.tree_desc = V.load_tree_cells(os.path.join(tmp, *ip["af"].split("/")), man["inputs"][ip["af"]])
    cfg.xtrees = {"K%d" % s: V.load_tree_cells(os.path.join(tmp, *ip["k"][s].split("/")), man["inputs"][ip["k"][s]])[0] for s in SEEDS}
    cfg.g14_identity = fx.reg["identity"]
    cfg.policy_path = cfg.policy_path.replace("pol.json", "rp13_pol.json"); cfg.out_u = cfg.out_u.replace("U.txt", "RP13.txt")
    cfg.mark_u = cfg.mark_u.replace("U.READ_STARTED", "RP13.READ_STARTED")
    cfg.tail = rp13_tail
    cfg.pre_eval = r10_check
    with _patched(fx):
        cfg.rp13 = dict(leg_u_policy=json.load(open(P(fx.reg["leg_u_policy"]))), leg_u_sha="x", ak_lines=["AKLINE"], ak_words={},
                        info=dict(ksrc=fx.ksrc, n_leaves=7, p_fl="0.5", d_fd="NOT COMPUTED"))
        with contextlib.redirect_stdout(io.StringIO()):
            r = V.mode(cfg, "U", False)
    st = r["st"]
    tsrc = V.contrast(r["bt"], r["D"], "ALL", V.TSRC, V.BS)
    assert abs(st["G"]["point"] - fx.c1["point"]) < 1e-12 and st["M"]["point"] == 0.0 and st["M"]["se2"] == 0.0
    assert abs(st["GK"]["point"] - tsrc["point"]) < 1e-12 and abs(st["GK"]["se2"] - tsrc["se2"]) < 1e-9 and st["spread_K"] == 0.0
    assert abs(st["DK"]["point"] - (fx.c1["point"] - tsrc["point"])) < 1e-12 and abs(st["DK"]["point"]) > 1e-6
    assert r["words"]["U3b"] == "EQUIVALENT", r["words"]
    t = open(cfg.out_u, encoding="utf-8").read()
    _need(t, "M_AF = G_AF - G_declared = +0.00pp (0.00000) | two-stage [+0.00pp, +0.00pp]", "AKLINE", "LICENSED CLAUSE (U3b EQUIVALENT)")
    cfg2 = fx.cfg_factory()
    cfg2.tree, cfg2.tree_desc = cfg.tree, cfg.tree_desc
    ev_scored = [i for i, k in zip(r["D"].items, r["D"].is_eval) if k][0]
    cfg2.xtrees = {nm: dict(v) for nm, v in cfg.xtrees.items()}
    cfg2.xtrees["K0"][ev_scored] = NO_ROW
    cfg2.g14_identity, cfg2.tail, cfg2.rp13 = cfg.g14_identity, rp13_tail, cfg.rp13
    try:
        with _patched(fx):
            with contextlib.redirect_stdout(io.StringIO()):
                V.mode(cfg2, "U", False)
        raise AssertionError("an EVAL item without a K0 cell did not refuse")
    except SystemExit as e:
        assert str(e).startswith("[G14-NOROW] arm K0: 1 EVAL item(s)") and not os.path.exists(cfg2.mark_u), str(e)
    # lin() equals contrast() on a two-arm contrast
    l2 = lin(r["bt"], r["D"], "ALL", {V.TREE: 1.0, V.BS: -1.0})
    assert l2["point"] == st["G"]["point"] and abs(l2["se2"] - st["G"]["se2"]) < 1e-15
    assert max(abs(x - y) for x, y in zip(l2["pct"], st["G"]["pct"])) < 1e-15


def st_refusals(tmp_factory):
    # identity miss (declared): no outcome
    fx = _fx_full(tmp_factory())
    r2 = dict(fx.reg, identity=("+9.99pp", "+1.00pp", "+2.00pp"))
    lines, err = _capture(run, fx, r2)
    assert err and err.startswith("[RP13-IDENTITY]") and not os.path.exists(os.path.join(fx.tmp, "res", "outcome.txt")), err
    # C-3: the point equal, ONE interval end differing
    fx = _fx_full(tmp_factory())
    r2 = dict(fx.reg, identity=(fx.reg["identity"][0], fx.reg["identity"][1], pp(float(fx.reg["identity"][2][:-2]) / 100 + 0.0001)))
    lines, err = _capture(run, fx, r2)
    assert err and err.startswith("[RP13-IDENTITY]") and not os.path.exists(os.path.join(fx.tmp, "res", "outcome.txt")), err
    # C-2: a frozen extra-arm pick differing from the re-fit beside EVAL (the frozen dict altered after it was written)
    fx = _fx_full(tmp_factory())
    def tamper(cfg_, pol_, psha_, say_):
        r10_check(cfg_, pol_, psha_, say_)
        k0 = pol_["xtree_cell"]["K0"]
        c0 = sorted(k0)[0]
        k0[c0] = sorted(m for m in pol_["roster"] if m != k0[c0])[0]
    orig_make = make_cfg
    def make_t(man, say):
        cfg_ = orig_make(man, say)
        cfg_.pre_eval = tamper
        return cfg_
    globals()["make_cfg"] = make_t
    try:
        lines, err = _capture(run, fx)
    finally:
        globals()["make_cfg"] = orig_make
    assert err and err.startswith("[B3] an RP13 extra arm's policy re-fitted beside EVAL differs"), err
    # D-5: the policy path not git-ignored (or tracked) refuses before any read
    fx = _fx_full(tmp_factory())
    with _patched(fx):
        _IGNORED[0] = lambda path: False
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                run(out=lambda s_: print(s_))
            err = None
        except SystemExit as e:
            err = str(e)
    assert err and "D-5: the frozen TRAIN policy path" in err and not os.path.exists(os.path.join(fx.tmp, "res", "scratch")), err
    # AK identity miss
    fx = _fx_full(tmp_factory())
    r2 = dict(fx.reg, ak_identity=dict(fx.reg["ak_identity"], spread_us="9.9999"))
    lines, err = _capture(run, fx, r2)
    assert err and "[RP13-AK-IDENTITY]" in err and "spread_us" in err and not os.path.exists(os.path.join(fx.tmp, "res", "scratch", "pol.json")), err
    # denominator miss
    fx = _fx_full(tmp_factory())
    r2 = dict(fx.reg, n_route=fx.reg["n_route"] + 1)
    lines, err = _capture(run, fx, r2)
    assert err and err.startswith("[RP13-DENOM]"), err
    # R3: leg U's policy file with another best single
    fx = _fx_full(tmp_factory())
    lp = os.path.join(fx.tmp, *fx.reg["leg_u_policy"].split("/"))
    pj = json.load(open(lp)); pj["best_single"] = "zz-other"
    os.remove(lp); write_x(lp, json.dumps(pj))
    lines, err = _capture(run, fx)
    assert err and err.startswith("[RP13-R3]") and "best_single" in err, err
    assert not os.path.exists(os.path.join(fx.tmp, "res", "READ_STARTED"))   # C-4: refused BEFORE the B1 marker / EVAL key read
    assert os.path.exists(os.path.join(fx.tmp, "res", "scratch", "pol.json"))  # ... and after the B3 policy file
    # C-1: ONE true_source_domain pick differs, best single equal
    fx = _fx_full(tmp_factory())
    lp = os.path.join(fx.tmp, *fx.reg["leg_u_policy"].split("/"))
    pj = json.load(open(lp))
    c0 = sorted(pj["true_source_domain"])[0]
    pj["true_source_domain"][c0] = sorted(m for m in pj["roster"] if m != pj["true_source_domain"][c0])[0]
    os.remove(lp); write_x(lp, json.dumps(pj))
    lines, err = _capture(run, fx)
    assert err and err.startswith("[RP13-R3]") and "['true_source_domain']" in err, err
    assert not os.path.exists(os.path.join(fx.tmp, "res", "READ_STARTED"))
    # a pinned AF-U file changed after --build-inputs
    fx = _fx_full(tmp_factory())
    with open(os.path.join(fx.tmp, *fx.val.split("/"), RP.QUERIES), "a", encoding="utf-8") as f:
        f.write("\n")
    lines, err = _capture(run, fx)
    assert err and "pinned file(s) changed since --build-inputs" in err and RP.QUERIES in err, err
    # D-8: two commits
    fx = _fx_full(tmp_factory())
    with open(os.path.join(fx.tmp, "res", "AF-U", "math", "seed_42", "diagnostics", "run_manifest.json"), "w") as f:
        json.dump(dict(commit="othercommit"), f)
    lines, err = _capture(run, fx)
    assert err and "D-8" in err, err
    # the pool check failing
    fx = _fx_full(tmp_factory())
    with _patched(fx):
        _POOL[0] = lambda pool: (1, "stub: another pool")
        lines = []
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                run(out=lines.append)
            err = None
        except SystemExit as e:
            err = str(e)
    assert err and "B0-2 pool check failed" in err and lines[0].startswith("POOL ") and any("rc 1" in l for l in lines), (err, lines[:3])
    # a member's sources not the registered ones / leaves CSV not the snapshot set
    fx = _fx_full(tmp_factory())
    with open(os.path.join(fx.tmp, *fx.val.split("/"), RP.LEAVES), "a", encoding="utf-8") as f:
        f.write("BBH:L7,,2,0,,1.0\n")
    lines, err = _capture(dry_run, fx)
    assert err and "leaves CSV covers 8 leaves, the member snapshots 7" in err, err


def st_dry_run(tmp_factory):
    # (a) AF-U ABSENT: the POOL line first, the denominators, the AK identity, then the refusal; nothing written
    fx = _fixture(tmp_factory())
    with _patched(fx):
        with contextlib.redirect_stdout(io.StringIO()):
            build_inputs(out=lambda s: None)
    b, _m = GC.load_bundle(os.path.join(fx.tmp, "res", "inputs", "af_u_bundle_256"), expect=None)
    o = _oracle_ak(fx, b, 7, fx.ksrc)
    fx.reg["ak_identity"] = dict(d_u="%+.4f" % o["d_u"], d_us="%+.4f" % o["d_us"], spread_u="%.4f" % o["spread_u"],
                                 spread_us="%.4f" % o["spread_us"])
    import shutil
    shutil.rmtree(os.path.join(fx.tmp, "res", "AF-U", "graft_flatleaf"))
    before = sorted(os.listdir(os.path.join(fx.tmp, "res")))
    lines, err = _capture(dry_run, fx)
    t = "\n".join(lines)
    assert lines[0].startswith("POOL %s (UNION-AF-ROUTE, RP13; --dry-run" % RP.POOL_UNION), lines[0]
    _need(t, "DENOMINATORS (registered): U1-U3 %d EVAL items in %d components" % (fx.reg["n_route"], fx.reg["comp_route"]),
          "AK1 / AK2 %d EVAL items in %d components" % (fx.reg["n_fl"], fx.reg["comp_fl"]), "AK-IDENTITY REPRODUCED",
          "ABSENT  res/AF-U/graft_flatleaf/seed_42/validation/MAIN_union_routing_queries.csv")
    assert err and "AF-U build outputs ABSENT (4 of 10)" in err, err
    assert sorted(os.listdir(os.path.join(fx.tmp, "res"))) == before
    # (b) the REAL registered constants: the denominators of record are printed (the run-operator's lines)
    t2 = []
    denominators(t2.append)
    _need("\n".join(t2), "U1-U3 5907 EVAL items in 5404 components", "AK1 / AK2 6139 EVAL items in 5628 components",
          "before the exclusion 6153 / 5642", "TRAIN 12334 expected", "C1 +2.67pp [+1.46pp, +3.89pp]", "D_U +0.0738, D_Us +0.0656,"
          " spread_U 0.0414, spread_US 0.0233")
    # (c) present, inputs not built: refused
    fx = _fixture(tmp_factory())
    _fx_vdc_plain(fx)
    with _patched(fx):
        with contextlib.redirect_stdout(io.StringIO()):
            build_inputs(out=lambda s: None)
    b, _m = GC.load_bundle(os.path.join(fx.tmp, "res", "inputs", "af_u_bundle_256"), expect=None)
    o = _oracle_ak(fx, b, 7, fx.ksrc)
    fx.reg["ak_identity"] = dict(d_u="%+.4f" % o["d_u"], d_us="%+.4f" % o["d_us"], spread_u="%.4f" % o["spread_u"],
                                 spread_us="%.4f" % o["spread_us"])
    os.rename(os.path.join(fx.tmp, "res", "inputs", "inputs_manifest.json"), os.path.join(fx.tmp, "res", "man.bak"))
    lines, err = _capture(dry_run, fx)
    assert err and "the inputs are not built" in err, err
    os.rename(os.path.join(fx.tmp, "res", "man.bak"), os.path.join(fx.tmp, "res", "inputs", "inputs_manifest.json"))
    # (d) present and built: the vdc dry-run runs, no statistic, nothing written
    lines, err = _capture(dry_run, fx)
    t = "\n".join(lines)
    assert err is None, err
    _need(t, "DRY-RUN: no key column was selected", "DRY-RUN: nothing written", "G14 TREE-CELL ARM")
    assert "G_AF =" not in t and "D_K =" not in t and "AK1:" not in t
    assert not os.path.exists(os.path.join(fx.tmp, "res", "outcome.txt")) and not os.path.exists(os.path.join(fx.tmp, "res", "scratch", "pol.json"))


def _syn_u(g=(0.024, 0.012, 0.036), dk=(0.001, -0.005, 0.007), m=(-0.002, -0.006, 0.002), spread=0.004, se_dk=None, se_m=None):
    def mk(p, lo, hi, se=None):
        se = se if se is not None else (hi - lo) / 3.92
        return dict(point=p, lo=lo, hi=hi, se2=se, se_iid=se * 0.9, deff=1.3, n_eff=4000.0, mde=2.8 * se, n=5907, pct=(lo, hi))
    st = dict(C1=mk(0.0267, 0.0146, 0.0389), G=mk(*g), M=mk(*m, se=se_m), DK=mk(*dk, se=se_dk), GK=mk(0.02, 0.01, 0.03),
              GK_s={"K%d" % s: mk(0.02 + 0.001 * s, 0.01, 0.03) for s in SEEDS}, names=["K%d" % s for s in SEEDS], spread_K=spread)
    return st


def _syn_info():
    return dict(ksrc={s: 10 for s in REG["sources"]}, n_leaves=60, eval_units=5404, n_train=11841, af_distinct=60, p_fl="0.7100",
                d_fd="NOT COMPUTED (R9)")


def st_branches():
    def U(**kw):
        L, W = u_lines(_syn_u(**kw), _syn_info())
        return "\n".join(L), W
    # U1
    sl = single_lines({"IFEVAL": dict(member="ifeval", best_sep=0.02111, n_site=325, cell="IFEVAL:n00000001")})
    assert sl[1] == "  IFEVAL (member ifeval): no anchor-free split clears the bar (best root separation 0.02111 < 0.025, n 325; every" \
        " root GROW row NO_PROPOSAL min_pair_sep_below_bar); counts 1 leaf (cell IFEVAL:n00000001)" and "k = 1 there" in sl[2]
    assert single_lines({}) == ["ONE-CELL MEMBERS: none (every member's anchor-free root cleared the bar 0.025)"]
    t, w = U(g=(0.024, 0.0001, 0.036)); assert "ONE-CELL MEMBERS: none" in t and "DISCLOSURE (D-4): K_s files every item among the centroids of its TRUE declared source" in t
    assert w["U1"] == "HELD" and "U1 -> HELD" in t and "F-U1 does not fire (U1 HELD)" in t
    t, w = U(g=(-0.01, -0.02, 0.0)); assert w["U1"] == "FAILED" and "F-U1 FIRES (U1 FAILED)" in t
    t, w = U(g=(0.01, 0.0, 0.02)); assert w["U1"] == "UNDETERMINED" and "U1 -> UNDETERMINED" in t        # lo = 0 is not HELD
    assert "F-U1 does not fire (U1 UNDETERMINED)" in t
    # the TOST p and the strict "inside" by hand values
    assert abs(tost_p(dict(point=0.004, se2=0.003), 0.01) - (1 - _phi(2.0))) < 1e-12
    assert abs(tost_p(dict(point=-0.004, se2=0.003), 0.01) - (1 - _phi(2.0))) < 1e-12
    assert inside(dict(point=0.5, se2=0.25), 1.0, 0.75) is False and inside(dict(point=0.5, se2=0.25), 1.0, 0.7500001) is True
    assert inside(dict(point=-0.5, se2=0.25), 1.0, 0.75) is False
    # U2
    t, w = U(dk=(0.012, 0.004, 0.02), spread=0.005)
    assert w["U2"] == "FIRES" and "L-1 FIRES" in t and "F-TAX L-1: FIRES" in t and "a lever AND N-1" in t
    t, w = U(dk=(0.005, 0.004, 0.006), spread=0.005); assert w["U2"] == "NOT FIRED"                      # D_K == spread: not fired
    t, w = U(dk=(-0.012, -0.02, -0.004), spread=0.005); assert w["U2"] == "REVERSE" and "REVERSE is observed" in t
    t, w = U(dk=(-0.003, -0.005, -0.001), spread=0.004); assert w["U2"] == "NOT FIRED" and "REVERSE" not in t    # below 0, inside spread
    t, w = U(dk=(0.001, -0.005, 0.007), spread=0.004)
    assert w["U2"] == "NOT FIRED" and "(lever leg not fired, by support: |D_K| 0.10pp <= bar" in t and "never \"no lever\"" in t
    t, w = U(dk=(0.006, -0.004, 0.016), spread=0.004, se_dk=0.00255)                                        # |D_K| > spread, <= MDE80
    assert w["U2"] == "NOT FIRED" and "(lever leg not fired, by support: |D_K| 0.60pp <= bar 0.71pp)" in t
    t, w = U(dk=(0.03, -0.001, 0.061), spread=0.004, se_dk=0.0005)
    assert w["U2"] == "NOT FIRED" and "by support" not in t and "F-TAX L-1: NOT FIRED -> \"a filing device only\" (N-1 fired);" in t
    # U3 Holm: both EQUIVALENT (U3a first, smaller p); U3b first and failing stops U3a; the 90% second step; the strict boundary
    t, w = U(dk=(0.0, -0.001, 0.001), m=(0.001, -0.004, 0.006), se_dk=0.0005, se_m=0.0025)
    assert (w["U3a"], w["U3b"]) == ("EQUIVALENT", "EQUIVALENT") and "Holm order U3a first (95%), U3b second (90%)" in t
    assert "U3b M_AF (AF against declared labels): step 2, 90% interval [-0.31pp, +0.51pp] -> EQUIVALENT" in t
    assert "LICENSED CLAUSE (U3b EQUIVALENT)" in t
    t, w = U(dk=(0.0, -0.01, 0.01), m=(0.0, -0.001, 0.001), se_dk=0.0062, se_m=0.0005)
    assert "Holm order U3b first" in t and w["U3b"] == "EQUIVALENT" and w["U3a"] == "NOT EQUIVALENT"
    assert "step 2, 90% interval [-1.02pp, +1.02pp] -> NOT EQUIVALENT (the interval leaves +-1.00pp)" in t
    t, w = U(dk=(0.0, -0.01, 0.01), m=(0.0, -0.001, 0.001), se_dk=0.0055, se_m=0.0005)
    assert w["U3a"] == "EQUIVALENT" and "step 2, 90% interval [-0.90pp, +0.90pp] -> EQUIVALENT" in t        # 95% would leave
    t, w = U(dk=(0.0, -0.001, 0.001), m=(0.0, -0.012, 0.012), se_dk=0.0005, se_m=0.0062)
    assert w["U3b"] == "NOT EQUIVALENT" and "No parity clause is licensed (U3b NOT EQUIVALENT)" in t
    t, w = U(dk=(0.0, -0.01, 0.01), m=(0.0, -0.012, 0.012), se_dk=0.0062, se_m=0.0062)
    assert (w["U3a"], w["U3b"]) == ("NOT EQUIVALENT", "NOT EQUIVALENT") and "(Holm stopped at the first step)" in t
    t, w = U(dk=(0.0, -0.01, 0.01), m=(0.0, -0.01, 0.01), se_dk=0.0058, se_m=0.0053)                      # Holm stops at step 1
    assert "Holm order U3b first" in t and (w["U3a"], w["U3b"]) == ("NOT EQUIVALENT", "NOT EQUIVALENT")
    assert "U3a D_K (AF against per-source k-means): step 2, 90% interval [-0.95pp, +0.95pp] -> NOT EQUIVALENT (Holm stopped at the first step)" in t
    se_b = 0.01 / 1.96
    t, w = U(dk=(0.0, -0.01, 0.01), m=(0.0, -0.02, 0.02), se_dk=se_b, se_m=0.01)
    assert w["U3a"] == "NOT EQUIVALENT"                                                                   # end point at +-delta: outside
    # joined record
    t, w = U(dk=(0.003, 0.0025, 0.0035), spread=0.001, se_dk=0.00025)
    assert w["U2"] == "FIRES" and w["U3a"] == "EQUIVALENT" and "recorded joined \"L-1 FIRES / U3a EQUIVALENT\"" in t
    # predictions by value
    t, w = U(g=(0.024, 0.012, 0.036), dk=(0.001, -0.005, 0.007), spread=0.005, m=(-0.002, -0.006, 0.002))
    _need(t, "PREDICTION U1 G_AF = +2.4pp [+1.2, +3.6]: observed +2.40pp -> HELD", "PREDICTION U2 D_K = +0.1pp [-0.8, +1.0]: observed +0.10pp -> HELD",
          "PREDICTION U2 spread_K = 0.5pp [0.2, 1.0]: observed +0.50pp -> HELD", "PREDICTION U3b M_AF = -0.2pp [-1.0, +0.6]: observed -0.20pp -> HELD",
          "PREDICTION leaves AF-U 70-110 in total: observed 60 -> FAILED", "D_fd NOT COMPUTED (R9)")
    t, w = U(g=(0.037, 0.03, 0.044), spread=0.0101); _need(t, "observed +3.70pp -> FAILED", "observed +1.01pp -> FAILED")
    t, w = U(g=(0.012, 0.001, 0.023), spread=0.010); _need(t, "PREDICTION U1 G_AF = +2.4pp [+1.2, +3.6]: observed +1.20pp -> HELD",
                                                           "PREDICTION U2 spread_K = 0.5pp [0.2, 1.0]: observed +1.00pp -> HELD")   # inclusive ends
    # AK branches
    def A(d1, d2, sp1=0.04, sp2=0.02):
        def mk(d, lo, hi):
            return dict(d=d, lo=lo, hi=hi, se=0.006, deff=1.3, n=6139, G=5628, n_eff=4600.0, mde=0.0168, disc=0.16)
        R = dict(n=6139, G=5628, n_train=12334, L=90, n_major=89, ksrc={s: 15 for s in REG["sources"]}, p_fl=0.71,
                 p_u={s: 0.73 for s in SEEDS}, p_us={s: 0.74 for s in SEEDS}, p_us_in={s: 0.75 for s in SEEDS},
                 spread_au=sp1, spread_aus=sp2, AK1=mk(*d1), AK2=mk(*d2), p_u0=0.73, p_us0=0.74, d_au=d1[0], d_aus=d2[0],
                 by_source={"MMLU_PRO_LB": (3478, mk(-0.01, -0.02, 0.0), mk(-0.02, -0.03, -0.01)), "GPQA": (0, None, None)},
                 p_ncc=0.80, p_kc="not computable (x)")
        L, W = ak_lines(R)
        return "\n".join(L), W
    t, w = A((0.06, 0.05, 0.07), (0.03, 0.025, 0.035))
    assert (w["AK1"], w["AK2"], w["F-AK"]) == ("HELD", "HELD", "NOT FIRED") and "AK1: HELD" in t and "F-AK does not fire" in t
    assert "GPQA n 0 D_AU n/a (0 items)" in t and "KC_0 not computable (x)" in t
    t, w = A((-0.06, -0.07, -0.05), (-0.03, -0.035, -0.025))
    assert (w["AK1"], w["AK2"], w["F-AK"]) == ("REVERSED", "REVERSED", "FIRES") and "F-AK FIRES (REVERSED): AK2's upper bound -0.0250" in t
    t, w = A((0.02, 0.01, 0.03), (0.01, -0.001, 0.02))
    assert w["AK1"] == "UNDETERMINED" and "AK1: UNDETERMINED by spread: the interval excludes 0 but |D_AU| 0.0200 <= spread_AU 0.0400;"         " reads \"not shown\", never parity and never \"no difference\"" in t
    assert w["AK2"] == "UNDETERMINED" and "AK2: UNDETERMINED: the interval [-0.0010, +0.0200] reaches 0" in t
    assert w["F-AK"] == "FIRES" and "F-AK FIRES (not better)" in t                                         # upper 0.02 <= spread 0.02
    t, w = A((0.0, -0.01, 0.01), (0.0, -0.01, 0.0201))
    assert w["F-AK"] == "NOT FIRED" and "this is never \"the tree beats k-means\" unless AK2 is HELD (AK2 UNDETERMINED)" in t
    _need(t, "PREDICTION AK1 verdict probabilities (HELD 0.10, REVERSED 0.25, UNDETERMINED 0.65): observed UNDETERMINED",
          "PREDICTION F-AK verdict probabilities (fires 0.70): observed NOT FIRED", "PREDICTION P_fl(AF-U) 0.71 [0.64, 0.78]: observed +0.7100 -> HELD")


def st_branch_cover():
    """Every print branch above is hit by st_branches (the registry; TOPIC-PARTITION D1 / D7)."""
    HIT.clear()
    st_branches()
    need = ["U.IDENTITY_OK", "U1.HELD", "U1.FAILED", "U1.UNDETERMINED", "U2.FIRES", "U2.REVERSE", "U2.NOT_FIRED", "U3a.EQ", "U3a.NEQ",
            "U3b.EQ", "U3b.NEQ", "FU1.FIRES", "FU1.NOT_FIRED", "FTAX.L1_FIRES", "FTAX.JOINED", "FTAX.L1_NOT_BY_SUPPORT", "FTAX.L1_NOT",
            "FTAX.U3B_CLAUSE", "FTAX.NO_U3B_CLAUSE", "PU.HELD", "PU.FAILED", "AK1.HELD", "AK1.REVERSED", "AK1.UNDET_SPREAD",
            "AK1.UNDET_INTERVAL", "AK2.HELD", "AK2.REVERSED", "AK2.UNDET_INTERVAL", "FAK.FIRES_REVERSED", "FAK.FIRES_NOTBETTER",
            "FAK.NOT_FIRED", "PAK.HELD"]
    miss = [n for n in need if not HIT[n]]
    assert not miss, miss


def st_desc(tmp):
    """R9: with a descent graft present, D_fd is computed (value against a hand computation)."""
    fx = _fixture(tmp, extra_desc=True)
    with _patched(fx):
        with contextlib.redirect_stdout(io.StringIO()):
            build_inputs(out=lambda s: None)
        b, _m = GC.load_bundle(os.path.join(tmp, "res", "inputs", "af_u_bundle_256"), expect=None)
        t = d_fd_text(b, os.path.join(tmp, "res", "AF-U", "graft_descent", "seed_42", "validation"))
        t0 = d_fd_text(b, os.path.join(tmp, "nothing"))
    classes = [str(x) for x in b["classes"]]
    dok = [int(classes[int(y)] == fx.dom_of["BBH:L0"]) for y in b["eval_y"]]
    want = float(np.mean(np.asarray(b["eval_fl"]) - np.asarray(dok)))
    assert t.startswith("%+.4f [" % want) and "P_descent %.4f" % np.mean(dok) in t, (t, want)
    assert t0.startswith("NOT COMPUTED"), t0


def st_vdc_inert(tmp):
    """v2_declared_cells without cfg.xtrees / cfg.tail equals blob c5b90278 (the previous blob) on its fixture with a tree:
    the G14 outcome line for line (identity lines and paths normalised) and the frozen policy key for key."""
    import importlib.util as ilu
    import subprocess
    import re
    src = subprocess.run(["git", "show", "c5b902785b89352c3bf3b23c916e953bf28a6274"], cwd=ROOT, capture_output=True, check=True).stdout
    bp = os.path.join(tmp, "v2dc_base_c5b90278.py")
    with open(bp, "wb") as f:
        f.write(src)
    spb = ilu.spec_from_file_location("v2dc_base_c5b90278", bp)
    base = ilu.module_from_spec(spb)
    spb.loader.exec_module(base)
    spec = V._fixture_spec()
    outs = {}
    for name, mod in (("new", V), ("base", base)):
        cfg = mod._fixture_cfg(tmp, spec, "inert_" + name)
        with contextlib.redirect_stdout(io.StringIO()):
            ru = mod.mode(cfg, "U", False)
        c1 = ru["st"]["C1"]
        mc6 = [it for it in spec["items"] if "mc6" in it["cvs"] and it["side"] in ("TRAIN", "EVAL")]
        pth = os.path.join(tmp, "tree_%s.tsv" % name)
        with open(pth, "w", encoding="utf-8", newline="\n") as f:
            f.write("# %s fixture\nitem_id\ttree_cell\n" % V.TREE_CELLS_FORMAT + "".join("%s\t%s\n" % (it["id"], it["src"] + ("/x" if it["dom"] in ("b0", "x1") else "")) for it in mc6))
        cfg2 = mod._fixture_cfg(tmp, spec, "inert_tree_" + name)
        cfg2.tree, cfg2.tree_desc = mod.load_tree_cells(pth, hashlib.sha256(open(pth, "rb").read()).hexdigest())
        cfg2.g14_identity = (mod._pp(c1["point"]), mod._pp(c1["lo"]), mod._pp(c1["hi"]))
        cfg2.policy_path = cfg2.policy_path.replace("pol.json", "G14_pol.json"); cfg2.out_u = cfg2.out_u.replace("U.txt", "G14.txt")
        cfg2.mark_u = cfg2.mark_u.replace("U.READ_STARTED", "G14.READ_STARTED")
        with contextlib.redirect_stdout(io.StringIO()):
            mod.mode(cfg2, "U", False)
        d = os.path.dirname(cfg2.gen_path)
        lines = []
        for l in open(cfg2.out_u, encoding="utf-8").read().splitlines():
            if "v2_declared_cells" in l or "v2dc_base_c5b90278" in l:
                continue
            l = l.replace(d, "<D>").replace(pth, "<T>")
            lines.append(re.sub(r"\| sha256 [0-9a-f]{64} \|", "| sha256 <P> |", l))
        pj = json.load(open(cfg2.policy_path))
        for k in ("script", "gen_view_sha256_bytes", "g14"):
            pj.pop(k, None)
        outs[name] = (lines, pj)
    assert outs["new"][0] == outs["base"][0] and len(outs["new"][0]) > 40, "G14 outcome differs from blob c5b90278"
    assert outs["new"][1] == outs["base"][1] and "xtree_cell" not in outs["new"][1]
    assert any("G_tree = acc(" in l for l in outs["new"][0])



def _u_values(fx, tmp, out):
    """G_AF, G_K,s, G_K, spread_K, D_K, M_AF printed to 5 dp == independent plain-loop policy accuracies -> the K_s gaps."""
    import re
    man = json.load(open(os.path.join(tmp, "res", "inputs", "inputs_manifest.json")))
    af, _ = V.load_tree_cells(os.path.join(tmp, "res", "inputs", "af_cells.tsv"), man["inputs"]["res/inputs/af_cells.tsv"])
    acc_af, bs = _naive_arm(fx.spec, af)
    g_af = acc_af - bs
    gks, kcs = [], []
    for s_ in SEEDS:
        kc, _ = V.load_tree_cells(os.path.join(tmp, "res", "inputs", "k_cells_s%d.tsv" % s_), man["inputs"]["res/inputs/k_cells_s%d.tsv" % s_])
        a_, b_ = _naive_arm(fx.spec, kc)
        gks.append(a_ - b_)
        kcs.append(kc)
    acc_d, _bs2 = _naive_arm(fx.spec, {it["id"]: "%s/%s" % (it["src"], it["dom"]) for it in fx.spec["items"]})
    g_k = sum(gks) / len(gks)
    d_k, spread, m_af = g_af - g_k, max(gks) - min(gks), acc_af - acc_d

    def num(pat):
        m_ = re.search(pat + r" [+-]?[0-9.]+pp \(([+-]?[0-9.]+)\)", out)
        if not m_:
            raise AssertionError("no line %r" % pat)
        return float(m_.group(1))
    for pat, want in ((r"G_AF = acc\(AF-U leaf cells\) - acc\(best single\) =", g_af), (r"G_K = mean over s =", g_k),
                      (r"spread_K = max - min over s =", spread), (r"D_K = G_AF - G_K =", d_k), (r"M_AF = G_AF - G_declared =", m_af)):
        got = num(pat)
        assert abs(got - want) <= 6e-6, (pat, got, want)
    return af, kcs


def st_single_e2e(tmp):
    """ONE-CELL (BBH, 2 snapshot leaves in B0, 3 declared domains): --build-inputs and --run end to end. The BBH items file to
    the one cell BBH:n00000001 (AF) and to K<s>:BBH:000 (k = 1) in every K_s; AK uses k = 6 = 4 + 1 + 1 and BBH 1; the values
    equal independent oracles; the disclosure is printed in the U and the AK block; the graft CSVs carry no BBH row."""
    fx = _fx_full(tmp, single="BBH")
    lines, err = _capture(run, fx)
    assert err is None, err
    out = open(os.path.join(tmp, "res", "outcome.txt"), encoding="utf-8").read()
    one = "  BBH (member bbh): no anchor-free split clears the bar (best root separation 0.02111 < 0.025, n 450; every root GROW row" \
          " NO_PROPOSAL min_pair_sep_below_bar); counts 1 leaf (cell BBH:n00000001)"
    assert out.count(one) == 2 and out.count("  DISCLOSURE: the flatLeaf graft omits a one-cell member") == 2, "disclosure not in both blocks"
    _need(out, "k = 6 (AF-U's total leaf count, a one-cell member counted 1; 5 with a TRAIN profile); k per source MMLU_PRO 4, BBH 1, MATH 1",
          "DESCRIPTIVE: AF-U leaves per source MMLU_PRO 4, BBH 1, MATH 1 (total 6)", "  |   ONE-CELL members (declaration res/AF-U/single_cell_members.json",
          "D_AU = P_fl - P(U_0) %+.4f  95%% [%+.4f, %+.4f]" % (fx.oracle["d_u"], fx.oracle["ci1"][0], fx.oracle["ci1"][1]),
          "D_AUs = P_fl - P(US_0) %+.4f  95%% [%+.4f, %+.4f]" % (fx.oracle["d_us"], fx.oracle["ci2"][0], fx.oracle["ci2"][1]))
    # C-S1: the MIRRORED rule decides (the lines above, against the mirror oracle); the registered nearest-of-all beside, DESCRIPTIVE
    o, g = fx.oracle, fx.oracle_reg
    _need(out, "AK2 U-source (MIRRORED, C-S1, DECIDES: one-cell BBH filed by source to its k = 1 centroid",
          "P(US_s) %s; spread_AUs %.4f; D_AUs = P_fl - P(US_0) %+.4f" % (" / ".join("%.4f" % o["pus"][s_] for s_ in SEEDS), o["spread_us"], o["d_us"]),
          "  DESCRIPTIVE (the registered nearest-of-ALL-centroids AK2, C-S1): P(US_s) %s; spread_AUs %.4f; D_AUs %+.4f  95%% [%+.4f, %+.4f]" % (
              " / ".join("%.4f" % g["pus"][s_] for s_ in SEEDS), g["spread_us"], g["d_us"], g["ci2"][0], g["ci2"][1]),
          "  DESCRIPTIVE (the registered nearest-of-all AK1, C-S1;", "D_AU %+.4f  95%% [%+.4f, %+.4f]" % (g["d_u"], g["ci1"][0], g["ci1"][1]),
          "AK1 U-global (MIRRORED, C-S1, DECIDES: one-cell BBH filed by source to its k = 1 centroid, which no other item can reach; k = 5")
    assert "%.4f" % o["d_us"] != "%.4f" % g["d_us"] and "%.4f" % o["d_u"] != "%.4f" % g["d_u"], (o["d_us"], g["d_us"])   # not vacuous
    import re
    vm = re.search(r"\nAK2: (HELD|REVERSED|UNDETERMINED)", out).group(1)
    wm = "HELD" if (o["ci2"][0] > 0 and o["d_us"] > o["spread_us"]) else "REVERSED" if (o["ci2"][1] < 0 and o["d_us"] < -o["spread_us"]) else "UNDETERMINED"
    assert vm == wm, (vm, wm)                                                # the verdict is the mirrored one's
    # C-M1 (READY_union_af_mirror): F-AK reads the MIRRORED spread_AUs. The outcome's F-AK line prints it, and on the run's own
    # R with AK2's upper bound placed BETWEEN the registered and the mirrored spread the word follows the mirrored one.
    assert abs(o["spread_us"] - g["spread_us"]) > 1e-4, (o["spread_us"], g["spread_us"])
    fl_ = [ln for ln in out.splitlines() if ln.startswith("F-AK ")][0]
    assert ("the measured spread_AUs %.4f" % o["spread_us"]) in fl_, fl_
    with _patched(fx):
        Rm = ak_compute(fx.bundle, sum(fx.ksrc.values()), fx.ksrc, FX_SOURCES, ladder=False, single=("BBH",))
        assert "%.4f" % Rm["spread_aus"] == "%.4f" % o["spread_us"] and "%.4f" % Rm["reg"]["spread_aus"] == "%.4f" % g["spread_us"]
        lo_s, hi_s = sorted((Rm["spread_aus"], Rm["reg"]["spread_aus"]))
        Rm["AK2"] = dict(Rm["AK2"], hi=(lo_s + hi_s) / 2, lo=-1.0)
        Lm, Wm = ak_lines(Rm)
    want_fak = "FIRES" if Rm["AK2"]["hi"] <= Rm["spread_aus"] else "NOT FIRED"
    assert Wm["F-AK"] == want_fak, (Wm["F-AK"], want_fak, Rm["AK2"]["hi"], Rm["spread_aus"], Rm["reg"]["spread_aus"])
    _need(out, "Like with like holds IN k", "IS MIRRORED in AK1 / AK2 only (C-S1", "No wider like-with-like claim (C-S2)")
    assert "(the source centroid), like with like;" not in out
    af, kcs = _u_values(fx, tmp, out)
    bbh = [it["id"] for it in fx.spec["items"] if "mc6" in it["cvs"] and it["src"] == "BBH" and it["side"] in ("TRAIN", "EVAL")]
    assert bbh and all(af[i] == "BBH:n00000001" for i in bbh), sorted({af[i] for i in bbh})
    assert not any(v == "BBH:n00000001" for i, v in af.items() if fx.strata[i][0] != "BBH" and i != fx.mc)
    for s_, kc in zip(SEEDS, kcs):
        assert {kc[i] for i in bbh} == {"K%d:BBH:000" % s_}, (s_, {kc[i] for i in bbh})
    # the graft's CSVs: no BBH row; the merged CSVs: one row per BBH side item (EVAL + GATE held-out, TRAIN), named by majority
    import csv
    g = list(csv.DictReader(open(os.path.join(tmp, *fx.val.split("/"), RP.QUERIES), encoding="utf-8")))
    m = list(csv.DictReader(open(os.path.join(tmp, "res", "inputs", "validation_merged", RP.QUERIES), encoding="utf-8")))
    t = list(csv.DictReader(open(os.path.join(tmp, "res", "inputs", "validation_merged", RP.TRAIN), encoding="utf-8")))
    assert not any(src_of(r["true_key"]) == "BBH" for r in g)
    held_b = [it["id"] for it in fx.spec["items"] if "mc6" in it["cvs"] and it["src"] == "BBH" and it["side"] in ("EVAL", "GATE")]
    tr_b = [it for it in fx.spec["items"] if "mc6" in it["cvs"] and it["src"] == "BBH" and it["side"] == "TRAIN"]
    cnt = Counter("%s/%s" % (it["src"], it["dom"]) for it in tr_b)
    maj = min(k for k, v in cnt.items() if v == max(cnt.values()))
    mb = [r for r in m if r["rule"] == "one-cell"]
    assert sorted(r["item_id"] for r in mb) == sorted(held_b) and all(r["leaf_dominant"] == maj and r["leaf_id"] == "BBH:n00000001" for r in mb)
    assert sorted(r["item_id"] for r in t if r["rule"] == "one-cell") == sorted(it["id"] for it in tr_b)
    assert all(r["top1"] == str(int(r["true_key"] == maj)) for r in mb)
    # merged_validation on a hand case with UNEQUAL TRAIN counts: the cell is named by the majority (y: 2 of 3), not the minority
    d0 = os.path.join(tmp, "mv")
    os.makedirs(d0)
    for nm in (RP.QUERIES, RP.TRAIN):
        _write_csv(os.path.join(d0, nm), GB.Q_HEAD, [])
    _write_csv(os.path.join(d0, RP.LEAVES), ["leaf_id", "leaf_label", "leaf_depth", "profile_size", "leaf_dominant", "leaf_purity"], [])
    side_ = {"a": ("c1", "TRAIN"), "b": ("c2", "TRAIN"), "c": ("c3", "TRAIN"), "d": ("c4", "EVAL"), "e": ("c5", "GATE")}
    strata_ = {"a": ("Z", "x"), "b": ("Z", "y"), "c": ("Z", "y"), "d": ("Z", "x"), "e": ("Z", "y")}
    with _patched(fx):
        inf = merged_validation(d0, os.path.join(tmp, "mv_out"), {"Z": dict(cell="Z:n1")}, side_, strata_)
    assert inf == {"Z": (2, 3, "Z/y")}, inf
    q = list(csv.DictReader(open(os.path.join(tmp, "mv_out", RP.QUERIES), encoding="utf-8")))
    lv = list(csv.DictReader(open(os.path.join(tmp, "mv_out", RP.LEAVES), encoding="utf-8")))
    assert [(r["item_id"], r["leaf_dominant"], r["top1"]) for r in q] == [("d", "Z/y", "0"), ("e", "Z/y", "1")], q
    assert [(r["leaf_id"], r["profile_size"], r["leaf_dominant"], r["leaf_purity"]) for r in lv] == [("Z:n1", "3", "Z/y", "0.6667")], lv


def st_single_refusals(tmp_factory):
    """Every S1-S6 defect, the declaration checks, a graft row of the one-cell source and the ABSENT evidence REFUSE (through
    --build-inputs, before any input is written)."""
    def case(expect, **kw):
        fx = _fixture(tmp_factory(), single="BBH")
        edit = kw.pop("edit", None)
        if kw:
            _fx_single_evidence(fx.tmp, fx.afu, "bbh", "BBH", **kw)
        if edit:
            edit(fx)
        lines, err = _capture(build_inputs, fx)
        assert err and expect in err, (expect, err)
        assert not os.path.exists(os.path.join(fx.tmp, "res", "inputs")), "an input was written before the refusal"
    case("S1 run_manifest anchor_free False", anchor_free=False)
    case("S1 run_manifest anchor_free True, config_sha256_lf " + "0" * 64, toml_sha="0" * 64)
    case("S2 the console log LACKS the single-leaf refusal", log_line=None)
    case("and names a saved snapshot", snapshot=True)
    case("S3 proposals.csv has 3 rows, 3 ACCEPTED / REJECTED", decision="REJECTED")
    case("S4 rows at 2 (type, site, label, n) combinations", site2=True)
    case("S4 the console's refusal names siteId n00000009", console_site="n00000009")
    case("S5 row NO_PROPOSAL", bar="0.03000")                    # sep 0.02111 < 0.03: only the registered-bar check refuses
    case("S5 row NO_PROPOSAL", rows=(("1", "0.02600", "2"),))
    case("declares best_root_sep 0.0199", edit=lambda fx: _fx_write_decl(fx.tmp, fx.afu, [("bbh", "BBH", 0.0199, 450)]))
    case("member 'gpqa' / source 'BBH' is not a registered member", edit=lambda fx: _fx_write_decl(fx.tmp, fx.afu, [("gpqa", "BBH", 0.02111, 450)]))
    case("every member is declared one-cell", edit=lambda fx: _fx_write_decl(fx.tmp, fx.afu, [(m, so, 0.02111, 450) for m, so in FX_MEMBERS]))

    def graft_row(fx):
        pth = os.path.join(fx.tmp, *fx.val.split("/"), RP.QUERIES)
        it = [x for x in fx.spec["items"] if "mc6" in x["cvs"] and x["src"] == "BBH" and x["side"] == "EVAL"][0]
        with open(pth, "a", encoding="utf-8") as f:
            f.write("BBH/b0,BBH,flatLeaf,MMLU_PRO:L0,,2,,1.0,,,,,,%s\n" % it["id"])
    case("carries a row of a one-cell source", edit=graft_row)
    case("AF-U build outputs ABSENT (1 of 12)", edit=lambda fx: os.remove(os.path.join(fx.tmp, "res", "AF-U", "bbh", "build.log")))
    case("AF-U build outputs ABSENT (1 of 12)", edit=lambda fx: os.remove(os.path.join(fx.tmp, "res", "AF-U", "math", "seed_42", "dag_snapshots.jsonl")))
    # a UTF-16 console log (Windows PowerShell 5.1 Tee-Object) is read: no refusal from the evidence
    fx = _fixture(tmp_factory(), single="BBH")
    cp = os.path.join(fx.tmp, "res", "AF-U", "bbh", "build.log")
    txt = open(cp, encoding="utf-8").read()
    with open(cp, "wb") as f:
        f.write(txt.encode("utf-16"))
    with _patched(fx):
        ev = single_evidence("bbh", "BBH")
    assert "%.5f" % ev["best_sep"] == "0.02111" and ev["root"] == "n00000001" and ev["n_site"] == 450 and ev["rows"] == 3


CASES = (("branches", "every U1 / U2 / U3 (Holm) / F-U1 / F-TAX / AK1 / AK2 / F-AK branch and prediction line by value", "plain"),
         ("branch_cover", "the branch registry: every print branch hit", "plain"),
         ("builders", "R1 AF cells (modal leaf_id, tie, unrouted, no-row, multi-class) and R2-R4 K cells against an oracle; write-once", "tmp"),
         ("ak_e2e", "AK1 / AK2 / F-AK on the fixture bundle against an independent oracle (P, D, spread, interval, words)", "tmp"),
         ("run_e2e", "--run end to end: outcome values against independent naive policies; verdict words; write-once", "tmp"),
         ("identity_tree", "identity tree: G_AF == C1, M_AF == 0 (U3b EQUIVALENT), G_K == TRUE source, spread 0; R4 refusal; lin == contrast", "tmp"),
         ("refusals", "declared / AK identity, denominator, R3, pins, D-8, pool check, leaves CSV vs snapshots", "factory"),
         ("dry_run", "--dry-run: POOL first, denominators, AK identity, AF-U ABSENT refusal; inputs absent; the vdc dry-run, no statistic", "factory"),
         ("desc", "R9: D_fd computed with a descent graft (hand value), NOT COMPUTED without", "tmp"),
         ("vdc_inert", "v2_declared_cells hooks absent == blob c5b90278 (G14 outcome and policy on its fixture)", "tmp"),
         ("single_e2e", "ONE-CELL member (BBH): one cell, k = 1, AK k total, values vs oracles, the disclosure twice, merged rows", "tmp"),
         ("single_refusals", "ONE-CELL: S1-S6 defects, declaration checks, a graft row of the source, ABSENT evidence; UTF-16 console read", "factory"))
_FN = {"branches": st_branches, "branch_cover": st_branch_cover, "builders": st_builders, "ak_e2e": st_ak_e2e, "run_e2e": st_run_e2e,
       "identity_tree": st_identity_tree, "refusals": st_refusals, "dry_run": st_dry_run, "desc": st_desc, "vdc_inert": st_vdc_inert,
       "single_e2e": st_single_e2e, "single_refusals": st_single_refusals}


def selftest(only=None, quiet=False):
    import tempfile
    import shutil
    made, fails, ran = [], [], 0

    def factory():
        d = tempfile.mkdtemp(prefix="rp13_")
        made.append(d)
        return d
    try:
        for name, desc, kind in CASES:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    fn = _FN[name]
                    fn() if kind == "plain" else fn(factory()) if kind == "tmp" else fn(factory)
                if not quiet:
                    print("  ok   %-13s %s" % (name, desc), flush=True)
            except BaseException as e:            # noqa: B902
                fails.append(name)
                if not quiet:
                    import traceback
                    print("  FAIL %-13s %s: %s: %s" % (name, desc, type(e).__name__, str(e)[:400]), flush=True)
                    traceback.print_exc()
    finally:
        for d in made:
            shutil.rmtree(d, ignore_errors=True)
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants(only=None):
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    vsrc = open(V.__file__, encoding="utf-8").read()
    cut = src.index(chr(10) + "MUTANTS = (")
    head, tail = src[:cut], src[cut:]
    print("MUTANTS (%d): one temporary edit each (in memory; X* edit this file, V* edit v2_declared_cells.py re-executed in the"
          " imported module after the pin check); KILLED iff the targeted selftest subset fails" % len(MUTANTS))
    killed, base, control_ok, surv = 0, {}, True, []
    for m_ in MUTANTS:
        name, edits, tests = m_[:3]
        if only and not any(name.startswith(o) for o in only):
            continue
        target = m_[3] if len(m_) > 3 else "self"
        mut = head if target == "self" else vsrc
        for old, new in edits:
            if mut.count(old) != 1:
                raise SystemExit("%s mutant %r: target occurs %d times (must be exactly 1): %r" % (TAG, name, mut.count(old), old[:80]))
            mut = mut.replace(old, new)
        key = tuple(sorted(tests))
        if key not in base:
            base[key] = _exec_selftest(src, tests)
        res = _exec_selftest(mut + tail, tests) if target == "self" else _exec_selftest(src, tests, vdc_src=mut, vdc_orig=vsrc)
        k = res is not True and base[key] is True
        if name.startswith("X00"):
            control_ok = res is True and base[key] is True
            print("  %-58s tests %-24s original %-4s control %s" % (name, ",".join(tests), "PASS" if base[key] is True else "FAIL",
                                                                   "SURVIVED (as it must)" if control_ok else "KILLED (harness broken)"), flush=True)
            continue
        killed += int(k)
        if not k:
            surv.append(name)
        print("  %-58s tests %-24s original %-4s mutant %-8s %s" % (name, ",".join(tests), "PASS" if base[key] is True else "FAIL",
                                                                   "KILLED" if k else "SURVIVED", "" if res is True else res[:90]), flush=True)
    n_real = sum(1 for m in MUTANTS if not m[0].startswith("X00") and (not only or any(m[0].startswith(o) for o in only)))
    print("MUTANTS: %d of %d KILLED; control %s; survivors %s" % (killed, n_real, "survived" if control_ok else "KILLED", surv or "none"))
    return 0 if killed == n_real and control_ok else 1


def _exec_selftest(src, tests, vdc_src=None, vdc_orig=None):
    ns = {"__name__": "union_af_route_mutant", "__file__": os.path.abspath(__file__)}
    try:
        exec(compile(src, "<mutant>", "exec"), ns)
        if vdc_src is not None:
            exec(compile(vdc_src, V.__file__, "exec"), ns["V"].__dict__)
        ns["selftest"](only=set(tests), quiet=True)
        return True
    except BaseException as e:                   # noqa: B902
        return "%s: %s" % (type(e).__name__, str(e)[:160])
    finally:
        if vdc_src is not None:
            exec(compile(vdc_orig, V.__file__, "exec"), V.__dict__)


NL = chr(10)
MUTANTS = (
    ("X00 control (no-op edit)", [("    return band[0] <= x <= band[1]", "    return band[0] <= x <= band[1]")], ["branches", "run_e2e"]),
    # spread / mean over seeds / first seed only / arm indices (min<->max; first site only; wrong population)
    ("X01 spread_K min<->max", [('st["spread_K"] = max(pts) - min(pts)', 'st["spread_K"] = min(pts) - max(pts)')], ["run_e2e"]),
    ("X02 G_K = seed 0 only (not the mean over s)", [("    wk = {k: 1.0 / nk for k in kidx}", "    wk = {kidx[0]: 1.0}")], ["run_e2e"]),
    ("X03 D_K against seed 0 only", [("    wd = {k: -1.0 / nk for k in kidx}", "    wd = {kidx[0]: -1.0}")], ["run_e2e"]),
    ("X04 K arm index off by one", [("kidx = [V.TREE + 1 + i for i in range(len(names))]", "kidx = [V.TREE + i for i in range(len(names))]")], ["run_e2e"]),
    ("X05 G_AF read from the TRUE source arm", [('G=V.contrast(bt, D, "ALL", V.TREE, V.BS), M=', 'G=V.contrast(bt, D, "ALL", V.TSRC, V.BS), M=')], ["run_e2e"]),
    ("X06 M_AF against TRUE source, not (source, domain)", [('M=V.contrast(bt, D, "ALL", V.TREE, V.TDOM)', 'M=V.contrast(bt, D, "ALL", V.TREE, V.TSRC)')],
     ["run_e2e"]),
    # verdict boundaries (U1, U2)
    ("X07 U1 HELD admits lo = 0", [('    if g["lo"] > 0:' + NL + '        return "HELD"', '    if g["lo"] >= 0:' + NL + '        return "HELD"')], ["branches"]),
    ("X08 U1 FAILED needs hi < 0", [('    if g["hi"] <= 0:' + NL + '        return "FAILED"', '    if g["hi"] < 0:' + NL + '        return "FAILED"')], ["branches"]),
    ("X09 U2 without the spread clause", [('    if dk["lo"] > 0 and dk["point"] > spread:', '    if dk["lo"] > 0:')], ["branches"]),
    ("X10 U2 point clause >= spread", [('    if dk["lo"] > 0 and dk["point"] > spread:', '    if dk["lo"] > 0 and dk["point"] >= spread:')], ["branches"]),
    ("X11 U2 reverse without its spread clause", [('    if dk["hi"] < 0 and dk["point"] < -spread:', '    if dk["hi"] < 0:')], ["branches"]),
    # U3 (Holm order and stop, TOST p, z, contrast, strict inside)
    ("X12 Holm in fixed order U3a first", [('    order = sorted(items, key=lambda t: (tost_p(t[1], delta), 0 if t[0] == "U3a" else 1))', "    order = items")],
     ["branches"]),
    ("X13 Holm does not stop after a failed first step", [("    e2 = e1 and inside(s2, 1.645, delta)", "    e2 = inside(s2, 1.645, delta)")], ["branches"]),
    ("X14 first Holm step at 90%", [("    e1 = inside(s1, 1.96, delta)", "    e1 = inside(s1, 1.645, delta)")], ["branches"]),
    ("X15 second Holm step at 95%", [("    e2 = e1 and inside(s2, 1.645, delta)", "    e2 = e1 and inside(s2, 1.96, delta)")], ["branches"]),
    ("X16 TOST p one-sided (registered form changed)", [("    return max(1.0 - _phi((d + delta) / se), _phi((d - delta) / se))",
                                                          "    return 1.0 - _phi((d + delta) / se)")], ["branches"]),
    ("X17 U3a on G_AF instead of D_K", [('    u3, order, _e1 = holm_u3(dk, m, c["delta"])', '    u3, order, _e1 = holm_u3(g, m, c["delta"])')], ["branches"]),
    ("X18 inside not strict", [('    return bool(st["point"] - z * st["se2"] > -delta and st["point"] + z * st["se2"] < delta)',
                                '    return bool(st["point"] - z * st["se2"] >= -delta and st["point"] + z * st["se2"] <= delta)')], ["branches"]),
    # F-U1 / F-TAX / skip-path lines / predictions
    ("X19 F-U1 fires on UNDETERMINED", [('    if v1 == "FAILED":' + NL + '        hit("FU1.FIRES")', '    if v1 != "HELD":' + NL + '        hit("FU1.FIRES")')],
     ["branches"]),
    ("X20 by-support bar = spread_K only", [('    bar = max(dk["mde"], spread)' + NL + '    if v2 == "FIRES":', '    bar = spread' + NL + '    if v2 == "FIRES":')],
     ["branches"]),
    ("X21 by-support clause omitted (skip path)", [('" (lever leg not fired, by support: |D_K| %s <= bar %s)" % (pp(abs(dk["point"])).lstrip("+"), pp(bar).lstrip("+"))',
                                                     '""')], ["branches"]),
    ("X22 joined record omitted", [('        if words["U3a"] == "EQUIVALENT":' + NL + '            hit("FTAX.JOINED")',
                                    '        if False:' + NL + '            hit("FTAX.JOINED")')], ["branches"]),
    ("X23 prediction band exclusive at the ends", [("    return band[0] <= x <= band[1]", "    return band[0] < x < band[1]")], ["branches"]),
    # AK (F-AK, spreads, populations, seed of record, side, k)
    ("X24 F-AK decided by AK1", [('    fires = bool(st2["hi"] <= R["spread_aus"])', '    fires = bool(st1["hi"] <= R["spread_au"])')], ["branches"]),
    ("X25 F-AK strict <", [('    fires = bool(st2["hi"] <= R["spread_aus"])', '    fires = bool(st2["hi"] < R["spread_aus"])')], ["branches"]),
    ("X26 F-AK NOT FIRED line omitted (skip path)", [('        hit("FAK.NOT_FIRED")' + NL + '        say(', '        hit("FAK.NOT_FIRED")' + NL + '        (lambda *a: None)(')],
     ["branches"]),
    ("X27 UNDETERMINED without its 'not shown' words", [('            say("%s: %s; reads \\"not shown\\", never parity and never \\"no difference\\"" % (key, why))',
                                                         '            say("%s: %s" % (key, why))')], ["branches"]),
    ("X28 per-source D crashes on an empty source (zero items)", [('("%+.4f" % a["d"]) if a else "n/a (0 items)"', '("%+.4f" % a["d"])')], ["branches"]),
    ("X29 spread_AUs from the within-source population", [('    R["spread_aus"] = GB.spread_of(R["p_us"].values())', '    R["spread_aus"] = GB.spread_of(R["p_us_in"].values())')],
     ["ak_e2e"]),
    ("X30 AK2 primary with a source oracle", [('    R["AK2"] = GB.stat(fl - us_ok[0], comp)', '    R["AK2"] = GB.stat(fl - us_in[0], comp)')], ["ak_e2e"]),
    ("X31 AK1 comparator of record seed 1", [('    R["AK1"] = GB.stat(fl - ug_ok[0], comp)', '    R["AK1"] = GB.stat(fl - ug_ok[1], comp)')], ["ak_e2e"]),
    ("X32 AK1 named on EVAL (wrong side)", [('        lab = GB.name_clusters(fit["labels"], L, yt, classes)',
                                            '        lab = GB.name_clusters(np.argmax(Xe @ fit["centers"].T, axis=1), L, ye, classes)')], ["ak_e2e"]),
    ("X33 AK k = leaves with a profile, not all snapshot leaves (--run)", [('    R = ak_compute(b, sum(ksrc.values()), ksrc, c["sources"], ladder=True, single=tuple(single))',
                                                                            '    R = ak_compute(b, len(b["leaf_major"]), ksrc, c["sources"], ladder=True, single=tuple(single))')], ["run_e2e"]),
    # C-S1 / C-S2 (programme L23098 / L23664 brackets, d3653625)
    ("O15 F-AK reads the registered spread under mirroring (READY_union_af_mirror C-M1)",
     [('    fires = bool(st2["hi"] <= R["spread_aus"])', '    fires = bool(st2["hi"] <= (R["reg"]["spread_aus"] if R.get("mirrored") else R["spread_aus"]))')],
     ["single_e2e"]),
    ("X79 nearest-of-all decides (C-S1 not applied)", [("    if single:                                                   # C-S1: the registered rule kept beside",
                                                         "    if False:                                                   # C-S1: the registered rule kept beside")], ["single_e2e"]),
    ("X80 AK2 mirror: the one-cell centroid not excluded from other items' search", [("    S = np.where(np.isin(csrc, list(single))[None, :], -np.inf, Xe @ C.T)",
                                                                                       "    S = Xe @ C.T")], ["single_e2e"]),
    ("X81 AK1 mirror: fitted on every TRAIN item at k = L", [("    fit, _t = GB.ukm_fit(Xt[~one], k_rest, s)" + NL + "    lab = GB.name_clusters(fit[\"labels\"], k_rest, yt[~one], classes)",
                                                              "    fit, _t = GB.ukm_fit(Xt, L, s)" + NL + "    lab = GB.name_clusters(fit[\"labels\"], L, yt, classes)")], ["single_e2e"]),
    ("X82 AK2 mirror: the one-cell source's items not filed by source", [("    for so in sorted(single):" + NL + "        p2[esrc == so] = names[csrc == so][0]",
                                                                          "    for so in ():" + NL + "        p2[esrc == so] = names[csrc == so][0]")], ["single_e2e"]),
    ("X83 C-S2: the old unqualified like-with-like disclosure", [('" another source can be filed to it and none of its items to another member\'s leaf. Like with like holds IN k: K_s"',
                                                                 '" another source can be filed to it and none of its items to another member\'s leaf; (the source centroid), like with like; K_s"')],
     ["single_e2e"]),
    ("X84 the registered value not printed beside", [('        say("  DESCRIPTIVE (the registered nearest-of-ALL-centroids AK2, C-S1): P(US_s) %s; spread_AUs %.4f; D_AUs %s" % (',
                                                      '        (lambda *a: None)("  DESCRIPTIVE (the registered nearest-of-ALL-centroids AK2, C-S1): P(US_s) %s; spread_AUs %.4f; D_AUs %s" % (')],
     ["single_e2e"]),
    # builders (R1-R4)
    ("X34 K fitted on EVAL (wrong split side)", [('        kc, ki = k_cells(s, Xt, tsrc, titems, ksrc, c["sources"], vec, srcs, cells)',
                                                  '        kc, ki = k_cells(s, _Xe, np.array([src_of(classes[i]) for i in _ye]), titems, ksrc, c["sources"], vec, srcs, cells)')],
     ["builders"]),
    ("X35 K filing ignores the source", [("    allowed = np.isin(csrc, list(srcset))", "    allowed = np.ones(len(csrc), dtype=bool)")], ["builders"]),
    ("X36 multi-class item filed in its first source only", [("    return {it: sorted(s) for it, s in by.items()}", "    return {it: sorted(s)[:1] for it, s in by.items()}")],
     ["builders"]),
    ("X37 AF cell = the leaf's declared-class name (label leak)", [("        cells[it] = lh[it][0]", "        cells[it] = held[it][0] if it in held else lh[it][0]")],
     ["builders"]),
    ("X38 AF cell = the first row (no modal rule, no tie rule)", [("    lh, lt = GB.item_leaves(rows_h), GB.item_leaves(rows_t)",
                                                                   '    lh, lt = {r["item_id"]: (r["leaf_id"] or UNROUTED, 0) for r in reversed(rows_h)}, GB.item_leaves(rows_t)')],
     ["builders"]),
    ("X39 no-row fill removed", [("            cells[it] = NO_ROW" + NL + "            filled[s] += 1", "            filled[s] += 1")], ["builders"]),
    ("X40 write_x overwrites (mode w)", [('    with open(path, "x", encoding="utf-8", newline="\\n") as f:', '    with open(path, "w", encoding="utf-8", newline="\\n") as f:')],
     ["builders"]),
    ("X41 build-inputs existence refusal removed", [("    if ex:" + NL + '        refuse("input file(s) exist', "    if False:" + NL + '        refuse("input file(s) exist')],
     ["builders"]),
    # guards and refusals
    ("X42 declared identity check removed", [("    if got != ident:" + NL + '        raise SystemExit("[RP13-IDENTITY]', "    if False:" + NL + '        raise SystemExit("[RP13-IDENTITY]')],
     ["refusals"]),
    ("X43 AK identity check removed", [("    if bad:" + NL + '        refuse("[RP13-AK-IDENTITY]', "    if False:" + NL + '        refuse("[RP13-AK-IDENTITY]')], ["refusals"]),
    ("X44 denominator check removed", [('    if (D.n_eval, D.eval_units["n_units"]) != (c["n_route"], c["comp_route"]):', "    if False:")], ["refusals"]),
    ("X45 R3 check removed", [("    if bad:" + NL + '        hit("REFUSE.R3")', "    if False:" + NL + '        hit("REFUSE.R3")')], ["refusals"]),
    ("X58 (O1) R10 compares best_single only", [("    bad = [k for k in R10_KEYS if nn(lu.get(k)) != nn(pol.get(k))]",
                                                  '    bad = [k for k in ("best_single",) if nn(lu.get(k)) != nn(pol.get(k))]')], ["refusals"]),
    ("X59 (O4) identity compares the point only", [("    if got != ident:" + NL + '        raise SystemExit("[RP13-IDENTITY]',
                                                     "    if got[0] != ident[0]:" + NL + '        raise SystemExit("[RP13-IDENTITY]')], ["refusals"]),
    ("X60 D-4 disclosure omitted", [('    hit("U2.D4_DISCLOSED")' + NL + '    say(', '    hit("U2.D4_DISCLOSED")' + NL + '    (lambda *a: None)(')], ["branches"]),
    ("X61 D-5 ignore-path refusal removed", [('    if not _IGNORED[0](P(c["policy"])):', "    if False:")], ["refusals"]),
    ("X62 (C-4) R10 not wired before EVAL", [("    cfg.pre_eval = r10_check" + NL + "    return cfg", "    return cfg")], ["run_e2e"]),
    ("X46 pin re-check removed", [("    if bad:" + NL + '        hit("REFUSE.PIN")', "    if False:" + NL + '        hit("REFUSE.PIN")')], ["refusals"]),
    ("X47 D-8 one-commit check removed", [("    if len(set(got.values())) != 1:", "    if False:")], ["refusals"]),
    ("X48 pool check ignored in --run", [("    if rc != 0:" + NL + '        refuse("the B0-2 pool check failed: %s" % msg)' + NL + "    denominators(say)",
                                          "    if False:" + NL + '        refuse("the B0-2 pool check failed: %s" % msg)' + NL + "    denominators(say)")], ["refusals"]),
    ("X49 leaves CSV vs snapshot check removed", [("    if csv_ids != snap_ids:", "    if False:")], ["refusals"]),
    ("X50 AF-U ABSENT refusal removed (the dry-run goes on)", [("    if miss:" + NL + '        hit("REFUSE.AFU_ABSENT")', "    if False:" + NL + '        hit("REFUSE.AFU_ABSENT")')],
     ["dry_run"]),
    ("X51 inputs-absent refusal removed", [("    if not os.path.isfile(mp):" + NL + '        hit("REFUSE.INPUTS_ABSENT")', "    if False:" + NL + '        hit("REFUSE.INPUTS_ABSENT")')],
     ["dry_run"]),
    ("X52 R4 re-derivation check removed", [("        if diff:" + NL + '            hit("REFUSE.K_REDERIVE")', "        if False:" + NL + '            hit("REFUSE.K_REDERIVE")')],
     ["identity_tree"]),
    ("X53 run write-once pre-check removed", [("        if os.path.exists(P(p)):" + NL + '            hit("REFUSE.WRITE_ONCE")', "        if False:" + NL + '            hit("REFUSE.WRITE_ONCE")')],
     ["run_e2e"]),
    ("X54 pre-read lines not copied into the outcome", [('    for ln in cfg.rp13.get("pre_lines", ()):', "    for ln in ():")], ["run_e2e"]),
    ("X55 AK block not written into the outcome", [('    for ln in cfg.rp13["ak_lines"]:', "    for ln in []:")], ["run_e2e"]),
    ("X56 D_fd skip line omitted", [('        return "NOT COMPUTED (no descent graft: the AF-U TOMLs at a994a722 carry graft_flatleaf only; R9)"', '        return ""')],
     ["desc"]),
    ("X57 D_fd sign flipped", [('    st = GB.stat(np.asarray(b["eval_fl"], dtype=np.int64) - dok, np.asarray(b["eval_comp"]))',
                                '    st = GB.stat(dok - np.asarray(b["eval_fl"], dtype=np.int64), np.asarray(b["eval_comp"]))')], ["desc"]),
    # the v2_declared_cells hooks (V*: the mutated source re-executed in the imported module, restored after)
    ("V01 vdc: the extra arms' rows not appended", [('    for nm in getattr(D, "xnames", ()):                          # RP13: the extra arms, indices 6.. in sorted name order',
                                                     "    for nm in ():")], ["run_e2e"], "vdc"),
    ("V02 vdc: the extra arms grouped by the tree cells", [("            D.xkeys[nm], g_ = _index([xtrees[nm][i] for i in items])",
                                                            "            D.xkeys[nm], g_ = _index([tree[i] for i in items])")], ["run_e2e"], "vdc"),
    ("V03 vdc: [G14-NOROW] not applied to the extra arms", [("            if norow_x:", "            if False:")], ["identity_tree"], "vdc"),
    ("V04 vdc: cfg.tail ignored (g14_tail used)", [('        return (getattr(cfg, "tail", None) or g14_tail)(cfg,', "        return (g14_tail)(cfg,")], ["run_e2e"], "vdc"),
    ("V05 vdc: the extra arms' policies not frozen", [('        pj["xtree_cell"] = {nm:', '        pj["xtree_cellX"] = {nm:')], ["run_e2e"], "vdc"),
    # ONE-CELL members (THE AUTHOR's decision 2026-10-03)
    ("X63 S2 console refusal not required", [("    if sm is None or SNAPSHOT_LINE in log or SNAPSHOT_LINE in con:", "    if False:")], ["single_refusals"]),
    ("X64 S3 a REJECTED / ACCEPTED row admitted", [('    if not rows or any(r["decision"] in ("ACCEPTED", "REJECTED") for r in rows):', "    if not rows:")],
     ["single_refusals"]),
    ("X65 S5 sep < bar not required", [(' or not float(m_.group(1)) < float(m_.group(2)):', ':')], ["single_refusals"]),
    ("X66 S5 bar not compared with the registered bar", [(' or abs(float(m_.group(2)) - c["bar"]) > 1e-9', '')], ["single_refusals"]),
    ("X67 S4 one root site not required", [('    if len(sites) != 1 or list(sites)[0][0] != "GROW" or list(sites)[0][2] != src:',
                                           '    if list(sites)[0][0] != "GROW" or list(sites)[0][2] != src:')], ["single_refusals"]),
    ("X68 S4 console siteId not cross-checked", [("    if sm.group(1) != root:", "    if False:")], ["single_refusals"]),
    ("X69 S1 TOML sha not checked", [('    if man.get("anchor_free") is not True or got is None or got != want:', '    if man.get("anchor_free") is not True:')],
     ["single_refusals"]),
    ("X70 declared best_root_sep not checked", [('        if "%.5f" % ev["best_sep"] != "%.5f" % float(e.get("best_root_sep", -1)) or ev["n_site"] != int(e.get("n_site", -1)):',
                                                  "        if False:")], ["single_refusals"]),
    ("X71 a graft row of a one-cell source admitted", [('                hit("REFUSE.SINGLE_IN_GRAFT")' + NL + '                refuse(',
                                                         '                hit("REFUSE.SINGLE_IN_GRAFT")' + NL + '                (lambda *a: None)(')], ["single_refusals"]),
    ("X72 a one-cell member counts its snapshot leaves (k != 1)", [('        ksrc[s], ids[s] = 1, {e["cell"]}', '        ksrc[s], ids[s] = 2, {e["cell"]}')],
     ["single_e2e"]),
    ("X73 one-cell held-out items not added", [('            want = ("TRAIN",) if nm == RP.TRAIN else ("EVAL", "GATE")', '            want = ("TRAIN",) if nm == RP.TRAIN else ("GATE",)')],
     ["single_e2e"]),
    ("X74 one-cell name = the minority class", [("            maj = min(k for k, v in cnt.items() if v == top)", "            maj = min(cnt, key=lambda k: (cnt[k], k))")],
     ["single_e2e"]),
    ("X75 one-cell disclosure omitted from the AK block", [('    for ln in single_lines(R.get("single", {})):', "    for ln in []:")], ["single_e2e"]),
    ("X76 one-cell evidence not required (snapshot asked instead)", [("        if src in single:" + NL + '            snaps += [("%s ONE-CELL proposals"',
                                                                       "        if False:" + NL + '            snaps += [("%s ONE-CELL proposals"')], ["single_refusals"]),
    ("X77 all-members-one-cell declaration admitted", [('    if len(out) >= len(c["members"]):' + NL + '        refuse("ONE-CELL declaration: every member',
                                                         '    if False:' + NL + '        refuse("ONE-CELL declaration: every member')], ["single_refusals"]),
    ("X78 UTF-16 console not decoded", [("    if raw[:2] in (bytes([255, 254]), bytes([254, 255])):", "    if False:")], ["single_refusals"]),
    ("V07 (O2) vdc: the extra arms' B3 re-fit check disabled", [("    if xtrees and {k: nn(v) for k, v in", "    if False and xtrees and {k: nn(v) for k, v in")],
     ["refusals"], "vdc"),
    ("V08 vdc: pre_eval hook not called", [("        cfg.pre_eval(cfg, pol, psha, say)", "        pass")], ["run_e2e"], "vdc"),
    ("V06 vdc: an empty xtree_cell key frozen when the arms are absent (inertness)", [
        ('    if getattr(D, "xnames", ()):                                 # RP13: the extra arms\' frozen TRAIN policies',
         '    pj["xtree_cell"] = {}' + NL + '    if getattr(D, "xnames", ()):')], ["vdc_inert"], "vdc"),)


if __name__ == "__main__":
    sys.exit(main())
