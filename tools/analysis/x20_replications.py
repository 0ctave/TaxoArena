"""TIER-HONEST-X20 and PROFILE-RELIABILITY-X20 — do the two findings RESOLVE rests on replicate on a bigger
board? (registered 2026-09-14, zero calls)

  python tools/analysis/x20_replications.py

TIER-HONEST is the result the entire budget line exists to answer, and on x12 it rested on TWO within-tier
separations out of 66 pairs. PROFILE-RELIABILITY closed the granular-profile deliverable on 12 models at a
reliability of 0.6728 against a 0.70 bar. The 20-model board carries 12,394 cached verdicts and 190 pairs and
has never been put through either instrument.

x20 CONTAINS x12, so the 66 shared pairs are NOT an independent replication and are reported separately.
"""
import os, sys, math, random, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import judge_free_tests as jf
import pool_guard
import profile_reliability as pr

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "x20_replications.txt")
X20 = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_x20.db")
KEY_GAP = 0.017          # the tier gap TIER-HONEST used
B = 400                  # TIER-HONEST used 400 draws
CONF = 0.95
TREE = "bareq512_s42"


def key_tiers(acc, models, gap=KEY_GAP):
    o = sorted(models, key=lambda m: -acc[m]); out = []; cur = [o[0]]
    for a, b in zip(o, o[1:]):
        if acc[a] - acc[b] < gap: cur.append(b)
        else: out.append(cur); cur = [b]
    out.append(cur); return out


def main():
    L = []
    con = sqlite3.connect("file:%s?mode=ro" % X20, uri=True)
    rows = [r for r in con.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    models = sorted({r[0] for r in rows} | {r[1] for r in rows})
    old = set(p8.ARENA12)

    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")}
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in models:
            K[q][m] = int(c or 0)
    acc = {}
    for m in models:
        v = [K[q][m] for q in pool if m in K.get(q, {})]
        if v: acc[m] = sum(v) / len(v)

    # ================= TIER-HONEST-X20 =================
    L.append("=== TIER-HONEST-X20: does the finding the whole budget line rests on replicate? ===")
    L.append("  x12 gave: across-tier 62 of 64 separated with ZERO wrong; within-tier 2 of 2 separated, BOTH")
    L.append("  pointing the wrong way per tier_design_probes.txt (the first version of this header said ONE,")
    L.append("  which understated x12). Here: %d models, %d pairs, %d verdicts."
             % (len(models), len(models) * (len(models) - 1) // 2, len(rows)))
    L.append("  SUPERSEDED 2026-09-15: this script reads the x20 cache ALONE, which carries no verdicts on the 66")
    L.append("  original pairs; x20_merged.py is the instrument of record. Kept so the sparse-board numbers reproduce.")
    rng = random.Random(42)
    qs = sorted({r[2] for r in rows})
    byq = defaultdict(list)
    for r in rows:
        byq[r[2]].append(r)
    boards = []
    for _ in range(B):
        pick = [qs[rng.randrange(len(qs))] for _ in qs]
        sub = [r for q in pick for r in byq[q]]
        boards.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                                     for a, b, _, w, _iv in sub], models))
    kt = key_tiers(acc, models)
    tier_of = {m: i for i, t in enumerate(kt) for m in t}
    L.append("")
    L.append("  the key's %d tiers at a %.3f gap:" % (len(kt), KEY_GAP))
    for i, t in enumerate(kt):
        L.append("    tier %d: %s" % (i, ", ".join("%s (%.3f)" % (m[:24], acc[m]) for m in t)))

    def report(name, pairs):
        sep = []
        for a, b in pairs:
            p = sum(1 for d in boards if d[a] > d[b]) / B
            if p >= CONF or p <= 1 - CONF:
                sep.append((a, b, p, (p > 0.5) == (acc[a] > acc[b])))
        same = [x for x in sep if tier_of[x[0]] == tier_of[x[1]]]
        diff = [x for x in sep if tier_of[x[0]] != tier_of[x[1]]]
        ns = sum(1 for a, b in pairs if tier_of[a] == tier_of[b])
        nd = len(pairs) - ns
        sw = sum(1 for x in same if not x[3]); dw = sum(1 for x in diff if not x[3])
        L.append("  %-26s within-tier %3d/%3d separated, %2d WRONG (%.1f%%) | across-tier %3d/%3d, %2d WRONG (%.1f%%)"
                 % (name, len(same), ns, sw, 100.0 * sw / max(1, len(same)),
                    len(diff), nd, dw, 100.0 * dw / max(1, len(diff))))
        return same, diff, sw, dw

    allp = [(a, b) for i, a in enumerate(models) for b in models[i + 1:]]
    shared = [(a, b) for a, b in allp if a in old and b in old]
    novel = [(a, b) for a, b in allp if not (a in old and b in old)]
    L.append("")
    L.append("  separations at %.0f%% confidence:" % (100 * CONF))
    s_all, d_all, sw_all, dw_all = report("ALL %d pairs" % len(allp), allp)
    report("SHARED (in x12, not new)", shared)
    s_nov, d_nov, sw_nov, dw_nov = report("NOVEL (independent)", novel)

    L.append("")
    L.append("  (1) PRIMARY: is the within-tier rate disproportionately wrong against across-tier?")
    rs = 100.0 * sw_all / max(1, len(s_all)); rd = 100.0 * dw_all / max(1, len(d_all))
    L.append("      within-tier %.1f%% wrong against across-tier %.1f%% -> %s"
             % (rs, rd, "REPLICATES: within-tier separations are where the board is dishonest" if rs > rd
                else "DOES NOT REPLICATE at this roster"))
    L.append("      on the NOVEL pairs alone (the only independent test): within %.1f%%, across %.1f%%"
             % (100.0 * sw_nov / max(1, len(s_nov)), 100.0 * dw_nov / max(1, len(d_nov))))
    if s_all:
        L.append("")
        L.append("      every WITHIN-TIER separation that points the wrong way:")
        for a, b, p, ok in s_all:
            if not ok:
                L.append("        %-26s vs %-26s p=%.3f but key says %.3f vs %.3f"
                         % (a[:26], b[:26], p, acc[a], acc[b]))

    # (2) the arena's own self-tiering
    L.append("")
    L.append("  (2) THE ARENA'S OWN TIERING, by its own intervals:")
    order = sorted(models, key=lambda m: -sum(d[m] for d in boards) / B)
    groups = [[order[0]]]
    for a, b in zip(order, order[1:]):
        p = sum(1 for d in boards if d[a] > d[b]) / B
        if p >= CONF: groups.append([b])
        else: groups[-1].append(b)
    L.append("      the arena separates itself into %d tiers (x12 gave 10)" % len(groups))
    invs = []
    for i, g in enumerate(groups):
        for j in range(i + 1, len(groups)):
            for x in g:
                for y in groups[j]:
                    if acc[x] < acc[y]: invs.append((x, y))
    L.append("      cross-tier key inversions in its own tiering: %d (x12 gave 2)" % len(invs))
    for x, y in invs:  # [2026-09-16 hygiene: was invs[:8], which hid inversions beyond the eighth]
        L.append("        %-26s tiered ABOVE %-26s but scores %.3f against %.3f" % (x[:26], y[:26], acc[x], acc[y]))

    # ================= PROFILE-RELIABILITY-X20 =================
    L.append("")
    L.append("=== PROFILE-RELIABILITY-X20: does a bigger roster rescue the anchor profile? ===")
    L.append("  x12 gave anchor R = 0.6728 against a registered 0.70 bar, and the deliverable was closed on it.")
    route = r512.primary_routing(TREE)
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anc = r512.anchor_fn(nodes)
    rows_by_q = defaultdict(list)
    for a, b, q, w, _ in rows:
        rows_by_q[q].append((a, b, q, w))
    q2 = sorted(set(route) & set(rows_by_q))
    qsel = set(q2)
    leaf_cells = defaultdict(list); anc_cells = defaultdict(list)
    for q in q2:
        leaf_cells[route[q]].append(q); anc_cells[anc(route[q])].append(q)

    def judge_build(cqs):
        rs = [r for q in cqs for r in rows_by_q[q]]
        if len({r[2] for r in rs}) < 10: return None
        return jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                              for a, b, _, w in rs], models)

    def key_build(cqs):
        d = {}
        for m in models:
            v = [K[q][m] for q in cqs if m in K.get(q, {})]
            if v: d[m] = sum(v) / len(v)
        return d if len(d) == len(models) else None

    L.append("  pool %d questions | %d leaves | %d anchors | %d models | %d verdicts"
             % (len(q2), len(leaf_cells), len(anc_cells), len(models), len(rows)))
    L.append("")
    L.append("  %-10s %7s %9s %12s %12s %12s" % ("level", "cells", "q/cell", "judge r", "judge R(SB)", "key R(SB)"))
    res = {}
    for name, cells in (("leaf", leaf_cells), ("anchor", anc_cells)):
        usable = {c: v for c, v in cells.items() if len(v) >= 50}
        if not usable: continue
        jr, jsd, nj = pr.reliability(usable, qsel, judge_build, models, random.Random(7))
        kr, _, _ = pr.reliability(usable, qsel, key_build, models, random.Random(7))
        qpc = sum(len(v) for v in usable.values()) / len(usable)
        res[name] = pr.sb(jr)
        L.append("  %-10s %7d %9.0f %12.4f %12.4f %12.4f" % (name, len(usable), qpc, jr, pr.sb(jr), pr.sb(kr)))
        L.append("             (split-half SD %.4f over %d halvings)" % (jsd, nj))
    if "anchor" in res:
        a20 = res["anchor"]
        L.append("")
        L.append("  REGISTERED BAR 0.70, the same one x12 failed at 0.6728:")
        L.append("    x20 anchor R = %.4f  ->  %s" % (a20, "PASS" if a20 >= 0.70 else "FAIL"))
        L.append("    against x12's 0.6728: %+.4f" % (a20 - 0.6728))
        if a20 >= 0.70:
            L.append("    -> A BIGGER BOARD RESCUES IT. RESOLVE may publish per-anchor capability claims on a board")
            L.append("       of this size, and must state the size requirement.")
        else:
            L.append("    -> NOT RESCUED. The finding is roster-independent on this corpus: %s models does not"
                     % len(models))
            L.append("       clear the bar either, so the deliverable is CLOSED rather than postponed.")

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
