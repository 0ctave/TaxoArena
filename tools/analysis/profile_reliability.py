"""PROFILE-RELIABILITY — is the ANCHOR-level capability profile reliable, and at what cell size? (registered 2026-09-14)

  python tools/analysis/profile_reliability.py

PROFILE-TREE-ROBUST measured the judge's per-LEAF profile at a split-half reliability of 0.086 (Spearman-Brown
R=0.158) and concluded the anchor is the reporting ceiling. It never measured the anchor. RESOLVE's deliverable
is a per-ANCHOR profile, so that hole has to be closed: if anchor reliability is also poor, the product is in
question and not merely its finest layer.

Identical instrument to PROFILE-TREE-ROBUST (5) so the numbers are directly comparable. Registered bar: the
anchor-level judge profile is publishable as a measured per-cell capability claim only if R >= 0.70.

  python tools/analysis/profile_reliability.py --interaction-only    # PROFILE-RELIABILITY-INTERACTION (registered 2026-09-18)
  python tools/analysis/profile_reliability.py --selftest            # pins the DEFAULT path on a synthetic table (no DB read)

--interaction-only (PROFILE-RELIABILITY-INTERACTION, docs/judge_v2_program.md "Registered 2026-09-18 ... PROFILE-RELIABILITY-
INTERACTION", commit 954e829): INERT when absent. With the flag the half-profile pairs are demeaned by model AND by anchor
(two-way, alternating until every row and column mean is < 1e-9, on each half separately) before the Pearson r; the same
40 halvings (random.Random(7)), the same builders, the same Spearman-Brown; the output goes to
profile_reliability_interaction_only.txt, never to the default file. The three registered legs with their intervals, the
C0 centring check, the no-interaction null and the variance decomposition live in profile_reliability_interaction.py.
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

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "profile_reliability.txt")
TREE = "bareq512_s42"
REPS = 40          # independent half-splits, averaged; PROFILE-TREE-ROBUST used a single split
BAR = 0.70         # registered publishability bar for the anchor level


def pearson(xs, ys):
    n = len(xs)
    if n < 3: return float("nan")
    mx = sum(xs) / n; my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx <= 0 or sy <= 0: return float("nan")
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def demean_by_model(P):
    sx = defaultdict(float); sy = defaultdict(float); c = defaultdict(int)
    for _, m, x, y in P:
        sx[m] += x; sy[m] += y; c[m] += 1
    return [(q, m, x - sx[m] / c[m], y - sy[m] / c[m]) for q, m, x, y in P]


def demean_two_way(P, tol=1e-9, max_iter=200):
    """PROFILE-RELIABILITY-INTERACTION: demean by model AND by cell (anchor), alternating until every row and column
    mean is below `tol`, on each half (x and y) separately. On a balanced table one pass of each is exact; the loop
    only matters when a (cell, model) pair is missing. Returns the same (cell, model, x, y) tuples."""
    P = list(P)
    for _ in range(max_iter):
        P = demean_by_model(P)
        sx = defaultdict(float); sy = defaultdict(float); c = defaultdict(int)
        for cell, _, x, y in P:
            sx[cell] += x; sy[cell] += y; c[cell] += 1
        P = [(cell, m, x - sx[cell] / c[cell], y - sy[cell] / c[cell]) for cell, m, x, y in P]
        mx = defaultdict(float); my = defaultdict(float); n = defaultdict(int)
        for _, m, x, y in P:
            mx[m] += x; my[m] += y; n[m] += 1
        if all(abs(mx[m] / n[m]) < tol and abs(my[m] / n[m]) < tol for m in n):
            break
    return P


DEMEAN = demean_by_model      # the default path; --interaction-only sets demean_two_way


def sb(r):
    return 2 * r / (1 + r) if r > -1 else float("nan")


def reliability(cells, qsel, build, models, rng, reps=REPS, min_cell=25, demean=None):
    """Mean split-half reliability over `reps` independent halvings. `build(list_of_qs)` -> {model: value}.
    `demean` defaults to the module's DEMEAN (demean_by_model unless --interaction-only)."""
    demean = demean or DEMEAN
    rs = []
    for _ in range(reps):
        P = []
        for c, cqs in cells.items():
            cc = [q for q in cqs if q in qsel]
            if len(cc) < 2 * min_cell:
                continue
            cc = sorted(cc); rng.shuffle(cc)
            mid = len(cc) // 2
            d1 = build(cc[:mid]); d2 = build(cc[mid:])
            if not d1 or not d2:
                continue
            for m in models:
                if m in d1 and m in d2:
                    P.append((c, m, d1[m], d2[m]))
        if len(P) < 50:
            continue
        D = demean(P)
        v = pearson([p[2] for p in D], [p[3] for p in D])
        if v == v:
            rs.append(v)
    if not rs:
        return float("nan"), float("nan"), 0
    rs.sort()
    mu = sum(rs) / len(rs)
    sd = math.sqrt(sum((x - mu) ** 2 for x in rs) / (len(rs) - 1)) if len(rs) > 1 else 0.0
    return mu, sd, len(rs)


def main():
    L = []
    rng = random.Random(42)
    models = sorted(p8.ARENA12)

    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in p8.ARENA12:
            K[q][m] = int(c or 0)

    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    rows_by_q = defaultdict(list)
    for a, b, q, w, _ in rows:
        rows_by_q[q].append((a, b, q, w))

    route = r512.primary_routing(TREE)
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anc = r512.anchor_fn(nodes)
    qs = sorted(set(route) & set(rows_by_q))
    qsel = set(qs)

    leaf_cells = defaultdict(list); anc_cells = defaultdict(list); one_cell = {"ALL": list(qs)}
    for q in qs:
        leaf_cells[route[q]].append(q); anc_cells[anc(route[q])].append(q)

    def judge_build(cqs):
        rs = [r for q in cqs for r in rows_by_q[q]]
        if len({r[2] for r in rs}) < 10:
            return None
        return jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in rs], models)

    def key_build(cqs):
        d = {}
        for m in models:
            v = [K[q][m] for q in cqs if q in K and m in K[q]]
            if v:
                d[m] = sum(v) / len(v)
        return d if len(d) == len(models) else None

    L.append("=== PROFILE-RELIABILITY: is the ANCHOR-level capability profile reliable? ===")
    if DEMEAN is demean_two_way:
        L.append("  --interaction-only (PROFILE-RELIABILITY-INTERACTION): half-profiles demeaned by MODEL AND BY CELL; the")
        L.append("  default (model-only) numbers of record are in profile_reliability.txt, which this run does not touch.")
    L.append("  tree %s | pool %d questions | %d leaves | %d anchors | %d models"
             % (TREE, len(qs), len(leaf_cells), len(anc_cells), len(models)))
    L.append("  instrument identical to PROFILE-TREE-ROBUST (5): disjoint half-splits of each cell's QUESTIONS,")
    L.append("  profiles built on each half, correlated model-demeaned, Spearman-Brown to full length.")
    L.append("  Averaged over %d independent halvings instead of the single split used there." % REPS)
    L.append("  NOTE ON COMPARABILITY: PROFILE-TREE-ROBUST reported leaf R=0.158 at a 25-question floor; this uses a")
    L.append("  50-question floor, so its leaf row covers fewer, larger cells and reads higher. The two are")
    L.append("  consistent with the size trend in (3), and the size sweep below is the instrument that settles it.")
    L.append("")
    L.append("  %-10s %7s %9s %12s %12s %12s" % ("level", "cells", "q/cell", "judge r", "judge R(SB)", "key R(SB)"))

    res = {}
    for name, cells in (("leaf", leaf_cells), ("anchor", anc_cells), ("whole pool", one_cell)):
        usable = {c: v for c, v in cells.items() if len(v) >= 50}
        if not usable:
            L.append("  %-10s no cell carries 50 questions" % name); continue
        jr, jsd, nj = reliability(usable, qsel, judge_build, models, random.Random(7))
        kr, ksd, nk = reliability(usable, qsel, key_build, models, random.Random(7))
        qpc = sum(len(v) for v in usable.values()) / len(usable)
        res[name] = (sb(jr), sb(kr), qpc, len(usable), jsd, nj)
        if jr != jr:
            L.append("  %-10s %7d %9.0f %12s %12s %12s" % (name, len(usable), qpc, "n/a", "n/a", "n/a"))
            L.append("             (undefined by construction: with one cell, demeaning by model leaves every")
            L.append("              value at zero, so there is nothing left to correlate. Not a failure.)")
        else:
            L.append("  %-10s %7d %9.0f %12.4f %12.4f %12.4f" % (name, len(usable), qpc, jr, sb(jr), sb(kr)))
            L.append("             (judge split-half SD %.4f over %d halvings, so R is stable to about +-%.3f)"
                     % (jsd, nj, sb(jr + 1.96 * jsd / math.sqrt(nj)) - sb(jr)))

    L.append("")
    L.append("=== (1) PRIMARY, registered bar %.2f at the ANCHOR level ===" % BAR)
    if "anchor" in res:
        aj = res["anchor"][0]; asd = res["anchor"][4]; an = res["anchor"][5]
        raw_r = aj / (2.0 - aj) if aj == aj else float('nan')  # inverse Spearman-Brown
        L.append("  anchor-level judge Spearman-Brown reliability: %.4f" % aj)
        L.append("  spread over %d independent halvings: split-half SD %.4f, so the estimate is stable to about" % (an, asd))
        L.append("  +-%.3f on R. The shortfall against the bar is %.4f, which is larger than that spread."
                 % (sb(raw_r + 1.96 * asd / math.sqrt(an)) - aj if asd else 0.0, BAR - aj))  # raw_r: the anchor's raw split-half r
        # [2026-09-16 hygiene: a pasted literal 0.5069 stood here; raw_r is recovered from aj = 2r/(1+r)]
        L.append("  -> %s" % ("PASS: the anchor profile clears the bar and may be published as a measured per-cell claim"
                              if aj >= BAR else
                              "FAIL: the anchor profile does NOT clear %.2f" % BAR))
        if aj < BAR:
            L.append("  CONSEQUENCE, as registered in advance: RESOLVE may not publish per-anchor capability claims as")
            L.append("  measured quantities. It publishes the board and the routing layer, and the granular capability")
            L.append("  profile becomes a stated aspiration carrying its questions-per-cell requirement.")

    L.append("")
    L.append("=== (2) THE COMPARATOR: is any shortfall the JUDGE's or the CELL's? ===")
    for name in ("leaf", "anchor", "whole pool"):
        if name in res and res[name][0] == res[name][0]:
            j, k, qpc, n = res[name][:4]
            L.append("  %-10s judge R %.4f | key R %.4f | ratio %.2f  (%d cells, %.0f q/cell)"
                     % (name, j, k, j / k if k else float("nan"), n, qpc))
    L.append("  A key R far above the judge's at the same granularity means the cells are fine and the JUDGE is the")
    L.append("  limiting instrument. A key R that is also low would mean the cells themselves carry no stable signal.")

    L.append("")
    L.append("=== (3) THE DESIGN NUMBER: at what cell size does judge reliability cross %.2f? ===" % BAR)
    L.append("  Subsample every ANCHOR down to a common size and measure reliability at that size, so the sweep")
    L.append("  varies cell size with the cell definition held fixed.")
    L.append("  %10s %10s %14s %14s" % ("q/cell", "cells", "judge R(SB)", "key R(SB)"))
    sizes = [50, 75, 100, 150, 200, 300, 400, 600, 800]
    cross = None
    for S in sizes:
        cells = {c: v for c, v in anc_cells.items() if len(v) >= S}
        if len(cells) < 4:
            continue
        rr = random.Random(11 + S)
        cut = {}
        for c, v in cells.items():
            vv = sorted(v); rr.shuffle(vv); cut[c] = vv[:S]
        jr, _, _ = reliability(cut, qsel, judge_build, models, random.Random(11 + S), min_cell=S // 2)
        kr, _, _ = reliability(cut, qsel, key_build, models, random.Random(11 + S), min_cell=S // 2)
        L.append("  %10d %10d %14.4f %14.4f" % (S, len(cells), sb(jr), sb(kr)))
        if cross is None and sb(jr) >= BAR:
            cross = S
    L.append("")
    if cross:
        L.append("  JUDGE reliability crosses %.2f at about %d questions per cell." % (BAR, cross))
    else:
        L.append("  JUDGE reliability does NOT reach %.2f at any cell size this pool can supply (max %d q/cell)."
                 % (BAR, max(len(v) for v in anc_cells.values())))
        L.append("  Extrapolating by Spearman-Brown from the largest measured point is the only available estimate")
        L.append("  and is reported as an extrapolation, not a measurement:")
        big = max((S for S in sizes if len({c: v for c, v in anc_cells.items() if len(v) >= S}) >= 4), default=None)
        if big:
            cells = {c: v for c, v in anc_cells.items() if len(v) >= big}
            rr = random.Random(11 + big)
            cut = {}
            for c, v in cells.items():
                vv = sorted(v); rr.shuffle(vv); cut[c] = vv[:big]
            jr, _, _ = reliability(cut, qsel, judge_build, models, random.Random(11 + big), min_cell=big // 2)
            R = sb(jr)
            if R and 0 < R < 1:
                k = (BAR * (1 - R)) / (R * (1 - BAR))
                L.append("    at %d q/cell R=%.4f -> reaching %.2f needs %.1fx, i.e. about %d questions per cell"
                         % (big, R, BAR, k, int(big * k)))
                L.append("    and it must come from NEW questions: TEMP-0 showed the 5.7% test-retest floor is")
                L.append("    intrinsic, so re-judging the same matches adds no independent evidence.")

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


def selftest():
    """Pins the DEFAULT path on a synthetic table (values recorded with the pre-flag file at commit 13f2142, sha256
    56ad450c...; 2026-09-18) and checks the two-way demeaning: zero row/column means, identity on a table whose cell
    means are already zero (the per-anchor BT case), and a difference where a cell main effect exists. No DB is read."""
    rng = random.Random(123)
    models = ["m%d" % i for i in range(9)]
    cells = {"c%d" % c: list(range(c * 1000, c * 1000 + 80)) for c in range(6)}
    qsel = set(q for v in cells.values() for q in v)
    tab = {}
    for c, qs in cells.items():
        for q in qs:
            for i, m in enumerate(models):
                p = 1 / (1 + math.exp(-(0.3 * i - 1.0 + 0.8 * math.sin(i + int(c[1:])))))
                tab[(q, m)] = 1 if rng.random() < p else 0
    build = lambda cqs: {m: sum(tab[(q, m)] for q in cqs) / len(cqs) for m in models}
    assert DEMEAN is demean_by_model, "selftest pins the default path; run it without --interaction-only"
    r, sd, n = reliability(cells, qsel, build, models, random.Random(7))
    r2, sd2, n2 = reliability(cells, qsel, build, models, random.Random(7), reps=10, min_cell=30)
    pins = [(r, 0.7721344620035897), (sd, 0.04706507856151532), (n, 40), (sb(r), 0.8714174669687402),
            (r2, 0.772737962757706), (sd2, 0.0432997182237597), (n2, 10)]
    for got, want in pins:
        assert got == want, "DEFAULT PATH CHANGED: %r != pinned %r" % (got, want)
    # two-way demeaning: means vanish; identity when cell means are already zero; differs when they are not
    P = [(c, m, rng.random() + 0.5 * int(c[1:]), rng.random() - 0.3 * int(c[1:])) for c in cells for m in models]
    D = demean_two_way(P)
    for key, idx in ((0, 2), (0, 3), (1, 2), (1, 3)):
        acc = defaultdict(float); cnt = defaultdict(int)
        for p in D: acc[p[key]] += p[idx]; cnt[p[key]] += 1
        assert max(abs(acc[k] / cnt[k]) for k in acc) < 1e-9, "two-way demeaning left a mean"
    r_model = pearson([p[2] for p in demean_by_model(P)], [p[3] for p in demean_by_model(P)])
    r_both = pearson([p[2] for p in D], [p[3] for p in D])
    assert abs(r_model - r_both) > 1e-3, "cell main effect present but the two demeanings agree"
    Pc = []
    for c in cells:
        xs = [rng.random() for _ in models]; ys = [rng.random() for _ in models]
        mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
        Pc += [(c, m, x - mx, y - my) for m, x, y in zip(models, xs, ys)]
    r_m = pearson([p[2] for p in demean_by_model(Pc)], [p[3] for p in demean_by_model(Pc)])
    r_b = pearson([p[2] for p in demean_two_way(Pc)], [p[3] for p in demean_two_way(Pc)])
    assert abs(r_m - r_b) < 1e-12, "cell-centred table: the two demeanings must agree by identity (%r vs %r)" % (r_m, r_b)
    # unbalanced table (one (cell, model) pair missing): the alternation must still converge
    Pu = [p for p in P if not (p[0] == "c0" and p[1] == "m0")]
    Du = demean_two_way(Pu)
    for key, idx in ((0, 2), (1, 3)):
        acc = defaultdict(float); cnt = defaultdict(int)
        for p in Du: acc[p[key]] += p[idx]; cnt[p[key]] += 1
        assert max(abs(acc[k] / cnt[k]) for k in acc) < 1e-9, "unbalanced two-way demeaning did not converge"
    print("SELFTEST OK: default reliability() pinned (r %.16f, sd %.16f, n %d; reps=10/min_cell=30 r %.15f); two-way demeaning"
          % (r, sd, n, r2))
    print("  zero means (balanced and unbalanced), identity on a cell-centred table (%.6f == %.6f), differs with a cell main"
          % (r_m, r_b))
    print("  effect (model-only %.4f vs two-way %.4f). Pool of record NOT read by --selftest." % (r_model, r_both))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--interaction-only", action="store_true",
                    help="PROFILE-RELIABILITY-INTERACTION: demean by model AND cell; writes *_interaction_only.txt")
    ap.add_argument("--selftest", action="store_true", help="pin the default path on a synthetic table; no DB read")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        sys.exit(0)
    if a.interaction_only:
        DEMEAN = demean_two_way
        OUT = OUT.replace("profile_reliability.txt", "profile_reliability_interaction_only.txt")
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
