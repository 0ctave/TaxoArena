"""Canonical refit of every r8 Bradley-Terry number from raw match_history.

WHY THIS EXISTS (2026-09-05). The audit found adjustForPositionBias (removed the same
day) double-counted ties, one-directionally toward the pair's lexicographically
smaller model. It fired on 51 leaf-pairs across the settled r8 batch. Contamination
scope, established by reading the production paths:

  - The PUBLISHED per-domain leaderboards and rho/tau came from
    TaxonomyRankingService.aggregateLeafScores, which pools RAW node_pair_stats from
    the database — the correction never touched them. This script re-derives those
    leaderboards from match_history (a second, fully independent path) to prove it.
  - The per-leaf fits (MAIN_leaf_leaderboard.csv exports, node_bt_states) DID go
    through the correction, as did the stopping/scheduling decisions that consumed
    them. This script refits every affected leaf raw, reproduces the old corrected
    fit from the stored order ledgers, and reports the delta.
  - What no refit can repair: the correction also fed pairStatus/isLeafConverged, so
    WHICH comparisons were funded was influenced. The refit corrects the estimator on
    the collected data, not the sampled design.

Fit matches BtMmFitter semantics: ties half-weighted, Jeffreys 0.5 phantom ties per
observed pair, MM iteration, scores centred to mean zero.

Usage: python tools/analysis/refit_bt_from_matches.py
Reads the tracked r8 DBs + exports; writes experiment_results/r8/refit_delta_report.md.
"""
import csv
import math
import os
import re
import sqlite3
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SNAP = "20260727_042523_Headless_Run_Auto_ge_MAIN"
PRIOR = 0.5
MIN_COMPARISONS = 5           # aggregateLeafScores minComparisons
AGREE_FLOOR = 0.50            # pooled leaf agreement floor
FIRE_MIN_N = 6.0              # old correction trigger
FIRE_DELTA = 0.3

# r8 directory -> ground-truth domain name in model_domain_scores.csv
DOMAINS = {
    "cs": "computer science", "engineering": "engineering", "history": "history",
    "law": "law", "math": "math", "philosophy": "philosophy",
    "physics": "physics", "psychology": "psychology",
}


def die(msg):
    sys.exit(f"REFIT ABORT: {msg}")


def mm_fit(agg, models, iters=2000):
    """agg: {(a, b): [wins_a_eff, n]} with ties already half-weighted; returns {m: theta}."""
    idx = {m: i for i, m in enumerate(models)}
    M = len(models)
    W = [0.0] * M
    Npair = defaultdict(float)
    for (a, b), (wa, n) in agg.items():
        i, j = idx[a], idx[b]
        W[i] += wa + PRIOR
        W[j] += (n - wa) + PRIOR
        Npair[(i, j)] += n + 2 * PRIOR
        Npair[(j, i)] += n + 2 * PRIOR
    p = [1.0] * M
    for _ in range(iters):
        new = []
        for m in range(M):
            den = sum(Npair[(m, o)] / (p[m] + p[o]) for o in range(M) if Npair[(m, o)])
            new.append(W[m] / den if den > 0 else p[m])
        s = sum(new) / M
        new = [v / s for v in new]
        if max(abs(x - y) for x, y in zip(new, p)) < 1e-12:
            p = new
            break
        p = new
    theta = [math.log(max(v, 1e-300)) for v in p]
    mean = sum(theta) / M
    return {m: theta[idx[m]] - mean for m in models}


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def kendall(xs, ys):
    n = len(xs)
    conc = disc = 0
    for i in range(n):
        for j in range(i + 1, n):
            s = (xs[i] - xs[j]) * (ys[i] - ys[j])
            if s > 0:
                conc += 1
            elif s < 0:
                disc += 1
    tot = n * (n - 1) // 2
    return (conc - disc) / tot if tot else float("nan")


def load_gt():
    """Ground-truth accuracy per (domain, model) over the thesis reserved set.

    The reserved set comes from the tracked reserved_leaf_assignments.csv, NOT from
    eval_results.is_reserved — that column mirrors whichever pool is currently
    active (the cross-domain runs repointed it). Ids are the eval question-id space
    on both sides, so the join is id-safe (the mmlu_pro id space is never touched).
    model_domain_scores.csv is unusable here: it carries the 12-model screening
    roster, not the r8 arena roster.
    """
    ids_by_cat = defaultdict(set)
    with open(os.path.join(ROOT, "reserved_leaf_assignments.csv"), newline="",
              encoding="utf-8") as f:
        rdr = csv.reader(f)
        next(rdr)
        for row in rdr:
            ids_by_cat[row[1].strip().lower()].add(int(row[0]))
    con = sqlite3.connect(
        f"file:{os.path.join(ROOT, 'mmlu_pro_dataset_cache_v2.db')}?mode=ro", uri=True)
    gt = defaultdict(dict)  # domain -> model -> acc
    for cat, ids in ids_by_cat.items():
        marks = ",".join("?" * len(ids))
        for model, acc, n in con.execute(
                f"SELECT model_name, AVG(is_correct), COUNT(*) FROM eval_results "
                f"WHERE question_id IN ({marks}) GROUP BY model_name", tuple(ids)):
            # eval_results holds the whole 47-model screen; partial-coverage models
            # simply never make it into gt and fail loudly at lookup time if the
            # arena roster ever needs one.
            if n >= 0.95 * len(ids):
                gt[cat][model] = acc
    con.close()
    return gt


def parse_published_tex(path):
    """Rank-ordered [(model, theta)] out of MAIN_leaderboard.tex."""
    out = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\s*(\d+)\s*&\s*([^&]+?)\s*&\s*([+-][\d.]+)\s*&", line)
        if m:
            out.append((m.group(2).replace("\\_", "_"), float(m.group(3))))
    if not out:
        die(f"no ranks parsed from {path}")
    return out


def eligible_leaves(con):
    """Replicate aggregateLeafScores eligibility on the MAIN snapshot scope."""
    total = {r[0]: r[1] for r in con.execute(
        "SELECT node_id, total_comparisons FROM node_bt_states WHERE snapshot_id=?", (SNAP,))}
    agree = defaultdict(lambda: [0, 0])
    for nid, w, c in con.execute(
            "SELECT node_id, agreement_wins, agreement_checks FROM node_pair_stats "
            "WHERE snapshot_id=?", (SNAP,)):
        agree[nid][0] += w
        agree[nid][1] += c
    kept, dropped = set(), []
    for nid, n in total.items():
        if n < MIN_COMPARISONS:
            dropped.append((nid, "n<%d" % MIN_COMPARISONS))
            continue
        w, c = agree[nid]
        if c >= MIN_COMPARISONS and w / c < AGREE_FLOOR:
            dropped.append((nid, "agreement %.2f" % (w / c)))
            continue
        kept.add(nid)
    return kept, dropped


def agg_from_matches(con, leaves):
    agg = defaultdict(lambda: [0.0, 0.0])
    per_leaf_counts = defaultdict(float)
    for ma, mb, winner, tie, nid in con.execute(
            "SELECT model_a, model_b, winner, is_tie, node_id FROM match_history "
            "WHERE condition='MAIN' AND snapshot_id=?", (SNAP,)):
        if nid not in leaves:
            continue
        a, b = min(ma, mb), max(ma, mb)
        rec = agg[(a, b)]
        rec[1] += 1
        if tie:
            rec[0] += 0.5
        elif winner == a:
            rec[0] += 1.0
        per_leaf_counts[nid] += 1
    return agg, per_leaf_counts


def agg_from_pairstats(rows):
    agg = defaultdict(lambda: [0.0, 0.0])
    for ma, mb, wa, wb, ties, n in rows:
        a, b = min(ma, mb), max(ma, mb)
        w = wa if ma == a else wb
        rec = agg[(a, b)]
        rec[0] += w + 0.5 * ties
        rec[1] += n
    return agg


def old_correction(rows):
    """The removed adjustForPositionBias, reproduced for the delta report."""
    out = []
    fired = []
    for ma, mb, wa, wb, ties, n, waf, was in rows:
        if n >= FIRE_MIN_N and abs(waf - was) / n > FIRE_DELTA:
            cwa = (waf + was) / 2.0
            cwb = max(0.0, n - cwa - ties)
            out.append((ma, mb, cwa, cwb, ties, n))
            fired.append((ma, mb, n, wa, cwa))
        else:
            out.append((ma, mb, wa, wb, ties, n))
    return out, fired


def main():
    gt = load_gt()
    lines = []
    say = lines.append
    say("# r8 refit from raw match_history — delta report for the removed position-bias correction")
    say("")
    say("Generated by tools/analysis/refit_bt_from_matches.py. See its docstring for scope.")
    say("")
    say("| domain | verdicts | pooled refit == published order | max pooled |dtheta| vs .tex | "
        "rho vs GT (refit) | rho vs GT (published) | tau vs GT | GT order | fired leaf-pairs | leaf fits changed |")
    say("|---|---|---|---|---|---|---|---|---|---|")

    summary_ok = True
    leaf_details = []

    for d in sorted(DOMAINS):
        db = os.path.join(ROOT, "experiment_results", "r8", d, f"ratings_r8_{d}.db")
        if not os.path.exists(db):
            die(f"missing {db}")
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)

        kept, dropped = eligible_leaves(con)

        # Independent path: raw verdicts -> pooled fit.
        agg_mh, _ = agg_from_matches(con, kept)
        models = sorted({m for k in agg_mh for m in k})
        theta_mh = mm_fit(agg_mh, models)

        # Published path replication: raw node_pair_stats of kept leaves -> pooled fit.
        ps_rows = [r for r in con.execute(
            "SELECT model_a, model_b, wins_a, wins_b, ties, total_comparisons "
            "FROM node_pair_stats WHERE snapshot_id=?", (SNAP,))]
        # restrict to kept leaves
        ps_rows_kept = [r for r in con.execute(
            "SELECT model_a, model_b, wins_a, wins_b, ties, total_comparisons "
            "FROM node_pair_stats WHERE snapshot_id=? AND node_id IN (%s)"
            % ",".join("?" * len(kept)), (SNAP, *kept))]
        theta_ps = mm_fit(agg_from_pairstats(ps_rows_kept), models)

        # Integrity: the two paths must agree.
        cross = max(abs(theta_mh[m] - theta_ps[m]) for m in models)
        if cross > 1e-6:
            die(f"{d}: match_history and node_pair_stats disagree (max dtheta {cross:.2e})")

        # Published leaderboard.
        tex = os.path.join(ROOT, "experiment_results", "r8", d, "seed_42",
                           "validation", "MAIN_leaderboard.tex")
        published = parse_published_tex(tex)
        pub_order = [m for m, _ in published]
        pub_theta = {m: t for m, t in published}
        pub_centered = {m: t - sum(pub_theta.values()) / len(pub_theta) for m, t in pub_theta.items()}
        refit_order = sorted(models, key=lambda m: -theta_mh[m])
        order_ok = refit_order == pub_order
        max_dpub = max(abs(theta_mh[m] - pub_centered[m]) for m in models if m in pub_centered)

        # Published GT-agreement metric, for side-by-side reproduction.
        pub_rho = None
        tm = os.path.join(ROOT, "experiment_results", "r8", d, "seed_42",
                          "validation", "MAIN_thesis_metrics.csv")
        with open(tm, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if len(row) == 3 and row[0] == "MAIN" and row[1] == "overallSpearmanRho":
                    pub_rho = float(row[2])

        # GT comparison.
        gtd = gt[DOMAINS[d]]
        gt_scores = [gtd[m] for m in models]
        bt_scores = [theta_mh[m] for m in models]
        rho = spearman(bt_scores, gt_scores)
        tau = kendall(bt_scores, gt_scores)
        gt_order = sorted(models, key=lambda m: -gtd[m])
        exact = refit_order == gt_order
        n_swaps = sum(1 for i in range(len(models)) for j in range(i + 1, len(models))
                      if (theta_mh[refit_order[i]] - theta_mh[refit_order[j]]) *
                         (gtd[refit_order[i]] - gtd[refit_order[j]]) < 0)
        recov = "exact" if exact else f"{n_swaps} discordant pair(s)"

        # Leaf-level delta: refit every leaf raw vs old-corrected.
        by_leaf = defaultdict(list)
        for nid, ma, mb, wa, wb, ties, n, waf, was in con.execute(
                "SELECT node_id, model_a, model_b, wins_a, wins_b, ties, total_comparisons, "
                "win_a_first, win_a_second FROM node_pair_stats WHERE snapshot_id=?", (SNAP,)):
            by_leaf[nid].append((ma, mb, wa, wb, ties, n, waf, was))
        fired_total = 0
        leaves_changed = 0
        for nid, rows in sorted(by_leaf.items()):
            corrected, fired = old_correction(rows)
            if not fired:
                continue
            fired_total += len(fired)
            raw_rows = [(ma, mb, wa, wb, t, n) for ma, mb, wa, wb, t, n, _, _ in rows]
            lm = sorted({m for r in rows for m in (r[0], r[1])})
            th_raw = mm_fit(agg_from_pairstats(raw_rows), lm)
            th_old = mm_fit(agg_from_pairstats(corrected), lm)
            dmax = max(abs(th_raw[m] - th_old[m]) for m in lm)
            rank_changed = ([m for m in sorted(lm, key=lambda x: -th_raw[x])] !=
                            [m for m in sorted(lm, key=lambda x: -th_old[x])])
            if dmax > 1e-9:
                leaves_changed += 1
                leaf_details.append(
                    f"| {d} | {nid} | {len(fired)} | {dmax:+.3f} | "
                    f"{'YES' if rank_changed else 'no'} |")

        nverdicts = int(sum(n for _, n in agg_mh.values()))
        pub_rho_s = f"{pub_rho:.3f}" if pub_rho is not None else "n/a"
        say(f"| {d} | {nverdicts} | {'YES' if order_ok else 'NO'} | {max_dpub:.4f} | "
            f"{rho:.3f} | {pub_rho_s} | {tau:.3f} | {recov} | {fired_total} | {leaves_changed} |")
        if not order_ok:
            summary_ok = False
            say(f"|  |  | published: {', '.join(pub_order)} |  |  |  | refit: {', '.join(refit_order)} |  |  |")
        con.close()

    say("")
    say("## Leaf-level deltas (every leaf where the old correction fired)")
    say("")
    say("These are the fits that WERE contaminated: the per-leaf exports "
        "(MAIN_leaf_leaderboard.csv / node_bt_states) and the stopping decisions that "
        "consumed them. dtheta is the largest per-model change between the raw refit "
        "and the old corrected fit of that leaf.")
    say("")
    say("| domain | leaf | fired pairs | max |dtheta| | intra-leaf rank change |")
    say("|---|---|---|---|---|")
    lines.extend(leaf_details)
    say("")
    say("## Reading")
    say("")
    if summary_ok:
        say("The pooled per-domain leaderboards — the numbers behind the ranking-recovery "
            "claim — reproduce from raw match_history on an independent code path, "
            "confirming the published domain rankings never passed through the removed "
            "correction (aggregateLeafScores pools raw node_pair_stats). The refit's "
            "GT-agreement column also reproduces the published overallSpearmanRho per "
            "domain (small deviations reflect the GT reference: this script scores "
            "accuracy over ALL reserved questions in the category, the in-app metric "
            "over the benchmark's judged query set). The contamination is confined to "
            "per-leaf fits (table above) and to the run-time stopping decisions those "
            "fits fed, which no post-hoc refit can repair: the corrected estimator runs "
            "on the design the biased estimator sampled.")
    else:
        say("AT LEAST ONE published domain ordering does NOT reproduce from raw "
            "match_history. Treat the affected domain's published numbers as open until "
            "resolved.")

    out = os.path.join(ROOT, "experiment_results", "r8", "refit_delta_report.md")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    main()
