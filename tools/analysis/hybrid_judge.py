"""HYBRID — grade to rank, compare only where grades are close (registered 2026-09-13, docs/judge_v2_program.md).

  python tools/analysis/hybrid_judge.py [--taus 0,1,2,5,10,15,20,30,40,60,100]

Zero LLM calls: both formats have already judged the same 1,980 R3 matches, so any routing rule between them is
a re-read of the caches. RULE: if |grade_a - grade_b| > tau take the POINTWISE verdict, else take the PAIRWISE
one. tau = 0 sends only exact grade ties to the pairwise judge; tau = 100 sends everything.
REGISTERED READOUT per tau: key-decidable accuracy, 12-model board rho vs key accuracy, top-4 key-order
violations, and the pairwise BUDGET (fraction of matches routed to pairwise, so calls per match = 1 + 2*budget
once grades are amortised). tau* = the smallest budget reaching accuracy >= 0.864 AND 0 top-4 violations.
"""
import os, sys, sqlite3, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pointwise_judge as pt
import rejudge_grok as rj
import judge_free_tests as jf
import stack_judge as sj


def main(taus):
    sample, tgt = pt.targets()
    Gr = {(q, m): g for q, m, g in pt.open_cache().execute("SELECT qid, model, grade FROM grades")}
    pw = {r[0]: r for r in sqlite3.connect("file:%s?mode=ro" % pt.PAIRWISE, uri=True).execute("SELECT match_id, model_a, model_b, qid, winner, invalid FROM verdicts")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    models = sorted({m for _, m in tgt}); TOP4 = sj.TOP4
    acck, _ = jf.gt_and_lengths(set(models)); gt = sorted(TOP4, key=lambda m: -acck[m])
    ms = []
    for m in sample:
        mid, qid, a, b = m[0], int(m[1]), m[2], m[3]
        p = pw.get(mid)
        if p is None or p[5] or (qid, a) not in Gr or (qid, b) not in Gr: continue
        ms.append((mid, qid, a, b))
    print("HYBRID: %d matches judged by BOTH formats | key order %s" % (len(ms), " > ".join(gt)))
    print("\n%6s %9s %10s %11s %10s %12s" % ("tau", "pairwise%", "accuracy", "board rho", "top-4 viol", "calls/match"))
    best = None
    for tau in taus:
        def verdict(mid, qid, a, b):
            ga, gb = Gr[(qid, a)], Gr[(qid, b)]
            if abs(ga - gb) > tau:
                return "TIE" if ga == gb else (a if ga > gb else b)
            return pw[mid][4]
        used_pw = sum(1 for mid, qid, a, b in ms if abs(Gr[(qid, a)] - Gr[(qid, b)]) <= tau) / len(ms)
        dec = [(mid, qid, a, b) for mid, qid, a, b in ms if K.get((qid, a)) is not None and K.get((qid, b)) is not None and K[(qid, a)] != K[(qid, b)]]
        acc = sum(1 for mid, qid, a, b in dec if verdict(mid, qid, a, b) == (a if K[(qid, a)] else b)) / len(dec)
        th = jf.board_from(((a, b, 0.5 if verdict(mid, qid, a, b) == "TIE" else (1.0 if verdict(mid, qid, a, b) == a else 0.0), 1.0) for mid, qid, a, b in ms), models)
        rho = rj.spearman([th[x] for x in models], [acck[x] for x in models])
        t4 = [(mid, qid, a, b) for mid, qid, a, b in ms if a in TOP4 and b in TOP4]
        th4 = jf.board_from(((a, b, 0.5 if verdict(mid, qid, a, b) == "TIE" else (1.0 if verdict(mid, qid, a, b) == a else 0.0), 1.0) for mid, qid, a, b in t4), TOP4)
        _, pv, _ = jf.violations(th4, gt)
        cpm = 1.0 * len(Gr) / len(sample) + 2.0 * used_pw
        print("%6d %8.1f%% %10.3f %11.4f %10d %12.2f" % (tau, 100 * used_pw, acc, rho, pv, cpm))
        if acc >= 0.864 and pv == 0 and (best is None or used_pw < best[1]): best = (tau, used_pw, acc, rho, cpm)
    print("\n  reference points: all-pairwise accuracy 0.864 / rho 0.9790 / 1 violation / 2.00 calls per match")
    print("                    all-pointwise  accuracy 0.808 / rho 0.9930 / 0 violations / 1.86 calls per match")
    if best:
        print("  tau* = %d: pairwise budget %.1f%%, accuracy %.3f, rho %.4f, %.2f calls/match -> PASS (accuracy >= 0.864 and 0 violations)"
              % (best[0], 100 * best[1], best[2], best[3], best[4]))
    else:
        print("  no tau reaches accuracy >= 0.864 AND 0 violations simultaneously -> report the frontier as measured")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--taus", default="0,1,2,5,10,15,20,30,40,60,100")
    a = ap.parse_args(); main([int(t) for t in a.taus.split(",")])
