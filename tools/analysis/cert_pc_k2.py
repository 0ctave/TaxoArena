"""cert_pc_k2.py: CERT-PC-K2, the K2 site file, the dry-run, the launch command and the READOUT of the declared two-family arm
(SeparationNullBySizeTest `certPcK2 - ...`, gradle task certPcK2). ZERO calls.

REGISTRATION OF RECORD (it governs; this docstring restates it and never replaces it): docs/judge_v2_program.md
"## Registered 2026-10-03 (before any code or call) — CERT-PC-K2: does the site-null certificate certify a DECLARED 2-way
partition inside a single MMLU-Pro category (source family: MMLU-original vs added sources) at G12's depth-1 site sizes (n 486,
441; 5 subsamples each) in math, physics and economics? (zero calls; site-null runs, CPU)" (span L23901-L23913, commit d50c47d4);
record docs/agents/results/CERT-PC-K2.json.
  ANCHORS math (489 / 316 = 805), physics (248 / 530 = 778), economics (266 / 238 = 504): MMLU-original (src ori_mmlu-*) vs added
  sources (stemez-*, theoremQA-*, scibench-*); TRAIN counts from MMLU-GOLD-GEOMETRY's src join on the member's 6,988 kept TRAIN
  items. Economics at n 486 uses 486 of 504 items, so its 5 subsamples overlap almost fully (disclosed).
  Per anchor and size (486, 441), 5 stratified subsamples (proportional to the two families; draw seeds 1-5); each a site with
  its own plain null (300 reps), C0 (300 size-matched 2-group relabellings) and the DEGENERATE / C0 gate first (CERT-PC-SIZE
  Q-1, Q-2).
  Per anchor: CERTIFIED-AT-SIZE iff >= 4 of 5 subsamples certified (k_d <= 14, C0 comparable), NOT-CERTIFIED iff <= 1, MIXED
  otherwise, NOT EVALUABLE gate first.
  PK1 (DECIDING, n 486): K2-CERTIFIABLE iff >= 2 of the 3 anchors CERTIFIED-AT-SIZE; K2-NOT iff 0; MIXED otherwise. PK2
  (deciding): the same at n 441.
  P1 PK1 K2-CERTIFIABLE 0.35 / MIXED 0.30 / K2-NOT 0.35. P2 physics CERTIFIED-AT-SIZE 0.45, economics 0.40, math 0.35. P3 C0
  comparable everywhere 0.85.
  F-PK fires iff PK1 reads K2-NOT.

INSTRUMENT. certPcSize's arm members, reused unchanged (pcsParseSites, pcsPopulation, pcsC0Seed, cpcDeclaredSite, cpcRelabelNull),
driven by a NEW method certPcK2 (additions only; the only new check is pk2SiteError: K2_<anchor>_n<n>_d<draw> sites with exactly
the two families; javap proof in the commit message). cert_pc_size.py blob de39c648 is IMPORTED (allocate, draw, assemble,
CPC_LABELS_SHA, the CPC / G modules it pins), never copied. Labels: CERT-POSITIVE-CONTROL's label file of record
(declared_labels.tsv, sha256 c0a20662..., 6,993 TRAIN ids of the B0/mmlu_pro_lb member root, columns query_id / category / src,
src = MMLU-GOLD-GEOMETRY's join, CPC CR-2), snapshot 20261001_094311_Headless_Run_Auto_ge; config
experiment_configs/rp12_r2/B0/g12_site_null.sitenull (slice 512, sepBar 0.0145, dropTop 0, whiten false, 300 reps, 12 threads).

LAUNCH SEQUENCE (run-operator; a site null = a rule-7 heavy process: W1-W5, 12 JVM threads, never beside a construction,
another site null or a pool reader; the pool check in the B0-2 form first; run from the data root's checkout, e.g. the
rp12-r2-run worktree after merging this branch there, TAXOARENA_DATA_ROOT unset; nothing here is committed from the run):
  python tools/analysis/cert_pc_k2.py --selftest                       (never with python -O: refused)
  python tools/analysis/cert_pc_k2.py --mutants
  TAXOARENA_DATA_ROOT=<main checkout> python tools/analysis/v2_union_pool.py --dry-run   (rc 0; pool file sha256-lf16 79d48f4b36434a55)
  python tools/analysis/cert_pc_k2.py --dry-run  [--data-root DIR] [--cpc-labels FILE]   populations, twins, allocations,
                                         overlaps, site file sha (= SITES_SHA256), G12 sizes beside, heap, wall, COMMAND; writes nothing
  python tools/analysis/cert_pc_k2.py --prepare  [--cpc-labels FILE]   writes experiment_results/cert_pc_k2/site_labels.tsv (x),
                                         refuses unless its sha256 is SITES_SHA256
  python tools/analysis/cert_pc_k2.py --hashes before
  <the printed COMMAND: .\\gradlew.bat certPcK2 ...>   then  .\\gradlew.bat --stop
  python tools/analysis/cert_pc_k2.py --hashes after
  python tools/analysis/cert_pc_k2.py --analyze  [--cpc-labels FILE]   outcome (write-once, mode x):
        experiment_results/cert_pc_k2/outcome.txt and pk2_sites.csv; runs the selftest first; refuses a REFUSED / partial arm,
        a hash change, an IDENTITY failure, a site file that is not the registered draw (rebuilt from the pinned labels; sha pinned),
        an instrument or snapshot other than the registered, a missing / extra / wrong-size / wrong-family site.
Outputs are NEVER committed: pin them by sha256 and back them up to E:/TaxoArena_backup_<date>_<tag> with SHA256SUMS.txt (the
emb_hashes_before/after.json included: CERT-PC-SIZE POSTRUN's LOW item).

BUILDER'S READINGS (each flagged to the registrar; printed in the outcome header):
  PK-1 population: per anchor, the member root's TRAIN ids whose CPC label carries that category and a non-empty src (gold's
       join; an id it excluded carries no src and is outside every anchor population); family 'ori_mmlu' iff src starts with
       'ori_mmlu-', 'added' iff it starts with 'stemez-', 'theoremQA-' or 'scibench-', any other src refuses. The arm's unit is
       the query id; ids sharing one split_side.stem_key of their distilled_text (the gold join's item) are collapsed to the
       smallest id, so the populations equal the registered ITEM counts: one twin, math scibench-stat q_dd452b7da138bf6f (twin of
       q_92ffd94400d168cd), is dropped (pinned in TWINS; the dry-run recomputes it from the cache and refuses on a difference).
       The populations are refused unless they equal 266 / 238, 489 / 316, 248 / 530.
  PK-2 allocation and draw: CERT-PC-SIZE's PCS-1 (cert_pc_size.draw, imported) over the two families ('added' sorts first);
       random.Random(seed) per (anchor, size, seed) with seeds 1-5 (the same seeds in every anchor and size: different
       populations). Site file: IDENTITY first (CERT-PC-SIZE's rows: the 6,993 root ids, 14 categories, sorted by id), then the
       anchors in name order (economics, math, physics), sizes 486 then 441, draws 1..5; each site's rows sorted by id; the
       label column is the family.
  PK-3 seeds: CERT-PC-SIZE's PCS-3 with the K2 site name (plain null base 20260908, deflated 88820260908, C0 cpcSeed(20261002,
       name, 0)); IDENTITY's plain null seeded by the root id (PC1's).
  PK-4 C0 "comparable" = C0 p95 < the plain null p95 (CERT-PC-SIZE PCS-4).
  PK-5 the anchor-level gate first (CERT-PC-SIZE's Q-1 / Q-2 rulings, 94fae9d5): 2 or more of the 5 subsamples NOT EVALUABLE
       (C0, DEGENERATE < 20 reached, or n < 110) -> NOT EVALUABLE, before CERTIFIED-AT-SIZE / NOT-CERTIFIED / MIXED.
  PK-6 (registration query Q-K1 to the registrar) PK1 / PK2 when an anchor is NOT EVALUABLE: the registered word is printed when
       it does not depend on how the NOT EVALUABLE anchors would have read (the word at c certified equals the word at c + e);
       otherwise PK reads NOT EVALUABLE (F-PK not fired, P1 not scored). With all three anchors evaluable this IS the
       registered rule; the counts (certified / not / MIXED / NOT EVALUABLE anchors) are printed either way.
  PK-7 P2 is scored at n 486 (the deciding size) per anchor, NOT SCORED for a NOT EVALUABLE anchor; P1 three-way Brier sum,
       NOT SCORED when PK1 is NOT EVALUABLE; P3 binary Brier over all 30 subsamples.
  PK-8 IDENTITY (CERT-PC-SIZE's instrument precondition) is kept: the full root reproduces declared 0.107803, k_d 0, seed
       n00000001, n 6,993, AND (CERT-PC-SIZE READY D-2) its plain null p95 / max equal PC1's 0.041626 / 0.042414; refused otherwise.
  PK-9 CERT-PC-SIZE READY D-1 fixed: --analyze rebuilds the site file from the CPC labels (sha256 pinned) and TWINS and refuses
       on any byte difference, and refuses unless the file's sha256 equals SITES_SHA256 and the arm's status line.

SELFTEST (python tools/analysis/cert_pc_k2.py --selftest): every registered branch through the real entry points (analyze(),
main(["--analyze"]), build_site_bytes(), populations()) on fixtures whose answer is known by hand, asserting the printed VALUE;
the case list is in selftest(). MUTANTS: --mutants runs the table MUTANTS below against --selftest (temporary copies, removed);
the table is in the commit message.
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

TAG = "[PK2]"
_IN_SELFTEST = False
PCS_BLOB = "de39c6488e0dca7dded489f34cbae291af5d3dd5"


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _import_pinned(name, blob):
    got = RO.git_blob_lf(os.path.join(HERE, name + ".py"))
    if got != blob:
        refuse("%s.py is blob %s, not the pinned %s (imported, never copied)" % (name, got, blob))
    return __import__(name)


PCS = _import_pinned("cert_pc_size", PCS_BLOB)
CPC = PCS.CPC
G = PCS.G

OUT_REL = "experiment_results/cert_pc_k2"
CPC_LABELS_REL = PCS.CPC_LABELS_REL
LABELS_SHA = PCS.CPC_LABELS_SHA
SITES_NAME, ARM_NAME, OUTCOME_NAME, CSV_NAME = "site_labels.tsv", "arm", "outcome.txt", "pk2_sites.csv"
SITE_HEADER = PCS.SITE_HEADER
SNAPSHOT, ROOT_ID, N_ROOT = PCS.SNAPSHOT, PCS.ROOT_ID, PCS.N_ROOT
ANCHORS = ("economics", "math", "physics")
FAM_ADD, FAM_ORI = "added", "ori_mmlu"
ADDED_PREFIXES = ("stemez-", "theoremQA-", "scibench-")
REG_COUNTS = {"economics": (266, 238), "math": (489, 316), "physics": (248, 530)}     # (ori_mmlu, added), registered items
TWINS = ("q_dd452b7da138bf6f",)                     # PK-1: stem-key twins dropped (math scibench-stat, twin of q_92ffd94400d168cd)
SITES_SHA256 = "efcc4e99cf5eed50d04249a28e7aa896b1518f39088102e25055e6a3f65393bb"   # the registered draw (dry-run 2026-10-03, data root rp12-r2-run)
SIZES = (486, 441)
DECIDING = {486: "PK1", 441: "PK2"}
DRAWS = (1, 2, 3, 4, 5)
REPS, MCS, DEGENERATE_MIN = 300, 55, 20
BAR = Fraction(1, 20)
IDENTITY_DECLARED, IDENTITY_K = "0.107803", 0
PC1_P95, PC1_MAX = "0.041626", "0.042414"
INSTRUMENT = {"arm": "certPcK2", "reps": "300", "sliceDim": "512", "sepBar": "0.0145", "dropTop": "0", "whiten": "false",
              "minClusterSize": "55", "c0Seed": "20261002"}
P1_PROBS = {"K2-CERTIFIABLE": 0.35, "MIXED": 0.30, "K2-NOT": 0.35}
P2_P = {"physics": 0.45, "economics": 0.40, "math": 0.35}
P3_P = 0.85
PCS_WALL_S = 926          # CERT-PC-SIZE's arm (POSTRUN 541fde40): IDENTITY + 15 subsamples (n 486 / 441 / 264) x (plain + deflated + C0)
REG = ('docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — CERT-PC-K2: ..." L23901-L23913 '
       '(as registered, d50c47d4)')

SENT_FPK_FIRED = ("F-PK: FIRED (PK1 K2-NOT): the certificate does not certify a declared 2-way partition inside one category at "
                  "G12's depth-1 sizes; G12's 0 of 60 is then read as possibly a k = 2 / within-category sensitivity limit "
                  "(CERT-PC-SIZE's \"not explained by n alone\" narrows to 14-way structure). F-TAX N-1 and F2 stand.")
SENT_CERT = ("READING (PK1 K2-CERTIFIABLE): N-1's empty set reads \"the tree's data-driven depth-1 splits are less separated than "
             "a declared source-family split inside a category at the same n and k\". F-TAX N-1 and F2 stand.")
LIKE = ["LIKE WITH LIKE: | site | k | population | partition |",
        "  | CERT-PC-K2 (this) | 2 | one category | declared source family |",
        "  | G12 TOP sites (of record) | 2-3 | one anchor (routed) | data-driven split |",
        "  | CERT-PC-SIZE (of record) | 14 | all categories | declared categories |",
        "  k- and size-matched to G12; the population is the declared category (labels), not the routed anchor region"]
DOES_NOT_SHOW = ("DOES NOT SHOW: a certificate of any tree site; that source families are the right sub-taxonomy; other categories, "
                 "members, draws or slices; a mode test")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def site_names():
    return ["K2_%s_n%d_d%d" % (a, n, d) for a in ANCHORS for n in SIZES for d in DRAWS]


def parse_name(s):
    _k2, a, n, d = s.split("_")
    return a, int(n[1:]), int(d[1:])


# ------------------------------------------------------------------------------------------------ labels, populations, site file
def read_labels(path, sha=None):
    """CPC's label file (sha256 pinned) -> ({id: category}, {id: src})."""
    sha = LABELS_SHA if sha is None else sha
    if not os.path.isfile(path):
        refuse("CERT-POSITIVE-CONTROL's label file %s not found (--cpc-labels)" % path)
    b = open(path, "rb").read()
    if sha256_bytes(b) != sha:
        refuse("%s is sha256 %s, not CERT-POSITIVE-CONTROL's label file of record %s" % (path, sha256_bytes(b), sha))
    lines = b.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if not lines or lines[0] != CPC.LABEL_HEADER:
        refuse("the CPC label file's header is not %r" % CPC.LABEL_HEADER)
    cat, src = {}, {}
    for ln in lines[1:]:
        p = ln.split("\t")
        if len(p) != 3 or not p[0] or not p[1] or p[0] in cat:
            refuse("malformed or duplicate CPC label row %r" % ln)
        cat[p[0]], src[p[0]] = p[1], p[2]
    return cat, src


def family(s):
    if s.startswith("ori_mmlu-"):
        return FAM_ORI
    if s.startswith(ADDED_PREFIXES):
        return FAM_ADD
    refuse("src %r is neither ori_mmlu-* nor an added source (stemez / theoremQA / scibench)" % s)


def find_twins(cat, src, text):
    """PK-1: inside each anchor's src-carrying ids, ids sharing a stem key of their text; all but the smallest -> sorted list."""
    import split_side
    drop = []
    for a in ANCHORS:
        by = {}
        for q in sorted(q for q in cat if cat[q] == a and src[q]):
            by.setdefault(split_side.stem_key(text[q]), []).append(q)
        for v in by.values():
            drop.extend(v[1:])
    return sorted(drop)


def populations(cat, src, twins=TWINS, reg=None):
    """PK-1 -> {anchor: {family: sorted ids}}; refuses unless the family counts equal the registered ones."""
    reg = REG_COUNTS if reg is None else reg
    tw = set(twins)
    pops = {}
    for a in ANCHORS:
        fam = {FAM_ADD: [], FAM_ORI: []}
        for q in sorted(cat):
            if cat[q] == a and src[q] and q not in tw:
                fam[family(src[q])].append(q)
        got = (len(fam[FAM_ORI]), len(fam[FAM_ADD]))
        if got != reg[a]:
            refuse("%s: ori_mmlu / added = %d / %d, not the registered %d / %d" % (a, got[0], got[1], reg[a][0], reg[a][1]))
        pops[a] = fam
    return pops


def build_site_bytes(cat, src, twins=TWINS, reg=None):
    """-> (bytes, {site: sorted ids}, {site: {id: label}}, pops); IDENTITY first (CERT-PC-SIZE's rows), then the K2 sites."""
    if len(set(cat.values())) != 14:
        refuse("%d declared categories, not 14" % len(set(cat.values())))
    pops = populations(cat, src, twins, reg)
    lab = {q: family(src[q]) for a in ANCHORS for f in pops[a].values() for q in f}
    sites = {"IDENTITY": sorted(cat)}
    labels = {"IDENTITY": {q: cat[q] for q in sites["IDENTITY"]}}
    for a in ANCHORS:
        for n in SIZES:
            for d in DRAWS:
                s = "K2_%s_n%d_d%d" % (a, n, d)
                sites[s] = PCS.draw(pops[a], n, d)
                labels[s] = {q: lab[q] for q in sites[s]}
    rows = [SITE_HEADER]
    for s, ids in sites.items():
        rows.extend("%s\t%s\t%s" % (s, q, labels[s][q]) for q in ids)
    return ("\n".join(rows) + "\n").encode("utf-8"), sites, labels, pops


def overlaps(sites):
    """Disclosure: per anchor and size the pairwise overlaps of the 5 draws (min / max); the same-seed n 441 within n 486."""
    out = {}
    for a in ANCHORS:
        for n in SIZES:
            ov = [len(set(sites["K2_%s_n%d_d%d" % (a, n, x)]) & set(sites["K2_%s_n%d_d%d" % (a, n, y)]))
                  for x in DRAWS for y in DRAWS if x < y]
            out[(a, n)] = (min(ov), max(ov))
        out[(a, "same-seed")] = [len(set(sites["K2_%s_n441_d%d" % (a, d)]) & set(sites["K2_%s_n486_d%d" % (a, d)])) for d in DRAWS]
    return out


def overlap_lines(sites, pops):
    ov = overlaps(sites)
    L = []
    for a in ANCHORS:
        N = len(pops[a][FAM_ADD]) + len(pops[a][FAM_ORI])
        L.append("OVERLAP %s (population %d): 5 draws pairwise min / max: n 486 %d / %d (chance %.0f), n 441 %d / %d (chance %.0f); "
                 "same-seed n 441 within n 486: %s of 441 (chance %.0f)%s" % (
                     a, N, ov[(a, 486)][0], ov[(a, 486)][1], 486.0 * 486 / N, ov[(a, 441)][0], ov[(a, 441)][1], 441.0 * 441 / N,
                     ov[(a, "same-seed")], 441.0 * 486 / N,
                     "; DISCLOSED: n 486 uses 486 of %d items, the 5 subsamples overlap almost fully" % N if 486 > 0.9 * N else ""))
    L.append("OVERLAP: the 5 draws of one anchor and the two sizes are NOT independent replicates (CERT-PC-SIZE D-5)")
    return L


def parse_site_file(path):
    return PCS.parse_site_file(path)


# ------------------------------------------------------------------------------------------------ dry-run / prepare / hashes
def cache_texts(data_root, ids):
    con = RO.open_ro(os.path.join(data_root, "embeddings_cache.db"))
    try:
        txt, ids = {}, list(ids)
        for i in range(0, len(ids), 500):
            ch = ids[i:i + 500]
            for q, t in con.execute("SELECT id, distilled_text FROM queries WHERE id IN (%s)" % ",".join("?" * len(ch)), ch):
                txt[q] = t
    finally:
        con.close()
    if len(txt) != len(ids):
        refuse("embeddings_cache.db holds %d of %d anchor texts" % (len(txt), len(ids)))
    return txt


def assemble(data_root, cpc_labels):
    cfg, sid, root, cat14, _d, _s = PCS.assemble(data_root, cpc_labels)      # snapshot, root, labels pin, region == labels
    cat, src = read_labels(cpc_labels)
    if cat != cat14:
        refuse("the label file read twice differs")
    anchor_ids = [q for q in cat if cat[q] in ANCHORS and src[q]]
    tw = find_twins(cat, src, cache_texts(data_root, anchor_ids))
    if tuple(tw) != TWINS:
        refuse("stem-key twins in the anchors %s, not the pinned %s" % (tw, list(TWINS)))
    data, sites, labels, pops = build_site_bytes(cat, src)
    return cfg, sid, root, cat, src, data, sites, labels, pops


def command(cfg, heap):
    return ('.\\gradlew.bat certPcK2 --console=plain --offline --no-daemon -PjvmThreads=%d -PnullReps=%d '
            '"-DsnapshotId=%s" "-DsliceDim=%d" "-DsepBar=%s" "-DdropTop=%d" "-Dwhiten=%s" "-DsiteLabels=%s/%s" "-DoutDir=%s/%s"%s'
            % (cfg["jvmThreads"], cfg["nullReps"], SNAPSHOT, cfg["sliceDim"], repr(cfg["sepBar"]), cfg["dropTop"],
               str(cfg["whiten"]).lower(), OUT_REL, SITES_NAME, OUT_REL, ARM_NAME,
               "" if heap <= G.DEFAULT_HEAP_GB else ' "-DsiteNullHeap=%dg"' % heap))


def dry_run(data_root, cpc_labels, out=print):
    out("pool: the B0-2 check is the operator's (v2_union_pool.py --dry-run); this mode opens no pool table")
    out("%s DRY RUN: zero calls, nothing written, no null replicate, no verdict" % TAG)
    CPC.heavy_check()
    cfg, sid, root, cat, src, data, sites, labels, pops = assemble(data_root, cpc_labels)
    out("%s member B0/mmlu_pro_lb = snapshot %s; root %s '%s' n = %d (TRAIN); CPC labels %s sha256 %s (= the pin)"
        % (TAG, sid, root["id"], root.get("label"), len(cat), cpc_labels, LABELS_SHA[:16]))
    out("%s stem-key twins dropped (PK-1): %s (= the pin)" % (TAG, list(TWINS)))
    for a in ANCHORS:
        cnt = {f: len(v) for f, v in pops[a].items()}
        out("%s %s: ori_mmlu %d / added %d = %d (registered %d / %d)" % (TAG, a, cnt[FAM_ORI], cnt[FAM_ADD], cnt[FAM_ORI] + cnt[FAM_ADD],
                                                                         REG_COUNTS[a][0], REG_COUNTS[a][1]))
        for n in SIZES:
            q = PCS.allocate(cnt, n)
            out("%s   n %d (%s): allocation added %d / ori_mmlu %d" % (TAG, n, DECIDING[n], q[FAM_ADD], q[FAM_ORI]))
    for ln in overlap_lines(sites, pops):
        out("%s %s" % (TAG, ln))
    g12 = sorted(int(r["n"]) for r in csv.DictReader(open(os.path.join(ROOT, PCS.G12_SITES_REL), encoding="utf-8"))
                 if r["family_key"] == "TOP")
    out("%s G12 TOP-site n (beside; the sizes were fixed by the registration): %s" % (TAG, g12))
    sha = sha256_bytes(data)
    sp = os.path.join(ROOT, OUT_REL, SITES_NAME)
    out("%s site file %s/%s: %d sites, %d rows, sha256 %s (%s; %s)" % (
        TAG, OUT_REL, SITES_NAME, len(sites), data.count(b"\n") - 1, sha,
        "= SITES_SHA256" if sha == SITES_SHA256 else "NOT SITES_SHA256 %s" % SITES_SHA256,
        "present, IDENTICAL" if os.path.exists(sp) and open(sp, "rb").read() == data else
        ("present, DIFFERENT" if os.path.exists(sp) else "absent: --prepare writes it")))
    need, live, heap = G.heap_estimate(N_ROOT, cfg["sliceDim"], cfg["nullReps"], cfg["jvmThreads"])
    out("%s heap (g12_site_null's rule, the IDENTITY site n %d): live %d, peak %.2f GB -> %s" % (
        TAG, N_ROOT, live, need, "fits the 6g default" if heap <= G.DEFAULT_HEAP_GB else "-DsiteNullHeap=%dg" % heap))
    out("%s wall: about %.0f min at %d threads (bound: CERT-PC-SIZE's arm took %d s for IDENTITY + 15 subsamples at n <= 486; "
        "this arm runs the same IDENTITY + 30 subsamples at n 441-486; budget the window at about 35-40 min)"
        % (TAG, 2.0 * PCS_WALL_S / 60.0, cfg["jvmThreads"], PCS_WALL_S))
    if os.path.exists(os.path.join(ROOT, OUT_REL, ARM_NAME)):
        refuse("%s/%s exists: the arm writes it once" % (OUT_REL, ARM_NAME))
    pf = os.path.join(ROOT, "experiment_configs", "engine_pool_%s.json" % cfg["poolId"])
    pf_sha = sha256_bytes(open(pf, "rb").read().replace(b"\r\n", b"\n"))
    out("%s pool file sha256-lf %s (%s)" % (TAG, pf_sha[:16], "= the stamp's" if pf_sha == cfg["enginePoolSha256Lf"] else "MISMATCH"))
    if pf_sha != cfg["enginePoolSha256Lf"]:
        refuse("the engine pool file's LF sha256 is not the stamp's")
    same = CPC.same_checkout(data_root)
    out("%s LAUNCH FROM %s%s" % (TAG, os.path.abspath(data_root), "" if same else
        " (the data root is NOT this checkout: this dry-run is a preview; merge the branch there and run from there)"))
    out("%s COMMAND: %s" % (TAG, command(cfg, heap)))
    out("%s after the arm: .\\gradlew.bat --stop" % TAG)
    return dict(sha=sha, heap=heap, sites=len(sites))


def prepare(data_root, cpc_labels):
    if not CPC.same_checkout(data_root):
        refuse("--prepare writes the site file into this checkout; the arm reads it from the data root's: run from %s" % data_root)
    CPC.heavy_check()
    _c, _s, _r, _cat, _src, data, sites, _l, _p = assemble(data_root, cpc_labels)
    if sha256_bytes(data) != SITES_SHA256:
        refuse("the site file's sha256 %s is not SITES_SHA256 %s (the registered draw)" % (sha256_bytes(data), SITES_SHA256))
    d = os.path.join(ROOT, OUT_REL)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, SITES_NAME), "xb") as f:
        f.write(data)
    print("%s wrote %s/%s (%d sites, sha256 %s)" % (TAG, OUT_REL, SITES_NAME, len(sites), sha256_bytes(data)))


def hashes(label, data_root):
    if not CPC.same_checkout(data_root):
        refuse("--hashes records the cache the arm reads: run it from the data root's checkout %s" % data_root)
    CPC.heavy_check()
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
def subsample_status(n, k, comparable, reached):
    if n < 2 * MCS:
        return "NOT EVALUABLE (NULL-INFEASIBLE)"
    if reached < DEGENERATE_MIN:
        return "NOT EVALUABLE (DEGENERATE)"
    if not comparable:
        return "NOT EVALUABLE (C0)"
    return "CERTIFIED" if bool(CPC.p_of(k) <= BAR) else "NOT CERTIFIED"


def anchor_verdict(statuses):
    ne = sum(1 for s in statuses if s.startswith("NOT EVALUABLE"))
    c = sum(1 for s in statuses if s == "CERTIFIED")
    if ne >= 2:
        return "NOT EVALUABLE"
    if c >= 4:
        return "CERTIFIED-AT-SIZE"
    if c <= 1:
        return "NOT-CERTIFIED"
    return "MIXED"


def pk_word(c):
    if c >= 2:
        return "K2-CERTIFIABLE"
    if c == 0:
        return "K2-NOT"
    return "MIXED"


def pk_verdict(anchor_words):
    """PK1 / PK2 from the three anchor verdicts (PK-6: NOT EVALUABLE anchors decide nothing they could change)."""
    c = sum(1 for v in anchor_words if v == "CERTIFIED-AT-SIZE")
    e = sum(1 for v in anchor_words if v == "NOT EVALUABLE")
    lo, hi = pk_word(c), pk_word(c + e)
    return lo if lo == hi else "NOT EVALUABLE"


def median(xs):
    s = sorted(xs)
    return s[len(s) // 2]


def analyze(arm_dir, out_dir, sites_path, labels_path, out=print):
    outcome_p, csv_p = os.path.join(out_dir, OUTCOME_NAME), os.path.join(out_dir, CSV_NAME)
    for p in (outcome_p, csv_p):
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
    if st.get("snapshot") != SNAPSHOT:
        refuse("the arm read snapshot %r, not %s" % (st.get("snapshot"), SNAPSHOT))
    sbytes = open(sites_path, "rb").read()
    s_sha = sha256_bytes(sbytes)
    if st.get("sites_sha256") != s_sha:
        refuse("the arm read site file sha256 %s; %s is %s" % (st.get("sites_sha256"), sites_path, s_sha))
    if s_sha != SITES_SHA256:
        refuse("the site file's sha256 %s is not SITES_SHA256 %s (the registered draw)" % (s_sha, SITES_SHA256))
    cat, src = read_labels(labels_path)
    rebuilt, _rs, rlabels, rpops = build_site_bytes(cat, src)
    if rebuilt != sbytes:
        refuse("the site file is not the registered draw rebuilt from the CPC labels (sha256 %s) and TWINS %s"
               % (LABELS_SHA[:16], list(TWINS)))
    hb, ha = (os.path.join(out_dir, "emb_hashes_%s.json" % x) for x in ("before", "after"))
    if not (os.path.isfile(hb) and os.path.isfile(ha)):
        refuse("the embeddings_cache.db hashes before and after the arm are owed (--hashes before / after)")
    if json.load(open(hb)) != json.load(open(ha)):
        refuse("embeddings_cache.db changed during the arm (per-table hashes differ)")
    sfile = parse_site_file(sites_path)
    want = ["IDENTITY"] + site_names()
    if list(sfile) != want:
        refuse("the site file lists %s, not IDENTITY + the 30 registered K2 sites in order" % list(sfile)[:20])
    say("%s CERT-PC-K2 outcome (tools/analysis/cert_pc_k2.py blob %s; cert_pc_size.py blob %s imported). Zero calls."
        % (TAG, RO.git_blob_lf(os.path.abspath(__file__)), PCS_BLOB))
    say("registration: " + REG)
    say("arm: %s; snapshot %s; site file sha256 %s (= SITES_SHA256; rebuilt from the CPC labels sha256 %s and TWINS %s: "
        "byte-identical); reps %s; sliceDim %s; sepBar %s; dropTop %s; whiten %s; minClusterSize %s; C0 seed base %s; threads %s; "
        "embeddings_cache.db per-table hashes before == after" % (
            st["arm"], st["snapshot"], s_sha, LABELS_SHA[:16], list(TWINS), st["reps"], st["sliceDim"], st["sepBar"], st["dropTop"],
            st["whiten"], st["minClusterSize"], st["c0Seed"], st.get("threads")))
    say("builder's readings PK-1..PK-9 (docstring); registration query Q-K1 (PK-6: PK with NOT EVALUABLE anchors) to the registrar")
    for a in ANCHORS:
        say("population %s: ori_mmlu %d / added %d (registered %d / %d)" % (
            a, len(rpops[a][FAM_ORI]), len(rpops[a][FAM_ADD]), REG_COUNTS[a][0], REG_COUNTS[a][1]))

    with open(os.path.join(arm_dir, "sites.csv"), newline="", encoding="utf-8") as f:
        rows = {r["site_id"]: r for r in csv.DictReader(f)}
    if list(rows) != want:
        refuse("sites.csv holds %s, not IDENTITY + the 30 registered K2 sites in order" % list(rows)[:20])
    reps = {}
    with open(os.path.join(arm_dir, "replicates.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            reps.setdefault((r["site_id"], r["arm"]), []).append((int(r["rep"]), float(r["stat"])))
    for key, xs in reps.items():
        if [i for i, _x in xs] != list(range(REPS)):
            refuse("replicates %s: reps %d, not 0..%d in order (a partial file)" % (key, len(xs), REPS - 1))
    R = {k: [x for _i, x in v] for k, v in reps.items()}
    for s in want:
        for a_ in (("SN",) if s == "IDENTITY" else ("SN", "SND", "C0")):
            if (s, a_) not in R:
                refuse("replicates: %s's %s arm is missing" % (s, a_))

    # IDENTITY (PK-8)
    ir = rows["IDENTITY"]
    d0 = float(ir["declared_stat"])
    k0 = CPC.kcount(R[("IDENTITY", "SN")], d0)
    sn0 = sorted(R[("IDENTITY", "SN")])
    p95_0, max_0 = "%.6f" % CPC.pctl(sn0, 0.95), "%.6f" % sn0[-1]
    say("IDENTITY: full-size root n %s, declared %.6f (registered %s), k_d %d of %d (registered %d); null seeded by %s; null p95 "
        "%s / max %s (PC1 of record %s / %s)" % (ir["n"], d0, IDENTITY_DECLARED, k0, REPS, IDENTITY_K, ir["null_seed_id"],
                                                  p95_0, max_0, PC1_P95, PC1_MAX))
    if not ("%.6f" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K and int(ir["n"]) == N_ROOT and ir["null_seed_id"] == ROOT_ID
            and p95_0 == PC1_P95 and max_0 == PC1_MAX):
        refuse("IDENTITY FAILED: declared %.6f k_d %d n %s seed %s p95 %s max %s (want %s, %d, %d, %s, %s, %s); no readout"
               % (d0, k0, ir["n"], ir["null_seed_id"], p95_0, max_0, IDENTITY_DECLARED, IDENTITY_K, N_ROOT, ROOT_ID, PC1_P95, PC1_MAX))
    say("IDENTITY: REPRODUCED (precondition held; null p95 / max equal PC1's)")

    se = math.sqrt(0.05 * 0.95 / REPS)
    say("SUPPORT (a) deciding denominator: 3 anchors x 5 subsamples per deciding size (n 486 PK1, n 441 PK2), each a site with %d "
        "null replicates; (b) DEFF 1.0 by construction (independent seeded generator draws; no item-level resampling: a tree-arm "
        "DEFF does not apply, D-PR-1); (c) n_eff = %d replicates per subsample; (d) SE of an exceedance proportion at the bar "
        "sqrt(0.05 x 0.95 / %d) = %.4f per subsample; (e) MDE80 = 2.80 x SE = %.4f per subsample; (g) floor 1/301 = %.4f << 0.05; "
        "NULL-INFEASIBLE below n %d, DEGENERATE below %d reached replicates" % (
            REPS, REPS, REPS, se, 2.80 * se, 1 / 301.0, 2 * MCS, DEGENERATE_MIN))
    say("SUPPORT: no matches and no questions: wrong(established), the tie conventions A / B and a question-clustered bootstrap "
        "are N/A to a null exceedance count")
    for ln in LIKE:
        say(ln)
    for ln in overlap_lines({s: sorted(sfile[s]) for s in site_names()}, rpops):
        say(ln)

    res, out_rows = {}, []
    for s in site_names():
        a, n_reg, _d = parse_name(s)
        r = rows[s]
        n = int(r["n"])
        fam = rlabels[s]
        gs = "%d/%d" % (sum(1 for v in fam.values() if v == FAM_ADD), sum(1 for v in fam.values() if v == FAM_ORI))
        if n != len(sfile[s]) or n != n_reg or int(r["groups"]) != 2 or r["group_sizes"] != gs:
            refuse("sites.csv: %s n %s groups %s sizes %s (the site file holds %d, families added/ori_mmlu %s; want n %d, 2 groups)"
                   % (s, r["n"], r["groups"], r["group_sizes"], len(sfile[s]), gs, n_reg))
        d = float(r["declared_stat"])
        sn = sorted(R[(s, "SN")])
        k = CPC.kcount(R[(s, "SN")], d)
        if k != int(r["k_declared"]):
            refuse("%s: k_d recount %d != the arm's %s" % (s, k, r["k_declared"]))
        c0 = sorted(R[(s, "C0")])
        c0p95, np95 = CPC.pctl(c0, 0.95), CPC.pctl(sn, 0.95)
        if c0p95 != float(r["c0_p95"]):
            refuse("%s: C0 p95 recount %r != the arm's %s" % (s, c0p95, r["c0_p95"]))
        comparable = not bool(c0p95 >= np95)
        reached = sum(1 for x in R[(s, "SN")] if x > 0.0)
        status = subsample_status(n, k, comparable, reached)
        sd = R[(s, "SND")]
        kd = CPC.kcount(sd, d)
        res[s] = dict(anchor=a, n=n, d=d, k=k, np95=np95, c0p95=c0p95, comparable=comparable, reached=reached, status=status)
        say("  %-20s n %3d (added/ori %s): declared %.6f; null p05 %.6f / p50 %.6f / p95 %.6f / max %.6f; k_d %3d of %d, p_d "
            "%d/301 = %.6f; C0 p95 %.6f (%s); reached %d; deflated k %d (p95 %.6f) -> %s" % (
                s, n, gs, d, CPC.pctl(sn, 0.05), CPC.pctl(sn, 0.50), np95, sn[-1], k, REPS, k + 1, float(CPC.p_of(k)), c0p95,
                "comparable" if comparable else "FAILS: reaches the null p95", reached, kd, CPC.pctl(sorted(sd), 0.95), status))
        out_rows.append([s, a, n, gs, "%.6f" % d, k, "%d/301" % (k + 1), "%.6f" % np95, "%.6f" % c0p95, str(comparable).lower(),
                         reached, kd, status])

    av, pk = {}, {}
    for n in SIZES:
        for a in ANCHORS:
            sts = [res["K2_%s_n%d_d%d" % (a, n, dd)]["status"] for dd in DRAWS]
            c = sum(1 for x in sts if x == "CERTIFIED")
            nc = sum(1 for x in sts if x == "NOT CERTIFIED")
            ne_c0 = sum(1 for x in sts if x == "NOT EVALUABLE (C0)")
            ne_all = sum(1 for x in sts if x.startswith("NOT EVALUABLE"))
            av[(a, n)] = anchor_verdict(sts)
            ds = [res["K2_%s_n%d_d%d" % (a, n, dd)]["d"] for dd in DRAWS]
            ns = [res["K2_%s_n%d_d%d" % (a, n, dd)]["np95"] for dd in DRAWS]
            say("ANCHOR %s n %d: %s; certified %d, not certified %d, NOT EVALUABLE %d (C0 %d, degenerate / infeasible %d) of 5 "
                "(gate first: PK-5); median declared %.6f vs median null p95 %.6f" % (
                    a, n, av[(a, n)], c, nc, ne_all, ne_c0, ne_all - ne_c0, median(ds), median(ns)))
        words = [av[(a, n)] for a in ANCHORS]
        pk[n] = pk_verdict(words)
        say("%s (n %d): %s; anchors CERTIFIED-AT-SIZE %d, NOT-CERTIFIED %d, MIXED %d, NOT EVALUABLE %d of 3 (PK-6)" % (
            DECIDING[n], n, pk[n], words.count("CERTIFIED-AT-SIZE"), words.count("NOT-CERTIFIED"), words.count("MIXED"),
            words.count("NOT EVALUABLE")))

    pk1 = pk[486]
    if pk1 == "K2-NOT":
        say(SENT_FPK_FIRED)
    else:
        say("F-PK: NOT FIRED (PK1 %s). F-TAX N-1 and F2 stand." % pk1)
        if pk1 == "K2-CERTIFIABLE":
            say(SENT_CERT)
        else:
            say("READING: none (PK1 %s: %s; no sentence)" % (pk1, "a registered MIXED" if pk1 == "MIXED" else "not evaluable (PK-6)"))

    if pk1 in P1_PROBS:
        b1 = sum((p - (1.0 if v == pk1 else 0.0)) ** 2 for v, p in P1_PROBS.items())
        say("P1 PK1 readings (K2-CERTIFIABLE 0.35, MIXED 0.30, K2-NOT 0.35): outcome %s, Brier (3-way sum) %.4f" % (pk1, b1))
    else:
        say("P1 PK1 readings: NOT SCORED (PK1 NOT EVALUABLE; PK-7)")
    for a in ("physics", "economics", "math"):
        v = av[(a, 486)]
        if v != "NOT EVALUABLE":
            e = bool(v == "CERTIFIED-AT-SIZE")
            say("P2 %s CERTIFIED-AT-SIZE at n 486 (p %.2f): event %s (%s), Brier %.4f" % (
                a, P2_P[a], "yes" if e else "no", v, (P2_P[a] - (1.0 if e else 0.0)) ** 2))
        else:
            say("P2 %s CERTIFIED-AT-SIZE at n 486 (p %.2f): NOT SCORED (NOT EVALUABLE; PK-7)" % (a, P2_P[a]))
    allc = sum(1 for s in site_names() if res[s]["comparable"])
    e3 = bool(allc == len(site_names()))
    say("P3 C0 comparable on every subsample (p 0.85): event %s (%d of %d comparable), Brier %.4f" % (
        "yes" if e3 else "no", allc, len(site_names()), (P3_P - (1.0 if e3 else 0.0)) ** 2))
    say(DOES_NOT_SHOW)

    os.makedirs(out_dir, exist_ok=True)
    with open(outcome_p, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(csv_p, "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["site", "anchor", "n", "added_ori", "declared", "k_d", "p_d", "null_p95", "c0_p95", "c0_comparable", "reached",
                    "defl_k", "status"])
        w.writerows(out_rows)
    out("%s wrote %s and %s (write-once)" % (TAG, outcome_p, csv_p))
    return dict(pk=pk, anchors=av, res=res, fired=bool(pk1 == "K2-NOT"), lines=L)


# ------------------------------------------------------------------------------------------------ selftest
def _labels_fixture():
    """6,993 ids: the three anchors at the registered family counts (math with one stem-key twin, the twin dropped by TWINS), 11
    other categories filling the rest; 4 ids without src (gold's exclusions)."""
    cat, src, i = {}, {}, 0

    def add(c, s, qid=None):
        nonlocal i
        q = qid or "q_%05d" % i
        i += 1
        cat[q], src[q] = c, s
    for a, (o, ad) in REG_COUNTS.items():
        for j in range(o):
            add(a, "ori_mmlu-%s" % a)
        pre = {"economics": ["stemez-Econ"], "math": ["scibench-stat", "theoremQA-Math"], "physics": ["stemez-Phys", "scibench-x",
                                                                                                         "theoremQA-Physics"]}[a]
        for j in range(ad):
            add(a, pre[j % len(pre)])
    add("math", "scibench-stat", TWINS[0])
    add("math", "")
    add("math", "")
    others = ["c%02d" % j for j in range(11)]
    while len(cat) < N_ROOT - 1:
        add(others[len(cat) % 11], "ori_mmlu-x")
    add("c00", "")
    return cat, src


def _write_labels(path, cat, src):
    data = (CPC.LABEL_HEADER + "\n" + "".join("%s\t%s\t%s\n" % (q, cat[q], src[q]) for q in sorted(cat))).encode("utf-8")
    open(path, "wb").write(data)
    return sha256_bytes(data)


def _fx(tmp, spec=None, status="COMPLETE", hashes_equal=True, partial=False, site_sha_bad=False, sepbar="0.0145", arm="certPcK2",
        snapshot=SNAPSHOT, ident_d=0.10780301, ident_k=0, ident_seed="n00000001", ident_n=6993, ident_p95=0.041626,
        ident_max=0.042414, drop_site=None, n_bad=None, k_lie=None, c0_lie=None, gs_lie=None, tamper_site=None,
        drop_reps_arm=None):
    """spec[site] = dict(k=, c0=small|equal|below, reached=None|int, scale=): SN = i*scale (i = 0..299), declared = (300-k)*scale
    so exactly k replicates are >= it (a tie at k); null p95 = 284*scale. Returns (arm, out, sites path, labels path, pins)."""
    spec = spec or {}
    arm_d, outd = os.path.join(tmp, "arm"), os.path.join(tmp, "out")
    os.makedirs(arm_d)
    os.makedirs(outd)
    cat, src = _labels_fixture()
    lp = os.path.join(tmp, "declared_labels.tsv")
    lsha = _write_labels(lp, cat, src)
    data, sites, labels, _p = build_site_bytes(cat, src)
    pin = sha256_bytes(data)
    sp = os.path.join(outd, SITES_NAME)
    if tamper_site:          # swap one K2 row's id for an id outside the draw (same size, same family): not the registered draw
        a, _n, _d = parse_name(tamper_site)
        fam = labels[tamper_site][sites[tamper_site][0]]
        repl = next(q for q in sorted(cat) if cat[q] == a and src[q] and q not in sites[tamper_site] and q not in TWINS
                    and family(src[q]) == fam)
        old = ("%s\t%s\t%s\n" % (tamper_site, sites[tamper_site][0], fam)).encode()
        data = data.replace(old, ("%s\t%s\t%s\n" % (tamper_site, repl, fam)).encode(), 1)
    open(sp, "wb").write(data)
    sha = sha256_bytes(data if not site_sha_bad else b"x")
    with open(os.path.join(arm_d, "status.txt"), "w") as f:
        f.write("%s\narm=%s\nsnapshot=%s\nsites_sha256=%s\nreps=300\nsliceDim=512\nsepBar=%s\ndropTop=0\nwhiten=false\n"
                "minClusterSize=55\nc0Seed=20261002\nthreads=12\n" % (status, arm, snapshot, sha, sepbar))
    names = ["IDENTITY"] + site_names()
    if drop_site:
        names.remove(drop_site)
    srows, rep_lines = [], []
    for s in names:
        if s == "IDENTITY":
            sn = [i / 100000.0 for i in range(284)] + [ident_p95] * 15 + [ident_max]   # p95 = rank 285 (index 284); max last
            if ident_k:
                sn[-1] = ident_d + 1e-9
            srows.append('IDENTITY,"IDENTITY",%d,14,,%r,%d,,,,,%s,300' % (ident_n, ident_d, ident_k, ident_seed))
            rep_lines += ['"IDENTITY",SN,%d,%r' % (i, x) for i, x in enumerate(sn[:150] if partial else sn)]
            continue
        sp_ = dict(k=0, c0="small", reached=None, scale=1 / 1000.0)
        sp_.update(spec.get(s, {}))
        sc = sp_["scale"]
        n = len(sites[s]) + (1 if n_bad == s else 0)
        fam = labels[s]
        gs = "%d/%d" % (sum(1 for v in fam.values() if v == FAM_ADD), sum(1 for v in fam.values() if v == FAM_ORI))
        if gs_lie == s:
            gs = "1/%d" % (n - 1)
        sn = [i * sc for i in range(300)]
        if sp_["reached"] is not None:
            sn = [0.0] * (300 - sp_["reached"]) + [0.5 * sc + j * sc for j in range(sp_["reached"])]
        d = (300 - sp_["k"]) * sc if sp_["reached"] is None else 1000.0 * sc
        c0 = {"small": [i * sc * 0.001 for i in range(300)], "equal": list(sn), "below": [x - 1e-12 for x in sn]}[sp_["c0"]]
        k_arm = sum(1 for x in sn if x >= d) + (1 if k_lie == s else 0)
        c0p = CPC.pctl(sorted(c0), 0.95) + (1e-6 if c0_lie == s else 0.0)
        srows.append('K2,"%s",%d,2,%s,%r,%d,1,0,%r,123,%s,300' % (s, n, gs, d, k_arm, c0p, s))
        for arm_, xs in (("SN", sn), ("SND", [x / 2 for x in sn]), ("C0", c0)):
            if drop_reps_arm == (s, arm_):
                continue
            rep_lines += ['"%s",%s,%d,%r' % (s, arm_, i, x) for i, x in enumerate(xs)]
    with open(os.path.join(arm_d, "sites.csv"), "w") as f:
        f.write("role,site_id,n,groups,group_sizes,declared_stat,k_declared,defl_dims,defl_k_declared,c0_p95,c0_seed,null_seed_id,reps\n")
        f.write("\n".join(srows) + "\n")
    with open(os.path.join(arm_d, "replicates.csv"), "w") as f:
        f.write("site_id,arm,rep,stat\n" + "\n".join(rep_lines) + "\n")
    for x in ("before", "after"):
        json.dump({"embeddings": "aa/1", "queries": "bb/2" if (hashes_equal or x == "before") else "cc/2"},
                  open(os.path.join(outd, "emb_hashes_%s.json" % x), "w"))
    return arm_d, outd, sp, lp, (lsha, pin)


@contextlib.contextmanager
def _pins(lsha, pin):
    global LABELS_SHA, SITES_SHA256
    saved = (LABELS_SHA, SITES_SHA256)
    LABELS_SHA, SITES_SHA256 = lsha, pin
    try:
        yield
    finally:
        LABELS_SHA, SITES_SHA256 = saved


def _ks(anchor, size, ks, **kw):
    return {"K2_%s_n%d_d%d" % (anchor, size, i + 1): dict(k=k, **kw) for i, k in enumerate(ks)}


def selftest():
    global _IN_SELFTEST
    _IN_SELFTEST = True
    if not __debug__:
        refuse("python -O strips the selftest's asserts (CERT-PC-SIZE READY D-4): run without -O")
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="pk2st_")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:            # noqa: BLE001
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))

    def run(tmp, pins_override=None, **kw):
        arm, outd, sp, lp, pins = _fx(tmp, **kw)
        lines = []
        with _pins(*(pins_override or pins)):
            r = analyze(arm, outd, sp, lp, out=lines.append)
        return r, lines, outd

    def refused(tmp, needle, pins_override=None, **kw):
        arm, outd, sp, lp, pins = _fx(tmp, **kw)
        try:
            with _pins(*(pins_override(pins) if pins_override else pins)):
                analyze(arm, outd, sp, lp, out=lambda s: None)
        except SystemExit as e:
            assert needle in str(e), (needle, str(e))
            assert not os.path.exists(os.path.join(outd, OUTCOME_NAME)), "a refusal wrote an outcome"
            return
        raise AssertionError("not refused: " + needle)

    def has(lines, s):
        assert s in lines, "missing line %r; got:\n%s" % (s, "\n".join(lines))

    def sub(tmp, i):
        p = os.path.join(tmp, "s%d" % i)
        os.makedirs(p)
        return p

    def all_cert(tmp):
        r, L, outd = run(tmp)
        assert r["pk"] == {486: "K2-CERTIFIABLE", 441: "K2-CERTIFIABLE"} and r["fired"] is False, r["pk"]
        has(L, "ANCHOR economics n 486: CERTIFIED-AT-SIZE; certified 5, not certified 0, NOT EVALUABLE 0 (C0 0, degenerate / "
               "infeasible 0) of 5 (gate first: PK-5); median declared 0.300000 vs median null p95 0.284000")
        has(L, "PK1 (n 486): K2-CERTIFIABLE; anchors CERTIFIED-AT-SIZE 3, NOT-CERTIFIED 0, MIXED 0, NOT EVALUABLE 0 of 3 (PK-6)")
        has(L, "PK2 (n 441): K2-CERTIFIABLE; anchors CERTIFIED-AT-SIZE 3, NOT-CERTIFIED 0, MIXED 0, NOT EVALUABLE 0 of 3 (PK-6)")
        has(L, "F-PK: NOT FIRED (PK1 K2-CERTIFIABLE). F-TAX N-1 and F2 stand.")
        has(L, SENT_CERT)
        has(L, "P1 PK1 readings (K2-CERTIFIABLE 0.35, MIXED 0.30, K2-NOT 0.35): outcome K2-CERTIFIABLE, Brier (3-way sum) 0.6350")
        has(L, "P2 physics CERTIFIED-AT-SIZE at n 486 (p 0.45): event yes (CERTIFIED-AT-SIZE), Brier 0.3025")
        has(L, "P2 economics CERTIFIED-AT-SIZE at n 486 (p 0.40): event yes (CERTIFIED-AT-SIZE), Brier 0.3600")
        has(L, "P2 math CERTIFIED-AT-SIZE at n 486 (p 0.35): event yes (CERTIFIED-AT-SIZE), Brier 0.4225")
        has(L, "P3 C0 comparable on every subsample (p 0.85): event yes (30 of 30 comparable), Brier 0.0225")
        has(L, "IDENTITY: full-size root n 6993, declared 0.107803 (registered 0.107803), k_d 0 of 300 (registered 0); null seeded "
               "by n00000001; null p95 0.041626 / max 0.042414 (PC1 of record 0.041626 / 0.042414)")
        has(L, "IDENTITY: REPRODUCED (precondition held; null p95 / max equal PC1's)")
        has(L, "population math: ori_mmlu 489 / added 316 (registered 489 / 316)")
        has(L, "population physics: ori_mmlu 248 / added 530 (registered 248 / 530)")
        has(L, "  K2_economics_n486_d1 n 486 (added/ori 230/256): declared 0.300000; null p05 0.014000 / p50 0.149000 / p95 0.284000 "
               "/ max 0.299000; k_d   0 of 300, p_d 1/301 = 0.003322; C0 p95 0.000284 (comparable); reached 299; deflated k 0 (p95 "
               "0.142000) -> CERTIFIED")
        has(L, "  K2_math_n441_d1      n 441 (added/ori 173/268): declared 0.300000; null p05 0.014000 / p50 0.149000 / p95 0.284000 "
               "/ max 0.299000; k_d   0 of 300, p_d 1/301 = 0.003322; C0 p95 0.000284 (comparable); reached 299; deflated k 0 (p95 "
               "0.142000) -> CERTIFIED")
        has(L, DOES_NOT_SHOW)
        has(L, "OVERLAP economics (population 504): 5 draws pairwise min / max: n 486 468 / 470 (chance 469), n 441 383 / 390 "
               "(chance 386); same-seed n 441 within n 486: [433, 432, 431, 435, 432] of 441 (chance 425); DISCLOSED: n 486 uses 486 "
               "of 504 items, the 5 subsamples overlap almost fully")
        assert any(l.startswith("OVERLAP physics (population 778)") and "DISCLOSED" not in l for l in L)
        assert any(l.startswith("SUPPORT (a) deciding denominator: 3 anchors x 5 subsamples") and "0.0126" in l and "0.0352" in l
                   for l in L), L
        txt = open(os.path.join(outd, OUTCOME_NAME), encoding="utf-8").read()
        assert txt.startswith("pool: none (no DB opened)\n") and "\nPK1 (n 486): K2-CERTIFIABLE;" in txt
        rows = list(csv.DictReader(open(os.path.join(outd, CSV_NAME), encoding="utf-8")))
        assert len(rows) == 30 and rows[0]["site"] == "K2_economics_n486_d1" and rows[0]["p_d"] == "1/301" and \
            rows[0]["status"] == "CERTIFIED" and rows[0]["added_ori"] == "230/256", rows[0]
        try:
            with _pins(*_fx(sub(tmp, 9))[4]):
                analyze(os.path.join(tmp, "arm"), outd, os.path.join(outd, SITES_NAME), os.path.join(tmp, "declared_labels.tsv"),
                        out=lambda s: None)
            raise AssertionError("second analyze not refused")
        except SystemExit as e:
            assert "write-once" in str(e), e

    def anchor_boundaries(tmp):
        # physics at n 486: k 14 certifies (p 15/301), k 15 does not; 4 / 3 / 2 / 1 / 0 of 5
        for i, (ks, v) in enumerate((([14, 14, 14, 14, 15], "CERTIFIED-AT-SIZE"), ([14, 14, 14, 15, 15], "MIXED"),
                                     ([14, 14, 15, 15, 15], "MIXED"), ([14, 15, 15, 15, 15], "NOT-CERTIFIED"),
                                     ([15, 300, 15, 16, 200], "NOT-CERTIFIED"))):
            r, L, _o = run(sub(tmp, i), spec=_ks("physics", 486, ks))
            assert r["anchors"][("physics", 486)] == v and r["anchors"][("physics", 441)] == "CERTIFIED-AT-SIZE", (ks, r["anchors"])
            assert r["pk"][486] == "K2-CERTIFIABLE", r["pk"]            # economics and math still certify
            assert r["res"]["K2_physics_n486_d1"]["k"] == ks[0]
            if v == "NOT-CERTIFIED":
                has(L, "P2 physics CERTIFIED-AT-SIZE at n 486 (p 0.45): event no (NOT-CERTIFIED), Brier 0.2025")
            if v == "MIXED":
                has(L, "P2 physics CERTIFIED-AT-SIZE at n 486 (p 0.45): event no (MIXED), Brier 0.2025")
        r, L, _o = run(sub(tmp, 8), spec=_ks("physics", 486, [14, 15, 15, 15, 15]))
        has(L, "  K2_physics_n486_d1   n 486 (added/ori 331/155): declared 0.286000; null p05 0.014000 / p50 0.149000 / p95 0.284000 "
               "/ max 0.299000; k_d  14 of 300, p_d 15/301 = 0.049834; C0 p95 0.000284 (comparable); reached 299; deflated k 0 (p95 "
               "0.142000) -> CERTIFIED")
        has(L, "  K2_physics_n486_d2   n 486 (added/ori 331/155): declared 0.285000; null p05 0.014000 / p50 0.149000 / p95 0.284000 "
               "/ max 0.299000; k_d  15 of 300, p_d 16/301 = 0.053156; C0 p95 0.000284 (comparable); reached 299; deflated k 0 (p95 "
               "0.142000) -> NOT CERTIFIED")

    def pk_levels(tmp):
        no = [100] * 5
        # 2 anchors certified -> K2-CERTIFIABLE; 1 -> MIXED; 0 -> K2-NOT with F-PK and its sentence
        sp1 = _ks("math", 486, no)
        r, L, _o = run(sub(tmp, 0), spec=sp1)
        assert r["pk"][486] == "K2-CERTIFIABLE" and r["fired"] is False, r["pk"]
        sp1.update(_ks("physics", 486, no))
        r, L, _o = run(sub(tmp, 1), spec=sp1)
        assert r["pk"] == {486: "MIXED", 441: "K2-CERTIFIABLE"} and r["fired"] is False, r["pk"]
        has(L, "PK1 (n 486): MIXED; anchors CERTIFIED-AT-SIZE 1, NOT-CERTIFIED 2, MIXED 0, NOT EVALUABLE 0 of 3 (PK-6)")
        has(L, "F-PK: NOT FIRED (PK1 MIXED). F-TAX N-1 and F2 stand.")
        has(L, "READING: none (PK1 MIXED: a registered MIXED; no sentence)")
        has(L, "P1 PK1 readings (K2-CERTIFIABLE 0.35, MIXED 0.30, K2-NOT 0.35): outcome MIXED, Brier (3-way sum) 0.7350")
        sp1.update(_ks("economics", 486, no))
        r, L, _o = run(sub(tmp, 2), spec=sp1)
        assert r["pk"] == {486: "K2-NOT", 441: "K2-CERTIFIABLE"} and r["fired"] is True, r["pk"]
        has(L, "PK1 (n 486): K2-NOT; anchors CERTIFIED-AT-SIZE 0, NOT-CERTIFIED 3, MIXED 0, NOT EVALUABLE 0 of 3 (PK-6)")
        has(L, SENT_FPK_FIRED)
        assert not any(l.startswith("READING") or l.startswith("F-PK: NOT FIRED") for l in L), L
        has(L, "P1 PK1 readings (K2-CERTIFIABLE 0.35, MIXED 0.30, K2-NOT 0.35): outcome K2-NOT, Brier (3-way sum) 0.6350")
        has(L, "P2 economics CERTIFIED-AT-SIZE at n 486 (p 0.40): event no (NOT-CERTIFIED), Brier 0.1600")
        # MIXED anchors count as not certified at PK level: 2 MIXED + 1 certified -> PK MIXED
        sp2 = _ks("math", 486, [14, 14, 14, 15, 15])
        sp2.update(_ks("physics", 486, [14, 14, 15, 15, 15]))
        r, L, _o = run(sub(tmp, 3), spec=sp2)
        assert r["pk"][486] == "MIXED", r["pk"]
        has(L, "PK1 (n 486): MIXED; anchors CERTIFIED-AT-SIZE 1, NOT-CERTIFIED 0, MIXED 2, NOT EVALUABLE 0 of 3 (PK-6)")
        # PK2 read from n 441 only: all n 441 NOT certified, n 486 all certified -> PK1 CERTIFIABLE, PK2 K2-NOT, F-PK not fired
        sp3 = {}
        for a in ANCHORS:
            sp3.update(_ks(a, 441, no))
        r, L, _o = run(sub(tmp, 4), spec=sp3)
        assert r["pk"] == {486: "K2-CERTIFIABLE", 441: "K2-NOT"} and r["fired"] is False, r["pk"]
        has(L, "PK2 (n 441): K2-NOT; anchors CERTIFIED-AT-SIZE 0, NOT-CERTIFIED 3, MIXED 0, NOT EVALUABLE 0 of 3 (PK-6)")
        # and the mirror: PK1 from n 486 only
        sp4 = {}
        for a in ANCHORS:
            sp4.update(_ks(a, 486, no))
        r, L, _o = run(sub(tmp, 5), spec=sp4)
        assert r["pk"] == {486: "K2-NOT", 441: "K2-CERTIFIABLE"} and r["fired"] is True, r["pk"]

    def gates(tmp):
        # one C0 failure + 4 certified -> CERTIFIED-AT-SIZE; P3 event no
        sp_ = _ks("math", 486, [0] * 5)
        sp_["K2_math_n486_d5"]["c0"] = "equal"
        r, L, _o = run(sub(tmp, 0), spec=sp_)
        assert r["anchors"][("math", 486)] == "CERTIFIED-AT-SIZE" and r["res"]["K2_math_n486_d5"]["status"] == "NOT EVALUABLE (C0)"
        has(L, "P3 C0 comparable on every subsample (p 0.85): event no (29 of 30 comparable), Brier 0.7225")
        # two C0 failures -> anchor NOT EVALUABLE although 3 certify; P2 math NOT SCORED; PK1 stays K2-CERTIFIABLE (2 others)
        sp_["K2_math_n486_d4"]["c0"] = "equal"
        r, L, _o = run(sub(tmp, 1), spec=sp_)
        assert r["anchors"][("math", 486)] == "NOT EVALUABLE" and r["pk"][486] == "K2-CERTIFIABLE", (r["anchors"], r["pk"])
        has(L, "ANCHOR math n 486: NOT EVALUABLE; certified 3, not certified 0, NOT EVALUABLE 2 (C0 2, degenerate / infeasible 0) "
               "of 5 (gate first: PK-5); median declared 0.300000 vs median null p95 0.284000")
        has(L, "P2 math CERTIFIED-AT-SIZE at n 486 (p 0.35): NOT SCORED (NOT EVALUABLE; PK-7)")
        has(L, "PK1 (n 486): K2-CERTIFIABLE; anchors CERTIFIED-AT-SIZE 2, NOT-CERTIFIED 0, MIXED 0, NOT EVALUABLE 1 of 3 (PK-6)")
        # gate precedes NOT-CERTIFIED: 2 C0 failures with 3 NOT CERTIFIED
        sp2 = _ks("math", 486, [100, 100, 100, 0, 0])
        sp2["K2_math_n486_d4"]["c0"] = sp2["K2_math_n486_d5"]["c0"] = "equal"
        r, L, _o = run(sub(tmp, 2), spec=sp2)
        assert r["anchors"][("math", 486)] == "NOT EVALUABLE", r["anchors"]
        # C0 one step below the null p95 is comparable; at equality it reaches
        r, L, _o = run(sub(tmp, 3), spec=_ks("math", 486, [0] * 5, c0="below"))
        assert all(r["res"]["K2_math_n486_d%d" % i]["comparable"] for i in DRAWS) and r["anchors"][("math", 486)] == "CERTIFIED-AT-SIZE"
        # DEGENERATE 19 / 20, and one degenerate + one C0 -> the anchor gate (Q-2)
        sp3 = _ks("physics", 441, [0] * 5)
        sp3["K2_physics_n441_d1"]["reached"] = 19
        r, L, _o = run(sub(tmp, 4), spec=sp3)
        assert r["res"]["K2_physics_n441_d1"]["status"] == "NOT EVALUABLE (DEGENERATE)" and r["anchors"][("physics", 441)] == "CERTIFIED-AT-SIZE"
        sp3["K2_physics_n441_d1"]["reached"] = 20
        r, L, _o = run(sub(tmp, 5), spec=sp3)
        assert r["res"]["K2_physics_n441_d1"]["status"] == "CERTIFIED", r["res"]["K2_physics_n441_d1"]
        sp3["K2_physics_n441_d1"]["reached"] = 5
        sp3["K2_physics_n441_d2"]["c0"] = "equal"
        r, L, _o = run(sub(tmp, 6), spec=sp3)
        has(L, "ANCHOR physics n 441: NOT EVALUABLE; certified 3, not certified 0, NOT EVALUABLE 2 (C0 1, degenerate / infeasible 1) "
               "of 5 (gate first: PK-5); median declared 0.300000 vs median null p95 0.284000")
        assert subsample_status(109, 0, True, 300) == "NOT EVALUABLE (NULL-INFEASIBLE)" and subsample_status(110, 0, True, 300) == "CERTIFIED"

    def pk_with_not_evaluable(tmp):
        ne = dict(c0="equal")
        # math NOT EVALUABLE, physics + economics NOT-CERTIFIED: c 0, e 1 -> K2-NOT vs MIXED -> NOT EVALUABLE; F-PK NOT fired
        sp_ = _ks("math", 486, [0] * 5, **ne)
        sp_.update(_ks("physics", 486, [100] * 5))
        sp_.update(_ks("economics", 486, [100] * 5))
        r, L, _o = run(sub(tmp, 0), spec=sp_)
        assert r["pk"][486] == "NOT EVALUABLE" and r["fired"] is False, r["pk"]
        has(L, "PK1 (n 486): NOT EVALUABLE; anchors CERTIFIED-AT-SIZE 0, NOT-CERTIFIED 2, MIXED 0, NOT EVALUABLE 1 of 3 (PK-6)")
        has(L, "F-PK: NOT FIRED (PK1 NOT EVALUABLE). F-TAX N-1 and F2 stand.")
        has(L, "READING: none (PK1 NOT EVALUABLE: not evaluable (PK-6); no sentence)")
        has(L, "P1 PK1 readings: NOT SCORED (PK1 NOT EVALUABLE; PK-7)")
        # c 1, e 1 -> MIXED vs CERTIFIABLE -> NOT EVALUABLE
        sp2 = _ks("math", 486, [0] * 5, **ne)
        sp2.update(_ks("physics", 486, [100] * 5))
        r, L, _o = run(sub(tmp, 1), spec=sp2)
        assert r["pk"][486] == "NOT EVALUABLE", r["pk"]
        # c 0, e 2 and c 0, e 3 -> NOT EVALUABLE
        sp3 = _ks("math", 486, [0] * 5, **ne)
        sp3.update(_ks("physics", 486, [0] * 5, **ne))
        sp3.update(_ks("economics", 486, [100] * 5))
        r, L, _o = run(sub(tmp, 2), spec=sp3)
        assert r["pk"][486] == "NOT EVALUABLE" and r["fired"] is False, r["pk"]
        assert [pk_verdict(w) for w in (["NOT EVALUABLE"] * 3, ["CERTIFIED-AT-SIZE", "CERTIFIED-AT-SIZE", "NOT EVALUABLE"],
                                        ["CERTIFIED-AT-SIZE", "NOT EVALUABLE", "NOT EVALUABLE"],
                                        ["MIXED", "NOT-CERTIFIED", "NOT-CERTIFIED"])] == \
            ["NOT EVALUABLE", "K2-CERTIFIABLE", "NOT EVALUABLE", "K2-NOT"]

    def identity(tmp):
        refused(sub(tmp, 0), "IDENTITY FAILED: declared 0.107804 k_d 0", ident_d=0.1078041)
        refused(sub(tmp, 1), "IDENTITY FAILED: declared 0.107803 k_d 1", ident_k=1)
        refused(sub(tmp, 2), "IDENTITY FAILED: declared 0.107803 k_d 0 n 6993 seed PS_x", ident_seed="PS_x")
        refused(sub(tmp, 3), "IDENTITY FAILED: declared 0.107803 k_d 0 n 6992 seed n00000001", ident_n=6992)
        refused(sub(tmp, 4), "IDENTITY FAILED: declared 0.107803 k_d 0 n 6993 seed n00000001 p95 0.041627 max 0.042414", ident_p95=0.041627)
        refused(sub(tmp, 5), "IDENTITY FAILED: declared 0.107803 k_d 0 n 6993 seed n00000001 p95 0.041626 max 0.042415", ident_max=0.042415)

    def refusals(tmp):
        for i, (needle, kw) in enumerate([
                ("the arm's status is 'REFUSED: x'", dict(status="REFUSED: x")),
                ("a partial file", dict(partial=True)),
                ("embeddings_cache.db changed during the arm", dict(hashes_equal=False)),
                ("the arm read site file sha256", dict(site_sha_bad=True)),
                ("instrument: the arm ran sepBar='0.025'", dict(sepbar="0.025")),
                ("instrument: the arm ran arm='certPcSize'", dict(arm="certPcSize")),
                ("the arm read snapshot 'OTHER'", dict(snapshot="OTHER")),
                ("sites.csv holds", dict(drop_site="K2_math_n441_d3")),
                ("sites.csv: K2_physics_n441_d2 n 442", dict(n_bad="K2_physics_n441_d2")),
                ("sites.csv: K2_math_n486_d4 n 486 groups 2 sizes 1/485", dict(gs_lie="K2_math_n486_d4")),
                ("K2_math_n486_d3: k_d recount 0 != the arm's 1", dict(k_lie="K2_math_n486_d3")),
                ("K2_economics_n441_d5: C0 p95 recount", dict(c0_lie="K2_economics_n441_d5")),
                ("replicates: K2_physics_n486_d2's C0 arm is missing", dict(drop_reps_arm=("K2_physics_n486_d2", "C0")))]):
            refused(sub(tmp, i), needle, **kw)
        # D-1 fixed: a site file other than the registered draw refuses, by the pin and by the rebuild (each alone)
        refused(sub(tmp, 20), "is not SITES_SHA256", tamper_site="K2_physics_n486_d3")
        refused(sub(tmp, 21), "the site file is not the registered draw rebuilt from the CPC labels", tamper_site="K2_physics_n486_d3",
                pins_override=lambda p: (p[0], sha256_bytes(open(os.path.join(tmp, "s21", "out", SITES_NAME), "rb").read())))
        refused(sub(tmp, 22), "not CERT-POSITIVE-CONTROL's label file of record", pins_override=lambda p: ("0" * 64, p[1]))

    def site_file(tmp):
        cat, src = _labels_fixture()
        assert len(cat) == N_ROOT and len(set(cat.values())) == 14
        data, sites, labels, pops = build_site_bytes(cat, src)
        assert list(sites) == ["IDENTITY"] + site_names() and len(sites["IDENTITY"]) == N_ROOT
        assert all(len(sites[s]) == parse_name(s)[1] for s in site_names())
        assert TWINS[0] not in set().union(*[set(sites[s]) for s in site_names()]), "the pinned twin was drawn"
        assert {a: (len(pops[a][FAM_ORI]), len(pops[a][FAM_ADD])) for a in ANCHORS} == REG_COUNTS
        assert all(set(sites[s]) <= set(pops[parse_name(s)[0]][FAM_ADD]) | set(pops[parse_name(s)[0]][FAM_ORI]) for s in site_names())
        # allocation (PCS-1): economics n 486 -> added 230 / ori 256 (the .5 tie to 'added' by name); math n 441 -> 173 / 268
        cnt = lambda s: (sum(1 for v in labels[s].values() if v == FAM_ADD), sum(1 for v in labels[s].values() if v == FAM_ORI))
        assert cnt("K2_economics_n486_d1") == (230, 256) and cnt("K2_math_n441_d1") == (173, 268) and \
            cnt("K2_physics_n486_d1") == (331, 155), (cnt("K2_economics_n486_d1"), cnt("K2_math_n441_d1"), cnt("K2_physics_n486_d1"))
        # IDENTITY rows are CERT-PC-SIZE's (same ids, same order, same categories)
        pdata, psites = PCS.build_site_bytes(cat)
        assert psites["IDENTITY"] == sites["IDENTITY"] and pdata.split(b"\nPS_")[0] == data.split(b"\nK2_")[0]
        assert sites["K2_math_n486_d1"] != sites["K2_math_n486_d2"] and sites["K2_math_n486_d1"] != sites["K2_physics_n486_d1"]
        d2, s2, _l2, _p2 = build_site_bytes(dict(cat), dict(src))
        assert d2 == data and s2 == sites, "the draw is not deterministic"
        assert sha256_bytes(data) == "e3b563caf92acd0f18c6c57918fdcbce354cf861dab66bb42c61e7561832ca86", sha256_bytes(data)
        # family rule and population refusals
        assert family("ori_mmlu-high_school_math") == FAM_ORI and family("theoremQA-Math") == FAM_ADD and family("stemez-Physics") == FAM_ADD
        for bad in ("ori-x", "mmlu-x", ""):
            try:
                family(bad)
                raise AssertionError("family %r accepted" % bad)
            except SystemExit as e:
                assert "neither ori_mmlu" in str(e), e
        try:
            populations(cat, src, twins=())
            raise AssertionError("the twin kept and accepted")
        except SystemExit as e:
            assert "math: ori_mmlu / added = 489 / 317, not the registered 489 / 316" in str(e), e
        try:
            build_site_bytes({q: ("c01" if c == "c00" else c) for q, c in cat.items()}, src)
            raise AssertionError("13 categories accepted")
        except SystemExit as e:
            assert "13 declared categories, not 14" in str(e), e
        # twins: found by stem key inside an anchor only, smallest id kept
        text = {q: "text %s" % q for q in cat}
        first_math_added = min(q for q in cat if cat[q] == "math" and src[q] == "scibench-stat" and q not in TWINS)
        assert first_math_added < TWINS[0]
        text[TWINS[0]] = text[first_math_added]             # the math twin pair -> keep the smaller id, drop TWINS[0]
        assert cat["q_00000"] == cat["q_00001"] == "economics"
        text["q_00001"] = text["q_00000"]                   # an economics twin pair -> keep q_00000, drop q_00001
        others = sorted(q for q in cat if cat[q] == "c01")[:2]
        text[others[1]] = text[others[0]]                   # outside the anchors: ignored
        nosrc = sorted(q for q in cat if cat[q] == "math" and not src[q])
        text[nosrc[0]] = text[first_math_added]             # a no-src id sharing the key: outside the anchor population, ignored
        got = find_twins(cat, src, text)
        assert got == sorted(["q_00001", TWINS[0]]), got
        assert find_twins(cat, src, {q: "text %s" % q for q in cat}) == [], "twins found where none are"

    def helpers(tmp):
        cfg = G.load_config(os.path.join(ROOT, PCS.CONFIG_REL))
        assert command(cfg, 6) == (
            '.\\gradlew.bat certPcK2 --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 '
            '"-DsnapshotId=20261001_094311_Headless_Run_Auto_ge" "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" '
            '"-DsiteLabels=experiment_results/cert_pc_k2/site_labels.tsv" "-DoutDir=experiment_results/cert_pc_k2/arm"'), command(cfg, 6)
        assert command(cfg, 8).endswith(' "-DsiteNullHeap=8g"')
        assert median([5, 1, 4, 2, 3]) == 3
        # the local rules equal CERT-PC-SIZE's (imported) on every count pattern of 5
        import itertools
        for combo in itertools.product(["CERTIFIED", "NOT CERTIFIED", "NOT EVALUABLE (C0)", "NOT EVALUABLE (DEGENERATE)"], repeat=5):
            mine, theirs = anchor_verdict(list(combo)), PCS.size_verdict(list(combo))
            assert mine == theirs.replace("NOT-CERTIFIED-AT-SIZE", "NOT-CERTIFIED"), (combo, mine, theirs)
        for n_, k_, c_, r_ in itertools.product((109, 110, 486), (0, 14, 15), (True, False), (19, 20)):
            assert subsample_status(n_, k_, c_, r_) == PCS.subsample_status(n_, k_, c_, r_)
        for fn_, arg in ((prepare, (tmp, "x")), (hashes, ("before", tmp))):
            try:
                fn_(*arg)
                raise AssertionError("%s from another data root not refused" % fn_.__name__)
            except SystemExit as e:
                assert tmp in str(e), e

    def main_analyze(tmp):
        global OUT_REL
        arm, outd, sp, lp, pins = _fx(tmp, spec=dict(list(_ks("math", 486, [100] * 5).items()) +
                                                     list(_ks("physics", 486, [100] * 5).items()) +
                                                     list(_ks("economics", 486, [14, 15, 15, 15, 15]).items())))
        os.replace(arm, os.path.join(outd, ARM_NAME))
        saved = OUT_REL
        OUT_REL = os.path.abspath(outd)
        try:
            with _pins(*pins):
                rc = main(["--analyze", "--cpc-labels", lp])
            if rc != 0:
                raise AssertionError("main --analyze returned %r" % rc)
        finally:
            OUT_REL = saved
        txt = open(os.path.join(outd, OUTCOME_NAME), encoding="utf-8").read()
        assert "\nPK1 (n 486): K2-NOT;" in txt and "\n" + SENT_FPK_FIRED + "\n" in txt and "\nPK2 (n 441): K2-CERTIFIABLE;" in txt, txt[-900:]

    def main_red_gate(tmp):
        global _IN_SELFTEST, selftest
        saved = (_IN_SELFTEST, selftest)
        _IN_SELFTEST, selftest = False, (lambda: 1)
        try:
            main(["--analyze", "--cpc-labels", os.path.join(tmp, "none.tsv")])
            raise AssertionError("main --analyze ran on a red selftest")
        except SystemExit as e:
            assert "the selftest is red: no readout" in str(e), e
        finally:
            _IN_SELFTEST, selftest = saved

    for nm, fn in [("main --analyze (the run-of-record wiring)", main_analyze),
                   ("main --analyze refuses on a red selftest", main_red_gate),
                   ("all CERTIFIED: every printed line, write-once", all_cert),
                   ("anchor boundaries 4 / 3 / 2 / 1 / 0 of 5; tie at k 14", anchor_boundaries),
                   ("PK levels: 2 / 1 / 0 anchors; MIXED anchors; PK1 486 only, PK2 441 only; F-PK", pk_levels),
                   ("gates: C0 1 / 2, precedence, equality, DEGENERATE 19 / 20, degenerate + C0", gates),
                   ("PK with NOT EVALUABLE anchors (PK-6)", pk_with_not_evaluable),
                   ("IDENTITY refusals (incl. PC1 p95 / max)", identity), ("refusals (incl. D-1 rebuild and pin)", refusals),
                   ("labels, populations, twins, allocation, site file", site_file), ("helpers", helpers)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


MUTANTS = [
    ("M0 control (no-op; must SURVIVE)", "TAG = \"[PK2]\"", "TAG = \"[PK2]\""),
    ("M1 k_d counts > (not >=)", "        k = CPC.kcount(R[(s, \"SN\")], d)", "        k = sum(1 for x in R[(s, \"SN\")] if x > d)"),
    ("M2 p = k/300", "    return \"CERTIFIED\" if bool(CPC.p_of(k) <= BAR) else \"NOT CERTIFIED\"",
     "    return \"CERTIFIED\" if bool(Fraction(k, 300) <= BAR) else \"NOT CERTIFIED\""),
    ("M3 anchor c >= 4 -> >= 3", "    if c >= 4:", "    if c >= 3:"),
    ("M4 anchor c <= 1 -> <= 2", "    if c <= 1:", "    if c <= 2:"),
    ("M5 anchor gate ne >= 2 -> >= 1", "    if ne >= 2:", "    if ne >= 1:"),
    ("M6 anchor gate after NOT-CERTIFIED", "    if ne >= 2:\n        return \"NOT EVALUABLE\"\n    if c >= 4:\n        return \"CERTIFIED-AT-SIZE\"\n    if c <= 1:\n        return \"NOT-CERTIFIED\"",
     "    if c >= 4:\n        return \"CERTIFIED-AT-SIZE\"\n    if c <= 1:\n        return \"NOT-CERTIFIED\"\n    if ne >= 2:\n        return \"NOT EVALUABLE\""),
    ("M7 PK c >= 2 -> >= 1", "    if c >= 2:\n        return \"K2-CERTIFIABLE\"", "    if c >= 1:\n        return \"K2-CERTIFIABLE\""),
    ("M8 PK c >= 2 -> >= 3", "    if c >= 2:\n        return \"K2-CERTIFIABLE\"", "    if c >= 3:\n        return \"K2-CERTIFIABLE\""),
    ("M9 PK K2-NOT iff c <= 1", "    if c == 0:\n        return \"K2-NOT\"", "    if c <= 1:\n        return \"K2-NOT\""),
    ("M10 PK counts MIXED anchors as certified", "    c = sum(1 for v in anchor_words if v == \"CERTIFIED-AT-SIZE\")",
     "    c = sum(1 for v in anchor_words if v in (\"CERTIFIED-AT-SIZE\", \"MIXED\"))"),
    ("M11 PK-6 ignores NOT EVALUABLE anchors", "    return lo if lo == hi else \"NOT EVALUABLE\"", "    return lo"),
    ("M12 PK-6 NOT EVALUABLE on any NE anchor", "    return lo if lo == hi else \"NOT EVALUABLE\"", "    return lo if e == 0 else \"NOT EVALUABLE\""),
    ("M13 PK1 from the n-441 verdict", "    pk1 = pk[486]", "    pk1 = pk[441]"),
    ("M14 PK read from the first anchor only", "        words = [av[(a, n)] for a in ANCHORS]", "        words = [av[(ANCHORS[0], n)] for a in ANCHORS]"),
    ("M15 anchor statuses from the first draw only", "            sts = [res[\"K2_%s_n%d_d%d\" % (a, n, dd)][\"status\"] for dd in DRAWS]",
     "            sts = [res[\"K2_%s_n%d_d%d\" % (a, n, 1)][\"status\"] for dd in DRAWS]"),
    ("M16 F-PK on MIXED too", "    if pk1 == \"K2-NOT\":\n        say(SENT_FPK_FIRED)", "    if pk1 in (\"K2-NOT\", \"MIXED\"):\n        say(SENT_FPK_FIRED)"),
    ("M17 CERT sentence on MIXED", "        if pk1 == \"K2-CERTIFIABLE\":\n            say(SENT_CERT)", "        if pk1 != \"K2-NOT\":\n            say(SENT_CERT)"),
    ("M18 P1 scored when NOT EVALUABLE", "    if pk1 in P1_PROBS:", "    if True:"),
    ("M19 P2 NOT EVALUABLE scored", "        if v != \"NOT EVALUABLE\":\n            e = bool(v == \"CERTIFIED-AT-SIZE\")", "        if True:\n            e = bool(v == \"CERTIFIED-AT-SIZE\")"),
    ("M20 P2 from n 441", "        v = av[(a, 486)]", "        v = av[(a, 441)]"),
    ("M21 P2 MIXED counted as an event", "            e = bool(v == \"CERTIFIED-AT-SIZE\")", "            e = bool(v in (\"CERTIFIED-AT-SIZE\", \"MIXED\"))"),
    ("M22 P3 over the n-486 subsamples only", "    allc = sum(1 for s in site_names() if res[s][\"comparable\"])\n    e3 = bool(allc == len(site_names()))",
     "    allc = sum(1 for s in site_names() if \"n486\" in s and res[s][\"comparable\"])\n    e3 = bool(allc == 15)"),
    ("M23 C0 reaches strict", "        comparable = not bool(c0p95 >= np95)", "        comparable = not bool(c0p95 > np95)"),
    ("M24 C0 not a precondition", "    if not comparable:\n        return \"NOT EVALUABLE (C0)\"", "    if False:\n        return \"NOT EVALUABLE (C0)\""),
    ("M25 degenerate check removed", "    if reached < DEGENERATE_MIN:", "    if False:"),
    ("M26 degenerate floor 20 -> 19", "REPS, MCS, DEGENERATE_MIN = 300, 55, 20", "REPS, MCS, DEGENERATE_MIN = 300, 55, 19"),
    ("M27 degenerate not counted toward the gate", "    ne = sum(1 for s in statuses if s.startswith(\"NOT EVALUABLE\"))",
     "    ne = sum(1 for s in statuses if s == \"NOT EVALUABLE (C0)\")"),
    ("M28 infeasible floor removed", "    if n < 2 * MCS:", "    if False:"),
    ("M29 k_d from the deflated arm", "        k = CPC.kcount(R[(s, \"SN\")], d)", "        k = CPC.kcount(R[(s, \"SND\")], d)"),
    ("M30 C0 p95 from the null", "        c0 = sorted(R[(s, \"C0\")])", "        c0 = sorted(R[(s, \"SN\")])"),
    ("M31 null p95 -> max", "        c0p95, np95 = CPC.pctl(c0, 0.95), CPC.pctl(sn, 0.95)", "        c0p95, np95 = CPC.pctl(c0, 0.95), sn[-1]"),
    ("M32 median -> min", "def median(xs):\n    s = sorted(xs)\n    return s[len(s) // 2]", "def median(xs):\n    s = sorted(xs)\n    return s[0]"),
    ("M33 IDENTITY gate removed", "    if not (\"%.6f\" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K", "    if False and not (\"%.6f\" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K"),
    ("M34 IDENTITY p95 / max not checked (D-2)", "\n            and p95_0 == PC1_P95 and max_0 == PC1_MAX):", "):"),
    # M35: k alone is EQUIVALENT under the D-2 max check (k_d >= 1 implies max >= 0.107803 != 0.042414), so k and max go together
    ("M35 IDENTITY k and max not checked",
     "IDENTITY_DECLARED and k0 == IDENTITY_K and int(ir[\"n\"]) == N_ROOT and ir[\"null_seed_id\"] == ROOT_ID\n            and p95_0 == PC1_P95 and max_0 == PC1_MAX):",
     "IDENTITY_DECLARED and int(ir[\"n\"]) == N_ROOT and ir[\"null_seed_id\"] == ROOT_ID\n            and p95_0 == PC1_P95):"),
    ("M36 IDENTITY seed not checked", " and ir[\"null_seed_id\"] == ROOT_ID\n", "\n"),
    ("M37 site pin not checked (D-1)", "    if s_sha != SITES_SHA256:", "    if False:"),
    ("M38 site rebuild not checked (D-1)", "    if rebuilt != sbytes:", "    if False:"),
    ("M39 arm-read sha not checked", "    if st.get(\"sites_sha256\") != s_sha:", "    if False:"),
    ("M40 hash check removed", "    if json.load(open(hb)) != json.load(open(ha)):", "    if False:"),
    ("M41 write-once pre-check removed", "        if os.path.exists(p):\n            refuse(\"%s exists: the outcome is write-once\" % p)",
     "        if False:\n            refuse(\"%s exists: the outcome is write-once\" % p)"),
    ("M42 partial replicates accepted", "        if [i for i, _x in xs] != list(range(REPS)):", "        if False:"),
    ("M43 instrument check removed", "        if st.get(k) != v:\n            refuse(\"instrument", "        if False:\n            refuse(\"instrument"),
    ("M44 snapshot check removed", "    if st.get(\"snapshot\") != SNAPSHOT:", "    if False:"),
    ("M45 sites.csv set check removed", "    if list(rows) != want:", "    if False:"),
    ("M46 k recount check removed", "        if k != int(r[\"k_declared\"]):", "        if False:"),
    ("M47 C0 recount check removed", "        if c0p95 != float(r[\"c0_p95\"]):", "        if False:"),
    ("M48 group sizes not checked", " or int(r[\"groups\"]) != 2 or r[\"group_sizes\"] != gs:", " or int(r[\"groups\"]) != 2:"),
    ("M49 missing arm not checked", "            if (s, a_) not in R:", "            if False:"),
    ("M50 twins not dropped", "            if cat[q] == a and src[q] and q not in tw:", "            if cat[q] == a and src[q]:"),
    ("M51 twin keeps the largest id", "            drop.extend(v[1:])", "            drop.extend(v[:-1])"),
    ("M52 registered counts not checked", "        if got != reg[a]:", "        if False:"),
    ("M53 family: theoremQA not added", "ADDED_PREFIXES = (\"stemez-\", \"theoremQA-\", \"scibench-\")", "ADDED_PREFIXES = (\"stemez-\", \"scibench-\")"),
    ("M54 unknown src accepted as added", "    refuse(\"src %r is neither ori_mmlu-* nor an added source (stemez / theoremQA / scibench)\" % s)", "    return FAM_ADD"),
    ("M55 draw seed shifted (d + 1)", "                sites[s] = PCS.draw(pops[a], n, d)", "                sites[s] = PCS.draw(pops[a], n, d + 1)"),
    ("M56 no-src ids enter the anchor", "            if cat[q] == a and src[q] and q not in tw:", "            if cat[q] == a and q not in tw:"),
    ("M57 overlap: draws compared with themselves", "for x in DRAWS for y in DRAWS if x < y]", "for x in DRAWS for y in DRAWS if x <= y]"),
    ("M58 economics overlap disclosure dropped", "if 486 > 0.9 * N else \"\"))", "if False else \"\"))"),
    ("M59 labels sha not checked", "    if sha256_bytes(b) != sha:", "    if False:"),
    ("M60 selftest gate in main removed", "    if not _IN_SELFTEST and selftest() != 0:", "    if False:"),
]


def mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    t0 = src.index("\nMUTANTS = [\n")
    t1 = src.index("\n]\n", t0) + 3
    head, table, tail = src[:t0], src[t0:t1], src[t1:]        # never mutate the table's own text (a pattern may sit there first)
    rows = []
    for name, old, new in MUTANTS:
        if old in head:
            mut = head.replace(old, new, 1) + table + tail
        elif old in tail:
            mut = head + table + tail.replace(old, new, 1)
        else:
            rows.append((name, "NOT APPLIED (pattern absent)"))
            continue
        tmp = os.path.join(HERE, "_pk2_mutant_%d.py" % os.getpid())
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(mut)
            r = subprocess.run([sys.executable, tmp, "--selftest"], capture_output=True, text=True, timeout=1800)
            rows.append((name, "KILLED" if r.returncode != 0 else "SURVIVED"))
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    for n, v in rows:
        print("  %-60s %s" % (n, v))
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
    ap.add_argument("--cpc-labels", default=None)
    a = ap.parse_args(argv)
    cpc_labels = a.cpc_labels or os.path.join(a.data_root, CPC_LABELS_REL)
    if a.selftest:
        return selftest()
    if a.mutants:
        return mutants()
    if a.dry_run:
        dry_run(a.data_root, cpc_labels)
        return 0
    if a.prepare:
        prepare(a.data_root, cpc_labels)
        return 0
    if a.hashes:
        hashes(a.hashes, a.data_root)
        return 0
    if not _IN_SELFTEST and selftest() != 0:
        refuse("the selftest is red: no readout")
    d = os.path.join(ROOT, OUT_REL)
    analyze(os.path.join(d, ARM_NAME), d, os.path.join(d, SITES_NAME), cpc_labels)
    return 0


if __name__ == "__main__":
    sys.exit(main())
