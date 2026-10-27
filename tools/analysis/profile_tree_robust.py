"""PROFILE-TREE-ROBUST — does the sub-anchor capability profile survive a change of tree? (registered 2026-09-14)

  python tools/analysis/profile_tree_robust.py

RESOLVE ships statements of the form "model m is stronger than its own average in cell c". Every one is made
relative to a partition that was itself estimated, and nothing in the programme has asked whether they survive
re-estimating it. H10 registered this at ~18,000 calls because a different tree gives different per-cell
rubrics; the rubric line is closed, so the counterfactual now reduces to RE-CELLING THE SAME VERDICTS at 0 calls.

Two trees, same clean reserved pool (p2dca), same seed, different embedding configuration:
  bareq512_s42  87 leaves / 158 nodes      abt2d512_s42  47 leaves / 67 nodes
Anchor assignment agrees 99.7% and is NOT a test - the anchors are the pinned MMLU-Pro categories. The test is
at the leaf level.
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

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "profile_tree_robust.txt")
TREE_A = "bareq512_s42"
TREE_B = "abt2d512_s42"
NULL_REPS = 200
BOOT = 1000
MIN_CELL = 25          # a leaf with fewer questions than this cannot support a board; folded into its anchor
CORR_BAR = 0.50        # registered adoption bar


def profile(part, rows_by_q, models, glob):
    """Per-leaf BT strengths. Returns {cell: (raw, centred)} where centred[m] = theta(m|cell) - theta(m|all).

    Both are kept because they answer different questions and conflating them was a bug in the first run:
    the ROUTER wants the strongest model in the cell (raw argmax), while the PROFILE claim is about a model
    being above its own average (centred)."""
    bycell = defaultdict(list)
    for q, rs in rows_by_q.items():
        c = part.get(q)
        if c is not None:
            bycell[c].extend(rs)
    out = {}
    for c, rs in bycell.items():
        if len({r[2] for r in rs}) < MIN_CELL:
            continue
        th = jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in rs], models)
        out[c] = (dict(th), {m: th[m] - glob[m] for m in models})
    return out


def paired(pa, pb, partA, partB, qs, models):
    """Per-(model, question) centred strengths under both trees, for questions both trees can profile."""
    out = []
    for q in qs:
        ca, cb = partA.get(q), partB.get(q)
        if ca not in pa or cb not in pb:
            continue
        for m in models:
            out.append((q, m, pa[ca][1][m], pb[cb][1][m]))
    return out


def demean_by_model(P):
    """Remove each model's own mean from both columns.

    WHY THIS EXISTS (amendment, disclosed): the registered primary correlates raw centred strengths, and its
    size-matched null came in at +0.86 - a RANDOM partition reproduces almost the whole correlation. The cause
    is that a small cell shrinks the whole BT vector toward zero, so centred ~= (s_c - 1) * theta_global with a
    cell-specific scalar s_c. Both trees' profiles are then proportional to the SAME global ordering and
    correlate whatever the partition is. Removing each model's mean removes everything that is a pure function
    of the model, leaving only "is m unusually strong HERE" - which is the claim the profile actually makes."""
    sums = defaultdict(float); cnts = defaultdict(int)
    sumy = defaultdict(float)
    for _, m, x, y in P:
        sums[m] += x; sumy[m] += y; cnts[m] += 1
    return [(q, m, x - sums[m] / cnts[m], y - sumy[m] / cnts[m]) for q, m, x, y in P]


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    mx = sum(xs) / n; my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx <= 0 or sy <= 0:
        return float("nan")
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def shuffled_partition(part, rng):
    """A random partition with the SAME cell-size distribution: permute the question->cell map.

    DEFECT, found by the review of 2026-09-15: this permutes ACROSS anchors, so it destroys the anchor
    membership the two trees share on 2,800 of 2,811 questions. A sub-anchor question needs a null that keeps
    the anchor and permutes only the leaves inside it - see shuffled_within_anchor. Kept so the first run's
    numbers can be reproduced; no longer the null the primary is read against."""
    qs = list(part); cells = [part[q] for q in qs]
    rng.shuffle(cells)
    return dict(zip(qs, cells))


def shuffled_within_anchor(part, anc_fn, rng):
    """Permute leaves INSIDE each anchor only. This is the null a sub-anchor question conditions on."""
    by = defaultdict(list)
    for q in part:
        by[anc_fn(part[q])].append(q)
    out = {}
    for a, qq in by.items():
        cells = [part[q] for q in qq]
        rng.shuffle(cells)
        out.update(dict(zip(qq, cells)))
    return out


def demean_by_model_anchor(P, anc_of_q):
    """Remove each (model, anchor) mean. What is left is the claim 'm is unusually strong in THIS LEAF, beyond
    what it is in the anchor' - the only claim a sub-anchor profile makes."""
    sx = defaultdict(float); sy = defaultdict(float); c = defaultdict(int)
    for q, m, x, y in P:
        k = (m, anc_of_q(q)); sx[k] += x; sy[k] += y; c[k] += 1
    return [(q, m, x - sx[(m, anc_of_q(q))] / c[(m, anc_of_q(q))], y - sy[(m, anc_of_q(q))] / c[(m, anc_of_q(q))])
            for q, m, x, y in P]


def main():
    L = []
    rng = random.Random(42)
    models = sorted(p8.ARENA12)

    # ---- the answer key, for the router readout ----
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in p8.ARENA12:
            K[q][m] = int(c or 0)

    # ---- the verdicts ----
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    rows_by_q = defaultdict(list)
    for a, b, q, w, _ in rows:
        rows_by_q[q].append((a, b, q, w))

    # ---- the two trees ----
    routeA = r512.primary_routing(TREE_A); routeB = r512.primary_routing(TREE_B)
    nodesA = r512.load_graph(r512.snapshot_id(TREE_A)); ancA = r512.anchor_fn(nodesA)
    nodesB = r512.load_graph(r512.snapshot_id(TREE_B)); ancB = r512.anchor_fn(nodesB)
    qs = sorted(set(routeA) & set(routeB) & set(rows_by_q))

    L.append("=== PROFILE-TREE-ROBUST: does the sub-anchor profile survive a change of tree? ===")
    L.append("  trees %s (%d leaves) and %s (%d leaves) on the same reserved pool"
             % (TREE_A, len({routeA[q] for q in qs}), TREE_B, len({routeB[q] for q in qs})))
    L.append("  questions carrying verdicts under both: %d | matches %d | models %d" % (len(qs), len(rows), len(models)))

    same_anc = sum(1 for q in qs if ancA(routeA[q]) == ancB(routeB[q]))
    L.append("")
    L.append("  ANCHOR LEVEL, reported as a NULL BY CONSTRUCTION and not as a result: the two trees place")
    L.append("  %d of %d questions (%.3f) in the same anchor, because the anchors ARE the pinned MMLU-Pro"
             % (same_anc, len(qs), same_anc / len(qs)))
    L.append("  categories. Nothing can be learned from an anchor-level counterfactual on these trees.")

    glob = jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                          for q in qs for a, b, _, w in rows_by_q[q]], models)
    sub = {q: rows_by_q[q] for q in qs}
    partA = {q: routeA[q] for q in qs}; partB = {q: routeB[q] for q in qs}
    pa = profile(partA, sub, models, glob); pb = profile(partB, sub, models, glob)
    L.append("")
    L.append("  leaves carrying at least %d questions: %s %d of %d | %s %d of %d"
             % (MIN_CELL, TREE_A, len(pa), len({partA[q] for q in qs}),
                TREE_B, len(pb), len({partB[q] for q in qs})))

    P = paired(pa, pb, partA, partB, qs, models)
    xs = [p[2] for p in P]; ys = [p[3] for p in P]
    r = pearson(xs, ys)
    L.append("")
    L.append("=== (1) PRIMARY: correlation of the two trees' centred per-(model, question) strengths ===")
    L.append("  pairs %d over %d questions" % (len(P), len({p[0] for p in P})))
    L.append("  observed Pearson r = %+.4f" % r)

    # question-clustered bootstrap
    byq = defaultdict(list)
    for q, m, x, y in P:
        byq[q].append((x, y))
    qlist = sorted(byq)
    bs = []
    for _ in range(BOOT):
        pick = [qlist[rng.randrange(len(qlist))] for _ in qlist]
        bx = []; by = []
        for q in pick:
            for x, y in byq[q]:
                bx.append(x); by.append(y)
        v = pearson(bx, by)
        if v == v:
            bs.append(v)
    bs.sort()
    lo, hi = bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs))]
    L.append("  question-clustered bootstrap 95%% CI [%+.4f, %+.4f] over %d draws" % (lo, hi, len(bs)))

    # size-matched random-partition null
    nulls = []
    for i in range(NULL_REPS):
        ra = shuffled_partition(partA, rng); rb = shuffled_partition(partB, rng)
        na = profile(ra, sub, models, glob); nb = profile(rb, sub, models, glob)
        Q = paired(na, nb, ra, rb, qs, models)
        if len(Q) > 100:
            v = pearson([p[2] for p in Q], [p[3] for p in Q])
            if v == v:
                nulls.append(v)
    nulls.sort()
    n95 = nulls[int(0.95 * len(nulls))] if nulls else float("nan")
    L.append("  size-matched random-partition null over %d reps: median %+.4f | 95th pct %+.4f | max %+.4f"
             % (len(nulls), nulls[len(nulls) // 2], n95, nulls[-1]))
    beats_null = r > n95
    beats_bar = r > CORR_BAR
    L.append("")
    L.append("  REGISTERED BAR: adopt sub-anchor reporting only if r exceeds the null's 95th pct AND exceeds %.2f" % CORR_BAR)
    L.append("    exceeds null 95th pct: %s (%+.4f vs %+.4f)" % ("YES" if beats_null else "NO", r, n95))
    L.append("    exceeds %.2f:           %s (%+.4f)" % (CORR_BAR, "YES" if beats_bar else "NO", r))
    L.append("  -> AS REGISTERED: %s" % ("PASSES both conditions"
                                         if (beats_null and beats_bar) else
                                         "does NOT pass"))
    L.append("")
    L.append("  BUT THE REGISTERED BAR IS UNINFORMATIVE AND I AM SAYING SO RATHER THAN BANKING THE PASS.")
    L.append("  The null sits at %+.4f. A RANDOM partition of the same shape reproduces almost the whole" % nulls[len(nulls) // 2])
    L.append("  correlation, so the 0.50 bar was miscalibrated when I registered it: anything at all would clear")
    L.append("  it. The cause is a shrinkage artefact - a small cell pulls the whole BT vector toward zero, so")
    L.append("  the centred profile is roughly (s_c - 1) x theta_global with a cell-specific scalar, and both")
    L.append("  trees' profiles end up proportional to the SAME global ordering whatever the partition is. The")
    L.append("  margin over the null, %+.4f, is the only part of the primary that carries information."
             % (r - nulls[len(nulls) // 2]))

    # ---- (1b) the amendment: model-demeaned correlation ----
    L.append("")
    L.append("=== (1b) AMENDMENT, recorded before the result was read: the same test with model means removed ===")
    L.append("  Removing each model's own mean removes everything that is a pure function of the model and")
    L.append("  leaves only the claim the profile actually makes - is m unusually strong HERE. The null must")
    L.append("  collapse toward zero for this statistic to be the right instrument; if it does not, neither")
    L.append("  statistic works and the honest answer is that this design cannot measure tree robustness.")
    D = demean_by_model(P)
    rd = pearson([p[2] for p in D], [p[3] for p in D])
    byqd = defaultdict(list)
    for q, m, x, y in D:
        byqd[q].append((x, y))
    qld = sorted(byqd)
    bsd = []
    for _ in range(BOOT):
        pick = [qld[rng.randrange(len(qld))] for _ in qld]
        bx = []; by = []
        for q in pick:
            for x, y in byqd[q]:
                bx.append(x); by.append(y)
        v = pearson(bx, by)
        if v == v:
            bsd.append(v)
    bsd.sort()
    L.append("  observed model-demeaned r = %+.4f | question-clustered 95%% CI [%+.4f, %+.4f]"
             % (rd, bsd[int(0.025 * len(bsd))], bsd[int(0.975 * len(bsd))]))
    nd = []
    for i in range(NULL_REPS):
        ra = shuffled_partition(partA, rng); rb = shuffled_partition(partB, rng)
        na = profile(ra, sub, models, glob); nb = profile(rb, sub, models, glob)
        Q = paired(na, nb, ra, rb, qs, models)
        if len(Q) > 100:
            v = pearson(*zip(*[(p[2], p[3]) for p in demean_by_model(Q)]))
            if v == v:
                nd.append(v)
    nd.sort()
    nd95 = nd[int(0.95 * len(nd))] if nd else float("nan")
    L.append("  size-matched random-partition null over %d reps: median %+.4f | 95th pct %+.4f | max %+.4f"
             % (len(nd), nd[len(nd) // 2], nd95, nd[-1]))
    L.append("  -> the demeaned null %s, so this statistic %s"
             % ("collapses toward zero" if abs(nd[len(nd) // 2]) < 0.15 else "does NOT collapse",
                "is the right instrument" if abs(nd[len(nd) // 2]) < 0.15 else "is no better than the first"))
    L.append("  -> observed %+.4f against a %+.4f null 95th pct: %s"
             % (rd, nd95, "the leaf profile carries real, tree-reproducible structure" if rd > nd95 else
                "the leaf profile does NOT reproduce across trees once the global ordering is removed"))

    # ---- (1c) CORRECTION 2026-09-15: the null must keep the anchor; the demeaning must remove it ----
    L.append("")
    L.append("=== (1c) CORRECTED NULL AND DEMEANING (review of 2026-09-15) ===")
    L.append("  The nulls above permute cells ACROSS anchors and so destroy the anchor membership the two trees")
    L.append("  share on 2,800 of 2,811 questions; and model-demeaning leaves the anchor profile in. A sub-anchor")
    L.append("  question needs a WITHIN-anchor null and (model, anchor) demeaning. Both, for judge and key:")
    anc_of_q = lambda q: ancA(partA[q])
    def r_ma(Q):
        D = demean_by_model_anchor(Q, anc_of_q); return pearson([p[2] for p in D], [p[3] for p in D])
    rd_ma = r_ma(P)
    nw_m = []; nw_ma = []
    for i in range(NULL_REPS):
        ra = shuffled_within_anchor(partA, ancA, rng); rb = shuffled_within_anchor(partB, ancB, rng)
        na = profile(ra, sub, models, glob); nb = profile(rb, sub, models, glob)
        Q = paired(na, nb, ra, rb, qs, models)
        if len(Q) > 100:
            v1 = pearson(*zip(*[(p[2], p[3]) for p in demean_by_model(Q)]))
            v2 = r_ma(Q)
            if v1 == v1: nw_m.append(v1)
            if v2 == v2: nw_ma.append(v2)
    nw_m.sort(); nw_ma.sort()
    L.append("  JUDGE  model-demeaned          observed %+.4f | within-anchor null median %+.4f, 95th %+.4f"
             % (rd, nw_m[len(nw_m) // 2], nw_m[int(0.95 * len(nw_m))]))
    L.append("  JUDGE  (model, anchor)-demeaned observed %+.4f | within-anchor null median %+.4f, 95th %+.4f"
             % (rd_ma, nw_ma[len(nw_ma) // 2], nw_ma[int(0.95 * len(nw_ma))]))
    L.append("  READ: the model-demeaned observed value sitting near its within-anchor null median means it was")
    L.append("  measuring the anchor profile the trees share by fiat. Only the (model, anchor)-demeaned line speaks")
    L.append("  to the registered question, and only if it clears its own within-anchor null.")

    # ---- (2) router agreement and realised gain ----
    L.append("")
    L.append("=== (2) SECONDARY: router agreement and realised key-decidable accuracy ===")
    # The router picks the strongest model IN the cell, i.e. argmax of the RAW per-cell theta. The first run
    # took argmax of the CENTRED value, which selects whichever model most exceeds its own average - a weak
    # model having a good day - and scored 0.2317. That was a bug in the readout, not a finding.
    bestA = {}; bestB = {}
    for q in qs:
        ca, cb = partA.get(q), partB.get(q)
        if ca in pa: bestA[q] = max(models, key=lambda m: pa[ca][0][m])
        if cb in pb: bestB[q] = max(models, key=lambda m: pb[cb][0][m])
    both = [q for q in qs if q in bestA and q in bestB]
    agree = sum(1 for q in both if bestA[q] == bestB[q]) / max(1, len(both))
    L.append("  the two trees name the same best model for %d of %d questions = %.3f" % (
        sum(1 for q in both if bestA[q] == bestB[q]), len(both), agree))

    gm = max(models, key=lambda m: sum(K[q].get(m, 0) for q in both if m in K.get(q, {})))
    def acc(pick):
        v = [K[q][pick[q]] for q in both if q in K and pick[q] in K[q]]
        return sum(v) / max(1, len(v)), len(v)
    ga, gn = acc({q: gm for q in both})
    aa, an = acc(bestA); ba, bn = acc(bestB)
    L.append("  global best single model (%s): %.4f (n=%d)" % (gm, ga, gn))
    L.append("  %s leaf router: %.4f (n=%d) | %+.4f against the global best" % (TREE_A, aa, an, aa - ga))
    L.append("  %s leaf router: %.4f (n=%d) | %+.4f against the global best" % (TREE_B, ba, bn, ba - ga))
    L.append("  LEAF-POWER predicted neither router beats the global best: %s"
             % ("HELD - neither does" if (aa <= ga and ba <= ga) else
                "did NOT hold - at least one router beats it"))

    # ---- (3) the reader's number: sign reversal ----
    L.append("")
    L.append("=== (3) THE READER'S NUMBER: how often does a per-cell claim flip sign between trees? ===")
    nz = [(x, y) for _, _, x, y in P if abs(x) > 1e-9 and abs(y) > 1e-9]
    flip = sum(1 for x, y in nz if (x > 0) != (y > 0)) / max(1, len(nz))
    L.append("  sign-reversal rate over %d non-zero pairs: %.3f" % (len(nz), flip))
    for t in (0.05, 0.10, 0.20):
        strong = [(x, y) for x, y in nz if abs(x) >= t]
        if strong:
            f = sum(1 for x, y in strong if (x > 0) != (y > 0)) / len(strong)
            L.append("  restricted to |centred strength| >= %.2f in %s (n=%d): %.3f" % (t, TREE_A, len(strong), f))
    L.append("  READ: a reader asking what a published per-cell capability claim is worth should be told this")
    L.append("  number, whatever the primary does. It is the share of such claims that reverse if the tree is")
    L.append("  rebuilt with a different embedding configuration on the same data and the same split.")

    # ---- (4) is the reproducible profile CAPABILITY, or a shared judge artefact? ----
    L.append("")
    L.append("=== (4) ADDED before its result was computed: is the reproducible structure CAPABILITY or JUDGE? ===")
    L.append("  The leading alternative explanation for (1b) is that both trees capture the same JUDGE artefact")
    L.append("  rather than the same capability. The x12 verdicts carry a measured verbosity preference and a")
    L.append("  measured position effect; if either clusters by topic, both trees would pick it up and the two")
    L.append("  profiles would agree without any capability structure underneath. That would also explain why")
    L.append("  neither leaf router beats the global best in (2).")
    L.append("  THE DISCRIMINATOR, and it is free: run the identical model-demeaned tree-robustness statistic on")
    L.append("  per-cell ANSWER-KEY ACCURACY instead of judge-derived BT strength. The key cannot have a judge")
    L.append("  artefact. If the key-derived profile reproduces at a similar level, the structure is capability.")
    L.append("  If it sits near the null while the judge-derived one does not, the profile is a judge artefact.")

    def key_profile(part):
        bycell = defaultdict(list)
        for q in qs:
            c = part.get(q)
            if c is not None:
                bycell[c].append(q)
        out = {}
        for c, cqs in bycell.items():
            if len(cqs) < MIN_CELL:
                continue
            d = {}
            for m in models:
                v = [K[q][m] for q in cqs if q in K and m in K[q]]
                if v:
                    d[m] = sum(v) / len(v)
            if len(d) == len(models):
                out[c] = d
        return out

    def key_paired(ka, kb, ra, rb):
        out = []
        for q in qs:
            ca, cb = ra.get(q), rb.get(q)
            if ca not in ka or cb not in kb:
                continue
            for m in models:
                out.append((q, m, ka[ca][m], kb[cb][m]))
        return out

    ka = key_profile(partA); kb = key_profile(partB)
    KP = key_paired(ka, kb, partA, partB)
    if len(KP) > 100:
        KD = demean_by_model(KP)
        rk = pearson([p[2] for p in KD], [p[3] for p in KD])
        knull = []
        for i in range(NULL_REPS):
            ra = shuffled_partition(partA, rng); rb = shuffled_partition(partB, rng)
            Q = key_paired(key_profile(ra), key_profile(rb), ra, rb)
            if len(Q) > 100:
                v = pearson(*zip(*[(p[2], p[3]) for p in demean_by_model(Q)]))
                if v == v:
                    knull.append(v)
        knull.sort()
        k95 = knull[int(0.95 * len(knull))] if knull else float("nan")
        L.append("")
        L.append("  key-derived model-demeaned r = %+.4f over %d pairs" % (rk, len(KP)))
        L.append("  its size-matched null over %d reps: median %+.4f | 95th pct %+.4f" % (len(knull), knull[len(knull) // 2], k95))
        L.append("  judge-derived was %+.4f against a %+.4f null." % (rd, nd95))
        # CORRECTION 2026-09-15: the key's own within-anchor null, and its (model, anchor)-demeaned value
        kw_m = []; kw_ma = []
        for i in range(NULL_REPS):
            ra = shuffled_within_anchor(partA, ancA, rng); rb = shuffled_within_anchor(partB, ancB, rng)
            Q = key_paired(key_profile(ra), key_profile(rb), ra, rb)
            if len(Q) > 100:
                v1 = pearson(*zip(*[(p[2], p[3]) for p in demean_by_model(Q)])); v2 = r_ma(Q)
                if v1 == v1: kw_m.append(v1)
                if v2 == v2: kw_ma.append(v2)
        kw_m.sort(); kw_ma.sort()
        rk_ma = r_ma(KP)
        L.append("  KEY  model-demeaned          observed %+.4f | WITHIN-anchor null median %+.4f, 95th %+.4f"
                 % (rk, kw_m[len(kw_m) // 2], kw_m[int(0.95 * len(kw_m))]))
        L.append("  KEY  (model, anchor)-demeaned observed %+.4f | within-anchor null median %+.4f, 95th %+.4f"
                 % (rk_ma, kw_ma[len(kw_ma) // 2], kw_ma[int(0.95 * len(kw_ma))]))
        if rk <= kw_m[int(0.95 * len(kw_m))]:
            L.append("  -> CORRECTION: the key's %+.4f is AT its within-anchor null. 'The structure is real and" % rk)
            L.append("     tree-robust' measured the ANCHOR profile, which the two trees share on 2,800 of 2,811")
            L.append("     questions. It said nothing about sub-anchor structure. The (model, anchor)-demeaned")
            L.append("     line is the only test of the registered question.")
        if rk > k95:
            L.append("  -> THE KEY REPRODUCES TOO. The per-cell structure is a property of the QUESTIONS, not of the")
            L.append("     judge: the answer key, which cannot carry a judge artefact, agrees across trees at")
            L.append("     %+.4f against a %+.4f null. The judge-artefact explanation is rejected." % (rk, k95))
        else:
            L.append("  -> THE KEY DOES NOT REPRODUCE while the judge does. The reproducible per-cell structure is a")
            L.append("     shared JUDGE artefact, not capability, and no per-cell capability claim may rest on it.")
        L.append("  RATIO judge/key = %.2f. A ratio far above 1 means the judge sees more 'structure' than the key" % (rd / rk if rk else float("nan")))
        L.append("  supports, which is the signature of an artefact riding on top of real structure.")

        # ---- (5) is the judge LOSSY or merely NOISY? ----
        L.append("")
        L.append("=== (5) ADDED before its result was computed: is the judge's shortfall FIDELITY or NOISE? ===")
        L.append("  (4) shows the judge recovers a fraction of a structure the key reproduces at %+.4f. Two very" % rk)
        L.append("  different readings: the judge TRANSMITS LESS of the real structure (a fidelity loss, which is")
        L.append("  a property of the judge and is improvable), or the judge's per-cell estimate is simply NOISIER")
        L.append("  because it rests on about three matches per question where the key rests on a fact. Those")
        L.append("  demand different responses, so separate them by measuring each instrument's own reliability.")
        L.append("  METHOD: under ONE tree, split each cell's questions into two halves, build the profile on each")
        L.append("  half, correlate them model-demeaned, and Spearman-Brown to full length. Then disattenuate the")
        L.append("  cross-tree correlation by that reliability. Identical treatment for both instruments.")

        def half_split(part, rng2):
            ha = {}; hb = {}
            bycell = defaultdict(list)
            for q in qs:
                c = part.get(q)
                if c is not None:
                    bycell[c].append(q)
            for c, cqs in bycell.items():
                cc = sorted(cqs); rng2.shuffle(cc)
                mid = len(cc) // 2
                for q in cc[:mid]: ha[q] = c
                for q in cc[mid:]: hb[q] = c
            return ha, hb

        rng2 = random.Random(7)
        h1, h2 = half_split(partA, rng2)
        # judge reliability
        j1 = profile(h1, sub, models, glob); j2 = profile(h2, sub, models, glob)
        JP = [(q, m, j1[partA[q]][1][m], j2[partA[q]][1][m])
              for q in qs if partA.get(q) in j1 and partA.get(q) in j2 for m in models]
        # key reliability
        k1 = key_profile(h1); k2 = key_profile(h2)
        KK = [(q, m, k1[partA[q]][m], k2[partA[q]][m])
              for q in qs if partA.get(q) in k1 and partA.get(q) in k2 for m in models]
        out = []
        for nm, S, cross in (("judge", JP, rd), ("key", KK, rk)):
            if len(S) < 100:
                L.append("  %-6s reliability: too few pairs (%d)" % (nm, len(S))); continue
            SD = demean_by_model(S)
            rh = pearson([p[2] for p in SD], [p[3] for p in SD])
            R = 2 * rh / (1 + rh) if rh > -1 else float("nan")
            # both profiles are equally unreliable, so the classical correction divides by R, not sqrt(R)
            # (review 2026-09-15). The first run divided by sqrt(R); the verdict was discarded either way.
            dis = cross / R if R and R > 0 else float("nan")
            out.append((nm, rh, R, cross, dis))
            L.append("  %-6s split-half r=%+.4f -> Spearman-Brown reliability R=%+.4f | cross-tree %+.4f -> disattenuated %+.4f"
                     % (nm, rh, R, cross, dis))
        if len(out) == 2:
            dj = out[0][4]; dk = out[1][4]
            L.append("")
            if dj > 1.0:
                L.append("  THE DISATTENUATION IS INVALID AND ITS VERDICT IS DISCARDED. It returns %+.4f for the judge," % dj)
                L.append("  and a correlation cannot exceed 1. The assumption it breaks is independence: the two")
                L.append("  cross-tree profiles are built from the SAME questions and the SAME verdicts under two")
                L.append("  partitions that agree on 99.6% of anchor assignments, so they share almost all their data,")
                L.append("  while the split-half compares disjoint question sets. The two quantities are not on the")
                L.append("  same footing and their ratio means nothing. I am reporting this rather than the verdict it")
                L.append("  produced, which would have read 'NOISE, not fidelity'.")
            L.append("")
            L.append("  WHAT (5) DOES ESTABLISH, and it is more important than what it was built to test:")
            L.append("    judge per-cell profile split-half reliability  r=%+.4f  (Spearman-Brown R=%+.4f)" % (out[0][1], out[0][2]))
            L.append("    key   per-cell profile split-half reliability  r=%+.4f  (Spearman-Brown R=%+.4f)" % (out[1][1], out[1][2]))
            L.append("  Measured on two INDEPENDENT halves of the same cell in the same tree, the judge's per-cell")
            L.append("  capability profile reproduces at %+.4f. At the x12 budget it is close to pure noise. The key's" % out[0][1])
            L.append("  reproduces at %+.4f on exactly the same split, so this is a property of the judge-derived" % out[1][1])
            L.append("  estimate and not of the cells.")
            L.append("  AND THIS CUTS AGAINST (1b). The cross-tree judge correlation was %+.4f - %.1fx its own" % (rd, rd / out[0][1] if out[0][1] else float("nan")))
            L.append("  independent-sample reliability of %+.4f. Two measurements that share almost all their data" % out[0][1])
            L.append("  agree far better than two measurements that share none, which is what shared data does and")
            L.append("  not what reproducible structure does. (1b)'s reading that the judge profile 'carries real,")
            L.append("  tree-reproducible structure' is therefore NOT supported by (1b) alone.")

    # ---- (6) the honest cross-tree test: only questions the trees actually place differently ----
    L.append("")
    L.append("=== (6) ADDED before its result was computed: restrict to questions the two trees DISAGREE about ===")
    L.append("  (5) shows the cross-tree comparison is contaminated by shared data. The clean version is to keep")
    L.append("  only the questions whose CELL ACTUALLY CHANGES between trees, where the two profiles are genuinely")
    L.append("  being asked to agree about something. If the agreement in (1b) came from shared cells it collapses")
    L.append("  here; if the profile is really tree-robust it survives.")
    changed = [q for q in qs if partA.get(q) in pa and partB.get(q) in pb
               and {x for x in (partA[q],)} and partA[q] != partB[q]]
    # cell ids are not comparable across trees, so define "changed" by the question's COMPANY:
    coA = {}; coB = {}
    for q in qs:
        coA.setdefault(partA.get(q), set()).add(q)
        coB.setdefault(partB.get(q), set()).add(q)
    jac = {}
    for q in qs:
        A_ = coA.get(partA.get(q)); B_ = coB.get(partB.get(q))
        if A_ and B_:
            jac[q] = len(A_ & B_) / len(A_ | B_)
    prof_qs = [q for q in qs if partA.get(q) in pa and partB.get(q) in pb and q in jac]
    prof_qs.sort(key=lambda q: jac[q])
    L.append("  cell ids are not comparable across trees, so 'changed' is measured by the question's COMPANY:")
    L.append("  the Jaccard overlap between the set of questions sharing its cell in A and in B.")
    for lab, sel in (("most changed third (lowest overlap)", prof_qs[:len(prof_qs) // 3]),
                     ("middle third", prof_qs[len(prof_qs) // 3: 2 * len(prof_qs) // 3]),
                     ("least changed third (highest overlap)", prof_qs[2 * len(prof_qs) // 3:])):
        if len(sel) < 30:
            continue
        ss = set(sel)
        sd = demean_by_model([p for p in P if p[0] in ss])
        rr = pearson([p[2] for p in sd], [p[3] for p in sd])
        kk = float("nan")
        ksel = [p for p in KP if p[0] in ss] if len(KP) > 100 else []
        if len(ksel) > 100:
            kd = demean_by_model(ksel)
            kk = pearson([p[2] for p in kd], [p[3] for p in kd])
        mj = sum(jac[q] for q in sel) / len(sel)
        # (model, anchor)-demeaned versions of the same strata (correction 2026-09-15)
        rr_ma = r_ma([p for p in P if p[0] in ss])
        kk_ma = r_ma(ksel) if len(ksel) > 100 else float("nan")
        L.append("  %-38s n=%5d | overlap %.3f | model-demeaned judge %+.4f key %+.4f | (model,anchor)-demeaned judge %+.4f key %+.4f"
                 % (lab, len(sel), mj, rr, kk, rr_ma, kk_ma))
    L.append("  READ: if r falls as overlap falls, the cross-tree agreement is shared data. If r holds, the")
    L.append("  profile is genuinely tree-robust and (1b) stands. The KEY column is the decisive one: it says")
    L.append("  whether the structure itself is partition-dependent, or only the judge's estimate of it.")

    # ---- (7) what budget would a reliable leaf profile need? ----
    L.append("")
    L.append("=== (7) BUDGET IMPLICATION: what would it take to resolve the leaf profile? ===")
    try:
        R1 = out[0][2]
        # base = the mean size of the leaves R1 was actually measured on (those with >= 2*MIN_CELL questions),
        # not pool/leaves (review 2026-09-15: 53 vs ~71 questions; order of magnitude unchanged)
        meas = [c for c in pa if sum(1 for q in qs if partA[q] == c) >= 2 * MIN_CELL]
        base = sum(sum(1 for q in qs if partA[q] == c) for c in meas) / max(1, len(meas))
        L.append("  (base: %d leaves carried the split-half measurement, mean %.0f questions each)" % (len(meas), base))
        for tgt in (0.70, 0.80, 0.90):
            k = (tgt * (1 - R1)) / (R1 * (1 - tgt))
            qpc = base * k
            L.append("  to reach reliability %.2f: %.1fx the current per-cell evidence, i.e. ~%d questions per leaf"
                     % (tgt, k, int(qpc)))
        L.append("  (Spearman-Brown from the measured R=%+.4f, over %d profiled leaves averaging %.0f questions each)"
                 % (R1, len(pa), len(qs) / max(1, len(pa))))
        L.append("  AND THE CAVEAT THAT MATTERS: this is a QUESTIONS-PER-CELL requirement, not only a call budget.")
        L.append("  Re-judging the same match does not add independent evidence - TEMP-0 showed the 5.7% test-retest")
        L.append("  floor is intrinsic and survives temperature 0 - so the multiplier has to come from new")
        L.append("  questions in each cell. The reserved pool holds %d questions across %d profiled leaves; the"
                 % (len(qs), len(pa)))
        L.append("  0.80 target needs roughly %d, which MMLU-Pro does not contain. A reliable per-leaf capability"
                 % int((len(qs) / max(1, len(pa))) * ((0.80 * (1 - R1)) / (R1 * 0.20)) * len(pa)))
        L.append("  profile is therefore out of reach on this corpus at any call budget, which is a DATA limit and")
        L.append("  is the honest reason every leaf-level test in this programme has been underpowered.")
    except Exception as e:
        L.append("  not computable: %s" % e)

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
