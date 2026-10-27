"""knn_route.py: KNN-ROUTE -- does cell-free kNN routing (k = 50 deciding; restricted to the item's own source, [SC]) route the
union roster as well as AF-U's cells, with an unrestricted kNN floor and a correctness-pattern [TS] ceiling beside?
ZERO calls: no judge, no LLM, no embedding call (vectors are READ from embeddings_cache.db through rp12_pairing's read-only
readers and checked against the UNION-AF-ROUTE bundle), no construction, no Gradle. A CPU reader (T2 of the testing-logic review).

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — KNN-ROUTE: does cell-free kNN routing (k = 50
  deciding; restricted to the item's own source, [SC]) route the union roster as well as AF-U's cells, ..." (L24278-L24289,
  _as_of b66b075d): KN1, Support (a)-(g), P1-P3, F-KN, WILL-NOT-SHOW. Record L24259-L24263. Source:
  docs/literature/2026-10-04_testing_logic_review.md (bd5ca001) T2.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, plain form; never beside a construction: every step reads the pool):
  0. python tools/analysis/knn_route.py --selftest   # synthetic fixtures (temp on E: via scratch_dir); opens NO DB of record
     python tools/analysis/knn_route.py --mutants    # the mutant table, re-run (each must make the selftest fail)
  1. python tools/analysis/knn_route.py --dry-run    # POOL line first; pins; denominators; B0-2 pool check; inputs re-hashed;
                                                     #   frozen policy sha; NO key, NO statistic; writes nothing
  2. python tools/analysis/knn_route.py --run        # ONE EVAL key read (marker first); outcome WRITE-ONCE:
       experiment_results/archv2/knn_route/outcome.txt (+ knn_route.READ_STARTED). Never committed: pin by sha256 and back up to
       E:/TaxoArena_backup_<date>_knn_route with SHA256SUMS.txt (registration HYGIENE).
  --data-root <dir> (optional, every mode; set before any import). Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1)-(3) as route_source_null.py (pool line, write-once, B0-2 check, AF-U state, inputs manifest, AF / K0..K4 cells, frozen
  policy; the views, the marker, the EVAL key read; [KNN-DENOM]; [B3]); (4) the 256-d vectors of every scored item read through
  union_af_route._TV (rp12_pairing's readers) and checked EQUAL to the UNION-AF-ROUTE bundle's rows wherever the bundle carries
  the item ([KNN-VEC]); (5) run_boot (B 2,000, default_rng(42)) with a hook that re-fits each replicate (V.fit for the best
  single and the AF arm; the kNN arms on the replicate's TRAIN multiset); the hook's AF / best-single accuracies must equal
  run_boot's own arms in every replicate ([KNN-HOOK]); [KNN-IDENTITY] before any new number; (6) KN1, descriptive arms, the TS
  ceiling, predictions, F-KN; the outcome written mode "x" (*_VOID.txt if a view's sha changed during the read).

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  R1  Neighbour pool = the SCORED TRAIN items (the policy-fit set of G14's reader: 11,841 key-complete items under UNUSABLE_CELL),
      not the 12,334 bundle TRAIN rows the registration names as "TRAIN 12,334 keyed rows": 493 of those carry an unusable key cell
      for at least one model and cannot enter a mean keyed accuracy (DEVIATION, stated; for the registrar). Vectors: the item's
      256-d unit vector (AF-U's slice) from the readers of record, equal to the bundle's where the bundle carries it (MC-EXCLUDE'd
      items are read from the same readers).
  R2  KNN_k (k in {25, 50, 100}; 50 DECIDING): the k TRAIN items of largest cosine (ties -> the earlier TRAIN position, i.e. the
      smaller item_id); the model with the highest mean keyed accuracy among them (ties -> the first model in sorted-roster order,
      numpy argmax); BACKOFF to the best single iff the leader's margin over the runner-up (the second-largest mean) is STRICTLY
      below SE = sqrt(p1 (1 - p1) / n), p1 the leader's mean, n the neighbour count (k). KNN-SC: TRAIN items of the item's own
      stratum source only ([SC]); a source with fewer than k TRAIN items uses all of them (counted). KNN-ALL: unrestricted ([LF]).
  R3  Two-stage replicates: the kNN arms are recomputed on each replicate's TRAIN multiset (multiplicity = run_boot's TRAIN unit
      weight): walking the item's neighbour order, each TRAIN item counts with its multiplicity, capped so the total is k; the
      neighbour order is precomputed to 3k entries (a replicate whose 3k entries carry less than k weight uses what they carry:
      the shortfall count is printed). EVAL weights = run_boot's component draws (item-paired with the AF arm).
  R4  D_N = acc(KNN-SC k 50) - acc(AF-U) (= G_KNN-SC - G_AF); 95% interval = point +- 1.96 SE_2stage, 90% = +- 1.645 SE_2stage
      (G14's reader form); spread_K = max - min over s of G_K,s points (K0..K4, re-measured; UNION-AF-ROUTE printed 0.58pp).
  R5  KN1 = CELLS-ADD iff hi95 < 0 AND |D_N| > spread_K; CELLS-UNNEEDED iff (-0.5pp < lo90 AND hi90 < +0.5pp, strict) OR lo95 > 0;
      UNDETERMINED otherwise. If CELLS-ADD and CELLS-UNNEEDED both held on the data (possible only if spread_K < 0.5pp), the run
      REFUSES ([KN1-OVERLAP], a registration defect for the registrar) instead of choosing. Rule 8: CELLS-UNNEEDED is refuted iff
      hi95 < 0. F-KN fires iff CELLS-UNNEEDED.
  R6  TS ceiling (descriptive, never ranked): TRAIN items' 18-model correctness vectors, unit-normalised, clustered by
      g13_breakdown.ukm_fit (spherical k-means) at k = 123, seeds 0-4; all-zero vectors (no model correct) form one extra cell;
      each EVAL item filed to the majority TS cell of its k = 50 UNRESTRICTED neighbours (ties -> the smaller cell index); per-cell
      TRAIN policy by V.fit; TS - G_declared = acc(TS) - acc(TRUE (source, domain)), per seed and the mean over seeds.
  R7  Predictions "X [lo, hi]" HELD iff the point lies in the closed interval; KN1's probabilities scored by the three-outcome
      Brier sum. Not applicable (stated): no judge verdict (no wrong(established), no tie convention A / B); no call cache,
      --pilot or truncation guard (zero calls).

SELFTEST (--selftest; escalation_rc's fixture layout via union_route_common.build_layout; k scaled to the fixture: ks (3, 5, 9),
k = 5 deciding, TS k 4):
  branches      KN1 CELLS-ADD / CELLS-UNNEEDED (both branches) / UNDETERMINED by value incl. hi95 exactly 0, |D_N| exactly
                spread_K, the TOST end points exactly +-0.5pp, lo95 exactly 0; [KN1-OVERLAP]; rule 8; F-KN; P1-P3 bands inclusive;
                Brier; required lines
  units         knn_choose against plain loops (ties, backoff strictly below one SE, a short source, multiplicities capped at k)
  run_e2e       --run end to end: every KNN-SC / KNN-ALL accuracy at every k, D_N with its two-stage interval and SE, spread_K, the
                TS ceiling per seed against an INDEPENDENT oracle (plain-loop neighbours, means and backoff on the fixture's raw rows
                and vectors; the same unit draws); KN1 / F-KN by the hand rule from the printed numbers; second --run refused
  refusals      pool, manifest, policy sha, [KNN-DENOM], [KNN-IDENTITY], [B3], [KNN-VEC], [KNN-HOOK], marker present; no outcome
  dry_run       POOL first, no statistic, nothing written; the REAL constants' lines
  branch_cover  every print / refusal branch executed
MUTANTS: see MUTANTS at the end of this file and the commit message.
NOT DONE HERE: the real --run (the operator's, after READY); no Kotlin / Gradle.
"""
import os
import sys


def _pre_root(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


_DR = _pre_root(sys.argv[1:]) if __name__ == "__main__" else None
if _DR:
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_DR)
    os.environ["TAXOARENA_RESULTS_ROOT"] = os.path.abspath(_DR)

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import types         # noqa: E402
import argparse      # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import union_route_common as U   # noqa: E402  (pins escalation_rc, union_cells_io, union_af_route)

TAG = "[KNN]"
TEST_ID = "KNN-ROUTE"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — KNN-ROUTE: does cell-free kNN routing'
            ' (k = 50 deciding; restricted to the item\'s own source, [SC]) route the union roster as well as AF-U\'s cells, ..."'
            ' L24278-L24289 (_as_of b66b075d)')
OUT = "experiment_results/archv2/knn_route"
REG = dict(U.COMMON, out=OUT + "/outcome.txt", marker=OUT + "/knn_route.READ_STARTED", ks=(25, 50, 100), k_decide=50, ts_k=123,
           ts_seeds=(0, 1, 2, 3, 4), delta=0.005, n_train_reg=12334)
FIXTURE_REG = dict(out="res/knn/outcome.txt", marker="res/knn/READ_STARTED", ks=(3, 5, 9), k_decide=5, ts_k=4)
_REG = [REG]


def reg():
    return _REG[0]


SUPPORT = dict(deff=2.867, n_eff=2060, se=0.0044, mde=0.0123)
VERDICT_LINE = ("KN1 DESCRIPTIVE-ONLY at the prediction (D_N -0.3pp); the TOST branch of CELLS-UNNEEDED is UNREACHABLE at SE 0.44pp"
                " (reach 0.5 - 1.645 x 0.44 = -0.22pp < 0); CELLS-UNNEEDED reachable only by an interval wholly above 0 (D_N >= about"
                " 0.86pp); CELLS-ADD reachable at |D_N| >= about 1.2pp")
PRED_DN = (-0.015, 0.008)
PRED_ALL = (-0.002, 0.022)
PRED_TS = (-0.005, 0.030)
PROB_KN1 = (("CELLS-ADD", 0.15), ("CELLS-UNNEEDED", 0.15), ("UNDETERMINED", 0.70))
HIT = Counter()


def hit(name):
    HIT[name] += 1


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ── kNN machinery (R2, R3) ─────────────────────────────────────────────────────────────────────────────────────────────

def neighbours(XE, XT, src_e, src_t, restrict, kp, chunk=512):
    """-> (NE, kp) TRAIN row indices (into XT) by descending cosine, ties to the smaller row (stable sort); -1 padded."""
    NE = XE.shape[0]
    out = np.full((NE, kp), -1, dtype=np.int64)
    if restrict:
        for s in sorted(set(src_e)):
            ei = np.flatnonzero(src_e == s)
            ti = np.flatnonzero(src_t == s)
            if not len(ti):
                refuse("[KNN-SRC] EVAL items of source %s have no TRAIN neighbour" % s)
            for a in range(0, len(ei), chunk):
                e = ei[a:a + chunk]
                S = XE[e] @ XT[ti].T
                o = np.argsort(-S, axis=1, kind="stable")[:, :kp]
                out[e, :o.shape[1]] = ti[o]
    else:
        for a in range(0, NE, chunk):
            S = XE[a:a + chunk] @ XT.T
            o = np.argsort(-S, axis=1, kind="stable")[:, :kp]
            out[a:a + chunk, :o.shape[1]] = o
    return out


def knn_choose(nbr, AT, wt, k, gb):
    """R2 / R3: per EVAL row, the routed model under TRAIN multiplicities wt (over XT rows); -> (model, backoff, short)."""
    kp = min(nbr.shape[1], 3 * k)
    idx = nbr[:, :kp]
    valid = idx >= 0
    safe = np.where(valid, idx, 0)
    w = np.where(valid, wt[safe], 0).astype(np.float64)
    prev = np.cumsum(w, axis=1) - w
    take = np.clip(np.minimum(w, k - prev), 0.0, None)
    n = take.sum(axis=1)
    S = np.einsum("ij,ijm->im", take, AT[safe].astype(np.float64))
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = S / n[:, None]
    mean = np.where(n[:, None] > 0, mean, 0.0)
    lead = np.argmax(mean, axis=1)
    r = np.arange(len(lead))
    p1 = mean[r, lead]
    p2 = np.sort(mean, axis=1)[:, -2] if mean.shape[1] > 1 else np.zeros(len(lead))
    with np.errstate(invalid="ignore", divide="ignore"):
        se = np.sqrt(np.clip(p1 * (1.0 - p1), 0.0, None) / np.where(n > 0, n, 1.0))
    back = (n <= 0) | ((p1 - p2) < se)
    return np.where(back, gb, lead), back, int((n < k).sum())


def ts_cells(D, AT, nbr_all, k, ts_k, seed):
    """R6: one TS seed -> grouping over all scored positions (TRAIN: k-means label or the zero cell; EVAL: majority of its k
    unrestricted neighbours' TS cells, ties -> the smaller cell)."""
    X = AT.astype(np.float64)
    zero = X.sum(axis=1) == 0
    if int((~zero).sum()) < ts_k:
        refuse("[TS] %d non-zero correctness vectors < k %d" % (int((~zero).sum()), ts_k))
    r, _t = U.GB.ukm_fit(U.GC.FM.unit_rows(X[~zero]), ts_k, seed)
    lab_t = np.full(len(X), ts_k, dtype=np.int64)
    lab_t[~zero] = r["labels"]
    g = np.full(D.n, -1, dtype=np.int64)
    g[D.T] = lab_t
    top = nbr_all[:, :k]
    for j, e in enumerate(D.E):
        nb = top[j][top[j] >= 0]
        cnt = np.bincount(lab_t[nb], minlength=ts_k + 1)
        g[e] = int(np.argmax(cnt))
    return g, ts_k + 1


def kn1_verdict(dn, spread, delta):
    add = dn["hi"] < 0 and abs(dn["point"]) > spread
    tost = dn["lo90"] > -delta and dn["hi90"] < delta
    unneeded = tost or dn["lo"] > 0
    if add and unneeded:
        hit("REFUSE.OVERLAP")
        refuse("[KN1-OVERLAP] CELLS-ADD and CELLS-UNNEEDED both hold on these data (spread_K %.5f < delta %.3f): a registration"
               " defect for the registrar; no word is chosen" % (spread, delta))
    if add:
        return "CELLS-ADD", tost
    if unneeded:
        return "CELLS-UNNEEDED", tost
    return "UNDETERMINED", tost


def kn_lines(st):
    L = []
    dn, c = st["dn"], reg()
    kd = c["k_decide"]
    L.append("=== KNN-ROUTE KN1 (%s) ===" % REG_TEXT)
    L.append("DENOMINATOR: %d EVAL items in %d components (Kish mean cluster size %.3f; Support (a) 5907 / 5404); neighbour pool TRAIN"
             " %d scored items (R1; the registration names %s bundle TRAIN rows: a difference of %+d)" % (
                 dn["n"], st["comp"], st["kish"], st["n_train"], "{:,}".format(c["n_train_reg"]), st["n_train"] - c["n_train_reg"]))
    L.append("LIKE WITH LIKE: KNN-SC (deciding) [SC] vs AF-U [SC] | K_0 [SC] descriptive | KNN-ALL [LF] floor only (cross vs AF-U) |"
             " TS [TS] correctness-built ceiling, never ranked | declared [DECL] reference")
    L.append("G_AF = acc(AF-U) - acc(best single) = %s (%+.5f)" % (U.pp(st["g_af"]), st["g_af"]))
    for k in c["ks"]:
        L.append("  KNN-SC k %3d: G = %s (%+.5f); backoff share %.4f | KNN-ALL k %3d: G = %s (%+.5f); backoff share %.4f%s" % (
            k, U.pp(st["g_sc"][k]), st["g_sc"][k], st["bo_sc"][k], k, U.pp(st["g_all"][k]), st["g_all"][k], st["bo_all"][k],
            "  <- DECIDING (SC)" if k == kd else ""))
    L.append("  KNN-SC sources with fewer than k TRAIN items: %s" % (st["short_src"] or "none"))
    L.append("  two-stage replicates whose 3k-entry neighbour list carried less than k TRAIN weight: SC %d, ALL %d (of %d x %d item-replicates)" % (
        st["short_rep"][0], st["short_rep"][1], st["B"], dn["n"]))
    L.append("K_s (per-source k-means, seeds 0-4): G_K,s = %s; spread_K = max - min = %.5f (UNION-AF-ROUTE printed 0.58pp)" % (
        " / ".join(U.pp(x) for x in st["gk"]), st["spread"]))
    L.append("KN1 (DECIDING): D_N = G_KNN-SC(k %d) - G_AF = %s (%+.5f) | two-stage 95%% [%+.5f, %+.5f] | 90%% [%+.5f, %+.5f] | percentile"
             " [%+.5f, %+.5f]" % (kd, U.pp(dn["point"]), dn["point"], dn["lo"], dn["hi"], dn["lo90"], dn["hi90"], dn["pct"][0], dn["pct"][1]))
    reach = c["delta"] - 1.645 * dn["se2"]
    L.append("  support D_N: n %d, SE_2stage %.5f (registered 0.0044), i.i.d. SE %.5f, DEFF %.3f (registered 2.867, transported), n_eff"
             " %.0f (registered 2060), MDE80 %s (registered +1.23pp); TOST reach %+.5f (%s); verdict line of record: %s" % (
                 dn["n"], dn["se2"], dn["se_iid"], dn["deff"], dn["n_eff"], U.pp(dn["mde"]), reach,
                 "TOST branch UNREACHABLE at this SE" if reach <= 0 else "TOST branch reachable", VERDICT_LINE))
    v, tost = kn1_verdict(dn, st["spread"], c["delta"])
    if v == "CELLS-ADD":
        hit("KN1.ADD")
        L.append("  KN1 -> CELLS-ADD (95%% interval wholly below 0 AND |D_N| %.5f > spread_K %.5f)" % (abs(dn["point"]), st["spread"]))
    elif v == "CELLS-UNNEEDED":
        hit("KN1.UNNEEDED_TOST" if tost else "KN1.UNNEEDED_ABOVE")
        L.append("  KN1 -> CELLS-UNNEEDED (%s)" % ("the 90%% interval lies inside +-%.1fpp (TOST)" % (100 * c["delta"]) if tost else
                                                   "the 95% interval lies wholly above 0"))
    else:
        hit("KN1.UNDETERMINED")
        L.append("  KN1 -> UNDETERMINED (neither CELLS-ADD: hi95 < 0 and |D_N| > spread_K; nor CELLS-UNNEEDED: TOST inside +-0.5pp or"
                 " lo95 > 0); reads 'not shown'")
    if dn["hi"] < 0:
        hit("RULE8.REFUTED")
        L.append("RULE 8: CELLS-UNNEEDED is REFUTED (D_N's 95% interval lies wholly below 0)")
    else:
        hit("RULE8.NOT")
        L.append("RULE 8: CELLS-UNNEEDED is not refuted (the 95% interval does not lie wholly below 0)")
    if v == "CELLS-UNNEEDED":
        hit("FKN.FIRED")
        L.append("FALSIFIER F-KN: FIRES (KN1 CELLS-UNNEEDED): framework change 4's 'route on tree or k-means cells' loses its cell premise"
                 " (neighbourhoods route as well); the framework's value moves to reporting and filing discipline")
    else:
        hit("FKN.NOT")
        L.append("FALSIFIER F-KN: NOT FIRED (KN1 %s; F-KN fires iff KN1 CELLS-UNNEEDED)" % v)
    L.append("DESCRIPTIVE: G_KNN-ALL(k %d) = %s | two-stage 95%% [%s, %s] (floor; [LF], cross against AF-U)" % (
        kd, U.pp(st["g_all"][kd]), U.pp(st["all_ci"]["lo"]), U.pp(st["all_ci"]["hi"])))
    L.append("DESCRIPTIVE (CEILING, never ranked): TS (correctness-pattern cells, k %d, seeds 0-4): TS - G_declared = %s; mean %s" % (
        c["ts_k"], " / ".join(U.pp(x) for x in st["ts"]), U.pp(st["ts_mean"])))
    for lab, x, band in (("P1 D_N -0.3pp [-1.5, +0.8]", dn["point"], PRED_DN), ("P2 G_KNN-ALL +1.0pp [-0.2, +2.2] (descriptive)", st["g_all"][kd], PRED_ALL),
                         ("P3 TS - G_declared +1.0pp [-0.5, +3.0] (ceiling, descriptive)", st["ts_mean"], PRED_TS)):
        ok = U.in_band(x, band)
        hit("PRED.HELD" if ok else "PRED.FAILED")
        L.append("PREDICTION %s: observed %+.5f -> %s" % (lab, x, "HELD" if ok else "FAILED"))
    L.append("PREDICTION P1 KN1 CELLS-ADD 0.15, CELLS-UNNEEDED 0.15, UNDETERMINED 0.70: observed %s; Brier %.4f" % (v, U.brier(PROB_KN1, v)))
    L.append("WORDS: AF-U and KNN-SC are SOURCE-CONDITIONED [SC]; KNN-ALL is the only [LF] arm and is a floor, cross against AF-U; TS is"
             " built from correctness [TS] and is never ranked; key-scored, no judge verdict (no wrong(established), no convention A / B)")
    L.append("WILL NOT SHOW (registered): a label-free routing result against AF-U (KNN-ALL is cross); a ranking against the [TS]"
             " ceiling; other corpora, rosters or draws")
    return L, dict(KN1=v, F_KN=(v == "CELLS-UNNEEDED"), RULE8=bool(dn["hi"] < 0), TOST=bool(tost))


def denominators(say):
    c = reg()
    say("DENOMINATORS (registered Support (a)): %d EVAL items in %d components (Kish 1.09); DEFF 2.867 (UNION-AF-ROUTE U2 D_K two-stage,"
        " transported), n_eff 2,060, SE 0.44pp, MDE80 1.23pp; %s" % (c["n_route"], c["comp_route"], VERDICT_LINE))
    say("PLANNED: B = %d two-stage replicates (default_rng(%d)); k in %s, k = %d deciding; TOST delta %.1fpp; TS k %d seeds %s;"
        " registration's TRAIN 12,334 keyed rows vs the scored TRAIN pool (R1, printed in --run)" % (
            c["B"], c["seed"], "{%s}" % ", ".join(str(k) for k in c["ks"]), c["k_decide"], 100 * c["delta"], c["ts_k"],
            "-".join(str(s) for s in (c["ts_seeds"][0], c["ts_seeds"][-1]))))
    say("IDENTITY TARGETS (UNION-AF-ROUTE outcome sha256 %s): %s" % (c["uar_outcome_sha"][:16], U.identity_text(c["identity"])))


def dry_run(out=print):
    say = out
    U.header(say, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__), U.__file__] + [os.path.join(HERE, n) for n, _ in U.PINS])
    denominators(say)
    S = U.prepare(say, reg(), refuse, hit)
    cfg = U.UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(U.UAR.reg()["policy"])
    U.read_views(cfg, say, True, S["af"], S["kx"], reg()["marker"], None, refuse, hit, tag=TEST_ID)
    say("OUTPUTS (write-once, never committed): %s, %s" % (reg()["out"], reg()["marker"]))
    say("DRY-RUN: nothing written; no EVAL key read; no vector read; no statistic of EVAL printed.")
    hit("DRY.DONE")
    return 0


def vectors(D, say):
    """R1: the unit vectors of every scored item through union_af_route's reader; EQUAL to the bundle's rows where present."""
    u = U.UAR.reg()
    ip = U.UAR.input_paths()
    b, _m = U.GC.load_bundle(U.P(ip["bundle"]), expect=(u["pool"], u["n_eval_before"], u["comp_before"]), sides=None)
    vec = U.UAR._TV[0](sorted(D.items), int(u["dim"]))
    miss = [i for i in D.items if i not in vec]
    if miss:
        refuse("[KNN-VEC] %d scored item(s) have no vector (first %s)" % (len(miss), miss[:3]))
    X = U.GC.FM.unit_rows(np.vstack([np.asarray(vec[i], dtype=np.float64) for i in D.items]))
    pos = {it: j for j, it in enumerate(D.items)}
    bi = [str(x) for x in b["eval_item"]] + [str(x) for x in b["train_item"]]
    BX = U.GC.FM.unit_rows(np.vstack([np.asarray(b["eval_X"], dtype=np.float64), np.asarray(b["train_X"], dtype=np.float64)]))
    n = bad = 0
    for j, it in enumerate(bi):
        if it in pos:
            n += 1
            bad += int(not np.allclose(X[pos[it]], BX[j], atol=1e-9))
    if bad:
        hit("REFUSE.VEC")
        refuse("[KNN-VEC] %d of %d vectors differ from the UNION-AF-ROUTE bundle's rows" % (bad, n))
    say("  vectors (R1): %d scored items, %d-d unit rows; %d of them in the UNION-AF-ROUTE bundle, every one EQUAL; %d read beside it"
        % (len(D.items), X.shape[1], n, len(D.items) - n))
    return X


def run(out=print):
    c = reg()
    lines = []

    def say(s_):
        lines.append(s_)
        out(s_)
    U.header(say, TEST_ID, "--run", REG_TEXT, [os.path.abspath(__file__), U.__file__] + [os.path.join(HERE, n) for n, _ in U.PINS])
    for p in (c["out"], c["marker"]):
        if os.path.exists(U.P(p)):
            hit("REFUSE.WRITE_ONCE")
            refuse("%s exists (write-once); refused before any read" % p)
    denominators(say)
    S = U.prepare(say, c, refuse, hit)
    cfg = U.UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(U.UAR.reg()["policy"])
    if int(cfg.reg["B"]) != int(c["B"]) or int(cfg.reg["seed"]) != int(c["seed"]):
        refuse("the reader's B / seed %s / %s are not the registered %s / %s" % (cfg.reg["B"], cfg.reg["seed"], c["B"], c["seed"]))
    D, ok_sha = U.read_views(cfg, say, False, S["af"], S["kx"], c["marker"],
                             "KNN-ROUTE: the EVAL key read started. frozen policy sha256 %s" % c["uar_policy_sha"], refuse, hit, tag=TEST_ID)
    n_comp = U.check_denominators(D, c, refuse, hit, "KNN")
    say("  scored: TRAIN %d, EVAL %d key-complete items in %d components" % (D.n_train, D.n_eval, n_comp))
    P0 = U.b3_check(D, cfg, S["pol"], refuse, hit)
    say("  B3: the point policy re-fitted beside EVAL equals the frozen file (best single %s; AF, K0..K4, TRUE source, TRUE source/domain)"
        % S["pol"]["best_single"])
    X = vectors(D, say)
    XT, XE = X[D.T], X[D.E]
    src = np.array(D.src)
    src_t, src_e = src[D.T], src[D.E]
    AT = D.A[D.T]
    kmax = 3 * max(c["ks"])
    nbr = dict(SC=neighbours(XE, XT, src_e, src_t, True, kmax), ALL=neighbours(XE, XT, src_e, src_t, False, kmax))
    tcount = Counter(src_t.tolist())
    short_src = ", ".join("%s %d" % (s, tcount[s]) for s in sorted(tcount) if tcount[s] < max(c["ks"]))
    AE = D.A[D.E]
    r = np.arange(len(D.E))
    kd = c["k_decide"]
    gt = D.groupings["tree"][0]
    rec = dict(sc=[], all=[], af=[], best=[], short=[0, 0])

    def hook(D_, wt, v):
        Pp = V_fit(D_, wt)
        wtt = wt[D_.T]
        msc, _b1, s1 = knn_choose(nbr["SC"], AT, wtt, kd, Pp.gb)
        mal, _b2, s2 = knn_choose(nbr["ALL"], AT, wtt, kd, Pp.gb)
        rec["short"][0] += s1
        rec["short"][1] += s2
        v = np.asarray(v, dtype=np.float64)
        tot = v.sum()
        pa = Pp.pol["tree"][gt[D_.E]]
        pa = np.where(pa < 0, Pp.gb, pa)
        rec["sc"].append(float(v @ AE[r, msc]) / tot)
        rec["all"].append(float(v @ AE[r, mal]) / tot)
        rec["af"].append(float(v @ AE[r, pa]) / tot)
        rec["best"].append(float(v @ AE[r, Pp.gb]) / tot)
    bt = U.V.run_boot(D, c["B"], c["seed"], hook=hook)
    if D.fit_asserts != 2 * c["B"] + 2:
        refuse("[G3] %d fit checks executed, not %d" % (D.fit_asserts, 2 * c["B"] + 2))
    chk = np.stack([np.asarray(rec["best"]), np.asarray(rec["af"])], axis=1)
    ref = np.stack([bt["two"][:, 0, U.V.BS], bt["two"][:, 0, U.V.TREE]], axis=1)
    if chk.shape != ref.shape or not np.allclose(chk, ref, atol=1e-12, rtol=0):
        hit("REFUSE.HOOK")
        refuse("[KNN-HOOK] the hook's re-fitted accuracies differ from run_boot's own arms")
    ok, got = U.identity(bt, D, c["identity"])
    if not ok:
        hit("REFUSE.IDENTITY")
        refuse("[KNN-IDENTITY] %s is not UNION-AF-ROUTE's %s" % (U.identity_text(got), U.identity_text(c["identity"])))
    say("IDENTITY: %s -> REPRODUCED (UNION-AF-ROUTE's printed digits)" % U.identity_text(got))
    hit("IDENTITY.OK")
    ones = np.ones(len(D.T))
    best = float(bt["point"][0, U.V.BS])
    acc = {}
    st = dict(comp=n_comp, kish=U.kish_eval(D), n_train=D.n_train, B=c["B"], g_sc={}, g_all={}, bo_sc={}, bo_all={},
              short_src=short_src, short_rep=tuple(rec["short"]))
    for k in c["ks"]:
        for arm, key in (("SC", "sc"), ("ALL", "all")):
            m_, bo, _s = knn_choose(nbr[arm], AT, ones, k, P0.gb)
            acc[(arm, k)] = AE[r, m_].astype(np.float64)
            st["g_" + key][k] = float(acc[(arm, k)].mean()) - best
            st["bo_" + key][k] = float(bo.mean())
    st["g_af"] = float(bt["point"][0, U.V.TREE]) - best
    st["gk"] = [float(bt["point"][0, U.karm(D, nm)]) - best for nm in U.KNAMES]
    st["spread"] = max(st["gk"]) - min(st["gk"])
    pa0 = P0.pol["tree"][gt[D.E]]
    caf = AE[r, np.where(pa0 < 0, P0.gb, pa0)].astype(np.float64)
    two = np.asarray(rec["sc"]) - np.asarray(rec["af"])
    iid = [float(v @ (acc[("SC", kd)] - caf)) / v.sum() for v in U.iid_weights(c["seed"], len(D.E), c["B"])]
    st["dn"] = U.interval(float(acc[("SC", kd)].mean() - caf.mean()), two, iid, len(D.E))
    two_all = np.asarray(rec["all"]) - np.asarray(rec["best"])
    iid_all = [float(v @ (acc[("ALL", kd)] - AE[r, P0.gb])) / v.sum() for v in U.iid_weights(c["seed"], len(D.E), c["B"])]
    st["all_ci"] = U.interval(st["g_all"][kd], two_all, iid_all, len(D.E))
    tdom = float(bt["point"][0, U.V.TDOM])
    ts = []
    for sd in c["ts_seeds"]:
        g, ng = ts_cells(D, AT, nbr["ALL"], kd, c["ts_k"], sd)
        pol, gb = U.point_fit(D, g, ng)
        ts.append(float(U.routed_correct(D, pol, gb, g).mean()) - tdom)
    st["ts"], st["ts_mean"] = ts, float(np.mean(ts))
    L, words = kn_lines(st)
    for ln in L:
        say(ln)
    U.write_outcome(c["out"], "\n".join(lines) + "\n", ok_sha, refuse, out)
    hit("RUN.DONE")
    return dict(st=st, words=words, D=D, bt=bt, X=X, nbr=nbr)


def V_fit(D_, wt):
    return U.V.fit(D_, wt)


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    gr = ap.add_mutually_exclusive_group(required=True)
    gr.add_argument("--selftest", action="store_true")
    gr.add_argument("--mutants", action="store_true")
    gr.add_argument("--dry-run", action="store_true")
    gr.add_argument("--run", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--data-root", default=None, help="the checkout whose results / views / caches are read (set before any import)")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest(only=a.only)
        return 0
    if a.mutants:
        return U.run_mutants(os.path.abspath(__file__), "knn_route", MUTANTS, TAG, only=a.only)
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    if a.dry_run:
        return dry_run(out=out)
    run(out=out)
    return 0


# ══ SELFTEST ══════════════════════════════════════════════════════════════════════════════════════════════════════════

BRANCHES = ("KN1.ADD", "KN1.UNNEEDED_TOST", "KN1.UNNEEDED_ABOVE", "KN1.UNDETERMINED", "RULE8.REFUTED", "RULE8.NOT", "FKN.FIRED",
            "FKN.NOT", "PRED.HELD", "PRED.FAILED", "IDENTITY.OK", "RUN.DONE", "DRY.DONE", "MARKER.WRITTEN", "REFUSE.WRITE_ONCE",
            "REFUSE.POOL", "REFUSE.POLICY_SHA", "REFUSE.MANIFEST", "REFUSE.DENOM", "REFUSE.IDENTITY", "REFUSE.B3", "REFUSE.VEC",
            "REFUSE.HOOK", "REFUSE.OVERLAP")
need = U.need


def _me():
    return types.SimpleNamespace(_REG=_REG, REG=REG, FIXTURE_REG=FIXTURE_REG)


def _dn(pt, lo, hi, se2=None, lo90=None, hi90=None):
    se2 = se2 if se2 is not None else (hi - lo) / 3.92
    return dict(point=pt, lo=lo, hi=hi, lo90=pt - 1.645 * se2 if lo90 is None else lo90, hi90=pt + 1.645 * se2 if hi90 is None else hi90,
                pct=(lo, hi), se2=se2, se_iid=se2 / 1.7, deff=2.9, n_eff=2037.0, mde=2.8 * se2, n=5907)


def _syn(dn=None, spread=0.0058, g_all=0.010, ts=0.01):
    ks = REG["ks"]
    return dict(comp=5404, kish=1.09, n_train=11841, B=2000, dn=dn or _dn(-0.003, -0.0116, 0.0056), spread=spread,
                g_af=0.0152, g_sc={k: 0.012 for k in ks}, g_all={k: g_all for k in ks}, bo_sc={k: 0.1 for k in ks},
                bo_all={k: 0.1 for k in ks}, short_src="", short_rep=(0, 0), gk=[0.022, 0.018, 0.0164, 0.021, 0.0213],
                all_ci=dict(lo=g_all - 0.01, hi=g_all + 0.01), ts=[ts] * 5, ts_mean=ts)


def st_branches():
    B_ = {"CELLS-ADD": 0.7225 + 0.0225 + 0.49, "CELLS-UNNEEDED": 0.0225 + 0.7225 + 0.49, "UNDETERMINED": 0.0225 + 0.0225 + 0.09}
    cases = [(_dn(-0.012, -0.020, -0.004), 0.0058, "CELLS-ADD", False),
             (_dn(-0.012, -0.020, 0.0), 0.0058, "UNDETERMINED", False),             # hi95 exactly 0: not wholly below
             (_dn(-0.0058, -0.010, -0.001), 0.0058, "UNDETERMINED", False),         # |D_N| exactly spread_K: not above it
             (_dn(-0.0059, -0.010, -0.001), 0.0058, "CELLS-ADD", False),
             (_dn(0.009, 0.001, 0.017), 0.0058, "CELLS-UNNEEDED", False),           # wholly above 0
             (_dn(0.009, 0.0, 0.017), 0.0058, "UNDETERMINED", False),               # lo95 exactly 0
             (_dn(0.0, -0.0058, 0.0058, lo90=-0.0049, hi90=0.0049), 0.0058, "CELLS-UNNEEDED", True),
             (_dn(0.0, -0.0058, 0.0058, lo90=-0.005, hi90=0.0049), 0.0058, "UNDETERMINED", False),    # lo90 exactly -0.5pp: not inside
             (_dn(0.0, -0.0058, 0.0058, lo90=-0.0049, hi90=0.005), 0.0058, "UNDETERMINED", False),    # hi90 exactly +0.5pp: not inside
             (_dn(-0.002, -0.0045, -0.0001, lo90=-0.0041, hi90=-0.0002), 0.0058, "CELLS-UNNEEDED", True),  # below 0 but TOST: no ADD (|D_N| < spread)
             (_dn(0.001, -0.004, 0.006), 0.0058, "UNDETERMINED", False)]
    for dn, spread, want, tost in cases:
        L, w = kn_lines(_syn(dn=dn, spread=spread))
        t = "\n".join(L)
        assert w["KN1"] == want, (dn, w)
        if want == "CELLS-UNNEEDED":
            assert w["TOST"] is tost, (dn, w)
        need(t, "  KN1 -> %s" % want, "verdict line of record: " + VERDICT_LINE, "two-stage 95%% [%+.5f, %+.5f]" % (dn["lo"], dn["hi"]),
             "PREDICTION P1 KN1 CELLS-ADD 0.15, CELLS-UNNEEDED 0.15, UNDETERMINED 0.70: observed %s; Brier %.4f" % (want, B_[want]),
             "WILL NOT SHOW (registered)", "DENOMINATOR: 5907 EVAL items in 5404 components", "support D_N: n 5907", "[TS]", "[LF]",
             "spread_K = max - min = %.5f" % spread)
        need(t, "RULE 8: CELLS-UNNEEDED is REFUTED" if dn["hi"] < 0 else "RULE 8: CELLS-UNNEEDED is not refuted")
        assert w["RULE8"] is bool(dn["hi"] < 0)
        if want == "CELLS-UNNEEDED":
            assert w["F_KN"] is True
            need(t, "FALSIFIER F-KN: FIRES (KN1 CELLS-UNNEEDED)",
                 "(the 90% interval lies inside +-0.5pp (TOST))" if tost else "(the 95% interval lies wholly above 0)")
        else:
            assert w["F_KN"] is False
            need(t, "FALSIFIER F-KN: NOT FIRED (KN1 %s; F-KN fires iff KN1 CELLS-UNNEEDED)" % want)
    # the overlap is refused, never resolved: spread_K below delta with a tight interval below 0 inside +-0.5pp
    try:
        kn_lines(_syn(dn=_dn(-0.004, -0.0045, -0.0035, se2=0.0002), spread=0.003))
        raise AssertionError("no [KN1-OVERLAP] refusal")
    except SystemExit as e:
        assert "[KN1-OVERLAP]" in str(e), e
    for d_, want in ((-0.015, "HELD"), (0.008, "HELD"), (-0.0151, "FAILED"), (0.0081, "FAILED")):
        need("\n".join(kn_lines(_syn(dn=_dn(d_, d_ - 0.009, d_ + 0.009)))[0]), "PREDICTION P1 D_N -0.3pp [-1.5, +0.8]: observed %+.5f -> %s" % (d_, want))
    for g_, want in ((-0.002, "HELD"), (0.022, "HELD"), (-0.0021, "FAILED"), (0.0221, "FAILED")):
        need("\n".join(kn_lines(_syn(g_all=g_))[0]), "PREDICTION P2 G_KNN-ALL +1.0pp [-0.2, +2.2] (descriptive): observed %+.5f -> %s" % (g_, want))
    for g_, want in ((-0.005, "HELD"), (0.030, "HELD"), (-0.0051, "FAILED"), (0.0301, "FAILED")):
        need("\n".join(kn_lines(_syn(ts=g_))[0]), "PREDICTION P3 TS - G_declared +1.0pp [-0.5, +3.0] (ceiling, descriptive): observed %+.5f -> %s" % (g_, want))
    t = "\n".join(kn_lines(_syn())[0])
    need(t, "KNN-SC k  50: G = +1.20pp (+0.01200); backoff share 0.1000 | KNN-ALL k  50: G = +1.00pp", "<- DECIDING (SC)",
         "TOST reach -0.00222 (TOST branch UNREACHABLE at this SE)", "neighbour pool TRAIN 11841 scored items (R1; the registration names 12,334 bundle TRAIN rows: a difference of -493)")


def _o_choose(order, val_rows, k, w, mu, best):
    """Plain loops: walk the neighbour order with multiplicities capped at k; leader / runner-up / SE backoff (R2, R3)."""
    tot = {m_: 0.0 for m_ in mu}
    n = 0.0
    for it in order[:3 * k]:
        if n >= k:
            break
        t = min(w.get(it, 0), k - n)
        if t <= 0:
            continue
        n += t
        for m_ in mu:
            tot[m_] += t * val_rows[(it, m_)]
    if n == 0:
        return best, True
    means = [tot[m_] / n for m_ in mu]
    lead = max(range(len(mu)), key=lambda j: (means[j], -j))
    p1 = means[lead]
    p2 = sorted(means)[-2]
    se = (p1 * (1 - p1) / n) ** 0.5
    return (best, True) if (p1 - p2) < se else (mu[lead], False)


def st_units():
    rs = np.random.RandomState(7)
    mu = ["a", "b", "c"]
    tr = ["t%02d" % j for j in range(12)]
    val = {(t, m_): int(rs.rand() < (0.3 + 0.2 * mu.index(m_))) for t in tr for m_ in mu}
    AT = np.array([[val[(t, m_)] for m_ in mu] for t in tr])
    for trial in range(60):
        k = int(rs.randint(1, 6))
        order = list(rs.permutation(len(tr)))
        nbr = np.array([order + [-1] * 3], dtype=np.int64)
        wt = rs.randint(0, 3, len(tr)).astype(np.int64)
        m_, bo, _s = knn_choose(nbr, AT, wt, k, 1)
        om, ob = _o_choose([tr[j] for j in order], val, k, {tr[j]: int(wt[j]) for j in range(len(tr))}, mu, "b")
        assert mu[int(m_[0])] == om and bool(bo[0]) == ob, (trial, k, m_, om, bo, ob)
    # ties to the first model; a margin exactly one SE is NOT below it (no backoff); a short list uses what it has
    one = np.ones(4, dtype=np.int64)
    AT2 = np.array([[1, 1, 0], [1, 1, 0], [0, 1, 0], [1, 0, 0]])
    m_, bo, s = knn_choose(np.array([[0, 1, -1, -1]]), AT2, one, 2, 2)
    assert int(m_[0]) == 0 and not bo[0] and s == 0          # means (1, 1, 0): tie -> the first model; SE 0, margin 0 not < 0
    m_, bo, s = knn_choose(np.array([[0, 2, -1, -1]]), AT2, one, 2, 2)
    assert int(m_[0]) == 1 and not bo[0]                      # means (0.5, 1, 0): leader 1
    AT3 = np.array([[1, 1, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0]])
    m_, bo, s = knn_choose(np.array([[0, 1, 2, 3]]), AT3, one, 4, 2)
    assert int(m_[0]) == 0 and not bo[0]                      # means (.5, .25, 0): margin .25 == SE .25 is NOT below it
    AT4 = np.array([[1, 1, 0], [1, 1, 0], [0, 0, 0], [0, 0, 0]])
    m_, bo, s = knn_choose(np.array([[0, 1, 2, 3]]), AT4, one, 4, 2)
    assert int(m_[0]) == 2 and bo[0]                          # means (.5, .5, 0): margin 0 < SE .25 -> the best single (2)
    AT5 = np.array([[1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 1, 0]])
    m_, bo, s = knn_choose(np.array([[0, 1, 2, 3]]), AT5, np.array([3, 0, 5, 5]), 4, 2)
    assert int(m_[0]) == 0 and not bo[0] and s == 0           # multiplicities 3, 0, 5 capped to 3, 0, 1: means (.75, .25, 0)
    m_, bo, s = knn_choose(np.array([[0, -1, -1, -1]]), AT2, one, 2, 2)
    assert s == 1


def _oracle(lay, res):
    fx, D = lay.fx, res["D"]
    c = dict(REG, **dict(lay.common, **FIXTURE_REG))
    mu, val = U.o_key(fx.spec)
    tr = [D.items[k] for k in D.T]
    ev = [D.items[k] for k in D.E]
    vec = {i: np.asarray(fx.vec[i], float) / np.linalg.norm(fx.vec[i]) for i in tr + ev}
    src = {i: fx.strata[i][0] for i in tr + ev}
    man = U.json.load(open(os.path.join(lay.tmp, "res", "inputs", "inputs_manifest.json"), encoding="utf-8"))
    af, _ = U.V.load_tree_cells(os.path.join(lay.tmp, "res", "inputs", "af_cells.tsv"), man["inputs"]["res/inputs/af_cells.tsv"])
    best, paf = U.o_fit(tr, af, val, mu)
    tpos = {t: j for j, t in enumerate(tr)}
    orders = {}
    for arm in ("SC", "ALL"):
        for e in ev:
            cand = [t for t in tr if arm == "ALL" or src[t] == src[e]]
            orders[(arm, e)] = sorted(cand, key=lambda t: (-float(np.dot(vec[e], vec[t])), tpos[t]))
    o = dict(acc={}, best=U.o_acc(ev, af, val, best, {}), af=U.o_acc(ev, af, val, best, paf))
    w1 = {t: 1 for t in tr}
    for k in c["ks"]:
        for arm in ("SC", "ALL"):
            ch = {e: _o_choose(orders[(arm, e)], val, k, w1, mu, best)[0] for e in ev}
            o["acc"][(arm, k)] = sum(val[(e, ch[e])] for e in ev) / len(ev)
    kd = c["k_decide"]
    rng = np.random.default_rng(c["seed"])
    reps = []
    for _b in range(c["B"]):
        wt = np.zeros(D.n, dtype=np.int64)
        wt[D.T] = U.V.draw_units(rng, D.train_units)
        v = U.V.draw_units(rng, D.eval_units)
        w = {D.items[k]: int(wt[k]) for k in D.T}
        vv = {D.items[k]: float(v[j]) for j, k in enumerate(D.E)}
        b_, pa_ = U.o_fit(tr, af, val, mu, w)
        ch = {e: _o_choose(orders[("SC", e)], val, kd, w, mu, b_)[0] for e in ev}
        totv = sum(vv.values())
        reps.append(sum(vv[e] * val[(e, ch[e])] for e in ev) / totv - U.o_acc(ev, af, val, b_, pa_, vv))
    o["dn_se2"] = float(np.std(reps, ddof=1))
    ch = {e: _o_choose(orders[("SC", e)], val, kd, w1, mu, best)[0] for e in ev}
    de = [val[(e, ch[e])] - val[(e, paf.get(af[e], best))] for e in ev]
    rng2 = np.random.default_rng(c["seed"])
    iid = []
    for _b in range(c["B"]):
        cnt = np.bincount(rng2.integers(0, len(ev), len(ev)), minlength=len(ev))
        iid.append(float(np.dot(cnt, de)) / cnt.sum())
    o["dn_iid"] = float(np.std(iid, ddof=1))
    # TS ceiling per seed (the k-means call itself is the module's; filing and policy by loops)
    o["ts"] = []
    tdom_cells = {i: fx.strata[i] for i in tr + ev}
    bd, pd_ = U.o_fit(tr, tdom_cells, val, mu)
    acc_decl = U.o_acc(ev, tdom_cells, val, bd, pd_)
    X = np.array([[val[(t, m_)] for m_ in mu] for t in tr], float)
    for sd in c["ts_seeds"]:
        nz = [j for j in range(len(tr)) if X[j].sum() > 0]
        r, _t = U.GB.ukm_fit(U.GC.FM.unit_rows(X[nz]), c["ts_k"], sd)
        lab = {t: c["ts_k"] for t in tr}
        for jj, j in enumerate(nz):
            lab[tr[j]] = int(r["labels"][jj])
        cell = dict(lab)
        for e in ev:
            cnt = Counter(lab[t] for t in orders[("ALL", e)][:kd])
            cell[e] = max(sorted(cnt), key=lambda x: (cnt[x], -x))
        b_, p_ = U.o_fit(tr, cell, val, mu)
        o["ts"].append(U.o_acc(ev, cell, val, b_, p_) - acc_decl)
    return o


def st_run_e2e(base, mk):
    lay = U.clone(base, mk())
    text, err, res = U.cap(_me(), run, lay)
    assert err is None, err
    outp = os.path.join(lay.tmp, "res", "knn", "outcome.txt")
    out = open(outp, encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL %s (KNN-ROUTE; --run" % U.POOL)
    assert os.path.isfile(os.path.join(lay.tmp, "res", "knn", "READ_STARTED"))
    o = _oracle(lay, res)
    c = dict(REG, **dict(lay.common, **FIXTURE_REG))
    for k in c["ks"]:
        gsc, gall = U.num(out, r"KNN-SC k +%d: G = \S+ \(([+-][0-9.]+)\);.*?KNN-ALL k +%d: G = \S+ \(([+-][0-9.]+)\)" % (k, k))
        assert abs(gsc - (o["acc"][("SC", k)] - o["best"])) < 6e-6, (k, gsc, o["acc"][("SC", k)] - o["best"])
        assert abs(gall - (o["acc"][("ALL", k)] - o["best"])) < 6e-6, (k, gall)
    assert len(set(round(o["acc"][("SC", k)], 6) for k in c["ks"])) > 1, "k does not discriminate on the fixture"
    assert len(set(round(o["acc"][("ALL", k)], 6) for k in c["ks"])) == len(c["ks"]), "KNN-ALL's k does not discriminate on the fixture"
    p2, = U.num(out, r"PREDICTION P2 G_KNN-ALL \+1.0pp \[-0.2, \+2.2\] \(descriptive\): observed ([+-][0-9.]+)")
    assert abs(p2 - (o["acc"][("ALL", c["k_decide"])] - o["best"])) < 6e-6, p2
    assert abs(o["acc"][("SC", 5)] - o["acc"][("ALL", 5)]) > 1e-4, "SC and ALL agree on the fixture"
    p_, lo, hi = U.num(out, r"D_N = G_KNN-SC\(k \d+\) - G_AF = \S+ \(([+-][0-9.]+)\) \| two-stage 95% \[([+-][0-9.]+), ([+-][0-9.]+)\]")
    se2, sei = U.num(out, r"support D_N: n \d+, SE_2stage ([0-9.]+) \(registered 0.0044\), i.i.d. SE ([0-9.]+),")
    assert abs(sei - o["dn_iid"]) < 6e-6, (sei, o["dn_iid"])
    lo9, hi9 = U.num(out, r"\| 90% \[([+-][0-9.]+), ([+-][0-9.]+)\]")
    assert abs(lo9 - (p_ - 1.645 * se2)) < 2e-5 and abs(hi9 - (p_ + 1.645 * se2)) < 2e-5, (lo9, hi9)
    want_dn = o["acc"][("SC", c["k_decide"])] - o["af"]
    assert abs(p_ - want_dn) < 6e-6 and abs(want_dn) > 1e-4, (p_, want_dn)
    assert abs(se2 - o["dn_se2"]) < 6e-6, (se2, o["dn_se2"])
    assert abs(lo - (want_dn - 1.96 * o["dn_se2"])) < 2e-5 and abs(hi - (want_dn + 1.96 * o["dn_se2"])) < 2e-5
    sp, = U.num(out, r"spread_K = max - min = ([0-9.]+)")
    gks = [float(x) / 100 for x in U.re.search(r"G_K,s = ([+-][0-9.]+)pp / ([+-][0-9.]+)pp / ([+-][0-9.]+)pp / ([+-][0-9.]+)pp / ([+-][0-9.]+)pp; spread_K", out).groups()]
    bt = res["bt"]
    want_gk = [float(bt["point"][0, U.karm(res["D"], nm)] - bt["point"][0, U.V.BS]) for nm in U.KNAMES]
    assert all(abs(a_ - b_) < 6e-5 for a_, b_ in zip(gks, want_gk)) and abs(sp - (max(want_gk) - min(want_gk))) < 6e-6, (gks, sp)
    assert sp > 1e-4, "spread_K is 0 on the fixture"
    ts = [float(x) / 100 for x in U.re.search(r"TS - G_declared = ([+-][0-9.]+)pp / ([+-][0-9.]+)pp / ([+-][0-9.]+)pp / ([+-][0-9.]+)pp / ([+-][0-9.]+)pp", out).groups()]
    for a_, b_ in zip(ts, o["ts"]):
        assert abs(a_ - b_) < 6e-5, (ts, o["ts"])
    v = "CELLS-ADD" if (hi < 0 and abs(p_) > sp) else ("CELLS-UNNEEDED" if (lo > 0 or (p_ - 1.645 * se2 > -0.005 and p_ + 1.645 * se2 < 0.005)) else "UNDETERMINED")
    need(out, "  KN1 -> %s" % v, "FALSIFIER F-KN: %s" % ("FIRES" if v == "CELLS-UNNEEDED" else "NOT FIRED"),
         "IDENTITY: %s -> REPRODUCED" % U.identity_text(lay.common["identity"]), "vectors (R1):")
    t2, err2, _r = U.cap(_me(), run, lay)
    assert err2 and "write-once" in err2, err2
    assert open(outp, encoding="utf-8").read() == out


def _no_outcome(lay):
    assert not os.path.exists(os.path.join(lay.tmp, "res", "knn", "outcome.txt")), "an outcome was written by a refusal"


def st_refusals(base, mk):
    import io
    import contextlib
    import route_source_null as RSN
    lay = U.clone(base, mk())
    saved = U.UAR._POOL[0]
    buf = io.StringIO()
    with U.mine(_me(), lay):
        U.UAR._POOL[0] = lambda pool: (1, "stub failure")
        try:
            with contextlib.redirect_stdout(buf):
                try:
                    run(out=lambda s: print(s))
                    err = None
                except SystemExit as e:
                    err = str(e)
        finally:
            U.UAR._POOL[0] = saved
    assert err and "B0-2 pool check failed" in err, err
    assert buf.getvalue().splitlines()[0].startswith("POOL ")
    _no_outcome(lay)
    for over, needle in ((dict(uar_policy_sha="0" * 64), "frozen TRAIN policy"), (dict(manifest_sha="0" * 64), "inputs manifest is sha256"),
                         (dict(n_route=lay.common["n_route"] + 1), "[KNN-DENOM]")):
        lay = U.clone(base, mk())
        _t, err, _r = U.cap(_me(), run, lay, **over)
        assert err and needle in err, (over, err)
        _no_outcome(lay)
    idn = lay.common["identity"]
    for k in ("best", "af"):
        lay = U.clone(base, mk())
        _t, err, _r = U.cap(_me(), run, lay, identity=dict(idn, **{k: idn[k][:-1] + str((int(idn[k][-1]) + 1) % 10)}))
        assert err and "[KNN-IDENTITY]" in err, err
        assert "KN1 (DECIDING" not in _t
        _no_outcome(lay)
    RSN.st_b3(base, mk, run, _me, _no_outcome)
    # a vector differing from the bundle's row
    lay = U.clone(base, mk())
    tr0 = sorted(i for i, (_c, s_) in lay.fx.side.items() if s_ == "TRAIN")[0]
    keep = lay.fx.vec[tr0]
    lay.fx.vec = dict(lay.fx.vec)
    lay.fx.vec[tr0] = -np.asarray(keep)
    _t, err, _r = U.cap(_me(), run, lay)
    assert err and "[KNN-VEC]" in err, err
    _no_outcome(lay)
    # the hook check: a replicate fit that differs from run_boot's
    lay = U.clone(base, mk())
    g = globals()
    real = g["V_fit"]
    calls = [0]

    def bad_fit(D_, wt):
        calls[0] += 1
        return real(D_, U.V.train_full(D_) if calls[0] == 2 else wt)
    g["V_fit"] = bad_fit
    try:
        _t, err, _r = U.cap(_me(), run, lay)
    finally:
        g["V_fit"] = real
    assert err and "[KNN-HOOK]" in err, err
    _no_outcome(lay)
    lay = U.clone(base, mk())
    os.makedirs(os.path.join(lay.tmp, "res", "knn"), exist_ok=True)
    open(os.path.join(lay.tmp, "res", "knn", "READ_STARTED"), "w").close()
    _t, err, _r = U.cap(_me(), run, lay)
    assert err and "write-once" in err, err
    _no_outcome(lay)


def st_dry_run(base, mk):
    lay = U.clone(base, mk())
    text, err, _r = U.cap(_me(), dry_run, lay)
    assert err is None, err
    assert text.splitlines()[0].startswith("POOL %s (KNN-ROUTE; --dry-run" % U.POOL)
    need(text, "NOT opened by --dry-run", "DRY-RUN: nothing written; no EVAL key read", "POOL CHECK (B0-2): rc 0")
    for bad in ("KN1 (DECIDING", "D_N =", "IDENTITY:", "PREDICTION", "vectors (R1)"):
        assert bad not in text, bad
    assert not os.path.exists(os.path.join(lay.tmp, "res", "knn"))
    L = []
    saved = _REG[0]
    _REG[0] = REG
    try:
        U.header(L.append, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__)])
        denominators(L.append)
    finally:
        _REG[0] = saved
    t = "\n".join(L)
    assert L[0].startswith("POOL pv2_1575de61bb20e977 (KNN-ROUTE; --dry-run"), L[0]
    need(t, "5907 EVAL items in 5404 components", "DEFF 2.867", "n_eff 2,060", "SE 0.44pp", "MDE80 1.23pp", VERDICT_LINE,
         "B = 2000 two-stage replicates (default_rng(42))", "k in {25, 50, 100}, k = 50 deciding", "TOST delta 0.5pp", "TS k 123 seeds 0-4",
         "best single 0.6049, TRUE source 0.6150, AF-U leaf cell 0.6201, K_s K0 0.6271; C1 +2.67pp [+1.46pp, +3.89pp]; G_AF +1.52pp [+0.14pp, +2.91pp]",
         "L24278-L24289", "calls 0")
    assert REG["out"] == "experiment_results/archv2/knn_route/outcome.txt" and REG["k_decide"] == 50 and REG["ts_k"] == 123


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print / refusal branches never executed: %s" % miss


CASES = (("branches", "KN1 words by value incl. end points, TOST / above branches, OVERLAP refusal, rule 8, F-KN, P1-P3 inclusive, Brier", "plain"),
         ("units", "knn_choose vs plain loops (multiplicities capped at k, ties, backoff strictly below one SE, short list)", "plain"),
         ("run_e2e", "--run end to end: KNN-SC / KNN-ALL at every k, D_N interval and SE, TS per seed vs an independent oracle; verdict by hand; write-once", "base"),
         ("refusals", "pool, manifest, policy sha, DENOM, IDENTITY, B3 (four arms), KNN-VEC, KNN-HOOK, marker exists; no outcome", "base"),
         ("dry_run", "--dry-run: POOL first, no statistic, nothing written; the REAL constants' lines", "base"),
         ("branch_cover", "every print / refusal branch executed", "plain"))
_FN = {"branches": st_branches, "units": st_units, "run_e2e": st_run_e2e, "refusals": st_refusals, "dry_run": st_dry_run,
       "branch_cover": st_branch_cover}


def selftest(only=None, quiet=False, base=None):
    return U.run_selftest(TAG, CASES, _FN, HIT, only=only, quiet=quiet, base=base)


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "S", "", ""),
    ("X01 CELLS-ADD at hi95 <= 0 (boundary)", "S", 'add = dn["hi"] < 0 and abs(dn["point"]) > spread', 'add = dn["hi"] <= 0 and abs(dn["point"]) > spread'),
    ("X02 CELLS-ADD at |D_N| >= spread_K (boundary)", "S", 'add = dn["hi"] < 0 and abs(dn["point"]) > spread', 'add = dn["hi"] < 0 and abs(dn["point"]) >= spread'),
    ("X03 CELLS-ADD without the spread clause", "S", 'add = dn["hi"] < 0 and abs(dn["point"]) > spread', 'add = dn["hi"] < 0'),
    ("X04 TOST end points inclusive", "S", 'tost = dn["lo90"] > -delta and dn["hi90"] < delta', 'tost = dn["lo90"] >= -delta and dn["hi90"] <= delta'),
    ("X05 TOST on the 95% interval", "S", 'tost = dn["lo90"] > -delta and dn["hi90"] < delta', 'tost = dn["lo"] > -delta and dn["hi"] < delta'),
    ("X06 CELLS-UNNEEDED at lo95 >= 0 (boundary)", "S", 'unneeded = tost or dn["lo"] > 0', 'unneeded = tost or dn["lo"] >= 0'),
    ("X07 overlap refusal removed (criterion substitution)", "S", '    if add and unneeded:' + NL + '        hit("REFUSE.OVERLAP")', '    if False:' + NL + '        hit("REFUSE.OVERLAP")'),
    ("X08 F-KN fires on any non-ADD word", "S", '    if v == "CELLS-UNNEEDED":' + NL + '        hit("FKN.FIRED")', '    if v != "CELLS-ADD":' + NL + '        hit("FKN.FIRED")'),
    ("X09 rule 8 at hi95 <= 0", "S", '    if dn["hi"] < 0:' + NL + '        hit("RULE8.REFUTED")', '    if dn["hi"] <= 0:' + NL + '        hit("RULE8.REFUTED")'),
    ("X10 backoff at margin <= SE (boundary)", "S", 'back = (n <= 0) | ((p1 - p2) < se)', 'back = (n <= 0) | ((p1 - p2) <= se)'),
    ("X11 backoff removed", "S", 'back = (n <= 0) | ((p1 - p2) < se)', 'back = (n <= 0)'),
    ("X12 runner-up = the leader", "S", 'p2 = np.sort(mean, axis=1)[:, -2]', 'p2 = np.sort(mean, axis=1)[:, -1]'),
    ("X13 SE of the runner-up's mean", "S", 'np.clip(p1 * (1.0 - p1), 0.0, None)', 'np.clip(p2 * (1.0 - p2), 0.0, None)'),
    ("X14 replicate kNN on the full TRAIN (uncapped fork: no refit)", "S", '        wtt = wt[D_.T]', '        wtt = np.ones(len(D_.T), dtype=np.int64)'),
    ("X15 multiplicities not capped at k", "S", 'take = np.clip(np.minimum(w, k - prev), 0.0, None)', 'take = w'),
    ("X16 SC neighbours = the farthest (min<->max)", "S", '                o = np.argsort(-S, axis=1, kind="stable")[:, :kp]', '                o = np.argsort(S, axis=1, kind="stable")[:, :kp]'),
    ("X17 SC not restricted to the source", "S", '            ti = np.flatnonzero(src_t == s)', '            ti = np.arange(len(src_t))'),
    ("X18 deciding k = the first k", "S", '    kd = c["k_decide"]' + NL + '    gt = ', '    kd = c["ks"][0]' + NL + '    gt = '),
    ("X19 D_N against the best single (wrong arm)", "S", 'U.interval(float(acc[("SC", kd)].mean() - caf.mean()), two, iid, len(D.E))', 'U.interval(float(acc[("SC", kd)].mean() - best), two, iid, len(D.E))'),
    ("X20 D_N replicates not paired with AF", "S", 'two = np.asarray(rec["sc"]) - np.asarray(rec["af"])', 'two = np.asarray(rec["sc"]) - np.asarray(rec["best"])'),
    ("X21 hook check skipped", "S", 'if chk.shape != ref.shape or not np.allclose(chk, ref, atol=1e-12, rtol=0):', 'if False:'),
    ("X22 spread_K = max - mean", "S", 'st["spread"] = max(st["gk"]) - min(st["gk"])', 'st["spread"] = max(st["gk"]) - float(np.mean(st["gk"]))'),
    ("X23 TS filed by the SC neighbours", "S", 'g, ng = ts_cells(D, AT, nbr["ALL"], kd, c["ts_k"], sd)', 'g, ng = ts_cells(D, AT, nbr["SC"], kd, c["ts_k"], sd)'),
    ("X24 TS zero vectors merged into cell 0", "S", 'lab_t = np.full(len(X), ts_k, dtype=np.int64)', 'lab_t = np.full(len(X), 0, dtype=np.int64)'),
    ("X25 TS majority = the first neighbour's cell", "S", '        g[e] = int(np.argmax(cnt))', '        g[e] = int(lab_t[nb[0]])'),
    ("X26 TS against the best single (wrong reference)", "S", 'ts.append(float(U.routed_correct(D, pol, gb, g).mean()) - tdom)', 'ts.append(float(U.routed_correct(D, pol, gb, g).mean()) - best)'),
    ("X27 TS every seed = seed 0", "S", 'g, ng = ts_cells(D, AT, nbr["ALL"], kd, c["ts_k"], sd)', 'g, ng = ts_cells(D, AT, nbr["ALL"], kd, c["ts_k"], c["ts_seeds"][0])'),
    ("X28 P2 read at the first k", "S", '("P2 G_KNN-ALL +1.0pp [-0.2, +2.2] (descriptive)", st["g_all"][kd], PRED_ALL)', '("P2 G_KNN-ALL +1.0pp [-0.2, +2.2] (descriptive)", st["g_all"][c["ks"][0]], PRED_ALL)'),
    ("X29 P3 read against P2's band", "S", 'st["ts_mean"], PRED_TS)', 'st["ts_mean"], PRED_ALL)'),
    ("X30 Brier on a fixed outcome", "S", 'U.brier(PROB_KN1, v)', 'U.brier(PROB_KN1, "UNDETERMINED")'),
    ("X31 verdict line of record dropped", "S", '"TOST branch reachable", VERDICT_LINE))', '"TOST branch reachable", ""))'),
    ("X32 F-KN NOT FIRED line dropped (skip path)", "S", '        L.append("FALSIFIER F-KN: NOT FIRED (KN1 %s; F-KN fires iff KN1 CELLS-UNNEEDED)" % v)', '        pass'),
    ("X33 identity refusal removed", "S", '    if not ok:' + NL + '        hit("REFUSE.IDENTITY")', '    if False:' + NL + '        hit("REFUSE.IDENTITY")'),
    ("X34 vector check skipped", "S", '    if bad:' + NL + '        hit("REFUSE.VEC")', '    if False:' + NL + '        hit("REFUSE.VEC")'),
    ("X35 pre-read write-once check removed", "S", '        if os.path.exists(U.P(p)):' + NL + '            hit("REFUSE.WRITE_ONCE")', '        if False:' + NL + '            hit("REFUSE.WRITE_ONCE")'),
    ("X36 TOST delta 1.0pp (not the registered 0.5pp)", "S", 'v, tost = kn1_verdict(dn, st["spread"], c["delta"])', 'v, tost = kn1_verdict(dn, st["spread"], 0.010)'),
    ("X37 i.i.d. replicates on another seed", "S", 'iid = [float(v @ (acc[("SC", kd)] - caf)) / v.sum() for v in U.iid_weights(c["seed"], len(D.E), c["B"])]', 'iid = [float(v @ (acc[("SC", kd)] - caf)) / v.sum() for v in U.iid_weights(c["seed"] + 1, len(D.E), c["B"])]'),
    ("X38 KNN-ALL restricted like SC", "S", 'ALL=neighbours(XE, XT, src_e, src_t, False, kmax)', 'ALL=neighbours(XE, XT, src_e, src_t, True, kmax)'),
    ("X39 the leader's tie to the LAST model", "S", '    lead = np.argmax(mean, axis=1)', '    lead = mean.shape[1] - 1 - np.argmax(mean[:, ::-1], axis=1)'),
    ("C20 95% interval with z 1.645", "C", 'lo=pt - z * se2, hi=pt + z * se2', 'lo=pt - 1.645 * se2, hi=pt + 1.645 * se2'),
    ("C21 interval from the i.i.d. SE", "C", '    v2, vi = V._var(two), V._var(iid)', '    v2, vi = V._var(iid), V._var(iid)'),
    ("C22 90% interval with z 1.96", "C", 'lo90=pt - 1.645 * se2, hi90=pt + 1.645 * se2', 'lo90=pt - 1.96 * se2, hi90=pt + 1.96 * se2'),
    ("C23 i.i.d. draws not item-level (EVAL size halved)", "C", '        yield np.bincount(rng.integers(0, NE, NE), minlength=NE).astype(np.float64)', '        yield np.bincount(rng.integers(0, NE, NE // 2), minlength=NE).astype(np.float64)'),
    ("C24 identity: arm digits not compared", "C", 'ok = all(got[k] == idn[k] for k in ("best", "tsrc", "af", "k0")) and', 'ok = True and'),
)


if __name__ == "__main__":
    sys.exit(main())
