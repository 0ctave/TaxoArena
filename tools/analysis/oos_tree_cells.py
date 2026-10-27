"""OOS-TREE-CELLS: on CLINC150 (oos_plus OOS pool) and the same qwen3 256-d S0 vectors, do INTENT-TRANSFER-S1's anchor-free tree
cells (C-AF, 139 leaves) detect out-of-scope queries as well as flat spherical k-means at matched k (within 0.010 AUROC), with
OOS-BASELINES' detectors beside? Zero calls; no build; CPU readout.

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-10-03 (before any code or call) — OOS-TREE-CELLS: on CLINC150
(oos_plus OOS pool) and the same qwen3 256-d S0 vectors, ..." span L23875-L23886 _as_of d50c47d4 (the registrar's commit, parent
2cb20cca). Record docs/agents/results/OOS-TREE-CELLS.json. --run REFUSES unless a LINE of the programme starts with that heading
(REG_RE, line-anchored). Kind: zero-call CPU reader: zero judge calls, zero embeddings, no build, no Ollama, no pool of record
(pool_guard not engaged), no embeddings_cache*.db.

INSTRUMENT (imported unchanged, blobs asserted at every entry point; another blob REFUSES):
  tools/analysis/oos_baselines.py      blob:7e74108dedcb2d921be0da4cf8ddc842deb24d72 (LF): load_inputs (S0's pins, meta, the CLINC rows,
      the qwen3 256-d Space), rows (TRAIN / GATE / EVAL in-scope / every kept OOS row), census, census_line, maxcos, threshold,
      fpr_line, s0_scores (S0's K-150 no-match, seeds 0-4), baseline_scores ((a)-(d)), ob_status (the registered EQUIVALENT /
      DIFFERENT / NEITHER rule), verdict_line, brier, _hit, after_check, IDENTITY.
  tools/analysis/intent_transfer_s1.py blob:4e9d9d05fbdf14d0a85966b4c897cfbfd779186d (LF): arm_presence / snapshot_id_of (the run
      log's single "Snapshot ID:"), snapshot_row (snapshots.db row BY ID, read-only, a non-empty -wal refuses), tree_of (leaves = no
      childIds, sorted by id; vmfMu; sliceDim), load_tree_checked (dag_snapshots leaf set = graph's; the run manifest's intent_build
      = the re-derived build; the embedding source sha = the qwen3 pin), derive_inputs, check_code_pins.
  Through them intent_transfer_s0.py (f662ceb1): km_fit (spherical k-means, k-means++, n_init 1, max_iter 300, TRAIN through
  fit_rows), fit_rows (the TRAIN-ONLY guard), auroc, comp_weights, pct_ci, basic_ci, kish, Space, unit.

ARMS (higher = more in-scope; A = auroc(in-scope EVAL, OOS)):
  T     DECIDING. max-cos to C-AF's leaf vmfMu at the leaf slice (flatLeaf; slice 256 asserted = S0's Space); C-AF read from S1's
        snapshot 20261002_213715_Headless_Run_Auto_ge (the run log's Snapshot ID; another id REFUSES), L = 139 leaves asserted.
  K_s   max-cos to spherical k-means at k = L (read from the tree, = 139) on CLINC TRAIN in-scope, seeds 0-4 (ITS.km_fit).
  DESCRIPTIVE beside: C-AN's leaves (snapshot 20261002_214129_Headless_Run_Auto_ge, anchored, at ITS slice: 512 from S0's 512-d
  read); S0's K-150 no-match seeds 0-4 (OB.s0_scores); OOS-BASELINES' (a)-(d) (OB.baseline_scores); FPR95 of every score at its own
  GATE threshold (OB.fpr_line: the floor(0.05 n)-th smallest GATE in-scope score).

CRITERION OT1 (registered; ob_status of oos_baselines.py, the words mapped BASELINE-BETTER -> TREE-BETTER, S0-BETTER -> KMEANS-BETTER):
  Delta_T = A(T) - mean_{s=0..4} A(K_s). SE_total = sqrt(SE_boot^2 + var_seed / 5); SE_boot = SD (ddof 1) over B 2,000 paired
  draws of (A_w(T) - mean_s A_w(K_s)) under OOS-BASELINES' stratified component bootstrap (in-scope and OOS components resampled
  separately; one weight pair per draw for every score); var_seed = sample variance (ddof 1) of A(K_s) over s.
  EQUIVALENT iff Delta_T +/- 1.645 SE_total lies inside (-0.010, +0.010) (the INTERVAL decides); DIFFERENT iff |Delta_T| > 0.010
  AND Delta_T +/- 1.96 SE_total excludes 0 (TREE-BETTER if Delta_T > 0, KMEANS-BETTER if < 0); NEITHER otherwise. The two verdicts
  cannot co-fire (EQUIVALENT needs |Delta_T| < 0.010, DIFFERENT needs |Delta_T| > 0.010).
  F-OT fires iff OT1 reads KMEANS-BETTER. PREDICTIONS P1 Delta_T -0.002 [-0.008, +0.004]; OT1 EQUIVALENT 0.80, NEITHER 0.18,
  DIFFERENT 0.02; P2 A(C-AN) 0.965 [0.950, 0.975] (descriptive).

BUILDER'S READINGS (printed in the outcome; the registrar confirms or brackets):
  OT-R1 the bootstrap stream is OOS-BASELINES' (S0 C2's, BOOT_SEED + 2), consumed in its order (zip of the in-scope and OOS
        generators); "OOS-BASELINES' form" read as its paired_boot.
  OT-R2 IDENTITY PRECONDITION (refuse; nothing written): A(T) and A(K_0) reproduce S1's T-C6 (0.96776 / 0.96999, "%.5f", SEEN before
        the registration), and the descriptive S0 K-150 per-seed A and A(a) reproduce OOS-BASELINES' registered identity digits
        (0.97437 / 0.97263 / 0.97601 / 0.97446 / 0.97649; 0.97640). They are checked before K_1..K_4 and before any descriptive line.
  OT-R3 the verdict line (Support (f)) is re-stated at the measured SE_total against the seen point -0.0022 (OB.verdict_line:
        SCOREABLE (EQUIVALENT side) iff |P| <= 0.010 - 2.487 SE_total; DIFFERENT side iff |P| >= 0.010 + 0.842 SE_total).
  OT-R4 numeric predictions HELD iff the point lies in the closed interval; each probability is scored by its own Brier (event 1 /
        0), DIFFERENT = TREE-BETTER or KMEANS-BETTER; the per-prediction sum beside.
  OT-R5 C-AN is scored at its own snapshot slice (512: "anchored-512" recipe); C-AF's slice must be 256 (REFUSE otherwise).

HYGIENE: reads intent_transfer_corpora_v1.db and intent_emb_qwen3.db through S0's / OB's readers (pins sha256-bytes, checked before
and after; a change REFUSES and nothing is written), snapshots.db rows by Snapshot ID and the two run dirs (read-only; non-empty -wal
REFUSES). No fit reads EVAL or OOS (fit_rows audit printed); thresholds read GATE in-scope only. Threads OMP / OPENBLAS / MKL = 1
before numpy. --dry-run and --run REFUSE while a java.exe runs (snapshots.db is written by a construction).

OUTPUT (experiment_results/oos_tree_cells/, write-once, mode "x"; an existing path REFUSES before any read): outcome.txt (of record),
oos_tree_scores.csv (item id, role, every score; never text). Outputs are never committed (sha256 + backup).

LAUNCH (run-operator; zero calls; nothing heavy running; CPU lane; data root = the S1 build worktree, e.g.
  TAXOARENA_DATA_ROOT=.claude/worktrees/intent-s1-run, or --data-root):
  python tools/analysis/oos_tree_cells.py --selftest
  python tools/analysis/oos_tree_cells.py --mutants
  python tools/analysis/oos_tree_cells.py --dry-run --data-root <S1 worktree>   # pins, denominators, trees, T-C6 identity; writes nothing
  python tools/analysis/oos_tree_cells.py --run --data-root <S1 worktree>       # the file of record (write-once)

MUTANT TABLE: `--mutants` (each mutant names the selftest sections that must kill it) and the commit message.
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy: the CPU lane is single-threaded
    os.environ[_v] = "1"

import argparse        # noqa: E402
import contextlib      # noqa: E402
import csv             # noqa: E402
import hashlib         # noqa: E402
import io              # noqa: E402
import json            # noqa: E402
import re              # noqa: E402
import shutil          # noqa: E402
import sqlite3         # noqa: E402
import sys             # noqa: E402
import tempfile; import scratch_dir        # noqa: E402
import time            # noqa: E402

import numpy as np     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import oos_baselines as OB            # noqa: E402  (imported unchanged; blob asserted)
import intent_transfer_s1 as S1       # noqa: E402  (imported unchanged; blob asserted)
import split_side as SS               # noqa: E402
from data_v2 import ro as RO          # noqa: E402
ITS = OB.ITS
II = OB.II

TAG = "[OOS-TREE-CELLS]"
OB_BLOB = "7e74108dedcb2d921be0da4cf8ddc842deb24d72"
S1_BLOB = "4e9d9d05fbdf14d0a85966b4c897cfbfd779186d"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
D = 256                                    # S0's slice; C-AF's slice asserted equal
K_SEEDS = (0, 1, 2, 3, 4)
BOOT_B = 2000
STREAM = ITS.BOOT_SEED + 2                 # OT-R1: OOS-BASELINES' (S0 C2's) stream
MARGIN = 0.010
Z90, Z95, Z80P = 1.645, 1.96, 0.842
TREE, ANCH = "C-AF", "C-AN"
SIDS = {"C-AF": "20261002_213715_Headless_Run_Auto_ge", "C-AN": "20261002_214129_Headless_Run_Auto_ge"}
L_REG = 139
SEEN = {"tree": "0.96776", "km_seed0": "0.96999"}          # S1 T-C6 (seen before the registration)
OB_ID = {"per_seed": OB.IDENTITY["per_seed"], "A_a": OB.IDENTITY["A_a"]}
SEEN_POINT = -0.0022
SE_TRANSPORT = 0.0012
S0_MEAN_REG = 0.97479
PLAN = {"n_in": 6672, "n_oos": 1350}
P1 = (-0.002, -0.008, 0.004)
P_STAT = {"EQUIVALENT": 0.80, "NEITHER": 0.18, "DIFFERENT": 0.02}
P2 = (0.965, 0.950, 0.975)
WORD = {"EQUIVALENT": "EQUIVALENT", "NEITHER": "NEITHER", "BASELINE-BETTER": "TREE-BETTER", "S0-BETTER": "KMEANS-BETTER"}
DESC = ("a", "b", "c", "d")
OUT_DIR = os.path.join(ROOT, "experiment_results", "oos_tree_cells")
OUTCOME = "outcome.txt"
SCORES_CSV = "oos_tree_scores.csv"
PROGRAMME = os.path.join(ROOT, "docs", "judge_v2_program.md")
REG_HEADING = "## Registered 2026-10-03 (before any code or call) \u2014 OOS-TREE-CELLS:"
REG_RE = re.compile(r"^" + re.escape(REG_HEADING), re.M)
REG = ("docs/judge_v2_program.md \"## Registered 2026-10-03 (before any code or call) \u2014 OOS-TREE-CELLS: on CLINC150 (oos_plus OOS "
       "pool) and the same qwen3 256-d S0 vectors, ...\" L23875-L23886 _as_of d50c47d4 (registrar, parent 2cb20cca); kind zero-call")
LIKE = ("LIKE WITH LIKE (registered): T (C-AF tree cells, DECIDING; anchor-free construction; reads no label, TRAIN in-scope "
        "membership only) vs K (flat spherical k-means at k = L; reads no label; k matched to T); C-AN cells DESCRIPTIVE (anchored on "
        "the gold coarse labels); OOS-BASELINES (a), (b) read the 150 class labels. The deciding contrast is label-free vs label-free "
        "at matched cell count.")
SPLIT_NOTE = OB.SPLIT_NOTE
READINGS = ("builder's readings: OT-R1 OOS-BASELINES' paired bootstrap stream (BOOT_SEED + 2, its order); OT-R2 identity "
            "precondition: A(T) / A(K_0) = S1 T-C6 0.96776 / 0.96999 and S0 K-150 per seed / A(a) = OOS-BASELINES' digits; OT-R3 verdict "
            "line at the measured SE_total against the seen -0.0022; OT-R4 numeric HELD on the closed interval, one Brier per "
            "probability, DIFFERENT = TREE-BETTER or KMEANS-BETTER; OT-R5 C-AN at its own slice (512), C-AF at 256 (asserted)")
DOES_NOT_SHOW = ("WHAT THIS RESULT WILL NOT SHOW (registered): OOS on real traffic, other corpora or embedders; MMLU-Pro or capability "
                 "text; anchored cells as label-free (C-AN descriptive); parity outside +/-0.010; comparability with published CLINC "
                 "numbers.")
EVENTS = []


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def check_blobs():
    got = {"oos_baselines.py": RO.git_blob_lf(OB.__file__), "intent_transfer_s1.py": RO.git_blob_lf(S1.__file__)}
    want = {"oos_baselines.py": OB_BLOB, "intent_transfer_s1.py": S1_BLOB}
    for k in want:
        if got[k] != want[k]:
            refuse("%s is blob %s, not the registered %s: the instrument is imported unchanged" % (k, got[k], want[k]))
    OB.check_its_blob()
    S1.check_code_pins()
    return got


_foreign_heavy = ITS._foreign_heavy


def heavy_check():
    heavy = _foreign_heavy()
    print("%s heavy foreign processes: %s" % (TAG, heavy if heavy else "none"))
    if heavy:
        refuse("a foreign heavy process runs (%s): never beside a construction (snapshots.db is written by one)" % heavy[:3])


def check_registered(programme):
    ok = os.path.isfile(programme) and bool(REG_RE.search(open(programme, encoding="utf-8").read()))
    print("%s registration heading (line-anchored) in %s: %s" % (TAG, os.path.basename(programme), "PRESENT" if ok else "ABSENT"))
    return ok


def paths(data_root):
    return os.path.join(data_root, II.DB_NAME), data_root, os.path.join(data_root, "snapshots.db")


# ------------------------------------------------------------------------------------------------ trees
def graph_sha(graph):
    return hashlib.sha256(json.dumps(graph, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_trees(data_root, snap_db, db, emb_sha, sids=None):
    """C-AF and C-AN by the run log's Snapshot ID (S1's readers, unchanged). REFUSES a different id, L != 139, C-AF slice != 256."""
    sids = SIDS if sids is None else sids
    pres = S1.arm_presence(snap_db, data_root)
    D_ex = S1.derive_inputs(db)
    out = {}
    for name in (TREE, ANCH):
        p = pres[name]
        if not p["present"]:
            refuse("%s build ABSENT (%s)" % (name, p["why"]))
        if p["sid"] != sids[name]:
            refuse("%s: the run log's Snapshot ID %s != the registered %s" % (name, p["sid"], sids[name]))
        T, g = S1.load_tree_checked(name, p, snap_db, D_ex, {"qwen3": emb_sha})
        out[name] = {"T": T, "sid": p["sid"], "graph_sha": graph_sha(g), "L": len(T["leaves"]), "d": T["d"]}
    if out[TREE]["L"] != L_REG:
        refuse("C-AF has %d leaves, not the registered L = %d" % (out[TREE]["L"], L_REG))
    if out[TREE]["d"] != D:
        refuse("C-AF's slice is %d, not S0's %d (the registration reads the same qwen3 256-d vectors)" % (out[TREE]["d"], D))
    if out[ANCH]["d"] not in (D, ITS.SLICE2):
        refuse("C-AN's slice %d is neither 256 nor S0's 512-d read" % out[ANCH]["d"])
    return out


def tree_line(tr):
    return "TREES: " + "; ".join("%s snapshot %s (run log Snapshot ID), %d leaves, slice %d, graph sha256 %s" % (
        n, tr[n]["sid"], tr[n]["L"], tr[n]["d"], tr[n]["graph_sha"][:16]) for n in (TREE, ANCH))


def space_for(S, d, C):
    """S0's Space at slice d: the 256-d Space itself, else ITS.Space over the same 512-d S0 read (OT-R5)."""
    if d == D:
        return S
    return ITS.Space(S.vecs, C, d)


def leaf_scores(T, Sd, R):
    return {k: OB.maxcos(T["leaf_mu"], Sd.X[R[k]]) for k in ("in", "oos", "gate")}


def km_scores(C, S, R, L, seeds):
    out = {}
    for s in seeds:
        Cm = ITS.km_fit(C, S, L, s, "OTC k-means k=L=%d s%d" % (L, s))
        out["k%d" % s] = {k: OB.maxcos(Cm, S.X[R[k]]) for k in ("in", "oos", "gate")}
    return out


def A_of(sc):
    return ITS.auroc(sc["in"], sc["oos"])


# ------------------------------------------------------------------------------------------------ identity
def identity_check(got, target):
    bad = [k for k in ("tree", "km_seed0") if got[k] != target[k]]
    line = "IDENTITY (S1 T-C6): A(T) %s (seen %s), A(K_0) %s (seen %s)" % (got["tree"], target["tree"], got["km_seed0"], target["km_seed0"])
    if "per_seed" in target:
        if tuple(got["per_seed"]) != tuple(target["per_seed"]):
            bad.append("per_seed")
        if got["A_a"] != target["A_a"]:
            bad.append("A_a")
        line += "; OOS-BASELINES S0 K-150 per seed %s (registered %s), A(a) %s (registered %s)" % (
            " / ".join(got["per_seed"]), " / ".join(target["per_seed"]), got["A_a"], target["A_a"])
    print("%s %s" % (TAG, line))
    if bad:
        refuse("IDENTITY PRECONDITION FAILED on %s: the inputs do not reproduce the numbers of record; no readout is written" % bad)
    return line + " -> REPRODUCED"


# ------------------------------------------------------------------------------------------------ statistics
def ot_status(Dl, se):
    return WORD[OB.ob_status(Dl, se)]


def paired_boot(C, R, sc, names, B=None):
    """B paired draws: one (in-scope, OOS) weight pair per draw for every score (OOS-BASELINES' stream and order, OT-R1)."""
    B = BOOT_B if B is None else B
    rng = np.random.default_rng(STREAM)
    draws = {k: [] for k in names}
    for wi, wo in zip(ITS.comp_weights(C.comp[R["in"]], B, rng), ITS.comp_weights(C.comp[R["oos"]], B, rng)):
        for k in names:
            draws[k].append(ITS.auroc(sc[k]["in"], sc[k]["oos"], wi, wo))
    return {k: np.asarray(v) for k, v in draws.items()}


def readout(sc, draws):
    A_K = np.array([A_of(sc["k%d" % s]) for s in K_SEEDS])
    mean_K = float(A_K.mean())
    var_seed = float(np.var(A_K, ddof=1))
    A_T = A_of(sc["T"])
    Dl = A_T - mean_K
    k_draw_mean = np.mean(np.vstack([draws["k%d" % s] for s in K_SEEDS]), axis=0)
    dd = draws["T"] - k_draw_mean
    se_boot = float(np.std(dd, ddof=1))
    se = float(np.sqrt(se_boot ** 2 + var_seed / len(K_SEEDS)))
    plo, phi = ITS.pct_ci(dd)
    blo, bhi = ITS.basic_ci(Dl, dd)
    return {"A_T": A_T, "A_K": A_K, "mean_K": mean_K, "var_seed": var_seed, "D": Dl, "se_boot": se_boot, "se": se,
            "lo90": Dl - Z90 * se, "hi90": Dl + Z90 * se, "lo95": Dl - Z95 * se, "hi95": Dl + Z95 * se, "plo": plo, "phi": phi,
            "blo": blo, "bhi": bhi, "status": ot_status(Dl, se), "D_seed0": A_T - float(A_K[0]),
            "A_T_ci": ITS.pct_ci(draws["T"])}


def falsifier(status):
    return bool(status == "KMEANS-BETTER")


# ------------------------------------------------------------------------------------------------ lines
def support_lines(cn, RD):
    deff = max(cn["in_kish"], cn["oos_kish"])
    eq, df, w = OB.verdict_line(SEEN_POINT, RD["se"])
    eq_p, df_p, _w = OB.verdict_line(SEEN_POINT, SE_TRANSPORT)
    return ["== SUPPORT (measured; registered planning values beside) ==",
            "  denominators: n_in %d CLINC in-scope EVAL rows in %d components (Kish %.4f); n_OOS %d oos_plus OOS rows in %d components "
            "(Kish %.4f); DEFF %.4f (measured from the components, the max of the two strata); n_eff %.0f in-scope / %.0f OOS "
            "(registered 6,672 / 1,350, Kish 1.0000, DEFF 1.0)" % (cn["in"], cn["in_components"], cn["in_kish"], cn["oos"],
                                                                     cn["oos_components"], cn["oos_kish"], deff, cn["in"] / cn["in_kish"],
                                                                     cn["oos"] / cn["oos_kish"]),
            "  OT1: SE_boot %.5f, seed term sqrt(var_seed / 5) %.5f, SE_total %.5f (transported 0.0012 from OB-c); 90%% half-width %.5f; "
            "MDE80 (2.8 x SE_total) %.5f; EQUIVALENT reach |Delta_true| <= %.5f (registered %.4f), DIFFERENT reach >= %.5f (registered "
            "%.4f); verdict line at the seen point %+.4f: %s" % (RD["se_boot"], np.sqrt(RD["var_seed"] / 5), RD["se"], Z90 * RD["se"],
                                                                2.8 * RD["se"], eq, eq_p, df, df_p, SEEN_POINT, w)]


def readout_lines(RD, tr, L):
    return ["== READOUTS (A = AUROC in-scope EVAL vs OOS; Delta_T = A(T) - mean_s A(K_s); paired stratified component bootstrap, B %d) ==" % BOOT_B,
            "  T (C-AF tree cells, %d leaves, flatLeaf max-cos to vmfMu, slice %d): A %.5f [pct %.5f, %.5f]" % (tr[TREE]["L"], tr[TREE]["d"], RD["A_T"],
                                                                                                        RD["A_T_ci"][0], RD["A_T_ci"][1]),
            "  K (spherical k-means k = L = %d, TRAIN in-scope, seeds 0-4): A %s; mean %.5f; var_seed %.3e" % (
                L, " / ".join("%.5f" % a for a in RD["A_K"]), RD["mean_K"], RD["var_seed"]),
            "  Delta_T %+.5f; SE_boot %.5f; SE_total %.5f; 90%% [%+.5f, %+.5f]; 95%% [%+.5f, %+.5f]" % (
                RD["D"], RD["se_boot"], RD["se"], RD["lo90"], RD["hi90"], RD["lo95"], RD["hi95"])]


def criteria_lines(RD):
    st = RD["status"]
    L = ["== CRITERION OT1 (EQUIVALENT iff Delta_T +/- 1.645 SE_total inside (-%.3f, +%.3f); DIFFERENT iff |Delta_T| > %.3f AND Delta_T "
         "+/- 1.96 SE_total excludes 0; NEITHER otherwise) ==" % (MARGIN, MARGIN, MARGIN),
         "OT1: %s (Delta_T %+.5f, 90%% [%+.5f, %+.5f], 95%% [%+.5f, %+.5f], SE_total %.5f; C-AF tree cells vs k-means at k = L)" % (
             st, RD["D"], RD["lo90"], RD["hi90"], RD["lo95"], RD["hi95"], RD["se"])]
    if st == "EQUIVALENT":
        L.append("  EQUIVALENT: OOS-BASELINES' abstention sentence extends to the anchor-free tree's cells: label-free C-AF tree cells "
                 "detect out-of-scope queries within 0.010 AUROC of flat k-means at matched k (CLINC oos_plus, qwen3 256, one draw)")
    elif st == "TREE-BETTER":
        L.append("  TREE-BETTER: the C-AF tree cells exceed flat k-means at matched k by %+.5f AUROC (95%% interval excludes 0; CLINC "
                 "oos_plus, qwen3 256, one draw); no parity word is written" % RD["D"])
    elif st == "KMEANS-BETTER":
        L.append("  KMEANS-BETTER: flat k-means at matched k exceeds the C-AF tree cells by %+.5f AUROC (95%% interval excludes 0)" % (-RD["D"]))
    else:
        L.append("  NEITHER: neither parity within 0.010 nor a separable gap (Delta_T %+.5f); no sentence beyond the numbers" % RD["D"])
    if falsifier(st):
        L.append("F-OT: FIRED (OT1 KMEANS-BETTER): abstention by label-free cells is a flat-partition property, not available from the "
                 "tree's cells; \"abstention on flat cells only\" stays the wording")
    else:
        L.append("F-OT: NOT FIRED (OT1 reads %s, not KMEANS-BETTER)" % st)
    return L


def descriptive_lines(RD, desc, fl, tr):
    L = ["== DESCRIPTIVE (never scored) =="]
    an = desc["AN"]
    L.append("  C-AN (anchored on gold coarse labels, %d leaves, slice %d): A %.5f [pct %.5f, %.5f]; A(C-AN) - A(T) %+.5f" % (
        tr[ANCH]["L"], tr[ANCH]["d"], an["A"], an["ci"][0], an["ci"][1], an["A"] - RD["A_T"]))
    s0 = desc["S0"]
    L.append("  S0 K-150 no-match seeds 0-4: A %s, mean %.5f (registered 0.97479); A(T) - mean %+.5f [pct %+.5f, %+.5f]" % (
        " / ".join("%.5f" % a for a in s0["A"]), s0["mean"], RD["A_T"] - s0["mean"], s0["ci"][0], s0["ci"][1]))
    for b in DESC:
        r = desc[b]
        L.append("  OOS-BASELINES (%s) %s: A %.5f; A(T) - A(%s) %+.5f [pct %+.5f, %+.5f]" % (b, OB.DET_NAME[b], r["A"], b, RD["A_T"] - r["A"],
                                                                                         r["ci"][0], r["ci"][1]))
    for k, lab in (("T", "T (C-AF)"), ("k0", "K_0"), ("AN", "C-AN"), ("s0", "S0 K-150 s0")) + tuple((b, "(%s)" % b) for b in DESC):
        f = fl[k]
        L.append("  FPR95 %s: %.4f at its own GATE threshold %.5f (GATE TPR %.4f; EVAL TPR %.4f)" % (lab, f["fpr95"], f["thr"], f["tpr_gate"], f["tpr_eval"]))
    L.append("  OT1 BASIC 95%% [%+.5f, %+.5f]; percentile 95%% [%+.5f, %+.5f]; Delta vs K seed 0 %+.5f (T-C6's single-seed reading)" % (
        RD["blo"], RD["bhi"], RD["plo"], RD["phi"], RD["D_seed0"]))
    return L


def predictions_lines(RD, A_an):
    st = RD["status"]
    v = RD["D"]
    L = ["== PREDICTIONS (registered; numeric HELD iff the point lies in the closed interval; probabilities by Brier) =="]
    L.append("  P1 Delta_T %+.5f vs %+.3f [%+.3f, %+.3f]: %s" % (v, P1[0], P1[1], P1[2], "HELD" if OB._hit(v, P1[1], P1[2]) else "FAILED"))
    evt = {"EQUIVALENT": st == "EQUIVALENT", "NEITHER": st == "NEITHER", "DIFFERENT": st in ("TREE-BETTER", "KMEANS-BETTER")}
    br = {k: OB.brier(p, evt[k]) for k, p in P_STAT.items()}
    L.append("  P1 OT1 %s: Brier %s (sum %.4f)" % (st, ", ".join("%s %.4f" % kv for kv in br.items()), sum(br.values())))
    L.append("  P2 A(C-AN) %.5f vs %.3f [%.3f, %.3f]: %s (DESCRIPTIVE)" % (A_an, P2[0], P2[1], P2[2], "HELD" if OB._hit(A_an, P2[1], P2[2]) else "FAILED"))
    return L


def header_lines(blobs, pins_state, cn, tr, idline):
    return ["OOS-TREE-CELLS outcome (tools/analysis/oos_tree_cells.py, blob %s; imports oos_baselines.py blob %s and intent_transfer_s1.py "
            "blob %s unchanged)" % (blobs["self"], OB_BLOB, S1_BLOB),
            "registration: " + REG, "pool of record: none read (S0's DBs, snapshots.db rows by id); zero judge calls; no construction; no Ollama",
            LIKE, SPLIT_NOTE, pins_state, OB.census_line(cn), tree_line(tr), idline, READINGS]


# ------------------------------------------------------------------------------------------------ run
def out_paths(out_dir):
    return os.path.join(out_dir, OUTCOME), os.path.join(out_dir, SCORES_CSV)


def compute(C, S, trees, identity, B=None):
    """T and K_0 first, the identity (refuses before K_1..K_4 and any descriptive score), then K_1..K_4, the descriptive arms, the
    paired bootstrap and the readout."""
    del ITS.FIT_LOG[:]
    del EVENTS[:]
    R = OB.rows(C, S)
    if int(C.oos[R["train"]].sum()) or int(C.oos[R["gate"]].sum()):
        refuse("an OOS row sits in the TRAIN / GATE index sets")
    L = trees[TREE]["L"]
    ITS.fit_rows(C, R["gate"], (SS.GATE,), "OTC thresholds (GATE in-scope, every score)")
    sc = {"T": leaf_scores(trees[TREE]["T"], space_for(S, trees[TREE]["d"], C), R)}
    sc.update(km_scores(C, S, R, L, K_SEEDS[:1]))
    s0 = OB.s0_scores(C, S, R)
    tr_a = ITS.fit_rows(C, R["train"], (SS.TRAIN,), "OTC identity (a)")
    _u, G = ITS.centroids_by_label(S.X[tr_a], C.fine[tr_a])
    got = {"tree": "%.5f" % A_of(sc["T"]), "km_seed0": "%.5f" % A_of(sc["k0"]),
           "per_seed": tuple("%.5f" % A_of(s0["s%d" % s]) for s in OB.S0_SEEDS),
           "A_a": "%.5f" % ITS.auroc(OB.maxcos(G, S.X[R["in"]]), OB.maxcos(G, S.X[R["oos"]]))}
    idline = identity_check(got, identity)
    EVENTS.append(("IDENTITY", "ok"))
    sc.update(km_scores(C, S, R, L, K_SEEDS[1:]))
    EVENTS.append(("K", "fitted"))
    sc["AN"] = leaf_scores(trees[ANCH]["T"], space_for(S, trees[ANCH]["d"], C), R)
    bs, meta = OB.baseline_scores(C, S, R)
    for s in OB.S0_SEEDS:
        sc["s%d" % s] = s0["s%d" % s]
    for b in DESC:
        sc[b] = bs[b]
    names = ["T"] + ["k%d" % s for s in K_SEEDS] + ["AN"] + ["s%d" % s for s in OB.S0_SEEDS] + list(DESC)
    draws = paired_boot(C, R, sc, names, B)
    RD = readout(sc, draws)
    s0A = np.array([A_of(sc["s%d" % s]) for s in OB.S0_SEEDS])
    s0m_draw = np.mean(np.vstack([draws["s%d" % s] for s in OB.S0_SEEDS]), axis=0)
    desc = {"AN": {"A": A_of(sc["AN"]), "ci": ITS.pct_ci(draws["AN"])},
            "S0": {"A": s0A, "mean": float(s0A.mean()), "ci": ITS.pct_ci(draws["T"] - s0m_draw)}}
    for b in DESC:
        desc[b] = {"A": A_of(sc[b]), "ci": ITS.pct_ci(draws["T"] - draws[b])}
    fl = {k: OB.fpr_line(sc[k]) for k in ("T", "k0", "AN", "s0") + DESC}
    return {"R": R, "sc": sc, "draws": draws, "RD": RD, "desc": desc, "fl": fl, "idline": idline, "meta": meta, "L": L, "names": names}


def main_run(data_root=None, out_dir=OUT_DIR, programme=PROGRAMME, identity=None, sids=None, B=None):
    check_blobs()
    data_root = data_root or DATA_ROOT
    db, emb_dir, snap_db = paths(data_root)
    for p in out_paths(out_dir):
        if os.path.lexists(p):
            refuse("%s exists: the outcome of record is write-once" % p)
    if not check_registered(programme):
        refuse("the registration heading is absent from %s: --run reads only a registered test" % programme)
    heavy_check()
    sha0, C, S = OB.load_inputs(db, emb_dir, strict=True)
    cn = OB.census(C, S)
    print("%s %s" % (TAG, OB.census_line(cn)))
    trees = load_trees(data_root, snap_db, db, sha0["qwen3"], sids)
    print("%s %s" % (TAG, tree_line(trees)))
    X = compute(C, S, trees, dict(SEEN, **OB_ID) if identity is None else identity, B)
    pins_state = OB.after_check(sha0, db, emb_dir)
    blobs = {"self": RO.git_blob_lf(os.path.abspath(__file__))}
    L = header_lines(blobs, pins_state, cn, trees, X["idline"])
    L += support_lines(cn, X["RD"])
    L.append(ITS.fit_audit())
    L += readout_lines(X["RD"], trees, X["L"])
    L += criteria_lines(X["RD"])
    L += descriptive_lines(X["RD"], X["desc"], X["fl"], trees)
    L += predictions_lines(X["RD"], X["desc"]["AN"]["A"])
    L.append(DOES_NOT_SHOW)
    for ln in L:
        print(ln)
    os.makedirs(out_dir, exist_ok=True)
    po, pc = out_paths(out_dir)
    with open(po, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    write_scores(pc, C, X)
    print("%s wrote %s and %s (write-once, of record)" % (TAG, po, pc))
    return X, L, po


def write_scores(path, C, X):
    cols = X["names"]
    with open(path, "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["item_id", "role"] + cols)
        for role, key in (("EVAL_IN", "in"), ("EVAL_OOS", "oos"), ("GATE_IN", "gate")):
            for j, i in enumerate(X["R"][key]):
                w.writerow([C.ids[i], role] + ["%.8f" % X["sc"][c][key][j] for c in cols])


def dry_run(data_root=None, programme=PROGRAMME, identity=None, sids=None, timing=True):
    """Pins, census / denominators against the registration, the two trees, the T-C6 identity (numbers of record only: A(T), A(K_0));
    no K_1..K_4, no Delta_T, no descriptive score; nothing written."""
    check_blobs()
    data_root = data_root or DATA_ROOT
    db, emb_dir, snap_db = paths(data_root)
    print("%s DRY RUN (zero calls; nothing written); script blob %s; OB blob %s; S1 blob %s; data root %s" % (
        TAG, RO.git_blob_lf(os.path.abspath(__file__)), OB_BLOB, S1_BLOB, data_root))
    print("%s pool of record: none read (pool_guard not engaged); %s" % (TAG, REG))
    check_registered(programme)
    heavy_check()
    sha0, C, S = OB.load_inputs(db, emb_dir, strict=False)
    cn = OB.census(C, S)
    print("%s %s" % (TAG, OB.census_line(cn)))
    print("%s DENOMINATORS vs registration: n_in %d (registered %d) %s; n_OOS %d (registered %d) %s; components %d / %d; Kish %.4f / %.4f "
          "(registered 1.0000 / 1.0000); bootstrap B %d paired, stream %d" % (
              TAG, cn["in"], PLAN["n_in"], "MATCH" if cn["in"] == PLAN["n_in"] else "DIFFERENT", cn["oos"], PLAN["n_oos"],
              "MATCH" if cn["oos"] == PLAN["n_oos"] else "DIFFERENT", cn["in_components"], cn["oos_components"], cn["in_kish"],
              cn["oos_kish"], BOOT_B, STREAM))
    trees = load_trees(data_root, snap_db, db, sha0["qwen3"], sids)
    print("%s %s" % (TAG, tree_line(trees)))
    del ITS.FIT_LOG[:]
    R = OB.rows(C, S)
    t0 = time.time()
    tsc = leaf_scores(trees[TREE]["T"], space_for(S, trees[TREE]["d"], C), R)
    k0 = km_scores(C, S, R, trees[TREE]["L"], K_SEEDS[:1])["k0"]
    t_k = time.time() - t0
    target = dict(SEEN) if identity is None else {k: identity[k] for k in ("tree", "km_seed0")}
    idline = identity_check({"tree": "%.5f" % A_of(tsc), "km_seed0": "%.5f" % A_of(k0)}, target)
    if timing:
        t1 = time.time()
        rng = np.random.default_rng(STREAM)
        n_t = 20
        for wi, wo in zip(ITS.comp_weights(C.comp[R["in"]], n_t, rng), ITS.comp_weights(C.comp[R["oos"]], n_t, rng)):
            for _k in range(16):
                ITS.auroc(tsc["in"], tsc["oos"], wi, wo)
        t_b = (time.time() - t1) / n_t * BOOT_B
        print("%s TIMING: tree scores + one k-means k=%d %.1f s (x 5 seeds + 5 x K-150 + (a)-(d) at --run); %d paired draws x 16 AUROCs "
              "priced %.1f s; total about %.1f min single-threaded" % (TAG, trees[TREE]["L"], t_k, BOOT_B, t_b, (11 * t_k + t_b) / 60.0 + 2))
    print("%s %s" % (TAG, OB.after_check(sha0, db, emb_dir)))
    print("%s %s" % (TAG, ITS.fit_audit()))
    print("%s %s" % (TAG, idline))
    print("%s DRY RUN complete: nothing written; no Delta_T, no K_1..K_4, no descriptive score" % TAG)
    return 0


# ------------------------------------------------------------------------------------------------ selftest fixtures
FX_MODES = ("EQ", "KB", "TB", "NE")
FX_K = 16
FX_B = 200
FX_SIDS = {"C-AF": "fx_caf_sid", "C-AN": "fx_can_sid"}


def _rng(*parts):
    return np.random.default_rng(int(hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12], 16))


def _plant(mode, f, t):
    """CLINC planting (first 64 dims of 4096; the rest 1e-4 noise). In-scope intent f: 3 E[f] + E[16 + f % 4] + noise.
    EQ: noise 0.3; OOS on orthogonal axes 40-47 -> every A = 1, Delta 0, SE 0 (EQUIVALENT).
    KB: noise 0.3; OOS = 3 E[40 + j] (j < 4) + E[f'] -> k-means separates; the tree carries 4 leaves ON the OOS axes (KMEANS-BETTER).
    TB: noise 0.6 on dims 0-23; OOS = an in-scope point + 1.2 E[48]: cos overlaps for k-means; the tree's leaves carry -0.8 E[48]
        (TREE-BETTER).
    NE: noise 0.6; OOS = an in-scope point + 0.5 noise on dims 48-63; tree leaves = class means + 0.3 noise (a small, noisy Delta).
    TB / NE OOS also carry 1.5 E[300] (beyond slice 256): C-AN at its 512 slice reads it, a 256 reading would not.
    TB's C-AF drops its last class leaf (L = 15 != S0's fixture K 16): k matched to L is discriminated from k = K."""
    r = _rng("otc", mode, t)
    v = np.zeros(4096)
    v[64:] = 1e-4 * r.normal(size=4032)
    sig = 0.6 if mode in ("TB", "NE") else 0.3
    if f is not None:
        v[f] += 3.0
        v[16 + f % 4] += 1.0
        v[:24] += sig * r.normal(size=24)
        return v
    if mode == "EQ":
        v[40 + int(r.integers(8))] += 3.0
        v[:64] += 0.3 * r.normal(size=64)
    elif mode == "KB":
        v[40 + int(r.integers(4))] += 3.0
        v[int(r.integers(FX_K))] += 1.0
        v[:24] += 0.3 * r.normal(size=24)
    else:
        ff = int(r.integers(FX_K))
        v[ff] += 3.0
        v[16 + ff % 4] += 1.0
        v[:24] += sig * r.normal(size=24)
        if mode == "TB":
            v[48] += 1.2
        else:
            v[48:64] += 0.5 * r.normal(size=16)
        v[300] += 1.5                      # seen at slice 512 only: C-AN (512) scores differ from a 256-slice reading
    return v


def _tree_graph(mus, qids, d, tag):
    """root -> 2 internal nodes -> leaves (vmfMu = mus rows); every leaf carries TRAIN queryIds."""
    nodes, leaf_ids = [], []
    half = (len(mus) + 1) // 2
    groups = [list(range(0, half)), list(range(half, len(mus)))]
    nid = [2]

    def new_id():
        i = "n%08d" % nid[0]
        nid[0] += 1
        return i
    kids = []
    for g in groups:
        cid = new_id()
        kids.append(cid)
        lids = []
        for j in g:
            lid = new_id()
            q = qids[j] or ["q_%s_%d" % (tag, j)]
            nodes.append({"id": lid, "childIds": [], "parentIds": [cid], "sliceDim": d, "vmfMu": [float(x) for x in mus[j]], "vmfKappa": 30.0,
                          "queryIds": q, "queryWeights": {x: 1.0 for x in q}})
            lids.append(lid)
            leaf_ids.append(lid)
        nodes.append({"id": cid, "childIds": lids, "parentIds": ["n00000001"], "sliceDim": d,
                      "vmfMu": [float(x) for x in ITS.unit(np.mean(mus[g], 0)[None, :])[0]], "vmfKappa": 15.0, "queryIds": [], "queryWeights": {}})
    nodes.append({"id": "n00000001", "childIds": kids, "parentIds": [], "sliceDim": d, "vmfMu": [float(x) for x in ITS.unit(mus.mean(0)[None, :])[0]],
                  "vmfKappa": 5.0, "queryIds": [], "queryWeights": {}})
    settings = {"membershipFloor": 0.25, "routingBeamGamma": 0.2, "descentMargin": 0.12, "maxLeafAssignments": 5, "dagMode": "DAG_MAX"}
    return {"rootId": "n00000001", "nodes": nodes}, settings, leaf_ids


def _fixture_mus(mode, C, V, d, anchored):
    """Leaf directions at slice d from the TRAIN in-scope class means (the planted answer per mode)."""
    tr = [i for i in range(len(C.text)) if C.kept[i] and not C.oos[i] and C.side[i] == SS.TRAIN]
    lab = np.array([C.fine[i] for i in tr], dtype=str)
    X = ITS.unit(np.array([V[C.text[i]][:d] for i in tr]))
    ul = sorted(set(lab.tolist()))
    M = np.array([X[lab == u].mean(0) for u in ul])
    qids = [["q_%s" % hashlib.sha256(C.text[tr[k]].encode()).hexdigest()[:16] for k in np.nonzero(lab == u)[0]] for u in ul]
    if anchored:
        return ITS.unit(M), qids
    r = _rng("mus", mode)
    if mode == "KB":
        for j in range(4):
            M[j] = 0.0
            M[j, 40 + j] = 1.0
    elif mode == "TB":
        M[:, 48] -= 0.8
    elif mode == "NE":
        M[:, :64] += 0.3 * r.normal(size=(len(M), 64)) / np.sqrt(64) * np.linalg.norm(M, axis=1, keepdims=True).mean() * 3
    return ITS.unit(M), qids


def build_fixture(td, mode, can_d=512, caf_d=D, caf_drop=0):
    rows = ITS._fixture_rows()
    db = os.path.join(td, II.DB_NAME)
    with contextlib.redirect_stdout(io.StringIO()):
        II.write_db(db, rows, [("fixture", "none", "none", "0" * 64, 0, "1970-01-01T00:00:00Z")])
    CS = ITS.load_corpora(db)
    texts, set_sha, _d = ITS.text_set(CS)
    C = CS[OB.CORPUS]
    V = {}
    for i in np.nonzero(C.kept)[0]:
        V[C.text[i]] = _plant(mode, None if C.oos[i] else int(C.fine[i][-2:]), C.text[i])
    p = ITS.emb_path("qwen3", td)
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.executemany("INSERT INTO intent_meta VALUES (?, ?)", sorted(dict(ITS.expected_meta("qwen3", set_sha, len(texts), II.file_sha(db)),
                                                                          model_digest="stub").items()))
    con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, np.asarray(v, dtype=">f4").tobytes()) for t, v in sorted(V.items())])
    con.commit()
    con.close()
    emb_sha = II.file_sha(p)
    pins = os.path.join(td, "pins.json")
    con = II.open_db_ro(db)
    rawp = {n: s for n, s in con.execute("SELECT name, sha256 FROM provenance")}
    con.close()
    with open(pins, "w") as fh:
        json.dump({"schema": II.PINS_SCHEMA, "raw": rawp, "ingest_db": II.file_sha(db), "emb": {"qwen3": emb_sha}}, fh)
    prog = os.path.join(td, "programme.md")
    with open(prog, "w", encoding="utf-8") as fh:
        fh.write("intro\n%s fixture\n" % REG_HEADING)
    # the two builds: snapshots.db rows + run dirs (S1's layout)
    Vf = {t: np.asarray(v, dtype=">f4").astype(np.float64) for t, v in V.items()}
    D_ex = S1.derive_inputs(db)
    d1 = D_ex[("clinc", 1)]
    sdb = os.path.join(td, "snapshots.db")
    con = sqlite3.connect(sdb)
    con.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, timestamp TEXT, description TEXT, graph TEXT, metrics TEXT, settings TEXT)")
    graphs = {}
    for name, d, anch in ((TREE, caf_d, False), (ANCH, can_d, True)):
        mus, qids = _fixture_mus(mode, C, Vf, d, anch)
        if name == TREE and caf_drop:
            mus, qids = mus[:-caf_drop], qids[:-caf_drop]
        g, s, leaf_ids = _tree_graph(mus, qids, d, name)
        graphs[name] = g
        sid = FX_SIDS[name]
        con.execute("INSERT INTO snapshots VALUES (?, '2026-10-02', 'fx', ?, '{}', ?)", (sid, json.dumps(g), json.dumps(s)))
        con.execute("INSERT INTO snapshots VALUES (?, '2026-10-09', 'fx later', ?, '{}', ?)", (sid + "_later", json.dumps({"rootId": "x", "nodes": []}), json.dumps(s)))
        rd = S1.run_dir(S1.ARMS[name]["slug"], td)
        os.makedirs(os.path.join(rd, "diagnostics"))
        os.makedirs(os.path.join(rd, "validation"))
        open(os.path.join(rd, "headless_run.log"), "w").write("x Snapshot ID: %s\n" % sid)
        open(os.path.join(rd, "validation", "MAIN_routing_diagnostics.txt"), "w").write("fixture\n")
        with open(os.path.join(rd, "dag_snapshots.jsonl"), "w") as fh:
            fh.write(json.dumps({"nodes": [{"id": n["id"], "isLeaf": not n["childIds"]} for n in g["nodes"]]}) + "\n")
        man = {"intent_build": {"arm": name, "n_train": sum(1 for r in d1["rows"] if r["side"] == SS.TRAIN),
                                "n_gate": sum(1 for r in d1["rows"] if r["side"] == SS.GATE)}, "embedding_cache_source_sha256": emb_sha}
        json.dump(man, open(os.path.join(rd, "diagnostics", "run_manifest.json"), "w"))
    con.commit()
    con.close()
    fx = {"td": td, "db": db, "pins": pins, "prog": prog, "mode": mode, "graphs": graphs}
    fx["oracle"] = _oracle(fx)
    o = fx["oracle"]
    fx["L_REG"] = o["L"]
    fx["identity"] = {"tree": "%.5f" % o["A"]["T"], "km_seed0": "%.5f" % o["A"]["k0"],
                      "per_seed": tuple("%.5f" % o["A"]["s%d" % s] for s in OB.S0_SEEDS), "A_a": "%.5f" % o["A"]["a"]}
    return fx


def _wauc(pos, neg, wp, wn):
    """Brute-force weighted Mann-Whitney (independent of S0's auroc)."""
    gt = (pos[:, None] > neg[None, :]).astype(np.float64) + 0.5 * (pos[:, None] == neg[None, :])
    return float((wp[:, None] * wn[None, :] * gt).sum() / (wp.sum() * wn.sum()))


def _oracle(fx, B=None):
    """INDEPENDENT recomputation: own sqlite reads (embeddings; the snapshot graph BY the fixture's id), own slices + renormalise, own
    side masks, own leaf list (nodes without children), own AUROC, own weights (the same generator order); only S0's skmeans (same
    seeds) is shared."""
    with ITS.fixture_scope():
        C = ITS.load_corpora(fx["db"])[OB.CORPUS]
    con = sqlite3.connect(ITS.emb_path("qwen3", fx["td"]))
    raw = {t: np.frombuffer(b, dtype=">f4").astype(np.float64)[:512] for t, b in con.execute("SELECT query, vector FROM embeddings")}
    con.close()
    con = sqlite3.connect(os.path.join(fx["td"], "snapshots.db"))
    G = {n: json.loads(con.execute("SELECT graph FROM snapshots WHERE id = ?", (FX_SIDS[n],)).fetchone()[0]) for n in (TREE, ANCH)}
    con.close()
    U = lambda A: A / np.linalg.norm(A, axis=1, keepdims=True)
    m = lambda sd, o: [i for i in range(len(C.text)) if C.kept[i] and bool(C.oos[i]) == o and C.side[i] == sd]
    tr, gt, ein, eoos = m(SS.TRAIN, False), m(SS.GATE, False), m(SS.EVAL, False), m(SS.EVAL, True)
    Xs = lambda idx, d: U(np.array([raw[C.text[i]][:d] for i in idx]))
    leaves = {}
    for n, g in G.items():
        lv = sorted((x for x in g["nodes"] if not x["childIds"]), key=lambda x: x["id"])
        leaves[n] = (np.array([x["vmfMu"] for x in lv]), len(lv[0]["vmfMu"]))
    sc = {}
    for key, n in (("T", TREE), ("AN", ANCH)):
        Mu, d = leaves[n]
        sc[key] = [np.array([max(float(z @ mu) for mu in Mu) for z in Xs(idx, d)]) for idx in (ein, eoos, gt)]
    L = len(leaves[TREE][0])
    Xtr = Xs(tr, 256)
    for s in K_SEEDS:
        Cm = ITS.skmeans(Xtr, L, s)
        sc["k%d" % s] = [(Xs(idx, 256) @ Cm.T).max(1) for idx in (ein, eoos, gt)]
    for s in OB.S0_SEEDS:
        Cm = ITS.skmeans(Xtr, FX_K, s)
        sc["s%d" % s] = [(Xs(idx, 256) @ Cm.T).max(1) for idx in (ein, eoos, gt)]
    lab = np.array([C.fine[i] for i in tr], dtype=str)
    Gn = U(np.array([Xtr[lab == u].mean(0) for u in sorted(set(lab.tolist()))]))
    sc["a"] = [(Xs(idx, 256) @ Gn.T).max(1) for idx in (ein, eoos, gt)]
    one = lambda k: np.ones(k)
    A = {k: _wauc(v[0], v[1], one(len(v[0])), one(len(v[1]))) for k, v in sc.items()}
    A_K = np.array([A["k%d" % s] for s in K_SEEDS])
    B = FX_B if B is None else B
    rng = np.random.default_rng(STREAM)
    ci = np.unique(C.comp[ein], return_inverse=True)[1]
    co = np.unique(C.comp[eoos], return_inverse=True)[1]
    dd = []
    for _ in range(B):
        wi = np.bincount(rng.integers(ci.max() + 1, size=ci.max() + 1), minlength=ci.max() + 1)[ci].astype(float)
        wo = np.bincount(rng.integers(co.max() + 1, size=co.max() + 1), minlength=co.max() + 1)[co].astype(float)
        km = np.mean([_wauc(sc["k%d" % s][0], sc["k%d" % s][1], wi, wo) for s in K_SEEDS])
        dd.append(_wauc(sc["T"][0], sc["T"][1], wi, wo) - km)
    Dl = A["T"] - float(A_K.mean())
    var_seed = float(np.var(A_K, ddof=1))
    se = float(np.sqrt(np.std(dd, ddof=1) ** 2 + var_seed / 5))
    if Dl - 1.645 * se > -0.010 and Dl + 1.645 * se < 0.010:
        st = "EQUIVALENT"
    elif abs(Dl) > 0.010 and (Dl - 1.96 * se > 0 or Dl + 1.96 * se < 0):
        st = "TREE-BETTER" if Dl > 0 else "KMEANS-BETTER"
    else:
        st = "NEITHER"
    thr = float(np.sort(sc["T"][2])[int(np.floor(0.05 * len(sc["T"][2])))])
    return {"A": A, "D": Dl, "se": se, "var_seed": var_seed, "mean_K": float(A_K.mean()), "status": st, "L": L,
            "fpr95_T": float(np.mean(sc["T"][1] >= thr)), "n": {"train": len(tr), "gate": len(gt), "in": len(ein), "oos": len(eoos)}}


@contextlib.contextmanager
def _scope(fx):
    """Fixture scope: S0's fixture K (CLINC 16), the fixture's pins, no heavy process, B 200."""
    g = globals()
    saved = (g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], g["BOOT_B"], g["L_REG"])
    g["_foreign_heavy"] = lambda: []
    with ITS.fixture_scope():
        ITS.PINS_FILE_OVERRIDE[0] = fx["pins"] if fx else None
        g["BOOT_B"] = FX_B
        g["L_REG"] = (fx or {}).get("L_REG", FX_K)          # the fixture tree's registered L (16 class leaves)
        try:
            yield
        finally:
            g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], g["BOOT_B"], g["L_REG"] = saved


def make_fixtures(td):
    out = {}
    for mode in FX_MODES:
        d = os.path.join(td, mode)
        os.makedirs(d)
        with _scope(None):
            out[mode] = build_fixture(d, mode, caf_drop=1 if mode == "TB" else 0)
    return out


def _cap(fn):
    buf, err, res = io.StringIO(), None, None
    with contextlib.redirect_stdout(buf):
        try:
            res = fn()
        except SystemExit as ex:
            err = str(ex)
    return buf.getvalue(), err, res


def _line(out, prefix):
    lines = [ln[len(TAG) + 1:] if ln.startswith(TAG + " ") else ln for ln in out.splitlines()]
    got = [ln.lstrip() for ln in lines if ln.lstrip().startswith(prefix)]
    return got[-1] if got else ""


def _run(fx, tag, **kw):
    out_dir = os.path.join(fx["td"], "out_%s_%d" % (tag, len(os.listdir(fx["td"]))))
    args = dict(data_root=fx["td"], out_dir=out_dir, programme=fx["prog"], identity=fx["identity"], sids=FX_SIDS)
    args.update(kw)
    with _scope(fx):
        o, err, res = _cap(lambda: main_run(**args))
    return o, err, res, out_dir


def selftest(only=None, quiet=False, fixture=None):
    n = [0]
    sel = (lambda k: only is None or k in only)

    def ok(c, what):
        n[0] += 1
        if not bool(c):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    if fixture is None:
        td = tempfile.mkdtemp(prefix="otc_st_")
        try:
            _selftest(sel, ok, td, make_fixtures(td))
        finally:
            shutil.rmtree(td, ignore_errors=True)
    else:
        _selftest(sel, ok, fixture[0], fixture[1])
    if not quiet:
        print("SELFTEST: %d checks passed" % n[0])
    return 0


def _syn(st, Dl, se=0.002):
    return {"status": st, "D": Dl, "se": se, "se_boot": se, "lo90": Dl - Z90 * se, "hi90": Dl + Z90 * se, "lo95": Dl - Z95 * se,
            "hi95": Dl + Z95 * se, "A_T": 0.97 + Dl, "var_seed": 0.0}


def _selftest(sel, ok, td, FX):
    if sel("ST-CONST"):
        ok(MARGIN == 0.010 and (Z90, Z95, Z80P) == (1.645, 1.96, 0.842), "registered margin 0.010 and z 1.645 / 1.96 / 0.842")
        ok(BOOT_B == 2000 and STREAM == ITS.BOOT_SEED + 2 and K_SEEDS == (0, 1, 2, 3, 4) and D == 256, "B 2,000; OB's stream; seeds 0-4; slice 256")
        ok(L_REG == 139 and SIDS == {"C-AF": "20261002_213715_Headless_Run_Auto_ge", "C-AN": "20261002_214129_Headless_Run_Auto_ge"},
           "L 139; the two Snapshot IDs of S1's outcome")
        ok(SEEN == {"tree": "0.96776", "km_seed0": "0.96999"} and OB_ID["per_seed"] == ("0.97437", "0.97263", "0.97601", "0.97446", "0.97649")
           and OB_ID["A_a"] == "0.97640", "identity digits (T-C6; OOS-BASELINES)")
        ok(P1 == (-0.002, -0.008, 0.004) and P_STAT == {"EQUIVALENT": 0.80, "NEITHER": 0.18, "DIFFERENT": 0.02} and P2 == (0.965, 0.950, 0.975),
           "registered predictions")
        ok(RO.git_blob_lf(OB.__file__) == OB_BLOB and RO.git_blob_lf(S1.__file__) == S1_BLOB, "OB 7e74108d and S1 4e9d9d05 imported unchanged")
        ok(PLAN == {"n_in": 6672, "n_oos": 1350} and SEEN_POINT == -0.0022 and SE_TRANSPORT == 0.0012, "registered denominators, seen point, SE")
    if sel("ST-UNIT"):
        se = 0.002
        ok(ot_status(0.0, se) == "EQUIVALENT", "0 +/- 1.645 x 0.002 inside -> EQUIVALENT")
        ok(ot_status(0.00670, se) == "EQUIVALENT" and ot_status(0.00672, se) == "NEITHER", "EQUIVALENT boundary 0.010 - 1.645 SE (0.00671)")
        ok(ot_status(-0.00670, se) == "EQUIVALENT" and ot_status(-0.00672, se) == "NEITHER", "EQUIVALENT boundary, negative side")
        ok(ot_status(0.0101, 0.001) == "TREE-BETTER" and ot_status(-0.0101, 0.001) == "KMEANS-BETTER", "DIFFERENT both directions, words mapped")
        ok(ot_status(-0.0101, 0.0052) == "NEITHER", "|Delta| > 0.010 but the 95% interval reaches 0 -> NEITHER")
        ok(ot_status(-0.009, 0.0001) == "EQUIVALENT" and ot_status(-0.0099, 0.0001) == "NEITHER", "|Delta| < 0.010, tight: never DIFFERENT")
        ok(ot_status(-0.012, 0.0055) == "KMEANS-BETTER" and ot_status(-0.012, 0.0062) == "NEITHER", "DIFFERENT uses 1.96")
        eq, df, w = OB.verdict_line(SEEN_POINT, SE_TRANSPORT)
        ok(abs(eq - 0.0070) < 5e-5 and abs(df - 0.0110) < 5e-5 and w == "SCOREABLE (EQUIVALENT side)", "Support (e)/(f): reach 0.0070 / 0.0110, SCOREABLE")
        ok(falsifier(np.str_("KMEANS-BETTER")) is True and falsifier("NEITHER") is False and falsifier("TREE-BETTER") is False, "F-OT on KMEANS-BETTER only")
        S = type("S", (), {})()
        S.X = ITS.unit(_rng("x").normal(size=(6, 4)))
        T = {"leaf_mu": ITS.unit(_rng("m").normal(size=(3, 4)))}
        R = {"in": np.array([0, 1]), "oos": np.array([2, 3]), "gate": np.array([4, 5])}
        ls = leaf_scores(T, S, R)
        ok(np.allclose(ls["in"], [max(S.X[i] @ m for m in T["leaf_mu"]) for i in (0, 1)]) and np.allclose(ls["gate"], [max(S.X[i] @ m for m in T["leaf_mu"]) for i in (4, 5)]),
           "leaf score = the MAX cos over the leaves, per role")
        dr = {"T": np.array([0.9, 0.8, 0.7]), "k0": np.array([0.5, 0.5, 0.5]), "k1": np.array([0.6, 0.6, 0.6]), "k2": np.array([0.5, 0.5, 0.5]),
              "k3": np.array([0.5, 0.5, 0.5]), "k4": np.array([0.4, 0.4, 0.4])}
        scs = {"T": {"in": np.array([1.0, 2.0]), "oos": np.array([0.0, 3.0])}}
        for s in K_SEEDS:
            scs["k%d" % s] = {"in": np.array([1.0, 2.0]), "oos": np.array([0.0, 0.5 + s])}
        RD = readout(scs, dr)
        A_K = np.array([ITS.auroc(scs["k%d" % s]["in"], scs["k%d" % s]["oos"]) for s in K_SEEDS])
        ok(abs(RD["D"] - (0.5 - A_K.mean())) < 1e-12 and abs(RD["A_T"] - 0.5) < 1e-12 and abs(RD["var_seed"] - np.var(A_K, ddof=1)) < 1e-15, "Delta vs the 5-seed MEAN; var_seed ddof 1")
        ok(abs(RD["se_boot"] - np.std(dr["T"] - 0.5, ddof=1)) < 1e-12 and abs(RD["se"] - np.sqrt(RD["se_boot"] ** 2 + RD["var_seed"] / 5)) < 1e-12,
           "SE_boot = SD (ddof 1) of T draw - mean K draw (paired); SE_total adds var_seed / 5")
        ok(abs(OB.brier(0.8, True) - 0.04) < 1e-12 and OB._hit(-0.008, -0.008, 0.004) and OB._hit(0.004, -0.008, 0.004), "Brier; closed interval")
    if sel("ST-RENDER"):
        cases = (("EQUIVALENT", -0.002, 0.002), ("NEITHER", -0.006, 0.004), ("TREE-BETTER", 0.02, 0.002), ("KMEANS-BETTER", -0.03, 0.002))
        for st, Dl, se in cases:
            ok(ot_status(Dl, se) == st, "synthetic case %s is the status rule's own answer" % st)
            txt = "\n".join(criteria_lines(_syn(st, Dl, se)))
            ok(("OT1: %s (Delta_T %+.5f, 90%% [%+.5f, %+.5f]" % (st, Dl, Dl - Z90 * se, Dl + Z90 * se)) in txt, "OT1 %s printed with its value and 90%% interval" % st)
            ok(("F-OT: FIRED" in txt) == (st == "KMEANS-BETTER") and ("F-OT: NOT FIRED (OT1 reads %s" % st in txt) == (st != "KMEANS-BETTER"),
               "F-OT %s under %s" % ("FIRED" if st == "KMEANS-BETTER" else "NOT FIRED", st))
            ok(("OOS-BASELINES' abstention sentence extends" in txt) == (st == "EQUIVALENT"), "EQUIVALENT sentence iff EQUIVALENT (%s)" % st)
            ok(("  %s:" % st) in txt, "the %s sentence printed" % st)
            P = "\n".join(predictions_lines(_syn(st, Dl, se), 0.96))
            ev = {"EQUIVALENT": st == "EQUIVALENT", "NEITHER": st == "NEITHER", "DIFFERENT": st in ("TREE-BETTER", "KMEANS-BETTER")}
            want = ", ".join("%s %.4f" % (k, (p - (1.0 if ev[k] else 0.0)) ** 2) for k, p in P_STAT.items())
            ok(("P1 OT1 %s: Brier %s" % (st, want)) in P, "P1 Briers under %s: %s" % (st, want))
            ok(("P1 Delta_T %+.5f vs -0.002 [-0.008, +0.004]: %s" % (Dl, "HELD" if -0.008 <= Dl <= 0.004 else "FAILED")) in P, "P1 numeric under %s" % st)
        txt = "\n".join(criteria_lines(_syn("KMEANS-BETTER", -0.03)))
        ok("exceeds the C-AF tree cells by +0.03000 AUROC" in txt and "\"abstention on flat cells only\" stays the wording" in txt, "KMEANS-BETTER magnitude and F-OT wording")
        txt = "\n".join(criteria_lines(_syn("TREE-BETTER", 0.02)))
        ok("exceed flat k-means at matched k by +0.02000 AUROC" in txt, "TREE-BETTER magnitude")
        P = "\n".join(predictions_lines(_syn("NEITHER", 0.0045), 0.9495))
        ok("P1 Delta_T +0.00450 vs -0.002 [-0.008, +0.004]: FAILED" in P and "P2 A(C-AN) 0.94950 vs 0.965 [0.950, 0.975]: FAILED" in P, "P1 / P2 FAILED branches")
        P = "\n".join(predictions_lines(_syn("NEITHER", -0.008), 0.975))
        ok("P1 Delta_T -0.00800 vs -0.002 [-0.008, +0.004]: HELD" in P and "P2 A(C-AN) 0.97500 vs 0.965 [0.950, 0.975]: HELD" in P, "P1 / P2 HELD at the closed ends")
        RDs = _syn("NEITHER", -0.006, 0.004)
        cn = {"in": 6672, "oos": 1350, "in_components": 6672, "oos_components": 1350, "in_kish": 1.0, "oos_kish": 1.0}
        S_ = "\n".join(support_lines(cn, dict(RDs, var_seed=0.0)))
        ok("DEFF 1.0000" in S_ and "n_eff 6672 in-scope / 1350 OOS" in S_ and "verdict line at the seen point -0.0022: DESCRIPTIVE-ONLY" in S_,
           "support: DEFF, n_eff, verdict line at SE 0.004 DESCRIPTIVE-ONLY")
        S_ = "\n".join(support_lines(dict(cn, oos_kish=1.25), dict(_syn("EQUIVALENT", 0.0, 0.0012), var_seed=0.0)))
        ok("DEFF 1.2500" in S_ and "n_eff 6672 in-scope / 1080 OOS" in S_ and "SCOREABLE (EQUIVALENT side)" in S_ and "EQUIVALENT reach |Delta_true| <= 0.00702" in S_,
           "support: DEFF = max Kish, n_eff per stratum, reach at the measured SE")
    for mode in FX_MODES:
        key = "ST-E2E-" + mode
        if not sel(key):
            continue
        fx = FX[mode]
        orc = fx["oracle"]
        o, err, res, out_dir = _run(fx, "e2e")
        ok(err is None, "%s: --run completes (%s)" % (mode, err))
        X, L, po = res
        txt = open(po, encoding="utf-8").read()
        ok(txt.splitlines() == L, "%s: the file of record is the printed lines" % mode)
        RD = X["RD"]
        ok(abs(RD["D"] - orc["D"]) < 1e-12, "%s Delta_T %+.6f = oracle %+.6f" % (mode, RD["D"], orc["D"]))
        ok(abs(RD["se"] - orc["se"]) < 1e-9, "%s SE_total %.6f = oracle %.6f" % (mode, RD["se"], orc["se"]))
        ok(abs(RD["var_seed"] - orc["var_seed"]) < 1e-15 and abs(RD["mean_K"] - orc["mean_K"]) < 1e-12, "%s K mean / var_seed = oracle" % mode)
        ok(RD["status"] == orc["status"], "%s OT1 %s = oracle %s" % (mode, RD["status"], orc["status"]))
        ok(_line(o, "OT1: ").startswith("OT1: %s (Delta_T %+.5f" % (orc["status"], orc["D"])), "%s printed OT1 value: %s" % (mode, _line(o, "OT1: ")[:50]))
        ok(X["L"] == orc["L"] and ("k-means k = L = %d" % orc["L"]) in txt, "%s k matched to the tree's L = %d" % (mode, orc["L"]))
        ok(abs(X["desc"]["AN"]["A"] - orc["A"]["AN"]) < 1e-12 and ("P2 A(C-AN) %.5f" % orc["A"]["AN"]) in txt, "%s A(C-AN) %.5f at its slice = oracle" % (mode, orc["A"]["AN"]))
        ok(abs(X["fl"]["T"]["fpr95"] - orc["fpr95_T"]) < 1e-12, "%s FPR95(T) at its GATE threshold = oracle" % mode)
        ok(("FPR95 T (C-AF): %.4f" % orc["fpr95_T"]) in txt, "%s FPR95(T) printed" % mode)
        for b in ("a",):
            ok(abs(X["desc"][b]["A"] - orc["A"][b]) < 1e-12, "%s descriptive (a) = oracle" % mode)
        ok(all(abs(a - orc["A"]["s%d" % s]) < 1e-12 for s, a in zip(OB.S0_SEEDS, X["desc"]["S0"]["A"])), "%s S0 K-150(fixture 16) per seed = oracle" % mode)
        cl = _line(o, "CENSUS")
        ok(("EVAL OOS n_OOS %d" % orc["n"]["oos"]) in cl and ("EVAL in-scope n_in %d" % orc["n"]["in"]) in cl and ("TRAIN in-scope %d" % orc["n"]["train"]) in cl,
           "%s census denominators = oracle (in %d, OOS %d)" % (mode, orc["n"]["in"], orc["n"]["oos"]))
        ok(("n_in %d CLINC in-scope EVAL rows" % orc["n"]["in"]) in txt and ("n_OOS %d oos_plus OOS rows" % orc["n"]["oos"]) in txt, "%s support denominators" % mode)
        aud = _line(o, "TRAIN-ONLY:")
        ok(", 0 with an EVAL row, 0 OOS rows" in aud, "%s fit audit: no EVAL / OOS row in any fit" % mode)
        ok(sum(1 for f in ITS.FIT_LOG if f[0].startswith("OTC k-means")) == 5 and all(f[3] == (SS.TRAIN,) for f in ITS.FIT_LOG if f[0].startswith("OTC k-means")),
           "%s five k-means fits, TRAIN only" % mode)
        ok(EVENTS[:2] == [("IDENTITY", "ok"), ("K", "fitted")], "%s identity precedes K_1..K_4" % mode)
        fo = _line(o, "F-OT: ")
        ok(fo.startswith("F-OT: FIRED") == (orc["status"] == "KMEANS-BETTER") and fo.startswith("F-OT: NOT FIRED") == (orc["status"] != "KMEANS-BETTER"),
           "%s F-OT line %s" % (mode, fo[:20]))
        ev = {"EQUIVALENT": orc["status"] == "EQUIVALENT", "NEITHER": orc["status"] == "NEITHER", "DIFFERENT": orc["status"] in ("TREE-BETTER", "KMEANS-BETTER")}
        ok(("P1 OT1 %s: Brier %s" % (orc["status"], ", ".join("%s %.4f" % (k, (p - float(ev[k])) ** 2) for k, p in P_STAT.items()))) in txt, "%s P1 Brier values" % mode)
        for need in ("LIKE WITH LIKE (registered)", "CLINC150 SPLIT (registered)", "WHAT THIS RESULT WILL NOT SHOW", "IDENTITY (S1 T-C6)", "-> REPRODUCED",
                     "== PREDICTIONS", "builder's readings: OT-R1", "TREES: C-AF snapshot fx_caf_sid", "== SUPPORT", "MDE80"):
            ok(need in txt, "%s outcome carries %r" % (mode, need))
        with open(os.path.join(out_dir, SCORES_CSV), encoding="utf-8") as fh:
            rr = list(csv.DictReader(fh))
        ok(sum(1 for r in rr if r["role"] == "EVAL_OOS") == orc["n"]["oos"] and sum(1 for r in rr if r["role"] == "EVAL_IN") == orc["n"]["in"], "%s CSV rows" % mode)
        o2, err2, _r2, _d = _run(fx, "again", out_dir=out_dir)
        ok(err2 and "write-once" in err2 and "IDENTITY" not in o2, "%s a second --run REFUSES before any read (write-once)" % mode)
        planted = {"EQ": "EQUIVALENT", "KB": "KMEANS-BETTER", "TB": "TREE-BETTER", "NE": "NEITHER"}[mode]
        ok(orc["status"] == planted, "%s: the planted answer %s (oracle reads %s, Delta %+.4f, SE %.4f)" % (mode, planted, orc["status"], orc["D"], orc["se"]))
    if sel("ST-REFUSE"):
        fx = FX["NE"]
        for k, v in (("tree", "0.11111"), ("km_seed0", "0.11111"), ("A_a", "0.11111")):
            o, err, _r, d_ = _run(fx, "id" + k, identity=dict(fx["identity"], **{k: v}))
            ok(err and "IDENTITY PRECONDITION FAILED" in err and k in err and not os.path.exists(os.path.join(d_, OUTCOME)), "identity %s mismatch REFUSES; nothing written" % k)
            ok(not any(f[0] == "OTC k-means k=L=%d s4" % fx["oracle"]["L"] for f in ITS.FIT_LOG), "identity %s refuses before K_1..K_4" % k)
        bad = dict(fx["identity"])
        bad["per_seed"] = tuple(list(bad["per_seed"][:4]) + ["0.00000"])
        o, err, _r, _d = _run(fx, "idseed", identity=bad)
        ok(err and "per_seed" in err, "identity checks the 5th S0 seed (all seeds)")
        o, err, _r, _d = _run(fx, "sid", sids=dict(FX_SIDS, **{"C-AF": "fx_caf_sid_later"}))
        ok(err and "Snapshot ID" in err and "!= the registered" in err, "a Snapshot ID other than the registered one REFUSES")
        o, err, _r, _d = _run(fx, "sidan", sids=dict(FX_SIDS, **{"C-AN": "other"}))
        ok(err and "C-AN" in err and "Snapshot ID" in err, "C-AN's Snapshot ID checked too")
        g = globals()
        o, err, _r, _d = _run(dict(fx, L_REG=fx["oracle"]["L"] + 1), "lreg")
        ok(err and "leaves, not the registered L" in err, "L != the registered 139 REFUSES")
        prog2 = os.path.join(fx["td"], "prog_quoted.md")
        with open(prog2, "w", encoding="utf-8") as fh:
            fh.write("a quotation: %s\n" % REG_HEADING)
        o, err, _r, _d = _run(fx, "noreg", programme=prog2)
        ok(err and "registration heading is absent" in err, "a quoted (not line-anchored) heading REFUSES")
        pins = json.load(open(fx["pins"]))
        p2 = os.path.join(fx["td"], "pins_null.json")
        pins["emb"]["qwen3"] = None
        json.dump(pins, open(p2, "w"))
        o, err, _r, _d = _run(dict(fx, pins=p2), "nullpin")
        ok(err and "UNPINNED" in err, "--run REFUSES a null qwen3 pin")
        with _scope(fx):
            g["_foreign_heavy"] = lambda: ["java.exe 1234"]
            o, err, _r = _cap(lambda: main_run(data_root=fx["td"], out_dir=os.path.join(fx["td"], "heavy_%d" % len(os.listdir(fx["td"]))), programme=fx["prog"],
                                               identity=fx["identity"], sids=FX_SIDS))
        ok(err and "foreign heavy process" in err, "--run REFUSES beside a JVM")
        with _scope(fx):
            g["_foreign_heavy"] = lambda: ["java.exe 1234"]
            o, err, _r = _cap(lambda: dry_run(data_root=fx["td"], programme=fx["prog"], identity=fx["identity"], sids=FX_SIDS, timing=False))
        ok(err and "foreign heavy process" in err, "--dry-run REFUSES beside a JVM")
        d2 = os.path.join(td, "slice512")
        os.makedirs(d2)
        with _scope(None):
            fx2 = build_fixture(d2, "EQ", caf_d=512)
        o, err, _r, _d = _run(fx2, "slice")
        ok(err and "C-AF's slice is 512" in err, "C-AF at a slice other than 256 REFUSES")
        open(os.path.join(fx["td"], "snapshots.db-wal"), "wb").write(b"x")
        try:
            o, err, _r, _d = _run(fx, "wal")
        finally:
            os.remove(os.path.join(fx["td"], "snapshots.db-wal"))
        ok(err and "wal" in err.lower(), "a non-empty snapshots.db-wal REFUSES")
    if sel("ST-DRY"):
        fx = FX["TB"]
        with _scope(fx):
            o, err, _r = _cap(lambda: dry_run(data_root=fx["td"], programme=fx["prog"], identity=fx["identity"], sids=FX_SIDS, timing=True))
        ok(err is None, "dry-run completes (%s)" % err)
        orc = fx["oracle"]
        ok(("DENOMINATORS vs registration: n_in %d (registered 6672) DIFFERENT; n_OOS %d (registered 1350) DIFFERENT" % (orc["n"]["in"], orc["n"]["oos"])) in o,
           "dry-run prints the denominators against the registration")
        ok(("IDENTITY (S1 T-C6): A(T) %.5f" % orc["A"]["T"]) in o and "-> REPRODUCED" in o and "DRY RUN complete: nothing written" in o, "dry-run identity value printed")
        ok("TREES: C-AF snapshot fx_caf_sid (run log Snapshot ID), %d leaves, slice 256" % orc["L"] in o, "dry-run prints the trees (id, L, slice)")
        ok(not any(f[0].startswith("OTC k-means") and not f[0].endswith("s0") for f in ITS.FIT_LOG) and not any(f[0].startswith("OB (") for f in ITS.FIT_LOG),
           "dry-run fits K_0 only: no K_1..K_4, no (a)-(d)")
        ok("Delta_T " not in o.replace("no Delta_T", ""), "dry-run prints no Delta_T")
        ok(not any(os.path.exists(os.path.join(fx["td"], fn)) for fn in (OUTCOME, SCORES_CSV)), "dry-run leaves no outcome file")
        with _scope(fx):
            o, err, _r = _cap(lambda: dry_run(data_root=fx["td"], programme=fx["prog"], identity=dict(fx["identity"], tree="0.11111"), sids=FX_SIDS, timing=False))
        ok(err and "IDENTITY PRECONDITION FAILED" in err, "dry-run identity mismatch REFUSES")


MUTANTS = (
    ("margin 0.02", "MARGIN = 0.010\n", "MARGIN = 0.020\n", ("ST-CONST",)),
    ("status words swapped (direction flip)", "WORD = {\"EQUIVALENT\": \"EQUIVALENT\", \"NEITHER\": \"NEITHER\", \"BASELINE-BETTER\": \"TREE-BETTER\", \"S0-BETTER\": \"KMEANS-BETTER\"}\n",
     "WORD = {\"EQUIVALENT\": \"EQUIVALENT\", \"NEITHER\": \"NEITHER\", \"BASELINE-BETTER\": \"KMEANS-BETTER\", \"S0-BETTER\": \"TREE-BETTER\"}\n", ("ST-UNIT",)),
    ("Delta against K seed 0 (T-C6's single seed)", "    Dl = A_T - mean_K\n", "    Dl = A_T - float(A_K[0])\n", ("ST-UNIT", "ST-E2E-NE", "ST-E2E-TB")),
    ("Delta against the max K seed (min<->max)", "    mean_K = float(A_K.mean())\n", "    mean_K = float(A_K.max())\n", ("ST-UNIT", "ST-E2E-NE", "ST-E2E-TB")),
    ("seed term dropped", "    se = float(np.sqrt(se_boot ** 2 + var_seed / len(K_SEEDS)))\n", "    se = float(np.sqrt(se_boot ** 2))\n", ("ST-UNIT", "ST-E2E-NE")),
    ("seed term var_seed (not / 5)", "    se = float(np.sqrt(se_boot ** 2 + var_seed / len(K_SEEDS)))\n", "    se = float(np.sqrt(se_boot ** 2 + var_seed))\n", ("ST-UNIT", "ST-E2E-NE")),
    ("var_seed ddof 0", "    mean_K = float(A_K.mean())\n    var_seed = float(np.var(A_K, ddof=1))\n", "    mean_K = float(A_K.mean())\n    var_seed = float(np.var(A_K))\n", ("ST-UNIT", "ST-E2E-NE")),
    ("SE_boot ddof 0", "    se_boot = float(np.std(dd, ddof=1))\n", "    se_boot = float(np.std(dd))\n", ("ST-UNIT", "ST-E2E-NE")),
    ("unpaired bootstrap (T draws minus the K point)", "    dd = draws[\"T\"] - k_draw_mean\n", "    dd = draws[\"T\"] - mean_K\n", ("ST-UNIT", "ST-E2E-NE")),
    ("K draws from seed 0 only", "    k_draw_mean = np.mean(np.vstack([draws[\"k%d\" % s] for s in K_SEEDS]), axis=0)\n",
     "    k_draw_mean = draws[\"k0\"]\n", ("ST-UNIT", "ST-E2E-NE")),
    ("unpaired weights (fresh permutation per score)", "            draws[k].append(ITS.auroc(sc[k][\"in\"], sc[k][\"oos\"], wi, wo))\n",
     "            draws[k].append(ITS.auroc(sc[k][\"in\"], sc[k][\"oos\"], np.random.default_rng(len(draws[k]) + len(k)).permutation(wi), wo))\n", ("ST-E2E-NE",)),
    ("bootstrap strata swapped in the stream", "    for wi, wo in zip(ITS.comp_weights(C.comp[R[\"in\"]], B, rng), ITS.comp_weights(C.comp[R[\"oos\"]], B, rng)):\n        for k in names:\n",
     "    for wo, wi in zip(ITS.comp_weights(C.comp[R[\"oos\"]], B, rng), ITS.comp_weights(C.comp[R[\"in\"]], B, rng)):\n        for k in names:\n", ("ST-E2E-NE",)),
    ("four K seeds", "K_SEEDS = (0, 1, 2, 3, 4)\n", "K_SEEDS = (0, 1, 2, 3)\n", ("ST-CONST",)),
    ("k = L - 1 (k not matched)", "        Cm = ITS.km_fit(C, S, L, s, \"OTC k-means k=L=%d s%d\" % (L, s))\n",
     "        Cm = ITS.km_fit(C, S, L - 1, s, \"OTC k-means k=L=%d s%d\" % (L, s))\n", ("ST-E2E-NE", "ST-E2E-TB", "ST-E2E-KB")),
    ("k = S0's K (150 / fixture 16) instead of L", "    L = trees[TREE][\"L\"]\n    ITS.fit_rows(", "    L = II.GOLD_K[OB.CORPUS][1]\n    ITS.fit_rows(", ("ST-E2E-TB",)),
    ("leaf score min over leaves (min<->max)", "    return {k: OB.maxcos(T[\"leaf_mu\"], Sd.X[R[k]]) for k in (\"in\", \"oos\", \"gate\")}\n",
     "    return {k: (Sd.X[R[k]] @ T[\"leaf_mu\"].T).min(1) for k in (\"in\", \"oos\", \"gate\")}\n", ("ST-UNIT",)),
    ("first leaf only (first-site-only)", "    return {k: OB.maxcos(T[\"leaf_mu\"], Sd.X[R[k]]) for k in (\"in\", \"oos\", \"gate\")}\n",
     "    return {k: OB.maxcos(T[\"leaf_mu\"][:1], Sd.X[R[k]]) for k in (\"in\", \"oos\", \"gate\")}\n", ("ST-UNIT",)),
    ("T scored on C-AN's leaves (wrong tree)", "    sc = {\"T\": leaf_scores(trees[TREE][\"T\"], space_for(S, trees[TREE][\"d\"], C), R)}\n",
     "    sc = {\"T\": leaf_scores(trees[ANCH][\"T\"], space_for(S, trees[ANCH][\"d\"], C), R)}\n", ("ST-E2E-KB", "ST-E2E-TB")),
    ("C-AN scored at 256 (not its slice)", "    sc[\"AN\"] = leaf_scores(trees[ANCH][\"T\"], space_for(S, trees[ANCH][\"d\"], C), R)\n",
     "    sc[\"AN\"] = leaf_scores(dict(trees[ANCH][\"T\"], leaf_mu=ITS.unit(trees[ANCH][\"T\"][\"leaf_mu\"][:, :256])), S, R)\n", ("ST-E2E-TB", "ST-E2E-NE")),
    ("P2 scored on T instead of C-AN", "    L += predictions_lines(X[\"RD\"], X[\"desc\"][\"AN\"][\"A\"])\n", "    L += predictions_lines(X[\"RD\"], X[\"RD\"][\"A_T\"])\n",
     ("ST-E2E-KB", "ST-E2E-TB")),
    ("FPR95 threshold from EVAL in-scope", "    fl = {k: OB.fpr_line(sc[k]) for k in (\"T\", \"k0\", \"AN\", \"s0\") + DESC}\n",
     "    fl = {k: OB.fpr_line(dict(sc[k], gate=sc[k][\"in\"])) for k in (\"T\", \"k0\", \"AN\", \"s0\") + DESC}\n", ("ST-E2E-NE", "ST-E2E-TB")),
    ("OOS from the EVAL hash side only (wrong population)", "    R = OB.rows(C, S)\n    if int(C.oos[R[\"train\"]].sum())",
     "    R = OB.rows(C, S)\n    R[\"oos\"] = np.array([i for i in R[\"oos\"] if C.hash_side[i] == SS.EVAL], dtype=int)\n    if int(C.oos[R[\"train\"]].sum())", ("ST-E2E-NE", "ST-E2E-TB")),
    ("in-scope from GATE (wrong split side)", "    R = OB.rows(C, S)\n    if int(C.oos[R[\"train\"]].sum())",
     "    R = OB.rows(C, S)\n    R[\"in\"] = R[\"gate\"]\n    if int(C.oos[R[\"train\"]].sum())", ("ST-E2E-NE", "ST-E2E-TB")),
    ("k-means fitted on TRAIN + EVAL (no guard)", "        Cm = ITS.km_fit(C, S, L, s, \"OTC k-means k=L=%d s%d\" % (L, s))\n",
     "        Cm = ITS.skmeans(S.X[np.concatenate([R[\"train\"], R[\"in\"]])], L, s)\n", ("ST-E2E-NE", "ST-E2E-TB")),
    ("F-OT fires on any non-EQUIVALENT", "    return bool(status == \"KMEANS-BETTER\")\n", "    return bool(status != \"EQUIVALENT\")\n", ("ST-UNIT", "ST-RENDER")),
    ("F-OT identity-tested (numpy str never fires)", "    if falsifier(st):\n", "    if falsifier(st) is np.True_:\n", ("ST-RENDER", "ST-E2E-KB")),
    ("EQUIVALENT sentence omitted", "    if st == \"EQUIVALENT\":\n        L.append(", "    if False:\n        L.append(", ("ST-RENDER",)),
    ("KMEANS-BETTER sentence omitted", "    elif st == \"KMEANS-BETTER\":\n", "    elif False:\n", ("ST-RENDER",)),
    ("P1 interval open", "\"HELD\" if OB._hit(v, P1[1], P1[2]) else \"FAILED\"", "\"HELD\" if P1[1] < v < P1[2] else \"FAILED\"", ("ST-RENDER",)),
    ("DIFFERENT event includes NEITHER", "\"DIFFERENT\": st in (\"TREE-BETTER\", \"KMEANS-BETTER\")}\n    br =",
     "\"DIFFERENT\": st != \"EQUIVALENT\"}\n    br =", ("ST-RENDER",)),
    ("Brier event EQUIVALENT read as NEITHER", "    evt = {\"EQUIVALENT\": st == \"EQUIVALENT\", \"NEITHER\": st == \"NEITHER\",",
     "    evt = {\"EQUIVALENT\": st == \"NEITHER\", \"NEITHER\": st == \"NEITHER\",", ("ST-RENDER",)),
    ("support DEFF = min Kish (min<->max)", "    deff = max(cn[\"in_kish\"], cn[\"oos_kish\"])\n", "    deff = min(cn[\"in_kish\"], cn[\"oos_kish\"])\n", ("ST-RENDER",)),
    ("verdict line at the transported SE (not measured)", "    eq, df, w = OB.verdict_line(SEEN_POINT, RD[\"se\"])\n", "    eq, df, w = OB.verdict_line(SEEN_POINT, SE_TRANSPORT)\n", ("ST-RENDER",)),
    ("identity skipped", "    idline = identity_check(got, identity)\n", "    idline = \"IDENTITY (S1 T-C6): skipped -> REPRODUCED\"\n", ("ST-REFUSE",)),
    ("identity checks the first S0 seed only", "        if tuple(got[\"per_seed\"]) != tuple(target[\"per_seed\"]):\n",
     "        if got[\"per_seed\"][0] != target[\"per_seed\"][0]:\n", ("ST-REFUSE",)),
    ("identity after K_1..K_4", "    idline = identity_check(got, identity)\n    EVENTS.append((\"IDENTITY\", \"ok\"))\n    sc.update(km_scores(C, S, R, L, K_SEEDS[1:]))\n    EVENTS.append((\"K\", \"fitted\"))\n",
     "    sc.update(km_scores(C, S, R, L, K_SEEDS[1:]))\n    EVENTS.append((\"K\", \"fitted\"))\n    idline = identity_check(got, identity)\n    EVENTS.append((\"IDENTITY\", \"ok\"))\n", ("ST-REFUSE", "ST-E2E-EQ")),
    ("Snapshot ID check removed", "        if p[\"sid\"] != sids[name]:\n", "        if False:\n", ("ST-REFUSE",)),
    ("L check removed", "    if out[TREE][\"L\"] != L_REG:\n", "    if False:\n", ("ST-REFUSE",)),
    ("slice check removed", "    if out[TREE][\"d\"] != D:\n", "    if False:\n", ("ST-REFUSE",)),
    ("not write-once", "    for p in out_paths(out_dir):\n        if os.path.lexists(p):\n", "    for p in out_paths(out_dir):\n        if False:\n", ("ST-E2E-EQ",)),
    ("registration not line-anchored", "REG_RE = re.compile(r\"^\" + re.escape(REG_HEADING), re.M)\n", "REG_RE = re.compile(re.escape(REG_HEADING))\n", ("ST-REFUSE",)),
    ("non-strict pins on --run", "    sha0, C, S = OB.load_inputs(db, emb_dir, strict=True)\n", "    sha0, C, S = OB.load_inputs(db, emb_dir, strict=False)\n", ("ST-REFUSE",)),
    ("heavy check dropped from --run", "        refuse(\"the registration heading is absent from %s: --run reads only a registered test\" % programme)\n    heavy_check()\n",
     "        refuse(\"the registration heading is absent from %s: --run reads only a registered test\" % programme)\n", ("ST-REFUSE",)),
    ("dry-run fits all five K seeds", "    k0 = km_scores(C, S, R, trees[TREE][\"L\"], K_SEEDS[:1])[\"k0\"]\n", "    k0 = km_scores(C, S, R, trees[TREE][\"L\"], K_SEEDS)[\"k0\"]\n", ("ST-DRY",)),
    ("EQUIVALENT at 95% (z 1.96)", "    return WORD[OB.ob_status(Dl, se)]\n", "    return WORD[OB.ob_status(Dl, se * Z95 / Z90)]\n", ("ST-UNIT",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="otc_mut_")
    fx = make_fixtures(td)
    killed = 0
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        code = head.replace(old, new)
        ns = {"__name__": "otc_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(code, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests) if tests else None, quiet=True, fixture=(td, fx))
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:100])
        killed += res.startswith("KILLED")
        print("  %-58s %s" % (name, res))
        sys.stdout.flush()
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="OOS-TREE-CELLS (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--data-root", default=None, help="the S1 build worktree (DBs, snapshots.db, run dirs); default TAXOARENA_DATA_ROOT or the repo")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-timing", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run(a.data_root, timing=not a.no_timing)
    main_run(a.data_root, a.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
