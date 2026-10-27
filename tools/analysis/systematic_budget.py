"""SYSTEMATIC-BUDGET — fit the continuous widener SYSTEMATIC-SIGNAL licensed (registered 2026-09-14).

  python tools/analysis/systematic_budget.py

[APPENDED 2026-09-23, engine-coder, zero calls — two defects repaired; nothing above or below is rewritten.]

  python tools/analysis/systematic_budget.py --edges filtered      # the historical path: the 891 key-gap
                                                                   # >= 0.02 set; reproduces the file of
                                                                   # record byte for byte except the
                                                                   # criterion-(1) lines
  python tools/analysis/systematic_budget.py --edges unfiltered    # the deployable 920 any-gap set;
                                                                   # writes systematic_budget_unfiltered.txt

  --edges is REQUIRED and fail-closed. It is not defaulted because the record does not establish one:
  FRAMEWORK L95 says the 920 pair "becomes the shipped pair WHEN UNFILTERED-ADOPT LANDS", and
  UNFILTERED-ADOPT's own state is "ADOPTED: NOT YET (BLOCK 4)" (docs/test_ledger.html row
  UNFILTERED-ADOPT), while GROK-CALIB and ITEM-26-POOLED already report on the 920 denominator. Two
  parameter pairs are therefore in circulation as "the widener" (891: b0 -3.2326 / b1 +3.3133; 920:
  b0 -3.0438 / b1 +3.1980) and the script refuses to choose one silently. The selected set drives the
  WHOLE pipeline (fit, monotonicity, LOAO, all four registered criteria); the active set and its pair
  are announced on stderr on every run, pass or fail, and the section-(1) heading names the set in the
  file of record.

  Criterion (1) is now evaluated on the CALLED set (lo_wrong <= lo_nom), which is the criterion as
  registered ("realised wrong-direction rate at or below nominal" AT the operating point). The verdict
  word "PASS in aggregate" can no longer be printed: it was refuted on 2026-09-15 by the REVIEW ("criterion (1) 'PASS in
  aggregate' is carried by the 228 uncalled edges; at the operating point it is 3 wrong vs 1.27 nominal,
  UNDETERMINED; a doubled widener also passes the aggregate"), and the instrument was still printing it
  next to the called-set numbers, i.e. a verdict word and numbers computed on two different populations.
  The aggregate survives beside it, labelled DESCRIPTIVE and explicitly not the criterion.
  [CORRECTED 2026-09-23 by the branch review: the status word printed for criterion (1) is FRAMEWORK L101's
  (calibration_status.status_word: UNDETERMINED when nominal < 3; UNDETERMINED (power) when 3 <= nominal < 9;
  NOT DETECTABLY MISCALIBRATED / MISCALIBRATED at Poisson 0.05 only when nominal >= 9), not a rule of this
  script's own; the count beside it is wrong(established).]

TIER-HONEST: a bootstrap interval tightens around the wrong answer wherever the judge is systematically
biased, because resampling cannot see a bias present in every sample. SYSTEMATIC-SIGNAL showed two signals
predict where that happens, and that as a HARD GATE they are poor. RESOLVE wants a continuous WIDENER: a
systematic variance added to each edge so the realised wrong-direction rate matches the nominal one.

THE ADOPTED FORM, chosen from four by an adversarial derivation pass:

    A_e  = answer agreement between the two models on the cell's questions      (no key)
    m_e  = mean(theta_a - theta_b) over the B bootstrap boards                  (no key)
    s_e  = sd  (theta_a - theta_b) over the B bootstrap boards, ddof=1          (no key)
    tau_e = exp(b0 + b1 * A_e)                                                  TWO free parameters
    c_e  = min( c_raw_e , Phi( |m_e| / sqrt(s_e^2 + tau_e^2) ) )
    call the edge iff c_e >= 0.975

REFERENCE ACCURACY IS DELIBERATELY EXCLUDED. It fits better (the two-predictor LOAO deviance is 193.55
against 216.94) and it is NOT DEPLOYABLE: `rejudge_reference.references()` returns the reference graded
against the answer key, so per-cell reference accuracy is a key-derived quantity. SYSTEMATIC-SIGNAL called
it a "free signal", which was wrong - free of extra CALLS, not free of the KEY. Registered criterion (3)
forbids a key input at inference, so the shipped budget carries agreement only.
"""
import argparse, os, sys, math, random, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
import rejudge_grok as rj
import rejudge_reference as rref
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import pool_guard
from calibration_status import status_word   # FRAMEWORK L101, the one home of the status word

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "systematic_budget.txt")
OUT_UNFILTERED = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "systematic_budget_unfiltered.txt")
B = 300
THRESH = 0.975
GAP = 0.02          # the key-gap filter SYSTEMATIC-SIGNAL used; this script reports WITH and WITHOUT it


def build():
    """Per-anchor edges with the bootstrap's first two moments, plus the pooled 66-pair board."""
    models = sorted(p8.ARENA12)
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict); P = defaultdict(dict)
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in p8.ARENA12:
            K[q][m] = int(c or 0); P[q][m] = (pr or "").strip().upper()[:1]
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(list)
    for a, b, q, w, _ in rows:
        if q in route:
            by[anchor_of(route[q])].append((a, b, q, w))

    rng = random.Random(42)                      # same seed and draw order as systematic_signal.py
    anchor_qs = {}
    edges = []
    for anc in sorted(by):
        rs = by[anc]
        if len(rs) < 200:
            continue
        qs = sorted({q for _, _, q, _ in rs})
        anchor_qs[anc] = qs
        byq = defaultdict(list)
        for r in rs:
            byq[r[2]].append(r)
        draws = []
        for _ in range(B):
            pick = [qs[rng.randrange(len(qs))] for _ in qs]
            sub = [r for q in pick for r in byq[q]]
            draws.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                                        for a, b, _, w in sub], models))
        la = {}
        for m in models:
            v = [K[q].get(m) for q in qs if K[q].get(m) is not None]
            if v:
                la[m] = sum(v) / len(v)
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if a not in la or b not in la:
                    continue
                gap = abs(la[a] - la[b])
                if gap == 0:
                    continue
                d = np.array([dr[a] - dr[b] for dr in draws])
                p = float((d > 0).mean())
                both = [q for q in qs if P[q].get(a) and P[q].get(b)]
                if not both:
                    continue
                agree = sum(1 for q in both if P[q][a] == P[q][b]) / len(both)
                edges.append(dict(anchor=anc, a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                                  right=((p > 0.5) == (la[a] > la[b])), agree=agree, gap=gap, n=len(both)))
    return models, K, P, by, edges, anchor_qs


def pooled_board(by, K, P, models, rng):
    """The 66-pair board over every question, which is the object TIER-HONEST flagged."""
    rs = [r for anc in by for r in by[anc]]
    qs = sorted({q for _, _, q, _ in rs})
    byq = defaultdict(list)
    for r in rs:
        byq[r[2]].append(r)
    draws = []
    for _ in range(B):
        pick = [qs[rng.randrange(len(qs))] for _ in qs]
        sub = [r for q in pick for r in byq[q]]
        draws.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                                    for a, b, _, w in sub], models))
    la = {}
    for m in models:
        v = [K[q].get(m) for q in qs if K[q].get(m) is not None]
        if v:
            la[m] = sum(v) / len(v)
    out = []
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            d = np.array([dr[a] - dr[b] for dr in draws])
            p = float((d > 0).mean())
            both = [q for q in qs if P[q].get(a) and P[q].get(b)]
            agree = sum(1 for q in both if P[q][a] == P[q][b]) / len(both) if both else 0.0
            out.append(dict(a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                            right=((p > 0.5) == (la[a] > la[b])), agree=agree, gap=abs(la[a] - la[b])))
    return out


def craw(e):
    return max(e["p"], 1 - e["p"])


def cbud(e, b0, b1):
    tau = math.exp(b0 + b1 * e["agree"])
    g = float(norm.cdf(abs(e["m"]) / math.sqrt(e["s"] ** 2 + tau ** 2)))
    return min(craw(e), g)


def nll(par, es):
    """Wrong-direction likelihood. P(wrong) = Phi(-|m| / sqrt(s^2 + tau^2))."""
    b0, b1 = par
    t = 0.0
    for e in es:
        tau = math.exp(min(20.0, b0 + b1 * e["agree"]))
        z = abs(e["m"]) / math.sqrt(e["s"] ** 2 + tau ** 2)
        pw = min(max(float(norm.cdf(-z)), 1e-12), 1 - 1e-12)
        t -= math.log(pw) if not e["right"] else math.log(1 - pw)
    return t


def fit(es, x0=(-3.0, 3.0)):
    r = minimize(nll, np.array(x0), args=(es,), method="Nelder-Mead",
                 options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
    return float(r.x[0]), float(r.x[1])


def summarise(es, b0, b1, thresh=THRESH):
    raw_called = [e for e in es if craw(e) >= thresh]
    bud_called = [e for e in es if cbud(e, b0, b1) >= thresh]
    return (len(raw_called), sum(1 for e in raw_called if not e["right"]),
            len(bud_called), sum(1 for e in bud_called if not e["right"]),
            sum(1 - cbud(e, b0, b1) for e in bud_called))


def mcnemar_edge(e, K, anchor_qs):
    """Exact two-sided McNemar on the two models' per-question correctness over the anchor's JUDGED questions.

    Returns (p, b, c). Module-level so budget_transfer, budget_lomo and low_agreement apply the SAME test on the
    SAME denominator (the anchor's judged questions, not every pool question routed to it) - the review of
    2026-09-15 found the two denominators give 809 vs 826 established edges and flip individual labels."""
    b_ = c_ = 0
    for q in anchor_qs[e["anchor"]]:
        ka = K.get(q, {}).get(e["a"]); kb = K.get(q, {}).get(e["b"])
        if ka is None or kb is None or ka == kb:
            continue
        if ka > kb: b_ += 1
        else: c_ += 1
    n = b_ + c_
    if n == 0:
        return 1.0, 0, 0
    k = min(b_, c_)
    # exact integer arithmetic: 2.0 ** n overflows a float above n = 1024, which the pooled 2,811-question
    # board reaches (found 2026-09-15 when KEY-TIE-DECLINE applied this helper to pooled edges)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)), b_, c_


def established(edges, K, anchor_qs, alpha=0.05):
    return [e for e in edges if mcnemar_edge(e, K, anchor_qs)[0] < alpha]


def parse_args(argv=None):
    """--edges is REQUIRED: the record does not establish a default (see the docstring)."""
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    ap.add_argument("--edges", choices=("filtered", "unfiltered"), default=None,
                    help="which edge set drives the WHOLE pipeline: 'filtered' = the 891 key-gap >= 0.02 "
                         "set (b0 -3.2326 / b1 +3.3133), 'unfiltered' = the 920 any-gap deployable set "
                         "(b0 -3.0438 / b1 +3.1980)")
    a = ap.parse_args(argv)
    if a.edges is None:
        raise SystemExit("[SYSTEMATIC-BUDGET] --edges is REQUIRED and has no default: pass --edges filtered "
                         "(the 891 key-gap >= %.2f set, the historical fit b0 -3.2326 / b1 +3.3133) or "
                         "--edges unfiltered (the 920 any-gap deployable set, b0 -3.0438 / b1 +3.1980). "
                         "The record does not establish one: FRAMEWORK L95 makes the 920 pair the shipped "
                         "pair only WHEN UNFILTERED-ADOPT LANDS, and UNFILTERED-ADOPT reads 'ADOPTED: NOT "
                         "YET (BLOCK 4)'." % GAP)
    return a


def main(edge_set):
    L = []
    models, K, P, by, all_edges, anchor_qs = build()
    filt = [e for e in all_edges if e["gap"] >= GAP]
    # the ACTIVE set: fit, monotonicity, LOAO and all four registered criteria run on it
    sel = filt if edge_set == "filtered" else all_edges
    other = all_edges if edge_set == "filtered" else filt
    sel_name = "filtered" if edge_set == "filtered" else "unfiltered"
    other_name = "unfiltered" if edge_set == "filtered" else "filtered"

    L.append("=== SYSTEMATIC-BUDGET: fit the continuous widener, and check it independently ===")
    L.append("  form: tau(A) = exp(b0 + b1*A) added in quadrature to the bootstrap SD; call iff")
    L.append("  min(c_raw, Phi(|m|/sqrt(s^2+tau^2))) >= %.3f. TWO free parameters, NO key at inference." % THRESH)
    L.append("")
    L.append("  THE POPULATION, and the correction it forces to a number already published:")
    L.append("    edges with ANY key gap (the honest denominator): %d, of which %d point the wrong way"
             % (len(all_edges), sum(1 for e in all_edges if not e["right"])))
    L.append("    edges with a key gap >= %.2f (what SYSTEMATIC-SIGNAL reported): %d, %d wrong"
             % (GAP, len(filt), sum(1 for e in filt if not e["right"])))
    rc_all = [e for e in all_edges if craw(e) >= THRESH]
    rc_f = [e for e in filt if craw(e) >= THRESH]
    L.append("    raw certificate on ALL edges:      %d called, %d wrong = %.2f%%"
             % (len(rc_all), sum(1 for e in rc_all if not e["right"]),
                100.0 * sum(1 for e in rc_all if not e["right"]) / max(1, len(rc_all))))
    L.append("    raw certificate on FILTERED edges: %d called, %d wrong = %.2f%%"
             % (len(rc_f), sum(1 for e in rc_f if not e["right"]),
                100.0 * sum(1 for e in rc_f if not e["right"]) / max(1, len(rc_f))))
    L.append("    The key-gap filter is not available at deployment AND it selects the population - the")
    L.append("    excluded edges are far more often wrong. Every published rate must be restated on the")
    L.append("    unfiltered denominator.")

    # ---------- the fit ----------
    b0, b1 = fit(sel)
    # the active set and its pair, announced on every run, pass or fail (guard hygiene 2026-09-23); on
    # stderr so the file of record stays byte-identical on the historical --edges filtered path
    sys.stderr.write("[SYSTEMATIC-BUDGET] ACTIVE EDGE SET = %s (%d edges, %d wrong) | b0 = %+.4f | b1 = %+.4f"
                     " | every criterion below is computed on this set\n"
                     % (sel_name, len(sel), sum(1 for e in sel if not e["right"]), b0, b1))
    L.append("")
    if edge_set == "filtered":
        L.append("=== (1) THE FIT, on the %d filtered edges so it is comparable to the derivation ===" % len(sel))
    else:
        L.append("=== (1) THE FIT, on the %d unfiltered edges (the deployable any-gap denominator) ===" % len(sel))
    L.append("  b0 = %+.4f | b1 = %+.4f" % (b0, b1))
    L.append("  tau at A = 0.30 / 0.45 / 0.60 / 0.80 / 0.90: %s"
             % " / ".join("%.3f" % math.exp(b0 + b1 * a) for a in (0.30, 0.45, 0.60, 0.80, 0.90)))
    ss = sorted(e["s"] for e in sel)
    L.append("  against a per-anchor bootstrap s of median %.3f (p10 %.3f, p90 %.3f)"
             % (ss[len(ss) // 2], ss[len(ss) // 10], ss[9 * len(ss) // 10]))
    L.append("  b1 > 0 means the widener GROWS with answer agreement, which is the direction")
    L.append("  SYSTEMATIC-SIGNAL predicted (+1.511, z=+7.0).")

    b0u, b1u = fit(other)
    L.append("  refit on the %s %d: b0 = %+.4f | b1 = %+.4f" % (other_name, len(other), b0u, b1u))

    # ---------- no call is ever created ----------
    created = sum(1 for e in sel if cbud(e, b0, b1) > craw(e) + 1e-9)
    L.append("")
    L.append("  MONOTONICITY CHECK: edges the budget makes MORE confident: %d (must be 0)" % created)

    # ---------- in sample and leave-one-anchor-out ----------
    L.append("")
    L.append("=== (2) CALIBRATION: in sample and leave-one-ANCHOR-out (14 folds) ===")
    L.append("  %-26s %8s %7s %9s %8s" % ("certificate", "called", "wrong", "nominal", "ratio"))
    rcn, rcw, _, _, _ = summarise(sel, -50.0, 0.0)
    nom_raw = sum(1 - float(norm.cdf(abs(e["m"]) / e["s"])) for e in sel if craw(e) >= THRESH)
    L.append("  %-26s %8d %7d %9.2f %8s" % ("raw (tau = 0)", rcn, rcw, nom_raw,
                                            "%.1fx" % (rcw / nom_raw) if nom_raw > 0 else "-"))
    cn, cw, bn, bw, nom = summarise(sel, b0, b1)
    L.append("  %-26s %8d %7d %9.2f %8s" % ("budget, in sample", bn, bw, nom,
                                            "%.1fx" % (bw / nom) if nom > 0 else "-"))

    ancs = sorted({e["anchor"] for e in sel})
    oof = {}
    for A_ in ancs:
        tr = [e for e in sel if e["anchor"] != A_]
        te = [e for e in sel if e["anchor"] == A_]
        f0, f1 = fit(tr, x0=(b0, b1))
        for e in te:
            oof[id(e)] = cbud(e, f0, f1)
    lo_called = [e for e in sel if oof[id(e)] >= THRESH]
    lo_wrong = sum(1 for e in lo_called if not e["right"])
    lo_nom = sum(1 - oof[id(e)] for e in lo_called)
    L.append("  %-26s %8d %7d %9.2f %8s" % ("budget, LEAVE-ONE-ANCHOR-OUT", len(lo_called), lo_wrong, lo_nom,
                                            "%.1fx" % (lo_wrong / lo_nom) if lo_nom > 0 else "-"))
    sel_wrong = sum(1 for e in sel if not e["right"])
    agg = sum(1 - oof[id(e)] for e in sel)
    L.append("  out-of-fold nominal over ALL %d edges: %.1f against %d observed wrong  (%s)"
             % (len(sel), agg, sel_wrong, "CONSERVATIVE" if agg >= sel_wrong else "OPTIMISTIC"))

    L.append("")
    L.append("  REGISTERED CRITERIA:")
    frac = len(lo_called) / len(sel)
    # CRITERION (1), REPAIRED 2026-09-23 (zero calls). The registered criterion is the realised
    # wrong-direction rate AT THE OPERATING POINT, so it is evaluated on the CALLED set - lo_wrong
    # against lo_nom, the same population as the numbers printed beside it. The old line printed the
    # word "PASS in aggregate", decided by `agg >= wrong over ALL edges`, next to the called-set
    # numbers: a verdict and its evidence computed on two different populations. The REVIEW of
    # 2026-09-15 refuted that reading ("carried by the 228 uncalled edges ... a doubled widener also
    # passes the aggregate"); the aggregate is kept below as a DESCRIPTIVE line only.
    # [CORRECTED 2026-09-23 by the branch review] the status word is FRAMEWORK L101's, imported from
    # calibration_status (the same object unfiltered_adopt prints), never a rule of this script's own; the
    # count is wrong(established), CONTEXT section 3, established by mcnemar_edge on the anchor's judged questions.
    n_unc = len(sel) - len(lo_called)
    lo_wrong_est = len(established([e for e in lo_called if not e["right"]], K, anchor_qs))
    L.append("   (1) LOAO calibration, realised at or below nominal - THE CRITERION OF RECORD, on the")
    L.append("       CALLED set at the %.3f operating point: %s" % (THRESH, status_word(lo_nom, lo_wrong)))
    L.append("       wrong(established) %d(%d) of %d called vs %.2f nominal = %s (status word: FRAMEWORK L101)"
             % (lo_wrong, lo_wrong_est, len(lo_called), lo_nom,
                "%.1fx" % (lo_wrong / lo_nom) if lo_nom > 0 else "-"))
    L.append("       DESCRIPTIVE, NOT THE CRITERION: out-of-fold nominal over ALL %d edges %.1f against"
             % (len(sel), agg))
    L.append("       %d observed wrong = %s, carried by the %d edges the certificate never calls"
             % (sel_wrong, "CONSERVATIVE" if agg >= sel_wrong else "OPTIMISTIC", n_unc))
    L.append("       (%d wrong vs %.2f nominal). [CORRECTED 2026-09-15 by the REVIEW: the aggregate has"
             % (sel_wrong - lo_wrong, agg - lo_nom))
    L.append("       no bite - a doubled widener also passes it - and it is NOT the verdict word.]")
    L.append("   (2) still calls >= 60%% of edges: %s (%.1f%%)" % ("PASS" if frac >= 0.60 else "FAIL", 100 * frac))
    L.append("   (3) no answer-key input at inference: PASS - inputs are m, s and answer agreement only")
    L.append("   (4) at most 3 free parameters: PASS - two, and no bins or fitted thresholds")

    # ---------- the registered headline prediction ----------
    L.append("")
    L.append("=== (3) THE REGISTERED HEADLINE PREDICTION: does arx/iask stop being separated? ===")
    rng = random.Random(43)
    pool = pooled_board(by, K, P, models, rng)
    pr_called = [e for e in pool if craw(e) >= THRESH]
    pb_called = [e for e in pool if cbud(e, b0, b1) >= THRESH]
    L.append("  pooled 66-pair board: raw %d called / %d wrong  ->  budget %d called / %d wrong"
             % (len(pr_called), sum(1 for e in pr_called if not e["right"]),
                len(pb_called), sum(1 for e in pb_called if not e["right"])))
    ai = [e for e in pool if {e["a"], e["b"]} == {"arx_0314", "iask_pro"}]
    for e in ai:
        L.append("  arx vs iask: raw c %.4f -> budget c %.4f | agreement %.3f | key direction %s"
                 % (craw(e), cbud(e, b0, b1), e["agree"], "right" if e["right"] else "WRONG"))
        L.append("  -> %s" % ("PREDICTION HELD: the budget withdraws the separation the key contradicts"
                              if cbud(e, b0, b1) < THRESH else
                              "PREDICTION FAILED: still separated, and the budget does not do its job"))
    L.append("")
    L.append("  pooled pairs that LOSE their call:")
    L.append("  %-46s %7s %8s %8s" % ("pair", "agree", "budget c", "key"))
    for e in sorted(pool, key=lambda e: -cbud(e, b0, b1)):
        if craw(e) >= THRESH > cbud(e, b0, b1):
            L.append("  %-46s %7.3f %8.4f %8s" % ("%s vs %s" % (e["a"][:20], e["b"][:20]), e["agree"],
                                                  cbud(e, b0, b1), "right" if e["right"] else "WRONG"))

    # ---------- the attack that killed the conformal form ----------
    L.append("")
    L.append("  pooled board, every pair the KEY says the arena has backwards:")
    for e in pool:
        if not e["right"]:
            L.append("    %-46s key gap %.4f | raw c %.4f -> budget c %.4f"
                     % ("%s vs %s" % (e["a"][:20], e["b"][:20]), e["gap"], craw(e), cbud(e, b0, b1)))
    L.append("")
    L.append("=== (4) LABEL NOISE: how much of the fit is edges the key cannot actually adjudicate? ===")
    L.append("  An edge's 'wrong direction' label rests on a key gap that is itself an estimate. Refit using")
    L.append("  only edges whose key direction is established by an exact binomial at 5%.")
    # [DE-DUPLICATED 2026-09-23, zero calls] this block carried a second, byte-identical copy of the
    # McNemar computation (the module-level mcnemar_edge is the one budget_transfer, budget_lomo and
    # low_agreement import). Two copies of the same arithmetic are the hazard FRAMEWORK guard 22 names
    # for withinNull/siteNull: an edit sited by content lands in the wrong copy and still runs. Same
    # inputs, same integer math.comb arithmetic, same operation order, so this is byte-inert.
    def mcnemar_p(e):
        return mcnemar_edge(e, K, anchor_qs)

    est = []; indet = []
    for e in sel:
        pv, b_, c_ = mcnemar_p(e)
        (est if pv < 0.05 else indet).append(e)
    L.append("  test: exact two-sided McNemar on the two models' per-question correctness in that anchor.")
    L.append("  established at 5%%: %d of %d edges | indeterminate: %d" % (len(est), len(sel), len(indet)))
    wr_est = sum(1 for e in est if not e["right"]); wr_ind = sum(1 for e in indet if not e["right"])
    L.append("  wrong-direction edges: %d of %d sit on ESTABLISHED labels, %d of %d on indeterminate ones"
             % (wr_est, len(est), wr_ind, len(indet)))
    L.append("  so %d of the %d wrong edges (%.0f%%) rest on a key direction the key does not establish"
             % (wr_ind, wr_est + wr_ind, 100.0 * wr_ind / max(1, wr_est + wr_ind)))
    if len(est) > 50:
        e0, e1 = fit(est, x0=(b0, b1))
        L.append("  refit on established-direction edges only: b1 = %+.4f against %+.4f (%.0f%% of it)"
                 % (e1, b1, 100.0 * e1 / b1))
        L.append("  -> %s" % ("the fitted effect SURVIVES the attack that killed the conformal form"
                              if e1 > 0.4 * b1 else
                              "MOST of the fit is label indeterminacy and the scale cannot be trusted"))

    # ---------- (5) does the fitted widener actually beat a one-line agreement gate? ----------
    L.append("")
    L.append("=== (5) THE COMPARISON THAT DECIDES WHETHER THE FIT EARNS ITS KEEP ===")
    L.append("  SYSTEMATIC-SIGNAL rejected a hard gate on the grounds that at a ~1% base rate any gate")
    L.append("  catching half the errors discards many good calls. That argued against a gate as a SUBSTITUTE")
    L.append("  for the certificate. It did NOT establish that a fitted two-parameter widener beats one. This")
    L.append("  compares them on the same edges at the same operating point, out of fold for the budget.")
    L.append("")
    rc_sel = [e for e in sel if craw(e) >= THRESH]   # raw calls on the ACTIVE set (== rc_f when filtered)
    L.append("  PER-ANCHOR (%d raw calls, %d wrong):" % (len(rc_sel), sum(1 for e in rc_sel if not e["right"])))
    L.append("  %-34s %8s %7s %14s" % ("rule", "called", "wrong", "correct lost"))
    base_right = sum(1 for e in rc_sel if e["right"])
    L.append("  %-34s %8d %7d %14d" % ("raw certificate", len(rc_sel), sum(1 for e in rc_sel if not e["right"]), 0))
    L.append("  %-34s %8d %7d %14d" % ("budget, out of fold", len(lo_called), lo_wrong,
                                       base_right - sum(1 for e in lo_called if e["right"])))
    for t in (0.60, 0.65, 0.70, 0.75, 0.80, 0.85):
        g = [e for e in rc_sel if e["agree"] < t]
        L.append("  %-34s %8d %7d %14d" % ("agreement gate A < %.2f" % t, len(g),
                                           sum(1 for e in g if not e["right"]),
                                           base_right - sum(1 for e in g if e["right"])))
    L.append("")
    L.append("  POOLED 66-pair board (%d raw calls, %d wrong):"
             % (len(pr_called), sum(1 for e in pr_called if not e["right"])))
    L.append("  %-34s %8s %7s %14s" % ("rule", "called", "wrong", "correct lost"))
    pbase = sum(1 for e in pr_called if e["right"])
    L.append("  %-34s %8d %7d %14d" % ("raw certificate", len(pr_called),
                                       sum(1 for e in pr_called if not e["right"]), 0))
    L.append("  %-34s %8d %7d %14d" % ("budget", len(pb_called), sum(1 for e in pb_called if not e["right"]),
                                       pbase - sum(1 for e in pb_called if e["right"])))
    for t in (0.70, 0.75, 0.80, 0.85, 0.90):
        g = [e for e in pr_called if e["agree"] < t]
        L.append("  %-34s %8d %7d %14d" % ("agreement gate A < %.2f" % t, len(g),
                                           sum(1 for e in g if not e["right"]),
                                           pbase - sum(1 for e in g if e["right"])))
    L.append("")
    L.append("  READ: the widener earns its keep only if it removes the same errors for FEWER correct calls")
    L.append("  than the best gate. If a one-line gate matches it, the two fitted parameters are not paying")
    L.append("  for themselves and the honest product is the gate plus the diagnosis.")

    txt = "\n".join(L)
    print(txt)
    out_path = OUT if edge_set == "filtered" else OUT_UNFILTERED
    open(out_path, "w", encoding="utf-8").write(txt + "\n")
    sys.stderr.write("[SYSTEMATIC-BUDGET] edge set %s -> %s\n" % (sel_name, out_path))


if __name__ == "__main__":
    ARGS = parse_args()                       # fail-closed BEFORE any DB is opened
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main(ARGS.edges)
