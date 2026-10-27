"""KEY-NOISE-CEILING — how much of the arena's remaining error is the key's own noise? (registered 2026-09-15, zero calls)

  python tools/analysis/key_noise_ceiling.py

REGISTERED TEXT (docs/judge_v2_program.md, section A, commit 60cb7f3), quoted:
  "Eighteen of the 44 wrong-direction edges on x12 and eight of the nine within-tier separations on x20 sit on
  pairs the key cannot adjudicate. That suggests the judge line has reached the point where the KEY, not the
  judge, bounds what can be measured. Test it directly: for each anchor, split the judged questions into two
  halves; the key's direction for a pair on half 1 against half 2 gives the key's OWN direction-agreement rate,
  averaged over 40 halvings. That rate is the ceiling on any judge's direction-agreement with the key at this
  support. Compare the arena's direction-agreement with the key (raw certificate, called edges) on (i) all
  edges, (ii) established edges, against the key's split-half ceiling at the same support.
  CRITERIA: (1) PRIMARY: arena direction-agreement on established edges vs the key's split-half ceiling. If
  the arena is within 2pp of the ceiling, the measurable judge line on MMLU-Pro is CLOSED and further gains
  cannot be shown on this corpus. (2) The gap on ALL edges, so the label-noise share is stated as a number.
  (3) Per-anchor: which anchors are at ceiling and which are not.
  PREDICTION: the arena is within 2pp of the ceiling on established edges overall, below it on Law and
  History, and the all-edge gap is 3-5pp. FALSIFIER: an arena more than 5pp below the ceiling on established
  edges means there is measurable judge headroom left and the "ceiling" story is wrong."

IMPLEMENTATION (constraints from the launch note, not design freedom):
  * Edges, bootstrap moments, direction labels and anchor question sets come from systematic_budget.build()
    (Mistral STACK-v2 x12 verdicts, tree bareq512_s42, 14 anchors with >= 200 verdicts, seed 42). The
    population the registration counts ("44 wrong-direction edges") is the 891 edges with key gap >= 0.02;
    the 920-edge unfiltered population is reported alongside.
  * KEY DENOMINATOR: the anchor's JUDGED questions, anchor_qs[anchor] from build() (distinct qids with a valid
    verdict routed to the anchor) - the same denominator systematic_budget.mcnemar_edge / established use.
    Halves are halves of THAT set; the key direction on a half is sign(mean_a - mean_b) over the half's keyed
    questions, exactly as build() defines the full-anchor direction. A half with a tied key (gap 0) carries
    no direction and that halving is excluded for that edge, as build() excludes gap == 0 edges.
  * 40 halvings per anchor, random.Random(SEED=42), disjoint halves (n//2 and the rest).
  * "Established" = systematic_budget.established(): exact two-sided McNemar p < 0.05 on anchor_qs.
    Every wrong-direction count is printed as wrong(established).
  * SUPPORT MATCHING: the arena's direction is measured on the full anchor, the key's self-agreement on halves.
    Both are shown. The PRIMARY uses the Spearman-Brown-adjusted ceiling: the agreement rate a is mapped to
    the sign correlation phi = 2a - 1 (the Pearson correlation of two symmetric sign variables agreeing with
    probability a), profile_reliability.sb(phi) = 2phi/(1+phi) doubles the length, and (1+PHI)/2 maps back to
    an agreement rate. Two further readings are shown as sensitivity: sb() applied to the raw rate directly
    (always higher) and a per-edge-adjusted mean.
  * The ceiling is measured on the SAME edges the arena rate is measured on (the called edges); the ceiling on
    the uncalled/all edges is also shown. This is the reading hardest on the "at ceiling" claim: called edges
    have the larger key gaps and therefore the higher key self-agreement.
  * Verdict rule for (1), on the literal wording "within 2pp of the ceiling": PASS iff -2pp <= arena - ceiling
    <= +2pp; FAIL if below -2pp (falsifier FIRES below -5pp); if the arena sits MORE THAN 2pp ABOVE the
    ceiling the instrument does not bound the arena and (1) is reported UNDETERMINED with the numbers.
"""
import os, sys, math, random, pickle, time
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
import systematic_budget as sbud
import profile_reliability as pr

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "key_noise_ceiling.txt")
SCRATCH = r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\bigpic"
REPS = 40
SEED = 42
THRESH = 0.975
GAP = 0.02
WITHIN = 0.02
FALSIFY = 0.05
EPS = 1e-9        # 'within 2pp' includes exactly 2pp; 1 - 1/50 = 0.98 is 0.97999... in float


def load_build():
    """Reuse the session's cached systematic_budget.build() if present (identical seed, deterministic), else build."""
    os.makedirs(SCRATCH, exist_ok=True)
    for name in ("mistral_build.pkl", "key_noise_ceiling_build.pkl"):
        p = os.path.join(SCRATCH, name)
        if os.path.exists(p):
            d = pickle.load(open(p, "rb"))
            if len(d["edges"]) == 920 and len(d["anchor_qs"]) == 14 and len(d["models"]) == 12:
                return d["models"], d["K"], d["P"], d["edges"], d["anchor_qs"], name
    models, K, P, by, edges, anchor_qs = sbud.build()
    d = dict(models=models, K=dict(K), P=dict(P), edges=edges, anchor_qs=anchor_qs)
    pickle.dump(d, open(os.path.join(SCRATCH, "key_noise_ceiling_build.pkl"), "wb"))
    return models, K, P, edges, anchor_qs, "built now"


def key_means(qs, K, models):
    out = {}
    for m in models:
        v = [K[q][m] for q in qs if m in K.get(q, {})]
        if v:
            out[m] = sum(v) / len(v)
    return out


def halving_table(edges, anchor_qs, K, models, reps=REPS, seed=SEED):
    """Per edge: list over halvings of +1 (halves agree), 0 (halves disagree) or None (a half is tied)."""
    cache = os.path.join(SCRATCH, "key_noise_ceiling_halvings_r%d_s%d.pkl" % (reps, seed))
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    rng = random.Random(seed)
    by_anchor = defaultdict(list)
    for i, e in enumerate(edges):
        by_anchor[e["anchor"]].append(i)
    agree = {i: [] for i in range(len(edges))}
    for anc in sorted(anchor_qs):
        qs = sorted(anchor_qs[anc])
        for _ in range(reps):
            cc = list(qs); rng.shuffle(cc)
            mid = len(cc) // 2
            m1 = key_means(cc[:mid], K, models); m2 = key_means(cc[mid:], K, models)
            for i in by_anchor[anc]:
                e = edges[i]
                if e["a"] not in m1 or e["b"] not in m1 or e["a"] not in m2 or e["b"] not in m2:
                    agree[i].append(None); continue
                d1 = m1[e["a"]] - m1[e["b"]]; d2 = m2[e["a"]] - m2[e["b"]]
                if d1 == 0 or d2 == 0:
                    agree[i].append(None)
                else:
                    agree[i].append(1 if (d1 > 0) == (d2 > 0) else 0)
    pickle.dump(agree, open(cache, "wb"))
    return agree


def edge_rate(v):
    d = [x for x in v if x is not None]
    return (sum(d) / len(d)) if d else float("nan"), len(v) - len(d)


def sb_rate(a):
    """Spearman-Brown to double length on the sign correlation phi = 2a - 1, mapped back to a rate."""
    if a != a: return float("nan")
    phi = 2 * a - 1
    if phi <= -1: return float("nan")
    return (1 + pr.sb(phi)) / 2


def ceiling(idx, agree, per_rep=False):
    """Edge-weighted split-half agreement over the edge set; optionally the per-halving aggregate too."""
    rates = []; ties = 0
    for i in idx:
        r, t = edge_rate(agree[i]); ties += t
        if r == r: rates.append(r)
    if not rates:
        return float("nan"), float("nan"), float("nan"), 0, float("nan")
    raw = sum(rates) / len(rates)
    adj = sb_rate(raw)
    per_edge_adj = sum(sb_rate(max(r, 0.5)) for r in rates) / len(rates)   # a < 0.5 is halving noise, clipped at chance
    sd = float("nan")
    if per_rep:
        reps = len(agree[idx[0]])
        vals = []
        for k in range(reps):
            xs = [agree[i][k] for i in idx if agree[i][k] is not None]
            if xs: vals.append(sum(xs) / len(xs))
        mu = sum(vals) / len(vals)
        sd = math.sqrt(sum((x - mu) ** 2 for x in vals) / (len(vals) - 1)) if len(vals) > 1 else 0.0
    return raw, adj, per_edge_adj, ties, sd


def arena_rate(idx, edges, est_ids):
    called = [i for i in idx if sbud.craw(edges[i]) >= THRESH]
    wrong = [i for i in called if not edges[i]["right"]]
    wrong_est = [i for i in wrong if i in est_ids]
    return called, wrong, wrong_est, (1 - len(wrong) / len(called)) if called else float("nan")


def pp(x):
    return "%+.2fpp" % (100 * x) if x == x else "   n/a "


def main():
    t0 = time.time()
    L = []
    models, K, P, edges, anchor_qs, src = load_build()
    L.append("=== KEY-NOISE-CEILING: is the arena's direction-agreement with the key at the key's own split-half ceiling? ===")
    L.append("  build: systematic_budget.build() (%s) | %d edges, %d with key gap >= %.2f | %d anchors | %d models"
             % (src, len(edges), sum(1 for e in edges if e["gap"] >= GAP), GAP, len(anchor_qs), len(models)))
    L.append("  KEY DENOMINATOR: the anchor's JUDGED questions (anchor_qs, %d in total, %d-%d per anchor); halves, key"
             % (sum(len(v) for v in anchor_qs.values()), min(len(v) for v in anchor_qs.values()), max(len(v) for v in anchor_qs.values())))
    L.append("  direction and McNemar all use this set. %d halvings, random.Random(%d), disjoint halves." % (REPS, SEED))
    L.append("  arena direction-agreement = share of raw-certificate calls (c_raw >= %.3f) whose direction matches the" % THRESH)
    L.append("  key's full-anchor direction. wrong counts printed as wrong(McNemar-established at 5%).")
    L.append("  SUPPORT MATCHING: raw ceiling = half-support self-agreement; SB ceiling = Spearman-Brown on phi = 2a-1")
    L.append("  (profile_reliability.sb), mapped back to a rate. THE PRIMARY USES THE SB-ADJUSTED CEILING. Both shown.")
    L.append("  The ceiling is measured on the same edges the arena rate is measured on (the called edges).")
    L.append("")

    # ---------- data check before any stratum is read ----------
    miss = sum(1 for anc in anchor_qs for q in anchor_qs[anc] for m in models if m not in K.get(q, {}))
    n_est_all = len(sbud.established(edges, K, anchor_qs))
    filt = [i for i, e in enumerate(edges) if e["gap"] >= GAP]
    L.append("  DATA CHECK: (question, model) keys missing on the judged set: %d of %d; McNemar-established edges:"
             % (miss, sum(len(v) for v in anchor_qs.values()) * len(models)))
    L.append("  %d of %d (all gaps), %d of %d (gap >= %.2f; SYSTEMATIC-BUDGET printed 809 of 891). wrong-direction edges:"
             % (n_est_all, len(edges), len([i for i in filt if sbud.mcnemar_edge(edges[i], K, anchor_qs)[0] < 0.05]), len(filt), GAP))
    wf = [i for i in filt if not edges[i]["right"]]
    L.append("  %d(%d) on the %d, %d(%d) on the %d (registration: 44, of which 18 not established)."
             % (len(wf), sum(1 for i in wf if sbud.mcnemar_edge(edges[i], K, anchor_qs)[0] < 0.05), len(filt),
                sum(1 for e in edges if not e["right"]),
                sum(1 for e in edges if not e["right"] and sbud.mcnemar_edge(e, K, anchor_qs)[0] < 0.05), len(edges)))
    L.append("")

    agree = halving_table(edges, anchor_qs, K, models)
    est_ids = {i for i, e in enumerate(edges) if sbud.mcnemar_edge(e, K, anchor_qs)[0] < 0.05}
    total_ties = sum(1 for i in agree for x in agree[i] if x is None)
    L.append("  halvings with a tied key on a half (excluded for that edge): %d of %d edge-halvings (%.2f%%)"
             % (total_ties, len(edges) * REPS, 100.0 * total_ties / (len(edges) * REPS)))
    L.append("")

    def block(title, idx):
        L.append(title)
        L.append("  %-28s %6s %9s %8s %9s %9s %9s %9s %9s" %
                 ("edge set", "n", "wrong", "arena", "ceil raw", "ceil SB", "gap raw", "gap SB", "SB(rate)"))
        res = {}
        for label, sub in (("ALL edges (uncalled too)", idx),
                           ("called, all", [i for i in idx if sbud.craw(edges[i]) >= THRESH]),
                           ("ESTABLISHED (uncalled too)", [i for i in idx if i in est_ids]),
                           ("called, established", [i for i in idx if i in est_ids and sbud.craw(edges[i]) >= THRESH])):
            if not sub:
                L.append("  %-28s %6d" % (label, 0)); continue
            raw, adj, pea, ties, sd = ceiling(sub, agree, per_rep=True)
            called = [i for i in sub if sbud.craw(edges[i]) >= THRESH]
            wrong = [i for i in called if not edges[i]["right"]]
            ar = (1 - len(wrong) / len(called)) if called else float("nan")
            direct = pr.sb(raw) if raw == raw else float("nan")
            L.append("  %-28s %6d %5d(%d) %8.4f %9.4f %9.4f %9s %9s %9.4f"
                     % (label, len(sub), len(wrong), sum(1 for i in wrong if i in est_ids), ar, raw, adj,
                        pp(ar - raw), pp(ar - adj), direct))
            res[label] = dict(n=len(sub), called=len(called), wrong=len(wrong), wrong_est=sum(1 for i in wrong if i in est_ids),
                              arena=ar, raw=raw, adj=adj, pea=pea, direct=direct, sd=sd, ties=ties)
        L.append("  (arena is always measured on the called members of the row's set; on the two 'called' rows the ceiling")
        L.append("   is on exactly those edges = the support-matched comparison. 'SB(rate)' = sb() on the raw rate directly.)")
        return res

    R = block("=== (i)/(ii) OVERALL, population = %d edges with key gap >= %.2f (the registration's 44-wrong population) ==="
              % (len(filt), GAP), filt)
    L.append("")
    R920 = block("=== sensitivity: population = all %d edges with any key gap (SYSTEMATIC-BUDGET's honest denominator) ===" % len(edges),
                 list(range(len(edges))))
    L.append("")

    ce = R["called, established"]; ca = R["called, all"]
    L.append("  halving noise on the ceiling (SD of the per-halving aggregate over %d halvings): called-all %.4f, called-established %.4f"
             % (REPS, ca["sd"], ce["sd"]))
    L.append("  per-edge SB-adjusted mean (edges below chance clipped to 0.5): called-all %.4f, called-established %.4f"
             % (ca["pea"], ce["pea"]))
    L.append("  arena SE if the %d called edges were independent: %.4f (they are not - ~66 pairs share 14 anchors)"
             % (ca["called"], math.sqrt(ca["arena"] * (1 - ca["arena"]) / ca["called"])))

    # ---------- leave-one-anchor-out jackknife on the two gaps ----------
    def gap_on(idx_set, est_only):
        sub = [i for i in idx_set if sbud.craw(edges[i]) >= THRESH and (i in est_ids or not est_only)]
        if not sub: return float("nan")
        raw, adj, _, _, _ = ceiling(sub, agree)
        ar = 1 - sum(1 for i in sub if not edges[i]["right"]) / len(sub)
        return ar - adj
    ancs = sorted(anchor_qs)
    for est_only, label in ((True, "established"), (False, "all")):
        full = gap_on(filt, est_only)
        loo = [gap_on([i for i in filt if edges[i]["anchor"] != a], est_only) for a in ancs]
        n = len(loo); mu = sum(loo) / n
        se = math.sqrt((n - 1) / n * sum((x - mu) ** 2 for x in loo))
        L.append("  leave-one-anchor-out jackknife on gap SB (%s): %+.2fpp, SE %.2fpp, 95%% [%+.2f, %+.2f]pp"
                 % (label, 100 * full, 100 * se, 100 * (full - 1.96 * se), 100 * (full + 1.96 * se)))
    L.append("")

    # ---------- per anchor ----------
    L.append("=== (3) PER ANCHOR (population gap >= %.2f; 'at ceiling' = arena >= SB ceiling - %.0fpp on called, established) ===" % (GAP, 100 * WITHIN))
    L.append("  %-16s %5s | %6s %7s %7s %8s %8s %8s | %6s %7s %7s %8s %8s %8s | %s"
             % ("anchor", "qs", "called", "wrong", "arena", "ceilraw", "ceilSB", "gapSB", "c.est", "wrong", "arena", "ceilraw", "ceilSB", "gapSB", "verdict"))
    per = {}
    for a in ancs:
        idx = [i for i in filt if edges[i]["anchor"] == a]
        ca_ = [i for i in idx if sbud.craw(edges[i]) >= THRESH]
        ce_ = [i for i in ca_ if i in est_ids]
        row = {}
        for tag, sub in (("all", ca_), ("est", ce_)):
            if not sub:
                row[tag] = None; continue
            raw, adj, _, _, _ = ceiling(sub, agree)
            wrong = [i for i in sub if not edges[i]["right"]]
            ar = 1 - len(wrong) / len(sub)
            row[tag] = dict(n=len(sub), wrong=len(wrong), wrong_est=sum(1 for i in wrong if i in est_ids), arena=ar, raw=raw, adj=adj, gap=ar - adj)
        per[a] = row
        r1, r2 = row["all"], row["est"]
        if r2 is None:
            verdict = "UNDETERMINED (0 est. calls)"
        elif r2["gap"] >= -WITHIN - EPS:
            verdict = "at ceiling" + (" (ABOVE by >2pp)" if r2["gap"] > WITHIN + EPS else "") +                       (" - ON THE 2pp BOUNDARY" if abs(r2["gap"] + WITHIN) < 1e-6 else "")
        elif r2["gap"] >= -FALSIFY - EPS:
            verdict = "BELOW (2-5pp)"
        else:
            verdict = "BELOW >5pp"
        res_1pp = 100.0 / r2["n"] if r2 else float("nan")
        L.append("  %-16s %5d | %6d %4d(%d) %7.4f %8.4f %8.4f %+7.2fpp | %6d %4d(%d) %7.4f %8.4f %8.4f %+7.2fpp | %s [1 edge = %.1fpp]"
                 % (a, len(anchor_qs[a]), r1["n"], r1["wrong"], r1["wrong_est"], r1["arena"], r1["raw"], r1["adj"], 100 * r1["gap"],
                    r2["n"], r2["wrong"], r2["wrong_est"], r2["arena"], r2["raw"], r2["adj"], 100 * r2["gap"], verdict, res_1pp))
    L.append("  NOTE: with ~50 established calls per anchor one wrong edge moves the arena by ~2pp, so a per-anchor")
    L.append("  'below by 2-5pp' is one or two edges and is reported as such, not as a powered per-anchor finding.")
    L.append("")

    # ---------- the edges the arena has backwards, with their key self-agreement ----------
    L.append("=== the called edges the key says are backwards (population gap >= %.2f), with the key's own split-half rate ===" % GAP)
    L.append("  %-16s %-42s %7s %8s %6s %10s %9s" % ("anchor", "pair", "gap", "McNemar", "est", "keyhalf a", "c_raw"))
    for i in filt:
        e = edges[i]
        if sbud.craw(e) >= THRESH and not e["right"]:
            pv, b_, c_ = sbud.mcnemar_edge(e, K, anchor_qs)
            r, t = edge_rate(agree[i])
            L.append("  %-16s %-42s %7.4f %8.4f %6s %10.3f %9.4f"
                     % (e["anchor"], "%s vs %s" % (e["a"][:19], e["b"][:19]), e["gap"], pv, "yes" if i in est_ids else "no", r, sbud.craw(e)))
    L.append("")

    # ---------- verdicts ----------
    L.append("=== REGISTERED CRITERIA ===")
    g1 = ce["arena"] - ce["adj"]; g1raw = ce["arena"] - ce["raw"]
    if g1 != g1:
        v1 = "UNDETERMINED"
    elif g1 < -FALSIFY - EPS:
        v1 = "FAIL (falsifier FIRES: > 5pp below)"
    elif g1 < -WITHIN - EPS:
        v1 = "FAIL (not within 2pp; falsifier does not fire)"
    elif g1 <= WITHIN + EPS:
        v1 = "PASS"
    else:
        v1 = "UNDETERMINED (arena sits ABOVE the ceiling by more than 2pp: the split-half rate does not bound the arena)"
    L.append("  (1) PRIMARY, established called edges (n=%d, wrong %d(%d)): arena %.4f vs ceiling SB %.4f (raw %.4f) ->"
             % (ce["called"], ce["wrong"], ce["wrong_est"], ce["arena"], ce["adj"], ce["raw"]))
    L.append("      gap %s (SB, PRIMARY) / %s (raw half-support) / %s (sb on the rate) -> %s"
             % (pp(g1), pp(g1raw), pp(ce["arena"] - ce["direct"]), v1))
    g2 = ca["arena"] - ca["adj"]; g2raw = ca["arena"] - ca["raw"]
    L.append("  (2) ALL called edges (n=%d, wrong %d(%d)): arena %.4f vs ceiling SB %.4f (raw %.4f) ->"
             % (ca["called"], ca["wrong"], ca["wrong_est"], ca["arena"], ca["adj"], ca["raw"]))
    in_pred = (-0.05 <= g2 <= -0.03)
    L.append("      gap %s (SB) / %s (raw) / %s (sb on the rate); registered prediction 3-5pp below -> %s"
             % (pp(g2), pp(g2raw), pp(ca["arena"] - ca["direct"]), "PASS (prediction met)" if in_pred else "FAIL (prediction not met)"))
    L.append("      label-noise share of the all-edge error as a number: 1 - ceiling SB = %.2fpp of key self-disagreement against"
             % (100 * (1 - ca["adj"])))
    L.append("      an arena error of %.2fpp on the same edges" % (100 * (1 - ca["arena"])))
    below = [a for a in ancs if per[a]["est"] and per[a]["est"]["gap"] < -WITHIN - EPS]
    at = [a for a in ancs if per[a]["est"] and per[a]["est"]["gap"] >= -WITHIN - EPS]
    boundary = [a for a in at if abs(per[a]["est"]["gap"] + WITHIN) < 1e-6]
    L.append("  (3) PER ANCHOR (established called, SB ceiling): at ceiling: %s" % (", ".join(at) if at else "none"))
    L.append("      below by more than 2pp: %s" % (", ".join(below) if below else "none"))
    if boundary:
        L.append("      exactly ON the 2pp boundary (one wrong established call in 50; counted 'within' on the literal wording): %s" % ", ".join(boundary))
    pred3 = ("Law" in below) and ("History" in below)
    L.append("      registered prediction 'below it on Law and History': %s (Law gap %s, History gap %s)"
             % ("PASS" if pred3 else "FAIL",
                pp(per["Law"]["est"]["gap"]) if per["Law"]["est"] else "n/a",
                pp(per["History"]["est"]["gap"]) if per["History"]["est"] else "n/a"))
    L.append("")
    L.append("  sensitivity, 920-edge population: established gap SB %s (arena %.4f, ceiling %.4f); all-edge gap SB %s (arena %.4f, ceiling %.4f)"
             % (pp(R920["called, established"]["arena"] - R920["called, established"]["adj"]), R920["called, established"]["arena"], R920["called, established"]["adj"],
                pp(R920["called, all"]["arena"] - R920["called, all"]["adj"]), R920["called, all"]["arena"], R920["called, all"]["adj"]))
    L.append("")
    L.append("  CAVEAT ON THE INSTRUMENT (recorded, not used to change the registered test): the arena and the key are both")
    L.append("  evaluated on the SAME full-anchor questions, so question-sampling noise is shared between them; a judge whose")
    L.append("  verdicts reproduced the key per question would agree with it 100%, above any split-half 'ceiling'. The")
    L.append("  split-half rate bounds agreement with an INDEPENDENT measurement of the same latent gap, not with a judge on")
    L.append("  the same questions. An arena at or above the ceiling is therefore consistent with the judge line being")
    L.append("  bounded by the key AND with the ceiling simply not being a bound; the test cannot separate these.")
    L.append("  elapsed %.0fs" % (time.time() - t0))

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
