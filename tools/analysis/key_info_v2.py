"""key_info_v2.py: KEY-INFO-V2 -- does knowing an item's AF-U cell predict which of the 18 models answer it correctly (Brier gain of
the TRAIN cell accuracy over the TRAIN marginal, summed over models), more than K_0 cells and more than random within-source cells?
ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A CPU reader (T3 of the testing-logic review).

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — KEY-INFO-V2: does knowing an item's AF-U cell
  predict which of the 18 models answer it correctly (LOO Brier gain over the marginal, summed over models), more than K_0 cells
  and more than random within-source cells? ..." (L24291-L24302, _as_of b66b075d): KI1, KI2, Support (a)-(g), P1-P3, F-KI,
  WILL-NOT-SHOW. Record L24259-L24263. Source: docs/literature/2026-10-04_testing_logic_review.md (bd5ca001) T3.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, plain form; never beside a construction: every step reads the pool):
  0. python tools/analysis/key_info_v2.py --selftest   # synthetic fixtures (temp on E: via scratch_dir); opens NO DB of record
     python tools/analysis/key_info_v2.py --mutants    # the mutant table, re-run (each must make the selftest fail)
  1. python tools/analysis/key_info_v2.py --dry-run    # POOL line first; pins; denominators; B0-2 pool check; inputs re-hashed;
                                                       #   frozen policy sha; NO key, NO statistic; writes nothing
  2. python tools/analysis/key_info_v2.py --run        # the TRAIN-half pre-pass (TRAIN key only, printed BEFORE the eval view
       opens), then ONE EVAL key read (marker first); outcome WRITE-ONCE: experiment_results/archv2/key_info_v2/outcome.txt
       (+ key_info_v2.READ_STARTED). Never committed: pin by sha256 and back up to E:/TaxoArena_backup_<date>_key_info_v2 with
       SHA256SUMS.txt (registration HYGIENE).
  --data-root <dir> (optional, every mode; set before any import). Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1)-(3) as route_source_null.py, with the TRAIN-half PRE-PASS between the TRAIN key and the eval view (R4); (4) run_boot (B 2,000,
  default_rng(42)) with a hook computing every arm's KI on the replicate (TRAIN multiplicities, EVAL component weights); the hook's
  best-single / AF accuracies (V.fit on the replicate) must equal run_boot's arms ([KI-HOOK]); [KI-IDENTITY] before any new
  number; (5) every point KI recomputed through F6's estimator free_tests_f4_f7.loo_imp (unchanged) and REFUSED unless equal to
  the vectorised form to 1e-9 ([KI-F6]), and the Murphy identity REL - RES + UNC = Brier(cell) checked per arm ([KI-MURPHY]);
  (6) KI1, KI2 (200 RWS draws, as ROUTE-SOURCE-NULL), descriptive arms, predictions, F-KI; the outcome written mode "x".

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  R1  KI(arm) = mean over the 5,907 EVAL items of the SUM over the 18 models of [(p_m - y)^2 - (p_cm - y)^2], p_m the model's TRAIN
      accuracy (over the scored TRAIN items), p_cm its TRAIN accuracy in the item's cell (the marginal when the cell carries no TRAIN
      mass: loo_imp's held-out rule; G14's backoff). F6's loo_imp returns the per-model MEAN; the registered sum = 18 x that mean.
      The EVAL items are held out of the fit (fit = TRAIN), so loo_imp's leave-one-out branch never fires on them: "LOO" in the
      registration reads as loo_imp's held-out branch (stated; for the READY).
  R2  Murphy terms on EVAL, per model then summed: REL = sum_c (n_c / N)(p_cm - o_cm)^2, RES = sum_c (n_c / N)(o_cm - o_m)^2,
      UNC = o_m (1 - o_m) (o: EVAL observed accuracies); Brier(cell) = REL - RES + UNC (checked); printed beside KI (descriptive).
  R3  KI1: D = KI(AF-U) - mean_s KI(K_s); spread_K = max - min of KI(K_s) over s = 0..4 (points); 95% interval = point +- 1.96
      SE_2stage (G14's reader form; the replicate KI recomputed on run_boot's TRAIN multiplicities and EVAL component weights).
      AF-BETTER iff D > spread_K AND lo > 0; K0-BETTER iff D < -spread_K AND hi < 0; NEITHER otherwise (strict; exclusive).
  R4  The TRAIN-half pre-pass (Support (e) "TRAIN-half pre-pass, no EVAL"): the key-complete TRAIN items in item_id order, a
      default_rng(20261004) permutation, the first floor(n / 2) the fit half, the rest scored; KI of AF-U and K0..K4 on that split;
      printed: D_pre, spread_K_pre, the i.i.d. SE of D_pre and the planning SE x sqrt(1.6) (the declared DEFF), MDE80. It runs after
      the TRAIN key and BEFORE the eval view opens; nothing of EVAL enters it.
  R5  KI2: the 200 RWS draws of ROUTE-SOURCE-NULL R3 (union_route_common.rws_cells, default_rng(20261004 + r)); p97.5 numpy linear;
      BEYOND-SOURCE iff KI(AF-U) > p97.5 (strict); NOT-BEYOND otherwise; rule 8 = NOT-BEYOND; F-KI fires iff NOT-BEYOND. Monte
      Carlo SE of p97.5 as there. No sampling SE is claimed for KI2 (registered).
  R6  Predictions "X [lo, hi]" HELD iff the point lies in the closed interval; KI1 by the three-outcome Brier sum; KI2 and P3 by the
      two-outcome Brier sum. Not applicable (stated): no judge verdict (no wrong(established), no tie convention A / B); no call
      cache, --pilot or truncation guard (zero calls).

SELFTEST (--selftest; escalation_rc's fixture layout via union_route_common.build_layout):
  branches      KI1 AF-BETTER / K0-BETTER / NEITHER by value incl. D exactly +-spread_K and lo / hi exactly 0; KI2 BEYOND / NOT-BEYOND
                incl. KI(AF) exactly at p97.5; rule 8; F-KI; P1 band inclusive; the Brier values; required lines
  units         ki_terms against loo_imp x M (unit weights, multiplicities via a duplicated fit list, an empty cell); Murphy identity
  run_e2e       --run end to end: KI of every arm, D with its two-stage interval and SE, spread_K, the RWS p97.5, the pre-pass D_pre /
                spread_pre, against an INDEPENDENT oracle (loo_imp on plain dicts; replicates through loo_imp on duplicated fit lists
                and the same unit draws; RWS by loops); KI1 / KI2 / F-KI by the hand rule; the pre-pass printed before the eval view
                opens; second --run refused
  refusals      pool, manifest, policy sha, [KI-DENOM], [KI-IDENTITY], [B3], [KI-HOOK], [KI-F6], marker present; no outcome
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

import math          # noqa: E402
import types         # noqa: E402
import argparse      # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import union_route_common as U   # noqa: E402  (pins escalation_rc, union_cells_io, union_af_route)
F6_PIN = ("free_tests_f4_f7.py", "f0749d6133e030422671d15af69b6cff94ea1298")
if U.blob_lf(os.path.join(HERE, F6_PIN[0])) != F6_PIN[1]:
    raise SystemExit("[KI] REFUSED: %s is blob:%s, not the pinned blob:%s" % (F6_PIN[0], U.blob_lf(os.path.join(HERE, F6_PIN[0])), F6_PIN[1]))
import free_tests_f4_f7 as F6    # noqa: E402  (F6's estimator loo_imp, unchanged)
import sqlite3                   # noqa: E402
sqlite3.connect = getattr(sqlite3.connect, "_raw", sqlite3.connect)

TAG = "[KI]"
TEST_ID = "KEY-INFO-V2"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — KEY-INFO-V2: does knowing an item\'s AF-U'
            ' cell predict which of the 18 models answer it correctly (LOO Brier gain over the marginal, summed over models), ..."'
            ' L24291-L24302 (_as_of b66b075d)')
OUT = "experiment_results/archv2/key_info_v2"
REG = dict(U.COMMON, out=OUT + "/outcome.txt", marker=OUT + "/key_info_v2.READ_STARTED", pre_seed=20261004, deff_plan=1.6)
FIXTURE_REG = dict(out="res/ki/outcome.txt", marker="res/ki/READ_STARTED")
_REG = [REG]


def reg():
    return _REG[0]


SUPPORT = dict(deff=1.6, n_eff=3690, se=0.0016, mde=0.0046)
VERDICT_LINE = ("KI1 bar = spread_K (pilot 0.005); prediction D +0.002 lies inside it: DESCRIPTIVE-ONLY for AF-BETTER at the"
                " prediction; KI2 a percentile test, no sampling SE claimed (200-draw Monte Carlo SE printed): SCOREABLE as a classification")
PRED_D = (-0.005, 0.010)
PROB_KI1 = (("NEITHER", 0.65), ("AF-BETTER", 0.20), ("K0-BETTER", 0.15))
PROB_KI2 = (("BEYOND-SOURCE", 0.60), ("NOT-BEYOND", 0.40))
PROB_P3 = (("> 0", 0.80), ("<= 0", 0.20))
HIT = Counter()


def hit(name):
    HIT[name] += 1


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ── the estimator (R1, R2) ─────────────────────────────────────────────────────────────────────────────────────────────

def ki_terms(A_fit, lab_fit, w_fit, A_sc, lab_sc, ng):
    """Per scored item, the sum over models of [(p_m - y)^2 - (p_cm - y)^2] with p from the weighted fit set (R1)."""
    A_fit = np.asarray(A_fit, dtype=np.float64)
    w = np.asarray(w_fit, dtype=np.float64)
    tot = w.sum()
    marg = (A_fit * w[:, None]).sum(axis=0) / tot
    m = A_fit.shape[1]
    flat = (np.asarray(lab_fit)[:, None] * m + np.arange(m)[None, :]).ravel()
    S = np.bincount(flat, weights=(A_fit * w[:, None]).ravel(), minlength=ng * m).reshape(ng, m)
    mass = np.bincount(np.asarray(lab_fit), weights=w, minlength=ng)
    with np.errstate(invalid="ignore", divide="ignore"):
        p = np.where(mass[:, None] > 0, S / np.where(mass > 0, mass, 1.0)[:, None], marg[None, :])
    Y = np.asarray(A_sc, dtype=np.float64)
    pc = p[np.asarray(lab_sc)]
    return ((marg[None, :] - Y) ** 2 - (pc - Y) ** 2).sum(axis=1), p, marg


def murphy(p_cells, marg, A_sc, lab_sc):
    """R2 on the scored items: REL, RES, UNC, Brier(cell), Brier(marginal), each summed over models."""
    Y = np.asarray(A_sc, dtype=np.float64)
    lab = np.asarray(lab_sc)
    N = len(lab)
    o = Y.mean(axis=0)
    rel = res = 0.0
    for cl in np.unique(lab):
        mk = lab == cl
        nc = int(mk.sum())
        oc = Y[mk].mean(axis=0)
        rel += float((nc / N) * ((p_cells[cl] - oc) ** 2).sum())
        res += float((nc / N) * ((oc - o) ** 2).sum())
    unc = float((o * (1 - o)).sum())
    b_cell = float(((p_cells[lab] - Y) ** 2).mean(axis=0).sum())
    b_marg = float(((marg[None, :] - Y) ** 2).mean(axis=0).sum())
    return dict(rel=rel, res=res, unc=unc, b_cell=b_cell, b_marg=b_marg)


def ki_f6(D, g):
    """F6's estimator, unchanged: free_tests_f4_f7.loo_imp(part, qs = EVAL, models, G, fit = TRAIN) x M (the registered sum)."""
    models = list(D.models)
    part = {D.items[k]: int(g[k]) for k in range(D.n)}
    Gd = {m_: {D.items[k]: int(D.A[k, j]) for k in range(D.n)} for j, m_ in enumerate(models)}
    qs = [D.items[k] for k in D.E]
    fit = [D.items[k] for k in D.T]
    imp = F6.loo_imp(part, qs, models, Gd, fit=fit)
    return float(np.mean(imp)) * len(models)


def ki1_verdict(d, spread):
    if d["point"] > spread and d["lo"] > 0:
        return "AF-BETTER"
    if d["point"] < -spread and d["hi"] < 0:
        return "K0-BETTER"
    return "NEITHER"


def ki_lines(st):
    L = []
    d, c = st["d"], reg()
    L.append("=== KEY-INFO-V2 KI1 / KI2 (%s) ===" % REG_TEXT)
    L.append("DENOMINATOR: %d EVAL items in %d components (Kish mean cluster size %.3f; Support (a) 5907 / 5404); %d models; TRAIN %d"
             " scored items (the fit set); B %d two-stage replicates" % (d["n"], st["comp"], st["kish"], st["m"], st["n_train"], st["B"]))
    L.append("LIKE WITH LIKE: AF-U [SC] | SRC [SC] | RWS [SC] | K_0 [SC] | declared [DECL] (a labelled reference, cross); AF-U vs SRC /"
             " RWS / K_0 is like with like")
    L.append("ARM KI (sum over models of the Brier gain over the TRAIN marginal; mean over EVAL items) | Murphy REL / RES / UNC (summed"
             " over models) | Brier(cell) / Brier(marginal):")
    for name in ["AF-U"] + ["K_s %s" % nm for nm in U.KNAMES] + ["SRC", "declared"]:
        a = st["arms"][name]
        L.append("    %-12s KI %+.6f | REL %.6f RES %.6f UNC %.6f | Brier %.6f / %.6f" % (name, a["ki"], a["rel"], a["res"], a["unc"],
                                                                                         a["b_cell"], a["b_marg"]))
    L.append("  F6 cross-check: every point KI above equals free_tests_f4_f7.loo_imp x %d to 1e-9 (%d arms + %d RWS draws)" % (
        st["m"], len(st["arms"]), len(st["rws"])))
    L.append("KI1 (DECIDING; POINT AND INTERVAL): D = KI(AF-U) - mean_s KI(K_s) = %+.6f | two-stage 95%% [%+.6f, %+.6f] | percentile"
             " [%+.6f, %+.6f]; spread_K = max - min over s of KI(K_s) = %.6f" % (d["point"], d["lo"], d["hi"], d["pct"][0], d["pct"][1], st["spread"]))
    L.append("  support KI1: n %d, SE_2stage %.6f (registered 0.0016), i.i.d. SE %.6f, DEFF %.3f (declared pilot assumption 1.6), n_eff %.0f"
             " (registered 3690), MDE80 %.6f (registered 0.0046); bar spread_K %.6f (pilot 0.005); verdict line of record: %s" % (
                 d["n"], d["se2"], d["se_iid"], d["deff"], d["n_eff"], d["mde"], st["spread"], VERDICT_LINE))
    v1 = ki1_verdict(d, st["spread"])
    if v1 == "AF-BETTER":
        hit("KI1.AF")
        L.append("  KI1 -> AF-BETTER (D %+.6f > spread_K %.6f AND the 95%% interval lies above 0)" % (d["point"], st["spread"]))
    elif v1 == "K0-BETTER":
        hit("KI1.K0")
        L.append("  KI1 -> K0-BETTER (D %+.6f < -spread_K %.6f AND the 95%% interval lies below 0)" % (d["point"], st["spread"]))
    else:
        hit("KI1.NEITHER")
        L.append("  KI1 -> NEITHER (neither D > spread_K with lo > 0 nor D < -spread_K with hi < 0)")
    rws, p975 = st["rws"], st["p975"]
    L.append("KI2 (DECIDING; the POINT against the RWS percentile): KI(AF-U) = %+.6f | %d RWS draws: min %+.6f, median %+.6f, p97.5 %+.6f,"
             " max %+.6f; Monte Carlo SE of p97.5 %.6f" % (st["arms"]["AF-U"]["ki"], len(rws), min(rws), st["rws_med"], p975, max(rws), st["mc_se"]))
    beyond = st["arms"]["AF-U"]["ki"] > p975
    v2 = "BEYOND-SOURCE" if beyond else "NOT-BEYOND"
    if beyond:
        hit("KI2.BEYOND")
        L.append("  KI2 -> BEYOND-SOURCE (KI(AF-U) %+.6f > p97.5 %+.6f)" % (st["arms"]["AF-U"]["ki"], p975))
        L.append("RULE 8: BEYOND-SOURCE is not refuted (KI(AF-U) > the RWS p97.5)")
        L.append("FALSIFIER F-KI: NOT FIRED (KI2 BEYOND-SOURCE; F-KI fires iff KI2 NOT-BEYOND)")
    else:
        hit("KI2.NOT")
        L.append("  KI2 -> NOT-BEYOND (KI(AF-U) %+.6f <= p97.5 %+.6f)" % (st["arms"]["AF-U"]["ki"], p975))
        L.append("RULE 8: BEYOND-SOURCE is REFUTED (KI(AF-U) <= the RWS p97.5)")
        L.append("FALSIFIER F-KI: FIRES (KI2 NOT-BEYOND): AF-U carries no correctness information beyond random within-source cells,"
                 " and 'cell-conditional evaluation' on [SC] cells is unsupported beyond source")
    dd = st["arms"]["declared"]["ki"] - st["arms"]["AF-U"]["ki"]
    L.append("DESCRIPTIVE: KI(SRC) = %+.6f; KI(declared) = %+.6f; KI(declared) - KI(AF-U) = %+.6f (cross); KI(AF-U) - KI(SRC) = %+.6f" % (
        st["arms"]["SRC"]["ki"], st["arms"]["declared"]["ki"], dd, st["arms"]["AF-U"]["ki"] - st["arms"]["SRC"]["ki"]))
    ok = U.in_band(d["point"], PRED_D)
    hit("PRED.HELD" if ok else "PRED.FAILED")
    L.append("PREDICTION P1 D +0.002 [-0.005, +0.010]: observed %+.6f -> %s" % (d["point"], "HELD" if ok else "FAILED"))
    L.append("PREDICTION P1 KI1 NEITHER 0.65, AF-BETTER 0.20, K0-BETTER 0.15: observed %s; Brier %.4f" % (v1, U.brier(PROB_KI1, v1)))
    L.append("PREDICTION P2 KI2 BEYOND-SOURCE 0.60: observed %s; Brier %.4f" % (v2, U.brier(PROB_KI2, v2)))
    o3 = "> 0" if dd > 0 else "<= 0"
    L.append("PREDICTION P3 KI(declared) - KI(AF-U) > 0 with probability 0.80 (descriptive; cross): observed %+.6f (%s); Brier %.4f" % (
        dd, o3, U.brier(PROB_P3, o3)))
    L.append("WORDS: AF-U is SOURCE-CONDITIONED [SC], never label-free; Brier information is not decision value; key-scored, no judge"
             " verdict (no wrong(established), no convention A / B)")
    L.append("WILL NOT SHOW (registered): a routing gain (Brier information is not decision value); judged quantities; other corpora or draws")
    return L, dict(KI1=v1, KI2=v2, F_KI=(v2 == "NOT-BEYOND"), P3=o3)


def denominators(say):
    c = reg()
    say("DENOMINATORS (registered Support (a)): %d EVAL items in %d components (Kish 1.09); DEFF 1.6 (a DECLARED PILOT ASSUMPTION: U1's"
        " two-stage 1.595 transported), n_eff 3,690, SE of D 0.0016, MDE80 0.0046; %s" % (c["n_route"], c["comp_route"], VERDICT_LINE))
    say("PLANNED: B = %d two-stage replicates (default_rng(%d)); K_s seeds 0-4; RWS %d draws, default_rng(%d + r); TRAIN-half pre-pass"
        " default_rng(%d) before the eval view opens" % (c["B"], c["seed"], c["rws_n"], c["rws_seed0"], c["pre_seed"]))
    say("IDENTITY TARGETS (UNION-AF-ROUTE outcome sha256 %s): %s" % (c["uar_outcome_sha"][:16], U.identity_text(c["identity"])))


def prepass(say, c, af, kx):
    """R4: the TRAIN-half pre-pass (TRAIN key only)."""
    def between(K_tr, train_meta, models):
        items = sorted(U.V.complete_items(K_tr, models))
        A = np.array([[K_tr[i][m_] for m_ in models] for i in items], dtype=np.float64)
        perm = np.random.default_rng(c["pre_seed"]).permutation(len(items))
        h = len(items) // 2
        fi, si = perm[:h], perm[h:]
        diffs, kis = None, {}
        for name, cells in [("AF-U", af)] + [(nm, kx[nm]) for nm in U.KNAMES]:
            keys, lab = np.unique(np.array([cells.get(i, U.V.NO_ROUTING_ROW) for i in items]), return_inverse=True)
            t, _p, _m = ki_terms(A[fi], lab[fi], np.ones(len(fi)), A[si], lab[si], len(keys))
            kis[name] = t
        kmean = np.mean([kis[nm] for nm in U.KNAMES], axis=0)
        diffs = kis["AF-U"] - kmean
        vals = [float(kis[nm].mean()) for nm in U.KNAMES]
        se = float(np.std(diffs, ddof=1) / math.sqrt(len(diffs)))
        say("PRE-PASS (TRAIN halves, no EVAL; R4): fit %d / scored %d TRAIN items; KI(AF-U) %+.6f; KI(K_s) %s; D_pre %+.6f; spread_K_pre"
            " %.6f; i.i.d. SE of D_pre %.6f; planning SE x sqrt(%.1f) %.6f, MDE80 %.6f" % (
                len(fi), len(si), float(kis["AF-U"].mean()), " / ".join("%+.6f" % x for x in vals), float(diffs.mean()),
                max(vals) - min(vals), se, c["deff_plan"], se * math.sqrt(c["deff_plan"]), 2.8 * se * math.sqrt(c["deff_plan"])))
        hit("PREPASS.DONE")
    return between


def dry_run(out=print):
    say = out
    U.header(say, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__), U.__file__, os.path.join(HERE, F6_PIN[0])] +
             [os.path.join(HERE, n) for n, _ in U.PINS])
    denominators(say)
    S = U.prepare(say, reg(), refuse, hit)
    cfg = U.UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(U.UAR.reg()["policy"])
    U.read_views(cfg, say, True, S["af"], S["kx"], reg()["marker"], None, refuse, hit, tag=TEST_ID)
    say("OUTPUTS (write-once, never committed): %s, %s" % (reg()["out"], reg()["marker"]))
    say("DRY-RUN: nothing written; no key read (the pre-pass needs the TRAIN key: --run only); no statistic printed.")
    hit("DRY.DONE")
    return 0


def V_fit(D_, wt):
    return U.V.fit(D_, wt)


def run(out=print):
    c = reg()
    lines = []

    def say(s_):
        lines.append(s_)
        out(s_)
    U.header(say, TEST_ID, "--run", REG_TEXT, [os.path.abspath(__file__), U.__file__, os.path.join(HERE, F6_PIN[0])] +
             [os.path.join(HERE, n) for n, _ in U.PINS])
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
                             "KEY-INFO-V2: the EVAL key read started. frozen policy sha256 %s" % c["uar_policy_sha"], refuse, hit,
                             between=prepass(say, c, S["af"], S["kx"]), tag=TEST_ID)
    n_comp = U.check_denominators(D, c, refuse, hit, "KI")
    say("  scored: TRAIN %d, EVAL %d key-complete items in %d components" % (D.n_train, D.n_eval, n_comp))
    P0 = U.b3_check(D, cfg, S["pol"], refuse, hit)
    say("  B3: the point policy re-fitted beside EVAL equals the frozen file (best single %s; AF, K0..K4, TRUE source, TRUE source/domain)"
        % S["pol"]["best_single"])
    arms = [("AF-U", "tree")] + [("K_s %s" % nm, "x:" + nm) for nm in U.KNAMES] + [("SRC", "tsrc"), ("declared", "tdom")]
    G_ = {name: D.groupings[key] for name, key in arms}
    AT, AE = D.A[D.T], D.A[D.E]
    rec = dict(ki={name: [] for name, _k in arms}, chk=[])
    r = np.arange(len(D.E))
    gt = D.groupings["tree"][0]

    def hook(D_, wt, v):
        Pp = V_fit(D_, wt)
        v = np.asarray(v, dtype=np.float64)
        wtt = wt[D_.T]
        for name, _k in arms:
            g, ng = G_[name]
            t, _p, _m = ki_terms(AT, g[D_.T], wtt, AE, g[D_.E], ng)
            rec["ki"][name].append(float(v @ t) / v.sum())
        pa = Pp.pol["tree"][gt[D_.E]]
        pa = np.where(pa < 0, Pp.gb, pa)
        rec["chk"].append((float(v @ AE[r, Pp.gb]) / v.sum(), float(v @ AE[r, pa]) / v.sum()))
    bt = U.V.run_boot(D, c["B"], c["seed"], hook=hook)
    if D.fit_asserts != 2 * c["B"] + 2:
        refuse("[G3] %d fit checks executed, not %d" % (D.fit_asserts, 2 * c["B"] + 2))
    chk = np.asarray(rec["chk"])
    ref = np.stack([bt["two"][:, 0, U.V.BS], bt["two"][:, 0, U.V.TREE]], axis=1)
    if chk.shape != ref.shape or not np.allclose(chk, ref, atol=1e-12, rtol=0):
        hit("REFUSE.HOOK")
        refuse("[KI-HOOK] the hook's re-fitted accuracies differ from run_boot's own arms")
    ok, got = U.identity(bt, D, c["identity"])
    if not ok:
        hit("REFUSE.IDENTITY")
        refuse("[KI-IDENTITY] %s is not UNION-AF-ROUTE's %s" % (U.identity_text(got), U.identity_text(c["identity"])))
    say("IDENTITY: %s -> REPRODUCED (UNION-AF-ROUTE's printed digits)" % U.identity_text(got))
    hit("IDENTITY.OK")
    ones = np.ones(len(D.T))
    st = dict(comp=n_comp, kish=U.kish_eval(D), n_train=D.n_train, B=c["B"], m=len(D.models), arms={})
    terms = {}
    for name, _k in arms:
        g, ng = G_[name]
        t, p, marg = ki_terms(AT, g[D.T], ones, AE, g[D.E], ng)
        terms[name] = t
        mu = murphy(p, marg, AE, g[D.E])
        if abs(mu["rel"] - mu["res"] + mu["unc"] - mu["b_cell"]) > 1e-9 or abs((mu["b_marg"] - mu["b_cell"]) - float(t.mean())) > 1e-9:
            hit("REFUSE.MURPHY")
            refuse("[KI-MURPHY] %s: REL - RES + UNC or Brier(marginal) - Brier(cell) disagrees with KI" % name)
        f6 = ki_f6(D, g)
        if abs(f6 - float(t.mean())) > 1e-9:
            hit("REFUSE.F6")
            refuse("[KI-F6] %s: the vectorised KI %+.9f differs from free_tests_f4_f7.loo_imp x M %+.9f" % (name, float(t.mean()), f6))
        st["arms"][name] = dict(mu, ki=float(t.mean()))
    kmean_t = np.mean([terms["K_s %s" % nm] for nm in U.KNAMES], axis=0)
    two = np.asarray(rec["ki"]["AF-U"]) - np.mean([rec["ki"]["K_s %s" % nm] for nm in U.KNAMES], axis=0)
    dt = terms["AF-U"] - kmean_t
    iid = [float(v @ dt) / v.sum() for v in U.iid_weights(c["seed"], len(D.E), c["B"])]
    st["d"] = U.interval(float(dt.mean()), two, iid, len(D.E))
    kk = [st["arms"]["K_s %s" % nm]["ki"] for nm in U.KNAMES]
    st["spread"] = max(kk) - min(kk)
    prof = U.rws_profile(D, gt)
    rws = []
    for rr in range(1, c["rws_n"] + 1):
        g, ng = U.rws_cells(D, prof, c["rws_seed0"] + rr)
        t, _p, _m = ki_terms(AT, g[D.T], ones, AE, g[D.E], ng)
        f6 = ki_f6(D, g)
        if abs(f6 - float(t.mean())) > 1e-9:
            hit("REFUSE.F6")
            refuse("[KI-F6] RWS draw %d: the vectorised KI differs from loo_imp x M" % rr)
        rws.append(float(t.mean()))
    st.update(rws=rws, p975=U.pctl(rws, 97.5), rws_med=U.pctl(rws, 50), mc_se=U.mc_se_pct(rws, 97.5))
    L, words = ki_lines(st)
    for ln in L:
        say(ln)
    U.write_outcome(c["out"], "\n".join(lines) + "\n", ok_sha, refuse, out)
    hit("RUN.DONE")
    return dict(st=st, words=words, D=D, bt=bt, P0=P0)


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
        return U.run_mutants(os.path.abspath(__file__), "key_info_v2", MUTANTS, TAG, only=a.only)
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    if a.dry_run:
        return dry_run(out=out)
    run(out=out)
    return 0


# ══ SELFTEST ══════════════════════════════════════════════════════════════════════════════════════════════════════════

BRANCHES = ("KI1.AF", "KI1.K0", "KI1.NEITHER", "KI2.BEYOND", "KI2.NOT", "PRED.HELD", "PRED.FAILED", "IDENTITY.OK", "RUN.DONE",
            "DRY.DONE", "MARKER.WRITTEN", "PREPASS.DONE", "REFUSE.WRITE_ONCE", "REFUSE.POOL", "REFUSE.POLICY_SHA", "REFUSE.MANIFEST",
            "REFUSE.DENOM", "REFUSE.IDENTITY", "REFUSE.B3", "REFUSE.HOOK", "REFUSE.F6", "REFUSE.MURPHY")
need = U.need


def _me():
    return types.SimpleNamespace(_REG=_REG, REG=REG, FIXTURE_REG=FIXTURE_REG)


def _syn(d=(0.002, -0.001, 0.005), spread=0.004, ki_af=0.05, p975=0.04, decl=0.08):
    arm = lambda k: dict(ki=k, rel=0.01, res=0.02, unc=3.0, b_cell=2.99, b_marg=2.99 + k)
    arms = {"AF-U": arm(ki_af), "SRC": arm(0.03), "declared": arm(decl)}
    arms.update({"K_s %s" % nm: arm(0.048) for nm in U.KNAMES})
    return dict(comp=5404, kish=1.09, n_train=11841, B=2000, m=18, arms=arms, spread=spread,
                d=dict(point=d[0], lo=d[1], hi=d[2], pct=(d[1], d[2]), se2=0.0016, se_iid=0.0013, deff=1.5, n_eff=3938.0, mde=0.0045, n=5907),
                rws=[0.03] * 38 + [p975] * 2, p975=p975, rws_med=0.03, mc_se=0.0005)


def st_branches():
    B1 = {"NEITHER": 0.1225 + 0.04 + 0.0225, "AF-BETTER": 0.4225 + 0.64 + 0.0225, "K0-BETTER": 0.4225 + 0.04 + 0.7225}
    cases = [((0.006, 0.001, 0.011), 0.004, "AF-BETTER"), ((0.006, 0.0, 0.011), 0.004, "NEITHER"), ((0.004, 0.001, 0.007), 0.004, "NEITHER"),
             ((0.0041, 0.001, 0.007), 0.004, "AF-BETTER"), ((-0.006, -0.011, -0.001), 0.004, "K0-BETTER"),
             ((-0.006, -0.011, 0.0), 0.004, "NEITHER"), ((-0.004, -0.007, -0.001), 0.004, "NEITHER"), ((-0.0041, -0.007, -0.001), 0.004, "K0-BETTER"),
             ((0.002, -0.001, 0.005), 0.004, "NEITHER")]
    for d, sp, want in cases:
        L, w = ki_lines(_syn(d=d, spread=sp))
        t = "\n".join(L)
        assert w["KI1"] == want, (d, sp, w)
        need(t, "  KI1 -> %s" % want, "verdict line of record: " + VERDICT_LINE, "two-stage 95%% [%+.6f, %+.6f]" % (d[1], d[2]),
             "PREDICTION P1 KI1 NEITHER 0.65, AF-BETTER 0.20, K0-BETTER 0.15: observed %s; Brier %.4f" % (want, B1[want]),
             "WILL NOT SHOW (registered)", "DENOMINATOR: 5907 EVAL items in 5404 components", "support KI1: n 5907", "[SC]", "[DECL]",
             "spread_K = max - min over s of KI(K_s) = %.6f" % sp)
    for ki_af, p975, want in ((0.05, 0.04, "BEYOND-SOURCE"), (0.04, 0.04, "NOT-BEYOND"), (0.0400001, 0.04, "BEYOND-SOURCE"), (0.03, 0.04, "NOT-BEYOND")):
        L, w = ki_lines(_syn(ki_af=ki_af, p975=p975))
        t = "\n".join(L)
        assert w["KI2"] == want and w["F_KI"] is (want == "NOT-BEYOND"), (ki_af, w)
        need(t, "  KI2 -> %s" % want, "PREDICTION P2 KI2 BEYOND-SOURCE 0.60: observed %s; Brier %.4f" % (want, 0.32 if want == "BEYOND-SOURCE" else 0.72))
        if want == "NOT-BEYOND":
            need(t, "RULE 8: BEYOND-SOURCE is REFUTED", "FALSIFIER F-KI: FIRES (KI2 NOT-BEYOND)")
        else:
            need(t, "RULE 8: BEYOND-SOURCE is not refuted", "FALSIFIER F-KI: NOT FIRED (KI2 BEYOND-SOURCE; F-KI fires iff KI2 NOT-BEYOND)")
    for d_, want in ((-0.005, "HELD"), (0.010, "HELD"), (-0.0051, "FAILED"), (0.0101, "FAILED")):
        need("\n".join(ki_lines(_syn(d=(d_, d_ - 0.003, d_ + 0.003)))[0]), "PREDICTION P1 D +0.002 [-0.005, +0.010]: observed %+.6f -> %s" % (d_, want))
    for decl, want, b in ((0.08, "> 0", 0.08), (0.05, "<= 0", 1.28), (0.04, "<= 0", 1.28)):
        need("\n".join(ki_lines(_syn(decl=decl))[0]), "observed %+.6f (%s); Brier %.4f" % (decl - 0.05, want, b))
    t = "\n".join(ki_lines(_syn())[0])
    need(t, "    AF-U         KI +0.050000 | REL 0.010000 RES 0.020000 UNC 3.000000 | Brier 2.990000 / 3.040000",
         "KI(SRC) = +0.030000; KI(declared) = +0.080000; KI(declared) - KI(AF-U) = +0.030000", "p97.5 +0.040000")


def st_units():
    rs = np.random.RandomState(4)
    mu = ["a", "b", "c", "d"]
    fit = ["f%02d" % j for j in range(30)]
    qs = ["q%02d" % j for j in range(12)]
    cell = {i: "c%d" % rs.randint(0, 4) for i in fit + qs}
    cell["q00"] = "c9"                                       # a cell with no TRAIN mass -> the marginal
    G = {m_: {i: int(rs.rand() < 0.2 + 0.2 * j) for i in fit + qs} for j, m_ in enumerate(mu)}
    keys = sorted(set(cell.values()))
    lab = {i: keys.index(cell[i]) for i in fit + qs}
    A_f = np.array([[G[m_][i] for m_ in mu] for i in fit])
    A_q = np.array([[G[m_][i] for m_ in mu] for i in qs])
    t, p, marg = ki_terms(A_f, [lab[i] for i in fit], np.ones(len(fit)), A_q, [lab[i] for i in qs], len(keys))
    ref = np.asarray(F6.loo_imp(cell, qs, mu, G, fit=fit)) * len(mu)
    assert np.allclose(t, ref, atol=1e-12), (t, ref)
    w = rs.randint(0, 3, len(fit))
    t2, _p, _m = ki_terms(A_f, [lab[i] for i in fit], w, A_q, [lab[i] for i in qs], len(keys))
    dup = [i for i, k in zip(fit, w) for _ in range(int(k))]
    ref2 = np.asarray(F6.loo_imp(cell, qs, mu, G, fit=dup)) * len(mu)
    assert np.allclose(t2, ref2, atol=1e-12), (t2, ref2)
    mm = murphy(p, marg, A_q, [lab[i] for i in qs])
    assert abs(mm["rel"] - mm["res"] + mm["unc"] - mm["b_cell"]) < 1e-12 and abs(mm["b_marg"] - mm["b_cell"] - t.mean()) < 1e-12


def _oracle(lay, res):
    """KI of every arm and replicate through F6's loo_imp on plain dicts (duplicated fit lists for multiplicities); RWS by loops."""
    fx, D = lay.fx, res["D"]
    c = dict(REG, **dict(lay.common, **FIXTURE_REG))
    mu, val = U.o_key(fx.spec)
    tr = [D.items[k] for k in D.T]
    ev = [D.items[k] for k in D.E]
    G = {m_: {i: val[(i, m_)] for i in tr + ev} for m_ in mu}
    man = U.json.load(open(os.path.join(lay.tmp, "res", "inputs", "inputs_manifest.json"), encoding="utf-8"))
    rd = lambda rel: U.V.load_tree_cells(os.path.join(lay.tmp, *rel.split("/")), man["inputs"][rel])[0]
    cells = {"AF-U": rd("res/inputs/af_cells.tsv")}
    for s in U.SEEDS:
        cells["K_s K%d" % s] = rd("res/inputs/k_cells_s%d.tsv" % s)
    cells["SRC"] = {i: fx.strata[i][0] for i in tr + ev}
    cells["declared"] = {i: fx.strata[i] for i in tr + ev}
    ki = lambda part, fitl, vv=None: (sum((vv or {}).get(q, 1) * x for q, x in zip(ev, F6.loo_imp(part, ev, mu, G, fit=fitl))) /
                                      sum((vv or {}).get(q, 1) for q in ev)) * len(mu)
    o = dict(ki={n_: ki(cl, tr) for n_, cl in cells.items()})
    ks = ["K_s K%d" % s for s in U.SEEDS]
    o["d"] = o["ki"]["AF-U"] - sum(o["ki"][k] for k in ks) / 5
    o["spread"] = max(o["ki"][k] for k in ks) - min(o["ki"][k] for k in ks)
    rng = np.random.default_rng(c["seed"])
    reps = []
    for _b in range(c["B"]):
        wt = np.zeros(D.n, dtype=np.int64)
        wt[D.T] = U.V.draw_units(rng, D.train_units)
        v = U.V.draw_units(rng, D.eval_units)
        dup = [D.items[k] for k in D.T for _ in range(int(wt[k]))]
        vv = {D.items[k]: float(v[j]) for j, k in enumerate(D.E)}
        reps.append(ki(cells["AF-U"], dup, vv) - sum(ki(cells[k], dup, vv) for k in ks) / 5)
    o["se2"] = float(np.std(reps, ddof=1))
    per = {n_: np.asarray(F6.loo_imp(cells[n_], ev, mu, G, fit=tr)) * len(mu) for n_ in ["AF-U"] + ks}
    de = per["AF-U"] - np.mean([per[k] for k in ks], axis=0)
    rng2 = np.random.default_rng(c["seed"])
    iid = []
    for _b in range(c["B"]):
        cnt = np.bincount(rng2.integers(0, len(ev), len(ev)), minlength=len(ev))
        iid.append(float(np.dot(cnt, de)) / cnt.sum())
    o["iid"] = float(np.std(iid, ddof=1))
    src = {i: fx.strata[i][0] for i in tr + ev}
    o["rws"] = [ki(U.o_rws(tr, ev, src, cells["AF-U"], c["rws_seed0"] + r), tr) for r in range(1, c["rws_n"] + 1)]
    # the pre-pass on TRAIN halves (complete TRAIN items in item_id order = D's TRAIN order here)
    perm = np.random.default_rng(c["pre_seed"]).permutation(len(tr))
    h = len(tr) // 2
    fh, sh = [tr[j] for j in perm[:h]], [tr[j] for j in perm[h:]]
    pre = {}
    for n_ in ["AF-U"] + ks:
        pre[n_] = np.asarray(F6.loo_imp(cells[n_], sh, mu, G, fit=fh)) * len(mu)
    o["d_pre"] = float(np.mean(pre["AF-U"] - np.mean([pre[k] for k in ks], axis=0)))
    vals = [float(pre[k].mean()) for k in ks]
    o["spread_pre"] = max(vals) - min(vals)
    return o


def st_run_e2e(base, mk):
    lay = U.clone(base, mk())
    text, err, res = U.cap(_me(), run, lay)
    assert err is None, err
    outp = os.path.join(lay.tmp, "res", "ki", "outcome.txt")
    out = open(outp, encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL %s (KEY-INFO-V2; --run" % U.POOL)
    o = _oracle(lay, res)
    for name, want in o["ki"].items():
        got, = U.num(out, r"    %s\s+KI ([+-][0-9.]+) \|" % U.re.escape(name))
        assert abs(got - want) < 6e-7, (name, got, want)
    assert abs(o["ki"]["AF-U"] - o["ki"]["SRC"]) > 1e-4 and o["spread"] > 1e-5, "the fixture does not discriminate the arms"
    p_, lo, hi, sp = U.num(out, r"D = KI\(AF-U\) - mean_s KI\(K_s\) = ([+-][0-9.]+) \| two-stage 95% \[([+-][0-9.]+), ([+-][0-9.]+)\].*?spread_K = max - min over s of KI\(K_s\) = ([0-9.]+)")
    se2, sei = U.num(out, r"support KI1: n \d+, SE_2stage ([0-9.]+) \(registered 0.0016\), i.i.d. SE ([0-9.]+),")
    assert abs(sei - o["iid"]) < 6e-7, (sei, o["iid"])
    assert abs(p_ - o["d"]) < 6e-7 and abs(sp - o["spread"]) < 6e-7 and abs(se2 - o["se2"]) < 6e-7, (p_, o["d"], sp, o["spread"], se2, o["se2"])
    assert abs(lo - (o["d"] - 1.96 * o["se2"])) < 2e-6 and abs(hi - (o["d"] + 1.96 * o["se2"])) < 2e-6
    p975, = U.num(out, r"p97.5 ([+-][0-9.]+),")
    assert abs(p975 - float(np.percentile(o["rws"], 97.5))) < 6e-7, (p975, o["rws"])
    assert len(set(round(x, 9) for x in o["rws"])) > 3
    dpre, sppre = U.num(out, r"D_pre ([+-][0-9.]+); spread_K_pre ([0-9.]+);")
    assert abs(dpre - o["d_pre"]) < 6e-7 and abs(sppre - o["spread_pre"]) < 6e-7, (dpre, o["d_pre"], sppre, o["spread_pre"])
    assert out.index("PRE-PASS (TRAIN halves") < out.index("--- EVAL (eval_view"), "the pre-pass was not printed before the eval view opened"
    v1 = "AF-BETTER" if (p_ > sp and lo > 0) else ("K0-BETTER" if (p_ < -sp and hi < 0) else "NEITHER")
    kaf = o["ki"]["AF-U"]
    v2 = "BEYOND-SOURCE" if kaf > p975 else "NOT-BEYOND"
    need(out, "  KI1 -> %s" % v1, "  KI2 -> %s" % v2, "FALSIFIER F-KI: %s" % ("FIRES" if v2 == "NOT-BEYOND" else "NOT FIRED"),
         "IDENTITY: %s -> REPRODUCED" % U.identity_text(lay.common["identity"]), "F6 cross-check: every point KI above equals")
    t2, err2, _r = U.cap(_me(), run, lay)
    assert err2 and "write-once" in err2, err2
    assert open(outp, encoding="utf-8").read() == out


def _no_outcome(lay):
    assert not os.path.exists(os.path.join(lay.tmp, "res", "ki", "outcome.txt")), "an outcome was written by a refusal"


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
                         (dict(n_route=lay.common["n_route"] + 1), "[KI-DENOM]")):
        lay = U.clone(base, mk())
        _t, err, _r = U.cap(_me(), run, lay, **over)
        assert err and needle in err, (over, err)
        _no_outcome(lay)
    idn = lay.common["identity"]
    lay = U.clone(base, mk())
    _t, err, _r = U.cap(_me(), run, lay, identity=dict(idn, k0=idn["k0"][:-1] + str((int(idn["k0"][-1]) + 1) % 10)))
    assert err and "[KI-IDENTITY]" in err, err
    assert "KI1 (DECIDING" not in _t
    _no_outcome(lay)
    RSN.st_b3(base, mk, run, _me, _no_outcome)
    g = globals()
    for fname, bad, needle in (("V_fit", lambda real: (lambda D_, wt, n=[0]: real(D_, U.V.train_full(D_) if n.__setitem__(0, n[0] + 1) or n[0] == 2 else wt)), "[KI-HOOK]"),
                               ("ki_f6", lambda real: (lambda D_, g_: real(D_, g_) + 1e-6), "[KI-F6] AF-U"),
                               ("ki_f6", lambda real: (lambda D_, g_, n=[0]: real(D_, g_) + (1e-6 if n.__setitem__(0, n[0] + 1) or n[0] > 8 else 0.0)), "[KI-F6] RWS draw 1"),
                               ("murphy", lambda real: (lambda *a: dict(real(*a), rel=real(*a)["rel"] + 1e-6)), "[KI-MURPHY] AF-U")):
        lay = U.clone(base, mk())
        real = g[fname]
        g[fname] = bad(real)
        try:
            _t, err, _r = U.cap(_me(), run, lay)
        finally:
            g[fname] = real
        assert err and needle in err, (fname, err)
        _no_outcome(lay)
    lay = U.clone(base, mk())
    os.makedirs(os.path.join(lay.tmp, "res", "ki"), exist_ok=True)
    open(os.path.join(lay.tmp, "res", "ki", "READ_STARTED"), "w").close()
    _t, err, _r = U.cap(_me(), run, lay)
    assert err and "write-once" in err, err
    _no_outcome(lay)


def st_dry_run(base, mk):
    lay = U.clone(base, mk())
    text, err, _r = U.cap(_me(), dry_run, lay)
    assert err is None, err
    assert text.splitlines()[0].startswith("POOL %s (KEY-INFO-V2; --dry-run" % U.POOL)
    need(text, "NOT opened by --dry-run", "DRY-RUN: nothing written; no key read", "POOL CHECK (B0-2): rc 0")
    for bad in ("KI1 (DECIDING", "PRE-PASS (TRAIN", "IDENTITY:", "PREDICTION"):
        assert bad not in text, bad
    assert not os.path.exists(os.path.join(lay.tmp, "res", "ki"))
    L = []
    saved = _REG[0]
    _REG[0] = REG
    try:
        U.header(L.append, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__)])
        denominators(L.append)
    finally:
        _REG[0] = saved
    t = "\n".join(L)
    assert L[0].startswith("POOL pv2_1575de61bb20e977 (KEY-INFO-V2; --dry-run"), L[0]
    need(t, "5907 EVAL items in 5404 components", "DEFF 1.6 (a DECLARED PILOT ASSUMPTION", "n_eff 3,690", "SE of D 0.0016", "MDE80 0.0046",
         VERDICT_LINE, "B = 2000 two-stage replicates (default_rng(42))", "RWS 200 draws, default_rng(20261004 + r)", "pre-pass default_rng(20261004)",
         "best single 0.6049, TRUE source 0.6150, AF-U leaf cell 0.6201, K_s K0 0.6271; C1 +2.67pp [+1.46pp, +3.89pp]; G_AF +1.52pp [+0.14pp, +2.91pp]",
         "L24291-L24302", "calls 0")
    assert REG["out"] == "experiment_results/archv2/key_info_v2/outcome.txt"


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print / refusal branches never executed: %s" % miss


CASES = (("branches", "KI1 three words incl. D = +-spread_K and lo / hi = 0; KI2 incl. KI(AF) = p97.5; rule 8; F-KI; P1-P3; Brier", "plain"),
         ("units", "ki_terms vs loo_imp x M (unit weights, multiplicities via a duplicated fit list, an empty cell); Murphy identity", "plain"),
         ("run_e2e", "--run end to end: every arm's KI, D interval and SE, spread_K, RWS p97.5, pre-pass vs loo_imp oracle; verdicts by hand; write-once", "base"),
         ("refusals", "pool, manifest, policy sha, DENOM, IDENTITY, B3 (four arms), KI-HOOK, KI-F6, marker exists; no outcome", "base"),
         ("dry_run", "--dry-run: POOL first, no statistic, nothing written; the REAL constants' lines", "base"),
         ("branch_cover", "every print / refusal branch executed", "plain"))
_FN = {"branches": st_branches, "units": st_units, "run_e2e": st_run_e2e, "refusals": st_refusals, "dry_run": st_dry_run,
       "branch_cover": st_branch_cover}


def selftest(only=None, quiet=False, base=None):
    return U.run_selftest(TAG, CASES, _FN, HIT, only=only, quiet=quiet, base=base)


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "S", "", ""),
    ("X01 AF-BETTER at D >= spread_K (boundary)", "S", '    if d["point"] > spread and d["lo"] > 0:', '    if d["point"] >= spread and d["lo"] > 0:'),
    ("X02 AF-BETTER at lo >= 0 (boundary)", "S", '    if d["point"] > spread and d["lo"] > 0:', '    if d["point"] > spread and d["lo"] >= 0:'),
    ("X03 K0-BETTER without the interval clause", "S", '    if d["point"] < -spread and d["hi"] < 0:', '    if d["point"] < -spread:'),
    ("X04 K0-BETTER at D <= -spread_K (boundary)", "S", '    if d["point"] < -spread and d["hi"] < 0:', '    if d["point"] <= -spread and d["hi"] < 0:'),
    ("X05 KI2 BEYOND at KI(AF) >= p97.5 (boundary)", "S", 'beyond = st["arms"]["AF-U"]["ki"] > p975', 'beyond = st["arms"]["AF-U"]["ki"] >= p975'),
    ("X06 KI2 against the RWS median", "S", 'st.update(rws=rws, p975=U.pctl(rws, 97.5),', 'st.update(rws=rws, p975=U.pctl(rws, 50),'),
    ("X07 KI = the mean over models (registered: the sum)", "S", '    return ((marg[None, :] - Y) ** 2 - (pc - Y) ** 2).sum(axis=1), p, marg', '    return ((marg[None, :] - Y) ** 2 - (pc - Y) ** 2).mean(axis=1), p, marg'),
    ("X08 F6 cross-check without x M", "S", '    return float(np.mean(imp)) * len(models)', '    return float(np.mean(imp))'),
    ("X09 marginal from the scored (EVAL) items (wrong split side)", "S", '    marg = (A_fit * w[:, None]).sum(axis=0) / tot', '    marg = np.asarray(A_sc, dtype=np.float64).mean(axis=0)'),
    ("X10 an empty cell forecast 0 (not the marginal)", "S", 'p = np.where(mass[:, None] > 0, S / np.where(mass > 0, mass, 1.0)[:, None], marg[None, :])', 'p = np.where(mass[:, None] > 0, S / np.where(mass > 0, mass, 1.0)[:, None], 0.0)'),
    ("X11 replicate KI on the full TRAIN (uncapped fork: no refit)", "S", '        wtt = wt[D_.T]', '        wtt = np.ones(len(D_.T))'),
    ("X12 replicate KI without the EVAL weights", "S", '            rec["ki"][name].append(float(v @ t) / v.sum())', '            rec["ki"][name].append(float(t.mean()))'),
    ("X13 replicate D against K0 only (seed-0-only)", "S", 'two = np.asarray(rec["ki"]["AF-U"]) - np.mean([rec["ki"]["K_s %s" % nm] for nm in U.KNAMES], axis=0)', 'two = np.asarray(rec["ki"]["AF-U"]) - np.asarray(rec["ki"]["K_s K0"])'),
    ("X14 point D against K0 only (seed-0-only)", "S", '    kmean_t = np.mean([terms["K_s %s" % nm] for nm in U.KNAMES], axis=0)', '    kmean_t = terms["K_s K0"]'),
    ("X15 spread_K = max - mean", "S", '    st["spread"] = max(kk) - min(kk)', '    st["spread"] = max(kk) - float(np.mean(kk))'),
    ("X16 hook check skipped", "S", 'if chk.shape != ref.shape or not np.allclose(chk, ref, atol=1e-12, rtol=0):', 'if False:'),
    ("X17 identity refusal removed", "S", '    if not ok:' + NL + '        hit("REFUSE.IDENTITY")', '    if False:' + NL + '        hit("REFUSE.IDENTITY")'),
    ("X18 F6 cross-check (arms) removed", "S", '        if abs(f6 - float(t.mean())) > 1e-9:' + NL + '            hit("REFUSE.F6")' + NL + '            refuse("[KI-F6] %s', '        if False:' + NL + '            hit("REFUSE.F6")' + NL + '            refuse("[KI-F6] %s'),
    ("X19 F6 cross-check (RWS) removed", "S", '        if abs(f6 - float(t.mean())) > 1e-9:' + NL + '            hit("REFUSE.F6")' + NL + '            refuse("[KI-F6] RWS', '        if False:' + NL + '            hit("REFUSE.F6")' + NL + '            refuse("[KI-F6] RWS'),
    ("X20 Murphy check removed", "S", '            hit("REFUSE.MURPHY")' + NL, '            pass' + NL + '        if False:' + NL),
    ("X21 pre-pass not run before the eval view", "S", '                             between=prepass(say, c, S["af"], S["kx"]), tag=TEST_ID)', '                             tag=TEST_ID)'),
    ("X22 pre-pass scored on its fit half", "S", '        fi, si = perm[:h], perm[h:]', '        fi, si = perm[:h], perm[:h]'),
    ("X23 KI2 Brier on a fixed outcome", "S", 'U.brier(PROB_KI2, v2)', 'U.brier(PROB_KI2, "BEYOND-SOURCE")'),
    ("X24 P3 sign >= 0", "S", '    o3 = "> 0" if dd > 0 else "<= 0"', '    o3 = "> 0" if dd >= 0 else "<= 0"'),
    ("X25 F-KI NOT FIRED line dropped (skip path)", "S", '        L.append("FALSIFIER F-KI: NOT FIRED (KI2 BEYOND-SOURCE; F-KI fires iff KI2 NOT-BEYOND)")', '        pass'),
    ("X26 verdict line of record dropped", "S", '(pilot 0.005); verdict line of record: %s" % (', '(pilot 0.005); %s" % ('),
    ("X27 every RWS draw on one seed", "S", '        g, ng = U.rws_cells(D, prof, c["rws_seed0"] + rr)', '        g, ng = U.rws_cells(D, prof, c["rws_seed0"])'),
    ("X28 i.i.d. replicates on another seed", "S", '    iid = [float(v @ dt) / v.sum() for v in U.iid_weights(c["seed"], len(D.E), c["B"])]', '    iid = [float(v @ dt) / v.sum() for v in U.iid_weights(c["seed"] + 1, len(D.E), c["B"])]'),
    ("X29 RWS profile from K0 (wrong arm)", "S", '    prof = U.rws_profile(D, gt)', '    prof = U.rws_profile(D, D.groupings["x:K0"][0])'),
    ("X30 KI2 reads SRC (wrong arm)", "S", 'beyond = st["arms"]["AF-U"]["ki"] > p975', 'beyond = st["arms"]["SRC"]["ki"] > p975'),
    ("X31 P1 band read on the K spread", "S", '    ok = U.in_band(d["point"], PRED_D)', '    ok = U.in_band(st["spread"], PRED_D)'),
    ("X32 KI1 bar = 0 (spread_K dropped)", "S", '    v1 = ki1_verdict(d, st["spread"])', '    v1 = ki1_verdict(d, 0.0)'),
    ("X33 pre-read write-once check removed", "S", '        if os.path.exists(U.P(p)):' + NL + '            hit("REFUSE.WRITE_ONCE")', '        if False:' + NL + '            hit("REFUSE.WRITE_ONCE")'),
)


if __name__ == "__main__":
    sys.exit(main())
