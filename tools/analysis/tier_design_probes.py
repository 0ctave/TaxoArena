"""Two follow-ups the first four probes forced (registered 2026-09-14 in the same block, ZERO calls).

  python tools/analysis/tier_design_probes.py

TIER-HONEST   TIER-RECOVERY asked whether the judged board reproduces the KEY's gap-based tier partition and the
              answer was 0% at every coarseness and budget. That is the wrong question for a product. A tier
              should be defined by what the arena CANNOT DISTINGUISH - by the uncertainty of its own theta - not
              by a gap borrowed from the key's scale. This asks the design question instead: when the board
              tiers itself by its own confidence intervals, is it HONEST? That is, does it ever confidently
              separate two models the key ties, and does it ever tie two models the key clearly separates?

TIER-ROUTER-U TIER-ROUTER found nothing to route on MMLU-Pro: gemini is the best model in every anchor AND the
              cheapest in its own tier, so tier-then-cheapest is byte-identical to best-single. That is a
              property of this corpus, not of the idea. Re-run on the six-corpus union, where 18 models compete
              and no single one dominates.
"""
import os, sys, random, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_p8 as p8
import stack_judge as sj
import judge_free_tests as jf
import pool_guard

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "tier_design_probes.txt")
UNION_DB = os.path.join(ROOT, "multicorpus_cache_v1.db")
KEY_GAP = 0.017


def key_tiers(acc, models, gap=KEY_GAP):
    o = sorted(models, key=lambda m: -acc[m]); out = []; cur = [o[0]]
    for a, b in zip(o, o[1:]):
        if acc[a] - acc[b] < gap: cur.append(b)
        else: out.append(cur); cur = [b]
    out.append(cur); return out


def main():
    L = []
    models = sorted(p8.ARENA12)
    acc, _ = jf.gt_and_lengths(set(p8.ARENA12))
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute("SELECT model_a, model_b, winner, invalid FROM verdicts") if not r[3]]

    # ---------------- TIER-HONEST ----------------
    L.append("=== TIER-HONEST: when the board tiers itself by its OWN uncertainty, is it honest? ===")
    rng = random.Random(42)
    B = 400
    boards = []
    for _ in range(B):
        sub = [rows[rng.randrange(len(rows))] for _ in range(len(rows))]
        boards.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, w, _ in sub], models))
    point = jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, w, _ in rows], models)
    # P(A above B) over the bootstrap: the arena SEPARATES a pair when that probability clears 0.95
    sep = {}
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            p = sum(1 for t in boards if t[a] > t[b]) / B
            sep[(a, b)] = p
    kt = key_tiers(acc, models)
    tier_of = {m: i for i, t in enumerate(kt) for m in t}
    same = [(a, b) for (a, b) in sep if tier_of[a] == tier_of[b]]
    diff = [(a, b) for (a, b) in sep if tier_of[a] != tier_of[b]]
    conf = lambda p: p >= 0.95 or p <= 0.05
    wrongdir = sum(1 for (a, b) in diff if conf(sep[(a, b)]) and ((sep[(a, b)] >= 0.95) != (acc[a] > acc[b])))
    L.append("  the key's %d tiers at a %.3f gap; %d model pairs, %d within a tier, %d across tiers"
             % (len(kt), KEY_GAP, len(sep), len(same), len(diff)))
    L.append("")
    L.append("  ACROSS-TIER pairs (the key separates them):")
    L.append("    the arena separates %d of %d at 95%% confidence (%.0f%%)"
             % (sum(1 for p in diff if conf(sep[p])), len(diff), 100 * sum(1 for p in diff if conf(sep[p])) / len(diff)))
    L.append("    of those, %d point the WRONG WAY  <- these are the only real errors a tiered product can make" % wrongdir)
    L.append("  WITHIN-TIER pairs (the key ties them):")
    if same:
        L.append("    the arena separates %d of %d at 95%% confidence (%.0f%%) - overconfidence, the other failure mode"
                 % (sum(1 for p in same if conf(sep[p])), len(same), 100 * sum(1 for p in same if conf(sep[p])) / len(same)))
        for p in same:
            L.append("      %-28s vs %-28s P(first above) %.3f | key %.3f vs %.3f"
                     % (p[0][:28], p[1][:28], sep[p], acc[p[0]], acc[p[1]]))
    L.append("")
    L.append("  SELF-TIERING: group models the arena cannot separate at 95%%, reading down its own board.")
    o = sorted(models, key=lambda m: -point[m])
    groups = []; cur = [o[0]]
    for a, b in zip(o, o[1:]):
        p = sep.get((a, b), sep.get((b, a)))
        pp = p if (a, b) in sep else 1 - p
        if pp >= 0.95: groups.append(cur); cur = [b]
        else: cur.append(b)
    groups.append(cur)
    L.append("    the arena's own tiers (%d):" % len(groups))
    for i, g in enumerate(groups, 1):
        L.append("      tier %d: %s" % (i, ", ".join("%s (key %.3f)" % (m[:26], acc[m]) for m in g)))
    invs = [(x, y) for i, g in enumerate(groups) for j, h in enumerate(groups) if i < j
            for x in g for y in h if acc[y] > acc[x]]
    L.append("    cross-tier key inversions in the arena's own tiering: %d" % len(invs))
    for x, y in invs:
        L.append("      %-28s is tiered ABOVE %-28s but scores %.3f against %.3f" % (x[:28], y[:28], acc[x], acc[y]))
    L.append("    (an earlier version of this line required the inversion to exceed the 0.017 tier gap and")
    L.append("     reported 0, because the one real inversion sits EXACTLY on that threshold - corrected)")
    L.append("    READ: a tiered product is honest if it makes no confident wrong separations and its own tiers")
    L.append("    contain no key inversions. That is a far weaker demand than reproducing the key's partition,")
    L.append("    and it is the demand a cost-aware router actually places on the ranking.")

    # ---------------- TIER-ROUTER-U ----------------
    L.append("")
    L.append("=== TIER-ROUTER-U: tier-then-cheapest on the six-corpus union ===")
    try:
        con = sqlite3.connect("file:%s?mode=ro" % UNION_DB, uri=True)
        pid = pool_guard.assert_frozen_pool(con, pool_guard.UNION_POOL)   # the union pool of record, by id
        pool = {q for (q,) in con.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (pid,))}
        Q = {q: (s, d) for q, s, d in con.execute("SELECT question_id, source, domain FROM corpus_questions")}
        G = defaultdict(dict)
        for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
            G[q][m] = int(c)
        ms = sorted({m for q in G for m in G[q]})
        full = [q for q in pool if q in G and len(G[q]) == len(ms) and q in Q]
        L.append("  pool %s | %d questions with all %d models" % (pid, len(full), len(ms)))
        ov = {m: sum(G[q][m] for q in full) / len(full) for m in ms}
        best = max(ov, key=lambda m: ov[m])
        # cost proxy: parameter count parsed from the model name (billions); the union DB has no token counts
        import re
        def size(m):
            g = re.search(r"(\d+(?:\.\d+)?)[bB]\b", m)
            return float(g.group(1)) if g else 70.0
        cells = defaultdict(list)
        for q in full: cells[Q[q]].append(q)
        tot = {"best single": [0.0, 0.0], "per-cell best": [0.0, 0.0], "per-cell best TIER, smallest": [0.0, 0.0]}
        for cell, qs in cells.items():
            la = {m: sum(G[q][m] for q in qs) / len(qs) for m in ms}
            b1 = max(la, key=lambda m: la[m])
            top = key_tiers(la, ms, gap=KEY_GAP)[0]
            cheap = min(top, key=size)
            for k, m in (("best single", best), ("per-cell best", b1), ("per-cell best TIER, smallest", cheap)):
                tot[k][0] += la[m] * len(qs); tot[k][1] += size(m) * len(qs)
        n = len(full)
        L.append("  %-32s %10s %14s" % ("policy", "accuracy", "mean params B"))
        for k, (s, c) in tot.items():
            L.append("  %-32s %10.4f %14.1f" % (k, s / n, c / n))
        d = (tot["per-cell best TIER, smallest"][0] - tot["per-cell best"][0]) / n
        L.append("  tier-then-smallest against per-cell best: %+.4f accuracy at %.0f%% of the parameters"
                 % (d, 100 * tot["per-cell best TIER, smallest"][1] / max(1e-9, tot["per-cell best"][1])))
        L.append("  CAVEAT: parameter count parsed from the model name is a crude cost proxy and the union DB")
        L.append("  carries no token counts or latencies. It orders models by size, which is what a tier-then-")
        L.append("  cheapest rule needs, but it is not a price.")
    except Exception as e:
        L.append("  UNAVAILABLE: %s" % str(e)[:160])

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
