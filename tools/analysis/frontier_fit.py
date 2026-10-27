"""FRONTIER-FIT - the widener fitted on the frontier-internal edges alone (registered by reference, zero calls).

  python tools/analysis/frontier_fit.py

REGISTRATION (docs/design/FRAMEWORK.md at commit 8d77f7b, "## Tests to register before shipping", item 5; registered
by reference in docs/judge_v2_program.md and scheduled in docs/plan_2026-09-15.md, Block 1), quoted:
  "5. FRONTIER-FIT. Widener fit on the 75 frontier-internal edges. Criterion: nominal >= 3 and b1 identified.
   Prediction: UNDETERMINED; frontier band BANDED by rule confirmed. 0 calls."
The record it cites (FRAMEWORK.md Stage 6 "Tier portability"; RESOLVE_budget.md section 5; the review's adv_x12.py
[FR] line): "the shipped x12 fit included frontier edges, but 26 of its 44 wrong edges are frontier-internal (34.7%
wrong there vs 2.2% elsewhere) and an off-frontier fit applied cold to the 75 frontier-internal edges is ~33x
under-budgeted (12 called / 2 wrong / nominal 0.06); FRONTIER-FIT is expected UNDETERMINED (nominal < 3 on 75
edges), which confirms the rule" - the rule being "the frontier band gets no ORDERED edge inside it under any fit".

IMPLEMENTATION, fixed before the run:
  * OBJECT. The 891 x12 per-anchor edges (key gap >= 0.02) of systematic_budget.build(), read from KEY-TIE-DECLINE's
    cached table (scratchpad/bigpic/ktd_x12_edges.pkl; a cache miss rebuilds it with the committed builder). The
    frontier band is the record's named set on MMLU-Pro (FRAMEWORK.md, Stage 7 classes): arx_0314, iask_pro,
    gemini-3.1-pro_5-shots, gpt-4o-2024-08-06. "Frontier-internal" = both endpoints in that set. This must give
    exactly 75 edges with 26 wrong-direction, else the object is not the registered one and the run stops. The
    unfiltered slice (any key gap; 84 edges) is reported as a secondary because the review declared the key-gap
    filter undeployable.
  * FIT. systematic_budget.fit (Nelder-Mead on the committed nll) from several starts, best nll kept; cbud/craw
    from the same module; threshold 0.975 (the operating point). Five certificates on the 75, each with
    called / wrong(McNemar-established) / nominal = sum(1 - c) over the called set / ratio:
      raw (tau = 0); the shipped x12 fit (budget_transfer.B0/B1, which was fitted WITH these edges);
      the off-frontier fit (the 816 non-frontier edges of the 891) applied cold - must reproduce 12/2/0.06;
      the FRONTIER fit in sample; the FRONTIER fit leave-one-anchor-out inside the 75 (the out-of-fold reading).
    Each also composed with the key-tie decline (McNemar p >= 0.05 on the anchor's JUDGED questions declines).
  * "NOMINAL >= 3". At 0.975 an edge contributes at most 0.025, so on N edges nominal <= 0.025 N: 1.875 on 75, 2.1
    on 84. The criterion cannot be met on this object under any fit; it is scored, and the arithmetic is printed
    beside it. As a diagnostic (NOT the registered operating point) the same table is printed at 0.90 and 0.95.
    A second reading of "nominal" exists in the record (systematic_budget.txt: "out-of-fold nominal over ALL 891
    edges: 48.6 against 44 observed"): sum(1 - c) over EVERY edge of the slice, called or not, against the wrong
    count of the slice. That aggregate is printed for the frontier fit (in sample and LOAO) beside its Poisson
    read, because it is the reading under which a calibration status on the frontier could be read at all and
    is therefore the one hardest on the rule; the criterion is SCORED on the framework's own definition (the
    called set at 0.975, Stage 6 "Calibration statement per board"), and the docstring says which is which.
  * "b1 IDENTIFIED". The framework's definition (Stage 6): the established-label profile rejects b1 = 0 at
    delta-deviance 3.84. Computed as 2 * (min nll with b1 = 0, b0 free) - 2 * (min nll with both free) on the
    McNemar-established frontier edges; also on all 75; plus the profile-likelihood 95% set for b1 (b0 profiled)
    and an anchor-clustered bootstrap CI (1,000 resamples of the anchors, vectorised twin of the committed nll,
    checked equal to systematic_budget.nll at the point estimate). Identification is scored on the
    established-label delta-deviance; the other three are printed.
  * KEY DENOMINATOR. Every wrong count carries its established count from systematic_budget.established /
    mcnemar_edge over anchor_qs[anchor] = the anchor's JUDGED x12 questions (119-304 per anchor), never the routed
    pool. The pooled-board readout uses all judged x12 questions as one pseudo-anchor, as KEY-TIE-DECLINE did.
  * "BANDED BY RULE". The hardest reading against the rule is the tier object itself: the pooled 66-pair x12
    board (systematic_budget.pooled_board, 300 draws, seed 43, as in systematic_budget.main) restricted to the six
    frontier pairs, under raw, shipped-widener and frontier-fit certificates, each composed with the decline. A
    frontier pair that stays separated at 0.975 under a fit with a readable calibration status would contradict
    the rule; the status column says whether any fit here is readable. Cached under scratchpad/block1.
  * Meta-Llama-3-70B-Instruct is absent from the x12 roster (asserted). No network, no LLM calls.
  * Calibration status by the power rule (FRAMEWORK.md Stage 6): nominal < 3 UNDETERMINED; 3-9 UNDETERMINED
    (power: a 2x miscalibration is undetectable); >= 9 read against Poisson P(>= observed).
"""
import os, sys, math, random, pickle, time
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import norm, poisson
import pool_guard
import systematic_budget as sb
import budget_transfer as bt
import key_tie_decline as ktd
import rubric_512 as r512
import stack_judge as sj

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "frontier_fit.txt")
CACHE = os.path.join(r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena",
                     "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad", "block1")
FRONTIER = ("arx_0314", "iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06")
THRESH = 0.975
DIAG_THRESH = (0.90, 0.95, 0.975)
ALPHA = 0.05
DDEV = 3.84
EXCLUDE = "Meta-Llama-3-70B-Instruct"
STARTS = ((-3.0, 3.0), (0.0, 0.0), (2.0, -2.0), (-1.0, 5.0), (5.0, 0.0), (bt.B0, bt.B1))
R_BOOT = 1000
SHORT = {"arx_0314": "arx", "iask_pro": "iask", "gemini-3.1-pro_5-shots": "gemini", "gpt-4o-2024-08-06": "gpt-4o"}


def log(msg):
    print("[frontier-fit %s] %s" % (time.strftime("%H:%M:%S"), msg), file=sys.stderr, flush=True)


def cached(name, fn):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if os.path.exists(p):
        log("cache hit %s" % name); return pickle.load(open(p, "rb"))
    log("building %s" % name)
    v = fn(); pickle.dump(v, open(p, "wb")); return v


# ---------- fitting helpers: committed fit from several starts; vectorised twin for the loops ----------
def best_fit(es, extra=()):
    best = None
    for x0 in tuple(STARTS) + tuple(extra):
        b0, b1 = sb.fit(es, x0=x0)
        v = sb.nll((b0, b1), es)
        if best is None or v < best[0]:
            best = (v, b0, b1)
    return best[1], best[2], best[0]


def arrays(es):
    return (np.array([abs(e["m"]) for e in es]), np.array([e["s"] for e in es]),
            np.array([e["agree"] for e in es]), np.array([0.0 if e["right"] else 1.0 for e in es]))


def vnll(par, M, S, A, Y):
    b0, b1 = par
    tau = np.exp(np.minimum(20.0, b0 + b1 * A))
    pw = np.clip(norm.cdf(-M / np.sqrt(S ** 2 + tau ** 2)), 1e-12, 1 - 1e-12)
    return float(-np.sum(Y * np.log(pw) + (1 - Y) * np.log(1 - pw)))


def vfit(M, S, A, Y, starts):
    best = None
    for x0 in starts:
        r = minimize(vnll, np.array(x0, float), args=(M, S, A, Y), method="Nelder-Mead",
                     options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
        if best is None or r.fun < best[0]:
            best = (float(r.fun), float(r.x[0]), float(r.x[1]))
    return best


def fit_b1_zero(M, S, A, Y):
    r = minimize_scalar(lambda b0: vnll((b0, 0.0), M, S, A, Y), bounds=(-40.0, 40.0), method="bounded",
                        options=dict(xatol=1e-7))
    return float(r.fun), float(r.x)


def profile_set(M, S, A, Y, nll_min, grid):
    """b1 values whose profile deviance (b0 profiled out) is within DDEV of the minimum."""
    inside = []
    for b1 in grid:
        r = minimize_scalar(lambda b0: vnll((b0, b1), M, S, A, Y), bounds=(-40.0, 40.0), method="bounded",
                            options=dict(xatol=1e-6))
        if 2 * (r.fun - nll_min) <= DDEV:
            inside.append(b1)
    return inside


def ps_txt(ps, grid):
    if not ps:
        return "empty on the grid"
    lo, hi = min(ps), max(ps)
    return "[%s, %s]%s%s" % ("%.1f" % lo if lo > grid[0] else "<= %.0f (grid edge)" % grid[0],
                             "%.1f" % hi if hi < grid[-1] else ">= %.0f (grid edge)" % grid[-1],
                             " contains 0" if lo <= 0 <= hi else " EXCLUDES 0",
                             " (unbounded on the grid)" if lo <= grid[0] or hi >= grid[-1] else "")


def status_word(nominal, wrong):
    if nominal < 3:
        return "UNDETERMINED (nominal < 3)"
    if nominal < 9:
        return "UNDETERMINED (power: nominal 3-9, a 2x miscalibration is undetectable)"
    p = 1 - poisson.cdf(wrong - 1, nominal) if wrong > 0 else 1.0
    return ("DETECTABLY MISCALIBRATED (Poisson P(>=%d | %.2f) = %.3f)" % (wrong, nominal, p) if p < 0.05
            else "NOT DETECTABLY MISCALIBRATED (Poisson P(>=%d | %.2f) = %.3f)" % (wrong, nominal, p))


def block(es, cfun, K, aq, thresh=THRESH):
    """called / wrong(est) / nominal / decline residue for one certificate on one edge set."""
    called = [e for e in es if cfun(e) >= thresh]
    wrong = [e for e in called if not e["right"]]
    est_wrong = sb.established(wrong, K, aq)
    nominal = sum(1 - cfun(e) for e in called)
    res = [e for e in called if sb.mcnemar_edge(e, K, aq)[0] < ALPHA]
    res_wrong = [e for e in res if not e["right"]]
    return dict(called=len(called), wrong=len(wrong), wrong_est=len(est_wrong), nominal=nominal,
                residue=len(res), residue_wrong=len(res_wrong), residue_wrong_est=len(sb.established(res_wrong, K, aq)))


def fmt_row(name, st, n, thresh=None):
    return ("  %-30s %6s %6d/%-3d %5d(%d) %8.3f %7s %13d %10d(%d)   %s"
            % (name, ("%.3f" % thresh) if thresh is not None else "", st["called"], n, st["wrong"], st["wrong_est"], st["nominal"],
               ("%.1fx" % (st["wrong"] / st["nominal"])) if st["nominal"] > 0 else "-",
               st["residue"], st["residue_wrong"], st["residue_wrong_est"], status_word(st["nominal"], st["wrong"])))


HDR = "  %-30s %6s %10s %8s %8s %7s %13s %13s   %s" % ("certificate", "thr", "called/N", "wrong", "nominal", "ratio", "decl.residue", "res.wrong", "status by the power rule")


def loao_scores(es, fit_fn):
    """out-of-fold c for every edge: fit on the other anchors' edges of the same set."""
    oof = {}
    for A_ in sorted({e["anchor"] for e in es}):
        tr = [e for e in es if e["anchor"] != A_]
        b0, b1, _ = fit_fn(tr)
        for e in es:
            if e["anchor"] == A_:
                oof[id(e)] = sb.cbud(e, b0, b1)
    return oof


def build_pooled(models, K, P):
    """The x12 pooled 66-pair board exactly as systematic_budget.main builds it (300 draws, seed 43)."""
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(list)
    for a, b, q, w, _ in rows:
        if q in route:
            by[anchor_of(route[q])].append((a, b, q, w))
    pooled = sb.pooled_board(by, K, P, models, random.Random(43))
    qs = sorted({q for anc in by for _, _, q, _ in by[anc]})
    return pooled, qs


def x12_from_builder():
    t = sb.build()
    return t[0], dict(t[1]), dict(t[2]), t[4], t[5]


def main():
    L = []
    t0 = time.time()
    L.append("=== FRONTIER-FIT: the widener fitted on the frontier-internal edges alone (FRAMEWORK.md item 5, zero calls) ===")
    L.append("  pool of record %s asserted | frontier band = %s" % (pool_guard.FROZEN_POOL_ID, ", ".join(FRONTIER)))
    L.append("  widener tau(A) = exp(b0 + b1*A) in quadrature with the bootstrap SD; call iff min(c_raw, Phi(|m|/sqrt(s^2+tau^2))) >= %.3f" % THRESH)
    L.append("  wrong counts are all(McNemar-established); key denominator = the anchor's JUDGED x12 questions (systematic_budget.mcnemar_edge over anchor_qs)")

    # ---------------- object ----------------
    models, K, P, e_all, aq = ktd.cached("ktd_x12_edges.pkl", x12_from_builder)
    assert EXCLUDE not in models
    e891 = [e for e in e_all if e["gap"] >= sb.GAP]
    fr = [e for e in e891 if e["a"] in FRONTIER and e["b"] in FRONTIER]
    fr_u = [e for e in e_all if e["a"] in FRONTIER and e["b"] in FRONTIER]
    off = [e for e in e891 if not (e["a"] in FRONTIER and e["b"] in FRONTIER)]
    n_wrong = sum(1 for e in fr if not e["right"])
    L.append("")
    L.append("=== DATA CHECK ===")
    L.append("  x12: %d models | %d edges with any key gap (%d wrong) | %d with gap >= %.2f (%d wrong) | %d anchors, judged questions per anchor %d-%d"
             % (len(models), len(e_all), sum(1 for e in e_all if not e["right"]), len(e891),
                sb.GAP, sum(1 for e in e891 if not e["right"]), len(aq), min(map(len, aq.values())), max(map(len, aq.values()))))
    L.append("  frontier-internal edges among the 891: %d, wrong-direction %d(%d) -> registered object (75, 26): %s"
             % (len(fr), n_wrong, len(sb.established([e for e in fr if not e["right"]], K, aq)),
                "REPRODUCED" if (len(fr), n_wrong) == (75, 26) else "MISMATCH"))
    if (len(fr), n_wrong) != (75, 26):
        raise SystemExit("[FRONTIER-FIT] the frontier slice is not the registered object; stopping")
    est_fr = sb.established(fr, K, aq)
    L.append("  of the 75: key direction established (McNemar p < %.2f) %d, unestablished %d; wrong among established %d, among unestablished %d"
             % (ALPHA, len(est_fr), len(fr) - len(est_fr), sum(1 for e in est_fr if not e["right"]),
                n_wrong - sum(1 for e in est_fr if not e["right"])))
    L.append("  frontier-internal edges among the unfiltered 920 (secondary): %d, wrong %d(%d)"
             % (len(fr_u), sum(1 for e in fr_u if not e["right"]), len(sb.established([e for e in fr_u if not e["right"]], K, aq))))
    L.append("  off-frontier edges (the complement inside the 891): %d, wrong %d(%d) = %.1f%% vs %.1f%% on the frontier slice"
             % (len(off), sum(1 for e in off if not e["right"]), len(sb.established([e for e in off if not e["right"]], K, aq)),
                100.0 * sum(1 for e in off if not e["right"]) / len(off), 100.0 * n_wrong / len(fr)))
    anc_fr = sorted({e["anchor"] for e in fr})
    L.append("  anchors carrying frontier edges: %d (%s)" % (len(anc_fr), ", ".join("%s %d" % (a, sum(1 for e in fr if e["anchor"] == a)) for a in anc_fr)))
    L.append("  ARITHMETIC: at %.3f each called edge contributes at most %.3f to the nominal, so nominal <= %.3f on %d edges and <= %.3f on %d;"
             % (THRESH, 1 - THRESH, (1 - THRESH) * len(fr), len(fr), (1 - THRESH) * len(fr_u), len(fr_u)))
    L.append("  'nominal >= 3' needs >= %d called edges at %.3f. The criterion is unreachable on this object under ANY fit." % (math.ceil(3 / (1 - THRESH)), THRESH))

    # ---------------- the fits ----------------
    L.append("")
    L.append("=== FITS ===")
    sh0, sh1 = bt.B0, bt.B1
    L.append("  shipped x12 fit (budget_transfer.B0/B1, fitted on all 891 INCLUDING these 75): b0 = %+.4f | b1 = %+.4f" % (sh0, sh1))
    of0, of1, _ = best_fit(off, extra=((sh0, sh1),))
    L.append("  off-frontier fit (the %d non-frontier edges of the 891): b0 = %+.4f | b1 = %+.4f  (record: b1 1.455)" % (len(off), of0, of1))
    fr0, fr1, fr_nll = best_fit(fr, extra=((sh0, sh1), (of0, of1)))
    L.append("  FRONTIER fit (the 75 frontier-internal edges):          b0 = %+.4f | b1 = %+.4f | nll %.4f" % (fr0, fr1, fr_nll))
    A_fr = sorted(e["agree"] for e in fr); S_fr = sorted(e["s"] for e in fr)
    L.append("    agreement on the 75: min %.3f / median %.3f / max %.3f; tau at A = 0.60 / 0.70 / 0.80 / 0.90: %s"
             % (A_fr[0], A_fr[len(A_fr) // 2], A_fr[-1],
                " / ".join("%.3f" % math.exp(min(20.0, fr0 + fr1 * a)) for a in (0.60, 0.70, 0.80, 0.90))))
    lp_lo, lp_hi = fr0 + fr1 * A_fr[0], fr0 + fr1 * A_fr[-1]
    L.append("    bootstrap s on the 75: median %.3f (p10 %.3f, p90 %.3f); linear predictor b0 + b1*A over the data range: [%.2f, %.2f]%s"
             % (S_fr[len(S_fr) // 2], S_fr[len(S_fr) // 10], S_fr[9 * len(S_fr) // 10], min(lp_lo, lp_hi), max(lp_lo, lp_hi),
                "  <- reaches the nll clip (20): tau saturates, P(wrong) -> 0.5" if max(lp_lo, lp_hi) >= 20 else ""))
    M, S, A, Y = arrays(fr)
    tw = vnll((fr0, fr1), M, S, A, Y)
    L.append("    vectorised twin of systematic_budget.nll at the point estimate: %.6f vs %.6f (|diff| %.1e)" % (tw, fr_nll, abs(tw - fr_nll)))
    assert abs(tw - fr_nll) < 1e-6

    # ---------------- certificates on the 75 at the operating point ----------------
    oof_fr = loao_scores(fr, lambda tr: best_fit(tr, extra=((fr0, fr1),)))
    certs = [("raw (tau = 0)", lambda e: sb.craw(e)),
             ("shipped x12 fit (in sample)", lambda e: sb.cbud(e, sh0, sh1)),
             ("off-frontier fit, cold", lambda e: sb.cbud(e, of0, of1)),
             ("FRONTIER fit, in sample", lambda e: sb.cbud(e, fr0, fr1)),
             ("FRONTIER fit, LOAO within 75", lambda e: oof_fr[id(e)])]
    L.append("")
    L.append("=== (A) THE 75 FRONTIER-INTERNAL EDGES AT %.3f (the registered operating point) ===" % THRESH)
    L.append("  'nominal' = sum(1 - c) over the called set; ratio = wrong / nominal; decl.residue = calls surviving the key-tie decline (McNemar p >= %.2f declines)" % ALPHA)
    L.append(HDR)
    stA = {}
    for name, cf in certs:
        st = block(fr, cf, K, aq); stA[name] = st
        L.append(fmt_row(name, st, len(fr), THRESH))
    rep = stA["off-frontier fit, cold"]
    L.append("  reproduction of the record's cold off-frontier row (12 called / 2 wrong / nominal 0.06): %d / %d / %.3f -> %s"
             % (rep["called"], rep["wrong"], rep["nominal"], "OK" if (rep["called"], rep["wrong"]) == (12, 2) and abs(rep["nominal"] - 0.063) < 0.01 else "MISMATCH"))
    rr = stA["raw (tau = 0)"]
    L.append("  reproduction of the record's raw frontier row (31 called / 5 wrong): %d / %d -> %s" % (rr["called"], rr["wrong"], "OK" if (rr["called"], rr["wrong"]) == (31, 5) else "MISMATCH"))
    L.append("  utility on the 75: %s" % "; ".join("%s %.1f%%" % (n, 100.0 * stA[n]["called"] / len(fr)) for n, _ in certs))

    # ---------------- diagnostic thresholds ----------------
    L.append("")
    L.append("=== (B) DIAGNOSTIC, NOT THE OPERATING POINT: the same certificates at 0.90 / 0.95 / 0.975 on the 75 ===")
    L.append("  (at 0.90 the nominal ceiling is %.1f, so a calibration read becomes arithmetically possible there)" % (0.10 * len(fr)))
    L.append(HDR)
    for name, cf in certs:
        for t in DIAG_THRESH:
            L.append(fmt_row(name, block(fr, cf, K, aq, thresh=t), len(fr), t))

    # ---------------- identification ----------------
    L.append("")
    L.append("=== (C) IS b1 IDENTIFIED ON THE FRONTIER SLICE? ===")
    L.append("  framework definition (Stage 6): the ESTABLISHED-label profile rejects b1 = 0 at delta-deviance %.2f" % DDEV)
    Me, Se, Ae, Ye = arrays(est_fr)
    e_free = vfit(Me, Se, Ae, Ye, STARTS + ((fr0, fr1),))
    e_zero = fit_b1_zero(Me, Se, Ae, Ye)
    dd_est = 2 * (e_zero[0] - e_free[0])
    a_zero = fit_b1_zero(M, S, A, Y)
    dd_all = 2 * (a_zero[0] - fr_nll)
    L.append("  established labels (%d edges, %d wrong): free fit b0 %+.4f b1 %+.4f nll %.4f | b1 = 0 fit b0 %+.4f nll %.4f | delta-deviance %.3f -> %s"
             % (len(est_fr), int(Ye.sum()), e_free[1], e_free[2], e_free[0], e_zero[1], e_zero[0], dd_est,
                "b1 IDENTIFIED (rejects b1 = 0)" if dd_est >= DDEV else "b1 NOT identified (b1 = 0 not rejected)"))
    L.append("  all labels         (%d edges, %d wrong): free fit b0 %+.4f b1 %+.4f nll %.4f | b1 = 0 fit b0 %+.4f nll %.4f | delta-deviance %.3f -> %s"
             % (len(fr), int(Y.sum()), fr0, fr1, fr_nll, a_zero[1], a_zero[0], dd_all,
                "rejects b1 = 0" if dd_all >= DDEV else "does not reject b1 = 0"))
    grid = np.round(np.arange(-20.0, 30.0001, 0.1), 3)
    ps_all = profile_set(M, S, A, Y, fr_nll, grid)
    ps_est = profile_set(Me, Se, Ae, Ye, e_free[0], grid)
    L.append("  profile-likelihood 95%% set for b1 (b0 profiled, grid [-20, 30] step 0.1): all labels %s | established %s" % (ps_txt(ps_all, grid), ps_txt(ps_est, grid)))
    L.append("  x12 reference: b1 = +3.3133 on 891, anchor-clustered CI [1.72, 7.87]; established refit +2.1430; BUDGET-TRANSFER's INTERNAL set [-4.0, 2.75]")

    def boot():
        rng = np.random.default_rng(42)
        byA = {a: [e for e in fr if e["anchor"] == a] for a in anc_fr}
        b1s = []; b0s = []
        for _ in range(R_BOOT):
            pick = rng.choice(len(anc_fr), len(anc_fr), replace=True)
            sub = [e for i in pick for e in byA[anc_fr[i]]]
            if sum(1 for e in sub if not e["right"]) in (0, len(sub)):
                continue
            Mb, Sb, Ab, Yb = arrays(sub)
            v = vfit(Mb, Sb, Ab, Yb, ((fr0, fr1), (-3.0, 3.0), (0.0, 0.0)))
            b0s.append(v[1]); b1s.append(v[2])
        return np.array(b0s), np.array(b1s)
    b0s, b1s = cached("frontier_fit_anchor_boot_r%d.pkl" % R_BOOT, boot)
    L.append("  anchor-clustered bootstrap of the frontier fit (%d resamples of the %d anchors, %d usable): b1 median %+.3f, 95%% [%+.3f, %+.3f], P(b1 <= 0) = %.3f; b0 95%% [%+.3f, %+.3f]; corr(b0, b1) %.3f"
             % (R_BOOT, len(anc_fr), len(b1s), np.median(b1s), np.percentile(b1s, 2.5), np.percentile(b1s, 97.5), float((b1s <= 0).mean()),
                np.percentile(b0s, 2.5), np.percentile(b0s, 97.5), float(np.corrcoef(b0s, b1s)[0, 1]) if len(b1s) > 2 else float("nan")))
    loao_b1 = []
    for A_ in anc_fr:
        tr = [e for e in fr if e["anchor"] != A_]
        _, b1_, _ = best_fit(tr, extra=((fr0, fr1),)); loao_b1.append(b1_)
    L.append("  LOAO fold b1 range inside the 75: [%+.3f, %+.3f]" % (min(loao_b1), max(loao_b1)))
    identified = dd_est >= DDEV

    # ---------------- the edges ----------------
    L.append("")
    L.append("=== (D) THE 75 EDGES: certificate under each fit, key label, McNemar on the anchor's judged questions ===")
    L.append("  %-16s %-18s %6s %7s %7s %7s %7s %7s %6s %6s %s" % ("anchor", "pair", "A", "c_raw", "shipped", "offfr", "front", "LOAO", "|m|/s", "key", "McNemar b:c p"))
    for e in sorted(fr, key=lambda e: (e["anchor"], e["a"], e["b"])):
        p_, b_, c_ = sb.mcnemar_edge(e, K, aq)
        L.append("  %-16s %-18s %6.3f %7.4f %7.4f %7.4f %7.4f %7.4f %6.2f %6s %3d:%-3d p=%.4f%s"
                 % (e["anchor"][:16], "%s vs %s" % (SHORT[e["a"]], SHORT[e["b"]]), e["agree"], sb.craw(e), sb.cbud(e, sh0, sh1),
                    sb.cbud(e, of0, of1), sb.cbud(e, fr0, fr1), oof_fr[id(e)], abs(e["m"]) / e["s"],
                    "right" if e["right"] else "WRONG", b_, c_, p_, "" if p_ < ALPHA else " (unest.)"))

    # ---------------- secondary: unfiltered 84 ----------------
    L.append("")
    L.append("=== (E) SECONDARY: the unfiltered frontier slice (any key gap, %d edges) ===" % len(fr_u))
    u0, u1, u_nll = best_fit(fr_u, extra=((fr0, fr1),))
    est_u = sb.established(fr_u, K, aq)
    Mu, Su, Au, Yu = arrays(fr_u); Mue, Sue, Aue, Yue = arrays(est_u)
    ue_free = vfit(Mue, Sue, Aue, Yue, STARTS + ((u0, u1),)); ue_zero = fit_b1_zero(Mue, Sue, Aue, Yue)
    dd_u_est = 2 * (ue_zero[0] - ue_free[0])
    L.append("  fit: b0 %+.4f b1 %+.4f | established %d (wrong %d): delta-deviance %.3f -> %s | all-label delta-deviance %.3f"
             % (u0, u1, len(est_u), int(Yue.sum()), dd_u_est, "identified" if dd_u_est >= DDEV else "NOT identified",
                2 * (fit_b1_zero(Mu, Su, Au, Yu)[0] - u_nll)))
    oof_u = loao_scores(fr_u, lambda tr: best_fit(tr, extra=((u0, u1),)))
    L.append(HDR)
    for name, cf in (("raw (tau = 0)", lambda e: sb.craw(e)), ("shipped x12 fit", lambda e: sb.cbud(e, sh0, sh1)),
                     ("off-frontier fit, cold", lambda e: sb.cbud(e, of0, of1)), ("frontier-84 fit, in sample", lambda e: sb.cbud(e, u0, u1)),
                     ("frontier-84 fit, LOAO", lambda e: oof_u[id(e)])):
        L.append(fmt_row(name, block(fr_u, cf, K, aq), len(fr_u), THRESH))

    # ---------------- the tier object: pooled x12 board, frontier pairs ----------------
    L.append("")
    L.append("=== (F) THE TIER OBJECT: the six frontier pairs on the pooled x12 board (66 pairs, 300 question draws, seed 43) ===")
    pooled, qs_pool = cached("frontier_fit_pooled_x12.pkl", lambda: build_pooled(models, K, P))
    for e in pooled:                       # sb.pooled_board carries no anchor key; one pseudo-anchor, as KEY-TIE-DECLINE
        e["anchor"] = "POOLED"
    aq_pool = {"POOLED": qs_pool}
    L.append("  key denominator here: all %d judged x12 questions as one pseudo-anchor (as KEY-TIE-DECLINE did)" % len(qs_pool))
    p_raw = [e for e in pooled if sb.craw(e) >= THRESH]; p_sh = [e for e in pooled if sb.cbud(e, sh0, sh1) >= THRESH]
    tup = (len(p_raw), sum(1 for e in p_raw if not e["right"]), len(p_sh), sum(1 for e in p_sh if not e["right"]))
    L.append("  reproduction of systematic_budget.txt (raw 63 called / 1 wrong -> budget 57 / 0): raw %d / %d -> shipped %d / %d -> %s"
             % (tup + ("OK" if tup == (63, 1, 57, 0) else "DIFFERS (bootstrap draw order; read the frontier rows, not the totals)",)))
    pf = [e for e in pooled if e["a"] in FRONTIER and e["b"] in FRONTIER]
    L.append("  %-18s %7s %7s %7s %7s %7s %6s %-18s %s" % ("pair", "A", "s", "c_raw", "shipped", "front", "key", "McNemar b:c p", "separated at 0.975 under raw / shipped / frontier (after decline)"))
    sep_counts = {nm: [0, 0, 0] for nm in ("raw", "shipped", "frontier")}
    for e in sorted(pf, key=lambda e: -sb.craw(e)):
        p_, b_, c_ = sb.mcnemar_edge(e, K, aq_pool)
        cs = dict(raw=sb.craw(e), shipped=sb.cbud(e, sh0, sh1), frontier=sb.cbud(e, fr0, fr1))
        flags = []
        for nm in ("raw", "shipped", "frontier"):
            on = cs[nm] >= THRESH and p_ < ALPHA
            flags.append("yes" if on else ("declined" if cs[nm] >= THRESH else "no"))
            if cs[nm] >= THRESH:
                sep_counts[nm][0] += 1
                if not e["right"]: sep_counts[nm][1] += 1
                if on: sep_counts[nm][2] += 1
        L.append("  %-18s %7.3f %7.3f %7.4f %7.4f %7.4f %6s %3d:%-3d p=%.4f   %s"
                 % ("%s vs %s" % (SHORT[e["a"]], SHORT[e["b"]]), e["agree"], e["s"], cs["raw"], cs["shipped"], cs["frontier"],
                    "right" if e["right"] else "WRONG", b_, c_, p_, " / ".join(flags)))
    for nm in ("raw", "shipped", "frontier"):
        c_, w_, r_ = sep_counts[nm]
        L.append("  %-9s frontier pairs separated at %.3f: %d (wrong %d) -> after decline %d" % (nm, THRESH, c_, w_, r_))
    L.append("  the frontier fit is applied here across objects (fitted where s ~ %.2f, applied where s ~ %.2f): an extrapolation, printed for the readout only"
             % (S_fr[len(S_fr) // 2], sorted(e["s"] for e in pf)[len(pf) // 2]))

    # ---------------- criteria ----------------
    ins = stA["FRONTIER fit, in sample"]; lo = stA["FRONTIER fit, LOAO within 75"]; shp = stA["shipped x12 fit (in sample)"]
    nom_max = max(st["nominal"] for st in stA.values())
    L.append("")
    L.append("=== REGISTERED CRITERIA AND PREDICTION ===")
    L.append("  (1) nominal >= 3 on the frontier fit at %.3f: in sample %.3f (%d called, %d(%d) wrong) | LOAO within the 75: %.3f (%d called, %d(%d) wrong)"
             % (THRESH, ins["nominal"], ins["called"], ins["wrong"], ins["wrong_est"], lo["nominal"], lo["called"], lo["wrong"], lo["wrong_est"]))
    L.append("      largest nominal of any certificate on the 75: %.3f; arithmetic ceiling %.3f -> FAIL, and unreachable by construction (needs >= %d called edges)"
             % (nom_max, (1 - THRESH) * len(fr), math.ceil(3 / (1 - THRESH))))
    L.append("      calibration status of the frontier fit: %s" % status_word(lo["nominal"], lo["wrong"]))
    agg_in = sum(1 - sb.cbud(e, fr0, fr1) for e in fr); agg_lo = sum(1 - oof_fr[id(e)] for e in fr)
    agg_sh = sum(1 - sb.cbud(e, sh0, sh1) for e in fr); agg_of = sum(1 - sb.cbud(e, of0, of1) for e in fr)
    agg_raw = sum(1 - float(norm.cdf(abs(e["m"]) / e["s"])) for e in fr)
    L.append("      ALTERNATE READING (aggregate, sum(1 - c) over ALL %d edges vs %d(%d) observed wrong; NOT the scored definition):" % (len(fr), n_wrong, sum(1 for e in est_fr if not e["right"])))
    for nm, ag in (("raw Gaussian (tau = 0)", agg_raw), ("shipped x12 fit", agg_sh), ("off-frontier fit, cold", agg_of),
                   ("FRONTIER fit, in sample", agg_in), ("FRONTIER fit, LOAO within 75", agg_lo)):
        pp = 1 - poisson.cdf(n_wrong - 1, ag) if ag > 0 else float("nan")
        L.append("        %-30s aggregate nominal %7.2f | ratio %5.2fx | Poisson P(>= %d | %.2f) = %.3f -> %s"
                 % (nm, ag, n_wrong / ag if ag > 0 else float("inf"), n_wrong, ag, pp,
                    "aggregate CONSERVATIVE" if ag >= n_wrong else ("aggregate OPTIMISTIC, detectably (P < 0.05)" if pp < 0.05 else "aggregate OPTIMISTIC, not detectably")))
    L.append("        even under this reading the aggregate says nothing about the operating point: the called set at %.3f carries nominal <= %.3f." % (THRESH, (1 - THRESH) * len(fr)))
    L.append("  (2) b1 identified (established-label delta-deviance >= %.2f): %.3f on %d established edges -> %s; all-label %.3f; profile set %s; bootstrap 95%% [%+.2f, %+.2f]"
             % (DDEV, dd_est, len(est_fr), "PASS" if identified else "FAIL", dd_all, ps_txt(ps_est, grid), np.percentile(b1s, 2.5), np.percentile(b1s, 97.5)))
    L.append("  criterion as a whole ('nominal >= 3 AND b1 identified'): FAIL")
    L.append("  PREDICTION 'UNDETERMINED': holds - and by arithmetic, not by measurement: on 75 edges at 0.975 no fit can reach the nominal a status word needs.")
    L.append("  PREDICTION 'frontier band BANDED by rule confirmed': the rule ('no ORDERED edge inside the frontier band under any fit') stands unchallenged:")
    L.append("      no certificate on the frontier slice has a readable calibration status (max nominal %.3f < 3), so no frontier edge can be ORDERED-JUDGED;" % nom_max)
    L.append("      what the fits DO on the frontier at %.3f: raw %d called / %d(%d) wrong; shipped %d / %d(%d); frontier in-sample %d / %d(%d); frontier LOAO %d / %d(%d);"
             % (THRESH, rr["called"], rr["wrong"], rr["wrong_est"], shp["called"], shp["wrong"], shp["wrong_est"],
                ins["called"], ins["wrong"], ins["wrong_est"], lo["called"], lo["wrong"], lo["wrong_est"]))
    L.append("      on the pooled tier object the frontier pairs separated after widener + decline are: raw %d, shipped %d, frontier fit %d."
             % (sep_counts["raw"][2], sep_counts["shipped"][2], sep_counts["frontier"][2]))
    L.append("      Read: CONFIRMED in the item's sense (the test could not have overturned the rule at this support); this is confirmation by")
    L.append("      unreachability, not a measurement that could have gone the other way. The measured content is the identification read in (C)")
    L.append("      and the raw certificate's %d(%d) wrong of %d called on the frontier (%.1f%%)." % (rr["wrong"], rr["wrong_est"], rr["called"], 100.0 * rr["wrong"] / max(1, rr["called"])))
    L.append("  elapsed %.0f s" % (time.time() - t0))

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
