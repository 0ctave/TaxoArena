"""LEAF-PROFILE — is a per-LEAF capability profile real, and can the judged arena see it? (zero calls)

Two tests on the clean promoted tree bareq512_s42 (leaf = nearest leaf centroid on the 512-slice, the
disclosed approximation used by F2/F6):

A) KEY (46 models x all keyed questions, no judge): within each anchor, does the model x leaf
   interaction improve on model + leaf (leaf = difficulty only)? LRT = deviance(additive) -
   deviance(saturated cell means); null by QUESTION-level permutation of leaf membership within the
   anchor (whole questions move; per-leaf counts preserved). Plus F2-style LOO Brier gain of the
   leaf partition over the anchor partition, per anchor.
B) JUDGED (R2 atlas, 36,871 Mistral verdicts with leaf ids, 12 models): within each anchor, BT with
   per-leaf strengths vs one anchor-level strength; LRT = 2(ll_leaf - ll_anchor); same question-level
   permutation null. Also the median verdicts per (leaf, model) — the power the arena actually has.

REGISTERED (2026-09-10, before running): A is REAL iff the pooled question-permutation p < 0.05 AND
at least half of the anchors are individually p < 0.05; B is RESOLVED iff the pooled p < 0.05.
Prediction: A REAL (the key has 46 x ~10.9k observations); B NOT resolved at R2's volume (leaf-level
BT overfits: M1) — i.e. the profile exists and the arena is under-powered for it, not wrong.

  python tools/analysis/leaf_profile_evidence.py [--perms 200]
"""
import os, sys, math, random, sqlite3, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import free_tests_f4_f7 as ff
import profile_atlas as pa

RUN_DIR = "experiment_results/promoted/bareq512_s42/seed_42"
R2_DB = os.path.join(ROOT, "experiment_results", "x12_profile", "ratings_x12p.db")
MIN_LEAF_Q = 30


def assign_leaves():
    models, G, cat, text, qs_all = ff.keyed_questions()
    leaves = ff.tree_leaves(RUN_DIR); dim = len(leaves[0][1])
    vec = ff.embed_matrix(ff.EMB_DB, list(text.values()), dim)
    qs = [q for q in qs_all if text[q] in vec]
    Q = np.stack([vec[text[q]] for q in qs]); M = np.stack([mu / (np.linalg.norm(mu) or 1) for _, mu, _ in leaves])
    idx = np.argmax(Q @ M.T, axis=1)
    leaf = {q: leaves[i][0] for q, i in zip(qs, idx)}; anc = {q: leaves[i][2] for q, i in zip(qs, idx)}
    return models, G, qs, leaf, anc


def irls_additive(y, mi, li, M, L, iters=25):
    """Logistic y ~ model + leaf (dummy-coded, leaf 0 as baseline). Returns log-likelihood."""
    n = len(y); X = np.zeros((n, M + L - 1)); X[np.arange(n), mi] = 1.0
    mask = li > 0; X[np.arange(n)[mask], M + li[mask] - 1] = 1.0
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        eta = X @ beta; p = 1 / (1 + np.exp(-eta)); w = p * (1 - p) + 1e-9
        z = eta + (y - p) / w
        XtW = X.T * w
        beta_new = np.linalg.solve(XtW @ X + 1e-8 * np.eye(X.shape[1]), XtW @ z)
        if np.max(np.abs(beta_new - beta)) < 1e-8: beta = beta_new; break
        beta = beta_new
    p = np.clip(1 / (1 + np.exp(-(X @ beta))), 1e-12, 1 - 1e-12)
    return float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))


def ll_saturated(y, mi, li, M, L):
    s = np.zeros((M, L)); c = np.zeros((M, L))
    np.add.at(s, (mi, li), y); np.add.at(c, (mi, li), 1)
    p = np.clip(np.where(c > 0, s / np.maximum(c, 1), 0.5), 1e-12, 1 - 1e-12)
    return float(np.sum(s * np.log(p) + (c - s) * np.log(1 - p)))


def key_test(perms, rng):
    models, G, qs, leaf, anc = assign_leaves()
    print("== A) KEY: model x leaf interaction within anchors (46 models, %d questions, tree bareq512_s42) ==" % len(qs))
    by_anchor = defaultdict(list)
    for q in qs: by_anchor[anc[q]].append(q)
    pooled_obs = 0.0; pooled_null = np.zeros(perms); n_sig = n_anc = 0
    mi_of = {m: i for i, m in enumerate(models)}
    for a in sorted(by_anchor):
        aq = by_anchor[a]
        cnt = Counter(leaf[q] for q in aq); keep = {l for l, k in cnt.items() if k >= MIN_LEAF_Q}
        aq = [q for q in aq if leaf[q] in keep]
        if len(keep) < 2: print("  %-18s %d leaves >= %d questions: skipped" % (a, len(keep), MIN_LEAF_Q)); continue
        lidx = {l: i for i, l in enumerate(sorted(keep))}; L = len(lidx); M = len(models)
        y = np.array([G[m][q] for q in aq for m in models], dtype=float)
        mi = np.array([mi_of[m] for q in aq for m in models]); qleaf = np.array([lidx[leaf[q]] for q in aq])
        li = np.repeat(qleaf, M)
        obs = 2 * (ll_saturated(y, mi, li, M, L) - irls_additive(y, mi, li, M, L))
        null = np.empty(perms)
        for k in range(perms):
            perm = qleaf.copy(); rng.shuffle(perm); lp = np.repeat(perm, M)
            null[k] = 2 * (ll_saturated(y, mi, lp, M, L) - irls_additive(y, mi, lp, M, L))
        p = (1 + np.sum(null >= obs)) / (1 + perms)
        # F2-style LOO Brier gain of leaf over anchor partition on this anchor's questions
        il = ff.loo_imp({q: leaf[q] for q in aq}, aq, models, G); ia = ff.loo_imp({q: a for q in aq}, aq, models, G)
        gain = 1000 * (il.mean() - ia.mean())
        n_anc += 1; n_sig += p < 0.05; pooled_obs += obs; pooled_null += null
        print("  %-18s leaves %2d  q=%4d  LRT %7.1f  null p95 %7.1f  p=%.3f %s | LOO Brier leaf-over-anchor %+.2f/1000"
              % (a[:18], L, len(aq), obs, np.percentile(null, 95), p, "*" if p < 0.05 else " ", gain))
    pp = (1 + np.sum(pooled_null >= pooled_obs)) / (1 + perms)
    print("  POOLED LRT %.1f vs null p95 %.1f, p=%.3f | anchors significant %d/%d -> A %s" % (pooled_obs, np.percentile(pooled_null, 95), pp, n_sig, n_anc, "REAL" if (pp < 0.05 and n_sig * 2 >= n_anc) else "NOT SHOWN"))


def judged_test(perms, rng):
    nodes = rj.load_nodes(); parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}
    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1: n = nodes[parent[n["id"]]]
        return n["label"]
    c = sqlite3.connect("file:%s?mode=ro" % R2_DB, uri=True)
    rows = c.execute("SELECT model_a, model_b, winner, is_tie, node_id, eval_question_id FROM match_history WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,)).fetchall()
    models = sorted({r[0] for r in rows} | {r[1] for r in rows})
    print("\n== B) JUDGED: R2 atlas verdicts (%d, %d models), per-leaf vs anchor-level BT within anchors (frozen tree, R2's own routing) ==" % (len(rows), len(models)))
    by_anchor = defaultdict(list)
    for r in rows: by_anchor[anchor(r[4])].append(r)
    def agg_of(rs):
        agg = defaultdict(lambda: [0.0, 0.0])
        for a, b, w, tie, *_ in rs:
            key = (a, b) if a < b else (b, a); wa = 0.5 if tie else (1.0 if w == key[0] else 0.0)
            agg[key][0] += wa; agg[key][1] += 1
        return {k: (v[0], v[1]) for k, v in agg.items()}
    def lrt(rs, leaf_of_q):
        agg_all = agg_of(rs); th = pa.mm_fit(agg_all, models); ll_a = pa.ll_of(agg_all, th)
        by_leaf = defaultdict(list)
        for r in rs: by_leaf[leaf_of_q[r[5]]].append(r)
        ll_l = 0.0
        for l, lr in by_leaf.items():
            ag = agg_of(lr); ll_l += pa.ll_of(ag, pa.mm_fit(ag, models))
        return 2 * (ll_l - ll_a)
    pooled_obs = 0.0; pooled_null = np.zeros(perms); cells = []
    for a in sorted(by_anchor):
        rs = by_anchor[a]
        leaf_of_q = {}
        for r in rs: leaf_of_q[r[5]] = r[4]
        leaves = Counter(leaf_of_q.values())
        if len(leaves) < 2: print("  %-18s one leaf: skipped" % a); continue
        per_cell = Counter((r[4], m) for r in rs for m in (r[0], r[1])); cells += list(per_cell.values())
        obs = lrt(rs, leaf_of_q)
        qids = list(leaf_of_q); labels = [leaf_of_q[q] for q in qids]
        null = np.empty(perms)
        for k in range(perms):
            rng.shuffle(labels); null[k] = lrt(rs, dict(zip(qids, labels)))
        p = (1 + np.sum(null >= obs)) / (1 + perms)
        pooled_obs += obs; pooled_null += null
        print("  %-18s leaves %2d  verdicts %5d  questions %4d  LRT %7.1f  null p95 %7.1f  p=%.3f %s" % (a[:18], len(leaves), len(rs), len(qids), obs, np.percentile(null, 95), p, "*" if p < 0.05 else " "))
    pp = (1 + np.sum(pooled_null >= pooled_obs)) / (1 + perms)
    print("  POOLED LRT %.1f vs null p95 %.1f, p=%.3f -> B %s | verdicts per (leaf, model): median %d, p25 %d" % (pooled_obs, np.percentile(pooled_null, 95), pp, "RESOLVED" if pp < 0.05 else "NOT RESOLVED", int(np.median(cells)), int(np.percentile(cells, 25))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--perms", type=int, default=200); a = ap.parse_args()
    rng = random.Random(42); nrng = np.random.default_rng(42)
    key_test(a.perms, nrng)
    judged_test(a.perms, rng)
