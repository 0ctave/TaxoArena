"""PROFILE-DEVIATION-CERT - registered 2026-09-17 (before any code or call), docs/judge_v2_program.md
L5334-L5401, commit 62c4084; plan docs/agents/plans/2026-09-17_continual_capability_profile_leads.md A1;
lens docs/agents/leads/2026-09-17_arena_profile.md L1. ZERO judge calls.

  python tools/analysis/profile_deviation_cert.py --dry-run      # data object only, NO outcome number
  python tools/analysis/profile_deviation_cert.py --selftest     # synthetic verdicts, planted deviations, null rate
  python tools/analysis/profile_deviation_cert.py --run          # the readout of record, once, from complete caches
     [--B 2000] [--seed 42] [--selftest-reps 10] [--selftest-B 400]

THE REGISTRATION (quoted; the last bracket in the programme file wins over this copy):
  Question. Every published profile row is theta_ac = theta_a + delta_ac on the anchor's own board, and the record
  has never published delta_ac with a certificate of its own ... Claim under test: delta_ac carries certifiable
  content beyond theta_m, i.e. for some (model, anchor) cells the record may say "m is certified above / below its
  own standing in anchor c". ... The cell is the ANCHOR: this registration is at the anchor and nowhere below it.
  Hygiene. Caches opened mode=ro and row counts pinned before any fit: MISTRAL-MERGED = stack_v2_promptv2_x12all.db
  9,142 (2,811 judged q) + stack_v2_promptv2_x20.db 12,394 (2,646 q) = 21,536 verdicts, 20 models, the board of
  record; x20 is never read alone. Pool p2dca21ab5f4ef3ae, verified by `pool_guard.py --pool` as the first printed
  line; only JUDGED questions enter (per anchor 119-304). Anchors = the 14 bareq512_s42 anchors the boards group by
  (r512.primary_routing / r512.anchor_fn; the caches' `anchor` column agrees on 0 mismatches). Key =
  eval_results.is_correct as systematic_budget.build reads it (46-model roster, Meta-Llama-3-70B-Instruct excluded,
  join by the OPTIONS key, never question_text); all 20 contestants are keyed (BUDGET-TRANSFER). No train-side
  material; nothing induced; no leaf, no sub-anchor row. The Jeffreys prior (rj.mm_fit DEFAULT_PRIOR_STRENGTH 0.5)
  is printed with its per-anchor shrinkage (1.23-1.82x, K-RECONCILE checker (3)); routing attenuation (~20%
  proportional at 19%, ROUTING-ATTENUATION) is a caveat on the MAGNITUDE of every deviation, not on its sign, and
  is printed once.
  Instrument. (a) Draw matrix from x20_merged.merged_rows(): per resample, questions resampled WITHIN each anchor
  (question-clustered, B >= 2,000, seed 42 printed; resamples cached to disk so the reviewer recomputes from the
  same draws), and on the SAME resample both the per-anchor board (jf.board_from -> rj.mm_fit, prior 0.5) and the
  pooled board over all judged questions; delta_ac = theta_ac(per-anchor fit) - theta_m(pooled fit) per draw;
  point = the fit on the unresampled data; SD_ac = the draw SD. (b) Critical value: the MAXT-MULTIPLICITY
  construction applied to the deviation object, q_cell(dev) = the 95th percentile over draws of max over the
  anchor's 20 models of |delta*_ac - delta_hat_ac| / SD_ac (raw-z reading; the widened-q reading printed beside;
  the hybrid reading is NOT used, MAXT-MULTIPLICITY checker (1)); MAXT's pair-level merged per-anchor q (3.43-3.80)
  printed beside for scale. A deviation is CERTIFIED iff |delta_ac| / SD_ac >= q_cell(dev); the marginal 1.96 count
  is printed as a second column and is not the count of record. (c) Key comparator on the same cells: dev_key_mc =
  acc_mc - acc_m over the anchor's judged questions vs all 2,811 judged questions, question-bootstrap SD from the
  same resamples, certified iff |dev_key| / SD >= q_cell(dev, key) computed the same way on the key resamples;
  ESTABLISHED iff the exact two-sided Fisher test on the model's in-anchor vs out-of-anchor correctness (2 x 2 over
  judged questions, integer arithmetic) gives p < 0.05. (d) Variance share = var_cells(delta_ac) /
  (var_cells(delta_ac) + var_models(theta_m)) over the 280 cells, key and judge, with the mean bootstrap variance of
  delta subtracted and printed beside (sampling share). (e) wrong(established): judge-certified deviations whose
  key deviation has the OPPOSITE sign and is established under (c).
  Readouts and criteria (each scored HELD / FAILED; denominators named):
   (C1) key-certified share = certified key cells / 280 (20 models x 14 anchors), per anchor and overall.
   (C2) judge-certified share = certified judge cells / 280, per anchor and overall; the certified list per model,
        each row carrying the anchor's PROFILE-INTERVAL-ALL C2 class (PASS Physics, Math; PASS-WITH-INTERVAL Law,
        Psychology, Business, Chemistry, Philosophy, Other, History; FAIL Engineering, Biology, Computer science,
        Economics, Health). Rows in FAIL anchors are published PREDICTIVE-ONLY whatever the deviation test says
        (counted in C2, never a claim).
   (C3) wrong(established) among judge-certified deviations (e), with the denominator = judge-certified count.
   (C4) variance share of delta vs theta, key and judge, with the sampling share beside.
   (C5) agreement of the certified sets: of the judge-certified cells, the share whose key deviation has the same
        sign (descriptive; the sign agreement of ALL 280 cells printed beside as the null-ish baseline).
  Predictions (the plan's, recorded blind): key-certified < 30% of the 280 cells; judge-certified < 15%; the
  judge-certified cells concentrated in Physics / Math / Law (scored as >= 50% of judge-certified cells in those
  three anchors); wrong-key-sign 0-2 (established). Registrar's blind addition: if judge-certified = 0 the claim
  fails on SUPPORT, not through the falsifier, and the profile carries no deviation sentence at all.
  Falsifier. Judge-certified deviations with the wrong key sign (established) > 5% of those certified. ...
  It does NOT overturn the key-built rows (C1 stands on the key alone).
  Cost and consequence. 0 calls; ~1 CPU-hour (B >= 2,000 x 15 fits); writes experiment_results/x12_crossdomain/
  profile_deviation_cert.txt (+ profile_deviation_cert_cells.csv, one row per (model, anchor) with delta, SD,
  q_cell, certified, key deviation, Fisher p, class) once, from complete caches only.

IMPLEMENTATION, and the READINGS CHOSEN where the registration is silent (each stated here before the run):
  * Rows. The two caches are read with the SAME SQL as x20_merged.merged_rows() (invalid rows dropped) but opened
    `file:...?mode=ro` here, because merged_rows() reaches the x12 cache through stack_judge.open_cache(), which
    opens it read-write (CREATE TABLE IF NOT EXISTS + commit). The row lists are asserted identical in count to the
    pins (9,142 / 12,394 / 21,536) and the x12 cache's own `anchor` column is compared to the tree anchor (0
    mismatches asserted). Every judged question must route to one of the 14 anchors (asserted): the pooled board
    over "all judged questions" is then exactly the union of the 14 per-anchor resamples, which is what "on the
    SAME resample" requires.
  * Draws. One random.Random(seed) consumed in the record's order (anchors sorted, B draws per anchor, each draw
    `rng.randrange(n)` n times - the identical consumption of systematic_budget / budget_transfer /
    maxt_multiplicity); draw b of the pooled board = the union of draw b of every anchor. The multiplicity matrices
    and the theta draws are written to profile_deviation_cert_draws.npz beside the outcome file.
  * Fit. The record's fit is jf.board_from -> rj.mm_fit (a 0.5-win pseudo-match on each side of every OBSERVED
    pair, MM iterated to 1e-12 on the strength scale, mean-centred log). A numpy batched copy of the same MM
    (`fit_batch`) does the 30,000+ fits; it is asserted against rj.mm_fit through jf.board_from on every point fit
    and on the first draws of every board (max |dtheta| < 1e-8) before any number is read; the MM fixed point is
    unique, so the two iterate to the same theta.
  * SD and quantile. SD_ac = draw SD with ddof = 1 (MAXT's s); the 95th percentile is numpy's default linear
    percentile (MAXT's). The max-t is centred on the point delta_hat (MAXT checker (5)).
  * Widened-q reading (beside; NOT the certificate). The agreement widener is a PAIR term
    tau_ab = exp(B0 + B1 * agree_ab) (budget_transfer B0 = -3.2326, B1 = 3.3133, agreement over the anchor's judged
    questions with both predictions). A (model, anchor) deviation has no pair, so the reading taken is
    tau_mc = RMS over the model's 19 in-anchor pairs of tau_ab; the widened statistic |delta| / sqrt(SD^2 + tau^2)
    is held to q_w computed on the SAME widened scale (95th pct of max_m |delta* - delta_hat| / sqrt(SD^2 + tau^2)).
    The hybrid (widened statistic against the raw-scale q) is not computed anywhere.
  * Fisher. Exact two-sided Fisher on [[in correct, in wrong], [out correct, out wrong]] over the model's keyed
    judged questions: hypergeometric point probabilities as exact rationals (fractions.Fraction, math.comb), p =
    the sum of every table's probability <= the observed table's (no tolerance); cross-checked against
    scipy.stats.fisher_exact in --selftest.
  * Variance share. Sample variances (ddof = 1) over the 280 cells (delta) and over the 20 models (theta_m, resp.
    acc_m). "Sampling share" = mean over cells of SD_ac^2 divided by var_cells(delta); the noise-subtracted share
    uses var_cells(delta) - mean(SD_ac^2) in both numerator and denominator.
  * Shrinkage. Per anchor, SD across models of the point theta from an UNPENALISED MM fit (prior 0, same
    iteration cap) divided by the SD under the 0.5 prior - K-RECONCILE checker (3)'s statistic, here on the
    20-model merged board (its 1.23-1.82x was the 12-model x12 board and is printed beside).
  * Scoring. C1 is HELD iff the plan's prediction holds (key-certified < 30%); C2 iff judge-certified < 15% AND
    judge-certified > 0 (the registrar's support clause); C3 iff wrong(established) <= 5% of the judge-certified
    (the falsifier not triggered) AND judge-certified > 0; C4 and C5 carry no registered threshold and are scored
    DELIVERED. The concentration prediction is UNDETERMINED at judge-certified = 0 (0 / 0).
  * READING OF RECORD = the PRIOR-MATCHED deviation (programme bracket [CORRECTED 2026-09-18 by REVIEW], commit
    1534a4a): the per-anchor fit carries ~190 pseudo-matches against 695-2,881 real ones while the pooled fit
    carries 190 against 21,536, so under the exact null (every anchor shares theta_m) the registered
    delta_ac = theta_ac(prior 0.5) - theta_m(pooled, prior 0.5) is centred on ~ -(1 - k_pool/k_anchor) * theta_m,
    not on zero (slope -0.2185 on the record; null family rate 92.1% on the real schedule, 80.7% synthetic). The
    object of (b), (d), (e), C2-C5, P2-P4 and the falsifier is therefore
        delta'_ac = theta_ac(per-anchor MM, prior 0.5, the published row, unchanged)
                  - theta'_m,c(pooled MM with the prior scaled by pooled matches / anchor matches),
    so both fits carry the same prior-to-data weight (the MM fixed point is invariant to a common scaling of wins
    and prior); SD_ac, q_cell(dev) from the same within-anchor resamples and the same max-t. The registered
    reading is computed in full and printed beside every count as "registered; biased by construction (null
    family rate 80.7-92.1% at nominal 5%)" - reg_* columns in the CSV - and is NOT scored. (c) and C1 (the key
    comparator) are unchanged. The widened-q reading beside is taken on delta'.
  * Key denominator of every key number: the model's KEYED judged questions in the anchor (in) and in the other
    13 anchors (out); acc_m over all its keyed judged questions. wrong(established) = opposite key sign AND
    Fisher p < 0.05 (the established count carried beside every wrong count).
  * --run refuses to overwrite an existing outcome file (written once); --dry-run prints the data object and no
    fitted quantity; no network, no LLM calls.
  * SELFTEST (synthetic data; nothing of record read): asserts the mechanics (exact Fisher = scipy; batched MM =
    rj.mm_fit; key planted deviations recovered; key null rate within the binomial bound) and the null family rate
    of the PRIOR-MATCHED reading (<= the binomial 97.5% bound, 8.6% at 140 families); reports - does not fail on -
    the planted recovery per band of |theta_m| at |delta| = 1.2 and 1.5 (the prior-matched reading attenuates
    |delta'| for |theta_m| > 1.5; a certified SIGN is preserved, a magnitude is not published). The registered
    reading's null rate and recoveries are printed beside for the record of the bias (2026-09-18 finding: 80.7%
    family rate; its recoveries include artefact-inflated cells).
  * C2 is scored FAILED at judge-certified = 0 (the registrar's support clause: the claim fails on SUPPORT and the
    profile carries no deviation sentence) while P2 "< 15%" scores HELD at 0; both are stated in the outcome text.
"""
import os, sys, math, random, json, csv, time, argparse, sqlite3
from collections import defaultdict
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import pool_guard
import rejudge_grok as rj
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import budget_transfer as bt

POOL = pool_guard.MMLU_PRO_POOL          # p2dca21ab5f4ef3ae
TREE = "bareq512_s42"
OUT_DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
OUT = os.path.join(OUT_DIR, "profile_deviation_cert.txt")
CELLS = os.path.join(OUT_DIR, "profile_deviation_cert_cells.csv")
DRAWS = os.path.join(OUT_DIR, "profile_deviation_cert_draws.npz")
MAXT_TXT = os.path.join(OUT_DIR, "maxt_multiplicity.txt")
PIA_TXT = os.path.join(OUT_DIR, "profile_interval_all.txt")
B_DEFAULT = 2000
SEED_DEFAULT = 42
FWER = 0.05
ALPHA = 0.05
Z_MARGINAL = 1.959964
PRIOR = rj.PRIOR
EXCLUDE = "Meta-Llama-3-70B-Instruct"
B0, B1 = bt.B0, bt.B1
PIN = dict(n12=9142, n20=12394, n=21536, models=20, q=2811, q20=2646, anchors=14, cells=280, qmin=119, qmax=304)
CLASS = {"Physics": "PASS", "Math": "PASS",
         "Law": "PASS-WITH-INTERVAL", "Psychology": "PASS-WITH-INTERVAL", "Business": "PASS-WITH-INTERVAL",
         "Chemistry": "PASS-WITH-INTERVAL", "Philosophy": "PASS-WITH-INTERVAL", "Other": "PASS-WITH-INTERVAL",
         "History": "PASS-WITH-INTERVAL",
         "Engineering": "FAIL", "Biology": "FAIL", "Computer science": "FAIL", "Economics": "FAIL", "Health": "FAIL"}
CONCENTRATION = ("Physics", "Math", "Law")
MAXT_MERGED_Q = {"Biology": 3.437, "Business": 3.639, "Chemistry": 3.625, "Computer science": 3.531, "Economics": 3.449,
                 "Engineering": 3.800, "Health": 3.502, "History": 3.519, "Law": 3.547, "Math": 3.550, "Other": 3.545,
                 "Philosophy": 3.693, "Physics": 3.431, "Psychology": 3.568}   # maxt_multiplicity.txt, merged rows


def log(msg):
    print("[pdc %s] %s" % (time.strftime("%H:%M:%S"), msg), file=sys.stderr, flush=True)


def score(w, a):
    return 0.5 if w == "TIE" else (1.0 if w == a else 0.0)


# ----------------------------------------------------------------------------------------------------------
# data of record (read-only)
# ----------------------------------------------------------------------------------------------------------
def load_record():
    """Mirror of x20_merged.merged_rows() with both caches opened mode=ro; returns the data object."""
    assert abs(PRIOR - 0.5) < 1e-12, "rj.PRIOR is %r, the registration pins 0.5" % PRIOR
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    x12_path = sj.cache_path()
    con12 = sqlite3.connect("file:%s?mode=ro" % x12_path.replace("\\", "/"), uri=True)
    r12 = [r for r in con12.execute("SELECT model_a, model_b, qid, winner, invalid, anchor FROM verdicts") if not r[4]]
    con20 = sqlite3.connect("file:%s?mode=ro" % bt.X20.replace("\\", "/"), uri=True)
    r20 = [r for r in con20.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    con12.close(); con20.close()
    if len(r12) != PIN["n12"] or len(r20) != PIN["n20"]:
        raise SystemExit("[PIN] x12 %d (pinned %d), x20 %d (pinned %d): caches are not the board of record"
                         % (len(r12), PIN["n12"], len(r20), PIN["n20"]))
    rows = [(a, b, q, w) for a, b, q, w, _iv, _anc in r12] + [(a, b, q, w) for a, b, q, w, _iv in r20]
    models = sorted({r[0] for r in rows} | {r[1] for r in rows})
    assert EXCLUDE not in models, EXCLUDE
    if len(models) != PIN["models"] or len(rows) != PIN["n"]:
        raise SystemExit("[PIN] %d models / %d rows, pinned %d / %d" % (len(models), len(rows), PIN["models"], PIN["n"]))
    qs_all = sorted({r[2] for r in rows}); q20 = {r[2] for r in r20}
    if len(qs_all) != PIN["q"] or len(q20) != PIN["q20"]:
        raise SystemExit("[PIN] judged q %d (pinned %d), x20 q %d (pinned %d)" % (len(qs_all), PIN["q"], len(q20), PIN["q20"]))

    route = r512.primary_routing(TREE)
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anchor_of = r512.anchor_fn(nodes)
    unrouted = [q for q in qs_all if q not in route]
    if unrouted:
        raise SystemExit("[DATA] %d judged questions have no bareq512_s42 primary routing; the pooled board would not be "
                         "the union of the per-anchor resamples" % len(unrouted))
    anc_of_q = {q: anchor_of(route[q]) for q in qs_all}
    mismatch = sum(1 for a, b, q, w, _iv, anc in r12 if anc != anc_of_q[q])
    anchors = sorted(set(anc_of_q.values()))
    if len(anchors) != PIN["anchors"]:
        raise SystemExit("[PIN] %d anchors, pinned %d" % (len(anchors), PIN["anchors"]))

    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB.replace("\\", "/"), uri=True)
    K = defaultdict(dict); P = defaultdict(dict)
    mset = set(models)
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in mset:
            K[q][m] = int(c or 0); P[q][m] = (pr or "").strip().upper()[:1]
    ev.close()
    by = defaultdict(list)
    for r in rows:
        by[anc_of_q[r[2]]].append(r)
    qs = {anc: sorted({r[2] for r in by[anc]}) for anc in anchors}
    nq = [len(qs[a]) for a in anchors]
    if min(nq) != PIN["qmin"] or max(nq) != PIN["qmax"]:
        raise SystemExit("[PIN] per-anchor judged q %d-%d, pinned %d-%d" % (min(nq), max(nq), PIN["qmin"], PIN["qmax"]))
    return dict(models=models, anchors=anchors, rows=by, qs=qs, K=dict(K), P=dict(P), n12=len(r12), n20=len(r20),
                cache_anchor_mismatch=mismatch, x12_path=x12_path, x20_path=bt.X20, eval_path=rj.EVAL_DB, nq_all=len(qs_all))


def tensors(data):
    """Per anchor: A (n_q x M x M) fractional wins per question; Kmat (n_q x M, nan = no key); has (n_q x M)."""
    models, anchors = data["models"], data["anchors"]; mi = {m: i for i, m in enumerate(models)}; M = len(models)
    T = {}
    for anc in anchors:
        qs = data["qs"][anc]; qi = {q: i for i, q in enumerate(qs)}
        A = np.zeros((len(qs), M, M))
        for a, b, q, w in data["rows"][anc]:
            s = score(w, a); A[qi[q], mi[a], mi[b]] += s; A[qi[q], mi[b], mi[a]] += 1.0 - s
        Km = np.full((len(qs), M), np.nan)
        for i, q in enumerate(qs):
            for m, c in data["K"].get(q, {}).items():
                Km[i, mi[m]] = c
        T[anc] = dict(A=A, K=Km, has=~np.isnan(Km), n=len(qs), nrows=len(data["rows"][anc]))
    return T


# ----------------------------------------------------------------------------------------------------------
# the fit: numpy batched copy of rj.mm_fit, asserted against it
# ----------------------------------------------------------------------------------------------------------
def fit_batch(Wm, prior=PRIOR, iters=2000, tol=1e-12):
    """Wm: (B, M, M) fractional wins of i over j. Line-for-line the MM of rj.mm_fit: W_i = wins_i + prior per
    observed pair; N_ij = n_ij + 2 prior per observed pair; p_i <- W_i / sum_j N_ij / (p_i + p_j); mean-normalised;
    stop when max |p_new - p| < tol; theta = log p, mean-centred."""
    Bn, M, _ = Wm.shape
    Nreal = Wm + np.transpose(Wm, (0, 2, 1))
    O = Nreal > 0
    W = Wm.sum(2) + prior * O.sum(2)
    N = Nreal + 2.0 * prior * O
    p = np.ones((Bn, M))
    converged = False
    for _ in range(iters):
        den = (N / (p[:, :, None] + p[:, None, :])).sum(2)
        new = np.where(den > 0, W / np.where(den > 0, den, 1.0), p)
        new = new / new.mean(1, keepdims=True)
        if np.max(np.abs(new - p)) < tol:
            p = new; converged = True; break
        p = new
    th = np.log(np.maximum(p, 1e-300))
    return th - th.mean(1, keepdims=True), converged


def rows_from_counts(rows4, qs, counts):
    byq = defaultdict(list)
    for r in rows4:
        byq[r[2]].append(r)
    return [r for q, c in zip(qs, counts) for _ in range(int(c)) for r in byq[q]]


def assert_fit_equivalence(data, T, counts, th_draw, th_hat, n_draws=2, tol=1e-8):
    """rj.mm_fit through jf.board_from on the point fit and the first draws of every board, vs the batched fit."""
    models, anchors = data["models"], data["anchors"]
    worst = 0.0; checks = 0
    for anc in anchors:
        rows4 = data["rows"][anc]; qs = data["qs"][anc]
        ref = jf.board_from([(a, b, score(w, a), 1.0) for a, b, _, w in rows4], models)
        worst = max(worst, max(abs(ref[m] - th_hat[anc][i]) for i, m in enumerate(models))); checks += 1
        for b in range(n_draws):
            sub = rows_from_counts(rows4, qs, counts[anc][b])
            ref = jf.board_from([(a, b_, score(w, a), 1.0) for a, b_, _, w in sub], models)
            worst = max(worst, max(abs(ref[m] - th_draw[anc][b, i]) for i, m in enumerate(models))); checks += 1
    allrows = [r for anc in anchors for r in data["rows"][anc]]
    ref = jf.board_from([(a, b, score(w, a), 1.0) for a, b, _, w in allrows], models)
    worst = max(worst, max(abs(ref[m] - th_hat["POOLED"][i]) for i, m in enumerate(models))); checks += 1
    for b in range(n_draws):
        sub = [r for anc in anchors for r in rows_from_counts(data["rows"][anc], data["qs"][anc], counts[anc][b])]
        ref = jf.board_from([(a, b_, score(w, a), 1.0) for a, b_, _, w in sub], models)
        worst = max(worst, max(abs(ref[m] - th_draw["POOLED"][b, i]) for i, m in enumerate(models))); checks += 1
    if not worst < tol:
        raise SystemExit("[FIT] batched MM differs from rj.mm_fit by %.2e on %d fits (tolerance %.0e)" % (worst, checks, tol))
    return worst, checks


# ----------------------------------------------------------------------------------------------------------
# draws, deviations, certificate
# ----------------------------------------------------------------------------------------------------------
def draw_counts(data, B, seed):
    """One random.Random(seed), anchors in sorted order, B draws each, n randrange(n) calls per draw."""
    rng = random.Random(seed)
    counts = {}
    for anc in data["anchors"]:
        n = len(data["qs"][anc])
        C = np.zeros((B, n), dtype=np.uint16)
        for b in range(B):
            pick = [rng.randrange(n) for _ in range(n)]
            C[b] = np.bincount(pick, minlength=n)
        counts[anc] = C
    return counts


def fisher_exact_two_sided(a, b, c, d):
    """Exact two-sided Fisher on [[a, b], [c, d]] with integer arithmetic: p = sum of hypergeometric probabilities
    of every table with the same margins whose probability is <= the observed table's."""
    n = a + b + c + d
    if n == 0:
        return 1.0
    r1 = a + b; c1 = a + c
    lo = max(0, r1 + c1 - n); hi = min(r1, c1)
    denom = math.comb(n, c1)
    obs = Fraction(math.comb(r1, a) * math.comb(n - r1, c1 - a), denom)
    p = Fraction(0)
    for k in range(lo, hi + 1):
        pk = Fraction(math.comb(r1, k) * math.comb(n - r1, c1 - k), denom)
        if pk <= obs:
            p += pk
    return min(1.0, float(p))


def tau_widener(data, T):
    """tau_mc = RMS over the model's in-anchor pairs of exp(B0 + B1 * agree_ab), agreement over the anchor's judged
    questions where both models have a prediction."""
    models, anchors, P = data["models"], data["anchors"], data["P"]; M = len(models)
    tau = np.zeros((len(anchors), M))
    for ci, anc in enumerate(anchors):
        qs = data["qs"][anc]
        pred = np.full((len(qs), M), "", dtype=object)
        for i, q in enumerate(qs):
            for j, m in enumerate(models):
                pred[i, j] = P.get(q, {}).get(m, "")
        for i in range(M):
            t2 = []
            for j in range(M):
                if i == j:
                    continue
                both = [(pred[k, i], pred[k, j]) for k in range(len(qs)) if pred[k, i] and pred[k, j]]
                agree = (sum(1 for x, y in both if x == y) / len(both)) if both else 0.0
                t2.append(math.exp(B0 + B1 * agree) ** 2)
            tau[ci, i] = math.sqrt(sum(t2) / len(t2))
    return tau


def maxt_block(d_draw, d_hat, scale=None):
    """SD (ddof 1), z, per-anchor 95th pct of max_m |d* - d_hat| / SD, certified, marginal. scale = optional
    (nA, M) widened SD replacing SD in both the statistic and the quantile (scale-consistent)."""
    SD = d_draw.std(1, ddof=1)
    S = SD if scale is None else scale
    z = np.abs(d_hat) / S
    Tm = (np.abs(d_draw - d_hat[:, None, :]) / S[:, None, :]).max(2)
    q = np.percentile(Tm, 100 * (1 - FWER), axis=1)
    return dict(SD=SD, z=z, q=q, cert=z >= q[:, None], marg=z >= Z_MARGINAL)


def certificate(data, T, B, seed, counts=None, want_widener=True, want_shrink=True, fit_check=True):
    models, anchors = data["models"], data["anchors"]; M = len(models); nA = len(anchors)
    t0 = time.time()
    if counts is None:
        log("drawing B = %d resamples, seed %d" % (B, seed)); counts = draw_counts(data, B, seed)
    th_draw = {}; th_hat = {}; Wm_pool_draw = None; Wm_pool_hat = None; conv = {}
    keynum_draw = np.zeros((B, M)); keyden_draw = np.zeros((B, M)); keynum_hat = np.zeros(M); keyden_hat = np.zeros(M)
    acc_c_draw = np.zeros((nA, B, M)); acc_c_hat = np.zeros((nA, M))
    for ci, anc in enumerate(anchors):
        A = T[anc]["A"]; C = counts[anc].astype(float)
        Wd = np.einsum("bq,qij->bij", C, A); Wh = A.sum(0)[None]
        th_draw[anc], c1 = fit_batch(Wd); th_hat[anc], c2 = fit_batch(Wh); th_hat[anc] = th_hat[anc][0]; conv[anc] = c1 and c2
        Wm_pool_draw = Wd if Wm_pool_draw is None else Wm_pool_draw + Wd
        Wm_pool_hat = Wh if Wm_pool_hat is None else Wm_pool_hat + Wh
        K0 = np.nan_to_num(T[anc]["K"]); H = T[anc]["has"].astype(float)
        num = C @ K0; den = C @ H
        acc_c_draw[ci] = num / np.where(den > 0, den, np.nan); acc_c_hat[ci] = K0.sum(0) / np.where(H.sum(0) > 0, H.sum(0), np.nan)
        keynum_draw += num; keyden_draw += den; keynum_hat += K0.sum(0); keyden_hat += H.sum(0)
        log("  %-18s fitted (%.0fs)" % (anc, time.time() - t0))
    th_draw["POOLED"], c1 = fit_batch(Wm_pool_draw); th_hat["POOLED"], c2 = fit_batch(Wm_pool_hat); th_hat["POOLED"] = th_hat["POOLED"][0]
    conv["POOLED"] = c1 and c2
    log("  POOLED fitted (%.0fs)" % (time.time() - t0))
    fit_dev = None
    if fit_check:
        fit_dev = assert_fit_equivalence(data, T, counts, th_draw, th_hat)
        log("  fit equivalence vs rj.mm_fit: max |dtheta| %.2e over %d fits" % fit_dev)

    R = dict(models=models, anchors=anchors, B=B, seed=seed, counts=counts, th_draw=th_draw, th_hat=th_hat, conv=conv, fit_dev=fit_dev)
    # ---- the READING OF RECORD: prior-matched delta' = theta_ac - theta'_m,c (pooled MM, prior x pooled/anchor matches)
    n_pool = float(sum(T[anc]["nrows"] for anc in anchors))
    pm_hat = np.zeros((nA, M)); pm_draw = np.zeros((nA, B, M)); pm_prior = np.zeros(nA); pm_conv = {}
    for ci, anc in enumerate(anchors):
        pr = PRIOR * n_pool / T[anc]["nrows"]; pm_prior[ci] = pr
        tp_d, c1 = fit_batch(Wm_pool_draw, prior=pr); tp_h, c2 = fit_batch(Wm_pool_hat, prior=pr); pm_conv[anc] = c1 and c2
        pm_draw[ci] = tp_d; pm_hat[ci] = tp_h[0]
    delta_draw = np.stack([th_draw[anc] for anc in anchors]) - pm_draw
    delta_hat = np.stack([th_hat[anc] for anc in anchors]) - pm_hat
    R.update(delta_draw=delta_draw, delta_hat=delta_hat, pm_theta_hat=pm_hat, pm_prior=pm_prior, pm_conv=pm_conv)
    R.update(maxt_block(delta_draw, delta_hat))
    log("  prior-matched reading fitted (%.0fs)" % (time.time() - t0))
    # ---- the REGISTERED reading, kept beside (biased by construction; not scored)
    reg_draw = np.stack([th_draw[anc] - th_draw["POOLED"] for anc in anchors])
    reg_hat = np.stack([th_hat[anc] - th_hat["POOLED"] for anc in anchors])
    rb = maxt_block(reg_draw, reg_hat)
    R.update(reg_delta_draw=reg_draw, reg_delta_hat=reg_hat, reg_SD=rb["SD"], reg_z=rb["z"], reg_q=rb["q"], reg_cert=rb["cert"], reg_marg=rb["marg"])
    # (c) key deviations on the same resamples (unchanged by the bracket)
    acc_m_draw = keynum_draw / keyden_draw; acc_m_hat = keynum_hat / keyden_hat
    dk_draw = acc_c_draw - acc_m_draw[None]; dk_hat = acc_c_hat - acc_m_hat[None]
    kb = maxt_block(dk_draw, dk_hat)
    fisher = np.ones((nA, M)); table = np.zeros((nA, M, 4), dtype=int)
    for ci, anc in enumerate(anchors):
        K0 = np.nan_to_num(T[anc]["K"]); H = T[anc]["has"]
        for i in range(M):
            a_ = int(K0[:, i].sum()); n_in = int(H[:, i].sum())
            a_out = int(keynum_hat[i]) - a_; n_out = int(keyden_hat[i]) - n_in
            table[ci, i] = (a_, n_in - a_, a_out, n_out - a_out)
            fisher[ci, i] = fisher_exact_two_sided(a_, n_in - a_, a_out, n_out - a_out)
    R.update(acc_m_hat=acc_m_hat, acc_c_hat=acc_c_hat, dk_hat=dk_hat, SDk=kb["SD"], zk=kb["z"], qk=kb["q"], certk=kb["cert"],
             fisher=fisher, est=fisher < ALPHA, table=table, keyed_in=table[:, :, 0] + table[:, :, 1])
    # widened-q reading beside, on delta'
    if want_widener:
        tau = tau_widener(data, T)
        wb = maxt_block(delta_draw, delta_hat, scale=np.sqrt(R["SD"] ** 2 + tau ** 2))
        R.update(tau=tau, zw=wb["z"], qw=wb["q"], certw=wb["cert"])
    # shrinkage of the prior, per anchor
    if want_shrink:
        sh = {}
        for anc in anchors:
            thu, cu = fit_batch(T[anc]["A"].sum(0)[None], prior=0.0)
            sh[anc] = (float(thu[0].std(ddof=1)) / float(th_hat[anc].std(ddof=1)), cu)
        thu, cu = fit_batch(Wm_pool_hat, prior=0.0)
        sh["POOLED"] = (float(thu[0].std(ddof=1)) / float(th_hat["POOLED"].std(ddof=1)), cu)
        R["shrink"] = sh
    log("certificate done (%.0fs)" % (time.time() - t0))
    return R


# ----------------------------------------------------------------------------------------------------------
# readout
# ----------------------------------------------------------------------------------------------------------
def var1(v):
    v = np.asarray(v, dtype=float).ravel(); return float(v.var(ddof=1))


REG_LABEL = "registered; biased by construction (null family rate 80.7-92.1% at nominal 5%)"


def readout(data, R, L, classes=CLASS, maxt_q=MAXT_MERGED_Q, record=True):
    models, anchors = R["models"], R["anchors"]; M = len(models); nA = len(anchors); ncell = nA * M
    cert, certk, est = R["cert"], R["certk"], R["est"]
    same = np.sign(R["delta_hat"]) == np.sign(R["dk_hat"])
    opp = (R["delta_hat"] * R["dk_hat"]) < 0
    wrong = cert & opp; wrong_est = cert & opp & est
    n_cert = int(cert.sum()); n_certk = int(certk.sum()); n_marg = int(R["marg"].sum())
    n_wrong = int(wrong.sum()); n_wrong_est = int(wrong_est.sum())
    rcert = R["reg_cert"]; ropp = (R["reg_delta_hat"] * R["dk_hat"]) < 0; rsame = np.sign(R["reg_delta_hat"]) == np.sign(R["dk_hat"])
    rn_cert = int(rcert.sum()); rn_wrong = int((rcert & ropp).sum()); rn_wrong_est = int((rcert & ropp & est).sum())
    say = L.append
    say("=== PROFILE-DEVIATION-CERT: is delta'_ac = theta_ac - theta'_m,c certifiable beyond zero? (%s) ==="
        % ("board of record" if record else "SYNTHETIC"))
    say("  cells: %d models x %d anchors = %d (the anchor is the cell; no leaf, no sub-anchor row)" % (M, nA, ncell))
    say("  READING OF RECORD (programme bracket [CORRECTED 2026-09-18 by REVIEW], 1534a4a): PRIOR-MATCHED deviation "
        "delta' = theta_ac (per-anchor MM, prior %.1f, the published row) - theta'_m,c (pooled MM with the prior scaled by "
        "pooled matches / anchor matches, so both fits carry the same prior-to-data weight)." % PRIOR)
    say("  the REGISTERED reading delta = theta_ac - theta_m (pooled MM, prior %.1f) is printed beside every count as "
        "\"%s\" and is not scored." % (PRIOR, REG_LABEL))
    say("  fit: jf.board_from -> rj.mm_fit (0.5 pseudo-win per side of every observed pair, Jeffreys, BtMmFitter "
        "DEFAULT_PRIOR_STRENGTH); batched numpy copy asserted vs rj.mm_fit: max |dtheta| %s over %s fits"
        % (("%.2e" % R["fit_dev"][0]) if R["fit_dev"] else "n/a", R["fit_dev"][1] if R["fit_dev"] else "-"))
    say("  resamples: B = %d, seed %d, questions resampled WITHIN each anchor (random.Random(seed), anchors sorted, B draws "
        "each); pooled draw b = union of the anchors' draw b; SD = draw SD (ddof 1); q_cell = 95th pct (numpy linear) of "
        "max over the anchor's %d models of |delta'* - delta'_hat| / SD; CERTIFIED iff |delta'_hat| / SD >= q_cell"
        % (R["B"], R["seed"], M))
    say("  MM convergence at 1e-12 within 2000 iterations: %s; prior-matched pooled fits: %s"
        % ("all boards" if all(R["conv"].values()) else "NOT on " + ", ".join(k for k, v in R["conv"].items() if not v),
           "all" if all(R["pm_conv"].values()) else "NOT on " + ", ".join(k for k, v in R["pm_conv"].items() if not v)))
    say("  routing attenuation caveat (ROUTING-ATTENUATION, printed once): ~20% proportional shrinkage of every contrast at "
        "19% mis-routing (30-35% in the smallest anchors) - a caveat on the MAGNITUDE of every deviation below, not on its "
        "sign; the prior-matched reading attenuates |delta'| further for |theta_m| > 1.5 (a certified sign is preserved, "
        "a magnitude is not published).")
    if "shrink" in R:
        say("")
        say("  prior shrinkage per anchor (SD of theta, unpenalised MM / prior-0.5 MM; K-RECONCILE checker (3) measured "
            "1.23-1.82x on the 12-model x12 board) and the prior-matched pooled prior (0.5 x pooled / anchor matches):")
        say("  %-18s %6s %8s %7s %10s %10s" % ("anchor", "q", "matches", "shrink", "unpen.conv", "pm prior"))
        for ci, anc in enumerate(anchors):
            say("  %-18s %6d %8d %6.2fx %10s %10.2f" % (anc, len(data["qs"][anc]), len(data["rows"][anc]), R["shrink"][anc][0],
                                                        "yes" if R["shrink"][anc][1] else "NO", R["pm_prior"][ci]))
        say("  %-18s %6d %8d %6.2fx %10s %10s" % ("POOLED", sum(len(data["qs"][a]) for a in anchors),
                                                   sum(len(data["rows"][a]) for a in anchors), R["shrink"]["POOLED"][0],
                                                   "yes" if R["shrink"]["POOLED"][1] else "NO", "-"))
        slope = np.polyfit(np.tile(R["th_hat"]["POOLED"], nA), R["reg_delta_hat"].ravel(), 1)[0]
        slope_pm = np.polyfit(np.tile(R["th_hat"]["POOLED"], nA), R["delta_hat"].ravel(), 1)[0]
        say("  slope of delta_hat on theta_m over the %d cells: registered %+.4f (the bias; -0.2185 on the record per the "
            "bracket), prior-matched %+.4f" % (ncell, slope, slope_pm))
    say("")
    say("=== per anchor: q_cell(dev) on delta' (the certificate), widened-q beside, registered beside, MAXT pair-level q for scale ===")
    say("  %-18s %-19s %5s %7s %5s %5s | %7s %6s | %7s %5s %5s | %7s %5s %5s | %7s" %
        ("anchor", "class (PIA C2)", "q", "q_dev", "cert", "marg", "q_w", "cert_w", "q_key", "certk", "est", "reg_q", "reg", "regm", "maxt q"))
    for ci, anc in enumerate(anchors):
        say("  %-18s %-19s %5d %7.3f %5d %5d | %7s %6s | %7.3f %5d %5d | %7.3f %5d %5d | %7s" %
            (anc, classes.get(anc, "?"), len(data["qs"][anc]), R["q"][ci], int(cert[ci].sum()), int(R["marg"][ci].sum()),
             ("%.3f" % R["qw"][ci]) if "qw" in R else "-", ("%d" % R["certw"][ci].sum()) if "certw" in R else "-",
             R["qk"][ci], int(certk[ci].sum()), int(est[ci].sum()),
             R["reg_q"][ci], int(rcert[ci].sum()), int(R["reg_marg"][ci].sum()),
             ("%.3f" % maxt_q[anc]) if maxt_q and anc in maxt_q else "-"))
    say("  q_dev range %.3f-%.3f (median %.3f); marginal 1.96 count (NOT the count of record): %d of %d; reg / regm = the %s"
        % (R["q"].min(), R["q"].max(), float(np.median(R["q"])), n_marg, ncell, REG_LABEL))
    if "certw" in R:
        say("  widened-q reading on delta': tau_mc = RMS of the model's in-anchor pair wideners exp(%.4f + %.4f * agree); widened "
            "statistic held to the widened-scale q; certified %d of %d (beside; the hybrid is not computed)"
            % (B0, B1, int(R["certw"].sum()), ncell))
    # C1
    say("")
    say("=== (C1) key-certified share: certified key cells / %d (unchanged by the bracket) ===" % ncell)
    say("  overall %d / %d = %.1f%%; established (Fisher p < %.2f, in vs out, %s) %d / %d"
        % (n_certk, ncell, 100 * n_certk / ncell, ALPHA, "keyed judged questions", int(est.sum()), ncell))
    say("  per anchor: " + ", ".join("%s %d/%d" % (anc, int(certk[ci].sum()), M) for ci, anc in enumerate(anchors)))
    # C2
    say("")
    say("=== (C2) judge-certified share: certified judge cells (delta') / %d ===" % ncell)
    say("  overall %d / %d = %.1f%% (marginal 1.96: %d, not of record) | %d / %d = %.1f%% (%s)"
        % (n_cert, ncell, 100 * n_cert / ncell, n_marg, rn_cert, ncell, 100 * rn_cert / ncell, REG_LABEL))
    say("  per anchor: " + ", ".join("%s %d/%d" % (anc, int(cert[ci].sum()), M) for ci, anc in enumerate(anchors)))
    say("  per anchor (%s): %s" % (REG_LABEL, ", ".join("%s %d" % (anc, int(rcert[ci].sum())) for ci, anc in enumerate(anchors))))
    n_conc = int(sum(cert[ci].sum() for ci, anc in enumerate(anchors) if anc in CONCENTRATION))
    rn_conc = int(sum(rcert[ci].sum() for ci, anc in enumerate(anchors) if anc in CONCENTRATION))
    n_fail = int(sum(cert[ci].sum() for ci, anc in enumerate(anchors) if classes.get(anc) == "FAIL"))
    say("  in Physics / Math / Law: %d of %d judge-certified (%s: %d of %d); in FAIL anchors (PREDICTIVE-ONLY, counted, never a "
        "claim): %d" % (n_conc, n_cert, REG_LABEL, rn_conc, rn_cert, n_fail))
    say("  overlap of the two certified sets: %d cells in both; %d only prior-matched; %d only registered"
        % (int((cert & rcert).sum()), int((cert & ~rcert).sum()), int((rcert & ~cert).sum())))
    say("  certified list per model on delta' (sign = above (+) / below (-) its own standing; key dev, Fisher p; class; publishable?):")
    for i, m in enumerate(models):
        rows = [(anchors[ci], ci) for ci in range(nA) if cert[ci, i]]
        rrows = [anchors[ci] for ci in range(nA) if rcert[ci, i]]
        head = "    %-30s theta_m %+.3f" % (m, R["th_hat"]["POOLED"][i])
        if not rows:
            say(head + "  none" + ("   [registered-only: %s]" % ", ".join(rrows) if rrows else "")); continue
        say(head + ("   [registered set: %s]" % (", ".join(rrows) if rrows else "none")))
        for anc, ci in rows:
            cl = classes.get(anc, "?")
            flag = "PREDICTIVE-ONLY" if cl == "FAIL" else ("wrong(established)" if wrong_est[ci, i] else ("wrong key sign" if opp[ci, i] else "ok"))
            say("      %-18s delta' %+.3f SD %.3f z %5.2f q %.2f | reg delta %+.3f z %5.2f | key dev %+.3f (z %.2f, Fisher p %.3g%s) | %-19s %s"
                % (anc, R["delta_hat"][ci, i], R["SD"][ci, i], R["z"][ci, i], R["q"][ci], R["reg_delta_hat"][ci, i], R["reg_z"][ci, i],
                   R["dk_hat"][ci, i], R["zk"][ci, i], R["fisher"][ci, i], ", est" if est[ci, i] else "", cl, flag))
    # C3
    say("")
    say("=== (C3) wrong(established) among the judge-certified (delta'): denominator = judge-certified count %d ===" % n_cert)
    say("  wrong key sign %d, of which Fisher-established %d -> wrong(established) = %d / %d%s"
        % (n_wrong, n_wrong_est, n_wrong_est, n_cert, (" = %.1f%%" % (100 * n_wrong_est / n_cert)) if n_cert else " (no certified cell)"))
    say("  (%s: wrong key sign %d, wrong(established) %d / %d)" % (REG_LABEL, rn_wrong, rn_wrong_est, rn_cert))
    # C4
    say("")
    say("=== (C4) variance share of delta' vs theta (sample variances over %d cells / %d models) ===" % (ncell, M))
    vj = var1(R["delta_hat"]); vt = var1(R["th_hat"]["POOLED"]); sj_ = float((R["SD"] ** 2).mean())
    vr = var1(R["reg_delta_hat"]); sr = float((R["reg_SD"] ** 2).mean())
    vk = var1(R["dk_hat"]); va = var1(R["acc_m_hat"]); sk = float((R["SDk"] ** 2).mean())
    say("  judge: var_cells(delta') %.4f / (that + var_models(theta_m) %.4f) = %.3f; mean bootstrap var %.4f -> "
        "noise-subtracted share %.3f; sampling share %.1f%%"
        % (vj, vt, vj / (vj + vt), sj_, max(vj - sj_, 0) / (max(vj - sj_, 0) + vt), 100 * sj_ / vj))
    say("  (%s: var_cells(delta) %.4f -> share %.3f, noise-subtracted %.3f, sampling share %.1f%%)"
        % (REG_LABEL, vr, vr / (vr + vt), max(vr - sr, 0) / (max(vr - sr, 0) + vt), 100 * sr / vr))
    say("  key:   var_cells(dev_key) %.5f / (that + var_models(acc_m) %.5f) = %.3f; mean bootstrap var %.5f -> "
        "noise-subtracted share %.3f; sampling share %.1f%%"
        % (vk, va, vk / (vk + va), sk, max(vk - sk, 0) / (max(vk - sk, 0) + va), 100 * sk / vk))
    # C5
    say("")
    say("=== (C5) sign agreement of the certified sets (delta') ===")
    n_same = int((cert & same).sum())
    say("  of the %d judge-certified cells, key deviation with the SAME sign: %d%s; baseline over all %d cells: %d = %.1f%%"
        % (n_cert, n_same, (" = %.1f%%" % (100 * n_same / n_cert)) if n_cert else "", ncell, int(same.sum()), 100 * same.sum() / ncell))
    both = int((cert & certk).sum())
    say("  cells certified by BOTH judge and key: %d (of which same sign %d); key-certified only %d; judge-certified only %d"
        % (both, int((cert & certk & same).sum()), int((certk & ~cert).sum()), int((cert & ~certk).sum())))
    say("  (%s: same sign %d / %d; baseline %d / %d)" % (REG_LABEL, int((rcert & rsame).sum()), rn_cert, int(rsame.sum()), ncell))
    # verdicts
    say("")
    say("=== PREDICTIONS (recorded blind) and FALSIFIER - scored on delta' ===")
    p1 = n_certk / ncell < 0.30; p2 = n_cert / ncell < 0.15
    say("  P1 key-certified < 30%% of %d:            %d = %.1f%% -> %s" % (ncell, n_certk, 100 * n_certk / ncell, "HELD" if p1 else "FAILED"))
    say("  P2 judge-certified < 15%% of %d:          %d = %.1f%% -> %s%s  (%s: %d = %.1f%%)"
        % (ncell, n_cert, 100 * n_cert / ncell, "HELD" if p2 else "FAILED",
           " (HELD at 0 as a prediction; C2 below is scored FAILED at 0 under the registrar's support clause)" if n_cert == 0 else "",
           REG_LABEL, rn_cert, 100 * rn_cert / ncell))
    if n_cert:
        p3 = n_conc / n_cert >= 0.5
        say("  P3 >= 50%% of judge-certified in Physics/Math/Law: %d / %d = %.1f%% -> %s" % (n_conc, n_cert, 100 * n_conc / n_cert, "HELD" if p3 else "FAILED"))
    else:
        say("  P3 >= 50%% of judge-certified in Physics/Math/Law: 0 / 0 -> UNDETERMINED")
    p4 = n_wrong_est <= 2
    say("  P4 wrong-key-sign (established) 0-2:        %d -> %s" % (n_wrong_est, "HELD" if p4 else "FAILED"))
    if n_cert == 0:
        say("  Registrar's addition: judge-certified = 0 -> the claim FAILS ON SUPPORT (not through the falsifier); the "
            "profile carries no deviation sentence at all.")
        fals = None
    else:
        fals = n_wrong_est / n_cert > 0.05
        say("  Falsifier wrong(established) > 5%% of judge-certified: %d / %d = %.1f%% -> %s"
            % (n_wrong_est, n_cert, 100 * n_wrong_est / n_cert, "TRIGGERED (claim overturned at this support; no 'certified above / "
               "below its own standing' for any judge-built cell; C1 stands on the key alone)" if fals else "not triggered"))
    say("")
    say("=== CRITERIA (C2-C5 on delta'; C1 on the key) ===")
    say("  C1 key-certified share:      %d / %d = %.1f%% -> %s (prediction < 30%%)" % (n_certk, ncell, 100 * n_certk / ncell, "HELD" if p1 else "FAILED"))
    c2 = p2 and n_cert > 0
    say("  C2 judge-certified share:    %d / %d = %.1f%% (%d in FAIL anchors PREDICTIVE-ONLY) -> %s (prediction < 15%%%s)"
        % (n_cert, ncell, 100 * n_cert / ncell, n_fail, "HELD" if c2 else "FAILED",
           "; FAILED at judge-certified = 0 under the registrar's support clause while P2 scores HELD at 0" if n_cert == 0 else ""))
    c3 = (n_cert > 0) and not fals
    say("  C3 wrong(established):       %d / %d -> %s" % (n_wrong_est, n_cert, ("HELD" if c3 else "FAILED") if n_cert else "FAILED (no support)"))
    say("  C4 variance share:           judge %.3f (noise-subtracted %.3f), key %.3f (noise-subtracted %.3f) -> DELIVERED (no threshold registered)"
        % (vj / (vj + vt), max(vj - sj_, 0) / (max(vj - sj_, 0) + vt), vk / (vk + va), max(vk - sk, 0) / (max(vk - sk, 0) + va)))
    say("  C5 sign agreement:           %d / %d certified same-sign; baseline %.1f%% -> DELIVERED (descriptive)"
        % (n_same, n_cert, 100 * same.sum() / ncell))
    claim = (n_cert > 0) and not fals
    say("  CLAIM 'delta_ac carries certifiable content beyond theta_m': %s"
        % ("HELD at this support (%d judge-certified cells, %d wrong(established))" % (n_cert, n_wrong_est) if claim
           else ("FAILS ON SUPPORT (0 judge-certified)" if n_cert == 0 else "FALSIFIED (%d / %d wrong(established))" % (n_wrong_est, n_cert))))
    return dict(n_cert=n_cert, n_certk=n_certk, n_wrong=n_wrong, n_wrong_est=n_wrong_est, n_conc=n_conc, claim=claim, wrong_est=wrong_est, same=same)


def write_cells(path, data, R, S, classes=CLASS):
    models, anchors = R["models"], R["anchors"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "anchor", "class", "publishable", "n_judged_q", "keyed_in", "theta_ac", "theta_m", "theta_m_prior_matched",
                    "pm_prior", "delta", "SD", "z", "q_cell", "certified", "marginal_1.96", "tau_w", "z_w", "q_w", "certified_w",
                    "acc_mc", "acc_m", "dev_key", "SD_key", "z_key", "q_key", "key_certified", "fisher_p", "established", "same_sign",
                    "wrong_established", "reg_delta", "reg_SD", "reg_z", "reg_q", "reg_certified", "reg_marginal_1.96"])
        for ci, anc in enumerate(anchors):
            for i, m in enumerate(models):
                cl = classes.get(anc, "?")
                w.writerow([m, anc, cl, "PREDICTIVE-ONLY" if cl == "FAIL" else "claimable", len(data["qs"][anc]), int(R["keyed_in"][ci, i]),
                            "%.6f" % R["th_hat"][anc][i], "%.6f" % R["th_hat"]["POOLED"][i], "%.6f" % R["pm_theta_hat"][ci, i],
                            "%.4f" % R["pm_prior"][ci], "%.6f" % R["delta_hat"][ci, i],
                            "%.6f" % R["SD"][ci, i], "%.4f" % R["z"][ci, i], "%.4f" % R["q"][ci], int(R["cert"][ci, i]), int(R["marg"][ci, i]),
                            "%.6f" % R["tau"][ci, i] if "tau" in R else "", "%.4f" % R["zw"][ci, i] if "zw" in R else "",
                            "%.4f" % R["qw"][ci] if "qw" in R else "", int(R["certw"][ci, i]) if "certw" in R else "",
                            "%.6f" % R["acc_c_hat"][ci, i], "%.6f" % R["acc_m_hat"][i], "%.6f" % R["dk_hat"][ci, i], "%.6f" % R["SDk"][ci, i],
                            "%.4f" % R["zk"][ci, i], "%.4f" % R["qk"][ci], int(R["certk"][ci, i]), "%.6g" % R["fisher"][ci, i],
                            int(R["est"][ci, i]), int(S["same"][ci, i]), int(S["wrong_est"][ci, i]),
                            "%.6f" % R["reg_delta_hat"][ci, i], "%.6f" % R["reg_SD"][ci, i], "%.4f" % R["reg_z"][ci, i],
                            "%.4f" % R["reg_q"][ci], int(R["reg_cert"][ci, i]), int(R["reg_marg"][ci, i])])


def write_draws(path, R):
    arrs = {"seed": np.array(R["seed"]), "B": np.array(R["B"]), "models": np.array(R["models"]), "anchors": np.array(R["anchors"])}
    for anc in R["anchors"]:
        arrs["counts__" + anc] = R["counts"][anc]; arrs["theta__" + anc] = R["th_draw"][anc]
    arrs["theta__POOLED"] = R["th_draw"]["POOLED"]
    arrs["pm_prior"] = R["pm_prior"]; arrs["delta_pm_draw"] = R["delta_draw"]
    np.savez_compressed(path, **arrs)


def registered_classes_check(L):
    """The classes are the registration's; if profile_interval_all.txt is on disk its merged-board table must agree."""
    if not os.path.exists(PIA_TXT):
        L.append("  PROFILE-INTERVAL-ALL outcome file not on disk; classes taken from the registration text."); return
    txt = open(PIA_TXT, encoding="utf-8").read().split("\n")
    try:
        i = next(k for k, l in enumerate(txt) if l.strip().startswith("--- MERGED judge, 20 rows ---"))
    except StopIteration:
        L.append("  profile_interval_all.txt: merged-board table not found; classes taken from the registration text."); return
    found = {}
    for l in txt[i + 2:i + 2 + 14]:
        parts = l.split()
        if len(parts) < 8:
            continue
        name = l[:22].strip()
        cls = next((p for p in parts if p in ("PASS", "PASS-WITH-INTERVAL", "FAIL")), None)
        if cls:
            found[name] = cls
    bad = {a: (CLASS[a], found.get(a)) for a in CLASS if found.get(a) != CLASS[a]}
    if bad:
        raise SystemExit("[CLASS] registration classes differ from profile_interval_all.txt: %s" % bad)
    L.append("  PROFILE-INTERVAL-ALL C2 classes (registration) agree with profile_interval_all.txt's merged-board table: 14 / 14.")


# ----------------------------------------------------------------------------------------------------------
# --dry-run
# ----------------------------------------------------------------------------------------------------------
def dry_run():
    data = load_record()
    models, anchors = data["models"], data["anchors"]
    print("=== PROFILE-DEVIATION-CERT --dry-run: the data object (no fit, no outcome number) ===")
    print("  x12 cache %s" % data["x12_path"])
    print("  x20 cache %s" % data["x20_path"])
    print("  key      %s (eval_results.is_correct, %s excluded)" % (data["eval_path"], EXCLUDE))
    print("  rows: x12 %d + x20 %d = %d verdicts (invalid dropped) | pinned %d + %d = %d"
          % (data["n12"], data["n20"], data["n12"] + data["n20"], PIN["n12"], PIN["n20"], PIN["n"]))
    print("  models: %d | judged questions %d (x20-judged %d) | anchors %d -> cells %d"
          % (len(models), data["nq_all"], PIN["q20"], len(anchors), len(models) * len(anchors)))
    print("  x12 cache `anchor` column vs bareq512_s42 tree anchor: %d mismatches" % data["cache_anchor_mismatch"])
    print("  %-18s %-19s %6s %8s %10s %12s" % ("anchor", "class (PIA C2)", "q", "matches", "keyed q", "min/max keyed"))
    for anc in anchors:
        qs = data["qs"][anc]
        cov = [sum(1 for q in qs if m in data["K"].get(q, {})) for m in models]
        print("  %-18s %-19s %6d %8d %10d %5d/%5d" % (anc, CLASS[anc], len(qs), len(data["rows"][anc]),
                                                       sum(1 for q in qs if data["K"].get(q)), min(cov), max(cov)))
    print("  key coverage per model over the %d judged questions:" % data["nq_all"])
    allq = [q for anc in anchors for q in data["qs"][anc]]
    for m in models:
        n = sum(1 for q in allq if m in data["K"].get(q, {}))
        print("    %-30s %5d / %d keyed (%.1f%%)" % (m, n, len(allq), 100 * n / len(allq)))
    L = []; registered_classes_check(L); print("\n".join(L))
    print("  prior: rj.PRIOR = %.1f; widener B0 %.4f B1 %.4f (budget_transfer, applied cold); MAXT merged per-anchor q "
          "%.2f-%.2f printed beside at --run" % (PRIOR, B0, B1, min(MAXT_MERGED_Q.values()), max(MAXT_MERGED_Q.values())))
    print("  --run would: draw B = %d resamples (seed %d), fit %d per-anchor + 1 pooled boards per draw (+ %d prior-matched "
          "pooled fits), write %s, %s and %s once." % (B_DEFAULT, SEED_DEFAULT, len(anchors), len(anchors), OUT, CELLS, DRAWS))
    print("  outcome file on disk: %s" % ("YES - --run would refuse" if os.path.exists(OUT) else "no"))
    print("  nothing fitted, nothing written, no calls.")


# ----------------------------------------------------------------------------------------------------------
# --selftest: synthetic verdicts with planted deviations
# ----------------------------------------------------------------------------------------------------------
def synth(seed, M=20, nA=14, q_range=(120, 300), matches_per_q=8, tie_rate=0.10, spread=2.5, planted=None, key_planted=None):
    """Synthetic board: theta_m evenly spread in [-spread, spread]; theta_ac = theta_m + planted[(m, c)]; verdicts
    Bernoulli(sigmoid(theta_a - theta_b)) with a TIE rate; keys Bernoulli(acc_m + key_planted[(m, c)])."""
    rng = random.Random(seed); nr = np.random.default_rng(seed)
    models = ["m%02d" % i for i in range(M)]; anchors = ["A%02d" % c for c in range(nA)]
    theta = np.linspace(-spread, spread, M); nr.shuffle(theta)
    acc = 1 / (1 + np.exp(-0.5 * theta)) * 0.7 + 0.15
    planted = planted or {}; key_planted = key_planted or {}
    rows = {}; qs = {}; K = {}; P = {}; qid = 0
    for c, anc in enumerate(anchors):
        n = rng.randint(*q_range); qs[anc] = list(range(qid, qid + n)); qid += n
        th = theta.copy(); ac = acc.copy()
        for i, m in enumerate(models):
            th[i] += planted.get((m, anc), 0.0); ac[i] += key_planted.get((m, anc), 0.0)
        rs = []
        for q in qs[anc]:
            K[q] = {}; P[q] = {}
            for i, m in enumerate(models):
                k = int(rng.random() < ac[i]); K[q][m] = k; P[q][m] = "A" if k else rng.choice("BCDEFGHIJ")
            for _ in range(matches_per_q):
                i, j = rng.sample(range(M), 2)
                if rng.random() < tie_rate:
                    w = "TIE"
                else:
                    pa = 1 / (1 + math.exp(-(th[i] - th[j]))); w = models[i] if rng.random() < pa else models[j]
                rs.append((models[i], models[j], q, w))
        rows[anc] = rs
    return dict(models=models, anchors=anchors, rows=rows, qs=qs, K=K, P=P, theta=theta, acc=acc)


def selftest(reps, B, seed):
    L = []; say = L.append
    say("=== PROFILE-DEVIATION-CERT --selftest (synthetic verdicts; nothing of record is read) ===")
    say("  B = %d per replicate, %d null replicates; 20 models x 14 anchors; theta_m spread +-2.5 (the record's per-anchor theta "
        "SD is ~1.3 under the prior); ~8 matches per question, 10%% ties" % (B, reps))
    ok = True
    # ---- (1) Fisher vs scipy
    from scipy.stats import fisher_exact
    import scipy.stats as st
    rng = random.Random(1); worst = 0.0
    for _ in range(200):
        a, b, c, d = (rng.randint(0, 150) for _ in range(4))
        worst = max(worst, abs(fisher_exact_two_sided(a, b, c, d) - float(fisher_exact([[a, b], [c, d]])[1])))
    say("  (1) exact two-sided Fisher (integer arithmetic) vs scipy.stats.fisher_exact on 200 random 2x2: max |dp| %.2e -> %s"
        % (worst, "OK" if worst < 1e-9 else "MISMATCH")); ok &= worst < 1e-9
    # ---- (2)+(3) planted deviations: two replicates, |delta| = 1.2 and 1.5, one cell per model band, sign alternating
    plants = {}
    for size, sd in ((1.2, seed), (1.5, seed + 1)):
        d0 = synth(sd)                                   # to know theta_m per model before planting
        th = d0["theta"]; order = np.argsort(np.abs(th))
        low = [int(i) for i in order if abs(th[i]) < 1.0][:2]; mid = [int(i) for i in order if 1.0 <= abs(th[i]) < 1.75][:2]
        hi = [int(i) for i in order[::-1] if abs(th[i]) >= 1.75][:2]
        cells = []
        for k, i in enumerate(low + mid + hi):
            m = "m%02d" % i; anc = "A%02d" % ((2 * k + 1) % 14); sign = 1.0 if k % 2 == 0 else -1.0
            cells.append((m, anc, sign * size, sign * 0.30 if k < 5 else -sign * 0.30, "|theta_m| < 1.0" if i in low else ("1.0-1.75" if i in mid else ">= 1.75")))
        planted = {(m, a): dl for m, a, dl, _, _ in cells}; key_planted = {(m, a): dk for m, a, _, dk, _ in cells}
        data = synth(sd, planted=planted, key_planted=key_planted); T = tensors(data)
        R = certificate(data, T, B, sd, want_widener=(size == 1.2), want_shrink=(size == 1.2), fit_check=True)
        if size == 1.2:
            say("  (2) batched MM vs rj.mm_fit on the synthetic board: max |dtheta| %.2e over %d fits -> OK" % R["fit_dev"])
            classes = {a: "PASS" for a in data["anchors"]}
            S = readout(data, R, L, classes=classes, maxt_q=None, record=False)
        else:
            S = None
        ai = {a: i for i, a in enumerate(data["anchors"])}; mi = {m: i for i, m in enumerate(data["models"])}
        say("")
        say("  (3) planted deviations |delta| = %.1f (one cell per band of |theta_m|; key deviation +-0.30 same sign except the last, "
            "opposite) - recovery per band:" % size)
        band_stats = defaultdict(lambda: [0, 0, 0, 0])
        for m, a, dl, dk, band in cells:
            ci, i = ai[a], mi[m]
            pm, rg, kc = bool(R["cert"][ci, i]), bool(R["reg_cert"][ci, i]), bool(R["certk"][ci, i])
            band_stats[band][0] += 1; band_stats[band][1] += pm; band_stats[band][2] += rg; band_stats[band][3] += kc
            say("      %s (theta_m %+.2f, %-14s) in %s planted %+.1f: prior-matched delta' %+.3f z %.2f (q %.2f) %s | registered delta %+.3f z %.2f %s "
                "| key z %.2f %s, Fisher p %.2g" %
                (m, R["th_hat"]["POOLED"][i], band, a, dl, R["delta_hat"][ci, i], R["z"][ci, i], R["q"][ci], "CERT" if pm else "miss",
                 R["reg_delta_hat"][ci, i], R["reg_z"][ci, i], "CERT" if rg else "miss", R["zk"][ci, i], "CERT" if kc else "miss", R["fisher"][ci, i]))
        for band in ("|theta_m| < 1.0", "1.0-1.75", ">= 1.75"):
            n, a_, b_, c_ = band_stats[band]
            say("      band %-14s: prior-matched %d / %d, registered %d / %d (%s), key %d / %d" % (band, a_, n, b_, n, "artefact-inflated", c_, n))
        plants[size] = dict(pm=sum(v[1] for v in band_stats.values()), reg=sum(v[2] for v in band_stats.values()),
                            key=sum(v[3] for v in band_stats.values()), n=len(cells), R=R, cells=cells, ai=ai, mi=mi)
        if S is not None:
            m, a = cells[-1][0], cells[-1][1]
            say("      the planted opposite-key-sign cell (%s, %s) counted as wrong(established): prior-matched %s, registered %s"
                % (m, a, "yes" if S["wrong_est"][ai[a], mi[m]] else "NO (not certified or not established)",
                   "yes" if (R["reg_cert"][ai[a], mi[m]] and R["est"][ai[a], mi[m]] and R["reg_delta_hat"][ai[a], mi[m]] * R["dk_hat"][ai[a], mi[m]] < 0) else "NO"))
        say("      certified judge cells NOT planted in this replicate: prior-matched %d, registered %d"
            % (int(R["cert"].sum()) - plants[size]["pm"], int(R["reg_cert"].sum()) - plants[size]["reg"]))
    key_rec_ok = all(v["key"] >= v["n"] - 1 for v in plants.values()); ok &= key_rec_ok
    # ---- (4) null rate
    say("")
    say("  (4) null rate under the EXACT null (no planted deviation; every anchor shares theta_m), %d replicates x 14 anchors:" % reps)
    fam = fam_r = fam_k = 0; cells_n = cells_r = 0; tot_fam = tot_cells = 0
    by_abs = defaultdict(lambda: [0, 0, 0])
    for r in range(reps):
        d = synth(seed + 100 + r); Tt = tensors(d)
        Rn = certificate(d, Tt, B, seed + 100 + r, want_widener=False, want_shrink=False, fit_check=False)
        fam += int((Rn["cert"].sum(1) > 0).sum()); fam_r += int((Rn["reg_cert"].sum(1) > 0).sum()); fam_k += int((Rn["certk"].sum(1) > 0).sum())
        cells_n += int(Rn["cert"].sum()); cells_r += int(Rn["reg_cert"].sum()); tot_fam += len(d["anchors"]); tot_cells += Rn["cert"].size
        th = Rn["th_hat"]["POOLED"]
        for i in range(len(d["models"])):
            band = "|theta_m| >= 1.5" if abs(th[i]) >= 1.5 else "|theta_m| < 1.5"
            by_abs[band][0] += int(Rn["cert"][:, i].sum()); by_abs[band][1] += int(Rn["reg_cert"][:, i].sum()); by_abs[band][2] += Rn["cert"].shape[0]
        log("  null replicate %d/%d: prior-matched %d cells / %d anchors, registered %d / %d" %
            (r + 1, reps, int(Rn["cert"].sum()), int((Rn["cert"].sum(1) > 0).sum()), int(Rn["reg_cert"].sum()), int((Rn["reg_cert"].sum(1) > 0).sum())))
    ub = st.binom.ppf(0.975, tot_fam, 0.05) / tot_fam
    pm_ok = fam / tot_fam <= ub; reg_ok = fam_r / tot_fam <= ub; key_ok = fam_k / tot_fam <= ub
    say("      PRIOR-MATCHED reading (of record): anchors with >= 1 false certificate %d / %d = %.1f%% (nominal 5%%, binomial 97.5%% "
        "bound %.1f%%) -> %s; false cells %d / %d = %.2f%%" % (fam, tot_fam, 100 * fam / tot_fam, 100 * ub, "OK" if pm_ok else "EXCEEDED", cells_n, tot_cells, 100 * cells_n / tot_cells))
    for band in sorted(by_abs):
        say("        by the model's standing, %s: prior-matched %d / %d cells = %.1f%%; registered %d / %d = %.1f%%"
            % (band, by_abs[band][0], by_abs[band][2], 100 * by_abs[band][0] / by_abs[band][2], by_abs[band][1], by_abs[band][2], 100 * by_abs[band][1] / by_abs[band][2]))
    say("      REGISTERED reading (%s): %d / %d = %.1f%% -> %s; false cells %d / %d = %.2f%%"
        % (REG_LABEL, fam_r, tot_fam, 100 * fam_r / tot_fam, "OK" if reg_ok else "EXCEEDED", cells_r, tot_cells, 100 * cells_r / tot_cells))
    say("      key comparator: anchors with >= 1 false key certificate %d / %d = %.1f%% -> %s" % (fam_k, tot_fam, 100 * fam_k / tot_fam, "OK" if key_ok else "EXCEEDED"))
    say("")
    say("  SELFTEST verdicts:")
    say("    mechanics (Fisher exact vs scipy; batched MM vs rj.mm_fit; key planted recovered >= n-1 at both sizes; key null rate): %s"
        % ("PASS" if (ok and key_ok) else "FAIL"))
    say("    PRIOR-MATCHED reading: null family rate %.1f%% (bound %.1f%%) -> %s (scored); planted recovered %d / %d at 1.2, %d / %d at 1.5 (reported, not scored: attenuation)"
        % (100 * fam / tot_fam, 100 * ub, "PASS" if pm_ok else "EXCEEDED", plants[1.2]["pm"], plants[1.2]["n"], plants[1.5]["pm"], plants[1.5]["n"]))
    say("    REGISTERED reading (beside, not scored): null family rate %.1f%% -> %s; planted recovered %d / %d at 1.2, %d / %d at 1.5 (artefact-inflated)"
        % (100 * fam_r / tot_fam, "OK" if reg_ok else "EXCEEDED", plants[1.2]["reg"], plants[1.2]["n"], plants[1.5]["reg"], plants[1.5]["n"]))
    allok = ok and key_ok and pm_ok
    say("  SELFTEST: %s" % ("PASS" if allok else "FAIL (mechanics %s, prior-matched null rate %s)" % ("PASS" if (ok and key_ok) else "FAIL", "OK" if pm_ok else "EXCEEDED")))
    return L, allok


# ----------------------------------------------------------------------------------------------------------
# --run
# ----------------------------------------------------------------------------------------------------------
def run(B, seed):
    if os.path.exists(OUT):
        raise SystemExit("[ONCE] %s exists; the outcome of record is written once. Move it aside by hand if a rerun is registered." % OUT)
    if B < 2000:
        raise SystemExit("[B] the registration says B >= 2,000; got %d" % B)
    data = load_record()
    L = []
    L.append("PROFILE-DEVIATION-CERT outcome (%s); pool %s; script tools/analysis/profile_deviation_cert.py" % (time.strftime("%Y-%m-%d %H:%M"), POOL))
    L.append("  caches mode=ro: x12 %d + x20 %d = %d verdicts, %d models, %d judged q, %d anchors (x12 cache anchor column mismatches: %d)"
             % (data["n12"], data["n20"], data["n12"] + data["n20"], len(data["models"]), data["nq_all"], len(data["anchors"]), data["cache_anchor_mismatch"]))
    registered_classes_check(L)
    T = tensors(data)
    R = certificate(data, T, B, seed)
    S = readout(data, R, L)
    L.append("")
    L.append("  files: %s (this), %s (one row per cell), %s (multiplicity matrices + theta draws, seed %d)" % (OUT, CELLS, DRAWS, seed))
    write_cells(CELLS, data, R, S)
    write_draws(DRAWS, R)
    txt = "\n".join(L); print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--B", type=int, default=B_DEFAULT); ap.add_argument("--seed", type=int, default=SEED_DEFAULT)
    ap.add_argument("--selftest-reps", type=int, default=10); ap.add_argument("--selftest-B", type=int, default=400)
    a = ap.parse_args()
    if sum(map(bool, (a.dry_run, a.selftest, a.run))) != 1:
        ap.error("exactly one of --dry-run, --selftest, --run")
    if a.selftest:
        print("pool of record (not read by --selftest): %s" % pool_guard.assert_pool_of_record(POOL))
        L, ok = selftest(a.selftest_reps, a.selftest_B, a.seed)
        print("\n".join(L)); return
    print(pool_guard.assert_pool_of_record(POOL))
    if a.dry_run:
        dry_run()
    else:
        run(a.B, a.seed)


if __name__ == "__main__":
    main()
