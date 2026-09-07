"""Question-level permutation robustness check for the R2 atlas LRT.

POST-HOC ROBUSTNESS, NOT THE REGISTERED TEST (disclosed). The registered primary
(profile_atlas.py) permutes stratum labels at the MATCH level within (anchor, pair);
matches sharing a question scatter independently, which the measured query-level
design effect (median 2.0x, worst 3.7x) says can overstate significance. This check
permutes at the QUESTION level: within each split anchor, whole questions (with all
their matches) are reassigned between the two strata, preserving per-stratum
question counts. Everything else — LRT statistic, fits, NPERM, seed — matches the
registered script, imported from it directly.
"""
import sys, os, json, sqlite3, random
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import profile_atlas as pa

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    db = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        ROOT, "experiment_results", "x12_profile", "ratings_x12p.db")
    strata_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        ROOT, "experiment_configs", "strata_profile_v1.json")
    spec = json.load(open(strata_path, encoding="utf-8"))
    stratum_of, anchor_of_stratum = {}, {}
    for s in spec["strata"]:
        anchor_of_stratum[s["id"]] = s["anchor"]
        for l in s["leafIds"]:
            stratum_of[l] = s["id"]
    split_anchors = sorted({a for sid, a in anchor_of_stratum.items() if "-" in sid})

    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    raw = con.execute(
        "SELECT model_a, model_b, winner, is_tie, node_id, eval_question_id "
        "FROM match_history WHERE condition='MAIN'").fetchall()
    con.close()

    by_stratum_q = defaultdict(lambda: defaultdict(list))  # sid -> qid -> match rows
    models = set()
    for ma, mb, w, t, nid, qid in raw:
        sid = stratum_of.get(nid)
        if sid is None:
            continue
        by_stratum_q[sid][int(qid)].append((ma, mb, w, t))
        models.update((ma, mb))
    models = sorted(models)

    def anchor_lrt(pairs):
        total = 0.0
        for rows1, rows2 in pairs:
            agg1, agg2 = pa.aggregate(rows1), pa.aggregate(rows2)
            pooled = pa.aggregate(rows1 + rows2)
            th1, th2 = pa.mm_fit(agg1, models), pa.mm_fit(agg2, models)
            thp = pa.mm_fit(pooled, models)
            total += 2 * (pa.ll_of(agg1, th1) + pa.ll_of(agg2, th2) - pa.ll_of(pooled, thp))
        return total

    anchor_qmaps = []   # per split anchor: (qmap1, qmap2)
    for anchor in split_anchors:
        sids = sorted(sid for sid, a in anchor_of_stratum.items() if a == anchor)
        if len(sids) == 2 and all(s in by_stratum_q for s in sids):
            anchor_qmaps.append((by_stratum_q[sids[0]], by_stratum_q[sids[1]]))

    def flatten(qmap):
        return [m for v in qmap.values() for m in v]

    observed = anchor_lrt([(flatten(q1), flatten(q2)) for q1, q2 in anchor_qmaps])

    rng = random.Random(pa.PERM_SEED)
    null = []
    for _ in range(pa.NPERM):
        pairs = []
        for q1, q2 in anchor_qmaps:
            qids = list(q1) + list(q2)
            rng.shuffle(qids)
            n1 = len(q1)
            lookup = {**q1, **q2}
            r1 = [m for q in qids[:n1] for m in lookup[q]]
            r2 = [m for q in qids[n1:] for m in lookup[q]]
            pairs.append((r1, r2))
        null.append(anchor_lrt(pairs))
    null.sort()
    ge = sum(1 for v in null if v >= observed)
    p = (1 + ge) / (1 + pa.NPERM)
    print("=== ROBUSTNESS: question-level permutation of the pooled within-anchor LRT ===")
    print("(post-hoc, cluster-respecting; registered match-level test gave p = 0.001)")
    print("split anchors: %d | questions per anchor-pair: %s"
          % (len(anchor_qmaps), [len(q1) + len(q2) for q1, q2 in anchor_qmaps]))
    print("observed LRT = %.2f | null median %.2f, p95 %.2f, max %.2f | p_perm = %.4f"
          % (observed, null[len(null)//2], null[int(0.95*len(null))], null[-1], p))


if __name__ == "__main__":
    main()
