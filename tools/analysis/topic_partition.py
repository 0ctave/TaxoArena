"""TOPIC-PARTITION-20NG readout (docs/judge_v2_program.md, "Registered 2026-09-22 (before any code or call) -
TOPIC-PARTITION-20NG", L10030-L10390, registration commit 6aa2a0d; instrument I6; criteria C0-C3; predictions
P1-P12; falsifiers F1-F3). ZERO LLM calls. A pool reader (rule 7): runs AFTER every build and null, never beside one.

  python tools/analysis/topic_partition.py --selftest                 # synthetic planted hierarchy in temp DBs
  python tools/analysis/topic_partition.py --dry-run --arm <arm>      # reads everything, prints the denominators,
                                                                      #   computes nothing long, writes nothing
  python tools/analysis/topic_partition.py --run                      # all arms; write-once outcome file
Arms: ng_af_s42 (T1, the arm of record for C1-C3), ng_af_bareq512_s42 (T1b, C3 beside; C1-C2 REPORTED),
ng_af_bar_eq_s42 (T2, contingency, only if T1 is NOT built: rows printed "bar re-tuned", never compared), smoke
(ag_news_smoke_s42; --dry-run only: "built / pool recorded / snapshot saved / trickle ran").

What it reads (all read-only): the arm's experiment_results/topic_partition/<arm>/seed_42/dag_snapshots.jsonl
(last snapshot: leaf vmfMu, sliceDim, iteration; anchor_free_readout.load_tree), diagnostics/proposals.csv
(anchor_free_redraw.refused_rows), the build log <arm>.build.out ("Snapshot ID:"), snapshots.db
mode=ro&immutable=1 (the SerializedGraph: nodes[].childIds / queryIds / vmfMu / dasguptaDeltaNorm; reserved_queries;
anchor_free_redraw.load_graph / members), site_null_<arm>.csv (anchor_free_redraw.read_site_null: refuses reps != 300
and mixed snapshot ids) and sitenull_<arm>.out ("[SEPBAR]" line), embeddings_cache.db mode=ro (vectors by TEXT,
big-endian float32, first <slice> coordinates re-normalised = the engine's geometry, DataModels.kt L193-199;
anchor_free_readout.full_vectors / sliced), and the INGEST DB mode=ro (twenty_newsgroups_cache_v1.db: label by
text; NEVER queries.ground_truth_category). Labels come ONLY from the ingest DB: leaf queryIds are
"q_" + sha256(utf-8 text)[:16] (anchor_free_redraw.qid) and join to the ingest rows by text; the held-out list is
the snapshot's reserved_queries -> namespaced id 8,000,000 + k -> k = rowid, the three tables' texts asserted equal.
The 7-group map is the fixed table GROUP_OF below.

Fail-closed (--run refuses): the outcome file exists; an arm's site null is partial (reps != 300 or mixed snapshot
ids) or its snapshot id is not the build's; a train or held-out vector is missing; a leaf's sliceDim != the arm's
slice; any held-out text is a member of any leaf; the CSV's sites are not the graph's split sites.
Instruments (registration I6, verbatim in the code): Q1 held-out partition quality of the tree's leaves vs k-means
(k = L, n_init 10, seeds 0-4; reference k = 20 and k = 7), Ward (k = L), sklearn HDBSCAN (min_cluster_size 55), the
random partition (the tree's held-out cells with labels permuted, 5 seeds) and k-means at k = L on the FULL 4096-d
vectors; assignment = argmax cosine to a cell centroid; purity with the majority-TRAIN label (score_cells) and the
optimistic held-out-majority row; NMI (sklearn arithmetic) and ARI at 20 labels and 7 groups; seed spread =
max - min over the 5 seeds; paired comparator k-means seed 0; 1,000 held-out bootstrap resamples with the partitions
FIXED, percentile CI on NMI(20)_tree - NMI(20)_kmeans0. Q2 per-site child-partition NMI_20 / NMI_7 / H_20 on the
site's TRAIN members (a doc under two children -> the child of higher cosine), depth-1 majority groups and the
7-group x depth-1 migration matrix (train and held-out), depth-d cuts, per-label / per-group best-Jaccard nodes,
per-leaf max Jaccard; certification vs alignment: raw gap, depth-stratified gap (strata 0-1 / 2 / 3 / 4 / >= 5,
weights min(n_cert, n_uncert)), OLS Y ~ cert + log n + depth with HC1 SE, one-sided permutation p over 1,000
permutations of the certified flag WITHIN depth strata; sensitivity rows excluding leak documents and documents
> 8,000 chars. Q3 build / leaf count, root and depth-1 separations, p95 and margins beside R1's and K-SELECTION
R1''s values, certified share vs R1's 14 of 69 and by site-size band vs the four free draws' base rates,
depth-blocked leaves, iterations to stop, the deflated column as a diagnostic. Every number is printed with its
denominator; P1-P12 are scored HELD / FAILED / UNDETERMINED where the number is computed; C0-C3 print the registered
rule; the VERDICT RULE's sentences are printed ONLY under the registered conditions.
[INSERTED 2026-09-23 after the post-run review's defect D1 (docs/reviews/2026-09-23_topic_partition_post.md), nothing
above rewritten: every criterion verdict is normalised to True / False / None by tribool() AT THE POINT IT IS DECIDED
(`numpy.True_ is True` is False, so the 2026-09-23 run's C2 HELD sentence of record was never written into the
write-once outcome although the criterion line printed HELD), C2's VERDICT-RULE sentence is TOTAL over the three
verdicts (c2_sentence: HELD / FAILED / the UNDETERMINED no-contrast sentence of pre-run bracket (e)) and any other
value is a refusal, and the selftest count is pinned by SELFTEST_CHECKS (READY condition 12 / bracket (c)(12)).]
[INSERTED 2026-09-23 by TP20-C2-CONFORMANCE (queue item; registrar's ruling of 2026-09-23 adopting pre-run bracket
(e) as already-registered text, docs/judge_v2_program.md; nothing above rewritten): C2 is decided in c2_decide(),
which evaluates the FOUR no-contrast conditions of bracket (e) -- (i) fewer than 2 certified sites, (ii) fewer than 2
uncertified sites, (iii) total depth-stratum weight sum(min(n_cert, n_uncert)) over {0-1, 2, 3, 4, >= 5} = 0,
(iv) a degenerate permutation distribution (fewer than 2 distinct values over the within-stratum permutations) --
BEFORE the registered verdict expression (ruling (a)); each condition prints its named reason with the count that
fired it (ruling (b)); F2 is recorded NOT FIRED on every UNDETERMINED path (ruling (c)); and on a draw WITH a
contrast every printed character is unchanged (the 2026-09-23 draw had all four conditions false: 16 certified /
85 uncertified, total weight 11, a non-degenerate distribution, so no recorded number moves -- ruling (d)).]
"""
import argparse
import csv
import datetime
import hashlib
import json
import math
import os
import re
import sqlite3
import struct
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
import time
from collections import Counter, defaultdict

import numpy as np

os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))   # sklearn/joblib core probe: silence the Windows wmic warning

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import anchor_free_readout as afo    # noqa: E402  load_tree, sliced, route, score_cells, full_vectors (reused, not modified)
import anchor_free_redraw as afr     # noqa: E402  qid, load_graph, members, read_site_null, refused_rows (reused, not modified)
from t3_routing_inflation import wilson  # noqa: E402

REPS = 300
BOOT = 1000
PERM = 1000
RNG_SEED = 20260922
MCS = 55
# The PINNED selftest count (READY condition 12 / pre-run bracket (c)(12)): a tripwire against the silent LOSS of
# a check. 32 at 634e969 (the launched instrument); raised here in the same commit as the D1 fix and the seven
# missing path assertions. Any edit that changes the number of checks must change this line in the same commit.
SELFTEST_CHECKS = 59
LEAK_LONG_CHARS = 8000
RES_DIR = os.path.join(ROOT, "experiment_results", "topic_partition")
OUTCOME = os.path.join(RES_DIR, "topic_partition_outcome.txt")

# The fixed 7-group map (registration CORPUS): comp (5) / rec (4) / sci (4) / talk (4) / soc.religion.christian /
# misc.forsale / alt.atheism.
GROUP_OF = {
    "comp.graphics": "comp", "comp.os.ms-windows.misc": "comp", "comp.sys.ibm.pc.hardware": "comp",
    "comp.sys.mac.hardware": "comp", "comp.windows.x": "comp",
    "rec.autos": "rec", "rec.motorcycles": "rec", "rec.sport.baseball": "rec", "rec.sport.hockey": "rec",
    "sci.crypt": "sci", "sci.electronics": "sci", "sci.med": "sci", "sci.space": "sci",
    "talk.politics.guns": "talk", "talk.politics.mideast": "talk", "talk.politics.misc": "talk", "talk.religion.misc": "talk",
    "soc.religion.christian": "soc.religion.christian", "misc.forsale": "misc.forsale", "alt.atheism": "alt.atheism",
}
LABELS_20 = sorted(GROUP_OF)
GROUPS_7 = sorted(set(GROUP_OF.values()))
RELIGION_TRIAD = ["alt.atheism", "soc.religion.christian", "talk.religion.misc"]
P8_TEN = ["rec.sport.hockey", "rec.sport.baseball", "sci.space", "sci.crypt", "sci.med", "rec.autos",
          "rec.motorcycles", "talk.politics.guns", "talk.politics.mideast", "misc.forsale"]

# The record's reference values (registration Q3 / (f)); read-only constants, checked by the registrar against the CSVs.
R1_ROOT = dict(observed=0.042461, p95=0.037214, margin=1.141, node="n00000001")
R1_DISCURSIVE = dict(observed=0.059496, p95=0.028375, margin=2.097, node="n00000005")
R1_QUANT = dict(observed=0.025148, p95=0.033733, margin=0.746, node="n00000004")
R1_ROOT_REFUSED_D1_MINPAIR = 0.01319            # R1 af_clean_s42 proposals.csv: n00000005 k=2 first refused row
KSEL_R1PRIME_N4 = dict(observed=0.056502, p95=0.033471, margin=1.688)
R1_CERT = (14, 69)                               # 20.3%; per-draw band 10-16 of 64-69
RECORD_BANDS = {"n<200": (3, 66), "200-400": (11, 103), "400-800": (14, 52), ">=800": (24, 47)}
ARM4_NULL = dict(arm="af_bareq512 (ANCHOR-FREE-CERT arm 4)", csv="experiment_results/anchorfree/site_null_af_bareq512_s42.csv",
                 slice=512, bar=0.025, leaves=92, sites=87, certified=10,
                 how="the harness hardcoded proposalSeparationBar = 0.025 (SeparationNullBySizeTest.kt canonicalConfig, no -DsepBar "
                     "existed on 2026-09-17; cert_arm4.log 'SITENULL start (dim 512 dropTop 0)'; sitenull_bareq512.out is empty under -q)")

ARMS = {
    "ng_af_s42": dict(kind="T1", dir="ng_af_s42", slice=256, bar=0.025, db="twenty_newsgroups_cache_v1.db",
                      table="twenty_newsgroups", offset=8_000_000, toml="experiment_configs/topic_partition/ng_af_s42.toml"),
    "ng_af_bareq512_s42": dict(kind="T1b", dir="ng_af_bareq512_s42", slice=512, bar=0.0145, db="twenty_newsgroups_cache_v1.db",
                               table="twenty_newsgroups", offset=8_000_000, toml="experiment_configs/topic_partition/ng_af_bareq512_s42.toml"),
    "ng_af_bar_eq_s42": dict(kind="T2", dir="ng_af_bar_eq_s42", slice=256, bar=None, db="twenty_newsgroups_cache_v1.db",
                             table="twenty_newsgroups", offset=8_000_000, toml="experiment_configs/topic_partition/ng_af_bar_eq_s42.toml"),
    "smoke": dict(kind="smoke", dir="ag_news_smoke_s42", slice=256, bar=0.025, db="ag_news_smoke_cache_v1.db",
                  table="ag_news", offset=9_000_000, toml="experiment_configs/topic_partition/ag_news_smoke_s42.toml"),
}


def rel(p):
    try:
        return os.path.relpath(p, ROOT).replace("\\", "/")
    except ValueError:
        return p.replace("\\", "/")


def die(msg, code=1):
    print("[TOPIC-PARTITION] REFUSED: " + msg)
    sys.exit(code)


def script_sha():
    with open(os.path.abspath(__file__), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()[:16]


def ro(path, immutable=False):
    if not os.path.exists(path):
        die("%s not found" % rel(path))
    return sqlite3.connect("file:%s?mode=ro%s" % (path.replace("\\", "/"), "&immutable=1" if immutable else ""), uri=True)


# ----------------------------------------------------------------------------------------------- context
class Ctx:
    """Every path the readout touches, so the selftest can point all of them at temp files."""
    def __init__(self, root=ROOT, res_dir=RES_DIR, snap_db=None, emb_db=None, outcome=OUTCOME, boot=BOOT, perm=PERM):
        self.root = root
        self.res_dir = res_dir
        self.snap_db = snap_db or os.path.join(root, "snapshots.db")
        self.emb_db = emb_db or os.path.join(root, "embeddings_cache.db")
        self.outcome = outcome
        self.boot = boot
        self.perm = perm

    def run_dir(self, arm):
        return os.path.join(self.res_dir, ARMS[arm]["dir"], "seed_42")

    def build_out(self, arm):
        return os.path.join(self.res_dir, ARMS[arm]["dir"] + ".build.out")

    def site_null(self, arm):
        return os.path.join(self.res_dir, "site_null_%s.csv" % ARMS[arm]["dir"])

    def sitenull_out(self, arm):
        return os.path.join(self.res_dir, "sitenull_%s.out" % ARMS[arm]["dir"])

    def ingest_db(self, arm):
        return os.path.join(self.root, ARMS[arm]["db"])

    def chain_log(self):
        return os.path.join(self.res_dir, "chain.log")


# ----------------------------------------------------------------------------------------------- loaders
def snapshot_id_of(build_out):
    if not os.path.exists(build_out):
        return None
    sid = None
    with open(build_out, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.search(r"Snapshot ID: (\S+)", line)
            if m:
                sid = m.group(1)
    return sid


def build_state(build_out):
    """built / not built from the build log: the [ANCHOR-FREE] vacuity guard, the leaf count, the pool line."""
    st = dict(exists=os.path.exists(build_out), snapshot=None, leaves=None, guard_fired=False, pool=None, closure=None,
              fetched=None, slice_line=None, trickle_total=None, built=False, anchor_free_end=None)
    if not st["exists"]:
        return st
    txt = open(build_out, encoding="utf-8", errors="replace").read()
    st["snapshot"] = snapshot_id_of(build_out)
    m = re.findall(r"leaves=(\d+)", txt)
    st["leaves"] = int(m[-1]) if m else None
    st["guard_fired"] = "construction ended with the root as a single leaf" in txt
    m = re.search(r"\[POOL\] recorded (\S+) \(seed=", txt)
    st["pool"] = m.group(1) if m else None
    m = re.search(r"\[SPLIT-CLOSURE\] (\d+) train item", txt)
    st["closure"] = int(m.group(1)) if m else 0
    m = re.search(r"Fetched (\d+) (.+?) queries across (\d+) categories", txt)
    st["fetched"] = (int(m.group(1)), m.group(2), int(m.group(3))) if m else None
    m = re.search(r"\[SLICE\][^\n]*", txt)
    st["slice_line"] = m.group(0).strip() if m else None
    m = re.findall(r"Total Queries: (\d+)", txt)
    st["trickle_total"] = int(m[-1]) if m else None
    m = re.search(r"\[ANCHOR-FREE\] construction ended with (\d+) emergent depth-1 nodes", txt)
    st["anchor_free_end"] = int(m.group(1)) if m else None
    st["built"] = st["snapshot"] is not None and not st["guard_fired"]
    return st


def load_ingest(db, table, offset):
    """rowid -> (text, label); text -> label; qid -> rowid. Also the eval_question_link / corpus_questions agreement."""
    con = ro(db)
    try:
        rows = con.execute("SELECT id, question, category FROM %s ORDER BY id" % table).fetchall()
        link = dict(con.execute("SELECT question_id, question_text FROM eval_question_link").fetchall())
        cq = dict(con.execute("SELECT question_id, text FROM corpus_questions").fetchall())
    finally:
        con.close()
    by_id = {i: (t, c) for i, t, c in rows}
    label_of = {}
    for i, t, c in rows:
        label_of.setdefault(t, c)
    qid_of = {}
    for i, t, c in rows:
        qid_of.setdefault(afr.qid(t), i)
    bad = sum(1 for i, t, _ in rows if link.get(i) != t or cq.get(offset + i) != t)
    if bad:
        die("%d ingest rows disagree between %s / eval_question_link / corpus_questions (Design N broken)" % (bad, table))
    return dict(by_id=by_id, label_of=label_of, qid_of=qid_of, rows=len(rows), distinct_texts=len(label_of),
                labels=sorted({c for _, _, c in rows}))


def load_reserved(snap_db, snapshot_id):
    con = ro(snap_db, immutable=True)
    try:
        row = con.execute("SELECT reserved_queries FROM snapshots WHERE id = ?", (snapshot_id,)).fetchone()
    finally:
        con.close()
    if row is None or not row[0]:
        die("snapshot %s carries no reserved_queries in %s" % (snapshot_id, rel(snap_db)))
    return json.loads(row[0])


def check_site_null_complete(path, arm):
    """Refuse a partial site null before anchor_free_redraw.read_site_null parses it: reps != 300 on any row, mixed
    snapshot ids, or no rows (the registration reads only complete 300-rep nulls; UNDETERMINED otherwise)."""
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    if not rows:
        die("%s: site null %s has no rows" % (arm, rel(path)))
    reps = {r.get("reps", "") for r in rows}
    if reps != {str(REPS)}:
        die("%s: site null %s is PARTIAL: reps %s (the registration reads only %d-rep nulls)" % (arm, rel(path), sorted(reps), REPS))
    sids = {r["snapshot_id"] for r in rows}
    if len(sids) != 1:
        die("%s: site null %s carries several snapshot ids %s" % (arm, rel(path), sorted(sids)))


def sepbar_of(sitenull_out):
    if not os.path.exists(sitenull_out):
        return None
    m = None
    for line in open(sitenull_out, encoding="utf-8", errors="replace"):
        mm = re.search(r"\[SEPBAR\] proposalSeparationBar=([0-9.]+)", line)
        if mm:
            m = float(mm.group(1))
    return m


def toml_bar(path):
    if not os.path.exists(path):
        return None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\s*proposalSeparationBar\s*=\s*([0-9.]+)", line)
        if m:
            return float(m.group(1))
    return None


def load_arm(ctx, arm, need_null=True):
    """Everything an arm's analysis needs, with the fail-closed checks. Returns None-state dicts on a not-built arm."""
    spec = ARMS[arm]
    st = build_state(ctx.build_out(arm))
    out = dict(arm=arm, spec=spec, state=st)
    if not st["built"]:
        return out
    run_dir = ctx.run_dir(arm)
    if not os.path.exists(os.path.join(run_dir, "dag_snapshots.jsonl")):
        die("%s: built per the log but %s/dag_snapshots.jsonl is missing" % (arm, rel(run_dir)))
    tree = afo.load_tree(run_dir)
    if tree["dim"] != spec["slice"]:
        die("%s: leaves carry sliceDim %d, the arm's slice is %d" % (arm, tree["dim"], spec["slice"]))
    afr.SNAP_DB = ctx.snap_db
    graph = afr.load_graph(st["snapshot"])
    mem = afr.members(graph)
    byid = graph["byid"]
    leaf_ids_graph = sorted(i for i, n in byid.items() if not n.get("childIds"))
    if sorted(tree["leaf_ids"]) != leaf_ids_graph:
        die("%s: leaf id set of dag_snapshots.jsonl (%d) != snapshot graph (%d)" % (arm, len(tree["leaf_ids"]), len(leaf_ids_graph)))
    for i in leaf_ids_graph:
        if byid[i].get("sliceDim", spec["slice"]) != spec["slice"]:
            die("%s: graph leaf %s sliceDim %s != %d" % (arm, i, byid[i].get("sliceDim"), spec["slice"]))
    sites = sorted(i for i, n in byid.items() if len(n.get("childIds") or []) >= 2)
    ing = load_ingest(ctx.ingest_db(arm), spec["table"], spec["offset"])
    reserved = load_reserved(ctx.snap_db, st["snapshot"])
    held_ids = [q for ids in reserved.values() for q in ids]
    if any(q <= 0 for q in held_ids):
        die("%s: reserved_queries carry sentinel ids (%d); Design N records real ids only" % (arm, sum(1 for q in held_ids if q <= 0)))
    lo, hi = spec["offset"], spec["offset"] + 1_000_000
    if any(not (lo < q < hi) for q in held_ids):
        die("%s: reserved ids outside the %s namespace %d..%d" % (arm, spec["table"], lo, hi))
    held_k = [q - spec["offset"] for q in held_ids]
    missing_k = [k for k in held_k if k not in ing["by_id"]]
    if missing_k:
        die("%s: %d reserved ids have no ingest row (first %s)" % (arm, len(missing_k), missing_k[:5]))
    held_texts = []
    seen = set()
    for k in held_k:
        t = ing["by_id"][k][0]
        if t not in seen:
            seen.add(t); held_texts.append(t)
    held_qids = {afr.qid(t) for t in held_texts}
    leaf_union = set().union(*(mem[i] for i in leaf_ids_graph)) if leaf_ids_graph else set()
    leaf_slots = sum(len(mem[i]) for i in leaf_ids_graph)
    in_leaf = held_qids & leaf_union
    unknown = [q for q in leaf_union if q not in ing["qid_of"]]
    if unknown:
        die("%s: %d leaf queryIds match no ingest text (first %s)" % (arm, len(unknown), unknown[:3]))
    train_qids = sorted(leaf_union)
    train_texts = [ing["by_id"][ing["qid_of"][q]][0] for q in train_qids]
    train_labels = [ing["by_id"][ing["qid_of"][q]][1] for q in train_qids]
    held_labels = [ing["label_of"][t] for t in held_texts]
    neither = ing["distinct_texts"] - len(train_texts) - len(held_texts) + len(set(train_texts) & set(held_texts))
    null = None
    if need_null and os.path.exists(ctx.site_null(arm)):
        check_site_null_complete(ctx.site_null(arm), arm)
        null = afr.read_site_null(ctx.site_null(arm))
        if null["snapshot"] != st["snapshot"]:
            die("%s: site null snapshot %s != the build's %s" % (arm, null["snapshot"], st["snapshot"]))
        extra = sorted(set(null["rows"]) - set(sites))
        if extra:
            die("%s: site null rows for non-sites %s" % (arm, extra[:5]))
    out.update(tree=tree, graph=graph, mem=mem, byid=byid, leaf_ids=leaf_ids_graph, sites=sites, ing=ing, reserved=reserved,
               held_texts=held_texts, held_labels=held_labels, held_qids=held_qids, train_qids=train_qids, train_texts=train_texts,
               train_labels=train_labels, in_leaf=in_leaf, leaf_slots=leaf_slots, neither=neither, null=null,
               sepbar=sepbar_of(ctx.sitenull_out(arm)), toml_bar=toml_bar(os.path.join(ctx.root, spec["toml"])))
    return out


def load_vectors(ctx, texts):
    afo.EMB_DB = ctx.emb_db
    return afo.full_vectors(texts)


# ----------------------------------------------------------------------------------------------- metrics
def unit(M):
    M = np.asarray(M, dtype=np.float64)
    n = np.linalg.norm(M, axis=1, keepdims=True); n[n == 0] = 1.0
    return M / n


def nmi(a, b):
    from sklearn.metrics import normalized_mutual_info_score
    return float(normalized_mutual_info_score(a, b, average_method="arithmetic"))


def ari(a, b):
    from sklearn.metrics import adjusted_rand_score
    return float(adjusted_rand_score(a, b))


def entropy(labels):
    c = Counter(labels); n = sum(c.values())
    return -sum(v / n * math.log(v / n) for v in c.values()) if n else 0.0


def groups(labels):
    return [GROUP_OF.get(l, l) for l in labels]


def partition_metrics(cells_tr, cells_ho, train, heldout):
    """The registered Q1 rows for one partition: purity (train-majority; held-out-majority optimistic), NMI / ARI at 20 and 7."""
    sc = afo.score_cells(cells_tr, cells_ho, train, heldout)
    opt = afo.score_cells(cells_ho, cells_ho, heldout, heldout)
    lab = [c for _, c in heldout]
    grp = groups(lab)
    sc7 = afo.score_cells(cells_tr, cells_ho, [(t, GROUP_OF.get(c, c)) for t, c in train], [(t, g) for (t, _), g in zip(heldout, grp)])
    sup = Counter(cells_ho)
    supports = [sup.get(c, 0) for c in set(cells_tr)]
    return dict(purity=sc["acc"], lo=sc["lo"], hi=sc["hi"], hits=sc["hits"], n=sc["n"], purity_opt=opt["acc"],
                purity7=sc7["acc"], lo7=sc7["lo"], hi7=sc7["hi"],
                nmi20=nmi(lab, cells_ho), ari20=ari(lab, cells_ho), nmi7=nmi(grp, cells_ho), ari7=ari(grp, cells_ho),
                cells=len(set(cells_tr)), cells_ho=len(set(cells_ho)), support_median=float(np.median(supports)) if supports else 0.0,
                cells_lt30=sum(1 for s in supports if s < 30), cells_empty=sum(1 for s in supports if s == 0))


def fmt_row(name, m, extra=""):
    return ("  %-34s purity %.4f [%.4f, %.4f] (%d/%d)  opt %.4f  pur7 %.4f  NMI20 %.4f ARI20 %.4f  NMI7 %.4f ARI7 %.4f  cells %d (ho %d; med support %.0f; <30: %d; empty: %d)%s"
            % (name, m["purity"], m["lo"], m["hi"], m["hits"], m["n"], m["purity_opt"], m["purity7"], m["nmi20"], m["ari20"], m["nmi7"], m["ari7"],
               m["cells"], m["cells_ho"], m["support_median"], m["cells_lt30"], m["cells_empty"], extra))


def tribool(ok):
    """Normalise a verdict to the three Python values True / False / None, and REFUSE anything else.

    Post-run review 2026-09-23, defect D1 (HIGH): a verdict whose last operand is a numpy comparison is a
    numpy.bool_, and `numpy.True_ is True` is False, so every `is True` / `is False` dispatch below was
    fail-silent in BOTH directions -- the C2 sentence of record was never written into the write-once outcome
    although the criterion line printed HELD by truthiness. Every verdict is passed through this function at
    the point it is decided, so identity dispatch can never again depend on numpy's type."""
    if ok is None:
        return None
    if isinstance(ok, (bool, np.bool_)):
        return bool(ok)
    if isinstance(ok, (int, float, np.integer, np.floating)):
        return bool(ok)
    die("verdict value %r of type %s is neither a truth value nor None (fail-closed: no verdict is decided by "
        "truthiness alone)" % (ok, type(ok).__name__))


def in_range(x, lo, hi):
    return bool(x is not None and lo <= x <= hi)   # bool(): a numpy x would make the chain a numpy.bool_ (D1)


def verdict_word(ok):
    """HELD / FAILED / UNDETERMINED from any truth value or None (numpy-safe: see tribool)."""
    ok = tribool(ok)
    return "UNDETERMINED" if ok is None else ("HELD" if ok else "FAILED")


def score(pred, ok, detail):
    """One prediction line: HELD / FAILED / UNDETERMINED (ok None), printed where the number is computed."""
    v = verdict_word(ok)
    return "  %-4s %-12s %s" % (pred, v, detail), v


# ----------------------------------------------------------------------------------------------- Q1
def q1(a, vec, out, rng_seed=RNG_SEED, boot=BOOT):
    from sklearn.cluster import KMeans, AgglomerativeClustering, HDBSCAN
    dim = a["spec"]["slice"]
    train = list(zip(a["train_texts"], a["train_labels"]))
    heldout = list(zip(a["held_texts"], a["held_labels"]))
    Xtr = afo.sliced(vec, a["train_texts"], dim)
    Xho = afo.sliced(vec, a["held_texts"], dim)
    L = len(a["leaf_ids"])
    n_eval = len(heldout)
    out.append("Q1 PARTITION (arm %s, %s): denominator n_eval = %d distinct held-out texts of the corpus's own split; TRAIN = %d distinct texts in %d leaves (%d leaf slots); slice %d" % (a["arm"], a["spec"]["kind"], n_eval, len(train), L, a["leaf_slots"], dim))
    res = {}
    # tree: leaves by argmax cosine to vmfMu (anchor_free_readout.route)
    it = afo.route(a["tree"], Xtr); ih = afo.route(a["tree"], Xho)
    tree_tr = [a["tree"]["leaf_ids"][i] for i in it]; tree_ho = [a["tree"]["leaf_ids"][i] for i in ih]
    res["tree"] = partition_metrics(tree_tr, tree_ho, train, heldout)
    out.append(fmt_row("tree leaves (L=%d)" % L, res["tree"]))
    # k-means at k = L, seeds 0-4 (renormalised cluster_centers_)
    km = {}
    for s in range(5):
        model = KMeans(n_clusters=L, n_init=10, random_state=s).fit(Xtr)
        C = unit(model.cluster_centers_)
        ctr = list(np.argmax(Xtr @ C.T, axis=1)); cho = list(np.argmax(Xho @ C.T, axis=1))
        km[s] = partition_metrics(ctr, cho, train, heldout)
        km[s]["assign_tr"] = ctr; km[s]["assign_ho"] = cho
        out.append(fmt_row("k-means k=L seed %d" % s, km[s]))
    res["kmeans"] = km
    spread = max(km[s]["nmi20"] for s in km) - min(km[s]["nmi20"] for s in km)
    diff = res["tree"]["nmi20"] - km[0]["nmi20"]
    diff_ari = res["tree"]["ari20"] - km[0]["ari20"]
    # reference rows k = 20 and k = 7 (5 seeds)
    for k, key in ((20, "k20"), (7, "k7")):
        rows = []
        for s in range(5):
            model = KMeans(n_clusters=k, n_init=10, random_state=s).fit(Xtr)
            C = unit(model.cluster_centers_)
            rows.append(partition_metrics(list(np.argmax(Xtr @ C.T, axis=1)), list(np.argmax(Xho @ C.T, axis=1)), train, heldout))
        res[key] = rows
        for s, m in enumerate(rows):
            out.append(fmt_row("k-means k=%d seed %d (reference)" % (k, s), m))
    # Ward at k = L (renormalised train-member mean)
    ward = AgglomerativeClustering(n_clusters=L, linkage="ward").fit(Xtr)
    wl = ward.labels_
    C = unit(np.stack([Xtr[wl == c].mean(axis=0) for c in range(L)]))
    res["ward"] = partition_metrics(list(np.argmax(Xtr @ C.T, axis=1)), list(np.argmax(Xho @ C.T, axis=1)), train, heldout)
    out.append(fmt_row("Ward k=L", res["ward"]))
    # HDBSCAN (min_cluster_size 55): its own k, train noise fraction, non-noise member mean
    hd = HDBSCAN(min_cluster_size=MCS).fit(Xtr)
    hl = hd.labels_
    ks = sorted(set(int(x) for x in hl if x >= 0))
    noise = float(np.mean(hl < 0))
    if ks:
        C = unit(np.stack([Xtr[hl == c].mean(axis=0) for c in ks]))
        res["hdbscan"] = partition_metrics(list(np.argmax(Xtr @ C.T, axis=1)), list(np.argmax(Xho @ C.T, axis=1)), train, heldout)
        res["hdbscan"].update(k=len(ks), noise=noise)
        out.append(fmt_row("HDBSCAN mcs=55 (k=%d, train noise %.3f)" % (len(ks), noise), res["hdbscan"]))
    else:
        res["hdbscan"] = dict(k=0, noise=noise)
        out.append("  HDBSCAN mcs=55: no cluster (every train doc noise); no row")
    # random partition: the tree's held-out cells with labels permuted (5 seeds) = the chance floor at the tree's cell-size profile
    rnd = []
    for s in range(5):
        rs = np.random.RandomState(s)
        perm = [heldout[i][1] for i in rs.permutation(n_eval)]
        ph = [(t, c) for (t, _), c in zip(heldout, perm)]
        rnd.append(partition_metrics(tree_tr, tree_ho, train, ph))
    res["random"] = rnd
    for s, m in enumerate(rnd):
        out.append(fmt_row("random (tree cells, labels permuted) seed %d" % s, m))
    # sensitivity: k-means at k = L on the FULL 4096-d vectors
    Xtr_full = unit(np.stack([vec[t] for t in a["train_texts"]])); Xho_full = unit(np.stack([vec[t] for t in a["held_texts"]]))
    model = KMeans(n_clusters=L, n_init=10, random_state=0).fit(Xtr_full)
    C = unit(model.cluster_centers_)
    res["kmeans_full"] = partition_metrics(list(np.argmax(Xtr_full @ C.T, axis=1)), list(np.argmax(Xho_full @ C.T, axis=1)), train, heldout)
    out.append(fmt_row("k-means k=L on FULL %d-d (seed 0)" % Xtr_full.shape[1], res["kmeans_full"]))
    # fixed-partition bootstrap on NMI(20)_tree - NMI(20)_kmeans0 (ARI beside)
    rs = np.random.RandomState(rng_seed)
    lab = np.array([c for _, c in heldout]); t_ho = np.array(tree_ho); k_ho = np.array(km[0]["assign_ho"])
    d_nmi = []; d_ari = []
    for _ in range(boot):
        idx = rs.randint(0, n_eval, n_eval)
        d_nmi.append(nmi(lab[idx], t_ho[idx]) - nmi(lab[idx], k_ho[idx]))
        d_ari.append(ari(lab[idx], t_ho[idx]) - ari(lab[idx], k_ho[idx]))
    ci = (float(np.percentile(d_nmi, 2.5)), float(np.percentile(d_nmi, 97.5)))
    ci_ari = (float(np.percentile(d_ari, 2.5)), float(np.percentile(d_ari, 97.5)))
    res.update(spread=spread, diff=diff, diff_ari=diff_ari, ci=ci, ci_ari=ci_ari, n_eval=n_eval, L=L,
               tree_ho=tree_ho, tree_tr=tree_tr, kmeans0_ho=km[0]["assign_ho"])
    out.append("  NMI(20) tree - kmeans0 = %.4f (ARI diff %.4f); k-means seed spread (max - min over 5 seeds) = %.4f; %d-resample fixed-partition bootstrap CI [%.4f, %.4f] (ARI [%.4f, %.4f]); n_eval %d"
               % (diff, diff_ari, spread, boot, ci[0], ci[1], ci_ari[0], ci_ari[1], n_eval))
    # sensitivity rows: excluding leak documents; excluding documents > 8,000 chars
    lower = [l.lower() for l in LABELS_20]
    leak_idx = [i for i, (t, _) in enumerate(heldout) if any(l in t.lower() for l in lower)]
    long_idx = [i for i, (t, _) in enumerate(heldout) if len(t) > LEAK_LONG_CHARS]
    for name, drop in (("leak documents", leak_idx), ("documents > 8,000 chars", long_idx)):
        keep = [i for i in range(n_eval) if i not in set(drop)]
        if not keep or not drop:
            out.append("  sensitivity excluding %s: %d of %d excluded; %s" % (name, len(drop), n_eval, "no row" if not drop else "nothing left"))
            res["sens_" + name] = dict(excluded=len(drop), n=n_eval, tree=None, kmeans0=None)
            continue
        ho2 = [heldout[i] for i in keep]
        mt = partition_metrics(tree_tr, [tree_ho[i] for i in keep], train, ho2)
        mk = partition_metrics(km[0]["assign_tr"], [km[0]["assign_ho"][i] for i in keep], train, ho2)
        res["sens_" + name] = dict(excluded=len(drop), n=n_eval, tree=mt, kmeans0=mk)
        out.append("  sensitivity excluding %s (%d of %d held-out excluded; n=%d): tree purity %.4f (delta %+.4f pp) NMI20 %.4f; kmeans0 purity %.4f NMI20 %.4f"
                   % (name, len(drop), n_eval, len(keep), mt["purity"], 100 * (mt["purity"] - res["tree"]["purity"]), mt["nmi20"], mk["purity"], mk["nmi20"]))
    train_long = sum(1 for t in a["train_texts"] if len(t) > LEAK_LONG_CHARS)
    out.append("  (train documents > 8,000 chars: %d of %d; held-out leak documents: %d of %d = %.4f)" % (train_long, len(train), len(leak_idx), n_eval, len(leak_idx) / n_eval))
    res["leak_share"] = len(leak_idx) / n_eval
    return res


# ----------------------------------------------------------------------------------------------- Q2
def assign_child(a, node_id, docs, X_of):
    """docs (qids) at site node_id -> chosen child per doc: the child whose member set holds it; several -> higher cosine to the child's vmfMu."""
    kids = a["byid"][node_id]["childIds"]
    mus = {c: unit([a["byid"][c]["vmfMu"]])[0] for c in kids}
    choice = {}
    for q in docs:
        holders = [c for c in kids if q in a["mem"][c]]
        if not holders:
            continue
        if len(holders) == 1:
            choice[q] = holders[0]
        else:
            x = X_of[q]
            choice[q] = max(holders, key=lambda c: float(x @ mus[c]))
    return choice


def q2(a, vec, out, q1res=None, rng_seed=RNG_SEED, perm=PERM):
    dim = a["spec"]["slice"]
    X = afo.sliced(vec, a["train_texts"], dim)
    X_of = {q: X[i] for i, q in enumerate(a["train_qids"])}
    lab_of = {q: a["train_labels"][i] for i, q in enumerate(a["train_qids"])}
    root = a["graph"]["root"]
    n_train = len(a["train_qids"])
    out.append("Q2 TOPICS (arm %s): denominator per site = the site's TRAIN members (union of descendant leaves' queryIds; %d distinct train ids over %d leaf slots); %d sites (internal nodes with >= 2 children); labels from the ingest DB only" % (a["arm"], n_train, a["leaf_slots"], len(a["sites"])))
    res = dict(sites={})
    # per site: child partition vs labels on the site's members
    for s in a["sites"]:
        docs = sorted(a["mem"][s])
        ch = assign_child(a, s, docs, X_of)
        qs = [q for q in docs if q in ch]
        labs = [lab_of[q] for q in qs]; grp = groups(labs); kids = [ch[q] for q in qs]
        h20 = entropy(labs)
        per_child = {}
        for c in a["byid"][s]["childIds"]:
            cl = [lab_of[q] for q in qs if ch[q] == c]
            if cl:
                ml, mc = Counter(cl).most_common(1)[0]; mg, mgc = Counter(groups(cl)).most_common(1)[0]
                per_child[c] = dict(n=len(cl), label=ml, label_share=mc / len(cl), group=mg, group_share=mgc / len(cl))
            else:
                per_child[c] = dict(n=0, label=None, label_share=0.0, group=None, group_share=0.0)
        res["sites"][s] = dict(n=len(qs), k=len(a["byid"][s]["childIds"]), depth=a["byid"][s]["depth"],
                               nmi20=nmi(labs, kids) if len(set(kids)) > 1 and h20 > 0 else 0.0,
                               nmi7=nmi(grp, kids) if len(set(kids)) > 1 and entropy(grp) > 0 else 0.0,
                               h20=h20, children=per_child)
    zero_h = [s for s, r in res["sites"].items() if r["h20"] == 0.0]
    out.append("  sites with H_20 = 0 (single-label member set; printed, not dropped): %d of %d" % (len(zero_h), len(a["sites"])))
    # depth-1 children: majority 7-group and share; migration matrix 7-group x depth-1 cell (train and held-out)
    d1 = a["byid"][root]["childIds"]
    if root not in res["sites"]:
        # a one-child root is not a split site (the vacuity guard forbids zero children, not one): there is no depth-1
        # partition to read, and res["sites"][root] would raise. Fail closed, naming the node.
        die("%s: the root %s has %d child(ren) (%s) and is not a split site (>= 2 children): Q2 has no depth-1 "
            "partition to read at the root" % (a["arm"], root, len(d1), ", ".join(d1) if d1 else "none"))
    ch_root = assign_child(a, root, sorted(a["mem"][root]), X_of)
    out.append("  depth-1 cells (k = %d at the root; root members %d of %d train ids):" % (len(d1), len(ch_root), n_train))
    mig_tr = defaultdict(Counter)
    for q, c in ch_root.items():
        mig_tr[GROUP_OF.get(lab_of[q], lab_of[q])][c] += 1
    for c in d1:
        pc = res["sites"][root]["children"][c]
        out.append("    %s (%s): n=%d majority group %s (%.3f) majority label %s (%.3f)" % (c, a["byid"][c].get("label"), pc["n"], pc["group"], pc["group_share"], pc["label"], pc["label_share"]))
    # held-out migration: leaf routing -> depth-1 ancestor (the tree's own grouping)
    Xho = afo.sliced(vec, a["held_texts"], dim)
    ih = afo.route(a["tree"], Xho)
    ho_d1 = [a["tree"]["leaf_d1"][i] for i in ih]
    mig_ho = defaultdict(Counter)
    for g, c in zip(groups(a["held_labels"]), ho_d1):
        mig_ho[g][c] += 1
    out.append("  migration matrix 7-group x depth-1 cell, TRAIN (row = group, n; columns = %s):" % ",".join(d1))
    for g in GROUPS_7:
        n = sum(mig_tr[g].values())
        out.append("    %-24s n=%5d  %s" % (g, n, "  ".join("%s:%.3f" % (c, mig_tr[g][c] / n if n else 0.0) for c in d1)))
    out.append("  migration matrix 7-group x depth-1 cell, HELD-OUT (leaf-routed, depth-1 ancestor; n_eval %d):" % len(a["held_texts"]))
    for g in GROUPS_7:
        n = sum(mig_ho[g].values())
        out.append("    %-24s n=%5d  %s" % (g, n, "  ".join("%s:%.3f" % (c, mig_ho[g][c] / n if n else 0.0) for c in d1)))
    # P7's registrar rule: HELD iff the comp.* majority cell and the talk.* majority cell differ; rec.*'s cell and share printed
    def maj(g, mig):
        n = sum(mig[g].values())
        if not n:
            return None, 0.0
        c, v = mig[g].most_common(1)[0]
        return c, v / n
    comp_c, comp_s = maj("comp", mig_tr); talk_c, talk_s = maj("talk", mig_tr); rec_c, rec_s = maj("rec", mig_tr)
    res["p7_split"] = dict(comp=(comp_c, comp_s), talk=(talk_c, talk_s), rec=(rec_c, rec_s), held=(comp_c is not None and talk_c is not None and comp_c != talk_c))
    # depth-1 purity at 7 groups and at 20 labels (held-out, train-majority) for P7
    tr_d1 = [ch_root.get(q) for q in a["train_qids"]]
    keep = [i for i, c in enumerate(tr_d1) if c is not None]
    m7 = afo.score_cells([tr_d1[i] for i in keep], ho_d1, [(a["train_texts"][i], GROUP_OF.get(a["train_labels"][i], a["train_labels"][i])) for i in keep],
                         list(zip(a["held_texts"], groups(a["held_labels"]))))
    m20 = afo.score_cells([tr_d1[i] for i in keep], ho_d1, [(a["train_texts"][i], a["train_labels"][i]) for i in keep], list(zip(a["held_texts"], a["held_labels"])))
    res["d1_purity7"] = m7["acc"]; res["d1_purity20"] = m20["acc"]; res["d1_k"] = len(d1)
    out.append("  depth-1 held-out purity (train-majority): 7-group %.4f [%.4f, %.4f] (%d/%d); 20-label %.4f [%.4f, %.4f] (%d/%d); k = %d"
               % (m7["acc"], m7["lo"], m7["hi"], m7["hits"], m7["n"], m20["acc"], m20["lo"], m20["hi"], m20["hits"], m20["n"], len(d1)))
    # depth-d cuts: one path per train doc (child of higher cosine at every site), the node at depth <= d
    path_of = {}
    def descend(q):
        node = root; path = [node]
        while a["byid"][node].get("childIds"):
            ch = assign_child(a, node, [q], X_of).get(q)
            if ch is None:
                break
            node = ch; path.append(node)
        return path
    for q in a["train_qids"]:
        path_of[q] = descend(q)
    maxd = max(len(p) for p in path_of.values()) - 1
    labs = [lab_of[q] for q in a["train_qids"]]; grp = groups(labs)
    cuts = {}
    for d in range(1, 9):
        cells = [path_of[q][min(d, len(path_of[q]) - 1)] for q in a["train_qids"]]
        cuts[d] = dict(nmi7=nmi(grp, cells), nmi20=nmi(labs, cells), cells=len(set(cells)))
    best7 = max(cuts, key=lambda d: cuts[d]["nmi7"]); best20 = max(cuts, key=lambda d: cuts[d]["nmi20"])
    res["cuts"] = cuts; res["best7_depth"] = best7; res["best20_depth"] = best20; res["max_depth"] = maxd
    out.append("  depth-d cuts (TRAIN, n=%d; deepest node at depth <= d on the doc's max-cosine path; tree depth %d):" % (n_train, maxd))
    for d in range(1, 9):
        out.append("    d=%d  cells %4d  NMI_7 %.4f  NMI_20 %.4f%s%s" % (d, cuts[d]["cells"], cuts[d]["nmi7"], cuts[d]["nmi20"], "  <- argmax NMI_7" if d == best7 else "", "  <- argmax NMI_20" if d == best20 else ""))
    # per label: node of any depth with max Jaccard(member set, label set on TRAIN); per group likewise; per leaf max J
    label_set = defaultdict(set); group_set = defaultdict(set)
    for q in a["train_qids"]:
        label_set[lab_of[q]].add(q); group_set[GROUP_OF.get(lab_of[q], lab_of[q])].add(q)
    def best_node(S):
        best = (None, -1.0, 0, 0)
        for v, M in a["mem"].items():
            if not M:
                continue
            j = len(M & S) / len(M | S)
            if j > best[1]:
                best = (v, j, a["byid"][v]["depth"], len(M))
        return best
    res["label_best"] = {l: best_node(label_set[l]) for l in sorted(label_set)}
    res["group_best"] = {g: best_node(group_set[g]) for g in sorted(group_set)}
    out.append("  per-label best-Jaccard node (TRAIN; label n -> node, depth, J, node n):")
    for l, (v, j, d, n) in res["label_best"].items():
        out.append("    %-26s n=%4d -> %s depth %d J %.4f n %d" % (l, len(label_set[l]), v, d, j, n))
    out.append("  per-group best-Jaccard node:")
    for g, (v, j, d, n) in res["group_best"].items():
        out.append("    %-26s n=%4d -> %s depth %d J %.4f n %d" % (g, len(group_set[g]), v, d, j, n))
    lj = [j for _, j, _, _ in res["label_best"].values()]; ld = [d for _, _, d, _ in res["label_best"].values()]
    gj = [j for _, j, _, _ in res["group_best"].values()]; gd = [d for _, _, d, _ in res["group_best"].values()]
    res["label_median_depth"] = float(np.median(ld)); res["label_median_j"] = float(np.median(lj))
    res["group_median_depth"] = float(np.median(gd)); res["group_median_j"] = float(np.median(gj))
    out.append("  median best depth / median best J: 20 labels %.1f / %.4f (n=%d); 7 groups %.1f / %.4f (n=%d)"
               % (res["label_median_depth"], res["label_median_j"], len(lj), res["group_median_depth"], res["group_median_j"], len(gj)))
    leaf_j = {}
    for leaf in a["leaf_ids"]:
        M = a["mem"][leaf]
        leaf_j[leaf] = max((len(M & S) / len(M | S) for S in label_set.values()), default=0.0) if M else 0.0
    res["leaf_j"] = leaf_j
    res["leaves_j50"] = sum(1 for j in leaf_j.values() if j >= 0.5)
    out.append("  leaves at max-Jaccard >= 0.5: %d of %d (%.3f); median leaf max J %.4f" % (res["leaves_j50"], len(leaf_j), res["leaves_j50"] / max(1, len(leaf_j)), float(np.median(list(leaf_j.values()))) if leaf_j else 0.0))
    # certification vs alignment
    res["cert"] = None
    if a["null"] is not None:
        res["cert"] = cert_vs_alignment(a, res["sites"], out, rng_seed, perm)
    else:
        out.append("  certification vs alignment: no site null (UNDETERMINED)")
    return res


def strata_of(depth):
    return "0-1" if depth <= 1 else ("2" if depth == 2 else ("3" if depth == 3 else ("4" if depth == 4 else ">=5")))


def stratified_gap(y, cert, depth):
    num = 0.0; den = 0.0; rows = {}
    for s in ("0-1", "2", "3", "4", ">=5"):
        idx = [i for i in range(len(y)) if strata_of(depth[i]) == s]
        c = [y[i] for i in idx if cert[i]]; u = [y[i] for i in idx if not cert[i]]
        w = min(len(c), len(u))
        g = (float(np.mean(c)) - float(np.mean(u))) if w > 0 else None
        rows[s] = dict(n_cert=len(c), n_uncert=len(u), gap=g, w=w)
        if w > 0:
            num += w * g; den += w
    return (num / den if den > 0 else None), rows


def ols_hc1(y, X):
    X = np.asarray(X, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    n, p = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    e = y - X @ beta
    meat = X.T @ (X * (e ** 2)[:, None])
    V = XtX_inv @ meat @ XtX_inv * (n / max(1, n - p))
    se = np.sqrt(np.maximum(np.diag(V), 0.0))
    return beta, se


def cert_vs_alignment(a, site_res, out, rng_seed, perm):
    rows = a["null"]["rows"]
    ids = [s for s in a["sites"] if s in rows]
    missing = [s for s in a["sites"] if s not in rows]
    if missing:
        out.append("  NOTE: %d split sites have no site-null row (the harness enumerates dasguptaDeltaNorm > 0 sites): %s" % (len(missing), missing[:5]))
    res = {}
    for key, name in (("nmi20", "20 labels"), ("nmi7", "7 groups")):
        y = [site_res[s][key] for s in ids]; cert = [rows[s]["cert"] for s in ids]; depth = [rows[s]["depth"] for s in ids]; n = [rows[s]["n"] for s in ids]
        nc = sum(cert); nu = len(cert) - nc
        raw = (float(np.mean([v for v, c in zip(y, cert) if c])) - float(np.mean([v for v, c in zip(y, cert) if not c]))) if nc and nu else None
        sg, strata = stratified_gap(y, cert, depth)
        X = [[1.0, 1.0 if c else 0.0, math.log(max(1, nn)), float(d)] for c, nn, d in zip(cert, n, depth)]
        beta, se = ols_hc1(y, X) if len(y) > 4 else (np.array([float("nan")] * 4), np.array([float("nan")] * 4))
        rs = np.random.RandomState(rng_seed)
        ge = 0; done = 0
        perm_vals = set()   # (e)(iv): the DISTINCT values of the permuted stratified gap; collected, never used to shuffle
        if sg is not None:
            groups_idx = defaultdict(list)
            for i, d in enumerate(depth):
                groups_idx[strata_of(d)].append(i)
            for _ in range(perm):
                pc = list(cert)
                for idx in groups_idx.values():
                    vals = [cert[i] for i in idx]; rs.shuffle(vals)
                    for i, v in zip(idx, vals):
                        pc[i] = v
                    g, _ = stratified_gap(y, pc, depth)
                done += 1
                if g is not None and g >= sg:
                    ge += 1
                perm_vals.add(g)   # (e)(iv): exact values, unrounded (the registered test is "fewer than 2 distinct values")
        p = (1 + ge) / (1 + done) if done else None
        med_c = float(np.median([nn for nn, c in zip(n, cert) if c])) if nc else None
        med_u = float(np.median([nn for nn, c in zip(n, cert) if not c])) if nu else None
        res[key] = dict(raw=raw, strat=sg, strata=strata, beta=beta, se=se, p=p, n_cert=nc, n_uncert=nu, med_n_cert=med_c, med_n_uncert=med_u, sites=len(ids),
                        perm_distinct=len(perm_vals), perm_done=done)   # (e)(iv) inputs; nothing printed from them here
        out.append("  certification vs alignment at %s (Y_s = NMI_%s of the child partition; %d sites = %d certified + %d uncertified at cert_site_p95; median site n %s vs %s):"
                   % (name, "20" if key == "nmi20" else "7", len(ids), nc, nu, med_c, med_u))
        out.append("    (i) raw gap certified - uncertified = %s (confounded by size and depth)" % ("%.4f" % raw if raw is not None else "n/a"))
        out.append("    (ii) depth-stratified gap = %s; strata: %s" % ("%.4f" % sg if sg is not None else "n/a",
                   "; ".join("%s: c%d/u%d gap %s" % (s, r["n_cert"], r["n_uncert"], "%.4f" % r["gap"] if r["gap"] is not None else "-") for s, r in strata.items())))
        out.append("    (iii) OLS Y ~ cert + log n + depth (HC1): cert %.4f (SE %.4f), log n %.4f (SE %.4f), depth %.4f (SE %.4f), intercept %.4f" % (beta[1], se[1], beta[2], se[2], beta[3], se[3], beta[0]))
        out.append("    (iv) one-sided permutation p (certified higher; %d permutations of the flag WITHIN depth strata) = %s" % (done, "%.4f" % p if p is not None else "n/a"))
    return res


# ----------------------------------------------------------------------------------------------- Q3
def q3(a, out):
    st = a["state"]; spec = a["spec"]
    res = dict(built=st["built"], leaves=len(a["leaf_ids"]) if st["built"] else st["leaves"], sites=len(a["sites"]) if st["built"] else None)
    out.append("Q3 TRANSFER (arm %s, %s; bar %s, slice %d): built = %s (vacuity guard fired: %s); leaves = %s (> 7: %s; > 20: %s); sites = %s; iterations to stop = %s; fetched %s"
               % (a["arm"], spec["kind"], a.get("toml_bar", spec["bar"]), spec["slice"], st["built"], st["guard_fired"], res["leaves"],
                  res["leaves"] is not None and res["leaves"] > 7, res["leaves"] is not None and res["leaves"] > 20, res["sites"],
                  a["tree"]["iteration"] if st["built"] else "n/a", st["fetched"]))
    if not st["built"]:
        return res
    res["iterations"] = a["tree"]["iteration"]
    root = a["graph"]["root"]
    d1 = [c for c in a["byid"][root]["childIds"] if c in a["sites"]]
    # refused-k rows from proposals.csv (min_pair_sep_below_bar) at the root and the depth-1 sites
    pp = os.path.join(a["run_dir"] if "run_dir" in a else "", "diagnostics", "proposals.csv")
    refused = {}; bars = set()
    if os.path.exists(pp):
        refused, bars = afr.refused_rows(pp, [root] + list(a["byid"][root]["childIds"]))
    res["refused"] = refused; res["bars"] = sorted(bars)
    null = a["null"]
    res["depth_blocked"] = sum(1 for l in a["leaf_ids"] if a["byid"][l]["depth"] >= 8 and len(a["mem"][l]) >= 2 * MCS)
    res["max_depth"] = max(a["byid"][i]["depth"] for i in a["byid"])
    out.append("  depth reached %d; depth-blocked leaves (depth 8, n >= %d) = %d of %d leaves; proposals.csv bars seen %s" % (res["max_depth"], 2 * MCS, res["depth_blocked"], len(a["leaf_ids"]), res["bars"]))
    def site_line(s, tag):
        r = null["rows"].get(s) if null else None
        rf = refused.get(s, {}).get("minpair", [])
        rtxt = "; refused k rows: " + ", ".join("k=%d sep %.5f (emK %d, iter %d)" % (x["k"], x["sep"], x["emK"], x["iter"]) for x in rf) if rf else "; no min-pair refusal row"
        if r is None:
            return "  %s %s (%s): no site-null row%s" % (tag, s, a["byid"][s].get("label"), rtxt)
        return ("  %s %s (%s): depth %d n %d k %d observed %.6f site p95 %.6f margin %.3f cert_site_p95 %s (deflated p95 %.6f, cert_deflated %s [diagnostic only])%s"
                % (tag, s, a["byid"][s].get("label"), r["depth"], r["n"], r["k"], r["observed"], r["p95"], r["observed"] / r["p95"] if r["p95"] > 0 else float("inf"), r["cert"],
                   float(null["rows"][s].get("defl_p95", float("nan"))) if "defl_p95" in null["rows"][s] else float("nan"), r["defl"], rtxt))
    out.append(site_line(root, "root"))
    for c in a["byid"][root]["childIds"]:
        out.append(site_line(c, "depth-1"))
    out.append("  beside R1 af_clean_s42: root %.6f / p95 %.6f / margin %.3f (%s); discursive %.6f / %.6f / %.3f (%s); quantitative %.6f / %.6f / %.3f (%s); K-SELECTION R1' n00000004 %.6f / %.6f / %.3f"
               % (R1_ROOT["observed"], R1_ROOT["p95"], R1_ROOT["margin"], R1_ROOT["node"], R1_DISCURSIVE["observed"], R1_DISCURSIVE["p95"], R1_DISCURSIVE["margin"], R1_DISCURSIVE["node"],
                  R1_QUANT["observed"], R1_QUANT["p95"], R1_QUANT["margin"], R1_QUANT["node"], KSEL_R1PRIME_N4["observed"], KSEL_R1PRIME_N4["p95"], KSEL_R1PRIME_N4["margin"]))
    if null is None:
        out.append("  site null: ABSENT (certified share UNDETERMINED)")
        res.update(cert=None)
        return res
    rows = null["rows"]
    certd = sum(1 for r in rows.values() if r["cert"]); nsites = len(rows)
    res.update(cert=certd, null_sites=nsites, root_cert=rows.get(root, {}).get("cert", False),
               d1_cert=[c for c in a["byid"][root]["childIds"] if rows.get(c, {}).get("cert")], d1_sites=[c for c in a["byid"][root]["childIds"] if c in rows],
               root_k=rows.get(root, {}).get("k"), root_obs=rows.get(root, {}).get("observed"), root_p95=rows.get(root, {}).get("p95"),
               defl=sum(1 for r in rows.values() if r["defl"]), reps=null["reps"], sepbar=a.get("sepbar"))
    lo, hi = wilson(certd, nsites) if nsites else (0, 0)
    out.append("  certified share (cert_site_p95, %d reps, null bar %s): %d of %d = %.3f [%.3f, %.3f]; R1 %d of %d = %.3f (per-draw band 10-16 of 64-69); deflated (diagnostic, never the certificate): %d of %d"
               % (null["reps"], "%.4f" % a["sepbar"] if a.get("sepbar") is not None else "NOT RECORDED in sitenull_<arm>.out", certd, nsites, certd / nsites if nsites else 0.0, lo, hi, R1_CERT[0], R1_CERT[1], R1_CERT[0] / R1_CERT[1], res["defl"], nsites))
    bands = {}
    for name, cond in (("n<200", lambda n: n < 200), ("200-400", lambda n: 200 <= n < 400), ("400-800", lambda n: 400 <= n < 800), (">=800", lambda n: n >= 800)):
        b = [r for r in rows.values() if cond(r["n"])]
        bands[name] = (sum(1 for r in b if r["cert"]), len(b))
    res["bands"] = bands
    out.append("  by site-size band (this arm vs the record's four free draws; p95 falls with n, so a larger corpus certifies more easily: not like-for-like): "
               + "; ".join("%s %d/%d (record %d/%d = %.3f)" % (k, bands[k][0], bands[k][1], RECORD_BANDS[k][0], RECORD_BANDS[k][1], RECORD_BANDS[k][0] / RECORD_BANDS[k][1]) for k in bands))
    return res


# ----------------------------------------------------------------------------------------------- P12 machine times
def chain_times(ctx):
    p = ctx.chain_log()
    if not os.path.exists(p):
        return {}
    ev = {}
    for line in open(p, encoding="utf-8", errors="replace"):
        m = re.match(r"\[(\d\d):(\d\d):(\d\d)\] (\S+) (BUILD|SITENULL) (start|exit)", line)
        if m:
            t = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            ev[(m.group(4), m.group(5), m.group(6))] = t
    out = {}
    for arm in ("ag_news_smoke_s42", "ng_af_s42", "ng_af_bareq512_s42", "ng_af_bar_eq_s42"):
        for step in ("BUILD", "SITENULL"):
            s, e = ev.get((arm, step, "start")), ev.get((arm, step, "exit"))
            if s is not None and e is not None:
                d = e - s
                if d < 0:
                    d += 86400
                out[(arm, step)] = d / 60.0
    return out


# ----------------------------------------------------------------------------------------------- scoring
C2_SENTENCES = dict(
    held="The certificate is topic-informative on a corpus with discrete topics (stratified gap %.4f, p %.4f).",
    failed="The certificate reads geometry, not topic boundaries, on this corpus.",
    undetermined="The instrument had no certified/uncertified contrast to read at matched depth (C2 UNDETERMINED: "
                 "T1 not built, or no complete site null; pre-run bracket (e)).",
    # TP20-C2-CONFORMANCE (registrar's ruling 2026-09-23 (b)): the SAME registered sentence of record, with the
    # named reason and its count, on the no-contrast path of a BUILT arm with a complete null -- so that an EMPTY
    # INSTRUMENT can be told from a MEASURED NULL at a glance.
    undetermined_no_contrast="The instrument had no certified/uncertified contrast to read at matched depth "
                             "(C2 UNDETERMINED, F2 NOT FIRED; pre-run bracket (e): %s).")


def c2_sentence(c2, gap, p, no_contrast=None):
    """The C2 VERDICT-RULE sentence, TOTAL over the three registered verdicts: HELD, FAILED (a measured null) and
    UNDETERMINED (pre-run bracket (e): no contrast to read). Exactly one sentence is returned for every verdict and
    anything outside {True, False, None} is a refusal -- the write-once outcome can no longer lose the sentence in
    silence (post-run review 2026-09-23, defect D1: `numpy.True_ is True` is False, so the HELD sentence of the
    2026-09-23 run was never written although the criterion line printed HELD)."""
    if c2 is True:
        if gap is None or p is None:
            die("C2 is HELD but its stratified gap / permutation p are not recorded (gap %r, p %r)" % (gap, p))
        return C2_SENTENCES["held"] % (gap, p)
    if c2 is False:
        return C2_SENTENCES["failed"]
    if c2 is None:
        if no_contrast:
            return C2_SENTENCES["undetermined_no_contrast"] % "; ".join(no_contrast)
        return C2_SENTENCES["undetermined"]
    die("C2 verdict %r of type %s is not True / False / None: no sentence of record can be written for it "
        "(a numpy bool reaches here only if tribool() was bypassed)" % (c2, type(c2).__name__))


F2_NOT_FIRED = ("  F2 NOT FIRED (registrar's ruling 2026-09-23 (c): a falsifier may not fire on an UNDETERMINED C2 -- "
                "F2 fires only on a MEASURED null, a computed stratified gap <= 0 or a computed permutation p >= 0.05 "
                "with all four no-contrast conditions of pre-run bracket (e) false)")


def stratum_weight(strata):
    """Total depth-stratum weight sum(min(n_cert, n_uncert)) over the registered strata {0-1, 2, 3, 4, >= 5}
    (pre-run bracket (e)(iii)). A plain int: no numpy value is allowed to reach a printer or a truth test (D1)."""
    return int(sum(int(r["w"]) for r in strata.values()))


def c2_no_contrast(n_cert, n_uncert, weight, perm_distinct, perm_done):
    """The FOUR no-contrast conditions of pre-run bracket (e), each returning its NAMED REASON with the COUNT that
    fired it (registrar's ruling 2026-09-23 (b)): (i) fewer than 2 certified sites, (ii) fewer than 2 uncertified
    sites, (iii) total depth-stratum weight 0, (iv) a degenerate permutation distribution (fewer than 2 distinct
    values over the within-stratum permutations). The empty list means the instrument HAS a contrast and the
    verdict expression may be evaluated -- ruling (a): these are evaluated BEFORE it, so a draw with no contrast can
    never reach `strat > 0 and p < 0.05 and beta[1] > 0`. Every input is coerced to int here, so no numpy value can
    decide a condition by truthiness (the D1 lesson) and every printed count is a Python int."""
    n_cert = int(n_cert); n_uncert = int(n_uncert); weight = int(weight)
    perm_distinct = int(perm_distinct); perm_done = int(perm_done)
    reasons = []
    if n_cert < 2:
        reasons.append("(i) fewer than 2 certified sites: certified n = %d" % n_cert)
    if n_uncert < 2:
        reasons.append("(ii) fewer than 2 uncertified sites: uncertified n = %d" % n_uncert)
    if weight <= 0:
        reasons.append("(iii) total depth-stratum weight sum(min(n_cert, n_uncert)) over {0-1, 2, 3, 4, >= 5} = %d" % weight)
    if perm_distinct < 2:
        reasons.append("(iv) degenerate permutation distribution: %d distinct value(s) over %d within-stratum permutations"
                       % (perm_distinct, perm_done))
    return reasons


def c2_decide(c):
    """C2's verdict, its criterion line(s) and the verdict fields it records, from the nmi20 certification block.

    TP20-C2-CONFORMANCE (queue item; registrar's ruling of 2026-09-23, which adopts pre-run bracket (e) as already
    registered text): the four no-contrast conditions are evaluated FIRST (ruling (a)); if any fires, C2 reads
    UNDETERMINED with its named reason and count (ruling (b)), F2 is recorded NOT FIRED (ruling (c)) and the
    registered no-contrast sentence -- not either VERDICT-RULE sentence -- is what the outcome carries. Only a draw
    WITH a contrast reaches the registered verdict expression, whose line is byte-identical to the one this readout
    has always printed (ruling: a change that alters one character of the 2026-09-23 verdict block is refused)."""
    if "perm_distinct" not in c or "perm_done" not in c:
        die("the C2 inputs carry no permutation distinct-value count (perm_distinct / perm_done): pre-run bracket "
            "(e)(iv) cannot be evaluated and no C2 verdict may be decided without it")
    reasons = c2_no_contrast(c["n_cert"], c["n_uncert"], stratum_weight(c["strata"]), c["perm_distinct"], c["perm_done"])
    if reasons:
        strata_txt = "; ".join("%s: c%d/u%d gap %s" % (s, r["n_cert"], r["n_uncert"], "%.4f" % r["gap"] if r["gap"] is not None else "-")
                               for s, r in c["strata"].items())
        lines = ["C2 (Q2; rule: HELD if the depth-stratified certified - uncertified NMI_20 gap > 0 with permutation p < 0.05 (and the OLS cert coefficient > 0); FAILED otherwise, F2 fires; pre-run bracket (e): UNDETERMINED with F2 NOT FIRED when the comparison has no contrast to read): UNDETERMINED -- no contrast: %s"
                 % "; ".join(reasons),
                 "  still printed (bracket (e)): raw gap certified - uncertified = %s, depth-stratified gap %s, permutation p %s, %d certified / %d uncertified sites; strata: %s"
                 % ("%.4f" % c["raw"] if c["raw"] is not None else "n/a", "%.4f" % c["strat"] if c["strat"] is not None else "n/a",
                    "%.4f" % c["p"] if c["p"] is not None else "n/a", int(c["n_cert"]), int(c["n_uncert"]), strata_txt),
                 F2_NOT_FIRED]
        return None, lines, dict(c2=None, c2_gap=c["strat"], c2_p=c["p"], c2_no_contrast=reasons, f2=False)
    # tribool(): c["beta"] is a numpy array, so the last operand -- and therefore the whole and-chain -- is a
    # numpy.bool_; without this the True / False dispatch of the VERDICT-RULE sentence below is fail-silent (D1).
    c2 = tribool(c["strat"] is not None and c["strat"] > 0 and c["p"] is not None and c["p"] < 0.05 and c["beta"][1] > 0)
    lines = ["C2 (Q2; rule: HELD if the depth-stratified certified - uncertified NMI_20 gap > 0 with permutation p < 0.05 (and the OLS cert coefficient > 0); FAILED otherwise, F2 fires): %s -- stratified gap %s, p %s, OLS cert %.4f (HC1 SE %.4f), %d certified / %d uncertified sites"
             % ("HELD" if c2 else "FAILED", "%.4f" % c["strat"] if c["strat"] is not None else "n/a", "%.4f" % c["p"] if c["p"] is not None else "n/a", c["beta"][1], c["se"][1], c["n_cert"], c["n_uncert"])]
    return c2, lines, dict(c2=c2, c2_gap=c["strat"], c2_p=c["p"])


def criteria_and_predictions(ctx, arms, results, out, manifest, readout_minutes):
    lines = []
    verdict = {}
    T1 = results.get("ng_af_s42"); T1b = results.get("ng_af_bareq512_s42"); T2 = results.get("ng_af_bar_eq_s42")
    a1 = arms.get("ng_af_s42")
    # ---- C0 gate
    c0_parts = []
    fetched = a1["state"]["fetched"] if a1 else None
    kept = manifest["counts"]["kept"] if manifest else None
    c0_manifest = fetched is not None and kept is not None and fetched[0] == kept and fetched[2] == 20
    c0_parts.append("manifest asserted by the build log ('Fetched N ... across 20 categories', N = kept %s): %s" % (kept, fetched))
    pool_ok = a1 is not None and a1["state"]["pool"] is not None and os.path.exists(os.path.join(ctx.res_dir, "pool_guard_ng_af_s42.out"))
    pool_txt = open(os.path.join(ctx.res_dir, "pool_guard_ng_af_s42.out"), encoding="utf-8", errors="replace").read() if pool_ok else ""
    pool_ok = pool_ok and " OK:" in pool_txt
    c0_parts.append("pool recorded %s and verified by pool_guard --pool --db --id-file: %s" % (a1["state"]["pool"] if a1 else None, pool_ok))
    null_ok = a1 is not None and a1["state"]["built"] and a1.get("null") is not None and a1["null"]["reps"] == REPS
    c0_parts.append("T1 null complete at %d reps on every site: %s" % (REPS, null_ok))
    checks_ok = a1 is not None and a1["state"]["built"] and len(a1["in_leaf"]) == 0
    c0_parts.append("fail-closed checks (held-out in no leaf, vectors, sliceDim, null snapshot): %s" % checks_ok)
    c0 = c0_manifest and pool_ok and null_ok and checks_ok
    lines.append("C0 gate: %s -- %s" % ("HELD" if c0 else "FAILED (criteria depending on the missing piece are UNDETERMINED)", "; ".join(c0_parts)))
    # ---- C1
    c1 = None
    if T1 and T1.get("q1"):
        q = T1["q1"]
        c1 = tribool(q["diff"] > q["spread"] and (q["ci"][0] > 0))          # tribool(): numpy-safe identity dispatch (D1)
        f1p = tribool(q["diff"] < -0.05 and (q["ci"][1] < 0))
        lines.append("C1 (Q1; rule: HELD if NMI(20)_tree - NMI(20)_kmeans0 > seed spread AND the 1,000-resample bootstrap CI excludes 0; FAILED otherwise, F1 fires): %s -- diff %.4f, spread %.4f, CI [%.4f, %.4f], n_eval %d; F1' (tree below k-means by > 0.05 with the CI excluding 0): %s"
                     % ("HELD" if c1 else "FAILED", q["diff"], q["spread"], q["ci"][0], q["ci"][1], q["n_eval"], "FIRES" if f1p else "does not fire"))
        verdict["c1"] = c1; verdict["f1p"] = f1p
    else:
        lines.append("C1 (Q1): UNDETERMINED (T1 not built or Q1 not computed)")
    # ---- C2
    c2 = None
    if T1 and T1.get("q2") and T1["q2"].get("cert"):
        c = T1["q2"]["cert"]["nmi20"]
        # TP20-C2-CONFORMANCE: the four no-contrast conditions of pre-run bracket (e) are evaluated inside
        # c2_decide() BEFORE the registered verdict expression (ruling (a)); on a draw WITH a contrast the line it
        # returns is the one this readout has always printed, character for character.
        c2, c2_lines, c2_fields = c2_decide(c)
        lines.extend(c2_lines)
        verdict.update(c2_fields)
    else:
        lines.append("C2 (Q2): UNDETERMINED (T1 not built, or no complete site null)")
        lines.append(F2_NOT_FIRED)   # ruling (c): F2 is recorded NOT FIRED on EVERY UNDETERMINED path, not only the no-contrast one
        verdict["c2"] = None; verdict["f2"] = False
    # ---- C3 (T1 of record; T1b beside)
    def c3_of(R, name):
        if R is None or not R["q3"]["built"]:
            return "FAILED", "%s not built (F3 fires%s)" % (name, "; T2 runs" if name == "T1" else "")
        q = R["q3"]
        if q.get("cert") is None:
            return "UNDETERMINED", "%s built (leaves %d) but no complete site null" % (name, q["leaves"])
        ok = q["leaves"] > 20 and q["root_cert"] and len(q["d1_cert"]) >= 1
        if ok:
            return "HELD", "%s leaves %d > 20; root certified; depth-1 certified %d of %d" % (name, q["leaves"], len(q["d1_cert"]), len(q["d1_sites"]))
        if q["leaves"] > 7:
            return "PARTIAL", "%s leaves %d (> 7) but leaves > 20: %s, root certified: %s, depth-1 certified: %d of %d" % (name, q["leaves"], q["leaves"] > 20, q["root_cert"], len(q["d1_cert"]), len(q["d1_sites"]))
        return "FAILED", "%s built with leaves %d <= 7 (F3 fires; T2 runs)" % (name, q["leaves"])
    c3, c3txt = c3_of(T1, "T1")
    lines.append("C3 (Q3; rule: HELD if T1 builds with > 20 leaves AND the root and at least one depth-1 site certify; PARTIAL if T1 builds (> 7 leaves) but fails either clause; FAILED if T1 is not built): %s -- %s" % (c3, c3txt))
    verdict["c3"] = c3
    c3b, c3btxt = c3_of(T1b, "T1b")
    lines.append("C3 beside, T1b (same clauses, its own null at its own bar): %s -- %s" % (c3b, c3btxt))
    verdict["c3b"] = c3b
    if T1b and T1b["q3"]["built"] and T1b["q3"].get("cert") is not None:
        agree = T1b["q3"].get("sepbar") is not None and abs(T1b["q3"]["sepbar"] - ARM4_NULL["bar"]) < 1e-9
        lines.append("T1b comparability: T1b's null bar = %s (from sitenull_ng_af_bareq512_s42.out [SEPBAR]); %s used bar %.4f at slice %d (%s): the two certified counts (T1b %d of %d vs arm 4 %d of %d) are %s"
                     % ("%.4f" % T1b["q3"]["sepbar"] if T1b["q3"].get("sepbar") is not None else "NOT RECORDED", ARM4_NULL["arm"], ARM4_NULL["bar"], ARM4_NULL["slice"], ARM4_NULL["how"],
                        T1b["q3"]["cert"], T1b["q3"]["null_sites"], ARM4_NULL["certified"], ARM4_NULL["sites"], "COMPARED (nulls agree in bar)" if agree else "NOT COMPARED (the nulls differ in bar)"))
    # ---- predictions
    P = []
    def add(pred, ok, detail):
        l, v = score(pred, ok, detail); P.append(l); verdict[pred] = v
    q3t = T1["q3"] if T1 else None
    if q3t and q3t["built"]:
        parts = [("built at 0.025", True), ("leaves 95-175", in_range(q3t["leaves"], 95, 175)), ("sites 80-150", in_range(q3t["sites"], 80, 150)),
                 ("depth 8 reached", q3t["max_depth"] >= 8), ("depth-blocked leaves 2-15", in_range(q3t["depth_blocked"], 2, 15)), ("iterations 12-20", in_range(q3t["iterations"], 12, 20))]
        add("P1", all(ok for _, ok in parts), "; ".join("%s: %s" % (n, "HELD" if ok else "FAILED") for n, ok in parts) + " (leaves %d, sites %d, depth %d, blocked %d, iterations %d)" % (q3t["leaves"], q3t["sites"], q3t["max_depth"], q3t["depth_blocked"], q3t["iterations"]))
    else:
        add("P1", False if T1 else None, "T1 not built" if T1 else "no T1")
    if q3t and q3t.get("cert") is not None:
        rk, ro_, rp = q3t["root_k"], q3t["root_obs"], q3t["root_p95"]
        margin = ro_ / rp if rp else None
        d1rows = [T1["arm_null_rows"][c] for c in q3t["d1_sites"]]
        d1_all_cert = len(q3t["d1_cert"]) == len(q3t["d1_sites"]) and len(q3t["d1_sites"]) >= 1
        parts = [("root k = 2", rk == 2), ("root observed 0.045-0.10", in_range(ro_, 0.045, 0.10)), ("root p95 0.040-0.075", in_range(rp, 0.040, 0.075)),
                 ("root margin 1.1-1.8", in_range(margin, 1.1, 1.8)), ("root certified", q3t["root_cert"]), ("both depth-1 sites certified", d1_all_cert),
                 ("depth-1 observed 0.04-0.10", all(in_range(r["observed"], 0.04, 0.10) for r in d1rows) and bool(d1rows)),
                 ("depth-1 p95 0.030-0.060", all(in_range(r["p95"], 0.030, 0.060) for r in d1rows) and bool(d1rows))]
        add("P2", all(ok for _, ok in parts), "; ".join("%s: %s" % (n, "HELD" if ok else "FAILED") for n, ok in parts) + " (root k %s obs %s p95 %s margin %s; depth-1 sites %d certified %d)" % (rk, ro_, rp, "%.3f" % margin if margin else None, len(q3t["d1_sites"]), len(q3t["d1_cert"])))
        share = q3t["cert"] / q3t["null_sites"] if q3t["null_sites"] else 0.0
        b8 = q3t["bands"][">=800"]; b_lo = [q3t["bands"]["n<200"], q3t["bands"]["200-400"]]
        lo_c = sum(b[0] for b in b_lo); lo_n = sum(b[1] for b in b_lo)
        parts = [("certified share 22-38%%: %.3f (%d/%d)" % (share, q3t["cert"], q3t["null_sites"]), in_range(share, 0.22, 0.38)),
                 ("n >= 800 band 50-75%%: %s" % ("%.3f (%d/%d)" % (b8[0] / b8[1], b8[0], b8[1]) if b8[1] else "no site"), in_range(b8[0] / b8[1], 0.50, 0.75) if b8[1] else None),
                 ("below n 400 near the record's ~10%% (read as 5-15%%): %s" % ("%.3f (%d/%d)" % (lo_c / lo_n, lo_c, lo_n) if lo_n else "no site"), in_range(lo_c / lo_n, 0.05, 0.15) if lo_n else None)]
        oks = [ok for _, ok in parts]
        add("P3", None if any(o is None for o in oks) else all(oks), "; ".join("%s: %s" % (n, verdict_word(ok)) for n, ok in parts))
    else:
        add("P2", None, "no complete T1 null"); add("P3", None, "no complete T1 null")
    if T1 and T1.get("q1"):
        q = T1["q1"]; km0 = q["kmeans"][0]
        k20 = q["k20"][0]; k7 = q["k7"][0]
        parts = [("NMI20 tree 0.42-0.58: %.4f" % q["tree"]["nmi20"], in_range(q["tree"]["nmi20"], 0.42, 0.58)),
                 ("NMI20 k-means k=L 0.44-0.60: %.4f" % km0["nmi20"], in_range(km0["nmi20"], 0.44, 0.60)),
                 ("tree - kmeans0 in [-0.06, +0.02]: %.4f" % q["diff"], in_range(q["diff"], -0.06, 0.02)),
                 ("seed spread 0.005-0.02: %.4f" % q["spread"], in_range(q["spread"], 0.005, 0.02)),
                 ("C1 FAILED: %s" % ("FAILED" if c1 is False else ("HELD" if c1 is True else "n/a")), c1 is False),
                 ("Ward 0.40-0.58: %.4f" % q["ward"]["nmi20"], in_range(q["ward"]["nmi20"], 0.40, 0.58)),
                 ("NMI7 tree 0.35-0.50: %.4f" % q["tree"]["nmi7"], in_range(q["tree"]["nmi7"], 0.35, 0.50)),
                 ("NMI7 k-means 0.36-0.52: %.4f" % km0["nmi7"], in_range(km0["nmi7"], 0.36, 0.52)),
                 ("ARI20 tree 0.18-0.35: %.4f" % q["tree"]["ari20"], in_range(q["tree"]["ari20"], 0.18, 0.35)),
                 ("ARI20 k-means 0.20-0.38: %.4f" % km0["ari20"], in_range(km0["ari20"], 0.20, 0.38)),
                 ("k=20 NMI 0.55-0.70: %.4f" % k20["nmi20"], in_range(k20["nmi20"], 0.55, 0.70)),
                 ("k=20 ARI 0.35-0.55: %.4f" % k20["ari20"], in_range(k20["ari20"], 0.35, 0.55)),
                 ("k=20 purity 0.60-0.75: %.4f" % k20["purity"], in_range(k20["purity"], 0.60, 0.75)),
                 ("k=7 NMI(7) 0.45-0.65: %.4f" % k7["nmi7"], in_range(k7["nmi7"], 0.45, 0.65))]
        add("P4", all(ok for _, ok in parts), "; ".join("%s: %s" % (n, "HELD" if ok else "FAILED") for n, ok in parts))
        rnd = q["random"]
        parts = [("purity tree 0.68-0.82: %.4f" % q["tree"]["purity"], in_range(q["tree"]["purity"], 0.68, 0.82)),
                 ("purity k-means 0.70-0.84: %.4f" % km0["purity"], in_range(km0["purity"], 0.70, 0.84)),
                 ("purity Ward 0.66-0.82: %.4f" % q["ward"]["purity"], in_range(q["ward"]["purity"], 0.66, 0.82)),
                 ("tree at 7 groups 0.80-0.90: %.4f" % q["tree"]["purity7"], in_range(q["tree"]["purity7"], 0.80, 0.90)),
                 ("random purity 0.10-0.17: %s" % ",".join("%.3f" % r["purity"] for r in rnd), all(in_range(r["purity"], 0.10, 0.17) for r in rnd)),
                 ("random NMI20 0.03-0.08: %s" % ",".join("%.3f" % r["nmi20"] for r in rnd), all(in_range(r["nmi20"], 0.03, 0.08) for r in rnd)),
                 ("random ARI 0.000 +- 0.003: %s" % ",".join("%.4f" % r["ari20"] for r in rnd), all(abs(r["ari20"]) <= 0.003 for r in rnd))]
        add("P5", all(ok for _, ok in parts), "; ".join("%s: %s" % (n, "HELD" if ok else "FAILED") for n, ok in parts))
        h = q["hdbscan"]
        if h.get("k", 0) > 0:
            parts = [("train noise 35-80%%: %.3f" % h["noise"], in_range(h["noise"], 0.35, 0.80)), ("k 8-40: %d" % h["k"], in_range(h["k"], 8, 40)), ("held-out NMI20 0.35-0.60: %.4f" % h["nmi20"], in_range(h["nmi20"], 0.35, 0.60))]
            add("P6", all(ok for _, ok in parts), "; ".join("%s: %s" % (n, "HELD" if ok else "FAILED") for n, ok in parts))
        else:
            add("P6", False, "HDBSCAN found no cluster (noise %.3f)" % h["noise"])
    else:
        for p in ("P4", "P5", "P6"):
            add(p, None, "Q1 not computed")
    if T1 and T1.get("q2"):
        q = T1["q2"]
        k = q["d1_k"]
        p7range = (0.50, 0.70) if k in (3, 4) else (0.35, 0.60)
        sp = q["p7_split"]
        parts = [("depth-1 7-group purity %.2f-%.2f (k=%d): %.4f" % (p7range[0], p7range[1], k, q["d1_purity7"]), in_range(q["d1_purity7"], *p7range)),
                 ("depth-1 20-label purity 0.10-0.25: %.4f" % q["d1_purity20"], in_range(q["d1_purity20"], 0.10, 0.25)),
                 ("technical vs discursive (registrar's rule: comp.* majority cell %s (%.3f) != talk.* majority cell %s (%.3f); rec.* cell %s share %.3f)" % (sp["comp"][0], sp["comp"][1], sp["talk"][0], sp["talk"][1], sp["rec"][0], sp["rec"][1]), sp["held"]),
                 ("best 7-group depth 3-4: %d" % q["best7_depth"], in_range(q["best7_depth"], 3, 4))]
        add("P7", all(ok for _, ok in parts), "; ".join("%s: %s" % (n, "HELD" if ok else "FAILED") for n, ok in parts))
        lb = q["label_best"]
        tri = sum(1 for l in RELIGION_TRIAD if l in lb and lb[l][1] < 0.40)
        ten = sum(1 for l in P8_TEN if l in lb and lb[l][1] >= 0.5)
        share50 = q["leaves_j50"] / max(1, len(q["leaf_j"]))
        parts = [("median best depth 3-5 (point 4): %.1f" % q["label_median_depth"], in_range(q["label_median_depth"], 3, 5)),
                 ("median best J 0.40-0.60: %.4f" % q["label_median_j"], in_range(q["label_median_j"], 0.40, 0.60)),
                 ("religion triad J < 0.40 for >= 2 of 3: %d" % tri, tri >= 2),
                 ("comp.os.ms-windows.misc < 0.45: %.4f" % lb.get("comp.os.ms-windows.misc", (None, -1))[1], lb.get("comp.os.ms-windows.misc", (None, 1))[1] < 0.45),
                 ("comp.sys.ibm.pc.hardware < 0.45: %.4f" % lb.get("comp.sys.ibm.pc.hardware", (None, -1))[1], lb.get("comp.sys.ibm.pc.hardware", (None, 1))[1] < 0.45),
                 (">= 6 of the ten at J >= 0.5: %d" % ten, ten >= 6),
                 ("leaves at J >= 0.5 15-35%%: %.3f" % share50, in_range(share50, 0.15, 0.35))]
        add("P8", all(ok for _, ok in parts), "; ".join("%s: %s" % (n, "HELD" if ok else "FAILED") for n, ok in parts))
        if q.get("cert"):
            c = q["cert"]["nmi20"]
            parts = [("raw gap +0.10..+0.30: %s" % ("%.4f" % c["raw"] if c["raw"] is not None else "n/a"), in_range(c["raw"], 0.10, 0.30)),
                     ("depth-stratified gap +0.00..+0.10: %s" % ("%.4f" % c["strat"] if c["strat"] is not None else "n/a"), in_range(c["strat"], 0.0, 0.10)),
                     ("permutation p in [0.02, 0.6]: %s" % ("%.4f" % c["p"] if c["p"] is not None else "n/a"), in_range(c["p"], 0.02, 0.6)),
                     ("C2 FAILED: %s" % ("FAILED" if c2 is False else ("HELD" if c2 is True else "n/a")), c2 is False)]
            add("P9", all(ok for _, ok in parts), "; ".join("%s: %s" % (n, "HELD" if ok else "FAILED") for n, ok in parts))
        else:
            add("P9", None, "no complete T1 null")
    else:
        for p in ("P7", "P8", "P9"):
            add(p, None, "Q2 not computed")
    if manifest and T1 and T1.get("q1"):
        c = manifest["counts"]; q = T1["q1"]
        sens = q.get("sens_leak documents", {})
        dpp = abs(100 * (sens["tree"]["purity"] - q["tree"]["purity"])) if sens.get("tree") else None
        parts = [("leak documents 1-4%% of held-out: %.4f" % q["leak_share"], in_range(q["leak_share"], 0.01, 0.04)),
                 ("purity change when excluded < 0.5 pp: %s" % ("%.3f pp" % dpp if dpp is not None else "n/a"), dpp is not None and dpp < 0.5),
                 ("short-dropped 2-5%% of %d: %d = %.4f" % (c["raw"], c["dropped_short"], c["dropped_short"] / c["raw"]), in_range(c["dropped_short"] / c["raw"], 0.02, 0.05)),
                 ("duplicate-dropped 1-4%%: %d = %.4f" % (c["dropped_duplicate"], c["dropped_duplicate"] / c["raw"]), in_range(c["dropped_duplicate"] / c["raw"], 0.01, 0.04))]
        add("P10", all(ok for _, ok in parts), "; ".join("%s: %s" % (n, "HELD" if ok else "FAILED") for n, ok in parts))
    else:
        add("P10", None, "no manifest or no Q1")
    if T1b and T1 and T1["q3"]["built"] and T1b["q3"]["built"]:
        q, qb = T1["q3"], T1b["q3"]
        parts = [("T1b builds", True), ("more leaves than T1: %d vs %d" % (qb["leaves"], q["leaves"]), qb["leaves"] > q["leaves"])]
        if q.get("cert") is not None and qb.get("cert") is not None:
            parts.append(("lower certified share than T1: %.3f vs %.3f (own nulls at own bars; descriptive)" % (qb["cert"] / qb["null_sites"], q["cert"] / q["null_sites"]), qb["cert"] / qb["null_sites"] < q["cert"] / q["null_sites"]))
        else:
            parts.append(("certified share comparison", None))
        if T1.get("q1") and T1b.get("q1"):
            d = abs(T1b["q1"]["tree"]["nmi20"] - T1["q1"]["tree"]["nmi20"])
            parts.append(("NMI(20) within 0.03 of T1's: |%.4f - %.4f| = %.4f" % (T1b["q1"]["tree"]["nmi20"], T1["q1"]["tree"]["nmi20"], d), d <= 0.03))
        oks = [ok for _, ok in parts]
        add("P11", None if any(o is None for o in oks) else all(oks), "; ".join("%s: %s" % (n, verdict_word(ok)) for n, ok in parts))
    elif T1b:
        add("P11", False, "T1b not built (P 0.8 predicted a build)" if not T1b["q3"]["built"] else "T1 not built; T1b built with %s leaves" % T1b["q3"]["leaves"])
    else:
        add("P11", None, "no T1b")
    t = chain_times(ctx)
    parts = [("embedding + T1 build 45-80 min", t.get(("ng_af_s42", "BUILD"))), ("T1 null 55-90 min", t.get(("ng_af_s42", "SITENULL"))), ("T1b null 40-90 min", t.get(("ng_af_bareq512_s42", "SITENULL"))),
             ("smoke 3 min (read as <= 6)", t.get(("ag_news_smoke_s42", "BUILD"))), ("readout 6-15 min", readout_minutes)]
    ranges = [(45, 80), (55, 90), (40, 90), (0, 6), (6, 15)]
    oks = [None if v is None else in_range(v, lo, hi) for (_, v), (lo, hi) in zip(parts, ranges)]
    add("P12", None if any(o is None for o in oks) else all(oks), "; ".join("%s: %s (%s)" % (n, "%.1f min" % v if v is not None else "not in chain.log", verdict_word(ok)) for (n, v), ok in zip(parts, oks)))
    lines.append("PREDICTIONS (tree-construction-specialist's ranges; scored where computed):")
    lines.extend(P)
    # ---- verdict sentences (only under the registered conditions)
    V = []
    # the three verdicts are dispatched by identity below, so their domain is asserted here: anything outside it is a
    # loud refusal, never a silently missing sentence of record (post-run review 2026-09-23, D1).
    if not (c1 is True or c1 is False or c1 is None):
        die("C1 verdict %r of type %s is not True / False / None" % (c1, type(c1).__name__))
    if not (c2 is True or c2 is False or c2 is None):
        die("C2 verdict %r of type %s is not True / False / None" % (c2, type(c2).__name__))
    if c3 not in ("HELD", "PARTIAL", "FAILED", "UNDETERMINED"):
        die("C3 verdict %r is not HELD / PARTIAL / FAILED / UNDETERMINED" % (c3,))
    if c3 == "HELD" and c1 is False:
        V.append("On a corpus with known topics the anchor-free recipe of record builds and certifies, and partitions the embedding space no better than k-means at the same number of parts; its value on this corpus is the split discipline, the support per cell and the certificate, not the partition.")
    if c1 is True:
        q = T1["q1"]; k20 = T1["q1"]["k20"][0]
        V.append("On a corpus with known topics the anchor-free recipe of record builds%s, and partitions the embedding space better than k-means at the same number of parts by %.4f NMI [%.4f, %.4f] (k = 20 reference row beside: k-means k=20 NMI(20) %.4f, ARI %.4f, purity %.4f; the tree has L = %d leaves)."
                 % (" and certifies" if c3 == "HELD" else "", q["diff"], q["ci"][0], q["ci"][1], k20["nmi20"], k20["ari20"], k20["purity"], q["L"]))
    V.append(c2_sentence(c2, verdict.get("c2_gap"), verdict.get("c2_p"), verdict.get("c2_no_contrast")))   # TOTAL over the three verdicts (D1); bracket (e)'s reason where there is no contrast
    if c3 == "PARTIAL":
        V.append("The recipe of record builds on 20NG at bar 0.025 (> 7 leaves) but does not certify the root and a depth-1 site with > 20 leaves (C3 PARTIAL; F3 sentences as registered apply to the failed clause).")
    if c3 == "FAILED":
        V.append("The recipe of record does not build on 20NG at bar 0.025 (F3): the transfer of the flat bar is overturned; separation_null_by_size.md L20-23 narrows to 'unchanged for MMLU-Pro at this slice and N'; T2 measures whether the bar-equalised rule restores a build.")
    if T1b:
        V.append("The per-corpus pair (512 / 0.0145) %s on this corpus." % ("builds" if T1b["q3"]["built"] else "does not build"))
    lines.append("VERDICT (the only sentences of record; printed only under the registered conditions):")
    lines.extend("  " + v for v in V) if V else lines.append("  (no verdict sentence: its conditions are not met)")
    out.extend(lines)
    return verdict


# ----------------------------------------------------------------------------------------------- analysis driver
def analyse_arm(ctx, arm, out, bar_retuned=False):
    a = load_arm(ctx, arm)
    a["run_dir"] = ctx.run_dir(arm)
    st = a["state"]
    tag = " [bar re-tuned: T2's rows are never compared to T1's or to the record's]" if bar_retuned else ""
    out.append("=" * 120)
    out.append("ARM %s (%s)%s: build.out %s; snapshot %s; built %s; pool %s; closure %s; slice line %s; trickle Total Queries %s"
               % (arm, a["spec"]["kind"], tag, "present" if st["exists"] else "ABSENT", st["snapshot"], st["built"], st["pool"], st["closure"], st["slice_line"], st["trickle_total"]))
    R = dict(arm=arm, q3=None, q1=None, q2=None)
    if not st["built"]:
        R["q3"] = q3(a, out)
        return R
    out.append("  denominators: ingest rows %d (distinct texts %d); TRAIN in leaves %d distinct ids (%d leaf slots); held-out %d distinct texts (%d reserved ids); neither (closure routing-only / dropped) %d; leaves %d; sites %d; held-out texts inside a leaf: %d (must be 0)"
               % (a["ing"]["rows"], a["ing"]["distinct_texts"], len(a["train_qids"]), a["leaf_slots"], len(a["held_texts"]), sum(len(v) for v in a["reserved"].values()), a["neither"], len(a["leaf_ids"]), len(a["sites"]), len(a["in_leaf"])))
    if a["in_leaf"]:
        die("%s: %d held-out texts are members of a leaf (TRAIN-ONLY violated)" % (arm, len(a["in_leaf"])))
    # the TOML must carry the arm's registered bar (T1 / T1b / smoke); T2 has none registered (I4 computes it)
    if a["toml_bar"] is not None and a["spec"]["bar"] is not None and abs(a["toml_bar"] - a["spec"]["bar"]) > 1e-9:
        die("%s: TOML bar %.4f != the registered %.4f" % (arm, a["toml_bar"], a["spec"]["bar"]))
    if a["null"] is None:
        # an ABSENT site null on a BUILT arm is UNDETERMINED, not a refusal: C0's null clause reads FAILED, C2 / C3
        # and P2 / P3 read UNDETERMINED for what depends on it, and the outcome is still written. A PARTIAL null
        # (reps != %d on any row) or mixed snapshot ids still REFUSES in load_arm, as registered.
        if os.path.exists(ctx.site_null(arm)):
            die("%s: site null %s exists but could not be read" % (arm, rel(ctx.site_null(arm))))
        out.append("  site null %s ABSENT: this arm's certification is UNDETERMINED (C0's null clause FAILED; every "
                   "criterion and prediction that reads the null is UNDETERMINED); a partial null still refuses" % rel(ctx.site_null(arm)))
    else:
        # the null must have run at the ARM's bar (I5). T2's bar is not registered: it is the one the chain computed
        # (I4) and wrote into its TOML, so it is read from the TOML AND from the null log's [SEPBAR] line and the two
        # must agree -- without this a T2 null run at the harness default 0.025 would pass unchecked.
        want_bar = a["spec"]["bar"] if a["spec"]["bar"] is not None else a["toml_bar"]
        if a["spec"]["bar"] is None:
            if a["toml_bar"] is None:
                die("%s: no proposalSeparationBar in %s: the bar this arm's null had to run at (I4 / I5) cannot be read"
                    % (arm, a["spec"]["toml"]))
            if a["sepbar"] is None:
                die("%s: no [SEPBAR] line in %s: the null's bar cannot be checked against the chain's computed bar %.4f (I4 / I5)"
                    % (arm, rel(ctx.sitenull_out(arm)), a["toml_bar"]))
        if a["sepbar"] is None:
            out.append("  NOTE: no [SEPBAR] line in %s (the null's bar is not recorded there)" % rel(ctx.sitenull_out(arm)))
        elif want_bar is not None and abs(a["sepbar"] - want_bar) > 1e-9:
            die("%s: the site null ran at bar %.4f, the arm's bar is %.4f%s"
                % (arm, a["sepbar"], want_bar, "" if a["spec"]["bar"] is not None else " (not registered: computed by the chain (I4) and read from %s)" % a["spec"]["toml"]))
    vec = load_vectors(ctx, a["train_texts"] + a["held_texts"])
    missing = [t for t in a["train_texts"] + a["held_texts"] if t not in vec]
    if missing:
        die("%s: %d of %d texts have no vector in %s" % (arm, len(missing), len(a["train_texts"]) + len(a["held_texts"]), rel(ctx.emb_db)))
    out.append("  vectors: %d of %d texts present (%d-d); slice %d" % (len(vec), len(a["train_texts"]) + len(a["held_texts"]), len(next(iter(vec.values()))), a["spec"]["slice"]))
    R["q3"] = q3(a, out)
    R["arm_null_rows"] = a["null"]["rows"] if a["null"] is not None else {}   # {} when the null is absent (UNDETERMINED)
    R["q1"] = q1(a, vec, out, boot=ctx.boot)
    R["q2"] = q2(a, vec, out, R["q1"], perm=ctx.perm)
    return R


def dry_run(ctx, arm):
    print("[TOPIC-PARTITION] pool: the corpus's own split (no arena pool read or written); DRY RUN arm %s; script_sha %s" % (arm, script_sha()))
    spec = ARMS[arm]
    for p, name in ((ctx.build_out(arm), "build log"), (os.path.join(ctx.run_dir(arm), "dag_snapshots.jsonl"), "dag_snapshots.jsonl"),
                    (os.path.join(ctx.run_dir(arm), "diagnostics", "proposals.csv"), "proposals.csv"), (ctx.site_null(arm), "site null CSV"),
                    (ctx.sitenull_out(arm), "site null stdout"), (ctx.snap_db, "snapshots.db"), (ctx.emb_db, "embeddings_cache.db"), (ctx.ingest_db(arm), "ingest DB"),
                    (os.path.join(ctx.root, spec["toml"]), "TOML"), (ctx.outcome, "outcome file (must NOT exist for --run)")):
        print("  %-40s %s %s" % (name, "present" if os.path.exists(p) else "ABSENT ", rel(p)))
    st = build_state(ctx.build_out(arm))
    print("  build: exists %s snapshot %s leaves %s guard_fired %s pool %s closure %s fetched %s slice %s trickle TotalQueries %s anchor-free depth-1 %s -> built %s"
          % (st["exists"], st["snapshot"], st["leaves"], st["guard_fired"], st["pool"], st["closure"], st["fetched"], st["slice_line"], st["trickle_total"], st["anchor_free_end"], st["built"]))
    if spec["kind"] == "smoke":
        print("  smoke readouts: built %s / pool recorded %s / snapshot saved %s / trickle ran %s" % (st["built"], st["pool"] is not None, st["snapshot"] is not None, st["trickle_total"] is not None))
    if not st["built"]:
        print("  arm not built: nothing else to read")
        return 0
    a = load_arm(ctx, arm)
    print("  ingest %s: rows %d distinct texts %d labels %d" % (spec["table"], a["ing"]["rows"], a["ing"]["distinct_texts"], len(a["ing"]["labels"])))
    print("  tree: leaves %d (dim %d, iteration %d, depth %d); sites %d; TRAIN %d distinct ids over %d leaf slots; held-out %d distinct texts (%d reserved ids over %d keys); neither %d; held-out in a leaf %d"
          % (len(a["leaf_ids"]), a["tree"]["dim"], a["tree"]["iteration"], a["tree"]["depth"], len(a["sites"]), len(a["train_qids"]), a["leaf_slots"], len(a["held_texts"]),
             sum(len(v) for v in a["reserved"].values()), len(a["reserved"]), a["neither"], len(a["in_leaf"])))
    if a["null"] is not None:
        print("  site null: %d sites, %d certified (cert_site_p95), reps %d, snapshot %s, [SEPBAR] bar %s" % (a["null"]["sites"], len(a["null"]["cert"]), a["null"]["reps"], a["null"]["snapshot"], a["sepbar"]))
    else:
        print("  site null: absent or partial (read_site_null would refuse)")
    if os.path.exists(ctx.emb_db):
        con = ro(ctx.emb_db)
        try:
            n_emb = con.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
            want = set(a["train_texts"] + a["held_texts"])
            have = 0
            for (t,) in con.execute("SELECT query FROM embeddings"):
                if t in want:
                    have += 1
        finally:
            con.close()
        print("  vectors: %d of %d train+held-out texts present in embeddings (%d rows); missing %d" % (have, len(want), n_emb, len(want) - have))
    print("  TOML bar %s; registered bar %s; nothing computed, nothing written" % (a["toml_bar"], spec["bar"]))
    return 0


def run_all(ctx, manifest_path=None):
    t0 = time.time()
    if os.path.exists(ctx.outcome):
        die("%s exists (write-once); nothing recomputed" % rel(ctx.outcome))
    out = []
    out.append("TOPIC-PARTITION-20NG readout (registration docs/judge_v2_program.md L10030-L10390, commit 6aa2a0d); script_sha %s; date %s; %d-rep site nulls; %d bootstrap resamples; %d permutations; rng seed %d"
               % (script_sha(), datetime.date.today().isoformat(), REPS, ctx.boot, ctx.perm, RNG_SEED))
    out.append("pool: the corpus's own split (seed 42, ratio 0.30, per label) recorded in the separate ingest DB; no arena pool (p2dca, paeec) read or written; zero judge calls")
    manifest = None
    mp = manifest_path or (ctx.ingest_db("ng_af_s42") + ".manifest.json")
    if os.path.exists(mp):
        manifest = json.load(open(mp, encoding="utf-8"))
        out.append("ingest manifest %s: raw %d short %d dup %d kept %d leak %d sha %s" % (rel(mp), manifest["counts"]["raw"], manifest["counts"]["dropped_short"], manifest["counts"]["dropped_duplicate"], manifest["counts"]["kept"], manifest["counts"]["leak_count"], manifest["sha256_id_question_category"]))
    else:
        out.append("ingest manifest %s ABSENT (P10 UNDETERMINED)" % rel(mp))
    for arm in ("ng_af_s42", "ng_af_bareq512_s42"):
        if not os.path.exists(ctx.build_out(arm)):
            die("arm %s has no build log %s (all arms must be present)" % (arm, rel(ctx.build_out(arm))))
    results = {}
    arms = {}
    for arm in ("ng_af_s42", "ng_af_bareq512_s42"):
        results[arm] = analyse_arm(ctx, arm, out)
        arms[arm] = load_arm(ctx, arm, need_null=True)
    t1_built = results["ng_af_s42"]["q3"]["built"] and (results["ng_af_s42"]["q3"]["leaves"] or 0) > 7
    if os.path.exists(ctx.build_out("ng_af_bar_eq_s42")):
        if t1_built:
            die("T2 build log exists although T1 built with %s leaves (> 7): T2 must not run (I4)" % results["ng_af_s42"]["q3"]["leaves"])
        results["ng_af_bar_eq_s42"] = analyse_arm(ctx, "ng_af_bar_eq_s42", out, bar_retuned=True)
    elif not t1_built:
        # the registered F3 path with no I4 input (the chain's t2_bar found no refused depth-1 row): the outcome is
        # still WRITTEN -- C3 reads FAILED and F3 fires, T2 and everything that reads T1's tree read UNDETERMINED --
        # so that the registered outcome can be scored from a file instead of from an aborted run.
        note = ("T1 is not built (or <= 7 leaves) and T2's build log is absent: the contingency (I4) did not run; "
                "T2 UNDETERMINED; C3 FAILED stands and F3 fires")
        t2b = os.path.join(ctx.res_dir, "t2_bar.out")
        if os.path.exists(t2b):
            note += "; %s: %s" % (rel(t2b), open(t2b, encoding="utf-8", errors="replace").read().strip().replace("\n", " | "))
        else:
            note += "; %s absent (the I4 rule had no input)" % rel(t2b)
        out.append("=" * 120)
        out.append("T2 CONTINGENCY: " + note)
        print("[TOPIC-PARTITION] NOTE: " + note)
    readout_minutes = (time.time() - t0) / 60.0
    out.append("=" * 120)
    verdict = criteria_and_predictions(ctx, arms, results, out, manifest, readout_minutes)
    out.append("readout wall time %.1f min" % ((time.time() - t0) / 60.0))
    text = "\n".join(out) + "\n"
    print(text)
    os.makedirs(os.path.dirname(ctx.outcome), exist_ok=True)
    fd = os.open(ctx.outcome, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("[TOPIC-PARTITION] wrote %s (write-once)" % rel(ctx.outcome))
    return verdict


# ----------------------------------------------------------------------------------------------- selftest
def write_text(path, line):
    """selftest fixture helper: one line + LF."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(line + "\n")


def selftest():
    """Synthetic planted hierarchy: 7 groups x 20 labels in 256-d; a synthetic tree jsonl + a fake snapshot graph +
    a fake ingest DB + a fake embeddings DB + a fake site-null CSV in a temp dir; asserts the metrics recover the
    planted structure and that every fail-closed check fires."""
    rs = np.random.RandomState(7)
    dim = 256
    tmp = tempfile.mkdtemp(prefix="tp_selftest_")
    root = tmp
    res_dir = os.path.join(tmp, "experiment_results", "topic_partition")
    arm = "ng_af_s42"; spec = ARMS[arm]
    run_dir = os.path.join(res_dir, spec["dir"], "seed_42")
    os.makedirs(os.path.join(run_dir, "diagnostics"))
    # planted geometry
    gcent = {g: rs.randn(dim) for g in GROUPS_7}
    lcent = {l: gcent[GROUP_OF[l]] + 0.6 * rs.randn(dim) for l in LABELS_20}
    docs = []   # (text, label, side)
    for l in LABELS_20:
        for j in range(52):
            v = lcent[l] + 0.9 * rs.randn(dim)
            docs.append(("synthetic %s doc %03d %s" % (l, j, "x" * (j % 7)), l, "train" if j < 40 else "held"))
    texts = [t for t, _, _ in docs]
    vec = {}
    for (t, l, _) in docs:
        v = lcent[l] + 0.9 * rs.randn(dim)
        vec[t] = v / np.linalg.norm(v)
    # ingest DB (Design N)
    ing_db = os.path.join(root, spec["db"])
    con = sqlite3.connect(ing_db)
    con.executescript("CREATE TABLE twenty_newsgroups (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, category TEXT, cot_content TEXT, options TEXT, answer TEXT);"
                      "CREATE TABLE eval_question_link (question_id INTEGER PRIMARY KEY, mmlu_pro_row_id INTEGER, question_text TEXT, has_embedding INTEGER DEFAULT 0);"
                      "CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, text TEXT);")
    for k, (t, l, _) in enumerate(docs, start=1):
        con.execute("INSERT INTO twenty_newsgroups VALUES (?, ?, ?, '', '[]', ?)", (k, t, l, l))
        con.execute("INSERT INTO eval_question_link VALUES (?, ?, ?, 0)", (k, k, t))
        con.execute("INSERT INTO corpus_questions VALUES (?, ?)", (spec["offset"] + k, t))
    con.commit(); con.close()
    manifest = dict(counts=dict(raw=1040, dropped_short=30, dropped_duplicate=20, kept=len(docs), leak_count=15), sha256_id_question_category="selftest")
    json.dump(manifest, open(ing_db + ".manifest.json", "w", encoding="utf-8"))
    # embeddings DB (big-endian float32; 512-d so the 256 slice is a proper prefix)
    emb_db = os.path.join(root, "embeddings_cache.db")
    con = sqlite3.connect(emb_db)
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    for t, v in vec.items():
        full = np.concatenate([v, 0.01 * rs.randn(dim)])
        con.execute("INSERT INTO embeddings VALUES (?, ?)", (t, struct.pack(">%df" % len(full), *full.tolist())))
    con.commit(); con.close()
    # tree: root -> 7 group nodes -> label leaves (single-label groups are depth-1 leaves); one label split into 2 leaves
    train = [(t, l) for t, l, s in docs if s == "train"]; held = [(t, l) for t, l, s in docs if s == "held"]
    nodes = {}; nid = [0]
    def new(label, depth, parent):
        nid[0] += 1
        i = "n%08d" % nid[0]
        nodes[i] = dict(id=i, label=label, depth=depth, childIds=[], parentIds=[parent] if parent else [], queryIds=[], vmfMu=None, sliceDim=dim, dasguptaDeltaNorm=0.0)
        if parent:
            nodes[parent]["childIds"].append(i)
        return i
    r = new("TWENTY_NEWSGROUPS", 0, None)
    split_label = "sci.space"
    for g in GROUPS_7:
        labs = [l for l in LABELS_20 if GROUP_OF[l] == g]
        if len(labs) == 1:
            leaf = new(labs[0], 1, r)
            nodes[leaf]["queryIds"] = [afr.qid(t) for t, l in train if l == labs[0]]
        else:
            gn = new(g, 1, r)
            for l in labs:
                if l == split_label:
                    sn = new(l, 2, gn)
                    members = [t for t, ll in train if ll == l]
                    for half in (members[:20], members[20:]):
                        leaf = new(l + "/half", 3, sn)
                        nodes[leaf]["queryIds"] = [afr.qid(t) for t in half]
                else:
                    leaf = new(l, 2, gn)
                    nodes[leaf]["queryIds"] = [afr.qid(t) for t, ll in train if ll == l]
    text_of_qid = {afr.qid(t): t for t, _ in train}
    def mu(i):
        n = nodes[i]
        if n["childIds"]:
            M = np.stack([mu(c) for c in n["childIds"]]).mean(axis=0)
        else:
            M = np.stack([vec[text_of_qid[q]][:dim] for q in n["queryIds"]]).mean(axis=0)
        n["vmfMu"] = (M / np.linalg.norm(M)).tolist()
        n["dasguptaDeltaNorm"] = 0.05 if n["childIds"] else 0.0
        return M / np.linalg.norm(M)
    mu(r)
    def subtree(i):
        n = nodes[i]
        return len(n["queryIds"]) if not n["childIds"] else sum(subtree(c) for c in n["childIds"])
    snap = dict(iteration=5, nodes=[dict(id=i, label=n["label"], depth=n["depth"], isLeaf=not n["childIds"], childIds=n["childIds"], parentIds=n["parentIds"],
                                         vmfMu=n["vmfMu"], sliceDim=dim, directQueries=len(n["queryIds"]), subtreeQueries=subtree(i)) for i, n in nodes.items()])
    with open(os.path.join(run_dir, "dag_snapshots.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps(snap) + "\n")
    sid = "20260922_000000_Selftest"
    reserved = defaultdict(list)
    for k, (t, l, s) in enumerate(docs, start=1):
        if s == "held":
            reserved[l][:0] = []
            reserved[l].append(spec["offset"] + k)
    snap_db = os.path.join(root, "snapshots.db")
    con = sqlite3.connect(snap_db)
    con.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, timestamp TEXT, description TEXT, graph TEXT, metrics TEXT, settings TEXT, log_uuid TEXT, reserved_queries TEXT, config TEXT)")
    con.execute("INSERT INTO snapshots VALUES (?, '', '', ?, '', '', '', ?, '')", (sid, json.dumps(dict(rootId=r, nodes=list(nodes.values()), version=1)), json.dumps(reserved)))
    con.commit(); con.close()
    # build log, proposals.csv, site null, sitenull out, chain log, pool_guard out
    with open(os.path.join(res_dir, spec["dir"] + ".build.out"), "w", encoding="utf-8") as f:
        f.write("DatasetFetcher - Fetched %d 20 Newsgroups queries across 20 categories.\n[POOL] recorded pselftest0000000 (seed=42, gate=10, closedByContent=0); nothing activated\n"
                "[SLICE] embedding slice width = 256, split PCA dropTop=0 whiten=false\n[ANCHOR-FREE] construction ended with 7 emergent depth-1 nodes under the root (no category anchors)\n"
                "Successfully generated and saved snapshot. Snapshot ID: %s\n  - Total Queries: %d\nHeld-out leaf support (MAIN): leaves=%d, top1\n" % (len(docs), sid, len(held), sum(1 for n in nodes.values() if not n["childIds"])))
    with open(os.path.join(run_dir, "diagnostics", "proposals.csv"), "w", encoding="utf-8", newline="") as f:
        f.write("iter,type,site_id,site_label,dJ,SE_dJ,z,dV,decision,reason,n_site\n1,GROW,%s,TWENTY_NEWSGROUPS,0.05,0.001,50,7,ACCEPTED,,0\n"
                "2,GROW,%s,comp,,,,,NO_PROPOSAL,\"min_pair_sep_below_bar(sep=0.01900,bar=0.02500,k=2,emK=2)\",200\n" % (r, nodes[r]["childIds"][0]))
    sites = [i for i, n in nodes.items() if len(n["childIds"]) >= 2]
    with open(os.path.join(res_dir, "site_null_%s.csv" % spec["dir"]), "w", encoding="utf-8", newline="") as f:
        f.write("snapshot_id,node_id,label,depth,n,k,observed_sep,site_null_p50,site_null_p95,q_site,site_reach_pct,site_accept_pct,defl_dims,defl_null_p50,defl_null_p95,q_deflated,defl_reach_pct,defl_accept_pct,cert_site_p95,cert_deflated_p95,trunk_member,feasibility,reps\n")
        for s in sites:
            n = subtree(s); cert = nodes[s]["depth"] <= 1 and nodes[s]["label"] != "talk"   # talk (depth 1) and the sci.space split (depth 2) uncertified
            f.write('"%s","%s","%s",%d,%d,%d,0.060000,0.030000,0.035000,0.0000,100.0,100.0,1,0.02,0.021,0.0,100.0,0.0,%s,%s,%s,OK,%d\n' % (sid, s, nodes[s]["label"], nodes[s]["depth"], n, len(nodes[s]["childIds"]), "true" if cert else "false", "true" if cert else "false", "true" if cert else "false", REPS))
    with open(os.path.join(res_dir, "sitenull_%s.out" % spec["dir"]), "w", encoding="utf-8") as f:
        f.write("[SEPBAR] proposalSeparationBar=0.025 (-DsepBar absent -> default 0.025); sliceDim=256 dropTop=0 whiten=false reps=300\n")
    with open(os.path.join(res_dir, "pool_guard_ng_af_s42.out"), "w", encoding="utf-8") as f:
        f.write("pool pselftest0000000 OK: id file hashes to it; reserved_pool rows agree\n")
    with open(os.path.join(res_dir, "chain.log"), "w", encoding="utf-8") as f:
        f.write("[10:00:00] ng_af_s42 BUILD start\n[10:50:00] ng_af_s42 BUILD exit 0\n[10:50:10] ng_af_s42 SITENULL start\n[12:00:10] ng_af_s42 SITENULL exit 0\n")
    os.makedirs(os.path.join(root, "experiment_configs", "topic_partition"))
    with open(os.path.join(root, spec["toml"]), "w", encoding="utf-8") as f:
        f.write("proposalSeparationBar = 0.025\n")
    ctx = Ctx(root=root, res_dir=res_dir, snap_db=snap_db, emb_db=emb_db, outcome=os.path.join(res_dir, "topic_partition_outcome.txt"), boot=200, perm=200)
    checks = 0
    print("[TOPIC-PARTITION] selftest: %d docs (%d train / %d held-out), %d nodes, %d leaves, %d sites in %s" % (len(docs), len(train), len(held), len(nodes), sum(1 for n in nodes.values() if not n["childIds"]), len(sites), tmp))
    # dry-run must read everything and write nothing
    dry_run(ctx, arm); assert not os.path.exists(ctx.outcome); checks += 1
    # the analysis on the planted tree
    out = []
    R = analyse_arm(ctx, arm, out)
    print("\n".join(out))
    q = R["q1"]
    assert q["tree"]["nmi20"] > 0.85, q["tree"]["nmi20"]; checks += 1
    assert q["tree"]["purity"] > 0.85 and q["tree"]["nmi7"] > 0.6; checks += 1   # 21 leaves vs 7 groups: NMI_7 ~ 0.74 by construction
    assert q["kmeans"][0]["nmi20"] > 0.6 and q["ward"]["nmi20"] > 0.6; checks += 1
    assert all(r["nmi20"] < q["tree"]["nmi20"] - 0.5 and abs(r["ari20"]) < 0.05 and r["purity"] < 0.15 for r in q["random"]), "random floor (finite-sample NMI bias is large at n_eval 240 x 21 cells)"; checks += 1
    assert q["ci"][0] <= q["diff"] <= q["ci"][1]; checks += 1
    assert q["n_eval"] == len(held) and q["L"] == sum(1 for n in nodes.values() if not n["childIds"]); checks += 1
    q2r = R["q2"]
    assert q2r["cuts"][1]["nmi7"] > 0.99, q2r["cuts"][1]; checks += 1            # the depth-1 cut IS the planted 7-group partition
    assert q2r["best7_depth"] == 1; checks += 1
    assert q2r["label_median_j"] > 0.95 and q2r["label_median_depth"] == 2; checks += 1
    assert q2r["group_median_j"] > 0.99 and q2r["group_median_depth"] == 1; checks += 1
    assert q2r["sites"][r]["nmi7"] > 0.99 and 0 < q2r["sites"][r]["nmi20"] < 1; checks += 1
    assert q2r["leaves_j50"] == 21 and abs(min(q2r["leaf_j"].values()) - 0.5) < 1e-9, q2r["leaves_j50"]; checks += 1   # the two half-leaves sit at exactly J = 0.5 (20 of 40; the boundary is included)
    assert q2r["p7_split"]["held"]; checks += 1
    c = q2r["cert"]["nmi20"]
    assert c["n_cert"] == 4 and c["n_uncert"] == 2 and c["p"] is not None and c["strat"] is not None and c["strata"]["0-1"]["w"] == 1 and c["strata"]["2"]["w"] == 0, c; checks += 1
    q3r = R["q3"]
    assert q3r["built"] and q3r["leaves"] == 21 and q3r["root_cert"] and len(q3r["d1_cert"]) == 3 and q3r["cert"] == 4 and q3r["null_sites"] == 6, q3r; checks += 1
    assert q3r["refused"][nodes[r]["childIds"][0]]["minpair"][0]["sep"] == 0.019; checks += 1
    assert abs(q3r["sepbar"] - 0.025) < 1e-12; checks += 1
    # criteria / predictions / verdict assemble on a T1-only world: T1b absent -> run_all refuses (all arms must be present)
    try:
        run_all(ctx, manifest_path=ing_db + ".manifest.json"); raise AssertionError("run_all must refuse without T1b")
    except SystemExit:
        checks += 1
    assert not os.path.exists(ctx.outcome); checks += 1
    # clone the arm as T1b (bar 0.0145, slice 256 -> must refuse on sliceDim) then fix the slice to exercise the full run
    import shutil
    b = "ng_af_bareq512_s42"
    shutil.copy(ctx.build_out(arm), ctx.build_out(b)); shutil.copytree(run_dir, ctx.run_dir(b)); shutil.copy(ctx.site_null(arm), ctx.site_null(b))
    with open(ctx.sitenull_out(b), "w", encoding="utf-8") as f:
        f.write("[SEPBAR] proposalSeparationBar=0.0145 (-DsepBar '0.0145'); sliceDim=512\n")
    with open(os.path.join(root, ARMS[b]["toml"]), "w", encoding="utf-8") as f:
        f.write("proposalSeparationBar = 0.0145\n")
    try:
        load_arm(ctx, b); raise AssertionError("sliceDim mismatch must refuse")
    except SystemExit:
        checks += 1
    ARMS[b]["slice"] = 256   # selftest only: the fake tree is 256-d
    verdict = run_all(ctx, manifest_path=ing_db + ".manifest.json")
    assert os.path.exists(ctx.outcome); checks += 1
    txt = open(ctx.outcome, encoding="utf-8").read()
    full_txt = txt; full_verdict = verdict            # read again by the D1 assertions at the end of the selftest
    assert "C0 gate:" in txt and "C3 (Q3;" in txt and "P12" in txt and "VERDICT" in txt; checks += 1
    assert verdict["c3"] == "HELD" and verdict["c3b"] == "HELD", (verdict["c3"], verdict["c3b"]); checks += 1
    assert "NOT COMPARED (the nulls differ in bar)" in txt; checks += 1
    assert "P1   FAILED" in txt or "P1   HELD" in txt; checks += 1
    try:
        run_all(ctx, manifest_path=ing_db + ".manifest.json"); raise AssertionError("write-once must refuse")
    except SystemExit:
        checks += 1
    ARMS[b]["slice"] = 512
    # fail-closed: a held-out text planted inside a leaf
    leaf0 = next(i for i, n in nodes.items() if not n["childIds"])
    con = sqlite3.connect(snap_db)
    g = json.loads(con.execute("SELECT graph FROM snapshots WHERE id = ?", (sid,)).fetchone()[0])
    for n in g["nodes"]:
        if n["id"] == leaf0:
            n["queryIds"].append(afr.qid(held[0][0]))
    con.execute("UPDATE snapshots SET graph = ? WHERE id = ?", (json.dumps(g), sid)); con.commit(); con.close()
    os.remove(ctx.outcome)
    a = load_arm(ctx, arm)
    assert len(a["in_leaf"]) == 1; checks += 1
    try:
        analyse_arm(ctx, arm, []); raise AssertionError("held-out inside a leaf must refuse")
    except SystemExit:
        checks += 1
    con = sqlite3.connect(snap_db)
    for n in g["nodes"]:
        if n["id"] == leaf0:
            n["queryIds"].pop()
    con.execute("UPDATE snapshots SET graph = ? WHERE id = ?", (json.dumps(g), sid)); con.commit(); con.close()
    # fail-closed: partial site null (reps 299 on one row)
    csvp = ctx.site_null(arm); orig = open(csvp, encoding="utf-8").read()
    open(csvp, "w", encoding="utf-8", newline="").write(orig.replace(",OK,300\n", ",OK,299\n", 1))
    try:
        load_arm(ctx, arm); raise AssertionError("partial null must refuse")
    except SystemExit:
        checks += 1
    open(csvp, "w", encoding="utf-8", newline="").write(orig)
    # fail-closed: a missing vector
    con = sqlite3.connect(emb_db); con.execute("DELETE FROM embeddings WHERE query = ?", (held[3][0],)); con.commit(); con.close()
    try:
        analyse_arm(ctx, arm, []); raise AssertionError("missing vector must refuse")
    except SystemExit:
        checks += 1
    # fail-closed: the null's bar != the arm's bar
    with open(ctx.sitenull_out(arm), "w", encoding="utf-8") as f:
        f.write("[SEPBAR] proposalSeparationBar=0.0145 (-DsepBar '0.0145')\n")
    con = sqlite3.connect(emb_db)
    full = np.concatenate([vec[held[3][0]], 0.01 * rs.randn(dim)])
    con.execute("INSERT INTO embeddings VALUES (?, ?)", (held[3][0], struct.pack(">%df" % len(full), *full.tolist()))); con.commit(); con.close()
    try:
        analyse_arm(ctx, arm, []); raise AssertionError("null bar != arm bar must refuse")
    except SystemExit:
        checks += 1
    # ------------------------------------------------------------------ the numpy-bool verdict dispatch (D1)
    # post-run review 2026-09-23, defect D1: the C2 verdict's last operand is a numpy comparison, `numpy.True_ is
    # True` is False, and the registered sentence of record was therefore never written into the write-once outcome.
    # These assertions drive the verdict through all three outcomes, with a NUMPY bool in the HELD and FAILED cases.
    assert tribool(np.bool_(True)) is True and tribool(np.bool_(False)) is False and tribool(None) is None; checks += 1
    assert in_range(np.float64(0.5), 0.0, 1.0) is True and in_range(np.float64(2.0), 0.0, 1.0) is False; checks += 1
    assert verdict_word(np.bool_(False)) == "FAILED" and verdict_word(np.bool_(True)) == "HELD" and verdict_word(None) == "UNDETERMINED"; checks += 1
    np_held = tribool(0.0740 > 0 and 0.0480 < 0.05 and np.array([0.0, 0.0865])[1] > 0)     # the run's own and-chain
    assert type(np_held) is bool and np_held is True; checks += 1
    s_held = c2_sentence(np_held, 0.0740, 0.0480)
    assert s_held == "The certificate is topic-informative on a corpus with discrete topics (stratified gap 0.0740, p 0.0480).", s_held; checks += 1
    s_failed = c2_sentence(tribool(np.array([0.0, -0.01])[1] > 0), 0.0, 0.5)
    assert s_failed == C2_SENTENCES["failed"]; checks += 1
    assert c2_sentence(None, None, None) == C2_SENTENCES["undetermined"]; checks += 1
    try:
        c2_sentence("HELD", 0.1, 0.01); raise AssertionError("an unhandled C2 verdict must refuse, not write nothing")
    except SystemExit:
        checks += 1
    try:
        tribool("yes"); raise AssertionError("tribool must refuse a non-truth value")
    except SystemExit:
        checks += 1
    # the outcome of the full run above carried EXACTLY ONE of the three C2 sentences (under D1 it carried none)
    c2_in_outcome = [k for k, v in C2_SENTENCES.items() if (v.split(" (stratified")[0] if k == "held" else v) in full_txt]
    assert len(c2_in_outcome) == 1 and c2_in_outcome == ["failed"], (c2_in_outcome, [l for l in full_txt.splitlines() if "certificate" in l]); checks += 1
    assert full_verdict["c2"] is False, (full_verdict["c2"], type(full_verdict["c2"]).__name__); checks += 1   # a Python bool, not numpy.False_
    # ------------------------------------------------------------------ TP20-C2-CONFORMANCE: bracket (e)'s four
    # no-contrast conditions (registrar's ruling 2026-09-23 (a)-(e); queue item TP20-C2-CONFORMANCE). One assertion
    # per condition; each checks the NAMED REASON WITH ITS COUNT and that F2 DID NOT FIRE. Every fixture below
    # carries a stratified gap 0.0500 > 0, p 0.0100 < 0.05 and an OLS cert coefficient 0.0865 > 0, so the registered
    # verdict expression would read HELD if it were reached: UNDETERMINED here proves the conditions are evaluated
    # BEFORE it (ruling (a)) and that the word is the outcome of a real condition, not of a failure to compute.
    def c2_fixture(n_cert, n_uncert, strata, perm_distinct, perm_done=1000, strat=0.0500, p=0.0100):
        return dict(raw=0.1215, strat=strat, p=p, n_cert=n_cert, n_uncert=n_uncert,
                    strata={s: dict(n_cert=a, n_uncert=b, gap=(0.05 if min(a, b) > 0 else None), w=min(a, b)) for s, (a, b) in strata.items()},
                    beta=np.array([0.1827, 0.0865, 0.0041, -0.0146]), se=np.array([0.05, 0.0395, 0.0225, 0.0154]),
                    perm_distinct=perm_distinct, perm_done=perm_done)

    def c2_undetermined_case(fix, reason, must_not_fire=("(i)", "(ii)", "(iii)", "(iv)")):
        v, ls, fields = c2_decide(fix)
        txt = "\n".join(ls)
        other = [t for t in must_not_fire if t != reason.split(")")[0] + ")"]
        return (v is None and fields["c2"] is None and fields["f2"] is False and type(fields["f2"]) is bool
                and reason in txt and F2_NOT_FIRED in ls and "UNDETERMINED -- no contrast:" in ls[0]
                and "HELD" not in ls[0].split("): ")[-1] and "FAILED" not in ls[0].split("): ")[-1]
                and all(t not in txt.split("no contrast: ")[1].split("\n")[0] for t in other)
                and c2_sentence(v, fields["c2_gap"], fields["c2_p"], fields["c2_no_contrast"])
                == C2_SENTENCES["undetermined_no_contrast"] % reason), (v, ls, fields)
    # (i) fewer than 2 certified sites
    ok_i, ev_i = c2_undetermined_case(c2_fixture(1, 50, {"3": (1, 20), "4": (0, 30)}, perm_distinct=7),
                                      "(i) fewer than 2 certified sites: certified n = 1")
    assert ok_i, ev_i; checks += 1
    # (ii) fewer than 2 uncertified sites
    ok_ii, ev_ii = c2_undetermined_case(c2_fixture(50, 1, {"3": (20, 1), "4": (30, 0)}, perm_distinct=7),
                                        "(ii) fewer than 2 uncertified sites: uncertified n = 1")
    assert ok_ii, ev_ii; checks += 1
    # (iii) no depth stratum holds both kinds: total weight sum(min(n_cert, n_uncert)) = 0 (the stratified gap and
    # the permutation p are genuinely n/a on this fixture, and UNDETERMINED is the outcome, not a failure to compute)
    ok_iii, ev_iii = c2_undetermined_case(c2_fixture(5, 5, {"3": (5, 0), ">=5": (0, 5)}, perm_distinct=7, strat=None, p=None),
                                          "(iii) total depth-stratum weight sum(min(n_cert, n_uncert)) over {0-1, 2, 3, 4, >= 5} = 0")
    assert ok_iii, ev_iii; checks += 1
    # (iv) a degenerate permutation distribution: every one of the 1,000 within-stratum permutations returned the
    # same stratified gap, so the p is an artefact of an instrument with nothing to permute
    ok_iv, ev_iv = c2_undetermined_case(c2_fixture(8, 9, {"4": (8, 9)}, perm_distinct=1),
                                        "(iv) degenerate permutation distribution: 1 distinct value(s) over 1000 within-stratum permutations")
    assert ok_iv, ev_iv; checks += 1
    # ------------------------------------------------------------------ bracket (c)(12): the seven untested paths
    # T2 (bar re-tuned by I4, no registered bar): no TOML bar / no [SEPBAR] / the two bars disagree / they agree.
    write_text(ctx.sitenull_out(arm), "[SEPBAR] proposalSeparationBar=0.025 (restored after the bar-mismatch check)")
    t2 = "ng_af_bar_eq_s42"
    shutil.copy(ctx.build_out(arm), ctx.build_out(t2)); shutil.copytree(run_dir, ctx.run_dir(t2)); shutil.copy(ctx.site_null(arm), ctx.site_null(t2))
    t2_toml = os.path.join(root, ARMS[t2]["toml"])
    write_text(t2_toml, "# no proposalSeparationBar line")
    write_text(ctx.sitenull_out(t2), "[SEPBAR] proposalSeparationBar=0.0180 (-DsepBar '0.0180')")
    try:
        analyse_arm(ctx, t2, [], bar_retuned=True); raise AssertionError("T2 with no TOML bar must refuse")
    except SystemExit:
        checks += 1
    write_text(t2_toml, "proposalSeparationBar = 0.0180")
    write_text(ctx.sitenull_out(t2), "the null log with no [SEPBAR] line")
    try:
        analyse_arm(ctx, t2, [], bar_retuned=True); raise AssertionError("T2 with no [SEPBAR] line must refuse")
    except SystemExit:
        checks += 1
    write_text(ctx.sitenull_out(t2), "[SEPBAR] proposalSeparationBar=0.025 (the harness default)")
    try:
        analyse_arm(ctx, t2, [], bar_retuned=True); raise AssertionError("T2's null at a bar != the chain's computed bar must refuse")
    except SystemExit:
        checks += 1
    write_text(ctx.sitenull_out(t2), "[SEPBAR] proposalSeparationBar=0.0180 (-DsepBar '0.0180')")
    o2 = []
    R2 = analyse_arm(ctx, t2, o2, bar_retuned=True)
    assert R2["q3"]["built"] and abs(R2["q3"]["sepbar"] - 0.0180) < 1e-12 and R2["q1"]["L"] == 21, R2["q3"].get("sepbar"); checks += 1
    assert any("bar re-tuned: T2's rows are never compared" in l for l in o2); checks += 1
    # the ABSENT-null note on a BUILT arm: UNDETERMINED, printed, and the analysis continues (the outcome is written)
    os.remove(ctx.site_null(t2))
    o3 = []
    R3 = analyse_arm(ctx, t2, o3, bar_retuned=True)
    assert R3["q3"]["built"] and R3["q3"]["cert"] is None and R3["arm_null_rows"] == {}; checks += 1
    assert any("ABSENT: this arm's certification is UNDETERMINED" in l for l in o3) and any("site null: ABSENT (certified share UNDETERMINED)" in l for l in o3); checks += 1
    # the one-child root: q2 has no depth-1 partition to read and refuses by name (READY item 8)
    a_one = load_arm(ctx, arm)
    root_id = a_one["graph"]["root"]
    a_one["byid"][root_id]["childIds"] = [a_one["byid"][root_id]["childIds"][0]]
    a_one["sites"] = [x for x in a_one["sites"] if x != root_id]
    try:
        q2(a_one, load_vectors(ctx, a_one["train_texts"] + a_one["held_texts"]), [], R["q1"], perm=20)
        raise AssertionError("a one-child root must refuse")
    except SystemExit:
        checks += 1
    # the F3 contingency: T1 not built, no T2 build log -> the outcome is still WRITTEN, C3 FAILED, C2 UNDETERMINED
    os.remove(ctx.build_out(t2)); shutil.rmtree(ctx.run_dir(t2), ignore_errors=True)
    for x in (arm, b):
        txt_b = open(ctx.build_out(x), encoding="utf-8").read()
        open(ctx.build_out(x), "w", encoding="utf-8").write(txt_b.replace("Successfully generated and saved snapshot. Snapshot ID: %s" % sid, "(no snapshot)"))
    assert not build_state(ctx.build_out(arm))["built"]; checks += 1
    if os.path.exists(ctx.outcome):
        os.remove(ctx.outcome)
    v_f3 = run_all(ctx, manifest_path=ing_db + ".manifest.json")
    f3_txt = open(ctx.outcome, encoding="utf-8").read()
    assert v_f3["c3"] == "FAILED" and "T2 CONTINGENCY:" in f3_txt and "the contingency (I4) did not run" in f3_txt; checks += 1
    assert "The recipe of record does not build on 20NG at bar 0.025 (F3)" in f3_txt; checks += 1
    assert C2_SENTENCES["undetermined"] in f3_txt and C2_SENTENCES["failed"] not in f3_txt; checks += 1
    import gc
    gc.collect()                      # anchor_free_readout.full_vectors leaves its sqlite connection to the GC
    shutil.rmtree(tmp, ignore_errors=True)
    if checks != SELFTEST_CHECKS:
        die("selftest ran %d checks, the pinned count is %d (SELFTEST_CHECKS): a check was lost or added without "
            "raising the pin in the same commit (READY condition 12)" % (checks, SELFTEST_CHECKS))
    print("[TOPIC-PARTITION] selftest OK: %d checks (pinned %d), 0 failed (temp dir removed)" % (checks, SELFTEST_CHECKS))
    return 0


# ----------------------------------------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--arm", choices=sorted(ARMS), default=None)
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.dry_run:
        if not a.arm:
            die("--dry-run needs --arm <%s>" % "|".join(sorted(ARMS)))
        return dry_run(Ctx(), a.arm)
    if a.run:
        print("[TOPIC-PARTITION] pool: the corpus's own split (no arena pool read or written); RUN; script_sha %s" % script_sha())
        run_all(Ctx())
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
