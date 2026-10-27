"""Option A after the 2026-09-09 pool-mismatch incident: every affected claim re-scored on the
CLEAN subset (questions held out under BOTH pools: p2dca AND p8a29, n = 1,020) vs the
CONTAMINATED rest (questions on the frozen tree's train side / in rubric induction).
Zero judge calls. Output: experiment_results/clean_subset_reanalysis.txt.

  python tools/analysis/clean_subset_reanalysis.py
"""
import os, sys, csv, json, math, random, sqlite3
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import judge_free_tests as jf
import bias_audit as ba

R2_DB = os.path.join(ROOT, "experiment_results", "x12_profile", "ratings_x12p.db")
X = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
POOL_RECORD, POOL_TREE = "p2dca21ab5f4ef3ae", "p8a29d8f3ff75aa55"


def pools():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    p = lambda i: {r[0] for r in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (i,))}
    a, b = p(POOL_RECORD), p(POOL_TREE)
    return a, a & b


def mcn(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) * 0.5 ** n for i in range(min(b, c) + 1)))


def main():
    out = []
    def P(s=""):
        print(s); out.append(s)
    record, clean = pools()
    P("CLEAN subset: %d of %d pool-of-record questions are held out under both pools; the other %d were on the frozen tree's train side."
      % (len(clean), len(record), len(record) - len(clean)))
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    L = {(q, m): (ln or 0) for q, m, ln in ev.execute("SELECT question_id, model_name, length(model_output) FROM eval_results")}
    def dec(q, a, b):
        ca, cb = G.get((q, a)), G.get((q, b))
        return None if (ca is None or cb is None or ca == cb) else (a if ca else b)
    x12 = sqlite3.connect("file:%s?mode=ro" % rj.X12_DB, uri=True)
    cell = {r[0]: (int(r[1]), r[2], r[3], r[4], "TIE" if r[6] else r[5]) for r in x12.execute(
        "SELECT id, eval_question_id, model_a, model_b, node_id, winner, is_tie FROM match_history WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,))}

    def paired(title, other, la, lb, cell_lookup=None):
        P("== %s ==" % title)
        for tag, keep in (("CLEAN", lambda q: q in clean), ("CONTAMINATED", lambda q: q not in clean)):
            n = b = c = oa = ob = 0
            for mid, ow in other.items():
                rec = cell.get(mid)
                if rec is None: continue
                q, ma, mb, nid, cw = rec
                if cell_lookup is not None:
                    cw = cell_lookup.get(mid)
                    if cw is None: continue
                if not keep(q): continue
                d = dec(q, ma, mb)
                if d is None: continue
                n += 1; A = (cw == d); Bv = (ow == d); oa += A; ob += Bv; b += (A and not Bv); c += (Bv and not A)
            P("  %-13s n_dec=%4d | %s %.3f vs %s %.3f (%+.3f) | %d:%d McNemar p=%.4f" % (tag, n, la, oa / max(1, n), lb, ob / max(1, n), (oa - ob) / max(1, n), b, c, mcn(b, c)))

    rc = sqlite3.connect("file:%s?mode=ro" % os.path.join(X, "rubric_contrast.db"), uri=True)
    gen_m = {r[0]: r[1] for r in rc.execute("SELECT match_id, winner FROM verdicts WHERE judge='mistral' AND rubric='generic' AND invalid=0")}
    paired("RUBRIC VALUE (Mistral): cell rubric vs generic", gen_m, "cell", "generic")
    r3 = sqlite3.connect("file:%s?mode=ro" % rj.CACHE_DB, uri=True)
    grok_cell = {r[0]: r[1] for r in r3.execute("SELECT match_id, grok_winner FROM verdicts WHERE grok_invalid=0")}
    gen_g = {r[0]: r[1] for r in rc.execute("SELECT match_id, winner FROM verdicts WHERE judge='grok' AND rubric='generic' AND invalid=0")}
    paired("RUBRIC VALUE (grok): cell rubric vs generic", gen_g, "cell", "generic", cell_lookup=grok_cell)
    sw = sqlite3.connect("file:%s?mode=ro" % os.path.join(X, "rubric_swap.db"), uri=True)
    for arm, lb in (("swap_sibling", "sibling"), ("swap_random", "random-anchor"), ("cell_lengthisc", "cell+length-clause")):
        paired("H7: cell vs %s rubric" % lb, {r[0]: r[1] for r in sw.execute("SELECT match_id, winner FROM verdicts WHERE arm=? AND invalid=0", (arm,))}, "cell", lb)
    lad = sqlite3.connect("file:%s?mode=ro" % os.path.join(X, "rubric_ladder.db"), uri=True)
    anc = {r[0]: r[1] for r in lad.execute("SELECT match_id, winner FROM verdicts WHERE arm='anchor' AND invalid=0")}
    strat = {r[0]: r[1] for r in lad.execute("SELECT match_id, winner FROM verdicts WHERE arm='stratum' AND invalid=0")}
    paired("LADDER: leaf(cell, contaminated arm) vs ANCHOR (clean arm)", anc, "leaf", "anchor")
    paired("LADDER: STRATUM (clean) vs ANCHOR (clean)", anc, "stratum", "anchor", cell_lookup=strat)
    paired("LADDER: GENERIC (clean) vs ANCHOR (clean)", anc, "generic", "anchor", cell_lookup=gen_m)

    # 12-model ranking rho vs GT on clean vs contaminated matches
    models = sorted({m for v in cell.values() for m in (v[1], v[2])})
    acc, _ = jf.gt_and_lengths(set(models))
    gt_order = sorted(jf.TOP4, key=lambda m: -acc[m])
    P("== 12-model board vs key accuracy (BT on matches restricted by question subset) ==")
    for name, db in (("x12", rj.X12_DB), ("R2", R2_DB)):
        con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
        rows = [dict(q=int(q), a=a, b=b, w=("TIE" if t else w)) for q, a, b, w, t in con.execute("SELECT eval_question_id, model_a, model_b, winner, is_tie FROM match_history WHERE condition='MAIN'")]
        for tag, keep in (("CLEAN", lambda q: q in clean), ("CONTAMINATED", lambda q: q not in clean), ("ALL", lambda q: True)):
            sub = [r for r in rows if keep(r["q"])]
            th = jf.board_from(jf.current_votes(sub), models)
            o, pv, _ = jf.violations(th, gt_order)
            P("  %-4s %-13s n=%6d | rho %.4f | top-4 %s (viol %d)" % (name, tag, len(sub), jf.rho(th, acc, models), " > ".join(o), pv))

    # interaction LRT (additive BT vs per-group BT over math / law+psych / other) on clean vs contaminated, R2
    P("== model x domain interaction LRT (additive vs per-group BT; groups math / law+psych / other), permutation null 1000 ==")
    nodes = rj.load_nodes()
    parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}
    def anchor_of(nid):
        n = nodes[nid]
        while n["depth"] > 1: n = nodes[parent[n["id"]]]
        return n["label"].lower()
    def group(a):
        return "math" if a == "math" else ("lawpsy" if a in ("law", "psychology") else "other")
    con = sqlite3.connect("file:%s?mode=ro" % R2_DB, uri=True)
    rows = [dict(q=int(q), a=a, b=b, w=("TIE" if t else w), g=group(anchor_of(nid))) for q, a, b, w, t, nid in con.execute("SELECT eval_question_id, model_a, model_b, winner, is_tie, node_id FROM match_history WHERE condition='MAIN'")]
    def ll(rows_, th):
        s = 0.0
        for r in rows_:
            p = 1 / (1 + math.exp(-max(-30, min(30, th[r["a"]] - th[r["b"]]))))
            p = min(max(p, 1e-9), 1 - 1e-9)
            s += 0.5 * (math.log(p) + math.log(1 - p)) if r["w"] == "TIE" else (math.log(p) if r["w"] == r["a"] else math.log(1 - p))
        return s
    def lrt(rows_):
        th0 = jf.board_from(jf.current_votes(rows_), models)
        l0 = ll(rows_, th0)
        l1 = 0.0
        for g in ("math", "lawpsy", "other"):
            sub = [r for r in rows_ if r["g"] == g]
            if len(sub) < 50:
                l1 += ll(sub, th0); continue
            l1 += ll(sub, jf.board_from(jf.current_votes(sub), models))
        return 2 * (l1 - l0)
    rng = random.Random(42)
    for tag, keep in (("CLEAN", lambda q: q in clean), ("CONTAMINATED", lambda q: q not in clean)):
        sub = [dict(r) for r in rows if keep(r["q"])]
        obs = lrt(sub)
        # permute group labels at the QUESTION level (cluster-respecting)
        qs = sorted({r["q"] for r in sub}); qg = {}
        for r in sub: qg[r["q"]] = r["g"]
        labels = [qg[q] for q in qs]
        null = []
        for _ in range(1000):
            rng.shuffle(labels); m = dict(zip(qs, labels))
            for r in sub: r["g"] = m[r["q"]]
            null.append(lrt(sub))
        p = (sum(1 for v in null if v >= obs) + 1) / 1001
        P("  %-13s n=%6d | LRT %.2f | null median %.2f p95 %.2f | p_perm = %.3f" % (tag, len(sub), obs, float(np.median(null)), float(np.percentile(null, 95)), p))

    # verbosity coefficient clean vs contaminated (x12 Mistral cell arm)
    P("== verbosity beta_len (verdict ~ lenDiff/1k + gtDiff, decisive; x12 cell arm) ==")
    for tag, keep in (("CLEAN", lambda q: q in clean), ("CONTAMINATED", lambda q: q not in clean)):
        Xs, Ys = [], []
        for mid, (q, ma, mb, nid, w) in cell.items():
            if not keep(q) or w not in (ma, mb): continue
            la, lb = L.get((q, ma)), L.get((q, mb))
            if la is None or lb is None: continue
            Xs.append(((la - lb) / 1000.0, int(G.get((q, ma), 0)) - int(G.get((q, mb), 0)))); Ys.append(1.0 if w == ma else 0.0)
        b, s = ba._logit3(Xs, Ys)
        P("  %-13s n=%5d | beta_len %+.3f (z=%+.1f) | beta_gt %+.3f" % (tag, len(Ys), b[1], b[1] / s[1], b[2]))

    # strata: fraction of clean questions per stratum (R2 atlas is in-sample for the rest)
    P("== R2 strata: clean-question share (the atlas routing is in-sample for the rest) ==")
    strata = json.load(open(os.path.join(ROOT, "experiment_configs", "strata_profile_v1.json")))["strata"]
    leaf2s = {l: s["id"] for s in strata for l in s["leafIds"]}
    per = defaultdict(set); perc = defaultdict(set)
    for q, nid in con.execute("SELECT DISTINCT eval_question_id, node_id FROM match_history WHERE condition='MAIN'"):
        s = leaf2s.get(nid, "?"); per[s].add(int(q))
        if int(q) in clean: perc[s].add(int(q))
    for s in sorted(per, key=lambda s: len(perc[s]) / len(per[s])):
        P("  %-22s questions %4d | clean %4d (%.0f%%)" % (s, len(per[s]), len(perc[s]), 100 * len(perc[s]) / len(per[s])))
    open(os.path.join(ROOT, "experiment_results", "clean_subset_reanalysis.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
