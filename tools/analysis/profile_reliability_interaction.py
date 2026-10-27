"""PROFILE-RELIABILITY-INTERACTION (registered 2026-09-18 before any code or call, commit 954e829; zero calls) - what is the
MMLU-Pro profile reliability once anchor difficulty is removed: the model- AND anchor-demeaned split-half R on the 14
anchors, key and judge?

  python tools/analysis/profile_reliability_interaction.py --selftest   # synthetic tables only; no DB of record is opened
  python tools/analysis/profile_reliability_interaction.py --dry-run    # pool id, pinned row counts, C0 on one halving; no R
  python tools/analysis/profile_reliability_interaction.py --run        # write-once outcome from complete caches

THE REGISTRATION (docs/judge_v2_program.md "Registered 2026-09-18 (before any code or call) - PROFILE-RELIABILITY-
INTERACTION"; the last bracket in the programme file wins over this copy), condensed:
  Instrument. profile_reliability.py under --interaction-only (inert when absent; the default path pinned on a synthetic
  table by `profile_reliability.py --selftest`; the run first reproduces 0.9135 / 0.6728 to 4 dp on the fixed halvings
  as the reproduction gate). With the flag: the same 40 halvings (random.Random(7)), the same per-half builders (key_build
  = per-model accuracy over the half; judge_build = jf.board_from on the half's verdicts), then the half-profile pairs
  are demeaned by model AND by anchor (two-way, alternating until the row and column means are < 1e-9, on each half
  separately) before the Pearson r; Spearman-Brown; averaged over the halvings; leave-one-anchor-out jackknife interval
  and halving SD, on fixed halvings and re-halved (the ANCHOR-PROFILE-INTERVAL instrument).
  Legs: (K) the key, 14 anchors (beside 0.9135); (J1) the x12 judge board (beside 0.6728); (J2) the merged judge board
  through the same demeaning on x20_merged.merged_rows() (beside 0.7183). (C0, before any number is read): the per-anchor
  mean of each judge half-profile is printed; if the per-anchor BT fit centres theta by construction (anchor means
  identically 0 to 1e-6), the judge legs' interaction-only R equals the recorded model-demeaned R by IDENTITY and the
  outcome says so rather than reporting a "fall". Null: Bernoulli(logistic(a_m - d_c)) with a_m, d_c fitted by logistic
  regression on the real 46 x 14 x ~201 key table, 20 simulated tables, the instrument read on each under both
  demeanings (median and range beside the real readings); variance decomposition of the real 46 x 14 accuracy table.
  (C1) interaction-only R with jackknife interval and halving SD per leg, beside the recorded model-demeaned value
  reproduced to 4 dp; C0 first. (C2) the null under both demeanings and the variance decomposition.
  P1 key interaction-only R in 0.80-0.88 (lane-2 brief; the prediction of record); P1' 0.78-0.88 (night schedule
  wording; both scored); P2 key interaction-only R above 0.70 (lower jackknife bound >= 0.70 PASS; point >= 0.70 with
  the bound below PASS-WITH-INTERVAL, HELD on the point); P3 judge J2 in 0.55-0.70 on the point, scored
  FAILED-BY-IDENTITY with the C0 statement if the judge half-profiles are centred per anchor by construction; P4 the
  no-interaction null on the model-only instrument <= 0.90; registrar's addition: the null under the interaction-only
  demeaning <= 0.30, i.e. the real key reading sits >= 0.50 above its null. Falsifier: key interaction-only R < 0.70
  at the point (the key-built profile is a re-indexed global score; PROFILE-RELIABILITY and FRAMEWORK L117 bracketed).
  Output experiment_results/x12_crossdomain/profile_reliability_interaction_outcome.txt, written once.

IMPLEMENTATION, and the READINGS CHOSEN where the registration is silent or not implementable literally (each stated
here before the run):
  * "(K) the 46-model key, 14 anchors (beside 0.9135)" is NOT one object. The recorded 0.9135 is the 12-model ARENA12
    key (experiment_results/x12_crossdomain/profile_reliability.txt line 2 "12 models"; programme L3453 "Key comparator
    0.9135 (12) / 0.9139 (20)"; profile_reliability.main uses models = sorted(p8.ARENA12) for key_build). The 46-model
    key has no recorded model-demeaned value. Reading chosen: the LEG OF RECORD for P1 / P1' / P2 and the falsifier is
    K12 (the roster whose 0.9135 the falsifier's consequence attaches to; it is the leg the reproduction gate can be
    applied to). The 46-model roster (every eval_results model minus Meta-Llama-3-70B-Instruct; count pinned at 46) is
    read BESIDE as K46, with the same instrument and intervals, labelled "not the leg of record"; the null and the
    variance decomposition are read on BOTH rosters (the registration names the 46 x 14 table; the leg of record needs
    its own null). The registrar must bracket the registration with the roster of record; nothing here is committed.
  * Question set: the 2,811 routed + judged questions of pool p2dca21ab5f4ef3ae in the 14 bareq512_s42 anchors, in the
    exact dict order the recorded runs built (insertion order of anc_cells over sorted qids), because the halvings
    depend on it; the per-anchor counts are asserted equal to the recorded run's (ANCHOR-PROFILE-INTERVAL line 17).
  * Two-way demeaning = profile_reliability.demean_two_way (model pass, then anchor pass, alternating to 1e-9). On a
    balanced table (every model in every anchor's half-profile; true for every leg here, asserted) one pass is exact.
  * Jackknife: leave-one-anchor-out, 14 folds, SE = sqrt((n-1)/n * sum (R_-i - R_bar)^2) on the R scale, z = 1.96,
    centred on the full-sample R (ANCHOR-PROFILE-INTERVAL's primary); RE-HALVED (fresh Random(7) on the 13 cells) is the
    primary reading, FIXED halvings (the same 40 halvings, the dropped anchor's points removed) beside; if the two
    disagree on the 0.70 boundary the P2 class is UNDETERMINED (the ANCHOR-PROFILE-INTERVAL rule).
  * Null fit: logit p_mc = a_m - d_c, the MLE on the question-level Bernoulli table (equivalently on the per-cell
    (successes, trials) table), by alternating 1-D Newton steps on a and d until the change is < 1e-10; d centred to
    sum zero; logits clipped to [-15, 15] (separation guard; the clip count is printed). 20 tables, numpy RandomState
    (1..20), each question of each anchor drawn Bernoulli(p_mc) for every model; the instrument (same halvings,
    Random(7)) read under both demeanings. A no-LOGIT-interaction table still carries a reproducible accuracy-scale
    interaction (the logistic curvature compresses strong models' differences on easy anchors), so the null's
    interaction-only R is not zero by construction; the registrar's <= 0.30 bar is what makes it small.
  * Variance decomposition: T[m][c] = model m's key accuracy over anchor c's judged questions; grand mean, row and column
    main effects, interaction residual; shares of the three variances (population variance over the table, as the
    union checker computed them).
  * The judge legs carry no falsifier; their interaction-only R is read beside the recorded values with the C0 identity
    statement where it applies (rj.mm_fit returns theta minus its mean over the models of the fit, so every per-anchor
    half-profile is centred by construction; the expectation is C0 at 1e-16).
  * McNemar-established rule: nothing here is compared to the key's direction, so no wrong-direction count exists for
    systematic_budget.mcnemar_edge / established to attach to; stated, not applied. KEY DENOMINATOR of every instrument:
    each anchor's JUDGED questions (~201), halved.
  * Hygiene: caches opened file:...?mode=ro (x12 via stack_judge.cache_path(), never open_cache(); x20 via
    x20_replications.X20; x20 never read alone); rows pinned 9,142 / 12,394 / 21,536, 20 models, 2,811 judged q; the
    eval DB mode=ro; Meta-Llama-3-70B-Instruct excluded and asserted absent from the caches; pool_guard first line.
    --selftest opens nothing of record (rule 7 window). Write-once: --run refuses if the outcome file exists.

[ADDED 2026-09-23 - the LEAF-INTERACTION option `--level leaf`; CODE ONLY, the test itself is NOT REGISTERED and needs the
author's word before any number it produces enters the record.] The registered readout above works at the ANCHOR level (14
depth-1 cells). The open question is whether the frozen tree's LEAF cells carry any (model x cell) interaction the strata do
not. `--level leaf` is the SAME instrument on a different cell set:

  python tools/analysis/profile_reliability_interaction.py --selftest [--level leaf]
  python tools/analysis/profile_reliability_interaction.py --dry-run --level leaf
  python tools/analysis/profile_reliability_interaction.py --run --level leaf   # -> profile_reliability_interaction_leaf_outcome.txt

  * The cell set is bareq512_s42's LEAVES (rubric_512.primary_routing(TREE) read directly, without anchor_fn), in the
    insertion order of the sorted judged qids - the record's convention, and the halvings depend on it.
  * SUPPORT RULE, enforced, never silently pooled: a leaf below the record's 120-question floor (STABLE-CELL-SET C1,
    stable_cell_set.FLOOR = 120) is UNDETERMINED-by-support and is dropped from the cell set, never merged into a parent,
    a sibling or a remainder cell. The floor is applied to the leaf's JUDGED questions, the instrument's own denominator
    (a subset of the pool questions the floor of record counts, so this reading is the stricter one); both counts are
    printed per leaf. The count of ADMISSIBLE leaves is printed FIRST, before any support table and before any R.
  * REFUSAL: fewer than 2 admissible leaves -> the readout stops with UNDETERMINED-by-support and writes NO outcome file
    (a one-cell "interaction" is not a cell interaction). The instrument's own point floor (r_of's min_points = 50 points
    per halving = cells x models) is reported per leg and a leg below it reads UNDETERMINED-by-support, never a number.
  * Everything else is the anchor instrument, unchanged and shared: the same 40 halvings from random.Random(7), the same
    per-half builders, profile_reliability.demean_by_model / demean_two_way, Spearman-Brown, the leave-one-CELL-out
    jackknife (re-halved primary, fixed beside, z = 1.96) and the halving SD, the same logit-additive null (20 tables,
    seeds 1..20) and variance decomposition.
  * No recorded value exists at the leaf level, so there is NO reproduction gate and NO registered prediction is scored;
    the leaf outcome prints its numbers with the "UNREGISTERED" banner and the anchor readout beside it as context only.
  * INERT WHEN ABSENT: `--level anchor` is the default and every leaf branch is guarded on it; the anchor readout, its
    outcome path (OUT), its pins (RECORDED_COUNTS, PIN["anchors"]) and its printed lines are byte-identical to 2ccd646.
    The leaf path writes only LEAF_OUT and never OUT.
  [ADDED 2026-09-23 by READY_canary_analyze_fix_and_leaf.md (ad65d09), insertion only] A SECOND REFUSAL, below the support
    one: if len(admissible) x the SMALLEST leg roster is below r_of's 50-point floor, every halving of the leg of record
    (K12, 12 models) reads nan and LEAF_OUT would be a file of nan; the readout refuses instead and writes nothing (K46 may
    still clear the floor at that size - it is refused with the others, because the leg of record cannot be read).
    WHAT THE REVIEWER'S INDEPENDENT RECOMPUTATION SAYS THIS WILL DO ON THE REAL DATA (joining
    experiment_results/promoted/bareq512_s42_reserved_leaf_assignments.csv to the x12 cache of record, 9,142 valid verdicts
    / 2,811 judged questions): 87 leaves, mean 32.3 judged questions, EXACTLY ONE at or above the 120 floor (n00000030, 122
    judged), 86 below it with the largest at 91. So `--dry-run --level leaf` prints the 87-row support table, the line
    "ADMISSIBLE LEAVES (>= 120 judged questions): 1" FIRST, and then the support refusal: the leaf question is
    UNDETERMINED-by-support on this tree and this judged set, and no leaf number exists to enter the record.
"""
import os, sys, math, random, json, time, argparse, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import profile_reliability as pr

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "profile_reliability_interaction_outcome.txt")
LEAF_OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "profile_reliability_interaction_leaf_outcome.txt")
LEVEL = "anchor"        # --level; "leaf" is the UNREGISTERED cell-set option added 2026-09-23, inert unless asked for
LEAF_FLOOR = 120        # the record's support floor per cell (STABLE-CELL-SET C1, stable_cell_set.FLOOR); below it: UNDETERMINED-by-support
MIN_ADMISSIBLE = 2      # fewer admissible leaves than this and the leaf readout REFUSES (no outcome written)
MIN_POINTS = 50         # r_of's own floor: points per halving = cells x models; below it a leg reads UNDETERMINED-by-support
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "claude", "Z--FAC-TUBerlin-THESIS-TaxoArena",
                       "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad", "pri")
TREE = "bareq512_s42"
POOL = "p2dca21ab5f4ef3ae"
EXCLUDE = "Meta-Llama-3-70B-Instruct"
SEED = 7
REPS = pr.REPS          # 40
Z = 1.96
BAR = 0.70
N_NULL = 20
PIN = dict(n12=9142, n20=12394, n=21536, models=20, q=2811, anchors=14, roster46=46)
RECORDED = {"K12": 0.9135, "K20": 0.9139, "J1": 0.6728, "J2": 0.7183}
RECORDED_JK = {"J1": (0.4932, 0.8524), "J2": (0.6076, 0.8291), "K12": (0.8706, 0.9565), "K20": (0.8705, 0.9573)}
RECORDED_COUNTS = {"Philosophy": 132, "Psychology": 260, "Economics": 178, "Other": 211, "Business": 174, "Math": 304,
                   "Computer science": 162, "Law": 271, "Health": 129, "Biology": 181, "History": 119, "Chemistry": 269,
                   "Engineering": 162, "Physics": 259}
sb = pr.sb


# ----------------------------------------------------------------------------------------------- statistics
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


def halvings_fixed(cells, qsel, build, models, rng, reps=REPS, min_cell=25):
    """Line-for-line mirror of profile_reliability.reliability that RETURNS the per-halving (cell, model, x, y) points
    (the ANCHOR-PROFILE-INTERVAL fixed-halving reader), so both demeanings and every leave-one-anchor-out fold read the
    same fits."""
    per_rep = []
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
        per_rep.append(P)
    return per_rep


def r_of(P, demean, drop=None, min_points=MIN_POINTS):
    Q = [p for p in P if p[0] != drop] if drop is not None else P
    if len(Q) < min_points: return float("nan")
    D = demean(Q)
    return pr.pearson([p[2] for p in D], [p[3] for p in D])


def mean_r(per_rep, demean, drop=None):
    return mean_sd([r_of(P, demean, drop) for P in per_rep])


def c0_check(per_rep):
    """Per-anchor mean of each half-profile over the models, every halving and both halves: max |mean|, and the
    per-anchor means on the first halving (printed)."""
    worst = 0.0; first = {}
    for h, P in enumerate(per_rep):
        sx = defaultdict(float); sy = defaultdict(float); n = defaultdict(int)
        for c, m, x, y in P:
            sx[c] += x; sy[c] += y; n[c] += 1
        for c in n:
            mx, my = sx[c] / n[c], sy[c] / n[c]
            worst = max(worst, abs(mx), abs(my))
            if h == 0: first[c] = (mx, my, n[c])
    return worst, first


def balanced(per_rep, models):
    """Every model present in every anchor's half-profile on every halving (the identity's precondition)."""
    for P in per_rep:
        cnt = defaultdict(set)
        for c, m, _, _ in P: cnt[c].add(m)
        if any(len(cnt[c]) != len(models) for c in cnt): return False
    return True


def leg(cells, qsel, build, models, tag, progress=None):
    """One leg: fixed-halving points; model-only and interaction-only r on them; LOAO jackknife fixed and re-halved."""
    anchors = list(cells)
    per_rep = halvings_fixed(cells, qsel, build, models, random.Random(SEED))
    out = dict(tag=tag, anchors=anchors, per_rep=per_rep)
    for name, dm in (("model", pr.demean_by_model), ("both", pr.demean_two_way)):
        r, sd, n = mean_r(per_rep, dm)
        loo_fixed = {a: mean_r(per_rep, dm, a)[0] for a in anchors}
        out[name] = dict(r=r, sd=sd, n=n, R=sb(r), loo_fixed=loo_fixed)
    # re-halved LOAO (fresh Random(7) on the 13 remaining cells, exactly as reliability() would draw them)
    for name, dm in (("model", pr.demean_by_model), ("both", pr.demean_two_way)):
        loo = {}
        for a in anchors:
            sub = {c: v for c, v in cells.items() if c != a}
            r_i, _, _ = pr.reliability(sub, qsel, build, models, random.Random(SEED), demean=dm)
            loo[a] = r_i
            if progress: progress("%s %s drop %s r_-i %.4f" % (tag, name, a, r_i))
        out[name]["loo_rehalved"] = loo
    # a per-halving identity check between the two demeanings (the C0 consequence, if it holds)
    diffs = [abs(r_of(P, pr.demean_by_model) - r_of(P, pr.demean_two_way)) for P in per_rep]
    out["max_abs_r_diff"] = max(d for d in diffs if d == d) if any(d == d for d in diffs) else float("nan")
    out["c0_worst"], out["c0_first"] = c0_check(per_rep)
    out["balanced"] = balanced(per_rep, models)
    return out


def intervals(d, key):
    """(R, halving SD, jk re-halved [lo, hi], jk fixed [lo, hi], SEs) for demeaning `key` of a leg."""
    e = d[key]; anchors = d["anchors"]
    R = e["R"]
    loo_re = [sb(e["loo_rehalved"][a]) for a in anchors]; loo_fx = [sb(e["loo_fixed"][a]) for a in anchors]
    se_re, lo_re, hi_re = jack(R, loo_re); se_fx, lo_fx, hi_fx = jack(R, loo_fx)
    return dict(R=R, r=e["r"], sd=e["sd"], n=e["n"], se_re=se_re, lo_re=lo_re, hi_re=hi_re, se_fx=se_fx, lo_fx=lo_fx, hi_fx=hi_fx,
                loo_re=dict(zip(anchors, loo_re)), loo_fx=dict(zip(anchors, loo_fx)))


# ----------------------------------------------------------------------------------------------- the null
def fit_additive_logit(k, n, tol=1e-10, max_iter=500, clip=15.0):
    """MLE of logit p_mc = a_m - d_c on a (successes k, trials n) table (M x C), alternating 1-D Newton steps.
    Returns a (M), d (C, centred to sum zero), iterations, clip count."""
    k = np.asarray(k, float); n = np.asarray(n, float)
    M, C = k.shape
    a = np.zeros(M); d = np.zeros(C); clipped = 0
    for it in range(max_iter):
        a_old = a.copy(); d_old = d.copy()
        eta = a[:, None] - d[None, :]; p = 1 / (1 + np.exp(-eta))
        g = (k - n * p).sum(1); h = (n * p * (1 - p)).sum(1)
        a = a + np.where(h > 0, g / np.maximum(h, 1e-12), 0.0)
        eta = a[:, None] - d[None, :]; p = 1 / (1 + np.exp(-eta))
        g = (n * p - k).sum(0); h = (n * p * (1 - p)).sum(0)
        d = d + np.where(h > 0, g / np.maximum(h, 1e-12), 0.0)
        shift = d.mean(); d = d - shift; a = a - shift
        if np.abs(a).max() > clip or np.abs(d).max() > clip:
            clipped += int((np.abs(a) > clip).sum() + (np.abs(d) > clip).sum())
            a = np.clip(a, -clip, clip); d = np.clip(d, -clip, clip)
        if max(np.abs(a - a_old).max(), np.abs(d - d_old).max()) < tol:
            return a, d, it + 1, clipped
    return a, d, max_iter, clipped


def key_table(cells, K, models):
    """(successes, trials) per (model, anchor) over the anchors' questions; rows missing for a model are not trials."""
    anchors = list(cells)
    k = np.zeros((len(models), len(anchors))); n = np.zeros((len(models), len(anchors)))
    for j, c in enumerate(anchors):
        for q in cells[c]:
            row = K.get(q, {})
            for i, m in enumerate(models):
                v = row.get(m)
                if v is not None: k[i, j] += v; n[i, j] += 1
    return k, n


def variance_decomposition(k, n):
    T = k / np.maximum(n, 1)
    gm = T.mean(); rm = T.mean(1, keepdims=True) - gm; cs = T.mean(0, keepdims=True) - gm; inter = T - gm - rm - cs
    vm, vc, vi = float(rm.var()), float(cs.var()), float(inter.var()); tot = vm + vc + vi
    return dict(model=vm, anchor=vc, inter=vi, shares=(vm / tot, vc / tot, vi / tot), T=T)


def null_tables(cells, K, models, n_tables, seeds, scale="logit"):
    """Fit the additive logit on the real table; simulate `n_tables` no-interaction tables on the same questions;
    read the instrument under both demeanings on each (same halvings, Random(7)). scale="logit" is the REGISTERED
    null Bernoulli(logistic(a_m - d_c)); scale="prob" (unregistered, beside) is additive on the accuracy scale,
    p_mc = clip(grand + model + anchor main effects), i.e. zero accuracy-scale interaction by construction."""
    anchors = list(cells); k, n = key_table(cells, K, models)
    a, d, iters, clipped = fit_additive_logit(k, n)
    if scale == "logit":
        P = 1 / (1 + np.exp(-(a[:, None] - d[None, :])))
    else:
        T = k / np.maximum(n, 1); gm = T.mean()
        P = np.clip(gm + (T.mean(1, keepdims=True) - gm) + (T.mean(0, keepdims=True) - gm), 0.01, 0.99)
    qsel = set(q for v in cells.values() for q in v)
    reads = []
    for t in range(n_tables):
        rs = np.random.RandomState(seeds[t])
        Ksim = {}
        for j, c in enumerate(anchors):
            draws = rs.rand(len(cells[c]), len(models)) < P[:, j][None, :]
            for qi, q in enumerate(cells[c]):
                Ksim[q] = {m: int(draws[qi, i]) for i, m in enumerate(models)}
        def kb(cqs, Ksim=Ksim):
            return {m: sum(Ksim[q][m] for q in cqs) / len(cqs) for m in models}
        per_rep = halvings_fixed(cells, qsel, kb, models, random.Random(SEED))
        reads.append((sb(mean_r(per_rep, pr.demean_by_model)[0]), sb(mean_r(per_rep, pr.demean_two_way)[0])))
    return dict(a=a, d=d, iters=iters, clipped=clipped, P=P, reads=reads, k=k, n=n)


def summarise_null(reads, idx):
    v = sorted(x[idx] for x in reads)
    med = v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2
    return med, v[0], v[-1]


# ----------------------------------------------------------------------------------------------- the leaf cell set (--level leaf)
def admissible_leaves(cells, floor=LEAF_FLOOR):
    """Split a cell -> questions map by the record's support floor. Returns (admissible, undetermined counts). An
    inadmissible cell is DROPPED: it is never merged into a parent, a sibling or a remainder cell, and never pooled."""
    adm = {c: v for c, v in cells.items() if len(v) >= floor}
    und = {c: len(v) for c, v in cells.items() if len(v) < floor}
    return adm, und


def support_refusal(adm, und, floor=LEAF_FLOOR):
    """The refusal text when fewer than MIN_ADMISSIBLE cells clear the floor, or None."""
    if len(adm) >= MIN_ADMISSIBLE: return None
    return ("[SUPPORT] UNDETERMINED-by-support: %d cell(s) carry >= %d judged questions, fewer than the %d a (model x cell) "
            "interaction needs; %d cell(s) are below the floor (largest %d). Nothing is pooled, no R is read and no outcome "
            "file is written." % (len(adm), floor, MIN_ADMISSIBLE, len(und), max(und.values()) if und else 0))


def points_refusal(n_cells, rosters):
    """The second refusal (READY ad65d09 defect 4): r_of reads nan below MIN_POINTS points per halving (points = cells x
    models). If the SMALLEST leg roster cannot clear it, the leg of record (K12) is nan and the outcome would be a file of
    nan; refuse and write nothing. A larger roster may still clear the floor - it is refused with the others, because the
    leg of record cannot be read at this cell count."""
    smallest = min(rosters)
    if n_cells * smallest >= MIN_POINTS: return None
    return ("[SUPPORT] UNDETERMINED-by-support: %d admissible leaves x the smallest leg roster (%d models) = %d points per halving, below "
            "the instrument's floor of %d; the leg of record would read nan on every halving. No R is read and no outcome file is written."
            % (n_cells, smallest, n_cells * smallest, MIN_POINTS))


def leaf_cells(qs, route, pool, nodes, say):
    """The frozen tree's LEAF cells over the judged questions, in the insertion order of the sorted qids (the record's
    convention; the halvings depend on it), with the support rule enforced and the admissible count printed FIRST."""
    cells = defaultdict(list)
    for q in qs: cells[route[q]].append(q)
    pool_n = defaultdict(int)
    for q in pool:
        if q in route: pool_n[route[q]] += 1
    adm, und = admissible_leaves(cells)
    label = lambda c: (nodes.get(c, {}) or {}).get("label", "?")
    say("")
    say("--- LEAF CELL SET (--level leaf; UNREGISTERED instrument, code only) ---")
    say("  ADMISSIBLE LEAVES (>= %d judged questions): %d" % (LEAF_FLOOR, len(adm)))
    say("  tree %s: the primary routing uses %d distinct leaves over the pool of record and %d over the %d judged questions;"
        % (TREE, len(pool_n), len(cells), len(qs)))
    say("  SUPPORT RULE (the record's floor, STABLE-CELL-SET C1 = 120): a leaf below it is UNDETERMINED-by-support and is DROPPED -")
    say("  never merged into a parent, a sibling or a remainder cell, never pooled. The floor is read on the leaf's JUDGED questions")
    say("  (the instrument's own denominator, a subset of the pool questions the floor of record counts: the stricter reading);")
    say("  the routed POOL count is printed beside each leaf.")
    for c in sorted(cells, key=lambda c: -len(cells[c])):
        say("    %-12s %-34s judged %4d | routed pool %4d | %s" % (c, label(c)[:34], len(cells[c]), pool_n.get(c, 0),
                                                                   "ADMISSIBLE" if c in adm else "UNDETERMINED-by-support"))
    say("  UNDETERMINED-by-support: %d leaves holding %d of the %d judged questions (never pooled, never read)"
        % (len(und), sum(und.values()), len(qs)))
    return adm, und


# ----------------------------------------------------------------------------------------------- data of record
def load_record(say, level="anchor"):
    import rejudge_grok as rj, rubric_p8 as p8, rubric_512 as r512, stack_judge as sj, judge_free_tests as jf, x20_replications as xr
    assert abs(rj.PRIOR - 0.5) < 1e-12, "rj.PRIOR is %r, the record pins 0.5" % rj.PRIOR
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    x12_path = sj.cache_path()
    con12 = sqlite3.connect("file:%s?mode=ro" % x12_path.replace("\\", "/"), uri=True)
    r12 = [r for r in con12.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    con12.close()
    con20 = sqlite3.connect("file:%s?mode=ro" % xr.X20.replace("\\", "/"), uri=True)
    r20 = [r for r in con20.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    con20.close()
    say("  x12 cache %s: %d valid verdicts (pinned %d)" % (os.path.basename(x12_path), len(r12), PIN["n12"]))
    say("  x20 cache %s: %d valid verdicts (pinned %d); never read alone" % (os.path.basename(xr.X20), len(r20), PIN["n20"]))
    if len(r12) != PIN["n12"] or len(r20) != PIN["n20"]:
        raise SystemExit("[PIN] caches are not the board of record")
    rows12 = [(a, b, q, w) for a, b, q, w, _ in r12]; rows_m = rows12 + [(a, b, q, w) for a, b, q, w, _ in r20]
    models12 = sorted(p8.ARENA12); models20 = sorted({r[0] for r in rows_m} | {r[1] for r in rows_m})
    m12_in_cache = sorted({r[0] for r in rows12} | {r[1] for r in rows12})
    if m12_in_cache != models12 or len(models20) != PIN["models"] or EXCLUDE in models20:
        raise SystemExit("[PIN] model sets: x12 %d, merged %d, %s present %s" % (len(m12_in_cache), len(models20), EXCLUDE, EXCLUDE in models20))

    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB.replace("\\", "/"), uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    roster = sorted(m for (m,) in ev.execute("SELECT DISTINCT model_name FROM eval_results") if m != EXCLUDE)
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m != EXCLUDE: K[q][m] = int(c or 0)
    ev.close()
    say("  eval_results roster minus %s: %d models (pinned %d); ARENA12 subset: %s" % (EXCLUDE, len(roster), PIN["roster46"], set(models12) <= set(roster)))
    if len(roster) != PIN["roster46"] or not set(models12) <= set(roster):
        raise SystemExit("[PIN] key roster")

    route = r512.primary_routing(TREE)
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anc = r512.anchor_fn(nodes)
    by12 = defaultdict(list); bym = defaultdict(list)
    for r in rows12: by12[r[2]].append(r)
    for r in rows_m: bym[r[2]].append(r)
    qs = sorted(set(route) & set(by12)); qsel = set(qs)
    if set(bym) != set(by12) or len(qs) != PIN["q"] or not set(bym) <= pool:
        raise SystemExit("[PIN] judged question sets: x12 %d, merged %d, routed+judged %d, outside pool %d"
                         % (len(by12), len(bym), len(qs), len(set(bym) - pool)))
    undetermined = {}
    if level == "leaf":                                      # UNREGISTERED cell set (2026-09-23); the anchor branch below is untouched
        usable, undetermined = leaf_cells(qs, route, pool, nodes, say)
    else:
        anc_cells = defaultdict(list)
        for q in qs: anc_cells[anc(route[q])].append(q)          # the recorded dict order (the halvings depend on it)
        usable = {c: v for c, v in anc_cells.items() if len(v) >= 50}
        counts = {c: len(v) for c, v in usable.items()}
        if len(usable) != PIN["anchors"] or counts != RECORDED_COUNTS:
            raise SystemExit("[PIN] anchor counts differ from the recorded run: %s" % counts)
        say("  pool %s: %d judged questions all in the reserved pool; %d anchors, counts equal to the recorded run's" % (POOL, len(qs), len(usable)))
        say("  anchors (judged q): " + ", ".join("%s %d" % (c, len(usable[c])) for c in usable))
    gap = {m: sum(1 for q in qs if m not in K.get(q, {})) for m in roster}
    gap = {m: v for m, v in gap.items() if v}
    say("  key rows missing on the judged questions, by model: %s" % (gap or "none"))

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

    return dict(usable=usable, undetermined=undetermined, level=level, qsel=qsel, K=K, models12=models12, models20=models20, roster=roster,
                legs=[("K12", "key, 12 models (ARENA12; the roster of the recorded 0.9135) - LEG OF RECORD", kb_for(models12), models12),
                      ("K46", "key, %d models (every eval_results model minus %s) - beside, not the leg of record" % (len(roster), EXCLUDE), kb_for(roster), roster),
                      ("K20", "key, 20 models (the merged board's roster; recorded 0.9139) - beside", kb_for(models20), models20),
                      ("J1", "x12 judge board, 12 rows (recorded 0.6728)", jb_for(by12, models12), models12),
                      ("J2", "MERGED judge board, 20 rows, x20_merged rows (recorded 0.7183 [0.6076, 0.8291])", jb_for(bym, models20), models20)])


# ----------------------------------------------------------------------------------------------- the readout
def score_range(v, lo, hi): return "HELD" if (v == v and lo <= v <= hi) else "FAILED"


def readout(D, L, dry=False):
    say = L.append
    usable, qsel, K = D["usable"], D["qsel"], D["K"]
    t0 = time.time()
    res = {}
    for tag, desc, build, models in D["legs"]:
        res[tag] = leg(usable, qsel, build, models, tag, progress=lambda s: print("   ", s, "%.0fs" % (time.time() - t0), flush=True))
        print("leg", tag, "done: model-only R %.4f, interaction-only R %.4f (%.0fs)" % (res[tag]["model"]["R"], res[tag]["both"]["R"], time.time() - t0), flush=True)

    # ---- C0
    say("")
    say("=== C0 (before any number is read): per-anchor mean of each judge half-profile over its models ===")
    for tag in ("J1", "J2"):
        d = res[tag]
        say("  %s: max |per-anchor mean| over %d halvings x 2 halves x 14 anchors = %.3e; balanced (every model in every anchor's half): %s"
            % (tag, len(d["per_rep"]), d["c0_worst"], d["balanced"]))
        say("      first halving: " + ", ".join("%s (%+.1e, %+.1e)" % (c, v[0], v[1]) for c, v in d["c0_first"].items()))
        say("      max |r_model-only - r_interaction-only| over the halvings: %.3e" % d["max_abs_r_diff"])
    centred = all(res[t]["c0_worst"] < 1e-6 and res[t]["balanced"] for t in ("J1", "J2"))
    if centred:
        say("  C0 STATEMENT: the per-anchor Bradley-Terry fit (rj.mm_fit) centres theta over the models of the fit by construction")
        say("  (theta_m - mean_m theta), so every judge half-profile has anchor mean 0 and the anchor-demeaning step subtracts")
        say("  0 from every point (after model-demeaning the anchor means equal minus the grand mean, itself 0). The judge legs'")
        say("  interaction-only R therefore EQUALS the recorded model-demeaned R by IDENTITY. No 'fall' exists to report.")
    else:
        say("  C0 STATEMENT: the judge half-profiles are NOT centred per anchor (or the table is unbalanced); the judge legs'")
        say("  interaction-only R is a different number from the model-demeaned one and is read as such below.")
    for tag in ("K12", "K46"):
        say("  %s (key, for contrast): max |per-anchor mean| = %.4f (anchor difficulty; the demeaning removes it)" % (tag, res[tag]["c0_worst"]))
    if dry:
        return res, centred, None, None

    # ---- C1
    say("")
    say("=== C1: interaction-only R per leg, with the leave-one-anchor-out jackknife (re-halved primary; fixed beside) and the halving SD ===")
    say("  instrument: profile_reliability.reliability under --interaction-only (demean_two_way) on the same 40 halvings (Random(7));")
    say("  KEY DENOMINATOR: each anchor's JUDGED questions (2,811 of pool %s, 119-304 per anchor), halved; R = Spearman-Brown of the mean r." % POOL)
    say("  McNEMAR-ESTABLISHED RULE: no wrong-direction count exists here (nothing is compared to the key's direction); stated, not applied.")
    say("  %-4s %-8s %8s %8s %8s  %-18s %-18s | %-8s %8s %-18s %8s %s"
        % ("leg", "demean", "r", "R(SB)", "halvSD", "jk RE-HALVED 95%", "jk FIXED 95%", "recorded", "diff", "recorded jk", "repro", "gate"))
    gate = {}
    summ = {}
    for tag, desc, _, _ in D["legs"]:
        for key in ("model", "both"):
            iv = intervals(res[tag], key); summ[(tag, key)] = iv
            rec = RECORDED.get(tag) if key == "model" else None
            rjk = RECORDED_JK.get(tag) if key == "model" else None
            repro = ("%.4f" % iv["R"] == "%.4f" % rec) if rec is not None else None
            if key == "model" and rec is not None: gate[tag] = repro
            say("  %-4s %-8s %8.4f %8.4f %8.4f  [%6.4f, %6.4f]   [%6.4f, %6.4f]   | %-8s %8s %-18s %8s %s"
                % (tag, "model" if key == "model" else "both", iv["r"], iv["R"], iv["sd"], iv["lo_re"], iv["hi_re"], iv["lo_fx"], iv["hi_fx"],
                   "%.4f" % rec if rec is not None else "-", "%+.4f" % (iv["R"] - rec) if rec is not None else "-",
                   "[%.4f, %.4f]" % rjk if rjk else "-", "" if repro is None else ("yes" if repro else "NO"),
                   ("REPRODUCTION GATE" if tag in ("K12", "J1", "J2") and key == "model" else "")))
        say("       %s" % desc)
    say("  reproduction gate (0.9135 / 0.6728 / 0.7183 to 4 dp on the fixed halvings): K12 %s, J1 %s, J2 %s%s"
        % tuple(["yes" if gate.get(t) else "NO" for t in ("K12", "J1", "J2")] + ["" if all(gate.get(t) for t in ("K12", "J1", "J2")) else "  -> GATE FAILED: nothing below is a number of record"]))
    gate_ok = all(gate.get(t) for t in ("K12", "J1", "J2"))
    say("  per-anchor leave-one-out R (interaction-only, re-halved), K12 and K46 (which anchors carry the key reading):")
    for tag in ("K12", "K46"):
        iv = summ[(tag, "both")]
        say("    %s: " % tag + ", ".join("drop %s %.4f" % (a, iv["loo_re"][a]) for a in sorted(iv["loo_re"], key=lambda a: iv["loo_re"][a])))

    # ---- C2: null + variance decomposition
    say("")
    say("=== C2: the no-interaction null Bernoulli(logistic(a_m - d_c)) and the variance decomposition ===")
    nulls = {}
    for tag, models in (("K46", D["roster"]), ("K12", D["models12"])):
        nd = null_tables(usable, K, models, N_NULL, list(range(1, N_NULL + 1))); nulls[tag] = nd
        vd = variance_decomposition(nd["k"], nd["n"]); nd["vd"] = vd
        m_med, m_lo, m_hi = summarise_null(nd["reads"], 0); b_med, b_lo, b_hi = summarise_null(nd["reads"], 1)
        say("  %s table (%d models x %d anchors; trials per cell %d-%d): additive-logit MLE in %d sweeps, %d logits clipped"
            % (tag, len(models), len(usable), int(nd["n"].min()), int(nd["n"].max()), nd["iters"], nd["clipped"]))
        say("    a_m range [%.3f, %.3f]; d_c (centred): %s" % (nd["a"].min(), nd["a"].max(), ", ".join("%s %+.3f" % (c, v) for c, v in zip(usable, nd["d"]))))
        say("    variance of the accuracy table: model main %.5f, anchor main %.5f, interaction %.5f (shares %.2f / %.2f / %.2f)"
            % (vd["model"], vd["anchor"], vd["inter"], *vd["shares"]))
        say("    NULL, %d tables, model-only instrument: median %.4f, range [%.4f, %.4f]  (real %.4f)"
            % (N_NULL, m_med, m_lo, m_hi, summ[(tag, "model")]["R"]))
        say("    NULL, %d tables, interaction-only:      median %.4f, range [%.4f, %.4f]  (real %.4f; real minus null median %+.4f)"
            % (N_NULL, b_med, b_lo, b_hi, summ[(tag, "both")]["R"], summ[(tag, "both")]["R"] - b_med))
        nd["summary"] = dict(m=(m_med, m_lo, m_hi), b=(b_med, b_lo, b_hi))
        npb = null_tables(usable, K, models, N_NULL, list(range(101, 101 + N_NULL)), scale="prob")
        pm = summarise_null(npb["reads"], 0); pb = summarise_null(npb["reads"], 1)
        say("    UNREGISTERED, beside: probability-additive null (zero accuracy-scale interaction by construction): model-only median %.4f"
            % pm[0])
        say("      [%.4f, %.4f]; interaction-only median %.4f [%.4f, %.4f] (the sampling floor of the instrument at this cell size)"
            % (pm[1], pm[2], *pb))
        nd["summary_prob"] = dict(m=pm, b=pb)
    say("  (a no-LOGIT-interaction table keeps a reproducible accuracy-scale interaction from the logistic curvature, so the null's")
    say("   interaction-only R is not zero by construction; it is the floor the real reading must sit above.)")
    return res, centred, summ, nulls, gate_ok


def verdicts(D, L, res, centred, summ, nulls, gate_ok):
    say = L.append
    say("")
    say("=== PREDICTIONS AND FALSIFIER (scored on the leg of record K12; K46 beside, labelled) ===")
    if not gate_ok:
        say("  REPRODUCTION GATE FAILED: no prediction is scored; the recorded values did not reproduce on the fixed halvings.")
        return
    out = {}
    for tag in ("K12", "K46"):
        iv = summ[(tag, "both")]; R = iv["R"]
        p1 = score_range(R, 0.80, 0.88); p1p = score_range(R, 0.78, 0.88)
        cls_re = "PASS" if iv["lo_re"] >= BAR else ("PASS-WITH-INTERVAL" if R >= BAR else "FAIL")
        cls_fx = "PASS" if iv["lo_fx"] >= BAR else ("PASS-WITH-INTERVAL" if R >= BAR else "FAIL")
        cls = cls_re if (cls_re == cls_fx) else "UNDETERMINED (re-halved %s, fixed %s)" % (cls_re, cls_fx)
        p2 = "HELD" if R >= BAR else "FAILED"
        fals = R < BAR
        nd = nulls[tag]["summary"]
        p4 = "HELD" if nd["m"][0] <= 0.90 else "FAILED"
        reg = "HELD" if (nd["b"][0] <= 0.30 and R - nd["b"][0] >= 0.50) else "FAILED"
        lab = "LEG OF RECORD" if tag == "K12" else "beside, not the leg of record"
        say("  --- %s (%s): interaction-only R = %.4f, re-halved jk [%.4f, %.4f], fixed jk [%.4f, %.4f], halving SD %.4f ---"
            % (tag, lab, R, iv["lo_re"], iv["hi_re"], iv["lo_fx"], iv["hi_fx"], iv["sd"]))
        say("    P1  (lane-2 brief, prediction of record) key interaction-only R in [0.80, 0.88]: %s" % p1)
        say("    P1' (night schedule wording)              key interaction-only R in [0.78, 0.88]: %s" % p1p)
        say("    P2  key interaction-only R above the 0.70 bar: %s on the point; class %s (lower bound rule; re-halved primary)" % (p2, cls))
        say("    P4  no-interaction null on the model-only instrument <= 0.90: %s (null median %.4f, range [%.4f, %.4f])" % (p4, *nd["m"]))
        say("    registrar's addition: null under the interaction-only demeaning <= 0.30 AND real >= 0.50 above it: %s (null median %.4f, real - null %+.4f)"
            % (reg, nd["b"][0], R - nd["b"][0]))
        say("    FALSIFIER key interaction-only R < 0.70 at the point: %s" % ("FIRES" if fals else "silent"))
        out[tag] = dict(R=R, p1=p1, p1p=p1p, p2=p2, cls=cls, p4=p4, reg=reg, fals=fals)
    j2 = summ[("J2", "both")]; j1 = summ[("J1", "both")]
    say("  --- P3, judge J2 interaction-only R in [0.55, 0.70] on the point ---")
    if centred:
        say("    FAILED-BY-IDENTITY: C0 holds (per-anchor BT theta is centred by construction, max |anchor mean| < 1e-6, table balanced),")
        say("    so J2's interaction-only R = %.4f = its model-demeaned R %.4f (recorded 0.7183) exactly; J1 %.4f = %.4f (recorded 0.6728)."
            % (j2["R"], summ[("J2", "model")]["R"], j1["R"], summ[("J1", "model")]["R"]))
        say("    The brief's expectation of a fall was wrong for a structural reason: the demeaning removes nothing from a centred")
        say("    profile. The judge legs carry no falsifier and are read beside their recorded values.")
        p3 = "FAILED-BY-IDENTITY"
    else:
        p3 = score_range(j2["R"], 0.55, 0.70)
        say("    %s: J2 interaction-only R = %.4f [%.4f, %.4f] (model-demeaned %.4f)" % (p3, j2["R"], j2["lo_re"], j2["hi_re"], summ[("J2", "model")]["R"]))
    k = out["K12"]
    say("")
    say("=== VERDICT LINES ===")
    say("  C0: %s" % ("judge half-profiles centred per anchor by construction (identity)" if centred else "judge half-profiles NOT centred; interaction-only differs"))
    say("  C1: K12 interaction-only %.4f [%.4f, %.4f] (model-demeaned %.4f, recorded 0.9135); K46 %.4f [%.4f, %.4f] (model-demeaned %.4f, no recorded value);"
        % (k["R"], summ[("K12", "both")]["lo_re"], summ[("K12", "both")]["hi_re"], summ[("K12", "model")]["R"],
           out["K46"]["R"], summ[("K46", "both")]["lo_re"], summ[("K46", "both")]["hi_re"], summ[("K46", "model")]["R"]))
    say("      J1 %.4f (= model-demeaned %.4f, recorded 0.6728); J2 %.4f [%.4f, %.4f] (= model-demeaned %.4f, recorded 0.7183)"
        % (j1["R"], summ[("J1", "model")]["R"], j2["R"], j2["lo_re"], j2["hi_re"], summ[("J2", "model")]["R"]))
    say("  C2: null (K46) model-only median %.4f [%.4f, %.4f], interaction-only median %.4f [%.4f, %.4f]; variance shares model / anchor / interaction %.2f / %.2f / %.2f"
        % (*nulls["K46"]["summary"]["m"], *nulls["K46"]["summary"]["b"], *nulls["K46"]["vd"]["shares"]))
    say("      null (K12) model-only median %.4f [%.4f, %.4f], interaction-only median %.4f [%.4f, %.4f]; shares %.2f / %.2f / %.2f"
        % (*nulls["K12"]["summary"]["m"], *nulls["K12"]["summary"]["b"], *nulls["K12"]["vd"]["shares"]))
    say("  P1 %s | P1' %s | P2 %s (%s) | P3 %s | P4 %s | registrar's null addition %s | FALSIFIER %s   [K12, the leg of record]"
        % (k["p1"], k["p1p"], k["p2"], k["cls"], p3, k["p4"], k["reg"], "FIRES" if k["fals"] else "silent"))
    say("  K46 beside: P1 %s | P1' %s | P2 %s (%s) | P4 %s | registrar's addition %s | falsifier %s"
        % (out["K46"]["p1"], out["K46"]["p1p"], out["K46"]["p2"], out["K46"]["cls"], out["K46"]["p4"], out["K46"]["reg"], "FIRES" if out["K46"]["fals"] else "silent"))
    say("  REGISTRATION NOTE for the registrar: '(K) the 46-model key ... beside 0.9135' names two rosters; 0.9135 is the 12-model")
    say("  ARENA12 key (profile_reliability.txt line 2; programme L3453). K12 is scored as the leg of record here; a bracket must fix it.")
    if k["fals"]:
        say("  CONSEQUENCE (registered): PROFILE-RELIABILITY's row takes the bracket 'interaction-only %.4f; the 0.9135 is not a profile" % k["R"])
        say("  reliability'; FRAMEWORK L117's 'key 0.9135-0.9139' is bracketed; the atlas's key-built rows carry 'offset, not order'.")
    elif k["p2"] == "HELD":
        say("  CONSEQUENCE (registered): the v113 bracket is answered by insertion (interaction-only %.4f beside the 0.9135 in" % k["R"])
        say("  PROFILE-RELIABILITY's row and FRAMEWORK L117); the atlas's key-built rows may say 'profile' with this value beside them.")


# ----------------------------------------------------------------------------------------------- the leaf readout (--level leaf)
def leaf_readout(D, L):
    """The SAME instrument as readout(), on the admissible LEAF cells: same halvings (Random(7), 40 reps), same two-way
    demeaning, same Spearman-Brown, same leave-one-CELL-out jackknife and halving SD, same logit-additive null. No recorded
    leaf value exists, so there is no reproduction gate and no registered prediction is scored."""
    say = L.append
    usable, qsel, K = D["usable"], D["qsel"], D["K"]
    t0 = time.time()
    res = {}; summ = {}
    for tag, desc, build, models in D["legs"]:
        res[tag] = leg(usable, qsel, build, models, tag, progress=lambda s: print("   ", s, "%.0fs" % (time.time() - t0), flush=True))
        for key in ("model", "both"): summ[(tag, key)] = intervals(res[tag], key)
        print("leg", tag, "done: model-only R %.4f, interaction-only R %.4f (%.0fs)" % (res[tag]["model"]["R"], res[tag]["both"]["R"], time.time() - t0), flush=True)

    say("")
    say("=== L0: the cell set and the instrument's own point floor ===")
    say("  %d admissible leaves, %d judged questions in them (of %d judged; %d leaves are UNDETERMINED-by-support and were dropped, never pooled)"
        % (len(usable), sum(len(v) for v in usable.values()), len(qsel), len(D["undetermined"])))
    say("  cells (judged q): " + ", ".join("%s %d" % (c, len(usable[c])) for c in usable))
    for tag, desc, _, models in D["legs"]:
        pts = len(usable) * len(models)
        say("    %-4s roster %2d models -> %d points per halving (r_of's floor is %d): %s"
            % (tag, len(models), pts, MIN_POINTS, "read" if pts >= MIN_POINTS else "UNDETERMINED-by-support (no R is a number for this leg)"))
    say("  RESOLUTION: the leave-one-cell-out jackknife has %d folds here (the anchor readout has 14) and the two-way demeaning removes a"
        % len(usable))
    say("  cell main effect from a table of %d cells, so the interaction-only reading is the residual of a small table: its interval is a"
        % len(usable))
    say("  resolution statement, not a confidence statement.")

    say("")
    say("=== L1 (C0 at the leaf level): per-cell mean of each judge half-profile over its models ===")
    for tag in ("J1", "J2"):
        d = res[tag]
        say("  %s: max |per-cell mean| over %d halvings x 2 halves x %d cells = %.3e; balanced (every model in every cell's half): %s"
            % (tag, len(d["per_rep"]), len(usable), d["c0_worst"], d["balanced"]))
        say("      max |r_model-only - r_interaction-only| over the halvings: %.3e" % d["max_abs_r_diff"])
    centred = all(res[t]["c0_worst"] < 1e-6 and res[t]["balanced"] for t in ("J1", "J2"))
    say("  %s" % ("IDENTITY: the per-cell Bradley-Terry fit centres theta over the models of the fit, so the judge legs' interaction-only R "
                  "EQUALS their model-demeaned R by construction at the leaf level too."
                  if centred else "the judge half-profiles are NOT centred per cell (or the table is unbalanced); the two demeanings differ."))
    for tag in ("K12", "K46"):
        say("  %s (key, for contrast): max |per-cell mean| = %.4f (cell difficulty; the demeaning removes it)" % (tag, res[tag]["c0_worst"]))

    say("")
    say("=== L2: interaction-only R per leg on the LEAF cells, with the leave-one-cell-out jackknife (re-halved primary; fixed beside) ===")
    say("  KEY DENOMINATOR: each admissible leaf's JUDGED questions (%s), halved; R = Spearman-Brown of the mean r over 40 halvings."
        % ", ".join("%s %d" % (c, len(usable[c])) for c in usable))
    say("  McNEMAR-ESTABLISHED RULE: no wrong-direction count exists here (nothing is compared to the key's direction); stated, not applied.")
    say("  %-4s %-8s %8s %8s %8s  %-18s %-18s %s" % ("leg", "demean", "r", "R(SB)", "halvSD", "jk RE-HALVED 95%", "jk FIXED 95%", "anchor-level R (context only)"))
    for tag, desc, _, models in D["legs"]:
        for key in ("model", "both"):
            iv = summ[(tag, key)]
            ctx = RECORDED.get(tag) if key == "model" else None
            if iv["R"] != iv["R"]:
                say("  %-4s %-8s UNDETERMINED-by-support (%d points per halving < %d)" % (tag, key, len(usable) * len(models), MIN_POINTS)); continue
            say("  %-4s %-8s %8.4f %8.4f %8.4f  [%6.4f, %6.4f]   [%6.4f, %6.4f]   %s"
                % (tag, key, iv["r"], iv["R"], iv["sd"], iv["lo_re"], iv["hi_re"], iv["lo_fx"], iv["hi_fx"],
                   ("anchor-level model-demeaned %.4f (recorded; NOT a comparator by level)" % ctx) if ctx is not None else ""))
        say("       %s" % desc)

    say("")
    say("=== L3: the no-interaction null Bernoulli(logistic(a_m - d_c)) on the leaf cells, and the variance decomposition ===")
    nulls = {}
    for tag, models in (("K46", D["roster"]), ("K12", D["models12"])):
        nd = null_tables(usable, K, models, N_NULL, list(range(1, N_NULL + 1))); nulls[tag] = nd
        vd = variance_decomposition(nd["k"], nd["n"]); nd["vd"] = vd
        m_med, m_lo, m_hi = summarise_null(nd["reads"], 0); b_med, b_lo, b_hi = summarise_null(nd["reads"], 1)
        nd["summary"] = dict(m=(m_med, m_lo, m_hi), b=(b_med, b_lo, b_hi))
        say("  %s table (%d models x %d leaf cells; trials per cell %d-%d): additive-logit MLE in %d sweeps, %d logits clipped"
            % (tag, len(models), len(usable), int(nd["n"].min()), int(nd["n"].max()), nd["iters"], nd["clipped"]))
        say("    variance of the accuracy table: model main %.5f, cell main %.5f, interaction %.5f (shares %.2f / %.2f / %.2f)"
            % (vd["model"], vd["anchor"], vd["inter"], *vd["shares"]))
        say("    NULL, %d tables, model-only instrument: median %.4f, range [%.4f, %.4f]  (real %.4f)" % (N_NULL, m_med, m_lo, m_hi, summ[(tag, "model")]["R"]))
        say("    NULL, %d tables, interaction-only:      median %.4f, range [%.4f, %.4f]  (real %.4f; real minus null median %+.4f)"
            % (N_NULL, b_med, b_lo, b_hi, summ[(tag, "both")]["R"], summ[(tag, "both")]["R"] - b_med))

    say("")
    say("=== LEAF VERDICT LINES (UNREGISTERED: nothing here is scored against a registered prediction or falsifier) ===")
    k12, k46 = summ[("K12", "both")], summ[("K46", "both")]
    say("  L2: K12 (leg of record's roster) interaction-only %.4f [%.4f, %.4f]; K46 %.4f [%.4f, %.4f] on %d admissible leaves"
        % (k12["R"], k12["lo_re"], k12["hi_re"], k46["R"], k46["lo_re"], k46["hi_re"], len(usable)))
    say("  L3: K46 null interaction-only median %.4f [%.4f, %.4f]; real minus null %+.4f. K12 null median %.4f; real minus null %+.4f."
        % (*nulls["K46"]["summary"]["b"], k46["R"] - nulls["K46"]["summary"]["b"][0],
           nulls["K12"]["summary"]["b"][0], k12["R"] - nulls["K12"]["summary"]["b"][0]))
    say("  WHAT THIS IS NOT: not a registered test; not comparable BY LEVEL to the 14-anchor readout (different cell set, different")
    say("  denominators, different number of jackknife folds); the %d leaves below the 120-question floor are UNDETERMINED-by-support"
        % len(D["undetermined"]))
    say("  and carry no reading at all - they are not pooled into anything. The author's word is required before any number here")
    say("  enters the record.")
    return res, summ, nulls


# ----------------------------------------------------------------------------------------------- selftest
def selftest():
    print("=== PROFILE-RELIABILITY-INTERACTION --selftest (synthetic tables; nothing of record is opened) ===")
    rng = random.Random(5); rs = np.random.RandomState(5)
    models = ["m%02d" % i for i in range(12)]
    cells = {"A%d" % c: list(range(c * 1000, c * 1000 + 200)) for c in range(8)}
    qsel = set(q for v in cells.values() for q in v)
    a = np.linspace(-1.5, 1.5, 12); d = np.linspace(-1.2, 1.2, 8)
    # (1) additive-logit table: no interaction -> interaction-only R small, model-only R high (anchor difficulty carries it)
    def make(K_inter, scale="logit"):
        K = {}
        for j, c in enumerate(cells):
            for q in cells[c]:
                if scale == "logit":
                    pr_ = [1 / (1 + math.exp(-(a[i] - d[j] + K_inter[i, j]))) for i in range(12)]
                else:                      # additive on the PROBABILITY scale: zero accuracy-scale interaction exactly
                    pr_ = [min(0.98, max(0.02, 0.55 + 0.12 * a[i] - 0.15 * d[j])) for i in range(12)]
                K[q] = {m: int(rs.rand() < pr_[i]) for i, m in enumerate(models)}
        return K
    K0p = make(np.zeros((12, 8)), scale="prob")
    K0 = make(np.zeros((12, 8)))
    inter = rs.normal(0, 1.2, (12, 8)); inter -= inter.mean(1, keepdims=True); inter -= inter.mean(0, keepdims=True)
    K1 = make(inter)
    def kb_for(K):
        return lambda cqs: {m: sum(K[q][m] for q in cqs) / len(cqs) for m in models}
    r0p = leg(cells, qsel, kb_for(K0p), models, "null-table-prob")
    r0 = leg(cells, qsel, kb_for(K0), models, "null-table-logit")
    r1 = leg(cells, qsel, kb_for(K1), models, "interaction-table")
    print("  planted NO interaction (probability-additive): model-only R %.4f, interaction-only R %.4f" % (r0p["model"]["R"], r0p["both"]["R"]))
    print("  planted NO LOGIT interaction (a +-1.5, d +-1.2):  model-only R %.4f, interaction-only R %.4f  <- the curvature effect" % (r0["model"]["R"], r0["both"]["R"]))
    print("  planted interaction:                            model-only R %.4f, interaction-only R %.4f" % (r1["model"]["R"], r1["both"]["R"]))
    assert r0p["model"]["R"] > 0.85 and abs(r0p["both"]["R"]) < 0.35, "prob-additive null: model-only high, interaction-only near 0"
    assert r0["both"]["R"] < r1["both"]["R"] - 0.3, "logit-additive null must read well below the planted interaction"
    assert r1["both"]["R"] > 0.85, "planted interaction should reproduce"
    # (2) centred profiles (the BT case): identity between the demeanings; C0 reads 0
    def centred_build(cqs):
        v = {m: sum(K1[q][m] for q in cqs) / len(cqs) for m in models}; mu = sum(v.values()) / len(v)
        return {m: x - mu for m, x in v.items()}
    rc = leg(cells, qsel, centred_build, models, "centred")
    print("  centred (BT-like) profiles: C0 max |anchor mean| %.1e; max |r_model - r_both| %.1e; balanced %s" % (rc["c0_worst"], rc["max_abs_r_diff"], rc["balanced"]))
    assert rc["c0_worst"] < 1e-12 and rc["max_abs_r_diff"] < 1e-12 and rc["balanced"]
    # (3) the null fit recovers a and d; the null reads
    k, n = key_table(cells, K0, models)
    ah, dh, it, clipped = fit_additive_logit(k, n)
    err = max(np.abs((ah - ah.mean()) - (a - a.mean())).max(), np.abs(dh - (d - d.mean())).max())
    print("  additive-logit MLE: %d sweeps, max |param error| %.3f (n=200 per cell), clipped %d" % (it, err, clipped))
    assert err < 0.35 and clipped == 0
    nd = null_tables(cells, K0, models, 4, [11, 12, 13, 14])
    print("  null reads on the null table (4 tables): model-only %s, interaction-only %s"
          % (["%.3f" % x[0] for x in nd["reads"]], ["%.3f" % x[1] for x in nd["reads"]]))
    assert all(x[1] < r1["both"]["R"] - 0.3 for x in nd["reads"])
    vd = variance_decomposition(k, n)
    print("  variance shares (null table) model / anchor / interaction: %.2f / %.2f / %.2f" % vd["shares"])
    assert vd["shares"][2] < 0.15
    # (4) jackknife shape and write-once
    iv = intervals(r1, "both"); assert iv["lo_re"] < iv["R"] < iv["hi_re"] and iv["lo_fx"] < iv["R"] < iv["hi_fx"]
    tmp = os.path.join(SCRATCH, "selftest_outcome.txt"); os.makedirs(SCRATCH, exist_ok=True)
    open(tmp, "w").write("x\n")
    try:
        write_once(tmp, "y"); raise AssertionError("write-once did not refuse")
    except SystemExit:
        pass
    os.remove(tmp)
    print("SELFTEST OK: prob-additive null reads ~0 interaction-only, logit-additive null shows the curvature floor, planted interaction reproduces; centred profiles give the C0")
    print("  identity; the additive-logit MLE recovers its parameters; jackknife intervals bracket the point; write-once refuses.")


def leaf_selftest():
    """--selftest --level leaf: synthetic cells only; nothing of record is opened. Covers the support rule, the refusal,
    the instrument's point floor and the flag-absent identity of the shared instrument."""
    print("=== --level leaf --selftest (synthetic cells; nothing of record is opened) ===")
    global LEVEL
    rs = np.random.RandomState(11)
    NM = 16                                   # 5 admissible cells x 16 models = 80 points per halving, above r_of's floor of 50
    models = ["m%02d" % i for i in range(NM)]
    # 7 synthetic leaves: 5 at or above the 120 floor, 2 below it (119 and 40) - the floor is inclusive at 120
    sizes = {"L1": 200, "L2": 160, "L3": 120, "L4": 130, "L5": 150, "L6": 119, "L7": 40}
    cells = {}; base = 0
    for c, n in sizes.items():
        cells[c] = list(range(base, base + n)); base += 1000
    adm, und = admissible_leaves(cells)
    print("  support rule on %d synthetic leaves (floor %d): admissible %s; UNDETERMINED-by-support %s"
          % (len(cells), LEAF_FLOOR, sorted(adm), sorted(und)))
    assert sorted(adm) == ["L1", "L2", "L3", "L4", "L5"], sorted(adm)     # 120 clears the floor, 119 does not
    assert und == {"L6": 119, "L7": 40} and sum(len(v) for v in adm.values()) + sum(und.values()) == sum(sizes.values())
    assert not (set(adm) & set(und)), "an inadmissible leaf must never be pooled into the cell set"
    assert support_refusal(adm, und) is None
    # the refusal: one admissible leaf is not a (model x cell) interaction
    adm1, und1 = admissible_leaves({c: cells[c] for c in ("L1", "L6", "L7")})
    msg = support_refusal(adm1, und1)
    print("  refusal at %d admissible leaf: %s" % (len(adm1), (msg or "(none)")[:110]))
    assert msg and msg.startswith("[SUPPORT] UNDETERMINED-by-support") and "no outcome file is written" in msg
    assert support_refusal({}, und1), "zero admissible leaves must refuse too"
    # the instrument on the admissible cells: the same leg() / intervals() the anchor path uses
    av = np.linspace(-1.5, 1.5, NM); dv = np.linspace(-1.0, 1.0, len(adm))
    inter = rs.normal(0, 1.2, (NM, len(adm))); inter -= inter.mean(1, keepdims=True); inter -= inter.mean(0, keepdims=True)
    def make(K_inter, additive_prob=False):
        K = {}
        for j, c in enumerate(adm):
            for q in adm[c]:
                p = ([min(0.98, max(0.02, 0.55 + 0.12 * av[i] - 0.15 * dv[j])) for i in range(NM)] if additive_prob else
                     [1 / (1 + math.exp(-(av[i] - dv[j] + K_inter[i, j]))) for i in range(NM)])
                K[q] = {m: int(rs.rand() < p[i]) for i, m in enumerate(models)}
        return K
    qsel = set(q for v in adm.values() for q in v)
    kb = lambda K: (lambda cqs: {m: sum(K[q][m] for q in cqs) / len(cqs) for m in models})
    K_flat = make(np.zeros((NM, len(adm))), additive_prob=True); K_int = make(inter)
    r_flat = leg(adm, qsel, kb(K_flat), models, "leaf-flat")
    r_int = leg(adm, qsel, kb(K_int), models, "leaf-interaction")
    print("  %d admissible leaves x %d models = %d points per halving (floor %d): additive-prob cells interaction-only R %.4f; "
          "planted interaction %.4f" % (len(adm), NM, len(adm) * NM, MIN_POINTS, r_flat["both"]["R"], r_int["both"]["R"]))
    assert len(adm) * NM >= MIN_POINTS
    assert r_int["both"]["R"] > r_flat["both"]["R"] + 0.3, (r_int["both"]["R"], r_flat["both"]["R"])
    iv = intervals(r_int, "both")
    assert iv["lo_re"] < iv["R"] < iv["hi_re"] and len(iv["loo_re"]) == len(adm), iv
    # the instrument's own point floor: 2 cells x 16 models = 32 < 50 -> nan, never a number
    two = {c: adm[c] for c in list(adm)[:2]}
    r_two = leg(two, set(q for v in two.values() for q in v), kb(K_int), models, "leaf-two")
    print("  2 admissible leaves x %d models = %d points per halving: R reads %s (must be nan: UNDETERMINED-by-support)"
          % (NM, 2 * NM, r_two["both"]["R"]))
    assert r_two["both"]["R"] != r_two["both"]["R"], "below r_of's point floor the instrument must read nan, not a number"
    # ... and that is exactly what points_refusal must catch BEFORE any outcome file is written
    rosters = [12, 46, 20, 12, 20]                            # the five legs' rosters (K12, K46, K20, J1, J2)
    msg2 = points_refusal(2, rosters)
    print("  points refusal at 2 admissible leaves x %d models: %s" % (min(rosters), (msg2 or "(none)")[:110]))
    assert msg2 and msg2.startswith("[SUPPORT] UNDETERMINED-by-support") and "no outcome file is written" in msg2
    assert points_refusal(5, rosters) is None, "5 cells x 12 models = 60 points clears the floor"
    assert points_refusal(4, rosters), "4 cells x 12 models = 48 points is below the floor and must refuse"
    assert points_refusal(2, [46]) is None, "the floor is on the roster actually asked for (2 x 46 = 92 clears it)"
    # FLAG-ABSENT IDENTITY: the shared instrument never reads LEVEL; the same inputs give identical results either way
    saved = LEVEL
    try:
        LEVEL = "anchor"; ra = leg(adm, qsel, kb(K_int), models, "identity")
        LEVEL = "leaf"; rb = leg(adm, qsel, kb(K_int), models, "identity")
    finally:
        LEVEL = saved
    same = all(ra[k]["R"] == rb[k]["R"] and ra[k]["loo_fixed"] == rb[k]["loo_fixed"] and ra[k]["loo_rehalved"] == rb[k]["loo_rehalved"]
               for k in ("model", "both"))
    print("  flag-absent identity: leg() under LEVEL='anchor' and LEVEL='leaf' agree on every R and every jackknife fold: %s" % same)
    assert same, "the --level flag must not touch the shared instrument"
    assert OUT != LEAF_OUT and os.path.basename(LEAF_OUT) == "profile_reliability_interaction_leaf_outcome.txt"
    print("LEAF SELFTEST OK: the 120 floor admits 120 and refuses 119, inadmissible leaves are never pooled, one admissible leaf refuses,")
    print("  the planted (model x cell) interaction is recovered, the point floor reads nan, and the flag does not touch the instrument.")


def leaf_main(a):
    """--level leaf: the UNREGISTERED leaf cell set. Writes LEAF_OUT (write-once) and NEVER OUT."""
    import pool_guard
    L = []
    L.append("pool of record: %s" % pool_guard.assert_pool_of_record(POOL))
    L.append("=== PROFILE-RELIABILITY-INTERACTION --level leaf: the model- AND CELL-demeaned split-half R on the frozen tree's LEAF cells ===")
    L.append("  UNREGISTERED INSTRUMENT (code added 2026-09-23): the test is NOT registered and needs the author's word before any number")
    L.append("  here enters the record. Same instrument, same seeds (Random(7), 40 halvings), same two-way demeaning, same jackknife and")
    L.append("  halving SD, same logit-additive null as the registered anchor readout; only the CELL SET changes. Zero calls; caches mode=ro.")
    L.append("  %s | outcome %s (write-once; the anchor outcome is never touched)"
             % ("DRY RUN, no R is printed" if a.dry_run else "RUN", os.path.basename(LEAF_OUT)))
    L.append("")
    L.append("--- DATA CHECK (the object, before any cell is read) ---")
    D = load_record(L.append, level="leaf")
    refusal = (support_refusal(D["usable"], D["undetermined"])
               or points_refusal(len(D["usable"]), [len(models) for _, _, _, models in D["legs"]]))
    if refusal:
        print("\n".join(L), flush=True)
        raise SystemExit(refusal)
    if a.dry_run:
        L.append("  dry run: the legs, the intervals, the null and the decomposition run under --run only; no R printed.")
        print("\n".join(L)); return
    if os.path.exists(LEAF_OUT):
        raise SystemExit("[WRITE-ONCE] %s exists; not overwritten" % LEAF_OUT)
    print("\n".join(L), flush=True)
    res, summ, nulls = leaf_readout(D, L)
    os.makedirs(SCRATCH, exist_ok=True)
    json.dump({t: {k: v for k, v in r.items() if k not in ("per_rep",)} for t, r in res.items()},
              open(os.path.join(SCRATCH, "profile_reliability_interaction_leaf_legs.json"), "w"), indent=1, default=str)
    txt = "\n".join(L); print(txt)
    write_once(LEAF_OUT, txt)
    print("written", LEAF_OUT)


def write_once(path, txt):
    if os.path.exists(path):
        raise SystemExit("[WRITE-ONCE] %s exists; not overwritten" % path)
    open(path, "w", encoding="utf-8").write(txt + "\n")


# ----------------------------------------------------------------------------------------------- main
def main():
    global LEVEL
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--level", choices=["anchor", "leaf"], default="anchor",
                    help="cell set: the 14 depth-1 anchors (default, the registered readout) or the frozen tree's LEAVES "
                         "(UNREGISTERED, code only; support floor %d, refuses below %d admissible leaves)" % (LEAF_FLOOR, MIN_ADMISSIBLE))
    a = ap.parse_args()
    if sum(map(bool, (a.dry_run, a.selftest, a.run))) != 1:
        ap.error("exactly one of --dry-run, --selftest, --run")
    LEVEL = a.level
    if a.selftest:
        print("pool of record (NOT opened by --selftest): %s" % POOL)
        selftest()
        if LEVEL == "leaf": leaf_selftest()
        return
    if LEVEL == "leaf": return leaf_main(a)
    import pool_guard
    L = []
    L.append("pool of record: %s" % pool_guard.assert_pool_of_record(POOL))
    L.append("=== PROFILE-RELIABILITY-INTERACTION: the model- AND anchor-demeaned split-half R on the 14 MMLU-Pro anchors, key and judge ===")
    L.append("  registered 2026-09-18 (commit 954e829); zero calls; caches mode=ro; %s" % ("DRY RUN, no R is printed" if a.dry_run else "RUN"))
    L.append("")
    L.append("--- DATA CHECK (the object, before any stratum is read) ---")
    D = load_record(L.append)
    if a.dry_run:
        # C0 on ONE halving per judge leg (28 fits per leg); no R
        for tag, desc, build, models in D["legs"]:
            if tag not in ("J1", "J2"): continue
            per_rep = halvings_fixed(D["usable"], D["qsel"], build, models, random.Random(SEED), reps=1)
            worst, first = c0_check(per_rep)
            L.append("  C0 on one halving, %s: max |per-anchor mean of a half-profile| = %.3e; balanced %s" % (tag, worst, balanced(per_rep, models)))
            L.append("      " + ", ".join("%s (%+.1e, %+.1e)" % (c, v[0], v[1]) for c, v in first.items()))
        L.append("  dry run: the legs, the intervals, the null and the decomposition run under --run only; no R printed.")
        txt = "\n".join(L); print(txt); return
    if os.path.exists(OUT):
        raise SystemExit("[WRITE-ONCE] %s exists; not overwritten" % OUT)
    print("\n".join(L), flush=True)
    res, centred, summ, nulls, gate_ok = readout(D, L)
    verdicts(D, L, res, centred, summ, nulls, gate_ok)
    os.makedirs(SCRATCH, exist_ok=True)
    json.dump({t: {k: v for k, v in r.items() if k not in ("per_rep",)} for t, r in res.items()},
              open(os.path.join(SCRATCH, "profile_reliability_interaction_legs.json"), "w"), indent=1, default=str)
    txt = "\n".join(L); print(txt)
    write_once(OUT, txt)
    print("written", OUT)


if __name__ == "__main__":
    main()
