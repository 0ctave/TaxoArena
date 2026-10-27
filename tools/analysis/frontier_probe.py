"""FRONTIER — dilution, judge capability, or the dataset? (registered 2026-09-13; ZERO LLM calls)

  python tools/analysis/frontier_probe.py

(A) DATASET: for each top-4 pair, how many questions the two models actually DIFFER on, the win split, and
    whether the key's own accuracy gap is resolvable at that sample size.
(B) DILUTION: refit the top-4 board on DECIDABLE matches only (pairwise and pointwise arms) and compare the
    key-order violations against the all-matches boards (pairwise 1, pointwise 0).
"""
import os, sys, math, sqlite3
from itertools import combinations
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import judge_free_tests as jf
import stack_judge as sj
import pointwise_judge as pt
import rubric_p8 as p8

TOP4 = sj.TOP4


def main():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")}
    K = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results") if m in TOP4}
    acc, _ = jf.gt_and_lengths(set(TOP4)); gt = sorted(TOP4, key=lambda m: -acc[m])
    print("=== (A) DATASET: do the frontier models differ on enough questions to be separable at all? ===")
    print("key accuracy on the pool: %s" % " | ".join("%s %.3f" % (m[:12], acc[m]) for m in gt))
    qs = sorted(q for q in pool if all((q, m) in K for m in TOP4))
    print("\n%-13s %-13s %7s %8s %8s %9s %9s   %s" % ("model A", "model B", "differ", "A wins", "B wins", "win rate", "SE", "key gap / resolvable?"))
    for a, b in combinations(gt, 2):
        d = [q for q in qs if K[(q, a)] != K[(q, b)]]
        wa = sum(1 for q in d if K[(q, a)]); n = len(d)
        wr = wa / n; se = math.sqrt(wr * (1 - wr) / n)
        gap = acc[a] - acc[b]
        # a win rate of 0.5 means indistinguishable; resolvable if it is more than 2 SE from 0.5
        res = "YES" if abs(wr - 0.5) > 2 * se else "NO  (indistinguishable on this pool)"
        print("%-13s %-13s %7d %8d %8d %9.3f %9.3f   %+.3f  %s" % (a[:13], b[:13], n, wa, n - wa, wr, se, gap, res))
    print("\n  reading: 'differ' is the only evidence any judge can use on that pair; a win rate within 2 SE of")
    print("  0.500 means the pool itself cannot separate the two models, whatever the judge does.")

    print("\n=== (B) DILUTION: refit the top-4 board on DECIDABLE matches only ===")
    sample, tgt = pt.targets()
    Gr = {(q, m): g for q, m, g in pt.open_cache().execute("SELECT qid, model, grade FROM grades")}
    pw = {r[0]: r for r in sqlite3.connect("file:%s?mode=ro" % pt.PAIRWISE, uri=True).execute("SELECT match_id, model_a, model_b, qid, winner, invalid FROM verdicts")}
    ms = [(m[0], int(m[1]), m[2], m[3]) for m in sample if m[2] in TOP4 and m[3] in TOP4
          and pw.get(m[0]) and not pw[m[0]][5] and (int(m[1]), m[2]) in Gr and (int(m[1]), m[3]) in Gr]
    dec = [x for x in ms if K.get((x[1], x[2])) is not None and K.get((x[1], x[3])) is not None and K[(x[1], x[2])] != K[(x[1], x[3])]]
    print("  top-4 matches judged by both formats: %d | of which key-decidable: %d (%.0f%%)" % (len(ms), len(dec), 100 * len(dec) / len(ms)))
    fmt = {"pairwise": lambda x: 0.5 if pw[x[0]][4] == "TIE" else (1.0 if pw[x[0]][4] == x[2] else 0.0),
           "pointwise": lambda x: 0.5 if Gr[(x[1], x[2])] == Gr[(x[1], x[3])] else (1.0 if Gr[(x[1], x[2])] > Gr[(x[1], x[3])] else 0.0)}
    for name, fn in fmt.items():
        for label, subset in (("all matches", ms), ("decidable only", dec)):
            th = jf.board_from(((x[2], x[3], fn(x), 1.0) for x in subset), TOP4)
            o, pv, _ = jf.violations(th, gt)
            acc_sub = sum(1 for x in subset if (("TIE" if fn(x) == 0.5 else (x[2] if fn(x) > 0.5 else x[3])) == (x[2] if K[(x[1], x[2])] else x[3]))) / len(subset) if subset is dec else float("nan")
            print("  %-10s %-15s n=%4d | %s (%d violations)%s" % (name, label, len(subset), " > ".join(m[:12] for m in o), pv,
                  "" if subset is ms else " | accuracy on these %.3f" % acc_sub))
    print("\n  key order: %s" % " > ".join(m[:12] for m in gt))


if __name__ == "__main__":
    main()
