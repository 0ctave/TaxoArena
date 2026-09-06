"""R2 profile-run analysis: the model x stratum capability atlas and its registered tests.

REGISTERED PRIMARY (frozen before the R2 run; this script defines the test):
  Pooled WITHIN-ANCHOR interaction LRT over the split anchors of
  strata_profile_v1.json (anchors whose leaves the embedding geometry divided in
  two: Business, Chemistry, Economics, Engineering, Math, Other). For each split
  anchor: 2*(ll of per-stratum Bradley-Terry fits - ll of the pooled-anchor fit),
  summed over anchors. Ties half-weighted, Jeffreys 0.5 pseudo-count, likelihood on
  raw counts — the same estimator family as crossdomain_interaction_lrt.py (6433111),
  one level finer. Permutation null: stratum labels shuffled within (anchor, pair),
  NPERM = 1000, RNG seed 42, p = (1 + #{null >= observed}) / (1 + NPERM).

REGISTERED DIRECTIONAL CONTRASTS (centered: model delta minus roster-mean delta, so
stratum difficulty cancels — the quantity a per-stratum BT fit actually measures).
ADJUDICATING contrasts come only from anchors the mechanics pilot never observed:
  chemistry-1 - chemistry-2: gemini-3.1-pro_5-shots  > 0  (GT centered +0.68)
                             Meta-Llama-3_1-8B       < 0  (GT -0.66)
  economics-1 - economics-2: Meta-Llama-3_1-70B-Instruct > 0 (GT +0.50)
  math-1 - math-2:           arx_0314                > 0  (GT +0.41)
DISCLOSED, NON-ADJUDICATING (the Business strata were seen at SE~0.30 depth in the
mechanics pilot before this freeze — 2 of 3 predicted signs correct at noise-level
precision; reported for completeness, they decide nothing):
  business-1 - business-2:  gemini < 0 (GT -0.94), Llama-2-7b > 0 (GT +0.75),
                            gpt-4o < 0 (GT -0.68)

REGISTERED QUESTION (two-sided, both outcomes informative, adjudicates nothing):
  the x12 top-cluster collapse — under SE-targeted depth, do iask_pro / gemini /
  gpt-4o recover GT-direction deltas on the math-vs-law+psychology axis, or does
  the divergence persist? Recovery indicts decision-mode sampling (tie compression);
  persistence indicts the judge's view of top-tier reasoning.

Everything else this script prints (the atlas matrix, cross-axis deltas, per-model
SEs) is descriptive.

Usage: python tools/analysis/profile_atlas.py <ratings.db> [strata.json]
"""
import json
import math
import os
import random
import sqlite3
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRIOR = 0.5
NPERM = 1000
PERM_SEED = 42

REGISTERED_CONTRASTS = [
    ("Chemistry", "gemini-3.1-pro_5-shots", +1),
    ("Chemistry", "Meta-Llama-3_1-8B", -1),
    ("Economics", "Meta-Llama-3_1-70B-Instruct", +1),
    ("Math", "arx_0314", +1),
]

DISCLOSED_CONTRASTS = [   # pilot-observed; reported, never adjudicating
    ("Business", "gemini-3.1-pro_5-shots", -1),
    ("Business", "Llama-2-7b-hf", +1),
    ("Business", "gpt-4o-2024-08-06", -1),
]


def mm_fit(agg, models, iters=2000):
    idx = {m: i for i, m in enumerate(models)}
    M = len(models)
    W = [0.0] * M
    N = defaultdict(float)
    for (a, b), (wa, n) in agg.items():
        i, j = idx[a], idx[b]
        W[i] += wa + PRIOR
        W[j] += (n - wa) + PRIOR
        N[(i, j)] += n + 2 * PRIOR
        N[(j, i)] += n + 2 * PRIOR
    p = [1.0] * M
    for _ in range(iters):
        new = []
        for m in range(M):
            den = sum(N[(m, o)] / (p[m] + p[o]) for o in range(M) if N[(m, o)])
            new.append(W[m] / den if den > 0 else p[m])
        s = sum(new) / M
        new = [v / s for v in new]
        if max(abs(x - y) for x, y in zip(new, p)) < 1e-12:
            p = new
            break
        p = new
    th = [math.log(max(v, 1e-300)) for v in p]
    mean = sum(th) / M
    return {m: th[idx[m]] - mean for m in models}


def ll_of(agg, theta):
    ll = 0.0
    for (a, b), (wa, n) in agg.items():
        pa = 1.0 / (1.0 + math.exp(-(theta[a] - theta[b])))
        pa = min(max(pa, 1e-12), 1 - 1e-12)
        ll += wa * math.log(pa) + (n - wa) * math.log(1 - pa)
    return ll


def se_of(agg, theta, models):
    """Fisher-diagonal SEs with pseudo-counts — the script's registered SE definition."""
    fisher = {m: 0.0 for m in models}
    for (a, b), (wa, n) in agg.items():
        pa = 1.0 / (1.0 + math.exp(-(theta[a] - theta[b])))
        info = (n + 2 * PRIOR) * pa * (1 - pa)
        fisher[a] += info
        fisher[b] += info
    return {m: (1.0 / math.sqrt(f) if f > 0 else float("inf")) for m, f in fisher.items()}


def aggregate(rows):
    agg = defaultdict(lambda: [0.0, 0.0])
    for ma, mb, winner, tie in rows:
        a, b = min(ma, mb), max(ma, mb)
        rec = agg[(a, b)]
        rec[1] += 1
        if tie:
            rec[0] += 0.5
        elif winner == a:
            rec[0] += 1.0
    return {k: tuple(v) for k, v in agg.items()}


def main():
    db = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        ROOT, "experiment_results", "x12_profile", "ratings_x12p.db")
    strata_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        ROOT, "experiment_configs", "strata_profile_v1.json")
    spec = json.load(open(strata_path, encoding="utf-8"))
    stratum_of = {}
    anchor_of_stratum = {}
    for s in spec["strata"]:
        anchor_of_stratum[s["id"]] = s["anchor"]
        for l in s["leafIds"]:
            stratum_of[l] = s["id"]
    split_anchors = sorted({a for sid, a in anchor_of_stratum.items() if "-" in sid})

    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    raw = con.execute(
        "SELECT model_a, model_b, winner, is_tie, node_id FROM match_history "
        "WHERE condition='MAIN'").fetchall()
    con.close()
    by_stratum = defaultdict(list)
    models = set()
    for ma, mb, w, t, nid in raw:
        sid = stratum_of.get(nid)
        if sid is None:
            continue
        by_stratum[sid].append((ma, mb, w, t))
        models.update((ma, mb))
    models = sorted(models)
    print("matches: %d | strata with data: %d | models: %d"
          % (len(raw), len(by_stratum), len(models)))

    # ── The atlas ────────────────────────────────────────────────────────────────
    theta = {}
    se = {}
    for sid in sorted(by_stratum):
        agg = aggregate(by_stratum[sid])
        theta[sid] = mm_fit(agg, models)
        se[sid] = se_of(agg, theta[sid], models)
    print("\n=== Capability atlas: theta (SE) per model x stratum ===")
    strata_sorted = sorted(theta)
    header = "%-30s" % "model" + "".join("%18s" % s[:17] for s in strata_sorted)
    print(header)
    for m in models:
        row = "%-30s" % m
        for sid in strata_sorted:
            row += "%18s" % ("%+.2f(%.2f)" % (theta[sid][m], se[sid][m]))
        print(row)

    # ── Registered primary: pooled within-anchor LRT ────────────────────────────
    def anchor_lrt(rows_by_stratum_pair):
        total = 0.0
        for (rows1, rows2) in rows_by_stratum_pair:
            agg1, agg2 = aggregate(rows1), aggregate(rows2)
            pooled = aggregate(rows1 + rows2)
            th1, th2 = mm_fit(agg1, models), mm_fit(agg2, models)
            thp = mm_fit(pooled, models)
            total += 2 * (ll_of(agg1, th1) + ll_of(agg2, th2) - ll_of(pooled, thp))
        return total

    pairs_per_anchor = []
    for anchor in split_anchors:
        sids = sorted(sid for sid, a in anchor_of_stratum.items() if a == anchor)
        if len(sids) == 2 and all(s in by_stratum for s in sids):
            pairs_per_anchor.append((by_stratum[sids[0]], by_stratum[sids[1]]))
    observed = anchor_lrt(pairs_per_anchor)

    rng = random.Random(PERM_SEED)
    null = []
    for _ in range(NPERM):
        perm_pairs = []
        for rows1, rows2 in pairs_per_anchor:
            # shuffle stratum labels within (anchor, pair)
            bucket = defaultdict(list)
            for r in rows1:
                bucket[(min(r[0], r[1]), max(r[0], r[1]))].append((r, 0))
            for r in rows2:
                bucket[(min(r[0], r[1]), max(r[0], r[1]))].append((r, 1))
            p1, p2 = [], []
            for key, items in bucket.items():
                n1 = sum(1 for _, lab in items if lab == 0)
                rows = [r for r, _ in items]
                rng.shuffle(rows)
                p1.extend(rows[:n1])
                p2.extend(rows[n1:])
            perm_pairs.append((p1, p2))
        null.append(anchor_lrt(perm_pairs))
    null.sort()
    ge = sum(1 for v in null if v >= observed)
    p_perm = (1 + ge) / (1 + NPERM)
    print("\n=== REGISTERED PRIMARY: pooled within-anchor LRT over %d split anchors ==="
          % len(pairs_per_anchor))
    print("observed LRT = %.2f | null median %.2f, p95 %.2f | p_perm = %.4f"
          % (observed, null[len(null) // 2], null[int(0.95 * len(null))], p_perm))

    # ── Registered directional contrasts (centered) ─────────────────────────────
    print("\n=== REGISTERED CONTRASTS (centered delta, predicted sign) ===")
    for anchor, model, sign in REGISTERED_CONTRASTS + [("---", "", 0)] + DISCLOSED_CONTRASTS:
        if anchor == "---":
            print("  -- disclosed, non-adjudicating (Business seen in pilot) --")
            continue
        sids = sorted(sid for sid, a in anchor_of_stratum.items() if a == anchor)
        if len(sids) != 2 or any(s not in theta for s in sids):
            print("  %s / %s: strata missing" % (anchor, model))
            continue
        s1, s2 = sids
        deltas = {m: theta[s1][m] - theta[s2][m] for m in models}
        mean = sum(deltas.values()) / len(deltas)
        d = deltas[model] - mean
        cse = math.sqrt(se[s1][model] ** 2 + se[s2][model] ** 2)
        ok = (d > 0) == (sign > 0) and d != 0
        print("  %-12s %-30s pred %s  got %+.3f (+/-%.3f)  [%s]"
              % (anchor, model, "+" if sign > 0 else "-", d, cse, "SIGN OK" if ok else "SIGN WRONG"))

    # ── Registered question: top-cluster axis under SE-targeted depth ───────────
    math_s = [s for s, a in anchor_of_stratum.items() if a == "Math" and s in theta]
    lp_s = [s for s, a in anchor_of_stratum.items() if a in ("Law", "Psychology") and s in theta]
    if math_s and lp_s:
        print("\n=== REGISTERED QUESTION: delta(math - law/psych) under profile depth ===")
        print("(x12 decision-mode values in brackets; GT screen predicted the sign in parens)")
        ref = {"iask_pro": ("+0.002", "+"), "gemini-3.1-pro_5-shots": ("-0.215", "+"),
               "gpt-4o-2024-08-06": ("-0.588", "+"), "arx_0314": ("+0.548", "+"),
               "Llama-2-7b-hf": ("-0.379", "-"), "deepseek-chat-v2_5": ("+0.674", "+")}
        for m in models:
            dm = sum(theta[s][m] for s in math_s) / len(math_s) - \
                 sum(theta[s][m] for s in lp_s) / len(lp_s)
            x12, gt = ref.get(m, ("", ""))
            extra = ("   [x12 %s, GT %s]" % (x12, gt)) if x12 else ""
            print("  %-30s %+.3f%s" % (m, dm, extra))


if __name__ == "__main__":
    main()
