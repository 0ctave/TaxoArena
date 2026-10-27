"""SITE-SUPPORT readout (docs/judge_v2_program.md, "## Registered 2026-10-04 (before any code or call) -- SITE-SUPPORT: do
site-certified splits recur across the four anchor-free MMLU-Pro re-draw trees more than uncertified ones ...", L24349-L24360,
registration commit 633255f2; docs/agents/results/SITE-SUPPORT.json). ZERO LLM calls; CPU only; labels never read.

POOL READER (rule 7): it reads the reserved_pool rows of p2dca21ab5f4ef3ae (pool_guard.assert_pool_of_record, printed FIRST),
pd610c9ad05255f16, p19d9f473b5a610a0 and p8a29d8f3ff75aa55 (rows hashed to their ids by pool_guard.assert_frozen_pool), and
--run also reads embeddings_cache.db (the descriptive k-means hierarchies). Run it in a pool slot, never inside a construction or
site-null window. Three of the four draws are id-disjoint only (scope word); no EVAL quantity is computed.

LAUNCH SEQUENCE (zero calls; temp only under E: via scratch_dir; every DB is COPIED (db + -wal) into the process's scratch dir
before it is read: zc_common.stage_db):
  python tools/analysis/site_support.py --selftest     # fixture worlds in a scratch dir; value-asserting; mutant table below
  python tools/analysis/site_support.py --mutants      # re-runs the mutant table (copies in a sandbox; the file is never edited)
  python tools/analysis/site_support.py --dry-run      # pool line first, pins, staged copies, |C|, site counts per stratum; no TBE
  python tools/analysis/site_support.py --run          # the readout of record; WRITE-ONCE outcome on E: (+ SHA256SUMS.txt)
      --out <path>        default E:/TaxoArena_backup_<date>_site_support/site_support_outcome.txt; REFUSES an existing path
      --data-root <dir>   where snapshots.db / mmlu_pro_dataset_cache_v2.db / embeddings_cache.db / the site-null CSVs live
                          (default: the checkout holding this script)

INPUTS (read-only; DBs through staged copies).
  * site nulls of record (blob-pinned in cert_align_size.ARMS, committed 17a44347): experiment_results/anchorfree/redraw/
    site_null_<tree>.csv: cert_site_p95 (the deciding flag), cert_deflated_p95 (SB1d), n, depth; 300 reps; the pinned snapshot.
    Read through cert_align_size.read_site_null (blob, reps, snapshot checks) and re-read for the deflated column.
  * snapshots.db: cert_align_size.load_graph (ONLY `SELECT graph FROM snapshots WHERE id = ?`): node member sets = union of the
    descendant leaves' queryIds (q_ ids = "q_" + sha256(text)[:16]).
  * mmlu_pro_dataset_cache_v2.db: reserved_pool (pool_id, question_id), eval_question_link (question_id, question_text) and
    mmlu_pro.question ONLY (the category column is never selected: labels never read).
  * embeddings_cache.db (--run, descriptive only): the first 256 coordinates (the trees' sliceDim), renormalised, of C's texts.

INSTRUMENT (registration, verbatim in the code).
  C = the common item set of the four trees, restricted to the items each tree holds on its TRAIN side (see BUILDER'S READING
  SS-R1); each site of record s of tree A gives S = members(s) & C, p = min(|S|, |C| - |S|); a site is SKIPPED if |S| < 20 or
  p < 20 (counts printed by reason). delta(s, B) = min over ALL nodes b of B of |S symmetric-difference (b & C)|;
  TBE(s) = mean over the three other trees of max(0, 1 - delta / (p - 1)); the binary Felsenstein support (share of the three
  trees with delta = 0) beside.
  Strata = depth {0-1, 2, 3, >= 4} x size quintile (CERT-ALIGN-SIZE's rule: cutpoints np.quantile(log n, .2/.4/.6/.8) over the
  POOLED surviving sites of the four trees, stratum = number of cutpoints strictly below log n; n = |S|, the size on C (SS-R2)).
  G = sum_h w_h (mean TBE|cert - mean TBE|uncert) / sum_h w_h, w_h = min(n_cert,h, n_uncert,h) (cert_align_size.stratified_gap).
  p = one-sided permutation p, 10,000 permutations of the certified flag WITHIN the strata, numpy RandomState(20261004),
  p = (1 + #{G_perm >= G - 1e-12}) / (1 + 10,000) (cert_align_size.perm_test).
  Random reference (SB2): for the i-th surviving site (trees in the order af_clean_s42, af_s137, af_s2048, af_s42_o1, nodes sorted
  by id), 200 random subsets of C of size |S| (numpy RandomState(20261004 + i), choice without replacement), each scored with
  the same TBE against the same three trees; the site's p97.5 = np.percentile(200 values, 97.5) (linear).

CRITERIA (registered; every branch printed and executed by the selftest).
  SB1 (DECIDING): NOT EVALUABLE iff fewer than 20 certified sites survive the restriction (Support (g)); else
      SUPPORT-TRACKS-CERT iff G > 0 AND p <= 0.05; NOT-SHOWN otherwise (a G that cannot be formed reads NOT-SHOWN, reason printed).
  SB2 (DECIDING): RECURS iff median real-site TBE > the median over sites of their random-subset p97.5; NOT-RECURS otherwise.
  F-SS fires iff SB1 reads NOT-SHOWN with G <= 0.
  P1 |C| in [1,500, 3,000]. P2 G in [0.00, 0.20]; SB1 SUPPORT-TRACKS-CERT at 0.45 (Brier). P3 SB2 RECURS at 0.80 (Brier).
  Bands HELD iff the point lies in the closed interval.
SUPPORT (registered (a)-(f) quoted, not re-derived): planning ~230 sites / ~50 certified, DEFF 1.3 a DECLARED PILOT ASSUMPTION,
  SE 0.0365, MDE80 0.091, verdict line DESCRIPTIVE-ONLY at the prediction (+0.08). The readout prints the realised counts first,
  then the realised SD of TBE, SE = SD x sqrt(1/n_cert + 1/n_uncert) x sqrt(1.3), n_eff = n / 1.3, MDE80 = 2.487 x SE and the
  measured within-stratum permutation SD of G beside the deciding statistic.
DESCRIPTIVE: SB1d (the deflated flag); the pool-TRAIN-side reading of C (SS-R1) with its own SB1 / SB2 words (NOT of record);
  the full-n size strata (SS-R2, NOT of record); normalised Robinson-Foulds and sampled triplet distances (10^5 triplets,
  RandomState(20261004)) between tree pairs, against spherical k-means hierarchies (k = the median leaf count of the four trees,
  seeds 0-4, intent_transfer_s0.skmeans, average-link on the centroids, cosine); the majority-rule (>= 3 of 4, exact clusters
  on C) consensus and its overlap with the certified trunks (certified sites at depth <= 1).

BUILDER'S READINGS (printed in the outcome; the registrar confirms or brackets BEFORE --run):
  SS-R1 "the intersection of the four TRAIN sides": C = the intersection of the four trees' member sets (each member verified on
        its pool's TRAIN side, refused otherwise). This is the record's own definition for these trees ("the SHARED TRAIN texts of
        the two trees (= the intersection of their member id sets)", anchor_free_redraw.py docstring (d)). The literal pool reading
        (distinct mmlu_pro texts outside each pool) is 301 items larger on the real data and turns every root into a {placed,
        unplaced} bipartition (p about 100, TBE 0): it is printed beside with its own SB1 / SB2 words, NOT of record.
  SS-R2 "CERT-ALIGN-SIZE's size quintiles": computed on n = |S| (the size on C, the size TBE depends on); the full-n strata
        (the CSV n) are printed beside, NOT of record.
  SS-R3 the random-subset site index i counts SURVIVING sites only, in the order stated above.
  SS-R4 the one-sided direction of the permutation p is "certified higher" (the literature file's "one-sided").

SELFTEST MUTANTS (2026-10-04; copies in a scratch sandbox via `--mutants`, the file never edited): the 24 mutants in MUTANTS below
(M1-M24: delta max<->min, self in the TBE mean, p = |S|, the wrong C, the skip rules, strata x tree, full-n strata, SB1 / SB2
boundaries, the NOT EVALUABLE threshold, p95 for p97.5, one random seed, the deflated flag, F-SS unprinted, write-once dropped,
pool side and pool hash unchecked, across-strata permutation, first-other-tree only, mean for median, the depth >= 4 boundary,
an open P2 band): 24 / 24 KILLED on this code (final run 2026-10-04, scratch_dir --run; kill sites in the commit message).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import csv
import datetime
import glob
import json
import math
import sqlite3
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import zc_common as ZC          # noqa: E402  (imports scratch_dir: temp on E:, removed at exit)
import scratch_dir              # noqa: E402
import cert_align_size as CA    # noqa: E402
import pool_guard as PG         # noqa: E402

import numpy as np              # noqa: E402

ROOT = ZC.ROOT
TAG = "[SITE-SUPPORT]"
REG = "docs/judge_v2_program.md L24349-L24360 (registration commit 633255f2)"
SEED = 20261004
PERM = 10_000
RAND = 200
TRIPLETS = 100_000
MIN_ITEMS = 20
MIN_CERT = 20
DEFF = 1.3
Z80 = 1.645 + 0.842
P1_BAND = (1500, 3000)
P2_BAND = (0.00, 0.20); P2_PROB = 0.45
P3_PROB = 0.80
PLAN = "planning ~230 sites / ~50 certified, between-site SD of TBE 0.20, DEFF 1.3 DECLARED PILOT ASSUMPTION, SE 0.0365, MDE80 0.091"
TREES = ["af_clean_s42", "af_s137", "af_s2048", "af_s42_o1"]
POOLS = {"af_clean_s42": "p2dca21ab5f4ef3ae", "af_s137": "pd610c9ad05255f16", "af_s2048": "p19d9f473b5a610a0",
         "af_s42_o1": "p8a29d8f3ff75aa55"}
POOL_OF_RECORD = "p2dca21ab5f4ef3ae"
SELFTEST_CHECKS = 57

MUTANTS = [
    ("M1", "delta = max over nodes instead of min", "    return float(np.min(d)) if d.size else float(n_s)\n", "    return float(np.max(d)) if d.size else float(n_s)\n"),
    ("M2", "TBE averaged over all four trees (self included)", "        others = [b for b in trees if b != a]\n", "        others = list(trees)\n"),
    ("M3", "p = |S| instead of min(|S|, |C| - |S|)", "        p = min(n_s, nC - n_s)\n", "        p = n_s\n"),
    ("M4", "C = intersection of the pool TRAIN sides (the reading beside) as the deciding C", "    C_dec = C_roots\n", "    C_dec = C_pool\n"),
    ("M5", "skip rule |S| <= 20 instead of < 20", "        if n_s < MIN_ITEMS:\n", "        if n_s <= MIN_ITEMS:\n"),
    ("M6", "smaller-side rule not applied", "        elif p < MIN_ITEMS:\n", "        elif False:\n"),
    ("M7", "strata crossed with tree instead of depth", "    return [(depth_stratum(s[\"depth\"]), s[\"size_h\"]) for s in sites]\n", "    return [(s[\"tree\"], s[\"size_h\"]) for s in sites]\n"),
    ("M8", "size quintiles on the CSV n instead of |S|", "    cuts = ZC.quantile_cuts([s[\"n_c\"] for s in sites])\n", "    cuts = ZC.quantile_cuts([s[\"n_full\"] for s in sites])\n"),
    ("M9", "SB1 uses G >= 0", "    return \"SUPPORT-TRACKS-CERT\" if bool(G > 0) and bool(p <= 0.05) else \"NOT-SHOWN\"\n", "    return \"SUPPORT-TRACKS-CERT\" if bool(G >= 0) and bool(p <= 0.05) else \"NOT-SHOWN\"\n"),
    ("M10", "SB1 uses p < 0.05", "    return \"SUPPORT-TRACKS-CERT\" if bool(G > 0) and bool(p <= 0.05) else \"NOT-SHOWN\"\n", "    return \"SUPPORT-TRACKS-CERT\" if bool(G > 0) and bool(p < 0.05) else \"NOT-SHOWN\"\n"),
    ("M11", "NOT EVALUABLE threshold dropped", "    if n_cert < MIN_CERT:\n", "    if False:\n"),
    ("M12", "SB2 uses >= instead of >", "    return \"RECURS\" if bool(med_real > med_p975) else \"NOT-RECURS\"\n", "    return \"RECURS\" if bool(med_real >= med_p975) else \"NOT-RECURS\"\n"),
    ("M13", "SB2 random p95 instead of p97.5", "            p975.append(float(np.percentile(vals, 97.5)))\n            s[", "            p975.append(float(np.percentile(vals, 95.0)))\n            s["),
    ("M14", "SB2 one seed for every site (not SEED + i)", "            rs = np.random.RandomState(SEED + i)\n            R = np.zeros", "            rs = np.random.RandomState(SEED)\n            R = np.zeros"),
    ("M15", "certified flag read from cert_deflated_p95", "            cert=null[\"rows\"][node][\"cert\"],\n", "            cert=defl[node],\n"),
    ("M16", "F-SS line not printed on the NOT-SHOWN branch", "        out.append(\"F-SS (fires iff SB1 NOT-SHOWN with G <= 0): \" + (\"FIRED", "        0 and out.append(\"F-SS (fires iff SB1 NOT-SHOWN with G <= 0): \" + (\"FIRED"),
    ("M17", "write-once dropped (pre-check and mode x both gone; an existing outcome overwritten)",
     "        if os.path.exists(p):\n            ZC.refuse(TAG, \"%s exists: the outcome of record is WRITE-ONCE (refused before any read)\" % p)\n    lines, _ = analyse(ctx)\n    text = \"\\n\".join(lines) + \"\\n\"\n    print(text, end=\"\")\n    ZC.write_once(out_path, text, TAG)\n",
     "        pass\n    lines, _ = analyse(ctx)\n    text = \"\\n\".join(lines) + \"\\n\"\n    print(text, end=\"\")\n    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)\n    open(out_path, \"w\", encoding=\"utf-8\").write(text)\n"),
    ("M18", "a tree member on its own pool side not refused", "    if bad:\n        ZC.refuse(TAG, \"%s: %d tree members", "    if False:\n        ZC.refuse(TAG, \"%s: %d tree members"),
    ("M19", "pool rows not hashed to their id", "        PG.assert_frozen_pool(con, pool)\n", "        pass\n"),
    ("M20", "permutation across all sites (not within strata)", "    p, perm_sd, _ = CA.perm_test(y, cert, keys, G, ctx.perm, SEED)\n", "    p, perm_sd, _ = CA.perm_test(y, cert, [0] * len(keys), G, ctx.perm, SEED)\n"),
    ("M21", "only the first other tree scored (first-site-only analogue)", "    deltas = [min_delta(s_vec, n_s, mats[b]) for b in others]\n", "    deltas = [min_delta(s_vec, n_s, mats[b]) for b in others[:1]]\n"),
    ("M22", "median real-site TBE replaced by the mean", "        med_real = float(np.median(y))\n", "        med_real = float(np.mean(y))\n"),
    ("M23", "depth stratum boundary: depth 4 in its own stratum", "    return \"0-1\" if d <= 1 else (str(d) if d <= 3 else \">=4\")\n", "    return \"0-1\" if d <= 1 else (str(d) if d <= 4 else \">=4\")\n"),
    ("M24", "P2 band read as an open interval", "    p2 = ZC.in_band(G, P2_BAND)\n", "    p2 = bool(G is not None and P2_BAND[0] < G < P2_BAND[1])\n"),
]


# ----------------------------------------------------------------------------------------------- context
class Ctx(object):
    def __init__(self, data_root=ROOT, perm=PERM, rand=RAND, arms=None, pools=None, por=(POOL_OF_RECORD, None),
                 check_blobs=True, kmeans=True, triplets=TRIPLETS, km_k=None):
        self.data_root = data_root
        self.perm, self.rand, self.triplets = perm, rand, triplets
        self.arms = arms or {t: CA.ARMS[t] for t in TREES}
        self.pools = pools or dict(POOLS)
        self.por = por                     # (pool id of record, id file override or None = the registry's)
        self.check_blobs = check_blobs
        self.kmeans = kmeans
        self.km_k = km_k
        self.staged = {}
        self.stage_dir = None

    def path(self, rel):
        if rel in self.staged:
            return self.staged[rel]["path"]
        return os.path.join(self.data_root, rel)

    def stage(self, rel):
        if rel not in self.staged:
            if self.stage_dir is None:
                self.stage_dir = scratch_dir.mkdtemp(prefix="site_support_stage_")
            self.staged[rel] = ZC.stage_db(os.path.join(self.data_root, rel), self.stage_dir, TAG)
        return self.staged[rel]


# ----------------------------------------------------------------------------------------------- loaders
def pool_lines(ctx, out):
    """FIRST: the pool of record through pool_guard.assert_pool_of_record (on the staged copy), then each tree's pool rows hashed
    to its id. -> {tree: frozenset of TRAIN-side q_ ids (distinct mmlu_pro texts outside the pool)}."""
    mm = ctx.stage("mmlu_pro_dataset_cache_v2.db")
    pid, idf = ctx.por
    PG.assert_pool_of_record(pid, db=mm["path"], id_file=idf)
    out.append("POOL READER (rule 7): pool_guard.assert_pool_of_record(%s) OK on the staged copy of mmlu_pro_dataset_cache_v2.db "
               "(sha256 %s); the four trees' pools %s read (rows hashed to their ids); embeddings_cache.db read by --run "
               "(descriptive). Id-disjoint scope for af_s137 / af_s2048 / af_s42_o1; no EVAL quantity." % (
                   pid, mm["sha256"][:16], ", ".join("%s=%s" % (t, ctx.pools[t]) for t in ctx.arms)))
    con = ZC.open_ro(mm["path"], TAG)
    try:
        link = dict(con.execute("SELECT question_id, question_text FROM eval_question_link"))
        texts = sorted({t for (t,) in con.execute("SELECT question FROM mmlu_pro") if t is not None})
        train = {}
        for tree in ctx.arms:
            pool = ctx.pools[tree]
            PG.assert_frozen_pool(con, pool)
            ids = {q for v in PG.pool_rows(con, pool).values() for q in v}
            miss = sorted(q for q in ids if q not in link)
            if miss:
                ZC.refuse(TAG, "%s: %d pool ids of %s have no eval_question_link text (first %s)" % (tree, len(miss), pool, miss[:3]))
            ptexts = {link[q] for q in ids}
            tset = set(texts)
            stray = [t for t in ptexts if t not in tset]
            if stray:
                ZC.refuse(TAG, "%s: %d pool texts of %s are not mmlu_pro rows" % (tree, len(stray), pool))
            train[tree] = frozenset(CA.qid(t) for t in texts if t not in ptexts)
            out.append("  pool %s (%s): %d rows; TRAIN side = %d distinct mmlu_pro texts outside it" % (pool, tree, len(ids), len(train[tree])))
    finally:
        con.close()
    return train


def read_tree(ctx, tree, train_side):
    null = CA.read_site_null(ctx, tree)
    p = ctx.path(ctx.arms[tree]["csv"])
    defl = {}
    for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
        v = r["cert_deflated_p95"].strip().lower()
        if v not in ("true", "false"):
            ZC.refuse(TAG, "%s: cert_deflated_p95 %r at %s" % (tree, r["cert_deflated_p95"], r["node_id"]))
        defl[r["node_id"]] = (v == "true")
    g = CA.load_graph(ctx, ctx.arms[tree]["snap"])
    extra = sorted(set(null["rows"]) - set(g["sites"]))
    if extra:
        ZC.refuse(TAG, "%s: site-null rows for non-sites %s" % (tree, extra[:5]))
    for s, r in null["rows"].items():
        if r["n"] != len(g["mem"][s]) or r["depth"] != g["byid"][s].get("depth"):
            ZC.refuse(TAG, "%s: site %s n/depth %d/%d in the CSV != %d/%s in the graph" % (tree, s, r["n"], r["depth"], len(g["mem"][s]), g["byid"][s].get("depth")))
    root_mem = g["mem"][g["root"]]
    bad = sorted(root_mem - train_side)
    if bad:
        ZC.refuse(TAG, "%s: %d tree members are not on the TRAIN side of its pool %s (first %s): a split breach" % (tree, len(bad), ctx.pools[tree], bad[:3]))
    man = sorted(glob.glob(os.path.join(ctx.data_root, "experiment_results", "anchorfree", "redraw", tree, "seed_*", "diagnostics", "run_manifest.json")))
    if man:
        m = json.load(open(man[0], encoding="utf-8"))
        if m.get("reserved_pool_id") != ctx.pools[tree]:
            ZC.refuse(TAG, "%s: run_manifest reserved_pool_id %s != the pinned %s" % (tree, m.get("reserved_pool_id"), ctx.pools[tree]))
    leaves = sum(1 for n in g["byid"].values() if not (n.get("childIds") or []))
    return dict(tree=tree, null=null, defl=defl, g=g, root_mem=root_mem, manifest=bool(man), leaves=leaves)


def depth_stratum(d):
    return "0-1" if d <= 1 else (str(d) if d <= 3 else ">=4")


# ----------------------------------------------------------------------------------------------- core
def node_matrix(g, cidx, nC):
    ids = sorted(g["byid"])
    M = np.zeros((len(ids), nC), dtype=np.float64)
    for r, i in enumerate(ids):
        for q in g["mem"][i]:
            j = cidx.get(q)
            if j is not None:
                M[r, j] = 1.0
    return dict(ids=ids, M=M, size=M.sum(axis=1))


def min_delta(s_vec, n_s, mat):
    d = n_s + mat["size"] - 2.0 * (mat["M"] @ s_vec)
    return float(np.min(d)) if d.size else float(n_s)


def tbe_of(deltas, p):
    return float(np.mean([max(0.0, 1.0 - dl / (p - 1)) for dl in deltas]))


def size_keys(sites):
    cuts = ZC.quantile_cuts([s["n_c"] for s in sites])
    for s in sites:
        s["size_h"] = ZC.quantile_stratum(s["n_c"], cuts)
    return cuts


def strata_keys(sites):
    return [(depth_stratum(s["depth"]), s["size_h"]) for s in sites]


def sb1_decide(n_cert, G, p):
    """SB1 (registered): NOT EVALUABLE iff < 20 certified sites survive; else SUPPORT-TRACKS-CERT iff G > 0 AND p <= 0.05."""
    if n_cert < MIN_CERT:
        return "NOT EVALUABLE"
    if G is None or p is None:
        return "NOT-SHOWN"
    return "SUPPORT-TRACKS-CERT" if bool(G > 0) and bool(p <= 0.05) else "NOT-SHOWN"


def sb2_decide(med_real, med_p975):
    """SB2 (registered): RECURS iff median real-site TBE > median random-subset p97.5."""
    if med_real is None or med_p975 is None:
        return "NOT-RECURS"
    return "RECURS" if bool(med_real > med_p975) else "NOT-RECURS"


def core(ctx, T, C_list, flag="cert", with_random=True):
    """Sites on C, TBE, strata, G, p, SB2. T: tree -> read_tree dict. Pure function of its inputs."""
    nC = len(C_list)
    cidx = {q: j for j, q in enumerate(C_list)}
    trees = list(T)
    mats = {t: node_matrix(T[t]["g"], cidx, nC) for t in trees}
    sites, skipped = [], Counter()
    for a in trees:
        others = [b for b in trees if b != a]
        null, defl, g = T[a]["null"], T[a]["defl"], T[a]["g"]
        for node in sorted(null["rows"]):
            S = [cidx[q] for q in g["mem"][node] if q in cidx]
            n_s = len(S)
            p = min(n_s, nC - n_s)
            if n_s < MIN_ITEMS:
                skipped["fewer than 20 items in C"] += 1
                continue
            elif p < MIN_ITEMS:
                skipped["smaller side < 20"] += 1
                continue
            s_vec = np.zeros(nC); s_vec[S] = 1.0
            sites.append(dict(tree=a, node=node, depth=null["rows"][node]["depth"], n_full=null["rows"][node]["n"], n_c=n_s, p=p,
                              cert=null["rows"][node]["cert"],
                              defl=defl[node], s_idx=S, others=others))
    for s in sites:
        s_vec = np.zeros(nC); s_vec[s["s_idx"]] = 1.0
        others, n_s = s["others"], s["n_c"]
        deltas = [min_delta(s_vec, n_s, mats[b]) for b in others]
        s["deltas"] = deltas
        s["tbe"] = tbe_of(deltas, s["p"])
        s["fbp"] = float(np.mean([1.0 if dl == 0 else 0.0 for dl in deltas]))
    res = dict(nC=nC, sites=sites, skipped=skipped, mats=mats)
    if not sites:
        res.update(G=None, p=None, perm_sd=None, strata={}, n_cert=0, n_uncert=0, med_real=None, med_p975=None, p975=[], cuts=[])
        return res
    res["cuts"] = size_keys(sites)
    keys = strata_keys(sites)
    y = [s["tbe"] for s in sites]
    cert = [bool(s[flag]) for s in sites]
    G, strata = CA.stratified_gap(y, cert, keys)
    p, perm_sd, _ = CA.perm_test(y, cert, keys, G, ctx.perm, SEED)
    res.update(G=G, p=p, perm_sd=perm_sd, strata=strata, n_cert=sum(cert), n_uncert=len(cert) - sum(cert), keys=keys, y=y)
    if with_random:
        p975 = []
        for i, s in enumerate(sites):
            rs = np.random.RandomState(SEED + i)
            R = np.zeros((ctx.rand, nC))
            for r in range(ctx.rand):
                R[r, rs.choice(nC, s["n_c"], replace=False)] = 1.0
            dl = np.stack([np.min(s["n_c"] + mats[b]["size"][None, :] - 2.0 * (R @ mats[b]["M"].T), axis=1) for b in s["others"]])
            vals = np.mean(np.maximum(0.0, 1.0 - dl / (s["p"] - 1)), axis=0)
            p975.append(float(np.percentile(vals, 97.5)))
            s["p975"] = p975[-1]
        med_real = float(np.median(y))
        med_p975 = float(np.median(p975))
        res.update(p975=p975, med_real=med_real, med_p975=med_p975)
    return res


def fmt(x, nd=4):
    return "n/a" if x is None else ("%+.*f" % (nd, x))


def block_lines(r, out, label):
    sites = r["sites"]
    out.append("  [%s] |C| = %d; surviving sites %d (%d certified, %d uncertified); skipped %s"
               % (label, r["nC"], len(sites), r["n_cert"], r["n_uncert"], dict(sorted(r["skipped"].items())) or "{}"))
    if not sites:
        return
    cnt = Counter((k, s["cert"]) for k, s in zip(r["keys"], sites))
    ks = sorted({k for k in r["keys"]}, key=str)
    out.append("  [%s] COUNTS (printed before any TBE): certified/uncertified per depth x size stratum (size cutpoints on log |S|: n = %s): %s"
               % (label, ", ".join("%.1f" % math.exp(c) for c in r["cuts"]),
                  "; ".join("%s:q%d %d/%d" % (k[0], k[1], cnt[(k, True)], cnt[(k, False)]) for k in ks)))
    dropped = sum(1 for v in r["strata"].values() if v["w"] == 0)
    out.append("  [%s] mean TBE certified %s, uncertified %s; strata with both classes %d, dropped %d; per stratum c/u gap w: %s"
               % (label, fmt(float(np.mean([s["tbe"] for s in sites if s["cert"]])) if r["n_cert"] else None),
                  fmt(float(np.mean([s["tbe"] for s in sites if not s["cert"]])) if r["n_uncert"] else None),
                  len(r["strata"]) - dropped, dropped,
                  "; ".join("%s:q%d %d/%d %s w%d" % (k[0], k[1], v["n_cert"], v["n_uncert"], fmt(v["gap"]) if v["gap"] is not None else "-", v["w"])
                            for k, v in sorted(r["strata"].items(), key=lambda kv: str(kv[0])))))
    out.append("  [%s] G (depth x size stratified, w = min) = %s; one-sided permutation p (%d within-stratum permutations, seed %d, (1+ge)/(1+N)) = %s; permutation SD of G %s"
               % (label, fmt(r["G"]), r.get("perm_n", 0), SEED, "n/a" if r["p"] is None else "%.4f" % r["p"], fmt(r["perm_sd"])))
    if r.get("p975"):
        out.append("  [%s] SB2 inputs: median real-site TBE %.4f; median over sites of the random-subset p97.5 %.4f (%d subsets per site); sites above their own p97.5: %d of %d"
                   % (label, r["med_real"], r["med_p975"], r.get("rand_n", 0), sum(1 for s in sites if s["tbe"] > s["p975"]), len(sites)))


# ----------------------------------------------------------------------------------------------- descriptive
def clusters_on(g, Cset):
    out = set()
    for i in g["byid"]:
        c = frozenset(g["mem"][i] & Cset)
        if 2 <= len(c) < len(Cset):
            out.add(c)
    return out


def nrf(A, B):
    return (len(A ^ B) / float(len(A) + len(B))) if (A or B) else 0.0


def triplet_topo(cl_list, idx, trip):
    """topology per triplet: 0 = ab|c, 1 = ac|b, 2 = bc|a, 3 = unresolved (no pair or more than one pair resolved)."""
    if not cl_list:
        return np.full(trip.shape[0], 3)
    M = np.zeros((len(cl_list), len(idx)), dtype=bool)
    for r, c in enumerate(cl_list):
        for q in c:
            M[r, idx[q]] = True
    a, b, c = M[:, trip[:, 0]], M[:, trip[:, 1]], M[:, trip[:, 2]]
    ab = np.any(a & b & ~c, axis=0); ac = np.any(a & c & ~b, axis=0); bc = np.any(b & c & ~a, axis=0)
    cnt = ab.astype(int) + ac.astype(int) + bc.astype(int)
    return np.where(cnt != 1, 3, np.where(ab, 0, np.where(ac, 1, 2)))


def kmeans_hierarchies(ctx, Cv, X, k, seeds=(0, 1, 2, 3, 4)):
    import intent_transfer_s0 as ITS
    from scipy.cluster.hierarchy import linkage
    out = []
    for sd in seeds:
        Cn = ITS.skmeans(X, k, sd)
        lab = np.argmax(X @ Cn.T, axis=1)
        used = sorted(set(lab.tolist()))
        groups = [frozenset(Cv[j] for j in np.nonzero(lab == u)[0]) for u in used]
        cl = set(g for g in groups if 2 <= len(g) < len(Cv))
        if len(used) > 1:
            Z = linkage(Cn[used], method="average", metric="cosine")
            members = list(groups)
            for row in Z:
                m = members[int(row[0])] | members[int(row[1])]
                members.append(m)
                if 2 <= len(m) < len(Cv):
                    cl.add(m)
        out.append(cl)
    return out


def descriptive_lines(ctx, T, C_list, r, out):
    Cset = frozenset(C_list)
    trees = list(T)
    cl = {t: clusters_on(T[t]["g"], Cset) for t in trees}
    pairs = [(a, b) for i, a in enumerate(trees) for b in trees[i + 1:]]
    rs = np.random.RandomState(SEED)
    idx = {q: j for j, q in enumerate(C_list)}
    n = len(C_list)
    trip = np.array([rs.choice(n, 3, replace=False) for _ in range(ctx.triplets)]) if n >= 3 else np.zeros((0, 3), dtype=int)
    topo = {t: triplet_topo(sorted(cl[t], key=lambda c: sorted(c)), idx, trip) for t in trees}
    out.append("DESCRIPTIVE tree pairs on C (normalised RF over exact clusters; triplet distance over %d sampled triplets): %s"
               % (len(trip), "; ".join("%s~%s nRF %.4f trip %.4f" % (a, b, nrf(cl[a], cl[b]), float(np.mean(topo[a] != topo[b]))) for a, b in pairs)))
    cnt = Counter(c for t in trees for c in cl[t])
    cons = {c for c, m in cnt.items() if m >= 3}
    trunks = {frozenset(T[t]["g"]["mem"][s] & Cset) for t in trees for s, row in T[t]["null"]["rows"].items() if row["cert"] and row["depth"] <= 1}
    trunks = {c for c in trunks if c}
    out.append("DESCRIPTIVE majority-rule consensus (exact clusters on C in >= 3 of 4 trees): %d clusters; %d of them equal a certified trunk (certified site at depth <= 1); %d of %d distinct certified trunk sets are in the consensus"
               % (len(cons), len(cons & trunks), len(trunks & cons), len(trunks)))
    if not ctx.kmeans:
        out.append("DESCRIPTIVE k-means hierarchies: not computed (kmeans off)")
        return
    emb = ctx.stage("embeddings_cache.db")
    texts = text_of_qid(ctx, set(C_list))
    vec = CA.load_vectors(ctx, [texts[q] for q in C_list if q in texts])
    dim = len(T[trees[0]]["g"]["byid"][T[trees[0]]["g"]["root"]].get("vmfMu") or []) or 256
    Cv = [q for q in C_list if q in texts and texts[q] in vec]
    X = np.array([vec[texts[q]][:dim] for q in Cv], dtype=np.float64)
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    k = ctx.km_k or int(round(float(np.median([T[t]["leaves"] for t in trees]))))
    km = kmeans_hierarchies(ctx, Cv, X, k)
    Cvs = frozenset(Cv)
    clv = {t: {frozenset(c & Cvs) for c in cl[t] if 2 <= len(c & Cvs) < len(Cvs)} for t in trees}
    idxv = {q: j for j, q in enumerate(Cv)}
    tv = np.array([rs.choice(len(Cv), 3, replace=False) for _ in range(ctx.triplets)]) if len(Cv) >= 3 else np.zeros((0, 3), dtype=int)
    tt = {t: triplet_topo(sorted(clv[t], key=lambda c: sorted(c)), idxv, tv) for t in trees}
    kt = [triplet_topo(sorted(c, key=lambda c: sorted(c)), idxv, tv) for c in km]
    tr_rf = [nrf(clv[a], clv[b]) for a, b in pairs]
    tr_tp = [float(np.mean(tt[a] != tt[b])) for a, b in pairs]
    kp = [(i, j) for i in range(len(km)) for j in range(i + 1, len(km))]
    km_rf = [nrf(km[i], km[j]) for i, j in kp]
    km_tp = [float(np.mean(kt[i] != kt[j])) for i, j in kp]
    out.append("DESCRIPTIVE vs spherical k-means hierarchies (embeddings_cache.db sha256 %s, first %d coordinates renormalised; %d of %d C items with a vector; k = %d = median leaf count; seeds 0-4; average-link cosine on the centroids): tree pairs mean nRF %.4f, mean triplet %.4f; k-means seed pairs mean nRF %.4f, mean triplet %.4f"
               % (emb["sha256"][:16], dim, len(Cv), len(C_list), k, float(np.mean(tr_rf)), float(np.mean(tr_tp)), float(np.mean(km_rf)), float(np.mean(km_tp))))


def text_of_qid(ctx, want):
    con = ZC.open_ro(ctx.stage("mmlu_pro_dataset_cache_v2.db")["path"], TAG)
    try:
        out = {}
        for (t,) in con.execute("SELECT question FROM mmlu_pro ORDER BY id"):
            if t is None:
                continue
            q = CA.qid(t)
            if q in want and q not in out:
                out[q] = t
        return out
    finally:
        con.close()


# ----------------------------------------------------------------------------------------------- modes
def header(ctx, out, mode):
    out.append("SITE-SUPPORT readout (%s); mode %s; %s; zc_common blob:%s; cert_align_size blob:%s; date %s; ZERO calls"
               % (REG, mode, ZC.pins_line(os.path.abspath(__file__)), ZC.git_blob(ZC.__file__.replace(".pyc", ".py")),
                  ZC.git_blob(CA.__file__.replace(".pyc", ".py")), datetime.date.today().isoformat()))


def load_all(ctx, out):
    train = pool_lines(ctx, out)
    snap = ctx.stage("snapshots.db")
    out.append("  staged copies (db + -wal copied, source untouched): %s" % "; ".join(
        "%s sha256 %s (%d bytes, -wal %d)" % (k, v["sha256"][:16], v["bytes"], v["wal_bytes"]) for k, v in sorted(ctx.staged.items())))
    T = {}
    for t in ctx.arms:
        T[t] = read_tree(ctx, t, train[t])
        nc = sum(1 for r in T[t]["null"]["rows"].values() if r["cert"])
        out.append("  tree %-14s csv blob:%s snapshot %s; sites of record %d (%d certified); members %d (all on the TRAIN side of %s); leaves %d; run_manifest %s"
                   % (t, T[t]["null"]["blob"], ctx.arms[t]["snap"], len(T[t]["null"]["rows"]), nc, len(T[t]["root_mem"]), ctx.pools[t],
                      T[t]["leaves"], "checked" if T[t]["manifest"] else "absent (pools pinned in code)"))
    C_roots = sorted(frozenset.intersection(*[T[t]["root_mem"] for t in T]))
    C_pool = sorted(frozenset.intersection(*[train[t] for t in T]))
    return T, C_roots, C_pool


def dry_run(ctx):
    out = []
    header(ctx, out, "--dry-run")
    T, C_roots, C_pool = load_all(ctx, out)
    out.append("DENOMINATOR: |C| = %d (SS-R1, of record: the intersection of the four trees' member sets); the pool-TRAIN-side reading %d (beside)"
               % (len(C_roots), len(C_pool)))
    r = core(ctx, T, C_roots, with_random=False)
    out.append("  [deciding] surviving sites %d (%d certified, %d uncertified); skipped %s" % (len(r["sites"]), r["n_cert"], r["n_uncert"], dict(r["skipped"])))
    if r["sites"]:
        cnt = Counter((k, s["cert"]) for k, s in zip(r["keys"], r["sites"]))
        out.append("  [deciding] COUNTS per depth x size stratum: %s" % "; ".join(
            "%s:q%d %d/%d" % (k[0], k[1], cnt[(k, True)], cnt[(k, False)]) for k in sorted({k for k in r["keys"]}, key=str)))
    out.append("--dry-run: no TBE printed, nothing written.")
    print("\n".join(out))
    return 0


def analyse(ctx):
    out = []
    header(ctx, out, "--run")
    T, C_roots, C_pool = load_all(ctx, out)
    C_dec = C_roots
    out.append("BUILDER'S READINGS (the registrar confirms or brackets): SS-R1 C = the intersection of the four trees' member sets (anchor_free_redraw (d)); SS-R2 size quintiles on |S|; SS-R3 random-subset index over surviving sites; SS-R4 one-sided, certified higher")
    r = core(ctx, T, C_dec)
    r["perm_n"], r["rand_n"] = ctx.perm, ctx.rand
    out.append("DECIDING (SB1, SB2): the four AF MMLU-Pro re-draw trees on C")
    block_lines(r, out, "deciding")
    # support (realised)
    y = [s["tbe"] for s in r["sites"]]
    nc, nu = r["n_cert"], r["n_uncert"]
    sd = float(np.std(y, ddof=1)) if len(y) > 1 else float("nan")
    se = sd * math.sqrt(1.0 / max(1, nc) + 1.0 / max(1, nu)) * math.sqrt(DEFF) if nc and nu else float("nan")
    mde = Z80 * se
    out.append("SUPPORT AS REALISED (registered (a)-(f) quoted, not re-derived: %s; verdict line DESCRIPTIVE-ONLY at the prediction): realised %d certified / %d uncertified surviving sites; realised between-site SD of TBE %.4f; SE = %.4f x sqrt(1/%d + 1/%d) x sqrt(1.3) = %.4f; n_eff = %d / 1.3 = %.0f; MDE80 one-sided = 2.487 x %.4f = %.4f; measured permutation SD of G %s; prediction +0.08 vs realised MDE80: %s"
               % (PLAN, nc, nu, sd, sd, nc, nu, se, nc + nu, (nc + nu) / DEFF, se, mde, fmt(r["perm_sd"]),
                  "beyond the MDE" if 0.08 > mde else "inside the MDE (DESCRIPTIVE-ONLY at the prediction)"))
    # descriptive beside
    rd = core(ctx, T, C_dec, flag="defl", with_random=False); rd["perm_n"] = ctx.perm
    out.append("DESCRIPTIVE SB1d (cert_deflated_p95 as the flag; same sites and strata): G %s, p %s, %d deflated-certified of %d"
               % (fmt(rd["G"]), "n/a" if rd["p"] is None else "%.4f" % rd["p"], rd["n_cert"], len(rd["sites"])))
    sites_f = [dict(s) for s in r["sites"]]
    cuts_f = ZC.quantile_cuts([s["n_full"] for s in sites_f])
    for s in sites_f:
        s["size_h"] = ZC.quantile_stratum(s["n_full"], cuts_f)
    Gf, _ = CA.stratified_gap([s["tbe"] for s in sites_f], [s["cert"] for s in sites_f], strata_keys(sites_f))
    out.append("DESCRIPTIVE SS-R2 alternative (size quintiles on the CSV n, NOT of record): G %s" % fmt(Gf))
    rp = core(ctx, T, C_pool)
    out.append("DESCRIPTIVE SS-R1 alternative (C = the intersection of the four pool TRAIN sides, NOT of record): |C| %d; %d sites (%d certified); G %s, p %s -> SB1 would read %s; median TBE %s vs median p97.5 %s -> SB2 would read %s"
               % (rp["nC"], len(rp["sites"]), rp["n_cert"], fmt(rp["G"]), "n/a" if rp["p"] is None else "%.4f" % rp["p"],
                  sb1_decide(rp["n_cert"], rp["G"], rp["p"]), fmt(rp["med_real"]), fmt(rp["med_p975"]), sb2_decide(rp["med_real"], rp["med_p975"])))
    descriptive_lines(ctx, T, C_dec, r, out)
    # criteria
    G, p = r["G"], r["p"]
    v1 = sb1_decide(nc, G, p)
    out.append("CRITERIA AND PREDICTIONS")
    if v1 == "NOT EVALUABLE":
        out.append("SB1 (DECIDING; SUPPORT-TRACKS-CERT iff G > 0 AND p <= 0.05; NOT EVALUABLE iff < 20 certified sites survive): NOT EVALUABLE -- %d certified sites survive the C restriction (< 20); G %s, p %s printed, not scored"
                   % (nc, fmt(G), "n/a" if p is None else "%.4f" % p))
        out.append("F-SS (fires iff SB1 NOT-SHOWN with G <= 0): NOT FIRED (SB1 NOT EVALUABLE)")
    elif v1 == "SUPPORT-TRACKS-CERT":
        out.append("SB1 (DECIDING; SUPPORT-TRACKS-CERT iff G > 0 AND p <= 0.05; NOT EVALUABLE iff < 20 certified sites survive): SUPPORT-TRACKS-CERT -- G %s, p %.4f (%d certified / %d uncertified sites)"
                   % (fmt(G), p, nc, nu))
        out.append("F-SS (fires iff SB1 NOT-SHOWN with G <= 0): NOT FIRED")
    else:
        why = ("G cannot be formed (no stratum holds both classes)" if G is None else
               "G %s <= 0" % fmt(G) if not bool(G > 0) else "p %.4f > 0.05" % p)
        out.append("SB1 (DECIDING; SUPPORT-TRACKS-CERT iff G > 0 AND p <= 0.05; NOT EVALUABLE iff < 20 certified sites survive): NOT-SHOWN -- %s (G %s, p %s; %d certified / %d uncertified sites)"
                   % (why, fmt(G), "n/a" if p is None else "%.4f" % p, nc, nu))
        fired = bool(G is not None and G <= 0)
        out.append("F-SS (fires iff SB1 NOT-SHOWN with G <= 0): " + ("FIRED -- 'certification marks reproducible structure' is not supported on these re-draws" if fired else "NOT FIRED (G > 0 or not formed; p > 0.05)"))
    v2 = sb2_decide(r.get("med_real"), r.get("med_p975"))
    out.append("SB2 (DECIDING; RECURS iff median real-site TBE > median random-subset p97.5): %s -- median TBE %s vs median p97.5 %s (%d sites, %d random subsets each)"
               % (v2, fmt(r.get("med_real")), fmt(r.get("med_p975")), len(r["sites"]), ctx.rand))
    p1 = ZC.in_band(r["nC"], P1_BAND)
    out.append("P1 |C| %d in [1500, 3000]: %s" % (r["nC"], "HELD" if p1 else "FAILED"))
    p2 = ZC.in_band(G, P2_BAND)
    out.append("P2 G %s in [0.00, 0.20]: %s; SB1 SUPPORT-TRACKS-CERT predicted at 0.45, occurred: %s, Brier %.4f"
               % (fmt(G), "HELD" if p2 else "FAILED", "yes" if v1 == "SUPPORT-TRACKS-CERT" else "no", ZC.brier(P2_PROB, v1 == "SUPPORT-TRACKS-CERT")))
    out.append("P3 SB2 RECURS predicted at 0.80, occurred: %s, Brier %.4f" % ("yes" if v2 == "RECURS" else "no", ZC.brier(P3_PROB, v2 == "RECURS")))
    out.append("WHAT THIS RESULT DOES NOT SHOW (registered): that recurring splits are correct (stability is not correctness); any EVAL quantity; content-closed re-draws (three are id-only); FDR-corrected certification.")
    return out, dict(sb1=v1, sb2=v2, r=r)


def run(ctx, out_path):
    sums = os.path.join(os.path.dirname(os.path.abspath(out_path)), "SHA256SUMS.txt")
    for p in (out_path, sums):
        if os.path.exists(p):
            ZC.refuse(TAG, "%s exists: the outcome of record is WRITE-ONCE (refused before any read)" % p)
    lines, _ = analyse(ctx)
    text = "\n".join(lines) + "\n"
    print(text, end="")
    ZC.write_once(out_path, text, TAG)
    print("%s wrote %s (write-once; never committed)" % (TAG, out_path.replace("\\", "/")))
    return 0


# ----------------------------------------------------------------------------------------------- selftest
def _world(root, trees, pools_items, universe, por_tree=0, emb=False):
    """Writes a fixture world under root. trees: [ {node_id: dict(depth, kids, items)} ] (root id n00000001), cert / defl maps
    inside each node dict ('cert', 'defl'); pools_items: [list of universe indices per tree]; universe: list of texts.
    -> Ctx (check_blobs False, kmeans False)."""
    os.makedirs(root, exist_ok=True)
    snap = sqlite3.connect(os.path.join(root, "snapshots.db"))
    snap.execute("CREATE TABLE snapshots (id TEXT, graph TEXT, reserved_queries TEXT)")
    mm = sqlite3.connect(os.path.join(root, "mmlu_pro_dataset_cache_v2.db"))
    mm.execute("CREATE TABLE mmlu_pro (id INTEGER PRIMARY KEY, question TEXT, category TEXT)")
    mm.execute("CREATE TABLE eval_question_link (question_id INTEGER PRIMARY KEY, question_text TEXT)")
    mm.execute("CREATE TABLE reserved_pool (pool_id TEXT NOT NULL, question_id INTEGER NOT NULL, domain TEXT NOT NULL, PRIMARY KEY (pool_id, question_id))")
    for j, t in enumerate(universe):
        mm.execute("INSERT INTO mmlu_pro VALUES (?,?,?)", (j + 1, t, "x"))
        mm.execute("INSERT INTO eval_question_link VALUES (?,?)", (100000 + j, t))
    arms, pools = {}, {}
    por = None
    for ti, spec in enumerate(trees):
        name = TREES[ti]
        ids = {"math": [100000 + j for j in pools_items[ti]]}
        pid = PG.compute_pool_id(ids)
        pools[name] = pid
        for q in ids["math"]:
            mm.execute("INSERT INTO reserved_pool VALUES (?,?,?)", (pid, q, "math"))
        if ti == por_tree:
            idf = os.path.join(root, "pool_%s.json" % pid)
            json.dump(ids, open(idf, "w", encoding="utf-8"))
            por = (pid, idf)
        nodes = []
        mem = {}

        def members(i):
            if i in mem:
                return mem[i]
            n = spec[i]
            m = set(CA.qid(universe[j]) for j in n.get("items", [])) if not n.get("kids") else set().union(*(members(k) for k in n["kids"]))
            mem[i] = m
            return m
        rows = []
        for i in sorted(spec):
            n = spec[i]
            nodes.append(dict(id=i, depth=n["depth"], childIds=list(n.get("kids", [])),
                              queryIds=[CA.qid(universe[j]) for j in n.get("items", [])], vmfMu=[1.0, 0.0, 0.0, 0.0]))
            if len(n.get("kids", [])) >= 2:
                c = bool(n.get("cert", False))
                rows.append([CA.ARMS[name]["snap"], i, "x", n["depth"], len(members(i)), len(n["kids"]), "true" if c else "false",
                             "true" if n.get("defl", not c) else "false", 300])
        snap.execute("INSERT INTO snapshots VALUES (?,?,?)", (CA.ARMS[name]["snap"], json.dumps(dict(rootId="n00000001", nodes=nodes)), "[]"))
        rel = "nulls/site_null_%s.csv" % name
        os.makedirs(os.path.join(root, "nulls"), exist_ok=True)
        with open(os.path.join(root, rel), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["snapshot_id", "node_id", "label", "depth", "n", "k", "cert_site_p95", "cert_deflated_p95", "reps"])
            w.writerows(rows)
        arms[name] = dict(CA.ARMS[name], csv=rel, blob=None)
    for c in (snap, mm):
        c.commit(); c.close()
    if emb:
        import struct
        e = sqlite3.connect(os.path.join(root, "embeddings_cache.db"))
        e.execute("CREATE TABLE embeddings (query TEXT, vector BLOB)")
        rv = np.random.RandomState(1)
        for t in universe:
            e.execute("INSERT INTO embeddings VALUES (?,?)", (t, struct.pack(">4f", *rv.standard_normal(4))))
        e.commit(); e.close()
    return Ctx(data_root=root, perm=2000, rand=50, arms=arms, pools=pools, por=por, check_blobs=False, kmeans=False, triplets=2000)


def _core_world(seed, n_trees=4, core=True, extra_uncert_tree=3, omit_tree0=(398, 399), small=True, flip=False, cert_core=True,
                only_ab_cert=False, n_extra=0):
    """F1 family: universe 460 docs; C = docs 0..399 (each tree's pool: 15 docs of 400..459). Core (shared): A = 0..199, B =
    200..399, A1/A2/B1/B2 halves (100), leaves of 50. Per tree random sites: X (200 of C, depth 1), Z (250, depth 1), YA (100 of A,
    depth 2), YB (100 of B, depth 2); tree 3 has one more uncertified YC (100 of A). Tree 0 omits docs 398, 399 (C stays 400:
    the pool reading; the deciding C = the intersection of member sets = 398) and carries the small sites W (20 items: kept),
    V (19: skipped) and L (385: smaller side 13: skipped). Each tree carries a leaf of the NEXT tree's pool docs (on its own TRAIN
    side, outside C). cert: core sites certified (flip: random sites certified, core not)."""
    rng = np.random.RandomState(seed)
    universe = ["doc %d" % j for j in range(860)]           # 460..859: 100 tree-private docs per tree (on every TRAIN side)
    pools = [list(range(400 + 15 * t, 415 + 15 * t)) for t in range(4)]
    trees = []
    for t in range(n_trees):
        placed = [j for j in range(400) if not (t == 0 and j in omit_tree0)]
        pset = set(placed)
        spec = {}
        nid = [1]

        def new():
            nid[0] += 1
            return "n%08d" % nid[0]

        def site(depth, items, cert, split=None):
            i = new(); a = new(); b = new()
            items = sorted(items)
            h = split if split is not None else len(items) // 2
            spec[a] = dict(depth=depth + 1, items=items[:h]); spec[b] = dict(depth=depth + 1, items=items[h:])
            spec[i] = dict(depth=depth, kids=[a, b], cert=cert)
            return i

        def cflag(is_core):
            c = (is_core and cert_core) if not flip else (not is_core)
            return bool(c)
        kids_root = []
        if core:
            A = [j for j in range(200) if j in pset]; B = [j for j in range(200, 400) if j in pset]
            a1 = site(2, [j for j in A if j < 100], cflag(True) and not only_ab_cert)
            a2 = site(2, [j for j in A if j >= 100], cflag(True) and not only_ab_cert)
            b1 = site(2, [j for j in B if j < 300], cflag(True) and not only_ab_cert)
            b2 = site(2, [j for j in B if j >= 300], cflag(True) and not only_ab_cert)
            ya = site(2, list(np.random.RandomState(99).choice(A, 100, replace=False)), cflag(False))   # the SAME subset in every tree: recurs (TBE 1) though uncertified (M8)
            priv = new()                                  # YA carries 100 tree-private docs: CSV n 200, n on C 100 (M8)
            spec[priv] = dict(depth=3, items=list(range(460 + 100 * t, 560 + 100 * t)))
            spec[ya]["kids"].append(priv)
            yb = site(2, list(rng.choice(B, 100, replace=False)), cflag(False))
            kA = [a1, a2, ya]; kB = [b1, b2, yb]
            if t == extra_uncert_tree:
                kA.append(site(2, list(rng.choice(A, 100, replace=False)), cflag(False)))
            iA = new(); iB = new()
            spec[iA] = dict(depth=1, kids=kA, cert=cflag(True)); spec[iB] = dict(depth=1, kids=kB, cert=cflag(True))
            kids_root += [iA, iB]
        kids_root.append(site(1, list(rng.choice(placed, 200, replace=False)), cflag(False)))
        kids_root.append(site(1, list(rng.choice(placed, 250, replace=False)), cflag(False)))
        for _ in range(n_extra):
            kids_root.append(site(1, list(rng.choice(placed, 100, replace=False)), cflag(False)))
        if not core:
            for _ in range(8):
                kids_root.append(site(1, list(rng.choice(placed, 100, replace=False)), False))
        if t == 0 and small:
            kids_root.append(site(1, list(range(0, 20)), False))
            kids_root.append(site(1, list(range(20, 39)), False))
            kids_root.append(site(1, [j for j in placed if j >= 13], False))
        leak = new()
        spec[leak] = dict(depth=1, items=pools[(t + 1) % 4][:10])
        kids_root.append(leak)
        spec["n00000001"] = dict(depth=0, kids=kids_root, cert=True)
        trees.append(spec)
    return trees, pools, universe


def _dense_world(seed):
    """F4 (SB2 values): universe 100 docs, C = 0..59 (pools 60..99, 10 per tree). Per tree 30 random sites of 25 items (two leaf
    children each) at depth 1, the first 6 certified: random-subset TBEs are spread (not all 0), so the p97.5 values, the
    per-site seeds and the median are value-tested."""
    rng = np.random.RandomState(seed)
    universe = ["doc %d" % j for j in range(100)]
    pools = [list(range(60 + 10 * t, 70 + 10 * t)) for t in range(4)]
    trees = []
    for t in range(4):
        spec = {}
        kids = []
        for s in range(30):
            i, a, b = "n%08d" % (3 * s + 2), "n%08d" % (3 * s + 3), "n%08d" % (3 * s + 4)
            items = sorted(rng.choice(60, 25, replace=False).tolist())
            spec[a] = dict(depth=2, items=items[:12]); spec[b] = dict(depth=2, items=items[12:])
            spec[i] = dict(depth=1, kids=[a, b], cert=(s < 6))
            kids.append(i)
        spec["n00000001"] = dict(depth=0, kids=kids, cert=False)
        trees.append(spec)
    return trees, pools, universe


def _ref(trees, pools, universe, nperm_check=False, rand=50):
    """An INDEPENDENT reference (pure Python sets) of C, the surviving sites, TBE, the strata, G and the SB2 medians."""
    qid = lambda j: CA.qid(universe[j])

    def mem(spec, i):
        n = spec[i]
        return set(qid(j) for j in n.get("items", [])) if not n.get("kids") else set().union(*(mem(spec, k) for k in n["kids"]))
    roots = [mem(sp, "n00000001") for sp in trees]
    C = sorted(set.intersection(*roots))
    Cs = set(C)
    nodes = [[mem(sp, i) & Cs for i in sorted(sp)] for sp in trees]
    sites = []
    for ti, sp in enumerate(trees):
        for i in sorted(sp):
            if len(sp[i].get("kids", [])) < 2:
                continue
            S = mem(sp, i) & Cs
            p = min(len(S), len(C) - len(S))
            if len(S) < 20 or p < 20:
                continue
            ds = []
            for tj in range(len(trees)):
                if tj == ti:
                    continue
                ds.append(min(len(S ^ b) for b in nodes[tj]))
            tbe = sum(max(0.0, 1 - d / (p - 1)) for d in ds) / len(ds)
            sites.append(dict(ti=ti, node=i, S=S, n=len(S), p=p, depth=sp[i]["depth"], cert=bool(sp[i].get("cert")), tbe=tbe, others=[tj for tj in range(len(trees)) if tj != ti]))
    logs = np.log([s["n"] for s in sites])
    cuts = np.quantile(logs, [0.2, 0.4, 0.6, 0.8])
    for s in sites:
        d = s["depth"]
        s["key"] = ("0-1" if d <= 1 else (str(d) if d <= 3 else ">=4"), int(sum(1 for c in cuts if c < math.log(s["n"]))))
    num = den = 0.0
    for k in set(s["key"] for s in sites):
        c = [s["tbe"] for s in sites if s["key"] == k and s["cert"]]
        u = [s["tbe"] for s in sites if s["key"] == k and not s["cert"]]
        w = min(len(c), len(u))
        if w:
            num += w * (sum(c) / len(c) - sum(u) / len(u)); den += w
    G = num / den if den else None
    # SB2
    Cidx = {q: j for j, q in enumerate(C)}
    p975 = []
    for i, s in enumerate(sites):
        rs = np.random.RandomState(SEED + i)
        vals = []
        for _ in range(rand):
            R = set(C[j] for j in rs.choice(len(C), s["n"], replace=False))
            ds = [min(len(R ^ b) for b in nodes[tj]) for tj in s["others"]]
            vals.append(sum(max(0.0, 1 - d / (s["p"] - 1)) for d in ds) / len(ds))
        p975.append(float(np.percentile(vals, 97.5)))
    return dict(C=C, sites=sites, G=G, med_real=float(np.median([s["tbe"] for s in sites])), med_p975=float(np.median(p975)), p975=p975,
                n_cert=sum(1 for s in sites if s["cert"]))


def selftest():
    checks = 0
    with scratch_dir.scratch("site_support_selftest") as tmp:
        # ---------------- F1: SUPPORT-TRACKS-CERT on the real --run entry point; values against the independent reference
        trees, pools, uni = _core_world(7)
        ctx = _world(os.path.join(tmp, "f1"), trees, pools, uni, emb=True)
        ctx.kmeans, ctx.km_k = True, 4
        ref = _ref(trees, pools, uni)
        outp = os.path.join(tmp, "f1_out", "o.txt")
        rc, txt = ZC.capture(main, ["--run", "--out", outp], ctx)
        assert rc == 0, txt[-3000:]; checks += 1
        assert txt.splitlines()[1].startswith("POOL READER (rule 7): pool_guard.assert_pool_of_record(%s) OK" % ctx.por[0]), txt.splitlines()[1]; checks += 1
        dl = ZC.line(txt, "  [deciding] |C| = ")
        assert dl.startswith("  [deciding] |C| = 398; surviving sites %d (%d certified, %d uncertified); skipped {'fewer than 20 items in C': 1, 'smaller side < 20': 5}"
                             % (len(ref["sites"]), ref["n_cert"], len(ref["sites"]) - ref["n_cert"])), (dl, len(ref["sites"]), ref["n_cert"]); checks += 1   # M3 M4 M5 M6
        G_line = ZC.line(txt, "  [deciding] G ")
        G_val = float(G_line.split("w = min) = ")[1].split(";")[0])
        assert abs(G_val - round(ref["G"], 4)) < 1e-9 and G_val > 0.5, (G_val, ref["G"]); checks += 1          # M1 M2 M7 M8 M21
        assert "= 0.0005;" in G_line and "2000 within-stratum permutations, seed 20261004" in G_line, G_line; checks += 1     # p = 1/2001 (M20 tested in F2b)
        sb1 = ZC.line(txt, "SB1 ")
        assert sb1.endswith("): SUPPORT-TRACKS-CERT -- G %+.4f, p 0.0005 (%d certified / %d uncertified sites)" % (ref["G"], ref["n_cert"], len(ref["sites"]) - ref["n_cert"])), sb1; checks += 1
        assert ZC.line(txt, "F-SS ") == "F-SS (fires iff SB1 NOT-SHOWN with G <= 0): NOT FIRED"; checks += 1
        sb2 = ZC.line(txt, "SB2 (DECIDING")
        assert sb2.startswith("SB2 (DECIDING; RECURS iff median real-site TBE > median random-subset p97.5): RECURS -- median TBE %+.4f vs median p97.5 %+.4f"
                              % (ref["med_real"], ref["med_p975"])), (sb2, ref["med_real"], ref["med_p975"]); checks += 1
        assert ZC.line(txt, "P1 ") == "P1 |C| 398 in [1500, 3000]: FAILED"; checks += 1
        assert ZC.line(txt, "P2 ") == "P2 G %+.4f in [0.00, 0.20]: FAILED; SB1 SUPPORT-TRACKS-CERT predicted at 0.45, occurred: yes, Brier 0.3025" % ref["G"], ZC.line(txt, "P2 "); checks += 1
        assert ZC.line(txt, "P3 ") == "P3 SB2 RECURS predicted at 0.80, occurred: yes, Brier 0.0400"; checks += 1
        km = ZC.line(txt, "DESCRIPTIVE vs spherical k-means")
        assert "398 of 398 C items with a vector; k = 4 = median leaf count" in km and "first 4 coordinates" in km, km; checks += 1
        trl = ZC.line(txt, "DESCRIPTIVE tree pairs on C")
        assert all(0.0 <= float(x.split(" ")[0]) <= 1.0 for x in trl.split("nRF ")[1:]) and trl.count("~") == 6, trl; checks += 1
        alt = ZC.line(txt, "DESCRIPTIVE SS-R1 alternative")
        assert "|C| 800;" in alt, alt; checks += 1
        sup = ZC.line(txt, "SUPPORT AS REALISED")
        assert "realised %d certified / %d uncertified surviving sites" % (ref["n_cert"], len(ref["sites"]) - ref["n_cert"]) in sup, sup; checks += 1
        # hand values, site B of tree 1 (200 docs 200..399): on the deciding C (docs 398, 399 not in tree 0, so not in C) it has 198
        # items and recurs exactly (TBE 1); on the pool reading (C = 400) tree 0's B misses 2 of its 200: TBE = (1 + 1 + (1 - 2/199)) / 3
        sB = [s for s in ref["sites"] if s["ti"] == 1 and s["n"] == 198 and s["depth"] == 1 and s["cert"]]
        assert len(sB) == 1 and sB[0]["tbe"] == 1.0, [s["tbe"] for s in sB]; checks += 1
        _out = []
        ctx2 = _world(os.path.join(tmp, "f1b"), trees, pools, uni)
        Tt, Cr, Cp = load_all(ctx2, _out)
        rp_ = core(ctx2, Tt, Cp, with_random=False)
        sBp = [s for s in rp_["sites"] if s["tree"] == "af_s137" and s["n_c"] == 200 and s["depth"] == 1 and s["cert"]]
        tb_ = sorted(s["tbe"] for s in sBp)                  # B only (A carries YA's 100 private docs on the pool C: 300)
        assert len(tb_) == 1 and abs(tb_[0] - (1 - 2.0 / (3 * 199))) < 1e-12, tb_; checks += 1
        r = core(ctx2, Tt, Cr)
        tb = {(s["tree"], s["node"]): s["tbe"] for s in r["sites"]}
        rf = {(TREES[s["ti"]], s["node"]): s["tbe"] for s in ref["sites"]}
        assert set(tb) == set(rf) and max(abs(tb[k] - rf[k]) for k in tb) < 1e-12; checks += 1                # every site's TBE
        assert len(Cr) == 398 and len(Cp) == 800; checks += 1
        assert [round(x, 12) for x in r["p975"]] == [round(x, 12) for x in ref["p975"]]; checks += 1
        # write-once (M17)
        body = open(outp, encoding="utf-8").read()
        assert body.splitlines()[-1].startswith("WHAT THIS RESULT DOES NOT SHOW") and ZC.line(body, "SB1 ") == sb1; checks += 1
        rc2, txt2 = ZC.capture(main, ["--run", "--out", outp], ctx)
        assert rc2 == ("refused", 2) and "WRITE-ONCE" in txt2 and open(outp, encoding="utf-8").read() == body; checks += 1
        rc2b, txt2b = ZC.capture(run, _world(os.path.join(tmp, "f1c"), trees, pools, uni), os.path.join(tmp, "f1c_out", "o.txt"))
        assert rc2b == 0; checks += 1
        # M17 direct: the write path itself refuses an existing file (not only the pre-check)
        rc2c, txt2c = ZC.capture(ZC.write_once, os.path.join(tmp, "f1c_out", "o.txt"), "x", TAG)
        assert rc2c == ("refused", 2); checks += 1
        # dry-run
        rc3, txt3 = ZC.capture(main, ["--dry-run"], _world(os.path.join(tmp, "f1d"), trees, pools, uni))
        assert rc3 == 0 and "DENOMINATOR: |C| = 398 (SS-R1" in txt3 and "the pool-TRAIN-side reading 800" in txt3, txt3[-2000:]; checks += 1
        assert "TBE" not in ZC.line(txt3, "  [deciding] surviving") and txt3.rstrip().endswith("--dry-run: no TBE printed, nothing written."); checks += 1
        assert txt3.splitlines()[1].startswith("POOL READER (rule 7)"); checks += 1

        # ---------------- F2: flags flipped -> NOT-SHOWN with G <= 0, F-SS FIRED (M16), P2 FAILED
        trees2, pools2, uni2 = _core_world(7, flip=True, n_extra=1)
        ref2 = _ref(trees2, pools2, uni2)
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "f2_out", "o.txt")], _world(os.path.join(tmp, "f2"), trees2, pools2, uni2))
        assert rc == 0, txt[-2000:]; checks += 1
        assert "): NOT-SHOWN -- G %+.4f <= 0 (G %+.4f, p 1.0000;" % (ref2["G"], ref2["G"]) in ZC.line(txt, "SB1 "), (ZC.line(txt, "SB1 "), ref2["G"]); checks += 1
        assert ZC.line(txt, "F-SS ").startswith("F-SS (fires iff SB1 NOT-SHOWN with G <= 0): FIRED -- 'certification marks reproducible structure'"); checks += 1
        assert ZC.line(txt, "P2 ").startswith("P2 G %+.4f in [0.00, 0.20]: FAILED; SB1 SUPPORT-TRACKS-CERT predicted at 0.45, occurred: no, Brier 0.2025" % ref2["G"]); checks += 1

        # ---------------- F2b: the within-stratum permutation (M20): a G of record whose within-stratum p differs from the pooled one
        trees2b, pools2b, uni2b = _core_world(11, only_ab_cert=True)
        ref2b = _ref(trees2b, pools2b, uni2b)
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "f2b_out", "o.txt")], _world(os.path.join(tmp, "f2b"), trees2b, pools2b, uni2b))
        assert rc == 0, txt[-2000:]; checks += 1
        assert ref2b["n_cert"] == 8 and ZC.line(txt, "SB1 ").startswith("SB1 (DECIDING; SUPPORT-TRACKS-CERT iff G > 0 AND p <= 0.05; NOT EVALUABLE iff < 20 certified sites survive): NOT EVALUABLE -- 8 certified sites survive"), ZC.line(txt, "SB1 "); checks += 1   # M11
        assert ZC.line(txt, "F-SS ") == "F-SS (fires iff SB1 NOT-SHOWN with G <= 0): NOT FIRED (SB1 NOT EVALUABLE)"; checks += 1
        gl = ZC.line(txt, "  [deciding] G ")
        p_within = float(gl.split("(1+ge)/(1+N)) = ")[1].split(";")[0])
        Tb = load_all(_world(os.path.join(tmp, "f2c"), trees2b, pools2b, uni2b), [])
        rb = core(Ctx(perm=2000), Tb[0], Tb[1], with_random=False)
        p_pooled, _, _ = CA.perm_test(rb["y"], [s["cert"] for s in rb["sites"]], [0] * len(rb["sites"]), rb["G"], 2000, SEED)
        assert abs(p_within - round(rb["p"], 4)) < 1e-9 and abs(round(p_pooled, 4) - p_within) > 1e-4, (p_within, p_pooled); checks += 1

        # ---------------- F3: no core structure -> NOT-RECURS (median real TBE 0 = median p97.5 0; strict >, M12)
        trees3, pools3, uni3 = _core_world(5, core=False, small=False, cert_core=False)
        for sp in trees3:
            for k, v in sp.items():
                if v.get("kids") and k != "n00000001":
                    v["cert"] = True
        ref3 = _ref(trees3, pools3, uni3)
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "f3_out", "o.txt")], _world(os.path.join(tmp, "f3"), trees3, pools3, uni3))
        assert rc == 0, txt[-2000:]; checks += 1
        assert ref3["med_real"] == ref3["med_p975"] == 0.0, (ref3["med_real"], ref3["med_p975"]); checks += 1
        assert ZC.line(txt, "SB2 (DECIDING").startswith("SB2 (DECIDING; RECURS iff median real-site TBE > median random-subset p97.5): NOT-RECURS -- median TBE +0.0000 vs median p97.5 +0.0000"); checks += 1
        assert ZC.line(txt, "P3 ") == "P3 SB2 RECURS predicted at 0.80, occurred: no, Brier 0.6400"; checks += 1
        assert "NOT-SHOWN -- G cannot be formed (no stratum holds both classes)" in ZC.line(txt, "SB1 ") and ZC.line(txt, "F-SS ").endswith("NOT FIRED (G > 0 or not formed; p > 0.05)"); checks += 1

        # ---------------- F4: dense world -> SB2 values (per-site p97.5, seeds SEED + i, the median) against the reference (M13 M14 M22)
        trees4, pools4, uni4 = _dense_world(3)
        ref4 = _ref(trees4, pools4, uni4)
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "f4_out", "o.txt")], _world(os.path.join(tmp, "f4"), trees4, pools4, uni4))
        assert rc == 0, txt[-2000:]; checks += 1
        assert len(set(round(x, 6) for x in ref4["p975"])) > 3 and ref4["med_p975"] > 0, ref4["p975"][:10]; checks += 1
        sb2 = ZC.line(txt, "SB2 (DECIDING")
        assert ("median TBE %+.4f vs median p97.5 %+.4f" % (ref4["med_real"], ref4["med_p975"])) in sb2, (sb2, ref4["med_real"], ref4["med_p975"]); checks += 1
        T4 = load_all(_world(os.path.join(tmp, "f4b"), trees4, pools4, uni4), [])
        r4 = core(Ctx(perm=10, rand=50), T4[0], T4[1])
        assert [round(x, 12) for x in r4["p975"]] == [round(x, 12) for x in ref4["p975"]]; checks += 1
        assert abs(float(np.mean([x["tbe"] for x in r4["sites"]])) - ref4["med_real"]) > 1e-3; checks += 1     # median and mean of real TBE differ here (M22)

        # ---------------- refusals: member on its own pool side (M18), pool hash (M19), deflated flag (M15), decide boundaries (M9 M10), depth strata (M23), P2 band (M24)
        trees5, pools5, uni5 = _core_world(7)
        trees5[1]["n%08d" % 900] = dict(depth=1, items=pools5[1][:3])
        trees5[1]["n00000001"]["kids"].append("n%08d" % 900)
        rc, txt = ZC.capture(main, ["--dry-run"], _world(os.path.join(tmp, "f5"), trees5, pools5, uni5))
        assert rc == ("refused", 2) and "af_s137: 3 tree members are not on the TRAIN side of its pool" in txt, txt[-800:]; checks += 1
        ctx6 = _world(os.path.join(tmp, "f6"), trees, pools, uni)
        con = sqlite3.connect(os.path.join(ctx6.data_root, "mmlu_pro_dataset_cache_v2.db"))
        con.execute("DELETE FROM reserved_pool WHERE pool_id = ? AND question_id = ?", (ctx6.pools["af_s2048"], 100000 + pools[2][0]))
        con.commit(); con.close()
        rc, txt = ZC.capture(main, ["--dry-run"], ctx6)
        assert isinstance(rc, tuple) and rc[0] == "exit" and ("reserved_pool rows for %s hash to" % ctx6.pools["af_s2048"]) in rc[1], (rc, txt[-800:]); checks += 1
        assert sb1_decide(20, 1e-9, 0.05) == "SUPPORT-TRACKS-CERT" and sb1_decide(20, 0.0, 0.001) == "NOT-SHOWN"; checks += 1
        assert sb1_decide(19, 0.5, 0.0001) == "NOT EVALUABLE" and sb1_decide(25, np.float64(0.1), np.float64(0.01)) == "SUPPORT-TRACKS-CERT"; checks += 1
        assert sb2_decide(0.5, 0.5) == "NOT-RECURS" and sb2_decide(np.float64(0.51), np.float64(0.5)) == "RECURS"; checks += 1
        assert [depth_stratum(d) for d in (0, 1, 2, 3, 4, 7)] == ["0-1", "0-1", "2", "3", ">=4", ">=4"]; checks += 1
        assert ZC.in_band(0.0, P2_BAND) and ZC.in_band(0.2, P2_BAND); checks += 1
        # the deflated column: flags opposite to cert in F1 -> SB1d G is the negative of a flipped analysis (M15 kills via F1's G)
        d1 = ZC.line(open(outp, encoding="utf-8").read(), "DESCRIPTIVE SB1d")
        assert "deflated-certified of" in d1 and float(d1.split("G ")[1].split(",")[0]) < 0; checks += 1
        # P2 at its closed bound and F-SS at G = 0 through the --run path: four IDENTICAL trees (tree 1 of a core world, its
        # leak leaf removed) -> every TBE is 1, both classes in the strata -> G = 0 exactly -> P2 HELD (M24), SB1 NOT-SHOWN,
        # F-SS FIRED (the "<= 0" boundary)
        import copy
        tw, pools7, uni7 = _core_world(9, small=False)
        base = copy.deepcopy(tw[1])
        leak = [k for k, v in base.items() if v.get("items") and 400 <= min(v["items"]) < 460]
        assert len(leak) == 1
        base["n00000001"]["kids"].remove(leak[0]); del base[leak[0]]
        trees7 = [copy.deepcopy(base) for _ in range(4)]
        ref7 = _ref(trees7, pools7, uni7)
        assert all(s["tbe"] == 1.0 for s in ref7["sites"]) and ref7["n_cert"] >= 20
        assert ref7["G"] == 0.0, ref7["G"]; checks += 1
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "f7_out", "o.txt")], _world(os.path.join(tmp, "f7"), trees7, pools7, uni7))
        assert rc == 0, txt[-1500:]; checks += 1
        assert ZC.line(txt, "P2 ").startswith("P2 G +0.0000 in [0.00, 0.20]: HELD"), ZC.line(txt, "P2 "); checks += 1
        assert ZC.line(txt, "F-SS ").startswith("F-SS (fires iff SB1 NOT-SHOWN with G <= 0): FIRED"), ZC.line(txt, "F-SS "); checks += 1
    assert checks == SELFTEST_CHECKS, "selftest ran %d checks, pinned %d" % (checks, SELFTEST_CHECKS)
    print("%s SELFTEST OK: %d value-asserting checks (pinned %d)" % (TAG, checks, SELFTEST_CHECKS))
    return 0


# ----------------------------------------------------------------------------------------------- main
def main(argv=None, ctx=None):
    ap = argparse.ArgumentParser(description="SITE-SUPPORT readout (zero calls; POOL READER)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--data-root", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        res = ZC.run_mutants(os.path.abspath(__file__), MUTANTS)
        return 0 if all(r[2] == "killed" for r in res) else 1
    if ctx is None:
        ctx = Ctx(data_root=os.path.abspath(a.data_root) if a.data_root else ROOT)
    if a.dry_run:
        return dry_run(ctx)
    return run(ctx, a.out or ZC.default_out("site_support", "site_support_outcome.txt"))


if __name__ == "__main__":
    sys.exit(main())
