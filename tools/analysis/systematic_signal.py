"""SYSTEMATIC-SIGNAL — can a free signal predict where the bootstrap is confidently wrong? (registered 2026-09-14)

  python tools/analysis/systematic_signal.py

TIER-HONEST: the arena separates within-tier pairs 2 of 2 at 95% confidence, one of them in the wrong direction,
because a bootstrap sees sampling noise and never a bias present in every sample. RESOLVE proposes widening each
interval by a measured systematic budget and names three free candidate signals. This tests them on the 891
(anchor, model-pair) edges: does answer-agreement, or the reference's accuracy in that anchor, separate the
wrong-direction calls from the right ones?
"""
import os, sys, math, random, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import rejudge_grok as rj
import rejudge_reference as rref
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import consensus_fit as cf
import pool_guard

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "systematic_signal.txt")
B = 300
THRESH = 0.975


def main():
    L = []
    models = sorted(p8.ARENA12)
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict); P = defaultdict(dict)
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in p8.ARENA12: K[q][m] = int(c or 0); P[q][m] = (pr or "").strip().upper()[:1]
    rref.set_reference("grok-reasoning")
    refc = {q: bool(v[2]) for q, v in rref.references().items()}
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(list)
    for a, b, q, w, _ in rows:
        if q in route: by[anchor_of(route[q])].append((a, b, q, w))

    rng = random.Random(42)
    edges = []
    for anc in sorted(by):
        rs = by[anc]
        if len(rs) < 200: continue
        qs = sorted({q for _, _, q, _ in rs})
        byq = defaultdict(list)
        for r in rs: byq[r[2]].append(r)
        draws = []
        for _ in range(B):
            pick = [qs[rng.randrange(len(qs))] for _ in qs]
            sub = [r for q in pick for r in byq[q]]
            draws.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in sub], models))
        la = {}
        for m in models:
            v = [K[q].get(m) for q in qs if K[q].get(m) is not None]
            if v: la[m] = sum(v) / len(v)
        racc = [refc[q] for q in qs if q in refc]
        ra = sum(racc) / max(1, len(racc))
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if a not in la or b not in la or abs(la[a] - la[b]) < 0.02: continue
                p = sum(1 for d in draws if d[a] > d[b]) / B
                both = [q for q in qs if P[q].get(a) and P[q].get(b)]
                if not both: continue
                agree = sum(1 for q in both if P[q][a] == P[q][b]) / len(both)
                edges.append(dict(anchor=anc, a=a, b=b, p=p, right=((p > 0.5) == (la[a] > la[b])),
                                  agree=agree, refacc=ra, gap=abs(la[a] - la[b]), n=len(both)))
    L.append("=== SYSTEMATIC-SIGNAL: does a free signal predict the bootstrap's confident errors? ===")
    L.append("  %d edges over %d anchors | called at the %.3f threshold: %d"
             % (len(edges), len({e['anchor'] for e in edges}), THRESH,
                sum(1 for e in edges if e["p"] >= THRESH or e["p"] <= 1 - THRESH)))

    called = [e for e in edges if e["p"] >= THRESH or e["p"] <= 1 - THRESH]
    wrong = [e for e in called if not e["right"]]
    right = [e for e in called if e["right"]]
    L.append("  of those, %d point the WRONG way and %d the right way" % (len(wrong), len(right)))
    if not wrong:
        L.append("  no wrong calls at this threshold - the primary cannot be computed. Reported as UNDERPOWERED.")
    for name, key, expect in (("answer-agreement", "agree", "HIGHER on wrong edges"),
                              ("reference accuracy in the anchor", "refacc", "LOWER on wrong edges"),
                              ("key gap between the pair", "gap", "LOWER on wrong edges")):
        if not wrong or not right:
            L.append("  %-34s n/a" % name); continue
        mw = sum(e[key] for e in wrong) / len(wrong); mr = sum(e[key] for e in right) / len(right)
        ds = []
        for _ in range(2000):
            bw = [wrong[rng.randrange(len(wrong))][key] for _ in wrong]
            br = [right[rng.randrange(len(right))][key] for _ in right]
            ds.append(sum(bw) / len(bw) - sum(br) / len(br))
        ds.sort()
        lo, hi = ds[50], ds[1949]
        L.append("  %-34s wrong %.3f | right %.3f | diff %+.3f  95%% CI [%+.3f, %+.3f]%s"
                 % (name, mw, mr, mw - mr, lo, hi, "   <- excludes zero" if (lo > 0 or hi < 0) else ""))
        L.append("      expected: %s" % expect)

    # (3) two-predictor logistic on every edge, wrong-direction as the outcome
    L.append("")
    L.append("  (3) LOGISTIC over ALL %d edges: P(wrong direction) on standardised agreement and reference accuracy" % len(edges))
    y = np.array([0.0 if e["right"] else 1.0 for e in edges])
    if 0 < y.sum() < len(y):
        z = lambda v: (np.array(v) - np.mean(v)) / (np.std(v, ddof=1) or 1.0)
        X = np.column_stack([np.ones(len(edges)), z([e["agree"] for e in edges]), z([e["refacc"] for e in edges])])
        b, se = cf.logistic(X, y, np.ones(len(edges)))
        for nm, i in (("intercept", 0), ("answer-agreement", 1), ("reference accuracy", 2)):
            L.append("      %-22s %+.3f +- %.3f | z=%+5.1f" % (nm, b[i], se[i], b[i] / se[i] if se[i] else float("nan")))
        L.append("      (%d wrong of %d edges overall)" % (int(y.sum()), len(y)))

    # (4) operating point
    L.append("")
    L.append("  (4) OPERATING POINT: decline a called edge when the pair's answer-agreement exceeds a threshold")
    L.append("  %10s %10s %12s %14s" % ("agree >=", "declined", "wrong kept", "correct lost"))
    for t in (0.70, 0.75, 0.80, 0.85, 0.90, 1.01):
        dec = [e for e in called if e["agree"] >= t]
        kept_wrong = sum(1 for e in wrong if e["agree"] < t)
        lost_right = sum(1 for e in right if e["agree"] >= t)
        L.append("  %10.2f %10d %12d %14d" % (t, len(dec), kept_wrong, lost_right))
    L.append("  READ: a usable signal removes most wrong calls while losing few correct ones. With only %d wrong"
             % len(wrong))
    L.append("  edges this table is descriptive; it cannot establish an operating point on its own.")

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
