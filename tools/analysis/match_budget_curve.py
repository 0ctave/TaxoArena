"""M2 — match-budget curve (docs/m_series_registration.md; registered before running).

  python tools/analysis/match_budget_curve.py
"""
import os, sys, csv, random, sqlite3
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import judge_free_tests as jf

R2_DB = os.path.join(ROOT, "experiment_results", "x12_profile", "ratings_x12p.db")
J1_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_grok_4_1_fast_reasoning.db")
DRAWS = 200
BUDGETS = [250, 500, 1000, 2000, 4000]


def rows_from_db(db):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    return [dict(a=a, b=b, w=("TIE" if t else w), q=int(q)) for a, b, w, t, q in
            con.execute("SELECT model_a, model_b, winner, is_tie, eval_question_id FROM match_history WHERE condition='MAIN'")]


def fit_w(rows, models, weights=None):
    agg = defaultdict(lambda: [0.0, 0.0])
    for i, r in enumerate(rows):
        a, b = r["a"], r["b"]
        wa = 0.5 if r["w"] == "TIE" else (1.0 if r["w"] == a else 0.0)
        wt = 1.0 if weights is None else weights[i]
        if a > b:
            a, b, wa = b, a, 1.0 - wa
        rec = agg[(a, b)]
        rec[0] += wa * wt; rec[1] += wt
    return rj.mm_fit({k: tuple(v) for k, v in agg.items()}, models)


def curve(name, rows, models, acc, gt_order, weights=None, budgets=BUDGETS, seed=7):
    rng = random.Random(seed)
    n = len(rows)
    print("  %s (n=%d)%s" % (name, n, " confidence-weighted" if weights is not None else ""))
    print("     %7s | %8s %8s %8s | %10s %6s" % ("budget", "rho_med", "rho_p05", "rho>=.93", "top4viol_md", "gemini1st"))
    for bgt in [b for b in budgets if b < n] + [n]:
        rhos, viol, g1 = [], [], 0
        for _ in range(DRAWS if bgt < n else 1):
            idx = rng.sample(range(n), bgt) if bgt < n else list(range(n))
            sub = [rows[i] for i in idx]
            w = [weights[i] for i in idx] if weights is not None else None
            th = fit_w(sub, models, w)
            rhos.append(jf.rho(th, acc, models))
            o, pv, _ = jf.violations(th, gt_order)
            viol.append(pv); g1 += (o[0] == gt_order[0])
        rhos.sort()
        k = len(rhos)
        print("     %7d | %8.3f %8.3f %7.0f%% | %10.1f %5.0f%%" % (bgt, rhos[k // 2], rhos[int(0.05 * k)], 100 * sum(r >= 0.93 for r in rhos) / k, float(np.median(viol)), 100 * g1 / k))
    return None


def main():
    x12 = rows_from_db(rj.X12_DB)
    r2 = rows_from_db(R2_DB)
    models = sorted({m for r in r2 for m in (r["a"], r["b"])})
    acc, _ = jf.gt_and_lengths(set(models))
    gt_order = sorted(jf.TOP4, key=lambda m: -acc[m])
    print("M2 match-budget curve | 12 models | GT top-4 %s | %d draws per budget" % (" > ".join(gt_order), DRAWS))
    curve("x12 Mistral", x12, models, acc, gt_order)
    curve("R2 Mistral (all)", r2, models, acc, gt_order)
    # confidence-weighted on the R2 live subset
    conf = {}
    with open(jf.R2, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r["Rationale"].startswith("Reconstructed"):
                conf[(int(r["QueryId"]), r["ModelA"], r["ModelB"])] = float(r["Confidence"])
    live = [r for r in r2 if (r["q"], r["a"], r["b"]) in conf]
    curve("R2 live", live, models, acc, gt_order)
    curve("R2 live", live, models, acc, gt_order, weights=[max(0.05, conf[(r["q"], r["a"], r["b"])]) for r in live])
    if os.path.exists(J1_DB):
        c = sqlite3.connect("file:%s?mode=ro" % J1_DB, uri=True)
        j1 = [dict(a=a, b=b, w=w, q=q) for a, b, w, q, inv in c.execute("SELECT model_a, model_b, r1_winner, qid, r1_invalid FROM verdicts") if not inv]
        curve("R3 sample, grok-reasoning", j1, models, acc, gt_order, budgets=[250, 500, 1000])
        mist = [dict(a=a, b=b, w=w, q=q) for a, b, w, q in c.execute("SELECT model_a, model_b, mistral_winner, qid FROM verdicts")]
        curve("R3 sample, Mistral (same matches)", mist, models, acc, gt_order, budgets=[250, 500, 1000])
    print("REGISTERED CLAIM: rho >= 0.93 in >= 95%% of draws at 2,000 matches for the Mistral runs (see rho>=.93 column at budget 2000).")


if __name__ == "__main__":
    main()
