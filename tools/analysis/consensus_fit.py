"""CONSENSUS-FIT — correctness or consensus? the coefficients (registered 2026-09-14, ZERO calls)

  python tools/analysis/consensus_fit.py

(A) MATCH LEVEL, where the power is: a weighted logistic regression of the verdict on two signed contrasts,
    KEY (which model the answer key favours) and REF (which model the judge's reference agrees with), fitted on
    ARENA-13 arm A (ensemble reference) and on the x12 MAIN verdicts (the deployed grok reference).
(B) MODEL LEVEL, for the interpretable coefficient: the 13-model board's BT theta on standardised key accuracy
    and standardised ensemble agreement, with a permutation test and leave-one-model-out stability, n = 13.
"""
import os, sys, math, json, random, sqlite3
import numpy as np
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_p8 as p8
import stack_judge as sj
import judge_free_tests as jf
import arena13 as a13

NEW = a13.NEW; ENS = a13.ENS
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "consensusfit_outcome.txt")


def logistic(X, y, w):
    """IRLS. Returns beta, standard errors."""
    X = np.asarray(X, float); y = np.asarray(y, float); w = np.asarray(w, float)
    b = np.zeros(X.shape[1])
    for _ in range(60):
        eta = X @ b; mu = 1.0 / (1.0 + np.exp(-np.clip(eta, -30, 30)))
        W = w * mu * (1 - mu) + 1e-12
        z = eta + (y - mu) / np.clip(mu * (1 - mu), 1e-9, None)
        A = X.T @ (X * W[:, None]); rhs = X.T @ (W * z)
        nb = np.linalg.solve(A + 1e-10 * np.eye(X.shape[1]), rhs)
        if np.max(np.abs(nb - b)) < 1e-10: b = nb; break
        b = nb
    eta = X @ b; mu = 1.0 / (1.0 + np.exp(-np.clip(eta, -30, 30)))
    W = w * mu * (1 - mu) + 1e-12
    cov = np.linalg.inv(X.T @ (X * W[:, None]) + 1e-10 * np.eye(X.shape[1]))
    return b, np.sqrt(np.diag(cov))


def sign_contrast(fa, fb):
    if fa and not fb: return 1.0
    if fb and not fa: return -1.0
    return 0.0


def fit_matches(rows, label, L):
    """rows: (key_contrast, ref_contrast, winner in {A,B,TIE})."""
    X = []; y = []; w = []
    for k, r, win in rows:
        if win == "TIE": X += [[1.0, k, r], [1.0, k, r]]; y += [1.0, 0.0]; w += [0.5, 0.5]
        else: X.append([1.0, k, r]); y.append(1.0 if win == "A" else 0.0); w.append(1.0)
    b, se = logistic(X, y, w)
    L.append("  %s (n=%d matches, %d ties)" % (label, len(rows), sum(1 for r in rows if r[2] == "TIE")))
    for nm, i in (("intercept", 0), ("KEY  (the answer key favours this model)", 1), ("REF  (the reference agrees with this model)", 2)):
        z = b[i] / se[i] if se[i] else float("nan")
        L.append("      %-44s %+.3f +- %.3f | z=%+6.1f | odds x%.2f" % (nm, b[i], se[i], z, math.exp(b[i])))
    if abs(b[1]) > 1e-9:
        L.append("      REF / KEY ratio %.2f -> %s" % (b[2] / b[1], "the reference pulls HARDER than correctness" if b[2] > b[1] else "correctness pulls harder"))
    return b, se


def main():
    L = []
    pool, P, K, OPT, cot, route, anchor_of = a13.setup()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)

    # ── (A1) ARENA-13 arm A: ensemble reference, first model is always the new contestant ──────────────
    con = a13.open_cache()
    sch = {m: (q, opp) for m, q, opp in con.execute("SELECT mid, qid, opponent FROM schedule")}
    rows1 = []; acc_split = defaultdict(lambda: [0, 0])
    for m, arm, win, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if arm != "ensemble" or inv: continue
        q, opp = sch[m]
        e = a13.ensemble_ref(q, P, OPT, {opp, NEW})
        if e is None: continue
        na, oa = cot[q][0], P[q].get(opp, "")
        kc = sign_contrast(cot[q][1] == 1, K[q].get(opp, 0) == 1)
        rc = sign_contrast(e[0] == na, e[0] == oa)
        wl = "A" if win == NEW else ("B" if win == opp else "TIE")
        rows1.append((kc, rc, wl))
        if kc != 0:                                        # readout (2)
            agree = (kc > 0 and rc > 0) or (kc < 0 and rc < 0)
            correct = (wl == "A" and kc > 0) or (wl == "B" and kc < 0)
            cell = "reference agrees with the KEY-CORRECT model" if agree else ("reference agrees with the WRONG model" if rc != 0 else "reference agrees with neither")
            acc_split[cell][0] += 1; acc_split[cell][1] += int(correct)

    L.append("=== CONSENSUS-FIT: how much of a model's standing is correctness, and how much is agreeing with the field ===")
    L.append("")
    L.append("(1) MATCH-LEVEL logistic regression of the verdict on two signed contrasts")
    b1, _ = fit_matches(rows1, "ARENA-13 arm A - ENSEMBLE reference", L)

    # ── (A2) x12 MAIN, the deployed grok reference ────────────────────────────────────────────────────
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows2 = []
    for a, bmod, qid, refl, win, inv in sj.open_cache().execute("SELECT model_a, model_b, qid, ref_letter, winner, invalid FROM verdicts"):
        if inv or qid is None: continue
        pa, pb = P.get(qid, {}).get(a), P.get(qid, {}).get(bmod)
        if pa is None or pb is None: continue
        kc = sign_contrast(K[qid].get(a, 0) == 1, K[qid].get(bmod, 0) == 1)
        rl = (refl or "").strip().upper()[:1]
        rc = sign_contrast(rl == pa, rl == pb) if rl else 0.0
        wl = "A" if win == a else ("B" if win == bmod else "TIE")
        rows2.append((kc, rc, wl))
        if kc != 0:
            agree = (kc > 0 and rc > 0) or (kc < 0 and rc < 0)
            correct = (wl == "A" and kc > 0) or (wl == "B" and kc < 0)
            cell = "reference agrees with the KEY-CORRECT model" if agree else ("reference agrees with the WRONG model" if rc != 0 else "reference agrees with neither")
            acc_split[cell][0] += 1; acc_split[cell][1] += int(correct)
    L.append("")
    b2, _ = fit_matches(rows2, "x12 MAIN - the DEPLOYED grok reference", L)

    L.append("")
    L.append("(2) judge accuracy on key-decidable matches, split by what the reference agrees with (both datasets pooled)")
    for cell, (n, c) in sorted(acc_split.items(), key=lambda kv: -kv[1][0]):
        L.append("      %-46s n=%5d | accuracy %.3f" % (cell, n, c / max(1, n)))

    # ── (B) MODEL LEVEL ───────────────────────────────────────────────────────────────────────────────
    models = sorted(set(p8.ARENA12) | {NEW})
    old = [r for r in sj.open_cache().execute("SELECT model_a, model_b, winner, invalid FROM verdicts") if not r[3]]
    brows = [(a, b_, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b_, w, _ in old]
    for m, arm, win, inv in a13.open_cache().execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if arm != "ensemble" or inv: continue
        q, opp = sch[m]
        brows.append((NEW, opp, 0.5 if win == "TIE" else (1.0 if win == NEW else 0.0), 1.0))
    th = jf.board_from(brows, models)
    acck, _ = jf.gt_and_lengths(set(p8.ARENA12))
    acck[NEW] = sum(cot[q][1] for q in cot if q in pool) / max(1, sum(1 for q in cot if q in pool))

    # the new contestant is not in eval_results: its answers are the regenerated CoT run
    def answer(q, m):
        return (cot[q][0] if q in cot else None) if m == NEW else P.get(q, {}).get(m)

    agree = {}
    for m in models:
        n = ok = 0
        pm = {q: answer(q, m) for q in pool}
        for q in pool:
            a_ = pm.get(q)
            if not a_: continue
            votes = Counter(P[q][x] for x in ENS if x != m and P[q].get(x))
            if not votes: continue
            top = votes.most_common()
            if len(top) > 1 and top[0][1] == top[1][1]: continue
            n += 1; ok += int(a_ == top[0][0])
        agree[m] = ok / max(1, n)

    z = lambda v: (np.array(v) - np.mean(v)) / (np.std(v, ddof=1) or 1.0)
    Y = np.array([th[m] for m in models]); A = z([acck[m] for m in models]); G = z([agree[m] for m in models])
    Xm = np.column_stack([np.ones(len(models)), A, G])
    beta, *_ = np.linalg.lstsq(Xm, Y, rcond=None)
    resid = Y - Xm @ beta; dof = len(models) - 3
    s2 = float(resid @ resid) / dof
    cov = s2 * np.linalg.inv(Xm.T @ Xm); sem = np.sqrt(np.diag(cov))
    r2 = 1 - float(resid @ resid) / float(((Y - Y.mean()) ** 2).sum())
    L.append("")
    L.append("(3) MODEL-LEVEL fit, n=%d models: BT theta ~ standardised key accuracy + standardised ensemble agreement" % len(models))
    L.append("      key accuracy        %+.3f +- %.3f  (t=%+.2f)" % (beta[1], sem[1], beta[1] / sem[1]))
    L.append("      ensemble agreement  %+.3f +- %.3f  (t=%+.2f)" % (beta[2], sem[2], beta[2] / sem[2]))
    L.append("      R-squared %.3f | simple correlations: theta~accuracy %.3f, theta~agreement %.3f, accuracy~agreement %.3f"
             % (r2, np.corrcoef(Y, A)[0, 1], np.corrcoef(Y, G)[0, 1], np.corrcoef(A, G)[0, 1]))
    rng = np.random.default_rng(42); cnt = np.zeros(3)
    for _ in range(10000):
        yp = rng.permutation(Y)
        bp, *_ = np.linalg.lstsq(Xm, yp, rcond=None)
        cnt += np.abs(bp) >= np.abs(beta)
    L.append("      permutation p (10,000 shuffles): key accuracy %.4f | ensemble agreement %.4f" % (cnt[1] / 10000, cnt[2] / 10000))
    signs = []
    for i, m in enumerate(models):
        keep = [j for j in range(len(models)) if j != i]
        bl, *_ = np.linalg.lstsq(Xm[keep], Y[keep], rcond=None)
        signs.append((m, bl[2]))
    pos = sum(1 for _, v in signs if v > 0)
    L.append("      leave-one-model-out: the agreement coefficient stays positive in %d of %d refits (range %+.3f to %+.3f)"
             % (pos, len(signs), min(v for _, v in signs), max(v for _, v in signs)))
    rc_ = float(np.corrcoef(A, G)[0, 1])
    L.append("      COLLINEARITY: accuracy and agreement correlate at %.3f across the roster (VIF %.1f), so at n=13 the two"
             % (rc_, 1.0 / max(1e-9, 1 - rc_ ** 2)))
    L.append("      model-level coefficients are NOT separately identified - which is why the permutation test, whose null")
    L.append("      distribution is correspondingly wide, cannot reject either of them. Better models agree with the field")
    L.append("      more, ACROSS the roster; the two come apart only WITHIN a question, which is what the match-level fits use.")
    L.append("      CAVEAT: n=13 models. The match-level fits above carry the statistical weight; this one carries the units.")

    L.append("")
    L.append("      model                              theta    key acc   agrees with the field")
    for m in sorted(models, key=lambda m: -th[m])[:8]:
        L.append("      %-34s %+.3f    %.3f     %.3f" % (m, th[m], acck[m], agree[m]))

    # (4) counterfactual: equalise consensus agreement between the new contestant and gemini
    gem = "gemini-3.1-pro_5-shots"
    if gem in th and NEW in th:
        i_new, i_gem = models.index(NEW), models.index(gem)
        d = beta[2] * (G[i_new] - G[i_gem])
        L.append("")
        L.append("(4) what the consensus coefficient accounts for at the top of the board")
        L.append("      %s leads %s by %+.3f theta while scoring %.3f against %.3f on the key."
                 % (NEW, gem, th[NEW] - th[gem], acck[NEW], acck[gem]))
        L.append("      its consensus advantage is %.3f - %.3f = %+.3f agreement, worth %+.3f theta at the fitted coefficient,"
                 % (agree[NEW], agree[gem], agree[NEW] - agree[gem], d))
        L.append("      i.e. %.0f%% of the gap. Equalising agreement alone %s the order."
                 % (100 * d / (th[NEW] - th[gem]) if th[NEW] != th[gem] else 0,
                    "REVERSES" if d > (th[NEW] - th[gem]) else "does not reverse"))
    # (5) DESCRIPTIVE, not registered: what the arm A intercept is standing in for
    n00 = [r for r in rows1 if r[0] == 0 and r[1] == 0]
    w00 = sum(1 for r in n00 if r[2] == "A") / max(1, len(n00))
    L.append("")
    L.append("(5) DESCRIPTIVE, not registered - what the arm A intercept is standing in for")
    L.append("      On the %d arm A matches where NEITHER the key nor the reference favours a side, the new contestant" % len(n00))
    L.append("      still wins %.3f (the fitted intercept, which is not saturated, puts it at %.3f). Whatever that is, it is"
             % (w00, 1 / (1 + math.exp(-b1[0]))))
    L.append("      not consensus alignment: it is what makes the judge prefer that model with no evidence either way.")
    L.append("      THREE CANDIDATES, and this fit cannot separate them:")
    L.append("        - genuine quality the key does not capture;")
    L.append("        - style: its traces come from a different generation run than the twelve contestants;")
    L.append("        - POSITION: arm A was single order and the new contestant was ALWAYS Model A, so nothing cancelled")
    L.append("          the position effect. FLIP-PROV measured 13.9% position sensitivity and ORDER-1 showed the board")
    L.append("          itself depends on which single order is kept (rho 0.958 against 0.986).")
    L.append("      Separating them costs one reversed-order pass over a sample of arm A. Until that is bought, the")
    L.append("      ARENA-13 (1) failure should be attributed to the single-order design as readily as to the reference.")
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    main()
