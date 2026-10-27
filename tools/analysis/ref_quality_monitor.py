"""REF-QUALITY-MONITOR — is per-cell reference-correct rate the continual per-cell quality signal? with
DIFFICULTY-PROXY-WIDENER as the secondary leg, registered expecting UNDETERMINED (zero judge calls; registered 2026-09-17
at commit 62c4084 in docs/judge_v2_program.md L5522-L5584 BEFORE this script was written).

  python tools/analysis/ref_quality_monitor.py --dry-run       # pool id first; caches inspected mode=ro; data objects and
                                                               #   denominators only; NO outcome number; nothing written
  python tools/analysis/ref_quality_monitor.py --selftest      # the statistics on SYNTHETIC data (a planted rank correlation
                                                               #   recovered; a planted b2 recovered); no cache of record is read
  python tools/analysis/ref_quality_monitor.py --run [--boot 300] [--sims 1000] [--out <path>]
                                                               # the readout; refuses on a row-count mismatch; write-once: refuses
                                                               #   if any of its three outputs exists; writes
                                                               #   experiment_results/x12_crossdomain/ref_quality_monitor_outcome.txt
                                                               #   (+ ref_quality_monitor_cells.csv, difficulty_proxy_widener.txt)

QUESTION (registration). TOPIC-DIFFICULTY found 72-79% of a cell's easy-to-hard accuracy drop is the reference's. Primary:
across the boards of record, is the per-(anchor, cache) reference-correct rate on keyed audit mass a sufficient per-cell
statistic for the judge's key-decidable accuracy, so that a continual pipeline can MONITOR each cell's quality from the
reference alone? Secondary (the proxy leg): does the key-free plurality-agreement proxy (Spearman 0.785 with key
difficulty) predict wrong(established) edges as a second covariate in the widener, LOAO, at matched utility? The monitor
MONITORS; it never gates (ABSTAIN, REF-CONF, J2-D closed) and it is not a signal of reference accuracy at inference
(SYSTEMATIC-BUDGET correction (a)).

HYGIENE. Four caches, mode=ro, counts pinned: x12 MAIN stack_v2_promptv2_x12all.db 9,142 (2,811 q); GROK-CALIB
grok_calib.db 9,142 (11 INVALID, +1 reclassified by rule 10); KOTLIN kotlin_c0d3f708cbc3930e.db 9,123 (17 INVALID;
ref_correct taken from the x12 cache by match_id as TOPIC-DIFFICULTY did, same reference kit); x20
stack_v2_promptv2_x20.db 12,394 (2,646 q; its own ref_correct column; 124 new pairs only, zero verdicts on the 66 original
pairs: a different SCHEDULE on the same questions, printed as such). Pool p2dca21ab5f4ef3ae; anchors = the 14 bareq512_s42
anchors (the caches' anchor column asserted equal to anchor_fn(route)); key = eval_results.is_correct (roster of 46 models,
Meta-Llama-3-70B-Instruct excluded, OPTIONS-key join checked). Reference-correct = the cache's ref_correct column (the
reference kit's grade, the column TOPIC-DIFFICULTY read); its agreement with ref_letter == eval gt_answer is printed as a
hygiene line, not silently substituted. Conventions A (ties / INVALID / NON_TERMINATED wrong) and B (committed only) both.
Denominator hazard, stated before any number: x12, GROK-CALIB and KOTLIN judge the SAME matches under ONE reference
vintage, so their per-anchor reference-correct rates are identical up to the 19 dropped matches; the 14 x 4 = 56 cells
carry 14 + x20's 14 independent reference readings and four judge draws of accuracy. The registered 56-cell Spearman is
the plan's; the 14-cell Spearman per cache is printed beside it as the honest denominator; the outcome scores both.

INSTRUMENT, primary. Per (anchor, cache): key-decidable matches n, reference-correct rate over the key-decidable matches
with a graded reference (match level; the question-level rate beside), accuracy A and B, accuracy A within
reference-correct and within reference-wrong, INVALID rate. Spearman(reference-correct rate, accuracy A) across the 56
cells with a question-bootstrap interval (questions resampled within anchor, one resample shared by the four caches,
B = 300), the same for B, the same per cache across 14 anchors, and per anchor across 4 caches (descriptive, n = 4).
Residual: accuracy A within reference-correct per cell, its range against the range of accuracy A overall (ratio) and its
Spearman with the reference rate (a confounded monitor shows the judge's own residual tracking the reference rate).

INSTRUMENT, secondary (DIFFICULTY-PROXY-WIDENER). On the x12 MAIN edges (systematic_budget.build on an in-memory mode=ro
copy of the x12 rows, asserted 891 filtered / 920 unfiltered, 809 established), per-edge P = mean over the edge's questions (the anchor's judged questions where both
contestants predicted, the denominator of A) of the key-free plurality proxy (per question, the share of the roster's
predicted letters on the plurality letter). tau(A, P) = exp(b0 + b1 A + b2 P) fitted on established labels (the
systematic_budget likelihood, vectorised and asserted equal); delta-deviance of b2 = 0 against 3.84; the profile
likelihood of b2 over a grid; LOAO at 0.975 (folds on the established edges of the other 13 anchors): called /
wrong(established) / nominal against the A-only widener at MATCHED utility (the A-only threshold moved until called
counts equal); power by parametric simulation at the in-sample b2 (b0, b1 at their fits), 1,000 label sets on the
established population. P needs roster letters only; no key enters the deployed form.

CRITERIA (scored HELD / FAILED):  (C1) Spearman(reference-correct rate, accuracy A) across the 14 x 4 cells >= 0.8
(interval printed; the per-cache 14-cell values printed beside and each scored against 0.8).  (C2, secondary) the proxy
covariate: established wrong calls at matched utility not above the A-only widener under LOAO, AND b2 identified
(delta-deviance >= 3.84); UNDETERMINED is the outcome of record if b2 is not identified or nominal < 3.
PREDICTIONS (blind): C1 HELD (>= 0.8; the judge lens's 0.85-0.95 recorded as the lens's); C2 UNDETERMINED (26-40 events);
registrar's addition: accuracy A within reference-correct varies less than half as much across cells as accuracy A
overall (range ratio < 0.5).
FALSIFIER: C1 Spearman < 0.5 on the 56-cell reading AND on the per-cache 14-cell readings.

OUTPUT. experiment_results/x12_crossdomain/ref_quality_monitor_outcome.txt (the file of record, bracketed in the registration
at 1534a4a) + ref_quality_monitor_cells.csv + difficulty_proxy_widener.txt, written ONCE from complete caches: --run refuses
([ONCE]) if any of the three exists, --out is guarded the same way; --dry-run writes nothing. Every cache of record is opened
mode=ro only (the x12 rows are copied into an in-memory table for systematic_budget.build). Monitors only, never gates.
"""
import os, sys, csv, math, json, random, sqlite3, argparse, time
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
import pool_guard
import rejudge_grok as rj
import rubric_512 as r512
import stack_judge as sj
import systematic_budget as sb

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

POOL = pool_guard.MMLU_PRO_POOL                   # p2dca21ab5f4ef3ae
TREE = "bareq512_s42"
EXCLUDED = {"Meta-Llama-3-70B-Instruct"}
X12DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
CACHES = {                                        # name -> (path, pinned rows, pinned INVALID column, pinned rule-10 extra)
    "X12":        (os.path.join(X12DIR, "stack_v2_promptv2_x12all.db"), 9142, 0, 0),
    "GROK-CALIB": (os.path.join(X12DIR, "grok_calib.db"), 9142, 11, 1),
    "KOTLIN":     (os.path.join(ROOT, "experiment_results", "judge_wiring", "board", "kotlin_c0d3f708cbc3930e.db"), 9123, 17, 0),
    "X20":        (os.path.join(X12DIR, "stack_v2_promptv2_x20.db"), 12394, 0, 0),
}
ORDER = ["X12", "GROK-CALIB", "KOTLIN", "X20"]
N_Q = {"X12": 2811, "X20": 2646}; N_NOREF = 19
NON_TERMINATED = {"length", "content_filter", ""}
MIN_DEC = 20                                      # a cell below this prints its counts and no accuracy (TOPIC-DIFFICULTY's bar)
B_BOOT = 300; N_SIM = 1000; CHI1 = 3.84; SEED = 42
THRESH = sb.THRESH; GAP = sb.GAP
EXPECTED_EDGES = dict(filtered=891, unfiltered=920, established=809)
OUT = os.path.join(X12DIR, "ref_quality_monitor_outcome.txt")
OUT_CELLS = os.path.join(X12DIR, "ref_quality_monitor_cells.csv")
OUT_PROXY = os.path.join(X12DIR, "difficulty_proxy_widener.txt")
B2_GRID = [x / 2.0 for x in range(-24, 25)]        # profile likelihood of b2 over [-12, 12] step 0.5


def rel(p):
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:                      # a --out on another drive (Windows): print it absolute
        return p


def ro(path):
    if not os.path.isfile(path):
        raise SystemExit("[REF-QUALITY-MONITOR] cache not found: %s" % path)
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


def spearman(xs, ys):
    return rj.spearman(list(xs), list(ys))


# ── data objects ───────────────────────────────────────────────────────────────────────────────────────────────

class Data:
    """Every object the readout touches, loaded once; nothing here is an outcome number."""

    def __init__(self, log):
        self.log = log
        snap = r512.snapshot_id(TREE); nodes = r512.load_graph(snap)
        self.route = r512.primary_routing(TREE); self.anchor_of = r512.anchor_fn(nodes)
        self.anchor_of_q = {q: self.anchor_of(l) for q, l in self.route.items()}
        log("tree %s snapshot %s | %d routed pool questions | %d anchors" % (TREE, snap, len(self.route), len(set(self.anchor_of_q.values()))))
        self.rows = {}
        for name in ORDER:
            path, pinned, pinned_inv, pinned_r10 = CACHES[name]
            con = ro(path)
            cols = [c[1] for c in con.execute("PRAGMA table_info(verdicts)")]
            has_fin = "finish1" in cols
            q = ("SELECT match_id, model_a, model_b, qid, winner, invalid, ref_correct, ref_letter, anchor" + (", finish1, finish2" if has_fin else ", NULL, NULL") + " FROM verdicts")
            rows = con.execute(q).fetchall(); con.close()
            if len(rows) != pinned:
                raise SystemExit("[REF-QUALITY-MONITOR] %s holds %d verdict rows, the record pins %d: refusing" % (name, len(rows), pinned))
            ninv = sum(int(r[5] or 0) for r in rows)
            if ninv != pinned_inv:
                raise SystemExit("[REF-QUALITY-MONITOR] %s holds %d INVALID rows, the record pins %d: refusing" % (name, ninv, pinned_inv))
            reclass = 0; out = []
            for mid, a, b, qid, w, inv, rc, rl, anc, f1, f2 in rows:
                inv = int(inv or 0)
                if has_fin and ((f1 or "") in NON_TERMINATED or (f2 or "") in NON_TERMINATED) and not inv:
                    inv = 1; reclass += 1                     # rule 10: never a verdict, never a tie
                if inv:
                    w = "INVALID"
                out.append(dict(mid=int(mid), a=a, b=b, q=int(qid), w=w, inv=inv, rc=-1 if rc is None else int(rc), rl=(rl or "").strip().upper(), anc=anc))
            if reclass != pinned_r10:
                raise SystemExit("[REF-QUALITY-MONITOR] %s: rule 10 reclassifies %d rows, the record pins %d: refusing" % (name, reclass, pinned_r10))
            self.rows[name] = out
            log("cache %-10s %s | %d rows (pinned %d) | INVALID column %d | rule-10 reclassified %d | valid %d | questions %d | ref graded (ref_correct >= 0) %d"
                % (name, os.path.relpath(path, ROOT), len(out), pinned, ninv, reclass, sum(1 for r in out if not r["inv"]), len({r["q"] for r in out}), sum(1 for r in out if r["rc"] >= 0)))
        for name, n in N_Q.items():
            if len({r["q"] for r in self.rows[name]}) != n:
                raise SystemExit("[REF-QUALITY-MONITOR] %s carries %d questions, the record pins %d" % (name, len({r["q"] for r in self.rows[name]}), n))
        # KOTLIN records no ref_correct; the reference kit is the same cached solve -> take it from the x12 cache by match_id (TOPIC-DIFFICULTY)
        rc12 = {r["mid"]: (r["rc"], r["rl"]) for r in self.rows["X12"]}
        miss = [r["mid"] for r in self.rows["KOTLIN"] if r["mid"] not in rc12]
        if miss:
            raise SystemExit("[REF-QUALITY-MONITOR] %d Kotlin matches have no x12 row to take ref_correct from" % len(miss))
        bad_letter = sum(1 for r in self.rows["KOTLIN"] if r["rl"] and r["rl"] != rc12[r["mid"]][1])
        for r in self.rows["KOTLIN"]:
            r["rc"], r["rl"] = rc12[r["mid"]]
        log("KOTLIN ref_correct joined from X12 by match_id: %d of %d | ref_letter disagreements before the join %d | GROK-CALIB ref_correct == X12 ref_correct on %d of %d shared matches"
            % (len(self.rows["KOTLIN"]), len(self.rows["KOTLIN"]), bad_letter, sum(1 for r in self.rows["GROK-CALIB"] if r["mid"] in rc12 and rc12[r["mid"]][0] == r["rc"]), len(self.rows["GROK-CALIB"])))
        noref = {name: sorted({r["mid"] for r in self.rows[name] if r["rc"] < 0}) for name in ORDER}
        log("reference-less matches (ref_correct = -1; excluded from every reference rate): %s" % ", ".join("%s %d" % (n, len(noref[n])) for n in ORDER))
        if len(noref["X12"]) != N_NOREF or len(noref["GROK-CALIB"]) != N_NOREF or noref["KOTLIN"]:
            raise SystemExit("[REF-QUALITY-MONITOR] the reference-less set is not the record's 19 / 19 / 0")
        self.judged = sorted({r["q"] for n in ORDER for r in self.rows[n]})
        pool_guard.assert_scored_subset(POOL, self.judged, out=sys.stdout)
        unrouted = [q for q in self.judged if q not in self.anchor_of_q]
        if unrouted:
            raise SystemExit("[REF-QUALITY-MONITOR] %d judged questions have no route in %s" % (len(unrouted), TREE))
        for name in ORDER:
            bad = sum(1 for r in self.rows[name] if self.anchor_of_q[r["q"]] != r["anc"])
            if bad:
                raise SystemExit("[REF-QUALITY-MONITOR] %s: %d rows disagree with anchor_fn(route[qid])" % (name, bad))
        log("anchor column check: every row of every cache equals anchor_fn(route[qid]) on %s" % TREE)
        self.anchors = sorted({self.anchor_of_q[q] for q in self.judged})
        # key, predictions, plurality (roster of record; the OPTIONS-key join checked as TOPIC-DIFFICULTY does)
        ev = ro(rj.EVAL_DB); jset = set(self.judged)
        self.K = defaultdict(dict); self.P = defaultdict(dict); self.gt = {}
        roster = set()
        for q, m, pr, c, gt in ev.execute("SELECT question_id, model_name, pred, is_correct, gt_answer FROM eval_results"):
            if m in EXCLUDED:
                continue
            roster.add(m)
            if q in jset:
                self.K[q][m] = int(c or 0); self.P[q][m] = (pr or "").strip().upper()[:1]; self.gt[q] = (gt or "").strip().upper()
        self.roster = sorted(roster)
        self.plur = {}
        for q in self.judged:
            letters = [v for v in self.P[q].values() if v]
            if letters:
                self.plur[q] = Counter(letters).most_common(1)[0][1] / len(letters)
        def okey(o):
            try:
                return json.dumps(json.loads(o)) if o and o.strip().startswith("[") else o
            except Exception:
                return o
        mm = defaultdict(list)
        for i, o, ans in ev.execute("SELECT id, options, answer FROM mmlu_pro"):
            mm[okey(o)].append((i, (ans or "").strip().upper()))
        matched = multi = none = agree = 0
        for q, o, gt in ev.execute("SELECT question_id, options_json, gt_answer FROM eval_results GROUP BY question_id"):
            if q not in jset:
                continue
            hits = mm.get(okey(o), [])
            if len(hits) == 1:
                matched += 1; agree += int(hits[0][1] == (gt or "").strip().upper())
            elif len(hits) > 1:
                multi += 1
            else:
                none += 1
        ev.close()
        log("key: roster %d models (%s excluded) | OPTIONS-key join eval_results -> mmlu_pro on the %d judged questions: 1:1 %d | multi %d | none %d | gt_answer == mmlu_pro.answer on %d of %d"
            % (len(self.roster), ", ".join(sorted(EXCLUDED)), len(self.judged), matched, multi, none, agree, matched))
        # hygiene: the cache's ref_correct column against ref_letter == eval gt_answer (printed, not substituted)
        for name in ORDER:
            dis = [r for r in self.rows[name] if r["rc"] >= 0 and (r["rl"] == self.gt.get(r["q"])) != bool(r["rc"])]
            log("hygiene %-10s ref_correct column vs (ref_letter == eval gt_answer): %d matches on %d questions disagree (the column is the kit's grade, the one TOPIC-DIFFICULTY read; used as is)"
                % (name, len(dis), len({r["q"] for r in dis})))
        self.contestants = {name: sorted({r["a"] for r in self.rows[name]} | {r["b"] for r in self.rows[name]}) for name in ORDER}
        self.pairs = {name: {frozenset((r["a"], r["b"])) for r in self.rows[name]} for name in ORDER}
        log("contestants: %s | x20 pairs %d, of which shared with x12 %d (x20 is a different SCHEDULE on the same questions)"
            % (", ".join("%s %d" % (n, len(self.contestants[n])) for n in ORDER), len(self.pairs["X20"]), len(self.pairs["X20"] & self.pairs["X12"])))
        self.by = {name: defaultdict(list) for name in ORDER}
        for name in ORDER:
            for r in self.rows[name]:
                self.by[name][self.anchor_of_q[r["q"]]].append(r)
        self.anchor_qs = {anc: sorted({r["q"] for n in ORDER for r in self.by[n][anc]}) for anc in self.anchors}

    def decidable(self, r):
        ka, kb = self.K[r["q"]].get(r["a"]), self.K[r["q"]].get(r["b"])
        return ka is not None and kb is not None and ka != kb


# ── the per-cell statistic ─────────────────────────────────────────────────────────────────────────────────────

def cell_stats(d, rows):
    """One (anchor, cache) cell: A's denominator includes INVALID / non-terminated (convention A); B = committed only;
    reference rate over the key-decidable matches with a graded reference; the TOPIC-DIFFICULTY decomposition beside."""
    dec_all = [r for r in rows if d.decidable(r)]
    ok = lambda r: r["w"] == (r["a"] if d.K[r["q"]][r["a"]] else r["b"])
    okA = sum(1 for r in dec_all if ok(r))
    committed = [r for r in dec_all if r["w"] in (r["a"], r["b"])]
    okB = sum(1 for r in committed if ok(r))
    graded = [r for r in dec_all if r["rc"] >= 0]
    refok = [r for r in graded if r["rc"] == 1]; refwrong = [r for r in graded if r["rc"] == 0]
    qs = {r["q"] for r in rows}; qg = {r["q"]: r["rc"] for r in rows if r["rc"] >= 0}
    res = dict(nq=len(qs), nm=len(rows), ninv=sum(r["inv"] for r in rows), ndec=len(dec_all), ncommitted=len(committed),
               n_graded=len(graded), n_refok=len(refok), n_refwrong=len(refwrong), nq_graded=len(qg), nq_refok=sum(qg.values()),
               ties_dec=sum(1 for r in dec_all if r["w"] == "TIE"))
    res["accA"] = okA / len(dec_all) if len(dec_all) >= MIN_DEC else None
    res["accB"] = okB / len(committed) if len(committed) >= MIN_DEC else None
    res["ref_rate"] = len(refok) / len(graded) if graded else None
    res["ref_rate_q"] = res["nq_refok"] / len(qg) if qg else None
    res["accA_refok"] = sum(1 for r in refok if ok(r)) / len(refok) if len(refok) >= MIN_DEC else None
    res["accA_refwrong"] = sum(1 for r in refwrong if ok(r)) / len(refwrong) if len(refwrong) >= MIN_DEC else None
    res["inv_rate"] = res["ninv"] / len(rows) if rows else None
    res["tie_dec"] = res["ties_dec"] / len(dec_all) if dec_all else None
    return res


def all_cells(d, rows_by=None):
    rows_by = rows_by or d.by
    return {(anc, name): cell_stats(d, rows_by[name][anc]) for anc in d.anchors for name in ORDER}


def rho_over(cells, keys, x, y):
    pts = [(cells[k][x], cells[k][y]) for k in keys if cells[k][x] is not None and cells[k][y] is not None]
    if len(pts) < 4:
        return float("nan"), len(pts)
    return spearman([p[0] for p in pts], [p[1] for p in pts]), len(pts)


def resample(d, rng):
    """Questions resampled within anchor (one resample shared by the four caches); rows of a picked question enter once
    per pick (multiplicity), so every cell statistic is recomputed on the resampled board."""
    out = {name: defaultdict(list) for name in ORDER}
    byq = {name: defaultdict(list) for name in ORDER}
    for name in ORDER:
        for r in d.rows[name]:
            byq[name][r["q"]].append(r)
    for anc in d.anchors:
        qs = d.anchor_qs[anc]
        for _ in qs:
            q = qs[rng.randrange(len(qs))]
            for name in ORDER:
                out[name][anc].extend(byq[name][q])
    return out


def pct(v, p):
    v = sorted(x for x in v if not (isinstance(x, float) and math.isnan(x)))
    return v[min(len(v) - 1, max(0, int(round(p * (len(v) - 1)))))] if v else float("nan")


# ── the proxy leg ──────────────────────────────────────────────────────────────────────────────────────────────

def x12_edges():
    """systematic_budget.build on the x12 MAIN cache WITHOUT opening it read-write: the rows are read mode=ro into an
    in-memory table with the columns build() reads, sj.open_cache is patched to that connection (as item26_pooled.py does),
    and the edge population is asserted to be the record's 920 / 891 / 809."""
    sj.PROMPT = "v2"; sj.ALL_X12 = True; sj.JUDGE = "mistral"
    assert os.path.normcase(os.path.abspath(sj.cache_path())) == os.path.normcase(os.path.abspath(CACHES["X12"][0])), sj.cache_path()
    con = ro(CACHES["X12"][0])
    rows = con.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts").fetchall(); con.close()
    if len(rows) != CACHES["X12"][1]:
        raise SystemExit("[REF-QUALITY-MONITOR] x12 cache holds %d rows, the record pins %d" % (len(rows), CACHES["X12"][1]))
    mem = sqlite3.connect(":memory:")
    mem.execute("CREATE TABLE verdicts (model_a TEXT, model_b TEXT, qid INTEGER, winner TEXT, invalid INTEGER)")
    mem.executemany("INSERT INTO verdicts VALUES (?, ?, ?, ?, ?)", rows)
    saved = sj.open_cache
    sj.open_cache = lambda: mem
    try:
        built = sb.build()
    finally:
        sj.open_cache = saved
    models, K12, P12, by, edges, anchor_qs = built
    n_all, n_filt = len(edges), sum(1 for e in edges if e["gap"] >= GAP)
    n_est = len(sb.established(edges, K12, anchor_qs))
    if (n_all, n_filt, n_est) != (EXPECTED_EDGES["unfiltered"], EXPECTED_EDGES["filtered"], EXPECTED_EDGES["established"]):
        raise SystemExit("[REF-QUALITY-MONITOR] x12 edge population %d / %d / %d differs from the record's %d / %d / %d: refusing"
                         % (n_all, n_filt, n_est, EXPECTED_EDGES["unfiltered"], EXPECTED_EDGES["filtered"], EXPECTED_EDGES["established"]))
    return built


def edge_proxy(edges, anchor_qs, P12, plur):
    """P per edge: the mean plurality share over the anchor's judged questions where both contestants predicted (A's denominator)."""
    for e in edges:
        both = [q for q in anchor_qs[e["anchor"]] if P12[q].get(e["a"]) and P12[q].get(e["b"]) and q in plur]
        e["plur"] = sum(plur[q] for q in both) / len(both) if both else float("nan")


def arrays(es):
    return (np.array([e["agree"] for e in es]), np.array([e["plur"] for e in es]), np.array([abs(e["m"]) for e in es]),
            np.array([e["s"] for e in es]), np.array([0.0 if e["right"] else 1.0 for e in es]))


def nllx(par, A, Pp, am, s, wrong):
    """tau(A, P) = exp(b0 + b1 A + b2 P); equals systematic_budget.nll at b2 = 0 (asserted in --selftest and in --run)."""
    b0, b1, b2 = par
    tau = np.exp(np.minimum(20.0, b0 + b1 * A + b2 * Pp))
    z = am / np.sqrt(s ** 2 + tau ** 2)
    pw = np.clip(norm.cdf(-z), 1e-12, 1 - 1e-12)
    return float(-(wrong * np.log(pw) + (1 - wrong) * np.log(1 - pw)).sum())


def fitx(arr, x0=(-3.0, 3.0, 0.0), fix_b2=None):
    """Nelder-Mead as systematic_budget.fit; fix_b2 pins b2 at a value (None = free). Returns (b0, b1, b2, nll)."""
    A, Pp, am, s, wrong = arr
    if fix_b2 is None:
        r = minimize(lambda x: nllx(x, A, Pp, am, s, wrong), np.array(x0), method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
        return float(r.x[0]), float(r.x[1]), float(r.x[2]), float(r.fun)
    r = minimize(lambda x: nllx((x[0], x[1], fix_b2), A, Pp, am, s, wrong), np.array(x0[:2]), method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
    return float(r.x[0]), float(r.x[1]), float(fix_b2), float(r.fun)


def ddev_b2(arr):
    full = fitx(arr)
    null = fitx(arr, x0=(full[0], full[1], 0.0), fix_b2=0.0)
    return full, null, 2 * (null[3] - full[3])


def cbudx(e, b0, b1, b2):
    tau = math.exp(b0 + b1 * e["agree"] + b2 * e["plur"])
    return min(sb.craw(e), float(norm.cdf(abs(e["m"]) / math.sqrt(e["s"] ** 2 + tau ** 2))))


def loao_x(edges, est_ids, with_p, x0):
    ancs = sorted({e["anchor"] for e in edges}); oof = {}
    for A_ in ancs:
        tr = [e for e in edges if e["anchor"] != A_ and id(e) in est_ids]
        f = fitx(arrays(tr), x0=x0, fix_b2=None if with_p else 0.0)
        for e in edges:
            if e["anchor"] == A_:
                oof[id(e)] = cbudx(e, f[0], f[1], f[2])
    return oof


def power_status(nominal, wrong):
    if nominal < 3:
        return "UNDETERMINED (power rule: nominal < 3)"
    if nominal < 9:
        return "UNDETERMINED (power: 2x undetectable)"
    from scipy.stats import poisson
    return "NOT DETECTABLY MISCALIBRATED" if poisson.sf(wrong - 1, nominal) > 0.05 else "MISCALIBRATED"


def simulate_power_b2(es, b0, b1, b2, n_sim, rng):
    A, Pp, am, s, _ = arrays(es)
    tau = np.exp(b0 + b1 * A + b2 * Pp)
    pw = norm.cdf(-am / np.sqrt(s ** 2 + tau ** 2))
    hits = 0; events = 0.0
    for _ in range(n_sim):
        wrong = (rng.random(len(es)) < pw).astype(float)
        events += wrong.sum()
        if wrong.sum() == 0:
            continue
        _, _, dd = ddev_b2((A, Pp, am, s, wrong))
        hits += dd >= CHI1
    return hits / n_sim, events / n_sim


def edge_population(by_rows, K12, P12, models):
    """Edge denominators without the bootstrap (dry-run only): sb.build's pair rule on the x12 rows."""
    out = []
    for anc in sorted(by_rows):
        qs = sorted({r["q"] for r in by_rows[anc]})
        if len(by_rows[anc]) < 200:
            continue
        la = {}
        for m in models:
            v = [K12[q].get(m) for q in qs if K12[q].get(m) is not None]
            if v:
                la[m] = sum(v) / len(v)
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if a not in la or b not in la or la[a] == la[b]:
                    continue
                both = [q for q in qs if P12[q].get(a) and P12[q].get(b)]
                if both:
                    out.append(dict(anchor=anc, a=a, b=b, gap=abs(la[a] - la[b])))
    return out, {anc: sorted({r["q"] for r in by_rows[anc]}) for anc in by_rows}


# ── dry-run ────────────────────────────────────────────────────────────────────────────────────────────────────

def dry_run():
    print("reserved_pool_id=%s" % POOL)
    pool_guard.assert_pool_of_record(POOL)
    print("[DRY-RUN] REF-QUALITY-MONITOR + DIFFICULTY-PROXY-WIDENER | zero judge calls | caches opened mode=ro | nothing written | no outcome number below")
    d = Data(lambda s: print("  " + s))
    print("  cells: %d anchors x %d caches = %d | per cell: matches / key-decidable (A's denominator) / graded reference / committed:" % (len(d.anchors), len(ORDER), len(d.anchors) * len(ORDER)))
    print("  %-17s %5s | %s" % ("anchor", "nq", " | ".join("%-22s" % n for n in ORDER)))
    for anc in d.anchors:
        parts = []
        for name in ORDER:
            rows = d.by[name][anc]; dec = [r for r in rows if d.decidable(r)]
            parts.append("%-22s" % ("%d/%d/%d/%d" % (len(rows), len(dec), sum(1 for r in dec if r["rc"] >= 0), sum(1 for r in dec if r["w"] in (r["a"], r["b"])))))
        print("  %-17s %5d | %s" % (anc, len(d.anchor_qs[anc]), " | ".join(parts)))
    print("  DENOMINATOR HAZARD: X12, GROK-CALIB and KOTLIN judge the same matches under one reference vintage -> their per-anchor reference-correct rates are identical up to the 19 dropped matches; "
          "the 56 cells carry 14 + 14 (x20) independent reference readings and four judge draws of accuracy. Both the 56-cell and the per-cache 14-cell Spearman are scored.")
    pl = list(d.plur.values())
    print("  key-free plurality proxy over %d judged questions (roster %d): mean %.3f | quartiles %.3f / %.3f / %.3f (data object, not an outcome)"
          % (len(pl), len(d.roster), float(np.mean(pl)), *[float(np.percentile(pl, p)) for p in (25, 50, 75)]))
    import rubric_p8 as p8
    K12 = defaultdict(dict); P12 = defaultdict(dict)
    for q in d.judged:
        for m in p8.ARENA12:
            if m in d.K[q]:
                K12[q][m] = d.K[q][m]; P12[q][m] = d.P[q][m]
    by12 = {anc: [r for r in d.by["X12"][anc] if not r["inv"]] for anc in d.anchors}
    pop, aq = edge_population(by12, K12, P12, sorted(p8.ARENA12))
    est = sum(1 for e in pop if sb.mcnemar_edge(e, K12, aq)[0] < 0.05)
    print("  proxy leg, x12 MAIN edge population (sb.build's pair rule, no bootstrap): %d unfiltered (registration expects %d) | %d with key gap >= %.2f (expects %d) | %d established (expects %d)"
          % (len(pop), EXPECTED_EDGES["unfiltered"], sum(1 for e in pop if e["gap"] >= GAP), GAP, EXPECTED_EDGES["filtered"], est, EXPECTED_EDGES["established"]))
    print("  instrument: cell statistic = cell_stats (conventions A / B, MIN_DEC %d); Spearman = rejudge_grok.spearman; question bootstrap B=%d within anchor, shared across caches; "
          "proxy widener tau(A, P) = exp(b0 + b1 A + b2 P) on established labels, profile of b2 over [%.0f, %.0f] step 0.5, LOAO at %.3f vs A-only at matched utility, power sims %d"
          % (MIN_DEC, B_BOOT, B2_GRID[0], B2_GRID[-1], THRESH, N_SIM))
    print("  runtime estimate for --run: cell statistics + %d bootstrap replicates ~2-4 min; sb.build on x12 ~15 s; profile %d fits + LOAO 28 fits ~10 s; power sims %d x 2 fits ~2 min" % (B_BOOT, len(B2_GRID), N_SIM))
    print("[DRY-RUN] done: no outcome computed. Run with --run after the registration is committed.")


# ── the readout ────────────────────────────────────────────────────────────────────────────────────────────────

def fmt(x, nd=3):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else ("%%.%df" % nd) % x


def readout(boot, sims, out_path, d=None, log=print, selftest=False):
    if not selftest:
        for path in (out_path, OUT_CELLS, OUT_PROXY):
            if os.path.exists(path):
                raise SystemExit("[ONCE] %s exists: the files of record are written once, from complete caches; never overwritten (correct by insertion in the record, not by re-running)" % rel(path))
    L = []; LP = []
    def w(s=""):
        L.append(s); log(s)
    def wp(s=""):
        LP.append(s); L.append(s); log(s)
    w("reserved_pool_id=%s" % POOL)
    if not selftest:
        pool_guard.assert_pool_of_record(POOL)
    w("=== REF-QUALITY-MONITOR (registered 2026-09-17, commit 62c4084, docs/judge_v2_program.md L5522-L5584; zero judge calls; a MONITOR, never a gate) ===")
    if d is None:
        d = Data(lambda s: w("  " + s))
    t0 = time.time()
    w("  DENOMINATOR HAZARD (stated before any number): X12, GROK-CALIB and KOTLIN judge the same matches under one reference vintage; their per-anchor reference rates are identical up to the 19 dropped matches. "
      "The 56 cells carry 14 + 14 (x20) independent reference readings and four judge draws of accuracy; 'cache' varies the judge draw, not the reference. Both readings are scored.")
    cells = all_cells(d)
    keys56 = [(anc, name) for anc in d.anchors for name in ORDER]
    w(""); w("=== (1) per (anchor, cache) cells: n key-decidable | reference-correct rate (match level; question level) | accuracy A | B | A within ref-correct | A within ref-wrong | INVALID rate | tie rate on decidable ===")
    w("  %-17s %-10s %6s %8s %8s %7s %7s %8s %8s %6s %6s" % ("anchor", "cache", "ndec", "ref", "ref_q", "accA", "accB", "A|refok", "A|refwr", "inv", "tie"))
    for anc, name in keys56:
        c = cells[(anc, name)]
        w("  %-17s %-10s %6d %8s %8s %7s %7s %8s %8s %6s %6s" % (anc, name, c["ndec"], fmt(c["ref_rate"]), fmt(c["ref_rate_q"]), fmt(c["accA"]), fmt(c["accB"]), fmt(c["accA_refok"]), fmt(c["accA_refwrong"]), fmt(c["inv_rate"]), fmt(c["tie_dec"])))
    # (2) the Spearman readings with the question bootstrap
    w(""); w("=== (2) Spearman(reference-correct rate, accuracy) with a question bootstrap (questions resampled within anchor, one resample shared by the four caches, B=%d) ===" % boot)
    rng = random.Random(SEED)
    reps = defaultdict(list)
    for b in range(boot):
        cb = all_cells(d, resample(d, rng))
        for conv in ("accA", "accB"):
            reps[("all", conv)].append(rho_over(cb, keys56, "ref_rate", conv)[0])
            for name in ORDER:
                reps[(name, conv)].append(rho_over(cb, [(anc, name) for anc in d.anchors], "ref_rate", conv)[0])
        reps[("all", "accA_refok")].append(rho_over(cb, keys56, "ref_rate", "accA_refok")[0])
    R = {}
    for conv in ("accA", "accB"):
        r, n = rho_over(cells, keys56, "ref_rate", conv); R[("all", conv)] = r
        w("  56-cell reading, %s: Spearman %+.3f (n=%d cells) | 95%% percentile interval [%+.3f, %+.3f]" % (conv, r, n, pct(reps[("all", conv)], 0.025), pct(reps[("all", conv)], 0.975)))
        for name in ORDER:
            rr, nn = rho_over(cells, [(anc, name) for anc in d.anchors], "ref_rate", conv); R[(name, conv)] = rr
            w("    per cache %-10s 14-cell Spearman %+.3f (n=%d) | [%+.3f, %+.3f]" % (name, rr, nn, pct(reps[(name, conv)], 0.025), pct(reps[(name, conv)], 0.975)))
    w("  per anchor across the 4 caches (descriptive, n = 4; three of the four reference readings are the same number):")
    for anc in d.anchors:
        pts = [(cells[(anc, n)]["ref_rate"], cells[(anc, n)]["accA"]) for n in ORDER if cells[(anc, n)]["accA"] is not None and cells[(anc, n)]["ref_rate"] is not None]
        w("    %-17s ref rates %s | accA %s | Spearman %s" % (anc, "/".join("%.3f" % p[0] for p in pts), "/".join("%.3f" % p[1] for p in pts), fmt(spearman([p[0] for p in pts], [p[1] for p in pts])) if len(pts) >= 4 else "-"))
    # (3) residual
    w(""); w("=== (3) residual: accuracy A within reference-correct per cell against the reference rate ===")
    refok = [cells[k]["accA_refok"] for k in keys56 if cells[k]["accA_refok"] is not None]
    accA = [cells[k]["accA"] for k in keys56 if cells[k]["accA"] is not None]
    rng_ok = max(refok) - min(refok); rng_all = max(accA) - min(accA); ratio = rng_ok / rng_all if rng_all > 0 else float("nan")
    r_res, n_res = rho_over(cells, keys56, "ref_rate", "accA_refok")
    w("  accuracy A within reference-correct: range %.3f (%.3f-%.3f, %d cells) | accuracy A overall: range %.3f (%.3f-%.3f) | ratio %.3f"
      % (rng_ok, min(refok), max(refok), len(refok), rng_all, min(accA), max(accA), ratio))
    w("  Spearman(reference rate, accuracy A within reference-correct) over %d cells: %+.3f [%+.3f, %+.3f] (a confounded monitor shows the judge's own residual tracking the reference rate)"
      % (n_res, r_res, pct(reps[("all", "accA_refok")], 0.025), pct(reps[("all", "accA_refok")], 0.975)))
    for name in ORDER:
        rr, nn = rho_over(cells, [(anc, name) for anc in d.anchors], "ref_rate", "accA_refok")
        w("    per cache %-10s %+.3f (n=%d)" % (name, rr, nn))
    # (4) the registered lines for the primary
    w(""); w("=== (4) criteria, predictions, falsifier (primary) ===")
    c1_56 = R[("all", "accA")] >= 0.8
    w("  (C1) Spearman(reference-correct rate, accuracy A) across the 14 x 4 cells %+.3f >= 0.8: %s" % (R[("all", "accA")], "HELD" if c1_56 else "FAILED"))
    for name in ORDER:
        w("       per-cache 14-cell %-10s %+.3f >= 0.8: %s" % (name, R[(name, "accA")], "HELD" if R[(name, "accA")] >= 0.8 else "FAILED"))
    w("       convention B beside: 56-cell %+.3f | per cache %s" % (R[("all", "accB")], ", ".join("%s %+.3f" % (n, R[(n, "accB")]) for n in ORDER)))
    w("  prediction: C1 HELD: %s | the judge lens's finer 0.85-0.95: %s (%+.3f)" % ("HELD" if c1_56 else "FAILED", "inside" if 0.85 <= R[("all", "accA")] <= 0.95 else "outside", R[("all", "accA")]))
    w("  prediction (registrar): range ratio < 0.5: %s (%.3f)" % ("HELD" if ratio < 0.5 else "FAILED", ratio))
    fals = R[("all", "accA")] < 0.5 and all(R[(n, "accA")] < 0.5 for n in ORDER)
    w("  FALSIFIER C1 Spearman < 0.5 on the 56-cell reading AND on every per-cache 14-cell reading: %s%s"
      % ("TRIGGERED" if fals else "not triggered", " -> the per-cell reference-correct rate is not the continual per-cell quality signal; no key-free per-cell quality statistic until one is registered" if fals else ""))
    w("  consequence if C1 holds: FRAMEWORK Stage 9 may name the reference-correct rate on keyed audit mass as the per-cell MONITOR read each epoch (beside the canary and arm B); it changes no board, no certificate, no fit; never a gate")
    # ── the secondary leg ──
    wp(""); wp("=== DIFFICULTY-PROXY-WIDENER (secondary; registered expecting UNDETERMINED) on the x12 MAIN edges ===")
    if selftest:
        edges, anchor_qs, K12, P12 = d.synthetic_edges()
    else:
        import rubric_p8 as p8
        models, K12, P12, _, edges, anchor_qs = x12_edges()
    edge_proxy(edges, anchor_qs, P12, d.plur)
    edges = [e for e in edges if not math.isnan(e["plur"])]
    filt = [e for e in edges if e["gap"] >= GAP]
    est = sb.established(edges, K12, anchor_qs); est_ids = {id(e) for e in est}
    events = sum(1 for e in est if not e["right"])
    wp("  edges %d unfiltered / %d filtered (gap >= %.2f) | established %d | events (wrong-direction established) %d | P per edge: mean %.3f, range %.3f-%.3f | Spearman(A, P) over established %+.3f"
       % (len(edges), len(filt), GAP, len(est), events, float(np.mean([e["plur"] for e in edges])), min(e["plur"] for e in edges), max(e["plur"] for e in edges),
          spearman([e["agree"] for e in est], [e["plur"] for e in est])))
    if not selftest and (len(edges), len(filt), len(est)) != (EXPECTED_EDGES["unfiltered"], EXPECTED_EDGES["filtered"], EXPECTED_EDGES["established"]):
        wp("  WARNING: edge counts differ from the record's %d / %d / %d" % (EXPECTED_EDGES["unfiltered"], EXPECTED_EDGES["filtered"], EXPECTED_EDGES["established"]))
    by_anc = defaultdict(list)
    for e in est:
        by_anc[e["anchor"]].append(e["plur"])
    within = float(np.mean([np.std(v) for v in by_anc.values() if len(v) > 1])); between = float(np.std([np.mean(v) for v in by_anc.values()]))
    wp("  identification profile of P: %d distinct values (3 dp) over %d established edges | between-anchor sd %.4f vs mean within-anchor sd %.4f (P is an ANCHOR-level covariate up to the pairs' prediction coverage: ~14 effective values, so b2 competes with b0 across 14 cells)"
       % (len({round(e["plur"], 3) for e in est}), len(est), between, within))
    arr = arrays(est)
    chk = abs(nllx((-3.0, 3.0, 0.0), *arr) - sb.nll((-3.0, 3.0), est))
    full, null, dd = ddev_b2(arr)
    wp("  vectorised nll == systematic_budget.nll at b2 = 0 within %.1e" % chk)
    if abs(full[0]) > 15 or abs(full[2]) > 30:
        wp("  NOTE: the A + P fit is DEGENERATE (|b0| > 15 or |b2| > 30: b0 and b2 collinear through a near-constant P); b2 is read as not identified")
    wp("  A-only fit on established labels: b0 %+.4f b1 %+.4f nll %.3f | A + P fit: b0 %+.4f b1 %+.4f b2 %+.4f nll %.3f | delta-deviance of b2 = 0: %.2f vs %.2f -> %s"
       % (null[0], null[1], null[3], full[0], full[1], full[2], full[3], dd, CHI1, "IDENTIFIED" if dd >= CHI1 else "NOT identified"))
    prof = []
    for g in B2_GRID:
        f = fitx(arr, x0=(full[0], full[1], g), fix_b2=g); prof.append((g, 2 * (f[3] - full[3])))
    inside = [g for g, v in prof if v <= CHI1]
    wp("  profile likelihood of b2 (deviance above the minimum; grid step 0.5): %s" % " ".join("%+.1f:%.1f" % (g, v) for g, v in prof))
    wp("  b2 profile interval at %.2f: [%+.1f, %+.1f] on the grid (%s)" % (CHI1, min(inside) if inside else float("nan"), max(inside) if inside else float("nan"),
       "open at a grid end -> b2 NOT identified in this direction" if inside and (min(inside) == B2_GRID[0] or max(inside) == B2_GRID[-1]) else "closed"))
    oof_p = loao_x(edges, est_ids, True, (full[0], full[1], full[2])); oof_a = loao_x(edges, est_ids, False, (null[0], null[1], 0.0))
    called_p = [e for e in edges if oof_p[id(e)] >= THRESH]
    k = len(called_p)
    ca = sorted((oof_a[id(e)] for e in edges), reverse=True)
    t_match = ca[k - 1] if k else 1.0
    called_a = [e for e in edges if oof_a[id(e)] >= t_match]
    called_a975 = [e for e in edges if oof_a[id(e)] >= THRESH]
    def line(tag, called):
        wr = sum(1 for e in called if not e["right"]); wre = sum(1 for e in called if not e["right"] and id(e) in est_ids); nom = sum(1 - oof_p[id(e)] if tag.startswith("A + P") else 1 - oof_a[id(e)] for e in called)
        wp("  %-44s called %4d of %d (utility %.1f%%) | wrong %d (established %d) | nominal %.2f -> %s" % (tag, len(called), len(edges), 100 * len(called) / len(edges), wr, wre, nom, power_status(nom, wr)))
        return wr, wre, nom
    wp("  LOAO at %.3f (folds fitted on the established edges of the other 13 anchors; evaluated on every edge):" % THRESH)
    wr_p, wre_p, nom_p = line("A + P widener at 0.975", called_p)
    wr_a, wre_a, nom_a = line("A-only widener at MATCHED utility (t = %.4f)" % t_match, called_a)
    line("A-only widener at 0.975 (unmatched, beside)", called_a975)
    nrng = np.random.default_rng(SEED)
    power, ev_mean = simulate_power_b2(est, full[0], full[1], full[2], sims, nrng)
    wp("  power: parametric simulation at b2 = %+.3f (the in-sample fit; b0, b1 at their fits) on the %d established edges, %d label sets: P(delta-deviance >= %.2f) = %.3f (mean events %.1f)"
       % (full[2], len(est), sims, CHI1, power, ev_mean))
    ident = dd >= CHI1
    if not ident or nom_p < 3:
        c2 = "UNDETERMINED (%s)" % ("; ".join(s for s, f in (("b2 not identified", not ident), ("nominal < 3", nom_p < 3)) if f))
    else:
        c2 = "HELD" if wre_p <= wre_a else "FAILED"
    wp("  (C2, secondary) established wrong calls at matched utility: A + P %d vs A-only %d | b2 identified: %s -> %s" % (wre_p, wre_a, "yes" if ident else "no", c2))
    wp("  prediction: C2 UNDETERMINED (26-40 events; events here %d): %s" % (events, "HELD" if c2.startswith("UNDETERMINED") else "FAILED"))
    wp("  the proxy leg falsifies nothing at this event count; a HELD C2 licenses only a registration of the two-covariate widener on a larger established population, never a gate; no key enters P")
    w("  runtime %.0f s" % (time.time() - t0))
    if selftest:
        return cells, R, ratio, full, dd
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write("\n".join(L) + "\n")
    open(OUT_PROXY, "w", encoding="utf-8").write("reserved_pool_id=%s\n" % POOL + "\n".join(LP) + "\n")
    with open(OUT_CELLS, "w", newline="", encoding="utf-8") as f:
        cols = ["anchor", "cache", "nq", "nm", "ninv", "ndec", "ncommitted", "n_graded", "n_refok", "n_refwrong", "nq_graded", "nq_refok", "ref_rate", "ref_rate_q", "accA", "accB", "accA_refok", "accA_refwrong", "inv_rate", "tie_dec"]
        wr_ = csv.writer(f); wr_.writerow(cols)
        for anc, name in keys56:
            wr_.writerow([anc, name] + [cells[(anc, name)].get(c) for c in cols[2:]])
    print("[REF-QUALITY-MONITOR] written to %s, %s, %s" % tuple(os.path.relpath(p, ROOT) for p in (out_path, OUT_CELLS, OUT_PROXY)))


# ── self-test on synthetic data ────────────────────────────────────────────────────────────────────────────────

class Synthetic:
    """A synthetic Data: 14 anchors x 4 caches, per-anchor reference rate planted, judge accuracy = 0.55 + 0.4 x ref_rate
    within ref-correct 0.93 flat; a planted b2 in the widener's synthetic edges."""

    def __init__(self, seed=3, planted_b2=4.0):
        rng = random.Random(seed); self.anchors = ["anc%02d" % i for i in range(14)]
        self.K = defaultdict(dict); self.P = defaultdict(dict); self.plur = {}; self.rows = {n: [] for n in ORDER}; self.by = {n: defaultdict(list) for n in ORDER}
        models = ["m%d" % i for i in range(12)]; qid = 0; mid = 0; self.anchor_qs = {}
        for i, anc in enumerate(self.anchors):
            ref_rate = 0.55 + 0.4 * i / 13; qs = []
            for _ in range(300):
                qid += 1; qs.append(qid)
                for m in models:
                    self.K[qid][m] = int(rng.random() < 0.5); self.P[qid][m] = rng.choice("ABCD")
                self.plur[qid] = rng.uniform(0.3, 0.9)
                rc = int(rng.random() < ref_rate)
                for name in ORDER:
                    for _ in range(3):
                        a, b = rng.sample(models, 2)
                        if self.K[qid][a] == self.K[qid][b]:
                            continue
                        good = a if self.K[qid][a] else b
                        p_ok = 0.93 if rc else 0.45
                        w = good if rng.random() < p_ok else (b if good == a else a)
                        mid += 1; r = dict(mid=mid, a=a, b=b, q=qid, w=w, inv=0, rc=rc, rl="A", anc=anc)
                        self.rows[name].append(r); self.by[name][anc].append(r)
            self.anchor_qs[anc] = qs
        self.judged = sorted(self.K); self.roster = models; self.planted_b2 = planted_b2; self.rng = np.random.default_rng(seed)

    def decidable(self, r):
        ka, kb = self.K[r["q"]].get(r["a"]), self.K[r["q"]].get(r["b"])
        return ka is not None and kb is not None and ka != kb

    def synthetic_edges(self):
        r = self.rng; es = []; b0, b1, b2 = -3.0, 2.0, self.planted_b2
        anchor_qs = {}; K12 = defaultdict(dict); P12 = defaultdict(dict)
        for i, anc in enumerate(self.anchors):
            anchor_qs[anc] = self.anchor_qs[anc]
            for q in anchor_qs[anc]:
                K12[q] = dict(self.K[q]); P12[q] = dict(self.P[q])
            for j in range(60):
                A = float(r.uniform(0.25, 0.95)); s = float(r.uniform(0.05, 0.4)); m = float(r.normal(0, 0.6)); Pp = float(r.uniform(0.3, 0.9))
                tau = math.exp(b0 + b1 * A + b2 * Pp)
                pw = norm.cdf(-abs(m) / math.sqrt(s ** 2 + tau ** 2))
                es.append(dict(anchor=anc, a="m%d" % (j % 12), b="m%d" % ((j // 12 + 1 + j) % 12), p=0.9, m=m, s=s, agree=A, gap=0.1, right=bool(r.random() >= pw), plur_true=Pp))
        return es, anchor_qs, K12, P12


def selftest():
    print("reserved_pool_id=%s (selftest: no cache of record is read)" % POOL)
    d = Synthetic()
    # planted rank correlation: per-anchor reference rate 0.55 -> 0.95 with accuracy tracking it
    cells = all_cells(d)
    keys = [(anc, n) for anc in d.anchors for n in ORDER]
    r, n = rho_over(cells, keys, "ref_rate", "accA")
    print("  [1] planted monotone accuracy(ref_rate) over %d synthetic cells: Spearman %+.3f (planted ~+1)" % (n, r)); assert r > 0.8
    refok = [cells[k]["accA_refok"] for k in keys]; accA = [cells[k]["accA"] for k in keys]
    ratio = (max(refok) - min(refok)) / (max(accA) - min(accA))
    print("  [2] planted flat within-ref-correct accuracy: range ratio %.3f (planted < 0.5)" % ratio); assert ratio < 0.5
    rng = random.Random(1); rs = [rho_over(all_cells(d, resample(d, rng)), keys, "ref_rate", "accA")[0] for _ in range(20)]
    print("  [3] question bootstrap (20 replicates): Spearman interval [%+.3f, %+.3f]" % (pct(rs, 0.025), pct(rs, 0.975))); assert pct(rs, 0.025) > 0.6
    # planted b2 in the proxy widener (edge_proxy overwritten by the planted P so the fit is on the planted covariate)
    es, aq, K12, P12 = d.synthetic_edges()
    for e in es:
        e["plur"] = e["plur_true"]
    arr = arrays(es)
    v = nllx((-3.0, 2.0, 0.0), *arr); ref = sb.nll((-3.0, 2.0), es); assert abs(v - ref) < 1e-6 * max(1, abs(ref))
    print("  [4] nllx == systematic_budget.nll at b2 = 0 on %d synthetic edges: OK" % len(es))
    full, null, dd = ddev_b2(arr)
    print("  [5] planted b0 -3.0 b1 +2.0 b2 %+.1f -> fitted b0 %+.3f b1 %+.3f b2 %+.3f | delta-deviance %.1f" % (d.planted_b2, full[0], full[1], full[2], dd))
    assert abs(full[2] - d.planted_b2) < 1.5 and dd > CHI1, "planted b2 not recovered"
    est_ids = {id(e) for e in es}
    oof = loao_x(es, est_ids, True, (full[0], full[1], full[2])); assert len(oof) == len(es) and all(0 <= v <= 1 for v in oof.values())
    print("  [6] LOAO plumbing on %d synthetic edges: OK" % len(es))
    power, ev = simulate_power_b2(es[:300], full[0], full[1], full[2], 20, np.random.default_rng(2))
    print("  [7] power simulator (20 sims on 300 edges): power %.2f, mean events %.1f: runs" % (power, ev))
    # the full readout on the synthetic data (edge_proxy then uses the synthetic plurality; b2 there is not planted, no assertion on it)
    print("  [8] full readout on synthetic data (boot 10, sims 10), no file written:")
    readout(10, 10, None, d=d, log=lambda s: print("      " + s), selftest=True)
    print("[SELFTEST] OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--boot", type=int, default=B_BOOT); ap.add_argument("--sims", type=int, default=N_SIM); ap.add_argument("--out", default=OUT)
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
