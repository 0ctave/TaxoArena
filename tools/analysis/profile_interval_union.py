"""PROFILE-INTERVAL-ALL-UNION (registered 2026-09-17 at commit 62c4084, docs/judge_v2_program.md L5402-L5457; plan A2).
Zero calls. Key only. Pool paeec37aa28063c75.

  python tools/analysis/profile_interval_union.py --dry-run    # pool id, roster, 52 strata with reserved-side support; NO reliability number
  python tools/analysis/profile_interval_union.py --selftest   # synthetic key rows with planted profile structure, in-memory DB for the MATH-FIX read
  python tools/analysis/profile_interval_union.py --run        # writes experiment_results/multicorpus/profile_interval_all_union.txt (+ _strata.csv) ONCE

THE REGISTRATION, quoted (docs/judge_v2_program.md L5402-L5457):
  Question. FRAMEWORK L258 records "union strata have no reliability measurement at all" and the union is the only place
  a profile has a routing consequence (MC-E2E clean +3.38pp, seeds +4.37 / +2.43 / +3.34). PROFILE-INTERVAL-ALL delivered
  the per-anchor certifiability list on MMLU-Pro (item 9); the union half was never registered. Question: on the 18-model
  key rows of the union, per (source, domain) stratum, is the within-stratum model order split-half reliable at the
  registered 0.70 bar, with an interval, so that each stratum carries a class (PASS / PASS-WITH-INTERVAL / FAIL), and what
  is the board-level reliability over the 52 strata and over the 6 sources? The profile may then grow from 14 cells to up
  to 66, each with a class; the test adds or marks rows, it certifies no order and routes nothing.
  Hygiene. Key only, zero judge calls, no reference. multicorpus_cache_v1.db opened mode=ro (21,606 questions x 18 models,
  388,908 eval_results rows; the MATH column read from eval_results_mathfix, MATH-FIX, never the ingested MATH rows).
  Reserved side ONLY: the 6,482 question ids of pool paeec37aa28063c75 as frozen in
  experiment_configs/reserved_pool_frozen_paeec.json (52 keys "SOURCE/domain" -> id lists; the file IS the stratum
  definition), verified by `pool_guard.py --pool paeec37aa28063c75` as the first printed line; the DB holds a second
  6,482-row pool (pa95843d826d40ffd) and any pool but paeec37aa28063c75 is refused by id. Strata are never read from
  eval_results.category or the text-keyed ground_truth_category (shared across corpora, last writer wins); the routing
  CSV of record, experiment_results/multicorpus/union_s42/seed_42/validation/MAIN_union_routing_queries.csv (6,482 rows,
  true_key column), is asserted equal to the frozen file's stratum assignment before anything runs. The TRAIN side is
  never opened. The 18-model roster is not the 46: reliability is roster-dependent (PROFILE-RELIABILITY-X20), so no level
  of this test is compared to the 46-model 0.9135 or the merged key-20 rows; the MMLU-Pro strata are printed beside
  PROFILE-INTERVAL-ALL's key rows with the roster named on both sides and no comparison claimed.
  Instrument. profile_reliability.reliability, the recorded estimator, unchanged: 40 disjoint halvings of each stratum's
  reserved questions (random.Random(7)), per-half model accuracy vectors, model-demeaned Pearson r between half-profiles,
  Spearman-Brown to full length, averaged over the 40 halvings. Per stratum (the PROFILE-INTERVAL-ALL per-anchor
  instrument): split-half of the within-stratum model order over the 18 models, 40 halvings, SB, with the class read on the
  LOWER of a recentred question bootstrap (B = 125) and a delete-one-question jackknife, exactly as profile_interval_all.py
  reads it; halving SD printed. Support floor (registrar's decision, stated before any number): a stratum with fewer than
  25 reserved questions prints its counts and the class UNSUPPORTED, not FAIL. Board-level: R over all 52 strata and over
  the 6 source-level cells, each with a leave-one-stratum-out (leave-one-source-out) jackknife interval and the halving
  SD; R vs stratum size printed as the support curve.
  Readouts and criteria (scored HELD / FAILED; denominators = the stratum's reserved question count, printed per row):
   (C1) every stratum with >= 25 reserved questions receives a class (PASS: lower bound >= 0.70; PASS-WITH-INTERVAL: point
        >= 0.70, lower < 0.70; FAIL: point < 0.70), with R, halving SD, both lower bounds and n; strata below 25: counts only.
   (C2) board-level R over the 52 strata with its jackknife interval and halving SD (the number FRAMEWORK L258 lacks).
   (C3) board-level R per source (6 cells) with intervals; the 14 MMLU-Pro strata's classes beside PROFILE-INTERVAL-ALL's
        merged key-20 classes, roster named, no comparison of levels claimed.
  Predictions (the plan's, recorded blind): MMLU-Pro-source strata PASS (scored: all 14 PASS); MATH / GPQA / MuSR / IFEval
  strata mostly FAIL by support (scored: more than half of those 14 strata FAIL or UNSUPPORTED; the plan cites "1,324 /
  1,192 / 756 / 541 q", which are the CORPUS totals of multi_corpus_design.md L250; the reserved-side supports are
  398 / 358 / 227 / 162 per reserved_pool_meta, split over 7 / 3 / 3 / 1 strata, recorded here so the prediction is scored on
  the reserved denominators). No prediction is registered for BBH's 24 strata (~72 q each): they are printed.
  Falsifier. None in the plan's sense: the test adds or marks rows. What it overturns is a sentence, not a result:
  FRAMEWORK L258's "union strata have no reliability measurement at all" becomes false whatever the values (a bracket by
  insertion after the outcome). If the 14 MMLU-Pro strata do NOT all PASS on the 18-model key, the key-built profile's
  reliability is shown roster- and cell-dependent at the stratum level (a finding beside PROFILE-RELIABILITY's 0.9135,
  not a refutation of it, the rosters differing).
  Cost and consequence. 0 calls; minutes of CPU; writes experiment_results/multicorpus/profile_interval_all_union.txt
  (+ profile_interval_all_union_strata.csv) once.

IMPLEMENTATION AND THE READINGS CHOSEN WHERE THE REGISTRATION IS SILENT (each stated in the output too):
  * The pool. pool_guard.assert_pool_of_record("paeec37aa28063c75") is the first statement (id file hashes to the id,
    reserved_pool rows hash to it, sets equal); the first printed line is `reserved_pool_id=paeec37aa28063c75`. The DB's
    reserved_pool is read for THAT id only; a reader asked for any other id (pa95843d826d40ffd is the coexisting one)
    raises before any query. The stratum of a question is the frozen file's key; eval_results.category, the legacy side flag and
    corpus_questions.domain are never the stratum (corpus_questions is read once, in the data check, to assert the frozen
    keys agree with (source, domain), MMLU_PRO_LB <-> MMLU_PRO).
  * The routing CSV of record has NO question-id column (columns: true_key, true_source, rule, leaf_id, ...). "Asserted
    equal to the frozen file's stratum assignment" is therefore implemented at the level the CSV supports: the same 52
    keys, the same per-key row count (6,482 in total) and true_source == the key's source on every row. Row-level identity
    of ids is NOT checkable from that file; the sentence is implemented literally as far as the object allows, and said so.
  * The key. eval_results.is_correct for every pool question of BBH / GPQA / IFEVAL / MMLU_PRO_LB / MUSR; for the 398
    MATH pool questions ONLY eval_results_mathfix.is_correct (asserted present for all 398 x 18; the ingested MATH rows
    are never read into the key). Every pool question has 18 rows or the run refuses. Meta-Llama-3-70B-Instruct asserted
    absent from the roster.
  * The instrument. profile_reliability.reliability is imported and called unchanged. Its `min_cell` argument (the
    per-HALF floor, default 25 = a 50-question cell floor in the recorded MMLU-Pro runs) is set to 12 so that every
    stratum with >= 25 reserved questions contributes, which is the registered support floor; the default-argument
    reading (min_cell 25, i.e. strata >= 50 q only) is printed beside as the recorded-default variant. No stratum of this
    pool is below 25 (smallest: MATH/Counting & Probability 37), so UNSUPPORTED is expected empty; the class exists and
    is exercised by --selftest.
  * Per-stratum reading. As profile_interval_all.py section (3): reading (i) PROFILE = each half's model vector demeaned
    by model across ALL cells of the board (the 52 strata), r_s = Pearson across the 18 models of the two halves'
    deviations inside stratum s; reading (ii) RAW ORDER = Spearman across models of the raw half-accuracies. Both SB,
    mean over 40 halvings (Random(7)). The class is read on reading (i) (the deviation claim, the harder one), (ii) is
    printed beside. Interval (A): question bootstrap inside every stratum (resample with replacement, split on distinct
    questions so no question sits on both sides), B = 125 x 16 halvings, 2.5 / 97.5 percentiles RECENTRED on the point
    (bias printed; the raw percentile interval is printed, not read). Interval (B): delete-one-question jackknife on the
    first 10 fixed halvings. Class on the LOWER of the two lower bounds.
  * Board-level. (C2) R over the 52 strata: leave-one-stratum-out jackknife two ways (fixed halvings; re-halved with a
    fresh Random(7)), halving SD; the class of the number on the lowest lower bound is printed for the record (the
    registration asks for the number and its interval, not a class). Over the 6 source-level cells (each source's
    reserved questions pooled into one cell, demeaned across the 6): leave-one-source-out jackknife, both ways. (C3)
    "R per source": read as R over each source's OWN strata (leave-one-stratum-out), which is undefined by construction
    for IFEval (one stratum: model-demeaning leaves nothing to correlate, exactly profile_reliability's whole-pool note);
    the 6-cell reading above is the other reading and both are printed. Support curve: per-stratum R_prof against n,
    and binned means.
  * Predictions scored exactly as written: P1 HELD iff all 14 MMLU_PRO_LB strata have class PASS (PASS-WITH-INTERVAL
    counts as not PASS; the split is printed); P2 HELD iff more than half (>= 8) of the 14 MATH / GPQA / MUSR / IFEVAL
    strata are FAIL or UNSUPPORTED. BBH's 24 strata: printed, not scored.
  * Rosters. This test: the 18-model union roster of multicorpus_cache_v1.db. PROFILE-INTERVAL-ALL's key rows beside the
    14 MMLU_PRO_LB strata are the merged 20-model roster on the 2,811 judged questions of pool p2dca21ab5f4ef3ae (read
    from experiment_results/x12_crossdomain/profile_interval_all.txt, block "--- key, 20 rows ---"); different roster,
    different pool, different question sets; no comparison of levels is claimed.
  * McNemar-established rule: no wrong-direction count is produced (nothing is compared to a judge's direction), so
    systematic_budget.mcnemar_edge / established have nothing to attach to. Stated, not applied.
  * "Once": --run refuses if the outcome file already exists. Every DB is opened mode=ro. The TRAIN side is never read
    (only pool ids are ever looked up in eval tables).
"""
import os, sys, csv, math, json, random, sqlite3, time, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
import profile_reliability as pr

POOL = pool_guard.UNION_POOL                     # paeec37aa28063c75
REFUSED_POOL = "pa95843d826d40ffd"               # the coexisting 6,482-row pool; refused by id
ID_FILE = os.path.join(ROOT, "experiment_configs", "reserved_pool_frozen_paeec.json")
CSV_OF_RECORD = os.path.join(ROOT, "experiment_results", "multicorpus", "union_s42", "seed_42", "validation", "MAIN_union_routing_queries.csv")
PIA_TXT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "profile_interval_all.txt")
OUT_DIR = os.path.join(ROOT, "experiment_results", "multicorpus")
OUT_TXT = os.path.join(OUT_DIR, "profile_interval_all_union.txt")
OUT_CSV = os.path.join(OUT_DIR, "profile_interval_all_union_strata.csv")

EXCLUDE = "Meta-Llama-3-70B-Instruct"
N_MODELS = 18
N_POOL = 6482
N_STRATA = 52
SOURCES = ("MMLU_PRO_LB", "BBH", "MATH", "MUSR", "IFEVAL", "GPQA")
SOURCE_OF_CORPUS = {"MMLU_PRO_LB": "MMLU_PRO"}   # frozen-key source -> corpus_questions.source
EXPECTED_SUPPORT = {"MATH": (398, 7), "GPQA": (358, 3), "MUSR": (227, 3), "IFEVAL": (162, 1), "BBH": (1728, 24), "MMLU_PRO_LB": (3609, 14)}
PREDICTED_FAIL_SOURCES = ("MATH", "GPQA", "MUSR", "IFEVAL")

BAR = 0.70
SEED = 7
REPS = pr.REPS            # 40
FLOOR = 25                # registered support floor (reserved questions per stratum)
MIN_CELL = 12             # per-half floor passed to profile_reliability.reliability so that n >= 25 contributes
BOOT_B = 125
BOOT_H = 16
JACK_H = 10
Z = 1.96
sb = pr.sb


# ----------------------------------------------------------------------------------------------- helpers (mirrors of profile_interval_all.py)
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
    loo = [v for v in loo if v == v]
    n = len(loo)
    if n < 2: return float("nan"), float("nan"), float("nan")
    mean = sum(loo) / n
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


def classify(point, lo, n):
    if n < FLOOR: return "UNSUPPORTED"
    if point != point: return "n/a"
    if point >= BAR and lo == lo and lo >= BAR: return "PASS"
    if point >= BAR: return "PASS-WITH-INTERVAL"
    return "FAIL"


def halvings_fixed(cells, qsel, build, models, rng, reps=REPS, min_cell=MIN_CELL, sides=None):
    """Line-for-line mirror of profile_reliability.reliability that RETURNS the per-halving profile pairs."""
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


def per_cell_r(P):
    """{cell: (profile r = demeaned Pearson across models, raw Spearman)}"""
    D = pr.demean_by_model(P)
    byc = defaultdict(list); byraw = defaultdict(list)
    for p, q in zip(P, D):
        byc[p[0]].append((q[2], q[3])); byraw[p[0]].append((p[2], p[3]))
    out = {}
    for c in byc:
        xs, ys = zip(*byc[c]); rx, ry = zip(*byraw[c])
        out[c] = (pr.pearson(list(xs), list(ys)), spearman(list(rx), list(ry)))
    return out


def fmt(v, w=6, d=4):
    return ("%*.*f" % (w, d, v)) if v == v else ("%*s" % (w, "nan"))


# ----------------------------------------------------------------------------------------------- data
def load_strata():
    """{key: [ids]} exactly as the frozen id file lists them (judgeable ids; this pool has no sentinels)."""
    return {k: list(v) for k, v in pool_guard.judgeable(pool_guard.pool_file_ids(POOL)).items()}


def check_csv_of_record(strata, path=CSV_OF_RECORD):
    """The routing CSV of record has no question-id column: equality with the frozen file is asserted at the level the
    object supports (same 52 keys, same per-key row counts, true_source == key source on every row). Returns (n_rows, msgs)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    cnt = Counter(r["true_key"] for r in rows)
    msgs = []
    if "true_key" not in rows[0]:
        raise SystemExit("[CSV-OF-RECORD] no true_key column in %s" % path)
    if set(cnt) != set(strata):
        raise SystemExit("[CSV-OF-RECORD] key set differs from the frozen file: %s" % sorted(set(cnt) ^ set(strata)))
    bad = [k for k in strata if cnt[k] != len(strata[k])]
    if bad:
        raise SystemExit("[CSV-OF-RECORD] per-key counts differ from the frozen file on %s" % bad)
    if len(rows) != sum(len(v) for v in strata.values()):
        raise SystemExit("[CSV-OF-RECORD] %d rows, frozen file %d ids" % (len(rows), sum(len(v) for v in strata.values())))
    if any(r["true_source"] != r["true_key"].split("/", 1)[0] for r in rows):
        raise SystemExit("[CSV-OF-RECORD] true_source disagrees with the key's source on some row")
    msgs.append("routing CSV of record: %d rows, %d keys, per-key counts == frozen file, true_source == key source (no id column: row-level identity not checkable)" % (len(rows), len(cnt)))
    return len(rows), msgs


def guarded_pool_rows(conn, pool_id):
    """The only reader of reserved_pool: any id but the pool of record is refused before a query is issued."""
    if pool_id != POOL:
        raise SystemExit("[POOL-REFUSED] pool %s is not the pool of record %s; refused by id" % (pool_id, POOL))
    return pool_guard.pool_rows(conn, pool_id)


def load_key(conn, strata, models=None):
    """K[q] = np.array of 18 is_correct in roster order. MATH pool questions from eval_results_mathfix ONLY; every other
    pool question from eval_results. Refuses unless every pool question has all 18 rows on its designated table."""
    pool_ids = {q for v in strata.values() for q in v}
    math_ids = {q for k, v in strata.items() if k.split("/", 1)[0] == "MATH" for q in v}
    if models is None:
        models = sorted(m for (m,) in conn.execute("SELECT DISTINCT model_name FROM eval_results"))
    if EXCLUDE in models:
        raise SystemExit("[ROSTER] %s present in eval_results; excluded by standing rule" % EXCLUDE)
    mi = {m: i for i, m in enumerate(models)}
    K = {}
    have = Counter()
    for q, m, c in conn.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if q in pool_ids and q not in math_ids and m in mi:
            K.setdefault(q, np.full(len(models), np.nan))[mi[m]] = int(c or 0); have[q] += 1
    for q, m, c in conn.execute("SELECT question_id, model_name, is_correct FROM eval_results_mathfix"):
        if q in math_ids and m in mi:
            K.setdefault(q, np.full(len(models), np.nan))[mi[m]] = int(c or 0); have[q] += 1
    missing = [q for q in pool_ids if have[q] != len(models)]
    if missing:
        raise SystemExit("[KEY] %d pool questions lack a full %d-model key row (first: %s); refusing" % (len(missing), len(models), sorted(missing)[:5]))
    return K, models


def make_key_build(K, models):
    def key_build(cqs):
        if not cqs: return None
        M = np.stack([K[q] for q in cqs]).mean(axis=0)
        return {m: float(M[i]) for i, m in enumerate(models)}
    return key_build


# ----------------------------------------------------------------------------------------------- per-stratum intervals
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


def stratum_jackknife(per_rep, sides, K, models, cells, H):
    """Delete-one-question jackknife of the per-stratum split-half r (profile and raw-order readings) on H fixed halvings.
    For each halving and each question q of stratum s, the side holding q is rebuilt without q (mean over the side minus q),
    the model means used by the demeaning are updated for that one point, and r_s recomputed. Vectorised over the side's
    questions; identical in value to profile_interval_all.anchor_jackknife's rebuild-and-recompute."""
    nm = len(models); mi = {m: i for i, m in enumerate(models)}
    out = {}
    for s in cells:
        loo_p = defaultdict(list); loo_r = defaultdict(list)
        for h in range(H):
            P = per_rep[h]
            if s not in sides[h]: continue
            Sx = np.zeros(nm); Sy = np.zeros(nm); C = np.zeros(nm)
            d1 = np.zeros(nm); d2 = np.zeros(nm)
            for c, m, x, y in P:
                i = mi[m]; Sx[i] += x; Sy[i] += y; C[i] += 1
                if c == s: d1[i] = x; d2[i] = y
            for side_idx, side in enumerate(sides[h][s]):
                n_side = len(side)
                if n_side < 2: continue
                A = np.stack([K[q] for q in side])                     # n_side x nm
                tot = A.sum(axis=0)
                new = (tot[None, :] - A) / (n_side - 1)                # profile of the side without row q
                if side_idx == 0:
                    Sx_new = Sx[None, :] - d1[None, :] + new; xs = new - Sx_new / C[None, :]; ys = (d2 - Sy / C)[None, :].repeat(n_side, 0)
                    raw_x, raw_y = new, d2[None, :].repeat(n_side, 0)
                else:
                    Sy_new = Sy[None, :] - d2[None, :] + new; ys = new - Sy_new / C[None, :]; xs = (d1 - Sx / C)[None, :].repeat(n_side, 0)
                    raw_x, raw_y = d1[None, :].repeat(n_side, 0), new
                for j, q in enumerate(side):
                    loo_p[q].append(pr.pearson(list(xs[j]), list(ys[j])))
                    loo_r[q].append(spearman(list(raw_x[j]), list(raw_y[j])))
        qs = sorted(loo_p)
        th_p = [sb(mean_sd(loo_p[q])[0]) for q in qs]; th_r = [sb(mean_sd(loo_r[q])[0]) for q in qs]
        th_p = [t for t in th_p if t == t]; th_r = [t for t in th_r if t == t]
        se_p = jack(0.0, th_p)[0] if len(th_p) > 1 else float("nan")
        se_r = jack(0.0, th_r)[0] if len(th_r) > 1 else float("nan")
        out[s] = (se_p, se_r, len(qs))
    return out


def stratum_bootstrap(cells, build, models, B, H, seed=2026, log=None):
    rng = random.Random(seed)
    boot = defaultdict(lambda: ([], [])); boot_board = []
    for b in range(B):
        acc = defaultdict(lambda: ([], [])); accb = []
        for h in range(H):
            cut1, cut2 = boot_split(cells, rng)
            P = []
            for c in cells:
                d1 = build(cut1[c]); d2 = build(cut2[c])
                if not d1 or not d2: continue
                for m in models:
                    if m in d1 and m in d2: P.append((c, m, d1[m], d2[m]))
            accb.append(board_r(P))
            for c, (r1, r2) in per_cell_r(P).items():
                acc[c][0].append(r1); acc[c][1].append(r2)
        boot_board.append(sb(mean_sd(accb)[0]))
        for c in acc:
            boot[c][0].append(sb(mean_sd(acc[c][0])[0])); boot[c][1].append(sb(mean_sd(acc[c][1])[0]))
        if log and b % 25 == 0: log("boot %d/%d" % (b, B))
    return boot, boot_board


# ----------------------------------------------------------------------------------------------- the analysis (data-agnostic; --run and --selftest share it)
def analyse(strata, K, models, B=BOOT_B, H=BOOT_H, JH=JACK_H, log=None, pia_rows=None):
    """strata: {key: [ids]} in frozen-file order; K: {q: np.array(len(models))}. Returns (lines, rows_csv, summary)."""
    t0 = time.time()
    L = []; log = log or (lambda s: None)
    build = make_key_build(K, models)
    qsel = set(q for v in strata.values() for q in v)
    n_of = {k: len(v) for k, v in strata.items()}
    supported = {k: v for k, v in strata.items() if n_of[k] >= FLOOR}
    unsupported = [k for k in strata if n_of[k] < FLOOR]
    src_of = lambda k: k.split("/", 1)[0]
    sources = sorted({src_of(k) for k in strata}, key=lambda s: SOURCES.index(s) if s in SOURCES else 99)

    # ---------- (C2) board-level over the strata ----------
    L.append("")
    L.append("=== (C2) BOARD-LEVEL R OVER THE %d STRATA (profile_reliability.reliability, %d halvings, Random(%d)) ===" % (len(strata), REPS, SEED))
    L.append("  per-half floor min_cell=%d so that every stratum with >= %d reserved questions contributes; the recorded-default reading (min_cell 25 = strata >= 50 q) beside." % (MIN_CELL, FLOOR))
    r52, sd52, n52 = pr.reliability(strata, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL)
    R52 = sb(r52)
    sides52 = []
    per_rep52 = halvings_fixed(strata, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL, sides=sides52)
    r52f, sd52f, _ = mean_r(per_rep52)
    assert abs(r52f - r52) < 1e-12, "halvings_fixed does not mirror reliability()"
    present52 = sorted({p[0] for P in per_rep52 for p in P})
    loo_f = [sb(mean_r(per_rep52, drop=c)[0]) for c in present52]
    se_f, lo_f, hi_f = jack(R52, loo_f)
    loo_r = []
    for c in present52:
        sub = {k: v for k, v in strata.items() if k != c}
        r_i, _, _ = pr.reliability(sub, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL)
        loo_r.append(sb(r_i))
    se_r, lo_r, hi_r = jack(R52, loo_r)
    halv_sd52 = sb(r52 + sd52) - R52 if sd52 == sd52 else float("nan")
    r50, sd50, n50 = pr.reliability(strata, qsel, build, models, random.Random(SEED))          # default min_cell=25
    n_cells50 = sum(1 for k in strata if n_of[k] >= 50)
    L.append("  %-34s %5s %7s %7s %8s  %-19s %-19s" % ("reading", "cells", "r", "R(SB)", "halvSD", "jk FIXED 95%", "jk RE-HALVED 95%"))
    L.append("  %-34s %5d %7.4f %7.4f %8.4f  [%6.4f, %6.4f]  [%6.4f, %6.4f]" % ("all strata >= %d q (registered)" % FLOOR, len(present52), r52, R52, halv_sd52, lo_f, hi_f, lo_r, hi_r))
    L.append("  %-34s %5d %7.4f %7.4f %8s  %-19s %-19s" % ("recorded default (strata >= 50 q)", n_cells50, r50, sb(r50), fmt(sb(r50 + sd50) - sb(r50), 8), "(not read)", "(not read)"))
    cls52 = classify(R52, min(x for x in (lo_f, lo_r) if x == x) if any(x == x for x in (lo_f, lo_r)) else float("nan"), 10 ** 9)
    L.append("  class of the board-level number on the lowest lower bound (for the record; the registration asks for the number): %s" % cls52)
    L.append("  halvSD = SB-transformed spread of one halving around the mean r; the jackknife is leave-one-STRATUM-out, z = %.2f." % Z)
    summary = dict(R52=R52, r52=r52, halv_sd52=halv_sd52, jk_fixed52=(lo_f, hi_f), jk_rehalved52=(lo_r, hi_r), cells52=len(present52), cls52=cls52,
                   R50=sb(r50), cells50=n_cells50)
    log("(C2) 52-strata board done %.0fs" % (time.time() - t0))

    # ---------- (C3a) 6 source-level cells ----------
    L.append("")
    L.append("=== (C3a) BOARD-LEVEL R OVER THE %d SOURCE-LEVEL CELLS (each source's reserved questions pooled into one cell; leave-one-SOURCE-out jackknife) ===" % len(sources))
    src_cells = {s: [q for k in strata if src_of(k) == s for q in strata[k]] for s in sources}
    rS, sdS, nS = pr.reliability(src_cells, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL)
    RS = sb(rS)
    per_repS = halvings_fixed(src_cells, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL)
    presentS = sorted({p[0] for P in per_repS for p in P})
    looS_f = [sb(mean_r(per_repS, drop=c, )[0]) for c in presentS]
    seS_f, loS_f, hiS_f = jack(RS, looS_f)
    looS_r = []
    for c in presentS:
        sub = {k: v for k, v in src_cells.items() if k != c}
        r_i, _, _ = pr.reliability(sub, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL)
        looS_r.append(sb(r_i))
    seS_r, loS_r, hiS_r = jack(RS, looS_r)
    L.append("  %-34s %5d %7s %7s %8s  [%6s, %6s]  [%6s, %6s]" % ("%d source cells" % len(sources), len(presentS), fmt(rS, 7), fmt(RS, 7), fmt(sb(rS + sdS) - RS, 8), fmt(loS_f), fmt(hiS_f), fmt(loS_r), fmt(hiS_r)))
    L.append("  source cells (reserved q): " + ", ".join("%s %d" % (s, len(src_cells[s])) for s in sources))
    L.append("  leave-one-source-out R (fixed halvings): " + ", ".join("-%s %.4f" % (c, v) for c, v in zip(presentS, looS_f)))
    summary.update(RS=RS, jk_fixedS=(loS_f, hiS_f), jk_rehalvedS=(loS_r, hiS_r), halv_sdS=sb(rS + sdS) - RS)

    # ---------- (C3b) per source over its own strata ----------
    L.append("")
    L.append("=== (C3b) R PER SOURCE OVER ITS OWN STRATA (demeaned within the source; leave-one-stratum-out jackknife on fixed halvings) ===")
    L.append("  %-12s %6s %7s %7s %7s %8s  %-19s" % ("source", "strata", "q", "r", "R(SB)", "halvSD", "jk FIXED 95%"))
    per_source = {}
    for s in sources:
        cells_s = {k: v for k, v in strata.items() if src_of(k) == s}
        nq = sum(len(v) for v in cells_s.values())
        if len(cells_s) < 2:
            L.append("  %-12s %6d %7d %7s %7s %8s  %-19s  (undefined by construction: one stratum, model-demeaning leaves nothing to correlate)" % (s, len(cells_s), nq, "n/a", "n/a", "n/a", "n/a"))
            per_source[s] = dict(strata=len(cells_s), q=nq, R=float("nan"), lo=float("nan"), hi=float("nan"))
            continue
        per_rep_s = halvings_fixed(cells_s, qsel, build, models, random.Random(SEED), min_cell=MIN_CELL)
        r_s, sd_s, _ = mean_r(per_rep_s)
        # board_r's min_points=50 is a 14x12-board floor; here a source may carry 3 strata x 18 = 54 points, 2 x 18 after a drop
        r_s_list = [board_r(P, min_points=2 * len(models)) for P in per_rep_s]
        r_s, sd_s, _ = mean_sd(r_s_list)
        R_s = sb(r_s)
        present_s = sorted({p[0] for P in per_rep_s for p in P})
        loo_s = [sb(mean_sd([board_r(P, drop=c, min_points=2 * len(models)) for P in per_rep_s])[0]) for c in present_s]
        se_s, lo_s, hi_s = jack(R_s, loo_s)
        L.append("  %-12s %6d %7d %7.4f %7.4f %8s  [%6s, %6s]" % (s, len(present_s), nq, r_s, R_s, fmt(sb(r_s + sd_s) - R_s, 8), fmt(lo_s), fmt(hi_s)))
        per_source[s] = dict(strata=len(present_s), q=nq, R=R_s, lo=lo_s, hi=hi_s)
    L.append("  (jackknife over 2-3 strata is a resolution statement, not a confidence statement; printed as registered.)")
    summary["per_source"] = per_source
    log("(C3) sources done %.0fs" % (time.time() - t0))

    # ---------- (C1) per-stratum classes ----------
    L.append("")
    L.append("=== (C1) PER-STRATUM SPLIT-HALF OF THE WITHIN-STRATUM MODEL ORDER (%d models), CLASS ON THE LOWER OF TWO LOWER BOUNDS ===" % len(models))
    L.append("  reading (i) PROFILE: half-vectors model-demeaned across ALL %d strata of the board, r_s = Pearson across models inside s; the class is read here." % len(present52))
    L.append("  reading (ii) RAW ORDER: Spearman across models of the raw half-accuracies inside s; printed beside.")
    L.append("  intervals: (A) question bootstrap inside every stratum, B = %d x %d halvings, percentile 2.5/97.5 RECENTRED on the point (bias printed);" % (B, H))
    L.append("             (B) delete-one-question jackknife on the first %d fixed halvings. Class on the LOWER of (A) and (B) lower bounds." % JH)
    L.append("  support floor %d reserved questions -> UNSUPPORTED (counts only). Denominator per row = the stratum's reserved question count n." % FLOOR)
    pa = defaultdict(lambda: ([], []))
    for P in per_rep52:
        for c, (r1, r2) in per_cell_r(P).items():
            pa[c][0].append(r1); pa[c][1].append(r2)
    point = {c: (mean_sd(v[0]), mean_sd(v[1])) for c, v in pa.items()}
    jk = stratum_jackknife(per_rep52, sides52, K, models, [c for c in strata if c in point], JH)
    log("(C1) jackknife done %.0fs" % (time.time() - t0))
    boot, boot_board = stratum_bootstrap({k: v for k, v in strata.items() if k in point}, build, models, B, H, log=log)
    log("(C1) bootstrap done %.0fs" % (time.time() - t0))
    rows = []
    hdr = "  %-44s %4s  %7s %7s %-17s %+6s %-17s %-17s %-19s | %7s %-17s %-17s %-19s"
    L.append(hdr % ("stratum", "n", "R_prof", "halvSD", "boot95 recentred", "bias", "jackknife 95%", "raw boot95", "class (profile)", "R_raw", "boot95 recentred", "jackknife 95%", "class (raw order)"))
    for c in strata:
        n = n_of[c]
        if c not in point:
            rows.append(dict(key=c, source=src_of(c), domain=c.split("/", 1)[1], n=n, cls="UNSUPPORTED", R_prof=float("nan"), r_prof=float("nan"), halv_sd=float("nan"),
                             boot_lo=float("nan"), boot_hi=float("nan"), boot_bias=float("nan"), boot_raw_lo=float("nan"), boot_raw_hi=float("nan"),
                             jk_lo=float("nan"), jk_hi=float("nan"), jk_se=float("nan"), lower_used=float("nan"),
                             R_raw=float("nan"), rboot_lo=float("nan"), rboot_hi=float("nan"), rjk_lo=float("nan"), rjk_hi=float("nan"), cls_raw="UNSUPPORTED"))
            L.append("  %-44s %4d  %s" % (c, n, "UNSUPPORTED (n < %d: counts only)" % FLOOR))
            continue
        (rp, sdp, _), (rr, sdr, _) = point[c]
        Rp = sb(rp); Rr = sb(rr)
        plo, phi = pct(boot[c][0], 0.025), pct(boot[c][0], 0.975); pmu = mean_sd(boot[c][0])[0]
        rlo, rhi = pct(boot[c][1], 0.025), pct(boot[c][1], 0.975); rmu = mean_sd(boot[c][1])[0]
        bias_p = pmu - Rp; bias_r = rmu - Rr
        cplo, cphi = plo - bias_p, phi - bias_p; crlo, crhi = rlo - bias_r, rhi - bias_r
        se_p, se_r, _ = jk[c]
        jlo_p, jhi_p = Rp - Z * se_p, Rp + Z * se_p; jlo_r, jhi_r = Rr - Z * se_r, Rr + Z * se_r
        lows_p = [x for x in (cplo, jlo_p) if x == x]; lows_r = [x for x in (crlo, jlo_r) if x == x]
        low_p = min(lows_p) if lows_p else float("nan"); low_r = min(lows_r) if lows_r else float("nan")
        clsp = classify(Rp, low_p, n); clsr = classify(Rr, low_r, n)
        halv = sb(rp + sdp) - Rp if sdp == sdp else float("nan")
        rows.append(dict(key=c, source=src_of(c), domain=c.split("/", 1)[1], n=n, cls=clsp, R_prof=Rp, r_prof=rp, halv_sd=halv,
                         boot_lo=cplo, boot_hi=cphi, boot_bias=bias_p, boot_raw_lo=plo, boot_raw_hi=phi, jk_lo=jlo_p, jk_hi=jhi_p, jk_se=se_p, lower_used=low_p,
                         R_raw=Rr, rboot_lo=crlo, rboot_hi=crhi, rjk_lo=jlo_r, rjk_hi=jhi_r, cls_raw=clsr))
        L.append("  %-44s %4d  %7.4f %7s [%6s, %6s] %+6.3f [%6s, %6s] [%6s, %6s] %-19s | %7.4f [%6s, %6s] [%6s, %6s] %-19s"
                 % (c, n, Rp, fmt(halv, 7), fmt(cplo), fmt(cphi), bias_p, fmt(jlo_p), fmt(jhi_p), fmt(plo), fmt(phi), clsp, Rr, fmt(crlo), fmt(crhi), fmt(jlo_r), fmt(jhi_r), clsr))
    bb_lo, bb_hi = pct(boot_board, 0.025), pct(boot_board, 0.975); bb_mu = mean_sd(boot_board)[0]
    L.append("  board-level R over the strata from the same question bootstrap: raw mean %.4f [%.4f, %.4f] vs point %.4f (bias %+.4f); recentred [%.4f, %.4f]"
             % (bb_mu, bb_lo, bb_hi, R52, bb_mu - R52, bb_lo - (bb_mu - R52), bb_hi - (bb_mu - R52)))
    by_cls = Counter(r["cls"] for r in rows)
    L.append("  classes over the %d strata (profile reading): %s" % (len(rows), dict(by_cls)))
    L.append("  raw-order reading: %s" % dict(Counter(r["cls_raw"] for r in rows)))
    summary["rows"] = rows; summary["classes"] = dict(by_cls)

    # ---------- support curve ----------
    L.append("")
    L.append("=== SUPPORT CURVE: per-stratum R_prof against reserved n (profile reading), and binned means ===")
    for r in sorted(rows, key=lambda r: r["n"]):
        L.append("  n=%4d  %-44s R_prof %s  class %s" % (r["n"], r["key"], fmt(r["R_prof"], 7), r["cls"]))
    bins = [(0, FLOOR), (FLOOR, 50), (50, 100), (100, 200), (200, 300), (300, 10 ** 9)]
    for lo_b, hi_b in bins:
        sel = [r["R_prof"] for r in rows if lo_b <= r["n"] < hi_b and r["R_prof"] == r["R_prof"]]
        if sel:
            L.append("  bin [%d, %s): %d strata, mean R_prof %.4f, min %.4f, max %.4f" % (lo_b, "inf" if hi_b >= 10 ** 9 else hi_b, len(sel), sum(sel) / len(sel), min(sel), max(sel)))

    # ---------- (C3c) MMLU-Pro strata beside PROFILE-INTERVAL-ALL ----------
    L.append("")
    L.append("=== (C3c) THE MMLU_PRO_LB STRATA (this test: %d-model union roster, pool %s) BESIDE PROFILE-INTERVAL-ALL's key rows" % (len(models), POOL))
    L.append("    (merged 20-model roster, 2,811 judged questions of pool p2dca21ab5f4ef3ae, block '--- key, 20 rows ---'); roster named, NO comparison of levels claimed ===")
    L.append("  %-30s %4s %8s %-19s | %-30s %4s %8s %-19s" % ("stratum (18-model union key)", "n", "R_prof", "class", "PIA anchor (key, 20 rows)", "q", "R_prof", "class"))
    mm = [r for r in rows if r["source"] == "MMLU_PRO_LB"]
    for r in mm:
        d = r["domain"]; key_pia = d.lower()
        p = (pia_rows or {}).get(key_pia)
        left = "%-30s %4d %8s %-19s" % (r["key"], r["n"], fmt(r["R_prof"], 8), r["cls"])
        right = ("%-30s %4d %8.4f %-19s" % (p["anchor"], p["q"], p["R"], p["cls"])) if p else "%-30s (not in the PIA outcome)" % d
        L.append("  %s | %s" % (left, right))

    # ---------- predictions ----------
    L.append("")
    L.append("=== PREDICTIONS (the plan's, recorded blind; scored exactly as registered) ===")
    n_mm_pass = sum(1 for r in mm if r["cls"] == "PASS"); n_mm_pwi = sum(1 for r in mm if r["cls"] == "PASS-WITH-INTERVAL")
    p1 = ("HELD" if n_mm_pass == len(mm) else "FAILED") if mm else "N/A (no MMLU_PRO_LB strata in this data)"
    L.append("  P1 'MMLU-Pro-source strata PASS (scored: all 14 PASS)': %d of %d PASS, %d PASS-WITH-INTERVAL, %d FAIL, %d UNSUPPORTED -> %s"
             % (n_mm_pass, len(mm), n_mm_pwi, sum(1 for r in mm if r["cls"] == "FAIL"), sum(1 for r in mm if r["cls"] == "UNSUPPORTED"), p1))
    small = [r for r in rows if r["source"] in PREDICTED_FAIL_SOURCES]
    n_small_fail = sum(1 for r in small if r["cls"] in ("FAIL", "UNSUPPORTED"))
    p2 = ("HELD" if n_small_fail * 2 > len(small) else "FAILED") if small else "N/A (no such strata in this data)"
    L.append("  P2 'MATH / GPQA / MuSR / IFEval strata mostly FAIL by support (scored: more than half of those %d strata FAIL or UNSUPPORTED)': %d of %d FAIL or UNSUPPORTED (%s) -> %s"
             % (len(small), n_small_fail, len(small), ", ".join("%s %d" % (k, v) for k, v in sorted(Counter(r["cls"] for r in small).items())), p2))
    for s in PREDICTED_FAIL_SOURCES:
        ss = [r for r in rows if r["source"] == s]
        L.append("     %-8s reserved %4d q over %d strata: %s" % (s, sum(r["n"] for r in ss), len(ss), ", ".join("%s %s %s" % (r["domain"], fmt(r["R_prof"], 6), r["cls"]) for r in ss)))
    bbh = [r for r in rows if r["source"] == "BBH"]
    L.append("  BBH (no prediction registered; printed): %d strata, %s" % (len(bbh), dict(Counter(r["cls"] for r in bbh))))
    summary.update(p1=p1, p2=p2, n_mm_pass=n_mm_pass, n_mm=len(mm), n_small_fail=n_small_fail, n_small=len(small))

    # ---------- criteria and consequences ----------
    L.append("")
    L.append("=== CRITERIA (in the registration's words) ===")
    n_supported = sum(1 for r in rows if r["cls"] != "UNSUPPORTED"); n_classed = sum(1 for r in rows if r["cls"] in ("PASS", "PASS-WITH-INTERVAL", "FAIL"))
    L.append("  (C1) 'every stratum with >= %d reserved questions receives a class': %d of %d supported strata classed (%s); %d below the floor printed as counts -> %s"
             % (FLOOR, n_classed, n_supported, dict(by_cls), len(unsupported), "HELD" if n_classed == n_supported else "FAILED"))
    L.append("  (C2) 'board-level R over the 52 strata with its jackknife interval and halving SD': R = %.4f, jk fixed [%.4f, %.4f], re-halved [%.4f, %.4f], halving SD %.4f over %d strata -> PUBLISHED"
             % (R52, lo_f, hi_f, lo_r, hi_r, halv_sd52, len(present52)))
    L.append("  (C3) 'board-level R per source (6 cells) with intervals': 6-cell reading R = %.4f [%.4f, %.4f] (fixed) [%.4f, %.4f] (re-halved); per-source-own-strata readings above; MMLU-Pro strata printed beside PROFILE-INTERVAL-ALL, rosters named -> PUBLISHED"
             % (RS, loS_f, hiS_f, loS_r, hiS_r))
    L.append("  FALSIFIER (a sentence, not a result): FRAMEWORK L258 'union strata have no reliability measurement at all' is now false whatever the values; bracket by insertion.")
    if p1 == "FAILED":
        L.append("  CONSEQUENCE of P1 FAILED: the key-built profile's reliability is shown roster- and cell-dependent at the stratum level on the 18-model union key")
        L.append("     (a finding beside PROFILE-RELIABILITY's 0.9135 on the 46-model MMLU-Pro key, not a refutation of it: rosters and pools differ).")
    L.append("  CONSEQUENCE for the atlas (plan A5): a key-built row per union stratum with its class; FAIL / UNSUPPORTED strata ship as counts without a profile claim.")
    L.append("  McNEMAR-ESTABLISHED RULE: no wrong-direction count is produced here; nothing for systematic_budget.mcnemar_edge / established to attach to. Stated, not applied.")
    L.append("  runtime %.0fs, zero LLM calls" % (time.time() - t0))
    return L, rows, summary


# ----------------------------------------------------------------------------------------------- PIA rows (C3c)
def read_pia_key20(path=PIA_TXT):
    """PROFILE-INTERVAL-ALL's '--- key, 20 rows ---' per-anchor block: {anchor.lower(): dict(anchor, q, R, cls)}."""
    if not os.path.isfile(path): return {}
    out = {}; inside = False
    for line in open(path, "r", encoding="utf-8"):
        if line.strip() == "--- key, 20 rows ---": inside = True; continue
        if inside and line.strip().startswith("board-level R"): break
        if inside and line.startswith("  ") and not line.strip().startswith("anchor"):
            name = line[:20].strip(); rest = line[20:].split()
            try:
                q = int(rest[0]); R = float(rest[1])
            except (ValueError, IndexError):
                continue
            cls = "PASS-WITH-INTERVAL" if "PASS-WITH-INTERVAL" in line.split("|")[0] else ("PASS" if " PASS " in line.split("|")[0] else "FAIL")
            out[name.lower()] = dict(anchor=name, q=q, R=R, cls=cls)
    return out


# ----------------------------------------------------------------------------------------------- data check (shared by --dry-run and --run)
def data_check(conn, strata, L):
    ok = True
    def chk(name, good, val=""):
        nonlocal ok
        ok &= bool(good); L.append("  [%s] %s  %s" % ("ok" if good else "FAIL", name, ("(%s)" % (val,)) if val != "" else ""))
    n_ids = sum(len(v) for v in strata.values())
    chk("frozen id file %s: %d keys, %d judgeable ids" % (os.path.basename(ID_FILE), len(strata), n_ids), len(strata) == N_STRATA and n_ids == N_POOL)
    pools = dict(conn.execute("SELECT pool_id, COUNT(*) FROM reserved_pool GROUP BY pool_id").fetchall())
    chk("DB reserved_pool holds %d pools; %s (%d rows) is the pool of record; every other id is refused by the reader (incl. %s, %d rows)"
        % (len(pools), POOL, pools.get(POOL, 0), REFUSED_POOL, pools.get(REFUSED_POOL, 0)), pools.get(POOL) == N_POOL)
    try:
        guarded_pool_rows(conn, REFUSED_POOL); refused = False
    except SystemExit:
        refused = True
    chk("reader refuses pool %s by id" % REFUSED_POOL, refused)
    rows = guarded_pool_rows(conn, POOL)
    chk("reserved_pool rows of %s == frozen file (key, id) set" % POOL, {(k, q) for k, v in rows.items() for q in v} == {(k, q) for k, v in strata.items() for q in v})
    n_rows, msgs = check_csv_of_record(strata)
    for m in msgs: chk(m, True)
    cq = {q: (s, d) for q, s, d in conn.execute("SELECT question_id, source, domain FROM corpus_questions")}
    bad = 0
    for k, v in strata.items():
        s, d = k.split("/", 1)
        for q in v:
            if q not in cq or cq[q] != (SOURCE_OF_CORPUS.get(s, s), d): bad += 1
    chk("frozen keys agree with corpus_questions (source, domain) on every pool id (MMLU_PRO_LB <-> MMLU_PRO); the frozen key stays the stratum", bad == 0, bad)
    tot, nq, nm = conn.execute("SELECT COUNT(*), COUNT(DISTINCT question_id), COUNT(DISTINCT model_name) FROM eval_results").fetchone()
    chk("eval_results = 388,908 rows, 21,606 questions x 18 models", (tot, nq, nm) == (388908, 21606, 18), (tot, nq, nm))
    models = sorted(m for (m,) in conn.execute("SELECT DISTINCT model_name FROM eval_results"))
    chk("%s absent from the roster" % EXCLUDE, EXCLUDE not in models)
    math_ids = [q for k, v in strata.items() if k.startswith("MATH/") for q in v]
    mf = Counter(q for (q,) in conn.execute("SELECT question_id FROM eval_results_mathfix"))
    chk("eval_results_mathfix covers all %d MATH pool ids x %d models (MATH column read from MATH-FIX only)" % (len(math_ids), len(models)), all(mf[q] == len(models) for q in math_ids))
    ing = {(q, m): c for q, m, c in conn.execute("SELECT question_id, model_name, is_correct FROM eval_results WHERE question_id IN (SELECT question_id FROM reserved_pool WHERE pool_id=?) AND question_id >= 2000000 AND question_id < 3000000", (POOL,))}
    fix = {(q, m): c for q, m, c in conn.execute("SELECT question_id, model_name, is_correct FROM eval_results_mathfix")}
    n_diff = sum(1 for k in fix if k in ing and ing[k] != fix[k])
    L.append("  info: MATH-FIX differs from the ingested MATH rows on %d of %d pool (question, model) cells (the ingested rows are NOT read into the key)" % (n_diff, len(math_ids) * len(models)))
    return ok, models


def support_table(strata, L):
    src_of = lambda k: k.split("/", 1)[0]
    L.append("")
    L.append("  %-46s %5s  %s" % ("stratum (frozen key = SOURCE/domain)", "n", "support"))
    for k in strata:
        n = len(strata[k]); L.append("  %-46s %5d  %s" % (k, n, "UNSUPPORTED (< %d)" % FLOOR if n < FLOOR else ">= %d" % FLOOR))
    L.append("")
    L.append("  per source (reserved-side support, expected per reserved_pool_meta):")
    ok = True
    for s in SOURCES:
        ks = [k for k in strata if src_of(k) == s]; n = sum(len(strata[k]) for k in ks)
        e_n, e_k = EXPECTED_SUPPORT[s]; good = (n, len(ks)) == (e_n, e_k); ok &= good
        L.append("  [%s] %-12s %5d q over %2d strata (expected %d / %d)" % ("ok" if good else "FAIL", s, n, len(ks), e_n, e_k))
    L.append("  support floor: %d reserved questions -> UNSUPPORTED; strata below it: %s" % (FLOOR, [k for k in strata if len(strata[k]) < FLOOR] or "none"))
    return ok


# ----------------------------------------------------------------------------------------------- modes
def dry_run():
    print("reserved_pool_id=%s" % pool_guard.assert_pool_of_record(POOL))
    L = ["=== PROFILE-INTERVAL-ALL-UNION --dry-run (zero calls; no reliability number is computed here) ==="]
    strata = load_strata()
    conn = pool_guard.open_ro(pool_guard.db_path(POOL))
    try:
        ok, models = data_check(conn, strata, L)
    finally:
        conn.close()
    L.append("  roster (%d models, union key, %s excluded): %s" % (len(models), EXCLUDE, ", ".join(models)))
    ok &= support_table(strata, L)
    L.append("")
    L.append("  instrument on --run: profile_reliability.reliability (REPS %d, Random(%d), min_cell %d), per-stratum bootstrap B=%d x %d halvings, jackknife on %d halvings; bar %.2f."
             % (REPS, SEED, MIN_CELL, BOOT_B, BOOT_H, JACK_H, BAR))
    L.append("  outputs on --run (written once): %s, %s" % (OUT_TXT, OUT_CSV))
    L.append("  existing outcome file: %s" % ("YES (--run will refuse)" if os.path.exists(OUT_TXT) else "no"))
    L.append("  DRY-RUN %s" % ("READY" if ok else "NOT READY: a data check failed"))
    print("\n".join(L))
    return 0 if ok else 1


def run():
    print("reserved_pool_id=%s" % pool_guard.assert_pool_of_record(POOL))
    if os.path.exists(OUT_TXT):
        raise SystemExit("[ONCE] %s exists; the outcome is written once. Refusing." % OUT_TXT)
    t0 = time.time()
    L = ["=== PROFILE-INTERVAL-ALL-UNION: do the 52 (source, domain) union strata carry a key-built profile row with a class? ===",
         "  registered 2026-09-17 (commit 62c4084, docs/judge_v2_program.md L5402-L5457); zero calls; key only; pool %s" % POOL,
         "  reserved_pool_id=%s" % POOL, "",
         "--- DATA CHECK (the object, before any stratum is read) ---"]
    strata = load_strata()
    conn = pool_guard.open_ro(pool_guard.db_path(POOL))
    try:
        ok, models = data_check(conn, strata, L)
        ok &= support_table(strata, L)
        if not ok:
            L.append("  DATA CHECK FAILED - stopping before any stratum is read; nothing written.")
            print("\n".join(L)); return 1
        K, models = load_key(conn, strata, models)
    finally:
        conn.close()
    L.append("  roster (%d models): %s" % (len(models), ", ".join(models)))
    L.append("  KEY DENOMINATOR: each stratum's RESERVED questions of pool %s (n per row); key = is_correct (MATH: eval_results_mathfix)." % POOL)
    pia = read_pia_key20()
    body, rows, summary = analyse(strata, K, models, log=lambda s: print(s, flush=True), pia_rows=pia)
    L.extend(body)
    L.append("  total runtime %.0fs" % (time.time() - t0))
    txt = "\n".join(L)
    print(txt)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_TXT, "w", encoding="utf-8") as f: f.write(txt + "\n")
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    print("wrote %s and %s" % (OUT_TXT, OUT_CSV))
    return 0


# ----------------------------------------------------------------------------------------------- selftest
def selftest():
    """Synthetic key rows with planted profile structure; the MATH-FIX read on an in-memory DB; the guards."""
    print("reserved_pool_id=%s" % pool_guard.assert_pool_of_record(POOL))
    print("=== --selftest (synthetic; nothing of record is read beyond the pool guard) ===")
    rng = random.Random(1)
    models = ["m%02d" % i for i in range(N_MODELS)]
    ability = [rng.gauss(0.0, 0.8) for _ in models]
    # planted: 5 STRONG strata (n=200, per-(model, stratum) deviation SD 0.9 on the logit), 4 NULL strata (n=60, no deviation),
    # 1 TINY stratum (n=20 -> UNSUPPORTED, in source B), two one-stratum sources C and D (n=60: per-source R undefined by
    # construction; four sources so the leave-one-source-out jackknife keeps >= 50 points, the recorded estimator's floor).
    spec = [("A/s%d" % i, 200, 0.9) for i in range(5)] + [("B/n%d" % i, 60, 0.0) for i in range(4)] + [("B/tiny", 20, 0.9), ("C/one", 60, 0.9), ("D/one", 60, 0.9)]
    strata = {}; K = {}; qid = 1
    for key, n, dev_sd in spec:
        dev = [rng.gauss(0.0, dev_sd) for _ in models]
        ids = []
        for _ in range(n):
            diff = rng.gauss(0.0, 1.0)
            K[qid] = np.array([1.0 if rng.random() < 1 / (1 + math.exp(-(ability[i] + dev[i] - diff))) else 0.0 for i in range(len(models))])
            ids.append(qid); qid += 1
        strata[key] = ids
    global SOURCES
    saved_sources = SOURCES; SOURCES = ("A", "B", "C", "D")
    try:
        L, rows, summary = analyse(strata, K, models, B=20, H=4, JH=4, log=lambda s: print("  " + s, flush=True))
    finally:
        SOURCES = saved_sources
    print("\n".join(L))
    byk = {r["key"]: r for r in rows}
    fails = []
    for key, n, dev_sd in spec:
        r = byk[key]
        if n < FLOOR:
            if r["cls"] != "UNSUPPORTED": fails.append("%s should be UNSUPPORTED, got %s" % (key, r["cls"]))
        elif dev_sd > 0:
            if not (r["R_prof"] >= BAR and r["cls"] in ("PASS", "PASS-WITH-INTERVAL")): fails.append("%s planted strong: R_prof %.3f class %s" % (key, r["R_prof"], r["cls"]))
            if not (r["lower_used"] <= r["R_prof"]): fails.append("%s lower bound above the point" % key)
        else:
            if r["cls"] != "FAIL": fails.append("%s planted null: R_prof %.3f class %s (expected FAIL)" % (key, r["R_prof"], r["cls"]))
    if not (summary["R52"] == summary["R52"] and summary["jk_fixed52"][0] <= summary["R52"] <= summary["jk_fixed52"][1]): fails.append("board-level interval does not bracket the point")
    if summary["per_source"]["C"]["R"] == summary["per_source"]["C"]["R"]: fails.append("one-stratum source should be undefined")
    if not (summary["RS"] == summary["RS"] and summary["jk_fixedS"][0] <= summary["RS"] <= summary["jk_fixedS"][1]): fails.append("source-level interval does not bracket the point")
    # guards: CSV mismatch detection on a perturbed stratum definition
    real = load_strata(); pert = dict(real); k0 = next(iter(pert)); pert[k0] = pert[k0][:-1]
    try:
        check_csv_of_record(pert); fails.append("CSV check accepted a perturbed stratum definition")
    except SystemExit:
        pass
    # pool refusal by id
    conn = pool_guard.open_ro(pool_guard.db_path(POOL))
    try:
        try:
            guarded_pool_rows(conn, REFUSED_POOL); fails.append("reader did not refuse %s" % REFUSED_POOL)
        except SystemExit:
            pass
    finally:
        conn.close()
    # MATH-FIX precedence on an in-memory DB with the record's schema: ingested says 0, mathfix says 1 -> key must be 1
    mem = sqlite3.connect(":memory:")
    mem.execute("CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, category TEXT, question_text TEXT, options_json TEXT, gt_answer TEXT, pred TEXT, model_output TEXT, is_correct INTEGER, PRIMARY KEY (question_id, model_name))")
    mem.execute("CREATE TABLE eval_results_mathfix (question_id INTEGER, model_name TEXT, is_correct INTEGER, PRIMARY KEY (question_id, model_name))")
    mm = ["a", "b"]
    for m in mm:
        mem.execute("INSERT INTO eval_results VALUES (2000001, ?, 'x', 't', NULL, NULL, NULL, 'o', 0)", (m,))
        mem.execute("INSERT INTO eval_results VALUES (1000001, ?, 'x', 't', NULL, NULL, NULL, 'o', 1)", (m,))
        mem.execute("INSERT INTO eval_results_mathfix VALUES (2000001, ?, 1)", (m,))
    Kt, _ = load_key(mem, {"MATH/Algebra": [2000001], "BBH/navigate": [1000001]}, mm)
    if not (Kt[2000001].tolist() == [1.0, 1.0] and Kt[1000001].tolist() == [1.0, 1.0]): fails.append("MATH-FIX precedence broken: %s" % Kt)
    mem.execute("DELETE FROM eval_results_mathfix")
    try:
        load_key(mem, {"MATH/Algebra": [2000001], "BBH/navigate": [1000001]}, mm); fails.append("load_key accepted a MATH question absent from mathfix (fell back to ingested?)")
    except SystemExit:
        pass
    print("")
    if fails:
        print("SELFTEST FAILED:"); [print("  - " + f) for f in fails]; return 1
    print("SELFTEST OK: planted strong strata clear the bar, null strata FAIL, the 20-q stratum is UNSUPPORTED, the one-stratum source is undefined,")
    print("             the CSV-vs-frozen check rejects a perturbed definition, %s is refused by id, MATH rows come from eval_results_mathfix only." % REFUSED_POOL)
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="PROFILE-INTERVAL-ALL-UNION")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true"); g.add_argument("--selftest", action="store_true"); g.add_argument("--run", action="store_true")
    a = ap.parse_args(argv)
    if a.dry_run: return dry_run()
    if a.selftest: return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
