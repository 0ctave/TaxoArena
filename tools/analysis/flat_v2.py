"""FLAT on the v2 split (RP12 ARCH-V2-E-T, the FLAT readout): flat_mix_mmlu.py PARAMETERISED to B0's MMLU-Pro member on the
content-closed pool pv2_41dbd3dbcd399df0. ZERO calls: no judge, no LLM, no embedding call, no cap, no temperature.

REGISTRATION OF RECORD: docs/judge_v2_program.md, "## Registered 2026-09-29 (before any code or call) — ARCH-V2-E-T" (L22028-L22060
at 0a0361b): "FLAT (partition, MMLU-Pro member; FLAT-MIX-MMLU's criteria unchanged, re-pointed to T2 = B0's MMLU-Pro member,
k = its leaf count): C1 PURITY HELD iff M1(T2) - M1(V0) > spread_V(M1) (point) AND the paired 95% CI excludes 0 on the positive
side (interval), one conjunctive clause, FAILED otherwise, no UNDETERMINED; C2 the same on M2 (F6 x1000); L1 loss flag FIRES iff
for M1 or M2 the difference < -spread_V AND the CI excludes 0 on the negative side. Identity precondition: the v2
parameterisation reproduces af_clean_s42's M1 0.727 [0.712, 0.741] and M2 +12.785 before T2 is read." Support: FLAT M1 on
MMLU-Pro EVAL 3,492 items in 3,400 components (the count printed by the dry-run and reconciled at READY; a difference > 5% is
re-stated by bracket before any read), DEFF 1.03 DECLARED, n_eff 3,390, SE 0.00768, MDE80 0.0215, effective bar
max(MDE, spread_V), spread_V(M1) transported 0.0305; M2 SE 0.300e-3 transported, MDE80 0.84e-3, spread_V(M2) 0.822e-3.
P7: M1(T2) - M1(V0) = -0.015 [-0.040, +0.010]; M2 difference = -0.5e-3 [-1.8, +0.8]e-3; C1 FAILED 0.85; C2 FAILED 0.85; L1
fires 0.30. F3 fires iff FLAT L1 fires. L1 is DESCRIPTIVE-ONLY at the prediction; a non-fire is never read as parity.

THE INSTRUMENT (imported, never re-implemented): flat_mix_mmlu.py (blob-pinned below; it pin-verifies anchor_free_readout.py,
free_tests_f4_f7.py and embedder_guard.py on import and installs its read-only connect guard): fit_set, fit_matrix, load_T,
fit_partition (T2 by flatLeaf, V0-V4 flat vMF EM, K0-K4 spherical k-means, at k = T2's leaf count), measures (M1-M4), the
whole-group bootstrap draw (twin_boot_indices), criterion, loss, spread_opt, kish_mbar, identity. anchor_free_readout.corpus
through an eval-id override (flat_generality's device). v2_engine_pool.py (blob-pinned) for the side export (S1) and the pool
id recompute (S2).

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  (R1) HELD-OUT = the JUDGEABLE EVAL ids of the engine pool file (positive ids), as FLAT-MIX-MMLU's held-out was a pool's
       judgeable ids; texts through eval_question_link (anchor_free_readout.corpus). The registration counts 3,492 EVAL ITEMS;
       the dry-run prints both (items and judgeable ids) for the READY's reconciliation.
  (R2) LABEL (train) SET of M1 = the distinct mmlu_pro texts whose item is TRAIN in the side export (anchor_free_readout.corpus'
       "every other text" restricted to TRAIN: GATE and the EVAL sentinels leave it). Every held-out text's item must be EVAL,
       every fit text's item TRAIN (refused otherwise).
  (R3) PAIRED INTERVALS of M1 and M4: CK-CLOSE components whole (the side export's component of each held-out item), B 2,000,
       seed 20260929, flat_mix_mmlu's percentile rule (the registration's "intervals are 95% percentile, CK-CLOSE-component
       bootstrap, B 2,000, unless named"; FLAT-MIX-MMLU drew stem_key twin groups, B 1,000). M2's interval stays F6's own
       free_tests_f4_f7.boot_mean_ci over the keyed questions (as FLAT-MIX-MMLU; the Support transports M2's SE from it).
  (R4) M2's keyed set = free_tests_f4_f7.keyed_questions() ("the keyed MMLU-Pro items of both sides", count printed).
  (R5) The identity precondition runs af_clean_s42 through THIS script's corpus / measure path (p2dca, 256-d, no side filter)
       and must print M1 0.727 [0.712, 0.741] and M2 +12.785; --analyze REFUSES before any T2 read otherwise.

PRECONDITIONS THAT REFUSE --run / --analyze WHILE UNSET (owed; set by a delta of this script after B0 is built and the engine
pool file is generated and committed): T2 (run dir, snapshot id, leaf count, root fit count: the census), ENGINE_POOL_SHA_LF
(sha256 of the committed engine pool file's LF rendering). --dry-run takes --tree-run / --tree-snapshot / --leaves / --fit-n
for the census and prints counts only.

  python tools/analysis/flat_v2.py --selftest
  python tools/analysis/flat_v2.py --dry-run [--tree-run D --tree-snapshot S --leaves K --fit-n N]
  python tools/analysis/flat_v2.py --identity-check
  python tools/analysis/flat_v2.py --run [--max-chunks N]      # one partition per chunk, write-once state
  python tools/analysis/flat_v2.py --analyze                   # outcome of record WRITE-ONCE (mode x)
  Set TAXOARENA_DATA_ROOT to the main checkout when running from a worktree. A POOL READER: never beside a construction.
Outputs: experiment_results/archv2/rp12/flat_v2/state/*.json, flat_v2_outcome.txt (write-once).

[DELTA 2026-09-30 rp12-et2, READY_rp12_et C-6 / RA6 / D-6; insertion only] reconcile / reconcile_line / reconcile_gate: the
dry-run prints held-out ids -> texts -> items -> components against the registered 3,492 items / 3,400 components (gap = the
larger relative gap; WITHIN iff <= 5%, endpoint inclusive); --analyze REFUSES a gap over 5% while RECONCILE_BRACKET (the
registrar's bracket, set by a reviewed delta) is None, and runs the gate after the identity gate and before any T2 read. The
Kish line names the Sum m^2 / Sum m bound (D-6). RA6: a GATE held-out text refuses (tested beside TRAIN). Mutants: H0 control
survived; H1 gap on items only, H2 exactly 5% read as over, H3 the gate never refuses, H4 --analyze without the gate, H5 (RA6)
GATE admitted to the held-out set, H6 items counted per text: 6 of 6 killed.
[DELTA 2026-09-30 rp12-et3, READY_rp12_et2 D-10; insertion only] ENGINE_POOL_SHA_LF is set to pv2_41dbd3dbcd399df0's committed
file (8f1ed122..., the held-out side, R1); check_t2_stamp REFUSES unless T2's stored stamp is pool pv2_1575de61bb20e977, engine
pool file 79d48f4b..., namespaces ["MMLU_PRO"], rule CK-CLOSE-v2, on the side export read now; --dry-run prints it when a T2
snapshot is given, --run and --analyze run it before any T2 read. T2 itself stays owed (after B0). Mutants: T0 control survived;
T1 --run skips the stamp, T2 the side-export check removed, T3 namespaces not pinned, T4 the held-out pin changed to pv2_1575's,
T5 a missing stamp accepted: 5 of 5 killed.
[DELTA 2026-09-30 rp12-et4, READY_rp12_et3 F-1; insertion only] T2 = B0's MMLU_PRO_LB member: its run dir is the committed
build config's outputDir + /seed_42 (value-checked); its snapshot id is read from the pointer file entry B0/mmlu_pro_lb
(t2_snapshot_from_pointer; owed while the pointer is); the dry-run prints the [D-10] T2 stamp line and the census (leaf count,
root fit ids) once B0 exists, and "B0 not built yet" before; leaves and fit_n stay owed until a reviewed delta pins the census
(--run / --analyze refuse). Mutants: K0 control survived; K1 another member's entry, K2 the pointer ignored, K3 the census
counting internal nodes, K4 B0p's run dir: 4 of 4 killed.
[DELTA 2026-10-01 rp12-flat-pin, READY_rp12_pair_mc F-2..F-4 (ccef91d); insertion only] the census is PINNED: T2 leaves = 74,
fit_n = 6993, T2_CENSUS_SNAPSHOT = 20261001_070346_Headless_Run_Auto_ge (the reviewer's census: 135 nodes, 74 leaves, 6,993 root
fit ids with 6,993 distinct texts). The snapshot still comes from the pointer entry (owed until it is committed: --run /
--analyze refuse "preconditions owed: snapshot"). check_census: the snapshot, leaf count and root fit ids read now must equal the
pin, else "F-3 STOP for the registrar" (REFUSED); the dry-run prints it after the census line (not for --tree-* overrides), and
--run / --analyze run it after the D-10 stamp and before any T2 read. require_preconditions takes the root (the selftest reads
an empty one, so a committed pointer never turns the selftest into a real run). F-4 (rule 7: never beside B0'/o1/o2) is the
operator's. Mutants (P0 control survived): P1 leaves pinned 73, P2 fit_n pinned 6992, P3 the census compares the leaves only,
P4 the snapshot not compared, P5 --run skips the census, P6 --analyze skips it, P7 the dry-run skips it: 7 of 7 killed.
[DELTA 2026-10-01 rp12-r2-lane; insertion only] --lane {r1,r2} (default r1: every constant above, unchanged). set_lane("r2"):
T2 = experiment_results/archv2/rp12_r2/B0/mmlu_pro_lb/seed_42 through experiment_configs/rp12_r2/objects_of_record.json, the
census OWED (leaves, fit_n, snapshot None: --run / --analyze refuse "preconditions owed", check_census refuses) until a reviewed
delta pins R2's; outputs under experiment_results/archv2/rp12_r2/flat_v2/. A --tree-run of the other lane refuses.
[DELTA 2026-10-01 flat-r2-pin, READY_rp12_r2_lane C-2 / D-1; insertion only; supersedes "OWED" above for lane r2] lane r2's
census is PINNED from the R2 B0 MMLU_PRO_LB member: snapshot 20261001_094311_Headless_Run_Auto_ge (the entry B0/mmlu_pro_lb of
experiment_configs/rp12_r2/objects_of_record.json), leaves 74, fit_n 6993. Measured read-only (zero calls) on the R2 build
worktree's snapshots.db (rp12-r2-run, mode=ro immutable=1, WAL 0 bytes, sha unchanged): 135 nodes, 74 leaves (t2_census),
6,993 root fit ids; main's embeddings_cache.db (WAL 0) holds 6,993 queries rows with 6,993 distinct texts for them; the run
dir's final dag line: 135 nodes, 74 leaves. The snapshot is still READ from the R2 pointer (T2 snapshot None); check_census
compares it with the pin. D-1: a main()-level selftest runs main(["--dry-run", "--lane", "r2"]) with dry_run stubbed and
asserts T2, the pointer, the census pin and OUTCOME under rp12_r2 (the reviewer's M8, set_lane removed from main(): killed).
DATA_ROOT note: main's snapshots.db does not hold the R2 snapshots; FLAT R2 reads them with TAXOARENA_DATA_ROOT at the R2 build
worktree (the operator's step, rule 7).
[DELTA 2026-10-01 flat-f3-fix, D-FLAT-1; insertion only] main() built `over` as a dict of four keys, always truthy, so the CLI
dry-run never reached check_census and never printed "[F-3] T2 census equals the pin" (operator log
experiment_results/archv2/rp12_r2/readouts/flat_dryrun2.txt). `over` now holds only the overrides given. f3_dry_run_cli (replacing
the source-order check) runs main(["--dry-run", "--lane", "r2"]) through the real dry_run with its data readers stubbed and asserts
the [F-3] line by value, right after the census line; with --leaves 74 the census prints and [F-3] does not. Mutant DF1 (the
always-truthy dict restored): killed.
SELFTEST MUTANTS (run 2026-09-30 by a harness, one temporary edit at a time, reverted; F0 control survived): F1 C1 without the
spread clause | F2 comparator V1 | F3 B 1,000 | F4 L1 on M1 only | F5 the label set keeps GATE | F6 the held-out EVAL check
removed | F7 the fit check removed | F8 the identity gate bypassed | F9 the preconditions check removed | F10 P7 band exclusive |
F11 the engine pool's side-export pin ignored | F12 spread over V0..V3 | F13 groups by question (not component) | F14 L1 read on
the gain side: 14 of 14 killed. NOT EXERCISED on real data (no DB was opened): --dry-run, --identity-check, --run, --analyze need
B0, the committed engine pool file and a pool-reader window; the identity check is the READY's.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import sys
import io
import json
import time
import hashlib
import argparse
import contextlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[FLAT-V2]"
REGISTRATION = "docs/judge_v2_program.md L22028-L22060 (ARCH-V2-E-T, registered at 0a0361b)"
PINS = {"flat_mix_mmlu.py": "555ae3ac31b2f27ea040e4bb6a9b20be0eeeecd2",
        "v2_engine_pool.py": "435ee57c93716f583ddfa831b105ff9f42f98dbf"}
POOL_V2 = "pv2_41dbd3dbcd399df0"
CORPUS = "mmlu-pro-v2"
REG_ITEMS, REG_COMPONENTS = 3492, 3400
DIM = 512
SEEDS = (0, 1, 2, 3, 4)
BOOT_B, BOOT_SEED = 2000, 20260929
SE_M1, DEFF_M1, NEFF_M1, MDE_M1, SPREAD_V_M1 = 0.00768, 1.03, 3390, 0.0215, 0.0305
SE_M2, MDE_M2, SPREAD_V_M2 = 0.300e-3, 0.84e-3, 0.822e-3
P7_M1 = (-0.040, 0.010)
P7_M2 = (-1.8e-3, 0.8e-3)
ENGINE_POOL_REL = os.path.join("experiment_configs", "engine_pool_%s.json" % POOL_V2)
# PRECONDITIONS (owed; None REFUSES --run / --analyze)
# READY_rp12_et3 F-1 (delta rp12-et4): T2 = B0's MMLU_PRO_LB member. Its run dir is fixed by the build config
# (experiment_configs/rp12/B0/mmlu_pro_lb.toml); its snapshot id is read from the pointer file entry written after B0
# (g10_compare.py --write-pointer); its leaf count and root fit count are the census the dry-run prints, pinned here by the next
# reviewed delta (None = owed: --run / --analyze refuse).
T2 = dict(run="experiment_results/archv2/rp12/B0/mmlu_pro_lb/seed_42", snapshot=None, leaves=74, fit_n=6993)
# READY_rp12_pair_mc F-2..F-4 (ccef91d; delta rp12-flat-pin): the census of record, measured by the reviewer on snapshot
# 20261001_070346_Headless_Run_Auto_ge (135 nodes, 74 leaves, 6,993 root fit ids with 6,993 distinct texts). The snapshot keeps
# coming from the pointer (F-1); a pointer snapshot or a census other than this one is a STOP for the registrar (check_census).
T2_CENSUS_SNAPSHOT = "20261001_070346_Headless_Run_Auto_ge"
T2_POINTER = (os.path.join("experiment_configs", "rp12", "objects_of_record.json"), "B0/mmlu_pro_lb")
# READY_rp12_et2 D-10 (delta rp12-et3): the held-out file is pv2_41dbd3dbcd399df0's committed engine pool file (the EVAL side of
# FLAT, R1), pinned by the sha256 of its LF rendering; T2 (B0's MMLU_PRO_LB member) is tied to the union member pool by its
# snapshot stamp (check_t2_stamp), refused otherwise.
ENGINE_POOL_SHA_LF = "8f1ed122bfb45e435c772cb3ee9fe763026f7d7e5b1c3bfa56757231dbce53b8"
T2_STAMP = dict(rule="CK-CLOSE-v2", poolId="pv2_1575de61bb20e977",
                enginePoolSha256Lf="79d48f4b36434a551d3e706618a6a5e0cad9b0174d8e711bfeeb27f601b0f5a6", namespacesLoaded=["MMLU_PRO"])
# READY_rp12_et C-6: a held-out/registered gap over 5% must be re-stated by a registrar bracket before any read; the bracket's
# programme line is set here by a reviewed delta (None = no bracket: --analyze REFUSES on a gap over 5%)
RECONCILE_BRACKET = None
RECONCILE_LIMIT = 0.05
OUT_DIR = os.path.join(ROOT, "experiment_results", "archv2", "rp12", "flat_v2")
STATE_DIR = os.path.join(OUT_DIR, "state")
OUTCOME = os.path.join(OUT_DIR, "flat_v2_outcome.txt")
LANE = "r1"
# READY_rp12_r2_lane C-2 (delta flat-r2-pin): lane r2's census of record (the R2 B0 MMLU_PRO_LB member; see the docstring)
T2_R2_CENSUS = dict(snapshot="20261001_094311_Headless_Run_Auto_ge", counts=dict(leaves=74, fit_n=6993))


def set_lane(lane):
    """rp12-r2-lane: re-point T2, its pointer and the outputs to a lane. Lane r1 = the constants above, unchanged. Lane r2: T2 =
    the R2 B0 MMLU_PRO_LB member through the R2 pointer; its census (leaves, fit_n, snapshot) is OWED until a reviewed delta
    pins R2's (so --run / --analyze refuse, check_census refuses); outputs under experiment_results/archv2/rp12_r2/flat_v2/."""
    global LANE, T2, T2_POINTER, T2_CENSUS_SNAPSHOT, OUT_DIR, STATE_DIR, OUTCOME
    import rp12_lane as LN
    LN.check_lane(lane)
    LANE = lane
    if lane == "r1":
        return
    T2 = dict(run="%s/B0/mmlu_pro_lb/seed_42" % LN.results(lane), snapshot=None, **T2_R2_CENSUS["counts"])
    T2_POINTER = (os.path.join(*LN.pointer(lane).split("/")), "B0/mmlu_pro_lb")
    T2_CENSUS_SNAPSHOT = T2_R2_CENSUS["snapshot"]
    OUT_DIR = LN.out_path(lane, "flat_v2")
    STATE_DIR = os.path.join(OUT_DIR, "state")
    OUTCOME = os.path.join(OUT_DIR, "flat_v2_outcome.txt")


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _blob(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


for _f, _b in PINS.items():
    _p = os.path.join(HERE, _f)
    if _blob(_p) != _b:
        refuse("%s is blob:%s, not the pinned blob:%s" % (_p, _blob(_p), _b))
import flat_mix_mmlu as FM  # noqa: E402
import v2_engine_pool as EP  # noqa: E402
AF, F, split_side = FM.AF, FM.F, FM.split_side


def script_pins():
    return FM.pins_of(os.path.abspath(__file__))


# ── the v2 inputs ───────────────────────────────────────────────────────────────────────────────────────────────────

def side_map(side_path=None):
    """S1 + S2 on the committed side export: {item_id: (component, side, corpora)}, its meta; the pool id recomputed."""
    items, meta = EP.read_side(side_path or os.path.join(ROOT, EP.DEFAULT_SIDE))
    got, n_comp = EP.pool_of(items, CORPUS)
    if got != POOL_V2:
        refuse("the side export's %s pool is %s, not %s" % (CORPUS, got, POOL_V2))
    return items, meta, n_comp


def engine_pool(path, items_meta, sha_lf=None):
    """The engine pool file: its pool id and side-export pin must be the ones read now; sha_lf pinned when given."""
    raw = open(path, "rb").read().replace(b"\r\n", b"\n")
    got = hashlib.sha256(raw).hexdigest()
    if sha_lf is not None and got != sha_lf:
        refuse("engine pool file %s sha256 (LF) %s != the pinned %s" % (path, got, sha_lf))
    doc = json.loads(raw.decode("utf-8"))
    if doc.get("pool_id") != POOL_V2 or doc.get("format") != EP.FORMAT:
        refuse("engine pool file %s is not %s's (%s / %s)" % (path, POOL_V2, doc.get("format"), doc.get("pool_id")))
    if doc["side_export"]["sha256_lf"] != items_meta["sha256_lf"]:
        refuse("engine pool file %s pins side export sha256 (LF) %s, the export read now is %s"
               % (path, doc["side_export"]["sha256_lf"], items_meta["sha256_lf"]))
    return doc, got


def item_of(text):
    return "i:" + split_side.stem_key(text)


def v2_sets(train, heldout, fit_texts, items):
    """R2 / hygiene on the corpus the readout functions see: held-out items EVAL, the label set restricted to TRAIN items,
    fit texts TRAIN. -> (train restricted, counts). REFUSES on a held-out text that is not EVAL or a fit text that is not TRAIN."""
    bad_h = [t for t, _ in heldout if items.get(item_of(t), (None, None))[1] != "EVAL"]
    if bad_h:
        refuse("%d held-out text(s) are not EVAL items of the side export (first %r)" % (len(bad_h), bad_h[0][:60]))
    sides = [items.get(item_of(t), (None, "ABSENT"))[1] for t, _ in train]
    kept = [tc for tc, s in zip(train, sides) if s == "TRAIN"]
    dropped = {s: sides.count(s) for s in set(sides) if s != "TRAIN"}
    bad_f = {}
    for t in fit_texts:
        s = items.get(item_of(t), (None, "ABSENT"))[1]
        if s != "TRAIN":
            bad_f[s] = bad_f.get(s, 0) + 1
    if bad_f:
        refuse("fit texts that are not TRAIN items of the side export: %s (no EVAL or GATE text may enter any fit)" % bad_f)
    return kept, dict(train_in=len(train), train_kept=len(kept), train_dropped=dropped)


def reconcile(heldout, items, n_ids):
    """C-6: the held-out set (R1: judgeable EVAL ids) against the registered 3,492 items / 3,400 components. -> dict of the
    printed values; gap = the larger relative gap of items and components; within iff gap <= 5%."""
    its = {item_of(t) for t, _ in heldout}
    comps = {items[i][0] for i in its if i in items}
    ev_items = [i for i, (c, s, cs) in items.items() if s == "EVAL" and CORPUS in cs]
    g_items = abs(len(its) - REG_ITEMS) / REG_ITEMS
    g_comps = abs(len(comps) - REG_COMPONENTS) / REG_COMPONENTS
    gap = max(g_items, g_comps)
    return dict(ids=n_ids, texts=len({t for t, _ in heldout}), items=len(its), components=len(comps),
                export_items=len(ev_items), gap=gap, within=bool(gap <= RECONCILE_LIMIT + 1e-12))


def reconcile_line(r):
    return ("RECONCILE (C-6): held-out = %d judgeable EVAL ids -> %d distinct texts -> %d items in %d components; registered %d"
            " items / %d components (the export lists %d EVAL items of %s); gap %.2f%% -> %s"
            % (r["ids"], r["texts"], r["items"], r["components"], REG_ITEMS, REG_COMPONENTS, r["export_items"], CORPUS, 100 * r["gap"],
               "WITHIN 5%" if r["within"] else "OVER 5%%: re-stated by bracket before any read (bracket %s)" % (RECONCILE_BRACKET or "OWED")))


def reconcile_gate(r):
    """--analyze refuses a gap over 5% until a bracket is set (the registration's rule)."""
    if not r["within"] and RECONCILE_BRACKET is None:
        refuse(reconcile_line(r))
    return reconcile_line(r)


def component_groups(heldout, items):
    """Group index per held-out question = its CK-CLOSE component (R3)."""
    comps = [items[item_of(t)][0] for t, _ in heldout]
    _, g = np.unique(np.array(comps), return_inverse=True)
    return g.astype(int), int(g.max()) + 1 if len(g) else 0


def boot(diff, groups, B=BOOT_B, seed=BOOT_SEED):
    """flat_mix_mmlu's whole-group draw and percentile rule at B / seed -> (lo, hi, se)."""
    diff = np.asarray(diff, dtype=np.float64)
    members = FM.group_members(groups)
    rng = np.random.default_rng(seed)
    reps = np.array([diff[FM.twin_boot_indices(groups, rng, members)].mean() for _ in range(B)])
    bs = sorted(float(x) for x in reps)
    return bs[int(0.025 * B)], bs[int(0.975 * B) - 1], float(reps.std(ddof=1))


def paired_v2(arms, groups, arm="T", refs=("V0", "K0")):
    out = {}
    for a in refs:
        d1 = arms[arm]["per1"] - arms[a]["per1"]
        lo1, hi1, se1 = boot(d1, groups)
        if arms[arm].get("per4") is None or arms[a].get("per4") is None:
            d4, lo4, hi4 = None, None, None
        else:
            dd4 = arms[arm]["per4"] - arms[a]["per4"]
            d4 = float(dd4.mean())
            lo4, hi4, _ = boot(dd4, groups)
        common = [q for q in arms[arm]["per2"] if q in arms[a]["per2"]]
        d2 = np.array([arms[arm]["per2"][q] - arms[a]["per2"][q] for q in common])
        lo2, hi2 = F.boot_mean_ci(d2)
        v_iid = float(d1.var(ddof=1)) / len(d1) if len(d1) > 1 else float("nan")
        out[a] = dict(d1=float(d1.mean()), d1_lo=lo1, d1_hi=hi1, se1=se1, deff1=(se1 ** 2 / v_iid) if v_iid > 0 else float("nan"),
                      d2=float(d2.mean()), d2_lo=lo2, d2_hi=hi2, d4=d4, d4_lo=lo4, d4_hi=hi4)
    return out


def readout(arms, groups, G):
    p = paired_v2(arms, groups)
    sv = {m: FM.spread_opt([arms["V%d" % s][m] for s in SEEDS]) for m in ("m1", "m2", "m4")}
    v = p["V0"]
    c1 = bool(FM.criterion(v["d1"], sv["m1"], v["d1_lo"], v["d1_hi"]))
    c2 = bool(FM.criterion(v["d2"], sv["m2"], v["d2_lo"], v["d2_hi"]))
    l1_m1 = bool(FM.loss(v["d1"], sv["m1"], v["d1_lo"], v["d1_hi"]))
    l1_m2 = bool(FM.loss(v["d2"], sv["m2"], v["d2_lo"], v["d2_hi"]))
    return dict(n=len(groups), G=G, kish=FM.kish_mbar(groups), paired=p, spread_V=sv, c1=c1, c2=c2, l1_m1=l1_m1, l1_m2=l1_m2,
                l1=bool(l1_m1 or l1_m2), arms={a: {k: arms[a].get(k) for k in ("m1", "m1_lo", "m1_hi", "m2", "m3", "m4", "m4_void")}
                                                for a in arms}, n_keyed=len(arms["T"]["per2"]))


def _band(x, band):
    return "HELD" if band[0] <= x <= band[1] else "FAILED"


def render(r, meta):
    o = []
    say = o.append
    v, sv = r["paired"]["V0"], r["spread_V"]
    say("POOL %s (%s; the first line)" % (POOL_V2, CORPUS))
    say("%s FLAT on the v2 split | registration %s" % (TAG, REGISTRATION))
    for k in ("script", "instrument", "side_export", "engine_pool", "tree", "identity"):
        if k in meta:
            say("  %s: %s" % (k, meta[k]))
    say("SUPPORT: held-out %d questions in %d CK-CLOSE components (registered %d items / %d components); Kish mean %.4f;"
        " keyed (M2) %d" % (r["n"], r["G"], REG_ITEMS, REG_COMPONENTS, r["kish"], r["n_keyed"]))
    say("  M1 paired SE (component bootstrap, B %d) %.5f (registered %.5f); DEFF measured %.3f (declared %.2f); n_eff %.0f"
        " (registered %d); MDE80 %.4f (registered %.4f); effective bar max(MDE, spread_V) = %.4f"
        % (BOOT_B, v["se1"], SE_M1, v["deff1"], DEFF_M1, (r["n"] / v["deff1"]) if v["deff1"] == v["deff1"] and v["deff1"] > 0 else float("nan"),
           NEFF_M1, 2.80 * v["se1"], MDE_M1, max(2.80 * v["se1"], sv["m1"])))
    say("ARMS (M1 purity [Wilson] | M2 F6 x1000 | M3 | M4 nats):")
    for a in r["arms"]:
        x = r["arms"][a]
        m4 = x["m4_void"] if x.get("m4") is None else "%.4f" % x["m4"]
        say("  %-3s M1 %.4f [%.4f, %.4f] | M2 %+.3f | M3 %s | M4 %s" % (a, x["m1"], x["m1_lo"], x["m1_hi"], 1000 * x["m2"],
                                                                    "NA" if x["m3"] is None else "%.4f" % x["m3"], m4))
    say("spread_V: M1 %.4f (transported %.4f) | M2 %+.3f x1e-3 (transported %.3f) | M4 %s"
        % (sv["m1"], SPREAD_V_M1, 1000 * sv["m2"], 1000 * SPREAD_V_M2, "VOID" if sv["m4"] is None else "%.4f" % sv["m4"]))
    say("D1 = M1(T2) - M1(V0) = %+.4f  95%% [%+.4f, %+.4f] (CK-CLOSE components whole, B %d, seed %d)"
        % (v["d1"], v["d1_lo"], v["d1_hi"], BOOT_B, BOOT_SEED))
    say("D2 = M2(T2) - M2(V0) = %+.3f x1e-3  95%% [%+.3f, %+.3f] x1e-3 (F6's boot_mean_ci over the keyed questions)"
        % (1000 * v["d2"], 1000 * v["d2_lo"], 1000 * v["d2_hi"]))
    if v["d4"] is not None:
        say("D4 = M4(T2) - M4(V0) = %+.4f nats [%+.4f, %+.4f] (DESCRIPTIVE)" % (v["d4"], v["d4_lo"], v["d4_hi"]))
    say("C1 PURITY: %s (D1 %+.4f %s spread_V %.4f; CI %s 0 on the positive side)"
        % ("HELD" if r["c1"] else "FAILED", v["d1"], ">" if v["d1"] > sv["m1"] else "<=", sv["m1"], "excludes" if v["d1_lo"] > 0 else "does not exclude"))
    say("C2 (M2, F6 x1000): %s (D2 %+.3f %s spread_V %.3f x1e-3; CI %s 0 on the positive side)"
        % ("HELD" if r["c2"] else "FAILED", 1000 * v["d2"], ">" if v["d2"] > sv["m2"] else "<=", 1000 * sv["m2"],
           "excludes" if v["d2_lo"] > 0 else "does not exclude"))
    if r["l1"]:
        say("L1 LOSS FLAG: FIRES (on %s)" % " and ".join(m for m, f in (("M1", r["l1_m1"]), ("M2", r["l1_m2"])) if f))
    else:
        say("L1 LOSS FLAG: does not fire (DESCRIPTIVE-ONLY at the prediction; a non-fire is never read as parity)")
    say("F3: %s" % ("FIRES: F-TAX's partition clause extends from af_clean_s42 (one draw) to the v2 anchored tree; FLAT-MIX-MMLU's"
                    " anchored control 'ties, reported only' no longer describes the presented tree" if r["l1"]
                    else "does not fire (L1 did not fire)"))
    say("P7 M1(T2) - M1(V0) = -0.015 [-0.040, +0.010]: observed %+.4f -> %s" % (v["d1"], _band(v["d1"], P7_M1)))
    say("P7 M2 difference = -0.5 [-1.8, +0.8] x1e-3: observed %+.3f x1e-3 -> %s" % (1000 * v["d2"], _band(v["d2"], P7_M2)))
    say("P7 C1 FAILED (0.85): observed %s | C2 FAILED (0.85): observed %s | L1 fires (0.30): observed %s"
        % ("HELD" if r["c1"] else "FAILED", "HELD" if r["c2"] else "FAILED", "FIRES" if r["l1"] else "does not fire"))
    say("K0 beside: D1 vs K0 %+.4f [%+.4f, %+.4f]; D2 vs K0 %+.3f x1e-3" % (r["paired"]["K0"]["d1"], r["paired"]["K0"]["d1_lo"],
                                                                           r["paired"]["K0"]["d1_hi"], 1000 * r["paired"]["K0"]["d2"]))
    say("WORDS: v2 objects are content-closed under CK-CLOSE-v2 (residual disclosed); the partition clause names one tree, B0's"
        " MMLU-Pro member, at its own k")
    return o


# ── real-data paths (preconditions; pool reader) ────────────────────────────────────────────────────────────────────

def t2_snapshot_from_pointer(root=ROOT):
    """F-1: T2's snapshot id from the pointer file entry (None while the pointer or the entry is owed)."""
    p = os.path.join(root, T2_POINTER[0])
    if not os.path.isfile(p):
        return None
    e = json.load(open(p, encoding="utf-8")).get("entries", {}).get(T2_POINTER[1])
    return None if e is None else e["snapshot_id"]


def t2_census(graph_byid, root_id):
    """F-1: the census to pin: leaf nodes (no children) and the root region's distinct query ids (FM.region_query_ids)."""
    leaves = sum(1 for n in graph_byid.values() if not (n.get("childIds") or []))
    return leaves, len(FM.region_query_ids(root_id, graph_byid))


def check_census(snapshot, leaves, fit_n):
    """F-3: the census read now must be the pinned one (snapshot, leaves, root fit ids); anything else is a STOP for the
    registrar (REFUSED; nothing is fitted or measured). Returns the printed line."""
    want = (T2_CENSUS_SNAPSHOT, T2["leaves"], T2["fit_n"])
    if None in want:
        refuse("F-3: lane %s's T2 census is owed (a reviewed delta pins it); nothing is fitted or measured" % LANE)
    if (snapshot, leaves, fit_n) != want:
        refuse("F-3 STOP for the registrar: T2 census snapshot %s, leaves %s, root fit ids %s is not the pinned %s, leaves %s,"
               " fit_n %s" % ((snapshot, leaves, fit_n) + want))
    return "[F-3] T2 census equals the pin: snapshot %s, leaves %d, root fit ids %d" % want


def census_of(snapshot):
    g = FM.load_snapshot_graph(snapshot)
    return t2_census(g["byid"], g["root"])


def t2_spec(over=None, root=ROOT):
    spec = dict(T2)
    if spec["snapshot"] is None:
        spec["snapshot"] = t2_snapshot_from_pointer(root)
    if over:
        spec.update({k: v for k, v in over.items() if v is not None})
    return spec


def check_t2_stamp(stamp, side_meta):
    """D-10: T2's stamp must be the union member pool's (pool, engine pool file sha, the MMLU_PRO namespace only, the rule) on
    the side export read now. REFUSES otherwise; returns the printed line."""
    if stamp is None:
        refuse("D-10: T2's snapshot carries no v2 build stamp")
    bad = ["%s %r (want %r)" % (k, stamp.get(k), v) for k, v in T2_STAMP.items() if stamp.get(k) != v]
    if stamp.get("sideExportSha256Lf") != side_meta["sha256_lf"]:
        bad.append("sideExportSha256Lf %r (the export read now is %r)" % (stamp.get("sideExportSha256Lf"), side_meta["sha256_lf"]))
    if bad:
        refuse("D-10: T2's stamp is not B0's MMLU-Pro member on the union pool: %s" % "; ".join(bad))
    return ("[D-10] T2 stamp: pool %s, engine pool sha256(LF) %s, namespaces %s, side export %s: the union member of the draw"
            % (stamp["poolId"], stamp["enginePoolSha256Lf"][:16], stamp["namespacesLoaded"], stamp["sideExportSha256Lf"][:16]))


def read_t2_stamp(snapshot):
    """settings.buildStamp of T2's snapshot row (snapshots.db, read-only through pool_guard.open_ro)."""
    con = FM.pool_guard.open_ro(FM.data_path("snapshots.db"))
    try:
        row = con.execute("SELECT settings FROM snapshots WHERE id = ?", (snapshot,)).fetchone()
    finally:
        con.close()
    if row is None:
        refuse("D-10: T2 snapshot %s is not in snapshots.db" % snapshot)
    return json.loads(row[0]).get("buildStamp")


def require_preconditions(root=ROOT):
    miss = [k for k, v in t2_spec(root=root).items() if v is None]
    if ENGINE_POOL_SHA_LF is None:
        miss.append("ENGINE_POOL_SHA_LF")
    if miss:
        refuse("preconditions owed: %s (set by a delta after B0 is built and the engine pool file is committed)" % ", ".join(miss))


def v2_corpus(doc, items):
    """anchor_free_readout.corpus on the judgeable EVAL ids (R1) through the eval-id override, the label set restricted by R2."""
    ids = frozenset(i for i in doc["eval_ids"] if i > 0)
    orig = FM.pool_guard.eval_ids
    FM.pool_guard.eval_ids = lambda pid: ids if pid == POOL_V2 else orig(pid)
    try:
        train, heldout, cs = AF.corpus(POOL_V2)
    finally:
        FM.pool_guard.eval_ids = orig
    return train, heldout, sorted(ids), cs


def identity_values(keyed=None, veck=None):
    """R5: af_clean_s42 through this script's path (p2dca pool, 256-d, no side filter)."""
    tree = FM.load_T("T", run=FM.T_RUN, leaves=FM.T_LEAVES, dim=FM.DIM, name="af_clean_s42")
    train, heldout, _ = AF.corpus(FM.POOL_ID)
    vec = AF.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    keyed = F.keyed_questions() if keyed is None else keyed
    veck = F.embed_matrix(AF.EMB_DB, list(keyed[3].values()), FM.DIM) if veck is None else veck
    return FM.identity(tree, train, heldout, vec, keyed, veck, dim=FM.DIM)


def identity_gate(got):
    ok = got["m1"] == FM.RECORD_M1 and got["m2"] == FM.RECORD_M2
    line = ("IDENTITY (R5): af_clean_s42 through this path: M1 %s (recorded %s), M2 %s (recorded %s) -> %s"
            % (got["m1"], FM.RECORD_M1, got["m2"], FM.RECORD_M2, "REPRODUCED" if ok else "MISMATCH"))
    if not ok:
        refuse(line + "; T2 is not read (the registration's identity precondition)")
    return line


def header(over=None):
    items, meta, n_comp = side_map()
    print("POOL %s recomputed from the side export %s (%d EVAL components with a member in %s)" % (POOL_V2, meta["path"], n_comp, CORPUS))
    print("[SCRIPT] tools/analysis/flat_v2.py %s" % FM.fmt_pins(script_pins()))
    for f in PINS:
        print("[PIN] tools/analysis/%s %s (pinned on import)" % (f, FM.fmt_pins(FM.pins_of(os.path.join(HERE, f)))))
    doc, sha = engine_pool(os.path.join(ROOT, ENGINE_POOL_REL), meta, ENGINE_POOL_SHA_LF)   # a committed file of this checkout
    print("[ENGINE-POOL] %s sha256 (LF) %s (pinned %s); eval %d (judgeable %d), gate %d, train %d"
          % (ENGINE_POOL_REL, sha, ENGINE_POOL_SHA_LF, len(doc["eval_ids"]), sum(1 for i in doc["eval_ids"] if i > 0),
             len(doc["gate_ids"]), len(doc["train_ids"])))
    return items, meta, doc, sha


def dry_run(over=None):
    items, meta, doc, _ = header(over)
    spec = t2_spec(over)
    print("[MODE] --dry-run: counts only; NO measure, no fit, nothing written")
    ev_items = [i for i, (c, s, cs) in items.items() if s == "EVAL" and CORPUS in cs]
    print("EVAL items of %s %d (registered %d) in %d components (registered %d)" % (
        CORPUS, len(ev_items), REG_ITEMS, len(set(items[i][0] for i in ev_items)), REG_COMPONENTS))
    train, heldout, heldout_ids, cs = v2_corpus(doc, items)
    fit = []
    if spec["snapshot"]:
        fit, _g, _ids, _t = FM.fit_set(snapshot=spec["snapshot"], fit_n=spec["fit_n"]) if spec["fit_n"] else ([], None, None, None)
    kept, cnt = v2_sets(train, heldout, fit, items)
    groups, G = component_groups(heldout, items)
    print("HELD-OUT (R1) %d judgeable EVAL questions (%d distinct texts) in %d components; Kish mean %.4f (the Sum m^2 / Sum m bound"
          " with variable sizes; D-6)" % (len(heldout), len(set(t for t, _ in heldout)), G, FM.kish_mbar(groups) if len(groups) else float("nan")))
    print(reconcile_line(reconcile(heldout, items, len(heldout_ids))))
    print("LABEL SET (R2): %d corpus texts outside the held-out; kept TRAIN %d; dropped %s" % (cnt["train_in"], cnt["train_kept"], cnt["train_dropped"]))
    if not spec["snapshot"]:
        print("T2: B0 not built yet: the pointer entry %s of %s is owed (F-1); no T2 line" % (T2_POINTER[1], T2_POINTER[0]))
        spec = dict(spec, run=None)
    else:
        print(check_t2_stamp(read_t2_stamp(spec["snapshot"]), meta))
        g = FM.load_snapshot_graph(spec["snapshot"])
        lv, fn = t2_census(g["byid"], g["root"])
        print("T2 census (F-1; pinned by the next reviewed delta): snapshot %s, leaves %d, root fit ids %d; pinned leaves %s, fit_n %s"
              % (spec["snapshot"], lv, fn, T2["leaves"], T2["fit_n"]))
        if not over:                                         # the census overrides of --dry-run are exploratory: printed only
            print(check_census(spec["snapshot"], lv, fn))
    if spec["run"] and spec["leaves"] is not None:
        tr = FM.load_T("T", run=spec["run"], leaves=spec["leaves"], dim=DIM, name="T2")
        print("T2 %s: %d leaves (asserted %s), slice %d; fit set %d texts (asserted %s), all TRAIN" % (spec["run"], len(tr["leaves"]),
              spec["leaves"], tr["dim"], len(fit), spec["fit_n"]))
    else:
        print("T2: not given (B0 not built); the census prints here once --tree-run / --tree-snapshot / --leaves / --fit-n are passed")
    keyed = F.keyed_questions()
    print("KEYED (R4): %d questions, %d models" % (len(keyed[4]), len(keyed[0])))
    print("%s dry-run complete: zero measures, nothing written" % TAG)
    return 0


def ensure_meta(state_dir, spec, pool_sha):
    body = json.dumps(dict(test="ARCH-V2-E-T FLAT", registration=REGISTRATION, spec=spec, script=script_pins(), pins=PINS,
                           k=spec["leaves"], seeds=SEEDS, dim=DIM, boot=[BOOT_B, BOOT_SEED], engine_pool_sha_lf=pool_sha,
                           v=[FM.V_MAX_ITER, FM.V_TOL], km=FM.K_MAX_ITER), sort_keys=True)
    p = os.path.join(state_dir, "meta.json")
    if os.path.exists(p):
        if open(p, encoding="utf-8").read() != body:
            refuse("%s differs from this script's meta; a new state directory is needed" % p)
    else:
        FM.write_once(p, body)


NAMES = ("T",) + tuple("V%d" % s for s in SEEDS) + tuple("K%d" % s for s in SEEDS)


def run(state_dir=None, max_chunks=None):
    state_dir = state_dir or STATE_DIR
    require_preconditions()
    items, meta, doc, sha = header()
    spec = t2_spec()
    print(check_t2_stamp(read_t2_stamp(spec["snapshot"]), meta))                 # D-10: before any T2 read
    print(check_census(spec["snapshot"], *census_of(spec["snapshot"])))         # F-3: before any T2 read
    ensure_meta(state_dir, spec, sha)
    texts, _g, _ids, _t = FM.fit_set(snapshot=spec["snapshot"], fit_n=spec["fit_n"])
    train, heldout, _hids, _cs = v2_corpus(doc, items)
    v2_sets(train, heldout, texts, items)
    X = FM.fit_matrix(texts, dim=DIM)
    done = FM.read_state(state_dir)
    n = 0
    for name in NAMES:
        if name in done:
            continue
        if max_chunks is not None and n >= max_chunks:
            break
        body = FM.fit_partition(name, X, k=spec["leaves"], tree_kw=dict(run=spec["run"], leaves=spec["leaves"], dim=DIM, name="T2"))
        body["instrument"] = body["script"]
        body["script"] = script_pins()
        FM.write_once(os.path.join(state_dir, "part_%s.json" % name), json.dumps(body, sort_keys=True))
        n += 1
        print("%s partition %s fitted; no measure is printed by --run" % (TAG, name))
    print("%s %d partition(s) written" % (TAG, n))
    return 0


def analyze(state_dir=None, outcome=None, identity_fn=None):
    state_dir, outcome = state_dir or STATE_DIR, outcome or OUTCOME
    require_preconditions()
    if os.path.exists(outcome):
        refuse("%s exists: the outcome of record is WRITE-ONCE" % outcome)
    items, meta, doc, sha = header()
    spec = t2_spec()
    t2_line = check_t2_stamp(read_t2_stamp(spec["snapshot"]), meta)          # D-10: before any T2 read
    print(t2_line)
    print(check_census(spec["snapshot"], *census_of(spec["snapshot"])))         # F-3: before any T2 read
    ensure_meta(state_dir, spec, sha)
    parts = FM.read_state(state_dir)
    FM.require_all(parts, names=NAMES)
    keyed = F.keyed_questions()
    veck256 = F.embed_matrix(AF.EMB_DB, list(keyed[3].values()), FM.DIM)
    ident = identity_gate((identity_fn or identity_values)(keyed, veck256))       # BEFORE any T2 read
    train, heldout, heldout_ids, _cs = v2_corpus(doc, items)
    rec_line = reconcile_gate(reconcile(heldout, items, len(heldout_ids)))      # C-6: before any T2 read
    print(rec_line)
    texts, _g, _ids, _t = FM.fit_set(snapshot=spec["snapshot"], fit_n=spec["fit_n"])
    train, _cnt = v2_sets(train, heldout, texts, items)
    vec = AF.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    veck = F.embed_matrix(AF.EMB_DB, list(keyed[3].values()), DIM)
    arms = FM.measures(parts, train, heldout, heldout_ids, vec, keyed, veck, names=NAMES, dim=DIM)
    groups, G = component_groups(heldout, items)
    r = readout(arms, groups, G)
    lines = render(r, dict(script="tools/analysis/flat_v2.py %s" % FM.fmt_pins(script_pins()), side_export=json.dumps(meta, sort_keys=True),
                           engine_pool="%s sha256 (LF) %s" % (ENGINE_POOL_REL, sha), tree=json.dumps(spec, sort_keys=True), identity=ident))
    FM.write_once(outcome, "\n".join(lines) + "\n")
    print("\n".join(lines))
    print("%s wrote %s (write-once)" % (TAG, outcome))
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────

def f3_dry_run_cli():
    """D-FLAT-1: the CLI dry-run's [F-3] line, by value, through main() and the real dry_run (data readers stubbed; no DB)."""
    import types
    byid = {"root": {"id": "root", "childIds": ["L%d" % i for i in range(74)], "queryIds": []}}
    for i in range(74):
        byid["L%d" % i] = {"id": "L%d" % i, "childIds": [], "queryIds": [str(q) for q in range(i, 6993, 74)]}
    g = globals()
    keep = {k: g[k] for k in ("header", "v2_corpus", "v2_sets", "component_groups", "reconcile", "reconcile_line", "read_t2_stamp",
                              "check_t2_stamp", "F")}
    keep.update({k: g[k] for k in ("T2", "T2_POINTER", "T2_CENSUS_SNAPSHOT", "OUT_DIR", "STATE_DIR", "OUTCOME", "LANE")})
    fm_keep = {k: getattr(FM, k) for k in ("load_snapshot_graph", "fit_set", "load_T", "kish_mbar")}
    outs = []
    try:
        g.update(header=lambda over=None: ({}, {"sha256_lf": "s"}, {"eval_ids": []}, "x"), v2_corpus=lambda doc, items: ([], [], [], None),
                 v2_sets=lambda *a_: ([], dict(train_in=0, train_kept=0, train_dropped=0)), component_groups=lambda *a_: ([], 0),
                 reconcile=lambda *a_: None, reconcile_line=lambda r: "RECONCILE stub", read_t2_stamp=lambda sid: None,
                 check_t2_stamp=lambda st, meta: "[D-10] stub", F=types.SimpleNamespace(keyed_questions=lambda: ([0] * 18, 0, 0, {}, [0] * 5)))
        FM.load_snapshot_graph = lambda sid: dict(sha="x", byid=byid, root="root")
        FM.fit_set = lambda snapshot=None, fit_n=None: (["t%d" % i for i in range(fit_n)], None, None, None)
        FM.load_T = lambda *a_, **k_: dict(leaves=list(range(k_["leaves"])), dim=512)
        FM.kish_mbar = lambda groups: 1.0
        for argv in (["--dry-run", "--lane", "r2"], ["--dry-run", "--lane", "r2", "--leaves", "74"]):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main(argv)
            outs.append((rc, buf.getvalue()))
    finally:
        g.update(keep)
        for k, v in fm_keep.items():
            setattr(FM, k, v)
    f3 = "[F-3] T2 census equals the pin: snapshot 20261001_094311_Headless_Run_Auto_ge, leaves 74, root fit ids 6993"
    rc, t = outs[0]
    assert rc == 0 and f3 in t.splitlines(), t
    assert "T2 census (F-1; pinned by the next reviewed delta): snapshot 20261001_094311_Headless_Run_Auto_ge, leaves 74, root fit ids 6993;" \
        " pinned leaves 74, fit_n 6993" in t, t
    lines = t.splitlines()
    assert lines.index(f3) == [i for i, l in enumerate(lines) if l.startswith("T2 census (F-1;")][0] + 1, t     # right after the census
    rc2, t2 = outs[1]
    assert rc2 == 0 and "T2 census (F-1;" in t2 and "[F-3]" not in t2, t2          # an exploratory override: printed, not checked
    return True


def _arms(rng, n=300, gain=0.0, d2=0.0, nq=80, spread=0.0):
    """Per-question arms: V0-V4 equal up to a per-seed M1 shift (spread), K0-K4 a copy of V0, T = V0 with `gain` of its
    misses turned to hits (gain < 0: hits turned to misses); M2 per-question with T offset by d2."""
    base = (rng.uniform(size=n) < 0.7).astype(float)
    qs = ["q%03d" % i for i in range(nq)]
    arms = {}
    for a in NAMES:
        per1 = base.copy()
        if a[0] == "V" and a != "V0":
            s = int(a[1:])
            k = int(round(spread * n * s / 4.0))
            idx = np.flatnonzero(per1 == 0)[:k]
            per1[idx] = 1.0
        per2 = {q: 0.010 + 0.0002 * ((i * 7) % 5) for i, q in enumerate(qs)}
        if a == "T":
            if gain >= 0:
                idx = np.flatnonzero(per1 == 0)[:int(round(gain * n))]
                per1[idx] = 1.0
            else:
                idx = np.flatnonzero(per1 == 1)[:int(round(-gain * n))]
                per1[idx] = 0.0
            per2 = {q: x + d2 for q, x in per2.items()}
        per4 = -1.0 + 0.001 * np.cos(np.arange(n) + len(a))
        m1 = float(per1.mean())
        arms[a] = dict(m1=m1, m1_lo=m1 - 0.02, m1_hi=m1 + 0.02, per1=per1, m2=float(np.mean(list(per2.values()))), per2=per2,
                       m3=0.8, m4=float(per4.mean()), per4=per4, m4_void=None)
    return arms


def selftest():
    import tempfile, shutil; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        try:
            fn()
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))

    rng = np.random.default_rng(5)
    groups = np.arange(300) // 3                     # components of three questions

    def held():
        arms = _arms(rng, gain=0.10, d2=0.002, spread=0.0)
        r = readout(arms, groups, 100)
        assert r["c1"] and r["c2"] and not r["l1"], r
        t = "\n".join(render(r, {}))
        assert t.splitlines()[0] == "POOL pv2_41dbd3dbcd399df0 (mmlu-pro-v2; the first line)"
        assert "C1 PURITY: HELD (D1 +0.1000 > spread_V 0.0000; CI excludes 0 on the positive side)" in t, t
        assert "C2 (M2, F6 x1000): HELD (D2 +2.000 > spread_V 0.000 x1e-3" in t, t
        assert "L1 LOSS FLAG: does not fire (DESCRIPTIVE-ONLY at the prediction; a non-fire is never read as parity)" in t
        assert "F3: does not fire (L1 did not fire)" in t
        assert "P7 M1(T2) - M1(V0) = -0.015 [-0.040, +0.010]: observed +0.1000 -> FAILED" in t
        assert "P7 M2 difference = -0.5 [-1.8, +0.8] x1e-3: observed +2.000 x1e-3 -> FAILED" in t
        assert "(CK-CLOSE components whole, B 2000, seed 20260929)" in t, t
        lo_, hi_ = FM.twin_boot_ci(arms["T"]["per1"] - arms["V0"]["per1"], groups, B=2000, seed=20260929)
        assert (r["paired"]["V0"]["d1_lo"], r["paired"]["V0"]["d1_hi"]) == (lo_, hi_)

    def loss():
        arms = _arms(rng, gain=-0.10, d2=-0.002, spread=0.0)
        r = readout(arms, groups, 100)
        assert (not r["c1"]) and (not r["c2"]) and r["l1"] and r["l1_m1"] and r["l1_m2"], r
        t = "\n".join(render(r, {}))
        assert "C1 PURITY: FAILED (D1 -0.1000 <= spread_V 0.0000; CI does not exclude 0 on the positive side)" in t, t
        assert "L1 LOSS FLAG: FIRES (on M1 and M2)" in t and t.count("F3: FIRES") == 1
        r2 = readout(_arms(rng, gain=0.0, d2=-0.002, spread=0.0), groups, 100)     # M2 alone
        t2 = "\n".join(render(r2, {}))
        assert r2["l1"] and r2["l1_m2"] and not r2["l1_m1"] and "L1 LOSS FLAG: FIRES (on M2)" in t2 and "F3: FIRES" in t2, t2

    def spread_blocks():
        # T wins M1 by 0.02 with an interval above 0, but the V seeds spread by 0.04 -> C1 FAILED, and a small loss inside the
        # spread does not fire L1; the P7 band endpoints are inclusive
        arms = _arms(np.random.default_rng(21), gain=0.02, d2=0.0, spread=0.04)
        r = readout(arms, groups, 100)
        assert abs(r["spread_V"]["m1"] - 0.04) < 1e-12, r["spread_V"]
        assert r["paired"]["V0"]["d1_lo"] > 0 and not r["c1"], r["paired"]["V0"]
        arms2 = _arms(np.random.default_rng(22), gain=-0.03, d2=0.0, spread=0.04)
        r2 = readout(arms2, groups, 100)
        assert r2["paired"]["V0"]["d1_hi"] < 0 and not r2["l1_m1"], r2["paired"]["V0"]
        assert _band(-0.040, P7_M1) == "HELD" and _band(0.010, P7_M1) == "HELD" and _band(0.0101, P7_M1) == "FAILED"

    def boot_matches_instrument():
        d = (rng.uniform(size=300) < 0.5).astype(float) - 0.4
        lo, hi, se = boot(d, groups)
        lo2, hi2 = FM.twin_boot_ci(d, groups, B=BOOT_B, seed=BOOT_SEED)
        assert (lo, hi) == (lo2, hi2), ((lo, hi), (lo2, hi2))
        # component whole: the same diff under item groups gives another interval
        lo3, hi3, _ = boot(d, np.arange(300))
        assert (lo3, hi3) != (lo, hi)
        r = readout(_arms(rng, gain=0.05), groups, 100)
        d1 = _arms(np.random.default_rng(5), gain=0.05)
        assert r["paired"]["V0"]["d1_lo"] <= r["paired"]["V0"]["d1"] <= r["paired"]["V0"]["d1_hi"]

    def sets_and_groups():
        mk = lambda t: item_of(t)
        items = {mk("h1"): ("c:A", "EVAL", {"mmlu-pro-v2"}), mk("h2"): ("c:A", "EVAL", {"mmlu-pro-v2"}), mk("h3"): ("c:B", "EVAL", {"mmlu-pro-v2"}),
                 mk("t1"): ("c:T1", "TRAIN", {"mmlu-pro-v2"}), mk("g1"): ("c:G1", "GATE", {"mmlu-pro-v2"}),
                 mk("s1"): ("c:S1", "EVAL", {"mmlu-pro-v2"})}
        heldout = [("h1", "x"), ("h2", "x"), ("h3", "y")]
        train = [("t1", "x"), ("g1", "y"), ("s1", "x"), ("zz", "x")]
        kept, cnt = v2_sets(train, heldout, ["t1"], items)
        assert kept == [("t1", "x")] and cnt["train_dropped"] == {"GATE": 1, "EVAL": 1, "ABSENT": 1}, cnt
        g, G = component_groups(heldout, items)
        assert G == 2 and g[0] == g[1] != g[2], g
        for extra in ("t1", "g1"):           # a TRAIN and (READY RA6) a GATE held-out text
            try:
                v2_sets(train, heldout + [(extra, "x")], ["t1"], items)
                raise AssertionError("a %s held-out text not refused" % extra)
            except SystemExit as e:
                assert "1 held-out text(s) are not EVAL items" in str(e), e
        try:
            v2_sets(train, heldout, ["t1", "g1"], items)
            raise AssertionError("a GATE fit text not refused")
        except SystemExit as e:
            assert "fit texts that are not TRAIN items of the side export: {'GATE': 1}" in str(e), e

    def committed_export():
        items, meta, n_comp = side_map()
        assert n_comp == REG_COMPONENTS and meta["rows"] == 20544
        assert sum(1 for (c, s, cs) in items.values() if s == "EVAL" and CORPUS in cs) == REG_ITEMS

    def preconditions():
        import tempfile, shutil; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
        # rp12-flat-pin: leaves and fit_n are pinned; only the snapshot stays owed while the pointer entry is (an empty root)
        tmp = tempfile.mkdtemp(prefix="flatv2pre_")
        try:
            try:
                require_preconditions(root=tmp)
                raise AssertionError("no refusal while owed")
            except SystemExit as e:
                assert str(e) == ("%s REFUSED: preconditions owed: snapshot (set by a delta after B0 is built and the engine pool"
                                  " file is committed)" % TAG), e
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        assert (T2["leaves"], T2["fit_n"], T2_CENSUS_SNAPSHOT) == (74, 6993, "20261001_070346_Headless_Run_Auto_ge")
        # rp12-r2-lane: lane r2 re-points T2 / the pointer / the outputs and leaves the census OWED (a STOP); lane r1 restores
        saved = (T2, T2_POINTER, T2_CENSUS_SNAPSHOT, OUT_DIR, STATE_DIR, OUTCOME, LANE)
        try:
            set_lane("r2")
            assert (T2["run"], T2_POINTER[0].replace(os.sep, "/"), T2_CENSUS_SNAPSHOT, T2["leaves"], T2["fit_n"]) == (
                "experiment_results/archv2/rp12_r2/B0/mmlu_pro_lb/seed_42", "experiment_configs/rp12_r2/objects_of_record.json",
                "20261001_094311_Headless_Run_Auto_ge", 74, 6993)
            assert OUTCOME == os.path.join(ROOT, "experiment_results", "archv2", "rp12_r2", "flat_v2", "flat_v2_outcome.txt"), OUTCOME
            # flat-r2-pin: the R2 census passes; R1's snapshot (same counts) is a STOP in lane r2; the R2 pointer names the pin
            assert check_census("20261001_094311_Headless_Run_Auto_ge", 74, 6993) == (
                "[F-3] T2 census equals the pin: snapshot 20261001_094311_Headless_Run_Auto_ge, leaves 74, root fit ids 6993")
            try:
                check_census("20261001_070346_Headless_Run_Auto_ge", 74, 6993)
                raise AssertionError("the R1 census admitted in lane r2")
            except SystemExit as e:
                assert str(e).startswith("%s REFUSED: F-3 STOP for the registrar: T2 census snapshot 20261001_070346_Headless_Run_Auto_ge" % TAG), e
            assert t2_snapshot_from_pointer(ROOT) == "20261001_094311_Headless_Run_Auto_ge" == t2_spec()["snapshot"]
            tmp2 = tempfile.mkdtemp(prefix="flatv2lane_")
            try:
                try:
                    require_preconditions(root=tmp2)
                    raise AssertionError("lane r2 snapshot not owed without the pointer")
                except SystemExit as e:
                    assert str(e) == ("%s REFUSED: preconditions owed: snapshot (set by a delta after B0 is built and the engine pool"
                                      " file is committed)" % TAG), e
            finally:
                shutil.rmtree(tmp2, ignore_errors=True)
        finally:
            globals().update(dict(zip(("T2", "T2_POINTER", "T2_CENSUS_SNAPSHOT", "OUT_DIR", "STATE_DIR", "OUTCOME", "LANE"), saved)))
        # D-1 (the reviewer's M8): main() itself sets the lane: --dry-run --lane r2 with dry_run stubbed sees the R2 T2, pointer,
        # census pin and outputs; --dry-run with no --lane sees R1's
        seen = []
        real_dry = globals()["dry_run"]
        try:
            globals()["dry_run"] = lambda over: seen.append((dict(T2), T2_POINTER[0].replace(os.sep, "/"), T2_CENSUS_SNAPSHOT, OUTCOME, STATE_DIR, LANE, over)) or 0
            assert main(["--dry-run", "--lane", "r2"]) == 0
            globals().update(dict(zip(("T2", "T2_POINTER", "T2_CENSUS_SNAPSHOT", "OUT_DIR", "STATE_DIR", "OUTCOME", "LANE"), saved)))
            assert main(["--dry-run"]) == 0
        finally:
            globals()["dry_run"] = real_dry
            globals().update(dict(zip(("T2", "T2_POINTER", "T2_CENSUS_SNAPSHOT", "OUT_DIR", "STATE_DIR", "OUTCOME", "LANE"), saved)))
        r2o = os.path.join(ROOT, "experiment_results", "archv2", "rp12_r2", "flat_v2")
        assert seen[0][:6] == (dict(run="experiment_results/archv2/rp12_r2/B0/mmlu_pro_lb/seed_42", snapshot=None, leaves=74, fit_n=6993),
                               "experiment_configs/rp12_r2/objects_of_record.json", "20261001_094311_Headless_Run_Auto_ge",
                               os.path.join(r2o, "flat_v2_outcome.txt"), os.path.join(r2o, "state"), "r2"), seen[0]
        assert seen[1][0]["run"] == "experiment_results/archv2/rp12/B0/mmlu_pro_lb/seed_42" and seen[1][2] == "20261001_070346_Headless_Run_Auto_ge" \
            and seen[1][3] == os.path.join(ROOT, "experiment_results", "archv2", "rp12", "flat_v2", "flat_v2_outcome.txt") and seen[1][5] == "r1", seen[1]
        try:
            main(["--dry-run", "--lane", "r1", "--tree-run", "experiment_results/archv2/rp12_r2/B0/mmlu_pro_lb/seed_42"])
            raise AssertionError("an R2 tree run in lane r1 not refused")
        except SystemExit as e:
            assert "is an object of lane r2, the run is lane r1" in str(e), e
        finally:
            globals().update(dict(zip(("T2", "T2_POINTER", "T2_CENSUS_SNAPSHOT", "OUT_DIR", "STATE_DIR", "OUTCOME", "LANE"), saved)))
        # F-3: the census of record passes and prints; any other value (each field alone) is a STOP for the registrar
        assert check_census("20261001_070346_Headless_Run_Auto_ge", 74, 6993) == (
            "[F-3] T2 census equals the pin: snapshot 20261001_070346_Headless_Run_Auto_ge, leaves 74, root fit ids 6993")
        for args in (("20261001_070346_Headless_Run_Auto_gf", 74, 6993), ("20261001_070346_Headless_Run_Auto_ge", 73, 6993),
                     ("20261001_070346_Headless_Run_Auto_ge", 75, 6993), ("20261001_070346_Headless_Run_Auto_ge", 74, 6992),
                     ("20261001_070346_Headless_Run_Auto_ge", 74, 6994), (None, 74, 6993)):
            try:
                check_census(*args)
                raise AssertionError("census %s not refused" % (args,))
            except SystemExit as e:
                assert str(e).startswith("%s REFUSED: F-3 STOP for the registrar: T2 census snapshot %s, leaves %s, root fit ids %s"
                                         % ((TAG,) + args)), e
        # --run and --analyze check the census before any T2 read (source order; both need the DBs)
        import inspect
        for fn in (run, analyze):
            src = inspect.getsource(fn)
            assert src.index("check_census(spec[\"snapshot\"], *census_of(spec[\"snapshot\"]))") < src.index("FM.fit_set("), fn.__name__
        # D-FLAT-1 (replaces the source-order check): main(["--dry-run", "--lane", "r2"]) PRINTS the [F-3] line, through the real
        # dry_run with its data readers stubbed (a 74-leaf, 6,993-id graph); an override (--leaves) prints the census but no [F-3]
        f3_dry_run_cli()

    def f1(tmp=None):
        import tempfile, shutil; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
        tmp = tempfile.mkdtemp(prefix="flatv2f1_")
        try:
            assert t2_snapshot_from_pointer(tmp) is None and t2_spec(root=tmp)["snapshot"] is None
            os.makedirs(os.path.join(tmp, "experiment_configs", "rp12"))
            with open(os.path.join(tmp, T2_POINTER[0]), "w") as f:
                json.dump({"entries": {"B0/bbh": {"snapshot_id": "X"}, "B0/mmlu_pro_lb": {"snapshot_id": "SNAP_MMLU"}}}, f)
            assert t2_snapshot_from_pointer(tmp) == "SNAP_MMLU"
            s = t2_spec(root=tmp)
            assert (s["run"], s["snapshot"]) == ("experiment_results/archv2/rp12/B0/mmlu_pro_lb/seed_42", "SNAP_MMLU"), s
            assert t2_spec(dict(snapshot="OVR"), root=tmp)["snapshot"] == "OVR"
            byid = {"r": {"childIds": ["a", "b", "d"], "queryIds": ["1"]}, "a": {"childIds": [], "queryIds": ["2", "3"]},
                    "b": {"childIds": ["c"], "queryIds": ["3"]}, "c": {"childIds": [], "queryIds": ["4"]}, "d": {"childIds": [], "queryIds": []}}
            assert t2_census(byid, "r") == (3, 4), t2_census(byid, "r")      # 3 leaves (a, c, d), 2 internal; 4 distinct ids
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        # the run dir is the B0 MMLU_PRO_LB member's outputDir of the committed build config
        cfg = open(os.path.join(ROOT, "experiment_configs", "rp12", "B0", "mmlu_pro_lb.toml"), encoding="utf-8").read()
        assert 'outputDir     = "%s"' % T2["run"].rsplit("/seed_42", 1)[0] in cfg

    def t2_stamp():
        items, meta, _n = side_map()
        good = dict(T2_STAMP, sideExportSha256Lf=meta["sha256_lf"], trainRows=6994, seed=42)
        assert check_t2_stamp(good, meta) == ("[D-10] T2 stamp: pool pv2_1575de61bb20e977, engine pool sha256(LF) 79d48f4b36434a55,"
                                              " namespaces ['MMLU_PRO'], side export %s: the union member of the draw" % meta["sha256_lf"][:16])
        for over, needle in ((dict(poolId="pv2_41dbd3dbcd399df0"), "poolId 'pv2_41dbd3dbcd399df0'"),
                             (dict(enginePoolSha256Lf="0" * 64), "enginePoolSha256Lf '0000"),
                             (dict(namespacesLoaded=["BBH"]), "namespacesLoaded ['BBH']"),
                             (dict(namespacesLoaded=["MMLU_PRO", "BBH"]), "namespacesLoaded ['MMLU_PRO', 'BBH']"),
                             (dict(sideExportSha256Lf="f" * 64), "sideExportSha256Lf 'ffff"),
                             (dict(rule="CK-CLOSE-v1"), "rule 'CK-CLOSE-v1'")):
            try:
                check_t2_stamp(dict(good, **over), meta)
                raise AssertionError("not refused: %s" % over)
            except SystemExit as e:
                assert str(e).startswith("%s REFUSED: D-10: T2's stamp is not B0's MMLU-Pro member on the union pool: " % TAG) and needle in str(e), e
        try:
            check_t2_stamp(None, meta)
            raise AssertionError("no stamp not refused")
        except SystemExit as e:
            assert str(e) == "%s REFUSED: D-10: T2's snapshot carries no v2 build stamp" % TAG
        # the pins equal the committed files (LF sha)
        for rel, want in (("experiment_configs/engine_pool_pv2_41dbd3dbcd399df0.json", ENGINE_POOL_SHA_LF),
                          ("experiment_configs/engine_pool_pv2_1575de61bb20e977.json", T2_STAMP["enginePoolSha256Lf"])):
            assert hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read().replace(b"\r\n", b"\n")).hexdigest() == want, rel
        # --run and --analyze check the stamp before any T2 read (source order; both need the DBs)
        import inspect
        for fn in (run, analyze):
            src = inspect.getsource(fn)
            assert src.index("check_t2_stamp(read_t2_stamp(spec[\"snapshot\"]), meta)") < src.index("FM.fit_set("), fn.__name__

    def identity_gate_refuses():
        assert identity_gate(dict(m1=FM.RECORD_M1, m2=FM.RECORD_M2)).endswith("-> REPRODUCED")
        try:
            identity_gate(dict(m1="0.728 [0.712, 0.741]", m2=FM.RECORD_M2))
            raise AssertionError("mismatch not refused")
        except SystemExit as e:
            assert "MISMATCH; T2 is not read" in str(e), e

    def engine_pool_checks():
        tmp = tempfile.mkdtemp(prefix="flatv2_")
        try:
            items, meta, _ = side_map()
            p = os.path.join(tmp, "pool.json")
            doc = dict(format=EP.FORMAT, pool_id=POOL_V2, side_export=dict(sha256_lf=meta["sha256_lf"]), eval_ids=[1], gate_ids=[], train_ids=[])
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(doc))
            d, sha = engine_pool(p, meta)
            assert d["pool_id"] == POOL_V2 and len(sha) == 64
            for bad, needle in ((dict(doc, pool_id="pv2_0000000000000000"), "is not pv2_41dbd3dbcd399df0's"),
                                (dict(doc, side_export=dict(sha256_lf="0" * 64)), "pins side export sha256 (LF) 0000")):
                with open(p, "w", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps(bad))
                try:
                    engine_pool(p, meta)
                    raise AssertionError("not refused: %s" % needle)
                except SystemExit as e:
                    assert needle in str(e), e
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(doc))
            try:
                engine_pool(p, meta, sha_lf="0" * 64)
                raise AssertionError("pin not refused")
            except SystemExit as e:
                assert "!= the pinned 0000" in str(e), e
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def reconcile_case():
        mk = lambda t: item_of(t)
        items = {mk("h%d" % i): ("c:%d" % (i // 2), "EVAL", {CORPUS}) for i in range(10)}
        items[mk("x")] = ("c:x", "EVAL", {"mc6-2026-09-11"})
        global REG_ITEMS, REG_COMPONENTS
        saved = (REG_ITEMS, REG_COMPONENTS)
        try:
            REG_ITEMS, REG_COMPONENTS = 10, 5
            r = reconcile([("h%d" % i, "c") for i in range(10)] + [("h0", "c")], items, 11)
            assert (r["ids"], r["texts"], r["items"], r["components"], r["export_items"], r["within"]) == (11, 10, 10, 5, 10, True), r
            assert reconcile_line(r).endswith("gap 0.00% -> WITHIN 5%"), reconcile_line(r)
            r2 = reconcile([("h%d" % i, "c") for i in range(9)], items, 9)      # 9 items, 5 components: 10% item gap
            assert abs(r2["gap"] - 0.10) < 1e-12 and not r2["within"]
            try:
                reconcile_gate(r2)
                raise AssertionError("a 10% gap not refused")
            except SystemExit as e:
                assert "gap 10.00% -> OVER 5%: re-stated by bracket before any read (bracket OWED)" in str(e), e
            r3 = reconcile([("h%d" % i, "c") for i in range(8)], items, 8)       # 8 items, 4 components: 20% component gap
            assert abs(r3["gap"] - 0.20) < 1e-12
            # a gap on components alone decides too: 10 items (= registered), 5 components against 8 registered -> 37.5%
            REG_ITEMS, REG_COMPONENTS = 10, 8
            r7 = reconcile([("h%d" % i, "c") for i in range(10)], items, 10)
            assert abs(r7["gap"] - 0.375) < 1e-12 and not r7["within"], r7
            # exactly 5% stays WITHIN: 19 of 20 registered items, components equal
            big = {mk("b%d" % k): ("c:b%d" % k, "EVAL", {CORPUS}) for k in range(20)}
            REG_ITEMS, REG_COMPONENTS = 20, 19
            r5 = reconcile([("b%d" % k, "c") for k in range(19)], big, 19)
            assert abs(r5["gap"] - 0.05) < 1e-12 and r5["within"] and reconcile_gate(r5).endswith("WITHIN 5%"), r5
        finally:
            REG_ITEMS, REG_COMPONENTS = saved

    def analyze_order():
        # --analyze needs the DBs; its C-6 gate is pinned by source order: the gate runs before the T2 fit set is read
        import inspect
        src = inspect.getsource(analyze)
        i_gate, i_fit = src.index("reconcile_gate(reconcile(heldout, items, len(heldout_ids)))"), src.index("FM.fit_set(")
        i_ident = src.index("identity_gate(")
        assert i_ident < i_gate < i_fit, (i_ident, i_gate, i_fit)

    for nm, fn in [("C1 / C2 HELD, L1 silent, P7 FAILED (values)", held), ("C-6 reconciliation: values, the 5% gate", reconcile_case),
                   ("C-6 gate precedes the T2 read in --analyze", analyze_order), ("L1 FIRES on M1 and M2, F3 fires", loss),
                   ("the seed spread blocks C1 and L1; P7 endpoints inclusive", spread_blocks),
                   ("component bootstrap = flat_mix_mmlu's draw at B 2,000 (not item groups)", boot_matches_instrument),
                   ("R2 label set = TRAIN only; held-out EVAL; fit TRAIN; component groups", sets_and_groups),
                   ("committed export: pv2_41dbd3dbcd399df0, 3,492 items / 3,400 components", committed_export),
                   ("--run / --analyze refuse while the preconditions are owed", preconditions),
                   ("identity gate (R5) refuses a mismatch before T2", identity_gate_refuses), ("D-10 T2 stamp check", t2_stamp), ("F-1 T2 from the pointer; the census", f1),
                   ("engine pool file checks", engine_pool_checks)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("--selftest", "--dry-run", "--identity-check", "--run", "--analyze"):
        g.add_argument(m, action="store_true")
    ap.add_argument("--tree-run"); ap.add_argument("--tree-snapshot")
    ap.add_argument("--leaves", type=int); ap.add_argument("--fit-n", type=int)
    ap.add_argument("--max-chunks", type=int)
    import rp12_lane as LN
    LN.add_arg(ap)
    a = ap.parse_args(argv)
    set_lane(a.lane)
    if a.tree_run:
        LN.guard(a.lane, [("--tree-run", a.tree_run)])
    # D-FLAT-1: only the overrides actually given (an all-None dict is truthy and silenced dry_run's F-3 census check)
    over = {k: v for k, v in dict(run=a.tree_run, snapshot=a.tree_snapshot, leaves=a.leaves, fit_n=a.fit_n).items() if v is not None}
    if (a.run or a.analyze or a.identity_check) and over:
        refuse("--tree-* / --leaves / --fit-n are census overrides of --dry-run only; --run / --analyze read the pinned T2")
    if a.selftest:
        return selftest()
    if a.dry_run:
        return dry_run(over)
    if a.identity_check:
        print(identity_gate(identity_values()))
        return 0
    if a.run:
        return run(max_chunks=a.max_chunks)
    return analyze()


if __name__ == "__main__":
    sys.exit(main())
