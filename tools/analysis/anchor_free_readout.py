"""ANCHOR-FREE readout (docs/judge_v2_program.md, registered 2026-09-16 before any code). ZERO LLM calls.

  python tools/analysis/anchor_free_readout.py <anchor_free_run_dir> <control_run_dir>
         [--site-null <csv>] [--control-site-null <csv>] [--pool p2dca21ab5f4ef3ae] [--out <txt>]

  e.g.  python tools/analysis/anchor_free_readout.py experiment_results/anchor_free/seed_42 \
                                                     experiment_results/h9_order/o0/seed_42

The SAME Python instrument is applied to both run directories (each = a per-seed export holding
dag_snapshots.jsonl, validation/, diagnostics/run_manifest.json); nothing here reads the runner's
Top-1 or anchor-drift figures, which assume depth-1 = category and are not the measurement.

  (1) PURITY.  Every question is routed to the nearest LEAF centroid: cosine of the first-sliceDim MRL slice
      of its stored 4096-d embedding (embeddings_cache.db, joined by TEXT - the standing id-space rule) against
      the leaf's vmfMu, both unit-normalised - the flatLeaf rule exactly as free_tests_f4_f7.f6 /
      consensus_tree / epoch_null.recell apply it.  Held-out = the pool of record (pool_guard, MMLU_PRO_POOL,
      3,445 eval ids -> eval_question_link text -> mmlu_pro row); train = the other mmlu_pro rows (12,000 minus
      the pool's texts).  Every leaf gets the MAJORITY TRAIN category of the train questions routed to it; the
      held-out score is top-1 agreement of a pool question's true category with its leaf's majority label,
      with a 95% Wilson interval.  The same for depth-1 cells, two ways: (a) the leaf's depth-1 ancestor
      (the tree's own grouping), (b) direct nearest depth-1 centroid.
  (2) STRUCTURE.  Leaves, nodes, max depth, iterations; certified sites from a site-null CSV (gradlew siteNull,
      the dimsweep_report.site_cert reading: rows with cert_site_p95 == true) when one is given or found next
      to the run, else "not run".
  (3) KEY INFORMATION.  (a) the key-only LOO Brier improvement of leaf cells over the marginal, of depth-1
      cells over the marginal, and of the true category over the marginal, on the 10,925 keyed questions -
      free_tests_f4_f7's F6 instrument verbatim (keyed_questions, tree_leaves, embed_matrix, loo_imp are
      imported, not re-implemented; F6 works from a run dir's dag_snapshots.jsonl, no snapshot id needed);
      the paired per-question difference anchor-free minus control with F6's bootstrap CI.  (b) the split-half
      reliability (Spearman-Brown) of the KEY profile over profile_reliability's ARENA12 models at the tree's
      depth-1 cells and at its leaves, on the pool of record routed by (1) - profile_reliability.reliability
      with its key_build, 40 halvings, rng seed 7, cells of >= 50 questions, as that script's main does.
  (4) DESCRIPTIVE.  Migration matrix TrueCategory x depth-1 cell (held-out pool, routed by (1)) for the
      anchor-free tree; greedy mu-match of the CONTROL's leaves to the anchor-free leaves at cos >= 0.95
      (h9_stability's rule, h9_stability.cos).

Criteria (registered): C1 purity within 10pp of the control under this instrument; C2 certified sites >= the
control's minus 2; C3 leaf LOO improvement within 1/1000 Brier of the control's.

NOTE on splits: the control o0 was built on seed 42's own split (manifest reserved_pool_id p8a29d8f3ff75aa55),
not the pool of record, so ~71% of the pool of record sits on o0's TRAIN side (incident of 2026-09-09).  The
instrument is the registered one - the pool of record on both trees - and the manifests' pool ids are printed
so the reader sees which tree was fitted on how much of the held-out set.
"""
import os, sys, csv, glob, json, random, sqlite3, struct, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard                                   # noqa: E402
import consensus_tree as ct                         # noqa: E402  last_snapshot
import free_tests_f4_f7 as F                        # noqa: E402  keyed_questions, tree_leaves, embed_matrix, loo_imp, boot_mean_ci
import profile_reliability as PR                    # noqa: E402  reliability, sb, REPS
import rubric_p8 as p8                              # noqa: E402  ARENA12
import h9_stability as h9                           # noqa: E402  cos
from t3_routing_inflation import wilson             # noqa: E402

EMB_DB = os.path.join(ROOT, "embeddings_cache.db")
EVAL_DB = os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")
MU_MATCH_COS = 0.95
C1_PP = 0.10
C2_SLACK = 2
C3_BRIER = 0.001


# ----------------------------------------------------------------------------------------------- corpus
def corpus(pool_id):
    """(train, heldout): lists of (text, category) with one entry per distinct text; category lower-cased.
    Held-out = the pool of record's 3,445 questions, by eval id -> eval_question_link text; train = every
    other mmlu_pro row's text.  A text carried by several rows keeps its first row's category."""
    ev = sqlite3.connect("file:%s?mode=ro" % EVAL_DB.replace("\\", "/"), uri=True)
    ids = pool_guard.eval_ids(pool_id)
    link = {q: t for q, t in ev.execute("SELECT question_id, question_text FROM eval_question_link") if q in ids}
    missing = ids - set(link)
    if missing:
        raise SystemExit("[ANCHOR-FREE] %d pool ids have no eval_question_link text" % len(missing))
    rows = ev.execute("SELECT id, question, category FROM mmlu_pro ORDER BY id").fetchall()
    cat_of = {}
    for _, t, c in rows:
        cat_of.setdefault(t, c.lower())
    pool_texts = set(link.values())
    not_in_corpus = pool_texts - set(cat_of)
    if not_in_corpus:
        raise SystemExit("[ANCHOR-FREE] %d pool texts are not mmlu_pro rows" % len(not_in_corpus))
    heldout = [(link[q], cat_of[link[q]]) for q in sorted(ids)]
    train = [(t, c) for t, c in cat_of.items() if t not in pool_texts]
    return train, heldout, dict(rows=len(rows), distinct=len(cat_of), pool_rows=sum(1 for _, t, _ in rows if t in pool_texts))


def full_vectors(texts):
    """text -> 4096-d raw vector (big-endian float32 blobs), for the texts asked for."""
    want = set(texts)
    con = sqlite3.connect("file:%s?mode=ro" % EMB_DB.replace("\\", "/"), uri=True)
    vec = {}
    for t, blob in con.execute("SELECT query, vector FROM embeddings"):
        if t in want and isinstance(blob, bytes) and len(blob) % 4 == 0:
            vec[t] = np.array(struct.unpack(">%df" % (len(blob) // 4), blob), dtype=np.float64)
    return vec


def sliced(vec, texts, dim):
    Q = np.stack([vec[t][:dim] for t in texts])
    n = np.linalg.norm(Q, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return Q / n


# ----------------------------------------------------------------------------------------------- tree
def load_tree(run_dir):
    snap = ct.last_snapshot(run_dir)
    nodes = snap["nodes"]
    byid = {n["id"]: n for n in nodes}
    kid2parent = {c: n["id"] for n in nodes for c in n.get("childIds", [])}   # same construction as ct/F6

    def depth1(nid):
        n = byid[nid]
        while n["depth"] > 1:
            n = byid[kid2parent[n["id"]]]
        return n["id"]
    leaves = [n for n in nodes if n["isLeaf"]]
    d1 = [n for n in nodes if n["depth"] == 1]
    dims = {n.get("sliceDim", len(n["vmfMu"])) for n in leaves}
    if len(dims) != 1:
        raise SystemExit("[ANCHOR-FREE] %s: leaves carry several sliceDims %s" % (run_dir, sorted(dims)))
    dim = dims.pop()
    if any(len(n["vmfMu"]) != dim for n in leaves):
        raise SystemExit("[ANCHOR-FREE] %s: vmfMu length differs from sliceDim %d" % (run_dir, dim))
    manifest = {}
    mp = os.path.join(run_dir, "diagnostics", "run_manifest.json")
    if os.path.exists(mp):
        manifest = json.load(open(mp, encoding="utf-8"))
    multi_parent = sum(1 for n in nodes if len(n.get("parentIds", [])) > 1)

    def unit(M):
        M = np.asarray(M, dtype=np.float64)
        n = np.linalg.norm(M, axis=1, keepdims=True); n[n == 0] = 1.0
        return M / n
    return dict(
        run_dir=run_dir, name=run_name(run_dir), iteration=snap["iteration"], nodes=len(nodes), byid=byid,
        leaves=leaves, leaf_ids=[n["id"] for n in leaves], leaf_mu=unit([n["vmfMu"] for n in leaves]),
        leaf_d1=[depth1(n["id"]) for n in leaves], d1=d1, d1_ids=[n["id"] for n in d1],
        d1_mu=unit([n["vmfMu"] for n in d1]) if d1 else np.zeros((0, dim)),
        label={n["id"]: n["label"] for n in nodes}, depth=max(n["depth"] for n in nodes), dim=dim,
        manifest=manifest, multi_parent=multi_parent)


def run_name(run_dir):
    p = os.path.normpath(os.path.abspath(run_dir)).split(os.sep)
    return "/".join(p[-2:])


def route(tree, Q, level="leaf"):
    """index of the nearest centroid (max cosine) at the leaf level or the depth-1 level."""
    M = tree["leaf_mu"] if level == "leaf" else tree["d1_mu"]
    return np.argmax(Q @ M.T, axis=1)


# ----------------------------------------------------------------------------------------------- (1) purity
def purity(tree, train, heldout, vec):
    Qt = sliced(vec, [t for t, _ in train], tree["dim"])
    Qh = sliced(vec, [t for t, _ in heldout], tree["dim"])
    out = {}
    # leaf-routed, then the leaf's depth-1 ancestor
    it = route(tree, Qt); ih = route(tree, Qh)
    for lvl, key_t, key_h in (("leaf", [tree["leaf_ids"][i] for i in it], [tree["leaf_ids"][i] for i in ih]),
                              ("d1_via_leaf", [tree["leaf_d1"][i] for i in it], [tree["leaf_d1"][i] for i in ih])):
        out[lvl] = score_cells(key_t, key_h, train, heldout)
    if len(tree["d1_ids"]):
        it1 = route(tree, Qt, "d1"); ih1 = route(tree, Qh, "d1")
        out["d1_direct"] = score_cells([tree["d1_ids"][i] for i in it1], [tree["d1_ids"][i] for i in ih1], train, heldout)
    else:
        out["d1_direct"] = None
    out["heldout_cell"] = dict(leaf=[tree["leaf_ids"][i] for i in ih], d1=[tree["leaf_d1"][i] for i in ih])
    out["train_cell"] = dict(leaf=[tree["leaf_ids"][i] for i in it], d1=[tree["leaf_d1"][i] for i in it])
    return out


def score_cells(key_t, key_h, train, heldout):
    tc = defaultdict(Counter)
    for k, (_, c) in zip(key_t, train):
        tc[k][c] += 1
    major = {k: cnt.most_common(1)[0][0] for k, cnt in tc.items()}
    hits = sum(1 for k, (_, c) in zip(key_h, heldout) if major.get(k) == c)
    n = len(heldout)
    lo, hi = wilson(hits, n)
    used_h = set(key_h)
    return dict(acc=hits / n, lo=lo, hi=hi, hits=hits, n=n, cells_train=len(tc), cells_heldout=len(used_h),
                cells_heldout_untrained=len(used_h - set(tc)), major=major,
                train_purity=sum(cnt.most_common(1)[0][1] for cnt in tc.values()) / len(train))


# ----------------------------------------------------------------------------------------------- (2) structure
def find_site_null(run_dir, explicit):
    if explicit:
        return explicit
    cands = []
    for d in (run_dir, os.path.dirname(os.path.abspath(run_dir))):
        cands += glob.glob(os.path.join(d, "site_null*.csv"))
    return cands[0] if len(cands) == 1 else None


def site_cert(path):
    """dimsweep_report.site_cert's reading of a siteNull CSV, on an explicit path."""
    if not path or not os.path.exists(path):
        return None
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    return dict(path=path, sites=len(rows), cert=sum(1 for r in rows if r["cert_site_p95"] == "true"),
                defl=sum(1 for r in rows if r["cert_deflated_p95"] == "true"),
                trunk=sum(1 for r in rows if r["trunk_member"] == "true"),
                depth1=[r["label"] for r in rows if r["depth"] == "1" and r["cert_site_p95"] == "true"],
                snapshot=rows[0]["snapshot_id"] if rows else "", reps=rows[0]["reps"] if rows else "")


# ----------------------------------------------------------------------------------------------- (3) key information
def f6_block(run_dir, keyed):
    """The per-tree block of free_tests_f4_f7.f6, on a run dir: F6's own loaders and LOO formula."""
    models, G, cat, text, qs_all = keyed
    leaves = F.tree_leaves(run_dir)                                   # (id, mu, depth-1 label) per leaf
    dim = len(leaves[0][1])
    vec = F.embed_matrix(EMB_DB, list(text.values()), dim)
    qs = [q for q in qs_all if text[q] in vec]
    Q = np.stack([vec[text[q]] for q in qs])
    M = np.stack([mu / (np.linalg.norm(mu) or 1) for _, mu, _ in leaves])
    idx = np.argmax(Q @ M.T, axis=1)
    leaf_p = {q: leaves[i][0] for q, i in zip(qs, idx)}
    anc_p = {q: leaves[i][2].lower() for q, i in zip(qs, idx)}
    il = F.loo_imp(leaf_p, qs, models, G)
    ia = F.loo_imp(anc_p, qs, models, G)
    ic = F.loo_imp({q: cat[q] for q in qs}, qs, models, G)
    agree = sum(anc_p[q] == cat[q] for q in qs) / len(qs)
    return dict(n=len(qs), leaves=len(leaves), dim=dim, leaf=float(il.mean()), anchor=float(ia.mean()),
                category=float(ic.mean()), agree=agree, per_q=dict(zip(qs, il)))


def key_reliability(tree, pur, heldout, heldout_ids):
    """profile_reliability's key instrument: ARENA12 keys, split-half at the tree's depth-1 cells and leaves."""
    models = sorted(p8.ARENA12)
    ev = sqlite3.connect("file:%s?mode=ro" % EVAL_DB.replace("\\", "/"), uri=True)
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in p8.ARENA12 and q in heldout_ids:
            K[q][m] = int(c or 0)

    def key_build(cqs):
        d = {}
        for m in models:
            v = [K[q][m] for q in cqs if q in K and m in K[q]]
            if v:
                d[m] = sum(v) / len(v)
        return d if len(d) == len(models) else None

    out = {}
    qsel = set(q for q in heldout_ids if q in K)
    for name, key in (("leaf", "leaf"), ("depth-1", "d1")):
        cells = defaultdict(list)
        for q, k in zip(heldout_ids, pur["heldout_cell"][key]):
            cells[k].append(q)
        usable = {c: v for c, v in cells.items() if len(v) >= 50}
        if not usable:
            out[name] = dict(R=float("nan"), r=float("nan"), sd=float("nan"), reps=0, cells=0, qpc=0.0)
            continue
        r, sd, n = PR.reliability(usable, qsel, key_build, models, random.Random(7))
        out[name] = dict(R=PR.sb(r), r=r, sd=sd, reps=n, cells=len(usable),
                         qpc=sum(len(v) for v in usable.values()) / len(usable))
    return out


# ----------------------------------------------------------------------------------------------- (4) descriptive
def migration(tree, pur, heldout):
    M = defaultdict(Counter)
    for k, (_, c) in zip(pur["heldout_cell"]["d1"], heldout):
        M[c][k] += 1
    return M


def mu_match(control, other):
    """h9_stability's greedy rule: for each CONTROL leaf, the best unused OTHER leaf; matched if cos >= 0.95."""
    used, matched, best_cos = set(), 0, []
    for f in control["leaves"]:
        best, bi = -1, None
        for i, c in enumerate(other["leaves"]):
            if i in used:
                continue
            s = h9.cos(f["vmfMu"], c["vmfMu"])
            if s > best:
                best, bi = s, i
        best_cos.append(best)
        if best >= MU_MATCH_COS:
            matched += 1
            used.add(bi)
    return matched, len(control["leaves"]), best_cos


# ----------------------------------------------------------------------------------------------- report
def fmt_ci(p):
    return "%.3f [%.3f, %.3f]" % (p["acc"], p["lo"], p["hi"])


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("anchor_free")
    ap.add_argument("control")
    ap.add_argument("--site-null", default=None, help="siteNull CSV for the anchor-free run")
    ap.add_argument("--control-site-null", default=None, help="siteNull CSV for the control run")
    ap.add_argument("--pool", default=pool_guard.MMLU_PRO_POOL)
    ap.add_argument("--out", default=None, help="also write the report to this file")
    a = ap.parse_args(argv)

    L = []
    pid = pool_guard.assert_pool_of_record(a.pool)
    L.append("=== ANCHOR-FREE readout (registered 2026-09-16; zero LLM calls) ===")
    L.append("  pool of record: %s (pool_guard.assert_pool_of_record) | flatLeaf rule: max cosine of the first-sliceDim slice vs vmfMu" % pid)

    runs = [("anchor-free", a.anchor_free), ("control", a.control)]
    trees = {tag: load_tree(rd) for tag, rd in runs}
    for tag, t in trees.items():
        m = t["manifest"]
        L.append("  %-11s %s | snapshot iteration %d | manifest: commit %s, seed %s, split pool %s%s, train %s / test %s"
                 % (tag, t["name"], t["iteration"], str(m.get("commit", "?"))[:8], m.get("seed", "?"),
                    m.get("reserved_pool_id", "?"),
                    "" if m.get("reserved_pool_id") == pid else " (NOT the pool of record: part of the held-out set was on this tree's train side)",
                    m.get("train_size", "?"), m.get("test_size", "?")))
        if t["multi_parent"]:
            L.append("  %-11s %d node(s) with >1 parent; depth-1 ancestor taken through the last-listed parent (ct/F6 convention)" % (tag, t["multi_parent"]))

    train, heldout, cs = corpus(pid)
    heldout_ids = sorted(pool_guard.eval_ids(pid))
    vec = full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    miss = [t for t, _ in train + heldout if t not in vec]
    if miss:
        raise SystemExit("[ANCHOR-FREE] %d corpus texts have no embedding" % len(miss))
    L.append("  corpus: %d mmlu_pro rows, %d distinct texts; held-out %d (pool rows %d); train %d distinct texts; %d categories"
             % (cs["rows"], cs["distinct"], len(heldout), cs["pool_rows"], len(train), len({c for _, c in train})))

    # (1)
    pur = {tag: purity(trees[tag], train, heldout, vec) for tag, _ in runs}
    # (2)
    cert = {"anchor-free": site_cert(find_site_null(a.anchor_free, a.site_null)),
            "control": site_cert(find_site_null(a.control, a.control_site_null))}
    # (3)
    keyed = F.keyed_questions()
    f6 = {tag: f6_block(trees[tag]["run_dir"], keyed) for tag, _ in runs}
    rel = {tag: key_reliability(trees[tag], pur[tag], heldout, heldout_ids) for tag, _ in runs}
    # (4)
    mm, mm_n, mm_cos = mu_match(trees["control"], trees["anchor-free"])
    mig = migration(trees["anchor-free"], pur["anchor-free"], heldout)

    # ---- the table
    A, C = "anchor-free", "control"
    W = 34
    L.append("")
    L.append("  %-46s %*s %*s" % ("readout", W, trees[A]["name"], W, trees[C]["name"]))
    L.append("  " + "-" * (46 + 2 * W + 2))

    def row(name, fa, fc):
        L.append("  %-46s %*s %*s" % (name, W, fa, W, fc))
    row("(1) held-out purity, leaf majority-train label", fmt_ci(pur[A]["leaf"]), fmt_ci(pur[C]["leaf"]))
    row("    leaves used by held-out / with no train member",
        "%d / %d" % (pur[A]["leaf"]["cells_heldout"], pur[A]["leaf"]["cells_heldout_untrained"]),
        "%d / %d" % (pur[C]["leaf"]["cells_heldout"], pur[C]["leaf"]["cells_heldout_untrained"]))
    row("    train-side purity of the leaf labels", "%.3f" % pur[A]["leaf"]["train_purity"], "%.3f" % pur[C]["leaf"]["train_purity"])
    row("    depth-1 cell via the leaf's ancestor", fmt_ci(pur[A]["d1_via_leaf"]), fmt_ci(pur[C]["d1_via_leaf"]))
    row("    depth-1 cell, direct nearest depth-1 centroid",
        fmt_ci(pur[A]["d1_direct"]) if pur[A]["d1_direct"] else "no depth-1 nodes",
        fmt_ci(pur[C]["d1_direct"]) if pur[C]["d1_direct"] else "no depth-1 nodes")
    row("(2) leaves / nodes / max depth / iterations",
        "%d / %d / %d / %d" % (len(trees[A]["leaves"]), trees[A]["nodes"], trees[A]["depth"], trees[A]["iteration"]),
        "%d / %d / %d / %d" % (len(trees[C]["leaves"]), trees[C]["nodes"], trees[C]["depth"], trees[C]["iteration"]))
    row("    depth-1 cells / slice dim", "%d / %d" % (len(trees[A]["d1"]), trees[A]["dim"]), "%d / %d" % (len(trees[C]["d1"]), trees[C]["dim"]))

    def cert_s(c):
        return "not run" if c is None else "%d of %d sites (defl %d; %s reps)" % (c["cert"], c["sites"], c["defl"], c["reps"])
    row("    certified sites (site null, cert_site_p95)", cert_s(cert[A]), cert_s(cert[C]))
    row("(3a) F6 key-only LOO Brier improvement x1000, n=%d" % f6[A]["n"], "", "")
    row("    leaf cells over marginal", "%+.3f" % (1000 * f6[A]["leaf"]), "%+.3f" % (1000 * f6[C]["leaf"]))
    row("    depth-1 cells over marginal", "%+.3f" % (1000 * f6[A]["anchor"]), "%+.3f" % (1000 * f6[C]["anchor"]))
    row("    true category over marginal", "%+.3f" % (1000 * f6[A]["category"]), "%+.3f" % (1000 * f6[C]["category"]))
    row("    leaf minus category", "%+.3f" % (1000 * (f6[A]["leaf"] - f6[A]["category"])), "%+.3f" % (1000 * (f6[C]["leaf"] - f6[C]["category"])))
    row("    depth-1 label == category (F6's line)", "%.1f%%" % (100 * f6[A]["agree"]), "%.1f%%" % (100 * f6[C]["agree"]))
    common = [q for q in f6[A]["per_q"] if q in f6[C]["per_q"]]
    d = np.array([f6[A]["per_q"][q] - f6[C]["per_q"][q] for q in common])
    dlo, dhi = F.boot_mean_ci(d)
    row("    paired leaf diff (AF - control) x1000, 95% CI", "%+.3f [%+.3f, %+.3f]" % (1000 * d.mean(), 1000 * dlo, 1000 * dhi), "n=%d" % len(common))

    def rel_s(r):
        return "R=%.3f (r %.3f sd %.3f, %d cells, %.0f q/cell)" % (r["R"], r["r"], r["sd"], r["cells"], r["qpc"]) if r["cells"] else "no cell >= 50 q"
    row("(3b) key profile split-half R(SB), depth-1 cells", rel_s(rel[A]["depth-1"]), rel_s(rel[C]["depth-1"]))
    row("    key profile split-half R(SB), leaves", rel_s(rel[A]["leaf"]), rel_s(rel[C]["leaf"]))
    row("(4) mu-match of control leaves (cos >= %.2f)" % MU_MATCH_COS, "%d/%d" % (mm, mm_n), "median best cos %.3f" % float(np.median(mm_cos)))

    # ---- criteria
    L.append("")
    L.append("  Criteria (registered):")
    pa, pc = pur[A]["leaf"]["acc"], pur[C]["leaf"]["acc"]
    c1 = pa >= pc - C1_PP
    L.append("    C1 purity within %.0fpp of the control: %.3f vs %.3f (diff %+.1fpp) -> %s"
             % (100 * C1_PP, pa, pc, 100 * (pa - pc), "PASS" if c1 else "FAIL"))
    if cert[A] is None or cert[C] is None:
        L.append("    C2 certified sites >= control's - %d: site null not run for %s -> NOT SCORED"
                 % (C2_SLACK, " and ".join(t for t in (A, C) if cert[t] is None)))
    else:
        c2 = cert[A]["cert"] >= cert[C]["cert"] - C2_SLACK
        L.append("    C2 certified sites >= control's - %d: %d vs %d -> %s" % (C2_SLACK, cert[A]["cert"], cert[C]["cert"], "PASS" if c2 else "FAIL"))
    dl = f6[A]["leaf"] - f6[C]["leaf"]
    c3 = abs(dl) <= C3_BRIER
    L.append("    C3 leaf LOO improvement within %.3f Brier of the control's: %+.5f vs %+.5f (diff %+.5f) -> %s%s"
             % (C3_BRIER, f6[A]["leaf"], f6[C]["leaf"], dl, "PASS" if c3 else "FAIL",
                "" if c3 or dl < 0 else " (anchor-free EXCEEDS the control by more than the band)"))

    # ---- migration matrix
    L.append("")
    cells = sorted(trees[A]["d1_ids"], key=lambda k: -sum(M[k] for M in mig.values()))
    L.append("  (4) migration matrix: TrueCategory x %s depth-1 cell (held-out pool, leaf-routed then depth-1 ancestor)" % A)
    hdr = "  %-17s" % "category" + "".join("%7s" % ("c%d" % i) for i in range(len(cells))) + "   n"
    L.append(hdr)
    for c in sorted(mig, key=lambda c: -sum(mig[c].values())):
        L.append("  %-17s" % c + "".join("%7d" % mig[c].get(k, 0) for k in cells) + "%6d" % sum(mig[c].values()))
    L.append("  %-17s" % "TOTAL" + "".join("%7d" % sum(M.get(k, 0) for M in mig.values()) for k in cells) + "%6d" % len(heldout))
    L.append("  cells: " + "; ".join("c%d=%s [%s] major=%s" % (i, k, trees[A]["label"][k][:28], pur[A]["d1_via_leaf"]["major"].get(k, "-"))
                                     for i, k in enumerate(cells)))

    txt = "\n".join(L)
    print(txt)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
