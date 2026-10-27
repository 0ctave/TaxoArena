"""Judge v2 program — the FREE re-measurements (docs/judge_v2_program.md B2 and B8), from the caches.

B8 confidence calibration under the new configurations: per-verdict confidence (mean of the two
orders) vs key correctness on key-decidable matches — AUC, ECE (10 bins), and the ≥0.95-gated
top-4 board — for x12 MAIN (v1, no reference), STACK (v1 + reference + anchor rubric) and STACK-v2.
B2 position sensitivity: flip rate by key gap tier and by top-cluster membership for the same three
configurations, plus the second-shown win rate on single-order votes.
Zero calls; descriptive (the registered B8 claim is "confidence stays calibrated", AUC ≥ 0.70 and
ECE ≤ 0.06 under v2 and the reference).

  python tools/analysis/judge_v2_free_checks.py
"""
import os, sys, sqlite3, math
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import judge_free_tests as jf

TOP4 = ["iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314"]
X = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
CONFIGS = {
    "STACK (v1+ref+anchor)": (os.path.join(X, "stack_v2.db"), "SELECT match_id, model_a, model_b, qid, winner, conf1, conf2, flip, invalid, vote1, vote2_raw FROM verdicts"),
    "STACK-v2 (v2+ref+anchor)": (os.path.join(X, "stack_v2_promptv2.db"), "SELECT match_id, model_a, model_b, qid, winner, conf1, conf2, flip, invalid, vote1, vote2_raw FROM verdicts"),
}


def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]; neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg: return float("nan")
    ranks = {}; allv = sorted(set(scores))
    order = sorted(range(len(scores)), key=lambda i: scores[i]); r = 0
    # rank-sum AUC with ties averaged
    i = 0; rank = [0.0] * len(scores)
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]: j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1): rank[order[k]] = avg
        i = j + 1
    rp = sum(rank[i] for i in range(len(scores)) if labels[i])
    return (rp - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def ece(scores, labels, bins=10):
    scores = np.array(scores); labels = np.array(labels, dtype=float); e = 0.0
    for b in range(bins):
        m = (scores > b / bins) & (scores <= (b + 1) / bins) if b else (scores <= 1 / bins)
        if m.sum(): e += m.mean() * abs(labels[m].mean() - scores[m].mean())
    return e


def main():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    accK, _ = jf.gt_and_lengths(set(TOP4)); gt = sorted(TOP4, key=lambda m: -accK[m]); acc_all = {}
    for m in {m for (_, m) in G}: pass
    print("== B8 confidence calibration and B2 position sensitivity under the new configurations (zero calls) ==")
    print("   key order top-4: %s" % " > ".join(gt))
    for name, (db, sql) in CONFIGS.items():
        if not os.path.exists(db): continue
        rows = [r for r in sqlite3.connect("file:%s?mode=ro" % db, uri=True).execute(sql) if not r[8]]
        scores, labels, top_rows, gap_flips = [], [], [], defaultdict(lambda: [0, 0])
        second_shown = [0, 0]
        for mid, a, b, q, w, c1, c2, fl, inv, v1, v2 in rows:
            ca, cb = G.get((q, a)), G.get((q, b))
            if ca is None or cb is None: continue
            # single-order position: vote1 judged (a as A, b as B); vote2 judged (b as A, a as B) -> "Model B" in either = second-shown
            for v in (v1, v2):
                if v in ("Model A", "Model B"): second_shown[0] += (v == "Model B"); second_shown[1] += 1
            if ca == cb: continue
            d = a if ca else b
            conf = np.mean([x for x in (c1, c2) if x is not None]) if (c1 is not None or c2 is not None) else None
            if conf is not None and w != "TIE":
                scores.append(float(conf)); labels.append(w == d)
            gap = abs(accK.get(a, 0.5) - accK.get(b, 0.5)) if (a in accK and b in accK) else None
            tier = "top4" if (a in TOP4 and b in TOP4) else "other"
            gap_flips[tier][0] += fl; gap_flips[tier][1] += 1
            if tier == "top4": top_rows.append((a, b, w, c1, c2))
        print("\n  %s: %d decisive key-decidable verdicts with confidence" % (name, len(scores)))
        print("     AUC(conf -> correct) %.3f | ECE %.3f | mean conf %.3f | accuracy %.3f  -> B8 %s"
              % (auc(scores, labels), ece(scores, labels), np.mean(scores), np.mean(labels), "OK" if (auc(scores, labels) >= 0.70 and ece(scores, labels) <= 0.06) else "OUT OF BAND"))
        for gate in (0.0, 0.85, 0.95):
            sub = [r for r in top_rows if (r[3] or 0) >= gate and (r[4] or 0) >= gate]
            th = jf.board_from(((a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, w, _, _ in sub), TOP4)
            o, pv, _ = jf.violations(th, gt)
            print("     top-4 board, both-order conf >= %.2f: n=%3d  %s  violations %d" % (gate, len(sub), " > ".join(m.split("-")[0] for m in o), pv))
        print("     B2: flip rate top-4 pairs %.3f (n=%d) | other pairs %.3f (n=%d) | second-shown wins %.3f of %d single-order decisive votes"
              % (gap_flips["top4"][0] / max(1, gap_flips["top4"][1]), gap_flips["top4"][1], gap_flips["other"][0] / max(1, gap_flips["other"][1]), gap_flips["other"][1], second_shown[0] / max(1, second_shown[1]), second_shown[1]))


if __name__ == "__main__":
    main()
