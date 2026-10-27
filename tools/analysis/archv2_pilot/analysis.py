"""ARCH-V2-PILOT-K46 --analyze: C0 validity, C1 the exponent (PRIMARY), C1b the level, C1c the rungs, C3 the LOAO map, C2 the
schedule, the support beside the deciding statistic, the predictions and the falsifier (registration L15913-L15955 as
amended L15975-L15983; rulings L15985-L15994).

THE NOMINAL (the control of record; key-blind): the GROK-CALIB UNFILTERED pair (b0 -3.3172, b1 +3.3001), FROZEN, no
decline (cert.FROZEN_GROK_UNFILTERED; check_frozen refuses any other pair), applied to the edges of a sub-board built by
archv2_arena.data.edges_fast (question bootstrap, B 300 inner boards, the fit of record's MM) from the pilot's verdicts
and FREE data only: the edge's A (answer agreement) from the extracted answers. The key is SEALED: the board carries a
constant placeholder key (every model 0 on every question), so no edge is dropped by a key gap and no frontier is
banded, and the edge's `right` field is a placeholder that nothing reads. nominal_a = sum over the anchor's edges with
c~ >= 0.975 of (1 - c~); nu_2(k) = the mean over the 2 anchors of nominal_a on the sub-board of k models.
  EVERY line that uses the pair carries "frozen pair transported from 12 models; planning scale only" (ruling 3 (ii)).
  DEFINITION NOTE (for the registrar): G22's nu leg, which printed L12 = 0.1078, drops zero-gap edges and bands
  frontier-internal edges by the KEY; the key-blind nominal cannot, so C1b prints the level on BOTH definitions (the
  key-informed one only after C1 is written and the key unsealed).
C1 PRIMARY: beta-hat = [ln nu_2(46) - ln nu_2(12)] / ln(46/12), the 12 = rubric_p8.ARENA12 sub-board of the same verdicts;
  the question-clustered bootstrap within anchor, B 2,000, ONE registered stream "boot" drawing every replicate's
  question resample (in replicate order, anchors by name), each replicate refitting both sub-boards (inner edge streams
  "boot/rep<r>/k<k>/<anchor>/qboot", named, logged); SE_dec = sqrt(SE_boot^2 + 0.20^2 / 2); interval beta-hat +- 1.96
  SE_dec; "P EXCLUDED" iff lower > 1.06; "M EXCLUDED" iff upper < 2.05; neither: "UNRESOLVED AT THIS n". A replicate
  with a zero nominal at either k has no finite beta: counted and excluded (G22's nu-leg convention), printed. The
  integrated reading over 21 inner-stream seeds ("boot/integrated/s<ss>") is printed beside and decides nothing.
C1b (descriptive): nu_2(46) with its bootstrap interval, against DEFINITION-MATCHED bars from L12 = 0.1078 (G22_nu_grok.txt
  L32, d9f801b): P = L12 x (46/12)^1.06, M = L12 x 1035/66; the memo bars 0.38 / 0.85 / 1.36 printed "memo definition,
  not comparable"; the 14-anchor projection L12 x (46/12)^beta with C1's interval ("never measured").
  [F10 2026-09-25 (READY 286a1b0 F10), insertion only: the three lines above describe the k 46 C1b bars and the memo
  bars; they are SUPERSEDED by the k 37 bracket at the end of this docstring (0761cfa: P = L12 x (37/12)^1.06 = 0.3556,
  M = L12 x 666/66 = 1.0878; the memo bars are NOT printed). No executable k 46 value remains.]
C1c (descriptive): the slope of ln nu_2 on ln k over k in {12, 20, 28, 36, 46}: 12 = ARENA12, 46 = the roster, the
  middle rungs one random sub-roster each (stream "rungs"); its interval from the first 200 replicates of C1's bootstrap.
C3 (decides nothing; ruling 3 (iii)): after C1's file is written the key is unsealed (unseal_key refuses before); on the
  key-informed edges (zero-gap dropped, frontier banded, established = sb.mcnemar_edge p < 0.05) at k 46 and k 12:
  per LOAO fold (2 folds: each fits on the other anchor) and pooled, (b0, b1), the edge count, wrong(all labels) and
  wrong(established), b1's delta-deviance on the established edges against 3.84 (IDENTIFIED / NOT); the frozen / LOAO
  nominal ratio at k 46 and k 12; GROK-CALIB's 920-set LOAO nominal 1.24 beside; the monotonicity count (edges the widener
  makes MORE confident, expected 0); calibration_status.status_word printed as UNDETERMINED.
C0 VALIDITY (a)-(g) first; any failure: "UNDETERMINED BY VALIDITY", no reading. A store with pending slots is not a
  complete cache: the output is <out>_PARTIAL.txt and no reading is made.
THE ORCHESTRATION (the order above, the store, C0 and the outputs) is archv2_pilot.outcome.analyze.
OUTPUTS (write-once, mode "x"): <out>.C1.txt (C0 + C1, written BEFORE the key is unsealed), <out> (everything),
  <out>.streams.tsv, per-replicate records <out>.c1_boot.records.jsonl (g22.RecordStore) and their manifest.
[AMENDED 2026-09-25 BEFORE ANY CODE (0761cfa, docs/judge_v2_program.md L16787-L16992), insertion only; k = 37 by the
author's decision; every "46" above that is the roster size reads 37: C1 beta-hat = [ln nu_2(37) - ln nu_2(12)] /
ln(37/12), ln(37/12) = 1.12601; "M EXCLUDED" iff upper < THE EXACT M = ln(C(37,2)/C(12,2)) / ln(37/12) = ln(666/66) /
ln(37/12) = 2.052941, printed 2.0529 (pilot.exact_bar_M; the rounded 2.05 convention and its edge side-print are
SUPERSEDED: every comparison is made against the exact value). C1b bars P = L12 x (37/12)^1.06 = 0.3556, M = L12 x
666/66 = 1.0878; the memo bars (k = 46 quantities; the memo has no k = 37 reading) are NOT PRINTED. C1c rungs
k in {12, 20, 28, 37} (rung 36 dropped). C3 at k 37 and k 12. Support planning SE_boot 0.19, SE_dec 0.23, inflated
0.29, MDE 0.82 < the P-M separation 0.99 (SCOREABLE). P2b [0.6, 1.3] (point 0.9), P3a 0.79 / P3b 0.13, P4 [1,540, 2,664]
with after = before (t = 0). DISCLOSURE beside C1 and C1b: arx_0314's empty / short raw outputs on its scheduled cells and
its share of the called edges on each rung.]
[L7' 2026-09-25, AFTER the run and BEFORE --analyze (READY 1f58df5 L7'; READY 286a1b0 F2 / F3 / F4; delta G1 / G2),
insertion only; nothing above is rewritten:
  F2 (Support (b), L16893, K10 (a)): the MEASURED question-clustered DEFF of beta-hat is printed beside SE_dec and MDE
  (support_lines, deff_lines). DEFF = Var_q / Var_m, where Var_q is the variance of beta over C1's question-clustered
  bootstrap (the finite replicates of "boot") and Var_m is its variance over a MATCH-LEVEL bootstrap of the same size B
  (match_bootstrap: within each anchor the usable dual-order matches are resampled i.i.d., one registered stream
  "deff/mboot", each drawn match its own cluster in the inner edges_fast, inner streams "deff/rep<r>/k<k>/<anchor>/qboot";
  only the k_hi and k_lo sub-boards are refitted); n = the usable dual-order matches of the board (the match-level
  resample's units), n_eff = n / DEFF; the MDE at 80% = 2.80 x SE_dec, printed with and without the registered 1.25
  transport inflation. These lines DECIDE NOTHING: the SCOREABLE line, C1's interval and every reading are unchanged.
  The "DEFF: not applicable" line and the "n_eff(questions)" label are kept and bracketed in the printed text.
  F3 (the registrar's ruling, L15946 / L16921 brackets, before any data): P3a HELD iff C1 reads "P EXCLUDED" (lower >
  1.06), FAILED otherwise (UNRESOLVED included); P3b HELD iff C1 does NOT read "M EXCLUDED" (upper >= the exact M
  2.052941, unrounded), FAILED iff it does (= the falsifier fires); BOTH UNDETERMINED iff C1 gives no reading (C0 FAILS,
  or K7 fires). p3_lines; the former P3b line (HELD on "M EXCLUDED") was INVERTED.
  G1: P5's "posted" is the invocations summed over both stores (journal + prior), as C0 (f).
  F4: the disclosure of READY 286a1b0 F4 is printed verbatim beside C1 and C1b (f4_disclosure_lines), with this
  analysis's own counts beside it.]
[D-4 2026-09-25 (delta READY 3 0c10ea2, MEDIUM, option (a)), insertion only: when C1 gives no reading (C0 FAILED, or
K7), falsifier_lines prints "FALSIFIER NOT READ (no C1 reading: <reason>)" and states no planning consequence (it
printed "NOT FIRED ... planning stands" before, against the ruling "P3b FAILED iff the falsifier fires"); the C0-fail
and C0 (d)-void branches print it too. D-5 (LOW): the F8 board count is disclosed as a witness that can only print 0.]
"""
import math
import os
from collections import defaultdict

import numpy as np

from . import common as C
from . import pilot as PL
from archv2_arena import cert, design, report
from archv2_arena import data as AD
from archv2_arena.report import hit
from archv2_arena.streams import Streams

MUTANT = None       # SELFTEST-ONLY: "unseal_early", "refit_pair", "drop_nonfinite", "bars_on_keyblind", "unwidened_only"
# [L7'] SELFTEST-ONLY mutants added: "p3b_inverted" (the pre-L7' P3b: HELD on 'M EXCLUDED'), "p3_no_undetermined" (P3
# scored on the words when C1 gives no reading), "deff_inverted" (Var_m / Var_q); [D-4] "falsifier_not_fired_no_reading"
# (the pre-D-4 falsifier: "NOT FIRED ... planning stands" when C1 gives no reading)
# [READY 65a9173 K7, ruled] a C1 (and beta_matched) with ANY non-finite bootstrap replicate, or a non-finite point, reads
# "UNDETERMINED (n_inf non-finite replicates)" for both readings; the only admitted value
NONFINITE_RULE = "UNDETERMINED"
# [K5 ruling] C1b compares ONLY the key-informed matched level with the L12 bars; P2b is scored on it
C1B_BAR_LEVEL = "MATCHED"
# [K6 ruling] each C1b level: SE_dec = sqrt(SE_boot^2 + (cfg.level_cv x level)^2 / 2); both intervals printed
C1B_INTERVALS = ("NOT widened for the anchor draw", "widened by the DEV-transported between-anchor CV 0.133")
FROZEN_LABEL = "frozen pair transported from 12 models; planning scale only"
GROK_CALIB_LOAO_920 = 1.24
# [0761cfa] Support (d)-(f) at k 37: SE_dec 0.2342 (0.23), x 1.25 = 0.2928 (0.29), MDE 2.80 x 0.2928 = 0.820 (0.82),
# separation 2.0529 - 1.06 = 0.9929 (0.99)
PLANNING_SE, PLANNING_SE_INFL, PLANNING_MDE, P_M_SEPARATION = 0.23, 0.29, 0.82, 0.99
PLANNING_SE_BOOT = 0.19         # [0761cfa] Support (d): SE_boot 0.1867 (the SE_dec above is 0.23, not SE_boot)
DISCLOSED_MODEL = "arx_0314"    # [0761cfa] DISCLOSURE: in ARENA12 (both rungs), carries SHORT raw outputs
exact_M = PL.exact_M
C1_MARK = "C1 PRIMARY"


def check_frozen(pair, cfg):
    """The C1 nominal uses the FROZEN pair, never a refit (ruling 3 (i))."""
    C.need(tuple(pair) == tuple(cfg.frozen_pair) == tuple(cert.FROZEN_GROK_UNFILTERED),
           "the C1 nominal must use the FROZEN GROK-CALIB unfiltered pair %s, got %s (a refit is refused)"
           % (cert.FROZEN_GROK_UNFILTERED, tuple(pair)))
    return tuple(pair)


# ── boards ──────────────────────────────────────────────────────────────────────────────────

class _BlindKey(dict):
    """A constant placeholder key: every model 0 on every question (the key is sealed)."""

    def __init__(self, models):
        super().__init__()
        self.zero = {m: 0 for m in models}

    def get(self, q, d=None):
        return self.zero

    def __getitem__(self, q):
        return self.zero


class _KView:
    """The key keyed by the original question; bootstrap copies are (question, copy) (the matched bootstrap)."""

    def __init__(self, base):
        self.base = base

    @staticmethod
    def _orig(q):
        return q[0] if isinstance(q, tuple) else q

    def get(self, q, d=None):
        return self.base.get(self._orig(q), d)

    def __getitem__(self, q):
        return self.base[self._orig(q)]


class _PView:
    """Answers keyed by the original question; bootstrap copies are (question, copy)."""

    def __init__(self, base):
        self.base = base

    @staticmethod
    def _orig(q):
        return q[0] if isinstance(q, tuple) else q

    def get(self, q, d=None):
        return self.base.get(self._orig(q), d)

    def __getitem__(self, q):
        return self.base[self._orig(q)]


def make_board(rows, models, answers, label, key=None):
    b = design.DesignBoard(sorted(models), label)
    keep = set(models)
    b.by = defaultdict(list)
    b.votes = defaultdict(list)
    for anc, a, bb, q, w in rows:
        if a in keep and bb in keep:
            b.by[anc].append((a, bb, q, w))
            b.votes[anc].append((None, None))
    b.P = _PView(answers)
    b.K = key if key is not None else _BlindKey(models)
    b.L = {}
    return b


def blind_edges(board, B, streams, tag):
    edges, aq = AD.edges_fast(board, B, streams, tag, floor=0, keep_zero_gap=True)
    for e in edges:
        e["right"] = False          # a placeholder: the key is sealed; nothing reads it
        e["gap"] = 0.0
        e.pop("la", None)
    return edges


def per_anchor_nominal(edges, pair, anchors):
    out = {a: (0.0, 0, 0) for a in anchors}
    if not edges:
        return out
    E = cert.EdgeArrays(edges, anchors=sorted(anchors))
    c = cert.cbud_v(E, *pair)
    called = c >= cert.THRESH
    for k, a in enumerate(E.anchor_names):
        sel = E.anchor == k
        out[a] = (float((1 - c[sel & called]).sum()), int((sel & called).sum()), int(sel.sum()))
    return out


def nu2(edges, pair, anchors):
    pa = per_anchor_nominal(edges, pair, anchors)
    return float(np.mean([pa[a][0] for a in sorted(anchors)])), pa


def matched_edges(board, B, streams, tag):
    """G22's nu-leg definition (K5 ruling): the KEY-INFORMED edges (edges_fast with the key: zero-gap edges dropped), the
    frontier-internal ones banded by the key; returns (kept edges, n_edges, n_frontier)."""
    edges, _aq = AD.edges_fast(board, B, streams, tag, floor=0)
    fr = design.frontier_mask(edges) if edges else np.zeros(0, bool)
    return [e for e, f in zip(edges, fr) if not f], len(edges), int(fr.sum())


def beta_of(nu_hi, nu_lo, k_hi, k_lo):
    if not (nu_hi > 0 and nu_lo > 0):
        return float("nan")
    return (math.log(nu_hi) - math.log(nu_lo)) / math.log(k_hi / k_lo)


# ── the bootstrap (workers allowed; every stream named) ─────────────────────────────────────

_CTX = {}


def _init(ctx):
    from archv2_arena import ro as aro
    aro.install_global_guard()          # a worker opens no DB (the G22 practice): a refusal, not a hope
    _CTX.clear()
    _CTX.update(ctx)


def _rows_resampled(ctx, draws):
    rows = []
    for anc in sorted(ctx["anchors"]):
        qs = ctx["qs"][anc]
        for c, qi in enumerate(draws[anc]):
            q = qs[int(qi)]
            for a, b, w in ctx["rows_by_q"][(anc, q)]:
                rows.append((anc, a, b, (q, c), w))
    return rows


def replicate(rep, draws, ctx=None):
    ctx = ctx or _CTX
    st = Streams(ctx["master"])
    rows = _rows_resampled(ctx, draws)
    pair, anchors = ctx["pair"], ctx["anchors"]
    rec = {"rep": rep}
    if ctx.get("key") is not None:
        # the MATCHED bootstrap (K5): the same question draws, both rungs key-informed (after the unseal)
        for k in (ctx["k_hi"], ctx["k_lo"]):
            kept, _n, _f = matched_edges(make_board(rows, ctx["rosters"][k], ctx["answers"], "matched k%d" % k,
                                                    key=_KView(ctx["key"])), ctx["B_inner"], st,
                                         "boot/rep%04d/matched/k%02d" % (rep, k))
            rec["nu_k%02d" % k] = nu2(kept, pair, anchors)[0]
        rec["beta"] = beta_of(rec["nu_k%02d" % ctx["k_hi"]], rec["nu_k%02d" % ctx["k_lo"]], ctx["k_hi"], ctx["k_lo"])
        return rec, dict(st.log)
    for k, models in sorted(ctx["rosters"].items()):
        if k not in (ctx["k_hi"], ctx["k_lo"]) and rep >= ctx["B_rungs"]:
            continue
        e = blind_edges(make_board(rows, models, ctx["answers"], "boot k%d" % k), ctx["B_inner"], st,
                        "boot/rep%04d/k%02d" % (rep, k))
        v, pa = nu2(e, pair, anchors)
        rec["nu_k%02d" % k] = v
        rec["per_anchor_k%02d" % k] = {a: pa[a][0] for a in sorted(pa)}
    rec["beta"] = beta_of(rec["nu_k%02d" % ctx["k_hi"]], rec["nu_k%02d" % ctx["k_lo"]], ctx["k_hi"], ctx["k_lo"])
    return rec, dict(st.log)


def _rep_task(args):
    return replicate(*args)


def draw_tasks(ctx, streams, B):
    """The B question resamples within each anchor, from the ONE registered stream "boot" (replicate order, anchors by
    name). The same draws serve C1 and the matched bootstrap (K5: "same bootstrap")."""
    rng = streams.np("boot")
    tasks = []
    for r in range(B):
        draws = {anc: rng.integers(0, len(ctx["qs"][anc]), size=len(ctx["qs"][anc])) for anc in sorted(ctx["anchors"])}
        tasks.append((r, draws))
    return tasks


def run_bootstrap(ctx, streams, B, workers=1, tasks=None):
    tasks = tasks if tasks is not None else draw_tasks(ctx, streams, B)
    recs = []
    if workers <= 1:
        for r, d in tasks:
            rec, log = replicate(r, d, ctx)
            streams.merge(log)
            recs.append(rec)
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers, initializer=_init, initargs=(ctx,)) as ex:
            for rec, log in ex.map(_rep_task, tasks, chunksize=4):
                streams.merge(log)
                recs.append(rec)
    return sorted(recs, key=lambda x: x["rep"])


# ── [L7' F2] the MATCH-LEVEL bootstrap of beta-hat (the DEFF's denominator; decides nothing) ──────────

DEFF_STREAM = "deff/mboot"


def draw_match_tasks(ctx, streams, B):
    """B i.i.d. resamples of the usable dual-order matches within each anchor, from the ONE stream DEFF_STREAM (replicate
    order, anchors by name). ctx["rows_by_anchor"]: {anchor: [(a, b, q, w), ...]} in the board's order."""
    rng = streams.np(DEFF_STREAM)
    tasks = []
    for r in range(B):
        draws = {anc: rng.integers(0, len(ctx["rows_by_anchor"][anc]), size=len(ctx["rows_by_anchor"][anc]))
                 for anc in sorted(ctx["anchors"])}
        tasks.append((r, draws))
    return tasks


def replicate_match(rep, draws, ctx=None):
    """One match-level replicate: each drawn match is its own cluster ((question, draw position), the form of C1's
    copies), so the inner edges_fast resamples matches too; only the k_hi and k_lo sub-boards are refitted."""
    ctx = ctx or _CTX
    st = Streams(ctx["master"])
    rows = []
    for anc in sorted(ctx["anchors"]):
        rs = ctx["rows_by_anchor"][anc]
        for c, i in enumerate(draws[anc]):
            a, b, q, w = rs[int(i)]
            rows.append((anc, a, b, (q, c), w))
    rec = {"rep": rep}
    for k in (ctx["k_hi"], ctx["k_lo"]):
        e = blind_edges(make_board(rows, ctx["rosters"][k], ctx["answers"], "deff k%d" % k), ctx["B_inner"], st,
                        "deff/rep%04d/k%02d" % (rep, k))
        rec["nu_k%02d" % k] = nu2(e, ctx["pair"], ctx["anchors"])[0]
    rec["beta"] = beta_of(rec["nu_k%02d" % ctx["k_hi"]], rec["nu_k%02d" % ctx["k_lo"]], ctx["k_hi"], ctx["k_lo"])
    return rec, dict(st.log)


def _rep_task_match(args):
    return replicate_match(*args)


def match_bootstrap(ctx, streams, B, workers=1, tasks=None):
    tasks = tasks if tasks is not None else draw_match_tasks(ctx, streams, B)
    recs = []
    if workers <= 1:
        for r, d in tasks:
            rec, log = replicate_match(r, d, ctx)
            streams.merge(log)
            recs.append(rec)
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers, initializer=_init, initargs=(ctx,)) as ex:
            for rec, log in ex.map(_rep_task_match, tasks, chunksize=4):
                streams.merge(log)
                recs.append(rec)
    return sorted(recs, key=lambda x: x["rep"])


def measured_deff(betas_q, betas_m, n):
    """-> dict: var_q, var_m over the FINITE replicates of each bootstrap (ddof 1), their counts and non-finite counts,
    deff = var_q / var_m, n (named by the caller), n_eff = n / deff. deff / n_eff are None when either variance is
    undefined (fewer than 2 finite replicates) or var_m is 0."""
    bq = np.array([x for x in betas_q if np.isfinite(x)], dtype=float)
    bm = np.array([x for x in betas_m if np.isfinite(x)], dtype=float)
    vq = float(bq.var(ddof=1)) if bq.size > 1 else float("nan")
    vm = float(bm.var(ddof=1)) if bm.size > 1 else float("nan")
    ok = bool(np.isfinite(vq) and np.isfinite(vm) and vm > 0)
    deff = (vq / vm) if ok else None
    if ok and MUTANT == "deff_inverted":
        deff = vm / vq if vq > 0 else None
    n_eff = (n / deff) if (ok and deff > 0) else None
    return {"var_q": vq, "var_m": vm, "finite_q": int(bq.size), "finite_m": int(bm.size),
            "inf_q": int(len(betas_q) - bq.size), "inf_m": int(len(betas_m) - bm.size), "deff": deff, "n": int(n),
            "n_eff": n_eff}


def deff_lines(d, se_dec, n_what):
    """[L7' F2] the measured DEFF lines (decide nothing). d: measured_deff's dict; n_what names n's unit."""
    mde = 2.80 * se_dec if np.isfinite(se_dec) else float("nan")
    mde_infl = 2.80 * 1.25 * se_dec if np.isfinite(se_dec) else float("nan")
    head = ("    MEASURED question-clustered DEFF of beta-hat (amendment Support (b), K10 (a); L7' 2026-09-25; DECIDES"
            " NOTHING): Var_q %.6f over C1's question-clustered bootstrap (%d finite of %d) / Var_m %.6f over the"
            " match-level bootstrap (stream '%s', %d finite of %d)" % (
                d["var_q"], d["finite_q"], d["finite_q"] + d["inf_q"], d["var_m"], DEFF_STREAM, d["finite_m"],
                d["finite_m"] + d["inf_m"]))
    if d["deff"] is None:
        hit("SUPPORT.DEFF_UNDEFINED")
        return [head, "      DEFF undefined (a variance has fewer than 2 finite replicates, or Var_m is 0); n = %d %s;"
                      " n_eff not computed" % (d["n"], n_what)]
    hit("SUPPORT.DEFF_MEASURED")
    return [head,
            "      DEFF = %.3f | n = %d %s | n_eff = n / DEFF = %s | MDE at 80%% = 2.80 x SE_dec = %s; with the registered"
            " 1.25 transport inflation 2.80 x 1.25 x SE_dec = %s (planning %.2f) | the P-M separation %.2f" % (
                d["deff"], d["n"], n_what, ("%.1f" % d["n_eff"]) if d["n_eff"] is not None else "undefined (DEFF 0)",
                ("%.3f" % mde) if np.isfinite(mde) else "undefined", ("%.3f" % mde_infl) if np.isfinite(mde_infl)
                else "undefined", PLANNING_MDE, P_M_SEPARATION)]


# ── C1 readings (every branch executed by the selftest) ────────────────────────────────────

def c1_interval(beta_hat, betas, between_sd):
    """-> (SE_boot over the finite replicates, SE_dec, lo, hi, n_inf). n_inf (the non-finite replicates) decides under
    NONFINITE_RULE in c1_readings; they are never silently dropped from the reading."""
    b = np.array([x for x in betas if np.isfinite(x)], dtype=float)
    se_boot = float(b.std(ddof=1)) if b.size > 1 else float("nan")
    se_dec = math.sqrt(se_boot ** 2 + between_sd ** 2 / 2.0) if np.isfinite(se_boot) else float("nan")
    return se_boot, se_dec, beta_hat - 1.96 * se_dec, beta_hat + 1.96 * se_dec, int(len(betas) - b.size)


def c1_readings(beta_hat, lo, hi, bar_P, bar_M, n_inf=0, what="C1"):
    """-> (words, lines). K7 (ruled): any non-finite replicate or a non-finite point -> UNDETERMINED for both readings.
    Both exclusions may hold at once (the interval inside (1.06, 2.0529)); neither -> UNRESOLVED AT THIS n.
    [0761cfa] bar_M is THE EXACT M (pilot.exact_bar_M: exact_M(k_hi, k_lo), 2.052941 at k 37), compared unrounded and
    printed to 4 decimals; the former C1.M_EDGE branch (the rounded 2.05 against the exact value) is RETIRED: with an
    exact bar it cannot fire."""
    if NONFINITE_RULE != "UNDETERMINED":
        C.refuse("NONFINITE_RULE %r: the only admitted value is UNDETERMINED (K7 ruling)" % NONFINITE_RULE)
    inf = int(n_inf) if MUTANT != "drop_nonfinite" else 0
    if inf > 0 or not (np.isfinite(beta_hat) and np.isfinite(lo) and np.isfinite(hi)):
        hit("C1.UNDETERMINED_NONFINITE")
        w = "UNDETERMINED (%d non-finite replicates)" % int(n_inf)
        return [w], ["  %s READING: %s%s: neither 'P EXCLUDED' nor 'M EXCLUDED' is read" % (
            what, w, "" if np.isfinite(beta_hat) else "; the point estimate is non-finite")]
    words = []
    if bool(lo > bar_P):
        hit("C1.P_EXCLUDED")
        words.append("P EXCLUDED")
    else:
        hit("C1.P_NOT_EXCLUDED")
    if bool(hi < bar_M):
        hit("C1.M_EXCLUDED")
        words.append("M EXCLUDED")
    else:
        hit("C1.M_NOT_EXCLUDED")
    if not words:
        hit("C1.UNRESOLVED")
        words = ["UNRESOLVED AT THIS n"]
    lines = ["  %s READING: %s  (lower %.4f %s P's %.2f; upper %.4f %s M's %.4f; M bar %.4f (exact, registered);"
             " non-finite replicates 0)" % (what, " + ".join(words), lo, ">" if lo > bar_P else "<=", bar_P, hi,
                                           "<" if hi < bar_M else ">=", bar_M, bar_M)]
    return words, lines


def support_lines(se_boot, se_dec, stats, n_called, deff=None, n_what="usable dual-order matches"):
    """deff: [L7' F2] measured_deff's dict, printed by deff_lines after the (kept, bracketed) DEFF line; None -> the
    measured DEFF is not available to this call (said so)."""
    mde = 2.80 * se_dec if np.isfinite(se_dec) else float("nan")
    out = ["  SUPPORT (measured beside the deciding statistic): denominator = the called edges of the two sub-boards on the"
           " 2 anchors (%s); clusters = questions" % ", ".join("%s: k_hi %d / k_lo %d" % (a, v[0], v[1])
                                                           for a, v in sorted(n_called.items()))]
    for a, s in sorted(stats.items()):
        out.append("    anchor %s: questions judged %d, matches %d, Kish mean matches per question %.2f (sum m^2 / sum m),"
                   " n_eff(questions) %d [L7' 2026-09-25: this label is the questions judged (q_used), NOT an effective"
                   " n; the measured n_eff = n / DEFF is printed below]" % (a, s["q_used"], s["matches"], s["kish_m"],
                                                                           s["q_used"]))
    out.append("    SE_boot %.4f (planning %.2f) | SE_dec %.4f (planning %.2f; %.2f with the 1.25 transport inflation) | MDE at"
               " 80%% = 2.80 x SE_dec = %.3f (planning %.2f) | the P-M separation %.2f" % (
                   se_boot, PLANNING_SE_BOOT, se_dec, PLANNING_SE, PLANNING_SE_INFL, mde, PLANNING_MDE, P_M_SEPARATION))
    out.append("    DEFF: not applicable to the nominal (amendment 2296877: the transported 1.78 is of wrong labels); the"
               " interval IS the question-clustered bootstrap [L7' 2026-09-25: the MEASURED question-clustered DEFF of"
               " beta-hat owed by Support (b) (L16893) is printed below; it decides nothing]")
    if deff is None:
        hit("SUPPORT.DEFF_ABSENT")
        out.append("    MEASURED DEFF: not computed by this call")
    else:
        out += deff_lines(deff, se_dec, n_what)
    if np.isfinite(mde) and mde < P_M_SEPARATION:
        hit("SUPPORT.SCOREABLE")
        out.append("    at the MEASURED support the separation %.2f > MDE %.3f: SCOREABLE as registered" % (P_M_SEPARATION,
                                                                                                         mde))
    else:
        hit("SUPPORT.NOT_SCOREABLE")
        out.append("    at the MEASURED support the separation %.2f <= MDE %s: the reading is printed but the measured"
                   " support does NOT reach the registered MDE (disclosed, not a new criterion)" % (
                       P_M_SEPARATION, "%.3f" % mde if np.isfinite(mde) else "undefined"))
    return out


def level_intervals(level, se_boot, level_cv):
    """K6: (unwidened, widened) 95% intervals of a C1b level: level +- 1.96 SE_boot, and level +- 1.96 SE_dec with
    SE_dec = sqrt(SE_boot^2 + (level_cv x level)^2 / 2)."""
    se_dec = math.sqrt(se_boot ** 2 + (level_cv * level) ** 2 / 2.0)
    if MUTANT == "unwidened_only":
        se_dec = se_boot
    return (level - 1.96 * se_boot, level + 1.96 * se_boot), (level - 1.96 * se_dec, level + 1.96 * se_dec), se_dec


def bars(cfg, k_hi):
    pairs_hi = k_hi * (k_hi - 1) // 2
    pairs_lo = cfg.k_lo * (cfg.k_lo - 1) // 2
    return cfg.L12 * (k_hi / float(cfg.k_lo)) ** cfg.bar_P, cfg.L12 * pairs_hi / float(pairs_lo), pairs_hi, pairs_lo


def bar_word(level, P_bar, M_bar):
    if level < P_bar:
        hit("C1B.BELOW_P")
        return "BELOW the P bar"
    if level <= M_bar:
        hit("C1B.BETWEEN")
        return "BETWEEN the P and M bars"
    hit("C1B.ABOVE_M")
    return "ABOVE the M bar"


def c1b_lines(cfg, k_hi, kb, kb_se, mt, mt_se, beta_kb, beta_m, bm_lo, bm_hi, ratios):
    """C1b under the K5 / K6 rulings. kb: the KEY-BLIND level (first; 'definition differs from L12; no bar'); mt: the
    KEY-INFORMED matched level (G22's nu leg), the only one compared with the L12 bars. ratios: {k: (kb, mt, n_blind_edges,
    n_informed_edges, n_frontier)}. Returns (lines, the level the bars were compared with)."""
    P_bar, M_bar, pairs_hi, pairs_lo = bars(cfg, k_hi)
    out = []
    for name, lvl, se in (("KEY-BLIND", kb, kb_se), ("KEY-INFORMED (matched)", mt, mt_se)):
        (u0, u1), (w0, w1), sed = level_intervals(lvl, se, cfg.level_cv)
        out.append("  C1b %s LEVEL nu_2(%d) = %.4f (%s) | 95%% %s [%.4f, %.4f] (SE_boot %.4f) | 95%% %s [%.4f, %.4f]"
                   " (SE_dec %.4f)" % (name, k_hi, lvl, FROZEN_LABEL, C1B_INTERVALS[0], u0, u1, se, C1B_INTERVALS[1],
                                       w0, w1, sed))
        if name == "KEY-BLIND":
            out.append("    definition differs from L12; no bar")
    cmp_level = kb if MUTANT == "bars_on_keyblind" else mt
    if C1B_BAR_LEVEL != "MATCHED":
        C.refuse("C1B_BAR_LEVEL %r: the only admitted value is MATCHED (K5 ruling)" % C1B_BAR_LEVEL)
    out.append("    DEFINITION-MATCHED bars from L12 = %.4f (G22_nu_grok.txt L32): P = L12 x (%d/%d)^%.2f = %.4f; M = L12 x"
               " %d/%d = %.4f; the MATCHED level lies %s (descriptive)" % (
                   cfg.L12, k_hi, cfg.k_lo, cfg.bar_P, P_bar, pairs_hi, pairs_lo, M_bar,
                   bar_word(cmp_level, P_bar, M_bar)))
    for k in sorted(ratios):
        a, b, nb, ni, nf = ratios[k]
        out.append("    key-blind / key-informed nu_2 at k %d: %.4f / %.4f = %s | edges: key-blind %d, key-informed %d"
                   " (zero-gap dropped %d), frontier banded %d" % (
                       k, a, b, ("%.3f" % (a / b)) if b > 0 else "undefined (matched 0)", nb, ni, nb - ni, nf))
    proj = cfg.L12 * (k_hi / float(cfg.k_lo)) ** beta_m if np.isfinite(beta_m) else float("nan")
    pl = cfg.L12 * (k_hi / float(cfg.k_lo)) ** bm_lo if np.isfinite(bm_lo) else float("nan")
    ph = cfg.L12 * (k_hi / float(cfg.k_lo)) ** bm_hi if np.isfinite(bm_hi) else float("nan")
    mixed = cfg.L12 * (k_hi / float(cfg.k_lo)) ** beta_kb if np.isfinite(beta_kb) else float("nan")
    out.append("    THE 14-ANCHOR PROJECTION (descriptive, NEVER measured): nu_14(%d) = L12 x (%d/%d)^beta_matched = %.4f"
               " [%.4f, %.4f] (%s)" % (k_hi, k_hi, cfg.k_lo, proj, pl, ph, FROZEN_LABEL))
    out.append("    the MIXED projection (key-informed L12 x key-blind exponent; definitions differ) = %.4f; difference"
               " matched - mixed = %+.4f" % (mixed, proj - mixed))
    return out, cmp_level


def rung_lines(rung_nus, boot_slopes):
    ks = sorted(rung_nus)
    x = [math.log(k) for k in ks if rung_nus[k] > 0]
    y = [math.log(rung_nus[k]) for k in ks if rung_nus[k] > 0]
    slope = float(np.polyfit(x, y, 1)[0]) if len(set(x)) >= 2 else float("nan")
    b = np.array([s for s in boot_slopes if np.isfinite(s)])
    lo, hi = (float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975))) if b.size else (float("nan"),) * 2
    return ["  C1c RUNGS (descriptive, decides nothing; %s): %s" % (FROZEN_LABEL, ", ".join(
        "k %d nu %.4f" % (k, rung_nus[k]) for k in ks)),
            "    slope of ln nu_2 on ln k %.3f, percentile 95%% [%.3f, %.3f] over %d replicates" % (slope, lo, hi, b.size)], slope


def slope_of(rec, ks):
    x, y = [], []
    for k in ks:
        v = rec.get("nu_k%02d" % k)
        if v is not None and v > 0:
            x.append(math.log(k))
            y.append(math.log(v))
    return float(np.polyfit(x, y, 1)[0]) if len(set(x)) >= 2 else float("nan")


def c3_status_line(nominal, observed):
    import calibration_status as cs
    w = cs.status_word(nominal, observed)
    if str(w).startswith("UNDETERMINED"):
        hit("C3.STATUS_UNDETERMINED")
        return "    status_word: %s -> printed as UNDETERMINED (ruling 3 (iii): C3 decides nothing)" % w
    hit("C3.STATUS_OVERRIDDEN")
    return ("    status_word: UNDETERMINED (ruling 3 (iii): C3 decides nothing; the function returned %r, which is NOT a"
            " reading at 2 anchors)" % w)


def ident_word(ddev, unident, b1=float("nan")):
    """K10: b1's sign printed beside the word (IDENTIFIED is sign-blind; C3 decides nothing)."""
    sign = ("+" if b1 > 0 else "-" if b1 < 0 else "0") if np.isfinite(b1) else "n/a"
    if unident is None and np.isfinite(ddev) and ddev >= cert.CHI2_1_95:
        hit("C3.IDENTIFIED")
        return "IDENTIFIED (b1 sign %s)" % sign
    hit("C3.NOT_IDENTIFIED")
    return "NOT IDENTIFIED" + (" (%s)" % unident if unident else "") + " (b1 sign %s)" % sign


P3_RULING = ("the registrar's ruling 2026-09-25 before any data (READY 286a1b0 F3; programme L15946 / L16921 brackets):"
             " the interval decides")


def c1_has_reading(c0_pass, words):
    """[L7' F3] C1 gives a reading iff C0 PASSED and K7 did not fire (words is not UNDETERMINED)."""
    return bool(c0_pass) and bool(words) and not any(str(w).startswith("UNDETERMINED") for w in words)


def p3_lines(c0_pass, words):
    """[L7' F3] P3a / P3b scored by the ruling: P3a HELD iff 'P EXCLUDED', FAILED otherwise (UNRESOLVED included);
    P3b HELD iff NOT 'M EXCLUDED' (forecast 0.87 = 1 - 0.13), FAILED iff 'M EXCLUDED' (= the falsifier fires); both
    UNDETERMINED iff C1 gives no reading (C0 FAILED, or K7). The words come from c1_readings (unrounded comparisons)."""
    reading = " + ".join(words) if words else "none"
    if not c1_has_reading(c0_pass, words) and MUTANT != "p3_no_undetermined":
        why = "C0 FAILED (UNDETERMINED BY VALIDITY)" if not c0_pass else "K7 fired (%s)" % reading
        for t in ("P3a", "P3b"):
            hit("PRED.%s.UNDETERMINED" % t)
        return ["    P3a UNDETERMINED: C1 gives no reading (%s); forecast 'P EXCLUDED' 0.79 (%s)" % (why, P3_RULING),
                "    P3b UNDETERMINED: C1 gives no reading (%s); forecast NOT 'M EXCLUDED' 0.87 (= 1 - 0.13)" % why]
    p_ok = "P EXCLUDED" in words
    m_fired = "M EXCLUDED" in words
    if MUTANT == "p3b_inverted":
        m_fired = not m_fired
    hit("PRED.P3a.%s" % ("HELD" if p_ok else "NOT_HELD"))
    hit("PRED.P3b.%s" % ("NOT_HELD" if m_fired else "HELD"))
    return ["    P3a %s: C1 reads %r; HELD iff 'P EXCLUDED' (the widened interval's lower end > 1.06), FAILED otherwise,"
            " UNRESOLVED included; forecast 0.79 (%s)" % ("HELD" if p_ok else "FAILED", reading, P3_RULING),
            "    P3b %s: C1 reads %r; HELD iff C1 does NOT read 'M EXCLUDED' (the widened interval's upper end >= the exact"
            " M 2.052941, compared unrounded), FAILED iff it does (= the FALSIFIER fires); forecast 0.87 (= 1 - the"
            " registered 0.13 for 'M EXCLUDED')" % ("FAILED" if m_fired else "HELD", reading)]


def predictions_lines(c0_pass, beta, level, words, before, after, unusable_share, posted, cfg, prior=None):
    """posted: [L7' G1] the invocations summed over both stores (journal + prior), as C0 (f); prior: the retired
    stores' share, printed beside when given."""
    out = ["  PREDICTIONS (registered before any data; scored):"]

    def sc(tag, ok, text):
        hit("PRED.%s.%s" % (tag, "HELD" if ok else "NOT_HELD"))
        out.append("    %s %s: %s" % (tag, "HELD" if ok else "NOT HELD", text))
    sc("P1", bool(c0_pass), "C0 PASS (point probability 0.9)")
    sc("P2", bool(np.isfinite(beta) and 1.4 <= beta <= 2.4), "beta-hat %.3f in [1.4, 2.4] (point 1.9)" % beta)
    # [0761cfa] P2b, P3 and P4 restated before data at k 37
    sc("P2b", bool(np.isfinite(level) and 0.6 <= level <= 1.3), "the MATCHED (key-informed) level nu_2(37) %.4f in"
       " [0.6, 1.3] (point 0.9; K5 / K6 rulings; amendment 0761cfa)" % level)
    # [L7' F3] the former P3a / P3b lines (P3b HELD on 'M EXCLUDED': INVERTED against the ruling) are replaced by p3_lines
    out.extend(p3_lines(c0_pass, words))
    sc("P4", bool(1540 <= before <= 2664 and after == before),
       "filtered matches %d in [1,540, 2,664] (point 2,120), with no trim: after %d = before (t = 0)" % (before, after))
    sc("P5", bool(unusable_share <= 0.01 and posted <= cfg.ceiling_calls),
       "unusable verdicts %.4f <= 1%% of cached verdict-bearing calls; posted %d%s <= %d" % (
           unusable_share, posted, "" if prior is None else " (invocations: journal %d + prior (retired stores) %d, as"
                                                           " C0 (f))" % (posted - prior, prior), cfg.ceiling_calls))
    return out


def called_share(edges, pair, model):
    """[0761cfa] (called edges naming `model`, called edges) on a sub-board's edges under the frozen pair."""
    if not edges:
        return 0, 0
    E = cert.EdgeArrays(edges)
    called = cert.cbud_v(E, *pair) >= cert.THRESH
    mine = np.array([model in (e["a"], e["b"]) for e in edges], dtype=bool)
    return int((called & mine).sum()), int(called.sum())


def disclosure_lines(raw_counts, shares, where):
    """[0761cfa] DISCLOSURE (printed beside C1 and C1b): arx_0314 is in ARENA12 (both rungs) and carries SHORT raw outputs;
    its empty / short counts over ITS scheduled cells, and its share of the called edges on each rung (shares: {k:
    (called naming it, called) or None when the rung's roster lacks it}). Its sign on beta and on either level is unknown;
    beta is not corrected for it."""
    m = DISCLOSED_MODEL
    rc = raw_counts.get(m)
    out = ["  DISCLOSURE (%s; amendment 0761cfa): %s is in ARENA12 and sits on BOTH rungs; it carries SHORT raw outputs"
           " (< %d characters). Its pair weight differs between the rungs (%s), so its effect does NOT cancel in beta;"
           " its sign on beta and on either level is unknown; beta is NOT corrected for it." % (
               where, m, PL.SHORT_CHARS, ", ".join("k %d: %d of %d pairs" % (k, k - 1, k * (k - 1) // 2)
                                                   for k in sorted(shares) if shares[k] is not None))]
    if rc is None:
        hit("DISCLOSURE.ABSENT")
        out.append("    %s has no scheduled cell in this schedule" % m)
    else:
        hit("DISCLOSURE.COUNTS")
        out.append("    %s raw outputs over its %d scheduled cells: EMPTY %d, SHORT (< %d, empty included) %d, short non-empty"
                   " %d" % (m, rc["cells"], rc["empty"], PL.SHORT_CHARS, rc["short"], rc["short_nonempty"]))
    for k in sorted(shares):
        s = shares[k]
        if s is None:
            out.append("    rung k %d: %s not in this rung's roster" % (k, m))
        else:
            out.append("    rung k %d: called edges naming %s %d of %d (%s)" % (
                k, m, s[0], s[1], ("%.4f" % (s[0] / float(s[1]))) if s[1] else "no called edge"))
    return out


F4_TEXT = ("system turn byte-identical to STACK-NORUBRIC's measured norubric arm (944 of 944 rows, sys_sha"
           " d0c524bbd66b5a5e); the user turn is E-J's; 1,846 of 2,664 matches (69.3%) carry no reference, a branch"
           " STACK-NORUBRIC never measured; GENERIC_SYSTEM + GENERIC_RUBRIC on E-J's layer is UNMEASURED.")
F4_NORUBRIC_SYS16 = "d0c524bbd66b5a5e"      # stack_norubric.db verdicts.sys_sha of the norubric arm (sha256[:16])


def f4_disclosure_lines(klass_counts, system_sha, where):
    """[L7' F4] READY 286a1b0 F4's disclosure, VERBATIM, beside C1 and C1b; then this analysis's own counts (the plan's
    reference classes over the scheduled matches, free data; the loader is not needed) and the system turn's sha beside
    STACK-NORUBRIC's. Prints only; decides nothing."""
    n = sum(klass_counts.values())
    none = int(klass_counts.get("NONE", 0))
    same = system_sha[:16] == F4_NORUBRIC_SYS16
    hit("F4.SYSTEM_%s" % ("EQUAL" if same else "DIFFERS"))
    return ["  DISCLOSURE F4 (READY 286a1b0; programme L16931 bracket; %s): %s" % (where, F4_TEXT),
            "    this analysis: reference NONE on %d of %d scheduled matches (%s; the plan's reference classes %s); the"
            " system turn sha256-text %s, its first 16 = STACK-NORUBRIC's norubric sys_sha %s: %s. The header's '(="
            " STACK-NORUBRIC's measured combination: True)' is true of the SYSTEM TURN ONLY." % (
                none, n, ("%.1f%%" % (100.0 * none / n)) if n else "no scheduled match",
                ", ".join("%s %d" % kv for kv in sorted(klass_counts.items())), system_sha, F4_NORUBRIC_SYS16,
                "EQUAL" if same else "DIFFERS")]


def falsifier_lines(words, c0_pass=True):
    """[D-4 2026-09-25, READY 3 0c10ea2, option (a)] when C1 gives no reading (C0 FAILED, or K7), the falsifier is NOT
    READ and no planning consequence is stated (consistent with the ruling: P3b FAILED iff the falsifier fires; both
    UNDETERMINED without a reading)."""
    if not c1_has_reading(c0_pass, words) and MUTANT != "falsifier_not_fired_no_reading":
        hit("FALSIFIER.NOT_READ")
        why = ("C0 FAILED (UNDETERMINED BY VALIDITY)" if not c0_pass else
               "K7 fired (%s)" % (" + ".join(words) if words else "no words"))
        return ["  FALSIFIER NOT READ (no C1 reading: %s); no planning consequence is stated" % why]
    if "M EXCLUDED" in words:
        hit("FALSIFIER.FIRED")
        return ["  FALSIFIER FIRED: 'M EXCLUDED' overturns ruling 3 (a)'s planning on the memo's M / X columns (planning then"
                " uses the measured exponent, on reading P if it is P-like). NOT overturned: G22's validity readings, the"
                " split of record, the pools, any recorded verdict."]
    hit("FALSIFIER.NOT_FIRED")
    return ["  FALSIFIER NOT FIRED ('M EXCLUDED' did not hold): ruling 3 (a)'s planning on the M / X columns stands."]


def unseal_key(conn, cfg, items, roster, c1_path):
    """The key (response.is_correct, corpus_version named) is read ONLY after C1's file exists and carries the C1 line."""
    ok = bool(c1_path) and os.path.exists(c1_path)
    if ok:
        with open(c1_path, encoding="utf-8") as f:
            ok = C1_MARK in f.read()
    C.need(ok, "the key stays SEALED until C1 is written (ruling 3 (iii)): %r is absent or carries no C1 line" % c1_path)
    hit("KEY.UNSEALED")
    K = {}
    rset = set(roster)
    for m, iid, c in conn.execute("SELECT model, item_id, is_correct FROM response WHERE corpus_version=?", (cfg.cv,)):
        if iid in items and m in rset:
            K.setdefault(iid, {})[m] = int(c or 0)
    return K


def c3_board(say, board, streams, tag, pair, sb, fitfn, k, B):
    edges, aq = AD.edges_fast(board, B, streams, tag, floor=0)
    AD.mark_established(edges, board.K, aq, sb)
    fr = design.frontier_mask(edges) if edges else np.zeros(0, bool)
    kept = [e for e, f in zip(edges, fr) if not f]
    res = {"edges": len(edges), "frontier": int(fr.sum()), "kept": len(kept)}
    if len(kept) < 3:
        say("  C3 k %d: %d key-informed edges (fewer than 3 after the frontier band): no refit" % (k, len(kept)))
        res.update(frozen=0.0, loao=0.0)
        return res
    E = cert.EdgeArrays(kept)
    frozen = cert.summarise_v(E, *pair)
    lo = cert.loao_v(E, fit=fitfn)
    res.update(frozen=frozen[4], loao=lo["nominal"])
    say("  C3 k %d (decides nothing): %d key-informed edges, %d frontier-internal banded, %d kept | frozen-pair nominal %.4f"
        " (%s) | LOAO-refit nominal %.4f, called %d, wrong %d (established %d)" % (
            k, len(edges), int(fr.sum()), len(kept), frozen[4], FROZEN_LABEL, lo["nominal"], lo["n_called"], lo["wrong"],
            lo["wrong_est"]))
    for name in list(E.anchor_names) + ["POOLED"]:
        if name == "POOLED":
            tr = E
            b0, b1 = lo["b0"], lo["b1"]
        else:
            tr = E.subset(E.anchor != E.anchor_names.index(name))
            b0, b1 = lo["fold_params"][name]
        est = tr.subset(tr.est) if len(tr) else tr
        if len(est) >= 3:
            e1, dd, _e0 = cert.ddev_v(est, fit=fitfn)
            un = cert.unidentified(est)
        else:
            e1, dd, un = float("nan"), float("nan"), "fewer than 3 established edges"
        e1 = float(e1)
        say("    %s: (b0, b1) = (%+.4f, %+.4f) on %d edges | wrong(all labels) %d, wrong(established) %d | established"
            " refit b1 %+.4f, delta-deviance %.3f vs 3.84: %s" % (
                ("fold held-out " + name + " (fit on the other anchor)") if name != "POOLED" else "pooled", b0, b1, len(tr),
                int((~tr.right).sum()), int((~tr.right & tr.est).sum()), e1, dd, ident_word(dd, un, e1)))
    mono = int((lo["oof"] > cert.craw_v(E.p) + 1e-12).sum())
    say("    monotonicity: %d edge(s) the widener makes MORE confident (expected 0)" % mono)
    say(c3_status_line(lo["nominal"], lo["wrong"]))
    return res
