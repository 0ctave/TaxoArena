"""LOW-AGREEMENT — what predicts the errors the fitted budget is blind to? (registered 2026-09-14, zero calls)

  python tools/analysis/low_agreement.py

SYSTEMATIC-BUDGET leaves three wrong calls standing out of fold and all three are LOW agreement (0.475, 0.476,
0.605), while tau grows with agreement and so barely touches them. The two Law survivors carry the most solidly
established key labels of the eight (exact McNemar p=0.0018, 0.0015), so they are real inversions and not label
noise. A budget that handles the high-agreement channel and is blind to the rest should not be called a
systematic-error budget without characterising the blind spot.

Every predictor here is available WITHOUT the answer key at inference. The key gap is carried only as a sanity
check and is labelled unavailable, exactly as SYSTEMATIC-SIGNAL did.
"""
import os, sys, math, random, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.stats import norm
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import consensus_fit as cf
import pool_guard
import systematic_budget as sb

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "low_agreement.txt")
B = 300
THRESH = 0.975
GAP = 0.02
B0, B1 = -3.2326, 3.3133


def enrich():
    """The 891 edges plus every key-free predictor the blind spot might live in."""
    models = sorted(p8.ARENA12)
    acc, LEN = jf.gt_and_lengths(set(models))
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict); P = defaultdict(dict)
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in models:
            K[q][m] = int(c or 0); P[q][m] = (pr or "").strip().upper()[:1]
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(list)
    for a, b, q, w, _ in rows:
        if q in route:
            by[anchor_of(route[q])].append((a, b, q, w))

    rng = random.Random(42)
    edges = []; anchor_qs = {}
    for anc in sorted(by):
        rs = by[anc]
        if len(rs) < 200:
            continue
        qs = sorted({q for _, _, q, _ in rs}); anchor_qs[anc] = qs
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
        # per-pair tie rate from the verdicts actually judged in this anchor
        ties = defaultdict(lambda: [0, 0])
        for a, b, q, w in rs:
            k = tuple(sorted((a, b)))
            ties[k][1] += 1
            if w == "TIE":
                ties[k][0] += 1
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if a not in la or b not in la or abs(la[a] - la[b]) < GAP:
                    continue
                d = np.array([dr[a] - dr[b] for dr in draws])
                p = float((d > 0).mean())
                both = [q for q in qs if P[q].get(a) and P[q].get(b)]
                if not both:
                    continue
                agree = sum(1 for q in both if P[q][a] == P[q][b]) / len(both)
                # the model the ARENA asserts is stronger, and how much LONGER it writes than the other.
                # Positive means the arena's pick is the more verbose model - the campaign's best-measured
                # judge bias (+0.39 per 1k characters) and exactly what a question bootstrap cannot see.
                win, lose = (a, b) if p > 0.5 else (b, a)
                dl = [LEN.get((q, win), 0) - LEN.get((q, lose), 0) for q in both]
                lenadv = sum(dl) / len(dl) if dl else 0.0
                absl = sum(abs(x) for x in dl) / len(dl) if dl else 0.0
                # KEY-anchored signed length difference: mean(len[key-better] - len[key-worse]). The review of
                # 2026-09-15 showed lenadv == +/- lenkey with the sign being the LABEL itself (wrong edge <=>
                # arena pick != key pick), so lenadv cannot be a predictor of the label. lenkey can.
                kb, kw = (a, b) if la[a] > la[b] else (b, a)
                dk = [LEN.get((q, kb), 0) - LEN.get((q, kw), 0) for q in both]
                lenkey = sum(dk) / len(dk) if dk else 0.0
                tk = ties[tuple(sorted((a, b)))]
                edges.append(dict(anchor=anc, a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                                  right=((p > 0.5) == (la[a] > la[b])), agree=agree, gap=abs(la[a] - la[b]),
                                  n=len(both), craw=max(p, 1 - p), absm=abs(float(d.mean())),
                                  tie=tk[0] / tk[1] if tk[1] else 0.0, lenadv=lenadv / 1000.0, abslen=absl / 1000.0,
                                  lenkey=lenkey / 1000.0))
    return models, edges, anchor_qs, K


def boot_diff(wrong, right, key, rng, reps=2000):
    if not wrong or not right:
        return float("nan"), float("nan"), float("nan")
    mw = sum(e[key] for e in wrong) / len(wrong); mr = sum(e[key] for e in right) / len(right)
    ds = []
    for _ in range(reps):
        bw = [wrong[rng.randrange(len(wrong))][key] for _ in wrong]
        br = [right[rng.randrange(len(right))][key] for _ in right]
        ds.append(sum(bw) / len(bw) - sum(br) / len(br))
    ds.sort()
    return mw, mr, (ds[int(0.025 * reps)], ds[int(0.975 * reps)])


def main():
    L = []
    rng = random.Random(7)
    models, edges, anchor_qs, K = enrich()
    est = lambda es: len(sb.established([e for e in es if not e["right"]], K, anchor_qs))
    med = sorted(e["agree"] for e in edges)[len(edges) // 2]
    low = [e for e in edges if e["agree"] < med]
    high = [e for e in edges if e["agree"] >= med]

    L.append("=== LOW-AGREEMENT: what predicts the errors the fitted budget cannot see? (corrected 2026-09-15) ===")
    L.append("  %d edges | median answer agreement %.3f | low half %d, high half %d"
             % (len(edges), med, len(low), len(high)))
    lw = sum(1 for e in low if not e["right"]); hw = sum(1 for e in high if not e["right"])
    L.append("  wrong-direction edges: %d in the LOW half (%d McNemar-established), %d in the HIGH half (%d established)"
             % (lw, est(low), hw, est(high)))
    L.append("  wrong rate by agreement band over ALL %d edges, all(established):" % len(edges))
    for lo, hi in ((0, .35), (.35, .45), (.45, .55), (.55, .65), (.65, .80), (.80, 1.01)):
        band = [e for e in edges if lo <= e["agree"] < hi]
        bw = [e for e in band if not e["right"]]
        L.append("    %.2f-%.2f: %2d(%2d) wrong of %3d  (%.1f%% / %.1f%%)"
                 % (lo, hi, len(bw), est(band), len(band), 100.0 * len(bw) / max(1, len(band)), 100.0 * est(band) / max(1, len(band))))
    L.append("")
    L.append("  (3) THE REGISTERED POWER CHECK FIRST, because it decides how the rest may be read.")
    L.append("      I predicted roughly 20 wrong edges in the low half; there are %d." % lw)
    if lw < 12:
        L.append("      That is too few to support any claim and every result below is DESCRIPTIVE.")
    else:
        L.append("      Enough to look at, not enough to be confident; differences below are reported with CIs.")

    L.append("")
    L.append("=== (1) PRIMARY: predictors of a wrong direction WITHIN the low-agreement half ===")
    L.append("  every predictor is computable without the answer key at inference, except the last")
    L.append("  %-30s %8s %8s %9s %22s" % ("predictor", "wrong", "right", "diff", "95% CI"))
    lwr = [e for e in low if not e["right"]]; lrt = [e for e in low if e["right"]]
    keys = (("bootstrap SD s", "s"), ("|mean theta gap|", "absm"), ("raw confidence", "craw"),
            ("distinct questions", "n"), ("tie rate in the cell", "tie"),
            ("answer agreement", "agree"),
            ("|length difference| (k chars)  [REGISTERED predictor]", "abslen"),
            ("LENGTH ADV of arena pick [SUBSTITUTED, C-7: sign IS the label]", "lenadv"),
            ("LENGTH ADV of the KEY's pick (k chars)  [the honest signed one]", "lenkey"),
            ("key gap  [NOT available at inference]", "gap"))
    hits = []
    for nm, k in keys:
        mw, mr, ci = boot_diff(lwr, lrt, k, rng)
        if mw != mw:
            continue
        excl = ci[0] > 0 or ci[1] < 0
        if excl and k not in ("gap", "lenadv"):      # lenadv is excluded: its sign is the outcome by construction
            hits.append((nm, k))
        L.append("  %-62s %8.3f %8.3f %+9.3f  [%+.3f, %+.3f]%s"
                 % (nm[:62], mw, mr, mw - mr, ci[0], ci[1], "  <- excludes zero" if excl else ""))
    L.append("  NOTE (review 2026-09-15): the arena-signed length advantage equals +lenkey on right edges and -lenkey on")
    L.append("  wrong ones, so its 'effect' is the label's sign and it is NOT a predictor; the registered predictor is the")
    L.append("  absolute difference, and the only honest signed one is anchored on the KEY's pick.")

    L.append("")
    L.append("  surviving candidates before conditioning: %s" % (", ".join(n for n, _ in hits) if hits else "NONE"))

    # logistic with agreement already in it
    if hits:
        L.append("")
        L.append("  LOGISTIC over the low half, each candidate against agreement (does it survive?):")
        y = np.array([0.0 if e["right"] else 1.0 for e in low])
        z = lambda v: (np.array(v) - np.mean(v)) / (np.std(v, ddof=1) or 1.0)
        for nm, k in hits:
            X = np.column_stack([np.ones(len(low)), z([e["agree"] for e in low]), z([e[k] for e in low])])
            try:
                bb, se = cf.logistic(X, y, np.ones(len(low)))
                L.append("      %-34s coef %+.3f +- %.3f | z=%+5.1f  (agreement %+.3f)"
                         % (nm[:34], bb[2], se[2], bb[2] / se[2] if se[2] else float("nan"), bb[1]))
            except Exception as e:
                L.append("      %-34s logistic failed: %s" % (nm[:34], str(e)[:50]))
    else:
        L.append("")
        L.append("  -> NO key-free predictor separates the wrong from the right inside the low-agreement half.")
        L.append("     With %d wrong edges there this is UNDERPOWERED as registered, not evidence that no" % lw)
        L.append("     second channel exists. The honest statement for RESOLVE is that the budget covers the")
        L.append("     high-agreement channel and the low-agreement channel is UNCHARACTERISED.")

    # ---- (2) what a second channel would buy ----
    L.append("")
    L.append("=== (2) WHAT A SECOND CHANNEL WOULD BUY, on the wrong calls the budget keeps in sample ===")
    kept = [e for e in edges if sb.cbud(e, B0, B1) >= THRESH]
    keptw = [e for e in kept if not e["right"]]
    L.append("  the shipped budget calls %d edges in sample and keeps %d wrong (%d McNemar-established); percentiles"
             % (len(kept), len(keptw), est(kept)))
    L.append("  below are over the %d CALLED edges, not the 891 (the two populations give different quintile cuts):" % len(kept))
    for e in sorted(keptw, key=lambda e: -e["agree"]):
        L.append("    %-14s %-38s A=%.3f  len-adv %+0.3fk  tie %.3f  c=%.4f"
                 % (e["anchor"][:14], ("%s vs %s" % (e["a"][:17], e["b"][:17])), e["agree"],
                    e["lenadv"], e["tie"], sb.cbud(e, B0, B1)))
    if hits:
        nm, k = hits[0]
        vals = sorted(e[k] for e in kept)
        L.append("")
        L.append("  A second channel on '%s' would have to flag these three without flagging" % nm)
        L.append("  the %d correct calls. Their values of that predictor:" % (len(kept) - len(keptw)))
        for e in keptw:
            pct = sum(1 for v in vals if v <= e[k]) / len(vals)
            L.append("    %-38s %s = %+.3f  (percentile %.0f%% among called edges)"
                     % (("%s vs %s" % (e["a"][:17], e["b"][:17])), k, e[k], 100 * pct))
        L.append("  READ: if the three sit in the tail of that predictor, a second channel is worth adding; if")
        L.append("  they sit mid-distribution, it would cost more correct calls than it saves and must not be.")

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
