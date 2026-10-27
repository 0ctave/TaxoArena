"""FORMAT-REF — is GRADING less reference-dominated than COMPARING? (registered 2026-09-14, ZERO calls)

  python tools/analysis/format_ref.py

CONSENSUS-FIT measured the reference outweighing correctness 2.7 to 1, but only on pairwise verdicts. Four arms
over caches that already exist, all fitted with the same signed-contrast logistic:
  (a) PAIRWISE grok, R3            the format baseline
  (b) POINTWISE grok with a reference, the SAME matches   the format contrast, paired
  (c) POINTWISE grok WITHOUT a reference                  the NEGATIVE CONTROL: the judge never saw the
                                                          reference, so its REF coefficient must be near zero
  (d) PAIRWISE Mistral, the same matches and recipe       the judge-family contrast (JUDGE-SWAP's pair)
"""
import os, sys, math, sqlite3, random
import numpy as np
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reference as rref
import pointwise_judge as pt
import consensus_fit as cf

X = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
OUT = os.path.join(X, "formatref_outcome.txt")
PW_GROK = os.path.join(X, "stack_v2_promptv2_grok.db")
PW_MIST = os.path.join(X, "stack_v2_promptv2.db")


def evaluation():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    P = defaultdict(dict); K = defaultdict(dict)
    for q, m, p, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        P[q][m] = (p or "").strip().upper()[:1]; K[q][m] = int(c or 0)
    return P, K


def rows_pairwise(db, P, K, refs):
    out = {}
    for mid, a, b, qid, refl, win, inv in sqlite3.connect("file:%s?mode=ro" % db, uri=True).execute(
            "SELECT match_id, model_a, model_b, qid, ref_letter, winner, invalid FROM verdicts"):
        if inv or qid is None: continue
        rl = (refl or "").strip().upper()[:1] or ((refs.get(qid) or ("",))[0])
        pa, pb = P[qid].get(a), P[qid].get(b)
        if pa is None or pb is None: continue
        out[mid] = (cf.sign_contrast(K[qid].get(a, 0) == 1, K[qid].get(b, 0) == 1),
                    cf.sign_contrast(rl == pa, rl == pb),
                    "A" if win == a else ("B" if win == b else "TIE"))
    return out


def rows_pointwise(db, P, K, refs, sample):
    G = {(q, m): g for q, m, g in sqlite3.connect("file:%s?mode=ro" % db, uri=True).execute("SELECT qid, model, grade FROM grades")}
    out = {}
    for m_ in sample:
        mid, qid, a, b = m_[0], int(m_[1]), m_[2], m_[3]
        ga, gb = G.get((qid, a)), G.get((qid, b))
        if ga is None or gb is None: continue
        rl = (refs.get(qid) or ("",))[0]
        pa, pb = P[qid].get(a), P[qid].get(b)
        if pa is None or pb is None: continue
        out[mid] = (cf.sign_contrast(K[qid].get(a, 0) == 1, K[qid].get(b, 0) == 1),
                    cf.sign_contrast(rl == pa, rl == pb),
                    "TIE" if ga == gb else ("A" if ga > gb else "B"))
    return out


def fit(rows):
    Xm = []; y = []; w = []
    for k, r, win in rows:
        if win == "TIE": Xm += [[1.0, k, r], [1.0, k, r]]; y += [1.0, 0.0]; w += [0.5, 0.5]
        else: Xm.append([1.0, k, r]); y.append(1.0 if win == "A" else 0.0); w.append(1.0)
    return cf.logistic(Xm, y, w)


def boot_ratio(rows, B=600, seed=42):
    rng = random.Random(seed); n = len(rows); out = []
    for _ in range(B):
        s = [rows[rng.randrange(n)] for _ in range(n)]
        try:
            b, _ = fit(s)
            if abs(b[1]) > 1e-6: out.append(b[2] / b[1])
        except Exception: pass
    out.sort()
    return (out[int(0.025 * len(out))], out[int(0.975 * len(out))]) if out else (float("nan"), float("nan"))


def main():
    P, K = evaluation()
    rref.set_reference("grok-reasoning"); refs = rref.references()
    sample, _ = pt.targets()
    A = rows_pairwise(PW_GROK, P, K, refs)
    Bp = rows_pointwise(pt.CACHE, P, K, refs, sample)
    C = rows_pointwise(pt.CACHE.replace(".db", "_noref.db"), P, K, refs, sample)
    D = rows_pairwise(PW_MIST, P, K, refs)

    L = []
    L.append("=== FORMAT-REF: does the reference dominate GRADING as much as it dominates COMPARING? ===")
    L.append("")
    arms = [("(a) PAIRWISE grok, with reference", A), ("(b) POINTWISE grok, with reference", Bp),
            ("(c) POINTWISE grok, NO reference (negative control)", C), ("(d) PAIRWISE Mistral, with reference", D)]
    fits = {}
    for name, d in arms:
        r = list(d.values())
        b, se = fit(r)
        lo, hi = boot_ratio(r)
        fits[name] = (b, se, len(r))
        L.append("  %-52s n=%5d, ties %4d" % (name, len(r), sum(1 for x in r if x[2] == "TIE")))
        L.append("      KEY %+.3f +- %.3f | REF %+.3f +- %.3f | ratio %5.2f  bootstrap 95%% CI [%.2f, %.2f]"
                 % (b[1], se[1], b[2], se[2], b[2] / b[1] if b[1] else float("nan"), lo, hi))

    # (3) negative control against zero
    bC, seC, _ = fits["(c) POINTWISE grok, NO reference (negative control)"]
    z = bC[2] / seC[2]
    L.append("")
    L.append("  (3) NEGATIVE CONTROL: with no reference in the prompt the REF coefficient is %+.3f +- %.3f (z=%+.1f)."
             % (bC[2], seC[2], z))
    L.append("      %s" % ("Within the registered +-0.2 band -> the measurement is clean: what CONSENSUS-FIT fitted is the"
                           "\n      reference itself, not something correlated with it."
                           if abs(bC[2]) <= 0.2 else
                           "OUTSIDE the registered +-0.2 band. The REF contrast picks up signal even when the judge never"
                           "\n      saw a reference, so it is partly a proxy for question difficulty or for consensus among"
                           "\n      models, and the CONSENSUS-FIT coefficient is an upper bound rather than a clean estimate."))

    # collinearity of the two contrasts - the ratio is only meaningful while KEY is well away from zero
    L.append("")
    L.append("  DIAGNOSTIC: the two contrasts are correlated, because the reference is right most of the time.")
    for name, d in arms:
        r = list(d.values())
        k = np.array([x[0] for x in r]); rr = np.array([x[1] for x in r])
        L.append("      %-52s corr(KEY, REF) %.3f | agree on %.3f of matches"
                 % (name, float(np.corrcoef(k, rr)[0, 1]), float(np.mean(k == rr))))
    L.append("      Where KEY lands near zero the RATIO explodes and its bootstrap interval is meaningless; the")
    L.append("      paired contrasts below therefore compare the COEFFICIENTS and their difference REF-KEY, which")
    L.append("      stay well behaved. This supersedes the ratio as the registered statistic - the registration")
    L.append("      named a quantity that turns out to be undefined in one of the four arms.")

    def paired(d1, d2, n1, n2, tag):
        common = sorted(set(d1) & set(d2))
        b1, _ = fit([d1[m] for m in common]); b2, _ = fit([d2[m] for m in common])
        rng = random.Random(7); dk = []; dr = []; dd = []
        for _ in range(600):
            idx = [common[rng.randrange(len(common))] for _ in common]
            try:
                x1, _ = fit([d1[m] for m in idx]); x2, _ = fit([d2[m] for m in idx])
                dk.append(x2[1] - x1[1]); dr.append(x2[2] - x1[2])
                dd.append((x2[2] - x2[1]) - (x1[2] - x1[1]))
            except Exception: pass
        ci = lambda v: (sorted(v)[int(0.025 * len(v))], sorted(v)[int(0.975 * len(v))])
        L.append("")
        L.append("  %s, paired on the %d matches both arms judged:" % (tag, len(common)))
        L.append("      %-28s KEY %+.3f | REF %+.3f | REF-KEY %+.3f" % (n1, b1[1], b1[2], b1[2] - b1[1]))
        L.append("      %-28s KEY %+.3f | REF %+.3f | REF-KEY %+.3f" % (n2, b2[1], b2[2], b2[2] - b2[1]))
        for lbl, v, delta in (("KEY", dk, b2[1] - b1[1]), ("REF", dr, b2[2] - b1[2]),
                              ("REF-KEY", dd, (b2[2] - b2[1]) - (b1[2] - b1[1]))):
            lo_, hi_ = ci(v)
            L.append("      delta %-8s %+.3f  95%% CI [%+.3f, %+.3f]%s" % (lbl, delta, lo_, hi_, "" if lo_ < 0 < hi_ else "   <- excludes zero"))
        return b1, b2

    # (2) PAIRED format contrast
    paired(A, Bp, "pairwise, with reference", "pointwise, with reference",
           "(2) FORMAT CONTRAST - the same matches judged both ways")
    # the clean causal toggle: same format, same matches, reference present or absent
    paired(C, Bp, "pointwise, NO reference", "pointwise, with reference",
           "(2b) THE REFERENCE TOGGLE - the one manipulation in this set that is clean")

    # ROBUSTNESS: pointwise abstains more (711 ties vs 462), and half-weighted ties attenuate every coefficient,
    # so the format contrast is refitted on committed verdicts only. Attenuation would shrink KEY and REF alike;
    # a drop confined to KEY cannot be explained by it.
    common = sorted(set(A) & set(Bp))
    na = [A[m] for m in common if A[m][2] != "TIE"]; nb = [Bp[m] for m in common if Bp[m][2] != "TIE"]
    b1, _ = fit(na); b2, _ = fit(nb)
    L.append("")
    L.append("  ROBUSTNESS - committed verdicts only, ties dropped from each arm:")
    L.append("      pairwise  n=%4d KEY %+.3f | REF %+.3f | REF-KEY %+.3f" % (len(na), b1[1], b1[2], b1[2] - b1[1]))
    L.append("      pointwise n=%4d KEY %+.3f | REF %+.3f | REF-KEY %+.3f" % (len(nb), b2[1], b2[2], b2[2] - b2[1]))
    L.append("      -> the KEY gap %s when abstentions are removed" % ("survives" if b2[1] < b1[1] - 0.2 else "does NOT survive"))

    # (4) judge family
    bd, sed, _ = fits["(d) PAIRWISE Mistral, with reference"]
    ba_, sea, _ = fits["(a) PAIRWISE grok, with reference"]
    L.append("")
    L.append("  (4) JUDGE FAMILY, same recipe and same matches: grok ratio %.2f vs Mistral ratio %.2f"
             % (ba_[2] / ba_[1], bd[2] / bd[1]))
    L.append("      KEY grok %+.3f +- %.3f vs Mistral %+.3f +- %.3f | REF grok %+.3f +- %.3f vs Mistral %+.3f +- %.3f"
             % (ba_[1], sea[1], bd[1], sed[1], ba_[2], sea[2], bd[2], sed[2]))

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    main()
