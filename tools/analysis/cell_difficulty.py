"""cell_difficulty.py: CELL-DIFFICULTY -- are AF-U cells difficulty strata (share of EVAL item-difficulty variance explained by
cell, out-of-sample, vs random within-source cells), and do the 7 BH-surviving CELL-FLIPS cells survive a 1-D 3PL expectation
(evidence of more than one ability dimension)? ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — CELL-DIFFICULTY: are AF-U cells difficulty strata
  ..." L24402-L24414 (_as_of 633255f2): CD1 (DECIDING), CD2 (scored count; carries F-CD), Support (a)-(g), P1-P3, F-CD.
  Source: docs/literature/2026-10-04_response_structure.md T-R4. AF-U is [SC]; K_0, SRC and RWS are [SC]; declared [DECL] (cross).
  The 7 flip cells are CELL-FLIPS' (L24183-L24194; POSTRUN 4120f15a; its outcome sha256 03383314..., read and checked here).

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, or anywhere with --data-root <main checkout>; POOL READER, rule 7):
  0. python tools/analysis/cell_difficulty.py --selftest      # synthetic sealed fixture views under E:/TaxoArena_tmp; NO DB of record
     python tools/analysis/cell_difficulty.py --mutants       # the mutant table, re-run
  1. python tools/analysis/cell_difficulty.py --dry-run       # POOL line first; pins; policy; cells; the CELL-FLIPS cells; denominators
  2. python tools/analysis/cell_difficulty.py --run           # ONE TRAIN key read, ONE EVAL key read (B1 marker); outcome WRITE-ONCE:
       experiment_results/archv2/cell_difficulty/cell_difficulty_outcome.txt (+ cell_difficulty.READ_STARTED); never committed
  CPU: minutes. Then the reviewer, the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; write-once paths absent; (2) pins (this file, resp_structure_common, union_cells_io 92a04543, cell_flips 998d39a7,
  union_af_route bf3f17db, v2_declared_cells f0f56805); (3) the frozen policy 8d68018c..., the inputs manifest 53021e26..., the
  cells; (4) the CELL-FLIPS outcome (sha256 pinned) and its 7 "FLIP AF-U" lines, which must equal the 7 registered (cell,
  challenger, n, D_c); (5) the TRAIN key; the EVAL key (B1 marker; 5,907 / 5,404); (6) B3 + IDENTITY at the point; every flip
  cell's challenger = the frozen pick, its EVAL n and D_c recomputed equal to CELL-FLIPS' (refused otherwise); (7) the 3PL;
  eta2_b for AF-U, K0..K4, SRC, declared and 200 RWS draws; the composition share per model; the parametric bootstrap of the 7
  flip cells and BH; (8) CD1, CD2, F-CD, descriptive lines, predictions, Support; the outcome written (mode "x").

READINGS (stated, for the READY to confirm or refuse; none chosen silently):
  CD-R1 eta2_b(arm) = 1 - sum_{EVAL i} (b_i - bbar_c(i))^2 / sum_{EVAL i} (b_i - mean_EVAL b)^2; b_i = the EVAL item's 3PL difficulty
        (theta fixed from TRAIN, IRT-R2); bbar_c = the mean of the TRAIN items' b (the TRAIN fit, IRT-R1) in cell c, unshrunk (the
        registration fixes no shrinkage here); a cell with no TRAIN item takes the TRAIN grand mean of b. Out-of-sample; it can be < 0.
  CD-R2 composition share of model m = V_pred / (V_pred + V_res) over the AF-U cells that hold EVAL items, weighted by EVAL n_c:
        acc_cm = model m's EVAL accuracy in c; pred_cm = the mean 3PL probability P_im over c's EVAL items; V_pred = weighted variance
        of pred_cm across cells, V_res = weighted variance of acc_cm - pred_cm (the interaction part); the registered statistic is
        the median over the 18 models (a model with V_pred + V_res = 0 is NaN and dropped, counted).
  CD-R3 CD1's percentile: union_cells_io.pct (sorted[int(0.975 x 200) - 1]); DIFFICULTY-STRATA iff eta2_b(AF-U) > it (strict) AND the
        median share > 0.5 (strict); Monte Carlo SE of the percentile printed (2,000 resamples, default_rng(20261004)).
  CD-R4 Flip-cell parametric bootstrap: one default_rng(20261004) stream over the 7 cells in the registered order; per cell 1,000
        replicates of y*_ich ~ Bernoulli(P_ich), y*_ig ~ Bernoulli(P_ig) independently for every EVAL item of the cell (g = the
        frozen best single, ch = the frozen challenger; P from the fitted 1-D 3PL: TRAIN theta, EVAL item parameters; no refit);
        D* = mean(y*_ch - y*_g); p = k / 1,000, k = #{D* >= D_obs} (the registered resolution 0.001; a 0 is printed as 0.000);
        BH step-up at q 0.05 over the 7 (cell_flips.bh); MULTIDIM iff rejected. The 1-D expectation mean(P_ch - P_g) is printed.
  CD-R5 Predictions: "X [lo, hi]" HELD iff lo <= X <= hi (closed); CD1's probability by Brier; P2's ">= 4 of 7" printed as HELD /
        FAILED (no probability registered for it).
  CD-R7 DESCRIPTIVE control (added, not registered; no verdict reads it): the CD-R4 test on every other AF-U cell with a frozen
        challenger != g and EVAL n >= 20, on default_rng(20261004 + 1); the share with p < 0.05 shows how often the fitted 1-D model
        "rejects" a non-flip cell. CAVEAT for the READY: the registered ridge (lambda 1.0, on b and log a) pulls extreme item
        difficulties toward 0, so on near-ceiling cells the 1-D expectation for a weaker challenger is too low and D_obs can sit
        above it without any second dimension (seen on the selftest fixture); the control measures that rate.
  [DELTA 2026-10-04 resp-structure-fix1, READY_resp_structure B-CD2 and claim 11; insertion only]
  CD-R8 CD2 and F-CD's CD2 leg are printed as DESCRIPTIVE (the registrar's demotion: the 7 cells were selected on the same EVAL
        D_c, and a 1-D null with theta_ch <= theta_g has mean <= 0, so CD2 is a CONSISTENCY CHECK of CF1 under a 3PL null, not
        evidence of more than one ability dimension); CD1 decides alone; P2 is scored with that qualifier. The computation of CD2
        (CD-R4) is unchanged.
  CD-R9 Per-task guessing floors (DESCRIPTIVE sensitivity; the registered floors stay "fixed now"): BBH / MUSR items take 1 /
        options from a STATED table of the standard task formats (TASK_OPTIONS; 0 = free-form or variable, floor 0; unlisted tasks
        keep the registered floor and are counted); theta, TRAIN and EVAL items re-fitted under them; the CD-R4 test on the flip
        cells on its own stream default_rng(20261004 + 2) and BH; the EVAL item count per floor value is printed.
  CD-R6 The common hygiene's two-stage bootstrap (B 2,000) has no consumer here: no CD criterion reads an interval; it is not run.
  Not applicable (stated): no judge verdict (keyed correctness): no wrong(established), no tie conventions; no call cache, --pilot or
  truncation guard (zero calls).

SELFTEST (--selftest; fixtures on E: through scratch_dir): the sealed gen / eval fixture views of resp_structure_common (6 models,
4 sources, floors, MATH-FIX overlay, twins, out-of-set items), policy, manifest, cells, a CELL-FLIPS stub; pool check stubbed.
  irt         IRT-R1 / IRT-R2 against scipy
  constants   the REAL registered constants (200 RWS draws on 20261004 + r, p97.5, 1,000 replicates, seed 20261004, BH q 0.05, bar 0.5;
              the 7 registered flip cells)
  e2e         run() on the PLANTED fixture (difficulty strata; m2 +4 logits in two AF-U cells): every arm's eta2_b, the RWS p97.5, the
              median composition share and each model's share, every flip cell's expectation, k and p against an independent loop
              oracle; CD1 DIFFICULTY-STRATA; CD2 2 of 3 MULTIDIM by BH; F-CD NOT FIRED; predictions by value; outcome = printed; a
              second run refused
  null_e2e    run() on the NULL fixture (one difficulty centre, no interaction): CD1 NOT-DIFFICULTY-STRATA, CD2 0, F-CD FIRED
  branches    CD1 (both conditions, strict edges), CD2 / F-CD, P1-P3 bands, n/a lines by value on synthetic st
  refusals    the CELL-FLIPS outcome sha, a registered flip line not matching the outcome, a flip cell's D_c / challenger not
              matching the data, identity, B3, pool rc 1 (POOL line first), write-once outcome / marker, write_outcome on an
              existing path; no outcome written
  dry_run     POOL line first; denominators; the flip cells listed; no key read; nothing written
  branch_cover every print branch registered in BRANCHES was executed
MUTANTS: see MUTANTS at the end (run with --mutants; the table with the result is in the commit message).
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import json          # noqa: E402
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
TAG = "[CELL-DIFFICULTY]"
TEST_ID = "CELL-DIFFICULTY"
REG_TXT = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — CELL-DIFFICULTY: are AF-U cells difficulty'
           ' strata ..." L24402-L24414 (_as_of 633255f2)')
RP_ = dict(n_rws=200, rws_seed=20261004, q=0.975, n_boot=1000, flip_seed=20261004, bh_q=0.05, bar=0.5,
           out_dir="experiment_results/archv2/cell_difficulty", outcome="cell_difficulty_outcome.txt", marker="cell_difficulty.READ_STARTED")
_RP = [RP_]
PRED = dict(P1=0.60, P2=(2, 7), P2_min=4, P3=(0.4, 0.8))
ARMS = ("AF-U",) + RSC.KNAMES + ("SRC", "declared")
HIT = Counter()
BRANCHES = ("CD1.STRATA", "CD1.NOT", "FCD.FIRED", "FCD.NOT_FIRED", "P3.SCORED", "P3.UNSCORED", "DRY.DONE", "RUN.DONE")


def hit(name):
    HIT[name] += 1


def R():
    return _RP[0]


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ── the CELL-FLIPS cells ───────────────────────────────────────────────────────────────────────────────────────────────
def flip_cells(root, say):
    """The 7 BH-surviving AF-U cells: the CELL-FLIPS outcome (sha256 pinned) parsed and checked against the registered list."""
    k = RSC.K()
    p = U.P(root, k["flips_rel"])
    if not os.path.isfile(p):
        refuse("the CELL-FLIPS outcome %s is absent" % k["flips_rel"])
    sh = RSC.sha256_bytes(p)
    if sh != k["flips_sha"]:
        refuse("the CELL-FLIPS outcome is sha256 %s, not the pinned %s" % (sh, k["flips_sha"]))
    got = []
    for ln in open(p, encoding="utf-8").read().split("\n"):
        q = ln.split()
        if len(q) >= 11 and q[0] == "FLIP" and q[1] == "AF-U":
            got.append((q[2], q[6], int(q[4]), q[8]))
    want = [tuple(x) for x in k["flips"]]
    if got != want:
        refuse("the CELL-FLIPS outcome's FLIP AF-U lines %s are not the registered %d cells %s" % (got, len(want), want))
    say("%s CELL-FLIPS cells (outcome %s sha256 %s = the pin; %d FLIP AF-U lines = the registered list): %s" % (
        TAG, k["flips_rel"], sh, len(got), "; ".join("%s (challenger %s, n %d, D_c %s)" % x for x in got)))
    return got


# ── the statistics ──────────────────────────────────────────────────────────────────────────────────────────────────────
def eta2(bT, bE, gT, gE, ng):
    """CD-R1."""
    s = np.bincount(gT, weights=bT, minlength=ng)
    n = np.bincount(gT, minlength=ng)
    mu = np.where(n > 0, s / np.maximum(n, 1), bT.mean())
    return 1.0 - ((bE - mu[gE]) ** 2).sum() / ((bE - bE.mean()) ** 2).sum()


def composition(YE, PE, gE, ng):
    """CD-R2 -> (per-model shares, V_pred, V_res)."""
    n = np.bincount(gE, minlength=ng).astype(np.float64)
    keep = n > 0
    acc = np.zeros((ng, YE.shape[1]))
    pred = np.zeros((ng, YE.shape[1]))
    np.add.at(acc, gE, YE)
    np.add.at(pred, gE, PE)
    acc, pred, w = acc[keep] / n[keep, None], pred[keep] / n[keep, None], n[keep] / n[keep].sum()

    def wvar(x):
        mu = (w[:, None] * x).sum(axis=0)
        return (w[:, None] * (x - mu) ** 2).sum(axis=0)
    vp, vr = wvar(pred), wvar(acc - pred)
    tot = vp + vr
    share = np.where(tot > 0, vp / np.where(tot > 0, tot, 1.0), np.nan)
    return share, vp, vr


def one_cell(rng, I, idx, ci, gi, B):
    """CD-R4 for one cell: B replicates from the fitted 1-D 3PL -> dict(D, exp, k, p, sim_mean, sim_p95)."""
    yc, yg = I["YE"][idx, ci], I["YE"][idx, gi]
    Dobs = float((yc - yg).mean())
    pc, pg = I["PE"][idx, ci], I["PE"][idx, gi]
    sc = (rng.random((B, len(idx))) < pc[None, :]).astype(np.float64)
    sg = (rng.random((B, len(idx))) < pg[None, :]).astype(np.float64)
    Ds_ = (sc - sg).mean(axis=1)
    k = int((Ds_ >= Dobs - 1e-9).sum())
    return dict(n=len(idx), D=Dobs, exp=float((pc - pg).mean()), k=k, p=k / B, sim_mean=float(Ds_.mean()),
                sim_p95=float(np.percentile(Ds_, 95)))


def flip_boot(D, I, flips, g):
    """CD-R4."""
    rng = np.random.default_rng(R()["flip_seed"])
    gi = D.models.index(g)
    names = list(D.tree_keys)
    gE = D.g_tree[D.E]
    rows = []
    for cell, ch, n, Ds in flips:
        r = one_cell(rng, I, np.flatnonzero(gE == names.index(cell)), D.models.index(ch), gi, R()["n_boot"])
        r.update(cell=cell, ch=ch)
        rows.append(r)
    return mark_bh(rows)


def mark_bh(rows):
    """BH step-up at q 0.05 over the flip cells (cell_flips.bh); MULTIDIM iff rejected."""
    rej = RSC.CF.bh([r["p"] for r in rows], R()["bh_q"])
    for r, f in zip(rows, rej):
        r["multi"] = bool(f)
    return rows


# [DELTA B-CD2 / claim 11, READY_resp_structure; insertion only] per-task guessing floors as a DESCRIPTIVE sensitivity. The
# registered floors stay "fixed now" (GPQA 1/4, MMLU_PRO 1/10, else 0). Options per task from the standard BBH / MuSR formats,
# a STATED table, not re-read from the data; 0 = free-form or a variable option count (floor left at 0). Unlisted tasks keep the
# registered floor; their EVAL item count is printed.
TASK_OPTIONS = {
    "BBH": {"boolean_expressions": 2, "causal_judgement": 2, "date_understanding": 6, "disambiguation_qa": 3, "dyck_languages": 0,
            "formal_fallacies": 2, "geometric_shapes": 0, "hyperbaton": 2, "logical_deduction_five_objects": 5,
            "logical_deduction_seven_objects": 7, "logical_deduction_three_objects": 3, "movie_recommendation": 5,
            "multistep_arithmetic_two": 0, "navigate": 2, "object_counting": 0, "penguins_in_a_table": 5,
            "reasoning_about_colored_objects": 18, "ruin_names": 4, "salient_translation_error_detection": 6, "snarks": 2,
            "sports_understanding": 2, "temporal_sequences": 4, "tracking_shuffled_objects_five_objects": 5,
            "tracking_shuffled_objects_seven_objects": 7, "tracking_shuffled_objects_three_objects": 3, "web_of_lies": 2,
            "word_sorting": 0},
    "MUSR": {"murder_mysteries": 2, "object_placements": 0, "team_allocation": 3},
}
_TASK = [TASK_OPTIONS]


def task_floor(src, dom):
    """The sensitivity's floor of one item: 1 / options for a listed BBH / MUSR task with options > 0, else the registered floor."""
    k = _TASK[0].get(src, {}).get(dom)
    if k:
        return 1.0 / k
    return RSC.FLOOR.get(src, 0.0)


def task_floor_sensitivity(D, flips, pol):
    """DESCRIPTIVE: the CD2 test re-run under per-task floors: TRAIN theta and items, EVAL items re-fitted with those floors;
    one_cell on the flip cells on its own stream default_rng(flip_seed + 2); BH over them. The registered CD2 is untouched."""
    RSC.assert_train(D, D.T)
    cT = np.array([task_floor(D.src[k], D.dom[k][1]) for k in D.T])
    cE = np.array([task_floor(D.src[k], D.dom[k][1]) for k in D.E])
    YT, YE = D.A[D.T].astype(np.float64), D.A[D.E].astype(np.float64)
    ft = RSC.fit_train(YT, cT)
    aE, bE, _i, _m = RSC.fit_items(YE, cE, ft["theta"])
    I2 = dict(YE=YE, PE=RSC.prob(ft["theta"], aE, bE, cE))
    rng = np.random.default_rng(R()["flip_seed"] + 2)
    g = pol["best_single"]
    gi = D.models.index(g)
    names = list(D.tree_keys)
    gE = D.g_tree[D.E]
    rows = []
    for cell, ch, n, Ds in flips:
        r = one_cell(rng, I2, np.flatnonzero(gE == names.index(cell)), D.models.index(ch), gi, R()["n_boot"])
        r.update(cell=cell, ch=ch)
        rows.append(r)
    mark_bh(rows)
    per = Counter("%.4f" % x for x in cE)
    unl = sum(1 for k in D.E if D.src[k] in _TASK[0] and D.dom[k][1] not in _TASK[0][D.src[k]])
    return dict(rows=rows, n=int(sum(1 for r in rows if r["multi"])), per=dict(sorted(per.items())), unlisted=unl,
                converged=bool(ft["converged"]))


def calibration(D, I, pol, flips):
    """CD-R7 (DESCRIPTIVE control, not registered): the same 1-D test on every AF-U cell with a frozen challenger != g and EVAL
    n >= 20 (CELL-FLIPS' TESTED rule), on its own stream default_rng(flip_seed + 1) so the registered stream is untouched: the
    share with p < 0.05 (uncorrected) among the non-flip cells is the test's false-positive rate under the fitted model's misfit."""
    rng = np.random.default_rng(R()["flip_seed"] + 1)
    g = pol["best_single"]
    gi = D.models.index(g)
    gE = D.g_tree[D.E]
    fl = set(c for c, _ch, _n, _d in flips)
    out = []
    for j, cell in enumerate(D.tree_keys):
        ch = pol["tree_cell"].get(cell)
        idx = np.flatnonzero(gE == j)
        if ch in (None, g) or len(idx) < 20 or cell in fl:
            continue
        r = one_cell(rng, I, idx, D.models.index(ch), gi, R()["n_boot"])
        out.append(r["p"])
    return dict(n=len(out), n05=int(sum(1 for p in out if p < 0.05)))


def check_flips(D, pol, flips):
    """Each flip cell: challenger = the frozen pick, EVAL n and D_c recomputed = CELL-FLIPS'; challenger != best single."""
    g = pol["best_single"]
    names = list(D.tree_keys)
    gE = D.g_tree[D.E]
    gi = D.models.index(g)
    for cell, ch, n, Ds in flips:
        if cell not in names:
            refuse("CELL-FLIPS cell %s is not an AF-U cell of the scored set" % cell)
        if pol["tree_cell"].get(cell) != ch or ch == g:
            refuse("CELL-FLIPS cell %s: challenger %s is not the frozen pick %s (or is the best single %s)" % (
                cell, ch, pol["tree_cell"].get(cell), g))
        idx = np.flatnonzero(gE == names.index(cell))
        ci = D.models.index(ch)
        d = "%+.4f" % float((D.A[D.E][idx, ci] - D.A[D.E][idx, gi]).mean())
        if len(idx) != n or d != Ds:
            refuse("CELL-FLIPS cell %s: EVAL n %d / D_c %s recomputed, not CELL-FLIPS' %d / %s" % (cell, len(idx), d, n, Ds))


def analyze(D, I, arms, flips, pol):
    c = R()
    T, E = D.T, D.E
    st = dict(N=len(E), G=D.eval_units["n_units"], M=len(D.models), NT=len(T), g=pol["best_single"], models=list(D.models))
    st["eta"] = {nm: eta2(I["bT"], I["bE"], arms[nm][0][T], arms[nm][0][E], arms[nm][1]) for nm in ARMS}
    prof = RSC.rws_profile(D, arms["AF-U"][0])
    st["rws"] = []
    for r in range(1, c["n_rws"] + 1):
        g, ng = RSC.rws_cells(D, prof, c["rws_seed"] + r)
        st["rws"].append(eta2(I["bT"], I["bE"], g[T], g[E], ng))
    st["p975"] = U.pct(sorted(st["rws"]), c["q"])
    st["p975_se"] = RSC.mc_se_pct(st["rws"], c["q"])
    st["rws_med"] = float(np.median(st["rws"]))
    share, vp, vr = composition(I["YE"], I["PE"], arms["AF-U"][0][E], arms["AF-U"][1])
    st["share"], st["vp"], st["vr"] = share, vp, vr
    ok = share[np.isfinite(share)]
    st["share_n"], st["share_nan"] = int(len(ok)), int(len(share) - len(ok))
    st["share_med"] = float(np.median(ok)) if len(ok) else float("nan")
    st["flips"] = flip_boot(D, I, flips, pol["best_single"])
    st["cd2"] = int(sum(1 for r in st["flips"] if r["multi"]))
    st["calib"] = calibration(D, I, pol, flips)
    st["sens"] = task_floor_sensitivity(D, flips, pol)
    st["kish"] = RSC.support_deff(D)
    return st


# ── the printed readout ─────────────────────────────────────────────────────────────────────────────────────────────────
def f4(x):
    return "%+.4f" % x


def verdict_lines(st):
    c = R()
    e = st["eta"]["AF-U"]
    L = ["", "== CD1 (DECIDING; the POINT against the RWS percentile AND the composition bar, one clause) =="]
    L.append("  eta2_b(AF-U) = %s; RWS (%d random within-source cell sets at AF-U's per-source size profile, default_rng(%d + r),"
             " r = 1..%d): median %s, p97.5 %s (Monte Carlo SE %.4f)" % (f4(e), c["n_rws"], c["rws_seed"], c["n_rws"], f4(st["rws_med"]),
                                                                       f4(st["p975"]), st["p975_se"]))
    L.append("  median composition share over %d models (NaN dropped: %d) = %.4f (bar %.1f)" % (st["share_n"], st["share_nan"],
                                                                                            st["share_med"], c["bar"]))
    a = bool(e > st["p975"])
    b = bool(st["share_med"] > c["bar"])
    ds = a and b
    if ds:
        hit("CD1.STRATA")
        L.append("CD1: DIFFICULTY-STRATA: eta2_b(AF-U) %s is above the RWS p97.5 %s AND the median composition share %.4f is above %.1f:"
                 " AF-U cells sort items by difficulty beyond random cells of the same sizes, and most of a model's accuracy"
                 " differences across cells is difficulty composition" % (f4(e), f4(st["p975"]), st["share_med"], c["bar"]))
    else:
        hit("CD1.NOT")
        L.append("CD1: NOT-DIFFICULTY-STRATA: eta2_b above the RWS p97.5: %s (%s vs %s); median composition share above %.1f: %s (%.4f)"
                 " (FAILS for DIFFICULTY-STRATA, rule 8)" % ("yes" if a else "NO", f4(e), f4(st["p975"]), c["bar"], "yes" if b else "NO",
                                                              st["share_med"]))
    L.append("")
    L.append("== CD2 (DESCRIPTIVE, B-CD2 of READY_resp_structure: a CONSISTENCY CHECK of CF1 under a 3PL null; the cells were selected"
             " on the same EVAL D_c, so it is not evidence of more than one ability dimension; CD1 decides alone) ==")
    L.append("  per cell: %d parametric replicates from the fitted 1-D 3PL (default_rng(%d), one stream in the registered order); p = k /"
             " %d, k = #{D* >= D_obs}; BH q %.2f over %d" % (c["n_boot"], c["flip_seed"], c["n_boot"], c["bh_q"], len(st["flips"])))
    for r in st["flips"]:
        L.append("  FLIPCELL %-26s n %3d  challenger %-28s D_obs %s  1-D expectation %s  sim mean %s p95 %s  k %4d  p %.3f  %s" % (
            r["cell"], r["n"], r["ch"], f4(r["D"]), f4(r["exp"]), f4(r["sim_mean"]), f4(r["sim_p95"]), r["k"], r["p"],
            "MULTIDIM" if r["multi"] else "1-D-REPRODUCIBLE"))
    L.append("CD2 (descriptive): %d of %d CELL-FLIPS cells are MULTIDIM (BH q %.2f)" % (st["cd2"], len(st["flips"]), c["bh_q"]))
    if st["cd2"] == 0:
        hit("FCD.FIRED")
        L.append("F-CD (its CD2 leg DESCRIPTIVE, B-CD2; no falsifier verdict): CD2 = 0: every CELL-FLIPS flip is reproducible under the"
                 " fitted 3PL null (guessing, ceiling or null misfit)")
    else:
        hit("FCD.NOT_FIRED")
        L.append("F-CD (its CD2 leg DESCRIPTIVE, B-CD2; no falsifier verdict): CD2 = %d, not 0" % st["cd2"])
    L.append("")
    L.append("== DESCRIPTIVE (no verdict) ==")
    L.append("  eta2_b per arm: " + "; ".join("%s %s %s" % (nm, "[DECL]" if nm == "declared" else "[SC]", f4(st["eta"][nm])) for nm in ARMS)
             + "; K_0 mean %s" % f4(float(np.mean([st["eta"][k] for k in RSC.KNAMES]))))
    L.append("  composition split per model (V_pred / V_res / share): " + "; ".join(
        "%s %.5f / %.5f / %s" % (m, st["vp"][j], st["vr"][j], ("%.4f" % st["share"][j]) if np.isfinite(st["share"][j]) else "NaN")
        for j, m in enumerate(st["models"])))
    cb = st["calib"]
    L.append("  1-D calibration control (CD-R7, not registered): the same test on the %d other AF-U cells with a frozen challenger != g and"
             " EVAL n >= 20: %d with p < 0.05 (uncorrected; %s)" % (cb["n"], cb["n05"], ("%.3f" % (cb["n05"] / cb["n"])) if cb["n"] else "n/a"))
    sv = st["sens"]
    L.append("  per-task guessing floors (DESCRIPTIVE sensitivity, B-CD2 / claim 11; the registered floors are unchanged; stated BBH / MUSR"
             " option table): EVAL items per floor %s; BBH / MUSR EVAL items of unlisted tasks %d; TRAIN fit converged %s" % (
                 ", ".join("%s: %d" % kv for kv in sv["per"].items()), sv["unlisted"], "yes" if sv["converged"] else "NO"))
    for r in sv["rows"]:
        L.append("  TASKFLOOR %-26s 1-D expectation %s  k %4d  p %.3f  %s" % (r["cell"], f4(r["exp"]), r["k"], r["p"],
                                                                         "MULTIDIM" if r["multi"] else "1-D-REPRODUCIBLE"))
    L.append("  per-task floors: %d of %d CELL-FLIPS cells MULTIDIM (BH q %.2f; default_rng(%d + 2))" % (sv["n"], len(sv["rows"]), c["bh_q"],
                                                                                                    c["flip_seed"]))
    L.append("")
    L.append("== PREDICTIONS (registrar's priors; bands closed) ==")
    L.append("  P1 CD1 DIFFICULTY-STRATA 0.60: outcome %s -> Brier %.4f" % ("DIFFICULTY-STRATA" if ds else "NOT-DIFFICULTY-STRATA",
                                                                         RSC.brier(PRED["P1"], ds)))
    L.append("  P2 CD2 point 5 [2, 7] (scored with the B-CD2 qualifier: a consistency check of CF1, not a dimension claim): %d -> %s;"
             " >= 4 of 7 MULTIDIM: %d -> %s" % (st["cd2"], RSC.hw(st["cd2"], PRED["P2"]), st["cd2"],
                                                                              "HELD" if st["cd2"] >= PRED["P2_min"] else "FAILED"))
    if np.isfinite(st["share_med"]):
        hit("P3.SCORED")
        L.append("  P3 median composition share 0.6 [0.4, 0.8]: %.4f -> %s" % (st["share_med"], RSC.hw(st["share_med"], PRED["P3"])))
    else:
        hit("P3.UNSCORED")
        L.append("  P3 median composition share 0.6 [0.4, 0.8]: NOT SCOREABLE (no model with a non-zero cell variance)")
    L.append("")
    L.append("== SUPPORT (registered planning numbers; MEASURED beside) ==")
    L.append("  (a) EVAL %d items / %d components x %d models (registered 5,907 / 5,404); TRAIN %d; %d flip cells (named)" % (
        st["N"], st["G"], st["M"], st["NT"], len(st["flips"])))
    L.append("  (b) DEFF 1.6 declared pilot (two-stage); Kish mean EVAL component size %.4f; (c) n_eff 3,690 (registered)" % st["kish"])
    L.append("  (d) eta2_b's SE not claimed (percentile classification; Monte Carlo SE of the p97.5 %.4f over %d draws); per flip cell"
             " %d replicates (p resolution %.3f)" % (st["p975_se"], len(st["rws"]), c["n_boot"], 1.0 / c["n_boot"]))
    L.append("  (e) the flip cells' D_c %s at n %s (CELL-FLIPS 0.13-0.30 at 27-53); the 1-D expectations %s are the reference" % (
        "/".join("%.2f" % r["D"] for r in st["flips"]), "/".join(str(r["n"]) for r in st["flips"]),
        "/".join("%+.2f" % r["exp"] for r in st["flips"])))
    L.append("  (f) VERDICT LINE (registered, as bracketed by B-CD2): CD1 SCOREABLE as a classification and decides alone; CD2 DESCRIPTIVE"
             " (a consistency check of CF1). (g) STRUCTURAL: reachable;"
             " guessing floors fixed (not estimated) at 1/options.")
    L.append("  NOT APPLICABLE: wrong(established) and the tie conventions A / B (keyed correctness); the two-stage bootstrap (CD-R6).")
    L.append("  WHAT THIS RESULT WILL NOT SHOW (registered): a dimension count of the matrix; roster-independent difficulty; routing value.")
    return L


# ── modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def out_paths(root, out_dir):
    d = out_dir or U.P(root, R()["out_dir"])
    return os.path.join(d, R()["outcome"]), os.path.join(d, R()["marker"])


def planned(say):
    c = R()
    say("%s PLANNED: 3PL (floors GPQA 1/4, MMLU_PRO 1/10, else 0; ridge lambda %.1f; theta on TRAIN only); eta2_b arms %s; RWS %d draws"
        " (default_rng(%d + r), r = 1..%d); p97.5; composition bar %.1f; flip replicates %d (default_rng(%d)), BH q %.2f" % (
            TAG, RSC.LAMBDA, ", ".join(ARMS), c["n_rws"], c["rws_seed"], c["n_rws"], c["bar"], c["n_boot"], c["flip_seed"], c["bh_q"]))


def dry_run(root, out_dir=None, out=print):
    outp, mark = out_paths(root, out_dir)
    pol, af, kx = RSC.prelude(root, out, TAG, TEST_ID, REG_TXT, [os.path.abspath(__file__)], [outp, mark], True)
    flip_cells(root, out)
    RSC.dry_structure(root, out, TAG, pol, af, kx)
    planned(out)
    out("%s DRY-RUN complete: no key column selected (both tripwires sealed); no statistic; nothing written" % TAG)
    hit("DRY.DONE")


def write_outcome(path, text):
    return U.G.write_once(path, text)


def run(root, out_dir=None, out=print):
    lines = []

    def say(s):
        lines.append(s)
        out(s)
    outp, mark = out_paths(root, out_dir)
    pol, af, kx = RSC.prelude(root, say, TAG, TEST_ID, REG_TXT, [os.path.abspath(__file__)], [outp, mark], False)
    flips = flip_cells(root, say)
    planned(say)
    D = RSC.load_all(root, say, TAG, pol, af, kx, mark, "%s: the EVAL key read started (B1); policy sha256 %s" % (TAG, U.C()["policy_sha"]))
    RSC.b3_identity(D, pol, say, TAG)
    check_flips(D, pol, flips)
    say("%s the %d CELL-FLIPS cells re-derived on the scored set: challenger = the frozen pick, EVAL n and D_c = CELL-FLIPS'" % (TAG, len(flips)))
    I = RSC.irt_point(D, say, TAG)
    arms = RSC.arms_of(D)
    st = analyze(D, I, arms, flips, pol)
    for ln in verdict_lines(st):
        say(ln)
    text = "\n".join(lines) + "\n"
    write_outcome(outp, text)
    out("%s OUTCOME written write-once: %s" % (TAG, outp))
    hit("RUN.DONE")
    return st, text


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────
FX_RP = dict(RP_, n_rws=40, n_boot=400)


class _swap:
    def __init__(self, d):
        self.d = d

    def __enter__(self):
        self.old = _RP[0]
        _RP[0] = self.d

    def __exit__(self, *a):
        _RP[0] = self.old


def _oracle(X):
    O = RSC.fx_irt(X["rows"])
    tr, ev = O["tr"], O["ev"]

    def kf(nm):
        if nm == "AF-U":
            return lambda r: r["af"]
        if nm == "SRC":
            return lambda r: r["src"]
        if nm == "declared":
            return lambda r: (r["src"], r["dom"])
        return lambda r, s=int(nm[1]): X["kcells"][s][r["id"]]

    def eta_loop(f):
        sums, cnt = {}, {}
        for i, r in enumerate(tr):
            sums[f(r)] = sums.get(f(r), 0.0) + O["bT"][i]
            cnt[f(r)] = cnt.get(f(r), 0) + 1
        gm = float(np.mean(O["bT"]))
        me = float(np.mean(O["bE"]))
        num = sum((O["bE"][i] - (sums[f(r)] / cnt[f(r)] if f(r) in cnt else gm)) ** 2 for i, r in enumerate(ev))
        den = sum((O["bE"][i] - me) ** 2 for i in range(len(ev)))
        return 1.0 - num / den
    eta = {nm: eta_loop(kf(nm)) for nm in ARMS}
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
                for r, q in zip(eps, rng.choice(len(w), size=len(eps), p=w / w.sum())):
                    lab[r["id"]] = start[s] + q
        rws.append(eta_loop(lambda r: lab[r["id"]]))
    # composition by loops
    cells = sorted(set(r["af"] for r in ev))
    shares = []
    for j, m in enumerate(RSC.FX_MODELS):
        rows_ = []
        for c in cells:
            ii = [i for i, r in enumerate(ev) if r["af"] == c]
            a = sum(O["YE"][i, j] for i in ii) / len(ii)
            p = sum(O["PE"][i, j] for i in ii) / len(ii)
            rows_.append((len(ii), p, a - p))
        N = sum(x[0] for x in rows_)
        mp = sum(x[0] * x[1] for x in rows_) / N
        mr = sum(x[0] * x[2] for x in rows_) / N
        vp = sum(x[0] * (x[1] - mp) ** 2 for x in rows_) / N
        vr = sum(x[0] * (x[2] - mr) ** 2 for x in rows_) / N
        shares.append(vp / (vp + vr))
    # flips: the same stream, by loops
    rng = np.random.default_rng(FX_RP["flip_seed"])
    g = X["pol"]["best_single"]
    gi = RSC.FX_MODELS.index(g)
    fl = []
    for cell, ch, n, Ds in X["kconst"]["flips"]:
        ci = RSC.FX_MODELS.index(ch)
        ii = [i for i, r in enumerate(ev) if r["af"] == cell]
        Dobs = sum(O["YE"][i, ci] - O["YE"][i, gi] for i in ii) / len(ii)
        pc = np.array([O["PE"][i, ci] for i in ii])
        pg = np.array([O["PE"][i, gi] for i in ii])
        uc = rng.random((FX_RP["n_boot"], len(ii)))
        ug = rng.random((FX_RP["n_boot"], len(ii)))
        k = 0
        for b in range(FX_RP["n_boot"]):
            d = sum((1.0 if uc[b, t] < pc[t] else 0.0) - (1.0 if ug[b, t] < pg[t] else 0.0) for t in range(len(ii))) / len(ii)
            k += int(d >= Dobs - 1e-9)
        fl.append((cell, Dobs, float((pc - pg).mean()), k))
    return O, eta, rws, shares, fl


def st_constants():
    assert RP_["n_rws"] == 200 and RP_["rws_seed"] == 20261004 and RP_["q"] == 0.975 and RP_["n_boot"] == 1000
    assert RP_["flip_seed"] == 20261004 and RP_["bh_q"] == 0.05 and RP_["bar"] == 0.5
    assert PRED == dict(P1=0.60, P2=(2, 7), P2_min=4, P3=(0.4, 0.8))
    assert [c for c, _ch, _n, _d in RSC.KCONST["flips"]] == ["BBH:n00000066", "BBH:n00000067", "BBH:n00000105", "BBH:n00000124",
                                                             "BBH:n00000159", "MMLU_PRO_LB:n00000175", "MMLU_PRO_LB:n00000223"]
    assert RSC.KCONST["flips_sha"].startswith("03383314") and RSC.LAMBDA == 1.0


FX_GEN = dict(scale=2.5, n_ev=(36, 44))      # wide difficulty centres, larger EVAL cells: the planted fixture is DIFFICULTY-STRATA


FX_TASK = {"BBH": {"d1": 2}, "MUSR": {}}      # the fixture's BBH domain d1 gets a 1/2 floor in the sensitivity


def _oracle_sens(X):
    """INDEPENDENT: per-task floors by loops from the fixture rows; the same IRT estimator; the flip test on stream flip_seed + 2."""
    tr, ev, YT, YE = RSC.fx_matrices(X["rows"])

    def fl_(r):
        k = FX_TASK.get(r["src"], {}).get(r["dom"])
        return 1.0 / k if k else RSC.FLOOR.get(r["src"], 0.0)
    cT, cE = np.array([fl_(r) for r in tr]), np.array([fl_(r) for r in ev])
    ft = RSC.fit_train(YT, cT)
    aE, bE, _i, _m = RSC.fit_items(YE, cE, ft["theta"])
    PE = RSC.prob(ft["theta"], aE, bE, cE)
    rng = np.random.default_rng(FX_RP["flip_seed"] + 2)
    gi = RSC.FX_MODELS.index(X["pol"]["best_single"])
    out = []
    for cell, ch, n, Ds in X["kconst"]["flips"]:
        ci = RSC.FX_MODELS.index(ch)
        ii = [i for i, r in enumerate(ev) if r["af"] == cell]
        Dobs = sum(YE[i, ci] - YE[i, gi] for i in ii) / len(ii)
        uc = rng.random((FX_RP["n_boot"], len(ii)))
        ug = rng.random((FX_RP["n_boot"], len(ii)))
        k = 0
        for b in range(FX_RP["n_boot"]):
            d = sum((1.0 if uc[b, t] < PE[ii[t], ci] else 0.0) - (1.0 if ug[b, t] < PE[ii[t], gi] else 0.0) for t in range(len(ii))) / len(ii)
            k += int(d >= Dobs - 1e-9)
        out.append((cell, float(np.mean([PE[i, ci] - PE[i, gi] for i in ii])), k))
    per = Counter("%.4f" % x for x in cE)
    return out, per


def st_e2e(tmp):
    root, X = RSC.build_fixture(tmp, **FX_GEN)
    od = os.path.join(tmp, "out")
    O, eta, rws, shares, fl = _oracle(X)
    sens, per = _oracle_sens(X)
    old_task = _TASK[0]
    _TASK[0] = FX_TASK
    try:
        with _swap(FX_RP), RSC.patched(X):
            (st, text), printed = RSC.capture(run, root, od)
    finally:
        _TASK[0] = old_task
    RSC.need(text, "EVAL items per floor %s;" % ", ".join("%s: %d" % kv for kv in sorted(per.items())))
    assert "0.5000" in per, "the sensitivity changes a floor on the fixture"
    for cell, ex, k in sens:
        RSC.need(RSC.line_with(text, "  TASKFLOOR %-26s" % cell), "1-D expectation %s  k %4d  p %.3f" % (f4(ex), k, k / FX_RP["n_boot"]))
    nb = sum(RSC.CF.bh([k / FX_RP["n_boot"] for _c, _e, k in sens], 0.05))
    RSC.need(text, "per-task floors: %d of %d CELL-FLIPS cells MULTIDIM" % (nb, len(sens)))
    with _swap(FX_RP), RSC.patched(X):
        outp, mk = out_paths(root, od)
        assert open(outp, encoding="utf-8").read() == text and os.path.isfile(mk)
        assert printed.split("\n")[0].startswith(TAG + " POOL pv_fx")
        el = RSC.line_with(text, "  eta2_b per arm: ")
        for nm in ARMS:
            RSC.need(el, "%s %s %s" % (nm, "[DECL]" if nm == "declared" else "[SC]", f4(eta[nm])))
        p975 = sorted(rws)[int(0.975 * len(rws)) - 1]
        med = float(np.median(shares))
        RSC.need(text, "eta2_b(AF-U) = %s; RWS" % f4(eta["AF-U"]), "median %s, p97.5 %s (Monte Carlo SE" % (f4(float(np.median(rws))), f4(p975)),
                 "median composition share over 6 models (NaN dropped: 0) = %.4f (bar 0.5)" % med)
        cl = RSC.line_with(text, "  composition split per model")
        for j, m in enumerate(RSC.FX_MODELS):
            RSC.need(cl, "%s " % m, " / %.4f" % shares[j])
        assert eta["AF-U"] > p975 and med > 0.5, "the planted fixture is DIFFICULTY-STRATA by the oracle"
        RSC.need(text, "CD1: DIFFICULTY-STRATA: eta2_b(AF-U) %s is above the RWS p97.5 %s AND the median composition share %.4f" % (
            f4(eta["AF-U"]), f4(p975), med))
        ps = []
        for cell, Dobs, ex, k in fl:
            ln = RSC.line_with(text, "  FLIPCELL %-26s" % cell)
            RSC.need(ln, "D_obs %s  1-D expectation %s" % (f4(Dobs), f4(ex)), "k %4d  p %.3f" % (k, k / FX_RP["n_boot"]))
            ps.append(k / FX_RP["n_boot"])
        m = len(ps)
        srt = sorted(ps)
        kk = max([r + 1 for r in range(m) if srt[r] <= (r + 1) * 0.05 / m] or [0])
        cut = srt[kk - 1] if kk else -1.0
        multi = [p <= cut for p in ps]
        assert multi[:2] == [True, True], ("the planted cells are MULTIDIM", ps)
        nmulti = sum(multi)
        for (cell, _d, _e, _k), mu in zip(fl, multi):
            assert RSC.line_with(text, "  FLIPCELL %-26s" % cell).endswith("MULTIDIM" if mu else "1-D-REPRODUCIBLE")
        RSC.need(text, "CD2 (descriptive): %d of %d CELL-FLIPS cells are MULTIDIM (BH q 0.05)" % (nmulti, m),
                 "F-CD (its CD2 leg DESCRIPTIVE, B-CD2; no falsifier verdict): CD2 = %d, not 0" % nmulti, "== CD2 (DESCRIPTIVE, B-CD2",
                 "P1 CD1 DIFFICULTY-STRATA 0.60: outcome DIFFICULTY-STRATA -> Brier 0.1600",
                 "a dimension claim): %d -> HELD; >= 4 of 7 MULTIDIM: %d -> FAILED" % (nmulti, nmulti),
                 "P3 median composition share 0.6 [0.4, 0.8]: %.4f -> %s" % (med, "HELD" if 0.4 <= med <= 0.8 else "FAILED"),
                 "the %d CELL-FLIPS cells re-derived on the scored set" % m)
        g = X["pol"]["best_single"]
        flc = set(c for c, _ch, _n, _d in X["kconst"]["flips"])
        ncal = sum(1 for c in sorted(set(r["af"] for r in O["ev"])) if c not in flc and X["pol"]["tree_cell"].get(c) not in (None, g)
                   and sum(1 for r in O["ev"] if r["af"] == c) >= 20)
        RSC.need(text, "the same test on the %d other AF-U cells with a frozen challenger != g" % ncal)
        try:
            RSC.capture(run, root, od)
            raise AssertionError("second run not refused")
        except SystemExit as e:
            assert "write-once" in str(e), e
        assert open(outp, encoding="utf-8").read() == text


def st_null(tmp):
    root, X = RSC.build_fixture(tmp, "null")
    od = os.path.join(tmp, "out")
    O, eta, rws, shares, fl = _oracle(X)
    p975 = sorted(rws)[int(0.975 * len(rws)) - 1]
    assert not (eta["AF-U"] > p975 and float(np.median(shares)) > 0.5)
    sens, _per = _oracle_sens(X)
    old_task = _TASK[0]
    _TASK[0] = FX_TASK
    try:
        with _swap(FX_RP), RSC.patched(X):
            (st, text), _p = RSC.capture(run, root, od)
    finally:
        _TASK[0] = old_task
    assert sens and all(k > 0 for _c, _e, k in sens), "the sensitivity's own stream is visible (k > 0)"
    for cell, ex, k in sens:
        RSC.need(RSC.line_with(text, "  TASKFLOOR %-26s" % cell), "1-D expectation %s  k %4d  p %.3f" % (f4(ex), k, k / FX_RP["n_boot"]))
    nb = sum(RSC.CF.bh([k / FX_RP["n_boot"] for _c, _e, k in sens], 0.05))
    assert nb < len(sens)
    RSC.need(text, "per-task floors: %d of %d CELL-FLIPS cells MULTIDIM" % (nb, len(sens)))
    assert fl and all(k > 0 for _c, _d, _e, k in fl)
    for cell, Dobs, ex, k in fl:
        ln = RSC.line_with(text, "  FLIPCELL %-26s" % cell)
        RSC.need(ln, "D_obs %s  1-D expectation %s" % (f4(Dobs), f4(ex)), "k %4d  p %.3f" % (k, k / FX_RP["n_boot"]), "1-D-REPRODUCIBLE")
    RSC.need(text, "CD1: NOT-DIFFICULTY-STRATA", "CD2 (descriptive): 0 of %d CELL-FLIPS cells are MULTIDIM" % len(fl),
             "F-CD (its CD2 leg DESCRIPTIVE, B-CD2; no falsifier verdict): CD2 = 0: every CELL-FLIPS flip is reproducible",
             "P1 CD1 DIFFICULTY-STRATA 0.60: outcome NOT-DIFFICULTY-STRATA -> Brier 0.3600", "a dimension claim): 0 -> FAILED")


def _syn(e=0.3, p975=0.1, med=0.6, cd2=5, nflip=7):
    fl = [dict(cell="c%d" % i, ch="x", n=40, D=0.2, exp=-0.05, sim_mean=-0.05, sim_p95=0.1, k=0, p=0.0, multi=i < cd2) for i in range(nflip)]
    sens = dict(rows=[dict(cell="c%d" % i, exp=-0.1, k=0, p=0.0, multi=i < 2) for i in range(3)], n=2, per={"0.0000": 10, "0.5000": 4},
                unlisted=3, converged=True)
    return dict(sens=sens, calib=dict(n=10, n05=1), N=5907, G=5404, M=18, NT=12000, g="g", models=["a", "b"], eta={nm: 0.1 for nm in ARMS} | {"AF-U": e}, rws=[0.0] * 200,
                p975=p975, p975_se=0.01, rws_med=0.0, share=np.array([0.6, np.nan]), vp=np.array([1.0, 0.0]), vr=np.array([0.5, 0.0]),
                share_n=1, share_nan=1, share_med=med, flips=fl, cd2=cd2, kish=1.09)


def st_branches():
    J = lambda st: "\n".join(verdict_lines(st))           # noqa: E731
    RSC.need(J(_syn()), "CD1: DIFFICULTY-STRATA", "P1 CD1 DIFFICULTY-STRATA 0.60: outcome DIFFICULTY-STRATA -> Brier 0.1600")
    RSC.need(J(_syn(e=0.1, p975=0.1)), "CD1: NOT-DIFFICULTY-STRATA: eta2_b above the RWS p97.5: NO", "Brier 0.3600")
    RSC.need(J(_syn(med=0.5)), "CD1: NOT-DIFFICULTY-STRATA: eta2_b above the RWS p97.5: yes", "median composition share above 0.5: NO (0.5000)")
    RSC.need(J(_syn(cd2=0)), "CD2 (descriptive): 0 of 7", "F-CD (its CD2 leg DESCRIPTIVE, B-CD2; no falsifier verdict): CD2 = 0",
             "a dimension claim): 0 -> FAILED; >= 4 of 7 MULTIDIM: 0 -> FAILED")
    RSC.need(J(_syn(cd2=1)), "F-CD (its CD2 leg DESCRIPTIVE, B-CD2; no falsifier verdict): CD2 = 1, not 0", "1 -> FAILED; >= 4 of 7 MULTIDIM: 1 -> FAILED")
    for t_ in (J(_syn(cd2=0)), J(_syn(cd2=3))):
        assert "F-CD: FIRED" not in t_ and "F-CD: NOT FIRED" not in t_ and "CD2: " not in t_, "CD2 / F-CD never printed as verdicts"
        RSC.need(t_, "CD1 SCOREABLE as a classification and decides alone; CD2 DESCRIPTIVE",
                 "per-task floors: 2 of 3 CELL-FLIPS cells MULTIDIM", "EVAL items per floor 0.0000: 10, 0.5000: 4; BBH / MUSR EVAL items of unlisted tasks 3")
    # the per-task floor table by value (the REAL table)
    assert task_floor("BBH", "hyperbaton") == 0.5 and abs(task_floor("BBH", "logical_deduction_seven_objects") - 1 / 7) < 1e-15
    assert task_floor("BBH", "movie_recommendation") == 0.2 and task_floor("BBH", "date_understanding") == 1 / 6
    assert task_floor("MUSR", "murder_mysteries") == 0.5 and task_floor("MUSR", "team_allocation") == 1 / 3
    assert task_floor("MUSR", "object_placements") == 0.0 and task_floor("BBH", "word_sorting") == 0.0
    assert task_floor("BBH", "no_such_task") == 0.0 and task_floor("GPQA", "x") == 0.25 and task_floor("MMLU_PRO", "law") == 0.10
    assert task_floor("MATH", "algebra") == 0.0 and len(TASK_OPTIONS["BBH"]) == 27
    RSC.need(J(_syn(cd2=2)), "2 -> HELD; >= 4 of 7 MULTIDIM: 2 -> FAILED")
    RSC.need(J(_syn(cd2=4)), "4 -> HELD; >= 4 of 7 MULTIDIM: 4 -> HELD")
    RSC.need(J(_syn(cd2=7)), "7 -> HELD; >= 4 of 7 MULTIDIM: 7 -> HELD")
    RSC.need(J(_syn(med=0.4)), "0.4000 -> HELD")
    RSC.need(J(_syn(med=0.8)), "0.8000 -> HELD")
    RSC.need(J(_syn(med=0.8001)), "0.8001 -> FAILED")
    RSC.need(J(_syn(med=float("nan"))), "NOT SCOREABLE (no model with a non-zero cell variance)")
    # BH, not Bonferroni, not uncorrected (the CD2 count)
    for ps, want in (((0.01, 0.02, 0.9), [True, True, False]), ((0.01, 0.03, 0.04, 0.9), [True, False, False, False]),
                     ((0.0, 0.0, 0.051), [True, True, False])):
        assert [r["multi"] for r in mark_bh([dict(p=p) for p in ps])] == want, ps
    # helpers by value
    assert abs(eta2(np.array([0.0, 2.0, 10.0, 12.0]), np.array([1.0, 11.0]), np.array([0, 0, 1, 1]), np.array([0, 1]), 2) - 1.0) < 1e-12
    v = eta2(np.array([0.0, 2.0]), np.array([1.0, 3.0]), np.array([0, 0]), np.array([0, 1]), 2)     # cell 1 has no TRAIN item -> grand mean 1
    assert abs(v - (1.0 - (0.0 + 4.0) / 2.0)) < 1e-12, v
    s, vp, vr = composition(np.array([[1.0], [0.0], [1.0], [1.0]]), np.array([[0.5], [0.5], [0.9], [0.9]]), np.array([0, 0, 1, 1]), 2)
    # cells: acc 0.5 / 1.0, pred 0.5 / 0.9 -> resid 0 / 0.1; weights 1/2: V_pred = 0.04, V_res = 0.0025
    assert abs(vp[0] - 0.04) < 1e-12 and abs(vr[0] - 0.0025) < 1e-12 and abs(s[0] - 0.04 / 0.0425) < 1e-12


def st_refusals(tmp):
    def expect(needle, pool=(0, "stub"), pre=None, existed=False, kmut=None, variant="planted"):
        sub = os.path.join(tmp, "r%d" % len(os.listdir(tmp)))
        os.makedirs(sub)
        root, X = RSC.build_fixture(sub, variant)
        if kmut:
            X["kconst"] = dict(X["kconst"], **kmut(X))
        od = os.path.join(root, "out")
        if pre:
            pre(root, od, X)
        buf = []
        with _swap(dict(FX_RP, n_rws=4, n_boot=20)), RSC.patched(X, pool):
            try:
                run(root, od, out=buf.append)
                raise AssertionError("not refused: %s" % needle)
            except SystemExit as e:
                assert needle in str(e), (needle, str(e)[:300])
        op = os.path.join(od, R()["outcome"])
        if existed:
            assert open(op, encoding="utf-8").read() == "kept"
        else:
            assert not os.path.exists(op), "no outcome after a refusal"
        return buf
    expect("the CELL-FLIPS outcome is sha256", kmut=lambda X: dict(flips_sha="0" * 64))
    expect("FLIP AF-U lines", kmut=lambda X: dict(flips=X["kconst"]["flips"][:-1]))
    expect("FLIP AF-U lines", kmut=lambda X: dict(flips=tuple(X["kconst"]["flips"][:1]) + tuple((c, ch, n, "+0.9999") for c, ch, n, _d in X["kconst"]["flips"][1:])))

    def bad_outcome(field):
        def f(root, od, X):
            fp = U.P(root, X["kconst"]["flips_rel"])
            fl = list(X["kconst"]["flips"])
            c, ch, n, d = fl[0]
            fl[0] = (c, ch, n, "+0.9999") if field == "D" else (c, [m for m in RSC.FX_MODELS if m not in (ch, X["pol"]["best_single"])][0], n, d)
            with open(fp, "w", encoding="utf-8", newline="\n") as fh:
                for c_, ch_, n_, d_ in fl:
                    fh.write("  FLIP %-8s %-30s n %4d  challenger %-30s D_c %s  p %.5f\n" % ("AF-U", c_, n_, ch_, d_, 0.0001))
            X["kconst"]["flips"] = tuple(fl)
            X["kconst"]["flips_sha"] = RSC.sha256_bytes(fp)
        return f
    expect("recomputed, not CELL-FLIPS'", pre=bad_outcome("D"))
    expect("is not the frozen pick", pre=bad_outcome("ch"))
    expect("[IDENTITY] C1", kmut=lambda X: dict(c1="+9.99pp"))
    buf = expect("B0-2 pool check failed", pool=(1, "stub failure"))
    assert buf[0].startswith(TAG + " POOL")

    def mk(name, txt):
        def f(root, od, X):
            os.makedirs(od, exist_ok=True)
            with open(os.path.join(od, name), "w", encoding="utf-8") as fh:
                fh.write(txt)
        return f
    expect("write-once output(s) exist", pre=mk(RP_["marker"], ""))
    expect("write-once output(s) exist", pre=mk(RP_["outcome"], "kept"), existed=True)

    def b3(root, od, X):
        pp_ = U.P(root, U.CONST["policy_rel"])
        pol = json.load(open(pp_, encoding="utf-8"))
        pol["true_source_domain"]["BBH/d0"] = [m for m in RSC.FX_MODELS if m != pol["true_source_domain"]["BBH/d0"]][0]
        with open(pp_, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(pol, sort_keys=True, indent=1) + "\n")
        X["const"]["policy_sha"] = RSC.sha256_bytes(pp_)
    expect("[B3] the point policy", pre=b3)
    wp = os.path.join(tmp, "existing.txt")
    with open(wp, "w", encoding="utf-8") as fh:
        fh.write("kept")
    try:
        write_outcome(wp, "new")
        raise AssertionError("write_outcome overwrote")
    except SystemExit as e:
        assert "write-once" in str(e)
    assert open(wp, encoding="utf-8").read() == "kept"


def st_dry(tmp):
    root, X = RSC.build_fixture(tmp)
    od = os.path.join(tmp, "out")

    def files():
        return sorted(os.path.join(a, f_) for a, _d, fs in os.walk(tmp) for f_ in fs)
    before = files()
    with _swap(FX_RP), RSC.patched(X):
        _r, text = RSC.capture(dry_run, root, od)
    assert files() == before and text.split("\n")[0].startswith(TAG + " POOL pv_fx")
    assert "TRAIN key:" not in text and "key cells single" not in text
    RSC.need(text, "CELL-FLIPS cells (outcome", "TRAIN SET (gen view", "EVAL SET (G14's", "DENOMINATOR AF-U  12 distinct cells", "DRY-RUN complete",
             "PIN tools/analysis/cell_difficulty.py blob:")
    assert "CD1:" not in text and "eta2_b(" not in text


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
        return RSC.run_mutants(os.path.abspath(__file__), "cell_difficulty", MUTANTS, TAG, a.only)
    if a.dry_run:
        dry_run(os.path.abspath(a.data_root), a.out_dir)
        return 0
    run(os.path.abspath(a.data_root), a.out_dir)
    return 0


MUTANTS = (
    ("C00 control (no-op edit)", "    mu = np.where(n > 0, s / np.maximum(n, 1), bT.mean())", "    mu = np.where(n > 0, s / np.maximum(n, 1), bT.mean())", ["e2e"], "self"),
    ("Y01 eta2 with EVAL cell means (wrong side)", '    st["eta"] = {nm: eta2(I["bT"], I["bE"], arms[nm][0][T], arms[nm][0][E], arms[nm][1]) for nm in ARMS}',
     '    st["eta"] = {nm: eta2(I["bE"], I["bE"], arms[nm][0][E], arms[nm][0][E], arms[nm][1]) for nm in ARMS}', ["e2e"], "self"),
    ("Y02 eta2 denominator centred on the TRAIN mean", "    return 1.0 - ((bE - mu[gE]) ** 2).sum() / ((bE - bE.mean()) ** 2).sum()",
     "    return 1.0 - ((bE - mu[gE]) ** 2).sum() / ((bE - bT.mean()) ** 2).sum()", ["e2e", "branches"], "self"),
    ("Y03 a cell without TRAIN items predicts 0 (not the grand mean)", "    mu = np.where(n > 0, s / np.maximum(n, 1), bT.mean())",
     "    mu = np.where(n > 0, s / np.maximum(n, 1), 0.0)", ["branches"], "self"),
    ("Y04 RWS p97.5 -> p95", '    st["p975"] = U.pct(sorted(st["rws"]), c["q"])', '    st["p975"] = U.pct(sorted(st["rws"]), 0.95)', ["e2e"], "self"),
    ("Y05 CD1 eta2 >= instead of >", '    a = bool(e > st["p975"])', '    a = bool(e >= st["p975"])', ["branches"], "self"),
    ("Y06 CD1 share >= instead of >", '    b = bool(st["share_med"] > c["bar"])', '    b = bool(st["share_med"] >= c["bar"])', ["branches"], "self"),
    ("Y07 CD1 'or' (one clause only)", "    ds = a and b", "    ds = a or b", ["branches"], "self"),
    ("Y08 composition cells unweighted", "n[keep] / n[keep].sum()", "np.ones(int(keep.sum())) / keep.sum()", ["e2e", "branches"], "self"),
    ("Y09 composition share = V_pred / Var(acc)", '    share = np.where(tot > 0, vp / np.where(tot > 0, tot, 1.0), np.nan)',
     '    share = vp / wvar(acc)', ["e2e", "branches"], "self"),
    ("Y10 median -> mean over models", '    st["share_med"] = float(np.median(ok)) if len(ok) else float("nan")',
     '    st["share_med"] = float(np.mean(ok)) if len(ok) else float("nan")', ["e2e"], "self"),
    ("Y11 flip p with D* > D_obs (strict)", "    k = int((Ds_ >= Dobs - 1e-9).sum())", "    k = int((Ds_ > Dobs + 1e-9).sum())", ["null_e2e"], "self"),
    ("Y12 p = (k + 1) / (B + 1)", "k=k, p=k / B,", "k=k, p=(k + 1) / (B + 1),", ["e2e", "null_e2e"], "self"),
    ("Y13 Bonferroni instead of BH", '    rej = RSC.CF.bh([r["p"] for r in rows], R()["bh_q"])', '    rej = [r["p"] <= R()["bh_q"] / len(rows) for r in rows]',
     ["branches"], "self"),
    ("Y14 uncorrected p < 0.05", '    rej = RSC.CF.bh([r["p"] for r in rows], R()["bh_q"])', '    rej = [r["p"] < 0.05 for r in rows]', ["branches"], "self"),
    ("Y15 sign: D* <= D_obs counted", "    k = int((Ds_ >= Dobs - 1e-9).sum())", "    k = int((Ds_ <= Dobs + 1e-9).sum())", ["e2e"], "self"),
    ("Y16 registered flip list not checked against the outcome", "    if got != want:", "    if False:", ["refusals"], "self"),
    ("Y17 CELL-FLIPS outcome sha not checked", '    if sh != k["flips_sha"]:', "    if False:", ["refusals"], "self"),
    ("Y18 flip cell D_c not re-derived", "        if len(idx) != n or d != Ds:", "        if len(idx) != n:", ["refusals"], "self"),
    ("Y19 flip cell challenger not checked", '        if pol["tree_cell"].get(cell) != ch or ch == g:', "        if ch == g:", ["refusals"], "self"),
    ("Y20 F-CD (CD2 = 0) descriptive line omitted", '        L.append("F-CD (its CD2 leg DESCRIPTIVE, B-CD2; no falsifier verdict): CD2 = 0: every',
     '        (lambda *_: None)("F-CD (its CD2 leg DESCRIPTIVE, B-CD2; no falsifier verdict): CD2 = 0: every',
     ["null_e2e"], "self"),
    ("Y21 P2 '>= 4' read as '> 4'", '"HELD" if st["cd2"] >= PRED["P2_min"] else "FAILED"', '"HELD" if st["cd2"] > PRED["P2_min"] else "FAILED"', ["branches"], "self"),
    ("Y22 P1 Brier against 1 - p", 'RSC.brier(PRED["P1"], ds)', 'RSC.brier(1 - PRED["P1"], ds)', ["branches"], "self"),
    ("Y23 the flip stream re-seeded per cell", "        r = one_cell(rng, I, np.flatnonzero(gE == names.index(cell))",
     '        r = one_cell(np.random.default_rng(R()["flip_seed"]), I, np.flatnonzero(gE == names.index(cell))', ["e2e", "null_e2e"], "self"),
    ("Y24 flip seed 20261004 -> 20261005", "n_boot=1000, flip_seed=20261004,", "n_boot=1000, flip_seed=20261005,", ["constants"], "self"),
    ("Y25 1,000 -> 500 replicates", "n_boot=1000, flip_seed=20261004,", "n_boot=500, flip_seed=20261004,", ["constants"], "self"),
    ("Y26 RWS seeds 20261004 + 0..199", '    for r in range(1, c["n_rws"] + 1):', '    for r in range(c["n_rws"]):', ["e2e"], "self"),
    ("Y27 CD1 read from the declared arm", '    e = st["eta"]["AF-U"]', '    e = st["eta"]["declared"]', ["e2e"], "self"),
    ("Y28 composition over the K0 cells", '    share, vp, vr = composition(I["YE"], I["PE"], arms["AF-U"][0][E], arms["AF-U"][1])',
     '    share, vp, vr = composition(I["YE"], I["PE"], arms["K0"][0][E], arms["K0"][1])', ["e2e"], "self"),
    ("Y29 flip expectation from the TRAIN-less P (observed y)", '    pc, pg = I["PE"][idx, ci], I["PE"][idx, gi]', '    pc, pg = I["YE"][idx, ci], I["YE"][idx, gi]',
     ["e2e", "null_e2e"], "self"),
    ("Y30 outcome opened 'w'", "def write_outcome(path, text):\n    return U.G.write_once(path, text)",
     "def write_outcome(path, text):\n    open(path, 'w', encoding='utf-8').write(text)\n    return path", ["refusals"], "self"),
    ("Y31 bands open at the ends", "    return bool(band[0] <= x <= band[1])", "    return bool(band[0] < x < band[1])", ["branches"], "common"),
    ("Y32 identity (point) check off", '    if any(got[x] != k[x] for x in ("c1", "gaf", "best", "tdom", "af")):', "    if False:", ["refusals"], "common"),
    ("Y33 B3 check off", '        refuse(tag, "[B3] the point policy', '        (lambda *a: None)(tag, "[B3] the point policy', ["refusals"], "common"),
    ("Y34 theta fitted on TRAIN + EVAL (wrong side)", '    ft = fit_train(YT, cT, lam=lam)', '    ft = fit_train(np.vstack([YT, YE]), np.concatenate([cT, cE]), lam=lam)',
     ["e2e"], "common"),
    ("Y35 EVAL items keep the TRAIN start (no EVAL fit)", '    aE, bE, itE, mxE = fit_items(YE, cE, ft["theta"], lam)',
     '    aE, bE, itE, mxE = _item_init(YE) + (0, 0.0)', ["e2e"], "common"),
    ("Y36 dry-run reads the EVAL key", '    E = U.eval_set(root, say, tag, roster=pol["roster"], key=False)',
     '    E = U.eval_set(root, say, tag, roster=pol["roster"], key=True, marker=os.path.join(root, "mk"))', ["dry_run"], "common"),
    # resp-structure-fix1 (B-CD2: CD2 / F-CD descriptive; claim 11: per-task floors sensitivity)
    ("Y38 CD2 printed as a verdict line again", '    L.append("CD2 (descriptive): %d of %d CELL-FLIPS cells', '    L.append("CD2: %d of %d CELL-FLIPS cells', ["branches", "e2e"], "self"),
    ("Y39 F-CD printed as a falsifier verdict", '        L.append("F-CD (its CD2 leg DESCRIPTIVE, B-CD2; no falsifier verdict): CD2 = 0: every',
     '        L.append("F-CD: FIRED (CD2 = 0) (its CD2 leg DESCRIPTIVE, B-CD2; no falsifier verdict): CD2 = 0: every', ["branches"], "self"),
    ("Y40 sensitivity uses the registered floors (table ignored)", "    k = _TASK[0].get(src, {}).get(dom)", "    k = None", ["branches", "e2e"], "self"),
    ("Y41 sensitivity on the registered flip stream", '    rng = np.random.default_rng(R()["flip_seed"] + 2)', '    rng = np.random.default_rng(R()["flip_seed"])', ["e2e", "null_e2e"], "self"),
    ("Y42 floor = options, not 1 / options", "        return 1.0 / k\n    return RSC.FLOOR.get(src, 0.0)", "        return min(1.0, float(k))\n    return RSC.FLOOR.get(src, 0.0)",
     ["branches"], "self"),
    ("Y43 sensitivity floors keyed on the source only (MUSR dropped)", '    k = _TASK[0].get(src, {}).get(dom)', '    k = _TASK[0].get(src, {}).get(dom) if src == "BBH" else None',
     ["branches"], "self"),
    ("Y44 sensitivity count = every flip cell", '    return dict(rows=rows, n=int(sum(1 for r in rows if r["multi"])),', '    return dict(rows=rows, n=len(rows),', ["e2e", "null_e2e"], "self"),
    ("Y45 sensitivity's TRAIN fit sees EVAL", "    ft = RSC.fit_train(YT, cT)\n    aE, bE, _i, _m = RSC.fit_items(YE, cE, ft[\"theta\"])\n    I2 =",
     "    ft = RSC.fit_train(np.vstack([YT, YE]), np.concatenate([cT, cE]))\n    aE, bE, _i, _m = RSC.fit_items(YE, cE, ft[\"theta\"])\n    I2 =", ["e2e"], "self"),
    ("Y37 numpy-bool identity test on CD1", "    ds = a and b\n    if ds:", "    ds = (e > st[\"p975\"]) & (st[\"share_med\"] > c[\"bar\"])\n    if ds is True:",
     ["e2e"], "self"),
)

if __name__ == "__main__":
    sys.exit(main())
