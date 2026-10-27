"""CAP-GATE-POSTHOC (registered 2026-09-17 in docs/judge_v2_program.md BEFORE any number existed). ZERO LLM calls,
ZERO constructions, ZERO site nulls: a post-hoc feasibility study of a CAPABILITY split gate on trees that exist.

  python tools/analysis/cap_gate_posthoc.py --dry-run            # pool id, roster, denominators, site lists; NO gain
  python tools/analysis/cap_gate_posthoc.py --selftest           # the gain functions on synthetic data (no record data)
  python tools/analysis/cap_gate_posthoc.py --run                # the readout (refused without --run)
         [--boot 200] [--out experiment_results/anchorfree/cap_gate_posthoc_readout.txt]
         [--sites-csv experiment_results/anchorfree/cap_gate_posthoc_sites.csv]
         [--tree TAG=RUN_DIR[=SITE_NULL_CSV] ...]                 # replaces the default tree list

QUESTION.  The construction's split gate is geometric (the ascending-k first-accept rule on separation J, the
z-gate dJ >= acceptanceZ * SE_dJ, TaxonomySplitter.splitSingleNode) and a site is CERTIFIED afterwards when its
observed separation clears its own 300-rep site null (cert_site_p95).  Would a CAPABILITY gate - accept a split
only when the children carry different model-performance profiles - accept the same sites, a subset, or
different ones?  This is the feasibility study before any construction change ("capability-gated construction")
and it yields the JOINT-GATE count: sites certified by the site null AND accepted by the capability gate.

TREES (default list; every one is an existing artefact, read-only):
  af          experiment_results/anchorfree/af/seed_42          site_null_af_s42.csv          (anchor-free record, 256 d)
  af_abt2     experiment_results/anchorfree/af_abt2/seed_42     site_null_af_abt2_s42.csv     (anchor-free, dropTop 2)
  af_bareq512 experiment_results/anchorfree/af_bareq512/seed_42 site_null_af_bareq512_s42.csv (anchor-free, 512 d, bar 0.0145)
  promoted    experiment_results/promoted/bareq512_s42/seed_42  (NO site null exists on its snapshot
              20260909_212117_Headless_Run_Auto_ge: certified = n/a; the anchored tree of record, 512 d, on the pool of record)
  o0          experiment_results/h9_order/o0/seed_42            h9_order/site_null_o0_s42.csv (anchored same-code control of
              ANCHOR-FREE, 256 d, 5 of 65 certified; the one anchored seed-42 tree WITH a site null)

SITES.  A site = one accepted split = an internal node with >= 2 children in the tree's LAST dag_snapshots.jsonl
snapshot (the same snapshot the site null read; the script asserts that every site-null row is such a node with
the CSV's k and n).  Where no site null exists (promoted) the sites are those nodes, excluding the anchored root
(its 14 children are the category anchors bootstrapped by TaxonomyEngine, not a gate decision).  Bridges and
single-child passthrough nodes are not sites.

MEMBERSHIP.  Every scored question is routed to its nearest LEAF centroid (max cosine of the first-sliceDim
slice of its 4096-d embedding against vmfMu, both unit-normalised: the flatLeaf rule of free_tests_f4_f7.f6 and
anchor_free_readout).  A question belongs to a site iff the site is on its leaf's ancestor chain (kid2parent,
last-listed parent: the ct/F6 convention); its child at that site is the next node down the chain.  The tree's
own member sets are not exported, so the site's n is reported twice: n_site from the site null CSV
(subtreeQueries at the snapshot) and n_scored = routed keyed train-side questions.

SCORED SET (hygiene).  The roster and the keyed questions are free_tests_f4_f7.keyed_questions verbatim: the
eval_results models with >= 95% question coverage, Meta-Llama-3-70B-Instruct excluded (46 models), the question
joined mmlu_pro <-> eval by the OPTIONS key (never by text), 10,925 keyed questions.  Scored = keyed AND on the
tree's own TRAIN side (not in the tree's manifest reserved_pool_id, whose rows are hash-verified with
pool_guard.assert_frozen_pool) AND NOT in the pool of record p2dca21ab5f4ef3ae (pool_guard.assert_pool_of_record;
the af trees were built on seed 42's own split p8a29d8f3ff75aa55, so ~71% of the pool of record sits on their
train side - it is removed anyway: a construction gate may never read the arena pool's keys).  The script
asserts |scored ∩ eval_ids(p2dca)| = 0 for every tree and prints it.  embeddings_cache.db and
mmlu_pro_dataset_cache_v2.db are opened mode=ro.

GAIN (per site, per question q of the site, averaged over models m; Brier, x1000 in every table):
  in-roster  g_in(q)   = mean_m [ (A_m(q) - y) ^ 2 - (B_m(q) - y) ^ 2 ]   with A = the PARENT cell's LOO mean
             (site members minus q) and B = the CHILD cell's LOO mean (child members minus q; = A when the child
             has a single member).  This is free_tests_f4_f7.loo_imp(part = child, qs = site members) with the
             site as the "marginal" - the same function F6 applies to the whole tree, restricted to one split;
             the script computes it with loo_imp AND with the vectorised form and asserts they agree.
  LOMO       g_lomo(q) = mean_m* [ (A_m*(q) - y) ^ 2 - (clip(A_m*(q) + d_{-m*}(q)) - y) ^ 2 ]  where
             d_{-m*}(q) = mean over the other 45 models of (B_m(q) - A_m(q)): the child's offset is FIT on
             k-1 models and SCORED on the held-out model, cycling over all 46; the gate is then not a fact about
             the roster (a split that only re-describes one model's idiosyncrasy earns nothing).  Additive in
             probability, clipped to [0, 1] (author-side choice, stated).  g_in - g_lomo is the roster-specific
             residual (interaction + own-model information).
  the site's gain = the mean of g over its scored questions; the GATE at threshold t accepts iff 1000 * mean
  g_lomo >= t, t in {0, +0.5, +1, +2}; a fifth column reports the CI gate (bootstrap lower bound > 0).
  interval   question-level bootstrap of the site's mean g_lomo, B = 200 (>= 200 registered), numpy Generator
             seed 42, percentile 2.5 / 97.5 on the per-question values (F6's boot_mean_ci convention: plug-in
             on the LOO per-question values, not a refit).
  descriptive prof_sd = sqrt( sum_c (n_c / n) Var_m(Delta_c(m) - mean_m Delta_c) ), Delta_c(m) = child mean -
             parent mean: the profile INTERACTION spread (what a uniform difficulty shift leaves behind);
             models_pos = number of the 46 models whose own in-roster gain at the site is > 0.

READOUT (only with --run; per tree and pooled): per site node, label, depth, k, n_site, n_scored, observed
separation, site p95, certified, g_in, g_lomo [CI], prof_sd, models_pos; per threshold t the accepted count,
|accepted ∩ certified|, certified-only, accepted-only, Jaccard; Spearman and Pearson of g_lomo with observed
separation, with n_scored (and log n), with the margin observed_sep - p95, with depth; the depth profile
(sites, certified, accepted at each t, median g_lomo per depth); the paired median of g_lomo on certified vs
uncertified sites.  Predictions are scored HELD / FAILED by the registrar against the registration text.

Every tree here is STRUCTURAL EVIDENCE: nothing is judged, induced, promoted or handed to the arena.
"""
import os, sys, csv, json, argparse, math
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard                                   # noqa: E402
import consensus_tree as ct                         # noqa: E402  last_snapshot
import free_tests_f4_f7 as F                        # noqa: E402  keyed_questions, loo_imp
import anchor_free_readout as AFR                   # noqa: E402  full_vectors, sliced, site_cert

POOL = pool_guard.MMLU_PRO_POOL                     # p2dca21ab5f4ef3ae: never scored here
THRESH = (0.0, 0.5, 1.0, 2.0)                       # per 1000 Brier on the LOMO gain
BOOT_DEFAULT = 200
BOOT_SEED = 42
DEFAULT_TREES = [
    ("af", "experiment_results/anchorfree/af/seed_42", "experiment_results/anchorfree/site_null_af_s42.csv"),
    ("af_abt2", "experiment_results/anchorfree/af_abt2/seed_42", "experiment_results/anchorfree/site_null_af_abt2_s42.csv"),
    ("af_bareq512", "experiment_results/anchorfree/af_bareq512/seed_42", "experiment_results/anchorfree/site_null_af_bareq512_s42.csv"),
    ("promoted", "experiment_results/promoted/bareq512_s42/seed_42", None),
    ("o0", "experiment_results/h9_order/o0/seed_42", "experiment_results/h9_order/site_null_o0_s42.csv"),
]
OUT_DEFAULT = os.path.join("experiment_results", "anchorfree", "cap_gate_posthoc_readout.txt")
SITES_DEFAULT = os.path.join("experiment_results", "anchorfree", "cap_gate_posthoc_sites.csv")


# ----------------------------------------------------------------------------------------------- trees and sites
def load_tree(run_dir):
    """Last snapshot; nodes by id; kid2parent (last-listed parent); leaf ancestor chains; anchored flag."""
    rd = os.path.join(ROOT, run_dir) if not os.path.isabs(run_dir) else run_dir
    snap = ct.last_snapshot(rd)
    nodes = snap["nodes"]
    byid = {n["id"]: n for n in nodes}
    kid2parent = {}
    for n in nodes:
        for c in n.get("childIds", []):
            kid2parent[c] = n["id"]                  # a later-listed parent overwrites: the ct/F6 convention
    leaves = [n for n in nodes if n["isLeaf"]]
    dims = {n.get("sliceDim", len(n["vmfMu"])) for n in leaves}
    if len(dims) != 1:
        raise SystemExit("[CAP-GATE] %s: leaves carry several sliceDims %s" % (run_dir, sorted(dims)))
    dim = dims.pop()
    chains = {}
    for lf in leaves:
        ch, cur = [lf["id"]], lf["id"]
        while cur in kid2parent:
            cur = kid2parent[cur]
            ch.append(cur)
        chains[lf["id"]] = ch                        # leaf, parent, ..., root
    manifest = {}
    mp = os.path.join(rd, "diagnostics", "run_manifest.json")
    if os.path.exists(mp):
        manifest = json.load(open(mp, encoding="utf-8"))
    cfg = os.path.join(rd, "diagnostics", "config.toml")
    anchor_free = False
    if os.path.exists(cfg):
        for line in open(cfg, encoding="utf-8"):
            s = line.split("#", 1)[0].strip().replace(" ", "")
            if s.startswith("anchorFree="):
                anchor_free = s.split("=", 1)[1].lower() == "true"
    M = np.asarray([n["vmfMu"] for n in leaves], dtype=np.float64)
    nrm = np.linalg.norm(M, axis=1, keepdims=True); nrm[nrm == 0] = 1.0
    return dict(run_dir=run_dir, iteration=snap["iteration"], nodes=nodes, byid=byid, kid2parent=kid2parent,
                leaves=leaves, leaf_ids=[n["id"] for n in leaves], leaf_mu=M / nrm, dim=dim, chains=chains,
                manifest=manifest, anchor_free=anchor_free,
                multi_parent=sum(1 for n in nodes if len(n.get("parentIds", [])) > 1),
                bridges=sum(1 for n in nodes if n.get("isBridge")))


def sites_of(tree, site_null_csv):
    """The accepted split sites: internal nodes with >= 2 children.  With a site null CSV: its rows, asserted to be
    exactly those nodes (k and n agree).  Without: those nodes, minus the anchored root."""
    byid = tree["byid"]
    internal = [n for n in tree["nodes"] if not n["isLeaf"] and not n.get("isBridge") and len(n.get("childIds", [])) >= 2
                and not (n["depth"] == 0 and not tree["anchor_free"])]      # the anchored root: category anchors, not a gate decision
    sites = []
    if site_null_csv:
        p = os.path.join(ROOT, site_null_csv) if not os.path.isabs(site_null_csv) else site_null_csv
        rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
        ids = {r["node_id"] for r in rows}
        missing = [r["node_id"] for r in rows if r["node_id"] not in byid]
        if missing:
            raise SystemExit("[CAP-GATE] %s: %d site-null rows are not nodes of the last snapshot: %s" % (site_null_csv, len(missing), missing[:5]))
        extra = [n["id"] for n in internal if n["id"] not in ids]
        if extra:
            raise SystemExit("[CAP-GATE] %s: %d split sites of the snapshot are not in the site null: %s" % (site_null_csv, len(extra), extra[:5]))
        for r in rows:
            n = byid[r["node_id"]]
            if int(r["k"]) != len(n["childIds"]) or int(r["n"]) != n["subtreeQueries"]:
                raise SystemExit("[CAP-GATE] %s: site %s k/n disagree with the snapshot (%s/%s vs %d/%d)"
                                 % (site_null_csv, r["node_id"], r["k"], r["n"], len(n["childIds"]), n["subtreeQueries"]))
            sites.append(dict(node_id=n["id"], label=n["label"], depth=int(r["depth"]), k=int(r["k"]), n_site=int(r["n"]),
                              sep=float(r["observed_sep"]), p95=float(r["site_null_p95"]), p50=float(r["site_null_p50"]),
                              cert=(r["cert_site_p95"] == "true"), cert_defl=(r["cert_deflated_p95"] == "true"),
                              trunk=(r["trunk_member"] == "true"), snapshot=r["snapshot_id"], reps=r["reps"]))
        src = "%s (%d rows, snapshot %s, %s reps)" % (site_null_csv, len(rows), rows[0]["snapshot_id"], rows[0]["reps"])
    else:
        for n in internal:
            sites.append(dict(node_id=n["id"], label=n["label"], depth=n["depth"], k=len(n["childIds"]), n_site=n["subtreeQueries"],
                              sep=float("nan"), p95=float("nan"), p50=float("nan"), cert=None, cert_defl=None, trunk=None,
                              snapshot="", reps=""))
        src = "no site null on this snapshot: %d internal nodes with >= 2 children%s" % (
            len(sites), "" if tree["anchor_free"] else " (anchored root excluded)")
    sites.sort(key=lambda s: (s["depth"], -s["n_site"], s["node_id"]))
    return sites, src


# ----------------------------------------------------------------------------------------------- scored set
def own_pool_eval_ids(pool_id):
    """The tree's own reserved pool, by rows hash-verified against its id (a run's own split is not a registry entry)."""
    if pool_id == POOL:
        return set(pool_guard.eval_ids(POOL))
    conn = pool_guard.open_ro(pool_guard.db_path(POOL))
    try:
        pool_guard.assert_frozen_pool(conn, pool_id)
        return {q for _, q in conn.execute("SELECT domain, question_id FROM reserved_pool WHERE pool_id = ?", (pool_id,)) if q > 0}
    finally:
        conn.close()


def scored_set(keyed, tree, record_eval):
    models, G, cat, text, qs_all = keyed
    own_pid = tree["manifest"].get("reserved_pool_id")
    if not own_pid:
        raise SystemExit("[CAP-GATE] %s: manifest carries no reserved_pool_id" % tree["run_dir"])
    own = own_pool_eval_ids(own_pid)
    qs = [q for q in qs_all if q not in own and q not in record_eval]
    leak = sum(1 for q in qs if q in record_eval)
    if leak:
        raise SystemExit("[CAP-GATE] %d scored questions are in the pool of record" % leak)
    return dict(own_pool=own_pid, own_n=len(own), n_keyed=len(qs_all), n_in_own=sum(1 for q in qs_all if q in own),
                n_in_record=sum(1 for q in qs_all if q in record_eval),
                n_own_and_record=sum(1 for q in qs_all if q in own and q in record_eval), qs=qs, leak=leak)


def route_members(tree, keyed, qs, vec):
    """nearest-leaf routing of the scored questions; per site the member indices and their child index."""
    text = keyed[3]
    qs = [q for q in qs if text[q] in vec]
    Q = AFR.sliced(vec, [text[q] for q in qs], tree["dim"])
    idx = np.argmax(Q @ tree["leaf_mu"].T, axis=1)
    leaf_of = [tree["leaf_ids"][i] for i in idx]
    return qs, leaf_of


def site_members(tree, site, qs, leaf_of):
    """(member question list, child-index array 0..k-1, child ids) for one site."""
    sid = site["node_id"]
    kids = tree["byid"][sid]["childIds"]
    kidx = {c: i for i, c in enumerate(kids)}
    mem, ch = [], []
    for q, lf in zip(qs, leaf_of):
        chain = tree["chains"][lf]
        if sid in chain:
            j = chain.index(sid)
            if j == 0:
                continue                             # cannot happen: a site is internal
            below = chain[j - 1]
            if below not in kidx:
                raise SystemExit("[CAP-GATE] %s: chain element %s below site %s is not one of its children" % (tree["run_dir"], below, sid))
            mem.append(q); ch.append(kidx[below])
    return mem, np.asarray(ch, dtype=int), kids


# ----------------------------------------------------------------------------------------------- the gain
def site_gains(Y, child_idx, k):
    """Y: (M models x n questions) 0/1 correctness; child_idx: (n,) in 0..k-1.  Returns per-question in-roster and
    LOMO gains (Brier units, positive = the children predict better than the parent), per-model in-roster gains,
    and the profile-interaction spread.  Vectorised form of the docstring's formulas."""
    Y = np.asarray(Y, dtype=np.float64)
    M, n = Y.shape
    if n < 2 or M < 2:
        raise ValueError("site_gains needs >= 2 questions and >= 2 models")
    S = Y.sum(axis=1, keepdims=True)
    A = (S - Y) / (n - 1)                                        # parent LOO mean
    nc = np.bincount(child_idx, minlength=k).astype(np.float64)
    C = np.zeros((M, k))
    for c in range(k):
        C[:, c] = Y[:, child_idx == c].sum(axis=1)
    Cq = C[:, child_idx]
    ncq = nc[child_idx]
    with np.errstate(divide="ignore", invalid="ignore"):
        B = np.where(ncq > 1, (Cq - Y) / np.maximum(ncq - 1, 1), A)   # child LOO mean; single member -> parent
    err_p = (A - Y) ** 2
    g_in_mq = err_p - (B - Y) ** 2
    g_in = g_in_mq.mean(axis=0)
    per_model = g_in_mq.mean(axis=1)
    D = B - A
    delta = (D.sum(axis=0, keepdims=True) - D) / (M - 1)       # offset fit on the other M-1 models
    P = np.clip(A + delta, 0.0, 1.0)
    g_lomo = (err_p - (P - Y) ** 2).mean(axis=0)
    # profile interaction spread (descriptive; non-LOO cell means)
    pm = Y.mean(axis=1)
    cm = C / np.maximum(nc, 1)[None, :]
    Delta = cm - pm[:, None]
    Delta_c = Delta - Delta.mean(axis=0, keepdims=True)
    prof_sd = float(np.sqrt(np.sum((nc / n) * Delta_c.var(axis=0))))
    return g_in, g_lomo, per_model, prof_sd


def boot_ci(v, B, rng):
    v = np.asarray(v, dtype=np.float64)
    n = len(v)
    if n < 2:
        return float("nan"), float("nan")
    means = np.empty(B)
    for b in range(B):
        means[b] = v[rng.integers(0, n, n)].mean()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def selftest():
    """The gain functions on synthetic data: (a) children with a shared difficulty shift -> both gains positive and
    LOMO ~ in-roster; (b) identical children -> both gains <= ~0 (the LOO penalty); (c) a shift in ONE model only ->
    in-roster > 0 for that model, LOMO ~ 0; (d) the vectorised in-roster gain equals free_tests_f4_f7.loo_imp."""
    rng = np.random.default_rng(7)
    M, n = 20, 400
    base = rng.uniform(0.2, 0.8, M)
    child = (np.arange(n) >= n // 2).astype(int)
    # (a) shared shift
    p = np.clip(base[:, None] + np.where(child[None, :] == 1, 0.15, -0.15), 0, 1)
    Y = (rng.uniform(size=(M, n)) < p).astype(float)
    g_in, g_lomo, pm, sd = site_gains(Y, child, 2)
    a = (1000 * g_in.mean(), 1000 * g_lomo.mean(), sd)
    assert a[0] > 5 and a[1] > 5, a
    # (d) equality with loo_imp
    models = ["m%d" % i for i in range(M)]; qs = list(range(n))
    G = {m: {q: int(Y[i, q]) for q in qs} for i, m in enumerate(models)}
    ref = F.loo_imp({q: int(child[q]) for q in qs}, qs, models, G)
    assert np.allclose(ref, g_in, atol=1e-12), "vectorised in-roster gain != loo_imp"
    # (b) identical children
    Y0 = (rng.uniform(size=(M, n)) < base[:, None]).astype(float)
    g_in0, g_lomo0, _, sd0 = site_gains(Y0, child, 2)
    b = (1000 * g_in0.mean(), 1000 * g_lomo0.mean(), sd0)
    assert b[0] < 0.5 and b[1] < 0.5, b
    # (c) one-model shift
    p1 = np.repeat(base[:, None], n, axis=1).copy()
    p1[0] = np.clip(base[0] + np.where(child == 1, 0.3, -0.3), 0, 1)
    Y1 = (rng.uniform(size=(M, n)) < p1).astype(float)
    g_in1, g_lomo1, pm1, _ = site_gains(Y1, child, 2)
    c = (1000 * g_in1.mean(), 1000 * g_lomo1.mean(), 1000 * pm1[0])
    assert pm1[0] > 0.02 and abs(g_lomo1.mean()) < 0.001, c
    lo, hi = boot_ci(g_lomo, 200, np.random.default_rng(BOOT_SEED))
    print("[SELFTEST] shared shift: in %+.2f lomo %+.2f prof_sd %.3f | identical: in %+.2f lomo %+.2f | one-model: in %+.2f lomo %+.2f model0 %+.2f | CI [%+.2f, %+.2f] | loo_imp equality OK"
          % (a + b[:2] + c + (1000 * lo, 1000 * hi)))
    return 0


# ----------------------------------------------------------------------------------------------- statistics
def spearman(x, y):
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    ok = ~(np.isnan(x) | np.isnan(y))
    x, y = x[ok], y[ok]
    if len(x) < 3:
        return float("nan"), len(x)
    try:
        from scipy.stats import spearmanr
        return float(spearmanr(x, y).correlation), len(x)
    except Exception:
        def rank(v):
            o = np.argsort(v); r = np.empty(len(v)); r[o] = np.arange(1, len(v) + 1)
            return r
        return float(np.corrcoef(rank(x), rank(y))[0, 1]), len(x)


def pearson(x, y):
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    ok = ~(np.isnan(x) | np.isnan(y))
    if ok.sum() < 3:
        return float("nan")
    return float(np.corrcoef(x[ok], y[ok])[0, 1])


def median(v):
    v = [x for x in v if not (isinstance(x, float) and math.isnan(x))]
    return float(np.median(v)) if v else float("nan")


# ----------------------------------------------------------------------------------------------- main
def parse_trees(specs):
    out = []
    for s in specs:
        parts = s.split("=")
        if len(parts) not in (2, 3):
            raise SystemExit("[CAP-GATE] --tree TAG=RUN_DIR[=SITE_NULL_CSV], got %r" % s)
        out.append((parts[0], parts[1], parts[2] if len(parts) == 3 else None))
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="pool id, roster, denominators, site lists; computes NO gain")
    ap.add_argument("--run", action="store_true", help="compute and print the readout")
    ap.add_argument("--selftest", action="store_true", help="the gain functions on synthetic data")
    ap.add_argument("--boot", type=int, default=BOOT_DEFAULT)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--sites-csv", default=SITES_DEFAULT)
    ap.add_argument("--tree", action="append", default=[], help="TAG=RUN_DIR[=SITE_NULL_CSV]; repeatable; replaces the default list")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.dry_run or a.run):
        raise SystemExit("[CAP-GATE] refused: pass --dry-run (denominators only) or --run (the readout); see the docstring")
    if a.run and a.boot < 200:
        raise SystemExit("[CAP-GATE] --boot must be >= 200 (registered)")

    pid = pool_guard.assert_pool_of_record(POOL)
    print("reserved_pool_id=%s" % pid)                    # first line: the pool that is NEVER scored here
    record_eval = set(pool_guard.eval_ids(pid))
    trees_spec = parse_trees(a.tree) if a.tree else DEFAULT_TREES
    keyed = F.keyed_questions()
    models, G, cat, text, qs_all = keyed
    print("roster=%d models (keyed eval_results, >= 95%% coverage, Meta-Llama-3-70B-Instruct excluded) | keyed questions=%d (mmlu_pro <-> eval by the OPTIONS key) | pool of record eval ids=%d"
          % (len(models), len(qs_all), len(record_eval)))
    print("mode=%s | thresholds t (per 1000 Brier on the LOMO gain)=%s | bootstrap B=%d seed %d" % ("DRY-RUN (no gain computed)" if not a.run else "RUN", list(THRESH), a.boot, BOOT_SEED))

    L = []
    vec = None
    all_rows = []
    summary = {}
    for tag, run_dir, sn in trees_spec:
        tree = load_tree(run_dir)
        sites, src = sites_of(tree, sn)
        sc = scored_set(keyed, tree, record_eval)
        m = tree["manifest"]
        print("")
        print("[%s] %s | snapshot iteration %d | nodes %d leaves %d dim %d | anchorFree=%s | multi-parent %d bridges %d | manifest seed %s pool %s train %s"
              % (tag, run_dir, tree["iteration"], len(tree["nodes"]), len(tree["leaves"]), tree["dim"], tree["anchor_free"],
                 tree["multi_parent"], tree["bridges"], m.get("seed"), sc["own_pool"], m.get("train_size")))
        print("[%s] sites: %s | certified %s" % (tag, src, "n/a" if sites and sites[0]["cert"] is None else sum(1 for s in sites if s["cert"])))
        print("[%s] scored = keyed %d - in own pool %s (%d) - in pool of record (%d; of which also in own pool %d) = %d | scored_in_pool_of_record=%d"
              % (tag, sc["n_keyed"], sc["own_pool"], sc["n_in_own"], sc["n_in_record"], sc["n_own_and_record"], len(sc["qs"]), sc["leak"]))
        if vec is None:
            vec = AFR.full_vectors(list(text.values()))
        qs, leaf_of = route_members(tree, keyed, sc["qs"], vec)
        print("[%s] routed to a leaf: %d of %d scored (no embedding: %d) | leaves used %d of %d"
              % (tag, len(qs), len(sc["qs"]), len(sc["qs"]) - len(qs), len(set(leaf_of)), len(tree["leaves"])))
        assert not (set(qs) & record_eval), "pool of record leaked into the routed set"

        rows = []
        rng = np.random.default_rng(BOOT_SEED)
        for s in sites:
            mem, ch, kids = site_members(tree, s, qs, leaf_of)
            k = len(kids)
            r = dict(tree=tag, **{kk: s[kk] for kk in ("node_id", "label", "depth", "k", "n_site", "sep", "p95", "p50", "cert", "cert_defl", "trunk")})
            r["n_scored"] = len(mem)
            r["n_children_scored"] = [int((ch == c).sum()) for c in range(k)]
            if a.run:
                if len(mem) < 2 or len(set(ch.tolist())) < 2:
                    r.update(g_in=float("nan"), g_lomo=float("nan"), lo=float("nan"), hi=float("nan"), prof_sd=float("nan"), models_pos=-1, note="under 2 members or a single populated child")
                else:
                    Y = np.array([[G[mm][q] for q in mem] for mm in models], dtype=np.float64)
                    g_in, g_lomo, per_model, prof_sd = site_gains(Y, ch, k)
                    ref = F.loo_imp({q: int(c) for q, c in zip(mem, ch)}, mem, models, G)   # F6's own function on this site
                    if not np.allclose(ref, g_in, atol=1e-12):
                        raise SystemExit("[CAP-GATE] %s %s: vectorised in-roster gain differs from loo_imp" % (tag, s["node_id"]))
                    lo, hi = boot_ci(g_lomo, a.boot, rng)
                    r.update(g_in=1000 * float(g_in.mean()), g_lomo=1000 * float(g_lomo.mean()), lo=1000 * lo, hi=1000 * hi,
                             prof_sd=prof_sd, models_pos=int((per_model > 0).sum()), note="")
            rows.append(r)
        all_rows += rows

        if not a.run:
            print("[%s] site list (node, label, depth, k, n_site, n_scored, children scored, sep, p95, cert):" % tag)
            for r in rows:
                print("    %-10s %-28s d%d k%d n_site %5d n_scored %5d %-18s sep %s p95 %s cert %s"
                      % (r["node_id"], r["label"][:28], r["depth"], r["k"], r["n_site"], r["n_scored"], r["n_children_scored"],
                         "n/a" if math.isnan(r["sep"]) else "%.4f" % r["sep"], "n/a" if math.isnan(r["p95"]) else "%.4f" % r["p95"],
                         "n/a" if r["cert"] is None else r["cert"]))
            continue

        # ---- readout per tree
        ok = [r for r in rows if not math.isnan(r["g_lomo"])]
        has_cert = bool(ok) and ok[0]["cert"] is not None
        L.append("")
        L.append("=== [%s] %s | %d sites (%d scorable) | scored questions %d (train side of %s, pool of record removed) | certified %s ==="
                 % (tag, run_dir, len(rows), len(ok), len(qs), sc["own_pool"], sum(1 for r in ok if r["cert"]) if has_cert else "n/a (no site null)"))
        L.append("  %-10s %-26s d k n_site n_scrd    sep    p95 cert |   g_in  g_lomo [    95%% CI    ] prof_sd mpos | gate t0 t.5 t1 t2 ci"
                 % ("node", "label"))
        for r in sorted(ok, key=lambda r: (r["depth"], -r["n_site"])):
            gates = "".join(" %s" % ("A" if r["g_lomo"] >= t else ".") for t in THRESH) + "  %s" % ("A" if r["lo"] > 0 else ".")
            L.append("  %-10s %-26s %d %d %6d %6d %6s %6s %4s | %+6.2f %+7.2f [%+6.2f, %+6.2f] %7.3f %4d |     %s"
                     % (r["node_id"], r["label"][:26], r["depth"], r["k"], r["n_site"], r["n_scored"],
                        "n/a" if math.isnan(r["sep"]) else "%.4f" % r["sep"], "n/a" if math.isnan(r["p95"]) else "%.4f" % r["p95"],
                        "n/a" if r["cert"] is None else ("CERT" if r["cert"] else "-"),
                        r["g_in"], r["g_lomo"], r["lo"], r["hi"], r["prof_sd"], r["models_pos"], gates))
        for r in rows:
            if math.isnan(r.get("g_lomo", float("nan"))):
                L.append("  %-10s %-26s d%d k%d n_site %d n_scored %d: NOT SCORABLE (%s)" % (r["node_id"], r["label"][:26], r["depth"], r["k"], r["n_site"], r["n_scored"], r.get("note", "")))
        gl = [r["g_lomo"] for r in ok]; gi = [r["g_in"] for r in ok]
        L.append("  gain per 1000: in-roster median %+.2f [p25 %+.2f, p75 %+.2f]; LOMO median %+.2f [p25 %+.2f, p75 %+.2f]; LOMO/in-roster at the median site %.2f; sites with g_lomo > 0: %d of %d"
                 % (median(gi), np.percentile(gi, 25), np.percentile(gi, 75), median(gl), np.percentile(gl, 25), np.percentile(gl, 75),
                    (median(gl) / median(gi)) if median(gi) else float("nan"), sum(1 for x in gl if x > 0), len(gl)))
        cert_set = {r["node_id"] for r in ok if r["cert"]} if has_cert else set()
        tsum = {}
        for t in list(THRESH) + ["ci"]:
            acc = {r["node_id"] for r in ok if (r["lo"] > 0 if t == "ci" else r["g_lomo"] >= t)}
            inter = acc & cert_set
            union = acc | cert_set
            tsum[t] = dict(acc=len(acc), joint=len(inter), cert_only=len(cert_set - acc), acc_only=len(acc - cert_set),
                           jacc=(len(inter) / len(union)) if union else float("nan"))
            L.append("  gate t=%-4s accepted %3d of %d | joint (certified AND accepted) %s | certified-only %s | accepted-only %s | Jaccard %s"
                     % (t, len(acc), len(ok),
                        ("%d of %d certified" % (len(inter), len(cert_set))) if has_cert else "n/a",
                        len(cert_set - acc) if has_cert else "n/a", len(acc - cert_set) if has_cert else "n/a",
                        ("%.3f" % tsum[t]["jacc"]) if has_cert and union else "n/a"))
        # correlations
        sep = [r["sep"] for r in ok]; nsc = [r["n_scored"] for r in ok]; dep = [r["depth"] for r in ok]
        marg = [r["sep"] - r["p95"] for r in ok]
        rs_sep, nn = spearman(gl, sep); rs_n, _ = spearman(gl, nsc); rs_d, _ = spearman(gl, dep); rs_m, _ = spearman(gl, marg)
        L.append("  Spearman(g_lomo, observed sep) %s (n %d) | Spearman(g_lomo, n_scored) %+.3f | Spearman(g_lomo, log n) %+.3f | Spearman(g_lomo, sep - p95) %s | Spearman(g_lomo, depth) %+.3f"
                 % ("n/a" if math.isnan(rs_sep) else "%+.3f" % rs_sep, nn, rs_n, spearman(gl, np.log(nsc))[0], "n/a" if math.isnan(rs_m) else "%+.3f" % rs_m, rs_d))
        L.append("  Pearson (g_lomo, observed sep) %s | Pearson(g_lomo, n_scored) %+.3f | Spearman(g_in, observed sep) %s | Spearman(prof_sd, observed sep) %s"
                 % ("n/a" if math.isnan(pearson(gl, sep)) else "%+.3f" % pearson(gl, sep), pearson(gl, nsc),
                    "n/a" if math.isnan(spearman(gi, sep)[0]) else "%+.3f" % spearman(gi, sep)[0],
                    "n/a" if math.isnan(spearman([r["prof_sd"] for r in ok], sep)[0]) else "%+.3f" % spearman([r["prof_sd"] for r in ok], sep)[0]))
        if has_cert:
            gc = [r["g_lomo"] for r in ok if r["cert"]]; gu = [r["g_lomo"] for r in ok if not r["cert"]]
            L.append("  g_lomo median certified %+.2f (n %d, median n_scored %d) vs uncertified %+.2f (n %d, median n_scored %d); difference %+.2f"
                     % (median(gc), len(gc), median([r["n_scored"] for r in ok if r["cert"]]), median(gu), len(gu),
                        median([r["n_scored"] for r in ok if not r["cert"]]), median(gc) - median(gu)))
        # depth profile
        L.append("  depth profile: depth | sites | certified | accepted t0 / t.5 / t1 / t2 / ci | median g_lomo | median n_scored")
        by_d = defaultdict(list)
        for r in ok:
            by_d[r["depth"]].append(r)
        for d in sorted(by_d):
            rs = by_d[d]
            L.append("    d%d | %3d | %s | %3d / %3d / %3d / %3d / %3d | %+6.2f | %5d"
                     % (d, len(rs), ("%3d" % sum(1 for r in rs if r["cert"])) if has_cert else "n/a",
                        *[sum(1 for r in rs if r["g_lomo"] >= t) for t in THRESH], sum(1 for r in rs if r["lo"] > 0),
                        median([r["g_lomo"] for r in rs]), median([r["n_scored"] for r in rs])))
        summary[tag] = dict(sites=len(ok), cert=(len(cert_set) if has_cert else None), med_in=median(gi), med_lomo=median(gl),
                            tsum=tsum, rs_sep=rs_sep, rs_n=rs_n, rs_d=rs_d)

    if not a.run:
        print("")
        print("[CAP-GATE] dry-run complete: no gain computed, nothing written. The readout needs --run.")
        return 0

    # ---- cross-tree summary
    L.append("")
    L.append("=== summary (LOMO gain per 1000; joint = certified AND accepted) ===")
    L.append("  %-12s sites cert | med g_in med g_lomo | acc t0 (joint) | acc t.5 (joint) | acc t1 (joint) | acc t2 (joint) | acc ci (joint) | rho(sep) rho(n) rho(depth)" % "tree")
    for tag, s in summary.items():
        def cell(t):
            x = s["tsum"][t]
            return "%3d (%s)" % (x["acc"], ("%d/%d" % (x["joint"], s["cert"])) if s["cert"] is not None else "n/a")
        L.append("  %-12s %5d %4s | %+8.2f %+10.2f | %14s | %15s | %14s | %14s | %14s | %s %+.3f %+.3f"
                 % (tag, s["sites"], "n/a" if s["cert"] is None else s["cert"], s["med_in"], s["med_lomo"],
                    cell(0.0), cell(0.5), cell(1.0), cell(2.0), cell("ci"),
                    "n/a" if math.isnan(s["rs_sep"]) else "%+.3f" % s["rs_sep"], s["rs_n"], s["rs_d"]))
    L.append("  Every tree above is structural evidence only; the pool of record was scored nowhere (scored_in_pool_of_record=0 on every tree).")
    L.append("  F2-CLEAN caveat: the split boundaries were CHOSEN on these train-side questions; LOO removes a question from its cell mean, not from the choice of the boundary.")

    head = ["=== CAP-GATE-POSTHOC readout (registered 2026-09-17; zero LLM calls, zero constructions) ===",
            "  reserved_pool_id=%s (never scored) | roster %d models | keyed %d | thresholds %s | B=%d seed %d"
            % (pid, len(models), len(qs_all), list(THRESH), a.boot, BOOT_SEED)]
    txt = "\n".join(head + L)
    print(txt)
    if a.out:
        op = os.path.join(ROOT, a.out) if not os.path.isabs(a.out) else a.out
        os.makedirs(os.path.dirname(op), exist_ok=True)
        with open(op, "w", encoding="utf-8") as f:
            f.write(txt + "\n")
        print("[CAP-GATE] readout written to %s" % op)
    if a.sites_csv:
        sp = os.path.join(ROOT, a.sites_csv) if not os.path.isabs(a.sites_csv) else a.sites_csv
        cols = ["tree", "node_id", "label", "depth", "k", "n_site", "n_scored", "n_children_scored", "sep", "p95", "p50", "cert", "cert_defl", "trunk",
                "g_in", "g_lomo", "lo", "hi", "prof_sd", "models_pos", "note"]
        with open(sp, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in all_rows:
                w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})
        print("[CAP-GATE] per-site table written to %s" % sp)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
