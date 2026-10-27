"""resp_profile_info.py: RESP-PROFILE-INFO -- after a 1-D 3PL removes item difficulty, discrimination and general model ability, do
AF-U cells carry which-model (interaction) structure beyond random within-source cells (out-of-sample R^2 of Rasch-type
residuals)? ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A CPU readout of keyed correctness.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — RESP-PROFILE-INFO: after a 1-D 3PL removes item
  difficulty, discrimination and general model ability, do AF-U cells carry which-model (interaction) structure beyond random
  within-source cells ..." L24388-L24400 (_as_of 633255f2): RP1 (DECIDING), RP2 (deciding), Support (a)-(g), P1-P4, F-RP.
  Source: docs/literature/2026-10-04_response_structure.md T-R1. AF-U is [SC] (federated per source); every arm compared with it
  here is [SC] except the declared reference [DECL] (cross, never ranked).

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, or anywhere with --data-root <main checkout>; never beside a
construction: --dry-run and --run are POOL READERS, rule 7):
  0. python tools/analysis/resp_profile_info.py --selftest     # synthetic sealed fixture views under E:/TaxoArena_tmp; NO DB of record
     python tools/analysis/resp_profile_info.py --mutants      # the mutant table below, re-run
  1. python tools/analysis/resp_profile_info.py --dry-run      # POOL line first; pins; frozen policy; cells; TRAIN / EVAL
                                                               #   denominators (structure only, both keys sealed); nothing written
  2. python tools/analysis/resp_profile_info.py --run          # ONE TRAIN key read, the TRAIN-half pre-pass printed, then ONE EVAL
       key read (B1 marker); outcome WRITE-ONCE: experiment_results/archv2/resp_profile_info/resp_profile_info_outcome.txt
       (+ resp_profile_info.READ_STARTED); never committed (pin sha256, back up to E:/TaxoArena_backup_<date>_<tag>)
  CPU: the two-stage bootstrap re-fits the TRAIN 3PL 2,000 times (about 1-2 s each): about 1 h. Then the reviewer, the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line (B0-2 pool check); write-once paths absent; (2) pins (LF blob of record + working-tree sha) of this file,
  resp_structure_common.py, union_cells_io 92a04543, cell_flips 998d39a7, union_af_route bf3f17db, v2_declared_cells f0f56805;
  (3) frozen TRAIN policy 8d68018c...; inputs manifest 53021e26...; AF-U, K0..K4 cells (manifest-pinned); (4) the gen view's TRAIN
  key (response_lite, UNUSABLE_CELL, MATH-FIX overlay); (5) the TRAIN-HALF PRE-PASS (Support (d)): realised per-item SD of the
  contribution to D, its SE at n_eff 3,690 and MDE80, printed BEFORE the EVAL view opens; (6) the EVAL key (B1 marker; 5,907 /
  5,404 refused otherwise); (7) B3 + IDENTITY at the point (C1 +2.67pp, G_AF +1.52pp; refused otherwise); (8) the 3PL (TRAIN
  theta, EVAL items with theta fixed); R2_int and the raw-y version for AF-U, K0..K4, SRC, declared and 200 RWS draws; (9)
  run_boot (G14's two-stage reader, B 2,000, default_rng(42), TRAIN items resampled within stratum, EVAL components within
  stratum) with the RP2 hook: per replicate the TRAIN 3PL, the EVAL items and the cell means are RE-FITTED on the replicate;
  the C1 two-stage interval must print [+1.46pp, +3.89pp] (refused otherwise); (10) RP1, RP2, F-RP, descriptive lines,
  predictions, Support; the outcome written (mode "x").

READINGS (stated, for the READY to confirm or refuse; none chosen silently):
  RP-R1 ebar_c,m = sum of model m's TRAIN residuals in cell c / (n_c + 20): the TRAIN mean shrunk by n_c / (n_c + 20) (n_c = TRAIN
        items of c; replicate multiplicities in the bootstrap); a cell with no TRAIN item has ebar 0.
  RP-R2 R2_int = 1 - sum_{EVAL i, m} (e_im - ebar_c(i),m)^2 / sum_{EVAL i, m} e_im^2 (the registered form; it can be negative).
  RP-R3 raw-y version: r_im = y_im - pbar_m (pbar_m = model m's TRAIN accuracy), the same statistic on r (RP-R1 / RP-R2 with r for
        e); difficulty-carried share = (R2_raw - R2_int) / R2_raw for AF-U (n/a when R2_raw <= 0).
  RP-R4 RP1's percentile: union_cells_io.pct (g13 rule, upper end sorted[int(0.975 x 200) - 1] = the 195th of 200); BEYOND-SOURCE iff
        R2_int(AF-U) > it (strict). Monte Carlo SE of that percentile: SD over 2,000 resamples of the 200 values (default_rng(20261004)).
  RP-R5 RP2: D = R2_int(AF-U) - mean over s of R2_int(K_s); spread_K = max - min over the five K_s points; the 95% interval =
        D +- 1.96 SE_2stage (G14's reader form, v2_declared_cells.contrast), SE_2stage = SD of D over the 2,000 two-stage replicates
        (each replicate re-fits theta, the TRAIN and EVAL item parameters and every cell mean); AF-BETTER iff lo > 0 AND D > spread_K;
        K0-BETTER iff hi < 0 AND D < -spread_K; NEITHER otherwise. DEFF = Var_2stage / Var_iid (EVAL items i.i.d., fits fixed,
        default_rng(42)); n_eff = 5,907 / DEFF; MDE80 = 2.80 SE_2stage.
  RP-R6 Support (d) pre-pass: the scored TRAIN items split in halves by default_rng(20261004).permutation (first floor(n/2) = H1);
        theta and item parameters from the full TRAIN fit; cell means from H1 (RP-R1); on H2, d_i = (mean_s S_Ks,i - S_AF,i) /
        mean_H2(T_i), S_arm,i = sum_m (e_im - ebar)^2, T_i = sum_m e_im^2 (so that D = mean_i d_i); SD(d_i) (ddof 1); planning SE =
        SD / sqrt(5,907 / 1.6), MDE80 = 2.8 SE.
  RP-R7 P4 "the BBH cells carry the largest share of R2_int(AF-U)": share_s = sum over EVAL items of source s of (T_i - S_i) / sum
        over all EVAL items of (T_i - S_i); HELD iff BBH's share is the largest; NOT SCOREABLE when sum (T_i - S_i) <= 0.
  RP-R8 Predictions: "X [lo, hi]" HELD iff lo <= X <= hi (closed); outcome probabilities scored by Brier (p - outcome)^2.
  RP-R9 Bootstrap replicates in which the TRAIN fit does not converge are counted and printed (not dropped).
  Not applicable (stated): no judge verdict enters (keyed correctness): no wrong(established) count, no tie conventions A / B; no
  call cache, --pilot or truncation guard (zero calls).

SELFTEST (--selftest; fixtures under scratch_dir's process dir on E:, removed afterwards): sealed synthetic gen (TRAIN) and eval
(EVAL) views (6 models, 4 sources incl. GPQA / MMLU_PRO floors, MATH-FIX overlay, twins, out-of-set items with a missing and a
multi-response cell), the frozen policy / manifest / cells files; the pool check stubbed. Cases:
  irt         IRT-R1 / IRT-R2 against scipy (resp_structure_common.irt_selfcheck)
  constants   the REAL registered constants (shrink 20, 200 RWS draws on 20261004 + r, r = 1..200, p97.5, B 2,000, seed 42, lambda 1.0,
              floors, n_eff 3,690)
  e2e         run() on the PLANTED fixture (m2 +4 logits in two AF-U cells): every arm's R2_int and the raw R2 printed to 6 dp equal an
              independent loop oracle (its own IRT on the fixture rows, its own cell means, its own RWS draws); RP1 BEYOND-SOURCE; D,
              spread_K; RP2's word from the printed interval by hand; replicate 0 of the two-stage equals the oracle on run_boot's own
              draws; the pre-pass SD against the oracle and printed BEFORE the EVAL view line; P1-P4 lines by value; the outcome equals
              the printed text; a second run REFUSED with the outcome unchanged
  null_e2e    run() on the NULL fixture (one difficulty centre, no interaction): RP1 NOT-BEYOND, F-RP FIRED, the P2 Brier
  branches    RP1 / RP2 (all three words, both strict edges) / F-RP / P1-P4 / Support lines by value on synthetic st
  refusals    identity point, identity C1 interval, B3 (a frozen pick changed), policy sha, pool rc 1 (POOL line still first), the
              write-once outcome and marker, the TRAIN-only guard; no outcome written by any of them
  dry_run     POOL line first, pins, denominators; no key read; nothing written
  branch_cover every print branch registered in BRANCHES was executed
MUTANTS: see MUTANTS at the end (run with --mutants; the table with the result is in the commit message).
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import json          # noqa: E402
import math          # noqa: E402
import argparse      # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _pre(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


if __name__ == "__main__" and _pre(sys.argv[1:]):
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_pre(sys.argv[1:]))
import resp_structure_common as RSC   # noqa: E402

U, V = RSC.U, RSC.V
TAG = "[RESP-PROFILE-INFO]"
TEST_ID = "RESP-PROFILE-INFO"
REG_TXT = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — RESP-PROFILE-INFO: after a 1-D 3PL'
           ' removes item difficulty, discrimination and general model ability, do AF-U cells carry which-model (interaction)'
           ' structure beyond random within-source cells ..." L24388-L24400 (_as_of 633255f2)')
RP_ = dict(shrink=20.0, n_rws=200, rws_seed=20261004, q=0.975, B=2000, seed=42, half_seed=20261004, deff_plan=1.6,
           sd_plan=0.05, n_eff_plan=3690, out_dir="experiment_results/archv2/resp_profile_info",
           outcome="resp_profile_info_outcome.txt", marker="resp_profile_info.READ_STARTED")
_RP = [RP_]
PRED = dict(P1=(0.000, 0.030), P2=0.55, P3=0.70, P4=0.65)
ARMS = ("AF-U",) + RSC.KNAMES + ("SRC", "declared")
HIT = Counter()
BRANCHES = ("RP1.BEYOND", "RP1.NOT_BEYOND", "RP2.AF_BETTER", "RP2.K0_BETTER", "RP2.NEITHER", "FRP.FIRED", "FRP.NOT_FIRED",
            "P4.SCORED", "P4.UNSCORED", "SS.SCORED", "SS.NA", "DC.SCORED", "DC.NA", "DRY.DONE", "RUN.DONE")


def hit(name):
    HIT[name] += 1


def R():
    return _RP[0]


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ── the statistic ───────────────────────────────────────────────────────────────────────────────────────────────────────
def cell_means(eT, gT, ng, w, shrink):
    """RP-R1: per (cell, model) sum of TRAIN residuals / (n_c + shrink); w = TRAIN multiplicities."""
    m = eT.shape[1]
    S = np.zeros((ng, m))
    np.add.at(S, gT, eT * w[:, None])
    n = np.bincount(gT, weights=w, minlength=ng)
    return S / (n + shrink)[:, None]


def r2(eE, gE, eb, v=None):
    """RP-R2 with EVAL weights v (1 at the point)."""
    Si = ((eE - eb[gE]) ** 2).sum(axis=1)
    Ti = (eE ** 2).sum(axis=1)
    if v is None:
        return 1.0 - Si.sum() / Ti.sum()
    return 1.0 - (v * Si).sum() / (v * Ti).sum()


def terms(eE, gE, eb):
    return ((eE - eb[gE]) ** 2).sum(axis=1), (eE ** 2).sum(axis=1)


def arm_r2(eT, eE, gT, gE, ng, w=None, v=None):
    w = np.ones(len(gT)) if w is None else w
    return r2(eE, gE, cell_means(eT, gT, ng, w, R()["shrink"]), v)


def prepass(models, tmeta, K_tr, af, kx, say):
    """RP-R6 (Support (d)): the TRAIN-half pre-pass, BEFORE the EVAL view opens."""
    items = V.complete_items(K_tr, models)
    Y = np.array([[K_tr[i][m] for m in models] for i in items], dtype=np.float64)
    srcs = [tmeta[i][1] for i in items]
    c = RSC.floors_of(srcs)
    ft = RSC.fit_train(Y, c)
    e = RSC.resid(Y, RSC.prob(ft["theta"], ft["alpha"], ft["b"], c))
    rng = np.random.default_rng(R()["half_seed"])
    perm = rng.permutation(len(items))
    h1, h2 = perm[:len(items) // 2], perm[len(items) // 2:]

    def grp(cells):
        keys = sorted(set(cells[i] for i in items))
        pos = {k: j for j, k in enumerate(keys)}
        return np.array([pos[cells[i]] for i in items], dtype=np.int64), len(keys)
    S = {}
    for nm, cells in [("AF-U", af)] + [(k, kx[k]) for k in RSC.KNAMES]:
        g, ng = grp(cells)
        eb = cell_means(e[h1], g[h1], ng, np.ones(len(h1)), R()["shrink"])
        S[nm], T = terms(e[h2], g[h2], eb)
    d = (np.mean([S[k] for k in RSC.KNAMES], axis=0) - S["AF-U"]) / T.mean()
    sd = float(np.std(d, ddof=1))
    n_eff = U.C()["n_eval"] / R()["deff_plan"]
    se = sd / math.sqrt(n_eff)
    say("%s SUPPORT (d) TRAIN-HALF PRE-PASS (before the EVAL view opens): %d TRAIN items, halves %d / %d (default_rng(%d)); realised"
        " per-item SD of the contribution to D %.5f (planning %.2f); SE of D at n_eff %.0f (EVAL %d / DEFF %.1f declared) %.6f;"
        " MDE80 %.6f (registered SE 0.0008, MDE80 0.0023)" % (TAG, len(items), len(h1), len(h2), R()["half_seed"], sd, R()["sd_plan"],
                                                                n_eff, U.C()["n_eval"], R()["deff_plan"], se, 2.8 * se))
    return dict(sd=sd, se=se, mde=2.8 * se, n=len(items))


def point_stats(D, I, arms):
    T, E = D.T, D.E
    out = {}
    pbar = I["YT"].mean(axis=0)
    rT, rE = I["YT"] - pbar[None, :], I["YE"] - pbar[None, :]
    for nm in ARMS:
        g, ng, _k = arms[nm]
        out[nm] = dict(r2=arm_r2(I["eT"], I["eE"], g[T], g[E], ng), raw=arm_r2(rT, rE, g[T], g[E], ng))
    g, ng, _k = arms["AF-U"]
    eb = cell_means(I["eT"], g[T], ng, np.ones(len(T)), R()["shrink"])
    S, Tt = terms(I["eE"], g[E], eb)
    X = Tt - S
    srcE = [D.src[k] for k in E]
    shares = {}
    tot = X.sum()
    for s in sorted(set(srcE)):
        mk = np.array([x == s for x in srcE])
        shares[s] = dict(share=float(X[mk].sum() / tot) if tot > 0 else float("nan"), r2=float(1.0 - S[mk].sum() / Tt[mk].sum()),
                         n=int(mk.sum()))
    return out, shares, float(tot)


def rws_stats(D, I, arms):
    g_af = arms["AF-U"][0]
    prof = RSC.rws_profile(D, g_af)
    vals, raws = [], []
    pbar = I["YT"].mean(axis=0)
    rT, rE = I["YT"] - pbar[None, :], I["YE"] - pbar[None, :]
    for r in range(1, R()["n_rws"] + 1):
        g, ng = RSC.rws_cells(D, prof, R()["rws_seed"] + r)
        vals.append(arm_r2(I["eT"], I["eE"], g[D.T], g[D.E], ng))
        raws.append(arm_r2(rT, rE, g[D.T], g[D.E], ng))
    return vals, raws, prof


def boot(D, I, arms):
    """run_boot (G14's two-stage reader) with the RP2 hook: each replicate RE-FITS the TRAIN 3PL (multiplicities), the EVAL items
    (theta fixed at the replicate's) and every cell mean; D_b on the replicate's EVAL weights. -> (bt, two D, two per arm, nonconv)."""
    T, E = D.T, D.E
    cT, cE = I["cT"], I["cE"]
    YT, YE = I["YT"], I["YE"]
    rec = dict(D=[], arms=[], nonconv=0, fits=0)
    kn = ("AF-U",) + RSC.KNAMES

    def hook(D_, wt, v):
        w = wt[T].astype(np.float64)
        RSC.assert_train(D_, T[w > 0])
        sel = w > 0
        ft = RSC.fit_train(YT[sel], cT[sel], w=w[sel], theta=I["theta"], alpha=I["aT"][sel], b=I["bT"][sel])
        rec["fits"] += 1
        rec["nonconv"] += int(not ft["converged"])
        aE, bE, _i, _m = RSC.fit_items(YE, cE, ft["theta"], alpha=I["aE"], b=I["bE"])
        eT = RSC.resid(YT[sel], RSC.prob(ft["theta"], ft["alpha"], ft["b"], cT[sel]))
        eE = RSC.resid(YE, RSC.prob(ft["theta"], aE, bE, cE))
        vals = {}
        for nm in kn:
            g, ng, _k = arms[nm]
            vals[nm] = arm_r2(eT, eE, g[T][sel], g[E], ng, w=w[sel], v=np.asarray(v, dtype=np.float64))
        rec["arms"].append(vals)
        rec["D"].append(vals["AF-U"] - np.mean([vals[k] for k in RSC.KNAMES]))
    bt = V.run_boot(D, R()["B"], R()["seed"], hook=hook)
    return bt, rec


def iid_D(D, I, arms):
    """i.i.d. EVAL replicates with the point fits (default_rng(seed)): Var_iid of D for the DEFF."""
    T, E = D.T, D.E
    kn = ("AF-U",) + RSC.KNAMES
    ST = {}
    for nm in kn:
        g, ng, _k = arms[nm]
        eb = cell_means(I["eT"], g[T], ng, np.ones(len(T)), R()["shrink"])
        ST[nm] = terms(I["eE"], g[E], eb)
    rng = np.random.default_rng(R()["seed"])
    NE = len(E)
    out = []
    for _b in range(R()["B"]):
        v = np.bincount(rng.integers(0, NE, NE), minlength=NE).astype(np.float64)
        r = {nm: 1.0 - (v * ST[nm][0]).sum() / (v * ST[nm][1]).sum() for nm in kn}
        out.append(r["AF-U"] - np.mean([r[k] for k in RSC.KNAMES]))
    return np.asarray(out)


def rp2_word(D, lo, hi, spread):
    if lo > 0 and D > spread:
        return "AF-BETTER"
    if hi < 0 and D < -spread:
        return "K0-BETTER"
    return "NEITHER"


def analyze(D, I, arms, pre):
    st = dict(N=len(D.E), G=D.eval_units["n_units"], M=len(D.models), NT=len(D.T), pre=pre)
    st["pt"], st["shares"], st["xtot"] = point_stats(D, I, arms)
    st["rws"], st["rws_raw"], st["prof"] = rws_stats(D, I, arms)
    srt = sorted(st["rws"])
    st["p975"] = U.pct(srt, R()["q"])
    st["p975_se"] = RSC.mc_se_pct(st["rws"], R()["q"])
    st["rws_med"] = float(np.median(st["rws"]))
    ks = [st["pt"][k]["r2"] for k in RSC.KNAMES]
    st["D"] = st["pt"]["AF-U"]["r2"] - float(np.mean(ks))
    st["spread"] = float(max(ks) - min(ks))
    bt, rec = boot(D, I, arms)
    st["bt"], st["rec"] = bt, rec
    two = np.asarray(rec["D"])
    iid = iid_D(D, I, arms)
    v2, vi = V._var(two), V._var(iid)
    st["se2"], st["se_iid"] = math.sqrt(v2), math.sqrt(vi)
    st["lo"], st["hi"] = st["D"] - 1.96 * st["se2"], st["D"] + 1.96 * st["se2"]
    st["deff"] = v2 / vi if vi > 0 else float("nan")
    st["n_eff"] = st["N"] / st["deff"] if st["deff"] == st["deff"] and st["deff"] > 0 else float("nan")
    st["mde"] = 2.8 * st["se2"]
    st["kish"] = RSC.support_deff(D)
    st["arm_se"] = {nm: math.sqrt(V._var([r[nm] for r in rec["arms"]])) for nm in ("AF-U",) + RSC.KNAMES}
    return st


# ── the printed readout (every branch registered) ───────────────────────────────────────────────────────────────────────
def f6(x):
    return "%+.6f" % x


def verdict_lines(st):
    c = R()
    pt = st["pt"]
    raf = pt["AF-U"]["r2"]
    L = ["", "== RP1 (DECIDING; the POINT against the RWS percentile) =="]
    L.append("  R2_int(AF-U) = %s; RWS (%d random within-source cell sets at AF-U's per-source size profile, default_rng(%d + r),"
             " r = 1..%d): median %s, p97.5 %s (Monte Carlo SE of the p97.5 %.6f)" % (
                 f6(raf), c["n_rws"], c["rws_seed"], c["n_rws"], f6(st["rws_med"]), f6(st["p975"]), st["p975_se"]))
    beyond = bool(raf > st["p975"])
    if beyond:
        hit("RP1.BEYOND")
        L.append("RP1: BEYOND-SOURCE: R2_int(AF-U) %s is above the RWS p97.5 %s: once difficulty, discrimination and general ability"
                 " are removed, AF-U cells predict which models do better than random cells of the same sizes within each source"
                 % (f6(raf), f6(st["p975"])))
    else:
        hit("RP1.NOT_BEYOND")
        L.append("RP1: NOT-BEYOND: R2_int(AF-U) %s is not above the RWS p97.5 %s (FAILS for BEYOND-SOURCE, rule 8)" % (f6(raf), f6(st["p975"])))
    L.append("")
    L.append("== RP2 (deciding; POINT AND INTERVAL against spread_K, like G13) ==")
    L.append("  D = R2_int(AF-U) - mean R2_int(K_0 s0-4) = %s; R2_int(K_s) %s; spread_K (max - min over the five seeds) %.6f" % (
        f6(st["D"]), " / ".join(f6(pt[k]["r2"]) for k in RSC.KNAMES), st["spread"]))
    L.append("  95%% interval (two-stage, B %d, default_rng(%d); each replicate re-fits theta, the item parameters and the cell means):"
             " [%s, %s] (SE %.6f)" % (c["B"], c["seed"], f6(st["lo"]), f6(st["hi"]), st["se2"]))
    w = rp2_word(st["D"], st["lo"], st["hi"], st["spread"])
    if w == "AF-BETTER":
        hit("RP2.AF_BETTER")
        L.append("RP2: AF-BETTER: the interval lies above 0 and D %s exceeds spread_K %.6f" % (f6(st["D"]), st["spread"]))
    elif w == "K0-BETTER":
        hit("RP2.K0_BETTER")
        L.append("RP2: K0-BETTER: the interval lies below 0 and D %s is below -spread_K %.6f" % (f6(st["D"]), st["spread"]))
    else:
        hit("RP2.NEITHER")
        L.append("RP2: NEITHER: the interval [%s, %s] and spread_K %.6f do not separate AF-U from K_0" % (f6(st["lo"]), f6(st["hi"]), st["spread"]))
    L.append("")
    if not beyond:
        hit("FRP.FIRED")
        L.append("F-RP: FIRED (RP1 NOT-BEYOND): once difficulty is removed, AF-U cells carry no which-model information beyond random"
                 " within-source cells; any cell routing gain is difficulty composition or source, and 'cell-conditional evaluation'"
                 " must say so")
    else:
        hit("FRP.NOT_FIRED")
        L.append("F-RP: NOT FIRED (RP1 BEYOND-SOURCE)")
    L.append("")
    L.append("== DESCRIPTIVE (no verdict) ==")
    L.append("  arm       label   R2_int       raw-y R2     cells")
    for nm in ARMS:
        L.append("  %-9s %-6s  %s    %s    %d" % (nm, "[DECL]" if nm == "declared" else "[SC]", f6(pt[nm]["r2"]), f6(pt[nm]["raw"]),
                                               st["ncells"][nm]))
    rd = pt["declared"]["r2"]
    if rd > 0:
        hit("SS.SCORED")
        L.append("  source share = R2_int(SRC) / R2_int(declared) = %s / %s = %.4f" % (f6(pt["SRC"]["r2"]), f6(rd), pt["SRC"]["r2"] / rd))
    else:
        hit("SS.NA")
        L.append("  source share: n/a (R2_int(declared) %s <= 0)" % f6(rd))
    ra = pt["AF-U"]["raw"]
    if ra > 0:
        hit("DC.SCORED")
        L.append("  difficulty-carried share (AF-U) = (raw %s - residual %s) / raw = %.4f" % (f6(ra), f6(raf), (ra - raf) / ra))
    else:
        hit("DC.NA")
        L.append("  difficulty-carried share (AF-U): n/a (raw-y R2 %s <= 0)" % f6(ra))
    L.append("  RWS raw-y R2: median %s, p97.5 %s" % (f6(float(np.median(st["rws_raw"]))), f6(U.pct(sorted(st["rws_raw"]), c["q"]))))
    L.append("  per source (AF-U): " + "; ".join("%s n %d R2_int %s share %s" % (s, v["n"], f6(v["r2"]), "%.4f" % v["share"] if v["share"] == v["share"] else "n/a")
                                                 for s, v in sorted(st["shares"].items())))
    L.append("  two-stage SE per arm: " + ", ".join("%s %.6f" % (k, st["arm_se"][k]) for k in ("AF-U",) + RSC.KNAMES)
             + "; bootstrap TRAIN fits %d, not converged %d" % (st["rec"]["fits"], st["rec"]["nonconv"]))
    L.append("")
    L.append("== PREDICTIONS (registrar's priors; bands closed; Brier (p - outcome)^2) ==")
    L.append("  P1 R2_int(AF-U) < 0.03, point in [0.000, 0.030]: %s -> %s" % (f6(raf), RSC.hw(raf, PRED["P1"])))
    L.append("  P2 RP1 BEYOND-SOURCE 0.55: outcome %s -> Brier %.4f" % ("BEYOND-SOURCE" if beyond else "NOT-BEYOND", RSC.brier(PRED["P2"], beyond)))
    L.append("  P3 RP2 NEITHER 0.70: outcome %s -> Brier %.4f" % (w, RSC.brier(PRED["P3"], w == "NEITHER")))
    if st["xtot"] > 0:
        hit("P4.SCORED")
        top = max(st["shares"], key=lambda s: st["shares"][s]["share"])
        L.append("  P4 the BBH cells carry the largest share of R2_int(AF-U) 0.65 (descriptive): largest share %s %.4f (BBH %s) -> %s; Brier"
                 " %.4f" % (top, st["shares"][top]["share"], "%.4f" % st["shares"]["BBH"]["share"] if "BBH" in st["shares"] else "absent",
                            "HELD" if top == "BBH" else "FAILED", RSC.brier(PRED["P4"], top == "BBH")))
    else:
        hit("P4.UNSCORED")
        L.append("  P4 the BBH cells carry the largest share of R2_int(AF-U) 0.65 (descriptive): NOT SCOREABLE (R2_int(AF-U) <= 0: no"
                 " explained share to divide)")
    L.append("")
    L.append("== SUPPORT (registered planning numbers; MEASURED beside) ==")
    L.append("  (a) EVAL %d items / %d components x %d models (registered 5,907 / 5,404 x 18); TRAIN %d items" % (st["N"], st["G"], st["M"], st["NT"]))
    L.append("  (b) DEFF of D MEASURED two-stage %.3f (declared pilot 1.6); Kish mean EVAL component size %.4f" % (st["deff"], st["kish"]))
    L.append("  (c) n_eff %.0f (registered 3,690)" % st["n_eff"])
    L.append("  (d) pre-pass SD %.5f (planning 0.05), planning SE %.6f; MEASURED SE of D (two-stage) %.6f (i.i.d. %.6f; registered 0.0008)" % (
        st["pre"]["sd"], st["pre"]["se"], st["se2"], st["se_iid"]))
    L.append("  (e) MDE80 = 2.80 x SE %.6f (registered 0.0023)" % st["mde"])
    L.append("  (f) VERDICT LINE (registered): RP1 SCOREABLE as a percentile classification (Monte Carlo SE of the p97.5 %.6f, 200 draws);"
             " RP2 DESCRIPTIVE-ONLY for AF-BETTER at the prediction (D +0.001 inside spread_K; spread_K measured %.6f)" % (st["p975_se"], st["spread"]))
    L.append("  (g) STRUCTURAL (registered): reachable; with 18 models the 3PL item parameters are weak (Jiang 2026), hence cell"
             " aggregation and null partitions")
    L.append("  NOT APPLICABLE: wrong(established) and the tie conventions A / B (keyed correctness; no judge verdict enters).")
    L.append("  WHAT THIS RESULT WILL NOT SHOW (registered): a routing gain; roster-independent structure; a dimension count of the matrix.")
    return L


# ── modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def out_paths(root, out_dir):
    d = out_dir or U.P(root, R()["out_dir"])
    return os.path.join(d, R()["outcome"]), os.path.join(d, R()["marker"])


def planned(say):
    c = R()
    say("%s PLANNED: 3PL (floors GPQA 1/4, MMLU_PRO 1/10, else 0; ridge lambda %.1f; theta on TRAIN only); shrink n_c / (n_c + %g);"
        " arms %s; RWS %d draws (default_rng(%d + r), r = 1..%d); RP1 percentile %.3f; RP2 two-stage B %d, default_rng(%d)" % (
            TAG, RSC.LAMBDA, c["shrink"], ", ".join(ARMS), c["n_rws"], c["rws_seed"], c["n_rws"], c["q"], c["B"], c["seed"]))


def dry_run(root, out_dir=None, out=print):
    outp, mark = out_paths(root, out_dir)
    pol, af, kx = RSC.prelude(root, out, TAG, TEST_ID, REG_TXT, [os.path.abspath(__file__)], [outp, mark], True)
    RSC.dry_structure(root, out, TAG, pol, af, kx)
    planned(out)
    out("%s DRY-RUN complete: no key column selected (both tripwires sealed); no statistic; nothing written" % TAG)
    hit("DRY.DONE")


def write_outcome(path, text):
    """The outcome of record: mode "x" (v2_reader_guards.write_once); an existing path is REFUSED and left unchanged."""
    return U.G.write_once(path, text)


def run(root, out_dir=None, out=print):
    lines = []

    def say(s):
        lines.append(s)
        out(s)
    outp, mark = out_paths(root, out_dir)
    pol, af, kx = RSC.prelude(root, say, TAG, TEST_ID, REG_TXT, [os.path.abspath(__file__)], [outp, mark], False)
    planned(say)
    pre = {}

    def between(models, tmeta, K_tr):
        pre.update(prepass(models, tmeta, K_tr, af, kx, say))
    D = RSC.load_all(root, say, TAG, pol, af, kx, mark, "%s: the EVAL key read started (B1); policy sha256 %s" % (TAG, U.C()["policy_sha"]),
                     between=between)
    RSC.b3_identity(D, pol, say, TAG)
    I = RSC.irt_point(D, say, TAG)
    arms = RSC.arms_of(D)
    st = analyze(D, I, arms, pre)
    st["ncells"] = {nm: len(set(arms[nm][0][D.E].tolist())) for nm in ARMS}
    c1 = V.contrast(st["bt"], D, "ALL", V.TDOM, V.BS)
    got = (RSC.pp(c1["point"]), RSC.pp(c1["lo"]), RSC.pp(c1["hi"]))
    want = (RSC.K()["c1"],) + tuple(RSC.K()["c1_int"])
    if got != want:
        refuse("[IDENTITY] the declared arm's two-stage C1 %s [%s, %s] is not the registered %s [%s, %s]" % (got + want))
    say("%s IDENTITY (two-stage, the same run_boot as RP2): C1 %s [%s, %s] -> REPRODUCED" % ((TAG,) + got))
    for ln in verdict_lines(st):
        say(ln)
    text = "\n".join(lines) + "\n"
    write_outcome(outp, text)
    out("%s OUTCOME written write-once: %s" % (TAG, outp))
    hit("RUN.DONE")
    return st, text


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────
FX_RP = dict(RP_, n_rws=40, B=24)


def _fx(tmp, variant="planted"):
    root, X = RSC.build_fixture(tmp, variant)
    X["kconst"]["c1_int"] = _c1_interval(root, X)
    return root, X


def _c1_interval(root, X):
    """The fixture's two-stage C1 interval (run_boot of G14's reader on the fixture: the precondition's target there)."""
    with RSC.patched(X):
        pol, af, kx = RSC.prelude(root, lambda s: None, TAG, TEST_ID, REG_TXT, [], [os.path.join(root, "nx")], True)
        models, tmeta, cstr, K_tr, _n = RSC.read_train(root, lambda s: None, TAG, pol["roster"], True)
        tw, esha = V.open_tw("eval", "route", U.P(root, U.C()["eval_rel"]), U.C()["eval_sha"], "eval_view", lambda s: None)
        tw.unseal("selftest: the fixture's C1 interval")
        E = U._eval_set_open(tw, esha, U.P(root, U.C()["eval_rel"]), root, lambda s: None, TAG, pol["roster"], False, None)
        K_ev, _k = V.read_key(tw, "response", U.C()["cv"], models, E["meta"], True, U.C()["rule"])
        tw.close()
        E["K"] = K_ev
        D = RSC.build(models, tmeta, E, K_tr, cstr, af, kx, pol, TAG)
        bt = V.run_boot(D, FX_RP["B"], FX_RP["seed"])
        c = V.contrast(bt, D, "ALL", V.TDOM, V.BS)
    return (RSC.pp(c["lo"]), RSC.pp(c["hi"]))


class _swap:
    def __init__(self, d):
        self.d = d

    def __enter__(self):
        self.old = _RP[0]
        _RP[0] = self.d

    def __exit__(self, *a):
        _RP[0] = self.old


def _oracle(X):
    """INDEPENDENT loops on the fixture rows: IRT (same estimator), cell means, R2, RWS, pre-pass."""
    O = RSC.fx_irt(X["rows"])
    tr, ev = O["tr"], O["ev"]
    sh = FX_RP["shrink"]
    m = len(RSC.FX_MODELS)

    def cellf(nm):
        if nm == "AF-U":
            return lambda r: r["af"]
        if nm == "SRC":
            return lambda r: r["src"]
        if nm == "declared":
            return lambda r: (r["src"], r["dom"])
        s = int(nm[1])
        return lambda r: X["kcells"][s][r["id"]]

    def r2loop(eT, eE, kf):
        sums, cnt = {}, {}
        for i, r in enumerate(tr):
            k = kf(r)
            cnt[k] = cnt.get(k, 0) + 1
            sums[k] = sums.get(k, np.zeros(m)) + eT[i]
        num = den = 0.0
        for i, r in enumerate(ev):
            k = kf(r)
            eb = sums[k] / (cnt[k] + sh) if k in cnt else np.zeros(m)
            num += ((eE[i] - eb) ** 2).sum()
            den += (eE[i] ** 2).sum()
        return 1.0 - num / den
    pbar = O["YT"].mean(axis=0)
    res = {}
    for nm in ARMS:
        res[nm] = (r2loop(O["eT"], O["eE"], cellf(nm)), r2loop(O["YT"] - pbar, O["YE"] - pbar, cellf(nm)))
    # RWS by loops: the profile in AF cell order (sorted cell names = build_ud's index order), the same stream order
    srcs = sorted(set(r["src"] for r in tr + ev))
    rws = []
    for rr in range(1, FX_RP["n_rws"] + 1):
        rng = np.random.default_rng(FX_RP["rws_seed"] + rr)
        lab, prof, start, base = {}, {}, {}, 0
        for s in srcs:
            pos = [r for r in tr if r["src"] == s]
            cells = sorted(set(r["af"] for r in pos))
            sizes = [sum(1 for r in pos if r["af"] == c) for c in cells]
            perm = rng.permutation(len(pos))
            off = 0
            for j, sz in enumerate(sizes):
                for q in perm[off:off + sz]:
                    lab[pos[q]["id"]] = base + j
                off += sz
            prof[s], start[s] = sizes, base
            base += len(sizes)
        for s in srcs:
            eps = [r for r in ev if r["src"] == s]
            if eps:
                w = np.asarray(prof[s], dtype=float)
                ch = rng.choice(len(w), size=len(eps), p=w / w.sum())
                for r, q in zip(eps, ch):
                    lab[r["id"]] = start[s] + q
        rws.append(r2loop(O["eT"], O["eE"], lambda r: lab[r["id"]]))
    return O, res, rws


def _oracle_prepass(X):
    O = RSC.fx_irt(X["rows"])
    tr = O["tr"]
    perm = np.random.default_rng(FX_RP["half_seed"]).permutation(len(tr))
    h1, h2 = set(perm[:len(tr) // 2].tolist()), perm[len(tr) // 2:]
    m = len(RSC.FX_MODELS)

    def S_of(kf):
        sums, cnt = {}, {}
        for i in h1:
            k = kf(tr[i])
            cnt[k] = cnt.get(k, 0) + 1
            sums[k] = sums.get(k, np.zeros(m)) + O["eT"][i]
        out = []
        for i in h2:
            k = kf(tr[i])
            eb = sums[k] / (cnt[k] + FX_RP["shrink"]) if k in cnt else np.zeros(m)
            out.append(((O["eT"][i] - eb) ** 2).sum())
        return np.array(out)
    Saf = S_of(lambda r: r["af"])
    Sk = np.mean([S_of(lambda r, s=s: X["kcells"][s][r["id"]]) for s in RSC.KSEEDS], axis=0)
    T = np.array([(O["eT"][i] ** 2).sum() for i in h2])
    return float(np.std((Sk - Saf) / T.mean(), ddof=1))


def _num(line, label):
    i = line.index(label) + len(label)
    return float(line[i:].split()[0].rstrip(";,"))


def st_constants():
    assert RP_["shrink"] == 20.0 and RP_["n_rws"] == 200 and RP_["rws_seed"] == 20261004 and RP_["q"] == 0.975
    assert RP_["B"] == 2000 and RP_["seed"] == 42 and RP_["deff_plan"] == 1.6 and RP_["n_eff_plan"] == 3690
    assert RSC.LAMBDA == 1.0 and RSC.FLOOR == {"GPQA": 0.25, "MMLU_PRO": 0.10} and RSC.KNAMES == ("K0", "K1", "K2", "K3", "K4")
    assert V.REG["B"] == RP_["B"] and V.REG["seed"] == RP_["seed"], "the reader's B / seed are the registered ones"
    assert PRED == dict(P1=(0.000, 0.030), P2=0.55, P3=0.70, P4=0.65)
    assert U.CONST["n_eval"] == 5907 and U.CONST["comp_eval"] == 5404 and RSC.KCONST["c1"] == "+2.67pp" and RSC.KCONST["gaf"] == "+1.52pp"
    assert RSC.KCONST["c1_int"] == ("+1.46pp", "+3.89pp")


def st_e2e(tmp):
    root, X = _fx(tmp)
    od = os.path.join(tmp, "out")
    O, res, rws = _oracle(X)
    with _swap(FX_RP), RSC.patched(X):
        (st, text), printed = RSC.capture(run, root, od)
        outp, mk = out_paths(root, od)
        assert open(outp, encoding="utf-8").read() == text, "the outcome equals the printed text"
        assert printed.split("\n")[0].startswith(TAG + " POOL pv_fx"), "POOL line first"
        assert os.path.isfile(mk)
        # every arm's R2 against the oracle (printed to 6 dp)
        for nm in ARMS:
            ln = RSC.line_with(text, "  %-9s %-6s  " % (nm, "[DECL]" if nm == "declared" else "[SC]"))
            p = ln.split()
            assert p[2] == f6(res[nm][0]) and p[3] == f6(res[nm][1]), (nm, p, res[nm])
        srt = sorted(rws)
        p975 = srt[int(0.975 * len(srt)) - 1]
        RSC.need(text, "p97.5 %s (Monte Carlo SE" % f6(p975), "median %s, p97.5" % f6(float(np.median(rws))))
        assert res["AF-U"][0] > p975, "the planted fixture is BEYOND by the oracle"
        RSC.need(text, "RP1: BEYOND-SOURCE: R2_int(AF-U) %s is above the RWS p97.5 %s" % (f6(res["AF-U"][0]), f6(p975)),
                 "F-RP: NOT FIRED (RP1 BEYOND-SOURCE)")
        Dv = res["AF-U"][0] - np.mean([res[k][0] for k in RSC.KNAMES])
        spread = max(res[k][0] for k in RSC.KNAMES) - min(res[k][0] for k in RSC.KNAMES)
        RSC.need(text, "D = R2_int(AF-U) - mean R2_int(K_0 s0-4) = %s;" % f6(Dv), "spread_K (max - min over the five seeds) %.6f" % spread)
        ln = RSC.line_with(text, "  95% interval")
        iv = ln.split("): [")[1].split("]")[0].split(",")
        lo, hi = float(iv[0]), float(iv[1])
        se = float(ln.split("(SE ")[1].rstrip(")"))
        assert abs(lo - (Dv - 1.96 * se)) < 2e-6 and abs(hi - (Dv + 1.96 * se)) < 2e-6, (lo, hi, Dv, se)
        word = "AF-BETTER" if (lo > 0 and Dv > spread) else ("K0-BETTER" if (hi < 0 and Dv < -spread) else "NEITHER")
        RSC.need(text, "RP2: %s" % word)
        # replicate 0 of the two-stage against the oracle on run_boot's own draws
        D = st["bt"]
        rng = np.random.default_rng(FX_RP["seed"])
        # rebuild the positions view: build_ud orders items by id; TRAIN units = items within (source, domain) stratum
        tr, ev = O["tr"], O["ev"]
        ids = sorted([r["id"] for r in tr + ev])
        pos = {i: k for k, i in enumerate(ids)}
        Tpos = np.array([pos[r["id"]] for r in tr])
        # draw_units over the reader's own unit structure: re-derive it independently (strata = (src, dom) sorted, units sorted)
        def units(rs, unit_of):
            uk = sorted(set(unit_of(r) for r in rs))
            up = {u: j for j, u in enumerate(uk)}
            by = {}
            for r in rs:
                by.setdefault((r["src"], r["dom"]), set()).add(up[unit_of(r)])
            return dict(unit_pos=np.array([up[unit_of(r)] for r in rs]), strata=[np.array(sorted(by[s])) for s in sorted(by)], n_units=len(uk))
        UT = units(sorted(tr, key=lambda r: r["id"]), lambda r: r["id"])
        UE = units(sorted(ev, key=lambda r: r["id"]), lambda r: r["comp"])
        wt = V.draw_units(rng, UT).astype(float)
        v = V.draw_units(rng, UE).astype(float)
        sel = wt > 0
        ft = RSC.fit_train(O["YT"][sel], O["cT"][sel], w=wt[sel], theta=O["theta"], alpha=O["aT"][sel], b=O["bT"][sel])
        aE, bE, _i, _m = RSC.fit_items(O["YE"], O["cE"], ft["theta"], alpha=O["aE"], b=O["bE"])
        eT = RSC.resid(O["YT"][sel], RSC.prob(ft["theta"], ft["alpha"], ft["b"], O["cT"][sel]))
        eE = RSC.resid(O["YE"], RSC.prob(ft["theta"], aE, bE, O["cE"]))
        trs = [r for r, s_ in zip(tr, sel) if s_]
        ws = wt[sel]

        def r2w(kf):
            sums, cnt = {}, {}
            for i, r in enumerate(trs):
                k = kf(r)
                cnt[k] = cnt.get(k, 0) + ws[i]
                sums[k] = sums.get(k, 0) + ws[i] * eT[i]
            num = den = 0.0
            for i, r in enumerate(ev):
                k = kf(r)
                eb = sums[k] / (cnt[k] + FX_RP["shrink"]) if k in cnt else 0.0
                num += v[i] * ((eE[i] - eb) ** 2).sum()
                den += v[i] * (eE[i] ** 2).sum()
            return 1.0 - num / den
        d0 = r2w(lambda r: r["af"]) - np.mean([r2w(lambda r, s=s: X["kcells"][s][r["id"]]) for s in RSC.KSEEDS])
        assert abs(st["rec"]["D"][0] - d0) < 1e-9, (st["rec"]["D"][0], d0)
        assert st["rec"]["fits"] == FX_RP["B"] and st["rec"]["nonconv"] == 0
        assert len(set(np.round(st["rec"]["D"], 12).tolist())) > FX_RP["B"] // 2, "replicates differ (re-fitted)"
        # the pre-pass: value, and printed BEFORE the EVAL view opened
        sd = _oracle_prepass(X)
        pl = RSC.line_with(printed, TAG + " SUPPORT (d) TRAIN-HALF PRE-PASS")
        assert "SD of the contribution to D %.5f" % sd in pl, (pl, sd)
        se_ = sd / math.sqrt(len(ev) / 1.6)
        assert "(EVAL %d / DEFF 1.6 declared) %.6f; MDE80 %.6f" % (len(ev), se_, 2.8 * se_) in pl, (pl, se_)
        assert printed.index("TRAIN-HALF PRE-PASS") < printed.index("eval_view "), "pre-pass before the EVAL view"
        # predictions by value
        raf = res["AF-U"][0]
        RSC.need(text, "P1 R2_int(AF-U) < 0.03, point in [0.000, 0.030]: %s -> %s" % (f6(raf), "HELD" if 0 <= raf <= 0.03 else "FAILED"),
                 "P2 RP1 BEYOND-SOURCE 0.55: outcome BEYOND-SOURCE -> Brier 0.2025",
                 "P3 RP2 NEITHER 0.70: outcome %s -> Brier %.4f" % (word, (0.7 - (word == "NEITHER")) ** 2))
        # P4: shares by source from the oracle
        sums, cnt = {}, {}
        for i, r in enumerate(tr):
            cnt[r["af"]] = cnt.get(r["af"], 0) + 1
            sums[r["af"]] = sums.get(r["af"], 0) + O["eT"][i]
        Xs = {}
        for i, r in enumerate(ev):
            eb = sums[r["af"]] / (cnt[r["af"]] + FX_RP["shrink"])
            Xs[r["src"]] = Xs.get(r["src"], 0.0) + (O["eE"][i] ** 2).sum() - ((O["eE"][i] - eb) ** 2).sum()
        tot = sum(Xs.values())
        top = max(Xs, key=Xs.get)
        RSC.need(text, "largest share %s %.4f (BBH %.4f) -> %s" % (top, Xs[top] / tot, Xs["BBH"] / tot, "HELD" if top == "BBH" else "FAILED"))
        RSC.need(text, "(a) EVAL %d items / %d components x 6 models" % (len(ev), X["const"]["comp_eval"]),
                 "IDENTITY (two-stage, the same run_boot as RP2): C1 %s [%s, %s] -> REPRODUCED" % ((X["kconst"]["c1"],) + X["kconst"]["c1_int"]))
        try:
            RSC.capture(run, root, od)
            raise AssertionError("second run not refused")
        except SystemExit as e:
            assert "write-once" in str(e), e
        assert open(outp, encoding="utf-8").read() == text


def st_null(tmp):
    root, X = _fx(tmp, "null")
    od = os.path.join(tmp, "out")
    O, res, rws = _oracle(X)
    srt = sorted(rws)
    p975 = srt[int(0.975 * len(srt)) - 1]
    assert res["AF-U"][0] <= p975, "the null fixture is NOT-BEYOND by the oracle"
    with _swap(FX_RP), RSC.patched(X):
        (st, text), _p = RSC.capture(run, root, od)
    RSC.need(text, "RP1: NOT-BEYOND: R2_int(AF-U) %s is not above the RWS p97.5 %s (FAILS for BEYOND-SOURCE, rule 8)" % (f6(res["AF-U"][0]), f6(p975)),
             "F-RP: FIRED (RP1 NOT-BEYOND)", "P2 RP1 BEYOND-SOURCE 0.55: outcome NOT-BEYOND -> Brier 0.3025")


def _syn(raf=0.02, p975=0.01, D=0.002, lo=0.001, hi=0.003, spread=0.001, rd=0.05, ra=0.04, xtot=10.0, top="BBH"):
    pt = {nm: dict(r2=0.01, raw=0.02) for nm in ARMS}
    pt["AF-U"] = dict(r2=raf, raw=ra)
    pt["declared"] = dict(r2=rd, raw=0.06)
    pt["SRC"] = dict(r2=0.01, raw=0.02)
    shares = {"BBH": dict(share=0.6 if top == "BBH" else 0.2, r2=0.03, n=10), "MATH": dict(share=0.4 if top == "BBH" else 0.8, r2=0.01, n=10)}
    return dict(N=5907, G=5404, M=18, NT=12000, pre=dict(sd=0.05, se=0.0008, mde=0.0023), pt=pt, shares=shares, xtot=xtot,
                rws=[0.0] * 200, rws_raw=[0.0] * 200, p975=p975, p975_se=0.0001, rws_med=0.0, D=D, spread=spread, lo=lo, hi=hi,
                se2=0.001, se_iid=0.0008, deff=1.5, n_eff=3938, mde=0.0028, kish=1.09, arm_se={k: 0.001 for k in ("AF-U",) + RSC.KNAMES},
                rec=dict(fits=2000, nonconv=0), ncells={nm: 5 for nm in ARMS})


def st_branches():
    J = lambda st: "\n".join(verdict_lines(st))           # noqa: E731
    t = J(_syn(raf=0.02, p975=0.01))
    RSC.need(t, "RP1: BEYOND-SOURCE", "F-RP: NOT FIRED", "P2 RP1 BEYOND-SOURCE 0.55: outcome BEYOND-SOURCE -> Brier 0.2025")
    t = J(_syn(raf=0.01, p975=0.01))                      # strict: equal is NOT above
    RSC.need(t, "RP1: NOT-BEYOND", "F-RP: FIRED (RP1 NOT-BEYOND)", "Brier 0.3025")
    # RP2: all three words and both strict edges
    RSC.need(J(_syn(D=0.002, lo=0.001, hi=0.003, spread=0.001)), "RP2: AF-BETTER", "P3 RP2 NEITHER 0.70: outcome AF-BETTER -> Brier 0.4900")
    RSC.need(J(_syn(D=0.002, lo=0.0, hi=0.003, spread=0.001)), "RP2: NEITHER")              # lo = 0 is not above 0
    RSC.need(J(_syn(D=0.001, lo=0.0005, hi=0.003, spread=0.001)), "RP2: NEITHER")           # D = spread is not beyond
    RSC.need(J(_syn(D=-0.002, lo=-0.003, hi=-0.001, spread=0.001)), "RP2: K0-BETTER")
    RSC.need(J(_syn(D=-0.002, lo=-0.003, hi=0.0, spread=0.001)), "RP2: NEITHER")
    RSC.need(J(_syn(D=-0.001, lo=-0.003, hi=-0.0005, spread=0.001)), "RP2: NEITHER", "outcome NEITHER -> Brier 0.0900")
    assert rp2_word(np.float64(0.002), np.float64(0.001), np.float64(0.003), np.float64(0.001)) == "AF-BETTER"
    # P1 band closed at both ends
    RSC.need(J(_syn(raf=0.0, p975=-1)), "point in [0.000, 0.030]: +0.000000 -> HELD")
    RSC.need(J(_syn(raf=0.03, p975=-1)), "point in [0.000, 0.030]: +0.030000 -> HELD")
    RSC.need(J(_syn(raf=0.0300001, p975=-1)), "+0.030000 -> FAILED")
    RSC.need(J(_syn(raf=-0.000001, p975=-1)), "-0.000001 -> FAILED")
    # P4 and the n/a branches
    RSC.need(J(_syn(top="BBH")), "largest share BBH 0.6000 (BBH 0.6000) -> HELD; Brier 0.1225")
    RSC.need(J(_syn(top="MATH")), "largest share MATH 0.8000 (BBH 0.2000) -> FAILED; Brier 0.4225")
    RSC.need(J(_syn(xtot=0.0)), "NOT SCOREABLE (R2_int(AF-U) <= 0")
    RSC.need(J(_syn(rd=0.05)), "source share = R2_int(SRC) / R2_int(declared) = +0.010000 / +0.050000 = 0.2000")
    RSC.need(J(_syn(rd=-0.01)), "source share: n/a")
    RSC.need(J(_syn(raf=0.01, ra=0.04)), "difficulty-carried share (AF-U) = (raw +0.040000 - residual +0.010000) / raw = 0.7500")
    RSC.need(J(_syn(ra=0.0)), "difficulty-carried share (AF-U): n/a")
    RSC.need(J(_syn()), "(c) n_eff 3938", "(e) MDE80 = 2.80 x SE 0.002800", "(b) DEFF of D MEASURED two-stage 1.500")


def st_refusals(tmp):
    def expect(mut, needle, pool=(0, "stub"), pre=None, existed=None, kmut=None):
        sub = os.path.join(tmp, "r%d" % len(os.listdir(tmp)))
        os.makedirs(sub)
        root, X = RSC.build_fixture(sub)
        X["kconst"]["c1_int"] = ("+0.00pp", "+0.00pp")
        X["const"] = dict(X["const"], **mut)
        if kmut:
            X["kconst"] = dict(X["kconst"], **kmut)
        od = os.path.join(root, "out")
        if pre:
            pre(root, od, X)
        buf = []
        with _swap(dict(FX_RP, B=4, n_rws=4)), RSC.patched(X, pool):
            try:
                run(root, od, out=buf.append)
                raise AssertionError("not refused: %s" % needle)
            except SystemExit as e:
                assert needle in str(e), (needle, str(e)[:300])
        op = os.path.join(od, R()["outcome"])
        if existed:
            assert open(op, encoding="utf-8").read() == "kept", "a pre-existing outcome is left unchanged"
        else:
            assert not os.path.exists(op), "no outcome after a refusal"
        return buf
    expect({}, "[IDENTITY] the declared arm's two-stage C1")          # the interval target is wrong (+0.00pp)
    expect({}, "[IDENTITY] C1", kmut=dict(c1="+9.99pp"))
    expect({}, "[IDENTITY] C1", kmut=dict(gaf="+9.99pp"))
    expect(dict(policy_sha="0" * 64), "frozen TRAIN policy is sha256")
    buf = expect({}, "B0-2 pool check failed", pool=(1, "stub failure"))
    assert buf[0].startswith(TAG + " POOL"), "POOL line first even on refusal"

    def mk(name, txt):
        def f(root, od, X):
            os.makedirs(od, exist_ok=True)
            with open(os.path.join(od, name), "w", encoding="utf-8") as fh:
                fh.write(txt)
        return f
    expect({}, "write-once output(s) exist", pre=mk(RP_["marker"], ""))
    expect({}, "write-once output(s) exist", pre=mk(RP_["outcome"], "kept"), existed=True)

    def b3(root, od, X):
        pp_ = U.P(root, U.CONST["policy_rel"])
        pol = json.load(open(pp_, encoding="utf-8"))
        c = sorted(pol["tree_cell"])[0]
        pol["tree_cell"][c] = [m for m in RSC.FX_MODELS if m != pol["tree_cell"][c]][0]
        with open(pp_, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(pol, sort_keys=True, indent=1) + "\n")
        X["const"]["policy_sha"] = RSC.sha256_bytes(pp_)
    expect({}, "[B3] the point policy", pre=b3)

    wp = os.path.join(tmp, "existing.txt")
    with open(wp, "w", encoding="utf-8") as fh:
        fh.write("kept")
    try:
        write_outcome(wp, "new")
        raise AssertionError("write_outcome overwrote")
    except SystemExit as e:
        assert "write-once" in str(e)
    assert open(wp, encoding="utf-8").read() == "kept", "an existing outcome is left unchanged"

    class _D:
        train_set = frozenset([0, 1])
    try:
        RSC.assert_train(_D(), np.array([0, 1, 2]))
        raise AssertionError("TRAIN-only guard did not fire")
    except SystemExit as e:
        assert "[TRAIN-ONLY]" in str(e)


def st_dry(tmp):
    root, X = _fx(tmp)
    od = os.path.join(tmp, "out")

    def files():
        return sorted(os.path.join(a, f_) for a, _d, fs in os.walk(tmp) for f_ in fs)
    before = files()
    with _swap(FX_RP), RSC.patched(X):
        _r, text = RSC.capture(dry_run, root, od)
    assert files() == before, "the dry-run writes no file"
    assert text.split("\n")[0].startswith(TAG + " POOL pv_fx")
    assert "TRAIN key:" not in text and "key cells single" not in text, "no key read"
    RSC.need(text, "TRAIN SET (gen view TRAIN items of fx", "EVAL SET (G14's", "DENOMINATOR AF-U  12 distinct cells",
             "PIN tools/analysis/resp_profile_info.py blob:", "PLANNED: 3PL", "DRY-RUN complete")
    assert "RP1:" not in text and "R2_int" not in text


CASES = (("irt", RSC.irt_selfcheck, "plain"), ("constants", st_constants, "plain"), ("branches", st_branches, "plain"),
         ("e2e", st_e2e, "tmp"), ("null_e2e", st_null, "tmp"), ("refusals", st_refusals, "tmp"), ("dry_run", st_dry, "tmp"))


def selftest(only=None, quiet=False):
    return RSC.run_cases(TAG, CASES, HIT, BRANCHES, only, quiet)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--run", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--data-root", default=U.ROOT)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        selftest(set(a.only) if a.only else None)
        return 0
    if a.mutants:
        return RSC.run_mutants(os.path.abspath(__file__), "resp_profile_info", MUTANTS, TAG, a.only)
    if a.dry_run:
        dry_run(os.path.abspath(a.data_root), a.out_dir)
        return 0
    run(os.path.abspath(a.data_root), a.out_dir)
    return 0


# (name, old, new, selftest cases, target "self" | "common")
MUTANTS = (
    ("C00 control (no-op edit)", "    return 1.0 - (v * Si).sum() / (v * Ti).sum()", "    return 1.0 - (v * Si).sum() / (v * Ti).sum()", ["e2e"], "self"),
    # the statistic (registered form, shrinkage, denominator, wrong side)
    ("X01 no shrinkage (plain TRAIN cell mean)", "    return S / (n + shrink)[:, None]", "    return S / np.maximum(n, 1.0)[:, None]", ["e2e"], "self"),
    ("X02 registered shrink constant 20 -> 10", "RP_ = dict(shrink=20.0,", "RP_ = dict(shrink=10.0,", ["constants"], "self"),
    ("X03 cell means from EVAL residuals (wrong side)", 'out[nm] = dict(r2=arm_r2(I["eT"], I["eE"], g[T], g[E], ng)',
     'out[nm] = dict(r2=arm_r2(I["eE"], I["eE"], g[E], g[E], ng)', ["e2e"], "self"),
    ("X04 theta fitted on TRAIN + EVAL (wrong side)", '    ft = fit_train(YT, cT, lam=lam)', '    ft = fit_train(np.vstack([YT, YE]), np.concatenate([cT, cE]), lam=lam)',
     ["e2e"], "common"),
    ("X05 EVAL items with an EVAL-refitted theta", '    aE, bE, itE, mxE = fit_items(YE, cE, ft["theta"], lam)',
     '    aE, bE, itE, mxE = fit_items(YE, cE, fit_train(YE, cE)["theta"], lam)', ["e2e"], "common"),
    ("X06 guessing floors swapped (GPQA 1/10, MMLU_PRO 1/4)", 'FLOOR = {"GPQA": 0.25, "MMLU_PRO": 0.10}', 'FLOOR = {"GPQA": 0.10, "MMLU_PRO": 0.25}',
     ["irt", "constants"], "common"),
    ("X07 R2 denominator centred (not sum e^2)", "        return 1.0 - Si.sum() / Ti.sum()", "        return 1.0 - Si.sum() / ((eE - eE.mean(axis=0)) ** 2).sum()",
     ["e2e"], "self"),
    ("X08 RWS p97.5 -> p95", '    st["p975"] = U.pct(srt, R()["q"])', '    st["p975"] = U.pct(srt, 0.95)', ["e2e"], "self"),
    ("X09 RP1 >= instead of >", '    beyond = bool(raf > st["p975"])', '    beyond = bool(raf >= st["p975"])', ["branches"], "self"),
    ("X10 RWS seeds 20261004 + 0..199", '    for r in range(1, R()["n_rws"] + 1):', '    for r in range(R()["n_rws"]):', ["e2e"], "self"),
    ("X11 RWS profile over every position (EVAL too)", "        for k in D.T:\n            if D.src[k] == s:", "        for k in range(D.n):\n            if D.src[k] == s:",
     ["e2e"], "common"),
    ("X12 RWS EVAL filing uniform (not TRAIN size weights)", "rng.choice(len(w), size=len(epos), p=w / w.sum())", "rng.choice(len(w), size=len(epos))",
     ["e2e"], "common"),
    ("X13 RP2 AF-BETTER without the interval clause", "    if lo > 0 and D > spread:", "    if D > spread:", ["branches"], "self"),
    ("X14 RP2 AF-BETTER without the spread clause", "    if lo > 0 and D > spread:", "    if lo > 0:", ["branches"], "self"),
    ("X15 RP2 K0-BETTER against +spread", "    if hi < 0 and D < -spread:", "    if hi < 0 and D < spread:", ["branches"], "self"),
    ("X16 D against K0 only (seed-0-only)", '    st["D"] = st["pt"]["AF-U"]["r2"] - float(np.mean(ks))', '    st["D"] = st["pt"]["AF-U"]["r2"] - ks[0]', ["e2e"], "self"),
    ("X17 spread_K = max (not max - min)", '    st["spread"] = float(max(ks) - min(ks))', '    st["spread"] = float(max(ks))', ["e2e"], "self"),
    ("X18 uncapped fork: theta / items NOT re-fitted per replicate",
     '        ft = RSC.fit_train(YT[sel], cT[sel], w=w[sel], theta=I["theta"], alpha=I["aT"][sel], b=I["bT"][sel])',
     '        ft = dict(theta=I["theta"], alpha=I["aT"][sel], b=I["bT"][sel], converged=True)', ["e2e"], "self"),
    ("X19 replicate cell means ignore the TRAIN multiplicities", "vals[nm] = arm_r2(eT, eE, g[T][sel], g[E], ng, w=w[sel],",
     "vals[nm] = arm_r2(eT, eE, g[T][sel], g[E], ng, w=None,", ["e2e"], "self"),
    ("X20 replicate R2 ignores the EVAL weights", "w=w[sel], v=np.asarray(v, dtype=np.float64))", "w=w[sel], v=None)", ["e2e"], "self"),
    ("X21 interval from the i.i.d. SE", '    st["lo"], st["hi"] = st["D"] - 1.96 * st["se2"], st["D"] + 1.96 * st["se2"]',
     '    st["lo"], st["hi"] = st["D"] - 1.96 * st["se_iid"], st["D"] + 1.96 * st["se_iid"]', ["e2e"], "self"),
    ("X22 raw-y version centred on the EVAL marginal", '    out = {}\n    pbar = I["YT"].mean(axis=0)', '    out = {}\n    pbar = I["YE"].mean(axis=0)',
     ["e2e"], "self"),
    ("X23 P4 largest -> smallest share", '        top = max(st["shares"], key=lambda s: st["shares"][s]["share"])',
     '        top = min(st["shares"], key=lambda s: st["shares"][s]["share"])', ["branches"], "self"),
    ("X24 P2 Brier against 1 - p", 'RSC.brier(PRED["P2"], beyond)', 'RSC.brier(1 - PRED["P2"], beyond)', ["branches"], "self"),
    ("X25 prediction bands open at the ends", "    return bool(band[0] <= x <= band[1])", "    return bool(band[0] < x < band[1])", ["branches"], "common"),
    ("X26 F-RP FIRED line omitted", '        L.append("F-RP: FIRED (RP1 NOT-BEYOND): once difficulty',
     '        (lambda *_: None)("F-RP: FIRED (RP1 NOT-BEYOND): once difficulty', ["null_e2e"], "self"),
    ("X27 identity (point) check off", '    if any(got[x] != k[x] for x in ("c1", "gaf", "best", "tdom", "af")):', "    if False:", ["refusals"], "common"),
    ("X28 identity (two-stage C1 interval) check off", "    if got != want:", "    if False:", ["refusals"], "self"),
    ("X29 B3 check off", '        refuse(tag, "[B3] the point policy', '        (lambda *a: None)(tag, "[B3] the point policy', ["refusals"], "common"),
    ("X30 outcome opened 'w'", "    return U.G.write_once(path, text)", "    open(path, 'w', encoding='utf-8').write(text)\n    return path", ["refusals"], "self"),
    ("X31 prelude write-once check removed", "    if not dry:\n        U.write_once_check(outs, tag)", "    if False:\n        U.write_once_check(outs, tag)",
     ["e2e", "refusals"], "common"),
    ("X32 dry-run reads the TRAIN key", '    models, tmeta, _c, _K, ntr = read_train(root, say, tag, pol["roster"], False)',
     '    models, tmeta, _c, _K, ntr = read_train(root, say, tag, pol["roster"], True)', ["dry_run"], "common"),
    ("X33 pre-pass AFTER the EVAL key read", '''    if between is not None:
        between(models, tmeta, K_tr)
    E = U.eval_set(root, say, tag, roster=pol["roster"], key=True, marker=marker)''', '''    E = U.eval_set(root, say, tag, roster=pol["roster"], key=True, marker=marker)
    if between is not None:
        between(models, tmeta, K_tr)''', ["e2e"], "common"),
    ("X34 pre-pass SD on H1 (the half the means came from)", "        S[nm], T = terms(e[h2], g[h2], eb)", "        S[nm], T = terms(e[h1], g[h1], eb)", ["e2e"], "self"),
    ("X35 pre-pass SE without the declared DEFF", '    n_eff = U.C()["n_eval"] / R()["deff_plan"]', '    n_eff = U.C()["n_eval"]', ["e2e"], "self"),
    ("X36 TRAIN-only guard off", "    if bad:\n        raise SystemExit(\"[TRAIN-ONLY]", "    if False:\n        raise SystemExit(\"[TRAIN-ONLY]", ["refusals"], "common"),
    ("X37 identity test on a numpy bool", '    beyond = bool(raf > st["p975"])\n    if beyond:', '    beyond = raf > st["p975"]\n    if beyond is True:', ["e2e"], "self"),
    ("X38 RP1 read from the declared arm", '    raf = pt["AF-U"]["r2"]\n    L = ["", "== RP1', '    raf = pt["declared"]["r2"]\n    L = ["", "== RP1', ["e2e"], "self"),
    ("X39 K arms read from the AF-U cells", '        g, ng = D.groupings["x:" + nm]', "        g, ng = D.g_tree, len(D.tree_keys)", ["e2e"], "common"),
    ("X40 identity C1 read from the AF-U arm", '    acc_d = float(routed("tdom", D.g_tdom).mean())', '    acc_d = float(routed("tree", D.g_tree).mean())', ["e2e"], "common"),
    ("X41 TRAIN key without the MATH-FIX overlay", 'K, kst = V.read_key(tw, "response_lite", c["cv"], models, meta, True, c["rule"])',
     'K, kst = V.read_key(tw, "response_lite", c["cv"], models, meta, False, c["rule"])', ["e2e"], "common"),
    ("X42 P3 Brier on the complement", 'RSC.brier(PRED["P3"], w == "NEITHER")', 'RSC.brier(PRED["P3"], w != "NEITHER")', ["branches"], "self"),
    ("X43 P4 share over the source's item count", '        shares[s] = dict(share=float(X[mk].sum() / tot) if tot > 0',
     '        shares[s] = dict(share=float(X[mk].sum() / mk.sum()) if tot > 0', ["e2e"], "self"),
    ("X44 the replicate's EVAL items keep the point parameters", '        aE, bE, _i, _m = RSC.fit_items(YE, cE, ft["theta"], alpha=I["aE"], b=I["bE"])',
     '        aE, bE = I["aE"], I["bE"]', ["e2e"], "self"),
)

if __name__ == "__main__":
    sys.exit(main())
