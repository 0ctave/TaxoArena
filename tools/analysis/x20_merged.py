"""X20-MERGED — TIER-HONEST-X20 and PROFILE-RELIABILITY-X20 rerun on the BOARD OF RECORD (2026-09-15).

  python tools/analysis/x20_merged.py

CORRECTION. x20_replications.py, budget_transfer.py and every x20 analysis of 2026-09-14 read
stack_v2_promptv2_x20.db ALONE. That cache holds 12,394 verdicts on the 124 pairs involving at least one new
model and ZERO verdicts on the 66 original x12 pairs (checked by SQL, 2026-09-15). The 20-model board those
scripts fitted therefore never compared the twelve originals directly; ARENA-V2-X20 of record merged the x12
cache (9,142) with the x20 cache (12,394) = 21,536 verdicts. This script fits the MERGED board and reruns both
instruments on it, so the corrected numbers sit beside the sparse-board ones in the record.
"""
import os, sys, sqlite3, random
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import pool_guard
import profile_reliability as pr
import x20_replications as xr

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "x20_merged.txt")


def merged_rows():
    con = sqlite3.connect("file:%s?mode=ro" % xr.X20, uri=True)
    r20 = [r for r in con.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    r12 = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    return r12 + r20, len(r12), len(r20)


def main():
    L = []
    rows, n12, n20 = merged_rows()
    models = sorted({r[0] for r in rows} | {r[1] for r in rows})
    old = set(p8.ARENA12)
    L.append("=== X20-MERGED: the two x20 instruments on the BOARD OF RECORD ===")
    L.append("  x12 cache %d + x20 cache %d = %d verdicts | %d models" % (n12, n20, len(rows), len(models)))
    L.append("  the sparse board of 2026-09-14 used the x20 cache alone: 0 verdicts on the 66 original pairs.")

    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")}
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in models: K[q][m] = int(c or 0)
    qs_judged = sorted({r[2] for r in rows})
    # key accuracy over the JUDGED questions, not the whole pool (a defect the review found in x20_replications)
    acc = {m: sum(K[q][m] for q in qs_judged if m in K.get(q, {})) / max(1, sum(1 for q in qs_judged if m in K.get(q, {}))) for m in models}

    # ---------- TIER-HONEST on the merged board ----------
    rng = random.Random(42)
    byq = defaultdict(list)
    for r in rows: byq[r[2]].append(r)
    boards = []
    for _ in range(xr.B):
        pick = [qs_judged[rng.randrange(len(qs_judged))] for _ in qs_judged]
        sub = [r for q in pick for r in byq[q]]
        boards.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w, _iv in sub], models))
    kt = xr.key_tiers(acc, models); tier_of = {m: i for i, t in enumerate(kt) for m in t}

    def mcn(a, b):
        import math
        x = y = 0
        for q in qs_judged:
            ka = K[q].get(a); kb = K[q].get(b)
            if ka is None or kb is None or ka == kb: continue
            if ka > kb: x += 1
            else: y += 1
        n = x + y; k = min(x, y)
        return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0

    L.append("")
    L.append("=== TIER-HONEST on the merged board (key accuracy over the %d JUDGED questions) ===" % len(qs_judged))
    L.append("  key tiers at %.3f gap: %d" % (xr.KEY_GAP, len(kt)))
    allp = [(a, b) for i, a in enumerate(models) for b in models[i + 1:]]
    for name, pairs in (("ALL", allp), ("SHARED", [(a, b) for a, b in allp if a in old and b in old]),
                        ("NOVEL", [(a, b) for a, b in allp if not (a in old and b in old)])):
        sep = []
        for a, b in pairs:
            p = sum(1 for d in boards if d[a] > d[b]) / xr.B
            if p >= xr.CONF or p <= 1 - xr.CONF:
                sep.append((a, b, p, (p > 0.5) == (acc[a] > acc[b]), mcn(a, b) < 0.05))
        for lab, sel in (("within", lambda s: tier_of[s[0]] == tier_of[s[1]]), ("across", lambda s: tier_of[s[0]] != tier_of[s[1]])):
            ss = [s for s in sep if sel(s)]
            tot = sum(1 for a, b in pairs if (tier_of[a] == tier_of[b]) == (lab == "within"))
            w = [s for s in ss if not s[3]]; we = [s for s in w if s[4]]
            L.append("  %-6s %-7s %3d/%3d separated | wrong %2d, of which McNemar-ESTABLISHED %2d"
                     % (name, lab, len(ss), tot, len(w), len(we)))
    order = sorted(models, key=lambda m: -sum(d[m] for d in boards) / xr.B)
    groups = [[order[0]]]
    for a, b in zip(order, order[1:]):
        p = sum(1 for d in boards if d[a] > d[b]) / xr.B
        if p >= xr.CONF: groups.append([b])
        else: groups[-1].append(b)
    invs = [(x, y) for i, g in enumerate(groups) for j in range(i + 1, len(groups)) for x in g for y in groups[j] if acc[x] < acc[y]]
    L.append("  self-tiering: %d tiers | cross-tier key inversions %d, established %d"
             % (len(groups), len(invs), sum(1 for x, y in invs if mcn(x, y) < 0.05)))
    L.append("  (sparse board gave 11 tiers / 9 inversions; x12 gave 10 / 2)")

    # ---------- PROFILE-RELIABILITY on the merged board ----------
    route = r512.primary_routing(xr.TREE)
    nodes = r512.load_graph(r512.snapshot_id(xr.TREE)); anc = r512.anchor_fn(nodes)
    rows_by_q = defaultdict(list)
    for a, b, q, w, _ in rows: rows_by_q[q].append((a, b, q, w))
    q2 = sorted(set(route) & set(rows_by_q)); qsel = set(q2)
    leaf_cells = defaultdict(list); anc_cells = defaultdict(list)
    for q in q2: leaf_cells[route[q]].append(q); anc_cells[anc(route[q])].append(q)

    def judge_build(cqs):
        rs = [r for q in cqs for r in rows_by_q[q]]
        if len({r[2] for r in rs}) < 10: return None
        return jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in rs], models)

    def key_build(cqs):
        d = {m: sum(K[q][m] for q in cqs if m in K.get(q, {})) / max(1, sum(1 for q in cqs if m in K.get(q, {}))) for m in models}
        return d

    L.append("")
    L.append("=== PROFILE-RELIABILITY on the merged board (registered bar 0.70) ===")
    L.append("  %-8s %6s %8s %10s %12s %10s" % ("level", "cells", "q/cell", "judge r", "judge R(SB)", "key R(SB)"))
    for name, cells in (("leaf", leaf_cells), ("anchor", anc_cells)):
        usable = {c: v for c, v in cells.items() if len(v) >= 50}
        jr, jsd, nj = pr.reliability(usable, qsel, judge_build, models, random.Random(7))
        kr, _, _ = pr.reliability(usable, qsel, key_build, models, random.Random(7))
        qpc = sum(len(v) for v in usable.values()) / len(usable)
        L.append("  %-8s %6d %8.0f %10.4f %12.4f %10.4f   (SD %.4f)" % (name, len(usable), qpc, jr, pr.sb(jr), pr.sb(kr), jsd))
        if name == "anchor":
            R = pr.sb(jr)
            L.append("  anchor R on the board of record = %.4f -> %s the 0.70 bar (sparse board 0.6283; x12 0.6728)"
                     % (R, "CLEARS" if R >= 0.70 else "misses"))

    txt = "\n".join(L); print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
