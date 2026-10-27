"""POOLED-RESTATE — FRAMEWORK.md item 4, registered by reference at commit eaf1dbf (zero calls).

  python tools/analysis/pooled_restate.py

REGISTRATION (docs/design/FRAMEWORK.md at 8d77f7b, "## Tests to register before shipping", item 4), quoted:
  "POOLED-RESTATE (review verify item 7). Widener vs agreement gate on the pooled board of record, established
  pairs, judged-question denominator, Llama-3.1-8B/command-r excluded, gate at every grid threshold out of fold
  over >= 3 seeds. Criterion: fewer established wrong calls at matched correct surrenders out of fold.
  Prediction: widener + decline. 0 calls."
Review verify item 7 (docs/review_session_2026-09-14.md), quoted:
  "Restate the pooled adoption on established pairs with a fixed key denominator. State which key population
  (3,445 pool / 2,811 judged / 2,646 x20-judged) each script uses; exclude Llama-8B/command-r (p=0.39/0.89) from
  both counts; report the gate at every grid threshold out of fold or over seeds, or drop the 'strictly
  dominates' claim. The 'three independent bootstrap seeds' for the command-r pooled p (RESOLVE_budget.md
  correction 3) is UNVERIFIED: systematic_budget.py:258 uses one seed (43)."

WHAT IS UNDER TEST. The v87 ADOPTED SPLIT (judge_v2_program.md, SYSTEMATIC-BUDGET outcome; RESOLVE_budget.md
correction 4) adopted a plain agreement gate A < 0.85 for the POOLED board on the strength of one in-sample table
on the 66-pair x12 pooled board (gate 61/0/-1 against the widener 57/0/-5). FRAMEWORK.md overrides it with
"widener + decline" pending this test. The item asks whether the widener, at the SAME number of correct
separations surrendered, leaves FEWER established wrong calls than a gate whose threshold is chosen OUT OF FOLD.

READINGS FIXED BEFORE THE RUN (the item is under-specified on each; the reading hardest on the programme's own
claim - that the widener should replace the gate - is taken and named):
  * "the pooled board of record" = the pooled 20-model MERGED board (x12 9,142 + x20 12,394 verdicts, 190 pairs,
    the object FRAMEWORK.md calls "the pooled 20-model board of record"; x20_merged's TIER-HONEST object, 400
    question-resampled draws, seed 42). It is the PRIMARY object. The 66-pair x12 pooled board (300 draws, seed
    43; the object on which the split was adopted and which review item 8 dissects) is run as the SECONDARY
    object so the v87 table is restated on the same footing. Both use B and seed of record for the reproduction
    check, then four further seeds (137, 2048, 7, 31337): FIVE seeds per board.
  * "established pairs" = exact two-sided McNemar p < 0.05 on the two models' per-question correctness, via
    systematic_budget.mcnemar_edge with the pseudo-anchor {'POOLED': all judged questions}; the KEY DENOMINATOR
    is the 2,811 JUDGED questions (never the 3,445 pool). Key accuracy and answer agreement are over the same
    2,811. On established pairs the key-tie DECLINE is the identity (it declines exactly the unestablished
    pairs), so "widener + decline" = widener and "gate + decline" = gate there; the full-board rows (all pairs)
    are printed beside them so the decline's own effect is visible.
  * Meta-Llama-3_1-8B vs c4ai-command-r-v01 is removed from every count EXPLICITLY (it is also unestablished on
    this denominator, p = 0.89; its status is printed per seed, which settles the UNVERIFIED "three seeds" claim).
  * the operating point is 0.975 (RESOLVE-CALIB amendment 2). The gate is applied ON TOP of the raw certificate:
    called iff c_raw >= 0.975 and A < t. The widener: called iff min(c_raw, Phi(|m|/sqrt(s^2+tau(A)^2))) >= 0.975.
  * "every grid threshold" = A < t for t in 0.30, 0.35, ..., 0.95 (the recorded grids 0.70-0.90 pooled and
    0.60-0.85 per anchor are subsets) plus t = 1.00 = "no gate"; a 0.01-step grid is run as a sensitivity.
  * "out of fold" for the gate = LEAVE-BOTH-ENDPOINTS-OUT: for each raw-called established pair (a, b) the
    threshold is chosen on the pairs touching neither a nor b and applied to (a, b). Two selection rules, both
    reported, the first PRIMARY because it is the literal "matched correct surrenders":
      rule M (matched cost): t whose correct-surrender count on the training pairs is closest to the widener's
        on the same pairs; ties -> fewer training wrong calls, then the larger t;
      rule B (best at cost <= widener): t minimising training wrong calls subject to correct surrenders <= the
        widener's; ties -> the larger t (fewest surrenders). Under rule B a fold with no training error can
        legitimately choose "no gate".
      rule P (per-anchor-trained, added so the gate sees the SAME labelled population the LBO-refit widener is
        fitted on): t chosen by rule M on the board's PER-ANCHOR raw-called edges touching neither endpoint
        (x12 891 / merged 2,538 edges; 26+ wrong-direction labels instead of the pooled board's ~5), matched to
        the widener's correct-surrender count on those same edges, then applied to the pooled pair. This is the
        record's own per-anchor "best gate at matched error" procedure (RESOLVE_budget.md correction 4) made
        out of fold.
  * the widener is scored in two variants: SHIPPED (b0, b1 = budget_transfer.B0/B1, fitted on the x12 per-anchor
    edges and applied cold; this is FRAMEWORK.md's actual pooled rule, labelled EXTRAPOLATED there) and LBO-REFIT
    (per pair, refitted on the board's own per-anchor edges excluding every edge touching either endpoint: the
    x12 891 edges for the 66-pair board, budget_transfer's 2,538 merged edges for the 190-pair board), so the
    widener is held to the same out-of-fold standard as the gate. The refit uses a vectorised copy of
    systematic_budget.nll, verified against systematic_budget.fit on the 891 edges before anything is read.
  * CRITERION, scored per (board, seed, widener variant, selection rule): widener established wrong calls
    STRICTLY FEWER than the out-of-fold gate's at matched correct surrenders. A tie (both 0) is NOT "fewer".
    VERDICT: PASS iff the criterion holds on the PRIMARY board in every seed under both widener variants and
    all three selection rules (M, B, P); FAIL iff it fails on the primary board at the seed of record under the shipped widener
    and rule M; UNDETERMINED otherwise. The secondary board is reported with the same table and does not decide
    the verdict, but any cell where the gate beats the widener is named.
  * "strictly dominates" (v87) is re-read the other way round too: at matched WRONG calls, does either rule
    surrender fewer correct calls out of fold?
  * Meta-Llama-3-70B-Instruct is excluded (asserted absent from both rosters). No network, no LLM calls.
    Pooled edge tables are cached under the session scratchpad (block1/). Output: this script's OUT only.
"""
import os, sys, math, random, pickle, time
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.optimize import minimize
from scipy.special import ndtr
import pool_guard
import rubric_p8 as p8
import judge_free_tests as jf
import systematic_budget as sb
import budget_transfer as bt
import x20_replications as xr

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "pooled_restate.txt")
SCRATCH = os.environ.get("PR_CACHE", os.path.join(
    r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena",
    "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad"))
CACHE = os.path.join(SCRATCH, "block1")
KTD_CACHE = os.path.join(SCRATCH, "bigpic")
THRESH = 0.975
ALPHA = 0.05
EXCLUDE = "Meta-Llama-3-70B-Instruct"
EXCL_PAIR = frozenset(("Meta-Llama-3_1-8B", "c4ai-command-r-v01"))
GRID05 = [round(0.30 + 0.05 * i, 2) for i in range(14)] + [1.00]        # 0.30 .. 0.95, 1.00 = no gate
GRID01 = [round(0.30 + 0.01 * i, 2) for i in range(66)] + [1.00]        # 0.30 .. 0.95 step 0.01
SEEDS_MERGED = (42, 137, 2048, 7, 31337)      # 42 = the board of record (x20_merged / key_tie_decline)
SEEDS_X12 = (43, 137, 2048, 7, 31337)         # 43 = systematic_budget.pooled_board's seed of record
B0, B1 = bt.B0, bt.B1


def log(msg):
    print("[pr %s] %s" % (time.strftime("%H:%M:%S"), msg), file=sys.stderr, flush=True)


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


# ---------------------------------------------------------------- pooled board under a given seed
def pooled_edges(rows, models, K, P, qs, seed, B):
    """key_tie_decline.pooled_merged / systematic_budget.pooled_board with the seed and B as parameters; same
    draw order (rng over sorted judged questions), so seed 42 / B 400 reproduces the KTD cache and seed 43 /
    B 300 reproduces systematic_budget.txt's 66-pair table."""
    rng = random.Random(seed)
    byq = defaultdict(list)
    for r in rows:
        byq[r[2]].append(r)
    boards = []
    for _ in range(B):
        pick = [qs[rng.randrange(len(qs))] for _ in qs]
        sub = [r for q in pick for r in byq[q]]
        boards.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                                     for a, b, _, w, _iv in sub], models))
    acc = {m: sum(K[q][m] for q in qs if m in K.get(q, {})) / max(1, sum(1 for q in qs if m in K.get(q, {})))
           for m in models}
    edges = []
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            d = np.array([dr[a] - dr[b] for dr in boards])
            p = float((d > 0).mean())
            both = [q for q in qs if P[q].get(a) and P[q].get(b)]
            agree = sum(1 for q in both if P[q][a] == P[q][b]) / len(both) if both else 0.0
            edges.append(dict(anchor="POOLED", a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                              right=((p > 0.5) == (acc[a] > acc[b])), agree=agree, gap=abs(acc[a] - acc[b]), n=len(both)))
    return edges, acc


# ---------------------------------------------------------------- vectorised widener fit
def vec(es):
    return (np.array([e["agree"] for e in es]), np.array([abs(e["m"]) for e in es]),
            np.array([e["s"] for e in es]), np.array([bool(e["right"]) for e in es]))


def vnll(par, A, M, S, R):
    """Vectorised copy of systematic_budget.nll: same tau clip (20), same 1e-12 clip, same likelihood."""
    b0, b1 = par
    tau = np.exp(np.minimum(20.0, b0 + b1 * A))
    z = M / np.sqrt(S ** 2 + tau ** 2)
    pw = np.clip(ndtr(-z), 1e-12, 1 - 1e-12)
    return float(-(np.where(R, np.log(1 - pw), np.log(pw))).sum())


def vfit(es, x0=(-3.0, 3.0)):
    A, M, S, R = vec(es)
    r = minimize(vnll, np.array(x0), args=(A, M, S, R), method="Nelder-Mead",
                 options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
    return float(r.x[0]), float(r.x[1])


def cw(e, b0, b1):
    return sb.cbud(e, b0, b1)


def pair_key(e):
    return frozenset((e["a"], e["b"]))


# ---------------------------------------------------------------- the analysis of one (board, seed)
def gate_called(e, t):
    return e["agree"] < t


def counts(es, keep):
    """(called, wrong, correct surrendered) of a rule over raw-called established pairs es."""
    called = [e for e in es if keep(e)]
    wrong = sum(1 for e in called if not e["right"])
    right_all = sum(1 for e in es if e["right"])
    return len(called), wrong, right_all - sum(1 for e in called if e["right"])


def select_t(train, wid_c, grid, rule):
    """Choose the gate threshold on the training pairs. wid_c: id(e) -> widener c (already out of fold)."""
    _, _, s_w = counts(train, lambda e: wid_c[id(e)] >= THRESH)
    _, w_w, _ = counts(train, lambda e: wid_c[id(e)] >= THRESH)
    rows = []
    for t in grid:
        _, w_g, s_g = counts(train, lambda e, t=t: gate_called(e, t))
        rows.append((t, w_g, s_g))
    if rule == "M":                          # matched cost: closest surrender count, then fewer wrong, then larger t
        best = min(rows, key=lambda r: (abs(r[2] - s_w), r[1], -r[0]))
    elif rule == "B":                        # best wrong at cost <= widener's, then larger t
        feas = [r for r in rows if r[2] <= s_w] or rows
        best = min(feas, key=lambda r: (r[1], -r[0]))
    elif rule == "W":                        # matched WRONG: fewest surrenders at wrong <= widener's, then larger t
        feas = [r for r in rows if r[1] <= w_w] or rows
        best = min(feas, key=lambda r: (r[2], -r[0]))
    else:
        raise ValueError(rule)
    return best[0], s_w, w_w


def oof_gate(R, wid_c, grid, rule):
    """Leave-both-endpoints-out gate: per pair choose t on the pairs touching neither endpoint, apply to the pair."""
    kept = {}; chosen = Counter()
    for e in R:
        ab = {e["a"], e["b"]}
        train = [f for f in R if f["a"] not in ab and f["b"] not in ab]
        t, _, _ = select_t(train, wid_c, grid, rule)
        chosen[t] += 1
        kept[id(e)] = gate_called(e, t)
    n, w, s = counts(R, lambda e: kept[id(e)])
    return n, w, s, chosen


def oof_gate_peranchor(R, per_anchor, params_of, grid):
    """Rule P: per pooled pair choose t by rule M on the per-anchor RAW-CALLED edges touching neither endpoint
    (the widener's surrender count on those edges computed with params_of(pair): shipped or the pair's LBO refit),
    then apply t to the pooled pair."""
    kept = {}; chosen = Counter()
    for e in R:
        ab = {e["a"], e["b"]}
        train = [f for f in per_anchor if f["a"] not in ab and f["b"] not in ab and sb.craw(f) >= THRESH]
        b0, b1 = params_of(pair_key(e))
        wc = {id(f): cw(f, b0, b1) for f in train}
        t, _, _ = select_t(train, wc, grid, "M")
        chosen[t] += 1
        kept[id(e)] = gate_called(e, t)
    n, w, s = counts(R, lambda e: kept[id(e)])
    return n, w, s, chosen


def lbo_params(per_anchor, pairs):
    """Per pair: (b0, b1) refitted on the per-anchor edges touching neither endpoint."""
    out = {}
    for pk in pairs:
        es = [e for e in per_anchor if e["a"] not in pk and e["b"] not in pk]
        out[pk] = (vfit(es, x0=(B0, B1)), len(es))
    return out


def analyse(L, board, seed, pooled, acc, K, qs, lbo, full_fit, per_anchor):
    aq = {"POOLED": qs}
    mc = {id(e): sb.mcnemar_edge(e, K, aq) for e in pooled}
    ex = [e for e in pooled if pair_key(e) == EXCL_PAIR]
    assert len(ex) == 1
    ex = ex[0]
    est_all = [e for e in pooled if mc[id(e)][0] < ALPHA]
    est = [e for e in est_all if pair_key(e) != EXCL_PAIR]
    allp = [e for e in pooled if pair_key(e) != EXCL_PAIR]
    R = [e for e in est if sb.craw(e) >= THRESH]
    wid = {"SHIPPED": {id(e): cw(e, B0, B1) for e in pooled},
           "LBO-REFIT": {id(e): cw(e, *lbo[pair_key(e)][0]) for e in pooled}}
    L.append("")
    L.append("--- %s | seed %d ---" % (board, seed))
    L.append("  pairs %d | established (McNemar p < %.2f over the %d judged questions) %d | excluded pair %s"
             % (len(pooled), ALPHA, len(qs), len(est_all), "established" if mc[id(ex)][0] < ALPHA else "unestablished"))
    L.append("  Llama-3.1-8B vs command-r: key %.4f vs %.4f (gap %+.4f, McNemar %d:%d p=%.4f) | arena p(8B ahead)=%.4f c_raw=%.4f "
             "widener c=%.4f A=%.3f -> arena %s on the judged denominator; REMOVED from every count below"
             % (acc[ex["a"]], acc[ex["b"]], acc[ex["a"]] - acc[ex["b"]], mc[id(ex)][1], mc[id(ex)][2], mc[id(ex)][0],
                ex["p"], sb.craw(ex), cw(ex, B0, B1), ex["agree"], "right" if ex["right"] else "WRONG"))
    L.append("  established pairs after exclusion %d, wrong-direction %d | raw certificate at %.3f on them: called %d, wrong %d"
             % (len(est), sum(1 for e in est if not e["right"]), THRESH, len(R), sum(1 for e in R if not e["right"])))
    L.append("  the established wrong pairs the raw certificate calls (these are what a rule must remove):")
    for e in sorted(R, key=lambda e: -e["agree"]):
        if not e["right"]:
            L.append("    %-26s vs %-26s A=%.3f c_raw=%.4f |m|=%.3f s=%.3f shipped c=%.4f LBO c=%.4f (b1=%+.3f) McNemar %d:%d p=%.4f"
                     % (e["a"][:26], e["b"][:26], e["agree"], sb.craw(e), abs(e["m"]), e["s"], wid["SHIPPED"][id(e)],
                        wid["LBO-REFIT"][id(e)], lbo[pair_key(e)][0][1], mc[id(e)][1], mc[id(e)][2], mc[id(e)][0]))
    # ---- in-sample table on established raw-called pairs
    L.append("  IN SAMPLE on the %d raw-called established pairs:  %-28s %7s %6s %10s" % (len(R), "rule", "called", "wrong", "corr.surr"))
    n, w, s = counts(R, lambda e: True)
    L.append("    %-50s %7d %6d %10d" % ("raw certificate", n, w, s))
    res = {}
    for v in ("SHIPPED", "LBO-REFIT"):
        n, w, s = counts(R, lambda e, v=v: wid[v][id(e)] >= THRESH)
        res[("wid", v)] = (n, w, s)
        L.append("    %-50s %7d %6d %10d" % ("widener %s" % v + (" (b0 %+.4f b1 %+.4f)" % (B0, B1) if v == "SHIPPED" else " (per-pair refit)"), n, w, s))
    gate_rows = {}
    for t in GRID05:
        n, w, s = counts(R, lambda e, t=t: gate_called(e, t))
        gate_rows[t] = (n, w, s)
        L.append("    %-50s %7d %6d %10d" % ("gate A < %.2f%s" % (t, " (no gate)" if t == 1.0 else ""), n, w, s))
    # ---- full-board context: all pairs (excl. the pair), all(established), decline shown
    L.append("  FULL BOARD context (%d pairs after exclusion; wrong as all(established); decline = drop unestablished):" % len(allp))
    est_ids = {id(e) for e in est}
    def full(keep):
        c = [e for e in allp if keep(e)]
        cd = [e for e in c if id(e) in est_ids]
        return (len(c), sum(1 for e in c if not e["right"]), sum(1 for e in cd if not e["right"]), len(cd), sum(1 for e in cd if not e["right"]))
    for name, keep in [("raw", lambda e: sb.craw(e) >= THRESH),
                       ("widener SHIPPED", lambda e: wid["SHIPPED"][id(e)] >= THRESH),
                       ("widener LBO-REFIT", lambda e: wid["LBO-REFIT"][id(e)] >= THRESH)] + \
                      [("gate A < %.2f" % t, (lambda e, t=t: sb.craw(e) >= THRESH and gate_called(e, t))) for t in (0.70, 0.75, 0.80, 0.85, 0.90)]:
        c, wa, we, cd, wd = full(keep)
        L.append("    %-22s called %3d wrong %2d(%d) | + decline: called %3d wrong %d(%d)" % (name, c, wa, we, cd, wd, wd))
    # ---- out of fold
    L.append("  OUT OF FOLD (leave-both-endpoints-out threshold; grid 0.05 primary, 0.01 sensitivity; rule P trains on the %d per-anchor edges):" % len(per_anchor))
    L.append("    %-10s %-6s %-6s %7s %6s %10s | widener %6s %10s | chosen t" % ("widener", "rule", "grid", "called", "wrong", "corr.surr", "wrong", "corr.surr"))
    for v in ("SHIPPED", "LBO-REFIT"):
        for rule in ("M", "B", "W", "P"):
            for gname, grid in (("0.05", GRID05), ("0.01", GRID01)):
                if rule == "P":
                    params_of = (lambda pk: (B0, B1)) if v == "SHIPPED" else (lambda pk: lbo[pk][0])
                    n, w, s, chosen = oof_gate_peranchor(R, per_anchor, params_of, grid)
                else:
                    n, w, s, chosen = oof_gate(R, wid[v], grid, rule)
                res[("gate", v, rule, gname)] = (n, w, s)
                wn, ww, ws = res[("wid", v)]
                ch = ", ".join("%.2f x%d" % (t, k) for t, k in sorted(chosen.items()))
                L.append("    %-10s %-6s %-6s %7d %6d %10d | %14d %10d | %s" % (v, rule, gname, n, w, s, ww, ws, ch))
    return res, len(est), len(R)


def crit_line(res, v, rule, gname="0.05"):
    wn, ww, ws = res[("wid", v)]; gn, gw, gs = res[("gate", v, rule, gname)]
    if rule in ("M", "B", "P"):
        ok = ww < gw
        return ok, "widener wrong %d (surr %d) vs OOF gate wrong %d (surr %d) -> %s" % (ww, ws, gw, gs, "widener FEWER" if ok else ("TIE" if ww == gw else "GATE FEWER"))
    ok = ws < gs
    return ok, "at matched wrong: widener surr %d (wrong %d) vs OOF gate surr %d (wrong %d) -> %s" % (ws, ww, gs, gw, "widener fewer surrenders" if ok else ("TIE" if ws == gs else "GATE fewer surrenders"))


def main():
    active = pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    L = []
    L.append("[POOL-PIN] active reserved pool %s == pool of record (pool_guard.assert_pool_of_record); questions addressed by explicit id" % active)
    L.append("=== POOLED-RESTATE (FRAMEWORK item 4 / review verify item 7): widener vs agreement gate on the pooled board, "
             "established pairs, judged denominator, Llama-3.1-8B/command-r excluded, gate out of fold over %d seeds ===" % len(SEEDS_MERGED))
    L.append("  operating point %.3f | established = McNemar p < %.2f via systematic_budget.mcnemar_edge over {'POOLED': judged questions}"
             % (THRESH, ALPHA))
    L.append("  KEY DENOMINATOR: the 2,811 JUDGED questions for accuracy, agreement and McNemar on both boards (never the 3,445 pool).")
    L.append("  widener SHIPPED = tau(A) = exp(%+.4f %+.4f*A) (budget_transfer.B0/B1, x12 per-anchor fit, cold) | LBO-REFIT = per pair, "
             "refit on the board's per-anchor edges touching neither endpoint" % (B0, B1))
    L.append("  gate = raw certificate AND A < t; grid t in %s plus 1.00 (no gate); OOF = leave-both-endpoints-out threshold choice"
             % ", ".join("%.2f" % t for t in GRID05[:-1]))
    L.append("  rule M = matched correct surrenders (closest on training pairs); rule B = fewest training wrong at surrenders <= widener's; "
             "rule W = fewest surrenders at wrong <= widener's (the v87 'strictly dominates' direction); "
             "rule P = rule M trained on the per-anchor raw-called edges touching neither endpoint (the LBO widener's own population)")

    # ---------------- data ----------------
    r12, r20, models20, K, P = bt.load()
    assert EXCLUDE not in models20
    models12 = sorted(p8.ARENA12)
    assert EXCLUDE not in models12
    K = dict(K); P = dict(P)
    qs12 = sorted({r[2] for r in r12}); qs20 = sorted({r[2] for r in r12 + r20})
    L.append("")
    L.append("  DATA: x12 %d verdicts on %d questions, %d models | merged x12+x20 %d verdicts on %d questions, %d models | %s absent from both"
             % (len(r12), len(qs12), len(models12), len(r12) + len(r20), len(qs20), len(models20), EXCLUDE))

    # per-anchor fit populations (seed 42 tables from the KEY-TIE-DECLINE cache; single-seed by construction)
    m12c, K12c, P12c, e12_all, aq12 = pickle.load(open(os.path.join(KTD_CACHE, "ktd_x12_edges.pkl"), "rb"))
    e12 = [e for e in e12_all if e["gap"] >= sb.GAP]
    _m20c, _K20c, e_mg, _aq_mg, qs_judged_c, pooled_c, _acc_c, _n12, _n20 = pickle.load(open(os.path.join(KTD_CACHE, "ktd_merged_edges.pkl"), "rb"))
    L.append("  per-anchor fit populations: x12 %d edges (gap >= %.2f, ktd_x12_edges.pkl) | merged %d edges (ktd_merged_edges.pkl); "
             "both from the seed-42 per-anchor bootstrap, one seed only" % (len(e12), sb.GAP, len(e_mg)))

    # ---------------- checks before anything is read ----------------
    t0 = time.time()
    f_sb = sb.fit(e12)
    f_v = vfit(e12)
    L.append("  CHECK vectorised fit vs systematic_budget.fit on the 891 edges: sb (%+.4f, %+.4f) | vec (%+.4f, %+.4f) | shipped (%+.4f, %+.4f) -> %s  [%.0fs]"
             % (f_sb[0], f_sb[1], f_v[0], f_v[1], B0, B1,
                "OK" if max(abs(f_sb[0] - f_v[0]), abs(f_sb[1] - f_v[1])) < 1e-3 and max(abs(f_v[0] - B0), abs(f_v[1] - B1)) < 1e-3 else "MISMATCH",
                time.time() - t0))
    A_, M_, S_, R_ = vec(e12)
    L.append("  CHECK nll at the shipped point: sb %.6f | vec %.6f" % (sb.nll((B0, B1), e12), vnll((B0, B1), A_, M_, S_, R_)))

    # pooled tables per seed (cached)
    tables = {}
    for seed in SEEDS_X12:
        tables[("X12-66", seed)] = cached("pooled_restate_x12_s%d.pkl" % seed,
                                          lambda s=seed: pooled_edges(r12, models12, K, P, qs12, s, sb.B))
    for seed in SEEDS_MERGED:
        tables[("MERGED-190", seed)] = cached("pooled_restate_merged_s%d.pkl" % seed,
                                              lambda s=seed: pooled_edges(r12 + r20, models20, K, P, qs20, s, xr.B))
    # reproduction: seed 42 merged == KTD cache
    e42, _ = tables[("MERGED-190", 42)]
    dmax = max(max(abs(a["p"] - b["p"]), abs(a["m"] - b["m"]), abs(a["s"] - b["s"]), abs(a["agree"] - b["agree"]))
               for a, b in zip(e42, pooled_c))
    rc = [e for e in e42 if sb.craw(e) >= THRESH]; rw = [e for e in rc if not e["right"]]
    L.append("  CHECK merged seed 42 vs key_tie_decline's pooled table: max |diff| in p/m/s/A = %.2e -> %s; raw 0.975 called %d wrong %d(%d) (KTD: 179 / 8(5))"
             % (dmax, "IDENTICAL" if dmax < 1e-9 else "MISMATCH", len(rc), len(rw), len(sb.established(rw, K, {"POOLED": qs20}))))
    # reproduction: seed 43 x12 == systematic_budget.txt (63/1 -> 57/0)
    e43, _ = tables[("X12-66", 43)]
    rc = [e for e in e43 if sb.craw(e) >= THRESH]; bc = [e for e in e43 if cw(e, B0, B1) >= THRESH]
    ai = [e for e in e43 if pair_key(e) == frozenset(("arx_0314", "iask_pro"))][0]
    L.append("  CHECK x12 seed 43 vs systematic_budget.txt: raw %d called / %d wrong -> budget %d / %d (record 63/1 -> 57/0); arx/iask budget c %.4f A %.3f (record 0.7805, 0.880) -> %s"
             % (len(rc), sum(1 for e in rc if not e["right"]), len(bc), sum(1 for e in bc if not e["right"]), cw(ai, B0, B1), ai["agree"],
                "OK" if (len(rc), sum(1 for e in rc if not e["right"]), len(bc), sum(1 for e in bc if not e["right"])) == (63, 1, 57, 0) and abs(cw(ai, B0, B1) - 0.7805) < 5e-4 else "MISMATCH"))

    # LBO widener refits per pair, per board (seed-independent)
    t0 = time.time()
    pairs12 = {pair_key(e) for e in e43}; pairs20 = {pair_key(e) for e in e42}
    lbo12 = cached("pooled_restate_lbo_x12.pkl", lambda: lbo_params(e12, pairs12))
    lbo20 = cached("pooled_restate_lbo_merged.pkl", lambda: lbo_params(e_mg, pairs20))
    full12 = vfit(e12, x0=(B0, B1)); full20 = vfit(e_mg, x0=(B0, B1))
    b1s12 = sorted(v[0][1] for v in lbo12.values()); b1s20 = sorted(v[0][1] for v in lbo20.values())
    L.append("  LBO-REFIT parameters: x12 board, full refit b1 %+.4f, per-pair b1 range [%+.3f, %+.3f] on %d-%d edges | merged board, full refit b1 %+.4f, "
             "per-pair b1 range [%+.3f, %+.3f] on %d-%d edges  [%.0fs]"
             % (full12[1], b1s12[0], b1s12[-1], min(v[1] for v in lbo12.values()), max(v[1] for v in lbo12.values()),
                full20[1], b1s20[0], b1s20[-1], min(v[1] for v in lbo20.values()), max(v[1] for v in lbo20.values()), time.time() - t0))

    # ---------------- analysis ----------------
    results = {}
    L.append("")
    L.append("=== PRIMARY: the pooled 20-model MERGED board of record (190 pairs, %d draws) ===" % xr.B)
    for seed in SEEDS_MERGED:
        pooled, acc = tables[("MERGED-190", seed)]
        results[("MERGED-190", seed)] = analyse(L, "MERGED-190", seed, pooled, acc, K, qs20, lbo20, full20, e_mg)
    L.append("")
    L.append("=== SECONDARY: the pooled 66-pair x12 board on which v87 ADOPTED SPLIT was scored (%d draws) ===" % sb.B)
    for seed in SEEDS_X12:
        pooled, acc = tables[("X12-66", seed)]
        results[("X12-66", seed)] = analyse(L, "X12-66", seed, pooled, acc, K, qs12, lbo12, full12, e12)

    # ---------------- criteria ----------------
    L.append("")
    L.append("=== CRITERION: fewer established wrong calls at matched correct surrenders, out of fold (grid 0.05) ===")
    summary = {}
    for board, seeds in (("MERGED-190", SEEDS_MERGED), ("X12-66", SEEDS_X12)):
        L.append("  %s:" % board)
        for seed in seeds:
            res, n_est, n_R = results[(board, seed)]
            for v in ("SHIPPED", "LBO-REFIT"):
                for rule in ("M", "B", "P"):
                    ok, txt = crit_line(res, v, rule)
                    summary[(board, seed, v, rule)] = ok
                    L.append("    seed %6d %-10s rule %s: %s" % (seed, v, rule, txt))
        L.append("    established pairs %s, raw-called established %s" % (
            "/".join(str(results[(board, s)][1]) for s in seeds), "/".join(str(results[(board, s)][2]) for s in seeds)))
    L.append("  the v87 direction (rule W, matched wrong, fewer correct surrenders):")
    for board, seeds in (("MERGED-190", SEEDS_MERGED), ("X12-66", SEEDS_X12)):
        for seed in seeds:
            res, _, _ = results[(board, seed)]
            for v in ("SHIPPED", "LBO-REFIT"):
                ok, txt = crit_line(res, v, "W")
                L.append("    %-10s seed %6d %-10s: %s" % (board, seed, v, txt))
    # sensitivity: 0.01 grid
    L.append("  sensitivity, 0.01 grid (rules M, B and P), cells where the reading differs from the 0.05 grid:")
    diffs = 0
    for board, seeds in (("MERGED-190", SEEDS_MERGED), ("X12-66", SEEDS_X12)):
        for seed in seeds:
            res, _, _ = results[(board, seed)]
            for v in ("SHIPPED", "LBO-REFIT"):
                for rule in ("M", "B", "P"):
                    ok1, txt1 = crit_line(res, v, rule, "0.01")
                    if ok1 != summary[(board, seed, v, rule)]:
                        diffs += 1
                        L.append("    %-10s seed %6d %-10s rule %s (0.01 grid): %s" % (board, seed, v, rule, txt1))
    if not diffs:
        L.append("    none - every cell reads the same on the 0.01 grid")

    RULES = ("M", "B", "P")
    prim_all = all(summary[("MERGED-190", s, v, r)] for s in SEEDS_MERGED for v in ("SHIPPED", "LBO-REFIT") for r in RULES)
    prim_rec = summary[("MERGED-190", 42, "SHIPPED", "M")]
    sec_all = all(summary[("X12-66", s, v, r)] for s in SEEDS_X12 for v in ("SHIPPED", "LBO-REFIT") for r in RULES)
    sec_any_gate_better = False
    for s in SEEDS_X12:
        res, _, _ = results[("X12-66", s)]
        for v in ("SHIPPED", "LBO-REFIT"):
            for r in RULES:
                if res[("wid", v)][1] > res[("gate", v, r, "0.05")][1]:
                    sec_any_gate_better = True
    verdict = "PASS" if prim_all else ("FAIL" if not prim_rec else "UNDETERMINED")
    L.append("")
    NC = 2 * len(RULES)
    L.append("=== VERDICT (scored on the PRIMARY board; %d seeds x 2 widener variants x %d rules = %d cells) ===" % (len(SEEDS_MERGED), len(RULES), NC * len(SEEDS_MERGED)))
    L.append("  primary board: criterion holds in %d of %d cells; at the seed of record under the shipped widener and rule M: %s"
             % (sum(1 for s in SEEDS_MERGED for v in ("SHIPPED", "LBO-REFIT") for r in RULES if summary[("MERGED-190", s, v, r)]),
                NC * len(SEEDS_MERGED), "holds" if prim_rec else "fails"))
    L.append("  secondary (66-pair) board: criterion holds in %d of %d cells; a cell where the OOF gate has FEWER wrong than the widener: %s"
             % (sum(1 for s in SEEDS_X12 for v in ("SHIPPED", "LBO-REFIT") for r in RULES if summary[("X12-66", s, v, r)]),
                NC * len(SEEDS_X12), "yes" if sec_any_gate_better else "none"))
    L.append("  -> %s" % verdict)
    L.append("  PREDICTION 'widener + decline': %s on the board of record%s"
             % ("HELD" if prim_all else ("FAILED" if verdict == "FAIL" else "NOT DECIDED"),
                "" if sec_all else "; on the 66-pair object the widener and the out-of-fold gate TIE at 0 established wrong in at least one cell, "
                                   "so 'fewer' is not met there and neither rule 'strictly dominates' the other on that object"))
    L.append("  on established pairs the key-tie decline is the identity, so these numbers are 'widener + decline' vs 'gate + decline'; the")
    L.append("  full-board rows show the decline's own effect (it removes the unestablished wrong calls on both bases).")

    txt = "\n".join(L)
    print(txt)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    main()
