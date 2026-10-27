"""K-SELECTION I2 inertness check (docs/judge_v2_program.md, "Registered 2026-09-19 (before any code or call) - K-SELECTION",
programme L8224-L8390, commit 8fde7fa; criterion C0 / prediction P6). ZERO LLM calls; reads nothing but two build
directories and snapshots.db (mode=ro, immutable=1); never writes a database.

What it decides.  I2 = af_clean_s42 rebuilt on the merged engine with proposalAcceptMultiplier ABSENT (config
experiment_configs/anchorfree/redraw/kselect/af_clean_s42_inert.toml).  INERT iff the I2 tree's LEAF MEMBERSHIP is
identical to REDRAW R1's (experiment_results/anchorfree/redraw/af_clean_s42/seed_42, snapshot 20260917_201353):
the same number of leaves, and the multiset of leaf member sets (each leaf's queryIds as a set; DAG_MAX multi-
assignment kept as the engine wrote it) is the same.  Node ids MAY permute (a leaf is matched by its member set, not
its id); labels are not compared.  Anything else -> NOT INERT, and C0 fails (the registration: "the tree is the same
tree or I2 fails"; nothing primed is read).

Where membership lives.  dag_snapshots.jsonl carries per-node summaries only (id, depth, isLeaf, directQueries,
subtreeQueries, vmfMu; no queryIds).  The queryIds are in the SerializedGraph the engine saved to snapshots.db
(table snapshots, column graph, nodes[].childIds / nodes[].queryIds; anchor_free_redraw.py (d)); the snapshot id is
the last "Snapshot ID: <id>" of the build's headless_run.log (or of the chain's <arm>.build.out).  This script reads
the graph for the membership verdict and cross-checks it against dag_snapshots.jsonl's last iteration (leaf id set
== graph leaf id set; per-leaf directQueries == len(queryIds)), so the registration's phrase "the leaf member sets
of dag_snapshots.jsonl" is honoured through the file that actually holds the ids.

Supplementary lines (printed, NOT part of the verdict): the internal-node member sets (the union over descendant
leaves) compared the same way; per-matched-leaf vmfMu max |delta| from dag_snapshots.jsonl; sha256 of both
dag_snapshots.jsonl files (byte identity of the whole file is EXPECTED but not required: node ids may permute);
run_manifest.json's proposal_accept_multiplier of I2 (must be 1.0) and the R1 site null's certified count (the 14 of
69 that I2 inherits if INERT; the registration: no new null on I2).

Usage (from the repo root; the chain tools/chains/k_selection.sh calls the first form after the I2 build):
  python tools/analysis/k_selection_inert.py --i2 experiment_results/anchorfree/redraw/kselect/i2/seed_42 \
         --r1 experiment_results/anchorfree/redraw/af_clean_s42/seed_42 \
         [--r1-null experiment_results/anchorfree/redraw/site_null_af_clean_s42.csv] [--out <txt>]
  python tools/analysis/k_selection_inert.py --selftest      # R1 against itself: must print INERT (82 leaves, 0 differences)
Exit status: 0 INERT, 3 NOT INERT, 2 input error (a missing snapshot / file is an input error, never a verdict).
"""
import os, sys, re, csv, json, hashlib, sqlite3, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SNAP_DB = os.path.join(ROOT, "snapshots.db")
R1_DIR = os.path.join(ROOT, "experiment_results", "anchorfree", "redraw", "af_clean_s42", "seed_42")
R1_NULL = os.path.join(ROOT, "experiment_results", "anchorfree", "redraw", "site_null_af_clean_s42.csv")
R1_SNAPSHOT_OF_RECORD = "20260917_201353_Headless_Run_Auto_ge"   # registration (d): snapshot 20260917_201353


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def die(msg, code=2):
    print("[I2] " + msg)
    sys.exit(code)


def snapshot_id(run_dir):
    """The last 'Snapshot ID:' of headless_run.log in the run dir (the chain's <arm>.build.out carries the same line)."""
    cands = [os.path.join(run_dir, "headless_run.log"), os.path.join(run_dir, "diagnostics", "headless_run.log")]
    sid = None
    for p in cands:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = re.search(r"Snapshot ID: (\S+)", line)
                if m:
                    sid = m.group(1)
        if sid:
            return sid, p
    return None, cands[0]


def load_graph(sid):
    if not os.path.exists(SNAP_DB):
        die("%s not found" % rel(SNAP_DB))
    con = sqlite3.connect("file:%s?mode=ro&immutable=1" % SNAP_DB.replace("\\", "/"), uri=True)
    try:
        row = con.execute("SELECT graph FROM snapshots WHERE id = ?", (sid,)).fetchone()
    finally:
        con.close()
    if row is None:
        wal = os.path.join(ROOT, "snapshots.db-wal")
        hint = ""
        if os.path.exists(wal) and os.path.getsize(wal) > 0:
            hint = " (snapshots.db-wal is %d bytes: the writer has not checkpointed; wait for the JVM to exit, never rebuild)" % os.path.getsize(wal)
        die("snapshot %s not in %s%s" % (sid, rel(SNAP_DB), hint))
    g = json.loads(row[0])
    return dict(root=g["rootId"], byid={n["id"]: n for n in g["nodes"]})


def leaf_sets(graph):
    """leaf id -> frozenset(queryIds) for every node without childIds."""
    return {i: frozenset(n.get("queryIds") or []) for i, n in graph["byid"].items() if not (n.get("childIds") or [])}


def subtree_sets(graph):
    """every node id -> frozenset of descendant-leaf queryIds (memoised DFS over childIds)."""
    byid, memo = graph["byid"], {}

    def rec(i, stack):
        if i in memo:
            return memo[i]
        if i in stack:
            die("cycle at %s in the snapshot graph" % i)
        kids = byid[i].get("childIds") or []
        memo[i] = frozenset(byid[i].get("queryIds") or []) if not kids else frozenset().union(*(rec(c, stack | {i}) for c in kids))
        return memo[i]
    for i in byid:
        rec(i, frozenset())
    return memo


def last_jsonl(run_dir):
    p = os.path.join(run_dir, "dag_snapshots.jsonl")
    if not os.path.exists(p):
        die("%s missing" % rel(p))
    last = None
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = json.loads(line)
    if last is None:
        die("%s is empty" % rel(p))
    return p, last


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_multiplier(run_dir):
    p = os.path.join(run_dir, "diagnostics", "run_manifest.json")
    if not os.path.exists(p):
        return None, p
    with open(p, encoding="utf-8") as f:
        m = json.load(f)
    return m.get("proposal_accept_multiplier", "ABSENT"), p


def certified_count(csv_path):
    if not csv_path or not os.path.exists(csv_path):
        return None
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return sum(1 for r in rows if r.get("cert_site_p95", "").lower() in ("true", "1")), len(rows), sorted({r.get("reps", "?") for r in rows})


def tree(run_dir, tag):
    sid, logp = snapshot_id(run_dir)
    if sid is None:
        die("%s: no 'Snapshot ID:' in %s (build failed or absent)" % (tag, rel(logp)))
    g = load_graph(sid)
    jp, last = last_jsonl(run_dir)
    leaves = leaf_sets(g)
    jl = {n["id"]: n for n in last["nodes"] if n.get("isLeaf")}
    # cross-checks between the graph and dag_snapshots.jsonl (the file the registration names)
    if set(jl) != set(leaves):
        die("%s: leaf id set differs between snapshots.db graph (%d) and dag_snapshots.jsonl last iteration (%d)" % (tag, len(leaves), len(jl)))
    bad = [i for i in jl if jl[i].get("directQueries") != len(leaves[i])]
    if bad:
        die("%s: directQueries != len(queryIds) at %d leaves (e.g. %s)" % (tag, len(bad), bad[:3]))
    return dict(tag=tag, run_dir=run_dir, sid=sid, graph=g, leaves=leaves, subtree=subtree_sets(g), jsonl=last, jsonl_path=jp,
                jsonl_sha=sha256(jp), iteration=last.get("iteration"), nodes=len(g["byid"]))


def compare(i2, r1):
    L = []
    P = L.append
    a, b = i2["leaves"], r1["leaves"]
    ma, mb = {}, {}
    for i, s in a.items():
        ma.setdefault(s, []).append(i)
    for i, s in b.items():
        mb.setdefault(s, []).append(i)
    only_i2 = [s for s in ma if s not in mb]
    only_r1 = [s for s in mb if s not in ma]
    mult_diff = [s for s in ma if s in mb and len(ma[s]) != len(mb[s])]
    n_diff = len(only_i2) + len(only_r1) + len(mult_diff)
    inert = (len(a) == len(b)) and n_diff == 0
    P("I2 %s | snapshot %s | nodes %d leaves %d | iterations %s" % (rel(i2["run_dir"]), i2["sid"], i2["nodes"], len(a), i2["iteration"]))
    P("R1 %s | snapshot %s | nodes %d leaves %d | iterations %s" % (rel(r1["run_dir"]), r1["sid"], r1["nodes"], len(b), r1["iteration"]))
    if r1["sid"] != R1_SNAPSHOT_OF_RECORD:
        P("  NOTE R1 snapshot id %s != the registration's %s (the R1 directory on disk is not the one the registration names)" % (r1["sid"], R1_SNAPSHOT_OF_RECORD))
    P("leaf count: I2 %d vs R1 %d -> %s" % (len(a), len(b), "same" if len(a) == len(b) else "DIFFERENT"))
    P("leaf member sets (multiset of frozenset(queryIds), node ids free to permute): %d only in I2, %d only in R1, %d multiplicity differences -> %d differences"
      % (len(only_i2), len(only_r1), len(mult_diff), n_diff))
    P("distinct train ids: I2 %d, R1 %d; leaf slots (DAG_MAX multi-assignment): I2 %d, R1 %d"
      % (len(frozenset().union(*a.values())) if a else 0, len(frozenset().union(*b.values())) if b else 0,
         sum(len(s) for s in a.values()), sum(len(s) for s in b.values())))
    if only_i2 or only_r1:
        # nearest R1 leaf for each unmatched I2 leaf, by Jaccard, so a NOT INERT is legible
        for s in sorted(only_i2, key=len, reverse=True)[:10]:
            bestj, bestid = 0.0, None
            for t, ids in mb.items():
                u = len(s | t)
                j = len(s & t) / u if u else 0.0
                if j > bestj:
                    bestj, bestid = j, ids[0]
            P("    I2 leaf %s (n=%d) unmatched; nearest R1 leaf %s Jaccard %.3f" % (ma[s][0], len(s), bestid, bestj))
        for s in sorted(only_r1, key=len, reverse=True)[:10]:
            P("    R1 leaf %s (n=%d) has no identical I2 leaf" % (mb[s][0], len(s)))
    # the id permutation actually observed (supplementary)
    permuted = sum(1 for s, ids in ma.items() if s in mb and sorted(ids) != sorted(mb[s]))
    P("supplementary: matched leaves whose node ids differ between the trees: %d of %d" % (permuted, len(ma) - len(only_i2)))
    # internal nodes (supplementary): multiset of subtree member sets over non-leaf nodes
    ia = {}
    for i, s in i2["subtree"].items():
        if i not in a:
            ia[s] = ia.get(s, 0) + 1
    ib = {}
    for i, s in r1["subtree"].items():
        if i not in b:
            ib[s] = ib.get(s, 0) + 1
    int_diff = sum(abs(ia.get(s, 0) - ib.get(s, 0)) for s in set(ia) | set(ib))
    P("supplementary: internal-node subtree member sets: I2 %d, R1 %d, differences %d" % (len(ia), len(ib), int_diff))
    # vmfMu per matched leaf (supplementary)
    jl_a = {n["id"]: n for n in i2["jsonl"]["nodes"] if n.get("isLeaf")}
    jl_b = {n["id"]: n for n in r1["jsonl"]["nodes"] if n.get("isLeaf")}
    dmax, checked = 0.0, 0
    for s, ids in ma.items():
        if s in mb:
            va, vb = jl_a[ids[0]].get("vmfMu") or [], jl_b[mb[s][0]].get("vmfMu") or []
            if len(va) == len(vb) and va:
                dmax = max(dmax, max(abs(x - y) for x, y in zip(va, vb)))
                checked += 1
    P("supplementary: vmfMu max |delta| over %d matched leaves: %.6f (dag_snapshots.jsonl prints 6 decimals)" % (checked, dmax))
    P("supplementary: dag_snapshots.jsonl sha256 I2 %s | R1 %s -> %s" % (i2["jsonl_sha"][:16], r1["jsonl_sha"][:16], "byte-identical" if i2["jsonl_sha"] == r1["jsonl_sha"] else "differ (ids may permute; not the criterion)"))
    return inert, L


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--i2", default=None, help="I2 run dir (…/kselect/i2/seed_42)")
    ap.add_argument("--r1", default=R1_DIR, help="R1 run dir (default %s)" % rel(R1_DIR))
    ap.add_argument("--r1-null", default=R1_NULL, help="R1's existing site-null CSV (its certified count is what I2 inherits if INERT)")
    ap.add_argument("--out", default=None, help="also write the report here")
    ap.add_argument("--selftest", action="store_true", help="R1 against itself (must be INERT, 0 differences)")
    args = ap.parse_args(argv)
    if args.selftest:
        args.i2 = args.r1
    if not args.i2:
        ap.error("--i2 <run dir> or --selftest")
    print("pool p2dca21ab5f4ef3ae (R1 / I2 are the clean-split arms on the pool of record by reservedPoolFile; nothing here reads the pool)")
    r1 = tree(args.r1, "R1")
    i2 = tree(args.i2, "I2")
    inert, lines = compare(i2, r1)
    mult, mp = manifest_multiplier(args.i2)
    # The merged engine writes proposal_accept_multiplier on EVERY constructing run (DiagnosticsBundle.
    # recordProposalAcceptMultiplier); I2 must show exactly 1.0. ABSENT means a pre-flag engine built it
    # (not the registered I2); a value != 1.0 means the build was primed. Only the selftest (R1's own
    # pre-flag manifest) is allowed ABSENT.
    mult_ok = (mult == 1.0) or (args.selftest and mult in ("ABSENT", None))
    lines.append("I2 run_manifest.json proposal_accept_multiplier: %s (%s)%s" % (mult, rel(mp),
                 "" if mult_ok else ("  <- ABSENT: not the merged engine (pre-flag manifest); I2 must show 1.0" if mult in ("ABSENT", None)
                                     else "  <- != 1.0: this build was PRIMED, not the inertness build")))
    cc = certified_count(args.r1_null)
    if cc:
        lines.append("R1 site null %s: certified %d of %d sites, reps %s -> %s" % (rel(args.r1_null), cc[0], cc[1], ",".join(cc[2]),
                     "inherited by I2 (same tree; no new null, registration I2)" if (inert and mult_ok) else "NOT inherited"))
    verdict = "INERT" if (inert and mult_ok) else "NOT INERT"
    if args.selftest:
        lines.append("SELFTEST (R1 vs R1): expected INERT with 0 differences and 82 leaves")
    lines.append("I2 INERTNESS VERDICT: %s (C0 / P6 %s)" % (verdict, "HELD" if verdict == "INERT" else "FAILED"))
    txt = "\n".join(lines)
    print(txt)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(txt + "\n")
    sys.exit(0 if verdict == "INERT" else 3)


if __name__ == "__main__":
    main(sys.argv[1:])
