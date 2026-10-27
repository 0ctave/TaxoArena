"""PROFILE-INTERVAL-ALL (registered by reference at eaf1dbf; item 9 of docs/design/FRAMEWORK.md "Tests to
register before shipping", commit 8d77f7b; scheduled in docs/plan_2026-09-15.md Block 1). Zero calls.

  python tools/analysis/profile_interval_all.py

THE ITEM, quoted:
  9. PROFILE-INTERVAL-ALL. Jackknife intervals on every reliability number; fixed 6-cell size sweep over >= 8
  seeds; per-anchor within-cell split-half with a question-bootstrap interval. Criterion: crossing published
  as a range; per-anchor certifiability list. Prediction: History, Health, Philosophy below 0.70
  individually. 0 calls.

THE RECORD IT CITES (FRAMEWORK.md Stage 7 and "Per cell and per board"; review_session_2026-09-14.md item 5;
ledger rows PROFILE-RELIABILITY, PROFILE-RELIABILITY-X20 [X20-MERGED], ANCHOR-PROFILE-INTERVAL):
  * Board-level reliability numbers on the record: x12 judge 0.6728 (anchor, 14 cells) / 0.2559 (leaf, 8 cells),
    key 0.9135 / 0.8135; merged 20-model board 0.7183 / 0.3648, key 0.9139 / 0.8284; the x12 size sweep judge
    0.1919 / 0.1665 / 0.3616 / 0.4356 / 0.6891 and key 0.7143 / 0.8285 / 0.8513 / 0.9164 / 0.9283 at
    50 / 75 / 100 / 150 / 200 q/cell. Only the two anchor boards carry a jackknife interval so far
    (ANCHOR-PROFILE-INTERVAL: 0.6728 [0.4932, 0.8524]; 0.7183 [0.6076, 0.8291]).
  * "Support floors are provisional until PROFILE-INTERVAL-ALL runs: ... the judge reaches ~0.69 at 200 q/cell
    on the six largest anchors, with the 0.70 crossing 182-242 there and ~410-450 if all 14 anchors are held;
    '210' is not quoted." (FRAMEWORK.md Stage 7). The review's figures came from scratch scripts
    (review/v2/pr_recheck.py, review/adv/adv_profile.py), not from a committed one.
  * "Per-anchor certifiability has never been measured; the per-cell instrument (split-half of the within-anchor
    model order with a question-bootstrap interval) is registered in PROFILE-INTERVAL-ALL, and until it runs,
    History (119 judged q), Health (129) and Philosophy (132) carry the note 'smallest anchors; individual
    certifiability unmeasured' rather than a predicted failure." (FRAMEWORK.md)
  * Classes (FRAMEWORK.md Stage 7): PASS if the lower bound >= 0.70; PASS-WITH-INTERVAL if the point >= 0.70
    and the lower bound < 0.70; FAIL if the point < 0.70.

IMPLEMENTATION, and the READINGS CHOSEN where the item is silent (each taken hardest on the programme's own
claim, which here is that per-anchor rows are publishable and that the crossing sits near 201 q/cell):
  (1) "Jackknife intervals on every reliability number." Instrument = profile_reliability.reliability (40 disjoint
      halvings of each cell's questions, model-demeaned Pearson r between half-profiles, Spearman-Brown to R),
      seed random.Random(7) as in every recorded run. The jackknife is leave-one-CELL-out at the level of the
      number (14 anchors, 8 leaves, or the sweep's cells), computed two ways: on FIXED halvings (the same 40
      halvings, the dropped cell's points removed) and RE-HALVED (reliability() rerun on the reduced cell set
      with a fresh Random(7)); a cell-bootstrap (anchors resampled with replacement inside each halving, as the
      review's adv_profile.py did) is printed as a third interval. The class is read on the LOWEST lower bound
      of the readings. Covered: x12 judge, merged judge (20 rows), key (12 and 20 rows) at anchor and at leaf
      (50-question floor, the recorded instrument; a 25-question-floor leaf row is added, labelled as a
      different instrument from PROFILE-TREE-ROBUST's single-split 0.158), and every row of the size sweep.
  (2) "Fixed 6-cell size sweep over >= 8 seeds." The six largest anchors (Math, Law, Chemistry, Psychology,
      Physics, Other; exactly the six cells the recorded S=200 row used) subsampled to S in 50/75/100/150/200/210
      (210 = the largest common size), 10 seeds each; the first seed of each size is the recorded one
      (Random(11+S) for the cut and a fresh Random(11+S) for the halvings), so the committed row reproduces. The
      same sweep is run with all 14 anchors held at S in 50/75/100/115 (115 = History's 119 minus the halving
      slack), on the x12 judge, the merged judge and the key. The crossing is published as a RANGE four ways:
      (a) the Spearman-Brown extrapolation from the largest-S row across seeds (the review's 182-242);
      (b) the extrapolation from every row across seeds; (c) a least-squares fit of R(S) = S / (S + c) over the
      rows per seed, crossing = c * 0.70 / 0.30; (d) the union over seeds of the leave-one-cell-out jackknife
      interval on the crossing from the largest-S row.
      PUBLISHED: the point range is the union of (a) and (c) over seeds; the interval range is (d). (b) is printed
      as the Spearman-Brown-consistency check on the fixed cell set (the review found 491/875/412/453 when the cell
      set changed with S) and is not folded into the published range, because a row at S = 50 extrapolated 4x is not
      a crossing estimate the record ever used; where (b) is wider than the published range that is SAID in the
      output. The seed-0 cut of each size iterates the cells in the recorded dict order, so the recorded rows
      (six-cell S = 200 judge 0.6891; all-14 S = 50/75/100 judge 0.1919/0.1665/0.3616) are reproduced exactly.
  (3) "Per-anchor within-cell split-half with a question-bootstrap interval." Two readings of "the within-anchor
      model order": (i) PROFILE reading, the one the framework publishes (capability statements are
      (model x anchor) DEVIATIONS): each half's profile is model-demeaned across the 14 anchors exactly as in the
      board-level instrument, and r_a is the Pearson correlation across the 12 (or 20) models of the two halves'
      deviations inside anchor a; (ii) RAW-ORDER reading: Spearman rank correlation across models of the two
      halves' raw theta inside anchor a. Reading (i) is the harder one on the programme (the raw order reproduces
      the global model spread that every anchor shares) and is the one the certifiability list is read on;
      reading (ii) is printed beside it. Both are Spearman-Brown to full length and averaged over 40 halvings.
      The question-bootstrap: within every anchor its judged questions are resampled with replacement; the
      split is made on DISTINCT questions (a question drawn k times contributes k copies of its verdicts to one
      side only, so no question sits in both halves), B = 125 resamples x 16 halvings each; the 2.5 / 97.5
      percentiles of the per-resample R_a. STATED BIAS: a resample's half is a multiplicity-weighted set with
      sum of squared weights ~n, so it carries the noise of an n/4 sample and the raw percentile interval sits
      below the point (a smoke run put the key board at ~0.85 against its 0.9135). The published interval is
      the percentile interval RECENTRED on the point (bias printed), and beside it a delete-one-question
      jackknife on the first 10 fixed halvings (no duplication) as the bias-free check; the class per anchor is
      read on the LOWER of the two lower bounds, under the framework's three classes; the certifiability list is
      read on the merged 20-model board (the board the record publishes per-anchor claims on) with the x12
      board and the key beside it.
  * McNemar-established rule: this test produces no wrong-direction count (nothing is compared to the key's
    direction), so there is nothing for systematic_budget.mcnemar_edge / established to attach to; stated so.
    KEY DENOMINATOR of every instrument here: each anchor's JUDGED questions (the 2,811 routed + judged
    questions of the pool of record p2dca21ab5f4ef3ae, ~201 per anchor), never the pool's routed questions.
  * Meta-Llama-3-70B-Instruct is excluded everywhere (asserted absent from both caches).
  * Outputs: experiment_results/x12_crossdomain/profile_interval_all.txt; the per-seed / per-fold / per-resample
    tables are cached as JSON under the session scratchpad (block1/).
"""
import os, sys, math, random, json, sqlite3, time
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import pool_guard
import profile_reliability as pr
import x20_merged as xm

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "profile_interval_all.txt")
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "claude", "Z--FAC-TUBerlin-THESIS-TaxoArena",
                       "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad", "block1")
TREE = "bareq512_s42"
POOL = "p2dca21ab5f4ef3ae"
BAR = 0.70
SEED = 7
REPS = pr.REPS          # 40
Z = 1.96
EXCLUDE = "Meta-Llama-3-70B-Instruct"
SWEEP_SEEDS = 10        # item says >= 8
SIZES6 = [50, 75, 100, 150, 200, 210]
SIZES14 = [50, 75, 100, 115]
BOOT_B = 125          # question-bootstrap resamples per board
BOOT_H = 16           # halvings per resample (mean over them is the per-resample statistic)
JACK_H = 10           # fixed halvings used by the delete-one-question jackknife
sb = pr.sb


# ----------------------------------------------------------------------------------------------- helpers
def spearman(xs, ys):
    def rank(v):
        idx = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(idx):
            j = i
            while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]: j += 1
            for k in range(i, j + 1): r[idx[k]] = (i + j) / 2.0 + 1
            i = j + 1
        return r
    return pr.pearson(rank(xs), rank(ys))


def jack(full, loo, scale=Z):
    n = len(loo); mean = sum(loo) / n
    se = math.sqrt((n - 1) / n * sum((v - mean) ** 2 for v in loo))
    return se, full - scale * se, full + scale * se


def mean_sd(v):
    v = [x for x in v if x == x]
    if not v: return float("nan"), float("nan"), 0
    mu = sum(v) / len(v)
    sd = math.sqrt(sum((x - mu) ** 2 for x in v) / (len(v) - 1)) if len(v) > 1 else 0.0
    return mu, sd, len(v)


def pct(v, p):
    v = sorted(x for x in v if x == x)
    if not v: return float("nan")
    k = (len(v) - 1) * p; f = int(math.floor(k)); c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def halvings_fixed(cells, qsel, build, models, rng, reps=REPS, min_cell=25, sides=None):
    """Line-for-line mirror of profile_reliability.reliability that RETURNS the per-halving profile pairs.
    If `sides` is a list, the per-halving {cell: (side1 qids, side2 qids)} is appended to it."""
    per_rep = []
    for _ in range(reps):
        P = []; sd = {}
        for c, cqs in cells.items():
            cc = [q for q in cqs if q in qsel]
            if len(cc) < 2 * min_cell:
                continue
            cc = sorted(cc); rng.shuffle(cc)
            mid = len(cc) // 2
            d1 = build(cc[:mid]); d2 = build(cc[mid:])
            if not d1 or not d2:
                continue
            sd[c] = (cc[:mid], cc[mid:])
            for m in models:
                if m in d1 and m in d2:
                    P.append((c, m, d1[m], d2[m]))
        per_rep.append(P)
        if sides is not None: sides.append(sd)
    return per_rep


def board_r(P, drop=None, min_points=50):
    Q = [p for p in P if p[0] != drop] if drop is not None else P
    if len(Q) < min_points: return float("nan")
    D = pr.demean_by_model(Q)
    return pr.pearson([p[2] for p in D], [p[3] for p in D])


def mean_r(per_rep, drop=None):
    return mean_sd([board_r(P, drop) for P in per_rep])


def per_anchor_r(P):
    """{anchor: (profile r = demeaned Pearson across models, raw Spearman, raw Pearson)}"""
    D = pr.demean_by_model(P)
    byc = defaultdict(list); byraw = defaultdict(list)
    for p, q in zip(P, D):
        byc[p[0]].append((q[2], q[3])); byraw[p[0]].append((p[2], p[3]))
    out = {}
    for c in byc:
        xs, ys = zip(*byc[c]); rx, ry = zip(*byraw[c])
        out[c] = (pr.pearson(list(xs), list(ys)), spearman(list(rx), list(ry)), pr.pearson(list(rx), list(ry)))
    return out


def cell_boot(per_rep, rng, n=50):
    """Resample cells with replacement inside each halving (the review's adv_profile reading)."""
    out = []
    for P in per_rep:
        cells = sorted({p[0] for p in P}); byc = defaultdict(list)
        for p in P: byc[p[0]].append(p)
        for _ in range(n):
            pick = [cells[rng.randrange(len(cells))] for _ in cells]
            Q = [(i, p[1], p[2], p[3]) for i, c in enumerate(pick) for p in byc[c]]
            v = board_r(Q)
            if v == v: out.append(v)
    return out


def classify(point, lo):
    if point != point: return "n/a"
    if point >= BAR and lo >= BAR: return "PASS"
    if point >= BAR: return "PASS-WITH-INTERVAL"
    return "FAIL"


def fit_sb_form(pairs):
    """Least squares c in R(S) = S / (S + c) over (S, R) rows; grid + refinement. Returns c (nan if R<=0 everywhere)."""
    pts = [(S, R) for S, R in pairs if R == R and 0 < R < 1]
    if len(pts) < 2: return float("nan")
    def sse(c): return sum((R - S / (S + c)) ** 2 for S, R in pts)
    best = min((sse(c), c) for c in [x * 2.0 for x in range(1, 2000)])[1]
    lo, hi = max(0.5, best - 2), best + 2
    for _ in range(60):
        m1 = lo + (hi - lo) / 3; m2 = hi - (hi - lo) / 3
        if sse(m1) < sse(m2): hi = m2
        else: lo = m1
    return (lo + hi) / 2


def crossing_from(S, R):
    """Spearman-Brown extrapolation of the 0.70 crossing from a row (S, R). R <= 0 -> inf (no finite size
    reaches the bar on that reading); R >= 1 -> 0 (already above the bar at any size); nan stays nan."""
    if R != R: return float("nan")
    if R <= 0: return float("inf")
    if R >= 1: return 0.0
    return S * (BAR * (1 - R)) / (R * (1 - BAR))


def fmt_x(v):
    if v != v: return "nan"
    if v == float("inf"): return "inf"
    return "%.0f" % v


# ----------------------------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    L = []
    os.makedirs(SCRATCH, exist_ok=True)
    cache = {}

    # ---------------- data ----------------
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows12 = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    rows_m, n12, n20 = xm.merged_rows()
    models12 = sorted(p8.ARENA12)
    models20 = sorted({r[0] for r in rows_m} | {r[1] for r in rows_m})
    m12_in_cache = sorted({r[0] for r in rows12} | {r[1] for r in rows12})

    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in models20 and m != EXCLUDE:
            K[q][m] = int(c or 0)

    route = r512.primary_routing(TREE)
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anc = r512.anchor_fn(nodes)
    by12 = defaultdict(list); bym = defaultdict(list)
    for a, b, q, w, _ in rows12: by12[q].append((a, b, q, w))
    for a, b, q, w, _ in rows_m: bym[q].append((a, b, q, w))
    qs12 = sorted(set(route) & set(by12)); qsm = sorted(set(route) & set(bym))
    qs = qs12; qsel = set(qs)
    anc_cells = defaultdict(list); leaf_cells = defaultdict(list)
    for q in qs:
        anc_cells[anc(route[q])].append(q); leaf_cells[route[q]].append(q)
    usable = {c: v for c, v in anc_cells.items() if len(v) >= 50}          # same dict order as the recorded runs
    anchors = list(usable)
    leaf50 = {c: v for c, v in leaf_cells.items() if len(v) >= 50}
    leaf25 = {c: v for c, v in leaf_cells.items() if len(v) >= 26}
    six = sorted(anc_cells, key=lambda c: -len(anc_cells[c]))[:6]

    L.append("=== PROFILE-INTERVAL-ALL: intervals on every reliability number, the crossing as a range, per-anchor certifiability ===")
    L.append("  registered by reference at eaf1dbf (FRAMEWORK.md item 9, commit 8d77f7b); zero calls; pool of record %s" % POOL)
    L.append("")
    L.append("--- DATA CHECK (the object, before any stratum is read) ---")
    chk = [("x12 cache verdicts (valid) = 9,142", len(rows12) == 9142, len(rows12)),
           ("merged = x12 9,142 + x20 12,394 = 21,536", (n12, n20, len(rows_m)) == (9142, 12394, 21536), (n12, n20, len(rows_m))),
           ("x12 cache model set == ARENA12 (12 models)", m12_in_cache == models12, len(m12_in_cache)),
           ("merged model set has 20 models and contains ARENA12", len(models20) == 20 and set(models12) <= set(models20), len(models20)),
           ("%s absent from both caches and the key rows read" % EXCLUDE, EXCLUDE not in models20 and EXCLUDE not in m12_in_cache, EXCLUDE in models20),
           ("every judged question is in the reserved pool %s" % POOL, set(bym) <= pool and set(by12) <= pool, len(set(bym) - pool)),
           ("merged judged question set == x12 judged question set", set(bym) == set(by12), (len(bym), len(by12))),
           ("routed & judged questions = 2,811", len(qs12) == 2811 and len(qsm) == 2811, (len(qs12), len(qsm))),
           ("14 anchors, all >= 50 questions", len(usable) == 14 and len(anc_cells) == 14, (len(anc_cells), len(usable))),
           ("8 leaves >= 50 questions (the recorded leaf instrument)", len(leaf50) == 8, len(leaf50)),
           ("six largest anchors = the six cells of the recorded S=200 row", set(six) == {c for c, v in anc_cells.items() if len(v) >= 200}, six)]
    ok = True
    for name, good, val in chk:
        ok &= bool(good); L.append("  [%s] %s  (%s)" % ("ok" if good else "FAIL", name, val))
    L.append("  anchors (judged q): " + ", ".join("%s %d" % (c, len(usable[c])) for c in anchors))
    L.append("  KEY DENOMINATOR: each anchor's JUDGED questions (2,811 routed+judged questions of %s, %.1f per anchor)," % (POOL, len(qs) / 14))
    L.append("  halved into two disjoint sides; a half-profile is the Bradley-Terry fit (rj.mm_fit via judge_free_tests.board_from)")
    L.append("  on that side's verdicts, or the key's per-question correctness rate on that side.")
    L.append("  McNEMAR-ESTABLISHED RULE: no wrong-direction count is produced here (no separation is compared to the key's")
    L.append("  direction), so systematic_budget.mcnemar_edge / established have nothing to attach to. Stated, not applied.")
    if not ok:
        L.append("  DATA CHECK FAILED - stopping before any stratum is read.")
        txt = "\n".join(L); print(txt); open(OUT, "w", encoding="utf-8").write(txt + "\n"); return

    # ---------------- builders ----------------
    def jb_for(by, models):
        def jb(cqs):
            rs = [r for q in cqs for r in by[q]]
            if len({r[2] for r in rs}) < 10: return None
            return jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in rs], models)
        return jb

    def kb_for(models):
        def kb(cqs):
            d = {}
            for m in models:
                v = [K[q][m] for q in cqs if q in K and m in K[q]]
                if v: d[m] = sum(v) / len(v)
            return d if len(d) == len(models) else None
        return kb

    boards = [("x12 judge, 12 rows", jb_for(by12, models12), models12),
              ("MERGED judge, 20 rows", jb_for(bym, models20), models20),
              ("key, 12 rows", kb_for(models12), models12),
              ("key, 20 rows", kb_for(models20), models20)]

    # =====================================================================================================
    # (1) every recorded reliability number, with intervals
    # =====================================================================================================
    L.append("")
    L.append("=== (1) EVERY RELIABILITY NUMBER WITH A LEAVE-ONE-CELL-OUT JACKKNIFE (fixed halvings / re-halved) AND A CELL-BOOTSTRAP ===")
    L.append("  instrument: profile_reliability.reliability, %d halvings, seed Random(%d), min_cell 25 (13 on the 25-floor leaf row);" % (REPS, SEED))
    L.append("  R = Spearman-Brown of the mean r; jackknife SE on the R scale, z = 1.96; class read on the LOWEST lower bound.")
    L.append("  %-24s %-8s %5s %6s %7s %7s %7s  %-17s %-17s %-17s %s"
             % ("board", "level", "cells", "q/cell", "r", "R(SB)", "halvSD", "jk FIXED 95%", "jk RE-HALVED 95%", "cell-boot 95%", "class"))
    levels = [("anchor", usable, 25), ("leaf(50)", leaf50, 25), ("leaf(25)", leaf25, 13)]
    sec1 = {}
    fixed_anchor = {}      # per-board fixed halvings at anchor level, reused by (3)
    fixed_sides = {}       # the halving assignments behind them (for the delete-one-question jackknife)
    for bname, build, models in boards:
        for lname, cells, mc in levels:
            sides_ = []
            per_rep = halvings_fixed(cells, qsel, build, models, random.Random(SEED), min_cell=mc, sides=sides_)
            rf, sdf, nf = mean_r(per_rep)
            cells_present = sorted({p[0] for P in per_rep for p in P})
            if lname == "anchor": fixed_anchor[bname] = per_rep; fixed_sides[bname] = sides_
            # fixed-halving LOCO
            loo_f = [sb(mean_r(per_rep, drop=c)[0]) for c in cells_present]
            R = sb(rf); se_f, lo_f, hi_f = jack(R, loo_f)
            # re-halved LOCO (anchor and leaf(50) only; the 25-floor row is a side instrument)
            if lname in ("anchor", "leaf(50)"):
                loo_r = []
                for c in cells_present:
                    sub = {k: v for k, v in cells.items() if k != c}
                    r_i, _, _ = pr.reliability(sub, qsel, build, models, random.Random(SEED), min_cell=mc)
                    loo_r.append(sb(r_i))
                se_r, lo_r, hi_r = jack(R, loo_r)
            else:
                se_r = lo_r = hi_r = float("nan"); loo_r = []
            cb = [sb(v) for v in cell_boot(per_rep, random.Random(99))]
            cb_lo, cb_hi = pct(cb, 0.025), pct(cb, 0.975)
            lows = [x for x in (lo_f, lo_r, cb_lo) if x == x]
            cls = classify(R, min(lows)) if lows else "n/a"
            qpc = sum(len(cells[c]) for c in cells_present) / max(1, len(cells_present))
            sec1[(bname, lname)] = dict(r=rf, R=R, sd=sdf, n=nf, cells=len(cells_present), qpc=qpc, se_f=se_f, lo_f=lo_f, hi_f=hi_f,
                                        se_r=se_r, lo_r=lo_r, hi_r=hi_r, cb_lo=cb_lo, cb_hi=cb_hi, cls=cls,
                                        loo_fixed=dict(zip(cells_present, loo_f)), loo_rehalved=dict(zip(cells_present, loo_r)))
            L.append("  %-24s %-8s %5d %6.0f %7.4f %7.4f %7.4f  [%6.4f, %6.4f]  %-17s  [%6.4f, %6.4f]  %s"
                     % (bname, lname, len(cells_present), qpc, rf, R, sb(rf + sdf) - R if sdf == sdf else float("nan"),
                        lo_f, hi_f, ("[%6.4f, %6.4f]" % (lo_r, hi_r)) if lo_r == lo_r else "n/a", cb_lo, cb_hi, cls))
            print("(1) done", bname, lname, "%.4f" % R, "%.0fs" % (time.time() - t0), flush=True)
    L.append("  halvSD = SB-transformed spread of one halving around the mean (the recorded '+-' figures were SE-of-mean over 40 halvings).")
    L.append("  Recorded values to reproduce: x12 anchor 0.6728 / key 0.9135; x12 leaf 0.2559 / 0.8135; merged anchor 0.7183 / key 0.9139;")
    L.append("  merged leaf 0.3648 / 0.8284; ANCHOR-PROFILE-INTERVAL re-halved intervals 0.6728 [0.4932, 0.8524] and 0.7183 [0.6076, 0.8291].")
    L.append("  leaf(25) is a 40-halving, 13-per-side instrument on leaves >= 26 q; it is NOT PROFILE-TREE-ROBUST's single-split 0.158.")
    cache["section1"] = {"%s | %s" % k: v for k, v in sec1.items()}

    # =====================================================================================================
    # (2) the size sweep: fixed 6-cell set and all-14 set, >= 8 seeds, crossing as a range
    # =====================================================================================================
    L.append("")
    L.append("=== (2) SIZE SWEEP ON A FIXED CELL SET, %d SEEDS PER SIZE; THE 0.70 CROSSING AS A RANGE ===" % SWEEP_SEEDS)
    L.append("  six largest anchors (fixed set): " + ", ".join("%s %d" % (c, len(anc_cells[c])) for c in six))
    L.append("  seed s: cut = Random(s).shuffle of each cell then the first S; halvings = fresh Random(s); s = 11+S (the recorded seed) then 1..%d."
             % (SWEEP_SEEDS - 1))
    L.append("  crossing estimators: (a) SB extrapolation from a row, S * 0.7(1-R) / (0.3 R); (c) least-squares c in R(S) = S/(S+c), crossing 7c/3;")
    L.append("  (d) leave-one-cell-out jackknife interval on R of the largest-S row, pushed through (a). Jackknife on fixed halvings.")
    sweep_boards = [("x12 judge", boards[0][1], models12), ("MERGED judge", boards[1][1], models20), ("key (12 rows)", boards[2][1], models12)]
    sec2 = {}
    for setname, cellset, sizes in (("SIX-CELL", six, SIZES6), ("ALL-14", anchors, SIZES14)):
        for bname, build, models in sweep_boards:
            L.append("")
            L.append("  --- %s set, %s ---" % (setname, bname))
            L.append("  %6s %5s  %-8s %-17s %-17s  %-14s %-17s %-25s" % ("S", "cells", "mean R", "R range (seeds)", "jk 95% (seed0)", "crossing(a)", "range over seeds", "union of jk intervals (d)"))
            per_size = {}
            for S in sizes:
                seeds = [11 + S] + list(range(1, SWEEP_SEEDS))
                rowsS = []
                for s in seeds:
                    rr_ = random.Random(s); cut = {}
                    for c in anc_cells:                        # dict order, as profile_reliability.py section 3 iterates
                        if c not in cellset: continue
                        vv = sorted(anc_cells[c]); rr_.shuffle(vv); cut[c] = vv[:S]
                    per_rep = halvings_fixed(cut, qsel, build, models, random.Random(s), min_cell=S // 2)
                    rS, sdS, nS = mean_r(per_rep)
                    R = sb(rS)
                    present = sorted({p[0] for P in per_rep for p in P})
                    loo = [sb(mean_r(per_rep, drop=c)[0]) for c in present]
                    se, lo, hi = jack(R, loo)
                    rowsS.append(dict(seed=s, r=rS, R=R, sd=sdS, n=nS, se=se, lo=lo, hi=hi, cells=len(present),
                                      cross=crossing_from(S, R), cross_lo=crossing_from(S, hi), cross_hi=crossing_from(S, lo)))
                per_size[S] = rowsS
                Rs = [x["R"] for x in rowsS]; cr = [x["cross"] for x in rowsS if x["cross"] == x["cross"]]
                cl = [x["cross_lo"] for x in rowsS if x["cross_lo"] == x["cross_lo"]]; ch = [x["cross_hi"] for x in rowsS if x["cross_hi"] == x["cross_hi"]]
                L.append("  %6d %5d  %8.4f [%6.4f, %6.4f]  [%6.4f, %6.4f]   %-14s %-17s %-25s"
                         % (S, rowsS[0]["cells"], sum(Rs) / len(Rs), min(Rs), max(Rs), rowsS[0]["lo"], rowsS[0]["hi"],
                            fmt_x(rowsS[0]["cross"]),
                            ("%s-%s" % (fmt_x(min(cr)), fmt_x(max(cr)))) if cr else "n/a",
                            ("[%s, %s]" % (fmt_x(min(cl)), fmt_x(max(ch)))) if cl and ch else "n/a"))
                print("(2) done", setname, bname, S, "%.4f" % (sum(Rs) / len(Rs)), "%.0fs" % (time.time() - t0), flush=True)
            # per-seed SB-form fit over the rows
            fits = []
            for i in range(SWEEP_SEEDS):
                pairs = [(S, per_size[S][i]["R"]) for S in sizes]
                c = fit_sb_form(pairs); fits.append(c * BAR / (1 - BAR) if c == c else float("nan"))
            fits_ok = [f for f in fits if f == f]
            Smax = sizes[-1]
            a_range = [x["cross"] for x in per_size[Smax] if x["cross"] == x["cross"]]
            a200 = [x["cross"] for x in per_size.get(200, []) if x["cross"] == x["cross"]]
            b_all = [x["cross"] for S in sizes for x in per_size[S] if x["cross"] == x["cross"]]
            d_lo = [x["cross_lo"] for x in per_size[Smax] if x["cross_lo"] == x["cross_lo"]]
            d_hi = [x["cross_hi"] for x in per_size[Smax] if x["cross_hi"] == x["cross_hi"]]
            measured_cross = [S for S in sizes if sum(x["R"] for x in per_size[S]) / SWEEP_SEEDS >= BAR]
            L.append("  (a) from S=%d over %d seeds: %s%s" % (Smax, SWEEP_SEEDS, ("%s-%s q/cell" % (fmt_x(min(a_range)), fmt_x(max(a_range)))) if a_range else "n/a",
                     ("   [from S=200: %s-%s, the row the record's 182-242 was read from]" % (fmt_x(min(a200)), fmt_x(max(a200)))) if a200 and Smax != 200 else ""))
            L.append("  (b) from every row over seeds: %s" % (("%s-%s" % (fmt_x(min(b_all)), fmt_x(max(b_all)))) if b_all else "n/a"))
            L.append("  (c) SB-form fit R(S)=S/(S+c) per seed: %s  (per seed: %s)"
                     % (("%s-%s" % (fmt_x(min(fits_ok)), fmt_x(max(fits_ok)))) if fits_ok else "n/a", ", ".join(fmt_x(f) for f in fits)))
            L.append("  (d) union over seeds of the jackknife interval on the S=%d crossing: %s"
                     % (Smax, ("[%s, %s]" % (fmt_x(min(d_lo)), fmt_x(max(d_hi)))) if d_lo and d_hi else "n/a"))
            L.append("  measured (not extrapolated) sizes whose seed-mean R >= %.2f: %s" % (BAR, measured_cross if measured_cross else "none in range"))
            sec2[(setname, bname)] = dict(per_size={str(S): v for S, v in per_size.items()}, fits=fits, a=a_range, a200=a200, b=b_all, d_lo=d_lo, d_hi=d_hi, measured=measured_cross)
    cache["section2"] = {"%s | %s" % k: v for k, v in sec2.items()}

    # the published range, hardest reading = widest over (a), (c) on the six-cell x12 judge (the record's object) and merged
    def pub_range(key):
        d = sec2[key]; pts = list(d["a"]) + [f for f in d["fits"] if f == f]
        lo_pts, hi_pts = (min(pts), max(pts)) if pts else (float("nan"), float("nan"))
        lo_int = min(d["d_lo"]) if d["d_lo"] else float("nan")
        hi_int = max(d["d_hi"]) if d["d_hi"] else float("nan")
        return lo_pts, hi_pts, lo_int, hi_int
    L.append("")
    L.append("  PUBLISHED CROSSING RANGES (point range over seeds and estimators (a)+(c); interval range = union of jackknife intervals (d)):")
    pubs = {}
    for key in (("SIX-CELL", "x12 judge"), ("SIX-CELL", "MERGED judge"), ("ALL-14", "x12 judge"), ("ALL-14", "MERGED judge"), ("SIX-CELL", "key (12 rows)"), ("ALL-14", "key (12 rows)")):
        lo_p, hi_p, lo_i, hi_i = pub_range(key); pubs[key] = (lo_p, hi_p, lo_i, hi_i)
        L.append("    %-9s %-14s point range %4s-%-4s q/cell   interval range [%s, %s]"
                 % (key[0], key[1], fmt_x(lo_p), fmt_x(hi_p), fmt_x(lo_i), fmt_x(hi_i)))
    L.append("  record to compare: six-cell x12 crossing 182-242 (8 seeds, S=200); all-14 ~410-450; '210' not quoted; MMLU-Pro anchors average 201.")
    L.append("  HARDEST READING on 'MMLU-Pro sits on the threshold': the ALL-14 range is the one that applies to the board as published")
    L.append("  (14 anchors, ~201 q/cell); the six-cell range applies only to the six largest categories.")
    for key in (("SIX-CELL", "x12 judge"), ("SIX-CELL", "MERGED judge")):
        d = sec2[key]; lo_p, hi_p, _, _ = pubs[key]
        if d["b"] and (min(d["b"]) < lo_p or max(d["b"]) > hi_p):
            L.append("    NOTE %s %s: estimator (b) over every row spans %s-%s, WIDER than the published point range; the fixed"
                     % (key[0], key[1], fmt_x(min(d["b"])), fmt_x(max(d["b"]))))
            L.append("         cell set is NOT Spearman-Brown-consistent across sizes, so the published range is a largest-row statement.")

    # =====================================================================================================
    # (3) per-anchor within-cell split-half with a question bootstrap; certifiability list
    # =====================================================================================================
    L.append("")
    L.append("=== (3) PER-ANCHOR WITHIN-CELL SPLIT-HALF WITH A QUESTION-BOOTSTRAP INTERVAL; CERTIFIABILITY LIST ===")
    L.append("  reading (i) PROFILE: half-profiles model-demeaned across the 14 anchors, r_a = Pearson across models inside anchor a;")
    L.append("  reading (ii) RAW ORDER: Spearman across models of the raw half-theta inside anchor a. Both SB to full length,")
    L.append("  mean over %d halvings (seed Random(%d)); bootstrap = questions resampled with replacement inside every anchor," % (REPS, SEED))
    L.append("  split on distinct questions, B = %d x %d halvings, percentile 2.5 / 97.5 of the per-resample R_a." % (BOOT_B, BOOT_H))
    L.append("  READING CHOSEN: FRAMEWORK.md's 'split-half of the within-anchor model order' is reading (ii); the certifiability list is")
    L.append("  read on reading (i) because it is the harder one on the programme's claim (a per-anchor row is a DEVIATION claim, and")
    L.append("  the raw order carries the global model spread every anchor shares); (ii) is printed and scored beside it.")
    L.append("  BOOTSTRAP BIAS, stated: with disjoint halves a resample's half is a multiplicity-weighted set whose sum of squared")
    L.append("  weights is ~n, so each half carries the noise of an n/4 sample, not n/2, and the raw percentile interval sits BELOW")
    L.append("  the point (the smoke run put the key board at ~0.85 against 0.9135). Published intervals are therefore (A) the")
    L.append("  bootstrap RECENTRED on the point (point + (percentile - bootstrap mean); the bias is printed) and (B) a delete-one-")
    L.append("  question jackknife on the first %d fixed halvings (no duplication, the bias-free check). The class is read on the" % JACK_H)
    L.append("  LOWER of the two lower bounds; the raw (uncentred) percentile interval is printed for the record, not read.")
    sec3 = {}

    def boot_split(cells, rng):
        cut1 = {}; cut2 = {}
        for c, cqs in cells.items():
            n = len(cqs); draw = [cqs[rng.randrange(n)] for _ in range(n)]
            mult = defaultdict(int)
            for q in draw: mult[q] += 1
            ids = sorted(mult); rng.shuffle(ids)
            s1 = []; s2 = []; acc = 0
            for q in ids:
                if acc < n / 2: s1.extend([q] * mult[q]); acc += mult[q]
                else: s2.extend([q] * mult[q])
            cut1[c] = s1; cut2[c] = s2
        return cut1, cut2

    def anchor_jackknife(per_rep, sides, build, models, H):
        """Delete-one-question jackknife of the per-anchor split-half r (profile and raw-order readings) on H fixed
        halvings: for each question q of anchor a and each halving, the side holding q is rebuilt without q, the
        anchor's (model, half1, half2) points replaced, and r_a recomputed; theta_-q = SB(mean over halvings)."""
        out = {}
        for a in anchors:
            loo_p = defaultdict(list); loo_r = defaultdict(list)
            for h in range(H):
                P = per_rep[h]
                if a not in sides[h]: continue
                s1, s2 = sides[h][a]
                others = [p for p in P if p[0] != a]
                d1 = {m: x for c, m, x, y in P if c == a}; d2 = {m: y for c, m, x, y in P if c == a}
                for side_idx, side in ((0, s1), (1, s2)):
                    for q in side:
                        new = build([x for x in side if x != q])
                        if not new: continue
                        if side_idx == 0: pa_ = [(a, m, new[m], d2[m]) for m in models if m in new and m in d2]
                        else: pa_ = [(a, m, d1[m], new[m]) for m in models if m in d1 and m in new]
                        rp, rr, _ = per_anchor_r(others + pa_)[a]
                        loo_p[q].append(rp); loo_r[q].append(rr)
            qs_a = sorted(loo_p)
            th_p = [sb(mean_sd(loo_p[q])[0]) for q in qs_a]; th_r = [sb(mean_sd(loo_r[q])[0]) for q in qs_a]
            th_p = [t for t in th_p if t == t]; th_r = [t for t in th_r if t == t]
            se_p = jack(0.0, th_p)[0] if len(th_p) > 1 else float("nan")
            se_r = jack(0.0, th_r)[0] if len(th_r) > 1 else float("nan")
            out[a] = (se_p, se_r, len(qs_a))
        return out

    for bname, build, models in boards:
        per_rep = fixed_anchor[bname]; sides = fixed_sides[bname]
        pa = defaultdict(lambda: ([], [], []))
        for P in per_rep:
            for c, (r1, r2, r3) in per_anchor_r(P).items():
                pa[c][0].append(r1); pa[c][1].append(r2); pa[c][2].append(r3)
        point = {c: (mean_sd(v[0]), mean_sd(v[1]), mean_sd(v[2])) for c, v in pa.items()}
        # delete-one-question jackknife on fixed halvings
        jk = anchor_jackknife(per_rep, sides, build, models, JACK_H)
        print("(3)", bname, "jackknife done", "%.0fs" % (time.time() - t0), flush=True)
        # question bootstrap
        rngb = random.Random(2026)
        boot = defaultdict(lambda: ([], []))     # anchor -> (profile R list, raw-order R list)
        boot_board = []
        for b in range(BOOT_B):
            acc = defaultdict(lambda: ([], [])); accb = []
            for h in range(BOOT_H):
                cut1, cut2 = boot_split(usable, rngb)
                P = []
                for c in anchors:
                    d1 = build(cut1[c]); d2 = build(cut2[c])
                    if not d1 or not d2: continue
                    for m in models:
                        if m in d1 and m in d2: P.append((c, m, d1[m], d2[m]))
                accb.append(board_r(P))
                for c, (r1, r2, _) in per_anchor_r(P).items():
                    acc[c][0].append(r1); acc[c][1].append(r2)
            boot_board.append(sb(mean_sd(accb)[0]))
            for c in acc:
                boot[c][0].append(sb(mean_sd(acc[c][0])[0])); boot[c][1].append(sb(mean_sd(acc[c][1])[0]))
            if b % 25 == 0: print("(3)", bname, "boot", b, "%.0fs" % (time.time() - t0), flush=True)
        L.append("")
        L.append("  --- %s ---" % bname)
        L.append("  %-18s %4s  %8s %-17s %7s %-17s %-17s %-19s | %8s %-17s %-17s %-19s"
                 % ("anchor", "q", "R_prof", "boot95 recentred", "bias", "jackknife 95%", "raw boot95", "class (profile)",
                    "R_raw", "boot95 recentred", "jackknife 95%", "class (raw order)"))
        rows3 = {}
        for c in sorted(anchors, key=lambda a: sb(point[a][0][0])):
            Rp = sb(point[c][0][0]); Rr = sb(point[c][1][0])
            plo, phi = pct(boot[c][0], 0.025), pct(boot[c][0], 0.975); pmu = mean_sd(boot[c][0])[0]
            rlo, rhi = pct(boot[c][1], 0.025), pct(boot[c][1], 0.975); rmu = mean_sd(boot[c][1])[0]
            bias_p = pmu - Rp; bias_r = rmu - Rr
            cplo, cphi = plo - bias_p, phi - bias_p; crlo, crhi = rlo - bias_r, rhi - bias_r
            se_p, se_r, nq = jk[c]
            jlo_p, jhi_p = Rp - Z * se_p, Rp + Z * se_p; jlo_r, jhi_r = Rr - Z * se_r, Rr + Z * se_r
            low_p = min(x for x in (cplo, jlo_p) if x == x); low_r = min(x for x in (crlo, jlo_r) if x == x)
            clsp = classify(Rp, low_p); clsr = classify(Rr, low_r)
            rows3[c] = dict(q=len(usable[c]), r_prof=point[c][0][0], R_prof=Rp, sd_prof=point[c][0][1],
                            boot_prof=(cplo, cphi), boot_prof_raw=(plo, phi), bias_prof=bias_p, jk_prof=(jlo_p, jhi_p), se_jk_prof=se_p, cls_prof=clsp,
                            r_raw=point[c][1][0], R_raw=Rr, boot_raw=(crlo, crhi), boot_raw_raw=(rlo, rhi), bias_raw=bias_r, jk_raw=(jlo_r, jhi_r), se_jk_raw=se_r,
                            cls_raw=clsr, R_rawpearson=sb(point[c][2][0]), boot_prof_all=boot[c][0], boot_raw_all=boot[c][1])
            L.append("  %-18s %4d  %8.4f [%6.4f, %6.4f] %+7.3f [%6.4f, %6.4f] [%6.4f, %6.4f] %-19s | %8.4f [%6.4f, %6.4f] [%6.4f, %6.4f] %-19s"
                     % (c, len(usable[c]), Rp, cplo, cphi, bias_p, jlo_p, jhi_p, plo, phi, clsp, Rr, crlo, crhi, jlo_r, jhi_r, clsr))
        bb_lo, bb_hi = pct(boot_board, 0.025), pct(boot_board, 0.975); bb_mu = mean_sd(boot_board)[0]
        Rb = sec1[(bname, "anchor")]["R"]
        L.append("  board-level R from the same question bootstrap: raw mean %.4f [%.4f, %.4f] vs recorded point %.4f (bias %+.4f);"
                 % (bb_mu, bb_lo, bb_hi, Rb, bb_mu - Rb))
        L.append("    recentred [%.4f, %.4f]; section (1) leave-one-anchor-out interval [%.4f, %.4f]"
                 % (bb_lo - (bb_mu - Rb), bb_hi - (bb_mu - Rb), sec1[(bname, "anchor")]["lo_f"], sec1[(bname, "anchor")]["hi_f"]))
        sec3[bname] = dict(rows=rows3, boot_board=boot_board)
    L.append("  halvSD (profile reading, per anchor) is in the cache; 'bias' = bootstrap mean minus point on the R scale.")
    cache["section3"] = {b: {"rows": {c: {k: v for k, v in r.items() if not k.endswith("_all")} for c, r in d["rows"].items()},
                             "boot_board_pct": [pct(d["boot_board"], 0.025), pct(d["boot_board"], 0.5), pct(d["boot_board"], 0.975)],
                             "boot_board_mean": mean_sd(d["boot_board"])[0]}
                         for b, d in sec3.items()}

    # certifiability list, primary = merged judge board, profile reading
    L.append("")
    L.append("  CERTIFIABILITY LIST (primary: MERGED judge board, PROFILE reading; x12 judge and key beside):")
    prim = sec3["MERGED judge, 20 rows"]["rows"]; x12r = sec3["x12 judge, 12 rows"]["rows"]; keyr = sec3["key, 20 rows"]["rows"]
    L.append("  %-18s %4s  %-40s %-40s %-12s" % ("anchor", "q", "MERGED judge (profile)", "x12 judge (profile)", "key20 R_prof"))
    counts = defaultdict(int)
    for c in sorted(anchors, key=lambda a: prim[a]["R_prof"]):
        counts[prim[c]["cls_prof"]] += 1
        L.append("  %-18s %4d  %-40s %-40s %8.4f"
                 % (c, prim[c]["q"], "%.4f [%.4f, %.4f] %s" % (prim[c]["R_prof"], prim[c]["boot_prof"][0], prim[c]["boot_prof"][1], prim[c]["cls_prof"]),
                    "%.4f [%.4f, %.4f] %s" % (x12r[c]["R_prof"], x12r[c]["boot_prof"][0], x12r[c]["boot_prof"][1], x12r[c]["cls_prof"]), keyr[c]["R_prof"]))
    L.append("  merged-board classes: %s" % dict(counts))
    L.append("  raw-order reading on the merged board: %s" % {k: sum(1 for c in anchors if prim[c]["cls_raw"] == k) for k in ("PASS", "PASS-WITH-INTERVAL", "FAIL")})

    # prediction: History, Health, Philosophy below 0.70 individually
    trio = ["History", "Health", "Philosophy"]
    L.append("")
    L.append("  PREDICTION 'History, Health, Philosophy below 0.70 individually':")
    for bname, rows3 in (("MERGED judge (profile)", prim), ("x12 judge (profile)", x12r)):
        below = [c for c in trio if rows3[c]["R_prof"] < BAR]
        others_below = [c for c in anchors if c not in trio and rows3[c]["R_prof"] < BAR]
        L.append("    %-24s below 0.70: %s of 3 (%s); other anchors also below: %d of 11 (%s)"
                 % (bname, len(below), ", ".join("%s %.3f" % (c, rows3[c]["R_prof"]) for c in trio), len(others_below),
                    ", ".join("%s %.3f" % (c, rows3[c]["R_prof"]) for c in others_below) or "none"))
    for bname, rows3 in (("MERGED judge (raw order)", prim), ("x12 judge (raw order)", x12r)):
        below = [c for c in trio if rows3[c]["R_raw"] < BAR]
        others_below = [c for c in anchors if c not in trio and rows3[c]["R_raw"] < BAR]
        L.append("    %-24s below 0.70: %s of 3 (%s); other anchors also below: %d of 11 (%s)"
                 % (bname, len(below), ", ".join("%s %.3f %s" % (c, rows3[c]["R_raw"], rows3[c]["cls_raw"]) for c in trio), len(others_below),
                    ", ".join("%s %.3f" % (c, rows3[c]["R_raw"]) for c in others_below) or "none"))
    trio_below_prim = sum(1 for c in trio if prim[c]["R_prof"] < BAR)
    trio_below_x12 = sum(1 for c in trio if x12r[c]["R_prof"] < BAR)
    trio_upper_below = sum(1 for c in trio if prim[c]["boot_prof"][1] < BAR)
    n_below_prim = sum(1 for c in anchors if prim[c]["R_prof"] < BAR)
    if trio_below_prim == 3 and trio_below_x12 == 3:
        pred = "CONFIRMED on the point estimates of both judge boards"
        if n_below_prim > 3:
            pred += "; NOT DISTINCTIVE: %d of 14 anchors are below 0.70 on the merged board, so the three are not the failing set but part of it" % n_below_prim
        if trio_upper_below < 3:
            pred += "; the bootstrap upper bound clears 0.70 for %d of the three, so 'below 0.70' is a point statement, not an interval one" % (3 - trio_upper_below)
    elif trio_below_prim == 0:
        pred = "FAILED: none of the three is below 0.70 on the merged board"
    else:
        pred = "PARTLY: %d of 3 below on the merged board, %d of 3 on x12" % (trio_below_prim, trio_below_x12)
    L.append("    -> %s" % pred)

    # =====================================================================================================
    # verdicts
    # =====================================================================================================
    L.append("")
    L.append("=== VERDICTS (criteria in the item's words) ===")
    six12 = pubs[("SIX-CELL", "x12 judge")]; sixm = pubs[("SIX-CELL", "MERGED judge")]; a1412 = pubs[("ALL-14", "x12 judge")]; a14m = pubs[("ALL-14", "MERGED judge")]
    def rng_s(t): return "%s-%s q/cell (interval union [%s, %s])" % (fmt_x(t[0]), fmt_x(t[1]), fmt_x(t[2]), fmt_x(t[3]))
    L.append("  (C1) 'crossing published as a range': PUBLISHED. Six-cell x12 judge %s;" % rng_s(six12))
    L.append("       six-cell MERGED judge %s; all-14 x12 %s; all-14 MERGED %s." % (rng_s(sixm), rng_s(a1412), rng_s(a14m)))
    meas6 = sec2[("SIX-CELL", "x12 judge")]["measured"]; meas6m = sec2[("SIX-CELL", "MERGED judge")]["measured"]
    L.append("       No single number replaces '210'; the six-cell range is the one the record's 182-242 refers to. Measured (not")
    L.append("       extrapolated) six-cell sizes at or above 0.70 by seed-mean R: x12 %s; MERGED %s. All-14 rows never reach 0.70 in range."
             % (meas6 if meas6 else "none", meas6m if meas6m else "none"))
    L.append("  (C2) 'per-anchor certifiability list': PUBLISHED above; merged-board classes %s on the profile reading;" % dict(counts))
    L.append("       raw-order reading %s." % {k: sum(1 for c in anchors if prim[c]["cls_raw"] == k) for k in ("PASS", "PASS-WITH-INTERVAL", "FAIL")})
    L.append("  (P)  'History, Health, Philosophy below 0.70 individually': %s" % pred)
    L.append("       raw-order reading, merged board: %d of 3 below 0.70 (%s); x12: %d of 3."
             % (sum(1 for c in trio if prim[c]["R_raw"] < BAR), ", ".join("%s %.3f" % (c, prim[c]["R_raw"]) for c in trio),
                sum(1 for c in trio if x12r[c]["R_raw"] < BAR)))
    board_cls = {k[0] + " / " + k[1]: v["cls"] for k, v in sec1.items() if k[1] == "anchor"}
    L.append("  (1)  board-level classes on the lowest lower bound: %s" % board_cls)
    L.append("  cache: %s" % os.path.join(SCRATCH, "profile_interval_all_cache.json"))
    L.append("  runtime %.0fs, zero LLM calls" % (time.time() - t0))

    json.dump(cache, open(os.path.join(SCRATCH, "profile_interval_all_cache.json"), "w"), indent=1, default=str)
    txt = "\n".join(L); print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
