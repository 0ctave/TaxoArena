"""UNFILTERED-ADOPT — item 3 of docs/design/FRAMEWORK.md "Tests to register before shipping" (commit 8d77f7b),
registered BY REFERENCE at commit eaf1dbf (docs/judge_v2_program.md, "Registered 2026-09-15 (before any run)";
schedule docs/plan_2026-09-15.md, Block 1). Zero calls.

  python tools/analysis/unfiltered_adopt.py

THE ITEM, quoted:
  "3. UNFILTERED-ADOPT. The 920-edge fit as the shipped parameters. Criterion: established-label profile rejects
   b1 = 0; utility >= 60%; established wrong calls at 0.975 not above the filtered fit's; LOAO row printed by
   systematic_budget.py (the 646/3/1.28, 70.2% figure exists only in the review's scratch). Prediction: adopted.
   0 calls."

THE RECORD IT CITES: systematic_budget.txt (891 fit b0 -3.2326 / b1 +3.3133; unfiltered refit -3.0438 / +3.1980
"printed and unused"; in-sample 665/2, LOAO 663/3/1.27; established 809 of 891, 26 wrong on established);
review_session_2026-09-14.md item 11 (unfiltered LOAO 646/3/1.28 = 2.3x, utility 70.2%, scratch only);
FRAMEWORK.md Stage 6 (the 920 pair "becomes the shipped pair when UNFILTERED-ADOPT lands"; established-label
profile "rejects b1 = 0 at delta-deviance 3.84 ... delta-dev 5.22 established / 19.06 all-label" on the 891 set;
utility "(called / raw called) 74.4% on x12" — that gloss is wrong: 74.4% = 663 / 891 = LOAO called over the edge
set, which is also what systematic_budget.py criterion (2) computes and what the review's 70.2% = 646 / 920 is).

READINGS FIXED BEFORE THE RUN (where the item is under-specified, the reading hardest on the programme's claims):
  (a) "established-label profile rejects b1 = 0": exact McNemar p < 0.05 on the anchor's JUDGED questions
      (systematic_budget.mcnemar_edge / established) selects the labels; on those edges OF THE 920 SET the
      profile deviance 2*[nll(b1 = 0, b0 profiled) - nll(MLE)] must be >= 3.84 (chi-square(1) at 5%). The
      likelihood is systematic_budget.nll (the vectorised copy used for the b0 profile and the cluster bootstrap
      is asserted equal to it at the MLE). The 891-set values are recomputed as a reproduction check.
  (b) "utility >= 60%": LOAO called / 920 edges (the harder denominator; called / raw called is printed too).
  (c) "established wrong calls at 0.975 not above the filtered fit's": scored on FOUR like-for-like comparisons,
      each fit against the other on the same edges and the same protocol — in sample on 920, in sample on 891,
      leave-one-anchor-out on 920, leave-one-anchor-out on 891 — and FAILS if the 920 fit has more established
      wrong calls on ANY of them. Primary = LOAO on the deployable 920 population. For the filtered fit's LOAO on
      920, each fold is trained on the 891-set edges outside the anchor and scores every 920-set edge inside it.
  (d) "LOAO row printed by systematic_budget.py": read literally. This test may not modify another script, so
      the row is printed HERE from systematic_budget's own functions (build via the KEY-TIE-DECLINE cache of
      sb.build(), fit, cbud, craw, mcnemar_edge, established) and verified against the review's scratch figure;
      whether systematic_budget.py itself prints it is scored on the committed file as it stands.
  Calibration status word by the framework's power rule (nominal < 3 -> UNDETERMINED); the wrong-direction rate
  on the unfiltered edge set with an exact 95% upper bound; every wrong count as all(established) with the key
  denominator named; Meta-Llama-3-70B-Instruct excluded (asserted absent). The composed rule (widener + decline)
  is printed for both fits as the shipped operating point. Nothing here decides adoption; it scores the item.
"""
import os, sys, math, pickle, time
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import norm, poisson, beta
import pool_guard
import systematic_budget as sb

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "unfiltered_adopt.txt")
SCRATCH = os.path.join(r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena",
                       "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad")
KTD_CACHE = os.path.join(SCRATCH, "bigpic", "ktd_x12_edges.pkl")        # key_tie_decline's cached sb.build()
CACHE = os.path.join(SCRATCH, "block1")
TH = sb.THRESH
ALPHA = 0.05
EXCLUDE = "Meta-Llama-3-70B-Instruct"
F_REC = (-3.2326, 3.3133)        # systematic_budget.txt, the 891 fit (shipped-pending)
U_REC = (-3.0438, 3.1980)        # systematic_budget.txt, the 920 refit (this test's candidate)
BOOT_REPS = 600; BOOT_SEED = 11  # the review's anchor-cluster bootstrap (chk_ci.py) convention


def log(msg):
    print("[ua %s] %s" % (time.strftime("%H:%M:%S"), msg), file=sys.stderr, flush=True)


def cached(name, fn):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if os.path.exists(p):
        log("cache hit %s" % name); return pickle.load(open(p, "rb"))
    log("building %s" % name); v = fn(); pickle.dump(v, open(p, "wb")); return v


def load_edges():
    if os.path.exists(KTD_CACHE):
        log("loading key_tie_decline's x12 cache"); models, K, P, E, aq = pickle.load(open(KTD_CACHE, "rb"))
        return models, K, P, E, aq
    def build():
        models, K, P, by, E, aq = sb.build(); return models, dict(K), dict(P), E, aq
    return cached("ua_x12_edges.pkl", build)


# ---- vectorised copy of systematic_budget.nll, for the b0 profile and the cluster bootstrap only ----
def vec_nll(es):
    A = np.array([e["agree"] for e in es]); M = np.abs(np.array([e["m"] for e in es]))
    S = np.array([e["s"] for e in es]); R = np.array([bool(e["right"]) for e in es])
    def f(b0, b1):
        tau = np.exp(np.minimum(20.0, b0 + b1 * A)); z = M / np.sqrt(S ** 2 + tau ** 2)
        pw = np.clip(norm.cdf(-z), 1e-12, 1 - 1e-12)
        return -float(np.sum(np.where(R, np.log(1 - pw), np.log(pw))))
    return f


def vec_fit(es, x0=(-3.0, 3.0)):
    f = vec_nll(es)
    r = minimize(lambda p: f(p[0], p[1]), np.array(x0), method="Nelder-Mead",
                 options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
    return float(r.x[0]), float(r.x[1])


def profile_dev(es, b0, b1, at_b1=0.0):
    """2 * [nll(b1 = at_b1, b0 profiled) - nll(b0, b1)] on the vectorised copy."""
    f = vec_nll(es)
    r = minimize_scalar(lambda b0_: f(b0_, at_b1), bounds=(-30, 5), method="bounded")
    return 2.0 * (r.fun - f(b0, b1)), float(r.x)


def profile_set(es, b0, b1, grid):
    f = vec_nll(es); base = f(b0, b1)
    dev = {g: 2.0 * (minimize_scalar(lambda b0_: f(b0_, g), bounds=(-30, 5), method="bounded").fun - base) for g in grid}
    ok = [g for g in grid if dev[g] < 3.84]
    return dev, (min(ok), max(ok)) if ok else (float("nan"), float("nan"))


def cluster_boot(es, ancs, reps, seed):
    rng = np.random.default_rng(seed)
    bya = {a: [e for e in es if e["anchor"] == a] for a in ancs}
    out = []
    for _ in range(reps):
        pick = rng.choice(len(ancs), len(ancs), replace=True)
        sub = [e for i in pick for e in bya[ancs[i]]]
        out.append(vec_fit(sub))
    return np.array(out)


def wrong(es):
    return [e for e in es if not e["right"]]


def loao(train_pool, score_pool, ancs, x0):
    """Fold per anchor: fit on train_pool edges outside it, score score_pool edges inside it. Returns oof c~ by id."""
    oof = {}; folds = {}
    for A_ in ancs:
        tr = [e for e in train_pool if e["anchor"] != A_]
        f0, f1 = sb.fit(tr, x0=x0); folds[A_] = (f0, f1)
        for e in score_pool:
            if e["anchor"] == A_:
                oof[id(e)] = sb.cbud(e, f0, f1)
    return oof, folds


def cp_upper(k, n, conf=0.95):
    """Exact (Clopper-Pearson) one-sided upper bound on a binomial rate."""
    if n == 0:
        return float("nan")
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))


# [MOVED 2026-09-23, zero calls] status_word (FRAMEWORK L101) now lives in calibration_status.py, byte for byte,
# so systematic_budget.py can print the registered word without a second copy; same name, same behaviour.
from calibration_status import status_word  # noqa: E402


def main():
    L = []
    t0 = time.time()
    models, K, P, E, aq = load_edges()
    assert EXCLUDE not in models, EXCLUDE
    F = [e for e in E if e["gap"] >= sb.GAP]
    ancs = sorted({e["anchor"] for e in E})
    assert ancs == sorted({e["anchor"] for e in F})
    pv = {id(e): sb.mcnemar_edge(e, K, aq)[0] for e in E}
    est = lambda es: [e for e in es if pv[id(e)] < ALPHA]
    n_est = lambda es: len(est(es))
    W = lambda es: "%d(%d)" % (len(wrong(es)), n_est(wrong(es)))

    L.append("=== UNFILTERED-ADOPT: the 920-edge widener fit as the shipped parameters (FRAMEWORK item 3, 0 calls) ===")
    L.append("  pool of record %s | key denominator for every McNemar: the anchor's JUDGED questions (anchor_qs, %d anchors,"
             % (pool_guard.FROZEN_POOL_ID, len(aq)))
    L.append("  %d distinct judged questions) | wrong counts as all(McNemar-established at %.2f) | %s excluded (asserted)"
             % (len(set().union(*aq.values())), ALPHA, EXCLUDE))
    L.append("  edges: key_tie_decline's cached systematic_budget.build() (bigpic/ktd_x12_edges.pkl); fits by systematic_budget.fit;")
    L.append("  c~ by systematic_budget.cbud; the vectorised likelihood copy is used only for the b0 profile and the bootstrap.")

    # ---------------- data check ----------------
    L.append("")
    L.append("=== 0. DATA CHECK against systematic_budget.txt ===")
    rcE = [e for e in E if sb.craw(e) >= TH]; rcF = [e for e in F if sb.craw(e) >= TH]
    L.append("  edges with any key gap %d, wrong %s   [record 920 / 60]" % (len(E), W(E)))
    L.append("  edges with gap >= %.2f   %d, wrong %s   [record 891 / 44]" % (sb.GAP, len(F), W(F)))
    L.append("  raw certificate at %.3f: ALL %d called / %s wrong = %.2f%%   [record 748 / 11 = 1.47%%]"
             % (TH, len(rcE), W(rcE), 100.0 * len(wrong(rcE)) / len(rcE)))
    L.append("  raw certificate at %.3f: FILTERED %d called / %s wrong = %.2f%%   [record 739 / 8 = 1.08%%]"
             % (TH, len(rcF), W(rcF), 100.0 * len(wrong(rcF)) / len(rcF)))
    excl = [e for e in E if e["gap"] < sb.GAP]
    L.append("  edges the filter excludes: %d, wrong %s = %.1f%%   [FRAMEWORK Stage 6 says '33 excluded edges, 52%% wrong-direction':"
             % (len(excl), W(excl), 100.0 * len(wrong(excl)) / len(excl)))
    L.append("    does not reproduce from this build (zero-gap edges are never built, systematic_budget.py build(): 'if gap == 0: continue');")
    L.append("    the correct statement is %d excluded edges, %d wrong = %.1f%%]" % (len(excl), len(wrong(excl)), 100.0 * len(wrong(excl)) / len(excl)))
    L.append("  established (McNemar p < %.2f): %d of %d on the 920 set (wrong on established %d, indeterminate wrong %d);"
             % (ALPHA, n_est(E), len(E), n_est(wrong(E)), len(wrong(E)) - n_est(wrong(E))))
    L.append("    %d of %d on the 891 set (wrong on established %d)   [record 809 of 891, 26 wrong on established]"
             % (n_est(F), len(F), n_est(wrong(F))))
    fb0, fb1 = sb.fit(F); ub0, ub1 = sb.fit(E)
    L.append("  891 fit: b0 = %+.4f | b1 = %+.4f   [record %+.4f / %+.4f]" % (fb0, fb1, F_REC[0], F_REC[1]))
    L.append("  920 fit: b0 = %+.4f | b1 = %+.4f   [record %+.4f / %+.4f]" % (ub0, ub1, U_REC[0], U_REC[1]))
    ok = abs(fb0 - F_REC[0]) < 5e-4 and abs(fb1 - F_REC[1]) < 5e-4 and abs(ub0 - U_REC[0]) < 5e-4 and abs(ub1 - U_REC[1]) < 5e-4
    L.append("  reproduction of both committed fits to 4 decimals: %s" % ("OK" if ok else "MISMATCH"))
    vn = vec_nll(E)(ub0, ub1); sn = sb.nll((ub0, ub1), E)
    L.append("  vectorised likelihood == systematic_budget.nll at the 920 MLE: %.6f vs %.6f (%s)"
             % (vn, sn, "OK" if abs(vn - sn) < 1e-6 else "MISMATCH"))
    if not ok:
        L.append("  !! the data object is not the one of record; every number below is on THIS build.")
    L.append("  tau(A) at A = 0.30 / 0.45 / 0.60 / 0.80 / 0.90:")
    for nm, (b0, b1) in (("891 fit", (fb0, fb1)), ("920 fit", (ub0, ub1))):
        L.append("    %-8s %s" % (nm, " / ".join("%.3f" % math.exp(b0 + b1 * a) for a in (0.30, 0.45, 0.60, 0.80, 0.90))))
    L.append("  monotonicity (edges the 920 fit makes MORE confident than c_raw, on 920 edges): %d (must be 0)"
             % sum(1 for e in E if sb.cbud(e, ub0, ub1) > sb.craw(e) + 1e-9))

    # ---------------- (a) established-label profile ----------------
    L.append("")
    L.append("=== (a) established-label profile rejects b1 = 0 (delta-deviance >= 3.84 at b1 = 0, b0 profiled) ===")
    grid = [round(x, 2) for x in np.arange(-4.0, 14.01, 0.25)]
    prof_rows = {}
    for nm, es, x0 in (("920 all-label", E, (ub0, ub1)), ("920 ESTABLISHED", est(E), (ub0, ub1)),
                       ("891 all-label", F, (fb0, fb1)), ("891 ESTABLISHED", est(F), (fb0, fb1))):
        b0, b1 = sb.fit(es, x0=x0)
        dev0, b0_at0 = profile_dev(es, b0, b1, 0.0)
        devs, (lo, hi) = profile_set(es, b0, b1, grid)
        prof_rows[nm] = (b0, b1, dev0, lo, hi, len(es), len(wrong(es)))
        L.append("  %-16s n = %3d (wrong %2d): MLE b0 = %+.4f b1 = %+.4f | delta-dev at b1 = 0: %6.2f -> %s | profile 95%% set for b1 [%.2f, %.2f]"
                 % (nm, len(es), len(wrong(es)), b0, b1, dev0, "REJECTED" if dev0 >= 3.84 else "NOT rejected", lo, hi))
    L.append("  [record, 891 set: delta-dev 5.22 established / 19.06 all-label; established refit b1 = +2.1430]")
    a_dev = prof_rows["920 ESTABLISHED"][2]
    a_pass = a_dev >= 3.84
    same_est = {id(e) for e in est(E)} == {id(e) for e in est(F)}
    L.append("  IDENTITY CHECK: established edges of the 920 set == established edges of the 891 set: %s (%d of the %d filter-excluded"
             % ("YES" if same_est else "NO", n_est(excl), len(excl)))
    L.append("    edges are established). %s" % ("So criterion (a) on the 920 set is the SAME likelihood as the record's 5.22: the unfiltered"
             " fit adds no established label, and (a) is a reproduction of the 891 result, not an independent identification."
             if same_est else "The 920 set adds established labels; (a) is a new identification."))

    # anchor-cluster bootstrap (the review's convention: 600 draws over the 14 anchors, seed 11), vectorised fit
    L.append("")
    L.append("  anchor-cluster bootstrap for b1 (%d draws over %d anchors, seed %d; the review's chk_ci.py convention):" % (BOOT_REPS, len(ancs), BOOT_SEED))
    boots = {}
    for nm, es in (("920 all-label", E), ("920 ESTABLISHED", est(E)), ("891 all-label", F)):
        bs = cached("ua_boot_%s.pkl" % nm.replace(" ", "_"), lambda es=es: cluster_boot(es, ancs, BOOT_REPS, BOOT_SEED))
        boots[nm] = bs
        b1s = bs[:, 1]
        L.append("    %-16s b1 95%% CI [%.2f, %.2f], P(b1 <= 0) = %.4f, CI width %.2f%s"
                 % (nm, np.percentile(b1s, 2.5), np.percentile(b1s, 97.5), (b1s <= 0).mean(),
                    np.percentile(b1s, 97.5) - np.percentile(b1s, 2.5),
                    "   [record 891: [1.72, 7.87], P = 0.0017]" if nm == "891 all-label" else ""))

    # ---------------- LOAO, both fits, both populations ----------------
    L.append("")
    L.append("=== LEAVE-ONE-ANCHOR-OUT (%d folds), both fits, both populations; the row the item asks for ===" % len(ancs))
    oofU_920, foldsU = loao(E, E, ancs, (ub0, ub1))          # 920 fit, deployable population
    oofF_920, foldsF = loao(F, E, ancs, (fb0, fb1))          # 891 fit, scored on every edge of the held-out anchor
    L.append("  fold b1 range: 920-trained %.4f .. %.4f | 891-trained %.4f .. %.4f"
             % (min(v[1] for v in foldsU.values()), max(v[1] for v in foldsU.values()),
                min(v[1] for v in foldsF.values()), max(v[1] for v in foldsF.values())))

    def row(label, es, cfun, denom):
        called = [e for e in es if cfun(e) >= TH]
        w = wrong(called); nom = sum(1 - cfun(e) for e in called)
        return dict(label=label, called=len(called), wrong=len(w), wrong_est=n_est(w), nominal=nom,
                    ratio=(len(w) / nom) if nom > 0 else float("nan"), util=len(called) / denom,
                    util_raw=len(called) / len([e for e in es if sb.craw(e) >= TH]),
                    lost=sum(1 for e in es if sb.craw(e) >= TH and e["right"]) - sum(1 for e in called if e["right"]),
                    called_edges=called)

    L.append("  %-44s %7s %9s %8s %7s %14s %14s %12s" % ("certificate", "called", "wrong(est)", "nominal", "ratio", "utility/edges", "called/rawcall", "correct lost"))
    rows = {}
    def put(key, r):
        rows[key] = r
        L.append("  %-44s %7d %9s %8.2f %6.1fx %13.1f%% %13.1f%% %12d"
                 % (r["label"], r["called"], "%d(%d)" % (r["wrong"], r["wrong_est"]), r["nominal"], r["ratio"],
                    100 * r["util"], 100 * r["util_raw"], r["lost"]))
    L.append("  -- on the 920 (deployable) population --")
    put("raw920", row("raw (tau = 0)", E, sb.craw, len(E)))
    put("U_in_920", row("920 fit, in sample", E, lambda e: sb.cbud(e, ub0, ub1), len(E)))
    put("F_in_920", row("891 fit, in sample (cold on the 29)", E, lambda e: sb.cbud(e, fb0, fb1), len(E)))
    put("U_lo_920", row("920 fit, LEAVE-ONE-ANCHOR-OUT", E, lambda e: oofU_920[id(e)], len(E)))
    put("F_lo_920", row("891 fit, LEAVE-ONE-ANCHOR-OUT (folds on 891)", E, lambda e: oofF_920[id(e)], len(E)))
    L.append("  -- on the 891 (filtered) population --")
    put("raw891", row("raw (tau = 0)", F, sb.craw, len(F)))
    put("U_in_891", row("920 fit, in sample", F, lambda e: sb.cbud(e, ub0, ub1), len(F)))
    put("F_in_891", row("891 fit, in sample", F, lambda e: sb.cbud(e, fb0, fb1), len(F)))
    put("U_lo_891", row("920 fit, LEAVE-ONE-ANCHOR-OUT (folds on 920)", F, lambda e: oofU_920[id(e)], len(F)))
    put("F_lo_891", row("891 fit, LEAVE-ONE-ANCHOR-OUT", F, lambda e: oofF_920[id(e)], len(F)))
    L.append("  [record: 891 in sample 665/2 nominal 1.30; 891 LOAO 663/3/1.27, 74.4%%, established 649/2/1.18;")
    L.append("   review scratch: 920 LOAO 646/3/1.28 = 2.3x, utility 70.2%; the derivation said 650/3]")
    U = rows["U_lo_920"]
    L.append("  THE ROW: 920 fit, LOAO: %d called / %d wrong (all(established) %d) / nominal %.2f = %.1fx, utility %.1f%% of 920 edges"
             % (U["called"], U["wrong"], U["wrong_est"], U["nominal"], U["ratio"], 100 * U["util"]))
    L.append("    matches the review's scratch (646 / 3 / 1.28, 70.2%%): %s"
             % ("YES" if (U["called"], U["wrong"], round(U["nominal"], 2), round(100 * U["util"], 1)) == (646, 3, 1.28, 70.2) else "NO"))
    agg = sum(1 - oofU_920[id(e)] for e in E)
    L.append("    out-of-fold nominal over ALL 920 edges: %.1f against %d observed wrong (%s; the aggregate has no bite at the"
             % (agg, len(wrong(E)), "CONSERVATIVE" if agg >= len(wrong(E)) else "OPTIMISTIC"))
    L.append("    operating point, review item 6; it is printed for parity with systematic_budget.txt and not scored)")

    # ---------------- calibration statement, power rule ----------------
    L.append("")
    L.append("=== CALIBRATION STATEMENT for the 920 fit (framework Stage 6 wording) ===")
    for key in ("U_in_920", "U_lo_920"):
        r = rows[key]; ub = cp_upper(r["wrong"], r["called"])
        L.append("  %-40s called %d | wrong %d(%d) | nominal %.2f | wrong-direction rate on the unfiltered set %.2f%% (95%% UB %.2f%%) | %s"
                 % (r["label"], r["called"], r["wrong"], r["wrong_est"], r["nominal"], 100.0 * r["wrong"] / r["called"], 100 * ub,
                    status_word(r["nominal"], r["wrong"])))
    L.append("  Poisson P(>= %d | %.2f) = %.3f for the LOAO row (the 891 row's P(>= 3 | 1.27) = 0.135)"
             % (U["wrong"], U["nominal"], 1 - poisson.cdf(U["wrong"] - 1, U["nominal"])))

    # ---------------- the wrong calls, named ----------------
    L.append("")
    L.append("=== WRONG CALLS at %.3f under the 920 fit (McNemar b:c, p on the anchor's judged questions) ===" % TH)
    for key, label in (("U_in_920", "in sample"), ("U_lo_920", "LOAO")):
        L.append("  %s:" % label)
        for e in sorted(wrong(rows[key]["called_edges"]), key=lambda e: pv[id(e)]):
            p_, b_, c_ = sb.mcnemar_edge(e, K, aq)
            cf = sb.cbud(e, fb0, fb1) if key == "U_in_920" else oofF_920[id(e)]
            L.append("    %-14s %-26s vs %-26s gap %.4f A %.3f | c~(920) %.4f, c~(891) %.4f | McNemar %d:%d p = %.4f -> %s%s"
                     % (e["anchor"][:14], e["a"][:26], e["b"][:26], e["gap"], e["agree"],
                        (sb.cbud(e, ub0, ub1) if key == "U_in_920" else oofU_920[id(e)]), cf,
                        b_, c_, p_, "ESTABLISHED" if p_ < ALPHA else "indeterminate",
                        "" if e["gap"] >= sb.GAP else " [gap < 0.02: outside the 891 set]"))

    # ---------------- composed rule: widener + decline (the shipped operating point) ----------------
    L.append("")
    L.append("=== COMPOSED RULE widener + decline at %.3f (KEY-TIE-DECLINE), both fits, 920 population ===" % TH)
    L.append("  %-40s %7s %8s %13s" % ("base", "called", "residue", "residue wrong"))
    for label, cfun in (("920 fit, in sample", lambda e: sb.cbud(e, ub0, ub1)), ("891 fit, in sample", lambda e: sb.cbud(e, fb0, fb1)),
                        ("920 fit, LOAO", lambda e: oofU_920[id(e)]), ("891 fit, LOAO", lambda e: oofF_920[id(e)])):
        called = [e for e in E if cfun(e) >= TH]; res = est(called)
        L.append("  %-40s %7d %8d %13d   (established by construction)" % (label, len(called), len(res), len(wrong(res))))
    L.append("  [record, 891 population: widener + decline 651 / 1(1)]")

    # ---------------- (b), (c), (d) ----------------
    L.append("")
    L.append("=== REGISTERED CRITERIA ===")
    L.append("  (a) established-label profile rejects b1 = 0 on the 920 set: delta-dev %.2f vs 3.84 -> %s"
             % (a_dev, "PASS" if a_pass else "FAIL"))
    L.append("      (all-label 920: %.2f; 891 established %.2f / all-label %.2f, record 5.22 / 19.06)"
             % (prof_rows["920 all-label"][2], prof_rows["891 ESTABLISHED"][2], prof_rows["891 all-label"][2]))
    L.append("      CAVEAT: the established set is the 891 set's (identity check above), so this is the record's number reproduced;")
    L.append("      the anchor-cluster bootstrap on established labels has P(b1 <= 0) = %.3f with the percentile CI touching 0 -"
             % float((boots["920 ESTABLISHED"][:, 1] <= 0).mean()))
    L.append("      the profile at 3.84 is the registered instrument and it rejects; the cluster bootstrap would not at 95%.")
    b_pass = U["util"] >= 0.60
    L.append("  (b) utility >= 60%%: LOAO called / 920 edges = %d / 920 = %.1f%% -> %s   (called / raw called = %.1f%%; in sample %.1f%%)"
             % (U["called"], 100 * U["util"], "PASS" if b_pass else "FAIL", 100 * U["util_raw"], 100 * rows["U_in_920"]["util"]))
    comps = (("LOAO on 920 (primary)", "U_lo_920", "F_lo_920"), ("in sample on 920", "U_in_920", "F_in_920"),
             ("LOAO on 891", "U_lo_891", "F_lo_891"), ("in sample on 891", "U_in_891", "F_in_891"))
    c_fail = []
    L.append("  (c) established wrong calls at %.3f not above the filtered fit's, four like-for-like comparisons:" % TH)
    for nm, ku, kf in comps:
        ru, rf = rows[ku], rows[kf]
        bad = ru["wrong_est"] > rf["wrong_est"]
        if bad:
            c_fail.append(nm)
        L.append("      %-24s 920 fit %d(%d) of %d called  vs  891 fit %d(%d) of %d called  -> %s"
                 % (nm, ru["wrong"], ru["wrong_est"], ru["called"], rf["wrong"], rf["wrong_est"], rf["called"],
                    "ABOVE" if bad else ("equal" if ru["wrong_est"] == rf["wrong_est"] else "below")))
    c_pass = not c_fail
    L.append("      -> %s%s" % ("PASS (not above on any comparison)" if c_pass else "FAIL on: " + ", ".join(c_fail),
                              "" if c_pass else " (the hardest reading; the primary comparison alone: %s)"
                              % ("above" if "LOAO on 920 (primary)" in c_fail else "not above")))
    sbpath = os.path.join(HERE, "systematic_budget.py")
    src = open(sbpath, encoding="utf-8").read()
    prints_row = 'for e in all_edges if e["anchor"] != A_' in src      # a LOAO fold over the 920 set, absent at eaf1dbf
    L.append("  (d) LOAO row printed by systematic_budget.py: the committed script prints the 920 refit (b0, b1) and no unfiltered LOAO")
    L.append("      row (%s); this test may not modify it, so the row is printed above from its functions and matches the review's"
             % ("it does now" if prints_row else "checked on the file as it stands: absent"))
    L.append("      scratch to the digit -> %s on the literal wording; the row now exists in this test's output (this file, from"
             % ("PASS" if prints_row else "NOT MET"))
    L.append("      systematic_budget's committed functions); adding it to systematic_budget.py is a one-block engineering change for Block 4.")
    L.append("  PREDICTION 'adopted': the item's three numeric criteria %s; (d) is %s. Adoption is the record's decision, taken on"
             % ("all PASS" if (a_pass and b_pass and c_pass) else "do NOT all pass", "PASS" if prints_row else "NOT MET on the literal wording"))
    L.append("      these numbers: the 920 pair (b0 = %+.4f, b1 = %+.4f) %s the 891 pair on the deployable population at the same"
             % (ub0, ub1, "is not worse than" if c_pass else "is worse than"))
    L.append("      operating point, identified on established labels at delta-dev %.2f, at utility %.1f%%, with calibration %s."
             % (a_dev, 100 * U["util"], status_word(U["nominal"], U["wrong"]).split(" (")[0]))
    L.append("")
    L.append("  elapsed %.0f s; nothing posted; no network." % (time.time() - t0))

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
