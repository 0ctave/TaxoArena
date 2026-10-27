"""CERT-ALIGN-SIZE readout (docs/judge_v2_program.md, "## Registered 2026-10-04 (before any code or call) -- CERT-ALIGN-SIZE",
L24245-L24257, registration commit feac5b3d; docs/agents/results/CERT-ALIGN-SIZE.json). ZERO LLM calls; CPU only.

QUESTION (registered). On the four anchor-free MMLU-Pro re-draw trees (af_clean_s42, af_s137, af_s2048, af_s42_o1), are
site-certified splits (cert_site_p95 = true: site-null p95, per site, uncorrected, 300 reps) better aligned with the declared
categories than uncertified splits OF THE SAME SIZE?

LAUNCH SEQUENCE (zero calls; NOT a pool reader, rule 7 does not bind; temp files only under E: via scratch_dir):
  python tools/analysis/cert_align_size.py --selftest     # fixture DBs/CSVs in a scratch dir on E:; value-asserting; mutant table below
  python tools/analysis/cert_align_size.py --dry-run      # pins, inputs, denominators, site counts per tree x size stratum; no Y; writes nothing
  python tools/analysis/cert_align_size.py --run          # the readout of record; WRITE-ONCE outcome on E: (+ SHA256SUMS.txt)
      --out <path>          outcome path (default E:/TaxoArena_backup_<date>_cert_align_size/cert_align_size_outcome.txt);
                            REFUSES when the path (or the SHA256SUMS.txt beside it) exists; outputs are NEVER committed
      --data-root <dir>     where snapshots.db / the label DBs / embeddings_cache.db / the site-null CSVs live (default:
                            the checkout holding this script)

INPUTS (all read-only).
  * site nulls of record (blob-pinned below; committed 17a44347 / 0b99e9aa / 88049302): experiment_results/anchorfree/redraw/
    site_null_<arm>.csv and experiment_results/topic_partition/site_null_<arm>.csv: cert_site_p95 = certified, n = site
    size, depth; reps must be 300 and the snapshot id the pinned one. Labels never enter certification (no new null).
  * snapshots.db (mode=ro&immutable=1 after a -wal check; ONLY `SELECT graph FROM snapshots WHERE id = ?`; the
    reserved_queries column is never selected): site members = union of descendant leaves' queryIds (TRAIN only).
  * labels: mmlu_pro_dataset_cache_v2.db table mmlu_pro (category lower-cased; a text carried by several rows keeps its
    first row's category, anchor_free_readout.corpus's rule) and twenty_newsgroups_cache_v1.db table twenty_newsgroups,
    joined to queryIds by qid = "q_" + sha256(text)[:16] (TaxonomyPersistence.hashQuery). No eval id, no pool table, no
    reserved_queries is read. Every member of every site must carry a label (refused otherwise).
  * embeddings_cache.db (mode=ro&immutable=1 after a -wal check): vectors ONLY for members held by >= 2 children of a site
    (about 2% of member slots), assigned to the child with the higher cosine to the child's vmfMu in the node's sliceDim
    (first sliceDim coordinates re-normalised) -- TOPIC-PARTITION-20NG P9's assign_child rule, reused verbatim in form.
  snapshots_frozen.db is never opened.

INSTRUMENT (registration, verbatim in the code).
  Y_s = NMI(child assignment, declared category) on s's TRAIN members, arithmetic-mean normalisation (sklearn); a site with
  label entropy 0 is printed and gets Y = 0 (not dropped).
  Size stratum = quintile of log n over the POOLED sites of the four trees (cutpoints np.quantile(log n, .2/.4/.6/.8),
  stratum = number of cutpoints strictly below log n), crossed with tree (tree x size strata).
  G = sum_h w_h (mean Y|cert - mean Y|uncert) / sum_h w_h, w_h = min(n_cert,h, n_uncert,h); strata without both classes
  drop out (count printed).
  One-sided permutation p: 10,000 permutations of the certified flag WITHIN tree x size strata, numpy RandomState(20261004),
  direction certified higher: p = (1 + #{G_perm >= G - 1e-12}) / (1 + 10,000) (P9's form; ties count against).
  Beside: the raw gap; the depth-stratified gap (P9's strata 0-1 / 2 / 3 / 4 / >=5, crossed with tree); OLS
  Y ~ cert + log n + depth + tree (HC1).
  Descriptive arms: o0_clean_s42 ([AN], MMLU labels) and the 20NG main tree ng_af_s42 (P9's object, SEEN) and T1b
  ng_af_bareq512_s42 (1 certified): the SAME instrument, size quintiles over the arm's own sites (registration: the
  quintile rule is stated for the deciding pool; an arm's own pool is the like-for-like reading). The 20NG main tree's
  depth-stratified gap is printed beside the record's P9 value 0.0740 (raw 0.1215) as a loader check.

CRITERIA (registered; every branch printed and executed by the selftest).
  CA1 (DECIDING): ALIGNED-BEYOND-SIZE iff G > 0 AND p <= 0.05; SIZE-ONLY otherwise (a G that cannot be formed reads
  SIZE-ONLY, with the reason printed).  F-CA fires iff CA1 reads SIZE-ONLY.
  P1 G in [0.00, 0.12]; CA1 ALIGNED-BEYOND-SIZE at 0.55 (Brier).  P2 raw - G in [0.00, 0.10].  P3 20NG size-stratified gap
  in [0.00, 0.12] (descriptive, seen arm).  P4 o0_clean_s42 G in [-0.03, +0.07] (descriptive). Bands HELD iff the point
  lies in the closed interval.
SUPPORT (registered, quoted, not re-derived): DEFF 1.3 a DECLARED PILOT ASSUMPTION; SE 0.0166; MDE80 0.041; the readout
prints the realised counts first, then the realised SE (realised SD of Y x sqrt(1/n_cert + 1/n_uncert) x sqrt(1.3)),
n_eff, MDE80, and the measured permutation SD of G (the within-stratum null spread) beside the deciding statistic.

SELFTEST MUTANTS (2026-10-04; temporary edits of this file, each reverted; selftest run under scratch_dir on E:):
  20 / 20 killed; table in MUTANTS below (printed by --selftest). Loader check on the real data (2026-10-04, 20NG arm
  only, the SEEN descriptive arm; the deciding arms were NOT computed before review): raw 0.12146, depth-stratified
  0.07402 = the record's P9 0.1215 / 0.0740.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import math
import os
import sqlite3
import struct
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import tempfile; import scratch_dir  # noqa: E401,E402  TEMP-SPRAWL: temp on E:, removed at exit

import numpy as np  # noqa: E402

REG = "docs/judge_v2_program.md L24245-L24257 (registration commit feac5b3d)"
PERM = 10_000
SEED = 20261004
REPS = 300
TIE_EPS = 1e-12
DEFF = 1.3                       # declared pilot assumption (Support (b))
PLAN = dict(se=0.0166, mde=0.041, sd=0.10, n_cert=60, n_uncert=220)
Z80 = 1.645 + 0.842
P1_BAND = (0.00, 0.12); P1_PROB = 0.55
P2_BAND = (0.00, 0.10)
P3_BAND = (0.00, 0.12)
P4_BAND = (-0.03, 0.07)
P9_RECORD = dict(raw=0.1215, strat=0.0740)       # TOPIC-PARTITION-20NG P9 (L11490), 20 labels, depth strata
SELFTEST_CHECKS = 48                             # pinned count: an edit that changes the number of checks changes this line

MMLU = dict(db="mmlu_pro_dataset_cache_v2.db", table="mmlu_pro", lower=True)
NG = dict(db="twenty_newsgroups_cache_v1.db", table="twenty_newsgroups", lower=False)
# arm -> (role, csv (repo-relative), git blob of record, snapshot id, labels)
ARMS = {
    "af_clean_s42": dict(role="deciding", csv="experiment_results/anchorfree/redraw/site_null_af_clean_s42.csv",
                         blob="8ed1b699d692af1d4f1d573127196248598079dd", snap="20260917_201353_Headless_Run_Auto_ge", labels=MMLU),
    "af_s137": dict(role="deciding", csv="experiment_results/anchorfree/redraw/site_null_af_s137.csv",
                    blob="7ac6510d8eb4ab7f38ecaa5a24905b4b362a79cf", snap="20260918_041114_Headless_Run_Auto_ge", labels=MMLU),
    "af_s2048": dict(role="deciding", csv="experiment_results/anchorfree/redraw/site_null_af_s2048.csv",
                     blob="264f4cd9fefb52bb5c6c8b65b3866c5812f47496", snap="20260918_043908_Headless_Run_Auto_ge", labels=MMLU),
    "af_s42_o1": dict(role="deciding", csv="experiment_results/anchorfree/redraw/site_null_af_s42_o1.csv",
                      blob="fd998a7983e99599fb9e484daba28807ee7e3de4", snap="20260918_050715_Headless_Run_Auto_ge", labels=MMLU),
    "o0_clean_s42": dict(role="AN", csv="experiment_results/anchorfree/redraw/site_null_o0_clean_s42.csv",
                         blob="f69179a0ca375ea59c785d52a9db9e040c3b85ca", snap="20260918_040207_Headless_Run_Auto_ge", labels=MMLU),
    "ng_af_s42": dict(role="20NG", csv="experiment_results/topic_partition/site_null_ng_af_s42.csv",
                      blob="297c2d7590f9f9d142034042531b1275e7f03fc8", snap="20260922_195728_Headless_Run_Auto_ge", labels=NG),
    "ng_af_bareq512_s42": dict(role="20NG-T1b", csv="experiment_results/topic_partition/site_null_ng_af_bareq512_s42.csv",
                               blob="d632b14b472bc5cf8e6a6f8199398a839f828e0f", snap="20260923_043423_Headless_Run_Auto_ge", labels=NG),
}
DECIDING = ["af_clean_s42", "af_s137", "af_s2048", "af_s42_o1"]
DESCRIPTIVE = [("o0_clean_s42",), ("ng_af_s42",), ("ng_af_bareq512_s42",)]

MUTANTS = """
  id   mutant (temporary edit, reverted; copies under E:/TaxoArena_tmp, TMP/TEMP/TMPDIR sandboxed)   result (what killed it)
  M1   w_h = max(n_cert, n_uncert) instead of min                                  killed (F1 CA1 value: G +0.7000 vs +0.8750)
  M2   size strata not crossed with tree                                           killed (F1 CA1 value: G +0.6667)
  M3   quintiles per tree instead of pooled over the four trees                    killed (F1 counts line af_clean_s42)
  M4   permutation shuffles the flag across ALL sites, not within strata           killed (T1b / F2 p 1.0000 -> 0.9040)
  M5   p = ge / N (the form (1+ge)/(1+N) changed)                                   killed (F1 p 0.0000 vs 0.0005)
  M6   one-sided direction reversed (G_perm <= G)                                  killed (F1 CA1 SIZE-ONLY, p 1.0000)
  M7   CA1 uses G >= 0 instead of G > 0                                            killed (decide-path boundary ca1_decide(0.0, 0.001))
  M8   CA1 uses p < 0.05 instead of p <= 0.05                                      killed (decide-path boundary ca1_decide(1e-9, 0.05))
  M9   entropy-0 sites dropped instead of Y = 0                                    killed (F1 CA1 value: G +0.8571, 36 uncertified)
  M10  certified flag read from cert_deflated_p95                                  killed (F1 CA1 SIZE-ONLY, G -0.8750)
  M11  multi-holder member assigned to the first holder, not by cosine             killed (F1 CA1 value: G +0.8462)
  M12  F-CA line not printed on the SIZE-ONLY branch                               killed (F2 F-CA line absent)
  M13  write-once dropped (no existence refusal; "w")                              killed (F1 second --run not refused)
  M14  raw gap uncertified - certified                                             killed (F1 raw -0.6207)
  M15  P4 read from the 20NG arm instead of o0_clean_s42                           killed (F1 P4 +1.0000 vs +0.5000)
  M16  blob pin check skipped                                                      killed (pin refusal not raised)
  M17  label taken from the LAST row of a duplicated text                          killed (F4 duplicate label)
  M18  root site (depth 0) excluded                                                killed (F1 36 uncertified, 2 strata dropped)
  M19  G stratified by depth instead of size                                       killed (crash in the strata print: weak kill, by exception)
  M20  bands read as open intervals                                                killed (F2 P1 G +0.0000 FAILED vs HELD)
  20 / 20 killed.
"""


# ----------------------------------------------------------------------------------------------- utilities
class Refused(SystemExit):
    pass


def die(msg):
    print("[CERT-ALIGN-SIZE] REFUSED: " + msg)
    raise Refused(2)


def git_blob(path):
    """git hash-object of the LF rendering (the working tree may hold CRLF under autocrlf; LF is of record)."""
    with open(path, "rb") as f:
        b = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def script_pins():
    with open(os.path.abspath(__file__), "rb") as f:
        raw = f.read()
    lf = raw.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    blob = hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest()
    return dict(blob=blob, lf16=hashlib.sha256(lf).hexdigest()[:16], crlf16=hashlib.sha256(crlf).hexdigest()[:16])


def ro(path, immutable=True):
    if not os.path.exists(path):
        die("%s not found" % path)
    for suf in ("-wal", "-journal"):
        p = path + suf
        if os.path.exists(p) and os.path.getsize(p) > 0:
            die("%s is %d bytes (a writer has not checkpointed): a failed precondition, wait; immutable=1 would hide it"
                % (p, os.path.getsize(p)))
    return sqlite3.connect("file:%s?mode=ro%s" % (path.replace("\\", "/"), "&immutable=1" if immutable else ""), uri=True)


def qid(text):
    return "q_" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def in_band(x, band):
    return bool(x is not None and band[0] <= x <= band[1])


def fmt(x, nd=4):
    return "n/a" if x is None else ("%+.*f" % (nd, x))


def nmi(a, b):
    from sklearn.metrics import normalized_mutual_info_score
    return float(normalized_mutual_info_score(a, b, average_method="arithmetic"))


def entropy(labels):
    c = Counter(labels); n = sum(c.values())
    return -sum(v / n * math.log(v / n) for v in c.values()) if n else 0.0


class Ctx:
    def __init__(self, data_root=ROOT, perm=PERM, arms=None, check_blobs=True):
        self.data_root = data_root
        self.perm = perm
        self.arms = arms or ARMS
        self.check_blobs = check_blobs

    def path(self, rel):
        return os.path.join(self.data_root, rel)


# ----------------------------------------------------------------------------------------------- loaders
def read_site_null(ctx, arm):
    spec = ctx.arms[arm]
    p = ctx.path(spec["csv"])
    if not os.path.exists(p):
        die("%s: site null %s not found" % (arm, spec["csv"]))
    blob = git_blob(p)
    if ctx.check_blobs and blob != spec["blob"]:
        die("%s: %s is blob:%s, the site null of record is blob:%s" % (arm, spec["csv"], blob, spec["blob"]))
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    if not rows:
        die("%s: %s has no rows" % (arm, spec["csv"]))
    if {r["reps"] for r in rows} != {str(REPS)}:
        die("%s: reps %s (only %d-rep nulls are read)" % (arm, sorted({r["reps"] for r in rows}), REPS))
    sids = {r["snapshot_id"] for r in rows}
    if sids != {spec["snap"]}:
        die("%s: snapshot ids %s, the pinned one is %s" % (arm, sorted(sids), spec["snap"]))
    out = {}
    for r in rows:
        c = r["cert_site_p95"].strip().lower()
        if c not in ("true", "false"):
            die("%s: cert_site_p95 %r at %s is not true/false" % (arm, r["cert_site_p95"], r["node_id"]))
        out[r["node_id"]] = dict(node=r["node_id"], depth=int(r["depth"]), n=int(r["n"]), cert=(c == "true"))
    return dict(rows=out, blob=blob, sha256=sha256_file(p), path=spec["csv"])


def load_graph(ctx, snapshot_id):
    con = ro(ctx.path("snapshots.db"))
    try:
        row = con.execute("SELECT graph FROM snapshots WHERE id = ?", (snapshot_id,)).fetchone()
    finally:
        con.close()
    if row is None:
        die("snapshot %s not in snapshots.db" % snapshot_id)
    g = json.loads(row[0])
    byid = {n["id"]: n for n in g["nodes"]}
    memo = {}

    def rec(i, stack):
        if i in memo:
            return memo[i]
        if i in stack:
            die("cycle at %s in snapshot %s" % (i, snapshot_id))
        kids = byid[i].get("childIds") or []
        s = frozenset(byid[i].get("queryIds") or []) if not kids else frozenset().union(*(rec(c, stack | {i}) for c in kids))
        memo[i] = s
        return s
    for i in byid:
        rec(i, frozenset())
    sites = sorted(i for i, n in byid.items() if len(n.get("childIds") or []) >= 2)
    return dict(root=g["rootId"], byid=byid, mem=memo, sites=sites)


_LABEL_CACHE = {}


def load_labels(ctx, spec):
    key = (ctx.data_root, spec["db"], spec["table"])
    if key in _LABEL_CACHE:
        return _LABEL_CACHE[key]
    con = ro(ctx.path(spec["db"]))
    try:
        rows = con.execute("SELECT id, question, category FROM %s ORDER BY id" % spec["table"]).fetchall()
    finally:
        con.close()
    lab = {}; text = {}
    for _, t, c in rows:
        if t is None or c is None:
            continue
        q = qid(t)
        if q not in lab:                                     # first row by id wins (anchor_free_readout.corpus)
            lab[q] = c.lower() if spec["lower"] else c
            text[q] = t
    _LABEL_CACHE[key] = (lab, text, len(rows))
    return _LABEL_CACHE[key]


def load_vectors(ctx, texts):
    want = set(texts)
    if not want:
        return {}
    con = ro(ctx.path("embeddings_cache.db"))
    vec = {}
    try:
        for t, blob in con.execute("SELECT query, vector FROM embeddings"):
            if t in want and isinstance(blob, bytes) and len(blob) % 4 == 0:
                vec[t] = np.array(struct.unpack(">%df" % (len(blob) // 4), blob), dtype=np.float64)
    finally:
        con.close()
    return vec


def unit(v):
    v = np.asarray(v, dtype=np.float64); n = np.linalg.norm(v)
    return v / n if n > 0 else v


# ----------------------------------------------------------------------------------------------- per arm
def load_arm(ctx, arm, with_y=True):
    """Sites of record with (n, depth, cert); with_y adds Y_s. Fail-closed on every join."""
    spec = ctx.arms[arm]
    null = read_site_null(ctx, arm)
    g = load_graph(ctx, spec["snap"])
    rows = null["rows"]
    extra = sorted(set(rows) - set(g["sites"]))
    if extra:
        die("%s: site-null rows for non-sites %s" % (arm, extra[:5]))
    missing = sorted(set(g["sites"]) - set(rows))
    for s, r in rows.items():
        if r["n"] != len(g["mem"][s]):
            die("%s: site %s n %d in the CSV != %d members in the snapshot graph" % (arm, s, r["n"], len(g["mem"][s])))
        if r["depth"] != g["byid"][s].get("depth"):
            die("%s: site %s depth %d in the CSV != %s in the graph" % (arm, s, r["depth"], g["byid"][s].get("depth")))
    sites = [dict(tree=arm, node=s, n=rows[s]["n"], depth=rows[s]["depth"], cert=rows[s]["cert"]) for s in sorted(rows)]
    info = dict(arm=arm, null=null, missing=missing, n_sites_graph=len(g["sites"]), sites=sites, multi=0, slots=0, zero_h=[])
    lab, text, nrows = load_labels(ctx, spec["labels"])
    members = set().union(*(g["mem"][s] for s in rows)) if rows else set()
    unl = sorted(q for q in members if q not in lab)
    if unl:
        die("%s: %d site members carry no label in %s.%s (first %s)" % (arm, len(unl), spec["labels"]["db"], spec["labels"]["table"], unl[:3]))
    info["members"] = len(members); info["label_rows"] = nrows
    # multi-holders (needed for the dry-run denominator too)
    multi = {}
    for s in sorted(rows):
        kids = g["byid"][s]["childIds"]
        for q in g["mem"][s]:
            h = [c for c in kids if q in g["mem"][c]]
            info["slots"] += 1
            if len(h) > 1:
                multi[(s, q)] = h
    info["multi"] = len(multi)
    if not with_y:
        return info
    vec = load_vectors(ctx, [text[q] for (_, q) in multi])
    miss = sorted({q for (_, q) in multi if text[q] not in vec})
    if miss:
        die("%s: %d multi-holder members have no vector in embeddings_cache.db (first %s)" % (arm, len(miss), miss[:3]))
    for site in sites:
        s = site["node"]; kids = g["byid"][s]["childIds"]
        assign = {}
        for q in g["mem"][s]:
            h = multi.get((s, q))
            if h is None:
                assign[q] = next(c for c in kids if q in g["mem"][c])
            else:
                best = None; bv = None
                for c in h:
                    mu = unit(g["byid"][c]["vmfMu"]); d = len(mu)
                    v = float(unit(vec[text[q]][:d]) @ mu)
                    if bv is None or v > bv:
                        best, bv = c, v
                assign[q] = best
        qs = sorted(assign)
        labs = [lab[q] for q in qs]; ch = [assign[q] for q in qs]
        h20 = entropy(labs)
        site["h"] = h20
        if h20 == 0.0:
            site["y"] = 0.0; info["zero_h"].append(s)
        else:
            site["y"] = nmi(labs, ch) if len(set(ch)) > 1 else 0.0
    return info


# ----------------------------------------------------------------------------------------------- statistics
def size_cuts(ns):
    return [float(c) for c in np.quantile(np.log(np.asarray(ns, dtype=np.float64)), [0.2, 0.4, 0.6, 0.8])]


def size_stratum(n, cuts):
    ln = math.log(n)
    return int(sum(1 for c in cuts if c < ln))


def depth_stratum(d):
    return "0-1" if d <= 1 else (str(d) if d <= 4 else ">=5")


def stratified_gap(y, cert, keys):
    """G = sum_h w_h (mean Y|cert - mean Y|uncert) / sum_h w_h, w_h = min(n_cert,h, n_uncert,h); None if no stratum has both."""
    by = defaultdict(lambda: ([], []))
    for v, c, k in zip(y, cert, keys):
        by[k][0 if c else 1].append(v)
    num = 0.0; den = 0.0; rows = {}
    for k in sorted(by, key=str):
        c, u = by[k]
        w = min(len(c), len(u))
        gap = (float(np.mean(c)) - float(np.mean(u))) if w > 0 else None
        rows[k] = dict(n_cert=len(c), n_uncert=len(u), w=w, gap=gap)
        if w > 0:
            num += w * gap; den += w
    return (num / den if den > 0 else None), rows


def perm_test(y, cert, keys, g_obs, nperm, seed):
    """One-sided (certified higher) p over nperm permutations of the flag WITHIN the strata keys; (1+ge)/(1+nperm)."""
    if g_obs is None:
        return None, None, 0
    idx = defaultdict(list)
    for i, k in enumerate(keys):
        idx[k].append(i)
    groups = [np.asarray(idx[k]) for k in sorted(idx, key=str)]
    rs = np.random.RandomState(seed)
    y = np.asarray(y, dtype=np.float64); c0 = np.asarray(cert, dtype=bool)
    ge = 0; vals = []
    for _ in range(nperm):
        pc = c0.copy()
        for gi in groups:
            sh = c0[gi].copy(); rs.shuffle(sh); pc[gi] = sh
        g, _ = stratified_gap(y, pc, keys)
        vals.append(g)
        if g is not None and g >= g_obs - TIE_EPS:
            ge += 1
    p = (1 + ge) / (1 + nperm)
    sd = float(np.std([v for v in vals if v is not None], ddof=1)) if len(vals) > 1 else None
    return p, sd, len(set(vals))


def ols_hc1(y, X):
    X = np.asarray(X, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    e = y - X @ beta
    V = XtX_inv @ (X.T @ (X * (e ** 2)[:, None])) @ XtX_inv * (n / max(1, n - k))
    return beta, np.sqrt(np.maximum(np.diag(V), 0.0))


def ca1_decide(G, p):
    """CA1 (registered): ALIGNED-BEYOND-SIZE iff G > 0 AND p <= 0.05; SIZE-ONLY otherwise."""
    if G is None or p is None:
        return "SIZE-ONLY"
    return "ALIGNED-BEYOND-SIZE" if bool(G > 0) and bool(p <= 0.05) else "SIZE-ONLY"


def analyse_pool(sites, ctx, out, label, trees):
    """The registered instrument on a pool of sites (one or more trees). Prints counts BEFORE any Y."""
    ns = [s["n"] for s in sites]
    cuts = size_cuts(ns)
    for s in sites:
        s["size_h"] = size_stratum(s["n"], cuts)
    keys = [(s["tree"], s["size_h"]) for s in sites]
    out.append("  [%s] size-quintile cutpoints on log n over the pooled %d sites of %s: n = %s"
               % (label, len(sites), "+".join(trees), ", ".join("%.1f" % math.exp(c) for c in cuts)))
    cnt = Counter((k, s["cert"]) for k, s in zip(keys, sites))
    out.append("  [%s] COUNTS (printed before any Y): certified / uncertified per tree x size stratum:" % label)
    for t in trees:
        out.append("    %-20s %s   (tree total %d cert / %d uncert)" % (
            t, "  ".join("q%d %d/%d" % (h, cnt[((t, h), True)], cnt[((t, h), False)]) for h in range(5)),
            sum(1 for s in sites if s["tree"] == t and s["cert"]), sum(1 for s in sites if s["tree"] == t and not s["cert"])))
    return cuts, keys


def gap_block(sites, keys, ctx, out, label):
    y = [s["y"] for s in sites]; cert = [s["cert"] for s in sites]
    nc = sum(cert); nu = len(cert) - nc
    G, strata = stratified_gap(y, cert, keys)
    dropped = sum(1 for r in strata.values() if r["w"] == 0)
    p, perm_sd, distinct = perm_test(y, cert, keys, G, ctx.perm, SEED)
    raw = (float(np.mean([v for v, c in zip(y, cert) if c])) - float(np.mean([v for v, c in zip(y, cert) if not c]))) if nc and nu else None
    dkeys = [(s["tree"], depth_stratum(s["depth"])) for s in sites]
    Gd, _ = stratified_gap(y, cert, dkeys)
    trees = sorted({s["tree"] for s in sites})
    X = [[1.0, 1.0 if s["cert"] else 0.0, math.log(s["n"]), float(s["depth"])] + [1.0 if s["tree"] == t else 0.0 for t in trees[1:]] for s in sites]
    beta, se = ols_hc1(y, X) if len(y) > len(X[0]) else ([float("nan")] * len(X[0]), [float("nan")] * len(X[0]))
    out.append("  [%s] Y: %d sites (%d certified, %d uncertified); entropy-0 sites (Y = 0, kept): %d; mean Y certified %s, uncertified %s"
               % (label, len(y), nc, nu, sum(1 for s in sites if s.get("h") == 0.0),
                  fmt(float(np.mean([v for v, c in zip(y, cert) if c])) if nc else None),
                  fmt(float(np.mean([v for v, c in zip(y, cert) if not c])) if nu else None)))
    out.append("  [%s] strata: %d tree x size strata, %d with both classes, %d dropped (one class only); per stratum c/u gap w: %s"
               % (label, len(strata), len(strata) - dropped, dropped,
                  "; ".join("%s:q%d %d/%d %s w%d" % (k[0], k[1], r["n_cert"], r["n_uncert"], fmt(r["gap"]) if r["gap"] is not None else "-", r["w"]) for k, r in strata.items())))
    out.append("  [%s] G (size-stratified gap, w = min) = %s; one-sided permutation p (%d within-stratum permutations, seed %d, (1+ge)/(1+N)) = %s; permutation SD of G %s; distinct permuted values %d"
               % (label, fmt(G), ctx.perm, SEED, "n/a" if p is None else "%.4f" % p, fmt(perm_sd), distinct))
    out.append("  [%s] beside: raw gap %s; depth-stratified gap (P9 strata x tree) %s; raw - G %s; OLS Y ~ cert + log n + depth + tree (HC1): cert %s (SE %.4f), log n %s (SE %.4f), depth %s (SE %.4f)"
               % (label, fmt(raw), fmt(Gd), fmt(raw - G) if raw is not None and G is not None else "n/a",
                  fmt(float(beta[1])), float(se[1]), fmt(float(beta[2])), float(se[2]), fmt(float(beta[3])), float(se[3])))
    return dict(G=G, p=p, raw=raw, Gd=Gd, nc=nc, nu=nu, perm_sd=perm_sd, distinct=distinct, dropped=dropped, strata=strata,
                beta_cert=float(beta[1]), se_cert=float(se[1]), y=y)


def support_lines(r, out):
    sd = float(np.std(r["y"], ddof=1)) if len(r["y"]) > 1 else float("nan")
    nc, nu = r["nc"], r["nu"]
    se = sd * math.sqrt(1.0 / max(1, nc) + 1.0 / max(1, nu)) * math.sqrt(DEFF) if nc and nu else float("nan")
    mde = Z80 * se
    n = nc + nu
    out.append("SUPPORT AS REALISED (registered (d)-(f) quoted, not re-derived: planning SD 0.10, ~60 certified / ~220 uncertified, DEFF 1.3 "
               "DECLARED PILOT ASSUMPTION, SE 0.0166, MDE80 0.041, verdict line SCOREABLE, thin): realised %d certified / %d uncertified "
               "sites; realised between-site SD of Y %.4f; realised SE = %.4f x sqrt(1/%d + 1/%d) x sqrt(1.3) = %.4f; n_eff = %d / 1.3 = %.0f "
               "(certified %.0f); MDE80 one-sided = 2.487 x %.4f = %.4f; measured permutation SD of G (within-stratum null) %s. "
               "Prediction-to-bar distance 0.05 vs realised MDE80 %.4f: %s (the post-run applies registered line (f))."
               % (nc, nu, sd, sd, nc, nu, se, n, n / DEFF, nc / DEFF, se, mde, fmt(r["perm_sd"]), mde,
                  "beyond the MDE" if 0.05 > mde else "NOT beyond the MDE"))
    return dict(sd=sd, se=se, mde=mde)


# ----------------------------------------------------------------------------------------------- modes
def header(ctx, out, mode):
    pins = script_pins()
    out.append("CERT-ALIGN-SIZE readout (%s); mode %s; script blob:%s sha256-lf16:%s (LF rendering, of record; sha256-crlf16:%s beside); date %s"
               % (REG, mode, pins["blob"], pins["lf16"], pins["crlf16"], datetime.date.today().isoformat()))
    out.append("POOL: none read (registration HYGIENE: TRAIN members only; no reserved-pool, eval or reserved_queries row). ZERO calls. data root %s"
               % ctx.data_root.replace("\\", "/"))
    return pins


def dry_run(ctx):
    out = []
    header(ctx, out, "--dry-run")
    for db in ("snapshots.db", MMLU["db"], NG["db"], "embeddings_cache.db"):
        p = ctx.path(db)
        wal = p + "-wal"
        out.append("  input %s: %s; -wal %s" % (db, "present" if os.path.exists(p) else "MISSING",
                                               ("%d bytes" % os.path.getsize(wal)) if os.path.exists(wal) else "absent"))
    infos = {}
    for arm in DECIDING + [a[0] for a in DESCRIPTIVE]:
        info = load_arm(ctx, arm, with_y=False)
        infos[arm] = info
        nc = sum(1 for s in info["sites"] if s["cert"])
        out.append("  %-20s role %-8s csv %s blob:%s sha256:%s snapshot %s; sites of record %d (%d certified, %d uncertified); graph split sites %d (no null row: %d %s); TRAIN members %d (all labelled; %d label rows); member slots %d, multi-holder slots %d (cosine-assigned)"
                   % (arm, ctx.arms[arm]["role"], info["null"]["path"], info["null"]["blob"], info["null"]["sha256"][:16], ctx.arms[arm]["snap"],
                      len(info["sites"]), nc, len(info["sites"]) - nc, info["n_sites_graph"], len(info["missing"]), info["missing"][:3],
                      info["members"], info["label_rows"], info["slots"], info["multi"]))
    dec = [s for a in DECIDING for s in infos[a]["sites"]]
    out.append("DENOMINATOR (deciding): sites of %s = %d (%d certified); the registration planned about 280 / about 60"
               % ("+".join(DECIDING), len(dec), sum(1 for s in dec if s["cert"])))
    analyse_pool(dec, ctx, out, "deciding", DECIDING)
    out.append("--dry-run: no Y computed, nothing written.")
    print("\n".join(out))
    return 0


def analyse(ctx):
    out = []
    pins = header(ctx, out, "--run")
    infos = {arm: load_arm(ctx, arm, with_y=True) for arm in DECIDING + [a[0] for a in DESCRIPTIVE]}
    for arm, info in infos.items():
        out.append("  input %-20s csv blob:%s sha256:%s snapshot %s; %d sites of record; entropy-0 sites %d %s; multi-holder slots %d of %d; graph sites without a null row %d %s"
                   % (arm, info["null"]["blob"], info["null"]["sha256"][:16], ctx.arms[arm]["snap"], len(info["sites"]),
                      len(info["zero_h"]), info["zero_h"][:4], info["multi"], info["slots"], len(info["missing"]), info["missing"][:3]))
    res = {}
    out.append("DECIDING POOL (CA1): the four anchor-free MMLU-Pro re-draw trees; denominator = their sites of record")
    dec = [s for a in DECIDING for s in infos[a]["sites"]]
    _, keys = analyse_pool(dec, ctx, out, "deciding", DECIDING)
    r = gap_block(dec, keys, ctx, out, "deciding")
    res["deciding"] = r
    sup = support_lines(r, out)
    for arm in [a[0] for a in DESCRIPTIVE]:
        out.append("DESCRIPTIVE ARM %s (%s; size quintiles over the arm's own sites)" % (arm, ctx.arms[arm]["role"]))
        ss = infos[arm]["sites"]
        _, k2 = analyse_pool(ss, ctx, out, arm, [arm])
        res[arm] = gap_block(ss, k2, ctx, out, arm)
    ng = res["ng_af_s42"]
    p9_ok = bool(ng["raw"] is not None and ng["Gd"] is not None and abs(round(ng["raw"], 4) - P9_RECORD["raw"]) < 1e-9
                 and abs(round(ng["Gd"], 4) - P9_RECORD["strat"]) < 1e-9)
    out.append("LOADER CHECK (20NG main tree vs the record's P9, L11490): raw %s (record %+.4f), depth-stratified %s (record %+.4f): %s"
               % (fmt(ng["raw"]), P9_RECORD["raw"], fmt(ng["Gd"]), P9_RECORD["strat"], "REPRODUCED" if p9_ok else "NOT REPRODUCED"))
    # ------------------------------------------------------------------ criteria (every branch printed)
    G, p = r["G"], r["p"]
    verdict = ca1_decide(G, p)
    out.append("CRITERIA AND PREDICTIONS")
    if verdict == "ALIGNED-BEYOND-SIZE":
        out.append("CA1 (DECIDING; ALIGNED-BEYOND-SIZE iff G > 0 AND p <= 0.05): ALIGNED-BEYOND-SIZE -- G %s, p %.4f (%d certified / %d uncertified sites, %d strata dropped)"
                   % (fmt(G), p, r["nc"], r["nu"], r["dropped"]))
        out.append("F-CA (fires iff CA1 SIZE-ONLY): NOT FIRED")
    else:
        why = ("G cannot be formed (no tree x size stratum holds both classes)" if G is None else
               "G %s <= 0" % fmt(G) if not bool(G > 0) else "p %.4f > 0.05" % p)
        out.append("CA1 (DECIDING; ALIGNED-BEYOND-SIZE iff G > 0 AND p <= 0.05): SIZE-ONLY -- %s (G %s, p %s; %d certified / %d uncertified sites, %d strata dropped)"
                   % (why, fmt(G), "n/a" if p is None else "%.4f" % p, r["nc"], r["nu"], r["dropped"]))
        out.append("F-CA (fires iff CA1 SIZE-ONLY): FIRED -- on MMLU-Pro, site certification carries no declared-category alignment beyond "
                   "what site size explains; memo change 10 is limited to 'a statement about the split's geometry, not about its agreement "
                   "with declared categories'; alignment with declared categories is not the only kind of real structure.")
    p1 = in_band(G, P1_BAND)
    brier = (P1_PROB - (1.0 if verdict == "ALIGNED-BEYOND-SIZE" else 0.0)) ** 2
    out.append("P1 G %s in [%.2f, %.2f]: %s; CA1 ALIGNED-BEYOND-SIZE predicted at %.2f, occurred: %s, Brier %.4f"
               % (fmt(G), P1_BAND[0], P1_BAND[1], "HELD" if p1 else "FAILED", P1_PROB, "yes" if verdict == "ALIGNED-BEYOND-SIZE" else "no", brier))
    d2 = (r["raw"] - G) if (r["raw"] is not None and G is not None) else None
    out.append("P2 raw - G = %s in [%.2f, %.2f]: %s" % (fmt(d2), P2_BAND[0], P2_BAND[1], "HELD" if in_band(d2, P2_BAND) else "FAILED"))
    g3 = res["ng_af_s42"]["G"]
    out.append("P3 20NG size-stratified gap (ng_af_s42, descriptive, SEEN arm) %s in [%.2f, %.2f]: %s" % (fmt(g3), P3_BAND[0], P3_BAND[1], "HELD" if in_band(g3, P3_BAND) else "FAILED"))
    g4 = res["o0_clean_s42"]["G"]
    out.append("P4 o0_clean_s42 [AN] G (descriptive) %s in [%.2f, %.2f]: %s" % (fmt(g4), P4_BAND[0], P4_BAND[1], "HELD" if in_band(g4, P4_BAND) else "FAILED"))
    out.append("DESCRIPTIVE T1b (ng_af_bareq512_s42): G %s, p %s, %d certified (registered: 1 of 97)"
               % (fmt(res["ng_af_bareq512_s42"]["G"]), "n/a" if res["ng_af_bareq512_s42"]["p"] is None else "%.4f" % res["ng_af_bareq512_s42"]["p"], res["ng_af_bareq512_s42"]["nc"]))
    out.append("WHAT THIS RESULT DOES NOT SHOW (registered): that certified splits are 'correct'; anything about G12's 0 of 60; FDR-corrected certification; the [AN] or 20NG arms as decisive; any judge or routing quantity.")
    return out, dict(verdict=verdict, res=res, p1=p1, brier=brier, d2=d2, p9_ok=p9_ok, support=sup, pins=pins)


def default_out():
    d = "E:/TaxoArena_backup_%s_cert_align_size" % datetime.date.today().isoformat()
    return os.path.join(d, "cert_align_size_outcome.txt")


def run(ctx, out_path):
    sums = os.path.join(os.path.dirname(os.path.abspath(out_path)), "SHA256SUMS.txt")
    for p in (out_path, sums):
        if os.path.exists(p):
            die("%s exists: the outcome of record is WRITE-ONCE (never overwritten, never re-run over)" % p)
    lines, r = analyse(ctx)
    if not r["p9_ok"]:
        print("\n".join(lines))
        die("the 20NG loader check does not reproduce P9's recorded raw / depth-stratified gaps: the site Y differs from the record's; nothing written")
    text = "\n".join(lines) + "\n"
    print(text, end="")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    h = sha256_file(out_path)
    with open(sums, "x", encoding="utf-8", newline="\n") as f:
        f.write("%s  %s\n" % (h, os.path.basename(out_path)))
    print("[CERT-ALIGN-SIZE] wrote %s (sha256 %s) and %s (write-once; never committed)" % (out_path.replace("\\", "/"), h, sums.replace("\\", "/")))
    return 0


# ----------------------------------------------------------------------------------------------- selftest
def _fixture(root, plan, dup_label=False):
    """Writes snapshots.db / label DBs / embeddings_cache.db / site-null CSVs under root.
    plan: arm -> list of site specs dict(n, cert, defl, kind in {'aligned','mixed','zero','multi'}).
    Tree per arm: root (depth 0) -> one depth-1 site per spec (2 leaves each). The root is a site of record too (cert False);
    each site's members are disjoint; 'aligned' = child A all label a, child B all label b (Y = 1); 'mixed' = both
    children half a / half b (Y = 0); 'zero' = one label only (entropy 0 -> Y = 0); 'multi' = aligned, plus one member held
    by BOTH children whose vector points at child B (cosine) and whose label is b (Y stays 1; first-holder -> child A, Y < 1)."""
    os.makedirs(root, exist_ok=True)
    snap = sqlite3.connect(os.path.join(root, "snapshots.db"))
    snap.execute("CREATE TABLE snapshots (id TEXT, graph TEXT, reserved_queries TEXT)")
    mm = sqlite3.connect(os.path.join(root, MMLU["db"])); mm.execute("CREATE TABLE mmlu_pro (id INTEGER PRIMARY KEY, question TEXT, category TEXT)")
    ng = sqlite3.connect(os.path.join(root, NG["db"])); ng.execute("CREATE TABLE twenty_newsgroups (id INTEGER PRIMARY KEY, question TEXT, category TEXT)")
    emb = sqlite3.connect(os.path.join(root, "embeddings_cache.db")); emb.execute("CREATE TABLE embeddings (query TEXT, vector BLOB)")
    arms = {}
    rid = [0]
    D = 4
    muA = [1.0, 0.0, 0.0, 0.0]; muB = [0.0, 1.0, 0.0, 0.0]
    for arm, specs in plan.items():
        spec = dict(ARMS[arm])
        csv_rel = "nulls/site_null_%s.csv" % arm
        spec["csv"] = csv_rel; spec["blob"] = None
        db = mm if spec["labels"] is MMLU else ng
        table = spec["labels"]["table"]
        nodes = []; csv_rows = []
        kid_ids = []
        nid = [1]

        def new_id():
            nid[0] += 1
            return "n%08d" % nid[0]
        for si, sp in enumerate(specs):
            sid = new_id(); a = new_id(); b = new_id()
            kid_ids.append(sid)
            half = sp["n"] // 2
            qa = []; qb = []
            for j in range(sp["n"]):
                t = "%s site%d doc%d" % (arm, si, j)
                inA = j < half
                if sp["kind"] == "aligned" or sp["kind"] == "multi":
                    c = ("a%d" % si) if inA else ("b%d" % si)
                elif sp["kind"] == "mixed":
                    c = ("a%d" % si) if (j % 2 == 0) else ("b%d" % si)
                else:
                    c = "z%d" % si
                rid[0] += 1
                db.execute("INSERT INTO %s (id, question, category) VALUES (?,?,?)" % table, (rid[0], t, c.upper() if spec["labels"]["lower"] else c))
                (qa if inA else qb).append(qid(t))
            if dup_label and si == 0:
                # a duplicated text: first row (lower id) carries the TRUE label of an existing member, a later row a wrong one
                t0 = "%s site%d doc%d" % (arm, si, 0)
                rid[0] += 1
                db.execute("INSERT INTO %s (id, question, category) VALUES (?,?,?)" % table, (rid[0], t0, "WRONG"))
            if sp["kind"] == "multi":
                t = "%s site%d shared" % (arm, si)
                rid[0] += 1
                db.execute("INSERT INTO %s (id, question, category) VALUES (?,?,?)" % table, (rid[0], t, ("b%d" % si).upper() if spec["labels"]["lower"] else "b%d" % si))
                q = qid(t); qa.append(q); qb.append(q)
                emb.execute("INSERT INTO embeddings VALUES (?,?)", (t, struct.pack(">%df" % D, 0.1, 0.9, 0.0, 0.0)))
            n_site = len(set(qa) | set(qb))
            nodes.append(dict(id=sid, depth=1, childIds=[a, b], queryIds=[], vmfMu=[0.5, 0.5, 0, 0]))
            nodes.append(dict(id=a, depth=2, childIds=[], queryIds=qa, vmfMu=muA))
            nodes.append(dict(id=b, depth=2, childIds=[], queryIds=qb, vmfMu=muB))
            csv_rows.append(dict(node_id=sid, depth=1, n=n_site, cert=sp["cert"], defl=sp.get("defl", sp["cert"])))
        rootn = sum(r["n"] for r in csv_rows)
        nodes.insert(0, dict(id="n00000001", depth=0, childIds=kid_ids, queryIds=[], vmfMu=[0.5, 0.5, 0, 0]))
        csv_rows.insert(0, dict(node_id="n00000001", depth=0, n=rootn, cert=False, defl=False))
        snap.execute("INSERT INTO snapshots VALUES (?,?,?)", (spec["snap"], json.dumps(dict(rootId="n00000001", nodes=nodes)), "[]"))
        os.makedirs(os.path.join(root, "nulls"), exist_ok=True)
        with open(os.path.join(root, csv_rel), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["snapshot_id", "node_id", "label", "depth", "n", "k", "cert_site_p95", "cert_deflated_p95", "reps"])
            for r in csv_rows:
                w.writerow([spec["snap"], r["node_id"], "x", r["depth"], r["n"], 2, "true" if r["cert"] else "false", "true" if r["defl"] else "false", REPS])
        arms[arm] = spec
    for c in (snap, mm, ng, emb):
        c.commit(); c.close()
    return arms


def _site(n, cert, kind, defl=None):
    return dict(n=n, cert=cert, kind=kind, defl=cert if defl is None else defl)


def _plan_aligned():
    """F1: pooled quintiles put n 20/21/40 in q0, 80 in q1, 160 in q2, 320 in q3 and each root alone in q4 (dropped).
    Per tree: q0 = multi C, aligned C, zero U, mixed U, aligned C x2, mixed U x2 (gap 1, w 4); q1 = 2 C aligned / 2 U mixed
    (gap 1, w 2); q2 the same in af_clean_s42 / af_s137, but af_s2048 has 4 CERTIFIED MIXED and af_s42_o1 4 UNCERTIFIED
    ALIGNED (both dropped when crossed with tree; pooled across trees they would give gap 0, w 8: M2); q3 = 3 C aligned / 1 U
    aligned (gap 0, w min 1, max 3: M1). Expected G = (2(4+2+2) + 2(4+2)) / (2(4+2+2+1) + 2(4+2+1)) = 28/32 = 0.875
    (max weights 28/40 = 0.700; uncrossed 24/36 = 0.667; zero site dropped 26/30 = 0.867). The cert_deflated_p95 flag
    is the OPPOSITE of cert_site_p95 everywhere (M10)."""
    plan = {}
    for arm in DECIDING:
        s = [_site(20, True, "multi", defl=False), _site(20, True, "aligned", defl=False), _site(20, False, "zero", defl=True), _site(20, False, "mixed", defl=True)]
        for n in (40, 80):
            s += [_site(n, True, "aligned", defl=False)] * 2 + [_site(n, False, "mixed", defl=True)] * 2
        if arm == "af_s2048":
            s += [_site(160, True, "mixed", defl=False)] * 4
        elif arm == "af_s42_o1":
            s += [_site(160, False, "aligned", defl=True)] * 4
        else:
            s += [_site(160, True, "aligned", defl=False)] * 2 + [_site(160, False, "mixed", defl=True)] * 2
        s += [_site(320, True, "aligned", defl=False)] * 3 + [_site(320, False, "aligned", defl=True)]
        plan[arm] = s
    plan["o0_clean_s42"] = [_site(n, c, k) for n in (20, 40, 80, 160, 320) for c, k in ((True, "aligned"), (False, "mixed"), (False, "aligned"))]
    plan["ng_af_s42"] = [_site(n, c, "aligned" if c else "mixed") for n in (20, 40, 80, 160, 320) for c in (True, False, False)]
    plan["ng_af_bareq512_s42"] = [_site(n, c, "mixed") for n in (20, 40, 80, 160, 320) for c in (n == 320, False)]
    return plan


def _plan_nocontrast():
    """F5: no deciding site is certified -> G cannot be formed -> SIZE-ONLY with the reason, F-CA FIRED."""
    plan = _plan_aligned()
    for arm in DECIDING:
        plan[arm] = [dict(s, cert=False, defl=False) for s in plan[arm]]
    return plan


def _plan_size_only():
    """F2: certified sites are LARGE and aligned, uncertified SMALL and mixed, plus inside each stratum certified and
    uncertified have the SAME Y -> G = 0 exactly and every within-stratum permutation ties (p = 1; a shuffle across strata
    does not: M4), raw gap large -> SIZE-ONLY, F-CA FIRED."""
    plan = {}
    for arm in DECIDING:
        s = []
        for n in (20, 40):
            s += [_site(n, False, "mixed")] * 3 + [_site(n, True, "mixed")]
        s += [_site(80, False, "mixed"), _site(80, True, "mixed")] * 2
        for n in (160, 320):
            s += [_site(n, True, "aligned")] * 3 + [_site(n, False, "aligned")]
        plan[arm] = s
    plan["o0_clean_s42"] = _plan_aligned()["o0_clean_s42"]
    plan["ng_af_s42"] = _plan_aligned()["ng_af_s42"]
    plan["ng_af_bareq512_s42"] = _plan_aligned()["ng_af_bareq512_s42"]
    return plan


def _plan_pertree():
    """F3 (M3, pooled vs per-tree quintiles): two trees carry only small sites, two only large ones. Pooled quintiles put
    the small trees' sites in q0/q1 and the large trees' in q3/q4; per-tree quintiles would spread each tree over q0..q4."""
    plan = {}
    for i, arm in enumerate(DECIDING):
        sizes = (20, 22, 24, 26, 28) if i < 2 else (300, 330, 360, 390, 420)
        plan[arm] = [_site(n, c, "aligned" if c else "mixed") for n in sizes for c in (True, False)]
    plan["o0_clean_s42"] = _plan_aligned()["o0_clean_s42"]
    plan["ng_af_s42"] = _plan_aligned()["ng_af_s42"]
    plan["ng_af_bareq512_s42"] = _plan_aligned()["ng_af_bareq512_s42"]
    return plan


def _capture(fn, *a):
    buf = io.StringIO()
    rc = None
    with redirect_stdout(buf):
        try:
            rc = fn(*a)
        except Refused as e:
            rc = ("refused", e.code)
    return rc, buf.getvalue()


def _line(text, prefix):
    ls = [l for l in text.splitlines() if l.startswith(prefix)]
    assert len(ls) == 1, (prefix, ls)
    return ls[0]


def selftest():
    global P9_RECORD
    checks = 0
    saved_p9 = dict(P9_RECORD)
    with scratch_dir.scratch("cert_align_size_selftest") as tmp:
        # ---------------- F1: ALIGNED-BEYOND-SIZE on the real --run entry point (expected values derived in _plan_aligned)
        r1 = os.path.join(tmp, "f1")
        arms = _fixture(r1, _plan_aligned())
        ctx = Ctx(data_root=r1, perm=2000, arms=arms, check_blobs=False)
        _LABEL_CACHE.clear()
        _, pre = analyse(ctx)                     # the fixture's own 20NG gaps stand in for the record's P9 values
        P9_RECORD = dict(raw=round(pre["res"]["ng_af_s42"]["raw"], 4), strat=round(pre["res"]["ng_af_s42"]["Gd"], 4))
        outp = os.path.join(tmp, "f1_out", "outcome.txt")
        rc, txt = _capture(main, ["--run", "--out", outp], ctx)
        assert rc == 0, (rc, txt[-2000:]); checks += 1
        ca1 = _line(txt, "CA1 ")
        assert "): ALIGNED-BEYOND-SIZE -- G +0.8750, p 0.0005 (44 certified / 40 uncertified sites, 6 strata dropped)" in ca1, ca1; checks += 1   # M1 M2 M9 M11
        assert _line(txt, "F-CA ") == "F-CA (fires iff CA1 SIZE-ONLY): NOT FIRED"; checks += 1
        assert _line(txt, "P1 ") == "P1 G +0.8750 in [0.00, 0.12]: FAILED; CA1 ALIGNED-BEYOND-SIZE predicted at 0.55, occurred: yes, Brier 0.2025", _line(txt, "P1 "); checks += 1
        assert "(tree total 11 cert / 10 uncert)" in _line(txt, "    af_clean_s42 "); checks += 1                          # M10, M18
        assert _line(txt, "    af_s2048 ").startswith("    af_s2048             q0 4/4  q1 2/2  q2 4/0  q3 3/1  q4 0/1"), _line(txt, "    af_s2048 "); checks += 1   # M3
        yl = _line(txt, "  [deciding] Y: ")
        assert "84 sites (44 certified, 40 uncertified); entropy-0 sites (Y = 0, kept): 4;" in yl, yl; checks += 1
        gl = _line(txt, "  [deciding] G ")
        p_val = float(gl.split("(1+ge)/(1+N)) = ")[1].split(";")[0])
        assert p_val == round(1 / 2001, 4) and "2000 within-stratum permutations, seed 20261004" in gl, gl; checks += 1   # M5 M6
        bl = _line(txt, "  [deciding] beside: ")
        raw_v = float(bl.split("raw gap ")[1].split(";")[0])
        assert 0.5 < raw_v < 0.71, bl; checks += 1                                                  # M14 (0.909 - (8 + sum r)/40)
        assert _line(txt, "P4 ") == "P4 o0_clean_s42 [AN] G (descriptive) +0.5000 in [-0.03, 0.07]: FAILED", _line(txt, "P4 "); checks += 1   # M15
        assert _line(txt, "P3 ") == "P3 20NG size-stratified gap (ng_af_s42, descriptive, SEEN arm) +1.0000 in [0.00, 0.12]: FAILED", _line(txt, "P3 "); checks += 1
        assert _line(txt, "P2 ").endswith("FAILED") and abs(float(_line(txt, "P2 ").split("raw - G = ")[1].split(" ")[0]) - (raw_v - 0.875)) < 2e-4; checks += 1
        assert _line(txt, "LOADER CHECK").endswith(": REPRODUCED"); checks += 1
        sl = _line(txt, "SUPPORT AS REALISED")
        assert "realised 44 certified / 40 uncertified sites" in sl and "n_eff = 84 / 1.3 = 65 (certified 34)" in sl, sl; checks += 1
        assert _line(txt, "DESCRIPTIVE T1b").startswith("DESCRIPTIVE T1b (ng_af_bareq512_s42): G +0.0000, p 1.0000, 1 certified"), _line(txt, "DESCRIPTIVE T1b"); checks += 1
        # write-once (M13)
        body = open(outp, encoding="utf-8").read()
        assert body.splitlines()[-1].startswith("WHAT THIS RESULT DOES NOT SHOW") and _line(body, "CA1 ") == ca1; checks += 1
        sums = open(os.path.join(os.path.dirname(outp), "SHA256SUMS.txt"), encoding="utf-8").read()
        assert sums == "%s  outcome.txt\n" % sha256_file(outp); checks += 1
        rc2, txt2 = _capture(main, ["--run", "--out", outp], ctx)
        assert rc2 == ("refused", 2) and "WRITE-ONCE" in txt2 and open(outp, encoding="utf-8").read() == body; checks += 1
        # dry-run: pins + denominators + counts, no Y, nothing written
        rc3, txt3 = _capture(main, ["--dry-run"], ctx)
        assert rc3 == 0 and "DENOMINATOR (deciding): sites of af_clean_s42+af_s137+af_s2048+af_s42_o1 = 84 (44 certified)" in txt3, txt3[-1500:]; checks += 1
        assert "[deciding] Y:" not in txt3 and txt3.rstrip().endswith("--dry-run: no Y computed, nothing written."); checks += 1
        assert "multi-holder slots 1 (cosine-assigned)" in _line(txt3, "  af_clean_s42 "); checks += 1
        assert txt3.splitlines()[1].startswith("POOL: none read") and "sha256-lf16:" in txt3.splitlines()[0]; checks += 1
        # per-site Y: the multi site is 1 only under cosine assignment (M11); the zero site Y = 0 and listed (M9)
        _LABEL_CACHE.clear()
        info = load_arm(ctx, "af_clean_s42", with_y=True)
        ys = {x["node"]: x["y"] for x in info["sites"]}
        assert abs(ys["n00000002"] - 1.0) < 1e-12, ys["n00000002"]; checks += 1
        assert ys["n00000008"] == 0.0 and info["zero_h"] == ["n00000008"]; checks += 1
        assert info["multi"] == 1; checks += 1

        # ---------------- F2: SIZE-ONLY by size confounding; G = 0 exactly; F-CA FIRED (M12); within-stratum ties -> p 1 (M4)
        r2 = os.path.join(tmp, "f2")
        arms2 = _fixture(r2, _plan_size_only())
        ctx2 = Ctx(data_root=r2, perm=500, arms=arms2, check_blobs=False)
        _LABEL_CACHE.clear()
        rc, txt = _capture(main, ["--run", "--out", os.path.join(tmp, "f2_out", "o.txt")], ctx2)
        assert rc == 0, txt[-2000:]; checks += 1
        assert "): SIZE-ONLY -- G +0.0000 <= 0 (G +0.0000, p 1.0000; 40 certified / 44 uncertified sites, 4 strata dropped)" in _line(txt, "CA1 "), _line(txt, "CA1 "); checks += 1
        assert _line(txt, "F-CA ").startswith("F-CA (fires iff CA1 SIZE-ONLY): FIRED -- on MMLU-Pro, site certification carries no declared-category alignment"); checks += 1
        assert _line(txt, "P1 ") == "P1 G +0.0000 in [0.00, 0.12]: HELD; CA1 ALIGNED-BEYOND-SIZE predicted at 0.55, occurred: no, Brier 0.3025", _line(txt, "P1 "); checks += 1
        p2 = _line(txt, "P2 ")
        assert float(p2.split("raw - G = ")[1].split(" in ")[0]) > 0.29 and p2.endswith("FAILED"), p2; checks += 1

        # ---------------- F5: no contrast -> SIZE-ONLY with the reason; F-CA FIRED; P1/P2 n/a FAILED
        r5 = os.path.join(tmp, "f5")
        arms5 = _fixture(r5, _plan_nocontrast())
        _LABEL_CACHE.clear()
        rc, txt = _capture(main, ["--run", "--out", os.path.join(tmp, "f5_out", "o.txt")], Ctx(data_root=r5, perm=50, arms=arms5, check_blobs=False))
        assert rc == 0, txt[-2000:]; checks += 1
        assert "): SIZE-ONLY -- G cannot be formed (no tree x size stratum holds both classes) (G n/a, p n/a; 0 certified / 84 uncertified sites, 20 strata dropped)" in _line(txt, "CA1 "), _line(txt, "CA1 "); checks += 1
        assert _line(txt, "F-CA ").startswith("F-CA (fires iff CA1 SIZE-ONLY): FIRED"); checks += 1
        assert _line(txt, "P1 ").startswith("P1 G n/a in [0.00, 0.12]: FAILED") and _line(txt, "P2 ") == "P2 raw - G = n/a in [0.00, 0.10]: FAILED"; checks += 1

        # ---------------- F3: pooled (not per-tree) quintiles (M3)
        r3 = os.path.join(tmp, "f3")
        arms3 = _fixture(r3, _plan_pertree())
        _LABEL_CACHE.clear()
        rc, txt = _capture(main, ["--dry-run"], Ctx(data_root=r3, perm=10, arms=arms3, check_blobs=False))
        assert rc == 0, txt[-1500:]; checks += 1
        assert "q0 3/3  q1 2/2  q2 0/1  q3 0/0  q4 0/0" in _line(txt, "    af_clean_s42 "), _line(txt, "    af_clean_s42 "); checks += 1
        assert "q0 0/0  q1 0/0  q2 1/1  q3 3/3  q4 1/2" in _line(txt, "    af_s2048 "), _line(txt, "    af_s2048 "); checks += 1

        # ---------------- the decide path at its boundaries (M7 M8): the function the --run branch calls
        assert ca1_decide(0.0, 0.001) == "SIZE-ONLY"; checks += 1
        assert ca1_decide(1e-9, 0.05) == "ALIGNED-BEYOND-SIZE"; checks += 1
        assert ca1_decide(0.2, 0.0501) == "SIZE-ONLY" and ca1_decide(None, None) == "SIZE-ONLY"; checks += 1
        assert ca1_decide(np.float64(0.1), np.float64(0.01)) == "ALIGNED-BEYOND-SIZE"; checks += 1    # numpy scalars (TOPIC-PARTITION D1)

        # ---------------- refusals: blob pin (M16), -wal, reps, non-site rows, unlabelled member; duplicate label (M17); P9 loader check
        ctxb = Ctx(data_root=r1, perm=10, arms={a: dict(v, blob="0" * 40) for a, v in arms.items()}, check_blobs=True)
        rc, txt = _capture(main, ["--dry-run"], ctxb)
        assert rc == ("refused", 2) and "the site null of record is blob:" + "0" * 40 in txt; checks += 1
        open(os.path.join(r1, "snapshots.db-wal"), "wb").write(b"x")
        rc, txt = _capture(main, ["--dry-run"], ctx)
        assert rc == ("refused", 2) and "snapshots.db-wal is 1 bytes" in txt; checks += 1
        os.remove(os.path.join(r1, "snapshots.db-wal"))
        csvp = os.path.join(r1, arms["af_s137"]["csv"])
        rows_ = open(csvp, encoding="utf-8", newline="").read()
        open(csvp, "w", encoding="utf-8", newline="").write(rows_.replace(",300\r\n", ",299\r\n", 1))
        rc, txt = _capture(main, ["--dry-run"], ctx)
        assert rc == ("refused", 2) and "only 300-rep nulls" in txt, txt[-500:]; checks += 1
        open(csvp, "w", encoding="utf-8", newline="").write(rows_ + "%s,n99999999,x,1,4,2,true,true,300\r\n" % arms["af_s137"]["snap"])
        rc, txt = _capture(main, ["--dry-run"], ctx)
        assert rc == ("refused", 2) and "site-null rows for non-sites ['n99999999']" in txt, txt[-500:]; checks += 1
        open(csvp, "w", encoding="utf-8", newline="").write(rows_)
        con = sqlite3.connect(os.path.join(r1, MMLU["db"])); con.execute("DELETE FROM mmlu_pro WHERE question = 'af_s137 site3 doc1'"); con.commit(); con.close()
        _LABEL_CACHE.clear()
        rc, txt = _capture(main, ["--dry-run"], ctx)
        assert rc == ("refused", 2) and "af_s137: 1 site members carry no label" in txt, txt[-500:]; checks += 1
        r4 = os.path.join(tmp, "f4")
        arms4 = _fixture(r4, _plan_aligned(), dup_label=True)
        _LABEL_CACHE.clear()
        lab, _, _ = load_labels(Ctx(data_root=r4), MMLU)
        assert lab[qid("af_clean_s42 site0 doc0")] == "a0"; checks += 1
        P9_RECORD = dict(raw=0.1215, strat=0.0740)
        _LABEL_CACHE.clear()
        o5 = os.path.join(tmp, "f4_out", "o.txt")
        rc, txt = _capture(main, ["--run", "--out", o5], Ctx(data_root=r4, perm=50, arms=arms4, check_blobs=False))
        assert rc == ("refused", 2) and "NOT REPRODUCED" in txt and not os.path.exists(o5); checks += 1
    P9_RECORD = saved_p9
    _LABEL_CACHE.clear()
    assert checks == SELFTEST_CHECKS, "selftest ran %d checks, pinned %d" % (checks, SELFTEST_CHECKS)
    print("[CERT-ALIGN-SIZE] SELFTEST OK: %d value-asserting checks (pinned %d); mutant table:%s" % (checks, SELFTEST_CHECKS, MUTANTS))
    return 0


# ----------------------------------------------------------------------------------------------- main
def main(argv=None, ctx=None):
    ap = argparse.ArgumentParser(description="CERT-ALIGN-SIZE readout (zero calls; reads no pool)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--data-root", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if ctx is None:
        ctx = Ctx(data_root=os.path.abspath(a.data_root) if a.data_root else ROOT)
    if a.dry_run:
        return dry_run(ctx)
    return run(ctx, a.out or default_out())


if __name__ == "__main__":
    sys.exit(main())
