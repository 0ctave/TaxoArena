"""cert_pc_size.py: CERT-PC-SIZE, the subsample site file, the dry-run, the launch command and the READOUT of the subsampled
declared-site arm (SeparationNullBySizeTest `certPcSize - ...`, gradle task certPcSize). ZERO calls.

REGISTRATION OF RECORD (it governs; this docstring restates it and never replaces it): docs/judge_v2_program.md
"## Registered 2026-10-03 (before any code or call) — CERT-PC-SIZE: does the site-null certificate still certify the declared
14-category MMLU-Pro partition when the site is subsampled to G12's depth-1 site sizes (median 486, 25th percentile 441), where
the tree's own splits got 0 of 60? (zero calls; no construction; site-null runs, CPU)" (span L23722-L23750 as registered,
commit 02256ca6); record docs/agents/results/CERT-PC-SIZE.json.
  IDENTITY (precondition, refuse): the full-size root reproduces 0.107803 and k_d 0.
  SIZES n 486 (PS1, DECIDING), 441 (PS2, deciding), 264 (DESCRIPTIVE); per size 5 stratified subsamples (proportional
  allocation over the 14 groups, largest remainders; draw seeds 1-5); each subsample a site: the declared statistic, its own
  plain site null (300 reps) and C0 (300 random size-matched relabellings).
  A subsample is CERTIFIED iff k_d <= 14 (p_d = (k_d + 1) / 301 <= 0.05) with C0 comparable (relabelling p95 below the null
  p95); a C0 failure makes it NOT EVALUABLE; (g) a DEGENERATE null (< 20 replicates reach the gate) or n < 2 x mcs makes it
  NOT EVALUABLE.
  PS1 / PS2: CERTIFIED-AT-SIZE iff >= 4 of 5 CERTIFIED; NOT-CERTIFIED-AT-SIZE iff <= 1; MIXED otherwise (a registered
  UNDETERMINED); NOT EVALUABLE if 2 or more subsamples fail C0.
  P1 PS1 CERTIFIED-AT-SIZE 0.55 / MIXED 0.20 / NOT-CERTIFIED-AT-SIZE 0.25; P2 PS2 CERTIFIED-AT-SIZE 0.50; P3 the n 486 median
  declared statistic 0.11 [0.09, 0.14], null p95 0.07 [0.05, 0.10]; P4 C0 comparable on every subsample 0.85.
  F-PS fires iff PS1 reads NOT-CERTIFIED-AT-SIZE.

INSTRUMENT. The certPositiveControl arm's members, reused unchanged (declaredSiteStatistic, cpcSiteArm via cpcDeclaredSite,
cpcRelabelNull, cpcSeed; READY aac3f7fc + delta, merged 218f9b7f) driven by a NEW method certPcSize (additions only; javap proof
in the commit message). Population and labels: CERT-POSITIVE-CONTROL's label file of record (declared_labels.tsv, sha256
c0a20662..., 6,993 TRAIN items of the B0/mmlu_pro_lb member root, snapshot 20261001_094311_Headless_Run_Auto_ge), pinned by its
sha256 and checked against the snapshot's root region; config experiment_configs/rp12_r2/B0/g12_site_null.sitenull (slice 512,
sepBar 0.0145, dropTop 0, whiten false, 300 reps, 12 threads). cert_positive_control.py blob e0751d7c is IMPORTED (pctl, kcount,
p_of, member, region_ids, heavy_check), never copied; its own imports pin g12_site_null.py and cert_resolution.py.

LAUNCH SEQUENCE (run-operator; a site null = a rule-7 heavy process: W1-W5, 12 JVM threads, never beside a construction,
another site null or a pool reader; the pool check in the B0-2 form first; run from the data root's checkout, e.g. the
rp12-r2-run worktree after merging this branch there; nothing here is committed from the run):
  python tools/analysis/cert_pc_size.py --selftest
  python tools/analysis/cert_pc_size.py --mutants
  python tools/analysis/v2_union_pool.py --dry-run                     (rc 0; pool file sha256-lf16 79d48f4b36434a55)
  python tools/analysis/cert_pc_size.py --dry-run  [--data-root DIR] [--cpc-labels FILE]   population, allocations, site
                                                     file sha, G12 sizes beside, heap, wall bound, COMMAND; writes nothing
  python tools/analysis/cert_pc_size.py --prepare  [--cpc-labels FILE]   writes experiment_results/cert_pc_size/site_labels.tsv (x)
  python tools/analysis/cert_pc_size.py --hashes before
  <the printed COMMAND: .\\gradlew.bat certPcSize ...>   then  .\\gradlew.bat --stop
  python tools/analysis/cert_pc_size.py --hashes after
  python tools/analysis/cert_pc_size.py --analyze     outcome (write-once, mode x): experiment_results/cert_pc_size/outcome.txt
        and pcs_sites.csv; refuses a REFUSED / partial arm, a hash change, an IDENTITY failure, a site file other than the one
        the arm read, an instrument or snapshot other than the registered, a missing / extra / wrong-size subsample.
  --cpc-labels default: <data root>/experiment_results/cert_positive_control/declared_labels.tsv (the CPC run's file; any copy
  with the pinned sha256 is the same file).
Outputs are NEVER committed: pin them by sha256 and back them up to E:/TaxoArena_backup_<date>_<tag> with SHA256SUMS.txt.

BUILDER'S READINGS (each flagged to the registrar; printed in the outcome header):
  PCS-1 allocation: quota_g = floor(n x N_g / N) plus one for the (n - sum floor) groups with the largest remainders, ties by
        category name ascending; the draw: random.Random(seed) once per (size, seed), categories in sorted order, each group's
        quota by rng.sample over its ids sorted ascending. The site file lists the subsamples in size order 486, 441, 264, draw
        1..5, each site's rows sorted by query id; the first site IDENTITY is the full root (6,993 rows).
  PCS-2 the arm takes each site's population in the ROOT REGION's order and builds the groups as PC1's (sorted categories), so
        IDENTITY is PC1's site element for element (its plain null seeded by the root id n00000001, i.e. PC1's replicates).
  PCS-3 per-subsample seeds: plain null siteNull's formula on base 20260908 with the site NAME (PS_n486_d1 ...); deflated null
        base 88820260908 likewise (DESCRIPTIVE, the "deflated null beside"); C0 = siteNull's formula on base 20261002 (CPC's C0
        seed) with the site name, rep 0. Not fixed by the registration; fixed here before any run.
  PCS-4 C0 "comparable" = C0 p95 < the plain null p95 (CPC CR-3: "reaches" = >=; Kotlin percentile rank ceil(0.95 x 300)).
  PCS-5 PRECEDENCE (registration query Q-1 to the registrar): the size-level NOT EVALUABLE gate (2 or more subsamples NOT
        EVALUABLE) is tested FIRST, before CERTIFIED / NOT-CERTIFIED / MIXED; as registered, 2 C0 failures with <= 1 certified
        would satisfy both "NOT EVALUABLE" and "NOT-CERTIFIED-AT-SIZE" (or MIXED with 2-3 certified). Gate-first is CPC's
        CR-3 precedent (C0 failure -> NOT EVALUABLE whatever p_d). Q-2: a DEGENERATE / NULL-INFEASIBLE subsample (g) counts
        toward that gate like a C0 failure (both make the subsample NOT EVALUABLE); both counts are printed.
  PCS-6 P1 / P2 are scored only when their size is evaluable (NOT EVALUABLE is not among P1's three readings): "NOT SCORED"
        otherwise; P1 by the three-way Brier sum, P2 and P4 binary Brier. P3 medians over the 5 n-486 subsamples (the 3rd of 5
        sorted values), all five whatever their status; P4 over all 15 subsamples.
  PCS-7 the n-264 subsamples are DESCRIPTIVE: their per-subsample status and counts are printed, no size verdict word.

SELFTEST (python tools/analysis/cert_pc_size.py --selftest): every registered branch through the real entry points
(analyze(), main(["--analyze"]), build_site_bytes(), allocate()) on fixtures whose answer is known by hand, asserting the printed
VALUE: PS1 CERTIFIED-AT-SIZE at 4 of 5 (k_d 14 boundary, tie counts), MIXED at 3 and 2, NOT-CERTIFIED-AT-SIZE at 1 and 0 with
F-PS FIRED and its sentence; NOT EVALUABLE at 2 C0 failures (also with the rest NOT CERTIFIED: precedence) and at 1 C0 + 1
DEGENERATE; 1 C0 failure + 4 certified stays CERTIFIED; C0 at equality fails; reached 19 / 20; PS2 read from the n-441 rows
only, PS1 from n-486 only, n 264 never decides; P1 / P2 / P3 / P4 values and NOT SCORED; IDENTITY refusals (0.107804, k 1);
every refusal (status, partial, hashes, site sha, instrument, snapshot, missing / extra / wrong-size site, k and C0 recount);
write-once. MUTANTS: --mutants runs the table MUTANTS below against --selftest (temporary copies); table in the commit message.
"""
import argparse
import contextlib
import csv
import hashlib
import io
import json
import math
import os
import random
import subprocess
import sys
import tempfile
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from data_v2 import ro as RO  # noqa: E402

TAG = "[PCS]"
_IN_SELFTEST = False
CPC_BLOB = "e0751d7c6fe50b0a588cbb1160eee0b3e99ce8a1"


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _import_pinned(name, blob):
    got = RO.git_blob_lf(os.path.join(HERE, name + ".py"))
    if got != blob:
        refuse("%s.py is blob %s, not the pinned %s (imported, never copied)" % (name, got, blob))
    return __import__(name)


CPC = _import_pinned("cert_positive_control", CPC_BLOB)
G = CPC.G

CONFIG_REL = CPC.CONFIG_REL
G12_SITES_REL = CPC.G12_SITES_REL
OUT_REL = "experiment_results/cert_pc_size"
CPC_LABELS_REL = "experiment_results/cert_positive_control/declared_labels.tsv"
CPC_LABELS_SHA = "c0a20662047c6314ee57e64f5537e66525af3471b818607a88cb4afdfe2b3aef"
SITES_NAME, ARM_NAME, OUTCOME_NAME, CSV_NAME = "site_labels.tsv", "arm", "outcome.txt", "pcs_sites.csv"
SITE_HEADER = "site\tquery_id\tcategory"
SNAPSHOT = "20261001_094311_Headless_Run_Auto_ge"
ROOT_ID, N_ROOT = "n00000001", 6993
SIZES = (486, 441, 264)
DECIDING = {486: "PS1", 441: "PS2"}
DRAWS = (1, 2, 3, 4, 5)
REPS, N_CATS, MCS, DEGENERATE_MIN = 300, 14, 55, 20
BAR = Fraction(1, 20)
K_MAX = 14
IDENTITY_DECLARED, IDENTITY_K = "0.107803", 0
PC1_P95, PC1_MAX = "0.041626", "0.042414"
INSTRUMENT = {"reps": "300", "sliceDim": "512", "sepBar": "0.0145", "dropTop": "0", "whiten": "false", "minClusterSize": "55",
              "c0Seed": "20261002"}
P1_PROBS = {"CERTIFIED-AT-SIZE": 0.55, "MIXED": 0.20, "NOT-CERTIFIED-AT-SIZE": 0.25}
P2_P = 0.50
P3_D, P3_D_LO, P3_D_HI = 0.11, 0.09, 0.14
P3_N, P3_N_LO, P3_N_HI = 0.07, 0.05, 0.10
P4_P = 0.85
CPC_WALL_MIN = 24.2     # CPC arm: identity.csv 10:42:11 -> replicates.csv 11:06:23 (14 anchors both arms + root both arms + C0)
REG = ('docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — CERT-PC-SIZE: ..." L23722-L23750 '
       '(as registered, 02256ca6)')

SENT_FPS_FIRED = ("F-PS: FIRED (PS1 NOT-CERTIFIED-AT-SIZE): the certificate cannot certify the declared level at G12's depth-1 "
                  "site sizes, so G12's 0 of 60 at depth 1 IS read as a sensitivity limit at those sizes "
                  "(CERT-POSITIVE-CONTROL's root-scale result stands). F-TAX N-1 and F2 stand.")
SENT_CERT = ("READING (PS1 CERTIFIED-AT-SIZE): N-1's empty set reads 'the tree's data-driven depth-1 splits are less separated "
             "than the declared level at the same n' (size-matched to G12, NOT k-matched: 14 vs 2-3 groups; NOT "
             "population-matched: all categories vs one anchor)")
LIKE = ["LIKE WITH LIKE: | site | partition | k | n | population |",
        "  | PC1 (of record) | declared labels | 14 | 6,993 | member root |",
        "  | PS subsamples (this test) | declared labels, stratified | 14 | 486 / 441 / 264 | member root, subsampled |",
        "  | G12 TOP sites (of record) | data-driven splits inside one anchor | 2-3 | 264-778 | one declared anchor |",
        "  size-matched to G12, NOT k-matched (14 vs 2-3) nor population-matched (all categories vs one anchor); C0 guards the "
        "statistic's k-comparability per subsample"]
DOES_NOT_SHOW = ("DOES NOT SHOW: a certificate of any tree site; power for 2-3-way splits (k not matched) or within one anchor "
                 "(population not matched); other members, draws, slices or recipes; that the categories are geometric "
                 "clusters; a mode test (MIX-LRT-SITE closed)")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def site_names():
    return ["PS_n%d_d%d" % (n, d) for n in SIZES for d in DRAWS]


# ------------------------------------------------------------------------------------------------ allocation and the site file
def allocate(counts, n):
    """PCS-1: proportional allocation of n over the groups, largest remainders, ties by name ascending -> {cat: quota}."""
    tot = sum(counts.values())
    exact = {c: Fraction(n * m, tot) for c, m in counts.items()}
    q = {c: int(math.floor(v)) for c, v in exact.items()}
    left = n - sum(q.values())
    for c in sorted(counts, key=lambda c: (-(exact[c] - q[c]), c))[:left]:
        q[c] += 1
    return q


def draw(by_cat, n, seed):
    """PCS-1: one stratified subsample -> sorted ids."""
    q = allocate({c: len(v) for c, v in by_cat.items()}, n)
    rng = random.Random(seed)
    sel = []
    for c in sorted(by_cat):
        sel.extend(rng.sample(sorted(by_cat[c]), q[c]))
    return sorted(sel)


def read_cpc_labels(path, sha=CPC_LABELS_SHA):
    if not os.path.isfile(path):
        refuse("CERT-POSITIVE-CONTROL's label file %s not found (--cpc-labels)" % path)
    b = open(path, "rb").read()
    got = sha256_bytes(b)
    if got != sha:
        refuse("%s is sha256 %s, not CERT-POSITIVE-CONTROL's label file of record %s" % (path, got, sha))
    lines = b.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if not lines or lines[0] != CPC.LABEL_HEADER:
        refuse("the CPC label file's header is not %r" % CPC.LABEL_HEADER)
    cat = {}
    for ln in lines[1:]:
        p = ln.split("\t")
        if len(p) != 3 or not p[0] or not p[1] or p[0] in cat:
            refuse("malformed or duplicate CPC label row %r" % ln)
        cat[p[0]] = p[1]
    return cat


def build_site_bytes(cat):
    """-> (bytes, {site: sorted ids}); IDENTITY first, then SIZES x DRAWS."""
    by_cat = {}
    for q, c in cat.items():
        by_cat.setdefault(c, []).append(q)
    if len(by_cat) != N_CATS:
        refuse("%d declared categories, not the registered %d" % (len(by_cat), N_CATS))
    sites = {"IDENTITY": sorted(cat)}
    for n in SIZES:
        for d in DRAWS:
            sites["PS_n%d_d%d" % (n, d)] = draw(by_cat, n, d)
    rows = [SITE_HEADER]
    for s, ids in sites.items():
        rows.extend("%s\t%s\t%s" % (s, q, cat[q]) for q in ids)
    return ("\n".join(rows) + "\n").encode("utf-8"), sites


def parse_site_file(path):
    sites = {}
    lines = open(path, encoding="utf-8").read().split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if not lines or lines[0] != SITE_HEADER:
        refuse("%s: header is not %r" % (path, SITE_HEADER))
    for ln in lines[1:]:
        p = ln.split("\t")
        if len(p) != 3:
            refuse("%s: malformed row %r" % (path, ln))
        sites.setdefault(p[0], {})[p[1]] = p[2]
    return sites


# ------------------------------------------------------------------------------------------------ dry-run / prepare / hashes
def assemble(data_root, cpc_labels):
    cfg = G.load_config(os.path.join(ROOT, CONFIG_REL))
    G.lane_check("r2", os.path.join(ROOT, CONFIG_REL), cfg)
    sid, graph, byid, root = CPC.member(cfg, data_root)
    if sid != SNAPSHOT:
        refuse("the member's snapshot is %s, not CERT-POSITIVE-CONTROL's %s" % (sid, SNAPSHOT))
    if root["id"] != ROOT_ID:
        refuse("the member root is %s, not %s" % (root["id"], ROOT_ID))
    ids = CPC.region_ids(byid, root["id"])
    cat = read_cpc_labels(cpc_labels)
    if set(cat) != set(ids) or len(ids) != N_ROOT:
        refuse("the CPC labels cover %d ids, the member root region %d (want both %d, sets equal)" % (len(cat), len(ids), N_ROOT))
    data, sites = build_site_bytes(cat)
    return cfg, sid, root, cat, data, sites


def command(cfg, heap):
    return ('.\\gradlew.bat certPcSize --console=plain --offline --no-daemon -PjvmThreads=%d -PnullReps=%d '
            '"-DsnapshotId=%s" "-DsliceDim=%d" "-DsepBar=%s" "-DdropTop=%d" "-Dwhiten=%s" "-DsiteLabels=%s/%s" "-DoutDir=%s/%s"%s'
            % (cfg["jvmThreads"], cfg["nullReps"], SNAPSHOT, cfg["sliceDim"], repr(cfg["sepBar"]), cfg["dropTop"],
               str(cfg["whiten"]).lower(), OUT_REL, SITES_NAME, OUT_REL, ARM_NAME,
               "" if heap <= G.DEFAULT_HEAP_GB else ' "-DsiteNullHeap=%dg"' % heap))


def wall_bound():
    """Upper bound: CPC's 24.2 min covered 14 anchors (n 264-778, both arms) + the root (both arms) + C0; this arm runs the
    root's plain arm only + 15 subsamples (sum n^2 at both arms well below the anchors')."""
    sub = 2 * sum(n * n for n in SIZES) * len(DRAWS)
    return CPC_WALL_MIN, sub


def dry_run(data_root, cpc_labels, out=print):
    out("pool: the B0-2 check is the operator's (v2_union_pool.py --dry-run); this mode opens no pool table")
    out("%s DRY RUN: zero calls, nothing written, no null replicate, no verdict" % TAG)
    CPC.heavy_check()
    cfg, sid, root, cat, data, sites = assemble(data_root, cpc_labels)
    out("%s member B0/mmlu_pro_lb = snapshot %s; root %s '%s' n = %d (TRAIN); CPC labels %s sha256 %s (= the pin)"
        % (TAG, sid, root["id"], root.get("label"), len(cat), cpc_labels, CPC_LABELS_SHA[:16]))
    counts = {}
    for c in cat.values():
        counts[c] = counts.get(c, 0) + 1
    out("%s the 14 declared groups (N_g): %s" % (TAG, ", ".join("%s %d" % (c, counts[c]) for c in sorted(counts))))
    for n in SIZES:
        q = allocate(counts, n)
        out("%s n %d (%s) allocation (PCS-1): %s; min group %d" % (TAG, n, DECIDING.get(n, "DESCRIPTIVE"),
            " ".join(str(q[c]) for c in sorted(q)), min(q.values())))
    for n in SIZES:
        ov = [len(set(sites["PS_n%d_d%d" % (n, a)]) & set(sites["PS_n%d_d%d" % (n, b)])) for a in DRAWS for b in DRAWS if a < b]
        out("%s n %d: 5 draws, pairwise overlaps min %d / max %d items" % (TAG, n, min(ov), max(ov)))
    g12 = sorted(int(r["n"]) for r in csv.DictReader(open(os.path.join(ROOT, G12_SITES_REL), encoding="utf-8"))
                 if r["family_key"] == "TOP")
    out("%s G12 TOP-site n (beside; the sizes were fixed by the registration): %s" % (TAG, g12))
    sp = os.path.join(ROOT, OUT_REL, SITES_NAME)
    out("%s site file %s/%s: %d sites, %d rows, sha256 %s (%s)" % (TAG, OUT_REL, SITES_NAME, len(sites), data.count(b"\n") - 1,
        sha256_bytes(data), "present, IDENTICAL" if os.path.exists(sp) and open(sp, "rb").read() == data else
        ("present, DIFFERENT" if os.path.exists(sp) else "absent: --prepare writes it")))
    need, live, heap = G.heap_estimate(N_ROOT, cfg["sliceDim"], cfg["nullReps"], cfg["jvmThreads"])
    out("%s heap (g12_site_null's rule, the IDENTITY site n %d): live %d, peak %.2f GB -> %s" % (
        TAG, N_ROOT, live, need, "fits the 6g default" if heap <= G.DEFAULT_HEAP_GB else "-DsiteNullHeap=%dg" % heap))
    wb, sub = wall_bound()
    out("%s wall: under about %.0f min at %d threads (bound: CPC's arm, 14 anchors + root at both arms + C0, took %.1f min; this "
        "arm runs the root's plain arm + 15 subsamples, sum n^2 x 2 arms = %d)" % (TAG, wb, cfg["jvmThreads"], wb, sub))
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
    return dict(sha=sha256_bytes(data), heap=heap, sites=len(sites))


def prepare(data_root, cpc_labels):
    if not CPC.same_checkout(data_root):
        refuse("--prepare writes the site file into this checkout; the arm reads it from the data root's: run from %s" % data_root)
    CPC.heavy_check()
    _cfg, _sid, _root, _cat, data, sites = assemble(data_root, cpc_labels)
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


def size_verdict(statuses):
    ne = sum(1 for s in statuses if s.startswith("NOT EVALUABLE"))
    c = sum(1 for s in statuses if s == "CERTIFIED")
    if ne >= 2:
        return "NOT EVALUABLE"
    if c >= 4:
        return "CERTIFIED-AT-SIZE"
    if c <= 1:
        return "NOT-CERTIFIED-AT-SIZE"
    return "MIXED"


def median5(xs):
    s = sorted(xs)
    return s[len(s) // 2]


def analyze(arm_dir, out_dir, sites_path, out=print):
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
    s_sha = sha256_bytes(open(sites_path, "rb").read())
    if st.get("sites_sha256") != s_sha:
        refuse("the arm read site file sha256 %s; %s is %s" % (st.get("sites_sha256"), sites_path, s_sha))
    hb, ha = (os.path.join(out_dir, "emb_hashes_%s.json" % x) for x in ("before", "after"))
    if not (os.path.isfile(hb) and os.path.isfile(ha)):
        refuse("the embeddings_cache.db hashes before and after the arm are owed (--hashes before / after)")
    if json.load(open(hb)) != json.load(open(ha)):
        refuse("embeddings_cache.db changed during the arm (per-table hashes differ)")
    sfile = parse_site_file(sites_path)
    want = ["IDENTITY"] + site_names()
    if list(sfile) != want:
        refuse("the site file lists %s, not IDENTITY + the 15 registered subsamples in order" % list(sfile)[:20])
    for s in site_names():
        n = int(s.split("_")[1][1:])
        if len(sfile[s]) != n or len(set(sfile[s].values())) != N_CATS:
            refuse("site file: %s holds %d items in %d categories (want %d in %d)" % (s, len(sfile[s]), len(set(sfile[s].values())), n, N_CATS))
    if len(sfile["IDENTITY"]) != N_ROOT:
        refuse("site file: IDENTITY holds %d items, not %d" % (len(sfile["IDENTITY"]), N_ROOT))
    say("%s CERT-PC-SIZE outcome (tools/analysis/cert_pc_size.py blob %s; cert_positive_control.py blob %s imported). Zero calls."
        % (TAG, RO.git_blob_lf(os.path.abspath(__file__)), CPC_BLOB))
    say("registration: " + REG)
    say("arm: snapshot %s; site file sha256 %s; reps %s; sliceDim %s; sepBar %s; dropTop %s; whiten %s; minClusterSize %s; C0 "
        "seed base %s; threads %s; embeddings_cache.db per-table hashes before == after" % (
            st["snapshot"], s_sha, st["reps"], st["sliceDim"], st["sepBar"], st["dropTop"], st["whiten"], st["minClusterSize"],
            st["c0Seed"], st.get("threads")))
    say("builder's readings PCS-1..PCS-7 (docstring); registration queries Q-1 (gate precedence) and Q-2 (degenerate counts toward "
        "the gate) to the registrar")

    with open(os.path.join(arm_dir, "sites.csv"), newline="", encoding="utf-8") as f:
        rows = {r["site_id"]: r for r in csv.DictReader(f)}
    if list(rows) != want:
        refuse("sites.csv holds %s, not IDENTITY + the 15 registered subsamples in order" % list(rows)[:20])
    reps = {}
    with open(os.path.join(arm_dir, "replicates.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            reps.setdefault((r["site_id"], r["arm"]), []).append((int(r["rep"]), float(r["stat"])))
    for key, xs in reps.items():
        if [i for i, _x in xs] != list(range(REPS)):
            refuse("replicates %s: reps %d, not 0..%d in order (a partial file)" % (key, len(xs), REPS - 1))
    R = {k: [x for _i, x in v] for k, v in reps.items()}
    for s in want:
        for a in (("SN",) if s == "IDENTITY" else ("SN", "SND", "C0")):
            if (s, a) not in R:
                refuse("replicates: %s's %s arm is missing" % (s, a))

    # IDENTITY
    ir = rows["IDENTITY"]
    d0 = float(ir["declared_stat"])
    k0 = CPC.kcount(R[("IDENTITY", "SN")], d0)
    sn0 = sorted(R[("IDENTITY", "SN")])
    say("IDENTITY: full-size root n %s, declared %.6f (registered %s), k_d %d of %d (registered %d); null seeded by %s; null p95 "
        "%.6f / max %.6f (PC1 of record %s / %s: %s)" % (ir["n"], d0, IDENTITY_DECLARED, k0, REPS, IDENTITY_K, ir["null_seed_id"],
            CPC.pctl(sn0, 0.95), sn0[-1], PC1_P95, PC1_MAX,
            "equal" if ("%.6f" % CPC.pctl(sn0, 0.95), "%.6f" % sn0[-1]) == (PC1_P95, PC1_MAX) else "DIFFERENT, beside"))
    if not ("%.6f" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K and int(ir["n"]) == N_ROOT and ir["null_seed_id"] == ROOT_ID):
        refuse("IDENTITY FAILED: declared %.6f k_d %d n %s seed %s (want %s, %d, %d, %s); no readout"
               % (d0, k0, ir["n"], ir["null_seed_id"], IDENTITY_DECLARED, IDENTITY_K, N_ROOT, ROOT_ID))
    say("IDENTITY: REPRODUCED (precondition held)")

    say("SUPPORT (a) deciding denominator: 5 subsamples per deciding size (n 486 PS1, n 441 PS2), each a site with %d null "
        "replicates; (b) DEFF 1.0 by construction (independent generator draws; no item-level resampling, no G14 two-stage "
        "machinery: D-PR-1 does not apply); (c) n_eff = %d replicates per subsample, 5 subsamples per size; (d) SE of an "
        "exceedance proportion at the bar sqrt(0.05 x 0.95 / %d) = %.4f per subsample; (e) MDE80 = 2.80 x SE = %.4f per "
        "subsample; (g) floor 1/301 = %.4f << 0.05; NULL-INFEASIBLE below n %d, DEGENERATE below %d reached replicates"
        % (REPS, REPS, REPS, math.sqrt(0.0475 / REPS), 2.80 * math.sqrt(0.0475 / REPS), 1 / 301.0, 2 * MCS, DEGENERATE_MIN))
    say("SUPPORT: no matches and no questions: wrong(established), the tie conventions A / B and a question-clustered bootstrap "
        "are N/A to a null exceedance count")
    for ln in LIKE:
        say(ln)

    res, out_rows = {}, []
    for s in site_names():
        r = rows[s]
        n = int(r["n"])
        if n != len(sfile[s]) or int(r["groups"]) != N_CATS:
            refuse("sites.csv: %s n %s groups %s (the site file holds %d; want %d groups)" % (s, r["n"], r["groups"], len(sfile[s]), N_CATS))
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
        res[s] = dict(n=n, d=d, k=k, p=CPC.p_of(k), c0p95=c0p95, np95=np95, comparable=comparable, reached=reached,
                      status=status)
        say("  %-11s n %3d: declared %.6f; null p05 %.6f / p50 %.6f / p95 %.6f / max %.6f; k_d %3d of %d, p_d %d/301 = %.6f; "
            "C0 p95 %.6f (%s); reached %d; deflated k %d (p95 %.6f) -> %s" % (
                s, n, d, CPC.pctl(sn, 0.05), CPC.pctl(sn, 0.50), np95, sn[-1], k, REPS, k + 1, float(CPC.p_of(k)), c0p95,
                "comparable" if comparable else "FAILS: reaches the null p95", reached, kd, CPC.pctl(sorted(sd), 0.95), status))
        out_rows.append([s, n, "%.6f" % d, k, "%d/301" % (k + 1), "%.6f" % np95, "%.6f" % c0p95, str(comparable).lower(), reached,
                         kd, status])

    verdicts = {}
    for n in SIZES:
        sts = [res["PS_n%d_d%d" % (n, dd)]["status"] for dd in DRAWS]
        c = sum(1 for x in sts if x == "CERTIFIED")
        nc = sum(1 for x in sts if x == "NOT CERTIFIED")
        ne_c0 = sum(1 for x in sts if x == "NOT EVALUABLE (C0)")
        ne_all = sum(1 for x in sts if x.startswith("NOT EVALUABLE"))
        counts = "certified %d, not certified %d, NOT EVALUABLE %d (C0 %d, degenerate / infeasible %d) of 5" % (
            c, nc, ne_all, ne_c0, ne_all - ne_c0)
        if n in DECIDING:
            v = size_verdict(sts)
            verdicts[n] = v
            say("%s (n %d): %s; %s (gate first: PCS-5)" % (DECIDING[n], n, v, counts))
        else:
            say("DESCRIPTIVE (n %d, no criterion): %s" % (n, counts))
    ds = [res["PS_n486_d%d" % dd]["d"] for dd in DRAWS]
    ns = [res["PS_n486_d%d" % dd]["np95"] for dd in DRAWS]
    say("VERDICT LINE re-stated at the run (Support (f)): at n 486 the median declared statistic %.6f vs the median null p95 "
        "%.6f (the pilot guess was about 0.11 vs 0.07)" % (median5(ds), median5(ns)))

    ps1 = verdicts[486]
    if ps1 == "NOT-CERTIFIED-AT-SIZE":
        say(SENT_FPS_FIRED)
    else:
        say("F-PS: NOT FIRED (PS1 %s). F-TAX N-1 and F2 stand." % ps1)
        if ps1 == "CERTIFIED-AT-SIZE":
            say(SENT_CERT)
        else:
            say("READING: none (PS1 %s: %s; no sentence)" % (ps1, "a registered UNDETERMINED" if ps1 == "MIXED" else "not evaluable"))

    if ps1 in P1_PROBS:
        b1 = sum((p - (1.0 if v == ps1 else 0.0)) ** 2 for v, p in P1_PROBS.items())
        say("P1 PS1 readings (CERTIFIED-AT-SIZE 0.55, MIXED 0.20, NOT-CERTIFIED-AT-SIZE 0.25): outcome %s, Brier (3-way sum) %.4f"
            % (ps1, b1))
    else:
        say("P1 PS1 readings: NOT SCORED (PS1 NOT EVALUABLE; PCS-6)")
    ps2 = verdicts[441]
    if ps2 != "NOT EVALUABLE":
        e2 = bool(ps2 == "CERTIFIED-AT-SIZE")
        say("P2 PS2 CERTIFIED-AT-SIZE (p 0.50): event %s (PS2 %s), Brier %.4f" % ("yes" if e2 else "no", ps2, (P2_P - (1.0 if e2 else 0.0)) ** 2))
    else:
        say("P2 PS2 CERTIFIED-AT-SIZE: NOT SCORED (PS2 NOT EVALUABLE; PCS-6)")
    md, mn = median5(ds), median5(ns)
    say("P3 n 486 median declared statistic %.2f [%.2f, %.2f]: %s (%.6f); median null p95 %.2f [%.2f, %.2f]: %s (%.6f)" % (
        P3_D, P3_D_LO, P3_D_HI, "HELD" if bool(P3_D_LO <= md <= P3_D_HI) else "FAILED", md,
        P3_N, P3_N_LO, P3_N_HI, "HELD" if bool(P3_N_LO <= mn <= P3_N_HI) else "FAILED", mn))
    allc = sum(1 for s in site_names() if res[s]["comparable"])
    e4 = bool(allc == len(site_names()))
    say("P4 C0 comparable on every subsample (p 0.85): event %s (%d of %d comparable), Brier %.4f" % (
        "yes" if e4 else "no", allc, len(site_names()), (P4_P - (1.0 if e4 else 0.0)) ** 2))
    say(DOES_NOT_SHOW)

    os.makedirs(out_dir, exist_ok=True)
    with open(outcome_p, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(csv_p, "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["site", "n", "declared", "k_d", "p_d", "null_p95", "c0_p95", "c0_comparable", "reached", "defl_k", "status"])
        w.writerows(out_rows)
    out("%s wrote %s and %s (write-once)" % (TAG, outcome_p, csv_p))
    return dict(verdicts=verdicts, res=res, fired=ps1 == "NOT-CERTIFIED-AT-SIZE", lines=L)


# ------------------------------------------------------------------------------------------------ selftest
def _site_fixture(tmp):
    """A site file with IDENTITY (6,993 ids) and the 15 subsamples drawn from synthetic 14-category labels."""
    cat = {"q%05d" % i: "c%02d" % (i % 14 if i < 6900 else i % 3) for i in range(N_ROOT)}
    data, sites = build_site_bytes(cat)
    p = os.path.join(tmp, SITES_NAME)
    open(p, "wb").write(data)
    return p, data, sites


def _fx(tmp, spec=None, status="COMPLETE", hashes_equal=True, partial=False, site_sha_bad=False, sepbar="0.0145",
        snapshot=SNAPSHOT, ident_d=0.10780301, ident_k=0, drop_site=None, extra_site=False, n_bad=None, k_lie=None, c0_lie=None,
        short_site=None, ident_seed="n00000001", ident_n=6993):
    """spec[site] = dict(k=, c0=small|equal|below, reached=None|int, scale=): SN = i*scale (i = 0..299), declared = (300-k)*scale
    so exactly k replicates are >= it (declared equals replicate 300-k: a tie); null p95 = 284*scale."""
    spec = spec or {}
    arm, outd = os.path.join(tmp, "arm"), os.path.join(tmp, "out")
    os.makedirs(arm)
    os.makedirs(outd)
    sp, data, sites = _site_fixture(outd)
    if short_site:                       # the site file itself holds one item too few for short_site (the arm agrees)
        drop = "%s	%s	" % (short_site, sites[short_site][0])
        data = b"".join(ln for ln in data.splitlines(True) if not ln.decode("utf-8").startswith(drop))
        open(sp, "wb").write(data)
    sha = sha256_bytes(data if not site_sha_bad else b"x")
    with open(os.path.join(arm, "status.txt"), "w") as f:
        f.write("%s\nsnapshot=%s\nsites_sha256=%s\nreps=300\nsliceDim=512\nsepBar=%s\ndropTop=0\nwhiten=false\nminClusterSize=55\n"
                "c0Seed=20261002\nthreads=12\n" % (status, snapshot, sha, sepbar))
    names = ["IDENTITY"] + site_names()
    if drop_site:
        names.remove(drop_site)
    if extra_site:
        names.append("PS_n100_d1")
    srows, rep_lines = [], []
    for s in names:
        if s == "IDENTITY":
            sn = [i / 10000.0 for i in range(300)]
            if ident_k:
                sn[299] = ident_d + 1e-9
            srows.append('IDENTITY,"IDENTITY",%d,14,%r,%d,,,,,%s,300' % (ident_n, ident_d, ident_k, ident_seed))
            rep_lines += ['"IDENTITY",SN,%d,%r' % (i, x) for i, x in enumerate(sn[:150] if partial else sn)]
            continue
        sp_ = dict(k=0, c0="small", reached=None, scale=1 / 1000.0)
        sp_.update(spec.get(s, {}))
        sc = sp_["scale"]
        n = int(s.split("_")[1][1:]) if s != "PS_n100_d1" else 100
        if n_bad and s == n_bad:
            n += 1
        if short_site and s == short_site:
            n -= 1
        sn = [i * sc for i in range(300)]
        if sp_["reached"] is not None:
            sn = [0.0] * (300 - sp_["reached"]) + [0.5 * sc + j * sc for j in range(sp_["reached"])]
        d = (300 - sp_["k"]) * sc if sp_["reached"] is None else 1000.0 * sc
        c0 = {"small": [i * sc * 0.001 for i in range(300)], "equal": list(sn), "below": [x - 1e-12 for x in sn]}[sp_["c0"]]
        k_arm = sum(1 for x in sn if x >= d) + (1 if k_lie == s else 0)
        c0p = CPC.pctl(sorted(c0), 0.95) + (1e-6 if c0_lie == s else 0.0)
        srows.append('SUBSAMPLE,"%s",%d,14,%r,%d,13,0,%r,123,%s,300' % (s, n, d, k_arm, c0p, s))
        for arm_, xs in (("SN", sn), ("SND", [x / 2 for x in sn]), ("C0", c0)):
            rep_lines += ['"%s",%s,%d,%r' % (s, arm_, i, x) for i, x in enumerate(xs)]
    with open(os.path.join(arm, "sites.csv"), "w") as f:
        f.write("role,site_id,n,groups,declared_stat,k_declared,defl_dims,defl_k_declared,c0_p95,c0_seed,null_seed_id,reps\n")
        f.write("\n".join(srows) + "\n")
    with open(os.path.join(arm, "replicates.csv"), "w") as f:
        f.write("site_id,arm,rep,stat\n" + "\n".join(rep_lines) + "\n")
    for x in ("before", "after"):
        json.dump({"embeddings": "aa/1", "queries": "bb/2" if (hashes_equal or x == "before") else "cc/2"},
                  open(os.path.join(outd, "emb_hashes_%s.json" % x), "w"))
    return arm, outd, sp


def _ks(size, ks, **kw):
    return {"PS_n%d_d%d" % (size, i + 1): dict(k=k, **kw) for i, k in enumerate(ks)}


def selftest():
    global _IN_SELFTEST
    _IN_SELFTEST = True
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="pcsst_")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:            # noqa: BLE001
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))

    def run(tmp, **kw):
        arm, outd, sp = _fx(tmp, **kw)
        lines = []
        r = analyze(arm, outd, sp, out=lines.append)
        return r, lines, outd

    def refused(tmp, needle, **kw):
        arm, outd, sp = _fx(tmp, **kw)
        try:
            analyze(arm, outd, sp, out=lambda s: None)
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
        assert r["verdicts"] == {486: "CERTIFIED-AT-SIZE", 441: "CERTIFIED-AT-SIZE"} and r["fired"] is False, r["verdicts"]
        has(L, "PS1 (n 486): CERTIFIED-AT-SIZE; certified 5, not certified 0, NOT EVALUABLE 0 (C0 0, degenerate / infeasible 0) "
               "of 5 (gate first: PCS-5)")
        has(L, "F-PS: NOT FIRED (PS1 CERTIFIED-AT-SIZE). F-TAX N-1 and F2 stand.")
        has(L, SENT_CERT)
        has(L, "P1 PS1 readings (CERTIFIED-AT-SIZE 0.55, MIXED 0.20, NOT-CERTIFIED-AT-SIZE 0.25): outcome CERTIFIED-AT-SIZE, "
               "Brier (3-way sum) 0.3050")
        has(L, "P2 PS2 CERTIFIED-AT-SIZE (p 0.50): event yes (PS2 CERTIFIED-AT-SIZE), Brier 0.2500")
        has(L, "P4 C0 comparable on every subsample (p 0.85): event yes (15 of 15 comparable), Brier 0.0225")
        has(L, "IDENTITY: full-size root n 6993, declared 0.107803 (registered 0.107803), k_d 0 of 300 (registered 0); null "
               "seeded by n00000001; null p95 0.028400 / max 0.029900 (PC1 of record 0.041626 / 0.042414: DIFFERENT, beside)")
        has(L, "IDENTITY: REPRODUCED (precondition held)")
        has(L, "  PS_n486_d1  n 486: declared 0.300000; null p05 0.014000 / p50 0.149000 / p95 0.284000 / max 0.299000; k_d   0 "
               "of 300, p_d 1/301 = 0.003322; C0 p95 0.000284 (comparable); reached 299; deflated k 0 (p95 0.142000) -> CERTIFIED")
        has(L, "DESCRIPTIVE (n 264, no criterion): certified 5, not certified 0, NOT EVALUABLE 0 (C0 0, degenerate / infeasible 0) of 5")
        has(L, DOES_NOT_SHOW)
        assert any(l.startswith("SUPPORT (a) deciding denominator: 5 subsamples per deciding size") and "0.0126" in l and
                   "0.0352" in l for l in L), L
        txt = open(os.path.join(outd, OUTCOME_NAME), encoding="utf-8").read()
        assert txt.startswith("pool: none (no DB opened)\n") and "\nPS1 (n 486): CERTIFIED-AT-SIZE;" in txt
        rows = list(csv.DictReader(open(os.path.join(outd, CSV_NAME), encoding="utf-8")))
        assert len(rows) == 15 and rows[0]["site"] == "PS_n486_d1" and rows[0]["p_d"] == "1/301" and rows[0]["status"] == "CERTIFIED"
        try:
            analyze(os.path.join(tmp, "arm"), outd, os.path.join(outd, SITES_NAME), out=lambda s: None)
            raise AssertionError("second analyze not refused")
        except SystemExit as e:
            assert "write-once" in str(e), e

    def boundaries(tmp):
        # k 14 certifies (p 15/301 <= 0.05; a tie: declared equals replicate 286), k 15 does not
        for i, (ks, v) in enumerate((([14, 14, 14, 14, 15], "CERTIFIED-AT-SIZE"), ([14, 14, 14, 15, 15], "MIXED"),
                                     ([14, 14, 15, 15, 15], "MIXED"), ([14, 15, 15, 15, 15], "NOT-CERTIFIED-AT-SIZE"),
                                     ([15, 300, 15, 16, 200], "NOT-CERTIFIED-AT-SIZE"))):
            r, L, _o = run(sub(tmp, i), spec=_ks(486, ks))
            assert r["verdicts"][486] == v and r["verdicts"][441] == "CERTIFIED-AT-SIZE", (ks, r["verdicts"])
            assert r["res"]["PS_n486_d1"]["k"] == ks[0], r["res"]["PS_n486_d1"]
            if v == "NOT-CERTIFIED-AT-SIZE":
                has(L, SENT_FPS_FIRED)
                assert r["fired"] is True
                has(L, "P1 PS1 readings (CERTIFIED-AT-SIZE 0.55, MIXED 0.20, NOT-CERTIFIED-AT-SIZE 0.25): outcome "
                       "NOT-CERTIFIED-AT-SIZE, Brier (3-way sum) 0.9050")
                assert not any(l.startswith("READING") for l in L), L
            if v == "MIXED":
                has(L, "F-PS: NOT FIRED (PS1 MIXED). F-TAX N-1 and F2 stand.")
                has(L, "READING: none (PS1 MIXED: a registered UNDETERMINED; no sentence)")
                has(L, "P1 PS1 readings (CERTIFIED-AT-SIZE 0.55, MIXED 0.20, NOT-CERTIFIED-AT-SIZE 0.25): outcome MIXED, "
                       "Brier (3-way sum) 1.0050")
        r, L, _o = run(sub(tmp, 9), spec=_ks(486, [14, 15, 15, 15, 15]))
        has(L, "  PS_n486_d1  n 486: declared 0.286000; null p05 0.014000 / p50 0.149000 / p95 0.284000 / max 0.299000; k_d  14 "
               "of 300, p_d 15/301 = 0.049834; C0 p95 0.000284 (comparable); reached 299; deflated k 0 (p95 0.142000) -> CERTIFIED")
        has(L, "  PS_n486_d2  n 486: declared 0.285000; null p05 0.014000 / p50 0.149000 / p95 0.284000 / max 0.299000; k_d  15 "
               "of 300, p_d 16/301 = 0.053156; C0 p95 0.000284 (comparable); reached 299; deflated k 0 (p95 0.142000) -> NOT CERTIFIED")

    def c0_gate(tmp):
        # one C0 failure + 4 certified -> CERTIFIED-AT-SIZE
        sp_ = _ks(486, [0, 0, 0, 0, 0])
        sp_["PS_n486_d5"]["c0"] = "equal"
        r, L, _o = run(sub(tmp, 0), spec=sp_)
        assert r["verdicts"][486] == "CERTIFIED-AT-SIZE" and r["res"]["PS_n486_d5"]["status"] == "NOT EVALUABLE (C0)", r["verdicts"]
        has(L, "PS1 (n 486): CERTIFIED-AT-SIZE; certified 4, not certified 0, NOT EVALUABLE 1 (C0 1, degenerate / infeasible 0) "
               "of 5 (gate first: PCS-5)")
        has(L, "P4 C0 comparable on every subsample (p 0.85): event no (14 of 15 comparable), Brier 0.7225")
        # two C0 failures -> NOT EVALUABLE although 3 certify; P1 NOT SCORED
        sp_["PS_n486_d4"]["c0"] = "equal"
        r, L, _o = run(sub(tmp, 1), spec=sp_)
        assert r["verdicts"][486] == "NOT EVALUABLE" and r["fired"] is False, r["verdicts"]
        has(L, "P1 PS1 readings: NOT SCORED (PS1 NOT EVALUABLE; PCS-6)")
        has(L, "F-PS: NOT FIRED (PS1 NOT EVALUABLE). F-TAX N-1 and F2 stand.")
        has(L, "READING: none (PS1 NOT EVALUABLE: not evaluable; no sentence)")
        # two C0 failures with the rest NOT CERTIFIED: the gate precedes NOT-CERTIFIED (no F-PS)
        sp2 = _ks(486, [100, 100, 100, 0, 0])
        sp2["PS_n486_d4"]["c0"] = sp2["PS_n486_d5"]["c0"] = "equal"
        r, L, _o = run(sub(tmp, 2), spec=sp2)
        assert r["verdicts"][486] == "NOT EVALUABLE" and r["fired"] is False, r["verdicts"]
        # C0 one step below the null p95 is comparable; at equality it reaches
        sp3 = _ks(486, [0] * 5, c0="below")
        r, L, _o = run(sub(tmp, 3), spec=sp3)
        assert r["verdicts"][486] == "CERTIFIED-AT-SIZE" and all(r["res"]["PS_n486_d%d" % i]["comparable"] for i in DRAWS), r["verdicts"]
        # PS2 NOT EVALUABLE -> P2 NOT SCORED
        sp4 = _ks(441, [0] * 5)
        sp4["PS_n441_d1"]["c0"] = sp4["PS_n441_d2"]["c0"] = "equal"
        r, L, _o = run(sub(tmp, 4), spec=sp4)
        assert r["verdicts"] == {486: "CERTIFIED-AT-SIZE", 441: "NOT EVALUABLE"}, r["verdicts"]
        has(L, "P2 PS2 CERTIFIED-AT-SIZE: NOT SCORED (PS2 NOT EVALUABLE; PCS-6)")

    def degenerate(tmp):
        sp_ = _ks(486, [0] * 5)
        sp_["PS_n486_d1"]["reached"] = 19
        r, L, _o = run(sub(tmp, 0), spec=sp_)
        assert r["res"]["PS_n486_d1"]["status"] == "NOT EVALUABLE (DEGENERATE)" and r["res"]["PS_n486_d1"]["reached"] == 19
        assert r["verdicts"][486] == "CERTIFIED-AT-SIZE", r["verdicts"]
        sp_["PS_n486_d1"]["reached"] = 20
        r, L, _o = run(sub(tmp, 1), spec=sp_)
        assert r["res"]["PS_n486_d1"]["status"] == "CERTIFIED", r["res"]["PS_n486_d1"]
        # one degenerate + one C0 failure -> the size gate (Q-2)
        sp_["PS_n486_d1"]["reached"] = 5
        sp_["PS_n486_d2"]["c0"] = "equal"
        r, L, _o = run(sub(tmp, 2), spec=sp_)
        assert r["verdicts"][486] == "NOT EVALUABLE", r["verdicts"]
        has(L, "PS1 (n 486): NOT EVALUABLE; certified 3, not certified 0, NOT EVALUABLE 2 (C0 1, degenerate / infeasible 1) "
               "of 5 (gate first: PCS-5)")
        assert subsample_status(109, 0, True, 300) == "NOT EVALUABLE (NULL-INFEASIBLE)" and subsample_status(110, 0, True, 300) == "CERTIFIED"

    def sizes_separate(tmp):
        # PS1 from n 486 only, PS2 from n 441 only, n 264 never decides
        sp_ = _ks(441, [100] * 5)
        sp_.update(_ks(264, [100] * 5, c0="equal"))
        r, L, _o = run(tmp, spec=sp_)
        assert r["verdicts"] == {486: "CERTIFIED-AT-SIZE", 441: "NOT-CERTIFIED-AT-SIZE"} and r["fired"] is False, r["verdicts"]
        has(L, "PS2 (n 441): NOT-CERTIFIED-AT-SIZE; certified 0, not certified 5, NOT EVALUABLE 0 (C0 0, degenerate / infeasible 0) "
               "of 5 (gate first: PCS-5)")
        has(L, "P2 PS2 CERTIFIED-AT-SIZE (p 0.50): event no (PS2 NOT-CERTIFIED-AT-SIZE), Brier 0.2500")
        has(L, "DESCRIPTIVE (n 264, no criterion): certified 0, not certified 0, NOT EVALUABLE 5 (C0 5, degenerate / infeasible 0) of 5")
        has(L, "P4 C0 comparable on every subsample (p 0.85): event no (10 of 15 comparable), Brier 0.7225")
        r2, _L2, _o2 = run(sub(tmp, 1), spec=_ks(486, [100] * 5))
        assert r2["verdicts"] == {486: "NOT-CERTIFIED-AT-SIZE", 441: "CERTIFIED-AT-SIZE"} and r2["fired"] is True, r2["verdicts"]

    def p3(tmp):
        sc = [1 / 1000.0, 1 / 2000.0, 1 / 3000.0, 1 / 4000.0, 1 / 5000.0]
        sp_ = {"PS_n486_d%d" % (i + 1): dict(k=0, scale=s) for i, s in enumerate(sc)}
        r, L, _o = run(sub(tmp, 0), spec=sp_)
        has(L, "P3 n 486 median declared statistic 0.11 [0.09, 0.14]: HELD (0.100000); median null p95 0.07 [0.05, 0.10]: HELD "
               "(0.094667)")
        has(L, "VERDICT LINE re-stated at the run (Support (f)): at n 486 the median declared statistic 0.100000 vs the median null "
               "p95 0.094667 (the pilot guess was about 0.11 vs 0.07)")
        r, L, _o = run(sub(tmp, 1))
        has(L, "P3 n 486 median declared statistic 0.11 [0.09, 0.14]: FAILED (0.300000); median null p95 0.07 [0.05, 0.10]: FAILED "
               "(0.284000)")

    def identity(tmp):
        refused(sub(tmp, 0), "IDENTITY FAILED: declared 0.107804 k_d 0", ident_d=0.1078041)
        refused(sub(tmp, 1), "IDENTITY FAILED: declared 0.107803 k_d 1", ident_k=1)
        refused(sub(tmp, 2), "IDENTITY FAILED: declared 0.107803 k_d 0 n 6993 seed PS_x", ident_seed="PS_x")
        refused(sub(tmp, 3), "IDENTITY FAILED: declared 0.107803 k_d 0 n 6992 seed n00000001", ident_n=6992)

    def refusals(tmp):
        for i, (needle, kw) in enumerate([
                ("the arm's status is 'REFUSED: x'", dict(status="REFUSED: x")),
                ("a partial file", dict(partial=True)),
                ("embeddings_cache.db changed during the arm", dict(hashes_equal=False)),
                ("the arm read site file sha256", dict(site_sha_bad=True)),
                ("instrument: the arm ran sepBar='0.025'", dict(sepbar="0.025")),
                ("the arm read snapshot 'OTHER'", dict(snapshot="OTHER")),
                ("sites.csv holds", dict(drop_site="PS_n441_d3")),
                ("sites.csv holds", dict(extra_site=True)),
                ("sites.csv: PS_n264_d2 n 265", dict(n_bad="PS_n264_d2")),
                ("PS_n486_d3: k_d recount 0 != the arm's 1", dict(k_lie="PS_n486_d3")),
                ("PS_n441_d5: C0 p95 recount", dict(c0_lie="PS_n441_d5")),
                ("site file: PS_n441_d2 holds 440 items in 14 categories (want 441 in 14)", dict(short_site="PS_n441_d2"))]):
            refused(sub(tmp, i), needle, **kw)

    def site_file(tmp):
        assert allocate({"a": 5, "b": 3, "c": 2}, 5) == {"a": 3, "b": 1, "c": 1}           # 2.5 1.5 1.0 -> floors 2 1 1, +1 a (tie a/b by name)
        assert allocate({"b": 5, "a": 3, "c": 2}, 5) == {"b": 2, "a": 2, "c": 1}           # 2.5 1.5 1.0: the .5 tie goes to 'a' by name
        q = allocate({"x": 1, "y": 1, "z": 1}, 2)
        assert q == {"x": 1, "y": 1, "z": 0}, q
        cnt = {"c%02d" % i: 400 + 37 * i for i in range(14)}
        for n in SIZES:
            q = allocate(cnt, n)
            assert sum(q.values()) == n and all(abs(q[c] - n * cnt[c] / sum(cnt.values())) < 1 for c in cnt), q
        p, data, sites = _site_fixture(tmp)
        assert list(sites) == ["IDENTITY"] + site_names() and len(sites["IDENTITY"]) == N_ROOT
        assert all(len(sites[s]) == int(s.split("_")[1][1:]) for s in site_names())
        assert sites["PS_n486_d1"] != sites["PS_n486_d2"] and len(set(sites["PS_n486_d1"])) == 486
        _d2, s2 = build_site_bytes({"q%05d" % i: "c%02d" % (i % 14 if i < 6900 else i % 3) for i in range(N_ROOT)})
        assert s2 == sites and _d2 == data, "the draw is not deterministic"
        # golden: PCS-1 pinned on the fixture (allocation, rng per (size, seed), sorted pools, file order)
        assert sha256_bytes(data) == "276cecf958304affe4130e1d7606a4a74097b1881b952ea54ca7e20135654540", sha256_bytes(data)
        assert sites["PS_n264_d1"][:5] == ["q00007", "q00028", "q00033", "q00088", "q00107"], sites["PS_n264_d1"][:5]
        ps = parse_site_file(p)
        assert list(ps) == list(sites) and sorted(ps["PS_n264_d5"]) == sites["PS_n264_d5"]
        lab = os.path.join(tmp, "cpc.tsv")
        open(lab, "wb").write(b"query_id\tcategory\tsrc\nq1\tmath\t\nq2\tlaw\tx\n")
        assert read_cpc_labels(lab, sha=sha256_bytes(open(lab, "rb").read())) == {"q1": "math", "q2": "law"}
        try:
            read_cpc_labels(lab)
            raise AssertionError("a label file other than CPC's of record accepted")
        except SystemExit as e:
            assert "not CERT-POSITIVE-CONTROL's label file of record" in str(e), e
        try:
            build_site_bytes({"q1": "a", "q2": "b"})
            raise AssertionError("2 categories accepted")
        except SystemExit as e:
            assert "2 declared categories, not the registered 14" in str(e), e

    def helpers(tmp):
        cfg = G.load_config(os.path.join(ROOT, CONFIG_REL))
        assert command(cfg, 6) == (
            '.\\gradlew.bat certPcSize --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 '
            '"-DsnapshotId=20261001_094311_Headless_Run_Auto_ge" "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" '
            '"-DsiteLabels=experiment_results/cert_pc_size/site_labels.tsv" "-DoutDir=experiment_results/cert_pc_size/arm"'), command(cfg, 6)
        assert command(cfg, 8).endswith(' "-DsiteNullHeap=8g"')
        assert median5([5, 1, 4, 2, 3]) == 3
        assert size_verdict(["CERTIFIED"] * 4 + ["NOT EVALUABLE (C0)"]) == "CERTIFIED-AT-SIZE"
        for fn_, arg in ((prepare, (tmp, "x")), (hashes, ("before", tmp))):
            try:
                fn_(*arg)
                raise AssertionError("%s from another data root not refused" % fn_.__name__)
            except SystemExit as e:
                assert tmp in str(e), e

    def main_analyze(tmp):
        global OUT_REL
        arm, outd, sp = _fx(tmp, spec=_ks(486, [14, 15, 15, 15, 15]))
        os.replace(arm, os.path.join(outd, ARM_NAME))
        saved = OUT_REL
        OUT_REL = os.path.abspath(outd)
        try:
            rc = main(["--analyze"])
            if rc != 0:
                raise AssertionError("main --analyze returned %r" % rc)
        finally:
            OUT_REL = saved
        txt = open(os.path.join(outd, OUTCOME_NAME), encoding="utf-8").read()
        assert "\nPS1 (n 486): NOT-CERTIFIED-AT-SIZE;" in txt and "\n" + SENT_FPS_FIRED + "\n" in txt, txt[-800:]

    for nm, fn in [("main --analyze (the run-of-record wiring)", main_analyze),
                   ("all CERTIFIED: every printed line, write-once", all_cert),
                   ("PS1 boundaries 4 / 3 / 2 / 1 / 0 of 5; F-PS; tie at k 14", boundaries),
                   ("C0 gate: 1 fails -> CERTIFIED, 2 fail -> NOT EVALUABLE (precedence), equality, P1 / P2 NOT SCORED", c0_gate),
                   ("DEGENERATE 19 / 20; infeasible; degenerate + C0 -> gate", degenerate),
                   ("sizes read separately (PS1 486, PS2 441, 264 descriptive)", sizes_separate),
                   ("P3 medians HELD / FAILED", p3), ("IDENTITY refusals", identity),
                   ("refusals", refusals), ("allocation, draw, site file", site_file), ("helpers", helpers)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


MUTANTS = [
    ("M0 control (no-op; must SURVIVE)", "TAG = \"[PCS]\"", "TAG = \"[PCS]\""),
    ("M1 >= -> > (CPC kcount via wrapper)", "        k = CPC.kcount(R[(s, \"SN\")], d)", "        k = sum(1 for x in R[(s, \"SN\")] if x > d)"),
    ("M2 p = k/300", "    return \"CERTIFIED\" if bool(CPC.p_of(k) <= BAR) else \"NOT CERTIFIED\"",
     "    return \"CERTIFIED\" if bool(Fraction(k, 300) <= BAR) else \"NOT CERTIFIED\""),
    ("M3 c >= 4 -> c >= 3", "    if c >= 4:", "    if c >= 3:"),
    ("M4 c <= 1 -> c <= 2", "    if c <= 1:", "    if c <= 2:"),
    ("M5 gate ne >= 2 -> >= 1", "    if ne >= 2:", "    if ne >= 1:"),
    ("M6 gate after NOT-CERTIFIED", "    if ne >= 2:\n        return \"NOT EVALUABLE\"\n    if c >= 4:\n        return \"CERTIFIED-AT-SIZE\"\n    if c <= 1:\n        return \"NOT-CERTIFIED-AT-SIZE\"",
     "    if c >= 4:\n        return \"CERTIFIED-AT-SIZE\"\n    if c <= 1:\n        return \"NOT-CERTIFIED-AT-SIZE\"\n    if ne >= 2:\n        return \"NOT EVALUABLE\""),
    ("M7 C0 reaches strict", "        comparable = not bool(c0p95 >= np95)", "        comparable = not bool(c0p95 > np95)"),
    ("M8 C0 not a precondition", "    if not comparable:\n        return \"NOT EVALUABLE (C0)\"", "    if False:\n        return \"NOT EVALUABLE (C0)\""),
    ("M9 degenerate check removed", "    if reached < DEGENERATE_MIN:", "    if False:"),
    ("M10 degenerate floor 20 -> 19", "REPS, N_CATS, MCS, DEGENERATE_MIN = 300, 14, 55, 20", "REPS, N_CATS, MCS, DEGENERATE_MIN = 300, 14, 55, 19"),
    ("M11 PS1 from the n-441 rows", "    ps1 = verdicts[486]", "    ps1 = verdicts[441]"),
    ("M12 PS2 from the n-486 rows", "    ps2 = verdicts[441]", "    ps2 = verdicts[486]"),
    ("M13 n 264 decides (DECIDING incl. 264)", "DECIDING = {486: \"PS1\", 441: \"PS2\"}", "DECIDING = {486: \"PS1\", 441: \"PS2\", 264: \"PS3\"}"),
    ("M14 F-PS on MIXED too", "    if ps1 == \"NOT-CERTIFIED-AT-SIZE\":\n        say(SENT_FPS_FIRED)",
     "    if ps1 in (\"NOT-CERTIFIED-AT-SIZE\", \"MIXED\"):\n        say(SENT_FPS_FIRED)"),
    ("M15 P1 scored when NOT EVALUABLE", "    if ps1 in P1_PROBS:", "    if True:"),
    ("M16 P2 scored when NOT EVALUABLE", "    if ps2 != \"NOT EVALUABLE\":", "    if True:"),
    ("M17 P3 median -> min", "def median5(xs):\n    s = sorted(xs)\n    return s[len(s) // 2]", "def median5(xs):\n    s = sorted(xs)\n    return s[0]"),
    ("M18 P3 median -> mean", "def median5(xs):\n    s = sorted(xs)\n    return s[len(s) // 2]", "def median5(xs):\n    return sum(xs) / len(xs)"),
    ("M19 P4 over the deciding sizes only", "    allc = sum(1 for s in site_names() if res[s][\"comparable\"])\n    e4 = bool(allc == len(site_names()))",
     "    allc = sum(1 for s in site_names()[:10] if res[s][\"comparable\"])\n    e4 = bool(allc == 10)"),
    ("M20 IDENTITY gate removed", "    if not (\"%.6f\" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K", "    if False and not (\"%.6f\" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K"),
    ("M21 IDENTITY k not checked", "    if not (\"%.6f\" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K and", "    if not (\"%.6f\" % d0 == IDENTITY_DECLARED and"),
    ("M22 hash check removed", "    if json.load(open(hb)) != json.load(open(ha)):", "    if False:"),
    ("M23 write-once pre-check removed", "        if os.path.exists(p):\n            refuse(\"%s exists: the outcome is write-once\" % p)",
     "        if False:\n            refuse(\"%s exists: the outcome is write-once\" % p)"),
    ("M24 partial replicates accepted", "        if [i for i, _x in xs] != list(range(REPS)):", "        if False:"),
    ("M25 instrument check removed", "        if st.get(k) != v:\n            refuse(\"instrument", "        if False:\n            refuse(\"instrument"),
    ("M26 snapshot check removed", "    if st.get(\"snapshot\") != SNAPSHOT:", "    if False:"),
    ("M27 site sha check removed", "    if st.get(\"sites_sha256\") != s_sha:", "    if False:"),
    ("M28 sites.csv set check removed", "    if list(rows) != want:", "    if False:"),
    ("M29 k recount check removed", "        if k != int(r[\"k_declared\"]):", "        if False:"),
    ("M30 C0 recount check removed", "        if c0p95 != float(r[\"c0_p95\"]):", "        if False:"),
    ("M31 k_d from the deflated arm", "        k = CPC.kcount(R[(s, \"SN\")], d)", "        k = CPC.kcount(R[(s, \"SND\")], d)"),
    ("M32 C0 p95 from the null", "        c0 = sorted(R[(s, \"C0\")])", "        c0 = sorted(R[(s, \"SN\")])"),
    ("M33 null p95 -> max", "        c0p95, np95 = CPC.pctl(c0, 0.95), CPC.pctl(sn, 0.95)", "        c0p95, np95 = CPC.pctl(c0, 0.95), sn[-1]"),
    ("M34 allocation ties by name descending", "    for c in sorted(counts, key=lambda c: (-(exact[c] - q[c]), c))[:left]:",
     "    for c in sorted(counts, key=lambda c: (-(exact[c] - q[c]), c), reverse=True)[:left]:"),
    ("M35 allocation floor -> round", "    q = {c: int(math.floor(v)) for c, v in exact.items()}", "    q = {c: int(round(v)) for c, v in exact.items()}"),
    ("M36 one rng across sizes (not per size, seed)", "    rng = random.Random(seed)", "    rng = random.Random(seed + n)"),
    ("M37 site-size check removed", "        if len(sfile[s]) != n or len(set(sfile[s].values())) != N_CATS:", "        if False:"),
    ("M38 degenerate counted as not certified for the gate", "    ne = sum(1 for s in statuses if s.startswith(\"NOT EVALUABLE\"))",
     "    ne = sum(1 for s in statuses if s == \"NOT EVALUABLE (C0)\")"),
    ("M39 infeasible floor removed", "    if n < 2 * MCS:", "    if False:"),
    ("M40 size statuses from the first draw only", "        sts = [res[\"PS_n%d_d%d\" % (n, dd)][\"status\"] for dd in DRAWS]",
     "        sts = [res[\"PS_n%d_d%d\" % (n, 1)][\"status\"] for dd in DRAWS]"),
    ("M41 IDENTITY seed id not checked", " and int(ir[\"n\"]) == N_ROOT and ir[\"null_seed_id\"] == ROOT_ID):", " and int(ir[\"n\"]) == N_ROOT):"),
    ("M42 IDENTITY n not checked", " and int(ir[\"n\"]) == N_ROOT and ir[\"null_seed_id\"] == ROOT_ID):", " and ir[\"null_seed_id\"] == ROOT_ID):"),
]


def mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    rows = []
    for name, old, new in MUTANTS:
        if src.count(old) < 1:
            rows.append((name, "NOT APPLIED (pattern absent)"))
            continue
        mut = src.replace(old, new, 1)
        tmp = os.path.join(HERE, "_pcs_mutant_%d.py" % os.getpid())
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(mut)
            r = subprocess.run([sys.executable, tmp, "--selftest"], capture_output=True, text=True, timeout=900)
            rows.append((name, "KILLED" if r.returncode != 0 else "SURVIVED"))
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    for n, v in rows:
        print("  %-52s %s" % (n, v))
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
    analyze(os.path.join(d, ARM_NAME), d, os.path.join(d, SITES_NAME))
    return 0


if __name__ == "__main__":
    sys.exit(main())
