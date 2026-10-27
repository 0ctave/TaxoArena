"""ANCHOR-FREE-REDRAW readout (docs/judge_v2_program.md, "Registered 2026-09-17 (before running) - ANCHOR-FREE-REDRAW",
programme L4627-4781, commit d61f2cf; plan docs/agents/plans/2026-09-17_anchor_free_redraw.md, step 3). ZERO LLM calls.

Registration (verbatim in the programme; restated here as the script reads it).
  Question: does the anchor-free tree of record (af/seed_42: 81 leaves, 16 of 69 certified, ONE draw on the
  p8a29d8f3ff75aa55 split, 70.4% of the pool of record on its train side) reproduce its trunk axis, its trunk
  certification, its certified count and its certified sites under a re-draw of the sample (R1 clean split,
  R2 seed 137, R3 seed 2048) and of the construction order (R4)?  Anchored clean-split control R1c.
  Arms (one key each over experiment_configs/anchorfree/af_s42.toml; configs experiment_configs/anchorfree/redraw/):
    R1  af_clean_s42  + reservedPoolFile = experiment_configs/reserved_pool_frozen_p2dca.json (clean split)
    R1c o0_clean_s42  h9_order/o0_s42.toml + the same reservedPoolFile (the ANCHORED control on the clean split)
    R2  af_s137       seed = 137 (own split; a SAMPLE re-draw and nothing else: construction is seed-inert)
    R3  af_s2048      seed = 2048 (idem)
    R4  af_s42_o1     + constructionOrderShuffleSeed = 1 (order re-draw at the record's sample)
  Instrument (this script; zero calls):
    (a) EXISTENCE MARGIN at the root and every depth-1 site: the refused-k min-pair separations against the bar
        (diagnostics/proposals.csv NO_PROPOSAL rows, reason min_pair_sep_below_bar(sep=..,bar=..,k=..,emK=..)) and the
        accepted k with its joint sepScore (dasguptaDeltaNorm in the snapshot graph = observed_sep in the site-null
        CSV).  The engine records the accepted split's own min-pair separation ONLY when it fails (TaxonomySplitter.kt
        L403-409); no engine change is made.  Which number is printed is stated on every line: at an accepted k = 2 the
        min-pair IS the joint score (one pair, same ClusterStats; splitter comment L392-398), so the margin is exact;
        at an accepted k > 2 the min-pair is bounded below by the bar and above by the joint score, so the margin is an
        interval [1.00, joint/bar] and is reported as such.
    (b) TRUNK AXIS: root k; the majority depth-1 cell (flatLeaf rule, leaf-routed then the leaf's depth-1 ancestor,
        anchor_free_readout.purity / migration on the pool of record) of each of the 14 categories; scored on the 12
        the record assigns unambiguously (quantitative: math, physics, chemistry, engineering; discursive: law, other,
        economics, psychology, health, biology, philosophy, history); business and computer science reported, not scored.
        The arm's QUANTITATIVE cell = the depth-1 cell holding the most pool questions of the four quantitative
        categories; DISCURSIVE cell likewise over the eight; a scored category is "on the record's side" when its
        majority cell is its side's cell and the two side cells differ (if they coincide the axis is absent: 0 of 12).
    (c) TRUNK CERTIFICATION: cert_site_p95 of the root and of every depth-1 site, margin = observed_sep / site_null_p95.
    (d) CERTIFIED-SITE IDENTITY: a site's member set = the union of its descendant leaves' queryIds from the snapshot
        graph in snapshots.db (table `snapshots`, column `graph` = SerializedGraph JSON, nodes[].childIds /
        nodes[].queryIds; opened mode=ro&immutable=1; q_ ids are "q_" + SHA-256(text)[:16], TaxonomyPersistence.kt
        L74-77, identical across arms for the same text; DAG_MAX multi-assignment kept as the engine wrote it),
        restricted to the SHARED TRAIN texts of the two trees (= the intersection of their member id sets); a record
        certified site S reproduces in an arm when some certified site T of the arm has Jaccard(S, T) >= 0.5 on that
        set, one-to-one, greedy by Jaccard (largest first); per-site table with the record margin; count of 16; the
        RE-DRAW-STABLE CERTIFIED SET = record sites reproducing in R1, R2 and R3.
    (e) mu-match of the record's 81 leaves to the arm at cos >= 0.95 (anchor_free_readout.mu_match, h9_stability.cos).
  Readout-pool rule: purity and key information are read on the pool of record for every tree; that pool is ~70%
  in-sample for the record, R2, R3 and R4 (the overlap this script FINDS is printed per arm as pool texts among the
  tree's members) and clean for R1 / R1c.  Like-for-like purity pairs: R1 vs R1c, and R2 / R3 / R4 vs the record.
  R1 vs the record confounds re-draw with contamination removal and is read only as the registered prediction.
  Criteria: C1 leaves in [60, 100] per arm, sweep >= 4 of 5;  C2 root k = 2 and >= 11 of 12 scored categories on the
  record's side in every anchor-free arm that builds;  C3 all depth-1 sites certified in every anchor-free arm that
  builds, root certified in >= 3 of the 4 anchor-free arms;  C4 certified sites in [11, 21] and share in [16%, 30%] in
  every anchor-free arm that builds;  C5 >= 6 of the record's 16 certified sites reproduce in each of R1, R2, R3 and
  >= 14 of 16 in R4;  C6 R1 certifies >= R1c + 8 sites.  (C2, C3-depth-1 and C4 are read on the anchor-free arms: an
  anchored tree has root k = 14 by construction; the registration's "every arm that builds" cannot mean the control.)
  Predictions: every numeric prediction of the registration is scored HELD / FAILED below with its number beside it;
  the one prediction the engine cannot decide (a depth-1 margin at an accepted k > 2) is printed as an interval and
  marked NOT DECIDABLE, never HELD.  Falsifiers F1-F4 are named where the criterion they hang on is scored.
  UNDETERMINED is the registered outcome for an arm whose site null did not complete at 300 reps; the operator
  declares it with --undetermined ARM (never a partial null, never a retry); a build that crashed before writing
  its manifest is declared with --failed ARM and is a C1 FAIL.  All five arms run regardless of intermediate results.

Launch sequence (the run-operator; every step zero calls):
  python tools/analysis/anchor_free_redraw.py --selftest      # record vs record: 16/16 at Jaccard 1.0, 81/81, 12/12
  python tools/analysis/anchor_free_redraw.py --dry-run       # pool id first; lists inputs per arm; writes nothing
  python tools/analysis/anchor_free_redraw.py --arm af_clean_s42   # per-arm file (the chain calls this after each site null)
  python tools/analysis/anchor_free_redraw.py --run           # all five arms complete -> anchor_free_redraw_outcome.txt
      --failed <arm>        a build that crashed before writing diagnostics/run_manifest.json (C1 FAIL; never retried)
      --undetermined <arm>  a site null that did not complete at 300 reps (UNDETERMINED; no partial null is read)
      without these, --run / --arm REFUSE on a missing manifest / CSV / readout; a completed build with leaves outside
      [60, 100] is a C1 FAIL and "not built" for C2-C5 automatically (no flag needed)
Inputs per arm:  experiment_results/anchorfree/redraw/<arm>/seed_<seed>/ (dag_snapshots.jsonl, diagnostics/run_manifest.json,
  diagnostics/proposals.csv, headless_run.log with "Snapshot ID:"), experiment_results/anchorfree/redraw/site_null_<arm>.csv
  (reps == 300, snapshot_id == the build's), the arm's anchor_free_<arm>_readout.txt (anchor_free_readout.py <arm> af/seed_42),
  snapshots.db (read-only), embeddings_cache.db and mmlu_pro_dataset_cache_v2.db (read-only, via anchor_free_readout).
Outputs:  experiment_results/anchorfree/redraw/anchor_free_redraw_<arm>.txt (--arm) and
  experiment_results/anchorfree/redraw/anchor_free_redraw_outcome.txt (--run only, only from complete inputs).
"""
import os, sys, re, csv, json, glob, hashlib, sqlite3, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard                                   # noqa: E402
import anchor_free_readout as afr                   # noqa: E402  corpus, full_vectors, load_tree, purity, migration, mu_match, site_cert

POOL = pool_guard.MMLU_PRO_POOL                     # p2dca21ab5f4ef3ae
REDRAW = os.path.join(ROOT, "experiment_results", "anchorfree", "redraw")
RECORD_DIR = os.path.join(ROOT, "experiment_results", "anchorfree", "af", "seed_42")
RECORD_CSV = os.path.join(ROOT, "experiment_results", "anchorfree", "site_null_af_s42.csv")
RECORD_READOUT = os.path.join(ROOT, "experiment_results", "anchorfree", "anchor_free_readout.txt")
SNAP_DB = os.path.join(ROOT, "snapshots.db")
OUTCOME = os.path.join(REDRAW, "anchor_free_redraw_outcome.txt")

BAR = 0.025                 # proposalSeparationBar of every arm (af_s42.toml); cross-checked against proposals.csv
REPS = 300                  # site-null reps of record; anything else is refused
JACCARD = 0.5               # EPOCH-NULL's loosest bar (registration, author-side decision)
MU_COS = afr.MU_MATCH_COS   # 0.95 (h9_stability)
NEAR_BAR = 0.002            # "a depth-1 separation within 0.002 of the bar"
RECORD_CERT = 16            # the record's certified count (site_null_af_s42.csv); asserted in --selftest

QUANT = ("math", "physics", "chemistry", "engineering")
DISC = ("law", "other", "economics", "psychology", "health", "biology", "philosophy", "history")
REPORTED = ("business", "computer science")
SCORED = QUANT + DISC

# arm, tag, seed, kind (anchor-free / anchored)
ARMS = [
    dict(arm="af_clean_s42", tag="R1", seed=42, kind="anchor-free", key="reservedPoolFile = reserved_pool_frozen_p2dca.json"),
    dict(arm="o0_clean_s42", tag="R1c", seed=42, kind="anchored", key="o0_s42.toml + reservedPoolFile (anchored control)"),
    dict(arm="af_s137", tag="R2", seed=137, kind="anchor-free", key="seed = 137"),
    dict(arm="af_s2048", tag="R3", seed=2048, kind="anchor-free", key="seed = 2048"),
    dict(arm="af_s42_o1", tag="R4", seed=42, kind="anchor-free", key="constructionOrderShuffleSeed = 1"),
]
AF_ARMS = [a["arm"] for a in ARMS if a["kind"] == "anchor-free"]
SAMPLE_ARMS = ["af_clean_s42", "af_s137", "af_s2048"]
ORDER_ARM = "af_s42_o1"
CONTROL_ARM = "o0_clean_s42"

# K-SELECTION (2026-09-19, backwards-compatible): a primed arm's refusal row carries `,bar_eff=<accept level>` between
# bar and k (TaxonomySplitter.kt barEffReason); the optional group 3 is None on every unprimed row (REDRAW's rows parse
# exactly as before; k and emK are groups 4 and 5).
REASON_RE = re.compile(r"min_pair_sep_below_bar\(sep=([0-9.]+),bar=([0-9.]+)(?:,bar_eff=([0-9.]+))?,k=(\d+),emK=(\d+)\)")


def qid(text):
    """TaxonomyPersistence.hashQuery: 'q_' + hex(SHA-256(UTF-8 text))[:16]."""
    return "q_" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


# ----------------------------------------------------------------------------------------------- inputs per arm
def arm_paths(a):
    """Where the chain leaves an arm's inputs; nothing here is created."""
    base = os.path.join(REDRAW, a["arm"])
    run_dir = os.path.join(base, "seed_%d" % a["seed"])
    seed_dirs = sorted(glob.glob(os.path.join(base, "seed_*")))
    return dict(
        base=base, run_dir=run_dir, seed_dirs=seed_dirs,
        manifest=os.path.join(run_dir, "diagnostics", "run_manifest.json"),
        proposals=os.path.join(run_dir, "diagnostics", "proposals.csv"),
        log=os.path.join(run_dir, "headless_run.log"),
        jsonl=os.path.join(run_dir, "dag_snapshots.jsonl"),
        csv=os.path.join(REDRAW, "site_null_%s.csv" % a["arm"]),
        readout_candidates=[os.path.join(REDRAW, "anchor_free_%s_readout.txt" % a["arm"]),
                            os.path.join(base, "anchor_free_%s_readout.txt" % a["arm"]),
                            os.path.join(ROOT, "experiment_results", "anchorfree", "anchor_free_%s_readout.txt" % a["arm"])],
        per_arm_out=os.path.join(REDRAW, "anchor_free_redraw_%s.txt" % a["arm"]))


def find_readout(paths, explicit=None):
    if explicit:
        return explicit if os.path.exists(explicit) else None
    for c in paths["readout_candidates"]:
        if os.path.exists(c):
            return c
    return None


def snapshot_id_from_log(log_path):
    sid = None
    with open(log_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.search(r"Snapshot ID: (\S+)", line)
            if m:
                sid = m.group(1)
    return sid


def build_state(a, paths, failed_declared):
    """'built' | 'did-not-build' (manifest exit_reason != completed, or declared --failed) | 'not-run' | 'unfinished'."""
    if a["arm"] in failed_declared:
        return "did-not-build", "declared --failed by the operator (never a retry)"
    if not os.path.isdir(paths["base"]):
        return "not-run", "run dir absent"
    if not os.path.exists(paths["manifest"]):
        extra = "" if not paths["seed_dirs"] or paths["run_dir"] in paths["seed_dirs"] else \
            " (seed dirs present: %s)" % ", ".join(os.path.basename(d) for d in paths["seed_dirs"])
        return "unfinished", "no diagnostics/run_manifest.json yet%s" % extra
    m = json.load(open(paths["manifest"], encoding="utf-8"))
    if m.get("exit_reason") != "completed":
        return "did-not-build", "manifest exit_reason=%r" % m.get("exit_reason")
    if not os.path.exists(paths["jsonl"]) or not os.path.exists(paths["log"]):
        return "did-not-build", "manifest completed but dag_snapshots.jsonl / headless_run.log missing"
    if snapshot_id_from_log(paths["log"]) is None:
        return "did-not-build", "no 'Snapshot ID:' line in headless_run.log (no snapshot saved)"
    return "built", "manifest completed, snapshot %s" % snapshot_id_from_log(paths["log"])


def read_site_null(path):
    """Rows keyed by node_id with the numeric columns parsed; refuses reps != 300 and mixed snapshot ids."""
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    if not rows:
        raise SystemExit("[REDRAW] %s has no rows" % rel(path))
    reps = {r["reps"] for r in rows}
    if reps != {str(REPS)}:
        raise SystemExit("[REDRAW] %s: reps %s, the registration reads only %d-rep nulls (UNDETERMINED otherwise)"
                         % (rel(path), sorted(reps), REPS))
    sids = {r["snapshot_id"] for r in rows}
    if len(sids) != 1:
        raise SystemExit("[REDRAW] %s carries several snapshot ids %s" % (rel(path), sorted(sids)))
    out = {}
    for r in rows:
        out[r["node_id"]] = dict(
            node_id=r["node_id"], label=r["label"], depth=int(r["depth"]), n=int(r["n"]), k=int(r["k"]),
            observed=float(r["observed_sep"]), p50=float(r["site_null_p50"]), p95=float(r["site_null_p95"]),
            cert=r["cert_site_p95"].strip().lower() == "true", defl=r["cert_deflated_p95"].strip().lower() == "true",
            trunk=r["trunk_member"].strip().lower() == "true", feasibility=r["feasibility"])
    return dict(path=path, snapshot=sids.pop(), rows=out, sites=len(out),
                cert=[k for k, v in out.items() if v["cert"]], reps=REPS)


def load_graph(snapshot_id):
    """The SerializedGraph the engine saved: id -> node (childIds, queryIds, depth, dasguptaDeltaNorm, ...)."""
    if not os.path.exists(SNAP_DB):
        raise SystemExit("[REDRAW] %s not found" % rel(SNAP_DB))
    con = sqlite3.connect("file:%s?mode=ro&immutable=1" % SNAP_DB.replace("\\", "/"), uri=True)
    try:
        row = con.execute("SELECT graph FROM snapshots WHERE id = ?", (snapshot_id,)).fetchone()
    finally:
        con.close()
    if row is None:
        wal = os.path.join(ROOT, "snapshots.db-wal")
        hint = ""
        if os.path.exists(wal) and os.path.getsize(wal) > 0:
            hint = " (snapshots.db-wal is %d bytes: a writer has not checkpointed; wait for the JVM to close, never re-run)" % os.path.getsize(wal)
        raise SystemExit("[REDRAW] snapshot %s not in %s%s" % (snapshot_id, rel(SNAP_DB), hint))
    g = json.loads(row[0])
    byid = {n["id"]: n for n in g["nodes"]}
    return dict(root=g["rootId"], byid=byid, version=g.get("version"))


def members(graph):
    """node id -> set of descendant-leaf queryIds (a leaf = no childIds); memoised DFS over childIds."""
    byid = graph["byid"]
    memo = {}

    def rec(i, stack):
        if i in memo:
            return memo[i]
        if i in stack:
            raise SystemExit("[REDRAW] cycle at %s in the snapshot graph" % i)
        kids = byid[i].get("childIds") or []
        if not kids:
            s = frozenset(byid[i].get("queryIds") or [])
        else:
            s = frozenset().union(*(rec(c, stack | {i}) for c in kids))
        memo[i] = s
        return s
    for i in byid:
        rec(i, frozenset())
    return memo


def refused_rows(proposals_path, site_ids):
    """proposals.csv NO_PROPOSAL rows at the given sites: min-pair refusals parsed, other reasons counted."""
    out = {s: dict(minpair=[], other=Counter()) for s in site_ids}
    bars = set()
    with open(proposals_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["site_id"] not in out or r["decision"] != "NO_PROPOSAL":
                continue
            m = REASON_RE.search(r["reason"] or "")
            if m:
                sep, bar, k, emk = float(m.group(1)), float(m.group(2)), int(m.group(4)), int(m.group(5))
                bar_eff = float(m.group(3)) if m.group(3) is not None else None      # K-SELECTION primed arms only
                bars.add(bar)
                out[r["site_id"]]["minpair"].append(dict(iter=int(r["iter"]), sep=sep, bar=bar, bar_eff=bar_eff, k=k, emK=emk, n=int(r["n_site"] or 0)))
            else:
                out[r["site_id"]]["other"][(r["reason"] or "").split("(")[0]] += 1
    return out, bars


# ----------------------------------------------------------------------------------------------- one tree's block
def analyse_tree(name, run_dir, csv_path, corpus_ctx, record=None, readout_path=None):
    """Everything (a)-(e) for one tree.  `record` = the record's own block (None while analysing the record)."""
    train, heldout, vec = corpus_ctx
    tree = afr.load_tree(run_dir)
    sn = read_site_null(csv_path)
    log_sid = snapshot_id_from_log(os.path.join(run_dir, "headless_run.log"))
    if log_sid != sn["snapshot"]:
        raise SystemExit("[REDRAW] %s: site null is on snapshot %s, the build log says %s" % (name, sn["snapshot"], log_sid))
    graph = load_graph(sn["snapshot"])
    if set(graph["byid"]) != set(tree["byid"]):
        raise SystemExit("[REDRAW] %s: snapshots.db graph and dag_snapshots.jsonl last snapshot differ in node ids" % name)
    mem = members(graph)
    root = graph["root"]
    d1 = [c for c in graph["byid"][root].get("childIds") or []]
    if sorted(d1) != sorted(tree["d1_ids"]):
        raise SystemExit("[REDRAW] %s: depth-1 ids differ between snapshots.db and dag_snapshots.jsonl" % name)
    all_members = mem[root]
    if sn["rows"].get(root) and sn["rows"][root]["n"] != len(all_members):
        raise SystemExit("[REDRAW] %s: root n in the site null (%d) != union of leaf queryIds (%d)" % (name, sn["rows"][root]["n"], len(all_members)))

    # (a) existence margin
    refused, bars = refused_rows(os.path.join(run_dir, "diagnostics", "proposals.csv"), [root] + d1)
    if bars and bars != {BAR}:
        raise SystemExit("[REDRAW] %s: proposals.csv bar(s) %s != %.3f" % (name, sorted(bars), BAR))
    exist = {}
    for s in [root] + d1:
        node = graph["byid"][s]
        k = len(node.get("childIds") or [])
        joint = node.get("dasguptaDeltaNorm")
        csvrow = sn["rows"].get(s)
        if csvrow is not None and joint is not None and abs(csvrow["observed"] - joint) > 5e-6:
            raise SystemExit("[REDRAW] %s: %s dasguptaDeltaNorm %.6f != site-null observed_sep %.6f" % (name, s, joint, csvrow["observed"]))
        seen, uniq = set(), []
        for r in sorted(refused[s]["minpair"], key=lambda r: (r["k"], r["emK"], r["sep"], r["iter"])):
            key = (r["k"], r["emK"], r["sep"])
            if key not in seen:
                seen.add(key)
                uniq.append(dict(r, iters=[x["iter"] for x in refused[s]["minpair"] if (x["k"], x["emK"], x["sep"]) == key]))
        if k == 0:
            margin = None; exact = None
        elif k == 2:
            margin = (joint / BAR, joint / BAR); exact = True       # min-pair == joint at one pair
        else:
            margin = (1.0, joint / BAR); exact = False             # bar <= min-pair <= joint
        recorded_seps = [r["sep"] for r in uniq] + ([joint] if k == 2 else [])
        exist[s] = dict(id=s, label=node["label"], depth=node["depth"], k=k, joint=joint, refused=uniq,
                        other=dict(refused[s]["other"]), margin=margin, exact=exact, n=len(mem[s]),
                        near_bar=any(abs(x - BAR) <= NEAR_BAR for x in recorded_seps), recorded_seps=recorded_seps)

    # (b) trunk axis
    pur = afr.purity(tree, train, heldout, vec)
    mig = afr.migration(tree, pur, heldout)          # category -> Counter(depth-1 id)
    root_k = len(d1)
    if root_k:
        qcell = max(d1, key=lambda c: sum(mig[cat].get(c, 0) for cat in QUANT))
        dcell = max(d1, key=lambda c: sum(mig[cat].get(c, 0) for cat in DISC))
    else:
        qcell = dcell = None
    cat_rows = []
    on_side = 0
    for cat in SCORED + REPORTED:
        cnt = mig.get(cat, Counter())
        maj = max(d1, key=lambda c: cnt.get(c, 0)) if d1 else None
        side = "quantitative" if cat in QUANT else "discursive" if cat in DISC else "reported"
        ok = None
        if cat in SCORED:
            ok = (qcell != dcell) and (maj == (qcell if cat in QUANT else dcell))
            on_side += int(ok)
        cat_rows.append(dict(cat=cat, n=sum(cnt.values()), maj=maj, maj_n=cnt.get(maj, 0) if maj else 0, side=side, ok=ok,
                             counts={c: cnt.get(c, 0) for c in d1}))
    axis = dict(root_k=root_k, qcell=qcell, dcell=dcell, on_side=on_side, rows=cat_rows, axis_present=(qcell != dcell))

    # (c) trunk certification
    trunk = []
    for s in [root] + d1:
        r = sn["rows"].get(s)
        if r is None:
            trunk.append(dict(id=s, depth=graph["byid"][s]["depth"], label=graph["byid"][s]["label"], cert=None, observed=None, p95=None, margin=None, in_csv=False))
        else:
            trunk.append(dict(id=s, depth=r["depth"], label=r["label"], cert=r["cert"], observed=r["observed"], p95=r["p95"],
                              margin=r["observed"] / r["p95"] if r["p95"] > 0 else float("inf"), in_csv=True, feasibility=r["feasibility"]))
    root_cert = trunk[0]["cert"] is True
    d1_rows = trunk[1:]
    d1_all_cert = bool(d1_rows) and all(t["cert"] is True for t in d1_rows)

    # pool-of-record overlap (the readout-pool rule)
    pool_ids = {qid(t) for t, _ in heldout}
    overlap = len(pool_ids & all_members)

    # readout cross-check + key information
    readout = parse_readout(readout_path, tree["name"]) if readout_path else None
    if readout is not None and abs(readout["purity"] - pur["leaf"]["acc"]) > 0.0006:
        raise SystemExit("[REDRAW] %s: readout purity %.3f != recomputed %.4f (same instrument; inputs differ?)"
                         % (name, readout["purity"], pur["leaf"]["acc"]))

    blk = dict(name=name, run_name=tree["name"], run_dir=run_dir, tree=tree, snapshot=sn["snapshot"], sitenull=sn,
               graph=graph, members=mem, all_members=all_members, leaves=len(tree["leaves"]), nodes=tree["nodes"],
               depth=tree["depth"], iteration=tree["iteration"], manifest=tree["manifest"],
               sites=sn["sites"], cert=len(sn["cert"]), cert_ids=list(sn["cert"]),
               share=len(sn["cert"]) / sn["sites"] if sn["sites"] else float("nan"),
               exist=exist, root=root, d1=d1, axis=axis, trunk=trunk, root_cert=root_cert, d1_all_cert=d1_all_cert,
               purity=pur["leaf"], overlap=overlap, pool_n=len(heldout), readout=readout, readout_path=readout_path)
    if record is not None:
        blk["identity"] = site_identity(record, blk)
        mm, mm_n, mm_cos = afr.mu_match(record["tree"], tree)
        blk["mu"] = dict(matched=mm, n=mm_n, median=float(np.median(mm_cos)))
    return blk


def parse_readout(path, run_name):
    """The arm's anchor_free_<arm>_readout.txt: its first column must be this tree; purity and F6 leaf x1000."""
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"^\s*anchor-free\s+(\S+)\s+\|", txt, re.M)
    if not m or m.group(1) != run_name:
        raise SystemExit("[REDRAW] %s: readout's anchor-free column is %r, not %r" % (rel(path), m.group(1) if m else None, run_name))
    m2 = re.search(r"^\s*control\s+(\S+)\s+\|", txt, re.M)
    pm = re.search(r"held-out purity, leaf majority-train label\s+([0-9.]+) \[([0-9.]+), ([0-9.]+)\]\s+([0-9.]+) \[", txt)
    fm = re.search(r"leaf cells over marginal\s+([+-][0-9.]+)\s+([+-][0-9.]+)", txt)
    if not pm or not fm:
        raise SystemExit("[REDRAW] %s: purity / F6 lines not found" % rel(path))
    return dict(path=path, control=m2.group(1) if m2 else None, purity=float(pm.group(1)), purity_ci=(float(pm.group(2)), float(pm.group(3))),
                control_purity=float(pm.group(4)), f6_leaf=float(fm.group(1)), control_f6_leaf=float(fm.group(2)))


def site_identity(record, arm):
    """(d): Jaccard >= 0.5 on the shared train texts, one-to-one greedy by Jaccard, record certified sites vs the arm's."""
    shared = record["all_members"] & arm["all_members"]
    rs, ts = record["cert_ids"], arm["cert_ids"]
    J = {}
    for s in rs:
        S = record["members"][s] & shared
        for t in ts:
            T = arm["members"][t] & shared
            u = len(S | T)
            J[(s, t)] = (len(S & T) / u) if u else 0.0
    pairs = sorted(J.items(), key=lambda kv: (-kv[1], kv[0]))
    used_s, used_t, match = set(), set(), {}
    for (s, t), j in pairs:
        if j < JACCARD:
            break
        if s in used_s or t in used_t:
            continue
        match[s] = (t, j)
        used_s.add(s); used_t.add(t)
    best = {s: max(((J[(s, t)], t) for t in ts), default=(0.0, None)) for s in rs}
    return dict(shared=len(shared), record_members=len(record["all_members"]), arm_members=len(arm["all_members"]),
                match=match, best=best, reproduced=len(match), of=len(rs))


# ----------------------------------------------------------------------------------------------- formatting
def fmt_block(blk, record, tag=None, kind=None):
    L = []
    hdr = "%s %s" % (tag, blk["name"]) if tag else blk["name"]
    m = blk["manifest"]
    L.append("--- %s (%s) | %s | snapshot %s | manifest: seed %s, split pool %s, train %s / test %s, gate %s, anchor_free %s, order seed %s, commit %s"
             % (hdr, kind or "record", blk["run_name"], blk["snapshot"], m.get("seed"), m.get("reserved_pool_id"), m.get("train_size"),
                m.get("test_size"), m.get("gate_size"), m.get("anchor_free"), m.get("construction_order_shuffle_seed"), str(m.get("commit", "?"))[:8]))
    L.append("    site null: %s (%d sites, %d reps) | readout: %s" % (rel(blk["sitenull"]["path"]), blk["sites"], REPS,
                                                                        rel(blk["readout_path"]) if blk["readout_path"] else "none"))
    L.append("    leaves %d / nodes %d / max depth %d / iterations %d | certified %d of %d sites (%.1f%%) | members %d; pool of record among members %d of %d (%.1f%%)%s"
             % (blk["leaves"], blk["nodes"], blk["depth"], blk["iteration"], blk["cert"], blk["sites"], 100 * blk["share"],
                len(blk["all_members"]), blk["overlap"], blk["pool_n"], 100 * blk["overlap"] / blk["pool_n"],
                " (clean split: purity is out-of-sample)" if blk["overlap"] == 0 else " (in-sample share of the readout pool)"))
    p = blk["purity"]
    L.append("    held-out purity (leaf, flatLeaf, pool of record) %.3f [%.3f, %.3f]%s" % (
        p["acc"], p["lo"], p["hi"],
        (" | readout: purity %.3f, F6 leaf %+.3f/1000 (control column %s: %.3f, %+.3f)" %
         (blk["readout"]["purity"], blk["readout"]["f6_leaf"], blk["readout"]["control"], blk["readout"]["control_purity"], blk["readout"]["control_f6_leaf"]))
        if blk["readout"] else ""))
    # (a)
    L.append("  (a) existence margin (bar %.3f):" % BAR)
    for s in [blk["root"]] + blk["d1"]:
        e = blk["exist"][s]
        if e["k"] == 0:
            L.append("      %s d%d [%s] n=%d: LEAF (never split)" % (s, e["depth"], e["label"][:24], e["n"]))
            continue
        if e["exact"]:
            mtxt = "accepted k=2: min-pair == joint sepScore %.6f = %.3fx bar (EXACT)" % (e["joint"], e["margin"][0])
        else:
            mtxt = "accepted k=%d: joint sepScore %.6f = %.3fx bar; min-pair NOT recorded, in [1.00, %.3f]x bar (INTERVAL)" % (e["k"], e["joint"], e["margin"][1], e["margin"][1])
        L.append("      %s d%d [%s] n=%d: %s" % (s, e["depth"], e["label"][:24], e["n"], mtxt))
        for r in e["refused"]:
            L.append("          refused k=%d emK=%d: min-pair sep %.5f = %.3fx bar (iter %s, n_site %d)" % (r["k"], r["emK"], r["sep"], r["sep"] / BAR, ",".join(map(str, r["iters"])), r["n"]))
        if e["other"]:
            L.append("          other refusals: %s" % ", ".join("%s x%d" % kv for kv in sorted(e["other"].items())))
        if e["near_bar"]:
            L.append("          NEAR-BAR: a recorded separation lies within %.3f of the bar" % NEAR_BAR)
    # (b)
    ax = blk["axis"]
    L.append("  (b) trunk axis: root k = %d | quantitative cell %s | discursive cell %s | %s | scored %d of 12 on the record's side"
             % (ax["root_k"], ax["qcell"], ax["dcell"], "axis present" if ax["axis_present"] else "AXIS ABSENT (same cell)", ax["on_side"]))
    if ax["root_k"] <= 6:
        L.append("      %-17s %s %6s   majority cell   side" % ("category", "".join("%13s" % c for c in blk["d1"]), "n"))
        for r in ax["rows"]:
            L.append("      %-17s %s %6d   %-13s  %-12s %s" % (r["cat"], "".join("%13d" % r["counts"][c] for c in blk["d1"]), r["n"], r["maj"], r["side"],
                                                              "-" if r["ok"] is None else ("on record side" if r["ok"] else "OFF record side")))
    else:
        L.append("      (%d depth-1 cells: category x cell table omitted; majority cells: %s)" % (ax["root_k"], "; ".join("%s->%s" % (r["cat"], r["maj"]) for r in ax["rows"])))
    # (c)
    L.append("  (c) trunk certification (cert_site_p95; margin observed / p95):")
    for t in blk["trunk"]:
        if not t["in_csv"]:
            L.append("      %s d%d [%s]: NOT IN the site null CSV (leaf?)" % (t["id"], t["depth"], t["label"][:24]))
        else:
            L.append("      %s d%d [%s]: %s observed %.6f p95 %.6f margin %.3f%s" % (t["id"], t["depth"], t["label"][:24], "CERTIFIED" if t["cert"] else "not certified",
                                                                                     t["observed"], t["p95"], t["margin"], "" if t["feasibility"] == "OK" else " feasibility=" + t["feasibility"]))
    L.append("      root certified: %s | all %d depth-1 sites certified: %s" % (blk["root_cert"], len(blk["d1"]), blk["d1_all_cert"]))
    # (d)
    if "identity" in blk:
        idn = blk["identity"]
        L.append("  (d) certified-site identity vs the record: shared train texts %d (record members %d, arm members %d); Jaccard >= %.2f one-to-one greedy: %d of %d record sites reproduce"
                 % (idn["shared"], idn["record_members"], idn["arm_members"], JACCARD, idn["reproduced"], idn["of"]))
        L.append("      %-11s d  %5s  %-7s  %-11s  %-8s  %s" % ("record site", "n", "margin", "arm site", "Jaccard", "verdict"))
        for s in sorted(record["cert_ids"], key=lambda s: -record["sitenull"]["rows"][s]["observed"] / record["sitenull"]["rows"][s]["p95"]):
            rr = record["sitenull"]["rows"][s]
            if s in idn["match"]:
                t, j = idn["match"][s]
                L.append("      %-11s %d  %5d  %7.3f  %-11s  %8.3f  reproduces" % (s, rr["depth"], rr["n"], rr["observed"] / rr["p95"], t, j))
            else:
                j, t = idn["best"][s]
                L.append("      %-11s %d  %5d  %7.3f  %-11s  %8.3f  NOT reproduced (best Jaccard over the arm's certified sites)" % (s, rr["depth"], rr["n"], rr["observed"] / rr["p95"], t or "-", j))
        # (e)
        L.append("  (e) mu-match of the record's %d leaves to this tree at cos >= %.2f: %d of %d (median best cos %.3f)"
                 % (blk["mu"]["n"], MU_COS, blk["mu"]["matched"], blk["mu"]["n"], blk["mu"]["median"]))
    return L


def in_range(x, lo, hi):
    return lo <= x <= hi


def verdict(ok):
    return "HELD" if ok else "FAILED"


# ----------------------------------------------------------------------------------------------- scoring
def score(res, undetermined, failed):
    """res: arm -> block or None (did not build).  Returns text lines with C1-C6 and every prediction."""
    L = []
    built = {a: b for a, b in res.items() if b is not None}
    af_built = [a for a in AF_ARMS if a in built]

    def B(arm):
        return built.get(arm)
    # ---- criteria
    L.append("")
    L.append("=== Criteria (registered; anchor-free arms = %s; control = %s; UNDETERMINED: %s; did not build: %s) ==="
             % (", ".join(AF_ARMS), CONTROL_ARM, ", ".join(sorted(undetermined)) or "none", ", ".join(sorted(failed)) or "none"))
    c1 = {}
    for a in ARMS:
        arm = a["arm"]
        if arm in undetermined:
            c1[arm] = None; L.append("  C1 EXISTENCE %-4s %-13s UNDETERMINED (site null not at %d reps)" % (a["tag"], arm, REPS)); continue
        b = B(arm)
        if b is None:
            c1[arm] = False; L.append("  C1 EXISTENCE %-4s %-13s did not build -> FAIL" % (a["tag"], arm)); continue
        c1[arm] = in_range(b["leaves"], 60, 100)
        L.append("  C1 EXISTENCE %-4s %-13s leaves %d in [60, 100] -> %s" % (a["tag"], arm, b["leaves"], "PASS" if c1[arm] else "FAIL"))
    # an arm whose manifest completed but whose leaf count is outside [60, 100] (CERT's af_bar030 / af_d512 pattern)
    # is a C1 FAIL and NOT BUILT for every other criterion (registration: "every arm that builds"); it stays in the C1
    # sweep and in F2, and is excluded from C2 / C3 / C4 / C5 and from the F1 / F3 counts
    not_built = {arm for arm, v in c1.items() if v is False and built.get(arm) is not None}
    for a in ARMS:
        if a["arm"] in not_built:
            L.append("  C1 FAIL -> not built %-4s %-13s (leaves %d outside [60,100]); C2/C3/C4/C5 not scored (registration: 'every arm that builds')"
                     % (a["tag"], a["arm"], built[a["arm"]]["leaves"]))

    def built_ok(arm):
        return built.get(arm) is not None and arm not in undetermined and arm not in not_built
    n_c1 = sum(1 for v in c1.values() if v)
    c1_sweep = n_c1 >= 4
    L.append("  C1 sweep: %d of %d arms in band (>= 4 of 5 required; %d UNDETERMINED) -> %s%s" % (n_c1, len(c1), sum(1 for v in c1.values() if v is None), "PASS" if c1_sweep else "FAIL",
             "" if sum(1 for v in c1.values() if v is False) < 2 else "  [F2 FIRES: C1 fails in >= 2 arms]"))
    c2, c3d, c3r, c4 = {}, {}, {}, {}
    for arm in AF_ARMS:
        b = B(arm)
        tag = next(a["tag"] for a in ARMS if a["arm"] == arm)
        if not built_ok(arm):
            L.append("  C2/C3/C4 %-4s %-13s %s" % (tag, arm, "UNDETERMINED" if arm in undetermined else "not built -> not scored (C1 carries it)"))
            continue
        ax = b["axis"]
        c2[arm] = ax["root_k"] == 2 and ax["on_side"] >= 11
        L.append("  C2 TRUNK AXIS %-4s %-13s root k = %d, %d of 12 scored categories on the record's side (>= 11) -> %s" % (tag, arm, ax["root_k"], ax["on_side"], "PASS" if c2[arm] else "FAIL"))
        c3d[arm] = b["d1_all_cert"]
        c3r[arm] = b["root_cert"]
        L.append("  C3 TRUNK CERT %-4s %-13s depth-1 sites certified %d of %d (all k=%d depth-1 sites; registration says both, identical at root k=2) -> %s | root certified: %s (margin %.3f)"
                 % (tag, arm, sum(1 for t in b["trunk"][1:] if t["cert"]), len(b["d1"]), len(b["d1"]), "PASS" if c3d[arm] else "FAIL", c3r[arm], b["trunk"][0]["margin"] or float("nan")))
        c4[arm] = in_range(b["cert"], 11, 21) and in_range(b["share"], 0.16, 0.30)
        L.append("  C4 CERT COUNT %-4s %-13s %d of %d certified (%.1f%%): count in [11, 21] and share in [16%%, 30%%] -> %s" % (tag, arm, b["cert"], b["sites"], 100 * b["share"], "PASS" if c4[arm] else "FAIL"))
    c2_all = bool(c2) and all(c2.values())
    n_c2_fail = sum(1 for v in c2.values() if not v)
    L.append("  C2 sweep: holds in %d of %d anchor-free arms that built -> %s%s" % (sum(c2.values()), len(c2), "PASS" if c2_all else "FAIL",
             "  [F1 FIRES: C2 fails in >= 2 arms]" if n_c2_fail >= 2 else ""))
    c3d_all = bool(c3d) and all(c3d.values())
    n_root = sum(1 for v in c3r.values() if v)
    c3r_ok = n_root >= 3
    L.append("  C3 sweep: depth-1 certified in every built anchor-free arm -> %s | root certified in %d of %d anchor-free arms (>= 3 of 4 required) -> %s"
             % ("PASS" if c3d_all else "FAIL", n_root, len(c3r), "PASS" if c3r_ok else "FAIL"))
    c4_all = bool(c4) and all(c4.values())
    L.append("  C4 sweep: -> %s" % ("PASS" if c4_all else "FAIL"))
    c5 = {}
    for arm in SAMPLE_ARMS + [ORDER_ARM]:
        b = B(arm)
        tag = next(a["tag"] for a in ARMS if a["arm"] == arm)
        need = 14 if arm == ORDER_ARM else 6
        if not built_ok(arm):
            L.append("  C5 IDENTITY %-4s %-13s %s" % (tag, arm, "UNDETERMINED" if arm in undetermined else "not built -> not scored (C1 carries it)"))
            c5[arm] = None
            continue
        c5[arm] = b["identity"]["reproduced"] >= need
        L.append("  C5 IDENTITY %-4s %-13s %d of %d record sites reproduce (>= %d) -> %s" % (tag, arm, b["identity"]["reproduced"], b["identity"]["of"], need, "PASS" if c5[arm] else "FAIL"))
    f3 = any(c5.get(a) is False for a in SAMPLE_ARMS)
    if f3:
        L.append("  [F3 FIRES: C5 fails in a sample arm]")
    stable = None
    if all(built_ok(a) for a in SAMPLE_ARMS):
        stable = [s for s in built[SAMPLE_ARMS[0]]["identity"]["match"] if all(s in built[a]["identity"]["match"] for a in SAMPLE_ARMS)]
        rec_rows = built[SAMPLE_ARMS[0]]["record_rows"]
        L.append("  RE-DRAW-STABLE CERTIFIED SET (reproduces in R1, R2 and R3): %d of %d: %s" % (len(stable), RECORD_CERT,
                 ", ".join("%s(n=%d, margin %.2f)" % (s, rec_rows[s]["n"], rec_rows[s]["observed"] / rec_rows[s]["p95"]) for s in sorted(stable)) or "none"))
    else:
        L.append("  RE-DRAW-STABLE CERTIFIED SET: not computable (a sample arm is not built or UNDETERMINED)")
    r1, r1c = B("af_clean_s42"), B(CONTROL_ARM)
    if r1 is not None and r1c is not None and "af_clean_s42" not in undetermined and CONTROL_ARM not in undetermined:
        c6 = r1["cert"] >= r1c["cert"] + 8
        L.append("  C6 CONTROL: R1 certifies %d, R1c %d: R1 >= R1c + 8 -> %s%s" % (r1["cert"], r1c["cert"], "PASS" if c6 else "FAIL", "  [F4 FIRES]" if not c6 else ""))
    else:
        c6 = None
        L.append("  C6 CONTROL: not scorable (R1 or R1c did not build / UNDETERMINED)")

    # ---- predictions
    L.append("")
    L.append("=== Predictions (registered before any build; scored HELD / FAILED with the number beside) ===")

    def P(scope, text, ok, num):
        L.append("  %-4s %-58s %-14s %s" % (scope, text, "NOT SCORABLE" if ok is None else ("NOT DECIDABLE" if ok == "interval" else verdict(ok)), num))

    def margins_line(b):
        parts, dec = [], True
        for s in b["d1"]:
            e = b["exist"][s]
            if e["exact"]:
                parts.append("%s %.3fx exact" % (s, e["margin"][0]))
            else:
                parts.append("%s [1.00, %.3f]x interval" % (s, e["margin"][1]))
                dec = False
        return parts, dec

    def sample_arm_preds(arm, tag, leaves_band, cat_lo, cert_band, repro_band, mu_band, purity_band=None, f6_band=None, d1_margin=None, root_p=None, sites_band=None, share_band=None, leaves_label=None):
        b = B(arm)
        if b is None:
            if arm in undetermined:
                P(tag, "builds", None, "UNDETERMINED (declared; site null not complete)")
            else:
                P(tag, "builds", False, "did not build")
            return
        P(tag, leaves_label or ("builds, leaves %d-%d" % leaves_band), in_range(b["leaves"], *leaves_band), "leaves %d%s" % (b["leaves"], "" if in_range(b["leaves"], 60, 100) else " (C1 FAIL: not built)"))
        if d1_margin:
            parts, dec = margins_line(b)
            exact_bad = [s for s in b["d1"] if b["exist"][s]["exact"] and not in_range(b["exist"][s]["margin"][0], *d1_margin)]
            # an exact (k = 2) margin outside the band decides FAILED; an interval [1.00, joint/bar] always overlaps the band
            # (both contain 1.00) and can never decide HELD, so any k > 2 site leaves the prediction NOT DECIDABLE
            ok = False if exact_bad else (True if dec else "interval")
            P(tag, "depth-1 margins %.1f-%.1fx the bar (accepted min-pair)" % d1_margin, ok, "; ".join(parts))
        P(tag, "root k = 2", b["axis"]["root_k"] == 2, "root k = %d" % b["axis"]["root_k"])
        P(tag, "%d-12 of 12 categories on the record's side" % cat_lo if cat_lo < 12 else "12 of 12 categories on the record's side", b["axis"]["on_side"] >= cat_lo, "%d of 12" % b["axis"]["on_side"])
        d1m = [t for t in b["trunk"][1:]]
        if d1_margin and root_p is not None:
            P(tag, "both depth-1 sites certified at >= 1.6x p95", len(d1m) == 2 and all(t["cert"] and t["margin"] >= 1.6 for t in d1m),
              "; ".join("%s %s %.3f" % (t["id"], "cert" if t["cert"] else "not cert", t["margin"] or 0) for t in d1m))
            P(tag, "root certified (p 0.6)", b["root_cert"], "root %s, margin %.3f" % ("certified" if b["root_cert"] else "not certified", b["trunk"][0]["margin"] or 0))
        else:
            P(tag, "depth-1 certified (all)", b["d1_all_cert"], "; ".join("%s %s %.3f" % (t["id"], "cert" if t["cert"] else "not cert", t["margin"] or 0) for t in d1m))
        if sites_band:
            P(tag, "%d-%d certified of %d-%d sites (%d-%d%%)" % (cert_band + sites_band + share_band),
              in_range(b["cert"], *cert_band) and in_range(b["sites"], *sites_band) and in_range(100 * b["share"], *share_band),
              "%d of %d (%.1f%%)" % (b["cert"], b["sites"], 100 * b["share"]))
        else:
            P(tag, "%d-%d certified" % cert_band, in_range(b["cert"], *cert_band), "%d of %d (%.1f%%)" % (b["cert"], b["sites"], 100 * b["share"]))
        P(tag, "%d-%d of 16 sites reproduce" % repro_band, in_range(b["identity"]["reproduced"], *repro_band), "%d of %d" % (b["identity"]["reproduced"], b["identity"]["of"]))
        P(tag, "mu-match %d-%d of 81" % mu_band, in_range(b["mu"]["matched"], *mu_band), "%d of %d" % (b["mu"]["matched"], b["mu"]["n"]))
        if purity_band:
            P(tag, "held-out purity %.2f-%.2f (clean split; below the record's 0.715)" % purity_band, in_range(b["purity"]["acc"], *purity_band), "%.3f [%.3f, %.3f]" % (b["purity"]["acc"], b["purity"]["lo"], b["purity"]["hi"]))
        if f6_band:
            if b["readout"]:
                P(tag, "key-only leaf information %+.1f to %+.1f / 1000" % f6_band, in_range(b["readout"]["f6_leaf"], *f6_band), "%+.3f / 1000 (readout)" % b["readout"]["f6_leaf"])
            else:
                P(tag, "key-only leaf information %+.1f to %+.1f / 1000" % f6_band, None, "no readout file")

    sample_arm_preds("af_clean_s42", "R1", (74, 90), 12, (13, 19), (7, 10), (50, 65), purity_band=(0.68, 0.71), f6_band=(12.5, 13.5),
                     d1_margin=(1.0, 1.2), root_p=0.6, sites_band=(60, 80), share_band=(20, 26))
    if r1c is not None:
        P("R1c", "80-92 leaves", in_range(r1c["leaves"], 80, 92), "leaves %d" % r1c["leaves"])
        P("R1c", "3-7 certified of 60-70", in_range(r1c["cert"], 3, 7) and in_range(r1c["sites"], 60, 70), "%d of %d" % (r1c["cert"], r1c["sites"]))
        P("R1c", "purity 0.74-0.77", in_range(r1c["purity"]["acc"], 0.74, 0.77), "%.3f [%.3f, %.3f]" % (r1c["purity"]["acc"], r1c["purity"]["lo"], r1c["purity"]["hi"]))
        if r1 is not None:
            d = 100 * (r1["purity"]["acc"] - r1c["purity"]["acc"])
            P("R1c", "R1 - R1c purity -5 to -9pp (like-for-like: both clean)", in_range(d, -9, -5), "%+.1fpp (%.3f - %.3f)" % (d, r1["purity"]["acc"], r1c["purity"]["acc"]))
    else:
        P("R1c", "builds (80-92 leaves)", False, "did not build / UNDETERMINED")
    for arm, tag in (("af_s137", "R2"), ("af_s2048", "R3")):
        sample_arm_preds(arm, tag, (60, 100), 11, (12, 20), (6, 10), (50, 65), leaves_label="builds (C1 band; no registered leaves prediction for R2/R3)")
        b = B(arm)
        if b is not None:
            P(tag, "held-out purity (in-sample share printed; no band registered)", None, "%.3f, pool overlap %d of %d (%.1f%%)" % (b["purity"]["acc"], b["overlap"], b["pool_n"], 100 * b["overlap"] / b["pool_n"]))
    sample_built = [a for a in SAMPLE_ARMS if built_ok(a)]
    sample_undet = [a for a in SAMPLE_ARMS if a in undetermined]
    n_root_sample = sum(1 for a in sample_built if B(a)["root_cert"])
    P("R1-3", "root certified in 2 of the 3 sample arms", None if sample_undet else n_root_sample == 2,
      "%d of 3 (%d built; a non-building arm certifies nothing): %s%s" % (n_root_sample, len(sample_built),
       ", ".join("%s %s" % (a, "cert" if B(a)["root_cert"] else "no") for a in sample_built), "; UNDETERMINED: " + ", ".join(sample_undet) if sample_undet else ""))
    near = [a for a in sample_built if any(B(a)["exist"][s]["near_bar"] for s in B(a)["d1"])]
    P("R1-3", "ONE sample arm has a depth-1 separation within 0.002 of the bar", None if sample_undet else len(near) == 1,
      "%d arm(s): %s (recorded seps = refused-k min-pairs + the joint score at an accepted k = 2)%s" % (len(near), ", ".join(near) or "none",
       "; UNDETERMINED: " + ", ".join(sample_undet) if sample_undet else ""))
    r4 = B(ORDER_ARM)
    if r4 is not None:
        P("R4", "leaves 79-83", in_range(r4["leaves"], 79, 83), "leaves %d" % r4["leaves"])
        P("R4", "certified 15-17", in_range(r4["cert"], 15, 17), "%d of %d" % (r4["cert"], r4["sites"]))
        P("R4", ">= 14 of 16 sites reproduce", r4["identity"]["reproduced"] >= 14, "%d of %d" % (r4["identity"]["reproduced"], r4["identity"]["of"]))
        P("R4", "mu-match >= 78 of 81", r4["mu"]["matched"] >= 78, "%d of %d" % (r4["mu"]["matched"], r4["mu"]["n"]))
    else:
        P("R4", "builds", False, "did not build / UNDETERMINED")
    # sweep predictions
    P("SW", "C1 HELD (4-5 of 5)", c1_sweep and n_c1 in (4, 5), "%d of %d" % (n_c1, len(c1)))
    P("SW", "C2 HELD in every arm", c2_all, "%d of %d anchor-free arms" % (sum(c2.values()), len(c2)))
    P("SW", "C3 depth-1 HELD", c3d_all, "%d of %d arms" % (sum(c3d.values()), len(c3d)))
    P("SW", "C3 root FAILS at exactly 2 of 4", (n_root == 2) and len(c3r) == 4, "root certified in %d of %d" % (n_root, len(c3r)))
    P("SW", "C4 HELD", c4_all, "%d of %d arms" % (sum(c4.values()), len(c4)))
    for arm, tag, band in (("af_clean_s42", "R1", (6, 10)), ("af_s137", "R2", (6, 10)), ("af_s2048", "R3", (6, 10)), (ORDER_ARM, "R4", (14, 16))):
        b = B(arm)
        P("SW", "C5 HELD in %s at %d-%d" % (tag, band[0], band[1]), None if arm in undetermined else (built_ok(arm) and in_range(b["identity"]["reproduced"], *band)),
          "%s" % ("%d of 16" % b["identity"]["reproduced"] if built_ok(arm) else ("UNDETERMINED" if arm in undetermined else "not built (C1 FAIL)")))
    P("SW", "C6 HELD", bool(c6), "R1 %s vs R1c %s" % (r1["cert"] if r1 else "-", r1c["cert"] if r1c else "-"))
    if stable is not None:
        rec_rows = built[SAMPLE_ARMS[0]]["record_rows"]
        P("SW", "re-draw-stable certified set 5-8 sites, all record n >= 560", in_range(len(stable), 5, 8) and all(rec_rows[s]["n"] >= 560 for s in stable),
          "%d sites; min record n %s" % (len(stable), min((rec_rows[s]["n"] for s in stable), default="-")))
    else:
        P("SW", "re-draw-stable certified set 5-8 sites, all record n >= 560", None, "not computable")
    L.append("")
    L.append("  Readout-pool rule: purity is scored on the pool of record for every tree; that pool is in-sample for the record (%s) and for R2 / R3 / R4 by the"
             % ("2,406 of 3,445 members = 69.8% found; 70.4% of the split's train side, programme L3821"))
    L.append("  overlaps printed per arm, and out-of-sample for R1 / R1c.  Like-for-like pairs: R1 vs R1c; R2 / R3 / R4 vs the record.  R1 vs the record")
    L.append("  confounds re-draw with contamination removal and is read only as the registered prediction (0.68-0.71).")
    return L


# ----------------------------------------------------------------------------------------------- modes
def load_corpus_ctx():
    train, heldout, cs = afr.corpus(POOL)
    vec = afr.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    miss = [t for t, _ in train + heldout if t not in vec]
    if miss:
        raise SystemExit("[REDRAW] %d corpus texts have no embedding" % len(miss))
    return (train, heldout, vec), cs


def analyse_record(ctx):
    rec = analyse_tree("record af/seed_42", RECORD_DIR, RECORD_CSV, ctx, readout_path=RECORD_READOUT if os.path.exists(RECORD_READOUT) else None)
    rec["record_rows"] = rec["sitenull"]["rows"]
    if rec["cert"] != RECORD_CERT:
        raise SystemExit("[REDRAW] the record's site null certifies %d, not %d" % (rec["cert"], RECORD_CERT))
    return rec


def selftest():
    print(pool_guard.assert_pool_of_record(POOL))
    # REASON_RE: the unprimed (REDRAW) form and the K-SELECTION primed form (bar_eff between bar and k) both parse;
    # asserted here (not one of the counted checks below: the record's 17 stay 17)
    m_old = REASON_RE.search("min_pair_sep_below_bar(sep=0.02410,bar=0.02500,k=2,emK=2)")
    m_new = REASON_RE.search("min_pair_sep_below_bar(sep=0.02515,bar=0.02500,bar_eff=0.02625,k=2,emK=3)")
    assert m_old and m_old.groups() == ("0.02410", "0.02500", None, "2", "2"), m_old and m_old.groups()
    assert m_new and m_new.groups() == ("0.02515", "0.02500", "0.02625", "2", "3"), m_new and m_new.groups()
    assert REASON_RE.search("min_pair_sep_below_bar(sep=0.02515,bar_eff=0.02625,bar=0.02500,k=2,emK=3)") is None
    print("  REASON_RE: unprimed row -> bar_eff None; primed row -> bar_eff 0.02625 (k, emK unchanged)")
    ctx, cs = load_corpus_ctx()
    rec = analyse_record(ctx)
    # the record against itself: identity, mu-match, axis
    blk = analyse_tree("record-vs-record", RECORD_DIR, RECORD_CSV, ctx, record=rec, readout_path=RECORD_READOUT if os.path.exists(RECORD_READOUT) else None)
    blk["record_rows"] = rec["record_rows"]
    for line in fmt_block(blk, rec, tag="SELF", kind="record vs record"):
        print(line)
    checks = []
    idn = blk["identity"]
    checks.append(("16 of 16 certified sites reproduce", idn["reproduced"] == 16 and idn["of"] == 16))
    checks.append(("every match at Jaccard 1.0", all(abs(j - 1.0) < 1e-12 for _, j in idn["match"].values())))
    checks.append(("shared train texts = all 8133 members", idn["shared"] == len(rec["all_members"]) == 8133))
    checks.append(("mu-match 81 of 81", blk["mu"]["matched"] == 81 and blk["mu"]["n"] == 81))
    checks.append(("root k = 2", blk["axis"]["root_k"] == 2))
    checks.append(("12 of 12 categories on the record's side (Q cell n00000004, D cell n00000005)",
                   blk["axis"]["on_side"] == 12 and blk["axis"]["qcell"] == "n00000004" and blk["axis"]["dcell"] == "n00000005"))
    rows = {r["cat"]: r for r in blk["axis"]["rows"]}
    checks.append(("business 120 / 112 and CS 68 / 55 as the readout L43 / L47 (reported, not scored)",
                   rows["business"]["counts"]["n00000004"] == 120 and rows["business"]["counts"]["n00000005"] == 112
                   and rows["computer science"]["counts"]["n00000005"] == 68 and rows["computer science"]["counts"]["n00000004"] == 55))
    checks.append(("purity 0.715 (readout L7)", abs(blk["purity"]["acc"] - 0.715) < 0.0006))
    checks.append(("certified 16 of 69", blk["cert"] == 16 and blk["sites"] == 69))
    checks.append(("leaves 81 / nodes 150", blk["leaves"] == 81 and blk["nodes"] == 150))
    e4, e5, er = blk["exist"]["n00000004"], blk["exist"]["n00000005"], blk["exist"]["n00000001"]
    checks.append(("(a) n00000004 refused k=2 emK=2 sep 0.02410; n00000005 refused 0.01331 (emK 2) / 0.01360 (emK 3)",
                   [(r["k"], r["emK"], r["sep"]) for r in e4["refused"]] == [(2, 2, 0.0241)]
                   and [(r["k"], r["emK"], r["sep"]) for r in e5["refused"]] == [(2, 2, 0.01331), (2, 3, 0.0136)]))
    checks.append(("(a) joint sepScore n00000004 0.056435 / n00000005 0.059454 / root 0.042168 (k = 2, exact)",
                   abs(e4["joint"] - 0.056435) < 1e-6 and abs(e5["joint"] - 0.059454) < 1e-6 and abs(er["joint"] - 0.042168) < 1e-6 and er["exact"]))
    checks.append(("(a) NEAR-BAR at n00000004 (0.02410 within 0.002 of 0.025), not at n00000005 or the root",
                   e4["near_bar"] and not e5["near_bar"] and not er["near_bar"]))
    tr = {t["id"]: t for t in blk["trunk"]}
    checks.append(("(c) margins root 1.122 / n00000005 2.100 / n00000004 1.729, all certified",
                   all(tr[i]["cert"] for i in ("n00000001", "n00000005", "n00000004"))
                   and abs(tr["n00000001"]["margin"] - 1.1225) < 5e-4 and abs(tr["n00000005"]["margin"] - 2.0996) < 5e-4 and abs(tr["n00000004"]["margin"] - 1.7285) < 5e-4))
    checks.append(("site n from leaf unions = site-null n (root 8133, n00000005 4508, n00000004 3757)",
                   len(rec["members"]["n00000001"]) == 8133 and len(rec["members"]["n00000005"]) == 4508 and len(rec["members"]["n00000004"]) == 3757))
    checks.append(("pool of record among members 2406 of 3445", blk["overlap"] == 2406))
    checks.append(("q_ id = 'q_' + SHA-256(text)[:16] (embeddings_cache.db queries.id vs raw_text on the members)", qid_check(rec["all_members"])))
    print("")
    print("=== SELFTEST (record vs record) ===")
    bad = 0
    for name, ok in checks:
        print("  %-4s %s" % ("PASS" if ok else "FAIL", name))
        bad += (not ok)
    print("  SELFTEST %s (%d of %d checks)" % ("PASS" if not bad else "FAIL", len(checks) - bad, len(checks)))
    return 0 if not bad else 2


def qid_check(member_ids):
    con = sqlite3.connect("file:%s?mode=ro" % afr.EMB_DB.replace("\\", "/"), uri=True)
    try:
        txt = dict(con.execute("SELECT id, raw_text FROM queries"))
    finally:
        con.close()
    return all(i in txt and qid(txt[i]) == i for i in member_ids)


def dry_run(failed, undetermined):
    print(pool_guard.assert_pool_of_record(POOL))
    print("=== ANCHOR-FREE-REDRAW dry-run (zero calls; nothing written) ===")
    print("  record: %s | %s | readout %s | snapshots.db %s (mode=ro, immutable=1)" % (rel(RECORD_DIR), rel(RECORD_CSV), rel(RECORD_READOUT), "present" if os.path.exists(SNAP_DB) else "MISSING"))
    print("  bar %.3f | reps required %d | Jaccard >= %.2f on shared train texts | mu-match cos >= %.2f | outcome -> %s" % (BAR, REPS, JACCARD, MU_COS, rel(OUTCOME)))
    print("  operator: a build that crashed without run_manifest.json needs --failed <arm>; a site null not complete at %d reps needs --undetermined <arm>; else --run refuses" % REPS)
    ready = True
    for a in ARMS:
        p = arm_paths(a)
        state, why = build_state(a, p, failed)
        print("  %-4s %-13s [%s] one key: %s" % (a["tag"], a["arm"], a["kind"], a["key"]))
        print("       run dir   %s : %s (%s)" % (rel(p["run_dir"]), "present" if os.path.isdir(p["run_dir"]) else "ABSENT", state + ", " + why))
        print("       manifest  %s : %s" % (rel(p["manifest"]), "present" if os.path.exists(p["manifest"]) else "ABSENT"))
        print("       proposals %s : %s" % (rel(p["proposals"]), "present" if os.path.exists(p["proposals"]) else "ABSENT"))
        if os.path.exists(p["csv"]):
            try:
                sn = read_site_null(p["csv"])
                print("       site null %s : %d sites, %d reps, snapshot %s, certified %d" % (rel(p["csv"]), sn["sites"], REPS, sn["snapshot"], len(sn["cert"])))
            except SystemExit as e:
                print("       site null %s : REFUSED (%s)" % (rel(p["csv"]), e)); ready = False
        else:
            print("       site null %s : ABSENT" % rel(p["csv"])); ready = ready and state == "did-not-build"
        ro = find_readout(p)
        print("       readout   %s" % (rel(ro) if ro else "ABSENT (looked in: %s)" % ", ".join(rel(c) for c in p["readout_candidates"])))
        print("       per-arm output -> %s" % rel(p["per_arm_out"]))
        if state not in ("built", "did-not-build") or (state == "built" and not ro):
            ready = False
    print("  readout-pool rule: purity on the pool of record is ~70% in-sample for the record / R2 / R3 / R4 and clean for R1 / R1c; like-for-like pairs R1 vs R1c and R2 / R3 / R4 vs the record")
    print("  --run would %s" % ("proceed" if ready else "REFUSE (inputs incomplete; see above)"))
    print("  dry-run: the readout is refused here by design; nothing was written")
    return 0


def analyse_arm(a, ctx, rec, failed, undetermined, readout_override=None):
    p = arm_paths(a)
    state, why = build_state(a, p, failed)
    if state == "did-not-build":
        return None, "%s %s: did not build (%s) -> C1 FAIL" % (a["tag"], a["arm"], why)
    if state != "built":
        raise SystemExit("[REDRAW] %s %s: %s (%s); not scored, never re-run an arm" % (a["tag"], a["arm"], state, why))
    if not os.path.exists(p["csv"]):
        raise SystemExit("[REDRAW] %s %s: site null %s missing (UNDETERMINED is declared with --undetermined %s, never a partial null)" % (a["tag"], a["arm"], rel(p["csv"]), a["arm"]))
    ro = find_readout(p, readout_override)
    if ro is None:
        raise SystemExit("[REDRAW] %s %s: anchor_free_%s_readout.txt not found (run anchor_free_readout.py %s af/seed_42 first)" % (a["tag"], a["arm"], a["arm"], rel(p["run_dir"])))
    blk = analyse_tree(a["arm"], p["run_dir"], p["csv"], ctx, record=rec, readout_path=ro)
    blk["record_rows"] = rec["record_rows"]
    return blk, None


def header_lines(cs):
    return ["=== ANCHOR-FREE-REDRAW readout (registered 2026-09-17, programme L4627-4781; zero LLM calls) ===",
            "  pool of record: %s | corpus: %d mmlu_pro rows, %d distinct texts, held-out %d | record: %s, %s (%d certified of 69)"
            % (POOL, cs["rows"], cs["distinct"], 3445, rel(RECORD_DIR), rel(RECORD_CSV), RECORD_CERT),
            "  instrument: (a) existence margin (refused-k min-pair from proposals.csv; accepted joint sepScore = dasguptaDeltaNorm; min-pair exact at k = 2 only)",
            "              (b) trunk axis on the 12 scored categories (flatLeaf, pool of record); (c) trunk cert margins observed / p95; (d) Jaccard >= %.2f on shared train texts, one-to-one greedy;" % JACCARD,
            "              (e) mu-match cos >= %.2f | snapshots.db: table snapshots, column graph (SerializedGraph JSON: nodes[].childIds, nodes[].queryIds), opened mode=ro&immutable=1" % MU_COS,
            "  operator: a build that crashed without diagnostics/run_manifest.json must be declared with --failed <arm> (C1 FAIL, never retried); a site null that did not",
            "            complete at %d reps with --undetermined <arm> (never a partial null); otherwise --run / --arm REFUSE. A completed build with leaves outside [60, 100]" % REPS,
            "            is a C1 FAIL and 'not built' for C2-C5 automatically."]


def check_inputs(arms, failed, undetermined, readout_override=None):
    """Refuse BEFORE the corpus load: every arm is built (manifest completed + snapshot) with its 300-rep site null and
    readout, or did not build (manifest not completed / --failed), or is declared --undetermined."""
    for a in arms:
        if a["arm"] in undetermined:
            continue
        p = arm_paths(a)
        state, why = build_state(a, p, failed)
        if state == "did-not-build":
            continue
        if state != "built":
            raise SystemExit("[REDRAW] %s %s: %s (%s); not scored, never re-run an arm" % (a["tag"], a["arm"], state, why))
        if not os.path.exists(p["csv"]):
            raise SystemExit("[REDRAW] %s %s: site null %s missing (UNDETERMINED is declared with --undetermined %s, never a partial null)" % (a["tag"], a["arm"], rel(p["csv"]), a["arm"]))
        read_site_null(p["csv"])
        if find_readout(p, readout_override) is None:
            raise SystemExit("[REDRAW] %s %s: anchor_free_%s_readout.txt not found (run anchor_free_readout.py %s af/seed_42 first)" % (a["tag"], a["arm"], a["arm"], rel(p["run_dir"])))


def run_arm(arm_name, failed, undetermined, readout_override):
    a = next((x for x in ARMS if x["arm"] == arm_name), None)
    if a is None:
        raise SystemExit("[REDRAW] unknown arm %r; arms: %s" % (arm_name, ", ".join(x["arm"] for x in ARMS)))
    print(pool_guard.assert_pool_of_record(POOL))
    check_inputs([a], failed, undetermined, readout_override)
    ctx, cs = load_corpus_ctx()
    rec = analyse_record(ctx)
    blk, note = analyse_arm(a, ctx, rec, failed, undetermined, readout_override)
    L = header_lines(cs)
    if blk is None:
        L.append(note)
    else:
        L += fmt_block(blk, rec, tag=a["tag"], kind=a["kind"])
    txt = "\n".join(L)
    print(txt)
    out = arm_paths(a)["per_arm_out"]
    os.makedirs(REDRAW, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt + "\n")
    print("  written: %s" % rel(out))
    return 0


def run_all(failed, undetermined):
    print(pool_guard.assert_pool_of_record(POOL))
    if set(failed) | set(undetermined) >= {a["arm"] for a in ARMS}:
        raise SystemExit("[REDRAW] every arm is declared --failed / --undetermined: nothing to score, no outcome written")
    check_inputs(ARMS, failed, undetermined)
    ctx, cs = load_corpus_ctx()
    rec = analyse_record(ctx)
    L = header_lines(cs)
    L.append("  arms scored: %s | declared UNDETERMINED: %s | declared failed: %s"
             % (", ".join("%s=%s" % (a["tag"], a["arm"]) for a in ARMS), ", ".join(sorted(undetermined)) or "none", ", ".join(sorted(failed)) or "none"))
    L.append("")
    L += fmt_block(rec, rec, tag="REC", kind="record (the tree every arm is compared to)")
    res, notes = {}, []
    for a in ARMS:
        if a["arm"] in undetermined:
            res[a["arm"]] = None
            notes.append("%s %s: UNDETERMINED (declared; site null not complete at %d reps; not read)" % (a["tag"], a["arm"], REPS))
            continue
        blk, note = analyse_arm(a, ctx, rec, failed, undetermined)
        res[a["arm"]] = blk
        if note:
            notes.append(note)
    for n in notes:
        L.append("  " + n)
    for a in ARMS:
        b = res[a["arm"]]
        if b is not None:
            L.append("")
            L += fmt_block(b, rec, tag=a["tag"], kind=a["kind"])
    L += score(res, undetermined, failed)
    txt = "\n".join(L)
    print(txt)
    os.makedirs(REDRAW, exist_ok=True)
    with open(OUTCOME, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt + "\n")
    print("  written: %s" % rel(OUTCOME))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true", help="list the inputs per arm; write nothing")
    g.add_argument("--selftest", action="store_true", help="the record against itself")
    g.add_argument("--arm", default=None, help="analyse ONE arm and write anchor_free_redraw_<arm>.txt")
    g.add_argument("--run", action="store_true", help="all five arms -> anchor_free_redraw_outcome.txt")
    ap.add_argument("--undetermined", action="append", default=[], metavar="ARM", help="declare an arm UNDETERMINED (its site null did not complete at 300 reps); never a partial null")
    ap.add_argument("--failed", action="append", default=[], metavar="ARM", help="declare a build that crashed before its manifest (C1 FAIL); never a retry")
    ap.add_argument("--readout", default=None, help="(--arm) explicit path of the arm's anchor_free_<arm>_readout.txt")
    a = ap.parse_args(argv)
    for x in a.undetermined + a.failed:
        if x not in {y["arm"] for y in ARMS}:
            raise SystemExit("[REDRAW] unknown arm %r" % x)
    if a.selftest:
        return selftest()
    if a.dry_run:
        return dry_run(set(a.failed), set(a.undetermined))
    if a.arm:
        return run_arm(a.arm, set(a.failed), set(a.undetermined), a.readout)
    return run_all(set(a.failed), set(a.undetermined))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
