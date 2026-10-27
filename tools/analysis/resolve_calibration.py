"""RESOLVE-CALIBRATION — the three statistical objections the design's stress pass raised (zero calls).

  python tools/analysis/resolve_calibration.py

(A) THE SUPPORT CONSTANT. The design derives per-cell resolution from SE ~= sqrt(k/q) with k=3. The stress pass
    says the measured bootstrap gives k ~= 4.8, which would make every published resolution 1.5-4x optimistic.
    Measure k directly: fit a BT board per anchor, bootstrap over QUESTIONS (the clustering unit), and solve
    k = q * SE^2 per (anchor, model) cell.
(B) THE SEPARATION CERTIFICATE. The design calibrates its inflation factor f on 66 model pairs. Every
    (anchor, model-pair) cell with key-decidable evidence is an edge, which is far more. Sweep f and report the
    wrong-direction rate among edges the certificate is willing to call, with an upper confidence bound.
(C) CROSS-CELL SCALE. A tier map compares theta across anchors. That is only meaningful if the anchors share a
    scale. Measure each anchor's own BT dispersion on the shared roster.
"""
import os, sys, math, random, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import pool_guard

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "resolve_calibration.txt")
B = 300


def main():
    L = []
    models = sorted(p8.ARENA12)
    acc, _ = jf.gt_and_lengths(set(p8.ARENA12))
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in p8.ARENA12: K[q][m] = int(c or 0)
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(list)
    for a, b, q, w, _ in rows:
        if q in route: by[anchor_of(route[q])].append((a, b, q, w))

    # ---------- (A) the support constant ----------
    L.append("=== (A) THE SUPPORT CONSTANT: is SE ~= sqrt(k/q) with k=3, or larger? ===")
    L.append("  Per anchor: fit a BT board on that anchor's matches, bootstrap over QUESTIONS (the clustering")
    L.append("  unit, not matches), and solve k = q * SE^2 for each (anchor, model) cell.")
    L.append("")
    L.append("  %-16s %6s %7s %8s %8s %8s" % ("anchor", "matches", "q(med)", "SE(med)", "k(med)", "k(p90)"))
    ks = []
    rng = random.Random(42)
    for anc in sorted(by, key=lambda a: -len(by[a])):
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
        supp = defaultdict(set)
        for a, b, q, _ in rs: supp[a].add(q); supp[b].add(q)
        cellk = []
        for m in models:
            v = [d[m] for d in draws]
            mu = sum(v) / len(v)
            se = (sum((x - mu) ** 2 for x in v) / (len(v) - 1)) ** 0.5
            qn = len(supp[m])
            if qn > 10 and se > 0: cellk.append((qn, se, qn * se * se))
        if not cellk: continue
        cellk.sort(key=lambda t: t[2])
        med = cellk[len(cellk) // 2]
        p90 = cellk[int(0.9 * len(cellk))]
        ks.extend(t[2] for t in cellk)
        L.append("  %-16s %6d %7d %8.3f %8.2f %8.2f" % (anc[:16], len(rs), med[0], med[1], med[2], p90[2]))
    ks.sort()
    kmed = ks[len(ks) // 2]; kp90 = ks[int(0.9 * len(ks))]
    L.append("")
    L.append("  POOLED over %d cells: k median %.2f | p10 %.2f | p90 %.2f" % (len(ks), kmed, ks[int(0.1 * len(ks))], kp90))
    r = math.sqrt(kmed / 3.0)
    L.append("  The design assumes k=3; the measured median is %.2f (p90 %.2f)." % (kmed, kp90))
    L.append("  %s" % ("So k=3 OVERSTATES the per-cell SE by %.2fx and the design's resolution claim is CONSERVATIVE "
                       "by that factor - the stress pass's k~=4.8 does not reproduce." % (1 / r) if kmed < 3 else
                       "So k=3 UNDERSTATES the per-cell SE by %.2fx and every resolution claim is optimistic by it." % r))
    L.append("  At the measured k, SE=0.20 needs q = %d distinct questions per cell; at k=3 it needs %d."
             % (int(kmed / 0.04), int(3 / 0.04)))

    # ---------- (B) the separation certificate ----------
    L.append("")
    L.append("=== (B) THE SEPARATION CERTIFICATE: calibrate the inflation factor on every edge, not 66 ===")
    L.append("  An EDGE is an (anchor, model-pair) cell carrying key-decidable evidence. For each, the arena's")
    L.append("  P(A above B) comes from the per-anchor bootstrap; the truth comes from the key on that anchor.")
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
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if a not in la or b not in la or abs(la[a] - la[b]) < 0.02: continue
                p = sum(1 for d in draws if d[a] > d[b]) / B
                edges.append((p, la[a] > la[b]))
    L.append("  edges with a key gap above 2pp: %d (the design calibrated on 66 global pairs)" % len(edges))
    L.append("")
    L.append("  An earlier version of this sweep inflated the interval as |p-0.5|/f, which is unsatisfiable for")
    L.append("  f > 1.11 and reported 0 edges called at every f above 1. The quantity the design actually sets is")
    L.append("  the CONFIDENCE THRESHOLD, so sweep that.")
    L.append("")
    L.append("  %10s %10s %10s %16s %16s" % ("threshold", "called", "declined", "wrong-direction", "95% upper bound"))
    for thr in (0.90, 0.95, 0.975, 0.99, 0.995, 1.00):
        called = [((p > 0.5) == truth) for p, truth in edges if p >= thr or p <= 1 - thr]
        if not called:
            L.append("  %10.3f %10d %10d %16s %16s" % (thr, 0, len(edges), "-", "-")); continue
        wrong = sum(1 for c in called if not c)
        rate = wrong / len(called)
        ub = rate + 1.96 * math.sqrt(max(rate * (1 - rate), 1e-9) / len(called))
        L.append("  %10.3f %10d %10d %15.2f%% %15.2f%%" % (thr, len(called), len(edges) - len(called), 100 * rate, 100 * ub))
    L.append("  READ: pick the smallest threshold whose 95%% UPPER BOUND clears the target. A zero-count criterion on 66")
    L.append("  edges cannot distinguish a 0%% rate from a 4%% one; that is what the stress pass objected to.")

    # ---------- (C) cross-cell scale ----------
    L.append("")
    L.append("=== (C) CROSS-CELL SCALE: do anchors share a theta scale at all? ===")
    L.append("  %-16s %8s %10s %10s" % ("anchor", "matches", "theta SD", "range"))
    sds = []
    for anc in sorted(by, key=lambda a: -len(by[a])):
        rs = by[anc]
        if len(rs) < 200: continue
        th = jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in rs], models)
        v = list(th.values()); mu = sum(v) / len(v)
        sd = (sum((x - mu) ** 2 for x in v) / (len(v) - 1)) ** 0.5
        sds.append(sd)
        L.append("  %-16s %8d %10.3f %10.3f" % (anc[:16], len(rs), sd, max(v) - min(v)))
    sds.sort()
    L.append("")
    L.append("  theta SD across anchors: min %.3f, median %.3f, max %.3f - a %.1fx spread"
             % (sds[0], sds[len(sds) // 2], sds[-1], sds[-1] / max(1e-9, sds[0])))
    L.append("  A tier map that compares raw theta across anchors is comparing numbers on different scales by")
    L.append("  exactly that factor. Either standardise (publish theta/SD with the SD beside it) or publish")
    L.append("  independent within-anchor boards and no cross-anchor statement at all.")

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
