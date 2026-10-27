"""ITEM-26-POOLED + RE-JUDGE-RULE — does pooling the established labels of the two draws of the same judge on identical
bytes identify b1, and which re-judge triggers does the record support? (zero judge calls; registered 2026-09-17 at
commit 62c4084 in docs/judge_v2_program.md L5458-L5521 BEFORE this script was written; plan Amendment 4 in the same commit.)

  python tools/analysis/item26_pooled.py --dry-run             # pool id first; caches inspected mode=ro; data objects and
                                                               #   denominators only; NO outcome number; nothing written
  python tools/analysis/item26_pooled.py --selftest            # the estimators on SYNTHETIC edges (a planted b1 / b2 recovered;
                                                               #   the vectorised likelihood equals systematic_budget.nll); no cache read
  python tools/analysis/item26_pooled.py --run [--boot 300] [--sims 1000] [--out <path>]
                                                               # the readout; refuses on a row-count mismatch; write-once: refuses
                                                               #   if the outcome file exists; writes
                                                               #   experiment_results/x12_crossdomain/item26_pooled_outcome.txt

QUESTION (registration). FRAMEWORK item 26's criterion "b1 identified on established labels" was met on GROK-CALIB's draw
(established-label refit b1 +2.72, delta-deviance 4.47 > 3.84) and NOT met on the Kotlin draw of the identical judge on
identical bytes (JUDGE-WIRING-BOARD: +2.05, 2.26 < 3.84), at ~26 established wrong-direction events each. On the pooled
established labels of BOTH draws (~52 events), fitted with a draw indicator as a scale term and a bootstrap clustered by
question, is b1 identified at 3.84, and with what power? Second half, a rule not a measurement: the re-judge triggers the
record supports (docs/plan_2026-09-15.md Amendment 4; this script only prints them and checks the amendment is on disk).

HYGIENE. ONE judge (grok-4-1-fast-non-reasoning, STACK-v2, cap 8192, temperature omitted, dual order), ONE reference vintage
(judge_solve/grok-reasoning.db), TWO DRAWS on byte-identical prompts (posted-byte sha equality 9,123 / 9,123 in both orders,
JUDGE-WIRING-BOARD). Nothing else is pooled: no Mistral edge, no second judge, no second vintage, no other cache. Caches
mode=ro, row counts pinned: grok_calib.db 9,142 (11 INVALID), kotlin_c0d3f708cbc3930e.db 9,123 (17 INVALID). BOTH draws are
restricted to the 9,123 shared matches (the 19 reference-less GROK-CALIB matches on 10 questions dropped; those questions
have no other match, so the two edge populations are built on the same matches: expected 890 filtered / 918 unfiltered
edges per draw, 810 established, printed and asserted equal across draws up to the draw's own INVALID rows). Established
labels by systematic_budget.mcnemar_edge on the anchor's JUDGED questions (the draw's valid rows, as the record's
item26_criteria read them); the label and the agreement covariate A are properties of the edge, identical across draws
up to INVALID rows (the disagreement count is printed and the pooled established set is the intersection); only m and s
(the judge's bootstrap moments) differ. INVALID = the cache's `invalid` column exactly as systematic_budget.build reads it
(the record's 4.47 / 2.26 were read that way); the rows rule 10 would additionally reclassify (finish_reason length /
content_filter / empty) are COUNTED and printed, not applied, so the single-draw reproduction is byte-faithful. No key
input at inference (A only). Free parameters: b0, b1, b2 = 3, the SYSTEMATIC-BUDGET criterion (4) ceiling exactly.

INSTRUMENT. systematic_budget's helpers (build's edge construction reproduced on the restricted rows and asserted equal to
sb.build on the Kotlin draw, mcnemar_edge, established, nll, fit, craw) extended by ONE term:
    tau(A, D) = exp(b0 + b1*A + b2*D),  D = 0 for the GROK-CALIB draw, 1 for the Kotlin draw,
fitted on the union of the two draws' established edges (each edge appears twice, once per draw, with its own m and s).
Identification: delta-deviance of b1 = 0 (b0, b2 free) against b1 free, read at 3.84; both single-draw values of record
(4.47 / 2.26) and both single-draw b1 (+2.72 / +2.05) printed beside, with the same single-draw refits on the restricted
population. Pooled b1 with a question-clustered bootstrap interval (questions resampled within anchor, both draws' boards
rebuilt from the same resample with the record's 300 inner bootstrap draws, B = 300 outer, percentile 2.5 / 97.5).
Power: parametric simulation from the fitted pooled model at true b1 = +2.7 (b0, b2 at their fits), 1,000 simulated label
sets on each single-draw established population (~26 events) and on the pooled one (~52), P(delta-deviance >= 3.84).
LOAO at 0.975 on the pooled fit (folds fitted on the established edges of the other 13 anchors, both draws): called /
wrong(established) / nominal per draw and pooled (the pooled nominal counts each edge twice and says so); utility =
LOAO-called / ALL edges of the draw's population (Amendment 1 D6); scored on the unfiltered population (UNFILTERED-ADOPT),
the key-gap >= 0.02 population printed beside.

CRITERIA (scored HELD / FAILED):  (C1) pooled delta-deviance >= 3.84 -> b1 identified on the pooled established labels;
< 3.84 -> NOT identified, every grok cell BANDED-JUDGED.  (C2) the power statement at ~26 and ~52 events, printed whatever
C1 does.  (C3) LOAO on the pooled fit per draw and pooled; status by the power rule (nominal < 3 -> UNDETERMINED).
(C4) utility >= 60% per draw.
PREDICTIONS (blind): pooled delta-deviance 3.5-5.5; LOAO wrong 2-4 (established 1-2) per draw; nominal ~2.2; status
UNDETERMINED; registrar's addition b2 within [-1, +1].
FALSIFIER: pooled delta-deviance < 2.5 (item 26's criterion unmet on the evidence, every grok-judged cell BANDED-JUDGED).

OUTPUT. experiment_results/x12_crossdomain/item26_pooled_outcome.txt (the file of record, bracketed in the registration at
1534a4a), written ONCE from both complete caches: --run refuses ([ONCE]) if the file exists, --out is guarded the same way;
--dry-run writes nothing.
"""
import os, sys, math, json, random, sqlite3, argparse, time
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import norm
import pool_guard
import rejudge_grok as rj
import judge_free_tests as jf
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import systematic_budget as sb

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

POOL = pool_guard.MMLU_PRO_POOL                    # p2dca21ab5f4ef3ae
TREE = "bareq512_s42"
X12DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
DRAWS = {                                          # D -> (name, path, pinned rows, pinned INVALID)
    0: ("GROK-CALIB", os.path.join(X12DIR, "grok_calib.db"), 9142, 11),
    1: ("KOTLIN", os.path.join(ROOT, "experiment_results", "judge_wiring", "board", "kotlin_c0d3f708cbc3930e.db"), 9123, 17),
}
N_SHARED = 9123; N_DROPPED = 19; N_DROPPED_Q = 10
RECORD = {0: dict(b1=2.7194, ddev=4.47, src="grok_calib_outcome.txt L11/L14"),
          1: dict(b1=2.0451, ddev=2.26, src="judge_wiring/board_outcome.txt L45/L48")}
EXPECTED_EDGES = dict(filtered=890, unfiltered=918, established=810)   # the registration's expectation per draw
NON_TERMINATED = {"length", "content_filter", ""}
THRESH = sb.THRESH; GAP = sb.GAP; B_INNER = sb.B                        # 0.975, 0.02, 300: the record's
B_OUTER = 300; N_SIM = 1000; TRUE_B1 = 2.7; CHI1 = 3.84; SEED = 42
OUT = os.path.join(X12DIR, "item26_pooled_outcome.txt")
PLAN = os.path.join(ROOT, "docs", "plan_2026-09-15.md")
TRIGGERS = [
    "TRIGGER: judge fingerprint change (deployment / model id of the judge).",
    "TRIGGER: reference vintage change on a question (a new cached solve for that question).",
    "TRIGGER: canary alarm (CANARY-BASELINE; pass 2 >= 2026-09-22).",
    "NOT a trigger: tree re-celling while the anchor-rubric bytes are held fixed (verdicts depend on the tree only through the rubric, "
    "+0.2pp of discrimination, STACK-NORUBRIC; a regenerated rubric is a prompt-hash change, guard 11).",
    "NOT a trigger: provider re-draw alone (whole-board agreement inside 1.9pp, JUDGE-WIRING-BOARD).",
    "Every re-judge is read on identical matches, both conventions, question-clustered CI, floor ~1.9pp below 1,000 matches.",
]


def rel(p):
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:                      # a --out on another drive (Windows): print it absolute
        return p


def ro(path):
    if not os.path.isfile(path):
        raise SystemExit("[ITEM-26-POOLED] cache not found: %s" % path)
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


# ── data objects ───────────────────────────────────────────────────────────────────────────────────────────────

class Data:
    """Both draws, restricted to the shared matches; the key and predictions of the 12 contestants; the routing."""

    def __init__(self, log):
        self.log = log
        self.models = sorted(p8.ARENA12)
        self.raw = {}
        for D, (name, path, pinned, pinned_inv) in DRAWS.items():
            con = ro(path)
            cols = [c[1] for c in con.execute("PRAGMA table_info(verdicts)")]
            has_fin = "finish1" in cols
            rows = con.execute("SELECT match_id, model_a, model_b, qid, winner, invalid, ref_correct"
                               + (", finish1, finish2" if has_fin else ", NULL, NULL") + " FROM verdicts").fetchall()
            con.close()
            if len(rows) != pinned:
                raise SystemExit("[ITEM-26-POOLED] %s holds %d verdict rows, the record pins %d: refusing" % (name, len(rows), pinned))
            ninv = sum(int(r[5] or 0) for r in rows)
            if ninv != pinned_inv:
                raise SystemExit("[ITEM-26-POOLED] %s holds %d INVALID rows, the record pins %d: refusing" % (name, ninv, pinned_inv))
            rule10 = sum(1 for r in rows if has_fin and not int(r[5] or 0) and ((r[7] or "") in NON_TERMINATED or (r[8] or "") in NON_TERMINATED))
            self.raw[D] = {int(r[0]): (r[1], r[2], int(r[3]), r[4], int(r[5] or 0), -1 if r[6] is None else int(r[6])) for r in rows}
            log("draw D=%d %-10s %s | %d rows (pinned %d) | INVALID %d (pinned %d) | rule-10 would reclassify %d more (COUNTED, not applied: "
                "the record's single-draw values used the invalid column only)" % (D, name, os.path.relpath(path, ROOT), len(rows), pinned, ninv, pinned_inv, rule10))
        gc, kt = self.raw[0], self.raw[1]
        self.shared = sorted(set(kt))
        if len(self.shared) != N_SHARED or not set(kt) <= set(gc):
            raise SystemExit("[ITEM-26-POOLED] the Kotlin match ids (%d) are not a subset of GROK-CALIB's of size %d" % (len(kt), N_SHARED))
        dropped = sorted(set(gc) - set(kt))
        dq = sorted({gc[m][2] for m in dropped})
        if len(dropped) != N_DROPPED or len(dq) != N_DROPPED_Q or any(gc[m][5] != -1 for m in dropped) or set(dq) & {gc[m][2] for m in self.shared}:
            raise SystemExit("[ITEM-26-POOLED] the GROK-CALIB minus Kotlin set is not the 19 reference-less matches on 10 questions with no other match")
        self.dropped, self.dropped_q = dropped, dq
        for m in self.shared:
            if (gc[m][0], gc[m][1], gc[m][2]) != (kt[m][0], kt[m][1], kt[m][2]):
                raise SystemExit("[ITEM-26-POOLED] match %d differs between the draws (models / question)" % m)
        log("shared matches %d = every Kotlin match; GROK-CALIB rows dropped %d (reference-less; match_ids %s; qids %s); both draws now sit on the same %d matches"
            % (len(self.shared), len(dropped), dropped, dq, len(self.shared)))
        # verdict rows per draw as systematic_budget.build reads them: (model_a, model_b, qid, winner), invalid rows dropped
        self.rows = {D: [(r[0], r[1], r[2], r[3]) for m in self.shared for r in [self.raw[D][m]] if not r[4]] for D in DRAWS}
        # key and predictions of the 12 contestants (systematic_budget.build's K and P)
        ev = ro(rj.EVAL_DB)
        self.K = defaultdict(dict); self.P = defaultdict(dict)
        for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
            if m in p8.ARENA12:
                self.K[q][m] = int(c or 0); self.P[q][m] = (pr or "").strip().upper()[:1]
        ev.close()
        self.route = r512.primary_routing(TREE)
        nodes = r512.load_graph(r512.snapshot_id(TREE)); self.anchor_of = r512.anchor_fn(nodes)
        qs = sorted({r[2] for r in self.rows[0]} | {r[2] for r in self.rows[1]})
        pool_guard.assert_scored_subset(POOL, qs, out=sys.stdout)
        unrouted = [q for q in qs if q not in self.route]
        if unrouted:
            raise SystemExit("[ITEM-26-POOLED] %d judged questions have no route in %s" % (len(unrouted), TREE))
        self.by = {D: by_anchor(self.rows[D], self.route, self.anchor_of) for D in DRAWS}
        self.anchors = sorted(self.by[0])
        if sorted(self.by[1]) != self.anchors:
            raise SystemExit("[ITEM-26-POOLED] the two draws do not carry the same anchors")


def by_anchor(rows, route, anchor_of):
    by = defaultdict(list)
    for a, b, q, w in rows:
        if q in route:
            by[anchor_of(route[q])].append((a, b, q, w))
    return {anc: rs for anc, rs in by.items() if len(rs) >= 200}          # sb.build's support rule


def build_edges(by, K, P, models, rng, B=B_INNER, qmap=None):
    """systematic_budget.build's per-anchor edge construction on explicit rows: the same draw order (one Random, anchors
    ascending, B picks of len(qs) questions each), the same first two moments, the same key direction and agreement.
    qmap maps a (pseudo-)qid to the key/prediction qid (the outer bootstrap gives each resampled copy its own cluster id)."""
    kq = (lambda q: q) if qmap is None else (lambda q: qmap[q])
    edges = []; anchor_qs = {}
    for anc in sorted(by):
        rs = by[anc]
        qs = sorted({q for _, _, q, _ in rs}); anchor_qs[anc] = qs
        byq = defaultdict(list)
        for r in rs:
            byq[r[2]].append(r)
        draws = []
        for _ in range(B):
            pick = [qs[rng.randrange(len(qs))] for _ in qs]
            sub = [r for q in pick for r in byq[q]]
            draws.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in sub], models))
        la = {}
        for m in models:
            v = [K[kq(q)].get(m) for q in qs if K[kq(q)].get(m) is not None]
            if v:
                la[m] = sum(v) / len(v)
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if a not in la or b not in la:
                    continue
                gap = abs(la[a] - la[b])
                if gap == 0:
                    continue
                d = np.array([dr[a] - dr[b] for dr in draws])
                p = float((d > 0).mean())
                both = [q for q in qs if P[kq(q)].get(a) and P[kq(q)].get(b)]
                if not both:
                    continue
                agree = sum(1 for q in both if P[kq(q)][a] == P[kq(q)][b]) / len(both)
                edges.append(dict(anchor=anc, a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                                  right=((p > 0.5) == (la[a] > la[b])), agree=agree, gap=gap, n=len(both)))
    return edges, anchor_qs


def edge_key(e):
    return (e["anchor"], e["a"], e["b"])


def replicate(anchors, anchor_qs_shared, byq, K, P, models, rng, B=B_INNER):
    """ONE outer bootstrap replicate: questions resampled within anchor from the shared match set; every picked copy gets
    its own pseudo-qid (q, i) so duplicates are separate clusters; both draws rebuilt from the same picks.
    build_edges receives the ORIGINAL-keyed K / P plus qmap (it maps a pseudo-qid back before indexing); mcnemar_edge
    walks the pseudo anchor_qs, so it receives Kb keyed by pseudo-qid. (The run of 866812d passed Kb to build_edges too
    -> KeyError on the first replicate; fixed here and exercised by --selftest [8].)
    Returns (edges per draw, established edge keys per draw, qmap)."""
    qmap = {}; by_b = {D: defaultdict(list) for D in byq}
    for anc in anchors:
        qs = anchor_qs_shared[anc]
        for i in range(len(qs)):
            q = qs[rng.randrange(len(qs))]; pq = (q, i); qmap[pq] = q
            for D in byq:
                for a, bb, _, wv in byq[D][q]:
                    by_b[D][anc].append((a, bb, pq, wv))
    Kb = {pq: K[q] for pq, q in qmap.items()}
    Eb = {}; estb = {}
    for D in byq:
        Eb[D], AQb = build_edges({a: rs for a, rs in by_b[D].items() if len(rs) >= 200}, K, P, models, random.Random(SEED), B=B, qmap=qmap)
        estb[D] = {edge_key(e) for e in sb.established(Eb[D], Kb, AQb)}
    return Eb, estb, qmap


def edge_population(by, K, P, models):
    """The edge denominators WITHOUT the bootstrap (dry-run): (anchor, a, b, gap, agree) for every pair sb.build keeps."""
    out = []
    for anc in sorted(by):
        qs = sorted({q for _, _, q, _ in by[anc]})
        la = {}
        for m in models:
            v = [K[q].get(m) for q in qs if K[q].get(m) is not None]
            if v:
                la[m] = sum(v) / len(v)
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if a not in la or b not in la or la[a] == la[b]:
                    continue
                both = [q for q in qs if P[q].get(a) and P[q].get(b)]
                if not both:
                    continue
                out.append(dict(anchor=anc, a=a, b=b, gap=abs(la[a] - la[b]),
                                agree=sum(1 for q in both if P[q][a] == P[q][b]) / len(both)))
    return out


# ── the pooled model ───────────────────────────────────────────────────────────────────────────────────────────

def arrays(es):
    """(A, D, |m|, s, wrong) as numpy arrays; D defaults to 0 for single-draw edge lists."""
    return (np.array([e["agree"] for e in es]), np.array([float(e.get("D", 0)) for e in es]),
            np.array([abs(e["m"]) for e in es]), np.array([e["s"] for e in es]), np.array([0.0 if e["right"] else 1.0 for e in es]))


def nll3(par, A, D, am, s, wrong):
    """Wrong-direction likelihood with tau(A, D) = exp(b0 + b1 A + b2 D); equals systematic_budget.nll at b2 = 0, D = 0
    (asserted in --selftest and on the record edges in --run)."""
    b0, b1, b2 = par
    tau = np.exp(np.minimum(20.0, b0 + b1 * A + b2 * D))
    z = am / np.sqrt(s ** 2 + tau ** 2)
    pw = np.clip(norm.cdf(-z), 1e-12, 1 - 1e-12)
    return float(-(wrong * np.log(pw) + (1 - wrong) * np.log(1 - pw)).sum())


def fit3(arr, x0=(-3.0, 3.0, 0.0), fix_b1=False, fix_b2=False):
    """Nelder-Mead as systematic_budget.fit (xatol 1e-6, fatol 1e-8); fix_b1 pins b1 = 0 (the null), fix_b2 pins b2 = 0
    (the single-draw form). Returns (b0, b1, b2, nll)."""
    A, D, am, s, wrong = arr
    free = [i for i, f in enumerate((False, fix_b1, fix_b2)) if not f]
    def obj(x):
        par = [0.0, 0.0, 0.0]
        for i, v in zip(free, x): par[i] = v
        return nll3(par, A, D, am, s, wrong)
    r = minimize(obj, np.array([x0[i] for i in free]), method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
    par = [0.0, 0.0, 0.0]
    for i, v in zip(free, r.x): par[i] = float(v)
    return par[0], par[1], par[2], float(r.fun)


def ddev(arr, pooled):
    """delta-deviance of b1 = 0 against b1 free (b0, and b2 when pooled, free in both). Returns (full, null, delta)."""
    full = fit3(arr, fix_b2=not pooled)
    null = fit3(arr, x0=(full[0], 0.0, full[2]), fix_b1=True, fix_b2=not pooled)
    return full, null, 2 * (null[3] - full[3])


def cbud3(e, b0, b1, b2):
    tau = math.exp(b0 + b1 * e["agree"] + b2 * e.get("D", 0))
    return min(sb.craw(e), float(norm.cdf(abs(e["m"]) / math.sqrt(e["s"] ** 2 + tau ** 2))))


def loao(es_all_by_D, est_ids, x0):
    """Leave-one-anchor-out on the pooled fit: folds fitted on the established edges (both draws) of the other anchors,
    evaluated on EVERY edge of the held-out anchor in both draws. Returns {D: {id(e): c_oof}}."""
    ancs = sorted({e["anchor"] for D in es_all_by_D for e in es_all_by_D[D]})
    oof = {D: {} for D in es_all_by_D}
    for A_ in ancs:
        tr = [e for D in es_all_by_D for e in es_all_by_D[D] if e["anchor"] != A_ and id(e) in est_ids]
        f = fit3(arrays(tr), x0=x0)
        for D in es_all_by_D:
            for e in es_all_by_D[D]:
                if e["anchor"] == A_:
                    oof[D][id(e)] = cbud3(e, f[0], f[1], f[2])
    return oof


def power_status(nominal, wrong):
    """FRAMEWORK.md L101 status word; 'calibrated' is never emitted."""
    if nominal < 3:
        return "UNDETERMINED (power rule: nominal < 3)"
    if nominal < 9:
        return "UNDETERMINED (power: 2x undetectable)"
    from scipy.stats import poisson
    return "NOT DETECTABLY MISCALIBRATED" if poisson.sf(wrong - 1, nominal) > 0.05 else "MISCALIBRATED"


def simulate_power(es, b0, b1_true, b2, pooled, n_sim, rng):
    """Parametric: labels ~ Bernoulli(P(wrong)) under (b0, b1_true, b2) on the given established population; each set
    refitted full vs null; P(delta-deviance >= 3.84). Returns (rate, mean simulated events)."""
    A, D, am, s, _ = arrays(es)
    tau = np.exp(b0 + b1_true * A + b2 * D)
    pw = norm.cdf(-am / np.sqrt(s ** 2 + tau ** 2))
    hits = 0; events = 0.0
    for _ in range(n_sim):
        wrong = (rng.random(len(es)) < pw).astype(float)
        events += wrong.sum()
        if wrong.sum() == 0:
            continue
        _, _, dd = ddev((A, D, am, s, wrong), pooled)
        hits += dd >= CHI1
    return hits / n_sim, events / n_sim


# ── dry-run ────────────────────────────────────────────────────────────────────────────────────────────────────

def dry_run():
    print("reserved_pool_id=%s" % POOL)
    pool_guard.assert_pool_of_record(POOL)
    print("[DRY-RUN] ITEM-26-POOLED + RE-JUDGE-RULE | zero judge calls | caches opened mode=ro | nothing written | no outcome number below")
    d = Data(lambda s: print("  " + s))
    print("  contestants (systematic_budget's ARENA12): %d | tree %s | anchors with >= 200 valid rows: %d" % (len(d.models), TREE, len(d.anchors)))
    print("  %-17s %10s %10s %10s %10s | %s" % ("anchor", "rows D=0", "rows D=1", "qs D=0", "qs D=1", "qs symmetric difference (INVALID rows only)"))
    for anc in d.anchors:
        q0 = {r[2] for r in d.by[0][anc]}; q1 = {r[2] for r in d.by[1][anc]}
        print("  %-17s %10d %10d %10d %10d | %d" % (anc, len(d.by[0][anc]), len(d.by[1][anc]), len(q0), len(q1), len(q0 ^ q1)))
    for D in DRAWS:
        pop = edge_population(d.by[D], d.K, d.P, d.models)
        filt = [e for e in pop if e["gap"] >= GAP]
        aq = {anc: sorted({q for _, _, q, _ in d.by[D][anc]}) for anc in d.by[D]}
        est = sum(1 for e in pop if sb.mcnemar_edge(e, d.K, aq)[0] < 0.05)
        print("  draw D=%d %-10s edge population: %d unfiltered (registration expects %d) | %d with key gap >= %.2f (expects %d) | %d established by mcnemar_edge (expects %d)"
              % (D, DRAWS[D][0], len(pop), EXPECTED_EDGES["unfiltered"], len(filt), GAP, EXPECTED_EDGES["filtered"], est, EXPECTED_EDGES["established"]))
    p0 = {(e["anchor"], e["a"], e["b"]): e for e in edge_population(d.by[0], d.K, d.P, d.models)}
    p1 = {(e["anchor"], e["a"], e["b"]): e for e in edge_population(d.by[1], d.K, d.P, d.models)}
    common = set(p0) & set(p1)
    print("  edges in both draws %d | only D=0 %d | only D=1 %d | max |A(D=0) - A(D=1)| over common edges %.4f"
          % (len(common), len(set(p0) - common), len(set(p1) - common), max(abs(p0[k]["agree"] - p1[k]["agree"]) for k in common) if common else 0.0))
    print("  record values printed beside the pooled readout: D=0 b1 %+.4f, delta-dev %.2f (%s); D=1 b1 %+.4f, delta-dev %.2f (%s)"
          % (RECORD[0]["b1"], RECORD[0]["ddev"], RECORD[0]["src"], RECORD[1]["b1"], RECORD[1]["ddev"], RECORD[1]["src"]))
    print("  instrument: tau(A, D) = exp(b0 + b1 A + b2 D), 3 free parameters; inner bootstrap B=%d (the record's); outer question bootstrap B=%d; power sims %d at b1=%+.1f; LOAO at %.3f; utility over ALL edges (D6)"
          % (B_INNER, B_OUTER, N_SIM, TRUE_B1, THRESH))
    print("  runtime estimate for --run: one outer replicate (both draws, 14 anchors x %d BT fits each) 29 s measured on the record; outer bootstrap %d replicates ~%.0f min; power sims %d x 3 populations x 2 fits (~0.04 s each) ~%.0f min"
          % (B_INNER, B_OUTER, B_OUTER * 29 / 60, N_SIM, N_SIM * 3 * 2 * 0.04 / 60))
    print("  Amendment 4 on disk in %s: %s" % (os.path.relpath(PLAN, ROOT), "yes" if amendment_present() else "NO"))
    print("[DRY-RUN] done: no outcome computed. Run with --run after the registration is committed.")


def amendment_present():
    try:
        return any(l.startswith("## Amendment 4") for l in open(PLAN, encoding="utf-8"))
    except OSError:
        return False


# ── the readout ────────────────────────────────────────────────────────────────────────────────────────────────

def readout(boot, sims, out_path):
    if os.path.exists(out_path):
        raise SystemExit("[ONCE] %s exists: the outcome file of record is written once, from both complete caches; never overwritten (correct by insertion in the record, not by re-running)" % rel(out_path))
    L = []
    def w(s=""):
        L.append(s); print(s, flush=True)
    w("reserved_pool_id=%s" % POOL)
    pool_guard.assert_pool_of_record(POOL)
    w("=== ITEM-26-POOLED + RE-JUDGE-RULE (registered 2026-09-17, commit 62c4084, docs/judge_v2_program.md L5458-L5521; zero judge calls) ===")
    w("  judge grok-4-1-fast-non-reasoning | STACK-v2 | cap 8192 | temperature omitted | dual order | reference judge_solve/grok-reasoning.db")
    d = Data(lambda s: w("  " + s))
    t0 = time.time()
    # (1) the two draws' edges on the shared matches, and the fidelity check against sb.build on the Kotlin draw
    E = {}; AQ = {}
    for D in DRAWS:
        E[D], AQ[D] = build_edges(d.by[D], d.K, d.P, d.models, random.Random(SEED))
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    mem = sqlite3.connect(":memory:")
    mem.execute("CREATE TABLE verdicts (model_a TEXT, model_b TEXT, qid INTEGER, winner TEXT, invalid INTEGER)")
    mem.executemany("INSERT INTO verdicts VALUES (?, ?, ?, ?, 0)", d.rows[1])
    sj.open_cache = lambda: mem
    _, _, _, _, e_rec, aq_rec = sb.build()
    key = lambda e: (e["anchor"], e["a"], e["b"])
    rec = {key(e): e for e in e_rec}
    diffs = [abs(rec[key(e)]["m"] - e["m"]) + abs(rec[key(e)]["s"] - e["s"]) + abs(rec[key(e)]["agree"] - e["agree"]) for e in E[1]]
    if len(rec) != len(E[1]) or max(diffs) > 1e-12 or aq_rec != AQ[1]:
        raise SystemExit("[ITEM-26-POOLED] build_edges does not reproduce systematic_budget.build on the Kotlin draw (max diff %.3g)" % max(diffs))
    w("  fidelity: build_edges reproduces systematic_budget.build on the Kotlin draw edge for edge (%d edges; max |dm|+|ds|+|dA| %.1e)" % (len(E[1]), max(diffs)))
    # labels: established per draw, asserted equal across draws up to INVALID rows
    est = {D: {key(e) for e in sb.established(E[D], d.K, AQ[D])} for D in DRAWS}
    keys = {D: {key(e) for e in E[D]} for D in DRAWS}
    common = keys[0] & keys[1]
    lab_dis = sorted(k for k in common if (k in est[0]) != (k in est[1]))
    e0 = {key(e): e for e in E[0]}; e1 = {key(e): e for e in E[1]}
    dA = max(abs(e0[k]["agree"] - e1[k]["agree"]) for k in common)
    qdiff = sum(len(set(AQ[0][a]) ^ set(AQ[1][a])) for a in d.anchors)
    for D in DRAWS:
        filt = [e for e in E[D] if e["gap"] >= GAP]
        w("  draw D=%d %-10s edges %d unfiltered / %d filtered (gap >= %.2f) | established %d | wrong-direction: %d of the established (the events), %d of all"
          % (D, DRAWS[D][0], len(E[D]), len(filt), GAP, len(est[D]), sum(1 for e in E[D] if key(e) in est[D] and not e["right"]), sum(1 for e in E[D] if not e["right"])))
    w("  across draws: edges common %d | only D=0 %d | only D=1 %d | anchor question sets differ by %d questions (INVALID rows) | established-label disagreements %d%s | max |dA| %.4f"
      % (len(common), len(keys[0] - common), len(keys[1] - common), qdiff, len(lab_dis), (": " + "; ".join("%s %s vs %s" % k for k in lab_dis[:10])) if lab_dis else "", dA))
    est_both = (est[0] & est[1])
    w("  pooled established set = edges established in BOTH draws: %d (each enters twice, once per draw, with its own m and s)" % len(est_both))
    # (2) single-draw refits on the restricted population beside the record
    w(""); w("=== (2) single-draw identification on the restricted population, beside the record ===")
    single = {}
    for D in DRAWS:
        es = [e for e in E[D] if key(e) in est[D]]
        b0, b1 = sb.fit(es, x0=sb.fit([e for e in E[D] if e["gap"] >= GAP]))
        null = minimize_scalar(lambda x: sb.nll((x, 0.0), es), bounds=(-12, 4), method="bounded")
        dd = 2 * (null.fun - sb.nll((b0, b1), es))
        chk = abs(nll3((b0, b1, 0.0), *arrays(es)) - sb.nll((b0, b1), es))
        single[D] = (b0, b1, dd, len(es))
        w("  D=%d %-10s established %d: b0 %+.4f b1 %+.4f delta-dev %.2f -> %s | record: b1 %+.4f delta-dev %.2f (%s) | vectorised nll == sb.nll within %.1e"
          % (D, DRAWS[D][0], len(es), b0, b1, dd, "IDENTIFIED" if dd >= CHI1 else "NOT identified", RECORD[D]["b1"], RECORD[D]["ddev"], RECORD[D]["src"], chk))
    if abs(single[1][2] - RECORD[1]["ddev"]) > 0.02 or abs(single[1][1] - RECORD[1]["b1"]) > 0.01:
        w("  WARNING: the Kotlin draw (its population is unchanged by the restriction) does not reproduce the record's %.2f / %+.4f" % (RECORD[1]["ddev"], RECORD[1]["b1"]))
    else:
        w("  the Kotlin draw reproduces the record (its population is unchanged by the restriction); the GROK-CALIB draw differs by the 19 dropped matches only")
    # (3) the pooled fit
    w(""); w("=== (3) the pooled fit: tau(A, D) = exp(b0 + b1 A + b2 D) on the union of both draws' established edges (3 free parameters) ===")
    pooled = [dict(e, D=D) for D in DRAWS for e in E[D] if key(e) in est_both]
    arr = arrays(pooled)
    full, null, dd_pool = ddev(arr, pooled=True)
    events = int(arr[4].sum())
    w("  pooled established edges %d (%d per draw) | events (wrong-direction established) %d | b0 %+.4f | b1 %+.4f | b2 %+.4f | nll %.3f"
      % (len(pooled), len(est_both), events, full[0], full[1], full[2], full[3]))
    w("  null (b1 = 0; b0, b2 free): b0 %+.4f b2 %+.4f nll %.3f | delta-deviance %.2f vs %.2f -> %s"
      % (null[0], null[2], null[3], dd_pool, CHI1, "IDENTIFIED" if dd_pool >= CHI1 else "NOT identified"))
    w("  beside it, the single-draw values of record: D=0 %.2f (b1 %+.2f) | D=1 %.2f (b1 %+.2f)" % (RECORD[0]["ddev"], RECORD[0]["b1"], RECORD[1]["ddev"], RECORD[1]["b1"]))
    w("  tau at A = 0.30 / 0.60 / 0.90: D=0 %s | D=1 %s"
      % (" / ".join("%.3f" % math.exp(full[0] + full[1] * a) for a in (0.3, 0.6, 0.9)), " / ".join("%.3f" % math.exp(full[0] + full[1] * a + full[2]) for a in (0.3, 0.6, 0.9))))
    # (4) the question-clustered bootstrap of the pooled b1
    w(""); w("=== (4) question-clustered bootstrap of the pooled fit (questions resampled within anchor, both draws rebuilt from the same resample, inner B=%d, outer B=%d) ===" % (B_INNER, boot))
    rng = random.Random(SEED + 1); bs = []
    anchor_qs_shared = {anc: sorted({d.raw[0][m][2] for m in d.shared if d.route.get(d.raw[0][m][2]) is not None and d.anchor_of(d.route[d.raw[0][m][2]]) == anc}) for anc in d.anchors}
    byq = {D: defaultdict(list) for D in DRAWS}
    for D in DRAWS:
        for anc in d.anchors:
            for r in d.by[D][anc]:
                byq[D][r[2]].append(r)
    tb = time.time()
    for b in range(boot):
        Eb, estb, _ = replicate(d.anchors, anchor_qs_shared, byq, d.K, d.P, d.models, rng)
        eb = estb[0] & estb[1]
        pb = [dict(e, D=D) for D in DRAWS for e in Eb[D] if key(e) in eb]
        if sum(1 for e in pb if not e["right"]) == 0:
            bs.append((float("nan"), float("nan"), float("nan"))); continue
        fb, _, ddb = ddev(arrays(pb), pooled=True)
        bs.append((fb[1], fb[2], ddb))
        if b == 0:
            w("  first replicate %.1f s -> ~%.0f min for B=%d" % (time.time() - tb, (time.time() - tb) * boot / 60, boot))
    b1s = sorted(x[0] for x in bs if not math.isnan(x[0])); b2s = sorted(x[1] for x in bs if not math.isnan(x[1])); dds = sorted(x[2] for x in bs if not math.isnan(x[2]))
    def pct(v, p):
        return v[min(len(v) - 1, max(0, int(round(p * (len(v) - 1)))))] if v else float("nan")
    w("  %d replicates (%d degenerate, no events) | b1 %+.4f, 95%% percentile interval [%+.3f, %+.3f] | b2 [%+.3f, %+.3f] | delta-deviance median %.2f, share >= %.2f: %.3f"
      % (len(bs), boot - len(b1s), full[1], pct(b1s, 0.025), pct(b1s, 0.975), pct(b2s, 0.025), pct(b2s, 0.975), pct(dds, 0.5), CHI1, sum(1 for x in dds if x >= CHI1) / max(1, len(dds))))
    # (5) power
    w(""); w("=== (5) power statement (C2): parametric simulation at true b1 = %+.1f, b0 / b2 at the pooled fit, %d label sets each, P(delta-deviance >= %.2f) ===" % (TRUE_B1, sims, CHI1))
    nrng = np.random.default_rng(SEED)
    pw = {}
    for tag, es, pooled_flag in (("D=0 established (single draw)", [e for e in pooled if e["D"] == 0], False),
                                 ("D=1 established (single draw)", [e for e in pooled if e["D"] == 1], False),
                                 ("pooled (both draws)", pooled, True)):
        rate, ev = simulate_power(es, full[0], TRUE_B1, full[2], pooled_flag, sims, nrng)
        pw[tag] = (rate, ev)
        w("  %-32s edges %4d | mean simulated events %5.1f | power %.3f" % (tag, len(es), ev, rate))
    # (6) LOAO on the pooled fit
    w(""); w("=== (6) LOAO at %.3f on the pooled fit (folds on the established edges of the other 13 anchors, both draws; evaluated on every edge of the held-out anchor) ===" % THRESH)
    est_ids = {id(e) for D in DRAWS for e in E[D] if key(e) in est_both}
    oof = loao({D: E[D] for D in DRAWS}, est_ids, x0=(full[0], full[1], full[2]))
    C3 = {}; C4 = {}
    for tag, sel in (("unfiltered (adopted denominator, UNFILTERED-ADOPT)", lambda e: True), ("key gap >= %.2f (the derivation's population)" % GAP, lambda e: e["gap"] >= GAP)):
        w("  [%s]" % tag)
        w("  %-12s %7s %7s %7s %10s %9s %-40s %s" % ("draw", "edges", "called", "wrong", "wrong(est)", "nominal", "status", "utility = called / all edges (D6)"))
        tot = [0, 0, 0, 0, 0.0]
        for D in DRAWS:
            es = [e for e in E[D] if sel(e)]
            called = [e for e in es if oof[D][id(e)] >= THRESH]
            wr = sum(1 for e in called if not e["right"]); wre = sum(1 for e in called if not e["right"] and key(e) in est[D])
            nom = sum(1 - oof[D][id(e)] for e in called)
            util = len(called) / max(1, len(es))
            tot[0] += len(es); tot[1] += len(called); tot[2] += wr; tot[3] += wre; tot[4] += nom
            w("  %-12s %7d %7d %7d %10d %9.2f %-40s %.1f%% -> %s" % ("D=%d %s" % (D, DRAWS[D][0]), len(es), len(called), wr, wre, nom, power_status(nom, wr), 100 * util, "PASS" if util >= 0.60 else "FAIL"))
            C3[(tag, D)] = (len(called), wr, wre, nom); C4[(tag, D)] = util
        w("  %-12s %7d %7d %7d %10d %9.2f %-40s (each edge counted twice; not a utility)" % ("pooled", tot[0], tot[1], tot[2], tot[3], tot[4], power_status(tot[4], tot[2])))
        C3[(tag, "pooled")] = tuple(tot[1:])
    # (7) the registered lines
    w(""); w("=== (7) criteria, predictions, falsifier ===")
    w("  (C1) pooled delta-deviance %.2f >= %.2f: %s -> %s" % (dd_pool, CHI1, "HELD" if dd_pool >= CHI1 else "FAILED",
      "b1 identified on the pooled established labels; 'ORDERED-JUDGED available for grok' rests on the pooled evidence of both draws" if dd_pool >= CHI1 else
      "NOT identified; the power statement (C2) is mandatory beside every identification the record prints; every grok cell is BANDED-JUDGED (Stage 6 fallback), a registered outcome"))
    w("  (C2) power at ~26 events: D=0 %.3f (%.1f events), D=1 %.3f (%.1f events); at ~52 events (pooled) %.3f (%.1f events) -> printed whatever C1 does: HELD (a statement, not a bar)"
      % (pw["D=0 established (single draw)"][0], pw["D=0 established (single draw)"][1], pw["D=1 established (single draw)"][0], pw["D=1 established (single draw)"][1], pw["pooled (both draws)"][0], pw["pooled (both draws)"][1]))
    ut = "unfiltered (adopted denominator, UNFILTERED-ADOPT)"
    w("  (C3) LOAO per draw (unfiltered): %s | pooled nominal %.2f -> %s"
      % (" | ".join("D=%d called %d wrong %d (established %d) nominal %.2f -> %s" % ((D,) + C3[(ut, D)] + (power_status(C3[(ut, D)][3], C3[(ut, D)][1]),)) for D in DRAWS),
         C3[(ut, "pooled")][3], power_status(C3[(ut, "pooled")][3], C3[(ut, "pooled")][1])))
    w("  (C4) utility >= 60%% per draw (unfiltered, deciding): %s | filtered beside: %s"
      % (" | ".join("D=%d %.1f%% %s" % (D, 100 * C4[(ut, D)], "HELD" if C4[(ut, D)] >= 0.60 else "FAILED") for D in DRAWS),
         " | ".join("D=%d %.1f%%" % (D, 100 * C4[("key gap >= %.2f (the derivation's population)" % GAP, D)]) for D in DRAWS)))
    w("  prediction: pooled delta-deviance in [3.5, 5.5]: %s (%.2f)" % ("HELD" if 3.5 <= dd_pool <= 5.5 else "FAILED", dd_pool))
    for D in DRAWS:
        c, wr, wre, nom = C3[(ut, D)]
        w("  prediction: LOAO wrong 2-4 (established 1-2) on D=%d: %s (wrong %d, established %d)" % (D, "HELD" if (2 <= wr <= 4 and 1 <= wre <= 2) else "FAILED", wr, wre))
    w("  prediction: nominal ~2.2 (read on the pooled LOAO, each edge twice; scored within [1.5, 3.0]): %s (%.2f)" % ("HELD" if 1.5 <= C3[(ut, "pooled")][3] <= 3.0 else "FAILED", C3[(ut, "pooled")][3]))
    w("  prediction: status UNDETERMINED: %s" % ("HELD" if all(C3[(ut, D)][3] < 3 for D in DRAWS) else "FAILED"))
    w("  prediction (registrar): b2 within [-1, +1]: %s (%+.4f)" % ("HELD" if -1 <= full[2] <= 1 else "FAILED", full[2]))
    w("  FALSIFIER pooled delta-deviance < 2.5: %s (%.2f)%s" % ("TRIGGERED" if dd_pool < 2.5 else "not triggered", dd_pool,
      " -> item 26's criterion is unmet on the evidence; every grok-judged cell is BANDED-JUDGED; FRAMEWORK item 26 / Stage 6 carry the bracket until a larger established population exists (new questions, not re-draws)" if dd_pool < 2.5 else ""))
    w("  free parameters: 3 (b0, b1, b2) = the SYSTEMATIC-BUDGET criterion (4) ceiling")
    w(""); w("=== RE-JUDGE-RULE (plan Amendment 4, docs/plan_2026-09-15.md; a rule, not a measurement; on disk: %s) ===" % ("yes" if amendment_present() else "NO"))
    for t in TRIGGERS:
        w("  " + t)
    w("  consequence for the continual object: a refit each epoch will not grant and withdraw ORDERED-JUDGED on the same judge, because the certificate is read on pooled draws with a power number beside it")
    w("  runtime %.0f s" % (time.time() - t0))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("[ITEM-26-POOLED] written to %s" % os.path.relpath(out_path, ROOT))


# ── self-test on synthetic edges ───────────────────────────────────────────────────────────────────────────────

def selftest():
    print("reserved_pool_id=%s (selftest: no cache of record is read)" % POOL)
    rng = np.random.default_rng(7); random.seed(7)
    b0, b1, b2 = -3.0, 2.7, 0.5
    def synth(n, D, seed):
        r = np.random.default_rng(seed); es = []
        for i in range(n):
            A = float(r.uniform(0.25, 0.95)); s = float(r.uniform(0.05, 0.4)); m = float(r.normal(0, 0.6))
            tau = math.exp(b0 + b1 * A + b2 * D)
            pw = norm.cdf(-abs(m) / math.sqrt(s ** 2 + tau ** 2))
            es.append(dict(anchor="a%d" % (i % 14), a="x", b="y", p=0.9, m=m, s=s, agree=A, gap=0.1, right=bool(r.random() >= pw), D=D))
        return es
    es0 = synth(4000, 0, 1); es1 = synth(4000, 1, 2)
    # 1. the vectorised likelihood equals systematic_budget.nll at b2 = 0
    for par in ((-3.0, 2.0), (-2.0, 0.0), (-4.5, 3.3)):
        v = nll3((par[0], par[1], 0.0), *arrays(es0)); r = sb.nll(par, es0)
        assert abs(v - r) < 1e-6 * max(1, abs(r)), (v, r)
    print("  [1] nll3 == systematic_budget.nll at b2 = 0 on 4000 synthetic edges: OK")
    # 2. the planted (b1, b2) recovered on the pooled synthetic population
    full, null, dd = ddev(arrays(es0 + es1), pooled=True)
    print("  [2] planted b0 %+.2f b1 %+.2f b2 %+.2f -> fitted b0 %+.3f b1 %+.3f b2 %+.3f | delta-deviance %.1f" % (b0, b1, b2, full[0], full[1], full[2], dd))
    assert abs(full[1] - b1) < 0.6 and abs(full[2] - b2) < 0.4 and dd > CHI1, "planted b1 / b2 not recovered"
    # 3. no signal -> no identification (b1 = 0 planted)
    def synth0(n, seed):
        r = np.random.default_rng(seed); es = []
        for i in range(n):
            A = float(r.uniform(0.25, 0.95)); s = float(r.uniform(0.05, 0.4)); m = float(r.normal(0, 0.6)); tau = math.exp(-3.0)
            es.append(dict(anchor="a%d" % (i % 14), a="x", b="y", p=0.9, m=m, s=s, agree=A, gap=0.1, right=bool(r.random() >= norm.cdf(-abs(m) / math.sqrt(s ** 2 + tau ** 2))), D=i % 2))
        return es
    fz, nz, dz = ddev(arrays(synth0(4000, 3)), pooled=True)
    print("  [3] planted b1 = 0 -> fitted b1 %+.3f | delta-deviance %.2f (should sit below %.2f most of the time)" % (fz[1], dz, CHI1))
    # 4. mcnemar_edge and the LOAO plumbing on the synthetic edges
    K = {q: {"x": int(q % 3 == 0), "y": int(q % 5 == 0)} for q in range(300)}
    aq = {"a%d" % i: list(range(300)) for i in range(14)}
    p, bb, cc = sb.mcnemar_edge(dict(anchor="a0", a="x", b="y"), K, aq)
    print("  [4] mcnemar_edge on a planted 3:5 correctness pattern: p %.4f b %d c %d" % (p, bb, cc)); assert p < 0.05
    est_ids = {id(e) for e in es0[:400] + es1[:400]}
    oof = loao({0: es0[:400], 1: es1[:400]}, est_ids, x0=(b0, b1, b2))
    assert len(oof[0]) == 400 and len(oof[1]) == 400 and all(0 <= v <= 1 for v in oof[0].values())
    print("  [5] LOAO plumbing: %d + %d out-of-fold certificates in [0, 1]: OK" % (len(oof[0]), len(oof[1])))
    rate, ev = simulate_power(es0[:400] + es1[:400], b0, TRUE_B1, b2, True, 40, rng)
    print("  [6] power simulator on 800 synthetic edges (40 sims): power %.2f, mean events %.1f: runs" % (rate, ev))
    # 7. build_edges on a synthetic board reproduces sb.build's loop shape (same RNG, two identical calls agree)
    models = sorted(p8.ARENA12); rr = random.Random(5); rows = []
    for q in range(240):
        for _ in range(3):
            a, b = rr.sample(models, 2); rows.append((a, b, q, rr.choice([a, b, "TIE"])))
    Kx = {q: {m: int(rr.random() < 0.5) for m in models} for q in range(240)}; Px = {q: {m: rr.choice("ABCD") for m in models} for q in range(240)}
    e1, _ = build_edges({"anc": rows}, Kx, Px, models, random.Random(SEED), B=20); e2, _ = build_edges({"anc": rows}, Kx, Px, models, random.Random(SEED), B=20)
    assert [(e["m"], e["s"]) for e in e1] == [(e["m"], e["s"]) for e in e2] and len(e1) > 0
    print("  [7] build_edges deterministic under the seed (%d edges): OK" % len(e1))
    # 8. ONE outer bootstrap replicate through the run path: two draws, real-shaped int-keyed K / P (original qids only,
    #    no pseudo-qid entries), questions duplicated by the resample -> pseudo-qids (q, i) must be mapped back for K / P
    #    and used as is for mcnemar_edge (the KeyError of the 866812d run)
    anchors = ["Law", "Math"]; byq = {0: defaultdict(list), 1: defaultdict(list)}; aqs = {}; qid = 1000
    for anc in anchors:
        qs = []
        for _ in range(150):
            qid += 1; qs.append(qid)
            Kx[qid] = {m: int(rr.random() < 0.5) for m in models}; Px[qid] = {m: rr.choice("ABCD") for m in models}
            for D in (0, 1):
                for _ in range(3):
                    a, b = rr.sample(models, 2); byq[D][qid].append((a, b, qid, rr.choice([a, b, "TIE"])))
        aqs[anc] = qs
    rngr = random.Random(11)
    Eb, estb, qmap = replicate(anchors, aqs, byq, Kx, Px, models, rngr, B=10)
    dup = sum(1 for c in Counter(qmap.values()).values() if c > 1)
    assert dup > 0, "the resample produced no duplicated question; the case does not exercise the bug"
    assert all(isinstance(pq, tuple) for pq in qmap) and not any(pq in Kx for pq in qmap), "K must stay original-keyed"
    assert len(Eb[0]) > 0 and len(Eb[1]) > 0 and len(qmap) == 300
    # the established labels on the resample equal a direct multiset McNemar over the picks
    Kb = {pq: Kx[q] for pq, q in qmap.items()}
    for e in Eb[0][:20]:
        picks = [pq for pq in qmap if qmap[pq] in set(aqs[e["anchor"]])]
        b_ = sum(1 for pq in picks if Kx[qmap[pq]][e["a"]] > Kx[qmap[pq]][e["b"]]); c_ = sum(1 for pq in picks if Kx[qmap[pq]][e["a"]] < Kx[qmap[pq]][e["b"]])
        pv, bb_, cc_ = sb.mcnemar_edge(e, Kb, {e["anchor"]: picks})
        assert (bb_, cc_) == (b_, c_), ((bb_, cc_), (b_, c_))
    print("  [8] one outer replicate through the run path (2 draws, 300 picks, %d questions duplicated, real-shaped K): %d / %d edges, %d / %d established, McNemar on the multiset agrees: OK"
          % (dup, len(Eb[0]), len(Eb[1]), len(estb[0]), len(estb[1])))
    print("[SELFTEST] OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--boot", type=int, default=B_OUTER); ap.add_argument("--sims", type=int, default=N_SIM); ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.dry_run:
        dry_run()
    elif a.run:
        readout(a.boot, a.sims, a.out)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
