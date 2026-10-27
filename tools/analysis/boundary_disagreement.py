"""BOUNDARY-DISAGREEMENT (registered 2026-09-17 before any code; ZERO judge calls, reads caches of record only).

  python tools/analysis/boundary_disagreement.py --dry-run            # pool id, denominators, margin distribution; NO outcome numbers
  python tools/analysis/boundary_disagreement.py --run                # the readout -> experiment_results/x12_crossdomain/boundary_disagreement_outcome.txt
  python tools/analysis/boundary_disagreement.py --selftest           # the whole analysis on SYNTHETIC verdicts (no record number is produced)
  options: --frozen (add the frozen 20260727_042523 tree as a third, secondary margin), --boot B (default 2000),
           --stab-boot B (order-stability draws, default 2000), --pool p2dca21ab5f4ef3ae

QUESTION. Do judged questions that sit near a cell boundary of the tree (low routing margin) carry the judge
disagreement: more ties, more order flips, more INVALID verdicts, more wrong(established) verdicts, a less stable
model order?  If yes, dual-cell judging of boundary questions (the author's MULTI-OWNERSHIP idea) has a
mechanism and a bill; if no, that line closes at zero calls.

INSTRUMENT (per judged question q, computed at routing time, which the split allows).
  Tree of record for the boards: the promoted bareq512_s42 (experiment_results/promoted/bareq512_s42/seed_42,
  snapshot 20260909_212117_Headless_Run_Auto_ge in snapshots.db, 158 nodes / 87 leaves / sliceDim 512, split pool
  p2dca21ab5f4ef3ae = the pool of record, so the tree NEVER saw an eval question).  Evidence that the boards were
  fitted on it: systematic_budget.build() routes with r512.primary_routing("bareq512_s42"); every verdict cache's
  `anchor` column equals anchor_of(that routing) on all rows (checked 2026-09-17: 9,142 / 12,394 / 9,142 / 9,123 of
  9,142 / 12,394 / 9,142 / 9,123).  The caches' `node_id` column is the FROZEN tree's leaf that SCHEDULED the x12
  match (ratings_x12.db match_history, snapshot 20260727_042523_MAIN) - not the cell of record; the frozen tree is
  the incident tree (split p8a29, ~71% of the pool on its train side) and is offered only behind --frozen.
  Secondary tree: the anchor-free experiment_results/anchorfree/af/seed_42 (150 nodes / 81 leaves / sliceDim 256,
  2 depth-1 cells; manifest split pool p8a29d8f3ff75aa55, NOT the pool of record: part of the judged set was on its
  train side, so its margin is a DESCRIPTIVE secondary, flagged as such).
  Margins, the flatLeaf rule of anchor_free_readout (first-sliceDim slice of the stored 4096-d embedding, unit
  norm, cosine against every leaf's unit vmfMu; anchor_free_readout.sliced / full_vectors reused):
    leaf margin  m_leaf(q) = cos(best leaf) - cos(second-best leaf)                      PRIMARY
    depth-1 margin m_d1(q) = cos(best depth-1 centroid) - cos(second-best depth-1 centroid)   secondary
    record margin  m_rec(q) = cos(leaf of record) - max cos(any other leaf)             secondary (bareq512 only;
                   negative where the flatLeaf rule and the Kotlin routeReserved primary leaf disagree)
    two-candidate flag  = the Kotlin router listed 2 leaves for q (n_leaves = 2 in
                   experiment_results/promoted/bareq512_s42_reserved_leaf_assignments.csv)   the router's own
                   multi-owner set, binary, secondary
  Embeddings: embeddings_cache.db read-only, joined eval question_id -> mmlu_pro row by the OPTIONS key
  (whitespace-stripped option list, every model's options_json row tried, Meta-Llama-3-70B-Instruct excluded;
  questions whose option set matches several mmlu_pro rows are DROPPED and counted).  The cell for the fixed
  effects is the cell of record: the Kotlin primary leaf and its depth-1 anchor.

OUTCOMES (per question, from the verdict caches of record, all opened mode=ro; row semantics checked 2026-09-17:
  winner in {model_a, model_b, TIE, INVALID}; flip = 1 iff the two presentation orders disagreed (then winner = TIE,
  0 rows contradict); winner = TIE with flip = 0 iff both orders said TIE; invalid = 1 iff winner = INVALID = either
  order unparsed, and in the Kotlin cache also finish_reason in {length, content_filter}; the Mistral caches carry no
  finish column and 0 invalid rows; grok_calib has one row with finish2 = '' and a parsed verdict, kept as valid).
  Caches: x12 = stack_v2_promptv2_x12all.db (9,142 Mistral STACK-v2 verdicts, 2,811 judged questions, 66 pairs);
  x20 = stack_v2_promptv2_x20.db (12,394, 2,646 questions, 124 pairs with a new model, ZERO verdicts on the 66
  original pairs); merged = x12 + x20 = 21,536, the board of record (x20_merged.merged_rows); grok = grok_calib.db
  (9,142 grok-4-1-fast-non-reasoning verdicts on the x12 schedule, same match ids); kotlin = judge_wiring/board/
  kotlin_c0d3f708cbc3930e.db (9,123, the shipped path, same match ids as x12 on all 9,123).  Never one fit across
  judges: each cache is its own object.
  Per question: tie share (winner TIE, flip or both-tie), flip share, both-tie share, INVALID share, disagreement =
  1 - committed share; on the KEY-DECIDABLE matches (the two models' key correctness differs) the wrong count under
  convention A (TIE / INVALID count wrong; denominator every key-decidable match) and B (committed verdicts only);
  wrong(established) = the same on the matches whose (anchor, pair) edge is established by exact two-sided McNemar
  p < 0.05 on the anchor's JUDGED questions in that cache (systematic_budget.mcnemar_edge, integer arithmetic);
  cross-judge disagreement (x12 vs grok, x12 vs kotlin: winners differ on the same match id).

ANALYSIS. Quintiles of m_leaf over the primary population P0 (x12-judged questions with a margin; the same
  cut-points bin every cache, x20 / kotlin judged sets are subsets of x12's); each outcome per quintile with a
  question-clustered bootstrap 95% interval (B = 2,000, Random(42)) and the Q1 - Q5 difference with its interval;
  Spearman rho of m_leaf with the per-question tie share, flip share and disagreement (question bootstrap CI);
  logistic fits of flip (and tie) on z(m_leaf) with leaf fixed effects and with anchor fixed effects (within-cell;
  cells without variation in the outcome dropped and counted), cluster-robust SE by question; the same with the
  key difficulty of the question (mean ARENA12 key correctness) as a control, to separate "boundary" from "hard";
  model-order stability per quintile: the Bradley-Terry board of record (rejudge_grok.mm_fit, MM with the Jeffreys
  0.5 prior; a vectorised copy is asserted equal to it on every point fit) on the quintile's matches, Spearman with
  the key accuracy over the quintile's questions, and the bootstrap pairwise-order instability (share of model
  pairs whose order in a draw differs from the point board), Q1 vs Q5.  Outcome variables are never computed
  in --dry-run.

CRITERIA (scored on the merged Mistral board of record; x12, grok and kotlin are replications on one schedule).
  C1 concentration: tie share Q1 - Q5 >= +3pp AND flip share Q1 - Q5 >= +2pp, each with the bootstrap 95% interval
     excluding 0 -> HELD; interval excludes 0 but below the size -> WEAK; interval covers 0 and is narrower than
     twice the size (6pp / 4pp) -> FAILED; covers 0 and wider -> UNDETERMINED (power rule); upper bound < 0 ->
     REVERSED.  Power note written before the run: a quintile holds ~560 questions; on x12 alone (~1,850
     matches per quintile) the Q1 - Q5 tie difference has an expected 95% width near 7pp, so x12 alone may read
     UNDETERMINED; the merged board (~4,500 matches per quintile) is the object that resolves 3pp.
  C2 within-cell: the leaf-FE logistic coefficient of z(m_leaf) on flip is negative with the cluster-robust 95%
     interval excluding 0 -> HELD; else FAILED.  C2' (secondary): the same with the difficulty control.
  C3 wrong(established): Q1 - Q5 under convention A and under B, bootstrap 95% intervals both covering 0 -> HELD
     ("does not differ"); either excludes 0 -> FAILED (boundary questions are also where the judge is wrong).
  C4 order stability: pairwise instability Q1 - Q5 with the interval excluding 0 and positive -> boundary
     quintile less stable; else NOT SHOWN.
  Replication: the sign of C1 on x12 alone, grok and kotlin; UNDETERMINED where an interval is wider than the size.
  Resolution check: a Spearman or a rank is never read as a difference without its interval.

PREDICTIONS, BLIND (written before any outcome number existed).
  Caller (research-lead): lowest-margin quintile tie share 3-6pp above the highest, flip 2-4pp above;
     Spearman |rho| < 0.15; the within-cell effect survives; wrong(established) does not differ.
  Arena specialist (this script's author): the effect is mostly difficulty wearing a boundary costume.
     Q1 - Q5 tie +1 to +4pp; flip +1 to +3pp; Spearman |rho| < 0.10 for tie and flip; C2 HELD on the raw
     within-cell fit but C2' NOT HELD once key difficulty is controlled (the margin coefficient's interval covers
     0); wrong(established) Q1 - Q5 within +-2pp with both intervals covering 0; order instability Q1 - Q5 interval
     covers 0; the two-candidate flag moves the tie share by < 2pp with an interval covering 0; the grok and kotlin
     replications carry the same sign as x12 with intervals overlapping; the anchor-free m_leaf shows a weaker
     gradient than bareq512's (its 549-question leaf has no boundary to speak of).

FALSIFIER. If C1 FAILS on the merged board and on x12 (no tie or flip concentration in the low-margin quintile)
  or C2 FAILS (no within-cell effect), the mechanism behind MULTI-OWNERSHIP - that boundary questions are where the
  judge cannot decide - is overturned: dual-cell judging of low-margin questions would target nothing, and the
  line closes at zero calls (no E4 judged arm).  If C1 and C2 HOLD but C2' does not, the mechanism is question
  difficulty, not cell assignment: MULTI-OWNERSHIP would then be a difficulty targeting, and the bill for a
  dual-cell arm is stated (questions and matches in Q1 / the two-candidate set) but not launched.  If C3 FAILS in
  the direction of MORE wrong(established) at the boundary, the widener has a new predictor to register
  (SYSTEMATIC-BUDGET's tau(A) does not carry the margin), which is a separate registration.

HYGIENE. bareq512_s42 was built with reservedPoolFile = p2dca (manifest reserved_pool_id p2dca21ab5f4ef3ae, printed);
  the margin is a routing-time artefact of a held-out question, which rule 1 allows; nothing here induces anything
  over the reserved split; embeddings_cache.db, mmlu_pro_dataset_cache_v2.db, snapshots.db, snapshots_frozen.db and
  every verdict cache are opened read-only; the outcome file is written only if every cache holds exactly its row
  count of record (9,142 / 12,394 / 9,142 / 9,123); cost ZERO judge calls.
"""
import os, sys, re, csv, json, math, random, sqlite3, argparse, time
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard                                   # noqa: E402
import rejudge_grok as rj                           # noqa: E402  EVAL_DB, SNAP_ID, mm_fit, PRIOR
import rubric_512 as r512                           # noqa: E402  primary_routing, snapshot_id, load_graph, anchor_fn
import rubric_p8 as p8                              # noqa: E402  ARENA12
import stack_judge as sj                            # noqa: E402  cache_path
import x20_replications as xr                       # noqa: E402  X20
import systematic_budget as sb                      # noqa: E402  mcnemar_edge
import anchor_free_readout as afr                   # noqa: E402  full_vectors, sliced
import consensus_tree as ct                         # noqa: E402  last_snapshot

EXCLUDED_MODEL = "Meta-Llama-3-70B-Instruct"
TREE_REC = "bareq512_s42"
TREE_REC_DIR = os.path.join(ROOT, "experiment_results", "promoted", TREE_REC, "seed_42")
TREE_AF_DIR = os.path.join(ROOT, "experiment_results", "anchorfree", "af", "seed_42")
ROUTING_CSV = os.path.join(ROOT, "experiment_results", "promoted", "%s_reserved_leaf_assignments.csv" % TREE_REC)
FROZEN_DB = os.path.join(ROOT, "snapshots_frozen.db")
OUT_DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
OUT = os.path.join(OUT_DIR, "boundary_disagreement_outcome.txt")
OUT_PERQ = os.path.join(OUT_DIR, "boundary_disagreement_perq.csv")
EXPECTED_ROWS = {"x12": 9142, "x20": 12394, "grok": 9142, "kotlin": 9123}
NQ = 5
ALPHA_EST = 0.05
SEED = 42


def cache_paths():
    sj.PROMPT = "v2"; sj.ALL_X12 = True; sj.JUDGE = "mistral"; sj.DATACARD = False
    return {"x12": sj.cache_path(), "x20": xr.X20,
            "grok": os.path.join(OUT_DIR, "grok_calib.db"),
            "kotlin": os.path.join(ROOT, "experiment_results", "judge_wiring", "board", "kotlin_c0d3f708cbc3930e.db")}


def ro(path):
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


# ----------------------------------------------------------------------------------------------- eval side
def okey(o):
    """OPTIONS key: the JSON option list with each option whitespace-stripped (eval_results.options_json differs
    across model files by whitespace only; free_tests_f4_f7.okey without the strip loses 147 pool questions)."""
    try:
        v = json.loads(o)
        if isinstance(v, list):
            return json.dumps([str(x).strip() for x in v])
    except Exception:
        pass
    return (o or "").strip()


def eval_join(pool):
    """pool question_id -> mmlu_pro question text by the OPTIONS key; the key K[q][m]; stats of the join."""
    ev = ro(rj.EVAL_DB)
    opts2text = defaultdict(set)
    for _, t, o in ev.execute("SELECT id, question, options FROM mmlu_pro"):
        opts2text[okey(o)].add(t)
    cand = defaultdict(set)
    for q, o in ev.execute("SELECT DISTINCT question_id, options_json FROM eval_results WHERE model_name != ?", (EXCLUDED_MODEL,)):
        if q in pool:
            for t in opts2text.get(okey(o), ()):
                cand[q].add(t)
    text = {q: next(iter(ts)) for q, ts in cand.items() if len(ts) == 1}
    ambiguous = sorted(q for q, ts in cand.items() if len(ts) > 1)
    none = sorted(q for q in pool if not cand.get(q))
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results WHERE model_name != ?", (EXCLUDED_MODEL,)):
        if q in pool:
            K[q][m] = int(c or 0)
    ev.close()
    return text, K, dict(unique=len(text), ambiguous=ambiguous, none=none)


# ----------------------------------------------------------------------------------------------- trees
def tree_from_nodes(nodes, name, manifest=None):
    """The same object anchor_free_readout.load_tree builds, from a list of node dicts (run-dir snapshot or a
    snapshots DB graph; leaf = isLeaf when present, else no childIds)."""
    byid = {n["id"]: n for n in nodes}
    kid2parent = {c: n["id"] for n in nodes for c in n.get("childIds", [])}

    def is_leaf(n):
        return bool(n["isLeaf"]) if "isLeaf" in n else not n.get("childIds")

    def depth1(nid):
        n = byid[nid]
        while n["depth"] > 1:
            n = byid[kid2parent[n["id"]]]
        return n["id"]
    leaves = [n for n in nodes if is_leaf(n)]
    d1 = [n for n in nodes if n["depth"] == 1]
    dims = {n.get("sliceDim", len(n["vmfMu"])) for n in leaves}
    if len(dims) != 1:
        raise SystemExit("[BOUNDARY] %s: leaves carry several sliceDims %s" % (name, sorted(dims)))
    dim = dims.pop()
    if any(len(n["vmfMu"]) != dim for n in leaves):
        raise SystemExit("[BOUNDARY] %s: vmfMu length differs from sliceDim %d" % (name, dim))

    def unit(M):
        M = np.asarray(M, dtype=np.float64)
        n = np.linalg.norm(M, axis=1, keepdims=True); n[n == 0] = 1.0
        return M / n
    return dict(name=name, nodes=len(nodes), byid=byid, leaves=leaves, leaf_ids=[n["id"] for n in leaves],
                leaf_mu=unit([n["vmfMu"] for n in leaves]), leaf_d1={n["id"]: depth1(n["id"]) for n in leaves},
                d1_ids=[n["id"] for n in d1], d1_mu=unit([n["vmfMu"] for n in d1]) if d1 else np.zeros((0, dim)),
                label={n["id"]: n.get("label", n["id"]) for n in nodes}, dim=dim, manifest=manifest or {},
                depth=max(n["depth"] for n in nodes))


def tree_from_run_dir(run_dir, name):
    snap = ct.last_snapshot(run_dir)
    mp = os.path.join(run_dir, "diagnostics", "run_manifest.json")
    manifest = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
    t = tree_from_nodes(snap["nodes"], name, manifest)
    t["iteration"] = snap["iteration"]; t["run_dir"] = run_dir
    return t


def tree_frozen():
    con = ro(FROZEN_DB)
    g = json.loads(con.execute("SELECT graph FROM snapshots WHERE id=?", (rj.SNAP_ID,)).fetchone()[0])
    con.close()
    lst = g["nodes"]; lst = lst if isinstance(lst, list) else list(lst.values())
    t = tree_from_nodes(lst, "frozen_" + rj.SNAP_ID[:15], {"reserved_pool_id": "p8a29d8f3ff75aa55 (incident tree)"})
    t["iteration"] = -1; t["run_dir"] = FROZEN_DB
    return t


def check_tree_of_record(tree, route):
    """The run dir's last snapshot is the snapshot the routing CSV was made from: same 87 leaf ids as the CSV, and
    leaf mus equal (1e-5) to snapshots.db's graph for snapshot_id(bareq512_s42)."""
    sid = r512.snapshot_id(TREE_REC)
    g = r512.load_graph(sid)
    csv_leaves = set(route.values())
    if not csv_leaves <= set(tree["leaf_ids"]):
        raise SystemExit("[BOUNDARY] routing CSV names leaves absent from the run dir's last snapshot")
    if not csv_leaves <= set(g):
        raise SystemExit("[BOUNDARY] routing CSV names leaves absent from snapshots.db %s" % sid)
    d = max(float(np.abs(np.asarray(tree["byid"][l]["vmfMu"]) - np.asarray(g[l]["vmfMu"])).max()) for l in csv_leaves)
    if d > 1e-5:
        raise SystemExit("[BOUNDARY] run-dir vmfMu differs from snapshots.db by %.2e" % d)
    return sid, len(csv_leaves), d


def kotlin_candidates():
    """question -> number of leaves the Kotlin router listed (the CSV is written with a locale comma inside the
    weight field, so csv.DictReader misaligns the columns; parsed by regex on the raw line)."""
    pat = re.compile(r'^(\d+),"([^"]*)",(\w+),"([^"]*)",(-?\d+,\d+),(\d+)$')
    n_leaves = {}; second = {}
    for line in open(ROUTING_CSV, encoding="utf-8").read().splitlines()[1:]:
        m = pat.match(line)
        if not m:
            raise SystemExit("[BOUNDARY] unparsed routing line: %s" % line[:80])
        q = int(m.group(1)); n_leaves[q] = int(m.group(6))
        second.setdefault(q, []).append((float(m.group(5).replace(",", ".")), m.group(3)))
    return n_leaves, second


# ----------------------------------------------------------------------------------------------- margins
def margins_for(tree, Q, qs, route=None):
    S = Q @ tree["leaf_mu"].T
    order = np.argsort(-S, axis=1)
    i1, i2 = order[:, 0], order[:, 1]
    ar = np.arange(len(qs))
    out = dict(leaf_margin=S[ar, i1] - S[ar, i2], leaf_best=[tree["leaf_ids"][i] for i in i1],
               leaf_second=[tree["leaf_ids"][i] for i in i2])
    if len(tree["d1_ids"]) >= 2:
        S1 = Q @ tree["d1_mu"].T
        o1 = np.argsort(-S1, axis=1)
        out["d1_margin"] = S1[ar, o1[:, 0]] - S1[ar, o1[:, 1]]
    else:
        out["d1_margin"] = np.full(len(qs), np.nan)
    if route is not None:
        idx = {l: i for i, l in enumerate(tree["leaf_ids"])}
        rec = np.full(len(qs), np.nan)
        for k, q in enumerate(qs):
            l = route.get(q)
            if l in idx:
                s = S[k].copy(); own = s[idx[l]]; s[idx[l]] = -np.inf
                rec[k] = own - s.max()
        out["rec_margin"] = rec
    return out


# ----------------------------------------------------------------------------------------------- caches
def load_cache(name, path):
    con = ro(path)
    cols = [d[1] for d in con.execute("PRAGMA table_info(verdicts)")]
    has_fin = "finish1" in cols
    sql = "SELECT match_id, model_a, model_b, qid, anchor, winner, flip, invalid%s FROM verdicts" % (", finish1, finish2" if has_fin else "")
    rows = []
    for r in con.execute(sql):
        mid, a, b, q, anc, w, fl, inv = r[:8]
        fin = (r[8], r[9]) if has_fin else ("stop", "stop")
        if a == EXCLUDED_MODEL or b == EXCLUDED_MODEL:
            raise SystemExit("[BOUNDARY] %s carries %s" % (name, EXCLUDED_MODEL))
        inv = int(inv or 0)
        if inv and w != "INVALID":
            raise SystemExit("[BOUNDARY] %s: invalid row with winner %s" % (name, w))
        if not inv and w not in (a, b, "TIE"):
            raise SystemExit("[BOUNDARY] %s: valid row with winner %s" % (name, w))
        if int(fl or 0) and w != "TIE":
            raise SystemExit("[BOUNDARY] %s: flip row with winner %s" % (name, w))
        rows.append(dict(mid=mid, a=a, b=b, q=q, anchor=anc, w=w, flip=int(fl or 0), invalid=inv,
                         nonstop=int(fin[0] not in ("stop",) or fin[1] not in ("stop",)),
                         tie=int(w == "TIE"), both=int(w == "TIE" and not fl), committed=int(w in (a, b))))
    con.close()
    return rows


def established_edges(rows, K):
    """(anchor, frozenset{a,b}) edges established by exact two-sided McNemar p < 0.05 on the anchor's JUDGED
    questions in THIS cache (valid rows), systematic_budget.mcnemar_edge."""
    anchor_qs = defaultdict(set); pairs = set()
    for r in rows:
        if not r["invalid"]:
            anchor_qs[r["anchor"]].add(r["q"]); pairs.add((r["anchor"], r["a"], r["b"]))
    anchor_qs = {a: sorted(v) for a, v in anchor_qs.items()}
    est = set(); tested = 0
    for anc, a, b in sorted(pairs):
        key = (anc, frozenset((a, b)))
        if key in est:
            continue
        tested += 1
        p, _, _ = sb.mcnemar_edge(dict(anchor=anc, a=a, b=b), K, anchor_qs)
        if p < ALPHA_EST:
            est.add(key)
    return est, tested, anchor_qs


def per_question(rows, K, est):
    """Per-question sums of every outcome; the per-match key-decidable / wrong flags come along for the FE fit."""
    agg = defaultdict(lambda: Counter())
    for r in rows:
        q = r["q"]; c = agg[q]
        c["n"] += 1; c["tie"] += r["tie"]; c["flip"] += r["flip"]; c["both"] += r["both"]
        c["invalid"] += r["invalid"]; c["nonstop"] += r["nonstop"]; c["committed"] += r["committed"]
        ka = K.get(q, {}).get(r["a"]); kb = K.get(q, {}).get(r["b"])
        r["kd"] = 0; r["wrongA"] = 0; r["wrongB"] = 0; r["est"] = 0
        if ka is not None and kb is not None and ka != kb:
            right = r["a"] if ka > kb else r["b"]
            r["kd"] = 1; r["wrongA"] = int(r["w"] != right)
            r["wrongB"] = int(r["committed"] and r["w"] != right)
            r["est"] = int((r["anchor"], frozenset((r["a"], r["b"]))) in est)
            c["kd"] += 1; c["wrongA"] += r["wrongA"]; c["kdB"] += r["committed"]; c["wrongB"] += r["wrongB"]
            if r["est"]:
                c["est_kd"] += 1; c["est_wrongA"] += r["wrongA"]; c["est_kdB"] += r["committed"]; c["est_wrongB"] += r["wrongB"]
    return agg


# ----------------------------------------------------------------------------------------------- statistics
def boot_ratio(num, den, B, rng):
    """question-clustered bootstrap of sum(num)/sum(den); returns (point, lo, hi, draws)."""
    num = np.asarray(num, float); den = np.asarray(den, float); n = len(num)
    if n == 0 or den.sum() == 0:
        return float("nan"), float("nan"), float("nan"), np.full(B, np.nan)
    idx = rng.integers(0, n, size=(B, n))
    d = num[idx].sum(1) / np.maximum(den[idx].sum(1), 1e-12)
    return float(num.sum() / den.sum()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)), d


def ci_of(draws):
    return float(np.nanpercentile(draws, 2.5)), float(np.nanpercentile(draws, 97.5))


def boot_spearman(x, y, B, rng):
    x = np.asarray(x, float); y = np.asarray(y, float); n = len(x)
    if n < 10:
        return float("nan"), float("nan"), float("nan")
    r0 = spearmanr(x, y).correlation
    idx = rng.integers(0, n, size=(B, n))
    rs = []
    for i in range(B):
        xi = x[idx[i]]; yi = y[idx[i]]
        if xi.std() == 0 or yi.std() == 0:
            rs.append(np.nan)
        else:
            rs.append(spearmanr(xi, yi).correlation)
    return float(r0), float(np.nanpercentile(rs, 2.5)), float(np.nanpercentile(rs, 97.5))


def logit_fe(y, X, cell, cluster):
    """Logistic regression of y on X plus one dummy per cell (no intercept), IRLS; cluster-robust sandwich SE by
    `cluster`. Rows in cells with no variation in y are dropped (perfect separation). Returns dict with the
    coefficients of X, their SEs, n rows used, cells used, cells dropped, converged flag."""
    y = np.asarray(y, float); X = np.atleast_2d(np.asarray(X, float))
    if X.shape[0] != len(y):
        X = X.T
    cell = np.asarray(cell); cluster = np.asarray(cluster)
    all_cells = set(cell)
    keep_cells = {c for c in all_cells if 0 < y[cell == c].mean() < 1}
    n_dropped_cells = len(all_cells) - len(keep_cells)
    keep = np.array([c in keep_cells for c in cell])
    y, X, cell, cluster = y[keep], X[keep], cell[keep], cluster[keep]
    cells = sorted(keep_cells); cidx = {c: i for i, c in enumerate(cells)}
    D = np.zeros((len(y), len(cells)))
    D[np.arange(len(y)), [cidx[c] for c in cell]] = 1.0
    Z = np.hstack([X, D]); k = X.shape[1]
    beta = np.zeros(Z.shape[1]); conv = False
    for _ in range(100):
        eta = Z @ beta; p = 1 / (1 + np.exp(-eta)); w = p * (1 - p)
        H = Z.T @ (Z * w[:, None]) + 1e-9 * np.eye(Z.shape[1])
        g = Z.T @ (y - p)
        step = np.linalg.solve(H, g)
        beta += step
        if np.abs(step).max() < 1e-9:
            conv = True; break
    eta = Z @ beta; p = 1 / (1 + np.exp(-eta)); w = p * (1 - p)
    H = Z.T @ (Z * w[:, None]) + 1e-9 * np.eye(Z.shape[1])
    bread = np.linalg.inv(H)
    S = Z * (y - p)[:, None]
    meat = np.zeros_like(H)
    order = np.argsort(cluster, kind="stable"); cl = cluster[order]; Ss = S[order]
    bounds = np.flatnonzero(np.r_[True, cl[1:] != cl[:-1], True])
    for s, e in zip(bounds[:-1], bounds[1:]):
        u = Ss[s:e].sum(0); meat += np.outer(u, u)
    V = bread @ meat @ bread
    se = np.sqrt(np.maximum(np.diag(V)[:k], 0))
    return dict(beta=beta[:k], se=se, n=len(y), keep_cells=len(cells), dropped_cells=n_dropped_cells, converged=conv)


def mm_arrays(agg, models):
    """(W, N) of rejudge_grok.mm_fit: W[i] = wins + prior per pair the model is in; N[i, j] = n + 2 prior."""
    idx = {m: i for i, m in enumerate(models)}; M = len(models)
    W = np.zeros(M); N = np.zeros((M, M))
    for (a, b), (wa, n) in agg.items():
        i, j = idx[a], idx[b]
        W[i] += wa + rj.PRIOR; W[j] += (n - wa) + rj.PRIOR
        N[i, j] += n + 2 * rj.PRIOR; N[j, i] += n + 2 * rj.PRIOR
    return W, N


def mm_fit_np(agg, models):
    """rejudge_grok.mm_fit (MM for Bradley-Terry with the Jeffreys 0.5 prior) vectorised; asserted equal to the
    original on every point fit this script publishes."""
    return mm_fit_arrays(*mm_arrays(agg, models), models)


def mm_fit_arrays(W, N, models):
    M = len(models)
    p = np.ones(M)
    for _ in range(2000):
        den = (N / (p[:, None] + p[None, :])).sum(1)
        new = np.where(den > 0, W / np.where(den > 0, den, 1.0), p)
        new = new / new.mean()
        if np.abs(new - p).max() < 1e-12:
            p = new; break
        p = new
    th = np.log(np.maximum(p, 1e-300))
    return dict(zip(models, th - th.mean()))


def agg_from(rows):
    agg = defaultdict(lambda: [0.0, 0.0])
    for r in rows:
        if r["invalid"]:
            continue
        a, b = r["a"], r["b"]; wa = 0.5 if r["w"] == "TIE" else (1.0 if r["w"] == a else 0.0)
        if a > b:
            a, b, wa = b, a, 1.0 - wa
        agg[(a, b)][0] += wa; agg[(a, b)][1] += 1.0
    return {k: tuple(v) for k, v in agg.items()}


def order_stability(rows, K, models, B, rng):
    """Point board on the rows (rejudge_grok.mm_fit of record, checked against the vectorised copy), Spearman with
    the key accuracy over the rows' questions, and the question-clustered bootstrap pairwise instability (share of
    model pairs whose order in a draw differs from the point board). The bootstrap resamples questions: each draw's
    (W, N) are the multinomial question weights applied to per-question win / count tallies, the same MM."""
    byq = defaultdict(list)
    for r in rows:
        byq[r["q"]].append(r)
    qs = sorted(byq); M = len(models); idx = {m: i for i, m in enumerate(models)}
    agg = agg_from(rows)
    ref = rj.mm_fit(agg, models); fast = mm_fit_np(agg, models)
    dmax = max(abs(ref[m] - fast[m]) for m in models)
    if dmax > 1e-6:
        raise SystemExit("[BOUNDARY] vectorised MM differs from rejudge_grok.mm_fit by %.2e" % dmax)
    # per-question tallies: wins per model (row q, col model) and counts per ordered pair (row q, col i*M+j)
    Wq = np.zeros((len(qs), M)); Nq = np.zeros((len(qs), M * M))
    for k, q in enumerate(qs):
        for r in byq[q]:
            if r["invalid"]:
                continue
            i, j = idx[r["a"]], idx[r["b"]]
            wa = 0.5 if r["w"] == "TIE" else (1.0 if r["w"] == r["a"] else 0.0)
            Wq[k, i] += wa; Wq[k, j] += 1.0 - wa
            Nq[k, i * M + j] += 1.0; Nq[k, j * M + i] += 1.0
    def draw_arrays(c):
        """(W, N) of mm_fit on the rows resampled with question multiplicities c: the Jeffreys prior enters once per
        UNORDERED pair present in the draw, exactly as board_from -> mm_fit adds it per pair key."""
        W = c @ Wq; N = (c @ Nq).reshape(M, M)
        present = (N > 0).astype(float)
        return W + rj.PRIOR * present.sum(1), N + 2 * rj.PRIOR * present
    acc = {}
    for m in models:
        v = [K[q][m] for q in qs if m in K.get(q, {})]
        if v:
            acc[m] = sum(v) / len(v)
    ms = [m for m in models if m in acc]
    accv = [acc[m] for m in ms]
    rho = spearmanr([ref[m] for m in ms], accv).correlation if len(ms) >= 3 else float("nan")
    iu = np.triu_indices(M, 1)
    ref_v = np.array([ref[m] for m in models]); ref_sign = np.sign(ref_v[:, None] - ref_v[None, :])[iu]
    inst = np.zeros(B); rhos = np.full(B, np.nan)
    for b in range(B):
        c = rng.multinomial(len(qs), np.full(len(qs), 1.0 / len(qs))).astype(float)
        W, N = draw_arrays(c)
        th = mm_fit_arrays(W, N, models)
        if b == 0:                                    # the first draw is also fitted the record's way (rows -> mm_fit)
            sub = [r for k, q in enumerate(qs) for _ in range(int(c[k])) for r in byq[q]]
            chk = rj.mm_fit(agg_from(sub), models)
            d1 = max(abs(chk[m] - th[m]) for m in models)
            if d1 > 1e-6:
                raise SystemExit("[BOUNDARY] bootstrap draw arrays differ from rows -> mm_fit by %.2e" % d1)
            dmax = max(dmax, d1)
        v = np.array([th[m] for m in models])
        inst[b] = float((np.sign(v[:, None] - v[None, :])[iu] != ref_sign).mean())
        if len(ms) >= 3:
            rhos[b] = spearmanr([th[m] for m in ms], accv).correlation
    return dict(rho=float(rho), rho_lo=float(np.nanpercentile(rhos, 2.5)), rho_hi=float(np.nanpercentile(rhos, 97.5)),
                inst=float(inst.mean()), inst_draws=inst, n_q=len(qs), n_m=len(rows), mm_diff=dmax)


# ----------------------------------------------------------------------------------------------- the study
class Study:
    def __init__(self, pool_id, frozen=False, boot=2000, stab_boot=2000):
        self.L = []
        self.pool_id = pool_id; self.B = boot; self.SB = stab_boot; self.frozen = frozen

    def say(self, s=""):
        self.L.append(s); print(s, flush=True)

    # ---- structural part (dry-run and run alike; no outcome numbers)
    def prepare(self):
        say = self.say
        pid = pool_guard.assert_pool_of_record(self.pool_id)
        say("pool of record: %s (pool_guard.assert_pool_of_record)" % pid)
        say("=== BOUNDARY-DISAGREEMENT (registered 2026-09-17; ZERO judge calls) ===")
        pool = pool_guard.eval_ids(pid)
        text, K, js = eval_join(pool)
        self.pool, self.text, self.K = pool, text, K
        say("  eval join by the OPTIONS key (whitespace-stripped, every model's options_json row, %s excluded): pool %d -> unique mmlu_pro text %d, ambiguous (dropped) %d, none %d"
            % (EXCLUDED_MODEL, len(pool), js["unique"], len(js["ambiguous"]), len(js["none"])))

        route = r512.primary_routing(TREE_REC)
        nodes = r512.load_graph(r512.snapshot_id(TREE_REC)); anchor_of = r512.anchor_fn(nodes)
        self.route = route; self.anchor_of = anchor_of
        trees = {TREE_REC: tree_from_run_dir(TREE_REC_DIR, TREE_REC), "af_s42": tree_from_run_dir(TREE_AF_DIR, "af_s42")}
        if self.frozen:
            trees["frozen"] = tree_frozen()
        self.trees = trees
        sid, nl, dmu = check_tree_of_record(trees[TREE_REC], route)
        say("  tree of record %s: run dir %s, snapshot %s, %d nodes / %d leaves / sliceDim %d / depth %d; routing CSV names %d leaves; run-dir vs snapshots.db |dmu| max %.1e; manifest split pool %s%s"
            % (TREE_REC, os.path.relpath(TREE_REC_DIR, ROOT), sid, trees[TREE_REC]["nodes"], len(trees[TREE_REC]["leaves"]), trees[TREE_REC]["dim"],
               trees[TREE_REC]["depth"], nl, dmu, trees[TREE_REC]["manifest"].get("reserved_pool_id"),
               " = the pool of record (clean: the tree never saw an eval question)" if trees[TREE_REC]["manifest"].get("reserved_pool_id") == pid else " (NOT the pool of record)"))
        for nm, t in trees.items():
            if nm == TREE_REC:
                continue
            say("  secondary tree %s: %d nodes / %d leaves / %d depth-1 cells / sliceDim %d; manifest split pool %s%s"
                % (nm, t["nodes"], len(t["leaves"]), len(t["d1_ids"]), t["dim"], t["manifest"].get("reserved_pool_id"),
                   "" if t["manifest"].get("reserved_pool_id") == pid else " (NOT the pool of record: part of the judged set was on this tree's TRAIN side; descriptive only)"))
        say("  depth-1 cells of the tree of record: %d (%s)" % (len(trees[TREE_REC]["d1_ids"]), ", ".join(trees[TREE_REC]["label"][i][:14] for i in trees[TREE_REC]["d1_ids"])))

        # caches
        self.caches = {}
        for nm, path in cache_paths().items():
            if not os.path.exists(path):
                raise SystemExit("[BOUNDARY] cache missing: %s" % path)
            rows = load_cache(nm, path)
            self.caches[nm] = rows
            say("  cache %-6s %s: %d rows (record %d)%s | %d judged questions | %d models | %d anchors | anchor == anchor_of(Kotlin primary leaf) on %d rows"
                % (nm, os.path.relpath(path, ROOT), len(rows), EXPECTED_ROWS[nm], "" if len(rows) == EXPECTED_ROWS[nm] else " ROW COUNT DIFFERS FROM THE RECORD",
                   len({r["q"] for r in rows}), len({r["a"] for r in rows} | {r["b"] for r in rows}), len({r["anchor"] for r in rows}),
                   sum(1 for r in rows if r["q"] in route and anchor_of(route[r["q"]]) == r["anchor"])))
        self.caches["merged"] = self.caches["x12"] + self.caches["x20"]
        say("  cache merged: x12 + x20 = %d rows (the board of record, x20_merged.merged_rows), %d judged questions, %d models"
            % (len(self.caches["merged"]), len({r["q"] for r in self.caches["merged"]}), len({r["a"] for r in self.caches["merged"]} | {r["b"] for r in self.caches["merged"]})))
        jx = {r["q"] for r in self.caches["x12"]}
        for nm in ("x20", "grok", "kotlin"):
            s = {r["q"] for r in self.caches[nm]}
            say("  judged set %s subset of x12's: %s (%d of %d)" % (nm, s <= jx, len(s & jx), len(s)))
        self.judged_all = jx | {r["q"] for r in self.caches["x20"]}
        if not self.judged_all <= pool:
            raise SystemExit("[BOUNDARY] judged questions outside the pool of record")

        # margins on the judged questions with a text and an embedding
        want = sorted(q for q in self.judged_all if q in text)
        vec = afr.full_vectors([text[q] for q in want])
        qs = [q for q in want if text[q] in vec]
        self.qs = qs
        say("  judged questions (x12 u x20) %d; with OPTIONS-key text %d; with an embedding %d = the margin population" % (len(self.judged_all), len(want), len(qs)))
        self.M = {}
        for nm, t in trees.items():
            Q = afr.sliced(vec, [text[q] for q in qs], t["dim"])
            self.M[nm] = margins_for(t, Q, qs, route if nm == TREE_REC else None)
        n_leaves, second = kotlin_candidates()
        self.two = np.array([1 if n_leaves.get(q, 1) > 1 else 0 for q in qs])
        self.cell = [route[q] for q in qs]; self.anchor = [anchor_of(route[q]) for q in qs]
        self.qpos = {q: i for i, q in enumerate(qs)}
        # primary population and quintile cut-points
        P0 = np.array([q in jx for q in qs])
        self.P0 = P0
        m = self.M[TREE_REC]["leaf_margin"]
        self.cuts = np.percentile(m[P0], [20, 40, 60, 80])
        self.quint = np.searchsorted(self.cuts, m, side="right")            # 0 = lowest margin
        self.cuts_af = np.percentile(self.M["af_s42"]["leaf_margin"][P0], [20, 40, 60, 80])
        self.quint_af = np.searchsorted(self.cuts_af, self.M["af_s42"]["leaf_margin"], side="right")
        self.cuts_d1 = np.percentile(self.M[TREE_REC]["d1_margin"][P0], [20, 40, 60, 80])
        self.quint_d1 = np.searchsorted(self.cuts_d1, self.M[TREE_REC]["d1_margin"], side="right")

        say("")
        say("  MARGIN DISTRIBUTION on the primary population P0 = x12-judged questions with a margin, n = %d (no outcome numbers here)" % int(P0.sum()))
        for nm in trees:
            for key in ("leaf_margin", "d1_margin", "rec_margin"):
                v = self.M[nm].get(key)
                if v is None or np.all(np.isnan(v)):
                    continue
                v = v[P0]
                say("    %-12s %-11s min %.4f | p10 %.4f | p25 %.4f | median %.4f | p75 %.4f | p90 %.4f | max %.4f%s"
                    % (nm, key, v.min(), *np.percentile(v, [10, 25, 50, 75, 90]), v.max(),
                       " | negative (flatLeaf and Kotlin disagree) %d" % int((v < 0).sum()) if key == "rec_margin" else ""))
        say("    quintile cut-points of %s leaf margin: %s (Q1 = lowest margin = nearest a boundary)" % (TREE_REC, ", ".join("%.4f" % c for c in self.cuts)))
        say("    quintile cut-points of af_s42 leaf margin: %s" % ", ".join("%.4f" % c for c in self.cuts_af))
        say("    quintile cut-points of %s depth-1 margin: %s" % (TREE_REC, ", ".join("%.4f" % c for c in self.cuts_d1)))
        agree = sum(1 for k, q in enumerate(qs) if P0[k] and self.M[TREE_REC]["leaf_best"][k] == route.get(q))
        second_hit = sum(1 for k, q in enumerate(qs) if P0[k] and self.M[TREE_REC]["leaf_second"][k] == route.get(q))
        say("    flatLeaf best leaf == Kotlin primary leaf (cell of record): %d of %d; Kotlin leaf is the flatLeaf second-best: %d" % (agree, int(P0.sum()), second_hit))
        say("    Kotlin two-candidate questions (n_leaves = 2 in the routing CSV): pool %d of %d; P0 %d of %d"
            % (sum(1 for q in pool if n_leaves.get(q, 1) > 1), len(pool), int(self.two[P0].sum()), int(P0.sum())))
        # per-anchor median margin and quintile composition (structural)
        say("    per-anchor (cell of record) median leaf margin and share of its questions in Q1:")
        by_anc = defaultdict(list)
        for k, q in enumerate(qs):
            if P0[k]:
                by_anc[self.anchor[k]].append(k)
        for anc in sorted(by_anc, key=lambda a: -len(by_anc[a])):
            ks = by_anc[anc]
            say("      %-17s n %4d | median margin %.4f | in Q1 %.1f%%" % (anc, len(ks), float(np.median(m[ks])), 100 * float(np.mean(self.quint[ks] == 0))))
        for nm, rows in (("x12", self.caches["x12"]), ("merged", self.caches["merged"])):
            nq1 = sum(1 for q in set(r["q"] for r in rows) if q in self.qpos and self.quint[self.qpos[q]] == 0)
            nm1 = sum(1 for r in rows if r["q"] in self.qpos and self.quint[self.qpos[r["q"]]] == 0)
            ntwo = sum(1 for r in rows if r["q"] in self.qpos and self.two[self.qpos[r["q"]]])
            say("    the MULTI-OWNERSHIP bill on %s if it targeted Q1: %d questions, %d matches (x2 calls dual order); the Kotlin two-candidate set: %d matches" % (nm, nq1, nm1, ntwo))
        return self

    # ---- the readout (only with --run)
    def readout(self):
        say = self.say; K = self.K; qs = self.qs; rng = np.random.default_rng(SEED)
        expected = getattr(self, "expected", EXPECTED_ROWS)
        for nm in expected:
            if len(self.caches[nm]) != expected[nm]:
                raise SystemExit("[BOUNDARY] %s holds %d rows, record %d: partial or altered cache, readout refused" % (nm, len(self.caches[nm]), expected[nm]))
        m_leaf = self.M[TREE_REC]["leaf_margin"]; z = (m_leaf - m_leaf[self.P0].mean()) / m_leaf[self.P0].std()
        diff = np.array([np.mean([K[q][m] for m in sorted(p8.ARENA12) if m in K.get(q, {})]) if K.get(q) else np.nan for q in qs])
        diff_z = (diff - np.nanmean(diff)) / np.nanstd(diff)
        self.crit = {}
        say("")
        say("=== READOUT (bootstrap B = %d question-clustered, Random seed %d; wrong counts written wrong(established)) ===" % (self.B, SEED))
        results = {}
        for cname in ("x12", "merged", "grok", "kotlin", "x20"):
            rows = [r for r in self.caches[cname] if r["q"] in self.qpos]
            n_drop = len(self.caches[cname]) - len(rows)
            est, tested, anchor_qs = established_edges(rows, K)
            agg = per_question(rows, K, est)
            qlist = sorted(agg); pos = np.array([self.qpos[q] for q in qlist])
            A = {k: np.array([agg[q][k] for q in qlist], float) for k in
                 ("n", "tie", "flip", "both", "invalid", "committed", "kd", "wrongA", "kdB", "wrongB", "est_kd", "est_wrongA", "est_kdB", "est_wrongB")}
            say("")
            say("--- cache %s: %d matches on %d questions with a margin (%d matches on questions without one dropped); %d anchors; %d edges tested, %d established (McNemar p < %.2f on the anchor's judged questions in this cache); INVALID rows %d; non-stop finish rows %d"
                % (cname, len(rows), len(qlist), n_drop, len(anchor_qs), tested, len(est), ALPHA_EST, int(A["invalid"].sum()), sum(r["nonstop"] for r in rows)))
            res = {}
            for mname, quint in (("leaf_margin[%s]" % TREE_REC, self.quint), ("d1_margin[%s]" % TREE_REC, self.quint_d1), ("leaf_margin[af_s42]", self.quint_af)):
                qq = quint[pos]
                say("  quintiles of %s (Q1 = lowest margin):" % mname)
                say("    %-4s %5s %6s | %-24s %-24s %-24s %-24s | %-24s %-24s | %-24s %-24s" % ("Q", "n_q", "n_m", "tie", "flip", "both-tie", "INVALID", "wrongA (kd)", "wrongB (committed kd)", "wrong(est) A", "wrong(est) B"))
                table = {}
                for qi in range(NQ):
                    sel = qq == qi
                    row = {}
                    for key, num, den in (("tie", "tie", "n"), ("flip", "flip", "n"), ("both", "both", "n"), ("invalid", "invalid", "n"),
                                          ("wrongA", "wrongA", "kd"), ("wrongB", "wrongB", "kdB"), ("est_wrongA", "est_wrongA", "est_kd"), ("est_wrongB", "est_wrongB", "est_kdB")):
                        row[key] = boot_ratio(A[num][sel], A[den][sel], self.B, rng)
                    row["n_q"] = int(sel.sum()); row["n_m"] = int(A["n"][sel].sum()); row["kd"] = int(A["kd"][sel].sum()); row["est_kd"] = int(A["est_kd"][sel].sum())
                    table[qi] = row
                    f = lambda k: "%.3f [%.3f, %.3f]" % row[k][:3]
                    say("    Q%d   %5d %6d | %-24s %-24s %-24s %-24s | %-24s %-24s | %-24s %-24s" % (qi + 1, row["n_q"], row["n_m"], f("tie"), f("flip"), f("both"), f("invalid"), f("wrongA"), f("wrongB"), f("est_wrongA"), f("est_wrongB")))
                say("    key-decidable matches per quintile: %s; established key-decidable: %s"
                    % (", ".join(str(table[i]["kd"]) for i in range(NQ)), ", ".join(str(table[i]["est_kd"]) for i in range(NQ))))
                d = {}
                for key in ("tie", "flip", "both", "invalid", "wrongA", "wrongB", "est_wrongA", "est_wrongB"):
                    pt = table[0][key][0] - table[NQ - 1][key][0]
                    lo, hi = ci_of(table[0][key][3] - table[NQ - 1][key][3])
                    d[key] = (pt, lo, hi)
                say("    Q1 - Q5 (pp): tie %+.1f [%+.1f, %+.1f] | flip %+.1f [%+.1f, %+.1f] | both-tie %+.1f [%+.1f, %+.1f] | INVALID %+.1f [%+.1f, %+.1f]"
                    % tuple(100 * v for k in ("tie", "flip", "both", "invalid") for v in d[k]))
                say("    Q1 - Q5 (pp): wrongA %+.1f [%+.1f, %+.1f] | wrongB %+.1f [%+.1f, %+.1f] | wrong(est) A %+.1f [%+.1f, %+.1f] | wrong(est) B %+.1f [%+.1f, %+.1f]"
                    % tuple(100 * v for k in ("wrongA", "wrongB", "est_wrongA", "est_wrongB") for v in d[k]))
                res[mname] = dict(table=table, diff=d)
            # Spearman
            ml = m_leaf[pos]
            sp = {}
            for key, num, den in (("tie", "tie", "n"), ("flip", "flip", "n"), ("disagreement", "committed", "n"), ("wrongA", "wrongA", "kd")):
                ok = A[den] > 0
                share = A[num][ok] / A[den][ok]
                if key == "disagreement":
                    share = 1 - share
                sp[key] = boot_spearman(ml[ok], share, self.B, rng) + (int(ok.sum()),)
            say("  Spearman(leaf margin, per-question share), n questions: " + " | ".join("%s rho %+.3f [%+.3f, %+.3f] n=%d" % (k, *v) for k, v in sp.items()))
            # logistic within-cell
            y_flip = np.array([r["flip"] for r in rows], float); y_tie = np.array([r["tie"] for r in rows], float)
            rp = np.array([self.qpos[r["q"]] for r in rows])
            xz = z[rp]; xd = diff_z[rp]; okd = ~np.isnan(xd)
            cl = np.array([r["q"] for r in rows])
            cell_leaf = np.array([self.cell[i] for i in rp]); cell_anc = np.array([self.anchor[i] for i in rp]); cell_none = np.array(["all"] * len(rows))
            lg = {}
            for yname, y in (("flip", y_flip), ("tie", y_tie)):
                for fe, cellv in (("none", cell_none), ("anchor", cell_anc), ("leaf", cell_leaf)):
                    r0 = logit_fe(y, xz[:, None], cellv, cl)
                    r1 = logit_fe(y[okd], np.c_[xz[okd], xd[okd]], cellv[okd], cl[okd])
                    lg[(yname, fe)] = (r0, r1)
                    b, s = r0["beta"][0], r0["se"][0]; b1, s1 = r1["beta"][0], r1["se"][0]; bd, sd = r1["beta"][1], r1["se"][1]
                    say("  logit %-4s ~ z(leaf margin) + %-6s FE: beta %+.3f (SE %.3f) [%+.3f, %+.3f] OR/SD %.3f, cells %d, n %d, conv %s | + key difficulty: margin %+.3f [%+.3f, %+.3f], difficulty %+.3f [%+.3f, %+.3f]"
                        % (yname, fe, b, s, b - 1.96 * s, b + 1.96 * s, math.exp(b), r0["keep_cells"], r0["n"], r0["converged"],
                           b1, b1 - 1.96 * s1, b1 + 1.96 * s1, bd, bd - 1.96 * sd, bd + 1.96 * sd))
            # two-candidate flag
            tw = self.two[pos]
            t1 = boot_ratio(A["tie"][tw == 1], A["n"][tw == 1], self.B, rng); t0 = boot_ratio(A["tie"][tw == 0], A["n"][tw == 0], self.B, rng)
            f1 = boot_ratio(A["flip"][tw == 1], A["n"][tw == 1], self.B, rng); f0 = boot_ratio(A["flip"][tw == 0], A["n"][tw == 0], self.B, rng)
            say("  Kotlin two-candidate flag: n_q %d vs %d; tie %.3f vs %.3f, diff %+.1fpp [%+.1f, %+.1f]; flip %.3f vs %.3f, diff %+.1fpp [%+.1f, %+.1f]"
                % (int((tw == 1).sum()), int((tw == 0).sum()), t1[0], t0[0], 100 * (t1[0] - t0[0]), *[100 * v for v in ci_of(t1[3] - t0[3])],
                   f1[0], f0[0], 100 * (f1[0] - f0[0]), *[100 * v for v in ci_of(f1[3] - f0[3])]))
            # order stability per quintile (primary margin), not on x20 alone (no verdicts on the 66 original pairs)
            stab = {}
            if cname != "x20":
                models = sorted({r["a"] for r in rows} | {r["b"] for r in rows})
                srng = np.random.default_rng(SEED + 1)
                for qi in range(NQ):
                    sub = [r for r in rows if self.quint[self.qpos[r["q"]]] == qi]
                    stab[qi] = order_stability(sub, K, models, self.SB, srng)
                say("  order stability per quintile (BT of record on the quintile's matches, %d models; B = %d): " % (len(models), self.SB)
                    + " | ".join("Q%d rho(key) %.3f [%.3f, %.3f] inst %.3f" % (qi + 1, stab[qi]["rho"], stab[qi]["rho_lo"], stab[qi]["rho_hi"], stab[qi]["inst"]) for qi in range(NQ)))
                di = stab[0]["inst_draws"] - stab[NQ - 1]["inst_draws"]
                say("    instability Q1 - Q5 %+.3f [%+.3f, %+.3f] (draw-wise difference; mm_fit vs vectorised max |diff| %.1e)" % (stab[0]["inst"] - stab[NQ - 1]["inst"], *ci_of(di), max(stab[i]["mm_diff"] for i in stab)))
            results[cname] = dict(res=res, sp=sp, lg=lg, stab=stab, A=A, qlist=qlist, two=(t1, t0, f1, f0))
        # cross-judge disagreement on the common match ids
        say("")
        w12 = {r["mid"]: r["w"] for r in self.caches["x12"]}
        for other in ("grok", "kotlin"):
            wo = {r["mid"]: (r["w"], r["q"]) for r in self.caches[other]}
            per = defaultdict(lambda: [0, 0])
            for mid, (w, q) in wo.items():
                if mid in w12 and q in self.qpos:
                    per[q][0] += int(w != w12[mid]); per[q][1] += 1
            ql = sorted(per); pos = np.array([self.qpos[q] for q in ql]); qq = self.quint[pos]
            num = np.array([per[q][0] for q in ql], float); den = np.array([per[q][1] for q in ql], float)
            cells = [boot_ratio(num[qq == i], den[qq == i], self.B, rng) for i in range(NQ)]
            say("  cross-judge disagreement x12 vs %s (winner differs on the same match id; %d matches, %d questions): " % (other, int(den.sum()), len(ql))
                + " | ".join("Q%d %.3f [%.3f, %.3f]" % (i + 1, *cells[i][:3]) for i in range(NQ))
                + " | Q1 - Q5 %+.1fpp [%+.1f, %+.1f]" % (100 * (cells[0][0] - cells[-1][0]), *[100 * v for v in ci_of(cells[0][3] - cells[-1][3])]))
        self.results = results
        self.score(results)
        return self

    def score(self, results):
        say = self.say
        say("")
        say("=== CRITERIA (scored on the merged Mistral board of record; replications on x12, grok, kotlin) ===")
        primary = "leaf_margin[%s]" % TREE_REC
        def c1(cname):
            d = results[cname]["res"][primary]["diff"]
            t, f = d["tie"], d["flip"]
            def cls(x, size):
                pt, lo, hi = x
                if lo > 0 and pt >= size:
                    return "HELD"
                if lo > 0:
                    return "WEAK"
                if hi < 0:
                    return "REVERSED"
                return "FAILED" if (hi - lo) < 2 * size else "UNDETERMINED"
            return cls(t, 0.03), cls(f, 0.02), t, f
        for cname in ("merged", "x12", "grok", "kotlin", "x20"):
            ct_, cf, t, f = c1(cname)
            say("  C1 concentration [%s]: tie Q1-Q5 %+.1fpp [%+.1f, %+.1f] -> %s; flip %+.1fpp [%+.1f, %+.1f] -> %s%s"
                % (cname, 100 * t[0], 100 * t[1], 100 * t[2], ct_, 100 * f[0], 100 * f[1], 100 * f[2], cf, "  (PRIMARY)" if cname == "merged" else ""))
        self.crit["C1"] = c1("merged")[:2]
        for cname in ("merged", "x12", "grok", "kotlin"):
            r0, r1 = results[cname]["lg"][("flip", "leaf")]
            b, s = r0["beta"][0], r0["se"][0]; held = (b < 0) and (b + 1.96 * s < 0)
            b1, s1 = r1["beta"][0], r1["se"][0]; held1 = (b1 < 0) and (b1 + 1.96 * s1 < 0)
            say("  C2 within-cell (leaf FE, flip) [%s]: beta %+.3f [%+.3f, %+.3f] -> %s; C2' with key difficulty: %+.3f [%+.3f, %+.3f] -> %s%s"
                % (cname, b, b - 1.96 * s, b + 1.96 * s, "HELD" if held else "FAILED", b1, b1 - 1.96 * s1, b1 + 1.96 * s1, "HELD" if held1 else "NOT HELD", "  (PRIMARY)" if cname == "merged" else ""))
            if cname == "merged":
                self.crit["C2"] = ("HELD" if held else "FAILED", "HELD" if held1 else "NOT HELD")
        for cname in ("merged", "x12", "grok", "kotlin"):
            d = results[cname]["res"][primary]["diff"]
            a, b_ = d["est_wrongA"], d["est_wrongB"]
            cov = (a[1] <= 0 <= a[2]) and (b_[1] <= 0 <= b_[2])
            wide = max(a[2] - a[1], b_[2] - b_[1]) > 0.10
            verdict = "HELD (no difference)" if cov and not wide else ("UNDETERMINED (interval wider than 10pp)" if cov else "FAILED (differs)")
            say("  C3 wrong(established) [%s]: A %+.1fpp [%+.1f, %+.1f]; B %+.1fpp [%+.1f, %+.1f] -> %s%s"
                % (cname, 100 * a[0], 100 * a[1], 100 * a[2], 100 * b_[0], 100 * b_[1], 100 * b_[2], verdict, "  (PRIMARY)" if cname == "merged" else ""))
            if cname == "merged":
                self.crit["C3"] = verdict
        for cname in ("merged", "x12", "grok", "kotlin"):
            st = results[cname]["stab"]
            di = st[0]["inst_draws"] - st[NQ - 1]["inst_draws"]; lo, hi = ci_of(di); pt = st[0]["inst"] - st[NQ - 1]["inst"]
            verdict = "boundary quintile LESS stable" if lo > 0 else ("boundary quintile MORE stable" if hi < 0 else "NOT SHOWN")
            say("  C4 order stability [%s]: instability Q1 - Q5 %+.3f [%+.3f, %+.3f] -> %s%s" % (cname, pt, lo, hi, verdict, "  (PRIMARY)" if cname == "merged" else ""))
            if cname == "merged":
                self.crit["C4"] = verdict
        sp = results["merged"]["sp"]
        say("  Spearman prediction |rho| < 0.15 [merged]: tie %+.3f, flip %+.3f -> %s" % (sp["tie"][0], sp["flip"][0], "HELD" if max(abs(sp["tie"][0]), abs(sp["flip"][0])) < 0.15 else "FAILED"))
        say("")
        c1t, c1f = self.crit["C1"]
        mech = "OVERTURNED" if (c1t in ("FAILED", "REVERSED") and c1f in ("FAILED", "REVERSED")) or self.crit["C2"][0] == "FAILED" else ("STANDS (as difficulty, not cell assignment)" if self.crit["C2"][1] == "NOT HELD" else "STANDS")
        say("  Falsifier (the MULTI-OWNERSHIP mechanism: boundary questions carry the disagreement): %s" % mech)
        say("  Consequence: %s" % {"OVERTURNED": "no E4 judged arm; the MULTI-OWNERSHIP line closes at zero calls.",
                                    "STANDS (as difficulty, not cell assignment)": "dual-cell judging would target hard questions, not mis-assigned ones; the bill is stated above and no arm is launched without a new registration.",
                                    "STANDS": "a dual-cell arm has a mechanism; its registration (bill above) is a separate decision for the author."}[mech])
        # ---- the blind predictions, scored
        say("")
        say("=== PREDICTIONS (blind, docstring) scored on the merged board unless stated ===")
        d = results["merged"]["res"][primary]["diff"]; t, f = d["tie"], d["flip"]
        inr = lambda x, lo, hi: lo <= 100 * x[0] <= hi

        def held(b):
            return "HELD" if b else "MISSED"
        say("  caller: tie Q1-Q5 in [3, 6]pp: %+.1f -> %s | flip in [2, 4]pp: %+.1f -> %s | |rho| < 0.15 (tie %+.3f, flip %+.3f) -> %s | within-cell survives (C2) -> %s | wrong(established) does not differ (C3) -> %s"
            % (100 * t[0], held(inr(t, 3, 6)), 100 * f[0], held(inr(f, 2, 4)), sp["tie"][0], sp["flip"][0],
               held(max(abs(sp["tie"][0]), abs(sp["flip"][0])) < 0.15), self.crit["C2"][0], self.crit["C3"]))
        a, b_ = d["est_wrongA"], d["est_wrongB"]
        st = results["merged"]["stab"]; di = st[0]["inst_draws"] - st[NQ - 1]["inst_draws"]; ilo, ihi = ci_of(di)
        t1, t0, f1, f0 = results["merged"]["two"]; tlo, thi = ci_of(t1[3] - t0[3])
        same_sign = all(np.sign(results[c]["res"][primary]["diff"]["tie"][0]) == np.sign(results["x12"]["res"][primary]["diff"]["tie"][0]) for c in ("grok", "kotlin"))
        af_weaker = results["merged"]["res"]["leaf_margin[af_s42]"]["diff"]["tie"][0] < t[0]
        say("  arena specialist: tie in [1, 4]pp -> %s | flip in [1, 3]pp -> %s | |rho| < 0.10 -> %s | C2 HELD and C2' NOT HELD -> %s | wrong(est) within +-2pp, intervals cover 0 -> %s | instability Q1-Q5 covers 0 (%+.3f [%+.3f, %+.3f]) -> %s | two-candidate tie diff < 2pp and covers 0 (%+.1fpp [%+.1f, %+.1f]) -> %s | grok and kotlin same tie sign as x12 -> %s | af gradient weaker than bareq512 -> %s"
            % (held(inr(t, 1, 4)), held(inr(f, 1, 3)), held(max(abs(sp["tie"][0]), abs(sp["flip"][0])) < 0.10),
               held(self.crit["C2"] == ("HELD", "NOT HELD")),
               held(abs(a[0]) <= 0.02 and abs(b_[0]) <= 0.02 and a[1] <= 0 <= a[2] and b_[1] <= 0 <= b_[2]),
               st[0]["inst"] - st[NQ - 1]["inst"], ilo, ihi, held(ilo <= 0 <= ihi),
               100 * (t1[0] - t0[0]), 100 * tlo, 100 * thi, held(abs(t1[0] - t0[0]) < 0.02 and tlo <= 0 <= thi),
               held(same_sign), held(af_weaker)))

    def write(self):
        with open(OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(self.L) + "\n")
        with open(OUT_PERQ, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["qid", "cell_leaf", "anchor", "leaf_margin", "d1_margin", "rec_margin", "af_leaf_margin", "af_d1_margin", "two_candidate", "quintile", "in_P0"])
            for k, q in enumerate(self.qs):
                w.writerow([q, self.cell[k], self.anchor[k], "%.6f" % self.M[TREE_REC]["leaf_margin"][k], "%.6f" % self.M[TREE_REC]["d1_margin"][k],
                            "%.6f" % self.M[TREE_REC]["rec_margin"][k], "%.6f" % self.M["af_s42"]["leaf_margin"][k], "%.6f" % self.M["af_s42"]["d1_margin"][k],
                            int(self.two[k]), int(self.quint[k]) + 1, int(self.P0[k])])
        print("wrote %s and %s" % (OUT, OUT_PERQ))


# ----------------------------------------------------------------------------------------------- selftest
def selftest(B=200):
    """The whole analysis path on SYNTHETIC verdicts and margins (no cache is opened, no record number exists)."""
    rng = random.Random(1)
    models = ["m%02d" % i for i in range(8)]
    qs = list(range(1, 601)); K = {q: {m: rng.randrange(2) for m in models} for q in qs}
    anchors = ["A", "B", "C"]; anc_of = {q: anchors[q % 3] for q in qs}
    margin = np.array([rng.random() * 0.2 for _ in qs])
    rows = []
    mid = 0
    for q in qs:
        for _ in range(4):
            a, b = rng.sample(models, 2); mid += 1
            p_tie = 0.35 - margin[q - 1]                       # planted: low margin -> more ties
            u = rng.random()
            if u < p_tie:
                fl = int(rng.random() < 0.6); w = "TIE"
            else:
                fl = 0; w = a if rng.random() < 0.5 else b
            rows.append(dict(mid=mid, a=a, b=b, q=q, anchor=anc_of[q], w=w, flip=fl, invalid=0, nonstop=0, tie=int(w == "TIE"), both=int(w == "TIE" and not fl), committed=int(w in (a, b))))
    est, tested, aq = established_edges(rows, K)
    agg = per_question(rows, K, est)
    qlist = sorted(agg)
    A = {k: np.array([agg[q][k] for q in qlist], float) for k in ("n", "tie", "flip", "kd", "wrongA")}
    nrng = np.random.default_rng(0)
    cuts = np.percentile(margin, [20, 40, 60, 80]); quint = np.searchsorted(cuts, margin, side="right")
    t1 = boot_ratio(A["tie"][quint == 0], A["n"][quint == 0], B, nrng); t5 = boot_ratio(A["tie"][quint == 4], A["n"][quint == 4], B, nrng)
    print("SELFTEST synthetic: tie Q1 %.3f Q5 %.3f (planted gradient should show); edges tested %d established %d" % (t1[0], t5[0], tested, len(est)))
    z = (margin - margin.mean()) / margin.std()
    y = np.array([r["flip"] for r in rows], float); x = np.array([z[r["q"] - 1] for r in rows]); cl = np.array([r["q"] for r in rows]); cell = np.array([r["anchor"] for r in rows])
    lg = logit_fe(y, x[:, None], cell, cl)
    print("SELFTEST logit flip ~ z(margin) + anchor FE: beta %+.3f SE %.3f (planted negative), cells %d, converged %s" % (lg["beta"][0], lg["se"][0], lg["keep_cells"], lg["converged"]))
    st = order_stability(rows, K, models, 50, nrng)
    print("SELFTEST order stability: rho(key) %.3f inst %.3f mm_fit vs vectorised |diff| %.1e" % (st["rho"], st["inst"], st["mm_diff"]))
    sp = boot_spearman(margin, A["tie"] / A["n"], B, nrng)
    print("SELFTEST Spearman(margin, tie share) %+.3f [%+.3f, %+.3f]" % sp)
    selftest_readout(B)
    print("SELFTEST OK (synthetic data only; nothing of record was read or written)")


def selftest_readout(B):
    """Study.readout() end to end on a synthetic Study (five synthetic caches, synthetic margins); nothing written."""
    rng = random.Random(7)
    old = sorted(p8.ARENA12); new = ["new%d" % i for i in range(8)]
    qs = list(range(1000, 1700)); K = {q: {m: rng.randrange(2) for m in old + new} for q in qs}
    leaves = ["L%02d" % i for i in range(12)]; anc_of_leaf = {l: "ANC%d" % (i % 3) for i, l in enumerate(leaves)}
    cell = [leaves[q % 12] for q in qs]; anchor = [anc_of_leaf[c] for c in cell]
    m_leaf = np.array([rng.random() * 0.2 for _ in qs])

    def mk(qsub, pairs_from, per_q, mid0, perturb=0.0):
        rows = []; mid = mid0
        for q in qsub:
            for _ in range(per_q):
                a, b = pairs_from(); mid += 1
                p_tie = 0.35 - m_leaf[q - 1000]
                u = rng.random()
                if u < p_tie:
                    fl = int(rng.random() < 0.6); w = "TIE"
                else:
                    fl = 0; w = a if rng.random() < 0.5 + perturb else b
                inv = int(rng.random() < 0.002)
                if inv:
                    w = "INVALID"; fl = 0
                rows.append(dict(mid=mid, a=a, b=b, q=q, anchor=anc_of_leaf[leaves[q % 12]], w=w, flip=fl, invalid=inv, nonstop=0,
                                 tie=int(w == "TIE"), both=int(w == "TIE" and not fl), committed=int(w in (a, b))))
        return rows
    x12 = mk(qs, lambda: tuple(rng.sample(old, 2)), 3, 0)
    x20 = mk(qs[:600], lambda: (rng.choice(old), rng.choice(new)), 4, 10000)
    grok = [dict(r) for r in x12]; kotlin = [dict(r) for r in x12[:-5]]
    for r in grok + kotlin:
        if not r["invalid"] and rng.random() < 0.1:
            r["w"] = "TIE"; r["flip"] = 1; r["tie"] = 1; r["both"] = 0; r["committed"] = 0
    st = Study(pool_guard.MMLU_PRO_POOL, boot=B, stab_boot=30)
    st.say = lambda s="": None                          # silent: no synthetic line must look like a record line
    st.K = K; st.qs = qs; st.qpos = {q: i for i, q in enumerate(qs)}; st.cell = cell; st.anchor = anchor
    st.two = np.array([rng.randrange(2) for _ in qs]); st.P0 = np.ones(len(qs), bool)
    st.M = {TREE_REC: dict(leaf_margin=m_leaf, d1_margin=m_leaf * 1.1, rec_margin=m_leaf - 0.01),
            "af_s42": dict(leaf_margin=np.array([rng.random() * 0.2 for _ in qs]), d1_margin=m_leaf)}
    st.cuts = np.percentile(m_leaf, [20, 40, 60, 80]); st.quint = np.searchsorted(st.cuts, m_leaf, side="right")
    st.cuts_af = np.percentile(st.M["af_s42"]["leaf_margin"], [20, 40, 60, 80]); st.quint_af = np.searchsorted(st.cuts_af, st.M["af_s42"]["leaf_margin"], side="right")
    st.cuts_d1 = np.percentile(st.M[TREE_REC]["d1_margin"], [20, 40, 60, 80]); st.quint_d1 = np.searchsorted(st.cuts_d1, st.M[TREE_REC]["d1_margin"], side="right")
    st.caches = dict(x12=x12, x20=x20, grok=grok, kotlin=kotlin, merged=x12 + x20)
    st.expected = {k: len(v) for k, v in st.caches.items() if k != "merged"}
    st.readout()
    c = st.crit
    print("SELFTEST readout path ran end to end on synthetic caches: criteria keys %s; planted tie gradient scored %s" % (sorted(c), c["C1"][0]))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--frozen", action="store_true", help="add the frozen 20260727_042523 tree (incident split) as a secondary margin")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--stab-boot", type=int, default=2000)
    ap.add_argument("--pool", default=pool_guard.MMLU_PRO_POOL)
    a = ap.parse_args(argv)
    if a.selftest:
        selftest(); return 0
    if not (a.dry_run or a.run):
        raise SystemExit("[BOUNDARY] nothing to do: --dry-run (structure, no outcomes) or --run (the readout)")
    t0 = time.time()
    st = Study(a.pool, frozen=a.frozen, boot=a.boot, stab_boot=a.stab_boot).prepare()
    if a.run:
        st.readout(); st.write()
    else:
        st.say("")
        st.say("  DRY RUN: no outcome variable was computed; the readout needs --run (zero judge calls either way). %.0f s" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
