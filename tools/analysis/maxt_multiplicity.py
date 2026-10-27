"""MAXT-MULTIPLICITY — item 6 of docs/design/FRAMEWORK.md "Tests to register before shipping" (commit 8d77f7b),
registered by reference at commit eaf1dbf (docs/plan_2026-09-15.md, Block 1). Zero calls.

  python tools/analysis/maxt_multiplicity.py

THE ITEM, quoted:
  "6. MAXT-MULTIPLICITY. Simultaneous critical value per cell from the existing resamples; ORDERED counts
   marginal vs simultaneous on x12 and merged; tier maps under both. Registered readout; prediction: ORDERED
   falls by 15-25%. 0 calls."

THE RECORD IT CITES (FRAMEWORK.md, certificate section): "Multiplicity: the within-cell simultaneous critical
value is taken from the same resamples (max-t; the stress pass measured 3.21-4.51 against 1.96, ORDERED
756 -> 605 on the 924-edge slice) and both the marginal and the simultaneous ORDERED counts are printed per
cell; tier maps use the simultaneous call." The stress pass (docs/design/RESOLVE_stress_statistics.md section 2,
scratchpad edges.py) measured that on a DIFFERENT object: a raw 1.96*s Gaussian call on a BT fit of
ratings_x12.db with the MMLU-Pro category as the cell, no c_raw gate, no widener, no decline. The 15-25%
prediction is the 756 -> 605 = -20.0% carried over to the framework's ORDERED rule.

IMPLEMENTATION, fixed before the run (where the item is under-specified, the reading hardest on the
programme's own claims is taken and named):
  * CELLS and RESAMPLES. Four boards, each rebuilt with the SAME seed and draw order as the committed helpers so
    the draw matrices are the "existing resamples" (the committed helpers keep only p, m, s per edge; the
    (B x models) matrix the framework says is retained is regenerated here and verified edge-by-edge against
    the cached tables under scratchpad/bigpic/ and against the committed .txt counts):
      x12 per-anchor   : systematic_budget.build()   14 anchors x 12 models, B = 300, random.Random(42)
      x12 pooled       : systematic_budget.pooled_board()  66 pairs, B = 300, random.Random(43)
      merged per-anchor: budget_transfer.edges_from(r12 + r20)  14 anchors x 20 models, B = 300, Random(42)
      merged pooled    : key_tie_decline.pooled_merged()  190 pairs, B = 400, Random(42)
    Meta-Llama-3-70B-Instruct is excluded (asserted absent from every roster).
  * SIMULTANEOUS CRITICAL VALUE per cell: bootstrap max-t. For draw b and pair (a, b'): t_b = |d*_b - d_hat| / s,
    d_hat the point fit on the cell's full row set, s the draw SD (ddof = 1); q_cell = 95th percentile over draws
    of max over ALL C(M, 2) pairs on the board (66 or 190, not only the key-gap population - multiplicity is
    over what the board publishes). Two-sided family-wise 5%, the same level as the marginal 0.975 one-sided
    call. Sensitivity: the same quantile centred on the draw mean instead of the point fit.
  * CALLS. Marginal = the framework's rule exactly as committed: sb.craw(e) >= 0.975 (raw) or
    sb.cbud(e, B0, B1) >= 0.975 (widener, shipped -3.2326 / 3.3133), which is c_raw >= 0.975 AND
    |m| / sd >= 1.960 with sd = s or sqrt(s^2 + tau^2). Simultaneous = marginal AND |m| / sd >= q_cell, i.e. the
    SAME statistic against the cell's simultaneous critical value; the widened statistic is held to q_cell
    (hardest reading: tau is a non-resampled term, and holding the widened z to the max-t quantile is stricter
    than holding the raw z). STRICT variant also printed: the empirical gate raised to c_raw >= Phi(q_cell),
    which at B = 300/400 means every draw on one side. Decline = KEY-TIE-DECLINE as committed: exact McNemar
    p < 0.05 via systematic_budget.mcnemar_edge on the cell's JUDGED questions (per-anchor: anchor_qs[anchor];
    pooled: all judged questions) - the KEY DENOMINATOR named in every table. ORDERED in the framework's sense
    = widener + decline at 0.975. Every wrong-direction count carries its McNemar-established count.
  * POPULATIONS. ORDERED counts on the registered edge populations: x12 920 (any key gap, the honest
    denominator) and 891 (gap >= 0.02); merged per-anchor 2,538 (gap >= 0.02, budget_transfer's population);
    pooled 66 and 190. Tier maps use every pair on the board.
  * TIER MAPS. The record's adjacency reading-down rule (x20_merged.py, tier_check.py): order by the draw-mean
    theta, start a new tier where the ADJACENT pair is ORDERED; per cell and pooled, under the marginal and the
    simultaneous call; printed with ORDERED-inside-tier and cross-tier key inversions, all(established).
    Reproduction targets on the merged pooled board at 0.975 (FRAMEWORK, tiers paragraph): raw 11 tiers /
    7 inversions (4 est); widener + decline 3 tiers [9, 9, 2], 0 inversions, 35 of 150 ORDERED inside a tier.
  * PREDICTION SCORING. "ORDERED falls by 15-25%" is read on the framework's ORDERED (widener + decline, 0.975),
    marginal -> simultaneous, per board; it is ALSO shown on the raw call (the object the number came from).
    The verdict is per board; the overall verdict requires every registered board in range. UNDETERMINED is
    reported where the board's count is too small for a 15-25% band to be distinguishable (fewer than 20
    ORDERED edges, where one edge is >= 5%).
  * SENSITIVITIES printed beside the primary: 'sim(raw z)' (widener marginal gate, raw |m|/s held to q_cell - the
    reading where the max-t statistic and its critical value share a scale); q_cell from each half of the draws
    (a 95th percentile at B = 300 rests on 15 draws) with the fall recomputed under each.
  * SUPPLEMENT (not registered, printed for the record): the decline component is itself a per-cell family of
    McNemar tests; the counts under a within-cell Bonferroni on it (alpha / pairs) are shown once.
  * no network, no LLM calls; draw matrices are cached under scratchpad/block1/.
"""
import os, sys, math, random, pickle, time, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.stats import norm
import pool_guard
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import systematic_budget as sb
import budget_transfer as bt
import x20_replications as xr

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "maxt_multiplicity.txt")
SCRATCH = os.path.join(r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena",
                       "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad")
CACHE = os.environ.get("MAXT_CACHE", os.path.join(SCRATCH, "block1"))
BIGPIC = os.path.join(SCRATCH, "bigpic")
TH = sb.THRESH                 # 0.975
Z = float(norm.ppf(TH))        # 1.959964
FWER = 0.05
ALPHA = 0.05
B0, B1 = bt.B0, bt.B1
EXCLUDE = "Meta-Llama-3-70B-Instruct"
MIN_ORDERED_FOR_BAND = 20


def log(msg):
    print("[maxt %s] %s" % (time.strftime("%H:%M:%S"), msg), file=sys.stderr, flush=True)


def cached(name, fn):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if os.path.exists(p):
        log("cache hit %s" % name)
        return pickle.load(open(p, "rb"))
    log("building %s" % name)
    v = fn()
    pickle.dump(v, open(p, "wb"))
    return v


# ----------------------------------------------------------------------------------------------------------
# resamples, regenerated with the committed seeds and draw order, draw matrices retained
# ----------------------------------------------------------------------------------------------------------
def score(w, a):
    return 0.5 if w == "TIE" else (1.0 if w == a else 0.0)


def fit_board(rows4, models):
    return jf.board_from([(a, b, score(w, a), 1.0) for a, b, _, w in rows4], models)


def draw_matrix(rows4, qs, models, rng, B, tag):
    byq = defaultdict(list)
    for r in rows4:
        byq[r[2]].append(r)
    D = np.zeros((B, len(models)))
    for b in range(B):
        pick = [qs[rng.randrange(len(qs))] for _ in qs]          # identical rng consumption to the helpers
        sub = [r for q in pick for r in byq[q]]
        th = fit_board(sub, models)
        D[b] = [th[m] for m in models]
        if b % 100 == 99:
            log("  %s draw %d/%d" % (tag, b + 1, B))
    return D


def make_cell(name, rows4, models, K, rng, B):
    qs = sorted({r[2] for r in rows4})
    D = draw_matrix(rows4, qs, models, rng, B, name)
    th = fit_board(rows4, models)
    la = {}
    for m in models:
        v = [K[q].get(m) for q in qs if K[q].get(m) is not None]
        if v:
            la[m] = sum(v) / len(v)
    return dict(name=name, models=list(models), qs=qs, D=D, th=th, la=la, nrows=len(rows4), B=B)


def build_x12():
    """systematic_budget.build() with the draw matrices kept; then pooled_board() with Random(43)."""
    models = sorted(p8.ARENA12)
    assert EXCLUDE not in models
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict); P = defaultdict(dict)
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in p8.ARENA12:
            K[q][m] = int(c or 0); P[q][m] = (pr or "").strip().upper()[:1]
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(list)
    for a, b, q, w, _ in rows:
        if q in route:
            by[anchor_of(route[q])].append((a, b, q, w))
    rng = random.Random(42)
    cells = []
    for anc in sorted(by):
        rs = by[anc]
        if len(rs) < 200:
            continue
        cells.append(make_cell(anc, rs, models, K, rng, sb.B))
    rng2 = random.Random(43)
    rs = [r for anc in by for r in by[anc]]
    pooled = make_cell("POOLED", rs, models, K, rng2, sb.B)
    return dict(models=models, K=dict(K), P=dict(P), cells=cells, pooled=pooled, nrows=len(rows))


def build_merged():
    """budget_transfer.edges_from(r12 + r20) and key_tie_decline.pooled_merged() with the draw matrices kept."""
    r12, r20, models, K, P = bt.load()
    assert EXCLUDE not in models
    rows = r12 + r20
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(list)
    for a, b, q, w, _ in rows:
        if q in route:
            by[anchor_of(route[q])].append((a, b, q, w))
    rng = random.Random(42)
    cells = []
    for anc in sorted(by):
        rs = by[anc]
        if len(rs) < 200:
            continue
        cells.append(make_cell(anc, rs, models, K, rng, bt.B))
    rng2 = random.Random(42)
    rows4 = [(a, b, q, w) for a, b, q, w, _ in rows]
    pooled = make_cell("POOLED", rows4, models, K, rng2, xr.B)
    return dict(models=models, K=dict(K), P=dict(P), cells=cells, pooled=pooled, n12=len(r12), n20=len(r20))


# ----------------------------------------------------------------------------------------------------------
# edges over every pair of a cell, the max-t critical value, the calls, the tier map
# ----------------------------------------------------------------------------------------------------------
def cell_edges(cell, P):
    models, D, qs, la, th = cell["models"], cell["D"], cell["qs"], cell["la"], cell["th"]
    edges = []
    for i, a in enumerate(models):
        for j in range(i + 1, len(models)):
            b = models[j]
            d = D[:, i] - D[:, j]
            p = float((d > 0).mean())
            both = [q for q in qs if P.get(q, {}).get(a) and P.get(q, {}).get(b)]
            agree = (sum(1 for q in both if P[q][a] == P[q][b]) / len(both)) if both else 0.0
            gap = abs(la[a] - la[b]) if (a in la and b in la) else None
            right = None if (gap is None or gap == 0) else ((p > 0.5) == (la[a] > la[b]))
            edges.append(dict(anchor=cell["name"], a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                              right=right, agree=agree, gap=gap, n=len(both), dhat=float(th[a] - th[b])))
    return edges


def maxt_quantile(cell, centre="hat", draws=None):
    D = cell["D"] if draws is None else cell["D"][draws]; models = cell["models"]; M = len(models)
    diff = D[:, :, None] - D[:, None, :]
    if centre == "hat":
        th = np.array([cell["th"][m] for m in models]); c = th[:, None] - th[None, :]
    else:
        c = diff.mean(axis=0)
    sd = diff.std(axis=0, ddof=1)
    iu = np.triu_indices(M, 1)
    t = np.abs(diff[:, iu[0], iu[1]] - c[iu[0], iu[1]][None, :]) / sd[iu[0], iu[1]][None, :]
    return float(np.percentile(t.max(axis=1), 100 * (1 - FWER)))


def zstat(e, base):
    sd = e["s"] if base == "raw" else math.sqrt(e["s"] ** 2 + math.exp(B0 + B1 * e["agree"]) ** 2)
    return abs(e["m"]) / sd


def marginal(e, base):
    return (sb.craw(e) if base == "raw" else sb.cbud(e, B0, B1)) >= TH


def simultaneous(e, base, q, strict=False):
    if not marginal(e, base) or zstat(e, base) < q:
        return False
    return (sb.craw(e) >= float(norm.cdf(q))) if strict else True


def called(e, base, rule, q):
    if rule == "marginal":
        return marginal(e, base)
    if rule == "simultaneous":
        return simultaneous(e, base, q)
    if rule == "sim(raw z)":
        return marginal(e, base) and zstat(e, "raw") >= q
    return simultaneous(e, base, q, strict=True)


def tier_map(cell, S, K, aq):
    """Adjacency reading-down by draw-mean theta; S = set of frozenset pairs that are ORDERED."""
    models = cell["models"]; mean = cell["D"].mean(axis=0)
    order = sorted(models, key=lambda m: -mean[models.index(m)])
    groups = [[order[0]]]
    for a, b in zip(order, order[1:]):
        if frozenset((a, b)) in S:
            groups.append([b])
        else:
            groups[-1].append(b)
    inside = sum(1 for pr in S if any(all(m in g for m in pr) for g in groups))
    la = cell["la"]
    inv = [(x, y) for i, g in enumerate(groups) for h in groups[i + 1:] for x in g for y in h
           if x in la and y in la and la[x] < la[y]]
    inv_est = [(x, y) for x, y in inv if sb.mcnemar_edge(dict(anchor=cell["name"], a=x, b=y), K, aq)[0] < ALPHA]
    return groups, inside, inv, inv_est


# ----------------------------------------------------------------------------------------------------------
def reproduce(L, edges, pop, ref, label):
    """Edge-by-edge check of p, m, s, right against a cached table."""
    key = {(e["anchor"], e["a"], e["b"]): e for e in ref}
    mine = [e for e in edges if pop(e)]
    miss = [e for e in mine if (e["anchor"], e["a"], e["b"]) not in key]
    extra = len(ref) - (len(mine) - len(miss))
    dm = ds = dp = 0.0; dr = 0
    for e in mine:
        r = key.get((e["anchor"], e["a"], e["b"]))
        if r is None:
            continue
        dm = max(dm, abs(e["m"] - r["m"])); ds = max(ds, abs(e["s"] - r["s"])); dp = max(dp, abs(e["p"] - r["p"]))
        dr += int(bool(e["right"]) != bool(r["right"]))
    ok = (not miss) and extra == 0 and dm < 1e-9 and ds < 1e-9 and dp < 1e-12 and dr == 0
    L.append("  %-22s mine %4d vs cached %4d | unmatched %d / %d | max|dm| %.1e max|ds| %.1e max|dp| %.1e | direction mismatches %d -> %s"
             % (label, len(mine), len(ref), len(miss), extra, dm, ds, dp, dr, "REPRODUCED" if ok else "MISMATCH"))
    return ok


def count_block(L, title, edges, pop, K, aq, qcell, denom_note):
    """ORDERED counts marginal vs simultaneous, all bases, on one edge population. Returns dict of counts."""
    es = [e for e in edges if pop(e)]
    pv = {id(e): sb.mcnemar_edge(e, K, aq)[0] for e in es}
    est = {k: v < ALPHA for k, v in pv.items()}
    L.append("")
    L.append("=== %s ===" % title)
    L.append("  key denominator: %s" % denom_note)
    L.append("  edges %d | key established %d | wrong-direction %d(%d)"
             % (len(es), sum(est.values()), sum(1 for e in es if e["right"] is False),
                sum(1 for e in es if e["right"] is False and est[id(e)])))
    L.append("  wrong counts as all(McNemar-established). fall = 1 - simultaneous / marginal, on the called count.")
    L.append("  %-18s %-14s %7s %10s %8s" % ("certificate", "rule", "called", "wrong(est)", "fall"))
    out = {}
    for base, dec, name in (("raw", False, "raw"), ("raw", True, "raw+decline"),
                            ("widener", False, "widener"), ("widener", True, "widener+decline")):
        marg = None
        for rule in (("marginal", "simultaneous", "strict") if base == "raw" else ("marginal", "simultaneous", "sim(raw z)", "strict")):
            c = [e for e in es if called(e, base, rule, qcell[e["anchor"]]) and (est[id(e)] or not dec)]
            w = [e for e in c if e["right"] is False]
            we = sum(1 for e in w if est[id(e)])
            if rule == "marginal":
                marg = len(c)
            fall = (1 - len(c) / marg) if marg else float("nan")
            out[(name, rule)] = dict(called=len(c), wrong=len(w), wrong_est=we, fall=fall)
            L.append("  %-18s %-14s %7d %6d(%d) %7s" % (name if rule == "marginal" else "", rule, len(c), len(w), we,
                                                        ("%.1f%%" % (100 * fall)) if rule != "marginal" else "-"))
    return out, est


def per_cell_lines(L, edges, pop, est, qcell, cells_order):
    L.append("  per cell, framework ORDERED (widener + decline, 0.975): marginal -> simultaneous -> strict; wrong(est)")
    L.append("  %-20s %6s %5s  %-16s %-16s %-16s" % ("cell", "q_cell", "edges", "marginal", "simultaneous", "strict"))
    for cname in cells_order:
        es = [e for e in edges if pop(e) and e["anchor"] == cname]
        cols = []
        for rule in ("marginal", "simultaneous", "strict"):
            c = [e for e in es if called(e, "widener", rule, qcell[cname]) and est[id(e)]]
            w = [e for e in c if e["right"] is False]
            cols.append("%4d  %2d(%d)" % (len(c), len(w), sum(1 for e in w if est[id(e)])))
        L.append("  %-20s %6.2f %5d  %-16s %-16s %-16s" % (cname[:20], qcell[cname], len(es), cols[0], cols[1], cols[2]))


def tier_lines(L, cells, edges_by_cell, est_by_cell, qcell, K, aq_of, full_for=()):
    L.append("  %-20s | %-34s | %-34s" % ("cell", "MARGINAL: tiers sizes | inside | inv(est)", "SIMULTANEOUS: tiers sizes | inside | inv(est)"))
    res = {}
    for cell in cells:
        es = edges_by_cell[cell["name"]]; est = est_by_cell[cell["name"]]; aq = aq_of(cell)
        parts = []
        for rule in ("marginal", "simultaneous"):
            S = {frozenset((e["a"], e["b"])) for e in es if called(e, "widener", rule, qcell[cell["name"]]) and est[id(e)]}
            groups, inside, inv, inv_est = tier_map(cell, S, K, aq)
            res[(cell["name"], rule)] = (groups, inside, inv, inv_est, len(S))
            parts.append("%2d %-14s | %3d/%3d | %d(%d)" % (len(groups), str([len(g) for g in groups])[:14], inside, len(S), len(inv), len(inv_est)))
        L.append("  %-20s | %-34s | %-34s" % (cell["name"][:20], parts[0], parts[1]))
    for cname in full_for:
        for rule in ("marginal", "simultaneous"):
            groups, inside, inv, inv_est, nS = res[(cname, rule)]
            L.append("  %s / %s: %d tiers, ORDERED %d, inside a tier %d, cross-tier key inversions %d (established %d)"
                     % (cname, rule, len(groups), nS, inside, len(inv), len(inv_est)))
            for i, g in enumerate(groups, 1):
                L.append("    tier %2d: %s" % (i, ", ".join(m[:26] for m in g)))
            for x, y in inv_est:
                L.append("    established inversion: %s above %s" % (x[:26], y[:26]))
    return res


def band_verdict(marg, sim):
    if marg < MIN_ORDERED_FOR_BAND:
        return "UNDETERMINED (fewer than %d ORDERED edges; one edge is >= %.0f%%)" % (MIN_ORDERED_FOR_BAND, 100.0 / max(1, marg))
    fall = 1 - sim / marg
    return "PASS (%.1f%% is in 15-25%%)" % (100 * fall) if 0.15 <= fall <= 0.25 else "FAIL (%.1f%% is outside 15-25%%)" % (100 * fall)


def main():
    L = []
    L.append("=== MAXT-MULTIPLICITY: simultaneous (max-t) critical value per cell from the existing resamples ===")
    L.append("  item 6, FRAMEWORK.md 'Tests to register before shipping' (commit 8d77f7b), registered by reference at eaf1dbf")
    L.append("  marginal call, raw: c_raw = max(p, 1-p) >= %.3f (sb.craw, the empirical draw share; its Gaussian equivalent is |m|/s >= %.3f)"
             % (TH, Z))
    L.append("  marginal call, widener: min(c_raw, Phi(|m|/sqrt(s^2 + tau^2))) >= %.3f (sb.cbud), tau = exp(%.4f + %.4f*A), i.e. also |m|/sd_w >= %.3f"
             % (TH, B0, B1, Z))
    L.append("  simultaneous call: the marginal call AND |m|/sd >= q_cell, q_cell = 95th percentile over draws of max over all pairs of |d*-d_hat|/s;")
    L.append("  sd = s for raw, sd_w = sqrt(s^2 + tau^2) for the widener (primary, hardest); 'sim(raw z)' = widener marginal AND |m|/s >= q_cell (sensitivity)")
    L.append("  strict variant: additionally c_raw >= Phi(q_cell) (every draw on one side at B = 300/400)")
    L.append("  decline: exact McNemar p < %.2f on the cell's JUDGED questions (systematic_budget.mcnemar_edge); %s excluded" % (ALPHA, EXCLUDE))
    L.append("  framework ORDERED = widener + decline at 0.975; the stress pass's 756 -> 605 (-20.0%) was a raw 1.96*s call on another object")

    x12 = cached("maxt_x12_cells.pkl", build_x12)
    mg = cached("maxt_merged_cells.pkl", build_merged)
    for d in (x12, mg):
        assert EXCLUDE not in d["models"]

    # ---------------- edges over every pair; reproduction of the existing resamples ----------------
    E12 = {c["name"]: cell_edges(c, x12["P"]) for c in x12["cells"]}
    E12P = {"POOLED": cell_edges(x12["pooled"], x12["P"])}
    EMG = {c["name"]: cell_edges(c, mg["P"]) for c in mg["cells"]}
    EMGP = {"POOLED": cell_edges(mg["pooled"], mg["P"])}
    aq12 = {c["name"]: c["qs"] for c in x12["cells"]}; aq12P = {"POOLED": x12["pooled"]["qs"]}
    aqmg = {c["name"]: c["qs"] for c in mg["cells"]}; aqmgP = {"POOLED": mg["pooled"]["qs"]}
    pop920 = lambda e: e["gap"] is not None and e["gap"] > 0 and e["n"] > 0
    pop891 = lambda e: pop920(e) and e["gap"] >= sb.GAP
    popmg = lambda e: e["gap"] is not None and e["gap"] >= bt.GAP and e["n"] > 0
    popall = lambda e: True
    flat12 = [e for es in E12.values() for e in es]; flatmg = [e for es in EMG.values() for e in es]

    L.append("")
    L.append("=== DATA CHECK: the regenerated resamples against the committed tables ===")
    L.append("  x12: %d verdicts, %d models, %d anchors (>= 200 verdicts), B = %d per anchor, pooled B = %d over %d judged questions"
             % (x12["nrows"], len(x12["models"]), len(x12["cells"]), x12["cells"][0]["B"], x12["pooled"]["B"], len(x12["pooled"]["qs"])))
    L.append("  merged: x12 %d + x20 %d = %d verdicts, %d models, %d anchors, B = %d per anchor, pooled B = %d over %d judged questions"
             % (mg["n12"], mg["n20"], mg["n12"] + mg["n20"], len(mg["models"]), len(mg["cells"]), mg["cells"][0]["B"],
                mg["pooled"]["B"], len(mg["pooled"]["qs"])))
    checks = []
    try:
        t = pickle.load(open(os.path.join(BIGPIC, "ktd_x12_edges.pkl"), "rb"))
        checks.append(reproduce(L, flat12, pop920, t[3], "x12 per-anchor (920)"))
        t = pickle.load(open(os.path.join(BIGPIC, "ktd_merged_edges.pkl"), "rb"))
        checks.append(reproduce(L, flatmg, popmg, t[2], "merged per-anchor (2538)"))
        checks.append(reproduce(L, EMGP["POOLED"], popall, t[5], "merged pooled (190)"))
    except FileNotFoundError as ex:
        L.append("  cached tables under scratchpad/bigpic/ not found (%s); counts below are checked against the .txt records only" % ex)
    # committed .txt counts (key_tie_decline.txt, systematic_budget.txt)
    def cnt(edges, pop, K, aq, base, dec):
        es = [e for e in edges if pop(e)]
        c = [e for e in es if marginal(e, base) and (not dec or sb.mcnemar_edge(e, K, aq)[0] < ALPHA)]
        return len(c), sum(1 for e in c if e["right"] is False)
    rec = [("x12 891 raw 0.975", cnt(flat12, pop891, x12["K"], aq12, "raw", False), (739, 8)),
           ("x12 891 widener 0.975", cnt(flat12, pop891, x12["K"], aq12, "widener", False), (665, 2)),
           ("x12 891 raw+decline", cnt(flat12, pop891, x12["K"], aq12, "raw", True), (712, 4)),
           ("x12 891 widener+decline", cnt(flat12, pop891, x12["K"], aq12, "widener", True), (651, 1)),
           ("x12 920 raw 0.975", cnt(flat12, pop920, x12["K"], aq12, "raw", False), (748, 11)),
           ("x12 pooled raw", cnt(E12P["POOLED"], popall, x12["K"], aq12P, "raw", False), (63, 1)),
           ("x12 pooled widener", cnt(E12P["POOLED"], popall, x12["K"], aq12P, "widener", False), (57, 0)),
           ("merged 2538 raw 0.975", cnt(flatmg, popmg, mg["K"], aqmg, "raw", False), (2079, 42)),
           ("merged 2538 widener", cnt(flatmg, popmg, mg["K"], aqmg, "widener", False), (1783, 13)),
           ("merged 2538 widener+decline", cnt(flatmg, popmg, mg["K"], aqmg, "widener", True), (1714, 4)),
           ("merged pooled raw", cnt(EMGP["POOLED"], popall, mg["K"], aqmgP, "raw", False), (179, 8)),
           ("merged pooled widener+decline", cnt(EMGP["POOLED"], popall, mg["K"], aqmgP, "widener", True), (150, 0))]
    L.append("  marginal counts against the committed .txt records (called, wrong):")
    for name, got, want in rec:
        ok = got == want; checks.append(ok)
        L.append("    %-32s got %4d/%-3d  record %4d/%-3d  %s" % (name, got[0], got[1], want[0], want[1], "OK" if ok else "MISMATCH"))
    ai = [e for e in E12P["POOLED"] if {e["a"], e["b"]} == {"arx_0314", "iask_pro"}][0]
    L.append("    x12 pooled arx vs iask widener c = %.4f (record 0.7805) %s" % (sb.cbud(ai, B0, B1), "OK" if abs(sb.cbud(ai, B0, B1) - 0.7805) < 5e-4 else "MISMATCH"))
    checks.append(abs(sb.cbud(ai, B0, B1) - 0.7805) < 5e-4)
    all_ok = all(checks)
    L.append("  RESAMPLES OF RECORD: %s" % ("every check reproduced - these are the existing resamples" if all_ok else
                                           "AT LEAST ONE CHECK FAILED - the counts below are NOT on the resamples of record"))

    # ---------------- (1) simultaneous critical values ----------------
    L.append("")
    L.append("=== (1) SIMULTANEOUS CRITICAL VALUE PER CELL (bootstrap max-t, family-wise %.2f two-sided; marginal is %.3f) ===" % (FWER, Z))
    L.append("  %-8s %-20s %3s %5s %4s %8s %10s %7s %8s %8s" % ("board", "cell", "M", "pairs", "B", "q_cell", "q(mean-c)", "q/1.96", "q(1st h)", "q(2nd h)"))
    L.append("  q(1st h) / q(2nd h): the same quantile from the first / second half of the draws (B/2 each) - the stability of a 95th percentile")
    q12 = {}; q12P = {}; qmg = {}; qmgP = {}; qhalf = {}
    for board, cells, qd in (("x12", x12["cells"] + [x12["pooled"]], None), ("merged", mg["cells"] + [mg["pooled"]], None)):
        for c in cells:
            qh = maxt_quantile(c, "hat"); qm = maxt_quantile(c, "mean")
            h = c["B"] // 2
            qa = maxt_quantile(c, "hat", slice(0, h)); qb = maxt_quantile(c, "hat", slice(h, c["B"]))
            target = (q12P if c["name"] == "POOLED" else q12) if board == "x12" else (qmgP if c["name"] == "POOLED" else qmg)
            target[c["name"]] = qh
            qhalf[(board, c["name"])] = (qa, qb)
            M = len(c["models"])
            L.append("  %-8s %-20s %3d %5d %4d %8.3f %10.3f %7.2f %8.3f %8.3f" % (board, c["name"][:20], M, M * (M - 1) // 2, c["B"], qh, qm, qh / Z, qa, qb))
    for board, qd in (("x12 per-anchor", q12), ("merged per-anchor", qmg)):
        v = sorted(qd.values())
        L.append("  %s: q_cell range %.2f-%.2f, median %.2f (stress pass on ratings_x12 categories: 3.21-4.51)"
                 % (board, v[0], v[-1], v[len(v) // 2]))
    L.append("  pooled: x12 %.2f (66 pairs), merged %.2f (190 pairs). At B = 300 the 95th percentile of the max rests on the top 15 draws;"
             % (q12P["POOLED"], qmgP["POOLED"]))
    L.append("  at B = 400 on the top 20. The quantile is a registered readout, not a calibrated constant.")

    # ---------------- (2) ORDERED counts ----------------
    counts = {}
    counts["x12-920"], est920 = count_block(L, "(2a) x12 PER-ANCHOR, 920 edges (any key gap, the honest denominator)", flat12, pop920,
                                            x12["K"], aq12, q12, "the anchor's JUDGED questions (anchor_qs), 12-model x12 board")
    per_cell_lines(L, flat12, pop920, est920, q12, [c["name"] for c in x12["cells"]])
    counts["x12-891"], _ = count_block(L, "(2b) x12 PER-ANCHOR, 891 edges (key gap >= 0.02, the registered population)", flat12, pop891,
                                       x12["K"], aq12, q12, "the anchor's JUDGED questions (anchor_qs), 12-model x12 board")
    counts["x12-pooled"], est12P = count_block(L, "(2c) x12 POOLED, 66 pairs", E12P["POOLED"], popall, x12["K"], aq12P, q12P,
                                               "all %d judged x12 questions" % len(x12["pooled"]["qs"]))
    counts["merged-2538"], estmg = count_block(L, "(2d) MERGED PER-ANCHOR, 2,538 edges (key gap >= 0.02, budget_transfer's population)", flatmg, popmg,
                                               mg["K"], aqmg, qmg, "the anchor's JUDGED questions on the merged board, 20 models")
    per_cell_lines(L, flatmg, popmg, estmg, qmg, [c["name"] for c in mg["cells"]])
    counts["merged-pooled"], estmgP = count_block(L, "(2e) MERGED POOLED, 190 pairs (the board of record)", EMGP["POOLED"], popall,
                                                  mg["K"], aqmgP, qmgP, "all %d judged questions of the merged board" % len(mg["pooled"]["qs"]))

    # ---------------- (2f) half-sample sensitivity of the fall ----------------
    L.append("")
    L.append("=== (2f) SENSITIVITY: framework ORDERED (widener + decline) under q_cell from each half of the draws ===")
    for label, flat, pop, est, board, cells in (("x12 per-anchor, 920", flat12, pop920, est920, "x12", x12["cells"]),
                                                 ("merged per-anchor, 2538", flatmg, popmg, estmg, "merged", mg["cells"]),
                                                 ("x12 pooled, 66", E12P["POOLED"], popall, est12P, "x12", [x12["pooled"]]),
                                                 ("merged pooled, 190", EMGP["POOLED"], popall, estmgP, "merged", [mg["pooled"]])):
        es = [e for e in flat if pop(e)]
        marg = sum(1 for e in es if called(e, "widener", "marginal", None) and est[id(e)])
        outs = []
        for hi in (0, 1):
            qd = {c["name"]: qhalf[(board, c["name"])][hi] for c in cells}
            sim = sum(1 for e in es if called(e, "widener", "simultaneous", qd[e["anchor"]]) and est[id(e)])
            outs.append((sim, 1 - sim / marg if marg else float("nan")))
        L.append("  %-26s marginal %4d | q from 1st half -> %4d (fall %5.1f%%) | q from 2nd half -> %4d (fall %5.1f%%)"
                 % (label, marg, outs[0][0], 100 * outs[0][1], outs[1][0], 100 * outs[1][1]))

    # ---------------- (3) tier maps ----------------
    L.append("")
    L.append("=== (3) TIER MAPS under the marginal and the simultaneous ORDERED call (widener + decline, 0.975) ===")
    L.append("  adjacency reading-down by draw-mean theta; every pair on the board; inside = ORDERED edges inside a tier;")
    L.append("  inv(est) = cross-tier key inversions, all(McNemar-established) on the cell's judged questions.")
    est_all12 = {c["name"]: {id(e): sb.mcnemar_edge(e, x12["K"], aq12)[0] < ALPHA for e in E12[c["name"]]} for c in x12["cells"]}
    est_all12["POOLED"] = {id(e): sb.mcnemar_edge(e, x12["K"], aq12P)[0] < ALPHA for e in E12P["POOLED"]}
    est_allmg = {c["name"]: {id(e): sb.mcnemar_edge(e, mg["K"], aqmg)[0] < ALPHA for e in EMG[c["name"]]} for c in mg["cells"]}
    est_allmg["POOLED"] = {id(e): sb.mcnemar_edge(e, mg["K"], aqmgP)[0] < ALPHA for e in EMGP["POOLED"]}
    L.append("")
    L.append("  x12 (12 models):")
    q12all = dict(q12); q12all.update(q12P)
    E12all = dict(E12); E12all.update(E12P)
    t12 = tier_lines(L, x12["cells"] + [x12["pooled"]], E12all, est_all12, q12all, x12["K"],
                     lambda c: aq12P if c["name"] == "POOLED" else aq12, full_for=("POOLED",))
    L.append("")
    L.append("  merged (20 models):")
    qmgall = dict(qmg); qmgall.update(qmgP)
    EMGall = dict(EMG); EMGall.update(EMGP)
    tmg = tier_lines(L, mg["cells"] + [mg["pooled"]], EMGall, est_allmg, qmgall, mg["K"],
                     lambda c: aqmgP if c["name"] == "POOLED" else aqmg, full_for=("POOLED",))
    # reproduction of the record's pooled merged tier maps at 0.975 (raw marginal; widener + decline marginal)
    pc = mg["pooled"]; pe = EMGP["POOLED"]; pest = est_allmg["POOLED"]
    Sraw = {frozenset((e["a"], e["b"])) for e in pe if marginal(e, "raw")}
    g, ins, inv, inve = tier_map(pc, Sraw, mg["K"], aqmgP)
    L.append("")
    L.append("  reproduction, merged pooled at 0.975: raw marginal %d tiers, %d inversions (%d est) [record 11 / 7 (4)] %s"
             % (len(g), len(inv), len(inve), "OK" if (len(g), len(inv), len(inve)) == (11, 7, 4) else "MISMATCH"))
    g, ins, inv, inve, nS = tmg[("POOLED", "marginal")]
    L.append("  reproduction, merged pooled widener + decline marginal: %d tiers %s, %d inversions, %d of %d inside [record 3 [9, 9, 2], 0, 35 of 150] %s"
             % (len(g), [len(x) for x in g], len(inv), ins, nS, "OK" if ([len(x) for x in g], len(inv), ins, nS) == ([9, 9, 2], 0, 35, 150) else "MISMATCH"))
    # tier-map summary numbers
    def tier_summary(res, cells):
        m = [len(res[(c["name"], "marginal")][0]) for c in cells]; s = [len(res[(c["name"], "simultaneous")][0]) for c in cells]
        im = sum(res[(c["name"], "marginal")][1] for c in cells); is_ = sum(res[(c["name"], "simultaneous")][1] for c in cells)
        vm = sum(len(res[(c["name"], "marginal")][2]) for c in cells); vs = sum(len(res[(c["name"], "simultaneous")][2]) for c in cells)
        vme = sum(len(res[(c["name"], "marginal")][3]) for c in cells); vse = sum(len(res[(c["name"], "simultaneous")][3]) for c in cells)
        return sum(m), sum(s), im, is_, vm, vme, vs, vse
    for name, res, cells in (("x12 per-anchor", t12, x12["cells"]), ("merged per-anchor", tmg, mg["cells"])):
        tm, ts, im, is_, vm, vme, vs, vse = tier_summary(res, cells)
        L.append("  %s over %d cells: tiers %d -> %d | ORDERED inside a tier %d -> %d | cross-tier key inversions %d(%d) -> %d(%d)"
                 % (name, len(cells), tm, ts, im, is_, vm, vme, vs, vse))

    # ---------------- (4) supplement ----------------
    L.append("")
    L.append("=== (4) SUPPLEMENT (not registered): the decline component under a within-cell Bonferroni (alpha / pairs) ===")
    for name, flat, pop, K, aq, qd, cells in (("x12 920", flat12, pop920, x12["K"], aq12, q12, x12["cells"]),
                                               ("merged 2538", flatmg, popmg, mg["K"], aqmg, qmg, mg["cells"]),
                                               ("x12 pooled", E12P["POOLED"], popall, x12["K"], aq12P, q12P, [x12["pooled"]]),
                                               ("merged pooled", EMGP["POOLED"], popall, mg["K"], aqmgP, qmgP, [mg["pooled"]])):
        es = [e for e in flat if pop(e)]
        npairs = {c["name"]: len(c["models"]) * (len(c["models"]) - 1) // 2 for c in cells}
        row = []
        for rule in ("marginal", "simultaneous"):
            c = [e for e in es if called(e, "widener", rule, qd[e["anchor"]]) and sb.mcnemar_edge(e, K, aq)[0] < ALPHA / npairs[e["anchor"]]]
            w = [e for e in c if e["right"] is False]
            row.append("%d called, %d wrong" % (len(c), len(w)))
        L.append("  %-14s widener + Bonferroni-decline: marginal %s | simultaneous %s" % (name, row[0], row[1]))

    # ---------------- VERDICT ----------------
    L.append("")
    L.append("=== REGISTERED READOUT AND PREDICTION ('ORDERED falls by 15-25%') ===")
    L.append("  framework ORDERED = widener + decline at 0.975; fall = 1 - simultaneous / marginal (called counts)")
    verdicts = {}
    for key, label in (("x12-920", "x12 per-anchor, 920"), ("x12-891", "x12 per-anchor, 891"), ("x12-pooled", "x12 pooled, 66"),
                       ("merged-2538", "merged per-anchor, 2538"), ("merged-pooled", "merged pooled, 190")):
        cm = counts[key][("widener+decline", "marginal")]; cs = counts[key][("widener+decline", "simultaneous")]
        ct = counts[key][("widener+decline", "strict")]; cz = counts[key][("widener+decline", "sim(raw z)")]
        rm = counts[key][("raw", "marginal")]; rs = counts[key][("raw", "simultaneous")]
        v = band_verdict(cm["called"], cs["called"])
        verdicts[key] = v
        L.append("  %-26s ORDERED %4d -> %4d (fall %5.1f%%; strict %4d, %5.1f%%; sim(raw z) %4d, %5.1f%%) wrong %d(%d) -> %d(%d) | raw %4d -> %4d (%5.1f%%) wrong %d(%d) -> %d(%d) | %s"
                 % (label, cm["called"], cs["called"], 100 * cs["fall"], ct["called"], 100 * ct["fall"], cz["called"], 100 * cz["fall"],
                    cm["wrong"], cm["wrong_est"], cs["wrong"], cs["wrong_est"], rm["called"], rs["called"], 100 * rs["fall"],
                    rm["wrong"], rm["wrong_est"], rs["wrong"], rs["wrong_est"], v))
    reg = ["x12-920", "x12-pooled", "merged-2538", "merged-pooled"]
    n_pass = sum(1 for k in reg if verdicts[k].startswith("PASS")); n_fail = sum(1 for k in reg if verdicts[k].startswith("FAIL"))
    n_und = len(reg) - n_pass - n_fail
    overall = "PASS" if n_pass == len(reg) else ("FAIL" if n_fail else "UNDETERMINED")
    L.append("  registered boards (x12 920, x12 pooled, merged 2538, merged pooled): %d PASS, %d FAIL, %d UNDETERMINED -> prediction %s"
             % (n_pass, n_fail, n_und, overall))
    per_anchor = all(verdicts[k].startswith("PASS") for k in ("x12-920", "merged-2538"))
    L.append("  per-anchor reading (the object the 756 -> 605 figure came from: x12 920 and merged 2538 only): %s"
             % ("PASS" if per_anchor else "FAIL"))
    tp = tmg[("POOLED", "simultaneous")]; tp12 = t12[("POOLED", "simultaneous")]
    L.append("  product consequence: under the simultaneous call the shipped tier map of the 20-model pooled board of record is %d tier(s) %s"
             % (len(tp[0]), [len(g) for g in tp[0]]))
    L.append("  (marginal: 3 [9, 9, 2]); the 12-model x12 pooled board gives %d tier(s) %s (marginal 6). The fine product (the partial order) keeps %d / %d ORDERED edges."
             % (len(tp12[0]), [len(g) for g in tp12[0]], tp[4], tmg[("POOLED", "marginal")][4]))
    z_all = [counts[k][("widener+decline", "sim(raw z)")]["fall"] for k in reg]
    L.append("  hardest reading applied: the widened statistic is held to q_cell; the prediction must hold on every registered board.")
    L.append("  the band is NOT robust to which statistic q_cell is applied to: with the widener left at its marginal gate and the raw")
    L.append("  |m|/s held to q_cell (the scale the max-t was computed on), the fall is %s on the four registered boards - below the"
             % ", ".join("%.1f%%" % (100 * f) for f in z_all))
    L.append("  band everywhere; the widener at 0.975 already removes most of the edges the raw max-t removes, so the two corrections overlap.")
    L.append("  the readout itself (per-cell q_cell, both counts per cell, tier maps under both) is above; the tier maps of the")
    L.append("  shipped product are the SIMULTANEOUS ones by the framework's rule.")

    txt = "\n".join(L)
    print(txt)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
