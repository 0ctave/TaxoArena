"""cert_positive_control.py: CERT-POSITIVE-CONTROL, the label file, the dry-run, the launch command and the READOUT of the
declared-site arm (SeparationNullBySizeTest `certPositiveControl - ...`, gradle task certPositiveControl). ZERO calls.

REGISTRATION OF RECORD (it governs; this docstring restates it and never replaces it): docs/judge_v2_program.md
"## Registered 2026-10-02 (before any code or call) — CERT-POSITIVE-CONTROL: does the site-null certificate that left R2's
MMLU-Pro member with 0 of 60 sites (G12) certify the DECLARED 14-category level, ..." (span L23464-L23488 as registered);
record docs/agents/results/CERT-POSITIVE-CONTROL.json; go plan Amendment 38.
  I-1 / I-2 (identity preconditions, refuse, no readout). C0 (comparability precondition of PC1): 300 random size-matched
  relabellings of the 14 groups scored by the same routine; PC1 NOT EVALUABLE if their p95 reaches the site null's p95.
  PC1 (DECIDING; the POINT of the exceedance count decides, one site, no family): k_d = replicates >= the declared statistic,
  p_d = (k_d + 1) / 301; CERTIFIED iff p_d <= 0.05 (k_d <= 14); NOT CERTIFIED otherwise; NOT EVALUABLE iff C0 fails.
  PC3 (DESCRIPTIVE-ONLY): the src partition inside each of the 14 anchors (src < 55 TRAIN items pooled into one child; an
  anchor left with < 2 children not scored, count printed), BH over the scored TOP family (cert_resolution's bh_cutoff).
  DESCRIPTIVE beside: the deflated-null variants; the declared statistic against the null's p50 / p95 / max; G12's TOP-site
  statistics beside. Predictions P1-P3 (Brier); falsifier F-PC fires iff PC1 CERTIFIED; reading table fixed.

INSTRUMENT. The siteNull generator and splitter, seeds and convention (SeparationNullBySizeTest; see the arm's KDoc); the
statistic = the splitter's own call on a GIVEN partition (declaredSiteStatistic). Launched as G12 was (g12_site_null.py
blob:0cf5b091; its config experiment_configs/rp12_r2/B0/g12_site_null.sitenull supplies sliceDim 512, sepBar 0.0145, dropTop
0, whiten false, 300 reps, 12 threads, the pointer and the stamp); read with cert_resolution.py (blob:dbe9425d: p_site,
bh_cutoff) imported, never copied (both LF blobs asserted at import).

LAUNCH SEQUENCE (run-operator; a site null = a rule-7 heavy process: W1-W5, 12 JVM threads, never beside a construction,
another site null or a pool reader; the pool check in the B0-2 form first):
  python tools/analysis/cert_positive_control.py --selftest
  python tools/analysis/cert_positive_control.py --mutants
  python tools/analysis/v2_union_pool.py --dry-run                      (rc 0; pool file sha256-lf16 79d48f4b36434a55)
  python tools/analysis/cert_positive_control.py --dry-run  [--data-root DIR]   population, groups, labels, I-1 preview,
                                                            I-2 targets, PC3 preview, heap, wall estimate, COMMAND; writes nothing
  python tools/analysis/cert_positive_control.py --prepare  [--data-root DIR]   writes the label file (write-once)
  python tools/analysis/cert_positive_control.py --hashes before [--data-root DIR]   embeddings_cache.db per-table hashes (x)
  <the printed COMMAND, from the data root's checkout: .\\gradlew.bat certPositiveControl ...>
  python tools/analysis/cert_positive_control.py --hashes after  [--data-root DIR]
  python tools/analysis/cert_positive_control.py --analyze      the outcome (write-once, mode x):
        experiment_results/cert_positive_control/outcome.txt and cpc_sites.csv; refuses a REFUSED / partial arm, a hash
        change, an identity failure, a label file other than the one the arm read, an instrument other than the registered.
  --data-root DIR = the checkout holding snapshots.db (with the member's snapshot), embeddings_cache.db and
  multicorpus_cache_v1.db (default TAXOARENA_DATA_ROOT, else this checkout); the raw MMLU-Pro leaderboard samples are found
  under the data root, this checkout or the main checkout.

POOL: the B0-2 pool check is the operator's (above); this script opens no pool table. --dry-run / --prepare / --hashes are
rule-7 READERS of embeddings_cache.db (they refuse while any java.exe runs); --analyze opens no DB.

BUILDER'S READINGS (each flagged to the registrar; printed in the outcome header):
  CR-1 the declared labels: category = corpus_questions.domain of the tree query's query_id (multicorpus_cache_v1.db, source
       MMLU_PRO), cross-checked against queries.ground_truth_category == "MMLU_PRO_LB/" + domain (a disagreement REFUSES);
       every item must sit on side TRAIN of the draw-5a3e756 side export (else REFUSED: no EVAL item anywhere).
  CR-2 src = MMLU-GOLD-GEOMETRY's join (mmlu_gold_geometry.assemble: options key, never text; its exclusions); an item it
       excludes (no src / multi-src / multi-domain) carries no src and is POOLED in PC3 with the small sources, so the scored
       population equals the anchor's site-null population (n as in G12_sites.csv).
  CR-3 C0 "reaches" = C0 p95 >= the plain null p95 (the Kotlin percentile convention, rank ceil(0.95 x 300) = 285); C0 is a
       precondition: when it fails PC1 reads NOT EVALUABLE whatever p_d is (the three readings are exclusive, as the
       registered probabilities 0.85 + 0.12 + 0.03 = 1 require).
  CR-4 P1's interval is scored only when PC1 is evaluable; the three-way PC1 probabilities are scored by the multi-category
       Brier sum (p_i - o_i)^2 over the three readings. P2's event is C0 p95 < null p05 (strict; rank 15).
  CR-5 I-2 re-runs ALL 14 anchors' plain nulls (PC3 needs their replicates): the three registered sites decide I-2 (refuse on a
       mismatch); the other 11 are printed beside. The I-2 rows' "persisted" column carries G12's k, "recomputed" the re-run k.
  CR-6 C0 seed 20261002 (fixed now); the src children ordered by name, the pooled child last.

REGISTRATION DEFECT D-I1 (reported to the registrar, NOT resolved in code): I-1 as registered ("the declared-site routine
applied to each of G12's 60 accepted sites' own routed partitions reproduces the persisted dasguptaDeltaNorm to the printed
digits") cannot pass by construction: the persisted value is computed on the routed partition AT THE SPLIT, and the snapshot
persists only the children's FINAL regions (re-routed over the later iterations, multi-assigned items in two children). A
numpy replica of the routine (--dry-run's I-1 preview) reproduces 6 of 60 (the sites whose child regions never changed, to
1e-15) and misses 54. The arm therefore refuses under the registered form. A LIVE leg is built beside it: each site's real
population through the production splitSingleNode, the routine on the routed children must return the splitter's own
dasguptaDeltaNorm bit for bit; it becomes the gate only with -Di1Form=live -Di1Bracket="<the registrar's bracket>", which the
arm prints and records, and --analyze prints.

SELFTEST (python tools/analysis/cert_positive_control.py --selftest): every registered branch is executed through the real entry
points (analyze(), build_labels(), dry-run helpers) on fixtures whose answer is known by hand, asserting the printed VALUE:
PC1 CERTIFIED at the boundary k_d = 14 and NOT CERTIFIED at 15; a tie counts (>=); NOT EVALUABLE at C0 p95 == null p95;
F-PC FIRED / NOT FIRED; the three reading sentences; P1 HELD / FAILED / NOT SCORED; P2 event true / false; P3 HELD / FAILED;
PC3 BH set (4 of 12 at the r = 4 step) and the empty set; unscored anchors counted; I-1 registered refusal (6 of 60), the live
form under a bracket; I-2 mismatch refusal; a REFUSED status, a partial replicate file, a hash change, a label sha mismatch,
an instrument mismatch, an existing outcome (write-once) all refuse; label building (category / src / side / gtc refusals).
MUTANTS: --mutants runs the table MUTANTS below against --selftest (each a source edit in a temporary copy). Run 2026-10-02 on
this blob's parent text: 26 of 26 KILLED, control M0 SURVIVED (harness valid): M1 >= -> > | M2 p = k/300 | M3 p = (k+1)/300 |
M4 C0 "reaches" strict | M5 C0 not a precondition | M7 null p95 -> max | M8 percentile rank floor | M9 I-1 gate skipped |
M10 I-2 first site only | M11 P2 non-strict | M12 BH q 0.10 | M13 PC3 read from the deflated arm | M14 hash check removed |
M15 write-once pre-check removed | M16 pooling >= -> > | M17 F-PC on NOT CERTIFIED | M18 P1 scored when NOT EVALUABLE |
M19 gtc check removed | M20 TRAIN check removed | M21 P3 interval | M22 partial replicates accepted | M23 instrument check
removed | M24 I-2 smallest -> largest TOP k | M25 k_d from the deflated arm | M26 C0 p95 from the null | M27 PC3 BH over the
unscored anchors too. Equivalent and dropped: "p_d <= 0.05" -> "<" (p = 1/20 is unreachable at 301); outcome open "x" -> "w"
(the pre-check refuses first; M15 removes the pre-check and is killed by mode "x").
[DELTA 2026-10-02, READY_cert_positive_control C-1; insertion only] selftest 21 / 21: the I-1 live gate refuses 59 live rows,
0 accepted and one accepted mismatch; a fixture with SN replicates in shuffled rep order; main --analyze checked by return code
(survives python -O). The reviewer's mutants added: R1 live rows == 60 dropped | R2 >= 1 accepted -> >= 0 | R9 live mismatch
ignored | R6 null quantiles on the unsorted list: all KILLED; --mutants 30 of 30 killed, control M0 SURVIVED.
"""
import argparse
import contextlib
import csv
import hashlib
import io
import json
import math
import os
import subprocess
import sys
import tempfile
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from data_v2 import ro as RO  # noqa: E402

TAG = "[CPC]"
_IN_SELFTEST = False
G12_BLOB = "0cf5b091fbfe97f74aa710233479a39c661899f5"
CR_BLOB = "dbe9425dc406edcd41661a6df4e00d33b44299b6"
GOLD_BLOB = "5ab1c87846e56cdd29da72f557e97ccb00645260"
G12_SITES_REL = "experiment_results/archv2/rp12_r2/g12/G12_sites.csv"
G12_SITES_BLOB = "21f110afae674f5f641e992c57f9f420abb8fdb5"
CONFIG_REL = "experiment_configs/rp12_r2/B0/g12_site_null.sitenull"
OUT_REL = "experiment_results/cert_positive_control"
LABELS_NAME, ARM_NAME = "declared_labels.tsv", "arm"
OUTCOME_NAME, SITES_NAME = "outcome.txt", "cpc_sites.csv"
LABEL_HEADER = "query_id\tcategory\tsrc"
REPS, N_CATS, MCS, N_G12_SITES = 300, 14, 55, 60
BAR = Fraction(1, 20)
Q = Fraction(1, 20)
C0_SEED = 20261002
INSTRUMENT = {"reps": "300", "sliceDim": "512", "sepBar": "0.0145", "dropTop": "0", "whiten": "false", "minClusterSize": "55",
              "c0Seed": str(C0_SEED)}
H_256, H_512 = 0.2912, 0.3130
G12_WALL_MIN, G12_SUM_N2 = 16.5, 6745608        # G12's site_null.log: 16 m 30 s at 12 threads, both arms, sum of n^2 over 60 sites
P1_POINT, P1_LO, P1_HI = 0.60, 0.05, 1.00
P1_PROBS = {"NOT CERTIFIED": 0.85, "CERTIFIED": 0.12, "NOT EVALUABLE": 0.03}
P2_P = 0.90
P3_POINT, P3_LO, P3_HI = 0, 0, 2
REG = ('docs/judge_v2_program.md "## Registered 2026-10-02 (before any code or call) — CERT-POSITIVE-CONTROL: ..." '
       'L23464-L23488 (as registered)')

SENT_NOT_CERT = ("the site-null certificate does not certify the declared 14-category level, which average-link recovers above "
                 "chance (H %.4f at 512; %.4f at 256, MMLU-GOLD-GEOMETRY); G12's 0 of 60 is therefore read as a sensitivity "
                 "limit of this certificate (an optimised-split null against the observed partition), not as evidence that "
                 "the MMLU-Pro member has no structure" % (H_512, H_256))
SENT_CERT = ("the certificate can certify the declared level at the member's root (n %d); G12's silence on the 14 depth-1 sites "
             "(n about 250-830) stands as 'no data-driven depth-1 split certified', and is not explained by an incapable "
             "instrument at root scale (n differs: no statement at depth-1 scale)")
DOES_NOT_SHOW = ("DOES NOT SHOW: that the declared categories are the right taxonomy or 'geometric clusters' (H is partial "
                 "recovery); a certificate of any tree site or of the tree; anything for another member, draw, slice, recipe or "
                 "embedder; power at depth-1 site sizes (PC1 is at root size; PC3 is descriptive); a mode test (MIX-LRT-SITE "
                 "closed; the dip half stays open); the deflated null as deciding")


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _import_pinned(name, blob):
    path = os.path.join(HERE, name + ".py")
    got = RO.git_blob_lf(path)
    if got != blob:
        refuse("%s.py is blob %s, not the pinned %s (imported, never copied)" % (name, got, blob))
    return __import__(name)


G = _import_pinned("g12_site_null", G12_BLOB)
CR = _import_pinned("cert_resolution", CR_BLOB)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def pctl(sorted_xs, q):
    """SeparationNullBySizeTest.percentile: rank ceil(q x n), clamped to [1, n]."""
    n = len(sorted_xs)
    r = min(max(int(math.ceil(q * n)), 1), n)
    return sorted_xs[r - 1]


def kcount(xs, obs):
    """The registered exceedance count: replicates >= the observed statistic."""
    return sum(1 for x in xs if x >= obs)


def p_of(k):
    return CR.p_site(k, REPS)


def main_checkout():
    try:
        common = subprocess.run(["git", "-C", ROOT, "rev-parse", "--git-common-dir"], capture_output=True, text=True,
                                timeout=30).stdout.strip()
        if common:
            return os.path.dirname(os.path.abspath(os.path.join(ROOT, common)))
    except Exception:                                       # noqa: BLE001
        pass
    return ROOT


def heavy_check():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq java.exe", "/NH", "/FO", "CSV"], capture_output=True, text=True,
                             timeout=30).stdout if os.name == "nt" else subprocess.run(["pgrep", "-l", "java"],
                                                                                     capture_output=True, text=True).stdout
        heavy = [ln for ln in out.splitlines() if ln.lower().startswith('"java.exe"') or (os.name != "nt" and ln.strip())]
    except Exception as ex:                                 # noqa: BLE001
        heavy = ["UNCHECKABLE (%s)" % ex]
    print("%s heavy foreign processes (java): %s" % (TAG, heavy if heavy else "none"))
    if heavy:
        refuse("a java process runs (%s): this mode reads embeddings_cache.db (rule 7: never beside a construction or site "
               "null); stop it (by PID) or wait" % heavy[:3])


# ------------------------------------------------------------------------------------------------ the population and labels
def region_ids(byid, nid):
    seen, stack, q = set(), [nid], set()
    while stack:
        c = stack.pop()
        if c in seen:
            continue
        seen.add(c)
        q.update(byid[c].get("queryIds") or [])
        stack.extend(x for x in (byid[c].get("childIds") or []) if x in byid)
    return q


def member(cfg, data_root):
    entry = G.pointer_entry(cfg, ROOT)
    graph, settings = G.snapshot_row(os.path.join(data_root, "snapshots.db"), entry["snapshot_id"])
    G.check_stamp(cfg, entry, settings)
    byid = {n["id"]: n for n in graph["nodes"]}
    root = byid.get(graph.get("rootId"))
    if root is None or root.get("depth") != 0:
        refuse("the snapshot's rootId %r is not a depth-0 node" % graph.get("rootId"))
    return entry["snapshot_id"], graph, byid, root


def build_labels(ids, qrows, crows, side_items, kept, stem):
    """-> (rows [(query_id, category, src)] sorted by id, counts). qrows: id -> (query_id, gtc); crows: question_id ->
    (source, domain, text); side_items: item -> (comp, side, corpora); kept: item -> {"src", "dom"} (gold's join)."""
    rows, cnt = [], {"no_src": 0, "src": 0}
    for qid in sorted(ids):
        q = qrows.get(qid)
        if q is None:
            refuse("query %s is not in embeddings_cache.db queries" % qid)
        up, gtc = q
        c = crows.get(up)
        if up is None or up == -1 or c is None:
            refuse("query %s: query_id %r has no corpus_questions row" % (qid, up))
        source, dom, text = c
        if source != "MMLU_PRO":
            refuse("query %s: corpus row %s is source %r, not MMLU_PRO" % (qid, up, source))
        if gtc != "MMLU_PRO_LB/" + dom:
            refuse("query %s: ground_truth_category %r != 'MMLU_PRO_LB/%s' (CR-1)" % (qid, gtc, dom))
        item = "i:" + stem(text)
        si = side_items.get(item)
        if si is None or si[1] != "TRAIN":
            refuse("query %s: item %s is on side %r, not TRAIN (no EVAL item anywhere)" % (qid, item, None if si is None else si[1]))
        k = kept.get(item)
        if k is not None and k["dom"] != dom:
            refuse("query %s: gold's domain %r != the corpus domain %r" % (qid, k["dom"], dom))
        src = k["src"] if k is not None else ""
        if "\t" in src or "\n" in src or "\t" in dom:
            refuse("a label carries a tab or newline")
        cnt["src" if src else "no_src"] += 1
        rows.append((qid, dom, src))
    cats = sorted({r[1] for r in rows})
    if len(cats) != N_CATS:
        refuse("%d declared categories, not the registered %d" % (len(cats), N_CATS))
    cnt["categories"] = {c: sum(1 for r in rows if r[1] == c) for c in cats}
    return rows, cnt


def labels_bytes(rows):
    return ("\n".join([LABEL_HEADER] + ["%s\t%s\t%s" % r for r in rows]) + "\n").encode("utf-8")


def src_groups(ids_sorted, srcof, mcs=MCS):
    """PC3's partition (the Kotlin cpcSrcGroups rule): sizes of [src >= mcs ...by name, pooled], pooled count."""
    by = {}
    pooled = 0
    for q in ids_sorted:
        s = srcof.get(q, "")
        if s:
            by[s] = by.get(s, 0) + 1
        else:
            pooled += 1
    kids = []
    for s in sorted(by):
        if by[s] >= mcs:
            kids.append(by[s])
        else:
            pooled += by[s]
    if pooled:
        kids.append(pooled)
    return kids, pooled


def read_labels_db(ids, data_root):
    import mmlu_gold_geometry as GOLD
    if RO.git_blob_lf(GOLD.__file__) != GOLD_BLOB:
        refuse("mmlu_gold_geometry.py is not the pinned blob %s" % GOLD_BLOB)
    from data_v2 import common as DC
    import v2_engine_pool as EP
    import glob
    emb = os.path.join(data_root, "embeddings_cache.db")
    mc = os.path.join(data_root, "multicorpus_cache_v1.db")
    raw = []
    for base in (data_root, ROOT, main_checkout()):
        raw = sorted(glob.glob(os.path.join(base, "experiment_results", "multicorpus", "raw", "*", "*",
                                            "samples_leaderboard_mmlu_pro_*.jsonl")))[:GOLD.RAW_N]
        if raw:
            break
    kept, _L, smeta = GOLD.assemble(mc, emb, GOLD.SIDE_FILE, raw)
    side_items, _m = EP.read_side(GOLD.SIDE_FILE)
    qrows = {}
    con = RO.open_ro(emb)
    try:
        idl = sorted(ids)
        for s in range(0, len(idl), 500):
            ch = idl[s:s + 500]
            for r in con.execute("SELECT id, query_id, ground_truth_category FROM queries WHERE id IN (%s)" % ",".join("?" * len(ch)), ch):
                qrows[r[0]] = (r[1], r[2])
    finally:
        con.close()
    crows = {}
    con = RO.open_ro(mc)
    try:
        ups = sorted({v[0] for v in qrows.values()})
        for s in range(0, len(ups), 500):
            ch = ups[s:s + 500]
            for r in con.execute("SELECT question_id, source, domain, text FROM corpus_questions WHERE question_id IN (%s)"
                                 % ",".join("?" * len(ch)), ch):
                crows[r[0]] = (r[1], r[2], r[3])
    finally:
        con.close()
    keys = DC.KeyCache()
    return build_labels(ids, qrows, crows, side_items, kept, keys.stem)


def i1_preview(graph, byid, data_root, dim):
    """Numpy replica of the routine on every site's persisted child regions (descriptive; the arm decides)."""
    import numpy as np
    sites = [n for n in graph["nodes"] if len(n.get("childIds") or []) >= 2 and (n.get("dasguptaDeltaNorm") or 0) > 0]
    allids = set()
    for s in sites:
        allids |= region_ids(byid, s["id"])
    con = RO.open_ro(os.path.join(data_root, "embeddings_cache.db"))
    vec = {}
    try:
        idl = sorted(allids)
        for s0 in range(0, len(idl), 500):
            ch = idl[s0:s0 + 500]
            for qid, b in con.execute("SELECT q.id, e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text "
                                      "WHERE q.id IN (%s)" % ",".join("?" * len(ch)), ch):
                v = np.frombuffer(b, dtype=">f4", count=dim).astype(np.float64)
                vec[qid] = v / math.sqrt(float(v @ v))
    finally:
        con.close()

    def sep(groups):
        st = [(len(g), np.sum([vec[q] for q in g], axis=0)) for g in groups if g]
        n = sum(c for c, _ in st)
        tot = np.sum([s for _, s in st], axis=0)
        ww = sum(c * c - float(s @ s) for c, s in st)
        pf = sum(c * (c - 1.0) for c, _ in st)
        return 1.0 - ww / ((n * n - float(tot @ tot)) * pf / (n * (n - 1.0)))

    ok = 0
    for s in sites:
        v = sep([sorted(region_ids(byid, c)) for c in s["childIds"] if c in byid])
        ok += int("%.6f" % v == "%.6f" % s["dasguptaDeltaNorm"])
    return ok, len(sites)


def wall_estimate(n_root, anchors):
    """n^2-scaled from G12's 16.5 min (sum n^2 = 6,745,608, both arms, 12 threads); anchors: plain always, deflated if scored."""
    rate = G12_WALL_MIN / G12_SUM_N2
    work = n_root ** 2 + sum(n * n * (0.5 + 0.5 * int(sc)) for n, sc in anchors)
    return rate * work


def command(cfg, sid, heap):
    return ('.\\gradlew.bat certPositiveControl --console=plain --offline --no-daemon -PjvmThreads=%d -PnullReps=%d '
            '"-DsnapshotId=%s" "-DsliceDim=%d" "-DsepBar=%s" "-DdropTop=%d" "-Dwhiten=%s" "-DdeclaredLabels=%s/%s" '
            '"-Dg12Sites=%s" "-DoutDir=%s/%s"%s'
            % (cfg["jvmThreads"], cfg["nullReps"], sid, cfg["sliceDim"], repr(cfg["sepBar"]), cfg["dropTop"],
               str(cfg["whiten"]).lower(), OUT_REL, LABELS_NAME, G12_SITES_REL, OUT_REL, ARM_NAME,
               "" if heap <= G.DEFAULT_HEAP_GB else ' "-DsiteNullHeap=%dg"' % heap))


def assemble(data_root):
    cfg = G.load_config(os.path.join(ROOT, CONFIG_REL))
    G.lane_check("r2", os.path.join(ROOT, CONFIG_REL), cfg)
    sid, graph, byid, root = member(cfg, data_root)
    ids = region_ids(byid, root["id"])
    rows, cnt = read_labels_db(ids, data_root)
    return cfg, sid, graph, byid, root, ids, rows, cnt


def dry_run(data_root, out=print):
    out("pool: the B0-2 check is the operator's (v2_union_pool.py --dry-run); this mode opens no pool table")
    out("%s DRY RUN: zero calls, nothing written, no null replicate, no verdict" % TAG)
    heavy_check()
    cfg, sid, graph, byid, root, ids, rows, cnt = assemble(data_root)
    out("%s member B0/mmlu_pro_lb = snapshot %s (stamp = the pointer's; pool %s, namespace %s); root %s '%s' n = %d (TRAIN)"
        % (TAG, sid, cfg["poolId"], cfg["namespace"], root["id"], root.get("label"), len(ids)))
    out("%s PC1 groups (the 14 declared categories, CR-1): %s" % (TAG, ", ".join("%s %d" % kv for kv in cnt["categories"].items())))
    srcof = {r[0]: r[2] for r in rows}
    out("%s src (CR-2): %d items carry a src, %d none (pooled in PC3)" % (TAG, cnt["src"], cnt["no_src"]))
    data = labels_bytes(rows)
    lp = os.path.join(ROOT, OUT_REL, LABELS_NAME)
    out("%s label file %s/%s: %d rows, sha256 %s (%s)" % (TAG, OUT_REL, LABELS_NAME, len(rows), sha256_bytes(data),
        "present, IDENTICAL" if os.path.exists(lp) and open(lp, "rb").read() == data else
        ("present, DIFFERENT: --prepare's file is not this population" if os.path.exists(lp) else "absent: --prepare writes it")))
    sites = [n for n in graph["nodes"] if len(n.get("childIds") or []) >= 2 and (n.get("dasguptaDeltaNorm") or 0) > 0]
    anchors = [byid[c] for c in root["childIds"] if c in byid]
    g12 = read_g12(os.path.join(ROOT, G12_SITES_REL))
    prev = []
    for a in anchors:
        aids = sorted(region_ids(byid, a["id"]))
        kids, pooled = src_groups(aids, srcof)
        prev.append((len(aids), len(kids) >= 2))
        out("%s PC3 preview %-36s n %4d: src children %s (pooled %d) %s; G12 k %s" % (
            TAG, a.get("label"), len(aids), kids, pooled, "scored" if len(kids) >= 2 else "NOT SCORED", g12.get(a["id"], {}).get("k")))
    out("%s PC3: %d of %d anchors scored" % (TAG, sum(1 for _n, s in prev if s), len(anchors)))
    ok, m = i1_preview(graph, byid, data_root, cfg["sliceDim"])
    out("%s I-1 preview (numpy replica of the routine; the arm decides): %d of %d sites reproduce the persisted "
        "dasguptaDeltaNorm at 6 digits -> the registered form %s (D-I1)" % (TAG, ok, m, "PASSES" if ok == m else "REFUSES"))
    named = i2_named(g12, {a["id"]: a.get("label") or "" for a in anchors})
    out("%s I-2 targets (re-run, k must equal G12's): %s" % (TAG, "; ".join("%s %s k %d" % (n, g12[n]["label"], g12[n]["k"]) for n in named)))
    need, live, heap = G.heap_estimate(len(ids), cfg["sliceDim"], cfg["nullReps"], cfg["jvmThreads"])
    out("%s heap (g12_site_null's rule): n %d, live %d, peak %.2f GB -> %s" % (
        TAG, len(ids), live, need, "fits the 6g default" if heap <= G.DEFAULT_HEAP_GB else "-DsiteNullHeap=%dg" % heap))
    out("%s wall estimate: about %.0f min at %d threads (n^2-scaled from G12's %.1f min; unsourced beyond that scaling)"
        % (TAG, wall_estimate(len(ids), prev), cfg["jvmThreads"], G12_WALL_MIN))
    if os.path.exists(os.path.join(ROOT, OUT_REL, ARM_NAME)):
        refuse("%s/%s exists: the arm writes it once" % (OUT_REL, ARM_NAME))
    out("%s sites %d (I-1 runs on all of them); the arm refuses under the registered I-1 unless D-I1 is bracketed (then add "
        "\"-Di1Form=live\" \"-Di1Bracket=<programme line>\")" % (TAG, len(sites)))
    pf = os.path.join(ROOT, "experiment_configs", "engine_pool_%s.json" % cfg["poolId"])
    pf_sha = sha256_bytes(open(pf, "rb").read().replace(b"\r\n", b"\n"))
    out("%s pool file %s sha256-lf %s (%s; the B0-2 check: v2_union_pool.py --dry-run rc 0 is the operator's)" % (
        TAG, os.path.relpath(pf, ROOT).replace("\\", "/"), pf_sha[:16], "= the stamp's" if pf_sha == cfg["enginePoolSha256Lf"] else "MISMATCH"))
    if pf_sha != cfg["enginePoolSha256Lf"]:
        refuse("the engine pool file's LF sha256 is not the stamp's")
    same = same_checkout(data_root)
    out("%s LAUNCH FROM %s: the COMMAND reads snapshots.db and embeddings_cache.db from the checkout it runs in, and the label "
        "file and outDir relative to it; --prepare / --hashes / --analyze run from the same checkout%s" % (
            TAG, os.path.abspath(data_root), "" if same else " (the data root is NOT this checkout: this dry-run is a preview; merge "
            "the branch there and run from there)"))
    out("%s COMMAND: %s" % (TAG, command(cfg, sid, heap)))
    return dict(sid=sid, n=len(ids), heap=heap, i1=(ok, m))


def same_checkout(data_root):
    return os.path.normcase(os.path.abspath(data_root)) == os.path.normcase(os.path.abspath(ROOT))


def prepare(data_root):
    if not same_checkout(data_root):
        refuse("--prepare writes the label file into this checkout; the arm reads it from the data root's: run from %s" % data_root)
    heavy_check()
    _cfg, _sid, _g, _b, _r, _ids, rows, _cnt = assemble(data_root)
    d = os.path.join(ROOT, OUT_REL)
    os.makedirs(d, exist_ok=True)
    data = labels_bytes(rows)
    with open(os.path.join(d, LABELS_NAME), "xb") as f:
        f.write(data)
    print("%s wrote %s/%s (%d rows, sha256 %s)" % (TAG, OUT_REL, LABELS_NAME, len(rows), sha256_bytes(data)))


def hashes(label, data_root):
    if not same_checkout(data_root):
        refuse("--hashes records the cache the arm reads: run it from the data root's checkout %s" % data_root)
    heavy_check()
    con = RO.open_ro(os.path.join(data_root, "embeddings_cache.db"))
    try:
        h = {t: v["table_sha"] + "/%d" % v["rows"] for t, v in RO.table_shas(con).items()}
    finally:
        con.close()
    d = os.path.join(ROOT, OUT_REL)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "emb_hashes_%s.json" % label), "x", encoding="utf-8") as f:
        json.dump(h, f, sort_keys=True, indent=1)
    print("%s embeddings_cache.db per-table hashes (%s): %s" % (TAG, label, json.dumps({k: v[:16] for k, v in h.items()}, sort_keys=True)))


# ------------------------------------------------------------------------------------------------ the readout
def read_g12(path):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["node_id"]] = {"k": int(r["k"]), "family": r["family_key"], "label": r["label"], "depth": int(r["depth"])}
    return out


def i2_named(g12, anchor_labels):
    chem = [a for a, lab in anchor_labels.items() if lab.endswith("/chemistry")]
    math_ = [a for a, lab in anchor_labels.items() if lab.endswith("/math")]
    top = sorted((v["k"], n) for n, v in g12.items() if v["family"] == "TOP")
    if len(chem) != 1 or len(math_) != 1 or not top:
        refuse("I-2: cannot name chemistry, math and the smallest-k TOP site")
    return [chem[0], math_[0], top[0][1]]


def _f(s):
    return float(s)


def analyze(arm_dir, out_dir, g12_path, labels_path, g12_blob=G12_SITES_BLOB, out=print):
    outcome_p, sites_p = os.path.join(out_dir, OUTCOME_NAME), os.path.join(out_dir, SITES_NAME)
    for p in (outcome_p, sites_p):
        if os.path.exists(p):
            refuse("%s exists: the outcome is write-once" % p)
    L = []

    def say(s):
        L.append(s)
        out(s)

    say("pool: none (no DB opened)")
    st_p = os.path.join(arm_dir, "status.txt")
    if not os.path.isfile(st_p):
        refuse("the arm wrote no status.txt (not run or killed): no readout")
    st_lines = open(st_p, encoding="utf-8").read().splitlines()
    if not st_lines or st_lines[0] != "COMPLETE":
        refuse("the arm's status is %r: no readout (a refused or partial arm)" % (st_lines[0] if st_lines else ""))
    st = dict(ln.split("=", 1) for ln in st_lines[1:] if "=" in ln)
    for k, v in INSTRUMENT.items():
        if st.get(k) != v:
            refuse("instrument: the arm ran %s=%r, the registered value is %r" % (k, st.get(k), v))
    lab_sha = sha256_bytes(open(labels_path, "rb").read())
    if st.get("labels_sha256") != lab_sha:
        refuse("the arm read labels sha256 %s; %s is %s" % (st.get("labels_sha256"), labels_path, lab_sha))
    if RO.git_blob_lf(g12_path) != g12_blob:
        refuse("%s is not blob %s (G12_sites.csv of record)" % (g12_path, g12_blob))
    hb, ha = (os.path.join(out_dir, "emb_hashes_%s.json" % x) for x in ("before", "after"))
    if not (os.path.isfile(hb) and os.path.isfile(ha)):
        refuse("the embeddings_cache.db hashes before and after the arm are owed (--hashes before / after)")
    if json.load(open(hb)) != json.load(open(ha)):
        refuse("embeddings_cache.db changed during the arm (per-table hashes differ)")
    say("%s CERT-POSITIVE-CONTROL outcome (tools/analysis/cert_positive_control.py blob %s; cert_resolution.py blob %s imported). "
        "Zero calls." % (TAG, RO.git_blob_lf(os.path.abspath(__file__)), CR_BLOB))
    say("registration: " + REG)
    say("arm: snapshot %s; labels sha256 %s; reps %s; sliceDim %s; sepBar %s; dropTop %s; whiten %s; minClusterSize %s; "
        "C0 seed %s; threads %s; embeddings_cache.db per-table hashes before == after" % (
            st.get("snapshot"), lab_sha, st["reps"], st["sliceDim"], st["sepBar"], st["dropTop"], st["whiten"],
            st["minClusterSize"], st["c0Seed"], st.get("threads")))
    say("builder's readings CR-1..CR-6 (docstring); defect D-I1 reported to the registrar")
    g12 = read_g12(g12_path)

    # identity
    with open(os.path.join(arm_dir, "identity.csv"), newline="", encoding="utf-8") as f:
        idr = list(csv.DictReader(f))
    reg = [r for r in idr if r["leg"] == "I1_REGISTERED"]
    liv = [r for r in idr if r["leg"] == "I1_LIVE"]
    i2 = {r["site_id"]: r for r in idr if r["leg"] == "I2"}
    reg_ok = sum(1 for r in reg if r["match"] == "true")
    liv_acc = [r for r in liv if r["match"] != "not-accepted"]
    liv_ok = sum(1 for r in liv_acc if r["match"] == "true")
    form, bracket = st.get("i1Form", "registered"), st.get("i1Bracket", "")
    say("I-1 registered form: %d of %d sites reproduce the persisted dasguptaDeltaNorm at 6 printed digits (G12's sites %d)"
        % (reg_ok, len(reg), N_G12_SITES))
    say("I-1 live leg: %d of %d accepted real site populations reproduce the splitter's dasguptaDeltaNorm bit for bit (%d not accepted)"
        % (liv_ok, len(liv_acc), len(liv) - len(liv_acc)))
    if form == "registered":
        if not (len(reg) == N_G12_SITES and reg_ok == len(reg)):
            refuse("I-1 FAILED (registered form): %d of %d reproduce; no readout (D-I1)" % (reg_ok, len(reg)))
        say("I-1: PASS (registered form)")
    elif form == "live" and bracket.strip():
        if not (len(liv) == N_G12_SITES and len(liv_acc) >= 1 and liv_ok == len(liv_acc)):
            refuse("I-1 FAILED (live leg): %d of %d accepted reproduce; no readout" % (liv_ok, len(liv_acc)))
        say("I-1: PASS (live leg, under the registrar's bracket: %s)" % bracket)
    else:
        refuse("I-1 form %r with bracket %r is not admissible" % (form, bracket))

    with open(os.path.join(arm_dir, "sites.csv"), newline="", encoding="utf-8") as f:
        srows = list(csv.DictReader(f))
    roots = [r for r in srows if r["role"] == "ROOT"]
    anch = [r for r in srows if r["role"] == "ANCHOR"]
    if len(roots) != 1 or len(anch) != N_CATS:
        refuse("sites.csv holds %d ROOT and %d ANCHOR rows (want 1 and %d)" % (len(roots), len(anch), N_CATS))
    named = i2_named(g12, {r["site_id"]: r["label"] for r in anch})
    bad = []
    for n in named:
        r = i2.get(n)
        if r is None or int(r["recomputed"]) != g12[n]["k"]:
            bad.append(n)
    say("I-2: %s" % "; ".join("%s %s re-run k %s, G12 k %d" % (n, g12[n]["label"], i2[n]["recomputed"] if n in i2 else "-", g12[n]["k"])
                             for n in named))
    if bad:
        refuse("I-2 FAILED: %s do not reproduce G12_sites.csv's k; no readout" % bad)
    beside = [n for n in i2 if n not in named]
    say("I-2: PASS (the three registered sites reproduce exactly); beside: %d of %d other anchors reproduce"
        % (sum(1 for n in beside if int(i2[n]["recomputed"]) == g12.get(n, {}).get("k")), len(beside)))

    reps = {}
    with open(os.path.join(arm_dir, "replicates.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            reps.setdefault((r["site_id"], r["arm"]), []).append((int(r["rep"]), _f(r["stat"])))
    for key, xs in reps.items():
        if [i for i, _x in xs] != list(range(REPS)):
            refuse("replicates %s: reps %d, not 0..%d in order (a partial file)" % (key, len(xs), REPS - 1))
    R = {k: [x for _i, x in v] for k, v in reps.items()}
    rt = roots[0]
    rid = rt["site_id"]
    for arm in ("SN", "SND", "C0"):
        if (rid, arm) not in R:
            refuse("replicates: the root's %s arm is missing" % arm)
    d = _f(rt["declared_stat"])
    sn = sorted(R[(rid, "SN")])
    k_d = kcount(R[(rid, "SN")], d)
    if k_d != int(rt["k_declared"]):
        refuse("k_d recount %d != the arm's %s" % (k_d, rt["k_declared"]))
    p_d = p_of(k_d)
    c0 = sorted(R[(rid, "C0")])
    c0_p95, n_p95, n_p05 = pctl(c0, 0.95), pctl(sn, 0.95), pctl(sn, 0.05)
    if abs(c0_p95 - _f(rt["c0_p95"])) > 0.0:
        refuse("C0 p95 recount %r != the arm's %s" % (c0_p95, rt["c0_p95"]))
    comparable = not bool(c0_p95 >= n_p95)
    n_root = int(rt["n"])
    say("SUPPORT (a) deciding denominator: %d null replicates for one site, the member root (%d TRAIN items in %s declared "
        "groups); (b) DEFF 1.0 by construction (independent generator draws; item resampling is not part of the certificate); "
        "(c) n_eff = %d / 1.0 = %d; (d) SE at the bar sqrt(0.05 x 0.95 / %d) = %.4f; (e) MDE80 = 2.80 x SE = %.4f; "
        "(f) PC1 SCOREABLE (predicted p_d %.2f lies %.2f from the bar > MDE80); PC3 DESCRIPTIVE-ONLY; (g) one site: CERTIFIED "
        "needs k_d <= 14, floor 1/301 = %.4f; PC3 family reachable (1/301 <= 0.05/14 = %.5f)"
        % (REPS, n_root, rt["groups"], REPS, REPS, REPS, math.sqrt(0.0475 / REPS), 2.80 * math.sqrt(0.0475 / REPS), P1_POINT,
           P1_POINT - 0.05, 1 / 301.0, 0.05 / 14))
    say("SUPPORT: no matches and no questions: wrong(established), the tie conventions A / B and a question-clustered "
        "bootstrap are N/A to a null exceedance count")
    say("C0 (comparability precondition): %d size-matched relabellings of the %s groups, p95 %.6f vs the site null's p95 %.6f "
        "-> %s" % (len(c0), rt["groups"], c0_p95, n_p95, "comparable (C0 p95 below the null p95)" if comparable else
                   "FAILS (C0 p95 reaches the null p95): PC1 NOT EVALUABLE"))
    say("PC1 declared statistic (14 categories, root n %d) = %.6f; null p05 %.6f / p50 %.6f / p95 %.6f / max %.6f; "
        "k_d = %d of %d replicates >= it; p_d = (k_d + 1) / 301 = %d/301 = %.6f"
        % (n_root, d, n_p05, pctl(sn, 0.50), n_p95, sn[-1], k_d, REPS, k_d + 1, float(p_d)))
    if not comparable:
        verdict = "NOT EVALUABLE"
    elif bool(p_d <= BAR):
        verdict = "CERTIFIED"
    else:
        verdict = "NOT CERTIFIED"
    if comparable and (verdict == "CERTIFIED") != bool(k_d <= 14):
        refuse("internal: p_d <= 0.05 and k_d <= 14 disagree")
    say("PC1: %s" % verdict)
    if verdict == "NOT CERTIFIED":
        say("READING: " + SENT_NOT_CERT)
    elif verdict == "CERTIFIED":
        say("READING: " + SENT_CERT % n_root)
    else:
        say("READING: none (NOT EVALUABLE: no sentence; PC3 recorded descriptively)")
    fired = verdict == "CERTIFIED"
    if fired:
        say("F-PC: FIRED (PC1 CERTIFIED): the working reading that G12's 0 of 60 is a sensitivity limit of the certificate is "
            "overturned; N-1's empty set is evidence about the data-driven depth-1 splits (at the member's site sizes, the n "
            "caveat). F-TAX N-1 FIRES and F2 stand.")
    else:
        say("F-PC: NOT FIRED (PC1 %s); a NOT CERTIFIED outcome does not reinstate F-TAX's certificate clause; F-TAX N-1 FIRES "
            "stands" % verdict)

    # descriptive: deflated root
    sd = R[(rid, "SND")]
    kdd = kcount(sd, d)
    say("DESCRIPTIVE deflated null (declared-centroid subspace, %s dims): k = %d, p = %d/301 = %.6f; deflated p95 %.6f"
        % (rt["defl_dims"], kdd, kdd + 1, float(p_of(kdd)), pctl(sorted(sd), 0.95)))

    # PC3
    scored = [r for r in anch if r["scored"] == "true"]
    ps, rowsout = [], []
    for r in scored:
        xs = R.get((r["site_id"], "SN"))
        if xs is None:
            refuse("replicates: anchor %s's SN arm is missing" % r["site_id"])
        k = kcount(xs, _f(r["declared_stat"]))
        if k != int(r["k_declared"]):
            refuse("PC3 recount %d != the arm's %s for %s" % (k, r["k_declared"], r["site_id"]))
        ps.append(p_of(k))
    rej, thr = CR.bh_cutoff(ps, Q)
    say("PC3 (DESCRIPTIVE-ONLY; src geometry unknown: a non-certification is never a power statement): %d of %d anchors scored, "
        "%d not scored (< 2 children); BH over the scored TOP family (m = %d, q = 0.05): %d certified%s"
        % (len(scored), len(anch), len(anch) - len(scored), len(scored), len(rej),
           "" if thr is None else " (step-up cutoff %s = %.6f)" % (thr, float(thr))))
    for i, r in enumerate(scored):
        xs = R[(r["site_id"], "SN")]
        dx = R.get((r["site_id"], "SND"))
        kd = kcount(dx, _f(r["declared_stat"])) if dx else None
        say("  PC3 %-34s n %4s groups %2s (pooled %4s): src stat %.6f k %3d p %.6f %s | deflated k %s | G12 tree split %.6f k %d" % (
            r["label"], r["n"], r["groups"], r["pooled"], _f(r["declared_stat"]), int(r["k_declared"]), float(ps[i]),
            "BH-IN" if i in rej else "bh-out", "-" if kd is None else kd, _f(r["persisted_stat"]), g12[r["site_id"]]["k"]))
        rowsout.append(r)
    for r in anch:
        if r["scored"] != "true":
            say("  PC3 %-34s n %4s: NOT SCORED (%s child(ren) after pooling)" % (r["label"], r["n"], r["groups"]))
    say("BESIDE: G12's TOP-site (tree) statistics against their own nulls: %s" % "; ".join(
        "%s %.6f k %d" % (r["label"], _f(r["persisted_stat"]), g12[r["site_id"]]["k"]) for r in anch))

    # predictions
    if verdict != "NOT EVALUABLE":
        held = bool(P1_LO <= float(p_d) <= P1_HI)
        say("P1 p_d %.2f [%.2f, %.2f] (80%%): %s (p_d %.6f)" % (P1_POINT, P1_LO, P1_HI, "HELD" if held else "FAILED", float(p_d)))
    else:
        say("P1 p_d interval: NOT SCORED (PC1 NOT EVALUABLE; CR-4); p_d %.6f printed" % float(p_d))
    brier3 = sum((p - (1.0 if v == verdict else 0.0)) ** 2 for v, p in P1_PROBS.items())
    say("P1 PC1 readings (NOT CERTIFIED 0.85, CERTIFIED 0.12, NOT EVALUABLE 0.03): outcome %s, Brier (3-way sum) %.4f" % (verdict, brier3))
    ev2 = bool(c0_p95 < n_p05)
    say("P2 C0 p95 below the null p05 (p 0.90): event %s (C0 p95 %.6f, null p05 %.6f), Brier %.4f"
        % ("yes" if ev2 else "no", c0_p95, n_p05, (P2_P - (1.0 if ev2 else 0.0)) ** 2))
    n3 = len(rej)
    say("P3 PC3 certified anchors %d [%d, %d] of the scored: %s (%d of %d)" % (
        P3_POINT, P3_LO, P3_HI, "HELD" if bool(P3_LO <= n3 <= P3_HI) else "FAILED", n3, len(scored)))
    say(DOES_NOT_SHOW)

    os.makedirs(out_dir, exist_ok=True)
    with open(outcome_p, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(sites_p, "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["role", "site_id", "label", "n", "groups", "pooled", "scored", "declared_stat", "k_declared", "p", "bh_in",
                    "defl_k", "persisted_stat", "g12_k"])
        w.writerow(["ROOT", rid, rt["label"], rt["n"], rt["groups"], 0, "true", rt["declared_stat"], k_d, "%d/301" % (k_d + 1),
                    "", kdd, rt["persisted_stat"], ""])
        sidx = {r["site_id"]: i for i, r in enumerate(scored)}
        for r in anch:
            i = sidx.get(r["site_id"])
            dx = R.get((r["site_id"], "SND"))
            w.writerow(["ANCHOR", r["site_id"], r["label"], r["n"], r["groups"], r["pooled"], r["scored"], r["declared_stat"],
                        r["k_declared"], "" if i is None else "%d/301" % (int(r["k_declared"]) + 1),
                        "" if i is None else str(i in rej).lower(), "" if (not dx or i is None) else kcount(dx, _f(r["declared_stat"])),
                        r["persisted_stat"], g12[r["site_id"]]["k"]])
    out("%s wrote %s and %s (write-once)" % (TAG, outcome_p, sites_p))
    return dict(verdict=verdict, k_d=k_d, p_d=p_d, comparable=comparable, c0_p95=c0_p95, null_p95=n_p95, null_p05=n_p05,
                pc3=len(rej), scored=len(scored), fired=fired, lines=L)


# ------------------------------------------------------------------------------------------------ selftest
def _fx(tmp, k_root=15, c0_mode="small", i1_reg_ok=60, form="registered", bracket="", i2_bad=False, pc3_k=None,
        status="COMPLETE", hashes_equal=True, partial=False, lab_mismatch=False, sepbar="0.0145", tie=False,
        live="half", shuffle_sn=False):
    """A complete arm directory whose answer is known: root SN = i/1000 (i = 0..299), declared = (300 - k_root)/1000 so exactly
    k_root replicates are >= it (a tie when tie=True: declared equals a replicate); p95 = 0.284, p05 = 0.014."""
    arm, outd = os.path.join(tmp, "arm"), os.path.join(tmp, "out")
    os.makedirs(arm); os.makedirs(outd)
    lab = os.path.join(tmp, "labels.tsv")
    open(lab, "wb").write(b"query_id\tcategory\tsrc\nq1\tmath\tx\n")
    sha = sha256_bytes(b"query_id\tcategory\tsrc\nq1\tmath\tx\n" if not lab_mismatch else b"other")
    labels = ["M/law", "M/chemistry", "M/math"] + ["M/c%02d" % i for i in range(11)]
    aids = ["a%02d" % i for i in range(14)]
    g12k = [97, 300, 292] + [150 + i for i in range(11)]
    g = os.path.join(tmp, "g12.csv")
    with open(g, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["node_id", "label", "depth", "n", "k", "p_site", "family_key", "reached", "hier_bh", "cert_site_p95"])
        for a, lab_, k in zip(aids, labels, g12k):
            w.writerow([a, lab_, 1, 500, k, "x", "TOP", "true", "false", "false"])
        for i in range(46):
            w.writerow(["d%02d" % i, "deep", 2, 200, 200, "x", aids[i % 14], "true", "false", "false"])
    with open(os.path.join(arm, "status.txt"), "w") as f:
        f.write("%s\nsnapshot=SNAP\nlabels_sha256=%s\nreps=300\nsliceDim=512\nsepBar=%s\ndropTop=0\nwhiten=false\n"
                "minClusterSize=55\nc0Seed=20261002\ni1Form=%s\ni1Bracket=%s\nthreads=12\n" % (status, sha, sepbar, form, bracket))
    with open(os.path.join(arm, "identity.csv"), "w") as f:
        f.write("leg,site_id,label,depth,n,k_children,persisted,recomputed,match\n")
        for i in range(60):
            f.write("I1_REGISTERED,s%d,l,1,100,2,0.1,0.1,%s\n" % (i, "true" if i < i1_reg_ok else "false"))
        for i in range(59 if live == "rows59" else 60):
            m_ = {"half": "true" if i % 2 == 0 else "not-accepted", "rows59": "true" if i % 2 == 0 else "not-accepted",
                  "none": "not-accepted", "one_false": ("false" if i == 4 else "true") if i % 2 == 0 else "not-accepted"}[live]
            f.write("I1_LIVE,s%d,l,1,100,2,0.1,0.1,%s\n" % (i, m_))
        for j, (a, k) in enumerate(zip(aids, g12k)):
            kk = k + 1 if (i2_bad and j == 0) else k     # a00 = the smallest-k TOP site, the THIRD named
            f.write("I2,%s,%s,1,500,2,%d,%d,%s\n" % (a, labels[j], k, kk, str(kk == k).lower()))
    pc3_k = pc3_k if pc3_k is not None else [0, 0, 1, 3, 20, 40, 60, 80, 100, 120, 150, 200, None, None]
    sn_root = [i / 1000.0 for i in range(300)]
    d = (300 - k_root) / 1000.0
    c0 = {"small": [i * 0.0001 for i in range(300)], "tiny": [i * 0.00001 for i in range(300)], "equal": list(sn_root),
          "below": [x - 1e-9 for x in sn_root], "at_p05": [0.0] * 284 + [0.014] * 16}[c0_mode]
    with open(os.path.join(arm, "replicates.csv"), "w") as f:
        f.write("site_id,arm,rep,stat\n")
        sn_w = list(sn_root)
        if shuffle_sn:                       # replicate (rep) order is not value order in a real arm
            import random
            random.Random(3).shuffle(sn_w)
        for arm_, xs in (("SN", sn_w), ("SND", [x / 2 for x in sn_root]), ("C0", c0)):
            for i, x in enumerate(xs[:150] if (partial and arm_ == "SN") else xs):
                f.write("ROOT0,%s,%d,%r\n" % (arm_, i, x))
        for j, a in enumerate(aids):
            for i, x in enumerate(sn_root):
                f.write("%s,SN,%d,%r\n" % (a, i, x))
            for i, x in enumerate(sn_root if pc3_k[j] is not None else []):     # the arm dumps SND for scored anchors only
                f.write("%s,SND,%d,%r\n" % (a, i, x / 2))
    with open(os.path.join(arm, "sites.csv"), "w") as f:
        f.write("role,site_id,label,depth,n,groups,pooled,scored,declared_stat,persisted_stat,k_declared,k_persisted,g12_k,"
                "defl_dims,defl_k_declared,c0_p95,reps\n")
        f.write('ROOT,"ROOT0","M",0,6993,14,0,true,%r,0.0,%d,,,13,0,%r,300\n' % (d, k_root, pctl(sorted(c0), 0.95)))
        for j, a in enumerate(aids):
            k = pc3_k[j]
            if k is None:
                f.write('ANCHOR,"%s","%s",1,500,1,500,false,,0.04,,%d,%d,,,,300\n' % (a, labels[j], g12k[j], g12k[j]))
            else:
                f.write('ANCHOR,"%s","%s",1,500,3,70,true,%r,0.04,%d,%d,%d,2,,,300\n' % (a, labels[j], (300 - k) / 1000.0, k, g12k[j], g12k[j]))
    for x in ("before", "after"):
        json.dump({"embeddings": "aa/1", "queries": "bb/2" if (hashes_equal or x == "before") else "cc/2"},
                  open(os.path.join(outd, "emb_hashes_%s.json" % x), "w"))
    blob = RO.git_blob_lf(g)
    return arm, outd, g, lab, blob


def selftest():
    global _IN_SELFTEST
    _IN_SELFTEST = True
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="cpcst_")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:            # noqa: BLE001
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))

    def run(tmp, **kw):
        arm, outd, g, lab, blob = _fx(tmp, **kw)
        lines = []
        r = analyze(arm, outd, g, lab, g12_blob=blob, out=lines.append)
        return r, lines, outd

    def refused(tmp, needle, **kw):
        arm, outd, g, lab, blob = _fx(tmp, **kw)
        try:
            analyze(arm, outd, g, lab, g12_blob=blob, out=lambda s: None)
        except SystemExit as e:
            assert needle in str(e), (needle, str(e))
            assert not os.path.exists(os.path.join(outd, OUTCOME_NAME)), "a refusal wrote an outcome"
            return
        raise AssertionError("not refused: " + needle)

    def has(lines, s):
        assert s in lines, "missing line %r; got:\n%s" % (s, "\n".join(lines))

    def not_cert(tmp):
        r, L, outd = run(tmp, k_root=15)
        assert (r["verdict"], r["k_d"], r["p_d"]) == ("NOT CERTIFIED", 15, Fraction(16, 301)), r
        has(L, "PC1: NOT CERTIFIED")
        has(L, "PC1 declared statistic (14 categories, root n 6993) = 0.285000; null p05 0.014000 / p50 0.149000 / p95 0.284000 / "
               "max 0.299000; k_d = 15 of 300 replicates >= it; p_d = (k_d + 1) / 301 = 16/301 = 0.053156")
        has(L, "READING: " + SENT_NOT_CERT)
        has(L, "F-PC: NOT FIRED (PC1 NOT CERTIFIED); a NOT CERTIFIED outcome does not reinstate F-TAX's certificate clause; "
               "F-TAX N-1 FIRES stands")
        has(L, "P1 p_d 0.60 [0.05, 1.00] (80%): HELD (p_d 0.053156)")
        has(L, "P1 PC1 readings (NOT CERTIFIED 0.85, CERTIFIED 0.12, NOT EVALUABLE 0.03): outcome NOT CERTIFIED, Brier (3-way sum) 0.0378")
        has(L, "C0 (comparability precondition): 300 size-matched relabellings of the 14 groups, p95 0.028400 vs the site null's "
               "p95 0.284000 -> comparable (C0 p95 below the null p95)")
        has(L, "P2 C0 p95 below the null p05 (p 0.90): event no (C0 p95 0.028400, null p05 0.014000), Brier 0.8100")
        has(L, "DESCRIPTIVE deflated null (declared-centroid subspace, 13 dims): k = 0, p = 1/301 = 0.003322; deflated p95 0.142000")
        txt = open(os.path.join(outd, OUTCOME_NAME), encoding="utf-8").read()
        assert "PC1: NOT CERTIFIED\n" in txt and txt.startswith("pool: none (no DB opened)\n"), txt[:200]
        rows = list(csv.DictReader(open(os.path.join(outd, SITES_NAME), encoding="utf-8")))
        assert rows[0]["p"] == "16/301" and rows[1]["bh_in"] == "true" and rows[13]["scored"] == "false", rows[:2]
        try:
            arm = os.path.join(tmp, "arm")
            analyze(arm, outd, os.path.join(tmp, "g12.csv"), os.path.join(tmp, "labels.tsv"),
                    g12_blob=RO.git_blob_lf(os.path.join(tmp, "g12.csv")), out=lambda s: None)
            raise AssertionError("second analyze not refused")
        except SystemExit as e:
            assert "write-once" in str(e), e

    def cert_boundary(tmp):
        r, L, _o = run(tmp, k_root=14, c0_mode="tiny")
        assert (r["verdict"], r["k_d"]) == ("CERTIFIED", 14), r
        has(L, "PC1: CERTIFIED")
        has(L, "READING: " + SENT_CERT % 6993)
        assert any(l.startswith("F-PC: FIRED (PC1 CERTIFIED)") for l in L), L
        has(L, "P1 p_d 0.60 [0.05, 1.00] (80%): FAILED (p_d 0.049834)")
        has(L, "P1 PC1 readings (NOT CERTIFIED 0.85, CERTIFIED 0.12, NOT EVALUABLE 0.03): outcome CERTIFIED, Brier (3-way sum) 1.4978")
        has(L, "P2 C0 p95 below the null p05 (p 0.90): event yes (C0 p95 0.002840, null p05 0.014000), Brier 0.0100")

    def tie_counts(tmp):
        # declared = 0.286 exactly equals replicate 286/1000: k counts it (>=): 14 -> CERTIFIED; '>' would give 13
        r, _L, _o = run(tmp, k_root=14)
        assert r["k_d"] == 14 and kcount([0.286, 0.286, 0.1], 0.286) == 2, r

    def not_evaluable(tmp):
        # C0 identical to the null: C0 p95 == null p95 ("reaches", CR-3) -> NOT EVALUABLE even at k_d = 0
        r, L, _o = run(tmp, k_root=0, c0_mode="equal")
        assert (r["verdict"], r["comparable"]) == ("NOT EVALUABLE", False), r
        has(L, "PC1: NOT EVALUABLE")
        has(L, "READING: none (NOT EVALUABLE: no sentence; PC3 recorded descriptively)")
        has(L, "P1 p_d interval: NOT SCORED (PC1 NOT EVALUABLE; CR-4); p_d 0.003322 printed")
        has(L, "F-PC: NOT FIRED (PC1 NOT EVALUABLE); a NOT CERTIFIED outcome does not reinstate F-TAX's certificate clause; "
               "F-TAX N-1 FIRES stands")
        has(L, "P1 PC1 readings (NOT CERTIFIED 0.85, CERTIFIED 0.12, NOT EVALUABLE 0.03): outcome NOT EVALUABLE, Brier (3-way sum) 1.6778")

    def c0_just_below(tmp):
        # C0 p95 one step below the null p95 -> comparable
        r, _L, _o = run(tmp, k_root=15, c0_mode="below")
        assert r["comparable"] is True and r["c0_p95"] < r["null_p95"] and r["verdict"] == "NOT CERTIFIED", r
        sub = os.path.join(tmp, "p05")
        os.makedirs(sub)
        r2, L2, _o2 = run(sub, k_root=15, c0_mode="at_p05")
        has(L2, "P2 C0 p95 below the null p05 (p 0.90): event no (C0 p95 0.014000, null p05 0.014000), Brier 0.8100")

    def pc3_bh(tmp):
        r, L, _o = run(tmp)
        assert (r["pc3"], r["scored"]) == (4, 12), r
        has(L, "PC3 (DESCRIPTIVE-ONLY; src geometry unknown: a non-certification is never a power statement): 12 of 14 anchors "
               "scored, 2 not scored (< 2 children); BH over the scored TOP family (m = 12, q = 0.05): 4 certified (step-up "
               "cutoff 1/60 = 0.016667)")
        has(L, "P3 PC3 certified anchors 0 [0, 2] of the scored: FAILED (4 of 12)")
        has(L, "  PC3 %-34s n %4s: NOT SCORED (1 child(ren) after pooling)" % ("M/c09", "500"))
        assert any(l.startswith("  PC3 M/law") and "k   0 p 0.003322 BH-IN | deflated k 0 | G12 tree split 0.040000 k 97" in l
                   for l in L), [l for l in L if "M/law" in l]

    def pc3_empty(tmp):
        r, L, _o = run(tmp, pc3_k=[30] * 14)
        assert (r["pc3"], r["scored"]) == (0, 14), r
        has(L, "PC3 (DESCRIPTIVE-ONLY; src geometry unknown: a non-certification is never a power statement): 14 of 14 anchors "
               "scored, 0 not scored (< 2 children); BH over the scored TOP family (m = 14, q = 0.05): 0 certified")
        has(L, "P3 PC3 certified anchors 0 [0, 2] of the scored: HELD (0 of 14)")

    def pc3_boundary(tmp):
        # m = 14 at k = 0: p = 1/301 <= 0.05/14 -> one rejection (the registered reachability); k = 1 alone: 2/301 > 1/280 -> none
        r, _L, _o = run(tmp, pc3_k=[0] + [200] * 13)
        assert r["pc3"] == 1, r
        sub = os.path.join(tmp, "b")
        os.makedirs(sub)
        r2, _L2, _o2 = run(sub, pc3_k=[1] + [200] * 13)
        assert r2["pc3"] == 0, r2

    def i1_registered_refusal(tmp):
        refused(tmp, "I-1 FAILED (registered form): 6 of 60 reproduce; no readout (D-I1)", i1_reg_ok=6)

    def i1_live(tmp):
        r, L, _o = run(tmp, i1_reg_ok=6, form="live", bracket="prog L99999 (registrar)")
        has(L, "I-1: PASS (live leg, under the registrar's bracket: prog L99999 (registrar))")
        has(L, "I-1 live leg: 30 of 30 accepted real site populations reproduce the splitter's dasguptaDeltaNorm bit for bit (30 not accepted)")
        has(L, "I-1 registered form: 6 of 60 sites reproduce the persisted dasguptaDeltaNorm at 6 printed digits (G12's sites 60)")

    def i1_live_gate(tmp):
        # READY_cert_positive_control C-1: the live gate refuses 59 rows, 0 accepted, and one accepted mismatch
        br = dict(i1_reg_ok=6, form="live", bracket="prog L23470")
        for i, (live, needle) in enumerate((("rows59", "I-1 FAILED (live leg): 30 of 30 accepted reproduce"),
                                            ("none", "I-1 FAILED (live leg): 0 of 0 accepted reproduce"),
                                            ("one_false", "I-1 FAILED (live leg): 29 of 30 accepted reproduce"))):
            sub = os.path.join(tmp, str(i))
            os.makedirs(sub)
            refused(sub, needle, live=live, **br)

    def unsorted_reps(tmp):
        # replicates in shuffled rep order: the quantiles and k_d are order-free
        r, L, _o = run(tmp, k_root=15, shuffle_sn=True)
        assert (r["verdict"], r["k_d"], r["null_p95"], r["null_p05"]) == ("NOT CERTIFIED", 15, 0.284, 0.014), r
        has(L, "PC1 declared statistic (14 categories, root n 6993) = 0.285000; null p05 0.014000 / p50 0.149000 / p95 0.284000 / "
               "max 0.299000; k_d = 15 of 300 replicates >= it; p_d = (k_d + 1) / 301 = 16/301 = 0.053156")

    def i1_live_no_bracket(tmp):
        refused(tmp, "I-1 form 'live' with bracket '' is not admissible", form="live", bracket="")

    def i2_refusal(tmp):
        refused(tmp, "I-2 FAILED: ['a00'] do not reproduce", i2_bad=True)

    def i2_lines(tmp):
        _r, L, _o = run(tmp)
        has(L, "I-2: a01 M/chemistry re-run k 300, G12 k 300; a02 M/math re-run k 292, G12 k 292; a00 M/law re-run k 97, G12 k 97")
        has(L, "I-2: PASS (the three registered sites reproduce exactly); beside: 11 of 11 other anchors reproduce")

    def refusals(tmp):
        for i, (needle, kw) in enumerate([
                ("the arm's status is 'REFUSED: x'", dict(status="REFUSED: x")),
                ("a partial file", dict(partial=True)),
                ("embeddings_cache.db changed during the arm", dict(hashes_equal=False)),
                ("the arm read labels sha256", dict(lab_mismatch=True)),
                ("instrument: the arm ran sepBar='0.025'", dict(sepbar="0.025"))]):
            sub = os.path.join(tmp, str(i))
            os.makedirs(sub)
            refused(sub, needle, **kw)

    def labels(tmp):
        ids = {"q1", "q2", "q3"}
        stem = lambda t: t.lower()
        qrows = {"q1": (11, "MMLU_PRO_LB/math"), "q2": (12, "MMLU_PRO_LB/law"), "q3": (13, "MMLU_PRO_LB/law")}
        crows = {11: ("MMLU_PRO", "math", "A"), 12: ("MMLU_PRO", "law", "B"), 13: ("MMLU_PRO", "law", "C")}
        side = {"i:a": ("c1", "TRAIN", ()), "i:b": ("c2", "TRAIN", ()), "i:c": ("c3", "TRAIN", ())}
        kept = {"i:a": {"src": "s_math", "dom": "math"}, "i:b": {"src": "s_law", "dom": "law"}}
        global N_CATS
        saved = N_CATS
        N_CATS = 2
        try:
            rows, cnt = build_labels(ids, qrows, crows, side, kept, stem)
            assert rows == [("q1", "math", "s_math"), ("q2", "law", "s_law"), ("q3", "law", "")], rows
            assert (cnt["src"], cnt["no_src"], cnt["categories"]) == (2, 1, {"law": 2, "math": 1}), cnt
            assert labels_bytes(rows) == b"query_id\tcategory\tsrc\nq1\tmath\ts_math\nq2\tlaw\ts_law\nq3\tlaw\t\n"
            for needle, mut in (("not TRAIN", lambda: side.__setitem__("i:c", ("c3", "EVAL", ()))),
                                ("ground_truth_category", lambda: qrows.__setitem__("q3", (13, "MMLU_PRO_LB/math"))),
                                ("not MMLU_PRO", lambda: crows.__setitem__(13, ("BBH", "law", "C"))),
                                ("gold's domain", lambda: kept.__setitem__("i:c", {"src": "z", "dom": "math"}))):
                s0, q0, c0_, k0 = dict(side), dict(qrows), dict(crows), dict(kept)
                mut()
                try:
                    build_labels(ids, qrows, crows, side, kept, stem)
                    raise AssertionError("not refused: " + needle)
                except SystemExit as e:
                    assert needle in str(e), (needle, e)
                side.clear(); side.update(s0); qrows.clear(); qrows.update(q0); crows.clear(); crows.update(c0_)
                kept.clear(); kept.update(k0)
            N_CATS = 3
            try:
                build_labels(ids, qrows, crows, side, kept, stem)
                raise AssertionError("2 categories accepted as 3")
            except SystemExit as e:
                assert "2 declared categories, not the registered 3" in str(e), e
        finally:
            N_CATS = saved

    def pooling(tmp):
        ids = ["q%03d" % i for i in range(200)]
        src = {q: ("b" if i < 60 else "a" if i < 115 else "c" if i < 169 else "d" if i < 179 else "") for i, q in enumerate(ids)}
        assert src_groups(ids, src) == ([55, 60, 85], 85), src_groups(ids, src)
        assert src_groups(ids[:50], src) == ([50], 50)

    def helpers(tmp):
        xs = sorted(i / 1000.0 for i in range(300))
        assert (pctl(xs, 0.95), pctl(xs, 0.05), pctl(xs, 0.5)) == (0.284, 0.014, 0.149)
        assert pctl([1, 2, 3, 4, 5, 6, 7], 0.95) == 7 and pctl([1, 2, 3], 0.0) == 1    # rank ceil(6.65) = 7; clamped at 1
        assert p_of(14) == Fraction(15, 301) and p_of(14) <= BAR and not (p_of(15) <= BAR)
        assert wall_estimate(6993, [(778, True)]) > 119.0
        cfg = G.load_config(os.path.join(ROOT, CONFIG_REL))
        assert command(cfg, "SNAP", 6) == (
            '.\\gradlew.bat certPositiveControl --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 '
            '"-DsnapshotId=SNAP" "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" '
            '"-DdeclaredLabels=experiment_results/cert_positive_control/declared_labels.tsv" '
            '"-Dg12Sites=experiment_results/archv2/rp12_r2/g12/G12_sites.csv" '
            '"-DoutDir=experiment_results/cert_positive_control/arm"'), command(cfg, "SNAP", 6)
        assert command(cfg, "S", 8).endswith(' "-DsiteNullHeap=8g"')
        assert same_checkout(ROOT) and not same_checkout(tmp)
        for fn_, arg in ((prepare, (tmp,)), (hashes, ("before", tmp))):
            try:
                fn_(*arg)
                raise AssertionError("%s from another data root not refused" % fn_.__name__)
            except SystemExit as e:
                assert "run" in str(e) and tmp in str(e), e

    def main_analyze(tmp):
        # the run-of-record entry point: main(["--analyze"]) reads OUT_REL/arm, OUT_REL/declared_labels.tsv, G12_SITES_REL
        global OUT_REL, G12_SITES_REL, G12_SITES_BLOB
        arm, outd, g, lab, blob = _fx(tmp, k_root=15)
        os.replace(arm, os.path.join(outd, ARM_NAME))
        os.replace(lab, os.path.join(outd, LABELS_NAME))
        saved = (OUT_REL, G12_SITES_REL, G12_SITES_BLOB)
        OUT_REL, G12_SITES_REL, G12_SITES_BLOB = os.path.abspath(outd), os.path.abspath(g), blob
        try:
            rc = main(["--analyze"])
            if rc != 0:
                raise AssertionError("main --analyze returned %r" % rc)
        finally:
            OUT_REL, G12_SITES_REL, G12_SITES_BLOB = saved
        txt = open(os.path.join(outd, OUTCOME_NAME), encoding="utf-8").read()
        assert "\nPC1: NOT CERTIFIED\n" in txt and "\nF-PC: NOT FIRED (PC1 NOT CERTIFIED)" in txt, txt[-600:]

    def preview(tmp):
        # I-1 preview (numpy replica): a site whose persisted value is the routine's on its children reproduces, one with a
        # drifted value does not -> (1, 2)
        import sqlite3
        import struct
        db = os.path.join(tmp, "embeddings_cache.db")
        c = sqlite3.connect(db)
        c.execute("CREATE TABLE queries (id TEXT PRIMARY KEY, raw_text TEXT, distilled_text TEXT, ground_truth_category TEXT, query_id INTEGER)")
        c.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
        vecs = {"q1": [1, 0, 0, 0], "q2": [0.9, 0.1, 0, 0], "q3": [0, 1, 0, 0], "q4": [0, 0.9, 0.1, 0]}
        for q, v in vecs.items():
            c.execute("INSERT INTO queries VALUES (?,?,?,?,?)", (q, q, "t" + q, "", 1))
            c.execute("INSERT INTO embeddings VALUES (?,?)", ("t" + q, struct.pack(">4f", *v)))
        c.commit(); c.close()
        import numpy as np
        X = {q: np.array(v, dtype=np.float32).astype(np.float64) for q, v in vecs.items()}
        X = {q: v / math.sqrt(float(v @ v)) for q, v in X.items()}
        g1, g2 = ["q1", "q2"], ["q3", "q4"]
        s1, s2 = X["q1"] + X["q2"], X["q3"] + X["q4"]
        tot = s1 + s2
        val = 1.0 - ((2 - float(s1 @ s1) / 2) * 2 * 2) / ((16 - float(tot @ tot)) * 4 / 12.0)   # sum_c (n_c^2 - |s_c|^2), symmetric groups
        nodes = [{"id": "r", "childIds": ["a", "b"], "dasguptaDeltaNorm": val, "queryIds": []},
                 {"id": "a", "childIds": [], "dasguptaDeltaNorm": 0.0, "queryIds": g1},
                 {"id": "b", "childIds": [], "dasguptaDeltaNorm": 0.0, "queryIds": g2},
                 {"id": "x", "childIds": ["a", "b"], "dasguptaDeltaNorm": val + 0.001, "queryIds": []}]
        gr = {"nodes": nodes}
        assert i1_preview(gr, {n["id"]: n for n in nodes}, tmp, 4) == (1, 2), (val, i1_preview(gr, {n["id"]: n for n in nodes}, tmp, 4))

    for nm, fn in [("main --analyze (the run-of-record wiring)", main_analyze), ("I-1 preview (numpy replica)", preview),("PC1 NOT CERTIFIED at k_d = 15 (+ every printed line, write-once)", not_cert),
                   ("PC1 CERTIFIED at the boundary k_d = 14; F-PC FIRED; P2 yes", cert_boundary),
                   ("a tie counts (>=)", tie_counts), ("C0 reaches the null p95 -> NOT EVALUABLE", not_evaluable),
                   ("C0 one step below -> comparable", c0_just_below), ("PC3 BH 4 of 12; unscored counted", pc3_bh),
                   ("PC3 empty set; P3 HELD", pc3_empty), ("PC3 m = 14 reachability boundary", pc3_boundary),
                   ("I-1 registered refusal (6 of 60)", i1_registered_refusal), ("I-1 live under a bracket", i1_live),
                   ("I-1 live without a bracket refused", i1_live_no_bracket),
                   ("I-1 live gate refusals (59 rows, 0 accepted, one mismatch)", i1_live_gate),
                   ("replicates in shuffled rep order", unsorted_reps), ("I-2 mismatch refused", i2_refusal),
                   ("I-2 lines", i2_lines), ("refusals: status, partial, hashes, labels, instrument", refusals),
                   ("label building and its refusals", labels), ("PC3 pooling rule", pooling), ("helpers", helpers)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


MUTANTS = [
    ("M0 control (no-op; must SURVIVE)", "TAG = \"[CPC]\"", "TAG = \"[CPC]\""),
    ("M1 >= -> >", "    return sum(1 for x in xs if x >= obs)", "    return sum(1 for x in xs if x > obs)"),
    ("M2 p = k/300", "    return CR.p_site(k, REPS)", "    return Fraction(k, REPS)"),
    ("M3 p = (k+1)/300", "    return CR.p_site(k, REPS)", "    return Fraction(k + 1, REPS)"),
    ("M4 C0 reaches strict", "    comparable = not bool(c0_p95 >= n_p95)", "    comparable = not bool(c0_p95 > n_p95)"),
    ("M5 C0 not a precondition", "    if not comparable:\n        verdict = \"NOT EVALUABLE\"\n    elif bool(p_d <= BAR):",
     "    if bool(p_d <= BAR):\n        verdict = \"CERTIFIED\"\n    elif not comparable:\n        verdict = \"NOT EVALUABLE\"\n    elif bool(p_d <= BAR):"),
    ("M7 p95 -> max", "    c0_p95, n_p95, n_p05 = pctl(c0, 0.95), pctl(sn, 0.95), pctl(sn, 0.05)",
     "    c0_p95, n_p95, n_p05 = pctl(c0, 0.95), sn[-1], pctl(sn, 0.05)"),
    ("M8 percentile rank floor", "    r = min(max(int(math.ceil(q * n)), 1), n)", "    r = min(max(int(math.floor(q * n)), 1), n)"),
    ("M9 I-1 registered gate skipped", "        if not (len(reg) == N_G12_SITES and reg_ok == len(reg)):",
     "        if False:"),
    ("M10 I-2 first site only", "    for n in named:\n        r = i2.get(n)", "    for n in named[:1]:\n        r = i2.get(n)"),
    ("M11 P2 non-strict", "    ev2 = bool(c0_p95 < n_p05)", "    ev2 = bool(c0_p95 <= n_p05)"),
    ("M12 BH q 0.10", "    rej, thr = CR.bh_cutoff(ps, Q)", "    rej, thr = CR.bh_cutoff(ps, Q * 2)"),
    ("M13 PC3 from the deflated arm", "        xs = R.get((r[\"site_id\"], \"SN\"))\n        if xs is None:",
     "        xs = R.get((r[\"site_id\"], \"SND\")) or R.get((r[\"site_id\"], \"SN\"))\n        if xs is None:"),
    ("M14 hash check removed", "    if json.load(open(hb)) != json.load(open(ha)):", "    if False:"),
    ("M15 write-once pre-check removed", "        if os.path.exists(p):\n            refuse(\"%s exists: the outcome is write-once\" % p)",
     "        if False:\n            refuse(\"%s exists: the outcome is write-once\" % p)"),
    ("M16 pooling >= -> >", "        if by[s] >= mcs:", "        if by[s] > mcs:"),
    ("M17 F-PC on NOT CERTIFIED", "    fired = verdict == \"CERTIFIED\"", "    fired = verdict != \"NOT EVALUABLE\""),
    ("M18 P1 scored when NOT EVALUABLE", "    if verdict != \"NOT EVALUABLE\":\n        held", "    if True:\n        held"),
    ("M19 gtc check removed", "    if gtc != \"MMLU_PRO_LB/\" + dom:", "    if False:"),
    ("M20 TRAIN check removed", "        if si is None or si[1] != \"TRAIN\":", "        if si is None:"),
    ("M21 P3 interval upper 3", "P3_POINT, P3_LO, P3_HI = 0, 0, 2", "P3_POINT, P3_LO, P3_HI = 0, 0, 4"),
    ("M22 partial replicates accepted", "        if [i for i, _x in xs] != list(range(REPS)):", "        if False:"),
    ("M24 I-2 smallest -> largest TOP k", "    return [chem[0], math_[0], top[0][1]]", "    return [chem[0], math_[0], top[-1][1]]"),
    ("M25 k_d from the deflated arm", "    k_d = kcount(R[(rid, \"SN\")], d)", "    k_d = kcount(R[(rid, \"SND\")], d)"),
    ("M26 C0 p95 from the null", "    c0 = sorted(R[(rid, \"C0\")])", "    c0 = sorted(R[(rid, \"SN\")])"),
    ("M27 PC3 BH over all anchors (unscored as p = 1)", "    rej, thr = CR.bh_cutoff(ps, Q)",
     "    rej, thr = CR.bh_cutoff(ps + [Fraction(1)] * (len(anch) - len(scored)), Q)"),
    ("R1 live rows == 60 dropped", "        if not (len(liv) == N_G12_SITES and len(liv_acc) >= 1 and liv_ok == len(liv_acc)):",
     "        if not (len(liv_acc) >= 1 and liv_ok == len(liv_acc)):"),
    ("R2 live >= 1 accepted -> >= 0", "        if not (len(liv) == N_G12_SITES and len(liv_acc) >= 1 and liv_ok == len(liv_acc)):",
     "        if not (len(liv) == N_G12_SITES and len(liv_acc) >= 0 and liv_ok == len(liv_acc)):"),
    ("R9 live mismatch ignored", "        if not (len(liv) == N_G12_SITES and len(liv_acc) >= 1 and liv_ok == len(liv_acc)):",
     "        if not (len(liv) == N_G12_SITES and len(liv_acc) >= 1):"),
    ("R6 null quantiles on the unsorted list", "    sn = sorted(R[(rid, \"SN\")])", "    sn = list(R[(rid, \"SN\")])"),
    ("M23 instrument check removed", "        if st.get(k) != v:\n            refuse(\"instrument", "        if False:\n            refuse(\"instrument"),
]


def mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    rows = []
    for name, old, new in MUTANTS:
        if src.count(old) < 1:
            rows.append((name, "NOT APPLIED (pattern absent)"))
            continue
        mut = src.replace(old, new, 1)
        tmp = os.path.join(HERE, "_cpc_mutant_%d.py" % os.getpid())
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(mut)
            env = dict(os.environ, CPC_MUTANT="1")
            r = subprocess.run([sys.executable, tmp, "--selftest"], capture_output=True, text=True, env=env, timeout=600)
            rows.append((name, "KILLED" if r.returncode != 0 else "SURVIVED"))
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    for n, v in rows:
        print("  %-36s %s" % (n, v))
    k = sum(1 for n, v in rows if v == "KILLED" and not n.startswith("M0 "))
    ctrl = [v for n, v in rows if n.startswith("M0 ")] == ["SURVIVED"]
    print("%s mutants: %d of %d killed; control M0 %s" % (TAG, k, len(rows) - 1, "SURVIVED (harness valid)" if ctrl else "NOT SURVIVED (harness broken)"))
    return 0 if (k == len(rows) - 1 and ctrl) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--prepare", action="store_true")
    g.add_argument("--hashes", choices=("before", "after"))
    g.add_argument("--analyze", action="store_true")
    ap.add_argument("--data-root", default=os.environ.get("TAXOARENA_DATA_ROOT", ROOT))
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return mutants()
    if a.dry_run:
        dry_run(a.data_root)
        return 0
    if a.prepare:
        prepare(a.data_root)
        return 0
    if a.hashes:
        hashes(a.hashes, a.data_root)
        return 0
    if not _IN_SELFTEST and selftest() != 0:
        refuse("the selftest is red: no readout")
    d = os.path.join(ROOT, OUT_REL)
    analyze(os.path.join(d, ARM_NAME), d, os.path.join(ROOT, G12_SITES_REL), os.path.join(d, LABELS_NAME), g12_blob=G12_SITES_BLOB)
    return 0


if __name__ == "__main__":
    sys.exit(main())
